from __future__ import annotations

from pathlib import Path

from steel_connections.models.output import DetailedRunResult


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
                rows.append(item)
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
                notes.append(item)
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
                rows.append(item)
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
                notes.append(item)
    return notes


def _collect_step_2_mpr(result: DetailedRunResult) -> dict | None:
    for check in result.checks:
        if ".step2_probable_moment_plastic_hinge" not in check.rule_id:
            continue
        return {
            "rule_id": check.rule_id,
            "clause": check.clause,
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
    lines: list[str] = []
    for item in notes:
        note_id = _format_text(item.get("id"))
        scope = _format_text(item.get("scope")).upper()
        description = _format_text(item.get("description"))
        clause = _format_text(item.get("clause"))
        lines.append(f"### Nota tecnica - {description}")
        lines.append("")
        lines.append(f"- Ambito: `{scope}`")
        lines.append(f"- Clausula: `{clause}`")
        requirement = _format_text(item.get("requirement"))
        if requirement != "n/a":
            lines.append(f"- Requisito: `{requirement}`")
        if note_id == "section_6_3.end_plate_stiffener_geometry_note":
            formula = _format_text(item.get("formula"))
            hst = _format_quantity(item.get("candidate_a"))
            lst = _format_quantity(item.get("candidate_b"))
            edge = _format_quantity(item.get("derived_value"))
            if formula != "n/a":
                lines.append(f"- Formula: `{formula}`")
            lines.append(f"- stiffener_height (hst): `{hst}`")
            lines.append(f"- stiffener_widht(Lst): `{lst}`")
            lines.append(f"- edge detailing: `{edge}`")
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
        formula = _format_text(item.get("formula"))
        if formula != "n/a":
            candidate_a_label = _format_text(item.get("candidate_a_label"))
            candidate_a = _format_quantity(item.get("candidate_a"))
            candidate_b_label = _format_text(item.get("candidate_b_label"))
            candidate_b = _format_quantity(item.get("candidate_b"))
            protected_zone = _format_quantity(item.get("protected_zone_length"))
            derived_value = _format_quantity(item.get("derived_value"))
            lines.append(f"- Formula: `{formula}`")
            lines.append(f"- Candidato A ({candidate_a_label}): `{candidate_a}`")
            lines.append(f"- Candidato B ({candidate_b_label}): `{candidate_b}`")
            if derived_value != "n/a":
                lines.append(f"- Valor derivado: `{derived_value}`")
            elif protected_zone != "n/a":
                lines.append(f"- Longitud zona protegida requerida: `{protected_zone}`")
        lines.append("")
    return "\n".join(lines)


def _render_step_2_mpr(step_2: dict) -> str:
    inputs = step_2.get("inputs", {})
    inter = step_2.get("intermediates", {})
    lines = [
        "## Paso 2 - Probable Maximum Moment At Plastic Hinge (Mpr)",
        "",
        "Calculo de momento probable segun Eq. (2.4-1) y Eq. (2.4-2), usando `Ze = Zx` del catalogo de la viga.",
        "",
        f"- Clausula: `{_format_text(step_2.get('clause'))}`",
        f"- Ecuacion: `{_format_text(step_2.get('equation'))}`",
        f"- Fy: `{_format_quantity(inputs.get('beam_fy'))}`",
        f"- Fu: `{_format_quantity(inputs.get('beam_fu'))}`",
        f"- Ry: `{_format_text(inputs.get('ry'))}`",
        f"- Ze (catalogo): `{_format_quantity(inputs.get('ze'))}`",
        f"- Cpr: `{_format_text(inter.get('cpr'))}`",
        f"- Mpr calculado: `{_format_quantity(step_2.get('demand'))}`",
        f"- Mpr de comparacion: `{_format_quantity(step_2.get('capacity'))}`",
        f"- Resultado: `{_format_text(step_2.get('status'))}`",
        "",
    ]
    return "\n".join(lines)


def _render_step_3_sh(step_3: dict) -> str:
    inputs = step_3.get("inputs", {})
    lines = [
        "## Paso 3 - Distancia De Rotula Plastica Desde La Cara De Columna (Sh)",
        "",
        "Para 4E: `Sh = min(d/2, 3bf)`. Para 4ES/8ES: `Sh = Lst + tp`.",
        "",
        f"- Clausula: `{_format_text(step_3.get('clause'))}`",
        f"- Ecuacion: `{_format_text(step_3.get('equation'))}`",
        f"- Tipo de conexion: `{_format_text(inputs.get('connection_type'))}`",
        f"- Beam shape: `{_format_text(inputs.get('beam_shape'))}`",
        f"- Lst (si aplica): `{_format_quantity(inputs.get('stiffener_length'))}`",
        f"- tp (si aplica): `{_format_quantity(inputs.get('end_plate_thickness'))}`",
        f"- Sh calculado: `{_format_quantity(step_3.get('demand'))}`",
        f"- Resultado: `{_format_text(step_3.get('status'))}`",
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
        f"- Clausula: `{_format_text(step_4.get('clause'))}`",
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
        f"- Resultado: `{_format_text(step_4.get('status'))}`",
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
        f"- Clausula: `{_format_text(step_5.get('clause'))}`",
        "- Ecuacion: `Mfmax.der = Mpr + Vhmax.der*Sh; Mfmin.der = Mpr + Vhmin.der*Sh`",
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
        f"- Mfmax gobernante: `{_format_quantity(step_5.get('demand'))}`",
        f"- Resultado: `{_format_text(step_5.get('status'))}`",
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
                f"- Clausula: `{_format_text(step_6_1.get('clause'))}`",
                f"- Ecuacion: `{_format_text(step_6_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- h1: `{_format_quantity(inputs.get('h1'))}`",
                f"- h2: `{_format_quantity(inputs.get('h2'))}`",
                f"- h3: `{_format_quantity(inputs.get('h3'))}`",
                f"- h4: `{_format_quantity(inputs.get('h4'))}`",
                f"- Pub: `{_format_quantity(step_6_1.get('demand'))}`",
                f"- phiPnb: `{_format_quantity(step_6_1.get('capacity'))}`",
                f"- DCRbt: `{_format_text(step_6_1.get('dcr'))}`",
                f"- Resultado: `{_format_text(step_6_1.get('status'))}`",
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
                f"- Clausula: `{_format_text(step_6_2.get('clause'))}`",
                f"- Ecuacion: `{_format_text(step_6_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vhmax: `{_format_quantity(inputs.get('vhmax'))}`",
                f"- nb: `{_format_text(inputs.get('nb'))}`",
                f"- Vub: `{_format_quantity(step_6_2.get('demand'))}`",
                f"- phiVnb: `{_format_quantity(step_6_2.get('capacity'))}`",
                f"- DCRbv: `{_format_text(step_6_2.get('dcr'))}`",
                f"- Resultado: `{_format_text(step_6_2.get('status'))}`",
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
                f"- Clausula: `{_format_text(step_7_1_1.get('clause'))}`",
                f"- Ecuacion: `{_format_text(step_7_1_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Mup: `{_format_quantity(step_7_1_1.get('demand'))}`",
                f"- phiMnb: `{_format_quantity(step_7_1_1.get('capacity'))}`",
                f"- DCRpm: `{_format_text(step_7_1_1.get('dcr'))}`",
                f"- Yp calculado: `{_format_quantity(inputs.get('yp'))}`",
                f"- Tabla Yp aplicada: `{_format_text(inputs.get('yp_table'))}`",
                f"- Caso Yp: `{_format_text(inputs.get('yp_case'))}`",
                f"- s: `{_format_quantity(inter.get('s'))}`",
                f"- pfi de entrada: `{_format_quantity(inter.get('pfi_input'))}`",
                f"- pfi efectivo: `{_format_quantity(inter.get('pfi_effective'))}`",
                f"- Resultado: `{_format_text(step_7_1_1.get('status'))}`",
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
                f"- Clausula: `{_format_text(step_7_2_1.get('clause'))}`",
                f"- Ecuacion: `{_format_text(step_7_2_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vup: `{_format_quantity(step_7_2_1.get('demand'))}`",
                f"- phiVn1p: `{_format_quantity(step_7_2_1.get('capacity'))}`",
                f"- DCRpv: `{_format_text(step_7_2_1.get('dcr'))}`",
                f"- d (altura viga): `{_format_quantity(inputs.get('d'))}`",
                f"- Resultado: `{_format_text(step_7_2_1.get('status'))}`",
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
                f"- Clausula: `{_format_text(step_7_2_2.get('clause'))}`",
                f"- Ecuacion: `{_format_text(step_7_2_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vup: `{_format_quantity(step_7_2_2.get('demand'))}`",
                f"- phiVnb: `{_format_quantity(step_7_2_2.get('capacity'))}`",
                f"- DCRpv: `{_format_text(step_7_2_2.get('dcr'))}`",
                f"- dh (diametro agujero estandar): `{_format_quantity(inputs.get('dh'))}`",
                f"- d (altura viga): `{_format_quantity(inputs.get('d'))}`",
                f"- Resultado: `{_format_text(step_7_2_2.get('status'))}`",
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
                f"- Clausula: `{_format_text(step_7_3_1.get('clause'))}`",
                f"- Ecuacion: `{_format_text(step_7_3_1.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vu2p: `{_format_quantity(step_7_3_1.get('demand'))}`",
                f"- phiVn2p: `{_format_quantity(step_7_3_1.get('capacity'))}`",
                f"- DCRpn2: `{_format_text(step_7_3_1.get('dcr'))}`",
                f"- lc: `{_format_quantity(inputs.get('lc'))}`",
                f"- dh: `{_format_quantity(inputs.get('dh'))}`",
                f"- db: `{_format_quantity(inputs.get('db'))}`",
                f"- Resultado: `{_format_text(step_7_3_1.get('status'))}`",
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
                f"- Clausula: `{_format_text(step_7_3_2.get('clause'))}`",
                f"- Ecuacion: `{_format_text(step_7_3_2.get('equation'))}`",
                f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
                f"- Vu2p: `{_format_quantity(step_7_3_2.get('demand'))}`",
                f"- phiVn2p: `{_format_quantity(step_7_3_2.get('capacity'))}`",
                f"- DCRpn2: `{_format_text(step_7_3_2.get('dcr'))}`",
                f"- lc: `{_format_quantity(inputs.get('lc'))}`",
                f"- dh: `{_format_quantity(inputs.get('dh'))}`",
                f"- db: `{_format_quantity(inputs.get('db'))}`",
                f"- Resultado: `{_format_text(step_7_3_2.get('status'))}`",
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
        f"- Clausula: `{_format_text(step_8_1_1.get('clause'))}`",
        f"- Ecuacion: `{_format_text(step_8_1_1.get('equation'))}`",
        f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
        f"- Tipo soldadura rigidizador: `{weld_type}`",
    ]
    if weld_type == "cjp":
        lines.extend(
            [
                "- CJP: `Cumple`",
                f"- Resultado: `{_format_text(step_8_1_1.get('status'))}`",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            f"- Pust: `{_format_quantity(step_8_1_1.get('demand'))}`",
            f"- phiRnst: `{_format_quantity(step_8_1_1.get('capacity'))}`",
            f"- DCRst,w1,t: `{_format_text(step_8_1_1.get('dcr'))}`",
            f"- l_st (longitud soldadura): `{_format_quantity(inputs.get('lst'))}`",
            f"- w_st (espesor soldadura): `{_format_quantity(inputs.get('wst'))}`",
            f"- n_l (lineas soldadura): `{_format_text(inputs.get('nl'))}`",
            f"- Resultado: `{_format_text(step_8_1_1.get('status'))}`",
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
        f"- Clausula: `{_format_text(step_9_1_1.get('clause'))}`",
        f"- Ecuacion: `{_format_text(step_9_1_1.get('equation'))}`",
        f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
        f"- Tipo soldadura viga-rigidizador: `{weld_type}`",
    ]
    if weld_type == "cjp":
        lines.extend(
            [
                "- CJP: `Cumple`",
                f"- Resultado: `{_format_text(step_9_1_1.get('status'))}`",
                "",
            ]
        )
        return "\n".join(lines)
    lines.extend(
        [
            f"- Vust,w2: `{_format_quantity(step_9_1_1.get('demand'))}`",
            f"- phiVnst,w2: `{_format_quantity(step_9_1_1.get('capacity'))}`",
            f"- DCRst,w2,v: `{_format_text(step_9_1_1.get('dcr'))}`",
            f"- l_st,w2 (longitud soldadura): `{_format_quantity(inputs.get('lst_w2'))}`",
            f"- w_st,2 (espesor soldadura): `{_format_quantity(inputs.get('wst2'))}`",
            f"- n_l,w2 (lineas soldadura): `{_format_text(inputs.get('nl_w2'))}`",
            f"- Resultado: `{_format_text(step_9_1_1.get('status'))}`",
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
        f"- Clausula: `{_format_text(step_10_1_1.get('clause'))}`",
        f"- Ecuacion: `{_format_text(step_10_1_1.get('equation'))}`",
        f"- phi usado: `{_format_text(design_factors.get('phi'))}`",
        f"- Vubm: `{_format_quantity(step_10_1_1.get('demand'))}`",
        f"- phiVnbm: `{_format_quantity(step_10_1_1.get('capacity'))}`",
        f"- DCRbm,v: `{_format_text(step_10_1_1.get('dcr'))}`",
        f"- Cv1: `{_format_text(inputs.get('cv1'))}`",
        f"- kv: `{_format_text(inter.get('kv'))}`",
        f"- h/tw: `{_format_text(inter.get('h_over_tw'))}`",
        f"- h: `{_format_scalar_with_unit(inter.get('h_clear'), 'mm')}`",
        f"- Resultado: `{_format_text(step_10_1_1.get('status'))}`",
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
    pfi_mm = _quantity_to_mm(step_11_inputs.get("edge_pfi"))
    pb_mm = _quantity_to_mm(step_11_inputs.get("pitch_pb"))
    twe_mm = _quantity_to_mm(weld_thickness_twe)
    fybm_mpa = _stress_to_mpa(step_10_inputs.get("fybm"))
    tw_bm_mm = _quantity_to_mm(step_10_inputs.get("tw_bm"))
    fexx_mpa = _stress_to_mpa(step_11_inputs.get("weld_fexx"))
    nl_raw = step_11_inputs.get("end_plate_beam_web_weld_lines_nl")
    try:
        nl = int(nl_raw) if nl_raw is not None else 2
    except (TypeError, ValueError):
        nl = 2
    if nl < 1:
        nl = 1
    phi = 0.9

    hwef_mm = None
    puww3_kn = None
    phi_pnww3_kn = None
    dcr_ww3p = None
    if pfi_mm is not None and pb_mm is not None:
        hwef_mm = pfi_mm + pb_mm + 150.0
    if hwef_mm is not None and fybm_mpa is not None and tw_bm_mm is not None:
        puww3_kn = fybm_mpa * tw_bm_mm * hwef_mm / 1000.0
    if hwef_mm is not None and fexx_mpa is not None and twe_mm is not None:
        phi_pnww3_kn = phi * nl * 0.6 * fexx_mpa * 0.707 * hwef_mm * twe_mm / 1000.0
    if puww3_kn is not None and phi_pnww3_kn is not None and phi_pnww3_kn > 0.0:
        dcr_ww3p = puww3_kn / phi_pnww3_kn

    hwef_text = f"{_format_decimal(hwef_mm)} mm" if hwef_mm is not None else "n/a"
    puww3_text = f"{_format_decimal(puww3_kn)} kN" if puww3_kn is not None else "n/a"
    phi_pnww3_text = f"{_format_decimal(phi_pnww3_kn)} kN" if phi_pnww3_kn is not None else "n/a"
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
        "- Clausula: `Section 6.7 + AISC 360-22 J2.4`",
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
            f"- nl (numero de cordones): `{_format_text(nl)}`",
            f"- hwef: `{hwef_text}`",
            f"- Puww3: `{puww3_text}`",
            f"- phiPnww3: `{phi_pnww3_text}`",
            f"- DCRww3p: `{dcr_text}`",
            f"- Resultado: `{result_line}`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_splice_step_1_notes(notes: list[dict]) -> str:
    lines: list[str] = []
    for item in notes:
        note_id = _format_text(item.get("id"))
        if note_id == "bbmb_splice.step1.geometry_formulas_common_note":
            lines.extend(
                [
                    "### Nota tecnica - Formulas geometricas (dato comun)",
                    "",
                    "- Ambito: `VIGA`",
                    f"- Clausula: `{_format_text(item.get('clause'))}`",
                    f"- alpha = sep: `{_format_quantity(item.get('alpha'))}`",
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
                    f"- Clausula: `{_format_text(item.get('clause'))}`",
                    f"- Formula hp1: `{_format_text(item.get('hp1_formula'))}`",
                    f"- hp1 calculado: `{_format_quantity(item.get('hp1_calc'))}`",
                    f"- Formula bp1: `{_format_text(item.get('bp1_formula'))}`",
                    f"- bp1 calculado: `{_format_quantity(item.get('bp1_calc'))}`",
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
                    f"- Clausula: `{_format_text(item.get('clause'))}`",
                    f"- Formula bp2: `{_format_text(item.get('bp2_formula'))}`",
                    f"- bp2 calculado: `{_format_quantity(item.get('bp2_calc'))}`",
                    f"- Formula lp2: `{_format_text(item.get('lp2_formula'))}`",
                    f"- lp2 calculado: `{_format_quantity(item.get('lp2_calc'))}`",
                    "",
                ]
            )
    return "\n".join(lines)


def _render_fully_restrained_splice_outline(rows_viga: list[dict], notes_viga: list[dict]) -> str:
    lines = [
        "## Revision conexion: Viga",
        "",
        "### Punto 1 - Revision geometrica de detalle (detailing checks)",
        "",
    ]
    if rows_viga:
        lines.append(_render_step_1_list_grouped_by_scope(rows_viga))
    else:
        lines.append("No hay subchequeos de detailing disponibles para este caso.")
    rendered_notes = _render_splice_step_1_notes(notes_viga)
    if rendered_notes:
        lines.append(rendered_notes)
    lines.extend(
        [
            "",
            "## Revision conexion: Platina 1",
            "",
            "## Revision conexion: Pernos 1",
            "",
            "## Revision conexion: Platina 2",
            "",
            "## Revision conexion: Pernos 2",
            "",
        ]
    )
    return "\n".join(lines)

def _render_step_1_list(rows: list[dict]) -> str:
    lines: list[str] = []
    for idx, item in enumerate(rows, start=1):
        scope = str(item.get("scope", "n/a")).upper()
        description = str(item.get("description", "n/a"))
        calculated_symbol = str(item.get("calculated_symbol", "calc"))
        limit_symbol = str(item.get("limit_symbol", "lim"))
        calculated = _format_quantity(item.get("calculated"))
        result_text = _render_result_label(item.get("result", item.get("status", "UNKNOWN")))
        clause = str(item.get("clause", "n/a"))
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

        lines.append(f"### Chequeo 1.{idx} - {description} (`{calculated_symbol}`)")
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
    idx = 1
    for scope in sorted(grouped.keys()):
        lines.append(f"#### Ambito: `{scope}`")
        lines.append("")
        for item in grouped[scope]:
            description = str(item.get("description", "n/a"))
            calculated_symbol = str(item.get("calculated_symbol", "calc"))
            limit_symbol = str(item.get("limit_symbol", "lim"))
            calculated = _format_quantity(item.get("calculated"))
            result_text = _render_result_label(item.get("result", item.get("status", "UNKNOWN")))
            clause = str(item.get("clause", "n/a"))
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

            lines.append(f"### Chequeo 1.{idx} - {description} (`{calculated_symbol}`)")
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
    content = [
        "# Memoria de Calculo",
        "",
        f"- Proyecto: `{result.project_id}`",
        f"- Caso: `{result.case_id}`",
        f"- Familia: `{result.connection_family}`",
        f"- Tipo: `{result.connection_type}`",
        f"- Estado global: `{result.global_status.value}`",
        "",
    ]
    connection_family_normalized = str(result.connection_family).strip().lower()
    if connection_family_normalized == "moment_prequalified":
        content.extend(
            [
                "## Revision conexion viga a derecha de columna",
                "",
                "## Paso 1 - PREQUALIFICATION LIMITS",
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
        content.append(_render_fully_restrained_splice_outline(splice_rows_viga, splice_notes_viga))
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
    content.append("")
    return "\n".join(content)


def write_memory_markdown(result: DetailedRunResult, target_dir: str | Path) -> Path:
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "memory.md"
    rendered = render_memory_markdown(result).rstrip("\n") + "\n"
    target.write_text(rendered, encoding="utf-8")
    return target

