from __future__ import annotations

import pytest
from pydantic import ValidationError

from steel_connections.models.input import parse_input_case


def test_parse_moment_case_valid(moment_payload: dict) -> None:
    case = parse_input_case(moment_payload)
    assert case.connection_family == "moment_prequalified"
    assert case.connection_type == "wuf_w"
    assert case.units_system.value == "US"


def test_invalid_unit_rejected(moment_payload: dict) -> None:
    moment_payload["materials"]["weld_fexx"]["unit"] = "MPa"
    with pytest.raises(ValidationError):
        parse_input_case(moment_payload)


def test_missing_required_top_level_rejected(moment_payload: dict) -> None:
    del moment_payload["loads"]
    with pytest.raises(ValidationError):
        parse_input_case(moment_payload)


def test_manual_beam_profile_geometry_is_rejected(moment_payload: dict) -> None:
    moment_payload["geometry"]["beam_depth"] = {"value": 24.0, "unit": "in"}
    with pytest.raises(ValidationError):
        parse_input_case(moment_payload)
