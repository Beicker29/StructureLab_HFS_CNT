# StructureLab Steel Connections v1

Motor de diseno de conexiones de acero estructural hot-rolled, deterministico, auditable y fail-hard.

## Filosofia tecnica
- Sin defaults ocultos ni supuestos silenciosos.
- Si falta informacion para una regla aplicable, la corrida se detiene con error estructurado.
- Cada chequeo es trazable a documento y clausula.
- Si una regla aplicable no esta implementada: `NOT_IMPLEMENTED` bloqueante.

## Fuente de verdad normativa
- `a358-22w.pdf`
- `Design Guide 1 - Base Plate and Anchor Rod Design (3nd Edition).pdf`

## Fuente de perfiles
- `data/sections.xlsx` es la fuente maestra de propiedades de perfiles.
- El motor consume directamente `data/sections.xlsx` para lookup deterministico por `beam_shape` y `column_shape`.
- El motor no acepta propiedades geometricas de perfil en el input (`d`, `bf`, `tf`, `tw`).
- En chequeos que requieren espesor de ala de columna, se usa `tf` desde `sections.column_shape` (no desde `geometry`).
- Para pernos, el motor consume `data/sections.xlsx` hoja `Perno` para propiedades geometricas (incluyendo diametro nominal).

## Fuente de materiales
- `data/materials.xlsx` es la fuente maestra de propiedades mecanicas.
- Hoja `HRS`: `Fy/Fu` de perfiles (viga/columna).
- Hoja `Platinas`: `Fy/Fu` de platinas (placa extremo, rigidizadores, etc.).
- Hoja `Pernos`: `Fnt/Fnv` del perno.

## Alcance v1
- Operativo: familia `moment_prequalified` (`connection_type = wuf_w`) con chequeos iniciales trazables.
- Operativo: Chapter 6 AISC 358 para `connection_type = bueep_4e`, `bseep_4es`, `bseep_8es` con chequeos trazables de:
  - chequeo inicial `PREQUALIFICATION LIMITS` (Section 6.3 + Table 6.1) en flujo deterministico `validate -> route -> evaluate -> emit`
  - detalle por subchequeo para:
    - viga (`beam`)
    - columna (`column`)
    - tabla 6.1 (`table_6_1`)
- Preparado y bloqueante por alcance: familia `base_plate_anchor_rod` (`connection_type = dg1_base_plate`) via `NOT_IMPLEMENTED`.
- Nota tecnica: parametros tabulados aplicables (p. ej. `Yc`) se reciben por `procedure.*` con trazabilidad explicita.

## Estructura
```text
src/steel_connections/
  models/        # contratos de entrada/salida, unidades y errores
  codes/         # calculos normativos puros
    engineering/ # ecuaciones reutilizables por tema (DRY): weld, shear, flexure, geometry
  domain/        # reglas, routing y pipeline de motor
  reporting/     # salida terminal + persistencia JSON
  cli/           # interfaz de ejecucion
examples/        # casos de entrada
results/         # salidas por example
tests/           # unit e integration tests
```

## API DRY de ecuaciones
Ecuaciones de ingenieria reutilizables y trazables:
- `src/steel_connections/codes/engineering/weld.py`
- `src/steel_connections/codes/engineering/shear.py`
- `src/steel_connections/codes/engineering/flexure.py`
- `src/steel_connections/codes/engineering/geometry.py`
- `src/steel_connections/codes/engineering/constants.py`

Ejemplo (soldadura de filete, AISC 360-22 J2.4):
```python
from steel_connections.codes.engineering.weld import WeldFillet
from steel_connections.models.units import Quantity, UnitSystem

weld = WeldFillet(
    fexx=Quantity(value=490.0, unit="MPa"),
    weld_size=Quantity(value=8.0, unit="mm"),
    weld_length=Quantity(value=300.0, unit="mm"),
    weld_lines=2,
    unit_system=UnitSystem.SI,
    phi=0.9,
)
result = weld.design_strength()
# result["phi_rn"], result["rn"], result["equation"], result["reference"]
```

## Entrada JSON requerida
Campos obligatorios de alto nivel:
- `project_id`
- `case_id`
- `design_code_context`
- `units_system` (`US` o `SI`)
- `connection_family`
- `connection_type`
- `load_state`
- `sections` (incluye `beam_shape` y `column_shape` para chequeos del lado columna)
- `materials`
- `geometry`
- `loads`
- `design_factors`
- `procedure` para Chapter 6.7 (parametros normativos y capacidades auxiliares requeridas por paso)

Campos clave en `materials` para Chapter 6:
- `profile_steel_type` (lookup en `materials.xlsx` hoja `HRS`)
- `plate_steel_type` (lookup en `materials.xlsx` hoja `Platinas`)
- `bolt_fabrication_standard`, `bolt_description`
  - `bolt_fabrication_standard` + `bolt_description` se validan/leen contra `materials.xlsx` hoja `Pernos`
  - `bolt_shape` y `bolt_thread_condition` se reportan en `geometry.bolts.*`
  - `bolt_shape` se valida/lee contra `sections.xlsx` hoja `Perno`
  - `bolt_thread_condition` obligatorio: `N` (threads included in shear plane) o `X` (threads excluded), para seleccionar `Fnv` correcto desde `materials.xlsx`

Campos clave en `design_factors` para Chapter 6 Step 1a:
- `member_ductility_demand_beam`: `high` o `moderate`
- `member_ductility_demand_column`: `high` o `moderate`

