from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}, got {type(payload).__name__}.")
    return payload


def _require_dict(parent: dict[str, Any], key: str, context: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Missing object '{key}' in {context}.")
    return value


def _assert_equal(right_value: Any, left_value: Any, label: str) -> None:
    if right_value != left_value:
        raise ValueError(
            f"Mismatch between right and left beam inputs for '{label}'. "
            "Both sides must define the same geometry values."
        )


def main() -> None:
    here = Path(__file__).resolve().parent
    base_path = here / "case_003_column_and_common.json"
    beam_right_path = here / "case_003_beam_right_only.json"
    beam_left_path = here / "case_003_beam_left_only.json"
    output_path = here.parent / "case_003_bseep_8es.json"

    merged = _read_json(base_path)
    right_payload = _read_json(beam_right_path)
    left_payload = _read_json(beam_left_path)

    merged_geometry = _require_dict(merged, "geometry", "case_003_column_and_common.json")
    right_geometry = _require_dict(right_payload, "geometry", "case_003_beam_right_only.json")
    left_geometry = _require_dict(left_payload, "geometry", "case_003_beam_left_only.json")

    merged_geometry["beam_right"] = _require_dict(right_geometry, "beam_right", "case_003_beam_right_only.json.geometry")
    merged_geometry["beam_left"] = _require_dict(left_geometry, "beam_left", "case_003_beam_left_only.json.geometry")

    for group_name in ("end_plate", "continuity_plate", "stiffener", "bolts"):
        right_group = _require_dict(right_geometry, group_name, "case_003_beam_right_only.json.geometry")
        left_group = _require_dict(left_geometry, group_name, "case_003_beam_left_only.json.geometry")
        _assert_equal(right_group, left_group, f"geometry.{group_name}")
        merged_geometry[group_name] = right_group

    right_welds = _require_dict(right_geometry, "welds", "case_003_beam_right_only.json.geometry")
    left_welds = _require_dict(left_geometry, "welds", "case_003_beam_left_only.json.geometry")
    base_welds = _require_dict(merged_geometry, "welds", "case_003_column_and_common.json.geometry")
    weld_4 = _require_dict(base_welds, "weld_4", "case_003_column_and_common.json.geometry.welds")

    merged_welds: dict[str, Any] = {"weld_4": weld_4}
    for weld_name in ("weld_1", "weld_2", "weld_3"):
        right_weld = _require_dict(right_welds, weld_name, "case_003_beam_right_only.json.geometry.welds")
        left_weld = _require_dict(left_welds, weld_name, "case_003_beam_left_only.json.geometry.welds")
        _assert_equal(right_weld, left_weld, f"geometry.welds.{weld_name}")
        merged_welds[weld_name] = right_weld
    merged_geometry["welds"] = merged_welds

    merged_loads = dict(_require_dict(merged, "loads", "case_003_column_and_common.json"))
    merged_loads.update(_require_dict(right_payload, "loads", "case_003_beam_right_only.json"))
    merged_loads.update(_require_dict(left_payload, "loads", "case_003_beam_left_only.json"))
    merged["loads"] = merged_loads

    with output_path.open("w", encoding="utf-8") as stream:
        json.dump(merged, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    print(f"Case assembled successfully: {output_path}")


if __name__ == "__main__":
    main()
