# Memoria de Cálculo

- Proyecto: `proj_bseep_si_demo`
- Caso: `case_si_bseep_8es_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bseep_8es`
- Estado global: `🔴 No cumple`

## Paso 1 - Propiedades geométricas, mecánicas y fabricacion

Propiedades organizadas por ambito.

### 1.1 Ámbito `BEAM_IZQ`

#### 1.1.1 Resumen de geometria

- Perfil de viga izquierda (perfil_vgizq) (inp): `W21X68`
- Tipo de acero del perfil de viga izquierda (tipo_acero_perfil_vgizq) (inp): `ASTM A572 Gr 50`
- Demanda de ductilidad de viga izquierda (demanda_ductilidad_vgizq) (inp): `high`
- Luz libre de viga izquierda (Llb_vgizq) (inp): `7500 mm`
- Longitud sin conectores desde cara de columna (Lnc_vgizq) (inp): `1000 mm`
- Longitud de zona protegida (Lpz_vgizq): `458.53 mm`

### 1.2 Ámbito `BEAM_DER`

#### 1.2.1 Resumen de geometria

- Perfil de viga derecha (perfil_vgder) (inp): `W21X68`
- Tipo de acero del perfil de viga derecha (tipo_acero_perfil_vgder) (inp): `ASTM A572 Gr 50`
- Demanda de ductilidad de viga derecha (demanda_ductilidad_vgder) (inp): `high`
- Luz libre de viga derecha (Llb_vgder) (inp): `7500 mm`
- Longitud sin conectores desde cara de columna (Lnc_vgder) (inp): `1000 mm`
- Longitud de zona protegida (Lpz_vgder): `458.53 mm`

### 1.3 Ámbito `COLUMN`

#### 1.3.1 Resumen de geometria

- Perfil de columna (shape_col) (inp): `HEB 500`
- Tipo de acero del perfil de columna (tipo_acero_perfil_col) (inp): `ASTM A572 Gr 50`
- Altura de columna (d_col) (inp): `500 mm`
- Espesor de alma de columna (tw_col) (inp): `14.5 mm`
- Proyeccion de columna sobre vigas (St_col) (inp): `2500 mm`
- Distancia al punto de inflexion superior (ht_col) (inp): `1250 mm`
- Distancia al punto de inflexion inferior (hb_col) (inp): `1250 mm`
- gage horizontal de pernos en columna lado izquierda (g_b_col_vgizq) (inp): `150 mm`
- Distancia exterior ajustada lado izquierda (pso_vgizq): `50.75 mm`
- Distancia interior ajustada lado izquierda (psi_vgizq): `50.75 mm`
- Diametro de perforacion en columna lado izquierda (dh_col_vgizq): `28.57 mm`
- Parametro C de columna lado izquierda (C_col_vgizq): `117.4 mm`
- Parametro s de columna lado izquierda (s_col_vgizq): `106.07 mm`
- Distancia h1 de columna lado izquierda (h1_col_vgizq): `672.3 mm`
- Distancia h2 de columna lado izquierda (h2_col_vgizq): `577.3 mm`
- Distancia h3 de columna lado izquierda (h3_col_vgizq): `459.9 mm`
- Distancia h4 de columna lado izquierda (h4_col_vgizq): `364.9 mm`
- gage horizontal de pernos en columna lado derecha (g_b_col_vgder) (inp): `150 mm`
- Distancia exterior ajustada lado derecha (pso_vgder): `50.75 mm`
- Distancia interior ajustada lado derecha (psi_vgder): `50.75 mm`
- Diametro de perforacion en columna lado derecha (dh_col_vgder): `28.57 mm`
- Parametro C de columna lado derecha (C_col_vgder): `117.4 mm`
- Parametro s de columna lado derecha (s_col_vgder): `106.07 mm`
- Distancia h1 de columna lado derecha (h1_col_vgder): `672.3 mm`
- Distancia h2 de columna lado derecha (h2_col_vgder): `577.3 mm`
- Distancia h3 de columna lado derecha (h3_col_vgder): `459.9 mm`
- Distancia h4 de columna lado derecha (h4_col_vgder): `364.9 mm`

### 1.4 Ámbito `END_PLATE_DER`

#### 1.4.1 Resumen de geometria

- Altura de platina extremo de viga derecha (Hpe_vgder): `756 mm`
- Ancho de platina extremo de viga derecha (Bpe_vgder) (inp): `235 mm`
- Espesor de platina extremo de viga derecha (tpe_vgder) (inp): `25.4 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgder) (inp): `60 mm`
- Distancia entre filas de pernos (pb_pe_vgder) (inp): `95 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgder) (inp): `50 mm`
- Distancia interior a fila de pernos (pfi_pe_vgder) (inp): `50 mm`
- Diametro de perforacion de perno (dh_pe_vgder): `28.57 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgder) (inp): `150 mm`
- Parametro s de platina extremo derecha (s_pe_vgder): `93.87 mm`
- Distancia h1 de platina extremo derecha (h1_pe_vgder): `672.3 mm`
- Distancia h2 de platina extremo derecha (h2_pe_vgder): `577.3 mm`
- Distancia h3 de platina extremo derecha (h3_pe_vgder): `459.9 mm`
- Distancia h4 de platina extremo derecha (h4_pe_vgder): `364.9 mm`

### 1.5 Ámbito `END_PLATE_IZQ`

#### 1.5.1 Resumen de geometria

- Altura de platina extremo de viga izquierda (Hpe_vgizq): `756 mm`
- Ancho de platina extremo de viga izquierda (Bpe_vgizq) (inp): `235 mm`
- Espesor de platina extremo de viga izquierda (tpe_vgizq) (inp): `25.4 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgizq) (inp): `60 mm`
- Distancia entre filas de pernos (pb_pe_vgizq) (inp): `95 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgizq) (inp): `50 mm`
- Distancia interior a fila de pernos (pfi_pe_vgizq) (inp): `50 mm`
- Diametro de perforacion de perno (dh_pe_vgizq): `28.57 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgizq) (inp): `150 mm`
- Parametro s de platina extremo izquierda (s_pe_vgizq): `93.87 mm`
- Distancia h1 de platina extremo izquierda (h1_pe_vgizq): `672.3 mm`
- Distancia h2 de platina extremo izquierda (h2_pe_vgizq): `577.3 mm`
- Distancia h3 de platina extremo izquierda (h3_pe_vgizq): `459.9 mm`
- Distancia h4 de platina extremo izquierda (h4_pe_vgizq): `364.9 mm`

### 1.6 Ámbito `END_PLATE_STIFFENER_DER`

#### 1.6.1 Nota técnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ámbito: `END_PLATE_STIFFENER_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgder = pfo_pe_vgder + pb_pe_vgder + de_pe_vgder; L_pest_vgder = h_pest_vgder/tan(30 deg); Ed_pest_vgder = 25 mm`

### 1.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### 1.7.1 Nota técnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgizq = pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq; L_pest_vgizq = h_pest_vgizq/tan(30 deg); Ed_pest_vgizq = 25 mm`

### 1.8 platinas de continuidad

#### 1.8.1 Resumen de geometria

- Uso de platinas de continuidad (usar_pc_col) (inp): `True`
- Tipo de acero de platina de continuidad (tipo_acero_pc_col) (inp): `ASTM A572 Gr 50`
- Espesor de platina de continuidad (t_pc_col) (inp): `15.9 mm`
- Ancho base de platina de continuidad (b1_pc_col) (inp): `130 mm`
- Ancho b1.1 de platina de continuidad (b1.1_pc_col): `130 mm`
- Ancho b1.2 de platina de continuidad (b1.2_pc_col): `145.9 mm`
- Distancia de recorte 1 de platina de continuidad (Clip1_pc_col): `65 mm`
- Longitud util 1 de platina de continuidad (L1_pc_col): `441 mm`
- Longitud util 2 de platina de continuidad (L2_pc_col): `311 mm`
- Distancia de recorte 2 de platina de continuidad (Clip2_pc_col): `21.9 mm`
- Ancho neto de platina de continuidad (b2_pc_col): `108.1 mm`

### 1.9 Ámbito `BOLTS_DER`

### 1.10 Ámbito `BOLTS_IZQ`

### 1.11 Ámbito `TABLE_6_1_DER`

### 1.12 Ámbito `TABLE_6_1_IZQ`

### 1.13 Ámbito `WELD_1_VGDER`

### 1.14 Ámbito `WELD_1_VGIZQ`

### 1.15 Ámbito `WELD_2_VGDER`

