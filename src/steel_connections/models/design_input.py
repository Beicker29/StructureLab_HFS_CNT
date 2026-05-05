from __future__ import annotations

from typing import Any

from pydantic import Field

from steel_connections.models.input import InputCase
from steel_connections.models.resolved_input import ResolvedInput
from steel_connections.models.units import StrictModel


class DesignInput(StrictModel):
    schema_version: str = "design-input.v1"
    project_id: str
    case_id: str
    connection_family: str
    connection_type: str
    load_state: str
    units_system: str
    calculation_units_policy: str = "legacy_units_preserved_phase3"
    internal_units: dict[str, str] = Field(
        default_factory=lambda: {
            "force": "legacy_case_units",
            "length": "legacy_case_units",
            "stress": "legacy_case_units",
            "moment": "legacy_case_units",
        }
    )
    resolved_input: ResolvedInput
    legacy_case: InputCase
    payload: dict[str, Any]

    @classmethod
    def from_resolved_input(cls, resolved_input: ResolvedInput) -> "DesignInput":
        case = resolved_input.legacy_case
        return cls(
            project_id=case.project_id,
            case_id=case.case_id,
            connection_family=case.connection_family,
            connection_type=case.connection_type,
            load_state=case.load_state,
            units_system=case.units_system.value,
            resolved_input=resolved_input,
            legacy_case=case,
            payload=case.model_dump(mode="json"),
        )

    def to_legacy_case(self) -> InputCase:
        return self.legacy_case
