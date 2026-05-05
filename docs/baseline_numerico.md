# Fase 0 - Baseline numerico

## Metadatos

- Fecha de generacion: 2026-05-04T15:46:36.9934729-05:00
- Commit: b900c9b80e503b70851e536330c37068c671a599
- Rama registrada en `.git/HEAD`: refs/heads/main
- Paquete: steel-connections-engine 0.1.0
- Python: 3.12.10
- Sistema operativo: Microsoft Windows NT 10.0.26100.0

Catalogos usados:

| Archivo | SHA256 |
|---|---|
| data/sections.xlsx | 3B7077D03D22B89CF5518C532F2E47C6E5365833918A0C4517D5DA5F33F15329 |
| data/materials.xlsx | 3615FB9D7BA3A339BA587BAD294BCDA2432CA44E233E1683B623A41C3934221D |

## Pytest completo

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Resultado:

- Tests recolectados: 128
- Tests que pasan: 128
- Tests que fallan: 0
- Estado posterior a saneamiento controlado: suite verde, sin cambios intencionales en golden approved

## Comandos de metadatos

```powershell
.\.venv\Scripts\python.exe --version
Get-Content pyproject.toml
Get-Content .git\HEAD
Get-Content .git\refs\heads\main
Get-FileHash data\sections.xlsx -Algorithm SHA256
Get-FileHash data\materials.xlsx -Algorithm SHA256
[System.Environment]::OSVersion.VersionString
Get-Date -Format o
```

## Comandos de generacion de baseline

Los comandos aprobados se ejecutaron contra carpeta temporal para los casos `approved` originales. Los casos `observed_baseline` se regeneraron directamente en `tests/golden/observed_baseline` despues de corregir la normalizacion legacy de doubler plate desactivado.

```powershell
.\.venv\Scripts\python.exe -m src.steel_connections.run examples/moment_prequalified/case_003_bseep_8es_split_inputs .tmp_phase0_baseline\approved
.\.venv\Scripts\python.exe -m src.steel_connections.run "examples/Fully Restrained Moment/case_001_bbmb_splice.json" .tmp_phase0_baseline\approved
.\.venv\Scripts\python.exe -m src.steel_connections.run examples/moment_prequalified/case_002_bueep_4e_split_inputs tests\golden\observed_baseline
.\.venv\Scripts\python.exe -m src.steel_connections.run examples/moment_prequalified/case_004_bseep_4es_split_inputs tests\golden\observed_baseline
```

## Casos evaluados

| Caso | Input | Clasificacion | Justificacion | Estado global | Checks | Peor DCR | Golden files |
|---|---|---|---|---:|---:|---:|---|
| case_003_bseep_8es_split_inputs | examples/moment_prequalified/case_003_bseep_8es_split_inputs | approved | Validado por ingenieria segun instruccion explicita del usuario | PASS | 34 | 1.0 | tests/golden/approved/case_003_bseep_8es_split_inputs |
| case_001_bbmb_splice | examples/Fully Restrained Moment/case_001_bbmb_splice.json | approved | Validado por ingenieria segun instruccion explicita del usuario | FAIL | 2 | 0.15996492559686498 | tests/golden/approved/case_001_bbmb_splice |
| case_002_bueep_4e_split_inputs | examples/moment_prequalified/case_002_bueep_4e_split_inputs | observed_baseline | Comportamiento actual regenerado despues de corregir normalizacion legacy de doubler plate desactivado; no approved | ERROR | 30 | 1.5379468690231437 | tests/golden/observed_baseline/case_002_bueep_4e_split_inputs |
| case_004_bseep_4es_split_inputs | examples/moment_prequalified/case_004_bseep_4es_split_inputs | observed_baseline | Comportamiento actual regenerado despues de corregir normalizacion legacy de doubler plate desactivado; no approved | ERROR | 34 | 1.9936507972639428 | tests/golden/observed_baseline/case_004_bseep_4es_split_inputs |

La carpeta `suspicious` queda reservada para casos con ejecucion incompleta, inconsistencias o dudas tecnicas futuras. En esta actualizacion no contiene casos activos.

## DCRs criticos y resultados principales

### Approved: case_003_bseep_8es_split_inputs

- Estado global: PASS
- Checks: 34
- Peor DCR reportado: 1.0
- Step 2 Mpr: demanda 1143433.5 kN-mm, capacidad 1143433.5 kN-mm, DCR 1.0
- Step 3 Sh: demanda 385.4 mm, capacidad 385.4 mm, DCR 1.0
- Step 4 Vh: demanda 402.0256 kN, capacidad 402.0256 kN, DCR 1.0
- Step 5 Mf: demanda 1298374.16624 kN-mm, capacidad 1298374.16624 kN-mm, DCR 1.0
- WPZS columna: demanda 3793.1507977729825 kN, capacidad 3798.4500000000003 kN, DCR 0.9986049040458561
- Bolt tension izquierda: demanda 312.9517369456228 kN, capacidad 355.7086503264434 kN, DCR 0.8797979376054493
- Bolt shear izquierda: demanda 50.2532 kN, capacidad 214.3372636582415 kN, DCR 0.23445853111257495
- End plate flexural izquierda: demanda 1298374.16624 kN-mm, capacidad 1505185.0859887889 kN-mm, DCR 0.8626010039071506
- Beam shear yielding por lado: demanda 402.0256 kN, capacidad 1209.3768 kN, DCR 0.3324237739635819
- No hay errores registrados en `detailed.json`.

