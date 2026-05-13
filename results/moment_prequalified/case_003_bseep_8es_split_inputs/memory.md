# Memoria de Cálculo

- Proyecto: `proj_bseep_si_demo`
- Caso: `case_si_bseep_8es_w18x175_w24x76 | perfiles: vgizq=W21X68, vgder=W21X68, col=HEB 500`
- Familia: `moment_prequalified`
- Tipo: `bseep_8es`
- Estado global: `🟢 Cumple`

## Paso 1 - Propiedades geométricas, mecánicas y fabricación

Propiedades organizadas por ámbito.

### 1.1 Ámbito `BEAM_IZQ`

#### 1.1.1 Resumen de geometría

- Perfil de viga izquierda (perfil_vgizq) (inp): `W21X68`
- Tipo de acero del perfil de viga izquierda (tipo_acero_perfil_vgizq) (inp): `ASTM A572 Gr 50`
- Demanda de ductilidad de viga izquierda (demanda_ductilidad_vgizq) (inp): `high`
- Luz libre de viga izquierda (Llb_vgizq) (inp): `7500 mm`
- Longitud sin conectores desde cara de columna (Lnc_vgizq) (inp): `1000 mm`
- Longitud de zona protegida (Lpz_vgizq): `628 mm`

### 1.2 Ámbito `BEAM_DER`

#### 1.2.1 Resumen de geometría

- Perfil de viga derecha (perfil_vgder) (inp): `W21X68`
- Tipo de acero del perfil de viga derecha (tipo_acero_perfil_vgder) (inp): `ASTM A572 Gr 50`
- Demanda de ductilidad de viga derecha (demanda_ductilidad_vgder) (inp): `high`
- Luz libre de viga derecha (Llb_vgder) (inp): `7500 mm`
- Longitud sin conectores desde cara de columna (Lnc_vgder) (inp): `1000 mm`
- Longitud de zona protegida (Lpz_vgder): `628 mm`

### 1.3 Ámbito `END_PLATE_IZQ`

#### 1.3.1 Resumen de geometría

