from __future__ import annotations

from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.domain.engine.result_mapping import map_detailed_run_result
from steel_connections.reporting.markdown import build_report_projection, render_design_result_markdown
from tests.helpers.golden_compare import assert_same_detailed_result_numeric, load_json


APPROVED_CASE = "examples/moment_prequalified/case_003_bseep_8es_split_inputs"
APPROVED_GOLDEN = Path("tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json")


def test_report_projection_uses_design_result_without_changing_numbers() -> None:
    legacy_result = run_case_file(APPROVED_CASE)
    assert_same_detailed_result_numeric(legacy_result.model_dump(mode="json"), load_json(APPROVED_GOLDEN))
    design_result = map_detailed_run_result(legacy_result)

    projection = build_report_projection(design_result)

    assert len(projection.checks) == len(design_result.checks)
    assert projection.checks[0].index == 1
    assert projection.checks[0].check.rule_id == design_result.checks[0].rule_id
    assert projection.check_by_rule_id(design_result.checks[0].rule_id) == design_result.checks[0]
    assert projection.critical_checks
    assert projection.critical_checks[0].dcr == design_result.summary.worst_dcr


def test_design_result_markdown_includes_critical_checks_from_projection() -> None:
    legacy_result = run_case_file(APPROVED_CASE)
    design_result = map_detailed_run_result(legacy_result)

    rendered = render_design_result_markdown(design_result)

    assert "## Checks criticos" in rendered
    assert "- Peor DCR:" in rendered
    projection_rule_id = build_report_projection(design_result).critical_checks[0].rule_id
    assert projection_rule_id in rendered
