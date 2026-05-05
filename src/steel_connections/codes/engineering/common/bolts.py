from __future__ import annotations

import math
from typing import Any

from steel_connections.codes.engineering.constants import AISCConstants
from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def _to_in(value: Quantity, unit_system: UnitSystem) -> float:
    validate_quantity_unit(value, "length", unit_system, "geometry.bolt_diameter")
    return value.value if unit_system == UnitSystem.US else value.value / 25.4


def _from_in(length_in: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=length_in, unit="in")
    return Quantity(value=length_in * 25.4, unit="mm")


def compute_bolt_hole_dimensions_j33(
    *,
    bolt_diameter: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Quantity | float | str]:
    """Compute nominal hole dimensions from AISC 360-22 Table J3.3.

    Returned values:
    - standard_diameter
    - oversize_diameter
    - short_slot_width
    - short_slot_length
    - long_slot_width
    - long_slot_length
    """

    db_in = _to_in(bolt_diameter, unit_system)
    tol = 1e-3

    # Explicit rows up to 1 in from Table J3.3.
    explicit_rows_us: list[tuple[float, tuple[float, float, float, float, float, float], str]] = [
        (0.5, (0.5625, 0.625, 0.5625, 0.6875, 0.5625, 1.25), "db=0.5 in"),
        (0.625, (0.6875, 0.8125, 0.6875, 0.875, 0.6875, 1.5625), "db=0.625 in"),
        (0.75, (0.8125, 0.9375, 0.8125, 1.0, 0.8125, 1.875), "db=0.75 in"),
        (0.875, (0.9375, 1.0625, 0.9375, 1.125, 0.9375, 2.1875), "db=0.875 in"),
        (1.0, (1.125, 1.25, 1.125, 1.3125, 1.125, 2.5), "db=1.0 in"),
    ]

    standard_in: float | None = None
    oversize_in: float | None = None
    short_slot_w_in: float | None = None
    short_slot_l_in: float | None = None
    long_slot_w_in: float | None = None
    long_slot_l_in: float | None = None
    table_case: str | None = None

    for nominal_db, values, label in explicit_rows_us:
        if abs(db_in - nominal_db) <= tol:
            (
                standard_in,
                oversize_in,
                short_slot_w_in,
                short_slot_l_in,
                long_slot_w_in,
                long_slot_l_in,
            ) = values
            table_case = label
            break

    # For db >= 1-1/8 in, Table J3.3 gives formula-based rows.
    if standard_in is None and db_in >= (1.125 - tol):
        standard_in = db_in + 0.125
        oversize_in = db_in + 0.3125
        short_slot_w_in = db_in + 0.125
        short_slot_l_in = db_in + 0.375
        long_slot_w_in = db_in + 0.125
        long_slot_l_in = 2.5 * db_in
        table_case = "db>=1.125 in"

    if (
        standard_in is None
        or oversize_in is None
        or short_slot_w_in is None
        or short_slot_l_in is None
        or long_slot_w_in is None
        or long_slot_l_in is None
        or table_case is None
    ):
        raise ValueError(
            "Bolt nominal diameter is not a supported Table J3.3 value."
        )

    return {
        "db_in": db_in,
        "table_case": table_case,
        "standard_diameter": _from_in(standard_in, unit_system),
        "oversize_diameter": _from_in(oversize_in, unit_system),
        "short_slot_width": _from_in(short_slot_w_in, unit_system),
        "short_slot_length": _from_in(short_slot_l_in, unit_system),
        "long_slot_width": _from_in(long_slot_w_in, unit_system),
        "long_slot_length": _from_in(long_slot_l_in, unit_system),
        "standard_increment_in": standard_in - db_in,
        "oversize_increment_in": oversize_in - db_in,
    }


