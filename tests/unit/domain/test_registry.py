from __future__ import annotations

from steel_connections.domain.registry import default_registry
from steel_connections.domain.routing.applicability_matrix import APPLICABILITY_MATRIX
from steel_connections.domain.routing.dispatcher import resolve_applicable_rules
from steel_connections.models.input import InputCase, parse_input_case


def _legacy_matrix_rule_ids(case: InputCase) -> list[str]:
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
        filtered = []
        for item in matches:
            rule_id = str(item.rule_id).lower()
            if rule_id.endswith("_vgizq") and sides not in {"left_only", "both_sides"}:
                continue
            if rule_id.endswith("_vgder") and sides not in {"right_only", "both_sides"}:
                continue
            filtered.append(item)
        matches = filtered
    return [item.rule_id for item in matches]


def test_default_registry_contains_legacy_strategies() -> None:
    registry = default_registry()

    assert [strategy.strategy_id for strategy in registry.strategies] == [
        "aisc358.wuf_w",
        "aisc358.end_plate",
        "aisc360.bbmb_splice",
        "dg1.base_plate",
    ]


def test_registry_preserves_legacy_rule_order_for_wufw(moment_payload: dict) -> None:
    case = parse_input_case(moment_payload)

    assert [rule.rule_id for rule in default_registry().applicable_rules(case)] == _legacy_matrix_rule_ids(case)


def test_registry_preserves_legacy_rule_order_for_end_plate(bseep_8es_payload: dict) -> None:
    case = parse_input_case(bseep_8es_payload)

    assert [rule.rule_id for rule in default_registry().applicable_rules(case)] == _legacy_matrix_rule_ids(case)


def test_dispatcher_uses_registry_compatibility_path(bueep_4e_payload: dict) -> None:
    case = parse_input_case(bueep_4e_payload)

    registry_rules = default_registry().applicable_rules(case)
    dispatcher_rules = resolve_applicable_rules(case)

    assert [rule.rule_id for rule in dispatcher_rules] == [rule.rule_id for rule in registry_rules]


def test_registry_filters_side_specific_rules_like_legacy_dispatcher(bseep_8es_payload: dict) -> None:
    bseep_8es_payload["design_factors"]["beam_connection_sides"] = "left_only"
    case = parse_input_case(bseep_8es_payload)
    rules = default_registry().applicable_rules(case)

    assert all(not rule.rule_id.endswith("_vgder") for rule in rules)
    assert any(rule.rule_id.endswith("_vgizq") for rule in rules)
