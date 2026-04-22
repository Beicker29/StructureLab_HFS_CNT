# Memoria de Calculo

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Familia: `Fully_Restrained_Moment`
- Tipo: `bbmb_splice`
- Estado global: `No cumple`

## Revision conexion: Viga

### Punto 1 - Revision geometrica de detalle (detailing checks)

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Distancia minima a borde Le_blt_web_x1 para agujero estandar (`Le_blt_web_x1`)

- Ambito: `VIGA`
- Verificacion: `Le_blt_web_x1 >= max(Le_min, 5*(8*db.1+2mm)); 25.4 mm >= 35 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4 + Recomendacion del Manual AISC (metrico)`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.2 - Distancia maxima a borde Le_blt_web_x1 (`Le_blt_web_x1`)

- Ambito: `VIGA`
- Verificacion: `Le_blt_web_x1 <= Le_max; 25.4 mm <= 91.44 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.3 - Distancia Le_blt_web_y3 no menor que kdes_vg del catalogo (`Le_blt_web_y3`)

- Ambito: `VIGA`
- Verificacion: `Le_blt_web_y3 >= kdes_vg; 25 mm >= 21 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: Criterio solicitado por usuario + catalogo de secciones`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.4 - Factor de rezago de cortante 1 (U1) no mayor que 1 (`U1`)

- Ambito: `VIGA`
- Verificacion: `U1 <= 1.0; 0.95 adim <= 1 adim`
- Clausula: `Documento: AISC 360-22 | Seccion: Criterio solicitado por usuario`
- Resultado: 🟢 Cumple

### Nota tecnica - Geometria

- Ambito: `VIGA`
- Clausula: `Documento: AISC 360-22 | Seccion: Criterio solicitado por usuario`
- Separacion entre vigas (gap_sp): `25.4 mm`
- Tolerancia de fabricacion en longitud de viga (tol_L_vg): `6.35 mm`
- Referencia tolerancia: `AISC 303-22`
- Separacion horizontal entre columnas de pernos del alma (g_blt_web): `76.2 mm`
- Distancia de borde en direccion X del grupo de pernos del alma (Le_blt_web_x1): `25.4 mm`
- Formula: `Le_blt_web_x1' = Le_blt_web_x1 - tol_L_vg`
- Distancia de borde ajustada (Le_blt_web_x1'): `19.05 mm`
- Altura de viga (d_vg): `450 mm`
- Distancia vertical entre cara exterior de aleta inferior y fila inferior de pernos (Le_blt_web_y3): `25 mm`
- Formula: `Le_blt_web_y4 = d_vg - Le_blt_web_y3`
- Distancia complementaria vertical (Le_blt_web_y4): `425 mm`
- Diametro de perforacion para pernos 1 (dh.1): `17.46 mm`
- Diametro de perforacion para pernos 2 (dh.2): `20.64 mm`
- Formula Area neta de cortante 1: `Anv.y1.vg = tw_vg*(d_vg-n_blt_web_y*(dh_plt_web+1.6mm))`
- Area neta de cortante 1 (Anv.y1.vg): `2557.46 mm2`
- Formula Area neta a traccion 1: `Ant.x1.vg = tw_vg*(d_vg-n_blt_web_y*(dh_plt_web+1.6mm))`
- Area neta a traccion 1 (Ant.x1.vg): `2557.46 mm2`
- Formula factor de rezago de cortante 1: `si n_blt_web_x > 1 -> U1 = 1 - 0.5*tw_vg/((n_blt_web_x-1)*g_blt_web)`
- Factor de rezago de cortante 1 (U1): `0.95`


## Revision conexion: Platina 1

### Punto 1 - Revision geometrica de detalle (detailing checks)

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Altura de platina de alma no supera T_vg del catalogo (`B_plt_web`)

- Ambito: `PLATINA_1`
- Verificacion: `B_plt_web <= T_vg; 431 mm <= 394 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: Criterio de detallado solicitado por usuario`
- Resultado: 🔴 No cumple

### Nota tecnica - Formulas geometricas (Platina 1)

- Ambito: `PLATINA_1`
- Clausula: `Documento: AISC 360-22 | Seccion: Nomenclatura oficial splice`
- Formula hp1: `B_plt_web = Le_blt_web_y1 + Le_blt_web_y2 + (n_blt_web_y - 1)*p_blt_web`
- hp1 calculado: `431 mm`
- Formula bp1: `L_plt_web = 2*(Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web + Le_blt_web_x2) + gap_sp`
- bp1 calculado: `238.2 mm`

### Nota tecnica - Diametro de perforacion (Platina 1)

- Ambito: `PLATINA_1`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.3`
- Formula: `dh_plt_web = db_blt_web + 1/16 in (db<=7/8 in) else +1/8 in`
- db_blt_web: `15.88 mm`
- dh_plt_web: `17.46 mm`
- Incremento aplicado (in): `0.06`


## Revision conexion: Pernos 1

### Punto 1 - Revision geometrica de detalle (detailing checks)

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Separacion minima entre pernos del alma en direccion X (`g_blt_web`)

- Ambito: `PERNOS_1`
- Verificacion: `g_blt_web >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.2 - Separacion maxima entre pernos del alma en direccion X (`g_blt_web`)

- Ambito: `PERNOS_1`
- Verificacion: `g_blt_web <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.3 - Separacion minima entre pernos del alma en direccion Z (`p_blt_web`)

- Ambito: `PERNOS_1`
- Verificacion: `p_blt_web >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.4 - Separacion maxima entre pernos del alma en direccion Z (`p_blt_web`)

- Ambito: `PERNOS_1`
- Verificacion: `p_blt_web <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.5 - Distancia minima a borde Le_blt_web_x2 para agujero estandar (`Le_blt_web_x2`)

- Ambito: `PERNOS_1`
- Verificacion: `Le_blt_web_x2 >= max(Le_min, 5*(8*db.1+2mm)); 35 mm >= 35 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4 + Recomendacion del Manual AISC (metrico)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.6 - Distancia minima a borde Le_blt_web_y1 para agujero estandar (`Le_blt_web_y1`)

- Ambito: `PERNOS_1`
- Verificacion: `Le_blt_web_y1 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.7 - Distancia minima a borde Le_blt_web_y2 para agujero estandar (`Le_blt_web_y2`)

- Ambito: `PERNOS_1`
- Verificacion: `Le_blt_web_y2 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.8 - Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 1) (`Tb,min,1`)

