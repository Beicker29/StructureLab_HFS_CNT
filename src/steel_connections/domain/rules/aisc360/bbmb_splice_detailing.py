from __future__ import annotations

from steel_connections.codes.aisc358.chapter_06 import (
    compute_minimum_bolt_spacing,
    compute_minimum_edge_distance_standard_hole,
)
from steel_connections.data.sections_repository import get_beam_profile_properties, get_bolt_section_properties
from steel_connections.models.input import BeamBeamMomentBoltedCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus
from steel_connections.models.units import Quantity, UnitSystem


def _compute_standard_hole_diameter(*, bolt_diameter: Quantity, unit_system: UnitSystem) -> tuple[Quantity, dict[str, float]]:
    expected_unit = "in" if unit_system.value == "US" else "mm"
    if bolt_diameter.unit != expected_unit:
        raise ValueError(
            f"Invalid bolt diameter unit. Expected '{expected_unit}', got '{bolt_diameter.unit}'."
        )
    if bolt_diameter.value <= 0.0:
        raise ValueError("Bolt diameter must be positive to derive standard hole diameter.")
    db_in = bolt_diameter.value if unit_system.value == "US" else bolt_diameter.value / 25.4
    hole_add_in = 1.0 / 16.0 if db_in <= (7.0 / 8.0 + 1e-9) else 1.0 / 8.0
    dh_in = db_in + hole_add_in
    if unit_system.value == "US":
        return Quantity(value=dh_in, unit="in"), {"db_in": db_in, "hole_add_in": hole_add_in}
    return Quantity(value=dh_in * 25.4, unit="mm"), {"db_in": db_in, "hole_add_in": hole_add_in}


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

    dh_web, dh_web_inter = _compute_standard_hole_diameter(bolt_diameter=db_web, unit_system=case.units_system)
    dh_flange, dh_flange_inter = _compute_standard_hole_diameter(bolt_diameter=db_flange, unit_system=case.units_system)

    s_min_web = compute_minimum_bolt_spacing(bolt_diameter=db_web, unit_system=case.units_system)
    s_min_flange = compute_minimum_bolt_spacing(bolt_diameter=db_flange, unit_system=case.units_system)
    le_min_web, le_meta_web = compute_minimum_edge_distance_standard_hole(
        bolt_diameter=db_web,
        unit_system=case.units_system,
    )
    le_min_flange, le_meta_flange = compute_minimum_edge_distance_standard_hole(
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
    le1_y3 = case.geometry.Le_blt_web_y3
    le2_x1 = case.geometry.Le_blt_flange_x1
    le2_x2 = case.geometry.Le_blt_flange_x2
    le2_z1 = case.geometry.Le_blt_flange_z1
    le2_z2 = case.geometry.Le_blt_flange_z2
    le2_z3 = case.geometry.Le_blt_flange_z3

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

    # Le_blt_web_y4 is derived for reporting only.
    le1_y4: Quantity | None = None
    if le1_y3 is not None and le1_y3.unit == dvg_catalog.unit:
        le1_y4 = Quantity(value=dvg_catalog.value - le1_y3.value, unit=dvg_catalog.unit)

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

    # J3.6 max spacing / edge distance
    t_web = min(case.geometry.t_plt_web.value, tw_catalog.value)
    t_flange = min(min(case.geometry.t_plt_ftop.value, case.geometry.t_plt_fbot.value), tf_catalog.value)
    spacing_abs_max = 12.0 if case.units_system.value == "US" else 300.0
    edge_abs_max_regular = 6.0 if case.units_system.value == "US" else 150.0
    edge_abs_max_reduced = 5.0 if case.units_system.value == "US" else 125.0
    smax_web = min(24.0 * t_web, spacing_abs_max)
    smax_flange = min(24.0 * t_flange, spacing_abs_max)

    web_surface = case.geometry.cond_sup_plt_web or "unpainted"
    web_atm = case.geometry.cond_amb_plt_web or "non_corrosive"
    flange_surface = case.geometry.cond_sup_plt_flange or "unpainted"
    flange_atm = case.geometry.cond_amb_plt_flange or "non_corrosive"

    def _edge_max(t_value: float, *, atmospheric: str, surface: str) -> float:
        regular = min(12.0 * t_value, edge_abs_max_regular)
        reduced = min(8.0 * t_value, edge_abs_max_reduced)
        if atmospheric == "corrosive" and surface == "unpainted":
            return reduced
        return regular

    lemax_web = _edge_max(t_web, atmospheric=web_atm, surface=web_surface)
    lemax_flange = _edge_max(t_flange, atmospheric=flange_atm, surface=flange_surface)

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
            limit={"value": smax_web, "unit": s1x.unit},
            clause="AISC 360-22 J3.6",
            passed=s1x.value <= smax_web,
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
            limit={"value": smax_web, "unit": s1y.unit},
            clause="AISC 360-22 J3.6",
            passed=s1y.value <= smax_web,
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
            limit={"value": smax_flange, "unit": s2x.unit},
            clause="AISC 360-22 J3.6",
            passed=s2x.value <= smax_flange,
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
            passed=s2z1.value >= s_min_flange.value,
        ),
        _row(
            scope="pernos_2",
            description="Separacion maxima entre pernos del ala en direccion Z",
            calculated_symbol="g_blt_flange",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=s2z1.model_dump(),
            limit={"value": smax_flange, "unit": s2z1.unit},
            clause="AISC 360-22 J3.6",
            passed=s2z1.value <= smax_flange,
        ),
        _row(
            scope="viga",
            description="Distancia minima a borde Le_blt_web_x1 para agujero estandar",
            calculated_symbol="Le_blt_web_x1",
            limit_symbol=le1_min_limit_symbol,
            comparison_text=">=",
            calculated=le1_x1.model_dump(),
            limit=le1_min_limit.model_dump(),
            clause=le1_min_clause,
            passed=le1_x1.value >= le1_min_limit.value,
        ),
        _row(
            scope="viga",
            description="Distancia maxima a borde Le_blt_web_x1",
            calculated_symbol="Le_blt_web_x1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_x1.model_dump(),
            limit={"value": lemax_web, "unit": le1_x1.unit},
            clause="AISC 360-22 J3.6",
            passed=le1_x1.value <= lemax_web,
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
            calculated=(
                le1_y3.model_dump()
                if le1_y3 is not None
                else {"value": 0.5 * (dvg_catalog.value - (case.geometry.n_blt_web_y - 1) * s1y.value), "unit": dvg_catalog.unit}
            ),
            limit=kdes_catalog.model_dump(),
            clause="Criterio solicitado por usuario + catalogo de secciones",
            passed=(
                (le1_y3.value >= kdes_catalog.value)
                if le1_y3 is not None and le1_y3.unit == kdes_catalog.unit
                else (0.5 * (dvg_catalog.value - (case.geometry.n_blt_web_y - 1) * s1y.value) >= kdes_catalog.value)
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
    le1_y3_calc = (
        le1_y3
        if le1_y3 is not None
        else Quantity(value=0.5 * (dvg_catalog.value - (case.geometry.n_blt_web_y - 1) * s1y.value), unit=dvg_catalog.unit)
    )

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
                    "alpha_symbol": "gap_sp",
                    "alpha": alpha.model_dump(),
                    "beam_length_tolerance_var": "tol_L_vg",
                    "beam_length_tolerance": tlvg.model_dump(),
                    "beam_length_tolerance_ref": "AISC 303-22",
                    "s1x_var": "g_blt_web",
                    "s1x": s1x.model_dump(),
                    "le1x1_var": "Le_blt_web_x1",
                    "le1x1": le1_x1.model_dump(),
                    "le1x1_prime_var": "Le_blt_web_x1'",
                    "le1x1_prime_formula": "Le_blt_web_x1' = Le_blt_web_x1 - tol_L_vg",
                    "le1x1_prime": le1_x1_prime.model_dump() if le1_x1_prime is not None else None,
                    "dvg_var": "d_vg",
                    "dvg": dvg_catalog.model_dump(),
                    "le1y3_var": "Le_blt_web_y3",
                    "le1y3": le1_y3_calc.model_dump(),
                    "le1y4_var": "Le_blt_web_y4",
                    "le1y4_formula": "Le_blt_web_y4 = d_vg - Le_blt_web_y3",
                    "le1y4": le1_y4.model_dump() if le1_y4 is not None else None,
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
                    "hp1_formula": "B_plt_web = Le_blt_web_y1 + Le_blt_web_y2 + (n_blt_web_y - 1)*p_blt_web",
                    "hp1_calc": hp1.model_dump(),
                    "bp1_formula": "L_plt_web = 2*(Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web + Le_blt_web_x2) + gap_sp",
                    "bp1_calc": bp1.model_dump(),
                },
                {
                    "id": "bbmb_splice.step1.geometry_formulas_plt2_note",
                    "scope": "platina_2",
                    "description": "Formulas geometricas de platina 2",
                    "clause": "Nomenclatura oficial splice",
                    "bp2_formula": "B_plt_flange = bf_vg - 2*Le_blt_flange_z3 + Le_blt_flange_z1 + Le_blt_flange_z2",
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
