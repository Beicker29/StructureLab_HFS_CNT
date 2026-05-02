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

def _render_step_1_list(rows: list[dict], *, chapter_number: int = 1) -> str:
    lines: list[str] = []
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
            verification = f"{calculated_symbol} {comparison} {limit_symbol}; {calculated} {comparison} {limit}"

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
        for item in grouped.get(scope, []):
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
                verification = f"{calculated_symbol} {comparison} {limit_symbol}; {calculated} {comparison} {limit}"

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
            return (2, 98, 9)
        if scope_upper == "WELD_7_COL":
            return (2, 100, 8)
        if scope_upper == "WELD_6_COL":
            return (2, 100, 9)
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
                g_b_q = (rows_by_scope_symbol.get((f"BEAM_{side.upper()}", f"g_b_{tag}")) or {}).get("calculated")

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
                f"- Altura neta de panel zone en columna para enchape (dz_dp_col): "
                f"`{_format_quantity(step1_inputs.get('dz_dp_col'))}`"
            )
            lines.append(
                f"- Ancho neto gobernante entre vigas para enchape (wz_dp_col): "
                f"`{_format_quantity(step1_inputs.get('wz_dp_col'))}`"
            )
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
                f"- Numero de lineas de soldadura #7 (nl_w7_col) (inp): "
                f"`{_format_text(step1_inputs.get('nl_w7_col'))}`"
            )
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
        excluded_scopes.update({"DOUBLER_PLATE_COL", "WELD_7_COL"})

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
                    scopes=scope_template,
                    rows=rows,
                    step_1_inputs=step_1_inputs,
                    step_2=step_2,
                    step_3=step_3,
                    step_4=step_4,
                    step_7_1_1_by_side=step_7_1_1_by_side,
                    step_6_1_by_side=step_6_1_by_side,
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
        if scope_template:
            if notes_step2:
                content.append(
                    _render_step_1_notes_by_scope_template(
                        notes_step2,
                        chapter_number=2,
                        scopes=scope_template,
                    )
                )
            else:
                content.append(_render_scope_subtitles_only(chapter_number=2, scopes=scope_template))
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
    content.append("")
    rendered = "\n".join(content)
    rendered = _normalize_markdown_spacing(rendered)
    rendered = _normalize_memory_spanish_labels(rendered)
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


