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


def compute_fillet_weld_check_with_kds(
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
    """Compute fillet weld capacity and utilization including directional factor ``kds``.

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


def compute_total_weld_4_thickness(
    *,
    backing_thickness: Quantity,
    ductility_demand: str,
    weld_lines: int | None,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute total weld-4 thickness used as ``2w`` in column checks.

    Equation:
    - Low ductility: ``2w = nl * t_w4.1``
    - Moderate/high ductility: ``2w = t_w4.1``

    Reference:
    - Project implementation rule for Chapter 6 end-plate checks.
    """

    validate_quantity_unit(backing_thickness, "length", unit_system, "backing_thickness")
    demand = str(ductility_demand).strip().lower()
    if demand not in {"low", "moderate", "high"}:
        raise ValueError("ductility_demand must be 'low', 'moderate' or 'high'.")

    if demand == "low":
        if weld_lines is None or weld_lines <= 0:
            raise ValueError("weld_lines must be >= 1 when ductility_demand is 'low'.")
        total_value = weld_lines * backing_thickness.value
        equation = "2w = nl_w4 * t_w4.1"
    else:
        total_value = backing_thickness.value
        equation = "2w = t_w4.1"

    total = Quantity(value=total_value, unit=backing_thickness.unit)
    return {
        "equation": equation,
        "reference": "Project rule for weld #4 total thickness",
        "total_thickness": total,
        "ductility_demand": demand,
        "weld_lines": weld_lines,
    }


def compute_fillet_weld_minimum_size_table_j24(
    *,
    thinner_part_thickness: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute minimum fillet weld size from AISC Table J2.4.

    Equation:
    ``w_min = Table J2.4(thinner_part_thickness)``

    Reference:
    - AISC 360-22 Table J2.4
    """

    validate_quantity_unit(thinner_part_thickness, "length", unit_system, "thinner_part_thickness")
    t_mm = thinner_part_thickness.value if unit_system == UnitSystem.SI else thinner_part_thickness.value * 25.4
    if t_mm <= 6.0 + 1e-9:
        w_min_mm = 3.0
    elif t_mm <= 13.0 + 1e-9:
        w_min_mm = 5.0
    elif t_mm <= 19.0 + 1e-9:
        w_min_mm = 6.0
    else:
        w_min_mm = 8.0
    w_min_value = w_min_mm if unit_system == UnitSystem.SI else w_min_mm / 25.4
    return {
        "equation": "w_min = Table J2.4(thinner part thickness)",
        "reference": "AISC 360-22 Table J2.4",
        "w_min": Quantity(value=w_min_value, unit=thinner_part_thickness.unit),
        "thinner_part_thickness_mm": t_mm,
    }


def compute_fillet_weld_maximum_size_j2b(
    *,
    thinner_part_thickness: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute maximum fillet weld size from AISC J2b.

    Equation:
    - if ``t < 6 mm``: ``w_max = t``
    - if ``t >= 6 mm``: ``w_max = t - 2 mm``

    Reference:
    - AISC 360-22 Section J2b
    """

    validate_quantity_unit(thinner_part_thickness, "length", unit_system, "thinner_part_thickness")
    t_mm = thinner_part_thickness.value if unit_system == UnitSystem.SI else thinner_part_thickness.value * 25.4
    if t_mm < 6.0 - 1e-9:
        w_max_mm = t_mm
        branch = "t_lt_6mm"
    else:
        w_max_mm = max(t_mm - 2.0, 0.0)
        branch = "t_ge_6mm"
    w_max_value = w_max_mm if unit_system == UnitSystem.SI else w_max_mm / 25.4
    return {
        "equation": "w_max = t (t<6 mm) else t-2 mm",
        "reference": "AISC 360-22 Section J2b",
        "w_max": Quantity(value=w_max_value, unit=thinner_part_thickness.unit),
        "branch": branch,
        "thinner_part_thickness_mm": t_mm,
    }


def compute_fillet_weld_minimum_length_strength_j2c(
    *,
    weld_size: Quantity,
    weld_length: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute minimum fillet weld length criterion from AISC J2.2(c).

    Equation:
    ``l_min = 4*w``

    Reference:
    - AISC 360-22 Section J2.2(c)
    """

    validate_quantity_unit(weld_size, "length", unit_system, "weld_size")
    validate_quantity_unit(weld_length, "length", unit_system, "weld_length")
    l_min = Quantity(value=4.0 * weld_size.value, unit=weld_size.unit)
    passes = weld_length.value >= l_min.value - 1e-9
    w_effective_cap = Quantity(value=min(weld_size.value, weld_length.value / 4.0), unit=weld_size.unit)
    return {
        "equation": "l_min = 4*w",
        "reference": "AISC 360-22 Section J2.2(c)",
        "l_min": l_min,
        "passes": passes,
        "w_effective_cap_if_short": w_effective_cap,
    }


def compute_end_loaded_fillet_weld_effective_length_j2d(
    *,
    weld_size: Quantity,
    weld_length: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute effective length for end-loaded fillet welds from AISC J2.2(d).

    Equation:
    - if ``l/w <= 100``: ``l_eff = l``
    - if ``100 < l/w <= 300``: ``beta = min(1.0, 1.2 - 0.002*(l/w)); l_eff = beta*l``
    - if ``l/w > 300``: ``l_eff = 180*w``

    Reference:
    - AISC 360-22 Section J2.2(d), Eq. (J2-1)
    """

    validate_quantity_unit(weld_size, "length", unit_system, "weld_size")
    validate_quantity_unit(weld_length, "length", unit_system, "weld_length")
    if weld_size.value <= 0.0:
        raise ValueError("weld_size must be > 0 for J2.2(d) effective length.")
    ratio = weld_length.value / weld_size.value
    if ratio <= 100.0:
        beta = 1.0
        l_eff_value = weld_length.value
        branch = "lw_le_100"
    elif ratio <= 300.0:
        beta = min(1.0, 1.2 - 0.002 * ratio)
        l_eff_value = beta * weld_length.value
        branch = "100_lt_lw_le_300"
    else:
        l_eff_value = 180.0 * weld_size.value
        beta = l_eff_value / weld_length.value if weld_length.value > 0.0 else 0.0
        branch = "lw_gt_300"
    return {
        "equation": "l_eff = l (l/w<=100), l_eff=beta*l (100<l/w<=300), l_eff=180*w (l/w>300)",
        "reference": "AISC 360-22 Section J2.2(d), Eq. (J2-1)",
        "l_over_w": ratio,
        "beta": beta,
        "l_eff": Quantity(value=l_eff_value, unit=weld_length.unit),
        "branch": branch,
    }
