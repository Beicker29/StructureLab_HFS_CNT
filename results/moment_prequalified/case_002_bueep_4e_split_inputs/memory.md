# Memoria de Cálculo

- Proyecto: `proj_bueep_si_demo`
- Caso: `case_si_bueep_4e_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bueep_4e`
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
- Longitud de zona protegida (Lpz_vgizq): `607 mm`

### 1.2 Ámbito `BEAM_DER`

#### 1.2.1 Resumen de geometria

- Perfil de viga derecha (perfil_vgder) (inp): `W24X76`
- Tipo de acero del perfil de viga derecha (tipo_acero_perfil_vgder) (inp): `ASTM A572 Gr 50`
- Demanda de ductilidad de viga derecha (demanda_ductilidad_vgder) (inp): `high`
- Luz libre de viga derecha (Llb_vgder) (inp): `6096 mm`
- Longitud sin conectores desde cara de columna (Lnc_vgder) (inp): `1000 mm`
- Longitud de zona protegida (Lpz_vgder): `607 mm`

### 1.3 Ámbito `END_PLATE_IZQ`

#### 1.3.1 Resumen de geometria

- Altura de platina extremo de viga izquierda (Hpe_vgizq): `827 mm`
- Ancho de platina extremo de viga izquierda (Bpe_vgizq) (inp): `253 mm`
- Espesor de platina extremo de viga izquierda (tpe_vgizq) (inp): `25.4 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgizq) (inp): `n/a`
- Distancia entre filas de pernos (pb_pe_vgizq) (inp): `0 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgizq) (inp): `50 mm`
- Distancia interior a fila de pernos (pfi_pe_vgizq) (inp): `50 mm`
- Diametro de perforacion de perno (dh_pe_vgizq): `31.75 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgizq) (inp): `n/a`
- Distancia horizontal de borde en platina (deh_pe_vgizq): `n/a`
- Parametro s de platina extremo izquierda (s_pe_vgizq): `98.18 mm`
- Distancia h1 de platina extremo izquierda (h1_pe_vgizq): `648.35 mm`
- Distancia h2 de platina extremo izquierda (h2_pe_vgizq): `531.05 mm`

### 1.4 Ámbito `END_PLATE_DER`

#### 1.4.1 Resumen de geometria

- Altura de platina extremo de viga derecha (Hpe_vgder): `827 mm`
- Ancho de platina extremo de viga derecha (Bpe_vgder) (inp): `253 mm`
- Espesor de platina extremo de viga derecha (tpe_vgder) (inp): `25.4 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgder) (inp): `n/a`
- Distancia entre filas de pernos (pb_pe_vgder) (inp): `0 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgder) (inp): `50 mm`
- Distancia interior a fila de pernos (pfi_pe_vgder) (inp): `50 mm`
- Diametro de perforacion de perno (dh_pe_vgder): `31.75 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgder) (inp): `n/a`
- Distancia horizontal de borde en platina (deh_pe_vgder): `n/a`
- Parametro s de platina extremo derecha (s_pe_vgder): `98.18 mm`
- Distancia h1 de platina extremo derecha (h1_pe_vgder): `648.35 mm`
- Distancia h2 de platina extremo derecha (h2_pe_vgder): `531.05 mm`

### 1.5 Ámbito `COLUMN`

#### 1.5.1 Resumen de geometria

- Perfil de columna (shape_col) (inp): `W18X175`
- Tipo de acero del perfil de columna (tipo_acero_perfil_col) (inp): `ASTM A572 Gr 50`
- Altura de columna (d_col) (inp): `508 mm`
- Espesor de alma de columna (tw_col) (inp): `22.6 mm`
- Espesor de ala de columna (tf_col) (inp): `40.4 mm`
- Ancho de ala de columna (bf_col) (inp): `290 mm`
- Proyeccion de columna sobre vigas (St_col) (inp): `762 mm`
- Distancia al punto de inflexion superior (ht_col) (inp): `762 mm`
- Distancia al punto de inflexion inferior (hb_col) (inp): `762 mm`
- gage horizontal de pernos en columna lado izquierda (g_b_col_vgizq) (inp): `152.4 mm`
- Distancia exterior ajustada lado izquierda (pso_vgizq): `50.7 mm`
- Distancia interior ajustada lado izquierda (psi_vgizq): `50.7 mm`
- Diametro de perforacion en columna lado izquierda (dh_col_vgizq): `31.75 mm`
- Parametro C de columna lado izquierda (C_col_vgizq): `117.3 mm`
- Parametro s de columna lado izquierda (s_col_vgizq): `105.11 mm`
- Distancia h1 de columna lado izquierda (h1_col_vgizq): `648.35 mm`
- Distancia h2 de columna lado izquierda (h2_col_vgizq): `531.05 mm`
- gage horizontal de pernos en columna lado derecha (g_b_col_vgder) (inp): `152.4 mm`
- Distancia exterior ajustada lado derecha (pso_vgder): `50.7 mm`
- Distancia interior ajustada lado derecha (psi_vgder): `50.7 mm`
- Diametro de perforacion en columna lado derecha (dh_col_vgder): `31.75 mm`
- Parametro C de columna lado derecha (C_col_vgder): `117.3 mm`
- Parametro s de columna lado derecha (s_col_vgder): `105.11 mm`
- Distancia h1 de columna lado derecha (h1_col_vgder): `648.35 mm`
- Distancia h2 de columna lado derecha (h2_col_vgder): `531.05 mm`

### 1.6 Ámbito `END_PLATE_STIFFENER_DER`

#### 1.6.1 Resumen de geometria

- Tipo de acero de rigidizador derecha (tipo_acero_pest_vgder) (inp): `ASTM A572 Gr 50`
- Espesor de rigidizador derecha (t_pest_vgder) (inp): `n/a`
- Altura del rigidizador de platina extremo derecha (h_pest_vgder): `110 mm`
- Longitud del rigidizador de platina extremo derecha (L_pest_vgder): `200 mm`
- Requisito de borde del rigidizador de platina extremo derecha (Ed_pest_vgder): `25 mm`

### 1.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### 1.7.1 Resumen de geometria

- Tipo de acero de rigidizador izquierda (tipo_acero_pest_vgizq) (inp): `ASTM A572 Gr 50`
- Espesor de rigidizador izquierda (t_pest_vgizq) (inp): `n/a`
- Altura del rigidizador de platina extremo izquierda (h_pest_vgizq): `110 mm`
- Longitud del rigidizador de platina extremo izquierda (L_pest_vgizq): `200 mm`
- Requisito de borde del rigidizador de platina extremo izquierda (Ed_pest_vgizq): `25 mm`

### 1.8 Ámbito `BOLTS_DER`

#### 1.8.1 Resumen de geometria

- Diametro nominal de perno lado derecha (db_b_vgder) (inp): `28.57 mm`
- Resistencia nominal a traccion de perno lado derecha (Fnt_b_vgder) (inp): `780 MPa`
- Resistencia nominal a cortante de perno lado derecha (Fnv_b_vgder) (inp): `470 MPa`
- Condicion de rosca de perno lado derecha (thread_b_vgder) (inp): `N`
- Numero de pernos lado derecha (n_b_vgder) (inp): `4`
- Norma de fabricacion del perno lado derecha (std_v_vgder) (inp): `ASTM A490`
- Tipo de apriete del perno lado derecha (tipo_apriete_b_vgder) (inp): `pretensioned`
- Area efectiva de perno lado derecha (A_b_vgder): `641.3 mm2`

### 1.9 Ámbito `BOLTS_IZQ`

#### 1.9.1 Resumen de geometria

