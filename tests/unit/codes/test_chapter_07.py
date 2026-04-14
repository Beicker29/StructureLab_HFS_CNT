from __future__ import annotations

from steel_connections.codes.aisc358.chapter_07 import (
    compute_phi_flange_tension_capacity,
    compute_phi_flange_weld_capacity,
)
from steel_connections.models.units import Quantity, UnitSystem


def test_compute_phi_flange_tension_capacity_us() -> None:
    capacity, intermediates = compute_phi_flange_tension_capacity(
        fy=Quantity(value=50.0, unit="ksi"),
        flange_area=Quantity(value=10.0, unit="in2"),
        phi=0.9,
        unit_system=UnitSystem.US,
    )
    assert capacity.unit == "kip"
    assert capacity.value == 450.0
    assert intermediates["nominal_tension_force_kip"] == 500.0


def test_compute_phi_flange_weld_capacity_si() -> None:
    capacity, intermediates = compute_phi_flange_weld_capacity(
        fexx=Quantity(value=490.0, unit="MPa"),
        weld_effective_area=Quantity(value=2000.0, unit="mm2"),
        phi=0.75,
        unit_system=UnitSystem.SI,
    )
    assert capacity.unit == "kN"
    assert round(capacity.value, 3) == 441.0
    assert round(intermediates["nominal_weld_force_n"], 3) == 588000.0
