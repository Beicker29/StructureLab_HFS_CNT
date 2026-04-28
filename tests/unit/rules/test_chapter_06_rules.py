from __future__ import annotations

from steel_connections.data.materials_repository import get_bolt_strength_properties
from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.models.errors import StructuredEngineException
from steel_connections.models.output import CheckStatus, GlobalStatus
from steel_connections.models.units import UnitSystem


def test_bueep_rule_set_runs_without_errors(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    assert len(result.checks) >= 13
    assert all(check.status != CheckStatus.ERROR for check in result.checks)
    assert any(check.rule_id.endswith("_vgder") for check in result.checks)

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
    assert prequal.status in {CheckStatus.PASS, CheckStatus.FAIL}
    assert prequal.dcr is None
    limits = prequal.calculation_memory.intermediates["step_1_limits"]
    assert len(limits) >= 30
    assert {"beam_der", "column", "end_plate_der", "end_plate_stiffener_der", "welds", "continuity_plate", "bolts", "table_6_1_der"} <= {
        item["scope"] for item in limits
    }
    beam_shape = next(item for item in limits if item["id"] == "beam_der.shape_family")
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
    assert any(
        note.get("id") in {"section_6_7.beam_flange_to_end_plate_weld_note", "section_6_7.stiffened_end_plate_weld_sequence_note"}
        for note in notes
    )
    assert any(note.get("id") == "section_4_2.installation_requirements" for note in notes)
    assert any(note.get("id") == "section_4_3.quality_control_assurance" for note in notes)
    width_check = next(item for item in limits if item["id"] == "beam_der.bp_ge_bf_plus_margin")
    assert width_check["comparison"] == "le"
    assert width_check["calculated_symbol"] == "bp_pe_vgder"
    assert str(width_check["limit_symbol"]).startswith("bf_vgder + margin")
    assert width_check["result"] == "OK"
    span_depth = next(item for item in limits if item["id"] == "section_2_3_4.clear_span_to_depth_ratio_der")
    assert span_depth["comparison"] == "ge"
    assert span_depth["result"] == "OK"
    compactness_flange = next(item for item in limits if item["id"] == "section_2_3_4.beam_flange_width_to_thickness_der")
    assert compactness_flange["comparison"] == "le"
    assert compactness_flange["result"] == "OK"
    compactness_web = next(item for item in limits if item["id"] == "section_2_3_4.beam_web_width_to_thickness_der")
    assert compactness_web["comparison"] == "le"
    assert compactness_web["result"] == "OK"
    sc_clearance = next(item for item in limits if item["id"] == "section_6_3_1.beam_sc_greater_than_s_threshold_der")
    assert sc_clearance["scope"] == "beam_der"
    assert sc_clearance["comparison"] == "compound"
    assert "> S" in sc_clearance["verification_text"]
    stc_clearance = next(item for item in limits if item["id"] == "section_6_3_1.column_stc_minimum_requirement")
    assert stc_clearance["scope"] == "column"
    assert stc_clearance["comparison"] == "ge"
    tbf_range = next(item for item in limits if item["id"] == "table_6_1.tbf.range_der")
    assert tbf_range["comparison"] == "range"
    assert tbf_range["result"] == "OK"
    slab_iso = next(item for item in limits if item["id"] == "section_2_3_4.slab_isolation_condition")
    assert slab_iso["comparison"] == "equals"
    assert slab_iso["result"] == "OK"
    end_plate_dual = next(item for item in limits if item["id"] == "section_6_3.end_plate_width_dual_limit_der")
    assert end_plate_dual["scope"] == "end_plate_der"
    assert end_plate_dual["comparison"] == "compound"
    assert "bp_pe_vgder <= bbf_vgder +" in end_plate_dual["verification_text"]
    assert "<= bcf" in end_plate_dual["verification_text"]
    end_plate_stiffener = next(item for item in limits if item["id"] == "section_6_3.end_plate_stiffener_height_derived_der")
    assert end_plate_stiffener["scope"] == "end_plate_stiffener_der"
    assert end_plate_stiffener["comparison"] == "compound"
    assert "pfo_pe_vgder + de_pe_vgder" in end_plate_stiffener["verification_text"]
    end_plate_web_weld_type = next(item for item in limits if item["id"] == "section_6_7.end_plate_beam_web_weld_type_allowed")
    assert end_plate_web_weld_type["scope"] == "welds"
    assert end_plate_web_weld_type["comparison"] == "in_set"
    assert end_plate_web_weld_type["result"] == "OK"
    pfo_compound = next(item for item in limits if item["id"] == "table_6_1.edge_pfo_ge_emin_der")
    assert pfo_compound["comparison"] == "compound"
    assert "pso_pe_vgder (=pfo_pe_vgder)" in pfo_compound["verification_text"]
    pfi_compound = next(item for item in limits if item["id"] == "table_6_1.edge_pfi_ge_emin_der")
    assert pfi_compound["comparison"] == "compound"
    assert "psi_pe_vgder = pfi_pe_vgder + tf_vgder - tcp_col" in pfi_compound["verification_text"]


def test_step2_mpr_uses_beam_catalog_zx_for_bueep(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    step2 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bueep_4e.step2_probable_moment_plastic_hinge"
    )
    assert step2.status in {CheckStatus.PASS, CheckStatus.FAIL}
    assert step2.calculation_memory.inputs["ze_source"] == "sections_catalog_zx_by_side"
    assert step2.calculation_memory.inputs["ze_vgder"] is not None


def test_step3_sh_is_reported_for_bseep_8es(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step3 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step3_plastic_hinge_distance"
    )
    assert step3.status == CheckStatus.PASS
    assert step3.calculation_memory.inputs["connection_type"] == "bseep_8es"
    assert step3.demand.unit in {"in", "mm"}
    assert step3.demand.value > 0.0


def test_step6_bolt_capacity_checks_are_reported_for_bseep_8es(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step6_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step6_1_bolt_tension_rupture_vgizq"
    )
    step6_2 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step6_2_bolt_shear_rupture_vgizq"
    )
    assert step6_1.status == CheckStatus.PASS
    assert step6_2.status == CheckStatus.PASS
    assert step6_1.dcr is not None and step6_1.dcr <= 1.0
    assert step6_2.dcr is not None and step6_2.dcr <= 1.0


