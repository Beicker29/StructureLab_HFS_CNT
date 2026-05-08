# Memoria de Cálculo

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Familia: `Fully_Restrained_Moment`
- Tipo: `bbmb_splice`
- Estado global: `🔴 No cumple`

## Paso 1 - Propiedades geométricas, mecánicas y fabricacion

Propiedades organizadas por ambito.

### 1.1 Ámbito `VIGA`

#### 1.1.1 Resumen de geometria

- Perfil de viga (shape_vg) (inp): `W18X35`
- Tipo de acero de viga (steel_vg) (inp): `ASTM A572 Gr 50`
- Condicion superficial del ala (cond_sup_vg) (inp): `painted`
- Condicion ambiental ala (cond_amb_vg) (inp): `non_corrosive`
- Seleccion C3 para constructibilidad (c3_clearance_type) (inp): `circular`
- Fluencia de viga (Fy_vg): `345 MPa`
- Resistencia ultima de viga (Fu_vg): `450 MPa`
- Modulo elastico de viga (E_vg): `200000 MPa`
- Altura total de la seccion (d_vg): `450 mm`
- Altura libre del alma (T_vg): `394 mm`
- Ancho del ala (bf_vg): `152 mm`
- Ancho del ala para detallado (bfdet_vg): `152 mm`
- Espesor del alma (tw_vg): `7.62 mm`
- Espesor del alma para detallado (twdet_vg): `7.62 mm`
- Espesor del ala (tf_vg): `10.8 mm`
- Espesor del ala para detallado (tfdet_vg): `10.8 mm`
- Distancia k de diseno (kdes_vg): `21 mm`
- Distancia k detallada (kdet_vg): `21 mm`
- Distancia desde el eje del alma al inicio del radio interno de al viga (k1_vg): `19.1 mm`

#### 1.1.2 Resumen de geometria del alma

