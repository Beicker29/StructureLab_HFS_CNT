# Memoria de Cálculo

- Proyecto: `proj_bseep_si_demo`
- Caso: `case_si_bseep_4es_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bseep_4es`
- Estado global: `🔴 No cumple`

## Paso 1 - Propiedades geométricas, mecánicas y fabricacion

Propiedades organizadas por ambito.

### 1.1 Ámbito `BEAM_IZQ`

#### 1.1.1 Resumen de geometria

- Perfil de viga izquierda (perfil_vgizq) (inp): `W24X76`
- Tipo de acero del perfil de viga izquierda (tipo_acero_perfil_vgizq) (inp): `ASTM A572 Gr 50`
- Demanda de ductilidad de viga izquierda (demanda_ductilidad_vgizq) (inp): `high`
- Luz libre de viga izquierda (Llb_vgizq) (inp): `6096 mm`
- Longitud sin conectores desde cara de columna (Lnc_vgizq) (inp): `1000 mm`
- Longitud de zona protegida (Lpz_vgizq): `494.03 mm`

### 1.2 Ámbito `BEAM_DER`

#### 1.2.1 Resumen de geometria

- Perfil de viga derecha (perfil_vgder) (inp): `W18X76`
- Tipo de acero del perfil de viga derecha (tipo_acero_perfil_vgder) (inp): `ASTM A572 Gr 50`
- Demanda de ductilidad de viga derecha (demanda_ductilidad_vgder) (inp): `high`
- Luz libre de viga derecha (Llb_vgder) (inp): `6096 mm`
- Longitud sin conectores desde cara de columna (Lnc_vgder) (inp): `1000 mm`
- Longitud de zona protegida (Lpz_vgder): `421.53 mm`

### 1.3 Ámbito `COLUMN`

#### 1.3.1 Resumen de geometria

- Perfil de columna (shape_col) (inp): `W18X175`
- Tipo de acero del perfil de columna (tipo_acero_perfil_col) (inp): `ASTM A572 Gr 50`
- Altura de columna (d_col) (inp): `508 mm`
- Espesor de alma de columna (tw_col) (inp): `22.6 mm`
- Proyeccion de columna sobre vigas (St_col) (inp): `240 mm`
- Distancia al punto de inflexion superior (ht_col) (inp): `240 mm`
- Distancia al punto de inflexion inferior (hb_col) (inp): `240 mm`
- gage horizontal de pernos en columna lado izquierda (g_b_col_vgizq) (inp): `140 mm`
- Distancia exterior ajustada lado izquierda (pso_vgizq): `50.7 mm`
- Distancia interior ajustada lado izquierda (psi_vgizq): `50.7 mm`
- Diametro de perforacion en columna lado izquierda (dh_col_vgizq): `28.57 mm`
- Parametro C de columna lado izquierda (C_col_vgizq): `117.3 mm`
- Parametro s de columna lado izquierda (s_col_vgizq): `100.75 mm`
- Distancia h1 de columna lado izquierda (h1_col_vgizq): `648.35 mm`
- Distancia h2 de columna lado izquierda (h2_col_vgizq): `531.05 mm`
- gage horizontal de pernos en columna lado derecha (g_b_col_vgder) (inp): `135 mm`
- Distancia exterior ajustada lado derecha (pso_vgder): `55.7 mm`
- Distancia interior ajustada lado derecha (psi_vgder): `55.7 mm`
- Diametro de perforacion en columna lado derecha (dh_col_vgder): `28.57 mm`
- Parametro C de columna lado derecha (C_col_vgder): `127.3 mm`
- Parametro s de columna lado derecha (s_col_vgder): `98.93 mm`
- Distancia h1 de columna lado derecha (h1_col_vgder): `508.35 mm`
- Distancia h2 de columna lado derecha (h2_col_vgder): `381.05 mm`

### 1.4 Ámbito `END_PLATE_DER`

#### 1.4.1 Resumen de geometria

- Altura de platina extremo de viga derecha (Hpe_vgder): `682 mm`
- Ancho de platina extremo de viga derecha (Bpe_vgder) (inp): `260 mm`
- Espesor de platina extremo de viga derecha (tpe_vgder) (inp): `25.4 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgder) (inp): `55 mm`
- Distancia entre filas de pernos (pb_pe_vgder) (inp): `0 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgder) (inp): `55 mm`
- Distancia interior a fila de pernos (pfi_pe_vgder) (inp): `55 mm`
- Diametro de perforacion de perno (dh_pe_vgder): `28.57 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgder) (inp): `135 mm`
- Parametro s de platina extremo derecha (s_pe_vgder): `93.67 mm`
- Distancia h1 de platina extremo derecha (h1_pe_vgder): `508.35 mm`
- Distancia h2 de platina extremo derecha (h2_pe_vgder): `381.05 mm`

### 1.5 Ámbito `END_PLATE_IZQ`

#### 1.5.1 Resumen de geometria

- Altura de platina extremo de viga izquierda (Hpe_vgizq): `827 mm`
- Ancho de platina extremo de viga izquierda (Bpe_vgizq) (inp): `270 mm`
- Espesor de platina extremo de viga izquierda (tpe_vgizq) (inp): `25.4 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgizq) (inp): `60 mm`
- Distancia entre filas de pernos (pb_pe_vgizq) (inp): `0 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgizq) (inp): `50 mm`
- Distancia interior a fila de pernos (pfi_pe_vgizq) (inp): `50 mm`
- Diametro de perforacion de perno (dh_pe_vgizq): `28.57 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgizq) (inp): `140 mm`
- Parametro s de platina extremo izquierda (s_pe_vgizq): `97.21 mm`
- Distancia h1 de platina extremo izquierda (h1_pe_vgizq): `648.35 mm`
- Distancia h2 de platina extremo izquierda (h2_pe_vgizq): `531.05 mm`

### 1.6 Ámbito `END_PLATE_STIFFENER_DER`

#### 1.6.1 Nota técnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ámbito: `END_PLATE_STIFFENER_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgder = pfo_pe_vgder + de_pe_vgder; L_pest_vgder = h_pest_vgder/tan(30 deg); Ed_pest_vgder = 25 mm`

