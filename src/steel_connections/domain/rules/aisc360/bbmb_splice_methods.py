from __future__ import annotations

import math
from typing import Any

from steel_connections.codes.engineering.common import BoltCoordinate
from steel_connections.codes.engineering.common import BoltGroupMethod
from steel_connections.codes.engineering.common import BoltGroupSolverOptions
from steel_connections.codes.engineering.common import build_bolt_group_geometry
from steel_connections.codes.engineering.common import build_in_plane_load_from_explicit_eccentricity
from steel_connections.codes.engineering.common import build_mirrored_half_flange_bolt_pattern
from steel_connections.codes.engineering.common import solve_bolt_group_method
from steel_connections.codes.engineering.common.bolt_group_types import (
    ElasticECRResult,
    ElasticSuperpositionResult,
    ICRResult,
)
from steel_connections.data.materials_repository import get_bolt_strength_properties
from steel_connections.data.sections_repository import get_beam_profile_properties
from steel_connections.data.sections_repository import get_bolt_section_properties
from steel_connections.models.errors import missing_required_input_error
from steel_connections.models.input import BeamBeamMomentBoltedCase, BeamBeamMomentBoltedICRSettings
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import Quantity, UnitSystem

KIP_TO_KN = 4.4482216152605
IN_TO_MM = 25.4
KIP_IN_TO_KN_MM = KIP_TO_KN * IN_TO_MM


def _to_kip(force: Quantity, unit_system: UnitSystem) -> float:
    if unit_system == UnitSystem.US:
        if force.unit != "kip":
            raise ValueError(f"Expected force in kip for US case, got '{force.unit}'.")
        return force.value
    if force.unit == "kN":
        return force.value / KIP_TO_KN
    if force.unit == "N":
        return (force.value / 1000.0) / KIP_TO_KN
    raise ValueError(f"Unsupported SI force unit '{force.unit}'. Expected kN or N.")


def _from_kip(force_kip: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=force_kip, unit="kip")
    return Quantity(value=force_kip * KIP_TO_KN, unit="kN")


def _to_in(length: Quantity, unit_system: UnitSystem) -> float:
    if unit_system == UnitSystem.US:
        if length.unit != "in":
            raise ValueError(f"Expected length in in for US case, got '{length.unit}'.")
        return length.value
    if length.unit != "mm":
        raise ValueError(f"Expected length in mm for SI case, got '{length.unit}'.")
    return length.value / IN_TO_MM


def _from_kip_in(moment_kip_in: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=moment_kip_in, unit="kip-in")
    return Quantity(value=moment_kip_in * KIP_IN_TO_KN_MM, unit="kN-mm")


def _selected_procedure_icr(case: BeamBeamMomentBoltedCase) -> BeamBeamMomentBoltedICRSettings:
    if case.procedure is None:
        return BeamBeamMomentBoltedICRSettings()
    return case.procedure


def _resolve_eccentricity(case: BeamBeamMomentBoltedCase) -> Quantity:
    # Splice convention fixed by project:
    # ex = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x-1)*g_blt_web
    alpha = case.geometry.gap_sp
    le_x1 = case.geometry.Le_blt_web_x1
    g_web = case.geometry.g_blt_web
    if alpha.unit != le_x1.unit or alpha.unit != g_web.unit:
        raise ValueError("Incompatible units in ex = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x-1)*g_blt_web")
    ex_value = alpha.value + 2.0 * le_x1.value + (case.geometry.n_blt_web_x - 1) * g_web.value
    return Quantity(value=ex_value, unit=alpha.unit)


def _resolve_eccentricity_components(
    *,
    case: BeamBeamMomentBoltedCase,
) -> tuple[Quantity, Quantity, str]:
    ex = _resolve_eccentricity(case)
    ey_input = case.loads.e2_blt_web
    if ey_input is None:
        ey = Quantity(value=0.0, unit=ex.unit)
        return ex, ey, "splice_formula_ex_and_default_ey_zero"
    if ey_input.unit != ex.unit:
        raise ValueError("Incompatible units in splice eccentricity components ex/ey.")
    ey = Quantity(value=ey_input.value, unit=ey_input.unit)
    return ex, ey, "splice_formula_ex_plus_input_ey"


def _web_group_points_in(case: BeamBeamMomentBoltedCase) -> tuple[BoltCoordinate, ...]:
    sx_in = _to_in(case.geometry.g_blt_web, case.units_system)
    sy_in = _to_in(case.geometry.p_blt_web, case.units_system)
    points: list[BoltCoordinate] = []
    index = 1
    for ix in range(case.geometry.n_blt_web_x):
        for iy in range(case.geometry.n_blt_web_y):
            points.append(
                BoltCoordinate(
                    tag=f"w{index}",
                    x=float(ix) * sx_in,
                    y=float(iy) * sy_in,
                )
            )
            index += 1
    return tuple(points)


def _flange_group_points_in(
    case: BeamBeamMomentBoltedCase,
) -> tuple[tuple[BoltCoordinate, ...], Quantity, list[float]]:
    beam_props = get_beam_profile_properties(
        beam_shape=case.sections.shape_vg,
        unit_system=case.units_system,
    )
    bf_vg = beam_props.get("bf")
    if not isinstance(bf_vg, Quantity):
        raise ValueError(f"Unable to resolve bf_vg for shape '{case.sections.shape_vg}'.")

    le_z3 = case.geometry.Le_blt_flange_z3
    g_flange = case.geometry.g_blt_flange
    if bf_vg.unit != le_z3.unit or bf_vg.unit != g_flange.unit:
        raise ValueError("Incompatible units in g1_blt_flange = bf_vg - 2*(Le_blt_flange_z3 + (n_blt_flange_z-1)*g_blt_flange)")

    g1_value = bf_vg.value - 2.0 * (le_z3.value + (case.geometry.n_blt_flange_z - 1) * g_flange.value)
    g1_blt_flange = Quantity(value=g1_value, unit=bf_vg.unit)

    px_in = _to_in(case.geometry.p_blt_flange, case.units_system)
    gz_in = _to_in(case.geometry.g_blt_flange, case.units_system)
    g1z_in = _to_in(g1_blt_flange, case.units_system)

    bolts = build_mirrored_half_flange_bolt_pattern(
        nx=case.geometry.n_blt_flange_x,
        nz_half=case.geometry.n_blt_flange_z,
        px=px_in,
        gz=gz_in,
        g1z=g1z_in,
        tag_prefix="f",
    )

    y_rows_positive_in = [0.5 * g1z_in + float(m) * gz_in for m in range(case.geometry.n_blt_flange_z)]
    y_rows_in = [-value for value in reversed(y_rows_positive_in)] + y_rows_positive_in
    return bolts, g1_blt_flange, y_rows_in


