from __future__ import annotations

import math
from typing import Any

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def _elastic_modulus(unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=29000.0, unit="ksi")
    return Quantity(value=200000.0, unit="MPa")


def _force_from_stress_area(*, stress: float, area: float, phi: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=phi * stress * area, unit="kip")
    return Quantity(value=phi * stress * area / 1000.0, unit="kN")


def compute_plate_compression_buckling_strength(
    *,
    material_fy: Quantity,
    plate_width_b1: Quantity,
    plate_thickness_t: Quantity,
    unbraced_length_lp: Quantity,
    plate_count_n: int,
    unit_system: UnitSystem,
    phi: float = 0.9,
    k_factor: float = 0.65,
) -> dict[str, Any]:
    """Compute plate compression buckling strength.

    Legacy equation preserved:
        r = 0.29 * t
        KL/r = K * Lp / r
        Fe = pi^2 * E / (KL/r)^2
        Fcr = Fy                              for KL/r <= 25
        Fcr = 0.658^(Fy/Fe) * Fy              for KL/r <= 4.71*sqrt(E/Fy)
        Fcr = 0.877 * Fe                      otherwise
        phi*Rn = phi * Fcr * b1 * t * n

    Units:
        US: ksi, in -> kip
        SI: MPa, mm -> kN
    """
    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    validate_quantity_unit(plate_width_b1, "length", unit_system, "plate_width_b1")
    validate_quantity_unit(plate_thickness_t, "length", unit_system, "plate_thickness_t")
    validate_quantity_unit(unbraced_length_lp, "length", unit_system, "unbraced_length_lp")
    if plate_width_b1.unit != plate_thickness_t.unit or plate_width_b1.unit != unbraced_length_lp.unit:
        raise ValueError("Plate width, thickness, and unbraced length must share units.")
    if plate_count_n <= 0:
        raise ValueError("plate_count_n must be positive.")
    if phi <= 0.0:
        raise ValueError("phi must be positive.")
    if k_factor <= 0.0:
        raise ValueError("k_factor must be positive.")
    if material_fy.value <= 0.0 or plate_thickness_t.value <= 0.0 or unbraced_length_lp.value <= 0.0:
        raise ValueError("Fy, plate thickness, and unbraced length must be positive.")

    radius = Quantity(value=0.29 * plate_thickness_t.value, unit=plate_thickness_t.unit)
    klr = (k_factor * unbraced_length_lp.value) / radius.value
    elastic_modulus = _elastic_modulus(unit_system)
    fe = Quantity(value=(math.pi**2) * elastic_modulus.value / (klr**2), unit=elastic_modulus.unit)
    slenderness_limit = 4.71 * math.sqrt(elastic_modulus.value / material_fy.value)

    if klr <= 25.0:
        fcr_value = material_fy.value
        critical_stress_equation = "Fcr_pc_col = Fy_pc_col"
    elif klr <= slenderness_limit:
        fcr_value = (0.658 ** (material_fy.value / fe.value)) * material_fy.value
        critical_stress_equation = "Fcr_pc_col = 0.658^(Fy_pc_col/Fe_pc_col)*Fy_pc_col"
    else:
        fcr_value = 0.877 * fe.value
        critical_stress_equation = "Fcr_pc_col = 0.877*Fe_pc_col"

    critical_stress = Quantity(value=fcr_value, unit=elastic_modulus.unit)
    gross_area = plate_width_b1.value * plate_thickness_t.value * float(plate_count_n)
    phi_rn = _force_from_stress_area(stress=fcr_value, area=gross_area, phi=phi, unit_system=unit_system)
    return {
        "radius": radius,
        "klr": klr,
        "elastic_modulus": elastic_modulus,
        "elastic_buckling_stress": fe,
        "slenderness_limit": slenderness_limit,
        "critical_stress": critical_stress,
        "critical_stress_equation": critical_stress_equation,
        "gross_area": Quantity(
            value=gross_area,
            unit="in2" if unit_system == UnitSystem.US else "mm2",
        ),
        "phi_rn": phi_rn,
        "phi": phi,
        "k_factor": k_factor,
        "equation": "phi*Rn = phi * Fcr * b1 * t * n",
        "reference": "Plate compression buckling formula with configurable K factor",
    }
