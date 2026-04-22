# Memoria de Calculo

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Familia: `Fully_Restrained_Moment`
- Tipo: `bbmb_splice`
- Estado global: `FAIL`

## Revision conexion: Viga

### Punto 1 - Revision geometrica de detalle (detailing checks)

### Chequeo 1.1 - Distancia minima a borde Le1_x1 para agujero estandar (`Le1_x1`)

- Ambito: `VIGA`
- Verificacion: `Le1_x1 >= max(Le_min, 5*(8*db.1+2mm)); 25.4 mm >= 35 mm`
- Clausula: `AISC 360-22 Tabla J3.4 + Recomendacion del Manual AISC (metrico) | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🔴 No cumple

### Chequeo 1.2 - Distancia maxima a borde Le1_x1 (`Le1_x1`)

- Ambito: `VIGA`
- Verificacion: `Le1_x1 <= Le_max; 25.4 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.3 - Distancia Le1.y3 no menor que kdes del catalogo (`Le1.y3`)

- Ambito: `VIGA`
- Verificacion: `Le1.y3 >= kdes; 25 mm >= 21 mm`
- Clausula: `Criterio solicitado por usuario + catalogo de secciones | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.4 - Factor de rezago de cortante 1 (U1) no mayor que 1 (`U1`)

- Ambito: `VIGA`
- Verificacion: `U1 <= 1.0; 0.95 ratio <= 1 ratio`
- Clausula: `Criterio solicitado por usuario | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Nota tecnica - Geometria

