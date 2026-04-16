# Memoria de Calculo

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Familia: `Fully_Restrained_Moment`
- Tipo: `bbmb_splice`
- Estado global: `FAIL`

## Revision conexion: Viga

### Punto 1 - Revision geometrica de detalle (detailing checks)

#### Ambito: `PERNOS_1`

### Chequeo 1.1 - Separacion minima entre pernos del alma en direccion X (`S1_x`)
- Ambito: `PERNOS_1`
- Verificacion: `S1_x >= Smin; 60 mm >= 47.62 mm`
- Clausula: `AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

### Chequeo 1.2 - Separacion maxima entre pernos del alma en direccion X (`S1_x`)
- Ambito: `PERNOS_1`
- Verificacion: `S1_x <= Smax; 60 mm <= 182.88 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.3 - Separacion minima entre pernos del alma en direccion Y (`S1_y`)
- Ambito: `PERNOS_1`
- Verificacion: `S1_y >= Smin; 60 mm >= 47.62 mm`
- Clausula: `AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

### Chequeo 1.4 - Separacion maxima entre pernos del alma en direccion Y (`S1_y`)
- Ambito: `PERNOS_1`
- Verificacion: `S1_y <= Smax; 60 mm <= 182.88 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.5 - Distancia minima a borde Le1_x1 para agujero estandar (`Le1_x1`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_x1 >= Le_min; 35 mm >= 22.22 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.6 - Distancia maxima a borde Le1_x1 (`Le1_x1`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_x1 <= Le_max; 35 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.7 - Distancia minima a borde Le1_x2 para agujero estandar (`Le1_x2`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_x2 >= Le_min; 35 mm >= 22.22 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.8 - Distancia maxima a borde Le1_x2 (`Le1_x2`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_x2 <= Le_max; 35 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.9 - Distancia minima a borde Le1_y1 para agujero estandar (`Le1_y1`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_y1 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.10 - Distancia maxima a borde Le1_y1 (`Le1_y1`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_y1 <= Le_max; 25 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.11 - Distancia minima a borde Le1_y2 para agujero estandar (`Le1_y2`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_y2 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.12 - Distancia maxima a borde Le1_y2 (`Le1_y2`)
- Ambito: `PERNOS_1`
- Verificacion: `Le1_y2 <= Le_max; 25 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.13 - Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 1) (`Tb,min,1`)
- Ambito: `PERNOS_1`
- Verificacion: `Tb,min,1 = Tabla J3.1; 84.52 kN = 84.52 kN`
- Clausula: `AISC 360-22 Tabla J3.1`
- Resultado: 🟢 Cumple

#### Ambito: `PERNOS_2`

### Chequeo 1.14 - Separacion minima entre pernos del ala en direccion X (`S2_x`)
- Ambito: `PERNOS_2`
- Verificacion: `S2_x >= Smin; 60 mm >= 57.15 mm`
- Clausula: `AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

### Chequeo 1.15 - Separacion maxima entre pernos del ala en direccion X (`S2_x`)
- Ambito: `PERNOS_2`
- Verificacion: `S2_x <= Smax; 60 mm <= 259.2 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.16 - Separacion minima entre pernos del ala en direccion Z (S2_z1) (`S2_z1`)
- Ambito: `PERNOS_2`
- Verificacion: `S2_z1 >= Smin; 40 mm >= 57.15 mm`
- Clausula: `AISC 360-22 J3.3`
- Resultado: 🔴 No cumple

### Chequeo 1.17 - Separacion maxima entre pernos del ala en direccion Z (S2_z1) (`S2_z1`)
- Ambito: `PERNOS_2`
- Verificacion: `S2_z1 <= Smax; 40 mm <= 259.2 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.18 - Distancia minima a borde Le2_x1 para agujero estandar (`Le2_x1`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_x1 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.19 - Distancia maxima a borde Le2_x1 (`Le2_x1`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_x1 <= Le_max; 50 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.20 - Distancia minima a borde Le2_x2 para agujero estandar (`Le2_x2`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_x2 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.21 - Distancia maxima a borde Le2_x2 (`Le2_x2`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_x2 <= Le_max; 50 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.22 - Distancia minima a borde Le2_z1 para agujero estandar (`Le2_z1`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_z1 >= Le_min; 30 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.23 - Distancia maxima a borde Le2_z1 (`Le2_z1`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_z1 <= Le_max; 30 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.24 - Distancia minima a borde Le2_z2 para agujero estandar (`Le2_z2`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_z2 >= Le_min; 40 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.25 - Distancia maxima a borde Le2_z2 (`Le2_z2`)
- Ambito: `PERNOS_2`
- Verificacion: `Le2_z2 <= Le_max; 40 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### Chequeo 1.26 - Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 2) (`Tb,min,2`)
- Ambito: `PERNOS_2`
- Verificacion: `Tb,min,2 = Tabla J3.1; 124.55 kN = 124.55 kN`
- Clausula: `AISC 360-22 Tabla J3.1`
- Resultado: 🟢 Cumple

#### Ambito: `PLATINA_2`

### Chequeo 1.27 - Ancho de platina 2 no supera bf del catalogo del perfil (`bp2`)
- Ambito: `PLATINA_2`
- Verificacion: `bp2 <= bf; 110 mm <= 152 mm`
- Clausula: `Indicacion de diseno del usuario (constructivo) + catalogo de secciones`
- Resultado: 🟢 Cumple

#### Ambito: `VIGA`

### Chequeo 1.28 - Altura de platina 1 no supera T del catalogo del perfil (`hp1`)
- Ambito: `VIGA`
- Verificacion: `hp1 <= T; 350 mm <= 394 mm`
- Clausula: `Indicacion de diseno del usuario (constructivo) + catalogo de secciones`
- Resultado: 🟢 Cumple

### Nota tecnica - Formulas geometricas (dato comun)

- Ambito: `VIGA`
- Clausula: `Criterio solicitado por usuario`
- alpha = sep: `10 mm`

### Nota tecnica - Formulas geometricas (Platina 1)

- Ambito: `PLATINA_1`
- Clausula: `Criterio solicitado por usuario`
- Formula hp1: `hp1 = Le1.y1 + Le1.y2 + (nb1.y - 1) * S1.y`
- hp1 calculado: `350 mm`
- Formula bp1: `bp1 = Le1.x1 + Le1.x2 + alpha + 2 * (nb1.x - 1) * S1.x`
- bp1 calculado: `200 mm`

### Nota tecnica - Formulas geometricas (Platina 2)

- Ambito: `PLATINA_2`
- Clausula: `Criterio solicitado por usuario`
- Formula bp2: `bp2 = Le2.z2 + Le2.z1 + S2.z2 + (nb2.z - 2) * S2.z1`
- bp2 calculado: `160 mm`
- Formula lp2: `lp2 = 2 * (Le2.x1 + Le2.x2) + alpha + 2 * (nb2.x - 1) * S2.x + alpha`
- lp2 calculado: `580 mm`


## Revision conexion: Platina 1

## Revision conexion: Pernos 1

## Revision conexion: Platina 2

## Revision conexion: Pernos 2
