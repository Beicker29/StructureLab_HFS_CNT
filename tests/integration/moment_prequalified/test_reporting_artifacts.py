from __future__ import annotations

import shutil
from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.reporting.json_writer import write_detailed_result
from steel_connections.reporting.markdown_writer import write_memory_markdown


def test_example_results_folder_and_memory_artifact() -> None:
    input_path = "examples/moment_prequalified/case_003_bseep_8es_split_inputs"
    out_root = Path(".tmp_test_outputs")

    result = run_case_file(input_path)
    detailed_path = write_detailed_result(result, out_root, example_id=Path(input_path).stem)
    memory_path = write_memory_markdown(result, detailed_path.parent)

    assert detailed_path.exists()
    assert detailed_path == out_root / "case_003_bseep_8es_split_inputs" / "detailed.json"
    assert memory_path.exists()
    assert memory_path.name == "memory.md"
    memory = memory_path.read_text(encoding="utf-8")
    assert "## Paso 1 - PREQUALIFICATION LIMITS" in memory
    assert "## Paso 2 - Probable Maximum Moment At Plastic Hinge (Mpr)" in memory
    assert "## Paso 3 - Distancia De Rotula Plastica Desde La Cara De Columna (Sh)" in memory
    assert "## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)" in memory
    assert "## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)" in memory
    assert "## Paso 6 - Revision De Resistencia Pernos" in memory
    assert "### 6.1 Revision de capacidad a traccion" in memory
    assert "### 6.2 Revision de capacidad a cortante" in memory
    assert "## Paso 7 - Revision de resistencia end plate" in memory
    assert "#### 7.1.1. ELR #1: Fluencia (AISC 358-22 .7-8)" in memory
    assert "#### 7.2.1. Eje #1: Fluencia por cortante (AISC 358-22 G7-10)" in memory
    assert "#### 7.2.2. Eje #2: Rotura por cortante (AISC 358-22 G7-12)" in memory
    assert "### 7.3. Revision de capacidad a cortante paralelo al plano de la platina" in memory
    assert "#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno (AISC 360-22 J3.11a)" in memory
    assert "#### 7.3.2. ELR #2: Aplastamiento en la perforacion del perno (AISC 360-22 J3.11a)" in memory
    assert "phiVn2p" in memory
    assert "lc:" in memory
    assert "## Paso 8 - Revision de Resistencia soldadura #1" in memory
    assert "#### 8.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)" in memory
    assert "## Paso 9 - Revision de resistencia soldadura #2" in memory
    assert "#### 9.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)" in memory
    assert "## Paso 10 - Revision de resistencia de la viga" in memory
    assert "#### 10.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1)" in memory
    assert "DCRbm,v" in memory
    assert "Cv1" in memory
    assert "dh (diametro agujero estandar)" in memory
    assert "`bp`" in memory

    if out_root.exists():
        shutil.rmtree(out_root, ignore_errors=True)
