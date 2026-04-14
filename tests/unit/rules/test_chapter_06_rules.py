from __future__ import annotations

from steel_connections.data.materials_repository import get_bolt_strength_properties
from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.models.errors import StructuredEngineException
from steel_connections.models.output import CheckStatus, GlobalStatus
from steel_connections.models.units import UnitSystem


def test_bueep_rule_set_runs_without_errors(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.PASS
    assert len(result.checks) == 28
    assert all(check.status == CheckStatus.PASS for check in result.checks)


def test_bueep_missing_phi_n_fails_hard(bueep_4e_payload: dict) -> None:
    del bueep_4e_payload["design_factors"]["phi_n"]
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.errors) == 1
    assert result.errors[0].missing_fields == ["design_factors.phi_n"]


def test_bueep_missing_ductility_demand_fails_hard(bueep_4e_payload: dict) -> None:
    del bueep_4e_payload["design_factors"]["member_ductility_demand_beam"]
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.errors) == 1
    assert result.errors[0].missing_fields == ["design_factors.member_ductility_demand_beam"]


def test_bueep_missing_column_ductility_demand_fails_hard(bueep_4e_payload: dict) -> None:
    del bueep_4e_payload["design_factors"]["member_ductility_demand_column"]
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.errors) == 1
    assert result.errors[0].missing_fields == ["design_factors.member_ductility_demand_column"]


def test_bueep_missing_de_fails_hard(bueep_4e_payload: dict) -> None:
    del bueep_4e_payload["geometry"]["de"]
    try:
        run_case_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["geometry.de"]
    else:
        raise AssertionError("Expected StructuredEngineException for missing geometry.de.")


def test_bueep_missing_bolt_thread_condition_fails_hard(bueep_4e_payload: dict) -> None:
    del bueep_4e_payload["materials"]["bolt_thread_condition"]
    try:
        run_case_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["materials.bolt_thread_condition"]
    else:
        raise AssertionError("Expected StructuredEngineException for missing bolt_thread_condition.")


def test_bueep_bolt_fnv_uses_thread_condition_x(bueep_4e_payload: dict) -> None:
    bueep_4e_payload["materials"]["bolt_thread_condition"] = "X"
    case = parse_and_validate_payload(bueep_4e_payload)
    expected = get_bolt_strength_properties(
        description="Grupo 150",
        specification="ASTM A490",
        unit_system=UnitSystem.US,
    )["fnv_threads_excluded"]
    assert case.materials.bolt_fnv is not None
    assert case.materials.bolt_fnv.unit == expected.unit
    assert abs(case.materials.bolt_fnv.value - expected.value) < 1e-9


def test_bseep_step1_uses_ze_from_sections_catalog(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step1 = next(check for check in result.checks if check.rule_id == "AISC358.06.7.1.bseep_8es.step1_mpr")
    assert step1.calculation_memory.inputs["ze_source"] == "sections_catalog_zx"
    ze_value = step1.calculation_memory.inputs["ze"]["value"]
    assert abs(ze_value - (3280.0 / 16.387064)) < 1e-6


def test_bueep_step1a_compactness_is_reported(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    step1a = next(check for check in result.checks if check.rule_id == "AISC358.06.7.1.bueep_4e.step1a_compactness")
    assert step1a.status == CheckStatus.PASS
    assert step1a.calculation_memory.inputs["member_ductility_demand_beam"] == "moderate"
    assert step1a.calculation_memory.inputs["member_ductility_demand_column"] == "moderate"


def test_bueep_prequalification_limits_are_reported(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.PASS
    assert prequal.calculation_memory.intermediates["dcr_by_check"]["bp_ge_bf_plus_margin"] <= 1.0


def test_bueep_prequalification_limits_fail_when_pitch_is_below_3db(bueep_4e_payload: dict) -> None:
    bueep_4e_payload["geometry"]["pb"]["value"] = 2.0
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.FAIL
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    assert prequal.calculation_memory.intermediates["dcr_by_check"]["pitch_pb_ge_3db"] > 1.0


def test_kc_distance_input_is_forbidden(bueep_4e_payload: dict) -> None:
    bueep_4e_payload["geometry"]["kc_distance"] = {"value": 2.0, "unit": "in"}
    try:
        parse_and_validate_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert "kc_distance" in exc.error.message
    else:
        raise AssertionError("Expected validation error because geometry.kc_distance is no longer an allowed input.")
