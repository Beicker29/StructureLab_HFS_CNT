from __future__ import annotations

import math

from steel_connections.codes.engineering.common import (
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
    compute_standard_hole_diameter_j33,
)
from steel_connections.data.materials_repository import (
    get_bolt_strength_properties,
    get_hrs_steel_properties,
    get_plate_steel_properties,
)
from steel_connections.data.sections_repository import get_beam_profile_properties, get_bolt_section_properties
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
) -> dict:
    return {
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


def run_step1_viga_detailing(case: BeamBeamMomentBoltedCase, rule_binding: object) -> CheckResult:
    bolt_web = get_bolt_section_properties(
        bolt_shape=case.materials.shape_blt_web,
        unit_system=case.units_system,
    )
    bolt_flange = get_bolt_section_properties(
        bolt_shape=case.materials.shape_blt_flange,
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
    le2_z3 = case.geometry.Le_blt_flange_z3
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
    bp2_calc = bf_catalog.value - 2.0 * le2_z3.value + le2_z1.value + le2_z2.value
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
        and bf_catalog.unit == le2_z3.unit == k1_catalog.unit == s2z1.unit
    ):
        le2_z4 = Quantity(
            value=0.5 * bf_catalog.value
            - (le2_z3.value + k1_catalog.value + (case.geometry.n_blt_flange_z - 1) * s2z1.value),
            unit=bf_catalog.unit,
        )
    g1_blt_flange: Quantity | None = None
    if bf_catalog.unit == le2_z3.unit == s2z1.unit:
        g1_blt_flange = Quantity(
            value=bf_catalog.value - 2.0 * (le2_z3.value + (case.geometry.n_blt_flange_z - 1) * s2z1.value),
            unit=bf_catalog.unit,
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
    if s1y.unit != dh_web.unit:
        raise ValueError("Incompatible units in lc_blt_web_y = p_blt_web - dh.1.")
    lc_blt_web_y = Quantity(value=s1y.value - dh_web.value, unit=s1y.unit)
    svc_hole_deformation_design_web = bool(case.geometry.svc_hole_deformation_design_web)
    phi_fragil_web = 0.75
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
        value=case.loads.Pu_sp.value * case.loads.alpha_Pu_web,
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

    rows = [
        _row(
            scope="pernos_1",
            description="Separacion minima entre pernos del alma en direccion X",
            calculated_symbol="g_blt_web",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s1x.model_dump(),
            limit=s_min_web.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s1x.value >= s_min_web.value,
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
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s1y.model_dump(),
            limit=s_min_web.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s1y.value >= s_min_web.value,
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
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s2x.model_dump(),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s2x.value >= s_min_flange.value,
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
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=s2z1.model_dump(),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=(s2z1.value >= s_min_flange.value) if applies_g_blt_flange_spacing else True,
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
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_x1.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_x1.value >= le_min_web.value,
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
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_y3_1.model_dump() if le1_y3_1 is not None else {"value": 0.0, "unit": le1_y3.unit},
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=(le1_y3_1 is not None and le1_y3_1.value >= le_min_web.value),
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
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_x1.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_x1.value >= le_min_flange.value,
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
            description="Distancia minima a borde Le_blt_flange_z3 para agujero estandar",
            calculated_symbol="Le_blt_flange_z3",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z3.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_z3.value >= le_min_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le_blt_flange_z3",
            calculated_symbol="Le_blt_flange_z3",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z3.model_dump(),
            limit=lemax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=le2_z3.value <= lemax_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le_blt_flange_z4 para agujero estandar",
            calculated_symbol="Le_blt_flange_z4",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z4.model_dump() if le2_z4 is not None else {"value": 0.0, "unit": le2_z3.unit},
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=(le2_z4 is not None and le2_z4.value >= le_min_flange.value),
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le_blt_flange_z4",
            calculated_symbol="Le_blt_flange_z4",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z4.model_dump() if le2_z4 is not None else {"value": 0.0, "unit": le2_z3.unit},
            limit=lemax_flange.model_dump(),
            clause="AISC 360-22 J3.6",
            passed=(le2_z4 is not None and le2_z4.value <= lemax_flange.value),
        ),
        _row(
            scope="pernos_2",
            description="Separacion minima entre pernos del ala en direccion Z (g1)",
            calculated_symbol="g1_blt_flange",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=(
                g1_blt_flange.model_dump()
                if g1_blt_flange is not None
                else {"value": 0.0, "unit": s2z1.unit}
            ),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=(g1_blt_flange is not None and g1_blt_flange.value >= s_min_flange.value),
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
            "Le_blt_flange_z3": le2_z3.model_dump(),
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
                    "le2z4_formula": "Le_blt_flange_z4 = 0.5*bfdet_vg - (Le_blt_flange_z3 + k1_vg + (n_blt_flange_z - 1)*g_blt_flange)",
                    "le2z4": le2_z4.model_dump() if le2_z4 is not None else None,
                    "g1_blt_flange_var": "g1_blt_flange",
                    "g1_blt_flange_formula": "g1_blt_flange = bf_vg - 2*(Le_blt_flange_z3 + (n_blt_flange_z - 1)*g_blt_flange)",
                    "g1_blt_flange": g1_blt_flange.model_dump() if g1_blt_flange is not None else None,
                    "n2x_var": "n_blt_flange_x",
                    "n2x": case.geometry.n_blt_flange_x,
                    "s2x_var": "p_blt_flange",
                    "s2x": s2x.model_dump(),
                    "le2x1_var": "Le_blt_flange_x1",
                    "le2x1": le2_x1.model_dump(),
                    "n2z_var": "n_blt_flange_z",
                    "n2z": case.geometry.n_blt_flange_z,
                    "le2z3_var": "Le_blt_flange_z3",
                    "le2z3": le2_z3.model_dump(),
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
                    "ru3_v3_vg_formula": "Ru3_v3_vg = Pu_sp*alpha_Pu_web",
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
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if isinstance(fy_plt_web, Quantity) else None,
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
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if isinstance(fy_plt_web, Quantity) else None,
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
                    "fy_plt_web_var": "Fy_plt_web",
                    "fy_plt_web": fy_plt_web.model_dump() if isinstance(fy_plt_web, Quantity) else None,
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
                    "le_blt_flange_z3_var": "Le_blt_flange_z3",
                    "le_blt_flange_z3": le2_z3.model_dump(),
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
            "Le_blt_flange_z3": le2_z3.unit,
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