- Altura de platina extremo de viga izquierda (Hpe_vgizq): `950 mm`
- Ancho de platina extremo de viga izquierda (Bpe_vgizq) (inp): `230 mm`
- Espesor de platina extremo de viga izquierda (tpe_vgizq) (inp): `25 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgizq) (inp): `62 mm`
- Distancia entre filas de pernos (pb_pe_vgizq) (inp): `95 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgizq) (inp): `50 mm`
- Distancia interior a fila de pernos (pfi_pe_vgizq) (inp): `50 mm`
- Diámetro de perforación de perno (dh_pe_vgizq): `28.57 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgizq) (inp): `150 mm`
- Distancia horizontal de borde en platina (deh_pe_vgizq): `40 mm`
- Parametro s de platina extremo izquierda (s_pe_vgizq): `92.87 mm`
- Distancia h1 de platina extremo izquierda (h1_pe_vgizq): `672.3 mm`
- Distancia h2 de platina extremo izquierda (h2_pe_vgizq): `577.3 mm`
- Distancia h3 de platina extremo izquierda (h3_pe_vgizq): `459.9 mm`
- Distancia h4 de platina extremo izquierda (h4_pe_vgizq): `364.9 mm`

### 1.4 Ámbito `END_PLATE_DER`

#### 1.4.1 Resumen de geometría

- Altura de platina extremo de viga derecha (Hpe_vgder): `950 mm`
- Ancho de platina extremo de viga derecha (Bpe_vgder) (inp): `230 mm`
- Espesor de platina extremo de viga derecha (tpe_vgder) (inp): `25 mm`
- Distancia de borde a fila 1 de pernos (de_pe_vgder) (inp): `62 mm`
- Distancia entre filas de pernos (pb_pe_vgder) (inp): `95 mm`
- Distancia exterior a fila de pernos (pfo_pe_vgder) (inp): `50 mm`
- Distancia interior a fila de pernos (pfi_pe_vgder) (inp): `50 mm`
- Diámetro de perforación de perno (dh_pe_vgder): `28.57 mm`
- Distancia horizontal entre pernos en platina (g_pe_vgder) (inp): `150 mm`
- Distancia horizontal de borde en platina (deh_pe_vgder): `40 mm`
- Parametro s de platina extremo derecha (s_pe_vgder): `92.87 mm`
- Distancia h1 de platina extremo derecha (h1_pe_vgder): `672.3 mm`
- Distancia h2 de platina extremo derecha (h2_pe_vgder): `577.3 mm`
- Distancia h3 de platina extremo derecha (h3_pe_vgder): `459.9 mm`
- Distancia h4 de platina extremo derecha (h4_pe_vgder): `364.9 mm`

### 1.5 Ámbito `COLUMN`

#### 1.5.1 Resumen de geometría

- Perfil de columna (shape_col) (inp): `HEB 500`
- Tipo de acero del perfil de columna (tipo_acero_perfil_col) (inp): `ASTM A572 Gr 50`
- Altura de columna (d_col) (inp): `500 mm`
- Espesor de alma de columna (tw_col) (inp): `14.5 mm`
- Espesor de ala de columna (tf_col) (inp): `28 mm`
- Ancho de ala de columna (bf_col) (inp): `300 mm`
- Proyeccion de columna sobre vigas (St_col) (inp): `2500 mm`
- Distancia al punto de inflexion superior (ht_col) (inp): `1250 mm`
- Distancia al punto de inflexion inferior (hb_col) (inp): `1250 mm`
- gage horizontal de pernos en columna lado izquierda (g_b_col_vgizq) (inp): `150 mm`
- Distancia exterior ajustada lado izquierda (pso_vgizq): `50.7 mm`
- Distancia interior ajustada lado izquierda (psi_vgizq): `50.7 mm`
- Diámetro de perforación en columna lado izquierda (dh_col_vgizq): `28.57 mm`
- Parametro C de columna lado izquierda (C_col_vgizq): `117.4 mm`
- Parametro s de columna lado izquierda (s_col_vgizq): `106.07 mm`
- Distancia h1 de columna lado izquierda (h1_col_vgizq): `672.3 mm`
- Distancia h2 de columna lado izquierda (h2_col_vgizq): `577.3 mm`
- Distancia h3 de columna lado izquierda (h3_col_vgizq): `459.9 mm`
- Distancia h4 de columna lado izquierda (h4_col_vgizq): `364.9 mm`
- gage horizontal de pernos en columna lado derecha (g_b_col_vgder) (inp): `150 mm`
- Distancia exterior ajustada lado derecha (pso_vgder): `50.7 mm`
- Distancia interior ajustada lado derecha (psi_vgder): `50.7 mm`
- Diámetro de perforación en columna lado derecha (dh_col_vgder): `28.57 mm`
- Parametro C de columna lado derecha (C_col_vgder): `117.4 mm`
- Parametro s de columna lado derecha (s_col_vgder): `106.07 mm`
- Distancia h1 de columna lado derecha (h1_col_vgder): `672.3 mm`
- Distancia h2 de columna lado derecha (h2_col_vgder): `577.3 mm`
- Distancia h3 de columna lado derecha (h3_col_vgder): `459.9 mm`
- Distancia h4 de columna lado derecha (h4_col_vgder): `364.9 mm`

### 1.6 Ámbito `END_PLATE_STIFFENER_DER`

#### 1.6.1 Resumen de geometría

- Tipo de acero de rigidizador derecha (tipo_acero_pest_vgder) (inp): `ASTM A572 Gr 50`
- Espesor de rigidizador derecha (t_pest_vgder) (inp): `16 mm`
- Altura del rigidizador de platina extremo derecha (h_pest_vgder): `207 mm`
- Longitud del rigidizador de platina extremo derecha (L_pest_vgder): `360 mm`
- Requisito de borde del rigidizador de platina extremo derecha (Ed_pest_vgder): `25 mm`

### 1.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### 1.7.1 Resumen de geometría

- Tipo de acero de rigidizador izquierda (tipo_acero_pest_vgizq) (inp): `ASTM A572 Gr 50`
- Espesor de rigidizador izquierda (t_pest_vgizq) (inp): `16 mm`
- Altura del rigidizador de platina extremo izquierda (h_pest_vgizq): `207 mm`
- Longitud del rigidizador de platina extremo izquierda (L_pest_vgizq): `360 mm`
- Requisito de borde del rigidizador de platina extremo izquierda (Ed_pest_vgizq): `25 mm`

### 1.8 platinas de continuidad

#### 1.8.1 Resumen de geometría

- Uso de platinas de continuidad (usar_pc_col) (inp): `True`
- Tipo de acero de platina de continuidad (tipo_acero_pc_col) (inp): `ASTM A572 Gr 50`
- Espesor de platina de continuidad (t_pc_col) (inp): `16 mm`
- Ancho base de platina de continuidad (b1_pc_col) (inp): `130 mm`
- Ancho b1.1 de platina de continuidad (b1.1_pc_col): `130 mm`
- Ancho b1.2 de platina de continuidad (b1.2_pc_col): `130 mm`
- Distancia de recorte 1 de platina de continuidad (Clip1_pc_col): `65 mm`
- Longitud útil 1 de platina de continuidad (L1_pc_col): `441 mm`
- Longitud útil 2 de platina de continuidad (L2_pc_col): `311 mm`
- Distancia de recorte 2 de platina de continuidad (Clip2_pc_col): `25 mm`
- Ancho neto de platina de continuidad (b2_pc_col): `105 mm`

### 1.9 platina de enchape del alma

#### 1.9.1 Resumen de geometría

- Uso de platina de enchape del alma (usar_dp_col) (inp): `True`
- Tipo de acero de platina de enchape del alma (tipo_acero_dp_col) (inp): `ASTM A572 Gr 50`
- Espesor de platina de enchape del alma (t_dp_col) (inp): `12 mm`
- Número de platinas de enchape del alma (n_dp_col) (inp): `2`
- Condición geometrica de platina de enchape (Extended_dp_col) (inp): `True`
- Separación de la platina de enchape respecto al alma (gap_dp_col) (inp): `0 mm`
- Estado de contacto platina de enchape vs alma: `En contacto con el alma (gap_dp_col <= 2.0 mm)`
- Altura de la zona de panel (dz_dp_col): `501.2 mm`
- Ancho de zona de panel (wz_dp_col): `444 mm`
- Distancia vertical entre soldaduras tipo 7 (plug) o al borde de la zona de panel (h_w7_col): `125.3 mm`
- Distancia horizontal entre soldaduras tipo 7 (plug) o al borde de la zona de panel (b_w7_col): `130 mm`
- Altura de platina de enchape (h_dp_col): `840 mm`
- Ecuación de h_dp_col: `h_dp_col = 300 mm + max{d_vgder, d_vgizq}` (aplica cuando (`Extended_dp_col=false` y `usar_pc_col=false`) o (`Extended_dp_col=true` y `usar_pc_col=true`))
- Ancho de platina de enchape (b_dp_col): `390 mm`
- Ecuación de b_dp_col: `b_dp_col = d_col - 2*kdet_col` (cuando `tipo_w8_col = CJP` o `PJP`)

### 1.10 Ámbito `BOLTS_DER`

#### 1.10.1 Resumen de geometría

- Diámetro nominal de perno lado derecha (db_b_vgder) (inp): `25.4 mm`
- Resistencia nominal a tracción de perno lado derecha (Fnt_b_vgder) (inp): `780 MPa`
- Resistencia nominal a cortante de perno lado derecha (Fnv_b_vgder) (inp): `470 MPa`
- Condición de rosca de perno lado derecha (thread_b_vgder) (inp): `N`
- Número de pernos lado derecha (n_b_vgder) (inp): `8`
- Norma de fabricación del perno lado derecha (std_v_vgder) (inp): `ASTM A490`
- Tipo de apriete del perno lado derecha (tipo_apriete_b_vgder) (inp): `pretensioned`
- Area efectiva de perno lado derecha (A_b_vgder): `506.71 mm2`

### 1.11 Ámbito `BOLTS_IZQ`

#### 1.11.1 Resumen de geometría

- Diámetro nominal de perno lado izquierda (db_b_vgizq) (inp): `25.4 mm`
- Resistencia nominal a tracción de perno lado izquierda (Fnt_b_vgizq) (inp): `780 MPa`
- Resistencia nominal a cortante de perno lado izquierda (Fnv_b_vgizq) (inp): `470 MPa`
- Condición de rosca de perno lado izquierda (thread_b_vgizq) (inp): `N`
- Número de pernos lado izquierda (n_b_vgizq) (inp): `8`
- Norma de fabricación del perno lado izquierda (std_v_vgizq) (inp): `ASTM A490`
- Tipo de apriete del perno lado izquierda (tipo_apriete_b_vgizq) (inp): `pretensioned`
- Area efectiva de perno lado izquierda (A_b_vgizq): `506.71 mm2`

### 1.12 Ámbito `WELD_1_VGDER`

#### 1.12.1 Resumen de geometría

- Tipo de soldadura #1 lado derecha (tipo_w1_vgder) (inp): `CJP`
- Resistencia del electrodo de soldadura #1 lado derecha (Fexx_w1_vgder) (inp): `485 MPa`
- Espesor/size de soldadura #1 lado derecha (w_w1_vgder) (inp): `0 mm`
- Número de lineas de soldadura #1 lado derecha (nl_w1_vgder) (inp): `1`
- Separación de extremos de soldadura #1 lado derecha (L_gap_w1_vgder) (inp): `25 mm`
- Factor de dirección/sistema de soldadura #1 lado derecha (kds_w1_vgder) (inp): `1`
- Longitud efectiva de soldadura #1 lado derecha (L_w1_vgder): `132 mm`

### 1.13 Ámbito `WELD_1_VGIZQ`

#### 1.13.1 Resumen de geometría

- Tipo de soldadura #1 lado izquierda (tipo_w1_vgizq) (inp): `CJP`
- Resistencia del electrodo de soldadura #1 lado izquierda (Fexx_w1_vgizq) (inp): `485 MPa`
- Espesor/size de soldadura #1 lado izquierda (w_w1_vgizq) (inp): `0 mm`
- Número de lineas de soldadura #1 lado izquierda (nl_w1_vgizq) (inp): `1`
- Separación de extremos de soldadura #1 lado izquierda (L_gap_w1_vgizq) (inp): `25 mm`
- Factor de dirección/sistema de soldadura #1 lado izquierda (kds_w1_vgizq) (inp): `1`
- Longitud efectiva de soldadura #1 lado izquierda (L_w1_vgizq): `132 mm`

### 1.14 Ámbito `WELD_2_VGDER`

#### 1.14.1 Resumen de geometría

- Tipo de soldadura #2 lado derecha (tipo_w2_vgder) (inp): `CJP`
- Resistencia del electrodo de soldadura #2 lado derecha (Fexx_w2_vgder) (inp): `485 MPa`
- Espesor/size de soldadura #2 lado derecha (w_w2_vgder) (inp): `0 mm`
- Número de lineas de soldadura #2 lado derecha (nl_w2_vgder) (inp): `1`
- Separación de extremos de soldadura #2 lado derecha (L_gap_w2_vgder) (inp): `25 mm`
- Factor de dirección/sistema de soldadura #2 lado derecha (kds_w2_vgder) (inp): `1`
- Longitud efectiva de soldadura #2 lado derecha (L_w2_vgder): `285 mm`

### 1.15 Ámbito `WELD_2_VGIZQ`

#### 1.15.1 Resumen de geometría

- Tipo de soldadura #2 lado izquierda (tipo_w2_vgizq) (inp): `CJP`
- Resistencia del electrodo de soldadura #2 lado izquierda (Fexx_w2_vgizq) (inp): `485 MPa`
- Espesor/size de soldadura #2 lado izquierda (w_w2_vgizq) (inp): `0 mm`
- Número de lineas de soldadura #2 lado izquierda (nl_w2_vgizq) (inp): `1`
- Separación de extremos de soldadura #2 lado izquierda (L_gap_w2_vgizq) (inp): `25 mm`
- Factor de dirección/sistema de soldadura #2 lado izquierda (kds_w2_vgizq) (inp): `1`
- Longitud efectiva de soldadura #2 lado izquierda (L_w2_vgizq): `285 mm`

### 1.16 Ámbito `WELD_3_VGDER`

#### 1.16.1 Resumen de geometría

- Tipo de soldadura #3 lado derecha (tipo_w3_vgder) (inp): `CJP`
- Resistencia del electrodo de soldadura #3 lado derecha (Fexx_w3_vgder) (inp): `485 MPa`
- Espesor/size de soldadura #3 lado derecha (w_w3_vgder) (inp): `8 mm`
- Número de lineas de soldadura #3 lado derecha (nl_w3_vgder) (inp): `2`
- Longitud efectiva de soldadura #3 lado derecha (hwef_w3_vgder): `295 mm`

### 1.17 Ámbito `WELD_3_VGIZQ`

#### 1.17.1 Resumen de geometría

- Tipo de soldadura #3 lado izquierda (tipo_w3_vgizq) (inp): `CJP`
- Resistencia del electrodo de soldadura #3 lado izquierda (Fexx_w3_vgizq) (inp): `485 MPa`
- Espesor/size de soldadura #3 lado izquierda (w_w3_vgizq) (inp): `8 mm`
- Número de lineas de soldadura #3 lado izquierda (nl_w3_vgizq) (inp): `2`
- Longitud efectiva de soldadura #3 lado izquierda (hwef_w3_vgizq): `295 mm`

### 1.18 Ámbito `WELD_4_VGDER`

#### 1.18.1 Resumen de geometría

- Tipo de soldadura #4 lado derecha (tipo_w4_vgder) (inp): `cjp`
- Resistencia del electrodo de soldadura #4 lado derecha (Fexx_w4_vgder) (inp): `485 MPa`
- Espesor/size de soldadura #4 lado derecha (w_w4_vgder) (inp): `8 mm`
- Espesor total de garganta requerida #4 lado derecha (t_w4.1_vgder) (inp): `8 mm`
- Número de lineas de soldadura #4 lado derecha (nl_w4_vgder) (inp): `2`
- Factor de dirección/sistema de soldadura #4 lado derecha (kds_w4_vgder) (inp): `1`
- Longitud efectiva de soldadura #4 lado derecha (L_w4_vgder): `210 mm`

### 1.19 Ámbito `WELD_4_VGIZQ`

#### 1.19.1 Resumen de geometría

- Tipo de soldadura #4 lado izquierda (tipo_w4_vgizq) (inp): `cjp`
- Resistencia del electrodo de soldadura #4 lado izquierda (Fexx_w4_vgizq) (inp): `485 MPa`
- Espesor/size de soldadura #4 lado izquierda (w_w4_vgizq) (inp): `8 mm`
- Espesor total de garganta requerida #4 lado izquierda (t_w4.1_vgizq) (inp): `8 mm`
- Número de lineas de soldadura #4 lado izquierda (nl_w4_vgizq) (inp): `2`
- Factor de dirección/sistema de soldadura #4 lado izquierda (kds_w4_vgizq) (inp): `1`
- Longitud efectiva de soldadura #4 lado izquierda (L_w4_vgizq): `210 mm`

### 1.20 Ámbito `WELD_5_COL`

#### 1.20.1 Resumen de geometría

- Tipo de soldadura #5 de platina de continuidad (tipo_w5_col) (inp): `CJP`
- Resistencia del electrodo de soldadura #5 (Fexx_w5_col) (inp): `485 MPa`
- Espesor/size de soldadura #5 (w_w5_col) (inp): `12.7 mm`
- Número de lineas de soldadura #5 (nl_w5_col) (inp): `2`
- Separación de extremos de soldadura #5 (L_gap_w5_col) (inp): `12.7 mm`
- Factor de dirección/sistema de soldadura #5 (kds_w5_col) (inp): `1.5`
- Longitud efectiva de soldadura #5 (L_w5_col): `82.7 mm`

### 1.21 Ámbito `WELD_6_COL`

#### 1.21.1 Resumen de geometría

- Tipo de soldadura #6 de platina de continuidad (tipo_w6_col) (inp): `CJP`
- Resistencia del electrodo de soldadura #6 (Fexx_w6_col) (inp): `485 MPa`
- Espesor/size de soldadura #6 (w_w6_col) (inp): `12 mm`
- Número de lineas de soldadura #6 (nl_w6_col) (inp): `2`
- Separación de extremos de soldadura #6 (L_gap_w6_col) (inp): `25 mm`
- Factor de dirección/sistema de soldadura #6 (kds_w6_col) (inp): `1`
- Longitud efectiva de soldadura #6 (Lws_col): `261 mm`

### 1.22 Ámbito `WELD_7_COL`

#### 1.22.1 Resumen de geometría

- Tipo de soldadura #7 (tipo_w7_col) (inp): `plug`
- Resistencia del electrodo de soldadura #7 (Fexx_w7_col) (inp): `485 MPa`
- Espesor/size de soldadura #7 (w_w7_col) (inp): `16 mm`
- Número de filas de soldadura #7 (nfilas_w7_col) (inp): `3`
- Número de columnas de soldadura #7 (ncolumna_w7_col) (inp): `2`
- Diámetro de hueco para soldadura #7 (d_hole_w7_col) (inp): `31 mm`
- Distancia horizontal entre soldaduras tipo 7 (plug) o al borde de la zona de panel (b_w7_col): `130 mm`
- Distancia vertical entre soldaduras tipo 7 (plug) o al borde de la zona de panel (h_w7_col): `125.3 mm`
- Espesor de parte contenedora (t_part_w7_col = t_pc_col): `16 mm`

### 1.23 Ámbito `WELD_8_COL`

#### 1.23.1 Resumen de geometría

- Tipo de soldadura #8 (tipo_w8_col) (inp): `PJP`
- Nota PJP soldadura #8: `Debe ser conforme a AWS D1.8/D1.8M clause 4.3`
- Resistencia del electrodo de soldadura #8 (Fexx_w8_col) (inp): `485 MPa`
- Espesor/size de soldadura #8 (w_w8_col) (inp): `8 mm`
- Número de lineas de soldadura #8 (nl_w8_col) (inp): `1`
- Parametro Encr para soldadura #8 (Encr_w8_col): `7.9 mm`
- Fuente de Encr_w8_col: `AISC 16th Fig 10-3, rango 22.2 - 31.8 mm`
- Factor de dirección/sistema de soldadura #8 (kds_w8_col) (inp): `1`

### 1.24 Ámbito `WELD_9_COL`

#### 1.24.1 Resumen de geometría

- Uso de soldadura #9 (use_weld_9_col) (inp): `False`
- Tipo de soldadura #9 (tipo_w9_col) (inp): `fillet`
- Resistencia del electrodo de soldadura #9 (Fexx_w9_col) (inp): `485 MPa`
- Espesor/size de soldadura #9 (w_w9_col) (inp): `8 mm`
- Número de lineas de soldadura #9 (nl_w9_col) (inp): `2`
- Separación de extremos de soldadura #9 (L_gap_w9_col) (inp): `50 mm`
- Factor de dirección/sistema de soldadura #9 (kds_w9_col) (inp): `1`
- Longitud efectiva de soldadura #9 (L_w9_col): `0 mm`

## Paso 2 - Especificaciones técnicas

Especificaciones tecnicas organizadas por ámbito.

### 2.1 Ámbito `BEAM_IZQ`

### 2.2 Ámbito `BEAM_DER`

### 2.3 Ámbito `END_PLATE_IZQ`

### 2.4 Ámbito `END_PLATE_DER`

### 2.5 Ámbito `COLUMN`

#### 2.5.1 Nota técnica - Ubicacion de la conexión de placa de extremo en columna

- Ámbito: `COLUMN`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 (2)`
- Requisito: `La placa de extremo debe conectarse al ala de la columna.`

