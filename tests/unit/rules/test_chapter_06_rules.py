from __future__ import annotations

from steel_connections.data.materials_repository import get_bolt_strength_properties
from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.models.errors import StructuredEngineException
from steel_connections.models.output import CheckStatus, GlobalStatus
from steel_connections.models.units import UnitSystem


def test_bueep_rule_set_runs_without_errors(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.PASS
    assert len(result.checks) == 1
    assert all(check.status == CheckStatus.PASS for check in result.checks)

def test_bueep_missing_de_fails_hard(bueep_4e_payload: dict) -> None:
    del bueep_4e_payload["geometry"]["de"]
    try:
        run_case_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["geometry.de"]
    else:
        raise AssertionError("Expected StructuredEngineException for missing geometry.de.")


def test_bueep_missing_bolt_thread_condition_fails_hard(bueep_4e_payload: dict) -> None:
    del bueep_4e_payload["materials"]["bolt_thread_condition"]
    try:
        run_case_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["geometry.bolts.bolt_thread_condition"]
    else:
        raise AssertionError("Expected StructuredEngineException for missing bolt_thread_condition.")


def test_bueep_bolt_fnv_uses_thread_condition_x(bueep_4e_payload: dict) -> None:
    bueep_4e_payload["materials"]["bolt_thread_condition"] = "X"
    case = parse_and_validate_payload(bueep_4e_payload)
    expected = get_bolt_strength_properties(
        description="Grupo 150",
        specification="ASTM A490",
        unit_system=UnitSystem.US,
    )["fnv_threads_excluded"]
    assert case.materials.bolt_fnv is not None
    assert case.materials.bolt_fnv.unit == expected.unit
    assert abs(case.materials.bolt_fnv.value - expected.value) < 1e-9


def test_bueep_prequalification_limits_are_reported(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.PASS
    assert prequal.dcr is None
    limits = prequal.calculation_memory.intermediates["step_1_limits"]
    assert len(limits) == 29
    assert {"beam", "column", "end_plate", "end_plate_stiffener", "welds", "continuity_plate", "bolts", "table_6_1"} == {
        item["scope"] for item in limits
    }
    first_column_idx = next(i for i, item in enumerate(limits) if item["scope"] == "column")
    first_end_plate_idx = next(i for i, item in enumerate(limits) if item["scope"] == "end_plate")
    first_end_plate_stiffener_idx = next(i for i, item in enumerate(limits) if item["scope"] == "end_plate_stiffener")
    first_welds_idx = next(i for i, item in enumerate(limits) if item["scope"] == "welds")
    first_continuity_plate_idx = next(i for i, item in enumerate(limits) if item["scope"] == "continuity_plate")
    first_bolts_idx = next(i for i, item in enumerate(limits) if item["scope"] == "bolts")
    first_table_idx = next(i for i, item in enumerate(limits) if item["scope"] == "table_6_1")
    assert all(item["scope"] == "beam" for item in limits[:first_column_idx])
    assert all(item["scope"] == "column" for item in limits[first_column_idx:first_end_plate_idx])
    assert all(item["scope"] == "end_plate" for item in limits[first_end_plate_idx:first_end_plate_stiffener_idx])
    assert all(
        item["scope"] == "end_plate_stiffener"
        for item in limits[first_end_plate_stiffener_idx:first_welds_idx]
    )
    assert all(item["scope"] == "welds" for item in limits[first_welds_idx:first_continuity_plate_idx])
    assert all(item["scope"] == "continuity_plate" for item in limits[first_continuity_plate_idx:first_bolts_idx])
    assert all(item["scope"] == "bolts" for item in limits[first_bolts_idx:first_table_idx])
    assert all(item["scope"] == "table_6_1" for item in limits[first_table_idx:])
    beam_shape = next(item for item in limits if item["id"] == "beam.shape_family")
    assert beam_shape["comparison"] == "family_in"
    assert beam_shape["result"] == "OK"
    column_shape = next(item for item in limits if item["id"] == "column.shape_family")
    assert column_shape["comparison"] == "family_in"
    assert column_shape["result"] == "OK"
    column_depth = next(item for item in limits if item["id"] == "section_6_3.column_depth_maximum")
    assert column_depth["comparison"] == "le"
    assert column_depth["result"] == "OK"
    column_compactness_flange = next(item for item in limits if item["id"] == "section_2_3_4.column_flange_width_to_thickness")
    assert column_compactness_flange["comparison"] == "le"
    assert column_compactness_flange["result"] == "OK"
    column_compactness_web = next(item for item in limits if item["id"] == "section_2_3_4.column_web_width_to_thickness")
    assert column_compactness_web["comparison"] == "le"
    assert column_compactness_web["result"] == "OK"
    continuity_weld_type = next(
        item for item in limits if item["id"] == "section_6_3.continuity_plate_weld_type_for_thin_plate"
    )
    assert continuity_weld_type["comparison"] == "conditional_allowed_set"
    assert continuity_weld_type["result"] == "OK"
    continuity_weld_declared = next(
        item for item in limits if item["id"] == "section_6_3.continuity_plate_weld_type_declared"
    )
    assert continuity_weld_declared["comparison"] == "in_set"
    assert continuity_weld_declared["result"] == "OK"
    bolt_tight_valid = next(item for item in limits if item["id"] == "section_4_1.bolt_tightening_type_valid")
    assert bolt_tight_valid["comparison"] == "in_set"
    assert bolt_tight_valid["result"] == "OK"
    bolt_tight_required = next(
        item for item in limits if item["id"] == "section_4_1.bolt_tightening_required_pretensioned"
    )
    assert bolt_tight_required["comparison"] == "equals"
    assert bolt_tight_required["result"] == "OK"
    bolt_standard = next(item for item in limits if item["id"] == "section_4_1.bolt_fabrication_standard_permitted")
    assert bolt_standard["comparison"] == "in_set"
    assert bolt_standard["result"] == "OK"
    notes = prequal.calculation_memory.intermediates["step_1_notes"]
    assert isinstance(notes, list)
    assert any(note.get("id") == "section_2_3_4.protected_zone_length" for note in notes)
    assert any(note.get("id") == "section_6_3.end_plate_connection_location" for note in notes)
    assert any(note.get("id") == "section_6_3.end_plate_height_derived" for note in notes)
    assert any(note.get("id") == "section_6_7.beam_flange_to_end_plate_weld_note" for note in notes)
    assert any(note.get("id") == "section_4_2.installation_requirements" for note in notes)
    assert any(note.get("id") == "section_4_3.quality_control_assurance" for note in notes)
    width_check = next(item for item in limits if item["id"] == "beam.bp_ge_bf_plus_margin")
    assert width_check["comparison"] == "ge"
    assert width_check["calculated_symbol"] == "bp"
    assert width_check["limit_symbol"] == "bf + margin"
    assert width_check["result"] == "OK"
    span_depth = next(item for item in limits if item["id"] == "section_2_3_4.clear_span_to_depth_ratio")
    assert span_depth["comparison"] == "ge"
    assert span_depth["result"] == "OK"
    compactness_flange = next(item for item in limits if item["id"] == "section_2_3_4.beam_flange_width_to_thickness")
    assert compactness_flange["comparison"] == "le"
    assert compactness_flange["result"] == "OK"
    compactness_web = next(item for item in limits if item["id"] == "section_2_3_4.beam_web_width_to_thickness")
    assert compactness_web["comparison"] == "le"
    assert compactness_web["result"] == "OK"
    tbf_range = next(item for item in limits if item["id"] == "table_6_1.tbf.range")
    assert tbf_range["comparison"] == "range"
    assert tbf_range["result"] == "OK"
    slab_iso = next(item for item in limits if item["id"] == "section_2_3_4.slab_isolation_condition")
    assert slab_iso["comparison"] == "equals"
    assert slab_iso["result"] == "OK"
    end_plate_dual = next(item for item in limits if item["id"] == "section_6_3.end_plate_width_dual_limit")
    assert end_plate_dual["scope"] == "end_plate"
    assert end_plate_dual["comparison"] == "compound"
    assert "bp <= bbf +" in end_plate_dual["verification_text"]
    assert "bp <= bcf" in end_plate_dual["verification_text"]
    end_plate_stiffener = next(item for item in limits if item["id"] == "section_6_3.end_plate_stiffener_height_derived")
    assert end_plate_stiffener["scope"] == "end_plate_stiffener"
    assert end_plate_stiffener["comparison"] == "compound"
    assert "hst = pfo + de" in end_plate_stiffener["verification_text"]
    end_plate_web_weld_type = next(item for item in limits if item["id"] == "section_6_7.end_plate_beam_web_weld_type_allowed")
    assert end_plate_web_weld_type["scope"] == "welds"
    assert end_plate_web_weld_type["comparison"] == "in_set"
    assert end_plate_web_weld_type["result"] == "OK"
    pfo_compound = next(item for item in limits if item["id"] == "table_6_1.edge_pfo_ge_emin")
    assert pfo_compound["comparison"] == "compound"
    assert "pso (=pfo)" in pfo_compound["verification_text"]
    pfi_compound = next(item for item in limits if item["id"] == "table_6_1.edge_pfi_ge_emin")
    assert pfi_compound["comparison"] == "compound"
    assert "psi = pfi + tfb - tcp" in pfi_compound["verification_text"]


def test_bseep_prequalification_limits_fail_when_pitch_is_below_3db(bseep_8es_payload: dict) -> None:
    bseep_8es_payload["geometry"]["pb"]["value"] = 2.0
    result = run_case_payload(bseep_8es_payload)
    assert result.global_status == GlobalStatus.FAIL
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bseep_8es.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    pitch_check = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] == "table_6_1.pitch_pb_ge_3db"
    )
    assert pitch_check["result"] == "NO_OK"
    assert pitch_check["comparison"] == "compound"


