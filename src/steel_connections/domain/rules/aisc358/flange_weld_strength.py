from __future__ import annotations

from steel_connections.codes.aisc358.chapter_07 import compute_phi_flange_weld_capacity
from steel_connections.models.errors import missing_required_input_error
from steel_connections.models.input import AISC358MomentCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import to_design_force_unit


def run(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    if case.materials.weld_fexx is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["materials.weld_fexx"],
            message="Required input 'materials.weld_fexx' is missing for applicable rule.",
        )
    if case.geometry.weld_effective_area is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["geometry.weld_effective_area"],
            message="Required input 'geometry.weld_effective_area' is missing for applicable rule.",
        )
    if case.loads.beam_flange_tension is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["loads.beam_flange_tension"],
            message="Required input 'loads.beam_flange_tension' is missing for applicable rule.",
        )

    demand = to_design_force_unit(case.loads.beam_flange_tension, case.units_system)
    capacity, intermediates = compute_phi_flange_weld_capacity(
        fexx=case.materials.weld_fexx,
        weld_effective_area=case.geometry.weld_effective_area,
        phi=case.design_factors.phi_flange_weld,
        unit_system=case.units_system,
    )

    dcr = demand.value / capacity.value
    status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
    memory = CalculationMemory(
        inputs={
            "weld_fexx": case.materials.weld_fexx.model_dump(),
            "weld_effective_area": case.geometry.weld_effective_area.model_dump(),
            "beam_flange_tension": demand.model_dump(),
        },
        intermediates=intermediates,
        design_factors={"phi_flange_weld": case.design_factors.phi_flange_weld},
        equation="phi * 0.6 * FEXX * A_weld_effective",
        units_trace={
            "FEXX": case.materials.weld_fexx.unit,
            "A_weld_effective": case.geometry.weld_effective_area.unit,
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