def _resolve_flange_step2_components(
    case: BeamBeamMomentBoltedCase,
) -> tuple[Quantity, Quantity, Quantity, Quantity, Quantity, str]:
    beam_props = get_beam_profile_properties(
        beam_shape=case.sections.shape_vg,
        unit_system=case.units_system,
    )
    d_vg = beam_props.get("d")
    tf_vg = beam_props.get("tf")
    if not isinstance(d_vg, Quantity) or not isinstance(tf_vg, Quantity):
        raise ValueError(f"Unable to resolve d_vg/tf_vg for shape '{case.sections.shape_vg}'.")

    if d_vg.unit != tf_vg.unit:
        raise ValueError("Incompatible units between d_vg and tf_vg.")
    clear_depth = d_vg.value - tf_vg.value
    if abs(clear_depth) <= 1e-12:
        raise ValueError("Invalid denominator (d_vg - tf_vg) for P3_blt_flange computation.")

    pu_sp = case.loads.Pu_sp
    mu3_sp = case.loads.Mu3_sp
    vu3_sp = case.loads.Vu3_sp
    if case.units_system == UnitSystem.US:
        force_unit = "kip"
        moment_unit = "kip-in"
    else:
        force_unit = "kN"
        moment_unit = "kN-mm"
    if pu_sp.unit != force_unit or vu3_sp.unit != force_unit:
        raise ValueError(f"Expected Pu_sp/Vu3_sp in '{force_unit}' for step2 pernos2.")
    if mu3_sp.unit != moment_unit:
        raise ValueError(f"Expected Mu3_sp in '{moment_unit}' for step2 pernos2.")

    p3_value = (1.0 - case.loads.alpha_Pu_web) * pu_sp.value + mu3_sp.value / clear_depth
    p3_blt_flange = Quantity(value=p3_value, unit=force_unit)
    v1_blt_flange = Quantity(value=0.5 * vu3_sp.value, unit=force_unit)

    gap_sp = case.geometry.gap_sp
    le_x1 = case.geometry.Le_blt_flange_x1
    p_flange = case.geometry.p_blt_flange
    if gap_sp.unit != le_x1.unit or gap_sp.unit != p_flange.unit:
        raise ValueError(
            "Incompatible units in e3_blt_flange = gap_sp + 2*Le_blt_flange_x1 + (n_blt_flange_x - 1)*p_blt_flange"
        )
    ex_value = gap_sp.value + 2.0 * le_x1.value + (case.geometry.n_blt_flange_x - 1) * p_flange.value
    e3_blt_flange = Quantity(value=ex_value, unit=gap_sp.unit)

    ez_input = case.loads.e1_blt_flange
    if ez_input is None:
        e1_blt_flange = Quantity(value=0.0, unit=e3_blt_flange.unit)
        eccentricity_source = "splice_formula_e3_and_default_e1_zero"
    else:
        if ez_input.unit != e3_blt_flange.unit:
            raise ValueError("Incompatible units in step2 pernos2 eccentricity components e3/e1.")
        e1_blt_flange = Quantity(value=ez_input.value, unit=ez_input.unit)
        eccentricity_source = "splice_formula_e3_plus_input_e1"

    mu2_value = v1_blt_flange.value * e3_blt_flange.value - p3_blt_flange.value * e1_blt_flange.value
    mu2_blt_flange = Quantity(value=mu2_value, unit=moment_unit)
    return (
        p3_blt_flange,
        v1_blt_flange,
        e3_blt_flange,
        e1_blt_flange,
        mu2_blt_flange,
        eccentricity_source,
    )


def _derive_elastic_bolt_capacity_kip(
    case: BeamBeamMomentBoltedCase,
    *,
    scope: str = "web",
) -> tuple[float, dict[str, Any]]:
    scope_norm = scope.strip().lower()
    if scope_norm == "web":
        bolt_shape = case.materials.shape_blt_web
        bolt_standard = case.materials.std_blt_web
        bolt_description = case.materials.desc_blt_web
        thread_raw = case.materials.thread_blt_web
        suffix = "web"
    elif scope_norm == "flange":
        bolt_shape = case.materials.shape_blt_flange
        bolt_standard = case.materials.std_blt_flange
        bolt_description = case.materials.desc_blt_flange
        thread_raw = case.materials.thread_blt_flange
        suffix = "flange"
    else:
        raise ValueError(f"Unsupported bolt-capacity scope '{scope}'.")

    if not bolt_standard.strip() or not bolt_description.strip():
        raise ValueError(f"std_blt_{suffix}/desc_blt_{suffix} are required to derive elastic bolt capacity.")

    bolt_geom_us = get_bolt_section_properties(bolt_shape=bolt_shape, unit_system=UnitSystem.US)
    db_us = bolt_geom_us["diameter_nominal"]
    if not isinstance(db_us, Quantity):
        raise ValueError("Unable to resolve bolt diameter for elastic bolt capacity.")
    area_in2 = math.pi * (db_us.value ** 2) / 4.0

    strengths_us = get_bolt_strength_properties(
        description=bolt_description,
        specification=bolt_standard,
        unit_system=UnitSystem.US,
    )
    thread = thread_raw.strip().upper()
    if thread == "N":
        fnv = strengths_us["fnv_threads_not_excluded"]
    elif thread == "X":
        fnv = strengths_us["fnv_threads_excluded"]
    else:
        raise ValueError(f"materials.thread_blt_{suffix} must be N or X.")
    if not isinstance(fnv, Quantity):
        raise ValueError("Unable to resolve bolt shear strength Fnv.")

    phi = case.design_factors.phi_bv
    bolt_capacity_kip = phi * fnv.value * area_in2
    return bolt_capacity_kip, {
        f"db_{suffix}_us": db_us.model_dump(),
        f"ab_{suffix}_in2": area_in2,
        f"fnv_{suffix}_us": fnv.model_dump(),
        "phi_bv": phi,
        f"std_blt_{suffix}": bolt_standard,
        f"desc_blt_{suffix}": bolt_description,
    }


