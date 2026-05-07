from __future__ import annotations

from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.reporting.markdown_writer import (
    render_memory_markdown,
    render_splice_methods_table_markdown,
)
from tests.helpers.golden_compare import assert_same_detailed_result_numeric, compare_report_text, load_json


EXAMPLE_SPLICE_PATH = "examples/Fully Restrained Moment/case_001_bbmb_splice.json"
APPROVED_GOLDEN = Path("tests/golden/approved/case_001_bbmb_splice/detailed.json")
APPROVED_MEMORY = Path("tests/golden/approved/case_001_bbmb_splice/memory.md")
EXAMPLE_SPLICE_F_FLOOR_PATH = "examples/Fully Restrained Moment/case_001_bbmb_splice_test_f_floor.json"
APPROVED_GOLDEN_F_FLOOR = Path("tests/golden/approved/case_001_bbmb_splice_test_f_floor/detailed.json")
APPROVED_MEMORY_F_FLOOR = Path("tests/golden/approved/case_001_bbmb_splice_test_f_floor/memory.md")


def test_splice_memory_renders_from_design_result_wrapper_without_recalculation() -> None:
    result = run_case_file(EXAMPLE_SPLICE_PATH)
    assert_same_detailed_result_numeric(result.model_dump(mode="json"), load_json(APPROVED_GOLDEN))

    memory = render_memory_markdown(result)

    compare_report_text(memory, APPROVED_MEMORY.read_text(encoding="utf-8-sig"))
    assert "# Memoria de Cálculo" in memory
    assert "## Paso 1 - Propiedades geométricas, mecánicas y fabricacion" in memory


def test_splice_methods_table_wrapper_renders_design_result_detail() -> None:
    result = run_case_file(EXAMPLE_SPLICE_PATH)

    rendered = render_splice_methods_table_markdown(result)

    assert "# Reporte Metodos Pernos 1 (Splice)" in rendered
    assert "Metodo seleccionado en JSON: `icr`" in rendered
    assert "## 7. Instant Center of Rotation (ICR)" in rendered
    assert "```json" not in rendered


def test_splice_memory_renders_f_floor_branch_for_staggered_check() -> None:
    result = run_case_file(EXAMPLE_SPLICE_F_FLOOR_PATH)
    assert_same_detailed_result_numeric(result.model_dump(mode="json"), load_json(APPROVED_GOLDEN_F_FLOOR))

    memory = render_memory_markdown(result)

    compare_report_text(memory, APPROVED_MEMORY_F_FLOOR.read_text(encoding="utf-8-sig"))
    assert "#### Chequeo 2.1.23" in memory
    assert "Pmin_blt = min{|x_j_blt_web - x_k_blt_flange|}" in memory