### 1.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### 1.7.1 Nota técnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; L_pest_vgizq = h_pest_vgizq/tan(30 deg); Ed_pest_vgizq = 25 mm`

### 1.8 Ámbito `BOLTS_DER`

### 1.9 Ámbito `BOLTS_IZQ`

### 1.10 Ámbito `TABLE_6_1_DER`

### 1.11 Ámbito `TABLE_6_1_IZQ`

### 1.12 Ámbito `WELD_1_VGDER`

### 1.13 Ámbito `WELD_1_VGIZQ`

### 1.14 Ámbito `WELD_2_VGDER`

### 1.15 Ámbito `WELD_2_VGIZQ`

### 1.16 Ámbito `WELD_3_VGDER`

### 1.17 Ámbito `WELD_3_VGIZQ`

### 1.18 Ámbito `WELD_4_VGDER`

### 1.19 Ámbito `WELD_4_VGIZQ`

### 1.20 Ámbito `WELD_5_COL`

#### 1.20.1 Resumen de geometria

- Tipo de soldadura #5 de platina de continuidad (tipo_w5_col) (inp): `CJP`
- Resistencia del electrodo de soldadura #5 (Fexx_w5_col) (inp): `490 MPa`
- Espesor/size de soldadura #5 (t_w5_col) (inp): `n/a`
- Numero de lineas de soldadura #5 (nl_w5_col) (inp): `n/a`
- Separacion de extremos de soldadura #5 (L_gap_w5_col) (inp): `0 mm`
- Factor de direccion/sistema de soldadura #5 (kds_w5_col) (inp): `1`
- Longitud efectiva de soldadura #5 (L_w5_col): `328 mm`

### 1.21 platina de enchape del alma

#### 1.21.1 Resumen de geometria

- Uso de platina de enchape del alma (usar_dp_col) (inp): `False`
- Tipo de acero de platina de enchape del alma (tipo_acero_dp_col) (inp): `ASTM A572 Gr 50`
- Espesor de platina de enchape del alma (t_dp_col) (inp): `12.7 mm`
- Numero de platinas de enchape del alma (n_dp_col) (inp): `0`

### 1.22 Ámbito `WELD_6_COL`

#### 1.22.1 Resumen de geometria

- Tipo de soldadura #6 de platina de continuidad (tipo_w6_col) (inp): `CJP`
- Resistencia del electrodo de soldadura #6 (Fexx_w6_col) (inp): `490 MPa`
- Espesor/size de soldadura #6 (t_w6_col) (inp): `n/a`
- Numero de lineas de soldadura #6 (nl_w6_col) (inp): `n/a`
- Separacion de extremos de soldadura #6 (L_gap_w6_col) (inp): `0 mm`
- Factor de direccion/sistema de soldadura #6 (kds_w6_col) (inp): `1`
- Longitud efectiva de soldadura #6 (Lws_col): `328 mm`

### 1.23 platinas de continuidad

#### 1.23.1 Resumen de geometria

- Uso de platinas de continuidad (usar_pc_col) (inp): `True`
- Tipo de acero de platina de continuidad (tipo_acero_pc_col) (inp): `ASTM A572 Gr 50`
- Espesor de platina de continuidad (t_pc_col) (inp): `15.9 mm`
- Ancho base de platina de continuidad (b1_pc_col) (inp): `n/a`
- Espesor de platina de enchape del alma (t_dp_col) (inp): `12.7 mm`
- Numero de platinas de enchape del alma (n_dp_col) (inp): `0`
- Ancho b1.1 de platina de continuidad (b1.1_pc_col): `n/a`
- Ancho b1.2 de platina de continuidad (b1.2_pc_col): `n/a`
- Distancia de recorte 1 de platina de continuidad (Clip1_pc_col): `48.1 mm`
- Longitud util 1 de platina de continuidad (L1_pc_col): `424.2 mm`
- Longitud util 2 de platina de continuidad (L2_pc_col): `328 mm`
- Distancia de recorte 2 de platina de continuidad (Clip2_pc_col): `16.6 mm`
- Ancho neto de platina de continuidad (b2_pc_col): `n/a`

### 1.24 Ámbito `WELD_7_COL`

#### 1.24.1 Resumen de geometria

- Tipo de soldadura #7 (tipo_w7_col) (inp): `tapon`
- Resistencia del electrodo de soldadura #7 (Fexx_w7_col) (inp): `490 MPa`
- Espesor/size de soldadura #7 (t_w7_col) (inp): `8 mm`
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

### 2.8 Ámbito `BOLTS_DER`

#### 2.8.1 Nota técnica - Requisitos de instalacion para conjuntos empernados (right beam)

- Ámbito: `BOLTS_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.`

#### 2.8.2 Nota técnica - Control y aseguramiento de calidad para conjuntos empernados (right beam)

- Ámbito: `BOLTS_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 2.9 Ámbito `BOLTS_IZQ`

#### 2.9.1 Nota técnica - Requisitos de instalacion para conjuntos empernados (left beam)

- Ámbito: `BOLTS_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.`

#### 2.9.2 Nota técnica - Control y aseguramiento de calidad para conjuntos empernados (left beam)

- Ámbito: `BOLTS_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 2.10 Ámbito `TABLE_6_1_DER`

### 2.11 Ámbito `TABLE_6_1_IZQ`

### 2.12 Ámbito `WELD_1_VGDER`

### 2.13 Ámbito `WELD_1_VGIZQ`

### 2.14 Ámbito `WELD_2_VGDER`

### 2.15 Ámbito `WELD_2_VGIZQ`

### 2.16 Ámbito `WELD_3_VGDER`

### 2.17 Ámbito `WELD_3_VGIZQ`

### 2.18 Ámbito `WELD_4_VGDER`

### 2.19 Ámbito `WELD_4_VGIZQ`

### 2.20 Ámbito `WELD_5_COL`

### 2.21 Ámbito `DOUBLER_PLATE_COL`

### 2.22 Ámbito `WELD_6_COL`

### 2.23 Ámbito `CONTINUITY_PLATE_COL`

### 2.24 Ámbito `WELD_7_COL`