### 2.6 Ámbito `END_PLATE_STIFFENER_DER`

### 2.7 Ámbito `END_PLATE_STIFFENER_IZQ`

### 2.8 Ámbito `CONTINUITY_PLATE_COL`

### 2.9 Ámbito `DOUBLER_PLATE_COL`

### 2.10 Ámbito `BOLTS_DER`

#### 2.10.1 Nota técnica - Requisitos de instalacion para conjuntos empernados (right beam)

- Ámbito: `BOLTS_DER`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estándar indique lo contrario.`

#### 2.10.2 Nota técnica - Control y aseguramiento de calidad para conjuntos empernados (right beam)

- Ámbito: `BOLTS_DER`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 2.11 Ámbito `BOLTS_IZQ`

#### 2.11.1 Nota técnica - Requisitos de instalacion para conjuntos empernados (left beam)

- Ámbito: `BOLTS_IZQ`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estándar indique lo contrario.`

#### 2.11.2 Nota técnica - Control y aseguramiento de calidad para conjuntos empernados (left beam)

- Ámbito: `BOLTS_IZQ`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 2.12 Ámbito `WELD_1_VGDER`

### 2.13 Ámbito `WELD_1_VGIZQ`

### 2.14 Ámbito `WELD_2_VGDER`

### 2.15 Ámbito `WELD_2_VGIZQ`

### 2.16 Ámbito `WELD_3_VGDER`

### 2.17 Ámbito `WELD_3_VGIZQ`

### 2.18 Ámbito `WELD_4_VGDER`

### 2.19 Ámbito `WELD_4_VGIZQ`

### 2.20 Ámbito `WELD_5_COL`

### 2.21 Ámbito `WELD_6_COL`

### 2.22 Ámbito `WELD_7_COL`

### 2.23 Ámbito `WELD_8_COL`

### 2.24 Ámbito `WELD_9_COL`

## Paso 3 - Revisiones de requerimientos de propiedades mecánicas y geométricas

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### 3.1 Ámbito `BEAM_IZQ`

#### Chequeo 3.1.1 - Familia de perfil de viga permitida para precalificación (viga izquierda) (`perfil_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `perfil_vgizq in {W, HEA, HEB, IPE}; 'W21X68' in {W, HEA, HEB, IPE}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.2 - Ancho de placa de extremo vs ancho de ala de viga (left beam) (`bp_pe_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `bp_pe_vgizq <= bf_vgizq + margin (25 mm); 230 mm <= 235 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.3 - Longitud sin conectores de cortante desde la cara de columna (left beam) (`Lnc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `Lnc_vgizq >= 1.5d_vgizq; 1000 mm >= 804 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.4 - Criterio de despeje de viga con umbral Sc y S (left beam) (`Sc_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `Sc_vgizq = St_col - pfo_vgizq - pb_vgizq; S_vgizq = 0.5*sqrt(bcf*g_vgizq); Sc_vgizq > S_vgizq => 2355.000 mm > 106.066 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.5 - Relacion luz libre/peralte por sistema de marco (left beam) (`Llb_vgizq/d_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `Llb_vgizq/d_vgizq >= 7 (SMF); 13.99 adim >= 7 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.6 - Compacidad ancho-espesor del ala de viga (left beam) (`lambda_f_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `lambda_f_vgizq <= lambda_f_limit; 6.03 adim <= 6.89 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w / AISC 358-22w Sección 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.7 - Compacidad ancho-espesor del alma de viga (left beam) (`lambda_w_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `lambda_w_vgizq <= lambda_w_limit; 43.63 adim <= 56.24 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w / AISC 358-22w Sección 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.8 - Limites de ancho del ala de viga (left beam) (`bf_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `bf_vgizq in [bf_vgizq_min, bf_vgizq_max]; 190.5 mm <= 210 mm <= 311.15 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.1.9 - Limites de peralte de la viga conectada (left beam) (`d_vgizq`)

