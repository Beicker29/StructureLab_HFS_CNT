from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from steel_connections.models.raw_input import InputSource, InputSourceKind, RawInput


def raw_input_from_mapping(
    payload: dict[str, Any],
    *,
    source_path: str | Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> RawInput:
    path_text = str(source_path) if source_path is not None else None
    source = InputSource(
        kind=InputSourceKind.LEGACY_PAYLOAD,
        path=path_text,
        files=[path_text] if path_text else [],
    )
    return RawInput.from_mapping(payload, source=source, metadata=metadata)


def load_json_raw_input(path: str | Path) -> RawInput:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8-sig") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON input must contain an object at top level: {input_path}")
    source = InputSource(
        kind=InputSourceKind.JSON_FILE,
        path=str(input_path),
        files=[str(input_path)],
        encoding="utf-8-sig",
    )
    return RawInput.from_mapping(deepcopy(payload), source=source)
