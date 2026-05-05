from __future__ import annotations

from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.domain.engine.result_mapping import map_detailed_run_result
from steel_connections.models.results import DesignResult
from steel_connections.reporting.json_writer import write_design_result
from steel_connections.reporting.markdown import (
    render_design_result_markdown,
    write_design_result_markdown,
)
from tests.helpers.golden_compare import assert_same_detailed_result_numeric, load_json


APPROVED_CASE = "examples/moment_prequalified/case_003_bseep_8es_split_inputs"
APPROVED_GOLDEN = Path("tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json")


def test_pure_reporting_modules_have_no_impure_imports() -> None:
    pure_reporting_paths = [
        Path("src/steel_connections/reporting/json_writer.py"),
        *Path("src/steel_connections/reporting/markdown").rglob("*.py"),
    ]
    forbidden_imports = (
        "steel_connections.data",
        "steel_connections.catalogs",
        "steel_connections.codes",
        "steel_connections.models.output",
    )

    for path in pure_reporting_paths:
        if "__pycache__" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        for forbidden in forbidden_imports:
            assert forbidden not in source, f"{path} imports or references {forbidden}"


def test_design_result_markdown_consumes_design_result_only(tmp_path: Path) -> None:
    legacy_result = run_case_file(APPROVED_CASE)
    assert_same_detailed_result_numeric(legacy_result.model_dump(mode="json"), load_json(APPROVED_GOLDEN))
    design_result = map_detailed_run_result(legacy_result)

    rendered = render_design_result_markdown(design_result)
    assert "# Memoria de calculo" in rendered
    assert f"- Proyecto: `{design_result.project_id}`" in rendered
    assert f"- Caso: `{design_result.case_id}`" in rendered
    assert design_result.checks[0].rule_id in rendered
    assert "```json" in rendered

    target = write_design_result_markdown(design_result, tmp_path)
    assert target.name == "memory.md"
    assert target.read_text(encoding="utf-8") == rendered


def test_json_writer_serializes_design_result(tmp_path: Path) -> None:
    legacy_result = run_case_file(APPROVED_CASE)
    design_result = map_detailed_run_result(legacy_result)

    target = write_design_result(design_result, tmp_path, example_id="case_003")
    loaded = DesignResult.model_validate_json(target.read_text(encoding="utf-8"))

    assert target == tmp_path / "case_003" / "design_result.json"
    assert loaded.case_id == design_result.case_id
    assert loaded.summary.worst_dcr == design_result.summary.worst_dcr
    assert len(loaded.checks) == len(design_result.checks)
