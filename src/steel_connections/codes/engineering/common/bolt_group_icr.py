from __future__ import annotations

import math
from dataclasses import dataclass

from steel_connections.codes.engineering.common.bolt_group_types import (
    BoltForce,
    BoltGroupGeometry,
    BoltGroupMethod,
    ICRIteration,
    ICRResult,
    InPlaneLoad,
)


@dataclass(frozen=True)
class ICRLawParameters:
    """Nonlinear bolt force-deformation law parameters.

    Relationship:
    - Delta_i = (r_i / r_max) * delta_max
    - R_i = Rult * (1 - exp(-mu * Delta_i))^lambda_exp
    """

    mu: float = 10.0
    lambda_exp: float = 0.55
    delta_max: float = 0.34


@dataclass(frozen=True)
class _ICRTrialState:
    center_x: float
    center_y: float
    e_icr_x: float
    e_icr_y: float
    sum_unit_moment: float
    cu: float | None
    residual_fx: float
    residual_fy: float
    residual_norm: float
    bolt_forces: tuple[BoltForce, ...]


def _unit_force_factor(*, r: float, r_max: float, law: ICRLawParameters, epsilon: float) -> float:
    if r_max <= epsilon:
        return 0.0
    delta = (r / r_max) * law.delta_max
    return (1.0 - math.exp(-law.mu * delta)) ** law.lambda_exp


def _evaluate_icr_trial(
    *,
    geometry: BoltGroupGeometry,
    load: InPlaneLoad,
    center_x: float,
    center_y: float,
    law: ICRLawParameters,
    epsilon: float,
) -> _ICRTrialState:
    ax = geometry.centroid_x - center_x
    ay = center_y - geometry.centroid_y
    e_icr_x = load.ex + ax
    e_icr_y = load.ey - ay

    radii = [math.hypot(bolt.x - center_x, bolt.y - center_y) for bolt in geometry.bolts]
    r_max = max(radii) if radii else 0.0
    if r_max <= epsilon:
        return _ICRTrialState(
            center_x=center_x,
            center_y=center_y,
            e_icr_x=e_icr_x,
            e_icr_y=e_icr_y,
            sum_unit_moment=0.0,
            cu=None,
            residual_fx=float("inf"),
            residual_fy=float("inf"),
            residual_norm=float("inf"),
            bolt_forces=tuple(),
        )

    unit_factors: list[float] = []
    unit_moments: list[float] = []
    for idx, bolt in enumerate(geometry.bolts):
        factor = _unit_force_factor(r=radii[idx], r_max=r_max, law=law, epsilon=epsilon)
        unit_factors.append(factor)
        unit_moments.append(factor * radii[idx])
    sum_unit_moment = sum(unit_moments)
    if abs(sum_unit_moment) <= epsilon:
        return _ICRTrialState(
            center_x=center_x,
            center_y=center_y,
            e_icr_x=e_icr_x,
            e_icr_y=e_icr_y,
            sum_unit_moment=sum_unit_moment,
            cu=None,
            residual_fx=float("inf"),
            residual_fy=float("inf"),
            residual_norm=float("inf"),
            bolt_forces=tuple(),
        )

    if load.resultant <= epsilon:
        mp_scalar = -load.mz
        cu = abs(sum_unit_moment)
    else:
        mp_scalar = load.vx * e_icr_y - load.vy * e_icr_x
        mp_unit = -(load.vx / load.resultant) * e_icr_y + (load.vy / load.resultant) * e_icr_x
        cu = abs(sum_unit_moment / mp_unit) if abs(mp_unit) > epsilon else None

    force_scale = mp_scalar / sum_unit_moment

    bolt_forces: list[BoltForce] = []
    sum_fx = 0.0
    sum_fy = 0.0
    for idx, bolt in enumerate(geometry.bolts):
        dx_icr = bolt.x - center_x
        dy_icr = bolt.y - center_y
        radius = radii[idx]
        force = unit_factors[idx] * force_scale
        if radius > epsilon:
            fx = -force * dy_icr / radius
            fy = force * dx_icr / radius
        else:
            fx = 0.0
            fy = 0.0
        resultant = math.hypot(fx, fy)
        moment_cg = -fx * bolt.dy + fy * bolt.dx
        sum_fx += fx
        sum_fy += fy
        bolt_forces.append(
            BoltForce(
                tag=bolt.tag,
                fx=fx,
                fy=fy,
                resultant=resultant,
                moment_about_cg=moment_cg,
            )
        )

    residual_fx = sum_fx + load.vx
    residual_fy = sum_fy + load.vy
    residual_norm = math.hypot(residual_fx, residual_fy)
    return _ICRTrialState(
        center_x=center_x,
        center_y=center_y,
        e_icr_x=e_icr_x,
        e_icr_y=e_icr_y,
        sum_unit_moment=sum_unit_moment,
        cu=cu,
        residual_fx=residual_fx,
        residual_fy=residual_fy,
        residual_norm=residual_norm,
        bolt_forces=tuple(bolt_forces),
    )


