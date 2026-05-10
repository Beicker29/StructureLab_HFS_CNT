from __future__ import annotations

import math

from steel_connections.codes.engineering.common import (
    compute_plate_compression_buckling_strength,
    compute_plate_combined_force_interaction,
    compute_member_combined_interaction_h11,
    compute_bolt_hole_bearing_strength_j36,
    compute_bolt_hole_tearout_strength_j36,
    compute_max_spacing_and_edge_distance_limits_j36,
    compute_maximum_bolt_spacing_j36,
    compute_minimum_bolt_spacing_j33,
    compute_minimum_edge_distance_standard_hole_j34,
    compute_bolt_shear_rupture_capacity_per_bolt,
    compute_element_shear_yielding_strength_j42a,
    compute_element_shear_rupture_strength_j43,
    compute_block_shear_strength_j45,
    compute_element_tension_rupture_strength_j41b,
    compute_element_tension_yielding_strength_j41a,
    compute_rectangular_bar_flexural_yielding_strength_f111,
    compute_member_flexural_rupture_with_tension_flange_holes_f131,
    compute_rectangular_bar_net_flexural_rupture_strength_j55,
    compute_rectangular_bar_ltb_strength_f112,
    compute_standard_hole_diameter_j33,
)
from steel_connections.data.materials_repository import (
    get_bolt_strength_properties,
    get_hrs_steel_properties,
    get_plate_steel_properties,
)
from steel_connections.data.sections_repository import (
    get_beam_profile_properties,
    get_bolt_section_properties,
    get_minimum_staggered_pitch_from_f,
)
from steel_connections.models.input import BeamBeamMomentBoltedCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import Quantity, UnitSystem


def _minimum_bolt_pretension_kN(*, diameter_in: float, fabrication_standard: str) -> float:
    standard = fabrication_standard.strip().upper()
    if "A490" in standard:
        table_kip = {
            0.5: 15.0,
            0.625: 24.0,
            0.75: 35.0,
            0.875: 49.0,
            1.0: 64.0,
            1.125: 80.0,
            1.25: 102.0,
            1.375: 121.0,
            1.5: 148.0,
        }
    else:
        table_kip = {
            0.5: 12.0,
            0.625: 19.0,
            0.75: 28.0,
            0.875: 39.0,
            1.0: 51.0,
            1.125: 56.0,
            1.25: 71.0,
            1.375: 85.0,
            1.5: 103.0,
        }
    tol = 1e-3
    for dia_in, value_kip in table_kip.items():
        if abs(diameter_in - dia_in) <= tol:
            return value_kip * 4.4482216152605
    raise ValueError(
        f"No J3.1 pretension value found for diameter {diameter_in:.4f} in and standard '{fabrication_standard}'."
    )


def _row(
    *,
    scope: str,
    description: str,
    calculated_symbol: str,
    limit_symbol: str,
    comparison_text: str,
    calculated: dict,
    limit: dict,
    clause: str,
    passed: bool,
    source_document: str | None = None,
) -> dict:
    row_data = {
        "scope": scope,
        "description": description,
        "calculated_symbol": calculated_symbol,
        "limit_symbol": limit_symbol,
        "comparison": "simple",
        "comparison_text": comparison_text,
        "calculated": calculated,
        "limit": limit,
        "clause": clause,
        "result": "PASS" if passed else "FAIL",
    }
    if source_document is not None:
        row_data["source_document"] = source_document
    return row_data


