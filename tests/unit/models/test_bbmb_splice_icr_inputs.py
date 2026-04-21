from __future__ import annotations

from copy import deepcopy

import pytest
from pydantic import ValidationError

from steel_connections.models.input import parse_input_case


def _base_payload() -> dict:
    return {
        "project_id": "proj_bbmb_demo",
        "case_id": "case_001_bbmb_splice_si",
        "design_code_context": {"primary_document": "AISC 360-22", "supporting_documents": []},
        "units_system": "SI",
        "connection_family": "Fully_Restrained_Moment",
        "connection_type": "bbmb_splice",
        "load_state": "strength",
        "sections": {"beam_left_shape": "W18X35", "beam_right_shape": "W18X35"},
        "materials": {
            "beam_left_steel_type": "ASTM A572 Gr 50",
            "beam_right_steel_type": "ASTM A572 Gr 50",
            "plate_steel_type": "ASTM A36",
            "bolt_fabrication_standard": "ASTM A325",
            "bolt_fabrication_standard_web": "ASTM A325",
            "bolt_fabrication_standard_flange": "ASTM A325",
            "bolt_description": "Grupo 120",
            "bolt_shape": "P5/8\"X1-3/4\"",
            "bolt_shape_web": "P5/8\"X1-3/4\"",
            "bolt_shape_flange": "P3/4\"X1-3/4\"",
            "bolt_thread_condition": "N",
        },
        "geometry": {
            "splice_gap": {"value": 10.0, "unit": "mm"},
            "flange_plate_top_thickness": {"value": 19.05, "unit": "mm"},
            "flange_plate_top_width": {"value": 110.0, "unit": "mm"},
            "flange_plate_top_length": {"value": 580.0, "unit": "mm"},
            "flange_plate_bottom_thickness": {"value": 19.05, "unit": "mm"},
            "flange_plate_bottom_width": {"value": 110.0, "unit": "mm"},
            "flange_plate_bottom_length": {"value": 580.0, "unit": "mm"},
            "web_plate_thickness": {"value": 9.5, "unit": "mm"},
            "web_plate_height": {"value": 350.0, "unit": "mm"},
            "web_plate_length": {"value": 200.0, "unit": "mm"},
            "flange_bolt_gage": {"value": 60.0, "unit": "mm"},
            "flange_bolt_pitch": {"value": 40.0, "unit": "mm"},
            "flange_bolt_pitch_secondary": {"value": 90.0, "unit": "mm"},
            "flange_bolt_edge_distance_longitudinal": {"value": 50.0, "unit": "mm"},
            "flange_bolt_edge_distance_transverse": {"value": 30.0, "unit": "mm"},
            "flange_bolt_rows_per_side": 2,
            "flange_bolt_lines": 4,
            "web_bolt_gage": {"value": 60.0, "unit": "mm"},
            "web_bolt_pitch": {"value": 60.0, "unit": "mm"},
            "web_bolt_edge_distance": {"value": 25.0, "unit": "mm"},
            "web_bolt_edge_distance_x1": {"value": 35.0, "unit": "mm"},
            "web_bolt_edge_distance_x2": {"value": 35.0, "unit": "mm"},
            "web_bolt_edge_distance_y1": {"value": 25.0, "unit": "mm"},
            "web_bolt_edge_distance_y2": {"value": 25.0, "unit": "mm"},
            "web_bolt_edge_distance_y3": {"value": 25.0, "unit": "mm"},
            "flange_bolt_edge_distance_x1": {"value": 50.0, "unit": "mm"},
            "flange_bolt_edge_distance_x2": {"value": 50.0, "unit": "mm"},
            "flange_bolt_edge_distance_z1": {"value": 30.0, "unit": "mm"},
            "flange_bolt_edge_distance_z2": {"value": 40.0, "unit": "mm"},
            "web_bolt_rows_per_side": 6,
            "web_bolt_lines": 2,
            "web_bolt_tightening_type": "pretensioned",
            "flange_bolt_tightening_type": "pretensioned",
            "beam_surface_condition": "painted",
            "beam_atmospheric_condition": "non_corrosive",
            "web_plate_surface_condition": "painted",
            "web_plate_atmospheric_condition": "non_corrosive",
            "flange_plate_surface_condition": "painted",
            "flange_plate_atmospheric_condition": "non_corrosive",
            "beam_length_tolerance": {"value": 6.35, "unit": "mm"},
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
            "phi_slip_critical": 1.0,
        },
        "procedure": {
            "icr": {
                "method": "Elastic Method - Superposition",
                "tolerance_1": 0.01,
                "max_iterations_1": 1000,
            }
        },
    }


@pytest.mark.parametrize(
    "method_raw, expected",
    [
        ("Elastic Method - Superposition", "elastic_superposition"),
        ("Elastic Method - Center of Rotation", "elastic_ecr"),
        ("Instant Center of Rotation Method", "icr"),
    ],
)
def test_parse_splice_method_aliases(method_raw: str, expected: str) -> None:
    payload = _base_payload()
    payload["procedure"]["icr"]["method"] = method_raw
    if expected == "icr":
        payload["procedure"]["icr"]["rult_1_kip"] = {"value": 20.0, "unit": "kip"}
    case = parse_input_case(payload)
    assert case.procedure is not None
    assert case.procedure.icr.method == expected


def test_parse_splice_icr_requires_rult() -> None:
    payload = _base_payload()
    payload["procedure"]["icr"]["method"] = "icr"
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