def test_bseep8es_prequalification_limits_fail_when_pb_is_outside_89_95mm_range(bseep_8es_payload: dict) -> None:
    bseep_8es_payload["geometry"]["pb"]["value"] = 96.0
    result = run_case_payload(bseep_8es_payload)
    assert result.global_status == GlobalStatus.FAIL
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bseep_8es.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    pb_compound = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] == "table_6_1.pitch_pb_ge_3db"
    )
    assert pb_compound["result"] == "NO_OK"
    assert pb_compound["comparison"] == "compound"


def test_bueep_prequalification_limits_fail_when_thin_continuity_plate_weld_type_is_invalid(
    bueep_4e_payload: dict,
) -> None:
    bueep_4e_payload["geometry"]["continuity_plate_thickness"]["value"] = 0.30
    bueep_4e_payload["geometry"]["continuity_plate_weld_type"] = "single_bevel_groove"
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.FAIL
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    weld_type_check = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] == "section_6_3.continuity_plate_weld_type_for_thin_plate"
    )
    assert weld_type_check["result"] == "NO_OK"
    assert weld_type_check["comparison"] == "conditional_allowed_set"


def test_bueep_prequalification_limits_fail_when_continuity_plate_weld_type_is_missing(
    bueep_4e_payload: dict,
) -> None:
    del bueep_4e_payload["geometry"]["continuity_plate_weld_type"]
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.FAIL
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    weld_declared_check = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] == "section_6_3.continuity_plate_weld_type_declared"
    )
    assert weld_declared_check["result"] == "NO_OK"
    assert weld_declared_check["comparison"] == "in_set"


