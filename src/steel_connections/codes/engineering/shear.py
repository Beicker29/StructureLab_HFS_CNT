from __future__ import annotations

import math
from typing import Any

from steel_connections.codes.engineering.constants import AISCConstants
from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_beam_web_shear_yielding_strength(
    *,
    fy: Quantity,
    tw: Quantity,
    d: Quantity,
    kdes: Quantity,
    elastic_modulus: Quantity,
    unit_system: UnitSystem,
    phi: float = 1.0,
) -> dict[str, Any]:
    """Compute beam web shear yielding strength with Cv1.

    Equation:
    ``phiVn = phi * 0.6 * Fy * tw * d * Cv1``
    with ``Cv1 = min(1.0, lambda_r/(h/tw))`` and
    ``lambda_r = 1.10*sqrt(kv*E/Fy)``, ``kv=5.34``.

    Reference:
    - AISC 360-22 G2.1 (Eq. G2-3 / G2-4, unstiffened web)
    """

    validate_quantity_unit(fy, "stress", unit_system, "fy")
    validate_quantity_unit(tw, "length", unit_system, "tw")
    validate_quantity_unit(d, "length", unit_system, "d")
    validate_quantity_unit(kdes, "length", unit_system, "kdes")
    validate_quantity_unit(elastic_modulus, "stress", unit_system, "elastic_modulus")

    h_clear = d.value - 2.0 * kdes.value
    if h_clear <= 0.0:
        raise ValueError("Computed h_clear = d - 2*kdes must be positive.")
    h_over_tw = h_clear / tw.value
    kv = AISCConstants.BEAM_WEB_SHEAR_KV_UNSTIFFENED
    lambda_r = AISCConstants.BEAM_WEB_SHEAR_LAMBDA_FACTOR * math.sqrt(kv * elastic_modulus.value / fy.value)
    cv1 = 1.0 if h_over_tw <= lambda_r + 1e-9 else lambda_r / h_over_tw
    vn_base = AISCConstants.WELD_STRENGTH_FACTOR * fy.value * tw.value * d.value * cv1
    phi_vn_base = phi * vn_base
    if unit_system == UnitSystem.US:
        nominal = Quantity(value=vn_base, unit="kip")
        design = Quantity(value=phi_vn_base, unit="kip")
    else:
        nominal = Quantity(value=vn_base / 1000.0, unit="kN")
        design = Quantity(value=phi_vn_base / 1000.0, unit="kN")
    return {
        "equation": "phiVn = phi * 0.6 * Fy * tw * d * Cv1",
        "reference": "AISC 360-22 G2.1 Eq. G2-3/G2-4",
        "h_clear": Quantity(value=h_clear, unit=d.unit),
        "h_over_tw": h_over_tw,
        "kv": kv,
        "lambda_r": lambda_r,
        "cv1": cv1,
        "vn": nominal,
        "phi_vn": design,
        "vn_base_force": vn_base,
        "phi_vn_base_force": phi_vn_base,
        "phi": phi,
    }

