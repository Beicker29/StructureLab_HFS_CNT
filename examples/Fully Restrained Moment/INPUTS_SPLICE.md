# Inputs Tecnicos - Bolted Splice Connection (Viga-Viga)

Este documento define el significado fisico y geometrico de los inputs de una conexion metalica tipo empalme pernado de viga de acero.

## 1) Contexto general del problema

La conexion de empalme incluye:
1. Viga a empalmar.
2. Platina de union del alma (platina 1), centrada respecto a la altura de la viga.
3. Dos platinas de union de alas (platina 2), centradas en planta respecto al eje de la viga.
4. Grupo de pernos del alma (viga-alma con platina 1).
5. Grupo de pernos del ala (viga-ala con platina 2).

Convencion geometrica local:
- Direccion `x`: horizontal.
- Direccion `y`/vertical: vertical.

Estos inputs alimentan chequeos geometricos y de resistencia: pernos, aplastamiento, bloque de cortante, seccion neta y similares.

## 2) Inputs de la viga

### `sep`
Separacion libre entre extremos enfrentados de las dos vigas en la junta de empalme.

### `perfil`
Designacion del perfil metalico de la viga (W, IPE, HEB, etc.) para obtener propiedades geometricas.

### `tipo_acero_viga`
Tipo de acero del perfil principal de la viga (designacion o propiedades de resistencia).

### `condicion_superficial`
Condicion superficial de la viga: `pintada` o `no pintada`.

### `condicion_atmosferica`
Condicion atmosferica de exposicion para la viga: `corrosiva` o `no corrosiva`.

## 3) Inputs de la platina 1 (union del alma)

La platina 1 empalma el alma y se centra en altura respecto al eje de la viga.

### `tp1`
Espesor de la platina 1.

Nota de modelado:
- `bp1` y `hp1` se derivan automaticamente a partir del patron de pernos del grupo 1 (`Le1_*`, `S1_*`, `nb1_*`).
- No se ingresan manualmente como input principal.

### `tipo_acero_p1`
Material de la platina 1.

### `tipo_agujero_p1`
Tipo normativo de agujero en platina 1 (estandar, sobredimensionado, ranurado corto/largo, etc.).

### `condicion_superficial`
Condicion superficial de la platina 1: `pintada` o `no pintada`.

### `condicion_atmosferica`
Condicion atmosferica de exposicion de la platina 1: `corrosiva` o `no corrosiva`.

## 4) Inputs de la platina 2 (union de alas)

La platina 2 representa la configuracion tipo de la placa de ala (superior e inferior).

### `tp2`
Espesor de la platina 2.

Nota de modelado:
- `bp2` y `lp2` se derivan automaticamente a partir del patron de pernos del grupo 2 (`Le2_*`, `S2_*`, `nb2_*`).
- No se ingresan manualmente como input principal.

### `tipo_acero_p2`
Material de la platina 2.

### `tipo_agujero_p2`
Tipo normativo de agujero en platina 2.

### `condicion_superficial`
Condicion superficial de la platina 2: `pintada` o `no pintada`.

### `condicion_atmosferica`
Condicion atmosferica de exposicion de la platina 2: `corrosiva` o `no corrosiva`.

## 5) Inputs de pernos - Grupo 1 (alma con platina 1)

### `bolt_shape_1`
Tamano nominal o referencia geometrica del perno (3/4 in, 7/8 in, M20, etc.).

### `bolt_thread_condition_1`
Condicion de rosca respecto al plano de corte (incluida/excluida).

### `bolt_fabrication_standard_1`
Norma de fabricacion del perno (A325, A490, ASTM F3125, etc.).

### `bolt_description_1`
Descripcion complementaria del perno (grado/acabado/condicion).

### `bolt_tightening_type`
Tipo de apriete del perno del grupo 1: `pretensioned` o `snug_tight`.

### Ubicacion del patron de pernos del alma

#### `Le1_x1`
Distancia horizontal desde borde de viga hasta la primera columna de pernos.

#### `Le1_x2`
Distancia horizontal desde borde de platina 1 hasta la columna de pernos opuesta.

#### `S1_x`
Separacion horizontal entre columnas de pernos.

#### `S1_y`
Separacion vertical entre filas de pernos.

#### `Le1_y1`
Distancia vertical desde borde inferior de platina 1 hasta la fila inferior.

#### `Le1_y2`
Distancia vertical desde borde superior de platina 1 hasta la fila superior.

#### `nb1_x`
Numero de columnas de pernos en direccion `x` conectadas a **una viga**.
En la conexion completa (dos vigas), el total de columnas equivalentes en `x` es `2*nb1_x`.

#### `nb1_y`
Numero de filas en direccion vertical.

Interpretacion general:
- `Le...`: edge distance (distancia al borde).
- `S...`: spacing (separacion entre pernos).
- `nb...`: numero de repeticiones del patron.

## 6) Inputs de pernos - Grupo 2 (ala con platina 2)

### `bolt_shape_2`
Tamano nominal del perno del grupo de ala.

### `bolt_thread_condition_2`
Condicion de rosca del grupo de ala respecto al plano de corte.

### `bolt_fabrication_standard_2`
Norma de fabricacion del perno del grupo de ala.

### `bolt_description_2`
Descripcion complementaria del perno del grupo de ala.

### `bolt_tightening_type`
Tipo de apriete del perno del grupo 2: `pretensioned` o `snug_tight`.

### Ubicacion del patron de pernos del ala

#### `Le2_x1`
Distancia horizontal desde un borde longitudinal de platina 2 hasta la primera columna.

#### `Le2_x2`
Distancia horizontal desde el borde longitudinal opuesto hasta la ultima columna.

#### `S2_x`
Separacion horizontal entre columnas del grupo 2.

#### `Le2_z1`
Distancia vertical desde borde inferior de platina 2 hasta la fila inferior.

#### `Le2_z2`
Distancia vertical desde borde superior de platina 2 hasta la fila superior.

#### `S2_z1`
Separacion vertical entre filas en zona inferior del patron.

#### `S2_z2`
Separacion vertical entre filas en zona superior del patron.

Nota:
- No se asume separacion vertical uniforme en grupo 2.
- No se asume simetria automatica salvo indicacion explicita.

#### `nb2_x`
Numero de columnas en direccion `x`.

#### `nb2_z`
Numero de filas de pernos en direccion `z` (ancho de ala) conectadas a **una viga**.
En la conexion completa (dos vigas), el total de filas equivalentes es `2*nb2_z`.

## 7) Reglas de interpretacion obligatorias

1. No confundir dimensiones de placa, distancias a borde, separaciones y numero de filas/columnas.
2. No asumir por defecto: agujero estandar, rosca fuera del plano de corte, separaciones uniformes, o simetria.
3. Los inputs de ubicacion definen completamente la geometria del patron de pernos.
4. Ante ambiguedad, conservar la interpretacion consistente con:
   - Grupo 1: conexion de alma.
   - Grupo 2: conexion de ala.
   - `x = horizontal`, vertical = vertical.
5. En implementaciones de codigo, documentar con docstrings/comentarios tecnicos el significado fisico de cada input.