- Ámbito: `BEAM_IZQ`
- Verificación: `d_vgizq in [d_vgizq_min, d_vgizq_max]; 457.2 mm <= 536 mm <= 914.4 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.2 Ámbito `BEAM_DER`

#### Chequeo 3.2.1 - Familia de perfil de viga permitida para precalificación (viga derecha) (`perfil_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `perfil_vgder in {W, HEA, HEB, IPE}; 'W21X68' in {W, HEA, HEB, IPE}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.2 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `bp_pe_vgder <= bf_vgder + margin (25 mm); 230 mm <= 235 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.3 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 804 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.4 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `Sc_vgder = St_col - pfo_vgder - pb_vgder; S_vgder = 0.5*sqrt(bcf*g_vgder); Sc_vgder > S_vgder => 2355.000 mm > 106.066 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.5 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `Llb_vgder/d_vgder >= 7 (SMF); 13.99 adim >= 7 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.6 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `lambda_f_vgder <= lambda_f_limit; 6.03 adim <= 6.89 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w / AISC 358-22w Sección 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.7 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `lambda_w_vgder <= lambda_w_limit; 43.63 adim <= 56.24 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w / AISC 358-22w Sección 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.8 - Limites de ancho del ala de viga (right beam) (`bf_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `bf_vgder in [bf_vgder_min, bf_vgder_max]; 190.5 mm <= 210 mm <= 311.15 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.2.9 - Limites de peralte de la viga conectada (right beam) (`d_vgder`)

- Ámbito: `BEAM_DER`
- Verificación: `d_vgder in [d_vgder_min, d_vgder_max]; 457.2 mm <= 536 mm <= 914.4 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1`
- Resultado: 🟢 Cumple

### 3.3 Ámbito `END_PLATE_IZQ`

#### Chequeo 3.3.1 - Separación mínima de gage de pernos (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `g_b_vgizq >= 3db; 150 mm >= 76.2 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.2 - Desigualdades explicitas de ancho de placa de extremo (left beam) (`bp_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf; [min,max] = [228.6 mm, 235 mm]`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.3 - Horizontal edge distance from plate edge to bolt line (left beam) (`deh_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `deh_pe_vgizq >= emin; 40 mm >= 31.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.4 - Distancia de borde en de (left beam) (`de_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `de_pe_vgizq >= emin; 62 mm >= 31.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.5 - Maximum edge distance at de (left beam) (`de_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `de_pe_vgizq <= emax_j36; 62 mm <= 150 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.6 - Outside bolt-row distance minimum (left beam) (`pfo_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `pfo_pe_vgizq >= max(pfo_pe_vgizq_min, emin); 50 mm >= 41.27 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.7 - Outside bolt-row distance maximum (left beam) (`pfo_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `pfo_pe_vgizq <= min(pfo_pe_vgizq_max, emax_j36); 50 mm <= 50.8 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.8 - Inside bolt-row distance minimum (left beam) (`pfi_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `pfi_pe_vgizq >= max(pfi_pe_vgizq_min, emin); 50 mm >= 41.27 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.9 - Inside bolt-row distance maximum (left beam) (`pfi_pe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `pfi_pe_vgizq <= min(pfi_pe_vgizq_max, emax_j36); 50 mm <= 50.8 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.10 - Limites de espesor de placa de extremo (left beam) (`tpe_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `tpe_vgizq in [tpe_vgizq_min, tpe_vgizq_max]; 19.05 mm <= 25 mm <= 63.5 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.11 - Horizontal bolt spacing minimum (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `g_b_vgizq >= max(g_b_vgizq_min, 3db_j33); 150 mm >= 127 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.3 (compute_minimum_bolt_spacing_j33)`
- Resultado: 🟢 Cumple

#### Chequeo 3.3.12 - Horizontal bolt spacing maximum (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_IZQ`
- Verificación: `g_b_vgizq <= min(g_b_vgizq_max, smax_j36); 150 mm <= 152.4 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)`
- Resultado: 🟢 Cumple

### 3.4 Ámbito `END_PLATE_DER`

#### Chequeo 3.4.1 - Separación mínima de gage de pernos (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `g_b_vgder >= 3db; 150 mm >= 76.2 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.2 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [228.6 mm, 235 mm]`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.3 - Horizontal edge distance from plate edge to bolt line (right beam) (`deh_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `deh_pe_vgder >= emin; 40 mm >= 31.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.4 - Distancia de borde en de (right beam) (`de_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `de_pe_vgder >= emin; 62 mm >= 31.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.5 - Maximum edge distance at de (right beam) (`de_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `de_pe_vgder <= emax_j36; 62 mm <= 150 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.6 - Outside bolt-row distance minimum (right beam) (`pfo_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `pfo_pe_vgder >= max(pfo_pe_vgder_min, emin); 50 mm >= 41.27 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.7 - Outside bolt-row distance maximum (right beam) (`pfo_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `pfo_pe_vgder <= min(pfo_pe_vgder_max, emax_j36); 50 mm <= 50.8 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.8 - Inside bolt-row distance minimum (right beam) (`pfi_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `pfi_pe_vgder >= max(pfi_pe_vgder_min, emin); 50 mm >= 41.27 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.9 - Inside bolt-row distance maximum (right beam) (`pfi_pe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `pfi_pe_vgder <= min(pfi_pe_vgder_max, emax_j36); 50 mm <= 50.8 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.10 - Limites de espesor de placa de extremo (right beam) (`tpe_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `tpe_vgder in [tpe_vgder_min, tpe_vgder_max]; 19.05 mm <= 25 mm <= 63.5 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.11 - Horizontal bolt spacing minimum (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `g_b_vgder >= max(g_b_vgder_min, 3db_j33); 150 mm >= 127 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.3 (compute_minimum_bolt_spacing_j33)`
- Resultado: 🟢 Cumple

#### Chequeo 3.4.12 - Horizontal bolt spacing maximum (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_DER`
- Verificación: `g_b_vgder <= min(g_b_vgder_max, smax_j36); 150 mm <= 152.4 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)`
- Resultado: 🟢 Cumple

### 3.5 Ámbito `COLUMN`

#### Chequeo 3.5.1 - Familia de perfil de columna permitida para precalificación (`shape_col`)

- Ámbito: `COLUMN`
- Verificación: `shape_col in {W, HEA, HEB, IPE}; 'HEB 500' in {W, HEA, HEB, IPE}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.2 - Peralte máximo del perfil de columna (W36/W920) (`d_col`)

- Ámbito: `COLUMN`
- Verificación: `d_col <= W36/W920; 500 mm <= 920 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.3 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ámbito: `COLUMN`
- Verificación: `bp <= bcf; 230 mm <= 300 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.4 - Condición de conexión columna-losa (`col_losa`)

- Ámbito: `COLUMN`
- Verificación: `col_losa == isolated; 'isolated' == 'isolated'`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 2.3.4 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.5 - Proyeccion de columna mínima por encima de las vigas (`St_col`)

- Ámbito: `COLUMN`
- Verificación: `St_col >= pfo_pe_vgder + pb_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq + 12.5 mm; 2500.000 mm >= 219.500 mm; 2500.000 mm >= 219.500 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3.1 (criterio de despeje superior de columna)`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.6 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ámbito: `COLUMN`
- Verificación: `lambda_f_col <= lambda_f_limit; 5.36 adim <= 6.89 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w / AISC 358-22w Sección 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.7 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ámbito: `COLUMN`
- Verificación: `lambda_w_col <= lambda_w_limit; 26.9 adim <= 49.49 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w / AISC 358-22w Sección 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.8 - Espesor individual minimo del alma de columna (`tw_col`)

- Ámbito: `COLUMN`
- Verificación: `tw_col >= (dz_dp_col + wz_dp_col)/90; si use_weld_7_col=false: wz_dp_col=d_col-2*tf_col, dz_dp_col=max{d_lado-2*tf_lado}; si use_weld_7_col=true: h_w7_col=max{d_lado-2*tf_lado}/(nfilas_w7_col + 1), b_w7_col=b_dp_col/(ncolumna_w7_col + 1), dz_dp_col=h_w7_col, wz_dp_col=b_w7_col; 14.5 mm >= 2.84 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.9 - Chequeo adicional con soldadura #7 habilitada (`t_dp_col + tw_col`)

- Ámbito: `COLUMN`
- Verificación: `t_dp_col + tw_col >= (d_col - 2*tf_col + max{d_lado-2*tf_lado})/90; 26.5 mm >= 10.5 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.10 - Outside adjusted edge distance minimum (right beam) (`pso_pe_vgder`)

- Ámbito: `COLUMN`
- Verificación: `pso_pe_vgder >= emin; 50.7 mm >= 31.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.11 - Outside adjusted edge distance maximum (right beam) (`pso_pe_vgder`)

- Ámbito: `COLUMN`
- Verificación: `pso_pe_vgder <= emax_j36; 50.7 mm <= 150 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.12 - Outside adjusted edge distance minimum (left beam) (`pso_pe_vgizq`)

- Ámbito: `COLUMN`
- Verificación: `pso_pe_vgizq >= emin; 50.7 mm >= 31.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 3.5.13 - Outside adjusted edge distance maximum (left beam) (`pso_pe_vgizq`)

- Ámbito: `COLUMN`
- Verificación: `pso_pe_vgizq <= emax_j36; 50.7 mm <= 150 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 J3.6`
- Resultado: 🟢 Cumple

### 3.6 Ámbito `END_PLATE_STIFFENER_DER`

#### Chequeo 3.6.1 - Altura del rigidizador derivada de la geometría de la placa de extremo (right beam) (`h_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificación: `h_pest_vgder = pfo_pe_vgder + pb_pe_vgder + de_pe_vgder; 207.000 mm = 50.000 mm + 95.000 mm + 62.000 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.2 - Espesor minimo requerido del rigidizador (right beam) (`t_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificación: `t_pest_vgder >= tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 16 mm >= 10.9 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.3 - Limite de pandeo local ancho-espesor del rigidizador (right beam) (`h_pest_vgder/t_pest_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificación: `h_pest_vgder/t_pest_vgder <= 0.56*sqrt(E_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 12.94 adim <= 13.48 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 3.6.4 - Despeje del gage de pernos con espesor del rigidizador (right beam) (`g_b_vgder`)

- Ámbito: `END_PLATE_STIFFENER_DER`
- Verificación: `g_b_vgder >= 2emin + t_pest_vgder; 150 mm >= 79.5 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 3.7 Ámbito `END_PLATE_STIFFENER_IZQ`

#### Chequeo 3.7.1 - Altura del rigidizador derivada de la geometría de la placa de extremo (left beam) (`h_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificación: `h_pest_vgizq = pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq; 207.000 mm = 50.000 mm + 95.000 mm + 62.000 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.2 - Espesor minimo requerido del rigidizador (left beam) (`t_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificación: `t_pest_vgizq >= tw_vgizq*(Fy_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 16 mm >= 10.9 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.3 - Limite de pandeo local ancho-espesor del rigidizador (left beam) (`h_pest_vgizq/t_pest_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificación: `h_pest_vgizq/t_pest_vgizq <= 0.56*sqrt(E_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 12.94 adim <= 13.48 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 3.7.4 - Despeje del gage de pernos con espesor del rigidizador (left beam) (`g_b_vgizq`)

- Ámbito: `END_PLATE_STIFFENER_IZQ`
- Verificación: `g_b_vgizq >= 2emin + t_pest_vgizq; 150 mm >= 79.5 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 3.8 platina de continuidad

#### Chequeo 3.8.1 - Ancho máximo de platina de continuidad (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `b1_pc_col <= (bf_col - tw_col - n_dp_col*t_dp_col)/2; 130 mm <= 130.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 J10.8 / SDH 4th ed. 2024`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.2 - Ancho minimo de platina de continuidad (viga der) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `b1_pc_col >= bf_vgder/2 + 0.5*tw_col + 0.5*n_dp_col*t_dp_col; 130 mm >= 124.25 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 J10.8`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.3 - Ancho minimo alterno de platina de continuidad (viga der) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `b1_pc_col >= (bf_vgder - tw_col)/2; 130 mm >= 97.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: SDH 4th ed. 2024`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.4 - Ancho minimo de platina de continuidad (viga izq) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `b1_pc_col >= bf_vgizq/2 + 0.5*tw_col + 0.5*n_dp_col*t_dp_col; 130 mm >= 124.25 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 J10.8`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.5 - Ancho minimo alterno de platina de continuidad (viga izq) (`b1_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `b1_pc_col >= (bf_vgizq - tw_col)/2; 130 mm >= 97.75 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: SDH 4th ed. 2024`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.6 - Espesor minimo de platina de continuidad (viga izq) (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `t_pc_col >= min{tf_vgizq/2, tf_vgder/2, b1_pc_col/16, (b1_pc_col/0.56)*sqrt(Fy_pc_col/E_pc_col)}; 16 mm >= 8.12 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 J10.8`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.7 - Espesor minimo global de platina de continuidad (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `t_pc_col >= (b1_pc_col/0.45)*sqrt(Fy_pc_col/E_pc_col); 16 mm >= 12 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Requisito de proyecto (si usar_pc_col=true)`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.8 - Limite ancho/espesor de platina de continuidad (b/t) (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `t_pc_col >= (max(b1_pc_col, b2_pc_col)/0.56)*sqrt(Ry_pc_col*Fy_pc_col/E_pc_col); 16 mm >= 10.11 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22 Eq. (E3-9)`
- Resultado: 🟢 Cumple

#### Chequeo 3.8.9 - Espesor minimo de platina de continuidad (conexión a dos lados, 75% del ala mas gruesa) (`t_pc_col`)

- Ámbito: `CONTINUITY_PLATE_COL`
- Verificación: `t_pc_col >= 0.75*max(tf_vgizq, tf_vgder); 16 mm >= 13.05 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6f(1)(b)`
- Resultado: 🟢 Cumple

### 3.9 Ámbito `DOUBLER_PLATE_COL`

#### Chequeo 3.9.1 - Espesor minimo absoluto de platina de enchape para ductilidad moderada/alta (`t_dp_col`)

- Ámbito: `DOUBLER_PLATE_COL`
- Verificación: `t_dp_col >= 6.0 mm; 12 mm >= 6 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.2 - Espesor individual minimo de platina de enchape del alma (`t_dp_col`)

- Ámbito: `DOUBLER_PLATE_COL`
- Verificación: `t_dp_col >= (dz_dp_col + wz_dp_col)/90; si use_weld_7_col=false: wz_dp_col=d_col-2*tf_col, dz_dp_col=max{d_lado-2*tf_lado}; si use_weld_7_col=true: h_w7_col=max{d_lado-2*tf_lado}/(nfilas_w7_col + 1), b_w7_col=b_dp_col/(ncolumna_w7_col + 1), dz_dp_col=h_w7_col, wz_dp_col=b_w7_col; 12 mm >= 2.84 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.3 - Espesor minimo adicional de platina de enchape del alma (`t_dp_col`)

- Ámbito: `DOUBLER_PLATE_COL`
- Verificación: `t_dp_col >= max{dz_dp_col, wz_dp_col}*sqrt(Fy_dp_col/E_dp_col)/2.42; 12 mm >= 2.23 mm`
- Cláusula: `Documento: Design-guide-13--wide-flange-column-stiffening-at-moment-connections | Sección: DG13 Chapter 4`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.4 - Chequeo adicional con soldadura #7 habilitada (`t_dp_col + tw_col`)

- Ámbito: `DOUBLER_PLATE_COL`
- Verificación: `t_dp_col + tw_col >= (d_col - 2*tf_col + max{d_lado-2*tf_lado})/90; 26.5 mm >= 10.5 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

#### Chequeo 3.9.5 - Espesor minimo con soldadura #7 habilitada (ductilidad moderada/alta) (`t_dp_col`)

- Ámbito: `DOUBLER_PLATE_COL`
- Verificación: `t_dp_col >= (d_col - 2*kdet_col)*sqrt(fy_dp_col)/1136.78; 12 mm >= 6.37 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: design-guide-13--wide-flange-column-stiffening-at-moment-connections`
- Resultado: 🟢 Cumple

### 3.10 Ámbito `BOLTS_DER`

#### Chequeo 3.10.1 - El tipo de apriete del perno debe ser una categoria reconocida (right beam) (`tight_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificación: `tight_bolt_vgder in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.2 - Los pernos deben estar pretensionados salvo que una conexión especifica permita lo contrario (right beam) (`tight_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificación: `tight_bolt_vgder == pretensioned; 'pretensioned' == 'pretensioned'`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.10.3 - La norma de fabricación de pernos debe ser una designacion ASTM de alta resistencia permitida (right beam) (`std_bolt_vgder`)

- Ámbito: `BOLTS_DER`
- Verificación: `std_bolt_vgder in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### 3.11 Ámbito `BOLTS_IZQ`

#### Chequeo 3.11.1 - El tipo de apriete del perno debe ser una categoria reconocida (left beam) (`tight_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificación: `tight_bolt_vgizq in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.2 - Los pernos deben estar pretensionados salvo que una conexión especifica permita lo contrario (left beam) (`tight_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificación: `tight_bolt_vgizq == pretensioned; 'pretensioned' == 'pretensioned'`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 3.11.3 - La norma de fabricación de pernos debe ser una designacion ASTM de alta resistencia permitida (left beam) (`std_bolt_vgizq`)

- Ámbito: `BOLTS_IZQ`
- Verificación: `std_bolt_vgizq in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### 3.12 Ámbito `WELD_1_VGDER`

#### Chequeo 3.12.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w1_vgder`)

- Ámbito: `WELD_1_VGDER`
- Verificación: `si t_pest_vgder > 10.000 mm: tipo_w1_vgder == cjp; t_pest_vgder = 16.000 mm; tipo_w1_vgder = cjp`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.13 Ámbito `WELD_1_VGIZQ`

#### Chequeo 3.13.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w1_vgizq`)

- Ámbito: `WELD_1_VGIZQ`
- Verificación: `si t_pest_vgizq > 10.000 mm: tipo_w1_vgizq == cjp; t_pest_vgizq = 16.000 mm; tipo_w1_vgizq = cjp`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.14 Ámbito `WELD_2_VGDER`

#### Chequeo 3.14.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w2_vgder`)

- Ámbito: `WELD_2_VGDER`
- Verificación: `si t_pest_vgder > 10.000 mm: tipo_w2_vgder == cjp; t_pest_vgder = 16.000 mm; tipo_w2_vgder = cjp`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.15 Ámbito `WELD_2_VGIZQ`

#### Chequeo 3.15.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w2_vgizq`)

- Ámbito: `WELD_2_VGIZQ`
- Verificación: `si t_pest_vgizq > 10.000 mm: tipo_w2_vgizq == cjp; t_pest_vgizq = 16.000 mm; tipo_w2_vgizq = cjp`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 3.16 Ámbito `WELD_3_VGDER`

#### Chequeo 3.16.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (right beam) (`weld_ep_web_vgder`)

- Ámbito: `WELD_3_VGDER`
- Verificación: `weld_ep_web_vgder in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7`
- Resultado: 🟢 Cumple

### 3.17 Ámbito `WELD_3_VGIZQ`

#### Chequeo 3.17.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (left beam) (`weld_ep_web_vgizq`)

- Ámbito: `WELD_3_VGIZQ`
- Verificación: `weld_ep_web_vgizq in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7`
- Resultado: 🟢 Cumple

### 3.18 Ámbito `WELD_4_VGDER`

#### Chequeo 3.18.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha) (`tipo_w4_vgder`)

- Ámbito: `WELD_4_VGDER`
- Verificación: `si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 8 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 8.000 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7`
- Resultado: 🟢 Cumple

### 3.19 Ámbito `WELD_4_VGIZQ`

#### Chequeo 3.19.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda) (`tipo_w4_vgizq`)

- Ámbito: `WELD_4_VGIZQ`
- Verificación: `si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 8 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 8.000 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7`
- Resultado: 🟢 Cumple

