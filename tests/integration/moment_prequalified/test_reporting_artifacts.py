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
    assert "## Paso 1 - Limites de precalificacion" in memory
    assert "## Paso 2 - Momento probable maximo en rotula plastica (Mpr)" in memory
    assert "## Paso 3 - Distancia de rotula plastica desde la cara de la columna (Sh)" in memory
    assert "## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)" in memory
    assert "## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)" in memory
    assert "## Paso 6 - Revision De Resistencia Pernos (vg_izq)" in memory
    assert "## Paso 7 - Revision De Resistencia Pernos (vg_der)" in memory
    assert "## Paso 8 - Revision de resistencia platina extremo (vg_izq)" in memory
    assert "## Paso 9 - Revision de resistencia platina extremo (vg_der)" in memory
    assert "## Paso 10 - Revision de Resistencia soldadura #1" in memory
    assert "## Paso 16 - Revision de resistencia de la viga (vg_izq)" in memory
    assert "## Paso 17 - Revision de resistencia de la viga (vg_der)" in memory
    assert "## Paso 20 - Revision de resistencia de la aleta de la columna" in memory
    assert "## Paso 21 - Revision de resistencia del alma de la columna" in memory
    assert "- Mf_vgizq_critico: `1534.87 kN-m`" in memory
    assert "- Mf_vgder_critico: `1230.24 kN-m`" in memory

    checks_by_rule = {check.rule_id: check for check in result.checks}
    step5 = checks_by_rule["AISC358.06.7.bseep_8es.step5_probable_moment_face_column"]
    step12_izq = checks_by_rule["AISC358.06.7.bseep_8es.step12_1_1_column_flange_local_bending_vgizq"]
    step12_der = checks_by_rule["AISC358.06.7.bseep_8es.step12_1_1_column_flange_local_bending_vgder"]
    step13_izq = checks_by_rule["AISC358.06.7.bseep_8es.step13_1_1_column_web_local_yielding_vgizq"]
    step13_der = checks_by_rule["AISC358.06.7.bseep_8es.step13_1_1_column_web_local_yielding_vgder"]
    step14_2_1_izq = checks_by_rule["AISC358.06.7.bseep_8es.step14_2_1_column_web_local_crippling_vgizq"]
    step14_2_1_der = checks_by_rule["AISC358.06.7.bseep_8es.step14_2_1_column_web_local_crippling_vgder"]
    step14_2_2_der = checks_by_rule["AISC358.06.7.bseep_8es.step14_2_2_column_web_local_buckling_vgder"]

    mf_izqmax = float(step5.calculation_memory.intermediates["mf_izqmax"])
    mf_dermax = float(step5.calculation_memory.intermediates["mf_dermax"])
    assert abs(float(step12_izq.calculation_memory.inputs["mf"]["value"]) - mf_izqmax) < 1e-6
    assert abs(float(step12_der.calculation_memory.inputs["mf"]["value"]) - mf_dermax) < 1e-6
    assert abs(float(step13_izq.calculation_memory.inputs["mf_vgizq_critico"]["value"]) - mf_izqmax) < 1e-6
    assert abs(float(step13_der.calculation_memory.inputs["mf_vgder_critico"]["value"]) - mf_dermax) < 1e-6
    assert abs(float(step14_2_1_izq.calculation_memory.inputs["mf_vgizq_critico"]["value"]) - mf_izqmax) < 1e-6
    assert abs(float(step14_2_1_der.calculation_memory.inputs["mf_vgder_critico"]["value"]) - mf_dermax) < 1e-6

    wcb_der_inputs = step14_2_2_der.calculation_memory.inputs
    assert "d_vgder" in wcb_der_inputs and "d_vgizq" in wcb_der_inputs
    assert "tf_vgder" in wcb_der_inputs and "tf_vgizq" in wcb_der_inputs
    assert abs(float(wcb_der_inputs["d_vgder"]["value"]) - 536.0) < 1e-6
    assert abs(float(wcb_der_inputs["d_vgizq"]["value"]) - 607.0) < 1e-6
    assert abs(float(wcb_der_inputs["tf_vgder"]["value"]) - 17.4) < 1e-6
    assert abs(float(wcb_der_inputs["tf_vgizq"]["value"]) - 17.3) < 1e-6
    equation_wcb_der = step14_2_2_der.calculation_memory.equation
    assert "Mu3_vgder" in equation_wcb_der
    assert "Mu3_vgizq" in equation_wcb_der

    if out_root.exists():
        shutil.rmtree(out_root, ignore_errors=True)