## Paso 3 - Revisiónes de requerimientos de propiedades mecánicas y geométricas

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### 3.1 Ámbito `BEAM_IZQ`

#### Chequeo 3.1.1 - Familia de perfil de viga permitida para precalificación (viga izquierda) (`perfil_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `perfil_vgizq in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.2 - Ancho de placa de extremo vs ancho de ala de viga (left beam) (`bp_pe_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `bp_pe_vgizq <= bf_vgizq + margin (25 mm); 270 mm <= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

#### Chequeo 3.1.3 - Separacion minima de gage de pernos (left beam) (`g_b_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `g_b_vgizq >= 3db; 140 mm >= 76.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.4 - Longitud sin conectores de cortante desde la cara de columna (left beam) (`Lnc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Lnc_vgizq >= 1.5d_vgizq; 1000 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.5 - Criterio de despeje de viga con umbral Sc y S (left beam) (`Sc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Sc_vgizq = St_col - pfo_vgizq; S_vgizq = 0.5*sqrt(bcf*g_vgizq); Sc_vgizq > S_vgizq => 190.000 mm > 100.747 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.6 - Relacion luz libre/peralte por sistema de marco (left beam) (`Llb_vgizq/d_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Llb_vgizq/d_vgizq >= 7 (SMF); 10.04 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.7 - Compacidad ancho-espesor del ala de viga (left beam) (`lambda_f_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `lambda_f_vgizq <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.8 - Compacidad ancho-espesor del alma de viga (left beam) (`lambda_w_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `lambda_w_vgizq <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### 3.2 Ámbito `BEAM_DER`

#### Chequeo 3.2.1 - Familia de perfil de viga permitida para precalificación (viga derecha) (`perfil_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `perfil_vgder in {W, HEA, HEB, IPE}; 'W18X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.2 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `bp_pe_vgder <= bf_vgder + margin (25 mm); 260 mm <= 304 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.3 - Separacion minima de gage de pernos (right beam) (`g_b_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `g_b_vgder >= 3db; 135 mm >= 76.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.4 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 693 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.5 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Sc_vgder = St_col - pfo_vgder; S_vgder = 0.5*sqrt(bcf*g_vgder); Sc_vgder > S_vgder => 185.000 mm > 98.932 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.6 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Llb_vgder/d_vgder >= 7 (SMF); 13.19 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.7 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `lambda_f_vgder <= lambda_f_limit; 8.06 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🔴 No cumple

#### Chequeo 3.2.8 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `lambda_w_vgder <= lambda_w_limit; 37.7 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### 3.3 Ámbito `COLUMN`

#### Chequeo 3.3.1 - Familia de perfil de columna permitida para precalificación (`shape_col`)

- Ámbito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'W18X175' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.2 - Peralte máximo del perfil de columna (W36/W920) (`d_col`)

- Ámbito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 508 mm <= 920 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.3 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ámbito: `COLUMN`
- Verificacion: `bp <= bcf; 260 mm <= 290 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.4 - Condicion de conexión columna-losa (`col_losa`)

- Ámbito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.5 - Proyeccion de columna minima por encima de las vigas (`St_col`)

- Ámbito: `COLUMN`
- Verificacion: `St_col >= pfo_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + de_pe_vgizq + 12.5 mm; 240.000 mm >= 122.500 mm; 240.000 mm >= 122.500 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje superior de columna)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.6 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ámbito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.7 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ámbito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.01 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.8 - Espesor individual minimo del alma de columna (`tw_col`)

