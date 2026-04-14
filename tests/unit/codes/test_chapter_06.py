from __future__ import annotations

from steel_connections.codes.aisc358.chapter_06 import (
    compute_beam_flange_force_from_mf,
    compute_bolt_shear_rupture_capacity,
    compute_end_plate_shear_yielding_capacity,
    compute_flange_slenderness_limit,
    compute_flange_slenderness_ratio,
    compute_minimum_bolt_spacing,
    compute_minimum_edge_distance_standard_hole,
    compute_minimum_stiffener_length,
    compute_web_slenderness_limit,
    compute_web_slenderness_ratio,
)
from steel_connections.models.units import Quantity, UnitSystem


def test_compute_beam_flange_force_from_mf_us() -> None:
    force, intermediates = compute_beam_flange_force_from_mf(
        mf=Quantity(value=5200.0, unit="kip-in"),
        beam_depth=Quantity(value=24.0, unit="in"),
        beam_flange_thickness=Quantity(value=0.75, unit="in"),
        unit_system=UnitSystem.US,
    )
    assert force.unit == "kip"
    assert round(force.value, 3) == 223.656
    assert round(intermediates["lever_arm"], 3) == 23.25


def test_compute_end_plate_shear_yielding_capacity_us() -> None:
    capacity, _ = compute_end_plate_shear_yielding_capacity(
        end_plate_fy=Quantity(value=50.0, unit="ksi"),
        end_plate_width=Quantity(value=9.0, unit="in"),
        end_plate_thickness=Quantity(value=1.0, unit="in"),
        beam_flange_width=Quantity(value=8.0, unit="in"),
        phi_d=0.9,
        unit_system=UnitSystem.US,
    )
    assert capacity.unit == "kip"
    assert round(capacity.value, 3) == 243.0


def test_compute_bolt_shear_rupture_capacity_us() -> None:
    capacity, intermediates = compute_bolt_shear_rupture_capacity(
        bolt_fnv=Quantity(value=54.0, unit="ksi"),
        bolt_diameter=Quantity(value=1.0, unit="in"),
        n_bolts_compression=4,
        phi_n=0.75,
        unit_system=UnitSystem.US,
    )
    assert capacity.unit == "kip"
    assert round(capacity.value, 3) == 127.235
    assert intermediates["n_bolts_compression"] == 4


def test_compute_minimum_stiffener_length() -> None:
    required = compute_minimum_stiffener_length(
        Quantity(value=4.0, unit="in"),
        UnitSystem.US,
    )
    assert required.unit == "in"
    assert round(required.value, 3) == 6.928


def test_compute_compactness_ratios_and_limits() -> None:
    flange_ratio = compute_flange_slenderness_ratio(
        flange_width=Quantity(value=228.0, unit="mm"),
        flange_thickness=Quantity(value=17.3, unit="mm"),
        unit_system=UnitSystem.SI,
    )
    web_ratio, web_inter = compute_web_slenderness_ratio(
        section_depth=Quantity(value=607.0, unit="mm"),
        k_design=Quantity(value=30.0, unit="mm"),
        web_thickness=Quantity(value=11.2, unit="mm"),
        unit_system=UnitSystem.SI,
    )
    flange_limit = compute_flange_slenderness_limit(
        elastic_modulus=Quantity(value=200000.0, unit="MPa"),
        fy=Quantity(value=345.0, unit="MPa"),
        ry=1.1,
        member_ductility_demand="high",
        unit_system=UnitSystem.SI,
    )
    web_limit = compute_web_slenderness_limit(
        elastic_modulus=Quantity(value=200000.0, unit="MPa"),
        fy=Quantity(value=345.0, unit="MPa"),
        ry=1.1,
        ca=0.0,
        member_ductility_demand="high",
        unit_system=UnitSystem.SI,
    )

    assert round(flange_ratio, 2) == 6.59
    assert round(web_ratio, 2) == 48.84
    assert round(web_inter["clear_web_depth"], 1) == 547.0
    assert round(flange_limit, 2) == 6.89
    assert round(web_limit, 2) == 57.39


def test_compute_minimum_bolt_spacing_si() -> None:
    spacing = compute_minimum_bolt_spacing(
        bolt_diameter=Quantity(value=28.575, unit="mm"),
        unit_system=UnitSystem.SI,
    )
    assert spacing.unit == "mm"
    assert round(spacing.value, 3) == 85.725


def test_compute_minimum_edge_distance_j34_si() -> None:
    edge, inter = compute_minimum_edge_distance_standard_hole(
        bolt_diameter=Quantity(value=28.575, unit="mm"),
        unit_system=UnitSystem.SI,
    )
    assert edge.unit == "mm"
    assert round(edge.value, 1) == 38.1
    assert inter["table_row"] == "db=1.125 in"


def test_compute_minimum_edge_distance_j34_unsupported_diameter_raises() -> None:
    try:
        compute_minimum_edge_distance_standard_hole(
            bolt_diameter=Quantity(value=20.0, unit="mm"),
            unit_system=UnitSystem.SI,
        )
    except ValueError as exc:
        assert "Table J3.4" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported bolt diameter in Table J3.4 lookup.")
