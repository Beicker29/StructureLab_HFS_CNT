from __future__ import annotations

import pytest

from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.domain.routing.applicability_matrix import APPLICABILITY_MATRIX
from steel_connections.domain.rules.aisc358.beam_flange_tension import run
from steel_connections.models.errors import ErrorCode, StructuredEngineException


def test_beam_flange_tension_rule_missing_input_fails_hard(moment_payload: dict) -> None:
    moment_payload["geometry"]["beam_flange_area"] = None
    case = parse_and_validate_payload(moment_payload)
    binding = next(
        item
        for item in APPLICABILITY_MATRIX
        if item.rule_id == "AISC358.07.7.2.beam_flange_tension_strength"
    )
    with pytest.raises(StructuredEngineException) as exc_info:
        run(case, binding)
    assert exc_info.value.error.error_code == ErrorCode.MISSING_REQUIRED_INPUT


def test_beam_flange_tension_rule_returns_check_result(moment_payload: dict) -> None:
    case = parse_and_validate_payload(moment_payload)
    binding = next(
        item
        for item in APPLICABILITY_MATRIX
        if item.rule_id == "AISC358.07.7.2.beam_flange_tension_strength"
    )
    result = run(case, binding)
    assert result.rule_id == binding.rule_id
    assert result.dcr is not None
