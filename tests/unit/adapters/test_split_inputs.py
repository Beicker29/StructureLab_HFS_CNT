from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from steel_connections.adapters.split_inputs import (
    compose_split_payload,
    load_split_design_input,
    load_split_raw_input,
    resolve_split_input,
)
from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.domain.engine.validate import parse_and_validate_file
from steel_connections.models.raw_input import InputSourceKind
from tests.helpers.golden_compare import assert_same_detailed_result_numeric, load_json


APPROVED_SPLIT = Path("examples/moment_prequalified/case_003_bseep_8es_split_inputs")
OBSERVED_4ES_SPLIT = Path("examples/moment_prequalified/case_004_bseep_4es_split_inputs")
APPROVED_GOLDEN = Path("tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json")


def test_split_raw_input_preserves_user_files_before_composition() -> None:
    raw = load_split_raw_input(APPROVED_SPLIT)

    assert raw.source.kind == InputSourceKind.SPLIT_INPUTS
    assert raw.metadata["beam_connection_sides"] == "both_sides"
    assert "column_and_common" in raw.payload
    assert "beam_right" in raw.payload
    assert "beam_left" in raw.payload
    assert "platina_enchape_alma" in raw.payload["column_and_common"]
    assert raw.payload["column_and_common"]["platina_enchape_alma"]["n_dp_col"] == 2


def test_split_resolve_does_not_mutate_raw_input() -> None:
    raw = load_split_raw_input(APPROVED_SPLIT)
    before = deepcopy(raw.payload)

    resolved = resolve_split_input(raw)

    assert raw.payload == before
    assert resolved.legacy_case.connection_family == "moment_prequalified"
    assert resolved.legacy_case.connection_type == "bseep_8es"


def test_split_design_input_matches_legacy_validator_output() -> None:
    design_input = load_split_design_input(APPROVED_SPLIT)
    legacy_case = parse_and_validate_file(APPROVED_SPLIT)

    assert design_input.to_legacy_case().model_dump(mode="json") == legacy_case.model_dump(mode="json")
    assert design_input.connection_type == "bseep_8es"
    assert design_input.legacy_case.sections.beam_shape == "W21X68"


def test_split_composed_payload_preserves_approved_golden_numbers() -> None:
    raw = load_split_raw_input(APPROVED_SPLIT)
    result = run_case_payload(compose_split_payload(raw))

    assert_same_detailed_result_numeric(
        result.model_dump(mode="json"),
        load_json(APPROVED_GOLDEN),
    )


def test_split_design_input_normalizes_disabled_doubler_plate_without_mutating_raw() -> None:
    raw = load_split_raw_input(OBSERVED_4ES_SPLIT)
    before = deepcopy(raw.payload)

    design_input = load_split_design_input(OBSERVED_4ES_SPLIT)

    assert raw.payload == before
    assert raw.payload["column_and_common"]["platina_enchape_alma"]["usar_dp_col"] is False
    assert raw.payload["column_and_common"]["platina_enchape_alma"]["n_dp_col"] == 0
    assert design_input.legacy_case.geometry.doubler_plate_enabled is False
    assert design_input.legacy_case.geometry.doubler_plate_count == 1
    assert design_input.legacy_case.geometry.doubler_plate_thickness is not None
    assert design_input.legacy_case.geometry.doubler_plate_thickness.value > 0.0
