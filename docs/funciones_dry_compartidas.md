# Catalogo de funciones DRY compartidas

Este documento resume las funciones DRY de uso comun en el repo.
Fuente canonica: `src/steel_connections/codes/engineering/common`.

## 1) Utilizacion / DCR

`compute_dcr_ratio(demand, capacity)`

- Calcula `DCR = demand / capacity`.
- Devuelve si cumple (`passes`) con criterio `DCR <= 1.0`.

## 2) Pernos (J3.3 / J3.4 / J3.6 + resistencia)

`compute_bolt_hole_dimensions_j33(bolt_diameter, unit_system)`

- Devuelve dimensiones nominales de agujero (estandar, oversize, short-slot, long-slot) segun Tabla J3.3.

`compute_standard_hole_diameter_j33(bolt_diameter, unit_system)`

- Devuelve diametro de agujero estandar de Tabla J3.3.

`compute_spacing_requirements_j33(bolt_diameter, unit_system)`

- Devuelve separaciones minimas de J3.3 (centro-centro, preferida y clear distance).

`compute_minimum_bolt_spacing_j33(bolt_diameter, unit_system)`

- Devuelve separacion minima `Smin` de J3.3.

`compute_minimum_edge_distance_standard_hole_j34(bolt_diameter, unit_system)`

- Devuelve distancia minima al borde `Le_min` para agujero estandar (Tabla J3.4), con metadatos de fila usada.

`compute_entering_tightening_clearance_table_7_15(bolt_diameter, unit_system)`

- Devuelve clearances de constructibilidad de la Tabla 7-15 del Steel Construction Manual:
  - `H1`, `H2`, `C1`, `C2`, `C3_circular`, `C3_clipped`
- Para `bbmb_splice`, estos valores se toman del catalogo `data/sections.xlsx`, hoja `Perno`,
  asociados al perno de entrada (`shape + descripcion + norma`) via `get_bolt_section_properties`.

`get_minimum_staggered_pitch_from_f(width_across_flats, unit_system)` *(lookup de catalogo compartido)*

- Devuelve `Pmin` desde `data/sections.xlsx`, hoja `F_Perno`, a partir de `F` (width across flats) en pulgadas.

`compute_max_spacing_and_edge_distance_limits_j36(thinner_part_thickness, unit_system, is_unpainted_weathering_exposed)`

- Devuelve limites maximos de separacion y borde para J3.6 (regular/corrosivo).

`compute_maximum_bolt_spacing_j36(thinner_part_thickness, unit_system, is_unpainted_weathering_exposed)`

- Devuelve solo la separacion longitudinal maxima entre pernos de J3.6:
  - Regular: `Smax = min(24*t, 12 in / 300 mm)`
  - Corrosivo intemperie sin pintar: `Smax = min(14*t, 7 in / 180 mm)`

`compute_bolt_tension_rupture_capacity_per_bolt(bolt_diameter, bolt_fnt, unit_system, phi=0.9)`

- Calcula capacidad a traccion por perno (`Rn`, `phi*Rn`).

`compute_bolt_shear_rupture_capacity_per_bolt(bolt_diameter, bolt_fnv, unit_system, phi=0.9)`

- Calcula capacidad a cortante por perno (`Rn`, `phi*Rn`).

`compute_bolt_hole_tearout_strength_j36(material_fu, clear_distance_lc, connected_thickness_t, n_critical_bolts, phi_n, unit_system, deformation_at_service_is_design_consideration)`

- Calcula resistencia por desgarramiento (tearout) en agujero de perno, AISC 360-22 J3:
  - Con deformacion de servicio como criterio: `Rn1_ind = 1.2*lc*t*Fu` (J3-6c)
  - Sin deformacion de servicio como criterio: `Rn1_ind = 1.5*lc*t*Fu` (J3-6d)
  - Resistencia de diseno de grupo: `phi*Rn1 = phi_n*n_critical_bolts*Rn1_ind`

`compute_bolt_hole_bearing_strength_j36(material_fu, bolt_diameter_d, connected_thickness_t, phi_n, unit_system, deformation_at_service_is_design_consideration)`

- Calcula resistencia por aplatamiento (bearing) en agujero de perno, AISC 360-22 J3:
  - Con deformacion de servicio como criterio: `Rn2 = 2.4*d*t*Fu` (J3-6a)
  - Sin deformacion de servicio como criterio: `Rn2 = 3.0*d*t*Fu` (J3-6b)
  - Resistencia de diseno por perno: `phi*Rn2 = phi_n*Rn2`

`compute_element_shear_rupture_strength_j43(material_fu, net_shear_area_anv, phi_n, unit_system)`