def _to_method_enum(method: str) -> BoltGroupMethod:
    if method == "elastic_superposition":
        return BoltGroupMethod.ELASTIC_SUPERPOSITION
    if method == "elastic_ecr":
        return BoltGroupMethod.ELASTIC_ECR
    if method == "icr":
        return BoltGroupMethod.ICR
    raise ValueError(f"Unsupported method '{method}'.")


def _icr_summary(result: ICRResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "converged": result.converged,
        "note": result.note,
        "icr_x": result.icr_x,
        "icr_y": result.icr_y,
        "cu": result.cu,
        "demand": result.demand,
        "capacity": result.capacity,
        "dcr": result.dcr,
        "final_residual": result.final_residual,
        "n_iterations": len(result.iterations),
        "iterations": [
            {
                "iteration": item.iteration,
                "icr_x": item.icr_x,
                "icr_y": item.icr_y,
                "residual_fx": item.residual_fx,
                "residual_fy": item.residual_fy,
                "residual_norm": item.residual_norm,
                "step_dx": item.step_dx,
                "step_dy": item.step_dy,
            }
            for item in result.iterations
        ],
    }


def _solve_bolt_group_methods(
    *,
    method: str,
    tolerance: float,
    max_iterations: int,
    bolt_points: tuple[BoltCoordinate, ...],
    px_kip: float,
    py_kip: float,
    ex_in: float,
    ey_in: float,
    active_capacity_kip: float,
) -> dict[str, Any]:
    geometry = build_bolt_group_geometry(bolt_points)
    load = build_in_plane_load_from_explicit_eccentricity(
        vx=px_kip,
        vy=py_kip,
        ex=ex_in,
        ey=ey_in,
    )
    options = BoltGroupSolverOptions(
        tolerance=tolerance,
        max_iterations=max_iterations,
    )
    active_method = _to_method_enum(method)
    active_result = solve_bolt_group_method(
        method=active_method,
        geometry=geometry,
        load=load,
        bolt_capacity=active_capacity_kip,
        options=options,
    )

    icr_compare: ICRResult | None = None
    if method in {"elastic_superposition", "elastic_ecr"}:
        compare_result = solve_bolt_group_method(
            method=BoltGroupMethod.ICR,
            geometry=geometry,
            load=load,
            bolt_capacity=active_capacity_kip,
            options=options,
        )
        if isinstance(compare_result, ICRResult):
            icr_compare = compare_result

    return {
        "geometry": geometry,
        "load": load,
        "active_result": active_result,
        "icr_compare": icr_compare,
    }


def _is_not_applicable_when_mz_is_zero(note: str | None) -> bool:
    if not isinstance(note, str):
        return False
    return "not applicable when Mz=0" in note


def _build_mz_zero_not_applicable_note(method: str) -> str:
    return (
        f"Metodo seleccionado '{method}' no aplica cuando Mz=0. "
        "Cambia a 'elastic_superposition' para este grupo de pernos."
    )