- Ámbito: `COLUMN`
- Verificacion: `tw_col >= (d_z + w_z)/90 con d_z=d_izq-2tf_izq, w_z=bcf_col; 22.6 mm >= 9.58 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

### 3.4 Ámbito `END_PLATE_DER`

#### Chequeo 3.4.1 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [177.8 mm, 273.05 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.5 Ámbito `END_PLATE_IZQ`

#### Chequeo 3.5.1 - Desigualdades explicitas de ancho de placa de extremo (left beam) (`bp_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf; [min,max] = [177.8 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

### 3.6 Ámbito `END_PLATE_STIFFENER_DER`

#### Chequeo 3.6.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (right beam) (`h_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder = pfo_pe_vgder + de_pe_vgder; 110.000 mm = 55.000 mm + 55.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.2 - Espesor minimo requerido del rigidizador (right beam) (`t_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `t_pest_vgder >= tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 15.9 mm >= 10.8 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.3 - Limite de pandeo local ancho-espesor del rigidizador (right beam) (`h_pest_vgder/t_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder/t_pest_vgder <= 0.56*sqrt(E_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 6.92 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.4 - Despeje del gage de pernos con espesor del rigidizador (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `g_b_vgder >= 2emin + t_pest_vgder; 135 mm >= 79.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 3.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### Chequeo 3.7.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (left beam) (`h_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.2 - Espesor minimo requerido del rigidizador (left beam) (`t_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `t_pest_vgizq >= tw_vgizq*(Fy_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 15.9 mm >= 11.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.3 - Limite de pandeo local ancho-espesor del rigidizador (left beam) (`h_pest_vgizq/t_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq/t_pest_vgizq <= 0.56*sqrt(E_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 6.92 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.4 - Despeje del gage de pernos con espesor del rigidizador (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `g_b_vgizq >= 2emin + t_pest_vgizq; 140 mm >= 79.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 3.8 Ámbito `BOLTS_DER`

#### Chequeo 3.8.1 - El tipo de apriete del perno debe ser una categoria reconocida (right beam) (`tight_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificacion: `tight_bolt_vgder in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.2 - Los pernos deben estar pretensionados salvo que una conexión especifica permita lo contrario (right beam) (`tight_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificacion: `tight_bolt_vgder == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.3 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (right beam) (`std_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificacion: `std_bolt_vgder in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### 3.9 Ámbito `BOLTS_IZQ`

#### Chequeo 3.9.1 - El tipo de apriete del perno debe ser una categoria reconocida (left beam) (`tight_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificacion: `tight_bolt_vgizq in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.2 - Los pernos deben estar pretensionados salvo que una conexión especifica permita lo contrario (left beam) (`tight_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificacion: `tight_bolt_vgizq == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.3 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (left beam) (`std_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificacion: `std_bolt_vgizq in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### 3.10 Ámbito `TABLE_6_1_DER`

#### Chequeo 3.10.1 - Distancia de borde en de (right beam) (`de_pe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `de_pe_vgder >= emin; 55 mm >= 31.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.2 - Limites de distancia en fila exterior de pernos (right beam) (`pfo_pe_vgder - pso_pe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `pso_pe_vgder = pfo_pe_vgder + 0.5*tf_vgder - 0.5*t_pc_col; pso_pe_vgder >= emin; pfo_pe_vgder <= 140 mm; pfo_pe_vgder >= 44 mm; [min,max] = [44.45 mm, 139.7 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.3 - Limites de distancia en fila interior de pernos (right beam) (`pfi_pe_vgder - psi_pe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `pfi_pe_vgder >= emin; pfi_pe_vgder <= 140 mm; pfi_pe_vgder >= 44 mm; psi_pe_vgder = pfi_pe_vgder + 0.5*tf_vgder - 0.5*t_pc_col; psi_pe_vgder > 0; [min,max] = [44.45 mm, 139.7 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.4 - Limites de espesor del ala de viga (right beam) (`tf_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `tf_vgder in [tf_vgder_min, tf_vgder_max]; 9.52 mm <= 17.3 mm <= 19.05 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.5 - Limites de ancho del ala de viga (right beam) (`bf_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `bf_vgder in [bf_vgder_min, bf_vgder_max]; 152.4 mm <= 279 mm <= 228.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🔴 No cumple

#### Chequeo 3.10.6 - Limites de peralte de la viga conectada (right beam) (`d_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `d_vgder in [d_vgder_min, d_vgder_max]; 349.25 mm <= 462 mm <= 609.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.7 - Limites de espesor de placa de extremo (right beam) (`tpe_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `tpe_vgder in [tpe_vgder_min, tpe_vgder_max]; 12.7 mm <= 25.4 mm <= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.8 - Limites de separacion horizontal de pernos (right beam) (`g_b_vgder`)

- Ámbito: `TABLE_6_1_DER`
- Verificacion: `g_b_vgder in [g_b_vgder_min, g_b_vgder_max]; 82.55 mm <= 135 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.11 Ámbito `TABLE_6_1_IZQ`

#### Chequeo 3.11.1 - Distancia de borde en de (left beam) (`de_pe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `de_pe_vgizq >= emin; 60 mm >= 31.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.2 - Limites de distancia en fila exterior de pernos (left beam) (`pfo_pe_vgizq - pso_pe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `pso_pe_vgizq = pfo_pe_vgizq + 0.5*tf_vgizq - 0.5*t_pc_col; pso_pe_vgizq >= emin; pfo_pe_vgizq <= 140 mm; pfo_pe_vgizq >= 44 mm; [min,max] = [44.45 mm, 139.7 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.3 - Limites de distancia en fila interior de pernos (left beam) (`pfi_pe_vgizq - psi_pe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `pfi_pe_vgizq >= emin; pfi_pe_vgizq <= 140 mm; pfi_pe_vgizq >= 44 mm; psi_pe_vgizq = pfi_pe_vgizq + 0.5*tf_vgizq - 0.5*t_pc_col; psi_pe_vgizq > 0; [min,max] = [44.45 mm, 139.7 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.4 - Limites de espesor del ala de viga (left beam) (`tf_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `tf_vgizq in [tf_vgizq_min, tf_vgizq_max]; 9.52 mm <= 17.3 mm <= 19.05 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.5 - Limites de ancho del ala de viga (left beam) (`bf_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `bf_vgizq in [bf_vgizq_min, bf_vgizq_max]; 152.4 mm <= 228 mm <= 228.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.6 - Limites de peralte de la viga conectada (left beam) (`d_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `d_vgizq in [d_vgizq_min, d_vgizq_max]; 349.25 mm <= 607 mm <= 609.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.7 - Limites de espesor de placa de extremo (left beam) (`tpe_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `tpe_vgizq in [tpe_vgizq_min, tpe_vgizq_max]; 12.7 mm <= 25.4 mm <= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.8 - Limites de separacion horizontal de pernos (left beam) (`g_b_vgizq`)

- Ámbito: `TABLE_6_1_IZQ`
- Verificacion: `g_b_vgizq in [g_b_vgizq_min, g_b_vgizq_max]; 82.55 mm <= 140 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.12 Ámbito `WELD_1_VGDER`

#### Chequeo 3.12.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w1_vgder`)

- Ámbito: `WELD_1_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w1_vgder == cjp; t_pest_vgder = 15.900 mm; tipo_w1_vgder = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.13 Ámbito `WELD_1_VGIZQ`

#### Chequeo 3.13.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w1_vgizq`)

- Ámbito: `WELD_1_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w1_vgizq == cjp; t_pest_vgizq = 15.900 mm; tipo_w1_vgizq = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.14 Ámbito `WELD_2_VGDER`

#### Chequeo 3.14.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w2_vgder`)

- Ámbito: `WELD_2_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w2_vgder == cjp; t_pest_vgder = 15.900 mm; tipo_w2_vgder = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.15 Ámbito `WELD_2_VGIZQ`

#### Chequeo 3.15.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w2_vgizq`)

- Ámbito: `WELD_2_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w2_vgizq == cjp; t_pest_vgizq = 15.900 mm; tipo_w2_vgizq = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.16 Ámbito `WELD_3_VGDER`

#### Chequeo 3.16.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (right beam) (`weld_ep_web_vgder`)

- Ámbito: `WELD_3_VGDER`
- Verificacion: `weld_ep_web_vgder in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.17 Ámbito `WELD_3_VGIZQ`

#### Chequeo 3.17.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (left beam) (`weld_ep_web_vgizq`)

- Ámbito: `WELD_3_VGIZQ`
- Verificacion: `weld_ep_web_vgizq in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.18 Ámbito `WELD_4_VGDER`

#### Chequeo 3.18.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha) (`tipo_w4_vgder`)

- Ámbito: `WELD_4_VGDER`
- Verificacion: `si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 0 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 0.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.19 Ámbito `WELD_4_VGIZQ`

