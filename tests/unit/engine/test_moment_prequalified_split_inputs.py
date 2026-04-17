from __future__ import annotations

from pathlib import Path

from steel_connections.domain.engine.validate import parse_and_validate_file


SPLIT_ROOT = Path("examples/moment_prequalified/case_003_bseep_8es_split_inputs")
SPLIT_4E_ROOT = Path("examples/moment_prequalified/case_002_bueep_4e_split_inputs")
SPLIT_4ES_ROOT = Path("examples/moment_prequalified/case_004_bseep_4es_split_inputs")


def test_parse_moment_prequalified_split_bundle_from_directory() -> None:
    case = parse_and_validate_file(SPLIT_ROOT)
    assert case.connection_family == "moment_prequalified"
    assert case.connection_type == "bseep_8es"
    assert case.sections.beam_shape == "W24X76"
    assert case.sections.column_shape == "W18X175"
    assert case.loads.pu_viga_right is not None
    assert case.loads.pu_viga_right.value == 0.0
    assert case.loads.beam_left_vgravity is not None
    assert case.loads.beam_left_vgravity.value == 44.482


def test_parse_moment_prequalified_split_bundle_from_any_member_file() -> None:
    right_file = SPLIT_ROOT / "case_003_beam_right_only.json"
    case = parse_and_validate_file(right_file)
    assert case.connection_family == "moment_prequalified"
    assert case.connection_type == "bseep_8es"
    assert case.geometry.end_plate_width is not None
    assert case.geometry.end_plate_width.value == 253.0


def test_parse_moment_prequalified_split_bundle_4e_directory() -> None:
    case = parse_and_validate_file(SPLIT_4E_ROOT)
    assert case.connection_family == "moment_prequalified"
    assert case.connection_type == "bueep_4e"
    assert case.design_factors.phi_n == 0.9
    assert case.design_factors.phi_d == 1.0


def test_parse_moment_prequalified_split_bundle_4es_directory() -> None:
    case = parse_and_validate_file(SPLIT_4ES_ROOT)
    assert case.connection_family == "moment_prequalified"
    assert case.connection_type == "bseep_4es"
    assert case.geometry.stiffener_thickness is not None
    assert case.geometry.stiffener_thickness.value == 12.7
