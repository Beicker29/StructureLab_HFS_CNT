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
        "sections": {"shape_vg": "W24X76"},
        "materials": {
            "steel_vg": "ASTM A572 Gr 50",
            "shape_blt_web": "P1-1/8\"X1-3/4\"",
            "std_blt_web": "ASTM A490",
            "desc_blt_web": "Grupo 150",
            "thread_blt_web": "N",
            "shape_blt_flange": "P1-1/8\"X1-3/4\"",
            "std_blt_flange": "ASTM A490",
            "desc_blt_flange": "Grupo 150",
            "thread_blt_flange": "N",
        },
        "geometry": {
            "gap_sp": {"value": 20.0, "unit": "mm"},
            "tol_L_vg": {"value": 6.35, "unit": "mm"},
            "t_plt_web": {"value": 12.7, "unit": "mm"},
            "type_hole_plt_web": "standard",
            "t_plt_flange": {"value": 25.4, "unit": "mm"},
            "type_hole_plt_flange": "standard",
            "n_blt_web_x": 2,
            "n_blt_web_y": 4,
            "g_blt_web": {"value": 90.0, "unit": "mm"},
            "p_blt_web": {"value": 80.0, "unit": "mm"},
            "Le_blt_web_x1": {"value": 40.0, "unit": "mm"},
            "Le_blt_web_x2": {"value": 40.0, "unit": "mm"},
            "Le_blt_web_y1": {"value": 40.0, "unit": "mm"},
            "Le_blt_web_y2": {"value": 40.0, "unit": "mm"},
            "type_tight_blt_web": "pretensioned",
            "n_blt_flange_x": 2,
            "n_blt_flange_z": 4,
            "p_blt_flange": {"value": 90.0, "unit": "mm"},
            "g_blt_flange": {"value": 80.0, "unit": "mm"},
            "Le_blt_flange_x1": {"value": 40.0, "unit": "mm"},
            "Le_blt_flange_x2": {"value": 40.0, "unit": "mm"},
            "Le_blt_flange_z1": {"value": 40.0, "unit": "mm"},
            "Le_blt_flange_z2": {"value": 40.0, "unit": "mm"},
            "Le_blt_flange_z3": {"value": 40.0, "unit": "mm"},
            "type_tight_blt_flange": "pretensioned",
        },
        "loads": {
            "Pu_sp": {"value": 100.0, "unit": "kN"},
            "Vu2_sp": {"value": 250.0, "unit": "kN"},
            "Vu3_sp": {"value": 0.0, "unit": "kN"},
            "Mu3_sp": {"value": 450000.0, "unit": "kN-mm"},
            "Mu2_sp": {"value": 0.0, "unit": "kN-mm"},
            "Tu_sp": {"value": 0.0, "unit": "kN-mm"},
        },
        "design_factors": {
            "phi_bt": 0.9,
            "phi_bv": 0.9,
            "phi_py": 0.9,
            "phi_pr": 0.75,
            "phi_bs": 0.75,
        },
    }
    case = parse_input_case(payload)
    assert case.connection_family == "Fully_Restrained_Moment"
    assert case.connection_type == "bbmb_splice"
