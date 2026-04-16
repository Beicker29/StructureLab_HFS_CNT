# Inputs Segmentados - Case 003 BSEEP 8ES

Esta carpeta separa la entrada en 3 archivos:

1. `case_003_beam_right_only.json`
2. `case_003_beam_left_only.json`
3. `case_003_column_and_common.json`

Objetivo:
- Cargar por separado informacion de viga derecha, viga izquierda y columna/comunes.
- Luego ensamblar el caso completo con `assemble_case_003.py`.

## Regla de geometria segmentada

- `case_003_beam_right_only.json` y `case_003_beam_left_only.json` deben incluir la misma geometria compartida:
  - `end_plate`
  - `continuity_plate`
  - `stiffener`
  - `bolts`
  - `welds.weld_1`, `welds.weld_2`, `welds.weld_3`
- En `case_003_column_and_common.json` se deja solo:
  - `geometry.column.column_end_distance_to_beam_flange`
  - `geometry.welds.weld_4`
  - datos generales del caso (`project_id`, `materials`, `sections`, etc.).
- Si hay diferencias entre la geometria de viga derecha e izquierda, el ensamblador falla intencionalmente.

## Ensamblar caso completo

Desde la raiz del repo:

```powershell
.\.venv\Scripts\python.exe examples\moment_prequalified\case_003_bseep_8es_split_inputs\assemble_case_003.py
```

Salida:
- Sobrescribe `examples/moment_prequalified/case_003_bseep_8es.json`
