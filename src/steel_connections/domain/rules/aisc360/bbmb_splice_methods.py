from __future__ import annotations

import math
from typing import Any

from steel_connections.codes.engineering.common import BoltCoordinate
from steel_connections.codes.engineering.common import BoltGroupMethod
from steel_connections.codes.engineering.common import BoltGroupSolverOptions
from steel_connections.codes.engineering.common import build_bolt_group_geometry
from steel_connections.codes.engineering.common import build_in_plane_load_from_explicit_eccentricity
from steel_connections.codes.engineering.common import solve_bolt_group_method
from steel_connections.codes.engineering.common.bolt_group_types import (
    ElasticECRResult,
    ElasticSuperpositionResult,
    ICRResult,
)
from steel_connections.data.materials_repository import get_bolt_strength_properties
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
    return case.procedure.icr


def _resolve_eccentricity(case: BeamBeamMomentBoltedCase) -> Quantity:
    alpha = case.geometry.splice_gap
    le1_x1 = case.geometry.web_bolt_edge_distance_x1 or case.geometry.web_bolt_edge_distance
    sx = case.geometry.web_bolt_gage
    if alpha.unit != le1_x1.unit or alpha.unit != sx.unit:
        raise ValueError("Incompatible units in e = sep + 2*Le1.x1 + (nb1.x-1)*S1.x")
    e_value = alpha.value + 2.0 * le1_x1.value + (case.geometry.web_bolt_lines - 1) * sx.value
    return Quantity(value=e_value, unit=alpha.unit)


def _resolve_eccentricity_components(
    *,
    case: BeamBeamMomentBoltedCase,
) -> tuple[Quantity, Quantity, str]:
    # Splice-specific convention requested by user:
    # ex = sep + 2*Le1.x1 + (nb1.x-1)*S1.x
    # ey = input loads.eccentricity_ey (default 0)
    ex = _resolve_eccentricity(case)
    ey_input = case.loads.eccentricity_ey
    if ey_input is None:
        ey = Quantity(value=0.0, unit=ex.unit)
        return ex, ey, "splice_formula_ex_and_default_ey_zero"
    if ey_input.unit != ex.unit:
        raise ValueError("Incompatible units in splice eccentricity components ex/ey.")
    ey = Quantity(value=ey_input.value, unit=ey_input.unit)
    return ex, ey, "splice_formula_ex_plus_input_ey"


def _web_group_points_in(case: BeamBeamMomentBoltedCase) -> tuple[BoltCoordinate, ...]:
    sx_in = _to_in(case.geometry.web_bolt_gage, case.units_system)
    sy_in = _to_in(case.geometry.web_bolt_pitch, case.units_system)
    points: list[BoltCoordinate] = []
    index = 1
    for ix in range(case.geometry.web_bolt_lines):
        for iy in range(case.geometry.web_bolt_rows_per_side):
            points.append(
                BoltCoordinate(
                    tag=f"w{index}",
                    x=float(ix) * sx_in,
                    y=float(iy) * sy_in,
                )
            )
            index += 1
    return tuple(points)


def _derive_elastic_bolt_capacity_kip(case: BeamBeamMomentBoltedCase) -> tuple[float, dict[str, Any]]:
    bolt_shape = case.materials.bolt_shape_web or case.materials.bolt_shape
    bolt_standard = case.materials.bolt_fabrication_standard_web or case.materials.bolt_fabrication_standard
    bolt_description = case.materials.bolt_description
    if not bolt_standard.strip() or not bolt_description.strip():
        raise ValueError("Bolt standard/description are required to derive elastic bolt capacity.")

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
    thread = case.materials.bolt_thread_condition.strip().upper()
    if thread == "N":
        fnv = strengths_us["fnv_threads_not_excluded"]
    elif thread == "X":
        fnv = strengths_us["fnv_threads_excluded"]
    else:
        raise ValueError("materials.bolt_thread_condition must be N or X.")
    if not isinstance(fnv, Quantity):
        raise ValueError("Unable to resolve bolt shear strength Fnv.")

    phi = case.design_factors.phi_bolt_shear
    bolt_capacity_kip = phi * fnv.value * area_in2
    return bolt_capacity_kip, {
        "db_web_us": db_us.model_dump(),
        "ab_web_in2": area_in2,
        "fnv_web_us": fnv.model_dump(),
        "phi_bolt_shear": phi,
        "bolt_standard_web": bolt_standard,
        "bolt_description_web": bolt_description,
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


def run_step2_pernos1_method(case: BeamBeamMomentBoltedCase, rule_binding: object) -> CheckResult:
    procedure_icr = _selected_procedure_icr(case)
    method = procedure_icr.method
    tolerance = procedure_icr.tolerance_1
    max_iterations = procedure_icr.max_iterations_1

    px_kip = abs(_to_kip(case.loads.axial_right_end, case.units_system))
    py_kip = abs(_to_kip(case.loads.shear_right_end, case.units_system))
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
                missing_fields=["procedure.icr.rult_1_kip"],
                message="Required input 'procedure.icr.rult_1_kip' is missing when method='icr'.",
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

    demand: Quantity | None = None
    capacity: Quantity | None = None
    dcr: float | None = None
    status = CheckStatus.FAIL
    equation = "bbmb_splice Step 2 pernos 1: internal nonlinear/elastic bolt-group solver"
    notes: str | None = None
    active_mode_data: dict[str, Any] = {"method": method}

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

    memory = CalculationMemory(
        inputs={
            "method_selected": method,
            "px": case.loads.axial_right_end.model_dump(),
            "py": case.loads.shear_right_end.model_dump(),
            "ex": ex.model_dump(),
            "ey": ey.model_dump(),
            "eccentricity_source": eccentricity_source,
            "mz": _from_kip_in(mz_kip_in, case.units_system).model_dump(),
            "bolt_group_1_nx": case.geometry.web_bolt_lines,
            "bolt_group_1_ny": case.geometry.web_bolt_rows_per_side,
            "bolt_group_1_points_in": [{"tag": point.tag, "x": point.x, "y": point.y} for point in bolt_points],
            "tolerance_1": tolerance,
            "max_iterations_1": max_iterations,
            "rult_1_kip": (
                case.procedure.icr.rult_1_kip.model_dump()
                if case.procedure is not None and case.procedure.icr.rult_1_kip is not None
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
            },
        },
        design_factors={
            "phi_bolt_shear": case.design_factors.phi_bolt_shear,
        },
        equation=equation,
        units_trace={
            "px": case.loads.axial_right_end.unit,
            "py": case.loads.shear_right_end.unit,
            "ex": ex.unit,
            "ey": ey.unit,
            "mz": "kip-in" if case.units_system == UnitSystem.US else "kN-mm",
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
