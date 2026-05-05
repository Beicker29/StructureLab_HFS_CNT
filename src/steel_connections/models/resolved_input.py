from __future__ import annotations

from typing import Any

from pydantic import Field

from steel_connections.models.input import InputCase
from steel_connections.models.raw_input import InputSource, RawInput
from steel_connections.models.units import StrictModel


class ResolvedValueSource(StrictModel):
    field_path: str
    source_type: str
    source_name: str
    source_detail: dict[str, Any] = Field(default_factory=dict)


class ResolvedInput(StrictModel):
    schema_version: str = "resolved-input.v1"
    raw_source: InputSource
    raw_input: RawInput
    legacy_case: InputCase
    resolved_payload: dict[str, Any]
    resolver: str
    derived_sources: list[ResolvedValueSource] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @classmethod
    def from_legacy_case(
        cls,
        *,
        raw_input: RawInput,
        legacy_case: InputCase,
        resolver: str,
        derived_sources: list[ResolvedValueSource] | None = None,
        warnings: list[str] | None = None,
    ) -> "ResolvedInput":
        return cls(
            raw_source=raw_input.source,
            raw_input=raw_input,
            legacy_case=legacy_case,
            resolved_payload=legacy_case.model_dump(mode="json"),
            resolver=resolver,
            derived_sources=derived_sources or [],
            warnings=warnings or [],
        )
