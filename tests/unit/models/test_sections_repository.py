from __future__ import annotations

import pytest

from steel_connections.data.sections_repository import get_beam_profile_properties, get_bolt_section_properties
from steel_connections.models.errors import StructuredEngineException
from steel_connections.models.units import UnitSystem


def test_beam_profile_is_loaded_from_sections_catalog_us() -> None:
    props = get_beam_profile_properties(beam_shape="W24X76", unit_system=UnitSystem.US)
    assert round(props["d"].value, 3) == round(607.0 / 25.4, 3)
    assert props["d"].unit == "in"
    assert props["bf"].unit == "in"
    assert props["tf"].unit == "in"
    assert props["tw"].unit == "in"
    assert props["kdes"].unit == "in"
    assert round(props["kdes"].value, 3) == round(30.0 / 25.4, 3)
    assert props["zx"].unit == "in3"
    assert round(props["zx"].value, 3) == round(3280.0 / 16.387064, 3)


def test_unknown_beam_shape_fails_hard() -> None:
    with pytest.raises(StructuredEngineException):
        get_beam_profile_properties(beam_shape="W00X000", unit_system=UnitSystem.US)


def test_bolt_geometry_is_loaded_from_perno_sheet() -> None:
    props = get_bolt_section_properties(bolt_shape='P1-1/8"X1-3/4"', unit_system=UnitSystem.SI)
    assert props["diameter_nominal"].unit == "mm"
    assert round(props["diameter_nominal"].value, 3) == round(1.125 * 25.4, 3)