- Calcula resistencia a rotura por cortante del elemento (no del perno), AISC 360-22 J4.3(b):
  - `Rn = 0.60*Fu*Anv`
  - `phi*Rn = phi_n*Rn`

`compute_block_shear_strength_j45(material_fu, material_fy, net_shear_area_anv, gross_shear_area_agv, net_tension_area_ant, ubs_factor, phi_n, unit_system)`

- Calcula resistencia a bloque de cortante del elemento, AISC 360-22 J4-5:
  - `Rn_1 = 0.60*Fu*Anv + Ubs*Fu*Ant`
  - `Rn_2 = 0.60*Fy*Agv + Ubs*Fu*Ant`
  - `Rn = min(Rn_1, Rn_2)`
  - `phi*Rn = phi_n*Rn`

`compute_element_tension_rupture_strength_j41b(material_fu, effective_net_area_ae, phi_n, unit_system)`

- Calcula resistencia a rotura por traccion del elemento conectado, AISC 360-22 J4.1(b), Eq. J4-2:
  - `Rn = Fu*Ae`
  - `phi*Rn = phi_n*Rn`

`compute_element_tension_yielding_strength_j41a(material_fy, gross_tension_area_agt, phi_n, unit_system)`

- Calcula resistencia a fluencia por traccion del elemento conectado, AISC 360-22 J4.1(a), Eq. J4-1:
  - `Rn = Fy*Ag`
  - `phi*Rn = phi_n*Rn`

`compute_whitmore_section_area(plate_width_b, plate_thickness_t, primary_spacing_p, n_primary_lines, internal_gage_g1, secondary_spacing_g, n_secondary_lines, unit_system, whitmore_angle_deg=30)`

- Calcula seccion bruta efectiva tipo Whitmore reusable para conexiones apernadas:
  - `L_whitmore = 2*(n_primary_lines-1)*p*tan(theta) + g1 + 2*(n_secondary_lines-1)*g`
  - `A_rect = B*t`
  - `A_whitmore = L_whitmore*t`
  - `A_gt = min(A_rect, A_whitmore)`
- Devuelve `A_gt` y trazabilidad completa (`L_whitmore`, `A_rect`, `A_whitmore`, caso controlante).

`compute_half_beam_wt_centroid_distance_from_flange_edge(beam_depth_d, flange_width_bf, flange_thickness_tf, web_thickness_tw, unit_system)`

- Calcula la distancia desde el borde exterior del ala al centroide de media viga tratada como perfil WT:
  - `h_w = d` (altura total de la viga tomada del catalogo de perfiles; para splice normalmente `d_vg`).
  - `h_w_eff = h_w*0.5 - tf`
  - `A_f = bf*tf`
  - `A_w = h_w_eff*tw = (h_w*0.5 - tf)*tw`
  - `x_wt = (A_f*y_f + A_w*y_w)/(A_f + A_w)`
  - donde `y_f = tf/2` y `y_w = tf + h_w_eff/2`.
- Devuelve `x_wt` y trazabilidad de areas/centroides parciales.

`compute_u_v3_shear_lag_factor_case2(alpha_pu_web, n_blt_web_x, n_blt_flange_x, t_vg, tw_vg, bf_vg, a_vg, g_blt_web, p_plt_flange, xt_flange_vg, unit_system)`

- Calcula el factor de rezago `U_v3_vg` para ELR #2 de rotura a traccion de la viga (4.5.1), definido como **Caso 2** con subcasos:
  - **Subcaso 2.1**: `0.75 < alpha_Pu_web <= 1` -> `U_v3_vg = U_web`
  - **Subcaso 2.2**: `0.25 < alpha_Pu_web <= 0.75` -> `U_v3_vg = max(U_web, U_flange)`
  - **Subcaso 2.3**: `alpha_Pu_web <= 0.25` -> `U_v3_vg = U_flange`
- Donde:
  - `U_web = T_vg*tw_vg/A_vg` si `n_blt_web_x <= 1`, si no `1 - 0.5*tw_vg/((n_blt_web_x-1)*g_blt_web)`
  - `U_flange = 2*bf_vg*tw_vg/A_vg` si `n_blt_flange_x <= 1`, si no `1 - xt_flange_vg/((n_blt_flange_x-1)*p_plt_flange)`
- Cierre obligatorio: `U_v3_vg = min(U_v3_raw, 1.0)` para asegurar `U_v3_vg <= 1`.
- Devuelve `U_v3_vg` y trazabilidad (`U_web`, `U_flange`, caso seleccionado, ecuaciones).

## 3) Limites de precalificacion EP (Tabla 6.1)

`compute_limites_precalificacion_conexion_tipo_ep(connection_type, unit_system)`

- Devuelve los limites geometricos de Tabla 6.1 para:
  - `bueep_4e`
  - `bseep_4es`
  - `bseep_8es`
