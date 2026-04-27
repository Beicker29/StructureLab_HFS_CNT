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
    if (
        case.connection_family == "moment_prequalified"
        and hasattr(case, "design_factors")
        and getattr(case.design_factors, "beam_connection_sides", None) is not None
    ):
        sides = str(case.design_factors.beam_connection_sides)
        filtered: list[RuleBinding] = []
        for item in matches:
            rule_id = str(item.rule_id).lower()
            if rule_id.endswith("_vgizq") and sides not in {"left_only", "both_sides"}:
                continue
            if rule_id.endswith("_vgder") and sides not in {"right_only", "both_sides"}:
                continue
            filtered.append(item)
        matches = filtered
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
