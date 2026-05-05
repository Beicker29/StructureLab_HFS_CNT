from __future__ import annotations

from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.domain.engine.result_mapping import map_detailed_run_result
from steel_connections.models.output import CheckStatus as LegacyCheckStatus
from steel_connections.models.results import CheckStatus, DesignStatus
from tests.helpers.golden_compare import assert_same_detailed_result_numeric, load_json


APPROVED_CASES = [
    (
        "examples/moment_prequalified/case_003_bseep_8es_split_inputs",
        Path("tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json"),
    ),
    (
        "examples/Fully Restrained Moment/case_001_bbmb_splice.json",
        Path("tests/golden/approved/case_001_bbmb_splice/detailed.json"),
    ),
]


def test_result_mapping_preserves_approved_golden_numbers() -> None:
    for input_path, golden_path in APPROVED_CASES:
        legacy_result = run_case_file(input_path)
        assert_same_detailed_result_numeric(legacy_result.model_dump(mode="json"), load_json(golden_path))

        design_result = map_detailed_run_result(legacy_result)

        assert design_result.project_id == legacy_result.project_id
        assert design_result.case_id == legacy_result.case_id
        assert len(design_result.checks) == len(legacy_result.checks)
        assert design_result.summary.worst_dcr == legacy_result.summary.worst_dcr
        for legacy_check, mapped_check in zip(legacy_result.checks, design_result.checks):
            assert mapped_check.rule_id == legacy_check.rule_id
            assert mapped_check.demand == legacy_check.demand
            assert mapped_check.capacity == legacy_check.capacity
            assert mapped_check.dcr == legacy_check.dcr
            assert mapped_check.equation == legacy_check.calculation_memory.equation
            assert mapped_check.inputs == legacy_check.calculation_memory.inputs
            assert mapped_check.intermediates == legacy_check.calculation_memory.intermediates
            assert mapped_check.design_factors == legacy_check.calculation_memory.design_factors
            assert mapped_check.units == legacy_check.calculation_memory.units_trace


def test_result_mapping_maps_legacy_statuses_without_warning_status() -> None:
    result = run_case_file("examples/Fully Restrained Moment/case_001_bbmb_splice.json")
    mapped = map_detailed_run_result(result)

    assert mapped.status == DesignStatus.NG
    assert mapped.checks[0].status == CheckStatus.NG
    assert mapped.checks[1].status == CheckStatus.OK
    assert result.checks[0].status == LegacyCheckStatus.FAIL


def test_result_mapping_preserves_legacy_not_implemented_as_check_errors() -> None:
    result = run_case_file("examples/moment_prequalified/case_002_bueep_4e_split_inputs")
    mapped = map_detailed_run_result(result)

    assert mapped.status == DesignStatus.ERROR
    assert mapped.errors == []
    error_checks = [check for check in mapped.checks if check.status == CheckStatus.ERROR]
    assert len(error_checks) == result.summary.not_implemented_count
    assert all(check.errors for check in error_checks)
    assert {check.errors[0].error_code for check in error_checks} == {"NOT_IMPLEMENTED"}