- Campos devueltos por conexion: `tbf`, `bbf`, `d`, `tp`, `bp`, `g`, `pfi`, `pfo`, `pb`.
- Uso en reglas: chequeos de preclasificacion EP del Paso 3 (por ejemplo rangos y maximos de `pfi`, `pfo`, `de` combinados con J3.6).

## 4) Geometria de grupos de pernos

`build_bolt_group_geometry(bolts)`

- Construye invariantes geometricos del grupo (centroide, `Ix`, `Iy`, `Ixy`, `Ip`, offsets).

`build_in_plane_load(vx, vy, mz, x_ref, y_ref)`

- Crea carga en plano con excentricidad respecto a referencia.

`build_in_plane_load_from_explicit_eccentricity(vx, vy, mz, ex, ey)`

- Crea carga en plano usando excentricidades explicitas.

`build_rectangular_bolt_pattern(nx, ny, sx, sy, x0=0, y0=0, tag_prefix='B')`

- Genera patron rectangular de pernos.

`build_mirrored_half_flange_bolt_pattern(nx, nz_half, px, gz, g1z, x0=0, y0=0, tag_prefix='f')`

- Genera patron de pernos para una aleta cuando `n_blt_flange_z` se define por media aleta.
- Filas transversales:
  - `y_(m,Â±) = Â±(g1z/2 + m*gz)`, con `m = 0..nz_half-1`.
- Total de filas transversales en una aleta:
  - `N_y = 2*nz_half`.

## 5) Analisis elastico de grupos de pernos

`solve_elastic_superposition(geometry, load, bolt_capacity, epsilon=1e-12)`
- Resuelve demandas por superposicion elastica (cortante directo + torsion).

`solve_elastic_center_of_rotation(geometry, load, bolt_capacity, epsilon=1e-12)`
- Resuelve por metodo elastico con centro de rotacion (ECR).

## 6) Analisis ICR de grupos de pernos

`solve_instant_center_of_rotation(geometry, load, bolt_capacity, law=ICRLawParameters(), tolerance=0.01, max_iterations=1000, epsilon=1e-12)`
- Resuelve por metodo ICR no lineal.

`ICRLawParameters`
- Parametros de la ley no lineal de pernos para ICR (`mu`, `lambda_exp`, `delta_max`).

## 7) Solver unificado de grupos de pernos

`solve_bolt_group_method(method, geometry, load, bolt_capacity, options=None)`
- Enrutador unico para resolver por metodo (elastico-superposicion, elastico-ECR, ICR).

`BoltGroupSolverOptions`
- Configuracion comun de solucion (`tolerance`, `max_iterations`, `icr_law`).

## 8) Flexion de barras rectangulares

`compute_rectangular_bar_flexural_yielding_strength_f111(material_fy, plastic_section_modulus_z, elastic_section_modulus_sx, phi_n, unit_system)`

- Fluencia por flexion (AISC 360-22 F11.1):
  - `Mn = min(Fy*Z, 1.5*Fy*Sx)`
  - `phi*Mn = phi_n*Mn`

`compute_member_flexural_rupture_with_tension_flange_holes_f131(material_fu, material_fy, net_tension_flange_area_afn, gross_tension_flange_area_agf, elastic_section_modulus_sx, phi_n, unit_system)`

- Rotura por flexion con agujeros en ala traccionada (AISC 360-22 F13.1):
  - `Yf = 1.0` si `Fy/Fu <= 0.8`; `Yf = 1.1` en otro caso.
  - Si `Fu*Afn >= Yf*Fy*Agf`, el limite de rotura por traccion del ala no aplica.
  - Si `Fu*Afn < Yf*Fy*Agf`, `Mn = (Fu*Afn/Agf)*Sx`.
  - `phi*Mn = phi_n*Mn`.

`compute_rectangular_bar_ltb_strength_f112(material_fy, modulus_e, unbraced_length_lb, bar_depth_d, bar_thickness_t, elastic_section_modulus_sx, plastic_moment_mp, cb_factor, phi_n, unit_system)`

- Pandeo lateral-torsional (AISC 360-22 F11.2), casos (a), (b), (c) con limite por `Mp`.

`compute_rectangular_bar_net_flexural_rupture_strength_j55(material_fy, plate_thickness_tp, plate_height_h, hole_plus_allowance_d_prime, edge_e1, edge_e2, spacing_s, bolt_rows_n, phi_n, unit_system)`

- Rotura por flexion neta para barra rectangular perforada (AISC 360-22 J5.5):
  - `h = e1 + (n-1)*s + e2`
  - `Znet = tp*h^2/4 - d'*tp*sum(|e1 + i*s - h/2|)`
  - `Rn = Fy*Znet`
  - `phi*Rn = phi_n*Rn`

