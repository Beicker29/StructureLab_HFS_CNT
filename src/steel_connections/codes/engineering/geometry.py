from __future__ import annotations

from typing import Any

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_protected_zone_length(
    *,
    lst: Quantity | None,
    d: Quantity,
    bf: Quantity,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute protected-zone length.

    Equation:
    - Unstiffened: ``Lpz = min(d, 3bf)``
    - Stiffened: ``Lpz = min(lst + 0.5d, 3bf)``

    Reference:
    - AISC 358-22 Section 2.3.4(8)
    """

    validate_quantity_unit(d, "length", unit_system, "d")
    validate_quantity_unit(bf, "length", unit_system, "bf")
    if lst is not None:
        validate_quantity_unit(lst, "length", unit_system, "lst")

    if lst is None:
        candidate_a = d
        candidate_a_label = "d"
        equation = "Lpz = min(d, 3bf)"
    else:
        candidate_a = Quantity(value=lst.value + 0.5 * d.value, unit=d.unit)
        candidate_a_label = "lst + 0.5d"
        equation = "Lpz = min(lst + 0.5d, 3bf)"

    candidate_b = Quantity(value=3.0 * bf.value, unit=bf.unit)
    lpz = candidate_a if candidate_a.value <= candidate_b.value else candidate_b
    return {
        "equation": equation,
        "formula": equation,
        "reference": "AISC 358-22 Section 2.3.4(8)",
        "candidate_a_label": candidate_a_label,
        "candidate_a": candidate_a,
        "candidate_b_label": "3bf",
        "candidate_b": candidate_b,
        "lpz": lpz,
    }
