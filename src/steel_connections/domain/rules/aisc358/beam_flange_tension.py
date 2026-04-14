from __future__ import annotations

from steel_connections.codes.aisc358.chapter_07 import compute_phi_flange_tension_capacity
from steel_connections.models.errors import missing_required_input_error
from steel_connections.models.input import AISC358MomentCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import to_design_force_unit


def run(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    if case.materials.beam_fy is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["materials.beam_fy"],
            message="Required input 'materials.beam_fy' is missing for applicable rule.",
        )
    if case.geometry.beam_flange_area is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["geometry.beam_flange_area"],
            message="Required input 'geometry.beam_flange_area' is missing for applicable rule.",
        )
    if case.loads.beam_flange_tension is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["loads.beam_flange_tension"],
            message="Required input 'loads.beam_flange_tension' is missing for applicable rule.",
        )

    demand = to_design_force_unit(case.loads.beam_flange_tension, case.units_system)
    capacity, intermediates = compute_phi_flange_tension_capacity(
        fy=case.materials.beam_fy,
        flange_area=case.geometry.beam_flange_area,
        phi=case.design_factors.phi_flange_tension,
        unit_system=case.units_system,
    )

    dcr = demand.value / capacity.value
    status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
    memory = CalculationMemory(
        inputs={
            "beam_fy": case.materials.beam_fy.model_dump(),
            "beam_flange_area": case.geometry.beam_flange_area.model_dump(),
            "beam_flange_tension": demand.model_dump(),
        },
        intermediates=intermediates,
        design_factors={"phi_flange_tension": case.design_factors.phi_flange_tension},
        equation="phi * Fy * A_flange",
        units_trace={
            "Fy": case.materials.beam_fy.unit,
            "A_flange": case.geometry.beam_flange_area.unit,
            "demand": demand.unit,
            "capacity": capacity.unit,
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
        notes=None,
    )