- Ambito: `PERNOS_1`
- Verificacion: `Tb,min,1 = Tabla J3.1; 84.52 kN = 84.52 kN`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.1`
- Resultado: 🟢 Cumple

### Nota tecnica - Propiedades del perno (Grupo 1)

- Ambito: `PERNOS_1`
- Clausula: `Documento: AISC 360-22 | Seccion: Catalogo de pernos + inputs del caso`
- Perno: `P5/8"X1-3/4"`
- Clasificacion: `Grupo 150`
- Norma de fabricacion: `ASTM A325`
- Condicion de rosca: `N`
- Tipo de apriete: `pretensioned`
- Diametro nominal (db_blt_web): `15.88 mm`
- Longitud de vastago: `44.45 mm`
- Width across flats: `26.99 mm`
- Diametro de cabeza: `33.34 mm`
- Altura de cabeza: `9.92 mm`


### Punto 2 - Metodo ICR/Elastic

- Metodo seleccionado: `icr`
- Pu_sp: `0 kN`
- Vu2_sp: `250 kN`
- ex_blt_web: `152.4 mm`
- ey_blt_web: `0 mm`
- Fuente excentricidad: `splice_formula_ex_plus_input_ey`
- Muz_blt_web: `38.1 kN-m`
- Demanda (metodo activo): `250 kN`
- Capacidad (metodo activo): `2361.63 kN`
- DCR (metodo activo): `0.11`
- Residual final ICR: `0.01`
- Iteraciones ICR: `18`
- Coeficiente Cu (ICR): `7.17`
- Clausula: `Documento: AISC 360-22 (motor interno ICR/Elastic) | Seccion: Metodo configurable de pernos grupo 1 (ICR / Elastic)`
- Resultado: 🟢 Cumple

## Revision conexion: Platina 2

### Punto 1 - Revision geometrica de detalle (detailing checks)

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Ancho de platina de ala no supera bf_vg del catalogo (`B_plt_flange`)

- Ambito: `PLATINA_2`
- Verificacion: `B_plt_flange <= bf_vg; 162 mm <= 152 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: Criterio de detallado solicitado por usuario`
- Resultado: 🔴 No cumple

### Nota tecnica - Formulas geometricas (Platina 2)

- Ambito: `PLATINA_2`
- Clausula: `Documento: AISC 360-22 | Seccion: Nomenclatura oficial splice`
- Formula bp2: `B_plt_flange = bf_vg - 2*Le_blt_flange_z3 + Le_blt_flange_z1 + Le_blt_flange_z2`
- bp2 calculado: `162 mm`
- Formula lp2: `L_plt_flange = 2*(Le_blt_flange_x1 + (n_blt_flange_x - 1)*p_blt_flange + Le_blt_flange_x2) + gap_sp`
- lp2 calculado: `585.4 mm`

### Nota tecnica - Diametro de perforacion (Platina 2)

- Ambito: `PLATINA_2`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.3`
- Formula: `dh_plt_flange = db_blt_flange + 1/16 in (db<=7/8 in) else +1/8 in`
- db_blt_flange: `19.05 mm`
- dh_plt_flange: `20.64 mm`
- Incremento aplicado (in): `0.06`


