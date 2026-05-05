from __future__ import annotations

import math

from steel_connections.codes.engineering.common.bolts import (
    compute_bolt_hole_tearout_strength_j36,
    compute_bolt_hole_dimensions_j33,
    compute_bolt_shear_rupture_capacity_per_bolt,
    compute_bolt_tension_rupture_capacity_per_bolt,
    compute_maximum_bolt_spacing_j36,
    compute_max_spacing_and_edge_distance_limits_j36,
    compute_minimum_bolt_spacing_j33,
    compute_minimum_edge_distance_standard_hole_j34,
    compute_spacing_requirements_j33,
    compute_standard_hole_diameter_j33,
)
from steel_connections.codes.engineering.common.prequalified_ep import (
    compute_limites_precalificacion_conexion_tipo_ep,
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


def test_compute_minimum_bolt_spacing_j33_si() -> None:
    spacing = compute_minimum_bolt_spacing_j33(
        bolt_diameter=Quantity(value=28.575, unit="mm"),
        unit_system=UnitSystem.SI,
    )
    assert spacing.unit == "mm"
    assert math.isclose(spacing.value, 85.725, rel_tol=1e-9)


def test_compute_minimum_edge_distance_standard_hole_j34_si() -> None:
    edge, meta = compute_minimum_edge_distance_standard_hole_j34(
        bolt_diameter=Quantity(value=28.575, unit="mm"),
        unit_system=UnitSystem.SI,
    )
    assert edge.unit == "mm"
    assert math.isclose(edge.value, 38.1, rel_tol=1e-9)
    assert meta["table_row"] == "db=1.125 in"


def test_compute_bolt_hole_dimensions_j33_standard_and_slots() -> None:
    result = compute_bolt_hole_dimensions_j33(
        bolt_diameter=Quantity(value=0.75, unit="in"),
        unit_system=UnitSystem.US,
    )
    standard = result["standard_diameter"]
    oversize = result["oversize_diameter"]
    short_w = result["short_slot_width"]
    short_l = result["short_slot_length"]
    long_w = result["long_slot_width"]
    long_l = result["long_slot_length"]
    assert isinstance(standard, Quantity) and math.isclose(standard.value, 13.0 / 16.0, rel_tol=1e-9)
    assert isinstance(oversize, Quantity) and math.isclose(oversize.value, 15.0 / 16.0, rel_tol=1e-9)
    assert isinstance(short_w, Quantity) and math.isclose(short_w.value, 13.0 / 16.0, rel_tol=1e-9)
    assert isinstance(short_l, Quantity) and math.isclose(short_l.value, 1.0, rel_tol=1e-9)
    assert isinstance(long_w, Quantity) and math.isclose(long_w.value, 13.0 / 16.0, rel_tol=1e-9)
    assert isinstance(long_l, Quantity) and math.isclose(long_l.value, 15.0 / 8.0, rel_tol=1e-9)


def test_compute_standard_hole_diameter_j33_formula_branch() -> None:
    hole, meta = compute_standard_hole_diameter_j33(
        bolt_diameter=Quantity(value=1.25, unit="in"),
        unit_system=UnitSystem.US,
    )
    assert math.isclose(hole.value, 1.375, rel_tol=1e-9)
    assert math.isclose(float(meta["hole_add_in"]), 0.125, rel_tol=1e-9)


def test_compute_spacing_requirements_j33() -> None:
    req = compute_spacing_requirements_j33(
        bolt_diameter=Quantity(value=20.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )
    assert math.isclose(req["center_to_center_min_code"].value, (8.0 / 3.0) * 20.0, rel_tol=1e-9)
    assert math.isclose(req["center_to_center_preferred"].value, 60.0, rel_tol=1e-9)
    assert math.isclose(req["clear_distance_min"].value, 20.0, rel_tol=1e-9)


def test_compute_max_spacing_and_edge_distance_limits_j36_regular_and_corrosive() -> None:
    regular = compute_max_spacing_and_edge_distance_limits_j36(
        thinner_part_thickness=Quantity(value=8.0, unit="mm"),
        unit_system=UnitSystem.SI,
        is_unpainted_weathering_exposed=False,
    )
    corrosive = compute_max_spacing_and_edge_distance_limits_j36(
        thinner_part_thickness=Quantity(value=8.0, unit="mm"),
        unit_system=UnitSystem.SI,
        is_unpainted_weathering_exposed=True,
    )
    # Regular: min(24t, 300) = 192; edge: min(12t,150)=96
    assert math.isclose(regular["max_spacing_active"].value, 192.0, rel_tol=1e-9)
    assert math.isclose(regular["max_edge_distance_active"].value, 96.0, rel_tol=1e-9)
    # Corrosive: min(14t,180)=112; edge: min(8t,125)=64
    assert math.isclose(corrosive["max_spacing_active"].value, 112.0, rel_tol=1e-9)
    assert math.isclose(corrosive["max_edge_distance_active"].value, 64.0, rel_tol=1e-9)


def test_compute_maximum_bolt_spacing_j36_specialized_wrapper() -> None:
    smax_regular, meta_regular = compute_maximum_bolt_spacing_j36(
        thinner_part_thickness=Quantity(value=8.0, unit="mm"),
        unit_system=UnitSystem.SI,
        is_unpainted_weathering_exposed=False,
    )
    smax_corrosive, meta_corrosive = compute_maximum_bolt_spacing_j36(
        thinner_part_thickness=Quantity(value=8.0, unit="mm"),
        unit_system=UnitSystem.SI,
        is_unpainted_weathering_exposed=True,
    )
    assert math.isclose(smax_regular.value, 192.0, rel_tol=1e-9)
    assert math.isclose(smax_corrosive.value, 112.0, rel_tol=1e-9)
    assert meta_regular["active_formula"] == "Smax = min(24*t, 300 mm)"
    assert meta_corrosive["active_formula"] == "Smax = min(14*t, 180 mm)"


def test_compute_bolt_hole_tearout_strength_j36_with_service_deformation_design() -> None:
    phi_rn, meta = compute_bolt_hole_tearout_strength_j36(
        material_fu=Quantity(value=450.0, unit="MPa"),
        clear_distance_lc=Quantity(value=58.74, unit="mm"),
        connected_thickness_t=Quantity(value=7.62, unit="mm"),
        n_critical_bolts=6,
        phi_n=0.75,
        unit_system=UnitSystem.SI,
        deformation_at_service_is_design_consideration=True,
    )
    assert phi_rn.unit == "kN"
    assert math.isclose(float(meta["coefficient"]), 1.2, rel_tol=1e-9)
    assert meta["reference"] == "AISC 360-22 J3-6c"


def test_compute_bolt_hole_tearout_strength_j36_without_service_deformation_design() -> None:
    phi_rn, meta = compute_bolt_hole_tearout_strength_j36(
        material_fu=Quantity(value=450.0, unit="MPa"),
        clear_distance_lc=Quantity(value=58.74, unit="mm"),
        connected_thickness_t=Quantity(value=7.62, unit="mm"),
        n_critical_bolts=6,
        phi_n=0.75,
        unit_system=UnitSystem.SI,
        deformation_at_service_is_design_consideration=False,
    )
    assert phi_rn.unit == "kN"
    assert math.isclose(float(meta["coefficient"]), 1.5, rel_tol=1e-9)
    assert meta["reference"] == "AISC 360-22 J3-6d"


def test_compute_limites_precalificacion_conexion_tipo_ep_si() -> None:
    limits = compute_limites_precalificacion_conexion_tipo_ep(
        connection_type="bseep_8es",
        unit_system=UnitSystem.SI,
    )
    bp_min, bp_max = limits["bp"]  # type: ignore[misc]
    assert bp_min.unit == "mm"
    assert bp_max.unit == "mm"
    assert math.isclose(bp_min.value, 228.6, rel_tol=1e-9)
    assert math.isclose(bp_max.value, 381.0, rel_tol=1e-9)


def test_compute_limites_precalificacion_conexion_tipo_ep_invalid_type_raises() -> None:
    try:
        compute_limites_precalificacion_conexion_tipo_ep(
            connection_type="invalid_connection",
            unit_system=UnitSystem.SI,
        )
    except ValueError as exc:
        assert "Unsupported prequalified EP connection type" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported EP connection type.")


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
