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
  - procedimiento 6.7 completo (lado viga y lado columna) en flujo deterministico `validate -> route -> evaluate -> emit`
  - pasos 1, 1a y 2 a 18 de 6.7.1 (incluyendo 11-12 para 4E y verificaciones de rigidizador para BSEEP)
  - Paso 1a: revision de compacidad de viga y columna con limites segun demanda de ductilidad (`high` / `moderate`) usando AISC 341-22 Tabla D1.1
  - pasos 1 a 7 de 6.7.2 (incluyendo panel zone y column-beam moment ratio)
  - gage de pernos (Sec. 6.6.1)
  - cortante de placa en 4E (Ecs. 6.7-7 y 6.7-8)
  - ruptura por cortante de pernos (Ec. 6.7-11)
  - aplastamiento/tearout en placa y ala de columna (Ec. 6.7-12)
  - geometria/espesor/pandeo local de rigidizador en BSEEP (Ecs. 6.6-1, 6.7-9, 6.7-10)
- Preparado y bloqueante por alcance: familia `base_plate_anchor_rod` (`connection_type = dg1_base_plate`) via `NOT_IMPLEMENTED`.
- Nota tecnica: parametros tabulados (p. ej. `Yp`, `Yc`) se reciben por `procedure.*` con trazabilidad explicita; no hay inferencias ocultas.

## Estructura
```text
src/steel_connections/
  models/        # contratos de entrada/salida, unidades y errores
  codes/         # calculos normativos puros
  domain/        # reglas, routing y pipeline de motor
  reporting/     # salida terminal + persistencia JSON
  cli/           # interfaz de ejecucion
examples/        # casos de entrada
results/         # salidas por example
tests/           # unit e integration tests
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
- `bolt_fabrication_standard`, `bolt_description`, `bolt_shape`, `bolt_thread_condition`
  - `bolt_shape` se valida/lee contra `sections.xlsx` hoja `Perno`
  - `bolt_fabrication_standard` + `bolt_description` se validan/leen contra `materials.xlsx` hoja `Pernos`
  - `bolt_thread_condition` obligatorio para Chapter 6: `N` (threads included in shear plane) o `X` (threads excluded), para seleccionar `Fnv` correcto desde `materials.xlsx`

Campos clave en `design_factors` para Chapter 6 Step 1a:
- `member_ductility_demand_beam`: `high` o `moderate`
- `member_ductility_demand_column`: `high` o `moderate`
- `compactness_ca_beam`: coeficiente `Ca` del miembro de viga (`0 <= Ca < 1`)
- `compactness_ca_column`: coeficiente `Ca` del miembro de columna (`0 <= Ca < 1`)

Campos geometricos clave para artefacto tecnico (`geometry.svg`) en Chapter 6:
- `de`, `pb`, `pfo`, `pfi` como longitudes explicitas (sin defaults ocultos)
- El artefacto muestra y traza: `bp`, `g`, `de`, `pb`, `pfo`, `pfi`, `h1`, `h2`, `h3`, `h4`
- En el detalle, `h1..h4` se acotan desde la mitad del espesor de la aleta inferior y `tbf` corresponde al espesor de la aleta.

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
- Consola: resumen compacto de estado global, conteos y peor DCR.
- Carpeta por example: `results/<example_json_sin_extension>/`.
- Archivo detallado: `detailed.json`.
- Artefacto grafico: `geometry.svg` (esquema de geometria de la conexion para auditoria tecnica).
- Cada chequeo incluye `name`, `clause`, `demand`, `capacity`, `dcr`, `status`, `calculation_memory`.

## Ejemplos canonicos Chapter 6
- Se mantiene un solo JSON por variacion:
  - `case_002_bueep_4e.json`
  - `case_004_bseep_4es.json`
  - `case_003_bseep_8es.json`
- Los tres ejemplos estan en unidades `SI` con `column_shape = W18X175` y `beam_shape = W24X76`.

## CLI
```bash
python -m src.steel_connections.run examples/moment_prequalified/case_002_bueep_4e.json
python -m src.steel_connections.run examples/moment_prequalified/case_004_bseep_4es.json
python -m src.steel_connections.run examples/moment_prequalified/case_003_bseep_8es.json
```

Salida por defecto:
```bash
results/<example_json_sin_extension>/detailed.json
```

Opcionalmente puedes indicar carpeta de salida como segundo argumento:
```bash
python -m src.steel_connections.run <archivo.json> <carpeta_salida>
```

## Estado de chequeo
- `PASS`
- `FAIL`
- `ERROR`
- `NOT_IMPLEMENTED` (bloqueante si aplicable)

## Seguridad de implementacion
- No se incorporan aproximaciones no respaldadas explicitamente.
- Los campos/chequeos fuera de alcance se reportan de manera explicita.
