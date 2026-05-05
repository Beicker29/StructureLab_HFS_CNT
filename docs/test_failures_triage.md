# Fase 0 - Triage de tests fallidos

Fecha de ejecucion: 2026-05-04T15:46:36.9934729-05:00

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Resultado observado:

- Tests recolectados: 117
- Tests que pasan: 92
- Tests que fallan: 25
- Python: 3.12.10
- Paquete: steel-connections-engine 0.1.0
- Commit: b900c9b80e503b70851e536330c37068c671a599

Nota de Fase 0: un test fallido no se interpreta automaticamente como error del motor. Los resultados numericos actuales de los casos aprobados por ingenieria se conservan como baseline de referencia.

## Actualizacion posterior

Fecha de actualizacion: 2026-05-04T16:56:38.9630679-05:00

Despues del saneamiento autorizado de WPZS/doubler plate desactivado, fixtures obsoletos y lecturas con BOM, el comando `.\.venv\Scripts\python.exe -m pytest` recolecta 128 tests y pasan 128.

Los casos `case_002_bueep_4e_split_inputs` y `case_004_bseep_4es_split_inputs` dejaron de ser baselines `suspicious` por corte WPZS y fueron regenerados como `observed_baseline`. Siguen sin estar clasificados como `approved` porque no tienen validacion explicita de ingenieria.

La tabla siguiente queda como registro historico del triage inicial de Fase 0.