## 9) Platinas de continuidad

`compute_plate_compression_buckling_strength(material_fy, plate_width_b1, plate_thickness_t, unbraced_length_lp, plate_count_n, unit_system, phi=0.9, k_factor=0.65)`

- Calcula la resistencia a compresion por pandeo de flexion usada en memoria `24.2.1`:
  - `r = 0.29*t`
  - `KL/r = K*Lp/r`
  - `Fe = pi^2*E/(KL/r)^2`
  - `Fcr = Fy`, `0.658^(Fy/Fe)*Fy` o `0.877*Fe` segun esbeltez
  - `phi*Rn = phi*Fcr*b1*t*n`
- Preserva la formula legacy validada para conexiones precalificadas y evita duplicarla dentro de reportes.

## 10) Interaccion de fuerzas combinadas en platina

`compute_plate_combined_force_interaction(dcr_plt_m1_web, dcr_plt_v3_web, dcr_plt_v2_web, dcr_plt_p3_minus_web)`

- Calcula dos casos de interaccion para la platina de alma en `splice`:
  - `DCR_case_1 = DCR_plt_m1_web + (DCR_plt_v3_web)^2 + (DCR_plt_v2_web)^4`
  - `DCR_case_2 = DCR_plt_m1_web + (DCR_plt_p3(-)_web)^2 + (DCR_plt_v2_web)^4`
- Devuelve el valor gobernante:
  - `DCR_plt_Fcomb_web = max(DCR_case_1, DCR_case_2)`
- Incluye caso controlante y verificacion de cumplimiento (`<= 1.0`).

## 11) Interaccion de fuerzas combinadas en miembro (H1)

`compute_member_combined_interaction_h11(pr_over_pc, mrx_over_mcx, mry_over_mcy=0.0)`

- Calcula interaccion axial + flexion para miembros simetricos (AISC 360-22 H1):
  - Si `Pr/Pc >= 0.2` usa H1-1a:
    - `DCR = Pr/Pc + (8/9)*(Mrx/Mcx + Mry/Mcy)`
  - Si `Pr/Pc < 0.2` usa H1-1b:
    - `DCR = Pr/(2*Pc) + (Mrx/Mcx + Mry/Mcy)`
- Devuelve:
  - `dcr`, `equation_used` (`H1-1a` o `H1-1b`), y `passes` (`<= 1.0`).

## 12) Inventario canonico (exportado en `engineering/common`)

Listado sincronizado con `src/steel_connections/codes/engineering/common/__init__.py`:

- `build_bolt_group_geometry`
- `build_in_plane_load`
- `build_in_plane_load_from_explicit_eccentricity`
- `build_mirrored_half_flange_bolt_pattern`
- `build_rectangular_bolt_pattern`
- `compute_bolt_tension_rupture_capacity_per_bolt`
- `compute_bolt_shear_rupture_capacity_per_bolt`
- `compute_bolt_hole_tearout_strength_j36`
- `compute_bolt_hole_bearing_strength_j36`
- `compute_element_shear_yielding_strength_j42a`
- `compute_element_shear_rupture_strength_j43`
- `compute_block_shear_strength_j45`
- `compute_element_tension_rupture_strength_j41b`
- `compute_element_tension_yielding_strength_j41a`
- `compute_whitmore_section_area`
- `compute_half_beam_wt_centroid_distance_from_flange_edge`
- `compute_rectangular_bar_flexural_yielding_strength_f111`
- `compute_member_flexural_rupture_with_tension_flange_holes_f131`
- `compute_rectangular_bar_ltb_strength_f112`
- `compute_rectangular_bar_net_flexural_rupture_strength_j55`
- `compute_plate_compression_buckling_strength`
- `compute_plate_combined_force_interaction`
- `compute_member_combined_interaction_h11`
- `compute_bolt_hole_dimensions_j33`
- `compute_minimum_bolt_spacing_j33`
- `compute_minimum_edge_distance_standard_hole_j34`
- `compute_standard_hole_diameter_j33`
- `compute_spacing_requirements_j33`
- `compute_entering_tightening_clearance_table_7_15`
- `compute_max_spacing_and_edge_distance_limits_j36`
- `compute_maximum_bolt_spacing_j36`
- `compute_limites_precalificacion_conexion_tipo_ep`
- `compute_dcr_ratio`
- `solve_bolt_group_method`
- `solve_elastic_superposition`
- `solve_elastic_center_of_rotation`
- `solve_instant_center_of_rotation`

## Nota de uso

- Si una regla nueva requiere calculos repetibles, debe consumir estas funciones DRY compartidas.
- No duplicar formulas en reglas de dominio cuando exista funcion equivalente en `engineering/common`.