### 1.16 Ámbito `WELD_2_VGIZQ`

### 1.17 Ámbito `WELD_3_VGDER`

### 1.18 Ámbito `WELD_3_VGIZQ`

### 1.19 Ámbito `WELD_4_VGDER`

### 1.20 Ámbito `WELD_4_VGIZQ`

### 1.21 Ámbito `WELD_5_COL`

#### 1.21.1 Resumen de geometria

- Tipo de soldadura #5 de platina de continuidad (tipo_w5_col) (inp): `fillet`
- Resistencia del electrodo de soldadura #5 (Fexx_w5_col) (inp): `490 MPa`
- Espesor/size de soldadura #5 (w_w5_col) (inp): `12.7 mm`
- Numero de lineas de soldadura #5 (nl_w5_col) (inp): `2`
- Separacion de extremos de soldadura #5 (L_gap_w5_col) (inp): `12.7 mm`
- Factor de direccion/sistema de soldadura #5 (kds_w5_col) (inp): `1.5`
- Longitud efectiva de soldadura #5 (L_w5_col): `82.7 mm`

### 1.22 platina de enchape del alma

#### 1.22.1 Resumen de geometria

- Uso de platina de enchape del alma (usar_dp_col) (inp): `True`
- Tipo de acero de platina de enchape del alma (tipo_acero_dp_col) (inp): `ASTM A572 Gr 50`
- Espesor de platina de enchape del alma (t_dp_col) (inp): `9.5 mm`
- Numero de platinas de enchape del alma (n_dp_col) (inp): `1`
- Altura neta de panel zone en columna para enchape (dz_dp_col): `444 mm`
- Ancho neto gobernante entre vigas para enchape (wz_dp_col): `501.2 mm`

### 1.23 Ámbito `WELD_6_COL`

#### 1.23.1 Resumen de geometria

- Tipo de soldadura #6 de platina de continuidad (tipo_w6_col) (inp): `fillet`
- Resistencia del electrodo de soldadura #6 (Fexx_w6_col) (inp): `490 MPa`
- Espesor/size de soldadura #6 (w_w6_col) (inp): `12.7 mm`
- Numero de lineas de soldadura #6 (nl_w6_col) (inp): `2`
- Separacion de extremos de soldadura #6 (L_gap_w6_col) (inp): `13 mm`
- Factor de direccion/sistema de soldadura #6 (kds_w6_col) (inp): `1`
- Longitud efectiva de soldadura #6 (Lws_col): `285 mm`

### 1.24 Ámbito `WELD_7_COL`

#### 1.24.1 Resumen de geometria

- Tipo de soldadura #7 (tipo_w7_col) (inp): `plug`
- Resistencia del electrodo de soldadura #7 (Fexx_w7_col) (inp): `490 MPa`
- Espesor/size de soldadura #7 (w_w7_col) (inp): `8 mm`
- Numero de lineas de soldadura #7 (nl_w7_col) (inp): `1`

## Paso 2 - Especificaciones técnicas

Especificaciones tecnicas organizadas por ambito.

### 2.1 Ámbito `BEAM_IZQ`

### 2.2 Ámbito `BEAM_DER`

### 2.3 Ámbito `COLUMN`

#### 2.3.1 Nota técnica - Ubicacion de la conexión de placa de extremo en columna

- Ámbito: `COLUMN`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (2)`
- Requisito: `La placa de extremo debe conectarse al ala de la columna.`

### 2.4 Ámbito `END_PLATE_DER`

### 2.5 Ámbito `END_PLATE_IZQ`

### 2.6 Ámbito `END_PLATE_STIFFENER_DER`

### 2.7 Ámbito `END_PLATE_STIFFENER_IZQ`

### 2.8 Ámbito `CONTINUITY_PLATE_COL`

### 2.9 Ámbito `BOLTS_DER`

#### 2.9.1 Nota técnica - Requisitos de instalacion para conjuntos empernados (right beam)

- Ámbito: `BOLTS_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.`

#### 2.9.2 Nota técnica - Control y aseguramiento de calidad para conjuntos empernados (right beam)

- Ámbito: `BOLTS_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 2.10 Ámbito `BOLTS_IZQ`

#### 2.10.1 Nota técnica - Requisitos de instalacion para conjuntos empernados (left beam)

- Ámbito: `BOLTS_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.`

#### 2.10.2 Nota técnica - Control y aseguramiento de calidad para conjuntos empernados (left beam)

