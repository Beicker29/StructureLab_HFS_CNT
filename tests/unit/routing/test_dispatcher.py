from __future__ import annotations

from steel_connections.domain.routing.dispatcher import resolve_applicable_rules
from steel_connections.models.input import parse_input_case


def test_dispatcher_resolves_aisc358_rules(moment_payload: dict) -> None:
    case = parse_input_case(moment_payload)
    rules = resolve_applicable_rules(case)
    assert len(rules) == 2
    assert rules[0].rule_id.startswith("AISC358.")


def test_dispatcher_resolves_dg1_rule(dg1_payload: dict) -> None:
    case = parse_input_case(dg1_payload)
    rules = resolve_applicable_rules(case)
    assert len(rules) == 1
    assert rules[0].rule_id.startswith("DG1.")


def test_dispatcher_resolves_bueep_rules(bueep_4e_payload: dict) -> None:
    case = parse_input_case(bueep_4e_payload)
    rules = resolve_applicable_rules(case)
    assert len(rules) == 28
    assert all(rule.rule_id.startswith("AISC358.06.") for rule in rules)


def test_dispatcher_resolves_bseep_rules(bseep_8es_payload: dict) -> None:
    case = parse_input_case(bseep_8es_payload)
    rules = resolve_applicable_rules(case)
    assert len(rules) == 29
    assert all(rule.rule_id.startswith("AISC358.06.") for rule in rules)


def test_dispatcher_resolves_bseep_4es_rules(bseep_4es_payload: dict) -> None:
    case = parse_input_case(bseep_4es_payload)
    rules = resolve_applicable_rules(case)
    assert len(rules) == 29
    assert all(rule.rule_id.startswith("AISC358.06.") for rule in rules)
