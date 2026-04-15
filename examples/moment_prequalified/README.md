# Variables de Entrada para `examples/moment_prequalified/*.json`

Este documento define el significado de cada variable que debes ingresar en los casos JSON de conexiones precalificadas de momento (Chapter 6).

## Estructura general

El archivo debe tener estos bloques:

- `project_id`
- `case_id`
- `design_code_context`
- `units_system`
- `connection_family`
- `connection_type`
- `load_state`
- `sections`
- `materials`
- `geometry`
- `loads`
- `design_factors`
- `procedure`

## 1) Identificación y contexto

- `project_id`: identificador del proyecto.
- `case_id`: identificador único del caso.
- `design_code_context.primary_document`: norma principal del caso (ej. `AISC 358-22`).
- `design_code_context.supporting_documents`: lista de documentos de soporte.
- `units_system`: sistema de unidades (`US` o `SI`).
- `connection_family`: debe ser `moment_prequalified`.
- `connection_type`: tipo de conexión (`bueep_4e`, `bseep_4es`, `bseep_8es`).
- `load_state`: estado de carga (actualmente `strength`).

## 2) Secciones

- `sections.beam_shape`: perfil de viga (lookup en `data/sections.xlsx`).
- `sections.column_shape`: perfil de columna (lookup en `data/sections.xlsx`).

## 3) Materiales

- `materials.profile_steel_type`: tipo de acero para perfiles (lookup en `data/materials.xlsx`, hoja `HRS`).
- `materials.plate_steel_type`: tipo de acero para platinas (lookup en `data/materials.xlsx`, hoja `Platinas`).
- `materials.bolt_fabrication_standard`: norma de fabricación del perno (lookup en `materials.xlsx`, hoja `Pernos`).
- `materials.weld_fexx`: resistencia del electrodo para soldadura (`Fexx`).
- `materials.elastic_modulus`: módulo elástico `E`.
- `bolt_shape` y `bolt_thread_condition` van en `geometry.bolts` (no en `materials`).

## 4) Geometría

- La geometría se agrupa en:
  - `geometry.beam`
  - `geometry.column`
  - `geometry.end_plate`
  - `geometry.continuity_plate`
  - `geometry.stiffener`
  - `geometry.bolts`
  - `geometry.welds`
- `geometry.end_plate.end_plate_width`: `bp`, ancho de placa extremo. Limite de precalificacion activo: `bp >= bf + 25 mm` (o `bf + 1 in` en US).
- `geometry.end_plate.end_plate_thickness`: `tp`, espesor de placa extremo.
- `geometry.beam.clear_span_length`: luz libre de la viga (`L_clear`).
- `geometry.beam.shear_connector_free_length_from_column_face`: longitud sin conectores de cortante desde la cara de columna (`Lsc`), con chequeo `Lsc >= 1.5d`.
- `geometry.column.slab_connection_condition`: condicion union columna-losa (`isolated` o `not_isolated`; tambien acepta `aislada` o `no_aislada`).
- `geometry.bolts.bolt_gage`: `g`, separación transversal entre líneas de pernos.
- `geometry.end_plate.de`: `de`, distancia vertical de borde superior a primera línea de pernos.
- `geometry.end_plate.pb`: `pb`, paso vertical entre líneas de pernos.
- `geometry.end_plate.pfo`: `pso` (linea de pernos 2), distancia libre entre la placa de continuidad superior y el eje de la linea de pernos inmediatamente arriba de la aleta superior de la viga.
- `geometry.end_plate.pfi`: `pfi`, distancia libre base para la zona de la linea de pernos 3.
- `geometry.continuity_plate.continuity_plate_thickness`: `tcp`, espesor de la placa de continuidad.
- `geometry.welds.end_plate_beam_web_weld_type`: tipo de soldadura entre end plate y alma de viga (`CJP`, `double_sided_fillet`, `single_sided_fillet`).
- `geometry.welds.end_plate_beam_web_weld_length_lwe`: longitud de soldadura `Lwe`.
- `geometry.welds.end_plate_beam_web_weld_thickness_twe`: espesor de soldadura `twe` (requerido si el tipo es `double_sided_fillet` o `single_sided_fillet`).
- `psi` (linea de pernos 3 efectiva) se calcula como `psi = pfi + tfb - tcp`, donde `tfb` viene del catalogo de la viga.
- `geometry.bolts.bolt_tightening_type`: tipo de apriete de pernos (`pretensioned` o `snug_tight`; tambien acepta `pretensionado` y `apriete_justo`).
- `geometry.bolts.clear_distance_end_plate`: `lc_ep`, distancia libre para bearing/tearout en placa extremo (distancia horizontal en direccion de carga desde borde del agujero al borde libre de la platina).
- `geometry.bolts.clear_distance_column_flange`: `lc_cf`, distancia libre para bearing/tearout en ala de columna (distancia horizontal desde borde del agujero al borde libre del ala de la columna).
- `geometry.column.column_end_distance_to_beam_flange`: `a_col_end`, distancia vertical desde la aleta de la viga hasta el extremo de la columna para evaluar web crippling.
- `geometry.welds.weld_leg_size_w`: tamaño de filete de soldadura `w`.
- `geometry.stiffener.stiffener_thickness`: `ts` (solo conexiones `bseep_*`).
- `hst` ya no se ingresa como input: el motor lo deriva como `hst = pfo + de`.
- `Lst` ya no se ingresa como input: el motor lo deriva como `Lst = hst / tan(30 deg)`.
- `geometry.bolts.bolt_shape`: shape de perno (lookup geométrico en `sections.xlsx`, hoja `Perno`).
- `geometry.bolts.bolt_thread_condition`: condición de rosca para `Fnv`: `N` o `X`.

