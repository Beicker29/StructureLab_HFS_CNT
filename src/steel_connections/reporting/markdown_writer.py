from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any

from steel_connections.codes.engineering.flexure import (
    compute_column_flange_local_bending_strength,
    compute_dcr,
)
from steel_connections.codes.engineering.shear import compute_beam_web_shear_yielding_strength
from steel_connections.codes.engineering.weld import (
    WeldFillet,
    compute_fillet_weld_check_with_kds,
    compute_effective_web_weld_length,
    compute_plate_tension_demand_from_yielding,
)
from steel_connections.data.materials_repository import (
    get_hrs_steel_properties,
    get_plate_steel_properties,
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


def _format_indexed_quantity_series(value: object, *, index_key: str = "j", quantity_key: str = "x") -> str:
    if not isinstance(value, list):
        return "n/a"
    parts: list[str] = []
    for idx, item in enumerate(value):
        if isinstance(item, dict):
            j_raw = item.get(index_key, idx)
            q_raw = item.get(quantity_key, item)
        else:
            j_raw = idx
            q_raw = item
        q_text = _format_quantity(q_raw)
        if q_text == "n/a":
            continue
        parts.append(f"{index_key}={_format_text(j_raw)}: {q_text}")
    return "; ".join(parts) if parts else "n/a"


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
    if value in {"NOT_APPLICABLE", "NO_APLICA", "NO APLICA", "NA"}:
        return "🟠 No aplica (cumple)"
    if value in {"NO_OK", "FAIL", "ERROR", "NOT_IMPLEMENTED"}:
        return "🔴 No cumple"
    return _format_text(raw_result)


def _render_result_plain_es(raw_result: object) -> str:
    value = _format_text(raw_result).strip().upper()
    if value in {"OK", "PASS", "CUMPLE"}:
        return "🟢 Cumple"
    if value in {"NOT_APPLICABLE", "NO_APLICA", "NO APLICA", "NA"}:
        return "🟠 No aplica (cumple)"
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


def _collect_step_1_inputs(result: DetailedRunResult) -> dict:
    merged: dict = {}
    for check in result.checks:
        if ".06.3." not in check.rule_id:
            continue
        payload = check.calculation_memory.inputs
        if not isinstance(payload, dict):
            continue
        for key, value in payload.items():
            if key not in merged:
                merged[key] = value
                continue
            current = merged.get(key)
            if current is None and value is not None:
                merged[key] = value
    return merged

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


def _collect_step_21_5_1_column_panel_zone_shear_wpzs(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        rule_id = str(check.rule_id).lower()
        clause = str(check.clause).lower()
        name = str(check.name).lower()
        if (
            ".step21_5_1_column_panel_zone_shear_wpzs" not in rule_id
            and "panel_zone" not in rule_id
            and "wpzs" not in rule_id
            and "j10.6" not in clause
            and "panel-zone" not in name
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


def _dedupe_markdown_headings(text: str) -> str:
    lines = text.splitlines()
    seen: dict[tuple[int, str], int] = {}
    deduped: list[str] = []
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    for line in lines:
        match = heading_pattern.match(line)
        if not match:
            deduped.append(line)
            continue
        hashes, title = match.group(1), match.group(2).strip()
        key = (len(hashes), title.lower())
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            line = f"{hashes} {title} [{seen[key]}]"
        deduped.append(line)
    return "\n".join(deduped)


def _normalize_memory_spanish_labels(text: str) -> str:
    heading_replacements = {
        "Revision": "Revisión",
        "revision": "revisión",
        "Calculo": "Cálculo",
        "calculo": "cálculo",
        "tecnicas": "técnicas",
        "tecnica": "técnica",
        "geometricas": "geométricas",
        "geometrica": "geométrica",
        "mecanicas": "mecánicas",
        "mecanica": "mecánica",
        "precalificacion": "precalificación",
        "maximo": "máximo",
        "rotula": "rótula",
        "plastica": "plástica",
        "flexion": "flexión",
        "traccion": "tracción",
        "compresion": "compresión",
        "conexion": "conexión",
        "Ambito": "Ámbito",
        "ambito": "ámbito",
    }

    def _apply_heading_accents(line: str) -> str:
        updated = line
        for old, new in heading_replacements.items():
            updated = updated.replace(old, new)
        return updated

    normalized_lines: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            line = _apply_heading_accents(line)
        if line.startswith("- Ambito:"):
            line = line.replace("- Ambito:", "- Ámbito:")
        if line == "No hay notas tecnicas disponibles para este caso.":
            line = "No hay notas técnicas disponibles para este caso."
        normalized_lines.append(line)
    return "\n".join(normalized_lines)


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
    grouped: dict[str, list[dict]] = {}
    scope_order: list[str] = []
    for item in notes:
        note_id = _format_text(item.get("id"))
        if note_id == "section_6_7.beam_flange_to_end_plate_weld_note":
            continue
        scope = _format_text(item.get("scope")).upper()
        if scope not in grouped:
            grouped[scope] = []
            scope_order.append(scope)
        grouped[scope].append(item)

    def _scope_sort_key(scope: str) -> tuple[int, int, int]:
        scope_upper = scope.upper()
        if scope_upper == "CONTINUITY_PLATE_COL":
            return (2, 99, 10)
        if scope_upper == "CONTINUITY_PLATE_COL":
            return (2, 98, 10)
        if scope_upper == "DOUBLER_PLATE_COL":
            return (2, 99, 9)
        if scope_upper.startswith("WELD_"):
            parts = scope_upper.split("_")
            try:
                weld_idx = int(parts[1])
            except (IndexError, ValueError):
                weld_idx = 99
            side_rank = 9
            if scope_upper.endswith("_VGDER"):
                side_rank = 1
            elif scope_upper.endswith("_VGIZQ"):
                side_rank = 2
            elif scope_upper.endswith("_COL"):
                side_rank = 3
            return (2, weld_idx, side_rank)
        if scope in scope_order:
            return (1, scope_order.index(scope), 0)
        return (3, 999, 0)

    ordered_scopes = sorted(scope_order, key=_scope_sort_key)

    def _side_from_scope(scope: str) -> str:
        scope_upper = scope.upper()
        if scope_upper.endswith("_VGIZQ") or scope_upper.endswith("_IZQ") or "VGIZQ" in scope_upper:
            return "vg_izq"
        if scope_upper.endswith("_VGDER") or scope_upper.endswith("_DER") or "VGDER" in scope_upper:
            return "vg_der"
        return "otros"

    scopes_by_side: dict[str, list[str]] = {"vg_izq": [], "vg_der": [], "otros": []}
    for scope in ordered_scopes:
        scopes_by_side[_side_from_scope(scope)].append(scope)

    side_sections: list[tuple[str, str]] = []
    if scopes_by_side["vg_izq"]:
        side_sections.append(("vg_izq", "Notas tecnicas (vg_izq)"))
    if scopes_by_side["vg_der"]:
        side_sections.append(("vg_der", "Notas tecnicas (vg_der)"))
    if scopes_by_side["otros"]:
        side_sections.append(("otros", "Notas tecnicas (otros)"))
    lines: list[str] = []

    for section_offset, (side_key, side_title) in enumerate(side_sections, start=1):
        lines.append(f"### 1.{section_offset} {side_title}")
        lines.append("")
        local_note_index = 1
        side_items: list[tuple[str, dict]] = []
        for scope in scopes_by_side[side_key]:
            for item in grouped[scope]:
                side_items.append((scope, item))
        for scope, item in side_items:
            note_id = _format_text(item.get("id"))
            description = _translate_text_es(item.get("description"))
            clause = _render_clause_text(
                item.get("clause"),
                item.get("source_document"),
                item.get("rule_id"),
            )
            note_label = f"1.{section_offset}.{local_note_index}"
            local_note_index += 1
            lines.append(f"#### {note_label} Nota tecnica - {description}")
            lines.append("")
            lines.append(f"- Ambito: `{scope}`")
            lines.append(f"- Clausula: `{clause}`")
            requirement = _translate_text_es(item.get("requirement"))
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
                if formula != "n/a":
                    lines.append(f"- Formula: `{formula}`")
                if note_id == "section_6_3.end_plate_stiffener_geometry_note":
                    h_pest_vgder = _format_quantity(item.get("h_pest_vgder"))
                    l_pest_vgder = _format_quantity(item.get("l_pest_vgder"))
                    ed_pest_vgder = _format_quantity(item.get("ed_pest_vgder"))
                    lines.append(f"- h_pest_vgder: `{h_pest_vgder}`")
                    lines.append(f"- L_pest_vgder: `{l_pest_vgder}`")
                    lines.append(f"- edge_detailing (Ed_pest_vgder): `{ed_pest_vgder}`")
                else:
                    h_pest_vgizq = _format_quantity(item.get("h_pest_vgizq"))
                    l_pest_vgizq = _format_quantity(item.get("l_pest_vgizq"))
                    ed_pest_vgizq = _format_quantity(item.get("ed_pest_vgizq"))
                    lines.append(f"- h_pest_vgizq: `{h_pest_vgizq}`")
                    lines.append(f"- L_pest_vgizq: `{l_pest_vgizq}`")
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
                if h3 != "n/a":
                    lines.append(f"- h3_vgder: `{h3}`")
                if h4 != "n/a":
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
                if h3 != "n/a":
                    lines.append(f"- h3_vgizq: `{h3}`")
                if h4 != "n/a":
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


def _render_step_notes_grouped_by_scope(notes: list[dict], *, chapter_number: int) -> str:
    if not notes:
        return ""
    grouped: dict[str, list[dict]] = {}
    scope_order: list[str] = []
    for item in notes:
        note_id = _format_text(item.get("id"))
        if note_id == "section_6_7.beam_flange_to_end_plate_weld_note":
            continue
        scope = _format_text(item.get("scope")).upper()
        if scope not in grouped:
            grouped[scope] = []
            scope_order.append(scope)
        grouped[scope].append(item)

    def _scope_sort_key(scope: str) -> tuple[int, int, int]:
        scope_upper = scope.upper()
        if scope_upper == "CONTINUITY_PLATE_COL":
            return (2, 98, 10)
        if scope_upper == "DOUBLER_PLATE_COL":
            return (2, 99, 9)
        if scope_upper.startswith("WELD_"):
            parts = scope_upper.split("_")
            try:
                weld_idx = int(parts[1])
            except (IndexError, ValueError):
                weld_idx = 99
            side_rank = 9
            if scope_upper.endswith("_VGDER"):
                side_rank = 1
            elif scope_upper.endswith("_VGIZQ"):
                side_rank = 2
            elif scope_upper.endswith("_COL"):
                side_rank = 3
            return (2, weld_idx, side_rank)
        if scope in scope_order:
            return (1, scope_order.index(scope), 0)
        return (3, 999, 0)

    ordered_scopes = sorted(scope_order, key=_scope_sort_key)
    lines: list[str] = []
    for section_offset, scope in enumerate(ordered_scopes, start=1):
        lines.append(f"### {chapter_number}.{section_offset} Ámbito `{scope}`")
        lines.append("")
        local_note_index = 1
        for item in grouped[scope]:
            note_id = _format_text(item.get("id"))
            description = _translate_text_es(item.get("description"))
            clause = _render_clause_text(
                item.get("clause"),
                item.get("source_document"),
                item.get("rule_id"),
            )
            note_label = f"{chapter_number}.{section_offset}.{local_note_index}"
            local_note_index += 1
            lines.append(f"#### {note_label} Nota tecnica - {description}")
            lines.append("")
            lines.append(f"- Ambito: `{scope}`")
            lines.append(f"- Clausula: `{clause}`")
            requirement = _translate_text_es(item.get("requirement"))
            if requirement != "n/a":
                lines.append(f"- Requisito: `{requirement}`")
            formula = _format_text(item.get("formula"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
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
        "## Paso 4 - Momento probable maximo en rotula plastica (Mpr)",
        "",
        "Calculo de momento probable por lado usando `Mpr = Cpr * Ry * Fy * Ze` (Ze = Zx del catalogo).",
        "",
        "### 4.1 Calculo de Mpr para viga izquierda",
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
        "### 4.2 Calculo de Mpr para viga derecha",
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
        "## Paso 5 - Distancia de rotula plastica desde la cara de la columna (Sh)",
        "",
        "### 5.1 Calculo de Sh para viga izquierda",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Tipo de conexion: `{ctype}`",
        "- Ecuacion: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`",
        f"- d_vgizq: `{_format_quantity(inputs.get('d_vgizq'))}`",
        f"- bf_vgizq: `{_format_quantity(inputs.get('bf_vgizq'))}`",
        f"- Sh_vgizq: `{sh_izq}`",
        "",
        "### 5.2 Calculo de Sh para viga derecha",
        "",
        f"- Clausula: `{clause_text}`",
        f"- Tipo de conexion: `{ctype}`",
        "- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`",
        f"- d_vgder: `{_format_quantity(inputs.get('d_vgder'))}`",
        f"- bf_vgder: `{_format_quantity(inputs.get('bf_vgder'))}`",
        f"- Sh_vgder: `{sh_der}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_4_vh(step_4: dict) -> str:
    inputs = step_4.get("inputs", {})
    inter = step_4.get("intermediates", {})
    beam_connection_sides = _format_text(inputs.get("beam_connection_sides"))
    sides = ["izq", "der"] if beam_connection_sides == "both_sides" else ["der"]
    lines = [
        "## Paso 6 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)",
        "",
        "Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.",
        "",
    ]
    clause_text = _render_clause_text(step_4.get("clause"), step_4.get("source_document"), step_4.get("rule_id"))
    for side in sides:
        side_suffix = f"vg{side}"
        subtitle = "### 6.1 Calculo de cortante probable para viga izquierda" if side == "izq" else "### 6.2 Calculo de cortante probable para viga derecha"
        lines.extend(
            [
                subtitle,
                "",
                f"- Clausula: `{clause_text}`",
                f"- Ecuacion: `Vh_{side_suffix}_max = 2*Mpr_{side_suffix}/Llb_{side_suffix} + Vg_{side_suffix}; Vh_{side_suffix}_min = 2*Mpr_{side_suffix}/Llb_{side_suffix} - Vg_{side_suffix}`",
                f"- Mpr_{side_suffix}: `{_format_scalar_with_unit(inter.get(f'mpr_{side}'), 'kN-mm')}`",
                f"- Llb_{side_suffix}: `{_format_quantity(inputs.get(f'lh_{side}'))}`",
                f"- Vg_{side_suffix}: `{_format_quantity(inputs.get(f'vgravity_between_hinges_{side}'))}`",
                f"- Vh_{side_suffix}_max: `{_format_scalar_with_unit(inter.get(f'vh_{side}max'), 'kN')}`",
                f"- Vh_{side_suffix}_min: `{_format_scalar_with_unit(inter.get(f'vh_{side}min'), 'kN')}`",
                f"- Vhmax_{side_suffix} adoptado: `{_format_scalar_with_unit(inter.get(f'vh_{side}max_adopted'), 'kN')}`",
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
        "## Paso 7 - Momento Probable En Cara De Columna (Mfmax, Mfmin)",
        "",
        "Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.",
        "",
    ]
    for side in sides:
        side_suffix = f"vg{side}"
        subtitle = "### 7.1 Calculo de momento probable en cara de columna para viga izquierda" if side == "izq" else "### 7.2 Calculo de momento probable en cara de columna para viga derecha"
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
                f"- Fnv_b_vgizq: `{_format_quantity(inputs.get('fnv_b_vgizq'))}`",
                f"- thread_b_vgizq: `{_format_text(inputs.get('thread_b_vgizq'))}`",
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
    connection_type: str | None = None,
) -> str:
    connection_type_norm = str(connection_type or "").strip().lower()
    show_72_block = connection_type_norm == "bueep_4e"
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
    if show_72_block and step_7_2_1 is not None:
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
                f"- Mf_vgizq_critico: `{_format_quantity(inputs.get('mf_vgizq_critico'))}`",
                f"- Ru_pe_v1_vgizq: `{_format_quantity(step_7_2_1.get('demand'))}`",
                f"- phi*Rn_pe_v1_vgizq: `{_format_quantity(step_7_2_1.get('capacity'))}`",
                f"- DCR_pe_v1_vgizq: `{_format_text(step_7_2_1.get('dcr'))}`",
                f"- Resultado: `{_render_result_plain_es(step_7_2_1.get('status'))}`",
                "",
            ]
        )
    if show_72_block and step_7_2_2 is not None:
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
        rule_id = str(step_7_3_1.get("rule_id") or "").lower()
        show_pb = "bseep_8es" in rule_id and inputs.get("pb_pe_vgizq") is not None
        detail_lines = [
            "#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno",
            "",
            f"- Clausula: `{_render_clause_text(step_7_3_1.get('clause'), step_7_3_1.get('source_document'), step_7_3_1.get('rule_id'))}`",
            f"- Ecuacion: `{_format_text(step_7_3_1.get('equation'))}`",
            f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
            f"- Vh_vgizq_critico: `{_format_quantity(inputs.get('vh_vgizq_critico'))}`",
            f"- n_b_vgizq: `{_format_text(inputs.get('n_b_vgizq'))}`",
        ]
        if show_pb:
            detail_lines.append(f"- pb_pe_vgizq: `{_format_quantity(inputs.get('pb_pe_vgizq'))}`")
        detail_lines.extend(
            [
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
        lines.extend(detail_lines)
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
            "- l_w1_vgizq (longitud soldadura calculada): `l_w1_vgizq = h_pest_vgizq - 2*L_gap_w1_vgizq - c_pest_vgizq`",
            f"- Fys_pest_vgizq: `{_format_quantity(inputs.get('fys_pest_vgizq'))}`",
            f"- t_pest_vgizq: `{_format_quantity(inputs.get('t_pest_vgizq'))}`",
            f"- h_pest_vgizq: `{_format_quantity(inputs.get('h_pest_vgizq'))}`",
            f"- L_gap_w1_vgizq: `{_format_quantity(inputs.get('L_gap_w1_vgizq'))}`",
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
            "- l_w2_vgizq (longitud soldadura calculada): `l_w2_vgizq = L_pest_vgizq - 2*L_gap_w2_vgizq - c_pest_vgizq`",
            f"- Fys_pest_vgizq: `{_format_quantity(inputs.get('fys_pest_vgizq') or inputs.get('fys'))}`",
            f"- t_pest_vgizq: `{_format_quantity(inputs.get('t_pest_vgizq') or inputs.get('ts'))}`",
            f"- h_pest_vgizq: `{_format_quantity(inputs.get('h_pest_vgizq') or inputs.get('hst'))}`",
            f"- L_pest_vgizq: `{_format_quantity(inputs.get('l_pest_vgizq') or inputs.get('lst'))}`",
            f"- L_gap_w2_vgizq: `{_format_quantity(inputs.get('L_gap_w2_vgizq'))}`",
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
    step_11_design_factors = step_11_ctx.get("design_factors", {}) if isinstance(step_11_ctx, dict) else {}
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
    phi_raw = step_11_design_factors.get("phi")
    try:
        phi = float(phi_raw)
    except (TypeError, ValueError):
        phi = None

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
        and phi is not None
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
    if has_continuity_plate and ru_cf_v2_col_q is not None and phi_rn_cf_v2_col_q is not None:
        ru_cf_v2_col_q = Quantity(
            value=min(ru_cf_v2_col_q.value, phi_rn_cf_v2_col_q.value),
            unit=ru_cf_v2_col_q.unit,
        )
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
        "- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`",
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
        f"- Ru_cw_v2_col_vgizq: `{_format_quantity(step_13_1_1.get('demand'))}`",
        f"- phi*Rn_cw_v2_col_vgizq: `{_format_quantity(step_13_1_1.get('capacity'))}`",
        f"- DCR_cw_v2_col_vgizq: `{_format_text(step_13_1_1.get('dcr'))}`",
        f"- Resultado: `{_render_result_plain_es(step_13_1_1.get('status'))}`",
        "",
    ]

    def _render_wlc_rn_expression(case_key: object) -> str:
        case_txt = _format_text(case_key)
        if case_txt == "eq_6_7_19":
            return (
                "0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * "
                "sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]"
            )
        if case_txt == "eq_6_7_20":
            return (
                "0.40*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * "
                "sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-20]"
            )
        if case_txt == "eq_6_7_21":
            return (
                "0.40*tw_col^2 * [1 + (4*lb_col/d_col - 0.2)*(tw_col/tf_col)^1.5] * "
                "sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-21]"
            )
        return "n/a"

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
                f"- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; Rn_cw_v2_col_vgizq = {_render_wlc_rn_expression(wlc_inter.get('case'))}; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_cw_v2_col_vgizq; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`",
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
                    "### 1.1.1 Resumen de geometria",
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


def _render_splice_step_2_method_block(step2: dict | None, *, chapter_number: int | None = None) -> str:
    heading = "### Punto 2 - Metodo ICR/Elastic"
    if chapter_number is not None:
        heading = f"### {chapter_number}.1 Metodo ICR/Elastic"
    if not isinstance(step2, dict):
        return "\n".join(
            [
                heading,
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
    mz = _format_quantity(report.get("mz"))
    demand = _format_quantity(report.get("demand"))
    dcr = _format_text(report.get("dcr"))
    cu = _format_text(report.get("cu"))
    icr_compare = _format_quantity(report.get("icr_compare_capacity"))
    final_residual = _format_text(report.get("final_residual"))
    n_iterations = _format_text(report.get("n_iterations"))
    ru_crit = "n/a"
    ru_crit_tag = "n/a"
    ru_x_max = "n/a"
    ru_x_max_tag = "n/a"
    ru_y_max = "n/a"
    ru_y_max_tag = "n/a"
    ru_crit_var = "n/a"
    ru_x_var = "n/a"
    ru_y_var = "n/a"

    def _tag_to_row(tag: str) -> str:
        compact = "".join(ch for ch in str(tag) if ch.isdigit())
        return compact if compact else "?"
    methods_summary = report.get("methods_summary")
    if isinstance(methods_summary, list):
        selected_method = _format_text(report.get("method_selected")).strip().lower()
        active_summary = next(
            (
                item
                for item in methods_summary
                if isinstance(item, dict) and _format_text(item.get("method")).strip().lower() == selected_method
            ),
            None,
        )
        if isinstance(active_summary, dict):
            bolt_forces = active_summary.get("bolt_forces")
            if isinstance(bolt_forces, list):
                force_rows = [item for item in bolt_forces if isinstance(item, dict)]
                if force_rows:
                    crit = max(force_rows, key=lambda item: abs(float(item.get("resultant_kip", 0.0))))
                    ru_crit = _format_quantity({"value": float(crit.get("resultant_kip", 0.0)), "unit": "kip"})
                    ru_crit_tag = _format_text(crit.get("tag"))
                    crit_row = _tag_to_row(ru_crit_tag)
                    ru_crit_var = f"Ru_{crit_row}_blt_web"
                    crit_x = max(force_rows, key=lambda item: abs(float(item.get("fx_kip", 0.0))))
                    crit_y = max(force_rows, key=lambda item: abs(float(item.get("fy_kip", 0.0))))
                    ru_x_max = _format_quantity({"value": float(crit_x.get("fx_kip", 0.0)), "unit": "kip"})
                    ru_x_max_tag = _format_text(crit_x.get("tag"))
                    crit_x_row = _tag_to_row(ru_x_max_tag)
                    ru_x_var = f"Ru_{crit_x_row}_blt_web_v2"
                    ru_y_max = _format_quantity({"value": float(crit_y.get("fy_kip", 0.0)), "unit": "kip"})
                    ru_y_max_tag = _format_text(crit_y.get("tag"))
                    crit_y_row = _tag_to_row(ru_y_max_tag)
                    ru_y_var = f"Ru_{crit_y_row}_blt_web_v3"
    lines = [
        heading,
        "",
        f"- Metodo seleccionado: `{method}`",
        "- Clausula: `Documento: Steel Construction Manual AISC 16th edition 2023 | Seccion: Part 7 DESIGN CONSIDERATIONS FOR BOLTS - Instantaneous Center of Rotation Method`",
        "- Ecuaciones: `ex_blt_web = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web; Muz_blt_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`",
        f"- Pu_sp: `{px}`",
        f"- Vu2_sp: `{py}`",
        f"- ex_blt_web: `{ex}`",
        f"- ey_blt_web: `{ey}`",
        f"- Muz_blt_web: `{mz}`",
        f"- Demanda (metodo activo): `{demand}`",
        f"- Ru_web_vg: `{ru_crit_var} = {ru_crit}`",
        f"- Ru_web_v2_max_vg: `{ru_x_var} = {ru_x_max}`",
        f"- Ru_web_v3_max_vg: `{ru_y_var} = {ru_y_max}`",
    ]
    if method == "icr" and cu != "n/a":
        lines.append(f"- Coeficiente Cu (ICR): `{cu}`")
    if icr_compare != "n/a":
        lines.append(f"- Picr comparativo: `{icr_compare}`")
    notes = _format_text(step2.get("notes"))
    if notes != "n/a":
        lines.append(f"- Nota: `{notes}`")
    lines.append("")
    return "\n".join(lines)


def _render_fully_restrained_splice_outline(rows_viga: list[dict], notes_viga: list[dict], step2_pernos1: dict | None) -> str:
    def _rows_for_scope(scope: str) -> list[dict]:
        target = scope.upper()
        return [item for item in rows_viga if str(item.get("scope", "")).upper() == target]

    scope_template = ["VIGA", "PLATINA_1", "PERNOS_1", "PLATINA_2", "PERNOS_2"]
    notes_by_id_scope: dict[tuple[str, str], dict] = {}
    for note in notes_viga:
        nid = _format_text(note.get("id")).strip()
        nscope = _format_text(note.get("scope")).upper().strip()
        if nid and nscope:
            notes_by_id_scope[(nid, nscope)] = note

    lines: list[str] = [
        "## Paso 1 - Propiedades geometricas, mecanicas y fabricacion",
        "",
        "Propiedades organizadas por ambito.",
        "",
    ]
    for section_offset, scope in enumerate(scope_template, start=1):
        lines.append(f"### 1.{section_offset} Ambito `{scope}`")
        lines.append("")
        if scope == "VIGA":
            note = notes_by_id_scope.get(("bbmb_splice.step1.geometry_note", "VIGA"), {})
            if note:
                lines.extend(
                    [
                        f"#### 1.{section_offset}.1 Resumen de geometria",
                        "",
                        f"- Perfil de viga ({_format_text(note.get('shape_vg_var'))}) (inp): `{_format_text(note.get('shape_vg'))}`",
                        f"- Tipo de acero de viga ({_format_text(note.get('steel_vg_var'))}) (inp): `{_format_text(note.get('steel_vg'))}`",
                        f"- Condicion superficial del ala ({_format_text(note.get('cond_sup_vg_var'))}) (inp): `{_format_text(note.get('cond_sup_vg'))}`",
                        f"- Condicion ambiental ala ({_format_text(note.get('cond_amb_vg_var'))}) (inp): `{_format_text(note.get('cond_amb_vg'))}`",
                        f"- Seleccion C3 para constructibilidad ({_format_text(note.get('c3_clearance_type_var'))}) (inp): `{_format_text(note.get('c3_clearance_type'))}`",
                        f"- Fluencia de viga ({_format_text(note.get('fy_vg_var'))}): `{_format_quantity(note.get('fy_vg'))}`",
                        f"- Resistencia ultima de viga ({_format_text(note.get('fu_vg_var'))}): `{_format_quantity(note.get('fu_vg'))}`",
                        f"- Modulo elastico de viga ({_format_text(note.get('e_vg_var'))}): `{_format_quantity(note.get('e_vg'))}`",
                        f"- Altura total de la seccion ({_format_text(note.get('d_vg_var'))}): `{_format_quantity(note.get('d_vg'))}`",
                        f"- Altura libre del alma ({_format_text(note.get('t_vg_var'))}): `{_format_quantity(note.get('t_vg'))}`",
                        f"- Ancho del ala ({_format_text(note.get('bf_vg_var'))}): `{_format_quantity(note.get('bf_vg'))}`",
                        f"- Ancho del ala para detallado ({_format_text(note.get('bfdet_vg_var'))}): `{_format_quantity(note.get('bfdet_vg'))}`",
                        f"- Espesor del alma ({_format_text(note.get('tw_vg_var'))}): `{_format_quantity(note.get('tw_vg'))}`",
                        f"- Espesor del alma para detallado ({_format_text(note.get('twdet_vg_var'))}): `{_format_quantity(note.get('twdet_vg'))}`",
                        f"- Espesor del ala ({_format_text(note.get('tf_vg_var'))}): `{_format_quantity(note.get('tf_vg'))}`",
                        f"- Espesor del ala para detallado ({_format_text(note.get('tfdet_vg_var'))}): `{_format_quantity(note.get('tfdet_vg'))}`",
                        f"- Distancia k de diseno ({_format_text(note.get('kdes_vg_var'))}): `{_format_quantity(note.get('kdes_vg'))}`",
                        f"- Distancia k detallada ({_format_text(note.get('kdet_vg_var'))}): `{_format_quantity(note.get('kdet_vg'))}`",
                        f"- Distancia desde el eje del alma al inicio del radio interno de al viga ({_format_text(note.get('k1_vg_var'))}): `{_format_quantity(note.get('k1_vg'))}`",
                        "",
                        f"#### 1.{section_offset}.2 Resumen de geometria del alma",
                        "",
                        f"- Separacion entre vigas (gap_sp) (inp): `{_format_quantity(note.get('alpha'))}`",
                        f"- Tolerancia de fabricacion en longitud de viga ({_format_text(note.get('beam_length_tolerance_var'))}) (inp): `{_format_quantity(note.get('beam_length_tolerance'))}`",
                        f"- Referencia tolerancia: `{_format_text(note.get('beam_length_tolerance_ref'))}`",
                        f"- Numero de pernos en direccion X del alma ({_format_text(note.get('n1x_var'))}) (inp): `{_format_text(note.get('n1x'))}`",
                        f"- Separacion horizontal entre columnas de pernos del alma ({_format_text(note.get('s1x_var'))}) (inp): `{_format_quantity(note.get('s1x'))}`",
                        f"- Distancia de borde en direccion X del grupo de pernos del alma ({_format_text(note.get('le1x1_var'))}) (inp): `{_format_quantity(note.get('le1x1'))}`",
                        f"- Ecuacion coordenadas X de pernos del alma: `{_format_text(note.get('xj_blt_web_formula'))}`",
                        f"- Rango del indice: `{_format_text(note.get('xj_blt_web_j_range'))}`",
                        f"- Coordenadas en direccion X para pernos del alma ({_format_text(note.get('xj_blt_web_var'))}): `{_format_indexed_quantity_series(note.get('xj_blt_web_values'))}`",
                        f"- Distancia de borde ajustada ({_format_text(note.get('le1x1_prime_var'))}): `{_format_quantity(note.get('le1x1_prime'))}`",
                        f"- Numero de pernos en direccion Y del alma ({_format_text(note.get('n1y_var'))}) (inp): `{_format_text(note.get('n1y'))}`",
                        f"- Separacion vertical entre filas de pernos del alma ({_format_text(note.get('s1y_var'))}) (inp): `{_format_quantity(note.get('s1y'))}`",
                        f"- Tipo de perforacion por pernos grupo 1 alma ({_format_text(note.get('type_hole_web_var'))}) (inp): `{_format_text(note.get('type_hole_web'))}`",
                        f"- Distancia vertical entre cara exterior de aleta inferior y fila inferior de pernos ({_format_text(note.get('le1y3_var'))}): `{_format_quantity(note.get('le1y3'))}`",
                        f"- Distancia neta respecto a kdet en alma ({_format_text(note.get('le1y3_1_var'))}): `{_format_quantity(note.get('le1y3_1'))}`",
                        f"- Diametro de perforacion para pernos 1 (dh.1): `{_format_quantity(note.get('dh_1'))}`",
                        "",
                        f"#### 1.{section_offset}.3 Resumen de geometria de la aleta",
                        "",
                        f"- Numero de pernos en direccion X del ala ({_format_text(note.get('n2x_var'))}) (inp): `{_format_text(note.get('n2x'))}`",
                        f"- Separacion entre filas de pernos del ala ({_format_text(note.get('s2x_var'))}) (inp): `{_format_quantity(note.get('s2x'))}`",
                        f"- Distancia de borde en direccion X del grupo de pernos del ala ({_format_text(note.get('le2x1_var'))}) (inp): `{_format_quantity(note.get('le2x1'))}`",
                        f"- Ecuacion coordenadas X de pernos de aleta: `{_format_text(note.get('xk_blt_flange_formula'))}`",
                        f"- Rango del indice: `{_format_text(note.get('xk_blt_flange_k_range'))}`",
                        f"- Coordenadas en direccion X para pernos de aleta ({_format_text(note.get('xk_blt_flange_var'))}): `{_format_indexed_quantity_series(note.get('xk_blt_flange_values'), index_key='k', quantity_key='x')}`",
                        f"- Numero de pernos en na mitad de aleta en direccion Z de la aleta ({_format_text(note.get('n2z_var'))}) (inp): `{_format_text(note.get('n2z'))}`",
                        f"- Distancia de borde en direccion Z del grupo de pernos del ala ({_format_text(note.get('le2z3_var'))}) (inp): `{_format_quantity(note.get('le2z3'))}`",
                        f"- Distancia complementaria de borde en aleta ({_format_text(note.get('le2z4_var'))}): `{_format_quantity(note.get('le2z4'))}`",
                        f"- Gage entre columnas de pernos del ala ({_format_text(note.get('s2z1_var'))}) (inp): `{_format_quantity(note.get('s2z1'))}`",
                        f"- Tipo de perforacion por pernos grupo 2 ala ({_format_text(note.get('type_hole_flange_var'))}) (inp): `{_format_text(note.get('type_hole_flange'))}`",
                        f"- Distancia util entre filas internas de pernos de aleta ({_format_text(note.get('g1_blt_flange_var'))}): `{_format_quantity(note.get('g1_blt_flange'))}`",
                        f"- Despeje horizontal entre grupos de pernos ({_format_text(note.get('f_blt_flange_var'))}): `{_format_quantity(note.get('f_blt_flange'))}`",
                        f"- Diametro de perforacion para pernos 2 (dh.2): `{_format_quantity(note.get('dh_2'))}`",
                        "",
                        f"#### 1.{section_offset}.4 Formulas de calculo",
                        "",
                        f"- Formula ajuste distancia de borde: `{_format_text(note.get('le1x1_prime_formula'))}`",
                        "- Formula distancia vertical borde ala/pernos alma: `Le_blt_web_y3 = 0.5*(d_vg - (n_blt_web_y - 1)*p_blt_web)`",
                        f"- Formula distancia neta respecto a kdet en alma: `{_format_text(note.get('le1y3_1_formula'))}`",
                        f"- Formula coordenadas X pernos de aleta: `{_format_text(note.get('xk_blt_flange_formula'))}`",
                        f"- Formula distancia util entre filas internas de pernos de aleta: `{_format_text(note.get('g1_blt_flange_formula'))}`",
                        f"- Formula despeje horizontal entre grupos de pernos: `{_format_text(note.get('f_blt_flange_formula'))}`",
                        f"- Formula distancia complementaria de borde en aleta: `{_format_text(note.get('le2z4_formula'))}`",
                        "",
                    ]
                )
            else:
                lines.append("Sin notas tecnicas disponibles para este ambito.")
                lines.append("")
            continue
        if scope == "PLATINA_1":
            note_geom = notes_by_id_scope.get(("bbmb_splice.step1.geometry_formulas_plt1_note", "PLATINA_1"), {})
            note_hole = notes_by_id_scope.get(("bbmb_splice.step1.plate_1_hole_diameter_note", "PLATINA_1"), {})
            if note_geom or note_hole:
                lines.extend(
                    [
                        f"#### 1.{section_offset}.1 Resumen de geometria",
                        "",
                        f"- Tipo de acero de platina de alma ({_format_text(note_geom.get('steel_plt_web_var'))}) (inp): `{_format_text(note_geom.get('steel_plt_web'))}`",
                        f"- Fluencia de platina de alma ({_format_text(note_geom.get('fy_plt_web_var'))}): `{_format_quantity(note_geom.get('fy_plt_web'))}`",
                        f"- Resistencia ultima de platina de alma ({_format_text(note_geom.get('fu_plt_web_var'))}): `{_format_quantity(note_geom.get('fu_plt_web'))}`",
                        f"- Modulo elastico de platina de alma ({_format_text(note_geom.get('e_plt_web_var'))}): `{_format_quantity(note_geom.get('e_plt_web'))}`",
                        f"- Tipo de perforacion por pernos grupo 1 alma ({_format_text(note_geom.get('type_hole_plt_web_var'))}) (inp): `{_format_text(note_geom.get('type_hole_plt_web'))}`",
                        f"- Condicion superficial platina alma ({_format_text(note_geom.get('cond_sup_plt_web_var'))}) (inp): `{_format_text(note_geom.get('cond_sup_plt_web'))}`",
                        f"- Condicion ambiental platina alma ({_format_text(note_geom.get('cond_amb_plt_web_var'))}) (inp): `{_format_text(note_geom.get('cond_amb_plt_web'))}`",
                        f"- Espesor de platina de alma ({_format_text(note_geom.get('t_plt_web_var'))}) (inp): `{_format_quantity(note_geom.get('t_plt_web'))}`",
                        f"- Numero de pernos en direccion X del alma ({_format_text('n_plt_web_x')}) (inp): `{_format_text(note_geom.get('n_blt_web_x'))}`",
                        f"- Separacion horizontal entre columnas de pernos del alma ({_format_text('g_plt_web')}) (inp): `{_format_quantity(note_geom.get('g_blt_web'))}`",
                        f"- Distancia al borde en direccion X de platina de alma ({_format_text('Le_plt_web_x2')}) (inp): `{_format_quantity(note_geom.get('le_blt_web_x2'))}`",
                        f"- Numero de pernos en direccion Y del alma ({_format_text('n_plt_web_y')}) (inp): `{_format_text(note_geom.get('n_blt_web_y'))}`",
                        f"- Separacion vertical entre filas de pernos del alma ({_format_text('p_plt_web')}) (inp): `{_format_quantity(note_geom.get('p_blt_web'))}`",
                        f"- Distancia al borde inferior de platina de alma ({_format_text('Le_plt_web_y1')}) (inp): `{_format_quantity(note_geom.get('le_blt_web_y1'))}`",
                        f"- Distancia al borde superior de platina de alma ({_format_text('Le_plt_web_y2')}) (inp): `{_format_quantity(note_geom.get('le_blt_web_y2'))}`",
                        f"- Longitud de platina de alma ({_format_text(note_geom.get('l_plt_web_var'))}): `{_format_quantity(note_geom.get('l_plt_web'))}`",
                        f"- Altura de platina de alma ({_format_text(note_geom.get('h_plt_web_var'))}): `{_format_quantity(note_geom.get('h_plt_web'))}`",
                        f"- {_format_text(note_hole.get('dh_var'))}: `{_format_quantity(note_hole.get('dh'))}`",
                        "",
                        f"#### 1.{section_offset}.2 Formulas de calculo",
                        "",
                        "- Formula trazabilidad: `n_plt_web_x = n_blt_web_x`",
                        "- Formula trazabilidad: `g_plt_web = g_blt_web`",
                        "- Formula trazabilidad: `n_plt_web_y = n_blt_web_y`",
                        "- Formula trazabilidad: `p_plt_web = p_blt_web`",
                        "- Formula trazabilidad: `Le_plt_web_x2 = Le_blt_web_x2`",
                        "- Formula trazabilidad: `Le_plt_web_y1 = Le_blt_web_y1`",
                        "- Formula trazabilidad: `Le_plt_web_y2 = Le_blt_web_y2`",
                        f"- Formula H_plt_web: `{_format_text(note_geom.get('hp1_formula'))}`",
                        f"- Formula L_plt_web: `{_format_text(note_geom.get('bp1_formula'))}`",
                        f"- Formula dh_plt_web: `{_format_text(note_hole.get('formula'))}`",
                        "",
                    ]
                )
            else:
                lines.append("Sin notas tecnicas disponibles para este ambito.")
                lines.append("")
            continue
        if scope == "PERNOS_1":
            note = notes_by_id_scope.get(("bbmb_splice.step1.bolt_group_1_properties_note", "PERNOS_1"), {})
            if note:
                lines.extend(
                    [
                        f"#### 1.{section_offset}.1 Resumen de geometria",
                        "",
                        f"- Tipo de acero/perno ({_format_text('shape_blt_web')}) (inp): `{_format_text(note.get('bolt_shape'))}`",
                        f"- Norma de fabricacion (inp): `{_format_text(note.get('fabrication_standard'))}`",
                        f"- Clasificacion: `{_format_text(note.get('classification'))}`",
                        f"- Condicion de rosca (inp): `{_format_text(note.get('thread_condition'))}`",
                        f"- Tipo de apriete (inp): `{_format_text(note.get('tightening_type'))}`",
                        f"- Resistencia nominal a traccion ({_format_text(note.get('fnt_var'))}): `{_format_quantity(note.get('fnt'))}`",
                        f"- Resistencia nominal a cortante ({_format_text(note.get('fnv_var'))}): `{_format_quantity(note.get('fnv'))}`",
                        f"- Diametro nominal (db_blt_web): `{_format_quantity(note.get('diameter_nominal'))}`",
                        f"- Longitud de vastago: `{_format_quantity(note.get('length_shank'))}`",
                        f"- Width across flats: `{_format_quantity(note.get('width_across_flats'))}`",
                        f"- Diametro de cabeza: `{_format_quantity(note.get('head_diameter'))}`",
                        f"- Altura de cabeza: `{_format_quantity(note.get('head_height'))}`",
                        "",
                    ]
                )
            else:
                lines.append("Sin notas tecnicas disponibles para este ambito.")
                lines.append("")
            continue
        if scope == "PLATINA_2":
            note_geom = notes_by_id_scope.get(("bbmb_splice.step1.geometry_formulas_plt2_note", "PLATINA_2"), {})
            note_hole = notes_by_id_scope.get(("bbmb_splice.step1.plate_2_hole_diameter_note", "PLATINA_2"), {})
            if note_geom or note_hole:
                lines.extend(
                    [
                        f"#### 1.{section_offset}.1 Resumen de geometria",
                        "",
                        f"- Tipo de acero de platina de ala ({_format_text(note_geom.get('steel_plt_flange_var'))}) (inp): `{_format_text(note_geom.get('steel_plt_flange'))}`",
                        f"- Fluencia de platina de ala ({_format_text(note_geom.get('fy_plt_flange_var'))}): `{_format_quantity(note_geom.get('fy_plt_flange'))}`",
                        f"- Resistencia ultima de platina de ala ({_format_text(note_geom.get('fu_plt_flange_var'))}): `{_format_quantity(note_geom.get('fu_plt_flange'))}`",
                        f"- Modulo elastico de platina de ala ({_format_text(note_geom.get('e_plt_flange_var'))}): `{_format_quantity(note_geom.get('e_plt_flange'))}`",
                        f"- Tipo de perforacion por pernos grupo 2 ala ({_format_text(note_geom.get('type_hole_plt_flange_var'))}) (inp): `{_format_text(note_geom.get('type_hole_plt_flange'))}`",
                        f"- Condicion superficial platina ala ({_format_text(note_geom.get('cond_sup_plt_flange_var'))}) (inp): `{_format_text(note_geom.get('cond_sup_plt_flange'))}`",
                        f"- Condicion ambiental platina ala ({_format_text(note_geom.get('cond_amb_plt_flange_var'))}) (inp): `{_format_text(note_geom.get('cond_amb_plt_flange'))}`",
                        f"- Espesor de platina de ala ({_format_text(note_geom.get('t_plt_flange_var'))}) (inp): `{_format_quantity(note_geom.get('t_plt_flange'))}`",
                        f"- Numero de pernos en direccion X del ala ({_format_text('n_plt_flange_x')}) (inp): `{_format_text(note_geom.get('n_blt_flange_x'))}`",
                        f"- Separacion entre filas de pernos del ala ({_format_text('p_plt_flange')}) (inp): `{_format_quantity(note_geom.get('p_blt_flange'))}`",
                        f"- Distancia al borde de la platina de ala en x ({_format_text('Le_plt_flange_x2')}) (inp): `{_format_quantity(note_geom.get('le_blt_flange_x2'))}`",
                        f"- Numero de pernos en direccion Z del ala ({_format_text('n_plt_flange_z')}) (inp): `{_format_text(note_geom.get('n_blt_flange_z'))}`",
                        f"- Gage entre columnas de pernos del ala ({_format_text('g_plt_flange')}) (inp): `{_format_quantity(note_geom.get('g_blt_flange'))}`",
                        f"- Distancia de borde interior 1 en direccion Z del ala ({_format_text('Le_plt_flange_z1')}) (inp): `{_format_quantity(note_geom.get('le_blt_flange_z1'))}`",
                        f"- Distancia de borde interior 2 en direccion Z del ala ({_format_text('Le_plt_flange_z2')}) (inp): `{_format_quantity(note_geom.get('le_blt_flange_z2'))}`",
                        f"- Distancia util entre filas internas de pernos de aleta ({_format_text('g1_plt_flange')}): `{_format_quantity(note_geom.get('g1_blt_flange'))}`",
                        f"- Longitud de platina de ala ({_format_text(note_geom.get('l_plt_flange_var'))}): `{_format_quantity(note_geom.get('l_plt_flange'))}`",
                        f"- Ancho de platina de ala ({_format_text(note_geom.get('b_plt_flange_var'))}): `{_format_quantity(note_geom.get('b_plt_flange'))}`",
                        f"- {_format_text(note_hole.get('dh_var'))}: `{_format_quantity(note_hole.get('dh'))}`",
                        "",
                        f"#### 1.{section_offset}.2 Formulas de calculo",
                        "",
                        "- Formula trazabilidad: `n_plt_flange_x = n_blt_flange_x`",
                        "- Formula trazabilidad: `p_plt_flange = p_blt_flange`",
                        "- Formula trazabilidad: `Le_plt_flange_x2 = Le_blt_flange_x2`",
                        "- Formula trazabilidad: `n_plt_flange_z = n_blt_flange_z`",
                        "- Formula trazabilidad: `g_plt_flange = g_blt_flange`",
                        "- Formula trazabilidad: `Le_plt_flange_z1 = Le_blt_flange_z1`",
                        "- Formula trazabilidad: `Le_plt_flange_z2 = Le_blt_flange_z2`",
                        "- Formula calculo: `g1_plt_flange = bf_vg - 2*(Le_blt_flange_z3 + (n_blt_flange_z - 1)*g_blt_flange)`",
                        "- Formula trazabilidad: `g1_plt_flange = g1_blt_flange`",
                        f"- Formula B_plt_flange: `{_format_text(note_geom.get('bp2_formula'))}`",
                        f"- Formula L_plt_flange: `{_format_text(note_geom.get('lp2_formula'))}`",
                        f"- Formula dh_plt_flange: `{_format_text(note_hole.get('formula'))}`",
                        "",
                    ]
                )
            else:
                lines.append("Sin notas tecnicas disponibles para este ambito.")
                lines.append("")
            continue
        if scope == "PERNOS_2":
            note = notes_by_id_scope.get(("bbmb_splice.step1.bolt_group_2_properties_note", "PERNOS_2"), {})
            if note:
                lines.extend(
                    [
                        f"#### 1.{section_offset}.1 Resumen de geometria",
                        "",
                        f"- Tipo de acero/perno ({_format_text('shape_blt_flange')}) (inp): `{_format_text(note.get('bolt_shape'))}`",
                        f"- Norma de fabricacion (inp): `{_format_text(note.get('fabrication_standard'))}`",
                        f"- Clasificacion: `{_format_text(note.get('classification'))}`",
                        f"- Condicion de rosca (inp): `{_format_text(note.get('thread_condition'))}`",
                        f"- Tipo de apriete (inp): `{_format_text(note.get('tightening_type'))}`",
                        f"- Resistencia nominal a traccion ({_format_text(note.get('fnt_var'))}): `{_format_quantity(note.get('fnt'))}`",
                        f"- Resistencia nominal a cortante ({_format_text(note.get('fnv_var'))}): `{_format_quantity(note.get('fnv'))}`",
                        f"- Diametro nominal (db_blt_flange): `{_format_quantity(note.get('diameter_nominal'))}`",
                        f"- Longitud de vastago: `{_format_quantity(note.get('length_shank'))}`",
                        f"- Width across flats: `{_format_quantity(note.get('width_across_flats'))}`",
                        f"- Diametro de cabeza: `{_format_quantity(note.get('head_diameter'))}`",
                        f"- Altura de cabeza: `{_format_quantity(note.get('head_height'))}`",
                        "",
                    ]
                )
            else:
                lines.append("Sin notas tecnicas disponibles para este ambito.")
                lines.append("")
            continue
        lines.append("Sin notas tecnicas disponibles para este ambito.")
        lines.append("")

    lines.extend(
        [
            "## Paso 2 - Revisiones de requerimientos de propiedades mecanicas y geometricas",
            "",
        ]
    )
    all_rows = [item for scope in scope_template for item in _rows_for_scope(scope)]
    g_blt_web_rows = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "g_blt_web"
        and "direccion X" in _translate_text_es(item.get("description"))
    ]
    if not g_blt_web_rows:
        g_blt_web_rows = [
            item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "g_blt_web"
        ]
    g_blt_web_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    g_plt_web_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "g_plt_web"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_1"
    ]
    g_plt_web_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    if not g_plt_web_rows_for_step2:
        g_plt_web_rows_for_step2 = []
        for base_row in g_blt_web_rows[:2]:
            alias_row = dict(base_row)
            alias_row["calculated_symbol"] = "g_plt_web"
            g_plt_web_rows_for_step2.append(alias_row)
    le_plt_web_x2_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_plt_web_x2"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_1"
    ]
    le_plt_web_x2_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    p_plt_web_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "p_plt_web"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_1"
    ]
    p_plt_web_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_plt_web_y1_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_plt_web_y1"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_1"
    ]
    le_plt_web_y1_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_plt_web_y2_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_plt_web_y2"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_1"
    ]
    le_plt_web_y2_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    p_plt_flange_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "p_plt_flange"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_2"
    ]
    p_plt_flange_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_plt_flange_x2_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_plt_flange_x2"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_2"
    ]
    le_plt_flange_x2_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    g_plt_flange_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "g_plt_flange"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_2"
    ]
    g_plt_flange_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_plt_flange_z1_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_plt_flange_z1"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_2"
    ]
    le_plt_flange_z1_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_plt_flange_z2_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_plt_flange_z2"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_2"
    ]
    le_plt_flange_z2_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    g1_plt_flange_rows_for_step2 = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "g1_plt_flange"
        and str(item.get("scope", "")).strip().upper() == "PLATINA_2"
    ]
    g1_plt_flange_rows_for_step2.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_blt_web_x1_rows = [
        item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "Le_blt_web_x1"
    ]
    le_blt_web_x1_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    p_blt_web_rows = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "p_blt_web"
        and "direccion Z" in _translate_text_es(item.get("description"))
    ]
    if not p_blt_web_rows:
        p_blt_web_rows = [
            item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "p_blt_web"
    ]
    p_blt_web_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_blt_web_y31_rows = [
        item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "Le_blt_web_y3.1"
    ]
    le_blt_web_y31_rows = [
        item for item in le_blt_web_y31_rows if "(C3)" not in _translate_text_es(item.get("description"))
    ]
    le_blt_web_y31_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    p_blt_flange_rows = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "p_blt_flange"
        and "direccion X" in _translate_text_es(item.get("description"))
    ]
    if not p_blt_flange_rows:
        p_blt_flange_rows = [
            item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "p_blt_flange"
    ]
    p_blt_flange_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_blt_flange_x1_rows = [
        item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "Le_blt_flange_x1"
    ]
    le_blt_flange_x1_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_blt_flange_z3_rows = [
        item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "Le_blt_flange_z3"
    ]
    le_blt_flange_z3_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_blt_flange_z4_rows = [
        item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "Le_blt_flange_z4"
    ]
    le_blt_flange_z4_rows = [
        item for item in le_blt_flange_z4_rows if "(C3)" not in _translate_text_es(item.get("description"))
    ]
    le_blt_flange_z4_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    le_blt_flange_z4_c3_rows = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_blt_flange_z4"
        and "(C3)" in _translate_text_es(item.get("description"))
    ]
    le_blt_web_y31_c3_rows = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "Le_blt_web_y3.1"
        and "(C3)" in _translate_text_es(item.get("description"))
    ]
    f_blt_flange_rows = [
        item
        for item in all_rows
        if "Despeje horizontal F_blt_flange" in _translate_text_es(item.get("description"))
    ]
    g_blt_flange_rows = [
        item
        for item in all_rows
        if str(item.get("calculated_symbol", "")).strip() == "g_blt_flange"
        and "direccion Z" in _translate_text_es(item.get("description"))
    ]
    if not g_blt_flange_rows:
        g_blt_flange_rows = [
            item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "g_blt_flange"
    ]
    g_blt_flange_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    g1_blt_flange_rows = [
        item for item in all_rows if str(item.get("calculated_symbol", "")).strip() == "g1_blt_flange"
    ]
    g1_blt_flange_rows.sort(key=lambda r: 0 if str(r.get("comparison_text", "")).strip() == ">=" else 1)
    tight_allowed = ["pretensioned", "snug_tight"]
    std_allowed = [
        "ASTM F3125/F3125M",
        "ASTM A325",
        "ASTM A325M",
        "ASTM A490",
        "ASTM A490M",
        "ASTM F1852",
        "ASTM F2280",
    ]
    pernos1_note = notes_by_id_scope.get(("bbmb_splice.step1.bolt_group_1_properties_note", "PERNOS_1"), {})
    pernos2_note = notes_by_id_scope.get(("bbmb_splice.step1.bolt_group_2_properties_note", "PERNOS_2"), {})
    tight_1 = _format_text(pernos1_note.get("tightening_type"))
    std_1 = _format_text(pernos1_note.get("fabrication_standard"))
    tight_2 = _format_text(pernos2_note.get("tightening_type"))
    std_2 = _format_text(pernos2_note.get("fabrication_standard"))
    pernos1_step2_rows = [
        {
            "description": "Tipo de apriete permitido para pernos grupo 1",
            "calculated_symbol": "tight_bolt_vgder",
            "comparison": "in_set",
            "calculated_text": tight_1,
            "allowed_values": tight_allowed,
            "clause": "Criterio de proyecto splice",
            "result": "PASS" if tight_1 in tight_allowed else "FAIL",
        },
        {
            "description": "Norma de fabricacion permitida para pernos grupo 1",
            "calculated_symbol": "std_bolt_vgder",
            "comparison": "in_set",
            "calculated_text": std_1,
            "allowed_values": std_allowed,
            "clause": "Criterio de proyecto splice",
            "result": "PASS" if std_1 in std_allowed else "FAIL",
        },
    ]
    pernos2_step2_rows = [
        {
            "description": "Tipo de apriete permitido para pernos grupo 2",
            "calculated_symbol": "tight_bolt_vgder",
            "comparison": "in_set",
            "calculated_text": tight_2,
            "allowed_values": tight_allowed,
            "clause": "Criterio de proyecto splice",
            "result": "PASS" if tight_2 in tight_allowed else "FAIL",
        },
        {
            "description": "Norma de fabricacion permitida para pernos grupo 2",
            "calculated_symbol": "std_bolt_vgder",
            "comparison": "in_set",
            "calculated_text": std_2,
            "allowed_values": std_allowed,
            "clause": "Criterio de proyecto splice",
            "result": "PASS" if std_2 in std_allowed else "FAIL",
        },
    ]
    viga_rows_for_step2 = (
        g_blt_web_rows[:2]
        + le_blt_web_x1_rows[:2]
        + p_blt_web_rows[:2]
        + le_blt_web_y31_rows[:2]
        + p_blt_flange_rows[:2]
        + le_blt_flange_x1_rows[:2]
        + le_blt_flange_z3_rows[:2]
        + le_blt_flange_z4_rows[:2]
        + g_blt_flange_rows[:2]
        + g1_blt_flange_rows[:2]
        + le_blt_flange_z4_c3_rows[:1]
        + le_blt_web_y31_c3_rows[:1]
        + f_blt_flange_rows[:1]
    )

    def _render_simple_check(
        *,
        chapter: int,
        section: int,
        idx: int,
        scope_label: str,
        item: dict,
    ) -> None:
        comparison_mode = str(item.get("comparison", "")).strip()
        description = _translate_text_es(item.get("description"))
        calculated_symbol = str(item.get("calculated_symbol", "calc"))
        limit_symbol = str(item.get("limit_symbol", "lim"))
        comparison = str(item.get("comparison_text", "vs"))
        calculated = _format_quantity(item.get("calculated"))
        limit = _format_quantity(item.get("limit"))
        raw_result_value = str(item.get("result", item.get("status", "UNKNOWN"))).strip().upper()
        clause = _render_clause_text(
            item.get("clause"),
            item.get("source_document"),
            item.get("rule_id"),
        )
        verification_override = _format_text(item.get("verification_override"))
        if verification_override != "n/a":
            verification = verification_override
        elif comparison_mode == "in_set":
            calculated_text = _format_text(item.get("calculated_text"))
            allowed_values = item.get("allowed_values")
            allowed = ", ".join(str(v) for v in allowed_values) if isinstance(allowed_values, list) else limit_symbol
            verification = f"{calculated_symbol} in {{{allowed}}}; '{calculated_text}' in {{{allowed}}}"
        else:
            limit_symbol_text = limit_symbol
            if (
                calculated_symbol == "Le_blt_web_x1"
                and comparison == ">="
                and str(limit_symbol).strip().lower().startswith("max(le_min")
            ):
                limit_symbol_text = "Le_min"
            if raw_result_value in {"NOT_APPLICABLE", "NO_APLICA", "NO APLICA", "NA"}:
                applicability = _format_text(item.get("applicability"))
                if applicability != "n/a":
                    verification = applicability
                else:
                    verification = f"{calculated_symbol} {comparison} {limit_symbol_text}; {calculated} {comparison} {limit}"
            else:
                verification = f"{calculated_symbol} {comparison} {limit_symbol_text}; {calculated} {comparison} {limit}"
        result_text = _render_result_label(item.get("result", item.get("status", "UNKNOWN")))
        lines.append(f"#### Chequeo {chapter}.{section}.{idx} - {description} (`{calculated_symbol}`)")
        lines.append("")
        lines.append(f"- Ambito: `{scope_label}`")
        lines.append(f"- Verificacion: `{verification}`")
        lines.append(f"- Clausula: `{clause}`")
        lines.append(f"- Resultado: {result_text}")
        lines.append("")

    scope_summary: list[dict[str, Any]] = []
    for section_offset, scope in enumerate(scope_template, start=1):
        lines.append(f"### 2.{section_offset} Ámbito `{scope}`")
        lines.append("")
        if section_offset == 1:
            items_for_scope: list[dict] = viga_rows_for_step2
        elif section_offset == 2:
            items_for_scope = (
                g_plt_web_rows_for_step2
                + le_plt_web_x2_rows_for_step2
                + p_plt_web_rows_for_step2
                + le_plt_web_y1_rows_for_step2
                + le_plt_web_y2_rows_for_step2
            )
        elif section_offset == 3:
            items_for_scope = pernos1_step2_rows
        elif section_offset == 4:
            items_for_scope = (
                p_plt_flange_rows_for_step2
                + le_plt_flange_x2_rows_for_step2
                + g_plt_flange_rows_for_step2
                + le_plt_flange_z1_rows_for_step2
                + le_plt_flange_z2_rows_for_step2
                + g1_plt_flange_rows_for_step2
            )
        elif section_offset == 5:
            items_for_scope = pernos2_step2_rows
        else:
            items_for_scope = []
        local_idx = 1
        total_checks = 0
        pass_checks = 0
        fail_numerals: list[str] = []
        for item in items_for_scope:
            _render_simple_check(
                chapter=2,
                section=section_offset,
                idx=local_idx,
                scope_label=scope,
                item=item,
            )
            total_checks += 1
            status_raw = str(item.get("status", item.get("result", ""))).strip().upper()
            if status_raw in {"PASS", "OK", "NOT_APPLICABLE", "NO_APLICA", "NO APLICA", "NA"}:
                pass_checks += 1
            else:
                fail_numerals.append(f"2.{section_offset}.{local_idx}")
            local_idx += 1
        scope_summary.append(
            {
                "scope": scope,
                "section_offset": section_offset,
                "total": total_checks,
                "pass": pass_checks,
                "fail": total_checks - pass_checks,
                "fail_numerals": fail_numerals,
            }
        )

    lines.append(f"### 2.{len(scope_template)+1} Resumen de chequeos por ámbito")
    lines.append("")
    for summary in scope_summary:
        fail_numerals = summary["fail_numerals"]
        fail_text = ", ".join(fail_numerals) if fail_numerals else "ninguno"
        status_dot = "🟢" if summary["fail"] == 0 else "🔴"
        lines.append(
            f"- {status_dot} "
            f"`2.{summary['section_offset']}` `{summary['scope']}`: "
            f"total={summary['total']}, cumple={summary['pass']}, no_cumple={summary['fail']}, "
            f"numerales_no_cumplen={fail_text}"
        )

    lines.extend(
        [
            "",
            "## Paso 3 - Metodo ICR/Elastic para grupo de pernos 1",
            "",
        ]
    )
    lines.append(_render_splice_step_2_method_block(step2_pernos1, chapter_number=3))
    tearout_note = notes_by_id_scope.get(("bbmb_splice.step4.web_tearout_note", "VIGA"), {})
    plt1_tearout_v2_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_tearout_v2_note", "PLATINA_1"), {})
    plt1_bearing_v2_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_bearing_v2_note", "PLATINA_1"), {})
    plt1_tearout_v3_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_tearout_v3_note", "PLATINA_1"), {})
    plt1_bolt_shear_v2_v3_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_bolt_shear_rupture_note", "PLATINA_1"), {})
    plt1_block_shear_v2_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_block_shear_v2_note", "PLATINA_1"), {})
    plt1_block_shear_v3_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_block_shear_v3_note", "PLATINA_1"), {})
    plt1_tension_yielding_v3_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_tension_yielding_v3_note", "PLATINA_1"), {})
    plt1_tension_rupture_v3_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_tension_rupture_v3_note", "PLATINA_1"), {})
    plt1_flex_yielding_m1_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_flex_yielding_m1_note", "PLATINA_1"), {})
    plt1_ltb_m1_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_ltb_m1_note", "PLATINA_1"), {})
    plt1_flex_rupture_m1_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_flex_rupture_m1_note", "PLATINA_1"), {})
    plt1_shear_yielding_v2_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_shear_yielding_v2_note", "PLATINA_1"), {})
    plt1_shear_rupture_v2_note = notes_by_id_scope.get(("bbmb_splice.step5.plt1_web_shear_rupture_v2_note", "PLATINA_1"), {})
    tearout_v3_note = notes_by_id_scope.get(("bbmb_splice.step4.web_tearout_v3_note", "VIGA"), {})
    bearing_note = notes_by_id_scope.get(("bbmb_splice.step4.web_bearing_note", "VIGA"), {})
    bearing_v3_note = notes_by_id_scope.get(("bbmb_splice.step4.web_bearing_v3_note", "VIGA"), {})
    tension_rupture_v3_note = notes_by_id_scope.get(("bbmb_splice.step4.web_tension_rupture_v3_note", "VIGA"), {})
    block_shear_v3_note = notes_by_id_scope.get(("bbmb_splice.step4.web_block_shear_v3_note", "VIGA"), {})
    bolt_shear_note = notes_by_id_scope.get(("bbmb_splice.step4.web_bolt_shear_rupture_note", "VIGA"), {})
    web_shear_rupture_note = notes_by_id_scope.get(("bbmb_splice.step4.web_shear_rupture_note", "VIGA"), {})
    web_block_shear_note = notes_by_id_scope.get(("bbmb_splice.step4.web_block_shear_note", "VIGA"), {})
    tearout_result = _render_result_label(tearout_note.get("result_web_tearout_v2_vg"))
    ru_web_v2_max_vg_q: Quantity | None = None
    ru_web_v3_max_vg_q: Quantity | None = None
    ru_web_vg_q: Quantity | None = None
    if isinstance(step2_pernos1, dict):
        report = step2_pernos1.get("report")
        if isinstance(report, dict):
            method_selected = _format_text(report.get("method_selected")).strip().lower()
            methods_summary = report.get("methods_summary")
            if isinstance(methods_summary, list):
                active_summary = next(
                    (
                        item
                        for item in methods_summary
                        if isinstance(item, dict) and _format_text(item.get("method")).strip().lower() == method_selected
                    ),
                    None,
                )
                if isinstance(active_summary, dict):
                    bolt_forces = active_summary.get("bolt_forces")
                    if isinstance(bolt_forces, list):
                        rows = [item for item in bolt_forces if isinstance(item, dict)]
                        if rows:
                            crit_v2 = max(rows, key=lambda item: abs(float(item.get("fx_kip", 0.0))))
                            ru_web_v2_max_vg_q = Quantity(
                                value=float(crit_v2.get("fx_kip", 0.0)),
                                unit="kip",
                            )
                            crit_v3 = max(rows, key=lambda item: abs(float(item.get("fy_kip", 0.0))))
                            ru_web_v3_max_vg_q = Quantity(
                                value=float(crit_v3.get("fy_kip", 0.0)),
                                unit="kip",
                            )
                            crit_r = max(rows, key=lambda item: abs(float(item.get("resultant_kip", 0.0))))
                            ru_web_vg_q = Quantity(
                                value=float(crit_r.get("resultant_kip", 0.0)),
                                unit="kip",
                            )
    def _convert_ru_to_capacity_unit(ru_q: Quantity | None, cap_q: Quantity | None) -> Quantity | None:
        if not isinstance(ru_q, Quantity):
            return None
        if not isinstance(cap_q, Quantity):
            return ru_q
        if ru_q.unit == cap_q.unit:
            return ru_q
        if ru_q.unit == "kip" and cap_q.unit == "kN":
            return Quantity(value=ru_q.value * 4.4482216152605, unit="kN")
        if ru_q.unit == "kN" and cap_q.unit == "kip":
            return Quantity(value=ru_q.value / 4.4482216152605, unit="kip")
        return ru_q

    ru_web_v2_vg_disp: Quantity | None = ru_web_v2_max_vg_q
    phi_rn_web_q = _as_quantity(
        tearout_note.get("phi_rn1_web_v2_vg")
        if tearout_note.get("phi_rn1_web_v2_vg") is not None
        else tearout_note.get("phi_rn_web_v2_vg")
    )
    ru_web_v2_vg_disp = _convert_ru_to_capacity_unit(ru_web_v2_vg_disp, phi_rn_web_q)
    dcr1_web_v2_vg_disp: str = _format_text(
        tearout_note.get("dcr1_web_v2_vg")
        if tearout_note.get("dcr1_web_v2_vg") is not None
        else tearout_note.get("dcr_web_tearout_v2_vg")
    )
    if (
        isinstance(ru_web_v2_vg_disp, Quantity)
        and isinstance(phi_rn_web_q, Quantity)
        and ru_web_v2_vg_disp.unit == phi_rn_web_q.unit
        and abs(phi_rn_web_q.value) > 1e-12
    ):
        dcr1_web_v2_vg_disp = _format_decimal(abs(ru_web_v2_vg_disp.value) / phi_rn_web_q.value)
    ru_web_v2_vg_abs_disp: Quantity | None = None
    if isinstance(ru_web_v2_vg_disp, Quantity):
        ru_web_v2_vg_abs_disp = Quantity(value=abs(ru_web_v2_vg_disp.value), unit=ru_web_v2_vg_disp.unit)
    try:
        dcr1_num = float(dcr1_web_v2_vg_disp)
        tearout_result = _render_result_label("PASS" if dcr1_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.1.1 plate 1 tearout in v2 direction
    phi_rn1_plt_v2_web_q = _as_quantity(plt1_tearout_v2_note.get("phi_rn1_plt_v2_web"))
    ru1_plt_v2_web_disp = _convert_ru_to_capacity_unit(ru_web_v2_max_vg_q, phi_rn1_plt_v2_web_q)
    ru1_plt_v2_web_abs_disp: Quantity | None = None
    if isinstance(ru1_plt_v2_web_disp, Quantity):
        ru1_plt_v2_web_abs_disp = Quantity(value=abs(ru1_plt_v2_web_disp.value), unit=ru1_plt_v2_web_disp.unit)
    dcr1_plt_v2_web_disp = "n/a"
    if (
        isinstance(ru1_plt_v2_web_disp, Quantity)
        and isinstance(phi_rn1_plt_v2_web_q, Quantity)
        and ru1_plt_v2_web_disp.unit == phi_rn1_plt_v2_web_q.unit
        and abs(phi_rn1_plt_v2_web_q.value) > 1e-12
    ):
        dcr1_plt_v2_web_disp = _format_decimal(abs(ru1_plt_v2_web_disp.value) / phi_rn1_plt_v2_web_q.value)
    plt1_tearout_v2_result = _render_result_label("UNKNOWN")
    try:
        dcr1_plt_num = float(dcr1_plt_v2_web_disp)
        plt1_tearout_v2_result = _render_result_label("PASS" if dcr1_plt_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.1.2 plate 1 bearing in v2-v3 direction
    phi_rn2_plt_v2_web_q = _as_quantity(plt1_bearing_v2_note.get("phi_rn2_plt_v2_web"))
    ru2_plt_v2_web_disp = _convert_ru_to_capacity_unit(ru_web_vg_q, phi_rn2_plt_v2_web_q)
    ru2_plt_v2_web_abs_disp: Quantity | None = None
    if isinstance(ru2_plt_v2_web_disp, Quantity):
        ru2_plt_v2_web_abs_disp = Quantity(value=abs(ru2_plt_v2_web_disp.value), unit=ru2_plt_v2_web_disp.unit)
    dcr2_plt_v2_web_disp = _format_text(plt1_bearing_v2_note.get("dcr2_plt_v2_web"))
    if (
        isinstance(ru2_plt_v2_web_disp, Quantity)
        and isinstance(phi_rn2_plt_v2_web_q, Quantity)
        and ru2_plt_v2_web_disp.unit == phi_rn2_plt_v2_web_q.unit
        and abs(phi_rn2_plt_v2_web_q.value) > 1e-12
    ):
        dcr2_plt_v2_web_disp = _format_decimal(abs(ru2_plt_v2_web_disp.value) / phi_rn2_plt_v2_web_q.value)
    plt1_bearing_v2_result = _render_result_label("UNKNOWN")
    try:
        dcr2_plt_num = float(dcr2_plt_v2_web_disp)
        plt1_bearing_v2_result = _render_result_label("PASS" if dcr2_plt_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.1.3 plate 1 bolt shear rupture in v2-v3 direction
    phi_rn3_plt_v2_v3_web_q = _as_quantity(plt1_bolt_shear_v2_v3_note.get("phi_rn3_plt_v2_v3_web"))
    ru3_plt_v2_v3_web_disp = _convert_ru_to_capacity_unit(ru_web_vg_q, phi_rn3_plt_v2_v3_web_q)
    ru3_plt_v2_v3_web_abs_disp: Quantity | None = None
    if isinstance(ru3_plt_v2_v3_web_disp, Quantity):
        ru3_plt_v2_v3_web_abs_disp = Quantity(
            value=abs(ru3_plt_v2_v3_web_disp.value),
            unit=ru3_plt_v2_v3_web_disp.unit,
        )
    dcr3_plt_v2_v3_web_disp = "n/a"
    if (
        isinstance(ru3_plt_v2_v3_web_disp, Quantity)
        and isinstance(phi_rn3_plt_v2_v3_web_q, Quantity)
        and ru3_plt_v2_v3_web_disp.unit == phi_rn3_plt_v2_v3_web_q.unit
        and abs(phi_rn3_plt_v2_v3_web_q.value) > 1e-12
    ):
        dcr3_plt_v2_v3_web_disp = _format_decimal(
            abs(ru3_plt_v2_v3_web_disp.value) / phi_rn3_plt_v2_v3_web_q.value
        )
    plt1_bolt_shear_v2_v3_result = _render_result_label("UNKNOWN")
    try:
        dcr3_plt_num = float(dcr3_plt_v2_v3_web_disp)
        plt1_bolt_shear_v2_v3_result = _render_result_label("PASS" if dcr3_plt_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.1.4 plate 1 block shear in v2 direction
    phi_rn4_plt_v2_web_q = _as_quantity(plt1_block_shear_v2_note.get("phi_rn4_plt_v2_web"))
    ru4_plt_v2_web_q = _as_quantity(plt1_block_shear_v2_note.get("ru4_plt_v2_web"))
    ru4_plt_v2_web_disp = _convert_ru_to_capacity_unit(ru4_plt_v2_web_q, phi_rn4_plt_v2_web_q)
    ru4_plt_v2_web_abs_disp: Quantity | None = None
    if isinstance(ru4_plt_v2_web_disp, Quantity):
        ru4_plt_v2_web_abs_disp = Quantity(value=abs(ru4_plt_v2_web_disp.value), unit=ru4_plt_v2_web_disp.unit)
    dcr4_plt_v2_web_disp = _format_text(plt1_block_shear_v2_note.get("dcr4_plt_v2_web"))
    if (
        isinstance(ru4_plt_v2_web_disp, Quantity)
        and isinstance(phi_rn4_plt_v2_web_q, Quantity)
        and ru4_plt_v2_web_disp.unit == phi_rn4_plt_v2_web_q.unit
        and abs(phi_rn4_plt_v2_web_q.value) > 1e-12
    ):
        dcr4_plt_v2_web_disp = _format_decimal(abs(ru4_plt_v2_web_disp.value) / phi_rn4_plt_v2_web_q.value)
    plt1_block_shear_v2_result = _render_result_label(plt1_block_shear_v2_note.get("result4_plt_v2_web"))
    try:
        dcr4_plt_num = float(dcr4_plt_v2_web_disp)
        plt1_block_shear_v2_result = _render_result_label("PASS" if dcr4_plt_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.1.5 plate 1 shear yielding in v2 direction
    phi_rn5_plt_v2_web_q = _as_quantity(plt1_shear_yielding_v2_note.get("phi_rn5_plt_v2_web"))
    ru5_plt_v2_web_q = _as_quantity(plt1_shear_yielding_v2_note.get("ru5_plt_v2_web"))
    ru5_plt_v2_web_disp = _convert_ru_to_capacity_unit(ru5_plt_v2_web_q, phi_rn5_plt_v2_web_q)
    ru5_plt_v2_web_abs_disp: Quantity | None = None
    if isinstance(ru5_plt_v2_web_disp, Quantity):
        ru5_plt_v2_web_abs_disp = Quantity(value=abs(ru5_plt_v2_web_disp.value), unit=ru5_plt_v2_web_disp.unit)
    dcr5_plt_v2_web_disp = _format_text(plt1_shear_yielding_v2_note.get("dcr5_plt_v2_web"))
    if (
        isinstance(ru5_plt_v2_web_disp, Quantity)
        and isinstance(phi_rn5_plt_v2_web_q, Quantity)
        and ru5_plt_v2_web_disp.unit == phi_rn5_plt_v2_web_q.unit
        and abs(phi_rn5_plt_v2_web_q.value) > 1e-12
    ):
        dcr5_plt_v2_web_disp = _format_decimal(abs(ru5_plt_v2_web_disp.value) / phi_rn5_plt_v2_web_q.value)
    plt1_shear_yielding_v2_result = _render_result_label(plt1_shear_yielding_v2_note.get("result5_plt_v2_web"))
    try:
        dcr5_plt_num = float(dcr5_plt_v2_web_disp)
        plt1_shear_yielding_v2_result = _render_result_label("PASS" if dcr5_plt_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.1.6 plate 1 shear rupture in v2 direction
    phi_rn6_plt_v2_web_q = _as_quantity(plt1_shear_rupture_v2_note.get("phi_rn6_plt_v2_web"))
    ru6_plt_v2_web_q = _as_quantity(plt1_shear_rupture_v2_note.get("ru6_plt_v2_web"))
    ru6_plt_v2_web_disp = _convert_ru_to_capacity_unit(ru6_plt_v2_web_q, phi_rn6_plt_v2_web_q)
    ru6_plt_v2_web_abs_disp: Quantity | None = None
    if isinstance(ru6_plt_v2_web_disp, Quantity):
        ru6_plt_v2_web_abs_disp = Quantity(value=abs(ru6_plt_v2_web_disp.value), unit=ru6_plt_v2_web_disp.unit)
    dcr6_plt_v2_web_disp = _format_text(plt1_shear_rupture_v2_note.get("dcr6_plt_v2_web"))
    if (
        isinstance(ru6_plt_v2_web_disp, Quantity)
        and isinstance(phi_rn6_plt_v2_web_q, Quantity)
        and ru6_plt_v2_web_disp.unit == phi_rn6_plt_v2_web_q.unit
        and abs(phi_rn6_plt_v2_web_q.value) > 1e-12
    ):
        dcr6_plt_v2_web_disp = _format_decimal(abs(ru6_plt_v2_web_disp.value) / phi_rn6_plt_v2_web_q.value)
    plt1_shear_rupture_v2_result = _render_result_label(plt1_shear_rupture_v2_note.get("result6_plt_v2_web"))
    try:
        dcr6_plt_num = float(dcr6_plt_v2_web_disp)
        plt1_shear_rupture_v2_result = _render_result_label("PASS" if dcr6_plt_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.2.1 plate 1 tearout in v3 direction
    phi_rn1_plt_v3_web_q = _as_quantity(plt1_tearout_v3_note.get("phi_rn1_plt_v3_web"))
    ru1_plt_v3_web_disp = _convert_ru_to_capacity_unit(ru_web_v3_max_vg_q, phi_rn1_plt_v3_web_q)
    ru1_plt_v3_web_abs_disp: Quantity | None = None
    if isinstance(ru1_plt_v3_web_disp, Quantity):
        ru1_plt_v3_web_abs_disp = Quantity(value=abs(ru1_plt_v3_web_disp.value), unit=ru1_plt_v3_web_disp.unit)
    dcr1_plt_v3_web_disp = "n/a"
    if (
        isinstance(ru1_plt_v3_web_disp, Quantity)
        and isinstance(phi_rn1_plt_v3_web_q, Quantity)
        and ru1_plt_v3_web_disp.unit == phi_rn1_plt_v3_web_q.unit
        and abs(phi_rn1_plt_v3_web_q.value) > 1e-12
    ):
        dcr1_plt_v3_web_disp = _format_decimal(abs(ru1_plt_v3_web_disp.value) / phi_rn1_plt_v3_web_q.value)
    plt1_tearout_v3_result = _render_result_label("UNKNOWN")
    try:
        dcr1_plt_v3_num = float(dcr1_plt_v3_web_disp)
        plt1_tearout_v3_result = _render_result_label("PASS" if dcr1_plt_v3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.2.2 plate 1 block shear in v3 direction
    ru2_plt_v3_web_q = _as_quantity(plt1_block_shear_v3_note.get("ru2_plt_v3_web"))
    phi_rn2_plt_v3_web_q = _as_quantity(plt1_block_shear_v3_note.get("phi_rn2_plt_v3_web"))
    ru2_plt_v3_web_disp = _convert_ru_to_capacity_unit(ru2_plt_v3_web_q, phi_rn2_plt_v3_web_q)
    ru2_plt_v3_web_abs_disp: Quantity | None = None
    if isinstance(ru2_plt_v3_web_disp, Quantity):
        ru2_plt_v3_web_abs_disp = Quantity(value=abs(ru2_plt_v3_web_disp.value), unit=ru2_plt_v3_web_disp.unit)
    dcr2_plt_v3_web_disp = _format_text(plt1_block_shear_v3_note.get("dcr2_plt_v3_web"))
    if (
        isinstance(ru2_plt_v3_web_disp, Quantity)
        and isinstance(phi_rn2_plt_v3_web_q, Quantity)
        and ru2_plt_v3_web_disp.unit == phi_rn2_plt_v3_web_q.unit
        and abs(phi_rn2_plt_v3_web_q.value) > 1e-12
    ):
        dcr2_plt_v3_web_disp = _format_decimal(abs(ru2_plt_v3_web_disp.value) / phi_rn2_plt_v3_web_q.value)
    plt1_block_shear_v3_result = _render_result_label(plt1_block_shear_v3_note.get("result2_plt_v3_web"))
    try:
        dcr2_plt_v3_num = float(dcr2_plt_v3_web_disp)
        plt1_block_shear_v3_result = _render_result_label("PASS" if dcr2_plt_v3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.2.3 plate 1 tension yielding in v3 direction
    ru3_plt_v3_web_q = _as_quantity(plt1_tension_yielding_v3_note.get("ru3_plt_v3_web"))
    phi_rn3_plt_v3_web_q = _as_quantity(plt1_tension_yielding_v3_note.get("phi_rn3_plt_v3_web"))
    ru3_plt_v3_web_disp = _convert_ru_to_capacity_unit(ru3_plt_v3_web_q, phi_rn3_plt_v3_web_q)
    ru3_plt_v3_web_abs_disp: Quantity | None = None
    if isinstance(ru3_plt_v3_web_disp, Quantity):
        ru3_plt_v3_web_abs_disp = Quantity(value=abs(ru3_plt_v3_web_disp.value), unit=ru3_plt_v3_web_disp.unit)
    dcr3_plt_v3_web_disp = _format_text(plt1_tension_yielding_v3_note.get("dcr3_plt_v3_web"))
    if (
        isinstance(ru3_plt_v3_web_disp, Quantity)
        and isinstance(phi_rn3_plt_v3_web_q, Quantity)
        and ru3_plt_v3_web_disp.unit == phi_rn3_plt_v3_web_q.unit
        and abs(phi_rn3_plt_v3_web_q.value) > 1e-12
    ):
        dcr3_plt_v3_web_disp = _format_decimal(abs(ru3_plt_v3_web_disp.value) / phi_rn3_plt_v3_web_q.value)
    plt1_tension_yielding_v3_result = _render_result_label(plt1_tension_yielding_v3_note.get("result3_plt_v3_web"))
    try:
        dcr3_plt_v3_num = float(dcr3_plt_v3_web_disp)
        plt1_tension_yielding_v3_result = _render_result_label("PASS" if dcr3_plt_v3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.2.4 plate 1 tension rupture in v3 direction
    ru4_plt_v3_web_q = _as_quantity(plt1_tension_rupture_v3_note.get("ru4_plt_v3_web"))
    phi_rn4_plt_v3_web_q = _as_quantity(plt1_tension_rupture_v3_note.get("phi_rn4_plt_v3_web"))
    ru4_plt_v3_web_disp = _convert_ru_to_capacity_unit(ru4_plt_v3_web_q, phi_rn4_plt_v3_web_q)
    ru4_plt_v3_web_abs_disp: Quantity | None = None
    if isinstance(ru4_plt_v3_web_disp, Quantity):
        ru4_plt_v3_web_abs_disp = Quantity(value=abs(ru4_plt_v3_web_disp.value), unit=ru4_plt_v3_web_disp.unit)
    dcr4_plt_v3_web_disp = _format_text(plt1_tension_rupture_v3_note.get("dcr4_plt_v3_web"))
    if (
        isinstance(ru4_plt_v3_web_disp, Quantity)
        and isinstance(phi_rn4_plt_v3_web_q, Quantity)
        and ru4_plt_v3_web_disp.unit == phi_rn4_plt_v3_web_q.unit
        and abs(phi_rn4_plt_v3_web_q.value) > 1e-12
    ):
        dcr4_plt_v3_web_disp = _format_decimal(abs(ru4_plt_v3_web_disp.value) / phi_rn4_plt_v3_web_q.value)
    plt1_tension_rupture_v3_result = _render_result_label(plt1_tension_rupture_v3_note.get("result4_plt_v3_web"))
    try:
        dcr4_plt_v3_num = float(dcr4_plt_v3_web_disp)
        plt1_tension_rupture_v3_result = _render_result_label("PASS" if dcr4_plt_v3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.3.1 plate 1 flexural yielding around axis 1
    ru1_plt_m1_web_q = _as_quantity(plt1_flex_yielding_m1_note.get("ru1_plt_m1_web"))
    phi_mn1_plt_m1_web_q = _as_quantity(plt1_flex_yielding_m1_note.get("phi_mn1_plt_m1_web"))
    ru1_plt_m1_web_disp = _convert_ru_to_capacity_unit(ru1_plt_m1_web_q, phi_mn1_plt_m1_web_q)
    ru1_plt_m1_web_abs_disp: Quantity | None = None
    if isinstance(ru1_plt_m1_web_disp, Quantity):
        ru1_plt_m1_web_abs_disp = Quantity(value=abs(ru1_plt_m1_web_disp.value), unit=ru1_plt_m1_web_disp.unit)
    dcr1_plt_m1_web_disp = _format_text(plt1_flex_yielding_m1_note.get("dcr1_plt_m1_web"))
    if (
        isinstance(ru1_plt_m1_web_disp, Quantity)
        and isinstance(phi_mn1_plt_m1_web_q, Quantity)
        and ru1_plt_m1_web_disp.unit == phi_mn1_plt_m1_web_q.unit
        and abs(phi_mn1_plt_m1_web_q.value) > 1e-12
    ):
        dcr1_plt_m1_web_disp = _format_decimal(abs(ru1_plt_m1_web_disp.value) / phi_mn1_plt_m1_web_q.value)
    plt1_flex_yielding_m1_result = _render_result_label(plt1_flex_yielding_m1_note.get("result1_plt_m1_web"))
    try:
        dcr1_plt_m1_num = float(dcr1_plt_m1_web_disp)
        plt1_flex_yielding_m1_result = _render_result_label("PASS" if dcr1_plt_m1_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.3.2 plate 1 LTB around axis 1
    ru2_plt_m1_web_q = _as_quantity(plt1_ltb_m1_note.get("ru2_plt_m1_web"))
    phi_mn2_plt_m1_web_q = _as_quantity(plt1_ltb_m1_note.get("phi_mn2_plt_m1_web"))
    ru2_plt_m1_web_disp = _convert_ru_to_capacity_unit(ru2_plt_m1_web_q, phi_mn2_plt_m1_web_q)
    ru2_plt_m1_web_abs_disp: Quantity | None = None
    if isinstance(ru2_plt_m1_web_disp, Quantity):
        ru2_plt_m1_web_abs_disp = Quantity(value=abs(ru2_plt_m1_web_disp.value), unit=ru2_plt_m1_web_disp.unit)
    dcr2_plt_m1_web_disp = _format_text(plt1_ltb_m1_note.get("dcr2_plt_m1_web"))
    if (
        isinstance(ru2_plt_m1_web_disp, Quantity)
        and isinstance(phi_mn2_plt_m1_web_q, Quantity)
        and ru2_plt_m1_web_disp.unit == phi_mn2_plt_m1_web_q.unit
        and abs(phi_mn2_plt_m1_web_q.value) > 1e-12
    ):
        dcr2_plt_m1_web_disp = _format_decimal(abs(ru2_plt_m1_web_disp.value) / phi_mn2_plt_m1_web_q.value)
    plt1_ltb_m1_result = _render_result_label(plt1_ltb_m1_note.get("result2_plt_m1_web"))
    try:
        dcr2_plt_m1_num = float(dcr2_plt_m1_web_disp)
        plt1_ltb_m1_result = _render_result_label("PASS" if dcr2_plt_m1_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 5.3.3 plate 1 flexural rupture around axis 1
    ru3_plt_m1_web_q = _as_quantity(plt1_flex_rupture_m1_note.get("ru3_plt_m1_web"))
    phi_rn3_plt_m1_web_q = _as_quantity(plt1_flex_rupture_m1_note.get("phi_rn3_plt_m1_web"))
    ru3_plt_m1_web_disp = _convert_ru_to_capacity_unit(ru3_plt_m1_web_q, phi_rn3_plt_m1_web_q)
    ru3_plt_m1_web_abs_disp: Quantity | None = None
    if isinstance(ru3_plt_m1_web_disp, Quantity):
        ru3_plt_m1_web_abs_disp = Quantity(value=abs(ru3_plt_m1_web_disp.value), unit=ru3_plt_m1_web_disp.unit)
    dcr3_plt_m1_web_disp = _format_text(plt1_flex_rupture_m1_note.get("dcr3_plt_m1_web"))
    if (
        isinstance(ru3_plt_m1_web_disp, Quantity)
        and isinstance(phi_rn3_plt_m1_web_q, Quantity)
        and ru3_plt_m1_web_disp.unit == phi_rn3_plt_m1_web_q.unit
        and abs(phi_rn3_plt_m1_web_q.value) > 1e-12
    ):
        dcr3_plt_m1_web_disp = _format_decimal(abs(ru3_plt_m1_web_disp.value) / phi_rn3_plt_m1_web_q.value)
    plt1_flex_rupture_m1_result = _render_result_label(plt1_flex_rupture_m1_note.get("result3_plt_m1_web"))
    try:
        dcr3_plt_m1_num = float(dcr3_plt_m1_web_disp)
        plt1_flex_rupture_m1_result = _render_result_label("PASS" if dcr3_plt_m1_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 4.2.1 tearout metrics in v3 direction
    phi_rn1_web_v3_q = _as_quantity(tearout_v3_note.get("phi_rn1_web_v3_vg"))
    ru1_web_v3_vg_disp = _convert_ru_to_capacity_unit(ru_web_v3_max_vg_q, phi_rn1_web_v3_q)
    ru1_web_v3_vg_abs_disp: Quantity | None = None
    if isinstance(ru1_web_v3_vg_disp, Quantity):
        ru1_web_v3_vg_abs_disp = Quantity(value=abs(ru1_web_v3_vg_disp.value), unit=ru1_web_v3_vg_disp.unit)
    dcr1_web_v3_vg_disp = _format_text(tearout_v3_note.get("dcr1_web_v3_vg"))
    if (
        isinstance(ru1_web_v3_vg_disp, Quantity)
        and isinstance(phi_rn1_web_v3_q, Quantity)
        and ru1_web_v3_vg_disp.unit == phi_rn1_web_v3_q.unit
        and abs(phi_rn1_web_v3_q.value) > 1e-12
    ):
        dcr1_web_v3_vg_disp = _format_decimal(abs(ru1_web_v3_vg_disp.value) / phi_rn1_web_v3_q.value)
    tearout_v3_result = _render_result_label(tearout_v3_note.get("result1_web_v3_vg"))
    try:
        dcr1_v3_num = float(dcr1_web_v3_vg_disp)
        tearout_v3_result = _render_result_label("PASS" if dcr1_v3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 4.2.2 tension rupture metrics in v3 direction
    ru3_v3_vg_q = _as_quantity(tension_rupture_v3_note.get("ru3_v3_vg"))
    phi_rn3_v3_q = _as_quantity(tension_rupture_v3_note.get("phi_rn3_v3_vg"))
    ru3_v3_vg_disp = _convert_ru_to_capacity_unit(ru3_v3_vg_q, phi_rn3_v3_q)
    ru3_v3_vg_abs_disp: Quantity | None = None
    if isinstance(ru3_v3_vg_disp, Quantity):
        ru3_v3_vg_abs_disp = Quantity(value=abs(ru3_v3_vg_disp.value), unit=ru3_v3_vg_disp.unit)
    dcr3_v3_vg_disp = _format_text(tension_rupture_v3_note.get("dcr3_v3_vg"))
    if (
        isinstance(ru3_v3_vg_disp, Quantity)
        and isinstance(phi_rn3_v3_q, Quantity)
        and ru3_v3_vg_disp.unit == phi_rn3_v3_q.unit
        and abs(phi_rn3_v3_q.value) > 1e-12
    ):
        dcr3_v3_vg_disp = _format_decimal(abs(ru3_v3_vg_disp.value) / phi_rn3_v3_q.value)
    tension_rupture_v3_result = _render_result_label(tension_rupture_v3_note.get("result3_v3_vg"))
    try:
        dcr3_v3_num = float(dcr3_v3_vg_disp)
        tension_rupture_v3_result = _render_result_label("PASS" if dcr3_v3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 4.2.3 block shear metrics in v3 direction
    ru4_web_v3_vg_q = _as_quantity(block_shear_v3_note.get("ru4_web_v3_vg"))
    phi_rn4_web_v3_q = _as_quantity(block_shear_v3_note.get("phi_rn4_web_v3_vg"))
    ru4_web_v3_vg_disp = _convert_ru_to_capacity_unit(ru4_web_v3_vg_q, phi_rn4_web_v3_q)
    ru4_web_v3_vg_abs_disp: Quantity | None = None
    if isinstance(ru4_web_v3_vg_disp, Quantity):
        ru4_web_v3_vg_abs_disp = Quantity(value=abs(ru4_web_v3_vg_disp.value), unit=ru4_web_v3_vg_disp.unit)
    dcr4_web_v3_vg_disp = _format_text(block_shear_v3_note.get("dcr4_web_v3_vg"))
    if (
        isinstance(ru4_web_v3_vg_disp, Quantity)
        and isinstance(phi_rn4_web_v3_q, Quantity)
        and ru4_web_v3_vg_disp.unit == phi_rn4_web_v3_q.unit
        and abs(phi_rn4_web_v3_q.value) > 1e-12
    ):
        dcr4_web_v3_vg_disp = _format_decimal(abs(ru4_web_v3_vg_disp.value) / phi_rn4_web_v3_q.value)
    block_shear_v3_result = _render_result_label(block_shear_v3_note.get("result4_web_v3_vg"))
    try:
        dcr4_v3_num = float(dcr4_web_v3_vg_disp)
        block_shear_v3_result = _render_result_label("PASS" if dcr4_v3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 4.1.2 bearing (aplatamiento) metrics
    phi_rn2_web_q = _as_quantity(bearing_note.get("phi_rn2_web_v2_vg"))
    ru2_web_v2_vg_disp = _convert_ru_to_capacity_unit(ru_web_vg_q, phi_rn2_web_q)
    ru2_web_v2_vg_abs_disp: Quantity | None = None
    if isinstance(ru2_web_v2_vg_disp, Quantity):
        ru2_web_v2_vg_abs_disp = Quantity(value=abs(ru2_web_v2_vg_disp.value), unit=ru2_web_v2_vg_disp.unit)
    dcr2_web_v2_vg_disp = "n/a"
    if (
        isinstance(ru2_web_v2_vg_disp, Quantity)
        and isinstance(phi_rn2_web_q, Quantity)
        and ru2_web_v2_vg_disp.unit == phi_rn2_web_q.unit
        and abs(phi_rn2_web_q.value) > 1e-12
    ):
        dcr2_web_v2_vg_disp = _format_decimal(abs(ru2_web_v2_vg_disp.value) / phi_rn2_web_q.value)
    bearing_result = _render_result_label("UNKNOWN")
    try:
        dcr2_num = float(dcr2_web_v2_vg_disp)
        bearing_result = _render_result_label("PASS" if dcr2_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 4.1.3 bolt shear rupture metrics
    phi_rn3_web_q = _as_quantity(bolt_shear_note.get("phi_rn3_web_v2_vg"))
    ru3_web_v2_vg_disp = _convert_ru_to_capacity_unit(ru_web_vg_q, phi_rn3_web_q)
    ru3_web_v2_vg_abs_disp: Quantity | None = None
    if isinstance(ru3_web_v2_vg_disp, Quantity):
        ru3_web_v2_vg_abs_disp = Quantity(value=abs(ru3_web_v2_vg_disp.value), unit=ru3_web_v2_vg_disp.unit)
    dcr3_web_v2_vg_disp = "n/a"
    if (
        isinstance(ru3_web_v2_vg_disp, Quantity)
        and isinstance(phi_rn3_web_q, Quantity)
        and ru3_web_v2_vg_disp.unit == phi_rn3_web_q.unit
        and abs(phi_rn3_web_q.value) > 1e-12
    ):
        dcr3_web_v2_vg_disp = _format_decimal(abs(ru3_web_v2_vg_disp.value) / phi_rn3_web_q.value)
    bolt_shear_result = _render_result_label("UNKNOWN")
    try:
        dcr3_num = float(dcr3_web_v2_vg_disp)
        bolt_shear_result = _render_result_label("PASS" if dcr3_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 4.1.4 web shear rupture metrics (J4.3)
    ru4_web_v2_vg_q = _as_quantity(web_shear_rupture_note.get("ru4_web_v2_vg"))
    phi_rn4_web_q = _as_quantity(web_shear_rupture_note.get("phi_rn4_web_v2_vg"))
    ru4_web_v2_vg_disp = _convert_ru_to_capacity_unit(ru4_web_v2_vg_q, phi_rn4_web_q)
    ru4_web_v2_vg_abs_disp: Quantity | None = None
    if isinstance(ru4_web_v2_vg_disp, Quantity):
        ru4_web_v2_vg_abs_disp = Quantity(value=abs(ru4_web_v2_vg_disp.value), unit=ru4_web_v2_vg_disp.unit)
    dcr4_web_v2_vg_disp = _format_text(web_shear_rupture_note.get("dcr4_web_v2_vg"))
    if (
        isinstance(ru4_web_v2_vg_disp, Quantity)
        and isinstance(phi_rn4_web_q, Quantity)
        and ru4_web_v2_vg_disp.unit == phi_rn4_web_q.unit
        and abs(phi_rn4_web_q.value) > 1e-12
    ):
        dcr4_web_v2_vg_disp = _format_decimal(abs(ru4_web_v2_vg_disp.value) / phi_rn4_web_q.value)
    web_shear_rupture_result = _render_result_label(web_shear_rupture_note.get("result4_web_v2_vg"))
    try:
        dcr4_num = float(dcr4_web_v2_vg_disp)
        web_shear_rupture_result = _render_result_label("PASS" if dcr4_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    # 4.1.5 web block shear metrics (J4-5)
    ru5_web_v2_vg_q = _as_quantity(web_block_shear_note.get("ru5_web_v2_vg"))
    phi_rn5_web_q = _as_quantity(web_block_shear_note.get("phi_rn5_web_v2_vg"))
    ru5_web_v2_vg_disp = _convert_ru_to_capacity_unit(ru5_web_v2_vg_q, phi_rn5_web_q)
    ru5_web_v2_vg_abs_disp: Quantity | None = None
    if isinstance(ru5_web_v2_vg_disp, Quantity):
        ru5_web_v2_vg_abs_disp = Quantity(value=abs(ru5_web_v2_vg_disp.value), unit=ru5_web_v2_vg_disp.unit)
    dcr5_web_v2_vg_disp = _format_text(web_block_shear_note.get("dcr5_web_v2_vg"))
    if (
        isinstance(ru5_web_v2_vg_disp, Quantity)
        and isinstance(phi_rn5_web_q, Quantity)
        and ru5_web_v2_vg_disp.unit == phi_rn5_web_q.unit
        and abs(phi_rn5_web_q.value) > 1e-12
    ):
        dcr5_web_v2_vg_disp = _format_decimal(abs(ru5_web_v2_vg_disp.value) / phi_rn5_web_q.value)
    web_block_shear_result = _render_result_label(web_block_shear_note.get("result5_web_v2_vg"))
    try:
        dcr5_num = float(dcr5_web_v2_vg_disp)
        web_block_shear_result = _render_result_label("PASS" if dcr5_num <= 1.0 else "FAIL")
    except (TypeError, ValueError):
        pass
    web_block_shear_result_text = "Cumple"
    if "No aplica" in web_block_shear_result:
        web_block_shear_result_text = "No aplica (cumple)"
    elif "No cumple" in web_block_shear_result:
        web_block_shear_result_text = "No cumple"
    lines.extend(
        [
            "",
            "## Paso 4 - Revisión de resistencia de la viga",
            "",
            "### 4.1 Revisión de capacidad a cortante en el alma en direccion 2",
            "",
            "#### 4.1.1. ELR #1: Desgarramiento en la perforacion del perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`",
            (
                "- Ecuaciones: `lc_blt_web_y = p_blt_web - dh.1; "
                "Rn1_web_v2_vg = C*lc_blt_web_y*tw_vg*Fu_vg; "
                "phi*Rn1_web_v2_vg = phi_fragil*Rn1_web_v2_vg; "
                "DCR1_web_v2_vg = Ru1_web_v2_vg/phi*Rn1_web_v2_vg`"
            ),
            f"- Fu_vg: `{_format_quantity(tearout_note.get('fu_vg'))}`",
            f"- tw_vg: `{_format_quantity(tearout_note.get('tw_vg'))}`",
            f"- p_blt_web: `{_format_quantity(tearout_note.get('p_blt_web'))}`",
            f"- dh.1: `{_format_quantity(tearout_note.get('dh_1'))}`",
            f"- lc_blt_web_y: `{_format_quantity(tearout_note.get('lc_blt_web_y'))}`",
            f"- C: `{_format_text(tearout_note.get('coefficient'))}`",
            f"- phi_fragil: `{_format_text(tearout_note.get('phi_fragil'))}`",
            f"- Rn1_web_v2_vg: `{_format_quantity(tearout_note.get('rn1_web_v2_vg') or tearout_note.get('rn_web_ind_v2_vg') or tearout_note.get('rn1_web_ind_v2_vg'))}`",
            f"- phi*Rn1_web_v2_vg: `{_format_quantity(tearout_note.get('phi_rn1_web_v2_vg') or tearout_note.get('phi_rn_web_v2_vg') or tearout_note.get('phi_rn1_web_v2_vg'))}`",
            f"- Ru1_web_v2_vg: `{_format_quantity(ru_web_v2_vg_abs_disp.model_dump() if isinstance(ru_web_v2_vg_abs_disp, Quantity) else None)}`",
            f"- DCR1_web_v2_vg: `{dcr1_web_v2_vg_disp}`",
            f"- Resultado: {tearout_result}",
            "",
            "#### 4.1.2. ELR #2: Aplastamiento en la perforacion del perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(a)`",
            (
                "- Ecuaciones: `Rn2_web_v2-v3_vg = C*db_blt_web*tw_vg*Fu_vg; "
                "phi*Rn2_web_v2-v3_vg = phi_fragil*Rn2_web_v2-v3_vg; "
                "DCR2_web_v2-v3_vg = Ru2_web_v2-v3_vg/phi*Rn2_web_v2-v3_vg`"
            ),
            f"- Fu_vg: `{_format_quantity(bearing_note.get('fu_vg'))}`",
            f"- tw_vg: `{_format_quantity(bearing_note.get('tw_vg'))}`",
            f"- db_blt_web: `{_format_quantity(bearing_note.get('db_blt_web'))}`",
            f"- C: `{_format_text(bearing_note.get('coefficient'))}`",
            f"- phi_fragil: `{_format_text(bearing_note.get('phi_fragil'))}`",
            f"- Rn2_web_v2-v3_vg: `{_format_quantity(bearing_note.get('rn2_web_v2_vg'))}`",
            f"- phi*Rn2_web_v2-v3_vg: `{_format_quantity(bearing_note.get('phi_rn2_web_v2_vg'))}`",
            f"- Ru2_web_v2-v3_vg = Ru_web_vg: `{_format_quantity(ru2_web_v2_vg_abs_disp.model_dump() if isinstance(ru2_web_v2_vg_abs_disp, Quantity) else None)}`",
            f"- DCR2_web_v2-v3_vg: `{dcr2_web_v2_vg_disp}`",
            f"- Resultado: {bearing_result}",
            "",
            "#### 4.1.3. ELR #3: Rotura por cortante en el perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.7`",
            (
                "- Ecuaciones: `Rn3_web_v2-v3_vg = Ab_blt_web*Fnv_blt_web; "
                "phi*Rn3_web_v2-v3_vg = phi_fragil*Rn3_web_v2-v3_vg; "
                "DCR3_web_v2-v3_vg = Ru3_web_v2-v3_vg/phi*Rn3_web_v2-v3_vg`"
            ),
            f"- db_blt_web: `{_format_quantity(bolt_shear_note.get('db_blt_web'))}`",
            f"- Ab_blt_web: `{_format_quantity(bolt_shear_note.get('ab_blt_web'))}`",
            f"- Fnv_blt_web: `{_format_quantity(bolt_shear_note.get('fnv_blt_web'))}`",
            f"- phi_fragil: `{_format_text(bolt_shear_note.get('phi_fragil'))}`",
            f"- Rn3_web_v2-v3_vg: `{_format_quantity(bolt_shear_note.get('rn3_web_v2_vg'))}`",
            f"- phi*Rn3_web_v2-v3_vg: `{_format_quantity(bolt_shear_note.get('phi_rn3_web_v2_vg'))}`",
            f"- Ru3_web_v2-v3_vg = Ru_web_vg: `{_format_quantity(ru3_web_v2_vg_abs_disp.model_dump() if isinstance(ru3_web_v2_vg_abs_disp, Quantity) else None)}`",
            f"- DCR3_web_v2-v3_vg: `{dcr3_web_v2_vg_disp}`",
            f"- Resultado: {bolt_shear_result}",
            "",
            "#### 4.1.4. ELR #4: Rotura por cortante de la viga",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J4.2(b) (DRY: compute_element_shear_rupture_strength_j43)`",
            (
                "- Ecuaciones: `A_vg = d_vg*tw_vg; "
                "Anv_web_v2_vg = A_vg - n_blt_web_y*(dh.1+1.8mm)*tw_vg; "
                "Rn4_web_v2_vg = 0.60*Fu_vg*Anv_web_v2_vg; "
                "phi*Rn4_web_v2_vg = phi_fragil*Rn4_web_v2_vg; "
                "DCR4_web_v2_vg = Ru4_web_v2_vg/phi*Rn4_web_v2_vg`"
            ),
            f"- Fu_vg: `{_format_quantity(web_shear_rupture_note.get('fu_vg'))}`",
            f"- tw_vg: `{_format_quantity(web_shear_rupture_note.get('tw_vg'))}`",
            f"- A_vg: `{_format_quantity(web_shear_rupture_note.get('a_vg'))}`",
            f"- n_blt_web_y: `{_format_text(web_shear_rupture_note.get('n_blt_web_y'))}`",
            f"- dh.1: `{_format_quantity(web_shear_rupture_note.get('dh_1'))}`",
            f"- Anv_web_v2_vg: `{_format_quantity(web_shear_rupture_note.get('anv_web_v2_vg'))}`",
            f"- phi_fragil: `{_format_text(web_shear_rupture_note.get('phi_fragil'))}`",
            f"- Rn4_web_v2_vg: `{_format_quantity(web_shear_rupture_note.get('rn4_web_v2_vg'))}`",
            f"- phi*Rn4_web_v2_vg: `{_format_quantity(web_shear_rupture_note.get('phi_rn4_web_v2_vg'))}`",
            f"- Ru4_web_v2_vg = Vu2_sp: `{_format_quantity(ru4_web_v2_vg_abs_disp.model_dump() if isinstance(ru4_web_v2_vg_abs_disp, Quantity) else None)}`",
            f"- DCR4_web_v2_vg: `{dcr4_web_v2_vg_disp}`",
            f"- Resultado: {web_shear_rupture_result}",
            "",
            "#### 4.1.5. ELR #5: Bloque de cortante en alma de viga",
            "",
            "- Clausula: `Documento: AISC 360-22w | Seccion: J4.3 (DRY: compute_block_shear_strength_j45)`",
            (
                "- Ecuaciones: `Agv_web_v2_vg = p_blt_web*(n_blt_web_y - 1)*tw_vg + (Le_blt_web_y3 - tf_vg)*tw_vg + tf_vg*bf_vg; "
                "Anv_web_v2_vg = Agv_web_v2_vg - (n_blt_web_y - 0.5)*tw_vg*(dh.1 + 1.80mm); "
                "Agt_web_v2_vg = g_blt_web*(n_blt_web_x - 1)*tw_vg + Le_blt_web_x1*tw_vg; "
                "Ant_web_v2_vg = Agt_web_v2_vg - (n_blt_web_x - 0.5)*tw_vg*(dh.1 + 1.80mm); "
                "Rn5_1_web_v2_vg = 0.60*Fu_vg*Anv_web_v2_vg + Ubs_web_v2_vg*Fu_vg*Ant_web_v2_vg; "
                "Rn5_2_web_v2_vg = 0.60*Fy_vg*Agv_web_v2_vg + Ubs_web_v2_vg*Fu_vg*Ant_web_v2_vg; "
                "Rn5_web_v2_vg = min(Rn5_1_web_v2_vg, Rn5_2_web_v2_vg); "
                "phi*Rn5_web_v2_vg = phi_fragil*Rn5_web_v2_vg; "
                "DCR5_web_v2_vg = Ru5_web_v2_vg/phi*Rn5_web_v2_vg`"
            ),
            f"- Fu_vg: `{_format_quantity(web_block_shear_note.get('fu_vg'))}`",
            f"- Fy_vg: `{_format_quantity(web_block_shear_note.get('fy_vg'))}`",
            f"- tw_vg: `{_format_quantity(web_block_shear_note.get('tw_vg'))}`",
            f"- tf_vg: `{_format_quantity(web_block_shear_note.get('tf_vg'))}`",
            f"- bf_vg: `{_format_quantity(web_block_shear_note.get('bf_vg'))}`",
            f"- n_blt_web_x: `{_format_text(web_block_shear_note.get('n_blt_web_x'))}`",
            f"- n_blt_web_y: `{_format_text(web_block_shear_note.get('n_blt_web_y'))}`",
            f"- g_blt_web: `{_format_quantity(web_block_shear_note.get('g_blt_web'))}`",
            f"- p_blt_web: `{_format_quantity(web_block_shear_note.get('p_blt_web'))}`",
            f"- Le_blt_web_x1: `{_format_quantity(web_block_shear_note.get('le_blt_web_x1'))}`",
            f"- Le_blt_web_y3: `{_format_quantity(web_block_shear_note.get('le_blt_web_y3'))}`",
            f"- dh.1: `{_format_quantity(web_block_shear_note.get('dh_1'))}`",
            f"- Ubs_web_v2_vg (inp): `{_format_text(web_block_shear_note.get('ubs_web_v2_vg'))}`",
            f"- Agv_web_v2_vg: `{_format_quantity(web_block_shear_note.get('agv_web_v2_vg'))}`",
            f"- Anv_web_v2_vg: `{_format_quantity(web_block_shear_note.get('anv5_web_v2_vg'))}`",
            f"- Agt_web_v2_vg: `{_format_quantity(web_block_shear_note.get('agt_web_v2_vg'))}`",
            f"- Ant_web_v2_vg: `{_format_quantity(web_block_shear_note.get('ant_web_v2_vg'))}`",
            f"- phi_fragil: `{_format_text(web_block_shear_note.get('phi_fragil'))}`",
            f"- Rn5_1_web_v2_vg: `{_format_quantity(web_block_shear_note.get('rn5_1_web_v2_vg'))}`",
            f"- Rn5_2_web_v2_vg: `{_format_quantity(web_block_shear_note.get('rn5_2_web_v2_vg'))}`",
            f"- Rn5_web_v2_vg: `{_format_quantity(web_block_shear_note.get('rn5_web_v2_vg'))}`",
            f"- phi*Rn5_web_v2_vg: `{_format_quantity(web_block_shear_note.get('phi_rn5_web_v2_vg'))}`",
            f"- Ru5_web_v2_vg = Vu2_sp: `{_format_quantity(ru5_web_v2_vg_abs_disp.model_dump() if isinstance(ru5_web_v2_vg_abs_disp, Quantity) else None)}`",
            f"- DCR5_web_v2_vg: `{dcr5_web_v2_vg_disp}`",
            f"- Resultado: `{web_block_shear_result_text}`",
            "",
            "### 4.2 Revisión de capacidad a traccion en el alma en direccion 3",
            "",
            "#### 4.2.1. ELR #1: Desgarramiento en la perforacion del perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`",
            (
                "- Ecuaciones: `lc_web_v3_vg = min(g_blt_web - dh.1, Le_blt_web_x1 - 0.5*dh.1); "
                "Rn1_web_v3_vg = C*lc_web_v3_vg*tw_vg*Fu_vg; "
                "phi*Rn1_web_v3_vg = phi_fragil*Rn1_web_v3_vg; "
                "DCR1_web_v3_vg = Ru1_web_v3_vg/phi*Rn1_web_v3_vg`"
            ),
            f"- Fu_vg: `{_format_quantity(tearout_v3_note.get('fu_vg'))}`",
            f"- tw_vg: `{_format_quantity(tearout_v3_note.get('tw_vg'))}`",
            f"- g_blt_web: `{_format_quantity(tearout_v3_note.get('g_blt_web'))}`",
            f"- Le_blt_web_x1: `{_format_quantity(tearout_v3_note.get('le_blt_web_x1'))}`",
            f"- dh.1: `{_format_quantity(tearout_v3_note.get('dh_1'))}`",
            f"- lc_web_v3_vg: `{_format_quantity(tearout_v3_note.get('lc_web_v3_vg'))}`",
            f"- C: `{_format_text(tearout_v3_note.get('coefficient'))}`",
            f"- phi_fragil: `{_format_text(tearout_v3_note.get('phi_fragil'))}`",
            f"- Rn1_web_v3_vg: `{_format_quantity(tearout_v3_note.get('rn1_web_v3_vg'))}`",
            f"- phi*Rn1_web_v3_vg: `{_format_quantity(tearout_v3_note.get('phi_rn1_web_v3_vg'))}`",
            f"- Ru1_web_v3_vg = Ru_web_v3_max_vg: `{_format_quantity(ru1_web_v3_vg_abs_disp.model_dump() if isinstance(ru1_web_v3_vg_abs_disp, Quantity) else None)}`",
            f"- DCR1_web_v3_vg: `{dcr1_web_v3_vg_disp}`",
            f"- Resultado: {tearout_v3_result}",
            "",
            "#### 4.2.2. ELR #2: Rotura por traccion de la viga",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J4.1.(b)`",
            (
                "- Ecuaciones: `si 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web - n_blt_web_y*(dh.1 + 1.80mm) <= T_vg -> "
                "Ant_v3_vg = tw_vg*(2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web - n_blt_web_y*(dh.1 + 1.80mm)); "
                "si no -> Ant_v3_vg = A_vg - n_blt_web_y*(dh.1 + 1.80mm)*tw_vg; "
                "si n_blt_web_x <= 1 -> U_v3_vg = T_vg*tw_vg/A_vg; "
                "si n_blt_web_x > 1 -> U_v3_vg = 1 - 0.5*tw_vg/(n_blt_web_x*g_blt_web); "
                "Ae_v3_vg = Ant_v3_vg*U_v3_vg; "
                "Rn3_v3_vg = Fu_vg*Ae_v3_vg; "
                "phi*Rn3_v3_vg = phi_fragil*Rn3_v3_vg; "
                "Ru3_v3_vg = Pu_sp*alpha_Pu_web; "
                "DCR3_v3_vg = Ru3_v3_vg/phi*Rn3_v3_vg`"
            ),
            f"- Fu_vg: `{_format_quantity(tension_rupture_v3_note.get('fu_vg'))}`",
            f"- T_vg: `{_format_quantity(tension_rupture_v3_note.get('t_vg'))}`",
            f"- tw_vg: `{_format_quantity(tension_rupture_v3_note.get('tw_vg'))}`",
            f"- A_vg: `{_format_quantity(tension_rupture_v3_note.get('a_vg'))}`",
            f"- n_blt_web_y: `{_format_text(tension_rupture_v3_note.get('n_blt_web_y'))}`",
            f"- dh.1: `{_format_quantity(tension_rupture_v3_note.get('dh_1'))}`",
            f"- Ant_v3_vg: `{_format_quantity(tension_rupture_v3_note.get('ant_v3_vg'))}`",
            f"- n_blt_web_x: `{_format_text(tension_rupture_v3_note.get('n_blt_web_x'))}`",
            f"- g_blt_web: `{_format_quantity(tension_rupture_v3_note.get('g_blt_web'))}`",
            f"- U_v3_vg: `{_format_text(tension_rupture_v3_note.get('u_v3_vg'))}`",
            f"- Ae_v3_vg: `{_format_quantity(tension_rupture_v3_note.get('ae_v3_vg'))}`",
            f"- phi_fragil: `{_format_text(tension_rupture_v3_note.get('phi_fragil'))}`",
            f"- Rn3_v3_vg: `{_format_quantity(tension_rupture_v3_note.get('rn3_v3_vg'))}`",
            f"- phi*Rn3_v3_vg: `{_format_quantity(tension_rupture_v3_note.get('phi_rn3_v3_vg'))}`",
            f"- Pu_sp: `{_format_quantity(tension_rupture_v3_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(tension_rupture_v3_note.get('alpha_pu_web'))}`",
            f"- Ru3_v3_vg = Pu_sp*alpha_Pu_web: `{_format_quantity(ru3_v3_vg_abs_disp.model_dump() if isinstance(ru3_v3_vg_abs_disp, Quantity) else None)}`",
            f"- DCR3_v3_vg: `{dcr3_v3_vg_disp}`",
            f"- Resultado: {tension_rupture_v3_result}",
            "",
            "#### 4.2.3. ELR #3: Bloque de cortante en alma de viga",
            "",
            "- Clausula: `Documento: AISC 360-22w | Seccion: J4.3 (DRY: compute_block_shear_strength_j45)`",
            (
                "- Ecuaciones: `Agv_web_v3_vg = 2*(g_blt_web*(n_blt_web_x - 1)*tw_vg + Le_blt_web_x1*tw_vg); "
                "Anv_web_v3_vg = 2*(0.5*Agv_web_v3_vg - (n_blt_web_x - 0.5)*tw_vg*(dh.1 + 1.80mm)); "
                "Agt_web_v3_vg = p_blt_web*(n_blt_web_y - 1)*tw_vg; "
                "Ant_web_v3_vg = Agt_web_v3_vg - (n_blt_web_y - 1)*tw_vg*(dh.1 + 1.80mm); "
                "Rn4_1_web_v3_vg = 0.60*Fu_vg*Anv_web_v3_vg + Ubs_web_v3_vg*Fu_vg*Ant_web_v3_vg; "
                "Rn4_2_web_v3_vg = 0.60*Fy_vg*Agv_web_v3_vg + Ubs_web_v3_vg*Fu_vg*Ant_web_v3_vg; "
                "Rn4_web_v3_vg = min(Rn4_1_web_v3_vg, Rn4_2_web_v3_vg); "
                "phi*Rn4_web_v3_vg = phi_fragil*Rn4_web_v3_vg; "
                "Ru4_web_v3_vg = Pu_sp*alpha_Pu_web; "
                "DCR4_web_v3_vg = Ru4_web_v3_vg/phi*Rn4_web_v3_vg`"
            ),
            f"- Fu_vg: `{_format_quantity(block_shear_v3_note.get('fu_vg'))}`",
            f"- Fy_vg: `{_format_quantity(block_shear_v3_note.get('fy_vg'))}`",
            f"- tw_vg: `{_format_quantity(block_shear_v3_note.get('tw_vg'))}`",
            f"- n_blt_web_x: `{_format_text(block_shear_v3_note.get('n_blt_web_x'))}`",
            f"- n_blt_web_y: `{_format_text(block_shear_v3_note.get('n_blt_web_y'))}`",
            f"- g_blt_web: `{_format_quantity(block_shear_v3_note.get('g_blt_web'))}`",
            f"- p_blt_web: `{_format_quantity(block_shear_v3_note.get('p_blt_web'))}`",
            f"- Le_blt_web_x1: `{_format_quantity(block_shear_v3_note.get('le_blt_web_x1'))}`",
            f"- dh.1: `{_format_quantity(block_shear_v3_note.get('dh_1'))}`",
            f"- Ubs_web_v3_vg (inp): `{_format_text(block_shear_v3_note.get('ubs_web_v3_vg'))}`",
            f"- Agv_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('agv_web_v3_vg'))}`",
            f"- Anv_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('anv_web_v3_vg'))}`",
            f"- Agt_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('agt_web_v3_vg'))}`",
            f"- Ant_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('ant_web_v3_vg'))}`",
            f"- phi_fragil: `{_format_text(block_shear_v3_note.get('phi_fragil'))}`",
            f"- Rn4_1_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('rn4_1_web_v3_vg'))}`",
            f"- Rn4_2_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('rn4_2_web_v3_vg'))}`",
            f"- Rn4_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('rn4_web_v3_vg'))}`",
            f"- phi*Rn4_web_v3_vg: `{_format_quantity(block_shear_v3_note.get('phi_rn4_web_v3_vg'))}`",
            f"- Pu_sp: `{_format_quantity(block_shear_v3_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(block_shear_v3_note.get('alpha_pu_web'))}`",
            f"- Ru4_web_v3_vg = Pu_sp*alpha_Pu_web: `{_format_quantity(ru4_web_v3_vg_abs_disp.model_dump() if isinstance(ru4_web_v3_vg_abs_disp, Quantity) else None)}`",
            f"- DCR4_web_v3_vg: `{dcr4_web_v3_vg_disp}`",
            f"- Resultado: {block_shear_v3_result}",
            "",
            "## Paso 5 - Revisión de resistencia de la platina 1 de alma",
            "",
            "### 5.1 Revisión de capacidad a cortante en la platina 1 de alma en direccion 2",
            "",
            "#### 5.1.1. ELR #1: Desgarramiento en la perforacion del perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`",
            (
                "- Ecuaciones: `lc_plt_v2_web = min(p_plt_web - dh.1, Le_plt_web_y1 - 0.5*dh.1, Le_plt_web_y2 - 0.5*dh.1); "
                "Rn1_plt_v2_web = C*lc_plt_v2_web*t_plt_web*Fu_plt_web; "
                "phi*Rn1_plt_v2_web = phi_fragil*Rn1_plt_v2_web; "
                "DCR1_plt_v2_web = Ru1_plt_v2_web/phi*Rn1_plt_v2_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_tearout_v2_note.get('fu_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_tearout_v2_note.get('t_plt_web'))}`",
            f"- p_plt_web: `{_format_quantity(plt1_tearout_v2_note.get('p_plt_web'))}`",
            f"- Le_plt_web_y1: `{_format_quantity(plt1_tearout_v2_note.get('le_plt_web_y1'))}`",
            f"- Le_plt_web_y2: `{_format_quantity(plt1_tearout_v2_note.get('le_plt_web_y2'))}`",
            f"- dh.1: `{_format_quantity(plt1_tearout_v2_note.get('dh_1'))}`",
            f"- lc_plt_v2_web: `{_format_quantity(plt1_tearout_v2_note.get('lc_plt_v2_web'))}`",
            f"- C: `{_format_text(plt1_tearout_v2_note.get('coefficient'))}`",
            f"- phi_fragil: `{_format_text(plt1_tearout_v2_note.get('phi_fragil'))}`",
            f"- Rn1_plt_v2_web: `{_format_quantity(plt1_tearout_v2_note.get('rn1_plt_v2_web'))}`",
            f"- phi*Rn1_plt_v2_web: `{_format_quantity(plt1_tearout_v2_note.get('phi_rn1_plt_v2_web'))}`",
            f"- Ru1_plt_v2_web = Ru_web_v2_max_vg: `{_format_quantity(ru1_plt_v2_web_abs_disp.model_dump() if isinstance(ru1_plt_v2_web_abs_disp, Quantity) else None)}`",
            f"- DCR1_plt_v2_web: `{dcr1_plt_v2_web_disp}`",
            f"- Resultado: {plt1_tearout_v2_result}",
            "",
            "#### 5.1.2. ELR #2: Aplastamiento en la perforacion del perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(a)`",
            (
                "- Ecuaciones: `Rn2_plt_v2-v3_web = C*db_blt_web*t_plt_web*Fu_plt_web; "
                "phi*Rn2_plt_v2-v3_web = phi_fragil*Rn2_plt_v2-v3_web; "
                "DCR2_plt_v2-v3_web = Ru2_plt_v2-v3_web/phi*Rn2_plt_v2-v3_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_bearing_v2_note.get('fu_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_bearing_v2_note.get('t_plt_web'))}`",
            f"- db_blt_web: `{_format_quantity(plt1_bearing_v2_note.get('db_blt_web'))}`",
            f"- C: `{_format_text(plt1_bearing_v2_note.get('coefficient'))}`",
            f"- phi_fragil: `{_format_text(plt1_bearing_v2_note.get('phi_fragil'))}`",
            f"- Rn2_plt_v2-v3_web: `{_format_quantity(plt1_bearing_v2_note.get('rn2_plt_v2_web'))}`",
            f"- phi*Rn2_plt_v2-v3_web: `{_format_quantity(plt1_bearing_v2_note.get('phi_rn2_plt_v2_web'))}`",
            f"- Ru2_plt_v2-v3_web = Ru_web_vg: `{_format_quantity(ru2_plt_v2_web_abs_disp.model_dump() if isinstance(ru2_plt_v2_web_abs_disp, Quantity) else None)}`",
            f"- DCR2_plt_v2-v3_web: `{dcr2_plt_v2_web_disp}`",
            f"- Resultado: {plt1_bearing_v2_result}",
            "",
            "#### 5.1.3. ELR #3: Rotura por cortante en el perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.7`",
            (
                "- Ecuaciones: `Rn3_plt_v2-v3_web = Ab_blt_web*Fnv_blt_web; "
                "phi*Rn3_plt_v2-v3_web = phi_fragil*Rn3_plt_v2-v3_web; "
                "DCR3_plt_v2-v3_web = Ru3_plt_v2-v3_web/phi*Rn3_plt_v2-v3_web`"
            ),
            f"- db_blt_web: `{_format_quantity(plt1_bolt_shear_v2_v3_note.get('db_blt_web'))}`",
            f"- Ab_blt_web: `{_format_quantity(plt1_bolt_shear_v2_v3_note.get('ab_blt_web'))}`",
            f"- Fnv_blt_web: `{_format_quantity(plt1_bolt_shear_v2_v3_note.get('fnv_blt_web'))}`",
            f"- phi_fragil: `{_format_text(plt1_bolt_shear_v2_v3_note.get('phi_fragil'))}`",
            f"- Rn3_plt_v2-v3_web: `{_format_quantity(plt1_bolt_shear_v2_v3_note.get('rn3_plt_v2_v3_web'))}`",
            f"- phi*Rn3_plt_v2-v3_web: `{_format_quantity(plt1_bolt_shear_v2_v3_note.get('phi_rn3_plt_v2_v3_web'))}`",
            f"- Ru3_plt_v2-v3_web = Ru_web_vg: `{_format_quantity(ru3_plt_v2_v3_web_abs_disp.model_dump() if isinstance(ru3_plt_v2_v3_web_abs_disp, Quantity) else None)}`",
            f"- DCR3_plt_v2-v3_web: `{dcr3_plt_v2_v3_web_disp}`",
            f"- Resultado: {plt1_bolt_shear_v2_v3_result}",
            "",
            "#### 5.1.4. ELR #4: Bloque de cortante en platina 1 del alma",
            "",
            "- Clausula: `Documento: AISC 360-22w | Seccion: J4.3`",
            (
                "- Ecuaciones: `Agv_plt_v2_web = (p_plt_web*(n_plt_web_y - 1) + min(Le_plt_web_y1, Le_plt_web_y2))*t_plt_web; "
                "Anv_plt_v2_web = Agv_plt_v2_web - (n_blt_web_y - 0.5)*t_plt_web*(dh.1 + 1.80mm); "
                "Agt_plt_v2_web = (g_blt_web*(n_blt_web_x - 1) + Le_plt_web_x2)*t_plt_web; "
                "Ant_plt_v2_web = Agt_plt_v2_web - (n_blt_web_x - 0.5)*t_plt_web*(dh.1 + 1.80mm); "
                "Rn4_1_plt_v2_web = 0.60*Fu_plt_web*Anv_plt_v2_web + Ubs_plt_v2_web*Fu_plt_web*Ant_plt_v2_web; "
                "Rn4_2_plt_v2_web = 0.60*Fy_plt_web*Agv_plt_v2_web + Ubs_plt_v2_web*Fu_plt_web*Ant_plt_v2_web; "
                "Rn4_plt_v2_web = min(Rn4_1_plt_v2_web, Rn4_2_plt_v2_web); "
                "phi*Rn4_plt_v2_web = phi_fragil*Rn4_plt_v2_web; "
                "DCR4_plt_v2_web = Ru4_plt_v2_web/phi*Rn4_plt_v2_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_block_shear_v2_note.get('fu_plt_web'))}`",
            f"- Fy_plt_web: `{_format_quantity(plt1_block_shear_v2_note.get('fy_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_block_shear_v2_note.get('t_plt_web'))}`",
            f"- n_blt_web_x: `{_format_text(plt1_block_shear_v2_note.get('n_blt_web_x'))}`",
            f"- n_plt_web_y (= n_blt_web_y): `{_format_text(plt1_block_shear_v2_note.get('n_blt_web_y'))}`",
            f"- g_blt_web: `{_format_quantity(plt1_block_shear_v2_note.get('g_blt_web'))}`",
            f"- p_plt_web: `{_format_quantity(plt1_block_shear_v2_note.get('p_plt_web'))}`",
            f"- Le_plt_web_x2: `{_format_quantity(plt1_block_shear_v2_note.get('le_plt_web_x2'))}`",
            f"- Le_plt_web_y1: `{_format_quantity(plt1_block_shear_v2_note.get('le_plt_web_y1'))}`",
            f"- Le_plt_web_y2: `{_format_quantity(plt1_block_shear_v2_note.get('le_plt_web_y2'))}`",
            f"- dh.1: `{_format_quantity(plt1_block_shear_v2_note.get('dh_1'))}`",
            f"- Ubs_plt_v2_web (inp = Ubs_web_v2_vg): `{_format_text(plt1_block_shear_v2_note.get('ubs_plt_v2_web'))}`",
            f"- Agv_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('agv_plt_v2_web'))}`",
            f"- Anv_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('anv_plt_v2_web'))}`",
            f"- Agt_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('agt_plt_v2_web'))}`",
            f"- Ant_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('ant_plt_v2_web'))}`",
            f"- phi_fragil: `{_format_text(plt1_block_shear_v2_note.get('phi_fragil'))}`",
            f"- Rn4_1_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('rn4_1_plt_v2_web'))}`",
            f"- Rn4_2_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('rn4_2_plt_v2_web'))}`",
            f"- Rn4_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('rn4_plt_v2_web'))}`",
            f"- phi*Rn4_plt_v2_web: `{_format_quantity(plt1_block_shear_v2_note.get('phi_rn4_plt_v2_web'))}`",
            f"- Ru4_plt_v2_web = Vu2_sp: `{_format_quantity(ru4_plt_v2_web_abs_disp.model_dump() if isinstance(ru4_plt_v2_web_abs_disp, Quantity) else None)}`",
            f"- DCR4_plt_v2_web: `{dcr4_plt_v2_web_disp}`",
            f"- Resultado: {plt1_block_shear_v2_result}",
            "",
            "#### 5.1.5. ELR #5: fluencia por cortante en la platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J4.2(a)`",
            (
                "- Ecuaciones: `Agv_v2_plt_web = (p_plt_web*(n_plt_web_y - 1) + Le_plt_web_y1 + Le_plt_web_y2)*t_plt_web; "
                "Rn5_plt_v2_web = 0.60*Fy_plt_web*Agv_v2_plt_web; "
                "phi*Rn5_plt_v2_web = phi_ductil*Rn5_plt_v2_web; "
                "DCR5_plt_v2_web = Ru5_plt_v2_web/phi*Rn5_plt_v2_web`"
            ),
            f"- Fy_plt_web: `{_format_quantity(plt1_shear_yielding_v2_note.get('fy_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_shear_yielding_v2_note.get('t_plt_web'))}`",
            f"- n_plt_web_y (= n_blt_web_y): `{_format_text(plt1_shear_yielding_v2_note.get('n_plt_web_y'))}`",
            f"- p_plt_web: `{_format_quantity(plt1_shear_yielding_v2_note.get('p_plt_web'))}`",
            f"- Le_plt_web_y1: `{_format_quantity(plt1_shear_yielding_v2_note.get('le_plt_web_y1'))}`",
            f"- Le_plt_web_y2: `{_format_quantity(plt1_shear_yielding_v2_note.get('le_plt_web_y2'))}`",
            f"- Agv_v2_plt_web: `{_format_quantity(plt1_shear_yielding_v2_note.get('agv_plt_v2_web'))}`",
            f"- phi_ductil: `{_format_text(plt1_shear_yielding_v2_note.get('phi_ductil'))}`",
            f"- Rn5_plt_v2_web: `{_format_quantity(plt1_shear_yielding_v2_note.get('rn5_plt_v2_web'))}`",
            f"- phi*Rn5_plt_v2_web: `{_format_quantity(plt1_shear_yielding_v2_note.get('phi_rn5_plt_v2_web'))}`",
            f"- Ru5_plt_v2_web = Vu2_sp: `{_format_quantity(ru5_plt_v2_web_abs_disp.model_dump() if isinstance(ru5_plt_v2_web_abs_disp, Quantity) else None)}`",
            f"- DCR5_plt_v2_web: `{dcr5_plt_v2_web_disp}`",
            f"- Resultado: {plt1_shear_yielding_v2_result}",
            "",
            "#### 5.1.6. ELR #6: Rotura por cortante en la platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J4.2(b)`",
            (
                "- Ecuaciones: `Anv_v2_plt_web = (p_plt_web*(n_plt_web_y - 1) + Le_plt_web_y1 + Le_plt_web_y2 - n_plt_web_y*(dh.1 + 1.80mm))*t_plt_web; "
                "Rn6_plt_v2_web = 0.60*Fu_plt_web*Anv_v2_plt_web; "
                "phi*Rn6_plt_v2_web = phi_fragil*Rn6_plt_v2_web; "
                "DCR6_plt_v2_web = Ru6_plt_v2_web/phi*Rn6_plt_v2_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_shear_rupture_v2_note.get('fu_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_shear_rupture_v2_note.get('t_plt_web'))}`",
            f"- n_plt_web_y (= n_blt_web_y): `{_format_text(plt1_shear_rupture_v2_note.get('n_plt_web_y'))}`",
            f"- p_plt_web: `{_format_quantity(plt1_shear_rupture_v2_note.get('p_plt_web'))}`",
            f"- Le_plt_web_y1: `{_format_quantity(plt1_shear_rupture_v2_note.get('le_plt_web_y1'))}`",
            f"- Le_plt_web_y2: `{_format_quantity(plt1_shear_rupture_v2_note.get('le_plt_web_y2'))}`",
            f"- dh.1: `{_format_quantity(plt1_shear_rupture_v2_note.get('dh_1'))}`",
            f"- Anv_v2_plt_web: `{_format_quantity(plt1_shear_rupture_v2_note.get('anv_plt_v2_web'))}`",
            f"- phi_fragil: `{_format_text(plt1_shear_rupture_v2_note.get('phi_fragil'))}`",
            f"- Rn6_plt_v2_web: `{_format_quantity(plt1_shear_rupture_v2_note.get('rn6_plt_v2_web'))}`",
            f"- phi*Rn6_plt_v2_web: `{_format_quantity(plt1_shear_rupture_v2_note.get('phi_rn6_plt_v2_web'))}`",
            f"- Ru6_plt_v2_web = Vu2_sp: `{_format_quantity(ru6_plt_v2_web_abs_disp.model_dump() if isinstance(ru6_plt_v2_web_abs_disp, Quantity) else None)}`",
            f"- DCR6_plt_v2_web: `{dcr6_plt_v2_web_disp}`",
            f"- Resultado: {plt1_shear_rupture_v2_result}",
            "",
            "### 5.2 Revisión de capacidad a traccion en la platina 1 de alma en direccion 3",
            "",
            "#### 5.2.1. ELR #1: Desgarramiento en la perforacion del perno",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`",
            (
                "- Ecuaciones: `lc_plt_v3_web = min(g_plt_web - dh.1, Le_plt_web_x2 - 0.5*dh.1); "
                "Rn1_plt_v3_web = C*lc_plt_v3_web*t_plt_web*Fu_plt_web; "
                "phi*Rn1_plt_v3_web = phi_fragil*Rn1_plt_v3_web; "
                "DCR1_plt_v3_web = Ru1_plt_v3_web/phi*Rn1_plt_v3_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_tearout_v3_note.get('fu_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_tearout_v3_note.get('t_plt_web'))}`",
            f"- g_plt_web: `{_format_quantity(plt1_tearout_v3_note.get('g_plt_web'))}`",
            f"- Le_plt_web_x2: `{_format_quantity(plt1_tearout_v3_note.get('le_plt_web_x2'))}`",
            f"- dh.1: `{_format_quantity(plt1_tearout_v3_note.get('dh_1'))}`",
            f"- lc_plt_v3_web: `{_format_quantity(plt1_tearout_v3_note.get('lc_plt_v3_web'))}`",
            f"- C: `{_format_text(plt1_tearout_v3_note.get('coefficient'))}`",
            f"- phi_fragil: `{_format_text(plt1_tearout_v3_note.get('phi_fragil'))}`",
            f"- Rn1_plt_v3_web: `{_format_quantity(plt1_tearout_v3_note.get('rn1_plt_v3_web'))}`",
            f"- phi*Rn1_plt_v3_web: `{_format_quantity(plt1_tearout_v3_note.get('phi_rn1_plt_v3_web'))}`",
            f"- Ru1_plt_v3_web = Ru_web_v3_max_vg: `{_format_quantity(ru1_plt_v3_web_abs_disp.model_dump() if isinstance(ru1_plt_v3_web_abs_disp, Quantity) else None)}`",
            f"- DCR1_plt_v3_web: `{dcr1_plt_v3_web_disp}`",
            f"- Resultado: {plt1_tearout_v3_result}",
            "",
            "#### 5.2.2. ELR #2: Bloque de cortante en platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J4-5 (DRY: compute_block_shear_strength_j45)`",
            (
                "- Ecuaciones: `Agv_plt_v3_web = 2*(g_blt_web*(n_blt_web_x - 1)*t_plt_web + Le_blt_web_x2*t_plt_web); "
                "Anv_plt_v3_web = 2*(0.5*Agv_plt_v3_web - (n_blt_web_x - 0.5)*t_plt_web*(dh.1 + 1.80mm)); "
                "Agt_plt_v3_web = p_blt_web*(n_blt_web_y - 1)*t_plt_web; "
                "Ant_plt_v3_web = Agt_plt_v3_web - (n_blt_web_y - 1)*t_plt_web*(dh.1 + 1.80mm); "
                "Rn2_1_plt_v3_web = 0.60*Fu_plt_web*Anv_plt_v3_web + Ubs_plt_v3_web*Fu_plt_web*Ant_plt_v3_web; "
                "Rn2_2_plt_v3_web = 0.60*Fy_plt_web*Agv_plt_v3_web + Ubs_plt_v3_web*Fu_plt_web*Ant_plt_v3_web; "
                "Rn2_plt_v3_web = min(Rn2_1_plt_v3_web, Rn2_2_plt_v3_web); "
                "phi*Rn2_plt_v3_web = phi_fragil*Rn2_plt_v3_web; "
                "Ru2_plt_v3_web = Pu_sp*alpha_Pu_web; "
                "DCR2_plt_v3_web = Ru2_plt_v3_web/phi*Rn2_plt_v3_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_block_shear_v3_note.get('fu_plt_web'))}`",
            f"- Fy_plt_web: `{_format_quantity(plt1_block_shear_v3_note.get('fy_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_block_shear_v3_note.get('t_plt_web'))}`",
            f"- n_blt_web_x: `{_format_text(plt1_block_shear_v3_note.get('n_blt_web_x'))}`",
            f"- n_blt_web_y: `{_format_text(plt1_block_shear_v3_note.get('n_blt_web_y'))}`",
            f"- g_blt_web: `{_format_quantity(plt1_block_shear_v3_note.get('g_blt_web'))}`",
            f"- p_blt_web: `{_format_quantity(plt1_block_shear_v3_note.get('p_blt_web'))}`",
            f"- Le_blt_web_x2: `{_format_quantity(plt1_block_shear_v3_note.get('le_blt_web_x2'))}`",
            f"- dh.1: `{_format_quantity(plt1_block_shear_v3_note.get('dh_1'))}`",
            f"- Ubs_plt_v3_web (= Ubs_web_v3_vg): `{_format_text(plt1_block_shear_v3_note.get('ubs_plt_v3_web'))}`",
            f"- Agv_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('agv_plt_v3_web'))}`",
            f"- Anv_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('anv_plt_v3_web'))}`",
            f"- Agt_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('agt_plt_v3_web'))}`",
            f"- Ant_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('ant_plt_v3_web'))}`",
            f"- phi_fragil: `{_format_text(plt1_block_shear_v3_note.get('phi_fragil'))}`",
            f"- Rn2_1_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('rn2_1_plt_v3_web'))}`",
            f"- Rn2_2_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('rn2_2_plt_v3_web'))}`",
            f"- Rn2_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('rn2_plt_v3_web'))}`",
            f"- phi*Rn2_plt_v3_web: `{_format_quantity(plt1_block_shear_v3_note.get('phi_rn2_plt_v3_web'))}`",
            f"- Pu_sp: `{_format_quantity(plt1_block_shear_v3_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(plt1_block_shear_v3_note.get('alpha_pu_web'))}`",
            f"- Ru2_plt_v3_web = Pu_sp*alpha_Pu_web: `{_format_quantity(ru2_plt_v3_web_abs_disp.model_dump() if isinstance(ru2_plt_v3_web_abs_disp, Quantity) else None)}`",
            f"- DCR2_plt_v3_web: `{dcr2_plt_v3_web_disp}`",
            f"- Resultado: {plt1_block_shear_v3_result}",
            "",
            "#### 5.2.3. ELR #3: fluencia por traccion en la platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J4.1(a) (DRY: compute_element_tension_yielding_strength_j41a)`",
            (
                "- Ecuaciones: `Agt_v3_plt_web_expr = 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web; "
                "Agt_v3_plt_web = min(H_plt_web, Agt_v3_plt_web_expr)*t_plt_web; "
                "Rn3_plt_v3_web = Fy_plt_web*Agt_v3_plt_web; "
                "phi*Rn3_plt_v3_web = phi_no_ductil*Rn3_plt_v3_web; "
                "Ru3_plt_v3_web = alpha_Pu_web*Pu_sp; "
                "DCR3_plt_v3_web = Ru3_plt_v3_web/phi*Rn3_plt_v3_web`"
            ),
            f"- Fy_plt_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('fy_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('t_plt_web'))}`",
            f"- H_plt_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('h_plt_web'))}`",
            f"- n_blt_web_x: `{_format_text(plt1_tension_yielding_v3_note.get('n_blt_web_x'))}`",
            f"- n_blt_web_y: `{_format_text(plt1_tension_yielding_v3_note.get('n_blt_web_y'))}`",
            f"- g_blt_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('g_blt_web'))}`",
            f"- p_blt_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('p_blt_web'))}`",
            f"- Agt_v3_plt_web_expr: `{_format_quantity(plt1_tension_yielding_v3_note.get('agt_v3_plt_web_expr'))}`",
            f"- Agt_v3_plt_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('agt_v3_plt_web'))}`",
            f"- phi_no_ductil: `{_format_text(plt1_tension_yielding_v3_note.get('phi_no_ductil'))}`",
            f"- Rn3_plt_v3_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('rn3_plt_v3_web'))}`",
            f"- phi*Rn3_plt_v3_web: `{_format_quantity(plt1_tension_yielding_v3_note.get('phi_rn3_plt_v3_web'))}`",
            f"- Pu_sp: `{_format_quantity(plt1_tension_yielding_v3_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(plt1_tension_yielding_v3_note.get('alpha_pu_web'))}`",
            f"- Ru3_plt_v3_web = alpha_Pu_web*Pu_sp: `{_format_quantity(ru3_plt_v3_web_abs_disp.model_dump() if isinstance(ru3_plt_v3_web_abs_disp, Quantity) else None)}`",
            f"- DCR3_plt_v3_web: `{dcr3_plt_v3_web_disp}`",
            f"- Resultado: {plt1_tension_yielding_v3_result}",
            "",
            "#### 5.2.4. ELR #4: Rotura por tracción en la platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J4.1(b) (DRY: compute_element_tension_rupture_strength_j41b)`",
            (
                "- Ecuaciones: `Agt_v3_plt_web_expr = 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web; "
                "Agt_v3_plt_web = min(H_plt_web, Agt_v3_plt_web_expr)*t_plt_web; "
                "Ant_v3_plt_web = Agt_v3_plt_web - n_blt_web_y*(dh.1 + 1.80mm)*t_plt_web; "
                "U_v3_plt_web = 1; "
                "Ae_v3_plt_web = Ant_v3_plt_web*U_v3_plt_web; "
                "Rn4_plt_v3_web = Fu_plt_web*Ae_v3_plt_web; "
                "phi*Rn4_plt_v3_web = phi_fragil*Rn4_plt_v3_web; "
                "Ru4_plt_v3_web = alpha_Pu_web*Pu_sp; "
                "DCR4_plt_v3_web = Ru4_plt_v3_web/phi*Rn4_plt_v3_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('fu_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('t_plt_web'))}`",
            f"- H_plt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('h_plt_web'))}`",
            f"- n_blt_web_x: `{_format_text(plt1_tension_rupture_v3_note.get('n_blt_web_x'))}`",
            f"- n_blt_web_y: `{_format_text(plt1_tension_rupture_v3_note.get('n_blt_web_y'))}`",
            f"- g_blt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('g_blt_web'))}`",
            f"- p_blt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('p_blt_web'))}`",
            f"- dh.1: `{_format_quantity(plt1_tension_rupture_v3_note.get('dh_1'))}`",
            f"- Agt_v3_plt_web_expr: `{_format_quantity(plt1_tension_rupture_v3_note.get('agt_v3_plt_web_expr'))}`",
            f"- Agt_v3_plt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('agt_v3_plt_web'))}`",
            f"- Ant_v3_plt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('ant_v3_plt_web'))}`",
            f"- U_v3_plt_web: `{_format_text(plt1_tension_rupture_v3_note.get('u_v3_plt_web'))}`",
            f"- Ae_v3_plt_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('ae_v3_plt_web'))}`",
            f"- phi_fragil: `{_format_text(plt1_tension_rupture_v3_note.get('phi_fragil'))}`",
            f"- Rn4_plt_v3_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('rn4_plt_v3_web'))}`",
            f"- phi*Rn4_plt_v3_web: `{_format_quantity(plt1_tension_rupture_v3_note.get('phi_rn4_plt_v3_web'))}`",
            f"- Pu_sp: `{_format_quantity(plt1_tension_rupture_v3_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(plt1_tension_rupture_v3_note.get('alpha_pu_web'))}`",
            f"- Ru4_plt_v3_web = alpha_Pu_web*Pu_sp: `{_format_quantity(ru4_plt_v3_web_abs_disp.model_dump() if isinstance(ru4_plt_v3_web_abs_disp, Quantity) else None)}`",
            f"- DCR4_plt_v3_web: `{dcr4_plt_v3_web_disp}`",
            f"- Resultado: {plt1_tension_rupture_v3_result}",
            "",
            "### 5.3 Revisión de capacidad a compresion en la platina 1 de alma en direccion 3",
            "",
            "### 5.4 Revisión de capacidad a flexion en la platina 1 de alma alrededor de 1",
            "",
            "#### 5.4.1. ELR #1: Fluencia por flexion en la platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: F11.1 (DRY: compute_rectangular_bar_flexural_yielding_strength_f111)`",
            (
                "- Ecuaciones: `Z_plt_m1_web = t_plt_web*H_plt_web^2/4; "
                "S_plt_m1_web = t_plt_web*H_plt_web^2/6; "
                "Rn1_plt_m1_web = min(Fy_plt_web*Z_plt_m1_web, 1.5*Fy_plt_web*S_plt_m1_web); "
                "phi*Rn1_plt_m1_web = phi_no_ductil*Rn1_plt_m1_web; "
                "Ru1_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web; "
                "DCR1_plt_m1_web = Ru1_plt_m1_web/phi*Rn1_plt_m1_web`"
            ),
            f"- Fy_plt_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('fy_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('t_plt_web'))}`",
            f"- H_plt_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('h_plt_web'))}`",
            f"- Z_plt_m1_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('z_plt_m1_web'))}`",
            f"- S_plt_m1_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('s_plt_m1_web'))}`",
            f"- ex_blt_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('ex_blt_web'))}`",
            f"- ey_blt_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('ey_blt_web'))}`",
            f"- phi_no_ductil: `{_format_text(plt1_flex_yielding_m1_note.get('phi_no_ductil'))}`",
            f"- Rn1_plt_m1_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('mn1_plt_m1_web'))}`",
            f"- phi*Rn1_plt_m1_web: `{_format_quantity(plt1_flex_yielding_m1_note.get('phi_mn1_plt_m1_web'))}`",
            f"- Vu2_sp: `{_format_quantity(plt1_flex_yielding_m1_note.get('vu2_sp'))}`",
            f"- Pu_sp: `{_format_quantity(plt1_flex_yielding_m1_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(plt1_flex_yielding_m1_note.get('alpha_pu_web'))}`",
            f"- Ru1_plt_m1_web: `{_format_quantity(ru1_plt_m1_web_abs_disp.model_dump() if isinstance(ru1_plt_m1_web_abs_disp, Quantity) else None)}`",
            f"- DCR1_plt_m1_web: `{dcr1_plt_m1_web_disp}`",
            f"- Resultado: {plt1_flex_yielding_m1_result}",
            "",
            "#### 5.4.2. ELR #2: Pandeo lateral-torsional en la platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: F11.2 (DRY: compute_rectangular_bar_ltb_strength_f112)`",
            (
                "- Ecuaciones: `Z_plt_m1_web = t_plt_web*H_plt_web^2/4; "
                "S_plt_m1_web = t_plt_web*H_plt_web^2/6; "
                "Lb_plt_m1_web = max(2*Le_blt_web_x1 + gap_sp, g_plt_web); "
                "My_plt_m1_web = Fy_plt_web*S_plt_m1_web; "
                "Rn2_plt_m1_web = Mn_ltb(F11.2) <= Mp; "
                "phi*Rn2_plt_m1_web = phi_no_ductil*Rn2_plt_m1_web; "
                "Ru2_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web; "
                "DCR2_plt_m1_web = Ru2_plt_m1_web/phi*Rn2_plt_m1_web`"
            ),
            f"- Fy_plt_web: `{_format_quantity(plt1_ltb_m1_note.get('fy_plt_web'))}`",
            f"- E_plt_web: `{_format_quantity(plt1_ltb_m1_note.get('e_plt_web'))}`",
            f"- t_plt_web: `{_format_quantity(plt1_ltb_m1_note.get('t_plt_web'))}`",
            f"- H_plt_web: `{_format_quantity(plt1_ltb_m1_note.get('h_plt_web'))}`",
            f"- Z_plt_m1_web: `{_format_quantity(plt1_ltb_m1_note.get('z_plt_m1_web'))}`",
            f"- S_plt_m1_web: `{_format_quantity(plt1_ltb_m1_note.get('s_plt_m1_web'))}`",
            f"- Lb_plt_m1_web: `{_format_quantity(plt1_ltb_m1_note.get('lb_plt_m1_web'))}`",
            f"- My_plt_m1_web: `{_format_quantity(plt1_ltb_m1_note.get('my_plt_m1_web'))}`",
            f"- Cb_plt_m1_web (inp): `{_format_text(plt1_ltb_m1_note.get('cb_plt_m1_web'))}`",
            f"- ltb_case_id: `{_format_text(plt1_ltb_m1_note.get('ltb_case_id'))}`",
            f"- Lb*d/t^2: `{_format_text(plt1_ltb_m1_note.get('lb_d_over_t2'))}`",
            f"- 0.08E/Fy: `{_format_text(plt1_ltb_m1_note.get('limit_a_0p08e_over_fy'))}`",
            f"- 1.9E/Fy: `{_format_text(plt1_ltb_m1_note.get('limit_b_1p9e_over_fy'))}`",
            f"- Fcr: `{_format_quantity(plt1_ltb_m1_note.get('fcr'))}`",
            f"- phi_no_ductil: `{_format_text(plt1_ltb_m1_note.get('phi_no_ductil'))}`",
            f"- Rn2_plt_m1_web: `{_format_quantity(plt1_ltb_m1_note.get('mn2_plt_m1_web'))}`",
            f"- phi*Rn2_plt_m1_web: `{_format_quantity(plt1_ltb_m1_note.get('phi_mn2_plt_m1_web'))}`",
            f"- ex_blt_web: `{_format_quantity(plt1_ltb_m1_note.get('ex_blt_web'))}`",
            f"- ey_blt_web: `{_format_quantity(plt1_ltb_m1_note.get('ey_blt_web'))}`",
            f"- Vu2_sp: `{_format_quantity(plt1_ltb_m1_note.get('vu2_sp'))}`",
            f"- Pu_sp: `{_format_quantity(plt1_ltb_m1_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(plt1_ltb_m1_note.get('alpha_pu_web'))}`",
            f"- Ru2_plt_m1_web: `{_format_quantity(ru2_plt_m1_web_abs_disp.model_dump() if isinstance(ru2_plt_m1_web_abs_disp, Quantity) else None)}`",
            f"- DCR2_plt_m1_web: `{dcr2_plt_m1_web_disp}`",
            f"- Resultado: {plt1_ltb_m1_result}",
            "",
            "#### 5.4.3. ELR #3: Rotura por flexion en la platina 1 de alma",
            "",
            "- Clausula: `Documento: AISC 360-22 | Seccion: J5.5 (DRY: compute_rectangular_bar_net_flexural_rupture_strength_j55)`",
            (
                "- Ecuaciones: `h = e1 + (n - 1)*s + e2; "
                "Znet_plt_m1_web = tp*h^2/4 - d'*tp*sum_{i=0}^{n-1}|e1 + i*s - h/2|; "
                "Rn3_plt_m1_web = Fu_plt_web*Znet_plt_m1_web; "
                "phi*Rn3_plt_m1_web = phi_fragil*Rn3_plt_m1_web; "
                "Ru3_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web; "
                "DCR3_plt_m1_web = Ru3_plt_m1_web/phi*Rn3_plt_m1_web`"
            ),
            f"- Fu_plt_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('fu_plt_web'))}`",
            f"- tp = t_plt_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('tp_plt_m1_web'))}`",
            f"- h = H_plt_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('h_plt_m1_web'))}`",
            f"- d' = dh.1 + 1.80mm: `{_format_quantity(plt1_flex_rupture_m1_note.get('d_prime_plt_m1_web'))}`",
            f"- e1 = Le_plt_web_y1: `{_format_quantity(plt1_flex_rupture_m1_note.get('e1_plt_m1_web'))}`",
            f"- e2 = Le_plt_web_y2: `{_format_quantity(plt1_flex_rupture_m1_note.get('e2_plt_m1_web'))}`",
            f"- s = p_plt_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('s_plt_m1_web'))}`",
            f"- n = n_plt_web_y: `{_format_text(plt1_flex_rupture_m1_note.get('n_plt_web_y'))}`",
            f"- h calculado: `{_format_quantity(plt1_flex_rupture_m1_note.get('h_calc_plt_m1_web'))}`",
            f"- sum_abs: `{_format_quantity(plt1_flex_rupture_m1_note.get('sum_abs_plt_m1_web'))}`",
            f"- Znet_plt_m1_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('z_net_plt_m1_web'))}`",
            f"- phi_fragil: `{_format_text(plt1_flex_rupture_m1_note.get('phi_fragil'))}`",
            f"- Rn3_plt_m1_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('rn3_plt_m1_web'))}`",
            f"- phi*Rn3_plt_m1_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('phi_rn3_plt_m1_web'))}`",
            f"- ex_blt_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('ex_blt_web'))}`",
            f"- ey_blt_web: `{_format_quantity(plt1_flex_rupture_m1_note.get('ey_blt_web'))}`",
            f"- Vu2_sp: `{_format_quantity(plt1_flex_rupture_m1_note.get('vu2_sp'))}`",
            f"- Pu_sp: `{_format_quantity(plt1_flex_rupture_m1_note.get('pu_sp'))}`",
            f"- alpha_Pu_web: `{_format_text(plt1_flex_rupture_m1_note.get('alpha_pu_web'))}`",
            f"- Ru3_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web: `{_format_quantity(ru3_plt_m1_web_abs_disp.model_dump() if isinstance(ru3_plt_m1_web_abs_disp, Quantity) else None)}`",
            f"- DCR3_plt_m1_web: `{dcr3_plt_m1_web_disp}`",
            f"- Resultado: {plt1_flex_rupture_m1_result}",
            "",
        ]
    )
    return "\n".join(lines)

def _render_step_1_list(
    rows: list[dict],
    *,
    chapter_number: int = 1,
    heading_scope_label: str | None = None,
) -> str:
    lines: list[str] = []
    if heading_scope_label:
        lines.append(f"### {chapter_number}.2 Revisiones de propiedades geometricas [{heading_scope_label}]")
    else:
        lines.append(f"### {chapter_number}.2 Revisiones de propiedades geometricas")
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
            weld_size = _format_quantity(item.get("weld_size"))
            required_weld_size = _format_quantity(item.get("required_weld_size"))
            calculated_text = _format_text(item.get("calculated_text"))
            allowed_values = item.get("allowed_values")
            allowed = ", ".join(str(v) for v in allowed_values) if isinstance(allowed_values, list) else limit_symbol
            governing = _format_text(item.get("governing_condition"))
            if governing == "cjp_always_permitted":
                verification = (
                    f"tipo_w5_col='cjp' => cumple; "
                    f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
                )
            elif governing == "fillet_requires_minimum_size_075_tcp":
                verification = (
                    f"if tipo_w5_col='fillet': w_w5_col >= 0.75*t_pc_col; "
                    f"w_w5_col={weld_size}; 0.75*t_pc_col={required_weld_size}; "
                    f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
                )
            elif governing == "fillet_requires_size_input":
                verification = (
                    f"if tipo_w5_col='fillet': se requiere w_w5_col; "
                    f"w_w5_col={weld_size}; 0.75*t_pc_col={required_weld_size}; "
                    f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
                )
            else:
                verification = (
                    f"tipo_w5_col in {{{allowed}}}; "
                    f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
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
            limit_symbol_text = limit_symbol
            if (
                calculated_symbol == "Le_blt_web_x1"
                and comparison == ">="
                and str(limit_symbol).strip().lower().startswith("max(le_min")
            ):
                limit_symbol_text = "Le_min"
            verification = f"{calculated_symbol} {comparison} {limit_symbol_text}; {calculated} {comparison} {limit}"

        lines.append(f"#### Chequeo {chapter_number}.2.{idx} - {description} (`{calculated_symbol}`)")
        lines.append("")
        lines.append(f"- Ambito: `{scope}`")
        lines.append(f"- Verificacion: `{verification}`")
        lines.append(f"- Clausula: `{clause}`")
        lines.append(f"- Resultado: {result_text}")
        lines.append("")
    return "\n".join(lines)


def _render_step_1_list_grouped_by_scope(
    rows: list[dict],
    *,
    chapter_number: int = 1,
    scope_template: list[str] | None = None,
) -> str:
    grouped: dict[str, list[dict]] = {}
    scope_order: list[str] = []
    for item in rows:
        scope = str(item.get("scope", "n/a")).upper()
        if scope not in grouped:
            grouped[scope] = []
            scope_order.append(scope)
        grouped[scope].append(item)

    def _scope_sort_key(scope: str) -> tuple[int, int, int]:
        scope_upper = scope.upper()
        if scope_upper == "CONTINUITY_PLATE_COL":
            # Keep continuity-plate validations near the end, before doubler-plate scope.
            return (2, 98, 10)
        if scope_upper == "DOUBLER_PLATE_COL":
            # Render doubler-plate checks after continuity-plate checks.
            return (2, 99, 9)
        if scope_upper.startswith("WELD_"):
            parts = scope_upper.split("_")
            try:
                weld_idx = int(parts[1])
            except (IndexError, ValueError):
                weld_idx = 99
            side_rank = 9
            if scope_upper.endswith("_VGDER"):
                side_rank = 1
            elif scope_upper.endswith("_VGIZQ"):
                side_rank = 2
            elif scope_upper.endswith("_COL"):
                side_rank = 3
            return (2, weld_idx, side_rank)
        if scope in scope_order:
            return (1, scope_order.index(scope), 0)
        return (3, 999, 0)

    ordered_scopes = sorted(scope_order, key=_scope_sort_key)
    if scope_template:
        normalized_template = [str(scope).upper() for scope in scope_template]
        ordered_scopes = list(normalized_template)

    lines: list[str] = []
    scope_summary: list[dict[str, Any]] = []
    for section_offset, scope in enumerate(ordered_scopes, start=1):
        if chapter_number == 3 and scope.upper() == "CONTINUITY_PLATE_COL":
            lines.append(f"### {chapter_number}.{section_offset} platina de continuidad")
        elif chapter_number == 1 and scope.upper() == "DOUBLER_PLATE_COL":
            lines.append(f"### {chapter_number}.{section_offset} platina de enchape del alma")
        else:
            lines.append(f"### {chapter_number}.{section_offset} Ambito `{scope}`")
        lines.append("")
        local_idx = 1
        total_checks = 0
        pass_checks = 0
        fail_numerals: list[str] = []
        items_for_scope = list(grouped.get(scope, []))
        if chapter_number == 3 and scope.upper() in {"TABLE_6_1_DER", "TABLE_6_1_IZQ"}:
            excluded_ids = {
                "table_6_1.pitch_pb_ge_3db_der",
                "table_6_1.pitch_pb_ge_3db_izq",
                "table_6_1.tbf.range_der",
                "table_6_1.tbf.range_izq",
            }
            items_for_scope = [
                item
                for item in items_for_scope
                if str(item.get("id", "")).strip().lower() not in excluded_ids
            ]
        for item in items_for_scope:
            description = _translate_text_es(item.get("description"))
            calculated_symbol = str(item.get("calculated_symbol", "calc"))
            limit_symbol = str(item.get("limit_symbol", "lim"))
            calculated = _format_quantity(item.get("calculated"))
            result_text = _render_result_label(item.get("result", item.get("status", "UNKNOWN")))
            status_raw = str(item.get("status", item.get("result", ""))).strip().upper()
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
                weld_size = _format_quantity(item.get("weld_size"))
                required_weld_size = _format_quantity(item.get("required_weld_size"))
                calculated_text = _format_text(item.get("calculated_text"))
                allowed_values = item.get("allowed_values")
                allowed = ", ".join(str(v) for v in allowed_values) if isinstance(allowed_values, list) else limit_symbol
                governing = _format_text(item.get("governing_condition"))
                if governing == "cjp_always_permitted":
                    verification = (
                        f"tipo_w5_col='cjp' => cumple; "
                        f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
                    )
                elif governing == "fillet_requires_minimum_size_075_tcp":
                    verification = (
                        f"if tipo_w5_col='fillet': w_w5_col >= 0.75*t_pc_col; "
                        f"w_w5_col={weld_size}; 0.75*t_pc_col={required_weld_size}; "
                        f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
                    )
                elif governing == "fillet_requires_size_input":
                    verification = (
                        f"if tipo_w5_col='fillet': se requiere w_w5_col; "
                        f"w_w5_col={weld_size}; 0.75*t_pc_col={required_weld_size}; "
                        f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
                    )
                else:
                    verification = (
                        f"tipo_w5_col in {{{allowed}}}; "
                        f"t_pc_col={thickness}; tipo_w5_col='{calculated_text}'"
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
                limit_symbol_text = limit_symbol
                if (
                    calculated_symbol == "Le_blt_web_x1"
                    and comparison == ">="
                    and str(limit_symbol).strip().lower().startswith("max(le_min")
                ):
                    limit_symbol_text = "Le_min"
                verification = f"{calculated_symbol} {comparison} {limit_symbol_text}; {calculated} {comparison} {limit}"

            lines.append(f"#### Chequeo {chapter_number}.{section_offset}.{local_idx} - {description} (`{calculated_symbol}`)")
            lines.append("")
            lines.append(f"- Ambito: `{scope}`")
            lines.append(f"- Verificacion: `{verification}`")
            lines.append(f"- Clausula: `{clause}`")
            lines.append(f"- Resultado: {result_text}")
            lines.append("")
            numeral = f"{chapter_number}.{section_offset}.{local_idx}"
            total_checks += 1
            if status_raw in {"PASS", "OK"}:
                pass_checks += 1
            else:
                fail_numerals.append(numeral)
            local_idx += 1

        scope_summary.append(
            {
                "scope": scope,
                "section_offset": section_offset,
                "total": total_checks,
                "pass": pass_checks,
                "fail": total_checks - pass_checks,
                "fail_numerals": fail_numerals,
            }
        )

    summary_section = len(ordered_scopes) + 1
    lines.append(f"### {chapter_number}.{summary_section} Resumen de chequeos por ambito")
    lines.append("")
    for summary in scope_summary:
        fail_numerals = summary["fail_numerals"]
        fail_text = ", ".join(fail_numerals) if fail_numerals else "ninguno"
        status_dot = "🟢" if summary["fail"] == 0 else "🔴"
        lines.append(
            f"- {status_dot} "
                f"`{chapter_number}.{summary['section_offset']}` `{summary['scope']}`: "
            f"total={summary['total']}, cumple={summary['pass']}, no_cumple={summary['fail']}, "
            f"numerales_no_cumplen={fail_text}"
        )
    lines.append("")
    return "\n".join(lines)


def _ordered_scopes_from_rows(rows: list[dict]) -> list[str]:
    grouped: dict[str, list[dict]] = {}
    scope_order: list[str] = []
    for item in rows:
        scope = str(item.get("scope", "n/a")).upper()
        if scope not in grouped:
            grouped[scope] = []
            scope_order.append(scope)

    def _scope_sort_key(scope: str) -> tuple[int, int, int]:
        scope_upper = scope.upper()
        if scope_upper == "DOUBLER_PLATE_COL":
            if "CONTINUITY_PLATE_COL" in scope_order:
                return (1, scope_order.index("CONTINUITY_PLATE_COL"), 1)
            return (1, 999, 1)
        if scope_upper.startswith("WELD_"):
            parts = scope_upper.split("_")
            try:
                weld_idx = int(parts[1])
            except (IndexError, ValueError):
                weld_idx = 99
            side_rank = 9
            if scope_upper.endswith("_VGDER"):
                side_rank = 1
            elif scope_upper.endswith("_VGIZQ"):
                side_rank = 2
            elif scope_upper.endswith("_COL"):
                side_rank = 3
            return (2, weld_idx, side_rank)
        if scope in scope_order:
            return (1, scope_order.index(scope), 0)
        return (3, 999, 0)

    return sorted(scope_order, key=_scope_sort_key)


def _render_scope_subtitles_only(*, chapter_number: int, scopes: list[str]) -> str:
    lines: list[str] = []
    for section_offset, scope in enumerate(scopes, start=1):
        if chapter_number == 1 and scope == "CONTINUITY_PLATE_COL":
            lines.append(f"### {chapter_number}.{section_offset} platinas de continuidad")
        elif chapter_number == 1 and scope == "DOUBLER_PLATE_COL":
            lines.append(f"### {chapter_number}.{section_offset} platina de enchape del alma")
        else:
            lines.append(f"### {chapter_number}.{section_offset} Ámbito `{scope}`")
        lines.append("")
    return "\n".join(lines)


def _render_step_1_notes_by_scope_template(
    notes: list[dict],
    *,
    chapter_number: int,
    scopes: list[str],
    rows: list[dict] | None = None,
    step_1_inputs: dict | None = None,
    step_2: dict | None = None,
    step_3: dict | None = None,
    step_4: dict | None = None,
    step_7_1_1_by_side: dict | None = None,
    step_6_1_by_side: dict | None = None,
    step_6_2_by_side: dict | None = None,
    step_8_1_1_by_side: dict | None = None,
    step_9_1_1_by_side: dict | None = None,
    step_11_w3_by_side: dict | None = None,
    step_10_w4_by_side: dict | None = None,
    step_7_3_1_by_side: dict | None = None,
    step_21_5_1_panel_zone: dict | None = None,
) -> str:
    if not notes:
        return ""
    grouped: dict[str, list[dict]] = {}
    for item in notes:
        note_id = _format_text(item.get("id"))
        if note_id == "section_6_7.beam_flange_to_end_plate_weld_note":
            continue
        scope = _format_text(item.get("scope")).upper()
        grouped.setdefault(scope, []).append(item)
    rows_by_scope_symbol: dict[tuple[str, str], dict] = {}
    for row in (rows or []):
        rows_by_scope_symbol[(str(row.get("scope", "")).upper(), str(row.get("calculated_symbol", "")))] = row

    lines: list[str] = []
    for section_offset, scope in enumerate(scopes, start=1):
        if chapter_number == 1 and scope == "CONTINUITY_PLATE_COL":
            lines.append(f"### {chapter_number}.{section_offset} platinas de continuidad")
        elif chapter_number == 1 and scope == "DOUBLER_PLATE_COL":
            lines.append(f"### {chapter_number}.{section_offset} platina de enchape del alma")
        else:
            lines.append(f"### {chapter_number}.{section_offset} Ámbito `{scope}`")
        lines.append("")
        if chapter_number == 1 and scope == "BEAM_IZQ":
            rows_map: dict[str, dict] = {}
            for row in (rows or []):
                if str(row.get("scope", "")).upper() == "BEAM_IZQ":
                    rows_map[str(row.get("calculated_symbol", ""))] = row
            step2_inputs = (step_2 or {}).get("inputs", {}) if isinstance(step_2, dict) else {}
            step3_inputs = (step_3 or {}).get("inputs", {}) if isinstance(step_3, dict) else {}
            step4_inputs = (step_4 or {}).get("inputs", {}) if isinstance(step_4, dict) else {}

            perfil_vgizq = _format_text((rows_map.get("perfil_vgizq") or {}).get("calculated_text"))
            tipo_acero_perfil_vgizq = _format_text(
                step2_inputs.get("tipo_acero_perfil_vgizq")
                or step2_inputs.get("beam_steel_type_vgizq")
                or step2_inputs.get("beam_steel_type")
            )
            demanda_ductilidad_vgizq = _format_text(step2_inputs.get("member_ductility_demand_vgizq"))
            llb_vgizq = _format_quantity(step4_inputs.get("lh_izq"))
            lnc_vgizq = _format_quantity((rows_map.get("Lnc_vgizq") or {}).get("calculated"))

            lpz_vgizq = "n/a"
            for note_item in grouped.get("BEAM", []):
                if _format_text(note_item.get("id")) == "section_2_3_4.protected_zone_length":
                    lpz_vgizq = _format_quantity(note_item.get("protected_zone_length_vgizq"))
                    break

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Perfil de viga izquierda (perfil_vgizq) (inp): `{perfil_vgizq}`")
            lines.append(f"- Tipo de acero del perfil de viga izquierda (tipo_acero_perfil_vgizq) (inp): `{tipo_acero_perfil_vgizq}`")
            lines.append(f"- Demanda de ductilidad de viga izquierda (demanda_ductilidad_vgizq) (inp): `{demanda_ductilidad_vgizq}`")
            lines.append(f"- Luz libre de viga izquierda (Llb_vgizq) (inp): `{llb_vgizq}`")
            lines.append(f"- Longitud sin conectores desde cara de columna (Lnc_vgizq) (inp): `{lnc_vgizq}`")
            lines.append(f"- Longitud de zona protegida (Lpz_vgizq): `{lpz_vgizq}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "BEAM_DER":
            rows_map: dict[str, dict] = {}
            for row in (rows or []):
                if str(row.get("scope", "")).upper() == "BEAM_DER":
                    rows_map[str(row.get("calculated_symbol", ""))] = row
            step2_inputs = (step_2 or {}).get("inputs", {}) if isinstance(step_2, dict) else {}
            step4_inputs = (step_4 or {}).get("inputs", {}) if isinstance(step_4, dict) else {}

            perfil_vgder = _format_text((rows_map.get("perfil_vgder") or {}).get("calculated_text"))
            tipo_acero_perfil_vgder = _format_text(
                step2_inputs.get("tipo_acero_perfil_vgder")
                or step2_inputs.get("beam_steel_type_vgder")
                or step2_inputs.get("beam_steel_type")
            )
            demanda_ductilidad_vgder = _format_text(step2_inputs.get("member_ductility_demand_vgder"))
            llb_vgder = _format_quantity(step4_inputs.get("lh_der"))
            lnc_vgder = _format_quantity((rows_map.get("Lnc_vgder") or {}).get("calculated"))

            lpz_vgder = "n/a"
            for note_item in grouped.get("BEAM", []):
                if _format_text(note_item.get("id")) == "section_2_3_4.protected_zone_length":
                    lpz_vgder = _format_quantity(note_item.get("protected_zone_length_vgder"))
                    break

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Perfil de viga derecha (perfil_vgder) (inp): `{perfil_vgder}`")
            lines.append(f"- Tipo de acero del perfil de viga derecha (tipo_acero_perfil_vgder) (inp): `{tipo_acero_perfil_vgder}`")
            lines.append(f"- Demanda de ductilidad de viga derecha (demanda_ductilidad_vgder) (inp): `{demanda_ductilidad_vgder}`")
            lines.append(f"- Luz libre de viga derecha (Llb_vgder) (inp): `{llb_vgder}`")
            lines.append(f"- Longitud sin conectores desde cara de columna (Lnc_vgder) (inp): `{lnc_vgder}`")
            lines.append(f"- Longitud de zona protegida (Lpz_vgder): `{lpz_vgder}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "COLUMN":
            rows_map: dict[str, dict] = {}
            for row in (rows or []):
                if str(row.get("scope", "")).upper() == "COLUMN":
                    rows_map[str(row.get("calculated_symbol", ""))] = row
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            panel_inputs = (
                (step_21_5_1_panel_zone or {}).get("inputs", {})
                if isinstance(step_21_5_1_panel_zone, dict)
                else {}
            )

            shape_col = _format_text((rows_map.get("shape_col") or {}).get("calculated_text"))
            tipo_acero_perfil_col = _format_text(
                step1_inputs.get("tipo_acero_perfil_col")
                or step1_inputs.get("column_steel_type")
            )
            d_col = _format_quantity((rows_map.get("d_col") or {}).get("calculated"))
            tw_col = _format_quantity((rows_map.get("tw_col") or {}).get("calculated"))
            st_col = _format_quantity((rows_map.get("St_col") or {}).get("calculated"))
            hb_col = _format_quantity(panel_inputs.get("hb_col"))
            ht_col = _format_quantity(panel_inputs.get("ht_col"))
            bf_col_q = panel_inputs.get("bcf_col")
            tf_col_q = panel_inputs.get("tcf_col")
            tpc_col_q = step1_inputs.get("t_pc_col") or step1_inputs.get("tpc_col") or step1_inputs.get("continuity_plate_thickness_tcp")
            b1_pc_col_q = step1_inputs.get("b1_pc_col")
            usar_pc_col = step1_inputs.get("usar_pc_col")
            if usar_pc_col is None:
                usar_pc_col = step1_inputs.get("continuity_plate_enabled")
            tipo_acero_pc_col = _format_text(
                step1_inputs.get("tipo_acero_pc_col")
                or step1_inputs.get("continuity_plate_steel_type")
            )
            kdet_col_q = step1_inputs.get("kdet_col")
            k1_col_q = step1_inputs.get("k1_col")
            tfdet_col_q = step1_inputs.get("tfdet_col")
            tipo_w5_col = _format_text(
                step1_inputs.get("tipo_w5_col")
                or step1_inputs.get("continuity_plate_weld_type")
            )
            fexx_w5_col_q = step1_inputs.get("Fexx_w5_col") or step1_inputs.get("weld_fexx")
            t_w5_col_q = step1_inputs.get("w_w5_col") or step1_inputs.get("t_w5_col")
            nl_w5_col = step1_inputs.get("nl_w5_col")
            l_gap_w5_col_q = step1_inputs.get("L_gap_w5_col")
            kds_w5_col = step1_inputs.get("kds_w5_col")
            tw_col_q = (rows_map.get("tw_col") or {}).get("calculated")
            d_col_q = (rows_map.get("d_col") or {}).get("calculated")

            def _const_like(q: object, mm_value: float) -> dict | None:
                qq = _as_quantity(q)
                if qq is None:
                    return None
                if qq.unit == "mm":
                    return {"value": mm_value, "unit": "mm"}
                if qq.unit == "in":
                    return {"value": mm_value / 25.4, "unit": "in"}
                return None

            def _side_tag(side: str) -> str:
                return "vgizq" if side == "izq" else "vgder"

            def _qsum(a: object, b: object, c: object, *, factors: tuple[float, float, float] = (1.0, 1.0, 1.0)) -> dict | None:
                qa = _as_quantity(a)
                qb = _as_quantity(b)
                qc = _as_quantity(c)
                if qa is None or qb is None or qc is None:
                    return None
                if not (qa.unit == qb.unit == qc.unit):
                    return None
                return {"value": factors[0] * qa.value + factors[1] * qb.value + factors[2] * qc.value, "unit": qa.unit}

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Perfil de columna (shape_col) (inp): `{shape_col}`")
            lines.append(f"- Tipo de acero del perfil de columna (tipo_acero_perfil_col) (inp): `{tipo_acero_perfil_col}`")
            lines.append(f"- Altura de columna (d_col) (inp): `{d_col}`")
            lines.append(f"- Espesor de alma de columna (tw_col) (inp): `{tw_col}`")
            lines.append(f"- Espesor de ala de columna (tf_col) (inp): `{_format_quantity(tf_col_q)}`")
            lines.append(f"- Ancho de ala de columna (bf_col) (inp): `{_format_quantity(bf_col_q)}`")
            lines.append(f"- Proyeccion de columna sobre vigas (St_col) (inp): `{st_col}`")
            lines.append(f"- Distancia al punto de inflexion superior (ht_col) (inp): `{ht_col}`")
            lines.append(f"- Distancia al punto de inflexion inferior (hb_col) (inp): `{hb_col}`")
            for side in ("izq", "der"):
                side_label = "izquierda" if side == "izq" else "derecha"
                tag = _side_tag(side)
                step731_inputs = (
                    ((step_7_3_1_by_side or {}).get(side) or {}).get("inputs", {})
                    if isinstance((step_7_3_1_by_side or {}).get(side), dict)
                    else {}
                )
                step61_inputs = (
                    ((step_6_1_by_side or {}).get(side) or {}).get("inputs", {})
                    if isinstance((step_6_1_by_side or {}).get(side), dict)
                    else {}
                )
                pfo_q = step731_inputs.get(f"pfo_pe_{tag}")
                pfi_q = step731_inputs.get(f"pfi_pe_{tag}")
                tf_q = step731_inputs.get(f"tf_{tag}")
                dh_q = step731_inputs.get(f"dh_pe_{tag}")
                g_b_q = (
                    (rows_by_scope_symbol.get((f"BEAM_{side.upper()}", f"g_b_{tag}")) or {}).get("calculated")
                    or (rows_by_scope_symbol.get((f"END_PLATE_{side.upper()}", f"g_b_{tag}")) or {}).get("calculated")
                    or (rows_by_scope_symbol.get((f"TABLE_6_1_{side.upper()}", f"g_b_{tag}")) or {}).get("calculated")
                )

                pso_q = _qsum(pfo_q, tf_q, tpc_col_q, factors=(1.0, 0.5, -0.5))
                psi_q = _qsum(pfi_q, tf_q, tpc_col_q, factors=(1.0, 0.5, -0.5))
                c_col_q = _qsum(pfi_q, tf_q, pfo_q)
                s_col_q = None
                bf_col = _as_quantity(bf_col_q)
                g_col = _as_quantity(g_b_q)
                if bf_col is not None and g_col is not None and bf_col.unit == g_col.unit:
                    s_col_q = {"value": 0.5 * math.sqrt(bf_col.value * g_col.value), "unit": bf_col.unit}

                lines.append(f"- gage horizontal de pernos en columna lado {side_label} (g_b_col_{tag}) (inp): `{_format_quantity(g_b_q)}`")
                lines.append(f"- Distancia exterior ajustada lado {side_label} (pso_{tag}): `{_format_quantity(pso_q)}`")
                lines.append(f"- Distancia interior ajustada lado {side_label} (psi_{tag}): `{_format_quantity(psi_q)}`")
                lines.append(f"- Diametro de perforacion en columna lado {side_label} (dh_col_{tag}): `{_format_quantity(dh_q)}`")
                lines.append(f"- Parametro C de columna lado {side_label} (C_col_{tag}): `{_format_quantity(c_col_q)}`")
                lines.append(f"- Parametro s de columna lado {side_label} (s_col_{tag}): `{_format_quantity(s_col_q)}`")
                lines.append(
                    f"- Distancia h1 de columna lado {side_label} (h1_col_{tag}): "
                    f"`{_format_quantity(step61_inputs.get(f'h1_pe_{tag}'))}`"
                )
                lines.append(
                    f"- Distancia h2 de columna lado {side_label} (h2_col_{tag}): "
                    f"`{_format_quantity(step61_inputs.get(f'h2_pe_{tag}'))}`"
                )
                h3_val = step61_inputs.get(f"h3_pe_{tag}")
                if h3_val is not None:
                    lines.append(
                        f"- Distancia h3 de columna lado {side_label} (h3_col_{tag}): "
                        f"`{_format_quantity(h3_val)}`"
                    )
                h4_val = step61_inputs.get(f"h4_pe_{tag}")
                if h4_val is not None:
                    lines.append(
                        f"- Distancia h4 de columna lado {side_label} (h4_col_{tag}): "
                        f"`{_format_quantity(h4_val)}`"
                    )

            lines.append("")
            continue
        if chapter_number == 1 and scope == "WELD_5_COL":
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            rows_map: dict[str, dict] = {}
            for row in (rows or []):
                if str(row.get("scope", "")).upper() == "COLUMN":
                    rows_map[str(row.get("calculated_symbol", ""))] = row

            tipo_w5_col = _format_text(
                step1_inputs.get("tipo_w5_col")
                or step1_inputs.get("continuity_plate_weld_type")
            )
            fexx_w5_col_q = step1_inputs.get("Fexx_w5_col") or step1_inputs.get("weld_fexx")
            t_w5_col_q = step1_inputs.get("w_w5_col") or step1_inputs.get("t_w5_col")
            nl_w5_col = step1_inputs.get("nl_w5_col")
            l_gap_w5_col_q = step1_inputs.get("L_gap_w5_col")
            kds_w5_col = step1_inputs.get("kds_w5_col")
            b2_pc_col_q = step1_inputs.get("b2_pc_col")
            l_w5_col_text = "n/a"
            gap_q = _as_quantity(l_gap_w5_col_q)
            b2_q = _as_quantity(b2_pc_col_q)
            if b2_q is not None and gap_q is not None:
                if gap_q.unit == b2_q.unit:
                    gap_value = gap_q.value
                elif gap_q.unit == "mm" and b2_q.unit == "in":
                    gap_value = gap_q.value / 25.4
                elif gap_q.unit == "in" and b2_q.unit == "mm":
                    gap_value = gap_q.value * 25.4
                else:
                    gap_value = None
                if gap_value is not None:
                    l_w5_col_text = _format_quantity({"value": b2_q.value - 2.0 * gap_value, "unit": b2_q.unit})

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Tipo de soldadura #5 de platina de continuidad (tipo_w5_col) (inp): `{tipo_w5_col}`")
            lines.append(f"- Resistencia del electrodo de soldadura #5 (Fexx_w5_col) (inp): `{_format_quantity(fexx_w5_col_q)}`")
            lines.append(f"- Espesor/size de soldadura #5 (w_w5_col) (inp): `{_format_quantity(t_w5_col_q)}`")
            lines.append(f"- Numero de lineas de soldadura #5 (nl_w5_col) (inp): `{_format_text(nl_w5_col)}`")
            lines.append(f"- Separacion de extremos de soldadura #5 (L_gap_w5_col) (inp): `{_format_quantity(l_gap_w5_col_q)}`")
            lines.append(f"- Factor de direccion/sistema de soldadura #5 (kds_w5_col) (inp): `{_format_text(kds_w5_col)}`")
            lines.append(f"- Longitud efectiva de soldadura #5 (L_w5_col): `{l_w5_col_text}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "CONTINUITY_PLATE_COL":
            rows_map: dict[str, dict] = {}
            for row in (rows or []):
                if str(row.get("scope", "")).upper() == "COLUMN":
                    rows_map[str(row.get("calculated_symbol", ""))] = row
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}

            tpc_col_q = step1_inputs.get("t_pc_col") or step1_inputs.get("tpc_col") or step1_inputs.get("continuity_plate_thickness_tcp")
            b1_pc_col_q = step1_inputs.get("b1_pc_col")
            t_dp_col_q = step1_inputs.get("t_dp_col")
            n_dp_col = step1_inputs.get("n_dp_col")
            usar_pc_col = step1_inputs.get("usar_pc_col")
            if usar_pc_col is None:
                usar_pc_col = step1_inputs.get("continuity_plate_enabled")
            tipo_acero_pc_col = _format_text(
                step1_inputs.get("tipo_acero_pc_col")
                or step1_inputs.get("continuity_plate_steel_type")
            )
            kdet_col_q = step1_inputs.get("kdet_col")
            k1_col_q = step1_inputs.get("k1_col")
            tfdet_col_q = step1_inputs.get("tfdet_col")
            tw_col_q = (rows_map.get("tw_col") or {}).get("calculated")
            d_col_q = (rows_map.get("d_col") or {}).get("calculated")

            def _const_like(q: object, mm_value: float) -> dict | None:
                qq = _as_quantity(q)
                if qq is None:
                    return None
                if qq.unit == "mm":
                    return {"value": mm_value, "unit": "mm"}
                if qq.unit == "in":
                    return {"value": mm_value / 25.4, "unit": "in"}
                return None

            def _qsum(a: object, b: object, c: object, *, factors: tuple[float, float, float] = (1.0, 1.0, 1.0)) -> dict | None:
                qa = _as_quantity(a)
                qb = _as_quantity(b)
                qc = _as_quantity(c)
                if qa is None or qb is None or qc is None:
                    return None
                if not (qa.unit == qb.unit == qc.unit):
                    return None
                return {"value": factors[0] * qa.value + factors[1] * qb.value + factors[2] * qc.value, "unit": qa.unit}

            clip1_pc_col_q = _qsum(kdet_col_q, tfdet_col_q, _const_like(kdet_col_q, 38.0), factors=(1.0, -1.0, 1.0))
            l1_pc_col_q = _qsum(d_col_q, tfdet_col_q, _const_like(d_col_q, -3.0), factors=(1.0, -2.0, 1.0))
            l2_pc_col_q = _qsum(l1_pc_col_q, clip1_pc_col_q, _const_like(l1_pc_col_q, 0.0), factors=(1.0, -2.0, 0.0))
            clip2_core_q = _qsum(k1_col_q, tw_col_q, _const_like(k1_col_q, 0.0), factors=(1.0, -1.0, 0.0))
            clip2_pc_col_q = _qsum(
                clip2_core_q,
                _const_like(clip2_core_q, 0.0),
                _const_like(clip2_core_q, 12.0),
                factors=(0.5, 0.0, 1.0),
            )
            b2_pc_col_q = _qsum(b1_pc_col_q, clip2_pc_col_q, _const_like(b1_pc_col_q, 0.0), factors=(1.0, -1.0, 0.0))
            b11_pc_col_q = b1_pc_col_q
            b12_pc_col_q: dict | None = None
            b1_q = _as_quantity(b1_pc_col_q)
            tpc_q = _as_quantity(tpc_col_q)
            n_dp_int: int | None = None
            try:
                if n_dp_col is not None:
                    n_dp_int = int(n_dp_col)
            except (TypeError, ValueError):
                n_dp_int = None
            if b1_q is not None:
                if n_dp_int == 1 and tpc_q is not None:
                    if tpc_q.unit == b1_q.unit:
                        b12_pc_col_q = {"value": b1_q.value + tpc_q.value, "unit": b1_q.unit}
                    elif tpc_q.unit == "mm" and b1_q.unit == "in":
                        b12_pc_col_q = {"value": b1_q.value + (tpc_q.value / 25.4), "unit": "in"}
                    elif tpc_q.unit == "in" and b1_q.unit == "mm":
                        b12_pc_col_q = {"value": b1_q.value + (tpc_q.value * 25.4), "unit": "mm"}
                elif n_dp_int == 2:
                    b12_pc_col_q = {"value": b1_q.value, "unit": b1_q.unit}
            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Uso de platinas de continuidad (usar_pc_col) (inp): `{_format_text(usar_pc_col)}`")
            lines.append(f"- Tipo de acero de platina de continuidad (tipo_acero_pc_col) (inp): `{tipo_acero_pc_col}`")
            lines.append(f"- Espesor de platina de continuidad (t_pc_col) (inp): `{_format_quantity(tpc_col_q)}`")
            lines.append(f"- Ancho base de platina de continuidad (b1_pc_col) (inp): `{_format_quantity(b1_pc_col_q)}`")
            lines.append(f"- Ancho b1.1 de platina de continuidad (b1.1_pc_col): `{_format_quantity(b11_pc_col_q)}`")
            lines.append(f"- Ancho b1.2 de platina de continuidad (b1.2_pc_col): `{_format_quantity(b12_pc_col_q)}`")
            lines.append(f"- Distancia de recorte 1 de platina de continuidad (Clip1_pc_col): `{_format_quantity(clip1_pc_col_q)}`")
            lines.append(f"- Longitud util 1 de platina de continuidad (L1_pc_col): `{_format_quantity(l1_pc_col_q)}`")
            lines.append(f"- Longitud util 2 de platina de continuidad (L2_pc_col): `{_format_quantity(l2_pc_col_q)}`")
            lines.append(f"- Distancia de recorte 2 de platina de continuidad (Clip2_pc_col): `{_format_quantity(clip2_pc_col_q)}`")
            lines.append(f"- Ancho neto de platina de continuidad (b2_pc_col): `{_format_quantity(b2_pc_col_q)}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "DOUBLER_PLATE_COL":
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(
                f"- Uso de platina de enchape del alma (usar_dp_col) (inp): "
                f"`{_format_text(step1_inputs.get('doubler_plate_enabled'))}`"
            )
            lines.append(
                f"- Tipo de acero de platina de enchape del alma (tipo_acero_dp_col) (inp): "
                f"`{_format_text(step1_inputs.get('tipo_acero_dp_col'))}`"
            )
            lines.append(
                f"- Espesor de platina de enchape del alma (t_dp_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('t_dp_col'))}`"
            )
            lines.append(
                f"- Numero de platinas de enchape del alma (n_dp_col) (inp): "
                f"`{_format_text(step1_inputs.get('n_dp_col'))}`"
            )
            lines.append(
                f"- Condicion geometrica de platina de enchape (Extended_dp_col) (inp): "
                f"`{_format_text(step1_inputs.get('extended_dp_col'))}`"
            )
            lines.append(
                f"- Separacion de la platina de enchape respecto al alma (gap_dp_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('gap_dp_col'))}`"
            )
            estado_contacto_dp_col = step1_inputs.get("estado_contacto_dp_col")
            if estado_contacto_dp_col == "en_contacto_con_alma":
                estado_contacto_text = "En contacto con el alma (gap_dp_col <= 2.0 mm)"
            elif estado_contacto_dp_col == "sin_contacto_con_alma":
                estado_contacto_text = "Sin contacto con el alma (gap_dp_col > 2.0 mm)"
            else:
                estado_contacto_text = "n/a"
            lines.append(
                f"- Estado de contacto platina de enchape vs alma: "
                f"`{estado_contacto_text}`"
            )
            lines.append(
                f"- Altura neta de panel zone en columna para enchape (dz_dp_col): "
                f"`{_format_quantity(step1_inputs.get('dz_dp_col'))}`"
            )
            lines.append(
                f"- Ancho neto gobernante entre vigas para enchape (wz_dp_col): "
                f"`{_format_quantity(step1_inputs.get('wz_dp_col'))}`"
            )
            lines.append(
                f"- Altura de platina de enchape (h_dp_col): "
                f"`{_format_quantity(step1_inputs.get('h_dp_col'))}`"
            )
            h_dp_formula = str(step1_inputs.get("h_dp_col_formula") or "n/a").strip().lower()
            if h_dp_formula == "300 + max(d)":
                lines.append(
                    "- Ecuacion de h_dp_col: `h_dp_col = 300 mm + max{d_vgder, d_vgizq}` "
                    "(aplica cuando (`Extended_dp_col=false` y `usar_pc_col=false`) "
                    "o (`Extended_dp_col=true` y `usar_pc_col=true`))"
                )
            elif h_dp_formula == "300 + max(d-tf) - t_pc_col":
                lines.append(
                    "- Ecuacion de h_dp_col: `h_dp_col = 300 mm + max{d_vgder - tf_vgder, d_vgizq - tf_vgizq} - t_pc_col` "
                    "(aplica cuando `Extended_dp_col=false` y `usar_pc_col=true`)"
                )
            else:
                lines.append("- Ecuacion de h_dp_col: `n/a`")
            lines.append(
                f"- Ancho de platina de enchape (b_dp_col): "
                f"`{_format_quantity(step1_inputs.get('b_dp_col'))}`"
            )
            b_dp_formula = str(step1_inputs.get("b_dp_col_formula") or "n/a").strip().lower()
            if b_dp_formula == "d_col - 2*kdet_col":
                lines.append("- Ecuacion de b_dp_col: `b_dp_col = d_col - 2*kdet_col` (cuando `tipo_w8_col = CJP`)")
            elif b_dp_formula == "d_col - 2*tft_col":
                lines.append("- Ecuacion de b_dp_col: `b_dp_col = d_col - 2*tft_col` (cuando `tipo_w8_col = PJP` o `fillet`)")
            else:
                lines.append("- Ecuacion de b_dp_col: `n/a`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "WELD_7_COL":
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(
                f"- Tipo de soldadura #7 (tipo_w7_col) (inp): "
                f"`{_format_text(step1_inputs.get('tipo_w7_col'))}`"
            )
            lines.append(
                f"- Resistencia del electrodo de soldadura #7 (Fexx_w7_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('Fexx_w7_col') or step1_inputs.get('weld_fexx'))}`"
            )
            lines.append(
                f"- Espesor/size de soldadura #7 (w_w7_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('w_w7_col') or step1_inputs.get('t_w7_col'))}`"
            )
            lines.append(
                f"- Numero de filas de soldadura #7 (nfilas_w7_col) (inp): "
                f"`{_format_text(step1_inputs.get('nfilas_w7_col') if step1_inputs.get('nfilas_w7_col') is not None else step1_inputs.get('nl_w7_col'))}`"
            )
            lines.append(
                f"- Numero de columnas de soldadura #7 (ncolumna_w7_col) (inp): "
                f"`{_format_text(step1_inputs.get('ncolumna_w7_col'))}`"
            )
            lines.append(
                f"- Diametro de hueco para soldadura #7 (d_hole_w7_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('d_hole_w7_col'))}`"
            )
            lines.append(
                f"- Separacion horizontal centro a centro (sh_w7_col): "
                f"`{_format_quantity(step1_inputs.get('sh_w7_col'))}`"
            )
            lines.append(
                f"- Separacion vertical centro a centro (sv_w7_col): "
                f"`{_format_quantity(step1_inputs.get('sv_w7_col'))}`"
            )
            lines.append(
                f"- Espesor de parte contenedora (t_part_w7_col = t_pc_col): "
                f"`{_format_quantity(step1_inputs.get('t_part_w7_col'))}`"
            )
            lines.append("")
            continue
        if chapter_number == 1 and scope == "WELD_8_COL":
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            tipo_w8_step1_raw = _format_text(step1_inputs.get("tipo_w8_col"))
            tipo_w8_step1_norm = tipo_w8_step1_raw.strip().lower()
            if tipo_w8_step1_norm in {"partial_joint_penetration"}:
                tipo_w8_step1_norm = "pjp"
            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(
                f"- Tipo de soldadura #8 (tipo_w8_col) (inp): "
                f"`{_format_text(step1_inputs.get('tipo_w8_col'))}`"
            )
            if tipo_w8_step1_norm == "pjp":
                lines.append(
                    "- Nota PJP soldadura #8: `Debe ser conforme a AWS D1.8/D1.8M clause 4.3`"
                )
            lines.append(
                f"- Resistencia del electrodo de soldadura #8 (Fexx_w8_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('Fexx_w8_col') or step1_inputs.get('weld_fexx'))}`"
            )
            lines.append(
                f"- Espesor/size de soldadura #8 (w_w8_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('w_w8_col') or step1_inputs.get('t_w8_col'))}`"
            )
            lines.append(
                f"- Numero de lineas de soldadura #8 (nl_w8_col) (inp): "
                f"`{_format_text(step1_inputs.get('nl_w8_col'))}`"
            )
            lines.append(
                f"- Parametro Encr para soldadura #8 (Encr_w8_col): "
                f"`{_format_quantity(step1_inputs.get('Encr_w8_col'))}`"
            )
            if step1_inputs.get("Encr_w8_col_fuente") is not None:
                lines.append(
                    f"- Fuente de Encr_w8_col: "
                    f"`{_format_text(step1_inputs.get('Encr_w8_col_fuente'))}`"
                )
            lines.append(
                f"- Factor de direccion/sistema de soldadura #8 (kds_w8_col) (inp): "
                f"`{_format_text(step1_inputs.get('kds_w8_col'))}`"
            )
            lines.append("")
            continue
        if chapter_number == 1 and scope == "WELD_9_COL":
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(
                f"- Uso de soldadura #9 (use_weld_9_col) (inp): "
                f"`{_format_text(step1_inputs.get('use_weld_9_col'))}`"
            )
            lines.append(
                f"- Tipo de soldadura #9 (tipo_w9_col) (inp): "
                f"`{_format_text(step1_inputs.get('tipo_w9_col'))}`"
            )
            lines.append(
                f"- Resistencia del electrodo de soldadura #9 (Fexx_w9_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('Fexx_w9_col') or step1_inputs.get('weld_fexx'))}`"
            )
            lines.append(
                f"- Espesor/size de soldadura #9 (w_w9_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('w_w9_col') or step1_inputs.get('t_w9_col'))}`"
            )
            lines.append(
                f"- Numero de lineas de soldadura #9 (nl_w9_col) (inp): "
                f"`{_format_text(step1_inputs.get('nl_w9_col'))}`"
            )
            lines.append(
                f"- Separacion de extremos de soldadura #9 (L_gap_w9_col) (inp): "
                f"`{_format_quantity(step1_inputs.get('L_gap_w9_col'))}`"
            )
            lines.append(
                f"- Factor de direccion/sistema de soldadura #9 (kds_w9_col) (inp): "
                f"`{_format_text(step1_inputs.get('kds_w9_col'))}`"
            )
            lines.append(
                f"- Longitud efectiva de soldadura #9 (L_w9_col): "
                f"`{_format_quantity(step1_inputs.get('L_w9_col'))}`"
            )
            lines.append("")
            continue
        if chapter_number == 1 and scope in {"END_PLATE_STIFFENER_DER", "END_PLATE_STIFFENER_IZQ"}:
            side = "der" if scope.endswith("_DER") else "izq"
            side_label = "derecha" if side == "der" else "izquierda"
            side_tag = "vgder" if side == "der" else "vgizq"
            step2_inputs = (step_2 or {}).get("inputs", {}) if isinstance(step_2, dict) else {}
            note_h_key = f"h_pest_{side_tag}"
            note_l_key = f"l_pest_{side_tag}"
            note_ed_key = f"ed_pest_{side_tag}"
            tipo_acero_pest = _format_text(
                (step_1_inputs or {}).get(f"tipo_acero_pest_{side_tag}")
                or (step_1_inputs or {}).get(f"stiffener_steel_type_{side_tag}")
                or step2_inputs.get(f"tipo_acero_perfil_{side_tag}")
                or step2_inputs.get(f"beam_steel_type_{side_tag}")
                or step2_inputs.get("beam_steel_type")
            )
            t_pest = _format_quantity(
                (step_1_inputs or {}).get(f"t_pest_{side_tag}")
                or (step_1_inputs or {}).get(f"stiffener_thickness_{side_tag}")
                or (rows_by_scope_symbol.get((scope, f"t_pest_{side_tag}")) or {}).get("calculated")
            )
            h_pest = "n/a"
            l_pest = "n/a"
            ed_pest = "n/a"
            for note_item in grouped.get(scope, []):
                maybe_h = note_item.get(note_h_key)
                if isinstance(maybe_h, dict):
                    h_pest = _format_quantity(maybe_h)
                maybe_l = note_item.get(note_l_key)
                if isinstance(maybe_l, dict):
                    l_pest = _format_quantity(maybe_l)
                maybe_ed = note_item.get(note_ed_key)
                if isinstance(maybe_ed, dict):
                    ed_pest = _format_quantity(maybe_ed)
                if h_pest != "n/a" and l_pest != "n/a" and ed_pest != "n/a":
                    break

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(
                f"- Tipo de acero de rigidizador {side_label} "
                f"(tipo_acero_pest_{side_tag}) (inp): `{tipo_acero_pest}`"
            )
            lines.append(
                f"- Espesor de rigidizador {side_label} "
                f"(t_pest_{side_tag}) (inp): `{t_pest}`"
            )
            lines.append(
                f"- Altura del rigidizador de platina extremo {side_label} "
                f"(h_pest_{side_tag}): `{h_pest}`"
            )
            lines.append(
                f"- Longitud del rigidizador de platina extremo {side_label} "
                f"(L_pest_{side_tag}): `{l_pest}`"
            )
            lines.append(
                f"- Requisito de borde del rigidizador de platina extremo {side_label} "
                f"(Ed_pest_{side_tag}): `{ed_pest}`"
            )
            lines.append("")
            continue
        if chapter_number == 1 and scope in {"BOLTS_DER", "BOLTS_IZQ"}:
            side = "der" if scope.endswith("_DER") else "izq"
            side_label = "derecha" if side == "der" else "izquierda"
            side_tag = "vgder" if side == "der" else "vgizq"
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            step61 = (
                (step_6_1_by_side or {}).get(side)
                if isinstance((step_6_1_by_side or {}).get(side), dict)
                else {}
            )
            step62 = (
                (step_6_2_by_side or {}).get(side)
                if isinstance((step_6_2_by_side or {}).get(side), dict)
                else {}
            )
            inputs61 = step61.get("inputs", {}) if isinstance(step61, dict) else {}
            inter61 = step61.get("intermediates", {}) if isinstance(step61, dict) else {}
            inputs62 = step62.get("inputs", {}) if isinstance(step62, dict) else {}
            inter62 = step62.get("intermediates", {}) if isinstance(step62, dict) else {}

            bolt_diameter = inputs61.get("bolt_diameter") or inputs62.get("bolt_diameter") or step1_inputs.get("bolt_diameter")
            fnt_b = inputs61.get(f"fnt_b_{side_tag}")
            fnv_b = inputs62.get(f"fnv_b_{side_tag}")
            thread_b = inputs62.get(f"thread_b_{side_tag}")
            n_b = inputs62.get(f"n_b_{side_tag}")
            bolt_fabrication_standard = inputs61.get("bolt_fabrication_standard") or inputs62.get("bolt_fabrication_standard") or step1_inputs.get("bolt_fabrication_standard")
            bolt_tightening_type = inputs61.get("bolt_tightening_type") or inputs62.get("bolt_tightening_type") or step1_inputs.get("bolt_tightening_type")
            bolt_area = inter62.get(f"a_b_{side_tag}") or inter61.get(f"a_b_{side_tag}")

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Diametro nominal de perno lado {side_label} (db_b_{side_tag}) (inp): `{_format_quantity(bolt_diameter)}`")
            lines.append(f"- Resistencia nominal a traccion de perno lado {side_label} (Fnt_b_{side_tag}) (inp): `{_format_quantity(fnt_b)}`")
            lines.append(f"- Resistencia nominal a cortante de perno lado {side_label} (Fnv_b_{side_tag}) (inp): `{_format_quantity(fnv_b)}`")
            lines.append(f"- Condicion de rosca de perno lado {side_label} (thread_b_{side_tag}) (inp): `{_format_text(thread_b)}`")
            lines.append(f"- Numero de pernos lado {side_label} (n_b_{side_tag}) (inp): `{_format_text(n_b)}`")
            lines.append(f"- Norma de fabricacion del perno lado {side_label} (std_v_{side_tag}) (inp): `{_format_text(bolt_fabrication_standard)}`")
            lines.append(f"- Tipo de apriete del perno lado {side_label} (tipo_apriete_b_{side_tag}) (inp): `{_format_text(bolt_tightening_type)}`")
            lines.append(f"- Area efectiva de perno lado {side_label} (A_b_{side_tag}): `{_format_quantity(bolt_area)}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope in {"TABLE_6_1_DER", "TABLE_6_1_IZQ"}:
            side = "der" if scope.endswith("_DER") else "izq"
            side_label = "derecha" if side == "der" else "izquierda"
            side_tag = "vgder" if side == "der" else "vgizq"
            step731 = (
                (step_7_3_1_by_side or {}).get(side)
                if isinstance((step_7_3_1_by_side or {}).get(side), dict)
                else {}
            )
            inputs731 = step731.get("inputs", {}) if isinstance(step731, dict) else {}
            d_side = _format_quantity((rows_by_scope_symbol.get((scope, f"d_{side_tag}")) or {}).get("calculated"))
            bf_side = _format_quantity((rows_by_scope_symbol.get((scope, f"bf_{side_tag}")) or {}).get("calculated"))
            g_b_side = _format_quantity((rows_by_scope_symbol.get((scope, f"g_b_{side_tag}")) or {}).get("calculated"))
            tpe_side = _format_quantity(inputs731.get(f"tpe_{side_tag}") or (rows_by_scope_symbol.get((scope, f"tpe_{side_tag}")) or {}).get("calculated"))
            tf_side = _format_quantity(inputs731.get(f"tf_{side_tag}") or (rows_by_scope_symbol.get((scope, f"tf_{side_tag}")) or {}).get("calculated"))
            de_side = _format_quantity(inputs731.get(f"de_pe_{side_tag}") or (rows_by_scope_symbol.get((scope, f"de_pe_{side_tag}")) or {}).get("calculated"))
            pb_side = _format_quantity(inputs731.get(f"pb_pe_{side_tag}") or (rows_by_scope_symbol.get((scope, f"pb_pe_{side_tag}")) or {}).get("calculated"))
            pfo_side = _format_quantity(inputs731.get(f"pfo_pe_{side_tag}"))
            pfi_side = _format_quantity(inputs731.get(f"pfi_pe_{side_tag}"))

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Altura de viga lado {side_label} (d_{side_tag}) (inp): `{d_side}`")
            lines.append(f"- Ancho de ala de viga lado {side_label} (bf_{side_tag}) (inp): `{bf_side}`")
            lines.append(f"- Espesor de ala de viga lado {side_label} (tf_{side_tag}) (inp): `{tf_side}`")
            lines.append(f"- Gage horizontal de pernos lado {side_label} (g_b_{side_tag}) (inp): `{g_b_side}`")
            lines.append(f"- Espesor de platina extremo lado {side_label} (tpe_{side_tag}) (inp): `{tpe_side}`")
            lines.append(f"- Distancia de borde a fila 1 lado {side_label} (de_pe_{side_tag}) (inp): `{de_side}`")
            lines.append(f"- Distancia entre filas de pernos lado {side_label} (pb_pe_{side_tag}) (inp): `{pb_side}`")
            lines.append(f"- Distancia exterior a fila de pernos lado {side_label} (pfo_pe_{side_tag}) (inp): `{pfo_side}`")
            lines.append(f"- Distancia interior a fila de pernos lado {side_label} (pfi_pe_{side_tag}) (inp): `{pfi_side}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope in {"WELD_1_VGDER", "WELD_1_VGIZQ"}:
            side = "der" if scope.endswith("_VGDER") else "izq"
            side_label = "derecha" if side == "der" else "izquierda"
            side_tag = "vgder" if side == "der" else "vgizq"
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            step811 = (
                (step_8_1_1_by_side or {}).get(side)
                if isinstance((step_8_1_1_by_side or {}).get(side), dict)
                else {}
            )
            inputs811 = step811.get("inputs", {}) if isinstance(step811, dict) else {}
            tipo_w1 = _format_text(
                step1_inputs.get(f"tipo_w1_{side_tag}")
                or step1_inputs.get("end_plate_stiffener_weld_type")
                or inputs811.get("end_plate_stiffener_weld_type")
                or inputs811.get(f"tipo_w1_{side_tag}")
            )
            fexx_w1 = _format_quantity(
                step1_inputs.get(f"Fexx_w1_{side_tag}")
                or step1_inputs.get("weld_fexx")
            )
            w_w1 = _format_quantity(
                step1_inputs.get(f"w_w1_{side_tag}")
                or step1_inputs.get(f"end_plate_stiffener_weld_size_wst_{side_tag}")
                or step1_inputs.get("end_plate_stiffener_weld_size_wst")
            )
            nl_w1 = _format_text(
                step1_inputs.get(f"nl_w1_{side_tag}")
                or step1_inputs.get(f"end_plate_stiffener_weld_lines_nl_{side_tag}")
                or step1_inputs.get("end_plate_stiffener_weld_lines_nl")
            )
            l_gap_w1 = _format_quantity(step1_inputs.get(f"L_gap_w1_{side_tag}"))
            kds_w1 = _format_text(step1_inputs.get(f"kds_w1_{side_tag}"))
            l_w1_raw = step1_inputs.get(f"L_w1_{side_tag}") or step1_inputs.get(f"l_w1_{side_tag}")
            if l_w1_raw is None:
                gap_q = _as_quantity(step1_inputs.get(f"L_gap_w1_{side_tag}"))
                h_key = f"h_pest_{side_tag}"
                h_q = None
                for note_item in grouped.get(f"END_PLATE_STIFFENER_{'DER' if side == 'der' else 'IZQ'}", []):
                    maybe_h = note_item.get(h_key)
                    if isinstance(maybe_h, dict):
                        h_q = _as_quantity(maybe_h)
                        if h_q is not None:
                            break
                if h_q is not None and gap_q is not None:
                    clip_val = 25.0 if h_q.unit == "mm" else (25.0 / 25.4 if h_q.unit == "in" else None)
                    if clip_val is not None:
                        if gap_q.unit == h_q.unit:
                            gap_val = gap_q.value
                        elif gap_q.unit == "mm" and h_q.unit == "in":
                            gap_val = gap_q.value / 25.4
                        elif gap_q.unit == "in" and h_q.unit == "mm":
                            gap_val = gap_q.value * 25.4
                        else:
                            gap_val = None
                        if gap_val is not None:
                            l_w1_raw = {"value": h_q.value - 2.0 * gap_val - clip_val, "unit": h_q.unit}
            l_w1 = _format_quantity(l_w1_raw)

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Tipo de soldadura #1 lado {side_label} (tipo_w1_{side_tag}) (inp): `{tipo_w1}`")
            lines.append(f"- Resistencia del electrodo de soldadura #1 lado {side_label} (Fexx_w1_{side_tag}) (inp): `{fexx_w1}`")
            lines.append(f"- Espesor/size de soldadura #1 lado {side_label} (w_w1_{side_tag}) (inp): `{w_w1}`")
            lines.append(f"- Numero de lineas de soldadura #1 lado {side_label} (nl_w1_{side_tag}) (inp): `{nl_w1}`")
            lines.append(f"- Separacion de extremos de soldadura #1 lado {side_label} (L_gap_w1_{side_tag}) (inp): `{l_gap_w1}`")
            lines.append(f"- Factor de direccion/sistema de soldadura #1 lado {side_label} (kds_w1_{side_tag}) (inp): `{kds_w1}`")
            lines.append(f"- Longitud efectiva de soldadura #1 lado {side_label} (L_w1_{side_tag}): `{l_w1}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope in {"WELD_2_VGDER", "WELD_2_VGIZQ"}:
            side = "der" if scope.endswith("_VGDER") else "izq"
            side_label = "derecha" if side == "der" else "izquierda"
            side_tag = "vgder" if side == "der" else "vgizq"
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            step911 = (
                (step_9_1_1_by_side or {}).get(side)
                if isinstance((step_9_1_1_by_side or {}).get(side), dict)
                else {}
            )
            inputs911 = step911.get("inputs", {}) if isinstance(step911, dict) else {}
            tipo_w2 = _format_text(
                step1_inputs.get(f"tipo_w2_{side_tag}")
                or step1_inputs.get("beam_stiffener_weld_type")
                or step1_inputs.get("end_plate_beam_web_weld_type")
                or inputs911.get("beam_stiffener_weld_type")
                or inputs911.get(f"tipo_w2_{side_tag}")
            )
            fexx_w2 = _format_quantity(
                step1_inputs.get(f"Fexx_w2_{side_tag}")
                or step1_inputs.get("weld_fexx")
            )
            w_w2 = _format_quantity(
                step1_inputs.get(f"w_w2_{side_tag}")
                or step1_inputs.get(f"beam_stiffener_weld_size_wst2_{side_tag}")
                or step1_inputs.get("beam_stiffener_weld_size_wst2")
                or step1_inputs.get("end_plate_beam_web_weld_thickness_twe")
            )
            nl_w2 = _format_text(
                step1_inputs.get(f"nl_w2_{side_tag}")
                or step1_inputs.get(f"beam_stiffener_weld_lines_nl_w2_{side_tag}")
                or step1_inputs.get("beam_stiffener_weld_lines_nl_w2")
                or step1_inputs.get("end_plate_beam_web_weld_lines_nl")
            )
            l_gap_w2 = _format_quantity(step1_inputs.get(f"L_gap_w2_{side_tag}"))
            kds_w2 = _format_text(inputs911.get(f"kds_w2_{side_tag}") or step1_inputs.get(f"kds_w2_{side_tag}"))
            l_w2_raw = step1_inputs.get(f"L_w2_{side_tag}") or step1_inputs.get(f"l_w2_{side_tag}")
            if l_w2_raw is None:
                gap_q = _as_quantity(step1_inputs.get(f"L_gap_w2_{side_tag}"))
                l_key = f"l_pest_{side_tag}"
                l_pest_q = None
                for note_item in grouped.get(f"END_PLATE_STIFFENER_{'DER' if side == 'der' else 'IZQ'}", []):
                    maybe_l = note_item.get(l_key)
                    if isinstance(maybe_l, dict):
                        l_pest_q = _as_quantity(maybe_l)
                        if l_pest_q is not None:
                            break
                if l_pest_q is not None and gap_q is not None:
                    clip_val = 25.0 if l_pest_q.unit == "mm" else (25.0 / 25.4 if l_pest_q.unit == "in" else None)
                    if clip_val is not None:
                        if gap_q.unit == l_pest_q.unit:
                            gap_val = gap_q.value
                        elif gap_q.unit == "mm" and l_pest_q.unit == "in":
                            gap_val = gap_q.value / 25.4
                        elif gap_q.unit == "in" and l_pest_q.unit == "mm":
                            gap_val = gap_q.value * 25.4
                        else:
                            gap_val = None
                        if gap_val is not None:
                            l_w2_raw = {"value": l_pest_q.value - 2.0 * gap_val - clip_val, "unit": l_pest_q.unit}
            l_w2 = _format_quantity(l_w2_raw)

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Tipo de soldadura #2 lado {side_label} (tipo_w2_{side_tag}) (inp): `{tipo_w2}`")
            lines.append(f"- Resistencia del electrodo de soldadura #2 lado {side_label} (Fexx_w2_{side_tag}) (inp): `{fexx_w2}`")
            lines.append(f"- Espesor/size de soldadura #2 lado {side_label} (w_w2_{side_tag}) (inp): `{w_w2}`")
            lines.append(f"- Numero de lineas de soldadura #2 lado {side_label} (nl_w2_{side_tag}) (inp): `{nl_w2}`")
            lines.append(f"- Separacion de extremos de soldadura #2 lado {side_label} (L_gap_w2_{side_tag}) (inp): `{l_gap_w2}`")
            lines.append(f"- Factor de direccion/sistema de soldadura #2 lado {side_label} (kds_w2_{side_tag}) (inp): `{kds_w2}`")
            lines.append(f"- Longitud efectiva de soldadura #2 lado {side_label} (L_w2_{side_tag}): `{l_w2}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope in {"WELD_3_VGDER", "WELD_3_VGIZQ"}:
            side = "der" if scope.endswith("_VGDER") else "izq"
            side_label = "derecha" if side == "der" else "izquierda"
            side_tag = "vgder" if side == "der" else "vgizq"
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            step11 = (
                (step_11_w3_by_side or {}).get(side)
                if isinstance((step_11_w3_by_side or {}).get(side), dict)
                else {}
            )
            inputs11 = step11.get("inputs", {}) if isinstance(step11, dict) else {}

            tipo_w3 = _format_text(
                step1_inputs.get(f"tipo_w3_{side_tag}")
                or step1_inputs.get("end_plate_beam_web_weld_type")
                or inputs11.get(f"tipo_w3_{side_tag}")
            )
            fexx_w3 = _format_quantity(
                step1_inputs.get(f"Fexx_w3_{side_tag}")
                or step1_inputs.get("weld_fexx")
            )
            w_w3 = _format_quantity(
                step1_inputs.get(f"w_w3_{side_tag}")
                or step1_inputs.get(f"t_w3_{side_tag}")
                or step1_inputs.get("end_plate_beam_web_weld_thickness_twe")
            )
            nl_w3 = _format_text(
                step1_inputs.get(f"nl_w3_{side_tag}")
                or step1_inputs.get("end_plate_beam_web_weld_lines_nl")
            )
            kds_w3_raw = step1_inputs.get(f"kds_w3_{side_tag}") or inputs11.get(f"kds_w3_{side_tag}")
            kds_w3 = _format_text(kds_w3_raw)
            hwef_w3 = _format_quantity(inputs11.get(f"hwef_w3_{side_tag}"))

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Tipo de soldadura #3 lado {side_label} (tipo_w3_{side_tag}) (inp): `{tipo_w3}`")
            lines.append(f"- Resistencia del electrodo de soldadura #3 lado {side_label} (Fexx_w3_{side_tag}) (inp): `{fexx_w3}`")
            lines.append(f"- Espesor/size de soldadura #3 lado {side_label} (w_w3_{side_tag}) (inp): `{w_w3}`")
            lines.append(f"- Numero de lineas de soldadura #3 lado {side_label} (nl_w3_{side_tag}) (inp): `{nl_w3}`")
            if kds_w3_raw is not None:
                lines.append(f"- Factor de direccion/sistema de soldadura #3 lado {side_label} (kds_w3_{side_tag}) (inp): `{kds_w3}`")
            lines.append(f"- Longitud efectiva de soldadura #3 lado {side_label} (hwef_w3_{side_tag}): `{hwef_w3}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope in {"WELD_4_VGDER", "WELD_4_VGIZQ"}:
            side = "der" if scope.endswith("_VGDER") else "izq"
            side_label = "derecha" if side == "der" else "izquierda"
            side_tag = "vgder" if side == "der" else "vgizq"
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            step10 = (
                (step_10_w4_by_side or {}).get(side)
                if isinstance((step_10_w4_by_side or {}).get(side), dict)
                else {}
            )
            inputs10 = step10.get("inputs", {}) if isinstance(step10, dict) else {}

            tipo_w4 = _format_text(
                step1_inputs.get(f"tipo_w4_{side_tag}")
                or inputs10.get(f"tipo_w4_{side_tag}")
            )
            fexx_w4 = _format_quantity(
                step1_inputs.get(f"Fexx_w4_{side_tag}")
                or inputs10.get(f"Fexx_w4_{side_tag}")
                or step1_inputs.get("weld_fexx")
            )
            w_w4 = _format_quantity(
                step1_inputs.get(f"w_w4_{side_tag}")
                or step1_inputs.get(f"t_w4_{side_tag}")
                or inputs10.get(f"t_w4_{side_tag}")
            )
            t_w4_1 = _format_quantity(
                step1_inputs.get(f"t_w4.1_{side_tag}")
                or step1_inputs.get(f"t_w4_1_{side_tag}")
                or inputs10.get(f"t_w4_1_{side_tag}")
            )
            nl_w4 = _format_text(
                step1_inputs.get(f"nl_w4_{side_tag}")
                or inputs10.get(f"nl_w4_{side_tag}")
            )
            kds_w4_raw = step1_inputs.get(f"kds_w4_{side_tag}") or inputs10.get(f"kds_w4_{side_tag}")
            kds_w4 = _format_text(kds_w4_raw)
            l_w4 = _format_quantity(
                step1_inputs.get(f"L_w4_{side_tag}")
                or step1_inputs.get(f"l_w4_{side_tag}")
                or inputs10.get(f"l_w4_{side_tag}")
            )

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Tipo de soldadura #4 lado {side_label} (tipo_w4_{side_tag}) (inp): `{tipo_w4}`")
            lines.append(f"- Resistencia del electrodo de soldadura #4 lado {side_label} (Fexx_w4_{side_tag}) (inp): `{fexx_w4}`")
            lines.append(f"- Espesor/size de soldadura #4 lado {side_label} (w_w4_{side_tag}) (inp): `{w_w4}`")
            lines.append(f"- Espesor total de garganta requerida #4 lado {side_label} (t_w4.1_{side_tag}) (inp): `{t_w4_1}`")
            lines.append(f"- Numero de lineas de soldadura #4 lado {side_label} (nl_w4_{side_tag}) (inp): `{nl_w4}`")
            if kds_w4_raw is not None:
                lines.append(f"- Factor de direccion/sistema de soldadura #4 lado {side_label} (kds_w4_{side_tag}) (inp): `{kds_w4}`")
            lines.append(f"- Longitud efectiva de soldadura #4 lado {side_label} (L_w4_{side_tag}): `{l_w4}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "END_PLATE_DER":
            step731_inputs_der = (
                ((step_7_3_1_by_side or {}).get("der") or {}).get("inputs", {})
                if isinstance((step_7_3_1_by_side or {}).get("der"), dict)
                else {}
            )
            step711_inter_der = (
                ((step_7_1_1_by_side or {}).get("der") or {}).get("intermediates", {})
                if isinstance((step_7_1_1_by_side or {}).get("der"), dict)
                else {}
            )
            step61_inputs_der = (
                ((step_6_1_by_side or {}).get("der") or {}).get("inputs", {})
                if isinstance((step_6_1_by_side or {}).get("der"), dict)
                else {}
            )

            bpe_vgder = _format_quantity((rows_by_scope_symbol.get(("END_PLATE_DER", "bp_pe_vgder")) or {}).get("calculated"))
            bpe_vgder_q = _as_quantity((rows_by_scope_symbol.get(("END_PLATE_DER", "bp_pe_vgder")) or {}).get("calculated"))
            tpe_vgder = _format_quantity(step731_inputs_der.get("tpe_vgder"))
            de_pe_vgder = _format_quantity(
                step731_inputs_der.get("de_pe_vgder")
                or (rows_by_scope_symbol.get(("TABLE_6_1_DER", "de_pe_vgder")) or {}).get("calculated")
            )
            pb_pe_vgder = _format_quantity(step731_inputs_der.get("pb_pe_vgder"))
            pfo_pe_vgder = _format_quantity(step731_inputs_der.get("pfo_pe_vgder"))
            pfi_pe_vgder = _format_quantity(step731_inputs_der.get("pfi_pe_vgder"))
            dh_pe_vgder = _format_quantity(step731_inputs_der.get("dh_pe_vgder"))
            g_pe_vgder = _format_quantity(
                (rows_by_scope_symbol.get(("BEAM_DER", "g_b_vgder")) or {}).get("calculated")
            )
            g_pe_vgder_q = _as_quantity((rows_by_scope_symbol.get(("BEAM_DER", "g_b_vgder")) or {}).get("calculated"))
            deh_pe_vgder = "n/a"
            if bpe_vgder_q is not None and g_pe_vgder_q is not None:
                if bpe_vgder_q.unit == g_pe_vgder_q.unit:
                    deh_pe_vgder = _format_quantity(
                        {"value": (bpe_vgder_q.value - g_pe_vgder_q.value) / 2.0, "unit": bpe_vgder_q.unit}
                    )
            s_pe_vgder = _format_quantity(step711_inter_der.get("s"))
            h1_pe_vgder = _format_quantity(step61_inputs_der.get("h1_pe_vgder"))
            h2_pe_vgder = _format_quantity(step61_inputs_der.get("h2_pe_vgder"))
            h3_pe_vgder = _format_quantity(step61_inputs_der.get("h3_pe_vgder"))
            h4_pe_vgder = _format_quantity(step61_inputs_der.get("h4_pe_vgder"))

            hpe_vgder = "n/a"
            for note_item in grouped.get("END_PLATE_DER", []):
                maybe_hpe = note_item.get("hpe_vgder")
                if isinstance(maybe_hpe, dict):
                    hpe_vgder = _format_quantity(maybe_hpe)
                    break

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Altura de platina extremo de viga derecha (Hpe_vgder): `{hpe_vgder}`")
            lines.append(f"- Ancho de platina extremo de viga derecha (Bpe_vgder) (inp): `{bpe_vgder}`")
            lines.append(f"- Espesor de platina extremo de viga derecha (tpe_vgder) (inp): `{tpe_vgder}`")
            lines.append(f"- Distancia de borde a fila 1 de pernos (de_pe_vgder) (inp): `{de_pe_vgder}`")
            lines.append(f"- Distancia entre filas de pernos (pb_pe_vgder) (inp): `{pb_pe_vgder}`")
            lines.append(f"- Distancia exterior a fila de pernos (pfo_pe_vgder) (inp): `{pfo_pe_vgder}`")
            lines.append(f"- Distancia interior a fila de pernos (pfi_pe_vgder) (inp): `{pfi_pe_vgder}`")
            lines.append(f"- Diametro de perforacion de perno (dh_pe_vgder): `{dh_pe_vgder}`")
            lines.append(f"- Distancia horizontal entre pernos en platina (g_pe_vgder) (inp): `{g_pe_vgder}`")
            lines.append(f"- Distancia horizontal de borde en platina (deh_pe_vgder): `{deh_pe_vgder}`")
            lines.append(f"- Parametro s de platina extremo derecha (s_pe_vgder): `{s_pe_vgder}`")
            lines.append(f"- Distancia h1 de platina extremo derecha (h1_pe_vgder): `{h1_pe_vgder}`")
            lines.append(f"- Distancia h2 de platina extremo derecha (h2_pe_vgder): `{h2_pe_vgder}`")
            if h3_pe_vgder != "n/a":
                lines.append(f"- Distancia h3 de platina extremo derecha (h3_pe_vgder): `{h3_pe_vgder}`")
            if h4_pe_vgder != "n/a":
                lines.append(f"- Distancia h4 de platina extremo derecha (h4_pe_vgder): `{h4_pe_vgder}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "END_PLATE_IZQ":
            step731_inputs_izq = (
                ((step_7_3_1_by_side or {}).get("izq") or {}).get("inputs", {})
                if isinstance((step_7_3_1_by_side or {}).get("izq"), dict)
                else {}
            )
            step711_inter_izq = (
                ((step_7_1_1_by_side or {}).get("izq") or {}).get("intermediates", {})
                if isinstance((step_7_1_1_by_side or {}).get("izq"), dict)
                else {}
            )
            step61_inputs_izq = (
                ((step_6_1_by_side or {}).get("izq") or {}).get("inputs", {})
                if isinstance((step_6_1_by_side or {}).get("izq"), dict)
                else {}
            )

            bpe_vgizq = _format_quantity((rows_by_scope_symbol.get(("END_PLATE_IZQ", "bp_pe_vgizq")) or {}).get("calculated"))
            bpe_vgizq_q = _as_quantity((rows_by_scope_symbol.get(("END_PLATE_IZQ", "bp_pe_vgizq")) or {}).get("calculated"))
            tpe_vgizq = _format_quantity(step731_inputs_izq.get("tpe_vgizq"))
            de_pe_vgizq = _format_quantity(
                step731_inputs_izq.get("de_pe_vgizq")
                or (rows_by_scope_symbol.get(("TABLE_6_1_IZQ", "de_pe_vgizq")) or {}).get("calculated")
            )
            pb_pe_vgizq = _format_quantity(step731_inputs_izq.get("pb_pe_vgizq"))
            pfo_pe_vgizq = _format_quantity(step731_inputs_izq.get("pfo_pe_vgizq"))
            pfi_pe_vgizq = _format_quantity(step731_inputs_izq.get("pfi_pe_vgizq"))
            dh_pe_vgizq = _format_quantity(step731_inputs_izq.get("dh_pe_vgizq"))
            g_pe_vgizq = _format_quantity(
                (rows_by_scope_symbol.get(("BEAM_IZQ", "g_b_vgizq")) or {}).get("calculated")
            )
            g_pe_vgizq_q = _as_quantity((rows_by_scope_symbol.get(("BEAM_IZQ", "g_b_vgizq")) or {}).get("calculated"))
            deh_pe_vgizq = "n/a"
            if bpe_vgizq_q is not None and g_pe_vgizq_q is not None:
                if bpe_vgizq_q.unit == g_pe_vgizq_q.unit:
                    deh_pe_vgizq = _format_quantity(
                        {"value": (bpe_vgizq_q.value - g_pe_vgizq_q.value) / 2.0, "unit": bpe_vgizq_q.unit}
                    )
            s_pe_vgizq = _format_quantity(step711_inter_izq.get("s"))
            h1_pe_vgizq = _format_quantity(step61_inputs_izq.get("h1_pe_vgizq"))
            h2_pe_vgizq = _format_quantity(step61_inputs_izq.get("h2_pe_vgizq"))
            h3_pe_vgizq = _format_quantity(step61_inputs_izq.get("h3_pe_vgizq"))
            h4_pe_vgizq = _format_quantity(step61_inputs_izq.get("h4_pe_vgizq"))

            hpe_vgizq = "n/a"
            for note_item in grouped.get("END_PLATE_IZQ", []):
                maybe_hpe = note_item.get("hpe_vgizq")
                if isinstance(maybe_hpe, dict):
                    hpe_vgizq = _format_quantity(maybe_hpe)
                    break

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Altura de platina extremo de viga izquierda (Hpe_vgizq): `{hpe_vgizq}`")
            lines.append(f"- Ancho de platina extremo de viga izquierda (Bpe_vgizq) (inp): `{bpe_vgizq}`")
            lines.append(f"- Espesor de platina extremo de viga izquierda (tpe_vgizq) (inp): `{tpe_vgizq}`")
            lines.append(f"- Distancia de borde a fila 1 de pernos (de_pe_vgizq) (inp): `{de_pe_vgizq}`")
            lines.append(f"- Distancia entre filas de pernos (pb_pe_vgizq) (inp): `{pb_pe_vgizq}`")
            lines.append(f"- Distancia exterior a fila de pernos (pfo_pe_vgizq) (inp): `{pfo_pe_vgizq}`")
            lines.append(f"- Distancia interior a fila de pernos (pfi_pe_vgizq) (inp): `{pfi_pe_vgizq}`")
            lines.append(f"- Diametro de perforacion de perno (dh_pe_vgizq): `{dh_pe_vgizq}`")
            lines.append(f"- Distancia horizontal entre pernos en platina (g_pe_vgizq) (inp): `{g_pe_vgizq}`")
            lines.append(f"- Distancia horizontal de borde en platina (deh_pe_vgizq): `{deh_pe_vgizq}`")
            lines.append(f"- Parametro s de platina extremo izquierda (s_pe_vgizq): `{s_pe_vgizq}`")
            lines.append(f"- Distancia h1 de platina extremo izquierda (h1_pe_vgizq): `{h1_pe_vgizq}`")
            lines.append(f"- Distancia h2 de platina extremo izquierda (h2_pe_vgizq): `{h2_pe_vgizq}`")
            if h3_pe_vgizq != "n/a":
                lines.append(f"- Distancia h3 de platina extremo izquierda (h3_pe_vgizq): `{h3_pe_vgizq}`")
            if h4_pe_vgizq != "n/a":
                lines.append(f"- Distancia h4 de platina extremo izquierda (h4_pe_vgizq): `{h4_pe_vgizq}`")
            lines.append("")
            continue
        if chapter_number == 1 and scope == "WELD_6_COL":
            step1_inputs = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            rows_map: dict[str, dict] = {}
            for row in (rows or []):
                if str(row.get("scope", "")).upper() == "COLUMN":
                    rows_map[str(row.get("calculated_symbol", ""))] = row

            tipo_w6_col = _format_text(step1_inputs.get("tipo_w6_col"))
            fexx_w6_col_q = step1_inputs.get("Fexx_w6_col")
            t_w6_col_q = step1_inputs.get("w_w6_col") or step1_inputs.get("t_w6_col")
            nl_w6_col = step1_inputs.get("nl_w6_col")
            l_gap_w6_col_q = step1_inputs.get("L_gap_w6_col")
            kds_w6_col = step1_inputs.get("kds_w6_col")
            kdet_col_q = step1_inputs.get("kdet_col")
            tfdet_col_q = step1_inputs.get("tfdet_col")
            d_col_q = (rows_map.get("d_col") or {}).get("calculated")
            l_w6_col_text = "n/a"

            def _mm_in_unit(mm_value: float, unit: str) -> float | None:
                if unit == "mm":
                    return mm_value
                if unit == "in":
                    return mm_value / 25.4
                return None

            kdet_q = _as_quantity(kdet_col_q)
            tfdet_q = _as_quantity(tfdet_col_q)
            d_q = _as_quantity(d_col_q)
            gap_q = _as_quantity(l_gap_w6_col_q)
            if kdet_q is not None and tfdet_q is not None and d_q is not None and gap_q is not None:
                c38 = _mm_in_unit(38.0, kdet_q.unit)
                c3 = _mm_in_unit(3.0, d_q.unit)
                if c38 is not None and c3 is not None:
                    clip1 = {"value": kdet_q.value - tfdet_q.value + c38, "unit": kdet_q.unit}
                    if clip1["unit"] == d_q.unit:
                        l1 = {"value": d_q.value - 2.0 * tfdet_q.value - c3, "unit": d_q.unit}
                        l2 = {"value": l1["value"] - 2.0 * clip1["value"], "unit": l1["unit"]}
                        if gap_q.unit == l2["unit"]:
                            gap_value = gap_q.value
                        elif gap_q.unit == "mm" and l2["unit"] == "in":
                            gap_value = gap_q.value / 25.4
                        elif gap_q.unit == "in" and l2["unit"] == "mm":
                            gap_value = gap_q.value * 25.4
                        else:
                            gap_value = None
                        if gap_value is not None:
                            l_w6_col_text = _format_quantity({"value": l2["value"] - 2.0 * gap_value, "unit": l2["unit"]})

            lines.append(f"#### {chapter_number}.{section_offset}.1 Resumen de geometria")
            lines.append("")
            lines.append(f"- Tipo de soldadura #6 de platina de continuidad (tipo_w6_col) (inp): `{tipo_w6_col}`")
            lines.append(f"- Resistencia del electrodo de soldadura #6 (Fexx_w6_col) (inp): `{_format_quantity(fexx_w6_col_q)}`")
            lines.append(f"- Espesor/size de soldadura #6 (w_w6_col) (inp): `{_format_quantity(t_w6_col_q)}`")
            lines.append(f"- Numero de lineas de soldadura #6 (nl_w6_col) (inp): `{_format_text(nl_w6_col)}`")
            lines.append(f"- Separacion de extremos de soldadura #6 (L_gap_w6_col) (inp): `{_format_quantity(l_gap_w6_col_q)}`")
            lines.append(f"- Factor de direccion/sistema de soldadura #6 (kds_w6_col) (inp): `{_format_text(kds_w6_col)}`")
            lines.append(f"- Longitud efectiva de soldadura #6 (Lws_col): `{l_w6_col_text}`")
            lines.append("")
            continue
        local_note_index = 1
        for item in grouped.get(scope, []):
            description = _translate_text_es(item.get("description"))
            clause = _render_clause_text(
                item.get("clause"),
                item.get("source_document"),
                item.get("rule_id"),
            )
            lines.append(f"#### {chapter_number}.{section_offset}.{local_note_index} Nota tecnica - {description}")
            local_note_index += 1
            lines.append("")
            lines.append(f"- Ambito: `{scope}`")
            lines.append(f"- Clausula: `{clause}`")
            requirement = _translate_text_es(item.get("requirement"))
            if requirement != "n/a":
                lines.append(f"- Requisito: `{requirement}`")
            formula = _format_text(item.get("formula"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            lines.append("")
    return "\n".join(lines)


def _render_step_21_5_panel_zone_shear_wpzs(
    *,
    step_21_5_1: dict | None,
    heading_index: int,
) -> str:
    lines = [
        f"### 14.{heading_index}. Revision de capacidad a cortante (col)",
        "",
        f"#### 14.{heading_index}.1. ELR #1: Cortante en la zona del panel del alma (WPZS)",
        "",
    ]
    if not isinstance(step_21_5_1, dict):
        lines.extend(["- Resultado: `n/a`", ""])
        return "\n".join(lines)

    inputs = step_21_5_1.get("inputs", {})
    inter = step_21_5_1.get("intermediates", {})
    design_factors = step_21_5_1.get("design_factors", {})
    equation_text = _format_text(step_21_5_1.get("equation"))
    equation_text = (
        equation_text.replace("Ru_wpzs_col", "Ru_wpz_v2_col")
        .replace("phi*Rn_wpzs_col", "Rn_wpz_v2_col")
        .replace("Rn_wpzs_col", "Rn_wpz_v2_col")
        .replace("DCR_wpzs_col", "DCR_wpz_v2_col")
    )
    ru_equation_text = "Ru_wpz_v2_col = sum_Mf_col/(db-tf) - Vc2_col"
    equation_text = (
        f"{ru_equation_text}; {equation_text}"
        if equation_text != "n/a"
        else ru_equation_text
    )
    lines.extend(
        [
            f"- Clausula: `{_render_clause_text(step_21_5_1.get('clause'), step_21_5_1.get('source_document'), step_21_5_1.get('rule_id'))}`",
            f"- Ecuacion: `{equation_text}`",
            f"- Considera deformacion inelastica del panel zone: `{'Si' if inputs.get('consideracion_deformacion_inelastica_zona_panel') else 'No'}`",
            f"- phi_ductil (usado en WPZS): `{_format_text(inputs.get('phi_wpzs') or design_factors.get('phi_wpzs'))}`",
            f"- hb_col: `{_format_quantity(inputs.get('hb_col'))}`",
            f"- ht_col: `{_format_quantity(inputs.get('ht_col'))}`",
        ]
    )
    for side_tag in ("vgizq", "vgder"):
        mbe_max = inputs.get(f"mbe_col_{side_tag}_max")
        mbe_min = inputs.get(f"mbe_col_{side_tag}_min")
        if mbe_max is not None:
            lines.append(f"- Mbe_col_{side_tag}_max: `{_format_quantity(mbe_max)}`")
        if mbe_min is not None:
            lines.append(f"- Mbe_col_{side_tag}_min: `{_format_quantity(mbe_min)}`")
    lines.append(f"- sum_Mbe_col: `{_format_quantity(inputs.get('sum_mbe_col'))}`")
    lines.append(f"- Vc2_col: `{_format_quantity(inputs.get('vc2_col'))}`")
    for side_tag in ("vgizq", "vgder"):
        mf_max = inputs.get(f"mf_{side_tag}_max")
        mf_min = inputs.get(f"mf_{side_tag}_min")
        d_side = inputs.get(f"db_{side_tag}")
        if d_side is not None:
            lines.append(f"- d_{side_tag}: `{_format_quantity(d_side)}`")
        if mf_max is not None:
            lines.append(f"- Mf_{side_tag}_max: `{_format_quantity(mf_max)}`")
        if mf_min is not None:
            lines.append(f"- Mf_{side_tag}_min: `{_format_quantity(mf_min)}`")
    lines.extend(
        [
            f"- sum_Mf_col/(db-tf): `{_format_quantity(inputs.get('sum_mf_over_z_col'))}`",
            f"- Ru_wpz_v2_col: `{_format_quantity(step_21_5_1.get('demand'))}`",
            f"- Pr_col: `{_format_quantity(inputs.get('pr_col') or inputs.get('alpha_pr_col'))}`",
            f"- Py_col: `{_format_quantity(inputs.get('py_col'))}`",
            f"- alphaPr/Py: `{_format_text(inter.get('alpha_pr_over_py'))}`",
            f"- Ag_col: `{_format_quantity(inputs.get('ag_col'))}`",
            f"- Fy_col: `{_format_quantity(inputs.get('fy_col'))}`",
            f"- d_col: `{_format_quantity(inputs.get('d_col'))}`",
            f"- tw_col: `{_format_quantity(inputs.get('tw_col'))}`",
            f"- t_dp_col: `{_format_quantity(inputs.get('t_dp_col'))}`",
            f"- usar_weld_7_col: `{_format_text(inputs.get('use_weld_7_col'))}`",
            f"- tw_wpz_effective_col: `{_format_quantity(inputs.get('tw_wpz_effective_col'))}`",
            f"- Rn1_wpz_v2_col: `{_format_quantity(inputs.get('rn1_wpz_v2_col'))}`",
            f"- Rn2_wpz_v2_col: `{_format_quantity(inputs.get('rn2_wpz_v2_col'))}`",
            f"- bcf_col: `{_format_quantity(inputs.get('bcf_col'))}`",
            f"- tcf_col: `{_format_quantity(inputs.get('tcf_col'))}`",
            f"- Rn_wpz_v2_col: `{_format_quantity(step_21_5_1.get('capacity'))}`",
            f"- DCR_wpz_v2_col: `{_format_text(step_21_5_1.get('dcr'))}`",
            f"- Resultado: `{_render_result_plain_es(step_21_5_1.get('status'))}`",
            "",
        ]
    )
    lines.append("")
    return "\n".join(lines)


def render_memory_markdown(result: DetailedRunResult) -> str:
    rows = _collect_step_1_rows(result)
    notes = _collect_step_1_notes(result)
    step_1_inputs = _collect_step_1_inputs(result)
    def _to_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "si", "sí"}
        if isinstance(value, (int, float)):
            return value != 0
        return False

    use_pc_col = _to_bool(step_1_inputs.get("usar_pc_col")) or _to_bool(
        step_1_inputs.get("continuity_plate_enabled")
    )
    use_dp_col = _to_bool(step_1_inputs.get("usar_dp_col")) or _to_bool(
        step_1_inputs.get("doubler_plate_enabled")
    )

    excluded_scopes: set[str] = set()
    if not use_pc_col:
        excluded_scopes.update({"CONTINUITY_PLATE_COL", "WELD_5_COL", "WELD_6_COL"})
    if not use_dp_col:
        excluded_scopes.update({"DOUBLER_PLATE_COL", "WELD_7_COL", "WELD_8_COL", "WELD_9_COL"})

    if excluded_scopes:
        rows = [
            item
            for item in rows
            if str(item.get("scope", "")).upper() not in excluded_scopes
        ]
        notes = [
            item
            for item in notes
            if str(item.get("scope", "")).upper() not in excluded_scopes
        ]

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
    step_21_5_1_panel_zone = _collect_step_21_5_1_column_panel_zone_shear_wpzs(result)
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
        scope_template = _ordered_scopes_from_rows(rows)
        if use_pc_col and "CONTINUITY_PLATE_COL" not in scope_template:
            scope_template.append("CONTINUITY_PLATE_COL")
        if use_pc_col and "WELD_5_COL" not in scope_template:
            scope_template.append("WELD_5_COL")
        if use_pc_col and "WELD_6_COL" not in scope_template:
            scope_template.append("WELD_6_COL")
        if use_dp_col and "DOUBLER_PLATE_COL" not in scope_template:
            scope_template.append("DOUBLER_PLATE_COL")
        if use_dp_col and "WELD_7_COL" not in scope_template:
            scope_template.append("WELD_7_COL")
        if use_dp_col and "WELD_8_COL" not in scope_template:
            scope_template.append("WELD_8_COL")
        if use_dp_col and "WELD_9_COL" not in scope_template:
            scope_template.append("WELD_9_COL")
        step1_step2_hidden_scopes = {"TABLE_6_1_DER", "TABLE_6_1_IZQ"}
        scope_template_step1 = list(scope_template)
        scope_template_step2 = [s for s in scope_template if s not in step1_step2_hidden_scopes]
        step2_note_ids = {
            "section_6_3.end_plate_connection_location",
            "section_4_2.installation_requirements_der",
            "section_4_2.installation_requirements_izq",
            "section_4_2.installation_requirements_vgder",
            "section_4_2.installation_requirements_vgizq",
            "section_4_3.quality_control_assurance_der",
            "section_4_3.quality_control_assurance_izq",
            "section_4_3.quality_control_assurance_vgder",
            "section_4_3.quality_control_assurance_vgizq",
        }
        notes_step2 = [n for n in notes if _format_text(n.get("id")) in step2_note_ids] if notes else []
        notes_step1 = [n for n in notes if _format_text(n.get("id")) not in step2_note_ids] if notes else []
        content.extend(
            [
                "## Paso 1 - Propiedades geometricas, mecanicas y fabricacion",
                "",
                "Propiedades organizadas por ambito.",
                "",
            ]
        )
        if notes_step1:
            content.append(
                _render_step_1_notes_by_scope_template(
                    notes_step1,
                    chapter_number=1,
                    scopes=scope_template_step1,
                    rows=rows,
                    step_1_inputs=step_1_inputs,
                    step_2=step_2,
                    step_3=step_3,
                    step_4=step_4,
                    step_7_1_1_by_side=step_7_1_1_by_side,
                    step_6_1_by_side=step_6_1_by_side,
                    step_6_2_by_side=step_6_2_by_side,
                    step_8_1_1_by_side=step_8_1_1_by_side,
                    step_9_1_1_by_side=step_9_1_1_by_side,
                    step_11_w3_by_side=step_11_ctx_by_side,
                    step_10_w4_by_side=step_10_w4_1_1_by_side,
                    step_7_3_1_by_side=step_7_3_1_by_side,
                    step_21_5_1_panel_zone=step_21_5_1_panel_zone,
                )
            )
        else:
            content.append("No hay propiedades disponibles para este caso.")
        content.extend(
            [
                "",
                "## Paso 2 - Especificaciones tecnicas",
                "",
                "Especificaciones tecnicas organizadas por ambito.",
                "",
            ]
        )
        if scope_template_step2:
            if notes_step2:
                content.append(
                    _render_step_1_notes_by_scope_template(
                        notes_step2,
                        chapter_number=2,
                        scopes=scope_template_step2,
                    )
                )
            else:
                content.append(_render_scope_subtitles_only(chapter_number=2, scopes=scope_template_step2))
        else:
            content.append("No hay especificaciones tecnicas disponibles para este caso.")
        content.extend(
            [
                "",
                "## Paso 3 - Revisiones de requerimientos de propiedades mecanicas y geometricas",
                "",
                "Comparacion directa de valor calculado contra limite normativo (sin formato DCR).",
                "",
            ]
        )
        if rows:
            scope_template_step3 = list(scope_template)
            has_weld6_step3_checks = any(str(item.get("scope", "")).upper() == "WELD_6_COL" for item in rows)
            if not has_weld6_step3_checks and "WELD_6_COL" in scope_template_step3:
                scope_template_step3 = [s for s in scope_template_step3 if s != "WELD_6_COL"]
            content.append(
                _render_step_1_list_grouped_by_scope(
                    rows,
                    chapter_number=3,
                    scope_template=scope_template_step3,
                )
            )
        else:
            content.append("No hay revisiones de requerimientos disponibles para este caso.")
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
                (
                    lambda s71, s721, s722, s731, s732: _render_step_7_end_plate(
                        s71,
                        s721,
                        s722,
                        s731,
                        s732,
                        connection_type=result.connection_type,
                    )
                ),
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
        panel_zone_section_14 = _render_step_21_5_panel_zone_shear_wpzs(
            step_21_5_1=step_21_5_1_panel_zone,
            heading_index=heading_counter,
        ).strip()
        if panel_zone_section_14:
            side_sections_14.append(panel_zone_section_14)
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
    if connection_family_normalized == "moment_prequalified":
        def _render_step_24_continuity_plate_web_review(
            *,
            step_number: int,
            step12_by_side: dict[str, dict | None],
            step13_by_side: dict[str, dict | None],
            step14_2_1_by_side_local: dict[str, dict | None],
        ) -> str:
            def _convert_force_to_unit_local(force: Quantity | None, target_unit: str) -> Quantity | None:
                if force is None:
                    return None
                if force.unit == target_unit:
                    return force
                if force.unit == "kN" and target_unit == "kip":
                    return Quantity(value=force.value / 4.4482216152605, unit="kip")
                if force.unit == "kip" and target_unit == "kN":
                    return Quantity(value=force.value * 4.4482216152605, unit="kN")
                return None

            def _compute_ru_pc_for_side(side: str) -> dict[str, Any]:
                side_tag = "vgizq" if side == "izq" else "vgder"
                step12 = step12_by_side.get(side) if isinstance(step12_by_side, dict) else None
                step13 = step13_by_side.get(side) if isinstance(step13_by_side, dict) else None
                step14 = step14_2_1_by_side_local.get(side) if isinstance(step14_2_1_by_side_local, dict) else None

                i12 = step12.get("inputs", {}) if isinstance(step12, dict) else {}
                i13 = step13.get("inputs", {}) if isinstance(step13, dict) else {}
                i14 = step14.get("inputs", {}) if isinstance(step14, dict) else {}

                mf_q = _as_quantity(
                    i12.get("mf")
                    or i12.get("mf_vgizq_critico")
                    or i12.get("mf_vgder_critico")
                    or i13.get("mf_vgizq_critico")
                    or i13.get("mf_vgder_critico")
                )
                d_q = _as_quantity(i13.get("d_vgizq") or i13.get("d_vgder") or i12.get("d_vgizq") or i12.get("d_vgder"))
                tf_q = _as_quantity(
                    i13.get("tf_vgizq") or i13.get("tf_vgder") or i12.get("tf_vgizq") or i12.get("tf_vgder")
                )

                z_q: Quantity | None = None
                term_mf_over_z_q: Quantity | None = None
                if mf_q is not None and d_q is not None and tf_q is not None:
                    z_val = d_q.value - tf_q.value
                    if z_val > 0:
                        z_q = Quantity(value=z_val, unit=d_q.unit)
                        mf_conv = _convert_moment_to_unit(mf_q, "kN-mm" if z_q.unit == "mm" else "kip-in")
                        if mf_conv is not None:
                            force_unit = "kN" if z_q.unit == "mm" else "kip"
                            term_mf_over_z_q = Quantity(value=mf_conv.value / z_q.value, unit=force_unit)

                c22_q: Quantity | None = None
                if isinstance(step12, dict):
                    df12 = step12.get("design_factors", {}) if isinstance(step12.get("design_factors", {}), dict) else {}
                    phi12 = df12.get("phi_d")
                    try:
                        phi12_val = float(phi12)
                    except (TypeError, ValueError):
                        phi12_val = None
                    tf_col_q = _as_quantity(step12.get("capacity"))
                    i12_col = step12.get("inputs", {}) if isinstance(step12.get("inputs", {}), dict) else {}
                    fy_col_q = _as_quantity(i12_col.get("column_fy"))
                    yc_q = _as_quantity(i12_col.get("yc"))
                    if (
                        phi12_val is not None
                        and tf_col_q is not None
                        and fy_col_q is not None
                        and yc_q is not None
                        and z_q is not None
                        and tf_col_q.unit == "mm"
                        and fy_col_q.unit == "MPa"
                        and yc_q.unit == "mm"
                        and z_q.unit == "mm"
                    ):
                        # phi*Rn (force) = phi * ((tf_col^2 * Fy_col * Y)/(1.11*(d-tf))) in N; convert to kN.
                        c22_kN = (
                            phi12_val
                            * ((tf_col_q.value ** 2) * fy_col_q.value * yc_q.value)
                            / (1.11 * z_q.value)
                            / 1000.0
                        )
                        c22_q = Quantity(value=c22_kN, unit="kN")
                c23_1_q = _as_quantity(step13.get("capacity")) if isinstance(step13, dict) else None
                c23_2_q = _as_quantity(step14.get("capacity")) if isinstance(step14, dict) else None

                caps = [q for q in (c22_q, c23_1_q, c23_2_q) if isinstance(q, Quantity)]
                min_cap_q: Quantity | None = None
                if caps:
                    ref_unit = caps[0].unit
                    caps_conv: list[Quantity] = []
                    for q in caps:
                        q_conv = _convert_force_to_unit_local(q, ref_unit)
                        if q_conv is not None:
                            caps_conv.append(q_conv)
                    if caps_conv:
                        min_cap_q = min(caps_conv, key=lambda x: x.value)

                ru_pc_q: Quantity | None = None
                if term_mf_over_z_q is not None and min_cap_q is not None:
                    min_cap_in_term = _convert_force_to_unit_local(min_cap_q, term_mf_over_z_q.unit)
                    if min_cap_in_term is not None:
                        ru_pc_q = Quantity(value=term_mf_over_z_q.value - min_cap_in_term.value, unit=term_mf_over_z_q.unit)

                return {
                    "side_tag": side_tag,
                    "mf": mf_q,
                    "d": d_q,
                    "tf": tf_q,
                    "z": z_q,
                    "term_mf_over_z": term_mf_over_z_q,
                    "phi_rn_22": c22_q,
                    "phi_rn_23_1": c23_1_q,
                    "phi_rn_23_2": c23_2_q,
                    "min_cap": min_cap_q,
                    "ru_pc": ru_pc_q,
                }

            left = _compute_ru_pc_for_side("izq")
            right = _compute_ru_pc_for_side("der")

            ru_pc_col_q: Quantity | None = None
            ru_candidates = [q for q in (left.get("ru_pc"), right.get("ru_pc")) if isinstance(q, Quantity)]
            if ru_candidates:
                ref_u = ru_candidates[0].unit
                ru_conv: list[Quantity] = []
                for q in ru_candidates:
                    q_conv = _convert_force_to_unit_local(q, ref_u)
                    if q_conv is not None:
                        ru_conv.append(q_conv)
                if ru_conv:
                    ru_pc_col_q = max(ru_conv, key=lambda x: x.value)

            phi_pc = 0.9
            phi_rn_pc_col_q: Quantity | None = None
            dcr_pc_col: float | None = None
            result_pc_col: str = "n/a"
            fy_pc_col_q: Quantity | None = None
            phi_rn_pc_pminus_col_q: Quantity | None = None
            fcr_pc_col_q: Quantity | None = None
            e_pc_col_q: Quantity | None = None
            fe_pc_col_q: Quantity | None = None
            lp_pc_col_q: Quantity | None = None
            r_pc_col_q: Quantity | None = None
            klr_pc_col: float | None = None
            dcr_pc_pminus_col: float | None = None
            result_pc_pminus_col: str = "n/a"
            ru_pc_pminus_col_q: Quantity | None = None
            eq_fcr_used = "n/a"
            ru_pc_v2_col_q: Quantity | None = None
            phi_rn_pc_v2_col_q: Quantity | None = None
            dcr_pc_v2_col: float | None = None
            result_pc_v2_col: str = "n/a"
            n_pc_col_val: float | None = None
            steel_type_pc = _format_text((step_1_inputs or {}).get("tipo_acero_pc_col"))
            b1_pc_q = _as_quantity((step_1_inputs or {}).get("b1_pc_col"))
            t_pc_q = _as_quantity((step_1_inputs or {}).get("t_pc_col"))
            try:
                n_pc_raw = (step_1_inputs or {}).get("n_pc_col")
                n_pc_col_val = float(n_pc_raw) if n_pc_raw is not None else 1.0
            except (TypeError, ValueError):
                n_pc_col_val = None
            unit_system_pc: UnitSystem | None = None
            if isinstance(b1_pc_q, Quantity):
                unit_system_pc = _infer_unit_system_from_quantity(b1_pc_q.model_dump())
            elif isinstance(t_pc_q, Quantity):
                unit_system_pc = _infer_unit_system_from_quantity(t_pc_q.model_dump())
            if (
                steel_type_pc != "n/a"
                and isinstance(b1_pc_q, Quantity)
                and isinstance(t_pc_q, Quantity)
                and b1_pc_q.unit == t_pc_q.unit
                and unit_system_pc is not None
            ):
                try:
                    plate_props = get_plate_steel_properties(
                        steel_type=steel_type_pc,
                        unit_system=unit_system_pc,
                    )
                    fy_pc_col_q = plate_props.get("fy") if isinstance(plate_props.get("fy"), Quantity) else None
                    if isinstance(fy_pc_col_q, Quantity):
                        if unit_system_pc == UnitSystem.SI and fy_pc_col_q.unit == "MPa" and b1_pc_q.unit == "mm":
                            if n_pc_col_val is None:
                                raise ValueError("Invalid n_pc_col")
                            rn_n = fy_pc_col_q.value * b1_pc_q.value * t_pc_q.value * n_pc_col_val
                            phi_rn_pc_col_q = Quantity(value=phi_pc * rn_n / 1000.0, unit="kN")
                        elif unit_system_pc == UnitSystem.US and fy_pc_col_q.unit == "ksi" and b1_pc_q.unit == "in":
                            if n_pc_col_val is None:
                                raise ValueError("Invalid n_pc_col")
                            rn_kip = fy_pc_col_q.value * b1_pc_q.value * t_pc_q.value * n_pc_col_val
                            phi_rn_pc_col_q = Quantity(value=phi_pc * rn_kip, unit="kip")
                except Exception:
                    phi_rn_pc_col_q = None

            if isinstance(ru_pc_col_q, Quantity) and isinstance(phi_rn_pc_col_q, Quantity):
                phi_rn_conv = _convert_force_to_unit_local(phi_rn_pc_col_q, ru_pc_col_q.unit)
                if phi_rn_conv is not None and phi_rn_conv.value > 0:
                    dcr_pc_col = ru_pc_col_q.value / phi_rn_conv.value
                    result_pc_col = "Cumple" if dcr_pc_col <= 1.0 else "No cumple"

            # Compression (P-) per user-provided image:
            # Fcr by KL/r regions with K=0.65 and r=0.29*t_pc_col
            k_pc = 0.65
            if (
                isinstance(b1_pc_q, Quantity)
                and isinstance(t_pc_q, Quantity)
                and isinstance(fy_pc_col_q, Quantity)
                and n_pc_col_val is not None
                and unit_system_pc is not None
            ):
                d_col_q = _as_quantity((step_1_inputs or {}).get("column_depth_d_col"))
                kdet_col_q = _as_quantity((step_1_inputs or {}).get("kdet_col"))
                tfdet_col_q = _as_quantity((step_1_inputs or {}).get("tfdet_col"))

                if (
                    isinstance(d_col_q, Quantity)
                    and isinstance(kdet_col_q, Quantity)
                    and isinstance(tfdet_col_q, Quantity)
                    and d_col_q.unit == kdet_col_q.unit == tfdet_col_q.unit
                ):
                    unit_l = d_col_q.unit
                    add_38 = 38.0 if unit_l == "mm" else 38.0 / 25.4
                    sub_3 = 3.0 if unit_l == "mm" else 3.0 / 25.4
                    clip1_val = kdet_col_q.value - tfdet_col_q.value + add_38
                    l1_val = d_col_q.value - 2.0 * tfdet_col_q.value - sub_3
                    l2_val = l1_val - 2.0 * clip1_val
                    if l2_val > 0:
                        lp_pc_col_q = Quantity(value=l2_val, unit=unit_l)

                if isinstance(lp_pc_col_q, Quantity) and lp_pc_col_q.unit == t_pc_q.unit:
                    r_val = 0.29 * t_pc_q.value
                    if r_val > 0:
                        r_pc_col_q = Quantity(value=r_val, unit=t_pc_q.unit)
                        klr_pc_col = (k_pc * lp_pc_col_q.value) / r_pc_col_q.value

                if klr_pc_col is not None and klr_pc_col > 0:
                    if unit_system_pc == UnitSystem.SI:
                        e_pc_val = 200000.0  # MPa
                        e_pc_unit = "MPa"
                    else:
                        e_pc_val = 29000.0  # ksi
                        e_pc_unit = "ksi"
                    e_pc_col_q = Quantity(value=e_pc_val, unit=e_pc_unit)
                    e_over_fy = e_pc_val / fy_pc_col_q.value if fy_pc_col_q.value > 0 else None
                    if e_over_fy is not None and e_over_fy > 0:
                        fe_val = (math.pi ** 2) * e_pc_val / (klr_pc_col ** 2)
                        fe_pc_col_q = Quantity(value=fe_val, unit=e_pc_unit)
                        klr_limit_2 = 4.71 * math.sqrt(e_over_fy)
                        if klr_pc_col <= 25.0:
                            fcr_val = fy_pc_col_q.value
                        elif klr_pc_col <= klr_limit_2:
                            fcr_val = (0.658 ** (fy_pc_col_q.value / fe_val)) * fy_pc_col_q.value
                        else:
                            fcr_val = 0.877 * fe_val
                        fcr_pc_col_q = Quantity(value=fcr_val, unit=e_pc_unit)

                if isinstance(fcr_pc_col_q, Quantity):
                    if unit_system_pc == UnitSystem.SI and fcr_pc_col_q.unit == "MPa" and b1_pc_q.unit == "mm":
                        rn_n_pminus = fcr_pc_col_q.value * b1_pc_q.value * t_pc_q.value * n_pc_col_val
                        phi_rn_pc_pminus_col_q = Quantity(value=phi_pc * rn_n_pminus / 1000.0, unit="kN")
                    elif unit_system_pc == UnitSystem.US and fcr_pc_col_q.unit == "ksi" and b1_pc_q.unit == "in":
                        rn_kip_pminus = fcr_pc_col_q.value * b1_pc_q.value * t_pc_q.value * n_pc_col_val
                        phi_rn_pc_pminus_col_q = Quantity(value=phi_pc * rn_kip_pminus, unit="kip")

            ru_pc_pminus_col_q = ru_pc_col_q
            if isinstance(ru_pc_pminus_col_q, Quantity) and isinstance(phi_rn_pc_pminus_col_q, Quantity):
                phi_rn_pminus_conv = _convert_force_to_unit_local(phi_rn_pc_pminus_col_q, ru_pc_pminus_col_q.unit)
                if phi_rn_pminus_conv is not None and phi_rn_pminus_conv.value > 0:
                    dcr_pc_pminus_col = ru_pc_pminus_col_q.value / phi_rn_pminus_conv.value
                    result_pc_pminus_col = "Cumple" if dcr_pc_pminus_col <= 1.0 else "No cumple"

            if isinstance(klr_pc_col, float) and isinstance(fy_pc_col_q, Quantity):
                if klr_pc_col <= 25.0:
                    eq_fcr_used = "Fcr_pc_col = Fy_pc_col"
                elif (
                    isinstance(e_pc_col_q, Quantity)
                    and isinstance(fe_pc_col_q, Quantity)
                    and fy_pc_col_q.value > 0
                    and e_pc_col_q.value > 0
                    and klr_pc_col <= 4.71 * math.sqrt(e_pc_col_q.value / fy_pc_col_q.value)
                ):
                    eq_fcr_used = "Fcr_pc_col = 0.658^(Fy_pc_col/Fe_pc_col)*Fy_pc_col"
                else:
                    eq_fcr_used = "Fcr_pc_col = 0.877*Fe_pc_col"

            # Shear (V2) on continuity-plate web per user request:
            # Ru_pc_v2_col = Ru_pc_p+_col_vgder + Ru_pc_p+_col_vgizq
            # phi = 1.0
            # phi*Rn_pc_v2_col = phi * 0.6 * Fy_pc_col * t_pc_col * n_pc_col * L2_pc_col
            ru_left_q = left.get("ru_pc") if isinstance(left.get("ru_pc"), Quantity) else None
            ru_right_q = right.get("ru_pc") if isinstance(right.get("ru_pc"), Quantity) else None
            if isinstance(ru_left_q, Quantity) and isinstance(ru_right_q, Quantity):
                ru_right_conv = _convert_force_to_unit_local(ru_right_q, ru_left_q.unit)
                if ru_right_conv is not None:
                    ru_pc_v2_col_q = Quantity(value=ru_left_q.value + ru_right_conv.value, unit=ru_left_q.unit)
            elif isinstance(ru_left_q, Quantity):
                ru_pc_v2_col_q = ru_left_q
            elif isinstance(ru_right_q, Quantity):
                ru_pc_v2_col_q = ru_right_q

            phi_pc_v2 = 1.0
            l2_pc_col_q = lp_pc_col_q
            if (
                isinstance(fy_pc_col_q, Quantity)
                and isinstance(t_pc_q, Quantity)
                and isinstance(l2_pc_col_q, Quantity)
                and n_pc_col_val is not None
                and t_pc_q.unit == l2_pc_col_q.unit
                and unit_system_pc is not None
            ):
                if unit_system_pc == UnitSystem.SI and fy_pc_col_q.unit == "MPa" and t_pc_q.unit == "mm":
                    rn_n_v2 = 0.6 * fy_pc_col_q.value * t_pc_q.value * n_pc_col_val * l2_pc_col_q.value
                    phi_rn_pc_v2_col_q = Quantity(value=phi_pc_v2 * rn_n_v2 / 1000.0, unit="kN")
                elif unit_system_pc == UnitSystem.US and fy_pc_col_q.unit == "ksi" and t_pc_q.unit == "in":
                    rn_kip_v2 = 0.6 * fy_pc_col_q.value * t_pc_q.value * n_pc_col_val * l2_pc_col_q.value
                    phi_rn_pc_v2_col_q = Quantity(value=phi_pc_v2 * rn_kip_v2, unit="kip")

            if isinstance(ru_pc_v2_col_q, Quantity) and isinstance(phi_rn_pc_v2_col_q, Quantity):
                phi_rn_v2_conv = _convert_force_to_unit_local(phi_rn_pc_v2_col_q, ru_pc_v2_col_q.unit)
                if phi_rn_v2_conv is not None and phi_rn_v2_conv.value > 0:
                    dcr_pc_v2_col = ru_pc_v2_col_q.value / phi_rn_v2_conv.value
                    result_pc_v2_col = "Cumple" if dcr_pc_v2_col <= 1.0 else "No cumple"

            lines = [
                f"## Paso {step_number} - Revision de resistencia del alma de platinas de continuidad",
                "",
                f"### {step_number}.1. Revision de capacidad a traccion",
                "",
                f"#### {step_number}.1.1. ELR #1: Fluencia por traccion area bruta",
                "",
                "- Clausula: `Documento: AISC 358-22 | Seccion: Desarrollo interno de demanda para alma de platinas de continuidad`",
                (
                    f"- Ecuacion: `Ru_pc_p+_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq) - min{{phi*Rn_(23.1.1), "
                    f"phi*Rn_(23.2.1), phi*Rn_(22.1.1)}}; "
                    f"Ru_pc_p+_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder) - min{{phi*Rn_(23.3.1), "
                    f"phi*Rn_(23.4.1), phi*Rn_(22.2.1)}}; "
                    f"Ru_pc_p+_col = max{{Ru_pc_p+_col_vgder, Ru_pc_p+_col_vgizq}}; "
                    f"phi*Rn_pc_p+_col = phi * Fy_pc_col * b1_pc_col * t_pc_col * n_pc_col`"
                ),
                f"- Mf_vgizq_critico: `{_format_quantity(left.get('mf').model_dump() if isinstance(left.get('mf'), Quantity) else None)}`",
                f"- d_vgizq: `{_format_quantity(left.get('d').model_dump() if isinstance(left.get('d'), Quantity) else None)}`",
                f"- tf_vgizq: `{_format_quantity(left.get('tf').model_dump() if isinstance(left.get('tf'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (22.1.1): `{_format_quantity(left.get('phi_rn_22').model_dump() if isinstance(left.get('phi_rn_22'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (23.1.1): `{_format_quantity(left.get('phi_rn_23_1').model_dump() if isinstance(left.get('phi_rn_23_1'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (23.2.1): `{_format_quantity(left.get('phi_rn_23_2').model_dump() if isinstance(left.get('phi_rn_23_2'), Quantity) else None)}`",
                f"- min_capacidad_vgizq: `{_format_quantity(left.get('min_cap').model_dump() if isinstance(left.get('min_cap'), Quantity) else None)}`",
                f"- Ru_pc_p+_col_vgizq: `{_format_quantity(left.get('ru_pc').model_dump() if isinstance(left.get('ru_pc'), Quantity) else None)}`",
                f"- Mf_vgder_critico: `{_format_quantity(right.get('mf').model_dump() if isinstance(right.get('mf'), Quantity) else None)}`",
                f"- d_vgder: `{_format_quantity(right.get('d').model_dump() if isinstance(right.get('d'), Quantity) else None)}`",
                f"- tf_vgder: `{_format_quantity(right.get('tf').model_dump() if isinstance(right.get('tf'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (22.2.1): `{_format_quantity(right.get('phi_rn_22').model_dump() if isinstance(right.get('phi_rn_22'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (23.3.1): `{_format_quantity(right.get('phi_rn_23_1').model_dump() if isinstance(right.get('phi_rn_23_1'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (23.4.1): `{_format_quantity(right.get('phi_rn_23_2').model_dump() if isinstance(right.get('phi_rn_23_2'), Quantity) else None)}`",
                f"- min_capacidad_vgder: `{_format_quantity(right.get('min_cap').model_dump() if isinstance(right.get('min_cap'), Quantity) else None)}`",
                f"- Ru_pc_p+_col_vgder: `{_format_quantity(right.get('ru_pc').model_dump() if isinstance(right.get('ru_pc'), Quantity) else None)}`",
                f"- Ru_pc_p+_col: `{_format_quantity(ru_pc_col_q.model_dump() if isinstance(ru_pc_col_q, Quantity) else None)}`",
                f"- phi usado: `{_format_decimal(phi_pc)}`",
                f"- Fy_pc_col: `{_format_quantity(fy_pc_col_q.model_dump() if isinstance(fy_pc_col_q, Quantity) else None)}`",
                f"- b1_pc_col: `{_format_quantity(b1_pc_q.model_dump() if isinstance(b1_pc_q, Quantity) else None)}`",
                f"- t_pc_col: `{_format_quantity(t_pc_q.model_dump() if isinstance(t_pc_q, Quantity) else None)}`",
                f"- n_pc_col: `{_format_text(n_pc_col_val)}`",
                f"- phi*Rn_pc_p+_col: `{_format_quantity(phi_rn_pc_col_q.model_dump() if isinstance(phi_rn_pc_col_q, Quantity) else None)}`",
                f"- DCR_pc_p+_col: `{_format_decimal(dcr_pc_col) if dcr_pc_col is not None else 'n/a'}`",
                f"- Resultado: `{_render_result_plain_es(result_pc_col)}`",
                "",
                f"### {step_number}.2. Revision de capacidad a compresion",
                "",
                f"#### {step_number}.2.1. ELR #1: Pandeo por flexion",
                "",
                "- Clausula: `Documento: AISC 358-22 | Seccion: Formula de Fcr segun imagen de usuario (K=0.65)`",
                (
                    f"- Ecuacion: `"
                    f"{eq_fcr_used}; "
                    f"phi*Rn_pc_p-_col = phi * Fcr_pc_col * b1_pc_col * t_pc_col * n_pc_col`"
                ),
                f"- Mf_vgizq_critico: `{_format_quantity(left.get('mf').model_dump() if isinstance(left.get('mf'), Quantity) else None)}`",
                f"- d_vgizq: `{_format_quantity(left.get('d').model_dump() if isinstance(left.get('d'), Quantity) else None)}`",
                f"- tf_vgizq: `{_format_quantity(left.get('tf').model_dump() if isinstance(left.get('tf'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (22.1.1): `{_format_quantity(left.get('phi_rn_22').model_dump() if isinstance(left.get('phi_rn_22'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (23.1.1): `{_format_quantity(left.get('phi_rn_23_1').model_dump() if isinstance(left.get('phi_rn_23_1'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (23.2.1): `{_format_quantity(left.get('phi_rn_23_2').model_dump() if isinstance(left.get('phi_rn_23_2'), Quantity) else None)}`",
                f"- min_capacidad_vgizq: `{_format_quantity(left.get('min_cap').model_dump() if isinstance(left.get('min_cap'), Quantity) else None)}`",
                f"- Ru_pc_p-_col_vgizq: `{_format_quantity(left.get('ru_pc').model_dump() if isinstance(left.get('ru_pc'), Quantity) else None)}`",
                f"- Mf_vgder_critico: `{_format_quantity(right.get('mf').model_dump() if isinstance(right.get('mf'), Quantity) else None)}`",
                f"- d_vgder: `{_format_quantity(right.get('d').model_dump() if isinstance(right.get('d'), Quantity) else None)}`",
                f"- tf_vgder: `{_format_quantity(right.get('tf').model_dump() if isinstance(right.get('tf'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (22.2.1): `{_format_quantity(right.get('phi_rn_22').model_dump() if isinstance(right.get('phi_rn_22'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (23.3.1): `{_format_quantity(right.get('phi_rn_23_1').model_dump() if isinstance(right.get('phi_rn_23_1'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (23.4.1): `{_format_quantity(right.get('phi_rn_23_2').model_dump() if isinstance(right.get('phi_rn_23_2'), Quantity) else None)}`",
                f"- min_capacidad_vgder: `{_format_quantity(right.get('min_cap').model_dump() if isinstance(right.get('min_cap'), Quantity) else None)}`",
                f"- Ru_pc_p-_col_vgder: `{_format_quantity(right.get('ru_pc').model_dump() if isinstance(right.get('ru_pc'), Quantity) else None)}`",
                f"- Ru_pc_p-_col: `{_format_quantity(ru_pc_pminus_col_q.model_dump() if isinstance(ru_pc_pminus_col_q, Quantity) else None)}`",
                f"- phi usado: `{_format_decimal(phi_pc)}`",
                f"- K: `{_format_decimal(k_pc)}`",
                f"- Lp_pc_col: `{_format_quantity(lp_pc_col_q.model_dump() if isinstance(lp_pc_col_q, Quantity) else None)}`",
                f"- r_pc_col: `{_format_quantity(r_pc_col_q.model_dump() if isinstance(r_pc_col_q, Quantity) else None)}`",
                f"- KLr_pc_col: `{_format_decimal(klr_pc_col) if klr_pc_col is not None else 'n/a'}`",
                f"- E_pc_col: `{_format_quantity(e_pc_col_q.model_dump() if isinstance(e_pc_col_q, Quantity) else None)}`",
                f"- Fy_pc_col: `{_format_quantity(fy_pc_col_q.model_dump() if isinstance(fy_pc_col_q, Quantity) else None)}`",
                f"- Fe_pc_col: `{_format_quantity(fe_pc_col_q.model_dump() if isinstance(fe_pc_col_q, Quantity) else None)}`",
                f"- Fcr_pc_col: `{_format_quantity(fcr_pc_col_q.model_dump() if isinstance(fcr_pc_col_q, Quantity) else None)}`",
                f"- b1_pc_col: `{_format_quantity(b1_pc_q.model_dump() if isinstance(b1_pc_q, Quantity) else None)}`",
                f"- t_pc_col: `{_format_quantity(t_pc_q.model_dump() if isinstance(t_pc_q, Quantity) else None)}`",
                f"- n_pc_col: `{_format_text(n_pc_col_val)}`",
                f"- phi*Rn_pc_p-_col: `{_format_quantity(phi_rn_pc_pminus_col_q.model_dump() if isinstance(phi_rn_pc_pminus_col_q, Quantity) else None)}`",
                f"- DCR_pc_p-_col: `{_format_decimal(dcr_pc_pminus_col) if dcr_pc_pminus_col is not None else 'n/a'}`",
                f"- Resultado: `{_render_result_plain_es(result_pc_pminus_col)}`",
                "",
                f"### {step_number}.3. Revision de capacidad a cortante",
                "",
                f"#### {step_number}.3.1. ELR #1: Fluencia por cortante del area bruta",
                "",
                "- Clausula: `Documento: AISC 360-22 | Seccion: G2.1 (adaptado a demanda de alma de platina de continuidad)`",
                (
                    "- Ecuacion: `Ru_pc_v2_col = Ru_pc_p+_col_vgder + Ru_pc_p+_col_vgizq; "
                    "phi*Rn_pc_v2_col = phi * 0.6 * Fy_pc_col * t_pc_col * n_pc_col * L2_pc_col; "
                    "DCR_pc_v2_col = Ru_pc_v2_col / phi*Rn_pc_v2_col`"
                ),
                f"- Mf_vgizq_critico: `{_format_quantity(left.get('mf').model_dump() if isinstance(left.get('mf'), Quantity) else None)}`",
                f"- d_vgizq: `{_format_quantity(left.get('d').model_dump() if isinstance(left.get('d'), Quantity) else None)}`",
                f"- tf_vgizq: `{_format_quantity(left.get('tf').model_dump() if isinstance(left.get('tf'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (22.1.1): `{_format_quantity(left.get('phi_rn_22').model_dump() if isinstance(left.get('phi_rn_22'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (23.1.1): `{_format_quantity(left.get('phi_rn_23_1').model_dump() if isinstance(left.get('phi_rn_23_1'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgizq (23.2.1): `{_format_quantity(left.get('phi_rn_23_2').model_dump() if isinstance(left.get('phi_rn_23_2'), Quantity) else None)}`",
                f"- min_capacidad_vgizq: `{_format_quantity(left.get('min_cap').model_dump() if isinstance(left.get('min_cap'), Quantity) else None)}`",
                f"- Ru_pc_p+_col_vgizq: `{_format_quantity(left.get('ru_pc').model_dump() if isinstance(left.get('ru_pc'), Quantity) else None)}`",
                f"- Mf_vgder_critico: `{_format_quantity(right.get('mf').model_dump() if isinstance(right.get('mf'), Quantity) else None)}`",
                f"- d_vgder: `{_format_quantity(right.get('d').model_dump() if isinstance(right.get('d'), Quantity) else None)}`",
                f"- tf_vgder: `{_format_quantity(right.get('tf').model_dump() if isinstance(right.get('tf'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (22.2.1): `{_format_quantity(right.get('phi_rn_22').model_dump() if isinstance(right.get('phi_rn_22'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (23.3.1): `{_format_quantity(right.get('phi_rn_23_1').model_dump() if isinstance(right.get('phi_rn_23_1'), Quantity) else None)}`",
                f"- phi*Rn_cw_v2_col_vgder (23.4.1): `{_format_quantity(right.get('phi_rn_23_2').model_dump() if isinstance(right.get('phi_rn_23_2'), Quantity) else None)}`",
                f"- min_capacidad_vgder: `{_format_quantity(right.get('min_cap').model_dump() if isinstance(right.get('min_cap'), Quantity) else None)}`",
                f"- Ru_pc_p+_col_vgder: `{_format_quantity(right.get('ru_pc').model_dump() if isinstance(right.get('ru_pc'), Quantity) else None)}`",
                f"- Ru_pc_v2_col: `{_format_quantity(ru_pc_v2_col_q.model_dump() if isinstance(ru_pc_v2_col_q, Quantity) else None)}`",
                f"- phi usado: `{_format_decimal(phi_pc_v2)}`",
                f"- Fy_pc_col: `{_format_quantity(fy_pc_col_q.model_dump() if isinstance(fy_pc_col_q, Quantity) else None)}`",
                f"- t_pc_col: `{_format_quantity(t_pc_q.model_dump() if isinstance(t_pc_q, Quantity) else None)}`",
                f"- n_pc_col: `{_format_text(n_pc_col_val)}`",
                f"- L2_pc_col: `{_format_quantity(l2_pc_col_q.model_dump() if isinstance(l2_pc_col_q, Quantity) else None)}`",
                f"- phi*Rn_pc_v2_col: `{_format_quantity(phi_rn_pc_v2_col_q.model_dump() if isinstance(phi_rn_pc_v2_col_q, Quantity) else None)}`",
                f"- DCR_pc_v2_col: `{_format_decimal(dcr_pc_v2_col) if dcr_pc_v2_col is not None else 'n/a'}`",
                f"- Resultado: `{_render_result_plain_es(result_pc_v2_col)}`",
                "",
            ]
            return "\n".join(lines)

        assigned_step_number = next_step_number
        block_24 = _render_step_24_continuity_plate_web_review(
            step_number=assigned_step_number,
            step12_by_side=step_12_1_1_by_side,
            step13_by_side=step_13_1_1_by_side,
            step14_2_1_by_side_local=step_14_2_1_by_side,
        )
        block_24 = _align_nested_heading_numbers_with_step(block_24, step_number=assigned_step_number)
        content.append(block_24)
        next_step_number += 1
        use_pc_col_25 = _to_bool(
            step_1_inputs.get("continuity_plate_enabled")
            if isinstance(step_1_inputs, dict)
            else None
        )
        if isinstance(step_1_inputs, dict) and not use_pc_col_25:
            use_pc_col_25 = _to_bool(step_1_inputs.get("usar_pc_col"))
        if use_pc_col_25:
            assigned_step_number = next_step_number
            step1 = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            tipo_w5_raw = _format_text(step1.get("tipo_w5_col"))
            tipo_w5_norm = tipo_w5_raw.strip().lower()
            if tipo_w5_norm in {"complete_joint_penetration"}:
                tipo_w5_norm = "cjp"
            elif tipo_w5_norm in {"single_sided_fillet", "double_sided_fillet"}:
                tipo_w5_norm = "fillet"

            n_pc_val = 1.0
            try:
                if step1.get("n_pc_col") is not None:
                    n_pc_val = float(step1.get("n_pc_col"))
            except (TypeError, ValueError):
                n_pc_val = 1.0

            phi_fragil = 0.75
            try:
                if step1.get("phi_fragil") is not None:
                    phi_fragil = float(step1.get("phi_fragil"))
            except (TypeError, ValueError):
                phi_fragil = 0.75

            b2_pc_q = _as_quantity(step1.get("b2_pc_col"))
            t_pc_q = _as_quantity(step1.get("t_pc_col"))
            l_w5_col_q = _as_quantity(step1.get("L_w5_col")) or _as_quantity(step1.get("l_w5_col"))
            fexx_w5_q = _as_quantity(step1.get("Fexx_w5_col"))
            t_w5_q = _as_quantity(step1.get("w_w5_col")) or _as_quantity(step1.get("t_w5_col"))
            unit_system_w5: UnitSystem | None = None
            if isinstance(b2_pc_q, Quantity):
                unit_system_w5 = _infer_unit_system_from_quantity(b2_pc_q.model_dump())
            elif isinstance(t_pc_q, Quantity):
                unit_system_w5 = _infer_unit_system_from_quantity(t_pc_q.model_dump())

            fy_pc_col_q: Quantity | None = None
            steel_type_pc = _format_text(step1.get("tipo_acero_pc_col"))
            if steel_type_pc != "n/a" and unit_system_w5 is not None:
                try:
                    fy_pc_col_q = get_plate_steel_properties(
                        steel_type=steel_type_pc,
                        unit_system=unit_system_w5,
                    ).get("fy")
                except Exception:
                    fy_pc_col_q = None

            ru_w3_p_pos_col_q: Quantity | None = None
            if (
                isinstance(fy_pc_col_q, Quantity)
                and isinstance(b2_pc_q, Quantity)
                and isinstance(t_pc_q, Quantity)
                and b2_pc_q.unit == t_pc_q.unit
                and unit_system_w5 is not None
            ):
                if unit_system_w5 == UnitSystem.SI and fy_pc_col_q.unit == "MPa" and b2_pc_q.unit == "mm":
                    ru_w3_p_pos_col_q = Quantity(
                        value=(fy_pc_col_q.value * b2_pc_q.value * t_pc_q.value * n_pc_val) / 1000.0,
                        unit="kN",
                    )
                elif unit_system_w5 == UnitSystem.US and fy_pc_col_q.unit == "ksi" and b2_pc_q.unit == "in":
                    ru_w3_p_pos_col_q = Quantity(
                        value=fy_pc_col_q.value * b2_pc_q.value * t_pc_q.value * n_pc_val,
                        unit="kip",
                    )

            phi_rn_w3_p_pos_col_q: Quantity | None = None
            dcr_w3_p_pos_col: float | None = None
            result_w3_p_pos_col = "n/a"
            nl_w5_col = None
            try:
                if step1.get("nl_w5_col") is not None:
                    nl_w5_col = int(step1.get("nl_w5_col"))
            except (TypeError, ValueError):
                nl_w5_col = None
            kds_w5_col = None
            try:
                if step1.get("kds_w5_col") is not None:
                    kds_w5_col = float(step1.get("kds_w5_col"))
            except (TypeError, ValueError):
                kds_w5_col = None

            if tipo_w5_norm == "fillet":
                if (
                    isinstance(ru_w3_p_pos_col_q, Quantity)
                    and isinstance(fexx_w5_q, Quantity)
                    and isinstance(t_w5_q, Quantity)
                    and isinstance(l_w5_col_q, Quantity)
                    and nl_w5_col is not None
                    and kds_w5_col is not None
                    and unit_system_w5 is not None
                ):
                    try:
                        weld_check_w5 = compute_fillet_weld_check_with_kds(
                            demand=ru_w3_p_pos_col_q,
                            fexx=fexx_w5_q,
                            weld_size=t_w5_q,
                            weld_length=l_w5_col_q,
                            weld_lines=nl_w5_col,
                            unit_system=unit_system_w5,
                            kds=kds_w5_col,
                            phi=phi_fragil,
                        )
                        base_cap = weld_check_w5.get("phi_rn")
                        if isinstance(base_cap, Quantity):
                            phi_rn_w3_p_pos_col_q = Quantity(
                                value=base_cap.value * n_pc_val,
                                unit=base_cap.unit,
                            )
                    except Exception:
                        phi_rn_w3_p_pos_col_q = None
                if isinstance(ru_w3_p_pos_col_q, Quantity) and isinstance(phi_rn_w3_p_pos_col_q, Quantity) and phi_rn_w3_p_pos_col_q.value > 0:
                    phi_rn_conv = phi_rn_w3_p_pos_col_q
                    if phi_rn_w3_p_pos_col_q.unit != ru_w3_p_pos_col_q.unit:
                        if phi_rn_w3_p_pos_col_q.unit == "kN" and ru_w3_p_pos_col_q.unit == "kip":
                            phi_rn_conv = Quantity(value=phi_rn_w3_p_pos_col_q.value / 4.4482216152605, unit="kip")
                        elif phi_rn_w3_p_pos_col_q.unit == "kip" and ru_w3_p_pos_col_q.unit == "kN":
                            phi_rn_conv = Quantity(value=phi_rn_w3_p_pos_col_q.value * 4.4482216152605, unit="kN")
                    if phi_rn_conv.value > 0:
                        dcr_w3_p_pos_col = ru_w3_p_pos_col_q.value / phi_rn_conv.value
                        result_w3_p_pos_col = "Cumple" if dcr_w3_p_pos_col <= 1.0 else "No cumple"
                elif isinstance(ru_w3_p_pos_col_q, Quantity):
                    result_w3_p_pos_col = "No cumple"
            elif tipo_w5_norm == "cjp":
                result_w3_p_pos_col = "Cumple"

            block_25_lines = [
                f"## Paso {assigned_step_number}- Revisión de resistencia de soldadura # 5 ( Platina de continuidad con aleta de columna)",
                "",
                f"### {assigned_step_number}.1. Revisión de capacidad a tracción",
                "",
                f"#### {assigned_step_number}.1.1. ELR #1: Rotura de soldadura",
                "",
                "- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`",
                "- Ecuacion: `Ru_w5_p+_col = Fy_pc_col * b2_pc_col * t_pc_col * n_pc_col; Fillet: phi*Rn_w5_p+_col = phi_fragil * kds_w5_col * nl_w5_col * 0.6 * Fexx_w5_col * 0.707 * L_w5_col * w_w5_col * n_pc_col; DCR_w5_p+_col = Ru_w5_p+_col / phi*Rn_w5_p+_col`",
                f"- tipo_w5_col: `{tipo_w5_raw}`",
            ]
            if tipo_w5_norm == "cjp":
                block_25_lines.extend(
                    [
                        "- CJP: `Cumple`",
                        f"- Resultado: `{_render_result_plain_es(result_w3_p_pos_col)}`",
                        "",
                    ]
                )
            else:
                block_25_lines.extend(
                    [
                        f"- phi usado (phi_fragil): `{_format_decimal(phi_fragil)}`",
                        f"- Fy_pc_col: `{_format_quantity(fy_pc_col_q.model_dump() if isinstance(fy_pc_col_q, Quantity) else None)}`",
                        f"- b2_pc_col: `{_format_quantity(b2_pc_q.model_dump() if isinstance(b2_pc_q, Quantity) else None)}`",
                        f"- t_pc_col: `{_format_quantity(t_pc_q.model_dump() if isinstance(t_pc_q, Quantity) else None)}`",
                        f"- n_pc_col: `{_format_text(n_pc_val)}`",
                        f"- Ru_w5_p+_col: `{_format_quantity(ru_w3_p_pos_col_q.model_dump() if isinstance(ru_w3_p_pos_col_q, Quantity) else None)}`",
                        f"- Fexx_w5_col: `{_format_quantity(fexx_w5_q.model_dump() if isinstance(fexx_w5_q, Quantity) else None)}`",
                        f"- w_w5_col: `{_format_quantity(t_w5_q.model_dump() if isinstance(t_w5_q, Quantity) else None)}`",
                        f"- L_w5_col: `{_format_quantity(l_w5_col_q.model_dump() if isinstance(l_w5_col_q, Quantity) else None)}`",
                        f"- nl_w5_col: `{_format_text(nl_w5_col)}`",
                        f"- kds_w5_col: `{_format_text(kds_w5_col)}`",
                        f"- phi*Rn_w5_p+_col: `{_format_quantity(phi_rn_w3_p_pos_col_q.model_dump() if isinstance(phi_rn_w3_p_pos_col_q, Quantity) else None)}`",
                        f"- DCR_w5_p+_col: `{_format_decimal(dcr_w3_p_pos_col) if dcr_w3_p_pos_col is not None else 'n/a'}`",
                        f"- Resultado: `{_render_result_plain_es(result_w3_p_pos_col)}`",
                        "",
                    ]
                )

            block_25 = "\n".join(block_25_lines)
            block_25 = _align_nested_heading_numbers_with_step(block_25, step_number=assigned_step_number)
            content.append(block_25)
            next_step_number += 1

            # Paso 26 - Soldadura #6 (platina de continuidad con alma de columna)
            assigned_step_number = next_step_number
            tipo_w6_raw = _format_text(step1.get("tipo_w6_col"))
            tipo_w6_norm = tipo_w6_raw.strip().lower()
            if tipo_w6_norm in {"complete_joint_penetration"}:
                tipo_w6_norm = "cjp"
            elif tipo_w6_norm in {"single_sided_fillet", "double_sided_fillet"}:
                tipo_w6_norm = "fillet"

            l2_pc_col_q = _as_quantity(step1.get("L2_pc_col"))
            l_w6_col_q = _as_quantity(step1.get("L_w6_col")) or _as_quantity(step1.get("l_w6_col"))
            if not isinstance(l_w6_col_q, Quantity):
                l_gap_w6_q = _as_quantity(step1.get("L_gap_w6_col"))
                if isinstance(l2_pc_col_q, Quantity) and isinstance(l_gap_w6_q, Quantity):
                    if l_gap_w6_q.unit == l2_pc_col_q.unit:
                        l_gap_v = l_gap_w6_q.value
                    elif l_gap_w6_q.unit == "mm" and l2_pc_col_q.unit == "in":
                        l_gap_v = l_gap_w6_q.value / 25.4
                    elif l_gap_w6_q.unit == "in" and l2_pc_col_q.unit == "mm":
                        l_gap_v = l_gap_w6_q.value * 25.4
                    else:
                        l_gap_v = None
                    if l_gap_v is not None:
                        l_w6_col_q = Quantity(
                            value=l2_pc_col_q.value - 2.0 * l_gap_v,
                            unit=l2_pc_col_q.unit,
                        )
            fexx_w6_q = _as_quantity(step1.get("Fexx_w6_col")) or _as_quantity(step1.get("weld_fexx"))
            t_w6_q = _as_quantity(step1.get("w_w6_col")) or _as_quantity(step1.get("t_w6_col"))
            fy_pc_col_w6_q: Quantity | None = None
            fu_pc_col_w6_q: Quantity | None = None
            ru1_w5_v2_col_q: Quantity | None = None
            ru2_w5_v2_col_q: Quantity | None = None
            ru3_w5_v2_col_q: Quantity | None = None
            ru4_w5_v2_col_q: Quantity | None = None
            ru5_w5_v2_col_q: Quantity | None = None
            ru6_w5_v2_col_q: Quantity | None = None
            ru7_w5_v2_col_q: Quantity | None = None
            ru8_w5_v2_col_q: Quantity | None = None
            ru9_w5_v2_col_q: Quantity | None = None
            ru_w5_v2_col_q: Quantity | None = None
            cv1_col: float | None = None
            phi_rn_w6_p_pos_col_q: Quantity | None = None
            dcr_w6_p_pos_col: float | None = None
            result_w6_p_pos_col = "n/a"
            nl_w6_col = None
            try:
                if step1.get("nl_w6_col") is not None:
                    nl_w6_col = int(step1.get("nl_w6_col"))
            except (TypeError, ValueError):
                nl_w6_col = None
            kds_w6_col = None
            try:
                if step1.get("kds_w6_col") is not None:
                    kds_w6_col = float(step1.get("kds_w6_col"))
            except (TypeError, ValueError):
                kds_w6_col = None

            unit_system_w6: UnitSystem | None = None
            if isinstance(l2_pc_col_q, Quantity):
                unit_system_w6 = _infer_unit_system_from_quantity(l2_pc_col_q.model_dump())
            elif isinstance(t_pc_q, Quantity):
                unit_system_w6 = _infer_unit_system_from_quantity(t_pc_q.model_dump())

            if steel_type_pc != "n/a" and unit_system_w6 is not None:
                try:
                    pc_props = get_plate_steel_properties(
                        steel_type=steel_type_pc,
                        unit_system=unit_system_w6,
                    )
                    fy_pc_col_w6_q = pc_props.get("fy") if isinstance(pc_props.get("fy"), Quantity) else None
                    fu_pc_col_w6_q = pc_props.get("fu") if isinstance(pc_props.get("fu"), Quantity) else None
                except Exception:
                    fy_pc_col_w6_q = None
                    fu_pc_col_w6_q = None

            if (
                isinstance(fy_pc_col_w6_q, Quantity)
                and isinstance(l2_pc_col_q, Quantity)
                and isinstance(t_pc_q, Quantity)
                and l2_pc_col_q.unit == t_pc_q.unit
                and unit_system_w6 is not None
            ):
                if unit_system_w6 == UnitSystem.SI and fy_pc_col_w6_q.unit == "MPa" and l2_pc_col_q.unit == "mm":
                    ru1_w5_v2_col_q = Quantity(
                        value=(0.6 * fy_pc_col_w6_q.value * l2_pc_col_q.value * t_pc_q.value) / 1000.0,
                        unit="kN",
                    )
                elif unit_system_w6 == UnitSystem.US and fy_pc_col_w6_q.unit == "ksi" and l2_pc_col_q.unit == "in":
                    ru1_w5_v2_col_q = Quantity(
                        value=0.6 * fy_pc_col_w6_q.value * l2_pc_col_q.value * t_pc_q.value,
                        unit="kip",
                    )

            d_col_q = _as_quantity(step1.get("d_col"))
            tw_col_q_local = _as_quantity(step1.get("tw_col"))
            wz_dp_col_q = _as_quantity(step1.get("wz_dp_col"))
            kdes_col_q = _as_quantity(step1.get("kdes_col") or step1.get("kdet_col"))
            e_col_q = _as_quantity(step1.get("elastic_modulus"))
            if e_col_q is None:
                e_col_q = _as_quantity(step1.get("E_col"))
            phi_no_ductil = 0.9
            try:
                if step1.get("phi_no_ductil") is not None:
                    phi_no_ductil = float(step1.get("phi_no_ductil"))
            except (TypeError, ValueError):
                phi_no_ductil = 0.9
            t_dp_col_q = _as_quantity(step1.get("t_dp_col"))
            tipo_acero_dp_col = _format_text(step1.get("tipo_acero_dp_col"))
            tipo_acero_perfil_col = _format_text(step1.get("tipo_acero_perfil_col"))
            fy_dp_col_q: Quantity | None = None
            fu_dp_col_q: Quantity | None = None
            fy_col_q: Quantity | None = None
            fu_col_q: Quantity | None = None
            if unit_system_w6 is not None:
                if tipo_acero_dp_col != "n/a":
                    try:
                        dp_props = get_plate_steel_properties(
                            steel_type=tipo_acero_dp_col,
                            unit_system=unit_system_w6,
                        )
                        fy_dp_col_q = dp_props.get("fy") if isinstance(dp_props.get("fy"), Quantity) else None
                        fu_dp_col_q = dp_props.get("fu") if isinstance(dp_props.get("fu"), Quantity) else None
                    except Exception:
                        fy_dp_col_q = None
                        fu_dp_col_q = None
                if tipo_acero_perfil_col != "n/a":
                    try:
                        col_props = get_hrs_steel_properties(
                            steel_type=tipo_acero_perfil_col,
                            unit_system=unit_system_w6,
                        )
                        fy_col_q = col_props.get("fy") if isinstance(col_props.get("fy"), Quantity) else None
                        fu_col_q = col_props.get("fu") if isinstance(col_props.get("fu"), Quantity) else None
                    except Exception:
                        fy_col_q = None
                        fu_col_q = None

            def _ru_strength(
                *,
                stress_q: Quantity | None,
                thickness_q: Quantity | None,
                length_q: Quantity | None,
                unit_system: UnitSystem | None,
                factor: float = 0.6,
                extra_factor: float = 1.0,
            ) -> Quantity | None:
                if (
                    unit_system is None
                    or not isinstance(stress_q, Quantity)
                    or not isinstance(thickness_q, Quantity)
                    or not isinstance(length_q, Quantity)
                ):
                    return None
                if thickness_q.unit != length_q.unit:
                    if thickness_q.unit == "mm" and length_q.unit == "in":
                        t_conv = Quantity(value=thickness_q.value / 25.4, unit="in")
                    elif thickness_q.unit == "in" and length_q.unit == "mm":
                        t_conv = Quantity(value=thickness_q.value * 25.4, unit="mm")
                    else:
                        return None
                else:
                    t_conv = thickness_q
                if unit_system == UnitSystem.SI and stress_q.unit == "MPa" and t_conv.unit == "mm":
                    return Quantity(
                        value=factor * stress_q.value * t_conv.value * length_q.value * extra_factor / 1000.0,
                        unit="kN",
                    )
                if unit_system == UnitSystem.US and stress_q.unit == "ksi" and t_conv.unit == "in":
                    return Quantity(
                        value=factor * stress_q.value * t_conv.value * length_q.value * extra_factor,
                        unit="kip",
                    )
                return None

            # Ru2..Ru9 solicitados para 26.1.1
            ru2_w5_v2_col_q = _ru_strength(
                stress_q=fu_dp_col_q,
                thickness_q=t_dp_col_q,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )
            ru3_w5_v2_col_q = _ru_strength(
                stress_q=fy_dp_col_q,
                thickness_q=t_dp_col_q,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )
            ru4_w5_v2_col_q = _ru_strength(
                stress_q=fu_col_q,
                thickness_q=tw_col_q_local,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )
            ru5_w5_v2_col_q = _ru_strength(
                stress_q=fy_col_q,
                thickness_q=tw_col_q_local,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )
            ru6_w5_v2_col_q = _ru_strength(
                stress_q=fu_col_q,
                thickness_q=tw_col_q_local,
                length_q=d_col_q,
                unit_system=unit_system_w6,
            )
            if (
                isinstance(fy_col_q, Quantity)
                and isinstance(tw_col_q_local, Quantity)
                and isinstance(d_col_q, Quantity)
                and isinstance(kdes_col_q, Quantity)
                and isinstance(e_col_q, Quantity)
                and unit_system_w6 is not None
            ):
                try:
                    shear_col = compute_beam_web_shear_yielding_strength(
                        fy=fy_col_q,
                        tw=tw_col_q_local,
                        d=d_col_q,
                        kdes=kdes_col_q,
                        elastic_modulus=e_col_q,
                        unit_system=unit_system_w6,
                        phi=1.0,
                    )
                    cv1_col = float(shear_col.get("cv1")) if shear_col.get("cv1") is not None else None
                except Exception:
                    cv1_col = None
            ru7_w5_v2_col_q = _ru_strength(
                stress_q=fy_col_q,
                thickness_q=tw_col_q_local,
                length_q=d_col_q,
                unit_system=unit_system_w6,
                extra_factor=(cv1_col if cv1_col is not None else 1.0),
            ) if cv1_col is not None else None
            ru8_w5_v2_col_q = _ru_strength(
                stress_q=fu_dp_col_q,
                thickness_q=t_dp_col_q,
                length_q=wz_dp_col_q,
                unit_system=unit_system_w6,
            )
            ru9_w5_v2_col_q = _ru_strength(
                stress_q=fy_dp_col_q,
                thickness_q=t_dp_col_q,
                length_q=wz_dp_col_q,
                unit_system=unit_system_w6,
            )

            ru_candidates: list[Quantity] = []
            for q in (
                ru1_w5_v2_col_q,
                ru2_w5_v2_col_q,
                ru3_w5_v2_col_q,
                ru4_w5_v2_col_q,
                ru5_w5_v2_col_q,
                ru6_w5_v2_col_q,
                ru7_w5_v2_col_q,
                ru8_w5_v2_col_q,
                ru9_w5_v2_col_q,
            ):
                if isinstance(q, Quantity):
                    ru_candidates.append(q)
            if ru_candidates:
                base_unit = ru_candidates[0].unit
                converted_ru: list[Quantity] = []
                for q in ru_candidates:
                    if q.unit == base_unit:
                        converted_ru.append(q)
                    elif q.unit == "kN" and base_unit == "kip":
                        converted_ru.append(Quantity(value=q.value / 4.4482216152605, unit="kip"))
                    elif q.unit == "kip" and base_unit == "kN":
                        converted_ru.append(Quantity(value=q.value * 4.4482216152605, unit="kN"))
                if converted_ru:
                    ru_w5_v2_col_q = min(converted_ru, key=lambda x: x.value)

            if tipo_w6_norm == "fillet":
                if (
                    isinstance(ru_w5_v2_col_q, Quantity)
                    and isinstance(fexx_w6_q, Quantity)
                    and isinstance(t_w6_q, Quantity)
                    and isinstance(l_w6_col_q, Quantity)
                    and nl_w6_col is not None
                    and kds_w6_col is not None
                    and unit_system_w6 is not None
                ):
                    try:
                        weld_check_w6 = compute_fillet_weld_check_with_kds(
                            demand=ru_w5_v2_col_q,
                            fexx=fexx_w6_q,
                            weld_size=t_w6_q,
                            weld_length=l_w6_col_q,
                            weld_lines=nl_w6_col,
                            unit_system=unit_system_w6,
                            kds=kds_w6_col,
                            phi=phi_fragil,
                        )
                        base_cap_w6 = weld_check_w6.get("phi_rn")
                        if isinstance(base_cap_w6, Quantity):
                            phi_rn_w6_p_pos_col_q = base_cap_w6
                    except Exception:
                        phi_rn_w6_p_pos_col_q = None
                if (
                    isinstance(ru_w5_v2_col_q, Quantity)
                    and isinstance(phi_rn_w6_p_pos_col_q, Quantity)
                    and phi_rn_w6_p_pos_col_q.value > 0
                ):
                    phi_rn_conv_w6 = phi_rn_w6_p_pos_col_q
                    if phi_rn_w6_p_pos_col_q.unit != ru_w5_v2_col_q.unit:
                        if phi_rn_w6_p_pos_col_q.unit == "kN" and ru_w5_v2_col_q.unit == "kip":
                            phi_rn_conv_w6 = Quantity(value=phi_rn_w6_p_pos_col_q.value / 4.4482216152605, unit="kip")
                        elif phi_rn_w6_p_pos_col_q.unit == "kip" and ru_w5_v2_col_q.unit == "kN":
                            phi_rn_conv_w6 = Quantity(value=phi_rn_w6_p_pos_col_q.value * 4.4482216152605, unit="kN")
                    if phi_rn_conv_w6.value > 0:
                        dcr_w6_p_pos_col = ru_w5_v2_col_q.value / phi_rn_conv_w6.value
                        result_w6_p_pos_col = "Cumple" if dcr_w6_p_pos_col <= 1.0 else "No cumple"
                elif isinstance(ru_w5_v2_col_q, Quantity):
                    result_w6_p_pos_col = "No cumple"
            elif tipo_w6_norm == "cjp":
                result_w6_p_pos_col = "Cumple"

            # ELR adicional 26.6.2 - Rotura del material base

            def _phi_rn_base_metal(
                *,
                phi: float,
                stress_q: Quantity | None,
                thickness_q: Quantity | None,
                length_q: Quantity | None,
                unit_system: UnitSystem | None,
            ) -> Quantity | None:
                if (
                    unit_system is None
                    or not isinstance(stress_q, Quantity)
                    or not isinstance(thickness_q, Quantity)
                    or not isinstance(length_q, Quantity)
                ):
                    return None
                if thickness_q.unit != length_q.unit:
                    if thickness_q.unit == "mm" and length_q.unit == "in":
                        t_conv = Quantity(value=thickness_q.value / 25.4, unit="in")
                    elif thickness_q.unit == "in" and length_q.unit == "mm":
                        t_conv = Quantity(value=thickness_q.value * 25.4, unit="mm")
                    else:
                        return None
                else:
                    t_conv = thickness_q
                if unit_system == UnitSystem.SI and stress_q.unit == "MPa" and t_conv.unit == "mm":
                    return Quantity(
                        value=phi * 0.6 * stress_q.value * t_conv.value * length_q.value / 1000.0,
                        unit="kN",
                    )
                if unit_system == UnitSystem.US and stress_q.unit == "ksi" and t_conv.unit == "in":
                    return Quantity(
                        value=phi * 0.6 * stress_q.value * t_conv.value * length_q.value,
                        unit="kip",
                    )
                return None

            phi_rn1_w6_dp_v2_col_q = _phi_rn_base_metal(
                phi=phi_fragil,
                stress_q=fu_dp_col_q,
                thickness_q=t_dp_col_q,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )
            phi_rn2_w6_dp_v2_col_q = _phi_rn_base_metal(
                phi=phi_no_ductil,
                stress_q=fy_dp_col_q,
                thickness_q=t_dp_col_q,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )
            phi_rn1_w6_cw_v2_col_q = _phi_rn_base_metal(
                phi=phi_fragil,
                stress_q=fu_col_q,
                thickness_q=tw_col_q_local,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )
            phi_rn2_w6_cw_v2_col_q = _phi_rn_base_metal(
                phi=phi_no_ductil,
                stress_q=fy_col_q,
                thickness_q=tw_col_q_local,
                length_q=l_w6_col_q,
                unit_system=unit_system_w6,
            )

            phi_rn_candidates: list[Quantity] = []
            for q in (
                phi_rn1_w6_dp_v2_col_q,
                phi_rn2_w6_dp_v2_col_q,
                phi_rn1_w6_cw_v2_col_q,
                phi_rn2_w6_cw_v2_col_q,
            ):
                if isinstance(q, Quantity):
                    phi_rn_candidates.append(q)

            phi_rn_w6_v2_col_base_q: Quantity | None = None
            if phi_rn_candidates:
                base_unit = phi_rn_candidates[0].unit
                converted: list[Quantity] = []
                for q in phi_rn_candidates:
                    if q.unit == base_unit:
                        converted.append(q)
                    elif q.unit == "kN" and base_unit == "kip":
                        converted.append(Quantity(value=q.value / 4.4482216152605, unit="kip"))
                    elif q.unit == "kip" and base_unit == "kN":
                        converted.append(Quantity(value=q.value * 4.4482216152605, unit="kN"))
                if converted:
                    phi_rn_w6_v2_col_base_q = min(converted, key=lambda x: x.value)

            dcr_w6_v2_col_base: float | None = None
            result_w6_v2_col_base = "n/a"
            if isinstance(ru_w5_v2_col_q, Quantity) and isinstance(phi_rn_w6_v2_col_base_q, Quantity):
                phi_rn_conv = phi_rn_w6_v2_col_base_q
                if phi_rn_w6_v2_col_base_q.unit != ru_w5_v2_col_q.unit:
                    if phi_rn_w6_v2_col_base_q.unit == "kN" and ru_w5_v2_col_q.unit == "kip":
                        phi_rn_conv = Quantity(value=phi_rn_w6_v2_col_base_q.value / 4.4482216152605, unit="kip")
                    elif phi_rn_w6_v2_col_base_q.unit == "kip" and ru_w5_v2_col_q.unit == "kN":
                        phi_rn_conv = Quantity(value=phi_rn_w6_v2_col_base_q.value * 4.4482216152605, unit="kN")
                if phi_rn_conv.value > 0:
                    dcr_w6_v2_col_base = ru_w5_v2_col_q.value / phi_rn_conv.value
                    result_w6_v2_col_base = "Cumple" if dcr_w6_v2_col_base <= 1.0 else "No cumple"

            block_26_lines = [
                f"## Paso {assigned_step_number}- Revisión de resistencia de soldadura # 6 ( Platina de continuidad con alma de columna)",
                "",
                f"### {assigned_step_number}.1. Revisión de capacidad a cortante",
                "",
                f"#### {assigned_step_number}.1.1. ELR #1: Rotura de soldadura",
                "",
                "- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`",
                "- Ecuacion: `Ru1_w5_v2_col = 0.6 * Fy_pc_col * L2_pc_col * t_pc_col; Ru2_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * L_w6_col; Ru3_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * L_w6_col; Ru4_w5_v2_col = 0.6 * fu_col * tw_col * L_w6_col; Ru5_w5_v2_col = 0.6 * fy_col * tw_col * L_w6_col; Ru6_w5_v2_col = 0.6 * fu_col * tw_col * d_col; Ru7_w5_v2_col = 0.6 * fy_col * tw_col * d_col * Cv1; Ru8_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * wz_dp_col; Ru9_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * wz_dp_col; Ru_w5_v2_col = MIN{Ru1..Ru9}; Fillet: phi*Rn_w6_v2_col = phi_fragil * kds_w6_col * nl_w6_col * 0.6 * Fexx_w6_col * 0.707 * L_w6_col * w_w6_col; DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`",
                f"- tipo_w6_col: `{tipo_w6_raw}`",
            ]
            if tipo_w6_norm == "cjp":
                block_26_lines.extend(
                    [
                        "- CJP: `Cumple`",
                        f"- Resultado: `{_render_result_plain_es(result_w6_p_pos_col)}`",
                        "",
                    ]
                )
            else:
                block_26_lines.extend(
                    [
                        f"- phi usado (phi_fragil): `{_format_decimal(phi_fragil)}`",
                        f"- Fy_pc_col: `{_format_quantity(fy_pc_col_w6_q.model_dump() if isinstance(fy_pc_col_w6_q, Quantity) else None)}`",
                        f"- Fu_pc_col: `{_format_quantity(fu_pc_col_w6_q.model_dump() if isinstance(fu_pc_col_w6_q, Quantity) else None)}`",
                        f"- L2_pc_col: `{_format_quantity(l2_pc_col_q.model_dump() if isinstance(l2_pc_col_q, Quantity) else None)}`",
                        f"- t_pc_col: `{_format_quantity(t_pc_q.model_dump() if isinstance(t_pc_q, Quantity) else None)}`",
                        f"- Fu_dp_col: `{_format_quantity(fu_dp_col_q.model_dump() if isinstance(fu_dp_col_q, Quantity) else None)}`",
                        f"- Fy_dp_col: `{_format_quantity(fy_dp_col_q.model_dump() if isinstance(fy_dp_col_q, Quantity) else None)}`",
                        f"- t_dp_col: `{_format_quantity(t_dp_col_q.model_dump() if isinstance(t_dp_col_q, Quantity) else None)}`",
                        f"- Fu_col: `{_format_quantity(fu_col_q.model_dump() if isinstance(fu_col_q, Quantity) else None)}`",
                        f"- Fy_col: `{_format_quantity(fy_col_q.model_dump() if isinstance(fy_col_q, Quantity) else None)}`",
                        f"- tw_col: `{_format_quantity(tw_col_q_local.model_dump() if isinstance(tw_col_q_local, Quantity) else None)}`",
                        f"- d_col: `{_format_quantity(d_col_q.model_dump() if isinstance(d_col_q, Quantity) else None)}`",
                        f"- wz_dp_col: `{_format_quantity(wz_dp_col_q.model_dump() if isinstance(wz_dp_col_q, Quantity) else None)}`",
                        f"- Cv1: `{_format_decimal(cv1_col) if cv1_col is not None else 'n/a'}`",
                        f"- Ru1_w5_v2_col: `{_format_quantity(ru1_w5_v2_col_q.model_dump() if isinstance(ru1_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru2_w5_v2_col: `{_format_quantity(ru2_w5_v2_col_q.model_dump() if isinstance(ru2_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru3_w5_v2_col: `{_format_quantity(ru3_w5_v2_col_q.model_dump() if isinstance(ru3_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru4_w5_v2_col: `{_format_quantity(ru4_w5_v2_col_q.model_dump() if isinstance(ru4_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru5_w5_v2_col: `{_format_quantity(ru5_w5_v2_col_q.model_dump() if isinstance(ru5_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru6_w5_v2_col: `{_format_quantity(ru6_w5_v2_col_q.model_dump() if isinstance(ru6_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru7_w5_v2_col: `{_format_quantity(ru7_w5_v2_col_q.model_dump() if isinstance(ru7_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru8_w5_v2_col: `{_format_quantity(ru8_w5_v2_col_q.model_dump() if isinstance(ru8_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru9_w5_v2_col: `{_format_quantity(ru9_w5_v2_col_q.model_dump() if isinstance(ru9_w5_v2_col_q, Quantity) else None)}`",
                        f"- Ru_w5_v2_col: `{_format_quantity(ru_w5_v2_col_q.model_dump() if isinstance(ru_w5_v2_col_q, Quantity) else None)}`",
                        f"- Fexx_w6_col: `{_format_quantity(fexx_w6_q.model_dump() if isinstance(fexx_w6_q, Quantity) else None)}`",
                        f"- w_w6_col: `{_format_quantity(t_w6_q.model_dump() if isinstance(t_w6_q, Quantity) else None)}`",
                        f"- L_w6_col: `{_format_quantity(l_w6_col_q.model_dump() if isinstance(l_w6_col_q, Quantity) else None)}`",
                        f"- nl_w6_col: `{_format_text(nl_w6_col)}`",
                        f"- kds_w6_col: `{_format_text(kds_w6_col)}`",
                        f"- phi*Rn_w6_v2_col: `{_format_quantity(phi_rn_w6_p_pos_col_q.model_dump() if isinstance(phi_rn_w6_p_pos_col_q, Quantity) else None)}`",
                        f"- DCR_w6_v2_col: `{_format_decimal(dcr_w6_p_pos_col) if dcr_w6_p_pos_col is not None else 'n/a'}`",
                        f"- Resultado: `{_render_result_plain_es(result_w6_p_pos_col)}`",
                        "",
                    ]
                )
            block_26_lines.extend(
                [
                    f"### {assigned_step_number}.6. Revisión de capacidad del material base",
                    "",
                    f"#### {assigned_step_number}.6.2. ELR #1: Rotura del material base",
                    "",
                    "- Clausula: `AISC 360-22 J4 (material base)`",
                    "- Ecuacion: `Ru_w5_v2_col = MIN{Ru1..Ru9}; phi*Rn1_w6-dp_v2_col = phi_fragil * 0.6 * fu_dp_col * t_dp_col * L_w6_col; phi*Rn2_w6-dp_v2_col = phi_no_ductil * 0.6 * fy_dp_col * t_dp_col * L_w6_col; phi*Rn1_w6-cw_v2_col = phi_fragil * 0.6 * fu_col * tw_col * L_w6_col; phi*Rn2_w6-cw_v2_col = phi_no_ductil * 0.6 * fy_col * tw_col * L_w6_col; phi*Rn_w6_v2_col = min(phi*Rn1_w6-dp_v2_col, phi*Rn2_w6-dp_v2_col, phi*Rn1_w6-cw_v2_col, phi*Rn2_w6-cw_v2_col); DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`",
                ]
            )
            if tipo_w6_norm == "cjp":
                block_26_lines.extend(
                    [
                        f"- tipo_w6_col: `{tipo_w6_raw}`",
                        "- CJP: `Cumple`",
                        "- Resultado: `🟢 Cumple`",
                        "",
                    ]
                )
            else:
                block_26_lines.extend(
                    [
                        f"- phi fragil: `{_format_decimal(phi_fragil)}`",
                        f"- phi no ductil: `{_format_decimal(phi_no_ductil)}`",
                        f"- fu_dp_col: `{_format_quantity(fu_dp_col_q.model_dump() if isinstance(fu_dp_col_q, Quantity) else None)}`",
                        f"- fy_dp_col: `{_format_quantity(fy_dp_col_q.model_dump() if isinstance(fy_dp_col_q, Quantity) else None)}`",
                        f"- t_dp_col: `{_format_quantity(t_dp_col_q.model_dump() if isinstance(t_dp_col_q, Quantity) else None)}`",
                        f"- fu_col: `{_format_quantity(fu_col_q.model_dump() if isinstance(fu_col_q, Quantity) else None)}`",
                        f"- fy_col: `{_format_quantity(fy_col_q.model_dump() if isinstance(fy_col_q, Quantity) else None)}`",
                        f"- tw_col: `{_format_quantity(tw_col_q_local.model_dump() if isinstance(tw_col_q_local, Quantity) else None)}`",
                        f"- L_w6_col: `{_format_quantity(l_w6_col_q.model_dump() if isinstance(l_w6_col_q, Quantity) else None)}`",
                        f"- Ru_w5_v2_col: `{_format_quantity(ru_w5_v2_col_q.model_dump() if isinstance(ru_w5_v2_col_q, Quantity) else None)}`",
                        f"- phi*Rn1_w6-dp_v2_col: `{_format_quantity(phi_rn1_w6_dp_v2_col_q.model_dump() if isinstance(phi_rn1_w6_dp_v2_col_q, Quantity) else None)}`",
                        f"- phi*Rn2_w6-dp_v2_col: `{_format_quantity(phi_rn2_w6_dp_v2_col_q.model_dump() if isinstance(phi_rn2_w6_dp_v2_col_q, Quantity) else None)}`",
                        f"- phi*Rn1_w6-cw_v2_col: `{_format_quantity(phi_rn1_w6_cw_v2_col_q.model_dump() if isinstance(phi_rn1_w6_cw_v2_col_q, Quantity) else None)}`",
                        f"- phi*Rn2_w6-cw_v2_col: `{_format_quantity(phi_rn2_w6_cw_v2_col_q.model_dump() if isinstance(phi_rn2_w6_cw_v2_col_q, Quantity) else None)}`",
                        f"- phi*Rn_w6_v2_col: `{_format_quantity(phi_rn_w6_v2_col_base_q.model_dump() if isinstance(phi_rn_w6_v2_col_base_q, Quantity) else None)}`",
                        f"- DCR_w6_v2_col: `{_format_decimal(dcr_w6_v2_col_base) if dcr_w6_v2_col_base is not None else 'n/a'}`",
                        f"- Resultado: `{_render_result_plain_es(result_w6_v2_col_base)}`",
                        "",
                    ]
                )
            block_26 = "\n".join(block_26_lines)
            block_26 = _align_nested_heading_numbers_with_step(block_26, step_number=assigned_step_number)
            content.append(block_26)
            next_step_number += 1

            # Paso 27 - Soldadura #8 (platina de enchape con aleta de columna)
            assigned_step_number = next_step_number
            tipo_w8_raw = _format_text(step1.get("tipo_w8_col"))
            tipo_w8_norm = tipo_w8_raw.strip().lower()
            if tipo_w8_norm in {"complete_joint_penetration"}:
                tipo_w8_norm = "cjp"
            elif tipo_w8_norm in {"single_sided_fillet", "double_sided_fillet"}:
                tipo_w8_norm = "fillet"
            elif tipo_w8_norm in {"partial_joint_penetration"}:
                tipo_w8_norm = "pjp"

            n_dp_col_val = 1.0
            try:
                if step1.get("n_dp_col") is not None:
                    n_dp_col_val = float(step1.get("n_dp_col"))
            except (TypeError, ValueError):
                n_dp_col_val = 1.0

            h_dp_col_q = _as_quantity(step1.get("h_dp_col"))
            b_dp_col_q = _as_quantity(step1.get("b_dp_col"))
            t_dp_col_q_w8 = _as_quantity(step1.get("t_dp_col"))
            tw_col_q_w8 = _as_quantity(step1.get("tw_col"))
            fy_dp_col_q_w8 = fy_dp_col_q if isinstance(fy_dp_col_q, Quantity) else None
            fexx_w8_q = _as_quantity(step1.get("Fexx_w8_col"))
            w_w8_q = _as_quantity(step1.get("w_w8_col")) or _as_quantity(step1.get("t_w8_col"))
            l_gap_w8_col_q = _as_quantity(step1.get("L_gap_w8_col"))
            nl_w8_col = None
            try:
                if step1.get("nl_w8_col") is not None:
                    nl_w8_col = int(step1.get("nl_w8_col"))
            except (TypeError, ValueError):
                nl_w8_col = None
            kds_w8_col = None
            try:
                if step1.get("kds_w8_col") is not None:
                    kds_w8_col = float(step1.get("kds_w8_col"))
            except (TypeError, ValueError):
                kds_w8_col = None

            unit_system_w8 = unit_system_w6
            if unit_system_w8 is None:
                if isinstance(h_dp_col_q, Quantity):
                    unit_system_w8 = _infer_unit_system_from_quantity(h_dp_col_q.model_dump())
                elif isinstance(t_dp_col_q_w8, Quantity):
                    unit_system_w8 = _infer_unit_system_from_quantity(t_dp_col_q_w8.model_dump())

            ru1_w8_v2_col_q: Quantity | None = None
            if (
                isinstance(fy_dp_col_q_w8, Quantity)
                and isinstance(h_dp_col_q, Quantity)
                and isinstance(t_dp_col_q_w8, Quantity)
                and unit_system_w8 is not None
            ):
                if (
                    unit_system_w8 == UnitSystem.SI
                    and fy_dp_col_q_w8.unit == "MPa"
                    and h_dp_col_q.unit == "mm"
                    and t_dp_col_q_w8.unit == "mm"
                ):
                    ru1_w8_v2_col_q = Quantity(
                        value=(0.6 * fy_dp_col_q_w8.value * h_dp_col_q.value * t_dp_col_q_w8.value) / 1000.0,
                        unit="kN",
                    )
                elif (
                    unit_system_w8 == UnitSystem.US
                    and fy_dp_col_q_w8.unit == "ksi"
                    and h_dp_col_q.unit == "in"
                    and t_dp_col_q_w8.unit == "in"
                ):
                    ru1_w8_v2_col_q = Quantity(
                        value=0.6 * fy_dp_col_q_w8.value * h_dp_col_q.value * t_dp_col_q_w8.value,
                        unit="kip",
                    )

            wpz_inputs = (
                step_21_5_1_panel_zone.get("inputs", {})
                if isinstance(step_21_5_1_panel_zone, dict)
                else {}
            )
            mf_vgizq_max_q = _as_quantity(wpz_inputs.get("mf_vgizq_max"))
            mf_vgizq_min_q = _as_quantity(wpz_inputs.get("mf_vgizq_min"))
            mf_vgder_max_q = _as_quantity(wpz_inputs.get("mf_vgder_max"))
            mf_vgder_min_q = _as_quantity(wpz_inputs.get("mf_vgder_min"))

            ru2_w8_v2_col_q: Quantity | None = None
            combo1_q: Quantity | None = None
            combo2_q: Quantity | None = None
            combo_max_q: Quantity | None = None
            ratio_tdp_over_sum: float | None = None
            if (
                isinstance(mf_vgizq_max_q, Quantity)
                and isinstance(mf_vgder_min_q, Quantity)
                and isinstance(mf_vgder_max_q, Quantity)
                and isinstance(mf_vgizq_min_q, Quantity)
                and isinstance(t_dp_col_q_w8, Quantity)
                and isinstance(tw_col_q_w8, Quantity)
                and isinstance(b_dp_col_q, Quantity)
            ):
                target_m_unit = mf_vgizq_max_q.unit
                mf_vgder_min_conv = _convert_moment_to_unit(mf_vgder_min_q, target_m_unit)
                mf_vgder_max_conv = _convert_moment_to_unit(mf_vgder_max_q, target_m_unit)
                mf_vgizq_min_conv = _convert_moment_to_unit(mf_vgizq_min_q, target_m_unit)

                if (
                    isinstance(mf_vgder_min_conv, Quantity)
                    and isinstance(mf_vgder_max_conv, Quantity)
                    and isinstance(mf_vgizq_min_conv, Quantity)
                ):
                    combo1_q = Quantity(
                        value=mf_vgizq_max_q.value + mf_vgder_min_conv.value,
                        unit=target_m_unit,
                    )
                    combo2_q = Quantity(
                        value=mf_vgder_max_conv.value + mf_vgizq_min_conv.value,
                        unit=target_m_unit,
                    )
                    combo_max_q = combo1_q if combo1_q.value >= combo2_q.value else combo2_q

                    t_dp_for_ratio = t_dp_col_q_w8
                    if tw_col_q_w8.unit != t_dp_col_q_w8.unit:
                        if tw_col_q_w8.unit == "mm" and t_dp_col_q_w8.unit == "in":
                            tw_for_ratio = Quantity(value=tw_col_q_w8.value / 25.4, unit="in")
                        elif tw_col_q_w8.unit == "in" and t_dp_col_q_w8.unit == "mm":
                            tw_for_ratio = Quantity(value=tw_col_q_w8.value * 25.4, unit="mm")
                        else:
                            tw_for_ratio = None
                    else:
                        tw_for_ratio = tw_col_q_w8

                    if tw_for_ratio is not None:
                        denom_t = t_dp_for_ratio.value * n_dp_col_val + tw_for_ratio.value
                        if abs(denom_t) > 1e-12:
                            ratio_tdp_over_sum = t_dp_for_ratio.value / denom_t

                            b_for_div = b_dp_col_q
                            if b_for_div.unit == "mm" and target_m_unit == "kN-m":
                                b_for_div = Quantity(value=b_for_div.value / 1000.0, unit="m")
                            elif b_for_div.unit == "in" and target_m_unit == "kip-ft":
                                b_for_div = Quantity(value=b_for_div.value / 12.0, unit="ft")
                            elif b_for_div.unit == "mm" and target_m_unit == "kN-mm":
                                b_for_div = Quantity(value=b_for_div.value, unit="mm")
                            elif b_for_div.unit == "in" and target_m_unit == "kip-in":
                                b_for_div = Quantity(value=b_for_div.value, unit="in")
                            elif b_for_div.unit != "m" and target_m_unit == "kN-m":
                                b_for_div = None
                            elif b_for_div.unit != "ft" and target_m_unit == "kip-ft":
                                b_for_div = None

                            if isinstance(b_for_div, Quantity) and abs(b_for_div.value) > 1e-12:
                                if target_m_unit in {"kN-m", "kN-mm"}:
                                    ru2_w8_v2_col_q = Quantity(
                                        value=(combo_max_q.value * ratio_tdp_over_sum) / b_for_div.value,
                                        unit="kN",
                                    )
                                elif target_m_unit in {"kip-ft", "kip-in"}:
                                    ru2_w8_v2_col_q = Quantity(
                                        value=(combo_max_q.value * ratio_tdp_over_sum) / b_for_div.value,
                                        unit="kip",
                                    )

            ru_w8_v2_col_q: Quantity | None = None
            if isinstance(ru1_w8_v2_col_q, Quantity) and isinstance(ru2_w8_v2_col_q, Quantity):
                ru2_conv = ru2_w8_v2_col_q
                if ru2_w8_v2_col_q.unit != ru1_w8_v2_col_q.unit:
                    if ru2_w8_v2_col_q.unit == "kN" and ru1_w8_v2_col_q.unit == "kip":
                        ru2_conv = Quantity(value=ru2_w8_v2_col_q.value / 4.4482216152605, unit="kip")
                    elif ru2_w8_v2_col_q.unit == "kip" and ru1_w8_v2_col_q.unit == "kN":
                        ru2_conv = Quantity(value=ru2_w8_v2_col_q.value * 4.4482216152605, unit="kN")
                ru_w8_v2_col_q = ru1_w8_v2_col_q if ru1_w8_v2_col_q.value >= ru2_conv.value else ru2_conv
            elif isinstance(ru1_w8_v2_col_q, Quantity):
                ru_w8_v2_col_q = ru1_w8_v2_col_q
            elif isinstance(ru2_w8_v2_col_q, Quantity):
                ru_w8_v2_col_q = ru2_w8_v2_col_q

            l_w8_col_q: Quantity | None = None
            if isinstance(h_dp_col_q, Quantity) and isinstance(l_gap_w8_col_q, Quantity):
                gap_for_calc = l_gap_w8_col_q
                if l_gap_w8_col_q.unit != h_dp_col_q.unit:
                    if l_gap_w8_col_q.unit == "mm" and h_dp_col_q.unit == "in":
                        gap_for_calc = Quantity(value=l_gap_w8_col_q.value / 25.4, unit="in")
                    elif l_gap_w8_col_q.unit == "in" and h_dp_col_q.unit == "mm":
                        gap_for_calc = Quantity(value=l_gap_w8_col_q.value * 25.4, unit="mm")
                    else:
                        gap_for_calc = None
                if isinstance(gap_for_calc, Quantity):
                    l_w8_col_q = Quantity(
                        value=h_dp_col_q.value - 2.0 * gap_for_calc.value,
                        unit=h_dp_col_q.unit,
                    )

            phi_rn_w8_v2_col_q: Quantity | None = None
            dcr_w8_v2_col: float | None = None
            result_w8_v2_col = "n/a"
            if tipo_w8_norm == "fillet":
                if (
                    isinstance(ru_w8_v2_col_q, Quantity)
                    and isinstance(fexx_w8_q, Quantity)
                    and isinstance(w_w8_q, Quantity)
                    and isinstance(l_w8_col_q, Quantity)
                    and nl_w8_col is not None
                    and kds_w8_col is not None
                    and unit_system_w8 is not None
                ):
                    try:
                        weld_check_w8 = compute_fillet_weld_check_with_kds(
                            demand=ru_w8_v2_col_q,
                            fexx=fexx_w8_q,
                            weld_size=w_w8_q,
                            weld_length=l_w8_col_q,
                            weld_lines=nl_w8_col,
                            unit_system=unit_system_w8,
                            kds=kds_w8_col,
                            phi=phi_fragil,
                        )
                        base_cap_w8 = weld_check_w8.get("phi_rn")
                        if isinstance(base_cap_w8, Quantity):
                            phi_rn_w8_v2_col_q = base_cap_w8
                    except Exception:
                        phi_rn_w8_v2_col_q = None
                if (
                    isinstance(ru_w8_v2_col_q, Quantity)
                    and isinstance(phi_rn_w8_v2_col_q, Quantity)
                    and phi_rn_w8_v2_col_q.value > 0
                ):
                    phi_rn_conv_w8 = phi_rn_w8_v2_col_q
                    if phi_rn_w8_v2_col_q.unit != ru_w8_v2_col_q.unit:
                        if phi_rn_w8_v2_col_q.unit == "kN" and ru_w8_v2_col_q.unit == "kip":
                            phi_rn_conv_w8 = Quantity(value=phi_rn_w8_v2_col_q.value / 4.4482216152605, unit="kip")
                        elif phi_rn_w8_v2_col_q.unit == "kip" and ru_w8_v2_col_q.unit == "kN":
                            phi_rn_conv_w8 = Quantity(value=phi_rn_w8_v2_col_q.value * 4.4482216152605, unit="kN")
                    if phi_rn_conv_w8.value > 0:
                        dcr_w8_v2_col = ru_w8_v2_col_q.value / phi_rn_conv_w8.value
                        result_w8_v2_col = "Cumple" if dcr_w8_v2_col <= 1.0 else "No cumple"
                elif isinstance(ru_w8_v2_col_q, Quantity):
                    result_w8_v2_col = "No cumple"
            elif tipo_w8_norm == "cjp":
                result_w8_v2_col = "Cumple"
            elif tipo_w8_norm == "pjp":
                result_w8_v2_col = "Cumple"

            block_27_lines = [
                f"## Paso {assigned_step_number}- Revisión de resistencia de soldadura # 8 (Platina de enchape con aleta de columna)",
                "",
                f"### {assigned_step_number}.1. Revisión de capacidad a cortante",
                "",
                f"#### {assigned_step_number}.1.1. ELR #1: Rotura de soldadura",
                "",
                "- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`",
                "- Ecuacion: `Ru_w8_v2_col = max{Ru1_w8_v2_col, Ru2_w8_v2_col}; Ru1_w8_v2_col = 0.6 * Fy_dp_col * h_dp_col * t_dp_col; Ru2_w8_v2_col = max{Mf_vgizq_max + Mf_vgder_min, Mf_vgder_max + Mf_vgizq_min} * (t_dp_col/(t_dp_col*n_dp_col + tw_col)) / b_dp_col; Fillet: L_w8_col = h_dp_col - 2*L_gap_w8_col; phi*Rn_w8_v2_col = phi_fragil * kds_w8_col * nl_w8_col * 0.6 * Fexx_w8_col * 0.707 * L_w8_col * w_w8_col; DCR_w8_v2_col = Ru_w8_v2_col / phi*Rn_w8_v2_col`",
                f"- tipo_w8_col: `{tipo_w8_raw}`",
            ]
            if tipo_w8_norm == "cjp":
                block_27_lines.extend(
                    [
                        "- CJP: `Cumple`",
                        f"- Resultado: `{_render_result_plain_es(result_w8_v2_col)}`",
                        "",
                    ]
                )
            elif tipo_w8_norm == "pjp":
                block_27_lines.extend(
                    [
                        "- PJP: `Cumple`",
                        f"- DCR_w8_v2_col: `{_format_decimal(dcr_w8_v2_col) if dcr_w8_v2_col is not None else 'n/a'}`",
                        f"- Resultado: `{_render_result_plain_es(result_w8_v2_col)}`",
                        "",
                    ]
                )
            else:
                block_27_lines.extend(
                    [
                        f"- phi usado (phi_fragil): `{_format_decimal(phi_fragil)}`",
                        f"- Fy_dp_col: `{_format_quantity(fy_dp_col_q_w8.model_dump() if isinstance(fy_dp_col_q_w8, Quantity) else None)}`",
                        f"- h_dp_col: `{_format_quantity(h_dp_col_q.model_dump() if isinstance(h_dp_col_q, Quantity) else None)}`",
                        f"- t_dp_col: `{_format_quantity(t_dp_col_q_w8.model_dump() if isinstance(t_dp_col_q_w8, Quantity) else None)}`",
                        f"- n_dp_col: `{_format_text(n_dp_col_val)}`",
                        f"- tw_col: `{_format_quantity(tw_col_q_w8.model_dump() if isinstance(tw_col_q_w8, Quantity) else None)}`",
                        f"- b_dp_col: `{_format_quantity(b_dp_col_q.model_dump() if isinstance(b_dp_col_q, Quantity) else None)}`",
                        f"- L_gap_w8_col: `{_format_quantity(l_gap_w8_col_q.model_dump() if isinstance(l_gap_w8_col_q, Quantity) else None)}`",
                        f"- L_w8_col: `{_format_quantity(l_w8_col_q.model_dump() if isinstance(l_w8_col_q, Quantity) else None)}`",
                        f"- Fexx_w8_col: `{_format_quantity(fexx_w8_q.model_dump() if isinstance(fexx_w8_q, Quantity) else None)}`",
                        f"- w_w8_col: `{_format_quantity(w_w8_q.model_dump() if isinstance(w_w8_q, Quantity) else None)}`",
                        f"- nl_w8_col: `{_format_text(nl_w8_col)}`",
                        f"- kds_w8_col: `{_format_text(kds_w8_col)}`",
                        f"- Mf_vgizq_max: `{_format_quantity(mf_vgizq_max_q.model_dump() if isinstance(mf_vgizq_max_q, Quantity) else None)}`",
                        f"- Mf_vgizq_min: `{_format_quantity(mf_vgizq_min_q.model_dump() if isinstance(mf_vgizq_min_q, Quantity) else None)}`",
                        f"- Mf_vgder_max: `{_format_quantity(mf_vgder_max_q.model_dump() if isinstance(mf_vgder_max_q, Quantity) else None)}`",
                        f"- Mf_vgder_min: `{_format_quantity(mf_vgder_min_q.model_dump() if isinstance(mf_vgder_min_q, Quantity) else None)}`",
                        f"- Combo1_Mf: `{_format_quantity(combo1_q.model_dump() if isinstance(combo1_q, Quantity) else None)}`",
                        f"- Combo2_Mf: `{_format_quantity(combo2_q.model_dump() if isinstance(combo2_q, Quantity) else None)}`",
                        f"- MaxCombo_Mf: `{_format_quantity(combo_max_q.model_dump() if isinstance(combo_max_q, Quantity) else None)}`",
                        f"- Factor t_dp/(t_dp*n_dp+tw): `{_format_decimal(ratio_tdp_over_sum) if ratio_tdp_over_sum is not None else 'n/a'}`",
                        f"- Ru1_w8_v2_col: `{_format_quantity(ru1_w8_v2_col_q.model_dump() if isinstance(ru1_w8_v2_col_q, Quantity) else None)}`",
                        f"- Ru2_w8_v2_col: `{_format_quantity(ru2_w8_v2_col_q.model_dump() if isinstance(ru2_w8_v2_col_q, Quantity) else None)}`",
                        f"- Ru_w8_v2_col: `{_format_quantity(ru_w8_v2_col_q.model_dump() if isinstance(ru_w8_v2_col_q, Quantity) else None)}`",
                        f"- phi*Rn_w8_v2_col: `{_format_quantity(phi_rn_w8_v2_col_q.model_dump() if isinstance(phi_rn_w8_v2_col_q, Quantity) else None)}`",
                        f"- DCR_w8_v2_col: `{_format_decimal(dcr_w8_v2_col) if dcr_w8_v2_col is not None else 'n/a'}`",
                        f"- Resultado: `{_render_result_plain_es(result_w8_v2_col)}`",
                        "",
                    ]
                )
            block_27 = "\n".join(block_27_lines)
            block_27 = _align_nested_heading_numbers_with_step(block_27, step_number=assigned_step_number)
            content.append(block_27)
            next_step_number += 1

            # Paso 28 - Soldadura #7 (platina de enchape con alma de columna)
            assigned_step_number = next_step_number
            step1_w7 = step_1_inputs if isinstance(step_1_inputs, dict) else {}
            wpz_step = step_21_5_1_panel_zone if isinstance(step_21_5_1_panel_zone, dict) else {}
            wpz_inputs_28 = wpz_step.get("inputs", {}) if isinstance(wpz_step.get("inputs", {}), dict) else {}

            ru_wpz_v2_col_q = _as_quantity(wpz_step.get("demand"))
            fexx_w7_q = _as_quantity(step1_w7.get("Fexx_w7_col"))
            # As requested by user for 28.1.1 equation
            d_hole_for_w7_capacity_q = _as_quantity(step1_w7.get("d_hole_w7_col"))
            t_dp_col_q_w7 = _as_quantity(step1_w7.get("t_dp_col"))
            tw_col_q_w7 = _as_quantity(step1_w7.get("tw_col"))
            b_dp_col_q_w7 = _as_quantity(step1_w7.get("b_dp_col"))
            d_vgizq_q_w7 = _as_quantity(wpz_inputs_28.get("db_vgizq") or wpz_inputs_28.get("d_vgizq"))
            d_vgder_q_w7 = _as_quantity(wpz_inputs_28.get("db_vgder") or wpz_inputs_28.get("d_vgder"))
            tf_vgizq_q_w7 = _as_quantity(wpz_inputs_28.get("tf_vgizq"))
            tf_vgder_q_w7 = _as_quantity(wpz_inputs_28.get("tf_vgder"))

            nfilas_w7_col_val = None
            try:
                raw_nfil = step1_w7.get("nfilas_w7_col")
                if raw_nfil is None:
                    raw_nfil = step1_w7.get("nl_w7_col")
                if raw_nfil is not None:
                    nfilas_w7_col_val = int(raw_nfil)
            except (TypeError, ValueError):
                nfilas_w7_col_val = None

            ncolumna_w7_col_val = None
            try:
                raw_ncol = step1_w7.get("ncolumna_w7_col")
                if raw_ncol is not None:
                    ncolumna_w7_col_val = int(raw_ncol)
            except (TypeError, ValueError):
                ncolumna_w7_col_val = None

            n_dp_col_val_w7 = 1.0
            try:
                if step1_w7.get("n_dp_col") is not None:
                    n_dp_col_val_w7 = float(step1_w7.get("n_dp_col"))
            except (TypeError, ValueError):
                n_dp_col_val_w7 = 1.0

            phi_fragil_w7 = 0.75
            try:
                if step1_w7.get("phi_fragil") is not None:
                    phi_fragil_w7 = float(step1_w7.get("phi_fragil"))
            except (TypeError, ValueError):
                phi_fragil_w7 = 0.75

            max_d_minus_2tf_q: Quantity | None = None
            d_minus_candidates: list[Quantity] = []
            def _to_unit_len_w7(q: Quantity, target_unit: str) -> Quantity | None:
                if q.unit == target_unit:
                    return q
                if q.unit == "mm" and target_unit == "in":
                    return Quantity(value=q.value / 25.4, unit="in")
                if q.unit == "in" and target_unit == "mm":
                    return Quantity(value=q.value * 25.4, unit="mm")
                return None
            if isinstance(d_vgizq_q_w7, Quantity) and isinstance(tf_vgizq_q_w7, Quantity):
                tf_izq_conv = _to_unit_len_w7(tf_vgizq_q_w7, d_vgizq_q_w7.unit)
                if isinstance(tf_izq_conv, Quantity):
                    d_minus_candidates.append(
                        Quantity(value=d_vgizq_q_w7.value - 2.0 * tf_izq_conv.value, unit=d_vgizq_q_w7.unit)
                    )
            if isinstance(d_vgder_q_w7, Quantity) and isinstance(tf_vgder_q_w7, Quantity):
                tf_der_conv = _to_unit_len_w7(tf_vgder_q_w7, d_vgder_q_w7.unit)
                if isinstance(tf_der_conv, Quantity):
                    d_minus_candidates.append(
                        Quantity(value=d_vgder_q_w7.value - 2.0 * tf_der_conv.value, unit=d_vgder_q_w7.unit)
                    )
            if d_minus_candidates:
                base_unit_d = d_minus_candidates[0].unit
                converted_d: list[Quantity] = []
                for qd in d_minus_candidates:
                    qd_conv = _to_unit_len_w7(qd, base_unit_d)
                    if isinstance(qd_conv, Quantity):
                        converted_d.append(qd_conv)
                if converted_d:
                    max_d_minus_2tf_q = max(converted_d, key=lambda x: x.value)

            ru_w7_v2_col_q: Quantity | None = None
            if (
                isinstance(ru_wpz_v2_col_q, Quantity)
                and isinstance(t_dp_col_q_w7, Quantity)
                and isinstance(tw_col_q_w7, Quantity)
            ):
                tw_conv = _to_unit_len_w7(tw_col_q_w7, t_dp_col_q_w7.unit)
                if (
                    isinstance(tw_conv, Quantity)
                    and abs((t_dp_col_q_w7.value * n_dp_col_val_w7 + tw_conv.value)) > 1e-12
                ):
                    ratio_thickness = t_dp_col_q_w7.value / (t_dp_col_q_w7.value * n_dp_col_val_w7 + tw_conv.value)
                    ru_w7_v2_col_q = Quantity(
                        value=ru_wpz_v2_col_q.value * ratio_thickness,
                        unit=ru_wpz_v2_col_q.unit,
                    )

            phi_rn_w7_v2_col_q: Quantity | None = None
            if (
                isinstance(fexx_w7_q, Quantity)
                and isinstance(d_hole_for_w7_capacity_q, Quantity)
                and nfilas_w7_col_val is not None
                and ncolumna_w7_col_val is not None
            ):
                factor_cells = float(nfilas_w7_col_val) * float(ncolumna_w7_col_val)
                if fexx_w7_q.unit == "MPa" and d_hole_for_w7_capacity_q.unit == "mm":
                    rn_n = (
                        factor_cells
                        * 0.60
                        * fexx_w7_q.value
                        * (0.25 * 3.1416 * (d_hole_for_w7_capacity_q.value ** 2))
                    )
                    phi_rn_w7_v2_col_q = Quantity(value=phi_fragil_w7 * rn_n / 1000.0, unit="kN")
                elif fexx_w7_q.unit == "ksi" and d_hole_for_w7_capacity_q.unit == "in":
                    rn_kip = (
                        factor_cells
                        * 0.60
                        * fexx_w7_q.value
                        * (0.25 * 3.1416 * (d_hole_for_w7_capacity_q.value ** 2))
                    )
                    phi_rn_w7_v2_col_q = Quantity(value=phi_fragil_w7 * rn_kip, unit="kip")

            dcr_w7_v2_col: float | None = None
            result_w7_v2_col = "n/a"
            if isinstance(ru_w7_v2_col_q, Quantity) and isinstance(phi_rn_w7_v2_col_q, Quantity):
                if phi_rn_w7_v2_col_q.unit == ru_w7_v2_col_q.unit:
                    phi_rn_conv_w7 = phi_rn_w7_v2_col_q
                elif phi_rn_w7_v2_col_q.unit == "kN" and ru_w7_v2_col_q.unit == "kip":
                    phi_rn_conv_w7 = Quantity(value=phi_rn_w7_v2_col_q.value / 4.4482216152605, unit="kip")
                elif phi_rn_w7_v2_col_q.unit == "kip" and ru_w7_v2_col_q.unit == "kN":
                    phi_rn_conv_w7 = Quantity(value=phi_rn_w7_v2_col_q.value * 4.4482216152605, unit="kN")
                else:
                    phi_rn_conv_w7 = None
                if isinstance(phi_rn_conv_w7, Quantity) and phi_rn_conv_w7.value > 0:
                    dcr_w7_v2_col = ru_w7_v2_col_q.value / phi_rn_conv_w7.value
                    result_w7_v2_col = "Cumple" if dcr_w7_v2_col <= 1.0 else "No cumple"
                else:
                    result_w7_v2_col = "No cumple"

            block_28_lines = [
                f"## Paso {assigned_step_number}- Revisión de resistencia de soldadura # 7 (Platina de enchape con alma de columna)",
                "",
                f"### {assigned_step_number}.1. Revisión de capacidad a cortante",
                "",
                f"#### {assigned_step_number}.1.1. ELR #1: Rotura de soldadura",
                "",
                "- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + Desarrollo interno`",
                "- Ecuacion: `Ru_w7_v2_col = Ru_wpz_v2_col * (t_dp_col / (t_dp_col*n_dp_col + tw_col)); phi*Rn_w7_v2_col = phi_fragil * (nfilas_w7_col)*(ncolumna_w7_col) * 0.60 * Fexx_w7_col * 0.25 * 3.1416 * d_hole_w7_col^2; DCR_w7_v2_col = Ru_w7_v2_col / phi*Rn_w7_v2_col`",
                f"- phi usado (phi_fragil): `{_format_decimal(phi_fragil_w7)}`",
                f"- nfilas_w7_col: `{_format_text(nfilas_w7_col_val)}`",
                f"- ncolumna_w7_col: `{_format_text(ncolumna_w7_col_val)}`",
	                f"- Ru_wpz_v2_col: `{_format_quantity(ru_wpz_v2_col_q.model_dump() if isinstance(ru_wpz_v2_col_q, Quantity) else None)}`",
	                f"- t_dp_col: `{_format_quantity(t_dp_col_q_w7.model_dump() if isinstance(t_dp_col_q_w7, Quantity) else None)}`",
	                f"- n_dp_col: `{_format_text(n_dp_col_val_w7)}`",
	                f"- tw_col: `{_format_quantity(tw_col_q_w7.model_dump() if isinstance(tw_col_q_w7, Quantity) else None)}`",
	                f"- Fexx_w7_col: `{_format_quantity(fexx_w7_q.model_dump() if isinstance(fexx_w7_q, Quantity) else None)}`",
	                f"- d_hole_w7_col (usado en formula): `{_format_quantity(d_hole_for_w7_capacity_q.model_dump() if isinstance(d_hole_for_w7_capacity_q, Quantity) else None)}`",
	                f"- Ru_w7_v2_col: `{_format_quantity(ru_w7_v2_col_q.model_dump() if isinstance(ru_w7_v2_col_q, Quantity) else None)}`",
	                f"- phi*Rn_w7_v2_col: `{_format_quantity(phi_rn_w7_v2_col_q.model_dump() if isinstance(phi_rn_w7_v2_col_q, Quantity) else None)}`",
                f"- DCR_w7_v2_col: `{_format_decimal(dcr_w7_v2_col) if dcr_w7_v2_col is not None else 'n/a'}`",
                f"- Resultado: `{_render_result_plain_es(result_w7_v2_col)}`",
                "",
            ]
            block_28 = "\n".join(block_28_lines)
            block_28 = _align_nested_heading_numbers_with_step(block_28, step_number=assigned_step_number)
            content.append(block_28)
            next_step_number += 1
    if connection_family_normalized == "moment_prequalified":
        def _extract_dcr_summary_entries_from_content(blocks: list[str]) -> list[dict[str, Any]]:
            text = "\n".join(str(item) for item in blocks)
            current_h2 = ""
            current_h3 = ""
            current_h4 = ""
            entries: list[dict[str, Any]] = []
            for raw_line in text.splitlines():
                line = raw_line.strip()
                if line.startswith("## "):
                    current_h2 = line[3:].strip()
                    current_h3 = ""
                    current_h4 = ""
                    continue
                if line.startswith("### "):
                    current_h3 = line[4:].strip()
                    current_h4 = ""
                    continue
                if line.startswith("#### "):
                    current_h4 = line[5:].strip()
                    continue
                match = re.match(r"^- (DCR[^:]+): `([^`]*)`", line)
                if not match:
                    continue
                dcr_name = match.group(1).strip()
                dcr_raw = match.group(2).strip()
                if dcr_raw.lower() in {"n/a", "na", ""}:
                    continue
                try:
                    dcr_value = float(dcr_raw.replace(",", ""))
                except ValueError:
                    continue
                subchapter = current_h4 or current_h3 or current_h2
                entries.append(
                    {
                        "name": dcr_name,
                        "value": dcr_value,
                        "subchapter": subchapter,
                    }
                )
            entries.sort(key=lambda item: item["value"], reverse=True)
            return entries

        dcr_summary_entries = _extract_dcr_summary_entries_from_content(content)
        if dcr_summary_entries:
            assigned_step_number = next_step_number
            worst_entry = dcr_summary_entries[0]
            worst_state = "🔴" if worst_entry["value"] > 1.0 else "🟢"
            summary_lines = [
                f"## Paso {assigned_step_number} - Resumen general",
                "",
                "DCR ordenados de mayor a menor para identificar los estados limite criticos.",
                (
                    f"- DCR critico global: {worst_state} `{worst_entry['name']} = "
                    f"{_format_decimal(worst_entry['value'])}` en `{worst_entry['subchapter']}`"
                ),
                "",
            ]
            for idx, entry in enumerate(dcr_summary_entries, start=1):
                status_icon = "🟢" if entry["value"] <= 1.0 else "🔴"
                summary_lines.extend(
                    [
                        (
                            f"{idx}. {status_icon} `{entry['name']}` = "
                            f"`{_format_decimal(entry['value'])}`"
                        ),
                        f"Subcapitulo aplicado: `{entry['subchapter']}`",
                    ]
                )
            summary_lines.append("")
            block_29 = "\n".join(summary_lines)
            content.append(block_29)
            next_step_number += 1

    content.append("")
    rendered = "\n".join(content)
    rendered = _normalize_markdown_spacing(rendered)
    rendered = _normalize_memory_spanish_labels(rendered)
    rendered = _dedupe_markdown_headings(rendered)
    return rendered + "\n"


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
        ["Muz_blt_web", "Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web", _num(mz_kip_in), "kip-in"],
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
            "- Ecuacion base: `Muz_blt_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`",
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


