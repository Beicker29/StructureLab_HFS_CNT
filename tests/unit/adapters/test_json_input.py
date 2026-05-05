from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from steel_connections.adapters.json_input import load_json_raw_input
from steel_connections.adapters.legacy_input import design_input_from_raw
from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.models.raw_input import InputSourceKind


BBMB_CASE = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")
BOM_COLUMN_FILE = Path("examples/moment_prequalified/case_003_bseep_8es_split_inputs/case_003_column_and_common.json")


def test_json_raw_input_reads_utf8_sig_without_normalizing_payload() -> None:
    raw = load_json_raw_input(BOM_COLUMN_FILE)

    assert raw.source.kind == InputSourceKind.JSON_FILE
    assert raw.source.encoding == "utf-8-sig"
    assert "platina_enchape_alma" in raw.payload
    assert raw.payload["platina_enchape_alma"]["n_dp_col"] == 2


def test_json_design_input_does_not_mutate_raw_payload() -> None:
    raw = load_json_raw_input(BBMB_CASE)
    before = deepcopy(raw.payload)

    design_input = design_input_from_raw(raw)

    assert raw.payload == before
    assert design_input.connection_family == "Fully_Restrained_Moment"
    assert design_input.connection_type == "bbmb_splice"
    assert design_input.calculation_units_policy == "legacy_units_preserved_phase3"


def test_json_design_input_matches_legacy_validator_output() -> None:
    raw = load_json_raw_input(BBMB_CASE)

    design_input = design_input_from_raw(raw)
    legacy_case = parse_and_validate_payload(raw.payload_copy())

    assert design_input.to_legacy_case().model_dump(mode="json") == legacy_case.model_dump(mode="json")
    assert design_input.payload == legacy_case.model_dump(mode="json")
