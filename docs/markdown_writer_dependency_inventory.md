# Inventario de dependencias de markdown_writer.py

Fecha: 2026-05-04

Alcance: Fase 2. Este inventario documenta el estado actual antes de refactorizar
`src/steel_connections/reporting/markdown_writer.py`. No corrige formulas, no
cambia resultados y no reemplaza todavia la memoria legacy.

## Resumen ejecutivo

`markdown_writer.py` no es un renderizador puro todavia. Consume
`DetailedRunResult`, pero tambien:

- importa funciones de ingenieria desde `steel_connections.codes`;
- consulta propiedades de materiales en `steel_connections.data`;
- crea objetos `Quantity` y hace conversiones de unidades;
- recalcula demandas, capacidades y DCRs para bloques de reporte;
- deriva secciones completas de la memoria a partir de `inputs` e
  `intermediates` de checks previos.

Por esta razon, reemplazar `memory.md` por un writer puro de una sola vez
modificaria contenido tecnico o esconderia calculos que hoy viven en reporting.
El cambio seguro de Fase 2 es introducir una ruta nueva y pura para
`DesignResult`, mantener el writer legacy intacto y usar este inventario para
decidir que datos deben entrar al resultado trazable antes de retirar calculos
del reporte.

## Dependencias directas actuales

| Tipo | Dependencia | Uso actual | Riesgo |
|---|---|---|---|
| Modelo legacy | `DetailedRunResult` | Entrada principal de `render_memory_markdown`, collectors y writers | Acopla reporting a salida legacy |
| Modelo de unidades | `Quantity`, `UnitSystem` | Formato, conversiones y recalculos locales | Reporting contiene logica dimensional |
| Codigo de ingenieria | `compute_column_flange_local_bending_strength` | Recalcula capacidad para bloque de aleta de columna | Recalculo fuera del nucleo |
| Codigo de ingenieria | `compute_dcr` | Recalcula DCRs en varios bloques | Riesgo de doble fuente de verdad |
| Codigo de ingenieria | `compute_beam_web_shear_yielding_strength` | Recalcula resistencia de cortante de alma | Recalculo fuera del nucleo |
| Codigo de ingenieria | `WeldFillet`, `compute_fillet_weld_check_with_kds` | Recalcula resistencia de soldaduras | Recalculo fuera del nucleo |
| Codigo de ingenieria | `compute_effective_web_weld_length` | Deriva longitud efectiva de soldadura | Recalculo fuera del nucleo |
| Codigo de ingenieria | `compute_plate_tension_demand_from_yielding` | Deriva demanda a traccion | Recalculo fuera del nucleo |
| Catalogo/data | `get_hrs_steel_properties` | Obtiene propiedades de acero en bloques de reporte | Reporting consulta catalogos |
| Catalogo/data | `get_plate_steel_properties` | Obtiene Fy/Fu de placas para bloques de continuidad/doubler | Reporting consulta catalogos |

Referencias principales:

- Imports impuros: lineas 7-21.
- Entrada legacy: linea 23 y funciones tipadas con `DetailedRunResult`.
- Render principal legacy: `render_memory_markdown` cerca de linea 4930.
- Writer legacy: `write_memory_markdown` cerca de linea 6993.

## Datos que usa desde el resultado

El writer usa estos campos de `DetailedRunResult`:

| Campo | Uso |
|---|---|
| `project_id` | Encabezado de memoria |
| `case_id` | Encabezado de memoria |
| `connection_family` | Seleccion de layout moment prequalified vs BBMB splice |
| `connection_type` | Seleccion de bloques BSEEP/BUEEP/BBMB |
| `load_state` | Contexto general |
| `global_status` | Estado global, indirectamente |
| `summary` | Resumen y peor DCR |
| `checks` | Fuente primaria de checks y memoria de calculo |
| `errors` | Errores de ejecucion |

De cada `CheckResult` usa:

| Campo | Uso |
|---|---|
| `rule_id` | Filtrado por paso, lado y tipo de regla |
| `name` | Texto del check |
| `clause` | Clausulas en secciones |
| `source_document` | Fuente normativa |
| `demand` | Demanda reportada |
| `capacity` | Capacidad reportada |
| `dcr` | DCR reportado |
| `status` | Etiqueta visual de cumplimiento |
| `notes` | Notas tecnicas |
| `calculation_memory.inputs` | Datos principales y fallback para bloques |
| `calculation_memory.intermediates` | Derivados, tablas y reportes de metodo |
| `calculation_memory.design_factors` | Phi, flags y parametros |
| `calculation_memory.equation` | Ecuacion del check |
| `calculation_memory.units_trace` | Unidades usadas |
| `calculation_memory.final_capacity` | Capacidad final cuando existe |

