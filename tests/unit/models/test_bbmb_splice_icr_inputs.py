from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.models.input import parse_input_case


EXAMPLE_SPLICE_PATH = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")


def _base_payload() -> dict:
    raw = json.loads(EXAMPLE_SPLICE_PATH.read_text(encoding="utf-8"))
    # example can be scope-subdivided; normalize to canonical model payload for parse_input_case tests
    return parse_and_validate_payload(raw).model_dump()


@pytest.mark.parametrize(
    "method_raw, expected",
    [
        ("Elastic Method - Superposition", "elastic_superposition"),
        ("Elastic Method - Center of Rotation", "elastic_ecr"),
        ("Instant Center of Rotation Method", "icr"),
        ("nstant Center of Rotation Method continua", "icr"),
    ],
)
def test_parse_splice_method_aliases(method_raw: str, expected: str) -> None:
    payload = _base_payload()
    payload["procedure"]["icr"]["method"] = method_raw
    if expected != "icr":
        payload["procedure"]["icr"].pop("rult_1_kip", None)
    case = parse_input_case(payload)
    assert case.procedure is not None
    assert case.procedure.icr.method == expected


def test_parse_splice_icr_requires_rult() -> None:
    payload = _base_payload()
    payload["procedure"]["icr"]["method"] = "icr"
    payload["procedure"]["icr"].pop("rult_1_kip", None)
    with pytest.raises(ValidationError):
        parse_input_case(payload)


def test_parse_splice_icr_allows_rult_unit_kip() -> None:
    payload = _base_payload()
    payload["procedure"]["icr"]["method"] = "icr"
    payload["procedure"]["icr"]["rult_1_kip"] = {"value": 20.0, "unit": "kip"}
    case = parse_input_case(payload)
    assert case.procedure is not None
    assert case.procedure.icr.rult_1_kip is not None
    assert case.procedure.icr.rult_1_kip.unit == "kip"


def test_parse_splice_elastic_does_not_require_rult() -> None:
    payload = deepcopy(_base_payload())
    payload["procedure"]["icr"]["method"] = "elastic_ecr"
    payload["procedure"]["icr"].pop("rult_1_kip", None)
    case = parse_input_case(payload)
    assert case.procedure is not None
    assert case.procedure.icr.method == "elastic_ecr"
