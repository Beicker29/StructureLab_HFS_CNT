from __future__ import annotations

import json
from pathlib import Path

from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.domain.registry import default_registry
from steel_connections.domain.strategies import (
    AISC358EndPlateStrategy,
    AISC358WufWStrategy,
    AISC360BBMBSpliceStrategy,
    DG1BasePlateStrategy,
)
from steel_connections.models.input import parse_input_case


EXAMPLE_SPLICE_PATH = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")


def test_aisc358_end_plate_strategy_supports_only_end_plate_cases(
    bseep_8es_payload: dict,
    moment_payload: dict,
) -> None:
    strategy = AISC358EndPlateStrategy()

    assert strategy.supports(parse_input_case(bseep_8es_payload))
    assert not strategy.supports(parse_input_case(moment_payload))


def test_aisc358_wufw_strategy_supports_wufw_only(moment_payload: dict, bueep_4e_payload: dict) -> None:
    strategy = AISC358WufWStrategy()

    assert strategy.supports(parse_input_case(moment_payload))
    assert not strategy.supports(parse_input_case(bueep_4e_payload))


def test_aisc360_bbmb_splice_strategy_supports_splice_case(dg1_payload: dict) -> None:
    strategy = AISC360BBMBSpliceStrategy()
    splice_payload = json.loads(EXAMPLE_SPLICE_PATH.read_text(encoding="utf-8"))

    assert strategy.supports(parse_and_validate_payload(splice_payload))
    assert not strategy.supports(parse_input_case(dg1_payload))


def test_dg1_base_plate_strategy_supports_base_plate_only(dg1_payload: dict, moment_payload: dict) -> None:
    strategy = DG1BasePlateStrategy()

    assert strategy.supports(parse_input_case(dg1_payload))
    assert not strategy.supports(parse_input_case(moment_payload))


def test_registry_evaluate_delegates_to_legacy_rule_evaluation(moment_payload: dict) -> None:
    case = parse_and_validate_payload(moment_payload)
    checks, errors = default_registry().evaluate(case)

    assert errors == []
    assert [check.rule_id for check in checks] == [
        "AISC358.07.7.2.beam_flange_tension_strength",
        "AISC358.07.7.3.flange_weld_strength",
    ]