- Ámbito: `BOLTS_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 2.11 Ámbito `TABLE_6_1_DER`

### 2.12 Ámbito `TABLE_6_1_IZQ`

### 2.13 Ámbito `WELD_1_VGDER`

### 2.14 Ámbito `WELD_1_VGIZQ`

### 2.15 Ámbito `WELD_2_VGDER`

### 2.16 Ámbito `WELD_2_VGIZQ`

### 2.17 Ámbito `WELD_3_VGDER`

### 2.18 Ámbito `WELD_3_VGIZQ`

### 2.19 Ámbito `WELD_4_VGDER`

### 2.20 Ámbito `WELD_4_VGIZQ`

### 2.21 Ámbito `WELD_5_COL`

### 2.22 Ámbito `DOUBLER_PLATE_COL`

### 2.23 Ámbito `WELD_6_COL`

### 2.24 Ámbito `WELD_7_COL`

## Paso 3 - Revisiónes de requerimientos de propiedades mecánicas y geométricas

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### 3.1 Ámbito `BEAM_IZQ`

#### Chequeo 3.1.1 - Familia de perfil de viga permitida para precalificación (viga izquierda) (`perfil_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `perfil_vgizq in {W, HEA, HEB, IPE}; 'W21X68' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.2 - Ancho de placa de extremo vs ancho de ala de viga (left beam) (`bp_pe_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `bp_pe_vgizq <= bf_vgizq + margin (25 mm); 235 mm <= 235 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.3 - Separacion minima de gage de pernos (left beam) (`g_b_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `g_b_vgizq >= 3db; 150 mm >= 76.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.4 - Longitud sin conectores de cortante desde la cara de columna (left beam) (`Lnc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Lnc_vgizq >= 1.5d_vgizq; 1000 mm >= 804 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.5 - Criterio de despeje de viga con umbral Sc y S (left beam) (`Sc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Sc_vgizq = St_col - pfo_vgizq - pb_vgizq; S_vgizq = 0.5*sqrt(bcf*g_vgizq); Sc_vgizq > S_vgizq => 2355.000 mm > 106.066 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.6 - Relacion luz libre/peralte por sistema de marco (left beam) (`Llb_vgizq/d_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Llb_vgizq/d_vgizq >= 7 (SMF); 13.99 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.7 - Compacidad ancho-espesor del ala de viga (left beam) (`lambda_f_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `lambda_f_vgizq <= lambda_f_limit; 6.03 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.8 - Compacidad ancho-espesor del alma de viga (left beam) (`lambda_w_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `lambda_w_vgizq <= lambda_w_limit; 43.63 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### 3.2 Ámbito `BEAM_DER`

#### Chequeo 3.2.1 - Familia de perfil de viga permitida para precalificación (viga derecha) (`perfil_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `perfil_vgder in {W, HEA, HEB, IPE}; 'W21X68' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.2 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `bp_pe_vgder <= bf_vgder + margin (25 mm); 235 mm <= 235 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.3 - Separacion minima de gage de pernos (right beam) (`g_b_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `g_b_vgder >= 3db; 150 mm >= 76.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.4 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 804 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.5 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Sc_vgder = St_col - pfo_vgder - pb_vgder; S_vgder = 0.5*sqrt(bcf*g_vgder); Sc_vgder > S_vgder => 2355.000 mm > 106.066 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.6 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Llb_vgder/d_vgder >= 7 (SMF); 13.99 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.7 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `lambda_f_vgder <= lambda_f_limit; 6.03 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.8 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `lambda_w_vgder <= lambda_w_limit; 43.63 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### 3.3 Ámbito `COLUMN`

#### Chequeo 3.3.1 - Familia de perfil de columna permitida para precalificación (`shape_col`)

- Ámbito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'HEB 500' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.2 - Peralte máximo del perfil de columna (W36/W920) (`d_col`)

- Ámbito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 500 mm <= 920 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.3 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ámbito: `COLUMN`
- Verificacion: `bp <= bcf; 235 mm <= 300 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.4 - Condicion de conexión columna-losa (`col_losa`)

- Ámbito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.5 - Proyeccion de columna minima por encima de las vigas (`St_col`)

- Ámbito: `COLUMN`
- Verificacion: `St_col >= pfo_pe_vgder + pb_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq + 12.5 mm; 2500.000 mm >= 217.500 mm; 2500.000 mm >= 217.500 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje superior de columna)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.6 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ámbito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 5.36 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.7 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ámbito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 26.9 adim <= 49.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.8 - Espesor individual minimo del alma de columna (`tw_col`)

- Ámbito: `COLUMN`
- Verificacion: `tw_col >= (dz_dp_col + wz_dp_col)/90 con dz_dp_col=d_col-2*tf_col, wz_dp_col=min{d_<lado>-2*tf_<lado>}; 14.5 mm >= 10.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

### 3.4 Ámbito `END_PLATE_DER`

#### Chequeo 3.4.1 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [228.6 mm, 235 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.5 Ámbito `END_PLATE_IZQ`

#### Chequeo 3.5.1 - Desigualdades explicitas de ancho de placa de extremo (left beam) (`bp_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf; [min,max] = [228.6 mm, 235 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.6 Ámbito `END_PLATE_STIFFENER_DER`

#### Chequeo 3.6.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (right beam) (`h_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder = pfo_pe_vgder + pb_pe_vgder + de_pe_vgder; 205.000 mm = 50.000 mm + 95.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.2 - Espesor minimo requerido del rigidizador (right beam) (`t_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `t_pest_vgder >= tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 15.9 mm >= 10.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.3 - Limite de pandeo local ancho-espesor del rigidizador (right beam) (`h_pest_vgder/t_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder/t_pest_vgder <= 0.56*sqrt(E_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 12.89 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.4 - Despeje del gage de pernos con espesor del rigidizador (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `g_b_vgder >= 2emin + t_pest_vgder; 150 mm >= 79.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 3.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### Chequeo 3.7.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (left beam) (`h_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq = pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq; 205.000 mm = 50.000 mm + 95.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.2 - Espesor minimo requerido del rigidizador (left beam) (`t_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `t_pest_vgizq >= tw_vgizq*(Fy_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 15.9 mm >= 10.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.3 - Limite de pandeo local ancho-espesor del rigidizador (left beam) (`h_pest_vgizq/t_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq/t_pest_vgizq <= 0.56*sqrt(E_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 12.89 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.4 - Despeje del gage de pernos con espesor del rigidizador (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `g_b_vgizq >= 2emin + t_pest_vgizq; 150 mm >= 79.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 3.8 platina de continuidad

#### Chequeo 3.8.1 - Ancho máximo de platina de continuidad (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `b1_pc_col <= (bf_col - tw_col - n_dp_col*t_dp_col)/2; 130 mm <= 138 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 J10.8 / SDH 4th ed. 2024`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.2 - Ancho minimo de platina de continuidad (viga der) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `b1_pc_col >= bf_vgder/2 + 0.5*tw_col + 0.5*n_dp_col*t_dp_col; 130 mm >= 117 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 J10.8`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.3 - Ancho minimo alterno de platina de continuidad (viga der) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `b1_pc_col >= (bf_vgder - tw_col)/2; 130 mm >= 97.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: SDH 4th ed. 2024`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.4 - Ancho minimo de platina de continuidad (viga izq) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `b1_pc_col >= bf_vgizq/2 + 0.5*tw_col + 0.5*n_dp_col*t_dp_col; 130 mm >= 117 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 J10.8`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.5 - Ancho minimo alterno de platina de continuidad (viga izq) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `b1_pc_col >= (bf_vgizq - tw_col)/2; 130 mm >= 97.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: SDH 4th ed. 2024`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.6 - Espesor minimo de platina de continuidad (viga izq) (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `t_pc_col >= min{tf_vgizq/2, tf_vgder/2, b1_pc_col/16, (b1_pc_col/0.55)*sqrt(Fy_pc_col/E_pc_col)}; 15.9 mm >= 8.12 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 J10.8`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.7 - Espesor minimo global de platina de continuidad (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `t_pc_col >= (b1_pc_col/0.45)*sqrt(Fy_pc_col/E_pc_col); 15.9 mm >= 12 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Requisito de proyecto (si usar_pc_col=true)`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.8 - Limite ancho/espesor de platina de continuidad (b/t) (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `t_pc_col >= (max(b1_pc_col, b2_pc_col)/0.56)*sqrt(Ry_pc_col*Fy_pc_col/E_pc_col); 15.9 mm >= 10.11 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22 Eq. (E3-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.9 - Espesor minimo de platina de continuidad (conexión a dos lados, 75% del ala mas gruesa) (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificacion: `t_pc_col >= 0.75*max(tf_vgizq, tf_vgder); 15.9 mm >= 13.05 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6f(1)(b)`
- Resultado: 🟢 Cumple

### 3.9 Ámbito `BOLTS_DER`

#### Chequeo 3.9.1 - El tipo de apriete del perno debe ser una categoria reconocida (right beam) (`tight_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificacion: `tight_bolt_vgder in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.2 - Los pernos deben estar pretensionados salvo que una conexión especifica permita lo contrario (right beam) (`tight_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificacion: `tight_bolt_vgder == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.3 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (right beam) (`std_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificacion: `std_bolt_vgder in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### 3.10 Ámbito `BOLTS_IZQ`

#### Chequeo 3.10.1 - El tipo de apriete del perno debe ser una categoria reconocida (left beam) (`tight_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificacion: `tight_bolt_vgizq in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.2 - Los pernos deben estar pretensionados salvo que una conexión especifica permita lo contrario (left beam) (`tight_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificacion: `tight_bolt_vgizq == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.3 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (left beam) (`std_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificacion: `std_bolt_vgizq in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### 3.11 Ámbito `TABLE_6_1_DER`

#### Chequeo 3.11.1 - Distancia de borde en de (right beam) (`de_pe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `de_pe_vgder >= emin; 60 mm >= 31.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.2 - Limites de distancia en fila exterior de pernos (right beam) (`pfo_pe_vgder - pso_pe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `pso_pe_vgder = pfo_pe_vgder + 0.5*tf_vgder - 0.5*t_pc_col; pso_pe_vgder >= emin; pfo_pe_vgder <= 51 mm; pfo_pe_vgder >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.3 - Limites de distancia en fila interior de pernos (right beam) (`pfi_pe_vgder - psi_pe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `pfi_pe_vgder >= emin; pfi_pe_vgder <= 51 mm; pfi_pe_vgder >= 41 mm; psi_pe_vgder = pfi_pe_vgder + 0.5*tf_vgder - 0.5*t_pc_col; psi_pe_vgder > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.4 - Separacion minima vertical entre pernos (right beam) (`pb_pe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `pb_pe_vgder >= 3db; pb_pe_vgder <= 95.000 mm; pb_pe_vgder >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.5 - Limites de espesor del ala de viga (right beam) (`tf_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `tf_vgder in [tf_vgder_min, tf_vgder_max]; 14.29 mm <= 17.4 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.6 - Limites de ancho del ala de viga (right beam) (`bf_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `bf_vgder in [bf_vgder_min, bf_vgder_max]; 190.5 mm <= 210 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.7 - Limites de peralte de la viga conectada (right beam) (`d_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `d_vgder in [d_vgder_min, d_vgder_max]; 457.2 mm <= 536 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.8 - Limites de espesor de placa de extremo (right beam) (`tpe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `tpe_vgder in [tpe_vgder_min, tpe_vgder_max]; 19.05 mm <= 25.4 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.9 - Limites de separacion horizontal de pernos (right beam) (`g_b_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `g_b_vgder in [g_b_vgder_min, g_b_vgder_max]; 127 mm <= 150 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.12 Ámbito `TABLE_6_1_IZQ`

#### Chequeo 3.12.1 - Distancia de borde en de (left beam) (`de_pe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `de_pe_vgizq >= emin; 60 mm >= 31.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.2 - Limites de distancia en fila exterior de pernos (left beam) (`pfo_pe_vgizq - pso_pe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `pso_pe_vgizq = pfo_pe_vgizq + 0.5*tf_vgizq - 0.5*t_pc_col; pso_pe_vgizq >= emin; pfo_pe_vgizq <= 51 mm; pfo_pe_vgizq >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.3 - Limites de distancia en fila interior de pernos (left beam) (`pfi_pe_vgizq - psi_pe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `pfi_pe_vgizq >= emin; pfi_pe_vgizq <= 51 mm; pfi_pe_vgizq >= 41 mm; psi_pe_vgizq = pfi_pe_vgizq + 0.5*tf_vgizq - 0.5*t_pc_col; psi_pe_vgizq > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.4 - Separacion minima vertical entre pernos (left beam) (`pb_pe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `pb_pe_vgizq >= 3db; pb_pe_vgizq <= 95.000 mm; pb_pe_vgizq >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.5 - Limites de espesor del ala de viga (left beam) (`tf_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `tf_vgizq in [tf_vgizq_min, tf_vgizq_max]; 14.29 mm <= 17.4 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.6 - Limites de ancho del ala de viga (left beam) (`bf_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `bf_vgizq in [bf_vgizq_min, bf_vgizq_max]; 190.5 mm <= 210 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.7 - Limites de peralte de la viga conectada (left beam) (`d_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `d_vgizq in [d_vgizq_min, d_vgizq_max]; 457.2 mm <= 536 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.8 - Limites de espesor de placa de extremo (left beam) (`tpe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `tpe_vgizq in [tpe_vgizq_min, tpe_vgizq_max]; 19.05 mm <= 25.4 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.12.9 - Limites de separacion horizontal de pernos (left beam) (`g_b_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `g_b_vgizq in [g_b_vgizq_min, g_b_vgizq_max]; 127 mm <= 150 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.13 Ámbito `WELD_1_VGDER`

#### Chequeo 3.13.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w1_vgder`)

- Ámbito: `WELD_1_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w1_vgder == cjp; t_pest_vgder = 15.900 mm; tipo_w1_vgder = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.14 Ámbito `WELD_1_VGIZQ`

#### Chequeo 3.14.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w1_vgizq`)

- Ámbito: `WELD_1_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w1_vgizq == cjp; t_pest_vgizq = 15.900 mm; tipo_w1_vgizq = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.15 Ámbito `WELD_2_VGDER`

#### Chequeo 3.15.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w2_vgder`)

- Ámbito: `WELD_2_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w2_vgder == cjp; t_pest_vgder = 15.900 mm; tipo_w2_vgder = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.16 Ámbito `WELD_2_VGIZQ`

#### Chequeo 3.16.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w2_vgizq`)

