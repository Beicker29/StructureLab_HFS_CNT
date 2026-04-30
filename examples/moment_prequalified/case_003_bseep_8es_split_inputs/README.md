# Inputs Segmentados - Case 003 BSEEP 8ES

Esta carpeta separa la entrada en 3 archivos:

1. `case_003_beam_right_only.json`
2. `case_003_beam_left_only.json`
3. `case_003_column_and_common.json`

Objetivo:
- Cargar por separado informacion de viga derecha, viga izquierda y columna/comunes.
- El motor consume directamente estos 3 archivos (no se requiere archivo ensamblado intermedio).

## Formato reingenierizado (nomenclatura actual)

- Viga derecha/izquierda usan bloques:
  - `viga`
  - `placa_extremo`
  - `rigidizador`
  - `pernos`
  - `soldaduras`
  - `loads`
- Columna/comunes usa bloques:
  - `columna`
  - `platina_continuidad`
  - `loads`
  - `factores_diseno`
  - en `columna` agrega `consideracion_deformacion_inelastica_zona_panel` para WPZS (AISC 360-22w J10.6): `false` usa J10-9/J10-10 y `true` usa J10-11/J10-12.

## Reglas de consistencia

- La geometria compartida debe coincidir en viga derecha e izquierda:
  - `placa_extremo`
  - `rigidizador`
  - `pernos`
  - `soldaduras.weld_1`, `soldaduras.weld_2`, `soldaduras.weld_3`, `soldaduras.weld_4`
- `platina_continuidad` ahora se ingresa en `case_003_column_and_common.json`.
- `soldaduras.weld_4` se ingresa por lado en los archivos de viga:
  - soldadura #4 = ala de viga con platina extremo
  - incluye `tipo_w4_<lado>`, `Fexx_w4_<lado>`, `t_w4_<lado>`, `nl_w4_<lado>`, `kds_w4_<lado>`, `t_w4.1_<lado>`
- En `case_003_column_and_common.json`, la soldadura de platina de continuidad se ingresa como:
  - `soldaduras.weld_5` (soldadura #5 = platina de continuidad con aleta de columna)
  - campos: `tipo_w5`, `Fexx_w5` (y opcionalmente `t_w5`, `nl_w5`).
- `beam_shape` (desde `viga.perfil`) debe coincidir en derecha e izquierda.
- En columna/comunes, `materiales` mantiene:
  - `profile_steel_type`
  - `weld_fexx`
  - `elastic_modulus`
- Se usa nomenclatura con sufijo de lado:
  - derecha: `_vgder`
  - izquierda: `_vgizq`
- Ejemplos en `viga`:
  - `perfil_vgder` / `perfil_vgizq`
  - `tipo_acero_perfil_vgder` / `tipo_acero_perfil_vgizq`
  - `demanda_ductilidad_vgder` / `demanda_ductilidad_vgizq`
  - `E_vgder` / `E_vgizq`
  - `Llb_vgder` / `Llb_vgizq`
  - `Lnc_vgder` / `Lnc_vgizq`
- Ejemplos en `loads` de vigas:
  - `Pu_vgder` / `Pu_vgizq`
  - `Vg_vgder` / `Vg_vgizq`
  - `Vu2_vgder` / `Vu2_vgizq`
  - `Mu3_vgder` / `Mu3_vgizq`
- Ejemplos en `factores_diseno` (columna/common):
  - `phi_ductil` (se mapea a `phi_d`)
  - `phi_no_ductil` (se mapea a `phi_n`)
  - `phi_fragil` (se mapea a `phi_f`)
  - `lados_conexion`
  - `demanda_ductilidad_col`
  - `ratio_McMb_min`
  - `ratio_McMb`

## Ejecutar directamente (sin ensamblar)

Desde la raiz del repo:

```powershell
.\.venv\Scripts\python.exe -m src.steel_connections.run examples\moment_prequalified\case_003_bseep_8es_split_inputs
```
