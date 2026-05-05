from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import Any

from pydantic import Field, model_validator

from steel_connections.models.units import StrictModel


class InputSourceKind(str, Enum):
    JSON_FILE = "json_file"
    SPLIT_INPUTS = "split_inputs"
    LEGACY_PAYLOAD = "legacy_payload"


class InputSource(StrictModel):
    kind: InputSourceKind
    path: str | None = None
    files: list[str] = Field(default_factory=list)
    encoding: str | None = None


class RawInput(StrictModel):
    schema_version: str = "raw-input.v1"
    source: InputSource
    payload: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def ensure_payload_is_mapping(self) -> "RawInput":
        if not isinstance(self.payload, dict):
            raise ValueError("RawInput.payload must be a dictionary.")
        return self

    @classmethod
    def from_mapping(
        cls,
        payload: dict[str, Any],
        *,
        source: InputSource,
        metadata: dict[str, Any] | None = None,
    ) -> "RawInput":
        return cls(
            source=source,
            payload=deepcopy(payload),
            metadata=deepcopy(metadata or {}),
        )

    def payload_copy(self) -> dict[str, Any]:
        return deepcopy(self.payload)