| Test | Archivo | Modulo afectado | Mensaje resumido | Categoria | Causa probable | Severidad | Bloquea Fase 1 | Accion recomendada | Observacion tecnica | Afecta resultados numericos validados |
|---|---|---|---|---|---|---|---|---|---|---|
| test_example_results_folder_and_memory_artifact | tests/integration/moment_prequalified/test_reporting_artifacts.py | reporting/markdown_writer.py | No aparece `## Paso 1 - Limites de precalificacion` en memory.md | diferencia textual de reporte | El formato actual de memoria cambio respecto a la expectativa antigua | baja | No | Inventariar dependencias de markdown_writer antes de Fase 2 | No corregir texto en Fase 0 | No |
| test_run_bueep_4e_case | tests/integration/moment_prequalified/test_run_chapter6_cases.py | domain/rules/aisc358/chapter_06_end_plate.py | Espera >=15 checks, obtiene 6 | error de ejecucion parcial | La corrida se corta en WPZS por `doubler_plate_thickness/count` | alta | No | Mantener como suspicious y revisar despues del baseline | No corregir WPZS en Fase 0 | No, caso no approved |
| test_run_bseep_8es_case | tests/integration/moment_prequalified/test_run_chapter6_cases.py | domain/rules/aisc358/chapter_06_end_plate.py | Espera >=30 checks, obtiene 6 | error de ejecucion parcial | Fixture unitario no incluye datos requeridos para pasar WPZS | alta | No | Mantener triage; no inferir que el baseline approved esta mal | Diferente del split input approved | No, no es el golden approved |
| test_run_bseep_4es_case | tests/integration/moment_prequalified/test_run_chapter6_cases.py | domain/rules/aisc358/chapter_06_end_plate.py | Espera >=30 checks, obtiene 6 | error de ejecucion parcial | La corrida se corta en WPZS por `doubler_plate_thickness/count` | alta | No | Clasificar caso 004 como suspicious | No corregir WPZS en Fase 0 | No, caso suspicious |
| test_run_si_bueep_4e_case | tests/integration/moment_prequalified/test_run_chapter6_si_cases.py | domain/engine + rules | Espera >=20 checks, obtiene 6 | error de ejecucion parcial | Split input SI llega hasta WPZS y corta por doubler plate | alta | No | Baseline suspicious para detectar cambios futuros | Ejecucion incompleta documentada | No, caso suspicious |
| test_run_si_bseep_4es_case | tests/integration/moment_prequalified/test_run_chapter6_si_cases.py | domain/engine + rules | Espera 0 checks, obtiene 6 | cambio esperado por evolucion reciente | El motor ahora evalua pasos iniciales antes del error | media | No | Actualizar expectativa solo cuando se apruebe correccion de tests | No corregir ahora | No, caso suspicious |
| test_run_si_bseep_8es_case | tests/integration/moment_prequalified/test_run_chapter6_si_cases.py | domain/engine + rules | Espera FAIL, obtiene PASS | fixture obsoleto | El caso split actual aprobado produce PASS | alta | No | Proteger resultado actual en approved golden | El usuario marco este caso como validado por ingenieria | No, el baseline actual es referencia |
| test_parse_moment_prequalified_split_bundle_from_directory | tests/unit/engine/test_moment_prequalified_split_inputs.py | domain/engine/validate.py | Espera `W24X76`, obtiene `W21X68` | fixture obsoleto | El JSON actual del caso 003 usa W21X68 | media | No | Actualizar test despues de Fase 0 con justificacion | No modificar input ni parser ahora | No |
| test_parse_moment_prequalified_split_bundle_from_any_member_file | tests/unit/engine/test_moment_prequalified_split_inputs.py | domain/engine/validate.py | Espera ancho 270 mm, obtiene 235 mm | fixture obsoleto | El JSON actual del caso 003 usa Bpe 235 mm | media | No | Actualizar expectativa despues de Fase 0 | No modificar input ni parser ahora | No |
| test_parse_moment_prequalified_split_bundle_4es_directory | tests/unit/engine/test_moment_prequalified_split_inputs.py | domain/engine/validate.py | Espera excepcion, no se lanza | cambio esperado por evolucion reciente | El bundle 4ES ahora se puede componer/validar parcialmente | media | No | Revisar contrato de split inputs antes de Fase 3 | No cambiar validacion en Fase 0 | No |
| test_parse_moment_prequalified_split_bundle_left_only_two_files | tests/unit/engine/test_moment_prequalified_split_inputs.py | tests + examples | JSONDecodeError por BOM | error de encoding/BOM | El test lee con `utf-8`; archivo tiene BOM | baja | No | Proponer usar `utf-8-sig` o quitar BOM en fase separada | No corregir encoding en Fase 0 | No |
| test_parse_moment_prequalified_split_bundle_right_only_two_files | tests/unit/engine/test_moment_prequalified_split_inputs.py | tests + examples | JSONDecodeError por BOM | error de encoding/BOM | El test lee con `utf-8`; archivo tiene BOM | baja | No | Proponer usar `utf-8-sig` o quitar BOM en fase separada | No corregir encoding en Fase 0 | No |
| test_parse_moment_prequalified_split_bundle_both_sides_missing_beam_file_fails | tests/unit/engine/test_moment_prequalified_split_inputs.py | tests + examples | JSONDecodeError por BOM antes de probar falta de archivos | error de encoding/BOM | El test no llega al escenario esperado por BOM | baja | No | Corregir test/fixture despues de Fase 0 | No corregir encoding en Fase 0 | No |
| test_bueep_rule_set_runs_without_errors | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | Espera >=13 checks, obtiene 6 | error de ejecucion parcial | WPZS corta la evaluacion | alta | No | Mantener documentado; no corregir WPZS en Fase 0 | Relacionado con caso suspicious | No, caso no approved |
| test_bueep_prequalification_limits_are_reported | tests/unit/rules/test_chapter_06_rules.py | rules/prequalification memory | Falta scope `table_6_1_der` | causa indeterminada | La memoria de limites ya no expone ese scope con ese nombre | media | No | Revisar trazabilidad de memoria antes de cambiar tests | Puede ser cambio de contrato de memoria, no calculo | No |
| test_step6_bolt_capacity_checks_are_reported_for_bseep_8es | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | StopIteration buscando Step 6.1 | error de ejecucion parcial | La corrida del fixture se corta antes de Step 6 | alta | No | Separar fixture unitario de baseline approved | No cambiar reglas en Fase 0 | No, no es el golden approved |
| test_step7_end_plate_capacity_checks_are_reported_for_bseep_8es | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | StopIteration buscando Step 7.1.1 | error de ejecucion parcial | La corrida del fixture se corta antes de Step 7 | alta | No | Separar fixture unitario de baseline approved | No cambiar reglas en Fase 0 | No |
| test_step8_stiffener_weld_tension_rupture_is_reported_for_bseep_8es | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | StopIteration buscando Step 8.1.1 | error de ejecucion parcial | La corrida del fixture se corta antes de Step 8 | alta | No | Separar fixture unitario de baseline approved | No cambiar reglas en Fase 0 | No |
| test_step9_stiffener_beam_weld_shear_rupture_is_reported_for_bseep_8es | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | StopIteration buscando Step 9.1.1 | error de ejecucion parcial | La corrida del fixture se corta antes de Step 9 | alta | No | Separar fixture unitario de baseline approved | No cambiar reglas en Fase 0 | No |
| test_step10_beam_shear_yielding_is_reported_for_bseep_8es | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | StopIteration buscando beam shear yielding | error de ejecucion parcial | La corrida del fixture se corta antes del check esperado | alta | No | Separar fixture unitario de baseline approved | No cambiar reglas en Fase 0 | No |
| test_step7_yp_is_derived_from_tables_for_bseep_8es | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | StopIteration buscando Step 7.1.1 | error de ejecucion parcial | La corrida del fixture se corta antes de Yp | alta | No | Separar fixture unitario de baseline approved | No cambiar reglas en Fase 0 | No |
| test_bseep_prequalification_limits_fail_when_pitch_is_below_3db | tests/unit/rules/test_chapter_06_rules.py | rules/prequalification memory | No encuentra id `table_6_1.pitch_pb_ge_3db_*` | causa indeterminada | La memoria actual no registra ese id esperado | media | No | Revisar trazabilidad de IDs antes de corregir tests | No corregir en Fase 0 | No |
| test_bseep8es_prequalification_limits_fail_when_pb_is_outside_89_95mm_range | tests/unit/rules/test_chapter_06_rules.py | rules/prequalification memory | Lista de checks `pitch_pb_ge_3db_*` vacia | causa indeterminada | ID/estructura de memoria no coincide con expectativa antigua | media | No | Revisar trazabilidad de Table 6.1 en fase posterior | No corregir en Fase 0 | No |
| test_step12_column_flange_local_bending_uses_side_specific_mf | tests/unit/rules/test_chapter_06_rules.py | domain/rules/aisc358/chapter_06_end_plate.py | StopIteration buscando Step 12 izquierda | error de ejecucion parcial | La corrida del fixture se corta antes de Step 12 | alta | No | Validar con golden approved antes de tocar Step 12 | No cambiar reglas en Fase 0 | No |
| test_grouped_geometry_payload_is_supported | tests/unit/rules/test_chapter_06_rules.py | adapters legacy/validate + rules | Espera >=13 checks, obtiene 6 | error de ejecucion parcial | Payload agrupado llega a WPZS y se corta por doubler plate | alta | No | Mantener como compatibilidad pendiente para fase de adapters | No corregir en Fase 0 | No |

## Resumen por categoria

- diferencia textual de reporte: 1
- error de ejecucion parcial: 13
- cambio esperado por evolucion reciente: 2
- fixture obsoleto: 3
- error de encoding/BOM: 3
- causa indeterminada: 3

## Bloqueadores para Fase 1

No hay bloqueo para crear contratos de resultados si Fase 1 compara contra golden files y no exige suite verde completa. Si se exige `pytest` completo verde como puerta de Fase 1, estos 25 fallos deben tratarse antes con cambios justificados y separados del refactor arquitectonico.
