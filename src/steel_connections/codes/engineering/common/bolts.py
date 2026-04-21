from __future__ import annotations

import math
from typing import Any

from steel_connections.codes.engineering.constants import AISCConstants
from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


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
