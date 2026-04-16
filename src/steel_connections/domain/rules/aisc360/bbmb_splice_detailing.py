from __future__ import annotations

from steel_connections.codes.aisc358.chapter_06 import (
    compute_minimum_bolt_spacing,
    compute_minimum_edge_distance_standard_hole,
)
from steel_connections.data.sections_repository import get_beam_profile_properties, get_bolt_section_properties
from steel_connections.models.input import BeamBeamMomentBoltedCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus


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
        bolt_shape=case.materials.bolt_shape_web or case.materials.bolt_shape,
        unit_system=case.units_system,
    )
    bolt_flange = get_bolt_section_properties(
        bolt_shape=case.materials.bolt_shape_flange or case.materials.bolt_shape,
        unit_system=case.units_system,
    )
    db_web = bolt_web["diameter_nominal"]
    db_flange = bolt_flange["diameter_nominal"]
    if not isinstance(db_web, object) or not hasattr(db_web, "model_dump"):
        raise ValueError("Unable to resolve bolt diameter from bolt shape for bbmb_splice detailing.")
    if not isinstance(db_flange, object) or not hasattr(db_flange, "model_dump"):
        raise ValueError("Unable to resolve flange bolt diameter from bolt shape for bbmb_splice detailing.")
    db_web_in = db_web.value if case.units_system.value == "US" else db_web.value / 25.4
    db_flange_in = db_flange.value if case.units_system.value == "US" else db_flange.value / 25.4
    standard_web = case.materials.bolt_fabrication_standard_web or case.materials.bolt_fabrication_standard
    standard_flange = case.materials.bolt_fabrication_standard_flange or case.materials.bolt_fabrication_standard

    s_min = compute_minimum_bolt_spacing(bolt_diameter=db_web, unit_system=case.units_system)
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
        beam_shape=case.sections.beam_right_shape,
        unit_system=case.units_system,
    )
    t_catalog = beam_props.get("T")
    if t_catalog is None:
        raise ValueError(
            f"Sections catalog does not provide 'T' for shape '{case.sections.beam_right_shape}'."
        )
    k1_catalog = beam_props.get("k1")
    if k1_catalog is None:
        raise ValueError(
            f"Sections catalog does not provide 'k1' for shape '{case.sections.beam_right_shape}'."
        )
    tw_catalog = beam_props.get("tw")
    tf_catalog = beam_props.get("tf")
    bf_catalog = beam_props.get("bf")
    if tw_catalog is None or tf_catalog is None or bf_catalog is None:
        raise ValueError(
            f"Sections catalog does not provide 'tw/tf/bf' for shape '{case.sections.beam_right_shape}'."
        )

    s1x_ok = case.geometry.web_bolt_gage.value >= s_min.value
    s1y_ok = case.geometry.web_bolt_pitch.value >= s_min.value
    s2x_ok = case.geometry.flange_bolt_gage.value >= s_min_flange.value
    s2z1_ok = case.geometry.flange_bolt_pitch.value >= s_min_flange.value
    s2z2 = case.geometry.flange_bolt_pitch_secondary or case.geometry.flange_bolt_pitch
    le1_x1 = case.geometry.web_bolt_edge_distance_x1 or case.geometry.web_bolt_edge_distance
    le1_x2 = case.geometry.web_bolt_edge_distance_x2 or case.geometry.web_bolt_edge_distance
    le1_y1 = case.geometry.web_bolt_edge_distance_y1 or case.geometry.web_bolt_edge_distance
    le1_y2 = case.geometry.web_bolt_edge_distance_y2 or case.geometry.web_bolt_edge_distance
    le2_x1 = case.geometry.flange_bolt_edge_distance_x1 or case.geometry.flange_bolt_edge_distance_longitudinal
    le2_x2 = case.geometry.flange_bolt_edge_distance_x2 or case.geometry.flange_bolt_edge_distance_longitudinal
    le2_z1 = case.geometry.flange_bolt_edge_distance_z1 or case.geometry.flange_bolt_edge_distance_transverse
    le2_z2 = case.geometry.flange_bolt_edge_distance_z2 or case.geometry.flange_bolt_edge_distance_transverse

    le1_x1_ok = le1_x1.value >= le_min_web.value
    le1_x2_ok = le1_x2.value >= le_min_web.value
    le1_y1_ok = le1_y1.value >= le_min_web.value
    le1_y2_ok = le1_y2.value >= le_min_web.value
    le2_x1_ok = le2_x1.value >= le_min_flange.value
    le2_x2_ok = le2_x2.value >= le_min_flange.value
    le2_z1_ok = le2_z1.value >= le_min_flange.value
    le2_z2_ok = le2_z2.value >= le_min_flange.value
    s2_z2_compound_limit = 2.0 * s_min_flange.value + 2.0 * k1_catalog.value
    s2_z2_compound_ok = s2z2.value >= s2_z2_compound_limit
    hp1_ok = case.geometry.web_plate_height.value <= t_catalog.value
    bp2_ok = case.geometry.flange_plate_top_width.value <= bf_catalog.value

    alpha = case.geometry.splice_gap
    hp1_calc = le1_y1.value + le1_y2.value + (case.geometry.web_bolt_rows_per_side - 1) * case.geometry.web_bolt_pitch.value
    bp1_calc = (
        le1_x1.value
        + le1_x2.value
        + alpha.value
        + 2.0 * (case.geometry.web_bolt_lines - 1) * case.geometry.web_bolt_gage.value
    )
    bp2_calc = le2_z2.value + le2_z1.value + s2z2.value + max(case.geometry.flange_bolt_rows_per_side - 2, 0) * case.geometry.flange_bolt_pitch.value
    lp2_calc = (
        2.0 * (le2_x1.value + le2_x2.value)
        + alpha.value
        + 2.0 * (case.geometry.flange_bolt_lines - 1) * case.geometry.flange_bolt_gage.value
        + alpha.value
    )

    # J3.6 Maximum spacing and edge distance.
    # thinner connected part governs:
    # web splice -> min(tp1, tw_beam), flange splice -> min(tp2, tf_beam)
    t_web = min(case.geometry.web_plate_thickness.value, tw_catalog.value)
    t_flange = min(case.geometry.flange_plate_top_thickness.value, tf_catalog.value)

    spacing_abs_max = 12.0 if case.units_system.value == "US" else 300.0
    edge_abs_max_regular = 6.0 if case.units_system.value == "US" else 150.0
    edge_abs_max_reduced = 5.0 if case.units_system.value == "US" else 125.0

    smax_web = min(24.0 * t_web, spacing_abs_max)
    smax_flange = min(24.0 * t_flange, spacing_abs_max)

    web_surface = case.geometry.web_plate_surface_condition or "unpainted"
    web_atm = case.geometry.web_plate_atmospheric_condition or "non_corrosive"
    flange_surface = case.geometry.flange_plate_surface_condition or "unpainted"
    flange_atm = case.geometry.flange_plate_atmospheric_condition or "non_corrosive"

    def _edge_max(t_value: float, *, atmospheric: str, surface: str) -> float:
        regular = min(12.0 * t_value, edge_abs_max_regular)
        reduced = min(8.0 * t_value, edge_abs_max_reduced)
        if atmospheric == "corrosive" and surface == "unpainted":
            return reduced
        return regular

    lemax_web = _edge_max(t_web, atmospheric=web_atm, surface=web_surface)
    lemax_flange = _edge_max(t_flange, atmospheric=flange_atm, surface=flange_surface)

    nb2_z = case.geometry.flange_bolt_rows_per_side

    rows = [
        _row(
            scope="pernos_1",
            description="Separacion minima entre pernos del alma en direccion X",
            calculated_symbol="S1_x",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=case.geometry.web_bolt_gage.model_dump(),
            limit=s_min.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s1x_ok,
        ),
        _row(
            scope="pernos_1",
            description="Separacion maxima entre pernos del alma en direccion X",
            calculated_symbol="S1_x",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=case.geometry.web_bolt_gage.model_dump(),
            limit={"value": smax_web, "unit": case.geometry.web_bolt_gage.unit},
            clause="AISC 360-22 J3.6",
            passed=case.geometry.web_bolt_gage.value <= smax_web,
        ),
        _row(
            scope="pernos_1",
            description="Separacion minima entre pernos del alma en direccion Y",
            calculated_symbol="S1_y",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=case.geometry.web_bolt_pitch.model_dump(),
            limit=s_min.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s1y_ok,
        ),
        _row(
            scope="pernos_1",
            description="Separacion maxima entre pernos del alma en direccion Y",
            calculated_symbol="S1_y",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=case.geometry.web_bolt_pitch.model_dump(),
            limit={"value": smax_web, "unit": case.geometry.web_bolt_pitch.unit},
            clause="AISC 360-22 J3.6",
            passed=case.geometry.web_bolt_pitch.value <= smax_web,
        ),
        _row(
            scope="pernos_2",
            description="Separacion minima entre pernos del ala en direccion X",
            calculated_symbol="S2_x",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=case.geometry.flange_bolt_gage.model_dump(),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s2x_ok,
        ),
        _row(
            scope="pernos_2",
            description="Separacion maxima entre pernos del ala en direccion X",
            calculated_symbol="S2_x",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=case.geometry.flange_bolt_gage.model_dump(),
            limit={"value": smax_flange, "unit": case.geometry.flange_bolt_gage.unit},
            clause="AISC 360-22 J3.6",
            passed=case.geometry.flange_bolt_gage.value <= smax_flange,
        ),
        _row(
            scope="pernos_2",
            description="Separacion minima entre pernos del ala en direccion Z (S2_z1)",
            calculated_symbol="S2_z1",
            limit_symbol="Smin",
            comparison_text=">=",
            calculated=case.geometry.flange_bolt_pitch.model_dump(),
            limit=s_min_flange.model_dump(),
            clause="AISC 360-22 J3.3",
            passed=s2z1_ok,
        ),
        _row(
            scope="pernos_2",
            description="Separacion maxima entre pernos del ala en direccion Z (S2_z1)",
            calculated_symbol="S2_z1",
            limit_symbol="Smax",
            comparison_text="<=",
            calculated=case.geometry.flange_bolt_pitch.model_dump(),
            limit={"value": smax_flange, "unit": case.geometry.flange_bolt_pitch.unit},
            clause="AISC 360-22 J3.6",
            passed=case.geometry.flange_bolt_pitch.value <= smax_flange,
        ),
        _row(
            scope="pernos_1",
            description="Distancia minima a borde Le1_x1 para agujero estandar",
            calculated_symbol="Le1_x1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_x1.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_x1_ok,
        ),
        _row(
            scope="pernos_1",
            description="Distancia maxima a borde Le1_x1",
            calculated_symbol="Le1_x1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_x1.model_dump(),
            limit={"value": lemax_web, "unit": le1_x1.unit},
            clause="AISC 360-22 J3.6",
            passed=le1_x1.value <= lemax_web,
        ),
        _row(
            scope="pernos_1",
            description="Distancia minima a borde Le1_x2 para agujero estandar",
            calculated_symbol="Le1_x2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_x2.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_x2_ok,
        ),
        _row(
            scope="pernos_1",
            description="Distancia maxima a borde Le1_x2",
            calculated_symbol="Le1_x2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_x2.model_dump(),
            limit={"value": lemax_web, "unit": le1_x2.unit},
            clause="AISC 360-22 J3.6",
            passed=le1_x2.value <= lemax_web,
        ),
        _row(
            scope="pernos_1",
            description="Distancia minima a borde Le1_y1 para agujero estandar",
            calculated_symbol="Le1_y1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_y1.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_y1_ok,
        ),
        _row(
            scope="pernos_1",
            description="Distancia maxima a borde Le1_y1",
            calculated_symbol="Le1_y1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_y1.model_dump(),
            limit={"value": lemax_web, "unit": le1_y1.unit},
            clause="AISC 360-22 J3.6",
            passed=le1_y1.value <= lemax_web,
        ),
        _row(
            scope="pernos_1",
            description="Distancia minima a borde Le1_y2 para agujero estandar",
            calculated_symbol="Le1_y2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le1_y2.model_dump(),
            limit=le_min_web.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le1_y2_ok,
        ),
        _row(
            scope="pernos_1",
            description="Distancia maxima a borde Le1_y2",
            calculated_symbol="Le1_y2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le1_y2.model_dump(),
            limit={"value": lemax_web, "unit": le1_y2.unit},
            clause="AISC 360-22 J3.6",
            passed=le1_y2.value <= lemax_web,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le2_x1 para agujero estandar",
            calculated_symbol="Le2_x1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_x1.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_x1_ok,
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le2_x1",
            calculated_symbol="Le2_x1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_x1.model_dump(),
            limit={"value": lemax_flange, "unit": le2_x1.unit},
            clause="AISC 360-22 J3.6",
            passed=le2_x1.value <= lemax_flange,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le2_x2 para agujero estandar",
            calculated_symbol="Le2_x2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_x2.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_x2_ok,
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le2_x2",
            calculated_symbol="Le2_x2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_x2.model_dump(),
            limit={"value": lemax_flange, "unit": le2_x2.unit},
            clause="AISC 360-22 J3.6",
            passed=le2_x2.value <= lemax_flange,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le2_z1 para agujero estandar",
            calculated_symbol="Le2_z1",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z1.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_z1_ok,
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le2_z1",
            calculated_symbol="Le2_z1",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z1.model_dump(),
            limit={"value": lemax_flange, "unit": le2_z1.unit},
            clause="AISC 360-22 J3.6",
            passed=le2_z1.value <= lemax_flange,
        ),
        _row(
            scope="pernos_2",
            description="Distancia minima a borde Le2_z2 para agujero estandar",
            calculated_symbol="Le2_z2",
            limit_symbol="Le_min",
            comparison_text=">=",
            calculated=le2_z2.model_dump(),
            limit=le_min_flange.model_dump(),
            clause="AISC 360-22 Tabla J3.4",
            passed=le2_z2_ok,
        ),
        _row(
            scope="pernos_2",
            description="Distancia maxima a borde Le2_z2",
            calculated_symbol="Le2_z2",
            limit_symbol="Le_max",
            comparison_text="<=",
            calculated=le2_z2.model_dump(),
            limit={"value": lemax_flange, "unit": le2_z2.unit},
            clause="AISC 360-22 J3.6",
            passed=le2_z2.value <= lemax_flange,
        ),
        _row(
            scope="viga",
            description="Altura de platina 1 no supera T del catalogo del perfil",
            calculated_symbol="hp1",
            limit_symbol="T",
            comparison_text="<=",
            calculated=case.geometry.web_plate_height.model_dump(),
            limit=t_catalog.model_dump(),
            clause="Indicacion de diseno del usuario (constructivo) + catalogo de secciones",
            passed=hp1_ok,
        ),
        _row(
            scope="platina_2",
            description="Ancho de platina 2 no supera bf del catalogo del perfil",
            calculated_symbol="bp2",
            limit_symbol="bf",
            comparison_text="<=",
            calculated=case.geometry.flange_plate_top_width.model_dump(),
            limit=bf_catalog.model_dump(),
            clause="Indicacion de diseno del usuario (constructivo) + catalogo de secciones",
            passed=bp2_ok,
        ),
    ]
    if nb2_z >= 4:
        rows.insert(
            len(rows) - 1,
            _row(
                scope="pernos_2",
                description="Separacion minima S2_z2 respecto a 2*Smin + 2*k1",
                calculated_symbol="S2_z2",
                limit_symbol="2*Smin + 2*k1",
                comparison_text=">=",
                calculated=s2z2.model_dump(),
                limit={"value": s2_z2_compound_limit, "unit": s2z2.unit},
                clause="Criterio solicitado por usuario (k1 desde catalogo)",
                passed=s2_z2_compound_ok,
            ),
        )
    if case.geometry.web_bolt_tightening_type in {"pretensioned", "slip_critical"}:
        tmin_web_kn = _minimum_bolt_pretension_kN(
            diameter_in=db_web_in,
            fabrication_standard=standard_web,
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
    if case.geometry.flange_bolt_tightening_type in {"pretensioned", "slip_critical"}:
        tmin_flange_kn = _minimum_bolt_pretension_kN(
            diameter_in=db_flange_in,
            fabrication_standard=standard_flange,
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
    memory = CalculationMemory(
        inputs={
            "beam_shape": case.sections.beam_right_shape,
            "db_web": db_web.model_dump(),
            "db_flange": db_flange.model_dump(),
            "s1_x": case.geometry.web_bolt_gage.model_dump(),
            "s1_y": case.geometry.web_bolt_pitch.model_dump(),
            "s2_x": case.geometry.flange_bolt_gage.model_dump(),
            "s2_z1": case.geometry.flange_bolt_pitch.model_dump(),
            "s2_z2": s2z2.model_dump(),
            "le1_x1": le1_x1.model_dump(),
            "le1_x2": le1_x2.model_dump(),
            "le1_y1": le1_y1.model_dump(),
            "le1_y2": le1_y2.model_dump(),
            "le2_x1": le2_x1.model_dump(),
            "le2_x2": le2_x2.model_dump(),
            "le2_z1": le2_z1.model_dump(),
            "le2_z2": le2_z2.model_dump(),
            "k1_catalog": k1_catalog.model_dump(),
            "hp1": case.geometry.web_plate_height.model_dump(),
            "T_catalog": t_catalog.model_dump(),
            "bp2": case.geometry.flange_plate_top_width.model_dump(),
            "bf_catalog": bf_catalog.model_dump(),
            "web_plate_surface_condition": web_surface,
            "web_plate_atmospheric_condition": web_atm,
            "flange_plate_surface_condition": flange_surface,
            "flange_plate_atmospheric_condition": flange_atm,
        },
        intermediates={
            "step_1_limits": rows,
            "step_1_notes": [
                {
                    "id": "bbmb_splice.step1.geometry_formulas_common_note",
                    "scope": "viga",
                    "description": "Parametro comun de formulas geometricas",
                    "clause": "Criterio solicitado por usuario",
                    "alpha_symbol": "sep",
                    "alpha": alpha.model_dump(),
                },
                {
                    "id": "bbmb_splice.step1.geometry_formulas_plt1_note",
                    "scope": "platina_1",
                    "description": "Formulas geometricas de platina 1",
                    "clause": "Criterio solicitado por usuario",
                    "hp1_formula": "hp1 = Le1.y1 + Le1.y2 + (nb1.y - 1) * S1.y",
                    "hp1_calc": {"value": hp1_calc, "unit": le1_y1.unit},
                    "bp1_formula": "bp1 = Le1.x1 + Le1.x2 + alpha + 2 * (nb1.x - 1) * S1.x",
                    "bp1_calc": {"value": bp1_calc, "unit": le1_x1.unit},
                },
                {
                    "id": "bbmb_splice.step1.geometry_formulas_plt2_note",
                    "scope": "platina_2",
                    "description": "Formulas geometricas de platina 2",
                    "clause": "Criterio solicitado por usuario",
                    "bp2_formula": "bp2 = Le2.z2 + Le2.z1 + S2.z2 + (nb2.z - 2) * S2.z1",
                    "bp2_calc": {"value": bp2_calc, "unit": le2_z1.unit},
                    "lp2_formula": "lp2 = 2 * (Le2.x1 + Le2.x2) + alpha + 2 * (nb2.x - 1) * S2.x + alpha",
                    "lp2_calc": {"value": lp2_calc, "unit": le2_x1.unit},
                }
            ],
            "edge_distance_table_row_web": le_meta_web.get("table_row"),
            "edge_distance_table_row_flange": le_meta_flange.get("table_row"),
            "j3_6_t_web_governing": t_web,
            "j3_6_t_flange_governing": t_flange,
        },
        design_factors={},
        equation="Step 1 Detailing: S>=3db (J3.3), Le>=Tabla J3.4, hp1<=T_catalog, bp2<=bf_catalog",
        units_trace={
            "db_web": db_web.unit,
            "db_flange": db_flange.unit,
            "s1_x": case.geometry.web_bolt_gage.unit,
            "s1_y": case.geometry.web_bolt_pitch.unit,
            "s2_x": case.geometry.flange_bolt_gage.unit,
            "s2_z1": case.geometry.flange_bolt_pitch.unit,
            "s2_z2": s2z2.unit,
            "le1_x1": le1_x1.unit,
            "le1_x2": le1_x2.unit,
            "le1_y1": le1_y1.unit,
            "le1_y2": le1_y2.unit,
            "le2_x1": le2_x1.unit,
            "le2_x2": le2_x2.unit,
            "le2_z1": le2_z1.unit,
            "le2_z2": le2_z2.unit,
            "k1_catalog": k1_catalog.unit,
            "hp1": case.geometry.web_plate_height.unit,
            "T_catalog": t_catalog.unit,
            "bf_catalog": bf_catalog.unit,
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

