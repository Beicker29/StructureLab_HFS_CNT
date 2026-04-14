from __future__ import annotations

from steel_connections.data.materials_repository import (
    get_bolt_strength_properties,
    get_hrs_steel_properties,
    get_plate_steel_properties,
)
from steel_connections.models.units import UnitSystem


def test_hrs_material_is_loaded() -> None:
    props = get_hrs_steel_properties(steel_type="ASTM A572 Gr 50", unit_system=UnitSystem.SI)
    assert props["fy"].unit == "MPa"
    assert props["fu"].unit == "MPa"
    assert round(props["fy"].value, 3) == 345.0
    assert round(props["fu"].value, 3) == 450.0


def test_plate_material_is_loaded() -> None:
    props = get_plate_steel_properties(steel_type="ASTM A572 Gr 50", unit_system=UnitSystem.SI)
    assert props["fy"].unit == "MPa"
    assert props["fu"].unit == "MPa"
    assert round(props["fy"].value, 3) == 345.0
    assert round(props["fu"].value, 3) == 450.0


def test_bolt_strength_is_loaded() -> None:
    props = get_bolt_strength_properties(
        description="Grupo 150",
        specification="ASTM A490",
        unit_system=UnitSystem.SI,
    )
    assert props["fnt"].unit == "MPa"
    assert props["fnv_threads_not_excluded"].unit == "MPa"
    assert round(props["fnt"].value, 3) == 780.0
    assert round(props["fnv_threads_not_excluded"].value, 3) == 470.0