def test_step7_end_plate_capacity_checks_are_reported_for_bseep_8es(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step7_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step7_1_1_end_plate_flexural_yielding_vgizq"
    )
    step7_2_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step7_2_1_end_plate_shear_yielding_vgizq"
    )
    step7_2_2 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step7_2_2_end_plate_shear_rupture_vgizq"
    )
    step7_3_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step7_3_1_end_plate_hole_tearout_vgizq"
    )
    step7_3_2 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step7_3_2_end_plate_hole_bearing_vgizq"
    )
    assert all(
        check.status in {CheckStatus.PASS, CheckStatus.FAIL}
        for check in (step7_1, step7_2_1, step7_2_2, step7_3_1, step7_3_2)
    )
    assert all(check.dcr is not None for check in (step7_1, step7_2_1, step7_2_2, step7_3_1, step7_3_2))


def test_step8_stiffener_weld_tension_rupture_is_reported_for_bseep_8es(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step8_1_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step8_1_1_stiffener_weld_tension_rupture_vgizq"
    )
    assert step8_1_1.status == CheckStatus.PASS
    assert step8_1_1.dcr is not None and step8_1_1.dcr <= 1.0
    assert step8_1_1.calculation_memory.inputs["weld_type_normalized"] == "cjp"


def test_step9_stiffener_beam_weld_shear_rupture_is_reported_for_bseep_8es(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step9_1_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step9_1_1_stiffener_beam_weld_shear_rupture_vgizq"
    )
    assert step9_1_1.status == CheckStatus.PASS
    assert step9_1_1.dcr is not None and step9_1_1.dcr <= 1.0
    assert step9_1_1.calculation_memory.inputs["weld_type_normalized"] == "cjp"


def test_step10_beam_shear_yielding_is_reported_for_bseep_8es(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step10_1_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step11_1_1_beam_shear_yielding_vgizq"
    )
    assert step10_1_1.status == CheckStatus.PASS
    assert step10_1_1.dcr is not None and step10_1_1.dcr <= 1.0
    assert step10_1_1.calculation_memory.design_factors["phi"] == 1.0
    assert step10_1_1.calculation_memory.inputs["cv1"] > 0.0


def test_step7_yp_is_derived_from_tables_for_bseep_8es(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    step7_1 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step7_1_1_end_plate_flexural_yielding_vgizq"
    )
    assert step7_1.calculation_memory.inputs["yp_pe_vgizq_source"] == "derived_from_aisc358_tables_6_2_6_3_6_4"
    assert step7_1.calculation_memory.inputs["yp_pe_vgizq_table"] == "AISC 358-22 Table 6.4"
    assert step7_1.calculation_memory.inputs["yp_pe_vgizq_case"] in {"Case 1 (de <= s)", "Case 2 (de > s)"}
    assert step7_1.calculation_memory.inputs["yp_pe_vgizq"]["value"] > 0.0


def test_ry_input_is_forbidden_and_derived_from_catalog(bueep_4e_payload: dict) -> None:
    bueep_4e_payload["design_factors"]["ry"] = 1.1
    try:
        parse_and_validate_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["design_factors.ry"]
    else:
        raise AssertionError("Expected validation error because design_factors.ry is no longer an allowed input.")


