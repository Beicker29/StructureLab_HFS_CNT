from __future__ import annotations

from pathlib import Path

from steel_connections.adapters.legacy_input import load_legacy_design_input
from steel_connections.domain.engine.pipeline import run_case_file, run_case_file_design_result
from steel_connections.domain.engine.result_mapping import map_detailed_run_result
from steel_connections.domain.registry import default_registry
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
    (
        "examples/Fully Restrained Moment/case_001_bbmb_splice_test_f_floor.json",
        Path("tests/golden/approved/case_001_bbmb_splice_test_f_floor/detailed.json"),
    ),
]


def test_run_case_file_design_result_matches_mapped_legacy_result() -> None:
    for input_path, golden_path in APPROVED_CASES:
        legacy_result = run_case_file(input_path)
        assert_same_detailed_result_numeric(legacy_result.model_dump(mode="json"), load_json(golden_path))

        mapped = map_detailed_run_result(legacy_result)
        direct = run_case_file_design_result(input_path)

        assert direct.project_id == mapped.project_id
        assert direct.case_id == mapped.case_id
        assert direct.connection_family == mapped.connection_family
        assert direct.connection_type == mapped.connection_type
        assert direct.load_state == mapped.load_state
        assert direct.status == mapped.status
        assert direct.summary == mapped.summary
        assert len(direct.checks) == len(mapped.checks)
        for direct_check, mapped_check in zip(direct.checks, mapped.checks):
            assert direct_check.model_dump(mode="json") == mapped_check.model_dump(mode="json")


def test_registry_accepts_design_input_without_changing_rule_order() -> None:
    for input_path, _ in APPROVED_CASES:
        design_input = load_legacy_design_input(input_path)
        legacy_case = design_input.to_legacy_case()

        legacy_rules = default_registry().applicable_rules(legacy_case)
        design_input_rules = default_registry().applicable_rules(design_input)

        assert [rule.rule_id for rule in design_input_rules] == [rule.rule_id for rule in legacy_rules]


def test_registry_evaluates_design_input_with_same_checks_as_legacy() -> None:
    for input_path, _ in APPROVED_CASES:
        design_input = load_legacy_design_input(input_path)
        legacy_case = design_input.to_legacy_case()

        legacy_checks, legacy_errors = default_registry().evaluate(legacy_case)
        design_input_checks, design_input_errors = default_registry().evaluate(design_input)

        assert [error.model_dump(mode="json") for error in design_input_errors] == [
            error.model_dump(mode="json") for error in legacy_errors
        ]
        assert [check.model_dump(mode="json") for check in design_input_checks] == [
            check.model_dump(mode="json") for check in legacy_checks
        ]