## Revision conexion: Pernos 2

### Punto 1 - Revision geometrica de detalle (detailing checks)

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Separacion minima entre pernos del ala en direccion X (`p_blt_flange`)

- Ambito: `PERNOS_2`
- Verificacion: `p_blt_flange >= Smin; 60 mm >= 57.15 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.2 - Separacion maxima entre pernos del ala en direccion X (`p_blt_flange`)

- Ambito: `PERNOS_2`
- Verificacion: `p_blt_flange <= Smax; 60 mm <= 259.2 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.3 - Separacion minima entre pernos del ala en direccion Z (`g_blt_flange`)

- Ambito: `PERNOS_2`
- Verificacion: `g_blt_flange >= Smin; 40 mm >= 57.15 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.4 - Separacion maxima entre pernos del ala en direccion Z (`g_blt_flange`)

- Ambito: `PERNOS_2`
- Verificacion: `g_blt_flange <= Smax; 40 mm <= 259.2 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.5 - Distancia minima a borde Le_blt_flange_x1 para agujero estandar (`Le_blt_flange_x1`)

- Ambito: `PERNOS_2`
- Verificacion: `Le_blt_flange_x1 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.6 - Distancia minima a borde Le_blt_flange_x2 para agujero estandar (`Le_blt_flange_x2`)

- Ambito: `PERNOS_2`
- Verificacion: `Le_blt_flange_x2 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.7 - Distancia minima a borde Le_blt_flange_z1 para agujero estandar (`Le_blt_flange_z1`)

- Ambito: `PERNOS_2`
- Verificacion: `Le_blt_flange_z1 >= Le_min; 30 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.8 - Distancia minima a borde Le_blt_flange_z2 para agujero estandar (`Le_blt_flange_z2`)

- Ambito: `PERNOS_2`
- Verificacion: `Le_blt_flange_z2 >= Le_min; 40 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.9 - Distancia minima a borde Le_blt_flange_z3 para agujero estandar (`Le_blt_flange_z3`)

- Ambito: `PERNOS_2`
- Verificacion: `Le_blt_flange_z3 >= Le_min; 30 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.10 - Nota tecnica J3.1 - Fuerza minima de pretension por perno (grupo 2) (`Tb,min,2`)

- Ambito: `PERNOS_2`
- Verificacion: `Tb,min,2 = Tabla J3.1; 124.55 kN = 124.55 kN`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.1`
- Resultado: 🟢 Cumple

### Nota tecnica - Propiedades del perno (Grupo 2)

- Ambito: `PERNOS_2`
- Clausula: `Documento: AISC 360-22 | Seccion: Catalogo de pernos + inputs del caso`
- Perno: `P3/4"X1-3/4"`
- Clasificacion: `Grupo 150`
- Norma de fabricacion: `ASTM A325`
- Condicion de rosca: `N`
- Tipo de apriete: `pretensioned`
- Diametro nominal (db_blt_flange): `19.05 mm`
- Longitud de vastago: `44.45 mm`
- Width across flats: `31.75 mm`
- Diametro de cabeza: `39.69 mm`
- Altura de cabeza: `11.91 mm`