def compute_standard_hole_diameter_j33(
    *,
    bolt_diameter: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float | str]]:
    """Compute standard-hole diameter from AISC 360-22 Table J3.3."""

    dimensions = compute_bolt_hole_dimensions_j33(
        bolt_diameter=bolt_diameter,
        unit_system=unit_system,
    )
    standard = dimensions["standard_diameter"]
    if not isinstance(standard, Quantity):
        raise ValueError("Internal error: expected Quantity for standard hole diameter.")
    return standard, {
        "db_in": float(dimensions["db_in"]),
        "table_case": str(dimensions["table_case"]),
        "hole_add_in": float(dimensions["standard_increment_in"]),
    }


def compute_spacing_requirements_j33(
    *,
    bolt_diameter: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Quantity]:
    """Compute spacing requirements per AISC 360-22 Section J3.3.

    Returns:
    - center_to_center_min_code: 2.667*d
    - center_to_center_preferred: 3*d (user note preference)
    - clear_distance_min: d
    """

    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")
    return {
        "center_to_center_min_code": Quantity(value=(8.0 / 3.0) * bolt_diameter.value, unit=bolt_diameter.unit),
        "center_to_center_preferred": Quantity(value=3.0 * bolt_diameter.value, unit=bolt_diameter.unit),
        "clear_distance_min": Quantity(value=bolt_diameter.value, unit=bolt_diameter.unit),
    }


def compute_minimum_bolt_spacing_j33(
    *,
    bolt_diameter: Quantity,
    unit_system: UnitSystem,
) -> Quantity:
    """Compute minimum bolt spacing for standard bolted joints.

    Equation:
    ``Smin = 3 * db``

    Reference:
    - AISC 360-22 Section J3.3
    """

    return compute_spacing_requirements_j33(
        bolt_diameter=bolt_diameter,
        unit_system=unit_system,
    )["center_to_center_preferred"]


def compute_max_spacing_and_edge_distance_limits_j36(
    *,
    thinner_part_thickness: Quantity,
    unit_system: UnitSystem,
    is_unpainted_weathering_exposed: bool = False,
) -> dict[str, Quantity]:
    """Compute J3.6 maximum spacing and edge-distance limits.

    - Max longitudinal spacing:
      - Regular: min(24*t, 12 in / 300 mm)
      - Corrosive weathering unpainted: min(14*t, 7 in / 180 mm)
    - Max edge distance from hole center to nearest edge:
      - Regular: min(12*t, 6 in / 150 mm)
      - Corrosive weathering unpainted: min(8*t, 5 in / 125 mm)
    """

    validate_quantity_unit(thinner_part_thickness, "length", unit_system, "geometry.thinner_part_thickness")

    if unit_system == UnitSystem.US:
        spacing_abs_regular = 12.0
        spacing_abs_corrosive = 7.0
        edge_abs_regular = 6.0
        edge_abs_corrosive = 5.0
        unit = "in"
    else:
        spacing_abs_regular = 300.0
        spacing_abs_corrosive = 180.0
        edge_abs_regular = 150.0
        edge_abs_corrosive = 125.0
        unit = "mm"

    t = thinner_part_thickness.value
    spacing_regular = min(24.0 * t, spacing_abs_regular)
    spacing_corrosive = min(14.0 * t, spacing_abs_corrosive)
    edge_regular = min(12.0 * t, edge_abs_regular)
    edge_corrosive = min(8.0 * t, edge_abs_corrosive)

    active_spacing = spacing_corrosive if is_unpainted_weathering_exposed else spacing_regular
    active_edge = edge_corrosive if is_unpainted_weathering_exposed else edge_regular

    return {
        "max_spacing_regular": Quantity(value=spacing_regular, unit=unit),
        "max_spacing_corrosive": Quantity(value=spacing_corrosive, unit=unit),
        "max_edge_distance_regular": Quantity(value=edge_regular, unit=unit),
        "max_edge_distance_corrosive": Quantity(value=edge_corrosive, unit=unit),
        "max_spacing_active": Quantity(value=active_spacing, unit=unit),
        "max_edge_distance_active": Quantity(value=active_edge, unit=unit),
    }


