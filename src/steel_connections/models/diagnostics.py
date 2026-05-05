from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import Field

from steel_connections.models.units import StrictModel


class DiagnosticLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class DesignWarning(StrictModel):
    level: Literal[DiagnosticLevel.WARNING] = DiagnosticLevel.WARNING
    warning_code: str | None = None
    rule_id: str | None = None
    message: str
    source_document: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class DesignError(StrictModel):
    level: Literal[DiagnosticLevel.ERROR] = DiagnosticLevel.ERROR
    error_code: str | None = None
    stage: str | None = None
    rule_id: str | None = None
    missing_fields: list[str] | None = None
    message: str
    source_document: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
