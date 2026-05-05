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

## Nota de uso

- Si una regla nueva requiere calculos repetibles, debe consumir estas funciones DRY compartidas.
- No duplicar formulas en reglas de dominio cuando exista funcion equivalente en `engineering/common`.