### 3.20 Ámbito `WELD_5_COL`

#### Chequeo 3.20.1 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificación: `tipo_w5_col in {fillet, cjp}; 'cjp' in {fillet, cjp}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 3.20.2 - Tamano minimo de soldadura #5 cuando tipo_w5_col es fillet (`tipo_w5_col`)

- Ámbito: `WELD_5_COL`
- Verificación: `tipo_w5_col='cjp' => cumple; t_pc_col=16 mm; tipo_w5_col='cjp'`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

### 3.21 Ámbito `WELD_6_COL`

#### Chequeo 3.21.1 - Tipo de soldadura #6 permitido (`tipo_w6_col`)

- Ámbito: `WELD_6_COL`
- Verificación: `tipo_w6_col in {cjp, pjp, fillet}; 'cjp' in {cjp, pjp, fillet}`
- Cláusula: `Documento: AISC 358-22 | Sección: Sección 6.7`
- Resultado: 🟢 Cumple

### 3.22 Ámbito `WELD_7_COL`

#### Chequeo 3.22.1 - Malla mínima de soldadura #7 (`(nfilas_w7_col)*(ncolumna_w7_col)`)

- Ámbito: `WELD_7_COL`
- Verificación: `(nfilas_w7_col)*(ncolumna_w7_col) >= 4; 6 adim >= 4 adim`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

#### Chequeo 3.22.2 - Diámetro minimo de hueco para soldadura plug (#7, columna) (`d_hole_w7_col`)

- Ámbito: `WELD_7_COL`
- Verificación: `d_hole_w7_col >= redondeo_par(t_part_w7_col + 8 mm); 31 mm >= 24 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 Sección J2.3b(a)`
- Resultado: 🟢 Cumple

#### Chequeo 3.22.3 - Diámetro máximo de hueco para soldadura plug (#7, columna) (`d_hole_w7_col`)

- Ámbito: `WELD_7_COL`
- Verificación: `d_hole_w7_col <= max{d_min+3 mm, 2.25*w_w7_col}; 31 mm <= 36 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 Sección J2.3b(a)`
- Resultado: 🟢 Cumple

#### Chequeo 3.22.4 - Separación mínima centro a centro para soldadura plug (#7, columna) (`min(b_w7_col, h_w7_col)`)

- Ámbito: `WELD_7_COL`
- Verificación: `b_w7_col >= 4*d_hole_w7_col y h_w7_col >= 4*d_hole_w7_col; b_w7_col=130.000 mm, h_w7_col=125.300 mm, s_min=124.000 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 Sección J2.3b(b)`
- Resultado: 🟢 Cumple

#### Chequeo 3.22.5 - Espesor de soldadura plug vs espesor de material (#7, columna) (`w_w7_col`)

- Ámbito: `WELD_7_COL`
- Verificación: `w_w7_col == t_part_w7_col; w_w7_col=16.000 mm, t_part_w7_col=16.000 mm, requerido=16.000 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 360-22 Sección J2.3b(h)`
- Resultado: 🟢 Cumple

### 3.23 Ámbito `WELD_8_COL`

#### Chequeo 3.23.1 - Clasificación de contacto entre platina de enchape y alma de columna segun gap_dp_col (`gap_dp_col`)

- Ámbito: `WELD_8_COL`
- Verificación: `si gap_dp_col <= 2.0 mm => en_contacto_con_alma; si gap_dp_col > 2.0 mm => sin_contacto_con_alma; gap_dp_col = 0.000 mm, estado = en_contacto_con_alma`
- Cláusula: `Documento: AISC 358-22 | Sección: design-guide-13--wide-flange-column-stiffening-at-moment-connections`
- Resultado: 🟢 Cumple

#### Chequeo 3.23.2 - Tipo de soldadura #8 permitido (`tipo_w8_col`)

- Ámbito: `WELD_8_COL`
- Verificación: `tipo_w8_col in {fillet, pjp}; 'pjp' in {fillet, pjp}`
- Cláusula: `Documento: AISC 358-22 | Sección: AISC 341-22w E3.6e.3`
- Resultado: 🟢 Cumple

#### Chequeo 3.23.3 - Determinacion automatica de Encr para soldadura #8 (`Encr_w8_col`)

- Ámbito: `WELD_8_COL`
- Verificación: `Encr_w8_col calculado correctamente: 7.900 mm; fuente=AISC 16th Fig 10-3, rango 22.2 - 31.8 mm`
- Cláusula: `Documento: AISC 358-22 | Sección: Steel Construction Manual AISC 16th Edition 2023 Figure 10-3`
- Resultado: 🟢 Cumple

### 3.24 Ámbito `WELD_9_COL`

### 3.25 Resumen de chequeos por ámbito

- 🟢 `3.1` `BEAM_IZQ`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.2` `BEAM_DER`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.3` `END_PLATE_IZQ`: total=12, cumple=12, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.4` `END_PLATE_DER`: total=12, cumple=12, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.5` `COLUMN`: total=13, cumple=13, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.6` `END_PLATE_STIFFENER_DER`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.7` `END_PLATE_STIFFENER_IZQ`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.8` `CONTINUITY_PLATE_COL`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.9` `DOUBLER_PLATE_COL`: total=5, cumple=5, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.10` `BOLTS_DER`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.11` `BOLTS_IZQ`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.12` `WELD_1_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.13` `WELD_1_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.14` `WELD_2_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.15` `WELD_2_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.16` `WELD_3_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.17` `WELD_3_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.18` `WELD_4_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.19` `WELD_4_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.20` `WELD_5_COL`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.21` `WELD_6_COL`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.22` `WELD_7_COL`: total=5, cumple=5, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.23` `WELD_8_COL`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `3.24` `WELD_9_COL`: total=0, cumple=0, no_cumple=0, numerales_no_cumplen=ninguno

## Paso 4 - Momento probable máximo en rótula plástica (Mpr)

Cálculo de momento probable por lado usando `Mpr = Cpr * Ry * Fy * Ze` (Ze = Zx del catalogo).

### 4.1 Cálculo de Mpr para viga izquierda

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuación: `Mpr_vgizq = Cpr_vgizq * Ry * Fy * Ze_vgizq`
- Fy_vgizq: `345 MPa`
- Ry: `1.1`
- Ze_vgizq (catalogo): `2620000 mm3`
- Demanda de ductilidad_vgizq: `high`
- Cpr_vgizq: `1.15`
- Mpr_vgizq: `1143.43 kN-m`

### 4.2 Cálculo de Mpr para viga derecha

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuación: `Mpr_vgder = Cpr_vgder * Ry * Fy * Ze_vgder`
- Fy_vgder: `345 MPa`
- Ry: `1.1`
- Ze_vgder (catalogo): `2620000 mm3`
- Demanda de ductilidad_vgder: `high`
- Cpr_vgder: `1.15`
- Mpr_vgder: `1143.43 kN-m`

## Paso 5 - Distancia de rótula plástica desde la cara de la columna (Sh)

### 5.1 Cálculo de Sh para viga izquierda

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuación: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`
- d_vgizq: `536 mm`
- bf_vgizq: `210 mm`
- Sh_vgizq: `385 mm`

### 5.2 Cálculo de Sh para viga derecha

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuación: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`
- d_vgder: `536 mm`
- bf_vgder: `210 mm`
- Sh_vgder: `385 mm`

## Paso 6 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Cálculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.

### 6.1 Cálculo de cortante probable para viga izquierda

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuación: `Vh_vgizq_max = 2*Mpr_vgizq/Llb_vgizq + Vg_vgizq; Vh_vgizq_min = 2*Mpr_vgizq/Llb_vgizq - Vg_vgizq`
- Mpr_vgizq: `1143.43 kN-m`
- Llb_vgizq: `7500 mm`
- Vg_vgizq: `98.2 kN`
- Vh_vgizq_max: `403.12 kN`
- Vh_vgizq_min: `206.72 kN`
- Vhmax_vgizq adoptado: `403.12 kN`

### 6.2 Cálculo de cortante probable para viga derecha

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuación: `Vh_vgder_max = 2*Mpr_vgder/Llb_vgder + Vg_vgder; Vh_vgder_min = 2*Mpr_vgder/Llb_vgder - Vg_vgder`
- Mpr_vgder: `1143.43 kN-m`
- Llb_vgder: `7500 mm`
- Vg_vgder: `96.64 kN`
- Vh_vgder_max: `401.56 kN`
- Vh_vgder_min: `208.28 kN`
- Vhmax_vgder adoptado: `401.56 kN`

## Paso 7 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Cálculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.

### 7.1 Cálculo de momento probable en cara de columna para viga izquierda

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuación: `Mf_vgizq_max = Mpr_vgizq + Vh_vgizq_max*Sh_vgizq; Mf_vgizq_min = Mpr_vgizq + Vh_vgizq_min*Sh_vgizq`
- Mpr_vgizq: `1143.43 kN-m`
- Sh_vgizq: `385 mm`
- Mf_vgizq_max: `1298.63 kN-m`
- Mf_vgizq_min: `1223.02 kN-m`

### 7.2 Cálculo de momento probable en cara de columna para viga derecha

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuación: `Mf_vgder_max = Mpr_vgder + Vh_vgder_max*Sh_vgder; Mf_vgder_min = Mpr_vgder + Vh_vgder_min*Sh_vgder`
- Mpr_vgder: `1143.43 kN-m`
- Sh_vgder: `385 mm`
- Mf_vgder_max: `1298.03 kN-m`
- Mf_vgder_min: `1223.62 kN-m`

## Paso 8 - Revisión De Resistencia Pernos (vg_izq)

### 8.1 Revisión de capacidad a tracción (vg_izq)

#### 8.1.1 Estado #1: Rotura en el perno (vg_izq)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuación: `Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq + h3_pe_vgizq + h4_pe_vgizq)); phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1298.63 kN-m`
- h1_pe_vgizq: `672.3 mm`
- h2_pe_vgizq: `577.3 mm`
- h3_pe_vgizq: `459.9 mm`
- h4_pe_vgizq: `364.9 mm`
- A_b_vgizq: `506.71 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_p+_vgizq: `313.01 kN`
- phi*Rn_b_p+_vgizq: `355.71 kN`
- DCR_b_p+_vgizq: `0.88`
- Resultado: `🟢 Cumple`

### 8.2 Revisión de capacidad a cortante (vg_izq)

#### 8.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuación: `Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgizq_critico: `403.12 kN`
- n_b_vgizq: `8`
- A_b_vgizq: `506.71 mm2`
- Fnv_b_vgizq: `470 MPa`
- thread_b_vgizq: `N`
- Ru_b_v2_vgizq: `50.39 kN`
- phi*Rn_b_v2_vgizq: `214.34 kN`
- DCR_b_v2_vgizq: `0.24`
- Resultado: `🟢 Cumple`

## Paso 9 - Revisión De Resistencia Pernos (vg_der)

### 9.1 Revisión de capacidad a tracción (vg_der)