def _summarize_method_result(
    *,
    method_name: str,
    result: ElasticSuperpositionResult | ElasticECRResult | ICRResult,
    tolerance: float,
    max_iterations: int,
    geometry: Any,
    load: Any,
    law_params: dict[str, float],
) -> dict[str, Any]:
    bolt_forces_table = [
        {
            "tag": item.tag,
            "fx_kip": item.fx,
            "fy_kip": item.fy,
            "resultant_kip": item.resultant,
            "moment_about_cg_kip_in": item.moment_about_cg,
        }
        for item in result.bolt_forces
    ]
    if isinstance(result, ElasticSuperpositionResult):
        status = "PASS" if result.dcr <= 1.0 else "FAIL"
        direct_fx = -load.vx / float(geometry.bolt_count)
        direct_fy = -load.vy / float(geometry.bolt_count)
        return {
            "method": method_name,
            "applicable": True,
            "status": status,
            "demand_kip": result.bolt_demand,
            "capacity_kip": result.bolt_capacity,
            "dcr": result.dcr,
            "direct_fx_kip": direct_fx,
            "direct_fy_kip": direct_fy,
            "ip_in2": geometry.ip,
            "sum_fx_kip": result.sum_fx,
            "sum_fy_kip": result.sum_fy,
            "sum_mz_kip_in": result.sum_mz,
            "bolt_forces": bolt_forces_table,
            "note": None,
        }
    if isinstance(result, ElasticECRResult):
        center_x = result.center_x
        center_y = result.center_y
        ax = geometry.centroid_x - center_x if center_x is not None else None
        ay = center_y - geometry.centroid_y if center_y is not None else None
        ecc_x = (load.ex + ax) if ax is not None else None
        ecc_y = (load.ey - ay) if ay is not None else None
        radii = []
        if center_x is not None and center_y is not None:
            radii = [math.hypot(bolt.x - center_x, bolt.y - center_y) for bolt in geometry.bolts]
        dmax = max(radii) if radii else None
        sum_d2 = sum(value * value for value in radii) if radii else None
        if not result.applicable or result.dcr is None:
            status = "PASS" if _is_not_applicable_when_mz_is_zero(result.note) else "FAIL"
            return {
                "method": method_name,
                "applicable": False,
                "status": status,
                "demand_kip": result.demand,
                "capacity_kip": result.capacity,
                "dcr": result.dcr,
                "ax_in": ax,
                "ay_in": ay,
                "ecc_x_in": ecc_x,
                "ecc_y_in": ecc_y,
                "dmax_in": dmax,
                "sum_d2_in2": sum_d2,
                "center_x_in": result.center_x,
                "center_y_in": result.center_y,
                "ce": result.ce,
                "sum_fx_kip": result.sum_fx,
                "sum_fy_kip": result.sum_fy,
                "sum_mz_kip_in": result.sum_mz,
                "bolt_forces": bolt_forces_table,
                "note": result.note,
            }
        status = "PASS" if result.dcr <= 1.0 else "FAIL"
        return {
            "method": method_name,
            "applicable": True,
            "status": status,
            "demand_kip": result.demand,
            "capacity_kip": result.capacity,
            "dcr": result.dcr,
            "ax_in": ax,
            "ay_in": ay,
            "ecc_x_in": ecc_x,
            "ecc_y_in": ecc_y,
            "dmax_in": dmax,
            "sum_d2_in2": sum_d2,
            "center_x_in": result.center_x,
            "center_y_in": result.center_y,
            "ce": result.ce,
            "sum_fx_kip": result.sum_fx,
            "sum_fy_kip": result.sum_fy,
            "sum_mz_kip_in": result.sum_mz,
            "bolt_forces": bolt_forces_table,
            "note": result.note,
        }
    # ICR
    n_iterations = len(result.iterations)
    if result.dcr is None and _is_not_applicable_when_mz_is_zero(result.note):
        return {
            "method": method_name,
            "applicable": False,
            "status": "PASS",
            "converged": result.converged,
            "acceptance_ok": False,
            "demand_kip": result.demand,
            "capacity_kip": result.capacity,
            "dcr": result.dcr,
            "icr_x_in": result.icr_x,
            "icr_y_in": result.icr_y,
            "cu": result.cu,
            "final_residual": result.final_residual,
            "n_iterations": n_iterations,
            "law_mu": law_params["mu"],
            "law_lambda": law_params["lambda_exp"],
            "law_delta_max": law_params["delta_max"],
            "bolt_forces": bolt_forces_table,
            "note": result.note,
        }
    acceptance = (
        result.converged
        and result.final_residual <= tolerance
        and n_iterations <= max_iterations
        and result.dcr is not None
    )
    status = "PASS" if (acceptance and result.dcr is not None and result.dcr <= 1.0) else "FAIL"
    return {
        "method": method_name,
        "applicable": True,
        "status": status,
        "converged": result.converged,
        "acceptance_ok": acceptance,
        "demand_kip": result.demand,
        "capacity_kip": result.capacity,
        "dcr": result.dcr,
        "icr_x_in": result.icr_x,
        "icr_y_in": result.icr_y,
        "cu": result.cu,
        "final_residual": result.final_residual,
        "n_iterations": n_iterations,
        "law_mu": law_params["mu"],
        "law_lambda": law_params["lambda_exp"],
        "law_delta_max": law_params["delta_max"],
        "bolt_forces": bolt_forces_table,
        "note": result.note,
    }


