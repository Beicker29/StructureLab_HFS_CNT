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
- `materials.bolt_description`: descripción/clasificación del perno (lookup en `materials.xlsx`, hoja `Pernos`).
- `materials.bolt_shape`: shape de perno (lookup geométrico en `sections.xlsx`, hoja `Perno`).
- `materials.bolt_thread_condition`: condición de rosca para `Fnv`: `N` o `X`.
- `materials.elastic_modulus`: módulo elástico `E`.

## 4) Geometría

- `geometry.end_plate_width`: `bp`, ancho de placa extremo. Limite de precalificacion activo: `bp >= bf + 25 mm` (o `bf + 1 in` en US).
- `geometry.end_plate_thickness`: `tp`, espesor de placa extremo.
- `geometry.bolt_gage`: `g`, separación transversal entre líneas de pernos.
- `geometry.de`: `de`, distancia vertical de borde superior a primera línea de pernos.
- `geometry.pb`: `pb`, paso vertical entre líneas de pernos.
- `geometry.pfo`: `pso` (linea de pernos 2), distancia libre entre la placa de continuidad superior y el eje de la linea de pernos inmediatamente arriba de la aleta superior de la viga.
- `geometry.pfi`: `pfi`, distancia libre base para la zona de la linea de pernos 3.
- `geometry.continuity_plate_thickness`: `tcp`, espesor de la placa de continuidad.
- `psi` (linea de pernos 3 efectiva) se calcula como `psi = pfi + tfb - tcp`, donde `tfb` viene del catalogo de la viga.
- `geometry.clear_distance_end_plate`: `lc_ep`, distancia libre para bearing/tearout en placa extremo (distancia horizontal en direccion de carga desde borde del agujero al borde libre de la platina).
- `geometry.clear_distance_column_flange`: `lc_cf`, distancia libre para bearing/tearout en ala de columna (distancia horizontal en  desde borde del agujero al borde libre del ala de la columna).
- `geometry.column_end_distance_to_beam_flange`: `a_col_end`, distancia vertical desde la aleta de la viga hasta el extremo de la columna para evaluar web crippling.
- `geometry.weld_leg_size_w`: tamaño de filete de soldadura `w`.
- `geometry.stiffener_height`: `hst` (solo conexiones `bseep_*`).
- `geometry.stiffener_length`: `lst` (solo conexiones `bseep_*`).
- `geometry.stiffener_thickness`: `ts` (solo conexiones `bseep_*`).

## 5) Cargas

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
- `design_factors.compactness_ca_beam`: `Ca` para límite `h/tw` de viga.
- `design_factors.compactness_ca_column`: `Ca` para límite `h/tw` de columna.
- `design_factors.column_beam_moment_ratio_minimum`: relación mínima columna-viga.

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