#### Chequeo 3.19.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda) (`tipo_w4_vgizq`)

- Ámbito: `WELD_4_VGIZQ`
- Verificacion: `si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 0 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 0.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.20 Ámbito `WELD_5_COL`

#### Chequeo 3.20.1 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `tipo_w5_col in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 3.20.2 - Tipo de soldadura de platina de continuidad cuando el espesor es menor o igual a 10 mm (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `tipo_w5_col in {cjp, pjp} => cumple siempre; t_pc_col=15.9 mm; tipo_w5_col='cjp'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

### 3.21 Ámbito `DOUBLER_PLATE_COL`

#### Chequeo 3.21.1 - Espesor individual minimo de platina de enchape del alma (`t_dp_col`)

- Ámbito: `DOUBLER_PLATE_COL`
- Verificacion: `No aplica: usar_dp_col = false`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

### 3.22 Ámbito `WELD_6_COL`

#### Chequeo 3.22.1 - Longitud maxima de soldadura #6 en columna (`Lws_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `Lws_col <= d_col - 2*(kdet_col + 6*tw_col); 328 mm <= 135.8 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 358-22 Seccion 6.3`
- Resultado: 🔴 No cumple

#### Chequeo 3.22.2 - Longitud minima de soldadura #6 en columna (`Lws_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `Lws_col >= d_col - 2*(kdet_col + 4*tw_col); 328 mm >= 226.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 358-22 Seccion 6.3`
- Resultado: 🟢 Cumple

### 3.23 platina de continuidad

### 3.24 Ámbito `WELD_7_COL`

### 3.25 Resumen de chequeos por ámbito

- 🔴 `3.1` `BEAM_IZQ`: total=8, cumple=7, no_cumple=1, numerales_no_cumplen=3.1.2
- 🔴 `3.2` `BEAM_DER`: total=8, cumple=7, no_cumple=1, numerales_no_cumplen=3.2.7
- 🟢 `3.3` `COLUMN`: total=8, cumple=8, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.4` `END_PLATE_DER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `3.5` `END_PLATE_IZQ`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.5.1
- 🟢 `3.6` `END_PLATE_STIFFENER_DER`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.7` `END_PLATE_STIFFENER_IZQ`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.8` `BOLTS_DER`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.9` `BOLTS_IZQ`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `3.10` `TABLE_6_1_DER`: total=8, cumple=7, no_cumple=1, numerales_no_cumplen=3.10.5
- 🟢 `3.11` `TABLE_6_1_IZQ`: total=8, cumple=8, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.12` `WELD_1_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.13` `WELD_1_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.14` `WELD_2_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.15` `WELD_2_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.16` `WELD_3_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.17` `WELD_3_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.18` `WELD_4_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.19` `WELD_4_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.20` `WELD_5_COL`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.21` `DOUBLER_PLATE_COL`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `3.22` `WELD_6_COL`: total=2, cumple=1, no_cumple=1, numerales_no_cumplen=3.22.1
- 🟢 `3.23` `CONTINUITY_PLATE_COL`: total=0, cumple=0, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.24` `WELD_7_COL`: total=0, cumple=0, no_cumple=0, numerales_no_cumplen=ninguno

## Paso 4 - Momento probable máximo en rótula plástica (Mpr)

Calculo de momento probable por lado usando `Mpr = Cpr * Ry * Fy * Ze` (Ze = Zx del catalogo).

### 4.1 Cálculo de Mpr para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr_vgizq = Cpr_vgizq * Ry * Fy * Ze_vgizq`
- Fy_vgizq: `345 MPa`
- Ry: `1.1`
- Ze_vgizq (catalogo): `3280000 mm3`
- Demanda de ductilidad_vgizq: `high`
- Cpr_vgizq: `1.15`
- Mpr_vgizq: `1431.47 kN-m`

### 4.2 Cálculo de Mpr para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr_vgder = Cpr_vgder * Ry * Fy * Ze_vgder`
- Fy_vgder: `345 MPa`
- Ry: `1.1`
- Ze_vgder (catalogo): `2670000 mm3`
- Demanda de ductilidad_vgder: `high`
- Cpr_vgder: `1.15`
- Mpr_vgder: `1165.25 kN-m`

## Paso 5 - Distancia de rótula plástica desde la cara de la columna (Sh)

### 5.1 Cálculo de Sh para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_4es`
- Ecuacion: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`
- d_vgizq: `607 mm`
- bf_vgizq: `228 mm`
- Sh_vgizq: `225.4 mm`

### 5.2 Cálculo de Sh para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_4es`
- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`
- d_vgder: `462 mm`
- bf_vgder: `279 mm`
- Sh_vgder: `225.4 mm`

## Paso 6 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.

### 6.1 Cálculo de cortante probable para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgizq_max = 2*Mpr_vgizq/Llb_vgizq + Vg_vgizq; Vh_vgizq_min = 2*Mpr_vgizq/Llb_vgizq - Vg_vgizq`
- Mpr_vgizq: `1431.47 kN-m`
- Llb_vgizq: `6096 mm`
- Vg_vgizq: `44.48 kN`
- Vh_vgizq_max: `514.13 kN`
- Vh_vgizq_min: `425.16 kN`
- Vhmax_vgizq adoptado: `514.13 kN`

### 6.2 Cálculo de cortante probable para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgder_max = 2*Mpr_vgder/Llb_vgder + Vg_vgder; Vh_vgder_min = 2*Mpr_vgder/Llb_vgder - Vg_vgder`
- Mpr_vgder: `1165.25 kN-m`
- Llb_vgder: `6096 mm`
- Vg_vgder: `44.48 kN`
- Vh_vgder_max: `426.78 kN`
- Vh_vgder_min: `337.82 kN`
- Vhmax_vgder adoptado: `426.78 kN`

## Paso 7 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.

### 7.1 Cálculo de momento probable en cara de columna para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgizq_max = Mpr_vgizq + Vh_vgizq_max*Sh_vgizq; Mf_vgizq_min = Mpr_vgizq + Vh_vgizq_min*Sh_vgizq`
- Mpr_vgizq: `1431.47 kN-m`
- Sh_vgizq: `225.4 mm`
- Mf_vgizq_max: `1547.36 kN-m`
- Mf_vgizq_min: `1527.31 kN-m`

### 7.2 Cálculo de momento probable en cara de columna para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgder_max = Mpr_vgder + Vh_vgder_max*Sh_vgder; Mf_vgder_min = Mpr_vgder + Vh_vgder_min*Sh_vgder`
- Mpr_vgder: `1165.25 kN-m`
- Sh_vgder: `225.4 mm`
- Mf_vgder_max: `1261.45 kN-m`
- Mf_vgder_min: `1241.4 kN-m`

## Paso 8 - Revisión De Resistencia Pernos (vg_izq)

### 8.1 Revisión de capacidad a tracción (vg_izq)

#### 8.1.1 Estado #1: Rotura en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq)); phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1547.36 kN-m`
- h1_pe_vgizq: `648.35 mm`
- h2_pe_vgizq: `531.05 mm`
- h3_pe_vgizq: `n/a`
- h4_pe_vgizq: `n/a`
- A_b_vgizq: `506.71 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_p+_vgizq: `655.99 kN`
- phi*Rn_b_p+_vgizq: `355.71 kN`
- DCR_b_p+_vgizq: `1.84`
- Resultado: `🔴 No cumple`

### 8.2 Revisión de capacidad a cortante (vg_izq)

#### 8.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgizq_critico: `514.13 kN`
- n_b_vgizq: `4`
- A_b_vgizq: `506.71 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_v2_vgizq: `128.53 kN`
- phi*Rn_b_v2_vgizq: `214.34 kN`
- DCR_b_v2_vgizq: `0.6`
- Resultado: `🟢 Cumple`

## Paso 9 - Revisión De Resistencia Pernos (vg_der)

### 9.1 Revisión de capacidad a tracción (vg_der)

#### 9.1.1 Estado #1: Rotura en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgder_critico: `1261.45 kN-m`
- h1_pe_vgder: `508.35 mm`
- h2_pe_vgder: `381.05 mm`
- h3_pe_vgder: `n/a`
- h4_pe_vgder: `n/a`
- A_b_vgder: `506.71 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_p+_vgder: `709.16 kN`
- phi*Rn_b_p+_vgder: `355.71 kN`
- DCR_b_p+_vgder: `1.99`
- Resultado: `🔴 No cumple`

### 9.2 Revisión de capacidad a cortante (vg_der)

#### 9.2.1 ELR #2: Rotura por cortante en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgder_critico: `426.78 kN`
- n_b_vgder: `4`
- A_b_vgder: `506.71 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_v2_vgder: `106.7 kN`
- phi*Rn_b_v2_vgder: `214.34 kN`
- DCR_b_v2_vgder: `0.5`
- Resultado: `🟢 Cumple`

## Paso 10 - Revisión de resistencia platina extremo (vg_izq)

### 10.1. Revisión de capacidad a flexión (vg_izq)

#### 10.1.1. ELR #1: Fluencia (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgizq = Mf_vgizq_critico; phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1547.36 kN-m`
- tpe_vgizq: `25.4 mm`
- Fyp_pe_vgizq: `345 MPa`
- Yp_pe_vgizq: `6786.9 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.3`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgizq: `97.21 mm`
- pfi_pe_vgizq_entrada: `50 mm`
- pfi_pe_vgizq_efectivo: `50 mm`
- Ru_pe_m3_vgizq: `1547.36 kN-m`
- phi*Rn_pe_m3_vgizq: `1359.57 kN-m`
- DCR_pe_m3_vgizq: `1.14`
- Resultado: `🔴 No cumple`

### 10.2. Revisión de capacidad a cortante perpendicular al plano de la platina (vg_izq)

#### 10.2.1. ELR #1: Fluencia por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Ru_pe_v1_vgizq = Mf_vgizq_critico / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v1_vgizq = phi * 0.6 * Fyp_pe_vgizq * bpe_vgizq * tpe_vgizq (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.9`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `270 mm`
- tpe_vgizq: `25.4 mm`
- Fyp_pe_vgizq: `345 MPa`
- Mf_vgizq_critico: `1547.36 kN-m`
- Ru_pe_v1_vgizq: `1311.99 kN`
- phi*Rn_pe_v1_vgizq: `1277.65 kN`
- DCR_pe_v1_vgizq: `1.03`
- Resultado: `🔴 No cumple`

#### 10.2.2. ELR #2: Rotura por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgizq = Ru_pe_m3_vgizq / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v2_vgizq = phi * 0.6 * Fup_pe_vgizq * tpe_vgizq * (bpe_vgizq - 2*(dh_pe_vgizq + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Ru_pe_m3_vgizq: `1547.36 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `270 mm`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- dh_pe_vgizq: `28.57 mm`
- Rn_pe_v2_vgizq: `1311.99 kN`
- phi*Rn_pe_v2_vgizq: `1294 kN`
- DCR_pe_v2_vgizq: `1.01`
- Resultado: `🔴 No cumple`

### 10.3. Revisión de capacidad a cortante paralelo al plano de la platina (vg_izq)

#### 10.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgizq = pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq; Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 1.2 * lc_pe_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `514.13 kN`
- n_b_vgizq: `4`
- pfo_pe_vgizq: `50 mm`
- pfi_pe_vgizq: `50 mm`
- tf_vgizq: `17.3 mm`
- dh_pe_vgizq: `28.57 mm`
- lc_pe_vgizq: `88.72 mm`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- Ru_pe_v2_vgizq: `128.53 kN`
- phi*Rn_pe_v2_vgizq: `1095.26 kN`
- DCR_pe_v2_vgizq: `0.12`
- Resultado: `🟢 Cumple`

#### 10.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 2.4 * d_b_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `514.13 kN`
- n_b_vgizq: `4`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- d_b_vgizq: `25.4 mm`
- Ru_pe_v2_vgizq: `128.53 kN`
- phi*Rn_pe_v2_vgizq: `627.1 kN`
- DCR_pe_v2_vgizq: `0.2`
- Resultado: `🟢 Cumple`

## Paso 11 - Revisión de resistencia platina extremo (vg_der)

### 11.1. Revisión de capacidad a flexión (vg_der)

#### 11.1.1. ELR #1: Fluencia (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mf_vgder_critico: `1261.45 kN-m`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Yp_pe_vgder: `4899.53 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.3`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgder: `93.67 mm`
- pfi_pe_vgder_entrada: `55 mm`
- pfi_pe_vgder_efectivo: `55 mm`
- Ru_pe_m3_vgder: `1261.45 kN-m`
- phi*Rn_pe_m3_vgder: `981.48 kN-m`
- DCR_pe_m3_vgder: `1.29`
- Resultado: `🔴 No cumple`

### 11.2. Revisión de capacidad a cortante perpendicular al plano de la platina (vg_der)

#### 11.2.1. ELR #1: Fluencia por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Ru_pe_v1_vgder = Mf_vgder_critico / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v1_vgder = phi * 0.6 * Fyp_pe_vgder * bpe_vgder * tpe_vgder (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.9`
- d_vgder: `462 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `444.7 mm`
- bpe_vgder: `260 mm`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Mf_vgder_critico: `1261.45 kN-m`
- Ru_pe_v1_vgder: `1418.32 kN`
- phi*Rn_pe_v1_vgder: `1230.33 kN`
- DCR_pe_v1_vgder: `1.15`
- Resultado: `🔴 No cumple`

#### 11.2.2. ELR #2: Rotura por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v2_vgder = phi * 0.6 * Fup_pe_vgder * tpe_vgder * (bpe_vgder - 2*(dh_pe_vgder + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Ru_pe_m3_vgder: `1261.45 kN-m`
- d_vgder: `462 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `444.7 mm`
- bpe_vgder: `260 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- dh_pe_vgder: `28.57 mm`
- Rn_pe_v2_vgder: `1418.32 kN`
- phi*Rn_pe_v2_vgder: `1232.28 kN`
- DCR_pe_v2_vgder: `1.15`
- Resultado: `🔴 No cumple`

### 11.3. Revisión de capacidad a cortante paralelo al plano de la platina (vg_der)

#### 11.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgder = pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder; Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `426.78 kN`
- n_b_vgder: `4`
- pfo_pe_vgder: `55 mm`
- pfi_pe_vgder: `55 mm`
- tf_vgder: `17.3 mm`
- dh_pe_vgder: `28.57 mm`
- lc_pe_vgder: `98.72 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- Ru_pe_v2_vgder: `106.7 kN`
- phi*Rn_pe_v2_vgder: `1218.7 kN`
- DCR_pe_v2_vgder: `0.09`
- Resultado: `🟢 Cumple`

#### 11.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `426.78 kN`
- n_b_vgder: `4`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- d_b_vgder: `25.4 mm`
- Ru_pe_v2_vgder: `106.7 kN`
- phi*Rn_pe_v2_vgder: `627.1 kN`
- DCR_pe_v2_vgder: `0.17`
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
- Vh_vgizq_max: `514.13 kN`
- Fy_vgizq: `345 MPa`
- tw_vgizq: `11.2 mm`
- d_vgizq: `607 mm`
- kdes_vgizq: `30 mm`
- E_vgizq: `199947.96 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgizq/tw_vgizq: `48.84`
- h_vgizq: `547 mm`
- Ru_v2_vgizq: `514.13 kN`
- phi*Rn_v2_vgizq: `1407.27 kN`
- DCR_v2_vgizq: `0.37`
- Resultado: `🟢 Cumple`

## Paso 19 - Revisión de resistencia de la viga (vg_der)

### 19.1. Revisión de capacidad a cortante (vg_der)

#### 19.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Ru_v2_vgder = Vh_vgder_max; Rn_v2_vgder = 0.6 * Fy_vgder * tw_vgder * d_vgder * Cv1; phi*Rn_v2_vgder = phi * Rn_v2_vgder; DCR_v2_vgder = Ru_v2_vgder / phi*Rn_v2_vgder (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgder_max: `426.78 kN`
- Fy_vgder: `345 MPa`
- tw_vgder: `10.8 mm`
- d_vgder: `462 mm`
- kdes_vgder: `27.4 mm`
- E_vgder: `199947.96 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgder/tw_vgder: `37.7`
- h_vgder: `407.2 mm`
- Ru_v2_vgder: `426.78 kN`
- phi*Rn_v2_vgder: `1032.85 kN`
- DCR_v2_vgder: `0.41`
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
- Mf_vgizq_critico: `1547.36 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- tf_col: `40.4 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `7622.15 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.5`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgizq)`
- s_col: `100.75 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgizq: `2623.97 kN`
- phi*Rn_cf_v2_col_vgizq: `6557 kN`
- DCR_cf_v2_col_vgizq: `0.4`
- Resultado: `🟢 Cumple`

