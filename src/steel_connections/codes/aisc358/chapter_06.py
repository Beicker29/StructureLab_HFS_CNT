from __future__ import annotations

import math
from typing import Any

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def _expected_moment_unit(unit_system: UnitSystem) -> str:
    return "kip-in" if unit_system == UnitSystem.US else "kN-mm"


def _moment_to_base_force(moment: Quantity, length: Quantity, unit_system: UnitSystem) -> float:
    expected_moment_unit = _expected_moment_unit(unit_system)
    if moment.unit != expected_moment_unit:
        raise ValueError(f"Invalid moment unit. Expected '{expected_moment_unit}'.")
    validate_quantity_unit(length, "length", unit_system, "length")
    return moment.value / length.value


def compute_cpr(*, fy: Quantity, fu: Quantity, unit_system: UnitSystem) -> float:
    validate_quantity_unit(fy, "stress", unit_system, "materials.beam_fy")
    validate_quantity_unit(fu, "stress", unit_system, "materials.beam_fu")
    cpr = (fy.value + fu.value) / (2.0 * fy.value)
    return min(cpr, 1.2)


def compute_flange_slenderness_ratio(
    *,
    flange_width: Quantity,
    flange_thickness: Quantity,
    unit_system: UnitSystem,
) -> float:
    validate_quantity_unit(flange_width, "length", unit_system, "sections.bf")
    validate_quantity_unit(flange_thickness, "length", unit_system, "sections.tf")
    return flange_width.value / (2.0 * flange_thickness.value)


def compute_web_slenderness_ratio(
    *,
    section_depth: Quantity,
    k_design: Quantity,
    web_thickness: Quantity,
    unit_system: UnitSystem,
) -> tuple[float, dict[str, float]]:
    validate_quantity_unit(section_depth, "length", unit_system, "sections.d")
    validate_quantity_unit(k_design, "length", unit_system, "sections.kdes")
    validate_quantity_unit(web_thickness, "length", unit_system, "sections.tw")
    clear_web_depth = section_depth.value - 2.0 * k_design.value
    if clear_web_depth <= 0.0:
        raise ValueError("Computed clear web depth (d - 2*kdes) must be positive.")
    return clear_web_depth / web_thickness.value, {"clear_web_depth": clear_web_depth}


def compute_flange_slenderness_limit(
    *,
    elastic_modulus: Quantity,
    fy: Quantity,
    ry: float,
    member_ductility_demand: str,
    unit_system: UnitSystem,
) -> float:
    validate_quantity_unit(elastic_modulus, "stress", unit_system, "materials.elastic_modulus")
    validate_quantity_unit(fy, "stress", unit_system, "materials.beam_fy")
    if member_ductility_demand not in {"high", "moderate"}:
        raise ValueError("member_ductility_demand must be 'high' or 'moderate'.")
    factor = 0.30 if member_ductility_demand == "high" else 0.38
    return factor * math.sqrt(elastic_modulus.value / (ry * fy.value))


def compute_web_slenderness_limit(
    *,
    elastic_modulus: Quantity,
    fy: Quantity,
    ry: float,
    ca: float,
    member_ductility_demand: str,
    unit_system: UnitSystem,
) -> float:
    validate_quantity_unit(elastic_modulus, "stress", unit_system, "materials.elastic_modulus")
    validate_quantity_unit(fy, "stress", unit_system, "materials.beam_fy")
    if ca < 0.0 or ca >= 1.0:
        raise ValueError("Compactness coefficient Ca must satisfy 0 <= Ca < 1.")
    if member_ductility_demand not in {"high", "moderate"}:
        raise ValueError("member_ductility_demand must be 'high' or 'moderate'.")
    sqrt_term = math.sqrt(elastic_modulus.value / (ry * fy.value))
    if member_ductility_demand == "high":
        if ca <= 0.113:
            limit = 2.45 * (1.0 - 1.04 * ca) * sqrt_term
        else:
            limit = 2.26 * (1.0 - 0.38 * ca) * sqrt_term
    else:
        if ca <= 0.113:
            limit = 3.76 * (1.0 - 3.05 * ca) * sqrt_term
        else:
            limit = 2.61 * (1.0 - 0.49 * ca) * sqrt_term
    return max(limit, 1.56 * sqrt_term)