- Ambito: `VIGA`
- Clausula: `Criterio solicitado por usuario | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Separacion entre vigas (alpha): `25.4 mm`
- Tolerancia de fabricacion en longitud de viga (Tlvg): `6.35 mm`
- Referencia tolerancia: `AISC 303-22`
- Separacion horizontal entre columnas de pernos del alma (S1.x): `76.2 mm`
- Distancia de borde en direccion X del grupo de pernos del alma (Le1.x1): `25.4 mm`
- Formula: `Le1.x1' = Le1.x1 - Tlvg`
- Distancia de borde ajustada (Le1.x1'): `19.05 mm`
- Altura de viga (dvg): `450 mm`
- Distancia vertical entre cara exterior de aleta inferior y fila inferior de pernos (Le1.y3): `25 mm`
- Formula: `Le1.y4 = dvg - Le1.y3`
- Distancia complementaria vertical (Le1.y4): `425 mm`
- Diametro de perforacion para pernos 1 (dh.1): `17.46 mm`
- Diametro de perforacion para pernos 2 (dh.2): `20.64 mm`
- Formula Area neta de cortante 1: `Anv.y1.vg = tw*(d-nb1.y*(dh.1+1.6mm))`
- Area neta de cortante 1 (Anv.y1.vg): `2557.46 mm2`
- Formula Area neta a traccion 1: `Ant.x1.1 = tw*(d-nb1.y*(dh.1+1.6mm))`
- Area neta a traccion 1 (Ant.x1.vg): `2557.46 mm2`
- Formula factor de rezago de cortante 1: `si nb1.x > 1 -> U.1 = 1 - 0.5*tw/((nb1.x-1)*S1.x)`
- Factor de rezago de cortante 1 (U11): `0.95`


## Revision conexion: Platina 1

### Punto 1 - Revision geometrica de detalle (detailing checks)

### Chequeo 1.1 - Altura de platina 1 no supera T del catalogo del perfil (`hp1`)

- Ambito: `PLATINA_1`
- Verificacion: `hp1 <= T; 431 mm <= 394 mm`
- Clausula: `Indicacion de diseno del usuario (constructivo) + catalogo de secciones | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🔴 No cumple

### Nota tecnica - Formulas geometricas (Platina 1)

- Ambito: `PLATINA_1`
- Clausula: `Criterio solicitado por usuario | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Formula hp1: `hp1 = Le1.y1 + Le1.y2 + (nb1.y - 1) * S1.y`
- hp1 calculado: `431 mm`
- Formula bp1: `bp1 = Le1.x1 + Le1.x2 + alpha + 2 * (nb1.x - 1) * S1.x`
- bp1 calculado: `238.2 mm`

### Nota tecnica - Diametro de perforacion (Platina 1)

- Ambito: `PLATINA_1`
- Clausula: `AISC 360-22 Table J3.3 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Formula: `dh = d + 1/16 in (db<=7/8 in) else dh = d + 1/8 in`
- db.1: `15.88 mm`
- dh.1: `17.46 mm`
- Incremento aplicado (in): `0.06`


## Revision conexion: Pernos 1

### Punto 1 - Revision geometrica de detalle (detailing checks)

### Chequeo 1.1 - Separacion minima entre pernos del alma en direccion X (`S1_x`)

- Ambito: `PERNOS_1`
- Verificacion: `S1_x >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `AISC 360-22 J3.3 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.2 - Separacion maxima entre pernos del alma en direccion X (`S1_x`)

- Ambito: `PERNOS_1`
- Verificacion: `S1_x <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.3 - Separacion minima entre pernos del alma en direccion Y (`S1_y`)

- Ambito: `PERNOS_1`
- Verificacion: `S1_y >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `AISC 360-22 J3.3 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.4 - Separacion maxima entre pernos del alma en direccion Y (`S1_y`)

- Ambito: `PERNOS_1`
- Verificacion: `S1_y <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.5 - Distancia minima a borde Le1_x2 para agujero estandar (`Le1_x2`)

- Ambito: `PERNOS_1`
- Verificacion: `Le1_x2 >= max(Le_min, 5*(8*db.1+2mm)); 35 mm >= 35 mm`
- Clausula: `AISC 360-22 Tabla J3.4 + Recomendacion del Manual AISC (metrico) | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.6 - Distancia maxima a borde Le1_x2 (`Le1_x2`)

- Ambito: `PERNOS_1`
- Verificacion: `Le1_x2 <= Le_max; 35 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.7 - Distancia minima a borde Le1_y1 para agujero estandar (`Le1_y1`)

- Ambito: `PERNOS_1`
- Verificacion: `Le1_y1 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `AISC 360-22 Tabla J3.4 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.8 - Distancia maxima a borde Le1_y1 (`Le1_y1`)

- Ambito: `PERNOS_1`
- Verificacion: `Le1_y1 <= Le_max; 25 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.9 - Distancia minima a borde Le1_y2 para agujero estandar (`Le1_y2`)

- Ambito: `PERNOS_1`
- Verificacion: `Le1_y2 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `AISC 360-22 Tabla J3.4 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.10 - Distancia maxima a borde Le1_y2 (`Le1_y2`)

- Ambito: `PERNOS_1`
- Verificacion: `Le1_y2 <= Le_max; 25 mm <= 91.44 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.11 - Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 1) (`Tb,min,1`)

- Ambito: `PERNOS_1`
- Verificacion: `Tb,min,1 = Tabla J3.1; 84.52 kN = 84.52 kN`
- Clausula: `AISC 360-22 Tabla J3.1 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Nota tecnica - Propiedades del perno (Grupo 1)

- Ambito: `PERNOS_1`
- Clausula: `Catalogo de pernos + inputs del caso | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Perno: `P5/8"X1-3/4"`
- Clasificacion: `Grupo 150`
- Norma de fabricacion: `ASTM A325`
- Condicion de rosca: `N`
- Tipo de apriete: `pretensioned`
- Diametro nominal (db.1): `15.88 mm`
- Longitud de vastago: `44.45 mm`
- Width across flats: `26.99 mm`
- Diametro de cabeza: `33.34 mm`
- Altura de cabeza: `9.92 mm`


### Punto 2 - Metodo ICR/Elastic

- Metodo seleccionado: `icr`
- Px: `0 kN`
- Py: `250 kN`
- ex: `152.4 mm`
- ey: `0 mm`
- Fuente excentricidad: `splice_formula_ex_plus_input_ey`
- Mz: `38.1 kN-m`
- Demanda (metodo activo): `250 kN`
- Capacidad (metodo activo): `2361.63 kN`
- DCR (metodo activo): `0.11`
- Residual final ICR: `0.01`
- Iteraciones ICR: `18`
- Coeficiente Cu (ICR): `7.17`
- Clausula: `Metodo configurable de pernos grupo 1 (ICR / Elastic) | Documento: AISC 360-22 (motor interno ICR/Elastic) | Codigo: AISC360.J3.bbmb_splice.step2_pernos1_method`
- Resultado: 🟢 Cumple

## Revision conexion: Platina 2

### Punto 1 - Revision geometrica de detalle (detailing checks)

### Chequeo 1.1 - Ancho de platina 2 no supera bf del catalogo del perfil (`bp2`)

- Ambito: `PLATINA_2`
- Verificacion: `bp2 <= bf; 110 mm <= 152 mm`
- Clausula: `Indicacion de diseno del usuario (constructivo) + catalogo de secciones | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Nota tecnica - Formulas geometricas (Platina 2)

- Ambito: `PLATINA_2`
- Clausula: `Criterio solicitado por usuario | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Formula bp2: `bp2 = Le2.z2 + Le2.z1 + S2.z2 + (nb2.z - 2) * S2.z1`
- bp2 calculado: `160 mm`
- Formula lp2: `lp2 = 2 * (Le2.x1 + Le2.x2) + alpha + 2 * (nb2.x - 1) * S2.x + alpha`
- lp2 calculado: `610.8 mm`

### Nota tecnica - Diametro de perforacion (Platina 2)

- Ambito: `PLATINA_2`
- Clausula: `AISC 360-22 Table J3.3 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Formula: `dh = d + 1/16 in (db<=7/8 in) else dh = d + 1/8 in`
- db.2: `19.05 mm`
- dh.2: `20.64 mm`
- Incremento aplicado (in): `0.06`


## Revision conexion: Pernos 2

### Punto 1 - Revision geometrica de detalle (detailing checks)

### Chequeo 1.1 - Separacion minima entre pernos del ala en direccion X (`S2_x`)

- Ambito: `PERNOS_2`
- Verificacion: `S2_x >= Smin; 60 mm >= 57.15 mm`
- Clausula: `AISC 360-22 J3.3 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.2 - Separacion maxima entre pernos del ala en direccion X (`S2_x`)

- Ambito: `PERNOS_2`
- Verificacion: `S2_x <= Smax; 60 mm <= 259.2 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.3 - Separacion minima entre pernos del ala en direccion Z (S2_z1) (`S2_z1`)

- Ambito: `PERNOS_2`
- Verificacion: `S2_z1 >= Smin; 40 mm >= 57.15 mm`
- Clausula: `AISC 360-22 J3.3 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🔴 No cumple

### Chequeo 1.4 - Separacion maxima entre pernos del ala en direccion Z (S2_z1) (`S2_z1`)

- Ambito: `PERNOS_2`
- Verificacion: `S2_z1 <= Smax; 40 mm <= 259.2 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.5 - Distancia minima a borde Le2_x1 para agujero estandar (`Le2_x1`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_x1 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.6 - Distancia maxima a borde Le2_x1 (`Le2_x1`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_x1 <= Le_max; 50 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.7 - Distancia minima a borde Le2_x2 para agujero estandar (`Le2_x2`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_x2 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.8 - Distancia maxima a borde Le2_x2 (`Le2_x2`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_x2 <= Le_max; 50 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.9 - Distancia minima a borde Le2_z1 para agujero estandar (`Le2_z1`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_z1 >= Le_min; 30 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.10 - Distancia maxima a borde Le2_z1 (`Le2_z1`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_z1 <= Le_max; 30 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.11 - Distancia minima a borde Le2_z2 para agujero estandar (`Le2_z2`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_z2 >= Le_min; 40 mm >= 25.4 mm`
- Clausula: `AISC 360-22 Tabla J3.4 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.12 - Distancia maxima a borde Le2_z2 (`Le2_z2`)

- Ambito: `PERNOS_2`
- Verificacion: `Le2_z2 <= Le_max; 40 mm <= 129.6 mm`
- Clausula: `AISC 360-22 J3.6 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Chequeo 1.13 - Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 2) (`Tb,min,2`)

- Ambito: `PERNOS_2`
- Verificacion: `Tb,min,2 = Tabla J3.1; 124.55 kN = 124.55 kN`
- Clausula: `AISC 360-22 Tabla J3.1 | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Resultado: 🟢 Cumple

### Nota tecnica - Propiedades del perno (Grupo 2)

- Ambito: `PERNOS_2`
- Clausula: `Catalogo de pernos + inputs del caso | Documento: AISC 360-22 | Codigo: AISC360.J3.bbmb_splice.step1_detailing_viga`
- Perno: `P3/4"X1-3/4"`
- Clasificacion: `Grupo 150`
- Norma de fabricacion: `ASTM A325`
- Condicion de rosca: `N`
- Tipo de apriete: `pretensioned`
- Diametro nominal (db.2): `19.05 mm`
- Longitud de vastago: `44.45 mm`
- Width across flats: `31.75 mm`
- Diametro de cabeza: `39.69 mm`
- Altura de cabeza: `11.91 mm`