### Approved: case_001_bbmb_splice

- Estado global: FAIL
- Checks: 2
- Peor DCR reportado: 0.15996492559686498
- Step 1 detailing viga: FAIL, sin DCR numerico.
- Step 2 pernos metodo ICR/Elastic: demanda 258.819045074625 kN, capacidad 1617.9737158562302 kN, DCR 0.15996492559686498
- No hay errores registrados en `detailed.json`.
- El estado FAIL forma parte del baseline aprobado por instruccion explicita del usuario.

### Observed baseline: case_002_bueep_4e_split_inputs

- Estado global: ERROR
- Checks: 30
- Peor DCR reportado: 1.5379468690231437
- Step 2 Mpr: demanda 1431473.9999999998 kN-mm, capacidad 1431473.9999999998 kN-mm, DCR 1.0
- Step 3 Sh: demanda 303.5 mm, capacidad 303.5 mm, DCR 1.0
- Step 4 Vh: demanda 514.1257007874015 kN, capacidad 514.1257007874015 kN, DCR 1.0
- Step 5 Mf: demanda 1587511.1501889762 kN-mm, capacidad 1587511.1501889762 kN-mm, DCR 1.0
- WPZS columna: demanda 3116.1655028279874 kN, capacidad 2376.5256 kN, DCR 1.3112274081238542
- End plate flexural por lado: demanda 1587511.1501889762 kN-mm, capacidad 1032227.5640102667 kN-mm, DCR 1.5379468690231437
- Bolt tension por lado: demanda 673.0164279247821 kN, capacidad 450.193760569405 kN, DCR 1.494948368616995
- Estado ERROR por 2 checks NOT_IMPLEMENTED. No hay error de ejecucion WPZS/doubler plate.
- No usar como criterio de aprobacion tecnica.

### Observed baseline: case_004_bseep_4es_split_inputs

- Estado global: ERROR
- Checks: 34
- Peor DCR reportado: 1.9936507972639428
- Step 2 Mpr: demanda 1431473.9999999998 kN-mm, capacidad 1431473.9999999998 kN-mm, DCR 1.0
- Step 3 Sh: demanda 225.4 mm, capacidad 225.4 mm, DCR 1.0
- Step 4 Vh: demanda 514.1257007874015 kN, capacidad 514.1257007874015 kN, DCR 1.0
- Step 5 Mf: demanda 1547357.93295748 kN-mm, capacidad 1547357.93295748 kN-mm, DCR 1.0
- Bolt tension derecha: demanda 709.1588343169949 kN, capacidad 355.7086503264434 kN, DCR 1.9936507972639428
- Bolt tension izquierda: demanda 655.9936972008987 kN, capacidad 355.7086503264434 kN, DCR 1.8441882045850606
- End plate flexural derecha: demanda 1261451.7344830707 kN-mm, capacidad 1090537.9148928141 kN-mm, DCR 1.1567243259094344
- Estado ERROR por 2 checks NOT_IMPLEMENTED. No hay error de ejecucion WPZS/doubler plate.
- No usar como criterio de aprobacion tecnica.

## Archivos generados

Approved:

- tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json
- tests/golden/approved/case_003_bseep_8es_split_inputs/memory.md
- tests/golden/approved/case_003_bseep_8es_split_inputs/metadata.json
- tests/golden/approved/case_001_bbmb_splice/detailed.json
- tests/golden/approved/case_001_bbmb_splice/memory.md
- tests/golden/approved/case_001_bbmb_splice/metadata.json

Observed baseline:

- tests/golden/observed_baseline/case_002_bueep_4e_split_inputs/detailed.json
- tests/golden/observed_baseline/case_002_bueep_4e_split_inputs/memory.md
- tests/golden/observed_baseline/case_002_bueep_4e_split_inputs/metadata.json
- tests/golden/observed_baseline/case_004_bseep_4es_split_inputs/detailed.json
- tests/golden/observed_baseline/case_004_bseep_4es_split_inputs/memory.md
- tests/golden/observed_baseline/case_004_bseep_4es_split_inputs/metadata.json

Suspicious:

- Sin casos activos. La carpeta se conserva con `.gitkeep`.

Helper:

- tests/helpers/golden_compare.py

## Limitaciones del baseline

- Este baseline preserva comportamiento numerico actual; no es una nueva validacion normativa.
- Solo dos casos son `approved` por instruccion explicita del usuario.
- Los casos `observed_baseline` documentan comportamiento actual, pero no aprueban tecnicamente resultados de ingenieria.
- La suite completa de pytest esta verde despues del saneamiento controlado de tests obsoletos, BOM y normalizacion legacy de doubler plate desactivado.
- No se corrigieron diferencias textuales de reporte fuera de los cambios ya aprobados en fases posteriores.
- En esta regeneracion no se modificaron `markdown_writer.py`, `chapter_06_end_plate.py`, formulas ni golden approved.

## Uso previsto en fases futuras

Todo refactor posterior debe:

1. Regenerar salidas en una carpeta temporal.
2. Comparar `detailed.json` contra los golden approved con `tests/helpers/golden_compare.py`.
3. Comparar `memory.md` como texto, documentando cualquier diferencia textual.
4. Explicar y aprobar explicitamente cualquier diferencia numerica antes de continuar.
