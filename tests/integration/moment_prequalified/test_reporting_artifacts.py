from __future__ import annotations

import shutil
from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.reporting.json_writer import write_detailed_result
from steel_connections.reporting.markdown_writer import write_memory_markdown
from tests.helpers.golden_compare import assert_same_detailed_result_numeric, compare_report_files, load_json


def test_example_results_folder_and_memory_artifact() -> None:
    input_path = "examples/moment_prequalified/case_003_bseep_8es_split_inputs"
    out_root = Path(".tmp_test_outputs")

    result = run_case_file(input_path)
    assert_same_detailed_result_numeric(
        result.model_dump(mode="json"),
        load_json("tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json"),
    )
    detailed_path = write_detailed_result(result, out_root, example_id=Path(input_path).stem)
    memory_path = write_memory_markdown(result, detailed_path.parent)

    assert detailed_path.exists()
    assert detailed_path == out_root / "case_003_bseep_8es_split_inputs" / "detailed.json"
    assert memory_path.exists()
    assert memory_path.name == "memory.md"
    compare_report_files(
        memory_path,
        "tests/golden/approved/case_003_bseep_8es_split_inputs/memory.md",
    )

    checks_by_rule = {check.rule_id: check for check in result.checks}
    assert "AISC358.06.7.bseep_8es.step5_probable_moment_face_column" in checks_by_rule
    memory = memory_path.read_text(encoding="utf-8")
    assert "## Paso 1 - Propiedades geométricas, mecánicas y fabricacion" in memory
    assert "## Paso 10 - Revisión de resistencia platina extremo (vg_izq)" in memory

    if out_root.exists():
        shutil.rmtree(out_root, ignore_errors=True)
