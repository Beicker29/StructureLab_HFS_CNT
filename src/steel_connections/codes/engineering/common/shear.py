from __future__ import annotations

import math

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


def compute_rectangular_bar_flexural_yielding_strength_f111(
    *,
    material_fy: Quantity,
    plastic_section_modulus_z: Quantity,
    elastic_section_modulus_sx: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute flexural yielding strength for rectangular bars per AISC 360-22 F11.1.

    Equation:
    - ``Mn = Mp = Fy*Z <= 1.5*Fy*Sx``
    - ``phi*Mn = phi_n*Mn``
    """

    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    expected_modulus_unit = "in3" if unit_system == UnitSystem.US else "mm3"
    if plastic_section_modulus_z.unit != expected_modulus_unit:
        raise ValueError(
            f"Invalid unit at 'plastic_section_modulus_z'. Expected '{expected_modulus_unit}' for {unit_system.value}."
        )
    if elastic_section_modulus_sx.unit != expected_modulus_unit:
        raise ValueError(
            f"Invalid unit at 'elastic_section_modulus_sx'. Expected '{expected_modulus_unit}' for {unit_system.value}."
        )

    mn_mp_base = material_fy.value * plastic_section_modulus_z.value
    mn_limit_base = 1.5 * material_fy.value * elastic_section_modulus_sx.value
    mn_base = min(mn_mp_base, mn_limit_base)
    phi_mn_base = phi_n * mn_base

    if unit_system == UnitSystem.US:
        mn_mp = Quantity(value=mn_mp_base, unit="kip-in")
        mn_limit = Quantity(value=mn_limit_base, unit="kip-in")
        mn = Quantity(value=mn_base, unit="kip-in")
        phi_mn = Quantity(value=phi_mn_base, unit="kip-in")
    else:
        # SI: MPa * mm3 = N*mm
        mn_mp = Quantity(value=mn_mp_base / 1000.0, unit="kN-mm")
        mn_limit = Quantity(value=mn_limit_base / 1000.0, unit="kN-mm")
        mn = Quantity(value=mn_base / 1000.0, unit="kN-mm")
        phi_mn = Quantity(value=phi_mn_base / 1000.0, unit="kN-mm")

    controlling = "fy_z" if mn_mp_base <= mn_limit_base else "1p5_fy_sx"
    return phi_mn, {
        "reference": "AISC 360-22 F11.1, Eq. F11-1",
        "equation_nominal": "Mn = min(Fy*Z, 1.5*Fy*Sx)",
        "equation_design": "phi*Mn = phi_n*Mn",
        "mn_mp": mn_mp,
        "mn_limit_1p5_fy_sx": mn_limit,
        "mn": mn,
        "phi_n": phi_n,
        "controlling": controlling,
    }


def compute_rectangular_bar_net_flexural_rupture_strength_j55(
    *,
    material_fy: Quantity,
    plate_thickness_tp: Quantity,
    plate_height_h: Quantity,
    hole_plus_allowance_d_prime: Quantity,
    edge_e1: Quantity,
    edge_e2: Quantity,
    spacing_s: Quantity,
    bolt_rows_n: int,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute net flexural rupture strength for a perforated rectangular bar per J5.5.

    Equations:
    - ``h = e1 + (n-1)*s + e2``
    - ``Znet = tp*h^2/4 - d'*tp*sum_{i=0}^{n-1}|e1 + i*s - h/2|``
    - ``Rn = Fy*Znet``
    - ``phi*Rn = phi_n*Rn``
    """

    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    validate_quantity_unit(plate_thickness_tp, "length", unit_system, "plate_thickness_tp")
    validate_quantity_unit(plate_height_h, "length", unit_system, "plate_height_h")
    validate_quantity_unit(hole_plus_allowance_d_prime, "length", unit_system, "hole_plus_allowance_d_prime")
    validate_quantity_unit(edge_e1, "length", unit_system, "edge_e1")
    validate_quantity_unit(edge_e2, "length", unit_system, "edge_e2")
    validate_quantity_unit(spacing_s, "length", unit_system, "spacing_s")
    if bolt_rows_n < 1:
        raise ValueError("bolt_rows_n must be >= 1.")
    if not (
        plate_thickness_tp.unit
        == plate_height_h.unit
        == hole_plus_allowance_d_prime.unit
        == edge_e1.unit
        == edge_e2.unit
        == spacing_s.unit
    ):
        raise ValueError("All length inputs must share the same unit for J5.5 flexural rupture.")

    h_calc = edge_e1.value + (bolt_rows_n - 1) * spacing_s.value + edge_e2.value
    half_h = h_calc / 2.0
    sum_abs = 0.0
    for i in range(bolt_rows_n):
        sum_abs += abs(edge_e1.value + i * spacing_s.value - half_h)

    z_gross = plate_thickness_tp.value * (plate_height_h.value**2) / 4.0
    z_net = z_gross - hole_plus_allowance_d_prime.value * plate_thickness_tp.value * sum_abs

    rn_base = material_fy.value * z_net
    phi_rn_base = phi_n * rn_base

    section_modulus_unit = "in3" if unit_system == UnitSystem.US else "mm3"
    moment_unit = "kip-in" if unit_system == UnitSystem.US else "kN-mm"
    if unit_system == UnitSystem.US:
        z_gross_q = Quantity(value=z_gross, unit=section_modulus_unit)
        z_net_q = Quantity(value=z_net, unit=section_modulus_unit)
        rn = Quantity(value=rn_base, unit=moment_unit)
        phi_rn = Quantity(value=phi_rn_base, unit=moment_unit)
    else:
        z_gross_q = Quantity(value=z_gross, unit=section_modulus_unit)
        z_net_q = Quantity(value=z_net, unit=section_modulus_unit)
        rn = Quantity(value=rn_base / 1000.0, unit=moment_unit)
        phi_rn = Quantity(value=phi_rn_base / 1000.0, unit=moment_unit)

    return phi_rn, {
        "reference": "AISC 360-22 J5.5",
        "equation_nominal": "Rn = Fy*Znet",
        "equation_design": "phi*Rn = phi_n*Rn",
        "h_calc": Quantity(value=h_calc, unit=edge_e1.unit),
        "sum_abs": Quantity(value=sum_abs, unit=edge_e1.unit),
        "z_gross": z_gross_q,
        "z_net": z_net_q,
        "rn": rn,
        "phi_n": phi_n,
    }


def compute_rectangular_bar_ltb_strength_f112(
    *,
    material_fy: Quantity,
    modulus_e: Quantity,
    unbraced_length_lb: Quantity,
    bar_depth_d: Quantity,
    bar_thickness_t: Quantity,
    elastic_section_modulus_sx: Quantity,
    plastic_moment_mp: Quantity,
    cb_factor: float,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute rectangular-bar flexural LTB strength per AISC 360-22 F11.2.

    Piecewise:
    - (a) ``Lb*d/t^2 <= 0.08*E/Fy`` -> LTB not governing.
    - (b) ``0.08*E/Fy < Lb*d/t^2 <= 1.9*E/Fy``:
      ``Mn = Cb*[1.52 - 0.274*(Lb*d/t^2)*(Fy/E)]*My <= Mp``
    - (c) ``Lb*d/t^2 > 1.9*E/Fy``:
      ``Fcr = 1.9*E*Cb/(Lb*d/t^2)`` and ``Mn = Fcr*Sx <= Mp``
    """

    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    validate_quantity_unit(modulus_e, "stress", unit_system, "modulus_e")
    validate_quantity_unit(unbraced_length_lb, "length", unit_system, "unbraced_length_lb")
    validate_quantity_unit(bar_depth_d, "length", unit_system, "bar_depth_d")
    validate_quantity_unit(bar_thickness_t, "length", unit_system, "bar_thickness_t")
    if cb_factor <= 0.0:
        raise ValueError("cb_factor must be > 0.")

    expected_modulus_unit = "in3" if unit_system == UnitSystem.US else "mm3"
    if elastic_section_modulus_sx.unit != expected_modulus_unit:
        raise ValueError(
            f"Invalid unit at 'elastic_section_modulus_sx'. Expected '{expected_modulus_unit}' for {unit_system.value}."
        )
    expected_moment_unit = "kip-in" if unit_system == UnitSystem.US else "kN-mm"
    if plastic_moment_mp.unit != expected_moment_unit:
        raise ValueError(
            f"Invalid unit at 'plastic_moment_mp'. Expected '{expected_moment_unit}' for {unit_system.value}."
        )

    slenderness = (unbraced_length_lb.value * bar_depth_d.value) / (bar_thickness_t.value ** 2)
    limit_a = 0.08 * modulus_e.value / material_fy.value
    limit_b = 1.9 * modulus_e.value / material_fy.value

    # Normalize Mp to base moment unit (N*mm for SI, kip-in for US base).
    mp_base = plastic_moment_mp.value if unit_system == UnitSystem.US else plastic_moment_mp.value * 1000.0
    mn_ltb_base: float
    fcr: Quantity | None = None
    case_id: str
    if slenderness <= limit_a:
        mn_ltb_base = mp_base
        case_id = "f112a_not_applicable"
    elif slenderness <= limit_b:
        my_base = material_fy.value * elastic_section_modulus_sx.value
        mn_expr = cb_factor * (1.52 - 0.274 * slenderness * (material_fy.value / modulus_e.value)) * my_base
        mn_ltb_base = min(mn_expr, mp_base)
        case_id = "f112b_inelastic_ltb"
    else:
        fcr_base = 1.9 * modulus_e.value * cb_factor / slenderness
        mn_expr = fcr_base * elastic_section_modulus_sx.value
        mn_ltb_base = min(mn_expr, mp_base)
        fcr = Quantity(value=fcr_base, unit=material_fy.unit)
        case_id = "f112c_elastic_ltb"

    phi_mn_base = phi_n * mn_ltb_base
    if unit_system == UnitSystem.US:
        mn = Quantity(value=mn_ltb_base, unit="kip-in")
        phi_mn = Quantity(value=phi_mn_base, unit="kip-in")
    else:
        mn = Quantity(value=mn_ltb_base / 1000.0, unit="kN-mm")
        phi_mn = Quantity(value=phi_mn_base / 1000.0, unit="kN-mm")

    return phi_mn, {
        "reference": "AISC 360-22 F11.2, Eq. F11-3/F11-4/F11-5",
        "equation_nominal": "Mn per F11.2(a/b/c), capped by Mp",
        "equation_design": "phi*Mn = phi_n*Mn",
        "mn": mn,
        "phi_n": phi_n,
        "lb_d_over_t2": slenderness,
        "limit_a_0p08e_over_fy": limit_a,
        "limit_b_1p9e_over_fy": limit_b,
        "cb_factor": cb_factor,
        "case_id": case_id,
        "fcr": fcr,
    }
