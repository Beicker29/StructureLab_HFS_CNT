from __future__ import annotations

import math
from typing import Any

from steel_connections.data.materials_repository import get_bolt_strength_properties
from steel_connections.data.sections_repository import get_bolt_section_properties
from steel_connections.domain.rules.aisc360.ezbolt_wrapper import solve_bolt_group_with_ezbolt
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


def _web_group_points_in(case: BeamBeamMomentBoltedCase) -> list[tuple[float, float]]:
    sx_in = _to_in(case.geometry.web_bolt_gage, case.units_system)
    sy_in = _to_in(case.geometry.web_bolt_pitch, case.units_system)
    points: list[tuple[float, float]] = []
    for ix in range(case.geometry.web_bolt_lines):
        for iy in range(case.geometry.web_bolt_rows_per_side):
            points.append((float(ix) * sx_in, float(iy) * sy_in))
    return points


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


def _safe_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def run_step2_pernos1_method(case: BeamBeamMomentBoltedCase, rule_binding: object) -> CheckResult:
    procedure_icr = _selected_procedure_icr(case)
    method = procedure_icr.method
    tolerance = procedure_icr.tolerance_1
    max_iterations = procedure_icr.max_iterations_1

    px_kip = abs(_to_kip(case.loads.axial_right_end, case.units_system))
    py_kip = abs(_to_kip(case.loads.shear_right_end, case.units_system))
    e = _resolve_eccentricity(case)
    e_in = _to_in(e, case.units_system)
    mz_kip_in = py_kip * e_in
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

    solved = solve_bolt_group_with_ezbolt(
        bolt_points_in=bolt_points,
        vx_kip=px_kip,
        vy_kip=py_kip,
        torsion_kip_in=mz_kip_in,
        bolt_capacity_kip=bolt_capacity_active_kip,
        rule_id=rule_binding.rule_id,
        source_document=rule_binding.source_document,
    )
    raw_results = solved["results"]
    superposition = raw_results.get("Elastic Method - Superposition")
    ecr = raw_results.get("Elastic Method - Center of Rotation")
    icr = raw_results.get("Instant Center of Rotation Method")

    demand: Quantity | None = None
    capacity: Quantity | None = None
    dcr: float | None = None
    status = CheckStatus.FAIL
    equation = "bbmb_splice Step 2 pernos 1: ezbolt backend"
    notes: str | None = None

    active_mode_data: dict[str, Any] = {"method": method}
    if method == "elastic_superposition":
        if not isinstance(superposition, dict):
            notes = "Elastic superposition result not available from ezbolt."
        else:
            demand_kip = _safe_float(superposition.get("Bolt Demand"))
            capacity_kip = _safe_float(superposition.get("Bolt Capacity"))
            dcr = _safe_float(superposition.get("DCR"))
            if demand_kip is not None and capacity_kip is not None and dcr is not None:
                demand = _from_kip(demand_kip, case.units_system)
                capacity = _from_kip(capacity_kip, case.units_system)
                status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
            else:
                notes = "Elastic superposition values (demand/capacity/DCR) are incomplete."
            equation = "Elastic Superposition: DCR = BoltDemand / BoltCapacity"
            active_mode_data.update(
                {
                    "demand_kip": demand_kip,
                    "capacity_kip": capacity_kip,
                    "dcr": dcr,
                }
            )
    elif method == "elastic_ecr":
        if not isinstance(ecr, dict):
            notes = "Elastic ECR result not available from ezbolt."
        else:
            demand_kip = _safe_float(ecr.get("Connection Demand"))
            capacity_kip = _safe_float(ecr.get("Connection Capacity"))
            dcr = _safe_float(ecr.get("DCR"))
            if demand_kip is not None and capacity_kip is not None and dcr is not None:
                demand = _from_kip(demand_kip, case.units_system)
                capacity = _from_kip(capacity_kip, case.units_system)
                status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
            else:
                notes = "Elastic ECR values (demand/capacity/DCR) are incomplete."
            equation = "Elastic ECR: DCR = ConnectionDemand / ConnectionCapacity"
            active_mode_data.update(
                {
                    "demand_kip": demand_kip,
                    "capacity_kip": capacity_kip,
                    "dcr": dcr,
                }
            )
    else:
        if not isinstance(icr, dict):
            notes = "ICR result not available from ezbolt."
        else:
            demand_kip = _safe_float(icr.get("Connection Demand"))
            capacity_kip = _safe_float(icr.get("Connection Capacity"))
            dcr = _safe_float(icr.get("DCR"))
            cu = _safe_float(icr.get("Cu"))
            final_residual = _safe_float(solved.get("final_residual"))
            n_iterations = solved.get("n_iterations")
            converged = cu is not None and demand_kip is not None and capacity_kip is not None and dcr is not None
            if converged and final_residual is not None:
                converged = final_residual <= tolerance
            if converged and isinstance(n_iterations, int):
                converged = n_iterations <= max_iterations
            if converged and demand_kip is not None and capacity_kip is not None and dcr is not None:
                demand = _from_kip(demand_kip, case.units_system)
                capacity = _from_kip(capacity_kip, case.units_system)
                status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
            else:
                status = CheckStatus.FAIL
                notes = (
                    "ICR did not satisfy configured convergence acceptance "
                    f"(tol={tolerance}, max_iterations={max_iterations})."
                )
            equation = "ICR (ezbolt): DCR = ConnectionDemand / ConnectionCapacity"
            active_mode_data.update(
                {
                    "demand_kip": demand_kip,
                    "capacity_kip": capacity_kip,
                    "dcr": dcr,
                    "cu": cu,
                    "converged": converged,
                    "final_residual": final_residual,
                    "n_iterations": n_iterations,
                }
            )

    icr_capacity_compare_kip: float | None = None
    if method in {"elastic_superposition", "elastic_ecr"} and isinstance(icr, dict):
        icr_capacity_compare_kip = _safe_float(icr.get("Connection Capacity"))

    memory = CalculationMemory(
        inputs={
            "method_selected": method,
            "px": case.loads.axial_right_end.model_dump(),
            "py": case.loads.shear_right_end.model_dump(),
            "e": e.model_dump(),
            "mz": _from_kip_in(mz_kip_in, case.units_system).model_dump(),
            "bolt_group_1_nx": case.geometry.web_bolt_lines,
            "bolt_group_1_ny": case.geometry.web_bolt_rows_per_side,
            "bolt_group_1_points_in": [{"x": x, "y": y} for x, y in bolt_points],
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
            "active_mode_data": active_mode_data,
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
                "e": e.model_dump(),
                "mz": _from_kip_in(mz_kip_in, case.units_system).model_dump(),
                "demand": demand.model_dump() if demand is not None else None,
                "capacity": capacity.model_dump() if capacity is not None else None,
                "dcr": dcr,
                "status": status.value,
                "icr_compare_capacity": (
                    _from_kip(icr_capacity_compare_kip, case.units_system).model_dump()
                    if icr_capacity_compare_kip is not None
                    else None
                ),
                "final_residual": _safe_float(solved.get("final_residual")),
                "n_iterations": solved.get("n_iterations"),
            },
        },
        design_factors={
            "phi_bolt_shear": case.design_factors.phi_bolt_shear,
        },
        equation=equation,
        units_trace={
            "px": case.loads.axial_right_end.unit,
            "py": case.loads.shear_right_end.unit,
            "e": e.unit,
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