#### 9.1.1 Estado #1: Rotura en el perno (vg_der)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuación: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder + h3_pe_vgder + h4_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgder_critico: `1298.03 kN-m`
- h1_pe_vgder: `672.3 mm`
- h2_pe_vgder: `577.3 mm`
- h3_pe_vgder: `459.9 mm`
- h4_pe_vgder: `364.9 mm`
- A_b_vgder: `506.71 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_p+_vgder: `312.87 kN`
- phi*Rn_b_p+_vgder: `355.71 kN`
- DCR_b_p+_vgder: `0.88`
- Resultado: `🟢 Cumple`

### 9.2 Revisión de capacidad a cortante (vg_der)

#### 9.2.1 ELR #2: Rotura por cortante en el perno (vg_der)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuación: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgder_critico: `401.56 kN`
- n_b_vgder: `8`
- A_b_vgder: `506.71 mm2`
- Fnv_b_vgder: `470 MPa`
- thread_b_vgder: `N`
- Ru_b_v2_vgder: `50.19 kN`
- phi*Rn_b_v2_vgder: `214.34 kN`
- DCR_b_v2_vgder: `0.23`
- Resultado: `🟢 Cumple`

## Paso 10 - Revisión de resistencia platina extremo (vg_izq)

### 10.1. Revisión de capacidad a flexión (vg_izq)

#### 10.1.1. ELR #1: Fluencia (vg_izq)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuación: `Ru_pe_m3_vgizq = Mf_vgizq_critico; phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq (AISC 358-22 Eq. 6.7-8)`
- phi usado: `1`
- Mf_vgizq_critico: `1298.63 kN-m`
- tpe_vgizq: `25 mm`
- Fyp_pe_vgizq: `345 MPa`
- Yp_pe_vgizq: `6683.95 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgizq: `92.87 mm`
- pfi_pe_vgizq_entrada: `50 mm`
- pfi_pe_vgizq_efectivo: `50 mm`
- Ru_pe_m3_vgizq: `1298.63 kN-m`
- phi*Rn_pe_m3_vgizq: `1441.23 kN-m`
- DCR_pe_m3_vgizq: `0.9`
- Resultado: `🟢 Cumple`

### 10.3. Revisión de capacidad a cortante paralelo al plano de la platina (vg_izq)

#### 10.3.1. ELR #1: Desgarramiento en la perforación del perno (vg_izq)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuación: `lc_pe_vgizq = min(pb_pe_vgizq - dh_pe_vgizq, pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq); Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 1.2 * lc_pe_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `403.12 kN`
- n_b_vgizq: `8`
- pb_pe_vgizq: `95 mm`
- pfo_pe_vgizq: `50 mm`
- pfi_pe_vgizq: `50 mm`
- tf_vgizq: `17.4 mm`
- dh_pe_vgizq: `28.57 mm`
- lc_pe_vgizq: `66.42 mm`
- tpe_vgizq: `25 mm`
- Fup_pe_vgizq: `450 MPa`
- Ru_pe_v2_vgizq: `50.39 kN`
- phi*Rn_pe_v2_vgizq: `807.06 kN`
- DCR_pe_v2_vgizq: `0.06`
- Resultado: `🟢 Cumple`

#### 10.3.2. ELR #2: Aplastamiento en la perforación del perno (vg_izq)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuación: `Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 2.4 * d_b_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `403.12 kN`
- n_b_vgizq: `8`
- tpe_vgizq: `25 mm`
- Fup_pe_vgizq: `450 MPa`
- d_b_vgizq: `25.4 mm`
- Ru_pe_v2_vgizq: `50.39 kN`
- phi*Rn_pe_v2_vgizq: `617.22 kN`
- DCR_pe_v2_vgizq: `0.08`
- Resultado: `🟢 Cumple`

## Paso 11 - Revisión de resistencia platina extremo (vg_der)

### 11.1. Revisión de capacidad a flexión (vg_der)

#### 11.1.1. ELR #1: Fluencia (vg_der)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuación: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`
- phi usado: `1`
- Mf_vgder_critico: `1298.03 kN-m`
- tpe_vgder: `25 mm`
- Fyp_pe_vgder: `345 MPa`
- Yp_pe_vgder: `6683.95 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgder: `92.87 mm`
- pfi_pe_vgder_entrada: `50 mm`
- pfi_pe_vgder_efectivo: `50 mm`
- Ru_pe_m3_vgder: `1298.03 kN-m`
- phi*Rn_pe_m3_vgder: `1441.23 kN-m`
- DCR_pe_m3_vgder: `0.9`
- Resultado: `🟢 Cumple`

### 11.3. Revisión de capacidad a cortante paralelo al plano de la platina (vg_der)

#### 11.3.1. ELR #1: Desgarramiento en la perforación del perno (vg_der)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuación: `lc_pe_vgder = min(pb_pe_vgder - dh_pe_vgder, pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder); Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `401.56 kN`
- n_b_vgder: `8`
- pb_pe_vgder: `95 mm`
- pfo_pe_vgder: `50 mm`
- pfi_pe_vgder: `50 mm`
- tf_vgder: `17.4 mm`
- dh_pe_vgder: `28.57 mm`
- lc_pe_vgder: `66.42 mm`
- tpe_vgder: `25 mm`
- Fup_pe_vgder: `450 MPa`
- Ru_pe_v2_vgder: `50.19 kN`
- phi*Rn_pe_v2_vgder: `807.06 kN`
- DCR_pe_v2_vgder: `0.06`
- Resultado: `🟢 Cumple`

#### 11.3.2. ELR #2: Aplastamiento en la perforación del perno (vg_der)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuación: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `401.56 kN`
- n_b_vgder: `8`
- tpe_vgder: `25 mm`
- Fup_pe_vgder: `450 MPa`
- d_b_vgder: `25.4 mm`
- Ru_pe_v2_vgder: `50.19 kN`
- phi*Rn_pe_v2_vgder: `617.22 kN`
- DCR_pe_v2_vgder: `0.08`
- Resultado: `🟢 Cumple`

## Paso 12 - Revisión de Resistencia soldadura #1 (platina extremo vg_izq - rigidizador vg_izq)

### 12.1. Revisión de capacidad a tracción (vg_izq)

#### 12.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 + AISC 360-22 J2.4`
- Ecuación: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w1_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 13 - Revisión de Resistencia soldadura #1 (platina extremo vg_der - rigidizador vg_der)

### 13.1. Revisión de capacidad a tracción (vg_der)

#### 13.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 + AISC 360-22 J2.4`
- Ecuación: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w1_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 14 - Revisión de Resistencia soldadura #2 (viga vg_izq - rigidizador vg_izq)

### 14.1. Revisión de capacidad a cortante (vg_izq)

#### 14.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 + AISC 360-22 J2.4`
- Ecuación: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w2_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 15 - Revisión de Resistencia soldadura #2 (viga vg_der - rigidizador vg_der)

### 15.1. Revisión de capacidad a cortante (vg_der)

#### 15.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.1 + AISC 360-22 J2.4`
- Ecuación: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w2_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 16 - Revisión de Resistencia soldadura #4 (ala vg_izq - platina extremo vg_izq)

### 16.1. Revisión de capacidad a tracción (vg_izq)

#### 16.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 6.7.1 + AISC 360-22 J2.4`
- Ecuación: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w4_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 17 - Revisión de Resistencia soldadura #4 (ala vg_der - platina extremo vg_der)

### 17.1. Revisión de capacidad a tracción (vg_der)

#### 17.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 6.7.1 + AISC 360-22 J2.4`
- Ecuación: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w4_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 18 - Revisión de resistencia de la viga (vg_izq)

### 18.1. Revisión de capacidad a cortante (vg_izq)

#### 18.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_izq)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuación: `Ru_v2_vgizq = Vh_vgizq_max; Rn_v2_vgizq = 0.6 * Fy_vgizq * tw_vgizq * d_vgizq * Cv1; phi*Rn_v2_vgizq = phi * Rn_v2_vgizq; DCR_v2_vgizq = Ru_v2_vgizq / phi*Rn_v2_vgizq (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgizq_max: `403.12 kN`
- Fy_vgizq: `345 MPa`
- tw_vgizq: `10.9 mm`
- d_vgizq: `536 mm`
- kdes_vgizq: `30.2 mm`
- E_vgizq: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgizq/tw_vgizq: `43.63`
- h_vgizq: `475.6 mm`
- Ru_v2_vgizq: `403.12 kN`
- phi*Rn_v2_vgizq: `1209.38 kN`
- DCR_v2_vgizq: `0.33`
- Resultado: `🟢 Cumple`

## Paso 19 - Revisión de resistencia de la viga (vg_der)

### 19.1. Revisión de capacidad a cortante (vg_der)

#### 19.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_der)

- Cláusula: `Documento: AISC 360-22 | Sección: Capitulo 6 / Sección 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuación: `Ru_v2_vgder = Vh_vgder_max; Rn_v2_vgder = 0.6 * Fy_vgder * tw_vgder * d_vgder * Cv1; phi*Rn_v2_vgder = phi * Rn_v2_vgder; DCR_v2_vgder = Ru_v2_vgder / phi*Rn_v2_vgder (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgder_max: `401.56 kN`
- Fy_vgder: `345 MPa`
- tw_vgder: `10.9 mm`
- d_vgder: `536 mm`
- kdes_vgder: `30.2 mm`
- E_vgder: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgder/tw_vgder: `43.63`
- h_vgder: `475.6 mm`
- Ru_v2_vgder: `401.56 kN`
- phi*Rn_v2_vgder: `1209.38 kN`
- DCR_v2_vgder: `0.33`
- Resultado: `🟢 Cumple`

## Paso 20 - Revisión de Resistencia soldadura #3 (viga alma vg_izq - platina extremo vg_izq)

### 20.1 Revisión capacidad a tracción (vg_izq)

#### 20.1.1 ELR #1: Rotura de soldadura (vg_izq)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7 + AISC 360-22 J2.4`
- Ecuación: `Fillet: Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq; hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm; phi*Rn_w3_p+_vgizq = phi * kds_w3_vgizq * nl_w3_vgizq * 0.6 * Fexx_w3_vgizq * 0.707 * hwef_w3_vgizq * t_w3_vgizq; DCR_w3_p+_vgizq = Ru_w3_p+_vgizq / phi*Rn_w3_p+_vgizq`
- tipo_w3_vgizq: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 21 - Revisión de Resistencia soldadura #3 (viga alma vg_der - platina extremo vg_der)

### 21.1 Revisión capacidad a tracción (vg_der)

#### 21.1.1 ELR #1: Rotura de soldadura (vg_der)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7 + AISC 360-22 J2.4`
- Ecuación: `Fillet: Ru_w3_p+_vgder = Fy_vgder * tw_vgder * hwef_w3_vgder; hwef_w3_vgder = pfi_pe_vgder + pb_pe_vgder + 150 mm; phi*Rn_w3_p+_vgder = phi * kds_w3_vgder * nl_w3_vgder * 0.6 * Fexx_w3_vgder * 0.707 * hwef_w3_vgder * t_w3_vgder; DCR_w3_p+_vgder = Ru_w3_p+_vgder / phi*Rn_w3_p+_vgder`
- tipo_w3_vgder: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 22 - Revisión de resistencia de la aleta de la columna

### 22.1. Revisión de capacidad a flexión (vg_izq)

#### 22.1.1. ELR #1: Flexión local de la aleta (LFB)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-13)`
- Ecuación: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); phi*Rn_cf_v2_col_vgizq = phi_ductil * ((tf_col^2 * Fy_col * Y_cs)/(1.11 * (d_vgizq - tf_vgizq))); DCR_cf_v2_col_vgizq = Ru_cf_v2_col_vgizq / phi*Rn_cf_v2_col_vgizq`
- phi usado: `1`
- Mf_vgizq_critico: `1298.63 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- z_vgizq = d_vgizq - tf_vgizq: `518.6 mm`
- tf_col: `28 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `8167.22 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuación s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgizq)`
- s_col: `106.07 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgizq: `2504.11 kN`
- phi*Rn_cf_v2_col_vgizq: `3837.55 kN`
- DCR_cf_v2_col_vgizq: `0.65`
- Resultado: `🟢 Cumple`

Donde:

- Ecuación Y_cs: `Y_cs = bcf/2*[h1*(1/s) + h2*(1/pso) + h3*(1/psi) + h4*(1/s)] + (2/g)*[h1*(s + pb/4) + h2*(pso + 3pb/4) + h3*(psi + pb/4) + h4*(s + 3pb/4) + pb^2/2] + g`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

### 22.2. Revisión de capacidad a flexión (vg_der)