def test_ze_input_is_forbidden(bueep_4e_payload: dict) -> None:
    bueep_4e_payload.setdefault("procedure", {})
    bueep_4e_payload["procedure"]["beam_plastic_section_modulus_ze"] = {"value": 80.0, "unit": "in3"}
    try:
        parse_and_validate_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["procedure.beam_plastic_section_modulus_ze"]
    else:
        raise AssertionError(
            "Expected validation error because procedure.beam_plastic_section_modulus_ze is no longer an allowed input."
        )


def test_lh_input_is_forbidden(bueep_4e_payload: dict) -> None:
    bueep_4e_payload.setdefault("procedure", {})
    bueep_4e_payload["procedure"]["beam_span_between_plastic_hinges_lh"] = {"value": 240.0, "unit": "in"}
    try:
        parse_and_validate_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["procedure.beam_span_between_plastic_hinges_lh"]
    else:
        raise AssertionError(
            "Expected validation error because procedure.beam_span_between_plastic_hinges_lh is no longer an allowed input."
        )


def test_yp_input_is_forbidden(bueep_4e_payload: dict) -> None:
    bueep_4e_payload.setdefault("procedure", {})
    bueep_4e_payload["procedure"]["yield_line_parameter_yp"] = {"value": 7.0, "unit": "in"}
    try:
        parse_and_validate_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["procedure.yield_line_parameter_yp"]
    else:
        raise AssertionError(
            "Expected validation error because procedure.yield_line_parameter_yp is no longer an allowed input."
        )


def test_yc_unstiffened_input_is_forbidden(bueep_4e_payload: dict) -> None:
    bueep_4e_payload.setdefault("procedure", {})
    bueep_4e_payload["procedure"]["column_yield_line_parameter_yc_unstiffened"] = {"value": 250.0, "unit": "in"}
    try:
        parse_and_validate_payload(bueep_4e_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["procedure.column_yield_line_parameter_yc_unstiffened"]
    else:
        raise AssertionError(
            "Expected validation error because procedure.column_yield_line_parameter_yc_unstiffened is no longer an allowed input."
        )


def test_yc_stiffened_input_is_forbidden(bseep_8es_payload: dict) -> None:
    bseep_8es_payload.setdefault("procedure", {})
    bseep_8es_payload["procedure"]["column_yield_line_parameter_yc_stiffened"] = {"value": 275.0, "unit": "in"}
    try:
        parse_and_validate_payload(bseep_8es_payload)
    except StructuredEngineException as exc:
        assert exc.error.missing_fields == ["procedure.column_yield_line_parameter_yc_stiffened"]
    else:
        raise AssertionError(
            "Expected validation error because procedure.column_yield_line_parameter_yc_stiffened is no longer an allowed input."
        )


def test_bseep_prequalification_limits_fail_when_pitch_is_below_3db(bseep_8es_payload: dict) -> None:
    bseep_8es_payload["geometry"]["pb"]["value"] = 2.0
    bseep_8es_payload["geometry"]["pb_vgizq"]["value"] = 2.0
    bseep_8es_payload["geometry"]["pb_vgder"]["value"] = 2.0
    result = run_case_payload(bseep_8es_payload)
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bseep_8es.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    pitch_check = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] in {"table_6_1.pitch_pb_ge_3db_der", "table_6_1.pitch_pb_ge_3db_izq"}
    )
    assert pitch_check["result"] == "NO_OK"
    assert pitch_check["comparison"] == "compound"


def test_bseep_prequalification_includes_stiffener_strength_checks(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bseep_8es.prequalification_limits")
    assert prequal.status in {CheckStatus.PASS, CheckStatus.FAIL}
    limits = prequal.calculation_memory.intermediates["step_1_limits"]
    stiffener_ts = next(item for item in limits if item["id"] == "section_6_7_1.stiffener_thickness_minimum_izq")
    stiffener_buckling = next(item for item in limits if item["id"] == "section_6_7_1.stiffener_local_buckling_limit_izq")
    stiffener_gage = next(item for item in limits if item["id"] == "section_6_3_1.stiffener_bolt_gage_clearance_izq")
    assert stiffener_ts["scope"] == "end_plate_stiffener_izq"
    assert stiffener_ts["comparison"] == "ge"
    assert stiffener_ts["result"] in {"OK", "NO_OK"}
    assert stiffener_buckling["scope"] == "end_plate_stiffener_izq"
    assert stiffener_buckling["comparison"] == "le"
    assert stiffener_buckling["result"] in {"OK", "NO_OK"}
    assert stiffener_gage["scope"] == "end_plate_stiffener_izq"
    assert stiffener_gage["comparison"] == "ge"
    assert stiffener_gage["result"] in {"OK", "NO_OK"}


def test_bseep8es_prequalification_limits_fail_when_pb_is_outside_89_95mm_range(bseep_8es_payload: dict) -> None:
    bseep_8es_payload["geometry"]["pb"]["value"] = 96.0
    bseep_8es_payload["geometry"]["pb_vgizq"]["value"] = 96.0
    bseep_8es_payload["geometry"]["pb_vgder"]["value"] = 96.0
    result = run_case_payload(bseep_8es_payload)
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bseep_8es.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    pb_compound_all = [
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] in {"table_6_1.pitch_pb_ge_3db_der", "table_6_1.pitch_pb_ge_3db_izq"}
    ]
    assert pb_compound_all
    assert any(item["result"] == "NO_OK" for item in pb_compound_all)
    assert all(item["comparison"] == "compound" for item in pb_compound_all)


