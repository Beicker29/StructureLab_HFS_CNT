from __future__ import annotations

from steel_connections.domain.registry import default_registry
from steel_connections.domain.routing.applicability_matrix import RuleBinding
from steel_connections.models.input import InputCase


def resolve_applicable_rules(case: InputCase) -> list[RuleBinding]:
    return default_registry().applicable_rules(case)
