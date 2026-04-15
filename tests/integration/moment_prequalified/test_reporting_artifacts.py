from __future__ import annotations

import shutil
from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.domain.engine.validate import parse_and_validate_file
from steel_connections.reporting.geometry_artifact import write_connection_geometry_artifact
from steel_connections.reporting.json_writer import write_detailed_result
from steel_connections.reporting.markdown_writer import write_memory_markdown


def test_example_results_folder_and_geometry_artifact() -> None:
    input_path = "examples/moment_prequalified/case_003_bseep_8es.json"
    out_root = Path(".tmp_test_outputs")

    result = run_case_file(input_path)
    detailed_path = write_detailed_result(result, out_root, example_id=Path(input_path).stem)
    memory_path = write_memory_markdown(result, detailed_path.parent)
    case = parse_and_validate_file(input_path)
    geometry_path = write_connection_geometry_artifact(case, detailed_path.parent)

    assert detailed_path.exists()
    assert detailed_path == out_root / "case_003_bseep_8es" / "detailed.json"
    assert memory_path.exists()
    assert memory_path.name == "memory.md"
    assert geometry_path is not None
    assert geometry_path.exists()
    assert geometry_path.name == "geometry.svg"
    assert (detailed_path.parent / "geometry_bseep_8es_section.svg").exists()
    assert (detailed_path.parent / "geometry_bseep_8es_elevation.svg").exists()
    svg = geometry_path.read_text(encoding="utf-8")
    for token in (
        "bp =",
        "g =",
        "de =",
        "pb =",
        "pso (geometry.pfo) =",
        "pfi =",
        "tcp =",
        "psi = pfi + tfb - tcp =",
        "lc_ep =",
        "lc_cf =",
        "a_col_end =",
        "h1 =",
        "h2 =",
        "h3 =",
        "h4 =",
    ):
        assert token in svg
    memory = memory_path.read_text(encoding="utf-8")
    assert "## Paso 1 - PREQUALIFICATION LIMITS" in memory
    assert "`bp`" in memory

    if out_root.exists():
        shutil.rmtree(out_root, ignore_errors=True)
