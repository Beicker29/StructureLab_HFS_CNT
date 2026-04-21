from __future__ import annotations

import math

from steel_connections.codes.engineering.common.bolt_group_types import (
    BoltForce,
    BoltGroupGeometry,
    BoltGroupMethod,
    ElasticECRResult,
    ElasticSuperpositionResult,
    InPlaneLoad,
)


def solve_elastic_superposition(
    *,
    geometry: BoltGroupGeometry,
    load: InPlaneLoad,
    bolt_capacity: float,
    epsilon: float = 1e-12,
) -> ElasticSuperpositionResult:
    """Solve bolt demand with the elastic superposition method.

    Principle:
    - Direct shear equally distributed among bolts.
    - Torsional shear proportional to bolt distance from centroid.
    - Total bolt force is vector superposition.

    Equations:
    - Vx,dir = -Vx/n
    - Vy,dir = -Vy/n
    - Vx,t = Mz*dy/Ip
    - Vy,t = -Mz*dx/Ip
    """

    if geometry.bolt_count < 1:
        raise ValueError("Bolt group must contain at least one bolt.")
    if bolt_capacity <= 0.0:
        raise ValueError("bolt_capacity must be > 0.")
    if geometry.ip <= epsilon and abs(load.mz) > epsilon:
        raise ValueError("Elastic superposition requires Ip > 0 when Mz is applied.")

    direct_fx = -load.vx / float(geometry.bolt_count)
    direct_fy = -load.vy / float(geometry.bolt_count)

    bolt_forces: list[BoltForce] = []
    sum_fx = 0.0
    sum_fy = 0.0
    sum_mz = 0.0
    bolt_demand = 0.0

    for bolt in geometry.bolts:
        torsion_fx = load.mz * bolt.dy / geometry.ip if abs(load.mz) > epsilon else 0.0
        torsion_fy = -load.mz * bolt.dx / geometry.ip if abs(load.mz) > epsilon else 0.0
        fx = direct_fx + torsion_fx
        fy = direct_fy + torsion_fy
        resultant = math.hypot(fx, fy)
        moment_cg = -fx * bolt.dy + fy * bolt.dx

        sum_fx += fx
        sum_fy += fy
        sum_mz += moment_cg
        bolt_demand = max(bolt_demand, resultant)

        bolt_forces.append(
            BoltForce(
                tag=bolt.tag,
                fx=fx,
                fy=fy,
                resultant=resultant,
                moment_about_cg=moment_cg,
            )
        )

    return ElasticSuperpositionResult(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        bolt_forces=tuple(bolt_forces),
        bolt_demand=bolt_demand,
        bolt_capacity=bolt_capacity,
        dcr=bolt_demand / bolt_capacity,
        sum_fx=sum_fx,
        sum_fy=sum_fy,
        sum_mz=sum_mz,
    )


def solve_elastic_center_of_rotation(
    *,
    geometry: BoltGroupGeometry,
    load: InPlaneLoad,
    bolt_capacity: float,
    epsilon: float = 1e-12,
) -> ElasticECRResult:
    """Solve connection demand/capacity with Elastic Center of Rotation (ECR).

    Core steps:
    1) Compute ECR location from equilibrium of an elastic bolt group.
    2) Build force field tangent to radius from ECR.
    3) Compute global coefficient Ce and connection capacity.
    """

    if geometry.bolt_count < 1:
        raise ValueError("Bolt group must contain at least one bolt.")
    if bolt_capacity <= 0.0:
        raise ValueError("bolt_capacity must be > 0.")
    if abs(load.mz) <= epsilon:
        return ElasticECRResult(
            method=BoltGroupMethod.ELASTIC_ECR,
            applicable=False,
            note="Elastic ECR is not applicable when Mz=0.",
            center_x=None,
            center_y=None,
            ce=None,
            demand=None,
            capacity=None,
            dcr=None,
            bolt_forces=tuple(),
            sum_fx=None,
            sum_fy=None,
            sum_mz=None,
        )
    if geometry.ip <= epsilon:
        return ElasticECRResult(
            method=BoltGroupMethod.ELASTIC_ECR,
            applicable=False,
            note="Elastic ECR is not applicable because Ip is zero.",
            center_x=None,
            center_y=None,
            ce=None,
            demand=None,
            capacity=None,
            dcr=None,
            bolt_forces=tuple(),
            sum_fx=None,
            sum_fy=None,
            sum_mz=None,
        )

    n_bolts = float(geometry.bolt_count)
    ax = load.vy * geometry.ip / (load.mz * n_bolts)
    ay = load.vx * geometry.ip / (load.mz * n_bolts)
    center_x = geometry.centroid_x - ax
    center_y = geometry.centroid_y + ay

    ecc_x = load.ex + ax
    ecc_y = load.ey - ay
    ecc = math.hypot(ecc_x, ecc_y)

    radii = [math.hypot(bolt.x - center_x, bolt.y - center_y) for bolt in geometry.bolts]
    dmax = max(radii) if radii else 0.0
    sum_d2 = sum(value * value for value in radii)
    if dmax <= epsilon or sum_d2 <= epsilon:
        return ElasticECRResult(
            method=BoltGroupMethod.ELASTIC_ECR,
            applicable=False,
            note="Elastic ECR became singular (dmax or sum(d^2) is zero).",
            center_x=center_x,
            center_y=center_y,
            ce=None,
            demand=None,
            capacity=None,
            dcr=None,
            bolt_forces=tuple(),
            sum_fx=None,
            sum_fy=None,
            sum_mz=None,
        )

    if load.resultant <= epsilon:
        mp = 1.0
    else:
        mp = -(load.vx / load.resultant) * ecc_y + (load.vy / load.resultant) * ecc_x

    if abs(mp) <= epsilon:
        return ElasticECRResult(
            method=BoltGroupMethod.ELASTIC_ECR,
            applicable=False,
            note="Elastic ECR became singular because Mp is zero.",
            center_x=center_x,
            center_y=center_y,
            ce=None,
            demand=None,
            capacity=None,
            dcr=None,
            bolt_forces=tuple(),
            sum_fx=None,
            sum_fy=None,
            sum_mz=None,
        )

    ce = abs(sum_d2 / (mp * dmax))
    demand = abs(load.resultant) if ecc > epsilon else abs(load.mz)
    capacity = ce * bolt_capacity
    dcr = demand / capacity if capacity > epsilon else None

    if load.resultant <= epsilon:
        k_scale = mp / sum_d2 * load.mz
    else:
        k_scale = mp / sum_d2 * load.resultant

    bolt_forces: list[BoltForce] = []
    sum_fx = 0.0
    sum_fy = 0.0
    sum_mz = 0.0
    for bolt in geometry.bolts:
        dx_ecr = bolt.x - center_x
        dy_ecr = bolt.y - center_y
        fx = k_scale * dy_ecr
        fy = -k_scale * dx_ecr
        resultant = math.hypot(fx, fy)
        moment_cg = -fx * bolt.dy + fy * bolt.dx
        sum_fx += fx
        sum_fy += fy
        sum_mz += moment_cg
        bolt_forces.append(
            BoltForce(
                tag=bolt.tag,
                fx=fx,
                fy=fy,
                resultant=resultant,
                moment_about_cg=moment_cg,
            )
        )

    return ElasticECRResult(
        method=BoltGroupMethod.ELASTIC_ECR,
        applicable=True,
        note=None,
        center_x=center_x,
        center_y=center_y,
        ce=ce,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        bolt_forces=tuple(bolt_forces),
        sum_fx=sum_fx,
        sum_fy=sum_fy,
        sum_mz=sum_mz,
    )