- Diametro nominal de perno lado izquierda (db_b_vgizq) (inp): `28.57 mm`
- Resistencia nominal a traccion de perno lado izquierda (Fnt_b_vgizq) (inp): `780 MPa`
- Resistencia nominal a cortante de perno lado izquierda (Fnv_b_vgizq) (inp): `470 MPa`
- Condicion de rosca de perno lado izquierda (thread_b_vgizq) (inp): `N`
- Numero de pernos lado izquierda (n_b_vgizq) (inp): `4`
- Norma de fabricacion del perno lado izquierda (std_v_vgizq) (inp): `ASTM A490`
- Tipo de apriete del perno lado izquierda (tipo_apriete_b_vgizq) (inp): `pretensioned`
- Area efectiva de perno lado izquierda (A_b_vgizq): `641.3 mm2`

### 1.10 Ámbito `WELD_1_VGDER`

#### 1.10.1 Resumen de geometria

- Tipo de soldadura #1 lado derecha (tipo_w1_vgder) (inp): `n/a`
- Resistencia del electrodo de soldadura #1 lado derecha (Fexx_w1_vgder) (inp): `490 MPa`
- Espesor/size de soldadura #1 lado derecha (w_w1_vgder) (inp): `n/a`
- Numero de lineas de soldadura #1 lado derecha (nl_w1_vgder) (inp): `n/a`
- Separacion de extremos de soldadura #1 lado derecha (L_gap_w1_vgder) (inp): `n/a`
- Factor de direccion/sistema de soldadura #1 lado derecha (kds_w1_vgder) (inp): `n/a`
- Longitud efectiva de soldadura #1 lado derecha (L_w1_vgder): `n/a`

### 1.11 Ámbito `WELD_1_VGIZQ`

#### 1.11.1 Resumen de geometria

- Tipo de soldadura #1 lado izquierda (tipo_w1_vgizq) (inp): `n/a`
- Resistencia del electrodo de soldadura #1 lado izquierda (Fexx_w1_vgizq) (inp): `490 MPa`
- Espesor/size de soldadura #1 lado izquierda (w_w1_vgizq) (inp): `n/a`
- Numero de lineas de soldadura #1 lado izquierda (nl_w1_vgizq) (inp): `n/a`
- Separacion de extremos de soldadura #1 lado izquierda (L_gap_w1_vgizq) (inp): `n/a`
- Factor de direccion/sistema de soldadura #1 lado izquierda (kds_w1_vgizq) (inp): `n/a`
- Longitud efectiva de soldadura #1 lado izquierda (L_w1_vgizq): `n/a`

### 1.12 Ámbito `WELD_2_VGDER`

#### 1.12.1 Resumen de geometria

- Tipo de soldadura #2 lado derecha (tipo_w2_vgder) (inp): `CJP`
- Resistencia del electrodo de soldadura #2 lado derecha (Fexx_w2_vgder) (inp): `490 MPa`
- Espesor/size de soldadura #2 lado derecha (w_w2_vgder) (inp): `8 mm`
- Numero de lineas de soldadura #2 lado derecha (nl_w2_vgder) (inp): `2`
- Separacion de extremos de soldadura #2 lado derecha (L_gap_w2_vgder) (inp): `n/a`
- Factor de direccion/sistema de soldadura #2 lado derecha (kds_w2_vgder) (inp): `n/a`
- Longitud efectiva de soldadura #2 lado derecha (L_w2_vgder): `n/a`

### 1.13 Ámbito `WELD_2_VGIZQ`

#### 1.13.1 Resumen de geometria

- Tipo de soldadura #2 lado izquierda (tipo_w2_vgizq) (inp): `CJP`
- Resistencia del electrodo de soldadura #2 lado izquierda (Fexx_w2_vgizq) (inp): `490 MPa`
- Espesor/size de soldadura #2 lado izquierda (w_w2_vgizq) (inp): `8 mm`
- Numero de lineas de soldadura #2 lado izquierda (nl_w2_vgizq) (inp): `2`
- Separacion de extremos de soldadura #2 lado izquierda (L_gap_w2_vgizq) (inp): `n/a`
- Factor de direccion/sistema de soldadura #2 lado izquierda (kds_w2_vgizq) (inp): `n/a`
- Longitud efectiva de soldadura #2 lado izquierda (L_w2_vgizq): `n/a`

### 1.14 Ámbito `WELD_3_VGDER`

#### 1.14.1 Resumen de geometria

- Tipo de soldadura #3 lado derecha (tipo_w3_vgder) (inp): `CJP`
- Resistencia del electrodo de soldadura #3 lado derecha (Fexx_w3_vgder) (inp): `490 MPa`
- Espesor/size de soldadura #3 lado derecha (w_w3_vgder) (inp): `8 mm`
- Numero de lineas de soldadura #3 lado derecha (nl_w3_vgder) (inp): `2`
- Longitud efectiva de soldadura #3 lado derecha (hwef_w3_vgder): `200 mm`

### 1.15 Ámbito `WELD_3_VGIZQ`

#### 1.15.1 Resumen de geometria

- Tipo de soldadura #3 lado izquierda (tipo_w3_vgizq) (inp): `CJP`
- Resistencia del electrodo de soldadura #3 lado izquierda (Fexx_w3_vgizq) (inp): `490 MPa`
- Espesor/size de soldadura #3 lado izquierda (w_w3_vgizq) (inp): `8 mm`
- Numero de lineas de soldadura #3 lado izquierda (nl_w3_vgizq) (inp): `2`
- Longitud efectiva de soldadura #3 lado izquierda (hwef_w3_vgizq): `200 mm`

### 1.16 Ámbito `WELD_4_VGDER`

#### 1.16.1 Resumen de geometria

- Tipo de soldadura #4 lado derecha (tipo_w4_vgder) (inp): `n/a`
- Resistencia del electrodo de soldadura #4 lado derecha (Fexx_w4_vgder) (inp): `490 MPa`
- Espesor/size de soldadura #4 lado derecha (w_w4_vgder) (inp): `n/a`
- Espesor total de garganta requerida #4 lado derecha (t_w4.1_vgder) (inp): `n/a`
- Numero de lineas de soldadura #4 lado derecha (nl_w4_vgder) (inp): `n/a`
- Longitud efectiva de soldadura #4 lado derecha (L_w4_vgder): `n/a`

### 1.17 Ámbito `WELD_4_VGIZQ`

#### 1.17.1 Resumen de geometria

- Tipo de soldadura #4 lado izquierda (tipo_w4_vgizq) (inp): `n/a`
- Resistencia del electrodo de soldadura #4 lado izquierda (Fexx_w4_vgizq) (inp): `490 MPa`
- Espesor/size de soldadura #4 lado izquierda (w_w4_vgizq) (inp): `n/a`
- Espesor total de garganta requerida #4 lado izquierda (t_w4.1_vgizq) (inp): `n/a`
- Numero de lineas de soldadura #4 lado izquierda (nl_w4_vgizq) (inp): `n/a`
- Longitud efectiva de soldadura #4 lado izquierda (L_w4_vgizq): `n/a`

### 1.18 Ámbito `WELD_5_COL`

#### 1.18.1 Resumen de geometria

- Tipo de soldadura #5 de platina de continuidad (tipo_w5_col) (inp): `CJP`
- Resistencia del electrodo de soldadura #5 (Fexx_w5_col) (inp): `490 MPa`
- Espesor/size de soldadura #5 (w_w5_col) (inp): `n/a`
- Numero de lineas de soldadura #5 (nl_w5_col) (inp): `n/a`
- Separacion de extremos de soldadura #5 (L_gap_w5_col) (inp): `0 mm`
- Factor de direccion/sistema de soldadura #5 (kds_w5_col) (inp): `1`
- Longitud efectiva de soldadura #5 (L_w5_col): `n/a`

### 1.19 Ámbito `WELD_6_COL`

#### 1.19.1 Resumen de geometria