- Ámbito: `WELD_2_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w2_vgizq == cjp; t_pest_vgizq = 15.900 mm; tipo_w2_vgizq = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.17 Ámbito `WELD_3_VGDER`

#### Chequeo 3.17.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (right beam) (`weld_ep_web_vgder`)

- Ámbito: `WELD_3_VGDER`
- Verificacion: `weld_ep_web_vgder in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.18 Ámbito `WELD_3_VGIZQ`

#### Chequeo 3.18.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (left beam) (`weld_ep_web_vgizq`)

- Ámbito: `WELD_3_VGIZQ`
- Verificacion: `weld_ep_web_vgizq in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.19 Ámbito `WELD_4_VGDER`

#### Chequeo 3.19.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha) (`tipo_w4_vgder`)

- Ámbito: `WELD_4_VGDER`
- Verificacion: `si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 8 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 8.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.20 Ámbito `WELD_4_VGIZQ`

#### Chequeo 3.20.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda) (`tipo_w4_vgizq`)

- Ámbito: `WELD_4_VGIZQ`
- Verificacion: `si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 8 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 8.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.21 Ámbito `WELD_5_COL`

#### Chequeo 3.21.1 - Tamano minimo de soldadura de filete (#5, columna) (`w_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `w_w5_col >= wmin_j24_w5_col; 12.7 mm >= 6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Tabla J2.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.21.2 - Tamano máximo de soldadura de filete (#5, columna) (`w_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `w_w5_col <= wmax_j2b_w5_col; 12.7 mm <= 13.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2b`
- Resultado: 🟢 Cumple

#### Chequeo 3.21.3 - Longitud minima de soldadura de filete para diseno por resistencia (#5, columna) (`L_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `L_w5_col >= 4*w_w5_col; 82.7 mm >= 50.8 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(c)`
- Resultado: 🟢 Cumple

#### Chequeo 3.21.4 - Longitud efectiva de soldadura de filete cargada en el extremo (#5, columna) (`L_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `l/w = 6.512; beta = 1.000; l_eff_w5_col = 82.700 mm; si l/w<=100 => l_eff=l; si 100<l/w<=300 => l_eff=beta*l; si l/w>300 => l_eff=180w`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(d) + Eq. (J2-1)`
- Resultado: 🟢 Cumple

#### Chequeo 3.21.5 - Longitud maxima de soldadura #5 cuando tipo_w5_col es fillet (`L_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `L_w5_col <= b2_pc_col - 2*w_w5_col; 82.7 mm <= 82.7 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 3.21.6 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `tipo_w5_col in {fillet, cjp}; 'fillet' in {fillet, cjp}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 3.21.7 - Tamano minimo de soldadura #5 cuando tipo_w5_col es fillet (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `if tipo_w5_col='fillet': w_w5_col >= 0.75*t_pc_col; w_w5_col=12.7 mm; 0.75*t_pc_col=11.93 mm; t_pc_col=15.9 mm; tipo_w5_col='fillet'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

### 3.22 Ámbito `DOUBLER_PLATE_COL`

#### Chequeo 3.22.1 - Espesor individual minimo de platina de enchape del alma (`t_dp_col`)

- Ámbito: `DOUBLER_PLATE_COL`
- Verificacion: `t_dp_col >= (dz_dp_col + wz_dp_col)/90 con dz_dp_col=d_col-2*tf_col, wz_dp_col=min{d_<lado>-2*tf_<lado>}; 9.5 mm >= 10.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6e.2`
- Resultado: 🔴 No cumple

### 3.23 Ámbito `WELD_6_COL`

#### Chequeo 3.23.1 - Tipo de soldadura #6 permitido (`tipo_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `tipo_w6_col in {cjp, pjp, fillet}; 'fillet' in {cjp, pjp, fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 3.23.2 - Tamano minimo de soldadura de filete (#6, columna) (`w_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `w_w6_col >= wmin_j24_w6_col; 12.7 mm >= 6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Tabla J2.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.23.3 - Tamano máximo de soldadura de filete (#6, columna) (`w_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `w_w6_col <= wmax_j2b_w6_col; 12.7 mm <= 12.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2b`
- Resultado: 🔴 No cumple

#### Chequeo 3.23.4 - Longitud minima de soldadura de filete para diseno por resistencia (#6, columna) (`L_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `L_w6_col >= 4*w_w6_col; 285 mm >= 50.8 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(c)`
- Resultado: 🟢 Cumple

#### Chequeo 3.23.5 - Longitud efectiva de soldadura de filete cargada en el extremo (#6, columna) (`L_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `l/w = 22.441; beta = 1.000; l_eff_w6_col = 285.000 mm; si l/w<=100 => l_eff=l; si 100<l/w<=300 => l_eff=beta*l; si l/w>300 => l_eff=180w`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(d) + Eq. (J2-1)`
- Resultado: 🟢 Cumple

#### Chequeo 3.23.6 - Longitud maxima de soldadura #6 cuando tipo_w6_col es fillet (`L_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `L_w6_col <= L2_pc_col - 2*w_w6_col; 285 mm <= 285.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 3.23.7 - Longitud maxima de soldadura #6 en columna (`Lws_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `Lws_col <= d_col - 2*(kdet_col + 6*tw_col); 285 mm <= 216 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 358-22 Seccion 6.3`
- Resultado: 🔴 No cumple

#### Chequeo 3.23.8 - Longitud minima de soldadura #6 en columna (`Lws_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `Lws_col >= d_col - 2*(kdet_col + 4*tw_col); 285 mm >= 274 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 358-22 Seccion 6.3`
- Resultado: 🟢 Cumple

### 3.24 Ámbito `WELD_7_COL`

### 3.25 Resumen de chequeos por ámbito

- 🟢 `3.1` `BEAM_IZQ`: total=8, cumple=8, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.2` `BEAM_DER`: total=8, cumple=8, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.3` `COLUMN`: total=8, cumple=8, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.4` `END_PLATE_DER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.5` `END_PLATE_IZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.6` `END_PLATE_STIFFENER_DER`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.7` `END_PLATE_STIFFENER_IZQ`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.8` `CONTINUITY_PLATE_COL`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.9` `BOLTS_DER`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.10` `BOLTS_IZQ`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.11` `TABLE_6_1_DER`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.12` `TABLE_6_1_IZQ`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.13` `WELD_1_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.14` `WELD_1_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.15` `WELD_2_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.16` `WELD_2_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.17` `WELD_3_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.18` `WELD_3_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.19` `WELD_4_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.20` `WELD_4_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.21` `WELD_5_COL`: total=7, cumple=7, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `3.22` `DOUBLER_PLATE_COL`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.22.1
- 🔴 `3.23` `WELD_6_COL`: total=8, cumple=6, no_cumple=2, numerales_no_cumplen=3.23.3, 3.23.7
- 🟢 `3.24` `WELD_7_COL`: total=0, cumple=0, no_cumple=0, numerales_no_cumplen=ninguno

