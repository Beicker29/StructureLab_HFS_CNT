from __future__ import annotations

from copy import deepcopy

import pytest


MOMENT_CASE_PAYLOAD = {
    "project_id": "proj_moment_demo",
    "case_id": "case_001",
    "design_code_context": {
        "primary_document": "AISC 358-22",
        "supporting_documents": [
            "Design Guide 1 - Base Plate and Anchor Rod Design (3nd Edition)",
        ],
    },
    "units_system": "US",
    "connection_family": "moment_prequalified",
    "connection_type": "wuf_w",
    "load_state": "strength",
    "sections": {"beam_shape": "W24X76"},
    "materials": {
        "profile_steel_type": "ASTM A572 Gr 50",
        "weld_fexx": {"value": 70.0, "unit": "ksi"},
    },
    "geometry": {
        "beam_flange_area": {"value": 10.0, "unit": "in2"},
        "weld_effective_area": {"value": 12.0, "unit": "in2"},
    },
    "loads": {"beam_flange_tension": {"value": 200.0, "unit": "kip"}},
    "design_factors": {"phi_flange_tension": 0.9, "phi_flange_weld": 0.75},
}

DG1_CASE_PAYLOAD = {
    "project_id": "proj_dg1_demo",
    "case_id": "case_001",
    "design_code_context": {
        "primary_document": "Design Guide 1 - Base Plate and Anchor Rod Design (3nd Edition)",
        "supporting_documents": ["AISC 358-22"],
    },
    "units_system": "US",
    "connection_family": "base_plate_anchor_rod",
    "connection_type": "dg1_base_plate",
    "load_state": "strength",
    "materials": {
        "column_fy": {"value": 50.0, "unit": "ksi"},
        "plate_fy": {"value": 36.0, "unit": "ksi"},
        "anchor_fu": {"value": 75.0, "unit": "ksi"},
    },
    "geometry": {
        "base_plate_area": {"value": 400.0, "unit": "in2"},
        "anchor_area": {"value": 2.25, "unit": "in2"},
    },
    "loads": {"axial_compression": {"value": 250.0, "unit": "kip"}},
    "design_factors": {"phi_bearing": 0.75},
}

BUEEP_4E_CASE_PAYLOAD = {
    "project_id": "proj_bueep_demo",
    "case_id": "case_bueep_001",
    "design_code_context": {
        "primary_document": "AISC 358-22",
        "supporting_documents": [],
    },
    "units_system": "US",
    "connection_family": "moment_prequalified",
    "connection_type": "bueep_4e",
    "load_state": "strength",
    "sections": {"beam_shape": "W24X76", "column_shape": "W24X104"},
    "materials": {
        "profile_steel_type": "ASTM A572 Gr 50",
        "plate_steel_type": "ASTM A572 Gr 50",
        "bolt_fabrication_standard": "ASTM A490",
        "bolt_description": "Grupo 150",
        "bolt_shape": "P1-1/8\"X1-3/4\"",
        "bolt_thread_condition": "N",
        "weld_fexx": {"value": 70.0, "unit": "ksi"},
        "elastic_modulus": {"value": 29000.0, "unit": "ksi"},
    },
    "geometry": {
        "beam_clear_span_length": {"value": 240.0, "unit": "in"},
        "beam_shear_connector_free_length_from_column_face": {"value": 40.0, "unit": "in"},
        "column_slab_connection_condition": "isolated",
        "end_plate_width": {"value": 9.976377952755906, "unit": "in"},
        "end_plate_thickness": {"value": 1.2, "unit": "in"},
        "de": {"value": 2.3622, "unit": "in"},
        "pb": {"value": 3.7402, "unit": "in"},
        "pfo": {"value": 1.9685, "unit": "in"},
        "pfi": {"value": 1.9685, "unit": "in"},
        "continuity_plate_thickness": {"value": 0.625, "unit": "in"},
        "continuity_plate_weld_type": "CJP",
        "bolt_gage": {"value": 6.0, "unit": "in"},
        "bolt_tightening_type": "pretensioned",
        "clear_distance_end_plate": {"value": 2.0, "unit": "in"},
        "clear_distance_column_flange": {"value": 2.0, "unit": "in"},
        "column_end_distance_to_beam_flange": {"value": 30.0, "unit": "in"},
        "weld_leg_size_w": {"value": 0.5, "unit": "in"},
        "end_plate_beam_web_weld_type": "CJP",
        "end_plate_beam_web_weld_length_lwe": {"value": 12.0, "unit": "in"},
        "end_plate_beam_web_weld_thickness_twe": {"value": 0.25, "unit": "in"},
    },
    "loads": {
        "pu_viga": {"value": 0.0, "unit": "kip"},
        "pu_columna": {"value": 0.0, "unit": "kip"},
        "probable_moment_column_face": {"value": 6000.0, "unit": "kip-in"},
        "beam_right_vgravity": {"value": 10.0, "unit": "kip"}
    },
    "design_factors": {
        "phi_d": 0.9,
        "phi_n": 0.9,
        "member_ductility_demand_beam": "moderate",
        "member_ductility_demand_column": "moderate",
        "column_beam_moment_ratio_minimum": 1.0
    },
    "procedure": {
        "tension_bolt_line_distances": [
            {"value": 8.0, "unit": "in"},
            {"value": 10.0, "unit": "in"}
        ],
        "beam_available_shear_strength": {"value": 200.0, "unit": "kip"},
        "flange_weld_available_strength": {"value": 300.0, "unit": "kip"},
        "web_weld_available_strength": {"value": 200.0, "unit": "kip"},
        "continuity_plate_available_strength": {"value": 100.0, "unit": "kip"},
        "panel_zone_capacity": {"value": 150.0, "unit": "kip"},
        "column_beam_moment_ratio": 1.2
    }
}

