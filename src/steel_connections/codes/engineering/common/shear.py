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


def compute_whitmore_section_area(
    *,
    plate_width_b: Quantity,
    plate_thickness_t: Quantity,
    primary_spacing_p: Quantity,
    n_primary_lines: int,
    internal_gage_g1: Quantity,
    secondary_spacing_g: Quantity,
    n_secondary_lines: int,
    unit_system: UnitSystem,
    whitmore_angle_deg: float = 30.0,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute Whitmore effective gross section area for bolted plate checks.

    Expressions:
    - ``L_whitmore = 2*(n_primary_lines-1)*p*tan(theta) + g1 + 2*(n_secondary_lines-1)*g``
    - ``A_rect = B*t``
    - ``A_whitmore = L_whitmore*t``
    - ``A_gt = min(A_rect, A_whitmore)``
    """

    validate_quantity_unit(plate_width_b, "length", unit_system, "plate_width_b")
    validate_quantity_unit(plate_thickness_t, "length", unit_system, "plate_thickness_t")
    validate_quantity_unit(primary_spacing_p, "length", unit_system, "primary_spacing_p")
    validate_quantity_unit(internal_gage_g1, "length", unit_system, "internal_gage_g1")
    validate_quantity_unit(secondary_spacing_g, "length", unit_system, "secondary_spacing_g")

    if n_primary_lines < 1:
        raise ValueError("n_primary_lines must be >= 1.")
    if n_secondary_lines < 1:
        raise ValueError("n_secondary_lines must be >= 1.")
    if whitmore_angle_deg <= 0.0 or whitmore_angle_deg >= 90.0:
        raise ValueError("whitmore_angle_deg must be between 0 and 90 degrees.")

    length_unit = plate_width_b.unit
    if not (
        plate_thickness_t.unit == length_unit
        and primary_spacing_p.unit == length_unit
        and internal_gage_g1.unit == length_unit
        and secondary_spacing_g.unit == length_unit
    ):
        raise ValueError(
            "plate_width_b, plate_thickness_t, primary_spacing_p, internal_gage_g1, and secondary_spacing_g must share length unit."
        )

    tan_theta = math.tan(math.radians(whitmore_angle_deg))
    whitmore_length = (
        2.0 * (n_primary_lines - 1) * primary_spacing_p.value * tan_theta
        + internal_gage_g1.value
        + 2.0 * (n_secondary_lines - 1) * secondary_spacing_g.value
    )
    whitmore_length_q = Quantity(value=whitmore_length, unit=length_unit)

    area_unit = "in2" if unit_system == UnitSystem.US else "mm2"
    area_rect = Quantity(
        value=plate_width_b.value * plate_thickness_t.value,
        unit=area_unit,
    )
    area_whitmore = Quantity(
        value=whitmore_length_q.value * plate_thickness_t.value,
        unit=area_unit,
    )
    agt = area_rect if area_rect.value <= area_whitmore.value else area_whitmore
    controlling = "rectangular_b_t" if area_rect.value <= area_whitmore.value else "whitmore"

    return agt, {
        "reference": "Whitmore section geometry (reusable DRY helper)",
        "equation_length": "L_whitmore = 2*(n_primary_lines-1)*p*tan(theta) + g1 + 2*(n_secondary_lines-1)*g",
        "equation_area_rect": "A_rect = B*t",
        "equation_area_whitmore": "A_whitmore = L_whitmore*t",
        "equation_area_governing": "A_gt = min(A_rect, A_whitmore)",
        "whitmore_angle_deg": whitmore_angle_deg,
        "tan_theta": tan_theta,
        "whitmore_length": whitmore_length_q,
        "area_rect": area_rect,
        "area_whitmore": area_whitmore,
        "controlling": controlling,
    }


def compute_half_beam_wt_centroid_distance_from_flange_edge(
    *,
    beam_depth_d: Quantity,
    flange_width_bf: Quantity,
    flange_thickness_tf: Quantity,
    web_thickness_tw: Quantity,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str]]:
    """Compute centroid distance from flange outer edge for half-beam treated as WT.

    Geometric model (top half of a symmetric W shape):
    - ``h_w`` is the full beam depth from catalog (typically ``d_vg``).
    - Effective half-web height:
      ``h_w_eff = h_w*0.5 - tf``.
    - Flange rectangle: ``A_f = bf * tf`` with centroid at ``y_f = tf/2``.
    - Half-web rectangle:
      ``A_w = h_w_eff * tw = (h_w*0.5 - tf)*tw``,
      with centroid at ``y_w = tf + h_w_eff/2``.
    - WT centroid distance from flange outer edge:
      ``x_wt = (A_f*y_f + A_w*y_w) / (A_f + A_w)``.
    """

    validate_quantity_unit(beam_depth_d, "length", unit_system, "beam_depth_d")
    validate_quantity_unit(flange_width_bf, "length", unit_system, "flange_width_bf")
    validate_quantity_unit(flange_thickness_tf, "length", unit_system, "flange_thickness_tf")
    validate_quantity_unit(web_thickness_tw, "length", unit_system, "web_thickness_tw")

    length_unit = beam_depth_d.unit
    if not (
        flange_width_bf.unit == length_unit
        and flange_thickness_tf.unit == length_unit
        and web_thickness_tw.unit == length_unit
    ):
        raise ValueError("beam_depth_d, flange_width_bf, flange_thickness_tf, and web_thickness_tw must share unit.")

    if beam_depth_d.value <= 0.0:
        raise ValueError("beam_depth_d must be > 0.")
    if flange_width_bf.value <= 0.0:
        raise ValueError("flange_width_bf must be > 0.")
    if flange_thickness_tf.value <= 0.0:
        raise ValueError("flange_thickness_tf must be > 0.")
    if web_thickness_tw.value <= 0.0:
        raise ValueError("web_thickness_tw must be > 0.")

    h_w = beam_depth_d.value
    h_w_eff = 0.5 * h_w - flange_thickness_tf.value
    if h_w_eff <= 0.0:
        raise ValueError("Invalid half-web height: require d/2 - tf > 0.")

    area_unit = "in2" if unit_system == UnitSystem.US else "mm2"
    af = flange_width_bf.value * flange_thickness_tf.value
    aw = h_w_eff * web_thickness_tw.value
    at = af + aw
    if at <= 0.0:
        raise ValueError("Total WT area must be > 0.")

    y_f = 0.5 * flange_thickness_tf.value
    y_w = flange_thickness_tf.value + 0.5 * h_w_eff
    x_wt = (af * y_f + aw * y_w) / at

    return Quantity(value=x_wt, unit=length_unit), {
        "reference": "Half-beam WT centroid geometry helper",
        "equation_beam_depth": "h_w = d (altura total de la viga tomada del catalogo)",
        "equation_half_web_height_effective": "h_w_eff = h_w*0.5 - tf",
        "equation_flange_area": "A_f = bf*tf",
        "equation_half_web_area": "A_w = h_w_eff*tw = (h_w*0.5 - tf)*tw",
        "equation_centroid": "x_wt = (A_f*y_f + A_w*y_w)/(A_f + A_w)",
        "beam_depth_h_w": Quantity(value=h_w, unit=length_unit),
        "half_web_height_effective_h_w_eff": Quantity(value=h_w_eff, unit=length_unit),
        "flange_area_af": Quantity(value=af, unit=area_unit),
        "half_web_area_aw": Quantity(value=aw, unit=area_unit),
        "total_area_at": Quantity(value=at, unit=area_unit),
        "y_f": Quantity(value=y_f, unit=length_unit),
        "y_w": Quantity(value=y_w, unit=length_unit),
    }


def compute_u_v3_shear_lag_factor_case2(
    *,
    alpha_pu_web: float,
    n_blt_web_x: int,
    n_blt_flange_x: int,
    t_vg: Quantity,
    tw_vg: Quantity,
    bf_vg: Quantity,
    a_vg: Quantity,
    g_blt_web: Quantity,
    p_plt_flange: Quantity,
    xt_flange_vg: Quantity,
    unit_system: UnitSystem,
) -> tuple[float, dict[str, Quantity | float | str]]:
    """Compute ``U_v3_vg`` (shear-lag factor) for splice ELR #2 with case scaffold.

    This helper implements the currently requested criterion set for 4.5.1
    (treated as *Caso 2*), while keeping explicit branch labels that allow
    future expansion.

    Piecewise selection by ``alpha_Pu_web``:
    - ``0.75 < alpha <= 1``: use web expression.
    - ``0.25 < alpha <= 0.75`` (*Caso 2*): use ``max(U_web, U_flange)``.
    - ``0.00 < alpha <= 0.25``: use flange expression.

    Final cap:
    - ``U_v3_vg <= 1``.
    """

    validate_quantity_unit(t_vg, "length", unit_system, "t_vg")
    validate_quantity_unit(tw_vg, "length", unit_system, "tw_vg")
    validate_quantity_unit(bf_vg, "length", unit_system, "bf_vg")
    validate_quantity_unit(g_blt_web, "length", unit_system, "g_blt_web")
    validate_quantity_unit(p_plt_flange, "length", unit_system, "p_plt_flange")
    validate_quantity_unit(xt_flange_vg, "length", unit_system, "xt_flange_vg")
    validate_quantity_unit(a_vg, "area", unit_system, "a_vg")

    if n_blt_web_x < 1:
        raise ValueError("n_blt_web_x must be >= 1.")
    if n_blt_flange_x < 1:
        raise ValueError("n_blt_flange_x must be >= 1.")
    if a_vg.value <= 0.0:
        raise ValueError("a_vg must be > 0.")
    if g_blt_web.value <= 0.0:
        raise ValueError("g_blt_web must be > 0.")
    if p_plt_flange.value <= 0.0:
        raise ValueError("p_plt_flange must be > 0.")

    if n_blt_web_x <= 1:
        u_web = (t_vg.value * tw_vg.value) / a_vg.value
        u_web_formula = "si n_blt_web_x <= 1 -> U_web = T_vg*tw_vg/A_vg"
    else:
        u_web = 1.0 - 0.5 * tw_vg.value / ((n_blt_web_x - 1) * g_blt_web.value)
        u_web_formula = "si n_blt_web_x > 1 -> U_web = 1 - 0.5*tw_vg/((n_blt_web_x - 1)*g_blt_web)"

    if n_blt_flange_x <= 1:
        u_flange = 2.0 * bf_vg.value * tw_vg.value / a_vg.value
        u_flange_formula = "si n_blt_flange_x <= 1 -> U_flange = 2*bf_vg*tw_vg/A_vg"
    else:
        u_flange = 1.0 - xt_flange_vg.value / ((n_blt_flange_x - 1) * p_plt_flange.value)
        u_flange_formula = (
            "si n_blt_flange_x > 1 -> U_flange = 1 - xt_flange_vg/((n_blt_flange_x - 1)*p_plt_flange)"
        )

    if 0.75 < alpha_pu_web <= 1.0:
        selected_case = "2.1"
        u_raw = u_web
        selection_formula = "Subcaso 2.1: si 0.75 < alpha_Pu_web <= 1 -> U_v3_vg = U_web"
    elif 0.25 < alpha_pu_web <= 0.75:
        selected_case = "2.2"
        u_raw = max(u_web, u_flange)
        selection_formula = "Subcaso 2.2: si 0.25 < alpha_Pu_web <= 0.75 -> U_v3_vg = max(U_web, U_flange)"
    elif alpha_pu_web <= 0.25:
        selected_case = "2.3"
        u_raw = u_flange
        selection_formula = "Subcaso 2.3: si alpha_Pu_web <= 0.25 -> U_v3_vg = U_flange"
    else:
        selected_case = "2.1_fallback_alpha_gt_1"
        u_raw = u_web
        selection_formula = "alpha_Pu_web > 1.00 -> fallback Subcaso 2.1 (U_v3_vg = U_web)"

    u_capped = min(u_raw, 1.0)
    cap_formula = "U_v3_vg <= 1 -> U_v3_vg = min(U_raw, 1.0)"

    return u_capped, {
        "reference": "Splice web tension rupture helper (ELR #2, Caso 2 con subcasos 2.1/2.2/2.3)",
        "u_web_formula": u_web_formula,
        "u_flange_formula": u_flange_formula,
        "selection_formula": selection_formula,
        "cap_formula": cap_formula,
        "selected_case": selected_case,
        "u_web": u_web,
        "u_flange": u_flange,
        "u_raw": u_raw,
        "u_capped": u_capped,
        "alpha_pu_web": alpha_pu_web,
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


def compute_member_flexural_rupture_with_tension_flange_holes_f131(
    *,
    material_fu: Quantity,
    material_fy: Quantity,
    net_tension_flange_area_afn: Quantity,
    gross_tension_flange_area_agf: Quantity,
    elastic_section_modulus_sx: Quantity,
    phi_n: float,
    unit_system: UnitSystem,
) -> tuple[Quantity, dict[str, Quantity | float | str | bool]]:
    """Compute F13.1 flexural rupture limit for members with holes in tension flange.

    AISC 360-22 F13.1:
    - ``Yf = 1.0`` if ``Fy/Fu <= 0.8`` else ``1.1``.
    - If ``Fu*Afn >= Yf*Fy*Agf`` the tensile-rupture limit does not apply.
    - Else, at hole location ``Mn <= (Fu*Afn/Agf)*Sx``.
    - Design strength: ``phi*Mn = phi_n*Mn``.
    """

    validate_quantity_unit(material_fu, "stress", unit_system, "material_fu")
    validate_quantity_unit(material_fy, "stress", unit_system, "material_fy")
    validate_quantity_unit(net_tension_flange_area_afn, "area", unit_system, "net_tension_flange_area_afn")
    validate_quantity_unit(gross_tension_flange_area_agf, "area", unit_system, "gross_tension_flange_area_agf")

    if net_tension_flange_area_afn.unit != gross_tension_flange_area_agf.unit:
        raise ValueError("net_tension_flange_area_afn and gross_tension_flange_area_agf must share area unit.")
    if gross_tension_flange_area_agf.value <= 0.0:
        raise ValueError("gross_tension_flange_area_agf must be > 0.")

    expected_modulus_unit = "in3" if unit_system == UnitSystem.US else "mm3"
    if elastic_section_modulus_sx.unit != expected_modulus_unit:
        raise ValueError(
            f"Invalid unit at 'elastic_section_modulus_sx'. Expected '{expected_modulus_unit}' for {unit_system.value}."
        )

    fy_over_fu = material_fy.value / material_fu.value
    yf = 1.0 if fy_over_fu <= 0.8 else 1.1

    lhs_fu_afn = material_fu.value * net_tension_flange_area_afn.value
    rhs_yf_fy_agf = yf * material_fy.value * gross_tension_flange_area_agf.value
    tensile_rupture_limit_applies = lhs_fu_afn < rhs_yf_fy_agf

    mn_base = (lhs_fu_afn / gross_tension_flange_area_agf.value) * elastic_section_modulus_sx.value
    phi_mn_base = phi_n * mn_base

    if unit_system == UnitSystem.US:
        mn = Quantity(value=mn_base, unit="kip-in")
        phi_mn = Quantity(value=phi_mn_base, unit="kip-in")
    else:
        # SI: MPa * mm3 = N*mm
        mn = Quantity(value=mn_base / 1000.0, unit="kN-mm")
        phi_mn = Quantity(value=phi_mn_base / 1000.0, unit="kN-mm")

    lhs_q = (
        Quantity(value=lhs_fu_afn, unit="kip")
        if unit_system == UnitSystem.US
        else Quantity(value=lhs_fu_afn / 1000.0, unit="kN")
    )
    rhs_q = (
        Quantity(value=rhs_yf_fy_agf, unit="kip")
        if unit_system == UnitSystem.US
        else Quantity(value=rhs_yf_fy_agf / 1000.0, unit="kN")
    )

    return phi_mn, {
        "reference": "AISC 360-22 F13.1, Eq. F13-1",
        "equation_nominal": "Mn = (Fu*Afn/Agf)*Sx",
        "equation_design": "phi*Mn = phi_n*Mn",
        "yf": yf,
        "fy_over_fu": fy_over_fu,
        "lhs_fu_afn": lhs_q,
        "rhs_yf_fy_agf": rhs_q,
        "tensile_rupture_limit_applies": tensile_rupture_limit_applies,
        "mn": mn,
        "phi_n": phi_n,
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
