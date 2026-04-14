from __future__ import annotations

from typing import Any

from steel_connections.codes.aisc358.chapter_06 import (
    compute_minimum_bolt_spacing,
    compute_minimum_edge_distance_standard_hole,
    compute_column_flange_design_force_from_yield_line,
    compute_column_flange_required_thickness,
    compute_column_web_local_crippling_strength,
    compute_column_web_local_yielding_strength,
    compute_cpr,
    compute_beam_flange_force_from_mf,
    compute_mf,
    compute_mpr,
    compute_bolt_bearing_tearout_capacity,
    compute_required_bolt_diameter,
    compute_required_end_plate_thickness,
    compute_bolt_shear_rupture_capacity,
    compute_end_plate_shear_rupture_capacity,
    compute_end_plate_shear_yielding_capacity,
    compute_flange_slenderness_limit,
    compute_flange_slenderness_ratio,
    compute_minimum_stiffener_length,
    compute_sh,
    compute_required_stiffener_thickness,
    compute_stiffener_slenderness_ratio_limit,
    compute_web_slenderness_limit,
    compute_web_slenderness_ratio,
    compute_vh,
)
from steel_connections.data.sections_repository import get_beam_profile_properties, get_column_profile_properties
from steel_connections.models.errors import missing_required_input_error
from steel_connections.models.input import AISC358MomentCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import Quantity


def _resolve_path(obj: Any, field_path: str) -> Any:
    current = obj
    for item in field_path.split("."):
        current = getattr(current, item)
    return current


def _require(case: AISC358MomentCase, field_path: str, rule_binding: object) -> Any:
    value = _resolve_path(case, field_path)
    if value is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[field_path],
            message=f"Required input '{field_path}' is missing for applicable rule.",
        )
    return value


def _build_result(
    *,
    rule_binding: object,
    demand: Quantity,
    capacity: Quantity,
    equation: str,
    inputs: dict[str, Any],
    intermediates: dict[str, Any],
    design_factors: dict[str, float],
    units_trace: dict[str, str],
) -> CheckResult:
    dcr = demand.value / capacity.value
    status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        status=status,
        calculation_memory=CalculationMemory(
            inputs=inputs,
            intermediates=intermediates,
            design_factors=design_factors,
            equation=equation,
            units_trace=units_trace,
            final_capacity=capacity,
        ),
        notes=None,
    )


def _compression_bolt_count(case: AISC358MomentCase) -> int:
    if case.connection_type == "bseep_8es":
        return 8
    return 4


def _beam_profile(case: AISC358MomentCase) -> dict[str, Quantity]:
    return get_beam_profile_properties(
        beam_shape=case.sections.beam_shape,
        unit_system=case.units_system,
    )


def _column_profile(case: AISC358MomentCase) -> dict[str, Quantity]:
    if case.sections.column_shape is None:
        raise missing_required_input_error(
            rule_id="AISC358.06.7.column_profile_required",
            source_document="AISC 358-22",
            missing_fields=["sections.column_shape"],
            message="Required input 'sections.column_shape' is missing for column-side checks.",
        )
    return get_column_profile_properties(
        column_shape=case.sections.column_shape,
        unit_system=case.units_system,
    )


def _require_procedure(case: AISC358MomentCase, field_name: str, rule_binding: object) -> Any:
    if case.procedure is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["procedure"],
            message="Required object 'procedure' is missing for applicable rule.",
        )
    value = getattr(case.procedure, field_name)
    if value is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[f"procedure.{field_name}"],
            message=f"Required input 'procedure.{field_name}' is missing for applicable rule.",
        )
    return value


def _column_yc_parameter(case: AISC358MomentCase, rule_binding: object) -> Quantity:
    if case.connection_type == "bueep_4e":
        return _require_procedure(case, "column_yield_line_parameter_yc_unstiffened", rule_binding)
    return _require_procedure(case, "column_yield_line_parameter_yc_stiffened", rule_binding)


def _compute_mpr(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, float]]:
    fy = _require(case, "materials.beam_fy", rule_binding)
    fu = _require(case, "materials.beam_fu", rule_binding)
    ry = _require(case, "design_factors.ry", rule_binding)
    ze = _require_procedure(case, "beam_plastic_section_modulus_ze", rule_binding)
    return compute_mpr(
        fy=fy,
        fu=fu,
        ry=ry,
        ze=ze,
        unit_system=case.units_system,
    )


def _beam_plastic_modulus_zx(case: AISC358MomentCase, rule_binding: object) -> Quantity:
    beam_profile = _beam_profile(case)
    zx = beam_profile.get("zx")
    if zx is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["sections.beam_shape"],
            message=(
                "Catalog property 'Zx' for sections.beam_shape is required for "
                "AISC 358 Chapter 6 Step 1 in BSEEP connections."
            ),
        )
    return zx


def _profile_kdes(profile: dict[str, Quantity], *, role: str, rule_binding: object) -> Quantity:
    kdes = profile.get("kdes")
    if kdes is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[f"sections.{role}_shape"],
            message=(
                f"Catalog property 'kdes' for sections.{role}_shape is required for "
                "compactness review in Step 1a."
            ),
        )
    return kdes


def _compute_sh(case: AISC358MomentCase, rule_binding: object) -> Quantity:
    beam_profile = _beam_profile(case)
    stiffener_length = case.geometry.stiffener_length
    end_plate_thickness = case.geometry.end_plate_thickness
    if case.connection_type == "bueep_4e":
        stiffener_length = None
        end_plate_thickness = None
    else:
        stiffener_length = _require(case, "geometry.stiffener_length", rule_binding)
        end_plate_thickness = _require(case, "geometry.end_plate_thickness", rule_binding)
    return compute_sh(
        connection_type=case.connection_type,
        beam_depth=beam_profile["d"],
        beam_flange_width=beam_profile["bf"],
        stiffener_length=stiffener_length,
        end_plate_thickness=end_plate_thickness,
        unit_system=case.units_system,
    )


