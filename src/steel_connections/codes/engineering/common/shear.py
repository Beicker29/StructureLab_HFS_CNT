from __future__ import annotations

from steel_connections.models.units import Quantity, UnitSystem, validate_quantity_unit


def compute_element_shear_yielding_strength_j42a(
    *,
    material_fy: Quantity,
    gross_shear_area_agv: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute element shear-yielding strength per AISC 360-22 J4.2(a).

    Equation:
    - ``Rn = 0.60*Fy*Agv``
    - ``phi*Rn = phi_n*Rn``
    """

    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    validate_quantity_unit(gross_shear_area_agv, "area", unit_system, "gross_shear_area_agv")

    rn_base = 0.60 * material_fy.value * gross_shear_area_agv.value
    phi_rn_base = phi_n * rn_base
    if unit_system == UnitSystem.US:
        rn = Quantity(value=rn_base, unit="kip")
        phi_rn = Quantity(value=phi_rn_base, unit="kip")
    else:
        # SI: MPa * mm2 = N
        rn = Quantity(value=rn_base / 1000.0, unit="kN")
        phi_rn = Quantity(value=phi_rn_base / 1000.0, unit="kN")

    return phi_rn, {
        "reference": "AISC 360-22 J4.2(a)",
        "equation_nominal": "Rn = 0.60*Fy*Agv",
        "equation_design": "phi*Rn = phi_n*Rn",
        "rn": rn,
        "phi_n": phi_n,
    }


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


def compute_block_shear_strength_j45(
    *,
    material_fu: Quantity,
    material_fy: Quantity,
    net_shear_area_anv: Quantity,
    gross_shear_area_agv: Quantity,
    net_tension_area_ant: Quantity,
    ubs_factor: float,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute block-shear strength per AISC 360-22 J4-5.

    Equations:
    - ``Rn_1 = 0.60*Fu*Anv + Ubs*Fu*Ant``
    - ``Rn_2 = 0.60*Fy*Agv + Ubs*Fu*Ant``
    - ``Rn = min(Rn_1, Rn_2)``
    - ``phi*Rn = phi_n*Rn``
    """

    validate_quantity_unit(material_fu, "stress", unit_system, "material_fu")
    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    validate_quantity_unit(net_shear_area_anv, "area", unit_system, "net_shear_area_anv")
    validate_quantity_unit(gross_shear_area_agv, "area", unit_system, "gross_shear_area_agv")
    validate_quantity_unit(net_tension_area_ant, "area", unit_system, "net_tension_area_ant")

    rn1_base = (
        0.60 * material_fu.value * net_shear_area_anv.value
        + ubs_factor * material_fu.value * net_tension_area_ant.value
    )
    rn2_base = (
        0.60 * material_fy.value * gross_shear_area_agv.value
        + ubs_factor * material_fu.value * net_tension_area_ant.value
    )
    rn_base = min(rn1_base, rn2_base)
    phi_rn_base = phi_n * rn_base

    if unit_system == UnitSystem.US:
        rn1 = Quantity(value=rn1_base, unit="kip")
        rn2 = Quantity(value=rn2_base, unit="kip")
        rn = Quantity(value=rn_base, unit="kip")
        phi_rn = Quantity(value=phi_rn_base, unit="kip")
    else:
        # SI: MPa * mm2 = N
        rn1 = Quantity(value=rn1_base / 1000.0, unit="kN")
        rn2 = Quantity(value=rn2_base / 1000.0, unit="kN")
        rn = Quantity(value=rn_base / 1000.0, unit="kN")
        phi_rn = Quantity(value=phi_rn_base / 1000.0, unit="kN")

    controlling = "rn1_fu_anv_ant" if rn1_base <= rn2_base else "rn2_fy_agv_ant"
    return phi_rn, {
        "reference": "AISC 360-22 J4-5",
        "equation_nominal_1": "Rn_1 = 0.60*Fu*Anv + Ubs*Fu*Ant",
        "equation_nominal_2": "Rn_2 = 0.60*Fy*Agv + Ubs*Fu*Ant",
        "equation_nominal": "Rn = min(Rn_1, Rn_2)",
        "equation_design": "phi*Rn = phi_n*Rn",
        "rn1": rn1,
        "rn2": rn2,
        "rn": rn,
        "phi_n": phi_n,
        "ubs_factor": ubs_factor,
        "controlling": controlling,
    }


def compute_element_tension_rupture_strength_j41b(
    *,
    material_fu: Quantity,
    effective_net_area_ae: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute element tension-rupture strength per AISC 360-22 J4.1(b), J4-2.

    Equations:
    - ``Rn = Fu*Ae``
    - ``phi*Rn = phi_n*Rn``
    """

    validate_quantity_unit(material_fu, "stress", unit_system, "material_fu")
    validate_quantity_unit(effective_net_area_ae, "area", unit_system, "effective_net_area_ae")

    rn_base = material_fu.value * effective_net_area_ae.value
    phi_rn_base = phi_n * rn_base
    if unit_system == UnitSystem.US:
        rn = Quantity(value=rn_base, unit="kip")
        phi_rn = Quantity(value=phi_rn_base, unit="kip")
    else:
        # SI: MPa * mm2 = N
        rn = Quantity(value=rn_base / 1000.0, unit="kN")
        phi_rn = Quantity(value=phi_rn_base / 1000.0, unit="kN")

    return phi_rn, {
        "reference": "AISC 360-22 J4.1(b), Eq. J4-2",
        "equation_nominal": "Rn = Fu*Ae",
        "equation_design": "phi*Rn = phi_n*Rn",
        "rn": rn,
        "phi_n": phi_n,
    }


def compute_element_tension_yielding_strength_j41a(
    *,
    material_fy: Quantity,
    gross_tension_area_agt: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute element tension-yielding strength per AISC 360-22 J4.1(a), Eq. J4-1.

    Equations:
    - ``Rn = Fy*Ag``
    - ``phi*Rn = phi_n*Rn``
    """

    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    validate_quantity_unit(gross_tension_area_agt, "area", unit_system, "gross_tension_area_agt")

    rn_base = material_fy.value * gross_tension_area_agt.value
    phi_rn_base = phi_n * rn_base
    if unit_system == UnitSystem.US:
        rn = Quantity(value=rn_base, unit="kip")
        phi_rn = Quantity(value=phi_rn_base, unit="kip")
    else:
        # SI: MPa * mm2 = N
        rn = Quantity(value=rn_base / 1000.0, unit="kN")
        phi_rn = Quantity(value=phi_rn_base / 1000.0, unit="kN")

    return phi_rn, {
        "reference": "AISC 360-22 J4.1(a), Eq. J4-1",
        "equation_nominal": "Rn = Fy*Ag",
        "equation_design": "phi*Rn = phi_n*Rn",
        "rn": rn,
        "phi_n": phi_n,
    }
