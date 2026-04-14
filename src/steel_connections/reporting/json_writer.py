from __future__ import annotations

from pathlib import Path

from steel_connections.models.output import DetailedRunResult


def build_case_results_dir(
    result: DetailedRunResult,
    out_root: str | Path,
    *,
    example_id: str | None = None,
) -> Path:
    root = Path(out_root)
    if example_id:
        target_dir = root / example_id
    else:
        target_dir = root / result.connection_family / result.case_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def write_detailed_result(
    result: DetailedRunResult,
    out_root: str | Path,
    *,
    example_id: str | None = None,
) -> Path:
    target_dir = build_case_results_dir(result, out_root, example_id=example_id)
    target_path = target_dir / "detailed.json"
    target_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return target_path