def run_step2_pernos1_method(case: BeamBeamMomentBoltedCase, rule_binding: object) -> CheckResult:
    procedure_icr = _selected_procedure_icr(case)
    method = procedure_icr.method_1 or "elastic_superposition"
    tolerance = procedure_icr.tolerance_1
    max_iterations = procedure_icr.max_iterations_1

    px_kip = abs(_to_kip(case.loads.Pu_sp, case.units_system))
    py_kip = abs(_to_kip(case.loads.Vu2_sp, case.units_system))
    ex, ey, eccentricity_source = _resolve_eccentricity_components(case=case)
    ex_in = _to_in(ex, case.units_system)
    ey_in = _to_in(ey, case.units_system)
    mz_kip_in = py_kip * ex_in - px_kip * ey_in
    bolt_points = _web_group_points_in(case)

    elastic_capacity_kip, elastic_meta = _derive_elastic_bolt_capacity_kip(case)
    if method == "icr":
        if procedure_icr.rult_1_kip is None:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=["procedure.rult_1_kip"],
                message="Required input 'procedure.rult_1_kip' is missing when method_1='icr'.",
            )
        bolt_capacity_active_kip = procedure_icr.rult_1_kip.value
    else:
        bolt_capacity_active_kip = elastic_capacity_kip

    solved = _solve_bolt_group_methods(
        method=method,
        tolerance=tolerance,
        max_iterations=max_iterations,
        bolt_points=bolt_points,
        px_kip=px_kip,
        py_kip=py_kip,
        ex_in=ex_in,
        ey_in=ey_in,
        active_capacity_kip=bolt_capacity_active_kip,
    )
    active_result = solved["active_result"]
    icr_compare = solved["icr_compare"]
    geometry = solved["geometry"]
    load = solved["load"]

    method_effective = method

    demand: Quantity | None = None
    capacity: Quantity | None = None
    dcr: float | None = None
    status = CheckStatus.FAIL
    equation = "bbmb_splice Punto 2 pernos 1: solver interno ICR/Elastic"
    notes: str | None = None
    active_mode_data: dict[str, Any] = {
        "method_selected": method,
        "method_effective": method_effective,
    }

    if isinstance(active_result, ElasticSuperpositionResult):
        dcr = active_result.dcr
        demand = _from_kip(active_result.bolt_demand, case.units_system)
        capacity = _from_kip(active_result.bolt_capacity, case.units_system)
        status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
        equation = "Elastic Superposition: DCR = BoltDemand / BoltCapacity"
        active_mode_data.update(
            {
                "demand_kip": active_result.bolt_demand,
                "capacity_kip": active_result.bolt_capacity,
                "dcr": dcr,
                "sum_fx_kip": active_result.sum_fx,
                "sum_fy_kip": active_result.sum_fy,
                "sum_mz_kip_in": active_result.sum_mz,
            }
        )
    elif isinstance(active_result, ElasticECRResult):
        if not active_result.applicable or active_result.dcr is None:
            status = CheckStatus.FAIL
            if _is_not_applicable_when_mz_is_zero(active_result.note):
                notes = _build_mz_zero_not_applicable_note(method)
            else:
                notes = active_result.note or "Elastic ECR method is not applicable for this load state."
            active_mode_data.update({"applicable": False, "note": active_result.note})
        else:
            dcr = active_result.dcr
            demand = _from_kip(active_result.demand, case.units_system) if active_result.demand is not None else None
            capacity = (
                _from_kip(active_result.capacity, case.units_system) if active_result.capacity is not None else None
            )
            status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
            active_mode_data.update(
                {
                    "applicable": True,
                    "center_x_in": active_result.center_x,
                    "center_y_in": active_result.center_y,
                    "ce": active_result.ce,
                    "demand_kip": active_result.demand,
                    "capacity_kip": active_result.capacity,
                    "dcr": dcr,
                    "sum_fx_kip": active_result.sum_fx,
                    "sum_fy_kip": active_result.sum_fy,
                    "sum_mz_kip_in": active_result.sum_mz,
                }
            )
        equation = "Elastic ECR: DCR = ConnectionDemand / ConnectionCapacity"
    elif isinstance(active_result, ICRResult):
        n_iterations = len(active_result.iterations)
        converged = (
            active_result.converged
            and active_result.final_residual <= tolerance
            and n_iterations <= max_iterations
            and active_result.dcr is not None
        )
        dcr = active_result.dcr
        if converged and active_result.demand is not None and active_result.capacity is not None:
            demand = _from_kip(active_result.demand, case.units_system)
            capacity = _from_kip(active_result.capacity, case.units_system)
            status = CheckStatus.PASS if (dcr is not None and dcr <= 1.0) else CheckStatus.FAIL
        else:
            status = CheckStatus.FAIL
            if _is_not_applicable_when_mz_is_zero(active_result.note):
                notes = _build_mz_zero_not_applicable_note(method)
            else:
                notes = (
                    "ICR did not satisfy configured convergence acceptance "
                    f"(tol={tolerance}, max_iterations={max_iterations})."
                )
        active_mode_data.update(
            {
                "converged": active_result.converged,
                "icr_x_in": active_result.icr_x,
                "icr_y_in": active_result.icr_y,
                "cu": active_result.cu,
                "demand_kip": active_result.demand,
                "capacity_kip": active_result.capacity,
                "dcr": dcr,
                "final_residual": active_result.final_residual,
                "n_iterations": n_iterations,
                "solver_note": active_result.note,
            }
        )
        equation = "ICR: DCR = ConnectionDemand / ConnectionCapacity"
    else:
        raise TypeError("Unexpected bolt-group solver result type.")

    icr_report_source: ICRResult | None = active_result if isinstance(active_result, ICRResult) else icr_compare
    icr_capacity_compare_kip: float | None = None
    if method in {"elastic_superposition", "elastic_ecr"} and icr_compare is not None and icr_compare.capacity is not None:
        icr_capacity_compare_kip = icr_compare.capacity

    # Always compute a complete comparative bundle for reporting tables,
    # independent of selected method in JSON.
    geometry_all = build_bolt_group_geometry(bolt_points)
    load_all = build_in_plane_load_from_explicit_eccentricity(
        vx=px_kip,
        vy=py_kip,
        ex=ex_in,
        ey=ey_in,
    )
    options_all = BoltGroupSolverOptions(tolerance=tolerance, max_iterations=max_iterations)
    icr_reporting_capacity_kip = (
        procedure_icr.rult_1_kip.value if procedure_icr.rult_1_kip is not None else elastic_capacity_kip
    )
    result_elastic_superposition = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        geometry=geometry_all,
        load=load_all,
        bolt_capacity=elastic_capacity_kip,
        options=options_all,
    )
    result_elastic_ecr = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_ECR,
        geometry=geometry_all,
        load=load_all,
        bolt_capacity=elastic_capacity_kip,
        options=options_all,
    )
    result_icr = solve_bolt_group_method(
        method=BoltGroupMethod.ICR,
        geometry=geometry_all,
        load=load_all,
        bolt_capacity=icr_reporting_capacity_kip,
        options=options_all,
    )
    methods_summary = [
        _summarize_method_result(
            method_name="elastic_superposition",
            result=result_elastic_superposition,
            tolerance=tolerance,
            max_iterations=max_iterations,
            geometry=geometry_all,
            load=load_all,
            law_params={"mu": options_all.icr_law.mu, "lambda_exp": options_all.icr_law.lambda_exp, "delta_max": options_all.icr_law.delta_max},
        ),
        _summarize_method_result(
            method_name="elastic_ecr",
            result=result_elastic_ecr,
            tolerance=tolerance,
            max_iterations=max_iterations,
            geometry=geometry_all,
            load=load_all,
            law_params={"mu": options_all.icr_law.mu, "lambda_exp": options_all.icr_law.lambda_exp, "delta_max": options_all.icr_law.delta_max},
        ),
        _summarize_method_result(
            method_name="icr",
            result=result_icr,
            tolerance=tolerance,
            max_iterations=max_iterations,
            geometry=geometry_all,
            load=load_all,
            law_params={"mu": options_all.icr_law.mu, "lambda_exp": options_all.icr_law.lambda_exp, "delta_max": options_all.icr_law.delta_max},
        ),
    ]
    icr_iterations_table = []
    if isinstance(result_icr, ICRResult):
        icr_iterations_table = [
            {
                "iteration": item.iteration,
                "icr_x": item.icr_x,
                "icr_y": item.icr_y,
                "residual_fx": item.residual_fx,
                "residual_fy": item.residual_fy,
                "residual_norm": item.residual_norm,
                "step_dx": item.step_dx,
                "step_dy": item.step_dy,
            }
            for item in result_icr.iterations
        ]

    memory = CalculationMemory(
        inputs={
            "method_selected": method,
            "method_effective": method_effective,
            "P3_blt_web": case.loads.Pu_sp.model_dump(),
            "v2_blt_web": case.loads.Vu2_sp.model_dump(),
            "e3_blt_web": ex.model_dump(),
            "e2_blt_web": ey.model_dump(),
            "eccentricity_source": eccentricity_source,
            "Mu1_blt_web": _from_kip_in(mz_kip_in, case.units_system).model_dump(),
            "n_blt_web_x": case.geometry.n_blt_web_x,
            "n_blt_web_y": case.geometry.n_blt_web_y,
            "bolt_group_1_points_in": [{"tag": point.tag, "x": point.x, "y": point.y} for point in bolt_points],
            "tolerance_1": tolerance,
            "max_iterations_1": max_iterations,
            "rult_1_kip": (
                case.procedure.rult_1_kip.model_dump()
                if case.procedure is not None and case.procedure.rult_1_kip is not None
                else None
            ),
        },
        intermediates={
            "elastic_capacity_basis": elastic_meta,
            "bolt_group_geometry": {
                "bolt_count": geometry.bolt_count,
                "centroid_x_in": geometry.centroid_x,
                "centroid_y_in": geometry.centroid_y,
                "ix_in2": geometry.ix,
                "iy_in2": geometry.iy,
                "ixy_in2": geometry.ixy,
                "ip_in2": geometry.ip,
                "bolts_offsets": [
                    {
                        "tag": bolt.tag,
                        "x_in": bolt.x,
                        "y_in": bolt.y,
                        "dx_in": bolt.dx,
                        "dy_in": bolt.dy,
                        "r_in": bolt.radius,
                    }
                    for bolt in geometry.bolts
                ],
            },
            "load_in_plane_kip_in": {
                "vx_kip": load.vx,
                "vy_kip": load.vy,
                "mz_kip_in": load.mz,
                "ex_in": load.ex,
                "ey_in": load.ey,
                "resultant_kip": load.resultant,
            },
            "active_mode_data": active_mode_data,
            "icr_active_or_compare": _icr_summary(icr_report_source),
            "icr_compare_capacity": (
                _from_kip(icr_capacity_compare_kip, case.units_system).model_dump()
                if icr_capacity_compare_kip is not None
                else None
            ),
            "method_report": {
                "id": "bbmb_splice.step2.pernos1.method",
                "scope": "pernos_1",
                "method_selected": method,
                "method_effective": method_effective,
                "px": _from_kip(px_kip, case.units_system).model_dump(),
                "py": _from_kip(py_kip, case.units_system).model_dump(),
                "ex": ex.model_dump(),
                "ey": ey.model_dump(),
                "eccentricity_source": eccentricity_source,
                "mz": _from_kip_in(mz_kip_in, case.units_system).model_dump(),
                "demand": demand.model_dump() if demand is not None else None,
                "capacity": capacity.model_dump() if capacity is not None else None,
                "dcr": dcr,
                "status": status.value,
                "cu": icr_report_source.cu if icr_report_source is not None else None,
                "icr_compare_capacity": (
                    _from_kip(icr_capacity_compare_kip, case.units_system).model_dump()
                    if icr_capacity_compare_kip is not None
                    else None
                ),
                "final_residual": icr_report_source.final_residual if icr_report_source is not None else None,
                "n_iterations": len(icr_report_source.iterations) if icr_report_source is not None else None,
                "methods_summary": methods_summary,
                "icr_iterations": icr_iterations_table,
                "capacity_basis": {
                    "elastic_capacity_kip": elastic_capacity_kip,
                    "icr_reporting_capacity_kip": icr_reporting_capacity_kip,
                },
            },
        },
        design_factors={
            "phi_bv": case.design_factors.phi_bv,
        },
        equation=equation,
        units_trace={
            "P3_blt_web": case.loads.Pu_sp.unit,
            "v2_blt_web": case.loads.Vu2_sp.unit,
            "e3_blt_web": ex.unit,
            "e2_blt_web": ey.unit,
            "Mu1_blt_web": "kip-in" if case.units_system == UnitSystem.US else "kN-mm",
        },
        final_capacity=capacity,
    )
    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        status=status,
        calculation_memory=memory,
        notes=notes,
    )


