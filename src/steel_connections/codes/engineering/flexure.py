from __future__ import annotations

from typing import Any

from steel_connections.codes.engineering.constants import AISCConstants
from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


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

    validate_quantity_unit(t_cf, "length", unit_system, "t_cf")
    validate_quantity_unit(f_yc, "stress", unit_system, "f_yc")
    validate_quantity_unit(y_parameter, "length", unit_system, "y_parameter")
    mn_base = (t_cf.value**2) * f_yc.value * y_parameter.value / AISCConstants.COLUMN_FLANGE_LOCAL_BENDING_DIVISOR
    phi_mn_base = phi * mn_base
    if unit_system == UnitSystem.US:
        mn = Quantity(value=mn_base, unit="kip-in")
        phi_mn = Quantity(value=phi_mn_base, unit="kip-in")
    else:
        mn = Quantity(value=mn_base / 1000.0, unit="kN-mm")
        phi_mn = Quantity(value=phi_mn_base / 1000.0, unit="kN-mm")
    return {
        "equation": "phiM_ncf = phi * (t_cf^2 * f_yc * Y) / 1.11",
        "reference": "AISC 358-22 Section 6.7.2",
        "mn": mn,
        "phi_mn": phi_mn,
        "mn_base_moment": mn_base,
        "phi_mn_base_moment": phi_mn_base,
        "phi": phi,
    }


def compute_dcr(*, demand: Quantity, capacity: Quantity) -> dict[str, Any]:
    """Compute DCR = demand/capacity."""

    if demand.unit != capacity.unit:
        raise ValueError("Demand and capacity must have matching units for DCR.")
    if capacity.value <= 0.0:
        raise ValueError("Capacity must be positive to compute DCR.")
    dcr = demand.value / capacity.value
    return {"dcr": dcr, "status": "PASS" if dcr <= 1.0 else "FAIL"}

