# Auditoria DRY de Ecuaciones (AISC)

Fecha: 2026-04-20

## Objetivo
Eliminar duplicacion de formulas de ingenieria y consolidarlas en una capa reusable para reglas, API y reportes.

## Hallazgos principales (duplicacion detectada)
- Soldadura de filete `phi * nl * 0.6 * Fexx * 0.707 * L * w` repetida en:
  - `chapter_06_end_plate.py` (paso 8 y paso 9)
  - `markdown_writer.py` (paso 11)
- Flexion local de aleta de columna `phi*(t_cf^2*f_yc*Y)/1.11` repetida en:
  - reglas/evaluacion (paso 12)
  - reporte `memory.md` (paso 12)
- Cortante de alma de viga con `Cv1` repetido en:
  - `_compute_beam_available_shear_strength`
  - `run_step10_1_1_beam_shear_yielding`
- Longitud de zona protegida con la misma logica en mas de un punto del flujo.

## Refactor aplicado
Se creo la capa `src/steel_connections/codes/engineering/`:

- `constants.py`
  - `AISCConstants` centraliza factores repetidos (`0.6`, `0.707`, `1.11`, `phi`, `kv`, etc.).
- `weld.py`
  - `WeldFillet.design_strength()` (AISC 360-22 J2.4)
  - `compute_effective_web_weld_length()`
  - `compute_plate_tension_demand_from_yielding()`
  - `compute_plate_shear_demand_from_yielding()`
- `shear.py`
  - `compute_beam_web_shear_yielding_strength()` (AISC 360-22 G2.1)
- `flexure.py`
  - `compute_column_flange_local_bending_strength()` (AISC 358-22 6.7.2)
  - `compute_dcr()`
- `geometry.py`
  - `compute_protected_zone_length()` (AISC 358-22 2.3.4(8))

## Integracion hecha en motor y reporte
- `chapter_06_end_plate.py`
  - Paso 8 y 9 migrados a `WeldFillet` + demandas reutilizables.
  - Cortante de alma migrado a `compute_beam_web_shear_yielding_strength`.
  - Zona protegida migrada a `compute_protected_zone_length`.
- `markdown_writer.py`
  - Paso 11 usa las mismas ecuaciones de `weld.py`.
  - Paso 12 usa la misma ecuacion de `flexure.py`.

## Split inputs (viga derecha/izquierda)
- Se elimino la restriccion de igualdad forzada entre derecha e izquierda para:
  - `geometry.welds.weld_1/weld_2/weld_3`
  - `design_factors` de archivos de viga
- El flujo canonico actual consume lado derecho para campos legacy compartidos, sin bloquear que la viga izquierda tenga datos diferentes.

## Estado
- Se elimino duplicacion funcional de las ecuaciones anteriores (mismo nucleo para calcular y reportar).
- Quedan ecuaciones legacy en `codes/aisc358/chapter_06.py` que ya eran funciones puras, pero aun pueden enriquecerse en otra iteracion con objetos de resultado uniformes.
- Pruebas unitarias dedicadas para la capa reusable agregadas en `tests/unit/codes/test_engineering_equations.py`.

## Proxima iteracion recomendada
- Migrar progresivamente formulas restantes de `codes/aisc358/chapter_06.py` a resultados uniformes de alto nivel por tema (`weld`, `shear`, `flexure`, `bolts`, `geometry`) sin romper compatibilidad.
- Agregar tests unitarios dedicados para `codes/engineering/*` con trazabilidad de clausula.
