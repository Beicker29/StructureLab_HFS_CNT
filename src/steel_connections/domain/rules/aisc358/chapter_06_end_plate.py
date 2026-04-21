from __future__ import annotations

import math
from typing import Any, Callable

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
)
from steel_connections.codes.engineering.common import (
    compute_bolt_shear_rupture_capacity_per_bolt,
    compute_bolt_tension_rupture_capacity_per_bolt,
)
from steel_connections.codes.engineering.customized import (
    compute_bseep_step6_1_bolt_tension_demand,
    compute_moment_prequalified_step6_1_bolt_tension_demand,
    compute_moment_prequalified_step6_2_bolt_shear_demand,
)
from steel_connections.codes.engineering.geometry import compute_protected_zone_length as compute_protected_zone_length_eq
from steel_connections.codes.engineering.shear import compute_beam_web_shear_yielding_strength
from steel_connections.codes.engineering.weld import (
    WeldFillet,
    compute_plate_shear_demand_from_yielding,
    compute_plate_tension_demand_from_yielding,
)
from steel_connections.data.sections_repository import get_beam_profile_properties, get_column_profile_properties
from steel_connections.models.errors import missing_required_input_error
from steel_connections.models.input import AISC358MomentCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import Quantity, UnitSystem


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


def _column_yc_parameter(case: AISC358MomentCase, rule_binding: object) -> Quantity:
    if case.connection_type == "bueep_4e":
        yc_in = 250.0
    else:
        yc_in = 275.0
    if case.units_system == UnitSystem.US:
        return Quantity(value=yc_in, unit="in")
    return Quantity(value=yc_in * 25.4, unit="mm")


def _compute_mpr(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, float]]:
    fy = _require(case, "materials.beam_fy", rule_binding)
    fu = _require(case, "materials.beam_fu", rule_binding)
    ry = _require(case, "design_factors.ry", rule_binding)
    ze = _beam_plastic_modulus_zx(case, rule_binding)
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


def _derive_stiffener_height_from_de_pfo(*, de: Quantity, pfo: Quantity) -> Quantity:
    return Quantity(value=pfo.value + de.value, unit=pfo.unit)


def _derive_end_plate_height(*, beam_depth: Quantity, de: Quantity, pfo: Quantity) -> Quantity:
    return Quantity(value=beam_depth.value + 2.0 * pfo.value + 2.0 * de.value, unit=beam_depth.unit)


def _derive_stiffener_length_from_hst(*, stiffener_height: Quantity, unit_system: UnitSystem) -> Quantity:
    return compute_minimum_stiffener_length(stiffener_height, unit_system)


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
    raise ValueError(
        "Required input 'design_factors.beam_connection_sides' is missing or invalid. "
        "No default value is allowed under zero-guess policy."
    )


def _require_geometry_by_side(
    case: AISC358MomentCase,
    *,
    base_field: str,
    side: str,
    rule_binding: object,
) -> tuple[Quantity, str]:
    field_name = f"{base_field}_{side}"
    value = getattr(case.geometry, field_name)
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
    mpr, _ = _compute_mpr(case, rule_binding)
    force_unit = "kip" if case.units_system == UnitSystem.US else "kN"
    sides = _active_beam_sides(case)
    side_data: dict[str, Any] = {}

    for side in sides:
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
        base_shear = (2.0 * mpr.value) / lh.value
        vhmax = Quantity(value=base_shear + vgravity.value, unit=force_unit)
        vhmin = Quantity(value=base_shear - vgravity.value, unit=force_unit)
        side_data[side] = {
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
        "mpr": mpr,
        "sides": side_data,
        "governing_vhmax_side": governing_side,
        "governing_vhmax": governing_vhmax,
    }


def _compute_mf_by_side(
    case: AISC358MomentCase,
    rule_binding: object,
) -> dict[str, Any]:
    vh_data = _compute_vh_by_side(case, rule_binding)
    mpr = vh_data["mpr"]
    sh = _compute_sh(case, rule_binding)
    side_data: dict[str, Any] = vh_data["sides"]
    for side, data in side_data.items():
        vhmax = data["vhmax"]
        vhmin = data["vhmin"]
        data["mf_derivation_sh"] = sh
        data["mfmax"] = compute_mf(
            mpr=mpr,
            vh=vhmax,
            sh=sh,
            unit_system=case.units_system,
        )
        data["mfmin"] = compute_mf(
            mpr=mpr,
            vh=vhmin,
            sh=sh,
            unit_system=case.units_system,
        )

    mfmax_values = {side: data["mfmax"] for side, data in side_data.items()}
    governing_side, governing_mfmax = _select_max_quantity_by_side(mfmax_values)
    return {
        **vh_data,
        "sh": sh,
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


def _compute_sh(case: AISC358MomentCase, rule_binding: object) -> Quantity:
    beam_profile = _beam_profile(case)
    stiffener_length = case.geometry.stiffener_length
    end_plate_thickness = case.geometry.end_plate_thickness
    if case.connection_type == "bueep_4e":
        stiffener_length = None
        end_plate_thickness = None
    else:
        de = _require(case, "geometry.de", rule_binding)
        pfo = _require(case, "geometry.pfo", rule_binding)
        hst = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo)
        stiffener_length = _derive_stiffener_length_from_hst(
            stiffener_height=hst,
            unit_system=case.units_system,
        )
        end_plate_thickness = _require(case, "geometry.end_plate_thickness", rule_binding)
    return compute_sh(
        connection_type=case.connection_type,
        beam_depth=beam_profile["d"],
        beam_flange_width=beam_profile["bf"],
        stiffener_length=stiffener_length,
        end_plate_thickness=end_plate_thickness,
        unit_system=case.units_system,
    )


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


def _compute_end_plate_h_distances(case: AISC358MomentCase, rule_binding: object) -> dict[str, Quantity]:
    beam_profile = _beam_profile(case)
    beam_depth = beam_profile["d"]
    beam_flange_thickness = beam_profile["tf"]
    pb = _require(case, "geometry.pb", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pfi = _require(case, "geometry.pfi", rule_binding)
    tcp = _require(case, "geometry.continuity_plate_thickness", rule_binding)
    pso = pfo
    psi = Quantity(value=pfi.value + beam_flange_thickness.value - tcp.value, unit=pfi.unit)
    h1 = Quantity(
        value=beam_depth.value - 0.5 * beam_flange_thickness.value + pso.value + pb.value,
        unit=beam_depth.unit,
    )
    h2 = Quantity(
        value=beam_depth.value - 0.5 * beam_flange_thickness.value + pso.value,
        unit=beam_depth.unit,
    )
    h3 = Quantity(
        value=beam_depth.value - 1.5 * beam_flange_thickness.value - psi.value,
        unit=beam_depth.unit,
    )
    h4 = Quantity(
        value=beam_depth.value - 1.5 * beam_flange_thickness.value - psi.value - pb.value,
        unit=beam_depth.unit,
    )
    return {"h1": h1, "h2": h2, "h3": h3, "h4": h4}


def _compute_tension_bolt_line_distances(case: AISC358MomentCase, rule_binding: object) -> list[Quantity]:
    h = _compute_end_plate_h_distances(case, rule_binding)
    if case.connection_type == "bseep_8es":
        return [h["h1"], h["h2"], h["h3"], h["h4"]]
    return [h["h1"], h["h2"]]


def _compute_beam_available_shear_strength(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, Any]]:
    beam_profile = _beam_profile(case)
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
    pb = _require(case, "geometry.pb", rule_binding)
    h = _compute_end_plate_h_distances(case, rule_binding)
    h1 = h["h1"]
    h2 = h["h2"]
    h3 = h["h3"]
    h4 = h["h4"]

    for name, value in {
        "bp": bp.value,
        "g": g.value,
        "pfi": pfi_raw.value,
        "pfo": pfo.value,
        "de": de.value,
    }.items():
        if value <= 0.0:
            raise ValueError(f"Invalid geometry for Yp: '{name}' must be positive.")

    s = Quantity(value=0.5 * math.sqrt(bp.value * g.value), unit=bp.unit)
    pfi_eff = Quantity(value=min(pfi_raw.value, s.value), unit=pfi_raw.unit)
    de_le_s = de.value <= s.value + 1e-9

    table_ref = ""
    case_ref = "N/A"
    formula_text = ""

    if case.connection_type == "bueep_4e":
        # Table 6.2
        yp_value = (
            (bp.value / 2.0)
            * (
                h2.value * ((1.0 / pfi_eff.value) + (1.0 / s.value))
                + h1.value * (1.0 / pfo.value)
                - 0.5
            )
            + (2.0 / g.value) * (h2.value * (pfi_eff.value + s.value))
        )
        table_ref = "AISC 358-22 Table 6.2"
        formula_text = (
            "Yp = bp/2*[h2*(1/pfi + 1/s) + h1*(1/pfo) - 1/2] + (2/g)*[h2*(pfi + s)]"
        )
    elif case.connection_type == "bseep_4es":
        # Table 6.3
        if de_le_s:
            yp_value = (
                (bp.value / 2.0)
                * (
                    h2.value * ((1.0 / pfi_eff.value) + (1.0 / s.value))
                    + h1.value * ((1.0 / pfo.value) + (1.0 / (2.0 * de.value)))
                )
                + (2.0 / g.value) * (h2.value * (pfi_eff.value + s.value) + h1.value * (de.value + pfo.value))
            )
            case_ref = "Case 1 (de <= s)"
            formula_text = (
                "Yp = bp/2*[h2*(1/pfi + 1/s) + h1*(1/pfo + 1/(2de))] + "
                "(2/g)*[h2*(pfi + s) + h1*(de + pfo)]"
            )
        else:
            yp_value = (
                (bp.value / 2.0)
                * (
                    h2.value * ((1.0 / pfi_eff.value) + (1.0 / s.value))
                    + h1.value * ((1.0 / s.value) + (1.0 / pfo.value))
                )
                + (2.0 / g.value) * (h2.value * (pfi_eff.value + s.value) + h1.value * (s.value + pfo.value))
            )
            case_ref = "Case 2 (de > s)"
            formula_text = (
                "Yp = bp/2*[h2*(1/pfi + 1/s) + h1*(1/s + 1/pfo)] + "
                "(2/g)*[h2*(pfi + s) + h1*(s + pfo)]"
            )
        table_ref = "AISC 358-22 Table 6.3"
    else:
        # bseep_8es -> Table 6.4
        if de_le_s:
            yp_value = (
                (bp.value / 2.0)
                * (
                    h1.value * (1.0 / (2.0 * de.value))
                    + h2.value * (1.0 / pfo.value)
                    + h3.value * (1.0 / pfi_eff.value)
                    + h4.value * (1.0 / s.value)
                )
                + (2.0 / g.value)
                * (
                    h1.value * (de.value + 3.0 * pb.value / 4.0)
                    + h2.value * (pfo.value + pb.value / 4.0)
                    + h3.value * (pfi_eff.value + 3.0 * pb.value / 4.0)
                    + h4.value * (s.value + pb.value / 4.0)
                )
                + g.value
            )
            case_ref = "Case 1 (de <= s)"
            formula_text = (
                "Yp = bp/2*[h1*(1/(2de)) + h2*(1/pfo) + h3*(1/pfi) + h4*(1/s)] + "
                "(2/g)*[h1*(de + 3pb/4) + h2*(pfo + pb/4) + h3*(pfi + 3pb/4) + h4*(s + pb/4)] + g"
            )
        else:
            yp_value = (
                (bp.value / 2.0)
                * (
                    h1.value * (1.0 / s.value)
                    + h2.value * (1.0 / pfo.value)
                    + h3.value * (1.0 / pfi_eff.value)
                    + h4.value * (1.0 / s.value)
                )
                + (2.0 / g.value)
                * (
                    h1.value * (s.value + pb.value / 4.0)
                    + h2.value * (pfo.value + 3.0 * pb.value / 4.0)
                    + h3.value * (pfi_eff.value + pb.value / 4.0)
                    + h4.value * (s.value + 3.0 * pb.value / 4.0)
                )
                + g.value
            )
            case_ref = "Case 2 (de > s)"
            formula_text = (
                "Yp = bp/2*[h1*(1/s) + h2*(1/pfo) + h3*(1/pfi) + h4*(1/s)] + "
                "(2/g)*[h1*(s + pb/4) + h2*(pfo + 3pb/4) + h3*(pfi + pb/4) + h4*(s + 3pb/4)] + g"
            )
        table_ref = "AISC 358-22 Table 6.4"

    yp = Quantity(value=yp_value, unit=bp.unit)
    return yp, {
        "table_reference": table_ref,
        "case_reference": case_ref,
        "formula": formula_text,
        "s": s.model_dump(),
        "pfi_input": pfi_raw.model_dump(),
        "pfi_effective": pfi_eff.model_dump(),
        "de": de.model_dump(),
        "de_le_s": de_le_s,
    }


