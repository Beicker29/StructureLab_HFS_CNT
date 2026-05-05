# Arquitectura actual

Este documento describe el estado actual del repo despues de completar las
fases 0 a 6. No describe una arquitectura ideal futura, sino la estructura que
existe hoy y las compatibilidades legacy que se conservan para proteger
resultados validados.

## Resumen

El motor sigue un flujo deterministico:

```text
input JSON o split inputs
  -> adapters / validate
  -> InputCase legacy o DesignInput puente
  -> registry / strategy
  -> reglas aplicables
  -> DetailedRunResult
  -> DesignResult mapeado para trazabilidad
  -> JSON y Markdown
```

El contrato numerico aprobado sigue protegido por golden files. La prioridad de
la arquitectura actual es no cambiar resultados ni el formato publico de
`memory.md` sin aprobacion.

## Mapa de capas

### `models/`

Contiene contratos Pydantic y modelos legacy.

- `input.py`: `InputCase` legacy que todavia usa el motor principal.
- `raw_input.py`: entrada bruta tal como llega del usuario.
- `resolved_input.py`: entrada normalizada/enriquecida con trazabilidad de
  catalogos.
- `design_input.py`: contrato puente hacia calculo, con conversion a legacy.
- `materials.py`: `SteelMaterial`, `BoltMaterial`, `WeldMaterial`.
- `sections.py`: modelos de secciones y propiedades tipadas.
- `results.py`: `DesignResult`, `LimitStateResult`, estados de check y resumen.
- `diagnostics.py`: `DesignError`, `DesignWarning` y niveles de diagnostico.
- `output.py`: salida legacy `DetailedRunResult` y `CheckResult`.
- `units.py`: cantidades, unidades y modelo estricto base.

### `catalogs/`

Encapsula lectura tipada de catalogos XLSX.

- `interfaces.py`: contratos e identificacion de fuente de propiedades.
- `xlsx_sections.py`: repositorio de secciones.
- `xlsx_materials.py`: repositorio de materiales.

La carpeta `src/steel_connections/data/` sigue existiendo como compatibilidad
legacy durante la transicion.

### `adapters/`

Convierte formatos externos o legacy hacia modelos internos.

- `json_input.py`: payload JSON unico.
- `split_inputs.py`: composicion de entradas separadas por lado.
- `legacy_input.py`: compatibilidad hacia `InputCase`.

Aqui deben vivir aliases, compatibilidad de nombres y conversiones de entrada.
No debe agregarse logica normativa en esta capa.

### `codes/`

Contiene funciones de ingenieria y normativas reutilizables.

- `aisc358/chapter_06.py`: funciones puras extraidas de Chapter 6.
- `aisc358/chapter_07.py`: funciones para otros requisitos AISC 358.
- `dg1/chapter_01.py`: base inicial DG1.
- `engineering/`: ecuaciones compartidas por tema: soldadura, cortante,
  flexion, geometria, pernos y grupos de pernos.

Regla vigente: `codes/` no debe leer archivos, consultar catalogos ni generar
reportes.

### `domain/`

Orquesta el diseno.

- `engine/validate.py`: carga y validacion.
- `engine/pipeline.py`: corrida de caso y armado de `DetailedRunResult`.
- `engine/result_mapping.py`: mapeo temporal de `DetailedRunResult` a
  `DesignResult`.
- `routing/applicability_matrix.py`: matriz legacy de reglas aplicables.
- `registry.py`: registry actual de estrategias.
- `strategies/`: estrategias por familia/conexion.
- `rules/`: reglas ejecutables existentes.

Estado actual: el registry ya existe, pero varias reglas siguen trabajando con
`InputCase` legacy. La evolucion esperada es migrar gradualmente a
`DesignInput` y emitir `DesignResult` directamente.

### `reporting/`

Genera artefactos de salida.

- `json_writer.py`: escribe `detailed.json` legacy y `DesignResult`.
- `markdown/`: renderer puro de `DesignResult`.
- `markdown_writer.py`: writer legacy especializado para preservar el formato
  publico aprobado de `memory.md` y `Detalle_Ru_blt_web_v23.md`.

Decision actual: `memory.md` publico debe seguir saliendo por el writer legacy
hasta que la ruta pura pueda demostrar equivalencia textual contra golden.

### `cli/`

Interfaz de consola.

- `cli/main.py`: comando instalado `steel-connections`.
- `run.py`: compatibilidad con `python -m src.steel_connections.run`.

La CLI no debe contener logica normativa.

## Baseline y golden approved

Casos approved:

- `examples/moment_prequalified/case_003_bseep_8es_split_inputs`
- `examples/Fully Restrained Moment/case_001_bbmb_splice.json`

Archivos protegidos por comparacion:

- `tests/golden/approved/case_003_bseep_8es_split_inputs/detailed.json`
- `tests/golden/approved/case_003_bseep_8es_split_inputs/memory.md`
- `tests/golden/approved/case_001_bbmb_splice/detailed.json`
- `tests/golden/approved/case_001_bbmb_splice/memory.md`

Los golden `observed_baseline/` sirven para detectar cambios, pero no son
aprobacion tecnica de ingenieria.

## Riesgos residuales

- `markdown_writer.py` conserva calculos y consultas legacy por compatibilidad
  textual. No es la arquitectura final.
- `chapter_06_end_plate.py` sigue siendo grande. Debe reducirse solo por
  extracciones pequenas y comparadas contra golden.
- Algunas estrategias aceptan `DesignInput`, pero convierten a `InputCase`
  legacy internamente.
- No se debe agregar nueva funcionalidad antes de mantener la puerta de calidad
  en verde.
