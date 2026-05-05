from __future__ import annotations

from pathlib import Path

from steel_connections.adapters.json_input import raw_input_from_mapping
from steel_connections.domain.engine.validate import load_input_payload, parse_and_validate_payload
from steel_connections.models.design_input import DesignInput
from steel_connections.models.raw_input import InputSource, InputSourceKind, RawInput
from steel_connections.models.resolved_input import ResolvedInput, ResolvedValueSource


def resolve_raw_input(raw_input: RawInput) -> ResolvedInput:
    case = parse_and_validate_payload(raw_input.payload_copy())
    return ResolvedInput.from_legacy_case(
        raw_input=raw_input,
        legacy_case=case,
        resolver="steel_connections.domain.engine.validate.parse_and_validate_payload",
        derived_sources=[
            ResolvedValueSource(
                field_path="*",
                source_type="legacy_resolver",
                source_name="steel_connections.domain.engine.validate.parse_and_validate_payload",
                source_detail={
                    "catalogs": ["data/materials.xlsx", "data/sections.xlsx"],
                    "note": "Phase 3 bridge; field-level catalog provenance is deferred to Phase 4.",
                },
            )
        ],
    )


def build_design_input(resolved_input: ResolvedInput) -> DesignInput:
    return DesignInput.from_resolved_input(resolved_input)


def design_input_from_raw(raw_input: RawInput) -> DesignInput:
    return build_design_input(resolve_raw_input(raw_input))


def load_legacy_raw_input(path: str | Path) -> RawInput:
    payload = load_input_payload(path)
    input_path = Path(path)
    source = InputSource(
        kind=InputSourceKind.LEGACY_PAYLOAD,
        path=str(input_path),
        files=[str(input_path)],
        encoding="utf-8-sig",
    )
    return RawInput.from_mapping(
        payload,
        source=source,
        metadata={"loader": "steel_connections.domain.engine.validate.load_input_payload"},
    )


def load_legacy_design_input(path: str | Path) -> DesignInput:
    return design_input_from_raw(load_legacy_raw_input(path))


def design_input_from_payload(payload: dict) -> DesignInput:
    return design_input_from_raw(raw_input_from_mapping(payload))
