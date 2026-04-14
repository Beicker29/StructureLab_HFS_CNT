from __future__ import annotations

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_phi_flange_tension_capacity(
    *,
    fy: Quantity,
    flange_area: Quantity,
    phi: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(fy, "stress", unit_system, "materials.beam_fy")
    validate_quantity_unit(flange_area, "area", unit_system, "geometry.beam_flange_area")

    if unit_system == UnitSystem.US:
        nominal_force = fy.value * flange_area.value  # ksi * in2 = kip
        design_force = phi * nominal_force
        capacity = Quantity(value=design_force, unit="kip")
        intermediates = {
            "nominal_tension_force_kip": nominal_force,
            "phi": phi,
        }
        return capacity, intermediates

    nominal_force_n = fy.value * flange_area.value  # MPa * mm2 = N
    design_force_kn = (phi * nominal_force_n) / 1000.0
    capacity = Quantity(value=design_force_kn, unit="kN")
    intermediates = {
        "nominal_tension_force_n": nominal_force_n,
        "phi": phi,
        "n_to_kn": 0.001,
    }
    return capacity, intermediates


def compute_phi_flange_weld_capacity(
    *,
    fexx: Quantity,
    weld_effective_area: Quantity,
    phi: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, float]]:
    validate_quantity_unit(fexx, "stress", unit_system, "materials.weld_fexx")
    validate_quantity_unit(
        weld_effective_area,
        "area",
        unit_system,
        "geometry.weld_effective_area",
    )

    weld_strength_factor = 0.6
    if unit_system == UnitSystem.US:
        nominal_force = weld_strength_factor * fexx.value * weld_effective_area.value
        design_force = phi * nominal_force
        capacity = Quantity(value=design_force, unit="kip")
        intermediates = {
            "weld_strength_factor": weld_strength_factor,
            "nominal_weld_force_kip": nominal_force,
            "phi": phi,
        }
        return capacity, intermediates

    nominal_force_n = weld_strength_factor * fexx.value * weld_effective_area.value
    design_force_kn = (phi * nominal_force_n) / 1000.0
    capacity = Quantity(value=design_force_kn, unit="kN")
    intermediates = {
        "weld_strength_factor": weld_strength_factor,
        "nominal_weld_force_n": nominal_force_n,
        "phi": phi,
        "n_to_kn": 0.001,
    }
    return capacity, intermediates