def test_bueep_prequalification_limits_fail_when_double_sided_fillet_with_thick_plate(
    bueep_4e_payload: dict,
) -> None:
    bueep_4e_payload["geometry"]["continuity_plate_weld_type"] = "double_sided_fillet"
    bueep_4e_payload["geometry"]["continuity_plate_thickness"]["value"] = 0.625
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.FAIL
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    weld_condition_check = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] == "section_6_3.continuity_plate_weld_type_for_thin_plate"
    )
    assert weld_condition_check["result"] == "NO_OK"
    assert weld_condition_check["comparison"] == "conditional_allowed_set"


def test_bueep_prequalification_limits_fail_when_bolt_tightening_is_snug_tight(
    bueep_4e_payload: dict,
) -> None:
    bueep_4e_payload["geometry"]["bolt_tightening_type"] = "snug_tight"
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.FAIL
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    bolt_tight_required = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] == "section_4_1.bolt_tightening_required_pretensioned"
    )
    assert bolt_tight_required["result"] == "NO_OK"
    assert bolt_tight_required["comparison"] == "equals"


def test_kc_distance_input_is_forbidden(bueep_4e_payload: dict) -> None:
    bueep_4e_payload["geometry"]["kc_distance"] = {"value": 2.0, "unit": "in"}
    try:
        parse_and_validate_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert "kc_distance" in exc.error.message
    else:
        raise AssertionError("Expected validation error because geometry.kc_distance is no longer an allowed input.")


