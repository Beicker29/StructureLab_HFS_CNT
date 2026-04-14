from __future__ import annotations

from steel_connections.domain.routing.applicability_matrix import APPLICABILITY_MATRIX, RuleBinding
from steel_connections.models.errors import ErrorCode, Stage, StructuredEngineException, StructuredError
from steel_connections.models.input import InputCase


def resolve_applicable_rules(case: InputCase) -> list[RuleBinding]:
    matches = [
        item
        for item in APPLICABILITY_MATRIX
        if item.connection_family == case.connection_family
        and item.connection_type == case.connection_type
        and item.load_state == case.load_state
    ]
    if not matches:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.ROUTING_ERROR,
                stage=Stage.ROUTE,
                rule_id=None,
                missing_fields=None,
                message=(
                    "No applicable rules found for "
                    f"{case.connection_family}/{case.connection_type}/{case.load_state}."
                ),
                source_document=None,
            )
        )
    return matches