def compute_maximum_bolt_spacing_j36(
    *,
    thinner_part_thickness: Quantity,
    unit_system: UnitSystem,
    is_unpainted_weathering_exposed: bool = False,
) -> tuple[Quantity, dict[str, str | bool]]:
    """Compute only the maximum longitudinal bolt spacing limit (AISC 360-22 J3.6).

    This specialized DRY function targets the spacing clause shown in J3.6:
    - Regular condition: ``Smax = min(24*t, 12 in / 300 mm)``
    - Unpainted weathering exposed to atmospheric corrosion:
      ``Smax = min(14*t, 7 in / 180 mm)``

    It reuses :func:`compute_max_spacing_and_edge_distance_limits_j36` to avoid
    duplicating formulas and branching logic.
    """

    limits = compute_max_spacing_and_edge_distance_limits_j36(
        thinner_part_thickness=thinner_part_thickness,
        unit_system=unit_system,
        is_unpainted_weathering_exposed=is_unpainted_weathering_exposed,
    )
    spacing_active = limits["max_spacing_active"]
    if not isinstance(spacing_active, Quantity):
        raise ValueError("Internal error: expected Quantity for max_spacing_active.")

    if unit_system == UnitSystem.US:
        regular_formula = "Smax = min(24*t, 12 in)"
        corrosive_formula = "Smax = min(14*t, 7 in)"
    else:
        regular_formula = "Smax = min(24*t, 300 mm)"
        corrosive_formula = "Smax = min(14*t, 180 mm)"

    return spacing_active, {
        "reference": "AISC 360-22 J3.6",
        "is_unpainted_weathering_exposed": is_unpainted_weathering_exposed,
        "active_formula": corrosive_formula if is_unpainted_weathering_exposed else regular_formula,
    }


def compute_minimum_edge_distance_standard_hole_j34(
    *,
    bolt_diameter: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float | str]]:
    """Compute minimum edge distance (Le_min) for standard holes.

    Table lookup in US base units (in), then converted to the requested unit
    system. For diameters over 1-1/4 in, this implementation preserves the
    legacy project behavior used across current rules.

    Reference:
    - AISC 360-22 Table J3.4
    """

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