- Tipo de soldadura #6 de platina de continuidad (tipo_w6_col) (inp): `CJP`
- Resistencia del electrodo de soldadura #6 (Fexx_w6_col) (inp): `490 MPa`
- Espesor/size de soldadura #6 (w_w6_col) (inp): `n/a`
- Numero de lineas de soldadura #6 (nl_w6_col) (inp): `n/a`
- Separacion de extremos de soldadura #6 (L_gap_w6_col) (inp): `0 mm`
- Factor de direccion/sistema de soldadura #6 (kds_w6_col) (inp): `1`
- Longitud efectiva de soldadura #6 (Lws_col): `328 mm`

### 1.20 platinas de continuidad

#### 1.20.1 Resumen de geometria

- Uso de platinas de continuidad (usar_pc_col) (inp): `True`
- Tipo de acero de platina de continuidad (tipo_acero_pc_col) (inp): `ASTM A572 Gr 50`
- Espesor de platina de continuidad (t_pc_col) (inp): `15.9 mm`
- Ancho base de platina de continuidad (b1_pc_col) (inp): `n/a`
- Ancho b1.1 de platina de continuidad (b1.1_pc_col): `n/a`
- Ancho b1.2 de platina de continuidad (b1.2_pc_col): `n/a`
- Distancia de recorte 1 de platina de continuidad (Clip1_pc_col): `48.1 mm`
- Longitud util 1 de platina de continuidad (L1_pc_col): `424.2 mm`
- Longitud util 2 de platina de continuidad (L2_pc_col): `328 mm`
- Distancia de recorte 2 de platina de continuidad (Clip2_pc_col): `16.6 mm`
- Ancho neto de platina de continuidad (b2_pc_col): `n/a`

## Paso 2 - Especificaciones técnicas

Especificaciones tecnicas organizadas por ambito.

### 2.1 Ámbito `BEAM_IZQ`

### 2.2 Ámbito `BEAM_DER`

### 2.3 Ámbito `END_PLATE_IZQ`

### 2.4 Ámbito `END_PLATE_DER`

### 2.5 Ámbito `COLUMN`

#### 2.5.1 Nota técnica - Ubicacion de la conexión de placa de extremo en columna

