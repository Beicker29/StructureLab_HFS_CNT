from __future__ import annotations

from steel_connections.codes.engineering.common import (
    compute_max_spacing_and_edge_distance_limits_j36,
    compute_maximum_bolt_spacing_j36,
    compute_minimum_bolt_spacing_j33,
    compute_minimum_edge_distance_standard_hole_j34,
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
    bp1_calc = le1_x1.value + le1_x2.value + alpha.value + 2.0 * (case.geometry.n_blt_web_x - 1) * s1x.value
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

    status = CheckStatus.PASS if all(row["result"] == "PASS" for row in rows) else CheckStatus.FAIL

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
