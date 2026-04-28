from __future__ import annotations

import math
import re
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
    if value in {"OK", "PASS", "CUMPLE"}:
        return "🟢 Cumple"
    if value in {"NO_OK", "FAIL", "ERROR", "NOT_IMPLEMENTED", "NO CUMPLE"}:
        return "🔴 No cumple"
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
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "units_trace": check.calculation_memory.units_trace,
            "equation": check.calculation_memory.equation,
        }
    return None


def _collect_step_11_web_weld_tension_context(result: DetailedRunResult) -> dict | None:
    prequal_inputs: dict = {}
    beam_left_inputs: dict = {}
    for check in result.checks:
        if isinstance(check.calculation_memory.inputs, dict):
            maybe_inputs = check.calculation_memory.inputs
            if "d_vgizq" in maybe_inputs or "tf_vgizq" in maybe_inputs:
                beam_left_inputs.update(
                    {
                        key: maybe_inputs.get(key)
                        for key in ("d_vgizq", "tf_vgizq")
                        if maybe_inputs.get(key) is not None
                    }
                )
            if ".06.3." in check.rule_id and not prequal_inputs:
                prequal_inputs = maybe_inputs
    if not prequal_inputs:
        return None
    if beam_left_inputs:
        prequal_inputs = {**prequal_inputs, **beam_left_inputs}
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
            "demand": check.demand.model_dump() if check.demand is not None else None if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_10_1_1_beam_flange_end_plate_weld_tension_rupture(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step10_1_1_beam_flange_end_plate_weld_tension_rupture" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_10_1_1_beam_shear_yielding(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step11_1_1_beam_shear_yielding" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
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
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_13_1_1_column_web_local_yielding(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        rule_id = str(check.rule_id).lower()
        clause = str(check.clause).lower()
        name = str(check.name).lower()
        if (
            ".step13_1_1_column_web_local_yielding" not in rule_id
            and "web_local_yielding" not in rule_id
            and "6.7-17" not in clause
            and "column web" not in name
        ):
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump() if check.demand is not None else None if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_14_2_1_column_web_local_crippling(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        rule_id = str(check.rule_id).lower()
        clause = str(check.clause).lower()
        name = str(check.name).lower()
        if (
            ".step14_2_1_column_web_local_crippling" not in rule_id
            and "web_local_crippling" not in rule_id
            and "6.7-19" not in clause
            and "6.7-20" not in clause
            and "6.7-21" not in clause
            and "crippling" not in name
        ):
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
        }
    return None


def _collect_step_14_2_2_column_web_local_buckling(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        rule_id = str(check.rule_id).lower()
        clause = str(check.clause).lower()
        name = str(check.name).lower()
        if (
            ".step14_2_2_column_web_local_buckling" not in rule_id
            and "web_local_buckling" not in rule_id
            and "6.7-18" not in clause
            and "buckling" not in name
        ):
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
            "notes": check.notes,
        }
    return None


def _canonical_side_mode(value: object) -> str | None:
    text = _format_text(value).strip().lower()
    if text in {"left", "left_only", "izq", "izquierda", "solo_izquierda"}:
        return "left_only"
    if text in {"right", "right_only", "der", "derecha", "solo_derecha"}:
        return "right_only"
    if text in {"both", "both_sides", "ambas", "ambos_lados", "izq_der"}:
        return "both_sides"
    return None


def _collect_active_sides(result: DetailedRunResult) -> list[str]:
    for check in result.checks:
        design_factors = check.calculation_memory.design_factors
        if not isinstance(design_factors, dict):
            continue
        mode = _canonical_side_mode(
            design_factors.get("beam_connection_sides")
            if design_factors.get("beam_connection_sides") is not None
            else design_factors.get("lados_conexion")
        )
        if mode == "left_only":
            return ["izq"]
        if mode == "right_only":
            return ["der"]
        if mode == "both_sides":
            return ["izq", "der"]

    has_izq = any(str(check.rule_id).lower().endswith("_vgizq") for check in result.checks)
    has_der = any(str(check.rule_id).lower().endswith("_vgder") for check in result.checks)
    if has_izq and has_der:
        return ["izq", "der"]
    if has_der:
        return ["der"]
    return ["izq"]


def _collect_check_by_step_and_side(
    result: DetailedRunResult,
    *,
    step_fragment: str,
    side: str,
) -> dict | None:
    side_suffix = "vgizq" if side == "izq" else "vgder"
    token = f"_{side_suffix}"
    for check in result.checks:
        rule_id = str(check.rule_id)
        if step_fragment not in rule_id:
            continue
        if not rule_id.lower().endswith(token):
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
            "source_document": check.source_document,
            "status": check.status.value,
            "demand": check.demand.model_dump() if check.demand is not None else None,
            "capacity": check.capacity.model_dump() if check.capacity is not None else None,
            "inputs": check.calculation_memory.inputs,
            "intermediates": check.calculation_memory.intermediates,
            "design_factors": check.calculation_memory.design_factors,
            "equation": check.calculation_memory.equation,
            "dcr": check.dcr,
            "notes": check.notes,
        }
    return None


def _swap_side_tokens(value: object, *, to_side: str) -> object:
    if isinstance(value, dict):
        return {
            _swap_side_tokens(key, to_side=to_side): _swap_side_tokens(item, to_side=to_side)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_swap_side_tokens(item, to_side=to_side) for item in value]
    if isinstance(value, str):
        text = value

        def _swap_pair(raw: str, left: str, right: str, token: str) -> str:
            return raw.replace(left, token).replace(right, left).replace(token, right)

        # Use bidirectional swap to avoid key collisions when payloads contain both sides.
        text = _swap_pair(text, "vgizq", "vgder", "__TMP_VG_SIDE__")
        text = _swap_pair(text, "_izq", "_der", "__TMP_SUFFIX_SIDE__")
        text = _swap_pair(text, " izquierda", " derecha", "__TMP_ADJ_SIDE__")
        return text
    return value


def _prepare_payload_for_left_renderer(payload: dict | None, *, side: str) -> dict | None:
    if payload is None or side == "izq":
        return payload
    converted = _swap_side_tokens(payload, to_side="izq")
    return converted if isinstance(converted, dict) else payload


def _render_block_for_side(renderer: object, *payloads: object, side: str) -> str:
    prepared_args: list[object] = []
    for payload in payloads:
        if isinstance(payload, dict) or payload is None:
            prepared_args.append(_prepare_payload_for_left_renderer(payload, side=side))
        else:
            prepared_args.append(payload)
    if all(arg is None for arg in prepared_args):
        return ""
    text = renderer(*prepared_args)
    if side == "der":
        converted = _swap_side_tokens(text, to_side="der")
        return str(converted)
    return text


def _strip_first_h2(block: str) -> str:
    lines = block.splitlines()
    if lines and lines[0].startswith("## "):
        lines = lines[1:]
        if lines and lines[0].strip() == "":
            lines = lines[1:]
    return "\n".join(lines).strip()


def _tag_side_subheadings(block: str, *, side: str) -> str:
    side_tag = "vg_izq" if side == "izq" else "vg_der"
    tagged_lines: list[str] = []
    for line in block.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("### ") or stripped.startswith("#### "):
            if f"({side_tag})" not in stripped:
                line = f"{line} ({side_tag})"
        tagged_lines.append(line)
    return "\n".join(tagged_lines)


def _normalize_markdown_spacing(text: str) -> str:
    raw_lines = text.splitlines()
    lines: list[str] = []

    def _is_heading(value: str) -> bool:
        stripped = value.strip()
        return stripped.startswith("#")

    def _is_list_item(value: str) -> bool:
        return value.strip().startswith("- ")

    for raw in raw_lines:
        current = raw.rstrip()
        if _is_heading(current):
            while lines and lines[-1] == "":
                lines.pop()
            if lines:
                lines.append("")
            lines.append(current)
            lines.append("")
            continue

        if _is_list_item(current):
            if lines and lines[-1] != "" and not _is_list_item(lines[-1]):
                lines.append("")
            lines.append(current)
            continue

        if current == "":
            if lines and lines[-1] != "":
                lines.append("")
            continue

        if lines and _is_list_item(lines[-1]):
            lines.append("")
        lines.append(current)

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def _replace_first_step_heading_number(block: str, *, step_number: int) -> str:
    lines = block.splitlines()
    for idx, line in enumerate(lines):
        match = re.match(r"^(##\s+Paso)\s+\d+\s+-(.*)$", line)
        if match:
            lines[idx] = f"{match.group(1)} {step_number} -{match.group(2)}"
            break
    return "\n".join(lines)


def _align_nested_heading_numbers_with_step(block: str, *, step_number: int) -> str:
    lines = block.splitlines()
    aligned: list[str] = []
    for line in lines:
        match = re.match(r"^(\s*#{3,4}\s+)(\d+)((?:\.\d+)*)(\.?)(\s+)(.*)$", line)
        if match:
            aligned.append(
                f"{match.group(1)}{step_number}{match.group(3)}{match.group(4)}{match.group(5)}{match.group(6)}"
            )
            continue
        aligned.append(line)
    return "\n".join(aligned)


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
        if note_id == "section_6_7.beam_flange_to_end_plate_weld_note":
            continue
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
    clause_text = _render_clause_text(step_2.get("clause"), step_2.get("source_document"), step_2.get("rule_id"))
    fy = _format_quantity(inputs.get("beam_fy"))
    ry = _format_text(inputs.get("ry"))
    ze_der = _format_quantity(inputs.get("ze_vgder"))
    ze_izq = _format_quantity(inputs.get("ze_vgizq"))
    dd_der = _format_text(inter.get("member_ductility_demand_beam_der") or inputs.get("member_ductility_demand_vgder"))
    dd_izq = _format_text(inter.get("member_ductility_demand_beam_izq") or inputs.get("member_ductility_demand_vgizq"))
    cpr_der = _format_text(inter.get("cpr_der"))
    cpr_izq = _format_text(inter.get("cpr_izq"))
    mpr_der = _format_scalar_with_unit(inter.get("mpr_der"), "kN-mm")
    mpr_izq = _format_scalar_with_unit(inter.get("mpr_izq"), "kN-mm")
    lines = [
        "## Paso 2 - Momento probable maximo en rotula plastica (Mpr)",
        "",
        "Calculo de momento probable por lado usando `Mpr = Cpr * Ry * Fy * Ze` (Ze = Zx del catalogo).",
        "",
        "### 2.1 Calculo de Mpr para viga izquierda",
        "",
        f"- Clausula: `{clause_text}`",
        "- Ecuacion: `Mpr_vgizq = Cpr_vgizq * Ry * Fy * Ze_vgizq`",
        f"- Fy_vgizq: `{fy}`",
        f"- Ry: `{ry}`",
        f"- Ze_vgizq (catalogo): `{ze_izq}`",
        f"- Demanda de ductilidad_vgizq: `{dd_izq}`",
        f"- Cpr_vgizq: `{cpr_izq}`",
        f"- Mpr_vgizq: `{mpr_izq}`",
        "",
        "### 2.2 Calculo de Mpr para viga derecha",
        "",
        f"- Clausula: `{clause_text}`",
        "- Ecuacion: `Mpr_vgder = Cpr_vgder * Ry * Fy * Ze_vgder`",
        f"- Fy_vgder: `{fy}`",
        f"- Ry: `{ry}`",
        f"- Ze_vgder (catalogo): `{ze_der}`",
        f"- Demanda de ductilidad_vgder: `{dd_der}`",
        f"- Cpr_vgder: `{cpr_der}`",
        f"- Mpr_vgder: `{mpr_der}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_3_sh(step_3: dict) -> str:
    inputs = step_3.get("inputs", {})
    clause_text = _render_clause_text(step_3.get("clause"), step_3.get("source_document"), step_3.get("rule_id"))
    ctype = _format_text(inputs.get("connection_type"))
    sh_izq = _format_scalar_with_unit(step_3.get("intermediates", {}).get("sh_izq"), "mm")
    sh_der = _format_scalar_with_unit(step_3.get("intermediates", {}).get("sh_der"), "mm")
    lines = [
        "## Paso 3 - Distancia de rotula plastica desde la cara de la columna (Sh)",
        "",
        "### 3.1 Calculo de Sh para viga izquierda",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Tipo de conexion: `{ctype}`",
        "- Ecuacion: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`",
        f"- d_vgizq: `{_format_quantity(inputs.get('d_vgizq'))}`",
        f"- bf_vgizq: `{_format_quantity(inputs.get('bf_vgizq'))}`",
        f"- Sh_vgizq: `{sh_izq}`",
        "",
        "### 3.2 Calculo de Sh para viga derecha",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Tipo de conexion: `{ctype}`",
        "- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`",
        f"- d_vgder: `{_format_quantity(inputs.get('d_vgder'))}`",
        f"- bf_vgder: `{_format_quantity(inputs.get('bf_vgder'))}`",
        f"- Sh_vgder: `{sh_der}`",
        "",
        f"- Lado gobernante Sh: `{_format_text(inputs.get('governing_side_sh'))}`",
        f"- Sh adoptado (gobernante): `{_format_quantity(step_3.get('demand'))}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_4_vh(step_4: dict) -> str:
    inputs = step_4.get("inputs", {})
    inter = step_4.get("intermediates", {})
    beam_connection_sides = _format_text(inputs.get("beam_connection_sides"))
    sides = ["izq", "der"] if beam_connection_sides == "both_sides" else ["der"]
    lines = [
        "## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)",
        "",
        "Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.",
        "",
    ]
    clause_text = _render_clause_text(step_4.get("clause"), step_4.get("source_document"), step_4.get("rule_id"))
    for side in sides:
        side_suffix = f"vg{side}"
        subtitle = "### 4.1 Calculo de cortante probable para viga izquierda" if side == "izq" else "### 4.2 Calculo de cortante probable para viga derecha"
        lines.extend(
            [
                subtitle,
                "",
                f"- Clausula: `{clause_text}`",
                f"- Ecuacion: `Vh_{side_suffix}_max = 2*Mpr/Llb_{side_suffix} + Vg_{side_suffix}; Vh_{side_suffix}_min = 2*Mpr/Llb_{side_suffix} - Vg_{side_suffix}`",
                f"- Mpr_{side_suffix}: `{_format_scalar_with_unit(inter.get(f'mpr_{side}'), 'kN-mm')}`",
                f"- Llb_{side_suffix}: `{_format_quantity(inputs.get(f'lh_{side}'))}`",
                f"- Vg_{side_suffix}: `{_format_quantity(inputs.get(f'vgravity_between_hinges_{side}'))}`",
                f"- Vh_{side_suffix}_max: `{_format_scalar_with_unit(inter.get(f'vh_{side}max'), 'kN')}`",
                f"- Vh_{side_suffix}_min: `{_format_scalar_with_unit(inter.get(f'vh_{side}min'), 'kN')}`",
                f"- Vhmax adoptado (gobernante): `{_format_scalar_with_unit(inter.get(f'vh_{side}max'), 'kN')}`",
                "",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def _render_step_5_mf(step_5: dict) -> str:
    inputs = step_5.get("inputs", {})
    inter = step_5.get("intermediates", {})
    beam_connection_sides = _format_text(inputs.get("beam_connection_sides"))
    if beam_connection_sides == "both_sides":
        sides = ["izq", "der"]
    else:
        sides = ["der"]
    clause_text = _render_clause_text(step_5.get("clause"), step_5.get("source_document"), step_5.get("rule_id"))
    lines = [
        "## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)",
        "",
        "Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.",
        "",
    ]
    for side in sides:
        side_suffix = f"vg{side}"
        subtitle = "### 5.1 Calculo de momento probable en cara de columna para viga izquierda" if side == "izq" else "### 5.2 Calculo de momento probable en cara de columna para viga derecha"
        lines.extend(
            [
                subtitle,
                "",
                f"- Clausula: `{clause_text}`",
                (
                    f"- Ecuacion: `Mf_{side_suffix}_max = Mpr_{side_suffix} + Vh_{side_suffix}_max*Sh_{side_suffix}; "
                    f"Mf_{side_suffix}_min = Mpr_{side_suffix} + Vh_{side_suffix}_min*Sh_{side_suffix}`"
                ),
                f"- Mpr_{side_suffix}: `{_format_scalar_with_unit(inter.get(f'mpr_{side}'), 'kN-mm')}`",
                f"- Sh_{side_suffix}: `{_format_scalar_with_unit(inter.get(f'sh_{side}'), 'mm')}`",
                f"- Mf_{side_suffix}_max: `{_format_scalar_with_unit(inter.get(f'mf_{side}max'), 'kN-mm')}`",
                f"- Mf_{side_suffix}_min: `{_format_scalar_with_unit(inter.get(f'mf_{side}min'), 'kN-mm')}`",
                "",
            ]
        )
    return "\n".join(lines)


def _render_step_6_bolts(step_6_1: dict | None, step_6_2: dict | None) -> str:
    lines = [
        "## Paso 6 - Revision De Resistencia Pernos (vg_izq)",
        "",
    ]
    if step_6_1 is not None:
        inputs = step_6_1.get("inputs", {})
        inter = step_6_1.get("intermediates", {})
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
                f"- Mf_vgizq_critico: `{_format_quantity(inputs.get('mf_vgizq_critico'))}`",
                f"- h1_pe_vgizq: `{_format_quantity(inputs.get('h1_pe_vgizq'))}`",
                f"- h2_pe_vgizq: `{_format_quantity(inputs.get('h2_pe_vgizq'))}`",
                f"- h3_pe_vgizq: `{_format_quantity(inputs.get('h3_pe_vgizq'))}`",
                f"- h4_pe_vgizq: `{_format_quantity(inputs.get('h4_pe_vgizq'))}`",
                f"- A_b_vgizq: `{_format_quantity(inter.get('a_b_vgizq'))}`",
                f"- Fnt_b_vgizq: `{_format_quantity(inputs.get('fnt_b_vgizq'))}`",
                f"- Ru_b_p+_vgizq: `{_format_quantity(step_6_1.get('demand'))}`",
                f"- phi*Rn_b_p+_vgizq: `{_format_quantity(step_6_1.get('capacity'))}`",
                f"- DCR_b_p+_vgizq: `{_format_text(step_6_1.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_6_1.get('status'))}`",
                "",
            ]
        )
    if step_6_2 is not None:
        inputs = step_6_2.get("inputs", {})
        inter = step_6_2.get("intermediates", {})
        design_factors = step_6_2.get("design_factors", {})
        lines.extend(
            [
                "### 6.2 Revision de capacidad a cortante",
                "",
                "#### 6.2.1 ELR #2: Rotura por cortante en el perno",
                "",
                f"- Clausula: `{_render_clause_text(step_6_2.get('clause'), step_6_2.get('source_document'), step_6_2.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_6_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vh_vgizq_critico: `{_format_quantity(inputs.get('vh_vgizq_critico'))}`",
                f"- n_b_vgizq: `{_format_text(inputs.get('n_b_vgizq'))}`",
                f"- A_b_vgizq: `{_format_quantity(inter.get('a_b_vgizq'))}`",
                f"- Fnt_b_vgizq: `{_format_quantity(inputs.get('fnt_b_vgizq'))}`",
                f"- Ru_b_v2_vgizq: `{_format_quantity(step_6_2.get('demand'))}`",
                f"- phi*Rn_b_v2_vgizq: `{_format_quantity(step_6_2.get('capacity'))}`",
                f"- DCR_b_v2_vgizq: `{_format_text(step_6_2.get('dcr'))}`",
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
        "## Paso 7 - Revision de resistencia platina extremo (vg_izq)",
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
                "#### 7.1.1. ELR #1: Fluencia",
                "",
                f"- Clausula: `{_render_clause_text(step_7_1_1.get('clause'), step_7_1_1.get('source_document'), step_7_1_1.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_1_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Mf_vgizq_critico: `{_format_quantity(inputs.get('mf_vgizq_critico'))}`",
                f"- tpe_vgizq: `{_format_quantity(inputs.get('tpe_vgizq'))}`",
                f"- Fyp_pe_vgizq: `{_format_quantity(inputs.get('fyp_pe_vgizq'))}`",
                f"- Yp_pe_vgizq: `{_format_quantity(inputs.get('yp_pe_vgizq'))}`",
                f"- Tabla Yp aplicada: `{_format_text(inputs.get('yp_pe_vgizq_table')).replace('Table', 'Tabla')}`",
                f"- Caso Yp: `{_format_text(inputs.get('yp_pe_vgizq_case'))}`",
                *(
                    ["- Advertencia: `Yp_pe_vgizq esta hardcodeado`"]
                    if bool(inputs.get("yp_pe_vgizq_is_hardcoded"))
                    else []
                ),
                f"- s_pe_vgizq: `{_format_quantity(inter.get('s'))}`",
                f"- pfi_pe_vgizq_entrada: `{_format_quantity(inter.get('pfi_input'))}`",
                f"- pfi_pe_vgizq_efectivo: `{_format_quantity(inter.get('pfi_effective'))}`",
                f"- Ru_pe_m3_vgizq: `{_format_quantity(step_7_1_1.get('demand'))}`",
                f"- phi*Rn_pe_m3_vgizq: `{_format_quantity(step_7_1_1.get('capacity'))}`",
                f"- DCR_pe_m3_vgizq: `{_format_text(step_7_1_1.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_1_1.get('status'))}`",
                "",
            ]
        )
    if step_7_2_1 is not None:
        inputs = step_7_2_1.get("inputs", {})
        inter = step_7_2_1.get("intermediates", {})
        design_factors = step_7_2_1.get("design_factors", {})
        lines.extend(
            [
                "### 7.2. Revision de capacidad a cortante perpendicular al plano de la platina",
                "",
                "#### 7.2.1. ELR #1: Fluencia por cortante",
                "",
                f"- Clausula: `{_render_clause_text(step_7_2_1.get('clause'), step_7_2_1.get('source_document'), step_7_2_1.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_2_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- d_vgizq: `{_format_quantity(inputs.get('d_vgizq'))}`",
                f"- tf_vgizq: `{_format_quantity(inputs.get('tf_vgizq'))}`",
                f"- z_vgizq = d_vgizq - tf_vgizq: `{_format_scalar_with_unit(inter.get('z_vgizq'), 'mm')}`",
                f"- bpe_vgizq: `{_format_quantity(inputs.get('bpe_vgizq'))}`",
                f"- tpe_vgizq: `{_format_quantity(inputs.get('tpe_vgizq'))}`",
                f"- Fyp_pe_vgizq: `{_format_quantity(inputs.get('fyp_pe_vgizq'))}`",
                f"- Ru_pe_m3_vgizq: `{_format_quantity(inputs.get('ru_pe_m3_vgizq'))}`",
                f"- Rn_pe_v1_vgizq: `{_format_quantity(step_7_2_1.get('demand'))}`",
                f"- phi*Rn_pe_v1_vgizq: `{_format_quantity(step_7_2_1.get('capacity'))}`",
                f"- DCR_pe_v1_vgizq: `{_format_text(step_7_2_1.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_2_1.get('status'))}`",
                "",
            ]
        )
    if step_7_2_2 is not None:
        inputs = step_7_2_2.get("inputs", {})
        inter = step_7_2_2.get("intermediates", {})
        design_factors = step_7_2_2.get("design_factors", {})
        lines.extend(
            [
                "#### 7.2.2. ELR #2: Rotura por cortante",
                "",
                f"- Clausula: `{_render_clause_text(step_7_2_2.get('clause'), step_7_2_2.get('source_document'), step_7_2_2.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_2_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Ru_pe_m3_vgizq: `{_format_quantity(inputs.get('ru_pe_m3_vgizq'))}`",
                f"- d_vgizq: `{_format_quantity(inputs.get('d_vgizq'))}`",
                f"- tf_vgizq: `{_format_quantity(inputs.get('tf_vgizq'))}`",
                f"- z_vgizq = d_vgizq - tf_vgizq: `{_format_scalar_with_unit(inter.get('z_vgizq'), 'mm')}`",
                f"- bpe_vgizq: `{_format_quantity(inputs.get('bpe_vgizq'))}`",
                f"- tpe_vgizq: `{_format_quantity(inputs.get('tpe_vgizq'))}`",
                f"- Fup_pe_vgizq: `{_format_quantity(inputs.get('fup_pe_vgizq'))}`",
                f"- dh_pe_vgizq: `{_format_quantity(inputs.get('dh_pe_vgizq'))}`",
                f"- Rn_pe_v2_vgizq: `{_format_quantity(step_7_2_2.get('demand'))}`",
                f"- phi*Rn_pe_v2_vgizq: `{_format_quantity(step_7_2_2.get('capacity'))}`",
                f"- DCR_pe_v2_vgizq: `{_format_text(step_7_2_2.get('dcr'))}`",
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
        inter = step_7_3_1.get("intermediates", {})
        design_factors = step_7_3_1.get("design_factors", {})
        lines.extend(
            [
                "#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno",
                "",
                f"- Clausula: `{_render_clause_text(step_7_3_1.get('clause'), step_7_3_1.get('source_document'), step_7_3_1.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_3_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vh_vgizq_critico: `{_format_quantity(inputs.get('vh_vgizq_critico'))}`",
                f"- n_b_vgizq: `{_format_text(inputs.get('n_b_vgizq'))}`",
                f"- pb_pe_vgizq: `{_format_quantity(inputs.get('pb_pe_vgizq'))}`",
                f"- pfo_pe_vgizq: `{_format_quantity(inputs.get('pfo_pe_vgizq'))}`",
                f"- pfi_pe_vgizq: `{_format_quantity(inputs.get('pfi_pe_vgizq'))}`",
                f"- tf_vgizq: `{_format_quantity(inputs.get('tf_vgizq'))}`",
                f"- dh_pe_vgizq: `{_format_quantity(inputs.get('dh_pe_vgizq'))}`",
                f"- lc_pe_vgizq: `{_format_quantity(inputs.get('lc_pe_vgizq'))}`",
                f"- tpe_vgizq: `{_format_quantity(inputs.get('tpe_vgizq'))}`",
                f"- Fup_pe_vgizq: `{_format_quantity(inputs.get('fup_pe_vgizq'))}`",
                f"- Ru_pe_v2_vgizq: `{_format_quantity(step_7_3_1.get('demand'))}`",
                f"- phi*Rn_pe_v2_vgizq: `{_format_quantity(step_7_3_1.get('capacity'))}`",
                f"- DCR_pe_v2_vgizq: `{_format_text(step_7_3_1.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_3_1.get('status'))}`",
                "",
            ]
        )
    if step_7_3_2 is not None:
        inputs = step_7_3_2.get("inputs", {})
        design_factors = step_7_3_2.get("design_factors", {})
        lines.extend(
            [
                "#### 7.3.2. ELR #2: Aplastamiento en la perforacion del perno",
                "",
                f"- Clausula: `{_render_clause_text(step_7_3_2.get('clause'), step_7_3_2.get('source_document'), step_7_3_2.get('rule_id'))}`",
                f"- Ecuacion: `{_format_text(step_7_3_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vh_vgizq_critico: `{_format_quantity(inputs.get('vh_vgizq_critico'))}`",
                f"- n_b_vgizq: `{_format_text(inputs.get('n_b_vgizq'))}`",
                f"- tpe_vgizq: `{_format_quantity(inputs.get('tpe_vgizq'))}`",
                f"- Fup_pe_vgizq: `{_format_quantity(inputs.get('fup_pe_vgizq'))}`",
                f"- d_b_vgizq: `{_format_quantity(inputs.get('d_b_vgizq'))}`",
                f"- Ru_pe_v2_vgizq: `{_format_quantity(step_7_3_2.get('demand'))}`",
                f"- phi*Rn_pe_v2_vgizq: `{_format_quantity(step_7_3_2.get('capacity'))}`",
                f"- DCR_pe_v2_vgizq: `{_format_text(step_7_3_2.get('dcr'))}`",
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
    weld_type = _format_text(inputs.get("tipo_w1_vgizq"))
    if weld_type == "n/a":
        weld_type = _format_text(inputs.get("weld_type_normalized"))
    clause_text = _render_clause_text(step_8_1_1.get("clause"), step_8_1_1.get("source_document"), step_8_1_1.get("rule_id"))
    clause_text = clause_text.replace("Paso 8.1.1 + AISC", "+ AISC")
    clause_text = clause_text.replace("Paso 8.1.1 + ", "")
    lines = [
        "## Paso 8 - Revision de Resistencia soldadura #1 (platina extremo vg_izq - rigidizador vg_izq)",
        "",
        "### 8.1. Revision de capacidad a traccion",
        "",
        "#### 8.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Ecuacion: `{_format_text(step_8_1_1.get('equation'))}`",
        f"- tipo_w1_vgizq: `{weld_type}`",
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
            f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
            "- l_w1_vgizq (longitud soldadura calculada): `l_w1_vgizq = h_pest_vgizq - c_pest_vgizq - 2*w_w1_vgizq`",
            f"- Fys_pest_vgizq: `{_format_quantity(inputs.get('fys_pest_vgizq'))}`",
            f"- t_pest_vgizq: `{_format_quantity(inputs.get('t_pest_vgizq'))}`",
            f"- h_pest_vgizq: `{_format_quantity(inputs.get('h_pest_vgizq'))}`",
            f"- c_pest_vgizq: `{_format_quantity(inputs.get('c_pest_vgizq'))}`",
            f"- l_w1_vgizq: `{_format_quantity(inputs.get('l_w1_vgizq'))}`",
            f"- Fexx_w1_vgizq: `{_format_quantity(inputs.get('fexx_w1_vgizq') or inputs.get('fexx'))}`",
            f"- w_w1_vgizq: `{_format_quantity(inputs.get('w_w1_vgizq') or inputs.get('wst'))}`",
            f"- nl_w1_vgizq: `{_format_text(inputs.get('nl_w1_vgizq') if inputs.get('nl_w1_vgizq') is not None else inputs.get('nl'))}`",
            f"- kds_w1_vgizq: `{_format_text(inputs.get('kds_w1_vgizq'))}`",
            f"- Ru_w1_p+_vgizq: `{_format_quantity(step_8_1_1.get('demand'))}`",
            f"- phi*Rn_w1_p+_vgizq: `{_format_quantity(step_8_1_1.get('capacity'))}`",
            f"- DCR_w1_p+_vgizq: `{_format_text(step_8_1_1.get('dcr'))}`",
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
    weld_type = _format_text(inputs.get("tipo_w2_vgizq"))
    if weld_type == "n/a":
        weld_type = _format_text(inputs.get("weld_type_normalized"))
    clause_text = _render_clause_text(step_9_1_1.get("clause"), step_9_1_1.get("source_document"), step_9_1_1.get("rule_id"))
    clause_text = clause_text.replace("Paso 9.1.1 + AISC", "+ AISC")
    clause_text = clause_text.replace("Paso 9.1.1 + ", "")
    lines = [
        "## Paso 9 - Revision de Resistencia soldadura #2 (viga vg_izq - rigidizador vg_izq)",
        "",
        "### 9.1. Revision de capacidad a cortante",
        "",
        "#### 9.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Ecuacion: `{_format_text(step_9_1_1.get('equation'))}`",
        f"- tipo_w2_vgizq: `{weld_type}`",
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
            f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
            "- l_w2_vgizq (longitud soldadura calculada): `l_w2_vgizq = L_pest_vgizq - c_pest_vgizq - 2*w_w2_vgizq`",
            f"- Fys_pest_vgizq: `{_format_quantity(inputs.get('fys_pest_vgizq') or inputs.get('fys'))}`",
            f"- t_pest_vgizq: `{_format_quantity(inputs.get('t_pest_vgizq') or inputs.get('ts'))}`",
            f"- h_pest_vgizq: `{_format_quantity(inputs.get('h_pest_vgizq') or inputs.get('hst'))}`",
            f"- L_pest_vgizq: `{_format_quantity(inputs.get('l_pest_vgizq') or inputs.get('lst'))}`",
            f"- c_pest_vgizq: `{_format_quantity(inputs.get('c_pest_vgizq') or inputs.get('clip_st'))}`",
            f"- l_w2_vgizq: `{_format_quantity(inputs.get('l_w2_vgizq') or inputs.get('lst_w2'))}`",
            f"- Fexx_w2_vgizq: `{_format_quantity(inputs.get('fexx_w2_vgizq') or inputs.get('fexx'))}`",
            f"- w_w2_vgizq: `{_format_quantity(inputs.get('w_w2_vgizq') or inputs.get('wst2'))}`",
            f"- nl_w2_vgizq: `{_format_text(inputs.get('nl_w2_vgizq') if inputs.get('nl_w2_vgizq') is not None else inputs.get('nl_w2'))}`",
            f"- kds_w2_vgizq: `{_format_text(inputs.get('kds_w2_vgizq'))}`",
            f"- Ru_w2_v2_vgizq: `{_format_quantity(step_9_1_1.get('demand'))}`",
            f"- phi*Rn_w2_v2_vgizq: `{_format_quantity(step_9_1_1.get('capacity'))}`",
            f"- DCR_w2_v2_vgizq: `{_format_text(step_9_1_1.get('dcr'))}`",
            f"- Resultado: `{_render_result_plain_es(step_9_1_1.get('status'))}`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_step_10_beam_flange_end_plate_weld(step_10_1_1: dict | None) -> str:
    if step_10_1_1 is None:
        return ""
    inputs = step_10_1_1.get("inputs", {})
    design_factors = step_10_1_1.get("design_factors", {})
    weld_type = _format_text(inputs.get("tipo_w4_vgizq"))
    clause_text = _render_clause_text(step_10_1_1.get("clause"), step_10_1_1.get("source_document"), step_10_1_1.get("rule_id"))
    clause_text = clause_text.replace("Paso 10.1.1 + AISC", "+ AISC")
    clause_text = clause_text.replace("Paso 10.1.1 + ", "")
    clause_text = clause_text.replace("Paso 11.1.1 + AISC", "+ AISC")
    clause_text = clause_text.replace("Paso 11.1.1 + ", "")
    lines = [
        "## Paso 10 - Revision de Resistencia soldadura #4 (ala vg_izq - platina extremo vg_izq)",
        "",
        "### 10.1. Revision de capacidad a traccion",
        "",
        "#### 10.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Ecuacion: `{_format_text(step_10_1_1.get('equation'))}`",
        f"- tipo_w4_vgizq: `{weld_type}`",
    ]
    if weld_type == "cjp":
        lines.extend(
            [
                "- CJP: `Cumple`",
                f"- Resultado: `{_render_result_plain_es(step_10_1_1.get('status'))}`",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
            "- l_w4_vgizq (longitud soldadura calculada): `l_w4_vgizq = bf_vgizq`",
            f"- Mf_vgizq_critico: `{_format_quantity(inputs.get('mf_vgizq_critico'))}`",
            f"- d_vgizq: `{_format_quantity(inputs.get('d_vgizq'))}`",
            f"- tf_vgizq: `{_format_quantity(inputs.get('tf_vgizq'))}`",
            f"- bf_vgizq: `{_format_quantity(inputs.get('bf_vgizq'))}`",
            f"- l_w4_vgizq: `{_format_quantity(inputs.get('l_w4_vgizq'))}`",
            f"- Fexx_w4_vgizq: `{_format_quantity(inputs.get('Fexx_w4_vgizq'))}`",
            f"- t_w4_vgizq: `{_format_quantity(inputs.get('t_w4_vgizq'))}`",
            f"- nl_w4_vgizq: `{_format_text(inputs.get('nl_w4_vgizq'))}`",
            f"- kds_w4_vgizq: `{_format_text(inputs.get('kds_w4_vgizq'))}`",
            f"- t_w4_1_vgizq: `{_format_quantity(inputs.get('t_w4_1_vgizq'))}`",
            f"- Ru_w4_p+_vgizq: `{_format_quantity(step_10_1_1.get('demand'))}`",
            f"- phi*Rn_w4_p+_vgizq: `{_format_quantity(step_10_1_1.get('capacity'))}`",
            f"- DCR_w4_p+_vgizq: `{_format_text(step_10_1_1.get('dcr'))}`",
            f"- Resultado: `{_render_result_plain_es(step_10_1_1.get('status'))}`",
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
    clause_text = _render_clause_text(step_10_1_1.get("clause"), step_10_1_1.get("source_document"), step_10_1_1.get("rule_id"))
    clause_text = clause_text.replace("Paso 10.1.1 + AISC", "+ AISC")
    clause_text = clause_text.replace("Paso 10.1.1 + ", "")
    lines = [
        "## Paso 11 - Revision de resistencia de la viga (vg_izq)",
        "",
        "### 11.1. Revision de capacidad a cortante",
        "",
        "#### 11.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1)",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Ecuacion: `{_format_text(step_10_1_1.get('equation'))}`",
        f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
        f"- Vh_vgizq_max: `{_format_quantity(inputs.get('Vh_vgizq_max'))}`",
        f"- Fy_vgizq: `{_format_quantity(inputs.get('Fy_vgizq'))}`",
        f"- tw_vgizq: `{_format_quantity(inputs.get('tw_vgizq'))}`",
        f"- d_vgizq: `{_format_quantity(inputs.get('d_vgizq'))}`",
        f"- kdes_vgizq: `{_format_quantity(inputs.get('kdes_vgizq'))}`",
        f"- E_vgizq: `{_format_quantity(inputs.get('E_vgizq'))}`",
        f"- Cv1: `{_format_text(inputs.get('cv1'))}`",
        f"- kv: `{_format_text(inter.get('kv'))}`",
        f"- h_vgizq/tw_vgizq: `{_format_text(inter.get('h_over_tw'))}`",
        f"- h_vgizq: `{_format_scalar_with_unit(inter.get('h_clear'), 'mm')}`",
        f"- Ru_v2_vgizq: `{_format_quantity(step_10_1_1.get('demand'))}`",
        f"- phi*Rn_v2_vgizq: `{_format_quantity(step_10_1_1.get('capacity'))}`",
        f"- DCR_v2_vgizq: `{_format_text(step_10_1_1.get('dcr'))}`",
        f"- Resultado: `{_render_result_plain_es(step_10_1_1.get('status'))}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_11_end_plate_beam_web_weld_tension(step_11_ctx: dict | None, step_10_1_1: dict | None) -> str:
    if step_11_ctx is None:
        return ""
    step_11_inputs = step_11_ctx.get("inputs", {})
    step_10_inputs = step_10_1_1.get("inputs", {}) if step_10_1_1 is not None else {}

    def _pick(mapping: dict, *keys: str):
        for key in keys:
            if key in mapping and mapping.get(key) is not None:
                return mapping.get(key)
        return None

    weld_type_raw = _pick(step_11_inputs, "tipo_w3_vgizq", "end_plate_beam_web_weld_type")
    weld_thickness_twe = _pick(step_11_inputs, "t_w3_vgizq", "end_plate_beam_web_weld_thickness_twe")
    weld_type = _normalize_weld_type_step11(weld_type_raw)
    pfi_q = _as_quantity(_pick(step_11_inputs, "pfi_pe_vgizq", "edge_pfi"))
    pb_q = _as_quantity(_pick(step_11_inputs, "pb_pe_vgizq", "pitch_pb"))
    twe_q = _as_quantity(weld_thickness_twe)
    fybm_q = _as_quantity(_pick(step_10_inputs, "Fy_vgizq", "fybm"))
    tw_bm_q = _as_quantity(_pick(step_10_inputs, "tw_vgizq", "tw_bm"))
    fexx_q = _as_quantity(_pick(step_11_inputs, "Fexx_w3_vgizq", "weld_fexx"))
    nl_raw = _pick(step_11_inputs, "nl_w3_vgizq", "end_plate_beam_web_weld_lines_nl")
    kds_w3_vgizq = _pick(step_11_inputs, "kds_w3_vgizq")
    unit_system = _infer_unit_system_from_quantity(_pick(step_11_inputs, "pfi_pe_vgizq", "edge_pfi"))
    if unit_system is None:
        unit_system = _infer_unit_system_from_quantity(_pick(step_10_inputs, "tw_vgizq", "tw_bm"))
    try:
        nl = int(nl_raw) if nl_raw is not None else None
    except (TypeError, ValueError):
        nl = None
    if nl is not None and nl < 1:
        nl = None
    try:
        kds_factor = float(kds_w3_vgizq) if kds_w3_vgizq is not None else None
    except (TypeError, ValueError):
        kds_factor = None
    phi = 0.75

    hwef_w3_vgizq_q: Quantity | None = None
    ru_w3_p_pos_vgizq_q: Quantity | None = None
    phi_pn_q: Quantity | None = None
    dcr_w3_p_pos_vgizq = None
    if unit_system is not None and pfi_q is not None and pb_q is not None:
        hwef_w3_vgizq_q = compute_effective_web_weld_length(
            pfi=pfi_q,
            pb=pb_q,
            unit_system=unit_system,
        )["hwef"]
    if unit_system is not None and hwef_w3_vgizq_q is not None and fybm_q is not None and tw_bm_q is not None:
        ru_w3_p_pos_vgizq_q = compute_plate_tension_demand_from_yielding(
            fy=fybm_q,
            thickness=tw_bm_q,
            effective_length=hwef_w3_vgizq_q,
            unit_system=unit_system,
        )["pu"]
    if (
        unit_system is not None
        and hwef_w3_vgizq_q is not None
        and fexx_q is not None
        and twe_q is not None
        and nl is not None
    ):
        phi_pn_q = WeldFillet(
            fexx=fexx_q,
            weld_size=twe_q,
            weld_length=hwef_w3_vgizq_q,
            weld_lines=nl,
            unit_system=unit_system,
            phi=phi,
        ).design_strength()["phi_rn"]
        if kds_factor is not None:
            phi_pn_q = Quantity(value=phi_pn_q.value * kds_factor, unit=phi_pn_q.unit)
    if ru_w3_p_pos_vgizq_q is not None and phi_pn_q is not None and phi_pn_q.value > 0.0:
        dcr_w3_p_pos_vgizq = compute_dcr(demand=ru_w3_p_pos_vgizq_q, capacity=phi_pn_q)["dcr"]

    hwef_text = _format_quantity(hwef_w3_vgizq_q.model_dump()) if hwef_w3_vgizq_q is not None else "n/a"
    ru_text = _format_quantity(ru_w3_p_pos_vgizq_q.model_dump()) if ru_w3_p_pos_vgizq_q is not None else "n/a"
    phi_rn_text = _format_quantity(phi_pn_q.model_dump()) if phi_pn_q is not None else "n/a"
    dcr_text = _format_decimal(dcr_w3_p_pos_vgizq) if dcr_w3_p_pos_vgizq is not None else "n/a"
    twe_text = _format_quantity(weld_thickness_twe)
    fexx_text = _format_quantity(_pick(step_11_inputs, "Fexx_w3_vgizq", "weld_fexx"))
    fy_text = _format_quantity(_pick(step_10_inputs, "Fy_vgizq", "fybm"))
    tw_text = _format_quantity(_pick(step_10_inputs, "tw_vgizq", "tw_bm"))
    pfi_text = _format_quantity(_pick(step_11_inputs, "pfi_pe_vgizq", "edge_pfi"))
    pb_text = _format_quantity(_pick(step_11_inputs, "pb_pe_vgizq", "pitch_pb"))

    if weld_type == "cjp":
        result_line = "Cumple"
        ru_text = "n/a (CJP)"
        phi_rn_text = "n/a (CJP)"
        dcr_text = "n/a (CJP)"
    elif weld_type == "fillet" and dcr_w3_p_pos_vgizq is not None:
        result_line = "Cumple" if dcr_w3_p_pos_vgizq <= 1.0 else "No cumple"
    else:
        result_line = "No cumple"

    lines = [
        "## Paso 12 - Revision de Resistencia soldadura #3 (viga alma vg_izq - platina extremo vg_izq)",
        "",
        "### 12.1 Revision capacidad a traccion",
        "",
        "#### 12.1.1 ELR #1: Rotura de soldadura",
        "",
        "- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`",
        "- Ecuacion: `Fillet: Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq; hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm; phi*Rn_w3_p+_vgizq = phi * kds_w3_vgizq * nl_w3_vgizq * 0.6 * Fexx_w3_vgizq * 0.707 * hwef_w3_vgizq * t_w3_vgizq; DCR_w3_p+_vgizq = Ru_w3_p+_vgizq / phi*Rn_w3_p+_vgizq`",
        f"- tipo_w3_vgizq: `{_format_text(weld_type_raw)}`",
    ]
    if weld_type == "cjp":
        lines.extend(
            [
                "- CJP: `Cumple`",
                f"- Resultado: `{_render_result_plain_es(result_line)}`",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            f"- phi usado: `{_format_decimal(phi)}`",
            f"- hwef_w3_vgizq (longitud efectiva calculada): `hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm`",
            f"- hwef_w3_vgizq: `{hwef_text}`",
            f"- tw_vgizq: `{tw_text}`",
            f"- Fy_vgizq: `{fy_text}`",
            f"- Ru_w3_p+_vgizq: `{ru_text}`",
            f"- pfi_pe_vgizq: `{pfi_text}`",
            f"- pb_pe_vgizq: `{pb_text}`",
            f"- Fexx_w3_vgizq: `{fexx_text}`",
            f"- t_w3_vgizq: `{twe_text}`",
            f"- nl_w3_vgizq: `{_format_text(nl) if nl is not None else 'n/a (input requerido)'}`",
            f"- kds_w3_vgizq: `{_format_text(kds_w3_vgizq)}`",
            f"- phi*Rn_w3_p+_vgizq: `{phi_rn_text}`",
            f"- DCR_w3_p+_vgizq: `{dcr_text}`",
            f"- Resultado: `{_render_result_plain_es(result_line)}`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_step_12_column_flange_local_bending(
    step_12_1_1: dict | None,
    step_11_ctx: dict | None,
    step_10_1_1: dict | None,
) -> str:
    inputs = step_12_1_1.get("inputs", {}) if isinstance(step_12_1_1, dict) else {}
    inter = step_12_1_1.get("intermediates", {}) if isinstance(step_12_1_1, dict) else {}
    capacity = step_12_1_1.get("capacity") if isinstance(step_12_1_1, dict) else None
    design_factors = step_12_1_1.get("design_factors", {}) if isinstance(step_12_1_1, dict) else {}
    prequal_inputs = step_11_ctx.get("inputs", {}) if isinstance(step_11_ctx, dict) else {}
    step_10_inputs = step_10_1_1.get("inputs", {}) if isinstance(step_10_1_1, dict) else {}

    tcp_mm = _quantity_to_mm(prequal_inputs.get("continuity_plate_thickness_tcp"))
    enabled_raw = inputs.get("continuity_plate_enabled")
    if enabled_raw is None:
        enabled_raw = prequal_inputs.get("continuity_plate_enabled")
    if enabled_raw is None:
        enabled_raw = inter.get("continuity_plate_enabled")
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
    bcf_mm = _quantity_to_mm(prequal_inputs.get("column_flange_width_bcf"))
    if bcf_mm is None:
        bcf_mm = _quantity_to_mm(inter.get("bcf"))
    g_mm = _quantity_to_mm(prequal_inputs.get("bolt_gage_g"))
    if g_mm is None:
        g_mm = _quantity_to_mm(inter.get("g"))
    s_mm = _quantity_to_mm(inter.get("s"))
    if bcf_mm is not None and g_mm is not None and bcf_mm > 0.0 and g_mm > 0.0:
        s_mm = s_mm if s_mm is not None else 0.5 * ((bcf_mm * g_mm) ** 0.5)
    pfi_mm = _quantity_to_mm(prequal_inputs.get("pfi_pe_vgizq") or prequal_inputs.get("edge_pfi"))
    if pfi_mm is None:
        pfi_mm = _quantity_to_mm(inter.get("psi_input") or inter.get("psi_computed"))

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
    y_table_text = _format_text(inputs.get("yc_table_reference")).replace("Table", "Tabla")
    y_is_hardcoded = bool(inputs.get("yc_is_hardcoded"))
    d_vgizq_q = _as_quantity(step_10_inputs.get("d_vgizq") or prequal_inputs.get("d_vgizq") or inputs.get("d_vgizq") or inputs.get("beam_depth"))
    tf_vgizq_q = _as_quantity(
        step_10_inputs.get("tf_vgizq")
        or prequal_inputs.get("tf_vgizq")
        or inputs.get("tf_vgizq")
        or inputs.get("beam_flange_thickness")
    )
    z_vgizq_q: Quantity | None = None
    if d_vgizq_q is not None and tf_vgizq_q is not None:
        z_value = d_vgizq_q.value - tf_vgizq_q.value
        if z_value > 0.0:
            z_vgizq_q = Quantity(value=z_value, unit=d_vgizq_q.unit)
    mf_vgizq_max_q = inputs.get("mf")
    mf_vgizq_max_quantity = _as_quantity(mf_vgizq_max_q)

    ru_cf_v2_col_q: Quantity | None = None
    phi_rn_cf_v2_col_q: Quantity | None = None
    dcr_cf_v2_col = None
    if mf_vgizq_max_quantity is not None and z_vgizq_q is not None:
        converted_mf = _convert_moment_to_unit(mf_vgizq_max_quantity, "kN-mm" if z_vgizq_q.unit == "mm" else "kip-in")
        if converted_mf is not None:
            force_unit = "kN" if z_vgizq_q.unit == "mm" else "kip"
            ru_cf_v2_col_q = Quantity(value=converted_mf.value / z_vgizq_q.value, unit=force_unit)
    if phi_mn_q is not None and z_vgizq_q is not None:
        converted_phi_mn = _convert_moment_to_unit(phi_mn_q, "kN-mm" if z_vgizq_q.unit == "mm" else "kip-in")
        if converted_phi_mn is not None:
            force_unit = "kN" if z_vgizq_q.unit == "mm" else "kip"
            phi_rn_cf_v2_col_q = Quantity(value=converted_phi_mn.value / z_vgizq_q.value, unit=force_unit)
    if ru_cf_v2_col_q is not None and phi_rn_cf_v2_col_q is not None:
        try:
            dcr_cf_v2_col = compute_dcr(demand=ru_cf_v2_col_q, capacity=phi_rn_cf_v2_col_q)["dcr"]
        except ValueError:
            dcr_cf_v2_col = None

    case_y = _format_text(inputs.get("yc_case_reference"))
    if case_y == "n/a" and pfi_mm is not None and s_mm is not None:
        case_y = "Case 1 (pfi <= s)" if pfi_mm <= s_mm else "Case 2 (pfi > s)"

    dcr_text = _format_decimal(dcr_cf_v2_col) if dcr_cf_v2_col is not None else "n/a"
    if dcr_cf_v2_col is None:
        result_line = "n/a"
    else:
        result_line = "Cumple" if dcr_cf_v2_col <= 1.0 else "No cumple"
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
        "## Paso 13 - Revision de resistencia de la aleta de la columna (vg_izq)",
        "",
        "### 13.1. Revision de capacidad a flexion",
        "",
        "#### 13.1.1. ELR #1: Flexion local de la aleta (LFB)",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Ecuacion: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); phi*Rn_cf_v2_col_vgizq = phi_ductil * ((tf_col^2 * Fy_col * {y_symbol})/(1.11 * (d_vgizq - tf_vgizq))); DCR_cf_v2_col_vgizq = Ru_cf_v2_col_vgizq / phi*Rn_cf_v2_col_vgizq`",
        f"- phi usado: `{_format_decimal(phi)}`",
        f"- Mf_vgizq_critico: `{_format_quantity(mf_vgizq_max_q)}`",
        f"- d_vgizq: `{_format_quantity(d_vgizq_q.model_dump()) if d_vgizq_q is not None else 'n/a'}`",
        f"- tf_vgizq: `{_format_quantity(tf_vgizq_q.model_dump()) if tf_vgizq_q is not None else 'n/a'}`",
        f"- z_vgizq = d_vgizq - tf_vgizq: `{_format_quantity(z_vgizq_q.model_dump()) if z_vgizq_q is not None else 'n/a'}`",
        f"- tf_col: `{_format_quantity(inputs.get('column_flange_thickness_from_sections') or capacity)}`",
        f"- Fy_col: `{_format_quantity(inputs.get('column_fy'))}`",
        f"- {y_symbol} usado: `{_format_quantity(inputs.get('yc'))}`",
        f"- Tabla {y_symbol} aplicada: `{y_table_text}`",
        f"- Caso {y_symbol}: `{case_y}`",
        *([f"- Advertencia: `{y_symbol} esta hardcodeado`"] if y_is_hardcoded else []),
        f"- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgizq)`",
        f"- s_col: `{_format_decimal(s_mm)} mm`" if s_mm is not None else "- s_col: `n/a`",
        f"- usar_pc_col: `{continuity_text}`",
        f"- Ru_cf_v2_col_vgizq: `{_format_quantity(ru_cf_v2_col_q.model_dump()) if ru_cf_v2_col_q is not None else 'n/a'}`",
        f"- phi*Rn_cf_v2_col_vgizq: `{_format_quantity(phi_rn_cf_v2_col_q.model_dump()) if phi_rn_cf_v2_col_q is not None else 'n/a'}`",
        f"- DCR_cf_v2_col_vgizq: `{dcr_text}`",
        f"- Resultado: `{_render_result_plain_es(result_line)}`",
        "",
        "Donde:",
        "",
        f"- Ecuacion {y_symbol}: `{_format_text(inputs.get('yc_formula'))}`",
        "- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).",
        "- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).",
        "- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`",
        "",
    ]
    return "\n".join(lines)


def _render_step_13_column_web_local_yielding(
    step_13_1_1: dict | None,
    step_14_2_1: dict | None,
    step_14_2_2: dict | None,
) -> str:
    if not isinstance(step_13_1_1, dict):
        return "\n".join(
            [
                "## Paso 14 - Revision de resistencia del alma de la columna (vg_izq)",
                "",
                "Sin resultados para el Paso 14.",
                "",
            ]
        )
    inputs = step_13_1_1.get("inputs", {})
    inter = step_13_1_1.get("intermediates", {})
    design_factors = step_13_1_1.get("design_factors", {})
    lines = [
        "## Paso 14 - Revision de resistencia del alma de la columna (vg_izq)",
        "",
        "### 14.1. Revision de capacidad a traccion",
        "",
        "#### 14.1.1. ELR #1: Fluencia local del alma (WLY)",
        "",
        f"- Clausula: `{_render_clause_text(step_13_1_1.get('clause'), step_13_1_1.get('source_document'), step_13_1_1.get('rule_id'))}`",
        "- Ecuacion: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cf_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cf_v2_col_vgizq = Ru_cf_v2_col_vgizq / phi*Rn_cf_v2_col_vgizq`",
        f"- phi usado (phi_ductil): `{_format_text(design_factors.get('phi_d'))}`",
        f"- Mf_vgizq_critico: `{_format_quantity(inputs.get('mf_vgizq_critico'))}`",
        f"- St_col: `{_format_quantity(inputs.get('st_col'))}`",
        f"- d_col: `{_format_quantity(inputs.get('d_col'))}`",
        f"- Ct_col: `{_format_text(inputs.get('ct_col'))}`",
        f"- kc_col: `{_format_quantity(inputs.get('kc_col'))}`",
        f"- lb_col: `{_format_quantity(inputs.get('lb_col'))}`",
        f"- Ecuacion lb_col: `{_format_text(inputs.get('lb_col_formula'))}`",
        f"- Fy_col: `{_format_quantity(inputs.get('fy_col') or inputs.get('column_fy'))}`",
        f"- tw_col: `{_format_quantity(inputs.get('tw_col'))}`",
        f"- d_vgizq: `{_format_quantity(inputs.get('d_vgizq'))}`",
        f"- tf_vgizq: `{_format_quantity(inputs.get('tf_vgizq'))}`",
        f"- tpe_vgizq: `{_format_quantity(inputs.get('tpe_vgizq'))}`",
        f"- t_w4_1_vgizq: `{_format_quantity(inputs.get('t_w4_1_vgizq'))}`",
        f"- nl_w4_vgizq: `{_format_text(inputs.get('nl_w4_vgizq'))}`",
        f"- demanda_ductilidad_vgizq: `{_format_text(inputs.get('ductility_vgizq'))}`",
        f"- 2w_w4_vgizq: `{_format_quantity(inputs.get('total_weld_thickness_w4_vgizq'))}`",
        f"- Ecuacion 2w_w4_vgizq: `{_format_text(inputs.get('total_weld_thickness_w4_formula'))}`",
        f"- Ru_cf_v2_col_vgizq: `{_format_quantity(step_13_1_1.get('demand'))}`",
        f"- phi*Rn_cf_v2_col_vgizq: `{_format_quantity(step_13_1_1.get('capacity'))}`",
        f"- DCR_cf_v2_col_vgizq: `{_format_text(step_13_1_1.get('dcr'))}`",
        f"- Resultado: `{_render_result_plain_es(step_13_1_1.get('status'))}`",
        "",
    ]
    if isinstance(step_14_2_1, dict):
        wlc_inputs = step_14_2_1.get("inputs", {})
        wlc_inter = step_14_2_1.get("intermediates", {})
        wlc_design = step_14_2_1.get("design_factors", {})
        lines.extend(
            [
                "### 14.2. Revision de capacidad a compresion",
                "",
                "#### 14.2.1. ELR #1: Arrugamiento local del alma (WLC)",
                "",
                f"- Clausula: `{_render_clause_text(step_14_2_1.get('clause'), step_14_2_1.get('source_document'), step_14_2_1.get('rule_id'))}`",
                "- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_eq(6.7-19/6.7-20/6.7-21); DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`",
                f"- phi usado: `{_format_text(wlc_design.get('phi_wlc'))}`",
                f"- Mf_vgizq_critico: `{_format_quantity(wlc_inputs.get('mf_vgizq_critico'))}`",
                f"- St_col: `{_format_quantity(wlc_inputs.get('st_col'))}`",
                f"- d_col (dc): `{_format_quantity(wlc_inputs.get('d_col'))}`",
                f"- lb_col: `{_format_quantity(wlc_inputs.get('lb_col'))}`",
                f"- Ecuacion lb_col: `{_format_text(wlc_inputs.get('lb_col_formula'))}`",
                f"- Fy_col: `{_format_quantity(wlc_inputs.get('fy_col'))}`",
                f"- E_col: `{_format_quantity(wlc_inputs.get('e_col'))}`",
                f"- tw_col: `{_format_quantity(wlc_inputs.get('tw_col'))}`",
                f"- tf_col: `{_format_quantity(wlc_inputs.get('tf_col'))}`",
                f"- d_vgizq: `{_format_quantity(wlc_inputs.get('d_vgizq'))}`",
                f"- tf_vgizq: `{_format_quantity(wlc_inputs.get('tf_vgizq'))}`",
                f"- tpe_vgizq: `{_format_quantity(wlc_inputs.get('tpe_vgizq'))}`",
                f"- t_w4_1_vgizq: `{_format_quantity(wlc_inputs.get('t_w4_1_vgizq'))}`",
                f"- nl_w4_vgizq: `{_format_text(wlc_inputs.get('nl_w4_vgizq'))}`",
                f"- demanda_ductilidad_vgizq: `{_format_text(wlc_inputs.get('ductility_vgizq'))}`",
                f"- 2w_w4_vgizq: `{_format_quantity(wlc_inputs.get('total_weld_thickness_w4_vgizq'))}`",
                f"- Ecuacion 2w_w4_vgizq: `{_format_text(wlc_inputs.get('total_weld_thickness_w4_formula'))}`",
                f"- Ecuacion Rn aplicada: `{_format_text(wlc_inter.get('case'))}`",
                f"- Ru_cw_v2_col_vgizq: `{_format_quantity(step_14_2_1.get('demand'))}`",
                f"- phi*Rn_cw_v2_col_vgizq: `{_format_quantity(step_14_2_1.get('capacity'))}`",
                f"- DCR_cw_v2_col_vgizq: `{_format_text(step_14_2_1.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_14_2_1.get('status'))}`",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "### 14.2. Revision de capacidad a compresion",
                "",
                "#### 14.2.1. ELR #1: Arrugamiento local del alma (WLC)",
                "",
                "- Resultado: `n/a`",
                "",
            ]
        )
    if isinstance(step_14_2_2, dict):
        wcb_inputs = step_14_2_2.get("inputs", {})
        wcb_inter = step_14_2_2.get("intermediates", {})
        wcb_design = step_14_2_2.get("design_factors", {})
        applies = bool(wcb_inter.get("applicability_condition_met"))
        lines.extend(
            [
                "#### 14.2.2. ELR #2: Pandeo local del alma (WCB)",
                "",
                f"- Clausula: `{_render_clause_text(step_14_2_2.get('clause'), step_14_2_2.get('source_document'), step_14_2_2.get('rule_id'))}`",
                "- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgizq = max(|-Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|, |Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgizq = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`",
                f"- Condicion aplicabilidad cumplida: `{_format_text(applies)}`",
                f"- phi usado: `{_format_text(wcb_design.get('phi_wcb'))}`",
                f"- Mu3_vgizq: `{_format_quantity(wcb_inputs.get('mu3_vgizq'))}`",
                f"- Mu3_vgder: `{_format_quantity(wcb_inputs.get('mu3_vgder'))}`",
                f"- Pu_vgizq: `{_format_quantity(wcb_inputs.get('pu_vgizq'))}`",
                f"- Pu_vgder: `{_format_quantity(wcb_inputs.get('pu_vgder'))}`",
                f"- d_vgizq: `{_format_quantity(wcb_inputs.get('d_vgizq'))}`",
                f"- tf_vgizq: `{_format_quantity(wcb_inputs.get('tf_vgizq'))}`",
                f"- d_vgder: `{_format_quantity(wcb_inputs.get('d_vgder'))}`",
                f"- tf_vgder: `{_format_quantity(wcb_inputs.get('tf_vgder'))}`",
                f"- termino_condicion_izq: `{_format_scalar_with_unit(wcb_inter.get('cond_left_force'), (step_14_2_2.get('demand') or {}).get('unit', 'kN'))}`",
                f"- termino_condicion_der: `{_format_scalar_with_unit(wcb_inter.get('cond_right_force'), (step_14_2_2.get('demand') or {}).get('unit', 'kN'))}`",
                f"- tolerancia_condicion: `{_format_text(wcb_inter.get('cond_tolerance'))}`",
                f"- same_sign: `{_format_text(wcb_inter.get('same_sign'))}`",
                f"- St_col: `{_format_quantity(wcb_inputs.get('st_col'))}`",
                f"- d_col: `{_format_quantity(wcb_inputs.get('d_col'))}`",
                f"- Ct_col: `{_format_text(wcb_inter.get('ct'))}`",
                f"- kc_col: `{_format_quantity(wcb_inputs.get('kc_col'))}`",
                f"- h_col: `{_format_quantity(wcb_inputs.get('h_col'))}`",
                f"- E_col: `{_format_quantity(wcb_inputs.get('e_col'))}`",
                f"- Fy_col: `{_format_quantity(wcb_inputs.get('fy_col'))}`",
                f"- tw_col: `{_format_quantity(wcb_inputs.get('tw_col'))}`",
                f"- 2w_w4_vgizq: `{_format_quantity(wcb_inputs.get('total_weld_thickness_w4_vgizq'))}`",
                f"- Ecuacion 2w_w4_vgizq: `{_format_text(wcb_inputs.get('total_weld_thickness_w4_formula'))}`",
            ]
        )
        if applies:
            lines.extend(
                [
                    f"- Ru_cw_v2_col_vgizq: `{_format_quantity(step_14_2_2.get('demand'))}`",
                    f"- phi*Rn_cw_v2_col_vgizq: `{_format_quantity(step_14_2_2.get('capacity'))}`",
                    f"- DCR_cw_v2_col_vgizq: `{_format_text(step_14_2_2.get('dcr'))}`",
                    f"- Resultado: `{_render_result_plain_es(step_14_2_2.get('status'))}`",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "- Resultado: `No aplica`",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "#### 14.2.2. ELR #2: Pandeo local del alma (WCB)",
                "",
                "- Resultado: `n/a`",
                "",
            ]
        )
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
                    f"- Separacion entre vigas (gap_sp): `{_format_quantity(item.get('alpha'))}`",
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
                    f"- Factor de rezago de cortante 1 (U1): `{_format_text(item.get('us1'))}`",
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
                    f"- Diametro nominal (db_blt_web): `{_format_quantity(item.get('diameter_nominal'))}`",
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
                    f"- Diametro nominal (db_blt_flange): `{_format_quantity(item.get('diameter_nominal'))}`",
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
        f"- Pu_sp: `{px}`",
        f"- Vu2_sp: `{py}`",
        f"- ex_blt_web: `{ex}`",
        f"- ey_blt_web: `{ey}`",
        f"- Fuente excentricidad: `{e_source}`",
        f"- Muz_blt_web: `{mz}`",
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
    active_sides = _collect_active_sides(result)

    def _map_step(step_fragment: str) -> dict[str, dict | None]:
        return {
            side: _collect_check_by_step_and_side(
                result,
                step_fragment=step_fragment,
                side=side,
            )
            for side in active_sides
        }

    step_6_1_by_side = _map_step("step6_1_bolt_tension_rupture")
    step_6_2_by_side = _map_step("step6_2_bolt_shear_rupture")
    step_7_1_1_by_side = _map_step("step7_1_1_end_plate_flexural_yielding")
    step_7_2_1_by_side = _map_step("step7_2_1_end_plate_shear_yielding")
    step_7_2_2_by_side = _map_step("step7_2_2_end_plate_shear_rupture")
    step_7_3_1_by_side = _map_step("step7_3_1_end_plate_hole_tearout")
    step_7_3_2_by_side = _map_step("step7_3_2_end_plate_hole_bearing")
    step_8_1_1_by_side = _map_step("step8_1_1_stiffener_weld_tension_rupture")
    step_9_1_1_by_side = _map_step("step9_1_1_stiffener_beam_weld_shear_rupture")
    step_10_w4_1_1_by_side = _map_step("step10_1_1_beam_flange_end_plate_weld_tension_rupture")
    step_11_beam_shear_by_side = _map_step("step11_1_1_beam_shear_yielding")
    step_11_w3_check_by_side = _map_step("step11_1_1_beam_web_end_plate_weld_tension_rupture")
    step_11_ctx_by_side = {
        side: {"inputs": check_payload.get("inputs", {})} if isinstance(check_payload, dict) else None
        for side, check_payload in step_11_w3_check_by_side.items()
    }
    step_12_1_1_by_side = _map_step("step12_1_1_column_flange_local_bending")
    step_13_1_1_by_side = _map_step("step13_1_1_column_web_local_yielding")
    step_14_2_1_by_side = _map_step("step14_2_1_column_web_local_crippling")
    step_14_2_2_by_side = _map_step("step14_2_2_column_web_local_buckling")
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
    step_numbers_in_content: list[int] = []
    for item in content:
        for line in str(item).splitlines():
            match = re.match(r"^##\s+Paso\s+(\d+)\s+-", line.strip())
            if match:
                step_numbers_in_content.append(int(match.group(1)))
    next_step_number = (max(step_numbers_in_content) + 1) if step_numbers_in_content else 1
    if connection_family_normalized == "moment_prequalified":
        step_groups: list[tuple[object, list[dict[str, dict | None]]]] = [
            (_render_step_6_bolts, [step_6_1_by_side, step_6_2_by_side]),
            (
                _render_step_7_end_plate,
                [
                    step_7_1_1_by_side,
                    step_7_2_1_by_side,
                    step_7_2_2_by_side,
                    step_7_3_1_by_side,
                    step_7_3_2_by_side,
                ],
            ),
            (_render_step_8_stiffener_weld, [step_8_1_1_by_side]),
            (_render_step_9_stiffener_beam_weld, [step_9_1_1_by_side]),
            (_render_step_10_beam_flange_end_plate_weld, [step_10_w4_1_1_by_side]),
            (_render_step_10_beam_shear, [step_11_beam_shear_by_side]),
            (_render_step_11_end_plate_beam_web_weld_tension, [step_11_ctx_by_side, step_11_beam_shear_by_side]),
        ]
        for renderer, payload_maps in step_groups:
            for side in active_sides:
                args = [payload_map.get(side) for payload_map in payload_maps]
                block = _render_block_for_side(renderer, *args, side=side).strip()
                if block:
                    block = _tag_side_subheadings(block, side=side)
                    assigned_step_number = next_step_number
                    block = _replace_first_step_heading_number(block, step_number=assigned_step_number)
                    block = _align_nested_heading_numbers_with_step(block, step_number=assigned_step_number)
                    next_step_number += 1
                    content.append(block)

    if connection_family_normalized == "moment_prequalified":
        side_sections_13: list[str] = []
        side_index_13 = {side: idx for idx, side in enumerate(active_sides, start=1)}
        for side in active_sides:
            side_tag = "vg_izq" if side == "izq" else "vg_der"
            heading_index = side_index_13[side]
            block = _render_block_for_side(
                _render_step_12_column_flange_local_bending,
                step_12_1_1_by_side.get(side),
                step_11_ctx_by_side.get(side),
                step_10_w4_1_1_by_side.get(side),
                side=side,
            ).strip()
            if not block:
                continue
            body = _strip_first_h2(block)
            body = body.replace(
                "### 13.1. Revision de capacidad a flexion",
                f"### 13.{heading_index}. Revision de capacidad a flexion ({side_tag})",
            )
            body = body.replace("#### 13.1.1. ", f"#### 13.{heading_index}.1. ")
            side_sections_13.append(body)
        if side_sections_13:
            assigned_step_number = next_step_number
            block_13 = "\n".join(
                [
                    f"## Paso {assigned_step_number} - Revision de resistencia de la aleta de la columna",
                    "",
                    "\n\n".join(side_sections_13),
                ]
            )
            block_13 = _align_nested_heading_numbers_with_step(block_13, step_number=assigned_step_number)
            content.append(block_13)
            next_step_number += 1

    if connection_family_normalized == "moment_prequalified":
        side_sections_14: list[str] = []
        traction_heading_index_by_side: dict[str, int] = {}
        compression_heading_index_by_side: dict[str, int] = {}
        heading_counter = 1
        for side in active_sides:
            traction_heading_index_by_side[side] = heading_counter
            heading_counter += 1
            compression_heading_index_by_side[side] = heading_counter
            heading_counter += 1

        for side in active_sides:
            side_tag = "vg_izq" if side == "izq" else "vg_der"
            traction_idx = traction_heading_index_by_side[side]
            compression_idx = compression_heading_index_by_side[side]
            block = _render_block_for_side(
                _render_step_13_column_web_local_yielding,
                step_13_1_1_by_side.get(side),
                step_14_2_1_by_side.get(side),
                step_14_2_2_by_side.get(side),
                side=side,
            ).strip()
            if not block:
                continue
            body = _strip_first_h2(block)
            body = body.replace(
                "### 14.1. Revision de capacidad a traccion",
                f"### 14.{traction_idx}. Revision de capacidad a traccion ({side_tag})",
            )
            body = body.replace("#### 14.1.1. ", f"#### 14.{traction_idx}.1. ")
            body = body.replace(
                "### 14.2. Revision de capacidad a compresion",
                f"### 14.{compression_idx}. Revision de capacidad a compresion ({side_tag})",
            )
            body = body.replace("#### 14.2.1. ", f"#### 14.{compression_idx}.1. ")
            body = body.replace("#### 14.2.2. ", f"#### 14.{compression_idx}.2. ")
            side_sections_14.append(body)
        if side_sections_14:
            assigned_step_number = next_step_number
            block_14 = "\n".join(
                [
                    f"## Paso {assigned_step_number} - Revision de resistencia del alma de la columna",
                    "",
                    "\n\n".join(side_sections_14),
                ]
            )
            block_14 = _align_nested_heading_numbers_with_step(block_14, step_number=assigned_step_number)
            content.append(block_14)
            next_step_number += 1
    content.append("")
    rendered = "\n".join(content)
    return _normalize_markdown_spacing(rendered) + "\n"


def write_memory_markdown(result: DetailedRunResult, target_dir: str | Path) -> Path:
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "memory.md"
    rendered = render_memory_markdown(result).rstrip("\n") + "\n"
    target.write_text(rendered, encoding="utf-8")
    return target


def render_splice_methods_table_markdown(result: DetailedRunResult) -> str:
    step2 = _collect_splice_step_2_method(result)
    if not isinstance(step2, dict):
        return "\n".join(
            [
                "# Metodos Pernos 1 (Splice) - Desarrollo Paso a Paso",
                "",
                "No existe resultado de `Punto 2 - Metodo ICR/Elastic` para este caso.",
                "",
            ]
        )

    def _to_float(value: object) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def _num(value: object) -> str:
        numeric = _to_float(value)
        if numeric is None:
            return "n/a"
        return _format_decimal(numeric)

    def _normalize_markdown_spacing(text: str) -> str:
        raw_lines = text.splitlines()
        lines: list[str] = []
        for raw in raw_lines:
            lines.append(raw.rstrip())

        # Pass 1: ensure blank line before headings and before list blocks.
        pass1: list[str] = []
        for line in lines:
            stripped = line.strip()
            is_heading = stripped.startswith("#")
            is_list = stripped.startswith("- ")

            if is_heading and pass1 and pass1[-1] != "":
                pass1.append("")

            if is_list and pass1 and pass1[-1] != "" and not pass1[-1].lstrip().startswith("- "):
                pass1.append("")

            pass1.append(line)

        # Pass 2: ensure blank line after headings and after list blocks.
        pass2: list[str] = []
        total = len(pass1)
        for idx, line in enumerate(pass1):
            stripped = line.strip()
            is_heading = stripped.startswith("#")
            is_list = stripped.startswith("- ")
            next_line = pass1[idx + 1] if idx + 1 < total else None
            next_stripped = next_line.strip() if next_line is not None else ""
            next_is_list = next_stripped.startswith("- ")

            pass2.append(line)

            if is_heading and next_line is not None and next_stripped != "":
                pass2.append("")
            if is_list and next_line is not None and (not next_is_list) and next_stripped != "":
                pass2.append("")

        # Pass 3: collapse consecutive blank lines to one.
        pass3: list[str] = []
        previous_blank = False
        for line in pass2:
            is_blank = line.strip() == ""
            if is_blank and previous_blank:
                continue
            pass3.append(line)
            previous_blank = is_blank

        while pass3 and pass3[-1].strip() == "":
            pass3.pop()
        pass3.append("")
        return "\n".join(pass3)

    def _md_table(headers: list[str], rows: list[list[object]]) -> list[str]:
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        if not rows:
            lines.append("| " + " | ".join("-" for _ in headers) + " |")
            return lines
        for row in rows:
            formatted = [_format_text(value).replace("|", "\\|") for value in row]
            lines.append("| " + " | ".join(formatted) + " |")
        return lines

    report = step2.get("report")
    if not isinstance(report, dict):
        report = {}
    intermediates = step2.get("intermediates")
    if not isinstance(intermediates, dict):
        intermediates = {}

    methods_summary = report.get("methods_summary")
    if not isinstance(methods_summary, list):
        methods_summary = []
    methods_by_name: dict[str, dict] = {}
    for item in methods_summary:
        if isinstance(item, dict):
            methods_by_name[_format_text(item.get("method"))] = item

    method_super = methods_by_name.get("elastic_superposition", {})
    method_ecr = methods_by_name.get("elastic_ecr", {})
    method_icr = methods_by_name.get("icr", {})

    geometry_block = intermediates.get("bolt_group_geometry")
    if not isinstance(geometry_block, dict):
        geometry_block = {}
    load_block = intermediates.get("load_in_plane_kip_in")
    if not isinstance(load_block, dict):
        load_block = {}

    bolts_offsets = geometry_block.get("bolts_offsets")
    if not isinstance(bolts_offsets, list):
        bolts_offsets = []

    bolts: list[dict[str, object]] = []
    for index, bolt in enumerate(bolts_offsets, start=1):
        if not isinstance(bolt, dict):
            continue
        x_in = _to_float(bolt.get("x_in"))
        y_in = _to_float(bolt.get("y_in"))
        if x_in is None or y_in is None:
            continue
        bolts.append(
            {
                "row": index,
                "tag": _format_text(bolt.get("tag")),
                "x_in": x_in,
                "y_in": y_in,
                "dx_in": _to_float(bolt.get("dx_in")),
                "dy_in": _to_float(bolt.get("dy_in")),
                "r_in": _to_float(bolt.get("r_in")),
            }
        )

    bolt_count = _to_float(geometry_block.get("bolt_count"))
    x_cg = _to_float(geometry_block.get("centroid_x_in"))
    y_cg = _to_float(geometry_block.get("centroid_y_in"))
    ix_in2 = _to_float(geometry_block.get("ix_in2"))
    iy_in2 = _to_float(geometry_block.get("iy_in2"))
    ip_in2 = _to_float(geometry_block.get("ip_in2"))
    if x_cg is None and bolts:
        x_cg = sum(_to_float(b["x_in"]) or 0.0 for b in bolts) / float(len(bolts))
    if y_cg is None and bolts:
        y_cg = sum(_to_float(b["y_in"]) or 0.0 for b in bolts) / float(len(bolts))
    if bolt_count is None:
        bolt_count = float(len(bolts)) if bolts else None
    if ix_in2 is None and bolts and y_cg is not None:
        ix_in2 = sum(((_to_float(b["y_in"]) or 0.0) - y_cg) ** 2 for b in bolts)
    if iy_in2 is None and bolts and x_cg is not None:
        iy_in2 = sum(((_to_float(b["x_in"]) or 0.0) - x_cg) ** 2 for b in bolts)
    if ip_in2 is None and ix_in2 is not None and iy_in2 is not None:
        ip_in2 = ix_in2 + iy_in2

    vx_kip = _to_float(load_block.get("vx_kip")) or 0.0
    vy_kip = _to_float(load_block.get("vy_kip")) or 0.0
    ex_in = _to_float(load_block.get("ex_in")) or 0.0
    ey_in = _to_float(load_block.get("ey_in")) or 0.0
    mz_kip_in = _to_float(load_block.get("mz_kip_in"))
    if mz_kip_in is None:
        mz_kip_in = vy_kip * ex_in - vx_kip * ey_in

    p_kip = math.hypot(vx_kip, vy_kip)
    theta_blt_web_deg = math.degrees(math.atan2(vy_kip, vx_kip)) if p_kip > 1e-12 else 0.0
    e_mag_in = math.hypot(ex_in, ey_in)
    dmax_cg = None
    if bolts and x_cg is not None and y_cg is not None:
        dmax_cg = max(
            math.hypot((_to_float(b["x_in"]) or 0.0) - x_cg, (_to_float(b["y_in"]) or 0.0) - y_cg)
            for b in bolts
        )

    geometry_rows = [
        ["Ru_blt_web_v23", "sqrt(Pu_sp^2 + Vu2_sp^2)", _num(p_kip), "kip"],
        ["theta_blt_web", "atan2(Vu2_sp, Pu_sp)", _num(theta_blt_web_deg), "deg"],
        ["e_blt_web", "sqrt(ex_blt_web^2 + ey_blt_web^2)", _num(e_mag_in), "in"],
        ["n_blt_web", "conteo pernos activos", _num(bolt_count), "-"],
        ["x_cg_blt_web", "sum(x_i_blt_web)/n_blt_web", _num(x_cg), "in"],
        ["y_cg_blt_web", "sum(y_i_blt_web)/n_blt_web", _num(y_cg), "in"],
        ["Ix_blt_web", "sum((y_i_blt_web-y_cg_blt_web)^2)", _num(ix_in2), "in2"],
        ["Iy_blt_web", "sum((x_i_blt_web-x_cg_blt_web)^2)", _num(iy_in2), "in2"],
        ["J_blt_web", "Ix_blt_web + Iy_blt_web", _num(ip_in2), "in2"],
        ["Muz_blt_web", "Vu2_sp*ex_blt_web - Pu_sp*ey_blt_web", _num(mz_kip_in), "kip-in"],
        [
            "dmax_blt_web",
            "max(sqrt((x_i_blt_web-x_cg_blt_web)^2+(y_i_blt_web-y_cg_blt_web)^2))",
            _num(dmax_cg),
            "in",
        ],
    ]

    bolts_rows = [
        [
            bolt.get("row"),
            bolt.get("tag"),
            _num(bolt.get("x_in")),
            _num(bolt.get("y_in")),
            _num(bolt.get("dx_in")),
            _num(bolt.get("dy_in")),
            _num(bolt.get("r_in")),
        ]
        for bolt in bolts
    ]

    summary_rows = []
    for method in ("elastic_superposition", "elastic_ecr", "icr"):
        item = methods_by_name.get(method, {})
        summary_rows.append(
            [
                method,
                _format_text(item.get("applicable")),
                _format_text(item.get("status")),
                _num(item.get("demand_kip")),
                _num(item.get("capacity_kip")),
                _num(item.get("dcr")),
            ]
        )

    super_geom_rows: list[list[object]] = []
    super_force_rows: list[list[object]] = []
    super_summary_rows: list[list[object]] = []
    super_total_force_by_tag: dict[str, tuple[float, float]] = {}
    if bolts and bolt_count is not None and ip_in2 is not None and abs(ip_in2) > 1e-12:
        fx_dir = -vx_kip / bolt_count
        fy_dir = -vy_kip / bolt_count
        for bolt in bolts:
            dx = _to_float(bolt.get("dx_in")) or 0.0
            dy = _to_float(bolt.get("dy_in")) or 0.0
            d = math.hypot(dx, dy)
            fx_t = mz_kip_in * dy / ip_in2
            fy_t = -mz_kip_in * dx / ip_in2
            fx = fx_dir + fx_t
            fy = fy_dir + fy_t
            r = math.hypot(fx, fy)
            tag = bolt.get("tag")
            super_geom_rows.append(
                [bolt.get("row"), tag, _num(bolt.get("x_in")), _num(bolt.get("y_in")), _num(dx), _num(dy), _num(d)]
            )
            super_force_rows.append([bolt.get("row"), tag, _num(fx_dir), _num(fy_dir), _num(fx_t), _num(fy_t), _num(r)])
            super_summary_rows.append([bolt.get("row"), tag, _num(fx), _num(fy), _num(r)])
            if tag is not None:
                super_total_force_by_tag[_format_text(tag)] = (fx, fy)

    ecr_geom_rows: list[list[object]] = []
    ecr_force_rows: list[list[object]] = []
    ecr_summary_rows: list[list[object]] = []
    ax_ecr = None
    ay_ecr = None
    x_ecr_formula = None
    y_ecr_formula = None
    if (
        bolt_count is not None
        and ip_in2 is not None
        and mz_kip_in is not None
        and abs(float(bolt_count) * float(mz_kip_in)) > 1e-12
    ):
        ax_ecr = (vy_kip * ip_in2) / (float(bolt_count) * mz_kip_in)
        ay_ecr = (vx_kip * ip_in2) / (float(bolt_count) * mz_kip_in)
        if x_cg is not None:
            x_ecr_formula = x_cg + ax_ecr
        if y_cg is not None:
            y_ecr_formula = y_cg + ay_ecr

    # Unico ECR reportado: el calculado por Insight #1 (formula cerrada).
    center_x_ecr = x_ecr_formula
    center_y_ecr = y_ecr_formula

    if bolts and center_x_ecr is not None and center_y_ecr is not None:
        numerator_k = 0.0
        denominator_k = 0.0
        for bolt in bolts:
            tag = _format_text(bolt.get("tag"))
            x_i = _to_float(bolt.get("x_in")) or 0.0
            y_i = _to_float(bolt.get("y_in")) or 0.0
            dx_ecr = x_i - center_x_ecr
            dy_ecr = y_i - center_y_ecr
            super_forces = super_total_force_by_tag.get(tag)
            if super_forces is None:
                continue
            fx_total, fy_total = super_forces
            numerator_k += fx_total * dy_ecr - fy_total * dx_ecr
            denominator_k += dx_ecr * dx_ecr + dy_ecr * dy_ecr
        k_ecr = (numerator_k / denominator_k) if denominator_k > 1e-12 else None

        for bolt in bolts:
            tag = _format_text(bolt.get("tag"))
            x_i = _to_float(bolt.get("x_in")) or 0.0
            y_i = _to_float(bolt.get("y_in")) or 0.0
            dx_ecr = x_i - center_x_ecr
            dy_ecr = y_i - center_y_ecr
            d = math.hypot(dx_ecr, dy_ecr)
            if k_ecr is not None:
                fx_ecr = k_ecr * dy_ecr
                fy_ecr = -k_ecr * dx_ecr
                r_ecr = math.hypot(fx_ecr, fy_ecr)
            else:
                fx_ecr = None
                fy_ecr = None
                r_ecr = None
            ecr_geom_rows.append([bolt.get("row"), tag, _num(x_i), _num(y_i), _num(dx_ecr), _num(dy_ecr), _num(d)])
            ecr_force_rows.append(
                [
                    bolt.get("row"),
                    tag,
                    _num(fx_ecr),
                    _num(fy_ecr),
                    _num(r_ecr),
                    _num(center_x_ecr),
                    _num(center_y_ecr),
                ]
            )
            ecr_summary_rows.append([bolt.get("row"), tag, _num(fx_ecr), _num(fy_ecr), _num(r_ecr)])

    icr_iterations = report.get("icr_iterations")
    if not isinstance(icr_iterations, list):
        icr_iterations = []
    icr_x_final = _to_float(method_icr.get("icr_x_in"))
    icr_y_final = _to_float(method_icr.get("icr_y_in"))
    if (icr_x_final is None or icr_y_final is None) and icr_iterations:
        last_valid_iter = next(
            (it for it in reversed(icr_iterations) if isinstance(it, dict) and _to_float(it.get("icr_x")) is not None and _to_float(it.get("icr_y")) is not None),
            None,
        )
        if isinstance(last_valid_iter, dict):
            icr_x_final = _to_float(last_valid_iter.get("icr_x"))
            icr_y_final = _to_float(last_valid_iter.get("icr_y"))

    icr_coord_rows: list[list[object]] = []
    prev_x_after = None
    prev_y_after = None
    for idx_it, it in enumerate(icr_iterations):
        if not isinstance(it, dict):
            continue
        iteration_idx = _to_float(it.get("iteration"))
        x_after = _to_float(it.get("icr_x"))
        y_after = _to_float(it.get("icr_y"))
        if iteration_idx is None or x_after is None or y_after is None:
            continue
        if idx_it == 0:
            x_est = center_x_ecr if center_x_ecr is not None else x_after
            y_est = center_y_ecr if center_y_ecr is not None else y_after
        else:
            x_est = prev_x_after if prev_x_after is not None else x_after
            y_est = prev_y_after if prev_y_after is not None else y_after
        icr_coord_rows.append([_num(iteration_idx), _num(x_est), _num(y_est), _num(x_after), _num(y_after)])
        prev_x_after = x_after
        prev_y_after = y_after

    mu = _to_float(method_icr.get("law_mu")) or 10.0
    lambda_exp = _to_float(method_icr.get("law_lambda")) or 0.55
    delta_max = _to_float(method_icr.get("law_delta_max")) or 0.34

    icr_iter_rows_a: list[list[object]] = []
    icr_iter_rows_b: list[list[object]] = []
    icr_bolt_rows_a: list[list[object]] = []
    icr_bolt_rows_b: list[list[object]] = []

    if bolts:
        for it in icr_iterations:
            if not isinstance(it, dict):
                continue
            iteration = _to_float(it.get("iteration"))
            x_icr = _to_float(it.get("icr_x"))
            y_icr = _to_float(it.get("icr_y"))
            if iteration is None or x_icr is None or y_icr is None:
                continue

            if x_cg is not None and y_cg is not None:
                r_ox = ex_in + (x_cg - x_icr)
                r_oy = ey_in - (y_icr - y_cg)
                r_o = math.hypot(r_ox, r_oy)
            else:
                r_ox = None
                r_oy = None
                r_o = None

            per_bolt: list[dict[str, float | str | None]] = []
            for bolt in bolts:
                x_i = _to_float(bolt.get("x_in")) or 0.0
                y_i = _to_float(bolt.get("y_in")) or 0.0
                dx = x_i - x_icr
                dy = y_i - y_icr
                d = math.hypot(dx, dy)
                row_bolt = _to_float(bolt.get("row"))
                per_bolt.append(
                    {
                        "row": int(row_bolt) if row_bolt is not None else 0,
                        "tag": _format_text(bolt.get("tag")),
                        "dx": dx,
                        "dy": dy,
                        "d": d,
                    }
                )

            d_max = max((item["d"] for item in per_bolt), default=0.0)
            if d_max > 1e-12:
                for item in per_bolt:
                    delta = delta_max * float(item["d"]) / d_max
                    phi = (1.0 - math.exp(-mu * delta)) ** lambda_exp
                    item["delta"] = delta
                    item["phi"] = phi
            else:
                for item in per_bolt:
                    item["delta"] = 0.0
                    item["phi"] = 0.0

            sum_phi_d = sum(float(item.get("phi") or 0.0) * float(item["d"]) for item in per_bolt)
            m_p = (vx_kip * r_oy - vy_kip * r_ox) if (r_ox is not None and r_oy is not None) else None
            r_max = (m_p / sum_phi_d) if (m_p is not None and abs(sum_phi_d) > 1e-12) else None
            c_coeff = (sum_phi_d / r_o) if (r_o is not None and abs(r_o) > 1e-12) else None

            for item in per_bolt:
                d = float(item["d"])
                phi = float(item.get("phi") or 0.0)
                if r_max is None:
                    r_i = None
                    r_x = None
                    r_y = None
                else:
                    r_i = phi * r_max
                    if d > 1e-12:
                        r_x = -r_i * float(item["dy"]) / d
                        r_y = r_i * float(item["dx"]) / d
                    else:
                        r_x = 0.0
                        r_y = 0.0
                item["r_i"] = r_i
                item["r_x"] = r_x
                item["r_y"] = r_y
                icr_bolt_rows_a.append(
                    [
                        _num(iteration),
                        item.get("row"),
                        item["tag"],
                        _num(item["dx"]),
                        _num(item["dy"]),
                        _num(item["d"]),
                        _num(item.get("delta")),
                    ]
                )
                icr_bolt_rows_b.append(
                    [
                        _num(iteration),
                        item.get("row"),
                        item["tag"],
                        _num(item.get("phi")),
                        _num(item.get("r_i")),
                        _num(item.get("r_x")),
                        _num(item.get("r_y")),
                    ]
                )

            icr_iter_rows_a.append([_num(iteration), _num(x_icr), _num(y_icr), _num(it.get("residual_fx")), _num(it.get("residual_fy")), _num(it.get("residual_norm"))])
            icr_iter_rows_b.append([_num(iteration), _num(d_max), _num(sum_phi_d), _num(r_max), _num(c_coeff), _num(m_p)])

    lines: list[str] = [
        "# Reporte Metodos Pernos 1 (Splice)",
        "",
        "## 1. Informacion General",
        "",
        f"- Proyecto: `{result.project_id}`",
        f"- Caso: `{result.case_id}`",
        f"- Metodo seleccionado en JSON: `{_format_text(report.get('method_selected'))}`",
        "",
        "### 1.1 Variables de carga",
        "",
    ]

    px = report.get("px") if isinstance(report.get("px"), dict) else {}
    py = report.get("py") if isinstance(report.get("py"), dict) else {}
    ex = report.get("ex") if isinstance(report.get("ex"), dict) else {}
    ey = report.get("ey") if isinstance(report.get("ey"), dict) else {}
    mz = report.get("mz") if isinstance(report.get("mz"), dict) else {}

    lines.extend(
        [
            "- Ecuacion base: `Muz_blt_web = Vu2_sp*ex_blt_web - Pu_sp*ey_blt_web`",
            f"- Pu_sp: `{_format_text(px.get('value'))} {_format_text(px.get('unit'))}` (origen: `loads.Pu_sp`)",
            f"- Vu2_sp: `{_format_text(py.get('value'))} {_format_text(py.get('unit'))}` (origen: `loads.Vu2_sp`)",
            f"- ex_blt_web: `{_format_text(ex.get('value'))} {_format_text(ex.get('unit'))}` (origen: `formula splice`)",
            f"- ey_blt_web: `{_format_text(ey.get('value'))} {_format_text(ey.get('unit'))}` (origen: `input ey`)",
            f"- Muz_blt_web: `{_format_text(mz.get('value'))} {_format_text(mz.get('unit'))}`",
        ]
    )

    lines.extend(["", "## 2. Geometria de pernos derivada", ""])
    for variable, formula, value, unit in geometry_rows:
        lines.append(f"- {variable}: `{value} {unit}` con `{formula}`")

    lines.extend(["", "## 3. Geometria del grupo de pernos", ""])
    if not bolts_rows:
        lines.append("- No hay pernos activos reportados.")
    else:
        for row_n, tag, x_val, y_val, dx_val, dy_val, r_val in bolts_rows:
            lines.append(
                f"- Perno `{tag}`: x_{row_n}_blt_web=`{x_val} in`, y_{row_n}_blt_web=`{y_val} in`, "
                f"dx_cg_{row_n}_blt_web=`{dx_val} in`, dy_cg_{row_n}_blt_web=`{dy_val} in`, r_cg_{row_n}_blt_web=`{r_val} in`"
            )

    lines.extend(["", "## 4. Resumen global por metodo", ""])
    for method, applicable, status, demand, capacity, dcr in summary_rows:
        lines.append(
            f"- Metodo `{method}`: applicable=`{applicable}`, estado=`{status}`, demanda=`{demand} kip`, capacidad=`{capacity} kip`, DCR=`{dcr}`"
        )

    lines.extend(["", "## 5. Elastic Method - Superposition", ""])
    lines.append("")
    lines.append("### 5.1 Formulacion")
    lines.extend(
        [
            "- Ecuaciones:",
            "- `Ru_i_blt_web_v2 = -Pu_sp/n_blt_web`",
            "- `Ru_i_blt_web_v3 = -Vu2_sp/n_blt_web`",
            "- `Ru_mz_i_blt_web_v2 = Muz_blt_web*dy_cg_i_blt_web/J_blt_web`",
            "- `Ru_mz_i_blt_web_v3 = -Muz_blt_web*dx_cg_i_blt_web/J_blt_web`",
            "- `Ru_i_blt_web = sqrt((Ru_i_blt_web_v2+Ru_mz_i_blt_web_v2)^2 + (Ru_i_blt_web_v3+Ru_mz_i_blt_web_v3)^2)`",
            "- Geometria por perno:",
        ]
    )
    lines.append("")
    lines.append("### 5.2 Geometria por perno")
    if not super_geom_rows:
        lines.append("- Sin datos de geometria para superposition.")
    else:
        for row_n, tag, x_val, y_val, dx_val, dy_val, d_val in super_geom_rows:
            lines.append(
                f"- `{tag}`: x_{row_n}_blt_web=`{x_val}`, y_{row_n}_blt_web=`{y_val}`, "
                f"dx_cg_{row_n}_blt_web=`{dx_val}`, dy_cg_{row_n}_blt_web=`{dy_val}`, r_cg_{row_n}_blt_web=`{d_val}`"
            )
    lines.append("")
    lines.append("### 5.3 Fuerzas por perno")
    if not super_force_rows:
        lines.append("- Sin datos de fuerzas para superposition.")
    else:
        for row_n, tag, fx_dir, fy_dir, fx_t, fy_t, r_val in super_force_rows:
            lines.append(
                f"- `{tag}`: Ru_dir_{row_n}_blt_web_v2=`{fx_dir}`, Ru_dir_{row_n}_blt_web_v3=`{fy_dir}`, "
                f"Ru_rot_{row_n}_blt_web_v2=`{fx_t}`, Ru_rot_{row_n}_blt_web_v3=`{fy_t}`, Ru_{row_n}_blt_web=`{r_val}`"
            )
    lines.append("")
    lines.append("### 5.4 Resumen de fuerzas en pernos")
    if not super_summary_rows:
        lines.append("- Sin resumen de fuerzas resultantes para superposition.")
    else:
        for row_n, tag, fx_total, fy_total, r_val in super_summary_rows:
            lines.append(
                f"- `{tag}`: Ru_{row_n}_blt_web_v2=`{fx_total}`, Ru_{row_n}_blt_web_v3=`{fy_total}`, Ru_{row_n}_blt_web=`{r_val}`"
            )

    lines.extend(["", "## 6. Elastic Method - Center of Rotation (ECR)", ""])
    lines.append("")
    lines.append("### 6.1 Formulacion")
    lines.extend(
        [
            "- Ecuaciones:",
            "- `dx_ecr_i_blt_web = x_i_blt_web - x_ecr_blt_web`",
            "- `dy_ecr_i_blt_web = y_i_blt_web - y_ecr_blt_web`",
            "- `r_ecr_i_blt_web = sqrt(dx_ecr_i_blt_web^2 + dy_ecr_i_blt_web^2)`",
            "- `Ru_i_blt_web_v2 = k_ecr_blt_web*dy_ecr_i_blt_web`",
            "- `Ru_i_blt_web_v3 = -k_ecr_blt_web*dx_ecr_i_blt_web`",
            "- Geometria por perno respecto al ECR:",
        ]
    )
    lines.append("")
    lines.append("### 6.2 Calculo de ax, ay y coordenadas ECR")
    lines.extend(
        [
            "- Ecuaciones:",
            "- `ax_blt_web = (Vu2_sp*J_blt_web)/(n_blt_web*Muz_blt_web)`",
            "- `ay_blt_web = (Pu_sp*J_blt_web)/(n_blt_web*Muz_blt_web)`",
            "- `x_ecr_blt_web = x_cg_blt_web + ax_blt_web`",
            "- `y_ecr_blt_web = y_cg_blt_web + ay_blt_web`",
            f"- Pu_sp (componente aplicada en direccion v2): `{_num(vx_kip)} kip`",
            f"- Vu2_sp (componente aplicada en direccion v3): `{_num(vy_kip)} kip`",
            f"- n_blt_web: `{_num(bolt_count)}`",
            f"- J_blt_web: `{_num(ip_in2)} in2`",
            f"- Muz_blt_web: `{_num(mz_kip_in)} kip-in`",
            f"- ax_blt_web: `{_num(ax_ecr)} in`",
            f"- ay_blt_web: `{_num(ay_ecr)} in`",
            f"- x_ecr_blt_web: `{_num(center_x_ecr)} in`",
            f"- y_ecr_blt_web: `{_num(center_y_ecr)} in`",
        ]
    )
    lines.append("")
    lines.append("### 6.3 Geometria por perno respecto al ECR")
    if not ecr_geom_rows:
        lines.append("- Sin datos de geometria para ECR.")
    else:
        for row_n, tag, x_val, y_val, dx_val, dy_val, d_val in ecr_geom_rows:
            lines.append(
                f"- `{tag}`: x_{row_n}_blt_web=`{x_val}`, y_{row_n}_blt_web=`{y_val}`, "
                f"dx_ecr_{row_n}_blt_web=`{dx_val}`, dy_ecr_{row_n}_blt_web=`{dy_val}`, r_ecr_{row_n}_blt_web=`{d_val}`"
            )
    lines.append("")
    lines.append("### 6.4 Fuerzas por perno en ECR")
    if not ecr_force_rows:
        lines.append("- Sin datos de fuerzas para ECR.")
    else:
        for row_n, tag, fx_val, fy_val, r_val, x_ecr, y_ecr in ecr_force_rows:
            lines.append(
                f"- `{tag}`: Ru_{row_n}_blt_web_v2=`{fx_val}`, Ru_{row_n}_blt_web_v3=`{fy_val}`, Ru_{row_n}_blt_web=`{r_val}`, "
                f"x_ecr_blt_web=`{x_ecr}`, y_ecr_blt_web=`{y_ecr}`"
            )
    lines.append("")
    lines.append("### 6.5 Resumen de fuerzas en pernos")
    if not ecr_summary_rows:
        lines.append("- Sin resumen de fuerzas resultantes para ECR.")
    else:
        for row_n, tag, fx_total, fy_total, r_val in ecr_summary_rows:
            lines.append(
                f"- `{tag}`: Ru_{row_n}_blt_web_v2=`{fx_total}`, Ru_{row_n}_blt_web_v3=`{fy_total}`, Ru_{row_n}_blt_web=`{r_val}`"
            )

    lines.extend(["", "## 7. Instant Center of Rotation (ICR)", ""])
    lines.append("")
    lines.append("### 7.1 Formulacion")
    lines.extend(
        [
            "- Ecuaciones:",
            "- `delta_i_blt_web = (r_icr_i_blt_web/dmax_icr_blt_web)*delta_max_blt_web`",
            "- `phi_i_blt_web = (1-exp(-mu_blt_web*delta_i_blt_web))^lambda_blt_web`",
            "- `sum(phi_i_blt_web*r_icr_i_blt_web)`",
            "- `Rult_blt_web = M_icr_blt_web/sum(phi_i_blt_web*r_icr_i_blt_web)`",
            "- Coordenadas ICR:",
            f"- `x_icr_final_blt_web = {_num(icr_x_final)} in`",
            f"- `y_icr_final_blt_web = {_num(icr_y_final)} in`",
            "- Coordenadas por iteracion (`estimacion -> resultado`):",
        ]
    )
    if not icr_coord_rows:
        lines.append("- Sin coordenadas iterativas ICR reportadas.")
    else:
        for iter_idx, x_est, y_est, x_after, y_after in icr_coord_rows:
            lines.append(
                f"- Iter `{iter_idx}`: estimacion=`({x_est}, {y_est}) in` -> resultado=`({x_after}, {y_after}) in`"
            )
    lines.extend(
        [
            "- Iteraciones del ICR:",
        ]
    )
    lines.append("")
    lines.append("### 7.2 Iteraciones globales (residuales)")
    if not icr_iter_rows_a:
        lines.append("- Sin iteraciones ICR.")
    else:
        for it, x_icr, y_icr, rfx, rfy, rnorm in icr_iter_rows_a:
            lines.append(
                f"- Iter `{it}`: x_icr_blt_web=`{x_icr}`, y_icr_blt_web=`{y_icr}`, "
                f"res_Ru_blt_web_v2=`{rfx}`, res_Ru_blt_web_v3=`{rfy}`, res_norm_blt_web=`{rnorm}`"
            )
    lines.append("")
    lines.append("### 7.3 Parametros auxiliares por iteracion")
    if not icr_iter_rows_b:
        lines.append("- Sin parametros auxiliares ICR.")
    else:
        for it, dmax_val, sum_phi_d, rmax_val, c_val, mp_val in icr_iter_rows_b:
            lines.append(
                f"- Iter `{it}`: dmax_icr_blt_web=`{dmax_val}`, sum(phi_i_blt_web*r_icr_i_blt_web)=`{sum_phi_d}`, "
                f"Rult_blt_web=`{rmax_val}`, Cu_blt_web=`{c_val}`, M_icr_blt_web=`{mp_val}`"
            )

    lines.extend(["", "### 7.4 Bolt Detail ICR por iteracion", ""])
    if not icr_bolt_rows_a and not icr_bolt_rows_b:
        lines.append("- Sin datos de detalle por iteracion en ICR.")
    else:
        cinematic_by_iter: dict[str, list[tuple[object, object, object, object, object]]] = {}
        forces_by_iter: dict[str, list[tuple[object, object, object, object, object]]] = {}

        for it, row_n, perno, dx_val, dy_val, d_val, delta_val in icr_bolt_rows_a:
            iter_key = str(it)
            cinematic_by_iter.setdefault(iter_key, []).append((row_n, perno, dx_val, dy_val, d_val, delta_val))

        for it, row_n, perno, phi_val, ri_val, rx_val, ry_val in icr_bolt_rows_b:
            iter_key = str(it)
            forces_by_iter.setdefault(iter_key, []).append((row_n, perno, phi_val, ri_val, rx_val, ry_val))

        iter_keys = sorted(
            set(cinematic_by_iter.keys()) | set(forces_by_iter.keys()),
            key=lambda raw: float(raw) if str(raw).replace(".", "", 1).isdigit() else 1e12,
        )

        for idx, iter_key in enumerate(iter_keys, start=1):
            lines.append("")
            lines.append(f"#### 7.4.{idx} Iteracion {iter_key}")
            lines.append("")
            lines.append("- Cinematica por perno:")
            cinematic_rows = cinematic_by_iter.get(iter_key, [])
            if not cinematic_rows:
                lines.append("- Sin datos cinematicos para esta iteracion.")
            else:
                for row_n, perno, dx_val, dy_val, d_val, delta_val in cinematic_rows:
                    lines.append(
                        f"- `{perno}`: dx_icr_{row_n}_blt_web=`{dx_val}`, dy_icr_{row_n}_blt_web=`{dy_val}`, "
                        f"r_icr_{row_n}_blt_web=`{d_val}`, delta_{row_n}_blt_web=`{delta_val}`"
                    )

            lines.append("- Fuerzas por perno:")
            force_rows = forces_by_iter.get(iter_key, [])
            if not force_rows:
                lines.append("- Sin datos de fuerzas para esta iteracion.")
            else:
                for row_n, perno, phi_val, ri_val, rx_val, ry_val in force_rows:
                    lines.append(
                        f"- `{perno}`: phi_{row_n}_blt_web=`{phi_val}`, Ru_{row_n}_blt_web=`{ri_val}`, "
                        f"Ru_{row_n}_blt_web_v2=`{rx_val}`, Ru_{row_n}_blt_web_v3=`{ry_val}`"
                    )

    rendered = "\n".join(lines)
    return _normalize_markdown_spacing(rendered)

def write_splice_methods_table_markdown(result: DetailedRunResult, target_dir: str | Path) -> Path | None:
    if str(result.connection_family).strip().lower() != "fully_restrained_moment":
        return None
    if str(result.connection_type).strip().lower() != "bbmb_splice":
        return None
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "Detalle_Ru_blt_web_v23.md"
    rendered = render_splice_methods_table_markdown(result).rstrip("\n") + "\n"
    target.write_text(rendered, encoding="utf-8")
    return target


