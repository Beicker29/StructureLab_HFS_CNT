from __future__ import annotations

from steel_connections.catalogs.xlsx_sections import XlsxSectionsCatalog
from steel_connections.data.sections_repository import (
    get_beam_profile_properties,
    get_bolt_section_properties,
    get_column_profile_properties,
    get_shape_profile_properties,
)
from steel_connections.models.units import Quantity, UnitSystem


def _assert_quantity_equal(actual: Quantity | None, expected: Quantity | None) -> None:
    assert actual is not None
    assert expected is not None
    assert actual.unit == expected.unit
    assert actual.value == expected.value


def test_xlsx_shape_section_matches_legacy_repository() -> None:
    catalog = XlsxSectionsCatalog()

    for unit_system in (UnitSystem.SI, UnitSystem.US):
        typed = catalog.get_section(shape="W21X68", unit_system=unit_system)
        legacy = get_shape_profile_properties(shape="W21X68", unit_system=unit_system)

        assert typed.shape == "W21X68"
        _assert_quantity_equal(typed.d, legacy["d"])
        _assert_quantity_equal(typed.bf, legacy["bf"])
        _assert_quantity_equal(typed.tf, legacy["tf"])
        _assert_quantity_equal(typed.tw, legacy["tw"])
        _assert_quantity_equal(typed.kdes, legacy.get("kdes"))
        _assert_quantity_equal(typed.zx, legacy.get("zx"))
        assert typed.source.catalog == "sections"
        assert typed.source.checksum_sha256


def test_xlsx_beam_and_column_wrappers_match_legacy_repository() -> None:
    catalog = XlsxSectionsCatalog()

    beam = catalog.get_beam_section(beam_shape="W21X68", unit_system=UnitSystem.SI)
    legacy_beam = get_beam_profile_properties(beam_shape="W21X68", unit_system=UnitSystem.SI)
    _assert_quantity_equal(beam.d, legacy_beam["d"])
    _assert_quantity_equal(beam.bf, legacy_beam["bf"])
    _assert_quantity_equal(beam.tf, legacy_beam["tf"])
    _assert_quantity_equal(beam.tw, legacy_beam["tw"])

    column = catalog.get_column_section(column_shape="HEB 500", unit_system=UnitSystem.SI)
    legacy_column = get_column_profile_properties(column_shape="HEB 500", unit_system=UnitSystem.SI)
    _assert_quantity_equal(column.d, legacy_column["d"])
    _assert_quantity_equal(column.bf, legacy_column["bf"])
    _assert_quantity_equal(column.tf, legacy_column["tf"])
    _assert_quantity_equal(column.tw, legacy_column["tw"])


def test_xlsx_bolt_section_matches_legacy_repository() -> None:
    catalog = XlsxSectionsCatalog()

    for unit_system in (UnitSystem.SI, UnitSystem.US):
        typed = catalog.get_bolt_section(
            bolt_shape='P1-1/8"X1-3/4"',
            bolt_description="Grupo 150",
            bolt_fabrication_standard="ASTM A490",
            unit_system=unit_system,
        )
        legacy = get_bolt_section_properties(
            bolt_shape='P1-1/8"X1-3/4"',
            bolt_description="Grupo 150",
            bolt_fabrication_standard="ASTM A490",
            unit_system=unit_system,
        )

        assert typed.shape == legacy["shape"]
        assert typed.classification == legacy["classification"]
        assert typed.fabrication_standard == legacy["fabrication_standard"]
        _assert_quantity_equal(typed.diameter_nominal, legacy["diameter_nominal"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.length, legacy["length"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.width_across_flats, legacy["width_across_flats"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.head_diameter, legacy["head_diameter"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.head_height, legacy["head_height"])  # type: ignore[arg-type]
        assert typed.source.sheet == "Perno"
        assert typed.source.checksum_sha256