Donde:

- Ecuacion Y_cs: `Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

### 22.2. Revisión de capacidad a flexión (vg_der)

#### 22.2.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); phi*Rn_cf_v2_col_vgder = phi_ductil * ((tf_col^2 * Fy_col * Y_cs)/(1.11 * (d_vgder - tf_vgder))); DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado: `1`
- Mf_vgder_critico: `1261.45 kN-m`
- d_vgder: `462 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `444.7 mm`
- tf_col: `40.4 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `5656.34 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.5`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgder)`
- s_col: `98.93 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgder: `2836.64 kN`
- phi*Rn_cf_v2_col_vgder: `6452.49 kN`
- DCR_cf_v2_col_vgder: `0.44`
- Resultado: `🟢 Cumple`

Donde:

- Ecuacion Y_cs: `Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

## Paso 23 - Revisión de resistencia del alma de la columna

### 23.1. Revisión de capacidad a tracción (vg_izq)

#### 23.1.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado (phi_ductil): `1`
- Mf_vgizq_critico: `1547.36 kN-m`
- St_col: `240 mm`
- d_col: `508 mm`
- Ct_col: `0.5`
- kc_col: `50.5 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- tw_col: `22.6 mm`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- tpe_vgizq: `25.4 mm`
- t_w4_1_vgizq: `0 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `0 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `1712.22 kN`
- phi*Rn_cw_v2_col_vgizq: `1712.22 kN`
- DCR_cw_v2_col_vgizq: `1`
- Resultado: `🟢 Cumple`

### 23.2. Revisión de capacidad a compresión (vg_izq)

#### 23.2.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; Rn_cw_v2_col_vgizq = 0.40*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-20]; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_cw_v2_col_vgizq; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado: `0.75`
- Mf_vgizq_critico: `1547.36 kN-m`
- St_col: `240 mm`
- d_col (dc): `508 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- E_col: `199947.96 MPa`
- tw_col: `22.6 mm`
- tf_col: `40.4 mm`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- tpe_vgizq: `25.4 mm`
- t_w4_1_vgizq: `0 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `0 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_20`
- Ru_cw_v2_col_vgizq: `1987.85 kN`
- phi*Rn_cw_v2_col_vgizq: `1987.85 kN`
- DCR_cw_v2_col_vgizq: `1`
- Resultado: `🟢 Cumple`

#### 23.2.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgizq = max(|-Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|, |Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgizq = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `False`
- phi usado: `n/a`
- Mu3_vgizq: `n/a`
- Mu3_vgder: `n/a`
- Pu_vgizq: `n/a`
- Pu_vgder: `n/a`
- d_vgizq: `n/a`
- tf_vgizq: `n/a`
- d_vgder: `n/a`
- tf_vgder: `n/a`
- termino_condicion_izq: `n/a`
- termino_condicion_der: `n/a`
- tolerancia_condicion: `n/a`
- same_sign: `n/a`
- St_col: `n/a`
- d_col: `n/a`
- Ct_col: `n/a`
- kc_col: `n/a`
- h_col: `n/a`
- E_col: `n/a`
- Fy_col: `n/a`
- tw_col: `n/a`
- 2w_w4_vgizq: `n/a`
- Ecuacion 2w_w4_vgizq: `n/a`
- Resultado: `No aplica`

### 23.3. Revisión de capacidad a tracción (vg_der)

#### 23.3.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado (phi_ductil): `1`
- Mf_vgder_critico: `1261.45 kN-m`
- St_col: `240 mm`
- d_col: `508 mm`
- Ct_col: `0.5`
- kc_col: `50.5 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- tw_col: `22.6 mm`
- d_vgder: `462 mm`
- tf_vgder: `17.3 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `0 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `0 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `1712.22 kN`
- phi*Rn_cw_v2_col_vgder: `1712.22 kN`
- DCR_cw_v2_col_vgder: `1`
- Resultado: `🟢 Cumple`

### 23.4. Revisión de capacidad a compresión (vg_der)

#### 23.4.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; Rn_cw_v2_col_vgder = 0.40*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-20]; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_cw_v2_col_vgder; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado: `0.75`
- Mf_vgder_critico: `1261.45 kN-m`
- St_col: `240 mm`
- d_col (dc): `508 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- E_col: `199947.96 MPa`
- tw_col: `22.6 mm`
- tf_col: `40.4 mm`
- d_vgder: `462 mm`
- tf_vgder: `17.3 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `0 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `0 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_20`
- Ru_cw_v2_col_vgder: `1987.85 kN`
- phi*Rn_cw_v2_col_vgder: `1987.85 kN`
- DCR_cw_v2_col_vgder: `1`
- Resultado: `🟢 Cumple`

