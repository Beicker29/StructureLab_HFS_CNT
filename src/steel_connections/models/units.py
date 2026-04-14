from __future__ import annotations

import math
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class UnitSystem(str, Enum):
    US = "US"
    SI = "SI"


class Quantity(StrictModel):
    value: float
    unit: str

    @field_validator("value")
    @classmethod
    def validate_finite_value(cls, value: float) -> float:
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Quantity value must be finite.")
        return value


ALLOWED_UNITS: dict[UnitSystem, dict[str, set[str]]] = {
    UnitSystem.US: {
        "stress": {"ksi"},
        "area": {"in2"},
        "force": {"kip"},
        "length": {"in"},
    },
    UnitSystem.SI: {
        "stress": {"MPa"},
        "area": {"mm2"},
        "force": {"kN", "N"},
        "length": {"mm"},
    },
}


def validate_quantity_unit(
    quantity: Quantity,
    quantity_kind: str,
    unit_system: UnitSystem,
    field_path: str,
) -> None:
    allowed = ALLOWED_UNITS[unit_system][quantity_kind]
    if quantity.unit not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise ValueError(
            f"Invalid unit at '{field_path}'. Received '{quantity.unit}'. "
            f"Allowed for {unit_system.value}/{quantity_kind}: {allowed_text}."
        )


def to_design_force_unit(force: Quantity, unit_system: UnitSystem) -> Quantity:
    validate_quantity_unit(force, "force", unit_system, "force")
    if unit_system == UnitSystem.US:
        return force
    if force.unit == "kN":
        return force
    return Quantity(value=force.value / 1000.0, unit="kN")
