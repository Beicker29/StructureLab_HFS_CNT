from __future__ import annotations

from enum import Enum

from steel_connections.models.units import StrictModel


class ErrorCode(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    ROUTING_ERROR = "ROUTING_ERROR"
    MISSING_REQUIRED_INPUT = "MISSING_REQUIRED_INPUT"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class Stage(str, Enum):
    VALIDATE = "validate"
    ROUTE = "route"
    EVALUATE = "evaluate"
    EMIT = "emit"


class StructuredError(StrictModel):
    error_code: ErrorCode
    stage: Stage
    rule_id: str | None
    missing_fields: list[str] | None
    message: str
    source_document: str | None


class StructuredEngineException(Exception):
    def __init__(self, error: StructuredError):
        self.error = error
        super().__init__(error.message)


def missing_required_input_error(
    *,
    rule_id: str,
    source_document: str,
    missing_fields: list[str],
    message: str,
) -> StructuredEngineException:
    return StructuredEngineException(
        StructuredError(
            error_code=ErrorCode.MISSING_REQUIRED_INPUT,
            stage=Stage.EVALUATE,
            rule_id=rule_id,
            missing_fields=missing_fields,
            message=message,
            source_document=source_document,
        )
    )


def not_implemented_error(
    *,
    rule_id: str,
    source_document: str,
    message: str,
) -> StructuredEngineException:
    return StructuredEngineException(
        StructuredError(
            error_code=ErrorCode.NOT_IMPLEMENTED,
            stage=Stage.EVALUATE,
            rule_id=rule_id,
            missing_fields=None,
            message=message,
            source_document=source_document,
        )
    )
