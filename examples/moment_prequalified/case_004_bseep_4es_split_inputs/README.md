# Inputs Segmentados - Case 004 BSEEP 4ES

Esta carpeta separa la entrada en 3 archivos:

1. `case_004_beam_right_only.json`
2. `case_004_beam_left_only.json`
3. `case_004_column_and_common.json`

Notas:
- `soldaduras.weld_4` se define por lado en los archivos de viga.
- `soldaduras.weld_4` corresponde a la soldadura #4 entre ala de viga y platina extremo.
- La soldadura de platina de continuidad en `case_004_column_and_common.json` se define como `soldaduras.weld_5`.

Uso directo (sin ensamblar):

```powershell
.\.venv\Scripts\python.exe -m src.steel_connections.run examples\moment_prequalified\case_004_bseep_4es_split_inputs
```