def compute_mpr(
    *,
    fy: Quantity,
    fu: Quantity,
    ry: float,
    ze: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(fy, "stress", unit_system, "materials.beam_fy")
    validate_quantity_unit(fu, "stress", unit_system, "materials.beam_fu")
    expected_ze_unit = "in3" if unit_system == UnitSystem.US else "mm3"
    if ze.unit != expected_ze_unit:
        raise ValueError(f"Invalid Ze unit. Expected '{expected_ze_unit}'.")
    cpr = compute_cpr(fy=fy, fu=fu, unit_system=unit_system)
    mpr_base = cpr * ry * fy.value * ze.value  # ksi*in3=kip-in, MPa*mm3=N-mm
    if unit_system == UnitSystem.US:
        return Quantity(value=mpr_base, unit="kip-in"), {"cpr": cpr, "ry": ry}
    return Quantity(value=mpr_base / 1000.0, unit="kN-mm"), {"cpr": cpr, "ry": ry, "nmm_to_knmm": 0.001}


def compute_sh(
    *,
    connection_type: str,
    beam_depth: Quantity,
    beam_flange_width: Quantity,
    stiffener_length: Quantity | None,
    end_plate_thickness: Quantity | None,
    unit_system: UnitSystem,
) -> Quantity:
    validate_quantity_unit(beam_depth, "length", unit_system, "beam_depth")
    validate_quantity_unit(beam_flange_width, "length", unit_system, "beam_flange_width")
    if connection_type == "bueep_4e":
        return Quantity(value=min(beam_depth.value / 2.0, 3.0 * beam_flange_width.value), unit=beam_depth.unit)
    if stiffener_length is None or end_plate_thickness is None:
        raise ValueError("Stiffened end-plate connections require stiffener_length and end_plate_thickness.")
    validate_quantity_unit(stiffener_length, "length", unit_system, "stiffener_length")
    validate_quantity_unit(end_plate_thickness, "length", unit_system, "end_plate_thickness")
    return Quantity(value=stiffener_length.value + end_plate_thickness.value, unit=beam_depth.unit)


def compute_vh(
    *,
    mpr: Quantity,
    lh: Quantity,
    vgravity_between_hinges: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(lh, "length", unit_system, "geometry.beam_clear_span_length")
    validate_quantity_unit(vgravity_between_hinges, "force", unit_system, "loads.beam_gravity_shear_between_hinges")
    base_shear = (2.0 * mpr.value) / lh.value
    vh_value = base_shear + vgravity_between_hinges.value
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    return Quantity(value=vh_value, unit=force_unit), {"2mpr_over_lh": base_shear}


def compute_mf(
    *,
    mpr: Quantity,
    vh: Quantity,
    sh: Quantity,
    unit_system: UnitSystem,
) -> Quantity:
    validate_quantity_unit(vh, "force", unit_system, "vh")
    validate_quantity_unit(sh, "length", unit_system, "sh")
    moment_unit = _expected_moment_unit(unit_system)
    if mpr.unit != moment_unit:
        raise ValueError(f"Invalid Mpr unit. Expected '{moment_unit}'.")
    return Quantity(value=mpr.value + vh.value * sh.value, unit=moment_unit)


def compute_end_plate_yield_line_parameter(
    *,
    connection_type: str,
    bp: Quantity,
    g: Quantity,
    pfi: Quantity,
    pfo: Quantity,
    de: Quantity,
    pb: Quantity | None,
    h1: Quantity,
    h2: Quantity,
    h3: Quantity | None,
    h4: Quantity | None,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Any]]:
    """Compute end-plate yield-line parameter ``Yp``.

    Equation source:
    - AISC 358-22 Tables 6.2, 6.3 and 6.4
    """

    for name, value in {
        "bp": bp,
        "g": g,
        "pfi": pfi,
        "pfo": pfo,
        "de": de,
        "h1": h1,
        "h2": h2,
    }.items():
        validate_quantity_unit(value, "length", unit_system, name)
        if value.value <= 0.0:
            raise ValueError(f"{name} must be positive.")
    if pb is not None:
        validate_quantity_unit(pb, "length", unit_system, "pb")
        if connection_type == "bseep_8es" and pb.value <= 0.0:
            raise ValueError("pb must be positive.")
    if h3 is not None:
        validate_quantity_unit(h3, "length", unit_system, "h3")
    if h4 is not None:
        validate_quantity_unit(h4, "length", unit_system, "h4")

    s = Quantity(value=0.5 * math.sqrt(bp.value * g.value), unit=bp.unit)
    pfi_eff = Quantity(value=min(pfi.value, s.value), unit=pfi.unit)
    de_le_s = de.value <= s.value + 1e-9
    case_ref = "N/A"

    if connection_type == "bueep_4e":
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
    elif connection_type == "bseep_4es":
        yp_value = (
            (bp.value / 2.0)
            * (
                h2.value * ((1.0 / pfi_eff.value) + (1.0 / s.value))
                + h1.value * (
                    (1.0 / pfo.value) + (1.0 / (2.0 * de.value))
                    if de_le_s
                    else (1.0 / s.value) + (1.0 / pfo.value)
                )
            )
            + (2.0 / g.value)
            * (
                h2.value * (pfi_eff.value + s.value)
                + h1.value * ((de.value + pfo.value) if de_le_s else (s.value + pfo.value))
            )
        )
        case_ref = "Case 1 (de <= s)" if de_le_s else "Case 2 (de > s)"
        table_ref = "AISC 358-22 Table 6.3"
        formula_text = (
            "Yp = bp/2*[h2*(1/pfi + 1/s) + h1*(1/pfo + 1/(2de))] + "
            "(2/g)*[h2*(pfi + s) + h1*(de + pfo)]"
            if de_le_s
            else "Yp = bp/2*[h2*(1/pfi + 1/s) + h1*(1/s + 1/pfo)] + "
            "(2/g)*[h2*(pfi + s) + h1*(s + pfo)]"
        )
    elif connection_type == "bseep_8es":
        if pb is None or h3 is None or h4 is None:
            raise ValueError("bseep_8es requires pb, h3 and h4 to compute Yp.")
        yp_value = (
            (bp.value / 2.0)
            * (
                h1.value * ((1.0 / (2.0 * de.value)) if de_le_s else (1.0 / s.value))
                + h2.value * (1.0 / pfo.value)
                + h3.value * (1.0 / pfi_eff.value)
                + h4.value * (1.0 / s.value)
            )
            + (2.0 / g.value)
            * (
                h1.value * ((de.value + 3.0 * pb.value / 4.0) if de_le_s else (s.value + pb.value / 4.0))
                + h2.value * (pfo.value + (pb.value / 4.0 if de_le_s else 3.0 * pb.value / 4.0))
                + h3.value * (pfi_eff.value + (3.0 * pb.value / 4.0 if de_le_s else pb.value / 4.0))
                + h4.value * (s.value + (pb.value / 4.0 if de_le_s else 3.0 * pb.value / 4.0))
            )
            + g.value
        )
        case_ref = "Case 1 (de <= s)" if de_le_s else "Case 2 (de > s)"
        table_ref = "AISC 358-22 Table 6.4"
        formula_text = (
            "Yp = bp/2*[h1*(1/(2de)) + h2*(1/pfo) + h3*(1/pfi) + h4*(1/s)] + "
            "(2/g)*[h1*(de + 3pb/4) + h2*(pfo + pb/4) + h3*(pfi + 3pb/4) + h4*(s + pb/4)] + g"
            if de_le_s
            else "Yp = bp/2*[h1*(1/s) + h2*(1/pfo) + h3*(1/pfi) + h4*(1/s)] + "
            "(2/g)*[h1*(s + pb/4) + h2*(pfo + 3pb/4) + h3*(pfi + pb/4) + h4*(s + 3pb/4)] + g"
        )
    else:
        raise ValueError(f"Unsupported connection_type '{connection_type}' for Yp.")

    return Quantity(value=yp_value, unit=bp.unit), {
        "table_reference": table_ref,
        "case_reference": case_ref,
        "formula": formula_text,
        "s": s.model_dump(),
        "pfi_input": pfi.model_dump(),
        "pfi_effective": pfi_eff.model_dump(),
        "de": de.model_dump(),
        "de_le_s": de_le_s,
        "is_hardcoded": False,
    }


def compute_column_flange_yield_line_parameter(
    *,
    connection_type: str,
    is_stiffened: bool,
    bcf: Quantity,
    g: Quantity,
    h1: Quantity,
    h2: Quantity,
    unit_system: UnitSystem,
    c: Quantity | None = None,
    pso: Quantity | None = None,
    psi: Quantity | None = None,
    pb: Quantity | None = None,
    h3: Quantity | None = None,
    h4: Quantity | None = None,
) -> tuple[Quantity, dict[str, Any]]:
    """Compute column-flange yield-line parameter ``Yc`` or ``Ycs``.

    Equation source:
    - AISC 358-22 Table 6.5 for four-bolt extended end-plate connections
    - AISC 358-22 Table 6.6 for eight-bolt extended end-plate connections
    """

    for name, value in {"bcf": bcf, "g": g, "h1": h1, "h2": h2}.items():
        validate_quantity_unit(value, "length", unit_system, name)
        if value.value <= 0.0:
            raise ValueError(f"{name} must be positive.")

    s = Quantity(value=0.5 * math.sqrt(bcf.value * g.value), unit=bcf.unit)
    case_ref = "N/A"

    if connection_type in {"bueep_4e", "bseep_4es"}:
        if is_stiffened:
            if pso is None or psi is None:
                raise ValueError("Stiffened four-bolt column flange requires pso and psi.")
            validate_quantity_unit(pso, "length", unit_system, "pso")
            validate_quantity_unit(psi, "length", unit_system, "psi")
            psi_eff = Quantity(value=min(psi.value, s.value), unit=psi.unit)
            y_value = (
                (bcf.value / 2.0)
                * (
                    h2.value * ((1.0 / s.value) + (1.0 / psi_eff.value))
                    + h1.value * ((1.0 / s.value) + (1.0 / pso.value))
                )
                + (2.0 / g.value) * (h2.value * (s.value + psi_eff.value) + h1.value * (s.value + pso.value))
            )
            table_ref = "AISC 358-22 Table 6.5"
            formula_text = (
                "Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + "
                "(2/g)*[h2*(s + psi) + h1*(s + pso)]"
            )
            case_ref = "Case 1 (psi <= s)" if psi.value <= s.value + 1e-9 else "Case 2 (psi > s)"
            metadata = {"pso": pso.model_dump(), "psi_input": psi.model_dump(), "psi_effective": psi_eff.model_dump()}
        else:
            if c is None:
                raise ValueError("Unstiffened four-bolt column flange requires c.")
            validate_quantity_unit(c, "length", unit_system, "c")
            y_value = (
                (bcf.value / 2.0) * (h2.value * (1.0 / s.value) + h1.value * (1.0 / s.value))
                + (2.0 / g.value) * (h2.value * (s.value + 3.0 * c.value / 4.0) + h1.value * (s.value + c.value / 4.0) + (c.value**2) / 2.0)
                + g.value
            )
            table_ref = "AISC 358-22 Table 6.5"
            formula_text = (
                "Y_c = bcf/2*[h2*(1/s) + h1*(1/s)] + "
                "(2/g)*[h2*(s + 3c/4) + h1*(s + c/4) + c^2/2] + g"
            )
            metadata = {"c": c.model_dump()}
    elif connection_type == "bseep_8es":
        if h3 is None or h4 is None or pb is None:
            raise ValueError("Eight-bolt column flange requires pb, h3 and h4.")
        validate_quantity_unit(pb, "length", unit_system, "pb")
        validate_quantity_unit(h3, "length", unit_system, "h3")
        validate_quantity_unit(h4, "length", unit_system, "h4")
        if is_stiffened:
            if pso is None or psi is None:
                raise ValueError("Stiffened eight-bolt column flange requires pso and psi.")
            validate_quantity_unit(pso, "length", unit_system, "pso")
            validate_quantity_unit(psi, "length", unit_system, "psi")
            psi_eff = Quantity(value=min(psi.value, s.value), unit=psi.unit)
            y_value = (
                (bcf.value / 2.0)
                * (
                    h1.value * (1.0 / s.value)
                    + h2.value * (1.0 / pso.value)
                    + h3.value * (1.0 / psi_eff.value)
                    + h4.value * (1.0 / s.value)
                )
                + (2.0 / g.value)
                * (
                    h1.value * (s.value + pb.value / 4.0)
                    + h2.value * (pso.value + 3.0 * pb.value / 4.0)
                    + h3.value * (psi_eff.value + pb.value / 4.0)
                    + h4.value * (s.value + 3.0 * pb.value / 4.0)
                    + (pb.value**2) / 2.0
                )
                + g.value
            )
            table_ref = "AISC 358-22 Table 6.6"
            formula_text = (
                "Y_cs = bcf/2*[h1*(1/s) + h2*(1/pso) + h3*(1/psi) + h4*(1/s)] + "
                "(2/g)*[h1*(s + pb/4) + h2*(pso + 3pb/4) + h3*(psi + pb/4) + h4*(s + 3pb/4) + pb^2/2] + g"
            )
            case_ref = "Case 1 (psi <= s)" if psi.value <= s.value + 1e-9 else "Case 2 (psi > s)"
            metadata = {"pso": pso.model_dump(), "psi_input": psi.model_dump(), "psi_effective": psi_eff.model_dump(), "pb": pb.model_dump()}
        else:
            if c is None:
                raise ValueError("Unstiffened eight-bolt column flange requires c.")
            validate_quantity_unit(c, "length", unit_system, "c")
            y_value = (
                (bcf.value / 2.0) * (h1.value * (1.0 / s.value) + h4.value * (1.0 / s.value))
                + (2.0 / g.value)
                * (
                    h1.value * (pb.value + c.value / 2.0 + s.value)
                    + h2.value * (pb.value / 2.0 + c.value / 4.0)
                    + h3.value * (pb.value / 2.0 + c.value / 2.0)
                    + h4.value * s.value
                )
                + g.value / 2.0
            )
            table_ref = "AISC 358-22 Table 6.6"
            formula_text = (
                "Y_c = bcf/2*[h1*(1/s) + h4*(1/s)] + "
                "(2/g)*[h1*(pb + c/2 + s) + h2*(pb/2 + c/4) + h3*(pb/2 + c/2) + h4*(s)] + g/2"
            )
            metadata = {"c": c.model_dump(), "pb": pb.model_dump()}
    else:
        raise ValueError(f"Unsupported connection_type '{connection_type}' for column flange Y parameter.")

    return Quantity(value=y_value, unit=bcf.unit), {
        "table_reference": table_ref,
        "case_reference": case_ref,
        "formula": formula_text,
        "s": s.model_dump(),
        "is_hardcoded": False,
        **metadata,
    }


def compute_beam_flange_force_from_mf(
    *,
    mf: Quantity,
    beam_depth: Quantity,
    beam_flange_thickness: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(beam_depth, "length", unit_system, "geometry.beam_depth")
    validate_quantity_unit(
        beam_flange_thickness,
        "length",
        unit_system,
        "geometry.beam_flange_thickness",
    )
    expected_moment_unit = "kip-in" if unit_system == UnitSystem.US else "kN-mm"
    if mf.unit != expected_moment_unit:
        raise ValueError(
            f"Invalid unit for probable moment. Expected '{expected_moment_unit}', got '{mf.unit}'."
        )

    lever_arm = beam_depth.value - beam_flange_thickness.value
    if lever_arm <= 0.0:
        raise ValueError("Beam depth must be greater than beam flange thickness.")
    flange_force = mf.value / lever_arm
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    return Quantity(value=flange_force, unit=force_unit), {"lever_arm": lever_arm}


def compute_required_bolt_diameter(
    *,
    mf: Quantity,
    bolt_fnt: Quantity,
    phi_n: float,
    bolt_line_distances: list[Quantity],
    n_bolts_per_line: int,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(bolt_fnt, "stress", unit_system, "materials.bolt_fnt")
    if not bolt_line_distances:
        raise ValueError("At least one bolt line distance is required.")
    sum_h = 0.0
    for idx, distance in enumerate(bolt_line_distances):
        validate_quantity_unit(distance, "length", unit_system, f"bolt_line_distances[{idx}]")
        sum_h += distance.value
    if sum_h <= 0.0:
        raise ValueError("Sum of bolt line distances must be positive.")
    # Eq. 6.7-3/6.7-4 interpreted from AISC 358-22 transcription.
    db_sq = (2.0 * mf.value) / (phi_n * math.pi * n_bolts_per_line * bolt_fnt.value * sum_h)
    if db_sq <= 0.0:
        raise ValueError("Required bolt diameter squared is non-positive.")
    length_unit = "in" if unit_system == UnitSystem.US else "mm"
    return Quantity(value=math.sqrt(db_sq), unit=length_unit), {
        "sum_h": sum_h,
        "n_bolts_per_line": float(n_bolts_per_line),
        "db_sq": db_sq,
        "phi_n": phi_n,
    }


def compute_minimum_bolt_spacing(
    *,
    bolt_diameter: Quantity,
    unit_system: UnitSystem,
) -> Quantity:
    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")
    return Quantity(value=3.0 * bolt_diameter.value, unit=bolt_diameter.unit)


def compute_minimum_edge_distance_standard_hole(
    *,
    bolt_diameter: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float | str]]:
    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")

    db_in = bolt_diameter.value if unit_system == UnitSystem.US else bolt_diameter.value / 25.4
    table_j34_us: list[tuple[float, float]] = [
        (0.5, 0.75),
        (0.625, 0.875),
        (0.75, 1.0),
        (0.875, 1.125),
        (1.0, 1.25),
        (1.125, 1.5),
        (1.25, 1.625),
    ]
    tolerance = 1e-3
    edge_in: float | None = None
    matched_row: str | None = None
    for nominal_db, min_edge in table_j34_us:
        if abs(db_in - nominal_db) <= tolerance:
            edge_in = min_edge
            matched_row = f"db={nominal_db} in"
            break
    if edge_in is None and db_in > 1.25 + tolerance:
        edge_in = 1.75
        matched_row = "db>1.25 in"
    if edge_in is None:
        raise ValueError(
            "Bolt nominal diameter is not a supported Table J3.4 value and is not greater than 1-1/4 in."
        )

    if unit_system == UnitSystem.US:
        return Quantity(value=edge_in, unit="in"), {"db_in": db_in, "table_row": matched_row}
    return Quantity(value=edge_in * 25.4, unit="mm"), {"db_in": db_in, "table_row": matched_row, "in_to_mm": 25.4}


def compute_required_end_plate_thickness(
    *,
    mf: Quantity,
    beam_depth: Quantity,
    end_plate_fy: Quantity,
    yp: Quantity,
    phi_d: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(beam_depth, "length", unit_system, "beam_depth")
    validate_quantity_unit(end_plate_fy, "stress", unit_system, "end_plate_fy")
    validate_quantity_unit(yp, "length", unit_system, "yp")
    tp_req = 1.11 * mf.value / (phi_d * beam_depth.value * end_plate_fy.value * yp.value)
    length_unit = "in" if unit_system == UnitSystem.US else "mm"
    return Quantity(value=tp_req, unit=length_unit), {"phi_d": phi_d}


def compute_end_plate_shear_yielding_capacity(
    *,
    end_plate_fy: Quantity,
    end_plate_width: Quantity,
    end_plate_thickness: Quantity,
    beam_flange_width: Quantity,
    phi_d: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(end_plate_fy, "stress", unit_system, "materials.end_plate_fy")
    validate_quantity_unit(end_plate_width, "length", unit_system, "geometry.end_plate_width")
    validate_quantity_unit(
        end_plate_thickness,
        "length",
        unit_system,
        "geometry.end_plate_thickness",
    )
    validate_quantity_unit(beam_flange_width, "length", unit_system, "geometry.beam_flange_width")

    end_plate_width_effective = min(
        end_plate_width.value,
        beam_flange_width.value + (1.0 if unit_system == UnitSystem.US else 25.0),
    )
    nominal_strength = 0.6 * end_plate_fy.value * end_plate_width_effective * end_plate_thickness.value
    design_strength = phi_d * nominal_strength
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        design_strength /= 1000.0
        nominal_strength /= 1000.0
    return Quantity(value=design_strength, unit=force_unit), {
        "bp_effective": end_plate_width_effective,
        "nominal_strength": nominal_strength,
        "phi_d": phi_d,
    }


def compute_end_plate_shear_rupture_capacity(
    *,
    end_plate_fu: Quantity,
    end_plate_width: Quantity,
    end_plate_thickness: Quantity,
    bolt_diameter: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(end_plate_fu, "stress", unit_system, "materials.end_plate_fu")
    validate_quantity_unit(end_plate_width, "length", unit_system, "geometry.end_plate_width")
    validate_quantity_unit(
        end_plate_thickness,
        "length",
        unit_system,
        "geometry.end_plate_thickness",
    )
    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")

    hole_addition = 0.125 if unit_system == UnitSystem.US else 3.0
    net_width = end_plate_width.value - 2.0 * (bolt_diameter.value + hole_addition)
    if net_width <= 0.0:
        raise ValueError("Net end-plate width is non-positive for Eq. 6.7-8.")

    net_area = end_plate_thickness.value * net_width
    nominal_strength = 0.6 * end_plate_fu.value * net_area
    design_strength = phi_n * nominal_strength
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        design_strength /= 1000.0
        nominal_strength /= 1000.0
    return Quantity(value=design_strength, unit=force_unit), {
        "hole_addition": hole_addition,
        "net_width": net_width,
        "net_area": net_area,
        "nominal_strength": nominal_strength,
        "phi_n": phi_n,
    }


def compute_end_plate_hole_tearout_capacity(
    *,
    end_plate_fu: Quantity,
    clear_distance_lc: Quantity,
    end_plate_thickness: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(end_plate_fu, "stress", unit_system, "materials.end_plate_fu")
    validate_quantity_unit(clear_distance_lc, "length", unit_system, "geometry.lc")
    validate_quantity_unit(end_plate_thickness, "length", unit_system, "geometry.end_plate_thickness")

    nominal_strength = 1.2 * clear_distance_lc.value * end_plate_thickness.value * end_plate_fu.value
    design_strength = phi_n * nominal_strength
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        design_strength /= 1000.0
        nominal_strength /= 1000.0
    return Quantity(value=design_strength, unit=force_unit), {
        "nominal_strength": nominal_strength,
        "phi_n": phi_n,
    }


def compute_end_plate_hole_bearing_capacity(
    *,
    end_plate_fu: Quantity,
    bolt_diameter: Quantity,
    end_plate_thickness: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(end_plate_fu, "stress", unit_system, "materials.end_plate_fu")
    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")
    validate_quantity_unit(end_plate_thickness, "length", unit_system, "geometry.end_plate_thickness")

    nominal_strength = 2.4 * bolt_diameter.value * end_plate_thickness.value * end_plate_fu.value
    design_strength = phi_n * nominal_strength
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        design_strength /= 1000.0
        nominal_strength /= 1000.0
    return Quantity(value=design_strength, unit=force_unit), {
        "nominal_strength": nominal_strength,
        "phi_n": phi_n,
    }


def compute_bolt_shear_rupture_capacity(
    *,
    bolt_fnv: Quantity,
    bolt_diameter: Quantity,
    n_bolts_compression: int,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(bolt_fnv, "stress", unit_system, "materials.bolt_fnv")
    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")

    bolt_area = math.pi * (bolt_diameter.value**2) / 4.0
    nominal_strength = n_bolts_compression * bolt_fnv.value * bolt_area
    design_strength = phi_n * nominal_strength
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        design_strength /= 1000.0
        nominal_strength /= 1000.0
    return Quantity(value=design_strength, unit=force_unit), {
        "n_bolts_compression": n_bolts_compression,
        "bolt_area": bolt_area,
        "nominal_strength": nominal_strength,
        "phi_n": phi_n,
    }


def compute_bolt_bearing_tearout_capacity(
    *,
    material_fu: Quantity,
    clear_distance: Quantity,
    plate_thickness: Quantity,
    bolt_diameter: Quantity,
    n_bolts_compression: int,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(material_fu, "stress", unit_system, "material_fu")
    validate_quantity_unit(clear_distance, "length", unit_system, "clear_distance")
    validate_quantity_unit(plate_thickness, "length", unit_system, "plate_thickness")
    validate_quantity_unit(bolt_diameter, "length", unit_system, "bolt_diameter")

    rni_1 = 1.2 * clear_distance.value * plate_thickness.value * material_fu.value
    rni_2 = 2.4 * bolt_diameter.value * plate_thickness.value * material_fu.value
    per_bolt_nominal = min(rni_1, rni_2)
    nominal_strength = n_bolts_compression * per_bolt_nominal
    design_strength = phi_n * nominal_strength
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        design_strength /= 1000.0
        nominal_strength /= 1000.0
    return Quantity(value=design_strength, unit=force_unit), {
        "rni_case_1": rni_1,
        "rni_case_2": rni_2,
        "rni_per_bolt": per_bolt_nominal,
        "n_bolts_compression": n_bolts_compression,
        "nominal_strength": nominal_strength,
        "phi_n": phi_n,
    }


def compute_minimum_stiffener_length(stiffener_height: Quantity, unit_system: UnitSystem) -> Quantity:
    validate_quantity_unit(stiffener_height, "length", unit_system, "geometry.stiffener_height")
    return Quantity(
        value=stiffener_height.value / math.tan(math.radians(30.0)),
        unit=stiffener_height.unit,
    )


def compute_required_stiffener_thickness(
    *,
    beam_web_thickness: Quantity,
    beam_fy: Quantity,
    stiffener_fy: Quantity,
    unit_system: UnitSystem,
) -> Quantity:
    validate_quantity_unit(beam_web_thickness, "length", unit_system, "geometry.beam_web_thickness")
    validate_quantity_unit(beam_fy, "stress", unit_system, "materials.beam_fy")
    validate_quantity_unit(stiffener_fy, "stress", unit_system, "materials.stiffener_fy")
    return Quantity(
        value=beam_web_thickness.value * (beam_fy.value / stiffener_fy.value),
        unit=beam_web_thickness.unit,
    )


def compute_stiffener_slenderness_ratio_limit(
    *,
    elastic_modulus: Quantity,
    stiffener_fy: Quantity,
    unit_system: UnitSystem,
) -> float:
    validate_quantity_unit(elastic_modulus, "stress", unit_system, "materials.elastic_modulus")
    validate_quantity_unit(stiffener_fy, "stress", unit_system, "materials.stiffener_fy")
    return 0.56 * math.sqrt(elastic_modulus.value / stiffener_fy.value)


def compute_column_flange_required_thickness(
    *,
    mf: Quantity,
    beam_depth: Quantity,
    column_fy: Quantity,
    yc: Quantity,
    phi_d: float,
    unit_system: UnitSystem,
) -> Quantity:
    validate_quantity_unit(beam_depth, "length", unit_system, "beam_depth")
    validate_quantity_unit(column_fy, "stress", unit_system, "materials.column_fy")
    validate_quantity_unit(yc, "length", unit_system, "yc")
    tcf_req = 1.11 * mf.value / (phi_d * beam_depth.value * column_fy.value * yc.value)
    return Quantity(value=tcf_req, unit=beam_depth.unit)


def compute_column_flange_design_force_from_yield_line(
    *,
    beam_depth: Quantity,
    beam_flange_thickness: Quantity,
    column_fy: Quantity,
    yc: Quantity,
    column_flange_thickness: Quantity,
    phi_d: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(beam_depth, "length", unit_system, "beam_depth")
    validate_quantity_unit(beam_flange_thickness, "length", unit_system, "beam_flange_thickness")
    validate_quantity_unit(column_fy, "stress", unit_system, "column_fy")
    validate_quantity_unit(yc, "length", unit_system, "yc")
    validate_quantity_unit(column_flange_thickness, "length", unit_system, "column_flange_thickness")
    lever_arm = beam_depth.value - beam_flange_thickness.value
    if lever_arm <= 0.0:
        raise ValueError("Beam lever arm for column flange force must be positive.")
    mcf_design = phi_d * column_fy.value * yc.value * (column_flange_thickness.value**2)
    force_value = mcf_design / lever_arm
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        force_value /= 1000.0
        mcf_design /= 1000.0
    return Quantity(value=force_value, unit=force_unit), {"mcf_design": mcf_design, "lever_arm": lever_arm}


def compute_column_web_local_yielding_strength(
    *,
    ct: float,
    kc: Quantity,
    lb: Quantity,
    column_fy: Quantity,
    column_web_thickness: Quantity,
    phi_d: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(kc, "length", unit_system, "kc")
    validate_quantity_unit(lb, "length", unit_system, "lb")
    validate_quantity_unit(column_fy, "stress", unit_system, "column_fy")
    validate_quantity_unit(column_web_thickness, "length", unit_system, "column_web_thickness")
    rn_nominal = (6.0 * ct * kc.value + lb.value) * column_fy.value * column_web_thickness.value
    rn_design = phi_d * rn_nominal
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        rn_nominal /= 1000.0
        rn_design /= 1000.0
    return Quantity(value=rn_design, unit=force_unit), {"rn_nominal": rn_nominal, "ct": ct}


def compute_column_web_local_yielding_strength_eq_2_2_11(
    *,
    ct: float,
    kc: Quantity,
    tp: Quantity,
    n: Quantity,
    column_fy: Quantity,
    column_web_thickness: Quantity,
    phi_d: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    """Compute design strength for local web yielding using Eq. (2.2-11)-style form.

    Equation:
    ``phiRn = phi * [Ct*(6*k + 2*tp) + N] * Fy * tw``

    Reference:
    - User-provided Eq. (2.2-11) format for Chapter 6 column-web check adaptation.
    """

    validate_quantity_unit(kc, "length", unit_system, "kc")
    validate_quantity_unit(tp, "length", unit_system, "tp")
    validate_quantity_unit(n, "length", unit_system, "n")
    validate_quantity_unit(column_fy, "stress", unit_system, "column_fy")
    validate_quantity_unit(column_web_thickness, "length", unit_system, "column_web_thickness")

    rn_nominal = (ct * (6.0 * kc.value + 2.0 * tp.value) + n.value) * column_fy.value * column_web_thickness.value
    rn_design = phi_d * rn_nominal
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        rn_nominal /= 1000.0
        rn_design /= 1000.0
    return Quantity(value=rn_design, unit=force_unit), {"rn_nominal": rn_nominal, "ct": ct}


def compute_column_web_local_crippling_strength(
    *,
    lb: Quantity,
    column_depth: Quantity,
    column_web_thickness: Quantity,
    column_flange_thickness: Quantity,
    elastic_modulus: Quantity,
    column_fy: Quantity,
    distance_to_column_end: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(lb, "length", unit_system, "lb")
    validate_quantity_unit(column_depth, "length", unit_system, "column_depth")
    validate_quantity_unit(column_web_thickness, "length", unit_system, "column_web_thickness")
    validate_quantity_unit(column_flange_thickness, "length", unit_system, "column_flange_thickness")
    validate_quantity_unit(elastic_modulus, "stress", unit_system, "elastic_modulus")
    validate_quantity_unit(column_fy, "stress", unit_system, "column_fy")
    validate_quantity_unit(distance_to_column_end, "length", unit_system, "distance_to_column_end")

    lb_over_dc = lb.value / column_depth.value
    common = (column_web_thickness.value**2) * (
        1.0
        + 3.0 * (lb.value / column_depth.value) * ((column_web_thickness.value / column_flange_thickness.value) ** 1.5)
    ) * math.sqrt((elastic_modulus.value * column_fy.value * column_flange_thickness.value) / column_web_thickness.value)

    if distance_to_column_end.value >= column_depth.value / 2.0:
        rn_nominal = 0.80 * common
        case_name = "eq_6_7_19"
    elif lb_over_dc <= 0.2:
        rn_nominal = 0.40 * common
        case_name = "eq_6_7_20"
    else:
        rn_nominal = 0.40 * (
            (column_web_thickness.value**2)
            * (
                1.0
                + 0.24 * (lb.value / column_depth.value) * ((column_web_thickness.value / column_flange_thickness.value) ** 1.5)
            )
            * math.sqrt((elastic_modulus.value * column_fy.value * column_flange_thickness.value) / column_web_thickness.value)
        )
        case_name = "eq_6_7_21"

    phi = 0.75
    rn_design = phi * rn_nominal
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        rn_nominal /= 1000.0
        rn_design /= 1000.0
    return Quantity(value=rn_design, unit=force_unit), {"rn_nominal": rn_nominal, "phi": phi, "case": case_name}


def compute_column_web_local_buckling_strength(
    *,
    ct: float,
    column_web_thickness: Quantity,
    clear_web_depth: Quantity,
    elastic_modulus: Quantity,
    column_fy: Quantity,
    phi: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    """Compute design strength for column web local buckling (WCB).

    Equation:
    ``phiRn = phi * Ct * 24 * tw^3 * sqrt(E*Fy) / h``
    where ``h = d_col - 2*kc``.

    Reference:
    - AISC 358-22 Chapter 6, web local buckling (WCB) format.
    """

    validate_quantity_unit(column_web_thickness, "length", unit_system, "column_web_thickness")
    validate_quantity_unit(clear_web_depth, "length", unit_system, "clear_web_depth")
    validate_quantity_unit(elastic_modulus, "stress", unit_system, "elastic_modulus")
    validate_quantity_unit(column_fy, "stress", unit_system, "column_fy")
    if clear_web_depth.value <= 0.0:
        raise ValueError("Computed clear web depth h = d_col - 2*kc must be positive.")
    if ct <= 0.0:
        raise ValueError("Ct factor must be positive.")
    if phi <= 0.0:
        raise ValueError("Resistance factor phi must be positive.")

    rn_nominal = (
        ct
        * 24.0
        * (column_web_thickness.value**3)
        * math.sqrt(elastic_modulus.value * column_fy.value)
        / clear_web_depth.value
    )
    rn_design = phi * rn_nominal
    force_unit = "kip" if unit_system == UnitSystem.US else "kN"
    if unit_system == UnitSystem.SI:
        rn_nominal /= 1000.0
        rn_design /= 1000.0
    return Quantity(value=rn_design, unit=force_unit), {"rn_nominal": rn_nominal, "ct": ct, "phi": phi}
