from __future__ import annotations

from pathlib import Path

from steel_connections.codes.engineering.flexure import (
    compute_column_flange_local_bending_strength,
    compute_dcr,
)
from steel_connections.codes.engineering.weld import (
    WeldFillet,
    compute_effective_web_weld_length,
    compute_plate_tension_demand_from_yielding,
)
from steel_connections.models.output import DetailedRunResult
from steel_connections.models.units import Quantity, UnitSystem


def _format_decimal(value: float) -> str:
    text = f"{value:.2f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _format_quantity(value: object) -> str:
    if not isinstance(value, dict):
        return "n/a"
    raw = value.get("value")
    unit = value.get("unit")
    if raw is None or unit is None:
        return "n/a"
    try:
        numeric = float(raw)
        rendered_unit = str(unit)
        if rendered_unit == "kN-mm":
            numeric = numeric / 1000.0
            rendered_unit = "kN-m"
        elif rendered_unit == "ratio":
            rendered_unit = "adim"
        return f"{_format_decimal(numeric)} {rendered_unit}"
    except (TypeError, ValueError):
        return "n/a"


def _format_text(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _format_decimal(float(value))
    text = str(value).strip()
    return text if text else "n/a"


def _format_scalar_with_unit(value: object, unit: str) -> str:
    if value is None:
        return "n/a"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return _format_text(value)
    rendered_unit = unit
    if rendered_unit == "kN-mm":
        numeric = numeric / 1000.0
        rendered_unit = "kN-m"
    return f"{_format_decimal(numeric)} {rendered_unit}"


def _as_quantity(value: object) -> Quantity | None:
    if not isinstance(value, dict):
        return None
    raw = value.get("value")
    unit = value.get("unit")
    if raw is None or unit is None:
        return None
    try:
        return Quantity(value=float(raw), unit=str(unit))
    except (TypeError, ValueError):
        return None


def _infer_unit_system_from_quantity(value: object) -> UnitSystem | None:
    quantity = _as_quantity(value)
    if quantity is None:
        return None
    normalized = quantity.unit.strip().lower()
    if normalized in {"mm", "mpa", "kn", "kn-mm", "kn-m"}:
        return UnitSystem.SI
    if normalized in {"in", "ksi", "kip", "kip-in", "kip-ft"}:
        return UnitSystem.US
    return None


def _convert_moment_to_unit(moment: Quantity, target_unit: str) -> Quantity | None:
    source = moment.unit.strip().lower()
    target = target_unit.strip().lower()
    if source == target:
        return moment
    if source == "kn-m" and target == "kn-mm":
        return Quantity(value=moment.value * 1000.0, unit="kN-mm")
    if source == "kn-mm" and target == "kn-m":
        return Quantity(value=moment.value / 1000.0, unit="kN-m")
    if source == "kip-ft" and target == "kip-in":
        return Quantity(value=moment.value * 12.0, unit="kip-in")
    if source == "kip-in" and target == "kip-ft":
        return Quantity(value=moment.value / 12.0, unit="kip-ft")
    return None


def _quantity_to_mm(value: object) -> float | None:
    if not isinstance(value, dict):
        return None
    raw = value.get("value")
    unit = str(value.get("unit", "")).strip().lower()
    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        return None
    if unit == "mm":
        return numeric
    if unit == "in":
        return numeric * 25.4
    return None


def _stress_to_mpa(value: object) -> float | None:
    if not isinstance(value, dict):
        return None
    raw = value.get("value")
    unit = str(value.get("unit", "")).strip().lower()
    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        return None
    if unit == "mpa":
        return numeric
    if unit == "ksi":
        return numeric * 6.894757293168361
    return None


def _stress_to_ksi(value: object) -> float | None:
    if not isinstance(value, dict):
        return None
    raw = value.get("value")
    unit = str(value.get("unit", "")).strip().lower()
    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        return None
    if unit == "ksi":
        return numeric
    if unit == "mpa":
        return numeric / 6.894757293168361
    return None


def _normalize_weld_type_step11(raw: object) -> str:
    text = _format_text(raw).strip().lower()
    if text in {"cjp", "complete_joint_penetration"}:
        return "cjp"
    if text in {"fillet", "double_sided_fillet", "single_sided_fillet"}:
        return "fillet"
    return text


def _render_result_label(raw_result: object) -> str:
    value = _format_text(raw_result).strip().upper()
    if value in {"OK", "PASS"}:
        return "🟢 Cumple"
    if value in {"NO_OK", "FAIL", "ERROR", "NOT_IMPLEMENTED"}:
        return "🔴 No cumple"
    return _format_text(raw_result)


def _render_result_plain_es(raw_result: object) -> str:
    value = _format_text(raw_result).strip().upper()
    if value in {"OK", "PASS"}:
        return "Cumple"
    if value in {"NO_OK", "FAIL", "ERROR", "NOT_IMPLEMENTED"}:
        return "No cumple"
    return _format_text(raw_result)


def _translate_text_es(raw_text: object) -> str:
    text = _format_text(raw_text)
    replacements = {
        "Protected zone length measured from column face": "Longitud de zona protegida medida desde la cara de la columna",
        "End-plate connection location on column": "Ubicacion de la conexion de placa de extremo en columna",
        "Derived end-plate height reference": "Altura derivada de placa de extremo",
        "Derived end-plate stiffener geometry and detailing edge requirement": "Geometria derivada del rigidizador de placa de extremo y requisito de borde",
        "Installation requirements for bolted assemblies": "Requisitos de instalacion para conjuntos empernados",
        "Quality control and quality assurance for bolted assemblies": "Control y aseguramiento de calidad para conjuntos empernados",
        "Beam profile family allowed for prequalification": "Familia de perfil de viga permitida para precalificacion",
        "End-plate width vs beam flange width": "Ancho de placa de extremo vs ancho de ala de viga",
        "Bolt gage minimum spacing": "Separacion minima de gage de pernos",
        "Length without shear connectors from column face": "Longitud sin conectores de cortante desde la cara de columna",
        "Beam clearance criterion using Sc and S threshold": "Criterio de despeje de viga con umbral Sc y S",
        "Clear span-to-depth ratio by frame system": "Relacion luz libre/peralte por sistema de marco",
        "Beam flange width-to-thickness compactness": "Compacidad ancho-espesor del ala de viga",
        "Beam web width-to-thickness compactness": "Compacidad ancho-espesor del alma de viga",
        "Column profile family allowed for prequalification": "Familia de perfil de columna permitida para precalificacion",
        "Column profile depth maximum (W36/W920)": "Peralte maximo del perfil de columna (W36/W920)",
        "End-plate fit within column flange width": "Ajuste de placa de extremo dentro del ala de la columna",
        "Column-slab connection condition": "Condicion de conexion columna-losa",
        "End-plate width explicit dual inequalities": "Desigualdades explicitas de ancho de placa de extremo",
        "End-plate stiffener height derived from end-plate geometry": "Altura del rigidizador derivada de la geometria de la placa de extremo",
        "Stiffener thickness minimum requirement": "Espesor minimo requerido del rigidizador",
        "Stiffener local buckling width-thickness limit": "Limite de pandeo local ancho-espesor del rigidizador",
        "Bolt gage clearance with stiffener thickness": "Despeje del gage de pernos con espesor del rigidizador",
        "End-plate to beam-web weld type shall be an allowed category": "El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido",
        "Continuity-plate weld type shall be explicitly declared with an allowed weld category": "El tipo de soldadura de platina de continuidad debe declararse y ser permitido",
        "Continuity-plate weld type when plate thickness is less than or equal to 3/8 in (10 mm)": "Tipo de soldadura de platina de continuidad cuando el espesor es menor o igual a 10 mm",
        "Bolt tightening type must be one recognized category": "El tipo de apriete del perno debe ser una categoria reconocida",
        "Bolts shall be pretensioned unless a specific connection permits otherwise": "Los pernos deben estar pretensionados salvo que una conexion especifica permita lo contrario",
        "Bolt fabrication standard must be an allowed high-strength ASTM designation": "La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida",
        "Vertical pitch minimum spacing": "Separacion minima vertical entre pernos",
        "Edge distance at de": "Distancia de borde en de",
        "Outside bolt-row distance limits": "Limites de distancia en fila exterior de pernos",
        "Inside bolt-row distance limits": "Limites de distancia en fila interior de pernos",
        "Beam flange thickness limits": "Limites de espesor del ala de viga",
        "Beam flange width limits": "Limites de ancho del ala de viga",
        "Connecting beam depth limits": "Limites de peralte de la viga conectada",
        "End-plate thickness limits": "Limites de espesor de placa de extremo",
        "Horizontal bolt spacing limits": "Limites de separacion horizontal de pernos",
        "end-plate": "placa de extremo",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    text = (
        text.replace("uniÃ³n", "union")
        .replace("raÃ­z", "raiz")
        .replace("crÃ­tica", "critica")
        .replace("Ã¡", "a")
        .replace("Ã©", "e")
        .replace("Ã­", "i")
        .replace("Ã³", "o")
        .replace("Ãº", "u")
        .replace("Ã±", "n")
        .replace("ratio", "adim")
    )
    return text


def _render_clause_text(clause: object, source_document: object = None, rule_id: object = None) -> str:
    clause_text = _format_text(clause)
    clause_text = (
        clause_text.replace("Chapter", "Capitulo")
        .replace("Section", "Seccion")
        .replace("Step", "Paso")
        .replace("Table", "Tabla")
        .replace("continuity plate weld detail", "detalle de soldadura de platina de continuidad")
        .replace("beam clearance criterion", "criterio de despeje de viga")
        .replace("column top clearance criterion", "criterio de despeje superior de columna")
    )
    source_text = _format_text(source_document)
    if source_text != "n/a" and clause_text != "n/a":
        return f"Documento: {source_text} | Seccion: {clause_text}"
    if source_text != "n/a":
        return f"Documento: {source_text}"
    if clause_text != "n/a":
        return f"Seccion: {clause_text}"
    return "n/a"


def _collect_step_1_rows(result: DetailedRunResult) -> list[dict]:
    rows: list[dict] = []
    for check in result.checks:
        if ".06.3." not in check.rule_id:
            continue
        details = check.calculation_memory.intermediates.get("step_1_limits")
        if not isinstance(details, list):
            details = check.calculation_memory.intermediates.get("prequalification_limits")
        if not isinstance(details, list):
            continue
        for item in details:
            if isinstance(item, dict):
                enriched = dict(item)
                enriched.setdefault("source_document", check.source_document)
                enriched.setdefault("rule_id", check.rule_id)
                rows.append(enriched)
    return rows


def _collect_step_1_notes(result: DetailedRunResult) -> list[dict]:
    notes: list[dict] = []
    for check in result.checks:
        if ".06.3." not in check.rule_id:
            continue
        details = check.calculation_memory.intermediates.get("step_1_notes")
        if not isinstance(details, list):
            continue
        for item in details:
            if isinstance(item, dict):
                enriched = dict(item)
                enriched.setdefault("source_document", check.source_document)
                enriched.setdefault("rule_id", check.rule_id)
                notes.append(enriched)
    return notes

def _collect_splice_step_1_rows(result: DetailedRunResult) -> list[dict]:
    rows: list[dict] = []
    for check in result.checks:
        if ".bbmb_splice.step1_detailing_viga" not in check.rule_id:
            continue
        details = check.calculation_memory.intermediates.get("step_1_limits")
        if not isinstance(details, list):
            continue
        for item in details:
            if isinstance(item, dict):
                enriched = dict(item)
                enriched.setdefault("source_document", check.source_document)
                enriched.setdefault("rule_id", check.rule_id)
                rows.append(enriched)
    return rows


def _collect_splice_step_1_notes(result: DetailedRunResult) -> list[dict]:
    notes: list[dict] = []
    for check in result.checks:
        if ".bbmb_splice.step1_detailing_viga" not in check.rule_id:
            continue
        details = check.calculation_memory.intermediates.get("step_1_notes")
        if not isinstance(details, list):
            continue
        for item in details:
            if isinstance(item, dict):
                enriched = dict(item)
                enriched.setdefault("source_document", check.source_document)
                enriched.setdefault("rule_id", check.rule_id)
                notes.append(enriched)
    return notes


def _collect_splice_step_2_method(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".bbmb_splice.step2_pernos1_method" not in check.rule_id:
            continue
        report = check.calculation_memory.intermediates.get("method_report")
        if not isinstance(report, dict):
            report = {}
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "notes": check.notes,
            "report": report,
        }
    return None


def _collect_step_2_mpr(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step2_probable_moment_plastic_hinge" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "equation": check.calculation_memory.equation,
        }
    return None


def _collect_step_3_sh(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step3_plastic_hinge_distance" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "equation": check.calculation_memory.equation,
        }
    return None


def _collect_step_4_vh(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step4_shear_at_plastic_hinge" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "equation": check.calculation_memory.equation,
        }
    return None


def _collect_step_5_mf(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step5_probable_moment_face_column" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "equation": check.calculation_memory.equation,
        }
    return None


def _collect_step_11_web_weld_tension_context(result: DetailedRunResult) -> dict | None:
    prequal_inputs: dict = {}
    for check in result.checks:
        if ".06.3." not in check.rule_id:
            continue
        if isinstance(check.calculation_memory.inputs, dict):
            prequal_inputs = check.calculation_memory.inputs
            break
    if not prequal_inputs:
        return None
    return {
        "inputs": prequal_inputs,
    }


def _collect_step_6_1_bolt_tension(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step6_1_bolt_tension_rupture" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_6_2_bolt_shear(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step6_2_bolt_shear_rupture" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_7_1_1_end_plate_flexural(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step7_1_1_end_plate_flexural_yielding" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_7_2_1_end_plate_shear_yielding(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step7_2_1_end_plate_shear_yielding" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_7_2_2_end_plate_shear_rupture(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step7_2_2_end_plate_shear_rupture" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_7_3_1_end_plate_hole_tearout(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step7_3_1_end_plate_hole_tearout" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_7_3_2_end_plate_hole_bearing(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step7_3_2_end_plate_hole_bearing" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_8_1_1_stiffener_weld_tension_rupture(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step8_1_1_stiffener_weld_tension_rupture" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_9_1_1_stiffener_beam_weld_shear_rupture(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step9_1_1_stiffener_beam_weld_shear_rupture" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_10_1_1_beam_shear_yielding(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step10_1_1_beam_shear_yielding" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_12_1_1_column_flange_local_bending(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        rule_id = str(check.rule_id).lower()
        clause = str(check.clause).lower()
        name = str(check.name).lower()
        if (
            ".column_step1_flange_yielding" not in rule_id
            and "flange_yielding" not in rule_id
            and "eq. 6.7-13" not in clause
            and "column flange" not in name
        ):
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump(),
            "capacity": check.capacity.model_dump(),
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _render_step_1_notes(notes: list[dict]) -> str:
    if not notes:
        return ""
    lines: list[str] = []
    lines.append("### 1.1 Notas tecnicas")
    lines.append("")
    note_index = 1
    for item in notes:
        note_id = _format_text(item.get("id"))
        scope = _format_text(item.get("scope")).upper()
        description = _translate_text_es(item.get("description"))
        clause = _render_clause_text(
            item.get("clause"),
            item.get("source_document"),
            item.get("rule_id"),
        )
        note_label = f"1.1.{note_index}"
        note_index += 1
        lines.append(f"#### {note_label} Nota tecnica - {description}")
        lines.append("")
        lines.append(f"- Ambito: `{scope}`")
        lines.append(f"- Clausula: `{clause}`")
        requirement = _translate_text_es(item.get("requirement"))
        if note_id == "section_6_7.beam_flange_to_end_plate_weld_note":
            requirement = (
                "La union entre el ala de la viga y la placa de extremo debe ejecutarse con una soldadura "
                "de ranura CJP sin respaldo. La soldadura de ranura CJP debe realizarse de modo que la raiz "
                "de la soldadura quede del lado del alma de la viga respecto del ala. La cara interior del ala "
                "debe tener una soldadura de filete de c in. (8 mm). Estas soldaduras deben ser de demanda critica."
            )
        if requirement != "n/a" and note_id not in {
            "section_6_3.end_plate_height_derived",
            "section_6_3.end_plate_height_derived_izq",
            "section_6_3.end_plate_geometry_vgder_note",
            "section_6_3.end_plate_geometry_vgizq_note",
            "section_6_3.end_plate_stiffener_geometry_note",
            "section_6_3.end_plate_stiffener_geometry_vgizq_note",
        }:
            lines.append(f"- Requisito: `{requirement}`")
        if note_id in {
            "section_6_3.end_plate_stiffener_geometry_note",
            "section_6_3.end_plate_stiffener_geometry_vgizq_note",
        }:
            formula = _format_text(item.get("formula"))
            h_pest_vgder = _format_quantity(item.get("h_pest_vgder"))
            l_pest_vgder = _format_quantity(item.get("l_pest_vgder"))
            h_pest_vgizq = _format_quantity(item.get("h_pest_vgizq"))
            l_pest_vgizq = _format_quantity(item.get("l_pest_vgizq"))
            ed_pest_vgder = _format_quantity(item.get("ed_pest_vgder"))
            ed_pest_vgizq = _format_quantity(item.get("ed_pest_vgizq"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            lines.append(f"- h_pest_vgder: `{h_pest_vgder}`")
            lines.append(f"- L_pest_vgder: `{l_pest_vgder}`")
            if h_pest_vgizq != "n/a":
                lines.append(f"- h_pest_vgizq: `{h_pest_vgizq}`")
            if l_pest_vgizq != "n/a":
                lines.append(f"- L_pest_vgizq: `{l_pest_vgizq}`")
            lines.append(f"- edge_detailing (Ed_pest_vgder): `{ed_pest_vgder}`")
            if ed_pest_vgizq != "n/a":
                lines.append(f"- edge_detailing (Ed_pest_vgizq): `{ed_pest_vgizq}`")
            lines.append("")
            continue
        if note_id == "section_6_3.end_plate_h_distances_note":
            formula = _format_text(item.get("formula"))
            h1 = _format_quantity(item.get("h1"))
            h2 = _format_quantity(item.get("h2"))
            h3 = _format_quantity(item.get("h3"))
            h4 = _format_quantity(item.get("h4"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            lines.append(f"- h1: `{h1}`")
            lines.append(f"- h2: `{h2}`")
            lines.append(f"- h3: `{h3}`")
            lines.append(f"- h4: `{h4}`")
            lines.append("")
            continue
        if note_id == "section_6_3.end_plate_geometry_vgder_note":
            formula = _format_text(item.get("formula"))
            h1 = _format_quantity(item.get("h1_vgder"))
            h2 = _format_quantity(item.get("h2_vgder"))
            h3 = _format_quantity(item.get("h3_vgder"))
            h4 = _format_quantity(item.get("h4_vgder"))
            dh = _format_quantity(item.get("dh_vgder"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            lines.append(f"- h1_vgder: `{h1}`")
            lines.append(f"- h2_vgder: `{h2}`")
            lines.append(f"- h3_vgder: `{h3}`")
            lines.append(f"- h4_vgder: `{h4}`")
            lines.append(f"- dh_vgder: `{dh}`")
            lines.append("")
            continue
        if note_id == "section_6_3.end_plate_geometry_vgizq_note":
            formula = _format_text(item.get("formula"))
            h1 = _format_quantity(item.get("h1_vgizq"))
            h2 = _format_quantity(item.get("h2_vgizq"))
            h3 = _format_quantity(item.get("h3_vgizq"))
            h4 = _format_quantity(item.get("h4_vgizq"))
            dh = _format_quantity(item.get("dh_vgizq"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            lines.append(f"- h1_vgizq: `{h1}`")
            lines.append(f"- h2_vgizq: `{h2}`")
            lines.append(f"- h3_vgizq: `{h3}`")
            lines.append(f"- h4_vgizq: `{h4}`")
            lines.append(f"- dh_vgizq: `{dh}`")
            lines.append("")
            continue
        if note_id == "section_6_7.end_plate_standard_hole_diameter_note":
            formula = _format_text(item.get("formula"))
            db = _format_quantity(item.get("db"))
            dh = _format_quantity(item.get("dh"))
            hole_add_in = _format_text(item.get("hole_add_in"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            lines.append(f"- db (diametro perno): `{db}`")
            lines.append(f"- dh (agujero estandar): `{dh}`")
            lines.append(f"- Incremento aplicado (in): `{hole_add_in}`")
            lines.append("")
            continue
        if note_id in {
            "section_6_3.end_plate_height_derived",
            "section_6_3.end_plate_height_derived_izq",
        }:
            formula = _format_text(item.get("formula"))
            hpe_der = _format_quantity(item.get("hpe_vgder"))
            hpe_izq = _format_quantity(item.get("hpe_vgizq"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            if hpe_der != "n/a":
                lines.append(f"- Hpe_vgder: `{hpe_der}`")
            if hpe_izq != "n/a":
                lines.append(f"- Hpe_vgizq: `{hpe_izq}`")
            lines.append("")
            continue
        if note_id == "section_2_3_4.protected_zone_length":
            formula = _format_text(item.get("formula"))
            protected_zone_der = _format_quantity(item.get("protected_zone_length_vgder"))
            protected_zone_izq = _format_quantity(item.get("protected_zone_length_vgizq"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            if protected_zone_der != "n/a":
                lines.append(f"- Lpz_vgder: `{protected_zone_der}`")
            if protected_zone_izq != "n/a":
                lines.append(f"- Lpz_vgizq: `{protected_zone_izq}`")
            lines.append("")
            continue
        formula = _format_text(item.get("formula"))
        if formula != "n/a":
            candidate_a_label = _format_text(item.get("candidate_a_label"))
            candidate_a = _format_quantity(item.get("candidate_a"))
            candidate_b_label = _format_text(item.get("candidate_b_label"))
            candidate_b = _format_quantity(item.get("candidate_b"))
            protected_zone = _format_quantity(item.get("protected_zone_length"))
            protected_zone_der = _format_quantity(item.get("protected_zone_length_vgder"))
            protected_zone_izq = _format_quantity(item.get("protected_zone_length_vgizq"))
            derived_value = _format_quantity(item.get("derived_value"))
            lines.append(f"- Formula: `{formula}`")
            lines.append(f"- Candidato A ({candidate_a_label}): `{candidate_a}`")
            lines.append(f"- Candidato B ({candidate_b_label}): `{candidate_b}`")
            if protected_zone_der != "n/a":
                lines.append(f"- Longitud zona protegida viga derecha: `{protected_zone_der}`")
            if protected_zone_izq != "n/a":
                lines.append(f"- Longitud zona protegida viga izquierda: `{protected_zone_izq}`")
            if derived_value != "n/a":
                lines.append(f"- Valor derivado: `{derived_value}`")
            elif protected_zone != "n/a" and protected_zone_der == "n/a" and protected_zone_izq == "n/a":
                lines.append(f"- Longitud zona protegida requerida: `{protected_zone}`")
        lines.append("")
    return "\n".join(lines)


def _render_step_2_mpr(step_2: dict) -> str:
    inputs = step_2.get("inputs", {})
    inter = step_2.get("intermediates", {})
    lines = [
        "## Paso 2 - Momento probable maximo en rotula plastica (Mpr)",
        "",
        "Calculo de momento probable segun Eq. (2.4-1) y Eq. (2.4-2), usando `Ze = Zx` del catalogo de la viga.",
        "",
        f"- Clausula: `{_render_clause_text(step_2.get('clause'), step_2.get('source_document'), step_2.get('rule_id'))}`",
        f"- Ecuacion: `{_format_text(step_2.get('equation'))}`",
        f"- Fy: `{_format_quantity(inputs.get('beam_fy'))}`",
        f"- Fu: `{_format_quantity(inputs.get('beam_fu'))}`",
        f"- Ry: `{_format_text(inputs.get('ry'))}`",
        f"- Ze (catalogo): `{_format_quantity(inputs.get('ze'))}`",
        f"- Cpr: `{_format_text(inter.get('cpr'))}`",
        f"- Mpr calculado: `{_format_quantity(step_2.get('demand'))}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_3_sh(step_3: dict) -> str:
    inputs = step_3.get("inputs", {})
    lines = [
        "## Paso 3 - Distancia de rotula plastica desde la cara de la columna (Sh)",
        "",
        "Para 4E: `Sh = min(d/2, 3bf)`. Para 4ES/8ES: `Sh = Lst + tp`.",
        "",
        f"- Clausula: `{_render_clause_text(step_3.get('clause'), step_3.get('source_document'), step_3.get('rule_id'))}`",
        f"- Ecuacion: `{_format_text(step_3.get('equation'))}`",
        f"- Tipo de conexion: `{_format_text(inputs.get('connection_type'))}`",
        f"- Perfil de viga: `{_format_text(inputs.get('beam_shape'))}`",
        f"- Lst (si aplica): `{_format_quantity(inputs.get('stiffener_length'))}`",
        f"- tp (si aplica): `{_format_quantity(inputs.get('end_plate_thickness'))}`",
        f"- Sh calculado: `{_format_quantity(step_3.get('demand'))}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_4_vh(step_4: dict) -> str:
    inputs = step_4.get("inputs", {})
    inter = step_4.get("intermediates", {})
    beam_connection_sides = _format_text(inputs.get("beam_connection_sides"))
    # Memory report (presentation) is intentionally restricted to right-beam output.
    sides = ["der"]
    lines = [
        "## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)",
        "",
        "Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Lh + Vgravity` y `Vhmin = 2*Mpr/Lh - Vgravity` (se reporta lado derecho).",
        "",
        f"- Clausula: `{_render_clause_text(step_4.get('clause'), step_4.get('source_document'), step_4.get('rule_id'))}`",
        "- Ecuacion: `Vhmax.der = 2*Mpr/Lh.der + Vgravity.der; Vhmin.der = 2*Mpr/Lh.der - Vgravity.der`",
        f"- Configuracion de vigas: `{beam_connection_sides}`",
        f"- Lado gobernante Vhmax: `{_format_text(inputs.get('governing_side_vhmax'))}`",
        f"- Fuente Vhmax seleccionado: `{_format_text(inputs.get('selected_vhmax_source'))}`",
        f"- Mpr: `{_format_scalar_with_unit(inter.get('mpr'), 'kN-mm')}`",
    ]
    for side in sides:
        vgravity_label = "Beam_right_Vgravity" if side == "der" else "Beam_left_Vgravity"
        lines.extend(
            [
                f"- Lh.{side}: `{_format_quantity(inputs.get(f'lh_{side}'))}`",
                f"- {vgravity_label}: `{_format_quantity(inputs.get(f'vgravity_between_hinges_{side}'))}`",
                f"- 2*Mpr/Lh.{side}: `{_format_scalar_with_unit(inter.get(f'2mpr_over_lh_{side}'), 'kN')}`",
                f"- Vh.{side}max: `{_format_scalar_with_unit(inter.get(f'vh_{side}max'), 'kN')}`",
                f"- Vh.{side}min: `{_format_scalar_with_unit(inter.get(f'vh_{side}min'), 'kN')}`",
            ]
        )
    lines.extend(
        [
            f"- Vhmax gobernante: `{_format_quantity(step_4.get('demand'))}`",
        "",
        ]
    )
    return "\n".join(lines)


def _render_step_5_mf(step_5: dict) -> str:
    inputs = step_5.get("inputs", {})
    inter = step_5.get("intermediates", {})
    beam_connection_sides = _format_text(inputs.get("beam_connection_sides"))
    # Memory report (presentation) is intentionally restricted to right-beam output.
    sides = ["der"]
    lines = [
        "## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)",
        "",
        "Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh` (se reporta lado derecho).",
        "",
        f"- Clausula: `{_render_clause_text(step_5.get('clause'), step_5.get('source_document'), step_5.get('rule_id'))}`",
        "- Ecuacion: `Mfmax.der = Mpr + Vhmax.der*Sh; Mfmin.der = Mpr + Vhmin.der*Sh`",
        "- Definicion para diseno: `Mf = Mfmax gobernante`",
        f"- Configuracion de vigas: `{beam_connection_sides}`",
        f"- Lado gobernante Mfmax: `{_format_text(inputs.get('governing_side_mfmax'))}`",
        f"- Fuente Mfmax seleccionado: `{_format_text(inputs.get('selected_mfmax_source'))}`",
        f"- Mpr (intermedio): `{_format_scalar_with_unit(inter.get('mpr'), 'kN-mm')}`",
        f"- Sh (intermedio): `{_format_scalar_with_unit(inter.get('sh'), 'mm')}`",
    ]
    for side in sides:
        lines.extend(
            [
                f"- Vh.{side}max (intermedio): `{_format_scalar_with_unit(inter.get(f'vh_{side}max'), 'kN')}`",
                f"- Vh.{side}min (intermedio): `{_format_scalar_with_unit(inter.get(f'vh_{side}min'), 'kN')}`",
                f"- Mf.{side}max: `{_format_scalar_with_unit(inter.get(f'mf_{side}max'), 'kN-mm')}`",
                f"- Mf.{side}min: `{_format_scalar_with_unit(inter.get(f'mf_{side}min'), 'kN-mm')}`",
            ]
        )
    lines.extend(
        [
        f"- Mf (adoptado) = Mfmax gobernante: `{_format_quantity(step_5.get('demand'))}`",
        "",
        ]
    )
    return "\n".join(lines)


def _render_step_6_bolts(step_6_1: dict | None, step_6_2: dict | None) -> str:
    lines = [
        "## Paso 6 - Revision De Resistencia Pernos",
        "",
    ]
    if step_6_1 is not None:
        inputs = step_6_1.get("inputs", {})
        design_factors = step_6_1.get("design_factors", {})
        lines.extend(
            [
                "### 6.1 Revision de capacidad a traccion",
                "",
                "#### 6.1.1 Estado #1: Rotura en el perno",
                "",
                f"- Clausula: `{_render_clause_text(step_6_1.get('clause'), step_6_1.get('source_document'), step_6_1.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_6_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- h1: `{_format_quantity(inputs.get('h1'))}`",
                f"- h2: `{_format_quantity(inputs.get('h2'))}`",
                f"- h3: `{_format_quantity(inputs.get('h3'))}`",
                f"- h4: `{_format_quantity(inputs.get('h4'))}`",
                f"- Rut_b: `{_format_quantity(step_6_1.get('demand'))}`",
                f"- phiRnt_b: `{_format_quantity(step_6_1.get('capacity'))}`",
                f"- DCRbt: `{_format_text(step_6_1.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_6_1.get('status'))}`",
                "",
            ]
        )
    if step_6_2 is not None:
        inputs = step_6_2.get("inputs", {})
        design_factors = step_6_2.get("design_factors", {})
        lines.extend(
            [
                "### 6.2 Revision de capacidad a cortante",
                "",
                "#### 6.2.1 ELR #1: Rotura por cortante en el perno",
                "",
                f"- Clausula: `{_render_clause_text(step_6_2.get('clause'), step_6_2.get('source_document'), step_6_2.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_6_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vhmax: `{_format_quantity(inputs.get('vhmax'))}`",
                f"- nb: `{_format_text(inputs.get('nb'))}`",
                f"- Ruv2_b: `{_format_quantity(step_6_2.get('demand'))}`",
                f"- phiRnv_b: `{_format_quantity(step_6_2.get('capacity'))}`",
                f"- DCRbv: `{_format_text(step_6_2.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_6_2.get('status'))}`",
                "",
            ]
        )
    return "\n".join(lines)


def _render_step_7_end_plate(
    step_7_1_1: dict | None,
    step_7_2_1: dict | None,
    step_7_2_2: dict | None,
    step_7_3_1: dict | None,
    step_7_3_2: dict | None,
) -> str:
    lines = [
        "## Paso 7 - Revision de resistencia end plate",
        "",
    ]
    if step_7_1_1 is not None:
        inputs = step_7_1_1.get("inputs", {})
        inter = step_7_1_1.get("intermediates", {})
        design_factors = step_7_1_1.get("design_factors", {})
        lines.extend(
            [
                "### 7.1. Revision de capacidad a flexion",
                "",
                "#### 7.1.1. ELR #1: Fluencia (AISC 358-22 .7-8)",
                "",
                f"- Clausula: `{_render_clause_text(step_7_1_1.get('clause'), step_7_1_1.get('source_document'), step_7_1_1.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_1_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Mup: `{_format_quantity(step_7_1_1.get('demand'))}`",
                f"- phiMnb: `{_format_quantity(step_7_1_1.get('capacity'))}`",
                f"- DCRpm: `{_format_text(step_7_1_1.get('dcr'))}`",
                f"- Yp calculado: `{_format_quantity(inputs.get('yp'))}`",
                f"- Tabla Yp aplicada: `{_format_text(inputs.get('yp_table')).replace('Table', 'Tabla')}`",
                f"- Caso Yp: `{_format_text(inputs.get('yp_case'))}`",
                f"- s: `{_format_quantity(inter.get('s'))}`",
                f"- pfi de entrada: `{_format_quantity(inter.get('pfi_input'))}`",
                f"- pfi efectivo: `{_format_quantity(inter.get('pfi_effective'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_1_1.get('status'))}`",
                "",
            ]
        )
    if step_7_2_1 is not None:
        inputs = step_7_2_1.get("inputs", {})
        design_factors = step_7_2_1.get("design_factors", {})
        lines.extend(
            [
                "### 7.2. Revision de capacidad a cortante perpendicular al plano de la platina",
                "",
                "#### 7.2.1. Eje #1: Fluencia por cortante (AISC 358-22 G7-10)",
                "",
                f"- Clausula: `{_render_clause_text(step_7_2_1.get('clause'), step_7_2_1.get('source_document'), step_7_2_1.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_2_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vup: `{_format_quantity(step_7_2_1.get('demand'))}`",
                f"- phiVn1p: `{_format_quantity(step_7_2_1.get('capacity'))}`",
                f"- DCRpv: `{_format_text(step_7_2_1.get('dcr'))}`",
                f"- d (altura viga): `{_format_quantity(inputs.get('d'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_2_1.get('status'))}`",
                "",
            ]
        )
    if step_7_2_2 is not None:
        inputs = step_7_2_2.get("inputs", {})
        design_factors = step_7_2_2.get("design_factors", {})
        lines.extend(
            [
                "#### 7.2.2. Eje #2: Rotura por cortante (AISC 358-22 G7-12)",
                "",
                f"- Clausula: `{_render_clause_text(step_7_2_2.get('clause'), step_7_2_2.get('source_document'), step_7_2_2.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_2_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vup: `{_format_quantity(step_7_2_2.get('demand'))}`",
                f"- phiVnb: `{_format_quantity(step_7_2_2.get('capacity'))}`",
                f"- DCRpv: `{_format_text(step_7_2_2.get('dcr'))}`",
                f"- dh (diametro agujero estandar): `{_format_quantity(inputs.get('dh'))}`",
                f"- d (altura viga): `{_format_quantity(inputs.get('d'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_2_2.get('status'))}`",
                "",
            ]
        )
    if step_7_3_1 is not None or step_7_3_2 is not None:
        lines.extend(
            [
                "### 7.3. Revision de capacidad a cortante paralelo al plano de la platina",
                "",
            ]
        )
    if step_7_3_1 is not None:
        inputs = step_7_3_1.get("inputs", {})
        design_factors = step_7_3_1.get("design_factors", {})
        lines.extend(
            [
                "#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno (AISC 360-22 J3.11a)",
                "",
                f"- Clausula: `{_render_clause_text(step_7_3_1.get('clause'), step_7_3_1.get('source_document'), step_7_3_1.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_3_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vu2p: `{_format_quantity(step_7_3_1.get('demand'))}`",
                f"- phiVn2p: `{_format_quantity(step_7_3_1.get('capacity'))}`",
                f"- DCRpn2: `{_format_text(step_7_3_1.get('dcr'))}`",
                f"- lc: `{_format_quantity(inputs.get('lc'))}`",
                f"- dh: `{_format_quantity(inputs.get('dh'))}`",
                f"- db: `{_format_quantity(inputs.get('db'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_3_1.get('status'))}`",
                "",
            ]
        )
    if step_7_3_2 is not None:
        inputs = step_7_3_2.get("inputs", {})
        design_factors = step_7_3_2.get("design_factors", {})
        lines.extend(
            [
                "#### 7.3.2. ELR #2: Aplastamiento en la perforacion del perno (AISC 360-22 J3.11a)",
                "",
                f"- Clausula: `{_render_clause_text(step_7_3_2.get('clause'), step_7_3_2.get('source_document'), step_7_3_2.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_3_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vu2p: `{_format_quantity(step_7_3_2.get('demand'))}`",
                f"- phiVn2p: `{_format_quantity(step_7_3_2.get('capacity'))}`",
                f"- DCRpn2: `{_format_text(step_7_3_2.get('dcr'))}`",
                f"- lc: `{_format_quantity(inputs.get('lc'))}`",
                f"- dh: `{_format_quantity(inputs.get('dh'))}`",
                f"- db: `{_format_quantity(inputs.get('db'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_3_2.get('status'))}`",
                "",
            ]
        )
    return "\n".join(lines)


def _render_step_8_stiffener_weld(step_8_1_1: dict | None) -> str:
    if step_8_1_1 is None:
        return ""
    inputs = step_8_1_1.get("inputs", {})
    design_factors = step_8_1_1.get("design_factors", {})
    weld_type = _format_text(inputs.get("weld_type_normalized"))
    lines = [
        "## Paso 8 - Revision de Resistencia soldadura #1 (end plate con rigidizador)",
        "",
        "### 8.1. Revision de capacidad a traccion",
        "",
        "#### 8.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)",
        "",
        f"- Clausula: `{_render_clause_text(step_8_1_1.get('clause'), step_8_1_1.get('source_document'), step_8_1_1.get('rule_id'))}`",
        f"- Ecuacion: `{_format_text(step_8_1_1.get('equation'))}`",
        f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
        f"- Tipo soldadura rigidizador: `{weld_type}`",
    ]
    if weld_type == "cjp":
        lines.extend(
            [
                "- CJP: `Cumple`",
                f"- Resultado: `{_render_result_plain_es(step_8_1_1.get('status'))}`",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            f"- Pust: `{_format_quantity(step_8_1_1.get('demand'))}`",
            f"- phiRnst: `{_format_quantity(step_8_1_1.get('capacity'))}`",
            f"- DCRst,w1,t: `{_format_text(step_8_1_1.get('dcr'))}`",
            "- l_st (longitud soldadura calculada): `l_st = hst - clip_st - 2*w_st`",
            f"- l_st: `{_format_quantity(inputs.get('lst'))}`",
            f"- clip_st: `{_format_quantity(inputs.get('clip_st'))}`",
            f"- hst: `{_format_quantity(inputs.get('hst'))}`",
            f"- w_st (espesor soldadura): `{_format_quantity(inputs.get('wst'))}`",
            f"- n_l (lineas soldadura): `{_format_text(inputs.get('nl'))}`",
            f"- Resultado: `{_render_result_plain_es(step_8_1_1.get('status'))}`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_step_9_stiffener_beam_weld(step_9_1_1: dict | None) -> str:
    if step_9_1_1 is None:
        return ""
    inputs = step_9_1_1.get("inputs", {})
    design_factors = step_9_1_1.get("design_factors", {})
    weld_type = _format_text(inputs.get("weld_type_normalized"))
    lines = [
        "## Paso 9 - Revision de resistencia soldadura #2 (viga con rigidizador)",
        "",
        "### 9.1. Revision de capacidad a cortante",
        "",
        "#### 9.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)",
        "",
        f"- Clausula: `{_render_clause_text(step_9_1_1.get('clause'), step_9_1_1.get('source_document'), step_9_1_1.get('rule_id'))}`",
        f"- Ecuacion: `{_format_text(step_9_1_1.get('equation'))}`",
        f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
        f"- Tipo soldadura viga-rigidizador: `{weld_type}`",
    ]
    if weld_type == "cjp":
        lines.extend(
            [
                "- CJP: `Cumple`",
                f"- Resultado: `{_render_result_plain_es(step_9_1_1.get('status'))}`",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            f"- Vust,w2: `{_format_quantity(step_9_1_1.get('demand'))}`",
            f"- phiVnst,w2: `{_format_quantity(step_9_1_1.get('capacity'))}`",
            f"- DCRst,w2,v: `{_format_text(step_9_1_1.get('dcr'))}`",
            "- l_st,w2 (longitud soldadura calculada): `l_st,w2 = Lst - clip_st - 2*w_st`",
            f"- l_st,w2: `{_format_quantity(inputs.get('lst_w2'))}`",
            f"- Lst: `{_format_quantity(inputs.get('lst'))}`",
            f"- clip_st: `{_format_quantity(inputs.get('clip_st'))}`",
            f"- w_st,2 (espesor soldadura): `{_format_quantity(inputs.get('wst2'))}`",
            f"- n_l,w2 (lineas soldadura): `{_format_text(inputs.get('nl_w2'))}`",
            f"- Resultado: `{_render_result_plain_es(step_9_1_1.get('status'))}`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_step_10_beam_shear(step_10_1_1: dict | None) -> str:
    if step_10_1_1 is None:
        return ""
    inputs = step_10_1_1.get("inputs", {})
    inter = step_10_1_1.get("intermediates", {})
    design_factors = step_10_1_1.get("design_factors", {})
    lines = [
        "## Paso 10 - Revision de resistencia de la viga",
        "",
        "### 10.1. Revision de capacidad a cortante",
        "",
        "#### 10.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1)",
        "",
        f"- Clausula: `{_render_clause_text(step_10_1_1.get('clause'), step_10_1_1.get('source_document'), step_10_1_1.get('rule_id'))}`",
        f"- Ecuacion: `{_format_text(step_10_1_1.get('equation'))}`",
        f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
        f"- Vubm: `{_format_quantity(step_10_1_1.get('demand'))}`",
        f"- phiVnbm: `{_format_quantity(step_10_1_1.get('capacity'))}`",
        f"- DCRbm,v: `{_format_text(step_10_1_1.get('dcr'))}`",
        f"- Cv1: `{_format_text(inputs.get('cv1'))}`",
        f"- kv: `{_format_text(inter.get('kv'))}`",
        f"- h/tw: `{_format_text(inter.get('h_over_tw'))}`",
        f"- h: `{_format_scalar_with_unit(inter.get('h_clear'), 'mm')}`",
        f"- Resultado: `{_render_result_plain_es(step_10_1_1.get('status'))}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_11_end_plate_beam_web_weld_tension(step_11_ctx: dict | None, step_10_1_1: dict | None) -> str:
    if step_11_ctx is None:
        return ""
    step_11_inputs = step_11_ctx.get("inputs", {})
    step_10_inputs = step_10_1_1.get("inputs", {}) if step_10_1_1 is not None else {}

    weld_type_raw = step_11_inputs.get("end_plate_beam_web_weld_type")
    weld_thickness_twe = step_11_inputs.get("end_plate_beam_web_weld_thickness_twe")
    weld_type = _normalize_weld_type_step11(weld_type_raw)
    pfi_q = _as_quantity(step_11_inputs.get("edge_pfi"))
    pb_q = _as_quantity(step_11_inputs.get("pitch_pb"))
    twe_q = _as_quantity(weld_thickness_twe)
    fybm_q = _as_quantity(step_10_inputs.get("fybm"))
    tw_bm_q = _as_quantity(step_10_inputs.get("tw_bm"))
    fexx_q = _as_quantity(step_11_inputs.get("weld_fexx"))
    nl_raw = step_11_inputs.get("end_plate_beam_web_weld_lines_nl")
    unit_system = _infer_unit_system_from_quantity(step_11_inputs.get("edge_pfi"))
    if unit_system is None:
        unit_system = _infer_unit_system_from_quantity(step_10_inputs.get("tw_bm"))
    try:
        nl = int(nl_raw) if nl_raw is not None else None
    except (TypeError, ValueError):
        nl = None
    if nl is not None and nl < 1:
        nl = None
    phi = 0.9

    hwef_q: Quantity | None = None
    pu_q: Quantity | None = None
    phi_pn_q: Quantity | None = None
    dcr_ww3p = None
    if unit_system is not None and pfi_q is not None and pb_q is not None:
        hwef_q = compute_effective_web_weld_length(
            pfi=pfi_q,
            pb=pb_q,
            unit_system=unit_system,
        )["hwef"]
    if unit_system is not None and hwef_q is not None and fybm_q is not None and tw_bm_q is not None:
        pu_q = compute_plate_tension_demand_from_yielding(
            fy=fybm_q,
            thickness=tw_bm_q,
            effective_length=hwef_q,
            unit_system=unit_system,
        )["pu"]
    if (
        unit_system is not None
        and hwef_q is not None
        and fexx_q is not None
        and twe_q is not None
        and nl is not None
    ):
        phi_pn_q = WeldFillet(
            fexx=fexx_q,
            weld_size=twe_q,
            weld_length=hwef_q,
            weld_lines=nl,
            unit_system=unit_system,
            phi=phi,
        ).design_strength()["phi_rn"]
    if pu_q is not None and phi_pn_q is not None and phi_pn_q.value > 0.0:
        dcr_ww3p = compute_dcr(demand=pu_q, capacity=phi_pn_q)["dcr"]

    hwef_text = _format_quantity(hwef_q.model_dump()) if hwef_q is not None else "n/a"
    puww3_text = _format_quantity(pu_q.model_dump()) if pu_q is not None else "n/a"
    phi_pnww3_text = _format_quantity(phi_pn_q.model_dump()) if phi_pn_q is not None else "n/a"
    dcr_text = _format_decimal(dcr_ww3p) if dcr_ww3p is not None else "n/a"
    twe_text = _format_quantity(weld_thickness_twe)

    if weld_type == "cjp":
        result_line = "Cumple"
        puww3_text = "n/a (CJP)"
        phi_pnww3_text = "n/a (CJP)"
        dcr_text = "n/a (CJP)"
    elif weld_type == "fillet" and dcr_ww3p is not None:
        result_line = "Cumple" if dcr_ww3p <= 1.0 else "No cumple"
    else:
        result_line = "No cumple"

    lines = [
        "## Paso 11 - Revision de resistencia de soldadura viga-alma a end plate",
        "",
        "### 11.1 Revision capacidad a traccion",
        "",
        "#### 11.1.1 ELR #1: Rotura de soldadura",
        "",
        "- Clausula: `Documento: AISC 358-22 + AISC 360-22 | Seccion: Seccion 6.7 + AISC 360-22 J2.4`",
        "- Ecuacion: `Fillet: Puww3 = Fybm*tw*hwef; hwef = Pfi + Pb + 150 mm; phiPnww3 = phi*nl*0.6*Fexx*0.707*hwef*ww3; DCRww3p = Puww3/phiPnww3`",
        f"- phi usado: `{_format_decimal(phi)}`",
        "- Fuente de input: `geometry.welds.weld_3`",
        "- Soldadura #3: `viga (alma) con end plate`",
        f"- Tipo de soldadura viga-end_plate: `{_format_text(weld_type_raw)}`",
    ]
    if weld_type == "cjp":
        lines.extend(
            [
                "- CJP: `Cumple`",
                f"- Resultado: `{result_line}`",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            "- Longitud de soldadura: `no se usa como input en este chequeo`",
            f"- Espesor/tamano de soldadura (twe = ww3): `{twe_text}`",
            f"- nl (numero de cordones): `{_format_text(nl) if nl is not None else 'n/a (input requerido)'}`",
            f"- hwef: `{hwef_text}`",
            f"- Puww3: `{puww3_text}`",
            f"- phiPnww3: `{phi_pnww3_text}`",
            f"- DCRww3p: `{dcr_text}`",
            f"- Resultado: `{result_line}`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_step_12_column_flange_local_bending(step_12_1_1: dict | None, step_11_ctx: dict | None) -> str:
    inputs = step_12_1_1.get("inputs", {}) if isinstance(step_12_1_1, dict) else {}
    capacity = step_12_1_1.get("capacity") if isinstance(step_12_1_1, dict) else None
    design_factors = step_12_1_1.get("design_factors", {}) if isinstance(step_12_1_1, dict) else {}
    prequal_inputs = step_11_ctx.get("inputs", {}) if isinstance(step_11_ctx, dict) else {}

    tcp_mm = _quantity_to_mm(prequal_inputs.get("continuity_plate_thickness_tcp"))
    enabled_raw = prequal_inputs.get("continuity_plate_enabled")
    enabled_flag: bool | None = None
    if isinstance(enabled_raw, bool):
        enabled_flag = enabled_raw
    elif isinstance(enabled_raw, str):
        normalized = enabled_raw.strip().lower()
        if normalized in {"true", "si", "sí", "yes", "1"}:
            enabled_flag = True
        elif normalized in {"false", "no", "0"}:
            enabled_flag = False
    has_continuity_plate = enabled_flag if enabled_flag is not None else (tcp_mm is not None and tcp_mm > 0.0)
    bp_mm = _quantity_to_mm(prequal_inputs.get("end_plate_width_bp"))
    g_mm = _quantity_to_mm(prequal_inputs.get("bolt_gage_g"))
    s_mm = None
    if bp_mm is not None and g_mm is not None and bp_mm > 0.0 and g_mm > 0.0:
        s_mm = 0.5 * ((bp_mm * g_mm) ** 0.5)

    tcf_q = _as_quantity(capacity)
    yc_q = _as_quantity(inputs.get("yc"))
    fyc_q = _as_quantity(inputs.get("column_fy"))
    mf_q = _as_quantity(inputs.get("mf"))
    unit_system = _infer_unit_system_from_quantity(capacity)
    if unit_system is None:
        unit_system = _infer_unit_system_from_quantity(inputs.get("column_fy"))
    phi_input = design_factors.get("phi_d")
    try:
        phi = float(phi_input)
    except (TypeError, ValueError):
        phi = 1.0
    phi_mn_q: Quantity | None = None
    if unit_system is not None and tcf_q is not None and yc_q is not None and fyc_q is not None:
        phi_mn_q = compute_column_flange_local_bending_strength(
            t_cf=tcf_q,
            f_yc=fyc_q,
            y_parameter=yc_q,
            phi=phi,
            unit_system=unit_system,
        )["phi_mn"]

    mucf_q = None
    if mf_q is not None and phi_mn_q is not None:
        mucf_q = _convert_moment_to_unit(mf_q, phi_mn_q.unit)
    dcr_cfm = None
    if mucf_q is not None and phi_mn_q is not None:
        try:
            dcr_cfm = compute_dcr(demand=mucf_q, capacity=phi_mn_q)["dcr"]
        except ValueError:
            dcr_cfm = None

    y_symbol = "Y_cs" if has_continuity_plate else "Y_c"
    continuity_text = "hay platinas de continuidad" if has_continuity_plate else "no hay platinas de continuidad"
    phi_mncf_text = _format_quantity(phi_mn_q.model_dump()) if phi_mn_q is not None else "n/a"

    dcr_text = _format_decimal(dcr_cfm) if dcr_cfm is not None else "n/a"
    if dcr_cfm is None:
        result_line = "n/a"
    else:
        result_line = "Cumple" if dcr_cfm <= 1.0 else "No cumple"
    clause_text = (
        _render_clause_text(
            step_12_1_1.get("clause"),
            step_12_1_1.get("source_document"),
            step_12_1_1.get("rule_id"),
        )
        if isinstance(step_12_1_1, dict)
        else "Documento: AISC 358-22 | Seccion: 6.7.2"
    )

    lines = [
        "## Paso 12 - Revision de resistencia de la aleta de la columna",
        "",
        "### 12.1. Revision de capacidad a flexion",
        "",
        "#### 12.1.1 ELR # 1: Flexion local de la aleta (LFB) (AISC 358-22 6.7.2)",
        "",
        f"- Clausula: `{clause_text}`",
        f"- M_ucf: `{_format_quantity(inputs.get('mf'))}`",
        f"- phi usado: `{_format_decimal(phi)}`",
        f"- Condicion aplicable: `{continuity_text}`",
        f"- s: `{_format_decimal(s_mm)} mm`" if s_mm is not None else "- s: `n/a`",
        f"- {y_symbol} usado: `{_format_quantity(inputs.get('yc'))}`",
        f"- Ecuacion: `phiM_ncf = phi((t_cf^2 * f_yc * {y_symbol})/1.11)`",
        f"- phiM_ncf: `{phi_mncf_text}`",
        "- Ecuacion DCR: `DCR_cfm = M_ucf/(phiM_ncf)`",
        f"- DCR_cfm: `{dcr_text}`",
        f"- Resultado: `{result_line}`",
        "",
        "Donde:",
        "- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).",
        "- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).",
        "",
    ]
    return "\n".join(lines)


def _render_splice_step_1_notes(notes: list[dict], *, allowed_scopes: set[str] | None = None) -> str:
    lines: list[str] = []
    for item in notes:
        note_id = _format_text(item.get("id"))
        scope = _format_text(item.get("scope")).upper()
        if allowed_scopes is not None and scope not in allowed_scopes:
            continue
        if note_id == "bbmb_splice.step1.geometry_note":
            lines.extend(
                [
                    "### Nota tecnica - Geometria",
                    "",
                    "- Ambito: `VIGA`",
                    f"- Clausula: `{_render_clause_text(item.get('clause'), item.get('source_document'), item.get('rule_id'))}`",
                    f"- Separacion entre vigas (alpha): `{_format_quantity(item.get('alpha'))}`",
                    f"- Tolerancia de fabricacion en longitud de viga ({_format_text(item.get('beam_length_tolerance_var'))}): `{_format_quantity(item.get('beam_length_tolerance'))}`",
                    f"- Referencia tolerancia: `{_format_text(item.get('beam_length_tolerance_ref'))}`",
                    f"- Separacion horizontal entre columnas de pernos del alma ({_format_text(item.get('s1x_var'))}): `{_format_quantity(item.get('s1x'))}`",
                    f"- Distancia de borde en direccion X del grupo de pernos del alma ({_format_text(item.get('le1x1_var'))}): `{_format_quantity(item.get('le1x1'))}`",
                    f"- Formula: `{_format_text(item.get('le1x1_prime_formula'))}`",
                    f"- Distancia de borde ajustada ({_format_text(item.get('le1x1_prime_var'))}): `{_format_quantity(item.get('le1x1_prime'))}`",
                    f"- Altura de viga ({_format_text(item.get('dvg_var'))}): `{_format_quantity(item.get('dvg'))}`",
                    f"- Distancia vertical entre cara exterior de aleta inferior y fila inferior de pernos ({_format_text(item.get('le1y3_var'))}): `{_format_quantity(item.get('le1y3'))}`",
                    f"- Formula: `{_format_text(item.get('le1y4_formula'))}`",
                    f"- Distancia complementaria vertical ({_format_text(item.get('le1y4_var'))}): `{_format_quantity(item.get('le1y4'))}`",
                    f"- Diametro de perforacion para pernos 1 (dh.1): `{_format_quantity(item.get('dh_1'))}`",
                    f"- Diametro de perforacion para pernos 2 (dh.2): `{_format_quantity(item.get('dh_2'))}`",
                    f"- Formula Area neta de cortante 1: `{_format_text(item.get('anv1_formula'))}`",
                    f"- Area neta de cortante 1 (Anv.y1.vg): `{_format_quantity(item.get('anv1'))}`",
                    f"- Formula Area neta a traccion 1: `{_format_text(item.get('ant1_formula'))}`",
                    f"- Area neta a traccion 1 (Ant.x1.vg): `{_format_quantity(item.get('ant1'))}`",
                    f"- Formula factor de rezago de cortante 1: `{_format_text(item.get('us1_formula'))}`",
                    f"- Factor de rezago de cortante 1 (U11): `{_format_text(item.get('us1'))}`",
                    "",
                ]
            )
            continue
        if note_id == "bbmb_splice.step1.geometry_formulas_plt1_note":
            lines.extend(
                [
                    "### Nota tecnica - Formulas geometricas (Platina 1)",
                    "",
                    "- Ambito: `PLATINA_1`",
                    f"- Clausula: `{_render_clause_text(item.get('clause'), item.get('source_document'), item.get('rule_id'))}`",
                    f"- Formula hp1: `{_format_text(item.get('hp1_formula'))}`",
                    f"- hp1 calculado: `{_format_quantity(item.get('hp1_calc'))}`",
                    f"- Formula bp1: `{_format_text(item.get('bp1_formula'))}`",
                    f"- bp1 calculado: `{_format_quantity(item.get('bp1_calc'))}`",
                    "",
                ]
            )
            continue
        if note_id == "bbmb_splice.step1.plate_1_hole_diameter_note":
            lines.extend(
                [
                    "### Nota tecnica - Diametro de perforacion (Platina 1)",
                    "",
                    "- Ambito: `PLATINA_1`",
                    f"- Clausula: `{_render_clause_text(item.get('clause'), item.get('source_document'), item.get('rule_id'))}`",
                    f"- Formula: `{_format_text(item.get('formula'))}`",
                    f"- {_format_text(item.get('db_var'))}: `{_format_quantity(item.get('db'))}`",
                    f"- {_format_text(item.get('dh_var'))}: `{_format_quantity(item.get('dh'))}`",
                    f"- Incremento aplicado (in): `{_format_text(item.get('hole_add_in'))}`",
                    "",
                ]
            )
            continue
        if note_id == "bbmb_splice.step1.geometry_formulas_plt2_note":
            lines.extend(
                [
                    "### Nota tecnica - Formulas geometricas (Platina 2)",
                    "",
                    "- Ambito: `PLATINA_2`",
                    f"- Clausula: `{_render_clause_text(item.get('clause'), item.get('source_document'), item.get('rule_id'))}`",
                    f"- Formula bp2: `{_format_text(item.get('bp2_formula'))}`",
                    f"- bp2 calculado: `{_format_quantity(item.get('bp2_calc'))}`",
                    f"- Formula lp2: `{_format_text(item.get('lp2_formula'))}`",
                    f"- lp2 calculado: `{_format_quantity(item.get('lp2_calc'))}`",
                    "",
                ]
            )
            continue
        if note_id == "bbmb_splice.step1.plate_2_hole_diameter_note":
            lines.extend(
                [
                    "### Nota tecnica - Diametro de perforacion (Platina 2)",
                    "",
                    "- Ambito: `PLATINA_2`",
                    f"- Clausula: `{_render_clause_text(item.get('clause'), item.get('source_document'), item.get('rule_id'))}`",
                    f"- Formula: `{_format_text(item.get('formula'))}`",
                    f"- {_format_text(item.get('db_var'))}: `{_format_quantity(item.get('db'))}`",
                    f"- {_format_text(item.get('dh_var'))}: `{_format_quantity(item.get('dh'))}`",
                    f"- Incremento aplicado (in): `{_format_text(item.get('hole_add_in'))}`",
                    "",
                ]
            )
            continue
        if note_id == "bbmb_splice.step1.bolt_group_1_properties_note":
            lines.extend(
                [
                    "### Nota tecnica - Propiedades del perno (Grupo 1)",
                    "",
                    "- Ambito: `PERNOS_1`",
                    f"- Clausula: `{_render_clause_text(item.get('clause'), item.get('source_document'), item.get('rule_id'))}`",
                    f"- Perno: `{_format_text(item.get('bolt_shape'))}`",
                    f"- Clasificacion: `{_format_text(item.get('classification'))}`",
                    f"- Norma de fabricacion: `{_format_text(item.get('fabrication_standard'))}`",
                    f"- Condicion de rosca: `{_format_text(item.get('thread_condition'))}`",
                    f"- Tipo de apriete: `{_format_text(item.get('tightening_type'))}`",
                    f"- Diametro nominal (db.1): `{_format_quantity(item.get('diameter_nominal'))}`",
                    f"- Longitud de vastago: `{_format_quantity(item.get('length_shank'))}`",
                    f"- Width across flats: `{_format_quantity(item.get('width_across_flats'))}`",
                    f"- Diametro de cabeza: `{_format_quantity(item.get('head_diameter'))}`",
                    f"- Altura de cabeza: `{_format_quantity(item.get('head_height'))}`",
                    "",
                ]
            )
            continue
        if note_id == "bbmb_splice.step1.bolt_group_2_properties_note":
            lines.extend(
                [
                    "### Nota tecnica - Propiedades del perno (Grupo 2)",
                    "",
                    "- Ambito: `PERNOS_2`",
                    f"- Clausula: `{_render_clause_text(item.get('clause'), item.get('source_document'), item.get('rule_id'))}`",
                    f"- Perno: `{_format_text(item.get('bolt_shape'))}`",
                    f"- Clasificacion: `{_format_text(item.get('classification'))}`",
                    f"- Norma de fabricacion: `{_format_text(item.get('fabrication_standard'))}`",
                    f"- Condicion de rosca: `{_format_text(item.get('thread_condition'))}`",
                    f"- Tipo de apriete: `{_format_text(item.get('tightening_type'))}`",
                    f"- Diametro nominal (db.2): `{_format_quantity(item.get('diameter_nominal'))}`",
                    f"- Longitud de vastago: `{_format_quantity(item.get('length_shank'))}`",
                    f"- Width across flats: `{_format_quantity(item.get('width_across_flats'))}`",
                    f"- Diametro de cabeza: `{_format_quantity(item.get('head_diameter'))}`",
                    f"- Altura de cabeza: `{_format_quantity(item.get('head_height'))}`",
                    "",
                ]
            )
            continue
    return "\n".join(lines)


def _render_splice_step_2_method_block(step2: dict | None) -> str:
    if not isinstance(step2, dict):
        return "\n".join(
            [
                "### Punto 2 - Metodo ICR/Elastic",
                "",
                "Sin resultados de metodo ICR/Elastic para este caso.",
                "",
            ]
        )
    report = step2.get("report")
    if not isinstance(report, dict):
        report = {}
    method = _format_text(report.get("method_selected"))
    px = _format_quantity(report.get("px"))
    py = _format_quantity(report.get("py"))
    ex = _format_quantity(report.get("ex"))
    ey = _format_quantity(report.get("ey"))
    e_source = _format_text(report.get("eccentricity_source"))
    mz = _format_quantity(report.get("mz"))
    demand = _format_quantity(report.get("demand"))
    capacity = _format_quantity(report.get("capacity"))
    dcr = _format_text(report.get("dcr"))
    cu = _format_text(report.get("cu"))
    result = _render_result_label(step2.get("status"))
    icr_compare = _format_quantity(report.get("icr_compare_capacity"))
    final_residual = _format_text(report.get("final_residual"))
    n_iterations = _format_text(report.get("n_iterations"))
    lines = [
        "### Punto 2 - Metodo ICR/Elastic",
        "",
        f"- Metodo seleccionado: `{method}`",
        f"- Px: `{px}`",
        f"- Py: `{py}`",
        f"- ex: `{ex}`",
        f"- ey: `{ey}`",
        f"- Fuente excentricidad: `{e_source}`",
        f"- Mz: `{mz}`",
        f"- Demanda (metodo activo): `{demand}`",
        f"- Capacidad (metodo activo): `{capacity}`",
        f"- DCR (metodo activo): `{dcr}`",
        f"- Residual final ICR: `{final_residual}`",
        f"- Iteraciones ICR: `{n_iterations}`",
    ]
    if method == "icr" and cu != "n/a":
        lines.append(f"- Coeficiente Cu (ICR): `{cu}`")
    if icr_compare != "n/a":
        lines.append(f"- Picr comparativo: `{icr_compare}`")
    notes = _format_text(step2.get("notes"))
    if notes != "n/a":
        lines.append(f"- Nota: `{notes}`")
    lines.extend(
        [
            f"- Clausula: `{_render_clause_text(step2.get('clause'), step2.get('source_document'), step2.get('rule_id'))}`",
            f"- Resultado: {result}",
            "",
        ]
    )
    return "\n".join(lines)


def _render_fully_restrained_splice_outline(rows_viga: list[dict], notes_viga: list[dict], step2_pernos1: dict | None) -> str:
    def _rows_for_scope(scope: str) -> list[dict]:
        target = scope.upper()
        return [item for item in rows_viga if str(item.get("scope", "")).upper() == target]

    def _render_scope_block(*, title: str, scope: str) -> list[str]:
        section_lines: list[str] = [
            title,
            "",
            "### Punto 1 - Revision geometrica de detalle (detailing checks)",
            "",
        ]
        scoped_rows = _rows_for_scope(scope)
        if scoped_rows:
            section_lines.append(_render_step_1_list(scoped_rows))
        else:
            section_lines.append("No hay chequeos de detailing en punto 1 para este ambito.")

        scoped_notes = _render_splice_step_1_notes(notes_viga, allowed_scopes={scope.upper()})
        if scoped_notes:
            section_lines.append(scoped_notes)
        else:
            section_lines.extend(["", "Sin notas tecnicas en punto 1."])
        section_lines.append("")
        return section_lines

    lines = [
        "## Revision conexion: Viga",
        "",
        "### Punto 1 - Revision geometrica de detalle (detailing checks)",
        "",
    ]
    rows_viga_scope = _rows_for_scope("VIGA")
    if rows_viga_scope:
        lines.append(_render_step_1_list(rows_viga_scope))
    else:
        lines.append("No hay chequeos de detailing en punto 1 para este ambito.")
    rendered_notes = _render_splice_step_1_notes(notes_viga, allowed_scopes={"VIGA"})
    if rendered_notes:
        lines.append(rendered_notes)
    lines.append("")
    lines.extend(_render_scope_block(title="## Revision conexion: Platina 1", scope="PLATINA_1"))
    lines.extend(_render_scope_block(title="## Revision conexion: Pernos 1", scope="PERNOS_1"))
    lines.append(_render_splice_step_2_method_block(step2_pernos1))
    lines.extend(_render_scope_block(title="## Revision conexion: Platina 2", scope="PLATINA_2"))
    lines.extend(_render_scope_block(title="## Revision conexion: Pernos 2", scope="PERNOS_2"))
    return "\n".join(lines)

def _render_step_1_list(rows: list[dict]) -> str:
    lines: list[str] = []
    lines.append("### 1.2 Revisiones de propiedades geometricas")
    lines.append("")
    for idx, item in enumerate(rows, start=1):
        scope = str(item.get("scope", "n/a")).upper()
        description = _translate_text_es(item.get("description"))
        calculated_symbol = str(item.get("calculated_symbol", "calc"))
        limit_symbol = str(item.get("limit_symbol", "lim"))
        calculated = _format_quantity(item.get("calculated"))
        result_text = _render_result_label(item.get("result", item.get("status", "UNKNOWN")))
        clause = _render_clause_text(
            item.get("clause"),
            item.get("source_document"),
            item.get("rule_id"),
        )
        comparison_mode = str(item.get("comparison", ""))

        if comparison_mode == "range":
            minimum = _format_quantity(item.get("minimum"))
            maximum = _format_quantity(item.get("maximum"))
            verification = (
                f"{calculated_symbol} in {limit_symbol}; {minimum} <= {calculated} <= {maximum}"
            )
        elif comparison_mode == "equals":
            calculated_text = _format_text(item.get("calculated_text"))
            expected_text = _format_text(item.get("expected_text"))
            verification = f"{calculated_symbol} == {limit_symbol}; '{calculated_text}' == '{expected_text}'"
        elif comparison_mode == "family_in":
            calculated_text = _format_text(item.get("calculated_text"))
            families = item.get("allowed_families")
            allowed = ", ".join(str(v) for v in families) if isinstance(families, list) else limit_symbol
            verification = f"{calculated_symbol} in {limit_symbol}; '{calculated_text}' in {{{allowed}}}"
        elif comparison_mode == "in_set":
            calculated_text = _format_text(item.get("calculated_text"))
            allowed_values = item.get("allowed_values")
            allowed = ", ".join(str(v) for v in allowed_values) if isinstance(allowed_values, list) else limit_symbol
            verification = f"{calculated_symbol} in {limit_symbol}; '{calculated_text}' in {{{allowed}}}"
        elif comparison_mode == "conditional_allowed_set":
            thickness = _format_quantity(item.get("thickness"))
            thickness_limit = _format_quantity(item.get("thickness_limit"))
            calculated_text = _format_text(item.get("calculated_text"))
            allowed_values = item.get("allowed_values")
            allowed = ", ".join(str(v) for v in allowed_values) if isinstance(allowed_values, list) else limit_symbol
            governing = _format_text(item.get("governing_condition"))
            if governing == "cjp_or_pjp_always_permitted":
                verification = (
                    f"weld_cp in {{cjp, pjp}} => cumple siempre; "
                    f"tcp={thickness}; weld_cp='{calculated_text}'"
                )
            elif governing == "double_sided_fillet_requires_tcp_le_limit":
                verification = (
                    f"if weld_cp='double_sided_fillet': tcp <= {thickness_limit}; "
                    f"tcp={thickness}; weld_cp='{calculated_text}'"
                )
            else:
                verification = (
                    f"weld_cp in {{{allowed}}} y regla de espesor para double_sided_fillet; "
                    f"tcp={thickness}; weld_cp='{calculated_text}'"
                )
        elif comparison_mode == "compound":
            verification = _format_text(item.get("verification_text"))
            minimum = _format_quantity(item.get("minimum"))
            maximum = _format_quantity(item.get("maximum"))
            if minimum != "n/a" and maximum != "n/a":
                verification = f"{verification}; [min,max] = [{minimum}, {maximum}]"
        else:
            comparison = str(item.get("comparison_text", "vs"))
            limit = _format_quantity(item.get("limit"))
            verification = f"{calculated_symbol} {comparison} {limit_symbol}; {calculated} {comparison} {limit}"

        lines.append(f"#### Chequeo 1.2.{idx} - {description} (`{calculated_symbol}`)")
        lines.append("")
        lines.append(f"- Ambito: `{scope}`")
        lines.append(f"- Verificacion: `{verification}`")
        lines.append(f"- Clausula: `{clause}`")
        lines.append(f"- Resultado: {result_text}")
        lines.append("")
    return "\n".join(lines)


def _render_step_1_list_grouped_by_scope(rows: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for item in rows:
        scope = str(item.get("scope", "n/a")).upper()
        grouped.setdefault(scope, []).append(item)

    lines: list[str] = []
    lines.append("### 1.2 Revisiones de propiedades geometricas")
    lines.append("")
    idx = 1
    for scope in sorted(grouped.keys()):
        lines.append(f"#### Ambito: `{scope}`")
        lines.append("")
        for item in grouped[scope]:
            description = _translate_text_es(item.get("description"))
            calculated_symbol = str(item.get("calculated_symbol", "calc"))
            limit_symbol = str(item.get("limit_symbol", "lim"))
            calculated = _format_quantity(item.get("calculated"))
            result_text = _render_result_label(item.get("result", item.get("status", "UNKNOWN")))
            clause = _render_clause_text(
                item.get("clause"),
                item.get("source_document"),
                item.get("rule_id"),
            )
            comparison_mode = str(item.get("comparison", ""))

            if comparison_mode == "range":
                minimum = _format_quantity(item.get("minimum"))
                maximum = _format_quantity(item.get("maximum"))
                verification = (
                    f"{calculated_symbol} in {limit_symbol}; {minimum} <= {calculated} <= {maximum}"
                )
            elif comparison_mode == "equals":
                calculated_text = _format_text(item.get("calculated_text"))
                expected_text = _format_text(item.get("expected_text"))
                verification = f"{calculated_symbol} == {limit_symbol}; '{calculated_text}' == '{expected_text}'"
            elif comparison_mode == "family_in":
                calculated_text = _format_text(item.get("calculated_text"))
                families = item.get("allowed_families")
                allowed = ", ".join(str(v) for v in families) if isinstance(families, list) else limit_symbol
                verification = f"{calculated_symbol} in {limit_symbol}; '{calculated_text}' in {{{allowed}}}"
            elif comparison_mode == "in_set":
                calculated_text = _format_text(item.get("calculated_text"))
                allowed_values = item.get("allowed_values")
                allowed = ", ".join(str(v) for v in allowed_values) if isinstance(allowed_values, list) else limit_symbol
                verification = f"{calculated_symbol} in {limit_symbol}; '{calculated_text}' in {{{allowed}}}"
            elif comparison_mode == "conditional_allowed_set":
                thickness = _format_quantity(item.get("thickness"))
                thickness_limit = _format_quantity(item.get("thickness_limit"))
                calculated_text = _format_text(item.get("calculated_text"))
                allowed_values = item.get("allowed_values")
                allowed = ", ".join(str(v) for v in allowed_values) if isinstance(allowed_values, list) else limit_symbol
                governing = _format_text(item.get("governing_condition"))
                if governing == "cjp_or_pjp_always_permitted":
                    verification = (
                        f"weld_cp in {{cjp, pjp}} => cumple siempre; "
                        f"tcp={thickness}; weld_cp='{calculated_text}'"
                    )
                elif governing == "double_sided_fillet_requires_tcp_le_limit":
                    verification = (
                        f"if weld_cp='double_sided_fillet': tcp <= {thickness_limit}; "
                        f"tcp={thickness}; weld_cp='{calculated_text}'"
                    )
                else:
                    verification = (
                        f"weld_cp in {{{allowed}}} y regla de espesor para double_sided_fillet; "
                        f"tcp={thickness}; weld_cp='{calculated_text}'"
                    )
            elif comparison_mode == "compound":
                verification = _format_text(item.get("verification_text"))
                minimum = _format_quantity(item.get("minimum"))
                maximum = _format_quantity(item.get("maximum"))
                if minimum != "n/a" and maximum != "n/a":
                    verification = f"{verification}; [min,max] = [{minimum}, {maximum}]"
            else:
                comparison = str(item.get("comparison_text", "vs"))
                limit = _format_quantity(item.get("limit"))
                verification = f"{calculated_symbol} {comparison} {limit_symbol}; {calculated} {comparison} {limit}"

            lines.append(f"#### Chequeo 1.2.{idx} - {description} (`{calculated_symbol}`)")
            lines.append("")
            lines.append(f"- Ambito: `{scope}`")
            lines.append(f"- Verificacion: `{verification}`")
            lines.append(f"- Clausula: `{clause}`")
            lines.append(f"- Resultado: {result_text}")
            lines.append("")
            idx += 1
    return "\n".join(lines)


def render_memory_markdown(result: DetailedRunResult) -> str:
    rows = _collect_step_1_rows(result)
    notes = _collect_step_1_notes(result)
    splice_rows_viga = _collect_splice_step_1_rows(result)
    splice_notes_viga = _collect_splice_step_1_notes(result)
    splice_step_2_pernos1 = _collect_splice_step_2_method(result)
    step_2 = _collect_step_2_mpr(result)
    step_3 = _collect_step_3_sh(result)
    step_4 = _collect_step_4_vh(result)
    step_5 = _collect_step_5_mf(result)
    step_6_1 = _collect_step_6_1_bolt_tension(result)
    step_6_2 = _collect_step_6_2_bolt_shear(result)
    step_7_1_1 = _collect_step_7_1_1_end_plate_flexural(result)
    step_7_2_1 = _collect_step_7_2_1_end_plate_shear_yielding(result)
    step_7_2_2 = _collect_step_7_2_2_end_plate_shear_rupture(result)
    step_7_3_1 = _collect_step_7_3_1_end_plate_hole_tearout(result)
    step_7_3_2 = _collect_step_7_3_2_end_plate_hole_bearing(result)
    step_8_1_1 = _collect_step_8_1_1_stiffener_weld_tension_rupture(result)
    step_9_1_1 = _collect_step_9_1_1_stiffener_beam_weld_shear_rupture(result)
    step_10_1_1 = _collect_step_10_1_1_beam_shear_yielding(result)
    step_11_ctx = _collect_step_11_web_weld_tension_context(result)
    step_12_1_1 = _collect_step_12_1_1_column_flange_local_bending(result)
    content = [
        "# Memoria de Calculo",
        "",
        f"- Proyecto: `{result.project_id}`",
        f"- Caso: `{result.case_id}`",
        f"- Familia: `{result.connection_family}`",
        f"- Tipo: `{result.connection_type}`",
        f"- Estado global: `{_render_result_plain_es(result.global_status.value)}`",
        "",
    ]
    connection_family_normalized = str(result.connection_family).strip().lower()
    if connection_family_normalized == "moment_prequalified":
        content.extend(
            [
                "## Revision conexion viga a derecha de columna",
                "",
                "## Paso 1 - Limites de precalificacion",
                "",
                "Comparacion directa de valor calculado contra limite normativo (sin formato DCR).",
                "",
            ]
        )
        if notes:
            content.append(_render_step_1_notes(notes))
        if rows:
            content.append(_render_step_1_list(rows))
        else:
            content.append("No hay subchequeos de prequalification disponibles para este caso.")
    elif connection_family_normalized == "fully_restrained_moment":
        content.append(_render_fully_restrained_splice_outline(splice_rows_viga, splice_notes_viga, splice_step_2_pernos1))
    if step_2 is not None:
        content.append(_render_step_2_mpr(step_2))
    if step_3 is not None:
        content.append(_render_step_3_sh(step_3))
    if step_4 is not None:
        content.append(_render_step_4_vh(step_4))
    if step_5 is not None:
        content.append(_render_step_5_mf(step_5))
    if step_6_1 is not None or step_6_2 is not None:
        content.append(_render_step_6_bolts(step_6_1, step_6_2))
    if (
        step_7_1_1 is not None
        or step_7_2_1 is not None
        or step_7_2_2 is not None
        or step_7_3_1 is not None
        or step_7_3_2 is not None
    ):
        content.append(_render_step_7_end_plate(step_7_1_1, step_7_2_1, step_7_2_2, step_7_3_1, step_7_3_2))
    if step_8_1_1 is not None:
        content.append(_render_step_8_stiffener_weld(step_8_1_1))
    if step_9_1_1 is not None:
        content.append(_render_step_9_stiffener_beam_weld(step_9_1_1))
    if step_10_1_1 is not None:
        content.append(_render_step_10_beam_shear(step_10_1_1))
    if step_11_ctx is not None:
        content.append(_render_step_11_end_plate_beam_web_weld_tension(step_11_ctx, step_10_1_1))
    if connection_family_normalized == "moment_prequalified":
        content.append(_render_step_12_column_flange_local_bending(step_12_1_1, step_11_ctx))
    content.append("")
    return "\n".join(content)


def write_memory_markdown(result: DetailedRunResult, target_dir: str | Path) -> Path:
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "memory.md"
    rendered = render_memory_markdown(result).rstrip("\n") + "\n"
    target.write_text(rendered, encoding="utf-8")
    return target

