from __future__ import annotations

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_element_shear_rupture_strength_j43(
    *,
    material_fu: Quantity,
    net_shear_area_anv: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute element shear-rupture strength per AISC 360-22 J4.3(b).

    Equation:
    - ``Rn = 0.60*Fu*Anv``
    - ``phi*Rn = phi_n*Rn``
    """

    validate_quantity_unit(material_fu, "stress", unit_system, "material_fu")
    validate_quantity_unit(net_shear_area_anv, "area", unit_system, "net_shear_area_anv")

    rn_base = 0.60 * material_fu.value * net_shear_area_anv.value
    phi_rn_base = phi_n * rn_base
    if unit_system == UnitSystem.US:
        rn = Quantity(value=rn_base, unit="kip")
        phi_rn = Quantity(value=phi_rn_base, unit="kip")
    else:
        # SI: MPa * mm2 = N
        rn = Quantity(value=rn_base / 1000.0, unit="kN")
        phi_rn = Quantity(value=phi_rn_base / 1000.0, unit="kN")

    return phi_rn, {
        "reference": "AISC 360-22 J4.3(b)",
        "equation_nominal": "Rn = 0.60*Fu*Anv",
        "equation_design": "phi*Rn = phi_n*Rn",
        "rn": rn,
        "phi_n": phi_n,
    }

