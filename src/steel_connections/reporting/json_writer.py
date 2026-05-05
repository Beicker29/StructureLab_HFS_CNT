from __future__ import annotations

from pathlib import Path
from typing import Any

from steel_connections.models.results import DesignResult


def build_case_results_dir(
    result: Any,
    out_root: str | Path,
    *,
    example_id: str | None = None,
) -> Path:
    root = Path(out_root)
    if example_id:
        target_dir = root / Path(example_id)
    else:
        target_dir = root / result.connection_family / result.case_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def write_detailed_result(
    result: Any,
    out_root: str | Path,
    *,
    example_id: str | None = None,
) -> Path:
    target_dir = build_case_results_dir(result, out_root, example_id=example_id)
    target_path = target_dir / "detailed.json"
    target_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return target_path


def write_design_result(
    result: DesignResult,
    out_root: str | Path,
    *,
    example_id: str | None = None,
    filename: str = "design_result.json",
) -> Path:
    target_dir = build_case_results_dir(result, out_root, example_id=example_id)
    target_path = target_dir / filename
    target_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return target_path
