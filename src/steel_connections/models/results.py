from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field, model_validator

from steel_connections.models.diagnostics import DesignError, DesignWarning
from steel_connections.models.units import Quantity, StrictModel


class CheckStatus(str, Enum):
    OK = "OK"
    NG = "NG"
    NA = "NA"
    ERROR = "ERROR"


class DesignStatus(str, Enum):
    OK = "OK"
    NG = "NG"
    ERROR = "ERROR"


class LimitStateResult(StrictModel):
    name: str
    rule_id: str
    clause: str
    source_document: str
    status: CheckStatus
    demand: Quantity | None
    capacity: Quantity | None
    dcr: float | None
    equation: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    intermediates: dict[str, Any] = Field(default_factory=dict)
    derived_values: dict[str, Any] = Field(default_factory=dict)
    design_factors: dict[str, float] = Field(default_factory=dict)
    units: dict[str, str] = Field(default_factory=dict)
    final_capacity: Quantity | None = None
    notes: str | None = None
    warnings: list[DesignWarning] = Field(default_factory=list)
    errors: list[DesignError] = Field(default_factory=list)
    na_reason: str | None = None

    @model_validator(mode="after")
    def require_na_reason(self) -> LimitStateResult:
        if self.status == CheckStatus.NA and not self.na_reason:
            raise ValueError("LimitStateResult with status NA requires na_reason.")
        return self


class DesignSummary(StrictModel):
    ok_count: int
    ng_count: int
    na_count: int
    error_count: int
    warning_count: int
    worst_dcr: float | None


class DesignResult(StrictModel):
    schema_version: str = "design-result.v1"
    project_id: str
    case_id: str
    connection_family: str
    connection_type: str
    load_state: str
    status: DesignStatus
    checks: list[LimitStateResult]
    errors: list[DesignError] = Field(default_factory=list)
    warnings: list[DesignWarning] = Field(default_factory=list)
    summary: DesignSummary
    legacy_result_type: str | None = None