- Separacion entre vigas (gap_sp) (inp): `25.4 mm`
- Tolerancia de fabricacion en longitud de viga (tol_L_vg) (inp): `6.35 mm`
- Referencia tolerancia: `AISC 303-22`
- Numero de pernos en direccion X del alma (n_blt_web_x) (inp): `1`
- Separacion horizontal entre columnas de pernos del alma (g_blt_web) (inp): `76.2 mm`
- Distancia de borde en direccion X del grupo de pernos del alma (Le_blt_web_x1) (inp): `25.4 mm`
- Ecuacion coordenadas X de pernos del alma: `x_j_blt_web = Le_blt_web_x1 + j*g_blt_web`
- Rango del indice: `j = 0, 1, ..., n_blt_web_x - 1`
- Coordenadas en direccion X para pernos del alma (x_j_blt_web): `j=0: 25.4 mm`
- Distancia de borde ajustada (Le_blt_web_x1'): `19.05 mm`
- Numero de pernos en direccion Y del alma (n_blt_web_y) (inp): `6`
- Separacion vertical entre filas de pernos del alma (p_blt_web) (inp): `76.2 mm`
- Tipo de perforacion por pernos grupo 1 alma (type_hole_web) (inp): `standard`
- Distancia vertical entre cara exterior de aleta inferior y fila inferior de pernos (Le_blt_web_y3): `34.5 mm`
- Distancia neta respecto a kdet en alma (Le_blt_web_y3.1): `13.5 mm`
- Diametro de perforacion para pernos 1 (dh.1): `17.46 mm`

#### 1.1.3 Resumen de geometria de la aleta

- Numero de pernos en direccion X del ala (n_blt_flange_x) (inp): `4`
- Separacion entre filas de pernos del ala (p_blt_flange) (inp): `60 mm`
- Distancia de borde en direccion X del grupo de pernos del ala (Le_blt_flange_x1) (inp): `50 mm`
- Ecuacion coordenadas X de pernos de aleta: `x_k_blt_flange = Le_blt_flange_x1 + k*p_blt_flange`
- Rango del indice: `k = 0, 1, ..., n_blt_flange_x - 1`
- Coordenadas en direccion X para pernos de aleta (x_k_blt_flange): `k=0: 50 mm; k=1: 110 mm; k=2: 170 mm; k=3: 230 mm`
- Numero de pernos en na mitad de aleta en direccion Z de la aleta (n_blt_flange_z) (inp): `1`
- Distancia de borde en direccion Z del grupo de pernos del ala (Le_blt_flange_z1) (inp): `30 mm`
- Distancia complementaria de borde en aleta (Le_blt_flange_z4): `26.9 mm`
- Gage entre columnas de pernos del ala (g_blt_flange) (inp): `40 mm`
- Tipo de perforacion por pernos grupo 2 ala (type_hole_flange) (inp): `standard`
- Distancia util entre filas internas de pernos de aleta (g1_blt_flange): `92 mm`
- Despeje horizontal entre grupos de pernos (F_blt_flange): `32.69 mm`
- Diametro de perforacion para pernos 2 (dh.2): `20.64 mm`

#### 1.1.4 Formulas de cálculo

- Formula ajuste distancia de borde: `Le_blt_web_x1' = Le_blt_web_x1 - tol_L_vg`
- Formula distancia vertical borde ala/pernos alma: `Le_blt_web_y3 = 0.5*(d_vg - (n_blt_web_y - 1)*p_blt_web)`
- Formula distancia neta respecto a kdet en alma: `Le_blt_web_y3.1 = Le_blt_web_y3 - kdet_vg`
- Formula coordenadas X pernos de aleta: `x_k_blt_flange = Le_blt_flange_x1 + k*p_blt_flange`
- Formula distancia util entre filas internas de pernos de aleta: `g1_blt_flange = bf_vg - 2*(Le_blt_flange_z1 + (n_blt_flange_z - 1)*g_blt_flange)`
- Formula despeje horizontal entre grupos de pernos: `F_blt_flange = 0.5*g1_blt_flange - 0.5*tw_vg - t_plt_web`
- Formula distancia complementaria de borde en aleta: `Le_blt_flange_z4 = 0.5*bfdet_vg - (Le_blt_flange_z1 + k1_vg + (n_blt_flange_z - 1)*g_blt_flange)`

### 1.2 Ámbito `PLATINA_1`

#### 1.2.1 Resumen de geometria

- Tipo de acero de platina de alma (steel_plt_web) (inp): `ASTM A36`
- Fluencia de platina de alma (Fy_plt_web): `250 MPa`
- Resistencia ultima de platina de alma (Fu_plt_web): `400 MPa`
- Modulo elastico de platina de alma (E_plt_web): `200000 MPa`
- Tipo de perforacion por pernos grupo 1 alma (type_hole_plt_web) (inp): `standard`
- Condicion superficial platina alma (cond_sup_plt_web) (inp): `painted`
- Condicion ambiental platina alma (cond_amb_plt_web) (inp): `non_corrosive`
- Espesor de platina de alma (t_plt_web) (inp): `9.5 mm`
- Numero de pernos en direccion X del alma (n_plt_web_x) (inp): `1`
- Separacion horizontal entre columnas de pernos del alma (g_plt_web) (inp): `76.2 mm`
- Distancia al borde en direccion X de platina de alma (Le_plt_web_x2) (inp): `35 mm`
- Numero de pernos en direccion Y del alma (n_plt_web_y) (inp): `6`
- Separacion vertical entre filas de pernos del alma (p_plt_web) (inp): `76.2 mm`
- Distancia al borde inferior de platina de alma (Le_plt_web_y1) (inp): `25 mm`
- Distancia al borde superior de platina de alma (Le_plt_web_y2) (inp): `25 mm`
- Longitud de platina de alma (L_plt_web): `146.2 mm`
- Altura de platina de alma (H_plt_web): `431 mm`
- dh_plt_web: `17.46 mm`

#### 1.2.2 Formulas de cálculo

- Formula trazabilidad: `n_plt_web_x = n_blt_web_x`
- Formula trazabilidad: `g_plt_web = g_blt_web`
- Formula trazabilidad: `n_plt_web_y = n_blt_web_y`
- Formula trazabilidad: `p_plt_web = p_blt_web`
- Formula trazabilidad: `Le_plt_web_x2 = Le_blt_web_x2`
- Formula trazabilidad: `Le_plt_web_y1 = Le_blt_web_y1`
- Formula trazabilidad: `Le_plt_web_y2 = Le_blt_web_y2`
- Formula H_plt_web: `H_plt_web = Le_blt_web_y1 + Le_blt_web_y2 + (n_blt_web_y - 1)*p_blt_web`
- Formula L_plt_web: `L_plt_web = 2*(Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web + Le_blt_web_x2) + gap_sp`
- Formula dh_plt_web: `dh_plt_web = db_blt_web + 1/16 in (db<=7/8 in) else +1/8 in`

### 1.3 Ámbito `PERNOS_1`

#### 1.3.1 Resumen de geometria

- Tipo de acero/perno (shape_blt_web) (inp): `P5/8"X1-3/4"`
- Norma de fabricacion (inp): `ASTM A325`
- Clasificacion: `Grupo 120`
- Condicion de rosca (inp): `N`
- Tipo de apriete (inp): `pretensioned`
- Resistencia nominal a traccion (Fnt_blt_web): `620 MPa`
- Resistencia nominal a cortante (Fnv_blt_web): `370 MPa`
- Diametro nominal (db_blt_web): `15.88 mm`
- Longitud de vastago: `44.45 mm`
- Width across flats: `26.99 mm`
- Diametro de cabeza: `33.34 mm`
- Altura de cabeza: `9.92 mm`

### 1.4 Ámbito `PLATINA_2`

#### 1.4.1 Resumen de geometria

- Tipo de acero de platina de ala (steel_plt_flange) (inp): `ASTM A36`
- Fluencia de platina de ala (Fy_plt_flange): `250 MPa`
- Resistencia ultima de platina de ala (Fu_plt_flange): `400 MPa`
- Modulo elastico de platina de ala (E_plt_flange): `200000 MPa`
- Tipo de perforacion por pernos grupo 2 ala (type_hole_plt_flange) (inp): `standard`
- Condicion superficial platina ala (cond_sup_plt_flange) (inp): `painted`
- Condicion ambiental platina ala (cond_amb_plt_flange) (inp): `non_corrosive`
- Espesor de platina de ala (t_plt_flange) (inp): `19.05 mm`
- Numero de pernos en direccion X del ala (n_plt_flange_x) (inp): `4`
- Separacion entre filas de pernos del ala (p_plt_flange) (inp): `60 mm`
- Distancia al borde de la platina de ala en x (Le_plt_flange_x2) (inp): `50 mm`
- Numero de pernos en direccion Z del ala (n_plt_flange_z) (inp): `1`
- Gage entre columnas de pernos del ala (g_plt_flange) (inp): `40 mm`
- Distancia de borde interior 1 en direccion Z del ala (Le_plt_flange_z1) (inp): `30 mm`
- Distancia de borde interior 2 en direccion Z del ala (Le_plt_flange_z2) (inp): `40 mm`
- Distancia util entre filas internas de pernos de aleta (g1_plt_flange): `92 mm`
- Longitud de platina de ala (L_plt_flange): `585.4 mm`
- Ancho de platina de ala (B_plt_flange): `162 mm`
- dh_plt_flange: `20.64 mm`

#### 1.4.2 Formulas de cálculo

- Formula trazabilidad: `n_plt_flange_x = n_blt_flange_x`
- Formula trazabilidad: `p_plt_flange = p_blt_flange`
- Formula trazabilidad: `Le_plt_flange_x2 = Le_blt_flange_x2`
- Formula trazabilidad: `n_plt_flange_z = n_blt_flange_z`
- Formula trazabilidad: `g_plt_flange = g_blt_flange`
- Formula trazabilidad: `Le_plt_flange_z1 = Le_blt_flange_z1`
- Formula trazabilidad: `Le_plt_flange_z2 = Le_blt_flange_z2`
- Formula calculo: `g1_plt_flange = bf_vg - 2*(Le_blt_flange_z1 + (n_blt_flange_z - 1)*g_blt_flange)`
- Formula trazabilidad: `g1_plt_flange = g1_blt_flange`
- Formula B_plt_flange: `B_plt_flange = Le_blt_flange_z1 + Le_blt_flange_z2 + 2*(n_blt_flange_z - 1)*g_blt_flange + g1_blt_flange`
- Formula L_plt_flange: `L_plt_flange = 2*(Le_blt_flange_x1 + (n_blt_flange_x - 1)*p_blt_flange + Le_blt_flange_x2) + gap_sp`
- Formula dh_plt_flange: `dh_plt_flange = db_blt_flange + 1/16 in (db<=7/8 in) else +1/8 in`

### 1.5 Ámbito `PERNOS_2`

#### 1.5.1 Resumen de geometria

- Tipo de acero/perno (shape_blt_flange) (inp): `P3/4"X1-3/4"`
- Norma de fabricacion (inp): `ASTM A325`
- Clasificacion: `Grupo 120`
- Condicion de rosca (inp): `N`
- Tipo de apriete (inp): `pretensioned`
- Resistencia nominal a traccion (Fnt_blt_flange): `620 MPa`
- Resistencia nominal a cortante (Fnv_blt_flange): `370 MPa`
- Diametro nominal (db_blt_flange): `19.05 mm`
- Longitud de vastago: `44.45 mm`
- Width across flats: `31.75 mm`
- Diametro de cabeza: `39.69 mm`
- Altura de cabeza: `11.91 mm`

## Paso 2 - Revisiones de requerimientos de propiedades mecánicas y geométricas

### 2.1 Ámbito `VIGA`

#### Chequeo 2.1.1 - Separacion minima entre pernos del alma en direccion X (`g_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `g_blt_web >= max {2*C1, Smin}; 76.2 mm >= 60.32 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.3, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.2 - Separacion maxima entre pernos del alma en direccion X (`g_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `g_blt_web <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.3 - Distancia minima a borde Le_blt_web_x1 para agujero estandar (`Le_blt_web_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_x1 >= max {Le_min, C1}; 25.4 mm >= 30.16 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 Tabla J3.4, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🔴 No cumple

#### Chequeo 2.1.4 - Distancia maxima a borde Le_blt_web_x1 (`Le_blt_web_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_x1 <= Le_max; 25.4 mm <= 91.44 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.5 - Separacion minima entre pernos del alma en direccion Z (`p_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_web >= max {2*C1, Smin}; 76.2 mm >= 60.32 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.3, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.6 - Separacion maxima entre pernos del alma en direccion Z (`p_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_web <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.7 - Distancia minima a borde Le_blt_web_y3.1 para agujero estandar (`Le_blt_web_y3.1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_y3.1 >= max {Le_min, C1}; 13.5 mm >= 30.16 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 Tabla J3.4, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🔴 No cumple

#### Chequeo 2.1.8 - Distancia maxima a borde Le_blt_web_y3.1 (`Le_blt_web_y3.1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_y3.1 <= Le_max; 13.5 mm <= 91.44 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.9 - Separacion minima entre pernos del ala en direccion X (`p_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_flange >= max {2*C1, Smin}; 60 mm >= 60.32 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.3, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🔴 No cumple

#### Chequeo 2.1.10 - Separacion maxima entre pernos del ala en direccion X (`p_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_flange <= Smax; 60 mm <= 259.2 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.11 - Distancia minima a borde Le_blt_flange_x1 para agujero estandar (`Le_blt_flange_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_x1 >= max {Le_min, C1}; 50 mm >= 30.16 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 Tabla J3.4, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.12 - Distancia maxima a borde Le_blt_flange_x1 (`Le_blt_flange_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_x1 <= Le_max; 50 mm <= 129.6 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.13 - Distancia minima a borde Le_blt_flange_z1 para agujero estandar (`Le_blt_flange_z1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z1 >= Le_min; 30 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.14 - Distancia minima a borde Le_blt_flange_z1 para agujero estandar (`Le_blt_flange_z1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z1 >= max {Le_min, C1}; 30 mm >= 30.16 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 Tabla J3.4, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🔴 No cumple

#### Chequeo 2.1.15 - Distancia minima a borde Le_blt_flange_z4 para agujero estandar (`Le_blt_flange_z4`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z4 >= max {Le_min, C1}; 26.9 mm >= 30.16 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 Tabla J3.4, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🔴 No cumple

#### Chequeo 2.1.16 - Distancia maxima a borde Le_blt_flange_z4 (`Le_blt_flange_z4`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z4 <= Le_max; 26.9 mm <= 129.6 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.17 - Separacion minima entre pernos del ala en direccion Z (`g_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `n_blt_flange_z >= 2; 1 >= 2`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.3, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🟠 No aplica (cumple)

#### Chequeo 2.1.18 - Separacion maxima entre pernos del ala en direccion Z (`g_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `n_blt_flange_z >= 2; 1 >= 2`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟠 No aplica (cumple)

#### Chequeo 2.1.19 - Separacion minima entre pernos del ala en direccion Z (g1) (`g1_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `g1_blt_flange >= max {2*C1, Smin}; 92 mm >= 60.32 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.3, J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.20 - Separacion maxima entre pernos del ala en direccion Z (g1) (`g1_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `g1_blt_flange <= Smax; 92 mm <= 259.2 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.21 - Distancia minima a borde Le_blt_flange_z4 por constructibilidad (C3) (`Le_blt_flange_z4`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z4 >= C3; 26.9 mm >= 19.05 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.22 - Distancia minima a borde Le_blt_web_y3.1 por constructibilidad (C3) (`Le_blt_web_y3.1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_y3.1 >= C3; 13.5 mm >= 17.46 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.6 y Tabla 7-15 Entering and Tightening Clearance, in.`
- Resultado: 🔴 No cumple

#### Chequeo 2.1.23 - Despeje horizontal F_blt_flange y separacion escalonada minima entre pernos (`F_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `F_blt_flange >= C1_max; 32.69 mm >= 30.16 mm`
- Clausula: `Documento: AISC 360-22 + Steel Construction Manual AISC 16th edition 2023 | Seccion: AISC 360-22 J3.6 y Tabla 7-15 Entering and Tightening Clearance, in. (Aligned + Staggered Bolts)`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.24 - Alma de la viga no es esbelta (`h/tw`)

- Ámbito: `VIGA`
- Verificacion: `h/tw < 5.7*sqrt(E_vg/Fy_vg); 53.5 adim < 137.24 adim`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 (criterio solicitado por usuario)`
- Resultado: 🟢 Cumple

### 2.2 Ámbito `PLATINA_1`

#### Chequeo 2.2.1 - Separacion minima entre pernos de platina de alma en direccion X (`g_plt_web`)

- Ámbito: `PLATINA_1`
- Verificacion: `g_plt_web >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.2 - Separacion maxima entre pernos de platina de alma en direccion X (`g_plt_web`)

- Ámbito: `PLATINA_1`
- Verificacion: `g_plt_web <= Smax; 76.2 mm <= 228 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.3 - Distancia minima a borde de platina de alma Le_plt_web_x2 para agujero estandar (`Le_plt_web_x2`)

- Ámbito: `PLATINA_1`
- Verificacion: `Le_plt_web_x2 >= Le_min; 35 mm >= 22.22 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.4 - Distancia maxima a borde de platina de alma Le_plt_web_x2 (`Le_plt_web_x2`)

- Ámbito: `PLATINA_1`
- Verificacion: `Le_plt_web_x2 <= Le_max; 35 mm <= 114 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.5 - Separacion minima entre pernos de platina de alma en direccion Z (`p_plt_web`)

- Ámbito: `PLATINA_1`
- Verificacion: `p_plt_web >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.6 - Separacion maxima entre pernos de platina de alma en direccion Z (`p_plt_web`)

- Ámbito: `PLATINA_1`
- Verificacion: `p_plt_web <= Smax; 76.2 mm <= 228 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.7 - Distancia minima a borde de platina de alma Le_plt_web_y1 para agujero estandar (`Le_plt_web_y1`)

- Ámbito: `PLATINA_1`
- Verificacion: `Le_plt_web_y1 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.8 - Distancia maxima a borde de platina de alma Le_plt_web_y1 (`Le_plt_web_y1`)

- Ámbito: `PLATINA_1`
- Verificacion: `Le_plt_web_y1 <= Le_max; 25 mm <= 114 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.9 - Distancia minima a borde de platina de alma Le_plt_web_y2 para agujero estandar (`Le_plt_web_y2`)

- Ámbito: `PLATINA_1`
- Verificacion: `Le_plt_web_y2 >= Le_min; 25 mm >= 22.22 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.2.10 - Distancia maxima a borde de platina de alma Le_plt_web_y2 (`Le_plt_web_y2`)

- Ámbito: `PLATINA_1`
- Verificacion: `Le_plt_web_y2 <= Le_max; 25 mm <= 114 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### 2.3 Ámbito `PERNOS_1`

#### Chequeo 2.3.1 - Tipo de apriete permitido para pernos grupo 1 (`tight_bolt_vgder`)

- Ámbito: `PERNOS_1`
- Verificacion: `tight_bolt_vgder in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Seccion: Criterio de proyecto splice`
- Resultado: 🟢 Cumple

#### Chequeo 2.3.2 - Norma de fabricacion permitida para pernos grupo 1 (`std_bolt_vgder`)

- Ámbito: `PERNOS_1`
- Verificacion: `std_bolt_vgder in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A325' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Seccion: Criterio de proyecto splice`
- Resultado: 🟢 Cumple

### 2.4 Ámbito `PLATINA_2`

#### Chequeo 2.4.1 - Separacion minima entre pernos de platina de ala en direccion X (`p_plt_flange`)

- Ámbito: `PLATINA_2`
- Verificacion: `p_plt_flange >= Smin; 60 mm >= 57.15 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.2 - Separacion maxima entre pernos de platina de ala en direccion X (`p_plt_flange`)

- Ámbito: `PLATINA_2`
- Verificacion: `p_plt_flange <= Smax; 60 mm <= 300 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.3 - Distancia minima a borde de platina de ala Le_plt_flange_x2 para agujero estandar (`Le_plt_flange_x2`)

- Ámbito: `PLATINA_2`
- Verificacion: `Le_plt_flange_x2 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.4 - Distancia maxima a borde de platina de ala Le_plt_flange_x2 (`Le_plt_flange_x2`)

- Ámbito: `PLATINA_2`
- Verificacion: `Le_plt_flange_x2 <= Le_max; 50 mm <= 150 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.5 - Separacion minima entre pernos de platina de ala en direccion Z (`g_plt_flange`)

- Ámbito: `PLATINA_2`
- Verificacion: `n_blt_flange_z >= 2; 1 >= 2`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟠 No aplica (cumple)

#### Chequeo 2.4.6 - Separacion maxima entre pernos de platina de ala en direccion Z (`g_plt_flange`)

- Ámbito: `PLATINA_2`
- Verificacion: `n_blt_flange_z >= 2; 1 >= 2`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟠 No aplica (cumple)

#### Chequeo 2.4.7 - Distancia minima a borde de platina de ala Le_plt_flange_z1 para agujero estandar (`Le_plt_flange_z1`)

- Ámbito: `PLATINA_2`
- Verificacion: `Le_plt_flange_z1 >= Le_min; 30 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.8 - Distancia maxima a borde de platina de ala Le_plt_flange_z1 (`Le_plt_flange_z1`)

- Ámbito: `PLATINA_2`
- Verificacion: `Le_plt_flange_z1 <= Le_max; 30 mm <= 150 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.9 - Distancia minima a borde de platina de ala Le_plt_flange_z2 para agujero estandar (`Le_plt_flange_z2`)

- Ámbito: `PLATINA_2`
- Verificacion: `Le_plt_flange_z2 >= Le_min; 40 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.10 - Distancia maxima a borde de platina de ala Le_plt_flange_z2 (`Le_plt_flange_z2`)

- Ámbito: `PLATINA_2`
- Verificacion: `Le_plt_flange_z2 <= Le_max; 40 mm <= 150 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.11 - Separacion minima entre pernos de platina de ala en direccion Z entre filas internas (`g1_plt_flange`)

- Ámbito: `PLATINA_2`
- Verificacion: `g1_plt_flange >= Smin; 92 mm >= 57.15 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.4.12 - Separacion maxima entre pernos de platina de ala en direccion Z entre filas internas (`g1_plt_flange`)

- Ámbito: `PLATINA_2`
- Verificacion: `g1_plt_flange <= Smax; 92 mm <= 300 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### 2.5 Ámbito `PERNOS_2`

#### Chequeo 2.5.1 - Tipo de apriete permitido para pernos grupo 2 (`tight_bolt_vgder`)

- Ámbito: `PERNOS_2`
- Verificacion: `tight_bolt_vgder in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Seccion: Criterio de proyecto splice`
- Resultado: 🟢 Cumple

#### Chequeo 2.5.2 - Norma de fabricacion permitida para pernos grupo 2 (`std_bolt_vgder`)

- Ámbito: `PERNOS_2`
- Verificacion: `std_bolt_vgder in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A325' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Seccion: Criterio de proyecto splice`
- Resultado: 🟢 Cumple

### 2.6 Resumen de chequeos por ámbito

- 🔴 `2.1` `VIGA`: total=24, cumple=18, no_cumple=6, numerales_no_cumplen=2.1.3, 2.1.7, 2.1.9, 2.1.14, 2.1.15, 2.1.22
- 🟢 `2.2` `PLATINA_1`: total=10, cumple=10, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `2.3` `PERNOS_1`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `2.4` `PLATINA_2`: total=12, cumple=12, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `2.5` `PERNOS_2`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno

## Paso 3 - Metodo ICR/Elastic

### 3.1 Metodo ICR/Elastic para pernos 1 del alma de la viga

- Metodo seleccionado: `icr`
- Clausula: `Documento: Steel Construction Manual AISC 16th edition 2023 | Seccion: Part 7 DESIGN CONSIDERATIONS FOR BOLTS - Instantaneous Center of Rotation Method`
- Ecuaciones: `e3_blt_web = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web; Mu1_blt_web = v2_blt_web*e3_blt_web - alpha_Pu_web*P3_blt_web*e2_blt_web`
- P3_blt_web: `66.99 kN`
- v2_blt_web: `250 kN`
- e3_blt_web: `76.2 mm`
- e2_blt_web: `0 mm`
- Mu1_blt_web: `19.05 kN-m`
- Demanda (metodo activo): `258.82 kN`
- Ru_blt_1_web_vg: `Ru_1_blt_1_web = 11.62 kip`
- Ru_blt_1_web_v3_max_vg: `Ru_1_blt_1_web_v3 = -9.28 kip`
- Ru_blt_1_web_v2_max_vg: `Ru_4_blt_1_web_v2 = -10.88 kip`
- Coeficiente Cu (ICR): `4.92`
- Verificacion de equilibrio por componentes:
- `sum(Ru_i_blt_1_web_v3) = -15.06 kip` vs `-P3_blt_web = -15.06 kip`; `diferencia = -0 kip`
- `sum(Ru_i_blt_1_web_v2) = -56.2 kip` vs `-v2_blt_web = -56.2 kip`; `diferencia = -0 kip`

### 3.2 Metodo ICR/Elastic para pernos 2 del ala de la viga

- Metodo seleccionado: `elastic_superposition`
- Clausula: `Documento: Steel Construction Manual AISC 16th edition 2023 | Seccion: Part 7 DESIGN CONSIDERATIONS FOR BOLTS - Instantaneous Center of Rotation Method`
- Ecuaciones: `P3_blt_flange = (1 - alpha_Pu_web)*Pu_sp + Mu3_sp/(d_vg - tf_vg); v1_blt_flange = 0.5*Vu3_sp; e3_blt_flange = gap_sp + 2*Le_blt_flange_x1 + (n_blt_flange_x - 1)*p_blt_flange; Mu2_blt_flange = v1_blt_flange*e3_blt_flange - P3_blt_flange*e1_blt_flange`
- P3_blt_flange: `1091.58 kN`
- v1_blt_flange: `0 kN`
- e3_blt_flange: `305.4 mm`
- e1_blt_flange: `0 mm`
- Mu2_blt_flange: `0 kN-m`
- Demanda (metodo activo): `136.45 kN`
- Ru_blt_2_flange_vg: `Ru_1_blt_2_flange = 30.67 kip`
- Ru_blt_2_flange_v3_max_vg: `Ru_1_blt_2_flange_v3 = -30.67 kip`
- Ru_blt_2_flange_v1_max_vg: `Ru_1_blt_2_flange_v1 = 0 kip`
- Verificacion de equilibrio por componentes:
- `sum(Ru_i_blt_2_flange_v3) = -245.4 kip` vs `-P3_blt_flange = -245.4 kip`; `diferencia = 0 kip`
- `sum(Ru_i_blt_2_flange_v1) = 0 kip` vs `-v1_blt_flange = -0 kip`; `diferencia = 0 kip`

## Paso 4 - Revisión de resistencia de la viga

### 4.1 Revisión de capacidad a cortante en el alma en direccion 2

#### 4.1.1. ELR #1: Desgarramiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`
- Ecuaciones: `lc_blt_web_y = p_blt_web - dh.1; Rn1_web_v2_vg = C*lc_blt_web_y*tw_vg*Fu_vg; phi*Rn1_web_v2_vg = phi_fragil*Rn1_web_v2_vg; DCR1_web_v2_vg = Ru1_web_v2_vg/phi*Rn1_web_v2_vg`
- Fu_vg: `450 MPa`
- tw_vg: `7.62 mm`
- p_blt_web: `76.2 mm`
- dh.1: `17.46 mm`
- lc_blt_web_y: `58.74 mm`
- C: `1.2`
- phi_fragil: `0.75`
- Rn1_web_v2_vg: `241.69 kN`
- phi*Rn1_web_v2_vg: `181.27 kN`
- Ru1_web_v2_vg: `41.29 kN`
- DCR1_web_v2_vg: `0.23`
- Resultado: 🟢 Cumple

#### 4.1.2. ELR #2: Aplastamiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(a)`
- Ecuaciones: `Rn2_web_v2-v3_vg = C*db_blt_web*tw_vg*Fu_vg; phi*Rn2_web_v2-v3_vg = phi_fragil*Rn2_web_v2-v3_vg; DCR2_web_v2-v3_vg = Ru2_web_v2-v3_vg/phi*Rn2_web_v2-v3_vg`
- Fu_vg: `450 MPa`
- tw_vg: `7.62 mm`
- db_blt_web: `15.88 mm`
- C: `2.4`
- phi_fragil: `0.75`
- Rn2_web_v2-v3_vg: `130.64 kN`
- phi*Rn2_web_v2-v3_vg: `97.98 kN`
- Ru2_web_v2-v3_vg = Ru_web_vg: `51.68 kN`
- DCR2_web_v2-v3_vg: `0.53`
- Resultado: 🟢 Cumple

#### 4.1.3. ELR #3: Rotura por cortante en el perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.7`
- Ecuaciones: `Rn3_web_v2-v3_vg = Ab_blt_web*Fnv_blt_web; phi*Rn3_web_v2-v3_vg = phi_fragil*Rn3_web_v2-v3_vg; DCR3_web_v2-v3_vg = Ru3_web_v2-v3_vg/phi*Rn3_web_v2-v3_vg`
- db_blt_web: `15.88 mm`
- Ab_blt_web: `197.93 mm2`
- Fnv_blt_web: `370 MPa`
- phi_fragil: `0.75`
- Rn3_web_v2-v3_vg: `73.24 kN`
- phi*Rn3_web_v2-v3_vg: `54.93 kN`
- Ru3_web_v2-v3_vg = Ru_web_vg: `51.68 kN`
- DCR3_web_v2-v3_vg: `0.94`
- Resultado: 🟢 Cumple

#### 4.1.5. ELR #5: Bloque de cortante en alma de viga

- Clausula: `Documento: AISC 360-22w | Seccion: J4.3 (DRY: compute_block_shear_strength_j45)`
- Ecuaciones: `Agv_web_v2_vg = p_blt_web*(n_blt_web_y - 1)*tw_vg + (Le_blt_web_y3 - tf_vg)*tw_vg + tf_vg*bf_vg; Anv_web_v2_vg = Agv_web_v2_vg - (n_blt_web_y - 0.5)*tw_vg*(dh.1 + 1.80mm); Agt_web_v2_vg = g_blt_web*(n_blt_web_x - 1)*tw_vg + Le_blt_web_x1*tw_vg; Ant_web_v2_vg = Agt_web_v2_vg - (n_blt_web_x - 0.5)*tw_vg*(dh.1 + 1.80mm); Rn5_1_web_v2_vg = 0.60*Fu_vg*Anv_web_v2_vg + Ubs_web_v2_vg*Fu_vg*Ant_web_v2_vg; Rn5_2_web_v2_vg = 0.60*Fy_vg*Agv_web_v2_vg + Ubs_web_v2_vg*Fu_vg*Ant_web_v2_vg; Rn5_web_v2_vg = min(Rn5_1_web_v2_vg, Rn5_2_web_v2_vg); phi*Rn5_web_v2_vg = phi_fragil*Rn5_web_v2_vg; DCR5_web_v2_vg = Ru5_web_v2_vg/phi*Rn5_web_v2_vg`
- Fu_vg: `450 MPa`
- Fy_vg: `345 MPa`
- tw_vg: `7.62 mm`
- tf_vg: `10.8 mm`
- bf_vg: `152 mm`
- n_blt_web_x: `1`
- n_blt_web_y: `6`
- g_blt_web: `76.2 mm`
- p_blt_web: `76.2 mm`
- Le_blt_web_x1: `25.4 mm`
- Le_blt_web_y3: `34.5 mm`
- dh.1: `17.46 mm`
- Ubs_web_v2_vg (inp): `0.5`
- Agv_web_v2_vg: `4725.41 mm2`
- Anv_web_v2_vg: `3918.12 mm2`
- Agt_web_v2_vg: `193.55 mm2`
- Ant_web_v2_vg: `120.16 mm2`
- phi_fragil: `0.75`
- Rn5_1_web_v2_vg: `1084.93 kN`
- Rn5_2_web_v2_vg: `1005.2 kN`
- Rn5_web_v2_vg: `1005.2 kN`
- phi*Rn5_web_v2_vg: `753.9 kN`
- Ru5_web_v2_vg = Vu2_sp: `250 kN`
- DCR5_web_v2_vg: `0.33`
- Resultado: `Cumple`

### 4.2 Revisión de capacidad a tracción en el alma en direccion 3

#### 4.2.1. ELR #1: Desgarramiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`
- Ecuaciones: `lc_web_v3_vg = min(g_blt_web - dh.1, Le_blt_web_x1 - 0.5*dh.1); Rn1_web_v3_vg = C*lc_web_v3_vg*tw_vg*Fu_vg; phi*Rn1_web_v3_vg = phi_fragil*Rn1_web_v3_vg; DCR1_web_v3_vg = Ru1_web_v3_vg/phi*Rn1_web_v3_vg`
- Fu_vg: `450 MPa`
- tw_vg: `7.62 mm`
- g_blt_web: `76.2 mm`
- Le_blt_web_x1: `25.4 mm`
- dh.1: `17.46 mm`
- lc_web_v3_vg: `16.67 mm`
- C: `1.2`
- phi_fragil: `0.75`
- Rn1_web_v3_vg: `68.59 kN`
- phi*Rn1_web_v3_vg: `51.44 kN`
- Ru1_web_v3_vg = Ru_web_v3_max_vg: `48.39 kN`
- DCR1_web_v3_vg: `0.94`
- Resultado: 🟢 Cumple

#### 4.2.3. ELR #3: Bloque de cortante en alma de viga

- Clausula: `Documento: AISC 360-22w | Seccion: J4.3 (DRY: compute_block_shear_strength_j45)`
- Ecuaciones: `Agv_web_v3_vg = 2*(g_blt_web*(n_blt_web_x - 1)*tw_vg + Le_blt_web_x1*tw_vg); Anv_web_v3_vg = 2*(0.5*Agv_web_v3_vg - (n_blt_web_x - 0.5)*tw_vg*(dh.1 + 1.80mm)); Agt_web_v3_vg = p_blt_web*(n_blt_web_y - 1)*tw_vg; Ant_web_v3_vg = Agt_web_v3_vg - (n_blt_web_y - 1)*tw_vg*(dh.1 + 1.80mm); Rn4_1_web_v3_vg = 0.60*Fu_vg*Anv_web_v3_vg + Ubs_web_v3_vg*Fu_vg*Ant_web_v3_vg; Rn4_2_web_v3_vg = 0.60*Fy_vg*Agv_web_v3_vg + Ubs_web_v3_vg*Fu_vg*Ant_web_v3_vg; Rn4_web_v3_vg = min(Rn4_1_web_v3_vg, Rn4_2_web_v3_vg); phi*Rn4_web_v3_vg = phi_fragil*Rn4_web_v3_vg; Ru4_web_v3_vg = Pu_sp*alpha_Pu_web; DCR4_web_v3_vg = Ru4_web_v3_vg/phi*Rn4_web_v3_vg`
- Fu_vg: `450 MPa`
- Fy_vg: `345 MPa`
- tw_vg: `7.62 mm`
- n_blt_web_x: `1`
- n_blt_web_y: `6`
- g_blt_web: `76.2 mm`
- p_blt_web: `76.2 mm`
- Le_blt_web_x1: `25.4 mm`
- dh.1: `17.46 mm`
- Ubs_web_v3_vg (inp): `0.5`
- Agv_web_v3_vg: `387.1 mm2`
- Anv_web_v3_vg: `240.32 mm2`
- Agt_web_v3_vg: `2903.22 mm2`
- Ant_web_v3_vg: `2169.32 mm2`
- phi_fragil: `0.75`
- Rn4_1_web_v3_vg: `552.98 kN`
- Rn4_2_web_v3_vg: `568.23 kN`
- Rn4_web_v3_vg: `552.98 kN`
- phi*Rn4_web_v3_vg: `414.74 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru4_web_v3_vg = Pu_sp*alpha_Pu_web: `0 kN`
- DCR4_web_v3_vg: `0`
- Resultado: 🟢 Cumple

### 4.3 Revisión de capacidad a tracción en el ala en direccion 3

#### 4.3.1. ELR #1: Desgarramiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)`
- Ecuaciones: `lc_flange_p3_vg = min(p_blt_flange - dh.2, Le_blt_flange_x1 - 0.5*dh.2); Rn1_flange_p3_vg = C*lc_flange_p3_vg*tf_vg*Fu_vg; phi*Rn1_flange_p3_vg = phi_pr*Rn1_flange_p3_vg; Ru1_flange_p3(+)_vg = Ru_flange_v3_max_vg (tomado de 3.2); DCR1_flange_p3_vg = Ru1_flange_p3(+)_vg/phi*Rn1_flange_p3_vg`
- Fu_vg: `450 MPa`
- tf_vg: `10.8 mm`
- p_blt_flange: `60 mm`
- Le_blt_flange_x1: `50 mm`
- dh.2: `20.64 mm`
- lc_flange_p3_vg: `39.36 mm`
- C: `1.2`
- phi_pr: `0.75`
- Rn1_flange_p3_vg: `229.56 kN`
- phi*Rn1_flange_p3_vg: `172.17 kN`
- alpha_Pu_web: `0`
- Pu_sp: `66.99 kN`
- Mu3_sp: `450 kN-m`
- d_vg: `450 mm`
- Ru1_flange_p3(+)_vg: `136.45 kN`
- DCR1_flange_p3_vg: `0.79`
- Resultado: 🟢 Cumple

#### 4.3.2. ELR #2: Aplastamiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(a) (DRY: compute_bolt_hole_bearing_strength_j36)`
- Ecuaciones: `Rn2_flange_p3_vg = C*db_blt_flange*tf_vg*Fu_vg; phi*Rn2_flange_p3_vg = phi_pr*Rn2_flange_p3_vg; Ru2_flange_p3(+)_vg = Ru_blt_2_flange_vg (tomado de 3.2); DCR2_flange_p3_vg = Ru2_flange_p3(+)_vg/phi*Rn2_flange_p3_vg`
- Fu_vg: `450 MPa`
- tf_vg: `10.8 mm`
- db_blt_flange: `19.05 mm`
- C: `2.4`
- phi_pr: `0.75`
- Rn2_flange_p3_vg: `222.2 kN`
- phi*Rn2_flange_p3_vg: `166.65 kN`
- Ru2_flange_p3(+)_vg: `136.45 kN`
- DCR2_flange_p3_vg: `0.82`
- Resultado: 🟢 Cumple

#### 4.3.3. ELR #3: Rotura por cortante en el perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.7 (DRY: compute_bolt_shear_rupture_capacity_per_bolt)`
- Ecuaciones: `Rn3_flange_p3_vg = Ab_blt_flange*Fnv_blt_flange; phi*Rn3_flange_p3_vg = phi_pr*Rn3_flange_p3_vg; Ru3_flange_p3(+)_vg = Ru_blt_2_flange_vg (tomado de 3.2); DCR3_flange_p3_vg = Ru3_flange_p3(+)_vg/phi*Rn3_flange_p3_vg`
- db_blt_flange: `19.05 mm`
- Ab_blt_flange: `285.02 mm2`
- Fnv_blt_flange: `370 MPa`
- phi_pr: `0.75`
- Rn3_flange_p3_vg: `105.46 kN`
- phi*Rn3_flange_p3_vg: `79.09 kN`
- Ru3_flange_p3(+)_vg: `136.45 kN`
- DCR3_flange_p3_vg: `1.73`
- Resultado: 🔴 No cumple

#### 4.3.4. ELR #4: Bloque de cortante en ala de viga

- Clausula: `Documento: AISC 360-22 | Seccion: J4.3 (DRY: compute_block_shear_strength_j45)`
- Ecuaciones: `Caso 1 -> Agt1_flange_v3_vg = 2*(Le_blt_flange_z1*tf_vg); Ant1_flange_v3_vg = Agt1_flange_v3_vg - 2*tf_vg*0.5*(dh.2 + 1.80mm); Agv1_flange_v3_vg = 2*tf_vg*(Le_blt_flange_x1 + (n_blt_flange_x - 1)*p_blt_flange); Anv1_flange_v3_vg = Agv1_flange_v3_vg - 2*tf_vg*(n_blt_flange_x - 0.5)*(dh.2 + 1.80mm); Caso 2 -> Agt2_flange_v3_vg = 0.5*(A_g - (d_vg - 2*kdes_vg)*tw_vg); Ant2_flange_v3_vg = Agt2_flange_v3_vg - n_blt_flange_z*tf_vg*(dh.2 + 1.80mm); Agv2_flange_v3_vg = tw_vg*(Le_blt_flange_x1 + (n_blt_flange_x - 1)*p_blt_flange); Anv2_flange_v3_vg = Agv2_flange_v3_vg; phi*Rn4_flange_p3_vg = min(phi*Rn4_case1_flange_p3_vg, phi*Rn4_case2_flange_p3_vg); Ru4_flange_p3(+)_vg = (1- alpha_Pu_web)*Pu_sp + Mu3_sp/(d_vg - tf_vg), si <0 entonces 0; DCR4_flange_p3_vg = Ru4_flange_p3(+)_vg/phi*Rn4_flange_p3_vg`
- Fu_vg: `450 MPa`
- Fy_vg: `345 MPa`
- tf_vg: `10.8 mm`
- tw_vg: `7.62 mm`
- d_vg: `450 mm`
- kdes_vg: `21 mm`
- A_g: `6650 mm2`
- n_blt_flange_x: `4`
- n_blt_flange_z: `1`
- p_blt_flange: `60 mm`
- Le_blt_flange_x1: `50 mm`
- Le_blt_flange_z1: `30 mm`
- dh.2: `20.64 mm`
- Ubs_flange_v3_vg (inp): `1`
- Ubs_flange_v1_vg (inp): `1`
- Agt1_flange_v3_vg: `648 mm2`
- Ant1_flange_v3_vg: `405.67 mm2`
- Agv1_flange_v3_vg: `4968 mm2`
- Anv1_flange_v3_vg: `3271.72 mm2`
- phi*Rn4_case1_flange_p3_vg: `799.44 kN`
- Agt2_flange_v3_vg: `1770.52 mm2`
- Ant2_flange_v3_vg: `1528.19 mm2`
- Agv2_flange_v3_vg: `1752.6 mm2`
- Anv2_flange_v3_vg: `1752.6 mm2`
- phi*Rn4_case2_flange_p3_vg: `787.86 kN`
- Caso control: `Caso 2`
- phi_pr: `0.75`
- phi*Rn4_flange_p3_vg: `787.86 kN`
- Ru4_flange_p3(+)_vg: `1091.58 kN`
- DCR4_flange_p3_vg: `1.39`
- Resultado: 🔴 No cumple

### 4.4 Revisión de capacidad a cortante en el ala en dirección 1

#### 4.4.1. ELR #1: Desgarramiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b) (DRY: compute_bolt_hole_tearout_strength_j36)`
- Ecuaciones: `si n_blt_flange_z >= 2 -> lc_flange_v1_vg = min(g_blt_flange - dh.2, Le_blt_flange_z1 - 0.5*dh.2); si n_blt_flange_z = 1 -> lc_flange_v1_vg = Le_blt_flange_z1 - 0.5*dh.2; Rn1_flange_v1_vg = C*lc_flange_v1_vg*tf_vg*Fu_vg; phi*Rn1_flange_v1_vg = phi_pr*Rn1_flange_v1_vg; Ru1_flange_v1_vg = Ru_blt_2_flange_v1_max_vg (tomado de 3.2); DCR1_flange_v1_vg = Ru1_flange_v1_vg/phi*Rn1_flange_v1_vg`
- Fu_vg: `450 MPa`
- tf_vg: `10.8 mm`
- g_blt_flange: `40 mm`
- n_blt_flange_z: `1`
- Le_blt_flange_z1: `30 mm`
- dh.2: `20.64 mm`
- lc_flange_v1_vg: `19.68 mm`
- C: `1.2`
- phi_pr: `0.75`
- Rn1_flange_v1_vg: `114.78 kN`
- phi*Rn1_flange_v1_vg: `86.09 kN`
- Ru1_flange_v1_vg: `0 kN`
- DCR1_flange_v1_vg: `0`
- Resultado: 🟢 Cumple

### 4.5 Revisión de capacidad a tracción de la viga en dirección 3

#### 4.5.1. ELR #2: Rotura por tracción de la viga

- Clausula: `Documento: AISC 360-22 | Seccion: J4.1.(b)`
- Ecuaciones: `si 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web - n_blt_web_y*(dh.1 + 1.80mm) <= T_vg -> Ant_v3_vg = tw_vg*(2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web - n_blt_web_y*(dh.1 + 1.80mm)); si no -> Ant_v3_vg = A_vg - n_blt_web_y*(dh.1 + 1.80mm)*tw_vg; si n_blt_web_x <= 1 -> U_v3_vg = T_vg*tw_vg/A_vg; si n_blt_web_x > 1 -> U_v3_vg = 1 - 0.5*tw_vg/(n_blt_web_x*g_blt_web); Ae_v3_vg = Ant_v3_vg*U_v3_vg; Rn3_v3_vg = Fu_vg*Ae_v3_vg; phi*Rn3_v3_vg = phi_fragil*Rn3_v3_vg; Ru3_v3_vg = Pu_sp; DCR3_v3_vg = Ru3_v3_vg/phi*Rn3_v3_vg`
- Fu_vg: `450 MPa`
- T_vg: `394 mm`
- tw_vg: `7.62 mm`
- A_vg: `3429 mm2`
- n_blt_web_y: `6`
- dh.1: `17.46 mm`
- Ant_v3_vg: `2022.54 mm2`
- n_blt_web_x: `1`
- g_blt_web: `76.2 mm`
- U_v3_vg: `0.88`
- Ae_v3_vg: `1770.84 mm2`
- phi_fragil: `0.75`
- Rn3_v3_vg: `796.88 kN`
- phi*Rn3_v3_vg: `597.66 kN`
- Pu_sp: `66.99 kN`
- Ru3_v3_vg = Pu_sp: `66.99 kN`
- DCR3_v3_vg: `0.11`
- Resultado: 🟢 Cumple

### 4.6 Revisión de capacidad a cortante de la viga en dirección 2

#### 4.6.1. ELR #4: Rotura por cortante de la viga

- Clausula: `Documento: AISC 360-22 | Seccion: J4.2(b) (DRY: compute_element_shear_rupture_strength_j43)`
- Ecuaciones: `A_vg = d_vg*tw_vg; Anv_v2_vg = A_vg - n_blt_web_y*(dh.1+1.8mm)*tw_vg; Rn1_v2_vg = 0.60*Fu_vg*Anv_v2_vg; phi*Rn1_v2_vg = phi_fragil*Rn1_v2_vg; DCR1_v2_vg = Ru1_v2_vg/phi*Rn1_v2_vg`
- Fu_vg: `450 MPa`
- tw_vg: `7.62 mm`
- A_vg: `3429 mm2`
- n_blt_web_y: `6`
- dh.1: `17.46 mm`
- Anv_v2_vg: `2548.32 mm2`
- phi_fragil: `0.75`
- Rn1_v2_vg: `688.05 kN`
- phi*Rn1_v2_vg: `516.03 kN`
- Ru1_v2_vg = Vu2_sp: `250 kN`
- DCR1_v2_vg: `0.48`
- Resultado: 🟢 Cumple

### 4.7 Revisión de capacidad a cortante de la viga en dirección 1

- Pendiente de desarrollo en esta versión.

### 4.8 Revisión de capacidad a flexión de la viga en dirección 1

#### 4.8.1. ELR #1: Rotura por flexión

- Clausula: `Documento: AISC 360-22 | Seccion: F13.1 (DRY: compute_member_flexural_rupture_with_tension_flange_holes_f131)`
- Ecuaciones: `Afg_m1_vg = tf_vg*bf_vg; Afn_m1_vg = Afg_m1_vg - 2*n_blt_flange_z*(dh.2 + 1.80mm)*tf_vg; Yf = 1.0 si Fy/Fu <= 0.8, 1.1 en otro caso; si Fu*Afn >= Yf*Fy*Agf -> limite F13.1 no aplica; si Fu*Afn < Yf*Fy*Agf -> Rn1_m1_vg = (Fu_vg*Afn_m1_vg/Afg_m1_vg)*Sx_vg; phi*Rn1_m1_vg = phi_no_ductil*Rn1_m1_vg; Ru1_m1_vg = Mu3_sp; DCR1_m1_vg = Ru1_m1_vg/phi*Rn1_m1_vg`
- Fu_vg: `450 MPa`
- Fy_vg: `345 MPa`
- tf_vg: `10.8 mm`
- bf_vg: `152 mm`
- n_blt_flange_z: `1`
- dh.2: `20.64 mm`
- Afg_m1_vg: `1641.6 mm2`
- Afn_m1_vg: `1156.95 mm2`
- Sx_vg: `1090000 mm3`
- Yf: `1`
- Fy/Fu: `0.77`
- Fu*Afn: `520.63 kN`
- Yf*Fy*Agf: `566.35 kN`
- F13.1 aplica: `True`
- phi_no_ductil: `0.9`
- Rn1_m1_vg: `345.69 kN-m`
- phi*Rn1_m1_vg: `311.12 kN-m`
- Ru1_m1_vg: `450 kN-m`
- DCR1_m1_vg: `1.45`
- Resultado: 🔴 No cumple

### 4.9 Revisi?n de capacidad bajo la acci?n de fuerzas combinadas en la viga

#### 4.9.1. ELR #1: Interacci?n entre cargas en la viga

- Clausula: `Documento: AISC 360-22 | Seccion: H1.1 (DRY: compute_member_combined_interaction_h11)`
- Ecuaciones: `si Pu_sp >= 0 -> Pr/(phiPc) = DCR_4.5.1 (hasta implementar 4.5.2); si Pu_sp < 0 -> Pr/(phiPc) = Pu_sp/phiPnc; Mrx/Mcx = max(|Mu3_sp|/phiMn3, DCR_4.8.1); Mry/Mcy = 0; si Pr/Pc >= 0.2 -> H1-1a = Pr/Pc + (8/9)*(Mrx/Mcx + Mry/Mcy); si Pr/Pc < 0.2 -> H1-1b = Pr/(2*Pc) + (Mrx/Mcx + Mry/Mcy)`
- Pu_sp: `66.99 kN`
- phiPnc: `1200 kN`
- phiMn3: `800 kN-m`
- phiMn2: `800 kN-m`
- DCR_4.5.1: `0.11`
- DCR_4.8.1: `1.45`
- |Mu3_sp|/phiMn3: `0.56`
- Pr/(phiPc): `0.11`
- Mrx/Mcx: `1.45`
- Mry/Mcy: `0`
- Ecuacion gobernante: `H1-1b`
- DCR_Fcomb_vg: `1.5`
- Resultado: 🔴 No cumple

## Paso 5 - Revisión de resistencia de la platina 1 de alma

### 5.1 Revisión de capacidad a cortante en la platina 1 de alma en direccion 2

#### 5.1.1. ELR #1: Desgarramiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`
- Ecuaciones: `lc_plt_v2_web = min(p_plt_web - dh.1, Le_plt_web_y1 - 0.5*dh.1, Le_plt_web_y2 - 0.5*dh.1); Rn1_plt_v2_web = C*lc_plt_v2_web*t_plt_web*Fu_plt_web; phi*Rn1_plt_v2_web = phi_fragil*Rn1_plt_v2_web; DCR1_plt_v2_web = Ru1_plt_v2_web/phi*Rn1_plt_v2_web`
- Fu_plt_web: `400 MPa`
- t_plt_web: `9.5 mm`
- p_plt_web: `76.2 mm`
- Le_plt_web_y1: `25 mm`
- Le_plt_web_y2: `25 mm`
- dh.1: `17.46 mm`
- lc_plt_v2_web: `16.27 mm`
- C: `1.2`
- phi_fragil: `0.75`
- Rn1_plt_v2_web: `74.19 kN`
- phi*Rn1_plt_v2_web: `55.64 kN`
- Ru1_plt_v2_web = Ru_web_v2_max_vg: `41.29 kN`
- DCR1_plt_v2_web: `0.74`
- Resultado: 🟢 Cumple

#### 5.1.2. ELR #2: Aplastamiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(a)`
- Ecuaciones: `Rn2_plt_v2-v3_web = C*db_blt_web*t_plt_web*Fu_plt_web; phi*Rn2_plt_v2-v3_web = phi_fragil*Rn2_plt_v2-v3_web; DCR2_plt_v2-v3_web = Ru2_plt_v2-v3_web/phi*Rn2_plt_v2-v3_web`
- Fu_plt_web: `400 MPa`
- t_plt_web: `9.5 mm`
- db_blt_web: `15.88 mm`
- C: `2.4`
- phi_fragil: `0.75`
- Rn2_plt_v2-v3_web: `144.78 kN`
- phi*Rn2_plt_v2-v3_web: `108.58 kN`
- Ru2_plt_v2-v3_web = Ru_web_vg: `51.68 kN`
- DCR2_plt_v2-v3_web: `0.48`
- Resultado: 🟢 Cumple

#### 5.1.3. ELR #3: Rotura por cortante en el perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.7`
- Ecuaciones: `Rn3_plt_v2-v3_web = Ab_blt_web*Fnv_blt_web; phi*Rn3_plt_v2-v3_web = phi_fragil*Rn3_plt_v2-v3_web; DCR3_plt_v2-v3_web = Ru3_plt_v2-v3_web/phi*Rn3_plt_v2-v3_web`
- db_blt_web: `15.88 mm`
- Ab_blt_web: `197.93 mm2`
- Fnv_blt_web: `370 MPa`
- phi_fragil: `0.75`
- Rn3_plt_v2-v3_web: `73.24 kN`
- phi*Rn3_plt_v2-v3_web: `54.93 kN`
- Ru3_plt_v2-v3_web = Ru_web_vg: `51.68 kN`
- DCR3_plt_v2-v3_web: `0.94`
- Resultado: 🟢 Cumple

#### 5.1.4. ELR #4: Bloque de cortante en platina 1 del alma

- Clausula: `Documento: AISC 360-22w | Seccion: J4.3`
- Ecuaciones: `Agv_plt_v2_web = (p_plt_web*(n_plt_web_y - 1) + min(Le_plt_web_y1, Le_plt_web_y2))*t_plt_web; Anv_plt_v2_web = Agv_plt_v2_web - (n_blt_web_y - 0.5)*t_plt_web*(dh.1 + 1.80mm); Agt_plt_v2_web = (g_blt_web*(n_blt_web_x - 1) + Le_plt_web_x2)*t_plt_web; Ant_plt_v2_web = Agt_plt_v2_web - (n_blt_web_x - 0.5)*t_plt_web*(dh.1 + 1.80mm); Rn4_1_plt_v2_web = 0.60*Fu_plt_web*Anv_plt_v2_web + Ubs_plt_v2_web*Fu_plt_web*Ant_plt_v2_web; Rn4_2_plt_v2_web = 0.60*Fy_plt_web*Agv_plt_v2_web + Ubs_plt_v2_web*Fu_plt_web*Ant_plt_v2_web; Rn4_plt_v2_web = min(Rn4_1_plt_v2_web, Rn4_2_plt_v2_web); phi*Rn4_plt_v2_web = phi_fragil*Rn4_plt_v2_web; DCR4_plt_v2_web = Ru4_plt_v2_web/phi*Rn4_plt_v2_web`
- Fu_plt_web: `400 MPa`
- Fy_plt_web: `n/a`
- t_plt_web: `9.5 mm`
- n_blt_web_x: `1`
- n_plt_web_y (= n_blt_web_y): `6`
- g_blt_web: `76.2 mm`
- p_plt_web: `76.2 mm`
- Le_plt_web_x2: `35 mm`
- Le_plt_web_y1: `25 mm`
- Le_plt_web_y2: `25 mm`
- dh.1: `17.46 mm`
- Ubs_plt_v2_web (inp = Ubs_web_v2_vg): `0.5`
- Agv_plt_v2_web: `3857 mm2`
- Anv_plt_v2_web: `2850.53 mm2`
- Agt_plt_v2_web: `332.5 mm2`
- Ant_plt_v2_web: `241 mm2`
- phi_fragil: `0.75`
- Rn4_1_plt_v2_web: `732.33 kN`
- Rn4_2_plt_v2_web: `626.75 kN`
- Rn4_plt_v2_web: `626.75 kN`
- phi*Rn4_plt_v2_web: `470.06 kN`
- Ru4_plt_v2_web = Vu2_sp: `250 kN`
- DCR4_plt_v2_web: `0.53`
- Resultado: 🟢 Cumple

#### 5.1.5. ELR #5: fluencia por cortante en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: J4.2(a)`
- Ecuaciones: `Agv_v2_plt_web = (p_plt_web*(n_plt_web_y - 1) + Le_plt_web_y1 + Le_plt_web_y2)*t_plt_web; Rn5_plt_v2_web = 0.60*Fy_plt_web*Agv_v2_plt_web; phi*Rn5_plt_v2_web = phi_ductil*Rn5_plt_v2_web; DCR5_plt_v2_web = Ru5_plt_v2_web/phi*Rn5_plt_v2_web`
- Fy_plt_web: `250 MPa`
- t_plt_web: `9.5 mm`
- n_plt_web_y (= n_blt_web_y): `6`
- p_plt_web: `76.2 mm`
- Le_plt_web_y1: `25 mm`
- Le_plt_web_y2: `25 mm`
- Agv_v2_plt_web: `4094.5 mm2`
- phi_ductil: `1`
- Rn5_plt_v2_web: `614.17 kN`
- phi*Rn5_plt_v2_web: `614.17 kN`
- Ru5_plt_v2_web = Vu2_sp: `250 kN`
- DCR5_plt_v2_web: `0.41`
- Resultado: 🟢 Cumple

#### 5.1.6. ELR #6: Rotura por cortante en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: J4.2(b)`
- Ecuaciones: `Anv_v2_plt_web = (p_plt_web*(n_plt_web_y - 1) + Le_plt_web_y1 + Le_plt_web_y2 - n_plt_web_y*(dh.1 + 1.80mm))*t_plt_web; Rn6_plt_v2_web = 0.60*Fu_plt_web*Anv_v2_plt_web; phi*Rn6_plt_v2_web = phi_fragil*Rn6_plt_v2_web; DCR6_plt_v2_web = Ru6_plt_v2_web/phi*Rn6_plt_v2_web`
- Fu_plt_web: `400 MPa`
- t_plt_web: `9.5 mm`
- n_plt_web_y (= n_blt_web_y): `6`
- p_plt_web: `76.2 mm`
- Le_plt_web_y1: `25 mm`
- Le_plt_web_y2: `25 mm`
- dh.1: `17.46 mm`
- Anv_v2_plt_web: `2850.53 mm2`
- phi_fragil: `0.75`
- Rn6_plt_v2_web: `719.17 kN`
- phi*Rn6_plt_v2_web: `539.38 kN`
- Ru6_plt_v2_web = Vu2_sp: `250 kN`
- DCR6_plt_v2_web: `0.46`
- Resultado: 🟢 Cumple

### 5.2 Revisión de capacidad a tracción en la platina 1 de alma en direccion 3

#### 5.2.1. ELR #1: Desgarramiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: J3.11a.(b)`
- Ecuaciones: `lc_plt_v3_web = min(g_plt_web - dh.1, Le_plt_web_x2 - 0.5*dh.1); Rn1_plt_v3_web = C*lc_plt_v3_web*t_plt_web*Fu_plt_web; phi*Rn1_plt_v3_web = phi_fragil*Rn1_plt_v3_web; DCR1_plt_v3_web = Ru1_plt_v3_web/phi*Rn1_plt_v3_web`
- Fu_plt_web: `400 MPa`
- t_plt_web: `9.5 mm`
- g_plt_web: `76.2 mm`
- Le_plt_web_x2: `35 mm`
- dh.1: `17.46 mm`
- lc_plt_v3_web: `26.27 mm`
- C: `1.2`
- phi_fragil: `0.75`
- Rn1_plt_v3_web: `119.79 kN`
- phi*Rn1_plt_v3_web: `89.84 kN`
- Ru1_plt_v3_web = Ru_web_v3_max_vg: `48.39 kN`
- DCR1_plt_v3_web: `0.54`
- Resultado: 🟢 Cumple

#### 5.2.2. ELR #2: Bloque de cortante en platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: J4-5 (DRY: compute_block_shear_strength_j45)`
- Ecuaciones: `Agv_plt_v3_web = 2*(g_blt_web*(n_blt_web_x - 1)*t_plt_web + Le_blt_web_x2*t_plt_web); Anv_plt_v3_web = 2*(0.5*Agv_plt_v3_web - (n_blt_web_x - 0.5)*t_plt_web*(dh.1 + 1.80mm)); Agt_plt_v3_web = p_blt_web*(n_blt_web_y - 1)*t_plt_web; Ant_plt_v3_web = Agt_plt_v3_web - (n_blt_web_y - 1)*t_plt_web*(dh.1 + 1.80mm); Rn2_1_plt_v3_web = 0.60*Fu_plt_web*Anv_plt_v3_web + Ubs_plt_v3_web*Fu_plt_web*Ant_plt_v3_web; Rn2_2_plt_v3_web = 0.60*Fy_plt_web*Agv_plt_v3_web + Ubs_plt_v3_web*Fu_plt_web*Ant_plt_v3_web; Rn2_plt_v3_web = min(Rn2_1_plt_v3_web, Rn2_2_plt_v3_web); phi*Rn2_plt_v3_web = phi_fragil*Rn2_plt_v3_web; Ru2_plt_v3_web = Pu_sp*alpha_Pu_web; DCR2_plt_v3_web = Ru2_plt_v3_web/phi*Rn2_plt_v3_web`
- Fu_plt_web: `400 MPa`
- Fy_plt_web: `n/a`
- t_plt_web: `9.5 mm`
- n_blt_web_x: `1`
- n_blt_web_y: `6`
- g_blt_web: `76.2 mm`
- p_blt_web: `76.2 mm`
- Le_blt_web_x2: `35 mm`
- dh.1: `17.46 mm`
- Ubs_plt_v3_web (= Ubs_web_v3_vg): `0.5`
- Agv_plt_v3_web: `665 mm2`
- Anv_plt_v3_web: `482.01 mm2`
- Agt_plt_v3_web: `3619.5 mm2`
- Ant_plt_v3_web: `2704.53 mm2`
- phi_fragil: `0.75`
- Rn2_1_plt_v3_web: `656.59 kN`
- Rn2_2_plt_v3_web: `640.66 kN`
- Rn2_plt_v3_web: `640.66 kN`
- phi*Rn2_plt_v3_web: `480.49 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru2_plt_v3_web = Pu_sp*alpha_Pu_web: `0 kN`
- DCR2_plt_v3_web: `0`
- Resultado: 🟢 Cumple

#### 5.2.3. ELR #3: fluencia por tracción en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: J4.1(a) (DRY: compute_element_tension_yielding_strength_j41a)`
- Ecuaciones: `Agt_v3_plt_web_expr = 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web; Agt_v3_plt_web = min(H_plt_web, Agt_v3_plt_web_expr)*t_plt_web; Rn3_plt_v3_web = Fy_plt_web*Agt_v3_plt_web; phi*Rn3_plt_v3_web = phi_no_ductil*Rn3_plt_v3_web; Ru3_plt_v3_web = alpha_Pu_web*Pu_sp; DCR3_plt_v3_web = Ru3_plt_v3_web/phi*Rn3_plt_v3_web`
- Fy_plt_web: `n/a`
- t_plt_web: `9.5 mm`
- H_plt_web: `431 mm`
- n_blt_web_x: `1`
- n_blt_web_y: `6`
- g_blt_web: `76.2 mm`
- p_blt_web: `76.2 mm`
- Agt_v3_plt_web_expr: `381 mm`
- Agt_v3_plt_web: `3619.5 mm2`
- phi_no_ductil: `0.9`
- Rn3_plt_v3_web: `904.88 kN`
- phi*Rn3_plt_v3_web: `814.39 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru3_plt_v3_web = alpha_Pu_web*Pu_sp: `0 kN`
- DCR3_plt_v3_web: `0`
- Resultado: 🟢 Cumple

#### 5.2.4. ELR #4: Rotura por tracción en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: J4.1(b) (DRY: compute_element_tension_rupture_strength_j41b)`
- Ecuaciones: `Agt_v3_plt_web_expr = 2*g_blt_web*(n_blt_web_x - 1)*sqrt(3)/3 + (n_blt_web_y - 1)*p_blt_web; Agt_v3_plt_web = min(H_plt_web, Agt_v3_plt_web_expr)*t_plt_web; Ant_v3_plt_web = Agt_v3_plt_web - n_blt_web_y*(dh.1 + 1.80mm)*t_plt_web; U_v3_plt_web = 1; Ae_v3_plt_web = Ant_v3_plt_web*U_v3_plt_web; Rn4_plt_v3_web = Fu_plt_web*Ae_v3_plt_web; phi*Rn4_plt_v3_web = phi_fragil*Rn4_plt_v3_web; Ru4_plt_v3_web = alpha_Pu_web*Pu_sp; DCR4_plt_v3_web = Ru4_plt_v3_web/phi*Rn4_plt_v3_web`
- Fu_plt_web: `400 MPa`
- t_plt_web: `9.5 mm`
- H_plt_web: `431 mm`
- n_blt_web_x: `1`
- n_blt_web_y: `6`
- g_blt_web: `76.2 mm`
- p_blt_web: `76.2 mm`
- dh.1: `17.46 mm`
- Agt_v3_plt_web_expr: `381 mm`
- Agt_v3_plt_web: `3619.5 mm2`
- Ant_v3_plt_web: `2521.54 mm2`
- U_v3_plt_web: `1`
- Ae_v3_plt_web: `2521.54 mm2`
- phi_fragil: `0.75`
- Rn4_plt_v3_web: `1008.62 kN`
- phi*Rn4_plt_v3_web: `756.46 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru4_plt_v3_web = alpha_Pu_web*Pu_sp: `0 kN`
- DCR4_plt_v3_web: `0`
- Resultado: 🟢 Cumple

### 5.3 Revisión de capacidad a compresión en la platina 1 de alma

#### 5.3.1. ELR #1: Pandeo por flexión en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: E3 y J4.4 (DRY: compute_plate_compression_buckling_strength)`
- Ecuaciones: `Lp_plt_p3(-)_web = min(gap_sp + 2*Le_blt_web_x1, g_blt_web); Ru1_plt_p3(-)_web = alpha_Pu_web*Pu_sp; phi*Rn1_plt_p3(-)_web = phi*Fcr_plt_p3(-)_web*H_plt_web*t_plt_web*n_plt_web; DCR1_plt_p3(-)_web = Ru1_plt_p3(-)_web/phi*Rn1_plt_p3(-)_web`
- Fy_plt_web: `250 MPa`
- H_plt_web: `431 mm`
- t_plt_web: `9.5 mm`
- Lp_plt_p3(-)_web: `76.2 mm`
- n_plt_web: `1`
- phi_no_ductil: `0.9`
- K: `0.65`
- r_plt_p3(-)_web: `2.75 mm`
- KL_r_plt_p3(-)_web: `17.98`
- Fe_plt_p3(-)_web: `6107.12 MPa`
- Fcr_plt_p3(-)_web: `250 MPa`
- Ecuacion Fcr usada: `Fcr_pc_col = Fy_pc_col`
- Ag_plt_p3(-)_web: `4094.5 mm2`
- phi*Rn1_plt_p3(-)_web: `921.26 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru1_plt_p3(-)_web: `0 kN`
- DCR1_plt_p3(-)_web: `0`
- Resultado: 🟢 Cumple

### 5.4 Revisión de capacidad a flexión en la platina 1 de alma alrededor de 1

#### 5.4.1. ELR #1: Fluencia por flexión en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: F11.1 (DRY: compute_rectangular_bar_flexural_yielding_strength_f111)`
- Ecuaciones: `Z_plt_m1_web = t_plt_web*H_plt_web^2/4; S_plt_m1_web = t_plt_web*H_plt_web^2/6; Rn1_plt_m1_web = min(Fy_plt_web*Z_plt_m1_web, 1.5*Fy_plt_web*S_plt_m1_web); phi*Rn1_plt_m1_web = phi_no_ductil*Rn1_plt_m1_web; Ru1_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web; DCR1_plt_m1_web = Ru1_plt_m1_web/phi*Rn1_plt_m1_web`
- Fy_plt_web: `250 MPa`
- t_plt_web: `9.5 mm`
- H_plt_web: `431 mm`
- Z_plt_m1_web: `441182.38 mm3`
- S_plt_m1_web: `294121.58 mm3`
- ex_blt_web: `76.2 mm`
- ey_blt_web: `0 mm`
- phi_no_ductil: `0.9`
- Rn1_plt_m1_web: `110.3 kN-m`
- phi*Rn1_plt_m1_web: `99.27 kN-m`
- Vu2_sp: `250 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru1_plt_m1_web: `19.05 kN-m`
- DCR1_plt_m1_web: `0.19`
- Resultado: 🟢 Cumple

#### 5.4.2. ELR #2: Pandeo lateral-torsional en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: F11.2 (DRY: compute_rectangular_bar_ltb_strength_f112)`
- Ecuaciones: `Z_plt_m1_web = t_plt_web*H_plt_web^2/4; S_plt_m1_web = t_plt_web*H_plt_web^2/6; Lb_plt_m1_web = max(2*Le_blt_web_x1 + gap_sp, g_plt_web); My_plt_m1_web = Fy_plt_web*S_plt_m1_web; Rn2_plt_m1_web = Mn_ltb(F11.2) <= Mp; phi*Rn2_plt_m1_web = phi_no_ductil*Rn2_plt_m1_web; Ru2_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web; DCR2_plt_m1_web = Ru2_plt_m1_web/phi*Rn2_plt_m1_web`
- Fy_plt_web: `250 MPa`
- E_plt_web: `200000 MPa`
- t_plt_web: `9.5 mm`
- H_plt_web: `431 mm`
- Z_plt_m1_web: `441182.38 mm3`
- S_plt_m1_web: `294121.58 mm3`
- Lb_plt_m1_web: `76.2 mm`
- My_plt_m1_web: `73.53 kN-m`
- Cb_plt_m1_web (inp): `1`
- ltb_case_id: `f112b_inelastic_ltb`
- Lb*d/t^2: `363.9`
- 0.08E/Fy: `64`
- 1.9E/Fy: `1520`
- Fcr: `n/a`
- phi_no_ductil: `0.9`
- Rn2_plt_m1_web: `102.6 kN-m`
- phi*Rn2_plt_m1_web: `92.34 kN-m`
- ex_blt_web: `76.2 mm`
- ey_blt_web: `0 mm`
- Vu2_sp: `250 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru2_plt_m1_web: `19.05 kN-m`
- DCR2_plt_m1_web: `0.21`
- Resultado: 🟢 Cumple

#### 5.4.3. ELR #3: Rotura por flexión en la platina 1 de alma

- Clausula: `Documento: AISC 360-22 | Seccion: J5.5 (DRY: compute_rectangular_bar_net_flexural_rupture_strength_j55)`
- Ecuaciones: `h = e1 + (n - 1)*s + e2; Znet_plt_m1_web = tp*h^2/4 - d'*tp*sum_{i=0}^{n-1}|e1 + i*s - h/2|; Rn3_plt_m1_web = Fu_plt_web*Znet_plt_m1_web; phi*Rn3_plt_m1_web = phi_fragil*Rn3_plt_m1_web; Ru3_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web; DCR3_plt_m1_web = Ru3_plt_m1_web/phi*Rn3_plt_m1_web`
- Fu_plt_web: `400 MPa`
- tp = t_plt_web: `9.5 mm`
- h = H_plt_web: `431 mm`
- d' = dh.1 + 1.80mm: `19.26 mm`
- e1 = Le_plt_web_y1: `25 mm`
- e2 = Le_plt_web_y2: `25 mm`
- s = p_plt_web: `76.2 mm`
- n = n_plt_web_y: `6`
- h calculado: `431 mm`
- sum_abs: `685.8 mm`
- Znet_plt_m1_web: `315685.26 mm3`
- phi_fragil: `0.75`
- Rn3_plt_m1_web: `126.27 kN-m`
- phi*Rn3_plt_m1_web: `94.71 kN-m`
- ex_blt_web: `76.2 mm`
- ey_blt_web: `0 mm`
- Vu2_sp: `250 kN`
- Pu_sp: `66.99 kN`
- alpha_Pu_web: `0`
- Ru3_plt_m1_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web: `19.05 kN-m`
- DCR3_plt_m1_web: `0.2`
- Resultado: 🟢 Cumple

### 5.5 Revisión de capacidad bajo al accion de fuerzas combinadas en la platina 1 de alma

#### 5.5.1. ELR #1: Interaccion entre cargas en la platina 1 de alma

- Clausula: `Documento: Criterio de interaccion solicitado por usuario (DRY: compute_plate_combined_force_interaction)`
- Ecuaciones: `DCR_case_1 = DCR_plt_m1_web + (DCR_plt_v3_web)^2 + (DCR_plt_v2_web)^4; DCR_case_2 = DCR_plt_m1_web + (DCR_plt_p3(-)_web)^2 + (DCR_plt_v2_web)^4; DCR_plt_Fcomb_web = max(DCR_case_1, DCR_case_2)`
- DCR_plt_v2_web (max de 5.1): `0.94`
- DCR_plt_v3_web (max de 5.2): `0.54`
- DCR_plt_p3(-)_web (max de 5.3): `0`
- DCR_plt_m1_web (max de 5.4): `0.21`
- DCR_case_1: `1.28`
- DCR_case_2: `0.99`
- Caso controlante: `Caso 1`
- DCR_plt_Fcomb_web: `1.28`
- Resultado: 🔴 No cumple