def compute_bolt_tension_rupture_capacity_per_bolt(
    *,
    bolt_diameter: Quantity,
    bolt_fnt: Quantity,
    phi: float = AISCConstants.PHI_BOLT_RUPTURE_DEFAULT,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute tensile rupture capacity for one bolt.

    Equation:
    ``Ab = pi*db^2/4``
    ``Rnt_b = Ab * Fnt``
    ``phiRnt_b = phi * Rnt_b``

    Reference:
    - AISC 360-22 Section J3.7
    """

    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")
    validate_quantity_unit(bolt_fnt, "stress", unit_system, "materials.bolt_fnt")

    # Source: AISC 360-22 Section J3.7 (bolt tension rupture capacity).
    bolt_area = math.pi * (bolt_diameter.value**2) / 4.0
    rnt_b_base = bolt_area * bolt_fnt.value  # US: kip, SI: N
    if unit_system == UnitSystem.US:
        rnt_b = Quantity(value=rnt_b_base, unit="kip")
    else:
        rnt_b = Quantity(value=rnt_b_base / 1000.0, unit="kN")
    phi_rnt_b = Quantity(value=phi * rnt_b.value, unit=rnt_b.unit)

    return {
        "equation": "Ab = pi*db^2/4; Rnt_b = Ab*Fnt; phiRnt_b = phi*Rnt_b",
        "reference": "AISC 360-22 Section J3.7",
        "bolt_area": Quantity(value=bolt_area, unit=f"{bolt_diameter.unit}2"),
        "rnt_b": rnt_b,
        "phi_rnt_b": phi_rnt_b,
        "rnt_b_base_force": rnt_b_base,
        # Backward-compatible aliases.
        "pn": rnt_b,
        "phi_pn": phi_rnt_b,
        "pn_base_force": rnt_b_base,
        "phi": phi,
    }


def compute_bolt_shear_rupture_capacity_per_bolt(
    *,
    bolt_diameter: Quantity,
    bolt_fnv: Quantity,
    phi: float = AISCConstants.PHI_BOLT_RUPTURE_DEFAULT,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute shear rupture capacity for one bolt.

    Equation:
    ``Ab = pi*db^2/4``
    ``Rnv_b = Ab * Fnv``
    ``phiRnv_b = phi * Rnv_b``

    Reference:
    - AISC 360-22 Section J3.7
    """

    validate_quantity_unit(bolt_diameter, "length", unit_system, "geometry.bolt_diameter")
    validate_quantity_unit(bolt_fnv, "stress", unit_system, "materials.bolt_fnv")

    # Source: AISC 360-22 Section J3.7 (bolt shear rupture capacity).
    bolt_area = math.pi * (bolt_diameter.value**2) / 4.0
    rnv_b_base = bolt_area * bolt_fnv.value  # US: kip, SI: N
    if unit_system == UnitSystem.US:
        rnv_b = Quantity(value=rnv_b_base, unit="kip")
    else:
        rnv_b = Quantity(value=rnv_b_base / 1000.0, unit="kN")
    phi_rnv_b = Quantity(value=phi * rnv_b.value, unit=rnv_b.unit)

    return {
        "equation": "Ab = pi*db^2/4; Rnv_b = Ab*Fnv; phiRnv_b = phi*Rnv_b",
        "reference": "AISC 360-22 Section J3.7",
        "bolt_area": Quantity(value=bolt_area, unit=f"{bolt_diameter.unit}2"),
        "rnv_b": rnv_b,
        "phi_rnv_b": phi_rnv_b,
        "rnv_b_base_force": rnv_b_base,
        # Backward-compatible aliases.
        "pn": rnv_b,
        "phi_pn": phi_rnv_b,
        "pn_base_force": rnv_b_base,
        "phi": phi,
    }


def compute_bolt_hole_tearout_strength_j36(
    *,
    material_fu: Quantity,
    clear_distance_lc: Quantity,
    connected_thickness_t: Quantity,
    n_critical_bolts: int,
    phi_n: float,
    unit_system: UnitSystem,
    deformation_at_service_is_design_consideration: bool,
) -> tuple[Quantity, dict[str, Quantity | float | str | bool | int]]:
    """Compute bolt-hole tearout strength per AISC 360-22 J3.

    Per-bolt nominal:
    - J3-6c: ``Rn1_ind = 1.2 * lc * t * Fu`` when service-load deformation is a design consideration.
    - J3-6d: ``Rn1_ind = 1.5 * lc * t * Fu`` otherwise.

    Group design strength:
    ``phi*Rn1 = phi_n * n_critical_bolts * Rn1_ind``
    """

    validate_quantity_unit(material_fu, "stress", unit_system, "material_fu")
    validate_quantity_unit(clear_distance_lc, "length", unit_system, "clear_distance_lc")
    validate_quantity_unit(connected_thickness_t, "length", unit_system, "connected_thickness_t")

    if clear_distance_lc.unit != connected_thickness_t.unit:
        raise ValueError("clear_distance_lc and connected_thickness_t must use the same length unit.")
    if n_critical_bolts <= 0:
        raise ValueError("n_critical_bolts must be >= 1.")

    coefficient = 1.2 if deformation_at_service_is_design_consideration else 1.5
    reference = (
        "AISC 360-22 J3-6c"
        if deformation_at_service_is_design_consideration
        else "AISC 360-22 J3-6d"
    )

    rn1_ind_base = coefficient * clear_distance_lc.value * connected_thickness_t.value * material_fu.value
    rn1_total_base = float(n_critical_bolts) * rn1_ind_base
    phi_rn1_total_base = phi_n * rn1_total_base

    if unit_system == UnitSystem.US:
        force_unit = "kip"
        rn1_ind = Quantity(value=rn1_ind_base, unit=force_unit)
        rn1_total = Quantity(value=rn1_total_base, unit=force_unit)
        phi_rn1_total = Quantity(value=phi_rn1_total_base, unit=force_unit)
    else:
        # SI: MPa * mm^2 = N
        force_unit = "kN"
        rn1_ind = Quantity(value=rn1_ind_base / 1000.0, unit=force_unit)
        rn1_total = Quantity(value=rn1_total_base / 1000.0, unit=force_unit)
        phi_rn1_total = Quantity(value=phi_rn1_total_base / 1000.0, unit=force_unit)

    return phi_rn1_total, {
        "coefficient": coefficient,
        "reference": reference,
        "deformation_at_service_is_design_consideration": deformation_at_service_is_design_consideration,
        "n_critical_bolts": n_critical_bolts,
        "rn1_ind": rn1_ind,
        "rn1_total": rn1_total,
        "phi_n": phi_n,
        "equation_individual": "Rn1_ind = C*lc*t*Fu",
        "equation_group_design": "phi*Rn1 = phi_n*n_critical_bolts*Rn1_ind",
    }


def compute_bolt_hole_bearing_strength_j36(
    *,
    material_fu: Quantity,
    bolt_diameter_d: Quantity,
    connected_thickness_t: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
    deformation_at_service_is_design_consideration: bool,
) -> tuple[Quantity, dict[str, Quantity | float | str | bool]]:
    """Compute per-bolt hole-bearing strength per AISC 360-22 J3.

    Per-bolt nominal:
    - J3-6a: ``Rn2 = 2.4*d*t*Fu`` when service-load deformation is a design consideration.
    - J3-6b: ``Rn2 = 3.0*d*t*Fu`` otherwise.

    Per-bolt design:
    ``phi*Rn2 = phi_n*Rn2``
    """

    validate_quantity_unit(material_fu, "stress", unit_system, "material_fu")
    validate_quantity_unit(bolt_diameter_d, "length", unit_system, "bolt_diameter_d")
    validate_quantity_unit(connected_thickness_t, "length", unit_system, "connected_thickness_t")
    if bolt_diameter_d.unit != connected_thickness_t.unit:
        raise ValueError("bolt_diameter_d and connected_thickness_t must use the same length unit.")

    coefficient = 2.4 if deformation_at_service_is_design_consideration else 3.0
    reference = (
        "AISC 360-22 J3-6a"
        if deformation_at_service_is_design_consideration
        else "AISC 360-22 J3-6b"
    )

    rn2_base = coefficient * bolt_diameter_d.value * connected_thickness_t.value * material_fu.value
    phi_rn2_base = phi_n * rn2_base
    if unit_system == UnitSystem.US:
        force_unit = "kip"
        rn2 = Quantity(value=rn2_base, unit=force_unit)
        phi_rn2 = Quantity(value=phi_rn2_base, unit=force_unit)
    else:
        # SI: MPa * mm^2 = N
        force_unit = "kN"
        rn2 = Quantity(value=rn2_base / 1000.0, unit=force_unit)
        phi_rn2 = Quantity(value=phi_rn2_base / 1000.0, unit=force_unit)

    return phi_rn2, {
        "coefficient": coefficient,
        "reference": reference,
        "deformation_at_service_is_design_consideration": deformation_at_service_is_design_consideration,
        "rn2": rn2,
        "phi_n": phi_n,
        "equation_individual": "Rn2 = C*d*t*Fu",
        "equation_design": "phi*Rn2 = phi_n*Rn2",
    }