#### 23.4.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder y F_right = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq; Ru_cw_v2_col_vgder = max(|-Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|, |Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgder = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `False`
- phi usado: `n/a`
- Mu3_vgder: `n/a`
- Mu3_vgizq: `n/a`
- Pu_vgder: `n/a`
- Pu_vgizq: `n/a`
- d_vgder: `n/a`
- tf_vgder: `n/a`
- d_vgizq: `n/a`
- tf_vgizq: `n/a`
- termino_condicion_der: `n/a`
- termino_condicion_izq: `n/a`
- tolerancia_condicion: `n/a`
- same_sign: `n/a`
- St_col: `n/a`
- d_col: `n/a`
- Ct_col: `n/a`
- kc_col: `n/a`
- h_col: `n/a`
- E_col: `n/a`
- Fy_col: `n/a`
- tw_col: `n/a`
- 2w_w4_vgder: `n/a`
- Ecuacion 2w_w4_vgder: `n/a`
- Resultado: `No aplica`

### 23.5. Revisión de capacidad a cortante (col)

#### 23.5.1. ELR #1: Cortante en la zona del panel del alma (WPZS)

- Clausula: `Documento: AISC 360-22w | Seccion: AISC 360-22w Seccion J10.6 + Eq. (J10-9) to Eq. (J10-12)`
- Ecuacion: `Rn_wpz_v2_col = 0.60*Fy_col*d_col*tw_col (J10-9)`
- Considera deformacion inelastica del panel zone: `No`
- phi_ductil (usado en WPZS): `1`
- hb_col: `240 mm`
- ht_col: `240 mm`
- Mbe_col_vgizq_max: `1677.95 kN-m`
- Mbe_col_vgizq_min: `1635.3 kN-m`
- Mbe_col_vgder_max: `1369.85 kN-m`
- Mbe_col_vgder_min: `1327.21 kN-m`
- sum_Mbe_col: `3005.15 kN-m`
- Vc2_col: `6260.73 kN`
- d_vgizq: `607 mm`
- Mf_vgizq_max: `1547.36 kN-m`
- Mf_vgizq_min: `1527.31 kN-m`
- d_vgder: `462 mm`
- Mf_vgder_max: `1261.45 kN-m`
- Mf_vgder_min: `1241.4 kN-m`
- sum_Mf_col/(db-tf): `5426.61 kN`
- Ru_wpz_v2_col: `-834.13 kN`
- Pr_col: `0 kN`
- Py_col: `11454 kN`
- alphaPr/Py: `0`
- Ag_col: `33200 mm2`
- Fy_col: `345 MPa`
- d_col: `508 mm`
- tw_col: `22.6 mm`
- bcf_col: `290 mm`
- tcf_col: `40.4 mm`
- Rn_wpz_v2_col: `2376.53 kN`
- DCR_wpz_v2_col: `-0.35`
- Resultado: `🟢 Cumple`