Campos clave en `loads` para compactacion Chapter 6:
- `pu_viga`: carga axial `Pu` de la viga.
- `pu_columna`: carga axial `Pu` de la columna.
- Convencion de signo axial del repo: traccion positiva (`+`) y compresion negativa (`-`).
- El motor calcula `Ca` automaticamente como `Ca = Pu / (Ry * Ag * Fy)`:
  - `Ag` desde `data/sections.xlsx` (catalogo de secciones)
  - `Fy` desde `data/materials.xlsx` (hoja `HRS`)
  - `Ry` derivado automaticamente desde `data/materials.xlsx` (hoja `HRS`) segun `materials.profile_steel_type`

Campos geometricos clave en Chapter 6:
- Estructura agrupada recomendada:
  - `geometry.beam`
  - `geometry.column`
  - `geometry.end_plate`
  - `geometry.continuity_plate`
  - `geometry.stiffener`
  - `geometry.bolts`
  - `geometry.welds`
- `geometry.beam.clear_span_length`: luz libre de la viga.
- `geometry.beam.shear_connector_free_length_from_column_face`: longitud sin conectores de cortante medida desde la cara de columna (`Lsc`).
- `geometry.column.slab_connection_condition`: condicion union columna-losa (`isolated`/`not_isolated`; tambien acepta `aislada`/`no_aislada`).
- `geometry.welds.continuity_plate_weld_type`: tipo de soldadura para la platina de continuidad (`double_sided_fillet`, `CJP`, `PJP`).
- `geometry.bolts.bolt_tightening_type`: tipo de apriete de pernos (`pretensioned` o `snug_tight`).
- En particular: `geometry.end_plate.de`, `geometry.end_plate.pb`, `geometry.end_plate.pfo`, `geometry.end_plate.pfi`
- La altura de platina se deriva como `hp = d + 2*pfo + 2*de` (`d` desde catalogo de la viga).

Regla de arquitectura:
- `d`, `bf`, `tf`, `tw` del perfil **no** se aceptan en el input.
- Esas propiedades se obtienen exclusivamente desde `data/sections.xlsx` usando `sections.beam_shape` y `sections.column_shape`.
- `bolt_diameter`, `bolt_fnt` y `bolt_fnv` se derivan desde catalogos; no deben controlarse manualmente.
- Para `bseep_4es` y `bseep_8es`, en el Paso 1 (Mpr) el motor usa `Ze = Zx` del catalogo de secciones (`data/sections.xlsx`), con trazabilidad en `calculation_memory.inputs.ze_source`.

Cada magnitud numerica usa objeto:
```json
{ "value": 50.0, "unit": "ksi" }
```

## Salida
- Consola: resumen compacto de estado global, conteos y pasos de verificacion legibles (`calculado` vs `limite`) con simbolos tecnicos (`bp`, `bf`, `db`, etc.).
- Carpeta por example (default): `results/<ruta_relativa_en_examples_sin_extension>/`.
- Archivo detallado: `detailed.json`.
- Memoria de presentacion: `memory.md`.
- En esta etapa (Paso 1), cada chequeo reporta subverificaciones con `calculated`, `limit`, `comparison`, `margin` y `result`.
- El Paso 1 tambien incluye los requisitos de Section 2.3.4: `Lsc >= 1.5d` y losa `isolated`.

## Ejemplos canonicos Chapter 6
- Se mantiene un bundle split por variacion (3 archivos: columna/comunes, viga derecha, viga izquierda):
  - `case_002_bueep_4e_split_inputs/`
  - `case_004_bseep_4es_split_inputs/`
  - `case_003_bseep_8es_split_inputs/`
- Los tres ejemplos estan en unidades `SI`.
- En split-inputs, derecha e izquierda pueden usar perfiles distintos; el motor conserva ambos (`beam_shape_der`, `beam_shape_izq`).

## CLI
```bash
python -m src.steel_connections.run examples/moment_prequalified/case_002_bueep_4e_split_inputs
python -m src.steel_connections.run examples/moment_prequalified/case_004_bseep_4es_split_inputs
python -m src.steel_connections.run examples/moment_prequalified/case_003_bseep_8es_split_inputs
python -m src.steel_connections.run "examples/Fully Restrained Moment/case_001_bbmb_splice.json"
```

Salida por defecto:
```bash
results/<ruta_relativa_en_examples_sin_extension>/detailed.json
```

Opcionalmente puedes indicar carpeta de salida como segundo argumento:
```bash
python -m src.steel_connections.run <archivo.json> <carpeta_salida>
```

En `bbmb_splice` (Pernos 1 / Punto 2) puedes seleccionar:
- `Elastic Method - Superposition`
- `Elastic Method - Center of Rotation`
- `Instant Center of Rotation Method`
El motor usa un nucleo matematico interno desacoplado (sin dependencia runtime de `ezbolt`).
Para `bbmb_splice`, la excentricidad se define por convencion de detalle:
- `ex = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x-1)*g_blt_web`
- `ey = loads.ey_blt_web` (default `0`)
- `Mz = Vy*ex - Vx*ey`

## Estado de chequeo
- `PASS`
- `FAIL`
- `ERROR`
- `NOT_IMPLEMENTED` (bloqueante si aplicable)

## Seguridad de implementacion
- No se incorporan aproximaciones no respaldadas explicitamente.
- Los campos/chequeos fuera de alcance se reportan de manera explicita.
