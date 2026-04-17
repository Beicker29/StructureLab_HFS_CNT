# Inputs Segmentados - Case 003 BSEEP 8ES

Esta carpeta separa la entrada en 3 archivos:

1. `case_003_beam_right_only.json`
2. `case_003_beam_left_only.json`
3. `case_003_column_and_common.json`

Objetivo:
- Cargar por separado informacion de viga derecha, viga izquierda y columna/comunes.
- El motor consume directamente estos 3 archivos (no se requiere archivo ensamblado intermedio).

## Formato reingenierizado (referencia splice)

- Viga derecha/izquierda usan bloques tipo:
  - `viga`
  - `placa_extremo`
  - `rigidizador`
  - `pernos`
  - `soldaduras`
- Columna/comunes usa bloques tipo:
  - `columna`
  - `platina_continuidad`
  - `materiales`
  - `soldaduras` (solo `weld_4`)
  - `factores_diseno`

## Reglas de consistencia

- La geometria compartida debe coincidir en viga derecha e izquierda:
  - `placa_extremo`
  - `rigidizador`
  - `pernos`
  - `soldaduras.weld_1`, `soldaduras.weld_2`, `soldaduras.weld_3`
- `platina_continuidad` ahora se ingresa en `case_003_column_and_common.json`.
- `beam_shape` (desde `viga.perfil`) debe coincidir en derecha e izquierda.
- En columna/comunes, `materiales` mantiene:
  - `profile_steel_type`
  - `weld_fexx`
  - `elastic_modulus`
- `member_ductility_demand_beam` se ingresa en ambos archivos de viga dentro de `viga`.
- `member_ductility_demand_column` se mantiene en `case_003_column_and_common.json`.
- En `factores_diseno` de columna se usan:
  - `factor_reduccion_modo_no_ductil` (se mapea a `phi_n`)
  - `factor_reduccion_modo_ductil` (se mapea a `phi_d`)
- Los datos de material se ingresan por elemento en los archivos de viga:
  - `viga.tipo_acero_perfil` y `viga.elastic_modulus`
  - `placa_extremo.tipo_acero`
  - `rigidizador.tipo_acero`
  - `pernos.bolt_fabrication_standard` y `pernos.bolt_description`
  - `soldaduras.weld_fexx`

## Ejecutar directamente (sin ensamblar)

Desde la raiz del repo:

```powershell
.\.venv\Scripts\python.exe -m src.steel_connections.run examples\moment_prequalified\case_003_bseep_8es_split_inputs
```