def run_step1_viga_detailing(case: BeamBeamMomentBoltedCase, rule_binding: object) -> CheckResult:
    bolt_web = get_bolt_section_properties(
        bolt_shape=case.materials.shape_blt_web,
        bolt_description=case.materials.desc_blt_web,
        bolt_fabrication_standard=case.materials.std_blt_web,
        unit_system=case.units_system,
    )
    bolt_flange = get_bolt_section_properties(
        bolt_shape=case.materials.shape_blt_flange,
        bolt_description=case.materials.desc_blt_flange,
        bolt_fabrication_standard=case.materials.std_blt_flange,
        unit_system=case.units_system,
    )
    db_web = bolt_web["diameter_nominal"]
    db_flange = bolt_flange["diameter_nominal"]
    if not isinstance(db_web, Quantity) or not isinstance(db_flange, Quantity):
        raise ValueError("Unable to resolve bolt diameters for bbmb_splice detailing.")

    db_web_in = db_web.value if case.units_system.value == "US" else db_web.value / 25.4
    db_flange_in = db_flange.value if case.units_system.value == "US" else db_flange.value / 25.4

    dh_web, dh_web_inter = compute_standard_hole_diameter_j33(
        bolt_diameter=db_web, unit_system=case.units_system
    )
    dh_flange, dh_flange_inter = compute_standard_hole_diameter_j33(
        bolt_diameter=db_flange, unit_system=case.units_system
    )

    s_min_web = compute_minimum_bolt_spacing_j33(bolt_diameter=db_web, unit_system=case.units_system)
    s_min_flange = compute_minimum_bolt_spacing_j33(bolt_diameter=db_flange, unit_system=case.units_system)
    le_min_web, le_meta_web = compute_minimum_edge_distance_standard_hole_j34(
        bolt_diameter=db_web,
        unit_system=case.units_system,
    )
    le_min_flange, le_meta_flange = compute_minimum_edge_distance_standard_hole_j34(
        bolt_diameter=db_flange,
        unit_system=case.units_system,
    )

    beam_props = get_beam_profile_properties(
        beam_shape=case.sections.shape_vg,
        unit_system=case.units_system,
    )
    t_catalog = beam_props.get("T")
    kdes_catalog = beam_props.get("kdes")
    tw_catalog = beam_props.get("tw")
    tf_catalog = beam_props.get("tf")
    bf_catalog = beam_props.get("bf")
    dvg_catalog = beam_props.get("d")
    ag_catalog = beam_props.get("ag")
    h_over_tw_catalog = beam_props.get("h_over_tw")
    if (
        not isinstance(t_catalog, Quantity)
        or not isinstance(kdes_catalog, Quantity)
        or not isinstance(tw_catalog, Quantity)
        or not isinstance(tf_catalog, Quantity)
        or not isinstance(bf_catalog, Quantity)
        or not isinstance(dvg_catalog, Quantity)
    ):
        raise ValueError(
            f"Sections catalog does not provide required properties for shape '{case.sections.shape_vg}'."
        )

    s1x = case.geometry.g_blt_web
    s1y = case.geometry.p_blt_web
    s2x = case.geometry.p_blt_flange
    s2z1 = case.geometry.g_blt_flange
    le1_x1 = case.geometry.Le_blt_web_x1
    le1_x2 = case.geometry.Le_blt_web_x2
    le1_y1 = case.geometry.Le_blt_web_y1
    le1_y2 = case.geometry.Le_blt_web_y2
    le1_y3 = Quantity(
        value=0.5 * (dvg_catalog.value - (case.geometry.n_blt_web_y - 1) * s1y.value),
        unit=dvg_catalog.unit,
    )
    le1_y3_1: Quantity | None = None
    if le1_y3.unit == kdes_catalog.unit:
        le1_y3_1 = Quantity(value=le1_y3.value - kdes_catalog.value, unit=le1_y3.unit)
    le2_x1 = case.geometry.Le_blt_flange_x1
    le2_x2 = case.geometry.Le_blt_flange_x2
    le2_z1 = case.geometry.Le_blt_flange_z1
    le2_z2 = case.geometry.Le_blt_flange_z2
    k1_catalog = beam_props.get("k1")

    if case.units_system.value == "SI":
        le1_manual_add_mm = 2.0 if db_web_in <= (7.0 / 8.0 + 1e-9) else 3.0
        # Convencion solicitada por usuario:
        # 5*(8*db.1+2mm), con db.1 ingresado en pulgadas y resultado en SI.
        le1_manual_value = 5.0 * (8.0 * db_web_in + le1_manual_add_mm)
        le1_governing_value = max(le_min_web.value, le1_manual_value)
        le1_min_limit = Quantity(value=le1_governing_value, unit="mm")
        le1_min_limit_symbol = (
            "max(Le_min, 5*(8*db.1+2mm))" if le1_manual_add_mm == 2.0 else "max(Le_min, 5*(8*db.1+3mm))"
        )
        le1_min_clause = "AISC 360-22 Tabla J3.4 + Recomendacion del Manual AISC (metrico)"
    else:
        le1_min_limit = le_min_web
        le1_min_limit_symbol = "Le_min"
        le1_min_clause = "AISC 360-22 Tabla J3.4"

    alpha = case.geometry.gap_sp
    hp1_calc = le1_y1.value + le1_y2.value + (case.geometry.n_blt_web_y - 1) * s1y.value
    bp1_calc = 2.0 * (
        le1_x1.value + (case.geometry.n_blt_web_x - 1) * s1x.value + le1_x2.value
    ) + alpha.value
    bp2_calc = bf_catalog.value - 2.0 * le2_z1.value + le2_z1.value + le2_z2.value
    lp2_calc = (
        2.0 * (le2_x1.value + (case.geometry.n_blt_flange_x - 1) * s2x.value + le2_x2.value) + alpha.value
    )

    hp1 = Quantity(value=hp1_calc, unit=le1_y1.unit)
    bp1 = Quantity(value=bp1_calc, unit=le1_x1.unit)
    bp2 = Quantity(value=bp2_calc, unit=bf_catalog.unit)
    lp2 = Quantity(value=lp2_calc, unit=le2_x1.unit)
    le2_z4: Quantity | None = None
    if (
        isinstance(k1_catalog, Quantity)
        and bf_catalog.unit == le2_z1.unit == k1_catalog.unit == s2z1.unit
    ):
        le2_z4 = Quantity(
            value=0.5 * bf_catalog.value
            - (le2_z1.value + k1_catalog.value + (case.geometry.n_blt_flange_z - 1) * s2z1.value),
            unit=bf_catalog.unit,
        )
    g1_blt_flange: Quantity | None = None
    if bf_catalog.unit == le2_z1.unit == s2z1.unit:
        g1_blt_flange = Quantity(
            value=bf_catalog.value - 2.0 * (le2_z1.value + (case.geometry.n_blt_flange_z - 1) * s2z1.value),
            unit=bf_catalog.unit,
        )
    xj_blt_web_values: list[dict[str, object]] = []
    if le1_x1.unit == s1x.unit:
        for j in range(max(case.geometry.n_blt_web_x, 0)):
            xj = Quantity(value=le1_x1.value + j * s1x.value, unit=le1_x1.unit)
            xj_blt_web_values.append({"j": j, "x": xj.model_dump()})
    xk_blt_flange_values: list[dict[str, object]] = []
    if le2_x1.unit == s2x.unit:
        for k in range(max(case.geometry.n_blt_flange_x, 0)):
            xk = Quantity(value=le2_x1.value + k * s2x.value, unit=le2_x1.unit)
            xk_blt_flange_values.append({"k": k, "x": xk.model_dump()})
    f_blt_flange: Quantity | None = None
    if g1_blt_flange is not None and g1_blt_flange.unit == tw_catalog.unit == case.geometry.t_plt_web.unit:
        f_blt_flange = Quantity(
            value=0.5 * g1_blt_flange.value - 0.5 * tw_catalog.value - case.geometry.t_plt_web.value,
            unit=g1_blt_flange.unit,
        )

    # Material properties fallback for reporting summary in step 1.1.1.
    fy_vg = case.materials.Fy_vg
    fu_vg = case.materials.Fu_vg
    if fy_vg is None or fu_vg is None:
        try:
            steel_props = get_hrs_steel_properties(
                steel_type=case.materials.steel_vg,
                unit_system=case.units_system,
            )
            if fy_vg is None and isinstance(steel_props.get("fy"), Quantity):
                fy_vg = steel_props.get("fy")
            if fu_vg is None and isinstance(steel_props.get("fu"), Quantity):
                fu_vg = steel_props.get("fu")
        except Exception:
            pass
    e_vg = case.materials.E_vg
    if e_vg is None:
        e_vg = Quantity(value=200000.0, unit="MPa") if case.units_system.value == "SI" else Quantity(value=29000.0, unit="ksi")
    steel_plt_web = case.materials.steel_plt_web or case.materials.steel_vg
    fy_plt_web: Quantity | None = None
    fu_plt_web: Quantity | None = None
    try:
        plate_props = get_plate_steel_properties(
            steel_type=steel_plt_web,
            unit_system=case.units_system,
        )
        fy_plt_web = plate_props.get("fy") if isinstance(plate_props.get("fy"), Quantity) else None
        fu_plt_web = plate_props.get("fu") if isinstance(plate_props.get("fu"), Quantity) else None
    except Exception:
        pass
    e_plt_web = e_vg
    steel_plt_flange = case.materials.steel_plt_flange or case.materials.steel_vg
    fy_plt_flange: Quantity | None = None
    fu_plt_flange: Quantity | None = None
    try:
        plate_props_top = get_plate_steel_properties(
            steel_type=steel_plt_flange,
            unit_system=case.units_system,
        )
        maybe_fy = plate_props_top.get("fy")
        maybe_fu = plate_props_top.get("fu")
        if isinstance(maybe_fy, Quantity):
            fy_plt_flange = maybe_fy
        if isinstance(maybe_fu, Quantity):
            fu_plt_flange = maybe_fu
    except Exception:
        pass
    e_plt_flange = e_vg
    fnt_web: Quantity | None = None
    fnv_web: Quantity | None = None
    fnt_flange: Quantity | None = None
    fnv_flange: Quantity | None = None
    try:
        bolt_strength_web = get_bolt_strength_properties(
            description=case.materials.desc_blt_web,
            specification=case.materials.std_blt_web,
            unit_system=case.units_system,
        )
        maybe_fnt = bolt_strength_web.get("fnt")
        if isinstance(maybe_fnt, Quantity):
            fnt_web = maybe_fnt
        thread_web = (case.materials.thread_blt_web or "N").strip().upper()
        fnv_key = "fnv_threads_not_excluded" if thread_web == "N" else "fnv_threads_excluded"
        maybe_fnv = bolt_strength_web.get(fnv_key)
        if isinstance(maybe_fnv, Quantity):
            fnv_web = maybe_fnv
    except Exception:
        pass
    try:
        bolt_strength_flange = get_bolt_strength_properties(
            description=case.materials.desc_blt_flange,
            specification=case.materials.std_blt_flange,
            unit_system=case.units_system,
        )
        maybe_fnt = bolt_strength_flange.get("fnt")
        if isinstance(maybe_fnt, Quantity):
            fnt_flange = maybe_fnt
        thread_flange = (case.materials.thread_blt_flange or "").strip().upper()
        fnv_key = "fnv_threads_not_excluded" if thread_flange == "N" else "fnv_threads_excluded"
        maybe_fnv = bolt_strength_flange.get(fnv_key)
        if isinstance(maybe_fnv, Quantity):
            fnv_flange = maybe_fnv
    except Exception:
        pass

    # Net section note variables
    dh_clearance = 1.6 if case.units_system.value == "SI" else (1.6 / 25.4)
    anv1_value = tw_catalog.value * (dvg_catalog.value - case.geometry.n_blt_web_y * (dh_web.value + dh_clearance))
    ant1_value = anv1_value
    area_unit = "mm2" if case.units_system.value == "SI" else "in2"
    anv1 = Quantity(value=anv1_value, unit=area_unit)
    ant1 = Quantity(value=ant1_value, unit=area_unit)
    if case.geometry.n_blt_web_x <= 1:
        u1 = ((t_catalog.value * tw_catalog.value) / ag_catalog.value) if isinstance(ag_catalog, Quantity) else None
        u1_formula = "si n_blt_web_x <= 1 -> U1 = T_vg*tw_vg/A_vg"
    else:
        u1 = 1.0 - 0.5 * tw_catalog.value / ((case.geometry.n_blt_web_x - 1) * s1x.value)
        u1_formula = "si n_blt_web_x > 1 -> U1 = 1 - 0.5*tw_vg/((n_blt_web_x-1)*g_blt_web)"

    if fu_vg is None:
        raise ValueError("Unable to resolve Fu_vg for splice web bolt-hole tearout calculation.")

    if not isinstance(fy_vg, Quantity):
        raise ValueError("Unable to resolve Fy_vg for splice web slenderness check h/tw.")
    if not isinstance(e_vg, Quantity):
        raise ValueError("Unable to resolve E_vg for splice web slenderness check h/tw.")

    if isinstance(h_over_tw_catalog, Quantity):
        h_over_tw_vg = h_over_tw_catalog
    else:
        h_over_tw_vg = Quantity(value=dvg_catalog.value / tw_catalog.value, unit="ratio")

    stress_ratio_e_over_fy: float | None = None
    if e_vg.unit == fy_vg.unit:
        stress_ratio_e_over_fy = e_vg.value / fy_vg.value
    elif e_vg.unit == "MPa" and fy_vg.unit == "ksi":
        stress_ratio_e_over_fy = e_vg.value / (fy_vg.value * 6.894757293168361)
    elif e_vg.unit == "ksi" and fy_vg.unit == "MPa":
        stress_ratio_e_over_fy = e_vg.value / (fy_vg.value / 6.894757293168361)
    if stress_ratio_e_over_fy is None or stress_ratio_e_over_fy <= 0.0:
        raise ValueError("Incompatible stress units for h/tw slenderness check in splice beam web.")
    h_over_tw_limit = Quantity(
        value=5.7 * math.sqrt(stress_ratio_e_over_fy),
        unit="ratio",
    )
    if s1y.unit != dh_web.unit:
        raise ValueError("Incompatible units in lc_blt_web_y = p_blt_web - dh.1.")
    lc_blt_web_y = Quantity(value=s1y.value - dh_web.value, unit=s1y.unit)
    svc_hole_deformation_design_web = bool(case.geometry.svc_hole_deformation_design_web)
    svc_hole_deformation_design_flange = bool(case.geometry.svc_hole_deformation_design_flange)
    phi_fragil_web = 0.75
    phi_fragil_flange = float(case.design_factors.phi_pr)
    phi_rn1_web_v2_vg, tearout_web_inter = compute_bolt_hole_tearout_strength_j36(
        material_fu=fu_vg,
        clear_distance_lc=lc_blt_web_y,
        connected_thickness_t=tw_catalog,
        n_critical_bolts=1,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_web,
    )
    rn1_web_ind_v2_vg = tearout_web_inter.get("rn1_ind")
    ru_web_v2_vg = case.loads.Vu2_sp
    tearout_web_dcr: float | None = None
    tearout_web_passed = False
    if (
        isinstance(ru_web_v2_vg, Quantity)
        and isinstance(phi_rn1_web_v2_vg, Quantity)
        and ru_web_v2_vg.unit == phi_rn1_web_v2_vg.unit
        and phi_rn1_web_v2_vg.value > 0.0
    ):
        tearout_web_dcr = ru_web_v2_vg.value / phi_rn1_web_v2_vg.value
        tearout_web_passed = tearout_web_dcr <= 1.0
    # Plate 1 tearout in v2 (uses same deformation design flag from pernos_grupo_1_web).
    if fu_plt_web is None:
        fu_plt_web = fu_vg
    if fu_plt_web is None:
        raise ValueError("Unable to resolve Fu_plt_web for splice plate 1 bolt-hole tearout calculation.")
    if not (s1y.unit == le1_y1.unit == le1_y2.unit == dh_web.unit):
        raise ValueError(
            "Incompatible units in lc_plt_v2_web = min(p_plt_web - dh.1, Le_plt_web_y1 - 0.5*dh.1, Le_plt_web_y2 - 0.5*dh.1)."
        )
    lc_plt_v2_web_value = min(
        s1y.value - dh_web.value,
        le1_y1.value - 0.5 * dh_web.value,
        le1_y2.value - 0.5 * dh_web.value,
    )
    lc_plt_v2_web = Quantity(value=lc_plt_v2_web_value, unit=s1y.unit)
    phi_rn1_plt_v2_web, tearout_plt1_web_inter = compute_bolt_hole_tearout_strength_j36(
        material_fu=fu_plt_web,
        clear_distance_lc=lc_plt_v2_web,
        connected_thickness_t=case.geometry.t_plt_web,
        n_critical_bolts=1,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_web,
    )
    rn1_plt_v2_web = tearout_plt1_web_inter.get("rn1_ind")
    if not (s1x.unit == le1_x2.unit == dh_web.unit):
        raise ValueError(
            "Incompatible units in lc_plt_v3_web = min(g_plt_web - dh.1, Le_plt_web_x2 - 0.5*dh.1)."
        )
    lc_plt_v3_web = Quantity(
        value=min(
            s1x.value - dh_web.value,
            le1_x2.value - 0.5 * dh_web.value,
        ),
        unit=s1x.unit,
    )
    phi_rn1_plt_v3_web, tearout_plt1_web_v3_inter = compute_bolt_hole_tearout_strength_j36(
        material_fu=fu_plt_web,
        clear_distance_lc=lc_plt_v3_web,
        connected_thickness_t=case.geometry.t_plt_web,
        n_critical_bolts=1,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_web,
    )
    rn1_plt_v3_web = tearout_plt1_web_v3_inter.get("rn1_ind")
    if not (s1x.unit == le1_x1.unit == dh_web.unit):
        raise ValueError(
            "Incompatible units in lc_web_v3_vg = min(g_blt_web - dh.1, Le_blt_web_x1 - 0.5*dh.1)."
        )
    lc_web_v3_vg = Quantity(
        value=min(
            s1x.value - dh_web.value,
            le1_x1.value - 0.5 * dh_web.value,
        ),
        unit=s1x.unit,
    )
    phi_rn1_web_v3_vg, tearout_web_v3_inter = compute_bolt_hole_tearout_strength_j36(
        material_fu=fu_vg,
        clear_distance_lc=lc_web_v3_vg,
        connected_thickness_t=tw_catalog,
        n_critical_bolts=1,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_web,
    )
    rn1_web_v3_vg = tearout_web_v3_inter.get("rn1_ind")
    ru1_web_v3_vg = case.loads.Vu3_sp
    dcr1_web_v3_vg: float | None = None
    result1_web_v3_vg = "FAIL"
    if (
        isinstance(ru1_web_v3_vg, Quantity)
        and isinstance(phi_rn1_web_v3_vg, Quantity)
        and ru1_web_v3_vg.unit == phi_rn1_web_v3_vg.unit
        and abs(phi_rn1_web_v3_vg.value) > 1e-12
    ):
        dcr1_web_v3_vg = abs(ru1_web_v3_vg.value) / phi_rn1_web_v3_vg.value
        result1_web_v3_vg = "PASS" if dcr1_web_v3_vg <= 1.0 else "FAIL"

    # Flange tension tearout in direction 3 (AISC 360-22 J3.11a.(b), DRY function).
    if fu_vg is None:
        raise ValueError("Unable to resolve Fu_vg for splice flange tearout calculation.")
    if not (s2x.unit == dh_flange.unit == le2_x1.unit == dvg_catalog.unit == tf_catalog.unit):
        raise ValueError(
            "Incompatible units for flange tearout check in direction 3."
        )
    lc_flange_p3_vg = Quantity(
        value=min(
            s2x.value - dh_flange.value,
            le2_x1.value - 0.5 * dh_flange.value,
        ),
        unit=s2x.unit,
    )
    phi_rn1_flange_p3_vg, tearout_flange_p3_inter = compute_bolt_hole_tearout_strength_j36(
        material_fu=fu_vg,
        clear_distance_lc=lc_flange_p3_vg,
        connected_thickness_t=tf_catalog,
        n_critical_bolts=1,
        phi_n=phi_fragil_flange,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_flange,
    )
    rn1_flange_p3_vg = tearout_flange_p3_inter.get("rn1_ind")
    force_unit = "kip" if case.units_system == UnitSystem.US else "kN"
    pu_base = case.loads.Pu_sp.value
    if case.units_system == UnitSystem.SI and case.loads.Pu_sp.unit == "N":
        pu_base = case.loads.Pu_sp.value / 1000.0
    if case.units_system == UnitSystem.US and case.loads.Pu_sp.unit == "lb":
        pu_base = case.loads.Pu_sp.value / 1000.0
    mu3_base = case.loads.Mu3_sp.value
    if case.units_system == UnitSystem.SI:
        # Keep mu3_base in kN-mm to match denominator in mm and get force in kN.
        if case.loads.Mu3_sp.unit == "kN-m":
            mu3_base = case.loads.Mu3_sp.value * 1000.0
        elif case.loads.Mu3_sp.unit == "kN-mm":
            mu3_base = case.loads.Mu3_sp.value
        elif case.loads.Mu3_sp.unit == "N-mm":
            mu3_base = case.loads.Mu3_sp.value / 1000.0
        else:
            raise ValueError("Unsupported Mu3_sp unit for SI in splice detailing.")
    else:
        # Keep mu3_base in kip-in to match denominator in in and get force in kip.
        if case.loads.Mu3_sp.unit == "kip-in":
            mu3_base = case.loads.Mu3_sp.value
        elif case.loads.Mu3_sp.unit == "kip-ft":
            mu3_base = case.loads.Mu3_sp.value * 12.0
        elif case.loads.Mu3_sp.unit == "lb-in":
            mu3_base = case.loads.Mu3_sp.value / 1000.0
        else:
            raise ValueError("Unsupported Mu3_sp unit for US in splice detailing.")
    ru1_flange_p3_raw = (1.0 - case.loads.alpha_Pu_web) * pu_base + mu3_base / (dvg_catalog.value - tf_catalog.value)
    ru1_flange_p3_vg = Quantity(value=ru1_flange_p3_raw, unit=force_unit)
    dcr1_flange_p3_vg: float | None = None
    result1_flange_p3_vg = "FAIL"
    if (
        isinstance(phi_rn1_flange_p3_vg, Quantity)
        and ru1_flange_p3_vg.unit == phi_rn1_flange_p3_vg.unit
        and abs(phi_rn1_flange_p3_vg.value) > 1e-12
    ):
        dcr1_flange_p3_vg = abs(ru1_flange_p3_vg.value) / phi_rn1_flange_p3_vg.value
        result1_flange_p3_vg = "PASS" if dcr1_flange_p3_vg <= 1.0 else "FAIL"

    # Flange tension hole bearing in direction 3 (AISC 360-22 J3.11a.(a), DRY function).
    phi_rn2_flange_p3_vg, bearing_flange_p3_inter = compute_bolt_hole_bearing_strength_j36(
        material_fu=fu_vg,
        bolt_diameter_d=db_flange,
        connected_thickness_t=tf_catalog,
        phi_n=phi_fragil_flange,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_flange,
    )
    rn2_flange_p3_vg = bearing_flange_p3_inter.get("rn2")
    ru2_flange_p3_vg = Quantity(value=ru1_flange_p3_vg.value, unit=ru1_flange_p3_vg.unit)
    dcr2_flange_p3_vg: float | None = None
    result2_flange_p3_vg = "FAIL"
    if (
        isinstance(phi_rn2_flange_p3_vg, Quantity)
        and ru2_flange_p3_vg.unit == phi_rn2_flange_p3_vg.unit
        and abs(phi_rn2_flange_p3_vg.value) > 1e-12
    ):
        dcr2_flange_p3_vg = abs(ru2_flange_p3_vg.value) / phi_rn2_flange_p3_vg.value
        result2_flange_p3_vg = "PASS" if dcr2_flange_p3_vg <= 1.0 else "FAIL"

    # Flange shear tearout in direction 1 (AISC 360-22 J3.11a.(b), DRY function).
    if not (s2z1.unit == le2_z1.unit == dh_flange.unit):
        raise ValueError(
            "Incompatible units for flange tearout check in direction 1."
        )
    if case.geometry.n_blt_flange_z >= 2:
        lc_flange_v1_vg = Quantity(
            value=min(
                s2z1.value - dh_flange.value,
                le2_z1.value - 0.5 * dh_flange.value,
            ),
            unit=s2z1.unit,
        )
        lc_flange_v1_vg_formula = (
            "si n_blt_flange_z >= 2 -> lc_flange_v1_vg = min(g_blt_flange - dh.2, Le_blt_flange_z1 - 0.5*dh.2)"
        )
    else:
        lc_flange_v1_vg = Quantity(
            value=le2_z1.value - 0.5 * dh_flange.value,
            unit=le2_z1.unit,
        )
        lc_flange_v1_vg_formula = (
            "si n_blt_flange_z = 1 -> lc_flange_v1_vg = Le_blt_flange_z1 - 0.5*dh.2"
        )
    phi_rn1_flange_v1_vg, tearout_flange_v1_inter = compute_bolt_hole_tearout_strength_j36(
        material_fu=fu_vg,
        clear_distance_lc=lc_flange_v1_vg,
        connected_thickness_t=tf_catalog,
        n_critical_bolts=1,
        phi_n=phi_fragil_flange,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_flange,
    )
    rn1_flange_v1_vg = tearout_flange_v1_inter.get("rn1_ind")

    # Flange block shear in direction 3 (AISC 360-22 J4.3, DRY J4-5 function), two project cases.
    if fy_vg is None:
        raise ValueError("Unable to resolve Fy_vg for splice flange block-shear calculation.")
    if not isinstance(ag_catalog, Quantity):
        raise ValueError("Unable to resolve A_g (ag) from beam catalog for splice flange block-shear calculation.")
    hole_add_block_flange = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    dh2_plus = dh_flange.value + hole_add_block_flange
    area_unit_flange = "in2" if case.units_system == UnitSystem.US else "mm2"

    # Case 1
    agt1_flange_v3_vg = Quantity(
        value=2.0 * (le2_z1.value * tf_catalog.value),
        unit=area_unit_flange,
    )
    ant1_flange_v3_vg = Quantity(
        value=agt1_flange_v3_vg.value - 2.0 * tf_catalog.value * 0.5 * dh2_plus,
        unit=area_unit_flange,
    )
    agv1_flange_v3_vg = Quantity(
        value=2.0 * tf_catalog.value * (le2_x1.value + (case.geometry.n_blt_flange_x - 1) * s2x.value),
        unit=area_unit_flange,
    )
    anv1_flange_v3_vg = Quantity(
        value=agv1_flange_v3_vg.value - 2.0 * tf_catalog.value * (case.geometry.n_blt_flange_x - 0.5) * dh2_plus,
        unit=area_unit_flange,
    )
    ubs_flange_v3_vg = float(case.geometry.Ubs_flange_v3_vg)
    phi_rn4_case1_flange_p3_vg, block_shear_flange_case1_inter = compute_block_shear_strength_j45(
        material_fu=fu_vg,
        material_fy=fy_vg,
        net_shear_area_anv=anv1_flange_v3_vg,
        gross_shear_area_agv=agv1_flange_v3_vg,
        net_tension_area_ant=ant1_flange_v3_vg,
        ubs_factor=ubs_flange_v3_vg,
        phi_n=phi_fragil_flange,
        unit_system=case.units_system,
    )
    rn4_1_case1_flange_p3_vg = block_shear_flange_case1_inter.get("rn1")
    rn4_2_case1_flange_p3_vg = block_shear_flange_case1_inter.get("rn2")
    rn4_case1_flange_p3_vg = block_shear_flange_case1_inter.get("rn")

    # Case 2
    agt2_flange_v3_vg = Quantity(
        value=0.5 * (ag_catalog.value - (dvg_catalog.value - 2.0 * kdes_catalog.value) * tw_catalog.value),
        unit=area_unit_flange,
    )
    ant2_flange_v3_vg = Quantity(
        value=agt2_flange_v3_vg.value - case.geometry.n_blt_flange_z * tf_catalog.value * dh2_plus,
        unit=area_unit_flange,
    )
    agv2_flange_v3_vg = Quantity(
        value=tw_catalog.value * (le2_x1.value + (case.geometry.n_blt_flange_x - 1) * s2x.value),
        unit=area_unit_flange,
    )
    anv2_flange_v3_vg = Quantity(
        value=agv2_flange_v3_vg.value,
        unit=area_unit_flange,
    )
    ubs_flange_v1_vg = float(case.geometry.Ubs_flange_v1_vg)
    phi_rn4_case2_flange_p3_vg, block_shear_flange_case2_inter = compute_block_shear_strength_j45(
        material_fu=fu_vg,
        material_fy=fy_vg,
        net_shear_area_anv=anv2_flange_v3_vg,
        gross_shear_area_agv=agv2_flange_v3_vg,
        net_tension_area_ant=ant2_flange_v3_vg,
        ubs_factor=ubs_flange_v1_vg,
        phi_n=phi_fragil_flange,
        unit_system=case.units_system,
    )
    rn4_1_case2_flange_p3_vg = block_shear_flange_case2_inter.get("rn1")
    rn4_2_case2_flange_p3_vg = block_shear_flange_case2_inter.get("rn2")
    rn4_case2_flange_p3_vg = block_shear_flange_case2_inter.get("rn")

    # Envelope case
    phi_rn4_flange_p3_vg: Quantity
    controlling_case_flange_p3_vg: str
    if phi_rn4_case1_flange_p3_vg.value <= phi_rn4_case2_flange_p3_vg.value:
        phi_rn4_flange_p3_vg = phi_rn4_case1_flange_p3_vg
        controlling_case_flange_p3_vg = "Caso 1"
    else:
        phi_rn4_flange_p3_vg = phi_rn4_case2_flange_p3_vg
        controlling_case_flange_p3_vg = "Caso 2"
    ru4_flange_p3_raw = (1.0 - case.loads.alpha_Pu_web) * pu_base + mu3_base / (dvg_catalog.value - tf_catalog.value)
    if ru4_flange_p3_raw < 0.0:
        ru4_flange_p3_raw = 0.0
    ru4_flange_p3_vg = Quantity(value=ru4_flange_p3_raw, unit=force_unit)
    dcr4_flange_p3_vg: float | None = None
    result4_flange_p3_vg = "FAIL"
    if (
        ru4_flange_p3_vg.unit == phi_rn4_flange_p3_vg.unit
        and abs(phi_rn4_flange_p3_vg.value) > 1e-12
    ):
        dcr4_flange_p3_vg = abs(ru4_flange_p3_vg.value) / phi_rn4_flange_p3_vg.value
        result4_flange_p3_vg = "PASS" if dcr4_flange_p3_vg <= 1.0 else "FAIL"

    # Beam flexural rupture with holes in tension flange (AISC 360-22 F13.1).
    sx_catalog = beam_props.get("zx")
    if not isinstance(sx_catalog, Quantity):
        raise ValueError("Unable to resolve Sx_vg (using catalog zx) for splice beam flexural rupture check.")
    if not (tf_catalog.unit == bf_catalog.unit == dh_flange.unit):
        raise ValueError("Incompatible units for Afg_flange_m1_vg / Afn_flange_m1_vg calculation.")
    hole_add_f13 = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    area_unit = "in2" if case.units_system == UnitSystem.US else "mm2"
    afg_flange_m1_vg = Quantity(
        value=tf_catalog.value * bf_catalog.value,
        unit=area_unit,
    )
    afn_flange_m1_vg = Quantity(
        value=afg_flange_m1_vg.value
        - 2.0 * case.geometry.n_blt_flange_z * (dh_flange.value + hole_add_f13) * tf_catalog.value,
        unit=area_unit,
    )
    phi_no_ductil_m1 = 0.9
    phi_rn1_flange_m1_vg, flange_flex_rupture_m1_inter = compute_member_flexural_rupture_with_tension_flange_holes_f131(
        material_fu=fu_vg,
        material_fy=fy_vg,
        net_tension_flange_area_afn=afn_flange_m1_vg,
        gross_tension_flange_area_agf=afg_flange_m1_vg,
        elastic_section_modulus_sx=sx_catalog,
        phi_n=phi_no_ductil_m1,
        unit_system=case.units_system,
    )
    rn1_flange_m1_vg = flange_flex_rupture_m1_inter.get("mn")
    ru1_flange_m1_vg = case.loads.Mu3_sp
    if (
        isinstance(phi_rn1_flange_m1_vg, Quantity)
        and ru1_flange_m1_vg.unit != phi_rn1_flange_m1_vg.unit
    ):
        conversions = {
            ("kN-m", "kN-mm"): 1000.0,
            ("kN-mm", "kN-m"): 1.0 / 1000.0,
            ("kip-ft", "kip-in"): 12.0,
            ("kip-in", "kip-ft"): 1.0 / 12.0,
        }
        factor = conversions.get((ru1_flange_m1_vg.unit, phi_rn1_flange_m1_vg.unit))
        if factor is not None:
            ru1_flange_m1_vg = Quantity(
                value=ru1_flange_m1_vg.value * factor,
                unit=phi_rn1_flange_m1_vg.unit,
            )
    dcr1_flange_m1_vg: float | None = None
    result1_flange_m1_vg = "FAIL"
    limit_applies_flange_m1 = bool(flange_flex_rupture_m1_inter.get("tensile_rupture_limit_applies"))
    if not limit_applies_flange_m1:
        dcr1_flange_m1_vg = 0.0
        result1_flange_m1_vg = "PASS"
    elif (
        ru1_flange_m1_vg.unit == phi_rn1_flange_m1_vg.unit
        and abs(phi_rn1_flange_m1_vg.value) > 1e-12
    ):
        dcr1_flange_m1_vg = abs(ru1_flange_m1_vg.value) / phi_rn1_flange_m1_vg.value
        result1_flange_m1_vg = "PASS" if dcr1_flange_m1_vg <= 1.0 else "FAIL"

    # Hole bearing (aplatamiento) per J3-6a/J3-6b at one critical bolt.
    phi_rn2_web_v2_vg, bearing_web_inter = compute_bolt_hole_bearing_strength_j36(
        material_fu=fu_vg,
        bolt_diameter_d=db_web,
        connected_thickness_t=tw_catalog,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_web,
    )
    rn2_web_v2_vg = bearing_web_inter.get("rn2")
    phi_rn2_plt_v2_web, bearing_plt1_web_inter = compute_bolt_hole_bearing_strength_j36(
        material_fu=fu_plt_web,
        bolt_diameter_d=db_web,
        connected_thickness_t=case.geometry.t_plt_web,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_web,
    )
    rn2_plt_v2_web = bearing_plt1_web_inter.get("rn2")
    ru2_plt_v2_web = ru_web_v2_vg
    dcr2_plt_v2_web: float | None = None
    result2_plt_v2_web = "FAIL"
    if (
        isinstance(ru2_plt_v2_web, Quantity)
        and isinstance(phi_rn2_plt_v2_web, Quantity)
        and ru2_plt_v2_web.unit == phi_rn2_plt_v2_web.unit
        and abs(phi_rn2_plt_v2_web.value) > 1e-12
    ):
        dcr2_plt_v2_web = abs(ru2_plt_v2_web.value) / phi_rn2_plt_v2_web.value
        result2_plt_v2_web = "PASS" if dcr2_plt_v2_web <= 1.0 else "FAIL"
    phi_rn2_web_v3_vg, bearing_web_v3_inter = compute_bolt_hole_bearing_strength_j36(
        material_fu=fu_vg,
        bolt_diameter_d=db_web,
        connected_thickness_t=tw_catalog,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
        deformation_at_service_is_design_consideration=svc_hole_deformation_design_web,
    )
    rn2_web_v3_vg = bearing_web_v3_inter.get("rn2")
    ru2_web_v3_vg = case.loads.Vu3_sp
    dcr2_web_v3_vg: float | None = None
    result2_web_v3_vg = "FAIL"
    if (
        isinstance(ru2_web_v3_vg, Quantity)
        and isinstance(phi_rn2_web_v3_vg, Quantity)
        and ru2_web_v3_vg.unit == phi_rn2_web_v3_vg.unit
        and abs(phi_rn2_web_v3_vg.value) > 1e-12
    ):
        dcr2_web_v3_vg = abs(ru2_web_v3_vg.value) / phi_rn2_web_v3_vg.value
        result2_web_v3_vg = "PASS" if dcr2_web_v3_vg <= 1.0 else "FAIL"
    # Beam tension rupture (AISC 360-22 J4.1(b), Eq. J4-2) in direction 3.
    hole_add_v3 = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    a_vg_v3 = Quantity(
        value=dvg_catalog.value * tw_catalog.value,
        unit="in2" if case.units_system == UnitSystem.US else "mm2",
    )
    sqrt3 = 3.0 ** 0.5
    ant_v3_length_expr = (
        2.0 * s1x.value * (case.geometry.n_blt_web_x - 1) * sqrt3 / 3.0
        + (case.geometry.n_blt_web_y - 1) * s1y.value
        - case.geometry.n_blt_web_y * (dh_web.value + hole_add_v3)
    )
    if ant_v3_length_expr <= t_catalog.value:
        ant_v3_vg = Quantity(
            value=tw_catalog.value * ant_v3_length_expr,
            unit=a_vg_v3.unit,
        )
        ant_v3_vg_formula = (
            "si 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web - "
            "n_blt_web_y*(dh.1 + 1.80mm) <= T_vg -> "
            "Ant_v3_vg = tw_vg*(2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + "
            "(n_blt_web_y - 1)*p_blt_web - n_blt_web_y*(dh.1 + 1.80mm))"
        )
    else:
        ant_v3_vg = Quantity(
            value=a_vg_v3.value - case.geometry.n_blt_web_y * (dh_web.value + hole_add_v3) * tw_catalog.value,
            unit=a_vg_v3.unit,
        )
        ant_v3_vg_formula = (
            "si 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web - "
            "n_blt_web_y*(dh.1 + 1.80mm) > T_vg -> "
            "Ant_v3_vg = A_vg - n_blt_web_y*(dh.1 + 1.80mm)*tw_vg"
        )
    if case.geometry.n_blt_web_x <= 1:
        u_v3_vg = (t_catalog.value * tw_catalog.value) / a_vg_v3.value
        u_v3_vg_formula = "si n_blt_web_x <= 1 -> U_v3_vg = T_vg*tw_vg/A_vg"
    else:
        u_v3_vg = 1.0 - 0.5 * tw_catalog.value / (case.geometry.n_blt_web_x * s1x.value)
        u_v3_vg_formula = "si n_blt_web_x > 1 -> U_v3_vg = 1 - 0.5*tw_vg/(n_blt_web_x*g_blt_web)"
    ae_v3_vg = Quantity(value=ant_v3_vg.value * u_v3_vg, unit=ant_v3_vg.unit)
    phi_rn3_v3_vg, tension_rupture_v3_inter = compute_element_tension_rupture_strength_j41b(
        material_fu=fu_vg,
        effective_net_area_ae=ae_v3_vg,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn3_v3_vg = tension_rupture_v3_inter.get("rn")
    ru3_v3_vg = Quantity(
        value=case.loads.Pu_sp.value,
        unit=case.loads.Pu_sp.unit,
    )
    dcr3_v3_vg: float | None = None
    result3_v3_vg = "FAIL"
    if (
        isinstance(ru3_v3_vg, Quantity)
        and isinstance(phi_rn3_v3_vg, Quantity)
        and ru3_v3_vg.unit == phi_rn3_v3_vg.unit
        and abs(phi_rn3_v3_vg.value) > 1e-12
    ):
        dcr3_v3_vg = abs(ru3_v3_vg.value) / phi_rn3_v3_vg.value
        result3_v3_vg = "PASS" if dcr3_v3_vg <= 1.0 else "FAIL"

    def _convert_moment_value_to_unit(value: Quantity, target_unit: str) -> float:
        if value.unit == target_unit:
            return value.value
        conversions = {
            ("kN-mm", "kN-m"): 1.0 / 1000.0,
            ("kN-m", "kN-mm"): 1000.0,
            ("kip-in", "kip-ft"): 1.0 / 12.0,
            ("kip-ft", "kip-in"): 12.0,
        }
        factor = conversions.get((value.unit, target_unit))
        if factor is None:
            raise ValueError(f"Unsupported moment unit conversion: {value.unit} -> {target_unit}.")
        return value.value * factor

    # Beam combined-force interaction (AISC 360-22 H1-1a/H1-1b) using DRY shared function.
    pr_over_pc_vg: float | None = None
    mrx_over_mcx_vg: float | None = None
    mry_over_mcy_vg = 0.0
    mrx_over_mcx_mu3_term: float | None = None
    dcr_fcomb_vg: float | None = None
    h11_equation_used_vg: str | None = None
    result_fcomb_vg = "NOT_AVAILABLE"
    member_capacity = case.capacidad_miembro
    if member_capacity is not None and abs(member_capacity.phiMn3.value) > 1e-12:
        if case.loads.Pu_sp.value >= 0.0:
            pr_over_pc_vg = float(dcr3_v3_vg) if isinstance(dcr3_v3_vg, (int, float)) else 0.0
        elif abs(member_capacity.phiPnc.value) > 1e-12:
            pr_over_pc_vg = case.loads.Pu_sp.value / member_capacity.phiPnc.value

        mu3_in_phi_mn3_unit = _convert_moment_value_to_unit(case.loads.Mu3_sp, member_capacity.phiMn3.unit)
        mrx_over_mcx_mu3_term = abs(mu3_in_phi_mn3_unit) / member_capacity.phiMn3.value
        dcr_481 = float(dcr1_flange_m1_vg) if isinstance(dcr1_flange_m1_vg, (int, float)) else 0.0
        mrx_over_mcx_vg = max(mrx_over_mcx_mu3_term, dcr_481)

        if pr_over_pc_vg is not None:
            member_h11_inter = compute_member_combined_interaction_h11(
                pr_over_pc=pr_over_pc_vg,
                mrx_over_mcx=mrx_over_mcx_vg,
                mry_over_mcy=mry_over_mcy_vg,
            )
            dcr_fcomb_vg = float(member_h11_inter.get("dcr", 0.0))
            h11_equation_used_vg = str(member_h11_inter.get("equation_used", "H1-1b"))
            result_fcomb_vg = "PASS" if bool(member_h11_inter.get("passes", False)) else "FAIL"
    # Block shear in direction 3 (AISC 360-22w J4.3, using DRY J4-5 function).
    if fy_vg is None:
        raise ValueError("Unable to resolve Fy_vg for splice web block-shear calculation (v3).")
    area_unit_v3 = "in2" if case.units_system == UnitSystem.US else "mm2"
    hole_add_block_v3 = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    agv_web_v3_vg = Quantity(
        value=2.0 * (s1x.value * (case.geometry.n_blt_web_x - 1) * tw_catalog.value + le1_x1.value * tw_catalog.value),
        unit=area_unit_v3,
    )
    anv_web_v3_vg = Quantity(
        value=2.0 * (
            0.5 * agv_web_v3_vg.value
            - (case.geometry.n_blt_web_x - 0.5) * tw_catalog.value * (dh_web.value + hole_add_block_v3)
        ),
        unit=area_unit_v3,
    )
    agt_web_v3_vg = Quantity(
        value=s1y.value * (case.geometry.n_blt_web_y - 1) * tw_catalog.value,
        unit=area_unit_v3,
    )
    ant_web_v3_vg = Quantity(
        value=agt_web_v3_vg.value
        - (case.geometry.n_blt_web_y - 1) * tw_catalog.value * (dh_web.value + hole_add_block_v3),
        unit=area_unit_v3,
    )
    ubs_web_v3_vg = float(case.geometry.Ubs_web_v3_vg)
    phi_rn4_web_v3_vg, block_shear_web_v3_inter = compute_block_shear_strength_j45(
        material_fu=fu_vg,
        material_fy=fy_vg,
        net_shear_area_anv=anv_web_v3_vg,
        gross_shear_area_agv=agv_web_v3_vg,
        net_tension_area_ant=ant_web_v3_vg,
        ubs_factor=ubs_web_v3_vg,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn4_web_v3_vg = block_shear_web_v3_inter.get("rn")
    rn4_1_web_v3_vg = block_shear_web_v3_inter.get("rn1")
    rn4_2_web_v3_vg = block_shear_web_v3_inter.get("rn2")
    ru4_web_v3_vg = Quantity(
        value=case.loads.Pu_sp.value * case.loads.alpha_Pu_web,
        unit=case.loads.Pu_sp.unit,
    )
    dcr4_web_v3_vg: float | None = None
    result4_web_v3_vg = "FAIL"
    if (
        isinstance(ru4_web_v3_vg, Quantity)
        and isinstance(phi_rn4_web_v3_vg, Quantity)
        and ru4_web_v3_vg.unit == phi_rn4_web_v3_vg.unit
        and abs(phi_rn4_web_v3_vg.value) > 1e-12
    ):
        dcr4_web_v3_vg = abs(ru4_web_v3_vg.value) / phi_rn4_web_v3_vg.value
        result4_web_v3_vg = "PASS" if dcr4_web_v3_vg <= 1.0 else "FAIL"
    # Bolt shear rupture per bolt (AISC 360-22 J3.7) with project-requested fragile phi.
    bolt_shear_web = compute_bolt_shear_rupture_capacity_per_bolt(
        bolt_diameter=db_web,
        bolt_fnv=fnv_web if isinstance(fnv_web, Quantity) else Quantity(value=0.0, unit="MPa" if case.units_system == UnitSystem.SI else "ksi"),
        phi=phi_fragil_web,
        unit_system=case.units_system,
    ) if isinstance(fnv_web, Quantity) else None
    bolt_shear_flange = compute_bolt_shear_rupture_capacity_per_bolt(
        bolt_diameter=db_flange,
        bolt_fnv=fnv_flange if isinstance(fnv_flange, Quantity) else Quantity(value=0.0, unit="MPa" if case.units_system == UnitSystem.SI else "ksi"),
        phi=phi_fragil_flange,
        unit_system=case.units_system,
    ) if isinstance(fnv_flange, Quantity) else None
    # Beam shear rupture (AISC 360-22 J4.3) with net shear area at web.
    av_web_v2_vg = Quantity(
        value=dvg_catalog.value * tw_catalog.value,
        unit="in2" if case.units_system == UnitSystem.US else "mm2",
    )
    hole_add_web = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    anv_web_v2_vg = Quantity(
        value=av_web_v2_vg.value - case.geometry.n_blt_web_y * (dh_web.value + hole_add_web) * tw_catalog.value,
        unit=av_web_v2_vg.unit,
    )
    phi_rn4_web_v2_vg, shear_rupture_web_inter = compute_element_shear_rupture_strength_j43(
        material_fu=fu_vg,
        net_shear_area_anv=anv_web_v2_vg,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn4_web_v2_vg = shear_rupture_web_inter.get("rn")
    ru4_web_v2_vg = case.loads.Vu2_sp
    dcr4_web_v2_vg: float | None = None
    result4_web_v2_vg = "FAIL"
    if (
        isinstance(ru4_web_v2_vg, Quantity)
        and isinstance(phi_rn4_web_v2_vg, Quantity)
        and ru4_web_v2_vg.unit == phi_rn4_web_v2_vg.unit
        and abs(phi_rn4_web_v2_vg.value) > 1e-12
    ):
        dcr4_web_v2_vg = abs(ru4_web_v2_vg.value) / phi_rn4_web_v2_vg.value
        result4_web_v2_vg = "PASS" if dcr4_web_v2_vg <= 1.0 else "FAIL"
    # Plate 1 shear rupture in v2 (DRY mapping for splice: J4.2(b)).
    if fu_plt_web is None:
        fu_plt_web = fu_vg
    if fu_plt_web is None:
        raise ValueError("Unable to resolve Fu_plt_web for splice plate 1 shear-rupture calculation.")
    hole_add_plt = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    area_unit_plt = "in2" if case.units_system == UnitSystem.US else "mm2"
    anv_plt_v2_web = Quantity(
        value=(
            s1y.value * (case.geometry.n_blt_web_y - 1)
            + le1_y1.value
            + le1_y2.value
            - case.geometry.n_blt_web_y * (dh_web.value + hole_add_plt)
        ) * case.geometry.t_plt_web.value,
        unit=area_unit_plt,
    )
    phi_rn6_plt_v2_web, shear_rupture_plt1_inter = compute_element_shear_rupture_strength_j43(
        material_fu=fu_plt_web,
        net_shear_area_anv=anv_plt_v2_web,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn6_plt_v2_web = shear_rupture_plt1_inter.get("rn")
    ru6_plt_v2_web = case.loads.Vu2_sp
    dcr6_plt_v2_web: float | None = None
    result6_plt_v2_web = "FAIL"
    if (
        isinstance(ru6_plt_v2_web, Quantity)
        and isinstance(phi_rn6_plt_v2_web, Quantity)
        and ru6_plt_v2_web.unit == phi_rn6_plt_v2_web.unit
        and abs(phi_rn6_plt_v2_web.value) > 1e-12
    ):
        dcr6_plt_v2_web = abs(ru6_plt_v2_web.value) / phi_rn6_plt_v2_web.value
        result6_plt_v2_web = "PASS" if dcr6_plt_v2_web <= 1.0 else "FAIL"

    if fy_vg is None:
        raise ValueError("Unable to resolve Fy_vg for splice web block-shear calculation.")
    hole_add_block = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    area_unit = "in2" if case.units_system == UnitSystem.US else "mm2"
    agv_web_v2_vg = Quantity(
        value=s1y.value * (case.geometry.n_blt_web_y - 1) * tw_catalog.value
        + (le1_y3.value - tf_catalog.value) * tw_catalog.value
        + tf_catalog.value * bf_catalog.value,
        unit=area_unit,
    )
    a_gt_web_v2_vg = Quantity(
        value=s1x.value * (case.geometry.n_blt_web_x - 1) * tw_catalog.value
        + le1_x1.value * tw_catalog.value,
        unit=area_unit,
    )
    anv5_web_v2_vg = Quantity(
        value=agv_web_v2_vg.value
        - (case.geometry.n_blt_web_y - 0.5) * tw_catalog.value * (dh_web.value + hole_add_block),
        unit=area_unit,
    )
    ant_web_v2_vg = Quantity(
        value=a_gt_web_v2_vg.value
        - (case.geometry.n_blt_web_x - 0.5) * tw_catalog.value * (dh_web.value + hole_add_block),
        unit=area_unit,
    )
    ubs_web_v2_vg = float(case.geometry.Ubs_web_v2_vg)
    phi_rn5_web_v2_vg, block_shear_web_inter = compute_block_shear_strength_j45(
        material_fu=fu_vg,
        material_fy=fy_vg,
        net_shear_area_anv=anv5_web_v2_vg,
        gross_shear_area_agv=agv_web_v2_vg,
        net_tension_area_ant=ant_web_v2_vg,
        ubs_factor=ubs_web_v2_vg,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn5_web_v2_vg = block_shear_web_inter.get("rn")
    rn5_1_web_v2_vg = block_shear_web_inter.get("rn1")
    rn5_2_web_v2_vg = block_shear_web_inter.get("rn2")
    ru5_web_v2_vg = case.loads.Vu2_sp
    dcr5_web_v2_vg: float | None = None
    result5_web_v2_vg = "FAIL"
    if (
        isinstance(ru5_web_v2_vg, Quantity)
        and isinstance(phi_rn5_web_v2_vg, Quantity)
        and ru5_web_v2_vg.unit == phi_rn5_web_v2_vg.unit
        and abs(phi_rn5_web_v2_vg.value) > 1e-12
    ):
        dcr5_web_v2_vg = abs(ru5_web_v2_vg.value) / phi_rn5_web_v2_vg.value
        result5_web_v2_vg = "PASS" if dcr5_web_v2_vg <= 1.0 else "FAIL"
    # Plate 1 block shear in v2 (AISC 360-22w J4.3, DRY J4-5 function).
    if fy_plt_web is None:
        fy_plt_web = fy_vg
    if fy_plt_web is None:
        raise ValueError("Unable to resolve Fy_plt_web for splice plate 1 block-shear calculation.")
    if fu_plt_web is None:
        fu_plt_web = fu_vg
    if fu_plt_web is None:
        raise ValueError("Unable to resolve Fu_plt_web for splice plate 1 block-shear calculation.")
    hole_add_block_plt1 = 1.8 if case.units_system == UnitSystem.SI else (1.8 / 25.4)
    t_plt_web = case.geometry.t_plt_web
    le_plt_web_y_min = min(le1_y1.value, le1_y2.value)
    agv_plt_v2_web = Quantity(
        value=(s1y.value * (case.geometry.n_blt_web_y - 1) + le_plt_web_y_min) * t_plt_web.value,
        unit=area_unit,
    )
    agt_plt_v2_web = Quantity(
        value=(s1x.value * (case.geometry.n_blt_web_x - 1) + le1_x2.value) * t_plt_web.value,
        unit=area_unit,
    )
    anv_plt_v2_web = Quantity(
        value=agv_plt_v2_web.value
        - (case.geometry.n_blt_web_y - 0.5) * t_plt_web.value * (dh_web.value + hole_add_block_plt1),
        unit=area_unit,
    )
    ant_plt_v2_web = Quantity(
        value=agt_plt_v2_web.value
        - (case.geometry.n_blt_web_x - 0.5) * t_plt_web.value * (dh_web.value + hole_add_block_plt1),
        unit=area_unit,
    )
    ubs_plt_v2_web = float(case.geometry.Ubs_web_v2_vg)
    phi_rn4_plt_v2_web, block_shear_plt1_inter = compute_block_shear_strength_j45(
        material_fu=fu_plt_web,
        material_fy=fy_plt_web,
        net_shear_area_anv=anv_plt_v2_web,
        gross_shear_area_agv=agv_plt_v2_web,
        net_tension_area_ant=ant_plt_v2_web,
        ubs_factor=ubs_plt_v2_web,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn4_1_plt_v2_web = block_shear_plt1_inter.get("rn1")
    rn4_2_plt_v2_web = block_shear_plt1_inter.get("rn2")
    rn4_plt_v2_web = block_shear_plt1_inter.get("rn")
    ru4_plt_v2_web = case.loads.Vu2_sp
    dcr4_plt_v2_web: float | None = None
    result4_plt_v2_web = "FAIL"
    if (
        isinstance(ru4_plt_v2_web, Quantity)
        and isinstance(phi_rn4_plt_v2_web, Quantity)
        and ru4_plt_v2_web.unit == phi_rn4_plt_v2_web.unit
        and abs(phi_rn4_plt_v2_web.value) > 1e-12
    ):
        dcr4_plt_v2_web = abs(ru4_plt_v2_web.value) / phi_rn4_plt_v2_web.value
        result4_plt_v2_web = "PASS" if dcr4_plt_v2_web <= 1.0 else "FAIL"
    # Plate 1 block shear in v3 (AISC 360-22 J4-5, DRY function).
    area_unit_plt_v3 = "in2" if case.units_system == UnitSystem.US else "mm2"
    agv_plt_v3_web = Quantity(
        value=2.0
        * (
            s1x.value * (case.geometry.n_blt_web_x - 1) * t_plt_web.value
            + le1_x2.value * t_plt_web.value
        ),
        unit=area_unit_plt_v3,
    )
    anv_plt_v3_web = Quantity(
        value=2.0
        * (
            0.5 * agv_plt_v3_web.value
            - (case.geometry.n_blt_web_x - 0.5) * t_plt_web.value * (dh_web.value + hole_add_block_plt1)
        ),
        unit=area_unit_plt_v3,
    )
    agt_plt_v3_web = Quantity(
        value=s1y.value * (case.geometry.n_blt_web_y - 1) * t_plt_web.value,
        unit=area_unit_plt_v3,
    )
    ant_plt_v3_web = Quantity(
        value=agt_plt_v3_web.value
        - (case.geometry.n_blt_web_y - 1) * t_plt_web.value * (dh_web.value + hole_add_block_plt1),
        unit=area_unit_plt_v3,
    )
    ubs_plt_v3_web = float(case.geometry.Ubs_web_v3_vg)
    phi_rn2_plt_v3_web, block_shear_plt1_v3_inter = compute_block_shear_strength_j45(
        material_fu=fu_plt_web,
        material_fy=fy_plt_web,
        net_shear_area_anv=anv_plt_v3_web,
        gross_shear_area_agv=agv_plt_v3_web,
        net_tension_area_ant=ant_plt_v3_web,
        ubs_factor=ubs_plt_v3_web,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn2_1_plt_v3_web = block_shear_plt1_v3_inter.get("rn1")
    rn2_2_plt_v3_web = block_shear_plt1_v3_inter.get("rn2")
    rn2_plt_v3_web = block_shear_plt1_v3_inter.get("rn")
    ru2_plt_v3_web = Quantity(
        value=case.loads.Pu_sp.value * case.loads.alpha_Pu_web,
        unit=case.loads.Pu_sp.unit,
    )
    dcr2_plt_v3_web: float | None = None
    result2_plt_v3_web = "FAIL"
    if (
        isinstance(ru2_plt_v3_web, Quantity)
        and isinstance(phi_rn2_plt_v3_web, Quantity)
        and ru2_plt_v3_web.unit == phi_rn2_plt_v3_web.unit
        and abs(phi_rn2_plt_v3_web.value) > 1e-12
    ):
        dcr2_plt_v3_web = abs(ru2_plt_v3_web.value) / phi_rn2_plt_v3_web.value
        result2_plt_v3_web = "PASS" if dcr2_plt_v3_web <= 1.0 else "FAIL"
    # Plate 1 tension yielding in v3 (AISC 360-22 J4.1(a), DRY function).
    phi_no_ductil_plt = 0.9
    agt_v3_plt_web_expr = (
        2.0 * s1x.value * (case.geometry.n_blt_web_x - 1) * math.sqrt(3.0) / 3.0
        + (case.geometry.n_blt_web_y - 1) * s1y.value
    )
    agt_v3_plt_web_len = min(hp1.value, agt_v3_plt_web_expr)
    agt_v3_plt_web = Quantity(
        value=agt_v3_plt_web_len * t_plt_web.value,
        unit=area_unit_plt_v3,
    )
    phi_rn3_plt_v3_web, tension_yielding_plt1_v3_inter = compute_element_tension_yielding_strength_j41a(
        material_fy=fy_plt_web,
        gross_tension_area_agt=agt_v3_plt_web,
        phi_n=phi_no_ductil_plt,
        unit_system=case.units_system,
    )
    rn3_plt_v3_web = tension_yielding_plt1_v3_inter.get("rn")
    ru3_plt_v3_web = Quantity(
        value=case.loads.alpha_Pu_web * case.loads.Pu_sp.value,
        unit=case.loads.Pu_sp.unit,
    )
    dcr3_plt_v3_web: float | None = None
    result3_plt_v3_web = "FAIL"
    if (
        isinstance(ru3_plt_v3_web, Quantity)
        and isinstance(phi_rn3_plt_v3_web, Quantity)
        and ru3_plt_v3_web.unit == phi_rn3_plt_v3_web.unit
        and abs(phi_rn3_plt_v3_web.value) > 1e-12
    ):
        dcr3_plt_v3_web = abs(ru3_plt_v3_web.value) / phi_rn3_plt_v3_web.value
        result3_plt_v3_web = "PASS" if dcr3_plt_v3_web <= 1.0 else "FAIL"
    # Plate 1 tension rupture in v3 (AISC 360-22 J4.1(b), DRY function).
    ant_v3_plt_web = Quantity(
        value=agt_v3_plt_web.value
        - case.geometry.n_blt_web_y * (dh_web.value + hole_add_block_plt1) * t_plt_web.value,
        unit=area_unit_plt_v3,
    )
    u_v3_plt_web = 1.0
    ae_v3_plt_web = Quantity(
        value=ant_v3_plt_web.value * u_v3_plt_web,
        unit=area_unit_plt_v3,
    )
    phi_rn4_plt_v3_web, tension_rupture_plt1_v3_inter = compute_element_tension_rupture_strength_j41b(
        material_fu=fu_plt_web,
        effective_net_area_ae=ae_v3_plt_web,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn4_plt_v3_web = tension_rupture_plt1_v3_inter.get("rn")
    ru4_plt_v3_web = Quantity(
        value=case.loads.alpha_Pu_web * case.loads.Pu_sp.value,
        unit=case.loads.Pu_sp.unit,
    )
    dcr4_plt_v3_web: float | None = None
    result4_plt_v3_web = "FAIL"
    if (
        isinstance(ru4_plt_v3_web, Quantity)
        and isinstance(phi_rn4_plt_v3_web, Quantity)
        and ru4_plt_v3_web.unit == phi_rn4_plt_v3_web.unit
        and abs(phi_rn4_plt_v3_web.value) > 1e-12
    ):
        dcr4_plt_v3_web = abs(ru4_plt_v3_web.value) / phi_rn4_plt_v3_web.value
        result4_plt_v3_web = "PASS" if dcr4_plt_v3_web <= 1.0 else "FAIL"
    # Plate 1 compression buckling under axial compression in web plate (DRY helper).
    if not (alpha.unit == le1_x1.unit == s1x.unit):
        raise ValueError("Incompatible units for ex_blt_web computation in splice flexural checks.")
    ex_blt_web = Quantity(
        value=alpha.value + 2.0 * le1_x1.value + (case.geometry.n_blt_web_x - 1) * s1x.value,
        unit=alpha.unit,
    )
    lp_plt_p3_minus_web = Quantity(
        value=min(alpha.value + 2.0 * le1_x1.value, s1x.value),
        unit=alpha.unit,
    )
    ey_blt_web = case.loads.e2_blt_web
    if ey_blt_web is None:
        ey_blt_web = Quantity(value=0.0, unit=ex_blt_web.unit)
    if ey_blt_web.unit != ex_blt_web.unit:
        raise ValueError("Incompatible units between ey_blt_web and ex_blt_web in splice flexural checks.")
    phi_no_ductil_flex = 0.9
    phi_rn1_plt_p3_minus_web: Quantity | None = None
    ru1_plt_p3_minus_web: Quantity | None = None
    dcr1_plt_p3_minus_web: float | None = None
    result1_plt_p3_minus_web = "FAIL"
    pminus_plt1_inter: dict[str, object] = {}
    ru1_p3_minus_value = case.loads.alpha_Pu_web * case.loads.Pu_sp.value if case.loads.Pu_sp.value < 0.0 else 0.0
    ru1_plt_p3_minus_web = Quantity(
        value=ru1_p3_minus_value,
        unit=case.loads.Pu_sp.unit,
    )
    try:
        pminus_plt1_inter = compute_plate_compression_buckling_strength(
            material_fy=fy_plt_web,
            plate_width_b1=hp1,
            plate_thickness_t=t_plt_web,
            unbraced_length_lp=lp_plt_p3_minus_web,
            plate_count_n=1,
            unit_system=case.units_system,
            phi=phi_no_ductil_flex,
            k_factor=0.65,
        )
    except ValueError:
        pminus_plt1_inter = {}
    phi_rn1_plt_p3_minus_web_q = pminus_plt1_inter.get("phi_rn")
    if isinstance(phi_rn1_plt_p3_minus_web_q, Quantity):
        phi_rn1_plt_p3_minus_web = phi_rn1_plt_p3_minus_web_q
    ru_for_dcr = ru1_plt_p3_minus_web
    if isinstance(ru_for_dcr, Quantity) and isinstance(phi_rn1_plt_p3_minus_web, Quantity):
        if ru_for_dcr.unit != phi_rn1_plt_p3_minus_web.unit:
            if ru_for_dcr.unit == "N" and phi_rn1_plt_p3_minus_web.unit == "kN":
                ru_for_dcr = Quantity(value=ru_for_dcr.value / 1000.0, unit="kN")
            elif ru_for_dcr.unit == "kN" and phi_rn1_plt_p3_minus_web.unit == "N":
                ru_for_dcr = Quantity(value=ru_for_dcr.value * 1000.0, unit="N")
            elif ru_for_dcr.unit == "lb" and phi_rn1_plt_p3_minus_web.unit == "kip":
                ru_for_dcr = Quantity(value=ru_for_dcr.value / 1000.0, unit="kip")
            elif ru_for_dcr.unit == "kip" and phi_rn1_plt_p3_minus_web.unit == "lb":
                ru_for_dcr = Quantity(value=ru_for_dcr.value * 1000.0, unit="lb")
        if ru_for_dcr.unit == phi_rn1_plt_p3_minus_web.unit and abs(phi_rn1_plt_p3_minus_web.value) > 1e-12:
            dcr1_plt_p3_minus_web = abs(ru_for_dcr.value) / phi_rn1_plt_p3_minus_web.value
            result1_plt_p3_minus_web = "PASS" if dcr1_plt_p3_minus_web <= 1.0 else "FAIL"

    # Plate 1 flexural yielding around axis 1 (AISC 360-22 F11.1).
    h_plt_web = hp1
    section_modulus_unit = "in3" if case.units_system == UnitSystem.US else "mm3"
    z_plt_m1_web = Quantity(
        value=t_plt_web.value * (h_plt_web.value ** 2) / 4.0,
        unit=section_modulus_unit,
    )
    s_plt_m1_web = Quantity(
        value=t_plt_web.value * (h_plt_web.value ** 2) / 6.0,
        unit=section_modulus_unit,
    )
    phi_rn1_plt_m1_web, flex_yield_plt1_inter = compute_rectangular_bar_flexural_yielding_strength_f111(
        material_fy=fy_plt_web,
        plastic_section_modulus_z=z_plt_m1_web,
        elastic_section_modulus_sx=s_plt_m1_web,
        phi_n=phi_no_ductil_flex,
        unit_system=case.units_system,
    )
    rn1_plt_m1_web = flex_yield_plt1_inter.get("mn")
    moment_unit = "kip-in" if case.units_system == UnitSystem.US else "kN-mm"
    vu2_base = case.loads.Vu2_sp.value if case.loads.Vu2_sp.unit == "kip" else case.loads.Vu2_sp.value
    pu_base = case.loads.Pu_sp.value if case.loads.Pu_sp.unit == "kip" else case.loads.Pu_sp.value
    if case.units_system == UnitSystem.SI and case.loads.Vu2_sp.unit == "N":
        vu2_base = case.loads.Vu2_sp.value / 1000.0
    if case.units_system == UnitSystem.SI and case.loads.Pu_sp.unit == "N":
        pu_base = case.loads.Pu_sp.value / 1000.0
    ru1_plt_m1_web = Quantity(
        value=vu2_base * ex_blt_web.value - case.loads.alpha_Pu_web * pu_base * ey_blt_web.value,
        unit=moment_unit,
    )
    dcr1_plt_m1_web: float | None = None
    result1_plt_m1_web = "FAIL"
    if (
        isinstance(phi_rn1_plt_m1_web, Quantity)
        and ru1_plt_m1_web.unit == phi_rn1_plt_m1_web.unit
        and abs(phi_rn1_plt_m1_web.value) > 1e-12
    ):
        dcr1_plt_m1_web = abs(ru1_plt_m1_web.value) / phi_rn1_plt_m1_web.value
        result1_plt_m1_web = "PASS" if dcr1_plt_m1_web <= 1.0 else "FAIL"
    # Plate 1 LTB around axis 1 (AISC 360-22 F11.2).
    lb_plt_m1_web = Quantity(
        value=max(2.0 * le1_x1.value + alpha.value, s1x.value),
        unit=le1_x1.unit,
    )
    my_base = fy_plt_web.value * s_plt_m1_web.value
    my_plt_m1_web = Quantity(
        value=my_base if case.units_system == UnitSystem.US else my_base / 1000.0,
        unit=moment_unit,
    )
    mp_plt_m1_web = flex_yield_plt1_inter.get("mn_mp")
    if not isinstance(mp_plt_m1_web, Quantity):
        mp_plt_m1_web = Quantity(
            value=fy_plt_web.value * z_plt_m1_web.value if case.units_system == UnitSystem.US else (fy_plt_web.value * z_plt_m1_web.value) / 1000.0,
            unit=moment_unit,
        )
    cb_plt_m1_web = float(case.geometry.Cb_plt_m1_web)
    phi_rn2_plt_m1_web, ltb_plt1_inter = compute_rectangular_bar_ltb_strength_f112(
        material_fy=fy_plt_web,
        modulus_e=e_plt_web,
        unbraced_length_lb=lb_plt_m1_web,
        bar_depth_d=h_plt_web,
        bar_thickness_t=t_plt_web,
        elastic_section_modulus_sx=s_plt_m1_web,
        plastic_moment_mp=mp_plt_m1_web,
        cb_factor=cb_plt_m1_web,
        phi_n=phi_no_ductil_flex,
        unit_system=case.units_system,
    )
    rn2_plt_m1_web = ltb_plt1_inter.get("mn")
    ru2_plt_m1_web = Quantity(
        value=vu2_base * ex_blt_web.value - case.loads.alpha_Pu_web * pu_base * ey_blt_web.value,
        unit=moment_unit,
    )
    dcr2_plt_m1_web: float | None = None
    result2_plt_m1_web = "FAIL"
    if (
        isinstance(phi_rn2_plt_m1_web, Quantity)
        and ru2_plt_m1_web.unit == phi_rn2_plt_m1_web.unit
        and abs(phi_rn2_plt_m1_web.value) > 1e-12
    ):
        dcr2_plt_m1_web = abs(ru2_plt_m1_web.value) / phi_rn2_plt_m1_web.value
        result2_plt_m1_web = "PASS" if dcr2_plt_m1_web <= 1.0 else "FAIL"
    # Plate 1 net-section flexural rupture around axis 1 (AISC 360-22 J5.5).
    n_plt_web_y = case.geometry.n_blt_web_y
    d_prime_add = 1.8 if dh_web.unit == "mm" else (1.8 / 25.4)
    d_prime_plt_m1_web = Quantity(
        value=dh_web.value + d_prime_add,
        unit=dh_web.unit,
    )
    phi_rn3_plt_m1_web, flex_rupture_plt1_inter = compute_rectangular_bar_net_flexural_rupture_strength_j55(
        material_fy=fu_plt_web,
        plate_thickness_tp=t_plt_web,
        plate_height_h=h_plt_web,
        hole_plus_allowance_d_prime=d_prime_plt_m1_web,
        edge_e1=le1_y1,
        edge_e2=le1_y2,
        spacing_s=s1y,
        bolt_rows_n=n_plt_web_y,
        phi_n=phi_fragil_web,
        unit_system=case.units_system,
    )
    rn3_plt_m1_web = flex_rupture_plt1_inter.get("rn")
    z_net_plt_m1_web = flex_rupture_plt1_inter.get("z_net")
    h_calc_plt_m1_web = flex_rupture_plt1_inter.get("h_calc")
    sum_abs_plt_m1_web = flex_rupture_plt1_inter.get("sum_abs")
    ru3_plt_m1_web = Quantity(
        value=vu2_base * ex_blt_web.value - case.loads.alpha_Pu_web * pu_base * ey_blt_web.value,
        unit=moment_unit,
    )
    dcr3_plt_m1_web: float | None = None
    result3_plt_m1_web = "FAIL"
    if (
        isinstance(phi_rn3_plt_m1_web, Quantity)
        and ru3_plt_m1_web.unit == phi_rn3_plt_m1_web.unit
        and abs(phi_rn3_plt_m1_web.value) > 1e-12
    ):
        dcr3_plt_m1_web = abs(ru3_plt_m1_web.value) / phi_rn3_plt_m1_web.value
        result3_plt_m1_web = "PASS" if dcr3_plt_m1_web <= 1.0 else "FAIL"

    # Plate 1 shear yielding in v2 (AISC 360-22 J4.2(a), DRY function).
    phi_ductil_plt = 1.0
    agv5_plt_v2_web = Quantity(
        value=(
            s1y.value * (case.geometry.n_blt_web_y - 1)
            + le1_y1.value
            + le1_y2.value
        ) * t_plt_web.value,
        unit=area_unit,
    )
    phi_rn5_plt_v2_web, shear_yielding_plt1_inter = compute_element_shear_yielding_strength_j42a(
        material_fy=fy_plt_web,
        gross_shear_area_agv=agv5_plt_v2_web,
        phi_n=phi_ductil_plt,
        unit_system=case.units_system,
    )
    rn5_plt_v2_web = shear_yielding_plt1_inter.get("rn")
    ru5_plt_v2_web = case.loads.Vu2_sp
    dcr5_plt_v2_web: float | None = None
    result5_plt_v2_web = "FAIL"
    if (
        isinstance(ru5_plt_v2_web, Quantity)
        and isinstance(phi_rn5_plt_v2_web, Quantity)
        and ru5_plt_v2_web.unit == phi_rn5_plt_v2_web.unit
        and abs(phi_rn5_plt_v2_web.value) > 1e-12
    ):
        dcr5_plt_v2_web = abs(ru5_plt_v2_web.value) / phi_rn5_plt_v2_web.value
        result5_plt_v2_web = "PASS" if dcr5_plt_v2_web <= 1.0 else "FAIL"

    def _max_dcr(*values: float | None) -> float:
        valid = [float(v) for v in values if isinstance(v, (int, float))]
        if not valid:
            return 0.0
        return max(valid)

    dcr_plt_v2_web = _max_dcr(
        dcr2_plt_v2_web,
        dcr4_plt_v2_web,
        dcr5_plt_v2_web,
        dcr6_plt_v2_web,
    )
    dcr_plt_v3_web = _max_dcr(
        dcr2_plt_v3_web,
        dcr3_plt_v3_web,
        dcr4_plt_v3_web,
    )
    dcr_plt_p3_minus_web = _max_dcr(dcr1_plt_p3_minus_web)
    dcr_plt_m1_web = _max_dcr(
        dcr1_plt_m1_web,
        dcr2_plt_m1_web,
        dcr3_plt_m1_web,
    )
    fcomb_plt1_inter = compute_plate_combined_force_interaction(
        dcr_plt_m1_web=dcr_plt_m1_web,
        dcr_plt_v3_web=dcr_plt_v3_web,
        dcr_plt_v2_web=dcr_plt_v2_web,
        dcr_plt_p3_minus_web=dcr_plt_p3_minus_web,
    )
    dcr_case_1_plt_fcomb_web = float(fcomb_plt1_inter.get("dcr_case_1", 0.0))
    dcr_case_2_plt_fcomb_web = float(fcomb_plt1_inter.get("dcr_case_2", 0.0))
    dcr_plt_fcomb_web = float(fcomb_plt1_inter.get("dcr_fcomb", 0.0))
    fcomb_controlling_case = str(fcomb_plt1_inter.get("controlling_case", "Caso 1"))
    result_plt_fcomb_web = "PASS" if bool(fcomb_plt1_inter.get("passes", False)) else "FAIL"

    # J3.6 max spacing / edge distance (DRY common functions)
    t_web = Quantity(
        value=min(case.geometry.t_plt_web.value, tw_catalog.value),
        unit=case.geometry.t_plt_web.unit,
    )
    t_plt_flange_input = case.geometry.t_plt_flange
    t_flange = Quantity(
        value=min(t_plt_flange_input.value, tf_catalog.value),
        unit=t_plt_flange_input.unit,
    )
    t_plt_flange = Quantity(
        value=t_plt_flange_input.value,
        unit=t_plt_flange_input.unit,
    )
    web_surface = case.geometry.cond_sup_plt_web or "unpainted"
    web_atm = case.geometry.cond_amb_plt_web or "non_corrosive"
    flange_surface = case.geometry.cond_sup_plt_flange or "unpainted"
    flange_atm = case.geometry.cond_amb_plt_flange or "non_corrosive"
    is_web_corrosive_unpainted = web_atm == "corrosive" and web_surface == "unpainted"
    is_flange_corrosive_unpainted = flange_atm == "corrosive" and flange_surface == "unpainted"
    smax_web, _smax_web_meta = compute_maximum_bolt_spacing_j36(
        thinner_part_thickness=t_web,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_web_corrosive_unpainted,
    )
    smax_plt_web, _smax_plt_web_meta = compute_maximum_bolt_spacing_j36(
        thinner_part_thickness=case.geometry.t_plt_web,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_web_corrosive_unpainted,
    )
    smax_flange, _smax_flange_meta = compute_maximum_bolt_spacing_j36(
        thinner_part_thickness=t_flange,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_flange_corrosive_unpainted,
    )
    smax_plt_flange, _smax_plt_flange_meta = compute_maximum_bolt_spacing_j36(
        thinner_part_thickness=t_plt_flange,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_flange_corrosive_unpainted,
    )
    lemax_web = compute_max_spacing_and_edge_distance_limits_j36(
        thinner_part_thickness=t_web,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_web_corrosive_unpainted,
    )["max_edge_distance_active"]
    lemax_plt_web = compute_max_spacing_and_edge_distance_limits_j36(
        thinner_part_thickness=case.geometry.t_plt_web,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_web_corrosive_unpainted,
    )["max_edge_distance_active"]
    lemax_flange = compute_max_spacing_and_edge_distance_limits_j36(
        thinner_part_thickness=t_flange,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_flange_corrosive_unpainted,
    )["max_edge_distance_active"]
    lemax_plt_flange = compute_max_spacing_and_edge_distance_limits_j36(
        thinner_part_thickness=t_plt_flange,
        unit_system=case.units_system,
        is_unpainted_weathering_exposed=is_flange_corrosive_unpainted,
    )["max_edge_distance_active"]
    if (
        not isinstance(lemax_web, Quantity)
        or not isinstance(lemax_plt_web, Quantity)
        or not isinstance(lemax_plt_flange, Quantity)
        or not isinstance(lemax_flange, Quantity)
    ):
        raise ValueError("Unable to resolve J3.6 max edge distances for splice detailing.")

    applies_p_plt_flange_spacing = case.geometry.n_blt_flange_x >= 2
    applies_g_plt_flange_spacing = case.geometry.n_blt_flange_z >= 2
    applies_g_blt_flange_spacing = case.geometry.n_blt_flange_z >= 2

    c1_web = bolt_web.get("c1_table_715")
    c1_flange = bolt_flange.get("c1_table_715")
    c3_type_selected = str(case.geometry.c3_clearance_type).strip().lower()
    c3_key = "c3_clipped_table_715" if c3_type_selected == "clipped" else "c3_circular_table_715"
    c3_web = bolt_web.get(c3_key)
    c3_flange = bolt_flange.get(c3_key)
    if not isinstance(c1_web, Quantity) or not isinstance(c3_web, Quantity):
        raise ValueError("Unable to resolve C1/C3 constructibility values for web bolts (Table 7-15).")
    if not isinstance(c1_flange, Quantity) or not isinstance(c3_flange, Quantity):
        raise ValueError("Unable to resolve C1/C3 constructibility values for flange bolts (Table 7-15).")

    two_c1_web = Quantity(value=2.0 * c1_web.value, unit=c1_web.unit)
    two_c1_flange = Quantity(value=2.0 * c1_flange.value, unit=c1_flange.unit)
    g_blt_web_min_combined = Quantity(value=max(two_c1_web.value, s_min_web.value), unit=s_min_web.unit)
    p_blt_web_min_combined = Quantity(value=max(two_c1_web.value, s_min_web.value), unit=s_min_web.unit)
    p_blt_flange_min_combined = Quantity(value=max(two_c1_flange.value, s_min_flange.value), unit=s_min_flange.unit)
    g1_blt_flange_min_combined = Quantity(value=max(two_c1_flange.value, s_min_flange.value), unit=s_min_flange.unit)
    le_blt_web_x1_min_combined = Quantity(value=max(le_min_web.value, c1_web.value), unit=le_min_web.unit)
    le_blt_web_y31_min_combined = Quantity(value=max(le_min_web.value, c1_web.value), unit=le_min_web.unit)
    le_blt_flange_x1_min_combined = Quantity(value=max(le_min_flange.value, c1_flange.value), unit=le_min_flange.unit)
    le_blt_flange_z1_min_combined = Quantity(value=max(le_min_flange.value, c1_flange.value), unit=le_min_flange.unit)
    le_blt_flange_z4_min_combined = Quantity(value=max(le_min_flange.value, c1_flange.value), unit=le_min_flange.unit)
    g_blt_flange_min_constructive = Quantity(
        value=max(s_min_flange.value, two_c1_flange.value),
        unit=s_min_flange.unit,
    )

    construct_clause = "AISC 360-22 J3.6 y Table 7-15 Entering and Tightening Clearance, in."
    construct_clause_with_staggered = (
        "AISC 360-22 J3.6 y Table 7-15 Entering and Tightening Clearance, in. "
        "(Aligned + Staggered Bolts)"
    )
    combined_spacing_clause = "AISC 360-22 J3.3, J3.6 y Table 7-15 Entering and Tightening Clearance, in."
    combined_edge_clause = "AISC 360-22 Tabla J3.4, J3.6 y Table 7-15 Entering and Tightening Clearance, in."
    construct_source = "AISC 360-22 + Steel Construction Manual AISC 16th edition 2023"
    c1_governing = Quantity(value=max(c1_web.value, c1_flange.value), unit=c1_web.unit)
    f_blt_flange_check_row: dict[str, object]
    if f_blt_flange is None:
        f_blt_flange_check_row = {
            "scope": "viga",
            "description": "Despeje horizontal F_blt_flange y separacion escalonada minima entre pernos",
            "calculated_symbol": "F_blt_flange",
            "limit_symbol": "C1/P",
            "comparison": "custom",
            "comparison_text": ">=",
            "calculated": {"value": 0.0, "unit": c1_governing.unit},
            "limit": c1_governing.model_dump(),
            "clause": construct_clause_with_staggered,
            "source_document": construct_source,
            "verification_override": "No se pudo calcular F_blt_flange por incompatibilidad de unidades.",
            "result": "FAIL",
        }
    elif f_blt_flange.value >= c1_governing.value:
        f_blt_flange_check_row = {
            "scope": "viga",
            "description": "Despeje horizontal F_blt_flange y separacion escalonada minima entre pernos",
            "calculated_symbol": "F_blt_flange",
            "limit_symbol": "C1_max",
            "comparison": "custom",
            "comparison_text": ">=",
            "calculated": f_blt_flange.model_dump(),
            "limit": c1_governing.model_dump(),
            "clause": construct_clause_with_staggered,
            "source_document": construct_source,
            "verification_override": (
                f"F_blt_flange >= C1_max; {f_blt_flange.value:.2f} {f_blt_flange.unit} >= "
                f"{c1_governing.value:.2f} {c1_governing.unit}"
            ),
            "result": "PASS",
        }
    else:
        pair_diffs: list[tuple[int, int, Quantity]] = []
        for web_item in xj_blt_web_values:
            xj_raw = web_item.get("x")
            if not isinstance(xj_raw, dict):
                continue
            j_idx = int(web_item.get("j", 0))
            for flange_item in xk_blt_flange_values:
                xk_raw = flange_item.get("x")
                if not isinstance(xk_raw, dict):
                    continue
                k_idx = int(flange_item.get("k", 0))
                if xj_raw.get("unit") != xk_raw.get("unit"):
                    continue
                qdiff = Quantity(
                    value=abs(float(xj_raw.get("value", 0.0)) - float(xk_raw.get("value", 0.0))),
                    unit=str(xj_raw.get("unit")),
                )
                pair_diffs.append((j_idx, k_idx, qdiff))
        if pair_diffs:
            min_pair = min(pair_diffs, key=lambda item: item[2].value)
            pmin_blt = min_pair[2]
            p_lookup = get_minimum_staggered_pitch_from_f(
                f_clearance=f_blt_flange,
                unit_system=case.units_system,
            )
            p_required = p_lookup["p_min"]
            if not isinstance(p_required, Quantity):
                raise ValueError("Unable to resolve staggered minimum pitch from sheet F_Perno.")
            stagger_pass = (pmin_blt.value >= p_required.value) if pmin_blt.unit == p_required.unit else False
            diff_txt = ", ".join(
                f"|x_{j}-x_{k}|={q.value:.2f} {q.unit}" for j, k, q in pair_diffs
            )
            f_blt_flange_check_row = {
                "scope": "viga",
                "description": "Despeje horizontal F_blt_flange y separacion escalonada minima entre pernos",
                "calculated_symbol": "Pmin_blt",
                "limit_symbol": "P",
                "comparison": "custom",
                "comparison_text": ">=",
                "calculated": pmin_blt.model_dump(),
                "limit": p_required.model_dump(),
                "clause": construct_clause_with_staggered,
                "source_document": construct_source,
                "verification_override": (
                    f"F_blt_flange < C1_max; {f_blt_flange.value:.2f} {f_blt_flange.unit} < "
                    f"{c1_governing.value:.2f} {c1_governing.unit}; "
                    f"Pmin_blt = min{{|x_j_blt_web - x_k_blt_flange|}} = {pmin_blt.value:.2f} {pmin_blt.unit}; "
                    f"Pmin_blt >= P; {pmin_blt.value:.2f} {pmin_blt.unit} >= {p_required.value:.2f} {p_required.unit}; "
                    f"lista={diff_txt}"
                ),
                "result": "PASS" if stagger_pass else "FAIL",
            }
        else:
            f_blt_flange_check_row = {
                "scope": "viga",
                "description": "Despeje horizontal F_blt_flange y separacion escalonada minima entre pernos",
                "calculated_symbol": "Pmin_blt",
                "limit_symbol": "P",
                "comparison": "custom",
                "comparison_text": ">=",
                "calculated": {"value": 0.0, "unit": f_blt_flange.unit},
                "limit": {"value": 0.0, "unit": f_blt_flange.unit},
                "clause": construct_clause_with_staggered,
                "source_document": construct_source,
                "verification_override": "No se pudo construir lista de distancias |x_j_blt_web - x_k_blt_flange|.",
                "result": "FAIL",
            }

    rows = [
        _row(
            scope="pernos_1",
            description="Separacion minima entre pernos del alma en direccion X",
            calculated_symbol="g_blt_web",
            limit_symbol="max {2*C1, Smin}",
            comparison_text=">=",
            calculated=s1x.model_dump(),
            limit=g_blt_web_min_combined.model_dump(),
            clause=combined_spacing_clause,
            source_document=construct_source,
            passed=s1x.value >= g_blt_web_min_combined.value,
        ),
        _row(
            scope="pernos_1",
            description="Separacion maxima entre pernos del alma en direccion X",
            calculated_symbol="g_blt_web",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s1x.model_dump(),
            limit=smax_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=s1x.value <= smax_web.value,
        ),
        _row(
            scope="platina_1",
            description="Separacion minima entre pernos de platina de alma en direccion X",
            calculated_symbol="g_plt_web",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s1x.model_dump(),
            limit=s_min_web.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s1x.value >= s_min_web.value,
        ),
        _row(
            scope="platina_1",
            description="Separacion maxima entre pernos de platina de alma en direccion X",
            calculated_symbol="g_plt_web",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s1x.model_dump(),
            limit=smax_plt_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=s1x.value <= smax_plt_web.value,
        ),
        _row(
            scope="platina_1",
            description="Distancia minima a borde de platina de alma Le_plt_web_x2 para agujero estandar",
            calculated_symbol="Le_plt_web_x2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_x2.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_x2.value >= le_min_web.value,
        ),
        _row(
            scope="platina_1",
            description="Distancia maxima a borde de platina de alma Le_plt_web_x2",
            calculated_symbol="Le_plt_web_x2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_x2.model_dump(),
            limit=lemax_plt_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le1_x2.value <= lemax_plt_web.value,
        ),
        _row(
            scope="platina_1",
            description="Separacion minima entre pernos de platina de alma en direccion Z",
            calculated_symbol="p_plt_web",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s1y.model_dump(),
            limit=s_min_web.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s1y.value >= s_min_web.value,
        ),
        _row(
            scope="platina_1",
            description="Separacion maxima entre pernos de platina de alma en direccion Z",
            calculated_symbol="p_plt_web",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s1y.model_dump(),
            limit=smax_plt_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=s1y.value <= smax_plt_web.value,
        ),
        _row(
            scope="platina_1",
            description="Distancia minima a borde de platina de alma Le_plt_web_y1 para agujero estandar",
            calculated_symbol="Le_plt_web_y1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_y1.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_y1.value >= le_min_web.value,
        ),
        _row(
            scope="platina_1",
            description="Distancia maxima a borde de platina de alma Le_plt_web_y1",
            calculated_symbol="Le_plt_web_y1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_y1.model_dump(),
            limit=lemax_plt_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le1_y1.value <= lemax_plt_web.value,
        ),
        _row(
            scope="platina_1",
            description="Distancia minima a borde de platina de alma Le_plt_web_y2 para agujero estandar",
            calculated_symbol="Le_plt_web_y2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_y2.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_y2.value >= le_min_web.value,
        ),
        _row(
            scope="platina_1",
            description="Distancia maxima a borde de platina de alma Le_plt_web_y2",
            calculated_symbol="Le_plt_web_y2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_y2.model_dump(),
            limit=lemax_plt_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le1_y2.value <= lemax_plt_web.value,
        ),
        _row(
            scope="pernos_1",
            description="Separacion minima entre pernos del alma en direccion Z",
            calculated_symbol="p_blt_web",
            limit_symbol="max {2*C1, Smin}",
            comparison_text=">=",
            calculated=s1y.model_dump(),
            limit=p_blt_web_min_combined.model_dump(),
            clause=combined_spacing_clause,
            source_document=construct_source,
            passed=s1y.value >= p_blt_web_min_combined.value,
        ),
        _row(
            scope="pernos_1",
            description="Separacion maxima entre pernos del alma en direccion Z",
            calculated_symbol="p_blt_web",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s1y.model_dump(),
            limit=smax_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=s1y.value <= smax_web.value,
        ),
        _row(
            scope="pernos_2",
            description="Separacion minima entre pernos del ala en direccion X",
            calculated_symbol="p_blt_flange",
            limit_symbol="max {2*C1, Smin}",
            comparison_text=">=",
            calculated=s2x.model_dump(),
            limit=p_blt_flange_min_combined.model_dump(),
            clause=combined_spacing_clause,
            source_document=construct_source,
            passed=s2x.value >= p_blt_flange_min_combined.value,
        ),
        _row(
            scope="pernos_2",
            description="Separacion maxima entre pernos del ala en direccion X",
            calculated_symbol="p_blt_flange",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s2x.model_dump(),
            limit=smax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=s2x.value <= smax_flange.value,
        ),
        _row(
            scope="platina_2",
            description="Separacion minima entre pernos de platina de ala en direccion X",
            calculated_symbol="p_plt_flange",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s2x.model_dump(),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=(s2x.value >= s_min_flange.value) if applies_p_plt_flange_spacing else True,
        ),
        _row(
            scope="platina_2",
            description="Separacion maxima entre pernos de platina de ala en direccion X",
            calculated_symbol="p_plt_flange",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s2x.model_dump(),
            limit=smax_plt_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(s2x.value <= smax_plt_flange.value) if applies_p_plt_flange_spacing else True,
        ),
        _row(
            scope="platina_2",
            description="Distancia minima a borde de platina de ala Le_plt_flange_x2 para agujero estandar",
            calculated_symbol="Le_plt_flange_x2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_x2.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_x2.value >= le_min_flange.value,
        ),
        _row(
            scope="platina_2",
            description="Distancia maxima a borde de platina de ala Le_plt_flange_x2",
            calculated_symbol="Le_plt_flange_x2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_x2.model_dump(),
            limit=lemax_plt_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le2_x2.value <= lemax_plt_flange.value,
        ),
        _row(
            scope="platina_2",
            description="Separacion minima entre pernos de platina de ala en direccion Z",
            calculated_symbol="g_plt_flange",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s2z1.model_dump(),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=(s2z1.value >= s_min_flange.value) if applies_g_plt_flange_spacing else True,
        ),
        _row(
            scope="platina_2",
            description="Separacion maxima entre pernos de platina de ala en direccion Z",
            calculated_symbol="g_plt_flange",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s2z1.model_dump(),
            limit=smax_plt_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(s2z1.value <= smax_plt_flange.value) if applies_g_plt_flange_spacing else True,
        ),
        _row(
            scope="platina_2",
            description="Distancia minima a borde de platina de ala Le_plt_flange_z1 para agujero estandar",
            calculated_symbol="Le_plt_flange_z1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z1.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_z1.value >= le_min_flange.value,
        ),
        _row(
            scope="platina_2",
            description="Distancia maxima a borde de platina de ala Le_plt_flange_z1",
            calculated_symbol="Le_plt_flange_z1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z1.model_dump(),
            limit=lemax_plt_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le2_z1.value <= lemax_plt_flange.value,
        ),
        _row(
            scope="platina_2",
            description="Distancia minima a borde de platina de ala Le_plt_flange_z2 para agujero estandar",
            calculated_symbol="Le_plt_flange_z2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z2.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_z2.value >= le_min_flange.value,
        ),
        _row(
            scope="platina_2",
            description="Distancia maxima a borde de platina de ala Le_plt_flange_z2",
            calculated_symbol="Le_plt_flange_z2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z2.model_dump(),
            limit=lemax_plt_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le2_z2.value <= lemax_plt_flange.value,
        ),
        _row(
            scope="platina_2",
            description="Separacion minima entre pernos de platina de ala en direccion Z entre filas internas",
            calculated_symbol="g1_plt_flange",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=(
                g1_blt_flange.model_dump()
                if g1_blt_flange is not None
                else {"value": 0.0, "unit": bf_catalog.unit}
            ),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=(g1_blt_flange is not None and g1_blt_flange.value >= s_min_flange.value),
        ),
        _row(
            scope="platina_2",
            description="Separacion maxima entre pernos de platina de ala en direccion Z entre filas internas",
            calculated_symbol="g1_plt_flange",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=(
                g1_blt_flange.model_dump()
                if g1_blt_flange is not None
                else {"value": 0.0, "unit": bf_catalog.unit}
            ),
            limit=smax_plt_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(g1_blt_flange is not None and g1_blt_flange.value <= smax_plt_flange.value),
        ),
        _row(
            scope="pernos_2",
            description="Separacion minima entre pernos del ala en direccion Z",
            calculated_symbol="g_blt_flange",
            limit_symbol="max {2*C1, Smin}",
            comparison_text=">=",
            calculated=s2z1.model_dump(),
            limit=g_blt_flange_min_constructive.model_dump(),
            clause=combined_spacing_clause,
            source_document=construct_source,
            passed=(s2z1.value >= g_blt_flange_min_constructive.value) if applies_g_blt_flange_spacing else True,
        ),
        _row(
            scope="pernos_2",
            description="Separacion maxima entre pernos del ala en direccion Z",
            calculated_symbol="g_blt_flange",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s2z1.model_dump(),
            limit=smax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(s2z1.value <= smax_flange.value) if applies_g_blt_flange_spacing else True,
        ),
        _row(
            scope="viga",
            description="Distancia minima a borde Le_blt_web_x1 para agujero estandar",
            calculated_symbol="Le_blt_web_x1",
            limit_symbol="max {Le_min, C1}",
            comparison_text=">=",
            calculated=le1_x1.model_dump(),
            limit=le_blt_web_x1_min_combined.model_dump(),
            clause=combined_edge_clause,
            source_document=construct_source,
            passed=le1_x1.value >= le_blt_web_x1_min_combined.value,
        ),
        _row(
            scope="viga",
            description="Distancia maxima a borde Le_blt_web_x1",
            calculated_symbol="Le_blt_web_x1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_x1.model_dump(),
            limit=lemax_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le1_x1.value <= lemax_web.value,
        ),
        _row(
            scope="pernos_1",
            description="Distancia minima a borde Le_blt_web_x2 para agujero estandar",
            calculated_symbol="Le_blt_web_x2",
            limit_symbol=le1_min_limit_symbol,
            comparison_text=">=",
            calculated=le1_x2.model_dump(),
            limit=le1_min_limit.model_dump(),
            clause=le1_min_clause,
            passed=le1_x2.value >= le1_min_limit.value,
        ),
        _row(
            scope="pernos_1",
            description="Distancia minima a borde Le_blt_web_y1 para agujero estandar",
            calculated_symbol="Le_blt_web_y1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_y1.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_y1.value >= le_min_web.value,
        ),
        _row(
            scope="pernos_1",
            description="Distancia minima a borde Le_blt_web_y2 para agujero estandar",
            calculated_symbol="Le_blt_web_y2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_y2.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_y2.value >= le_min_web.value,
        ),
        _row(
            scope="viga",
            description="Distancia minima a borde Le_blt_web_y3.1 para agujero estandar",
            calculated_symbol="Le_blt_web_y3.1",
            limit_symbol="max {Le_min, C1}",
            comparison_text=">=",
            calculated=le1_y3_1.model_dump() if le1_y3_1 is not None else {"value": 0.0, "unit": le1_y3.unit},
            limit=le_blt_web_y31_min_combined.model_dump(),
            clause=combined_edge_clause,
            source_document=construct_source,
            passed=(le1_y3_1 is not None and le1_y3_1.value >= le_blt_web_y31_min_combined.value),
        ),
        _row(
            scope="viga",
            description="Distancia maxima a borde Le_blt_web_y3.1",
            calculated_symbol="Le_blt_web_y3.1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_y3_1.model_dump() if le1_y3_1 is not None else {"value": 0.0, "unit": le1_y3.unit},
            limit=lemax_web.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(le1_y3_1 is not None and le1_y3_1.value <= lemax_web.value),
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_x1 para agujero estandar",
            calculated_symbol="Le_blt_flange_x1",
            limit_symbol="max {Le_min, C1}",
            comparison_text=">=",
            calculated=le2_x1.model_dump(),
            limit=le_blt_flange_x1_min_combined.model_dump(),
            clause=combined_edge_clause,
            source_document=construct_source,
            passed=le2_x1.value >= le_blt_flange_x1_min_combined.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le_blt_flange_x1",
            calculated_symbol="Le_blt_flange_x1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_x1.model_dump(),
            limit=lemax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le2_x1.value <= lemax_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_x2 para agujero estandar",
            calculated_symbol="Le_blt_flange_x2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_x2.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_x2.value >= le_min_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_z1 para agujero estandar",
            calculated_symbol="Le_blt_flange_z1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z1.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_z1.value >= le_min_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_z2 para agujero estandar",
            calculated_symbol="Le_blt_flange_z2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z2.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_z2.value >= le_min_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_z1 para agujero estandar",
            calculated_symbol="Le_blt_flange_z1",
            limit_symbol="max {Le_min, C1}",
            comparison_text=">=",
            calculated=le2_z1.model_dump(),
            limit=le_blt_flange_z1_min_combined.model_dump(),
            clause=combined_edge_clause,
            source_document=construct_source,
            passed=le2_z1.value >= le_blt_flange_z1_min_combined.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le_blt_flange_z1",
            calculated_symbol="Le_blt_flange_z1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z1.model_dump(),
            limit=lemax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le2_z1.value <= lemax_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_z4 para agujero estandar",
            calculated_symbol="Le_blt_flange_z4",
            limit_symbol="max {Le_min, C1}",
            comparison_text=">=",
            calculated=le2_z4.model_dump() if le2_z4 is not None else {"value": 0.0, "unit": le2_z1.unit},
            limit=le_blt_flange_z4_min_combined.model_dump(),
            clause=combined_edge_clause,
            source_document=construct_source,
            passed=(le2_z4 is not None and le2_z4.value >= le_blt_flange_z4_min_combined.value),
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le_blt_flange_z4",
            calculated_symbol="Le_blt_flange_z4",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z4.model_dump() if le2_z4 is not None else {"value": 0.0, "unit": le2_z1.unit},
            limit=lemax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(le2_z4 is not None and le2_z4.value <= lemax_flange.value),
        ),
        _row(
            scope="pernos_2",
            description="Separacion minima entre pernos del ala en direccion Z (g1)",
            calculated_symbol="g1_blt_flange",
            limit_symbol="max {2*C1, Smin}",
            comparison_text=">=",
            calculated=(
                g1_blt_flange.model_dump()
                if g1_blt_flange is not None
                else {"value": 0.0, "unit": s2z1.unit}
            ),
            limit=g1_blt_flange_min_combined.model_dump(),
            clause=combined_spacing_clause,
            source_document=construct_source,
            passed=(g1_blt_flange is not None and g1_blt_flange.value >= g1_blt_flange_min_combined.value),
        ),
        _row(
            scope="pernos_2",
            description="Separacion maxima entre pernos del ala en direccion Z (g1)",
            calculated_symbol="g1_blt_flange",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=(
                g1_blt_flange.model_dump()
                if g1_blt_flange is not None
                else {"value": 0.0, "unit": s2z1.unit}
            ),
            limit=smax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(g1_blt_flange is not None and g1_blt_flange.value <= smax_flange.value),
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_z4 por constructibilidad (C3)",
            calculated_symbol="Le_blt_flange_z4",
            limit_symbol="C3",
            comparison_text=">=",
            calculated=le2_z4.model_dump() if le2_z4 is not None else {"value": 0.0, "unit": le2_z1.unit},
            limit=c3_flange.model_dump(),
            clause=construct_clause,
            source_document=construct_source,
            passed=(le2_z4 is not None and le2_z4.value >= c3_flange.value),
        ),
        _row(
            scope="viga",
            description="Distancia minima a borde Le_blt_web_y3.1 por constructibilidad (C3)",
            calculated_symbol="Le_blt_web_y3.1",
            limit_symbol="C3",
            comparison_text=">=",
            calculated=le1_y3_1.model_dump() if le1_y3_1 is not None else {"value": 0.0, "unit": le1_y3.unit},
            limit=c3_web.model_dump(),
            clause=construct_clause,
            source_document=construct_source,
            passed=(le1_y3_1 is not None and le1_y3_1.value >= c3_web.value),
        ),
        f_blt_flange_check_row,
        _row(
            scope="platina_1",
            description="Altura de platina de alma no supera T_vg del catalogo",
            calculated_symbol="B_plt_web",
            limit_symbol="T_vg",
            comparison_text="<=",
            calculated=hp1.model_dump(),
            limit=t_catalog.model_dump(),
            clause="Criterio de detallado solicitado por usuario",
            passed=hp1.value <= t_catalog.value,
        ),
        _row(
            scope="platina_2",
            description="Ancho de platina de ala no supera bf_vg del catalogo",
            calculated_symbol="B_plt_flange",
            limit_symbol="bf_vg",
            comparison_text="<=",
            calculated=bp2.model_dump(),
            limit=bf_catalog.model_dump(),
            clause="Criterio de detallado solicitado por usuario",
            passed=bp2.value <= bf_catalog.value,
        ),
        _row(
            scope="viga",
            description="Distancia Le_blt_web_y3 no menor que kdes_vg del catalogo",
            calculated_symbol="Le_blt_web_y3",
            limit_symbol="kdes_vg",
            comparison_text=">=",
            calculated=le1_y3.model_dump(),
            limit=kdes_catalog.model_dump(),
            clause="Criterio solicitado por usuario + catalogo de secciones",
            passed=(
                (le1_y3.value >= kdes_catalog.value) if le1_y3.unit == kdes_catalog.unit else False
            ),
        ),
        _row(
            scope="viga",
            description="Factor de rezago de cortante 1 (U1) no mayor que 1",
            calculated_symbol="U1",
            limit_symbol="1.0",
            comparison_text="<=",
            calculated={"value": u1, "unit": "ratio"},
            limit={"value": 1.0, "unit": "ratio"},
            clause="Criterio solicitado por usuario",
            passed=u1 is not None and u1 <= 1.0,
        ),
        _row(
            scope="viga",
            description="Alma de la viga no es esbelta",
            calculated_symbol="h/tw",
            limit_symbol="5.7*sqrt(E_vg/Fy_vg)",
            comparison_text="<",
            calculated=h_over_tw_vg.model_dump(),
            limit=h_over_tw_limit.model_dump(),
            clause="AISC 360-22 (criterio solicitado por usuario)",
            passed=h_over_tw_vg.value < h_over_tw_limit.value,
        ),
    ]

    if not applies_p_plt_flange_spacing:
        for row_item in rows:
            if row_item.get("scope") == "platina_2" and row_item.get("calculated_symbol") == "p_plt_flange":
                row_item["result"] = "NOT_APPLICABLE"
                row_item["applicability"] = f"n_blt_flange_x >= 2; {case.geometry.n_blt_flange_x} >= 2"

    if not applies_g_plt_flange_spacing:
        for row_item in rows:
            if row_item.get("scope") == "platina_2" and row_item.get("calculated_symbol") == "g_plt_flange":
                row_item["result"] = "NOT_APPLICABLE"
                row_item["applicability"] = f"n_blt_flange_z >= 2; {case.geometry.n_blt_flange_z} >= 2"
    if not applies_g_blt_flange_spacing:
        for row_item in rows:
            if row_item.get("scope") == "pernos_2" and row_item.get("calculated_symbol") == "g_blt_flange":
                row_item["result"] = "NOT_APPLICABLE"
                row_item["applicability"] = f"n_blt_flange_z >= 2; {case.geometry.n_blt_flange_z} >= 2"

    if case.geometry.type_tight_blt_web in {"pretensioned", "slip_critical"}:
        tmin_web_kn = _minimum_bolt_pretension_kN(
            diameter_in=db_web_in,
            fabrication_standard=case.materials.std_blt_web,
        )
        rows.append(
            _row(
                scope="pernos_1",
                description="Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 1)",
                calculated_symbol="Tb,min,1",
                limit_symbol="Tabla J3.1",
                comparison_text="=",
                calculated={"value": tmin_web_kn, "unit": "kN"},
                limit={"value": tmin_web_kn, "unit": "kN"},
                clause="AISC 360-22 Tabla J3.1",
                passed=True,
            )
        )
    if case.geometry.type_tight_blt_flange in {"pretensioned", "slip_critical"}:
        tmin_flange_kn = _minimum_bolt_pretension_kN(
            diameter_in=db_flange_in,
            fabrication_standard=case.materials.std_blt_flange,
        )
        rows.append(
            _row(
                scope="pernos_2",
                description="Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 2)",
                calculated_symbol="Tb,min,2",
                limit_symbol="Tabla J3.1",
                comparison_text="=",
                calculated={"value": tmin_flange_kn, "unit": "kN"},
                limit={"value": tmin_flange_kn, "unit": "kN"},
                clause="AISC 360-22 Tabla J3.1",
                passed=True,
            )
        )

    passing_results = {"PASS", "NOT_APPLICABLE"}
    status = CheckStatus.PASS if all(row["result"] in passing_results for row in rows) else CheckStatus.FAIL

    tlvg = case.geometry.tol_L_vg
    le1_x1_prime = Quantity(value=le1_x1.value - tlvg.value, unit=le1_x1.unit) if le1_x1.unit == tlvg.unit else None

    memory = CalculationMemory(
        inputs={
            "shape_vg": case.sections.shape_vg,
            "db_blt_web": db_web.model_dump(),
            "db_blt_flange": db_flange.model_dump(),
            "g_blt_web": s1x.model_dump(),
            "p_blt_web": s1y.model_dump(),
            "p_blt_flange": s2x.model_dump(),
            "g_blt_flange": s2z1.model_dump(),
            "Le_blt_web_x1": le1_x1.model_dump(),
            "Le_blt_web_x2": le1_x2.model_dump(),
            "Le_blt_web_y1": le1_y1.model_dump(),
            "Le_blt_web_y2": le1_y2.model_dump(),
            "Le_blt_flange_x1": le2_x1.model_dump(),
            "Le_blt_flange_x2": le2_x2.model_dump(),
            "Le_blt_flange_z1": le2_z1.model_dump(),
            "Le_blt_flange_z2": le2_z2.model_dump(),
            "Le_blt_flange_z1": le2_z1.model_dump(),
            "T_vg": t_catalog.model_dump(),
            "bf_vg": bf_catalog.model_dump(),
        },
        intermediates={
            "step_1_limits": rows,
            "step_1_notes": [
                {
                    "id": "bbmb_splice.step1.geometry_note",
                    "scope": "viga",
                    "description": "Parametros geometricos base",
                    "clause": "Criterio solicitado por usuario",
                    "shape_vg_var": "shape_vg",
                    "shape_vg": case.sections.shape_vg,
                    "steel_vg_var": "steel_vg",
                    "steel_vg": case.materials.steel_vg,
                    "cond_sup_vg_var": "cond_sup_vg",
                    "cond_sup_vg": case.geometry.cond_sup_vg,
                    "cond_amb_vg_var": "cond_amb_vg",
                    "cond_amb_vg": case.geometry.cond_amb_vg,
                    "c3_clearance_type_var": "c3_clearance_type",
                    "c3_clearance_type": case.geometry.c3_clearance_type,
                    "fy_vg_var": "Fy_vg",
                    "fy_vg": fy_vg.model_dump() if fy_vg is not None else None,
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump() if fu_vg is not None else None,
                    "e_vg_var": "E_vg",
                    "e_vg": e_vg.model_dump() if e_vg is not None else None,
                    "d_vg_var": "d_vg",
                    "d_vg": dvg_catalog.model_dump(),
                    "t_vg_var": "T_vg",
                    "t_vg": t_catalog.model_dump(),
                    "bf_vg_var": "bf_vg",
                    "bf_vg": bf_catalog.model_dump(),
                    "bfdet_vg_var": "bfdet_vg",
                    "bfdet_vg": bf_catalog.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "twdet_vg_var": "twdet_vg",
                    "twdet_vg": tw_catalog.model_dump(),
                    "tf_vg_var": "tf_vg",
                    "tf_vg": tf_catalog.model_dump(),
                    "tfdet_vg_var": "tfdet_vg",
                    "tfdet_vg": tf_catalog.model_dump(),
                    "kdes_vg_var": "kdes_vg",
                    "kdes_vg": kdes_catalog.model_dump(),
                    "kdet_vg_var": "kdet_vg",
                    "kdet_vg": kdes_catalog.model_dump(),
                    "k1_vg_var": "k1_vg",
                    "k1_vg": beam_props.get("k1").model_dump()
                    if isinstance(beam_props.get("k1"), Quantity)
                    else None,
                    "alpha_symbol": "gap_sp",
                    "alpha": alpha.model_dump(),
                    "beam_length_tolerance_var": "tol_L_vg",
                    "beam_length_tolerance": tlvg.model_dump(),
                    "beam_length_tolerance_ref": "AISC 303-22",
                    "n1x_var": "n_blt_web_x",
                    "n1x": case.geometry.n_blt_web_x,
                    "s1x_var": "g_blt_web",
                    "s1x": s1x.model_dump(),
                    "n1y_var": "n_blt_web_y",
                    "n1y": case.geometry.n_blt_web_y,
                    "s1y_var": "p_blt_web",
                    "s1y": s1y.model_dump(),
                    "type_hole_web_var": "type_hole_web",
                    "type_hole_web": case.geometry.type_hole_plt_web,
                    "le1x1_var": "Le_blt_web_x1",
                    "le1x1": le1_x1.model_dump(),
                    "xj_blt_web_var": "x_j_blt_web",
                    "xj_blt_web_formula": "x_j_blt_web = Le_blt_web_x1 + j*g_blt_web",
                    "xj_blt_web_j_range": "j = 0, 1, ..., n_blt_web_x - 1",
                    "xj_blt_web_values": xj_blt_web_values,
                    "le1x1_prime_var": "Le_blt_web_x1'",
                    "le1x1_prime_formula": "Le_blt_web_x1' = Le_blt_web_x1 - tol_L_vg",
                    "le1x1_prime": le1_x1_prime.model_dump() if le1_x1_prime is not None else None,
                    "dvg_var": "d_vg",
                    "dvg": dvg_catalog.model_dump(),
                    "le1y3_var": "Le_blt_web_y3",
                    "le1y3": le1_y3.model_dump(),
                    "le1y3_1_var": "Le_blt_web_y3.1",
                    "le1y3_1_formula": "Le_blt_web_y3.1 = Le_blt_web_y3 - kdet_vg",
                    "le1y3_1": le1_y3_1.model_dump() if le1_y3_1 is not None else None,
                    "le2z4_var": "Le_blt_flange_z4",
                    "le2z4_formula": "Le_blt_flange_z4 = 0.5*bfdet_vg - (Le_blt_flange_z1 + k1_vg + (n_blt_flange_z - 1)*g_blt_flange)",
                    "le2z4": le2_z4.model_dump() if le2_z4 is not None else None,
                    "g1_blt_flange_var": "g1_blt_flange",
                    "g1_blt_flange_formula": "g1_blt_flange = bf_vg - 2*(Le_blt_flange_z1 + (n_blt_flange_z - 1)*g_blt_flange)",
                    "g1_blt_flange": g1_blt_flange.model_dump() if g1_blt_flange is not None else None,
                    "f_blt_flange_var": "F_blt_flange",
                    "f_blt_flange_formula": "F_blt_flange = 0.5*g1_blt_flange - 0.5*tw_vg - t_plt_web",
                    "f_blt_flange": f_blt_flange.model_dump() if f_blt_flange is not None else None,
                    "n2x_var": "n_blt_flange_x",
                    "n2x": case.geometry.n_blt_flange_x,
                    "s2x_var": "p_blt_flange",
                    "s2x": s2x.model_dump(),
                    "le2x1_var": "Le_blt_flange_x1",
                    "le2x1": le2_x1.model_dump(),
                    "xk_blt_flange_var": "x_k_blt_flange",
                    "xk_blt_flange_formula": "x_k_blt_flange = Le_blt_flange_x1 + k*p_blt_flange",
                    "xk_blt_flange_k_range": "k = 0, 1, ..., n_blt_flange_x - 1",
                    "xk_blt_flange_values": xk_blt_flange_values,
                    "n2z_var": "n_blt_flange_z",
                    "n2z": case.geometry.n_blt_flange_z,
                    "le2z1_var": "Le_blt_flange_z1",
                    "le2z1": le2_z1.model_dump(),
                    "s2z1_var": "g_blt_flange",
                    "s2z1": s2z1.model_dump(),
                    "type_hole_flange_var": "type_hole_flange",
                    "type_hole_flange": case.geometry.type_hole_plt_flange,
                    "anv1_formula": "Anv.y1.vg = tw_vg*(d_vg-n_blt_web_y*(dh_plt_web+1.6mm))",
                    "anv1": anv1.model_dump(),
                    "ant1_formula": "Ant.x1.vg = tw_vg*(d_vg-n_blt_web_y*(dh_plt_web+1.6mm))",
                    "ant1": ant1.model_dump(),
                    "us1_formula": u1_formula,
                    "us1": u1,
                    "dh_1": dh_web.model_dump(),
                    "dh_2": dh_flange.model_dump(),
                },
                {
                    "id": "bbmb_splice.step4.web_tearout_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por desgarramiento de perno critico en alma",
                    "clause": "AISC 360-22 J3.11a.(b)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "p_blt_web_var": "p_blt_web",
                    "p_blt_web": s1y.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "lc_blt_web_y_var": "lc_blt_web_y",
                    "lc_blt_web_y_formula": "lc_blt_web_y = p_blt_web - dh.1",
                    "lc_blt_web_y": lc_blt_web_y.model_dump(),
                    "svc_hole_deformation_design_web_var": "svc_hole_deformation_design_web",
                    "svc_hole_deformation_design_web": svc_hole_deformation_design_web,
                    "rn1_web_v2_vg_var": "Rn1_web_v2_vg",
                    "rn1_web_v2_vg_formula": (
                        "Rn1_web_v2_vg = 1.2*lc_blt_web_y*tw_vg*Fu_vg"
                        if svc_hole_deformation_design_web
                        else "Rn1_web_v2_vg = 1.5*lc_blt_web_y*tw_vg*Fu_vg"
                    ),
                    "rn1_web_v2_vg": (
                        rn1_web_ind_v2_vg.model_dump() if isinstance(rn1_web_ind_v2_vg, Quantity) else None
                    ),
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "phi_rn1_web_v2_vg_var": "phi*Rn1_web_v2_vg",
                    "phi_rn1_web_v2_vg_formula": "phi*Rn1_web_v2_vg = phi_fragil*Rn1_web_v2_vg",
                    "phi_rn1_web_v2_vg": phi_rn1_web_v2_vg.model_dump(),
                    "ru1_web_v2_vg_var": "Ru1_web_v2_vg",
                    "ru1_web_v2_vg": ru_web_v2_vg.model_dump(),
                    "dcr1_web_v2_vg_var": "DCR1_web_v2_vg",
                    "dcr1_web_v2_vg": tearout_web_dcr,
                    "result_web_tearout_v2_vg": "PASS" if tearout_web_passed else "FAIL",
                    "coefficient": tearout_web_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_tearout_v2_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por desgarramiento en perforacion del perno de platina 1 (direccion 2)",
                    "clause": "AISC 360-22 J3.11a.(b)",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": case.geometry.t_plt_web.model_dump(),
                    "p_plt_web_var": "p_plt_web",
                    "p_plt_web": s1y.model_dump(),
                    "le_plt_web_y1_var": "Le_plt_web_y1",
                    "le_plt_web_y1": le1_y1.model_dump(),
                    "le_plt_web_y2_var": "Le_plt_web_y2",
                    "le_plt_web_y2": le1_y2.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "lc_plt_v2_web_var": "lc_plt_v2_web",
                    "lc_plt_v2_web_formula": "lc_plt_v2_web = min(p_plt_web - dh.1, Le_plt_web_y1 - 0.5*dh.1, Le_plt_web_y2 - 0.5*dh.1)",
                    "lc_plt_v2_web": lc_plt_v2_web.model_dump(),
                    "svc_hole_deformation_design_web_var": "svc_hole_deformation_design_web",
                    "svc_hole_deformation_design_web": svc_hole_deformation_design_web,
                    "rn1_plt_v2_web_var": "Rn1_plt_v2_web",
                    "rn1_plt_v2_web_formula": (
                        "Rn1_plt_v2_web = 1.2*lc_plt_v2_web*t_plt_web*Fu_plt_web"
                        if svc_hole_deformation_design_web
                        else "Rn1_plt_v2_web = 1.5*lc_plt_v2_web*t_plt_web*Fu_plt_web"
                    ),
                    "rn1_plt_v2_web": rn1_plt_v2_web.model_dump() if isinstance(rn1_plt_v2_web, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "phi_rn1_plt_v2_web_var": "phi*Rn1_plt_v2_web",
                    "phi_rn1_plt_v2_web_formula": "phi*Rn1_plt_v2_web = phi_fragil*Rn1_plt_v2_web",
                    "phi_rn1_plt_v2_web": phi_rn1_plt_v2_web.model_dump(),
                    "coefficient": tearout_plt1_web_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_tearout_v3_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por desgarramiento en perforacion del perno de platina 1 (direccion 3)",
                    "clause": "AISC 360-22 J3.11a.(b)",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": case.geometry.t_plt_web.model_dump(),
                    "g_plt_web_var": "g_plt_web",
                    "g_plt_web": s1x.model_dump(),
                    "le_plt_web_x2_var": "Le_plt_web_x2",
                    "le_plt_web_x2": le1_x2.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "lc_plt_v3_web_var": "lc_plt_v3_web",
                    "lc_plt_v3_web_formula": "lc_plt_v3_web = min(g_plt_web - dh.1, Le_plt_web_x2 - 0.5*dh.1)",
                    "lc_plt_v3_web": lc_plt_v3_web.model_dump(),
                    "svc_hole_deformation_design_web_var": "deformation_at_bolt_hole_service_load_is_design",
                    "svc_hole_deformation_design_web": svc_hole_deformation_design_web,
                    "rn1_plt_v3_web_var": "Rn1_plt_v3_web",
                    "rn1_plt_v3_web_formula": (
                        "Rn1_plt_v3_web = 1.2*lc_plt_v3_web*t_plt_web*Fu_plt_web"
                        if svc_hole_deformation_design_web
                        else "Rn1_plt_v3_web = 1.5*lc_plt_v3_web*t_plt_web*Fu_plt_web"
                    ),
                    "rn1_plt_v3_web": rn1_plt_v3_web.model_dump() if isinstance(rn1_plt_v3_web, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "phi_rn1_plt_v3_web_var": "phi*Rn1_plt_v3_web",
                    "phi_rn1_plt_v3_web_formula": "phi*Rn1_plt_v3_web = phi_fragil*Rn1_plt_v3_web",
                    "phi_rn1_plt_v3_web": phi_rn1_plt_v3_web.model_dump(),
                    "coefficient": tearout_plt1_web_v3_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step4.web_tearout_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por desgarramiento en perforacion del perno en direccion 3",
                    "clause": "AISC 360-22 J3.11a.(b)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "le_blt_web_x1_var": "Le_blt_web_x1",
                    "le_blt_web_x1": le1_x1.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "lc_web_v3_vg_var": "lc_web_v3_vg",
                    "lc_web_v3_vg_formula": "lc_web_v3_vg = min(g_blt_web - dh.1, Le_blt_web_x1 - 0.5*dh.1)",
                    "lc_web_v3_vg": lc_web_v3_vg.model_dump(),
                    "svc_hole_deformation_design_web_var": "svc_hole_deformation_design_web",
                    "svc_hole_deformation_design_web": svc_hole_deformation_design_web,
                    "rn1_web_v3_vg_var": "Rn1_web_v3_vg",
                    "rn1_web_v3_vg_formula": (
                        "Rn1_web_v3_vg = 1.2*lc_web_v3_vg*tw_vg*Fu_vg"
                        if svc_hole_deformation_design_web
                        else "Rn1_web_v3_vg = 1.5*lc_web_v3_vg*tw_vg*Fu_vg"
                    ),
                    "rn1_web_v3_vg": rn1_web_v3_vg.model_dump() if isinstance(rn1_web_v3_vg, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "phi_rn1_web_v3_vg_var": "phi*Rn1_web_v3_vg",
                    "phi_rn1_web_v3_vg_formula": "phi*Rn1_web_v3_vg = phi_fragil*Rn1_web_v3_vg",
                    "phi_rn1_web_v3_vg": phi_rn1_web_v3_vg.model_dump(),
                    "ru1_web_v3_vg_var": "Ru1_web_v3_vg",
                    "ru1_web_v3_vg": ru1_web_v3_vg.model_dump() if isinstance(ru1_web_v3_vg, Quantity) else None,
                    "dcr1_web_v3_vg_var": "DCR1_web_v3_vg",
                    "dcr1_web_v3_vg": dcr1_web_v3_vg,
                    "result1_web_v3_vg": result1_web_v3_vg,
                    "coefficient": tearout_web_v3_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step4.flange_tension_tearout_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por desgarramiento en la perforacion del perno del ala en direccion 3",
                    "clause": "AISC 360-22 J3.11a.(b)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tf_vg_var": "tf_vg",
                    "tf_vg": tf_catalog.model_dump(),
                    "p_blt_flange_var": "p_blt_flange",
                    "p_blt_flange": s2x.model_dump(),
                    "le_blt_flange_x1_var": "Le_blt_flange_x1",
                    "le_blt_flange_x1": le2_x1.model_dump(),
                    "dh_2_var": "dh.2",
                    "dh_2": dh_flange.model_dump(),
                    "lc_flange_p3_vg_var": "lc_flange_p3_vg",
                    "lc_flange_p3_vg_formula": "lc_flange_p3_vg = min(p_blt_flange - dh.2, Le_blt_flange_x1 - 0.5*dh.2)",
                    "lc_flange_p3_vg": lc_flange_p3_vg.model_dump(),
                    "svc_hole_deformation_design_flange_var": "deformation_at_bolt_hole_service_load_is_design",
                    "svc_hole_deformation_design_flange": svc_hole_deformation_design_flange,
                    "rn1_flange_p3_vg_var": "Rn1_flange_p3_vg",
                    "rn1_flange_p3_vg_formula": (
                        "Rn1_flange_p3_vg = 1.2*lc_flange_p3_vg*tf_vg*Fu_vg"
                        if svc_hole_deformation_design_flange
                        else "Rn1_flange_p3_vg = 1.5*lc_flange_p3_vg*tf_vg*Fu_vg"
                    ),
                    "rn1_flange_p3_vg": rn1_flange_p3_vg.model_dump() if isinstance(rn1_flange_p3_vg, Quantity) else None,
                    "phi_pr_var": "phi_pr",
                    "phi_pr": phi_fragil_flange,
                    "phi_rn1_flange_p3_vg_var": "phi*Rn1_flange_p3_vg",
                    "phi_rn1_flange_p3_vg_formula": "phi*Rn1_flange_p3_vg = phi_pr*Rn1_flange_p3_vg",
                    "phi_rn1_flange_p3_vg": phi_rn1_flange_p3_vg.model_dump() if isinstance(phi_rn1_flange_p3_vg, Quantity) else None,
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "mu3_sp_var": "Mu3_sp",
                    "mu3_sp": case.loads.Mu3_sp.model_dump(),
                    "d_vg_var": "d_vg",
                    "d_vg": dvg_catalog.model_dump(),
                    "ru1_flange_p3_vg_var": "Ru1_flange_p3(+)_vg",
                    "ru1_flange_p3_vg_formula": "Ru1_flange_p3(+)_vg = (1- alpha_Pu_web)*Pu_sp + Mu3_sp/(d_vg - tf_vg)",
                    "ru1_flange_p3_vg": ru1_flange_p3_vg.model_dump(),
                    "dcr1_flange_p3_vg_var": "DCR1_flange_p3_vg",
                    "dcr1_flange_p3_vg": dcr1_flange_p3_vg,
                    "result1_flange_p3_vg": result1_flange_p3_vg,
                    "coefficient": tearout_flange_p3_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step4.flange_shear_tearout_v1_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por desgarramiento en la perforacion del perno del ala en direccion 1",
                    "clause": "AISC 360-22 J3.11a.(b)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tf_vg_var": "tf_vg",
                    "tf_vg": tf_catalog.model_dump(),
                    "g_blt_flange_var": "g_blt_flange",
                    "g_blt_flange": s2z1.model_dump(),
                    "n_blt_flange_z_var": "n_blt_flange_z",
                    "n_blt_flange_z": case.geometry.n_blt_flange_z,
                    "le_blt_flange_z1_var": "Le_blt_flange_z1",
                    "le_blt_flange_z1": le2_z1.model_dump(),
                    "dh_2_var": "dh.2",
                    "dh_2": dh_flange.model_dump(),
                    "lc_flange_v1_vg_var": "lc_flange_v1_vg",
                    "lc_flange_v1_vg_formula": lc_flange_v1_vg_formula,
                    "lc_flange_v1_vg": lc_flange_v1_vg.model_dump(),
                    "svc_hole_deformation_design_flange_var": "deformation_at_bolt_hole_service_load_is_design",
                    "svc_hole_deformation_design_flange": svc_hole_deformation_design_flange,
                    "rn1_flange_v1_vg_var": "Rn1_flange_v1_vg",
                    "rn1_flange_v1_vg_formula": (
                        "Rn1_flange_v1_vg = 1.2*lc_flange_v1_vg*tf_vg*Fu_vg"
                        if svc_hole_deformation_design_flange
                        else "Rn1_flange_v1_vg = 1.5*lc_flange_v1_vg*tf_vg*Fu_vg"
                    ),
                    "rn1_flange_v1_vg": rn1_flange_v1_vg.model_dump() if isinstance(rn1_flange_v1_vg, Quantity) else None,
                    "phi_pr_var": "phi_pr",
                    "phi_pr": phi_fragil_flange,
                    "phi_rn1_flange_v1_vg_var": "phi*Rn1_flange_v1_vg",
                    "phi_rn1_flange_v1_vg_formula": "phi*Rn1_flange_v1_vg = phi_pr*Rn1_flange_v1_vg",
                    "phi_rn1_flange_v1_vg": (
                        phi_rn1_flange_v1_vg.model_dump() if isinstance(phi_rn1_flange_v1_vg, Quantity) else None
                    ),
                    "coefficient": tearout_flange_v1_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step4.flange_flexural_rupture_m1_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por rotura a flexion en la viga (agujeros en ala traccionada)",
                    "clause": "AISC 360-22 F13.1",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "fy_vg_var": "Fy_vg",
                    "fy_vg": fy_vg.model_dump() if isinstance(fy_vg, Quantity) else None,
                    "tf_vg_var": "tf_vg",
                    "tf_vg": tf_catalog.model_dump(),
                    "bf_vg_var": "bf_vg",
                    "bf_vg": bf_catalog.model_dump(),
                    "n_blt_flange_z_var": "n_blt_flange_z",
                    "n_blt_flange_z": case.geometry.n_blt_flange_z,
                    "dh_2_var": "dh.2",
                    "dh_2": dh_flange.model_dump(),
                    "hole_add_var": "delta_hole",
                    "hole_add": Quantity(value=hole_add_f13, unit=dh_flange.unit).model_dump(),
                    "afg_flange_m1_vg_var": "Afg_flange_m1_vg",
                    "afg_flange_m1_vg_formula": "Afg_flange_m1_vg = tf_vg*bf_vg",
                    "afg_flange_m1_vg": afg_flange_m1_vg.model_dump(),
                    "afn_flange_m1_vg_var": "Afn_flange_m1_vg",
                    "afn_flange_m1_vg_formula": "Afn_flange_m1_vg = Afg_flange_m1_vg - 2*n_blt_flange_z*(dh.2 + 1.80mm)*tf_vg",
                    "afn_flange_m1_vg": afn_flange_m1_vg.model_dump(),
                    "sx_vg_var": "Sx_vg",
                    "sx_vg_formula": "Sx_vg tomado del catalogo (usando zx)",
                    "sx_vg": sx_catalog.model_dump(),
                    "yf_var": "Yf",
                    "yf": flange_flex_rupture_m1_inter.get("yf"),
                    "fy_over_fu_var": "Fy/Fu",
                    "fy_over_fu": flange_flex_rupture_m1_inter.get("fy_over_fu"),
                    "lhs_fu_afn_var": "Fu*Afn",
                    "lhs_fu_afn": (
                        flange_flex_rupture_m1_inter.get("lhs_fu_afn").model_dump()
                        if isinstance(flange_flex_rupture_m1_inter.get("lhs_fu_afn"), Quantity)
                        else None
                    ),
                    "rhs_yf_fy_agf_var": "Yf*Fy*Agf",
                    "rhs_yf_fy_agf": (
                        flange_flex_rupture_m1_inter.get("rhs_yf_fy_agf").model_dump()
                        if isinstance(flange_flex_rupture_m1_inter.get("rhs_yf_fy_agf"), Quantity)
                        else None
                    ),
                    "limit_applies_var": "F13.1_aplica",
                    "limit_applies": limit_applies_flange_m1,
                    "phi_no_ductil_var": "phi_no_ductil",
                    "phi_no_ductil": phi_no_ductil_m1,
                    "rn1_flange_m1_vg_var": "Rn1_flange_m1_vg",
                    "rn1_flange_m1_vg_formula": "Rn1_flange_m1_vg = (Fu_vg*Afn_flange_m1_vg/Afg_flange_m1_vg)*Sx_vg",
                    "rn1_flange_m1_vg": rn1_flange_m1_vg.model_dump() if isinstance(rn1_flange_m1_vg, Quantity) else None,
                    "phi_rn1_flange_m1_vg_var": "phi*Rn1_flange_m1_vg",
                    "phi_rn1_flange_m1_vg_formula": "phi*Rn1_flange_m1_vg = phi_no_ductil*Rn1_flange_m1_vg",
                    "phi_rn1_flange_m1_vg": phi_rn1_flange_m1_vg.model_dump(),
                    "ru1_flange_m1_vg_var": "Ru1_flange_m1_vg",
                    "ru1_flange_m1_vg_formula": "Ru1_flange_m1_vg = Mu3_sp",
                    "mu3_sp_var": "Mu3_sp",
                    "mu3_sp": case.loads.Mu3_sp.model_dump(),
                    "ru1_flange_m1_vg": ru1_flange_m1_vg.model_dump(),
                    "dcr1_flange_m1_vg_var": "DCR1_flange_m1_vg",
                    "dcr1_flange_m1_vg": dcr1_flange_m1_vg,
                    "result1_flange_m1_vg": result1_flange_m1_vg,
                    "reference": "AISC 360-22 F13.1 (DRY: compute_member_flexural_rupture_with_tension_flange_holes_f131)",
                },
                {
                    "id": "bbmb_splice.step4.viga_combined_forces_note",
                    "scope": "viga",
                    "description": "Revision de capacidad bajo la accion de fuerzas combinadas en la viga",
                    "clause": "AISC 360-22 H1-1a/H1-1b",
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "phi_pnc_var": "phiPnc",
                    "phi_pnc": (
                        member_capacity.phiPnc.model_dump()
                        if member_capacity is not None and isinstance(member_capacity.phiPnc, Quantity)
                        else None
                    ),
                    "phi_mn3_var": "phiMn3",
                    "phi_mn3": (
                        member_capacity.phiMn3.model_dump()
                        if member_capacity is not None and isinstance(member_capacity.phiMn3, Quantity)
                        else None
                    ),
                    "phi_mn2_var": "phiMn2",
                    "phi_mn2": (
                        member_capacity.phiMn2.model_dump()
                        if member_capacity is not None and isinstance(member_capacity.phiMn2, Quantity)
                        else None
                    ),
                    "dcr_451_var": "DCR_4.5.1",
                    "dcr_451": dcr3_v3_vg,
                    "dcr_481_var": "DCR_4.8.1",
                    "dcr_481": dcr1_flange_m1_vg,
                    "mrx_from_mu3_var": "|Mu3_sp|/phiMn3",
                    "mrx_from_mu3": mrx_over_mcx_mu3_term,
                    "pr_over_pc_var": "Pr/(phiPc)",
                    "pr_over_pc": pr_over_pc_vg,
                    "mrx_over_mcx_var": "Mrx/Mcx",
                    "mrx_over_mcx": mrx_over_mcx_vg,
                    "mry_over_mcy_var": "Mry/Mcy",
                    "mry_over_mcy": mry_over_mcy_vg,
                    "equation_used": h11_equation_used_vg,
                    "dcr_fcomb_vg_var": "DCR_Fcomb_vg",
                    "dcr_fcomb_vg": dcr_fcomb_vg,
                    "result_fcomb_vg": result_fcomb_vg,
                    "reference": "AISC 360-22 H1.1 (DRY: compute_member_combined_interaction_h11)",
                },
                {
                    "id": "bbmb_splice.step4.flange_tension_bearing_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por aplatamiento en la perforacion del perno del ala en direccion 3",
                    "clause": "AISC 360-22 J3.11a.(a)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tf_vg_var": "tf_vg",
                    "tf_vg": tf_catalog.model_dump(),
                    "db_blt_flange_var": "db_blt_flange",
                    "db_blt_flange": db_flange.model_dump(),
                    "svc_hole_deformation_design_flange_var": "deformation_at_bolt_hole_service_load_is_design",
                    "svc_hole_deformation_design_flange": svc_hole_deformation_design_flange,
                    "rn2_flange_p3_vg_var": "Rn2_flange_p3_vg",
                    "rn2_flange_p3_vg_formula": (
                        "Rn2_flange_p3_vg = 2.4*db_blt_flange*tf_vg*Fu_vg"
                        if svc_hole_deformation_design_flange
                        else "Rn2_flange_p3_vg = 3.0*db_blt_flange*tf_vg*Fu_vg"
                    ),
                    "rn2_flange_p3_vg": rn2_flange_p3_vg.model_dump() if isinstance(rn2_flange_p3_vg, Quantity) else None,
                    "phi_pr_var": "phi_pr",
                    "phi_pr": phi_fragil_flange,
                    "phi_rn2_flange_p3_vg_var": "phi*Rn2_flange_p3_vg",
                    "phi_rn2_flange_p3_vg_formula": "phi*Rn2_flange_p3_vg = phi_pr*Rn2_flange_p3_vg",
                    "phi_rn2_flange_p3_vg": phi_rn2_flange_p3_vg.model_dump() if isinstance(phi_rn2_flange_p3_vg, Quantity) else None,
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "mu3_sp_var": "Mu3_sp",
                    "mu3_sp": case.loads.Mu3_sp.model_dump(),
                    "d_vg_var": "d_vg",
                    "d_vg": dvg_catalog.model_dump(),
                    "ru2_flange_p3_vg_var": "Ru2_flange_p3(+)_vg",
                    "ru2_flange_p3_vg_formula": "Ru2_flange_p3(+)_vg = (1- alpha_Pu_web)*Pu_sp + Mu3_sp/(d_vg - tf_vg)",
                    "ru2_flange_p3_vg": ru2_flange_p3_vg.model_dump(),
                    "dcr2_flange_p3_vg_var": "DCR2_flange_p3_vg",
                    "dcr2_flange_p3_vg": dcr2_flange_p3_vg,
                    "result2_flange_p3_vg": result2_flange_p3_vg,
                    "coefficient": bearing_flange_p3_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(a) (DRY: compute_bolt_hole_bearing_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step4.flange_tension_bolt_shear_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por rotura a cortante en el perno del ala en direccion 3",
                    "clause": "AISC 360-22 J3.7",
                    "db_blt_flange_var": "db_blt_flange",
                    "db_blt_flange": db_flange.model_dump(),
                    "ab_blt_flange_var": "Ab_blt_flange",
                    "ab_blt_flange": (
                        bolt_shear_flange.get("bolt_area").model_dump()
                        if isinstance(bolt_shear_flange, dict) and isinstance(bolt_shear_flange.get("bolt_area"), Quantity)
                        else None
                    ),
                    "fnv_blt_flange_var": "Fnv_blt_flange",
                    "fnv_blt_flange": fnv_flange.model_dump() if isinstance(fnv_flange, Quantity) else None,
                    "phi_pr_var": "phi_pr",
                    "phi_pr": phi_fragil_flange,
                    "rn3_flange_p3_vg_var": "Rn3_flange_p3_vg",
                    "rn3_flange_p3_vg_formula": "Rn3_flange_p3_vg = Ab_blt_flange*Fnv_blt_flange",
                    "rn3_flange_p3_vg": (
                        bolt_shear_flange.get("rnv_b").model_dump()
                        if isinstance(bolt_shear_flange, dict) and isinstance(bolt_shear_flange.get("rnv_b"), Quantity)
                        else None
                    ),
                    "phi_rn3_flange_p3_vg_var": "phi*Rn3_flange_p3_vg",
                    "phi_rn3_flange_p3_vg_formula": "phi*Rn3_flange_p3_vg = phi_pr*Rn3_flange_p3_vg",
                    "phi_rn3_flange_p3_vg": (
                        bolt_shear_flange.get("phi_rnv_b").model_dump()
                        if isinstance(bolt_shear_flange, dict) and isinstance(bolt_shear_flange.get("phi_rnv_b"), Quantity)
                        else None
                    ),
                    "ru3_flange_p3_vg_var": "Ru3_flange_p3(+)_vg",
                    "ru3_flange_p3_vg_formula": "Ru3_flange_p3(+)_vg = Ru_blt_2_flange_vg (tomado de 3.2)",
                    "ru3_flange_p3_vg": ru2_flange_p3_vg.model_dump(),
                    "dcr3_flange_p3_vg_var": "DCR3_flange_p3_vg",
                    "dcr3_flange_p3_vg": (
                        abs(ru2_flange_p3_vg.value) / bolt_shear_flange.get("phi_rnv_b").value
                        if isinstance(bolt_shear_flange, dict)
                        and isinstance(bolt_shear_flange.get("phi_rnv_b"), Quantity)
                        and ru2_flange_p3_vg.unit == bolt_shear_flange.get("phi_rnv_b").unit
                        and abs(bolt_shear_flange.get("phi_rnv_b").value) > 1e-12
                        else None
                    ),
                    "result3_flange_p3_vg": (
                        "PASS"
                        if isinstance(bolt_shear_flange, dict)
                        and isinstance(bolt_shear_flange.get("phi_rnv_b"), Quantity)
                        and ru2_flange_p3_vg.unit == bolt_shear_flange.get("phi_rnv_b").unit
                        and abs(bolt_shear_flange.get("phi_rnv_b").value) > 1e-12
                        and abs(ru2_flange_p3_vg.value) / bolt_shear_flange.get("phi_rnv_b").value <= 1.0
                        else "FAIL"
                    ),
                    "reference": "AISC 360-22 J3.7 (DRY: compute_bolt_shear_rupture_capacity_per_bolt)",
                },
                {
                    "id": "bbmb_splice.step4.flange_tension_block_shear_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por bloque de cortante en ala de viga en direccion 3",
                    "clause": "AISC 360-22 J4.3",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "fy_vg_var": "Fy_vg",
                    "fy_vg": fy_vg.model_dump() if isinstance(fy_vg, Quantity) else None,
                    "tf_vg_var": "tf_vg",
                    "tf_vg": tf_catalog.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "d_vg_var": "d_vg",
                    "d_vg": dvg_catalog.model_dump(),
                    "kdes_vg_var": "kdes_vg",
                    "kdes_vg": kdes_catalog.model_dump(),
                    "a_g_var": "A_g",
                    "a_g": ag_catalog.model_dump(),
                    "n_blt_flange_x_var": "n_blt_flange_x",
                    "n_blt_flange_x": case.geometry.n_blt_flange_x,
                    "n_blt_flange_z_var": "n_blt_flange_z",
                    "n_blt_flange_z": case.geometry.n_blt_flange_z,
                    "p_blt_flange_var": "p_blt_flange",
                    "p_blt_flange": s2x.model_dump(),
                    "le_blt_flange_x1_var": "Le_blt_flange_x1",
                    "le_blt_flange_x1": le2_x1.model_dump(),
                    "le_blt_flange_z1_var": "Le_blt_flange_z1",
                    "le_blt_flange_z1": le2_z1.model_dump(),
                    "dh_2_var": "dh.2",
                    "dh_2": dh_flange.model_dump(),
                    "hole_add_var": "delta_hole",
                    "hole_add": Quantity(value=hole_add_block_flange, unit=dh_flange.unit).model_dump(),
                    "ubs_flange_v3_vg_var": "Ubs_flange_v3_vg",
                    "ubs_flange_v3_vg": ubs_flange_v3_vg,
                    "ubs_flange_v1_vg_var": "Ubs_flange_v1_vg",
                    "ubs_flange_v1_vg": ubs_flange_v1_vg,
                    "agt1_flange_v3_vg_var": "Agt1_flange_v3_vg",
                    "agt1_flange_v3_vg_formula": "Agt1_flange_v3_vg = 2 * (Le_blt_flange_z1 * tf_vg)",
                    "agt1_flange_v3_vg": agt1_flange_v3_vg.model_dump(),
                    "ant1_flange_v3_vg_var": "Ant1_flange_v3_vg",
                    "ant1_flange_v3_vg_formula": "Ant1_flange_v3_vg = Agt1_flange_v3_vg - 2 *tf_vg * 0.5 * (dh.2 +1.80mm)",
                    "ant1_flange_v3_vg": ant1_flange_v3_vg.model_dump(),
                    "agv1_flange_v3_vg_var": "Agv1_flange_v3_vg",
                    "agv1_flange_v3_vg_formula": "Agv1_flange_v3_vg = 2 * tf_vg * ( Le_blt_flange_x1 + (n_blt_flange_x - 1)* p_blt_flange )",
                    "agv1_flange_v3_vg": agv1_flange_v3_vg.model_dump(),
                    "anv1_flange_v3_vg_var": "Anv1_flange_v3_vg",
                    "anv1_flange_v3_vg_formula": "Anv1_flange_v3_vg = Agv1_flange_v3_vg - 2 *tf_vg * (n_blt_flange_x - 0.5) * (dh.2 +1.80mm)",
                    "anv1_flange_v3_vg": anv1_flange_v3_vg.model_dump(),
                    "rn4_1_case1_flange_p3_vg_var": "Rn4_1_case1_flange_p3_vg",
                    "rn4_1_case1_flange_p3_vg": rn4_1_case1_flange_p3_vg.model_dump() if isinstance(rn4_1_case1_flange_p3_vg, Quantity) else None,
                    "rn4_2_case1_flange_p3_vg_var": "Rn4_2_case1_flange_p3_vg",
                    "rn4_2_case1_flange_p3_vg": rn4_2_case1_flange_p3_vg.model_dump() if isinstance(rn4_2_case1_flange_p3_vg, Quantity) else None,
                    "rn4_case1_flange_p3_vg_var": "Rn4_case1_flange_p3_vg",
                    "rn4_case1_flange_p3_vg": rn4_case1_flange_p3_vg.model_dump() if isinstance(rn4_case1_flange_p3_vg, Quantity) else None,
                    "phi_rn4_case1_flange_p3_vg_var": "phi*Rn4_case1_flange_p3_vg",
                    "phi_rn4_case1_flange_p3_vg": phi_rn4_case1_flange_p3_vg.model_dump(),
                    "agt2_flange_v3_vg_var": "Agt2_flange_v3_vg",
                    "agt2_flange_v3_vg_formula": "Agt2_flange_v3_vg = 0.5*(A_g - (d_vg - 2 *kdes_vg)*tw_vg)",
                    "agt2_flange_v3_vg": agt2_flange_v3_vg.model_dump(),
                    "ant2_flange_v3_vg_var": "Ant2_flange_v3_vg",
                    "ant2_flange_v3_vg_formula": "Ant2_flange_v3_vg = Agt2_flange_v3_vg - n_blt_flange_z * tf_vg * (dh.2 +1.80mm)",
                    "ant2_flange_v3_vg": ant2_flange_v3_vg.model_dump(),
                    "agv2_flange_v3_vg_var": "Agv2_flange_v3_vg",
                    "agv2_flange_v3_vg_formula": "Agv2_flange_v3_vg = tw_vg * ( Le_blt_flange_x1 + (n_blt_flange_x - 1)* p_blt_flange )",
                    "agv2_flange_v3_vg": agv2_flange_v3_vg.model_dump(),
                    "anv2_flange_v3_vg_var": "Anv2_flange_v3_vg",
                    "anv2_flange_v3_vg_formula": "Anv2_flange_v3_vg = Agv2_flange_v3_vg",
                    "anv2_flange_v3_vg": anv2_flange_v3_vg.model_dump(),
                    "rn4_1_case2_flange_p3_vg_var": "Rn4_1_case2_flange_p3_vg",
                    "rn4_1_case2_flange_p3_vg": rn4_1_case2_flange_p3_vg.model_dump() if isinstance(rn4_1_case2_flange_p3_vg, Quantity) else None,
                    "rn4_2_case2_flange_p3_vg_var": "Rn4_2_case2_flange_p3_vg",
                    "rn4_2_case2_flange_p3_vg": rn4_2_case2_flange_p3_vg.model_dump() if isinstance(rn4_2_case2_flange_p3_vg, Quantity) else None,
                    "rn4_case2_flange_p3_vg_var": "Rn4_case2_flange_p3_vg",
                    "rn4_case2_flange_p3_vg": rn4_case2_flange_p3_vg.model_dump() if isinstance(rn4_case2_flange_p3_vg, Quantity) else None,
                    "phi_rn4_case2_flange_p3_vg_var": "phi*Rn4_case2_flange_p3_vg",
                    "phi_rn4_case2_flange_p3_vg": phi_rn4_case2_flange_p3_vg.model_dump(),
                    "phi_pr_var": "phi_pr",
                    "phi_pr": phi_fragil_flange,
                    "phi_rn4_flange_p3_vg_var": "phi*Rn4_flange_p3_vg",
                    "phi_rn4_flange_p3_vg_formula": "phi*Rn4_flange_p3_vg = min(phi*Rn4_case1_flange_p3_vg, phi*Rn4_case2_flange_p3_vg)",
                    "phi_rn4_flange_p3_vg": phi_rn4_flange_p3_vg.model_dump(),
                    "controlling_case_flange_p3_vg_var": "Caso_control",
                    "controlling_case_flange_p3_vg": controlling_case_flange_p3_vg,
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "mu3_sp_var": "Mu3_sp",
                    "mu3_sp": case.loads.Mu3_sp.model_dump(),
                    "ru4_flange_p3_vg_var": "Ru4_flange_p3(+)_vg",
                    "ru4_flange_p3_vg_formula": "Ru4_flange_p3(+)_vg = (1- alpha_Pu_web ) * Pu_sp + Mu3_sp /(d_vg - tf_vg), si <0 entonces 0",
                    "ru4_flange_p3_vg": ru4_flange_p3_vg.model_dump(),
                    "dcr4_flange_p3_vg_var": "DCR4_flange_p3_vg",
                    "dcr4_flange_p3_vg": dcr4_flange_p3_vg,
                    "result4_flange_p3_vg": result4_flange_p3_vg,
                    "reference_case1": "AISC 360-22 J4.3 (DRY: compute_block_shear_strength_j45)",
                    "reference_case2": "AISC 360-22 J4.3 (DRY: compute_block_shear_strength_j45)",
                },
                {
                    "id": "bbmb_splice.step4.web_bearing_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por aplatamiento en perforacion de perno critico en alma",
                    "clause": "AISC 360-22 J3.11a.(a)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "db_blt_web_var": "db_blt_web",
                    "db_blt_web": db_web.model_dump(),
                    "svc_hole_deformation_design_web_var": "svc_hole_deformation_design_web",
                    "svc_hole_deformation_design_web": svc_hole_deformation_design_web,
                    "rn2_web_v2_vg_var": "Rn2_web_v2_vg",
                    "rn2_web_v2_vg_formula": (
                        "Rn2_web_v2_vg = 2.4*db_blt_web*tw_vg*Fu_vg"
                        if svc_hole_deformation_design_web
                        else "Rn2_web_v2_vg = 3.0*db_blt_web*tw_vg*Fu_vg"
                    ),
                    "rn2_web_v2_vg": rn2_web_v2_vg.model_dump() if isinstance(rn2_web_v2_vg, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "phi_rn2_web_v2_vg_var": "phi*Rn2_web_v2_vg",
                    "phi_rn2_web_v2_vg_formula": "phi*Rn2_web_v2_vg = phi_fragil*Rn2_web_v2_vg",
                    "phi_rn2_web_v2_vg": phi_rn2_web_v2_vg.model_dump(),
                    "coefficient": bearing_web_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(a) (DRY: compute_bolt_hole_bearing_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step4.web_bearing_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por aplastamiento en perforacion del perno en direccion 3",
                    "clause": "AISC 360-22 J3.11a.(a)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "db_blt_web_var": "db_blt_web",
                    "db_blt_web": db_web.model_dump(),
                    "svc_hole_deformation_design_web_var": "svc_hole_deformation_design_web",
                    "svc_hole_deformation_design_web": svc_hole_deformation_design_web,
                    "rn2_web_v3_vg_var": "Rn2_web_v3_vg",
                    "rn2_web_v3_vg_formula": (
                        "Rn2_web_v3_vg = 2.4*db_blt_web*tw_vg*Fu_vg"
                        if svc_hole_deformation_design_web
                        else "Rn2_web_v3_vg = 3.0*db_blt_web*tw_vg*Fu_vg"
                    ),
                    "rn2_web_v3_vg": rn2_web_v3_vg.model_dump() if isinstance(rn2_web_v3_vg, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "phi_rn2_web_v3_vg_var": "phi*Rn2_web_v3_vg",
                    "phi_rn2_web_v3_vg_formula": "phi*Rn2_web_v3_vg = phi_fragil*Rn2_web_v3_vg",
                    "phi_rn2_web_v3_vg": phi_rn2_web_v3_vg.model_dump(),
                    "ru2_web_v3_vg_var": "Ru2_web_v3_vg",
                    "ru2_web_v3_vg": ru2_web_v3_vg.model_dump() if isinstance(ru2_web_v3_vg, Quantity) else None,
                    "dcr2_web_v3_vg_var": "DCR2_web_v3_vg",
                    "dcr2_web_v3_vg": dcr2_web_v3_vg,
                    "result2_web_v3_vg": result2_web_v3_vg,
                    "coefficient": bearing_web_v3_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(a) (DRY: compute_bolt_hole_bearing_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_bearing_v2_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por aplastamiento en perforacion del perno de platina 1 (direccion 2)",
                    "clause": "AISC 360-22 J3.11a.(a)",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": case.geometry.t_plt_web.model_dump(),
                    "db_blt_web_var": "db_blt_web",
                    "db_blt_web": db_web.model_dump(),
                    "svc_hole_deformation_design_web_var": "deformation_at_bolt_hole_service_load_is_design",
                    "svc_hole_deformation_design_web": svc_hole_deformation_design_web,
                    "rn2_plt_v2_web_var": "Rn2_plt_v2_web",
                    "rn2_plt_v2_web_formula": (
                        "Rn2_plt_v2_web = 2.4*db_blt_web*t_plt_web*Fu_plt_web"
                        if svc_hole_deformation_design_web
                        else "Rn2_plt_v2_web = 3.0*db_blt_web*t_plt_web*Fu_plt_web"
                    ),
                    "rn2_plt_v2_web": rn2_plt_v2_web.model_dump() if isinstance(rn2_plt_v2_web, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "phi_rn2_plt_v2_web_var": "phi*Rn2_plt_v2_web",
                    "phi_rn2_plt_v2_web_formula": "phi*Rn2_plt_v2_web = phi_fragil*Rn2_plt_v2_web",
                    "phi_rn2_plt_v2_web": phi_rn2_plt_v2_web.model_dump(),
                    "ru2_plt_v2_web_var": "Ru2_plt_v2_web",
                    "ru2_plt_v2_web_formula": "Ru2_plt_v2_web = Ru_web_v2_max_vg",
                    "ru2_plt_v2_web": ru2_plt_v2_web.model_dump() if isinstance(ru2_plt_v2_web, Quantity) else None,
                    "dcr2_plt_v2_web_var": "DCR2_plt_v2_web",
                    "dcr2_plt_v2_web": dcr2_plt_v2_web,
                    "result2_plt_v2_web": result2_plt_v2_web,
                    "coefficient": bearing_plt1_web_inter.get("coefficient"),
                    "reference": "AISC 360-22 J3.11a.(a) (DRY: compute_bolt_hole_bearing_strength_j36)",
                },
                {
                    "id": "bbmb_splice.step4.web_tension_rupture_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por rotura a traccion de la viga en direccion 3",
                    "clause": "AISC 360-22 J4.1.(b)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "t_vg_var": "T_vg",
                    "t_vg": t_catalog.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "a_vg_var": "A_vg",
                    "a_vg_formula": "A_vg = d_vg*tw_vg",
                    "a_vg": a_vg_v3.model_dump(),
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "ant_v3_vg_var": "Ant_v3_vg",
                    "ant_v3_vg_formula": ant_v3_vg_formula,
                    "ant_v3_vg": ant_v3_vg.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "u_v3_vg_var": "U_v3_vg",
                    "u_v3_vg_formula": u_v3_vg_formula,
                    "u_v3_vg": u_v3_vg,
                    "ae_v3_vg_var": "Ae_v3_vg",
                    "ae_v3_vg_formula": "Ae_v3_vg = Ant_v3_vg*U_v3_vg",
                    "ae_v3_vg": ae_v3_vg.model_dump(),
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn3_v3_vg_var": "Rn3_v3_vg",
                    "rn3_v3_vg_formula": "Rn3_v3_vg = Fu_vg*Ae_v3_vg",
                    "rn3_v3_vg": rn3_v3_vg.model_dump() if isinstance(rn3_v3_vg, Quantity) else None,
                    "phi_rn3_v3_vg_var": "phi*Rn3_v3_vg",
                    "phi_rn3_v3_vg_formula": "phi*Rn3_v3_vg = phi_fragil*Rn3_v3_vg",
                    "phi_rn3_v3_vg": phi_rn3_v3_vg.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru3_v3_vg_var": "Ru3_v3_vg",
                    "ru3_v3_vg_formula": "Ru3_v3_vg = Pu_sp",
                    "ru3_v3_vg": ru3_v3_vg.model_dump() if isinstance(ru3_v3_vg, Quantity) else None,
                    "dcr3_v3_vg_var": "DCR3_v3_vg",
                    "dcr3_v3_vg": dcr3_v3_vg,
                    "result3_v3_vg": result3_v3_vg,
                    "reference": tension_rupture_v3_inter.get("reference"),
                },
                {
                    "id": "bbmb_splice.step4.web_block_shear_v3_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por bloque de cortante en alma de viga en direccion 3",
                    "clause": "AISC 360-22w J4.3",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "fy_vg_var": "Fy_vg",
                    "fy_vg": fy_vg.model_dump() if isinstance(fy_vg, Quantity) else None,
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "p_blt_web_var": "p_blt_web",
                    "p_blt_web": s1y.model_dump(),
                    "le_blt_web_x1_var": "Le_blt_web_x1",
                    "le_blt_web_x1": le1_x1.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "agv_web_v3_vg_var": "Agv_web_v3_vg",
                    "agv_web_v3_vg_formula": "Agv_web_v3_vg = 2*(g_blt_web*(n_blt_web_x - 1)*tw_vg + Le_blt_web_x1*tw_vg)",
                    "agv_web_v3_vg": agv_web_v3_vg.model_dump(),
                    "anv_web_v3_vg_var": "Anv_web_v3_vg",
                    "anv_web_v3_vg_formula": "Anv_web_v3_vg = 2*(0.5*Agv_web_v3_vg - (n_blt_web_x - 0.5)*tw_vg*(dh.1 + 1.80mm))",
                    "anv_web_v3_vg": anv_web_v3_vg.model_dump(),
                    "agt_web_v3_vg_var": "Agt_web_v3_vg",
                    "agt_web_v3_vg_formula": "Agt_web_v3_vg = p_blt_web*(n_blt_web_y - 1)*tw_vg",
                    "agt_web_v3_vg": agt_web_v3_vg.model_dump(),
                    "ant_web_v3_vg_var": "Ant_web_v3_vg",
                    "ant_web_v3_vg_formula": "Ant_web_v3_vg = Agt_web_v3_vg - (n_blt_web_y - 1)*tw_vg*(dh.1 + 1.80mm)",
                    "ant_web_v3_vg": ant_web_v3_vg.model_dump(),
                    "ubs_web_v3_vg_var": "Ubs_web_v3_vg",
                    "ubs_web_v3_vg": ubs_web_v3_vg,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn4_1_web_v3_vg_var": "Rn4_1_web_v3_vg",
                    "rn4_1_web_v3_vg_formula": "Rn4_1_web_v3_vg = 0.60*Fu_vg*Anv_web_v3_vg + Ubs_web_v3_vg*Fu_vg*Ant_web_v3_vg",
                    "rn4_1_web_v3_vg": rn4_1_web_v3_vg.model_dump() if isinstance(rn4_1_web_v3_vg, Quantity) else None,
                    "rn4_2_web_v3_vg_var": "Rn4_2_web_v3_vg",
                    "rn4_2_web_v3_vg_formula": "Rn4_2_web_v3_vg = 0.60*Fy_vg*Agv_web_v3_vg + Ubs_web_v3_vg*Fu_vg*Ant_web_v3_vg",
                    "rn4_2_web_v3_vg": rn4_2_web_v3_vg.model_dump() if isinstance(rn4_2_web_v3_vg, Quantity) else None,
                    "rn4_web_v3_vg_var": "Rn4_web_v3_vg",
                    "rn4_web_v3_vg_formula": "Rn4_web_v3_vg = min(Rn4_1_web_v3_vg, Rn4_2_web_v3_vg)",
                    "rn4_web_v3_vg": rn4_web_v3_vg.model_dump() if isinstance(rn4_web_v3_vg, Quantity) else None,
                    "phi_rn4_web_v3_vg_var": "phi*Rn4_web_v3_vg",
                    "phi_rn4_web_v3_vg_formula": "phi*Rn4_web_v3_vg = phi_fragil*Rn4_web_v3_vg",
                    "phi_rn4_web_v3_vg": phi_rn4_web_v3_vg.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru4_web_v3_vg_var": "Ru4_web_v3_vg",
                    "ru4_web_v3_vg_formula": "Ru4_web_v3_vg = Pu_sp*alpha_Pu_web",
                    "ru4_web_v3_vg": ru4_web_v3_vg.model_dump(),
                    "dcr4_web_v3_vg_var": "DCR4_web_v3_vg",
                    "dcr4_web_v3_vg": dcr4_web_v3_vg,
                    "result4_web_v3_vg": result4_web_v3_vg,
                    "controlling": block_shear_web_v3_inter.get("controlling"),
                    "reference": block_shear_web_v3_inter.get("reference"),
                },
                {
                    "id": "bbmb_splice.step4.web_bolt_shear_rupture_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por rotura a cortante en el perno",
                    "clause": "AISC 360-22 J3.7",
                    "db_blt_web_var": "db_blt_web",
                    "db_blt_web": db_web.model_dump(),
                    "ab_blt_web_var": "Ab_blt_web",
                    "ab_blt_web": (
                        bolt_shear_web.get("bolt_area").model_dump()
                        if isinstance(bolt_shear_web, dict) and isinstance(bolt_shear_web.get("bolt_area"), Quantity)
                        else None
                    ),
                    "fnv_blt_web_var": "Fnv_blt_web",
                    "fnv_blt_web": fnv_web.model_dump() if isinstance(fnv_web, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn3_web_v2_vg_var": "Rn3_web_v2_vg",
                    "rn3_web_v2_vg_formula": "Rn3_web_v2_vg = Ab_blt_web*Fnv_blt_web",
                    "rn3_web_v2_vg": (
                        bolt_shear_web.get("rnv_b").model_dump()
                        if isinstance(bolt_shear_web, dict) and isinstance(bolt_shear_web.get("rnv_b"), Quantity)
                        else None
                    ),
                    "phi_rn3_web_v2_vg_var": "phi*Rn3_web_v2_vg",
                    "phi_rn3_web_v2_vg_formula": "phi*Rn3_web_v2_vg = phi_fragil*Rn3_web_v2_vg",
                    "phi_rn3_web_v2_vg": (
                        bolt_shear_web.get("phi_rnv_b").model_dump()
                        if isinstance(bolt_shear_web, dict) and isinstance(bolt_shear_web.get("phi_rnv_b"), Quantity)
                        else None
                    ),
                    "reference": (bolt_shear_web.get("reference") if isinstance(bolt_shear_web, dict) else "AISC 360-22 Section J3.7"),
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_bolt_shear_rupture_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por rotura a cortante en el perno de platina 1",
                    "clause": "AISC 360-22 J3.7",
                    "db_blt_web_var": "db_blt_web",
                    "db_blt_web": db_web.model_dump(),
                    "ab_blt_web_var": "Ab_blt_web",
                    "ab_blt_web": (
                        bolt_shear_web.get("bolt_area").model_dump()
                        if isinstance(bolt_shear_web, dict) and isinstance(bolt_shear_web.get("bolt_area"), Quantity)
                        else None
                    ),
                    "fnv_blt_web_var": "Fnv_blt_web",
                    "fnv_blt_web": fnv_web.model_dump() if isinstance(fnv_web, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn3_plt_v2_v3_web_var": "Rn3_plt_v2-v3_web",
                    "rn3_plt_v2_v3_web_formula": "Rn3_plt_v2-v3_web = Ab_blt_web*Fnv_blt_web",
                    "rn3_plt_v2_v3_web": (
                        bolt_shear_web.get("rnv_b").model_dump()
                        if isinstance(bolt_shear_web, dict) and isinstance(bolt_shear_web.get("rnv_b"), Quantity)
                        else None
                    ),
                    "phi_rn3_plt_v2_v3_web_var": "phi*Rn3_plt_v2-v3_web",
                    "phi_rn3_plt_v2_v3_web_formula": "phi*Rn3_plt_v2-v3_web = phi_fragil*Rn3_plt_v2-v3_web",
                    "phi_rn3_plt_v2_v3_web": (
                        bolt_shear_web.get("phi_rnv_b").model_dump()
                        if isinstance(bolt_shear_web, dict) and isinstance(bolt_shear_web.get("phi_rnv_b"), Quantity)
                        else None
                    ),
                    "reference": "AISC 360-22 J3.7 (DRY: compute_bolt_shear_rupture_capacity_per_bolt)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_block_shear_v2_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por bloque de cortante en platina 1 de alma en direccion 2",
                    "clause": "AISC 360-22w J4.3",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "p_plt_web_var": "p_plt_web",
                    "p_plt_web": s1y.model_dump(),
                    "le_plt_web_x2_var": "Le_plt_web_x2",
                    "le_plt_web_x2": le1_x2.model_dump(),
                    "le_plt_web_y1_var": "Le_plt_web_y1",
                    "le_plt_web_y1": le1_y1.model_dump(),
                    "le_plt_web_y2_var": "Le_plt_web_y2",
                    "le_plt_web_y2": le1_y2.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "agv_plt_v2_web_var": "Agv_plt_v2_web",
                    "agv_plt_v2_web_formula": "Agv_plt_v2_web = (p_plt_web*(n_blt_web_y - 1) + min(Le_plt_web_y1, Le_plt_web_y2))*t_plt_web",
                    "agv_plt_v2_web": agv_plt_v2_web.model_dump(),
                    "anv_plt_v2_web_var": "Anv_plt_v2_web",
                    "anv_plt_v2_web_formula": "Anv_plt_v2_web = Agv_plt_v2_web - (n_blt_web_y - 0.5)*t_plt_web*(dh.1 + 1.80mm)",
                    "anv_plt_v2_web": anv_plt_v2_web.model_dump(),
                    "agt_plt_v2_web_var": "Agt_plt_v2_web",
                    "agt_plt_v2_web_formula": "Agt_plt_v2_web = (g_blt_web*(n_blt_web_x - 1) + Le_plt_web_x2)*t_plt_web",
                    "agt_plt_v2_web": agt_plt_v2_web.model_dump(),
                    "ant_plt_v2_web_var": "Ant_plt_v2_web",
                    "ant_plt_v2_web_formula": "Ant_plt_v2_web = Agt_plt_v2_web - (n_blt_web_x - 0.5)*t_plt_web*(dh.1 + 1.80mm)",
                    "ant_plt_v2_web": ant_plt_v2_web.model_dump(),
                    "ubs_plt_v2_web_var": "Ubs_plt_v2_web",
                    "ubs_plt_v2_web": ubs_plt_v2_web,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn4_1_plt_v2_web_var": "Rn4_1_plt_v2_web",
                    "rn4_1_plt_v2_web_formula": "Rn4_1_plt_v2_web = 0.60*Fu_plt_web*Anv_plt_v2_web + Ubs_plt_v2_web*Fu_plt_web*Ant_plt_v2_web",
                    "rn4_1_plt_v2_web": rn4_1_plt_v2_web.model_dump() if isinstance(rn4_1_plt_v2_web, Quantity) else None,
                    "rn4_2_plt_v2_web_var": "Rn4_2_plt_v2_web",
                    "rn4_2_plt_v2_web_formula": "Rn4_2_plt_v2_web = 0.60*Fy_plt_web*Agv_plt_v2_web + Ubs_plt_v2_web*Fu_plt_web*Ant_plt_v2_web",
                    "rn4_2_plt_v2_web": rn4_2_plt_v2_web.model_dump() if isinstance(rn4_2_plt_v2_web, Quantity) else None,
                    "rn4_plt_v2_web_var": "Rn4_plt_v2_web",
                    "rn4_plt_v2_web_formula": "Rn4_plt_v2_web = min(Rn4_1_plt_v2_web, Rn4_2_plt_v2_web)",
                    "rn4_plt_v2_web": rn4_plt_v2_web.model_dump() if isinstance(rn4_plt_v2_web, Quantity) else None,
                    "phi_rn4_plt_v2_web_var": "phi*Rn4_plt_v2_web",
                    "phi_rn4_plt_v2_web_formula": "phi*Rn4_plt_v2_web = phi_fragil*Rn4_plt_v2_web",
                    "phi_rn4_plt_v2_web": phi_rn4_plt_v2_web.model_dump(),
                    "ru4_plt_v2_web_var": "Ru4_plt_v2_web",
                    "ru4_plt_v2_web_formula": "Ru4_plt_v2_web = Vu2_sp",
                    "ru4_plt_v2_web": ru4_plt_v2_web.model_dump() if isinstance(ru4_plt_v2_web, Quantity) else None,
                    "dcr4_plt_v2_web_var": "DCR4_plt_v2_web",
                    "dcr4_plt_v2_web": dcr4_plt_v2_web,
                    "result4_plt_v2_web": result4_plt_v2_web,
                    "controlling": block_shear_plt1_inter.get("controlling"),
                    "reference": "AISC 360-22w J4.3 (DRY: compute_block_shear_strength_j45)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_block_shear_v3_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por bloque de cortante en platina 1 de alma en direccion 3",
                    "clause": "AISC 360-22 J4-5",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "p_blt_web_var": "p_blt_web",
                    "p_blt_web": s1y.model_dump(),
                    "le_blt_web_x2_var": "Le_blt_web_x2",
                    "le_blt_web_x2": le1_x2.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "agv_plt_v3_web_var": "Agv_plt_v3_web",
                    "agv_plt_v3_web_formula": "Agv_plt_v3_web = 2*(g_blt_web*(n_blt_web_x - 1)*t_plt_web + Le_blt_web_x2*t_plt_web)",
                    "agv_plt_v3_web": agv_plt_v3_web.model_dump(),
                    "anv_plt_v3_web_var": "Anv_plt_v3_web",
                    "anv_plt_v3_web_formula": "Anv_plt_v3_web = 2*(0.5*Agv_plt_v3_web - (n_blt_web_x - 0.5)*t_plt_web*(dh.1 + 1.80mm))",
                    "anv_plt_v3_web": anv_plt_v3_web.model_dump(),
                    "agt_plt_v3_web_var": "Agt_plt_v3_web",
                    "agt_plt_v3_web_formula": "Agt_plt_v3_web = p_blt_web*(n_blt_web_y - 1)*t_plt_web",
                    "agt_plt_v3_web": agt_plt_v3_web.model_dump(),
                    "ant_plt_v3_web_var": "Ant_plt_v3_web",
                    "ant_plt_v3_web_formula": "Ant_plt_v3_web = Agt_plt_v3_web - (n_blt_web_y - 1)*t_plt_web*(dh.1 + 1.80mm)",
                    "ant_plt_v3_web": ant_plt_v3_web.model_dump(),
                    "ubs_plt_v3_web_var": "Ubs_plt_v3_web",
                    "ubs_plt_v3_web_formula": "Ubs_plt_v3_web = Ubs_web_v3_vg",
                    "ubs_plt_v3_web": ubs_plt_v3_web,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn2_1_plt_v3_web_var": "Rn2_1_plt_v3_web",
                    "rn2_1_plt_v3_web_formula": "Rn2_1_plt_v3_web = 0.60*Fu_plt_web*Anv_plt_v3_web + Ubs_plt_v3_web*Fu_plt_web*Ant_plt_v3_web",
                    "rn2_1_plt_v3_web": rn2_1_plt_v3_web.model_dump() if isinstance(rn2_1_plt_v3_web, Quantity) else None,
                    "rn2_2_plt_v3_web_var": "Rn2_2_plt_v3_web",
                    "rn2_2_plt_v3_web_formula": "Rn2_2_plt_v3_web = 0.60*Fy_plt_web*Agv_plt_v3_web + Ubs_plt_v3_web*Fu_plt_web*Ant_plt_v3_web",
                    "rn2_2_plt_v3_web": rn2_2_plt_v3_web.model_dump() if isinstance(rn2_2_plt_v3_web, Quantity) else None,
                    "rn2_plt_v3_web_var": "Rn2_plt_v3_web",
                    "rn2_plt_v3_web_formula": "Rn2_plt_v3_web = min(Rn2_1_plt_v3_web, Rn2_2_plt_v3_web)",
                    "rn2_plt_v3_web": rn2_plt_v3_web.model_dump() if isinstance(rn2_plt_v3_web, Quantity) else None,
                    "phi_rn2_plt_v3_web_var": "phi*Rn2_plt_v3_web",
                    "phi_rn2_plt_v3_web_formula": "phi*Rn2_plt_v3_web = phi_fragil*Rn2_plt_v3_web",
                    "phi_rn2_plt_v3_web": phi_rn2_plt_v3_web.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru2_plt_v3_web_var": "Ru2_plt_v3_web",
                    "ru2_plt_v3_web_formula": "Ru2_plt_v3_web = Pu_sp*alpha_Pu_web",
                    "ru2_plt_v3_web": ru2_plt_v3_web.model_dump() if isinstance(ru2_plt_v3_web, Quantity) else None,
                    "dcr2_plt_v3_web_var": "DCR2_plt_v3_web",
                    "dcr2_plt_v3_web": dcr2_plt_v3_web,
                    "result2_plt_v3_web": result2_plt_v3_web,
                    "controlling": block_shear_plt1_v3_inter.get("controlling"),
                    "reference": "AISC 360-22 J4-5 (DRY: compute_block_shear_strength_j45)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_tension_yielding_v3_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por fluencia a traccion en platina 1 de alma en direccion 3",
                    "clause": "AISC 360-22 J4.1(a)",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "h_plt_web_var": "H_plt_web",
                    "h_plt_web": hp1.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "p_blt_web_var": "p_blt_web",
                    "p_blt_web": s1y.model_dump(),
                    "agt_v3_plt_web_expr_var": "Agt_v3_plt_web_expr",
                    "agt_v3_plt_web_expr_formula": "Agt_v3_plt_web_expr = 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web",
                    "agt_v3_plt_web_expr": Quantity(value=agt_v3_plt_web_expr, unit=s1y.unit).model_dump(),
                    "agt_v3_plt_web_var": "Agt_v3_plt_web",
                    "agt_v3_plt_web_formula": "Agt_v3_plt_web = min(H_plt_web, Agt_v3_plt_web_expr)*t_plt_web",
                    "agt_v3_plt_web": agt_v3_plt_web.model_dump(),
                    "phi_no_ductil_var": "phi_no_ductil",
                    "phi_no_ductil": phi_no_ductil_plt,
                    "rn3_plt_v3_web_var": "Rn3_plt_v3_web",
                    "rn3_plt_v3_web_formula": "Rn3_plt_v3_web = Fy_plt_web*Agt_v3_plt_web",
                    "rn3_plt_v3_web": rn3_plt_v3_web.model_dump() if isinstance(rn3_plt_v3_web, Quantity) else None,
                    "phi_rn3_plt_v3_web_var": "phi*Rn3_plt_v3_web",
                    "phi_rn3_plt_v3_web_formula": "phi*Rn3_plt_v3_web = phi_no_ductil*Rn3_plt_v3_web",
                    "phi_rn3_plt_v3_web": phi_rn3_plt_v3_web.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru3_plt_v3_web_var": "Ru3_plt_v3_web",
                    "ru3_plt_v3_web_formula": "Ru3_plt_v3_web = alpha_Pu_web*Pu_sp",
                    "ru3_plt_v3_web": ru3_plt_v3_web.model_dump() if isinstance(ru3_plt_v3_web, Quantity) else None,
                    "dcr3_plt_v3_web_var": "DCR3_plt_v3_web",
                    "dcr3_plt_v3_web": dcr3_plt_v3_web,
                    "result3_plt_v3_web": result3_plt_v3_web,
                    "reference": "AISC 360-22 J4.1(a) (DRY: compute_element_tension_yielding_strength_j41a)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_tension_rupture_v3_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por rotura a traccion en platina 1 de alma en direccion 3",
                    "clause": "AISC 360-22 J4.1(b)",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "h_plt_web_var": "H_plt_web",
                    "h_plt_web": hp1.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "p_blt_web_var": "p_blt_web",
                    "p_blt_web": s1y.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "agt_v3_plt_web_expr_var": "Agt_v3_plt_web_expr",
                    "agt_v3_plt_web_expr_formula": "Agt_v3_plt_web_expr = 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web",
                    "agt_v3_plt_web_expr": Quantity(value=agt_v3_plt_web_expr, unit=s1y.unit).model_dump(),
                    "agt_v3_plt_web_var": "Agt_v3_plt_web",
                    "agt_v3_plt_web_formula": "Agt_v3_plt_web = min(H_plt_web, Agt_v3_plt_web_expr)*t_plt_web",
                    "agt_v3_plt_web": agt_v3_plt_web.model_dump(),
                    "ant_v3_plt_web_var": "Ant_v3_plt_web",
                    "ant_v3_plt_web_formula": "Ant_v3_plt_web = Agt_v3_plt_web - n_blt_web_y*(dh.1 + 1.80mm)*t_plt_web",
                    "ant_v3_plt_web": ant_v3_plt_web.model_dump(),
                    "u_v3_plt_web_var": "U_v3_plt_web",
                    "u_v3_plt_web": u_v3_plt_web,
                    "ae_v3_plt_web_var": "Ae_v3_plt_web",
                    "ae_v3_plt_web_formula": "Ae_v3_plt_web = Ant_v3_plt_web*U_v3_plt_web",
                    "ae_v3_plt_web": ae_v3_plt_web.model_dump(),
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn4_plt_v3_web_var": "Rn4_plt_v3_web",
                    "rn4_plt_v3_web_formula": "Rn4_plt_v3_web = Fu_plt_web*Ae_v3_plt_web",
                    "rn4_plt_v3_web": rn4_plt_v3_web.model_dump() if isinstance(rn4_plt_v3_web, Quantity) else None,
                    "phi_rn4_plt_v3_web_var": "phi*Rn4_plt_v3_web",
                    "phi_rn4_plt_v3_web_formula": "phi*Rn4_plt_v3_web = phi_fragil*Rn4_plt_v3_web",
                    "phi_rn4_plt_v3_web": phi_rn4_plt_v3_web.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru4_plt_v3_web_var": "Ru4_plt_v3_web",
                    "ru4_plt_v3_web_formula": "Ru4_plt_v3_web = alpha_Pu_web*Pu_sp",
                    "ru4_plt_v3_web": ru4_plt_v3_web.model_dump() if isinstance(ru4_plt_v3_web, Quantity) else None,
                    "dcr4_plt_v3_web_var": "DCR4_plt_v3_web",
                    "dcr4_plt_v3_web": dcr4_plt_v3_web,
                    "result4_plt_v3_web": result4_plt_v3_web,
                    "reference": "AISC 360-22 J4.1(b) (DRY: compute_element_tension_rupture_strength_j41b)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_comp_buckling_p3_minus_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por pandeo en compresion por flexion en platina 1 de alma",
                    "clause": "AISC 360-22 E3 y J4.4 (formulacion DRY)",
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if isinstance(fy_plt_web, Quantity) else None,
                    "h_plt_web_var": "H_plt_web",
                    "h_plt_web": hp1.model_dump(),
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "gap_sp_var": "gap_sp",
                    "gap_sp": alpha.model_dump(),
                    "le_blt_web_x1_var": "Le_blt_web_x1",
                    "le_blt_web_x1": le1_x1.model_dump(),
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "lp_plt_p3_minus_web_var": "Lp_plt_p3(-)_web",
                    "lp_plt_p3_minus_web_formula": "Lp_plt_p3(-)_web = min(gap_sp + 2*Le_blt_web_x1, g_blt_web)",
                    "lp_plt_p3_minus_web": lp_plt_p3_minus_web.model_dump(),
                    "plate_count_n_var": "n_plt_web",
                    "plate_count_n": 1,
                    "phi_no_ductil_var": "phi_no_ductil",
                    "phi_no_ductil": phi_no_ductil_flex,
                    "k_factor_var": "K",
                    "k_factor": 0.65,
                    "radius_var": "r_plt_p3(-)_web",
                    "radius": pminus_plt1_inter.get("radius").model_dump()
                    if isinstance(pminus_plt1_inter.get("radius"), Quantity)
                    else None,
                    "klr_var": "KL_r_plt_p3(-)_web",
                    "klr": pminus_plt1_inter.get("klr"),
                    "fe_var": "Fe_plt_p3(-)_web",
                    "fe": pminus_plt1_inter.get("elastic_buckling_stress").model_dump()
                    if isinstance(pminus_plt1_inter.get("elastic_buckling_stress"), Quantity)
                    else None,
                    "fcr_var": "Fcr_plt_p3(-)_web",
                    "fcr": pminus_plt1_inter.get("critical_stress").model_dump()
                    if isinstance(pminus_plt1_inter.get("critical_stress"), Quantity)
                    else None,
                    "fcr_equation": pminus_plt1_inter.get("critical_stress_equation"),
                    "area_gross_var": "Ag_plt_p3(-)_web",
                    "area_gross": pminus_plt1_inter.get("gross_area").model_dump()
                    if isinstance(pminus_plt1_inter.get("gross_area"), Quantity)
                    else None,
                    "phi_rn1_plt_p3_minus_web_var": "phi*Rn1_plt_p3(-)_web",
                    "phi_rn1_plt_p3_minus_web_formula": "phi*Rn1_plt_p3(-)_web = phi*Fcr_plt_p3(-)_web*H_plt_web*t_plt_web*n_plt_web",
                    "phi_rn1_plt_p3_minus_web": phi_rn1_plt_p3_minus_web.model_dump()
                    if isinstance(phi_rn1_plt_p3_minus_web, Quantity)
                    else None,
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru1_plt_p3_minus_web_var": "Ru1_plt_p3(-)_web",
                    "ru1_plt_p3_minus_web_formula": "Ru1_plt_p3(-)_web = si Pu_sp < 0 -> alpha_Pu_web*Pu_sp; si Pu_sp >= 0 -> 0",
                    "ru1_plt_p3_minus_web": ru1_plt_p3_minus_web.model_dump()
                    if isinstance(ru1_plt_p3_minus_web, Quantity)
                    else None,
                    "dcr1_plt_p3_minus_web_var": "DCR1_plt_p3(-)_web",
                    "dcr1_plt_p3_minus_web": dcr1_plt_p3_minus_web,
                    "result1_plt_p3_minus_web": result1_plt_p3_minus_web,
                    "reference": "DRY: compute_plate_compression_buckling_strength",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_flex_yielding_m1_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por fluencia a flexion en platina 1 de alma alrededor de 1",
                    "clause": "AISC 360-22 F11.1",
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if isinstance(fy_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "h_plt_web_var": "H_plt_web",
                    "h_plt_web": h_plt_web.model_dump(),
                    "z_plt_m1_web_var": "Z_plt_m1_web",
                    "z_plt_m1_web_formula": "Z_plt_m1_web = t_plt_web*H_plt_web^2/4",
                    "z_plt_m1_web": z_plt_m1_web.model_dump(),
                    "s_plt_m1_web_var": "S_plt_m1_web",
                    "s_plt_m1_web_formula": "S_plt_m1_web = t_plt_web*H_plt_web^2/6",
                    "s_plt_m1_web": s_plt_m1_web.model_dump(),
                    "ex_blt_web_var": "ex_blt_web",
                    "ex_blt_web_formula": "ex_blt_web = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web",
                    "ex_blt_web": ex_blt_web.model_dump(),
                    "ey_blt_web_var": "ey_blt_web",
                    "ey_blt_web": ey_blt_web.model_dump(),
                    "phi_no_ductil_var": "phi_no_ductil",
                    "phi_no_ductil": phi_no_ductil_flex,
                    "mn1_plt_m1_web_var": "Rn1_plt_m1_web",
                    "mn1_plt_m1_web_formula": "Rn1_plt_m1_web = min(Fy_plt_web*Z_plt_m1_web, 1.5*Fy_plt_web*S_plt_m1_web)",
                    "mn1_plt_m1_web": rn1_plt_m1_web.model_dump() if isinstance(rn1_plt_m1_web, Quantity) else None,
                    "phi_mn1_plt_m1_web_var": "phi*Rn1_plt_m1_web",
                    "phi_mn1_plt_m1_web_formula": "phi*Rn1_plt_m1_web = phi_no_ductil*Rn1_plt_m1_web",
                    "phi_mn1_plt_m1_web": phi_rn1_plt_m1_web.model_dump(),
                    "vu2_sp_var": "Vu2_sp",
                    "vu2_sp": case.loads.Vu2_sp.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru1_plt_m1_web_var": "Ru1_plt_m1_web",
                    "ru1_plt_m1_web_formula": "Ru1_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web",
                    "ru1_plt_m1_web": ru1_plt_m1_web.model_dump(),
                    "dcr1_plt_m1_web_var": "DCR1_plt_m1_web",
                    "dcr1_plt_m1_web": dcr1_plt_m1_web,
                    "result1_plt_m1_web": result1_plt_m1_web,
                    "controlling": flex_yield_plt1_inter.get("controlling"),
                    "reference": "AISC 360-22 F11.1 (DRY: compute_rectangular_bar_flexural_yielding_strength_f111)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_ltb_m1_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por pandeo lateral-torsional en platina 1 de alma alrededor de 1",
                    "clause": "AISC 360-22 F11.2",
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if isinstance(fy_plt_web, Quantity) else None,
                    "e_plt_web_var": "E_plt_web",
                    "e_plt_web": e_plt_web.model_dump() if isinstance(e_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "h_plt_web_var": "H_plt_web",
                    "h_plt_web": h_plt_web.model_dump(),
                    "z_plt_m1_web_var": "Z_plt_m1_web",
                    "z_plt_m1_web_formula": "Z_plt_m1_web = t_plt_web*H_plt_web^2/4",
                    "z_plt_m1_web": z_plt_m1_web.model_dump(),
                    "s_plt_m1_web_var": "S_plt_m1_web",
                    "s_plt_m1_web_formula": "S_plt_m1_web = t_plt_web*H_plt_web^2/6",
                    "s_plt_m1_web": s_plt_m1_web.model_dump(),
                    "lb_plt_m1_web_var": "Lb_plt_m1_web",
                    "lb_plt_m1_web_formula": "Lb_plt_m1_web = max(2*Le_blt_web_x1 + gap_sp, g_plt_web)",
                    "lb_plt_m1_web": lb_plt_m1_web.model_dump(),
                    "my_plt_m1_web_var": "My_plt_m1_web",
                    "my_plt_m1_web_formula": "My_plt_m1_web = Fy_plt_web*S_plt_m1_web",
                    "my_plt_m1_web": my_plt_m1_web.model_dump(),
                    "cb_plt_m1_web_var": "Cb_plt_m1_web",
                    "cb_plt_m1_web": cb_plt_m1_web,
                    "phi_no_ductil_var": "phi_no_ductil",
                    "phi_no_ductil": phi_no_ductil_flex,
                    "mn2_plt_m1_web_var": "Rn2_plt_m1_web",
                    "mn2_plt_m1_web_formula": "Rn2_plt_m1_web = Mn_ltb(F11.2) <= Mp",
                    "mn2_plt_m1_web": rn2_plt_m1_web.model_dump() if isinstance(rn2_plt_m1_web, Quantity) else None,
                    "phi_mn2_plt_m1_web_var": "phi*Rn2_plt_m1_web",
                    "phi_mn2_plt_m1_web_formula": "phi*Rn2_plt_m1_web = phi_no_ductil*Rn2_plt_m1_web",
                    "phi_mn2_plt_m1_web": phi_rn2_plt_m1_web.model_dump(),
                    "ltb_case_id": ltb_plt1_inter.get("case_id"),
                    "lb_d_over_t2": ltb_plt1_inter.get("lb_d_over_t2"),
                    "limit_a_0p08e_over_fy": ltb_plt1_inter.get("limit_a_0p08e_over_fy"),
                    "limit_b_1p9e_over_fy": ltb_plt1_inter.get("limit_b_1p9e_over_fy"),
                    "fcr": ltb_plt1_inter.get("fcr").model_dump() if isinstance(ltb_plt1_inter.get("fcr"), Quantity) else None,
                    "ex_blt_web_var": "ex_blt_web",
                    "ex_blt_web": ex_blt_web.model_dump(),
                    "ey_blt_web_var": "ey_blt_web",
                    "ey_blt_web": ey_blt_web.model_dump(),
                    "vu2_sp_var": "Vu2_sp",
                    "vu2_sp": case.loads.Vu2_sp.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru2_plt_m1_web_var": "Ru2_plt_m1_web",
                    "ru2_plt_m1_web_formula": "Ru2_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web",
                    "ru2_plt_m1_web": ru2_plt_m1_web.model_dump(),
                    "dcr2_plt_m1_web_var": "DCR2_plt_m1_web",
                    "dcr2_plt_m1_web": dcr2_plt_m1_web,
                    "result2_plt_m1_web": result2_plt_m1_web,
                    "reference": "AISC 360-22 F11.2 (DRY: compute_rectangular_bar_ltb_strength_f112)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_flex_rupture_m1_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por rotura a flexion en platina 1 de alma alrededor de 1",
                    "clause": "AISC 360-22 J5.5",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "tp_plt_m1_web_var": "tp",
                    "tp_plt_m1_web": t_plt_web.model_dump(),
                    "h_plt_m1_web_var": "h",
                    "h_plt_m1_web": h_plt_web.model_dump(),
                    "d_prime_plt_m1_web_var": "d'",
                    "d_prime_plt_m1_web_formula": "d' = dh.1 + 1.80mm",
                    "d_prime_plt_m1_web": d_prime_plt_m1_web.model_dump(),
                    "e1_plt_m1_web_var": "e1",
                    "e1_plt_m1_web": le1_y1.model_dump(),
                    "e2_plt_m1_web_var": "e2",
                    "e2_plt_m1_web": le1_y2.model_dump(),
                    "s_plt_m1_web_var": "s",
                    "s_plt_m1_web": s1y.model_dump(),
                    "n_plt_web_y_var": "n",
                    "n_plt_web_y": n_plt_web_y,
                    "h_formula_var": "h",
                    "h_formula": "h = e1 + (n - 1)*s + e2",
                    "h_calc_plt_m1_web": h_calc_plt_m1_web.model_dump() if isinstance(h_calc_plt_m1_web, Quantity) else None,
                    "sum_abs_plt_m1_web_var": "sum_abs",
                    "sum_abs_plt_m1_web_formula": "sum_abs = sum_{i=0}^{n-1}|e1 + i*s - h/2|",
                    "sum_abs_plt_m1_web": sum_abs_plt_m1_web.model_dump() if isinstance(sum_abs_plt_m1_web, Quantity) else None,
                    "z_net_plt_m1_web_var": "Znet_plt_m1_web",
                    "z_net_plt_m1_web_formula": "Znet_plt_m1_web = tp*h^2/4 - d'*tp*sum_abs",
                    "z_net_plt_m1_web": z_net_plt_m1_web.model_dump() if isinstance(z_net_plt_m1_web, Quantity) else None,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn3_plt_m1_web_var": "Rn3_plt_m1_web",
                    "rn3_plt_m1_web_formula": "Rn3_plt_m1_web = Fu_plt_web*Znet_plt_m1_web",
                    "rn3_plt_m1_web": rn3_plt_m1_web.model_dump() if isinstance(rn3_plt_m1_web, Quantity) else None,
                    "phi_rn3_plt_m1_web_var": "phi*Rn3_plt_m1_web",
                    "phi_rn3_plt_m1_web_formula": "phi*Rn3_plt_m1_web = phi_fragil*Rn3_plt_m1_web",
                    "phi_rn3_plt_m1_web": phi_rn3_plt_m1_web.model_dump(),
                    "ex_blt_web_var": "ex_blt_web",
                    "ex_blt_web": ex_blt_web.model_dump(),
                    "ey_blt_web_var": "ey_blt_web",
                    "ey_blt_web": ey_blt_web.model_dump(),
                    "vu2_sp_var": "Vu2_sp",
                    "vu2_sp": case.loads.Vu2_sp.model_dump(),
                    "pu_sp_var": "Pu_sp",
                    "pu_sp": case.loads.Pu_sp.model_dump(),
                    "alpha_pu_web_var": "alpha_Pu_web",
                    "alpha_pu_web": case.loads.alpha_Pu_web,
                    "ru3_plt_m1_web_var": "Ru3_plt_m1_web",
                    "ru3_plt_m1_web_formula": "Ru3_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web",
                    "ru3_plt_m1_web": ru3_plt_m1_web.model_dump(),
                    "dcr3_plt_m1_web_var": "DCR3_plt_m1_web",
                    "dcr3_plt_m1_web": dcr3_plt_m1_web,
                    "result3_plt_m1_web": result3_plt_m1_web,
                    "reference": "AISC 360-22 J5.5 (DRY: compute_rectangular_bar_net_flexural_rupture_strength_j55)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_combined_forces_note",
                    "scope": "platina_1",
                    "description": "Revision de capacidad bajo accion de fuerzas combinadas en la platina 1 de alma",
                    "clause": "Criterio de interaccion solicitado por usuario (DRY)",
                    "dcr_plt_v2_web_var": "DCR_plt_v2_web",
                    "dcr_plt_v2_web": dcr_plt_v2_web,
                    "dcr_plt_v3_web_var": "DCR_plt_v3_web",
                    "dcr_plt_v3_web": dcr_plt_v3_web,
                    "dcr_plt_p3_minus_web_var": "DCR_plt_p3(-)_web",
                    "dcr_plt_p3_minus_web": dcr_plt_p3_minus_web,
                    "dcr_plt_m1_web_var": "DCR_plt_m1_web",
                    "dcr_plt_m1_web": dcr_plt_m1_web,
                    "dcr_case_1_var": "DCR_case_1",
                    "dcr_case_1_formula": "DCR_case_1 = DCR_plt_m1_web + (DCR_plt_v3_web)^2 + (DCR_plt_v2_web)^4",
                    "dcr_case_1": dcr_case_1_plt_fcomb_web,
                    "dcr_case_2_var": "DCR_case_2",
                    "dcr_case_2_formula": "DCR_case_2 = DCR_plt_m1_web + (DCR_plt_p3(-)_web)^2 + (DCR_plt_v2_web)^4",
                    "dcr_case_2": dcr_case_2_plt_fcomb_web,
                    "dcr_plt_fcomb_web_var": "DCR_plt_Fcomb_web",
                    "dcr_plt_fcomb_web_formula": "DCR_plt_Fcomb_web = max(DCR_case_1, DCR_case_2)",
                    "dcr_plt_fcomb_web": dcr_plt_fcomb_web,
                    "controlling_case": fcomb_controlling_case,
                    "result_plt_fcomb_web": result_plt_fcomb_web,
                    "reference": "DRY: compute_plate_combined_force_interaction",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_shear_yielding_v2_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por fluencia a cortante en la platina 1 de alma",
                    "clause": "AISC 360-22 J4.2(a)",
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if isinstance(fy_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": t_plt_web.model_dump(),
                    "n_plt_web_y_var": "n_plt_web_y",
                    "n_plt_web_y": case.geometry.n_blt_web_y,
                    "p_plt_web_var": "p_plt_web",
                    "p_plt_web": s1y.model_dump(),
                    "le_plt_web_y1_var": "Le_plt_web_y1",
                    "le_plt_web_y1": le1_y1.model_dump(),
                    "le_plt_web_y2_var": "Le_plt_web_y2",
                    "le_plt_web_y2": le1_y2.model_dump(),
                    "agv_plt_v2_web_var": "Agv_plt_v2_web",
                    "agv_plt_v2_web_formula": "Agv_plt_v2_web = (p_plt_web*(n_plt_web_y - 1) + Le_plt_web_y1 + Le_plt_web_y2)*t_plt_web",
                    "agv_plt_v2_web": agv5_plt_v2_web.model_dump(),
                    "phi_ductil_var": "phi_ductil",
                    "phi_ductil": phi_ductil_plt,
                    "rn5_plt_v2_web_var": "Rn5_plt_v2_web",
                    "rn5_plt_v2_web_formula": "Rn5_plt_v2_web = 0.60*Fy_plt_web*Agv_plt_v2_web",
                    "rn5_plt_v2_web": rn5_plt_v2_web.model_dump() if isinstance(rn5_plt_v2_web, Quantity) else None,
                    "phi_rn5_plt_v2_web_var": "phi*Rn5_plt_v2_web",
                    "phi_rn5_plt_v2_web_formula": "phi*Rn5_plt_v2_web = phi_ductil*Rn5_plt_v2_web",
                    "phi_rn5_plt_v2_web": phi_rn5_plt_v2_web.model_dump(),
                    "ru5_plt_v2_web_var": "Ru5_plt_v2_web",
                    "ru5_plt_v2_web_formula": "Ru5_plt_v2_web = Vu2_sp",
                    "ru5_plt_v2_web": ru5_plt_v2_web.model_dump() if isinstance(ru5_plt_v2_web, Quantity) else None,
                    "dcr5_plt_v2_web_var": "DCR5_plt_v2_web",
                    "dcr5_plt_v2_web": dcr5_plt_v2_web,
                    "result5_plt_v2_web": result5_plt_v2_web,
                    "reference": "AISC 360-22 J4.2(a) (DRY: compute_element_shear_yielding_strength_j42a)",
                },
                {
                    "id": "bbmb_splice.step5.plt1_web_shear_rupture_v2_note",
                    "scope": "platina_1",
                    "description": "Revision de resistencia por rotura a cortante en la platina 1 de alma",
                    "clause": "AISC 360-22 J4.2(b)",
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if isinstance(fu_plt_web, Quantity) else None,
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": case.geometry.t_plt_web.model_dump(),
                    "n_plt_web_y_var": "n_plt_web_y",
                    "n_plt_web_y": case.geometry.n_blt_web_y,
                    "p_plt_web_var": "p_plt_web",
                    "p_plt_web": s1y.model_dump(),
                    "le_plt_web_y1_var": "Le_plt_web_y1",
                    "le_plt_web_y1": le1_y1.model_dump(),
                    "le_plt_web_y2_var": "Le_plt_web_y2",
                    "le_plt_web_y2": le1_y2.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "anv_plt_v2_web_var": "Anv_plt_v2_web",
                    "anv_plt_v2_web_formula": "Anv_plt_v2_web = (p_plt_web*(n_plt_web_y - 1) + Le_plt_web_y1 + Le_plt_web_y2 - n_plt_web_y*(dh.1 + 1.80mm))*t_plt_web",
                    "anv_plt_v2_web": anv_plt_v2_web.model_dump(),
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn6_plt_v2_web_var": "Rn6_plt_v2_web",
                    "rn6_plt_v2_web_formula": "Rn6_plt_v2_web = 0.60*Fu_plt_web*Anv_plt_v2_web",
                    "rn6_plt_v2_web": rn6_plt_v2_web.model_dump() if isinstance(rn6_plt_v2_web, Quantity) else None,
                    "phi_rn6_plt_v2_web_var": "phi*Rn6_plt_v2_web",
                    "phi_rn6_plt_v2_web_formula": "phi*Rn6_plt_v2_web = phi_fragil*Rn6_plt_v2_web",
                    "phi_rn6_plt_v2_web": phi_rn6_plt_v2_web.model_dump(),
                    "ru6_plt_v2_web_var": "Ru6_plt_v2_web",
                    "ru6_plt_v2_web_formula": "Ru6_plt_v2_web = Vu2_sp",
                    "ru6_plt_v2_web": ru6_plt_v2_web.model_dump() if isinstance(ru6_plt_v2_web, Quantity) else None,
                    "dcr6_plt_v2_web_var": "DCR6_plt_v2_web",
                    "dcr6_plt_v2_web": dcr6_plt_v2_web,
                    "result6_plt_v2_web": result6_plt_v2_web,
                    "reference": "AISC 360-22 J4.2(b) (DRY: compute_element_shear_rupture_strength_j43)",
                },
                {
                    "id": "bbmb_splice.step4.web_shear_rupture_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por rotura a cortante del alma de la viga",
                    "clause": "AISC 360-22 J4.2(b)",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "a_vg_var": "A_vg",
                    "a_vg_formula": "A_vg = d_vg*tw_vg",
                    "a_vg": av_web_v2_vg.model_dump(),
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "anv_web_v2_vg_var": "Anv_web_v2_vg",
                    "anv_web_v2_vg_formula": "Anv_web_v2_vg = A_vg - n_blt_web_y*(dh.1+1.8mm)*tw_vg",
                    "anv_web_v2_vg": anv_web_v2_vg.model_dump(),
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn4_web_v2_vg_var": "Rn4_web_v2_vg",
                    "rn4_web_v2_vg_formula": "Rn4_web_v2_vg = 0.60*Fu_vg*Anv_web_v2_vg",
                    "rn4_web_v2_vg": rn4_web_v2_vg.model_dump() if isinstance(rn4_web_v2_vg, Quantity) else None,
                    "phi_rn4_web_v2_vg_var": "phi*Rn4_web_v2_vg",
                    "phi_rn4_web_v2_vg_formula": "phi*Rn4_web_v2_vg = phi_fragil*Rn4_web_v2_vg",
                    "phi_rn4_web_v2_vg": phi_rn4_web_v2_vg.model_dump(),
                    "ru4_web_v2_vg_var": "Ru4_web_v2_vg",
                    "ru4_web_v2_vg": ru4_web_v2_vg.model_dump() if isinstance(ru4_web_v2_vg, Quantity) else None,
                    "dcr4_web_v2_vg_var": "DCR4_web_v2_vg",
                    "dcr4_web_v2_vg": dcr4_web_v2_vg,
                    "result4_web_v2_vg": result4_web_v2_vg,
                    "reference": "AISC 360-22 J4.2(b) (DRY: compute_element_shear_rupture_strength_j43)",
                },
                {
                    "id": "bbmb_splice.step4.web_block_shear_note",
                    "scope": "viga",
                    "description": "Revision de resistencia por bloque de cortante en alma de viga",
                    "clause": "AISC 360-22w J4.3",
                    "fu_vg_var": "Fu_vg",
                    "fu_vg": fu_vg.model_dump(),
                    "fy_vg_var": "Fy_vg",
                    "fy_vg": fy_vg.model_dump() if isinstance(fy_vg, Quantity) else None,
                    "tw_vg_var": "tw_vg",
                    "tw_vg": tw_catalog.model_dump(),
                    "tf_vg_var": "tf_vg",
                    "tf_vg": tf_catalog.model_dump(),
                    "bf_vg_var": "bf_vg",
                    "bf_vg": bf_catalog.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "p_blt_web_var": "p_blt_web",
                    "p_blt_web": s1y.model_dump(),
                    "le_blt_web_x1_var": "Le_blt_web_x1",
                    "le_blt_web_x1": le1_x1.model_dump(),
                    "le_blt_web_y3_var": "Le_blt_web_y3",
                    "le_blt_web_y3": le1_y3.model_dump(),
                    "dh_1_var": "dh.1",
                    "dh_1": dh_web.model_dump(),
                    "agv_web_v2_vg_var": "Agv_web_v2_vg",
                    "agv_web_v2_vg_formula": "Agv_web_v2_vg = p_blt_web*(n_blt_web_y - 1)*tw_vg + (Le_blt_web_y3 - tf_vg)*tw_vg + tf_vg*bf_vg",
                    "agv_web_v2_vg": agv_web_v2_vg.model_dump(),
                    "anv5_web_v2_vg_var": "Anv_web_v2_vg",
                    "anv5_web_v2_vg_formula": "Anv_web_v2_vg = Agv_web_v2_vg - (n_blt_web_y - 0.5)*tw_vg*(dh.1 + 1.80mm)",
                    "anv5_web_v2_vg": anv5_web_v2_vg.model_dump(),
                    "agt_web_v2_vg_var": "Agt_web_v2_vg",
                    "agt_web_v2_vg_formula": "Agt_web_v2_vg = g_blt_web*(n_blt_web_x - 1)*tw_vg + Le_blt_web_x1*tw_vg",
                    "agt_web_v2_vg": a_gt_web_v2_vg.model_dump(),
                    "ant_web_v2_vg_var": "Ant_web_v2_vg",
                    "ant_web_v2_vg_formula": "Ant_web_v2_vg = Agt_web_v2_vg - (n_blt_web_x - 0.5)*tw_vg*(dh.1 + 1.80mm)",
                    "ant_web_v2_vg": ant_web_v2_vg.model_dump(),
                    "ubs_web_v2_vg_var": "Ubs_web_v2_vg",
                    "ubs_web_v2_vg": ubs_web_v2_vg,
                    "phi_fragil_var": "phi_fragil",
                    "phi_fragil": phi_fragil_web,
                    "rn5_1_web_v2_vg_var": "Rn5_1_web_v2_vg",
                    "rn5_1_web_v2_vg_formula": "Rn5_1_web_v2_vg = 0.60*Fu_vg*Anv_web_v2_vg + Ubs_web_v2_vg*Fu_vg*Ant_web_v2_vg",
                    "rn5_1_web_v2_vg": rn5_1_web_v2_vg.model_dump() if isinstance(rn5_1_web_v2_vg, Quantity) else None,
                    "rn5_2_web_v2_vg_var": "Rn5_2_web_v2_vg",
                    "rn5_2_web_v2_vg_formula": "Rn5_2_web_v2_vg = 0.60*Fy_vg*Agv_web_v2_vg + Ubs_web_v2_vg*Fu_vg*Ant_web_v2_vg",
                    "rn5_2_web_v2_vg": rn5_2_web_v2_vg.model_dump() if isinstance(rn5_2_web_v2_vg, Quantity) else None,
                    "rn5_web_v2_vg_var": "Rn5_web_v2_vg",
                    "rn5_web_v2_vg_formula": "Rn5_web_v2_vg = min(Rn5_1_web_v2_vg, Rn5_2_web_v2_vg)",
                    "rn5_web_v2_vg": rn5_web_v2_vg.model_dump() if isinstance(rn5_web_v2_vg, Quantity) else None,
                    "phi_rn5_web_v2_vg_var": "phi*Rn5_web_v2_vg",
                    "phi_rn5_web_v2_vg_formula": "phi*Rn5_web_v2_vg = phi_fragil*Rn5_web_v2_vg",
                    "phi_rn5_web_v2_vg": phi_rn5_web_v2_vg.model_dump(),
                    "ru5_web_v2_vg_var": "Ru5_web_v2_vg",
                    "ru5_web_v2_vg": ru5_web_v2_vg.model_dump() if isinstance(ru5_web_v2_vg, Quantity) else None,
                    "dcr5_web_v2_vg_var": "DCR5_web_v2_vg",
                    "dcr5_web_v2_vg": dcr5_web_v2_vg,
                    "result5_web_v2_vg": result5_web_v2_vg,
                    "controlling": block_shear_web_inter.get("controlling"),
                    "reference": block_shear_web_inter.get("reference"),
                },
                {
                    "id": "bbmb_splice.step1.geometry_formulas_plt1_note",
                    "scope": "platina_1",
                    "description": "Formulas geometricas de platina 1",
                    "clause": "Nomenclatura oficial splice",
                    "t_plt_web_var": "t_plt_web",
                    "t_plt_web": case.geometry.t_plt_web.model_dump(),
                    "steel_plt_web_var": "steel_plt_web",
                    "steel_plt_web": steel_plt_web,
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if fy_plt_web is not None else None,
                    "fu_plt_web_var": "Fu_plt_web",
                    "fu_plt_web": fu_plt_web.model_dump() if fu_plt_web is not None else None,
                    "e_plt_web_var": "E_plt_web",
                    "e_plt_web": e_plt_web.model_dump() if e_plt_web is not None else None,
                    "le_blt_web_y1_var": "Le_blt_web_y1",
                    "le_blt_web_y1": le1_y1.model_dump(),
                    "le_blt_web_y2_var": "Le_blt_web_y2",
                    "le_blt_web_y2": le1_y2.model_dump(),
                    "le_blt_web_x2_var": "Le_blt_web_x2",
                    "le_blt_web_x2": le1_x2.model_dump(),
                    "n_blt_web_x_var": "n_blt_web_x",
                    "n_blt_web_x": case.geometry.n_blt_web_x,
                    "g_blt_web_var": "g_blt_web",
                    "g_blt_web": s1x.model_dump(),
                    "n_blt_web_y_var": "n_blt_web_y",
                    "n_blt_web_y": case.geometry.n_blt_web_y,
                    "p_blt_web_var": "p_blt_web",
                    "p_blt_web": s1y.model_dump(),
                    "l_plt_web_var": "L_plt_web",
                    "l_plt_web": bp1.model_dump(),
                    "h_plt_web_var": "H_plt_web",
                    "h_plt_web": hp1.model_dump(),
                    "type_hole_plt_web_var": "type_hole_plt_web",
                    "type_hole_plt_web": case.geometry.type_hole_plt_web,
                    "cond_sup_plt_web_var": "cond_sup_plt_web",
                    "cond_sup_plt_web": case.geometry.cond_sup_plt_web,
                    "cond_amb_plt_web_var": "cond_amb_plt_web",
                    "cond_amb_plt_web": case.geometry.cond_amb_plt_web,
                    "hp1_formula": "H_plt_web = Le_blt_web_y1 + Le_blt_web_y2 + (n_blt_web_y - 1)*p_blt_web",
                    "hp1_calc": hp1.model_dump(),
                    "bp1_formula": "L_plt_web = 2*(Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web + Le_blt_web_x2) + gap_sp",
                    "bp1_calc": bp1.model_dump(),
                },
                {
                    "id": "bbmb_splice.step1.geometry_formulas_plt2_note",
                    "scope": "platina_2",
                    "description": "Formulas geometricas de platina 2",
                    "clause": "Nomenclatura oficial splice",
                    "steel_plt_flange_var": "steel_plt_flange",
                    "steel_plt_flange": steel_plt_flange,
                    "fy_plt_flange_var": "Fy_plt_flange",
                    "fy_plt_flange": fy_plt_flange.model_dump() if fy_plt_flange is not None else None,
                    "fu_plt_flange_var": "Fu_plt_flange",
                    "fu_plt_flange": fu_plt_flange.model_dump() if fu_plt_flange is not None else None,
                    "e_plt_flange_var": "E_plt_flange",
                    "e_plt_flange": e_plt_flange.model_dump() if e_plt_flange is not None else None,
                    "t_plt_flange_var": "t_plt_flange",
                    "t_plt_flange": t_plt_flange.model_dump(),
                    "type_hole_plt_flange_var": "type_hole_plt_flange",
                    "type_hole_plt_flange": case.geometry.type_hole_plt_flange,
                    "cond_sup_plt_flange_var": "cond_sup_plt_flange",
                    "cond_sup_plt_flange": case.geometry.cond_sup_plt_flange,
                    "cond_amb_plt_flange_var": "cond_amb_plt_flange",
                    "cond_amb_plt_flange": case.geometry.cond_amb_plt_flange,
                    "n_blt_flange_x_var": "n_blt_flange_x",
                    "n_blt_flange_x": case.geometry.n_blt_flange_x,
                    "p_blt_flange_var": "p_blt_flange",
                    "p_blt_flange": s2x.model_dump(),
                    "n_blt_flange_z_var": "n_blt_flange_z",
                    "n_blt_flange_z": case.geometry.n_blt_flange_z,
                    "g_blt_flange_var": "g_blt_flange",
                    "g_blt_flange": s2z1.model_dump(),
                    "le_blt_flange_x1_var": "Le_blt_flange_x1",
                    "le_blt_flange_x1": le2_x1.model_dump(),
                    "le_blt_flange_x2_var": "Le_blt_flange_x2",
                    "le_blt_flange_x2": le2_x2.model_dump(),
                    "le_blt_flange_z1_var": "Le_blt_flange_z1",
                    "le_blt_flange_z1": le2_z1.model_dump(),
                    "le_blt_flange_z2_var": "Le_blt_flange_z2",
                    "le_blt_flange_z2": le2_z2.model_dump(),
                    "g1_blt_flange_var": "g1_blt_flange",
                    "g1_blt_flange": g1_blt_flange.model_dump() if g1_blt_flange is not None else None,
                    "l_plt_flange_var": "L_plt_flange",
                    "l_plt_flange": lp2.model_dump(),
                    "b_plt_flange_var": "B_plt_flange",
                    "b_plt_flange": bp2.model_dump(),
                    "bp2_formula": "B_plt_flange = Le_blt_flange_z1 + Le_blt_flange_z2 + 2*(n_blt_flange_z - 1)*g_blt_flange + g1_blt_flange",
                    "bp2_calc": bp2.model_dump(),
                    "lp2_formula": "L_plt_flange = 2*(Le_blt_flange_x1 + (n_blt_flange_x - 1)*p_blt_flange + Le_blt_flange_x2) + gap_sp",
                    "lp2_calc": lp2.model_dump(),
                },
                {
                    "id": "bbmb_splice.step1.plate_1_hole_diameter_note",
                    "scope": "platina_1",
                    "description": "Diametro de perforacion estandar en platina 1",
                    "clause": "AISC 360-22 Table J3.3",
                    "formula": "dh_plt_web = db_blt_web + 1/16 in (db<=7/8 in) else +1/8 in",
                    "db_var": "db_blt_web",
                    "dh_var": "dh_plt_web",
                    "db": db_web.model_dump(),
                    "dh": dh_web.model_dump(),
                    "hole_add_in": dh_web_inter["hole_add_in"],
                },
                {
                    "id": "bbmb_splice.step1.plate_2_hole_diameter_note",
                    "scope": "platina_2",
                    "description": "Diametro de perforacion estandar en platina 2",
                    "clause": "AISC 360-22 Table J3.3",
                    "formula": "dh_plt_flange = db_blt_flange + 1/16 in (db<=7/8 in) else +1/8 in",
                    "db_var": "db_blt_flange",
                    "dh_var": "dh_plt_flange",
                    "db": db_flange.model_dump(),
                    "dh": dh_flange.model_dump(),
                    "hole_add_in": dh_flange_inter["hole_add_in"],
                },
                {
                    "id": "bbmb_splice.step1.bolt_group_1_properties_note",
                    "scope": "pernos_1",
                    "description": "Propiedades del perno usado en Pernos 1",
                    "clause": "Catalogo de pernos + inputs del caso",
                    "bolt_shape": str(bolt_web.get("shape", "")),
                    "classification": str(bolt_web.get("classification", "")),
                    "fabrication_standard": case.materials.std_blt_web,
                    "thread_condition": case.materials.thread_blt_web,
                    "tightening_type": case.geometry.type_tight_blt_web or "n/a",
                    "fnt_var": "Fnt_blt_web",
                    "fnt": fnt_web.model_dump() if fnt_web is not None else None,
                    "fnv_var": "Fnv_blt_web",
                    "fnv": fnv_web.model_dump() if fnv_web is not None else None,
                    "diameter_nominal": db_web.model_dump(),
                    "length_shank": bolt_web["length"].model_dump() if isinstance(bolt_web.get("length"), Quantity) else None,
                    "width_across_flats": (
                        bolt_web["width_across_flats"].model_dump()
                        if isinstance(bolt_web.get("width_across_flats"), Quantity)
                        else None
                    ),
                    "head_diameter": (
                        bolt_web["head_diameter"].model_dump()
                        if isinstance(bolt_web.get("head_diameter"), Quantity)
                        else None
                    ),
                    "head_height": (
                        bolt_web["head_height"].model_dump()
                        if isinstance(bolt_web.get("head_height"), Quantity)
                        else None
                    ),
                },
                {
                    "id": "bbmb_splice.step1.bolt_group_2_properties_note",
                    "scope": "pernos_2",
                    "description": "Propiedades del perno usado en Pernos 2",
                    "clause": "Catalogo de pernos + inputs del caso",
                    "bolt_shape": str(bolt_flange.get("shape", "")),
                    "classification": str(bolt_flange.get("classification", "")),
                    "fabrication_standard": case.materials.std_blt_flange,
                    "thread_condition": case.materials.thread_blt_flange,
                    "tightening_type": case.geometry.type_tight_blt_flange or "n/a",
                    "fnt_var": "Fnt_blt_flange",
                    "fnt": fnt_flange.model_dump() if fnt_flange is not None else None,
                    "fnv_var": "Fnv_blt_flange",
                    "fnv": fnv_flange.model_dump() if fnv_flange is not None else None,
                    "diameter_nominal": db_flange.model_dump(),
                    "length_shank": (
                        bolt_flange["length"].model_dump() if isinstance(bolt_flange.get("length"), Quantity) else None
                    ),
                    "width_across_flats": (
                        bolt_flange["width_across_flats"].model_dump()
                        if isinstance(bolt_flange.get("width_across_flats"), Quantity)
                        else None
                    ),
                    "head_diameter": (
                        bolt_flange["head_diameter"].model_dump()
                        if isinstance(bolt_flange.get("head_diameter"), Quantity)
                        else None
                    ),
                    "head_height": (
                        bolt_flange["head_height"].model_dump()
                        if isinstance(bolt_flange.get("head_height"), Quantity)
                        else None
                    ),
                },
            ],
            "edge_distance_table_row_web": le_meta_web.get("table_row"),
            "edge_distance_table_row_flange": le_meta_flange.get("table_row"),
        },
        design_factors={},
        equation="Step 1 detailing splice: J3.3 + Tabla J3.4 + J3.6 + checks geometricos de proyecto",
        units_trace={
            "db_blt_web": db_web.unit,
            "db_blt_flange": db_flange.unit,
            "g_blt_web": s1x.unit,
            "p_blt_web": s1y.unit,
            "p_blt_flange": s2x.unit,
            "g_blt_flange": s2z1.unit,
            "Le_blt_web_x1": le1_x1.unit,
            "Le_blt_web_x2": le1_x2.unit,
            "Le_blt_web_y1": le1_y1.unit,
            "Le_blt_web_y2": le1_y2.unit,
            "Le_blt_flange_x1": le2_x1.unit,
            "Le_blt_flange_x2": le2_x2.unit,
            "Le_blt_flange_z1": le2_z1.unit,
            "Le_blt_flange_z2": le2_z2.unit,
            "Le_blt_flange_z1": le2_z1.unit,
        },
        final_capacity=None,
    )
    return CheckResult(
        name=rule_binding.name,
        rule_id=rule_binding.rule_id,
        clause=rule_binding.clause,
        source_document=rule_binding.source_document,
        demand=None,
        capacity=None,
        dcr=None,
        status=status,
        calculation_memory=memory,
        notes=None,
    )
