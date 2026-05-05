from __future__ import annotations

from pathlib import Path
from typing import Any

from steel_connections.domain.engine.validate import (
    _canonical_beam_connection_sides,
    _compose_moment_prequalified_split_payload,
    _read_json_object,
    _resolve_moment_prequalified_split_paths,
)
from steel_connections.models.design_input import DesignInput
from steel_connections.models.raw_input import InputSource, InputSourceKind, RawInput
from steel_connections.models.resolved_input import ResolvedInput
from steel_connections.adapters.legacy_input import build_design_input, resolve_raw_input


def _split_file_payload(path: Path | None) -> dict[str, Any] | None:
    return _read_json_object(path) if path is not None else None


def load_split_raw_input(path: str | Path) -> RawInput:
    input_path = Path(path)
    split_paths = _resolve_moment_prequalified_split_paths(input_path)
    if split_paths is None:
        raise ValueError(f"Input path is not a moment prequalified split-input bundle: {input_path}")

    column_path, right_path, left_path = split_paths
    column_raw = _read_json_object(column_path)
    right_raw = _split_file_payload(right_path)
    left_raw = _split_file_payload(left_path)

    design_factors_raw = column_raw.get("design_factors")
    if not isinstance(design_factors_raw, dict):
        design_factors_raw = column_raw.get("factores_diseno")
    beam_connection_sides = _canonical_beam_connection_sides(
        design_factors_raw.get("beam_connection_sides")
        if isinstance(design_factors_raw, dict) and design_factors_raw.get("beam_connection_sides") is not None
        else design_factors_raw.get("lados_conexion") if isinstance(design_factors_raw, dict) else None
    )
    if beam_connection_sides is None:
        raise ValueError("Split input bundle is missing a valid beam_connection_sides value.")

    files = [str(column_path)]
    if right_path is not None:
        files.append(str(right_path))
    if left_path is not None:
        files.append(str(left_path))
    source = InputSource(
        kind=InputSourceKind.SPLIT_INPUTS,
        path=str(input_path),
        files=files,
        encoding="utf-8-sig",
    )
    payload = {
        "column_and_common": column_raw,
        "beam_right": right_raw,
        "beam_left": left_raw,
    }
    return RawInput.from_mapping(
        payload,
        source=source,
        metadata={"beam_connection_sides": beam_connection_sides},
    )


def compose_split_payload(raw_input: RawInput) -> dict[str, Any]:
    if raw_input.source.kind != InputSourceKind.SPLIT_INPUTS:
        raise ValueError("compose_split_payload expects RawInput with source.kind='split_inputs'.")
    beam_connection_sides = raw_input.metadata.get("beam_connection_sides")
    if not isinstance(beam_connection_sides, str):
        raise ValueError("Split RawInput metadata is missing beam_connection_sides.")
    return _compose_moment_prequalified_split_payload(
        column_raw=raw_input.payload["column_and_common"],
        right_raw=raw_input.payload.get("beam_right"),
        left_raw=raw_input.payload.get("beam_left"),
        beam_connection_sides=beam_connection_sides,
    )


def resolve_split_input(raw_input: RawInput) -> ResolvedInput:
    composed_payload = compose_split_payload(raw_input)
    composed_raw = RawInput.from_mapping(
        composed_payload,
        source=InputSource(
            kind=InputSourceKind.LEGACY_PAYLOAD,
            path=raw_input.source.path,
            files=raw_input.source.files,
            encoding=raw_input.source.encoding,
        ),
        metadata={
            "composed_from": "split_inputs",
            "beam_connection_sides": raw_input.metadata.get("beam_connection_sides"),
        },
    )
    return resolve_raw_input(composed_raw)


def load_split_design_input(path: str | Path) -> DesignInput:
    return build_design_input(resolve_split_input(load_split_raw_input(path)))
