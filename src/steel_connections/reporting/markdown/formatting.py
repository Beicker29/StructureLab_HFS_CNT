from __future__ import annotations

import math
from typing import Any, Mapping

from steel_connections.models.units import Quantity


def format_decimal(value: object, *, digits: int = 6) -> str:
    if value is None:
        return "n/a"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return format_text(value)
    if not math.isfinite(numeric):
        return "n/a"
    text = f"{numeric:.{digits}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_text(value: object) -> str:
    if value is None:
        return "n/a"
    text = str(value).strip()
    return text if text else "n/a"


def quantity_to_mapping(value: object) -> Mapping[str, Any] | None:
    if isinstance(value, Quantity):
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return value
    return None


def format_quantity(value: object) -> str:
    mapping = quantity_to_mapping(value)
    if mapping is None:
        return "n/a"
    raw = mapping.get("value")
    unit = mapping.get("unit")
    if raw is None or unit is None:
        return "n/a"
    return f"{format_decimal(raw)} {format_text(unit)}"


def format_ratio(value: object) -> str:
    return format_decimal(value)


def format_status(value: object) -> str:
    text = format_text(getattr(value, "value", value)).upper()
    if text in {"OK", "PASS"}:
        return "OK"
    if text in {"NG", "FAIL"}:
        return "NG"
    if text in {"NA", "NOT_APPLICABLE", "NO_APLICA"}:
        return "NA"
    if text in {"ERROR", "NOT_IMPLEMENTED"}:
        return "ERROR"
    return text


def normalize_markdown_spacing(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    while "\n\n\n" in normalized:
        normalized = normalized.replace("\n\n\n", "\n\n")
    return normalized.rstrip() + "\n"