#### 22.2.1. ELR #1: Flexión local de la aleta (LFB)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-13)`
- Ecuación: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); phi*Rn_cf_v2_col_vgder = phi_ductil * ((tf_col^2 * Fy_col * Y_cs)/(1.11 * (d_vgder - tf_vgder))); DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado: `1`
- Mf_vgder_critico: `1298.03 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- z_vgder = d_vgder - tf_vgder: `518.6 mm`
- tf_col: `28 mm`
- Fy_col: `345 MPa`
- Y_cs usado: `8167.22 mm`
- Tabla Y_cs aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_cs: `Case 1 (psi <= s)`
- Ecuación s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgder)`
- s_col: `106.07 mm`
- usar_pc_col: `hay platinas de continuidad`
- Ru_cf_v2_col_vgder: `2502.95 kN`
- phi*Rn_cf_v2_col_vgder: `3837.55 kN`
- DCR_cf_v2_col_vgder: `0.65`
- Resultado: `🟢 Cumple`

Donde:

- Ecuación Y_cs: `Y_cs = bcf/2*[h1*(1/s) + h2*(1/pso) + h3*(1/psi) + h4*(1/s)] + (2/g)*[h1*(s + pb/4) + h2*(pso + 3pb/4) + h3*(psi + pb/4) + h4*(s + 3pb/4) + pb^2/2] + g`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

## Paso 23 - Revisión de resistencia del alma de la columna

### 23.1. Revisión de capacidad a tracción (vg_izq)

#### 23.1.1. ELR #1: Fluencia local del alma (WLY)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-17)`
- Ecuación: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado (phi_ductil): `1`
- Mf_vgizq_critico: `1298.63 kN-m`
- St_col: `2500 mm`
- d_col: `500 mm`
- Ct_col: `1`
- kc_col: `55 mm`
- lb_col: `75.4 mm`
- Ecuación lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- tw_col: `14.5 mm`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- tpe_vgizq: `25 mm`
- t_w4_1_vgizq: `8 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `8 mm`
- Ecuación 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `2028.01 kN`
- phi*Rn_cw_v2_col_vgizq: `2028.01 kN`
- DCR_cw_v2_col_vgizq: `1`
- Resultado: `🟢 Cumple`

### 23.2. Revisión de capacidad a compresión (vg_izq)

#### 23.2.1. ELR #1: Arrugamiento local del alma (WLC)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuación: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; Rn_cw_v2_col_vgizq = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_cw_v2_col_vgizq; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado: `0.75`
- Mf_vgizq_critico: `1298.63 kN-m`
- St_col: `2500 mm`
- d_col (dc): `500 mm`
- lb_col: `75.4 mm`
- Ecuación lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `14.5 mm`
- tf_col: `28 mm`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- tpe_vgizq: `25 mm`
- t_w4_1_vgizq: `8 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `8 mm`
- Ecuación 2w_w4_vgizq: `2w = t_w4.1`
- Ecuación Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgizq: `1701.65 kN`
- phi*Rn_cw_v2_col_vgizq: `1701.65 kN`
- DCR_cw_v2_col_vgizq: `1`
- Resultado: `🟢 Cumple`

#### 23.2.2. ELR #2: Pandeo local del alma (WCB)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-18)`
- Ecuación: `Condición aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgizq = max(|-Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|, |Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgizq = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condición aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgizq: `392.52 kN-m`
- Mu3_vgder: `382.5 kN-m`
- Pu_vgizq: `0 kN`
- Pu_vgder: `0 kN`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- termino_condicion_izq: `-756.88 kN`
- termino_condicion_der: `-737.56 kN`
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
- Ecuación 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `756.88 kN`
- phi*Rn_cw_v2_col_vgizq: `1168.79 kN`
- DCR_cw_v2_col_vgizq: `0.65`
- Resultado: `🟢 Cumple`

### 23.3. Revisión de capacidad a tracción (vg_der)

#### 23.3.1. ELR #1: Fluencia local del alma (WLY)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-17)`
- Ecuación: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado (phi_ductil): `1`
- Mf_vgder_critico: `1298.03 kN-m`
- St_col: `2500 mm`
- d_col: `500 mm`
- Ct_col: `1`
- kc_col: `55 mm`
- lb_col: `75.4 mm`
- Ecuación lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- tw_col: `14.5 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- tpe_vgder: `25 mm`
- t_w4_1_vgder: `8 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `8 mm`
- Ecuación 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `2028.01 kN`
- phi*Rn_cw_v2_col_vgder: `2028.01 kN`
- DCR_cw_v2_col_vgder: `1`
- Resultado: `🟢 Cumple`

### 23.4. Revisión de capacidad a compresión (vg_der)

#### 23.4.1. ELR #1: Arrugamiento local del alma (WLC)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuación: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; Rn_cw_v2_col_vgder = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_cw_v2_col_vgder; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado: `0.75`
- Mf_vgder_critico: `1298.03 kN-m`
- St_col: `2500 mm`
- d_col (dc): `500 mm`
- lb_col: `75.4 mm`
- Ecuación lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `14.5 mm`
- tf_col: `28 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- tpe_vgder: `25 mm`
- t_w4_1_vgder: `8 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `8 mm`
- Ecuación 2w_w4_vgder: `2w = t_w4.1`
- Ecuación Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgder: `1701.65 kN`
- phi*Rn_cw_v2_col_vgder: `1701.65 kN`
- DCR_cw_v2_col_vgder: `1`
- Resultado: `🟢 Cumple`

