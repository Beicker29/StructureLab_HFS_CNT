# Variables de Entrada para `examples/moment_prequalified/*.json`

Este documento define el significado de cada variable que debes ingresar en los casos JSON de conexiones precalificadas de momento (Chapter 6).

## Estructura general

El archivo legacy monolitico usa estos bloques:

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

Nota:
- para los casos actuales `bueep_4e`, `bseep_4es` y `bseep_8es` trabajamos preferentemente con `inputs split` por viga derecha, viga izquierda y columna/comunes.
- la nomenclatura preferida es `*_vgder`, `*_vgizq` y `*_col`.
- varios nombres listados abajo existen solo por compatibilidad legacy; evita usarlos en inputs nuevos.

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
- `geometry.end_plate.pb`: `pb`, paso vertical entre líneas de pernos. Solo aplica a `bseep_8es`.
- `geometry.end_plate.pfo`: `pso` (linea de pernos 2), distancia libre entre la placa de continuidad superior y el eje de la linea de pernos inmediatamente arriba de la aleta superior de la viga.
- `geometry.end_plate.pfi`: `pfi`, distancia libre base para la zona de la linea de pernos 3.
- `hp` (altura de platina) se calcula como `hp = d + 2*pfo + 2*de`, donde `d` proviene del catalogo de la viga.
- `geometry.continuity_plate.continuity_plate_thickness`: `tcp`, espesor de la placa de continuidad.
- `geometry.doubler_plate.extended_dp_col` (en split: `platina_enchape_alma.extended_dp_col`):
  - `true`: **Extended doubler plates**.
  - `false`: **Doubler plates placed between continuity plates**.
- `geometry.welds.weld_4`: soldadura #4 (ala de viga con platina extremo).
- `geometry.welds.weld_4.weld_type`: tipo de soldadura de ala de viga con platina extremo (`CJP` o filete segun el caso).
- `geometry.welds.weld_4.backing_thickness`: en inputs split se expresa como `t_w4.1_<lado>` o `t_w4_1_<lado>`.
- el espesor total de soldadura #4 se calcula como:
  - ductilidad baja: `2w = nl_w4 * t_w4.1`
  - ductilidad moderada/alta: `2w = t_w4.1`
- `geometry.welds.weld_1`: soldadura #1 (rigidizador con end plate).
- `geometry.welds.weld_1.weld_type`: tipo (`CJP` o `fillet`).
- `geometry.welds.weld_1.length`: legacy. Ya no se ingresa; el motor calcula `l_w1` automaticamente.
- `geometry.welds.weld_1.size`: legacy monolitico. En inputs split se usa `w_w1_<lado>`.
- `geometry.welds.weld_1.nl`: legacy monolitico. En inputs split se usa `nl_w1_<lado>`.
- `geometry.welds.weld_2`: soldadura #2 (viga con rigidizador).
- `geometry.welds.weld_2.weld_type`: tipo (`CJP` o `fillet`; fallback al tipo de `weld_1`).
- `geometry.welds.weld_2.length`: legacy. Ya no se ingresa; el motor calcula `l_w2` automaticamente.
- `geometry.welds.weld_2.size`: legacy monolitico. En inputs split se usa `w_w2_<lado>`.
- `geometry.welds.weld_2.nl`: legacy monolitico. En inputs split se usa `nl_w2_<lado>`.
- `geometry.welds.weld_3`: soldadura #3 (alma de viga con end plate).
- `geometry.welds.weld_3.weld_type`: tipo (`CJP`, `double_sided_fillet`, `single_sided_fillet`).
- `geometry.welds.weld_3.thickness`: espesor `twe` (requerido si `weld_type` es `double_sided_fillet` o `single_sided_fillet`).
- `geometry.welds.weld_3.nl`: numero de lineas efectivas `n_l` para Paso 11 (usado en `phiPnww3`).
- En el chequeo de capacidad de soldadura #3 no se usa `Lwe` como input; se usa `hwef = pfi + pb + 150 mm`.
- `psi` (linea de pernos 3 efectiva) se calcula como `psi = pfi + tfb - tcp`, donde `tfb` viene del catalogo de la viga.
- `geometry.bolts.bolt_tightening_type`: tipo de apriete de pernos (`pretensioned` o `snug_tight`; tambien acepta `pretensionado` y `apriete_justo`).
- `geometry.bolts.clear_distance_end_plate`: `lc_ep`, distancia libre para bearing/tearout en placa extremo (distancia horizontal en direccion de carga desde borde del agujero al borde libre de la platina).
- `geometry.bolts.clear_distance_column_flange`: `lc_cf`, distancia libre para bearing/tearout en ala de columna (distancia horizontal desde borde del agujero al borde libre del ala de la columna).
- `columna.St_col`: distancia vertical desde el tope de las vigas hasta el tope de la columna; se usa en la verificacion geometrica de proyeccion minima de columna y en revisiones de resistencia del panel/columna.
- `columna.consideracion_deformacion_inelastica_zona_panel` (mapeado a `geometry.panel_zone_inelastic_deformation_considered`): condicion WPZS de AISC 360-22w J10.6.
  - `false`: usar paquete (a), ecuaciones J10-9 / J10-10.
  - `true`: usar paquete (b), ecuaciones J10-11 / J10-12.
