from __future__ import annotations

from typing import Any

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_bseep_step6_1_bolt_tension_demand(
    *,
    mf: Quantity,
    h1: Quantity,
    h2: Quantity,
    h3: Quantity,
    h4: Quantity,
    connection_type: str,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute BSEEP bolt tension demand for Step 6.1.1.

    Equation (BSEEP):
    - ``Pu = Mf / (2*(h1 + h2))`` for 4ES
    - ``Pu = Mf / (2*(h1 + h2 + h3 + h4))`` for 8ES

    Reference:
    - AISC 358-22 Section 6.7 (bolt tension demand expression used in Step 6.1.1)
    """

    if connection_type not in {"bseep_4es", "bseep_8es"}:
        raise ValueError("connection_type must be 'bseep_4es' or 'bseep_8es'.")
    validate_quantity_unit(h1, "length", unit_system, "geometry.h1")
    validate_quantity_unit(h2, "length", unit_system, "geometry.h2")
    validate_quantity_unit(h3, "length", unit_system, "geometry.h3")
    validate_quantity_unit(h4, "length", unit_system, "geometry.h4")

    expected_moment_unit = "kip-in" if unit_system == UnitSystem.US else "kN-mm"
    if mf.unit != expected_moment_unit:
        raise ValueError(
            f"Invalid unit for 'mf'. Expected '{expected_moment_unit}', got '{mf.unit}'."
        )

    # Source: AISC 358-22 Section 6.7, bolt-row lever-arm demand format for BSEEP.
    if connection_type == "bseep_8es":
        sum_h = h1.value + h2.value + h3.value + h4.value
        equation = "Pu = Mf / (2*(h1 + h2 + h3 + h4))"
    else:
        sum_h = h1.value + h2.value
        equation = "Pu = Mf / (2*(h1 + h2))"

    if sum_h <= 0.0:
        raise ValueError("Computed sum_h must be positive for BSEEP Step 6.1.1.")

    rut_b = Quantity(value=mf.value / (2.0 * sum_h), unit="kip" if unit_system == UnitSystem.US else "kN")
    return {
        "equation": equation.replace("Pu", "Rut_b"),
        "reference": "AISC 358-22 Section 6.7",
        "rut_b": rut_b,
        # Backward-compatible alias.
        "pu": rut_b,
        "sum_h": Quantity(value=sum_h, unit=h1.unit),
    }
