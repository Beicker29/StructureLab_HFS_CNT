from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, Callable

from steel_connections.codes.aisc358.chapter_06 import (
    compute_minimum_bolt_spacing,
    compute_minimum_edge_distance_standard_hole,
    compute_column_flange_design_force_from_yield_line,
    compute_column_flange_required_thickness,
    compute_column_flange_yield_line_parameter,
    compute_column_web_local_crippling_strength,
    compute_column_web_local_buckling_strength,
    compute_column_web_local_yielding_strength,
    compute_column_beam_clearance_distance,
    compute_column_beam_clearance_threshold,
    compute_column_panel_zone_shear_strength_j10_6,
    compute_beam_flange_force_from_mf,
    compute_end_plate_yield_line_parameter,
    compute_mf,
    compute_bolt_bearing_tearout_capacity,
    compute_required_bolt_diameter,
    compute_detail_stiffener_length_from_height,
    compute_minimum_column_end_distance_to_beam_flange,
    compute_required_end_plate_thickness,
    compute_bolt_shear_rupture_capacity,
    compute_end_plate_shear_rupture_capacity,
    compute_end_plate_shear_yielding_capacity,
    compute_end_plate_hole_tearout_capacity,
    compute_end_plate_hole_bearing_capacity,
    compute_end_plate_height_from_geometry,
    compute_end_plate_yield_line_h_terms,
    compute_flange_slenderness_limit,
    compute_flange_slenderness_ratio,
    compute_minimum_stiffener_length,
    compute_minimum_stiffener_bolt_gage,
    compute_stiffener_height_from_end_plate_geometry,
    compute_sh,
    compute_vh,
    compute_required_stiffener_thickness,
    compute_stiffener_slenderness_ratio,
    compute_stiffener_slenderness_ratio_limit,
    compute_web_slenderness_limit,
    compute_web_slenderness_ratio,
)
from steel_connections.codes.engineering.common import (
    compute_dcr_ratio,
    compute_bolt_shear_rupture_capacity_per_bolt,
    compute_bolt_tension_rupture_capacity_per_bolt,
    compute_standard_hole_diameter_j33,
    compute_maximum_bolt_spacing_j36,
    compute_max_spacing_and_edge_distance_limits_j36,
    compute_limites_precalificacion_conexion_tipo_ep,
)
from steel_connections.codes.engineering.flexure import compute_yield_line_flexural_strength
from steel_connections.codes.engineering.customized import (
    compute_bseep_step6_1_bolt_tension_demand,
    compute_moment_prequalified_step6_1_bolt_tension_demand,
    compute_moment_prequalified_step6_2_bolt_shear_demand,
)
from steel_connections.codes.engineering.geometry import compute_protected_zone_length as compute_protected_zone_length_eq
from steel_connections.codes.engineering.shear import compute_beam_web_shear_yielding_strength
from steel_connections.codes.engineering.weld import (
    WeldFillet,
    compute_end_loaded_fillet_weld_effective_length_j2d,
    compute_fillet_weld_check_with_kds,
    compute_fillet_weld_maximum_size_j2b,
    compute_fillet_weld_minimum_length_strength_j2c,
    compute_fillet_weld_minimum_size_table_j24,
    compute_plate_shear_demand_from_yielding,
    compute_plate_tension_demand_from_yielding,
    compute_total_weld_4_thickness,
)
from steel_connections.data.materials_repository import get_plate_steel_properties
from steel_connections.data.sections_repository import get_beam_profile_properties, get_column_profile_properties
from steel_connections.models.errors import missing_required_input_error
from steel_connections.models.input import AISC358MomentCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import Quantity, UnitSystem, to_design_force_unit


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
    dcr_result = compute_dcr_ratio(demand=demand, capacity=capacity)
    dcr = dcr_result["dcr"]
    status = CheckStatus.PASS if dcr_result["passes"] else CheckStatus.FAIL
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


def _beam_shape_by_side(case: AISC358MomentCase, side: str) -> str:
    if side == "der":
        return case.sections.beam_shape_der or case.sections.beam_shape
    if side == "izq":
        return case.sections.beam_shape_izq or case.sections.beam_shape_der or case.sections.beam_shape
    raise ValueError("Invalid side. Expected 'der' or 'izq'.")


def _beam_profile_by_side(case: AISC358MomentCase, side: str) -> dict[str, Quantity]:
    return get_beam_profile_properties(
        beam_shape=_beam_shape_by_side(case, side),
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


def _convert_length_quantity(q: Quantity, target_unit: str) -> Quantity | None:
    if q.unit == target_unit:
        return q
    if q.unit == "mm" and target_unit == "in":
        return Quantity(value=q.value / 25.4, unit="in")
    if q.unit == "in" and target_unit == "mm":
        return Quantity(value=q.value * 25.4, unit="mm")
    return None


def _compute_encr_w8_from_aisc_16_figure_10_3(
    *,
    kdet_col: Quantity,
    tf_col: Quantity,
) -> tuple[Quantity | None, str]:
    kdet_mm = _convert_length_quantity(kdet_col, "mm")
    tf_mm = _convert_length_quantity(tf_col, "mm")
    if kdet_mm is None or tf_mm is None:
        return None, "unidades_no_convertibles_a_mm"
    delta_mm = kdet_mm.value - tf_mm.value
    tol = 1e-9
    encr_mm_value: float | None = None
    matched_range = ""
    if delta_mm <= 7.9 + tol:
        encr_mm_value = 3.2
        matched_range = "<= 7.9 mm"
    elif 9.5 - tol <= delta_mm <= 12.7 + tol:
        encr_mm_value = 4.8
        matched_range = "9.5 - 12.7 mm"
    elif 14.3 - tol <= delta_mm <= 20.6 + tol:
        encr_mm_value = 6.4
        matched_range = "14.3 - 20.6 mm"
    elif 22.2 - tol <= delta_mm <= 31.8 + tol:
        encr_mm_value = 7.9
        matched_range = "22.2 - 31.8 mm"
    elif 33.3 - tol <= delta_mm <= 34.9 + tol:
        encr_mm_value = 9.5
        matched_range = "33.3 - 34.9 mm"
    if encr_mm_value is None:
        return None, f"fuera_de_tabla (kdet_col-tf_col={delta_mm:.3f} mm)"
    encr_mm = Quantity(value=encr_mm_value, unit="mm")
    encr_target = _convert_length_quantity(encr_mm, kdet_col.unit)
    if encr_target is None:
        return None, "no_se_pudo_convertir_encr_a_unidad_objetivo"
    return encr_target, f"AISC 16th Fig 10-3, rango {matched_range}"


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


def _get_procedure_optional(case: AISC358MomentCase, field_name: str) -> Any | None:
    if case.procedure is None:
        return None
    return getattr(case.procedure, field_name, None)


def _column_yc_parameter_details(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, Any]]:
    column_profile = _column_profile(case)
    beam_profile = _beam_profile(case)
    h = _compute_end_plate_h_distances(case, rule_binding)
    g = _require(case, "geometry.bolt_gage", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pfi = _require(case, "geometry.pfi", rule_binding)
    pb = _optional_pb_for_connection(case, rule_binding)
    continuity_enabled = bool(case.geometry.continuity_plate_enabled)

    continuity_plate_thickness = _require(case, "geometry.continuity_plate_thickness", rule_binding)
    c = Quantity(value=pfo.value + pfi.value + beam_profile["tf"].value, unit=pfo.unit)
    pso = Quantity(
        value=pfo.value + 0.5 * beam_profile["tf"].value - 0.5 * continuity_plate_thickness.value,
        unit=pfo.unit,
    )
    psi = Quantity(
        value=pfi.value + 0.5 * beam_profile["tf"].value - 0.5 * continuity_plate_thickness.value,
        unit=pfi.unit,
    )
    y_parameter, metadata = compute_column_flange_yield_line_parameter(
        connection_type=case.connection_type,
        is_stiffened=continuity_enabled,
        bcf=column_profile["bf"],
        g=g,
        h1=h["h1"],
        h2=h["h2"],
        h3=h.get("h3"),
        h4=h.get("h4"),
        c=c,
        pso=pso,
        psi=psi,
        pb=pb,
        unit_system=case.units_system,
    )
    return y_parameter, {
        **metadata,
        "continuity_plate_enabled": continuity_enabled,
        "c": c.model_dump(),
        "pso": pso.model_dump(),
        "psi_computed": psi.model_dump(),
        "continuity_plate_thickness": continuity_plate_thickness.model_dump(),
        "h1": h["h1"].model_dump(),
        "h2": h["h2"].model_dump(),
        "h3": h.get("h3").model_dump() if h.get("h3") is not None else None,
        "h4": h.get("h4").model_dump() if h.get("h4") is not None else None,
        "bcf": column_profile["bf"].model_dump(),
        "g": g.model_dump(),
    }


def _column_yc_parameter(case: AISC358MomentCase, rule_binding: object) -> Quantity:
    yc, _ = _column_yc_parameter_details(case, rule_binding)
    return yc


def _compute_mpr(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, float]]:
    mpr_data = _compute_mpr_by_side(case, rule_binding)
    governing_side = mpr_data["governing_side"]
    governing_mpr: Quantity = mpr_data["sides"][governing_side]["mpr"]
    return governing_mpr, {"cpr": mpr_data["sides"][governing_side]["cpr"], "ry": mpr_data["ry"]}


def _compute_mpr_by_side(case: AISC358MomentCase, rule_binding: object) -> dict[str, Any]:
    fy = _require(case, "materials.beam_fy", rule_binding)
    ry = _require(case, "design_factors.ry", rule_binding)
    ductility_default = _require(case, "design_factors.member_ductility_demand_column", rule_binding)
    side_data: dict[str, Any] = {}
    for side in _active_beam_sides(case):
        side_profile = _beam_profile_by_side(case, side)
        ze_side = side_profile["zx"]
        side_ductility = ductility_default
        cpr_side = 1.0 if str(side_ductility).strip().lower() == "low" else 1.15
        mpr_base = cpr_side * ry * fy.value * ze_side.value
        mpr_side = (
            Quantity(value=mpr_base, unit="kip-in")
            if case.units_system == UnitSystem.US
            else Quantity(value=mpr_base / 1000.0, unit="kN-mm")
        )
        side_data[side] = {
            "mpr": mpr_side,
            "ze": ze_side,
            "cpr": cpr_side,
            "member_ductility_demand_beam": side_ductility,
        }
    mpr_values = {side: data["mpr"] for side, data in side_data.items()}
    governing_side, governing_mpr = _select_max_quantity_by_side(mpr_values)
    return {"fy": fy, "ry": ry, "sides": side_data, "governing_side": governing_side, "governing_mpr": governing_mpr}


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


def _profile_ag(profile: dict[str, Quantity], *, role: str, rule_binding: object) -> Quantity:
    ag = profile.get("ag")
    if ag is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[f"sections.{role}_shape"],
            message=(
                f"Catalog property 'A' (gross area) for sections.{role}_shape is required "
                "to compute compactness coefficient Ca = Pu/(Ry*Ag*Fy)."
            ),
        )
    return ag


def _derive_stiffener_height_from_de_pfo(
    *,
    de: Quantity,
    pfo: Quantity,
    pb: Quantity | None = None,
) -> Quantity:
    unit_system = UnitSystem.US if pfo.unit == "in" else UnitSystem.SI
    return compute_stiffener_height_from_end_plate_geometry(
        pfo=pfo,
        de=de,
        pb=pb,
        unit_system=unit_system,
    )


def _derive_end_plate_height(
    *,
    beam_depth: Quantity,
    de: Quantity,
    pfo: Quantity,
    pb: Quantity | None = None,
) -> Quantity:
    unit_system = UnitSystem.US if beam_depth.unit == "in" else UnitSystem.SI
    return compute_end_plate_height_from_geometry(
        beam_depth=beam_depth,
        pfo=pfo,
        de=de,
        pb=pb,
        unit_system=unit_system,
    )


def _derive_stiffener_length_from_hst(*, stiffener_height: Quantity, unit_system: UnitSystem) -> Quantity:
    return compute_detail_stiffener_length_from_height(stiffener_height, unit_system)


def _compute_protected_zone_length(
    *,
    lst: Quantity | None,
    d: Quantity,
    bf: Quantity,
) -> dict[str, Quantity | str]:
    unit_system = UnitSystem.US if d.unit == "in" else UnitSystem.SI
    return compute_protected_zone_length_eq(lst=lst, d=d, bf=bf, unit_system=unit_system)  # type: ignore[return-value]


def _stiffener_clip_distance(unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.SI:
        return Quantity(value=25.0, unit="mm")
    return Quantity(value=25.0 / 25.4, unit="in")


def _active_beam_sides(case: AISC358MomentCase) -> tuple[str, ...]:
    beam_connection_sides = case.design_factors.beam_connection_sides
    if beam_connection_sides == "both_sides":
        return ("der", "izq")
    if beam_connection_sides == "right_only":
        return ("der",)
    if beam_connection_sides == "left_only":
        return ("izq",)
    raise ValueError(
        "Required input 'design_factors.beam_connection_sides' is missing or invalid. "
        "No default value is allowed under zero-guess policy."
    )


def _replace_side_tokens(value: Any, *, to_side: str) -> Any:
    if isinstance(value, dict):
        return {_replace_side_tokens(key, to_side=to_side): _replace_side_tokens(item, to_side=to_side) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_side_tokens(item, to_side=to_side) for item in value]
    if isinstance(value, str):
        text = value

        def _swap_pair(raw: str, left: str, right: str, token: str) -> str:
            return raw.replace(left, token).replace(right, left).replace(token, right)

        # Use bidirectional swap to avoid key collisions when payloads contain both sides.
        text = _swap_pair(text, "vgizq", "vgder", "__TMP_VG_SIDE__")
        text = _swap_pair(text, "_izq", "_der", "__TMP_SUFFIX_SIDE__")
        text = _swap_pair(text, " izquierda", " derecha", "__TMP_ADJ_SIDE__")
        return text
    return value


def _adapt_case_for_side_as_left(case: AISC358MomentCase, *, side: str) -> AISC358MomentCase:
    if side not in {"izq", "der"}:
        raise ValueError("side must be 'izq' or 'der'.")
    adapted = deepcopy(case)
    # Force side availability for legacy left-side evaluators.
    adapted.design_factors.beam_connection_sides = "both_sides"

    primary_tag = "vgizq" if side == "izq" else "vgder"
    secondary_tag = "vgder" if primary_tag == "vgizq" else "vgizq"

    def _geometry_side_value(field_root: str, tag: str) -> Any:
        return getattr(case.geometry, f"{field_root}_{tag}", None)

    def _geometry_primary_or_common(field_root: str) -> Any:
        return _geometry_side_value(field_root, primary_tag) or getattr(case.geometry, field_root, None)

    def _geometry_secondary(field_root: str) -> Any:
        return _geometry_side_value(field_root, secondary_tag)

    # Map selected side to legacy "left-facing" fields.
    primary_shape = case.sections.beam_shape_izq if primary_tag == "vgizq" else case.sections.beam_shape_der
    secondary_shape = case.sections.beam_shape_der if primary_tag == "vgizq" else case.sections.beam_shape_izq
    adapted.sections.beam_shape_izq = primary_shape or case.sections.beam_shape
    adapted.sections.beam_shape_der = secondary_shape or case.sections.beam_shape_der or case.sections.beam_shape_izq
    adapted.sections.beam_shape = adapted.sections.beam_shape_izq or adapted.sections.beam_shape_der or case.sections.beam_shape

    primary_clear_span = (
        case.geometry.beam_clear_span_length_izq
        if primary_tag == "vgizq"
        else case.geometry.beam_clear_span_length_der
    ) or case.geometry.beam_clear_span_length
    secondary_clear_span = (
        case.geometry.beam_clear_span_length_der
        if primary_tag == "vgizq"
        else case.geometry.beam_clear_span_length_izq
    )
    primary_shear_free = (
        case.geometry.beam_shear_connector_free_length_from_column_face_izq
        if primary_tag == "vgizq"
        else case.geometry.beam_shear_connector_free_length_from_column_face_der
    ) or case.geometry.beam_shear_connector_free_length_from_column_face
    secondary_shear_free = (
        case.geometry.beam_shear_connector_free_length_from_column_face_der
        if primary_tag == "vgizq"
        else case.geometry.beam_shear_connector_free_length_from_column_face_izq
    )
    adapted.geometry.beam_clear_span_length_izq = primary_clear_span
    adapted.geometry.beam_shear_connector_free_length_from_column_face_izq = primary_shear_free
    adapted.geometry.beam_clear_span_length_der = secondary_clear_span or case.geometry.beam_clear_span_length_der
    adapted.geometry.beam_shear_connector_free_length_from_column_face_der = (
        secondary_shear_free or case.geometry.beam_shear_connector_free_length_from_column_face_der
    )

    primary_vgravity = case.loads.beam_left_vgravity if primary_tag == "vgizq" else case.loads.beam_right_vgravity
    if primary_vgravity is None and primary_tag == "vgder":
        primary_vgravity = case.loads.beam_gravity_shear_between_hinges_der
    if primary_vgravity is None and primary_tag == "vgizq":
        primary_vgravity = case.loads.beam_gravity_shear_between_hinges_izq
    secondary_vgravity = case.loads.beam_right_vgravity if primary_tag == "vgizq" else case.loads.beam_left_vgravity

    primary_pu = case.loads.pu_viga_left if primary_tag == "vgizq" else case.loads.pu_viga_right
    secondary_pu = case.loads.pu_viga_right if primary_tag == "vgizq" else case.loads.pu_viga_left
    primary_vh_max = case.loads.shear_plastic_hinge_izqmax if primary_tag == "vgizq" else case.loads.shear_plastic_hinge_dermax
    primary_vh_min = case.loads.shear_plastic_hinge_izqmin if primary_tag == "vgizq" else case.loads.shear_plastic_hinge_dermin
    secondary_vh_max = case.loads.shear_plastic_hinge_dermax if primary_tag == "vgizq" else case.loads.shear_plastic_hinge_izqmax
    secondary_vh_min = case.loads.shear_plastic_hinge_dermin if primary_tag == "vgizq" else case.loads.shear_plastic_hinge_izqmin
    primary_mu3 = case.loads.Mu3_vgizq if primary_tag == "vgizq" else case.loads.Mu3_vgder
    secondary_mu3 = case.loads.Mu3_vgder if primary_tag == "vgizq" else case.loads.Mu3_vgizq

    adapted.loads.beam_left_vgravity = primary_vgravity
    adapted.loads.beam_right_vgravity = secondary_vgravity or case.loads.beam_right_vgravity
    adapted.loads.pu_viga_left = primary_pu or case.loads.pu_viga
    adapted.loads.pu_viga_right = secondary_pu or case.loads.pu_viga_right
    adapted.loads.shear_plastic_hinge_izqmax = primary_vh_max or case.loads.shear_plastic_hinge
    adapted.loads.shear_plastic_hinge_izqmin = primary_vh_min
    adapted.loads.shear_plastic_hinge_dermax = secondary_vh_max or case.loads.shear_plastic_hinge_dermax
    adapted.loads.shear_plastic_hinge_dermin = secondary_vh_min or case.loads.shear_plastic_hinge_dermin
    adapted.loads.Mu3_vgizq = primary_mu3 or case.loads.Mu3_vgizq
    adapted.loads.Mu3_vgder = secondary_mu3 or case.loads.Mu3_vgder

    # Legacy/common geometry fields resolved from the selected side.
    adapted.geometry.end_plate_width = _geometry_primary_or_common("end_plate_width")
    adapted.geometry.end_plate_thickness = _geometry_primary_or_common("end_plate_thickness")
    adapted.geometry.de = _geometry_primary_or_common("de")
    adapted.geometry.pb = _geometry_primary_or_common("pb")
    adapted.geometry.pfo = _geometry_primary_or_common("pfo")
    adapted.geometry.pfi = _geometry_primary_or_common("pfi")
    adapted.geometry.bolt_gage = _geometry_primary_or_common("bolt_gage")
    adapted.geometry.bolt_diameter = _geometry_primary_or_common("bolt_diameter")
    adapted.geometry.bolt_tightening_type = _geometry_primary_or_common("bolt_tightening_type")
    adapted.geometry.clear_distance_end_plate = _geometry_primary_or_common("clear_distance_end_plate")
    adapted.geometry.clear_distance_column_flange = _geometry_primary_or_common("clear_distance_column_flange")
    adapted.geometry.stiffener_thickness = _geometry_primary_or_common("stiffener_thickness")
    adapted.geometry.end_plate_beam_web_weld_type = _geometry_primary_or_common("end_plate_beam_web_weld_type")
    adapted.geometry.end_plate_beam_web_weld_thickness_twe = _geometry_primary_or_common(
        "end_plate_beam_web_weld_thickness_twe"
    )
    adapted.geometry.end_plate_beam_web_weld_lines_nl = _geometry_primary_or_common("end_plate_beam_web_weld_lines_nl")
    adapted.geometry.end_plate_stiffener_weld_type = _geometry_primary_or_common("end_plate_stiffener_weld_type")
    adapted.geometry.L_gap_w1 = _geometry_primary_or_common("L_gap_w1")
    adapted.geometry.end_plate_stiffener_weld_size_wst = _geometry_primary_or_common("end_plate_stiffener_weld_size_wst")
    adapted.geometry.end_plate_stiffener_weld_lines_nl = _geometry_primary_or_common("end_plate_stiffener_weld_lines_nl")
    adapted.geometry.beam_stiffener_weld_type = _geometry_primary_or_common("beam_stiffener_weld_type")
    adapted.geometry.L_gap_w2 = _geometry_primary_or_common("L_gap_w2")
    adapted.geometry.beam_stiffener_weld_size_wst2 = _geometry_primary_or_common("beam_stiffener_weld_size_wst2")
    adapted.geometry.beam_stiffener_weld_lines_nl_w2 = _geometry_primary_or_common("beam_stiffener_weld_lines_nl_w2")

    # Keep both side-specific fields populated coherently in adapted context.
    for root in (
        "end_plate_width",
        "end_plate_thickness",
        "de",
        "pb",
        "pfo",
        "pfi",
        "bolt_gage",
        "bolt_diameter",
        "bolt_tightening_type",
        "clear_distance_end_plate",
        "clear_distance_column_flange",
        "stiffener_thickness",
        "end_plate_beam_web_weld_type",
        "end_plate_beam_web_weld_thickness_twe",
        "end_plate_beam_web_weld_lines_nl",
        "end_plate_stiffener_weld_type",
        "L_gap_w1",
        "end_plate_stiffener_weld_size_wst",
        "end_plate_stiffener_weld_lines_nl",
        "beam_stiffener_weld_type",
        "L_gap_w2",
        "beam_stiffener_weld_size_wst2",
        "beam_stiffener_weld_lines_nl_w2",
    ):
        setattr(adapted.geometry, f"{root}_vgizq", _geometry_primary_or_common(root))
        setattr(adapted.geometry, f"{root}_vgder", _geometry_secondary(root) or getattr(case.geometry, f"{root}_vgder", None))

    for root in ("kds_w1", "kds_w2", "kds_w3", "tipo_w4", "t_w4", "nl_w4", "t_w4_1", "kds_w4"):
        primary_value = getattr(case.geometry, f"{root}_{primary_tag}", None)
        secondary_value = getattr(case.geometry, f"{root}_{secondary_tag}", None)
        setattr(adapted.geometry, f"{root}_vgizq", primary_value if primary_value is not None else getattr(case.geometry, f"{root}_vgizq", None))
        setattr(adapted.geometry, f"{root}_vgder", secondary_value if secondary_value is not None else getattr(case.geometry, f"{root}_vgder", None))

    primary_stiffener_fy = getattr(case.materials, f"stiffener_fy_{primary_tag}", None)
    secondary_stiffener_fy = getattr(case.materials, f"stiffener_fy_{secondary_tag}", None)
    adapted.materials.stiffener_fy = primary_stiffener_fy or case.materials.stiffener_fy
    adapted.materials.stiffener_fy_vgizq = primary_stiffener_fy or case.materials.stiffener_fy_vgizq
    adapted.materials.stiffener_fy_vgder = secondary_stiffener_fy or case.materials.stiffener_fy_vgder

    primary_w4_fexx = getattr(case.materials, f"weld_fexx_w4_{primary_tag}", None)
    secondary_w4_fexx = getattr(case.materials, f"weld_fexx_w4_{secondary_tag}", None)
    adapted.materials.weld_fexx_w4_vgizq = primary_w4_fexx or case.materials.weld_fexx_w4_vgizq
    adapted.materials.weld_fexx_w4_vgder = secondary_w4_fexx or case.materials.weld_fexx_w4_vgder

    # Map side-specific bolt properties into legacy/common fields used by evaluators.
    primary_bolt_fnt = getattr(case.materials, f"bolt_fnt_{primary_tag}", None)
    secondary_bolt_fnt = getattr(case.materials, f"bolt_fnt_{secondary_tag}", None)
    primary_bolt_fnv = getattr(case.materials, f"bolt_fnv_{primary_tag}", None)
    secondary_bolt_fnv = getattr(case.materials, f"bolt_fnv_{secondary_tag}", None)
    adapted.materials.bolt_fnt = primary_bolt_fnt or case.materials.bolt_fnt
    adapted.materials.bolt_fnv = primary_bolt_fnv or case.materials.bolt_fnv
    adapted.materials.bolt_fnt_vgizq = primary_bolt_fnt or case.materials.bolt_fnt_vgizq
    adapted.materials.bolt_fnt_vgder = secondary_bolt_fnt or case.materials.bolt_fnt_vgder
    adapted.materials.bolt_fnv_vgizq = primary_bolt_fnv or case.materials.bolt_fnv_vgizq
    adapted.materials.bolt_fnv_vgder = secondary_bolt_fnv or case.materials.bolt_fnv_vgder

    for root in (
        "bolt_fabrication_standard",
        "bolt_description",
        "bolt_shape",
        "bolt_thread_condition",
    ):
        primary_value = getattr(case.materials, f"{root}_{primary_tag}", None)
        secondary_value = getattr(case.materials, f"{root}_{secondary_tag}", None)
        setattr(adapted.materials, root, primary_value or getattr(case.materials, root, None))
        setattr(
            adapted.materials,
            f"{root}_vgizq",
            primary_value or getattr(case.materials, f"{root}_vgizq", None),
        )
        setattr(
            adapted.materials,
            f"{root}_vgder",
            secondary_value or getattr(case.materials, f"{root}_vgder", None),
        )

    column_ductility = case.design_factors.member_ductility_demand_column
    adapted.design_factors.member_ductility_demand_beam_vgizq = (
        column_ductility
        or case.design_factors.member_ductility_demand_beam_vgizq
        or case.design_factors.member_ductility_demand_beam
    )
    adapted.design_factors.member_ductility_demand_beam_vgder = (
        column_ductility
        or case.design_factors.member_ductility_demand_beam_vgder
        or case.design_factors.member_ductility_demand_beam
    )
    adapted.design_factors.member_ductility_demand_beam = (
        column_ductility or case.design_factors.member_ductility_demand_beam
    )

    return adapted


def _evaluate_left_style_rule_for_side(
    *,
    case: AISC358MomentCase,
    rule_binding: object,
    left_evaluator: Callable[[AISC358MomentCase, object], CheckResult],
    side: str,
) -> CheckResult:
    adapted_case = _adapt_case_for_side_as_left(case, side=side)
    result = left_evaluator(adapted_case, rule_binding)
    if side == "izq":
        return result
    payload = result.model_dump()
    payload["rule_id"] = rule_binding.rule_id
    payload["calculation_memory"]["inputs"] = _replace_side_tokens(payload["calculation_memory"]["inputs"], to_side="der")
    payload["calculation_memory"]["intermediates"] = _replace_side_tokens(
        payload["calculation_memory"]["intermediates"], to_side="der"
    )
    payload["calculation_memory"]["equation"] = _replace_side_tokens(payload["calculation_memory"]["equation"], to_side="der")
    payload["name"] = _replace_side_tokens(payload["name"], to_side="der")
    payload["clause"] = _replace_side_tokens(payload["clause"], to_side="der")
    payload["notes"] = _replace_side_tokens(payload.get("notes"), to_side="der")
    return CheckResult.model_validate(payload)


def _require_geometry_by_side(
    case: AISC358MomentCase,
    *,
    base_field: str,
    side: str,
    rule_binding: object,
) -> tuple[Quantity, str]:
    field_name = f"{base_field}_{side}"
    value = getattr(case.geometry, field_name, None)
    if value is not None:
        return value, f"geometry.{field_name}"
    if side == "der":
        legacy_value = getattr(case.geometry, base_field)
        if legacy_value is not None:
            return legacy_value, f"geometry.{base_field}"
    raise missing_required_input_error(
        rule_id=rule_binding.rule_id,
        source_document=rule_binding.source_document,
        missing_fields=[f"geometry.{field_name}"],
        message=f"Required input 'geometry.{field_name}' is missing for applicable rule.",
    )


def _require_load_by_side(
    case: AISC358MomentCase,
    *,
    base_field: str,
    side: str,
    rule_binding: object,
) -> tuple[Quantity, str]:
    if base_field == "beam_gravity_shear_between_hinges":
        side_field = "beam_right_vgravity" if side == "der" else "beam_left_vgravity"
        value = getattr(case.loads, side_field)
        if value is not None:
            return value, f"loads.{side_field}"
    field_name = f"{base_field}_{side}"
    value = getattr(case.loads, field_name)
    if value is not None:
        return value, f"loads.{field_name}"
    if side == "der":
        legacy_value = getattr(case.loads, base_field)
        if legacy_value is not None:
            return legacy_value, f"loads.{base_field}"
    raise missing_required_input_error(
        rule_id=rule_binding.rule_id,
        source_document=rule_binding.source_document,
        missing_fields=[f"loads.{field_name}"],
        message=f"Required input 'loads.{field_name}' is missing for applicable rule.",
    )


def _select_max_quantity_by_side(values: dict[str, Quantity]) -> tuple[str, Quantity]:
    units = {item.unit for item in values.values()}
    if len(units) != 1:
        raise ValueError("Incompatible units between beam sides; right/left values must use the same unit.")
    winning_side = max(values, key=lambda side: values[side].value)
    return winning_side, values[winning_side]


def _compute_vh_by_side(
    case: AISC358MomentCase,
    rule_binding: object,
) -> dict[str, Any]:
    mpr_data = _compute_mpr_by_side(case, rule_binding)
    force_unit = "kip" if case.units_system == UnitSystem.US else "kN"
    sides = _active_beam_sides(case)
    side_data: dict[str, Any] = {}

    for side in sides:
        mpr_side: Quantity = mpr_data["sides"][side]["mpr"]
        lh, lh_source = _require_geometry_by_side(
            case,
            base_field="beam_clear_span_length",
            side=side,
            rule_binding=rule_binding,
        )
        vgravity, vgravity_source = _require_load_by_side(
            case,
            base_field="beam_gravity_shear_between_hinges",
            side=side,
            rule_binding=rule_binding,
        )
        vhmax, vh_trace = compute_vh(
            mpr=mpr_side,
            lh=lh,
            vgravity_between_hinges=vgravity,
            unit_system=case.units_system,
        )
        base_shear = vh_trace["2mpr_over_lh"]
        vhmin = Quantity(value=base_shear - vgravity.value, unit=force_unit)
        side_data[side] = {
            "mpr": mpr_side,
            "lh": lh,
            "lh_source": lh_source,
            "vgravity": vgravity,
            "vgravity_source": vgravity_source,
            "2mpr_over_lh": base_shear,
            "vhmax": vhmax,
            "vhmin": vhmin,
        }

    vhmax_values = {side: data["vhmax"] for side, data in side_data.items()}
    governing_side, governing_vhmax = _select_max_quantity_by_side(vhmax_values)
    return {
        "mpr": mpr_data["governing_mpr"],
        "sides": side_data,
        "governing_vhmax_side": governing_side,
        "governing_vhmax": governing_vhmax,
    }


def _compute_mf_by_side(
    case: AISC358MomentCase,
    rule_binding: object,
) -> dict[str, Any]:
    vh_data = _compute_vh_by_side(case, rule_binding)
    sh_data = _compute_sh_by_side(case, rule_binding)
    side_data: dict[str, Any] = vh_data["sides"]
    for side, data in side_data.items():
        mpr_side = data["mpr"]
        vhmax = data["vhmax"]
        vhmin = data["vhmin"]
        sh = sh_data["sides"][side]["sh"]
        data["mf_derivation_sh"] = sh
        data["mfmax"] = compute_mf(
            mpr=mpr_side,
            vh=vhmax,
            sh=sh,
            unit_system=case.units_system,
        )
        data["mfmin"] = compute_mf(
            mpr=mpr_side,
            vh=vhmin,
            sh=sh,
            unit_system=case.units_system,
        )

    mfmax_values = {side: data["mfmax"] for side, data in side_data.items()}
    governing_side, governing_mfmax = _select_max_quantity_by_side(mfmax_values)
    return {
        **vh_data,
        "sh": sh_data["governing_sh"],
        "sh_by_side": {side: sh_data["sides"][side]["sh"] for side in sh_data["sides"]},
        "governing_mfmax_side": governing_side,
        "governing_mfmax": governing_mfmax,
    }


def _select_stated_vhmax_for_design(
    case: AISC358MomentCase,
    computed_by_side: dict[str, Any],
) -> tuple[Quantity, str]:
    candidates: dict[str, tuple[Quantity, str]] = {}
    for side in _active_beam_sides(case):
        side_specific = getattr(case.loads, f"shear_plastic_hinge_{side}max")
        if side_specific is not None:
            candidates[side] = (side_specific, f"loads.shear_plastic_hinge_{side}max")
        elif side == "der" and case.loads.shear_plastic_hinge is not None:
            candidates[side] = (case.loads.shear_plastic_hinge, "loads.shear_plastic_hinge")
        else:
            candidates[side] = (computed_by_side["sides"][side]["vhmax"], f"step4_computed_vhmax_{side}")
    governing_side = max(candidates, key=lambda item: candidates[item][0].value)
    selected, source = candidates[governing_side]
    return selected, f"{source} (governing_side={governing_side})"


def _select_vu_connection_for_design(
    case: AISC358MomentCase,
    rule_binding: object,
) -> tuple[Quantity, str]:
    vh_data = _compute_vh_by_side(case, rule_binding)
    vu_selected, source = _select_stated_vhmax_for_design(case, vh_data)
    return vu_selected, source


def _select_stated_mfmax_for_design(
    case: AISC358MomentCase,
    computed_by_side: dict[str, Any],
) -> tuple[Quantity, str]:
    if case.loads.probable_moment_column_face is not None:
        return case.loads.probable_moment_column_face, "loads.probable_moment_column_face (legacy)"
    governing_side = computed_by_side["governing_mfmax_side"]
    selected = computed_by_side["sides"][governing_side]["mfmax"]
    return selected, f"step5_computed_mf_{governing_side}max (governing_side={governing_side})"


def _compute_compactness_ca(
    *,
    pu: Quantity,
    ry: float,
    ag: Quantity,
    fy: Quantity,
    role: str,
    unit_system: UnitSystem,
) -> tuple[float, dict[str, Any]]:
    # US: ksi * in2 = kip. SI: MPa * mm2 = N, convert to kN for consistency with Pu(kN).
    denominator_base = ry * ag.value * fy.value
    denominator_force = denominator_base if unit_system == UnitSystem.US else denominator_base / 1000.0
    if denominator_force <= 0.0:
        raise ValueError(f"Invalid denominator for Ca calculation in {role}: Ry*Ag*Fy must be positive.")
    ca = pu.value / denominator_force
    return ca, {
        "pu": pu.model_dump(),
        "ry": ry,
        "ag": ag.model_dump(),
        "fy": fy.model_dump(),
        "formula": "Ca = Pu / (Ry * Ag * Fy)",
        "denominator_base": denominator_base,
        "denominator_force_units": denominator_force,
    }


def _compute_sh_by_side(case: AISC358MomentCase, rule_binding: object) -> dict[str, Any]:
    stiffener_length = case.geometry.stiffener_length
    end_plate_thickness = case.geometry.end_plate_thickness
    if case.connection_type == "bueep_4e":
        stiffener_length = None
        end_plate_thickness = None
    else:
        de = _require(case, "geometry.de", rule_binding)
        pfo = _require(case, "geometry.pfo", rule_binding)
        pb = _optional_pb_for_connection(case, rule_binding) if case.connection_type == "bseep_8es" else None
        hst = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo, pb=pb)
        stiffener_length = _derive_stiffener_length_from_hst(
            stiffener_height=hst,
            unit_system=case.units_system,
        )
        end_plate_thickness = _require(case, "geometry.end_plate_thickness", rule_binding)
    side_data: dict[str, Any] = {}
    for side in _active_beam_sides(case):
        beam_profile = _beam_profile_by_side(case, side)
        sh = compute_sh(
            connection_type=case.connection_type,
            beam_depth=beam_profile["d"],
            beam_flange_width=beam_profile["bf"],
            stiffener_length=stiffener_length,
            end_plate_thickness=end_plate_thickness,
            unit_system=case.units_system,
        )
        side_data[side] = {
            "sh": sh,
            "beam_depth": beam_profile["d"],
            "beam_flange_width": beam_profile["bf"],
            "stiffener_length": stiffener_length,
            "end_plate_thickness": end_plate_thickness,
        }
    sh_values = {side: data["sh"] for side, data in side_data.items()}
    governing_side, governing_sh = _select_max_quantity_by_side(sh_values)
    return {"sides": side_data, "governing_side": governing_side, "governing_sh": governing_sh}


def _compute_sh(case: AISC358MomentCase, rule_binding: object) -> Quantity:
    return _compute_sh_by_side(case, rule_binding)["governing_sh"]


def _compute_vh(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, Any]]:
    vh_data = _compute_vh_by_side(case, rule_binding)
    governing_side = vh_data["governing_vhmax_side"]
    governing_vhmax = vh_data["governing_vhmax"]
    side_data = vh_data["sides"][governing_side]
    return governing_vhmax, {
        "mpr": vh_data["mpr"].value,
        "2mpr_over_lh": side_data["2mpr_over_lh"],
        "governing_side": governing_side,
    }


def _compute_mf(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, Any]]:
    mf_data = _compute_mf_by_side(case, rule_binding)
    governing_side = mf_data["governing_mfmax_side"]
    governing_mfmax = mf_data["governing_mfmax"]
    side_data = mf_data["sides"][governing_side]
    return governing_mfmax, {
        "mpr": mf_data["mpr"].value,
        "sh": mf_data["sh"].value,
        "vhmax": side_data["vhmax"].value,
        "vhmin": side_data["vhmin"].value,
        "governing_side": governing_side,
    }


def _optional_pb_for_connection(case: AISC358MomentCase, rule_binding: object) -> Quantity | None:
    if case.connection_type == "bseep_8es":
        return _require(case, "geometry.pb", rule_binding)
    return case.geometry.pb


def _compute_end_plate_h_distances(case: AISC358MomentCase, rule_binding: object) -> dict[str, Quantity | None]:
    beam_profile = _beam_profile(case)
    beam_depth = beam_profile["d"]
    beam_flange_thickness = beam_profile["tf"]
    pb = _optional_pb_for_connection(case, rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pfi = _require(case, "geometry.pfi", rule_binding)
    if case.connection_type == "bseep_8es":
        if pb is None:
            raise ValueError("geometry.pb is required for bseep_8es end-plate distances.")
        h1 = Quantity(
            value=beam_depth.value - 0.5 * beam_flange_thickness.value + pfo.value + pb.value,
            unit=beam_depth.unit,
        )
        h2 = Quantity(
            value=beam_depth.value - 0.5 * beam_flange_thickness.value + pfo.value,
            unit=beam_depth.unit,
        )
        h3 = Quantity(
            value=beam_depth.value - 1.5 * beam_flange_thickness.value - pfi.value,
            unit=beam_depth.unit,
        )
        h4 = Quantity(
            value=beam_depth.value - 1.5 * beam_flange_thickness.value - pfi.value - pb.value,
            unit=beam_depth.unit,
        )
    else:
        h1 = Quantity(
            value=beam_depth.value - 0.5 * beam_flange_thickness.value + pfo.value,
            unit=beam_depth.unit,
        )
        h2 = Quantity(
            value=beam_depth.value - 1.5 * beam_flange_thickness.value - pfi.value,
            unit=beam_depth.unit,
        )
        h3 = None
        h4 = None
    return {"h1": h1, "h2": h2, "h3": h3, "h4": h4}


def _compute_tension_bolt_line_distances(case: AISC358MomentCase, rule_binding: object) -> list[Quantity]:
    h = _compute_end_plate_h_distances(case, rule_binding)
    if case.connection_type == "bseep_8es":
        return [h["h1"], h["h2"], h["h3"], h["h4"]]
    return [h["h1"], h["h2"]]


def _compute_beam_available_shear_strength(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, Any]]:
    beam_profile = _beam_profile(case)
    beam_profile_der = _beam_profile_by_side(case, "der")
    beam_profile_izq = _beam_profile_by_side(case, "izq") if beam_connection_sides == "both_sides" else None
    d = beam_profile["d"]
    tw = beam_profile["tw"]
    kdes = _profile_kdes(beam_profile, role="beam", rule_binding=rule_binding)
    fybm = _require(case, "materials.beam_fy", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    shear_result = compute_beam_web_shear_yielding_strength(
        fy=fybm,
        tw=tw,
        d=d,
        kdes=kdes,
        elastic_modulus=elastic_modulus,
        unit_system=case.units_system,
        phi=1.0,
    )
    capacity = shear_result["phi_vn"]
    return capacity, {
        "h_clear": shear_result["h_clear"].value,
        "h_over_tw": shear_result["h_over_tw"],
        "kv": shear_result["kv"],
        "lambda_r": shear_result["lambda_r"],
        "cv1": shear_result["cv1"],
    }


def _select_mf_for_design(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, str, Quantity]:
    mf_data = _compute_mf_by_side(case, rule_binding)
    mf_computed = mf_data["governing_mfmax"]
    mf_selected, source = _select_stated_mfmax_for_design(case, mf_data)
    return mf_selected, source, mf_computed


def _derive_yp_from_tables_6_2_6_3_6_4(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, Any]]:
    bp = _require(case, "geometry.end_plate_width", rule_binding)
    g = _require(case, "geometry.bolt_gage", rule_binding)
    pfi_raw = _require(case, "geometry.pfi", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    de = _require(case, "geometry.de", rule_binding)
    pb = _optional_pb_for_connection(case, rule_binding)
    h = _compute_end_plate_h_distances(case, rule_binding)
    return compute_end_plate_yield_line_parameter(
        connection_type=case.connection_type,
        bp=bp,
        g=g,
        pfi=pfi_raw,
        pfo=pfo,
        de=de,
        pb=pb,
        h1=h["h1"],
        h2=h["h2"],
        h3=h["h3"],
        h4=h["h4"],
        unit_system=case.units_system,
    )


def _compute_standard_hole_diameter(*, bolt_diameter: Quantity, unit_system: UnitSystem) -> tuple[Quantity, dict[str, float | str]]:
    return compute_standard_hole_diameter_j33(
        bolt_diameter=bolt_diameter,
        unit_system=unit_system,
    )


def _normalize_end_plate_stiffener_weld_type(raw: str | None) -> str:
    if raw is None:
        return "cjp"
    normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
    if not normalized:
        return "cjp"
    if normalized in {"cjp", "complete_joint_penetration"}:
        return "cjp"
    if normalized in {"pjp", "partial_joint_penetration"}:
        return "pjp"
    if normalized in {"fillet", "double_sided_fillet", "single_sided_fillet", "single_sided_fille"}:
        return "fillet"
    return normalized


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
    mpr_data = _compute_mpr_by_side(case, rule_binding)
    fy: Quantity = mpr_data["fy"]
    ry: float = mpr_data["ry"]
    side_results: dict[str, dict[str, Any]] = mpr_data["sides"]
    ze_input = case.procedure.beam_plastic_section_modulus_ze if case.procedure is not None else None
    governing_side = mpr_data["governing_side"]
    mpr = side_results[governing_side]["mpr"]
    intermediates: dict[str, Any] = {
        "governing_side_mpr": governing_side,
    }
    for side, data in side_results.items():
        side_suffix = f"vg{side}"
        intermediates[f"cpr_{side}"] = data["cpr"]
        intermediates[f"mpr_{side}"] = data["mpr"].value
        intermediates[f"member_ductility_demand_beam_{side}"] = data["member_ductility_demand_beam"]

    stated_mpr = case.loads.probable_moment_plastic_hinge
    demand = mpr
    capacity = stated_mpr if stated_mpr is not None else mpr

    input_payload: dict[str, Any] = {
        "beam_fy": fy.model_dump(),
        "beam_steel_type": case.materials.profile_steel_type,
        "ry": ry,
        "ze_source": "sections_catalog_zx_by_side",
        "ze_input": ze_input.model_dump() if ze_input is not None else None,
        "stated_mpr": stated_mpr.model_dump() if stated_mpr is not None else None,
    }
    for side, data in side_results.items():
        suffix = f"vg{side}"
        input_payload[f"ze_{suffix}"] = data["ze"].model_dump()
        input_payload[f"member_ductility_demand_{suffix}"] = data["member_ductility_demand_beam"]

    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation="Mpr = Cpr * Ry * Fy * Ze",
        inputs=input_payload,
        intermediates=intermediates,
        design_factors={},
        units_trace={"mpr_computed": mpr.unit, "mpr_stated": capacity.unit},
    )


def run_step1a_member_compactness(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    column_profile = _column_profile(case)

    ry = _require(case, "design_factors.ry", rule_binding)
    column_ductility = _require(case, "design_factors.member_ductility_demand_column", rule_binding)
    beam_ductility = column_ductility
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    beam_fy = _require(case, "materials.beam_fy", rule_binding)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    pu_beam = _require(case, "loads.pu_viga", rule_binding)
    pu_column = _require(case, "loads.pu_columna", rule_binding)
    beam_ag = _profile_ag(beam_profile, role="beam", rule_binding=rule_binding)
    column_ag = _profile_ag(column_profile, role="column", rule_binding=rule_binding)
    ca_beam, ca_beam_trace = _compute_compactness_ca(
        pu=pu_beam,
        ry=ry,
        ag=beam_ag,
        fy=beam_fy,
        role="beam",
        unit_system=case.units_system,
    )
    ca_column, ca_column_trace = _compute_compactness_ca(
        pu=pu_column,
        ry=ry,
        ag=column_ag,
        fy=column_fy,
        role="column",
        unit_system=case.units_system,
    )

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
            "pu_viga": pu_beam.model_dump(),
            "pu_columna": pu_column.model_dump(),
            "ag_viga": beam_ag.model_dump(),
            "ag_columna": column_ag.model_dump(),
            "compactness_ca_beam_calculated": ca_beam,
            "compactness_ca_column_calculated": ca_column,
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
            "ca_beam_trace": ca_beam_trace,
            "ca_column_trace": ca_column_trace,
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
    sh_data = _compute_sh_by_side(case, rule_binding)
    sh = sh_data["governing_sh"]
    sides = sh_data["sides"]
    inputs_payload: dict[str, Any] = {
        "connection_type": case.connection_type,
        "governing_side_sh": sh_data["governing_side"],
    }
    intermediates_payload: dict[str, Any] = {}
    for side in ("izq", "der"):
        if side not in sides:
            continue
        suffix = f"vg{side}"
        side_item = sides[side]
        inputs_payload[f"d_{suffix}"] = side_item["beam_depth"].model_dump()
        inputs_payload[f"bf_{suffix}"] = side_item["beam_flange_width"].model_dump()
        if side_item["stiffener_length"] is not None:
            inputs_payload[f"L_pest_{suffix}"] = side_item["stiffener_length"].model_dump()
        if side_item["end_plate_thickness"] is not None:
            inputs_payload[f"tpe_{suffix}"] = side_item["end_plate_thickness"].model_dump()
        intermediates_payload[f"sh_{side}"] = side_item["sh"].value

    return _build_result(
        rule_binding=rule_binding,
        demand=sh,
        capacity=sh,
        equation="Sh_vglado = min(d_vglado/2, 3*bf_vglado) [4E] o Sh_vglado = L_pest_vglado + tpe_vglado [4ES/8ES]",
        inputs=inputs_payload,
        intermediates=intermediates_payload,
        design_factors={},
        units_trace={"sh": sh.unit},
    )


def run_step3_shear_at_plastic_hinge(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vh_data = _compute_vh_by_side(case, rule_binding)
    demand = vh_data["governing_vhmax"]
    _, selected_source = _select_stated_vhmax_for_design(case, vh_data)
    capacity = demand
    sides = _active_beam_sides(case)
    side_inputs: dict[str, Any] = {}
    side_intermediates: dict[str, Any] = {}
    for side in sides:
        side_data = vh_data["sides"][side]
        side_inputs[f"lh_{side}"] = side_data["lh"].model_dump()
        side_inputs[f"lh_{side}_source"] = side_data["lh_source"]
        side_inputs[f"vgravity_between_hinges_{side}"] = side_data["vgravity"].model_dump()
        side_inputs[f"vgravity_between_hinges_{side}_source"] = side_data["vgravity_source"]
        stated_side = getattr(case.loads, f"shear_plastic_hinge_{side}max")
        stated_side_source = f"loads.shear_plastic_hinge_{side}max"
        if side == "der" and stated_side is None and case.loads.shear_plastic_hinge is not None:
            stated_side = case.loads.shear_plastic_hinge
            stated_side_source = "loads.shear_plastic_hinge"
        selected_side = stated_side if stated_side is not None else side_data["vhmax"]
        selected_side_source = stated_side_source if stated_side is not None else f"step4_computed_vhmax_{side}"

        side_inputs[f"stated_vh_{side}max"] = stated_side.model_dump() if stated_side is not None else None
        side_inputs[f"selected_vh_{side}max_source"] = selected_side_source
        side_intermediates[f"2mpr_over_lh_{side}"] = side_data["2mpr_over_lh"]
        side_intermediates[f"mpr_{side}"] = side_data["mpr"].value
        side_intermediates[f"vh_{side}max"] = side_data["vhmax"].value
        side_intermediates[f"vh_{side}min"] = side_data["vhmin"].value
        side_intermediates[f"vh_{side}max_adopted"] = selected_side.value
    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation=(
            "Vhmax = 2*Mpr/Lh + Vgravity; "
            "Vhmin = 2*Mpr/Lh - Vgravity (Eq. 2.4-3, side-specific der/izq)"
        ),
        inputs={
            "beam_connection_sides": case.design_factors.beam_connection_sides,
            "governing_side_vhmax": vh_data["governing_vhmax_side"],
            "selected_vhmax_source": selected_source,
            **side_inputs,
        },
        intermediates={
            "mpr": vh_data["mpr"].value,
            **side_intermediates,
        },
        design_factors={},
        units_trace={"vhmax_governing": demand.unit, "vhmax_selected": capacity.unit},
    )


def run_step4_probable_moment_face_column(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf_data = _compute_mf_by_side(case, rule_binding)
    demand = mf_data["governing_mfmax"]
    _, selected_source = _select_stated_mfmax_for_design(case, mf_data)
    capacity = demand
    sides = _active_beam_sides(case)
    side_inputs: dict[str, Any] = {}
    side_intermediates: dict[str, Any] = {}
    for side in sides:
        side_data = mf_data["sides"][side]
        stated_side = case.loads.probable_moment_column_face if side == "der" else None
        side_inputs[f"stated_mf_{side}max"] = stated_side.model_dump() if stated_side is not None else None
        side_intermediates[f"mpr_{side}"] = side_data["mpr"].value
        side_intermediates[f"sh_{side}"] = mf_data["sh_by_side"][side].value
        side_intermediates[f"mf_{side}max"] = side_data["mfmax"].value
        side_intermediates[f"mf_{side}min"] = side_data["mfmin"].value
        side_intermediates[f"vh_{side}max"] = side_data["vhmax"].value
        side_intermediates[f"vh_{side}min"] = side_data["vhmin"].value
    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation=(
            "Mfmax = Mpr + Vhmax*Sh; "
            "Mfmin = Mpr + Vhmin*Sh (Eq. 2.4-4, side-specific der/izq)"
        ),
        inputs={
            "beam_connection_sides": case.design_factors.beam_connection_sides,
            "governing_side_mfmax": mf_data["governing_mfmax_side"],
            "selected_mfmax_source": selected_source,
            **side_inputs,
        },
        intermediates={
            "mpr": mf_data["mpr"].value,
            "sh": mf_data["sh"].value,
            **side_intermediates,
        },
        design_factors={},
        units_trace={"mfmax_governing": demand.unit, "mfmax_selected": capacity.unit},
    )


def run_step6_1_bolt_tension_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf_data = _compute_mf_by_side(case, rule_binding)
    if "izq" not in mf_data["sides"]:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 6.1.1 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    mf_vgizq_max = mf_data["sides"]["izq"]["mfmax"]
    mf_vgizq_min = mf_data["sides"]["izq"]["mfmin"]
    mf = mf_vgizq_max if mf_vgizq_max.value >= mf_vgizq_min.value else mf_vgizq_min
    mf_source = "max(Mf_vgizq_max, Mf_vgizq_min)"
    mf_computed = mf
    fnt = _require(case, "materials.bolt_fnt", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    h_distances = _compute_end_plate_h_distances(case, rule_binding)
    h1 = h_distances["h1"]
    h2 = h_distances["h2"]
    h3 = h_distances["h3"]
    h4 = h_distances["h4"]

    if case.connection_type == "bseep_8es":
        pu_result = compute_bseep_step6_1_bolt_tension_demand(
            mf=mf,
            h1=h1,
            h2=h2,
            h3=h3,
            h4=h4,
            connection_type=case.connection_type,
            unit_system=case.units_system,
        )
        ru_b_p_pos = pu_result["rut_b"]
        sum_h = pu_result["sum_h"].value
    else:
        pu_result = compute_moment_prequalified_step6_1_bolt_tension_demand(
            mf=mf,
            h1=h1,
            h2=h2,
            connection_type=case.connection_type,
            unit_system=case.units_system,
        )
        ru_b_p_pos = pu_result["rut_b"]
        sum_h = pu_result["sum_h"].value

    capacity_result = compute_bolt_tension_rupture_capacity_per_bolt(
        bolt_diameter=db,
        bolt_fnt=fnt,
        unit_system=case.units_system,
    )
    rnt_b = capacity_result["rnt_b"]
    phi_rn_b_p_pos = capacity_result["phi_rnt_b"]
    bolt_area_q = capacity_result["bolt_area"]
    bolt_area = bolt_area_q.value
    nominal_capacity = rnt_b.value
    phi = capacity_result["phi"]

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_b_p_pos,
        capacity=phi_rn_b_p_pos,
        equation=(
            (
                "Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq + h3_pe_vgizq + h4_pe_vgizq)); "
                if case.connection_type == "bseep_8es"
                else "Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq)); "
            )
            + "phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, "
            + "A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)"
        ),
        inputs={
            "mf": mf.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "mf_vgizq_critico": mf.model_dump(),
            "h1_pe_vgizq": h1.model_dump(),
            "h2_pe_vgizq": h2.model_dump(),
            "h3_pe_vgizq": h3.model_dump() if h3 is not None else None,
            "h4_pe_vgizq": h4.model_dump() if h4 is not None else None,
            "bolt_diameter": db.model_dump(),
            "bolt_fnt": fnt.model_dump(),
            "fnt_b_vgizq": fnt.model_dump(),
            "connection_type": case.connection_type,
        },
        intermediates={
            "sum_h": sum_h,
            "bolt_area": bolt_area,
            "a_b_vgizq": bolt_area_q.model_dump(),
            "rnt_b": rnt_b.value,
            "ru_b_p_pos": ru_b_p_pos.value,
            "phi_rn_b_p_pos": phi_rn_b_p_pos.value,
            "nominal_tension_capacity_per_bolt": nominal_capacity,
        },
        design_factors={"phi": phi},
        units_trace={"ru_b_p_pos": ru_b_p_pos.unit, "phi_rn_b_p_pos": phi_rn_b_p_pos.unit},
    )


def run_step6_2_bolt_shear_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vh_data = _compute_vh_by_side(case, rule_binding)
    if "izq" not in vh_data["sides"]:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 6.1.2 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    vh_vgizq_max = vh_data["sides"]["izq"]["vhmax"]
    vh_vgizq_min = vh_data["sides"]["izq"]["vhmin"]
    vh_crit = vh_vgizq_max if vh_vgizq_max.value >= vh_vgizq_min.value else vh_vgizq_min
    vh_source = "max(Vh_vgizq_max, Vh_vgizq_min)"
    fnv = _require(case, "materials.bolt_fnv", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    demand_result = compute_moment_prequalified_step6_2_bolt_shear_demand(
        vhmax=vh_crit,
        connection_type=case.connection_type,
        unit_system=case.units_system,
    )
    n_b_vgizq = demand_result["nb"]
    ru_b_v2_vgizq = demand_result["ruv2_b"]

    capacity_result = compute_bolt_shear_rupture_capacity_per_bolt(
        bolt_diameter=db,
        bolt_fnv=fnv,
        unit_system=case.units_system,
    )
    rnv_b = capacity_result["rnv_b"]
    phi_rn_b_v2_vgizq = capacity_result["phi_rnv_b"]
    bolt_area_q = capacity_result["bolt_area"]
    bolt_area = bolt_area_q.value
    nominal_capacity = rnv_b.value
    phi = capacity_result["phi"]

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_b_v2_vgizq,
        capacity=phi_rn_b_v2_vgizq,
        equation=(
            "Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, "
            "phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, "
            "Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, "
            "n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)"
        ),
        inputs={
            "vh_vgizq_critico": vh_crit.model_dump(),
            "vh_vgizq_critico_source": vh_source,
            "n_b_vgizq": n_b_vgizq,
            "bolt_diameter": db.model_dump(),
            "bolt_fnv": fnv.model_dump(),
            "fnv_b_vgizq": fnv.model_dump(),
            "thread_b_vgizq": getattr(case.materials, "bolt_thread_condition", None),
            "connection_type": case.connection_type,
        },
        intermediates={
            "bolt_area": bolt_area,
            "a_b_vgizq": bolt_area_q.model_dump(),
            "rnv_b": rnv_b.value,
            "ru_b_v2_vgizq": ru_b_v2_vgizq.value,
            "phi_rn_b_v2_vgizq": phi_rn_b_v2_vgizq.value,
            "nominal_shear_capacity_per_bolt": nominal_capacity,
        },
        design_factors={"phi": phi},
        units_trace={"ru_b_v2_vgizq": ru_b_v2_vgizq.unit, "phi_rn_b_v2_vgizq": phi_rn_b_v2_vgizq.unit},
    )


def run_step7_1_1_end_plate_flexural_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf_data = _compute_mf_by_side(case, rule_binding)
    if "izq" not in mf_data["sides"]:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 7.1.1 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    mf_vgizq_max = mf_data["sides"]["izq"]["mfmax"]
    mf_vgizq_min = mf_data["sides"]["izq"]["mfmin"]
    mf = mf_vgizq_max if mf_vgizq_max.value >= mf_vgizq_min.value else mf_vgizq_min
    mf_source = "max(Mf_vgizq_max, Mf_vgizq_min)"
    mf_computed = mf
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    fyp = _require(case, "materials.end_plate_fy", rule_binding)
    yp, yp_intermediates = _derive_yp_from_tables_6_2_6_3_6_4(case, rule_binding)

    phi = _require(case, "design_factors.phi_d", rule_binding)
    flexural_strength = compute_yield_line_flexural_strength(
        thickness=tp,
        fy=fyp,
        y_parameter=yp,
        phi=phi,
        divisor=1.0,
        unit_system=case.units_system,
        reference="AISC 358-22 Eq. 6.7-8 + Tables 6.2, 6.3 and 6.4",
        equation="phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq",
    )
    nominal_moment = flexural_strength["rn"].value
    design_moment = flexural_strength["phi_rn"].value
    phi_mnb = flexural_strength["phi_rn"]

    return _build_result(
        rule_binding=rule_binding,
        demand=mf,
        capacity=phi_mnb,
        equation=(
            "Ru_pe_m3_vgizq = Mf_vgizq_critico; "
            "phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq "
            "(AISC 358-22 Eq. 6.7-8)"
        ),
        inputs={
            "mf_vgizq_critico": mf.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "tpe_vgizq": tp.model_dump(),
            "fyp_pe_vgizq": fyp.model_dump(),
            "yp_pe_vgizq": yp.model_dump(),
            "yp_pe_vgizq_source": "derived_from_aisc358_tables_6_2_6_3_6_4",
            "yp_pe_vgizq_table": yp_intermediates["table_reference"],
            "yp_pe_vgizq_case": yp_intermediates["case_reference"],
            "yp_pe_vgizq_is_hardcoded": yp_intermediates.get("is_hardcoded", False),
        },
        intermediates={
            "nominal_moment": nominal_moment,
            "design_moment": design_moment,
            **yp_intermediates,
        },
        design_factors={"phi": phi},
        units_trace={"ru_pe_m3_vgizq": mf.unit, "phi_rn_pe_m3_vgizq": phi_mnb.unit},
    )


def run_step7_2_1_end_plate_shear_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf_data = _compute_mf_by_side(case, rule_binding)
    if "izq" not in mf_data["sides"]:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 7.2.1 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    mf_vgizq_max = mf_data["sides"]["izq"]["mfmax"]
    mf_vgizq_min = mf_data["sides"]["izq"]["mfmin"]
    mf_crit = mf_vgizq_max if mf_vgizq_max.value >= mf_vgizq_min.value else mf_vgizq_min
    mf_source = "max(Mf_vgizq_max, Mf_vgizq_min)"
    mf_computed = mf_crit

    beam_profile = _beam_profile_by_side(case, "izq")
    d_vgizq = beam_profile["d"]
    tf_vgizq = beam_profile["tf"]
    lever_arm = d_vgizq.value - tf_vgizq.value
    if lever_arm <= 0.0:
        raise ValueError("Beam lever arm (d_vgizq - tf_vgizq) must be positive for Step 7.2.1.")

    ru_pe_v1_vgizq = Quantity(
        value=mf_crit.value / (2.0 * lever_arm),
        unit="kip" if case.units_system == UnitSystem.US else "kN",
    )
    bpe_vgizq = _require(case, "geometry.end_plate_width", rule_binding)
    tpe_vgizq = _require(case, "geometry.end_plate_thickness", rule_binding)
    fyp_pe_vgizq = _require(case, "materials.end_plate_fy", rule_binding)
    phi = _require(case, "design_factors.phi_d", rule_binding)
    nominal_shear = 0.6 * fyp_pe_vgizq.value * bpe_vgizq.value * tpe_vgizq.value
    design_shear = phi * nominal_shear
    if case.units_system == UnitSystem.SI:
        nominal_shear /= 1000.0
        design_shear /= 1000.0
    phi_rn_pe_v1_vgizq = Quantity(value=design_shear, unit=ru_pe_v1_vgizq.unit)

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_pe_v1_vgizq,
        capacity=phi_rn_pe_v1_vgizq,
        equation=(
            "Ru_pe_v1_vgizq = Mf_vgizq_critico / (2*(d_vgizq - tf_vgizq)); "
            "phi*Rn_pe_v1_vgizq = phi * 0.6 * Fyp_pe_vgizq * bpe_vgizq * tpe_vgizq "
            "(AISC 358-22 Eq. 6.7-10)"
        ),
        inputs={
            "mf_vgizq_critico": mf_crit.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "d_vgizq": d_vgizq.model_dump(),
            "tf_vgizq": tf_vgizq.model_dump(),
            "bpe_vgizq": bpe_vgizq.model_dump(),
            "tpe_vgizq": tpe_vgizq.model_dump(),
            "fyp_pe_vgizq": fyp_pe_vgizq.model_dump(),
        },
        intermediates={
            "z_vgizq": lever_arm,
            "ru_pe_v1_vgizq": nominal_shear,
            "phi_rn_pe_v1_vgizq": design_shear,
        },
        design_factors={"phi": phi},
        units_trace={"ru_pe_v1_vgizq": ru_pe_v1_vgizq.unit, "phi_rn_pe_v1_vgizq": phi_rn_pe_v1_vgizq.unit},
    )


def run_step7_2_2_end_plate_shear_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf_data = _compute_mf_by_side(case, rule_binding)
    if "izq" not in mf_data["sides"]:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 7.2.2 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    mf_vgizq_max = mf_data["sides"]["izq"]["mfmax"]
    mf_vgizq_min = mf_data["sides"]["izq"]["mfmin"]
    mf_crit = mf_vgizq_max if mf_vgizq_max.value >= mf_vgizq_min.value else mf_vgizq_min
    mf_source = "max(Mf_vgizq_max, Mf_vgizq_min)"
    mf_computed = mf_crit

    beam_profile = _beam_profile_by_side(case, "izq")
    d_vgizq = beam_profile["d"]
    tf_vgizq = beam_profile["tf"]
    lever_arm = d_vgizq.value - tf_vgizq.value
    if lever_arm <= 0.0:
        raise ValueError("Beam lever arm (d_vgizq - tf_vgizq) must be positive for Step 7.2.2.")

    rn_pe_v2_vgizq = Quantity(
        value=mf_crit.value / (2.0 * lever_arm),
        unit="kip" if case.units_system == UnitSystem.US else "kN",
    )
    bpe_vgizq = _require(case, "geometry.end_plate_width", rule_binding)
    tpe_vgizq = _require(case, "geometry.end_plate_thickness", rule_binding)
    fup_pe_vgizq = _require(case, "materials.end_plate_fu", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    dh, dh_inter = _compute_standard_hole_diameter(bolt_diameter=db, unit_system=case.units_system)

    phi = 0.9
    edge_allowance = 1.0 / 16.0 if case.units_system == UnitSystem.US else 1.6
    net_width = bpe_vgizq.value - 2.0 * (dh.value + edge_allowance)
    if net_width <= 0.0:
        raise ValueError("Net end-plate width (bpe - 2*(dh + 1.6 mm)) must be positive for Step 7.2.2.")
    nominal_strength = 0.6 * fup_pe_vgizq.value * tpe_vgizq.value * net_width
    design_strength = phi * nominal_strength
    if case.units_system == UnitSystem.SI:
        nominal_strength /= 1000.0
        design_strength /= 1000.0
    phi_rn_pe_v2_vgizq = Quantity(value=design_strength, unit=rn_pe_v2_vgizq.unit)

    if case.units_system == UnitSystem.US:
        edge_allowance_label = "1/16 in"
    else:
        edge_allowance_label = "1.6 mm"

    return _build_result(
        rule_binding=rule_binding,
        demand=rn_pe_v2_vgizq,
        capacity=phi_rn_pe_v2_vgizq,
        equation=(
            "Rn_pe_v2_vgizq = Ru_pe_m3_vgizq / (2*(d_vgizq - tf_vgizq)); "
            f"phi*Rn_pe_v2_vgizq = phi * 0.6 * Fup_pe_vgizq * tpe_vgizq * (bpe_vgizq - 2*(dh_pe_vgizq + {edge_allowance_label})) "
            "(AISC 358-22 Eq. 6.7-12)"
        ),
        inputs={
            "ru_pe_m3_vgizq": mf_crit.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "d_vgizq": d_vgizq.model_dump(),
            "tf_vgizq": tf_vgizq.model_dump(),
            "bpe_vgizq": bpe_vgizq.model_dump(),
            "tpe_vgizq": tpe_vgizq.model_dump(),
            "fup_pe_vgizq": fup_pe_vgizq.model_dump(),
            "db": db.model_dump(),
            "dh_pe_vgizq": dh.model_dump(),
        },
        intermediates={
            "z_vgizq": lever_arm,
            "net_width": net_width,
            "nominal_shear": nominal_strength,
            "design_shear": phi_rn_pe_v2_vgizq.value,
            "phi_n": phi,
            "edge_allowance": edge_allowance,
            **dh_inter,
        },
        design_factors={"phi": phi},
        units_trace={"rn_pe_v2_vgizq": rn_pe_v2_vgizq.unit, "phi_rn_pe_v2_vgizq": phi_rn_pe_v2_vgizq.unit},
    )


def _compute_step7_3_lc(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, float]]:
    uses_pb = case.connection_type == "bseep_8es"
    pb = _require(case, "geometry.pb", rule_binding) if uses_pb else case.geometry.pb
    pfo = _require(case, "geometry.pfo", rule_binding)
    pfi = _require(case, "geometry.pfi", rule_binding)
    beam_profile = _beam_profile(case)
    tbf = beam_profile["tf"]
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    dh, dh_inter = _compute_standard_hole_diameter(bolt_diameter=db, unit_system=case.units_system)

    lc_1 = (pb.value - dh.value) if pb is not None else float("nan")
    lc_2 = pfo.value + pfi.value + tbf.value - dh.value
    if uses_pb:
        lc_value = min(lc_1, lc_2)
        lc_rule = 1.0  # 1 => min(pb-dh, pfo+pfi+tbf-dh)
    else:
        lc_value = lc_2
        lc_rule = 2.0  # 2 => pfo+pfi+tbf-dh
    if lc_value <= 0.0:
        raise ValueError("Computed lc must be positive for Step 7.3 checks.")

    lc = Quantity(value=lc_value, unit=(pb.unit if pb is not None else pfo.unit))
    return lc, {
        "lc_1_pb_minus_dh": lc_1,
        "lc_2_pfo_plus_pfi_plus_tbf_minus_dh": lc_2,
        "lc_rule_selector": lc_rule,
        "dh": dh.value,
        "db": db.value,
        **dh_inter,
    }


def run_step7_3_1_end_plate_hole_tearout(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vh_data = _compute_vh_by_side(case, rule_binding)
    if "izq" not in vh_data["sides"]:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 7.3.1 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    vh_vgizq_max = vh_data["sides"]["izq"]["vhmax"]
    vh_vgizq_min = vh_data["sides"]["izq"]["vhmin"]
    vh_crit = vh_vgizq_max if vh_vgizq_max.value >= vh_vgizq_min.value else vh_vgizq_min
    vh_source = "max(Vh_vgizq_max, Vh_vgizq_min)"
    n_b_vgizq = _compression_bolt_count(case)
    ru_pe_v2_vgizq = Quantity(value=vh_crit.value / float(n_b_vgizq), unit=vh_crit.unit)

    lc, lc_inter = _compute_step7_3_lc(case, rule_binding)
    tpe_vgizq = _require(case, "geometry.end_plate_thickness", rule_binding)
    fup_pe_vgizq = _require(case, "materials.end_plate_fu", rule_binding)
    tf_vgizq = _beam_profile_by_side(case, "izq")["tf"]
    pb_pe_vgizq = _require(case, "geometry.pb", rule_binding) if case.connection_type == "bseep_8es" else case.geometry.pb
    pfo_pe_vgizq = _require(case, "geometry.pfo", rule_binding)
    pfi_pe_vgizq = _require(case, "geometry.pfi", rule_binding)
    dh_pe_vgizq = Quantity(value=lc_inter["dh"], unit=lc.unit)
    phi = 0.9

    phi_rn_pe_v2_vgizq, cap_intermediate = compute_end_plate_hole_tearout_capacity(
        end_plate_fu=fup_pe_vgizq,
        clear_distance_lc=lc,
        end_plate_thickness=tpe_vgizq,
        phi_n=phi,
        unit_system=case.units_system,
    )

    lc_formula = (
        "lc_pe_vgizq = min(pb_pe_vgizq - dh_pe_vgizq, pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq)"
        if case.connection_type == "bseep_8es"
        else "lc_pe_vgizq = pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq"
    )

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_pe_v2_vgizq,
        capacity=phi_rn_pe_v2_vgizq,
        equation=(
            f"{lc_formula}; "
            "Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; "
            "phi*Rn_pe_v2_vgizq = phi * 1.2 * lc_pe_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)"
        ),
        inputs={
            "vh_vgizq_critico": vh_crit.model_dump(),
            "vh_vgizq_critico_source": vh_source,
            "n_b_vgizq": n_b_vgizq,
            "lc_pe_vgizq": lc.model_dump(),
            "tpe_vgizq": tpe_vgizq.model_dump(),
            "fup_pe_vgizq": fup_pe_vgizq.model_dump(),
            "pfo_pe_vgizq": pfo_pe_vgizq.model_dump(),
            "pfi_pe_vgizq": pfi_pe_vgizq.model_dump(),
            "pb_pe_vgizq": pb_pe_vgizq.model_dump() if pb_pe_vgizq is not None else None,
            "tf_vgizq": tf_vgizq.model_dump(),
            "dh_pe_vgizq": dh_pe_vgizq.model_dump(),
        },
        intermediates={
            **lc_inter,
            "ru_pe_v2_vgizq": ru_pe_v2_vgizq.value,
            "nominal_strength": cap_intermediate["nominal_strength"],
            "design_strength": phi_rn_pe_v2_vgizq.value,
        },
        design_factors={"phi": phi},
        units_trace={"ru_pe_v2_vgizq": ru_pe_v2_vgizq.unit, "phi_rn_pe_v2_vgizq": phi_rn_pe_v2_vgizq.unit},
    )


def run_step7_3_2_end_plate_hole_bearing(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vh_data = _compute_vh_by_side(case, rule_binding)
    if "izq" not in vh_data["sides"]:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 7.3.2 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    vh_vgizq_max = vh_data["sides"]["izq"]["vhmax"]
    vh_vgizq_min = vh_data["sides"]["izq"]["vhmin"]
    vh_crit = vh_vgizq_max if vh_vgizq_max.value >= vh_vgizq_min.value else vh_vgizq_min
    vh_source = "max(Vh_vgizq_max, Vh_vgizq_min)"
    n_b_vgizq = _compression_bolt_count(case)
    ru_pe_v2_vgizq = Quantity(value=vh_crit.value / float(n_b_vgizq), unit=vh_crit.unit)

    tpe_vgizq = _require(case, "geometry.end_plate_thickness", rule_binding)
    fup_pe_vgizq = _require(case, "materials.end_plate_fu", rule_binding)
    d_b_vgizq = _require(case, "geometry.bolt_diameter", rule_binding)
    phi = 0.9

    phi_rn_pe_v2_vgizq, cap_intermediate = compute_end_plate_hole_bearing_capacity(
        end_plate_fu=fup_pe_vgizq,
        bolt_diameter=d_b_vgizq,
        end_plate_thickness=tpe_vgizq,
        phi_n=phi,
        unit_system=case.units_system,
    )

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_pe_v2_vgizq,
        capacity=phi_rn_pe_v2_vgizq,
        equation=(
            "Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; "
            "phi*Rn_pe_v2_vgizq = phi * 2.4 * d_b_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)"
        ),
        inputs={
            "vh_vgizq_critico": vh_crit.model_dump(),
            "vh_vgizq_critico_source": vh_source,
            "n_b_vgizq": n_b_vgizq,
            "tpe_vgizq": tpe_vgizq.model_dump(),
            "fup_pe_vgizq": fup_pe_vgizq.model_dump(),
            "d_b_vgizq": d_b_vgizq.model_dump(),
        },
        intermediates={
            "ru_pe_v2_vgizq": ru_pe_v2_vgizq.value,
            "nominal_strength": cap_intermediate["nominal_strength"],
            "design_strength": phi_rn_pe_v2_vgizq.value,
        },
        design_factors={"phi": phi},
        units_trace={"ru_pe_v2_vgizq": ru_pe_v2_vgizq.unit, "phi_rn_pe_v2_vgizq": phi_rn_pe_v2_vgizq.unit},
    )


def run_step8_1_1_stiffener_weld_tension_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    weld_type_raw = case.geometry.end_plate_stiffener_weld_type
    weld_type = _normalize_end_plate_stiffener_weld_type(weld_type_raw)

    if weld_type == "cjp":
        return _build_result(
            rule_binding=rule_binding,
            demand=Quantity(value=0.0, unit="ratio"),
            capacity=Quantity(value=1.0, unit="ratio"),
            equation="CJP => cumple (AISC 360-22 J2.4)",
            inputs={
                "end_plate_stiffener_weld_type": weld_type_raw,
                "weld_type_normalized": weld_type,
                "tipo_w1_vgizq": weld_type,
            },
            intermediates={},
            design_factors={},
            units_trace={"dcr": "ratio"},
        )

    if weld_type != "fillet":
        raise ValueError(
            "Unsupported geometry.end_plate_stiffener_weld_type for Step 8.1.1. "
            "Allowed values: CJP or fillet variants."
        )

    stiffener_fy = _require(case, "materials.stiffener_fy", rule_binding)
    stiffener_thickness = _require(case, "geometry.stiffener_thickness", rule_binding)
    de = _require(case, "geometry.de", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pb = _optional_pb_for_connection(case, rule_binding) if case.connection_type == "bseep_8es" else None
    h_pest_vgizq = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo, pb=pb)
    weld_fexx = _require(case, "materials.weld_fexx", rule_binding)
    c_pest_vgizq = _stiffener_clip_distance(case.units_system)
    l_gap_w1_vgizq = case.geometry.L_gap_w1 or c_pest_vgizq
    l_gap_w1_source = "geometry.L_gap_w1" if case.geometry.L_gap_w1 is not None else "fallback:c_pest_vgizq"
    kds_w1_vgizq = _require(case, "geometry.kds_w1_vgizq", rule_binding)

    wst = case.geometry.end_plate_stiffener_weld_size_wst
    wst_source = "geometry.end_plate_stiffener_weld_size_wst"
    if wst is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["geometry.end_plate_stiffener_weld_size_wst"],
            message=(
                "Required input 'geometry.end_plate_stiffener_weld_size_wst' is missing for "
                "Step 8.1.1 fillet weld check."
            ),
        )

    if l_gap_w1_vgizq.unit == h_pest_vgizq.unit:
        l_gap_w1_for_calc = l_gap_w1_vgizq.value
    elif l_gap_w1_vgizq.unit == "mm" and h_pest_vgizq.unit == "in":
        l_gap_w1_for_calc = l_gap_w1_vgizq.value / 25.4
    elif l_gap_w1_vgizq.unit == "in" and h_pest_vgizq.unit == "mm":
        l_gap_w1_for_calc = l_gap_w1_vgizq.value * 25.4
    else:
        raise ValueError(
            f"Unsupported mixed units for l_w1_vgizq derivation: {h_pest_vgizq.unit} vs {l_gap_w1_vgizq.unit}"
        )

    l_w1_vgizq = Quantity(
        value=h_pest_vgizq.value - (2.0 * l_gap_w1_for_calc) - c_pest_vgizq.value,
        unit=h_pest_vgizq.unit,
    )
    lst_source = "derived_hst_minus_2L_gap_w1_minus_clip_st"
    if l_w1_vgizq.value <= 0.0:
        raise ValueError("Derived weld_1 length (l_w1 = h_pest - 2*L_gap_w1 - c_pest) must be positive.")

    nl = case.geometry.end_plate_stiffener_weld_lines_nl if case.geometry.end_plate_stiffener_weld_lines_nl is not None else 2
    if nl <= 0:
        raise ValueError("geometry.end_plate_stiffener_weld_lines_nl must be >= 1 for Step 8.1.1.")

    demand_result = compute_plate_tension_demand_from_yielding(
        fy=stiffener_fy,
        thickness=stiffener_thickness,
        effective_length=h_pest_vgizq,
        unit_system=case.units_system,
    )
    ru_w1_p_pos_vgizq = demand_result["pu"]
    phi = _require(case, "design_factors.phi_f", rule_binding)
    weld_check = compute_fillet_weld_check_with_kds(
        demand=ru_w1_p_pos_vgizq,
        fexx=weld_fexx,
        weld_size=wst,
        weld_length=l_w1_vgizq,
        weld_lines=nl,
        kds=kds_w1_vgizq,
        unit_system=case.units_system,
        phi=phi,
    )
    phi_rn_w1_p_pos_vgizq = weld_check["phi_rn"]

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_w1_p_pos_vgizq,
        capacity=phi_rn_w1_p_pos_vgizq,
        equation=(
            "Fillet: Ru_w1_p+_vgizq = Fys_pest_vgizq * t_pest_vgizq * h_pest_vgizq; "
            "l_w1_vgizq = h_pest_vgizq - 2*L_gap_w1_vgizq - c_pest_vgizq; "
            "phi*Rn_w1_p+_vgizq = phi * kds_w1_vgizq * nl_w1_vgizq * 0.6 * Fexx_w1_vgizq "
            "* 0.707 * l_w1_vgizq * w_w1_vgizq; "
            "DCR_w1_p+_vgizq = Ru_w1_p+_vgizq / phi*Rn_w1_p+_vgizq "
            "(AISC 360-22 J2.4)"
        ),
        inputs={
            "end_plate_stiffener_weld_type": weld_type_raw,
            "weld_type_normalized": weld_type,
            "tipo_w1_vgizq": weld_type,
            "fys_pest_vgizq": stiffener_fy.model_dump(),
            "t_pest_vgizq": stiffener_thickness.model_dump(),
            "h_pest_vgizq": h_pest_vgizq.model_dump(),
            "c_pest_vgizq": c_pest_vgizq.model_dump(),
            "L_gap_w1_vgizq": l_gap_w1_vgizq.model_dump(),
            "L_gap_w1_source": l_gap_w1_source,
            "fexx": weld_fexx.model_dump(),
            "fexx_w1_vgizq": weld_fexx.model_dump(),
            "l_w1_vgizq": l_w1_vgizq.model_dump(),
            "lst_source": lst_source,
            "wst": wst.model_dump(),
            "w_w1_vgizq": wst.model_dump(),
            "wst_source": wst_source,
            "nl": nl,
            "nl_w1_vgizq": nl,
            "kds_w1_vgizq": kds_w1_vgizq,
        },
        intermediates={
            "ru_w1_p_pos_vgizq_nominal": demand_result["pu_base_force"],
            "rn_w1_p_pos_vgizq_nominal": weld_check["rn_base_force"],
            "phi_rn_w1_p_pos_vgizq_nominal": weld_check["phi_rn_base_force"],
            "ru_w1_p_pos_vgizq": ru_w1_p_pos_vgizq.value,
            "phi_rn_w1_p_pos_vgizq": phi_rn_w1_p_pos_vgizq.value,
            "dcr_w1_p_pos_vgizq": weld_check["dcr"],
        },
        design_factors={"phi": phi},
        units_trace={"ru_w1_p_pos_vgizq": ru_w1_p_pos_vgizq.unit, "phi_rn_w1_p_pos_vgizq": phi_rn_w1_p_pos_vgizq.unit},
    )


def run_step9_1_1_stiffener_beam_weld_shear_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    weld_type_raw = case.geometry.beam_stiffener_weld_type
    weld_type_source = "geometry.beam_stiffener_weld_type"
    if weld_type_raw is None:
        weld_type_raw = case.geometry.end_plate_stiffener_weld_type
        weld_type_source = "geometry.end_plate_stiffener_weld_type"
    weld_type = _normalize_end_plate_stiffener_weld_type(weld_type_raw)

    if weld_type == "cjp":
        return _build_result(
            rule_binding=rule_binding,
            demand=Quantity(value=0.0, unit="ratio"),
            capacity=Quantity(value=1.0, unit="ratio"),
            equation="CJP => cumple (AISC 360-22 J2.4)",
            inputs={
                "beam_stiffener_weld_type": weld_type_raw,
                "weld_type_source": weld_type_source,
                "weld_type_normalized": weld_type,
                "tipo_w2_vgizq": weld_type,
                "kds_w2_vgizq": _require(case, "geometry.kds_w2_vgizq", rule_binding),
            },
            intermediates={},
            design_factors={},
            units_trace={"dcr": "ratio"},
        )

    if weld_type != "fillet":
        raise ValueError(
            "Unsupported beam stiffener weld type for Step 9.1.1. "
            "Allowed values: CJP or fillet variants."
        )

    stiffener_fy = _require(case, "materials.stiffener_fy", rule_binding)
    stiffener_thickness = _require(case, "geometry.stiffener_thickness", rule_binding)
    weld_fexx = _require(case, "materials.weld_fexx", rule_binding)
    de = _require(case, "geometry.de", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pb = _optional_pb_for_connection(case, rule_binding) if case.connection_type == "bseep_8es" else None
    h_pest_vgizq = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo, pb=pb)
    l_pest_vgizq = _derive_stiffener_length_from_hst(stiffener_height=h_pest_vgizq, unit_system=case.units_system)
    c_pest_vgizq = _stiffener_clip_distance(case.units_system)
    l_gap_w2_vgizq = case.geometry.L_gap_w2 or c_pest_vgizq
    l_gap_w2_source = "geometry.L_gap_w2" if case.geometry.L_gap_w2 is not None else "fallback:c_pest_vgizq"

    wst2 = case.geometry.beam_stiffener_weld_size_wst2
    wst2_source = "geometry.beam_stiffener_weld_size_wst2"
    if wst2 is None:
        wst2 = case.geometry.end_plate_stiffener_weld_size_wst
        wst2_source = "geometry.end_plate_stiffener_weld_size_wst"
    if wst2 is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["geometry.beam_stiffener_weld_size_wst2"],
            message=(
                "Required input 'geometry.beam_stiffener_weld_size_wst2' is missing for "
                "Step 9.1.1 fillet weld check."
            ),
        )

    if l_gap_w2_vgizq.unit == l_pest_vgizq.unit:
        l_gap_w2_for_calc = l_gap_w2_vgizq.value
    elif l_gap_w2_vgizq.unit == "mm" and l_pest_vgizq.unit == "in":
        l_gap_w2_for_calc = l_gap_w2_vgizq.value / 25.4
    elif l_gap_w2_vgizq.unit == "in" and l_pest_vgizq.unit == "mm":
        l_gap_w2_for_calc = l_gap_w2_vgizq.value * 25.4
    else:
        raise ValueError(
            f"Unsupported mixed units for l_w2_vgizq derivation: {l_pest_vgizq.unit} vs {l_gap_w2_vgizq.unit}"
        )
    l_w2_vgizq = Quantity(
        value=l_pest_vgizq.value - (2.0 * l_gap_w2_for_calc) - c_pest_vgizq.value,
        unit=l_pest_vgizq.unit,
    )
    lst_w2_source = "derived_lst_minus_2L_gap_w2_minus_clip_st"
    if l_w2_vgizq.value <= 0.0:
        raise ValueError("Derived weld_2 length (l_w2 = L_pest - 2*L_gap_w2 - c_pest) must be positive.")

    nl_w2 = case.geometry.beam_stiffener_weld_lines_nl_w2
    nl_w2_source = "geometry.beam_stiffener_weld_lines_nl_w2"
    if nl_w2 is None:
        nl_w2 = case.geometry.end_plate_stiffener_weld_lines_nl
        nl_w2_source = "geometry.end_plate_stiffener_weld_lines_nl"
    if nl_w2 is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[
                "geometry.beam_stiffener_weld_lines_nl_w2",
                "geometry.end_plate_stiffener_weld_lines_nl",
            ],
            message=(
                "Required input for weld-line count is missing. "
                "Provide 'geometry.beam_stiffener_weld_lines_nl_w2' or "
                "'geometry.end_plate_stiffener_weld_lines_nl'. "
                "No default value is allowed under zero-guess policy."
            ),
        )
    if nl_w2 <= 0:
        raise ValueError("beam_stiffener_weld_lines_nl_w2 must be >= 1 for Step 9.1.1.")
    kds_w2_vgizq = _require(case, "geometry.kds_w2_vgizq", rule_binding)

    demand_result = compute_plate_shear_demand_from_yielding(
        fy=stiffener_fy,
        thickness=stiffener_thickness,
        effective_length=l_w2_vgizq,
        unit_system=case.units_system,
    )
    ru_w2_v2_vgizq = demand_result["vu"]
    phi = _require(case, "design_factors.phi_f", rule_binding)
    weld_strength = compute_fillet_weld_check_with_kds(
        demand=ru_w2_v2_vgizq,
        fexx=weld_fexx,
        weld_size=wst2,
        weld_length=l_w2_vgizq,
        weld_lines=nl_w2,
        kds=kds_w2_vgizq,
        unit_system=case.units_system,
        phi=phi,
    )
    phi_rn_w2_v2_vgizq = weld_strength["phi_rn"]

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_w2_v2_vgizq,
        capacity=phi_rn_w2_v2_vgizq,
        equation=(
            "Fillet: Ru_w2_v2_vgizq = Fys_pest_vgizq * 0.6 * t_pest_vgizq * l_w2_vgizq; "
            "l_w2_vgizq = L_pest_vgizq - 2*L_gap_w2_vgizq - c_pest_vgizq; "
            "phi*Rn_w2_v2_vgizq = phi * kds_w2_vgizq * nl_w2_vgizq * 0.6 * Fexx_w2_vgizq * 0.707 * l_w2_vgizq * w_w2_vgizq; "
            "DCR_w2_v2_vgizq = Ru_w2_v2_vgizq / phi*Rn_w2_v2_vgizq "
            "(AISC 360-22W J2b(g))"
        ),
        inputs={
            "beam_stiffener_weld_type": weld_type_raw,
            "weld_type_source": weld_type_source,
            "weld_type_normalized": weld_type,
            "tipo_w2_vgizq": weld_type,
            "fys": stiffener_fy.model_dump(),
            "fys_pest_vgizq": stiffener_fy.model_dump(),
            "ts": stiffener_thickness.model_dump(),
            "t_pest_vgizq": stiffener_thickness.model_dump(),
            "fexx": weld_fexx.model_dump(),
            "fexx_w2_vgizq": weld_fexx.model_dump(),
            "hst": h_pest_vgizq.model_dump(),
            "h_pest_vgizq": h_pest_vgizq.model_dump(),
            "lst": l_pest_vgizq.model_dump(),
            "l_pest_vgizq": l_pest_vgizq.model_dump(),
            "clip_st": c_pest_vgizq.model_dump(),
            "c_pest_vgizq": c_pest_vgizq.model_dump(),
            "L_gap_w2_vgizq": l_gap_w2_vgizq.model_dump(),
            "L_gap_w2_source": l_gap_w2_source,
            "lst_w2": l_w2_vgizq.model_dump(),
            "l_w2_vgizq": l_w2_vgizq.model_dump(),
            "lst_w2_source": lst_w2_source,
            "wst2": wst2.model_dump(),
            "w_w2_vgizq": wst2.model_dump(),
            "wst2_source": wst2_source,
            "nl_w2": nl_w2,
            "nl_w2_vgizq": nl_w2,
            "kds_w2_vgizq": kds_w2_vgizq,
            "nl_w2_source": nl_w2_source,
        },
        intermediates={
            "ru_w2_v2_vgizq_nominal": demand_result["vu_base_force"],
            "rn_w2_v2_vgizq_nominal": weld_strength["rn_base_force"],
            "phi_rn_w2_v2_vgizq_nominal": weld_strength["phi_rn_base_force"],
            "ru_w2_v2_vgizq": ru_w2_v2_vgizq.value,
            "phi_rn_w2_v2_vgizq": phi_rn_w2_v2_vgizq.value,
        },
        design_factors={"phi": phi},
        units_trace={
            "ru_w2_v2_vgizq": ru_w2_v2_vgizq.unit,
            "phi_rn_w2_v2_vgizq": phi_rn_w2_v2_vgizq.unit,
        },
    )


def run_step10_1_1_beam_flange_end_plate_weld_tension_rupture(
    case: AISC358MomentCase,
    rule_binding: object,
) -> CheckResult:
    if "izq" not in _active_beam_sides(case):
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 10.1.1 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )

    weld_type_raw = case.geometry.tipo_w4_vgizq
    weld_type = _normalize_end_plate_stiffener_weld_type(weld_type_raw)
    backing_thickness = case.geometry.t_w4_1_vgizq
    beam_profile_izq = _beam_profile_by_side(case, "izq")
    l_w4_vgizq = beam_profile_izq["bf"]
    weld_fexx_optional = case.materials.weld_fexx_w4_vgizq
    t_w4_vgizq_optional = case.geometry.t_w4_vgizq
    nl_w4_vgizq_optional = case.geometry.nl_w4_vgizq
    kds_w4_vgizq_optional = case.geometry.kds_w4_vgizq

    if weld_type == "cjp":
        return _build_result(
            rule_binding=rule_binding,
            demand=Quantity(value=0.0, unit="ratio"),
            capacity=Quantity(value=1.0, unit="ratio"),
            equation="CJP => cumple (AISC 360-22 J2.4)",
            inputs={
                "tipo_w4_vgizq": weld_type,
                "mf_vgizq_critico": None,
                "d_vgizq": beam_profile_izq["d"].model_dump(),
                "tf_vgizq": beam_profile_izq["tf"].model_dump(),
                "bf_vgizq": beam_profile_izq["bf"].model_dump(),
                "l_w4_vgizq": l_w4_vgizq.model_dump(),
                "Fexx_w4_vgizq": weld_fexx_optional.model_dump() if weld_fexx_optional is not None else None,
                "t_w4_vgizq": t_w4_vgizq_optional.model_dump() if t_w4_vgizq_optional is not None else None,
                "nl_w4_vgizq": nl_w4_vgizq_optional,
                "kds_w4_vgizq": kds_w4_vgizq_optional,
                "t_w4_1_vgizq": backing_thickness.model_dump() if backing_thickness is not None else None,
            },
            intermediates={},
            design_factors={"phi": _require(case, "design_factors.phi_f", rule_binding)},
            units_trace={"dcr": "ratio"},
        )

    if weld_type != "fillet":
        raise ValueError(
            "Unsupported geometry.tipo_w4_vgizq for Step 10.1.1. "
            "Allowed values: CJP or fillet variants."
        )

    mf_data = _compute_mf_by_side(case, rule_binding)
    mf_vgizq_max = mf_data["sides"]["izq"]["mfmax"]
    mf_vgizq_min = mf_data["sides"]["izq"]["mfmin"]
    mf_vgizq_critico = mf_vgizq_max if mf_vgizq_max.value >= mf_vgizq_min.value else mf_vgizq_min
    flange_force, flange_force_intermediate = compute_beam_flange_force_from_mf(
        mf=mf_vgizq_critico,
        beam_depth=beam_profile_izq["d"],
        beam_flange_thickness=beam_profile_izq["tf"],
        unit_system=case.units_system,
    )
    weld_fexx = _require(case, "materials.weld_fexx_w4_vgizq", rule_binding)
    t_w4_vgizq = _require(case, "geometry.t_w4_vgizq", rule_binding)
    nl_w4_vgizq = _require(case, "geometry.nl_w4_vgizq", rule_binding)
    kds_w4_vgizq = _require(case, "geometry.kds_w4_vgizq", rule_binding)
    phi = _require(case, "design_factors.phi_f", rule_binding)

    weld_check = compute_fillet_weld_check_with_kds(
        demand=flange_force,
        fexx=weld_fexx,
        weld_size=t_w4_vgizq,
        weld_length=l_w4_vgizq,
        weld_lines=nl_w4_vgizq,
        kds=kds_w4_vgizq,
        unit_system=case.units_system,
        phi=phi,
    )

    return _build_result(
        rule_binding=rule_binding,
        demand=flange_force,
        capacity=weld_check["phi_rn"],
        equation=(
            "Ru_w4_p+_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); "
            "l_w4_vgizq = bf_vgizq; "
            "phi*Rn_w4_p+_vgizq = phi * kds_w4_vgizq * nl_w4_vgizq * 0.6 * Fexx_w4_vgizq * 0.707 * l_w4_vgizq * t_w4_vgizq; "
            "DCR_w4_p+_vgizq = Ru_w4_p+_vgizq / phi*Rn_w4_p+_vgizq (AISC 360-22 J2.4)"
        ),
        inputs={
            "tipo_w4_vgizq": weld_type,
            "mf_vgizq_critico": mf_vgizq_critico.model_dump(),
            "d_vgizq": beam_profile_izq["d"].model_dump(),
            "tf_vgizq": beam_profile_izq["tf"].model_dump(),
            "bf_vgizq": beam_profile_izq["bf"].model_dump(),
            "l_w4_vgizq": l_w4_vgizq.model_dump(),
            "Fexx_w4_vgizq": weld_fexx.model_dump(),
            "t_w4_vgizq": t_w4_vgizq.model_dump(),
            "nl_w4_vgizq": nl_w4_vgizq,
            "kds_w4_vgizq": kds_w4_vgizq,
            "t_w4_1_vgizq": backing_thickness.model_dump() if backing_thickness is not None else None,
        },
        intermediates={
            "lever_arm": flange_force_intermediate["lever_arm"],
            "ru_w4_p_pos_vgizq": flange_force.value,
            "phi_rn_w4_p_pos_vgizq": weld_check["phi_rn"].value,
        },
        design_factors={"phi": phi},
        units_trace={
            "ru_w4_p_pos_vgizq": flange_force.unit,
            "phi_rn_w4_p_pos_vgizq": weld_check["phi_rn"].unit,
        },
    )


def run_step10_1_1_beam_shear_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    if "izq" not in _active_beam_sides(case):
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 10.1.1 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'both_sides'."
            ),
        )
    beam_profile = _beam_profile_by_side(case, "izq")
    d_vgizq = beam_profile["d"]
    tw_vgizq = beam_profile["tw"]
    kdes_vgizq = _profile_kdes(beam_profile, role="beam", rule_binding=rule_binding)
    fy_vgizq = _require(case, "materials.beam_fy", rule_binding)
    e_vgizq = _require(case, "materials.elastic_modulus", rule_binding)
    vh_data = _compute_vh_by_side(case, rule_binding)
    vh_vgizq_max = vh_data["sides"]["izq"]["vhmax"]
    ru_v2_vgizq = vh_vgizq_max
    vh_source = "step4_computed_vhmax_izq"

    phi = 1.0
    shear_result = compute_beam_web_shear_yielding_strength(
        fy=fy_vgizq,
        tw=tw_vgizq,
        d=d_vgizq,
        kdes=kdes_vgizq,
        elastic_modulus=e_vgizq,
        unit_system=case.units_system,
        phi=phi,
    )
    phi_rn_v2_vgizq = shear_result["phi_vn"]
    nominal_shear = shear_result["vn"].value
    design_shear = phi_rn_v2_vgizq.value

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_v2_vgizq,
        capacity=phi_rn_v2_vgizq,
        equation=(
            "Ru_v2_vgizq = Vh_vgizq_max; Rn_v2_vgizq = 0.6 * Fy_vgizq * tw_vgizq * d_vgizq * Cv1; "
            "phi*Rn_v2_vgizq = phi * Rn_v2_vgizq; DCR_v2_vgizq = Ru_v2_vgizq / phi*Rn_v2_vgizq "
            "(AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)"
        ),
        inputs={
            "Vh_vgizq_max": ru_v2_vgizq.model_dump(),
            "Vh_vgizq_source": vh_source,
            "Fy_vgizq": fy_vgizq.model_dump(),
            "tw_vgizq": tw_vgizq.model_dump(),
            "d_vgizq": d_vgizq.model_dump(),
            "kdes_vgizq": kdes_vgizq.model_dump(),
            "E_vgizq": e_vgizq.model_dump(),
            "cv1": shear_result["cv1"],
        },
        intermediates={
            "h_clear": shear_result["h_clear"].value,
            "h_over_tw": shear_result["h_over_tw"],
            "kv": shear_result["kv"],
            "lambda_r": shear_result["lambda_r"],
            "cv1": shear_result["cv1"],
            "rn_v2_vgizq": nominal_shear,
            "phi_rn_v2_vgizq": design_shear,
        },
        design_factors={"phi": phi},
        units_trace={
            "Ru_v2_vgizq": ru_v2_vgizq.unit,
            "phi*Rn_v2_vgizq": phi_rn_v2_vgizq.unit,
        },
    )


def run_step11_1_1_beam_web_end_plate_weld_tension_rupture(
    case: AISC358MomentCase,
    rule_binding: object,
) -> CheckResult:
    if "izq" not in _active_beam_sides(case):
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["design_factors.beam_connection_sides"],
            message=(
                "Step 11.1.1 requires left-beam evaluation. "
                "Set design_factors.beam_connection_sides = 'left_only' or 'both_sides'."
            ),
        )

    weld_type_raw = case.geometry.end_plate_beam_web_weld_type
    weld_type = _normalize_end_plate_stiffener_weld_type(weld_type_raw)
    beam_profile = _beam_profile_by_side(case, "izq")
    fy_vgizq = _require(case, "materials.beam_fy", rule_binding)
    tw_vgizq = beam_profile["tw"]
    pfi = _require(case, "geometry.pfi", rule_binding)
    pb = _optional_pb_for_connection(case, rule_binding)
    if pb is None:
        pb = Quantity(value=0.0, unit=pfi.unit)
    extension = 150.0 if case.units_system == UnitSystem.SI else (150.0 / 25.4)
    hwef_w3_vgizq = Quantity(
        value=pfi.value + pb.value + extension,
        unit=pfi.unit,
    )
    demand_result = compute_plate_tension_demand_from_yielding(
        fy=fy_vgizq,
        thickness=tw_vgizq,
        effective_length=hwef_w3_vgizq,
        unit_system=case.units_system,
    )
    ru_w3_p_pos_vgizq = demand_result["pu"]
    phi = _require(case, "design_factors.phi_f", rule_binding)

    if weld_type == "cjp":
        return _build_result(
            rule_binding=rule_binding,
            demand=Quantity(value=0.0, unit="ratio"),
            capacity=Quantity(value=1.0, unit="ratio"),
            equation=(
                "CJP => cumple; Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq, "
                "hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm"
            ),
            inputs={
                "tipo_w3_vgizq": weld_type_raw,
                "hwef_w3_vgizq": hwef_w3_vgizq.model_dump(),
                "tw_vgizq": tw_vgizq.model_dump(),
                "fy_vgizq": fy_vgizq.model_dump(),
                "ru_w3_p_pos_vgizq": ru_w3_p_pos_vgizq.model_dump(),
            },
            intermediates={},
            design_factors={"phi": phi},
            units_trace={"dcr": "ratio"},
        )

    if weld_type != "fillet":
        raise ValueError(
            "Unsupported geometry.end_plate_beam_web_weld_type for Step 11.1.1. "
            "Allowed values: CJP or fillet variants."
        )

    twe = _require(case, "geometry.end_plate_beam_web_weld_thickness_twe", rule_binding)
    nl = _require(case, "geometry.end_plate_beam_web_weld_lines_nl", rule_binding)
    kds = _require(case, "geometry.kds_w3_vgizq", rule_binding)
    fexx = _require(case, "materials.weld_fexx", rule_binding)
    weld_check = compute_fillet_weld_check_with_kds(
        demand=ru_w3_p_pos_vgizq,
        fexx=fexx,
        weld_size=twe,
        weld_length=hwef_w3_vgizq,
        weld_lines=nl,
        kds=kds,
        unit_system=case.units_system,
        phi=phi,
    )

    return _build_result(
        rule_binding=rule_binding,
        demand=ru_w3_p_pos_vgizq,
        capacity=weld_check["phi_rn"],
        equation=(
            "Fillet: Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq; "
            "hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm; "
            "phi*Rn_w3_p+_vgizq = phi * kds_w3_vgizq * nl_w3_vgizq * 0.6 * Fexx_w3_vgizq * 0.707 * hwef_w3_vgizq * t_w3_vgizq; "
            "DCR_w3_p+_vgizq = Ru_w3_p+_vgizq / phi*Rn_w3_p+_vgizq"
        ),
        inputs={
            "tipo_w3_vgizq": weld_type_raw,
            "hwef_w3_vgizq": hwef_w3_vgizq.model_dump(),
            "tw_vgizq": tw_vgizq.model_dump(),
            "fy_vgizq": fy_vgizq.model_dump(),
            "fexx_w3_vgizq": fexx.model_dump(),
            "t_w3_vgizq": twe.model_dump(),
            "nl_w3_vgizq": nl,
            "kds_w3_vgizq": kds,
            "ru_w3_p_pos_vgizq": ru_w3_p_pos_vgizq.model_dump(),
        },
        intermediates={
            "ru_w3_p_pos_vgizq_nominal": demand_result["pu_base_force"],
            "rn_w3_p_pos_vgizq_nominal": weld_check["rn_base_force"],
            "phi_rn_w3_p_pos_vgizq_nominal": weld_check["phi_rn_base_force"],
            "ru_w3_p_pos_vgizq": ru_w3_p_pos_vgizq.value,
            "phi_rn_w3_p_pos_vgizq": weld_check["phi_rn"].value,
            "dcr_w3_p_pos_vgizq": weld_check["dcr"],
        },
        design_factors={"phi": phi},
        units_trace={
            "ru_w3_p_pos_vgizq": ru_w3_p_pos_vgizq.unit,
            "phi_rn_w3_p_pos_vgizq": weld_check["phi_rn"].unit,
        },
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
    beam_connection_sides = _require(case, "design_factors.beam_connection_sides", rule_binding)

    def _get_geometry_by_side(
        field_root: str,
        side_suffix: str,
        *,
        require_explicit_for_both_sides: bool = False,
    ) -> Any:
        side_attr = f"{field_root}_vg{side_suffix}"
        side_value = getattr(case.geometry, side_attr, None)
        if side_value is not None:
            return side_value
        if beam_connection_sides == "both_sides" and require_explicit_for_both_sides:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=[f"geometry.{side_attr}"],
                message=f"Required input 'geometry.{side_attr}' is missing for applicable rule.",
            )
        common_value = getattr(case.geometry, field_root, None)
        if common_value is not None:
            return common_value
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[f"geometry.{field_root}"],
            message=f"Required input 'geometry.{field_root}' is missing for applicable rule.",
        )

    def _get_material_by_side(
        field_root: str,
        side_suffix: str,
        *,
        require_explicit_for_both_sides: bool = False,
    ) -> Any:
        side_attr = f"{field_root}_vg{side_suffix}"
        side_value = getattr(case.materials, side_attr, None)
        if side_value is not None:
            return side_value
        if beam_connection_sides == "both_sides" and require_explicit_for_both_sides:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=[f"materials.{side_attr}"],
                message=f"Required input 'materials.{side_attr}' is missing for applicable rule.",
            )
        common_value = getattr(case.materials, field_root, None)
        if common_value is not None:
            return common_value
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[f"materials.{field_root}"],
            message=f"Required input 'materials.{field_root}' is missing for applicable rule.",
        )

    g_der = _get_geometry_by_side("bolt_gage", "der")
    db_der = _get_geometry_by_side("bolt_diameter", "der")
    bp_der = _get_geometry_by_side("end_plate_width", "der")
    de_der = _get_geometry_by_side("de", "der")
    pfo_der = _get_geometry_by_side("pfo", "der")
    pfi_der = _get_geometry_by_side("pfi", "der")
    tp_der = _get_geometry_by_side("end_plate_thickness", "der")
    ts_der = case.geometry.stiffener_thickness_vgder or case.geometry.stiffener_thickness
    pb_der = (
        _get_geometry_by_side("pb", "der")
        if case.connection_type == "bseep_8es"
        else case.geometry.pb_vgder or case.geometry.pb
    )

    g_izq: Quantity | None = None
    db_izq: Quantity | None = None
    bp_izq: Quantity | None = None
    de_izq: Quantity | None = None
    pfo_izq: Quantity | None = None
    pfi_izq: Quantity | None = None
    tp_izq: Quantity | None = None
    ts_izq: Quantity | None = None
    pb_izq: Quantity | None = None
    if beam_connection_sides == "both_sides":
        g_izq = _get_geometry_by_side("bolt_gage", "izq", require_explicit_for_both_sides=True)
        db_izq = _get_geometry_by_side("bolt_diameter", "izq", require_explicit_for_both_sides=True)
        bp_izq = _get_geometry_by_side("end_plate_width", "izq", require_explicit_for_both_sides=True)
        de_izq = _get_geometry_by_side("de", "izq", require_explicit_for_both_sides=True)
        pfo_izq = _get_geometry_by_side("pfo", "izq", require_explicit_for_both_sides=True)
        pfi_izq = _get_geometry_by_side("pfi", "izq", require_explicit_for_both_sides=True)
        tp_izq = _get_geometry_by_side("end_plate_thickness", "izq", require_explicit_for_both_sides=True)
        ts_izq = case.geometry.stiffener_thickness_vgizq or case.geometry.stiffener_thickness
        pb_izq = (
            _get_geometry_by_side("pb", "izq", require_explicit_for_both_sides=True)
            if case.connection_type == "bseep_8es"
            else case.geometry.pb_vgizq or case.geometry.pb
        )

    # Keep legacy aliases for non-side-specific checks and reporting fields.
    g = g_der
    db = db_der
    bp = bp_der
    de = de_der
    pfo = pfo_der
    pfi = pfi_der
    tp = tp_der
    pb = pb_der
    bolt_tightening_type = _get_geometry_by_side("bolt_tightening_type", "der")
    bolt_fabrication_standard = _get_material_by_side("bolt_fabrication_standard", "der")
    continuity_plate_enabled_raw = case.geometry.continuity_plate_enabled
    if continuity_plate_enabled_raw is None:
        continuity_plate_enabled = any(
            x is not None
            for x in (
                case.geometry.continuity_plate_thickness,
                case.geometry.continuity_plate_width_b1,
                case.geometry.continuity_plate_weld_type_col,
                case.geometry.continuity_plate_weld_type,
                case.geometry.continuity_plate_web_weld_type_col,
            )
        )
    else:
        continuity_plate_enabled = bool(continuity_plate_enabled_raw)

    doubler_plate_enabled_raw = case.geometry.doubler_plate_enabled
    if doubler_plate_enabled_raw is None:
        doubler_plate_enabled = any(
            x is not None
            for x in (
                case.geometry.doubler_plate_thickness,
                case.geometry.doubler_plate_web_plug_weld_type,
                case.geometry.tipo_w8_col,
            )
        )
    else:
        doubler_plate_enabled = bool(doubler_plate_enabled_raw)
    tcp = (
        _require(case, "geometry.continuity_plate_thickness", rule_binding)
        if continuity_plate_enabled
        else case.geometry.continuity_plate_thickness
    )
    continuity_plate_weld_type_raw = (
        case.geometry.continuity_plate_weld_type_col
        or case.geometry.continuity_plate_weld_type
    )
    continuity_plate_web_weld_type_raw = case.geometry.continuity_plate_web_weld_type_col
    w_w5_col = case.geometry.w_w5_col or case.geometry.t_w5_col
    nl_w5_col = case.geometry.nl_w5_col
    l_gap_w5_col = case.geometry.L_gap_w5_col
    kds_w5_col = case.geometry.kds_w5_col
    w_w6_col = case.geometry.w_w6_col or case.geometry.t_w6_col
    nl_w6_col = case.geometry.nl_w6_col
    l_gap_w6_col = case.geometry.L_gap_w6_col
    kds_w6_col = case.geometry.kds_w6_col
    weld_7_type_raw = case.geometry.doubler_plate_web_plug_weld_type
    weld7_type_norm = _normalize_end_plate_stiffener_weld_type(weld_7_type_raw)
    w_w7_col = case.geometry.w_w7_col or case.geometry.doubler_plate_web_plug_weld_size
    d_hole_w7_col = case.geometry.d_hole_w7_col
    weld_8_type_raw = case.geometry.tipo_w8_col
    w_w8_col = case.geometry.w_w8_col or case.geometry.t_w8_col
    nl_w8_col = case.geometry.nl_w8_col
    l_gap_w8_col = case.geometry.L_gap_w8_col
    kds_w8_col = case.geometry.kds_w8_col
    weld_9_type_raw = case.geometry.tipo_w9_col
    w_w9_col = case.geometry.w_w9_col or case.geometry.t_w9_col
    nl_w9_col = case.geometry.nl_w9_col
    l_gap_w9_col = case.geometry.L_gap_w9_col
    kds_w9_col = case.geometry.kds_w9_col
    gap_dp_col = case.geometry.gap_dp_col
    use_weld_7_col = case.geometry.use_weld_7_col
    use_weld_9_col = case.geometry.use_weld_9_col
    end_plate_beam_web_weld_type_raw = case.geometry.end_plate_beam_web_weld_type
    weld_fexx = _require(case, "materials.weld_fexx", rule_binding)
    beam_clear_span_length = _require(case, "geometry.beam_clear_span_length", rule_binding)
    shear_connector_free_length = _require(case, "geometry.beam_shear_connector_free_length_from_column_face", rule_binding)
    beam_clear_span_length_der, _ = _require_geometry_by_side(
        case,
        base_field="beam_clear_span_length",
        side="der",
        rule_binding=rule_binding,
    )
    shear_connector_free_length_der, _ = _require_geometry_by_side(
        case,
        base_field="beam_shear_connector_free_length_from_column_face",
        side="der",
        rule_binding=rule_binding,
    )
    beam_clear_span_length_izq: Quantity | None = None
    shear_connector_free_length_izq: Quantity | None = None
    if beam_connection_sides == "both_sides":
        beam_clear_span_length_izq, _ = _require_geometry_by_side(
            case,
            base_field="beam_clear_span_length",
            side="izq",
            rule_binding=rule_binding,
        )
        shear_connector_free_length_izq, _ = _require_geometry_by_side(
            case,
            base_field="beam_shear_connector_free_length_from_column_face",
            side="izq",
            rule_binding=rule_binding,
        )
    slab_connection_condition = _require(case, "geometry.column_slab_connection_condition", rule_binding)
    stc = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)
    beam_profile = _beam_profile(case)
    beam_profile_der = _beam_profile_by_side(case, "der")
    beam_profile_izq = _beam_profile_by_side(case, "izq") if beam_connection_sides == "both_sides" else None
    column_profile = _column_profile(case)
    bf = beam_profile["bf"]
    bcf = column_profile["bf"]
    beam_depth = beam_profile["d"]
    column_ductility = _require(case, "design_factors.member_ductility_demand_column", rule_binding)
    beam_ductility = column_ductility
    ry = _require(case, "design_factors.ry", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    beam_fy = _require(case, "materials.beam_fy", rule_binding)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    pu_beam = _require(case, "loads.pu_viga", rule_binding)
    pu_column = _require(case, "loads.pu_columna", rule_binding)
    beam_ag = _profile_ag(beam_profile, role="beam", rule_binding=rule_binding)
    column_ag = _profile_ag(column_profile, role="column", rule_binding=rule_binding)
    stiffener_height_der = _derive_stiffener_height_from_de_pfo(de=de_der, pfo=pfo_der, pb=pb_der)
    stiffener_height_izq = (
        _derive_stiffener_height_from_de_pfo(de=de_izq, pfo=pfo_izq, pb=pb_izq)
        if (de_izq is not None and pfo_izq is not None)
        else None
    )
    stiffener_height = stiffener_height_der
    pb_for_hpe_der = pb_der if case.connection_type == "bseep_8es" else None
    pb_for_hpe_izq = pb_izq if case.connection_type == "bseep_8es" else None
    end_plate_height_der = _derive_end_plate_height(
        beam_depth=beam_profile_der["d"],
        de=de_der,
        pfo=pfo_der,
        pb=pb_for_hpe_der,
    )
    end_plate_height_izq = (
        _derive_end_plate_height(
            beam_depth=beam_profile_izq["d"],
            de=de_izq,
            pfo=pfo_izq,
            pb=pb_for_hpe_izq,
        )
        if beam_profile_izq is not None and de_izq is not None and pfo_izq is not None
        else None
    )
    end_plate_height = end_plate_height_der
    stiffener_length_derived_der = _derive_stiffener_length_from_hst(
        stiffener_height=stiffener_height_der,
        unit_system=case.units_system,
    )
    stiffener_length_derived_izq = (
        _derive_stiffener_length_from_hst(
            stiffener_height=stiffener_height_izq,
            unit_system=case.units_system,
        )
        if stiffener_height_izq is not None
        else None
    )
    stiffener_length_derived = stiffener_length_derived_der

    h_terms_der = compute_end_plate_yield_line_h_terms(
        connection_type=case.connection_type,
        beam_depth=beam_profile_der["d"],
        beam_flange_thickness=beam_profile_der["tf"],
        pfo=pfo_der,
        pfi=pfi_der,
        pb=pb_der,
        unit_system=case.units_system,
    )
    h_terms_izq = (
        compute_end_plate_yield_line_h_terms(
            connection_type=case.connection_type,
            beam_depth=beam_profile_izq["d"],
            beam_flange_thickness=beam_profile_izq["tf"],
            pfo=pfo_izq,
            pfi=pfi_izq,
            pb=pb_izq,
            unit_system=case.units_system,
        )
        if beam_profile_izq is not None and pfo_izq is not None and pfi_izq is not None and de_izq is not None
        else None
    )

    h1 = h_terms_der["h1"]
    h2 = h_terms_der["h2"]
    h3 = h_terms_der["h3"]
    h4 = h_terms_der["h4"]
    ca_beam, ca_beam_trace = _compute_compactness_ca(
        pu=pu_beam,
        ry=ry,
        ag=beam_ag,
        fy=beam_fy,
        role="beam",
        unit_system=case.units_system,
    )
    ca_column, ca_column_trace = _compute_compactness_ca(
        pu=pu_column,
        ry=ry,
        ag=column_ag,
        fy=column_fy,
        role="column",
        unit_system=case.units_system,
    )

    min_spacing_der = compute_minimum_bolt_spacing(
        bolt_diameter=db_der,
        unit_system=case.units_system,
    )
    min_spacing_izq = (
        compute_minimum_bolt_spacing(
            bolt_diameter=db_izq,
            unit_system=case.units_system,
        )
        if db_izq is not None
        else None
    )
    bp_margin = 1.0 if case.units_system.value == "US" else 25.0
    bp_margin_mm = bp_margin * 25.4 if case.units_system.value == "US" else bp_margin
    bp_margin_mm_label = f"{bp_margin_mm:.3f} mm" if case.units_system.value == "US" else f"{bp_margin_mm:.0f} mm"
    min_bp = Quantity(value=bf.value + bp_margin, unit=bf.unit)
    min_edge_der, edge_intermediate_der = compute_minimum_edge_distance_standard_hole(
        bolt_diameter=db_der,
        unit_system=case.units_system,
    )
    min_edge_izq, edge_intermediate_izq = (
        compute_minimum_edge_distance_standard_hole(
            bolt_diameter=db_izq,
            unit_system=case.units_system,
        )
        if db_izq is not None
        else (None, None)
    )
    standard_hole_diameter_der, _ = _compute_standard_hole_diameter(
        bolt_diameter=db_der,
        unit_system=case.units_system,
    )
    standard_hole_diameter_izq, _ = (
        _compute_standard_hole_diameter(
            bolt_diameter=db_izq,
            unit_system=case.units_system,
        )
        if db_izq is not None
        else (None, None)
    )

    def _table61_length(*, us_in: float, si_mm: float) -> Quantity:
        if case.units_system.value == "US":
            return Quantity(value=us_in, unit="in")
        # Use exact in->mm conversion to avoid rounding mismatches between paired unit columns.
        return Quantity(value=us_in * 25.4, unit="mm")

    def _step1_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        calculated_symbol: str,
        limit_symbol: str,
        calculated: Quantity,
        limit: Quantity,
        comparison: str,
    ) -> dict[str, Any]:
        if comparison == "ge":
            passes = calculated.value >= limit.value
            margin_value = calculated.value - limit.value
            comparison_text = ">="
        elif comparison == "le":
            passes = calculated.value <= limit.value
            margin_value = limit.value - calculated.value
            comparison_text = "<="
        else:
            raise ValueError("comparison must be 'ge' or 'le'.")

        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        return {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": calculated_symbol,
            "limit_symbol": limit_symbol,
            "calculated": calculated.model_dump(),
            "limit": limit.model_dump(),
            "comparison": comparison,
            "comparison_text": comparison_text,
            "margin": Quantity(value=margin_value, unit=calculated.unit).model_dump(),
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }

    def _step1_range_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        symbol: str,
        calculated: Quantity,
        minimum: Quantity,
        maximum: Quantity,
    ) -> dict[str, Any]:
        eps = 1e-9
        passes = (calculated.value >= (minimum.value - eps)) and (calculated.value <= (maximum.value + eps))
        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        margin_to_min = calculated.value - minimum.value
        margin_to_max = maximum.value - calculated.value
        if abs(margin_to_min) <= eps:
            margin_to_min = 0.0
        if abs(margin_to_max) <= eps:
            margin_to_max = 0.0
        return {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": symbol,
            "limit_symbol": f"[{symbol}_min, {symbol}_max]",
            "calculated": calculated.model_dump(),
            "minimum": minimum.model_dump(),
            "maximum": maximum.model_dump(),
            "comparison": "range",
            "comparison_text": "in",
            "margin_to_min": Quantity(value=margin_to_min, unit=calculated.unit).model_dump(),
            "margin_to_max": Quantity(value=margin_to_max, unit=calculated.unit).model_dump(),
            "margin": Quantity(value=min(margin_to_min, margin_to_max), unit=calculated.unit).model_dump(),
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }

    def _step1_compound_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        calculated_symbol: str,
        verification_text: str,
        passes: bool,
        calculated: Quantity,
        limit_3db: Quantity | None = None,
        minimum: Quantity | None = None,
        maximum: Quantity | None = None,
    ) -> dict[str, Any]:
        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        payload: dict[str, Any] = {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": calculated_symbol,
            "limit_symbol": "compound",
            "comparison": "compound",
            "comparison_text": "compound",
            "verification_text": verification_text,
            "calculated": calculated.model_dump(),
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }
        if limit_3db is not None:
            payload["limit_3db"] = limit_3db.model_dump()
        if minimum is not None:
            payload["minimum"] = minimum.model_dump()
        if maximum is not None:
            payload["maximum"] = maximum.model_dump()
        return payload

    def _step1_text_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        calculated_symbol: str,
        limit_symbol: str,
        calculated_text: str,
        expected_text: str,
    ) -> dict[str, Any]:
        normalized_calc = calculated_text.strip().lower()
        normalized_exp = expected_text.strip().lower()
        passes = normalized_calc == normalized_exp
        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        return {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": calculated_symbol,
            "limit_symbol": limit_symbol,
            "comparison": "equals",
            "comparison_text": "==",
            "calculated_text": calculated_text,
            "expected_text": expected_text,
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }

    def _step1_text_in_set_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        calculated_symbol: str,
        limit_symbol: str,
        calculated_text: str,
        allowed_values: tuple[str, ...],
        normalizer: Callable[[str], str] | None = None,
    ) -> dict[str, Any]:
        normalized_calc = normalizer(calculated_text) if normalizer is not None else calculated_text.strip().lower()
        normalized_allowed = (
            {normalizer(item) for item in allowed_values}
            if normalizer is not None
            else {item.strip().lower() for item in allowed_values}
        )
        passes = normalized_calc in normalized_allowed
        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        return {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": calculated_symbol,
            "limit_symbol": limit_symbol,
            "comparison": "in_set",
            "comparison_text": "in",
            "calculated_text": calculated_text,
            "allowed_values": list(allowed_values),
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }

    def _step1_verification_only_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        calculated_symbol: str,
        verification_text: str,
        passes: bool,
    ) -> dict[str, Any]:
        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        return {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": calculated_symbol,
            "limit_symbol": "verification_only",
            "comparison": "compound",
            "comparison_text": "compound",
            "verification_text": verification_text,
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }

    def _step1_shape_family_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        calculated_symbol: str,
        limit_symbol: str,
        shape_text: str,
        allowed_families: tuple[str, ...],
    ) -> dict[str, Any]:
        normalized = shape_text.strip().upper()
        passes = any(normalized.startswith(prefix) for prefix in allowed_families)
        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        return {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": calculated_symbol,
            "limit_symbol": limit_symbol,
            "comparison": "family_in",
            "comparison_text": "in",
            "calculated_text": shape_text,
            "allowed_families": list(allowed_families),
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }

    def _normalize_bolt_tightening(raw: str | None) -> str:
        if raw is None:
            return "not_provided"
        normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
        if not normalized:
            return "not_provided"
        if normalized in {"pretensioned", "pretensionado", "pretensado", "apriete_pretensionado"}:
            return "pretensioned"
        if normalized in {"snug_tight", "snugtight", "apriete_justo"}:
            return "snug_tight"
        return normalized

    def _normalize_bolt_standard(raw: str) -> str:
        return "".join(ch for ch in raw.upper() if ch.isalnum())

    def _normalize_continuity_plate_weld_type(raw: str | None) -> str:
        if raw is None:
            return "not_provided"
        normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
        if not normalized:
            return "not_provided"
        if normalized in {
            "fillet",
            "double_sided_fillet",
            "double_fillet",
            "fillet_double_sided",
            "single_sided_fillet",
            "single_fillet",
            "fillet_single_sided",
            "filete",
            "filete_doble_cara",
            "filete_simple_cara",
        }:
            return "fillet"
        if normalized in {"double_sided_fillet", "double_fillet", "fillet_double_sided", "filete_doble_cara"}:
            return "double_sided_fillet"
        if normalized in {"cjp", "complete_joint_penetration"}:
            return "cjp"
        if normalized in {"pjp", "partial_joint_penetration"}:
            return "pjp"
        return normalized

    def _normalize_end_plate_beam_web_weld_type(raw: str | None) -> str:
        if raw is None:
            return "not_provided"
        normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
        if not normalized:
            return "not_provided"
        if normalized in {"cjp", "complete_joint_penetration"}:
            return "cjp"
        if normalized in {"double_sided_fillet", "double_fillet", "fillet_double_sided"}:
            return "double_sided_fillet"
        if normalized in {"single_sided_fillet", "single_fillet", "fillet_single_sided", "single_sided_fille"}:
            return "single_sided_fillet"
        return normalized

    def _step1_continuity_plate_weld_limit(
        *,
        check_id: str,
        scope: str,
        clause: str,
        description: str,
        continuity_plate_thickness: Quantity,
        weld_size: Quantity | None,
        weld_type_raw: str | None,
    ) -> dict[str, Any]:
        weld_type = _normalize_continuity_plate_weld_type(weld_type_raw)
        allowed_values = ["fillet", "cjp"]
        required_size = Quantity(
            value=0.75 * continuity_plate_thickness.value,
            unit=continuity_plate_thickness.unit,
        )
        condition_applies = weld_type == "fillet"
        weld_size_same_unit: Quantity | None = None
        if weld_size is not None:
            if weld_size.unit == continuity_plate_thickness.unit:
                weld_size_same_unit = weld_size
            elif weld_size.unit == "in" and continuity_plate_thickness.unit == "mm":
                weld_size_same_unit = Quantity(value=weld_size.value * 25.4, unit="mm")
            elif weld_size.unit == "mm" and continuity_plate_thickness.unit == "in":
                weld_size_same_unit = Quantity(value=weld_size.value / 25.4, unit="in")
        if weld_type == "cjp":
            passes = True
            governing_condition = "cjp_always_permitted"
        elif weld_type == "fillet":
            if weld_size_same_unit is None:
                passes = False
                governing_condition = "fillet_requires_size_input"
            else:
                passes = weld_size_same_unit.value >= (required_size.value - 1e-9)
                governing_condition = "fillet_requires_minimum_size_075_tcp"
        else:
            passes = False
            governing_condition = "weld_type_not_permitted"
        status = CheckStatus.PASS if passes else CheckStatus.FAIL
        return {
            "step": "1",
            "id": check_id,
            "scope": scope,
            "clause": clause,
            "description": description,
            "calculated_symbol": "tipo_w5_col",
            "limit_symbol": "{fillet, cjp}; si fillet => w_w5_col >= 0.75*t_pc_col",
            "comparison": "conditional_allowed_set",
            "comparison_text": "in_if",
            "thickness": continuity_plate_thickness.model_dump(),
            "weld_size": weld_size_same_unit.model_dump() if weld_size_same_unit is not None else None,
            "required_weld_size": required_size.model_dump(),
            "condition_applies": condition_applies,
            "governing_condition": governing_condition,
            "calculated_text": weld_type,
            "allowed_values": allowed_values,
            "status": status.value,
            "result": "OK" if passes else "NO_OK",
        }

    allowed_shape_families = ("W", "HEA", "HEB", "IPE")

    stiffener_length_for_pz = None if case.connection_type == "bueep_4e" else case.geometry.stiffener_length
    beam_profile_der = _beam_profile_by_side(case, "der")
    pz_der = _compute_protected_zone_length(
        lst=stiffener_length_for_pz,
        d=beam_profile_der["d"],
        bf=beam_profile_der["bf"],
    )
    pz_izq = None
    if case.design_factors.beam_connection_sides == "both_sides":
        beam_profile_izq = _beam_profile_by_side(case, "izq")
        pz_izq = _compute_protected_zone_length(
            lst=stiffener_length_for_pz,
            d=beam_profile_izq["d"],
            bf=beam_profile_izq["bf"],
        )
    if stiffener_length_for_pz is None:
        pz_formula = (
            "Lpz_vgder = min(d_vgder, 3*bf_vgder); "
            "Lpz_vgizq = min(d_vgizq, 3*bf_vgizq)"
        )
    else:
        pz_formula = (
            "Lpz_vgder = min(L_pest_vgder + 0.5*d_vgder, 3*bf_vgder); "
            "Lpz_vgizq = min(L_pest_vgizq + 0.5*d_vgizq, 3*bf_vgizq)"
        )
    step_1_notes = [
        {
            "step": "1",
            "id": "section_2_3_4.protected_zone_length",
            "scope": "beam",
            "clause": "Section 2.3.4 (8)",
            "description": "Protected zone length measured from column face",
            "beam_connection_sides": case.design_factors.beam_connection_sides,
            "formula": pz_formula,
            "protected_zone_length": pz_der["lpz"].model_dump(),
            "protected_zone_length_vgder": pz_der["lpz"].model_dump(),
            "protected_zone_length_vgizq": (
                pz_izq["lpz"].model_dump() if isinstance(pz_izq, dict) else None
            ),
        },
        {
            "step": "1",
            "id": "section_6_3.end_plate_connection_location",
            "scope": "column",
            "clause": "Section 6.3 (2)",
            "description": "End-plate connection location on column",
            "requirement": "La placa de extremo debe conectarse al ala de la columna.",
        },
        {
            "step": "1",
            "id": "section_6_3.end_plate_height_derived",
            "scope": "end_plate_der",
            "clause": "Section 6.3",
            "description": "Altura derivada de placa de extremo",
            "formula": (
                "Hpe_vgder = d_vgder + 2*pfo_pe_vgder + 2*de_pe_vgder + 2*pb_pe_vgder"
                if case.connection_type == "bseep_8es"
                else "Hpe_vgder = d_vgder + 2*pfo_pe_vgder + 2*de_pe_vgder"
            ),
            "hpe_vgder": end_plate_height_der.model_dump(),
        },
        {
            "step": "1",
            "id": "section_6_3.end_plate_geometry_vgder_note",
            "scope": "end_plate_der",
            "clause": "Section 6.3 + AISC 360-22 Table J3.3",
            "description": "Geometria end-plate de viga a derecha",
            "requirement": (
                "h1_vgder, h2_vgder, h3_vgder, h4_vgder y dh_vgder para trazabilidad geometrica"
                if case.connection_type == "bseep_8es"
                else "h1_vgder, h2_vgder y dh_vgder para trazabilidad geometrica"
            ),
            "formula": (
                (
                    "h1=d-0.5tf+pfo+pb; h2=d-0.5tf+pfo; h3=d-1.5tf-pfi; h4=d-1.5tf-pfi-pb; "
                    if case.connection_type == "bseep_8es"
                    else "h1=d-0.5tf+pfo; h2=d-1.5tf-pfi; "
                )
                + "dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in"
            ),
            "h1_vgder": h_terms_der["h1"].model_dump(),
            "h2_vgder": h_terms_der["h2"].model_dump(),
            "h3_vgder": h_terms_der["h3"].model_dump() if h_terms_der["h3"] is not None else None,
            "h4_vgder": h_terms_der["h4"].model_dump() if h_terms_der["h4"] is not None else None,
            "dh_vgder": standard_hole_diameter_der.model_dump(),
        },
        {
            "step": "1",
            "id": "section_6_3.end_plate_stiffener_geometry_note",
            "scope": "end_plate_stiffener_der",
            "clause": "Section 6.3",
            "description": "Derived end-plate stiffener geometry and detailing edge requirement",
            "formula": (
                (
                    "h_pest_vgder = pfo_pe_vgder + pb_pe_vgder + de_pe_vgder; "
                    if case.connection_type == "bseep_8es"
                    else "h_pest_vgder = pfo_pe_vgder + de_pe_vgder; "
                )
                + 
                "L_pest_vgder = h_pest_vgder/tan(30 deg); "
                "Ed_pest_vgder = 25 mm"
            ),
            "h_pest_vgder": stiffener_height_der.model_dump(),
            "l_pest_vgder": stiffener_length_derived_der.model_dump(),
            "ed_pest_vgder": Quantity(
                value=25.0 if case.units_system == UnitSystem.SI else (25.0 / 25.4),
                unit="mm" if case.units_system == UnitSystem.SI else "in",
            ).model_dump(),
        },
        {
            "step": "1",
            "id": "section_6_7.stiffened_end_plate_weld_sequence_note",
            "scope": "welds",
            "clause": "Section 6.7",
            "description": "Secuencia de soldadura para conexiones end-plate rigidizadas",
            "requirement": (
                "Para conexiones end-plate rigidizadas, la soldadura entre el ala de la viga y la placa "
                "de extremo debe ejecutarse antes de instalar el rigidizador."
            ),
        },
        {
            "step": "1",
            "id": "section_6_7.flange_root_backing_exception_note",
            "scope": "welds",
            "clause": "Section 6.7",
            "description": "Excepcion de respaldo en la raiz cerca del alma de la viga",
            "requirement": (
                "No se requiere respaldo en la raiz del ala, directamente por encima y por debajo "
                "del alma de la viga, en una longitud igual a 1.5k1. En esa ubicacion se permite "
                "una soldadura de ranura PJP de profundidad completa."
            ),
        },
    ]
    for side_tag in _active_beam_sides(case):
        side_scope = f"bolts_{side_tag}"
        side_label = "right beam" if side_tag == "der" else "left beam"
        step_1_notes.extend(
            [
                {
                    "step": "1",
                    "id": f"section_4_2.installation_requirements_{side_tag}",
                    "scope": side_scope,
                    "clause": "Section 4.2",
                    "description": f"Installation requirements for bolted assemblies ({side_label})",
                    "requirement": (
                        "Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la "
                        "especificacion RCSC, salvo que este estandar indique lo contrario."
                    ),
                },
                {
                    "step": "1",
                    "id": f"section_4_3.quality_control_assurance_{side_tag}",
                    "scope": side_scope,
                    "clause": "Section 4.3",
                    "description": f"Quality control and quality assurance for bolted assemblies ({side_label})",
                    "requirement": (
                        "El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions."
                    ),
                },
            ]
        )
    if case.design_factors.beam_connection_sides == "both_sides":
        step_1_notes.insert(
            4,
            {
                "step": "1",
                "id": "section_6_3.end_plate_geometry_vgizq_note",
                "scope": "end_plate_izq",
                "clause": "Section 6.3 + AISC 360-22 Table J3.3",
                "description": "Geometria end-plate de viga a izquierda",
                "requirement": (
                    "h1_vgizq, h2_vgizq, h3_vgizq, h4_vgizq y dh_vgizq para trazabilidad geometrica"
                    if case.connection_type == "bseep_8es"
                    else "h1_vgizq, h2_vgizq y dh_vgizq para trazabilidad geometrica"
                ),
                "formula": (
                    (
                        "h1=d-0.5tf+pfo+pb; h2=d-0.5tf+pfo; h3=d-1.5tf-pfi; h4=d-1.5tf-pfi-pb; "
                        if case.connection_type == "bseep_8es"
                        else "h1=d-0.5tf+pfo; h2=d-1.5tf-pfi; "
                    )
                    + "dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in"
                ),
                "h1_vgizq": h_terms_izq["h1"].model_dump() if h_terms_izq is not None else None,
                "h2_vgizq": h_terms_izq["h2"].model_dump() if h_terms_izq is not None else None,
                "h3_vgizq": (
                    h_terms_izq["h3"].model_dump()
                    if h_terms_izq is not None and h_terms_izq["h3"] is not None
                    else None
                ),
                "h4_vgizq": (
                    h_terms_izq["h4"].model_dump()
                    if h_terms_izq is not None and h_terms_izq["h4"] is not None
                    else None
                ),
                "dh_vgizq": (
                    standard_hole_diameter_izq.model_dump()
                    if standard_hole_diameter_izq is not None
                    else standard_hole_diameter_der.model_dump()
                ),
            },
        )
        step_1_notes.insert(
            4,
            {
                "step": "1",
                "id": "section_6_3.end_plate_height_derived_izq",
                "scope": "end_plate_izq",
                "clause": "Section 6.3",
                "description": "Altura derivada de placa de extremo",
                "formula": (
                    "Hpe_vgizq = d_vgizq + 2*pfo_pe_vgizq + 2*de_pe_vgizq + 2*pb_pe_vgizq"
                    if case.connection_type == "bseep_8es"
                    else "Hpe_vgizq = d_vgizq + 2*pfo_pe_vgizq + 2*de_pe_vgizq"
                ),
                "hpe_vgizq": end_plate_height_izq.model_dump(),
            },
        )
        step_1_notes.insert(
            7,
            {
                "step": "1",
                "id": "section_6_3.end_plate_stiffener_geometry_vgizq_note",
                "scope": "end_plate_stiffener_izq",
                "clause": "Section 6.3",
                "description": "Derived end-plate stiffener geometry and detailing edge requirement",
                "formula": (
                    (
                        "h_pest_vgizq = pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq; "
                        if case.connection_type == "bseep_8es"
                        else "h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; "
                    )
                    +
                    "L_pest_vgizq = h_pest_vgizq/tan(30 deg); "
                    "Ed_pest_vgizq = 25 mm"
                ),
                "h_pest_vgizq": stiffener_height_izq.model_dump() if stiffener_height_izq is not None else None,
                "l_pest_vgizq": (
                    stiffener_length_derived_izq.model_dump() if stiffener_length_derived_izq is not None else None
                ),
                "ed_pest_vgizq": Quantity(
                    value=25.0 if case.units_system == UnitSystem.SI else (25.0 / 25.4),
                    unit="mm" if case.units_system == UnitSystem.SI else "in",
                ).model_dump(),
            },
        )

    span_to_depth_limit = 7.0 if beam_ductility == "high" else 5.0
    frame_system = "SMF" if beam_ductility == "high" else "IMF"
    clear_span_to_depth_ratio_der = Quantity(
        value=beam_clear_span_length_der.value / beam_profile_der["d"].value,
        unit="ratio",
    )
    clear_span_to_depth_ratio_izq = (
        Quantity(
            value=beam_clear_span_length_izq.value / beam_profile_izq["d"].value,
            unit="ratio",
        )
        if (beam_clear_span_length_izq is not None and beam_profile_izq is not None)
        else None
    )
    beam_flange_ratio_der = compute_flange_slenderness_ratio(
        flange_width=beam_profile_der["bf"],
        flange_thickness=beam_profile_der["tf"],
        unit_system=case.units_system,
    )
    beam_flange_ratio_izq = (
        compute_flange_slenderness_ratio(
            flange_width=beam_profile_izq["bf"],
            flange_thickness=beam_profile_izq["tf"],
            unit_system=case.units_system,
        )
        if beam_profile_izq is not None
        else None
    )
    beam_web_ratio_der, _ = compute_web_slenderness_ratio(
        section_depth=beam_profile_der["d"],
        k_design=_profile_kdes(beam_profile_der, role="beam", rule_binding=rule_binding),
        web_thickness=beam_profile_der["tw"],
        unit_system=case.units_system,
    )
    beam_web_ratio_izq, _ = (
        compute_web_slenderness_ratio(
            section_depth=beam_profile_izq["d"],
            k_design=_profile_kdes(beam_profile_izq, role="beam", rule_binding=rule_binding),
            web_thickness=beam_profile_izq["tw"],
            unit_system=case.units_system,
        )
        if beam_profile_izq is not None
        else (None, None)
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
    column_flange_ratio = compute_flange_slenderness_ratio(
        flange_width=column_profile["bf"],
        flange_thickness=column_profile["tf"],
        unit_system=case.units_system,
    )
    column_web_ratio, _ = compute_web_slenderness_ratio(
        section_depth=column_profile["d"],
        k_design=_profile_kdes(column_profile, role="column", rule_binding=rule_binding),
        web_thickness=column_profile["tw"],
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

    active_table_61 = compute_limites_precalificacion_conexion_tipo_ep(
        connection_type=case.connection_type,
        unit_system=case.units_system,
    )
    stc_margin = Quantity(
        value=(12.5 / 25.4) if case.units_system == UnitSystem.US else 12.5,
        unit="in" if case.units_system == UnitSystem.US else "mm",
    )
    stc_min_izq: Quantity | None = None
    if case.connection_type == "bseep_8es":
        if pb_der is None:
            raise ValueError("geometry.pb_vgder is required for bseep_8es prequalification checks.")
        stc_min_der = compute_minimum_column_end_distance_to_beam_flange(
            pfo=pfo_der,
            de=de_der,
            pb=pb_der,
            margin=stc_margin,
            unit_system=case.units_system,
        )
        stc_limit_symbol = "pfo_pe_vgder + pb_pe_vgder + de_pe_vgder + 12.5 mm"
        if beam_connection_sides == "both_sides":
            if pb_izq is None or pfo_izq is None or de_izq is None:
                raise ValueError("geometry.pb_vgizq, geometry.pfo_vgizq and geometry.de_vgizq are required for both_sides.")
            stc_min_izq = compute_minimum_column_end_distance_to_beam_flange(
                pfo=pfo_izq,
                de=de_izq,
                pb=pb_izq,
                margin=stc_margin,
                unit_system=case.units_system,
            )
    else:
        stc_min_der = compute_minimum_column_end_distance_to_beam_flange(
            pfo=pfo_der,
            de=de_der,
            pb=None,
            margin=stc_margin,
            unit_system=case.units_system,
        )
        stc_limit_symbol = "pfo_pe_vgder + de_pe_vgder + 12.5 mm"
        if beam_connection_sides == "both_sides":
            if pfo_izq is None or de_izq is None:
                raise ValueError("geometry.pfo_vgizq and geometry.de_vgizq are required for both_sides.")
            stc_min_izq = compute_minimum_column_end_distance_to_beam_flange(
                pfo=pfo_izq,
                de=de_izq,
                pb=None,
                margin=stc_margin,
                unit_system=case.units_system,
            )
    stc_min = stc_min_der
    if stc_min_izq is not None and stc_min_izq.value > stc_min.value:
        stc_min = stc_min_izq
    stc_check_payload: dict[str, Any] | None = None
    if beam_connection_sides == "both_sides":
        if case.connection_type == "bseep_8es":
            stc_verification_text = (
                "St_col >= pfo_pe_vgder + pb_pe_vgder + de_pe_vgder + 12.5 mm; "
                "St_col >= pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq + 12.5 mm; "
                f"{stc.value:.3f} {stc.unit} >= {stc_min_der.value:.3f} {stc.unit}; "
                f"{stc.value:.3f} {stc.unit} >= {stc_min_izq.value:.3f} {stc.unit}"
            )
        else:
            stc_verification_text = (
                "St_col >= pfo_pe_vgder + de_pe_vgder + 12.5 mm; "
                "St_col >= pfo_pe_vgizq + de_pe_vgizq + 12.5 mm; "
                f"{stc.value:.3f} {stc.unit} >= {stc_min_der.value:.3f} {stc.unit}; "
                f"{stc.value:.3f} {stc.unit} >= {stc_min_izq.value:.3f} {stc.unit}"
            )
        stc_check_payload = _step1_compound_limit(
            check_id="section_6_3_1.column_stc_minimum_requirement",
            scope="column",
            clause="Section 6.3.1 (column top clearance criterion)",
            description="Proyeccion de columna minima por encima de las vigas",
            calculated_symbol="St_col",
            verification_text=stc_verification_text,
            passes=(stc.value >= stc_min_der.value) and (stc_min_izq is None or stc.value >= stc_min_izq.value),
            calculated=stc,
            minimum=stc_min,
        )
    s_threshold_der = compute_column_beam_clearance_threshold(
        column_flange_width=bcf,
        bolt_gage=g_der,
        unit_system=case.units_system,
    )
    s_threshold_izq = (
        compute_column_beam_clearance_threshold(
            column_flange_width=bcf,
            bolt_gage=g_izq,
            unit_system=case.units_system,
        )
        if g_izq is not None
        else None
    )
    if case.connection_type == "bseep_8es":
        if pb_der is None:
            raise ValueError("geometry.pb_vgder is required for bseep_8es prequalification checks.")
        sc_der = compute_column_beam_clearance_distance(
            column_end_distance_to_beam_flange=stc,
            pfo=pfo_der,
            pb=pb_der,
            unit_system=case.units_system,
        )
        sc_formula_der = "Sc_vgder = St_col - pfo_vgder - pb_vgder"
        sc_izq = (
            compute_column_beam_clearance_distance(
                column_end_distance_to_beam_flange=stc,
                pfo=pfo_izq,
                pb=pb_izq,
                unit_system=case.units_system,
            )
            if pfo_izq is not None and pb_izq is not None
            else None
        )
        sc_formula_izq = "Sc_vgizq = St_col - pfo_vgizq - pb_vgizq"
    else:
        sc_der = compute_column_beam_clearance_distance(
            column_end_distance_to_beam_flange=stc,
            pfo=pfo_der,
            pb=None,
            unit_system=case.units_system,
        )
        sc_formula_der = "Sc_vgder = St_col - pfo_vgder"
        sc_izq = (
            compute_column_beam_clearance_distance(
                column_end_distance_to_beam_flange=stc,
                pfo=pfo_izq,
                pb=None,
                unit_system=case.units_system,
            )
            if pfo_izq is not None
            else None
        )
        sc_formula_izq = "Sc_vgizq = St_col - pfo_vgizq"
    sc_pass_der = sc_der.value > s_threshold_der.value
    sc_pass_izq = (
        sc_izq.value > s_threshold_izq.value
        if sc_izq is not None and s_threshold_izq is not None
        else None
    )

    beam_shape_limits: list[dict[str, Any]] = []
    if beam_connection_sides == "both_sides":
        beam_shape_limits.append(
            _step1_shape_family_limit(
                check_id="beam_izq.shape_family",
                scope="beam_izq",
                clause="Section 2.3.4",
                description="Familia de perfil de viga permitida para precalificacion (viga izquierda)",
                calculated_symbol="perfil_vgizq",
                limit_symbol="{W, HEA, HEB, IPE}",
                shape_text=_beam_shape_by_side(case, "izq"),
                allowed_families=allowed_shape_families,
            )
        )
    beam_shape_limits.append(
        _step1_shape_family_limit(
            check_id="beam_der.shape_family",
            scope="beam_der",
            clause="Section 2.3.4",
            description="Familia de perfil de viga permitida para precalificacion (viga derecha)",
            calculated_symbol="perfil_vgder",
            limit_symbol="{W, HEA, HEB, IPE}",
            shape_text=_beam_shape_by_side(case, "der"),
            allowed_families=allowed_shape_families,
        )
    )

    beam_limits: list[dict[str, Any]] = []
    beam_limits.extend(beam_shape_limits)
    if beam_connection_sides == "both_sides" and beam_profile_izq is not None and clear_span_to_depth_ratio_izq is not None:
        beam_limits.extend(
            [
                _step1_limit(
                    check_id="beam_izq.bp_ge_bf_plus_margin",
                    scope="beam_izq",
                    clause="Section 6.3 / Table 6.1",
                    description="End-plate width vs beam flange width (left beam)",
                    calculated_symbol="bp_pe_vgizq",
                    limit_symbol=f"bf_vgizq + margin ({bp_margin_mm_label})",
                    calculated=bp_izq,
                    limit=Quantity(
                        value=beam_profile_izq["bf"].value + bp_margin,
                        unit=beam_profile_izq["bf"].unit,
                    ),
                    comparison="le",
                ),
                _step1_limit(
                    check_id="beam_izq.bolt_gage_g_ge_3db",
                    scope="end_plate_izq",
                    clause="Section 6.3 / Table 6.1",
                    description="Bolt gage minimum spacing (left beam)",
                    calculated_symbol="g_b_vgizq",
                    limit_symbol="3db",
                    calculated=g_izq,
                    limit=min_spacing_izq if min_spacing_izq is not None else min_spacing_der,
                    comparison="ge",
                ),
                _step1_limit(
                    check_id="section_2_3_4.no_shear_connectors_zone_izq",
                    scope="beam_izq",
                    clause="Section 2.3.4 (2)",
                    description="Length without shear connectors from column face (left beam)",
                    calculated_symbol="Lnc_vgizq",
                    limit_symbol="1.5d_vgizq",
                    calculated=shear_connector_free_length_izq,
                    limit=Quantity(value=1.5 * beam_profile_izq["d"].value, unit=beam_profile_izq["d"].unit),
                    comparison="ge",
                ),
                _step1_compound_limit(
                    check_id="section_6_3_1.beam_sc_greater_than_s_threshold_izq",
                    scope="beam_izq",
                    clause="Section 6.3.1 (beam clearance criterion)",
                    description="Beam clearance criterion using Sc and S threshold (left beam)",
                    calculated_symbol="Sc_vgizq",
                    verification_text=(
                        f"{sc_formula_izq}; S_vgizq = 0.5*sqrt(bcf*g_vgizq); "
                        f"Sc_vgizq > S_vgizq => {sc_izq.value:.3f} {sc_izq.unit} > "
                        f"{s_threshold_izq.value:.3f} {s_threshold_izq.unit}"
                    ),
                    passes=bool(sc_pass_izq),
                    calculated=sc_izq,
                ),
                _step1_limit(
                    check_id="section_2_3_4.clear_span_to_depth_ratio_izq",
                    scope="beam_izq",
                    clause="Section 2.3.4 (5)",
                    description="Clear span-to-depth ratio by frame system (left beam)",
                    calculated_symbol="Llb_vgizq/d_vgizq",
                    limit_symbol=f"{span_to_depth_limit:.0f} ({frame_system})",
                    calculated=clear_span_to_depth_ratio_izq,
                    limit=Quantity(value=span_to_depth_limit, unit="ratio"),
                    comparison="ge",
                ),
                _step1_limit(
                    check_id="section_2_3_4.beam_flange_width_to_thickness_izq",
                    scope="beam_izq",
                    clause="AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
                    description="Beam flange width-to-thickness compactness (left beam)",
                    calculated_symbol="lambda_f_vgizq",
                    limit_symbol="lambda_f_limit",
                    calculated=Quantity(value=beam_flange_ratio_izq, unit="ratio"),
                    limit=Quantity(value=beam_flange_limit, unit="ratio"),
                    comparison="le",
                ),
                _step1_limit(
                    check_id="section_2_3_4.beam_web_width_to_thickness_izq",
                    scope="beam_izq",
                    clause="AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
                    description="Beam web width-to-thickness compactness (left beam)",
                    calculated_symbol="lambda_w_vgizq",
                    limit_symbol="lambda_w_limit",
                    calculated=Quantity(value=beam_web_ratio_izq, unit="ratio"),
                    limit=Quantity(value=beam_web_limit, unit="ratio"),
                    comparison="le",
                ),
            ]
        )
    beam_limits.extend(
        [
            _step1_limit(
                check_id="beam_der.bp_ge_bf_plus_margin",
                scope="beam_der",
                clause="Section 6.3 / Table 6.1",
                description="End-plate width vs beam flange width (right beam)",
                calculated_symbol="bp_pe_vgder",
                limit_symbol=f"bf_vgder + margin ({bp_margin_mm_label})",
                calculated=bp_der,
                limit=Quantity(
                    value=beam_profile_der["bf"].value + bp_margin,
                    unit=beam_profile_der["bf"].unit,
                ),
                comparison="le",
            ),
            _step1_limit(
                check_id="beam_der.bolt_gage_g_ge_3db",
                scope="end_plate_der",
                clause="Section 6.3 / Table 6.1",
                description="Bolt gage minimum spacing (right beam)",
                calculated_symbol="g_b_vgder",
                limit_symbol="3db",
                calculated=g_der,
                limit=min_spacing_der,
                comparison="ge",
            ),
            _step1_limit(
                check_id="section_2_3_4.no_shear_connectors_zone_der",
                scope="beam_der",
                clause="Section 2.3.4 (2)",
                description="Length without shear connectors from column face (right beam)",
                calculated_symbol="Lnc_vgder",
                limit_symbol="1.5d_vgder",
                calculated=shear_connector_free_length_der,
                limit=Quantity(value=1.5 * beam_profile_der["d"].value, unit=beam_profile_der["d"].unit),
                comparison="ge",
            ),
            _step1_compound_limit(
                check_id="section_6_3_1.beam_sc_greater_than_s_threshold_der",
                scope="beam_der",
                clause="Section 6.3.1 (beam clearance criterion)",
                description="Beam clearance criterion using Sc and S threshold (right beam)",
                calculated_symbol="Sc_vgder",
                verification_text=(
                    f"{sc_formula_der}; S_vgder = 0.5*sqrt(bcf*g_vgder); "
                    f"Sc_vgder > S_vgder => {sc_der.value:.3f} {sc_der.unit} > "
                    f"{s_threshold_der.value:.3f} {s_threshold_der.unit}"
                ),
                passes=sc_pass_der,
                calculated=sc_der,
            ),
            _step1_limit(
                check_id="section_2_3_4.clear_span_to_depth_ratio_der",
                scope="beam_der",
                clause="Section 2.3.4 (5)",
                description="Clear span-to-depth ratio by frame system (right beam)",
                calculated_symbol="Llb_vgder/d_vgder",
                limit_symbol=f"{span_to_depth_limit:.0f} ({frame_system})",
                calculated=clear_span_to_depth_ratio_der,
                limit=Quantity(value=span_to_depth_limit, unit="ratio"),
                comparison="ge",
            ),
            _step1_limit(
                check_id="section_2_3_4.beam_flange_width_to_thickness_der",
                scope="beam_der",
                clause="AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
                description="Beam flange width-to-thickness compactness (right beam)",
                calculated_symbol="lambda_f_vgder",
                limit_symbol="lambda_f_limit",
                calculated=Quantity(value=beam_flange_ratio_der, unit="ratio"),
                limit=Quantity(value=beam_flange_limit, unit="ratio"),
                comparison="le",
            ),
            _step1_limit(
                check_id="section_2_3_4.beam_web_width_to_thickness_der",
                scope="beam_der",
                clause="AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
                description="Beam web width-to-thickness compactness (right beam)",
                calculated_symbol="lambda_w_vgder",
                limit_symbol="lambda_w_limit",
                calculated=Quantity(value=beam_web_ratio_der, unit="ratio"),
                limit=Quantity(value=beam_web_limit, unit="ratio"),
                comparison="le",
            ),
        ]
    )

    column_depth_max = Quantity(
        value=36.0 if case.units_system == UnitSystem.US else 920.0,
        unit="in" if case.units_system == UnitSystem.US else "mm",
    )
    column_limits = [
        _step1_shape_family_limit(
            check_id="column.shape_family",
            scope="column",
            clause="Section 2.3.4",
            description="Column profile family allowed for prequalification",
            calculated_symbol="shape_col",
            limit_symbol="{W, HEA, HEB, IPE}",
            shape_text=str(case.sections.column_shape),
            allowed_families=allowed_shape_families,
        ),
        _step1_limit(
            check_id="section_6_3.column_depth_maximum",
            scope="column",
            clause="Section 6.3 (3)",
            description="Column profile depth maximum (W36/W920)",
            calculated_symbol="d_col",
            limit_symbol="W36/W920",
            calculated=column_profile["d"],
            limit=column_depth_max,
            comparison="le",
        ),
        _step1_limit(
            check_id="column.bp_le_bcf",
            scope="column",
            clause="Section 6.3 / Table 6.1",
            description="End-plate fit within column flange width",
            calculated_symbol="bp",
            limit_symbol="bcf",
            calculated=bp,
            limit=bcf,
            comparison="le",
        ),
        _step1_text_limit(
            check_id="section_2_3_4.slab_isolation_condition",
            scope="column",
            clause="Section 2.3.4 (3)",
            description="Column-slab connection condition",
            calculated_symbol="col_losa",
            limit_symbol="isolated",
            calculated_text=str(slab_connection_condition),
            expected_text="isolated",
        ),
        (
            stc_check_payload
            if stc_check_payload is not None
            else _step1_limit(
                check_id="section_6_3_1.column_stc_minimum_requirement",
                scope="column",
                clause="Section 6.3.1 (column top clearance criterion)",
                description="Proyeccion de columna minima por encima de las vigas",
                calculated_symbol="St_col",
                limit_symbol=stc_limit_symbol,
                calculated=stc,
                limit=stc_min,
                comparison="ge",
            )
        ),
        _step1_limit(
            check_id="section_2_3_4.column_flange_width_to_thickness",
            scope="column",
            clause="AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
            description="Column flange width-to-thickness compactness",
            calculated_symbol="lambda_f_col",
            limit_symbol="lambda_f_limit",
            calculated=Quantity(value=column_flange_ratio, unit="ratio"),
            limit=Quantity(value=column_flange_limit, unit="ratio"),
            comparison="le",
        ),
        _step1_limit(
            check_id="section_2_3_4.column_web_width_to_thickness",
            scope="column",
            clause="AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
            description="Column web width-to-thickness compactness",
            calculated_symbol="lambda_w_col",
            limit_symbol="lambda_w_limit",
            calculated=Quantity(value=column_web_ratio, unit="ratio"),
            limit=Quantity(value=column_web_limit, unit="ratio"),
            comparison="le",
        ),
    ]

    doubler_plate_limits: list[dict[str, Any]] = []
    d_col_for_dz = column_profile["d"]
    tf_col_for_dz = column_profile["tf"]
    wz_candidates: list[Quantity] = []
    if beam_connection_sides in {"both_sides", "left_only"} and beam_profile_izq is not None:
        wz_candidates.append(
            Quantity(
                value=beam_profile_izq["d"].value - 2.0 * beam_profile_izq["tf"].value,
                unit=beam_profile_izq["d"].unit,
            )
        )
    if beam_connection_sides in {"both_sides", "right_only"}:
        wz_candidates.append(
            Quantity(
                value=beam_profile_der["d"].value - 2.0 * beam_profile_der["tf"].value,
                unit=beam_profile_der["d"].unit,
            )
        )

    def _to_unit_length_local(q: Quantity, target_unit: str) -> Quantity | None:
        if q.unit == target_unit:
            return q
        if q.unit == "mm" and target_unit == "in":
            return Quantity(value=q.value / 25.4, unit="in")
        if q.unit == "in" and target_unit == "mm":
            return Quantity(value=q.value * 25.4, unit="mm")
        return None

    h_dp_col: Quantity | None = None
    b_dp_col: Quantity | None = None
    h_dp_formula_tag = "n/a"
    b_dp_formula_tag = "n/a"
    h_dp_col_rounding_note = "none"

    d_candidates: list[Quantity] = []
    d_minus_tf_candidates: list[Quantity] = []
    if beam_connection_sides in {"both_sides", "right_only"}:
        d_der = beam_profile_der["d"]
        tf_der = beam_profile_der["tf"]
        d_candidates.append(d_der)
        d_minus_tf_candidates.append(Quantity(value=d_der.value - tf_der.value, unit=d_der.unit))
    if beam_connection_sides in {"both_sides", "left_only"} and beam_profile_izq is not None:
        d_izq = beam_profile_izq["d"]
        tf_izq = beam_profile_izq["tf"]
        d_candidates.append(d_izq)
        d_minus_tf_candidates.append(Quantity(value=d_izq.value - tf_izq.value, unit=d_izq.unit))

    if d_candidates:
        base_unit = d_candidates[0].unit
        d_converted: list[Quantity] = []
        for d_q in d_candidates:
            d_q_conv = _to_unit_length_local(d_q, base_unit)
            if d_q_conv is not None:
                d_converted.append(d_q_conv)
        plus_300_q = _to_unit_length_local(Quantity(value=300.0, unit="mm"), base_unit)
        extended_dp_col = case.geometry.extended_dp_col is True
        if (
            (not extended_dp_col and not continuity_plate_enabled)
            or (extended_dp_col and continuity_plate_enabled)
        ):
            if d_converted and plus_300_q is not None:
                d_max_q = max(d_converted, key=lambda x: x.value)
                h_dp_col = Quantity(value=d_max_q.value + plus_300_q.value, unit=base_unit)
                h_dp_formula_tag = "300 + max(d)"
        elif (not extended_dp_col) and continuity_plate_enabled:
            d_minus_tf_converted: list[Quantity] = []
            for dtf_q in d_minus_tf_candidates:
                dtf_q_conv = _to_unit_length_local(dtf_q, base_unit)
                if dtf_q_conv is not None:
                    d_minus_tf_converted.append(dtf_q_conv)
            t_pc_col_q = case.geometry.continuity_plate_thickness
            t_pc_col_conv = _to_unit_length_local(t_pc_col_q, base_unit) if t_pc_col_q is not None else None
            if d_minus_tf_converted and plus_300_q is not None and t_pc_col_conv is not None:
                d_minus_tf_max_q = max(d_minus_tf_converted, key=lambda x: x.value)
                h_dp_col = Quantity(
                    value=d_minus_tf_max_q.value + plus_300_q.value - t_pc_col_conv.value,
                    unit=base_unit,
                )
                h_dp_formula_tag = "300 + max(d-tf) - t_pc_col"

        if h_dp_col is not None and h_dp_col.unit == "mm":
            h_dp_col = Quantity(value=math.ceil(h_dp_col.value / 10.0) * 10.0, unit="mm")
            h_dp_col_rounding_note = "ceil_10mm"

    # b_dp_col depends on weld #8 type
    d_col_q = column_profile.get("d")
    kdet_col_q = column_profile.get("kdet") or column_profile.get("kdes")
    tft_col_q = column_profile.get("tfdet") or column_profile.get("tf")
    if d_col_q is not None:
        weld8_type_norm_local = _normalize_end_plate_stiffener_weld_type(case.geometry.tipo_w8_col)
        if weld8_type_norm_local in {"cjp", "pjp"} and kdet_col_q is not None:
            kdet_conv = _to_unit_length_local(kdet_col_q, d_col_q.unit)
            if kdet_conv is not None:
                b_dp_col = Quantity(value=d_col_q.value - 2.0 * kdet_conv.value, unit=d_col_q.unit)
                b_dp_formula_tag = "d_col - 2*kdet_col"
        elif weld8_type_norm_local == "fillet" and tft_col_q is not None:
            tft_conv = _to_unit_length_local(tft_col_q, d_col_q.unit)
            if tft_conv is not None:
                b_dp_col = Quantity(value=d_col_q.value - 2.0 * tft_conv.value, unit=d_col_q.unit)
                b_dp_formula_tag = "d_col - 2*tft_col"

    use_w7 = bool(use_weld_7_col)
    nfilas_w7_col_for_check = case.geometry.nfilas_w7_col or case.geometry.doubler_plate_web_plug_weld_lines_nl
    ncolumna_w7_col_for_check = case.geometry.ncolumna_w7_col
    dz_dp_col: Quantity | None = None
    wz_dp_col: Quantity | None = None
    h_w7_col: Quantity | None = None
    b_w7_col: Quantity | None = None
    if not use_w7:
        # use_weld_7_col = false:
        # wz_dp_col = d_col - 2*tf_col
        # dz_dp_col = max{d_lado - 2*tf_lado}
        wz_dp_col = Quantity(
            value=d_col_for_dz.value - 2.0 * tf_col_for_dz.value,
            unit=d_col_for_dz.unit,
        )
        if wz_candidates:
            converted: list[Quantity] = []
            for q in wz_candidates:
                q_conv = _to_unit_length_local(q, d_col_for_dz.unit)
                if q_conv is not None:
                    converted.append(q_conv)
            if converted:
                dz_dp_col = max(converted, key=lambda x: x.value)
    else:
        # use_weld_7_col = true:
        # dz_dp_col = max{d_lado - 2*tf_lado}/(nfilas_w7_col + 1)
        # wz_dp_col = b_dp_col/(ncolumna_w7_col + 1)
        nfilas_w7_col = case.geometry.nfilas_w7_col or case.geometry.doubler_plate_web_plug_weld_lines_nl
        ncolumna_w7_col = case.geometry.ncolumna_w7_col
        if b_dp_col is not None and nfilas_w7_col and ncolumna_w7_col and wz_candidates:
            converted: list[Quantity] = []
            for q in wz_candidates:
                q_conv = _to_unit_length_local(q, d_col_for_dz.unit)
                if q_conv is not None:
                    converted.append(q_conv)
            if converted:
                dz_governing = max(converted, key=lambda x: x.value)
                h_w7_col = Quantity(
                    value=dz_governing.value / float(nfilas_w7_col + 1),
                    unit=dz_governing.unit,
                )
                dz_dp_col = h_w7_col
            b_dp_for_wz = _to_unit_length_local(b_dp_col, d_col_for_dz.unit)
            if b_dp_for_wz is not None:
                b_w7_col = Quantity(
                    value=b_dp_for_wz.value / float(ncolumna_w7_col + 1),
                    unit=b_dp_for_wz.unit,
                )
                wz_dp_col = b_w7_col
        elif doubler_plate_enabled:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=[
                    "geometry.nfilas_w7_col",
                    "geometry.ncolumna_w7_col",
                ],
                message=(
                    "Unable to compute dz_dp_col/wz_dp_col when use_weld_7_col=true. "
                    "Require nfilas_w7_col, ncolumna_w7_col and active beam side data."
                ),
            )

    if use_w7 and doubler_plate_enabled:
        if nfilas_w7_col_for_check is not None and ncolumna_w7_col_for_check is not None:
            grid_product_q = Quantity(
                value=float(nfilas_w7_col_for_check) * float(ncolumna_w7_col_for_check),
                unit="adim",
            )
            doubler_plate_limits.append(
                _step1_limit(
                    check_id="section_e3_6e_2.weld_7_grid_minimum_col",
                    scope="weld_7_col",
                    clause="AISC 341-22w E3.6e.2",
                    description="Malla minima de soldadura #7",
                    calculated_symbol="(nfilas_w7_col)*(ncolumna_w7_col)",
                    limit_symbol="4",
                    calculated=grid_product_q,
                    limit=Quantity(value=4.0, unit="adim"),
                    comparison="ge",
                )
            )
        else:
            doubler_plate_limits.append(
                _step1_verification_only_limit(
                    check_id="section_e3_6e_2.weld_7_grid_minimum_col",
                    scope="weld_7_col",
                    clause="AISC 341-22w E3.6e.2",
                    description="Malla minima de soldadura #7",
                    calculated_symbol="(nfilas_w7_col)*(ncolumna_w7_col)",
                    verification_text=(
                        "Chequeo no evaluable por falta de datos: "
                        "nfilas_w7_col y/o ncolumna_w7_col"
                    ),
                    passes=False,
                )
            )

    t_req_e3_6 = (
        Quantity(value=(dz_dp_col.value + wz_dp_col.value) / 90.0, unit=dz_dp_col.unit)
        if dz_dp_col is not None and wz_dp_col is not None
        else None
    )
    column_ductility_normalized = str(column_ductility or "").strip().lower()
    ductility_applies = column_ductility_normalized in {"high", "moderate"}
    if ductility_applies:
        if t_req_e3_6 is None:
            raise ValueError("Unable to compute t_req_e3_6 because wz_dp_col could not be resolved.")
        column_limits.append(
            _step1_limit(
                check_id="section_e3_6_2.column_web_thickness_minimum",
                scope="column",
                clause="AISC 341-22w E3.6e.2",
                description="Espesor individual minimo del alma de columna",
                calculated_symbol="tw_col",
                limit_symbol="(dz_dp_col + wz_dp_col)/90; si use_weld_7_col=false: wz_dp_col=d_col-2*tf_col, dz_dp_col=max{d_lado-2*tf_lado}; si use_weld_7_col=true: h_w7_col=max{d_lado-2*tf_lado}/(nfilas_w7_col + 1), b_w7_col=b_dp_col/(ncolumna_w7_col + 1), dz_dp_col=h_w7_col, wz_dp_col=b_w7_col",
                calculated=column_profile["tw"],
                limit=t_req_e3_6,
                comparison="ge",
            )
        )
        if doubler_plate_enabled:
            t_dp_col = case.geometry.doubler_plate_thickness
            if t_dp_col is None:
                raise missing_required_input_error(
                    rule_id=rule_binding.rule_id,
                    source_document=rule_binding.source_document,
                    missing_fields=["geometry.doubler_plate_thickness"],
                    message=(
                        "Required input 'geometry.doubler_plate_thickness' is missing when "
                        "'geometry.doubler_plate_enabled' is true."
                    ),
                )
            # Additional minimum thickness requirement for moderate/high ductility.
            t_dp_min_6mm = (
                Quantity(value=6.0, unit="mm")
                if t_dp_col.unit == "mm"
                else (
                    Quantity(value=6.0 / 25.4, unit="in")
                    if t_dp_col.unit == "in"
                    else None
                )
            )
            if t_dp_min_6mm is not None:
                doubler_plate_limits.append(
                    _step1_limit(
                        check_id="section_custom.doubler_plate_thickness_min_6mm_mod_high",
                        scope="doubler_plate_col",
                        clause="AISC 341-22w E3.6e.2",
                        description="Espesor minimo absoluto de platina de enchape para ductilidad moderada/alta",
                        calculated_symbol="t_dp_col",
                        limit_symbol="6.0 mm",
                        calculated=t_dp_col,
                        limit=t_dp_min_6mm,
                        comparison="ge",
                    )
                )
            # If gap_dp_col > 2.0 mm, require at least 2 doubler plates.
            gap_dp_col = case.geometry.gap_dp_col
            n_dp_col = case.geometry.doubler_plate_count
            gap_dp_col_mm: float | None = None
            if gap_dp_col is not None:
                if gap_dp_col.unit == "mm":
                    gap_dp_col_mm = gap_dp_col.value
                elif gap_dp_col.unit == "in":
                    gap_dp_col_mm = gap_dp_col.value * 25.4
            if gap_dp_col_mm is not None and gap_dp_col_mm > 2.0:
                if n_dp_col is None:
                    raise missing_required_input_error(
                        rule_id=rule_binding.rule_id,
                        source_document=rule_binding.source_document,
                        missing_fields=["geometry.doubler_plate_count (n_dp_col)"],
                        message=(
                            "Required input 'geometry.doubler_plate_count' is missing for "
                            "the check gap_dp_col > 2.0 mm => n_dp_col >= 2."
                        ),
                    )
                doubler_plate_limits.append(
                    _step1_limit(
                        check_id="section_e3_6e_3.doubler_plate_count_min_when_gap_gt_2mm",
                        scope="doubler_plate_col",
                        clause="AISC 341-22w E3.6e.3",
                        description="Numero minimo de platinas de enchape cuando gap_dp_col > 2.0 mm",
                        calculated_symbol="n_dp_col",
                        limit_symbol="2",
                        calculated=Quantity(value=float(n_dp_col), unit="adim"),
                        limit=Quantity(value=2.0, unit="adim"),
                        comparison="ge",
                    )
                )
            doubler_plate_limits.append(
                _step1_limit(
                    check_id="section_e3_6_2.doubler_plate_thickness_minimum",
                    scope="doubler_plate_col",
                    clause="AISC 341-22w E3.6e.2",
                    description="Espesor individual minimo de platina de enchape del alma",
                    calculated_symbol="t_dp_col",
                    limit_symbol="(dz_dp_col + wz_dp_col)/90; si use_weld_7_col=false: wz_dp_col=d_col-2*tf_col, dz_dp_col=max{d_lado-2*tf_lado}; si use_weld_7_col=true: h_w7_col=max{d_lado-2*tf_lado}/(nfilas_w7_col + 1), b_w7_col=b_dp_col/(ncolumna_w7_col + 1), dz_dp_col=h_w7_col, wz_dp_col=b_w7_col",
                    calculated=t_dp_col,
                    limit=t_req_e3_6,
                    comparison="ge",
                )
            )
            tipo_acero_dp_col = case.materials.doubler_plate_steel_type or case.materials.plate_steel_type
            if tipo_acero_dp_col is not None and dz_dp_col is not None and wz_dp_col is not None:
                plate_props_dp = get_plate_steel_properties(
                    steel_type=str(tipo_acero_dp_col),
                    unit_system=case.units_system,
                )
                fy_dp_col = plate_props_dp["fy"]
                e_dp_col = elastic_modulus
                if isinstance(fy_dp_col, Quantity) and isinstance(e_dp_col, Quantity):
                    fy_over_e_dp = fy_dp_col.value / e_dp_col.value
                    if fy_over_e_dp < 0.0:
                        raise ValueError("Invalid Fy_dp_col/E_dp_col ratio for doubler plate additional thickness check.")
                    wz_for_max = _to_unit_length_local(wz_dp_col, dz_dp_col.unit)
                    if wz_for_max is not None:
                        dz_wz_max = dz_dp_col if dz_dp_col.value >= wz_for_max.value else wz_for_max
                        t_req_dp_2_42 = Quantity(
                            value=dz_wz_max.value * math.sqrt(fy_over_e_dp) / 2.42,
                            unit=dz_wz_max.unit,
                        )
                        doubler_plate_limits.append(
                            _step1_limit(
                                check_id="section_custom.doubler_plate_thickness_min_max_dz_wz_2_42",
                                scope="doubler_plate_col",
                                clause="Documento: Design-guide-13--wide-flange-column-stiffening-at-moment-connections | Seccion: DG13 Chapter 4",
                                description="Espesor minimo adicional de platina de enchape del alma",
                                calculated_symbol="t_dp_col",
                                limit_symbol="max{dz_dp_col, wz_dp_col}*sqrt(Fy_dp_col/E_dp_col)/2.42",
                                calculated=t_dp_col,
                                limit=t_req_dp_2_42,
                                comparison="ge",
                            )
                        )
    else:
        column_limits.append(
            _step1_verification_only_limit(
                check_id="section_e3_6_2.column_web_thickness_minimum",
                scope="column",
                clause="AISC 341-22w E3.6e.2",
                description="Espesor individual minimo del alma de columna",
                calculated_symbol="tw_col",
                verification_text=(
                    "No aplica para demanda_ductilidad_col='low'. "
                    "Formula de referencia: t >= (dz_dp_col + wz_dp_col)/90"
                ),
                passes=True,
            )
        )
        if doubler_plate_enabled:
            doubler_plate_limits.append(
                _step1_verification_only_limit(
                    check_id="section_e3_6_2.doubler_plate_thickness_minimum",
                    scope="doubler_plate_col",
                    clause="AISC 341-22w E3.6e.2",
                    description="Espesor individual minimo de platina de enchape del alma",
                    calculated_symbol="t_dp_col",
                    verification_text=(
                        "No aplica para demanda_ductilidad_col='low'. "
                        "Formula de referencia: t >= (dz_dp_col + wz_dp_col)/90"
                    ),
                    passes=True,
                )
            )

    # Additional check requested (only when use_weld_7_col=true):
    # t_dp_col + tw_col >= (d_col - 2*tf_col + max{d_lado-2*tf_lado})/90
    if use_w7 and doubler_plate_enabled and case.geometry.doubler_plate_thickness is not None:
        d_beam_net_candidates: list[Quantity] = []
        if beam_connection_sides in {"both_sides", "left_only"} and beam_profile_izq is not None:
            d_beam_net_candidates.append(
                Quantity(
                    value=beam_profile_izq["d"].value - 2.0 * beam_profile_izq["tf"].value,
                    unit=beam_profile_izq["d"].unit,
                )
            )
        if beam_connection_sides in {"both_sides", "right_only"}:
            d_beam_net_candidates.append(
                Quantity(
                    value=beam_profile_der["d"].value - 2.0 * beam_profile_der["tf"].value,
                    unit=beam_profile_der["d"].unit,
                )
            )
        if d_beam_net_candidates:
            base_unit = column_profile["tw"].unit
            converted_nets: list[Quantity] = []
            for q in d_beam_net_candidates:
                q_conv = _to_unit_length_local(q, base_unit)
                if q_conv is not None:
                    converted_nets.append(q_conv)
            d_col_conv = _to_unit_length_local(column_profile["d"], base_unit)
            tf_col_conv = _to_unit_length_local(column_profile["tf"], base_unit)
            t_dp_col_conv = _to_unit_length_local(case.geometry.doubler_plate_thickness, base_unit)
            if converted_nets and d_col_conv is not None and tf_col_conv is not None and t_dp_col_conv is not None:
                rhs_q = Quantity(
                    value=(
                        d_col_conv.value
                        - 2.0 * tf_col_conv.value
                        + max(converted_nets, key=lambda x: x.value).value
                    )
                    / 90.0,
                    unit=base_unit,
                )
                lhs_q = Quantity(
                    value=t_dp_col_conv.value + column_profile["tw"].value,
                    unit=base_unit,
                )
                column_limits.append(
                    _step1_limit(
                        check_id="section_e3_6_2.column_web_plus_doubler_with_w7",
                        scope="column",
                        clause="AISC 341-22w E3.6e.2",
                        description="Chequeo adicional con soldadura #7 habilitada",
                        calculated_symbol="t_dp_col + tw_col",
                        limit_symbol="(d_col - 2*tf_col + max{d_lado-2*tf_lado})/90",
                        calculated=lhs_q,
                        limit=rhs_q,
                        comparison="ge",
                    )
                )
                doubler_plate_limits.append(
                    _step1_limit(
                        check_id="section_e3_6_2.doubler_plate_plus_web_with_w7",
                        scope="doubler_plate_col",
                        clause="AISC 341-22w E3.6e.2",
                        description="Chequeo adicional con soldadura #7 habilitada",
                        calculated_symbol="t_dp_col + tw_col",
                        limit_symbol="(d_col - 2*tf_col + max{d_lado-2*tf_lado})/90",
                        calculated=lhs_q,
                        limit=rhs_q,
                        comparison="ge",
                    )
                )

    bp_bounds = active_table_61.get("bp")
    end_plate_limits: list[dict[str, Any]] = []
    if bp_bounds is not None:
        bp_min, bp_max = bp_bounds
        beam_margin_label = (
            f"{bp_margin:.0f} mm" if case.units_system == UnitSystem.SI else f"{bp_margin:.3f} in"
        )

        bp_plus_beam_margin_der = Quantity(value=beam_profile_der["bf"].value + bp_margin, unit=beam_profile_der["bf"].unit)
        bp_governing_max_der = Quantity(
            value=min(bp_max.value, bp_plus_beam_margin_der.value, bcf.value),
            unit=bp.unit,
        )
        bp_pass_der = (
            (bp_der.value <= bp_plus_beam_margin_der.value)
            and (bp_der.value <= bcf.value)
            and (bp_der.value >= bp_min.value)
        )
        end_plate_limits.append(
            _step1_compound_limit(
                check_id="section_6_3.end_plate_width_dual_limit_der",
                scope="end_plate_der",
                clause="Section 6.3 / Table 6.1",
                description="End-plate width explicit dual inequalities (right beam)",
                calculated_symbol="bp_pe_vgder",
                verification_text=(
                    f"bp_pe_vgder <= bbf_vgder + {beam_margin_label}; "
                    "bp_pe_vgder <= bcf"
                ),
                passes=bp_pass_der,
                calculated=bp_der,
                minimum=bp_min,
                maximum=bp_governing_max_der,
            )
        )
        deh_pe_vgder = Quantity(
            value=(bp_der.value - g_der.value) / 2.0,
            unit=bp_der.unit,
        )
        end_plate_limits.append(
            _step1_limit(
                check_id="section_6_3.end_plate_horizontal_edge_distance_ge_emin_der",
                scope="end_plate_der",
                clause="Section 6.3 / Table 6.1 + AISC 360 Table J3.4",
                description="Horizontal edge distance from plate edge to bolt line (right beam)",
                calculated_symbol="deh_pe_vgder",
                limit_symbol="emin",
                calculated=deh_pe_vgder,
                limit=min_edge_der,
                comparison="ge",
            )
        )

        if beam_connection_sides == "both_sides" and beam_profile_izq is not None and bp_izq is not None:
            bp_plus_beam_margin_izq = Quantity(
                value=beam_profile_izq["bf"].value + bp_margin,
                unit=beam_profile_izq["bf"].unit,
            )
            bp_governing_max_izq = Quantity(
                value=min(bp_max.value, bp_plus_beam_margin_izq.value, bcf.value),
                unit=bp.unit,
            )
            bp_pass_izq = (
                (bp_izq.value <= bp_plus_beam_margin_izq.value)
                and (bp_izq.value <= bcf.value)
                and (bp_izq.value >= bp_min.value)
            )
            end_plate_limits.append(
                _step1_compound_limit(
                    check_id="section_6_3.end_plate_width_dual_limit_izq",
                    scope="end_plate_izq",
                    clause="Section 6.3 / Table 6.1",
                    description="End-plate width explicit dual inequalities (left beam)",
                    calculated_symbol="bp_pe_vgizq",
                    verification_text=(
                        f"bp_pe_vgizq <= bbf_vgizq + {beam_margin_label}; "
                        "bp_pe_vgizq <= bcf"
                    ),
                    passes=bp_pass_izq,
                    calculated=bp_izq,
                    minimum=bp_min,
                    maximum=bp_governing_max_izq,
                )
            )
            if g_izq is None:
                raise ValueError("geometry.bolt_gage_vgizq is required for deh_pe_vgizq check.")
            if min_edge_izq is None:
                raise ValueError("minimum edge distance for vgizq could not be resolved for deh_pe_vgizq check.")
            deh_pe_vgizq = Quantity(
                value=(bp_izq.value - g_izq.value) / 2.0,
                unit=bp_izq.unit,
            )
            end_plate_limits.append(
                _step1_limit(
                    check_id="section_6_3.end_plate_horizontal_edge_distance_ge_emin_izq",
                    scope="end_plate_izq",
                    clause="Section 6.3 / Table 6.1 + AISC 360 Table J3.4",
                    description="Horizontal edge distance from plate edge to bolt line (left beam)",
                    calculated_symbol="deh_pe_vgizq",
                    limit_symbol="emin",
                    calculated=deh_pe_vgizq,
                    limit=min_edge_izq,
                    comparison="ge",
                )
            )

    end_plate_stiffener_limits = [
        _step1_compound_limit(
            check_id="section_6_3.end_plate_stiffener_height_derived_der",
            scope="end_plate_stiffener_der",
            clause="Section 6.3",
            description="End-plate stiffener height derived from end-plate geometry (right beam)",
            calculated_symbol="h_pest_vgder",
            verification_text=(
                    (
                        f"h_pest_vgder = pfo_pe_vgder + pb_pe_vgder + de_pe_vgder; {stiffener_height_der.value:.3f} {stiffener_height_der.unit} = "
                        f"{pfo_der.value:.3f} {pfo_der.unit} + {pb_der.value:.3f} {pb_der.unit} + {de_der.value:.3f} {de_der.unit}"
                    )
                    if case.connection_type == "bseep_8es" and pb_der is not None
                    else (
                        f"h_pest_vgder = pfo_pe_vgder + de_pe_vgder; {stiffener_height_der.value:.3f} {stiffener_height_der.unit} = "
                        f"{pfo_der.value:.3f} {pfo_der.unit} + {de_der.value:.3f} {de_der.unit}"
                    )
                ),
            passes=stiffener_height_der.value > 0.0,
            calculated=stiffener_height_der,
        )
    ]
    if beam_connection_sides == "both_sides" and stiffener_height_izq is not None and pfo_izq is not None and de_izq is not None:
        end_plate_stiffener_limits.append(
            _step1_compound_limit(
                check_id="section_6_3.end_plate_stiffener_height_derived_izq",
                scope="end_plate_stiffener_izq",
                clause="Section 6.3",
                description="End-plate stiffener height derived from end-plate geometry (left beam)",
                calculated_symbol="h_pest_vgizq",
                verification_text=(
                    (
                        f"h_pest_vgizq = pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq; {stiffener_height_izq.value:.3f} {stiffener_height_izq.unit} = "
                        f"{pfo_izq.value:.3f} {pfo_izq.unit} + {pb_izq.value:.3f} {pb_izq.unit} + {de_izq.value:.3f} {de_izq.unit}"
                    )
                    if case.connection_type == "bseep_8es" and pb_izq is not None
                    else (
                        f"h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; {stiffener_height_izq.value:.3f} {stiffener_height_izq.unit} = "
                        f"{pfo_izq.value:.3f} {pfo_izq.unit} + {de_izq.value:.3f} {de_izq.unit}"
                    )
                ),
                passes=stiffener_height_izq.value > 0.0,
                calculated=stiffener_height_izq,
            )
        )
    if case.connection_type in {"bseep_4es", "bseep_8es"}:
        if ts_der is None:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=["geometry.stiffener_thickness_vgder"],
                message="Required input 'geometry.stiffener_thickness_vgder' is missing for applicable rule.",
            )
        stiffener_fy_base = _require(case, "materials.stiffener_fy", rule_binding)
        stiffener_fy_der = case.materials.stiffener_fy_vgder or stiffener_fy_base
        stiffener_fy_izq = case.materials.stiffener_fy_vgizq or stiffener_fy_der
        ts = ts_der
        tbw = beam_profile_der["tw"]
        g_min_stiffener = compute_minimum_stiffener_bolt_gage(
            minimum_edge_distance=min_edge_der,
            stiffener_thickness=ts,
            unit_system=case.units_system,
        )
        ts_required = compute_required_stiffener_thickness(
            beam_web_thickness=tbw,
            beam_fy=beam_fy,
            stiffener_fy=stiffener_fy_der,
            unit_system=case.units_system,
        )
        slenderness_ratio = compute_stiffener_slenderness_ratio(
            stiffener_height=stiffener_height,
            stiffener_thickness=ts,
            unit_system=case.units_system,
        )
        slenderness_limit = compute_stiffener_slenderness_ratio_limit(
            elastic_modulus=elastic_modulus,
            stiffener_fy=stiffener_fy_der,
            unit_system=case.units_system,
        )
        end_plate_stiffener_limits.extend(
            [
                _step1_limit(
                    check_id="section_6_7_1.stiffener_thickness_minimum_der",
                    scope="end_plate_stiffener_der",
                    clause="Section 6.7.1 Eq. (6.7-9)",
                    description="Stiffener thickness minimum requirement (right beam)",
                    calculated_symbol="t_pest_vgder",
                    limit_symbol="tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder",
                    calculated=ts,
                    limit=ts_required,
                    comparison="ge",
                ),
                _step1_limit(
                    check_id="section_6_7_1.stiffener_local_buckling_limit_der",
                    scope="end_plate_stiffener_der",
                    clause="Section 6.7.1 Eq. (6.7-10)",
                    description="Stiffener local buckling width-thickness limit (right beam)",
                    calculated_symbol="h_pest_vgder/t_pest_vgder",
                    limit_symbol="0.56*sqrt(E_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder",
                    calculated=Quantity(value=slenderness_ratio, unit="ratio"),
                    limit=Quantity(value=slenderness_limit, unit="ratio"),
                    comparison="le",
                ),
                _step1_limit(
                    check_id="section_6_3_1.stiffener_bolt_gage_clearance_der",
                    scope="end_plate_stiffener_der",
                    clause="Section 6.3 (stiffened) + AISC 360 Table J3.4",
                    description="Bolt gage clearance with stiffener thickness (right beam)",
                    calculated_symbol="g_b_vgder",
                    limit_symbol="2emin + t_pest_vgder",
                    calculated=g_der,
                    limit=g_min_stiffener,
                    comparison="ge",
                ),
            ]
        )
        if beam_connection_sides == "both_sides" and beam_profile_izq is not None and stiffener_height_izq is not None:
            if ts_izq is None or g_izq is None:
                missing_fields: list[str] = []
                if ts_izq is None:
                    missing_fields.append("geometry.stiffener_thickness_vgizq")
                if g_izq is None:
                    missing_fields.append("geometry.bolt_gage_vgizq")
                raise missing_required_input_error(
                    rule_id=rule_binding.rule_id,
                    source_document=rule_binding.source_document,
                    missing_fields=missing_fields,
                    message="Required side-specific geometry is missing for left stiffener checks.",
                )
            ts_required_izq = compute_required_stiffener_thickness(
                beam_web_thickness=beam_profile_izq["tw"],
                beam_fy=beam_fy,
                stiffener_fy=stiffener_fy_izq,
                unit_system=case.units_system,
            )
            slenderness_ratio_izq = compute_stiffener_slenderness_ratio(
                stiffener_height=stiffener_height_izq,
                stiffener_thickness=ts_izq,
                unit_system=case.units_system,
            )
            slenderness_limit_izq = compute_stiffener_slenderness_ratio_limit(
                elastic_modulus=elastic_modulus,
                stiffener_fy=stiffener_fy_izq,
                unit_system=case.units_system,
            )
            min_edge_for_izq = min_edge_izq if min_edge_izq is not None else min_edge_der
            g_min_stiffener_izq = compute_minimum_stiffener_bolt_gage(
                minimum_edge_distance=min_edge_for_izq,
                stiffener_thickness=ts_izq,
                unit_system=case.units_system,
            )
            end_plate_stiffener_limits.extend(
                [
                    _step1_limit(
                        check_id="section_6_7_1.stiffener_thickness_minimum_izq",
                        scope="end_plate_stiffener_izq",
                        clause="Section 6.7.1 Eq. (6.7-9)",
                        description="Stiffener thickness minimum requirement (left beam)",
                        calculated_symbol="t_pest_vgizq",
                        limit_symbol="tw_vgizq*(Fy_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq",
                        calculated=ts_izq,
                        limit=ts_required_izq,
                        comparison="ge",
                    ),
                    _step1_limit(
                        check_id="section_6_7_1.stiffener_local_buckling_limit_izq",
                        scope="end_plate_stiffener_izq",
                        clause="Section 6.7.1 Eq. (6.7-10)",
                        description="Stiffener local buckling width-thickness limit (left beam)",
                        calculated_symbol="h_pest_vgizq/t_pest_vgizq",
                        limit_symbol="0.56*sqrt(E_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq",
                        calculated=Quantity(value=slenderness_ratio_izq, unit="ratio"),
                        limit=Quantity(value=slenderness_limit_izq, unit="ratio"),
                        comparison="le",
                    ),
                    _step1_limit(
                        check_id="section_6_3_1.stiffener_bolt_gage_clearance_izq",
                        scope="end_plate_stiffener_izq",
                        clause="Section 6.3 (stiffened) + AISC 360 Table J3.4",
                        description="Bolt gage clearance with stiffener thickness (left beam)",
                        calculated_symbol="g_b_vgizq",
                        limit_symbol="2emin + t_pest_vgizq",
                        calculated=g_izq,
                        limit=g_min_stiffener_izq,
                        comparison="ge",
                    ),
                ]
            )

    continuity_plate_limits: list[dict[str, object]] = []
    l_w5_col_computed: Quantity | None = None
    l_w6_col_computed: Quantity | None = None
    l_w8_col_computed: Quantity | None = None
    l_w9_col_computed: Quantity | None = None
    weld6_type_norm = _normalize_end_plate_stiffener_weld_type(continuity_plate_web_weld_type_raw)
    continuity_plate_weld_thickness_limit = Quantity(
        value=3.0 / 8.0 if case.units_system == UnitSystem.US else 10.0,
        unit="in" if case.units_system == UnitSystem.US else "mm",
    )
    if (
        continuity_plate_enabled
        and tcp is not None
        and continuity_plate_weld_type_raw is not None
        and str(continuity_plate_weld_type_raw).strip()
    ):
        continuity_plate_weld_type_normalized = _normalize_continuity_plate_weld_type(continuity_plate_weld_type_raw)
        continuity_plate_limits = [
            _step1_text_in_set_limit(
                check_id="section_6_3.continuity_plate_weld_type_declared",
                scope="weld_5_col",
                clause="Section 6.3 (continuity plate weld detail)",
                description="Continuity-plate weld type shall be explicitly declared with an allowed weld category",
                calculated_symbol="tipo_w5_col",
                limit_symbol="{fillet, cjp}",
                calculated_text=continuity_plate_weld_type_normalized,
                allowed_values=("fillet", "cjp"),
            ),
            _step1_continuity_plate_weld_limit(
                check_id="section_6_3.continuity_plate_weld_type_for_thin_plate",
                scope="weld_5_col",
                clause="Section 6.3 (continuity plate weld detail)",
                description="Tamano minimo de soldadura #5 cuando tipo_w5_col es fillet",
                continuity_plate_thickness=tcp,
                weld_size=w_w5_col,
                weld_type_raw=continuity_plate_weld_type_raw,
            ),
        ]

    kdet_for_pc = column_profile.get("kdet") or column_profile.get("kdes")
    tfdet_for_pc = column_profile.get("tfdet") or column_profile.get("tf")
    def _mm_to_unit_value(mm_value: float, unit: str) -> float:
        if unit == "mm":
            return mm_value
        if unit == "in":
            return mm_value / 25.4
        raise ValueError(f"Unsupported length unit for continuity-plate weld 5 derivation: {unit}")

    def _round_up_to_multiple_5mm(value: float, unit: str) -> float:
        step = _mm_to_unit_value(5.0, unit)
        if step <= 0.0:
            return value
        return math.ceil(value / step) * step

    l2_pc_col_q: Quantity | None = None
    b2_pc_col_q: Quantity | None = None
    if (
        kdet_for_pc is not None
        and tfdet_for_pc is not None
        and column_profile.get("d") is not None
    ):
        clip1_pc_col_q = Quantity(
            value=kdet_for_pc.value - tfdet_for_pc.value + _mm_to_unit_value(38.0, kdet_for_pc.unit),
            unit=kdet_for_pc.unit,
        )
        l1_pc_col_q = Quantity(
            value=column_profile["d"].value
            - 2.0 * tfdet_for_pc.value
            - _mm_to_unit_value(3.0, column_profile["d"].unit),
            unit=column_profile["d"].unit,
        )
        l2_pc_col_q = Quantity(
            value=l1_pc_col_q.value - 2.0 * clip1_pc_col_q.value,
            unit=l1_pc_col_q.unit,
        )
    if (
        continuity_plate_enabled
        and case.geometry.continuity_plate_width_b1 is not None
        and column_profile.get("k1") is not None
        and column_profile.get("tw") is not None
        and case.geometry.continuity_plate_width_b1.unit == column_profile["k1"].unit == column_profile["tw"].unit
    ):
        clip2_pc_col_q = Quantity(
            value=((column_profile["k1"].value - column_profile["tw"].value) / 2.0)
            + _mm_to_unit_value(12.0, column_profile["k1"].unit),
            unit=column_profile["k1"].unit,
        )
        clip2_pc_col_q = Quantity(
            value=_round_up_to_multiple_5mm(clip2_pc_col_q.value, clip2_pc_col_q.unit),
            unit=clip2_pc_col_q.unit,
        )
        b2_pc_col_q = Quantity(
            value=case.geometry.continuity_plate_width_b1.value - clip2_pc_col_q.value,
            unit=case.geometry.continuity_plate_width_b1.unit,
        )
    if continuity_plate_enabled and b2_pc_col_q is not None and l_gap_w5_col is not None:
        if l_gap_w5_col.unit == b2_pc_col_q.unit:
            l_gap_for_lw5 = l_gap_w5_col.value
        elif l_gap_w5_col.unit == "mm" and b2_pc_col_q.unit == "in":
            l_gap_for_lw5 = l_gap_w5_col.value / 25.4
        elif l_gap_w5_col.unit == "in" and b2_pc_col_q.unit == "mm":
            l_gap_for_lw5 = l_gap_w5_col.value * 25.4
        else:
            raise ValueError(
                f"Unsupported mixed units for L_w5_col derivation: {b2_pc_col_q.unit} vs {l_gap_w5_col.unit}"
            )
        l_w5_col_computed = Quantity(
            value=b2_pc_col_q.value - 2.0 * l_gap_for_lw5,
            unit=b2_pc_col_q.unit,
        )
    if continuity_plate_enabled and l2_pc_col_q is not None and l_gap_w6_col is not None:
        if l_gap_w6_col.unit == l2_pc_col_q.unit:
            l_gap_for_lw6 = l_gap_w6_col.value
        elif l_gap_w6_col.unit == "mm" and l2_pc_col_q.unit == "in":
            l_gap_for_lw6 = l_gap_w6_col.value / 25.4
        elif l_gap_w6_col.unit == "in" and l2_pc_col_q.unit == "mm":
            l_gap_for_lw6 = l_gap_w6_col.value * 25.4
        else:
            raise ValueError(
                f"Unsupported mixed units for L_w6_col derivation: {l2_pc_col_q.unit} vs {l_gap_w6_col.unit}"
            )
        l_w6_col_computed = Quantity(
            value=l2_pc_col_q.value - 2.0 * l_gap_for_lw6,
            unit=l2_pc_col_q.unit,
        )
    if h_dp_col is not None and l_gap_w8_col is not None:
        if l_gap_w8_col.unit == h_dp_col.unit:
            l_gap_for_lw8 = l_gap_w8_col.value
        elif l_gap_w8_col.unit == "mm" and h_dp_col.unit == "in":
            l_gap_for_lw8 = l_gap_w8_col.value / 25.4
        elif l_gap_w8_col.unit == "in" and h_dp_col.unit == "mm":
            l_gap_for_lw8 = l_gap_w8_col.value * 25.4
        else:
            raise ValueError(
                f"Unsupported mixed units for L_w8_col derivation: {h_dp_col.unit} vs {l_gap_w8_col.unit}"
            )
        l_w8_col_computed = Quantity(
            value=h_dp_col.value - 2.0 * l_gap_for_lw8,
            unit=h_dp_col.unit,
        )
    if bool(use_weld_9_col):
        if b_dp_col is not None and l_gap_w9_col is not None:
            if l_gap_w9_col.unit == b_dp_col.unit:
                l_gap_for_lw9 = l_gap_w9_col.value
            elif l_gap_w9_col.unit == "mm" and b_dp_col.unit == "in":
                l_gap_for_lw9 = l_gap_w9_col.value / 25.4
            elif l_gap_w9_col.unit == "in" and b_dp_col.unit == "mm":
                l_gap_for_lw9 = l_gap_w9_col.value * 25.4
            else:
                raise ValueError(
                    f"Unsupported mixed units for L_w9_col derivation: {b_dp_col.unit} vs {l_gap_w9_col.unit}"
                )
            l_w9_col_computed = Quantity(
                value=b_dp_col.value - 2.0 * l_gap_for_lw9,
                unit=b_dp_col.unit,
            )
    else:
        zero_unit_w9 = b_dp_col.unit if b_dp_col is not None else (l_gap_w9_col.unit if l_gap_w9_col is not None else "mm")
        l_w9_col_computed = Quantity(value=0.0, unit=zero_unit_w9)
    if continuity_plate_enabled and l_w6_col_computed is not None and weld6_type_norm == "fillet":
        tw_col = column_profile.get("tw")
        d_col = column_profile.get("d")
        if kdet_for_pc is None or tw_col is None or d_col is None:
            raise ValueError("Missing d_col/tw_col/kdet_col to evaluate weld_6_col limits.")
        if not (l_w6_col_computed.unit == d_col.unit == tw_col.unit == kdet_for_pc.unit):
            raise ValueError(
                "Inconsistent units for weld_6_col length checks: "
                f"Lws_col={l_w6_col_computed.unit}, d_col={d_col.unit}, tw_col={tw_col.unit}, kdet_col={kdet_for_pc.unit}"
            )
        lws_max = Quantity(
            value=d_col.value - 2.0 * (kdet_for_pc.value + 4.0 * tw_col.value),
            unit=d_col.unit,
        )
        lws_min = Quantity(
            value=d_col.value - 2.0 * (kdet_for_pc.value + 6.0 * tw_col.value),
            unit=d_col.unit,
        )
        continuity_plate_limits.extend(
            [
                _step1_limit(
                    check_id="section_6_3.weld_6_length_max",
                    scope="weld_6_col",
                    clause="AISC 358-22 Section 6.3",
                    description="Longitud maxima de soldadura #6 en columna",
                    calculated_symbol="Lws_col",
                    limit_symbol="d_col - 2*(kdet_col + 4*tw_col)",
                    calculated=l_w6_col_computed,
                    limit=lws_max,
                    comparison="le",
                ),
                _step1_limit(
                    check_id="section_6_3.weld_6_length_min",
                    scope="weld_6_col",
                    clause="AISC 358-22 Section 6.3",
                    description="Longitud minima de soldadura #6 en columna",
                    calculated_symbol="Lws_col",
                    limit_symbol="d_col - 2*(kdet_col + 6*tw_col)",
                    calculated=l_w6_col_computed,
                    limit=lws_min,
                    comparison="ge",
                ),
            ]
        )

    # Continuity plate geometry checks (AISC 360 J10.8 + SDH 4th ed. 2024)
    b1_pc_col = case.geometry.continuity_plate_width_b1
    t_pc_col = case.geometry.continuity_plate_thickness
    tipo_acero_pc_col = case.materials.continuity_plate_steel_type or case.materials.plate_steel_type
    n_dp_col = case.geometry.doubler_plate_count
    if case.geometry.doubler_plate_enabled and n_dp_col is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["geometry.doubler_plate_count"],
            message="Required input 'geometry.doubler_plate_count' is missing when 'geometry.doubler_plate_enabled' is true.",
        )
    t_dp_col = case.geometry.doubler_plate_thickness
    dp_extra = 0.0
    if case.geometry.doubler_plate_enabled:
        if t_dp_col is None:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=["geometry.doubler_plate_thickness"],
                message="Required input 'geometry.doubler_plate_thickness' is missing when 'geometry.doubler_plate_enabled' is true.",
            )
        n_dp_value = float(n_dp_col or 0)
        dp_extra = n_dp_value * t_dp_col.value
    if continuity_plate_enabled and b1_pc_col is not None and t_pc_col is not None and tipo_acero_pc_col is not None:
        plate_props_pc = get_plate_steel_properties(
            steel_type=str(tipo_acero_pc_col),
            unit_system=case.units_system,
        )
        fy_pc_col = plate_props_pc["fy"]
        ry_pc_col = float(plate_props_pc["ry"])
        e_pc_col = elastic_modulus
        if not isinstance(fy_pc_col, Quantity) or not isinstance(e_pc_col, Quantity):
            raise ValueError("Invalid continuity plate material properties for Fy/E evaluation.")

        # Global bound independent of side.
        b1_pc_col_max = Quantity(
            value=(bcf.value - column_profile["tw"].value - dp_extra) / 2.0,
            unit=bcf.unit,
        )
        continuity_plate_limits.append(
            _step1_limit(
                check_id="section_j10_8.continuity_plate_width_max",
                scope="continuity_plate_col",
                clause="AISC 360-22 J10.8 / SDH 4th ed. 2024",
                description="Ancho maximo de platina de continuidad",
                calculated_symbol="b1_pc_col",
                limit_symbol="(bf_col - tw_col - n_dp_col*t_dp_col)/2",
                calculated=b1_pc_col,
                limit=b1_pc_col_max,
                comparison="le",
            )
        )

        active_sides_for_cp = _active_beam_sides(case)
        for side_suffix in active_sides_for_cp:
            side_profile = beam_profile_izq if side_suffix == "izq" else beam_profile_der
            if side_profile is None:
                continue
            bf_side = side_profile["bf"]
            tw_col = column_profile["tw"]
            side_tag = f"vg{side_suffix}"

            b1_min_j108 = Quantity(
                value=bf_side.value / 2.0 + 0.5 * tw_col.value + 0.5 * dp_extra,
                unit=bf_side.unit,
            )
            continuity_plate_limits.append(
                _step1_limit(
                    check_id=f"section_j10_8.continuity_plate_width_min_{side_suffix}",
                    scope="continuity_plate_col",
                    clause="AISC 360-22 J10.8",
                    description=f"Ancho minimo de platina de continuidad (viga {side_suffix})",
                    calculated_symbol="b1_pc_col",
                    limit_symbol=f"bf_vg{side_suffix}/2 + 0.5*tw_col + 0.5*n_dp_col*t_dp_col",
                    calculated=b1_pc_col,
                    limit=b1_min_j108,
                    comparison="ge",
                )
            )

            b1_min_sdh = Quantity(
                value=(bf_side.value - tw_col.value) / 2.0,
                unit=bf_side.unit,
            )
            continuity_plate_limits.append(
                _step1_limit(
                    check_id=f"section_sdh_2024.continuity_plate_width_min_{side_suffix}",
                    scope="continuity_plate_col",
                    clause="SDH 4th ed. 2024",
                    description=f"Ancho minimo alterno de platina de continuidad (viga {side_suffix})",
                    calculated_symbol="b1_pc_col",
                    limit_symbol=f"(bf_vg{side_suffix} - tw_col)/2",
                    calculated=b1_pc_col,
                    limit=b1_min_sdh,
                    comparison="ge",
                )
            )

            fy_over_e = fy_pc_col.value / e_pc_col.value
            if fy_over_e < 0.0:
                raise ValueError("Fy_pc_col / E_pc_col must be non-negative.")
            tf_candidates: list[Quantity] = []
            if beam_profile_izq is not None:
                tf_candidates.append(
                    Quantity(
                        value=beam_profile_izq["tf"].value / 2.0,
                        unit=beam_profile_izq["tf"].unit,
                    )
                )
            if beam_profile_der is not None:
                tf_candidates.append(
                    Quantity(
                        value=beam_profile_der["tf"].value / 2.0,
                        unit=beam_profile_der["tf"].unit,
                    )
                )
            if not tf_candidates:
                tf_candidates.append(
                    Quantity(
                        value=side_profile["tf"].value / 2.0,
                        unit=side_profile["tf"].unit,
                    )
                )
            t_req_1 = min(tf_candidates, key=lambda q: q.value)
            t_req_2 = Quantity(value=b1_pc_col.value / 16.0, unit=b1_pc_col.unit)
            t_req_3 = Quantity(
                value=(b1_pc_col.value / 0.56) * math.sqrt(fy_over_e),
                unit=b1_pc_col.unit,
            )
            t_req_min = min((t_req_1, t_req_2, t_req_3), key=lambda q: q.value)
            if beam_profile_izq is not None and beam_profile_der is not None:
                t_limit_symbol = (
                    "min{tf_vgizq/2, tf_vgder/2, b1_pc_col/16, "
                    "(b1_pc_col/0.56)*sqrt(Fy_pc_col/E_pc_col)}"
                )
            else:
                active_tf_tag = "tf_vgizq" if beam_profile_izq is not None else "tf_vgder"
                t_limit_symbol = (
                    f"min{{{active_tf_tag}/2, b1_pc_col/16, "
                    "(b1_pc_col/0.56)*sqrt(Fy_pc_col/E_pc_col)}}"
                )
            # In both-sides cases this verification is identical for left/right;
            # keep a single rendered check to avoid duplication.
            if not (len(active_sides_for_cp) == 2 and side_suffix == "der"):
                continuity_plate_limits.append(
                    _step1_limit(
                        check_id=f"section_j10_8.continuity_plate_thickness_min_{side_suffix}",
                        scope="continuity_plate_col",
                        clause="AISC 360-22 J10.8",
                        description=f"Espesor minimo de platina de continuidad (viga {side_suffix})",
                        calculated_symbol="t_pc_col",
                        limit_symbol=t_limit_symbol,
                        calculated=t_pc_col,
                        limit=t_req_min,
                        comparison="ge",
                    )
                )

        # Global continuity-plate thickness lower bound requested by user.
        # Applies whenever continuity plates are enabled.
        fy_over_e_global = fy_pc_col.value / e_pc_col.value
        if fy_over_e_global < 0.0:
            raise ValueError("Fy_pc_col / E_pc_col must be non-negative.")
        t_req_global_045 = Quantity(
            value=(b1_pc_col.value / 0.45) * math.sqrt(fy_over_e_global),
            unit=b1_pc_col.unit,
        )
        continuity_plate_limits.append(
            _step1_limit(
                check_id="project.continuity_plate_thickness_min_global_045",
                scope="continuity_plate_col",
                clause="Requisito de proyecto (si usar_pc_col=true)",
                description="Espesor minimo global de platina de continuidad",
                calculated_symbol="t_pc_col",
                limit_symbol="(b1_pc_col/0.45)*sqrt(Fy_pc_col/E_pc_col)",
                calculated=t_pc_col,
                limit=t_req_global_045,
                comparison="ge",
            )
        )

        # Additional continuity-plate requirements for moderate/high ductility.
        # E3.6f(1)(b): one-sided -> t >= 0.50*tf_side; two-sided -> t >= 0.75*max(tf_left, tf_right)
        # E3-9: b/t <= 0.56*sqrt(E/(Ry*Fy)) -> t >= (b/0.56)*sqrt(Ry*Fy/E), with b = max(b1, b2)
        column_ductility_norm = str(column_ductility or "").strip().lower()
        if column_ductility_norm in {"moderate", "high"}:
            two_sided_connection = len(active_sides_for_cp) == 2
            if two_sided_connection:
                tf_candidates_341: list[Quantity] = []
                if beam_profile_izq is not None:
                    tf_candidates_341.append(beam_profile_izq["tf"])
                if beam_profile_der is not None:
                    tf_candidates_341.append(beam_profile_der["tf"])
                if not tf_candidates_341:
                    raise ValueError("Two-sided continuity plate check requires beam flange thickness.")
                tf_thicker = max(tf_candidates_341, key=lambda q: q.value)
                t_req_341_tf = Quantity(value=0.75 * tf_thicker.value, unit=tf_thicker.unit)
                t_limit_341_symbol = "0.75*max(tf_vgizq, tf_vgder)"
                t_desc_341 = "Espesor minimo de platina de continuidad (conexion a dos lados, 75% del ala mas gruesa)"
            else:
                side_for_tf = active_sides_for_cp[0] if active_sides_for_cp else "izq"
                profile_for_tf = beam_profile_izq if side_for_tf == "izq" else beam_profile_der
                if profile_for_tf is None:
                    raise ValueError("One-sided continuity plate check requires active beam flange thickness.")
                tf_side = profile_for_tf["tf"]
                t_req_341_tf = Quantity(value=0.50 * tf_side.value, unit=tf_side.unit)
                t_limit_341_symbol = f"0.50*tf_vg{side_for_tf}"
                t_desc_341 = f"Espesor minimo de platina de continuidad (conexion a un lado, 50% de tf_vg{side_for_tf})"

            k1_col = column_profile.get("k1")
            b2_pc_col: Quantity | None = None
            if isinstance(k1_col, Quantity):
                tw_col_k1 = column_profile["tw"]
                clip2_pc_col = Quantity(
                    value=((k1_col.value - tw_col_k1.value) / 2.0) + _mm_to_unit_value(12.0, k1_col.unit),
                    unit=k1_col.unit,
                )
                clip2_pc_col = Quantity(
                    value=_round_up_to_multiple_5mm(clip2_pc_col.value, clip2_pc_col.unit),
                    unit=clip2_pc_col.unit,
                )
                b2_pc_col = Quantity(
                    value=b1_pc_col.value - clip2_pc_col.value,
                    unit=b1_pc_col.unit,
                )
            b_eff_pc_col = b2_pc_col if (b2_pc_col is not None and b2_pc_col.value > b1_pc_col.value) else b1_pc_col
            t_req_341_ry = Quantity(
                value=(b_eff_pc_col.value / 0.56) * math.sqrt((ry_pc_col * fy_pc_col.value) / e_pc_col.value),
                unit=b_eff_pc_col.unit,
            )
            continuity_plate_limits.append(
                _step1_limit(
                    check_id="section_e3_9.continuity_plate_width_to_thickness_limit",
                    scope="continuity_plate_col",
                    clause="AISC 341-22 Eq. (E3-9)",
                    description="Limite ancho/espesor de platina de continuidad (b/t)",
                    calculated_symbol="t_pc_col",
                    limit_symbol="(max(b1_pc_col, b2_pc_col)/0.56)*sqrt(Ry_pc_col*Fy_pc_col/E_pc_col)",
                    calculated=t_pc_col,
                    limit=t_req_341_ry,
                    comparison="ge",
                )
            )
            continuity_plate_limits.append(
                _step1_limit(
                    check_id="section_e3_6f_1b.continuity_plate_thickness_min_by_connection",
                    scope="continuity_plate_col",
                    clause="AISC 341-22w E3.6f(1)(b)",
                    description=t_desc_341,
                    calculated_symbol="t_pc_col",
                    limit_symbol=t_limit_341_symbol,
                    calculated=t_pc_col,
                    limit=t_req_341_tf,
                    comparison="ge",
                )
            )


    weld_limits: list[dict[str, object]] = []
    for side_suffix in _active_beam_sides(case):
        side_tag = f"vg{side_suffix}"
        ductility_side = column_ductility
        if str(ductility_side).strip().lower() not in {"high", "moderate"}:
            continue
        weld_type_side_raw = getattr(case.geometry, f"tipo_w4_{side_tag}", None)
        weld_type_side = _normalize_end_plate_stiffener_weld_type(weld_type_side_raw)
        backing_thickness_side = getattr(case.geometry, f"t_w4_1_{side_tag}", None)
        required_backing_mm = 8.0
        backing_matches = False
        if backing_thickness_side is not None:
            if backing_thickness_side.unit == "mm":
                backing_value_mm = backing_thickness_side.value
            elif backing_thickness_side.unit == "in":
                backing_value_mm = backing_thickness_side.value * 25.4
            else:
                backing_value_mm = float("nan")
            backing_matches = abs(backing_value_mm - required_backing_mm) <= 1e-6
        passes_w4 = (weld_type_side == "cjp") and backing_matches
        backing_text = (
            "0 mm"
            if backing_thickness_side is None
            else f"{backing_thickness_side.value:.3f} {backing_thickness_side.unit}"
        )
        weld_limits.append(
            _step1_verification_only_limit(
                check_id=f"section_6_7.beam_flange_to_end_plate_weld_requirement_{side_tag}",
                scope=f"weld_4_{side_tag}",
                clause="Section 6.7",
                description=(
                    "Requisitos de soldadura entre ala de viga y placa de extremo "
                    f"({'viga izquierda' if side_suffix == 'izq' else 'viga derecha'})"
                ),
                calculated_symbol=f"tipo_w4_{side_tag}",
                verification_text=(
                    f"si demanda_ductilidad_{side_tag} in {{high, moderate}}: "
                    f"tipo_w4_{side_tag} == cjp; t_w4_1_{side_tag} == 8 mm; "
                    f"demanda_ductilidad_{side_tag} = {ductility_side}; "
                    f"tipo_w4_{side_tag} = {weld_type_side}; "
                    f"t_w4_1_{side_tag} = {backing_text}"
                ),
                passes=passes_w4,
            )
        )

    def _geometry_by_side(field_root: str, side_tag: str) -> Any:
        side_value = getattr(case.geometry, f"{field_root}_{side_tag}", None)
        if side_value is not None:
            return side_value
        if beam_connection_sides == "both_sides":
            return None
        return getattr(case.geometry, field_root, None)

    def _minimum_thickness(left: Quantity | None, right: Quantity | None) -> Quantity | None:
        if left is None or right is None:
            return None
        if left.unit == right.unit:
            value = left if left.value <= right.value else right
            return Quantity(value=value.value, unit=value.unit)
        if left.unit == "in" and right.unit == "mm":
            left_mm = left.value * 25.4
            value_mm = left_mm if left_mm <= right.value else right.value
            return Quantity(value=value_mm, unit="mm")
        if left.unit == "mm" and right.unit == "in":
            right_mm = right.value * 25.4
            value_mm = left.value if left.value <= right_mm else right_mm
            return Quantity(value=value_mm, unit="mm")
        return None

    def _append_fillet_missing_limit(
        *,
        check_id: str,
        scope: str,
        description: str,
        calculated_symbol: str,
        missing_fields: tuple[str, ...],
    ) -> None:
        weld_limits.append(
            _step1_verification_only_limit(
                check_id=check_id,
                scope=scope,
                clause="AISC 360-22 Section J2",
                description=description,
                calculated_symbol=calculated_symbol,
                verification_text=(
                    "Chequeo no evaluable por falta de datos requeridos para soldadura de filete: "
                    + ", ".join(missing_fields)
                ),
                passes=False,
            )
        )

    def _append_fillet_limit_suite(
        *,
        weld_index: str,
        scope: str,
        size_symbol: str,
        length_symbol: str,
        weld_size: Quantity | None,
        weld_length: Quantity | None,
        thinner_part: Quantity | None,
        description_suffix: str,
        check_id_suffix: str,
    ) -> None:
        if weld_size is None or thinner_part is None:
            missing = []
            if weld_size is None:
                missing.append(size_symbol)
            if thinner_part is None:
                missing.append(f"t_delgado_w{weld_index}_{check_id_suffix}")
            _append_fillet_missing_limit(
                check_id=f"section_j2_4.weld_{weld_index}_minimum_size_{check_id_suffix}",
                scope=scope,
                description=f"Tamano minimo de soldadura de filete {description_suffix}",
                calculated_symbol=size_symbol,
                missing_fields=tuple(missing),
            )
        else:
            minimum_size = compute_fillet_weld_minimum_size_table_j24(
                thinner_part_thickness=thinner_part,
                unit_system=case.units_system,
            )["w_min"]
            weld_limits.append(
                _step1_limit(
                    check_id=f"section_j2_4.weld_{weld_index}_minimum_size_{check_id_suffix}",
                    scope=scope,
                    clause="AISC 360-22 Table J2.4",
                    description=f"Tamano minimo de soldadura de filete {description_suffix}",
                    calculated_symbol=size_symbol,
                    limit_symbol=f"wmin_j24_w{weld_index}_{check_id_suffix}",
                    calculated=weld_size,
                    limit=minimum_size,
                    comparison="ge",
                )
            )

        if weld_size is None or thinner_part is None:
            missing = []
            if weld_size is None:
                missing.append(size_symbol)
            if thinner_part is None:
                missing.append(f"t_delgado_w{weld_index}_{check_id_suffix}")
            _append_fillet_missing_limit(
                check_id=f"section_j2_b.weld_{weld_index}_maximum_size_{check_id_suffix}",
                scope=scope,
                description=f"Tamano maximo de soldadura de filete {description_suffix}",
                calculated_symbol=size_symbol,
                missing_fields=tuple(missing),
            )
        else:
            maximum_size = compute_fillet_weld_maximum_size_j2b(
                thinner_part_thickness=thinner_part,
                unit_system=case.units_system,
            )["w_max"]
            weld_limits.append(
                _step1_limit(
                    check_id=f"section_j2_b.weld_{weld_index}_maximum_size_{check_id_suffix}",
                    scope=scope,
                    clause="AISC 360-22 Section J2b",
                    description=f"Tamano maximo de soldadura de filete {description_suffix}",
                    calculated_symbol=size_symbol,
                    limit_symbol=f"wmax_j2b_w{weld_index}_{check_id_suffix}",
                    calculated=weld_size,
                    limit=maximum_size,
                    comparison="le",
                )
            )

        if weld_size is None or weld_length is None:
            missing = []
            if weld_size is None:
                missing.append(size_symbol)
            if weld_length is None:
                missing.append(length_symbol)
            _append_fillet_missing_limit(
                check_id=f"section_j2_2_c.weld_{weld_index}_minimum_length_{check_id_suffix}",
                scope=scope,
                description=f"Longitud minima de soldadura de filete para diseno por resistencia {description_suffix}",
                calculated_symbol=length_symbol,
                missing_fields=tuple(missing),
            )
            _append_fillet_missing_limit(
                check_id=f"section_j2_2_d.weld_{weld_index}_effective_length_{check_id_suffix}",
                scope=scope,
                description=f"Longitud efectiva de soldadura de filete cargada en el extremo {description_suffix}",
                calculated_symbol=length_symbol,
                missing_fields=tuple(missing),
            )
            return

        minimum_length = compute_fillet_weld_minimum_length_strength_j2c(
            weld_size=weld_size,
            weld_length=weld_length,
            unit_system=case.units_system,
        )["l_min"]
        weld_limits.append(
            _step1_limit(
                check_id=f"section_j2_2_c.weld_{weld_index}_minimum_length_{check_id_suffix}",
                scope=scope,
                clause="AISC 360-22 Section J2.2(c)",
                description=f"Longitud minima de soldadura de filete para diseno por resistencia {description_suffix}",
                calculated_symbol=length_symbol,
                limit_symbol=f"4*{size_symbol}",
                calculated=weld_length,
                limit=minimum_length,
                comparison="ge",
            )
        )

        effective_length_result = compute_end_loaded_fillet_weld_effective_length_j2d(
            weld_size=weld_size,
            weld_length=weld_length,
            unit_system=case.units_system,
        )
        l_over_w = effective_length_result["l_over_w"]
        beta = effective_length_result["beta"]
        l_eff = effective_length_result["l_eff"]
        passes_effective = beta > 0.0 and beta <= 1.0 + 1e-9
        weld_limits.append(
            _step1_verification_only_limit(
                check_id=f"section_j2_2_d.weld_{weld_index}_effective_length_{check_id_suffix}",
                scope=scope,
                clause="AISC 360-22 Section J2.2(d) + Eq. (J2-1)",
                description=f"Longitud efectiva de soldadura de filete cargada en el extremo {description_suffix}",
                calculated_symbol=length_symbol,
                verification_text=(
                    f"l/w = {l_over_w:.3f}; beta = {beta:.3f}; "
                    f"l_eff_w{weld_index}_{check_id_suffix} = {l_eff.value:.3f} {l_eff.unit}; "
                    "si l/w<=100 => l_eff=l; si 100<l/w<=300 => l_eff=beta*l; si l/w>300 => l_eff=180w"
                ),
                passes=passes_effective,
            )
        )

    def _append_plug_missing_limit(
        *,
        check_id: str,
        scope: str,
        description: str,
        calculated_symbol: str,
        missing_fields: tuple[str, ...],
    ) -> None:
        weld_limits.append(
            _step1_verification_only_limit(
                check_id=check_id,
                scope=scope,
                clause="AISC 360-22 Section J2.3b",
                description=description,
                calculated_symbol=calculated_symbol,
                verification_text=(
                    "Chequeo no evaluable por falta de datos requeridos para soldadura plug: "
                    + ", ".join(missing_fields)
                ),
                passes=False,
            )
        )

    def _append_plug_limit_suite(
        *,
        weld_index: str,
        scope: str,
        weld_size_symbol: str,
        hole_diameter_symbol: str,
        spacing_h_symbol: str,
        spacing_v_symbol: str,
        weld_size: Quantity | None,
        hole_diameter: Quantity | None,
        spacing_h: Quantity | None,
        spacing_v: Quantity | None,
        containing_part_thickness: Quantity | None,
        description_suffix: str,
        check_id_suffix: str,
    ) -> None:
        def _to_mm(q: Quantity | None) -> float | None:
            if q is None:
                return None
            if q.unit == "mm":
                return q.value
            if q.unit == "in":
                return q.value * 25.4
            return None

        # Clause (a) - hole diameter minimum and maximum limits.
        if weld_size is None or hole_diameter is None or containing_part_thickness is None:
            missing_a: list[str] = []
            if hole_diameter is None:
                missing_a.append(hole_diameter_symbol)
            if containing_part_thickness is None:
                missing_a.append(f"t_part_w{weld_index}_{check_id_suffix}")
            if weld_size is None:
                missing_a.append(weld_size_symbol)
            _append_plug_missing_limit(
                check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_minimum_{check_id_suffix}",
                scope=scope,
                description=f"Diametro minimo de hueco para soldadura plug {description_suffix}",
                calculated_symbol=hole_diameter_symbol,
                missing_fields=tuple(missing_a),
            )
            _append_plug_missing_limit(
                check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_maximum_{check_id_suffix}",
                scope=scope,
                description=f"Diametro maximo de hueco para soldadura plug {description_suffix}",
                calculated_symbol=hole_diameter_symbol,
                missing_fields=tuple(missing_a),
            )
        else:
            t_part_mm = _to_mm(containing_part_thickness)
            w_mm = _to_mm(weld_size)
            d_hole_mm = _to_mm(hole_diameter)
            if t_part_mm is None or w_mm is None or d_hole_mm is None:
                _append_plug_missing_limit(
                    check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_minimum_{check_id_suffix}",
                    scope=scope,
                    description=f"Diametro minimo de hueco para soldadura plug {description_suffix}",
                    calculated_symbol=hole_diameter_symbol,
                    missing_fields=("conversion_mm",),
                )
                _append_plug_missing_limit(
                    check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_maximum_{check_id_suffix}",
                    scope=scope,
                    description=f"Diametro maximo de hueco para soldadura plug {description_suffix}",
                    calculated_symbol=hole_diameter_symbol,
                    missing_fields=("conversion_mm",),
                )
            else:
                d_min_mm_unrounded = t_part_mm + 8.0
                d_min_mm = math.ceil(d_min_mm_unrounded / 2.0) * 2.0
                d_max_1_mm = d_min_mm + 3.0
                d_max_2_mm = 2.25 * w_mm
                # "A or B" interpreted as the more permissive governing upper limit in SI workflow.
                d_max_governing_mm = max(d_max_1_mm, d_max_2_mm)
                if hole_diameter.unit == "mm":
                    d_min_q = Quantity(value=d_min_mm, unit="mm")
                    d_max_q = Quantity(value=d_max_governing_mm, unit="mm")
                elif hole_diameter.unit == "in":
                    d_min_q = Quantity(value=d_min_mm / 25.4, unit="in")
                    d_max_q = Quantity(value=d_max_governing_mm / 25.4, unit="in")
                else:
                    d_min_q = None
                    d_max_q = None

                if d_min_q is None or d_max_q is None:
                    _append_plug_missing_limit(
                        check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_minimum_{check_id_suffix}",
                        scope=scope,
                        description=f"Diametro minimo de hueco para soldadura plug {description_suffix}",
                        calculated_symbol=hole_diameter_symbol,
                        missing_fields=("conversion_unidad",),
                    )
                    _append_plug_missing_limit(
                        check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_maximum_{check_id_suffix}",
                        scope=scope,
                        description=f"Diametro maximo de hueco para soldadura plug {description_suffix}",
                        calculated_symbol=hole_diameter_symbol,
                        missing_fields=("conversion_unidad",),
                    )
                else:
                    weld_limits.append(
                        _step1_limit(
                            check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_minimum_{check_id_suffix}",
                            scope=scope,
                            clause="AISC 360-22 Section J2.3b(a)",
                            description=f"Diametro minimo de hueco para soldadura plug {description_suffix}",
                            calculated_symbol=hole_diameter_symbol,
                            limit_symbol=f"redondeo_par(t_part_w{weld_index}_{check_id_suffix} + 8 mm)",
                            calculated=hole_diameter,
                            limit=d_min_q,
                            comparison="ge",
                        )
                    )
                    weld_limits.append(
                        _step1_limit(
                            check_id=f"section_j2_3b_a.weld_{weld_index}_hole_diameter_maximum_{check_id_suffix}",
                            scope=scope,
                            clause="AISC 360-22 Section J2.3b(a)",
                            description=f"Diametro maximo de hueco para soldadura plug {description_suffix}",
                            calculated_symbol=hole_diameter_symbol,
                            limit_symbol=f"max{{d_min+3 mm, 2.25*{weld_size_symbol}}}",
                            calculated=hole_diameter,
                            limit=d_max_q,
                            comparison="le",
                        )
                    )

        # Clause (b) - minimum center-to-center spacing.
        if hole_diameter is None or spacing_h is None or spacing_v is None:
            missing_b: list[str] = []
            if hole_diameter is None:
                missing_b.append(hole_diameter_symbol)
            if spacing_h is None:
                missing_b.append(spacing_h_symbol)
            if spacing_v is None:
                missing_b.append(spacing_v_symbol)
            _append_plug_missing_limit(
                check_id=f"section_j2_3b_b.weld_{weld_index}_minimum_center_spacing_{check_id_suffix}",
                scope=scope,
                description=f"Separacion minima centro a centro para soldadura plug {description_suffix}",
                calculated_symbol=f"min({spacing_h_symbol}, {spacing_v_symbol})",
                missing_fields=tuple(missing_b),
            )
        else:
            d_hole_mm = _to_mm(hole_diameter)
            sh_mm = _to_mm(spacing_h)
            sv_mm = _to_mm(spacing_v)
            if d_hole_mm is None or sh_mm is None or sv_mm is None:
                _append_plug_missing_limit(
                    check_id=f"section_j2_3b_b.weld_{weld_index}_minimum_center_spacing_{check_id_suffix}",
                    scope=scope,
                    description=f"Separacion minima centro a centro para soldadura plug {description_suffix}",
                    calculated_symbol=f"min({spacing_h_symbol}, {spacing_v_symbol})",
                    missing_fields=("conversion_mm",),
                )
            else:
                scc_min_mm = 4.0 * d_hole_mm
                passes_b = (sh_mm >= scc_min_mm - 1e-9) and (sv_mm >= scc_min_mm - 1e-9)
                weld_limits.append(
                    _step1_verification_only_limit(
                        check_id=f"section_j2_3b_b.weld_{weld_index}_minimum_center_spacing_{check_id_suffix}",
                        scope=scope,
                        clause="AISC 360-22 Section J2.3b(b)",
                        description=f"Separacion minima centro a centro para soldadura plug {description_suffix}",
                        calculated_symbol=f"min({spacing_h_symbol}, {spacing_v_symbol})",
                        verification_text=(
                            f"{spacing_h_symbol} >= 4*{hole_diameter_symbol} y {spacing_v_symbol} >= 4*{hole_diameter_symbol}; "
                            f"{spacing_h_symbol}={sh_mm:.3f} mm, {spacing_v_symbol}={sv_mm:.3f} mm, "
                            f"s_min={scc_min_mm:.3f} mm"
                        ),
                        passes=passes_b,
                    )
                )

        # Clause (h) - plug weld thickness vs containing-part thickness.
        if weld_size is None or containing_part_thickness is None:
            missing_h: list[str] = []
            if weld_size is None:
                missing_h.append(weld_size_symbol)
            if containing_part_thickness is None:
                missing_h.append(f"t_part_w{weld_index}_{check_id_suffix}")
            _append_plug_missing_limit(
                check_id=f"section_j2_3b_h.weld_{weld_index}_thickness_limits_{check_id_suffix}",
                scope=scope,
                description=f"Espesor de soldadura plug vs espesor de material {description_suffix}",
                calculated_symbol=weld_size_symbol,
                missing_fields=tuple(missing_h),
            )
        else:
            t_part_mm = _to_mm(containing_part_thickness)
            w_mm = _to_mm(weld_size)
            if t_part_mm is None or w_mm is None:
                _append_plug_missing_limit(
                    check_id=f"section_j2_3b_h.weld_{weld_index}_thickness_limits_{check_id_suffix}",
                    scope=scope,
                    description=f"Espesor de soldadura plug vs espesor de material {description_suffix}",
                    calculated_symbol=weld_size_symbol,
                    missing_fields=("conversion_mm",),
                )
            else:
                if t_part_mm <= 16.0 + 1e-9:
                    required_mm = t_part_mm
                    passes_h = abs(w_mm - required_mm) <= 1e-9
                    criteria_text = f"{weld_size_symbol} == t_part_w{weld_index}_{check_id_suffix}"
                else:
                    required_mm = max(0.5 * t_part_mm, 16.0)
                    passes_h = w_mm >= required_mm - 1e-9
                    criteria_text = (
                        f"{weld_size_symbol} >= max(0.5*t_part_w{weld_index}_{check_id_suffix}, 16 mm)"
                    )
                weld_limits.append(
                    _step1_verification_only_limit(
                        check_id=f"section_j2_3b_h.weld_{weld_index}_thickness_limits_{check_id_suffix}",
                        scope=scope,
                        clause="AISC 360-22 Section J2.3b(h)",
                        description=f"Espesor de soldadura plug vs espesor de material {description_suffix}",
                        calculated_symbol=weld_size_symbol,
                        verification_text=(
                            f"{criteria_text}; "
                            f"{weld_size_symbol}={w_mm:.3f} mm, "
                            f"t_part_w{weld_index}_{check_id_suffix}={t_part_mm:.3f} mm, "
                            f"requerido={required_mm:.3f} mm"
                        ),
                        passes=passes_h,
                    )
                )

    for side_suffix in _active_beam_sides(case):
        side_tag = f"vg{side_suffix}"
        side_label = "viga izquierda" if side_suffix == "izq" else "viga derecha"
        side_profile = _beam_profile_by_side(case, side_suffix)
        weld3_type = _normalize_end_plate_beam_web_weld_type(_geometry_by_side("end_plate_beam_web_weld_type", side_tag))
        weld_limits.append(
            _step1_text_in_set_limit(
                check_id=f"section_6_7.end_plate_beam_web_weld_type_allowed_{side_tag}",
                scope=f"weld_3_{side_tag}",
                clause="Section 6.7",
                description=(
                    "End-plate to beam-web weld type shall be an allowed category "
                    f"({'left beam' if side_suffix == 'izq' else 'right beam'})"
                ),
                calculated_symbol=f"weld_ep_web_{side_tag}",
                limit_symbol="{cjp, double_sided_fillet, single_sided_fillet}",
                calculated_text=weld3_type,
                allowed_values=("cjp", "double_sided_fillet", "single_sided_fillet"),
            )
        )

        end_plate_thickness_side = _geometry_by_side("end_plate_thickness", side_tag) or tp
        stiffener_thickness_side = _geometry_by_side("stiffener_thickness", side_tag)
        de_side = _geometry_by_side("de", side_tag) or de
        pfo_side = _geometry_by_side("pfo", side_tag) or pfo
        pfi_side = _geometry_by_side("pfi", side_tag) or pfi
        pb_side = _geometry_by_side("pb", side_tag) or pb
        clip_st_side = _stiffener_clip_distance(case.units_system)

        h_pest_side = (
            _derive_stiffener_height_from_de_pfo(de=de_side, pfo=pfo_side, pb=pb_side)
            if de_side is not None and pfo_side is not None
            else None
        )
        l_pest_side = (
            _derive_stiffener_length_from_hst(stiffener_height=h_pest_side, unit_system=case.units_system)
            if h_pest_side is not None
            else None
        )
        hwef_w3_side = (
            Quantity(value=pfi_side.value + pb_side.value + (150.0 / 25.4 if case.units_system == UnitSystem.US else 150.0), unit=pfi_side.unit)
            if pfi_side is not None and pb_side is not None
            else None
        )
        l_w4_side = side_profile["bf"] if side_profile is not None else None

        weld_contexts: list[dict[str, Any]] = [
            {
                "index": "1",
                "weld_name": "weld_1",
                "type_raw": _geometry_by_side("end_plate_stiffener_weld_type", side_tag),
                "size": _geometry_by_side("end_plate_stiffener_weld_size_wst", side_tag),
                "gap": _geometry_by_side("L_gap_w1", side_tag) or clip_st_side,
                "size_symbol": f"w_w1_{side_tag}",
                "length": (
                    Quantity(
                        value=h_pest_side.value
                        - 2.0 * ((_geometry_by_side("L_gap_w1", side_tag) or clip_st_side).value)
                        - clip_st_side.value,
                        unit=h_pest_side.unit,
                    )
                    if h_pest_side is not None and _geometry_by_side("end_plate_stiffener_weld_size_wst", side_tag) is not None
                    else None
                ),
                "length_symbol": f"l_w1_{side_tag}",
                "thinner_part": _minimum_thickness(stiffener_thickness_side, end_plate_thickness_side),
            },
            {
                "index": "2",
                "weld_name": "weld_2",
                "type_raw": _geometry_by_side("beam_stiffener_weld_type", side_tag)
                or _geometry_by_side("end_plate_stiffener_weld_type", side_tag),
                "size": _geometry_by_side("beam_stiffener_weld_size_wst2", side_tag)
                or _geometry_by_side("end_plate_stiffener_weld_size_wst", side_tag),
                "gap": _geometry_by_side("L_gap_w2", side_tag) or clip_st_side,
                "size_symbol": f"w_w2_{side_tag}",
                "length": (
                    Quantity(
                        value=l_pest_side.value
                        - 2.0 * ((_geometry_by_side("L_gap_w2", side_tag) or clip_st_side).value)
                        - clip_st_side.value,
                        unit=l_pest_side.unit,
                    )
                    if l_pest_side is not None
                    and (
                        _geometry_by_side("beam_stiffener_weld_size_wst2", side_tag)
                        or _geometry_by_side("end_plate_stiffener_weld_size_wst", side_tag)
                    )
                    is not None
                    else None
                ),
                "length_symbol": f"l_w2_{side_tag}",
                "thinner_part": _minimum_thickness(stiffener_thickness_side, side_profile["tw"] if side_profile is not None else None),
            },
            {
                "index": "3",
                "weld_name": "weld_3",
                "type_raw": _geometry_by_side("end_plate_beam_web_weld_type", side_tag),
                "size": _geometry_by_side("end_plate_beam_web_weld_thickness_twe", side_tag),
                "size_symbol": f"t_w3_{side_tag}",
                "length": hwef_w3_side,
                "length_symbol": f"hwef_w3_{side_tag}",
                "thinner_part": _minimum_thickness(end_plate_thickness_side, side_profile["tw"] if side_profile is not None else None),
            },
            {
                "index": "4",
                "weld_name": "weld_4",
                "type_raw": _geometry_by_side("tipo_w4", side_tag),
                "size": _geometry_by_side("t_w4", side_tag),
                "size_symbol": f"t_w4_{side_tag}",
                "length": l_w4_side,
                "length_symbol": f"l_w4_{side_tag}",
                "thinner_part": _minimum_thickness(end_plate_thickness_side, side_profile["tf"] if side_profile is not None else None),
            },
        ]

        # AISC 358-22 Section 6.7 (item 6): end-plate-to-stiffener joints shall be CJP.
        # Exception: if stiffener thickness <= 3/8 in (10 mm), fillet weld is permitted.
        weld1_type_raw = _geometry_by_side("end_plate_stiffener_weld_type", side_tag)
        weld1_type_normalized = _normalize_end_plate_stiffener_weld_type(weld1_type_raw)
        stiffener_weld_thickness_limit = Quantity(
            value=3.0 / 8.0 if case.units_system == UnitSystem.US else 10.0,
            unit="in" if case.units_system == UnitSystem.US else "mm",
        )
        if stiffener_thickness_side is None:
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id=f"section_6_7.weld_1_type_vs_stiffener_thickness_{side_tag}",
                    scope=f"weld_1_{side_tag}",
                    clause="Section 6.7 (item 6)",
                    description=f"Tipo de soldadura de end-plate con rigidizador segun espesor del rigidizador ({side_label})",
                    calculated_symbol=f"tipo_w1_{side_tag}",
                    verification_text=(
                        f"si t_pest_{side_tag} > {stiffener_weld_thickness_limit.value:.3f} {stiffener_weld_thickness_limit.unit}: "
                        f"tipo_w1_{side_tag} == cjp; "
                        f"dato faltante: t_pest_{side_tag}"
                    ),
                    passes=False,
                )
            )
        else:
            thin_stiffener = stiffener_thickness_side.value <= (stiffener_weld_thickness_limit.value + 1e-9)
            if thin_stiffener:
                passes_weld1_rule = weld1_type_normalized in {"cjp", "fillet"}
                verification_text = (
                    f"si t_pest_{side_tag} <= {stiffener_weld_thickness_limit.value:.3f} {stiffener_weld_thickness_limit.unit}: "
                    f"tipo_w1_{side_tag} in {{cjp, fillet}}; "
                    f"t_pest_{side_tag} = {stiffener_thickness_side.value:.3f} {stiffener_thickness_side.unit}; "
                    f"tipo_w1_{side_tag} = {weld1_type_normalized}"
                )
            else:
                passes_weld1_rule = weld1_type_normalized == "cjp"
                verification_text = (
                    f"si t_pest_{side_tag} > {stiffener_weld_thickness_limit.value:.3f} {stiffener_weld_thickness_limit.unit}: "
                    f"tipo_w1_{side_tag} == cjp; "
                    f"t_pest_{side_tag} = {stiffener_thickness_side.value:.3f} {stiffener_thickness_side.unit}; "
                    f"tipo_w1_{side_tag} = {weld1_type_normalized}"
                )
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id=f"section_6_7.weld_1_type_vs_stiffener_thickness_{side_tag}",
                    scope=f"weld_1_{side_tag}",
                    clause="Section 6.7 (item 6)",
                    description=f"Tipo de soldadura de end-plate con rigidizador segun espesor del rigidizador ({side_label})",
                    calculated_symbol=f"tipo_w1_{side_tag}",
                    verification_text=verification_text,
                    passes=passes_weld1_rule,
                )
            )

        weld2_type_raw = (
            _geometry_by_side("beam_stiffener_weld_type", side_tag)
            or _geometry_by_side("end_plate_stiffener_weld_type", side_tag)
        )
        weld2_type_normalized = _normalize_end_plate_stiffener_weld_type(weld2_type_raw)
        if stiffener_thickness_side is None:
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id=f"section_6_7.weld_2_type_vs_stiffener_thickness_{side_tag}",
                    scope=f"weld_2_{side_tag}",
                    clause="Section 6.7 (item 6)",
                    description=f"Tipo de soldadura de viga con rigidizador segun espesor del rigidizador ({side_label})",
                    calculated_symbol=f"tipo_w2_{side_tag}",
                    verification_text=(
                        f"si t_pest_{side_tag} > {stiffener_weld_thickness_limit.value:.3f} {stiffener_weld_thickness_limit.unit}: "
                        f"tipo_w2_{side_tag} == cjp; "
                        f"dato faltante: t_pest_{side_tag}"
                    ),
                    passes=False,
                )
            )
        else:
            thin_stiffener_w2 = stiffener_thickness_side.value <= (stiffener_weld_thickness_limit.value + 1e-9)
            if thin_stiffener_w2:
                passes_weld2_rule = weld2_type_normalized in {"cjp", "fillet"}
                verification_text_w2 = (
                    f"si t_pest_{side_tag} <= {stiffener_weld_thickness_limit.value:.3f} {stiffener_weld_thickness_limit.unit}: "
                    f"tipo_w2_{side_tag} in {{cjp, fillet}}; "
                    f"t_pest_{side_tag} = {stiffener_thickness_side.value:.3f} {stiffener_thickness_side.unit}; "
                    f"tipo_w2_{side_tag} = {weld2_type_normalized}"
                )
            else:
                passes_weld2_rule = weld2_type_normalized == "cjp"
                verification_text_w2 = (
                    f"si t_pest_{side_tag} > {stiffener_weld_thickness_limit.value:.3f} {stiffener_weld_thickness_limit.unit}: "
                    f"tipo_w2_{side_tag} == cjp; "
                    f"t_pest_{side_tag} = {stiffener_thickness_side.value:.3f} {stiffener_thickness_side.unit}; "
                    f"tipo_w2_{side_tag} = {weld2_type_normalized}"
                )
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id=f"section_6_7.weld_2_type_vs_stiffener_thickness_{side_tag}",
                    scope=f"weld_2_{side_tag}",
                    clause="Section 6.7 (item 6)",
                    description=f"Tipo de soldadura de viga con rigidizador segun espesor del rigidizador ({side_label})",
                    calculated_symbol=f"tipo_w2_{side_tag}",
                    verification_text=verification_text_w2,
                    passes=passes_weld2_rule,
                )
            )

        for weld_ctx in weld_contexts:
            weld_type_normalized = _normalize_end_plate_stiffener_weld_type(weld_ctx["type_raw"])
            if weld_type_normalized != "fillet":
                continue

            weld_index = weld_ctx["index"]
            weld_scope = f"weld_{weld_index}_{side_tag}"
            weld_size = weld_ctx["size"]
            weld_length = weld_ctx["length"]
            thinner_part = weld_ctx["thinner_part"]
            size_symbol = weld_ctx["size_symbol"]
            length_symbol = weld_ctx["length_symbol"]
            description_suffix = f"(#{weld_index}, {side_label})"
            _append_fillet_limit_suite(
                weld_index=weld_index,
                scope=weld_scope,
                size_symbol=size_symbol,
                length_symbol=length_symbol,
                weld_size=weld_size,
                weld_length=weld_length,
                thinner_part=thinner_part,
                description_suffix=description_suffix,
                check_id_suffix=side_tag,
            )
            if (
                weld_index == "1"
                and weld_length is not None
                and weld_size is not None
                and h_pest_side is not None
            ):
                if weld_size.unit == h_pest_side.unit:
                    w_size_for_limit = weld_size
                elif weld_size.unit == "mm" and h_pest_side.unit == "in":
                    w_size_for_limit = Quantity(value=weld_size.value / 25.4, unit="in")
                elif weld_size.unit == "in" and h_pest_side.unit == "mm":
                    w_size_for_limit = Quantity(value=weld_size.value * 25.4, unit="mm")
                else:
                    w_size_for_limit = None
                if w_size_for_limit is not None:
                    max_l_w1 = Quantity(
                        value=h_pest_side.value - 2.0 * w_size_for_limit.value,
                        unit=h_pest_side.unit,
                    )
                    weld_limits.append(
                        _step1_limit(
                            check_id=f"section_6_7.weld_1_fillet_length_max_{side_tag}",
                            scope=f"weld_1_{side_tag}",
                            clause="Section 6.7",
                            description=f"Longitud maxima de soldadura #1 cuando tipo_w1_{side_tag} es fillet ({side_label})",
                            calculated_symbol=f"l_w1_{side_tag}",
                            limit_symbol=f"h_pest_{side_tag} - 2*w_w1_{side_tag}",
                            calculated=weld_length,
                            limit=max_l_w1,
                            comparison="le",
                        )
                    )
            if (
                weld_index == "2"
                and weld_length is not None
                and weld_size is not None
                and l_pest_side is not None
            ):
                if weld_size.unit == l_pest_side.unit:
                    w_size_for_limit = weld_size
                elif weld_size.unit == "mm" and l_pest_side.unit == "in":
                    w_size_for_limit = Quantity(value=weld_size.value / 25.4, unit="in")
                elif weld_size.unit == "in" and l_pest_side.unit == "mm":
                    w_size_for_limit = Quantity(value=weld_size.value * 25.4, unit="mm")
                else:
                    w_size_for_limit = None
                if w_size_for_limit is not None:
                    max_l_w2 = Quantity(
                        value=l_pest_side.value - 2.0 * w_size_for_limit.value,
                        unit=l_pest_side.unit,
                    )
                    weld_limits.append(
                        _step1_limit(
                            check_id=f"section_6_7.weld_2_fillet_length_max_{side_tag}",
                            scope=f"weld_2_{side_tag}",
                            clause="Section 6.7",
                            description=f"Longitud maxima de soldadura #2 cuando tipo_w2_{side_tag} es fillet ({side_label})",
                            calculated_symbol=f"l_w2_{side_tag}",
                            limit_symbol=f"L_pest_{side_tag} - 2*w_w2_{side_tag}",
                            calculated=weld_length,
                            limit=max_l_w2,
                            comparison="le",
                        )
                    )

    # Reusable fillet-weld detailing checks for column weld scopes (#5 and #6).
    column_flange_thickness = column_profile.get("tf")
    column_web_thickness = column_profile.get("tw")

    weld5_type_norm = _normalize_end_plate_stiffener_weld_type(continuity_plate_weld_type_raw)
    if continuity_plate_enabled and tcp is not None and weld5_type_norm == "fillet":
        _append_fillet_limit_suite(
            weld_index="5",
            scope="weld_5_col",
            size_symbol="w_w5_col",
            length_symbol="L_w5_col",
            weld_size=w_w5_col,
            weld_length=l_w5_col_computed,
            thinner_part=_minimum_thickness(tcp, column_flange_thickness),
            description_suffix="(#5, columna)",
            check_id_suffix="col",
        )
        k1_col = column_profile.get("k1")
        tw_col = column_profile.get("tw")
        if (
            b1_pc_col is not None
            and w_w5_col is not None
            and l_w5_col_computed is not None
            and k1_col is not None
            and tw_col is not None
            and k1_col.unit == tw_col.unit == b1_pc_col.unit
        ):
            clip2_pc_col = Quantity(
                value=((k1_col.value - tw_col.value) / 2.0) + _mm_to_unit_value(12.0, k1_col.unit),
                unit=k1_col.unit,
            )
            clip2_pc_col = Quantity(
                value=_round_up_to_multiple_5mm(clip2_pc_col.value, clip2_pc_col.unit),
                unit=clip2_pc_col.unit,
            )
            b2_pc_col_local = Quantity(
                value=b1_pc_col.value - clip2_pc_col.value,
                unit=b1_pc_col.unit,
            )
            if w_w5_col.unit == b2_pc_col_local.unit:
                t_w5_for_limit = w_w5_col
            elif w_w5_col.unit == "mm" and b2_pc_col_local.unit == "in":
                t_w5_for_limit = Quantity(value=w_w5_col.value / 25.4, unit="in")
            elif w_w5_col.unit == "in" and b2_pc_col_local.unit == "mm":
                t_w5_for_limit = Quantity(value=w_w5_col.value * 25.4, unit="mm")
            else:
                t_w5_for_limit = None
            if t_w5_for_limit is not None:
                l_w5_max = Quantity(
                    value=b2_pc_col_local.value - 2.0 * t_w5_for_limit.value,
                    unit=b2_pc_col_local.unit,
                )
                weld_limits.append(
                    _step1_limit(
                        check_id="section_6_7.weld_5_fillet_length_max_col",
                        scope="weld_5_col",
                        clause="Section 6.7",
                        description="Longitud maxima de soldadura #5 cuando tipo_w5_col es fillet",
                        calculated_symbol="L_w5_col",
                        limit_symbol="b2_pc_col - 2*w_w5_col",
                        calculated=l_w5_col_computed,
                        limit=l_w5_max,
                        comparison="le",
                    )
                )

    if (
        continuity_plate_enabled
        and tcp is not None
        and continuity_plate_web_weld_type_raw is not None
        and str(continuity_plate_web_weld_type_raw).strip()
    ):
        weld_limits.append(
            _step1_text_in_set_limit(
                check_id="section_6_7.weld_6_type_allowed_col",
                scope="weld_6_col",
                clause="Section 6.7",
                description="Tipo de soldadura #6 permitido",
                calculated_symbol="tipo_w6_col",
                limit_symbol="{cjp, pjp, fillet}",
                calculated_text=weld6_type_norm,
                allowed_values=("cjp", "pjp", "fillet"),
            )
        )

    if continuity_plate_enabled and tcp is not None and weld6_type_norm == "fillet":
        _append_fillet_limit_suite(
            weld_index="6",
            scope="weld_6_col",
            size_symbol="w_w6_col",
            length_symbol="L_w6_col",
            weld_size=w_w6_col,
            weld_length=l_w6_col_computed,
            thinner_part=_minimum_thickness(tcp, column_web_thickness),
            description_suffix="(#6, columna)",
            check_id_suffix="col",
        )
        if (
            l2_pc_col_q is not None
            and w_w6_col is not None
            and l_w6_col_computed is not None
        ):
            if w_w6_col.unit == l2_pc_col_q.unit:
                w_w6_for_limit = w_w6_col
            elif w_w6_col.unit == "mm" and l2_pc_col_q.unit == "in":
                w_w6_for_limit = Quantity(value=w_w6_col.value / 25.4, unit="in")
            elif w_w6_col.unit == "in" and l2_pc_col_q.unit == "mm":
                w_w6_for_limit = Quantity(value=w_w6_col.value * 25.4, unit="mm")
            else:
                w_w6_for_limit = None
            if w_w6_for_limit is not None:
                l_w6_max = Quantity(
                    value=l2_pc_col_q.value - 2.0 * w_w6_for_limit.value,
                    unit=l2_pc_col_q.unit,
                )
                weld_limits.append(
                    _step1_limit(
                        check_id="section_6_7.weld_6_fillet_length_max_col",
                        scope="weld_6_col",
                        clause="Section 6.7",
                        description="Longitud maxima de soldadura #6 cuando tipo_w6_col es fillet",
                        calculated_symbol="L_w6_col",
                        limit_symbol="L2_pc_col - 2*w_w6_col",
                        calculated=l_w6_col_computed,
                        limit=l_w6_max,
                        comparison="le",
                        )
                    )

    sh_w7_col: Quantity | None = None
    sv_w7_col: Quantity | None = None
    nfilas_w7_col_local = case.geometry.nfilas_w7_col or case.geometry.doubler_plate_web_plug_weld_lines_nl
    ncolumna_w7_col_local = case.geometry.ncolumna_w7_col
    if (
        doubler_plate_enabled
        and bool(use_weld_7_col)
        and nfilas_w7_col_local
        and ncolumna_w7_col_local
    ):
        # Unificacion: sh_w7_col y sv_w7_col representan las mismas distancias
        # geometricas ya calculadas como b_w7_col y h_w7_col respectivamente.
        if b_w7_col is not None:
            sh_w7_col = b_w7_col
        elif b_dp_col is not None:
            sh_w7_col = Quantity(
                value=b_dp_col.value / float(ncolumna_w7_col_local + 1),
                unit=b_dp_col.unit,
            )

        if h_w7_col is not None:
            sv_w7_col = h_w7_col
        else:
            sv_candidates: list[Quantity] = []
            if beam_connection_sides in {"both_sides", "right_only"} and beam_profile_der is not None:
                d_der_q = beam_profile_der["d"]
                tf_der_q = beam_profile_der["tf"]
                sv_candidates.append(Quantity(value=d_der_q.value - 2.0 * tf_der_q.value, unit=d_der_q.unit))
            if beam_connection_sides in {"both_sides", "left_only"} and beam_profile_izq is not None:
                d_izq_q = beam_profile_izq["d"]
                tf_izq_q = beam_profile_izq["tf"]
                sv_candidates.append(Quantity(value=d_izq_q.value - 2.0 * tf_izq_q.value, unit=d_izq_q.unit))
            if sv_candidates:
                base_unit = sv_candidates[0].unit
                sv_converted: list[Quantity] = []
                for sv_q in sv_candidates:
                    sv_q_conv = _to_unit_length_local(sv_q, base_unit)
                    if sv_q_conv is not None:
                        sv_converted.append(sv_q_conv)
                if sv_converted:
                    sv_max = max(sv_converted, key=lambda x: x.value)
                    sv_w7_col = Quantity(
                        value=sv_max.value / float(nfilas_w7_col_local + 1),
                        unit=base_unit,
                    )

    if (
        doubler_plate_enabled
        and bool(use_weld_7_col)
        and weld7_type_norm == "plug"
    ):
        spacing_h_for_plug = b_w7_col or sh_w7_col
        spacing_v_for_plug = h_w7_col or sv_w7_col
        _append_plug_limit_suite(
            weld_index="7",
            scope="weld_7_col",
            weld_size_symbol="w_w7_col",
            hole_diameter_symbol="d_hole_w7_col",
            spacing_h_symbol="b_w7_col",
            spacing_v_symbol="h_w7_col",
            weld_size=w_w7_col,
            hole_diameter=d_hole_w7_col,
            spacing_h=spacing_h_for_plug,
            spacing_v=spacing_v_for_plug,
            containing_part_thickness=tcp,
            description_suffix="(#7, columna)",
            check_id_suffix="col",
        )

    weld8_type_norm = _normalize_end_plate_stiffener_weld_type(weld_8_type_raw)
    encr_w8_col: Quantity | None = None
    encr_w8_source: str | None = None
    gap_dp_col_mm: float | None = None
    weld8_contact_state_col: str | None = None
    weld8_in_contact_with_web: bool | None = None
    if gap_dp_col is not None:
        if gap_dp_col.unit == "mm":
            gap_dp_col_mm = gap_dp_col.value
        elif gap_dp_col.unit == "in":
            gap_dp_col_mm = gap_dp_col.value * 25.4
        if gap_dp_col_mm is not None:
            weld8_in_contact_with_web = gap_dp_col_mm <= 2.0 + 1e-9
            weld8_contact_state_col = (
                "en_contacto_con_alma"
                if weld8_in_contact_with_web
                else "sin_contacto_con_alma"
            )
    if doubler_plate_enabled:
        weld_limits.append(
            _step1_verification_only_limit(
                check_id="section_6_7.weld_8_gap_contact_classification_col",
                scope="weld_8_col",
                clause="design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                description="Clasificacion de contacto entre platina de enchape y alma de columna segun gap_dp_col",
                calculated_symbol="gap_dp_col",
                verification_text=(
                    "si gap_dp_col <= 2.0 mm => en_contacto_con_alma; "
                    "si gap_dp_col > 2.0 mm => sin_contacto_con_alma; "
                    f"gap_dp_col = {gap_dp_col.value:.3f} {gap_dp_col.unit}, "
                    f"estado = {weld8_contact_state_col}"
                )
                if gap_dp_col is not None and weld8_contact_state_col is not None
                else "gap_dp_col no definido; no se puede clasificar contacto con el alma",
                passes=gap_dp_col is not None and weld8_contact_state_col is not None,
            )
        )
    if (
        doubler_plate_enabled
        and weld_8_type_raw is not None
        and str(weld_8_type_raw).strip()
    ):
        weld8_type_description = "Tipo de soldadura #8 permitido"
        if weld8_in_contact_with_web is True:
            weld8_allowed_types = ("fillet", "pjp")
            weld8_limit_symbol = "{fillet, pjp}"
        else:
            weld8_allowed_types = ("cjp", "pjp", "fillet")
            weld8_limit_symbol = "{cjp, pjp, fillet}"
        weld_limits.append(
            _step1_text_in_set_limit(
                check_id="section_6_7.weld_8_type_allowed_col",
                scope="weld_8_col",
                clause="AISC 341-22w E3.6e.3",
                description=weld8_type_description,
                calculated_symbol="tipo_w8_col",
                limit_symbol=weld8_limit_symbol,
                calculated_text=weld8_type_norm,
                allowed_values=weld8_allowed_types,
            )
        )

    if (
        doubler_plate_enabled
        and weld_8_type_raw is not None
        and str(weld_8_type_raw).strip()
    ):
        kdet_col_for_encr = column_profile.get("kdet") or column_profile.get("kdes")
        tf_col_for_encr = column_profile.get("tf")
        if (
            kdet_col_for_encr is not None
            and tf_col_for_encr is not None
            and kdet_col_for_encr.unit == tf_col_for_encr.unit
        ):
            encr_w8_col, encr_w8_source = _compute_encr_w8_from_aisc_16_figure_10_3(
                kdet_col=kdet_col_for_encr,
                tf_col=tf_col_for_encr,
            )
        else:
            encr_w8_col = None
            encr_w8_source = "no_se_pudo_evaluar_kdet_col_y_tf_col"

        weld_limits.append(
            _step1_verification_only_limit(
                check_id="section_6_7.weld_8_encr_from_figure_10_3_col",
                scope="weld_8_col",
                clause="Steel Construction Manual AISC 16th Edition 2023 Figure 10-3",
                description="Determinacion automatica de Encr para soldadura #8",
                calculated_symbol="Encr_w8_col",
                verification_text=(
                    f"Encr_w8_col calculado correctamente: {encr_w8_col.value:.3f} {encr_w8_col.unit}; "
                    f"fuente={encr_w8_source}"
                )
                if encr_w8_col is not None
                else (
                    "No se pudo determinar Encr_w8_col desde Figura 10-3; "
                    f"detalle={encr_w8_source}"
                ),
                passes=encr_w8_col is not None,
            )
        )

    if (
        doubler_plate_enabled
        and weld8_type_norm == "fillet"
        and case.geometry.doubler_plate_thickness is not None
        and encr_w8_col is not None
    ):
        # For this DG13 fillet-thickness check, prioritize kdes as requested by user.
        kdet_col = column_profile.get("kdes") or column_profile.get("kdet")
        tf_col = column_profile.get("tf")
        t_dp_col = case.geometry.doubler_plate_thickness
        if kdet_col is not None and tf_col is not None:
            encr_for_limit = _convert_length_quantity(encr_w8_col, kdet_col.unit)
            if (
                encr_for_limit is not None
                and tf_col.unit == kdet_col.unit
                and t_dp_col.unit == kdet_col.unit
            ):
                tdp_min = Quantity(
                    value=kdet_col.value - tf_col.value - encr_for_limit.value,
                    unit=kdet_col.unit,
                )
                weld_limits.append(
                    _step1_limit(
                        check_id="section_6_7.weld_8_doubler_plate_thickness_min_col",
                        scope="doubler_plate_col",
                        clause="design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                        description="Espesor minimo de platina de enchape cuando soldadura #8 es fillet",
                        calculated_symbol="t_dp_col",
                        limit_symbol="kdet_col - tf_col - Encr_w8_col",
                        calculated=t_dp_col,
                        limit=tdp_min,
                        comparison="ge",
                    )
                )

    if doubler_plate_enabled and weld8_type_norm == "fillet":
        _append_fillet_limit_suite(
            weld_index="8",
            scope="weld_8_col",
            size_symbol="w_w8_col",
            length_symbol="L_w8_col",
            weld_size=w_w8_col,
            weld_length=l_w8_col_computed,
            thinner_part=_minimum_thickness(case.geometry.doubler_plate_thickness, tft_col_q),
            description_suffix="(#8, columna)",
            check_id_suffix="col",
        )

    weld9_type_norm = _normalize_end_plate_stiffener_weld_type(weld_9_type_raw)
    if bool(use_weld_9_col):
        weld_limits.append(
            _step1_text_in_set_limit(
                check_id="section_6_7.weld_9_type_allowed_when_used_col",
                scope="doubler_plate_col",
                clause="AISC 341-22w E3.6e.3",
                description="Tipo de soldadura #9 permitido (usar_weld_9_col=true)",
                calculated_symbol="tipo_w9_col",
                limit_symbol="{fillet}",
                calculated_text=weld9_type_norm,
                allowed_values=("fillet",),
            )
        )
        if weld9_type_norm == "fillet":
            _append_fillet_limit_suite(
                weld_index="9",
                scope="doubler_plate_col",
                size_symbol="w_w9_col",
                length_symbol="L_w9_col",
                weld_size=w_w9_col,
                weld_length=l_w9_col_computed,
                thinner_part=_minimum_thickness(case.geometry.doubler_plate_thickness, column_profile.get("tw")),
                description_suffix="(#9, columna)",
                check_id_suffix="col",
            )
            kdet_col = column_profile.get("kdet") or column_profile.get("kdes")
            d_col = column_profile.get("d")
            if (
                l_w9_col_computed is not None
                and w_w9_col is not None
                and d_col is not None
                and kdet_col is not None
            ):
                kdet_for_limit = _convert_length_quantity(kdet_col, d_col.unit)
                if kdet_for_limit is not None:
                    l_w9_max = Quantity(
                        value=d_col.value - 2.0 * kdet_for_limit.value - 2.0 * _mm_to_unit_value(38.0, d_col.unit),
                        unit=d_col.unit,
                    )
                    weld_limits.append(
                        _step1_limit(
                            check_id="section_6_7.weld_9_length_max_col",
                            scope="doubler_plate_col",
                            clause="Section 6.7",
                            description="Longitud maxima de soldadura #9 cuando tipo_w9_col es fillet",
                            calculated_symbol="L_w9_col",
                            limit_symbol="d_col - 2*kdet_col - 2*38 mm",
                            calculated=l_w9_col_computed,
                            limit=l_w9_max,
                            comparison="le",
                        )
                    )
                else:
                    _append_fillet_missing_limit(
                        check_id="section_6_7.weld_9_length_max_col",
                        scope="doubler_plate_col",
                        description="Longitud maxima de soldadura #9 cuando tipo_w9_col es fillet",
                        calculated_symbol="L_w9_col",
                        missing_fields=("kdet_col",),
                    )
            else:
                _append_fillet_missing_limit(
                    check_id="section_6_7.weld_9_length_max_col",
                    scope="doubler_plate_col",
                    description="Longitud maxima de soldadura #9 cuando tipo_w9_col es fillet",
                    calculated_symbol="L_w9_col",
                    missing_fields=("L_w9_col", "w_w9_col", "d_col", "kdet_col"),
                )

    # Checks requested for scope 3.26 (WELD_9_COL):
    # Apply only when extended_dp_col=true and usar_pc_col=false.
    # 1) if gap_dp_col<=2.0mm and t_dp_col>=((d_col-2*tf_col)+max{d_lado-2*tf_lado})/90 => use_weld_9_col must be true
    #    otherwise use_weld_9_col must be false.
    # 2) same logic replacing t_dp_col with tw_col.
    if (
        doubler_plate_enabled
        and bool(case.geometry.extended_dp_col)
        and (not continuity_plate_enabled)
        and bool(use_weld_9_col)
    ):
        d_beam_net_candidates_w9: list[Quantity] = []
        if beam_connection_sides in {"both_sides", "left_only"} and beam_profile_izq is not None:
            d_beam_net_candidates_w9.append(
                Quantity(
                    value=beam_profile_izq["d"].value - 2.0 * beam_profile_izq["tf"].value,
                    unit=beam_profile_izq["d"].unit,
                )
            )
        if beam_connection_sides in {"both_sides", "right_only"}:
            d_beam_net_candidates_w9.append(
                Quantity(
                    value=beam_profile_der["d"].value - 2.0 * beam_profile_der["tf"].value,
                    unit=beam_profile_der["d"].unit,
                )
            )

        base_unit_w9 = column_profile["tw"].unit
        d_col_conv_w9 = _to_unit_length_local(column_profile["d"], base_unit_w9)
        tf_col_conv_w9 = _to_unit_length_local(column_profile["tf"], base_unit_w9)
        tw_col_conv_w9 = _to_unit_length_local(column_profile["tw"], base_unit_w9)
        t_dp_col_conv_w9 = (
            _to_unit_length_local(case.geometry.doubler_plate_thickness, base_unit_w9)
            if case.geometry.doubler_plate_thickness is not None
            else None
        )
        gap_dp_mm_w9: float | None = None
        if gap_dp_col is not None:
            gap_dp_conv_mm = _to_unit_length_local(gap_dp_col, "mm")
            if gap_dp_conv_mm is not None:
                gap_dp_mm_w9 = gap_dp_conv_mm.value

        d_beam_nets_conv_w9: list[Quantity] = []
        for q in d_beam_net_candidates_w9:
            q_conv = _to_unit_length_local(q, base_unit_w9)
            if q_conv is not None:
                d_beam_nets_conv_w9.append(q_conv)

        rhs_w9_q: Quantity | None = None
        if d_col_conv_w9 is not None and tf_col_conv_w9 is not None and d_beam_nets_conv_w9:
            rhs_w9_q = Quantity(
                value=(
                    d_col_conv_w9.value
                    - 2.0 * tf_col_conv_w9.value
                    + max(d_beam_nets_conv_w9, key=lambda x: x.value).value
                )
                / 90.0,
                unit=base_unit_w9,
            )

        use_w9_input_bool = bool(use_weld_9_col)

        # Check 1: threshold with t_dp_col
        if rhs_w9_q is not None and t_dp_col_conv_w9 is not None and gap_dp_mm_w9 is not None:
            cond1 = (gap_dp_mm_w9 <= 2.0 + 1e-9) and (t_dp_col_conv_w9.value >= rhs_w9_q.value)
            expected_use_w9_1 = cond1
            passes_use_w9_1 = use_w9_input_bool == expected_use_w9_1
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id="section_dg13.weld_9_required_by_gap_and_t_dp_col",
                    scope="weld_9_col",
                    clause="AISC 341-22w E3.6e.3 + design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                    description="Uso de soldadura #9 segun gap_dp_col y umbral con t_dp_col",
                    calculated_symbol="use_weld_9_col",
                    verification_text=(
                        f"si gap_dp_col<=2.0mm y t_dp_col>=(d_col-2*tf_col+max{{d_lado-2*tf_lado}})/90 "
                        f"=> use_weld_9_col=true; en caso contrario false. "
                        f"gap_dp_col={gap_dp_mm_w9:.3f} mm, "
                        f"t_dp_col={t_dp_col_conv_w9.value:.3f} {t_dp_col_conv_w9.unit}, "
                        f"umbral={rhs_w9_q.value:.3f} {rhs_w9_q.unit}, "
                        f"condicion={str(cond1).lower()}, "
                        f"use_weld_9_col(input)={str(use_w9_input_bool).lower()}, "
                        f"use_weld_9_col(esperado)={str(expected_use_w9_1).lower()}"
                    ),
                    passes=passes_use_w9_1,
                )
            )
        else:
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id="section_dg13.weld_9_required_by_gap_and_t_dp_col",
                    scope="weld_9_col",
                    clause="AISC 341-22w E3.6e.3 + design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                    description="Uso de soldadura #9 segun gap_dp_col y umbral con t_dp_col",
                    calculated_symbol="use_weld_9_col",
                    verification_text=(
                        "No se pudo evaluar el chequeo por datos faltantes/invalidos: "
                        f"gap_dp_col={gap_dp_col is not None}, "
                        f"t_dp_col={case.geometry.doubler_plate_thickness is not None}, "
                        f"rhs={(rhs_w9_q is not None)}"
                    ),
                    passes=False,
                )
            )
        # Check 2: threshold with tw_col
        if rhs_w9_q is not None and tw_col_conv_w9 is not None and gap_dp_mm_w9 is not None:
            cond2 = (gap_dp_mm_w9 <= 2.0 + 1e-9) and (tw_col_conv_w9.value >= rhs_w9_q.value)
            expected_use_w9_2 = cond2
            passes_use_w9_2 = use_w9_input_bool == expected_use_w9_2
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id="section_dg13.weld_9_required_by_gap_and_tw_col",
                    scope="weld_9_col",
                    clause="AISC 341-22w E3.6e.3 + design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                    description="Uso de soldadura #9 segun gap_dp_col y umbral con tw_col",
                    calculated_symbol="use_weld_9_col",
                    verification_text=(
                        f"si gap_dp_col<=2.0mm y tw_col>=(d_col-2*tf_col+max{{d_lado-2*tf_lado}})/90 "
                        f"=> use_weld_9_col=true; en caso contrario false. "
                        f"gap_dp_col={gap_dp_mm_w9:.3f} mm, "
                        f"tw_col={tw_col_conv_w9.value:.3f} {tw_col_conv_w9.unit}, "
                        f"umbral={rhs_w9_q.value:.3f} {rhs_w9_q.unit}, "
                        f"condicion={str(cond2).lower()}, "
                        f"use_weld_9_col(input)={str(use_w9_input_bool).lower()}, "
                        f"use_weld_9_col(esperado)={str(expected_use_w9_2).lower()}"
                    ),
                    passes=passes_use_w9_2,
                )
            )
        else:
            weld_limits.append(
                _step1_verification_only_limit(
                    check_id="section_dg13.weld_9_required_by_gap_and_tw_col",
                    scope="weld_9_col",
                    clause="AISC 341-22w E3.6e.3 + design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                    description="Uso de soldadura #9 segun gap_dp_col y umbral con tw_col",
                    calculated_symbol="use_weld_9_col",
                    verification_text=(
                        "No se pudo evaluar el chequeo por datos faltantes/invalidos: "
                        f"gap_dp_col={gap_dp_col is not None}, "
                        f"tw_col={(column_profile.get('tw') is not None)}, "
                        f"rhs={(rhs_w9_q is not None)}"
                    ),
                    passes=False,
                )
            )
    elif doubler_plate_enabled and bool(use_weld_9_col):
        weld_limits.append(
            _step1_verification_only_limit(
                check_id="section_dg13.weld_9_activation_not_applicable_note",
                scope="weld_9_col",
                clause="AISC 341-22w E3.6e.3 + design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                description="Chequeos de activacion de soldadura #9",
                calculated_symbol="use_weld_9_col",
                verification_text=(
                    "No aplica: estos chequeos solo aplican cuando "
                    "extended_dp_col=true y usar_pc_col=false; "
                    f"extended_dp_col={str(bool(case.geometry.extended_dp_col)).lower()}, "
                    f"usar_pc_col={str(bool(continuity_plate_enabled)).lower()}"
                ),
                passes=True,
            )
        )

    # Design Guide 13 check for low ductility:
    # if usar_weld_7_col=false -> t_dp_col >= (d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78
    # if usar_weld_7_col=true  -> t_dp_col + tw_col >= (d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78
    if (
        doubler_plate_enabled
        and str(column_ductility).strip().lower() == "low"
        and case.geometry.doubler_plate_thickness is not None
    ):
        d_col = column_profile.get("d")
        kdet_col = column_profile.get("kdet") or column_profile.get("kdes")
        tw_col = column_profile.get("tw")
        t_dp_col = case.geometry.doubler_plate_thickness
        tipo_acero_dp_col = case.materials.doubler_plate_steel_type
        if d_col is not None and kdet_col is not None and tw_col is not None and tipo_acero_dp_col is not None:
            plate_props_dp = get_plate_steel_properties(
                steel_type=str(tipo_acero_dp_col),
                unit_system=case.units_system,
            )
            fy_dp_col = plate_props_dp["fy"]

            def _to_mm(q: Quantity) -> float | None:
                if q.unit == "mm":
                    return q.value
                if q.unit == "in":
                    return q.value * 25.4
                return None

            def _to_mpa(q: Quantity) -> float | None:
                if q.unit == "MPa":
                    return q.value
                if q.unit == "ksi":
                    return q.value * 6.894757293168361
                return None

            d_col_mm = _to_mm(d_col)
            kdet_col_mm = _to_mm(kdet_col)
            tw_col_mm = _to_mm(tw_col)
            t_dp_col_mm = _to_mm(t_dp_col)
            fy_dp_col_mpa = _to_mpa(fy_dp_col) if isinstance(fy_dp_col, Quantity) else None

            if (
                d_col_mm is not None
                and kdet_col_mm is not None
                and tw_col_mm is not None
                and t_dp_col_mm is not None
                and fy_dp_col_mpa is not None
                and fy_dp_col_mpa >= 0.0
            ):
                rhs_mm_value = (d_col_mm - 2.0 * kdet_col_mm) * math.sqrt(fy_dp_col_mpa) / 1136.78
                rhs_q = Quantity(
                    value=rhs_mm_value if t_dp_col.unit == "mm" else rhs_mm_value / 25.4,
                    unit=t_dp_col.unit,
                )
                use_w7 = bool(use_weld_7_col)
                if use_w7:
                    tw_for_calc = tw_col if tw_col.unit == t_dp_col.unit else (
                        Quantity(value=tw_col.value * 25.4, unit="mm")
                        if tw_col.unit == "in" and t_dp_col.unit == "mm"
                        else (
                            Quantity(value=tw_col.value / 25.4, unit="in")
                            if tw_col.unit == "mm" and t_dp_col.unit == "in"
                            else None
                        )
                    )
                    if tw_for_calc is not None:
                        lhs_q = Quantity(
                            value=t_dp_col.value + tw_for_calc.value,
                            unit=t_dp_col.unit,
                        )
                        weld_limits.append(
                            _step1_limit(
                                check_id="section_dg13.weld_8_doubler_plate_thickness_low_ductility_with_w7",
                                scope="doubler_plate_col",
                                clause="design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                                description="Espesor minimo con soldadura #7 habilitada (ductilidad baja)",
                                calculated_symbol="t_dp_col + tw_col",
                                limit_symbol="(d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78",
                                calculated=lhs_q,
                                limit=rhs_q,
                                comparison="ge",
                            )
                        )
                else:
                    weld_limits.append(
                        _step1_limit(
                            check_id="section_dg13.weld_8_doubler_plate_thickness_low_ductility_without_w7",
                            scope="doubler_plate_col",
                            clause="design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                            description="Espesor minimo sin soldadura #7 habilitada (ductilidad baja)",
                            calculated_symbol="t_dp_col",
                            limit_symbol="(d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78",
                            calculated=t_dp_col,
                            limit=rhs_q,
                            comparison="ge",
                        )
                    )

    # Design Guide 13 check for moderate/high ductility (requested formulation):
    # if usar_weld_7_col=true  -> t_dp_col >= (d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78
    # if usar_weld_7_col=false -> t_dp_col + tw_col >= (d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78
    if (
        doubler_plate_enabled
        and str(column_ductility).strip().lower() in {"moderate", "high"}
        and case.geometry.doubler_plate_thickness is not None
    ):
        d_col = column_profile.get("d")
        kdet_col = column_profile.get("kdet") or column_profile.get("kdes")
        tw_col = column_profile.get("tw")
        t_dp_col = case.geometry.doubler_plate_thickness
        tipo_acero_dp_col = case.materials.doubler_plate_steel_type
        if d_col is not None and kdet_col is not None and tw_col is not None and tipo_acero_dp_col is not None:
            plate_props_dp = get_plate_steel_properties(
                steel_type=str(tipo_acero_dp_col),
                unit_system=case.units_system,
            )
            fy_dp_col = plate_props_dp["fy"]

            def _to_mm_mod_high(q: Quantity) -> float | None:
                if q.unit == "mm":
                    return q.value
                if q.unit == "in":
                    return q.value * 25.4
                return None

            def _to_mpa_mod_high(q: Quantity) -> float | None:
                if q.unit == "MPa":
                    return q.value
                if q.unit == "ksi":
                    return q.value * 6.894757293168361
                return None

            d_col_mm = _to_mm_mod_high(d_col)
            kdet_col_mm = _to_mm_mod_high(kdet_col)
            tw_col_mm = _to_mm_mod_high(tw_col)
            t_dp_col_mm = _to_mm_mod_high(t_dp_col)
            fy_dp_col_mpa = _to_mpa_mod_high(fy_dp_col) if isinstance(fy_dp_col, Quantity) else None

            if (
                d_col_mm is not None
                and kdet_col_mm is not None
                and tw_col_mm is not None
                and t_dp_col_mm is not None
                and fy_dp_col_mpa is not None
                and fy_dp_col_mpa >= 0.0
            ):
                rhs_mm_value = (d_col_mm - 2.0 * kdet_col_mm) * math.sqrt(fy_dp_col_mpa) / 1136.78
                rhs_q = Quantity(
                    value=rhs_mm_value if t_dp_col.unit == "mm" else rhs_mm_value / 25.4,
                    unit=t_dp_col.unit,
                )
                use_w7 = bool(use_weld_7_col)
                if use_w7:
                    weld_limits.append(
                        _step1_limit(
                            check_id="section_dg13.weld_8_doubler_plate_thickness_mod_high_with_w7",
                            scope="doubler_plate_col",
                            clause="design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                            description="Espesor minimo con soldadura #7 habilitada (ductilidad moderada/alta)",
                            calculated_symbol="t_dp_col",
                            limit_symbol="(d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78",
                            calculated=t_dp_col,
                            limit=rhs_q,
                            comparison="ge",
                        )
                    )
                else:
                    tw_for_calc = tw_col if tw_col.unit == t_dp_col.unit else (
                        Quantity(value=tw_col.value * 25.4, unit="mm")
                        if tw_col.unit == "in" and t_dp_col.unit == "mm"
                        else (
                            Quantity(value=tw_col.value / 25.4, unit="in")
                            if tw_col.unit == "mm" and t_dp_col.unit == "in"
                            else None
                        )
                    )
                    if tw_for_calc is not None:
                        lhs_q = Quantity(
                            value=t_dp_col.value + tw_for_calc.value,
                            unit=t_dp_col.unit,
                        )
                        weld_limits.append(
                            _step1_limit(
                                check_id="section_dg13.weld_8_doubler_plate_thickness_mod_high_without_w7",
                                scope="doubler_plate_col",
                                clause="design-guide-13--wide-flange-column-stiffening-at-moment-connections",
                                description="Espesor minimo sin soldadura #7 habilitada (ductilidad moderada/alta)",
                                calculated_symbol="t_dp_col + tw_col",
                                limit_symbol="(d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78",
                                calculated=lhs_q,
                                limit=rhs_q,
                                comparison="ge",
                            )
                        )

    required_bolt_standards = (
        "ASTM F3125/F3125M",
        "ASTM A325",
        "ASTM A325M",
        "ASTM A490",
        "ASTM A490M",
        "ASTM F1852",
        "ASTM F2280",
    )
    bolt_limits: list[dict[str, Any]] = []
    for side_tag in _active_beam_sides(case):
        side_scope = f"bolts_{side_tag}"
        side_symbol = f"vg{side_tag}"
        side_label = "right beam" if side_tag == "der" else "left beam"
        bolt_tightening_type_side = _get_geometry_by_side("bolt_tightening_type", side_tag)
        tightening_type_normalized = _normalize_bolt_tightening(str(bolt_tightening_type_side))
        bolt_fabrication_standard_side = _get_material_by_side("bolt_fabrication_standard", side_tag)
        bolt_standard_text = str(bolt_fabrication_standard_side or "not_provided")
        bolt_limits.extend(
            [
                _step1_text_in_set_limit(
                    check_id=f"section_4_1.bolt_tightening_type_valid_{side_tag}",
                    scope=side_scope,
                    clause="Section 4.1 FASTENER ASSEMBLIES",
                    description=f"Bolt tightening type must be one recognized category ({side_label})",
                    calculated_symbol=f"tight_bolt_{side_symbol}",
                    limit_symbol="{pretensioned, snug_tight}",
                    calculated_text=tightening_type_normalized,
                    allowed_values=("pretensioned", "snug_tight"),
                ),
                _step1_text_limit(
                    check_id=f"section_4_1.bolt_tightening_required_pretensioned_{side_tag}",
                    scope=side_scope,
                    clause="Section 4.1 FASTENER ASSEMBLIES",
                    description=f"Bolts shall be pretensioned unless a specific connection permits otherwise ({side_label})",
                    calculated_symbol=f"tight_bolt_{side_symbol}",
                    limit_symbol="pretensioned",
                    calculated_text=tightening_type_normalized,
                    expected_text="pretensioned",
                ),
                _step1_text_in_set_limit(
                    check_id=f"section_4_1.bolt_fabrication_standard_permitted_{side_tag}",
                    scope=side_scope,
                    clause="Section 4.1 FASTENER ASSEMBLIES",
                    description=f"Bolt fabrication standard must be an allowed high-strength ASTM designation ({side_label})",
                    calculated_symbol=f"std_bolt_{side_symbol}",
                    limit_symbol="{ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}",
                    calculated_text=bolt_standard_text,
                    allowed_values=required_bolt_standards,
                    normalizer=_normalize_bolt_standard,
                ),
            ]
        )

    pfo_bounds = active_table_61.get("pfo")
    pfi_bounds = active_table_61.get("pfi")
    table_61_checks: list[dict[str, Any]] = []
    side_entries: list[tuple[str, str, dict[str, Quantity]]] = [("der", "table_6_1_der", beam_profile_der)]
    if beam_connection_sides == "both_sides" and beam_profile_izq is not None:
        side_entries.append(("izq", "table_6_1_izq", beam_profile_izq))

    for side_tag, side_scope, side_profile in side_entries:
        side_suffix = f"vg{side_tag}"
        side_label = "right beam" if side_tag == "der" else "left beam"
        if side_tag == "der":
            de_side = de_der
            pfo_side = pfo_der
            pfi_side = pfi_der
            pb_side = pb_der
            g_side = g_der
            db_side = db_der
            min_edge_side = min_edge_der
            min_spacing_side = min_spacing_der
            bp_side = bp_der
            tp_side = tp_der
        else:
            de_side = de_izq
            pfo_side = pfo_izq
            pfi_side = pfi_izq
            pb_side = pb_izq
            g_side = g_izq
            db_side = db_izq
            min_edge_side = min_edge_izq
            min_spacing_side = min_spacing_izq
            bp_side = bp_izq
            tp_side = tp_izq
        if db_side is None or min_edge_side is None or min_spacing_side is None:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=[f"geometry.bolt_diameter_{side_suffix}"],
                message=f"Required side-specific bolt diameter is missing for side '{side_tag}'.",
            )
        if (
            de_side is None
            or pfo_side is None
            or pfi_side is None
            or g_side is None
            or bp_side is None
            or tp_side is None
        ):
            missing_fields: list[str] = []
            if de_side is None:
                missing_fields.append(f"geometry.de_{side_suffix}")
            if pfo_side is None:
                missing_fields.append(f"geometry.pfo_{side_suffix}")
            if pfi_side is None:
                missing_fields.append(f"geometry.pfi_{side_suffix}")
            if g_side is None:
                missing_fields.append(f"geometry.bolt_gage_{side_suffix}")
            if bp_side is None:
                missing_fields.append(f"geometry.end_plate_width_{side_suffix}")
            if tp_side is None:
                missing_fields.append(f"geometry.end_plate_thickness_{side_suffix}")
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=missing_fields,
                message=f"Required side-specific geometry is missing for Table 6.1 checks on side '{side_tag}'.",
            )

        tfb = side_profile["tf"]
        pso = Quantity(
            value=pfo_side.value + 0.5 * tfb.value - 0.5 * tcp.value,
            unit=pfo_side.unit,
        )
        psi = Quantity(
            value=pfi_side.value + 0.5 * tfb.value - 0.5 * tcp.value,
            unit=pfi_side.unit,
        )

        table_61_checks.append(
            _step1_limit(
                check_id=f"table_6_1.edge_de_ge_emin_{side_tag}",
                scope=f"end_plate_{side_tag}",
                clause="Table 6.1 + AISC 360 Table J3.4",
                description=f"Edge distance at de ({side_label})",
                calculated_symbol=f"de_pe_{side_suffix}",
                limit_symbol="emin",
                calculated=de_side,
                limit=min_edge_side,
                comparison="ge",
            )
        )
        surface_cond_side = (
            case.geometry.cond_pe_vgder
            if side_tag == "der"
            else case.geometry.cond_pe_vgizq
        ) or case.geometry.cond_col
        atmospheric_cond_side = (
            case.geometry.cond_amb_pe_vgder
            if side_tag == "der"
            else case.geometry.cond_amb_pe_vgizq
        ) or case.geometry.cond_amb_col
        is_unpainted_weathering_exposed = (
            surface_cond_side == "unpainted" and atmospheric_cond_side == "corrosive"
        )
        tf_col_for_j36 = column_profile["tf"]
        t_for_j36 = _minimum_thickness(tp_side, tf_col_for_j36)
        if t_for_j36 is None:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=[
                    f"geometry.end_plate_thickness_{side_suffix}",
                    "sections.column_shape.tf",
                ],
                message=(
                    "Unable to evaluate AISC 360-22 J3.6 maximum edge distance "
                    f"for side '{side_tag}' because min{{tpe_{side_suffix}, tf_col}} "
                    "could not be resolved."
                ),
            )
        # AISC 360-22 J3.6: max edge distance from hole center to nearest edge.
        j36_limits_side = compute_max_spacing_and_edge_distance_limits_j36(
            thinner_part_thickness=t_for_j36,
            unit_system=case.units_system,
            is_unpainted_weathering_exposed=is_unpainted_weathering_exposed,
        )
        j36_limits_tf_col = compute_max_spacing_and_edge_distance_limits_j36(
            thinner_part_thickness=tf_col_for_j36,
            unit_system=case.units_system,
            is_unpainted_weathering_exposed=is_unpainted_weathering_exposed,
        )
        j36_limits_tpe_side = compute_max_spacing_and_edge_distance_limits_j36(
            thinner_part_thickness=tp_side,
            unit_system=case.units_system,
            is_unpainted_weathering_exposed=is_unpainted_weathering_exposed,
        )
        table_61_checks.append(
            _step1_limit(
                check_id=f"table_6_1.edge_de_le_emax_{side_tag}",
                scope=f"end_plate_{side_tag}",
                clause="Table 6.1 + AISC 360-22 J3.6",
                description=f"Maximum edge distance at de ({side_label})",
                calculated_symbol=f"de_pe_{side_suffix}",
                limit_symbol="emax_j36",
                calculated=de_side,
                limit=j36_limits_side["max_edge_distance_active"],
                comparison="le",
            )
        )
        if pfo_bounds is not None:
            pfo_min, pfo_max = pfo_bounds
            pfo_min_governing = (
                pfo_min
                if pfo_min.value >= min_edge_side.value
                else min_edge_side
            )
            pfo_max_governing = (
                pfo_max
                if pfo_max.value <= j36_limits_tpe_side["max_edge_distance_active"].value
                else j36_limits_tpe_side["max_edge_distance_active"]
            )
            table_61_checks.append(
                _step1_limit(
                    check_id=f"table_6_1.edge_pfo_ge_pfo_min_{side_tag}",
                    scope=f"end_plate_{side_tag}",
                    clause="Table 6.1 + AISC 360 Table J3.4",
                    description=f"Outside bolt-row distance minimum ({side_label})",
                    calculated_symbol=f"pfo_pe_{side_suffix}",
                    limit_symbol=f"max(pfo_pe_{side_suffix}_min, emin)",
                    calculated=pfo_side,
                    limit=pfo_min_governing,
                    comparison="ge",
                )
            )
            table_61_checks.append(
                _step1_limit(
                    check_id=f"table_6_1.edge_pfo_le_emax_{side_tag}",
                    scope=f"end_plate_{side_tag}",
                    clause="Table 6.1 + AISC 360-22 J3.6",
                    description=f"Outside bolt-row distance maximum ({side_label})",
                    calculated_symbol=f"pfo_pe_{side_suffix}",
                    limit_symbol=f"min(pfo_pe_{side_suffix}_max, emax_j36)",
                    calculated=pfo_side,
                    limit=pfo_max_governing,
                    comparison="le",
                )
            )
            table_61_checks.append(
                _step1_limit(
                    check_id=f"table_6_1.edge_pso_ge_emin_{side_tag}",
                    scope="column",
                    clause="Table 6.1 + AISC 360 Table J3.4",
                    description=f"Outside adjusted edge distance minimum ({side_label})",
                    calculated_symbol=f"pso_pe_{side_suffix}",
                    limit_symbol="emin",
                    calculated=pso,
                    limit=min_edge_side,
                    comparison="ge",
                )
            )
            table_61_checks.append(
                _step1_limit(
                    check_id=f"table_6_1.edge_pso_le_emax_{side_tag}",
                    scope="column",
                    clause="AISC 360-22 J3.6",
                    description=f"Outside adjusted edge distance maximum ({side_label})",
                    calculated_symbol=f"pso_pe_{side_suffix}",
                    limit_symbol="emax_j36",
                    calculated=pso,
                    limit=j36_limits_tf_col["max_edge_distance_active"],
                    comparison="le",
                )
            )
        if pfi_bounds is not None:
            pfi_min, pfi_max = pfi_bounds
            pfi_min_governing = (
                pfi_min
                if pfi_min.value >= min_edge_side.value
                else min_edge_side
            )
            table_61_checks.append(
                _step1_limit(
                    check_id=f"table_6_1.edge_pfi_ge_pfi_min_{side_tag}",
                    scope=f"end_plate_{side_tag}",
                    clause="Table 6.1 + AISC 360 Table J3.4",
                    description=f"Inside bolt-row distance minimum ({side_label})",
                    calculated_symbol=f"pfi_pe_{side_suffix}",
                    limit_symbol=f"max(pfi_pe_{side_suffix}_min, emin)",
                    calculated=pfi_side,
                    limit=pfi_min_governing,
                    comparison="ge",
                )
            )
            pfi_max_governing = (
                pfi_max
                if pfi_max.value <= j36_limits_tpe_side["max_edge_distance_active"].value
                else j36_limits_tpe_side["max_edge_distance_active"]
            )
            table_61_checks.append(
                _step1_limit(
                    check_id=f"table_6_1.edge_pfi_le_emax_{side_tag}",
                    scope=f"end_plate_{side_tag}",
                    clause="Table 6.1 + AISC 360-22 J3.6",
                    description=f"Inside bolt-row distance maximum ({side_label})",
                    calculated_symbol=f"pfi_pe_{side_suffix}",
                    limit_symbol=f"min(pfi_pe_{side_suffix}_max, emax_j36)",
                    calculated=pfi_side,
                    limit=pfi_max_governing,
                    comparison="le",
                )
            )
        if case.connection_type == "bseep_8es":
            if pb_side is None:
                raise ValueError("geometry.pb is required for bseep_8es prequalification checks.")
            pb_8es_min = _table61_length(us_in=89.0 / 25.4, si_mm=89.0)
            pb_8es_max = _table61_length(us_in=95.0 / 25.4, si_mm=95.0)
            pb_tol = 1e-3
            pb_passes = (
                (pb_side.value >= (min_spacing_side.value - pb_tol))
                and (pb_side.value <= (pb_8es_max.value + pb_tol))
                and (pb_side.value >= (pb_8es_min.value - pb_tol))
            )

        table_61_values: list[tuple[str, str, str, Quantity]] = [
            ("bbf", "Beam flange width", f"bf_{side_suffix}", side_profile["bf"]),
            ("d", "Connecting beam depth", f"d_{side_suffix}", side_profile["d"]),
            ("tp", "End-plate thickness", f"tpe_{side_suffix}", tp_side),
            ("bp", "End-plate width", f"bp_pe_{side_suffix}", bp_side),
            ("g", "Horizontal bolt spacing", f"g_b_{side_suffix}", g_side),
        ]
        if case.connection_type == "bseep_8es" and pb_side is not None:
            table_61_values.append(("pb", "Vertical bolt-row spacing", f"pb_pe_{side_suffix}", pb_side))

        for symbol, description, symbol_display, value in table_61_values:
            bounds = active_table_61.get(symbol)
            if bounds is None:
                continue
            minimum, maximum = bounds
            if symbol == "bp":
                continue
            target_scope = side_scope
            if symbol in {"bbf", "d"}:
                target_scope = f"beam_{side_tag}"
            elif symbol == "tp":
                target_scope = f"end_plate_{side_tag}"

            if symbol == "g":
                g_min_governing = (
                    minimum
                    if minimum.value >= min_spacing_side.value
                    else min_spacing_side
                )
                g_max_j36, _g_max_j36_meta = compute_maximum_bolt_spacing_j36(
                    thinner_part_thickness=t_for_j36,
                    unit_system=case.units_system,
                    is_unpainted_weathering_exposed=is_unpainted_weathering_exposed,
                )
                g_max_governing = (
                    maximum
                    if maximum.value <= g_max_j36.value
                    else g_max_j36
                )
                table_61_checks.append(
                    _step1_limit(
                        check_id=f"table_6_1.{symbol}.ge_min_{side_tag}",
                        scope=f"end_plate_{side_tag}",
                        clause="Table 6.1 + AISC 360 Table J3.3 (compute_minimum_bolt_spacing_j33)",
                        description=f"{description} minimum ({side_label})",
                        calculated_symbol=symbol_display,
                        limit_symbol=f"max({symbol_display}_min, 3db_j33)",
                        calculated=value,
                        limit=g_min_governing,
                        comparison="ge",
                    )
                )
                table_61_checks.append(
                    _step1_limit(
                        check_id=f"table_6_1.{symbol}.le_max_{side_tag}",
                        scope=f"end_plate_{side_tag}",
                        clause="Table 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)",
                        description=f"{description} maximum ({side_label})",
                        calculated_symbol=symbol_display,
                        limit_symbol=f"min({symbol_display}_max, smax_j36)",
                        calculated=value,
                        limit=g_max_governing,
                        comparison="le",
                    )
                )
            else:
                table_61_checks.append(
                    _step1_range_limit(
                        check_id=f"table_6_1.{symbol}.range_{side_tag}",
                        scope=target_scope,
                        clause="Table 6.1",
                        description=f"{description} limits ({side_label})",
                        symbol=symbol_display,
                        calculated=value,
                        minimum=minimum,
                        maximum=maximum,
                    )
                )

    step_1_limits = (
        beam_limits
        + column_limits
        + doubler_plate_limits
        + end_plate_limits
        + end_plate_stiffener_limits
        + weld_limits
        + continuity_plate_limits
        + bolt_limits
        + table_61_checks
    )

    overall_status = CheckStatus.PASS if all(item["status"] == CheckStatus.PASS.value for item in step_1_limits) else CheckStatus.FAIL
    b2_pc_col_input: Quantity | None = None
    if (
        case.geometry.continuity_plate_width_b1 is not None
        and column_profile.get("k1") is not None
        and column_profile.get("tw") is not None
        and column_profile["k1"].unit == column_profile["tw"].unit
    ):
        clip2_input = Quantity(
            value=((column_profile["k1"].value - column_profile["tw"].value) / 2.0) + 12.0,
            unit=column_profile["k1"].unit,
        )
        b2_pc_col_input = Quantity(
            value=case.geometry.continuity_plate_width_b1.value - clip2_input.value,
            unit=case.geometry.continuity_plate_width_b1.unit,
        )

    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=None,
        capacity=None,
        dcr=None,
        status=overall_status,
        calculation_memory=CalculationMemory(
            inputs={
                "bolt_diameter": db.model_dump(),
                "beam_flange_width_bf": bf.model_dump(),
                "column_flange_width_bcf": bcf.model_dump(),
                "column_depth_d_col": column_profile["d"].model_dump(),
                "column_depth_limit_max": column_depth_max.model_dump(),
                "continuity_plate_thickness_tcp": tcp.model_dump() if tcp is not None else None,
                "t_pc_col": tcp.model_dump() if tcp is not None else None,
                "b1_pc_col": (
                    case.geometry.continuity_plate_width_b1.model_dump()
                    if case.geometry.continuity_plate_width_b1 is not None
                    else None
                ),
                "n_pc_col": case.geometry.continuity_plate_count,
                "usar_pc_col": case.geometry.continuity_plate_enabled,
                "tipo_acero_pc_col": (
                    case.materials.continuity_plate_steel_type
                    or case.materials.plate_steel_type
                ),
                "kdet_col": (
                    (column_profile.get("kdet") or column_profile.get("kdes")).model_dump()
                    if (column_profile.get("kdet") or column_profile.get("kdes")) is not None
                    else None
                ),
                "k1_col": (
                    column_profile.get("k1").model_dump()
                    if column_profile.get("k1") is not None
                    else None
                ),
                "tw_col": (
                    column_profile.get("tw").model_dump()
                    if column_profile.get("tw") is not None
                    else None
                ),
                "b2_pc_col": (
                    b2_pc_col_input.model_dump()
                    if b2_pc_col_input is not None
                    else None
                ),
                "L2_pc_col": (
                    l2_pc_col_q.model_dump()
                    if l2_pc_col_q is not None
                    else None
                ),
                "L_w5_col": (
                    l_w5_col_computed.model_dump()
                    if l_w5_col_computed is not None
                    else None
                ),
                "phi_fragil": case.design_factors.phi_f,
                "tfdet_col": (
                    (column_profile.get("tfdet") or column_profile.get("tf")).model_dump()
                    if (column_profile.get("tfdet") or column_profile.get("tf")) is not None
                    else None
                ),
                "continuity_plate_enabled": case.geometry.continuity_plate_enabled,
                "continuity_plate_weld_type": continuity_plate_weld_type_raw,
                "tipo_w5_col": continuity_plate_weld_type_raw,
                "Fexx_w5_col": weld_fexx.model_dump(),
                "w_w5_col": w_w5_col.model_dump() if w_w5_col is not None else None,
                "t_w5_col": w_w5_col.model_dump() if w_w5_col is not None else None,
                "nl_w5_col": nl_w5_col,
                "L_gap_w5_col": l_gap_w5_col.model_dump() if l_gap_w5_col is not None else None,
                "kds_w5_col": kds_w5_col,
                "Fexx_w6_col": weld_fexx.model_dump(),
                "tipo_w6_col": continuity_plate_web_weld_type_raw,
                "w_w6_col": w_w6_col.model_dump() if w_w6_col is not None else None,
                "t_w6_col": w_w6_col.model_dump() if w_w6_col is not None else None,
                "nl_w6_col": nl_w6_col,
                "L_gap_w6_col": l_gap_w6_col.model_dump() if l_gap_w6_col is not None else None,
                "kds_w6_col": kds_w6_col,
                "Fexx_w8_col": weld_fexx.model_dump(),
                "tipo_w8_col": weld_8_type_raw,
                "w_w8_col": w_w8_col.model_dump() if w_w8_col is not None else None,
                "t_w8_col": w_w8_col.model_dump() if w_w8_col is not None else None,
                "nl_w8_col": nl_w8_col,
                "L_gap_w8_col": (
                    case.geometry.L_gap_w8_col.model_dump()
                    if case.geometry.L_gap_w8_col is not None
                    else None
                ),
                "L_w8_col": l_w8_col_computed.model_dump() if l_w8_col_computed is not None else None,
                "Encr_w8_col": encr_w8_col.model_dump() if encr_w8_col is not None else None,
                "Encr_w8_col_fuente": encr_w8_source,
                "kds_w8_col": kds_w8_col,
                "use_weld_9_col": case.geometry.use_weld_9_col,
                "tipo_w9_col": weld_9_type_raw,
                "w_w9_col": w_w9_col.model_dump() if w_w9_col is not None else None,
                "t_w9_col": (
                    w_w9_col.model_dump()
                    if w_w9_col is not None
                    else None
                ),
                "nl_w9_col": nl_w9_col,
                "L_gap_w9_col": l_gap_w9_col.model_dump() if l_gap_w9_col is not None else None,
                "kds_w9_col": kds_w9_col,
                "L_w9_col": l_w9_col_computed.model_dump() if l_w9_col_computed is not None else None,
                "gap_dp_col": gap_dp_col.model_dump() if gap_dp_col is not None else None,
                "estado_contacto_dp_col": weld8_contact_state_col,
                "tipo_acero_dp_col": case.materials.doubler_plate_steel_type,
                "tipo_w7_col": case.geometry.doubler_plate_web_plug_weld_type,
                "Fexx_w7_col": weld_fexx.model_dump(),
                "w_w7_col": (
                    case.geometry.doubler_plate_web_plug_weld_size.model_dump()
                    if case.geometry.doubler_plate_web_plug_weld_size is not None
                    else None
                ),
                "t_w7_col": (
                    case.geometry.doubler_plate_web_plug_weld_size.model_dump()
                    if case.geometry.doubler_plate_web_plug_weld_size is not None
                    else None
                ),
                "nl_w7_col": case.geometry.doubler_plate_web_plug_weld_lines_nl,
                "nfilas_w7_col": (
                    case.geometry.nfilas_w7_col
                    if case.geometry.nfilas_w7_col is not None
                    else case.geometry.doubler_plate_web_plug_weld_lines_nl
                ),
                "ncolumna_w7_col": case.geometry.ncolumna_w7_col,
                "d_hole_w7_col": (
                    case.geometry.d_hole_w7_col.model_dump()
                    if case.geometry.d_hole_w7_col is not None
                    else None
                ),
                "sh_w7_col": sh_w7_col.model_dump() if sh_w7_col is not None else None,
                "sv_w7_col": sv_w7_col.model_dump() if sv_w7_col is not None else None,
                "t_part_w7_col": tcp.model_dump() if tcp is not None else None,
                # Legacy aliases (compatibility while migrating naming).
                "tipo_wdp_plug": case.geometry.doubler_plate_web_plug_weld_type,
                "t_wdp_plug": (
                    case.geometry.doubler_plate_web_plug_weld_size.model_dump()
                    if case.geometry.doubler_plate_web_plug_weld_size is not None
                    else None
                ),
                "nl_wdp_plug": case.geometry.doubler_plate_web_plug_weld_lines_nl,
                "end_plate_beam_web_weld_type": end_plate_beam_web_weld_type_raw,
                "weld_fexx": weld_fexx.model_dump(),
                "end_plate_beam_web_weld_thickness_twe": (
                    case.geometry.end_plate_beam_web_weld_thickness_twe.model_dump()
                    if case.geometry.end_plate_beam_web_weld_thickness_twe is not None
                    else None
                ),
                "end_plate_beam_web_weld_lines_nl": case.geometry.end_plate_beam_web_weld_lines_nl,
                "L_gap_w1_vgder": (
                    case.geometry.L_gap_w1_vgder.model_dump()
                    if case.geometry.L_gap_w1_vgder is not None
                    else None
                ),
                "L_gap_w1_vgizq": (
                    case.geometry.L_gap_w1_vgizq.model_dump()
                    if case.geometry.L_gap_w1_vgizq is not None
                    else None
                ),
                "L_gap_w2_vgder": (
                    case.geometry.L_gap_w2_vgder.model_dump()
                    if case.geometry.L_gap_w2_vgder is not None
                    else None
                ),
                "L_gap_w2_vgizq": (
                    case.geometry.L_gap_w2_vgizq.model_dump()
                    if case.geometry.L_gap_w2_vgizq is not None
                    else None
                ),
                "tipo_w1_vgder": case.geometry.end_plate_stiffener_weld_type_vgder
                or case.geometry.end_plate_stiffener_weld_type,
                "tipo_w1_vgizq": case.geometry.end_plate_stiffener_weld_type_vgizq
                or case.geometry.end_plate_stiffener_weld_type,
                "w_w1_vgder": (
                    case.geometry.end_plate_stiffener_weld_size_wst_vgder.model_dump()
                    if case.geometry.end_plate_stiffener_weld_size_wst_vgder is not None
                    else (
                        case.geometry.end_plate_stiffener_weld_size_wst.model_dump()
                        if case.geometry.end_plate_stiffener_weld_size_wst is not None
                        else None
                    )
                ),
                "w_w1_vgizq": (
                    case.geometry.end_plate_stiffener_weld_size_wst_vgizq.model_dump()
                    if case.geometry.end_plate_stiffener_weld_size_wst_vgizq is not None
                    else (
                        case.geometry.end_plate_stiffener_weld_size_wst.model_dump()
                        if case.geometry.end_plate_stiffener_weld_size_wst is not None
                        else None
                    )
                ),
                "nl_w1_vgder": case.geometry.end_plate_stiffener_weld_lines_nl_vgder
                if case.geometry.end_plate_stiffener_weld_lines_nl_vgder is not None
                else case.geometry.end_plate_stiffener_weld_lines_nl,
                "nl_w1_vgizq": case.geometry.end_plate_stiffener_weld_lines_nl_vgizq
                if case.geometry.end_plate_stiffener_weld_lines_nl_vgizq is not None
                else case.geometry.end_plate_stiffener_weld_lines_nl,
                "kds_w1_vgder": case.geometry.kds_w1_vgder,
                "kds_w1_vgizq": case.geometry.kds_w1_vgizq,
                "tipo_w2_vgder": case.geometry.beam_stiffener_weld_type_vgder
                or case.geometry.beam_stiffener_weld_type,
                "tipo_w2_vgizq": case.geometry.beam_stiffener_weld_type_vgizq
                or case.geometry.beam_stiffener_weld_type,
                "w_w2_vgder": (
                    case.geometry.beam_stiffener_weld_size_wst2_vgder.model_dump()
                    if case.geometry.beam_stiffener_weld_size_wst2_vgder is not None
                    else (
                        case.geometry.beam_stiffener_weld_size_wst2.model_dump()
                        if case.geometry.beam_stiffener_weld_size_wst2 is not None
                        else (
                            case.geometry.end_plate_beam_web_weld_thickness_twe_vgder.model_dump()
                            if case.geometry.end_plate_beam_web_weld_thickness_twe_vgder is not None
                            else (
                                case.geometry.end_plate_beam_web_weld_thickness_twe.model_dump()
                                if case.geometry.end_plate_beam_web_weld_thickness_twe is not None
                                else None
                            )
                        )
                    )
                ),
                "w_w2_vgizq": (
                    case.geometry.beam_stiffener_weld_size_wst2_vgizq.model_dump()
                    if case.geometry.beam_stiffener_weld_size_wst2_vgizq is not None
                    else (
                        case.geometry.beam_stiffener_weld_size_wst2.model_dump()
                        if case.geometry.beam_stiffener_weld_size_wst2 is not None
                        else (
                            case.geometry.end_plate_beam_web_weld_thickness_twe_vgizq.model_dump()
                            if case.geometry.end_plate_beam_web_weld_thickness_twe_vgizq is not None
                            else (
                                case.geometry.end_plate_beam_web_weld_thickness_twe.model_dump()
                                if case.geometry.end_plate_beam_web_weld_thickness_twe is not None
                                else None
                            )
                        )
                    )
                ),
                "nl_w2_vgder": case.geometry.beam_stiffener_weld_lines_nl_w2_vgder
                if case.geometry.beam_stiffener_weld_lines_nl_w2_vgder is not None
                else (
                    case.geometry.beam_stiffener_weld_lines_nl_w2
                    if case.geometry.beam_stiffener_weld_lines_nl_w2 is not None
                    else case.geometry.end_plate_beam_web_weld_lines_nl
                ),
                "nl_w2_vgizq": case.geometry.beam_stiffener_weld_lines_nl_w2_vgizq
                if case.geometry.beam_stiffener_weld_lines_nl_w2_vgizq is not None
                else (
                    case.geometry.beam_stiffener_weld_lines_nl_w2
                    if case.geometry.beam_stiffener_weld_lines_nl_w2 is not None
                    else case.geometry.end_plate_beam_web_weld_lines_nl
                ),
                "kds_w2_vgder": case.geometry.kds_w2_vgder,
                "kds_w2_vgizq": case.geometry.kds_w2_vgizq,
                "bolt_tightening_type": bolt_tightening_type,
                "bolt_fabrication_standard": bolt_fabrication_standard,
                "end_plate_width_bp": bp.model_dump(),
                "bolt_gage_g": g.model_dump(),
                "pitch_pb": pb.model_dump() if pb is not None else None,
                "edge_de": de.model_dump(),
                "edge_pfo": pfo.model_dump(),
                "edge_pfi": pfi.model_dump(),
                "end_plate_height": end_plate_height.model_dump(),
                "stiffener_height": stiffener_height.model_dump(),
                "stiffener_length": stiffener_length_derived.model_dump(),
                "beam_connection_sides": beam_connection_sides,
                "t_dp_col": (
                    case.geometry.doubler_plate_thickness.model_dump()
                    if case.geometry.doubler_plate_thickness is not None
                    else None
                ),
                "n_dp_col": case.geometry.doubler_plate_count,
                "extended_dp_col": case.geometry.extended_dp_col,
                "doubler_plate_enabled": case.geometry.doubler_plate_enabled,
                "use_weld_7_col": case.geometry.use_weld_7_col,
                "usar_weld_7_col": case.geometry.use_weld_7_col,
                "beam_clear_span_length_der": beam_clear_span_length_der.model_dump(),
                "beam_shear_connector_free_length_from_column_face_der": shear_connector_free_length_der.model_dump(),
                "beam_clear_span_length_izq": beam_clear_span_length_izq.model_dump()
                if beam_clear_span_length_izq is not None
                else None,
                "beam_shear_connector_free_length_from_column_face_izq": (
                    shear_connector_free_length_izq.model_dump()
                    if shear_connector_free_length_izq is not None
                    else None
                ),
                "beam_clear_span_length": beam_clear_span_length.model_dump(),
                "beam_shear_connector_free_length_from_column_face": shear_connector_free_length.model_dump(),
                "column_slab_connection_condition": slab_connection_condition,
                "tipo_acero_perfil_col": case.materials.profile_steel_type,
                "column_end_distance_to_beam_flange_st_col": stc.model_dump(),
                "column_st_col_min": stc_min.model_dump(),
                "d_col": column_profile["d"].model_dump(),
                "tf_col": column_profile["tf"].model_dump(),
                "kdes_col": (
                    (column_profile.get("kdes") or column_profile.get("kdet")).model_dump()
                    if (column_profile.get("kdes") or column_profile.get("kdet")) is not None
                    else None
                ),
                "elastic_modulus": case.materials.elastic_modulus.model_dump(),
                "beam_sc_vgder": sc_der.model_dump(),
                "beam_s_threshold_vgder": s_threshold_der.model_dump(),
                "beam_sc_vgizq": sc_izq.model_dump() if sc_izq is not None else None,
                "beam_s_threshold_vgizq": s_threshold_izq.model_dump() if s_threshold_izq is not None else None,
                "beam_ductility_demand": beam_ductility,
                "column_ductility_demand": column_ductility,
                "pu_viga": pu_beam.model_dump(),
                "pu_columna": pu_column.model_dump(),
                "ag_viga": beam_ag.model_dump(),
                "ag_columna": column_ag.model_dump(),
                "compactness_ca_beam_calculated": ca_beam,
                "compactness_ca_column_calculated": ca_column,
                "dz_dp_col": dz_dp_col.model_dump(),
                "wz_dp_col": wz_dp_col.model_dump() if wz_dp_col is not None else None,
                "h_w7_col": h_w7_col.model_dump() if h_w7_col is not None else None,
                "b_w7_col": b_w7_col.model_dump() if b_w7_col is not None else None,
                "h_dp_col": h_dp_col.model_dump() if h_dp_col is not None else None,
                "h_dp_col_formula": h_dp_formula_tag,
                "h_dp_col_rounding_note": h_dp_col_rounding_note,
                "b_dp_col": b_dp_col.model_dump() if b_dp_col is not None else None,
                "b_dp_col_formula": b_dp_formula_tag,
            },
            intermediates={
                "minimum_spacing_3db": min_spacing_der.model_dump(),
                "minimum_spacing_3db_vgizq": min_spacing_izq.model_dump() if min_spacing_izq is not None else None,
                "minimum_bp_bf_plus_margin": min_bp.model_dump(),
                "bp_margin": bp_margin,
                "minimum_edge_distance_j34": min_edge_der.model_dump(),
                "minimum_edge_distance_j34_vgizq": min_edge_izq.model_dump() if min_edge_izq is not None else None,
                "clear_span_to_depth_ratio_der": clear_span_to_depth_ratio_der.model_dump(),
                "clear_span_to_depth_ratio_izq": (
                    clear_span_to_depth_ratio_izq.model_dump() if clear_span_to_depth_ratio_izq is not None else None
                ),
                "clear_span_to_depth_limit": {"value": span_to_depth_limit, "unit": "ratio"},
                "frame_system_for_span_ratio": frame_system,
                "beam_flange_compactness_ratio_der": beam_flange_ratio_der,
                "beam_flange_compactness_ratio_izq": beam_flange_ratio_izq,
                "beam_flange_compactness_limit": beam_flange_limit,
                "beam_web_compactness_ratio_der": beam_web_ratio_der,
                "beam_web_compactness_ratio_izq": beam_web_ratio_izq,
                "beam_web_compactness_limit": beam_web_limit,
                "column_flange_compactness_ratio": column_flange_ratio,
                "column_flange_compactness_limit": column_flange_limit,
                "column_web_compactness_ratio": column_web_ratio,
                "column_web_compactness_limit": column_web_limit,
                "ca_beam_trace": ca_beam_trace,
                "ca_column_trace": ca_column_trace,
                "continuity_plate_weld_thickness_limit": continuity_plate_weld_thickness_limit.model_dump(),
                "L_w5_col": l_w5_col_computed.model_dump() if l_w5_col_computed is not None else None,
                "L_w5_col_formula": "L_w5_col = b2_pc_col - 2*(L_gap_w5_col)",
                "L_w6_col": l_w6_col_computed.model_dump() if l_w6_col_computed is not None else None,
                "L_w6_col_formula": "L_w6_col = L2_pc_col - 2*(L_gap_w6_col)",
                "L_w8_col": l_w8_col_computed.model_dump() if l_w8_col_computed is not None else None,
                "L_w8_col_formula": "L_w8_col = h_dp_col - 2*(L_gap_w8_col)",
                "L_w9_col": l_w9_col_computed.model_dump() if l_w9_col_computed is not None else None,
                "L_w9_col_formula": (
                    "L_w9_col = b_dp_col - 2*(L_gap_w9_col) si usar_weld_9_col=true; "
                    "L_w9_col = 0 si usar_weld_9_col=false"
                ),
                "j34_lookup": edge_intermediate_der,
                "j34_lookup_vgizq": edge_intermediate_izq,
                "step_1_notes": step_1_notes,
                "step_1_limits": step_1_limits,
                "prequalification_limits": step_1_limits,
            },
            design_factors={},
            equation=(
                "Step 1 PREQUALIFICATION LIMITS: compute each geometric value and compare directly against Table 6.1 limits "
                "using calculated vs limit checks (>= or <=, no DCR format)."
            ),
            units_trace={
                "db": db.unit,
                "bf": bf.unit,
                "bcf": bcf.unit,
                "bp": bp.unit,
                "g": g.unit,
                "pb": pb.unit if pb is not None else None,
                "de": de.unit,
                "pfo": pfo.unit,
                "pfi": pfi.unit,
            },
            final_capacity=None,
        ),
        notes=None,
    )


def run_step6_required_bolt_diameter(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf, _, _ = _select_mf_for_design(case, rule_binding)
    fnt = _require(case, "materials.bolt_fnt", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)
    distances = _compute_tension_bolt_line_distances(case, rule_binding)
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
    mf, _, _ = _select_mf_for_design(case, rule_binding)
    fnt = _require(case, "materials.bolt_fnt", rule_binding)
    phi_n = _require(case, "design_factors.phi_n", rule_binding)
    distances = _compute_tension_bolt_line_distances(case, rule_binding)
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
    mf, _, _ = _select_mf_for_design(case, rule_binding)
    beam_depth = _beam_profile(case)["d"]
    end_plate_fy = _require(case, "materials.end_plate_fy", rule_binding)
    yp, yp_intermediates = _derive_yp_from_tables_6_2_6_3_6_4(case, rule_binding)
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
            "yp_source": "derived_from_aisc358_tables_6_2_6_3_6_4",
            "tp_trial": tp_trial.model_dump(),
        },
        intermediates={**intermediates, **yp_intermediates},
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
    mf, _, _ = _select_mf_for_design(case, rule_binding)
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
    mf, _, _ = _select_mf_for_design(case, rule_binding)
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
    mf, _, _ = _select_mf_for_design(case, rule_binding)
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
    vu, vu_source = _select_vu_connection_for_design(case, rule_binding)
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
        equation="Vu = Vhmax (Eq. 2.4-3); Vu <= phi_n * nb * Fnv * Ab (Eq. 6.7-11)",
        inputs={
            "vu_connection_derived": vu.model_dump(),
            "vu_connection_source": vu_source,
            "bolt_fnv": bolt_fnv.model_dump(),
            "bolt_diameter": bolt_diameter.model_dump(),
            "n_bolts_compression": n_bolts,
        },
        intermediates=intermediates,
        design_factors={"phi_n": phi_n},
        units_trace={"vu": vu.unit, "capacity": capacity.unit},
    )


def run_bolt_bearing_tearout_end_plate(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vu, vu_source = _select_vu_connection_for_design(case, rule_binding)
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
        equation=(
            "Vu = Vhmax (Eq. 2.4-3); "
            "Vu <= phi_n * sum[min(1.2*lc*t*Fu, 2.4*db*t*Fu)] (Eq. 6.7-12, end plate)"
        ),
        inputs={
            "vu_connection_derived": vu.model_dump(),
            "vu_connection_source": vu_source,
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
    vu, vu_source = _select_vu_connection_for_design(case, rule_binding)
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
        equation=(
            "Vu = Vhmax (Eq. 2.4-3); "
            "Vu <= phi_n * sum[min(1.2*lc*t*Fu, 2.4*db*t*Fu)] (Eq. 6.7-12, column flange)"
        ),
        inputs={
            "vu_connection_derived": vu.model_dump(),
            "vu_connection_source": vu_source,
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
    de = _require(case, "geometry.de", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pb = _optional_pb_for_connection(case, rule_binding) if case.connection_type == "bseep_8es" else None
    hst = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo, pb=pb)
    lst = _derive_stiffener_length_from_hst(stiffener_height=hst, unit_system=case.units_system)

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
            inputs={
                "de": de.model_dump(),
                "pfo": pfo.model_dump(),
                "stiffener_height_derived": hst.model_dump(),
                "stiffener_length_derived": lst.model_dump(),
            },
            intermediates={},
            design_factors={},
            equation="hst = pfo + de; Lst >= hst / tan(30 deg) (Eq. 6.6-1)",
            units_trace={"de": de.unit, "pfo": pfo.unit, "hst": hst.unit, "lst": lst.unit},
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
    de = _require(case, "geometry.de", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pb = _optional_pb_for_connection(case, rule_binding) if case.connection_type == "bseep_8es" else None
    hst = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo, pb=pb)
    ts = _require(case, "geometry.stiffener_thickness", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    stiffener_fy = _require(case, "materials.stiffener_fy", rule_binding)

    ratio = compute_stiffener_slenderness_ratio(
        stiffener_height=hst,
        stiffener_thickness=ts,
        unit_system=case.units_system,
    )
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
                "de": de.model_dump(),
                "pfo": pfo.model_dump(),
                "stiffener_height_derived": hst.model_dump(),
                "stiffener_thickness": ts.model_dump(),
                "elastic_modulus": elastic_modulus.model_dump(),
                "stiffener_fy": stiffener_fy.model_dump(),
            },
            intermediates={"hst_over_ts": ratio, "limit": limit},
            design_factors={},
            equation="hst = pfo + de; hst/ts <= 0.56 * sqrt(E/Fys) (Eq. 6.7-10)",
            units_trace={"de": de.unit, "pfo": pfo.unit, "hst": hst.unit, "ts": ts.unit, "ratio": "ratio"},
            final_capacity=capacity,
        ),
        notes=None,
    )


def run_step14_beam_shear_strength(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vu, vu_source = _select_vu_connection_for_design(case, rule_binding)
    beam_shear_capacity, shear_intermediate = _compute_beam_available_shear_strength(case, rule_binding)
    return _build_result(
        rule_binding=rule_binding,
        demand=vu,
        capacity=beam_shear_capacity,
        equation="Vu_beam = Vhmax (Eq. 2.4-3); Vu_beam <= phi*Vn (AISC Specification per Section 6.7.1 Step 14)",
        inputs={
            "vu_beam_derived": vu.model_dump(),
            "vu_beam_source": vu_source,
            "beam_available_shear_strength_derived": beam_shear_capacity.model_dump(),
        },
        intermediates=shear_intermediate,
        design_factors={},
        units_trace={"vu": vu.unit, "capacity": beam_shear_capacity.unit},
    )


def run_step15_connection_shear_requirement(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vu_beam, vu_beam_source = _select_vu_connection_for_design(case, rule_binding)
    vu_connection, vu_connection_source = vu_beam, vu_beam_source
    return _build_result(
        rule_binding=rule_binding,
        demand=vu_beam,
        capacity=vu_connection,
        equation="Vu(beam) = Vhmax and Vu(connection) = Vhmax (Eq. 2.4-3); Vu(connection) = Vu(beam) (Section 6.7.1 Step 15)",
        inputs={
            "vu_beam_derived": vu_beam.model_dump(),
            "vu_beam_source": vu_beam_source,
            "vu_connection_derived": vu_connection.model_dump(),
            "vu_connection_source": vu_connection_source,
        },
        intermediates={},
        design_factors={},
        units_trace={"vu_beam": vu_beam.unit, "vu_connection": vu_connection.unit},
    )


def run_step18_weld_design(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    mf, _, _ = _select_mf_for_design(case, rule_binding)
    ffu, ffu_intermediate = compute_beam_flange_force_from_mf(
        mf=mf,
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    flange_weld_capacity = _get_procedure_optional(case, "flange_weld_available_strength")
    web_weld_capacity = _get_procedure_optional(case, "web_weld_available_strength")
    vu_connection, vu_source = _select_vu_connection_for_design(case, rule_binding)
    required_web_weld = Quantity(
        value=0.4 * vu_connection.value,
        unit=vu_connection.unit,
    )

    if flange_weld_capacity is None or web_weld_capacity is None:
        missing_fields: list[str] = []
        if flange_weld_capacity is None:
            missing_fields.append("procedure.flange_weld_available_strength")
        if web_weld_capacity is None:
            missing_fields.append("procedure.web_weld_available_strength")
        return CheckResult(
            name=rule_binding.name,
            rule_id=rule_binding.rule_id,
            clause=rule_binding.clause,
            source_document=rule_binding.source_document,
            demand=None,
            capacity=None,
            dcr=None,
            status=CheckStatus.NOT_IMPLEMENTED,
            calculation_memory=CalculationMemory(
                inputs={
                    "mf": mf.model_dump(),
                    "required_web_weld_force_derived": required_web_weld.model_dump(),
                    "vu_connection_derived": vu_connection.model_dump(),
                    "vu_connection_source": vu_source,
                    "flange_weld_available_strength": None,
                    "web_weld_available_strength": None,
                    "missing_fields": missing_fields,
                },
                intermediates={**ffu_intermediate, "ffu": ffu.value},
                design_factors={},
                equation=(
                    "Section 6.7.1 Step 18 requires explicit weld capacities. "
                    "No automatic PASS is allowed under zero-guess policy."
                ),
                units_trace={"dcr": "ratio"},
                final_capacity=None,
            ),
            notes=None,
        )

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
                "required_web_weld_force_derived": required_web_weld.model_dump(),
                "vu_connection_derived": vu_connection.model_dump(),
                "vu_connection_source": vu_source,
                "flange_weld_available_strength": flange_weld_capacity.model_dump(),
                "web_weld_available_strength": web_weld_capacity.model_dump(),
            },
            intermediates={
                **ffu_intermediate,
                "ffu": ffu.value,
                "flange_weld_dcr": flange_dcr,
                "web_weld_dcr": web_dcr,
                "required_web_weld_factor_from_vu": 0.4,
            },
            design_factors={},
            equation="Section 6.7.1 Step 18 + Section 6.6.6 weld design checks",
            units_trace={"dcr": "ratio"},
            final_capacity=capacity,
        ),
        notes=None,
    )


def run_column_step1_flange_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf_data = _compute_mf_by_side(case, rule_binding)
    mf = mf_data["sides"]["izq"]["mfmax"]
    mf_source = "step5_computed_mf_izqmax (selected_side=izq)"
    if case.loads.probable_moment_column_face is not None:
        mf = case.loads.probable_moment_column_face
        mf_source = "loads.probable_moment_column_face (legacy)"
    beam_depth = _beam_profile(case)["d"]
    column_profile = _column_profile(case)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    yc, yc_meta = _column_yc_parameter_details(case, rule_binding)
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
            "mf_source": mf_source,
            "beam_depth": beam_depth.model_dump(),
            "column_shape": case.sections.column_shape,
            "column_fy": column_fy.model_dump(),
            "yc": yc.model_dump(),
            "yc_table_reference": yc_meta.get("table_reference"),
            "yc_case_reference": yc_meta.get("case_reference"),
            "yc_formula": yc_meta.get("formula"),
            "yc_is_hardcoded": yc_meta.get("is_hardcoded", False),
            "continuity_plate_enabled": yc_meta.get("continuity_plate_enabled"),
        },
        intermediates=yc_meta,
        design_factors={"phi_d": phi_d},
        units_trace={"tcf_req": tcf_req.unit, "tcf": tcf.unit},
    )


def run_column_step2_stiffener_force(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    column_profile = _column_profile(case)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    yc, yc_meta = _column_yc_parameter_details(case, rule_binding)
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
        mf=_select_mf_for_design(case, rule_binding)[0],
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=ffu,
        capacity=d_rn,
        equation="Equivalent column flange design force from Eq. 6.7-14 and Eq. 6.7-15",
        inputs={
            "column_shape": case.sections.column_shape,
            "column_fy": column_fy.model_dump(),
            "yc": yc.model_dump(),
            "yc_table_reference": yc_meta.get("table_reference"),
            "yc_case_reference": yc_meta.get("case_reference"),
            "yc_formula": yc_meta.get("formula"),
            "yc_is_hardcoded": yc_meta.get("is_hardcoded", False),
        },
        intermediates={**intermediates, **yc_meta},
        design_factors={"phi_d": phi_d},
        units_trace={"ffu": ffu.unit, "d_rn": d_rn.unit},
    )


def run_column_step3_web_local_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile_by_side(case, "izq")
    column_profile = _column_profile(case)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    kc = _profile_kdes(column_profile, role="column", rule_binding=rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    phi_d = _require(case, "design_factors.phi_d", rule_binding)
    column_top_distance = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)
    backing_thickness = _require(case, "geometry.t_w4_1_vgizq", rule_binding)
    ductility_vgizq = case.design_factors.member_ductility_demand_column
    if ductility_vgizq is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[
                "design_factors.member_ductility_demand_column",
            ],
            message="Required column ductility demand is missing.",
        )
    nl_w4_vgizq: int | None = None
    if str(ductility_vgizq).strip().lower() == "low":
        nl_w4_vgizq = _require(case, "geometry.nl_w4_vgizq", rule_binding)
    total_weld = compute_total_weld_4_thickness(
        backing_thickness=backing_thickness,
        ductility_demand=str(ductility_vgizq),
        weld_lines=nl_w4_vgizq if nl_w4_vgizq is not None else case.geometry.nl_w4_vgizq,
        unit_system=case.units_system,
    )
    total_weld_thickness = total_weld["total_thickness"]

    ct = 0.5 if column_top_distance.value < column_profile["d"].value else 1.0
    lb = Quantity(
        value=beam_profile["tf"].value + total_weld_thickness.value + 2.0 * tp.value,
        unit=beam_profile["tf"].unit,
    )
    capacity, intermediates = compute_column_web_local_yielding_strength(
        ct=ct,
        kc=kc,
        lb=lb,
        column_fy=column_fy,
        column_web_thickness=column_profile["tw"],
        phi_d=phi_d,
        unit_system=case.units_system,
    )
    mf_data = _compute_mf_by_side(case, rule_binding)
    mf_vgizq_critico = mf_data["sides"]["izq"]["mfmax"]
    ffu, _ = compute_beam_flange_force_from_mf(
        mf=mf_vgizq_critico,
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    use_continuity_plate = bool(case.geometry.continuity_plate_enabled)
    ru_base = ffu
    demand_force = (
        Quantity(value=min(ru_base.value, capacity.value), unit=ru_base.unit)
        if use_continuity_plate
        else ru_base
    )
    demand_source = (
        "continuity_plate_enabled => Ru_adoptado = min(Ru_base, phi*Rn_cf_v2_col_vgizq)"
        if use_continuity_plate
        else "Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq)"
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=demand_force,
        capacity=capacity,
        equation=(
            "Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); "
            "lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; "
            "phi*Rn_cf_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col"
        ),
        inputs={
            "column_shape": case.sections.column_shape,
            "ru_cf_v2_col_vgizq_base": ru_base.model_dump(),
            "ru_cf_v2_col_vgizq_adoptado": demand_force.model_dump(),
            "ru_cf_v2_col_vgizq": demand_force.model_dump(),
            "ru_cf_v2_col_vgizq_source": demand_source,
            "mf_vgizq_critico": mf_vgizq_critico.model_dump(),
            "st_col": column_top_distance.model_dump(),
            "d_col": column_profile["d"].model_dump(),
            "ct_col": ct,
            "kc_from_sections_kdes": kc.model_dump(),
            "kc_col": kc.model_dump(),
            "lb": lb.model_dump(),
            "lb_col": lb.model_dump(),
            "lb_col_formula": "lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq",
            "t_w4_1_vgizq": backing_thickness.model_dump(),
            "nl_w4_vgizq": case.geometry.nl_w4_vgizq,
            "ductility_vgizq": ductility_vgizq,
            "total_weld_thickness_w4_vgizq": total_weld_thickness.model_dump(),
            "total_weld_thickness_w4_formula": total_weld["equation"],
            "column_fy": column_fy.model_dump(),
            "fy_col": column_fy.model_dump(),
            "tw_col": column_profile["tw"].model_dump(),
            "d_vgizq": beam_profile["d"].model_dump(),
            "tf_vgizq": beam_profile["tf"].model_dump(),
            "tpe_vgizq": tp.model_dump(),
        },
        intermediates={
            "phi_rn_cf_v2_col_vgizq": capacity.value,
            "rn_nominal_cf_v2_col_vgizq": intermediates.get("rn_nominal"),
            "continuity_plate_enabled": use_continuity_plate,
        },
        design_factors={"phi_d": phi_d},
        units_trace={"ffu": demand_force.unit, "capacity": capacity.unit},
    )


def run_column_step4_web_local_crippling(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile_by_side(case, "izq")
    column_profile = _column_profile(case)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    distance_to_end = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)
    backing_thickness = _require(case, "geometry.t_w4_1_vgizq", rule_binding)
    ductility_vgizq = case.design_factors.member_ductility_demand_column
    if ductility_vgizq is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[
                "design_factors.member_ductility_demand_column",
            ],
            message="Required column ductility demand is missing.",
        )
    nl_w4_vgizq: int | None = None
    if str(ductility_vgizq).strip().lower() == "low":
        nl_w4_vgizq = _require(case, "geometry.nl_w4_vgizq", rule_binding)
    total_weld = compute_total_weld_4_thickness(
        backing_thickness=backing_thickness,
        ductility_demand=str(ductility_vgizq),
        weld_lines=nl_w4_vgizq if nl_w4_vgizq is not None else case.geometry.nl_w4_vgizq,
        unit_system=case.units_system,
    )
    total_weld_thickness = total_weld["total_thickness"]
    lb = Quantity(
        value=beam_profile["tf"].value + total_weld_thickness.value + 2.0 * tp.value,
        unit=beam_profile["tf"].unit,
    )
    phi_f = _require(case, "design_factors.phi_f", rule_binding)
    capacity, intermediates = compute_column_web_local_crippling_strength(
        lb=lb,
        column_depth=column_profile["d"],
        column_web_thickness=column_profile["tw"],
        column_flange_thickness=column_profile["tf"],
        elastic_modulus=elastic_modulus,
        column_fy=column_fy,
        distance_to_column_end=distance_to_end,
        phi=phi_f,
        unit_system=case.units_system,
    )
    mf_data = _compute_mf_by_side(case, rule_binding)
    mf_vgizq_critico = mf_data["sides"]["izq"]["mfmax"]
    ffu, _ = compute_beam_flange_force_from_mf(
        mf=mf_vgizq_critico,
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    use_continuity_plate = bool(case.geometry.continuity_plate_enabled)
    ru_base = ffu
    demand_force = (
        Quantity(value=min(ru_base.value, capacity.value), unit=ru_base.unit)
        if use_continuity_plate
        else ru_base
    )
    demand_source = (
        "continuity_plate_enabled => Ru_adoptado = min(Ru_base, phi*Rn_cw_v2_col_vgizq)"
        if use_continuity_plate
        else "Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq)"
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=demand_force,
        capacity=capacity,
        equation=(
            "Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); "
            "lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; "
            "phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_eq(6.7-19/6.7-20/6.7-21); "
            "DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq"
        ),
        inputs={
            "mf_vgizq_critico": mf_vgizq_critico.model_dump(),
            "ru_cw_v2_col_vgizq_base": ru_base.model_dump(),
            "ru_cw_v2_col_vgizq_adoptado": demand_force.model_dump(),
            "ru_cw_v2_col_vgizq_source": demand_source,
            "st_col": distance_to_end.model_dump(),
            "d_col": column_profile["d"].model_dump(),
            "lb_col": lb.model_dump(),
            "lb_col_formula": "lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq",
            "fy_col": column_fy.model_dump(),
            "tw_col": column_profile["tw"].model_dump(),
            "tf_col": column_profile["tf"].model_dump(),
            "e_col": elastic_modulus.model_dump(),
            "d_vgizq": beam_profile["d"].model_dump(),
            "tf_vgizq": beam_profile["tf"].model_dump(),
            "tpe_vgizq": tp.model_dump(),
            "t_w4_1_vgizq": backing_thickness.model_dump(),
            "nl_w4_vgizq": case.geometry.nl_w4_vgizq,
            "ductility_vgizq": ductility_vgizq,
            "total_weld_thickness_w4_vgizq": total_weld_thickness.model_dump(),
            "total_weld_thickness_w4_formula": total_weld["equation"],
        },
        intermediates={
            **intermediates,
            "phi_rn_cf_v2_col_vgizq_eq1": capacity.value,
            "rn_nominal_cf_v2_col_vgizq_eq1": intermediates.get("rn_nominal"),
            "continuity_plate_enabled": use_continuity_plate,
        },
        design_factors={"phi_wlc": intermediates.get("phi")},
        units_trace={"ffu": demand_force.unit, "capacity": capacity.unit},
    )


def run_column_step4_2_web_local_buckling(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    def _not_applicable_result(*, reason: str, inputs: dict[str, Any], intermediates: dict[str, Any]) -> CheckResult:
        return CheckResult(
            name=rule_binding.name,
            rule_id=rule_binding.rule_id,
            clause=rule_binding.clause,
            source_document=rule_binding.source_document,
            demand=None,
            capacity=None,
            dcr=None,
            status=CheckStatus.NOT_IMPLEMENTED,
            calculation_memory=CalculationMemory(
                inputs=inputs,
                intermediates=intermediates,
                design_factors={},
                equation=f"No aplica: {reason}",
                units_trace={},
                final_capacity=None,
            ),
            notes="No aplica",
        )

    if case.design_factors.beam_connection_sides != "both_sides":
        return _not_applicable_result(
            reason="Se requiere conexion con vigas a izquierda y derecha simultaneamente.",
            inputs={"beam_connection_sides": case.design_factors.beam_connection_sides},
            intermediates={},
        )

    mu3_vgizq = case.loads.Mu3_vgizq
    mu3_vgder = case.loads.Mu3_vgder
    pu_vgizq = case.loads.pu_viga_left
    pu_vgder = case.loads.pu_viga_right
    missing_fields: list[str] = []
    if mu3_vgizq is None:
        missing_fields.append("loads.Mu3_vgizq")
    if mu3_vgder is None:
        missing_fields.append("loads.Mu3_vgder")
    if pu_vgizq is None:
        missing_fields.append("loads.pu_viga_left")
    if pu_vgder is None:
        missing_fields.append("loads.pu_viga_right")
    if missing_fields:
        return _not_applicable_result(
            reason=(
                "Faltan datos para evaluar la condicion de aplicabilidad de WCB: "
                + ", ".join(missing_fields)
            ),
            inputs={"missing_fields": missing_fields},
            intermediates={},
        )

    beam_profile_izq = _beam_profile_by_side(case, "izq")
    beam_profile_der = _beam_profile_by_side(case, "der")
    force_mu3_vgizq, _ = compute_beam_flange_force_from_mf(
        mf=mu3_vgizq,
        beam_depth=beam_profile_izq["d"],
        beam_flange_thickness=beam_profile_izq["tf"],
        unit_system=case.units_system,
    )
    force_mu3_vgder, _ = compute_beam_flange_force_from_mf(
        mf=mu3_vgder,
        beam_depth=beam_profile_der["d"],
        beam_flange_thickness=beam_profile_der["tf"],
        unit_system=case.units_system,
    )
    force_mu3_vgizq = to_design_force_unit(force_mu3_vgizq, case.units_system)
    force_mu3_vgder = to_design_force_unit(force_mu3_vgder, case.units_system)
    pu_vgizq = to_design_force_unit(pu_vgizq, case.units_system)
    pu_vgder = to_design_force_unit(pu_vgder, case.units_system)

    cond_left = -force_mu3_vgizq.value + 0.5 * pu_vgizq.value
    cond_right = -force_mu3_vgder.value + 0.5 * pu_vgder.value
    cond_tol = 1e-9
    same_sign = (cond_left > cond_tol and cond_right > cond_tol) or (
        cond_left < -cond_tol and cond_right < -cond_tol
    )
    if not same_sign:
        return _not_applicable_result(
            reason=(
                "No se cumple la condicion de mismo signo entre fuerzas de ambos lados: "
                "F_left y F_right deben ser ambas de traccion o ambas de compresion."
            ),
            inputs={
                "mu3_vgizq": mu3_vgizq.model_dump(),
                "mu3_vgder": mu3_vgder.model_dump(),
                "pu_vgizq": pu_vgizq.model_dump(),
                "pu_vgder": pu_vgder.model_dump(),
                "d_vgizq": beam_profile_izq["d"].model_dump(),
                "tf_vgizq": beam_profile_izq["tf"].model_dump(),
                "d_vgder": beam_profile_der["d"].model_dump(),
                "tf_vgder": beam_profile_der["tf"].model_dump(),
            },
            intermediates={
                "cond_left_force": cond_left,
                "cond_right_force": cond_right,
                "cond_tolerance": "1e-9",
                "same_sign": same_sign,
            },
        )

    ru_expr_neg = -force_mu3_vgizq.value + pu_vgizq.value
    ru_expr_pos = force_mu3_vgizq.value + pu_vgizq.value
    ru = Quantity(value=max(abs(ru_expr_neg), abs(ru_expr_pos)), unit=pu_vgizq.unit)

    column_profile = _column_profile(case)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    kc_col = _profile_kdes(column_profile, role="column", rule_binding=rule_binding)
    st_col = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)
    h_col = Quantity(value=column_profile["d"].value - 2.0 * kc_col.value, unit=column_profile["d"].unit)
    ct_col = 0.5 if st_col.value < 0.5 * column_profile["d"].value else 1.0
    phi_wcb = _require(case, "design_factors.phi_f", rule_binding)

    backing_thickness = _require(case, "geometry.t_w4_1_vgizq", rule_binding)
    ductility_vgizq = case.design_factors.member_ductility_demand_column
    if ductility_vgizq is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[
                "design_factors.member_ductility_demand_column",
            ],
            message="Required column ductility demand is missing.",
        )
    nl_w4_vgizq: int | None = None
    if str(ductility_vgizq).strip().lower() == "low":
        nl_w4_vgizq = _require(case, "geometry.nl_w4_vgizq", rule_binding)
    total_weld = compute_total_weld_4_thickness(
        backing_thickness=backing_thickness,
        ductility_demand=str(ductility_vgizq),
        weld_lines=nl_w4_vgizq if nl_w4_vgizq is not None else case.geometry.nl_w4_vgizq,
        unit_system=case.units_system,
    )
    total_weld_thickness = total_weld["total_thickness"]

    capacity, intermediates = compute_column_web_local_buckling_strength(
        ct=ct_col,
        column_web_thickness=column_profile["tw"],
        clear_web_depth=h_col,
        elastic_modulus=elastic_modulus,
        column_fy=column_fy,
        phi=phi_wcb,
        unit_system=case.units_system,
    )
    use_continuity_plate = bool(case.geometry.continuity_plate_enabled)
    demand_force = (
        Quantity(value=min(ru.value, capacity.value), unit=ru.unit)
        if use_continuity_plate
        else ru
    )
    demand_source = (
        "continuity_plate_enabled => Ru_adoptado = min(Ru_base, phi*Rn_cw_v2_col_vgizq)"
        if use_continuity_plate
        else "Ru_cw_v2_col_vgizq = max(|-Mu3/(d-tf)+Pu|, |Mu3/(d-tf)+Pu|)"
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=demand_force,
        capacity=capacity,
        equation=(
            "Condicion aplicabilidad: "
            "same_sign(F_left, F_right), con F_left = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq "
            "y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; "
            "Ru_cw_v2_col_vgizq = max(|-Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|, |Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|); "
            "h_col = d_col - 2*kc_col; "
            "phi*Rn_cw_v2_col_vgizq = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col"
        ),
        inputs={
            "mu3_vgizq": mu3_vgizq.model_dump(),
            "mu3_vgder": mu3_vgder.model_dump(),
            "pu_vgizq": pu_vgizq.model_dump(),
            "pu_vgder": pu_vgder.model_dump(),
            "d_vgizq": beam_profile_izq["d"].model_dump(),
            "tf_vgizq": beam_profile_izq["tf"].model_dump(),
            "d_vgder": beam_profile_der["d"].model_dump(),
            "tf_vgder": beam_profile_der["tf"].model_dump(),
            "st_col": st_col.model_dump(),
            "d_col": column_profile["d"].model_dump(),
            "kc_col": kc_col.model_dump(),
            "h_col": h_col.model_dump(),
            "fy_col": column_fy.model_dump(),
            "e_col": elastic_modulus.model_dump(),
            "tw_col": column_profile["tw"].model_dump(),
            "t_w4_1_vgizq": backing_thickness.model_dump(),
            "nl_w4_vgizq": case.geometry.nl_w4_vgizq,
            "ductility_vgizq": ductility_vgizq,
            "total_weld_thickness_w4_vgizq": total_weld_thickness.model_dump(),
            "total_weld_thickness_w4_formula": total_weld["equation"],
            "ru_cw_v2_col_vgizq_base": ru.model_dump(),
            "ru_cw_v2_col_vgizq_adoptado": demand_force.model_dump(),
            "ru_cw_v2_col_vgizq_source": demand_source,
            "continuity_plate_enabled": use_continuity_plate,
        },
        intermediates={
            **intermediates,
            "cond_left_force": cond_left,
            "cond_right_force": cond_right,
            "cond_tolerance": "1e-9",
            "same_sign": same_sign,
            "applicability_condition_met": True,
            "ru_expr_neg": ru_expr_neg,
            "ru_expr_pos": ru_expr_pos,
            "phi_rn_cf_v2_col_vgizq_eq_wcb": capacity.value,
            "continuity_plate_enabled": use_continuity_plate,
        },
        design_factors={"phi_wcb": phi_wcb},
        units_trace={"demand": ru.unit, "capacity": capacity.unit},
    )


def run_column_step5_panel_zone_shear_wpzs(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    inelastic_panel_zone = case.geometry.panel_zone_inelastic_deformation_considered
    if inelastic_panel_zone is None:
        legacy_package = case.geometry.panel_zone_equation_package
        if legacy_package is None:
            raise missing_required_input_error(
                rule_id=rule_binding.rule_id,
                source_document=rule_binding.source_document,
                missing_fields=["geometry.panel_zone_inelastic_deformation_considered"],
                message=(
                    "Required input 'geometry.panel_zone_inelastic_deformation_considered' is missing for WPZS. "
                    "Set false to use J10-9/J10-10, or true to use J10-11/J10-12."
                ),
            )
        inelastic_panel_zone = str(legacy_package).strip().lower() == "b"
    package = "b" if bool(inelastic_panel_zone) else "a"
    column_profile = _column_profile(case)
    ag_col = column_profile.get("ag")
    if ag_col is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["sections.column_shape -> ag (catalog)"],
            message=(
                "Column gross area 'Ag' is required from sections catalog for WPZS (J10.6) "
                "and was not found for the selected column shape."
            ),
        )
    fy_col = _require(case, "materials.column_fy", rule_binding)
    pu_col = to_design_force_unit(_require(case, "loads.pu_columna", rule_binding), case.units_system)
    force_unit = "kip" if case.units_system == UnitSystem.US else "kN"
    py_value = fy_col.value * ag_col.value
    if case.units_system == UnitSystem.SI:
        py_value /= 1000.0
    py_col = Quantity(value=py_value, unit=force_unit)
    alpha = 1.0  # LRFD per AISC 360-22 J10.6
    alpha_pr_col = Quantity(value=alpha * abs(pu_col.value), unit=pu_col.unit)

    ductility_col = case.design_factors.member_ductility_demand_column
    if ductility_col is not None and str(ductility_col).strip().lower() == "low":
        raise ValueError(
            "WPZS with demanda_ductilidad_col='low' is not implemented yet in this repository."
        )

    active_sides = _active_beam_sides(case)
    mf_data = _compute_mf_by_side(case, rule_binding)
    mpr_data = _compute_mpr_by_side(case, rule_binding)
    vh_data = _compute_vh_by_side(case, rule_binding)
    sh_data = _compute_sh_by_side(case, rule_binding)
    hb_col = _require(case, "geometry.hb_col", rule_binding)
    ht_col = _require(case, "geometry.ht_col", rule_binding)
    if hb_col.unit != ht_col.unit:
        raise ValueError(
            "Incompatible units between geometry.hb_col and geometry.ht_col; both must use the same unit."
        )
    hb_plus_ht = hb_col.value + ht_col.value
    if hb_plus_ht <= 0.0:
        raise ValueError("Sum of hb_col + ht_col must be positive to compute Vc_col.")

    expected_moment_unit = "kip-in" if case.units_system == UnitSystem.US else "kN-mm"
    sum_mbe_col = 0.0
    sum_mf_over_z = 0.0
    side_inputs: dict[str, Any] = {}
    side_intermediates: dict[str, Any] = {}
    beam_depth_candidates: dict[str, Quantity] = {}
    mbe_by_side: dict[str, dict[str, Quantity]] = {}
    mf_force_by_side: dict[str, dict[str, Quantity]] = {}
    for side in active_sides:
        side_tag = "vgizq" if side == "izq" else "vgder"
        beam_profile = _beam_profile_by_side(case, side)
        beam_depth_candidates[side] = beam_profile["d"]
        mpr_side = mpr_data["sides"][side]["mpr"]
        vhmax_side = vh_data["sides"][side]["vhmax"]
        vhmin_side = vh_data["sides"][side]["vhmin"]
        sh_side = sh_data["sides"][side]["sh"]
        if mpr_side.unit != expected_moment_unit:
            raise ValueError(
                f"Invalid unit for Mpr_{side_tag}. Expected '{expected_moment_unit}', got '{mpr_side.unit}'."
            )
        if sh_side.unit != column_profile["d"].unit:
            raise ValueError(
                f"Incompatible units between Sh_{side_tag} ('{sh_side.unit}') and d_col ('{column_profile['d'].unit}')."
            )
        arm_side = Quantity(
            value=sh_side.value + 0.5 * column_profile["d"].value,
            unit=sh_side.unit,
        )
        mbe_col_side_max = Quantity(
            value=mpr_side.value + vhmax_side.value * arm_side.value,
            unit=expected_moment_unit,
        )
        mbe_col_side_min = Quantity(
            value=mpr_side.value + vhmin_side.value * arm_side.value,
            unit=expected_moment_unit,
        )

        mf_col_face_side_max = mf_data["sides"][side]["mfmax"]
        mf_col_face_side_min = mf_data["sides"][side]["mfmin"]
        f_mf_col_side_max, f_mf_trace = compute_beam_flange_force_from_mf(
            mf=mf_col_face_side_max,
            beam_depth=beam_profile["d"],
            beam_flange_thickness=beam_profile["tf"],
            unit_system=case.units_system,
        )
        f_mf_col_side_min, _ = compute_beam_flange_force_from_mf(
            mf=mf_col_face_side_min,
            beam_depth=beam_profile["d"],
            beam_flange_thickness=beam_profile["tf"],
            unit_system=case.units_system,
        )
        mbe_by_side[side] = {"max": mbe_col_side_max, "min": mbe_col_side_min}
        mf_force_by_side[side] = {"max": f_mf_col_side_max, "min": f_mf_col_side_min}
        side_inputs[f"mpr_{side_tag}"] = mpr_side.model_dump()
        side_inputs[f"vh_{side_tag}_max"] = vhmax_side.model_dump()
        side_inputs[f"vh_{side_tag}_min"] = vhmin_side.model_dump()
        side_inputs[f"sh_{side_tag}"] = sh_side.model_dump()
        side_inputs[f"mbe_col_{side_tag}_max"] = mbe_col_side_max.model_dump()
        side_inputs[f"mbe_col_{side_tag}_min"] = mbe_col_side_min.model_dump()
        side_inputs[f"mf_{side_tag}_max"] = mf_col_face_side_max.model_dump()
        side_inputs[f"mf_{side_tag}_min"] = mf_col_face_side_min.model_dump()
        side_inputs[f"db_{side_tag}"] = beam_profile["d"].model_dump()
        side_inputs[f"tf_{side_tag}"] = beam_profile["tf"].model_dump()
        side_intermediates[f"z_{side_tag}"] = f_mf_trace["lever_arm"]
        side_intermediates[f"f_mf_{side_tag}_max"] = f_mf_col_side_max.value
        side_intermediates[f"f_mf_{side_tag}_min"] = f_mf_col_side_min.value
        side_intermediates[f"arm_center_col_{side_tag}"] = arm_side.value

    if len(active_sides) == 2 and "izq" in mbe_by_side and "der" in mbe_by_side:
        mbe_comb_1 = mbe_by_side["izq"]["max"].value + mbe_by_side["der"]["min"].value
        mbe_comb_2 = mbe_by_side["izq"]["min"].value + mbe_by_side["der"]["max"].value
        sum_mbe_col = max(mbe_comb_1, mbe_comb_2)
        mfz_comb_1 = mf_force_by_side["izq"]["max"].value + mf_force_by_side["der"]["min"].value
        mfz_comb_2 = mf_force_by_side["izq"]["min"].value + mf_force_by_side["der"]["max"].value
        sum_mf_over_z = max(mfz_comb_1, mfz_comb_2)
        side_intermediates["sum_mbe_col_combo_1"] = mbe_comb_1
        side_intermediates["sum_mbe_col_combo_2"] = mbe_comb_2
        side_intermediates["sum_mf_over_z_col_combo_1"] = mfz_comb_1
        side_intermediates["sum_mf_over_z_col_combo_2"] = mfz_comb_2
    else:
        only_side = active_sides[0]
        sum_mbe_col = max(
            mbe_by_side[only_side]["max"].value,
            mbe_by_side[only_side]["min"].value,
        )
        sum_mf_over_z = max(
            mf_force_by_side[only_side]["max"].value,
            mf_force_by_side[only_side]["min"].value,
        )

    vc2_col = Quantity(value=sum_mbe_col / hb_plus_ht, unit=force_unit)
    demand = Quantity(value=sum_mf_over_z - vc2_col.value, unit=force_unit)
    db_side_for_rn, db_col = _select_max_quantity_by_side(beam_depth_candidates)

    use_w7 = bool(case.geometry.use_weld_7_col)
    n_dp_col_raw = case.geometry.doubler_plate_count
    n_dp_col = int(n_dp_col_raw) if n_dp_col_raw is not None else 1
    if n_dp_col <= 0:
        raise ValueError("geometry.doubler_plate_count (n_dp_col) must be >= 1 for WPZS Rn formulation.")
    t_dp_col = case.geometry.doubler_plate_thickness
    tw_col = column_profile["tw"]
    if t_dp_col is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=["geometry.doubler_plate_thickness"],
            message="Required input 'geometry.doubler_plate_thickness' is required for WPZS Rn formulation.",
        )
    if t_dp_col.unit != tw_col.unit:
        if t_dp_col.unit == "mm" and tw_col.unit == "in":
            t_dp_col_eff = Quantity(value=t_dp_col.value / 25.4, unit="in")
        elif t_dp_col.unit == "in" and tw_col.unit == "mm":
            t_dp_col_eff = Quantity(value=t_dp_col.value * 25.4, unit="mm")
        else:
            raise ValueError(
                f"Incompatible units between t_dp_col ('{t_dp_col.unit}') and tw_col ('{tw_col.unit}') for WPZS."
            )
    else:
        t_dp_col_eff = t_dp_col
    t_dp_total_eff = Quantity(value=t_dp_col_eff.value * float(n_dp_col), unit=t_dp_col_eff.unit)

    rn1_wpz_nominal = Quantity(
        value=0.60 * fy_col.value * column_profile["d"].value * tw_col.value,
        unit="kN" if case.units_system == UnitSystem.SI else "kip",
    )
    rn2_wpz_nominal = Quantity(
        value=0.60 * fy_col.value * column_profile["d"].value * t_dp_total_eff.value,
        unit="kN" if case.units_system == UnitSystem.SI else "kip",
    )
    if case.units_system == UnitSystem.SI:
        rn1_wpz_nominal = Quantity(value=rn1_wpz_nominal.value / 1000.0, unit=rn1_wpz_nominal.unit)
        rn2_wpz_nominal = Quantity(value=rn2_wpz_nominal.value / 1000.0, unit=rn2_wpz_nominal.unit)

    if use_w7:
        tw_wpz_effective = Quantity(value=tw_col.value + t_dp_total_eff.value, unit=tw_col.unit)
        rn_base_formula_text = "Rn_wpz_v2_col = 0.60*Fy_col*d_col*(tw_col + n_dp_col*t_dp_col)"
        rn1_for_report = None
        rn2_for_report = None
    else:
        tw_wpz_effective = Quantity(value=min(tw_col.value, t_dp_total_eff.value), unit=tw_col.unit)
        rn_base_formula_text = (
            "Rn1_wpz_v2_col = 0.60*Fy_col*d_col*tw_col; "
            "Rn2_wpz_v2_col = 0.60*Fy_col*d_col*(n_dp_col*t_dp_col); "
            "Rn_wpz_v2_col = min{Rn1_wpz_v2_col, Rn2_wpz_v2_col}"
        )
        rn1_for_report = rn1_wpz_nominal
        rn2_for_report = rn2_wpz_nominal

    phi_wpzs = float(_require(case, "design_factors.phi_d", rule_binding))
    capacity, intermediates = compute_column_panel_zone_shear_strength_j10_6(
        package=str(package),
        alpha_pr=alpha_pr_col,
        py=py_col,
        column_fy=fy_col,
        column_depth=column_profile["d"],
        column_web_thickness=tw_wpz_effective,
        column_flange_width=column_profile["bf"],
        beam_depth=db_col,
        column_flange_thickness=column_profile["tf"],
        phi=phi_wpzs,
        unit_system=case.units_system,
    )

    db_symbol = "d_vgizq" if db_side_for_rn == "izq" else "d_vgder"
    eq_case = str(intermediates.get("eq_case"))
    if eq_case == "J10-9":
        equation = f"{rn_base_formula_text} (J10-9)"
    elif eq_case == "J10-10":
        equation = f"{rn_base_formula_text}*(1.4 - Pr_col/Py_col) (J10-10)"
    elif eq_case == "J10-11":
        equation = (
            f"{rn_base_formula_text}*(1 + 3*bcf_col*tcf_col^2/({db_symbol}*d_col*tw_col)) "
            "(J10-11)"
        )
    elif eq_case == "J10-12":
        equation = (
            f"{rn_base_formula_text}*(1 + 3*bcf_col*tcf_col^2/({db_symbol}*d_col*tw_col))"
            "*(1.9 - 1.2*Pr_col/Py_col) (J10-12)"
        )
    else:
        equation = "Rn_wpzs_col = n/a"
    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation=equation,
        inputs={
            "consideracion_deformacion_inelastica_zona_panel": bool(inelastic_panel_zone),
            "package_wpzs": package,
            "eq_case_wpzs": eq_case,
            "phi_wpzs": phi_wpzs,
            "alpha": alpha,
            "hb_col": hb_col.model_dump(),
            "ht_col": ht_col.model_dump(),
            "vc2_col": vc2_col.model_dump(),
            "sum_mbe_col": {"value": sum_mbe_col, "unit": expected_moment_unit},
            "sum_mf_over_z_col": {"value": sum_mf_over_z, "unit": force_unit},
            "ru_wpzs_col": demand.model_dump(),
            "pu_col": pu_col.model_dump(),
            "pr_col": alpha_pr_col.model_dump(),
            "alpha_pr_col": alpha_pr_col.model_dump(),
            "py_col": py_col.model_dump(),
            "ag_col": ag_col.model_dump(),
            "fy_col": fy_col.model_dump(),
            "d_col": column_profile["d"].model_dump(),
            "tw_col": column_profile["tw"].model_dump(),
            "t_dp_col": t_dp_col.model_dump(),
            "n_dp_col": n_dp_col,
            "t_dp_total_col": t_dp_total_eff.model_dump(),
            "use_weld_7_col": use_w7,
            "tw_wpz_effective_col": tw_wpz_effective.model_dump(),
            "rn1_wpz_v2_col": rn1_for_report.model_dump() if rn1_for_report is not None else None,
            "rn2_wpz_v2_col": rn2_for_report.model_dump() if rn2_for_report is not None else None,
            "bcf_col": column_profile["bf"].model_dump(),
            "tcf_col": column_profile["tf"].model_dump(),
            "db_col": db_col.model_dump(),
            "db_col_source_side": db_side_for_rn,
            **side_inputs,
        },
        intermediates={
            "alpha_pr_over_py": intermediates.get("alpha_pr_over_py"),
            "panel_factor": intermediates.get("panel_factor"),
            "rn_nominal_wpzs_col": intermediates.get("rn_nominal"),
            "package_wpzs": intermediates.get("package"),
            "eq_case_wpzs": intermediates.get("eq_case"),
            "sum_mbe_over_hb_plus_ht_formula": "Vc2_col = sum_Mbe_col/(hb_col + ht_col)",
            "ru_wpz_formula": "Ru_wpz_v2_col = sum_Mf_col/(db - tf) - Vc2_col",
            **side_intermediates,
        },
        design_factors={"phi_wpzs": phi_wpzs, "alpha": alpha},
        units_trace={"demand": demand.unit, "capacity": capacity.unit},
    )


def run_column_step5_continuity_plate_strength(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    mf, _, _ = _select_mf_for_design(case, rule_binding)
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
    continuity_capacity = _get_procedure_optional(case, "continuity_plate_available_strength")
    if continuity_capacity is None:
        return CheckResult(
            name=rule_binding.name,
            rule_id=rule_binding.rule_id,
            clause=rule_binding.clause,
            source_document=rule_binding.source_document,
            demand=required_fsu,
            capacity=None,
            dcr=None,
            status=CheckStatus.NOT_IMPLEMENTED,
            calculation_memory=CalculationMemory(
                inputs={
                    "ffu": ffu.model_dump(),
                    "continuity_plate_available_strength": None,
                    "missing_fields": ["procedure.continuity_plate_available_strength"],
                },
                intermediates={"min_design_strength": min_strength},
                design_factors={},
                equation=(
                    "Fsu = Ffu - min(Rn) (Eq. 6.7-22). "
                    "Explicit continuity-plate capacity is required; no auto-capacity is allowed."
                ),
                units_trace={"fsu_required": required_fsu.unit, "capacity": "n/a"},
                final_capacity=None,
            ),
            notes=None,
        )

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
    vu_connection, vu_source = _select_vu_connection_for_design(case, rule_binding)
    demand = Quantity(value=0.5 * vu_connection.value, unit=vu_connection.unit)
    capacity = _get_procedure_optional(case, "panel_zone_capacity")
    if capacity is None:
        return CheckResult(
            name=rule_binding.name,
            rule_id=rule_binding.rule_id,
            clause=rule_binding.clause,
            source_document=rule_binding.source_document,
            demand=demand,
            capacity=None,
            dcr=None,
            status=CheckStatus.NOT_IMPLEMENTED,
            calculation_memory=CalculationMemory(
                inputs={
                    "panel_zone_demand_derived": demand.model_dump(),
                    "vu_connection_derived": vu_connection.model_dump(),
                    "vu_connection_source": vu_source,
                    "panel_zone_capacity": None,
                    "missing_fields": ["procedure.panel_zone_capacity"],
                },
                intermediates={},
                design_factors={},
                equation=(
                    "Panel zone check per Section 2.7 / AISC Seismic Provisions requires explicit capacity. "
                    "No auto-capacity is allowed."
                ),
                units_trace={"panel_zone_demand": demand.unit, "capacity": "n/a"},
                final_capacity=None,
            ),
            notes=None,
        )
    return _build_result(
        rule_binding=rule_binding,
        demand=demand,
        capacity=capacity,
        equation="Panel zone check per Section 2.7 / AISC Seismic Provisions",
        inputs={
            "panel_zone_demand_derived": demand.model_dump(),
            "vu_connection_derived": vu_connection.model_dump(),
            "vu_connection_source": vu_source,
            "panel_zone_capacity": capacity.model_dump(),
        },
        intermediates={"panel_zone_demand_factor_from_vu": 0.5},
        design_factors={},
        units_trace={"demand": demand.unit, "capacity": capacity.unit},
    )


def run_column_step7_column_beam_moment_ratio(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    ratio = _require(case, "design_factors.column_beam_moment_ratio", rule_binding)
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


def run_step6_1_bolt_tension_rupture_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step6_1_bolt_tension_rupture,
        side="izq",
    )


def run_step6_2_bolt_shear_rupture_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step6_2_bolt_shear_rupture,
        side="izq",
    )


def run_step7_1_1_end_plate_flexural_yielding_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_1_1_end_plate_flexural_yielding,
        side="izq",
    )


def run_step7_2_1_end_plate_shear_yielding_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_2_1_end_plate_shear_yielding,
        side="izq",
    )


def run_step7_2_2_end_plate_shear_rupture_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_2_2_end_plate_shear_rupture,
        side="izq",
    )


def run_step7_3_1_end_plate_hole_tearout_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_3_1_end_plate_hole_tearout,
        side="izq",
    )


def run_step7_3_2_end_plate_hole_bearing_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_3_2_end_plate_hole_bearing,
        side="izq",
    )


def run_step8_1_1_stiffener_weld_tension_rupture_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step8_1_1_stiffener_weld_tension_rupture,
        side="izq",
    )


def run_step9_1_1_stiffener_beam_weld_shear_rupture_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step9_1_1_stiffener_beam_weld_shear_rupture,
        side="izq",
    )


def run_step10_1_1_beam_flange_end_plate_weld_tension_rupture_vgizq(
    case: AISC358MomentCase,
    rule_binding: object,
) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step10_1_1_beam_flange_end_plate_weld_tension_rupture,
        side="izq",
    )


def run_step11_1_1_beam_shear_yielding_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step10_1_1_beam_shear_yielding,
        side="izq",
    )


def run_step11_1_1_beam_web_end_plate_weld_tension_rupture_vgizq(
    case: AISC358MomentCase,
    rule_binding: object,
) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step11_1_1_beam_web_end_plate_weld_tension_rupture,
        side="izq",
    )


def run_column_step1_flange_yielding_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step1_flange_yielding,
        side="izq",
    )


def run_column_step3_web_local_yielding_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step3_web_local_yielding,
        side="izq",
    )


def run_column_step4_web_local_crippling_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step4_web_local_crippling,
        side="izq",
    )


def run_column_step4_2_web_local_buckling_vgizq(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    if case.design_factors.beam_connection_sides != "both_sides":
        return run_column_step4_2_web_local_buckling(case, rule_binding)
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step4_2_web_local_buckling,
        side="izq",
    )


def run_step6_1_bolt_tension_rupture_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step6_1_bolt_tension_rupture,
        side="der",
    )


def run_step6_2_bolt_shear_rupture_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step6_2_bolt_shear_rupture,
        side="der",
    )


def run_step7_1_1_end_plate_flexural_yielding_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_1_1_end_plate_flexural_yielding,
        side="der",
    )


def run_step7_2_1_end_plate_shear_yielding_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_2_1_end_plate_shear_yielding,
        side="der",
    )


def run_step7_2_2_end_plate_shear_rupture_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_2_2_end_plate_shear_rupture,
        side="der",
    )


def run_step7_3_1_end_plate_hole_tearout_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_3_1_end_plate_hole_tearout,
        side="der",
    )


def run_step7_3_2_end_plate_hole_bearing_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step7_3_2_end_plate_hole_bearing,
        side="der",
    )


def run_step8_1_1_stiffener_weld_tension_rupture_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step8_1_1_stiffener_weld_tension_rupture,
        side="der",
    )


def run_step9_1_1_stiffener_beam_weld_shear_rupture_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step9_1_1_stiffener_beam_weld_shear_rupture,
        side="der",
    )


def run_step10_1_1_beam_flange_end_plate_weld_tension_rupture_vgder(
    case: AISC358MomentCase,
    rule_binding: object,
) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step10_1_1_beam_flange_end_plate_weld_tension_rupture,
        side="der",
    )


def run_step11_1_1_beam_shear_yielding_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step10_1_1_beam_shear_yielding,
        side="der",
    )


def run_step11_1_1_beam_web_end_plate_weld_tension_rupture_vgder(
    case: AISC358MomentCase,
    rule_binding: object,
) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_step11_1_1_beam_web_end_plate_weld_tension_rupture,
        side="der",
    )


def run_column_step1_flange_yielding_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step1_flange_yielding,
        side="der",
    )


def run_column_step3_web_local_yielding_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step3_web_local_yielding,
        side="der",
    )


def run_column_step4_web_local_crippling_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step4_web_local_crippling,
        side="der",
    )


def run_column_step4_2_web_local_buckling_vgder(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    if case.design_factors.beam_connection_sides != "both_sides":
        return run_column_step4_2_web_local_buckling(case, rule_binding)
    return _evaluate_left_style_rule_for_side(
        case=case,
        rule_binding=rule_binding,
        left_evaluator=run_column_step4_2_web_local_buckling,
        side="der",
    )

