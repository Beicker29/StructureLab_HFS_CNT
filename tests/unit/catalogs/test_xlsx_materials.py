from __future__ import annotations

from steel_connections.catalogs.xlsx_materials import XlsxMaterialsCatalog, weld_material_from_fexx
from steel_connections.data.materials_repository import (
    get_bolt_strength_properties,
    get_hrs_steel_properties,
    get_plate_steel_properties,
)
from steel_connections.models.units import Quantity, UnitSystem


def _assert_quantity_equal(actual: Quantity, expected: Quantity) -> None:
    assert actual.unit == expected.unit
    assert actual.value == expected.value


def test_xlsx_hrs_steel_material_matches_legacy_repository() -> None:
    catalog = XlsxMaterialsCatalog()

    for unit_system in (UnitSystem.SI, UnitSystem.US):
        typed = catalog.get_hrs_steel(steel_type="ASTM A572 Gr 50", unit_system=unit_system)
        legacy = get_hrs_steel_properties(steel_type="ASTM A572 Gr 50", unit_system=unit_system)

        assert typed.steel_type == legacy["steel_type"]
        _assert_quantity_equal(typed.fy, legacy["fy"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.fu, legacy["fu"])  # type: ignore[arg-type]
        assert typed.ry == legacy["ry"]
        assert typed.rt == legacy["rt"]
        assert typed.source.sheet == "HRS"
        assert typed.source.checksum_sha256


def test_xlsx_plate_steel_material_matches_legacy_repository() -> None:
    catalog = XlsxMaterialsCatalog()

    for unit_system in (UnitSystem.SI, UnitSystem.US):
        typed = catalog.get_plate_steel(steel_type="ASTM A572 Gr 50", unit_system=unit_system)
        legacy = get_plate_steel_properties(steel_type="ASTM A572 Gr 50", unit_system=unit_system)

        assert typed.steel_type == legacy["steel_type"]
        _assert_quantity_equal(typed.fy, legacy["fy"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.fu, legacy["fu"])  # type: ignore[arg-type]
        assert typed.ry == legacy["ry"]
        assert typed.rt == legacy["rt"]
        assert typed.source.sheet == "Platinas"
        assert typed.source.checksum_sha256


def test_xlsx_bolt_material_matches_legacy_repository() -> None:
    catalog = XlsxMaterialsCatalog()

    for unit_system in (UnitSystem.SI, UnitSystem.US):
        typed = catalog.get_bolt_material(
            description="Grupo 150",
            specification="ASTM A490",
            unit_system=unit_system,
        )
        legacy = get_bolt_strength_properties(
            description="Grupo 150",
            specification="ASTM A490",
            unit_system=unit_system,
        )

        assert typed.description == legacy["description"]
        assert typed.specification == legacy["specification"]
        _assert_quantity_equal(typed.fnt, legacy["fnt"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.fnv_threads_not_excluded, legacy["fnv_threads_not_excluded"])  # type: ignore[arg-type]
        _assert_quantity_equal(typed.fnv_threads_excluded, legacy["fnv_threads_excluded"])  # type: ignore[arg-type]
        assert typed.source.sheet == "Pernos"
        assert typed.source.checksum_sha256


def test_weld_material_is_separate_from_steel_and_bolt_materials() -> None:
    weld = weld_material_from_fexx(
        electrode="E70",
        fexx=Quantity(value=490.0, unit="MPa"),
    )

    assert weld.electrode == "E70"
    assert weld.fexx.value == 490.0
    assert weld.fexx.unit == "MPa"
    assert weld.source is None