BSEEP_8ES_CASE_PAYLOAD = {
    "project_id": "proj_bseep_demo",
    "case_id": "case_bseep_001",
    "design_code_context": {
        "primary_document": "AISC 358-22",
        "supporting_documents": [],
    },
    "units_system": "US",
    "connection_family": "moment_prequalified",
    "connection_type": "bseep_8es",
    "load_state": "strength",
    "sections": {"beam_shape": "W24X76", "column_shape": "W24X104"},
    "materials": {
        "profile_steel_type": "ASTM A572 Gr 50",
        "plate_steel_type": "ASTM A572 Gr 50",
        "bolt_fabrication_standard": "ASTM A490",
        "bolt_description": "Grupo 150",
        "bolt_shape": "P1-1/8\"X1-3/4\"",
        "bolt_thread_condition": "N",
        "weld_fexx": {"value": 70.0, "unit": "ksi"},
        "elastic_modulus": {"value": 29000.0, "unit": "ksi"},
    },
    "geometry": {
        "beam_clear_span_length": {"value": 240.0, "unit": "in"},
        "beam_shear_connector_free_length_from_column_face": {"value": 40.0, "unit": "in"},
        "column_slab_connection_condition": "isolated",
        "bolt_gage": {"value": 6.0, "unit": "in"},
        "end_plate_width": {"value": 9.976377952755906, "unit": "in"},
        "end_plate_thickness": {"value": 1.2, "unit": "in"},
        "de": {"value": 2.3622, "unit": "in"},
        "pb": {"value": 3.7402, "unit": "in"},
        "pfo": {"value": 1.9685, "unit": "in"},
        "pfi": {"value": 1.9685, "unit": "in"},
        "continuity_plate_thickness": {"value": 0.625, "unit": "in"},
        "continuity_plate_weld_type": "CJP",
        "clear_distance_end_plate": {"value": 2.0, "unit": "in"},
        "bolt_tightening_type": "pretensioned",
        "clear_distance_column_flange": {"value": 2.0, "unit": "in"},
        "column_end_distance_to_beam_flange": {"value": 30.0, "unit": "in"},
        "weld_leg_size_w": {"value": 0.5, "unit": "in"},
        "end_plate_beam_web_weld_type": "CJP",
        "end_plate_beam_web_weld_length_lwe": {"value": 12.0, "unit": "in"},
        "end_plate_beam_web_weld_thickness_twe": {"value": 0.25, "unit": "in"},
        "end_plate_stiffener_weld_type": "CJP",
        "end_plate_stiffener_weld_length_lst": {"value": 7.5, "unit": "in"},
        "end_plate_stiffener_weld_size_wst": {"value": 0.5, "unit": "in"},
        "end_plate_stiffener_weld_lines_nl": 2,
        "beam_stiffener_weld_type": "CJP",
        "beam_stiffener_weld_length_lstw2": {"value": 7.5, "unit": "in"},
        "beam_stiffener_weld_size_wst2": {"value": 0.5, "unit": "in"},
        "beam_stiffener_weld_lines_nl_w2": 2,
        "stiffener_thickness": {"value": 0.5, "unit": "in"},
    },
    "loads": {
        "pu_viga": {"value": 0.0, "unit": "kip"},
        "pu_columna": {"value": 0.0, "unit": "kip"},
        "probable_moment_column_face": {"value": 6000.0, "unit": "kip-in"},
        "beam_right_vgravity": {"value": 10.0, "unit": "kip"},
        "beam_left_vgravity": {"value": 10.0, "unit": "kip"}
    },
    "design_factors": {
        "phi_d": 0.9,
        "phi_n": 0.9,
        "member_ductility_demand_beam": "moderate",
        "member_ductility_demand_column": "moderate",
        "column_beam_moment_ratio_minimum": 1.0
    },
    "procedure": {
        "tension_bolt_line_distances": [
            {"value": 8.0, "unit": "in"},
            {"value": 10.0, "unit": "in"},
            {"value": 12.0, "unit": "in"},
            {"value": 14.0, "unit": "in"}
        ],
        "beam_available_shear_strength": {"value": 260.0, "unit": "kip"},
        "flange_weld_available_strength": {"value": 300.0, "unit": "kip"},
        "web_weld_available_strength": {"value": 200.0, "unit": "kip"},
        "continuity_plate_available_strength": {"value": 100.0, "unit": "kip"},
        "panel_zone_capacity": {"value": 150.0, "unit": "kip"},
        "column_beam_moment_ratio": 1.2
    }
}

BSEEP_4ES_CASE_PAYLOAD = deepcopy(BSEEP_8ES_CASE_PAYLOAD)
BSEEP_4ES_CASE_PAYLOAD["connection_type"] = "bseep_4es"
BSEEP_4ES_CASE_PAYLOAD["case_id"] = "case_bseep_4es_001"


@pytest.fixture
def moment_payload() -> dict:
    return deepcopy(MOMENT_CASE_PAYLOAD)


@pytest.fixture
def dg1_payload() -> dict:
    return deepcopy(DG1_CASE_PAYLOAD)


@pytest.fixture
def bueep_4e_payload() -> dict:
    return deepcopy(BUEEP_4E_CASE_PAYLOAD)


@pytest.fixture
def bseep_8es_payload() -> dict:
    return deepcopy(BSEEP_8ES_CASE_PAYLOAD)


@pytest.fixture
def bseep_4es_payload() -> dict:
    return deepcopy(BSEEP_4ES_CASE_PAYLOAD)