- `dcf_col`: nombre legacy; ya no debe usarse en inputs nuevos.
- `geometry.stiffener.stiffener_thickness`: `ts` (solo conexiones `bseep_*`).
- `hst` ya no se ingresa como input: el motor lo deriva como `hst = pfo + de`.
- `Lst` ya no se ingresa como input: el motor lo deriva como `Lst = hst / tan(30 deg)`.
- `geometry.bolts.bolt_shape`: shape de perno (lookup geométrico en `sections.xlsx`, hoja `Perno`).
- `geometry.bolts.bolt_thread_condition`: condición de rosca para `Fnv`: `N` o `X`.

## 5) Cargas

- `loads.pu_viga_right`: alias legacy de `Pu_vgder`.
- `loads.pu_viga_left`: alias legacy de `Pu_vgizq`.
- `loads.pu_viga`: alias legacy; evitar en inputs nuevos.
- `loads.Vu2_vgder` / `loads.Vu2_vgizq`: cortante factorizado por lado cuando se quiera declarar como input explicito.
- `loads.Mu3_vgder` / `loads.Mu3_vgizq`: momento factorizado por lado cuando se quiera declarar como input explicito.
- `loads.pu_columna`: alias legacy de `Pu_col`.
- `loads.probable_moment_column_face`: alias legacy opcional; evitar en inputs nuevos.
- `loads.Beam_right_Vgravity` / `loads.Beam_left_Vgravity`: aliases legacy.
- `loads.beam_right_vgravity` / `loads.beam_left_vgravity`: nombres legacy del payload normalizado.
- en inputs split actuales se usan `Vg_vgder` y `Vg_vgizq`.
- `loads.beam_gravity_shear_between_hinges*`: aliases legacy para compatibilidad.
- `Vu` de viga normalmente se deriva automáticamente desde `Vhmax` del Paso 3, salvo que se declare explícitamente como `Vu2_<lado>`.
- `Mu` en cara de columna normalmente se deriva automáticamente, salvo que se declare explícitamente como `Mu3_<lado>`.
- `loads.required_web_weld_force`: ya no se acepta como input; se deriva internamente a partir de `Vu` de conexión (temporalmente con factor 0.4).
- `loads.panel_zone_demand`: ya no se acepta como input; se deriva internamente a partir de `Vu` de conexión (temporalmente con factor 0.5).

## 6) Factores de diseño

- `design_factors.phi_d`: factor de resistencia para chequeos tipo `phi_d`.
- `design_factors.phi_n`: factor de resistencia para chequeos tipo `phi_n`.
- `design_factors.phi_f`: factor de resistencia para chequeos tipo `phi_f` (fragil).
- `design_factors.member_ductility_demand_column`: demanda de ductilidad (`high`, `moderate` o `low`) y fuente unica para chequeos/cálculos de viga izquierda, viga derecha y columna.
- `design_factors.column_beam_moment_ratio_minimum`: relación mínima columna-viga.
- `design_factors.column_beam_moment_ratio`: relación columna-viga del caso.

Nota de compactacion:
- `Ca` ya no se ingresa como input.
- El motor calcula `Ca = Pu / (Ry * Ag * Fy)` para viga y columna usando:
  - `Pu` desde `loads.pu_viga_right` (y `loads.pu_viga_left` cuando aplica) / `loads.pu_columna`
  - `Ry` derivado automáticamente desde `data/materials.xlsx` (hoja `HRS`) según `materials.profile_steel_type`
  - `Ag` desde `data/sections.xlsx`
  - `Fy` desde `data/materials.xlsx` (hoja `HRS`)

## 7) Parametros derivados`r`n`r`n- El bloque `procedure` ya no se usa como input.`r`n- `Ze` se deriva de `Zx` del catalogo (`sections.xlsx`) segun `sections.beam_shape`.`r`n- `Lh` se deriva de `geometry.beam_clear_span_length`.`r`n- `h1..h4` se derivan de la geometria del end plate (`pfo`, `pfi`, `pb`, `tcp`, `d`, `tf`).`r`n- `beam_available_shear_strength` se calcula internamente en el motor.`r`n`r`n## Reglas importantes

- No usar defaults ocultos: si falta un dato aplicable, el motor falla con error estructurado.
- `Fy/Fu` de perfiles/platinas y `Fnt/Fnv`/diámetro de perno se derivan de catálogos, no se ingresan manualmente.
- `kc` para web local yielding se obtiene del catalogo (`kdes` de `sections.xlsx` para la columna); no debe definirse manualmente en el JSON.
- Todas las magnitudes físicas se ingresan como:

```json
{ "value": 0.0, "unit": "mm" }
```




