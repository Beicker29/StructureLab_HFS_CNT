from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from steel_connections.models.results import DesignResult, LimitStateResult

from .formatting import (
    format_quantity,
    format_ratio,
    format_status,
    format_text,
    normalize_markdown_spacing,
)
from .projection import ReportProjection, build_report_projection


def _json_block(payload: Mapping[str, Any]) -> list[str]:
    if not payload:
        return []
    rendered = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    return ["", "```json", rendered, "```"]


def _render_diagnostics(result: DesignResult) -> list[str]:
    lines: list[str] = []
    if result.warnings:
        lines.extend(["", "## Advertencias", ""])
        for warning in result.warnings:
            lines.append(f"- {format_text(warning.warning_code)}: {format_text(warning.message)}")
    if result.errors:
        lines.extend(["", "## Errores", ""])
        for error in result.errors:
            lines.append(f"- {format_text(error.error_code)}: {format_text(error.message)}")
    return lines


def _render_check(index: int, check: LimitStateResult) -> list[str]:
    lines = [
        "",
        f"## Check {index} - {format_text(check.name)}",
        "",
        f"- Regla: `{format_text(check.rule_id)}`",
        f"- Documento: `{format_text(check.source_document)}`",
        f"- Clausula: `{format_text(check.clause)}`",
        f"- Estado: `{format_status(check.status)}`",
        f"- Demanda: `{format_quantity(check.demand)}`",
        f"- Capacidad: `{format_quantity(check.capacity)}`",
        f"- Capacidad final: `{format_quantity(check.final_capacity)}`",
        f"- DCR: `{format_ratio(check.dcr)}`",
        f"- Ecuacion: `{format_text(check.equation)}`",
    ]
    if check.na_reason:
        lines.append(f"- Razon NA: `{format_text(check.na_reason)}`")
    if check.notes:
        lines.append(f"- Notas: `{format_text(check.notes)}`")
    if check.warnings:
        lines.append("- Advertencias:")
        for warning in check.warnings:
            lines.append(f"  - `{format_text(warning.warning_code)}` {format_text(warning.message)}")
    if check.errors:
        lines.append("- Errores:")
        for error in check.errors:
            lines.append(f"  - `{format_text(error.error_code)}` {format_text(error.message)}")
    if check.inputs:
        lines.extend(["", "### Inputs"])
        lines.extend(_json_block(check.inputs))
    if check.intermediates:
        lines.extend(["", "### Intermedios"])
        lines.extend(_json_block(check.intermediates))
    if check.derived_values:
        lines.extend(["", "### Valores derivados"])
        lines.extend(_json_block(check.derived_values))
    if check.design_factors:
        lines.extend(["", "### Factores de diseno"])
        lines.extend(_json_block(check.design_factors))
    if check.units:
        lines.extend(["", "### Unidades"])
        lines.extend(_json_block(check.units))
    return lines


def _render_critical_checks(projection: ReportProjection) -> list[str]:
    if not projection.critical_checks:
        return []
    lines = ["", "## Checks criticos", ""]
    for item in projection.critical_checks:
        lines.append(
            f"- `{item.rule_id}` | Estado: `{format_status(item.status)}` | DCR: `{format_ratio(item.dcr)}`"
        )
    return lines


def render_design_result_markdown(result: DesignResult, *, title: str = "Memoria de calculo") -> str:
    """Render a DesignResult without reading catalogs or recalculating checks."""
    projection = build_report_projection(result)
    result = projection.result
    lines = [
        f"# {title}",
        "",
        "## Resumen",
        "",
        f"- Proyecto: `{format_text(result.project_id)}`",
        f"- Caso: `{format_text(result.case_id)}`",
        f"- Familia: `{format_text(result.connection_family)}`",
        f"- Tipo: `{format_text(result.connection_type)}`",
        f"- Estado de carga: `{format_text(result.load_state)}`",
        f"- Estado global: `{format_status(result.status)}`",
        f"- Checks OK: `{result.summary.ok_count}`",
        f"- Checks NG: `{result.summary.ng_count}`",
        f"- Checks NA: `{result.summary.na_count}`",
        f"- Checks ERROR: `{result.summary.error_count}`",
        f"- Advertencias: `{result.summary.warning_count}`",
        f"- Peor DCR: `{format_ratio(result.summary.worst_dcr)}`",
    ]
    lines.extend(_render_critical_checks(projection))
    lines.extend(_render_diagnostics(result))
    for item in projection.checks:
        lines.extend(_render_check(item.index, item.check))
    return normalize_markdown_spacing("\n".join(lines))


def write_design_result_markdown(
    result: DesignResult,
    target_dir: str | Path,
    *,
    filename: str = "memory.md",
    title: str = "Memoria de calculo",
) -> Path:
    directory = Path(target_dir)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename
    target.write_text(render_design_result_markdown(result, title=title), encoding="utf-8")
    return target