def test_bueep_prequalification_limits_fail_when_thin_continuity_plate_weld_type_is_invalid(
    bueep_4e_payload: dict,
) -> None:
    bueep_4e_payload["geometry"]["continuity_plate_thickness"]["value"] = 0.30
    bueep_4e_payload["geometry"]["continuity_plate_weld_type"] = "single_bevel_groove"
    result = run_case_payload(bueep_4e_payload)
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status == CheckStatus.FAIL
    weld_type_check = next(
        item
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
        if item["id"] == "section_6_3.continuity_plate_weld_type_for_thin_plate"
    )
    assert weld_type_check["result"] == "NO_OK"
    assert weld_type_check["comparison"] == "conditional_allowed_set"


def test_bueep_prequalification_limits_allow_missing_continuity_plate_weld_type(
    bueep_4e_payload: dict,
) -> None:
    del bueep_4e_payload["geometry"]["continuity_plate_weld_type"]
    result = run_case_payload(bueep_4e_payload)
    prequal = next(check for check in result.checks if check.rule_id == "AISC358.06.3.bueep_4e.prequalification_limits")
    assert prequal.status in {CheckStatus.PASS, CheckStatus.FAIL}
    assert all(
        item["id"] != "section_6_3.continuity_plate_weld_type_declared"
        for item in prequal.calculation_memory.intermediates["step_1_limits"]
    )


def test_bueep_prequalification_limits_fail_when_double_sided_fillet_with_thick_plate(
    bueep_4e_payload: dict,
) -> None:
    bueep_4e_payload["geometry"]["continuity_plate_weld_type"] = "double_sided_fillet"
    bueep_4e_payload["geometry"]["continuity_plate_thickness"]["value"] = 0.625
    result = run_case_payload(bueep_4e_payload)
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


def test_step12_column_flange_local_bending_uses_side_specific_mf(bseep_8es_payload: dict) -> None:
    # Force side-specific Step 5 Mf usage (no legacy global override).
    if "probable_moment_column_face" in bseep_8es_payload.get("loads", {}):
        bseep_8es_payload["loads"]["probable_moment_column_face"] = None
    # Force asymmetric side demands so left/right Mf must differ.
    bseep_8es_payload["loads"]["beam_left_vgravity"]["value"] = 8.0
    bseep_8es_payload["loads"]["beam_right_vgravity"]["value"] = 14.0
    result = run_case_payload(bseep_8es_payload)
    step5 = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step5_probable_moment_face_column"
    )
    step12_izq = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step12_1_1_column_flange_local_bending_vgizq"
    )
    step12_der = next(
        check
        for check in result.checks
        if check.rule_id == "AISC358.06.7.bseep_8es.step12_1_1_column_flange_local_bending_vgder"
    )

    mf_izqmax = float(step5.calculation_memory.intermediates["mf_izqmax"])
    mf_dermax = float(step5.calculation_memory.intermediates["mf_dermax"])
    mf_step12_izq = float(step12_izq.calculation_memory.inputs["mf"]["value"])
    mf_step12_der = float(step12_der.calculation_memory.inputs["mf"]["value"])

    assert abs(mf_step12_izq - mf_izqmax) < 1e-6
    assert abs(mf_step12_der - mf_dermax) < 1e-6
    assert abs(mf_step12_izq - mf_step12_der) > 1e-6


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
                "weld_4": {
                    "weld_type": geo["continuity_plate_weld_type"],
                    "thickness_vgder": geo["t_w4_vgder"],
                    "nl_vgder": geo["nl_w4_vgder"],
                    "backing_thickness_vgder": geo["t_w4_1_vgder"],
                    "kds_w4_vgder": geo["kds_w4_vgder"],
                },
                "weld_3": {
                    "weld_type": geo["end_plate_beam_web_weld_type"],
                    "thickness": geo["end_plate_beam_web_weld_thickness_twe"],
                },
            },
        }

    result = run_case_payload(bueep_4e_payload)
    assert len(result.checks) >= 13
    assert all(check.status != CheckStatus.ERROR for check in result.checks)
