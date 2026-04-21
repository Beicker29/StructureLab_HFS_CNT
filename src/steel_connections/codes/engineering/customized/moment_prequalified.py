from __future__ import annotations

from typing import Any

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_moment_prequalified_step6_1_bolt_tension_demand(
    *,
    mf: Quantity,
    h1: Quantity,
    h2: Quantity,
    connection_type: str,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute Step 6.1.1 bolt tension demand for BUEEP/BSEEP 4-bolt layouts.

    Equation:
    ``Rut_b = Mf / (2*(h1 + h2))``

    Reference:
    - AISC 358-22 Section 6.7 (project Step 6.1.1 interpretation)
    """

    if connection_type not in {"bueep_4e", "bseep_4es"}:
        raise ValueError("connection_type must be 'bueep_4e' or 'bseep_4es'.")
    validate_quantity_unit(h1, "length", unit_system, "geometry.h1")
    validate_quantity_unit(h2, "length", unit_system, "geometry.h2")

    expected_moment_unit = "kip-in" if unit_system == UnitSystem.US else "kN-mm"
    if mf.unit != expected_moment_unit:
        raise ValueError(
            f"Invalid unit for 'mf'. Expected '{expected_moment_unit}', got '{mf.unit}'."
        )

    # Source: AISC 358-22 Section 6.7, 4-bolt lever-arm demand format.
    sum_h = h1.value + h2.value
    if sum_h <= 0.0:
        raise ValueError("Computed sum_h must be positive for Step 6.1.1.")
    rut_b = Quantity(value=mf.value / (2.0 * sum_h), unit="kip" if unit_system == UnitSystem.US else "kN")
    return {
        "equation": "Rut_b = Mf / (2*(h1 + h2))",
        "reference": "AISC 358-22 Section 6.7",
        "rut_b": rut_b,
        "sum_h": Quantity(value=sum_h, unit=h1.unit),
    }


def compute_moment_prequalified_step6_2_bolt_shear_demand(
    *,
    vhmax: Quantity,
    connection_type: str,
    unit_system: UnitSystem,
) -> dict[str, Any]:
    """Compute Step 6.2.1 bolt shear demand for prequalified moment end-plate connections.

    Equation:
    ``Ruv2_b = Vhmax / nb``
    with ``nb = 4`` for ``bueep_4e`` and ``bseep_4es``,
    and ``nb = 8`` for ``bseep_8es``.

    Reference:
    - AISC 358-22 Section 6.7 (project Step 6.2.1 interpretation)
    """

    validate_quantity_unit(vhmax, "force", unit_system, "loads.vhmax")

    # Source: AISC 358-22 Section 6.7 bolt-row force distribution for Step 6.2.1.
    if connection_type in {"bueep_4e", "bseep_4es"}:
        nb = 4
    elif connection_type == "bseep_8es":
        nb = 8
    else:
        raise ValueError(
            "Unsupported connection_type for Step 6.2.1 demand. "
            "Expected one of: bueep_4e, bseep_4es, bseep_8es."
        )

    ruv2_b = Quantity(value=vhmax.value / float(nb), unit=vhmax.unit)
    return {
        "equation": "Ruv2_b = Vhmax/nb",
        "reference": "AISC 358-22 Section 6.7",
        "nb": nb,
        "ruv2_b": ruv2_b,
    }