## Paso 4 - Momento probable máximo en rótula plástica (Mpr)

Calculo de momento probable por lado usando `Mpr = Cpr * Ry * Fy * Ze` (Ze = Zx del catalogo).

### 4.1 Cálculo de Mpr para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr_vgizq = Cpr_vgizq * Ry * Fy * Ze_vgizq`
- Fy_vgizq: `345 MPa`
- Ry: `1.1`
- Ze_vgizq (catalogo): `2620000 mm3`
- Demanda de ductilidad_vgizq: `high`
- Cpr_vgizq: `1.15`
- Mpr_vgizq: `1143.43 kN-m`

### 4.2 Cálculo de Mpr para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr_vgder = Cpr_vgder * Ry * Fy * Ze_vgder`
- Fy_vgder: `345 MPa`
- Ry: `1.1`
- Ze_vgder (catalogo): `2620000 mm3`
- Demanda de ductilidad_vgder: `high`
- Cpr_vgder: `1.15`
- Mpr_vgder: `1143.43 kN-m`

## Paso 5 - Distancia de rótula plástica desde la cara de la columna (Sh)

### 5.1 Cálculo de Sh para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuacion: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`
- d_vgizq: `536 mm`
- bf_vgizq: `210 mm`
- Sh_vgizq: `385.4 mm`

### 5.2 Cálculo de Sh para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`
- d_vgder: `536 mm`
- bf_vgder: `210 mm`
- Sh_vgder: `385.4 mm`

## Paso 6 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.

### 6.1 Cálculo de cortante probable para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgizq_max = 2*Mpr_vgizq/Llb_vgizq + Vg_vgizq; Vh_vgizq_min = 2*Mpr_vgizq/Llb_vgizq - Vg_vgizq`
- Mpr_vgizq: `1143.43 kN-m`
- Llb_vgizq: `7500 mm`
- Vg_vgizq: `97.11 kN`
- Vh_vgizq_max: `402.03 kN`
- Vh_vgizq_min: `207.81 kN`
- Vhmax_vgizq adoptado: `402.03 kN`

### 6.2 Cálculo de cortante probable para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgder_max = 2*Mpr_vgder/Llb_vgder + Vg_vgder; Vh_vgder_min = 2*Mpr_vgder/Llb_vgder - Vg_vgder`
- Mpr_vgder: `1143.43 kN-m`
- Llb_vgder: `7500 mm`
- Vg_vgder: `97.11 kN`
- Vh_vgder_max: `402.03 kN`
- Vh_vgder_min: `207.81 kN`
- Vhmax_vgder adoptado: `402.03 kN`

## Paso 7 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.

### 7.1 Cálculo de momento probable en cara de columna para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgizq_max = Mpr_vgizq + Vh_vgizq_max*Sh_vgizq; Mf_vgizq_min = Mpr_vgizq + Vh_vgizq_min*Sh_vgizq`
- Mpr_vgizq: `1143.43 kN-m`
- Sh_vgizq: `385.4 mm`
- Mf_vgizq_max: `1298.37 kN-m`
- Mf_vgizq_min: `1223.52 kN-m`

### 7.2 Cálculo de momento probable en cara de columna para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgder_max = Mpr_vgder + Vh_vgder_max*Sh_vgder; Mf_vgder_min = Mpr_vgder + Vh_vgder_min*Sh_vgder`
- Mpr_vgder: `1143.43 kN-m`
- Sh_vgder: `385.4 mm`
- Mf_vgder_max: `1298.37 kN-m`
- Mf_vgder_min: `1223.52 kN-m`

## Paso 8 - Revisión De Resistencia Pernos (vg_izq)

### 8.1 Revisión de capacidad a tracción (vg_izq)

#### 8.1.1 Estado #1: Rotura en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq + h3_pe_vgizq + h4_pe_vgizq)); phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1298.37 kN-m`
- h1_pe_vgizq: `672.3 mm`
- h2_pe_vgizq: `577.3 mm`
- h3_pe_vgizq: `459.9 mm`
- h4_pe_vgizq: `364.9 mm`
- A_b_vgizq: `506.71 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_p+_vgizq: `312.95 kN`
- phi*Rn_b_p+_vgizq: `355.71 kN`
- DCR_b_p+_vgizq: `0.88`
- Resultado: `🟢 Cumple`

### 8.2 Revisión de capacidad a cortante (vg_izq)

#### 8.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgizq_critico: `402.03 kN`
- n_b_vgizq: `8`
- A_b_vgizq: `506.71 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_v2_vgizq: `50.25 kN`
- phi*Rn_b_v2_vgizq: `214.34 kN`
- DCR_b_v2_vgizq: `0.23`
- Resultado: `🟢 Cumple`

## Paso 9 - Revisión De Resistencia Pernos (vg_der)

### 9.1 Revisión de capacidad a tracción (vg_der)

#### 9.1.1 Estado #1: Rotura en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder + h3_pe_vgder + h4_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgder_critico: `1298.37 kN-m`
- h1_pe_vgder: `672.3 mm`
- h2_pe_vgder: `577.3 mm`
- h3_pe_vgder: `459.9 mm`
- h4_pe_vgder: `364.9 mm`
- A_b_vgder: `506.71 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_p+_vgder: `312.95 kN`
- phi*Rn_b_p+_vgder: `355.71 kN`
- DCR_b_p+_vgder: `0.88`
- Resultado: `🟢 Cumple`

### 9.2 Revisión de capacidad a cortante (vg_der)

#### 9.2.1 ELR #2: Rotura por cortante en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgder_critico: `402.03 kN`
- n_b_vgder: `8`
- A_b_vgder: `506.71 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_v2_vgder: `50.25 kN`
- phi*Rn_b_v2_vgder: `214.34 kN`
- DCR_b_v2_vgder: `0.23`
- Resultado: `🟢 Cumple`

## Paso 10 - Revisión de resistencia platina extremo (vg_izq)

### 10.1. Revisión de capacidad a flexión (vg_izq)

#### 10.1.1. ELR #1: Fluencia (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgizq = Mf_vgizq_critico; phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq (AISC 358-22 Eq. 6.7-8)`
- phi usado: `1`
- Mf_vgizq_critico: `1298.37 kN-m`
- tpe_vgizq: `25.4 mm`
- Fyp_pe_vgizq: `345 MPa`
- Yp_pe_vgizq: `6762.44 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgizq: `93.87 mm`
- pfi_pe_vgizq_entrada: `50 mm`
- pfi_pe_vgizq_efectivo: `50 mm`
- Ru_pe_m3_vgizq: `1298.37 kN-m`
- phi*Rn_pe_m3_vgizq: `1505.19 kN-m`
- DCR_pe_m3_vgizq: `0.86`
- Resultado: `🟢 Cumple`

### 10.3. Revisión de capacidad a cortante paralelo al plano de la platina (vg_izq)

#### 10.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgizq = min(pb_pe_vgizq - dh_pe_vgizq, pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq); Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 1.2 * lc_pe_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `402.03 kN`
- n_b_vgizq: `8`
- pb_pe_vgizq: `95 mm`
- pfo_pe_vgizq: `50 mm`
- pfi_pe_vgizq: `50 mm`
- tf_vgizq: `17.4 mm`
- dh_pe_vgizq: `28.57 mm`
- lc_pe_vgizq: `66.42 mm`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- Ru_pe_v2_vgizq: `50.25 kN`
- phi*Rn_pe_v2_vgizq: `819.98 kN`
- DCR_pe_v2_vgizq: `0.06`
- Resultado: `🟢 Cumple`

#### 10.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 2.4 * d_b_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `402.03 kN`
- n_b_vgizq: `8`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- d_b_vgizq: `25.4 mm`
- Ru_pe_v2_vgizq: `50.25 kN`
- phi*Rn_pe_v2_vgizq: `627.1 kN`
- DCR_pe_v2_vgizq: `0.08`
- Resultado: `🟢 Cumple`

## Paso 11 - Revisión de resistencia platina extremo (vg_der)

### 11.1. Revisión de capacidad a flexión (vg_der)

#### 11.1.1. ELR #1: Fluencia (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`
- phi usado: `1`
- Mf_vgder_critico: `1298.37 kN-m`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Yp_pe_vgder: `6762.44 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgder: `93.87 mm`
- pfi_pe_vgder_entrada: `50 mm`
- pfi_pe_vgder_efectivo: `50 mm`
- Ru_pe_m3_vgder: `1298.37 kN-m`
- phi*Rn_pe_m3_vgder: `1505.19 kN-m`
- DCR_pe_m3_vgder: `0.86`
- Resultado: `🟢 Cumple`

### 11.3. Revisión de capacidad a cortante paralelo al plano de la platina (vg_der)

#### 11.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgder = min(pb_pe_vgder - dh_pe_vgder, pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder); Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `402.03 kN`
- n_b_vgder: `8`
- pb_pe_vgder: `95 mm`
- pfo_pe_vgder: `50 mm`
- pfi_pe_vgder: `50 mm`
- tf_vgder: `17.4 mm`
- dh_pe_vgder: `28.57 mm`
- lc_pe_vgder: `66.42 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- Ru_pe_v2_vgder: `50.25 kN`
- phi*Rn_pe_v2_vgder: `819.98 kN`
- DCR_pe_v2_vgder: `0.06`
- Resultado: `🟢 Cumple`

