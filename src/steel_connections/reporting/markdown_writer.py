from __future__ import annotations

from pathlib import Path

from steel_connections.models.output import DetailedRunResult


def _format_quantity(value: object) -> str:
    if not isinstance(value, dict):
        return "n/a"
    raw = value.get("value")
    unit = value.get("unit")
    if raw is None or unit is None:
        return "n/a"
    try:
        return f"{float(raw):.3f} {unit}"
    except (TypeError, ValueError):
        return "n/a"


def _format_text(value: object) -> str:
    if value is None:
        return "n/a"
    text = str(value).strip()
    return text if text else "n/a"


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
        lines.append("")
        lines.append(f"- Ambito: `{scope}`")
        lines.append(f"- Verificacion: `{verification}`")
        lines.append(f"- Clausula: `{clause}`")
        lines.append(f"- Resultado: {result_text}")
        lines.append("")
    return "\n".join(lines)


def render_memory_markdown(result: DetailedRunResult) -> str:
    rows = _collect_step_1_rows(result)
    notes = _collect_step_1_notes(result)
    content = [
        "# Memoria de Calculo",
        "",
        f"- Proyecto: `{result.project_id}`",
        f"- Caso: `{result.case_id}`",
        f"- Familia: `{result.connection_family}`",
        f"- Tipo: `{result.connection_type}`",
        f"- Estado global: `{result.global_status.value}`",
        "",
        "## Paso 1 - PREQUALIFICATION LIMITS",
        "",
        "Comparacion directa de valor calculado contra limite normativo (sin formato DCR).",
        "",
    ]
    if notes:
        content.append(_render_step_1_notes(notes))
    if rows:
        content.append(_render_step_1_list(rows))
    else:
        content.append("No hay subchequeos de prequalification disponibles para este caso.")
    content.append("")
    return "\n".join(content)


def write_memory_markdown(result: DetailedRunResult, target_dir: str | Path) -> Path:
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "memory.md"
    rendered = render_memory_markdown(result).rstrip("\n") + "\n"
    target.write_text(rendered, encoding="utf-8")
    return target