def test_stiffener_height_input_is_forbidden(bseep_8es_payload: dict) -> None:
    bseep_8es_payload["geometry"]["stiffener_height"] = {"value": 4.0, "unit": "in"}
    try:
        parse_and_validate_payload(bseep_8es_payload)
    except StructuredEngineException as exc:
        assert "stiffener_height" in exc.error.message
    else:
        raise AssertionError("Expected validation error because geometry.stiffener_height is no longer an allowed input.")


def test_stiffener_length_input_is_forbidden(bseep_8es_payload: dict) -> None:
    bseep_8es_payload["geometry"]["stiffener_length"] = {"value": 7.5, "unit": "in"}
    try:
        parse_and_validate_payload(bseep_8es_payload)
    except StructuredEngineException as exc:
        assert "stiffener_length" in exc.error.message
    else:
        raise AssertionError("Expected validation error because geometry.stiffener_length is no longer an allowed input.")


def test_grouped_geometry_payload_is_supported(bueep_4e_payload: dict) -> None:
    geo = bueep_4e_payload["geometry"]
    bolt_shape = bueep_4e_payload["materials"].pop("bolt_shape")
    bolt_thread = bueep_4e_payload["materials"].pop("bolt_thread_condition")
    bueep_4e_payload["geometry"] = {
        "beam": {
            "clear_span_length": geo["beam_clear_span_length"],
            "shear_connector_free_length_from_column_face": geo[
                "beam_shear_connector_free_length_from_column_face"
            ],
        },
        "column": {
            "column_end_distance_to_beam_flange": geo["column_end_distance_to_beam_flange"],
            "slab_connection_condition": geo["column_slab_connection_condition"],
        },
        "end_plate": {
            "end_plate_width": geo["end_plate_width"],
            "end_plate_thickness": geo["end_plate_thickness"],
            "de": geo["de"],
            "pb": geo["pb"],
            "pfo": geo["pfo"],
            "pfi": geo["pfi"],
        },
        "continuity_plate": {
            "continuity_plate_thickness": geo["continuity_plate_thickness"],
        },
        "stiffener": {},
        "bolts": {
            "bolt_gage": geo["bolt_gage"],
            "clear_distance_end_plate": geo["clear_distance_end_plate"],
            "clear_distance_column_flange": geo["clear_distance_column_flange"],
            "bolt_tightening_type": geo["bolt_tightening_type"],
            "bolt_shape": bolt_shape,
            "bolt_thread_condition": bolt_thread,
        },
        "welds": {
            "continuity_plate_weld_type": geo["continuity_plate_weld_type"],
            "weld_leg_size_w": geo["weld_leg_size_w"],
            "end_plate_beam_web_weld_type": geo["end_plate_beam_web_weld_type"],
            "end_plate_beam_web_weld_length_lwe": geo["end_plate_beam_web_weld_length_lwe"],
            "end_plate_beam_web_weld_thickness_twe": geo["end_plate_beam_web_weld_thickness_twe"],
        },
    }

    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.PASS
    assert len(result.checks) == 1
