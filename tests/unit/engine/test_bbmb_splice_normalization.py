from __future__ import annotations

from steel_connections.domain.engine.validate import parse_and_validate_payload


def test_parse_new_splice_payload_derives_plate_dimensions() -> None:
    payload = {
        "project_id": "proj_bbmb_demo",
        "case_id": "case_001_bbmb_splice_si",
        "design_code_context": {"primary_document": "AISC 360-22", "supporting_documents": []},
        "units_system": "SI",
        "connection_family": "Fully_Restrained_Moment",
        "connection_type": "bbmb_splice",
        "load_state": "strength",
        "viga": {
            "sep": {"value": 20.0, "unit": "mm"},
            "perfil": "W24X76",
            "tipo_acero_viga": "ASTM A572 Gr 50",
        },
        "platina_1_alma": {
            "tp1": {"value": 12.7, "unit": "mm"},
            "tipo_acero_p1": "ASTM A572 Gr 50",
            "tipo_agujero_p1": "estandar",
        },
        "platina_2_ala": {
            "tp2": {"value": 25.4, "unit": "mm"},
            "tipo_acero_p2": "ASTM A572 Gr 50",
            "tipo_agujero_p2": "estandar",
        },
        "pernos_grupo_1_alma": {
            "bolt_shape_1": "P1-1/8\"X1-3/4\"",
            "bolt_thread_condition_1": "N",
            "bolt_fabrication_standard_1": "ASTM A490",
            "bolt_description_1": "Grupo 150",
            "Le1_x1": {"value": 40.0, "unit": "mm"},
            "Le1_x2": {"value": 40.0, "unit": "mm"},
            "S1_x": {"value": 90.0, "unit": "mm"},
            "S1_y": {"value": 80.0, "unit": "mm"},
            "Le1_y1": {"value": 40.0, "unit": "mm"},
            "Le1_y2": {"value": 40.0, "unit": "mm"},
            "nb1_x": 2,
            "nb1_y": 4,
        },
        "pernos_grupo_2_ala": {
            "bolt_shape_2": "P1-1/8\"X1-3/4\"",
            "bolt_thread_condition_2": "N",
            "bolt_fabrication_standard_2": "ASTM A490",
            "bolt_description_2": "Grupo 150",
            "Le2_x1": {"value": 40.0, "unit": "mm"},
            "Le2_x2": {"value": 40.0, "unit": "mm"},
            "S2_x": {"value": 90.0, "unit": "mm"},
            "Le2_z1": {"value": 40.0, "unit": "mm"},
            "Le2_z2": {"value": 40.0, "unit": "mm"},
            "S2_z1": {"value": 80.0, "unit": "mm"},
            "S2_z2": {"value": 80.0, "unit": "mm"},
            "nb2_x": 2,
            "nb2_z": 4,
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
    }

    case = parse_and_validate_payload(payload)
    assert case.geometry.web_plate_height.value == 320.0
    assert case.geometry.web_plate_length.value == 360.0
    assert case.geometry.flange_plate_top_length.value == 170.0
    assert case.geometry.flange_plate_top_width.value == 320.0
