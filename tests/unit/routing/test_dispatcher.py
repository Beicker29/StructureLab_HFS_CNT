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
    assert len(rules) == 13
    assert all(rule.rule_id.startswith("AISC358.06.") for rule in rules)
    assert any(".step2_probable_moment_plastic_hinge" in rule.rule_id for rule in rules)
    assert any(".step3_plastic_hinge_distance" in rule.rule_id for rule in rules)
    assert any(".step4_shear_at_plastic_hinge" in rule.rule_id for rule in rules)
    assert any(".step5_probable_moment_face_column" in rule.rule_id for rule in rules)
    assert any(".step6_1_bolt_tension_rupture" in rule.rule_id for rule in rules)
    assert any(".step6_2_bolt_shear_rupture" in rule.rule_id for rule in rules)
    assert any(".step7_1_1_end_plate_flexural_yielding" in rule.rule_id for rule in rules)
    assert any(".step7_2_1_end_plate_shear_yielding" in rule.rule_id for rule in rules)
    assert any(".step7_2_2_end_plate_shear_rupture" in rule.rule_id for rule in rules)


def test_dispatcher_resolves_bseep_rules(bseep_8es_payload: dict) -> None:
    case = parse_input_case(bseep_8es_payload)
    rules = resolve_applicable_rules(case)
    assert len(rules) == 16
    assert all(rule.rule_id.startswith("AISC358.06.") for rule in rules)
    assert any(".step2_probable_moment_plastic_hinge" in rule.rule_id for rule in rules)
    assert any(".step3_plastic_hinge_distance" in rule.rule_id for rule in rules)
    assert any(".step4_shear_at_plastic_hinge" in rule.rule_id for rule in rules)
    assert any(".step5_probable_moment_face_column" in rule.rule_id for rule in rules)
    assert any(".step6_1_bolt_tension_rupture" in rule.rule_id for rule in rules)
    assert any(".step6_2_bolt_shear_rupture" in rule.rule_id for rule in rules)
    assert any(".step7_1_1_end_plate_flexural_yielding" in rule.rule_id for rule in rules)
    assert any(".step7_2_1_end_plate_shear_yielding" in rule.rule_id for rule in rules)
    assert any(".step7_2_2_end_plate_shear_rupture" in rule.rule_id for rule in rules)


def test_dispatcher_resolves_bseep_4es_rules(bseep_4es_payload: dict) -> None:
    case = parse_input_case(bseep_4es_payload)
    rules = resolve_applicable_rules(case)
    assert len(rules) == 16
    assert all(rule.rule_id.startswith("AISC358.06.") for rule in rules)
    assert any(".step2_probable_moment_plastic_hinge" in rule.rule_id for rule in rules)
    assert any(".step3_plastic_hinge_distance" in rule.rule_id for rule in rules)
    assert any(".step4_shear_at_plastic_hinge" in rule.rule_id for rule in rules)
    assert any(".step5_probable_moment_face_column" in rule.rule_id for rule in rules)
    assert any(".step6_1_bolt_tension_rupture" in rule.rule_id for rule in rules)
    assert any(".step6_2_bolt_shear_rupture" in rule.rule_id for rule in rules)
    assert any(".step7_1_1_end_plate_flexural_yielding" in rule.rule_id for rule in rules)
    assert any(".step7_2_1_end_plate_shear_yielding" in rule.rule_id for rule in rules)
    assert any(".step7_2_2_end_plate_shear_rupture" in rule.rule_id for rule in rules)