def solve_instant_center_of_rotation(
    *,
    geometry: BoltGroupGeometry,
    load: InPlaneLoad,
    bolt_capacity: float,
    tolerance: float,
    max_iterations: int,
    law: ICRLawParameters | None = None,
    epsilon: float = 1e-12,
) -> ICRResult:
    """Solve connection with nonlinear Instantaneous Center of Rotation (ICR).

    Procedure:
    - Start from an elastic center estimate.
    - Iterate center location so force equilibrium is satisfied:
      sum(Fx_i) + Vx = 0
      sum(Fy_i) + Vy = 0
    - At each iteration, bolt force follows the nonlinear deformation law.
    """

    if geometry.bolt_count < 1:
        raise ValueError("Bolt group must contain at least one bolt.")
    if bolt_capacity <= 0.0:
        raise ValueError("bolt_capacity must be > 0.")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be > 0.")
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1.")

    law_params = law or ICRLawParameters()
    if abs(load.mz) <= epsilon:
        return ICRResult(
            method=BoltGroupMethod.ICR,
            converged=False,
            note="ICR is not applicable when Mz=0.",
            icr_x=geometry.centroid_x,
            icr_y=geometry.centroid_y,
            cu=None,
            demand=None,
            capacity=None,
            dcr=None,
            final_residual=float("inf"),
            iterations=tuple(),
            bolt_forces=tuple(),
        )

    # Pure torsion branch (V = 0): no center iteration is required.
    if load.resultant <= epsilon:
        trial = _evaluate_icr_trial(
            geometry=geometry,
            load=load,
            center_x=geometry.centroid_x,
            center_y=geometry.centroid_y,
            law=law_params,
            epsilon=epsilon,
        )
        capacity = trial.cu * bolt_capacity if trial.cu is not None else None
        demand = abs(load.mz)
        dcr = (demand / capacity) if capacity and capacity > epsilon else None
        return ICRResult(
            method=BoltGroupMethod.ICR,
            converged=True,
            note=None,
            icr_x=trial.center_x,
            icr_y=trial.center_y,
            cu=trial.cu,
            demand=demand,
            capacity=capacity,
            dcr=dcr,
            final_residual=trial.residual_norm,
            iterations=(
                ICRIteration(
                    iteration=1,
                    icr_x=trial.center_x,
                    icr_y=trial.center_y,
                    residual_fx=trial.residual_fx,
                    residual_fy=trial.residual_fy,
                    residual_norm=trial.residual_norm,
                    step_dx=0.0,
                    step_dy=0.0,
                ),
            ),
            bolt_forces=trial.bolt_forces,
        )

    if geometry.ip <= epsilon:
        return ICRResult(
            method=BoltGroupMethod.ICR,
            converged=False,
            note="ICR is not applicable because Ip is zero.",
            icr_x=geometry.centroid_x,
            icr_y=geometry.centroid_y,
            cu=None,
            demand=None,
            capacity=None,
            dcr=None,
            final_residual=float("inf"),
            iterations=tuple(),
            bolt_forces=tuple(),
        )

    # Initial center from elastic estimate.
    n_bolts = float(geometry.bolt_count)
    ax0 = load.vy * geometry.ip / (load.mz * n_bolts)
    ay0 = load.vx * geometry.ip / (load.mz * n_bolts)
    center_x = geometry.centroid_x - ax0
    center_y = geometry.centroid_y + ay0

    ecc = math.hypot(load.ex, load.ey)
    if ecc < 1.0:
        step_factor = 0.5
    elif ecc < 5.0:
        step_factor = 1.0
    elif ecc < 10.0:
        step_factor = 2.0
    else:
        step_factor = 5.0

    iterations: list[ICRIteration] = []
    trial_history: list[_ICRTrialState] = []
    previous_norm: float | None = None

    for index in range(1, max_iterations + 1):
        trial = _evaluate_icr_trial(
            geometry=geometry,
            load=load,
            center_x=center_x,
            center_y=center_y,
            law=law_params,
            epsilon=epsilon,
        )
        trial_history.append(trial)

        step_dx = 0.0
        step_dy = 0.0
        if trial.residual_norm > tolerance:
            step_dx = trial.residual_fy * geometry.ip / (load.mz * n_bolts) / step_factor
            step_dy = trial.residual_fx * geometry.ip / (load.mz * n_bolts) / step_factor

        iterations.append(
            ICRIteration(
                iteration=index,
                icr_x=trial.center_x,
                icr_y=trial.center_y,
                residual_fx=trial.residual_fx,
                residual_fy=trial.residual_fy,
                residual_norm=trial.residual_norm,
                step_dx=step_dx,
                step_dy=step_dy,
            )
        )

        if trial.residual_norm <= tolerance:
            capacity = trial.cu * bolt_capacity if trial.cu is not None else None
            demand = abs(load.resultant)
            dcr = (demand / capacity) if capacity and capacity > epsilon else None
            return ICRResult(
                method=BoltGroupMethod.ICR,
                converged=True,
                note=None,
                icr_x=trial.center_x,
                icr_y=trial.center_y,
                cu=trial.cu,
                demand=demand,
                capacity=capacity,
                dcr=dcr,
                final_residual=trial.residual_norm,
                iterations=tuple(iterations),
                bolt_forces=trial.bolt_forces,
            )

        if previous_norm is not None and trial.residual_norm > previous_norm * 1.05:
            step_factor *= 2.0
        previous_norm = trial.residual_norm

        center_x = center_x - step_dx
        center_y = center_y + step_dy

    last = trial_history[-1] if trial_history else None
    return ICRResult(
        method=BoltGroupMethod.ICR,
        converged=False,
        note="ICR did not converge within max_iterations.",
        icr_x=last.center_x if last is not None else center_x,
        icr_y=last.center_y if last is not None else center_y,
        cu=last.cu if last is not None else None,
        demand=abs(load.resultant) if load.resultant > epsilon else None,
        capacity=(last.cu * bolt_capacity) if last is not None and last.cu is not None else None,
        dcr=(
            (abs(load.resultant) / (last.cu * bolt_capacity))
            if last is not None and last.cu is not None and abs(last.cu * bolt_capacity) > epsilon
            else None
        ),
        final_residual=last.residual_norm if last is not None else float("inf"),
        iterations=tuple(iterations),
        bolt_forces=last.bolt_forces if last is not None else tuple(),
    )