#### 23.4.2. ELR #2: Pandeo local del alma (WCB)

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7.2 + Eq. (6.7-18)`
- Ecuación: `Condición aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder y F_right = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq; Ru_cw_v2_col_vgder = max(|-Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|, |Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgder = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condición aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgder: `382.5 kN-m`
- Mu3_vgizq: `392.52 kN-m`
- Pu_vgder: `0 kN`
- Pu_vgizq: `0 kN`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- termino_condicion_der: `-737.56 kN`
- termino_condicion_izq: `-756.88 kN`
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
- Ecuación 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `737.56 kN`
- phi*Rn_cw_v2_col_vgder: `1168.79 kN`
- DCR_cw_v2_col_vgder: `0.63`
- Resultado: `🟢 Cumple`

### 23.5. Revisión de capacidad a cortante (col)

#### 23.5.1. ELR #1: Cortante en la zona del panel del alma (WPZS)

- Cláusula: `Documento: AISC 360-22w | Sección: AISC 360-22w Sección J10.6 + Eq. (J10-9) to Eq. (J10-12)`
- Ecuación: `Ru_wpz_v2_col = sum_Mf_col/(db-tf) - Vc2_col; Rn_wpz_v2_col = 0.60*Fy_col*d_col*(tw_col + n_dp_col*t_dp_col) (J10-9)`
- Considera deformacion inelastica del panel zone: `No`
- phi_ductil (usado en WPZS): `1`
- hb_col: `1250 mm`
- ht_col: `1250 mm`
- Mbe_col_vgizq_max: `1399.41 kN-m`
- Mbe_col_vgizq_min: `1274.7 kN-m`
- Mbe_col_vgder_max: `1398.42 kN-m`
- Mbe_col_vgder_min: `1275.69 kN-m`
- sum_Mbe_col: `2675.1 kN-m`
- Vc2_col: `1070.04 kN`
- d_vgizq: `536 mm`
- Mf_vgizq_max: `1298.63 kN-m`
- Mf_vgizq_min: `1223.02 kN-m`
- d_vgder: `536 mm`
- Mf_vgder_max: `1298.03 kN-m`
- Mf_vgder_min: `1223.62 kN-m`
- sum_Mf_col/(db-tf): `4863.58 kN`
- Ru_wpz_v2_col: `3793.54 kN`
- Pr_col: `1101.05 kN`
- Py_col: `8233.08 kN`
- alphaPr/Py: `0.13`
- Ag_col: `23864 mm2`
- Fy_col: `345 MPa`
- d_col: `500 mm`
- tw_col: `14.5 mm`
- t_dp_col: `12 mm`
- usar_weld_7_col: `True`
- tw_wpz_effective_col: `38.5 mm`
- Rn1_wpz_v2_col: `n/a`
- Rn2_wpz_v2_col: `n/a`
- bcf_col: `300 mm`
- tcf_col: `28 mm`
- Rn_wpz_v2_col: `3984.75 kN`
- DCR_wpz_v2_col: `0.95`
- Resultado: `🟢 Cumple`

## Paso 24 - Revisión de resistencia del alma de platinas de continuidad

### 24.1. Revisión de capacidad a tracción

#### 24.1.1. ELR #1: Fluencia por tracción area bruta

- Cláusula: `Documento: AISC 358-22 | Sección: Desarrollo interno de demanda para alma de platinas de continuidad`
- Ecuación: `Ru_pc_p+_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq) - min{phi*Rn_(23.1.1), phi*Rn_(23.2.1), phi*Rn_(22.1.1)}; Ru_pc_p+_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder) - min{phi*Rn_(23.3.1), phi*Rn_(23.4.1), phi*Rn_(22.2.1)}; Ru_pc_p+_col = max{Ru_pc_p+_col_vgder, Ru_pc_p+_col_vgizq}; phi*Rn_pc_p+_col = phi * Fy_pc_col * b1_pc_col * t_pc_col * n_pc_col`
- Mf_vgizq_critico: `1298.63 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `3837.55 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2028.01 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `1701.65 kN`
- min_capacidad_vgizq: `1701.65 kN`
- Ru_pc_p+_col_vgizq: `802.46 kN`
- Mf_vgder_critico: `1298.03 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `3837.55 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2028.01 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `1701.65 kN`
- min_capacidad_vgder: `1701.65 kN`
- Ru_pc_p+_col_vgder: `801.31 kN`
- Ru_pc_p+_col: `802.46 kN`
- phi usado: `0.9`
- Fy_pc_col: `345 MPa`
- b1_pc_col: `130 mm`
- t_pc_col: `16 mm`
- n_pc_col: `2`
- phi*Rn_pc_p+_col: `1291.68 kN`
- DCR_pc_p+_col: `0.62`
- Resultado: `🟢 Cumple`

### 24.2. Revisión de capacidad a compresión

#### 24.2.1. ELR #1: Pandeo por flexión

- Cláusula: `Documento: AISC 358-22 | Sección: Fórmula de Fcr segun imagen de usuario (K=0.65)`
- Ecuación: `Fcr_pc_col = 0.658^(Fy_pc_col/Fe_pc_col)*Fy_pc_col; phi*Rn_pc_p-_col = phi * Fcr_pc_col * b1_pc_col * t_pc_col * n_pc_col`
- Mf_vgizq_critico: `1298.63 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `3837.55 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2028.01 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `1701.65 kN`
- min_capacidad_vgizq: `1701.65 kN`
- Ru_pc_p-_col_vgizq: `802.46 kN`
- Mf_vgder_critico: `1298.03 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `3837.55 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2028.01 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `1701.65 kN`
- min_capacidad_vgder: `1701.65 kN`
- Ru_pc_p-_col_vgder: `801.31 kN`
- Ru_pc_p-_col: `802.46 kN`
- phi usado: `0.9`
- K: `0.65`
- Lp_pc_col: `311 mm`
- r_pc_col: `4.64 mm`
- KLr_pc_col: `43.57`
- E_pc_col: `200000 MPa`
- Fy_pc_col: `345 MPa`
- Fe_pc_col: `1039.96 MPa`
- Fcr_pc_col: `300.27 MPa`
- b1_pc_col: `130 mm`
- t_pc_col: `16 mm`
- n_pc_col: `2`
- phi*Rn_pc_p-_col: `1124.22 kN`
- DCR_pc_p-_col: `0.71`
- Resultado: `🟢 Cumple`

### 24.3. Revisión de capacidad a cortante

#### 24.3.1. ELR #1: Fluencia por cortante del area bruta

- Cláusula: `Documento: AISC 360-22 | Sección: G2.1 (adaptado a demanda de alma de platina de continuidad)`
- Ecuación: `Ru_pc_v2_col = Ru_pc_p+_col_vgder + Ru_pc_p+_col_vgizq; phi*Rn_pc_v2_col = phi * 0.6 * Fy_pc_col * t_pc_col * n_pc_col * L2_pc_col; DCR_pc_v2_col = Ru_pc_v2_col / phi*Rn_pc_v2_col`
- Mf_vgizq_critico: `1298.63 kN-m`
- d_vgizq: `536 mm`
- tf_vgizq: `17.4 mm`
- phi*Rn_cw_v2_col_vgizq (22.1.1): `3837.55 kN`
- phi*Rn_cw_v2_col_vgizq (23.1.1): `2028.01 kN`
- phi*Rn_cw_v2_col_vgizq (23.2.1): `1701.65 kN`
- min_capacidad_vgizq: `1701.65 kN`
- Ru_pc_p+_col_vgizq: `802.46 kN`
- Mf_vgder_critico: `1298.03 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- phi*Rn_cw_v2_col_vgder (22.2.1): `3837.55 kN`
- phi*Rn_cw_v2_col_vgder (23.3.1): `2028.01 kN`
- phi*Rn_cw_v2_col_vgder (23.4.1): `1701.65 kN`
- min_capacidad_vgder: `1701.65 kN`
- Ru_pc_p+_col_vgder: `801.31 kN`
- Ru_pc_v2_col: `1603.77 kN`
- phi usado: `1`
- Fy_pc_col: `345 MPa`
- t_pc_col: `16 mm`
- n_pc_col: `2`
- L2_pc_col: `311 mm`
- phi*Rn_pc_v2_col: `2060.06 kN`
- DCR_pc_v2_col: `0.78`
- Resultado: `🟢 Cumple`

## Paso 25- Revisión de resistencia de soldadura # 5 ( Platina de continuidad con aleta de columna)

### 25.1. Revisión de capacidad a tracción

#### 25.1.1. ELR #1: Rotura de soldadura

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7 + AISC 360-22 J2.4`
- Ecuación: `Ru_w5_p+_col = Fy_pc_col * b2_pc_col * t_pc_col * n_pc_col; Fillet: phi*Rn_w5_p+_col = phi_fragil * kds_w5_col * nl_w5_col * 0.6 * Fexx_w5_col * 0.707 * L_w5_col * w_w5_col * n_pc_col; DCR_w5_p+_col = Ru_w5_p+_col / phi*Rn_w5_p+_col`
- tipo_w5_col: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 26- Revisión de resistencia de soldadura # 6 ( Platina de continuidad con alma de columna)

### 26.1. Revisión de capacidad a cortante

#### 26.1.1. ELR #1: Rotura de soldadura

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7 + AISC 360-22 J2.4`
- Ecuación: `Ru1_w5_v2_col = 0.6 * Fy_pc_col * L2_pc_col * t_pc_col; Ru2_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * L_w6_col; Ru3_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * L_w6_col; Ru4_w5_v2_col = 0.6 * fu_col * tw_col * L_w6_col; Ru5_w5_v2_col = 0.6 * fy_col * tw_col * L_w6_col; Ru6_w5_v2_col = 0.6 * fu_col * tw_col * d_col; Ru7_w5_v2_col = 0.6 * fy_col * tw_col * d_col * Cv1; Ru8_w5_v2_col = 0.6 * fu_dp_col * t_dp_col * wz_dp_col; Ru9_w5_v2_col = 0.6 * fy_dp_col * t_dp_col * wz_dp_col; Ru_w5_v2_col = MIN{Ru1..Ru9}; Fillet: phi*Rn_w6_v2_col = phi_fragil * kds_w6_col * nl_w6_col * 0.6 * Fexx_w6_col * 0.707 * L_w6_col * w_w6_col; DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`
- tipo_w6_col: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

### 26.6. Revisión de capacidad del material base

#### 26.6.2. ELR #1: Rotura del material base

- Cláusula: `AISC 360-22 J4 (material base)`
- Ecuación: `Ru_w5_v2_col = MIN{Ru1..Ru9}; phi*Rn1_w6-dp_v2_col = phi_fragil * 0.6 * fu_dp_col * t_dp_col * L_w6_col; phi*Rn2_w6-dp_v2_col = phi_no_ductil * 0.6 * fy_dp_col * t_dp_col * L_w6_col; phi*Rn1_w6-cw_v2_col = phi_fragil * 0.6 * fu_col * tw_col * L_w6_col; phi*Rn2_w6-cw_v2_col = phi_no_ductil * 0.6 * fy_col * tw_col * L_w6_col; phi*Rn_w6_v2_col = min(phi*Rn1_w6-dp_v2_col, phi*Rn2_w6-dp_v2_col, phi*Rn1_w6-cw_v2_col, phi*Rn2_w6-cw_v2_col); DCR_w6_v2_col = Ru_w5_v2_col / phi*Rn_w6_v2_col`
- tipo_w6_col: `CJP`
- CJP: `Cumple`
- Resultado: `?? Cumple`

## Paso 27- Revisión de resistencia de soldadura # 8 (Platina de enchape con aleta de columna)

### 27.1. Revisión de capacidad a cortante

#### 27.1.1. ELR #1: Rotura de soldadura

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7 + AISC 360-22 J2.4`
- Ecuación: `Ru_w8_v2_col = max{Ru1_w8_v2_col, Ru2_w8_v2_col}; Ru1_w8_v2_col = 0.6 * Fy_dp_col * h_dp_col * t_dp_col; Ru2_w8_v2_col = max{Mf_vgizq_max + Mf_vgder_min, Mf_vgder_max + Mf_vgizq_min} * (t_dp_col/(t_dp_col*n_dp_col + tw_col)) / b_dp_col; Fillet: L_w8_col = h_dp_col - 2*L_gap_w8_col; phi*Rn_w8_v2_col = phi_fragil * kds_w8_col * nl_w8_col * 0.6 * Fexx_w8_col * 0.707 * L_w8_col * w_w8_col; DCR_w8_v2_col = Ru_w8_v2_col / phi*Rn_w8_v2_col`
- tipo_w8_col: `PJP`
- PJP: `Cumple`
- DCR_w8_v2_col: `n/a`
- Resultado: `🟢 Cumple`

## Paso 28- Revisión de resistencia de soldadura # 7 (Platina de enchape con alma de columna)

### 28.1. Revisión de capacidad a cortante

#### 28.1.1. ELR #1: Rotura de soldadura

- Cláusula: `Documento: AISC 358-22 | Sección: Capitulo 6 / Sección 6.7 + Desarrollo interno`
- Ecuación: `Ru_w7_v2_col = Ru_wpz_v2_col * (t_dp_col / (t_dp_col*n_dp_col + tw_col)); phi*Rn_w7_v2_col = phi_fragil * (nfilas_w7_col)*(ncolumna_w7_col) * 0.60 * Fexx_w7_col * 0.25 * 3.1416 * d_hole_w7_col^2; DCR_w7_v2_col = Ru_w7_v2_col / phi*Rn_w7_v2_col`
- phi usado (phi_fragil): `0.75`
- nfilas_w7_col: `3`
- ncolumna_w7_col: `2`
- Ru_wpz_v2_col: `3793.54 kN`
- t_dp_col: `12 mm`
- n_dp_col: `2`
- tw_col: `14.5 mm`
- Fexx_w7_col: `485 MPa`
- d_hole_w7_col (usado en fórmula): `31 mm`
- Ru_w7_v2_col: `1182.4 kN`
- phi*Rn_w7_v2_col: `988.37 kN`
- DCR_w7_v2_col: `1.2`
- Resultado: `🔴 No cumple`

## Paso 29 - Resumen general

DCR ordenados de mayor a menor para identificar los estados limite criticos.

- DCR critico global: 🔴 `DCR_w7_v2_col = 1.2` en `28.1.1. ELR #1: Rotura de soldadura`

1. 🔴 `DCR_w7_v2_col` = `1.2`
Subcapitulo aplicado: `28.1.1. ELR #1: Rotura de soldadura`
2. 🟢 `DCR_cw_v2_col_vgizq` = `1`
Subcapitulo aplicado: `23.1.1. ELR #1: Fluencia local del alma (WLY)`
3. 🟢 `DCR_cw_v2_col_vgizq` = `1`
Subcapitulo aplicado: `23.2.1. ELR #1: Arrugamiento local del alma (WLC)`
4. 🟢 `DCR_cw_v2_col_vgder` = `1`
Subcapitulo aplicado: `23.3.1. ELR #1: Fluencia local del alma (WLY)`
5. 🟢 `DCR_cw_v2_col_vgder` = `1`
Subcapitulo aplicado: `23.4.1. ELR #1: Arrugamiento local del alma (WLC)`
6. 🟢 `DCR_wpz_v2_col` = `0.95`
Subcapitulo aplicado: `23.5.1. ELR #1: Cortante en la zona del panel del alma (WPZS)`
7. 🟢 `DCR_pe_m3_vgizq` = `0.9`
Subcapitulo aplicado: `10.1.1. ELR #1: Fluencia (vg_izq)`
8. 🟢 `DCR_pe_m3_vgder` = `0.9`
Subcapitulo aplicado: `11.1.1. ELR #1: Fluencia (vg_der)`
9. 🟢 `DCR_b_p+_vgizq` = `0.88`
Subcapitulo aplicado: `8.1.1 Estado #1: Rotura en el perno (vg_izq)`
10. 🟢 `DCR_b_p+_vgder` = `0.88`
Subcapitulo aplicado: `9.1.1 Estado #1: Rotura en el perno (vg_der)`
11. 🟢 `DCR_pc_v2_col` = `0.78`
Subcapitulo aplicado: `24.3.1. ELR #1: Fluencia por cortante del area bruta`
12. 🟢 `DCR_pc_p-_col` = `0.71`
Subcapitulo aplicado: `24.2.1. ELR #1: Pandeo por flexión`
13. 🟢 `DCR_cf_v2_col_vgizq` = `0.65`
Subcapitulo aplicado: `22.1.1. ELR #1: Flexión local de la aleta (LFB)`
14. 🟢 `DCR_cf_v2_col_vgder` = `0.65`
Subcapitulo aplicado: `22.2.1. ELR #1: Flexión local de la aleta (LFB)`
15. 🟢 `DCR_cw_v2_col_vgizq` = `0.65`
Subcapitulo aplicado: `23.2.2. ELR #2: Pandeo local del alma (WCB)`
16. 🟢 `DCR_cw_v2_col_vgder` = `0.63`
Subcapitulo aplicado: `23.4.2. ELR #2: Pandeo local del alma (WCB)`
17. 🟢 `DCR_pc_p+_col` = `0.62`
Subcapitulo aplicado: `24.1.1. ELR #1: Fluencia por tracción area bruta`
18. 🟢 `DCR_v2_vgizq` = `0.33`
Subcapitulo aplicado: `18.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_izq)`
19. 🟢 `DCR_v2_vgder` = `0.33`
Subcapitulo aplicado: `19.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_der)`
20. 🟢 `DCR_b_v2_vgizq` = `0.24`
Subcapitulo aplicado: `8.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)`
21. 🟢 `DCR_b_v2_vgder` = `0.23`
Subcapitulo aplicado: `9.2.1 ELR #2: Rotura por cortante en el perno (vg_der)`
22. 🟢 `DCR_pe_v2_vgizq` = `0.08`
Subcapitulo aplicado: `10.3.2. ELR #2: Aplastamiento en la perforación del perno (vg_izq)`
23. 🟢 `DCR_pe_v2_vgder` = `0.08`
Subcapitulo aplicado: `11.3.2. ELR #2: Aplastamiento en la perforación del perno (vg_der)`
24. 🟢 `DCR_pe_v2_vgizq` = `0.06`
Subcapitulo aplicado: `10.3.1. ELR #1: Desgarramiento en la perforación del perno (vg_izq)`
25. 🟢 `DCR_pe_v2_vgder` = `0.06`
Subcapitulo aplicado: `11.3.1. ELR #1: Desgarramiento en la perforación del perno (vg_der)`
26. ⚪ `DCR_w8_v2_col` = `n/a`
Subcapitulo aplicado: `27.1.1. ELR #1: Rotura de soldadura`
