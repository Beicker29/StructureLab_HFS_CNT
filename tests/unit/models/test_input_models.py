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


def test_parse_non_prequalified_moment_splice_case_valid() -> None:
    payload = {
        "project_id": "proj_bbmb_demo",
        "case_id": "case_001_bbmb_splice_si",
        "design_code_context": {"primary_document": "AISC 360-22", "supporting_documents": []},
        "units_system": "SI",
        "connection_family": "Fully_Restrained_Moment",
        "connection_type": "bbmb_splice",
        "load_state": "strength",
        "sections": {"beam_left_shape": "W24X76", "beam_right_shape": "W24X76"},
        "materials": {
            "beam_left_steel_type": "ASTM A572 Gr 50",
            "beam_right_steel_type": "ASTM A572 Gr 50",
            "plate_steel_type": "ASTM A572 Gr 50",
            "bolt_fabrication_standard": "ASTM A490",
            "bolt_description": "Grupo 150",
            "bolt_shape": "P1-1/8\"X1-3/4\"",
            "bolt_thread_condition": "N",
        },
        "geometry": {
            "splice_gap": {"value": 20.0, "unit": "mm"},
            "flange_plate_top_thickness": {"value": 25.4, "unit": "mm"},
            "flange_plate_top_width": {"value": 260.0, "unit": "mm"},
            "flange_plate_top_length": {"value": 600.0, "unit": "mm"},
            "flange_plate_bottom_thickness": {"value": 25.4, "unit": "mm"},
            "flange_plate_bottom_width": {"value": 260.0, "unit": "mm"},
            "flange_plate_bottom_length": {"value": 600.0, "unit": "mm"},
            "web_plate_thickness": {"value": 12.7, "unit": "mm"},
            "web_plate_height": {"value": 350.0, "unit": "mm"},
            "web_plate_length": {"value": 500.0, "unit": "mm"},
            "flange_bolt_gage": {"value": 140.0, "unit": "mm"},
            "flange_bolt_pitch": {"value": 90.0, "unit": "mm"},
            "flange_bolt_edge_distance_longitudinal": {"value": 40.0, "unit": "mm"},
            "flange_bolt_edge_distance_transverse": {"value": 40.0, "unit": "mm"},
            "flange_bolt_rows_per_side": 4,
            "flange_bolt_lines": 2,
            "web_bolt_gage": {"value": 90.0, "unit": "mm"},
            "web_bolt_pitch": {"value": 80.0, "unit": "mm"},
            "web_bolt_edge_distance": {"value": 40.0, "unit": "mm"},
            "web_bolt_rows_per_side": 4,
            "web_bolt_lines": 2,
        },
        "loads": {
            "moment_right_end": {"value": 450000.0, "unit": "kN-mm"},
            "moment_left_end": {"value": 450000.0, "unit": "kN-mm"},
            "shear_right_end": {"value": 250.0, "unit": "kN"},
            "shear_left_end": {"value": 250.0, "unit": "kN"},
            "axial_right_end": {"value": 100.0, "unit": "kN"},
            "axial_left_end": {"value": 100.0, "unit": "kN"},
        },
        "design_factors": {
            "phi_bolt_tension": 0.9,
            "phi_bolt_shear": 0.9,
            "phi_plate_yielding": 0.9,
            "phi_plate_rupture": 0.75,
            "phi_block_shear": 0.75,
        },
    }
    case = parse_input_case(payload)
    assert case.connection_family == "Fully_Restrained_Moment"
    assert case.connection_type == "bbmb_splice"