def run_step2_pernos2_method(case: BeamBeamMomentBoltedCase, rule_binding: object) -> CheckResult:
    procedure_icr = _selected_procedure_icr(case)
    method = procedure_icr.method_2 or "elastic_superposition"
    tolerance = procedure_icr.tolerance_2
    max_iterations = procedure_icr.max_iterations_2

    p3_blt_flange, v1_blt_flange, e3_blt_flange, e1_blt_flange, mu2_blt_flange, eccentricity_source = (
        _resolve_flange_step2_components(case)
    )

    px_kip = _to_kip(p3_blt_flange, case.units_system)
    py_kip = _to_kip(v1_blt_flange, case.units_system)
    ex_in = _to_in(e3_blt_flange, case.units_system)
    ey_in = _to_in(e1_blt_flange, case.units_system)
    mz_kip_in = py_kip * ex_in - px_kip * ey_in
    bolt_points, g1_blt_flange, _y_rows_in = _flange_group_points_in(case)

    elastic_capacity_kip, elastic_meta = _derive_elastic_bolt_capacity_kip(case, scope="flange")
    if method == "icr":
        if procedure_icr.rult_2_kip is None:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=["procedure.rult_2_kip"],
                message="Required input 'procedure.rult_2_kip' is missing when method_2='icr' for pernos 2.",
            )
        bolt_capacity_active_kip = procedure_icr.rult_2_kip.value
    else:
        bolt_capacity_active_kip = elastic_capacity_kip

    solved = _solve_bolt_group_methods(
        method=method,
        tolerance=tolerance,
        max_iterations=max_iterations,
        bolt_points=bolt_points,
        px_kip=px_kip,
        py_kip=py_kip,
        ex_in=ex_in,
        ey_in=ey_in,
        active_capacity_kip=bolt_capacity_active_kip,
    )
    active_result = solved["active_result"]
    icr_compare = solved["icr_compare"]
    geometry = solved["geometry"]
    load = solved["load"]

    method_effective = method

    demand: Quantity | None = None
    capacity: Quantity | None = None
    dcr: float | None = None
    status = CheckStatus.FAIL
    equation = "bbmb_splice Punto 2 pernos 2: solver interno ICR/Elastic"
    notes: str | None = None
    active_mode_data: dict[str, Any] = {
        "method_selected": method,
        "method_effective": method_effective,
    }

    if isinstance(active_result, ElasticSuperpositionResult):
        dcr = active_result.dcr
        demand = _from_kip(active_result.bolt_demand, case.units_system)
        capacity = _from_kip(active_result.bolt_capacity, case.units_system)
        status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
        equation = "Elastic Superposition: DCR = BoltDemand / BoltCapacity"
        active_mode_data.update(
            {
                "demand_kip": active_result.bolt_demand,
                "capacity_kip": active_result.bolt_capacity,
                "dcr": dcr,
                "sum_fx_kip": active_result.sum_fx,
                "sum_fy_kip": active_result.sum_fy,
                "sum_mz_kip_in": active_result.sum_mz,
            }
        )
    elif isinstance(active_result, ElasticECRResult):
        if not active_result.applicable or active_result.dcr is None:
            status = CheckStatus.FAIL
            if _is_not_applicable_when_mz_is_zero(active_result.note):
                notes = _build_mz_zero_not_applicable_note(method)
            else:
                notes = active_result.note or "Elastic ECR method is not applicable for this load state."
            active_mode_data.update({"applicable": False, "note": active_result.note})
        else:
            dcr = active_result.dcr
            demand = _from_kip(active_result.demand, case.units_system) if active_result.demand is not None else None
            capacity = (
                _from_kip(active_result.capacity, case.units_system) if active_result.capacity is not None else None
            )
            status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
            active_mode_data.update(
                {
                    "applicable": True,
                    "center_x_in": active_result.center_x,
                    "center_y_in": active_result.center_y,
                    "ce": active_result.ce,
                    "demand_kip": active_result.demand,
                    "capacity_kip": active_result.capacity,
                    "dcr": dcr,
                    "sum_fx_kip": active_result.sum_fx,
                    "sum_fy_kip": active_result.sum_fy,
                    "sum_mz_kip_in": active_result.sum_mz,
                }
            )
        equation = "Elastic ECR: DCR = ConnectionDemand / ConnectionCapacity"
    elif isinstance(active_result, ICRResult):
        n_iterations = len(active_result.iterations)
        converged = (
            active_result.converged
            and active_result.final_residual <= tolerance
            and n_iterations <= max_iterations
            and active_result.dcr is not None
        )
        dcr = active_result.dcr
        if converged and active_result.demand is not None and active_result.capacity is not None:
            demand = _from_kip(active_result.demand, case.units_system)
            capacity = _from_kip(active_result.capacity, case.units_system)
            status = CheckStatus.PASS if (dcr is not None and dcr <= 1.0) else CheckStatus.FAIL
        else:
            status = CheckStatus.FAIL
            if _is_not_applicable_when_mz_is_zero(active_result.note):
                notes = _build_mz_zero_not_applicable_note(method)
            else:
                notes = (
                    "ICR did not satisfy configured convergence acceptance "
                    f"(tol={tolerance}, max_iterations={max_iterations})."
                )
        active_mode_data.update(
            {
                "converged": active_result.converged,
                "icr_x_in": active_result.icr_x,
                "icr_y_in": active_result.icr_y,
                "cu": active_result.cu,
                "demand_kip": active_result.demand,
                "capacity_kip": active_result.capacity,
                "dcr": dcr,
                "final_residual": active_result.final_residual,
                "n_iterations": n_iterations,
                "solver_note": active_result.note,
            }
        )
        equation = "ICR: DCR = ConnectionDemand / ConnectionCapacity"
    else:
        raise TypeError("Unexpected bolt-group solver result type.")

    icr_report_source: ICRResult | None = active_result if isinstance(active_result, ICRResult) else icr_compare
    icr_capacity_compare_kip: float | None = None
    if method in {"elastic_superposition", "elastic_ecr"} and icr_compare is not None and icr_compare.capacity is not None:
        icr_capacity_compare_kip = icr_compare.capacity

    geometry_all = build_bolt_group_geometry(bolt_points)
    load_all = build_in_plane_load_from_explicit_eccentricity(
        vx=px_kip,
        vy=py_kip,
        ex=ex_in,
        ey=ey_in,
    )
    options_all = BoltGroupSolverOptions(tolerance=tolerance, max_iterations=max_iterations)
    icr_reporting_capacity_kip = (
        procedure_icr.rult_2_kip.value if procedure_icr.rult_2_kip is not None else elastic_capacity_kip
    )
    result_elastic_superposition = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        geometry=geometry_all,
        load=load_all,
        bolt_capacity=elastic_capacity_kip,
        options=options_all,
    )
    result_elastic_ecr = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_ECR,
        geometry=geometry_all,
        load=load_all,
        bolt_capacity=elastic_capacity_kip,
        options=options_all,
    )
    result_icr = solve_bolt_group_method(
        method=BoltGroupMethod.ICR,
        geometry=geometry_all,
        load=load_all,
        bolt_capacity=icr_reporting_capacity_kip,
        options=options_all,
    )
    methods_summary = [
        _summarize_method_result(
            method_name="elastic_superposition",
            result=result_elastic_superposition,
            tolerance=tolerance,
            max_iterations=max_iterations,
            geometry=geometry_all,
            load=load_all,
            law_params={"mu": options_all.icr_law.mu, "lambda_exp": options_all.icr_law.lambda_exp, "delta_max": options_all.icr_law.delta_max},
        ),
        _summarize_method_result(
            method_name="elastic_ecr",
            result=result_elastic_ecr,
            tolerance=tolerance,
            max_iterations=max_iterations,
            geometry=geometry_all,
            load=load_all,
            law_params={"mu": options_all.icr_law.mu, "lambda_exp": options_all.icr_law.lambda_exp, "delta_max": options_all.icr_law.delta_max},
        ),
        _summarize_method_result(
            method_name="icr",
            result=result_icr,
            tolerance=tolerance,
            max_iterations=max_iterations,
            geometry=geometry_all,
            load=load_all,
            law_params={"mu": options_all.icr_law.mu, "lambda_exp": options_all.icr_law.lambda_exp, "delta_max": options_all.icr_law.delta_max},
        ),
    ]
    icr_iterations_table = []
    if isinstance(result_icr, ICRResult):
        icr_iterations_table = [
            {
                "iteration": item.iteration,
                "icr_x": item.icr_x,
                "icr_y": item.icr_y,
                "residual_fx": item.residual_fx,
                "residual_fy": item.residual_fy,
                "residual_norm": item.residual_norm,
                "step_dx": item.step_dx,
                "step_dy": item.step_dy,
            }
            for item in result_icr.iterations
        ]

    memory = CalculationMemory(
        inputs={
            "method_selected": method,
            "method_effective": method_effective,
            "P3_blt_flange": p3_blt_flange.model_dump(),
            "v1_blt_flange": v1_blt_flange.model_dump(),
            "e3_blt_flange": e3_blt_flange.model_dump(),
            "e1_blt_flange": e1_blt_flange.model_dump(),
            "eccentricity_source": eccentricity_source,
            "Mu2_blt_flange": mu2_blt_flange.model_dump(),
            "g1_blt_flange": g1_blt_flange.model_dump(),
            "n_blt_flange_x": case.geometry.n_blt_flange_x,
            "n_blt_flange_z": case.geometry.n_blt_flange_z,
            "bolt_group_2_points_in": [{"tag": point.tag, "x": point.x, "y": point.y} for point in bolt_points],
            "tolerance_2": tolerance,
            "max_iterations_2": max_iterations,
            "rult_2_kip": (
                case.procedure.rult_2_kip.model_dump()
                if case.procedure is not None and case.procedure.rult_2_kip is not None
                else None
            ),
        },
        intermediates={
            "elastic_capacity_basis": elastic_meta,
            "bolt_group_geometry": {
                "bolt_count": geometry.bolt_count,
                "centroid_x_in": geometry.centroid_x,
                "centroid_y_in": geometry.centroid_y,
                "ix_in2": geometry.ix,
                "iy_in2": geometry.iy,
                "ixy_in2": geometry.ixy,
                "ip_in2": geometry.ip,
                "bolts_offsets": [
                    {
                        "tag": bolt.tag,
                        "x_in": bolt.x,
                        "y_in": bolt.y,
                        "dx_in": bolt.dx,
                        "dy_in": bolt.dy,
                        "r_in": bolt.radius,
                    }
                    for bolt in geometry.bolts
                ],
            },
            "load_in_plane_kip_in": {
                "vx_kip": load.vx,
                "vy_kip": load.vy,
                "mz_kip_in": load.mz,
                "ex_in": load.ex,
                "ey_in": load.ey,
                "resultant_kip": load.resultant,
            },
            "active_mode_data": active_mode_data,
            "icr_active_or_compare": _icr_summary(icr_report_source),
            "icr_compare_capacity": (
                _from_kip(icr_capacity_compare_kip, case.units_system).model_dump()
                if icr_capacity_compare_kip is not None
                else None
            ),
            "method_report": {
                "id": "bbmb_splice.step2.pernos2.method",
                "scope": "pernos_2",
                "method_selected": method,
                "method_effective": method_effective,
                "px": p3_blt_flange.model_dump(),
                "py": v1_blt_flange.model_dump(),
                "ex": e3_blt_flange.model_dump(),
                "ey": e1_blt_flange.model_dump(),
                "eccentricity_source": eccentricity_source,
                "mz": mu2_blt_flange.model_dump(),
                "demand": demand.model_dump() if demand is not None else None,
                "capacity": capacity.model_dump() if capacity is not None else None,
                "dcr": dcr,
                "status": status.value,
                "cu": icr_report_source.cu if icr_report_source is not None else None,
                "icr_compare_capacity": (
                    _from_kip(icr_capacity_compare_kip, case.units_system).model_dump()
                    if icr_capacity_compare_kip is not None
                    else None
                ),
                "final_residual": icr_report_source.final_residual if icr_report_source is not None else None,
                "n_iterations": len(icr_report_source.iterations) if icr_report_source is not None else None,
                "methods_summary": methods_summary,
                "icr_iterations": icr_iterations_table,
                "capacity_basis": {
                    "elastic_capacity_kip": elastic_capacity_kip,
                    "icr_reporting_capacity_kip": icr_reporting_capacity_kip,
                },
            },
        },
        design_factors={
            "phi_bv": case.design_factors.phi_bv,
        },
        equation=equation,
        units_trace={
            "P3_blt_flange": p3_blt_flange.unit,
            "v1_blt_flange": v1_blt_flange.unit,
            "e3_blt_flange": e3_blt_flange.unit,
            "e1_blt_flange": e1_blt_flange.unit,
            "Mu2_blt_flange": mu2_blt_flange.unit,
        },
        final_capacity=capacity,
    )
    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        status=status,
        calculation_memory=memory,
        notes=notes,
    )