- Ámbito: `COLUMN`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (2)`
- Requisito: `La placa de extremo debe conectarse al ala de la columna.`

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

### 2.10 Ámbito `WELD_1_VGDER`

### 2.11 Ámbito `WELD_1_VGIZQ`

### 2.12 Ámbito `WELD_2_VGDER`

### 2.13 Ámbito `WELD_2_VGIZQ`

### 2.14 Ámbito `WELD_3_VGDER`

### 2.15 Ámbito `WELD_3_VGIZQ`

### 2.16 Ámbito `WELD_4_VGDER`

### 2.17 Ámbito `WELD_4_VGIZQ`

### 2.18 Ámbito `WELD_5_COL`

### 2.19 Ámbito `WELD_6_COL`

### 2.20 Ámbito `CONTINUITY_PLATE_COL`

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
- Verificacion: `bp_pe_vgizq <= bf_vgizq + margin (25 mm); 253 mm <= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.3 - Longitud sin conectores de cortante desde la cara de columna (left beam) (`Lnc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Lnc_vgizq >= 1.5d_vgizq; 1000 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.4 - Criterio de despeje de viga con umbral Sc y S (left beam) (`Sc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Sc_vgizq = St_col - pfo_vgizq; S_vgizq = 0.5*sqrt(bcf*g_vgizq); Sc_vgizq > S_vgizq => 712.000 mm > 105.114 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.5 - Relacion luz libre/peralte por sistema de marco (left beam) (`Llb_vgizq/d_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `Llb_vgizq/d_vgizq >= 7 (SMF); 10.04 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.6 - Compacidad ancho-espesor del ala de viga (left beam) (`lambda_f_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `lambda_f_vgizq <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.7 - Compacidad ancho-espesor del alma de viga (left beam) (`lambda_w_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `lambda_w_vgizq <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.8 - Limites de ancho del ala de viga (left beam) (`bf_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `bf_vgizq in [bf_vgizq_min, bf_vgizq_max]; 152.4 mm <= 228 mm <= 234.95 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.9 - Limites de peralte de la viga conectada (left beam) (`d_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificacion: `d_vgizq in [d_vgizq_min, d_vgizq_max]; 349.25 mm <= 607 mm <= 609.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.2 Ámbito `BEAM_DER`

#### Chequeo 3.2.1 - Familia de perfil de viga permitida para precalificación (viga derecha) (`perfil_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `perfil_vgder in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.2 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `bp_pe_vgder <= bf_vgder + margin (25 mm); 253 mm <= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.3 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.4 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Sc_vgder = St_col - pfo_vgder; S_vgder = 0.5*sqrt(bcf*g_vgder); Sc_vgder > S_vgder => 712.000 mm > 105.114 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.5 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `Llb_vgder/d_vgder >= 7 (SMF); 10.04 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.6 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `lambda_f_vgder <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.7 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `lambda_w_vgder <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.8 - Limites de ancho del ala de viga (right beam) (`bf_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `bf_vgder in [bf_vgder_min, bf_vgder_max]; 152.4 mm <= 228 mm <= 234.95 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.9 - Limites de peralte de la viga conectada (right beam) (`d_vgder`)

- Ámbito: `BEAM_DER`
- Verificacion: `d_vgder in [d_vgder_min, d_vgder_max]; 349.25 mm <= 607 mm <= 609.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.3 Ámbito `END_PLATE_IZQ`

#### Chequeo 3.3.1 - Separacion minima de gage de pernos (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `g_b_vgizq >= 3db; 152.4 mm >= 85.72 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.2 - Desigualdades explicitas de ancho de placa de extremo (left beam) (`bp_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf; [min,max] = [177.8 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.3 - Horizontal edge distance from plate edge to bolt line (left beam) (`deh_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `deh_pe_vgizq >= emin; 50.3 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.4 - Distancia de borde en de (left beam) (`de_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `de_pe_vgizq >= emin; 60 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.5 - Maximum edge distance at de (left beam) (`de_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `de_pe_vgizq <= emax_j36; 60 mm <= 150 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.6 - Outside bolt-row distance minimum (left beam) (`pfo_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `pfo_pe_vgizq >= max(pfo_pe_vgizq_min, emin); 50 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.7 - Outside bolt-row distance maximum (left beam) (`pfo_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `pfo_pe_vgizq <= min(pfo_pe_vgizq_max, emax_j36); 50 mm <= 114.3 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.8 - Inside bolt-row distance minimum (left beam) (`pfi_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `pfi_pe_vgizq >= max(pfi_pe_vgizq_min, emin); 50 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.9 - Inside bolt-row distance maximum (left beam) (`pfi_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `pfi_pe_vgizq <= min(pfi_pe_vgizq_max, emax_j36); 50 mm <= 114.3 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.10 - Limites de espesor de placa de extremo (left beam) (`tpe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `tpe_vgizq in [tpe_vgizq_min, tpe_vgizq_max]; 12.7 mm <= 25.4 mm <= 57.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.11 - Horizontal bolt spacing minimum (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `g_b_vgizq >= max(g_b_vgizq_min, 3db_j33); 152.4 mm >= 101.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.3 (compute_minimum_bolt_spacing_j33)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.12 - Horizontal bolt spacing maximum (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificacion: `g_b_vgizq <= min(g_b_vgizq_max, smax_j36); 152.4 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)`
- Resultado: 🔴 No cumple

### 3.4 Ámbito `END_PLATE_DER`

#### Chequeo 3.4.1 - Separacion minima de gage de pernos (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `g_b_vgder >= 3db; 152.4 mm >= 85.72 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.2 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [177.8 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.3 - Horizontal edge distance from plate edge to bolt line (right beam) (`deh_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `deh_pe_vgder >= emin; 50.3 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.4 - Distancia de borde en de (right beam) (`de_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `de_pe_vgder >= emin; 60 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.5 - Maximum edge distance at de (right beam) (`de_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `de_pe_vgder <= emax_j36; 60 mm <= 150 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.6 - Outside bolt-row distance minimum (right beam) (`pfo_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `pfo_pe_vgder >= max(pfo_pe_vgder_min, emin); 50 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.7 - Outside bolt-row distance maximum (right beam) (`pfo_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `pfo_pe_vgder <= min(pfo_pe_vgder_max, emax_j36); 50 mm <= 114.3 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.8 - Inside bolt-row distance minimum (right beam) (`pfi_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `pfi_pe_vgder >= max(pfi_pe_vgder_min, emin); 50 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.9 - Inside bolt-row distance maximum (right beam) (`pfi_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `pfi_pe_vgder <= min(pfi_pe_vgder_max, emax_j36); 50 mm <= 114.3 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.10 - Limites de espesor de placa de extremo (right beam) (`tpe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `tpe_vgder in [tpe_vgder_min, tpe_vgder_max]; 12.7 mm <= 25.4 mm <= 57.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.11 - Horizontal bolt spacing minimum (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `g_b_vgder >= max(g_b_vgder_min, 3db_j33); 152.4 mm >= 101.6 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.3 (compute_minimum_bolt_spacing_j33)`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.12 - Horizontal bolt spacing maximum (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificacion: `g_b_vgder <= min(g_b_vgder_max, smax_j36); 152.4 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)`
- Resultado: 🔴 No cumple

### 3.5 Ámbito `COLUMN`

#### Chequeo 3.5.1 - Familia de perfil de columna permitida para precalificación (`shape_col`)

- Ámbito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'W18X175' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.2 - Peralte máximo del perfil de columna (W36/W920) (`d_col`)

- Ámbito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 508 mm <= 920 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.3 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ámbito: `COLUMN`
- Verificacion: `bp <= bcf; 253 mm <= 290 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.4 - Condicion de conexión columna-losa (`col_losa`)

- Ámbito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.5 - Proyeccion de columna minima por encima de las vigas (`St_col`)

- Ámbito: `COLUMN`
- Verificacion: `St_col >= pfo_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + de_pe_vgizq + 12.5 mm; 762.000 mm >= 122.500 mm; 762.000 mm >= 122.500 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje superior de columna)`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.6 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ámbito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.7 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ámbito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.01 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.8 - Espesor individual minimo del alma de columna (`tw_col`)

- Ámbito: `COLUMN`
- Verificacion: `tw_col >= (dz_dp_col + wz_dp_col)/90; si use_weld_7_col=false: dz_dp_col=d_col-2*tf_col, wz_dp_col=max{d_lado-2*tf_lado}; si use_weld_7_col=true: dz_dp_col=h_dp_col/(nfilas_w7_col + 1), wz_dp_col=b_dp_col/(ncolumna_w7_col + 1); 22.6 mm >= 11.11 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.9 - Outside adjusted edge distance minimum (right beam) (`pso_pe_vgder`)

- Ámbito: `COLUMN`
- Verificacion: `pso_pe_vgder >= emin; 50.7 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.10 - Outside adjusted edge distance maximum (right beam) (`pso_pe_vgder`)

- Ámbito: `COLUMN`
- Verificacion: `pso_pe_vgder <= emax_j36; 50.7 mm <= 150 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.11 - Outside adjusted edge distance minimum (left beam) (`pso_pe_vgizq`)

- Ámbito: `COLUMN`
- Verificacion: `pso_pe_vgizq >= emin; 50.7 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.12 - Outside adjusted edge distance maximum (left beam) (`pso_pe_vgizq`)

- Ámbito: `COLUMN`
- Verificacion: `pso_pe_vgizq <= emax_j36; 50.7 mm <= 150 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### 3.6 Ámbito `END_PLATE_STIFFENER_DER`

#### Chequeo 3.6.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (right beam) (`h_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder = pfo_pe_vgder + de_pe_vgder; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

### 3.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### Chequeo 3.7.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (left beam) (`h_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
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

### 3.10 Ámbito `WELD_1_VGDER`

#### Chequeo 3.10.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w1_vgder`)

- Ámbito: `WELD_1_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w1_vgder == cjp; dato faltante: t_pest_vgder`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🔴 No cumple

### 3.11 Ámbito `WELD_1_VGIZQ`

#### Chequeo 3.11.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w1_vgizq`)

- Ámbito: `WELD_1_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w1_vgizq == cjp; dato faltante: t_pest_vgizq`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🔴 No cumple

### 3.12 Ámbito `WELD_2_VGDER`

#### Chequeo 3.12.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w2_vgder`)

- Ámbito: `WELD_2_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w2_vgder == cjp; dato faltante: t_pest_vgder`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🔴 No cumple

### 3.13 Ámbito `WELD_2_VGIZQ`

#### Chequeo 3.13.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w2_vgizq`)

- Ámbito: `WELD_2_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w2_vgizq == cjp; dato faltante: t_pest_vgizq`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🔴 No cumple

### 3.14 Ámbito `WELD_3_VGDER`

#### Chequeo 3.14.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (right beam) (`weld_ep_web_vgder`)

- Ámbito: `WELD_3_VGDER`
- Verificacion: `weld_ep_web_vgder in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.15 Ámbito `WELD_3_VGIZQ`

#### Chequeo 3.15.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (left beam) (`weld_ep_web_vgizq`)

- Ámbito: `WELD_3_VGIZQ`
- Verificacion: `weld_ep_web_vgizq in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.16 Ámbito `WELD_4_VGDER`

#### Chequeo 3.16.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha) (`tipo_w4_vgder`)

- Ámbito: `WELD_4_VGDER`
- Verificacion: `si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 8 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 0.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🔴 No cumple

### 3.17 Ámbito `WELD_4_VGIZQ`

#### Chequeo 3.17.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda) (`tipo_w4_vgizq`)

- Ámbito: `WELD_4_VGIZQ`
- Verificacion: `si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 8 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 0.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🔴 No cumple

### 3.18 Ámbito `WELD_5_COL`

#### Chequeo 3.18.1 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `tipo_w5_col in {fillet, cjp}; 'cjp' in {fillet, cjp}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 3.18.2 - Tamano minimo de soldadura #5 cuando tipo_w5_col es fillet (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificacion: `tipo_w5_col='cjp' => cumple; t_pc_col=15.9 mm; tipo_w5_col='cjp'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

### 3.19 Ámbito `WELD_6_COL`

#### Chequeo 3.19.1 - Tipo de soldadura #6 permitido (`tipo_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificacion: `tipo_w6_col in {cjp, pjp, fillet}; 'cjp' in {cjp, pjp, fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 3.20 platina de continuidad

### 3.21 Resumen de chequeos por ámbito

- 🟢 `3.1` `BEAM_IZQ`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.2` `BEAM_DER`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `3.3` `END_PLATE_IZQ`: total=12, cumple=11, no_cumple=1, numerales_no_cumplen=3.3.12
- 🔴 `3.4` `END_PLATE_DER`: total=12, cumple=11, no_cumple=1, numerales_no_cumplen=3.4.12
- 🟢 `3.5` `COLUMN`: total=12, cumple=12, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.6` `END_PLATE_STIFFENER_DER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.7` `END_PLATE_STIFFENER_IZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.8` `BOLTS_DER`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.9` `BOLTS_IZQ`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `3.10` `WELD_1_VGDER`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.10.1
- 🔴 `3.11` `WELD_1_VGIZQ`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.11.1
- 🔴 `3.12` `WELD_2_VGDER`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.12.1
- 🔴 `3.13` `WELD_2_VGIZQ`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.13.1
- 🟢 `3.14` `WELD_3_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.15` `WELD_3_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `3.16` `WELD_4_VGDER`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.16.1
- 🔴 `3.17` `WELD_4_VGIZQ`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=3.17.1
- 🟢 `3.18` `WELD_5_COL`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.19` `WELD_6_COL`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.20` `CONTINUITY_PLATE_COL`: total=0, cumple=0, no_cumple=0, numerales_no_cumplen=ninguno

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
- Ze_vgder (catalogo): `3280000 mm3`
- Demanda de ductilidad_vgder: `high`
- Cpr_vgder: `1.15`
- Mpr_vgder: `1431.47 kN-m`

## Paso 5 - Distancia de rótula plástica desde la cara de la columna (Sh)

### 5.1 Cálculo de Sh para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bueep_4e`
- Ecuacion: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`
- d_vgizq: `607 mm`
- bf_vgizq: `228 mm`
- Sh_vgizq: `303.5 mm`

### 5.2 Cálculo de Sh para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bueep_4e`
- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`
- d_vgder: `607 mm`
- bf_vgder: `228 mm`
- Sh_vgder: `303.5 mm`

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
- Mpr_vgder: `1431.47 kN-m`
- Llb_vgder: `6096 mm`
- Vg_vgder: `44.48 kN`
- Vh_vgder_max: `514.13 kN`
- Vh_vgder_min: `425.16 kN`
- Vhmax_vgder adoptado: `514.13 kN`

## Paso 7 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.

### 7.1 Cálculo de momento probable en cara de columna para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgizq_max = Mpr_vgizq + Vh_vgizq_max*Sh_vgizq; Mf_vgizq_min = Mpr_vgizq + Vh_vgizq_min*Sh_vgizq`
- Mpr_vgizq: `1431.47 kN-m`
- Sh_vgizq: `303.5 mm`
- Mf_vgizq_max: `1587.51 kN-m`
- Mf_vgizq_min: `1560.51 kN-m`

### 7.2 Cálculo de momento probable en cara de columna para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgder_max = Mpr_vgder + Vh_vgder_max*Sh_vgder; Mf_vgder_min = Mpr_vgder + Vh_vgder_min*Sh_vgder`
- Mpr_vgder: `1431.47 kN-m`
- Sh_vgder: `303.5 mm`
- Mf_vgder_max: `1587.51 kN-m`
- Mf_vgder_min: `1560.51 kN-m`

## Paso 8 - Revisión De Resistencia Pernos (vg_izq)

### 8.1 Revisión de capacidad a tracción (vg_izq)

#### 8.1.1 Estado #1: Rotura en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq)); phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1587.51 kN-m`
- h1_pe_vgizq: `648.35 mm`
- h2_pe_vgizq: `531.05 mm`
- h3_pe_vgizq: `n/a`
- h4_pe_vgizq: `n/a`
- A_b_vgizq: `641.3 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_p+_vgizq: `673.02 kN`
- phi*Rn_b_p+_vgizq: `450.19 kN`
- DCR_b_p+_vgizq: `1.49`
- Resultado: `🔴 No cumple`

### 8.2 Revisión de capacidad a cortante (vg_izq)

#### 8.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgizq_critico: `514.13 kN`
- n_b_vgizq: `4`
- A_b_vgizq: `641.3 mm2`
- Fnv_b_vgizq: `470 MPa`
- thread_b_vgizq: `N`
- Ru_b_v2_vgizq: `128.53 kN`
- phi*Rn_b_v2_vgizq: `271.27 kN`
- DCR_b_v2_vgizq: `0.47`
- Resultado: `🟢 Cumple`

## Paso 9 - Revisión De Resistencia Pernos (vg_der)

### 9.1 Revisión de capacidad a tracción (vg_der)

#### 9.1.1 Estado #1: Rotura en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgder_critico: `1587.51 kN-m`
- h1_pe_vgder: `648.35 mm`
- h2_pe_vgder: `531.05 mm`
- h3_pe_vgder: `n/a`
- h4_pe_vgder: `n/a`
- A_b_vgder: `641.3 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_p+_vgder: `673.02 kN`
- phi*Rn_b_p+_vgder: `450.19 kN`
- DCR_b_p+_vgder: `1.49`
- Resultado: `🔴 No cumple`

### 9.2 Revisión de capacidad a cortante (vg_der)

#### 9.2.1 ELR #2: Rotura por cortante en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgder_critico: `514.13 kN`
- n_b_vgder: `4`
- A_b_vgder: `641.3 mm2`
- Fnv_b_vgder: `470 MPa`
- thread_b_vgder: `N`
- Ru_b_v2_vgder: `128.53 kN`
- phi*Rn_b_v2_vgder: `271.27 kN`
- DCR_b_v2_vgder: `0.47`
- Resultado: `🟢 Cumple`

## Paso 10 - Revisión de resistencia platina extremo (vg_izq)

### 10.1. Revisión de capacidad a flexión (vg_izq)

#### 10.1.1. ELR #1: Fluencia (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgizq = Mf_vgizq_critico; phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq (AISC 358-22 Eq. 6.7-8)`
- phi usado: `1`
- Mf_vgizq_critico: `1587.51 kN-m`
- tpe_vgizq: `25.4 mm`
- Fyp_pe_vgizq: `345 MPa`
- Yp_pe_vgizq: `4637.55 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.2`
- Caso Yp: `N/A`
- s_pe_vgizq: `98.18 mm`
- pfi_pe_vgizq_entrada: `50 mm`
- pfi_pe_vgizq_efectivo: `50 mm`
- Ru_pe_m3_vgizq: `1587.51 kN-m`
- phi*Rn_pe_m3_vgizq: `1032.23 kN-m`
- DCR_pe_m3_vgizq: `1.54`
- Resultado: `🔴 No cumple`

### 10.2. Revisión de capacidad a cortante perpendicular al plano de la platina (vg_izq)

#### 10.2.1. ELR #1: Fluencia por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Ru_pe_v1_vgizq = Mf_vgizq_critico / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v1_vgizq = phi * 0.6 * Fyp_pe_vgizq * bpe_vgizq * tpe_vgizq (AISC 358-22 Eq. 6.7-10)`
- phi usado: `1`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `253 mm`
- tpe_vgizq: `25.4 mm`
- Fyp_pe_vgizq: `345 MPa`
- Mf_vgizq_critico: `1587.51 kN-m`
- Ru_pe_v1_vgizq: `1346.03 kN`
- phi*Rn_pe_v1_vgizq: `1330.22 kN`
- DCR_pe_v1_vgizq: `1.01`
- Resultado: `🔴 No cumple`

#### 10.2.2. ELR #2: Rotura por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgizq = Ru_pe_m3_vgizq / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v2_vgizq = phi * 0.6 * Fup_pe_vgizq * tpe_vgizq * (bpe_vgizq - 2*(dh_pe_vgizq + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Ru_pe_m3_vgizq: `1587.51 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `253 mm`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- dh_pe_vgizq: `31.75 mm`
- Rn_pe_v2_vgizq: `1346.03 kN`
- phi*Rn_pe_v2_vgizq: `1149.88 kN`
- DCR_pe_v2_vgizq: `1.17`
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
- dh_pe_vgizq: `31.75 mm`
- lc_pe_vgizq: `85.55 mm`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- Ru_pe_v2_vgizq: `128.53 kN`
- phi*Rn_pe_v2_vgizq: `1056.06 kN`
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
- d_b_vgizq: `28.57 mm`
- Ru_pe_v2_vgizq: `128.53 kN`
- phi*Rn_pe_v2_vgizq: `705.48 kN`
- DCR_pe_v2_vgizq: `0.18`
- Resultado: `🟢 Cumple`

## Paso 11 - Revisión de resistencia platina extremo (vg_der)

### 11.1. Revisión de capacidad a flexión (vg_der)

#### 11.1.1. ELR #1: Fluencia (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`
- phi usado: `1`
- Mf_vgder_critico: `1587.51 kN-m`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Yp_pe_vgder: `4637.55 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.2`
- Caso Yp: `N/A`
- s_pe_vgder: `98.18 mm`
- pfi_pe_vgder_entrada: `50 mm`
- pfi_pe_vgder_efectivo: `50 mm`
- Ru_pe_m3_vgder: `1587.51 kN-m`
- phi*Rn_pe_m3_vgder: `1032.23 kN-m`
- DCR_pe_m3_vgder: `1.54`
- Resultado: `🔴 No cumple`

### 11.2. Revisión de capacidad a cortante perpendicular al plano de la platina (vg_der)

#### 11.2.1. ELR #1: Fluencia por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Ru_pe_v1_vgder = Mf_vgder_critico / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v1_vgder = phi * 0.6 * Fyp_pe_vgder * bpe_vgder * tpe_vgder (AISC 358-22 Eq. 6.7-10)`
- phi usado: `1`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `589.7 mm`
- bpe_vgder: `253 mm`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Mf_vgder_critico: `1587.51 kN-m`
- Ru_pe_v1_vgder: `1346.03 kN`
- phi*Rn_pe_v1_vgder: `1330.22 kN`
- DCR_pe_v1_vgder: `1.01`
- Resultado: `🔴 No cumple`

#### 11.2.2. ELR #2: Rotura por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v2_vgder = phi * 0.6 * Fup_pe_vgder * tpe_vgder * (bpe_vgder - 2*(dh_pe_vgder + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Ru_pe_m3_vgder: `1587.51 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `589.7 mm`
- bpe_vgder: `253 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- dh_pe_vgder: `31.75 mm`
- Rn_pe_v2_vgder: `1346.03 kN`
- phi*Rn_pe_v2_vgder: `1149.88 kN`
- DCR_pe_v2_vgder: `1.17`
- Resultado: `🔴 No cumple`

### 11.3. Revisión de capacidad a cortante paralelo al plano de la platina (vg_der)

#### 11.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgder = pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder; Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `514.13 kN`
- n_b_vgder: `4`
- pfo_pe_vgder: `50 mm`
- pfi_pe_vgder: `50 mm`
- tf_vgder: `17.3 mm`
- dh_pe_vgder: `31.75 mm`
- lc_pe_vgder: `85.55 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- Ru_pe_v2_vgder: `128.53 kN`
- phi*Rn_pe_v2_vgder: `1056.06 kN`
- DCR_pe_v2_vgder: `0.12`
- Resultado: `🟢 Cumple`

#### 11.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `514.13 kN`
- n_b_vgder: `4`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- d_b_vgder: `28.57 mm`
- Ru_pe_v2_vgder: `128.53 kN`
- phi*Rn_pe_v2_vgder: `705.48 kN`
- DCR_pe_v2_vgder: `0.18`
- Resultado: `🟢 Cumple`

## Paso 12 - Revisión de Resistencia soldadura #3 (viga alma vg_izq - platina extremo vg_izq)

### 12.1 Revisión capacidad a tracción (vg_izq)

#### 12.1.1 ELR #1: Rotura de soldadura (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq; hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm; phi*Rn_w3_p+_vgizq = phi * kds_w3_vgizq * nl_w3_vgizq * 0.6 * Fexx_w3_vgizq * 0.707 * hwef_w3_vgizq * t_w3_vgizq; DCR_w3_p+_vgizq = Ru_w3_p+_vgizq / phi*Rn_w3_p+_vgizq`
- tipo_w3_vgizq: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 13 - Revisión de Resistencia soldadura #3 (viga alma vg_der - platina extremo vg_der)

### 13.1 Revisión capacidad a tracción (vg_der)

#### 13.1.1 ELR #1: Rotura de soldadura (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w3_p+_vgder = Fy_vgder * tw_vgder * hwef_w3_vgder; hwef_w3_vgder = pfi_pe_vgder + pb_pe_vgder + 150 mm; phi*Rn_w3_p+_vgder = phi * kds_w3_vgder * nl_w3_vgder * 0.6 * Fexx_w3_vgder * 0.707 * hwef_w3_vgder * t_w3_vgder; DCR_w3_p+_vgder = Ru_w3_p+_vgder / phi*Rn_w3_p+_vgder`
- tipo_w3_vgder: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 14 - Revisión de resistencia de la aleta de la columna

### 14.1. Revisión de capacidad a flexión (vg_izq)

#### 14.1.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); phi*Rn_cf_v2_col_vgizq = phi_ductil * ((tf_col^2 * Fy_col * Y_cs)/(1.11 * (d_vgizq - tf_vgizq))); DCR_cf_v2_col_vgizq = Ru_cf_v2_col_vgizq / phi*Rn_cf_v2_col_vgizq`
- phi usado: `1`
- Mf_vgizq_critico: `677.91 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `n/a`
- z_vgizq = d_vgizq - tf_vgizq: `n/a`
- tf_col: `40.4 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `7411.61 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.5`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgizq)`
- s_col: `105.11 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgizq: `n/a`
- phi*Rn_cf_v2_col_vgizq: `n/a`
- DCR_cf_v2_col_vgizq: `n/a`
- Resultado: `n/a`

Donde:

- Ecuacion Y_cs: `Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

### 14.2. Revisión de capacidad a flexión (vg_der)

#### 14.2.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); phi*Rn_cf_v2_col_vgder = phi_ductil * ((tf_col^2 * Fy_col * Y_cs)/(1.11 * (d_vgder - tf_vgder))); DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado: `1`
- Mf_vgder_critico: `677.91 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `n/a`
- z_vgder = d_vgder - tf_vgder: `n/a`
- tf_col: `40.4 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `7411.61 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.5`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgder)`
- s_col: `105.11 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgder: `n/a`
- phi*Rn_cf_v2_col_vgder: `n/a`
- DCR_cf_v2_col_vgder: `n/a`
- Resultado: `n/a`

Donde:

- Ecuacion Y_cs: `Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

## Paso 15 - Revisión de resistencia del alma de la columna

### 15.1. Revisión de capacidad a tracción (vg_izq)

#### 15.1.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado (phi_ductil): `1`
- Mf_vgizq_critico: `1587.51 kN-m`
- St_col: `762 mm`
- d_col: `508 mm`
- Ct_col: `1`
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
- Ru_cw_v2_col_vgizq: `2692.07 kN`
- phi*Rn_cw_v2_col_vgizq: `2893.47 kN`
- DCR_cw_v2_col_vgizq: `0.93`
- Resultado: `🟢 Cumple`

### 15.2. Revisión de capacidad a compresión (vg_izq)

#### 15.2.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; Rn_cw_v2_col_vgizq = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_cw_v2_col_vgizq; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado: `0.75`
- Mf_vgizq_critico: `1587.51 kN-m`
- St_col: `762 mm`
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
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgizq: `2692.07 kN`
- phi*Rn_cw_v2_col_vgizq: `3975.71 kN`
- DCR_cw_v2_col_vgizq: `0.68`
- Resultado: `🟢 Cumple`

#### 15.2.2. ELR #2: Pandeo local del alma (WCB)

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

### 15.3. Revisión de capacidad a tracción (vg_der)

#### 15.3.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado (phi_ductil): `1`
- Mf_vgder_critico: `1587.51 kN-m`
- St_col: `762 mm`
- d_col: `508 mm`
- Ct_col: `1`
- kc_col: `50.5 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- tw_col: `22.6 mm`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `0 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `0 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `2692.07 kN`
- phi*Rn_cw_v2_col_vgder: `2893.47 kN`
- DCR_cw_v2_col_vgder: `0.93`
- Resultado: `🟢 Cumple`

### 15.4. Revisión de capacidad a compresión (vg_der)

#### 15.4.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; Rn_cw_v2_col_vgder = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_cw_v2_col_vgder; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado: `0.75`
- Mf_vgder_critico: `1587.51 kN-m`
- St_col: `762 mm`
- d_col (dc): `508 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- E_col: `199947.96 MPa`
- tw_col: `22.6 mm`
- tf_col: `40.4 mm`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `0 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `0 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgder: `2692.07 kN`
- phi*Rn_cw_v2_col_vgder: `3975.71 kN`
- DCR_cw_v2_col_vgder: `0.68`
- Resultado: `🟢 Cumple`

#### 15.4.2. ELR #2: Pandeo local del alma (WCB)

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

### 15.5. Revisión de capacidad a cortante (col)

#### 15.5.1. ELR #1: Cortante en la zona del panel del alma (WPZS)

- Clausula: `Documento: AISC 360-22w | Seccion: AISC 360-22w Seccion J10.6 + Eq. (J10-9) to Eq. (J10-12)`
- Ecuacion: `Ru_wpz_v2_col = sum_Mf_col/(db-tf) - Vc2_col; Rn1_wpz_v2_col = 0.60*Fy_col*d_col*tw_col; Rn2_wpz_v2_col = 0.60*Fy_col*d_col*(n_dp_col*t_dp_col); Rn_wpz_v2_col = min{Rn1_wpz_v2_col, Rn2_wpz_v2_col} (J10-9)`
- Considera deformacion inelastica del panel zone: `No`
- phi_ductil (usado en WPZS): `1`
- hb_col: `762 mm`
- ht_col: `762 mm`
- Mbe_col_vgizq_max: `1718.1 kN-m`
- Mbe_col_vgizq_min: `1668.5 kN-m`
- Mbe_col_vgder_max: `1718.1 kN-m`
- Mbe_col_vgder_min: `1668.5 kN-m`
- sum_Mbe_col: `3386.6 kN-m`
- Vc2_col: `2222.18 kN`
- d_vgizq: `607 mm`
- Mf_vgizq_max: `1587.51 kN-m`
- Mf_vgizq_min: `1560.51 kN-m`
- d_vgder: `607 mm`
- Mf_vgder_max: `1587.51 kN-m`
- Mf_vgder_min: `1560.51 kN-m`
- sum_Mf_col/(db-tf): `5338.34 kN`
- Ru_wpz_v2_col: `3116.17 kN`
- Pr_col: `0 kN`
- Py_col: `11454 kN`
- alphaPr/Py: `0`
- Ag_col: `33200 mm2`
- Fy_col: `345 MPa`
- d_col: `508 mm`
- tw_col: `22.6 mm`
- t_dp_col: `22.6 mm`
- usar_weld_7_col: `False`
- tw_wpz_effective_col: `22.6 mm`
- Rn1_wpz_v2_col: `2376.53 kN`
- Rn2_wpz_v2_col: `2376.53 kN`
- bcf_col: `290 mm`
- tcf_col: `40.4 mm`
- Rn_wpz_v2_col: `2376.53 kN`
- DCR_wpz_v2_col: `1.31`
- Resultado: `🔴 No cumple`

## Paso 16 - Revisión de resistencia del alma de platinas de continuidad

### 16.1. Revisión de capacidad a tracción

#### 16.1.1. ELR #1: Fluencia por tracción area bruta

- Clausula: `Documento: AISC 358-22 | Seccion: Desarrollo interno de demanda para alma de platinas de continuidad`
- Ecuacion: `Ru_pc_p+_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq) - min{phi*Rn_(23.1.1), phi*Rn_(23.2.1), phi*Rn_(22.1.1)}; Ru_pc_p+_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder) - min{phi*Rn_(23.3.1), phi*Rn_(23.4.1), phi*Rn_(22.2.1)}; Ru_pc_p+_col = max{Ru_pc_p+_col_vgder, Ru_pc_p+_col_vgizq}; phi*Rn_pc_p+_col = phi * Fy_pc_col * b1_pc_col * t_pc_col * n_pc_col`
- Mf_vgizq_critico: `677.91 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `6375.88 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2893.47 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `3975.71 kN`
- min_capacidad_vgizq: `2893.47 kN`
- Ru_pc_p+_col_vgizq: `-1743.88 kN`
- Mf_vgder_critico: `677.91 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `6375.88 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2893.47 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `3975.71 kN`
- min_capacidad_vgder: `2893.47 kN`
- Ru_pc_p+_col_vgder: `-1743.88 kN`
- Ru_pc_p+_col: `-1743.88 kN`
- phi usado: `0.9`
- Fy_pc_col: `n/a`
- b1_pc_col: `n/a`
- t_pc_col: `15.9 mm`
- n_pc_col: `1`
- phi*Rn_pc_p+_col: `n/a`
- DCR_pc_p+_col: `n/a`
- Resultado: `n/a`

### 16.2. Revisión de capacidad a compresión

#### 16.2.1. ELR #1: Pandeo por flexión

- Clausula: `Documento: AISC 358-22 | Seccion: Formula de Fcr segun imagen de usuario (K=0.65)`
- Ecuacion: `n/a; phi*Rn_pc_p-_col = phi * Fcr_pc_col * b1_pc_col * t_pc_col * n_pc_col`
- Mf_vgizq_critico: `677.91 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `6375.88 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2893.47 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `3975.71 kN`
- min_capacidad_vgizq: `2893.47 kN`
- Ru_pc_p-_col_vgizq: `-1743.88 kN`
- Mf_vgder_critico: `677.91 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `6375.88 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2893.47 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `3975.71 kN`
- min_capacidad_vgder: `2893.47 kN`
- Ru_pc_p-_col_vgder: `-1743.88 kN`
- Ru_pc_p-_col: `-1743.88 kN`
- phi usado: `0.9`
- K: `0.65`
- Lp_pc_col: `n/a`
- r_pc_col: `n/a`
- KLr_pc_col: `n/a`
- E_pc_col: `n/a`
- Fy_pc_col: `n/a`
- Fe_pc_col: `n/a`
- Fcr_pc_col: `n/a`
- b1_pc_col: `n/a`
- t_pc_col: `15.9 mm`
- n_pc_col: `1`
- phi*Rn_pc_p-_col: `n/a`
- DCR_pc_p-_col: `n/a`
- Resultado: `n/a`

### 16.3. Revisión de capacidad a cortante

#### 16.3.1. ELR #1: Fluencia por cortante del area bruta

- Clausula: `Documento: AISC 360-22 | Seccion: G2.1 (adaptado a demanda de alma de platina de continuidad)`
- Ecuacion: `Ru_pc_v2_col = Ru_pc_p+_col_vgder + Ru_pc_p+_col_vgizq; phi*Rn_pc_v2_col = phi * 0.6 * Fy_pc_col * t_pc_col * n_pc_col * L2_pc_col; DCR_pc_v2_col = Ru_pc_v2_col / phi*Rn_pc_v2_col`
- Mf_vgizq_critico: `677.91 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `6375.88 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2893.47 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `3975.71 kN`
- min_capacidad_vgizq: `2893.47 kN`
- Ru_pc_p+_col_vgizq: `-1743.88 kN`
- Mf_vgder_critico: `677.91 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `6375.88 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2893.47 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `3975.71 kN`
- min_capacidad_vgder: `2893.47 kN`
- Ru_pc_p+_col_vgder: `-1743.88 kN`
- Ru_pc_v2_col: `-3487.77 kN`
- phi usado: `1`
- Fy_pc_col: `n/a`
- t_pc_col: `15.9 mm`
- n_pc_col: `1`
- L2_pc_col: `n/a`
- phi*Rn_pc_v2_col: `n/a`
- DCR_pc_v2_col: `n/a`
- Resultado: `n/a`

## Paso 17- Revisión de resistencia de soldadura # 5 ( Platina de continuidad con aleta de columna)

### 17.1. Revisión de capacidad a tracción

#### 17.1.1. ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Ru_w5_p+_col = Fy_pc_col * b2_pc_col * t_pc_col * n_pc_col; Fillet: phi*Rn_w5_p+_col = phi_fragil * kds_w5_col * nl_w5_col * 0.6 * Fexx_w5_col * 0.707 * L_w5_col * w_w5_col * n_pc_col; DCR_w5_p+_col = Ru_w5_p+_col / phi*Rn_w5_p+_col`
- tipo_w5_col: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 18- Revisión de resistencia de soldadura # 6 ( Platina de continuidad con alma de columna)

### 18.1. Revisión de capacidad a cortante

#### 18.1.1. ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Ru1_w5_v2_col = 0.6 * Fy_pc_col * L2_pc_col * t_pc_col; Ru2_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * L_w6_col; Ru3_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * L_w6_col; Ru4_w5_v2_col = 0.6 * fu_col * tw_col * L_w6_col; Ru5_w5_v2_col = 0.6 * fy_col * tw_col * L_w6_col; Ru6_w5_v2_col = 0.6 * fu_col * tw_col * d_col; Ru7_w5_v2_col = 0.6 * fy_col * tw_col * d_col * Cv1; Ru8_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * wz_dp_col; Ru9_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * wz_dp_col; Ru_w5_v2_col = MIN{Ru1..Ru9}; Fillet: phi*Rn_w6_v2_col = phi_fragil * kds_w6_col * nl_w6_col * 0.6 * Fexx_w6_col * 0.707 * L_w6_col * w_w6_col; DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`
- tipo_w6_col: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

### 18.6. Revisión de capacidad del material base

#### 18.6.2. ELR #1: Rotura del material base

- Clausula: `AISC 360-22 J4 (material base)`
- Ecuacion: `Ru_w5_v2_col = MIN{Ru1..Ru9}; phi*Rn1_w6-dp_v2_col = phi_fragil * 0.6 * fu_dp_col * t_dp_col * L_w6_col; phi*Rn2_w6-dp_v2_col = phi_no_ductil * 0.6 * fy_dp_col * t_dp_col * L_w6_col; phi*Rn1_w6-cw_v2_col = phi_fragil * 0.6 * fu_col * tw_col * L_w6_col; phi*Rn2_w6-cw_v2_col = phi_no_ductil * 0.6 * fy_col * tw_col * L_w6_col; phi*Rn_w6_v2_col = min(phi*Rn1_w6-dp_v2_col, phi*Rn2_w6-dp_v2_col, phi*Rn1_w6-cw_v2_col, phi*Rn2_w6-cw_v2_col); DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`
- tipo_w6_col: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 19- Revisión de resistencia de soldadura # 8 (Platina de enchape con aleta de columna)

### 19.1. Revisión de capacidad a cortante

#### 19.1.1. ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Ru_w8_v2_col = max{Ru1_w8_v2_col, Ru2_w8_v2_col}; Ru1_w8_v2_col = 0.6 * Fy_dp_col * h_dp_col * t_dp_col; Ru2_w8_v2_col = max{Mf_vgizq_max + Mf_vgder_min, Mf_vgder_max + Mf_vgizq_min} * (t_dp_col/(t_dp_col*n_dp_col + tw_col)) / b_dp_col; Fillet: L_w8_col = h_dp_col - 2*L_gap_w8_col; phi*Rn_w8_v2_col = phi_fragil * kds_w8_col * nl_w8_col * 0.6 * Fexx_w8_col * 0.707 * L_w8_col * w_w8_col; DCR_w8_v2_col = Ru_w8_v2_col / phi*Rn_w8_v2_col`
- tipo_w8_col: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 20- Revisión de resistencia de soldadura # 7 (Platina de enchape con alma de columna)

### 20.1. Revisión de capacidad a cortante

#### 20.1.1. ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + Desarrollo interno`
- Ecuacion: `Ru_w7_v2_col = Ru_wpz_v2_col * (t_dp_col / (t_dp_col*n_dp_col + tw_col)); phi*Rn_w7_v2_col = phi_fragil * (nfilas_w7_col)*(ncolumna_w7_col) * 0.60 * Fexx_w7_col * 0.25 * 3.1416 * d_hole_w7_col^2; DCR_w7_v2_col = Ru_w7_v2_col / phi*Rn_w7_v2_col`
- phi usado (phi_fragil): `0.75`
- nfilas_w7_col: `1`
- ncolumna_w7_col: `1`
- Ru_wpz_v2_col: `3116.17 kN`
- t_dp_col: `22.6 mm`
- n_dp_col: `1`
- tw_col: `22.6 mm`
- Fexx_w7_col: `490 MPa`
- d_hole_w7_col (usado en formula): `n/a`
- Ru_w7_v2_col: `1558.08 kN`
- phi*Rn_w7_v2_col: `n/a`
- DCR_w7_v2_col: `n/a`
- Resultado: `n/a`

## Paso 21 - Resumen general

DCR ordenados de mayor a menor para identificar los estados limite criticos.

- DCR critico global: 🔴 `DCR_pe_m3_vgizq = 1.54` en `10.1.1. ELR #1: Fluencia (vg_izq)`

1. 🔴 `DCR_pe_m3_vgizq` = `1.54`
Subcapitulo aplicado: `10.1.1. ELR #1: Fluencia (vg_izq)`
2. 🔴 `DCR_pe_m3_vgder` = `1.54`
Subcapitulo aplicado: `11.1.1. ELR #1: Fluencia (vg_der)`
3. 🔴 `DCR_b_p+_vgizq` = `1.49`
Subcapitulo aplicado: `8.1.1 Estado #1: Rotura en el perno (vg_izq)`
4. 🔴 `DCR_b_p+_vgder` = `1.49`
Subcapitulo aplicado: `9.1.1 Estado #1: Rotura en el perno (vg_der)`
5. 🔴 `DCR_wpz_v2_col` = `1.31`
Subcapitulo aplicado: `15.5.1. ELR #1: Cortante en la zona del panel del alma (WPZS)`
6. 🔴 `DCR_pe_v2_vgizq` = `1.17`
Subcapitulo aplicado: `10.2.2. ELR #2: Rotura por cortante (vg_izq)`
7. 🔴 `DCR_pe_v2_vgder` = `1.17`
Subcapitulo aplicado: `11.2.2. ELR #2: Rotura por cortante (vg_der)`
8. 🔴 `DCR_pe_v1_vgizq` = `1.01`
Subcapitulo aplicado: `10.2.1. ELR #1: Fluencia por cortante (vg_izq)`
9. 🔴 `DCR_pe_v1_vgder` = `1.01`
Subcapitulo aplicado: `11.2.1. ELR #1: Fluencia por cortante (vg_der)`
10. 🟢 `DCR_cw_v2_col_vgizq` = `0.93`
Subcapitulo aplicado: `15.1.1. ELR #1: Fluencia local del alma (WLY)`
11. 🟢 `DCR_cw_v2_col_vgder` = `0.93`
Subcapitulo aplicado: `15.3.1. ELR #1: Fluencia local del alma (WLY)`
12. 🟢 `DCR_cw_v2_col_vgizq` = `0.68`
Subcapitulo aplicado: `15.2.1. ELR #1: Arrugamiento local del alma (WLC)`
13. 🟢 `DCR_cw_v2_col_vgder` = `0.68`
Subcapitulo aplicado: `15.4.1. ELR #1: Arrugamiento local del alma (WLC)`
14. 🟢 `DCR_b_v2_vgizq` = `0.47`
Subcapitulo aplicado: `8.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)`
15. 🟢 `DCR_b_v2_vgder` = `0.47`
Subcapitulo aplicado: `9.2.1 ELR #2: Rotura por cortante en el perno (vg_der)`
16. 🟢 `DCR_pe_v2_vgizq` = `0.18`
Subcapitulo aplicado: `10.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_izq)`
17. 🟢 `DCR_pe_v2_vgder` = `0.18`
Subcapitulo aplicado: `11.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_der)`
18. 🟢 `DCR_pe_v2_vgizq` = `0.12`
Subcapitulo aplicado: `10.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_izq)`
19. 🟢 `DCR_pe_v2_vgder` = `0.12`
Subcapitulo aplicado: `11.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_der)`
