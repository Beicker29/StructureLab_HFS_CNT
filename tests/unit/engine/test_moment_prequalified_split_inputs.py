from __future__ import annotations

import json
from pathlib import Path

import pytest

from steel_connections.domain.engine.validate import load_input_payload
from steel_connections.domain.engine.validate import parse_and_validate_file


SPLIT_ROOT = Path("examples/moment_prequalified/case_003_bseep_8es_split_inputs")
SPLIT_4E_ROOT = Path("examples/moment_prequalified/case_002_bueep_4e_split_inputs")
SPLIT_4ES_ROOT = Path("examples/moment_prequalified/case_004_bseep_4es_split_inputs")


def test_parse_moment_prequalified_split_bundle_from_directory() -> None:
    case = parse_and_validate_file(SPLIT_ROOT)
    assert case.connection_family == "moment_prequalified"
    assert case.connection_type == "bseep_8es"
    assert case.sections.beam_shape == "W21X68"
    assert case.sections.column_shape == "HEB 500"
    assert case.loads.pu_viga_right is not None
    assert case.loads.pu_viga_right.value == 0.0
    assert case.loads.beam_left_vgravity is not None
    assert case.loads.beam_left_vgravity.value == 97.11


def test_parse_moment_prequalified_split_bundle_from_any_member_file() -> None:
    right_file = SPLIT_ROOT / "case_003_beam_right_only.json"
    case = parse_and_validate_file(right_file)
    assert case.connection_family == "moment_prequalified"
    assert case.connection_type == "bseep_8es"
    assert case.geometry.end_plate_width is not None
    assert case.geometry.end_plate_width.value == 235.0
    assert case.geometry.end_plate_width_vgizq is not None
    assert case.geometry.end_plate_width_vgizq.value == 235.0


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
    assert case.geometry.doubler_plate_enabled is False
    assert case.geometry.doubler_plate_count == 1
    assert case.geometry.doubler_plate_thickness is not None
    assert case.geometry.doubler_plate_thickness.value > 0.0
    assert case.geometry.doubler_plate_thickness.unit == "mm"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def test_parse_moment_prequalified_split_bundle_left_only_two_files(tmp_path: Path) -> None:
    column = _read_json(SPLIT_ROOT / "case_003_column_and_common.json")
    column["factores_diseno"]["lados_conexion"] = "left_only"
    left = _read_json(SPLIT_ROOT / "case_003_beam_left_only.json")

    _write_json(tmp_path / "case_003_column_and_common.json", column)
    _write_json(tmp_path / "case_003_beam_left_only.json", left)

    case = parse_and_validate_file(tmp_path)
    assert case.design_factors.beam_connection_sides == "left_only"
    assert case.sections.beam_shape_izq == "W21X68"
    assert case.sections.beam_shape == "W21X68"


def test_parse_moment_prequalified_split_bundle_right_only_two_files(tmp_path: Path) -> None:
    column = _read_json(SPLIT_ROOT / "case_003_column_and_common.json")
    column["factores_diseno"]["lados_conexion"] = "right_only"
    right = _read_json(SPLIT_ROOT / "case_003_beam_right_only.json")

    _write_json(tmp_path / "case_003_column_and_common.json", column)
    _write_json(tmp_path / "case_003_beam_right_only.json", right)

    case = parse_and_validate_file(tmp_path)
    assert case.design_factors.beam_connection_sides == "right_only"
    assert case.sections.beam_shape_der == "W21X68"
    assert case.sections.beam_shape == "W21X68"


def test_parse_moment_prequalified_split_bundle_both_sides_missing_beam_file_fails(tmp_path: Path) -> None:
    column = _read_json(SPLIT_ROOT / "case_003_column_and_common.json")
    column["factores_diseno"]["lados_conexion"] = "both_sides"
    left = _read_json(SPLIT_ROOT / "case_003_beam_left_only.json")

    _write_json(tmp_path / "case_003_column_and_common.json", column)
    _write_json(tmp_path / "case_003_beam_left_only.json", left)

    with pytest.raises(Exception) as exc:
        load_input_payload(tmp_path)
    assert "requires both split files" in str(exc.value).lower()