## 5) Cargas

- `loads.pu_viga`: carga axial `Pu` en la viga (se usa para calcular `Ca` de viga).
- `loads.pu_columna`: carga axial `Pu` en la columna (se usa para calcular `Ca` de columna).
- `loads.probable_moment_column_face`: `Mf`, momento probable en cara de columna.
- `loads.beam_gravity_shear_between_hinges`: cortante de gravedad entre rótulas plásticas.
- `loads.required_connection_shear`: `Vu` requerida en la conexión.
- `loads.required_beam_shear`: `Vu` requerida de la viga.
- `loads.required_web_weld_force`: fuerza requerida para soldadura de alma.
- `loads.panel_zone_demand`: demanda en panel zone.

## 6) Factores de diseño

- `design_factors.phi_d`: factor de resistencia para chequeos tipo `phi_d`.
- `design_factors.phi_n`: factor de resistencia para chequeos tipo `phi_n`.
- `design_factors.ry`: factor `Ry` del acero.
- `design_factors.member_ductility_demand_beam`: demanda de ductilidad para compacidad de viga (`high` o `moderate`).
- `design_factors.member_ductility_demand_column`: demanda de ductilidad para compacidad de columna (`high` o `moderate`).
- `design_factors.column_beam_moment_ratio_minimum`: relación mínima columna-viga.

Nota de compactacion:
- `Ca` ya no se ingresa como input.
- El motor calcula `Ca = Pu / (Ry * Ag * Fy)` para viga y columna usando:
  - `Pu` desde `loads.pu_viga` / `loads.pu_columna`
  - `Ry` desde `design_factors.ry`
  - `Ag` desde `data/sections.xlsx`
  - `Fy` desde `data/materials.xlsx` (hoja `HRS`)

## 7) Parámetros de procedimiento (`procedure`)

- `procedure.beam_plastic_section_modulus_ze`: `Ze` de procedimiento (para BSEEP, Step 1 usa `Zx` de catálogo y deja trazabilidad).
- `procedure.beam_span_between_plastic_hinges_lh`: `Lh`.
- `procedure.yield_line_parameter_yp`: `Yp`.
- `procedure.column_yield_line_parameter_yc_unstiffened`: `Yc` para BUEEP.
- `procedure.column_yield_line_parameter_yc_stiffened`: `Yc` para BSEEP.
- `procedure.tension_bolt_line_distances`: distancias `h_i` de líneas de pernos a la línea de compresión.
- `procedure.beam_available_shear_strength`: capacidad disponible de cortante de viga.
- `procedure.flange_weld_available_strength`: capacidad disponible de soldadura en aleta.
- `procedure.web_weld_available_strength`: capacidad disponible de soldadura en alma.
- `procedure.continuity_plate_available_strength`: capacidad disponible de placa de continuidad.
- `procedure.panel_zone_capacity`: capacidad de panel zone.
- `procedure.column_beam_moment_ratio`: relación columna-viga del caso.

## Reglas importantes

- No usar defaults ocultos: si falta un dato aplicable, el motor falla con error estructurado.
- `Fy/Fu` de perfiles/platinas y `Fnt/Fnv`/diámetro de perno se derivan de catálogos, no se ingresan manualmente.
- `kc` para web local yielding se obtiene del catalogo (`kdes` de `sections.xlsx` para la columna); no debe definirse manualmente en el JSON.
- Todas las magnitudes físicas se ingresan como:

```json
{ "value": 0.0, "unit": "mm" }
```

