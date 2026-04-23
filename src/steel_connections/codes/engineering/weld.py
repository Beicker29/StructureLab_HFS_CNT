from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from steel_connections.codes.engineering.constants import AISCConstants
from steel_connections.codes.engineering.common import compute_dcr_ratio
from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def _force_quantity(value_base: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=value_base, unit="kip")
    return Quantity(value=value_base / 1000.0, unit="kN")


def compute_effective_web_weld_length(
    *,
    pfi: Quantity,
    pb: Quantity,
    unit_system: UnitSystem,
    extra_length_mm: float = 150.0,
) -> dict[str, Any]:
    """Compute effective web weld length ``hwef``.

    Equation:
    ``hwef = pfi + pb + 150 mm`` (or equivalent inches in US units).

    Reference:
    - AISC 358-22 Section 6.7 (project step convention)
    """

    validate_quantity_unit(pfi, "length", unit_system, "pfi")
    validate_quantity_unit(pb, "length", unit_system, "pb")
    extra = extra_length_mm if unit_system == UnitSystem.SI else extra_length_mm / 25.4
    hwef = Quantity(value=pfi.value + pb.value + extra, unit=pfi.unit)
    return {
        "equation": "hwef = pfi + pb + 150 mm",
        "reference": "AISC 358-22 Section 6.7",
        "hwef": hwef,
        "extra_length": Quantity(value=extra, unit=pfi.unit),
    }


def compute_plate_tension_demand_from_yielding(
    *,
    fy: Quantity,
    thickness: Quantity,
    effective_length: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute tension demand from yielding of a plate strip.

    Equation:
    ``Pu = Fy * t * L``

    Reference:
    - AISC 360-22 (general yielding format used in project weld checks)
    """

    validate_quantity_unit(fy, "stress", unit_system, "fy")
    validate_quantity_unit(thickness, "length", unit_system, "thickness")
    validate_quantity_unit(effective_length, "length", unit_system, "effective_length")
    pu_base = fy.value * thickness.value * effective_length.value
    return {
        "equation": "Pu = Fy * t * L",
        "reference": "AISC 360-22 yielding format",
        "pu": _force_quantity(pu_base, unit_system),
        "pu_base_force": pu_base,
    }


def compute_plate_shear_demand_from_yielding(
    *,
    fy: Quantity,
    thickness: Quantity,
    effective_length: Quantity,
    unit_system: UnitSystem,
    shear_factor: float = AISCConstants.WELD_STRENGTH_FACTOR,
) -> dict[str, Any]:
    """Compute shear demand from yielding of a plate strip.

    Equation:
    ``Vu = 0.6 * Fy * t * L``

    Reference:
    - AISC 360-22 shear yielding format
    """

    validate_quantity_unit(fy, "stress", unit_system, "fy")
    validate_quantity_unit(thickness, "length", unit_system, "thickness")
    validate_quantity_unit(effective_length, "length", unit_system, "effective_length")
    vu_base = shear_factor * fy.value * thickness.value * effective_length.value
    return {
        "equation": "Vu = 0.6 * Fy * t * L",
        "reference": "AISC 360-22 shear yielding format",
        "vu": _force_quantity(vu_base, unit_system),
        "vu_base_force": vu_base,
        "shear_factor": shear_factor,
    }


@dataclass(frozen=True)
class WeldFillet:
    """Fillet weld design model.

    Equation:
    ``phiRn = phi * nl * 0.6 * Fexx * 0.707 * L * w``

    Reference:
    - AISC 360-22 J2.4

    Example:
    ``WeldFillet(...).design_strength()``
    """

    fexx: Quantity
    weld_size: Quantity
    weld_length: Quantity
    weld_lines: int
    unit_system: UnitSystem
    phi: float = AISCConstants.PHI_WELD_DEFAULT

    def design_strength(self) -> dict[str, Any]:
        validate_quantity_unit(self.fexx, "stress", self.unit_system, "fexx")
        validate_quantity_unit(self.weld_size, "length", self.unit_system, "weld_size")
        validate_quantity_unit(self.weld_length, "length", self.unit_system, "weld_length")
        if self.weld_lines <= 0:
            raise ValueError("weld_lines must be >= 1.")

        throat = (
            AISCConstants.FILLET_EFFECTIVE_THROAT_FACTOR
            * self.weld_length.value
            * self.weld_size.value
            * self.weld_lines
        )
        rn_base = AISCConstants.WELD_STRENGTH_FACTOR * self.fexx.value * throat
        phi_rn_base = self.phi * rn_base
        return {
            "equation": "phiRn = phi * nl * 0.6 * Fexx * 0.707 * L * w",
            "reference": "AISC 360-22 J2.4",
            "throat_area_effective": Quantity(value=throat, unit=f"{self.weld_size.unit}2"),
            "rn": _force_quantity(rn_base, self.unit_system),
            "phi_rn": _force_quantity(phi_rn_base, self.unit_system),
            "rn_base_force": rn_base,
            "phi_rn_base_force": phi_rn_base,
            "phi": self.phi,
            "weld_lines": self.weld_lines,
        }


def compute_fillet_weld_tension_check_with_kds(
    *,
    demand: Quantity,
    fexx: Quantity,
    weld_size: Quantity,
    weld_length: Quantity,
    weld_lines: int,
    kds: float,
    unit_system: UnitSystem,
    phi: float = AISCConstants.PHI_WELD_DEFAULT,
) -> dict[str, Any]:
    """Compute fillet weld tension capacity and utilization including directional factor ``kds``.

    Equation:
    ``phiRn = phi * kds * nl * 0.6 * Fexx * 0.707 * L * w``

    Reference:
    - AISC 360-22 J2.4 (project implementation with directional factor ``kds``)
    """

    if kds <= 0.0:
        raise ValueError("kds must be > 0.")

    base = WeldFillet(
        fexx=fexx,
        weld_size=weld_size,
        weld_length=weld_length,
        weld_lines=weld_lines,
        unit_system=unit_system,
        phi=phi,
    ).design_strength()
    rn = base["rn"]
    phi_rn = Quantity(value=base["phi_rn"].value * kds, unit=base["phi_rn"].unit)
    dcr_result = compute_dcr_ratio(demand=demand, capacity=phi_rn)
    return {
        "equation": "phiRn = phi * kds * nl * 0.6 * Fexx * 0.707 * L * w",
        "reference": "AISC 360-22 J2.4",
        "rn": rn,
        "phi_rn": phi_rn,
        "rn_base_force": base["rn_base_force"],
        "phi_rn_base_force": base["phi_rn_base_force"] * kds,
        "phi": phi,
        "kds": kds,
        "dcr": dcr_result["dcr"],
        "passes": dcr_result["passes"],
    }