## Datos que ya vienen del resultado trazable Fase 1

El `DesignResult` de Fase 1 ya conserva, por check:

- `rule_id`, `name`, `clause`, `source_document`;
- `status`;
- `demand`, `capacity`, `dcr`;
- `equation`;
- `inputs`;
- `intermediates`;
- `design_factors`;
- `units`;
- `final_capacity`;
- `notes`;
- errores y advertencias estructuradas.

Esto permite crear un Markdown puro generico desde `DesignResult`, pero no
permite reproducir todavia todo el `memory.md` legacy sin recalcular, porque
algunos bloques del legacy construyen valores nuevos que no existen como checks
ni como campos trazables.

## Datos que recalcula el writer legacy

| Bloque aproximado | Que recalcula | Fuente parcial | Observacion |
|---|---|---|---|
| Paso 12 soldadura #3 | `hwef`, demanda de placa, capacidad de filete, DCR | `step_11_inputs`, `step_10_inputs` | Debe salir del motor como resultado trazable o intermedio |
| Paso 13 aleta columna | `phi*Mn`, `Ru_cf`, `phi*Rn_cf`, DCR | check de flexion local, prequal inputs | Usa funciones de flexion y conversion de momentos |
| Pasos 24-25 continuidad | demandas `Ru_pc`, capacidades tension/compresion/cortante, Fcr, KL/r | checks 12/13/14 + step 1 inputs | Calcula estados completos en reporting |
| Paso 26 soldadura #6 | demandas Ru1..Ru9, resistencia de filete y material base, DCRs | step 1 inputs + WPZS | Usa shear y weld helpers |
| Paso 27 soldadura #8 | demandas por combinaciones de momentos, capacidad de filete, DCR | step 1 + WPZS | Calcula demanda/capacidad en reporte |
| Paso 28 soldadura #7 | demanda desde WPZS/doubler, capacidad, DCR | step 1 + WPZS | Parte de los casos suspicious actuales |
| Resumen DCR final | Extrae DCRs desde texto renderizado | Bloques markdown ya generados | Riesgo: resumen depende del texto, no del resultado |

## Datos que consulta en catalogos/data

| Funcion | Uso | Dato faltante en resultado |
|---|---|---|
| `get_plate_steel_properties` | Propiedades Fy/Fu de placas de continuidad/doubler | Material resuelto con fuente y unidades |
| `get_hrs_steel_properties` | Propiedades de acero HRS para piezas especificas | Material resuelto con fuente y unidades |

Estos accesos deben moverse fuera de reporting en fases posteriores. El dato
debe llegar al reporte dentro de `DesignResult` como input resuelto,
intermedio, `derived_values` o check independiente.

## Datos faltantes en DesignResult para retirar el legacy

Antes de reemplazar `memory.md` legacy, el flujo de calculo debe entregar:

- metadatos de layout del reporte: orden de pasos, agrupacion por lado, titulos
  visibles y bloques aplicables;
- valores derivados usados solo por reporte hoy: `Ru_pc`, `phi*Rn_pc`,
  `Fcr_pc`, `KL/r`, `Ru_w5`, `Ru_w6`, `Ru_w8`, capacidades de material base y
  DCRs asociados;
- propiedades de materiales resueltas para placas, soldaduras y perfiles con
  fuente de catalogo;
- flags de aplicabilidad con razon cuando el bloque sea `NA`;
- resumen de DCR construido desde checks, no desde texto Markdown;
- datos de metodo BBMB splice ya normalizados para render sin reconstruccion.

## Decision de Fase 2 aplicada

Se introduce una ruta nueva:

- `steel_connections.reporting.markdown` renderiza `DesignResult` sin importar
  `data`, `catalogs`, `codes` ni `markdown_writer`;
- `steel_connections.reporting.json_writer` serializa `DesignResult` sin romper
  `DetailedRunResult`;
- `markdown_writer.py` queda intacto como writer legacy hasta que los datos
  anteriores existan en resultados trazables.

Esta decision evita cambios textuales o numericos no aprobados en los golden
files actuales.