def _compute_standard_hole_diameter(*, bolt_diameter: Quantity, unit_system: UnitSystem) -> tuple[Quantity, dict[str, float]]:
    validate_unit = "in" if unit_system == UnitSystem.US else "mm"
    if bolt_diameter.unit != validate_unit:
        raise ValueError(f"Invalid bolt diameter unit. Expected '{validate_unit}'.")
    db_in = bolt_diameter.value if unit_system == UnitSystem.US else bolt_diameter.value / 25.4
    if db_in <= 0.0:
        raise ValueError("Bolt diameter must be positive to derive standard hole diameter.")

    # AISC 360 Table J3.3: up to 7/8 in => d + 1/16; 1 in and larger => d + 1/8.
    hole_add_in = 1.0 / 16.0 if db_in <= (7.0 / 8.0 + 1e-9) else 1.0 / 8.0
    dh_in = db_in + hole_add_in
    if unit_system == UnitSystem.US:
        return Quantity(value=dh_in, unit="in"), {"db_in": db_in, "hole_add_in": hole_add_in}
    return Quantity(value=dh_in * 25.4, unit="mm"), {"db_in": db_in, "hole_add_in": hole_add_in}


def _normalize_end_plate_stiffener_weld_type(raw: str | None) -> str:
    if raw is None:
        return "cjp"
    normalized = raw.strip().lower().replace("-", "_").replace(" ", "_")
    if not normalized:
        return "cjp"
    if normalized in {"cjp", "complete_joint_penetration"}:
        return "cjp"
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
    fy = _require(case, "materials.beam_fy", rule_binding)
    fu = _require(case, "materials.beam_fu", rule_binding)
    ry = _require(case, "design_factors.ry", rule_binding)
    ze = _beam_plastic_modulus_zx(case, rule_binding)
    ze_source = "sections_catalog_zx"
    ze_input = case.procedure.beam_plastic_section_modulus_ze if case.procedure is not None else None
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
            "ze_input": ze_input.model_dump() if ze_input is not None else None,
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
        if side == "der" and stated_side is None:
            stated_side = case.loads.shear_plastic_hinge
        side_inputs[f"stated_vh_{side}max"] = stated_side.model_dump() if stated_side is not None else None
        side_intermediates[f"2mpr_over_lh_{side}"] = side_data["2mpr_over_lh"]
        side_intermediates[f"vh_{side}max"] = side_data["vhmax"].value
        side_intermediates[f"vh_{side}min"] = side_data["vhmin"].value
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
    mf, mf_source, mf_computed = _select_mf_for_design(case, rule_binding)
    fnt = _require(case, "materials.bolt_fnt", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    h_distances = _compute_end_plate_h_distances(case, rule_binding)
    h1 = h_distances["h1"]
    h2 = h_distances["h2"]
    h3 = h_distances["h3"]
    h4 = h_distances["h4"]

    if case.connection_type in {"bseep_4es", "bseep_8es"}:
        pu_result = compute_bseep_step6_1_bolt_tension_demand(
            mf=mf,
            h1=h1,
            h2=h2,
            h3=h3,
            h4=h4,
            connection_type=case.connection_type,
            unit_system=case.units_system,
        )
        rut_b = pu_result["rut_b"]
        sum_h = pu_result["sum_h"].value
        pu_equation = pu_result["equation"]
    else:
        pu_result = compute_moment_prequalified_step6_1_bolt_tension_demand(
            mf=mf,
            h1=h1,
            h2=h2,
            connection_type=case.connection_type,
            unit_system=case.units_system,
        )
        rut_b = pu_result["rut_b"]
        sum_h = pu_result["sum_h"].value
        pu_equation = pu_result["equation"]

    capacity_result = compute_bolt_tension_rupture_capacity_per_bolt(
        bolt_diameter=db,
        bolt_fnt=fnt,
        unit_system=case.units_system,
    )
    rnt_b = capacity_result["rnt_b"]
    phi_rnt_b = capacity_result["phi_rnt_b"]
    bolt_area = capacity_result["bolt_area"].value
    nominal_capacity = rnt_b.value
    phi = capacity_result["phi"]

    return _build_result(
        rule_binding=rule_binding,
        demand=rut_b,
        capacity=phi_rnt_b,
        equation=(
            f"{pu_equation}; "
            "phiRnt_b = phi * Rnt_b, Rnt_b = Ab * Fnt, Ab = pi*db^2/4 (AISC 360-22 J3.7)"
        ),
        inputs={
            "mf": mf.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "h1": h1.model_dump(),
            "h2": h2.model_dump(),
            "h3": h3.model_dump(),
            "h4": h4.model_dump(),
            "bolt_diameter": db.model_dump(),
            "bolt_fnt": fnt.model_dump(),
            "connection_type": case.connection_type,
        },
        intermediates={
            "sum_h": sum_h,
            "bolt_area": bolt_area,
            "rnt_b": rnt_b.value,
            "rut_b": rut_b.value,
            "phi_rnt_b": phi_rnt_b.value,
            "nominal_tension_capacity_per_bolt": nominal_capacity,
        },
        design_factors={"phi": phi},
        units_trace={"rut_b": rut_b.unit, "phi_rnt_b": phi_rnt_b.unit},
    )


def run_step6_2_bolt_shear_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vh_data = _compute_vh_by_side(case, rule_binding)
    vh_computed = vh_data["governing_vhmax"]
    vh, vh_source = _select_stated_vhmax_for_design(case, vh_data)
    fnv = _require(case, "materials.bolt_fnv", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    demand_result = compute_moment_prequalified_step6_2_bolt_shear_demand(
        vhmax=vh,
        connection_type=case.connection_type,
        unit_system=case.units_system,
    )
    nb = demand_result["nb"]
    ruv2_b = demand_result["ruv2_b"]

    capacity_result = compute_bolt_shear_rupture_capacity_per_bolt(
        bolt_diameter=db,
        bolt_fnv=fnv,
        unit_system=case.units_system,
    )
    rnv_b = capacity_result["rnv_b"]
    phi_rnv_b = capacity_result["phi_rnv_b"]
    bolt_area = capacity_result["bolt_area"].value
    nominal_capacity = rnv_b.value
    phi = capacity_result["phi"]

    return _build_result(
        rule_binding=rule_binding,
        demand=ruv2_b,
        capacity=phi_rnv_b,
        equation=(
            "Ruv2_b = Vhmax/nb, phiRnv_b = phi * Rnv_b, Rnv_b = Ab * Fnv, Ab = pi*db^2/4, "
            "nb = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)"
        ),
        inputs={
            "vhmax": vh.model_dump(),
            "vhmax_source": vh_source,
            "vhmax_computed": vh_computed.model_dump(),
            "nb": nb,
            "bolt_diameter": db.model_dump(),
            "bolt_fnv": fnv.model_dump(),
            "connection_type": case.connection_type,
        },
        intermediates={
            "bolt_area": bolt_area,
            "rnv_b": rnv_b.value,
            "ruv2_b": ruv2_b.value,
            "phi_rnv_b": phi_rnv_b.value,
            "nominal_shear_capacity_per_bolt": nominal_capacity,
        },
        design_factors={"phi": phi},
        units_trace={"ruv2_b": ruv2_b.unit, "phi_rnv_b": phi_rnv_b.unit},
    )


def run_step7_1_1_end_plate_flexural_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf, mf_source, mf_computed = _select_mf_for_design(case, rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    fyp = _require(case, "materials.end_plate_fy", rule_binding)
    yp, yp_intermediates = _derive_yp_from_tables_6_2_6_3_6_4(case, rule_binding)

    phi = 0.9
    nominal_moment = (tp.value**2) * fyp.value * yp.value
    design_moment = phi * nominal_moment
    if case.units_system == UnitSystem.SI:
        nominal_moment /= 1000.0
        design_moment /= 1000.0
    phi_mnb = Quantity(value=design_moment, unit=mf.unit)

    return _build_result(
        rule_binding=rule_binding,
        demand=mf,
        capacity=phi_mnb,
        equation="Mup = Mf; phiMnb = phi * tp^2 * Fyp * Yp (AISC 358-22 Eq. 6.7-8)",
        inputs={
            "mf": mf.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "tp": tp.model_dump(),
            "fyp": fyp.model_dump(),
            "yp": yp.model_dump(),
            "yp_source": "derived_from_aisc358_tables_6_2_6_3_6_4",
            "yp_table": yp_intermediates["table_reference"],
            "yp_case": yp_intermediates["case_reference"],
        },
        intermediates={
            "nominal_moment": nominal_moment,
            "design_moment": design_moment,
            **yp_intermediates,
        },
        design_factors={"phi": phi},
        units_trace={"mup": mf.unit, "phi_mnb": phi_mnb.unit},
    )


def run_step7_2_1_end_plate_shear_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf, mf_source, mf_computed = _select_mf_for_design(case, rule_binding)
    beam_profile = _beam_profile(case)
    d = beam_profile["d"]
    tbf = beam_profile["tf"]
    lever_arm = d.value - tbf.value
    if lever_arm <= 0.0:
        raise ValueError("Beam lever arm (d - tbf) must be positive for Step 7.2.1.")

    vub = Quantity(
        value=mf.value / (2.0 * lever_arm),
        unit="kip" if case.units_system == UnitSystem.US else "kN",
    )
    bp = _require(case, "geometry.end_plate_width", rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    fyp = _require(case, "materials.end_plate_fy", rule_binding)
    phi = 0.9
    nominal_shear = 0.6 * fyp.value * bp.value * tp.value
    design_shear = phi * nominal_shear
    if case.units_system == UnitSystem.SI:
        nominal_shear /= 1000.0
        design_shear /= 1000.0
    phi_vnb = Quantity(value=design_shear, unit=vub.unit)

    return _build_result(
        rule_binding=rule_binding,
        demand=vub,
        capacity=phi_vnb,
        equation="Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fyp * bp * tp (AISC 358-22 Eq. 6.7-10)",
        inputs={
            "mf": mf.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "d": d.model_dump(),
            "tbf": tbf.model_dump(),
            "bp": bp.model_dump(),
            "tp": tp.model_dump(),
            "fyp": fyp.model_dump(),
        },
        intermediates={
            "lever_arm": lever_arm,
            "nominal_shear": nominal_shear,
            "design_shear": design_shear,
        },
        design_factors={"phi": phi},
        units_trace={"vup": vub.unit, "phi_vnb": phi_vnb.unit},
    )


def run_step7_2_2_end_plate_shear_rupture(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    mf, mf_source, mf_computed = _select_mf_for_design(case, rule_binding)
    beam_profile = _beam_profile(case)
    d = beam_profile["d"]
    tbf = beam_profile["tf"]
    lever_arm = d.value - tbf.value
    if lever_arm <= 0.0:
        raise ValueError("Beam lever arm (d - tbf) must be positive for Step 7.2.2.")

    vub = Quantity(
        value=mf.value / (2.0 * lever_arm),
        unit="kip" if case.units_system == UnitSystem.US else "kN",
    )
    bp = _require(case, "geometry.end_plate_width", rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    fup = _require(case, "materials.end_plate_fu", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    dh, dh_inter = _compute_standard_hole_diameter(bolt_diameter=db, unit_system=case.units_system)
    net_width = bp.value - 2.0 * dh.value
    if net_width <= 0.0:
        raise ValueError("Net end-plate width (bp - 2*dh) must be positive for Step 7.2.2.")

    phi = 0.9
    nominal_shear = 0.6 * fup.value * tp.value * net_width
    design_shear = phi * nominal_shear
    if case.units_system == UnitSystem.SI:
        nominal_shear /= 1000.0
        design_shear /= 1000.0
    phi_vnb = Quantity(value=design_shear, unit=vub.unit)

    return _build_result(
        rule_binding=rule_binding,
        demand=vub,
        capacity=phi_vnb,
        equation="Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fup * tp * (bp - 2*dh) (AISC 358-22 Eq. 6.7-12)",
        inputs={
            "mf": mf.model_dump(),
            "mf_source": mf_source,
            "mf_computed": mf_computed.model_dump(),
            "d": d.model_dump(),
            "tbf": tbf.model_dump(),
            "bp": bp.model_dump(),
            "tp": tp.model_dump(),
            "fup": fup.model_dump(),
            "db": db.model_dump(),
            "dh": dh.model_dump(),
        },
        intermediates={
            "lever_arm": lever_arm,
            "net_width": net_width,
            "nominal_shear": nominal_shear,
            "design_shear": design_shear,
            **dh_inter,
        },
        design_factors={"phi": phi},
        units_trace={"vup": vub.unit, "phi_vnb": phi_vnb.unit},
    )


def _compute_step7_3_lc(case: AISC358MomentCase, rule_binding: object) -> tuple[Quantity, dict[str, float]]:
    pb = _require(case, "geometry.pb", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pfi = _require(case, "geometry.pfi", rule_binding)
    beam_profile = _beam_profile(case)
    tbf = beam_profile["tf"]
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    dh, dh_inter = _compute_standard_hole_diameter(bolt_diameter=db, unit_system=case.units_system)

    lc_1 = pb.value - dh.value
    lc_2 = pfo.value + pfi.value + tbf.value - dh.value
    if case.connection_type == "bseep_8es":
        lc_value = min(lc_1, lc_2)
        lc_rule = 1.0  # 1 => min(pb-dh, pfo+pfi+tbf-dh)
    else:
        lc_value = lc_2
        lc_rule = 2.0  # 2 => pfo+pfi+tbf-dh
    if lc_value <= 0.0:
        raise ValueError("Computed lc must be positive for Step 7.3 checks.")

    lc = Quantity(value=lc_value, unit=pb.unit)
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
    vh_computed = vh_data["governing_vhmax"]
    vh, vh_source = _select_stated_vhmax_for_design(case, vh_data)
    nb = _compression_bolt_count(case)
    vu2p = Quantity(value=vh.value / float(nb), unit=vh.unit)

    lc, lc_inter = _compute_step7_3_lc(case, rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    fup = _require(case, "materials.end_plate_fu", rule_binding)
    phi = 0.9

    nominal_strength = 1.2 * lc.value * tp.value * fup.value
    design_strength = phi * nominal_strength
    if case.units_system == UnitSystem.SI:
        nominal_strength /= 1000.0
        design_strength /= 1000.0
    phi_vn2p = Quantity(value=design_strength, unit=vu2p.unit)

    return _build_result(
        rule_binding=rule_binding,
        demand=vu2p,
        capacity=phi_vn2p,
        equation="Vu2p = Vhmax/nb; phiVn2p = phi * 1.2 * lc * tp * Fup (AISC 360-22 J3.11a)",
        inputs={
            "vhmax": vh.model_dump(),
            "vhmax_source": vh_source,
            "vhmax_computed": vh_computed.model_dump(),
            "nb": nb,
            "lc": lc.model_dump(),
            "tp": tp.model_dump(),
            "fup": fup.model_dump(),
            "pb": _require(case, "geometry.pb", rule_binding).model_dump(),
            "pfo": _require(case, "geometry.pfo", rule_binding).model_dump(),
            "pfi": _require(case, "geometry.pfi", rule_binding).model_dump(),
            "de": _require(case, "geometry.de", rule_binding).model_dump(),
            "tbf": _beam_profile(case)["tf"].model_dump(),
            "db": _require(case, "geometry.bolt_diameter", rule_binding).model_dump(),
            "dh": Quantity(value=lc_inter["dh"], unit=lc.unit).model_dump(),
        },
        intermediates={
            **lc_inter,
            "vu2p": vu2p.value,
            "nominal_strength": nominal_strength,
            "design_strength": design_strength,
        },
        design_factors={"phi": phi},
        units_trace={"vu2p": vu2p.unit, "phi_vn2p": phi_vn2p.unit},
    )


def run_step7_3_2_end_plate_hole_bearing(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    vh_data = _compute_vh_by_side(case, rule_binding)
    vh_computed = vh_data["governing_vhmax"]
    vh, vh_source = _select_stated_vhmax_for_design(case, vh_data)
    nb = _compression_bolt_count(case)
    vu2p = Quantity(value=vh.value / float(nb), unit=vh.unit)

    lc, lc_inter = _compute_step7_3_lc(case, rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    fup = _require(case, "materials.end_plate_fu", rule_binding)
    db = _require(case, "geometry.bolt_diameter", rule_binding)
    phi = 0.9

    db_plus_1p6mm = db.value + (1.6 if case.units_system == UnitSystem.SI else 1.6 / 25.4)
    nominal_strength = 2.4 * db_plus_1p6mm * tp.value * fup.value
    design_strength = phi * nominal_strength
    if case.units_system == UnitSystem.SI:
        nominal_strength /= 1000.0
        design_strength /= 1000.0
    phi_vn2p = Quantity(value=design_strength, unit=vu2p.unit)

    return _build_result(
        rule_binding=rule_binding,
        demand=vu2p,
        capacity=phi_vn2p,
        equation="Vu2p = Vhmax/nb; phiVn2p = phi * 2.4 * (db + 1.6 mm) * tp * Fup (AISC 360-22 J3.11a)",
        inputs={
            "vhmax": vh.model_dump(),
            "vhmax_source": vh_source,
            "vhmax_computed": vh_computed.model_dump(),
            "nb": nb,
            "lc": lc.model_dump(),
            "tp": tp.model_dump(),
            "fup": fup.model_dump(),
            "db": db.model_dump(),
            "db_plus_1p6mm": {"value": db_plus_1p6mm, "unit": db.unit},
            "dh": Quantity(value=lc_inter["dh"], unit=lc.unit).model_dump(),
        },
        intermediates={
            **lc_inter,
            "vu2p": vu2p.value,
            "nominal_strength": nominal_strength,
            "design_strength": design_strength,
            "db_plus_1p6mm": db_plus_1p6mm,
        },
        design_factors={"phi": phi},
        units_trace={"vu2p": vu2p.unit, "phi_vn2p": phi_vn2p.unit},
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
    stiffener_height = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo)
    weld_fexx = _require(case, "materials.weld_fexx", rule_binding)
    clip_st = _stiffener_clip_distance(case.units_system)

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

    lst = Quantity(
        value=stiffener_height.value - clip_st.value - (2.0 * wst.value),
        unit=stiffener_height.unit,
    )
    lst_source = "derived_hst_minus_clip_st_minus_2w_st"
    if lst.value <= 0.0:
        raise ValueError("Derived weld_1 length (l_st = hst - clip_st - 2*w_st) must be positive.")

    nl = case.geometry.end_plate_stiffener_weld_lines_nl if case.geometry.end_plate_stiffener_weld_lines_nl is not None else 2
    if nl <= 0:
        raise ValueError("geometry.end_plate_stiffener_weld_lines_nl must be >= 1 for Step 8.1.1.")

    demand_result = compute_plate_tension_demand_from_yielding(
        fy=stiffener_fy,
        thickness=stiffener_thickness,
        effective_length=stiffener_height,
        unit_system=case.units_system,
    )
    pust = demand_result["pu"]
    phi = 0.9
    weld_strength = WeldFillet(
        fexx=weld_fexx,
        weld_size=wst,
        weld_length=lst,
        weld_lines=nl,
        unit_system=case.units_system,
        phi=phi,
    ).design_strength()
    phi_rnst = weld_strength["phi_rn"]

    return _build_result(
        rule_binding=rule_binding,
        demand=pust,
        capacity=phi_rnst,
        equation=(
            "Fillet: Pust = Fys * ts * hst; "
            "l_st = hst - clip_st - 2*w_st; "
            "phiRnst = phi * nl * 0.6 * FEXX * 0.707 * l_st * w_st (AISC 360-22 J2.4)"
        ),
        inputs={
            "end_plate_stiffener_weld_type": weld_type_raw,
            "weld_type_normalized": weld_type,
            "fys": stiffener_fy.model_dump(),
            "ts": stiffener_thickness.model_dump(),
            "hst": stiffener_height.model_dump(),
            "clip_st": clip_st.model_dump(),
            "fexx": weld_fexx.model_dump(),
            "lst": lst.model_dump(),
            "lst_source": lst_source,
            "wst": wst.model_dump(),
            "wst_source": wst_source,
            "nl": nl,
        },
        intermediates={
            "pust_nominal": demand_result["pu_base_force"],
            "rnst_nominal": weld_strength["rn_base_force"],
            "phi_rnst_nominal": weld_strength["phi_rn_base_force"],
            "pust": pust.value,
            "phi_rnst": phi_rnst.value,
        },
        design_factors={"phi": phi},
        units_trace={"pust": pust.unit, "phi_rnst": phi_rnst.unit},
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
    hst = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo)
    lst = _derive_stiffener_length_from_hst(stiffener_height=hst, unit_system=case.units_system)
    clip_st = _stiffener_clip_distance(case.units_system)

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

    lst_w2 = Quantity(
        value=lst.value - clip_st.value - (2.0 * wst2.value),
        unit=lst.unit,
    )
    lst_w2_source = "derived_lst_minus_clip_st_minus_2w_st"
    if lst_w2.value <= 0.0:
        raise ValueError("Derived weld_2 length (l_st,w2 = Lst - clip_st - 2*w_st) must be positive.")

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

    demand_result = compute_plate_shear_demand_from_yielding(
        fy=stiffener_fy,
        thickness=stiffener_thickness,
        effective_length=lst_w2,
        unit_system=case.units_system,
    )
    vust = demand_result["vu"]
    phi = 0.9
    weld_strength = WeldFillet(
        fexx=weld_fexx,
        weld_size=wst2,
        weld_length=lst_w2,
        weld_lines=nl_w2,
        unit_system=case.units_system,
        phi=phi,
    ).design_strength()
    phi_vnst = weld_strength["phi_rn"]

    return _build_result(
        rule_binding=rule_binding,
        demand=vust,
        capacity=phi_vnst,
        equation=(
            "Fillet: Vust,w2 = Fys * 0.6 * ts * l_st,w2; "
            "l_st,w2 = Lst - clip_st - 2*w_st; "
            "phiVnst,w2 = phi * nl * 0.6 * FEXX * 0.707 * l_st,w2 * w_st "
            "(AISC 360-22W J2b(g))"
        ),
        inputs={
            "beam_stiffener_weld_type": weld_type_raw,
            "weld_type_source": weld_type_source,
            "weld_type_normalized": weld_type,
            "fys": stiffener_fy.model_dump(),
            "ts": stiffener_thickness.model_dump(),
            "fexx": weld_fexx.model_dump(),
            "hst": hst.model_dump(),
            "lst": lst.model_dump(),
            "clip_st": clip_st.model_dump(),
            "lst_w2": lst_w2.model_dump(),
            "lst_w2_source": lst_w2_source,
            "wst2": wst2.model_dump(),
            "wst2_source": wst2_source,
            "nl_w2": nl_w2,
            "nl_w2_source": nl_w2_source,
        },
        intermediates={
            "vust_nominal": demand_result["vu_base_force"],
            "vnst_nominal": weld_strength["rn_base_force"],
            "phi_vnst_nominal": weld_strength["phi_rn_base_force"],
            "vust": vust.value,
            "phi_vnst": phi_vnst.value,
        },
        design_factors={"phi": phi},
        units_trace={"vust": vust.unit, "phi_vnst": phi_vnst.unit},
    )


def run_step10_1_1_beam_shear_yielding(case: AISC358MomentCase, rule_binding: object) -> CheckResult:
    beam_profile = _beam_profile(case)
    d = beam_profile["d"]
    tw = beam_profile["tw"]
    kdes = _profile_kdes(beam_profile, role="beam", rule_binding=rule_binding)
    fybm = _require(case, "materials.beam_fy", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    vh_data = _compute_vh_by_side(case, rule_binding)
    vh_computed = vh_data["governing_vhmax"]
    vubm, vh_source = _select_stated_vhmax_for_design(case, vh_data)

    phi = 1.0
    shear_result = compute_beam_web_shear_yielding_strength(
        fy=fybm,
        tw=tw,
        d=d,
        kdes=kdes,
        elastic_modulus=elastic_modulus,
        unit_system=case.units_system,
        phi=phi,
    )
    phi_vnbm = shear_result["phi_vn"]
    nominal_shear = shear_result["vn"].value
    design_shear = phi_vnbm.value

    return _build_result(
        rule_binding=rule_binding,
        demand=vubm,
        capacity=phi_vnbm,
        equation=(
            "Vubm = Vhmax; phiVnbm = phi * 0.6 * Fybm * tw,bm * d * Cv1 "
            "(AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)"
        ),
        inputs={
            "vhmax": vubm.model_dump(),
            "vhmax_source": vh_source,
            "vhmax_computed": vh_computed.model_dump(),
            "fybm": fybm.model_dump(),
            "tw_bm": tw.model_dump(),
            "d": d.model_dump(),
            "kdes": kdes.model_dump(),
            "elastic_modulus": elastic_modulus.model_dump(),
            "cv1": shear_result["cv1"],
        },
        intermediates={
            "h_clear": shear_result["h_clear"].value,
            "h_over_tw": shear_result["h_over_tw"],
            "kv": shear_result["kv"],
            "lambda_r": shear_result["lambda_r"],
            "cv1": shear_result["cv1"],
            "nominal_shear": nominal_shear,
            "design_shear": design_shear,
        },
        design_factors={"phi": phi},
        units_trace={"vubm": vubm.unit, "phi_vnbm": phi_vnbm.unit},
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
    bolt_tightening_type = case.geometry.bolt_tightening_type
    bolt_fabrication_standard = case.materials.bolt_fabrication_standard
    bp = _require(case, "geometry.end_plate_width", rule_binding)
    pb = _require(case, "geometry.pb", rule_binding)
    de = _require(case, "geometry.de", rule_binding)
    pfo = _require(case, "geometry.pfo", rule_binding)
    pfi = _require(case, "geometry.pfi", rule_binding)
    tp = _require(case, "geometry.end_plate_thickness", rule_binding)
    tcp = _require(case, "geometry.continuity_plate_thickness", rule_binding)
    continuity_plate_weld_type_raw = case.geometry.continuity_plate_weld_type
    end_plate_beam_web_weld_type_raw = case.geometry.end_plate_beam_web_weld_type
    weld_fexx = _require(case, "materials.weld_fexx", rule_binding)
    beam_clear_span_length = _require(case, "geometry.beam_clear_span_length", rule_binding)
    shear_connector_free_length = _require(
        case,
        "geometry.beam_shear_connector_free_length_from_column_face",
        rule_binding,
    )
    beam_connection_sides = _require(case, "design_factors.beam_connection_sides", rule_binding)
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
    column_profile = _column_profile(case)
    bf = beam_profile["bf"]
    bcf = column_profile["bf"]
    beam_depth = beam_profile["d"]
    beam_ductility = _require(case, "design_factors.member_ductility_demand_beam", rule_binding)
    column_ductility = _require(case, "design_factors.member_ductility_demand_column", rule_binding)
    ry = _require(case, "design_factors.ry", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    beam_fy = _require(case, "materials.beam_fy", rule_binding)
    column_fy = _require(case, "materials.column_fy", rule_binding)
    pu_beam = _require(case, "loads.pu_viga", rule_binding)
    pu_column = _require(case, "loads.pu_columna", rule_binding)
    beam_ag = _profile_ag(beam_profile, role="beam", rule_binding=rule_binding)
    column_ag = _profile_ag(column_profile, role="column", rule_binding=rule_binding)
    stiffener_height = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo)
    end_plate_height = _derive_end_plate_height(beam_depth=beam_depth, de=de, pfo=pfo)
    stiffener_length_derived = _derive_stiffener_length_from_hst(
        stiffener_height=stiffener_height,
        unit_system=case.units_system,
    )
    pso = pfo
    psi = Quantity(value=pfi.value + beam_profile["tf"].value - tcp.value, unit=pfi.unit)
    h1 = Quantity(
        value=beam_depth.value - 0.5 * beam_profile["tf"].value + pso.value + pb.value,
        unit=beam_depth.unit,
    )
    h2 = Quantity(
        value=beam_depth.value - 0.5 * beam_profile["tf"].value + pso.value,
        unit=beam_depth.unit,
    )
    h3 = Quantity(
        value=beam_depth.value - 1.5 * beam_profile["tf"].value - psi.value,
        unit=beam_depth.unit,
    )
    h4 = Quantity(
        value=beam_depth.value - 1.5 * beam_profile["tf"].value - psi.value - pb.value,
        unit=beam_depth.unit,
    )
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
    standard_hole_diameter, standard_hole_intermediate = _compute_standard_hole_diameter(
        bolt_diameter=db,
        unit_system=case.units_system,
    )

    def _table61_length(*, us_in: float, si_mm: float) -> Quantity:
        if case.units_system.value == "US":
            return Quantity(value=us_in, unit="in")
        # Use exact in->mm conversion to avoid rounding mismatches between paired unit columns.
        return Quantity(value=us_in * 25.4, unit="mm")

    table_61_limits: dict[str, dict[str, tuple[Quantity, Quantity] | None]] = {
        "bueep_4e": {
            "tbf": (_table61_length(us_in=3.0 / 8.0, si_mm=10.0), _table61_length(us_in=3.0 / 4.0, si_mm=19.0)),
            "bbf": (_table61_length(us_in=6.0, si_mm=150.0), _table61_length(us_in=9.25, si_mm=230.0)),
            "d": (_table61_length(us_in=13.75, si_mm=350.0), _table61_length(us_in=24.0, si_mm=600.0)),
            "tp": (_table61_length(us_in=0.5, si_mm=13.0), _table61_length(us_in=2.25, si_mm=57.0)),
            "bp": (_table61_length(us_in=7.0, si_mm=180.0), _table61_length(us_in=10.75, si_mm=270.0)),
            "g": (_table61_length(us_in=4.0, si_mm=100.0), _table61_length(us_in=6.0, si_mm=150.0)),
            "pfi": (_table61_length(us_in=1.5, si_mm=38.0), _table61_length(us_in=4.5, si_mm=110.0)),
            "pfo": (_table61_length(us_in=1.5, si_mm=38.0), _table61_length(us_in=4.5, si_mm=110.0)),
            "pb": None,
        },
        "bseep_4es": {
            "tbf": (_table61_length(us_in=3.0 / 8.0, si_mm=10.0), _table61_length(us_in=3.0 / 4.0, si_mm=19.0)),
            "bbf": (_table61_length(us_in=6.0, si_mm=150.0), _table61_length(us_in=9.0, si_mm=230.0)),
            "d": (_table61_length(us_in=13.75, si_mm=350.0), _table61_length(us_in=24.0, si_mm=600.0)),
            "tp": (_table61_length(us_in=0.5, si_mm=13.0), _table61_length(us_in=1.5, si_mm=38.0)),
            "bp": (_table61_length(us_in=7.0, si_mm=180.0), _table61_length(us_in=10.75, si_mm=270.0)),
            "g": (_table61_length(us_in=3.25, si_mm=83.0), _table61_length(us_in=6.0, si_mm=150.0)),
            "pfi": (_table61_length(us_in=1.75, si_mm=44.0), _table61_length(us_in=5.5, si_mm=140.0)),
            "pfo": (_table61_length(us_in=1.75, si_mm=44.0), _table61_length(us_in=5.5, si_mm=140.0)),
            "pb": None,
        },
        "bseep_8es": {
            "tbf": (_table61_length(us_in=9.0 / 16.0, si_mm=14.0), _table61_length(us_in=1.0, si_mm=25.0)),
            "bbf": (_table61_length(us_in=7.5, si_mm=190.0), _table61_length(us_in=12.25, si_mm=310.0)),
            "d": (_table61_length(us_in=18.0, si_mm=460.0), _table61_length(us_in=36.0, si_mm=910.0)),
            "tp": (_table61_length(us_in=0.75, si_mm=19.0), _table61_length(us_in=2.5, si_mm=64.0)),
            "bp": (_table61_length(us_in=9.0, si_mm=230.0), _table61_length(us_in=15.0, si_mm=380.0)),
            "g": (_table61_length(us_in=5.0, si_mm=130.0), _table61_length(us_in=6.0, si_mm=150.0)),
            "pfi": (_table61_length(us_in=1.625, si_mm=41.0), _table61_length(us_in=2.0, si_mm=51.0)),
            "pfo": (_table61_length(us_in=1.625, si_mm=41.0), _table61_length(us_in=2.0, si_mm=51.0)),
            "pb": None,
        },
    }

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
        thickness_limit: Quantity,
        weld_type_raw: str | None,
    ) -> dict[str, Any]:
        weld_type = _normalize_continuity_plate_weld_type(weld_type_raw)
        allowed_values = ["double_sided_fillet", "cjp", "pjp"]
        condition_applies = continuity_plate_thickness.value <= (thickness_limit.value + 1e-9)
        if weld_type in {"cjp", "pjp"}:
            passes = True
            governing_condition = "cjp_or_pjp_always_permitted"
        elif weld_type == "double_sided_fillet":
            passes = condition_applies
            governing_condition = "double_sided_fillet_requires_tcp_le_limit"
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
            "calculated_symbol": "weld_cp",
            "limit_symbol": "{double_sided_fillet, cjp, pjp} if tcp<=tcp_limit",
            "comparison": "conditional_allowed_set",
            "comparison_text": "in_if",
            "thickness": continuity_plate_thickness.model_dump(),
            "thickness_limit": thickness_limit.model_dump(),
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
    step_1_notes = [
        {
            "step": "1",
            "id": "section_2_3_4.protected_zone_length",
            "scope": "beam",
            "clause": "Section 2.3.4 (8)",
            "description": "Protected zone length measured from column face",
            "beam_connection_sides": case.design_factors.beam_connection_sides,
            "formula": str(pz_der["formula"]),
            "candidate_a_label": str(pz_der["candidate_a_label"]),
            "candidate_a": pz_der["candidate_a"].model_dump(),
            "candidate_b_label": str(pz_der["candidate_b_label"]),
            "candidate_b": pz_der["candidate_b"].model_dump(),
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
            "requirement": "The end plate shall be connected to the flange of the column.",
        },
        {
            "step": "1",
            "id": "section_6_3.end_plate_height_derived",
            "scope": "end_plate",
            "clause": "Section 6.3",
            "description": "Derived end-plate height reference",
            "requirement": "hp = d + 2*pfo + 2*de",
            "formula": "hp = d + 2*pfo + 2*de",
            "candidate_a_label": "d",
            "candidate_a": beam_depth.model_dump(),
            "candidate_b_label": "2*pfo + 2*de",
            "candidate_b": Quantity(value=2.0 * pfo.value + 2.0 * de.value, unit=pfo.unit).model_dump(),
            "derived_value": end_plate_height.model_dump(),
        },
        {
            "step": "1",
            "id": "section_6_3.end_plate_geometry_vgder_note",
            "scope": "end_plate",
            "clause": "Section 6.3 + AISC 360-22 Table J3.3",
            "description": "Geometria end-plate de viga a derecha",
            "requirement": "h1_vgder, h2_vgder, h3_vgder, h4_vgder y dh_vgder para trazabilidad geometrica",
            "formula": (
                "h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb; "
                "dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in"
            ),
            "h1_vgder": h1.model_dump(),
            "h2_vgder": h2.model_dump(),
            "h3_vgder": h3.model_dump(),
            "h4_vgder": h4.model_dump(),
            "dh_vgder": standard_hole_diameter.model_dump(),
        },
        {
            "step": "1",
            "id": "section_6_3.end_plate_stiffener_geometry_note",
            "scope": "end_plate_stiffener",
            "clause": "Section 6.3",
            "description": "Derived end-plate stiffener geometry and detailing edge requirement",
            "requirement": "hst = pfo + de; Lst = hst/tan(30 deg); clip_st (Cst) = 25 mm; edge detailing >= 25 mm",
            "formula": "hst = pfo + de; Lst = hst / tan(30 deg)",
            "candidate_a_label": "hst",
            "candidate_a": stiffener_height.model_dump(),
            "candidate_b_label": "Lst",
            "candidate_b": stiffener_length_derived.model_dump(),
            "clip_st": _stiffener_clip_distance(case.units_system).model_dump(),
            "derived_value": Quantity(
                value=25.0 if case.units_system == UnitSystem.SI else (25.0 / 25.4),
                unit="mm" if case.units_system == UnitSystem.SI else "in",
            ).model_dump(),
        },
        {
            "step": "1",
            "id": "section_6_7.beam_flange_to_end_plate_weld_note",
            "scope": "welds",
            "clause": "Section 6.7",
            "description": "Requisitos de soldadura entre ala de viga y placa de extremo",
            "requirement": (
                "La unión entre el ala de la viga y la placa de extremo debe ejecutarse con una soldadura "
                "de ranura CJP sin respaldo. La soldadura de ranura CJP debe realizarse de modo que la raíz "
                "de la soldadura quede del lado del alma de la viga respecto del ala. La cara interior del ala "
                "debe tener una soldadura de filete de c in. (8 mm). Estas soldaduras deben ser de demanda crítica."
            ),
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
        {
            "step": "1",
            "id": "section_4_2.installation_requirements",
            "scope": "bolts",
            "clause": "Section 4.2",
            "description": "Installation requirements for bolted assemblies",
            "requirement": (
                "Installation requirements shall be in accordance with the AISC Seismic Provisions and "
                "the RCSC Specification, except as otherwise specifically indicated in this standard."
            ),
        },
        {
            "step": "1",
            "id": "section_4_3.quality_control_assurance",
            "scope": "bolts",
            "clause": "Section 4.3",
            "description": "Quality control and quality assurance for bolted assemblies",
            "requirement": (
                "Quality control and quality assurance shall be in accordance with the AISC Seismic Provisions."
            ),
        },
    ]
    if case.design_factors.beam_connection_sides == "both_sides":
        step_1_notes.insert(
            4,
            {
                "step": "1",
                "id": "section_6_3.end_plate_geometry_vgizq_note",
                "scope": "end_plate",
                "clause": "Section 6.3 + AISC 360-22 Table J3.3",
                "description": "Geometria end-plate de viga a izquierda",
                "requirement": "h1_vgizq, h2_vgizq, h3_vgizq, h4_vgizq y dh_vgizq para trazabilidad geometrica",
                "formula": (
                    "h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb; "
                    "dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in"
                ),
                "h1_vgizq": h1.model_dump(),
                "h2_vgizq": h2.model_dump(),
                "h3_vgizq": h3.model_dump(),
                "h4_vgizq": h4.model_dump(),
                "dh_vgizq": standard_hole_diameter.model_dump(),
            },
        )

    span_to_depth_limit = 7.0 if beam_ductility == "high" else 5.0
    frame_system = "SMF" if beam_ductility == "high" else "IMF"
    clear_span_to_depth_ratio = Quantity(
        value=beam_clear_span_length.value / beam_depth.value,
        unit="ratio",
    )
    beam_flange_ratio = compute_flange_slenderness_ratio(
        flange_width=beam_profile["bf"],
        flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    beam_web_ratio, _ = compute_web_slenderness_ratio(
        section_depth=beam_profile["d"],
        k_design=_profile_kdes(beam_profile, role="beam", rule_binding=rule_binding),
        web_thickness=beam_profile["tw"],
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

    active_table_61 = table_61_limits[case.connection_type]
    stc_margin = Quantity(
        value=(12.5 / 25.4) if case.units_system == UnitSystem.US else 12.5,
        unit="in" if case.units_system == UnitSystem.US else "mm",
    )
    if case.connection_type == "bseep_8es":
        stc_min = Quantity(value=pfo.value + pb.value + de.value + stc_margin.value, unit=stc.unit)
        stc_formula = "Stc >= pfo + pb + de + 12.5 mm"
    else:
        stc_min = Quantity(value=pfo.value + de.value + stc_margin.value, unit=stc.unit)
        stc_formula = "Stc >= pfo + de + 12.5 mm"
    s_threshold = Quantity(value=0.5 * math.sqrt(bcf.value * g.value), unit=bcf.unit)
    if case.connection_type == "bseep_8es":
        sc = Quantity(value=stc.value - pfo.value - pb.value, unit=stc.unit)
        sc_formula = "Sc = Stc - pfo - pb"
    else:
        sc = Quantity(value=stc.value - pfo.value, unit=stc.unit)
        sc_formula = "Sc = Stc - pfo"
    sc_pass = sc.value > s_threshold.value

    beam_limits = [
        _step1_shape_family_limit(
            check_id="beam.shape_family",
            scope="beam",
            clause="Section 2.3.4",
            description="Beam profile family allowed for prequalification",
            calculated_symbol="shape_beam",
            limit_symbol="{W, HEA, HEB, IPE}",
            shape_text=case.sections.beam_shape,
            allowed_families=allowed_shape_families,
        ),
        _step1_limit(
            check_id="beam.bp_ge_bf_plus_margin",
            scope="beam",
            clause="Section 6.3 / Table 6.1",
            description="End-plate width vs beam flange width",
            calculated_symbol="bp",
            limit_symbol="bf + margin",
            calculated=bp,
            limit=min_bp,
            comparison="ge",
        ),
        _step1_limit(
            check_id="beam.bolt_gage_g_ge_3db",
            scope="beam",
            clause="Section 6.3 / Table 6.1",
            description="Bolt gage minimum spacing",
            calculated_symbol="g",
            limit_symbol="3db",
            calculated=g,
            limit=min_spacing,
            comparison="ge",
        ),
        _step1_limit(
            check_id="section_2_3_4.no_shear_connectors_zone",
            scope="beam",
            clause="Section 2.3.4 (2)",
            description="Length without shear connectors from column face",
            calculated_symbol="Lsc",
            limit_symbol="1.5d",
            calculated=shear_connector_free_length,
            limit=Quantity(value=1.5 * beam_depth.value, unit=beam_depth.unit),
            comparison="ge",
        ),
        _step1_compound_limit(
            check_id="section_6_3_1.beam_sc_greater_than_s_threshold",
            scope="beam",
            clause="Section 6.3.1 (beam clearance criterion)",
            description="Beam clearance criterion using Sc and S threshold",
            calculated_symbol="Sc",
            verification_text=(
                f"{sc_formula}; S = 0.5*sqrt(bcf*g); "
                f"Sc > S => {sc.value:.3f} {sc.unit} > {s_threshold.value:.3f} {s_threshold.unit}"
            ),
            passes=sc_pass,
            calculated=sc,
        ),
        _step1_limit(
            check_id="section_2_3_4.clear_span_to_depth_ratio",
            scope="beam",
            clause="Section 2.3.4 (5)",
            description="Clear span-to-depth ratio by frame system",
            calculated_symbol="Lclear/d",
            limit_symbol=f"{span_to_depth_limit:.0f} ({frame_system})",
            calculated=clear_span_to_depth_ratio,
            limit=Quantity(value=span_to_depth_limit, unit="ratio"),
            comparison="ge",
        ),
        _step1_limit(
            check_id="section_2_3_4.beam_flange_width_to_thickness",
            scope="beam",
            clause="Section 2.3.4 (6) + AISC Seismic Provisions",
            description="Beam flange width-to-thickness compactness",
            calculated_symbol="lambda_f_beam",
            limit_symbol="lambda_f_limit",
            calculated=Quantity(value=beam_flange_ratio, unit="ratio"),
            limit=Quantity(value=beam_flange_limit, unit="ratio"),
            comparison="le",
        ),
        _step1_limit(
            check_id="section_2_3_4.beam_web_width_to_thickness",
            scope="beam",
            clause="Section 2.3.4 (6) + AISC Seismic Provisions",
            description="Beam web width-to-thickness compactness",
            calculated_symbol="lambda_w_beam",
            limit_symbol="lambda_w_limit",
            calculated=Quantity(value=beam_web_ratio, unit="ratio"),
            limit=Quantity(value=beam_web_limit, unit="ratio"),
            comparison="le",
        ),
    ]

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
        _step1_limit(
            check_id="section_6_3_1.column_stc_minimum_requirement",
            scope="column",
            clause="Section 6.3.1 (column top clearance criterion)",
            description=stc_formula,
            calculated_symbol="Stc",
            limit_symbol="Stc_min",
            calculated=stc,
            limit=stc_min,
            comparison="ge",
        ),
        _step1_limit(
            check_id="section_2_3_4.column_flange_width_to_thickness",
            scope="column",
            clause="Section 2.3.4 (6) + AISC Seismic Provisions",
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
            clause="Section 2.3.4 (6) + AISC Seismic Provisions",
            description="Column web width-to-thickness compactness",
            calculated_symbol="lambda_w_col",
            limit_symbol="lambda_w_limit",
            calculated=Quantity(value=column_web_ratio, unit="ratio"),
            limit=Quantity(value=column_web_limit, unit="ratio"),
            comparison="le",
        ),
    ]

    bp_bounds = active_table_61.get("bp")
    end_plate_limits: list[dict[str, Any]] = []
    if bp_bounds is not None:
        bp_min, bp_max = bp_bounds
        bp_plus_beam_margin = Quantity(value=bf.value + bp_margin, unit=bf.unit)
        bp_governing_max = Quantity(
            value=min(bp_max.value, bp_plus_beam_margin.value, bcf.value),
            unit=bp.unit,
        )
        bp_pass = (bp.value <= bp_plus_beam_margin.value) and (bp.value <= bcf.value) and (bp.value >= bp_min.value)
        beam_margin_label = (
            f"{bp_margin:.0f} mm" if case.units_system == UnitSystem.SI else f"{bp_margin:.3f} in"
        )
        end_plate_limits.append(
            _step1_compound_limit(
                check_id="section_6_3.end_plate_width_dual_limit",
                scope="end_plate",
                clause="Section 6.3 / Table 6.1",
                description="End-plate width explicit dual inequalities",
                calculated_symbol="bp",
                verification_text=(
                    f"bp <= bbf + {beam_margin_label}; "
                    "bp <= bcf"
                ),
                passes=bp_pass,
                calculated=bp,
                minimum=bp_min,
                maximum=bp_governing_max,
            )
        )

    end_plate_stiffener_limits = [
        _step1_compound_limit(
            check_id="section_6_3.end_plate_stiffener_height_derived",
            scope="end_plate_stiffener",
            clause="Section 6.3",
                description="End-plate stiffener height derived from end-plate geometry",
                calculated_symbol="hst",
                verification_text=(
                    f"hst = pfo + de; {stiffener_height.value:.3f} {stiffener_height.unit} = "
                    f"{pfo.value:.3f} {pfo.unit} + {de.value:.3f} {de.unit}"
                ),
                passes=stiffener_height.value > 0.0,
                calculated=stiffener_height,
            )
        ]
    if case.connection_type in {"bseep_4es", "bseep_8es"}:
        ts = _require(case, "geometry.stiffener_thickness", rule_binding)
        stiffener_fy = _require(case, "materials.stiffener_fy", rule_binding)
        tbw = beam_profile["tw"]
        g_min_stiffener = Quantity(value=(2.0 * min_edge.value) + ts.value, unit=g.unit)
        ts_required = compute_required_stiffener_thickness(
            beam_web_thickness=tbw,
            beam_fy=beam_fy,
            stiffener_fy=stiffener_fy,
            unit_system=case.units_system,
        )
        slenderness_ratio = stiffener_height.value / ts.value
        slenderness_limit = compute_stiffener_slenderness_ratio_limit(
            elastic_modulus=elastic_modulus,
            stiffener_fy=stiffener_fy,
            unit_system=case.units_system,
        )
        end_plate_stiffener_limits.extend(
            [
                _step1_limit(
                    check_id="section_6_7_1.stiffener_thickness_minimum",
                    scope="end_plate_stiffener",
                    clause="Section 6.7.1 Eq. (6.7-9)",
                    description="Stiffener thickness minimum requirement",
                    calculated_symbol="ts",
                    limit_symbol="tbw*(Fyb/Fys)",
                    calculated=ts,
                    limit=ts_required,
                    comparison="ge",
                ),
                _step1_limit(
                    check_id="section_6_7_1.stiffener_local_buckling_limit",
                    scope="end_plate_stiffener",
                    clause="Section 6.7.1 Eq. (6.7-10)",
                    description="Stiffener local buckling width-thickness limit",
                    calculated_symbol="hst/ts",
                    limit_symbol="0.56*sqrt(E/Fys)",
                    calculated=Quantity(value=slenderness_ratio, unit="ratio"),
                    limit=Quantity(value=slenderness_limit, unit="ratio"),
                    comparison="le",
                ),
                _step1_limit(
                    check_id="section_6_3_1.stiffener_bolt_gage_clearance",
                    scope="end_plate_stiffener",
                    clause="Section 6.3 (stiffened) + AISC 360 Table J3.4",
                    description="Bolt gage clearance with stiffener thickness",
                    calculated_symbol="g",
                    limit_symbol="2emin + ts",
                    calculated=g,
                    limit=g_min_stiffener,
                    comparison="ge",
                ),
            ]
        )

    continuity_plate_limits: list[dict[str, object]] = []
    continuity_plate_weld_thickness_limit = Quantity(
        value=3.0 / 8.0 if case.units_system == UnitSystem.US else 10.0,
        unit="in" if case.units_system == UnitSystem.US else "mm",
    )
    if continuity_plate_weld_type_raw is not None and str(continuity_plate_weld_type_raw).strip():
        continuity_plate_weld_type_normalized = _normalize_continuity_plate_weld_type(continuity_plate_weld_type_raw)
        continuity_plate_limits = [
            _step1_text_in_set_limit(
                check_id="section_6_3.continuity_plate_weld_type_declared",
                scope="continuity_plate",
                clause="Section 6.3 (continuity plate weld detail)",
                description="Continuity-plate weld type shall be explicitly declared with an allowed weld category",
                calculated_symbol="weld_cp",
                limit_symbol="{double_sided_fillet, cjp, pjp}",
                calculated_text=continuity_plate_weld_type_normalized,
                allowed_values=("double_sided_fillet", "cjp", "pjp"),
            ),
            _step1_continuity_plate_weld_limit(
                check_id="section_6_3.continuity_plate_weld_type_for_thin_plate",
                scope="continuity_plate",
                clause="Section 6.3 (continuity plate weld detail)",
                description=(
                    "Continuity-plate weld type when plate thickness is less than or equal to 3/8 in (10 mm)"
                ),
                continuity_plate_thickness=tcp,
                thickness_limit=continuity_plate_weld_thickness_limit,
                weld_type_raw=continuity_plate_weld_type_raw,
            ),
        ]

    end_plate_beam_web_weld_type_normalized = _normalize_end_plate_beam_web_weld_type(end_plate_beam_web_weld_type_raw)
    weld_limits = [
        _step1_text_in_set_limit(
            check_id="section_6_7.end_plate_beam_web_weld_type_allowed",
            scope="welds",
            clause="Section 6.7",
            description="End-plate to beam-web weld type shall be an allowed category",
            calculated_symbol="weld_ep_web",
            limit_symbol="{cjp, double_sided_fillet, single_sided_fillet}",
            calculated_text=end_plate_beam_web_weld_type_normalized,
            allowed_values=("cjp", "double_sided_fillet", "single_sided_fillet"),
        )
    ]

    tightening_type_normalized = _normalize_bolt_tightening(bolt_tightening_type)
    bolt_standard_text = str(bolt_fabrication_standard or "not_provided")
    required_bolt_standards = (
        "ASTM F3125/F3125M",
        "ASTM A325",
        "ASTM A325M",
        "ASTM A490",
        "ASTM A490M",
        "ASTM F1852",
        "ASTM F2280",
    )
    bolt_limits = [
        _step1_text_in_set_limit(
            check_id="section_4_1.bolt_tightening_type_valid",
            scope="bolts",
            clause="Section 4.1 FASTENER ASSEMBLIES",
            description="Bolt tightening type must be one recognized category",
            calculated_symbol="tight_bolt",
            limit_symbol="{pretensioned, snug_tight}",
            calculated_text=tightening_type_normalized,
            allowed_values=("pretensioned", "snug_tight"),
        ),
        _step1_text_limit(
            check_id="section_4_1.bolt_tightening_required_pretensioned",
            scope="bolts",
            clause="Section 4.1 FASTENER ASSEMBLIES",
            description="Bolts shall be pretensioned unless a specific connection permits otherwise",
            calculated_symbol="tight_bolt",
            limit_symbol="pretensioned",
            calculated_text=tightening_type_normalized,
            expected_text="pretensioned",
        ),
        _step1_text_in_set_limit(
            check_id="section_4_1.bolt_fabrication_standard_permitted",
            scope="bolts",
            clause="Section 4.1 FASTENER ASSEMBLIES",
            description="Bolt fabrication standard must be an allowed high-strength ASTM designation",
            calculated_symbol="std_bolt",
            limit_symbol="{ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}",
            calculated_text=bolt_standard_text,
            allowed_values=required_bolt_standards,
            normalizer=_normalize_bolt_standard,
        ),
    ]

    pfo_bounds = active_table_61.get("pfo")
    pfi_bounds = active_table_61.get("pfi")
    pso = pfo
    tfb = beam_profile["tf"]
    psi = Quantity(value=pfi.value + tfb.value - tcp.value, unit=pfi.unit)

    table_61_checks = [
        _step1_limit(
            check_id="table_6_1.edge_de_ge_emin",
            scope="table_6_1",
            clause="Table 6.1 + AISC 360 Table J3.4",
            description="Edge distance at de",
            calculated_symbol="de",
            limit_symbol="emin",
            calculated=de,
            limit=min_edge,
            comparison="ge",
        ),
    ]
    if pfo_bounds is not None:
        pfo_min, pfo_max = pfo_bounds
        pfo_min_label = f"{pfo_min.value:.0f} {pfo_min.unit}" if pfo_min.unit == "mm" else f"{pfo_min.value:.3f} {pfo_min.unit}"
        pfo_max_label = f"{pfo_max.value:.0f} {pfo_max.unit}" if pfo_max.unit == "mm" else f"{pfo_max.value:.3f} {pfo_max.unit}"
        pfo_pass = (
            (pfo.value >= min_edge.value)
            and (pfo.value >= pfo_min.value)
            and (pfo.value <= pfo_max.value)
        )
        table_61_checks.append(
            _step1_compound_limit(
                check_id="table_6_1.edge_pfo_ge_emin",
                scope="table_6_1",
                clause="Table 6.1 + AISC 360 Table J3.4",
                description="Outside bolt-row distance limits",
                calculated_symbol="pfo - pso",
                verification_text=(
                    f"pso (=pfo) >= emin; pfo <= {pfo_max_label}; pfo >= {pfo_min_label}"
                ),
                passes=pfo_pass,
                calculated=pfo,
                minimum=pfo_min,
                maximum=pfo_max,
            )
        )
    if pfi_bounds is not None:
        pfi_min, pfi_max = pfi_bounds
        pfi_min_label = f"{pfi_min.value:.0f} {pfi_min.unit}" if pfi_min.unit == "mm" else f"{pfi_min.value:.3f} {pfi_min.unit}"
        pfi_max_label = f"{pfi_max.value:.0f} {pfi_max.unit}" if pfi_max.unit == "mm" else f"{pfi_max.value:.3f} {pfi_max.unit}"
        psi_pass = psi.value > 0.0
        pfi_pass = (
            (pfi.value >= min_edge.value)
            and (pfi.value >= pfi_min.value)
            and (pfi.value <= pfi_max.value)
            and psi_pass
        )
        table_61_checks.append(
            _step1_compound_limit(
                check_id="table_6_1.edge_pfi_ge_emin",
                scope="table_6_1",
                clause="Table 6.1 + AISC 360 Table J3.4",
                description="Inside bolt-row distance limits",
                calculated_symbol="pfi - psi",
                verification_text=(
                    f"pfi >= emin; pfi <= {pfi_max_label}; pfi >= {pfi_min_label}; "
                    "psi = pfi + tfb - tcp; psi > 0"
                ),
                passes=pfi_pass,
                calculated=pfi,
                minimum=pfi_min,
                maximum=pfi_max,
            )
        )
    if case.connection_type == "bseep_4es":
        table_61_checks.insert(
            0,
            _step1_limit(
                check_id="table_6_1.pitch_pb_ge_3db",
                scope="table_6_1",
                clause="Table 6.1",
                description="Vertical pitch minimum spacing",
                calculated_symbol="pb",
                limit_symbol="3db",
                calculated=pb,
                limit=min_spacing,
                comparison="ge",
            ),
        )
    if case.connection_type == "bseep_8es":
        pb_8es_min = _table61_length(us_in=89.0 / 25.4, si_mm=89.0)
        pb_8es_max = _table61_length(us_in=95.0 / 25.4, si_mm=95.0)
        pb_tol = 1e-3
        pb_passes = (
            (pb.value >= (min_spacing.value - pb_tol))
            and (pb.value <= (pb_8es_max.value + pb_tol))
            and (pb.value >= (pb_8es_min.value - pb_tol))
        )
        table_61_checks.insert(
            0,
            _step1_compound_limit(
                check_id="table_6_1.pitch_pb_ge_3db",
                scope="table_6_1",
                clause="Table 6.1 (BSEEP-8ES)",
                description="Vertical pitch minimum spacing",
                calculated_symbol="pb",
                verification_text=(
                    f"pb >= 3db; pb <= {pb_8es_max.value:.3f} {pb_8es_max.unit}; "
                    f"pb >= "
                    f"{pb_8es_min.value:.0f} {pb_8es_min.unit}"
                    if pb_8es_min.unit == "mm"
                    else f"pb >= 3db; pb <= {pb_8es_max.value:.3f} {pb_8es_max.unit}; pb >= {pb_8es_min.value:.3f} {pb_8es_min.unit}"
                ),
                passes=pb_passes,
                calculated=pb,
                limit_3db=min_spacing,
                minimum=pb_8es_min,
                maximum=pb_8es_max,
            ),
        )

    table_61_values: list[tuple[str, str, Quantity]] = [
        ("tbf", "Beam flange thickness", beam_profile["tf"]),
        ("bbf", "Beam flange width", beam_profile["bf"]),
        ("d", "Connecting beam depth", beam_profile["d"]),
        ("tp", "End-plate thickness", tp),
        ("bp", "End-plate width", bp),
        ("g", "Horizontal bolt spacing", g),
        ("pb", "Vertical bolt-row spacing", pb),
    ]

    for symbol, description, value in table_61_values:
        bounds = active_table_61.get(symbol)
        if bounds is None:
            continue
        minimum, maximum = bounds
        if symbol == "bp":
            continue
        table_61_checks.append(
            _step1_range_limit(
                check_id=f"table_6_1.{symbol}.range",
                scope="table_6_1",
                clause="Table 6.1",
                description=f"{description} limits",
                symbol=symbol,
                calculated=value,
                minimum=minimum,
                maximum=maximum,
            )
        )

    step_1_limits = (
        beam_limits
        + column_limits
        + end_plate_limits
        + end_plate_stiffener_limits
        + weld_limits
        + continuity_plate_limits
        + bolt_limits
        + table_61_checks
    )

    overall_status = CheckStatus.PASS if all(item["status"] == CheckStatus.PASS.value for item in step_1_limits) else CheckStatus.FAIL

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
                "continuity_plate_thickness_tcp": tcp.model_dump(),
                "continuity_plate_enabled": case.geometry.continuity_plate_enabled,
                "continuity_plate_weld_type": continuity_plate_weld_type_raw,
                "end_plate_beam_web_weld_type": end_plate_beam_web_weld_type_raw,
                "weld_fexx": weld_fexx.model_dump(),
                "end_plate_beam_web_weld_thickness_twe": (
                    case.geometry.end_plate_beam_web_weld_thickness_twe.model_dump()
                    if case.geometry.end_plate_beam_web_weld_thickness_twe is not None
                    else None
                ),
                "end_plate_beam_web_weld_lines_nl": case.geometry.end_plate_beam_web_weld_lines_nl,
                "bolt_tightening_type": bolt_tightening_type,
                "bolt_fabrication_standard": bolt_fabrication_standard,
                "end_plate_width_bp": bp.model_dump(),
                "bolt_gage_g": g.model_dump(),
                "pitch_pb": pb.model_dump(),
                "edge_de": de.model_dump(),
                "edge_pfo": pfo.model_dump(),
                "edge_pfi": pfi.model_dump(),
                "end_plate_height": end_plate_height.model_dump(),
                "stiffener_height": stiffener_height.model_dump(),
                "stiffener_length": stiffener_length_derived.model_dump(),
                "beam_connection_sides": beam_connection_sides,
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
                "column_end_distance_to_beam_flange_stc": stc.model_dump(),
                "column_stc_min": stc_min.model_dump(),
                "beam_sc": sc.model_dump(),
                "beam_s_threshold": s_threshold.model_dump(),
                "beam_ductility_demand": beam_ductility,
                "column_ductility_demand": column_ductility,
                "pu_viga": pu_beam.model_dump(),
                "pu_columna": pu_column.model_dump(),
                "ag_viga": beam_ag.model_dump(),
                "ag_columna": column_ag.model_dump(),
                "compactness_ca_beam_calculated": ca_beam,
                "compactness_ca_column_calculated": ca_column,
            },
            intermediates={
                "minimum_spacing_3db": min_spacing.model_dump(),
                "minimum_bp_bf_plus_margin": min_bp.model_dump(),
                "bp_margin": bp_margin,
                "minimum_edge_distance_j34": min_edge.model_dump(),
                "clear_span_to_depth_ratio": clear_span_to_depth_ratio.model_dump(),
                "clear_span_to_depth_limit": {"value": span_to_depth_limit, "unit": "ratio"},
                "frame_system_for_span_ratio": frame_system,
                "beam_flange_compactness_ratio": beam_flange_ratio,
                "beam_flange_compactness_limit": beam_flange_limit,
                "beam_web_compactness_ratio": beam_web_ratio,
                "beam_web_compactness_limit": beam_web_limit,
                "column_flange_compactness_ratio": column_flange_ratio,
                "column_flange_compactness_limit": column_flange_limit,
                "column_web_compactness_ratio": column_web_ratio,
                "column_web_compactness_limit": column_web_limit,
                "ca_beam_trace": ca_beam_trace,
                "ca_column_trace": ca_column_trace,
                "continuity_plate_weld_thickness_limit": continuity_plate_weld_thickness_limit.model_dump(),
                "j34_lookup": edge_intermediate,
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
                "pb": pb.unit,
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
    hst = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo)
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
    hst = _derive_stiffener_height_from_de_pfo(de=de, pfo=pfo)
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
    mf, _, _ = _select_mf_for_design(case, rule_binding)
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
    phi_d = _require(case, "design_factors.phi_d", rule_binding)
    column_top_distance = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)
    w = case.geometry.end_plate_stiffener_weld_size_wst
    weld_size_source = "geometry.end_plate_stiffener_weld_size_wst"
    if w is None:
        w = case.geometry.beam_stiffener_weld_size_wst2
        weld_size_source = "geometry.beam_stiffener_weld_size_wst2"
    if w is None:
        w = case.geometry.end_plate_beam_web_weld_thickness_twe
        weld_size_source = "geometry.end_plate_beam_web_weld_thickness_twe"
    if w is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[
                "geometry.end_plate_stiffener_weld_size_wst",
                "geometry.beam_stiffener_weld_size_wst2",
                "geometry.end_plate_beam_web_weld_thickness_twe",
            ],
            message=(
                "Required weld size for lb calculation is missing. "
                "No assumed zero value is allowed under zero-guess policy."
            ),
        )

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
        mf=_select_mf_for_design(case, rule_binding)[0],
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
            "weld_size_for_lb": w.model_dump(),
            "weld_size_for_lb_source": weld_size_source,
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
    column_fy = _require(case, "materials.column_fy", rule_binding)
    elastic_modulus = _require(case, "materials.elastic_modulus", rule_binding)
    distance_to_end = _require(case, "geometry.column_end_distance_to_beam_flange", rule_binding)
    w = case.geometry.end_plate_stiffener_weld_size_wst
    weld_size_source = "geometry.end_plate_stiffener_weld_size_wst"
    if w is None:
        w = case.geometry.beam_stiffener_weld_size_wst2
        weld_size_source = "geometry.beam_stiffener_weld_size_wst2"
    if w is None:
        w = case.geometry.end_plate_beam_web_weld_thickness_twe
        weld_size_source = "geometry.end_plate_beam_web_weld_thickness_twe"
    if w is None:
        raise missing_required_input_error(
            rule_id=rule_binding.rule_id,
            source_document=rule_binding.source_document,
            missing_fields=[
                "geometry.end_plate_stiffener_weld_size_wst",
                "geometry.beam_stiffener_weld_size_wst2",
                "geometry.end_plate_beam_web_weld_thickness_twe",
            ],
            message=(
                "Required weld size for lb calculation is missing. "
                "No assumed zero value is allowed under zero-guess policy."
            ),
        )
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
        mf=_select_mf_for_design(case, rule_binding)[0],
        beam_depth=beam_profile["d"],
        beam_flange_thickness=beam_profile["tf"],
        unit_system=case.units_system,
    )
    return _build_result(
        rule_binding=rule_binding,
        demand=ffu,
        capacity=capacity,
        equation="Ffu <= phi*Rn (Eq. 6.7-18 to Eq. 6.7-21)",
        inputs={
            "lb": lb.model_dump(),
            "distance_to_column_end": distance_to_end.model_dump(),
            "weld_size_for_lb": w.model_dump(),
            "weld_size_for_lb_source": weld_size_source,
        },
        intermediates=intermediates,
        design_factors={},
        units_trace={"ffu": ffu.unit, "capacity": capacity.unit},
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
