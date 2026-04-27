from __future__ import annotations

from typing import Any

from steel_connections.codes.engineering.constants import AISCConstants
from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_yield_line_flexural_strength(
    *,
    thickness: Quantity,
    fy: Quantity,
    y_parameter: Quantity,
    phi: float,
    divisor: float,
    unit_system: UnitSystem,
    reference: str,
    equation: str,
) -> dict[str, Any]:
    """Compute flexural strength from a yield-line parameter.

    Equation:
    ``Rn = (t^2 * Fy * Y) / divisor``
    ``phiRn = phi * Rn``

    Reference:
    - Caller-defined in ``reference`` and ``equation`` so the same implementation
      can support end-plate and column-flange yield-line checks without duplicating
      the numerical core.
    """

    validate_quantity_unit(thickness, "length", unit_system, "thickness")
    validate_quantity_unit(fy, "stress", unit_system, "fy")
    validate_quantity_unit(y_parameter, "length", unit_system, "y_parameter")
    if divisor <= 0.0:
        raise ValueError("divisor must be positive.")

    rn_base = (thickness.value**2) * fy.value * y_parameter.value / divisor
    phi_rn_base = phi * rn_base
    if unit_system == UnitSystem.US:
        rn = Quantity(value=rn_base, unit="kip-in")
        phi_rn = Quantity(value=phi_rn_base, unit="kip-in")
    else:
        rn = Quantity(value=rn_base / 1000.0, unit="kN-mm")
        phi_rn = Quantity(value=phi_rn_base / 1000.0, unit="kN-mm")
    return {
        "equation": equation,
        "reference": reference,
        "rn": rn,
        "phi_rn": phi_rn,
        "rn_base_moment": rn_base,
        "phi_rn_base_moment": phi_rn_base,
        "phi": phi,
        "divisor": divisor,
    }


def compute_column_flange_local_bending_strength(
    *,
    t_cf: Quantity,
    f_yc: Quantity,
    y_parameter: Quantity,
    phi: float,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute column flange local bending strength.

    Equation:
    ``phiM_ncf = phi * (t_cf^2 * f_yc * Y) / 1.11``

    Reference:
    - AISC 358-22 Section 6.7.2 (Eq. 6.7-13 form used in project)
    """

    strength = compute_yield_line_flexural_strength(
        thickness=t_cf,
        fy=f_yc,
        y_parameter=y_parameter,
        phi=phi,
        divisor=AISCConstants.COLUMN_FLANGE_LOCAL_BENDING_DIVISOR,
        unit_system=unit_system,
        reference="AISC 358-22 Section 6.7.2",
        equation="phiM_ncf = phi * (t_cf^2 * f_yc * Y) / 1.11",
    )
    return {
        "equation": strength["equation"],
        "reference": strength["reference"],
        "mn": strength["rn"],
        "phi_mn": strength["phi_rn"],
        "mn_base_moment": strength["rn_base_moment"],
        "phi_mn_base_moment": strength["phi_rn_base_moment"],
        "phi": strength["phi"],
    }


def compute_dcr(*, demand: Quantity, capacity: Quantity) -> dict[str, Any]:
    """Compute DCR = demand/capacity."""

    if demand.unit != capacity.unit:
        raise ValueError("Demand and capacity must have matching units for DCR.")
    if capacity.value <= 0.0:
        raise ValueError("Capacity must be positive to compute DCR.")
    dcr = demand.value / capacity.value
    return {"dcr": dcr, "status": "PASS" if dcr <= 1.0 else "FAIL"}