#### 11.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `402.03 kN`
- n_b_vgder: `8`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- d_b_vgder: `25.4 mm`
- Ru_pe_v2_vgder: `50.25 kN`
- phi*Rn_pe_v2_vgder: `627.1 kN`
- DCR_pe_v2_vgder: `0.08`
- Resultado: `🟢 Cumple`

## Paso 12 - Revisión de Resistencia soldadura #1 (platina extremo vg_izq - rigidizador vg_izq)

### 12.1. Revisión de capacidad a tracción (vg_izq)

#### 12.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w1_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 13 - Revisión de Resistencia soldadura #1 (platina extremo vg_der - rigidizador vg_der)

### 13.1. Revisión de capacidad a tracción (vg_der)

#### 13.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w1_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 14 - Revisión de Resistencia soldadura #2 (viga vg_izq - rigidizador vg_izq)

### 14.1. Revisión de capacidad a cortante (vg_izq)

#### 14.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w2_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 15 - Revisión de Resistencia soldadura #2 (viga vg_der - rigidizador vg_der)

### 15.1. Revisión de capacidad a cortante (vg_der)

#### 15.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w2_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 16 - Revisión de Resistencia soldadura #4 (ala vg_izq - platina extremo vg_izq)

### 16.1. Revisión de capacidad a tracción (vg_izq)

#### 16.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w4_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 17 - Revisión de Resistencia soldadura #4 (ala vg_der - platina extremo vg_der)

### 17.1. Revisión de capacidad a tracción (vg_der)

#### 17.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w4_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 18 - Revisión de resistencia de la viga (vg_izq)

### 18.1. Revisión de capacidad a cortante (vg_izq)

#### 18.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Ru_v2_vgizq = Vh_vgizq_max; Rn_v2_vgizq = 0.6 * Fy_vgizq * tw_vgizq * d_vgizq * Cv1; phi*Rn_v2_vgizq = phi * Rn_v2_vgizq; DCR_v2_vgizq = Ru_v2_vgizq / phi*Rn_v2_vgizq (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgizq_max: `402.03 kN`
- Fy_vgizq: `345 MPa`
- tw_vgizq: `10.9 mm`
- d_vgizq: `536 mm`
- kdes_vgizq: `30.2 mm`
- E_vgizq: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgizq/tw_vgizq: `43.63`
- h_vgizq: `475.6 mm`
- Ru_v2_vgizq: `402.03 kN`
- phi*Rn_v2_vgizq: `1209.38 kN`
- DCR_v2_vgizq: `0.33`
- Resultado: `🟢 Cumple`

## Paso 19 - Revisión de resistencia de la viga (vg_der)

### 19.1. Revisión de capacidad a cortante (vg_der)

#### 19.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Ru_v2_vgder = Vh_vgder_max; Rn_v2_vgder = 0.6 * Fy_vgder * tw_vgder * d_vgder * Cv1; phi*Rn_v2_vgder = phi * Rn_v2_vgder; DCR_v2_vgder = Ru_v2_vgder / phi*Rn_v2_vgder (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgder_max: `402.03 kN`
- Fy_vgder: `345 MPa`
- tw_vgder: `10.9 mm`
- d_vgder: `536 mm`
- kdes_vgder: `30.2 mm`
- E_vgder: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgder/tw_vgder: `43.63`
- h_vgder: `475.6 mm`
- Ru_v2_vgder: `402.03 kN`
- phi*Rn_v2_vgder: `1209.38 kN`
- DCR_v2_vgder: `0.33`
- Resultado: `🟢 Cumple`

## Paso 20 - Revisión de Resistencia soldadura #3 (viga alma vg_izq - platina extremo vg_izq)

### 20.1 Revisión capacidad a tracción (vg_izq)

#### 20.1.1 ELR #1: Rotura de soldadura (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq; hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm; phi*Rn_w3_p+_vgizq = phi * kds_w3_vgizq * nl_w3_vgizq * 0.6 * Fexx_w3_vgizq * 0.707 * hwef_w3_vgizq * t_w3_vgizq; DCR_w3_p+_vgizq = Ru_w3_p+_vgizq / phi*Rn_w3_p+_vgizq`
- tipo_w3_vgizq: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 21 - Revisión de Resistencia soldadura #3 (viga alma vg_der - platina extremo vg_der)

### 21.1 Revisión capacidad a tracción (vg_der)

#### 21.1.1 ELR #1: Rotura de soldadura (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w3_p+_vgder = Fy_vgder * tw_vgder * hwef_w3_vgder; hwef_w3_vgder = pfi_pe_vgder + pb_pe_vgder + 150 mm; phi*Rn_w3_p+_vgder = phi * kds_w3_vgder * nl_w3_vgder * 0.6 * Fexx_w3_vgder * 0.707 * hwef_w3_vgder * t_w3_vgder; DCR_w3_p+_vgder = Ru_w3_p+_vgder / phi*Rn_w3_p+_vgder`
- tipo_w3_vgder: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 22 - Revisión de resistencia de la aleta de la columna

### 22.1. Revisión de capacidad a flexión (vg_izq)

#### 22.1.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); phi*Rn_cf_v2_col_vgizq = phi_ductil * ((tf_col^2 * Fy_col * Y_cs)/(1.11 * (d_vgizq - tf_vgizq))); DCR_cf_v2_col_vgizq = Ru_cf_v2_col_vgizq / phi*Rn_cf_v2_col_vgizq`
- phi usado: `1`
- Mf_vgizq_critico: `1298.37 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- z_vgizq = d_vgizq - tf_vgizq: `518.6 mm`
- tf_col: `28 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `8164.89 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgizq)`
- s_col: `106.07 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgizq: `2503.61 kN`
- phi*Rn_cf_v2_col_vgizq: `3836.45 kN`
- DCR_cf_v2_col_vgizq: `0.65`
- Resultado: `🟢 Cumple`

Donde:

- Ecuacion Y_cs: `Y_cs = bcf/2*[h1*(1/s) + h2*(1/pso) + h3*(1/psi) + h4*(1/s)] + (2/g)*[h1*(s + pb/4) + h2*(pso + 3pb/4) + h3*(psi + pb/4) + h4*(s + 3pb/4) + pb^2/2] + g`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

### 22.2. Revisión de capacidad a flexión (vg_der)

#### 22.2.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); phi*Rn_cf_v2_col_vgder = phi_ductil * ((tf_col^2 * Fy_col * Y_cs)/(1.11 * (d_vgder - tf_vgder))); DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado: `1`
- Mf_vgder_critico: `1298.37 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- z_vgder = d_vgder - tf_vgder: `518.6 mm`
- tf_col: `28 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `8164.89 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgder)`
- s_col: `106.07 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgder: `2503.61 kN`
- phi*Rn_cf_v2_col_vgder: `3836.45 kN`
- DCR_cf_v2_col_vgder: `0.65`
- Resultado: `🟢 Cumple`

Donde:

- Ecuacion Y_cs: `Y_cs = bcf/2*[h1*(1/s) + h2*(1/pso) + h3*(1/psi) + h4*(1/s)] + (2/g)*[h1*(s + pb/4) + h2*(pso + 3pb/4) + h3*(psi + pb/4) + h4*(s + 3pb/4) + pb^2/2] + g`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

