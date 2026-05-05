# Comparacion contra golden approved

La comparacion golden protege los resultados validados por ingenieria y el
formato publico de los reportes.

## Casos approved

Los unicos casos approved actuales son:

- `case_003_bseep_8es_split_inputs`
- `case_001_bbmb_splice`

Cada caso approved compara:

- `detailed.json`: equivalencia numerica con tolerancias explicitas.
- `memory.md`: equivalencia textual exacta, normalizando solo saltos de linea.

## Puerta de calidad recomendada

Ejecutar:

```powershell
.\.venv\Scripts\python.exe scripts\quality_gate.py
```

La puerta hace:

1. `pytest -q`
2. genera los dos casos approved en `.tmp_quality_gate/approved/`
3. compara `detailed.json` contra `tests/golden/approved/`
4. compara `memory.md` contra `tests/golden/approved/`

Si hay diferencia numerica o textual, el comando falla.

## Comparacion manual

Pytest completo:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Generar caso moment prequalified approved:

```powershell
.\.venv\Scripts\python.exe -m src.steel_connections.run examples/moment_prequalified/case_003_bseep_8es_split_inputs .tmp_quality_gate/approved
```

Generar caso BBMB splice approved:

```powershell
.\.venv\Scripts\python.exe -m src.steel_connections.run "examples/Fully Restrained Moment/case_001_bbmb_splice.json" .tmp_quality_gate/approved
```

Comparacion programatica:

```powershell
.\.venv\Scripts\python.exe -c "from tests.helpers.golden_compare import compare_detailed_json_files, compare_report_files; compare_detailed_json_files('.tmp_quality_gate/approved/moment_prequalified/case_003_bseep_8es_split_inputs/detailed.json', 'tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json'); compare_report_files('.tmp_quality_gate/approved/moment_prequalified/case_003_bseep_8es_split_inputs/memory.md', 'tests/golden/approved/case_003_bseep_8es_split_inputs/memory.md'); compare_detailed_json_files('.tmp_quality_gate/approved/Fully Restrained Moment/case_001_bbmb_splice/detailed.json', 'tests/golden/approved/case_001_bbmb_splice/detailed.json'); compare_report_files('.tmp_quality_gate/approved/Fully Restrained Moment/case_001_bbmb_splice/memory.md', 'tests/golden/approved/case_001_bbmb_splice/memory.md'); print('golden approved OK')"
```

## Tolerancias

Las tolerancias estan en:

```text
tests/helpers/golden_compare.py
```

Valores iniciales:

- fuerzas: relativa `1e-6`
- momentos: relativa `1e-6`
- longitudes/espesores: absoluta `1e-6 mm`
- esfuerzos: relativa `1e-6`
- DCR/ratios: absoluta `1e-6`
- texto: no ocultar cambios de contenido tecnico

## Regla de uso

No actualizar golden approved para hacer pasar la prueba. Si aparece una
diferencia, debe documentarse la causa tecnica y aprobarse explicitamente antes
de cambiar el baseline.
