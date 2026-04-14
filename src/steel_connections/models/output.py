from __future__ import annotations

from enum import Enum
from typing import Any

from steel_connections.models.errors import StructuredError
from steel_connections.models.units import Quantity, StrictModel


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class GlobalStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class CalculationMemory(StrictModel):
    inputs: dict[str, Any]
    intermediates: dict[str, Any]
    design_factors: dict[str, float]
    equation: str
    units_trace: dict[str, str]
    final_capacity: Quantity | None


class CheckResult(StrictModel):
    name: str
    rule_id: str
    clause: str
    source_document: str
    demand: Quantity | None
    capacity: Quantity | None
    dcr: float | None
    status: CheckStatus
    calculation_memory: CalculationMemory
    notes: str | None


class RunSummary(StrictModel):
    pass_count: int
    fail_count: int
    error_count: int
    not_implemented_count: int
    worst_dcr: float | None


class DetailedRunResult(StrictModel):
    project_id: str
    case_id: str
    connection_family: str
    connection_type: str
    load_state: str
    global_status: GlobalStatus
    checks: list[CheckResult]
    errors: list[StructuredError]
    summary: RunSummary