## Paso 23 - Revisión de resistencia del alma de la columna

### 23.1. Revisión de capacidad a tracción (vg_izq)

#### 23.1.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado (phi_ductil): `1`
- Mf_vgizq_critico: `1298.37 kN-m`
- St_col: `2500 mm`
- d_col: `500 mm`
- Ct_col: `1`
- kc_col: `55 mm`
- lb_col: `76.2 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- tw_col: `14.5 mm`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- tpe_vgizq: `25.4 mm`
- t_w4_1_vgizq: `8 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `8 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `2032.02 kN`
- phi*Rn_cw_v2_col_vgizq: `2032.02 kN`
- DCR_cw_v2_col_vgizq: `1`
- Resultado: `🟢 Cumple`

### 23.2. Revisión de capacidad a compresión (vg_izq)

#### 23.2.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; Rn_cw_v2_col_vgizq = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_cw_v2_col_vgizq; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado: `0.75`
- Mf_vgizq_critico: `1298.37 kN-m`
- St_col: `2500 mm`
- d_col (dc): `500 mm`
- lb_col: `76.2 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `14.5 mm`
- tf_col: `28 mm`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- tpe_vgizq: `25.4 mm`
- t_w4_1_vgizq: `8 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `8 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgizq: `1704.25 kN`
- phi*Rn_cw_v2_col_vgizq: `1704.25 kN`
- DCR_cw_v2_col_vgizq: `1`
- Resultado: `🟢 Cumple`

#### 23.2.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgizq = max(|-Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|, |Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgizq = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgizq: `352.94 kN-m`
- Mu3_vgder: `353.56 kN-m`
- Pu_vgizq: `0 kN`
- Pu_vgder: `0 kN`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- termino_condicion_izq: `-680.56 kN`
- termino_condicion_der: `-681.76 kN`
- tolerancia_condicion: `1e-9`
- same_sign: `True`
- St_col: `2500 mm`
- d_col: `500 mm`
- Ct_col: `1`
- kc_col: `55 mm`
- h_col: `390 mm`
- E_col: `200000 MPa`
- Fy_col: `345 MPa`
- tw_col: `14.5 mm`
- 2w_w4_vgizq: `8 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `680.56 kN`
- phi*Rn_cw_v2_col_vgizq: `1168.79 kN`
- DCR_cw_v2_col_vgizq: `0.58`
- Resultado: `🟢 Cumple`

### 23.3. Revisión de capacidad a tracción (vg_der)

#### 23.3.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado (phi_ductil): `1`
- Mf_vgder_critico: `1298.37 kN-m`
- St_col: `2500 mm`
- d_col: `500 mm`
- Ct_col: `1`
- kc_col: `55 mm`
- lb_col: `76.2 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- tw_col: `14.5 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `8 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `8 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `2032.02 kN`
- phi*Rn_cw_v2_col_vgder: `2032.02 kN`
- DCR_cw_v2_col_vgder: `1`
- Resultado: `🟢 Cumple`

### 23.4. Revisión de capacidad a compresión (vg_der)

#### 23.4.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; Rn_cw_v2_col_vgder = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_cw_v2_col_vgder; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado: `0.75`
- Mf_vgder_critico: `1298.37 kN-m`
- St_col: `2500 mm`
- d_col (dc): `500 mm`
- lb_col: `76.2 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `14.5 mm`
- tf_col: `28 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `8 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `8 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgder: `1704.25 kN`
- phi*Rn_cw_v2_col_vgder: `1704.25 kN`
- DCR_cw_v2_col_vgder: `1`
- Resultado: `🟢 Cumple`

#### 23.4.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder y F_right = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq; Ru_cw_v2_col_vgder = max(|-Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|, |Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgder = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgder: `353.56 kN-m`
- Mu3_vgizq: `352.94 kN-m`
- Pu_vgder: `0 kN`
- Pu_vgizq: `0 kN`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- termino_condicion_der: `-681.76 kN`
- termino_condicion_izq: `-680.56 kN`
- tolerancia_condicion: `1e-9`
- same_sign: `True`
- St_col: `2500 mm`
- d_col: `500 mm`
- Ct_col: `1`
- kc_col: `55 mm`
- h_col: `390 mm`
- E_col: `200000 MPa`
- Fy_col: `345 MPa`
- tw_col: `14.5 mm`
- 2w_w4_vgder: `8 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `681.76 kN`
- phi*Rn_cw_v2_col_vgder: `1168.79 kN`
- DCR_cw_v2_col_vgder: `0.58`
- Resultado: `🟢 Cumple`

### 23.5. Revisión de capacidad a cortante (col)

#### 23.5.1. ELR #1: Cortante en la zona del panel del alma (WPZS)

- Clausula: `Documento: AISC 360-22w | Seccion: AISC 360-22w Seccion J10.6 + Eq. (J10-9) to Eq. (J10-12)`
- Ecuacion: `Rn_wpz_v2_col = 0.60*Fy_col*d_col*tw_col (J10-9)`
- Considera deformacion inelastica del panel zone: `No`
- phi_ductil (usado en WPZS): `1`
- hb_col: `1250 mm`
- ht_col: `1250 mm`
- Mbe_col_vgizq_max: `1398.88 kN-m`
- Mbe_col_vgizq_min: `1275.47 kN-m`
- Mbe_col_vgder_max: `1398.88 kN-m`
- Mbe_col_vgder_min: `1275.47 kN-m`
- sum_Mbe_col: `2674.35 kN-m`
- Vc2_col: `1069.74 kN`
- d_vgizq: `536 mm`
- Mf_vgizq_max: `1298.37 kN-m`
- Mf_vgizq_min: `1223.52 kN-m`
- d_vgder: `536 mm`
- Mf_vgder_max: `1298.37 kN-m`
- Mf_vgder_min: `1223.52 kN-m`
- sum_Mf_col/(db-tf): `4862.89 kN`
- Ru_wpz_v2_col: `3793.15 kN`
- Pr_col: `1212.01 kN`
- Py_col: `8233.08 kN`
- alphaPr/Py: `0.15`
- Ag_col: `23864 mm2`
- Fy_col: `345 MPa`
- d_col: `500 mm`
- tw_col: `14.5 mm`
- bcf_col: `300 mm`
- tcf_col: `28 mm`
- Rn_wpz_v2_col: `1500.75 kN`
- DCR_wpz_v2_col: `2.53`
- Resultado: `🔴 No cumple`

## Paso 24 - Revisión de resistencia del alma de platinas de continuidad

### 24.1. Revisión de capacidad a tracción

#### 24.1.1. ELR #1: Fluencia por tracción area bruta

- Clausula: `Documento: AISC 358-22 | Seccion: Desarrollo interno de demanda para alma de platinas de continuidad`
- Ecuacion: `Ru_pc_p+_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq) - min{phi*Rn_(23.1.1), phi*Rn_(23.2.1), phi*Rn_(22.1.1)}; Ru_pc_p+_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder) - min{phi*Rn_(23.3.1), phi*Rn_(23.4.1), phi*Rn_(22.2.1)}; Ru_pc_p+_col = max{Ru_pc_p+_col_vgder, Ru_pc_p+_col_vgizq}; phi*Rn_pc_p+_col = phi * Fy_pc_col * b1_pc_col * t_pc_col * n_pc_col`
- Mf_vgizq_critico: `1298.37 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `3836.45 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2032.02 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `1704.25 kN`
- min_capacidad_vgizq: `1704.25 kN`
- Ru_pc_p+_col_vgizq: `799.36 kN`
- Mf_vgder_critico: `1298.37 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `3836.45 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2032.02 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `1704.25 kN`
- min_capacidad_vgder: `1704.25 kN`
- Ru_pc_p+_col_vgder: `799.36 kN`
- Ru_pc_p+_col: `799.36 kN`
- phi usado: `0.9`
- Fy_pc_col: `345 MPa`
- b1_pc_col: `130 mm`
- t_pc_col: `15.9 mm`
- n_pc_col: `2`
- phi*Rn_pc_p+_col: `1283.61 kN`
- DCR_pc_p+_col: `0.62`
- Resultado: `🟢 Cumple`

### 24.2. Revisión de capacidad a compresión

#### 24.2.1. ELR #1: Pandeo por flexión

