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
- Numero de pernos en na mitad de aleta en direccion Z de la aleta (n_blt_flange_z) (inp): `1`
- Distancia de borde en direccion Z del grupo de pernos del ala (Le_blt_flange_z3) (inp): `30 mm`
- Distancia complementaria de borde en aleta (Le_blt_flange_z4): `26.9 mm`
- Gage entre columnas de pernos del ala (g_blt_flange) (inp): `40 mm`
- Tipo de perforacion por pernos grupo 2 ala (type_hole_flange) (inp): `standard`
- Distancia util entre filas internas de pernos de aleta (g1_blt_flange): `92 mm`
- Diametro de perforacion para pernos 2 (dh.2): `20.64 mm`

#### 1.1.4 Formulas de cálculo

- Formula ajuste distancia de borde: `Le_blt_web_x1' = Le_blt_web_x1 - tol_L_vg`
- Formula distancia vertical borde ala/pernos alma: `Le_blt_web_y3 = 0.5*(d_vg - (n_blt_web_y - 1)*p_blt_web)`
- Formula distancia neta respecto a kdet en alma: `Le_blt_web_y3.1 = Le_blt_web_y3 - kdet_vg`
- Formula distancia util entre filas internas de pernos de aleta: `g1_blt_flange = bf_vg - 2*(Le_blt_flange_z3 + (n_blt_flange_z - 1)*g_blt_flange)`
- Formula distancia complementaria de borde en aleta: `Le_blt_flange_z4 = 0.5*bfdet_vg - (Le_blt_flange_z3 + k1_vg + (n_blt_flange_z - 1)*g_blt_flange)`

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
- Longitud de platina de alma (L_plt_web): `85.8 mm`
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
- Formula calculo: `g1_plt_flange = bf_vg - 2*(Le_blt_flange_z3 + (n_blt_flange_z - 1)*g_blt_flange)`
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

## Paso 2 - Revisiónes de requerimientos de propiedades mecánicas y geométricas

### 2.1 Ámbito `VIGA`

#### Chequeo 2.1.1 - Separacion minima entre pernos del alma en direccion X (`g_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `g_blt_web >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.2 - Separacion maxima entre pernos del alma en direccion X (`g_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `g_blt_web <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.3 - Distancia minima a borde Le_blt_web_x1 para agujero estandar (`Le_blt_web_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_x1 >= Le_min; 25.4 mm >= 22.22 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.4 - Distancia maxima a borde Le_blt_web_x1 (`Le_blt_web_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_x1 <= Le_max; 25.4 mm <= 91.44 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.5 - Separacion minima entre pernos del alma en direccion Z (`p_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_web >= Smin; 76.2 mm >= 47.62 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.6 - Separacion maxima entre pernos del alma en direccion Z (`p_blt_web`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_web <= Smax; 76.2 mm <= 182.88 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.7 - Distancia minima a borde Le_blt_web_y3.1 para agujero estandar (`Le_blt_web_y3.1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_y3.1 >= Le_min; 13.5 mm >= 22.22 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🔴 No cumple

#### Chequeo 2.1.8 - Distancia maxima a borde Le_blt_web_y3.1 (`Le_blt_web_y3.1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_web_y3.1 <= Le_max; 13.5 mm <= 91.44 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.9 - Separacion minima entre pernos del ala en direccion X (`p_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_flange >= Smin; 60 mm >= 57.15 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.10 - Separacion maxima entre pernos del ala en direccion X (`p_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `p_blt_flange <= Smax; 60 mm <= 259.2 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.11 - Distancia minima a borde Le_blt_flange_x1 para agujero estandar (`Le_blt_flange_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_x1 >= Le_min; 50 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.12 - Distancia maxima a borde Le_blt_flange_x1 (`Le_blt_flange_x1`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_x1 <= Le_max; 50 mm <= 129.6 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.13 - Distancia minima a borde Le_blt_flange_z3 para agujero estandar (`Le_blt_flange_z3`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z3 >= Le_min; 30 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.14 - Distancia maxima a borde Le_blt_flange_z3 (`Le_blt_flange_z3`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z3 <= Le_max; 30 mm <= 129.6 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.15 - Distancia minima a borde Le_blt_flange_z4 para agujero estandar (`Le_blt_flange_z4`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z4 >= Le_min; 26.9 mm >= 25.4 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.16 - Distancia maxima a borde Le_blt_flange_z4 (`Le_blt_flange_z4`)

- Ámbito: `VIGA`
- Verificacion: `Le_blt_flange_z4 <= Le_max; 26.9 mm <= 129.6 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.17 - Separacion minima entre pernos del ala en direccion Z (`g_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `n_blt_flange_z >= 2; 1 >= 2`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟠 No aplica (cumple)

#### Chequeo 2.1.18 - Separacion maxima entre pernos del ala en direccion Z (`g_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `n_blt_flange_z >= 2; 1 >= 2`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟠 No aplica (cumple)

#### Chequeo 2.1.19 - Separacion minima entre pernos del ala en direccion Z (g1) (`g1_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `g1_blt_flange >= Smin; 92 mm >= 57.15 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.3`
- Resultado: 🟢 Cumple

#### Chequeo 2.1.20 - Separacion maxima entre pernos del ala en direccion Z (g1) (`g1_blt_flange`)

- Ámbito: `VIGA`
- Verificacion: `g1_blt_flange <= Smax; 92 mm <= 259.2 mm`
- Clausula: `Documento: AISC 360-22 | Seccion: AISC 360-22 J3.6`
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

- 🔴 `2.1` `VIGA`: total=20, cumple=19, no_cumple=1, numerales_no_cumplen=2.1.7
- 🟢 `2.2` `PLATINA_1`: total=10, cumple=10, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `2.3` `PERNOS_1`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `2.4` `PLATINA_2`: total=12, cumple=12, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `2.5` `PERNOS_2`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno

## Paso 3 - Metodo ICR/Elastic para grupo de pernos 1

### 3.1 Metodo ICR/Elastic

- Metodo seleccionado: `icr`
- Pu_sp: `66.99 kN`
- Vu2_sp: `250 kN`
- Formula ex_blt_web: `ex_blt_web = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x - 1)*g_blt_web`
- ex_blt_web: `76.2 mm`
- ey_blt_web: `0 mm`
- Fuente excentricidad: `splice_formula_ex_plus_input_ey`
- Formula Muz_blt_web: `Muz_blt_web = Vu2_sp*ex_blt_web - Pu_sp*ey_blt_web`
- Muz_blt_web: `19.05 kN-m`
- Demanda (metodo activo): `258.82 kN`
- Capacidad (metodo activo): `1617.97 kN`
- DCR (metodo activo): `0.16`
- Residual final ICR: `0.01`
- Iteraciones ICR: `19`
- Coeficiente Cu (ICR): `4.92`
- Clausula: `Documento: AISC 360-22 (motor interno ICR/Elastic) | Seccion: Metodo configurable de pernos grupo 1 (ICR / Elastic)`
- Resultado: 🟢 Cumple