def _compute_vh(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, float]]:
    mpr, _ = _compute_mpr(case, rule_binding)
    lh = _require_procedure(case, "beam_span_between_plastic_hinges_lh", rule_binding)
    vgravity = _require(case, "loads.beam_gravity_shear_between_hinges", rule_binding)
    return compute_vh(
        mpr=mpr,
        lh=lh,
        vgravity_between_hinges=vgravity,
        unit_system=case.units_system,
    )


def _compute_mf(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, float]]:
    mpr, mpr_intermediate = _compute_mpr(case, rule_binding)
    sh = _compute_sh(case, rule_binding)
    vh, vh_intermediate = _compute_vh(case, rule_binding)
    mf = compute_mf(
        mpr=mpr,
        vh=vh,
        sh=sh,
        unit_system=case.units_system,
    )
    return mf, {**mpr_intermediate, **vh_intermediate, "sh": sh.value, "mpr": mpr.value, "vh": vh.value}


def run_bolt_gage_limit(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    gage = _require(case, "geometry.bolt_gage", rule_binding)
    beam_flange_width = _beam_profile(case)["bf"]

    return _build_result(
        rule_binding=rule_binding,
        demand=gage,
        capacity=beam_flange_width,
        equation="g <= bf (Section 6.6.1)",
        inputs={
            "bolt_gage": gage.model_dump(),
            "beam_flange_width": beam_flange_width.model_dump(),
        },
        intermediates={},
        design_factors={},
        units_trace={"g": gage.unit, "bf": beam_flange_width.unit},
    )


def run_step1_probable_moment_plastic_hinge(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    fy = _require(case, "materials.beam_fy", rule_binding)
    fu = _require(case, "materials.beam_fu", rule_binding)
    ry = _require(case, "design_factors.ry", rule_binding)
    if case.connection_type in {"bseep_4es", "bseep_8es"}:
        ze = _beam_plastic_modulus_zx(case, rule_binding)
        ze_source = "sections_catalog_zx"
        ze_input = _require_procedure(case, "beam_plastic_section_modulus_ze", rule_binding)
    else:
        ze = _require_procedure(case, "beam_plastic_section_modulus_ze", rule_binding)
        ze_source = "procedure_input"
        ze_input = ze
    mpr, intermediates = compute_mpr(
        fy=fy,
        fu=fu,
        ry=ry,
        ze=ze,
        unit_system=case.units_system,
    )
    stated_mpr = case.loads.probable_moment_plastic_hinge
    demand = mpr
    capacity = stated_mpr if stated_mpr is not None else mpr
    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation="Mpr = Cpr * Ry * Fy * Ze (Eq. 2.4-1 and Eq. 2.4-2)",
        inputs={
            "beam_fy": fy.model_dump(),
            "beam_fu": fu.model_dump(),
            "ry": ry,
            "ze": ze.model_dump(),
            "ze_source": ze_source,
            "ze_input": ze_input.model_dump(),
            "stated_mpr": stated_mpr.model_dump() if stated_mpr is not None else None,
        },
        intermediates=intermediates,
        design_factors={},
        units_trace={"mpr_computed": mpr.unit, "mpr_stated": capacity.unit},
    )


def run_step1a_member_compactness(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    column_profile = _column_profile(case)

    ry = _require(case, "design_factors.ry", rule_binding)
    beam_ductility = _require(case, "design_factors.member_ductility_demand_beam", rule_binding)
    column_ductility = _require(case, "design_factors.member_ductility_demand_column", rule_binding)
    ca_beam = _require(case, "design_factors.compactness_ca_beam", rule_binding)
    ca_column = _require(case, "design_factors.compactness_ca_column", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    beam_fy = _require(case, "materials.beam_fy", rule_binding)
    column_fy = _require(case, "materials.column_fy", rule_binding)

    beam_flange_ratio = compute_flange_slenderness_ratio(
        flange_width=beam_profile["bf"],
        flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    beam_web_ratio, beam_web_intermediate = compute_web_slenderness_ratio(
        section_depth=beam_profile["d"],
        k_design=_profile_kdes(beam_profile, role="beam", rule_binding=rule_binding),
        web_thickness=beam_profile["tw"],
        unit_system=case.units_system,
    )
    column_flange_ratio = compute_flange_slenderness_ratio(
        flange_width=column_profile["bf"],
        flange_thickness=column_profile["tf"],
        unit_system=case.units_system,
    )
    column_web_ratio, column_web_intermediate = compute_web_slenderness_ratio(
        section_depth=column_profile["d"],
        k_design=_profile_kdes(column_profile, role="column", rule_binding=rule_binding),
        web_thickness=column_profile["tw"],
        unit_system=case.units_system,
    )

    beam_flange_limit = compute_flange_slenderness_limit(
        elastic_modulus=elastic_modulus,
        fy=beam_fy,
        ry=ry,
        member_ductility_demand=beam_ductility,
        unit_system=case.units_system,
    )
    beam_web_limit = compute_web_slenderness_limit(
        elastic_modulus=elastic_modulus,
        fy=beam_fy,
        ry=ry,
        ca=ca_beam,
        member_ductility_demand=beam_ductility,
        unit_system=case.units_system,
    )
    column_flange_limit = compute_flange_slenderness_limit(
        elastic_modulus=elastic_modulus,
        fy=column_fy,
        ry=ry,
        member_ductility_demand=column_ductility,
        unit_system=case.units_system,
    )
    column_web_limit = compute_web_slenderness_limit(
        elastic_modulus=elastic_modulus,
        fy=column_fy,
        ry=ry,
        ca=ca_column,
        member_ductility_demand=column_ductility,
        unit_system=case.units_system,
    )

    beam_flange_dcr = beam_flange_ratio / beam_flange_limit
    beam_web_dcr = beam_web_ratio / beam_web_limit
    column_flange_dcr = column_flange_ratio / column_flange_limit
    column_web_dcr = column_web_ratio / column_web_limit
    max_dcr = max(beam_flange_dcr, beam_web_dcr, column_flange_dcr, column_web_dcr)

    return _build_result(
        rule_binding=rule_binding,
        demand=Quantity(value=max_dcr, unit="ratio"),
        capacity=Quantity(value=1.0, unit="ratio"),
        equation=(
            "Compactness checks per AISC 341-22 Table D1.1 "
            "(unstiffened flange b/t and stiffened web h/tw limits)"
        ),
        inputs={
            "beam_shape": case.sections.beam_shape,
            "column_shape": case.sections.column_shape,
            "member_ductility_demand_beam": beam_ductility,
            "member_ductility_demand_column": column_ductility,
            "elastic_modulus": elastic_modulus.model_dump(),
            "beam_fy": beam_fy.model_dump(),
            "column_fy": column_fy.model_dump(),
            "ry": ry,
            "compactness_ca_beam": ca_beam,
            "compactness_ca_column": ca_column,
            "beam_flange_ratio_b_over_t": beam_flange_ratio,
            "beam_web_ratio_h_over_tw": beam_web_ratio,
            "column_flange_ratio_b_over_t": column_flange_ratio,
            "column_web_ratio_h_over_tw": column_web_ratio,
        },
        intermediates={
            "beam_flange_limit": beam_flange_limit,
            "beam_web_limit": beam_web_limit,
            "column_flange_limit": column_flange_limit,
            "column_web_limit": column_web_limit,
            "beam_flange_dcr": beam_flange_dcr,
            "beam_web_dcr": beam_web_dcr,
            "column_flange_dcr": column_flange_dcr,
            "column_web_dcr": column_web_dcr,
            "beam_web_clear_depth": beam_web_intermediate["clear_web_depth"],
            "column_web_clear_depth": column_web_intermediate["clear_web_depth"],
        },
        design_factors={
            "ry": ry,
            "compactness_ca_beam": ca_beam,
            "compactness_ca_column": ca_column,
        },
        units_trace={
            "all_ratios": "ratio",
            "elastic_modulus": elastic_modulus.unit,
            "beam_fy": beam_fy.unit,
            "column_fy": column_fy.unit,
        },
    )


def run_step2_plastic_hinge_distance(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    sh = _compute_sh(case, rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=sh,
        capacity=sh,
        equation="Sh from connection-specific rules (Eq. 6.7-1 or Eq. 6.7-2)",
        inputs={
            "connection_type": case.connection_type,
            "beam_shape": case.sections.beam_shape,
            "stiffener_length": case.geometry.stiffener_length.model_dump()
            if case.geometry.stiffener_length is not None
            else None,
            "end_plate_thickness": case.geometry.end_plate_thickness.model_dump()
            if case.geometry.end_plate_thickness is not None
            else None,
        },
        intermediates={},
        design_factors={},
        units_trace={"sh": sh.unit},
    )


def run_step3_shear_at_plastic_hinge(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vh, intermediates = _compute_vh(case, rule_binding)
    stated_vh = case.loads.shear_plastic_hinge
    demand = vh
    capacity = stated_vh if stated_vh is not None else vh
    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation="Vh = 2*Mpr/Lh + Vgravity (Eq. 2.4-3)",
        inputs={
            "lh": _require_procedure(case, "beam_span_between_plastic_hinges_lh", rule_binding).model_dump(),
            "vgravity_between_hinges": _require(
                case,
                "loads.beam_gravity_shear_between_hinges",
                rule_binding,
            ).model_dump(),
            "stated_vh": stated_vh.model_dump() if stated_vh is not None else None,
        },
        intermediates=intermediates,
        design_factors={},
        units_trace={"vh_computed": vh.unit, "vh_stated": capacity.unit},
    )


def run_step4_probable_moment_face_column(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf, intermediates = _compute_mf(case, rule_binding)
    stated_mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=mf,
        capacity=stated_mf,
        equation="Mf = Mpr + Vh * Sh (Eq. 2.4-4)",
        inputs={"stated_mf": stated_mf.model_dump()},
        intermediates=intermediates,
        design_factors={},
        units_trace={"mf_computed": mf.unit, "mf_stated": stated_mf.unit},
    )


def run_step5_preliminary_geometry_selection(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    g = _require(case, "geometry.bolt_gage", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    if case.materials.bolt_grade is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["materials.bolt_grade"],
            message="Required input 'materials.bolt_grade' is missing for Step 5.",
        )
    return _build_result(
        rule_binding=rule_binding,
        demand=db,
        capacity=db,
        equation="Step 5 preliminary geometry and bolt grade selection (Section 6.7.1)",
        inputs={
            "connection_type": case.connection_type,
            "bolt_gage": g.model_dump(),
            "bolt_diameter": db.model_dump(),
            "bolt_grade": case.materials.bolt_grade,
        },
        intermediates={},
        design_factors={},
        units_trace={"db": db.unit},
    )


def run_section63_prequalification_limits(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    g = _require(case, "geometry.bolt_gage", rule_binding)
    bp = _require(case, "geometry.end_plate_width", rule_binding)
    pb = _require(case, "geometry.pb", rule_binding)
    de = _require(case, "geometry.de", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pfi = _require(case, "geometry.pfi", rule_binding)
    bf = _beam_profile(case)["bf"]

    min_spacing = compute_minimum_bolt_spacing(
        bolt_diameter=db,
        unit_system=case.units_system,
    )
    bp_margin = 1.0 if case.units_system.value == "US" else 25.0
    min_bp = Quantity(value=bf.value + bp_margin, unit=bf.unit)
    min_edge, edge_intermediate = compute_minimum_edge_distance_standard_hole(
        bolt_diameter=db,
        unit_system=case.units_system,
    )
    per_check = {
        "bp_ge_bf_plus_margin": {"actual": bp.value, "required": min_bp.value},
        "bolt_gage_g_ge_3db": {"actual": g.value, "required": min_spacing.value},
        "pitch_pb_ge_3db": {"actual": pb.value, "required": min_spacing.value},
        "edge_de_ge_emin": {"actual": de.value, "required": min_edge.value},
        "edge_pfo_ge_emin": {"actual": pfo.value, "required": min_edge.value},
        "edge_pfi_ge_emin": {"actual": pfi.value, "required": min_edge.value},
    }
    dcr_by_check = {name: values["required"] / values["actual"] for name, values in per_check.items()}
    max_dcr = max(dcr_by_check.values())

    return _build_result(
        rule_binding=rule_binding,
        demand=Quantity(value=max_dcr, unit="ratio"),
        capacity=Quantity(value=1.0, unit="ratio"),
        equation=(
            "AISC 358-22w Section 6.3 prequalification geometry limits: bp >= bf + 25 mm (or +1 in in US); spacing >= 3db; "
            "minimum edge distances per Table J3.4 for standard holes"
        ),
        inputs={
            "bolt_diameter": db.model_dump(),
            "beam_flange_width_bf": bf.model_dump(),
            "end_plate_width_bp": bp.model_dump(),
            "bolt_gage_g": g.model_dump(),
            "pitch_pb": pb.model_dump(),
            "edge_de": de.model_dump(),
            "edge_pfo": pfo.model_dump(),
            "edge_pfi": pfi.model_dump(),
        },
        intermediates={
            "minimum_spacing_3db": min_spacing.model_dump(),
            "minimum_bp_bf_plus_margin": min_bp.model_dump(),
            "bp_margin": bp_margin,
            "minimum_edge_distance_j34": min_edge.model_dump(),
            "j34_lookup": edge_intermediate,
            "per_check": per_check,
            "dcr_by_check": dcr_by_check,
            "max_dcr": max_dcr,
        },
        design_factors={},
        units_trace={
            "db": db.unit,
            "bf": bf.unit,
            "bp": bp.unit,
            "g": g.unit,
            "pb": pb.unit,
            "de": de.unit,
            "pfo": pfo.unit,
            "pfi": pfi.unit,
            "ratios": "ratio",
        },
    )


def run_step6_required_bolt_diameter(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    fnt = _require(case, "materials.bolt_fnt", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)
    distances = _require_procedure(case, "tension_bolt_line_distances", rule_binding)
    db_req, intermediates = compute_required_bolt_diameter(
        mf=mf,
        bolt_fnt=fnt,
        phi_n=phi_n,
        bolt_line_distances=distances,
        n_bolts_per_line=2,
        unit_system=case.units_system,
    )
    db_trial = _require(case, "geometry.bolt_diameter", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=db_req,
        capacity=db_trial,
        equation="db,req from Eq. 6.7-3/6.7-4",
        inputs={
            "mf": mf.model_dump(),
            "bolt_fnt": fnt.model_dump(),
            "phi_n": phi_n,
            "tension_bolt_line_distances": [item.model_dump() for item in distances],
            "db_trial": db_trial.model_dump(),
        },
        intermediates=intermediates,
        design_factors={"phi_n": phi_n},
        units_trace={"db_req": db_req.unit, "db_trial": db_trial.unit},
    )


def run_step7_select_trial_bolt(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    fnt = _require(case, "materials.bolt_fnt", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)
    distances = _require_procedure(case, "tension_bolt_line_distances", rule_binding)
    db_req, _ = compute_required_bolt_diameter(
        mf=mf,
        bolt_fnt=fnt,
        phi_n=phi_n,
        bolt_line_distances=distances,
        n_bolts_per_line=2,
        unit_system=case.units_system,
    )
    db_trial = _require(case, "geometry.bolt_diameter", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=db_req,
        capacity=db_trial,
        equation="db,trial >= db,req (Section 6.7.1 Step 7)",
        inputs={"db_req": db_req.model_dump(), "db_trial": db_trial.model_dump()},
        intermediates={},
        design_factors={},
        units_trace={"db_req": db_req.unit, "db_trial": db_trial.unit},
    )


def run_step8_required_end_plate_thickness(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    beam_depth = _beam_profile(case)["d"]
    end_plate_fy = _require(case, "materials.end_plate_fy", rule_binding)
    yp = _require_procedure(case, "yield_line_parameter_yp", rule_binding)
    phi_d = _require(case, "design_factors.phi_d", rule_binding)
    tp_req, intermediates = compute_required_end_plate_thickness(
        mf=mf,
        beam_depth=beam_depth,
        end_plate_fy=end_plate_fy,
        yp=yp,
        phi_d=phi_d,
        unit_system=case.units_system,
    )
    tp_trial = _require(case, "geometry.end_plate_thickness", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=tp_req,
        capacity=tp_trial,
        equation="tp,req from Eq. 6.7-5 with Yp from Tables 6.2-6.4",
        inputs={
            "mf": mf.model_dump(),
            "beam_depth": beam_depth.model_dump(),
            "end_plate_fy": end_plate_fy.model_dump(),
            "yp": yp.model_dump(),
            "tp_trial": tp_trial.model_dump(),
        },
        intermediates=intermediates,
        design_factors={"phi_d": phi_d},
        units_trace={"tp_req": tp_req.unit, "tp_trial": tp_trial.unit},
    )


def run_step9_select_end_plate_thickness(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    tp_req = run_step8_required_end_plate_thickness(case, rule_binding).demand
    tp_trial = _require(case, "geometry.end_plate_thickness", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=tp_req,
        capacity=tp_trial,
        equation="tp,trial >= tp,req (Section 6.7.1 Step 9)",
        inputs={"tp_req": tp_req.model_dump(), "tp_trial": tp_trial.model_dump()},
        intermediates={},
        design_factors={},
        units_trace={"tp_req": tp_req.unit, "tp_trial": tp_trial.unit},
    )


def run_step10_factored_beam_flange_force(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    ffu, intermediates = compute_beam_flange_force_from_mf(
        mf=mf,
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=ffu,
        capacity=ffu,
        equation="Ffu = Mf / (d - tbf) (Eq. 6.7-6)",
        inputs={
            "mf": mf.model_dump(),
            "beam_shape": case.sections.beam_shape,
            "beam_depth": beam_profile["d"].model_dump(),
            "beam_flange_thickness": beam_profile["tf"].model_dump(),
        },
        intermediates=intermediates,
        design_factors={},
        units_trace={"ffu": ffu.unit},
    )


def run_end_plate_shear_yielding_4e(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    beam_depth = beam_profile["d"]
    beam_flange_thickness = beam_profile["tf"]
    end_plate_fy = _require(case, "materials.end_plate_fy", rule_binding)
    end_plate_width = _require(case, "geometry.end_plate_width", rule_binding)
    end_plate_thickness = _require(case, "geometry.end_plate_thickness", rule_binding)
    beam_flange_width = beam_profile["bf"]
    phi_d = _require(case, "design_factors.phi_d", rule_binding)

    flange_force, ffu_intermediate = compute_beam_flange_force_from_mf(
        mf=mf,
        beam_depth=beam_depth,
        beam_flange_thickness=beam_flange_thickness,
        unit_system=case.units_system,
    )
    demand = Quantity(value=flange_force.value / 2.0, unit=flange_force.unit)
    capacity, cap_intermediate = compute_end_plate_shear_yielding_capacity(
        end_plate_fy=end_plate_fy,
        end_plate_width=end_plate_width,
        end_plate_thickness=end_plate_thickness,
        beam_flange_width=beam_flange_width,
        phi_d=phi_d,
        unit_system=case.units_system,
    )

    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation="Ffu/2 <= phi_d * 0.6 * Fyp * bp_eff * tp (Eq. 6.7-7, with Ffu from Eq. 6.7-6)",
        inputs={
            "beam_shape": case.sections.beam_shape,
            "mf": mf.model_dump(),
            "beam_depth": beam_depth.model_dump(),
            "beam_flange_thickness": beam_flange_thickness.model_dump(),
            "end_plate_fy": end_plate_fy.model_dump(),
            "end_plate_width": end_plate_width.model_dump(),
            "beam_flange_width": beam_flange_width.model_dump(),
            "end_plate_thickness": end_plate_thickness.model_dump(),
        },
        intermediates={**ffu_intermediate, **cap_intermediate, "ffu": flange_force.value},
        design_factors={"phi_d": phi_d},
        units_trace={
            "mf": mf.unit,
            "d": beam_depth.unit,
            "tbf": beam_flange_thickness.unit,
            "demand": demand.unit,
            "capacity": capacity.unit,
        },
    )


def run_end_plate_shear_rupture_4e(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    beam_depth = beam_profile["d"]
    beam_flange_thickness = beam_profile["tf"]
    end_plate_fu = _require(case, "materials.end_plate_fu", rule_binding)
    end_plate_width = _require(case, "geometry.end_plate_width", rule_binding)
    end_plate_thickness = _require(case, "geometry.end_plate_thickness", rule_binding)
    bolt_diameter = _require(case, "geometry.bolt_diameter", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)

    flange_force, ffu_intermediate = compute_beam_flange_force_from_mf(
        mf=mf,
        beam_depth=beam_depth,
        beam_flange_thickness=beam_flange_thickness,
        unit_system=case.units_system,
    )
    demand = Quantity(value=flange_force.value / 2.0, unit=flange_force.unit)
    capacity, cap_intermediate = compute_end_plate_shear_rupture_capacity(
        end_plate_fu=end_plate_fu,
        end_plate_width=end_plate_width,
        end_plate_thickness=end_plate_thickness,
        bolt_diameter=bolt_diameter,
        phi_n=phi_n,
        unit_system=case.units_system,
    )

    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation="Ffu/2 <= phi_n * 0.6 * Fup * An (Eq. 6.7-8, with Ffu from Eq. 6.7-6)",
        inputs={
            "beam_shape": case.sections.beam_shape,
            "mf": mf.model_dump(),
            "beam_depth": beam_depth.model_dump(),
            "beam_flange_thickness": beam_flange_thickness.model_dump(),
            "end_plate_fu": end_plate_fu.model_dump(),
            "end_plate_width": end_plate_width.model_dump(),
            "end_plate_thickness": end_plate_thickness.model_dump(),
            "bolt_diameter": bolt_diameter.model_dump(),
        },
        intermediates={**ffu_intermediate, **cap_intermediate, "ffu": flange_force.value},
        design_factors={"phi_n": phi_n},
        units_trace={
            "mf": mf.unit,
            "demand": demand.unit,
            "capacity": capacity.unit,
        },
    )


def run_bolt_shear_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vu = _require(case, "loads.required_connection_shear", rule_binding)
    bolt_fnv = _require(case, "materials.bolt_fnv", rule_binding)
    bolt_diameter = _require(case, "geometry.bolt_diameter", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)

    n_bolts = _compression_bolt_count(case)
    capacity, intermediates = compute_bolt_shear_rupture_capacity(
        bolt_fnv=bolt_fnv,
        bolt_diameter=bolt_diameter,
        n_bolts_compression=n_bolts,
        phi_n=phi_n,
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=vu,
        capacity=capacity,
        equation="Vu <= phi_n * nb * Fnv * Ab (Eq. 6.7-11)",
        inputs={
            "vu": vu.model_dump(),
            "bolt_fnv": bolt_fnv.model_dump(),
            "bolt_diameter": bolt_diameter.model_dump(),
            "n_bolts_compression": n_bolts,
        },
        intermediates=intermediates,
        design_factors={"phi_n": phi_n},
        units_trace={"vu": vu.unit, "capacity": capacity.unit},
    )


def run_bolt_bearing_tearout_end_plate(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vu = _require(case, "loads.required_connection_shear", rule_binding)
    end_plate_fu = _require(case, "materials.end_plate_fu", rule_binding)
    lc = _require(case, "geometry.clear_distance_end_plate", rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)

    n_bolts = _compression_bolt_count(case)
    capacity, intermediates = compute_bolt_bearing_tearout_capacity(
        material_fu=end_plate_fu,
        clear_distance=lc,
        plate_thickness=tp,
        bolt_diameter=db,
        n_bolts_compression=n_bolts,
        phi_n=phi_n,
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=vu,
        capacity=capacity,
        equation="Vu <= phi_n * sum[min(1.2*lc*t*Fu, 2.4*db*t*Fu)] (Eq. 6.7-12, end plate)",
        inputs={
            "vu": vu.model_dump(),
            "end_plate_fu": end_plate_fu.model_dump(),
            "lc_end_plate": lc.model_dump(),
            "end_plate_thickness": tp.model_dump(),
            "bolt_diameter": db.model_dump(),
            "n_bolts_compression": n_bolts,
        },
        intermediates=intermediates,
        design_factors={"phi_n": phi_n},
        units_trace={"vu": vu.unit, "capacity": capacity.unit},
    )


def run_bolt_bearing_tearout_column_flange(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vu = _require(case, "loads.required_connection_shear", rule_binding)
    column_fu = _require(case, "materials.column_fu", rule_binding)
    lc = _require(case, "geometry.clear_distance_column_flange", rule_binding)
    column_profile = _column_profile(case)
    tcf = column_profile["tf"]
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)

    n_bolts = _compression_bolt_count(case)
    capacity, intermediates = compute_bolt_bearing_tearout_capacity(
        material_fu=column_fu,
        clear_distance=lc,
        plate_thickness=tcf,
        bolt_diameter=db,
        n_bolts_compression=n_bolts,
        phi_n=phi_n,
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=vu,
        capacity=capacity,
        equation="Vu <= phi_n * sum[min(1.2*lc*t*Fu, 2.4*db*t*Fu)] (Eq. 6.7-12, column flange)",
        inputs={
            "vu": vu.model_dump(),
            "column_shape": case.sections.column_shape,
            "column_fu": column_fu.model_dump(),
            "lc_column_flange": lc.model_dump(),
            "column_flange_thickness_from_sections": tcf.model_dump(),
            "bolt_diameter": db.model_dump(),
            "n_bolts_compression": n_bolts,
        },
        intermediates=intermediates,
        design_factors={"phi_n": phi_n},
        units_trace={"vu": vu.unit, "capacity": capacity.unit},
    )


def run_stiffener_minimum_length(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    hst = _require(case, "geometry.stiffener_height", rule_binding)
    lst = _require(case, "geometry.stiffener_length", rule_binding)

    required_lst = compute_minimum_stiffener_length(hst, case.units_system)
    demand = required_lst
    capacity = lst
    dcr = demand.value / capacity.value
    status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL

    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        status=status,
        calculation_memory=CalculationMemory(
            inputs={"stiffener_height": hst.model_dump(), "stiffener_length": lst.model_dump()},
            intermediates={},
            design_factors={},
            equation="Lst >= hst / tan(30 deg) (Eq. 6.6-1)",
            units_trace={"hst": hst.unit, "lst": lst.unit},
            final_capacity=capacity,
        ),
        notes=None,
    )


def run_stiffener_thickness(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    tbw = _beam_profile(case)["tw"]
    beam_fy = _require(case, "materials.beam_fy", rule_binding)
    stiffener_fy = _require(case, "materials.stiffener_fy", rule_binding)
    ts = _require(case, "geometry.stiffener_thickness", rule_binding)

    required_ts = compute_required_stiffener_thickness(
        beam_web_thickness=tbw,
        beam_fy=beam_fy,
        stiffener_fy=stiffener_fy,
        unit_system=case.units_system,
    )
    demand = required_ts
    capacity = ts
    dcr = demand.value / capacity.value
    status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL

    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        status=status,
        calculation_memory=CalculationMemory(
            inputs={
                "beam_shape": case.sections.beam_shape,
                "beam_web_thickness": tbw.model_dump(),
                "beam_fy": beam_fy.model_dump(),
                "stiffener_fy": stiffener_fy.model_dump(),
                "stiffener_thickness": ts.model_dump(),
            },
            intermediates={},
            design_factors={},
            equation="ts >= (Fyb/Fys) * tbw (Eq. 6.7-9)",
            units_trace={"tbw": tbw.unit, "ts": ts.unit},
            final_capacity=capacity,
        ),
        notes=None,
    )


def run_stiffener_local_buckling(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    hst = _require(case, "geometry.stiffener_height", rule_binding)
    ts = _require(case, "geometry.stiffener_thickness", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    stiffener_fy = _require(case, "materials.stiffener_fy", rule_binding)

    ratio = hst.value / ts.value
    limit = compute_stiffener_slenderness_ratio_limit(
        elastic_modulus=elastic_modulus,
        stiffener_fy=stiffener_fy,
        unit_system=case.units_system,
    )
    demand = Quantity(value=ratio, unit="ratio")
    capacity = Quantity(value=limit, unit="ratio")
    dcr = demand.value / capacity.value
    status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL

    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        status=status,
        calculation_memory=CalculationMemory(
            inputs={
                "stiffener_height": hst.model_dump(),
                "stiffener_thickness": ts.model_dump(),
                "elastic_modulus": elastic_modulus.model_dump(),
                "stiffener_fy": stiffener_fy.model_dump(),
            },
            intermediates={"hst_over_ts": ratio, "limit": limit},
            design_factors={},
            equation="hst/ts <= 0.56 * sqrt(E/Fys) (Eq. 6.7-10)",
            units_trace={"hst": hst.unit, "ts": ts.unit, "ratio": "ratio"},
            final_capacity=capacity,
        ),
        notes=None,
    )


def run_step14_beam_shear_strength(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vu = _require(case, "loads.required_beam_shear", rule_binding)
    beam_shear_capacity = _require_procedure(case, "beam_available_shear_strength", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=vu,
        capacity=beam_shear_capacity,
        equation="Vu <= phi*Vn (AISC Specification per Section 6.7.1 Step 14)",
        inputs={"required_beam_shear": vu.model_dump(), "beam_available_shear_strength": beam_shear_capacity.model_dump()},
        intermediates={},
        design_factors={},
        units_trace={"vu": vu.unit, "capacity": beam_shear_capacity.unit},
    )


def run_step15_connection_shear_requirement(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    required_beam_shear = _require(case, "loads.required_beam_shear", rule_binding)
    required_connection_shear = _require(case, "loads.required_connection_shear", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=required_beam_shear,
        capacity=required_connection_shear,
        equation="Vu(connection) = Vu(beam) (Section 6.7.1 Step 15)",
        inputs={
            "required_beam_shear": required_beam_shear.model_dump(),
            "required_connection_shear": required_connection_shear.model_dump(),
        },
        intermediates={},
        design_factors={},
        units_trace={"vu_beam": required_beam_shear.unit, "vu_connection": required_connection_shear.unit},
    )


def run_step18_weld_design(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    ffu, ffu_intermediate = compute_beam_flange_force_from_mf(
        mf=mf,
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    flange_weld_capacity = _require_procedure(case, "flange_weld_available_strength", rule_binding)
    web_weld_capacity = _require_procedure(case, "web_weld_available_strength", rule_binding)
    required_web_weld = _require(case, "loads.required_web_weld_force", rule_binding)

    flange_dcr = ffu.value / flange_weld_capacity.value
    web_dcr = required_web_weld.value / web_weld_capacity.value
    demand = Quantity(value=max(flange_dcr, web_dcr), unit="ratio")
    capacity = Quantity(value=1.0, unit="ratio")
    status = CheckStatus.PASS if demand.value <= 1.0 else CheckStatus.FAIL
    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=demand.value,
        status=status,
        calculation_memory=CalculationMemory(
            inputs={
                "mf": mf.model_dump(),
                "required_web_weld_force": required_web_weld.model_dump(),
                "flange_weld_available_strength": flange_weld_capacity.model_dump(),
                "web_weld_available_strength": web_weld_capacity.model_dump(),
            },
            intermediates={
                **ffu_intermediate,
                "ffu": ffu.value,
                "flange_weld_dcr": flange_dcr,
                "web_weld_dcr": web_dcr,
            },
            design_factors={},
            equation="Section 6.7.1 Step 18 + Section 6.6.6 weld design checks",
            units_trace={"dcr": "ratio"},
            final_capacity=capacity,
        ),
        notes=None,
    )


def run_column_step1_flange_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    beam_depth = _beam_profile(case)["d"]
    column_profile = _column_profile(case)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    yc = _column_yc_parameter(case, rule_binding)
    phi_d = _require(case, "design_factors.phi_d", rule_binding)
    tcf_req = compute_column_flange_required_thickness(
        mf=mf,
        beam_depth=beam_depth,
        column_fy=column_fy,
        yc=yc,
        phi_d=phi_d,
        unit_system=case.units_system,
    )
    tcf = column_profile["tf"]
    return _build_result(
        rule_binding=rule_binding,
        demand=tcf_req,
        capacity=tcf,
        equation="tcf >= 1.11 Mf / (phi_d * d * Fyc * Yc) (Eq. 6.7-13)",
        inputs={
            "mf": mf.model_dump(),
            "beam_depth": beam_depth.model_dump(),
            "column_shape": case.sections.column_shape,
            "column_fy": column_fy.model_dump(),
            "yc": yc.model_dump(),
        },
        intermediates={},
        design_factors={"phi_d": phi_d},
        units_trace={"tcf_req": tcf_req.unit, "tcf": tcf.unit},
    )


def run_column_step2_stiffener_force(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    column_profile = _column_profile(case)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    yc = _column_yc_parameter(case, rule_binding)
    phi_d = _require(case, "design_factors.phi_d", rule_binding)
    d_rn, intermediates = compute_column_flange_design_force_from_yield_line(
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        column_fy=column_fy,
        yc=yc,
        column_flange_thickness=column_profile["tf"],
        phi_d=phi_d,
        unit_system=case.units_system,
    )
    ffu, _ = compute_beam_flange_force_from_mf(
        mf=_require(case, "loads.probable_moment_column_face", rule_binding),
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=ffu,
        capacity=d_rn,
        equation="Equivalent column flange design force from Eq. 6.7-14 and Eq. 6.7-15",
        inputs={"column_shape": case.sections.column_shape, "column_fy": column_fy.model_dump(), "yc": yc.model_dump()},
        intermediates=intermediates,
        design_factors={"phi_d": phi_d},
        units_trace={"ffu": ffu.unit, "d_rn": d_rn.unit},
    )


def run_column_step3_web_local_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    column_profile = _column_profile(case)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    kc = _profile_kdes(column_profile, role="column", rule_binding=rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    w = _require(case, "geometry.weld_leg_size_w", rule_binding)
    phi_d = _require(case, "design_factors.phi_d", rule_binding)
    column_top_distance = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)

    ct = 0.5 if column_top_distance.value < column_profile["d"].value else 1.0
    lb = Quantity(value=beam_profile["tf"].value + 2.0 * w.value + 2.0 * tp.value, unit=beam_profile["tf"].unit)
    capacity, intermediates = compute_column_web_local_yielding_strength(
        ct=ct,
        kc=kc,
        lb=lb,
        column_fy=column_fy,
        column_web_thickness=column_profile["tw"],
        phi_d=phi_d,
        unit_system=case.units_system,
    )
    ffu, _ = compute_beam_flange_force_from_mf(
        mf=_require(case, "loads.probable_moment_column_face", rule_binding),
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=ffu,
        capacity=capacity,
        equation="Ffu <= phi_d * Rn, Rn=(6Ct*kc+lb)Fyc*tcw (Eq. 6.7-16 and Eq. 6.7-17)",
        inputs={
            "column_shape": case.sections.column_shape,
            "kc_from_sections_kdes": kc.model_dump(),
            "lb": lb.model_dump(),
            "column_fy": column_fy.model_dump(),
        },
        intermediates=intermediates,
        design_factors={"phi_d": phi_d},
        units_trace={"ffu": ffu.unit, "capacity": capacity.unit},
    )


def run_column_step4_web_local_crippling(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    column_profile = _column_profile(case)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    w = _require(case, "geometry.weld_leg_size_w", rule_binding)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    distance_to_end = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)
    lb = Quantity(value=beam_profile["tf"].value + 2.0 * w.value + 2.0 * tp.value, unit=beam_profile["tf"].unit)
    capacity, intermediates = compute_column_web_local_crippling_strength(
        lb=lb,
        column_depth=column_profile["d"],
        column_web_thickness=column_profile["tw"],
        column_flange_thickness=column_profile["tf"],
        elastic_modulus=elastic_modulus,
        column_fy=column_fy,
        distance_to_column_end=distance_to_end,
        unit_system=case.units_system,
    )
    ffu, _ = compute_beam_flange_force_from_mf(
        mf=_require(case, "loads.probable_moment_column_face", rule_binding),
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=ffu,
        capacity=capacity,
        equation="Ffu <= phi*Rn (Eq. 6.7-18 to Eq. 6.7-21)",
        inputs={"lb": lb.model_dump(), "distance_to_column_end": distance_to_end.model_dump()},
        intermediates=intermediates,
        design_factors={},
        units_trace={"ffu": ffu.unit, "capacity": capacity.unit},
    )


def run_column_step5_continuity_plate_strength(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    mf = _require(case, "loads.probable_moment_column_face", rule_binding)
    ffu, _ = compute_beam_flange_force_from_mf(
        mf=mf,
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )

    # Recompute design strengths from Steps 2 to 4.
    d_rn = run_column_step2_stiffener_force(case, rule_binding).capacity
    r3 = run_column_step3_web_local_yielding(case, rule_binding).capacity
    r4 = run_column_step4_web_local_crippling(case, rule_binding).capacity
    min_strength = min(d_rn.value, r3.value, r4.value)
    required_fsu = Quantity(value=max(ffu.value - min_strength, 0.0), unit=ffu.unit)
    continuity_capacity = _require_procedure(case, "continuity_plate_available_strength", rule_binding)

    return _build_result(
        rule_binding=rule_binding,
        demand=required_fsu,
        capacity=continuity_capacity,
        equation="Fsu = Ffu - min(Rn) (Eq. 6.7-22)",
        inputs={"ffu": ffu.model_dump(), "continuity_plate_available_strength": continuity_capacity.model_dump()},
        intermediates={"min_design_strength": min_strength},
        design_factors={},
        units_trace={"fsu_required": required_fsu.unit, "capacity": continuity_capacity.unit},
    )


def run_column_step6_panel_zone(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    demand = _require(case, "loads.panel_zone_demand", rule_binding)
    capacity = _require_procedure(case, "panel_zone_capacity", rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation="Panel zone check per Section 2.7 / AISC Seismic Provisions",
        inputs={"panel_zone_demand": demand.model_dump(), "panel_zone_capacity": capacity.model_dump()},
        intermediates={},
        design_factors={},
        units_trace={"demand": demand.unit, "capacity": capacity.unit},
    )


def run_column_step7_column_beam_moment_ratio(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    ratio = _require_procedure(case, "column_beam_moment_ratio", rule_binding)
    ratio_min = _require(case, "design_factors.column_beam_moment_ratio_minimum", rule_binding)
    demand = Quantity(value=ratio_min, unit="ratio")
    capacity = Quantity(value=ratio, unit="ratio")
    dcr = demand.value / capacity.value
    status = CheckStatus.PASS if dcr <= 1.0 else CheckStatus.FAIL
    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=demand,
        capacity=capacity,
        dcr=dcr,
        status=status,
        calculation_memory=CalculationMemory(
            inputs={"column_beam_moment_ratio": ratio, "required_minimum_ratio": ratio_min},
            intermediates={},
            design_factors={},
            equation="Column-beam moment ratio per Section 2.8 / AISC Seismic Provisions",
            units_trace={"ratio": "ratio"},
            final_capacity=capacity,
        ),
        notes=None,
    )
