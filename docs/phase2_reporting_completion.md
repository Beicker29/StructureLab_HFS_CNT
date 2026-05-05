# Fase 2 - Cierre de reportes puros

Fecha: 2026-05-04

## Decision aplicada

Se agrego una ruta pura nueva para renderizar `DesignResult`, pero la salida
publica `memory.md` conserva el writer legacy especializado mientras no exista
equivalencia textual aprobada.

`src/steel_connections/reporting/markdown_writer.py` queda como writer legacy
de compatibilidad para conservar los nombres publicos existentes:

- `render_memory_markdown`
- `write_memory_markdown`
- `render_splice_methods_table_markdown`
- `write_splice_methods_table_markdown`

La ruta pura queda disponible en `steel_connections.reporting.markdown` y
`steel_connections.reporting.json_writer`, pero no reemplaza todavia los
artefactos publicos de memoria.

## Cambios esperados

El contenido textual de `memory.md` no debe cambiar respecto al baseline legacy
aprobado.

La memoria legacy recalcula valores y consulta catalogos dentro de reporting;
por eso no se considera arquitectura final. Sin embargo, reemplazarla por una
memoria generica basada en `DesignResult` cambia la salida visible y no debe ser
la ruta publica hasta que el motor emita todos los datos necesarios para
reproducir la memoria sin recalcular.

No hay cambios numericos intencionales porque:

- el motor de calculo no se modifica;
- `chapter_06_end_plate.py` no se modifica;
- `markdown_writer.py` se mantiene como writer legacy para preservar texto;
- `DesignResult` conserva `demand`, `capacity`, `dcr`, inputs,
  intermedios, factores y unidades desde `DetailedRunResult`;
- `detailed.json` legacy sigue escribiendose con `write_detailed_result`.

## Limitacion residual

La memoria pura no replica todavia la narrativa detallada del writer legacy.
Para reemplazar la memoria legacy sin cambiar texto, las fases siguientes deben
hacer que el motor emita como `DesignResult` todos los datos que antes se
derivaban dentro del writer legacy.

La equivalencia numerica y textual de los casos aprobados debe validarse contra
golden files antes de retirar el writer legacy.
