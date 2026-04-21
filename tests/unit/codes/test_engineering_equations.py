from __future__ import annotations

import math

from steel_connections.codes.engineering.common.bolts import (
    compute_bolt_shear_rupture_capacity_per_bolt,
    compute_bolt_tension_rupture_capacity_per_bolt,
)
from steel_connections.codes.engineering.customized.bseep import compute_bseep_step6_1_bolt_tension_demand
from steel_connections.codes.engineering.customized.moment_prequalified import (
    compute_moment_prequalified_step6_1_bolt_tension_demand,
    compute_moment_prequalified_step6_2_bolt_shear_demand,
)
from steel_connections.codes.engineering.flexure import (
    compute_column_flange_local_bending_strength,
    compute_dcr,
)
from steel_connections.codes.engineering.geometry import compute_protected_zone_length
from steel_connections.codes.engineering.shear import compute_beam_web_shear_yielding_strength
from steel_connections.codes.engineering.weld import (
    WeldFillet,
    compute_effective_web_weld_length,
)
from steel_connections.models.units import Quantity, UnitSystem


def test_compute_effective_web_weld_length_us() -> None:
    result = compute_effective_web_weld_length(
        pfi=Quantity(value=2.0, unit="in"),
        pb=Quantity(value=3.0, unit="in"),
        unit_system=UnitSystem.US,
    )
    expected_extra = 150.0 / 25.4
    assert math.isclose(result["hwef"].value, 2.0 + 3.0 + expected_extra, rel_tol=1e-9)
    assert result["hwef"].unit == "in"


def test_weld_fillet_design_strength_returns_structured_values() -> None:
    weld = WeldFillet(
        fexx=Quantity(value=70.0, unit="ksi"),
        weld_size=Quantity(value=0.5, unit="in"),
        weld_length=Quantity(value=10.0, unit="in"),
        weld_lines=2,
        unit_system=UnitSystem.US,
        phi=0.9,
    )
    result = weld.design_strength()
    rn_expected = 0.6 * 70.0 * 0.707 * 10.0 * 0.5 * 2
    assert math.isclose(result["rn"].value, rn_expected, rel_tol=1e-9)
    assert math.isclose(result["phi_rn"].value, 0.9 * rn_expected, rel_tol=1e-9)
    assert result["reference"] == "AISC 360-22 J2.4"


def test_compute_beam_web_shear_yielding_strength() -> None:
    result = compute_beam_web_shear_yielding_strength(
        fy=Quantity(value=50.0, unit="ksi"),
        tw=Quantity(value=0.5, unit="in"),
        d=Quantity(value=24.0, unit="in"),
        kdes=Quantity(value=1.0, unit="in"),
        elastic_modulus=Quantity(value=29000.0, unit="ksi"),
        unit_system=UnitSystem.US,
        phi=1.0,
    )
    assert result["cv1"] <= 1.0
    assert result["phi_vn"].value > 0.0
    assert result["phi_vn"].unit == "kip"


def test_compute_column_flange_local_bending_strength_and_dcr() -> None:
    strength = compute_column_flange_local_bending_strength(
        t_cf=Quantity(value=1.0, unit="in"),
        f_yc=Quantity(value=50.0, unit="ksi"),
        y_parameter=Quantity(value=10.0, unit="in"),
        phi=1.0,
        unit_system=UnitSystem.US,
    )
    assert strength["phi_mn"].unit == "kip-in"
    assert strength["phi_mn"].value > 0.0

    dcr = compute_dcr(
        demand=Quantity(value=100.0, unit="kip-in"),
        capacity=Quantity(value=200.0, unit="kip-in"),
    )
    assert dcr["status"] == "PASS"
    assert math.isclose(dcr["dcr"], 0.5, rel_tol=1e-9)


def test_compute_protected_zone_length_uses_single_reusable_expression() -> None:
    result = compute_protected_zone_length(
        lst=Quantity(value=8.0, unit="in"),
        d=Quantity(value=24.0, unit="in"),
        bf=Quantity(value=8.0, unit="in"),
        unit_system=UnitSystem.US,
    )
    assert math.isclose(result["candidate_a"].value, 8.0 + 0.5 * 24.0, rel_tol=1e-9)
    assert math.isclose(result["candidate_b"].value, 3.0 * 8.0, rel_tol=1e-9)
    assert math.isclose(result["lpz"].value, 20.0, rel_tol=1e-9)


def test_compute_bolt_tension_rupture_capacity_per_bolt() -> None:
    result = compute_bolt_tension_rupture_capacity_per_bolt(
        bolt_diameter=Quantity(value=1.0, unit="in"),
        bolt_fnt=Quantity(value=90.0, unit="ksi"),
        unit_system=UnitSystem.US,
    )
    expected_area = math.pi / 4.0
    expected_pn = expected_area * 90.0
    assert math.isclose(result["bolt_area"].value, expected_area, rel_tol=1e-9)
    assert math.isclose(result["pn"].value, expected_pn, rel_tol=1e-9)
    assert math.isclose(result["phi_pn"].value, 0.9 * expected_pn, rel_tol=1e-9)


def test_compute_bseep_step6_1_bolt_tension_demand_8es() -> None:
    result = compute_bseep_step6_1_bolt_tension_demand(
        mf=Quantity(value=6000.0, unit="kip-in"),
        h1=Quantity(value=8.0, unit="in"),
        h2=Quantity(value=10.0, unit="in"),
        h3=Quantity(value=12.0, unit="in"),
        h4=Quantity(value=14.0, unit="in"),
        connection_type="bseep_8es",
        unit_system=UnitSystem.US,
    )
    expected = 6000.0 / (2.0 * (8.0 + 10.0 + 12.0 + 14.0))
    assert math.isclose(result["rut_b"].value, expected, rel_tol=1e-9)
    assert result["rut_b"].unit == "kip"


def test_compute_bolt_shear_rupture_capacity_per_bolt() -> None:
    result = compute_bolt_shear_rupture_capacity_per_bolt(
        bolt_diameter=Quantity(value=1.0, unit="in"),
        bolt_fnv=Quantity(value=54.0, unit="ksi"),
        unit_system=UnitSystem.US,
    )
    expected_area = math.pi / 4.0
    expected_rnv = expected_area * 54.0
    assert math.isclose(result["bolt_area"].value, expected_area, rel_tol=1e-9)
    assert math.isclose(result["rnv_b"].value, expected_rnv, rel_tol=1e-9)
    assert math.isclose(result["phi_rnv_b"].value, 0.9 * expected_rnv, rel_tol=1e-9)


def test_compute_moment_prequalified_step6_2_bolt_shear_demand_8es() -> None:
    result = compute_moment_prequalified_step6_2_bolt_shear_demand(
        vhmax=Quantity(value=80.0, unit="kip"),
        connection_type="bseep_8es",
        unit_system=UnitSystem.US,
    )
    assert result["nb"] == 8
    assert math.isclose(result["ruv2_b"].value, 10.0, rel_tol=1e-9)
    assert result["ruv2_b"].unit == "kip"


def test_compute_moment_prequalified_step6_1_bolt_tension_demand_4e() -> None:
    result = compute_moment_prequalified_step6_1_bolt_tension_demand(
        mf=Quantity(value=4000.0, unit="kip-in"),
        h1=Quantity(value=8.0, unit="in"),
        h2=Quantity(value=12.0, unit="in"),
        connection_type="bueep_4e",
        unit_system=UnitSystem.US,
    )
    assert math.isclose(result["rut_b"].value, 100.0, rel_tol=1e-9)
    assert result["rut_b"].unit == "kip"
