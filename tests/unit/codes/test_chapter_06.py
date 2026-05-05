from __future__ import annotations

from steel_connections.codes.aisc358.chapter_06 import (
    compute_beam_flange_force_from_mf,
    compute_bolt_shear_rupture_capacity,
    compute_bseep_4es_end_plate_yield_line_parameter_value,
    compute_bseep_8es_end_plate_yield_line_parameter_value,
    compute_bueep_4e_end_plate_yield_line_parameter_value,
    compute_column_beam_clearance_distance,
    compute_column_beam_clearance_threshold,
    compute_detail_stiffener_length_from_height,
    compute_effective_column_flange_stiffener_pitch,
    compute_effective_end_plate_inner_pitch,
    compute_eight_bolt_stiffened_column_flange_yield_line_parameter_value,
    compute_eight_bolt_unstiffened_column_flange_yield_line_parameter_value,
    compute_end_plate_height_from_geometry,
    compute_end_plate_shear_yielding_capacity,
    compute_end_plate_yield_line_h_terms,
    compute_end_plate_yield_line_spacing_limit,
    compute_flange_slenderness_limit,
    compute_four_bolt_stiffened_column_flange_yield_line_parameter_value,
    compute_four_bolt_unstiffened_column_flange_yield_line_parameter_value,
    compute_flange_slenderness_ratio,
    compute_minimum_bolt_spacing,
    compute_minimum_column_end_distance_to_beam_flange,
    compute_minimum_edge_distance_standard_hole,
    compute_minimum_stiffener_bolt_gage,
    compute_minimum_stiffener_length,
    compute_stiffener_height_from_end_plate_geometry,
    compute_stiffener_slenderness_ratio,
    compute_web_slenderness_limit,
    compute_web_slenderness_ratio,
    is_column_flange_stiffener_pitch_within_spacing_limit,
    is_end_plate_edge_distance_within_spacing_limit,
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


def test_compute_detail_stiffener_length_from_height_rounds_si_to_10_mm() -> None:
    detailed = compute_detail_stiffener_length_from_height(
        Quantity(value=205.0, unit="mm"),
        UnitSystem.SI,
    )

    assert detailed.unit == "mm"
    assert detailed.value == 360.0


def test_compute_stiffener_height_from_end_plate_geometry_si() -> None:
    height = compute_stiffener_height_from_end_plate_geometry(
        pfo=Quantity(value=50.0, unit="mm"),
        de=Quantity(value=60.0, unit="mm"),
        pb=Quantity(value=95.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert height.unit == "mm"
    assert height.value == 205.0


def test_compute_end_plate_height_from_geometry_si() -> None:
    height = compute_end_plate_height_from_geometry(
        beam_depth=Quantity(value=607.0, unit="mm"),
        pfo=Quantity(value=50.0, unit="mm"),
        de=Quantity(value=60.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert height.unit == "mm"
    assert height.value == 827.0


def test_compute_stiffener_slenderness_ratio_si() -> None:
    ratio = compute_stiffener_slenderness_ratio(
        stiffener_height=Quantity(value=120.0, unit="mm"),
        stiffener_thickness=Quantity(value=15.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert ratio == 8.0


def test_compute_minimum_stiffener_bolt_gage_si() -> None:
    gage = compute_minimum_stiffener_bolt_gage(
        minimum_edge_distance=Quantity(value=38.1, unit="mm"),
        stiffener_thickness=Quantity(value=15.9, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert gage.unit == "mm"
    assert round(gage.value, 3) == 92.1


def test_compute_minimum_column_end_distance_to_beam_flange_si() -> None:
    minimum = compute_minimum_column_end_distance_to_beam_flange(
        pfo=Quantity(value=50.0, unit="mm"),
        de=Quantity(value=60.0, unit="mm"),
        pb=Quantity(value=95.0, unit="mm"),
        margin=Quantity(value=12.5, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert minimum.unit == "mm"
    assert minimum.value == 217.5


def test_compute_column_beam_clearance_threshold_si() -> None:
    threshold = compute_column_beam_clearance_threshold(
        column_flange_width=Quantity(value=300.0, unit="mm"),
        bolt_gage=Quantity(value=140.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert threshold.unit == "mm"
    assert round(threshold.value, 3) == 102.47


def test_compute_column_beam_clearance_distance_si() -> None:
    clearance = compute_column_beam_clearance_distance(
        column_end_distance_to_beam_flange=Quantity(value=2500.0, unit="mm"),
        pfo=Quantity(value=50.0, unit="mm"),
        pb=Quantity(value=95.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert clearance.unit == "mm"
    assert clearance.value == 2355.0


def test_compute_end_plate_yield_line_h_terms_bseep_8es_si() -> None:
    terms = compute_end_plate_yield_line_h_terms(
        connection_type="bseep_8es",
        beam_depth=Quantity(value=607.0, unit="mm"),
        beam_flange_thickness=Quantity(value=17.3, unit="mm"),
        pfo=Quantity(value=50.0, unit="mm"),
        pfi=Quantity(value=50.0, unit="mm"),
        pb=Quantity(value=95.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert round(terms["h1"].value, 3) == 743.35
    assert round(terms["h2"].value, 3) == 648.35
    assert round(terms["h3"].value, 3) == 531.05
    assert round(terms["h4"].value, 3) == 436.05


def test_compute_end_plate_yield_line_h_terms_four_bolt_si() -> None:
    terms = compute_end_plate_yield_line_h_terms(
        connection_type="bseep_4es",
        beam_depth=Quantity(value=607.0, unit="mm"),
        beam_flange_thickness=Quantity(value=17.3, unit="mm"),
        pfo=Quantity(value=50.0, unit="mm"),
        pfi=Quantity(value=50.0, unit="mm"),
        pb=None,
        unit_system=UnitSystem.SI,
    )

    assert round(terms["h1"].value, 3) == 648.35
    assert round(terms["h2"].value, 3) == 531.05
    assert terms["h3"] is None
    assert terms["h4"] is None


def test_compute_end_plate_yield_line_spacing_limit_si() -> None:
    spacing_limit = compute_end_plate_yield_line_spacing_limit(
        end_plate_width=Quantity(value=280.0, unit="mm"),
        bolt_gage=Quantity(value=140.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert spacing_limit.unit == "mm"
    assert round(spacing_limit.value, 3) == 98.995


def test_compute_effective_end_plate_inner_pitch_si() -> None:
    effective = compute_effective_end_plate_inner_pitch(
        inner_pitch=Quantity(value=120.0, unit="mm"),
        spacing_limit=Quantity(value=98.995, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert effective.unit == "mm"
    assert effective.value == 98.995


def test_is_end_plate_edge_distance_within_spacing_limit_si() -> None:
    assert is_end_plate_edge_distance_within_spacing_limit(
        edge_distance=Quantity(value=60.0, unit="mm"),
        spacing_limit=Quantity(value=98.995, unit="mm"),
        unit_system=UnitSystem.SI,
    )


def test_compute_bueep_4e_end_plate_yield_line_parameter_value_si() -> None:
    value = compute_bueep_4e_end_plate_yield_line_parameter_value(
        bp=Quantity(value=200.0, unit="mm"),
        g=Quantity(value=200.0, unit="mm"),
        pfi_effective=Quantity(value=100.0, unit="mm"),
        pfo=Quantity(value=100.0, unit="mm"),
        h1=Quantity(value=100.0, unit="mm"),
        h2=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert value == 450.0


def test_compute_bseep_4es_end_plate_yield_line_parameter_value_si() -> None:
    value = compute_bseep_4es_end_plate_yield_line_parameter_value(
        bp=Quantity(value=200.0, unit="mm"),
        g=Quantity(value=200.0, unit="mm"),
        pfi_effective=Quantity(value=100.0, unit="mm"),
        pfo=Quantity(value=100.0, unit="mm"),
        de=Quantity(value=100.0, unit="mm"),
        h1=Quantity(value=100.0, unit="mm"),
        h2=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        de_le_spacing_limit=True,
        unit_system=UnitSystem.SI,
    )

    assert value == 750.0


def test_compute_bseep_8es_end_plate_yield_line_parameter_value_si() -> None:
    value = compute_bseep_8es_end_plate_yield_line_parameter_value(
        bp=Quantity(value=200.0, unit="mm"),
        g=Quantity(value=200.0, unit="mm"),
        pfi_effective=Quantity(value=100.0, unit="mm"),
        pfo=Quantity(value=100.0, unit="mm"),
        de=Quantity(value=100.0, unit="mm"),
        pb=Quantity(value=100.0, unit="mm"),
        h1=Quantity(value=100.0, unit="mm"),
        h2=Quantity(value=100.0, unit="mm"),
        h3=Quantity(value=100.0, unit="mm"),
        h4=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        de_le_spacing_limit=True,
        unit_system=UnitSystem.SI,
    )

    assert value == 1150.0


def test_compute_effective_column_flange_stiffener_pitch_si() -> None:
    effective = compute_effective_column_flange_stiffener_pitch(
        stiffener_pitch=Quantity(value=120.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert effective.unit == "mm"
    assert effective.value == 100.0


def test_is_column_flange_stiffener_pitch_within_spacing_limit_si() -> None:
    assert is_column_flange_stiffener_pitch_within_spacing_limit(
        stiffener_pitch=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )


def test_compute_four_bolt_stiffened_column_flange_yield_line_parameter_value_si() -> None:
    value = compute_four_bolt_stiffened_column_flange_yield_line_parameter_value(
        bcf=Quantity(value=200.0, unit="mm"),
        g=Quantity(value=200.0, unit="mm"),
        h1=Quantity(value=100.0, unit="mm"),
        h2=Quantity(value=100.0, unit="mm"),
        pso=Quantity(value=100.0, unit="mm"),
        psi_effective=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert value == 800.0


def test_compute_four_bolt_unstiffened_column_flange_yield_line_parameter_value_si() -> None:
    value = compute_four_bolt_unstiffened_column_flange_yield_line_parameter_value(
        bcf=Quantity(value=200.0, unit="mm"),
        g=Quantity(value=200.0, unit="mm"),
        h1=Quantity(value=100.0, unit="mm"),
        h2=Quantity(value=100.0, unit="mm"),
        c=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert value == 750.0


def test_compute_eight_bolt_stiffened_column_flange_yield_line_parameter_value_si() -> None:
    value = compute_eight_bolt_stiffened_column_flange_yield_line_parameter_value(
        bcf=Quantity(value=200.0, unit="mm"),
        g=Quantity(value=200.0, unit="mm"),
        h1=Quantity(value=100.0, unit="mm"),
        h2=Quantity(value=100.0, unit="mm"),
        h3=Quantity(value=100.0, unit="mm"),
        h4=Quantity(value=100.0, unit="mm"),
        pso=Quantity(value=100.0, unit="mm"),
        psi_effective=Quantity(value=100.0, unit="mm"),
        pb=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert value == 1250.0


def test_compute_eight_bolt_unstiffened_column_flange_yield_line_parameter_value_si() -> None:
    value = compute_eight_bolt_unstiffened_column_flange_yield_line_parameter_value(
        bcf=Quantity(value=200.0, unit="mm"),
        g=Quantity(value=200.0, unit="mm"),
        h1=Quantity(value=100.0, unit="mm"),
        h2=Quantity(value=100.0, unit="mm"),
        h3=Quantity(value=100.0, unit="mm"),
        h4=Quantity(value=100.0, unit="mm"),
        c=Quantity(value=100.0, unit="mm"),
        pb=Quantity(value=100.0, unit="mm"),
        spacing_limit=Quantity(value=100.0, unit="mm"),
        unit_system=UnitSystem.SI,
    )

    assert value == 825.0


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
    assert round(web_limit, 2) == 56.24


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