- Clausula: `Documento: AISC 358-22 | Seccion: Formula de Fcr segun imagen de usuario (K=0.65)`
- Ecuacion: `Fcr_pc_col = 0.658^(Fy_pc_col/Fe_pc_col)*Fy_pc_col; phi*Rn_pc_p-_col = phi * Fcr_pc_col * b1_pc_col * t_pc_col * n_pc_col`
- Mf_vgizq_critico: `1298.37 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `3836.45 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2032.02 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `1704.25 kN`
- min_capacidad_vgizq: `1704.25 kN`
- Ru_pc_p-_col_vgizq: `799.36 kN`
- Mf_vgder_critico: `1298.37 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `3836.45 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2032.02 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `1704.25 kN`
- min_capacidad_vgder: `1704.25 kN`
- Ru_pc_p-_col_vgder: `799.36 kN`
- Ru_pc_p-_col: `799.36 kN`
- phi usado: `0.9`
- K: `0.65`
- Lp_pc_col: `311 mm`
- r_pc_col: `4.61 mm`
- KLr_pc_col: `43.84`
- E_pc_col: `200000 MPa`
- Fy_pc_col: `345 MPa`
- Fe_pc_col: `1027 MPa`
- Fcr_pc_col: `299.75 MPa`
- b1_pc_col: `130 mm`
- t_pc_col: `15.9 mm`
- n_pc_col: `2`
- phi*Rn_pc_p-_col: `1115.24 kN`
- DCR_pc_p-_col: `0.72`
- Resultado: `🟢 Cumple`

### 24.3. Revisión de capacidad a cortante

#### 24.3.1. ELR #1: Fluencia por cortante del area bruta

- Clausula: `Documento: AISC 360-22 | Seccion: G2.1 (adaptado a demanda de alma de platina de continuidad)`
- Ecuacion: `Ru_pc_v2_col = Ru_pc_p+_col_vgder + Ru_pc_p+_col_vgizq; phi*Rn_pc_v2_col = phi * 0.6 * Fy_pc_col * t_pc_col * n_pc_col * L2_pc_col; DCR_pc_v2_col = Ru_pc_v2_col / phi*Rn_pc_v2_col`
- Mf_vgizq_critico: `1298.37 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `3836.45 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2032.02 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `1704.25 kN`
- min_capacidad_vgizq: `1704.25 kN`
- Ru_pc_p+_col_vgizq: `799.36 kN`
- Mf_vgder_critico: `1298.37 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `3836.45 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2032.02 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `1704.25 kN`
- min_capacidad_vgder: `1704.25 kN`
- Ru_pc_p+_col_vgder: `799.36 kN`
- Ru_pc_v2_col: `1598.72 kN`
- phi usado: `1`
- Fy_pc_col: `345 MPa`
- t_pc_col: `15.9 mm`
- n_pc_col: `2`
- L2_pc_col: `311 mm`
- phi*Rn_pc_v2_col: `2047.19 kN`
- DCR_pc_v2_col: `0.78`
- Resultado: `🟢 Cumple`

## Paso 25- Revisión de resistencia de soldadura # 5 ( Platina de continuidad con aleta de columna)

### 25.1. Revisión de capacidad a tracción

#### 25.1.1. ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Ru_w5_p+_col = Fy_pc_col * b2_pc_col * t_pc_col * n_pc_col; Fillet: phi*Rn_w5_p+_col = phi_fragil * kds_w5_col * nl_w5_col * 0.6 * Fexx_w5_col * 0.707 * L_w5_col * w_w5_col * n_pc_col; DCR_w5_p+_col = Ru_w5_p+_col / phi*Rn_w5_p+_col`
- tipo_w5_col: `fillet`
- phi usado (phi_fragil): `0.75`
- Fy_pc_col: `345 MPa`
- b2_pc_col: `108.1 mm`
- t_pc_col: `15.9 mm`
- n_pc_col: `2`
- Ru_w5_p+_col: `1185.97 kN`
- Fexx_w5_col: `490 MPa`
- w_w5_col: `12.7 mm`
- L_w5_col: `82.7 mm`
- nl_w5_col: `2`
- kds_w5_col: `1.5`
- phi*Rn_w5_p+_col: `982.4 kN`
- DCR_w5_p+_col: `1.21`
- Resultado: `🔴 No cumple`

## Paso 26- Revisión de resistencia de soldadura # 6 ( Platina de continuidad con alma de columna)

### 26.1. Revisión de capacidad a cortante

#### 26.1.1. ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Ru1_w5_v2_col = 0.6 * Fy_pc_col * L2_pc_col * t_pc_col; Ru2_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * L_w6_col; Ru3_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * L_w6_col; Ru4_w5_v2_col = 0.6 * fu_col * tw_col * L_w6_col; Ru5_w5_v2_col = 0.6 * fy_col * tw_col * L_w6_col; Ru6_w5_v2_col = 0.6 * fu_col * tw_col * d_col; Ru7_w5_v2_col = 0.6 * fy_col * tw_col * d_col * Cv1; Ru8_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * wz_dp_col; Ru9_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * wz_dp_col; Ru_w5_v2_col = MIN{Ru1..Ru9}; Fillet: phi*Rn_w6_v2_col = phi_fragil * kds_w6_col * nl_w6_col * 0.6 * Fexx_w6_col * 0.707 * L_w6_col * w_w6_col; DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`
- tipo_w6_col: `fillet`
- phi usado (phi_fragil): `0.75`
- Fy_pc_col: `345 MPa`
- Fu_pc_col: `450 MPa`
- L2_pc_col: `311 mm`
- t_pc_col: `15.9 mm`
- Fu_dp_col: `450 MPa`
- Fy_dp_col: `345 MPa`
- t_dp_col: `9.5 mm`
- Fu_col: `450 MPa`
- Fy_col: `345 MPa`
- tw_col: `14.5 mm`
- d_col: `500 mm`
- wz_dp_col: `501.2 mm`
- Cv1: `1`
- Ru1_w5_v2_col: `1023.59 kN`
- Ru2_w5_v2_col: `731.02 kN`
- Ru3_w5_v2_col: `560.45 kN`
- Ru4_w5_v2_col: `1115.78 kN`
- Ru5_w5_v2_col: `855.43 kN`
- Ru6_w5_v2_col: `1957.5 kN`
- Ru7_w5_v2_col: `1500.75 kN`
- Ru8_w5_v2_col: `1285.58 kN`
- Ru9_w5_v2_col: `985.61 kN`
- Ru_w5_v2_col: `560.45 kN`
- Fexx_w6_col: `490 MPa`
- w_w6_col: `12.7 mm`
- L_w6_col: `285 mm`
- nl_w6_col: `2`
- kds_w6_col: `1`
- phi*Rn_w6_v2_col: `1128.51 kN`
- DCR_w6_v2_col: `0.5`
- Resultado: `🟢 Cumple`

### 26.6. Revisión de capacidad del material base

#### 26.6.2. ELR #1: Rotura del material base

- Clausula: `AISC 360-22 J4 (material base)`
- Ecuacion: `Ru_w5_v2_col = MIN{Ru1..Ru9}; phi*Rn1_w6-dp_v2_col = phi_fragil * 0.6 * fu_dp_col * t_dp_col * L_w6_col; phi*Rn2_w6-dp_v2_col = phi_no_ductil * 0.6 * fy_dp_col * t_dp_col * L_w6_col; phi*Rn1_w6-cw_v2_col = phi_fragil * 0.6 * fu_col * tw_col * L_w6_col; phi*Rn2_w6-cw_v2_col = phi_no_ductil * 0.6 * fy_col * tw_col * L_w6_col; phi*Rn_w6_v2_col = min(phi*Rn1_w6-dp_v2_col, phi*Rn2_w6-dp_v2_col, phi*Rn1_w6-cw_v2_col, phi*Rn2_w6-cw_v2_col); DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`
- phi fragil: `0.75`
- phi no ductil: `0.9`
- fu_dp_col: `450 MPa`
- fy_dp_col: `345 MPa`
- t_dp_col: `9.5 mm`
- fu_col: `450 MPa`
- fy_col: `345 MPa`
- tw_col: `14.5 mm`
- L_w6_col: `285 mm`
- Ru_w5_v2_col: `560.45 kN`
- phi*Rn1_w6-dp_v2_col: `548.27 kN`
- phi*Rn2_w6-dp_v2_col: `504.41 kN`
- phi*Rn1_w6-cw_v2_col: `836.83 kN`
- phi*Rn2_w6-cw_v2_col: `769.88 kN`
- phi*Rn_w6_v2_col: `504.41 kN`
- DCR_w6_v2_col: `1.11`
- Resultado: `🔴 No cumple`
