from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class NumericTolerance:
    relative: float = 1e-6
    absolute: float = 0.0


TOLERANCES: dict[str, NumericTolerance] = {
    "force": NumericTolerance(relative=1e-6, absolute=1e-6),
    "moment": NumericTolerance(relative=1e-6, absolute=1e-3),
    "length": NumericTolerance(relative=0.0, absolute=1e-6),
    "thickness": NumericTolerance(relative=0.0, absolute=1e-6),
    "stress": NumericTolerance(relative=1e-6, absolute=1e-6),
    "ratio": NumericTolerance(relative=0.0, absolute=1e-6),
    "dcr": NumericTolerance(relative=0.0, absolute=1e-6),
}


UNIT_KINDS: dict[str, str] = {
    "N": "force",
    "kN": "force",
    "kip": "force",
    "N-mm": "moment",
    "kN-mm": "moment",
    "kN-m": "moment",
    "kip-in": "moment",
    "mm": "length",
    "in": "length",
    "MPa": "stress",
    "ksi": "stress",
    "ratio": "ratio",
}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def infer_quantity_kind(quantity: Mapping[str, Any]) -> str:
    unit = str(quantity.get("unit", ""))
    if unit not in UNIT_KINDS:
        raise AssertionError(f"Unsupported quantity unit for golden comparison: {unit!r}")
    return UNIT_KINDS[unit]


def assert_close_number(
    actual: float,
    expected: float,
    *,
    kind: str,
    context: str = "",
    tolerance: NumericTolerance | None = None,
) -> None:
    tol = tolerance or TOLERANCES[kind]
    if not math.isfinite(actual) or not math.isfinite(expected):
        raise AssertionError(f"Non-finite value at {context}: actual={actual}, expected={expected}")
    if math.isclose(actual, expected, rel_tol=tol.relative, abs_tol=tol.absolute):
        return
    diff = actual - expected
    raise AssertionError(
        f"Numeric mismatch at {context}: actual={actual}, expected={expected}, "
        f"diff={diff}, rel_tol={tol.relative}, abs_tol={tol.absolute}, kind={kind}"
    )


def assert_close_quantity(
    actual: Mapping[str, Any] | None,
    expected: Mapping[str, Any] | None,
    *,
    context: str = "",
) -> None:
    if actual is None or expected is None:
        if actual != expected:
            raise AssertionError(f"Quantity presence mismatch at {context}: actual={actual}, expected={expected}")
        return
    actual_unit = actual.get("unit")
    expected_unit = expected.get("unit")
    if actual_unit != expected_unit:
        raise AssertionError(f"Quantity unit mismatch at {context}: actual={actual_unit}, expected={expected_unit}")
    kind = infer_quantity_kind(expected)
    assert_close_number(float(actual["value"]), float(expected["value"]), kind=kind, context=context)


def assert_same_check_numeric(actual_check: Mapping[str, Any], expected_check: Mapping[str, Any]) -> None:
    rule_id = str(expected_check.get("rule_id", "<unknown_rule>"))
    if actual_check.get("rule_id") != expected_check.get("rule_id"):
        raise AssertionError(f"Rule id mismatch: actual={actual_check.get('rule_id')}, expected={rule_id}")
    if actual_check.get("status") != expected_check.get("status"):
        raise AssertionError(
            f"Status mismatch for {rule_id}: actual={actual_check.get('status')}, expected={expected_check.get('status')}"
        )
    assert_close_quantity(actual_check.get("demand"), expected_check.get("demand"), context=f"{rule_id}.demand")
    assert_close_quantity(actual_check.get("capacity"), expected_check.get("capacity"), context=f"{rule_id}.capacity")
    actual_dcr = actual_check.get("dcr")
    expected_dcr = expected_check.get("dcr")
    if actual_dcr is None or expected_dcr is None:
        if actual_dcr != expected_dcr:
            raise AssertionError(f"DCR presence mismatch for {rule_id}: actual={actual_dcr}, expected={expected_dcr}")
    else:
        assert_close_number(float(actual_dcr), float(expected_dcr), kind="dcr", context=f"{rule_id}.dcr")


def assert_same_detailed_result_numeric(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    for key in ("project_id", "case_id", "connection_family", "connection_type", "load_state", "global_status"):
        if actual.get(key) != expected.get(key):
            raise AssertionError(f"Detailed result metadata mismatch for {key}: {actual.get(key)} != {expected.get(key)}")
    actual_checks = actual.get("checks", [])
    expected_checks = expected.get("checks", [])
    if len(actual_checks) != len(expected_checks):
        raise AssertionError(f"Check count mismatch: actual={len(actual_checks)}, expected={len(expected_checks)}")
    for index, (actual_check, expected_check) in enumerate(zip(actual_checks, expected_checks), start=1):
        assert_same_check_numeric(actual_check, expected_check)
    actual_summary = actual.get("summary", {})
    expected_summary = expected.get("summary", {})
    for key in ("pass_count", "fail_count", "error_count", "not_implemented_count"):
        if actual_summary.get(key) != expected_summary.get(key):
            raise AssertionError(f"Summary mismatch for {key}: {actual_summary.get(key)} != {expected_summary.get(key)}")
    if actual_summary.get("worst_dcr") is not None or expected_summary.get("worst_dcr") is not None:
        assert_close_number(
            float(actual_summary["worst_dcr"]),
            float(expected_summary["worst_dcr"]),
            kind="dcr",
            context="summary.worst_dcr",
        )


def compare_detailed_json_files(actual_path: str | Path, expected_path: str | Path) -> None:
    assert_same_detailed_result_numeric(load_json(actual_path), load_json(expected_path))


def normalize_report_text(text: str, *, normalize_whitespace: bool = False) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if normalize_whitespace:
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized


def compare_report_text(
    actual_text: str,
    expected_text: str,
    *,
    normalize_whitespace: bool = False,
) -> None:
    actual = normalize_report_text(actual_text, normalize_whitespace=normalize_whitespace)
    expected = normalize_report_text(expected_text, normalize_whitespace=normalize_whitespace)
    if actual != expected:
        raise AssertionError("Report text mismatch. Whitespace normalization does not hide content changes.")


def compare_report_files(
    actual_path: str | Path,
    expected_path: str | Path,
    *,
    normalize_whitespace: bool = False,
) -> None:
    compare_report_text(
        Path(actual_path).read_text(encoding="utf-8-sig"),
        Path(expected_path).read_text(encoding="utf-8-sig"),
        normalize_whitespace=normalize_whitespace,
    )
