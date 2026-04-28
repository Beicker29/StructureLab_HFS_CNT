# Memoria de Calculo

- Proyecto: `proj_bseep_si_demo`
- Caso: `case_si_bseep_8es_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bseep_8es`
- Estado global: `🔴 No cumple`

## Paso 1 - Limites de precalificacion

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### 1.1 Notas tecnicas

#### 1.1.1 Nota tecnica - Longitud de zona protegida medida desde la cara de la columna

- Ambito: `BEAM`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (8)`
- Formula: `Lpz_vgder = min(L_pest_vgder + 0.5*d_vgder, 3*bf_vgder); Lpz_vgizq = min(L_pest_vgizq + 0.5*d_vgizq, 3*bf_vgizq)`
- Lpz_vgder: `458.53 mm`
- Lpz_vgizq: `494.03 mm`

#### 1.1.2 Nota tecnica - Ubicacion de la conexion de placa de extremo en columna

- Ambito: `COLUMN`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (2)`
- Requisito: `La placa de extremo debe conectarse al ala de la columna.`

#### 1.1.3 Nota tecnica - Altura derivada de placa de extremo

- Ambito: `END_PLATE_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `Hpe_vgder = d_vgder + 2*pfo_pe_vgder + 2*de_pe_vgder`
- Hpe_vgder: `756 mm`

#### 1.1.4 Nota tecnica - Geometria placa de extremo de viga a derecha

- Ambito: `END_PLATE_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 + AISC 360-22 Tabla J3.3`
- Formula: `h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in`
- h1_vgder: `672.3 mm`
- h2_vgder: `577.3 mm`
- h3_vgder: `458.4 mm`
- h4_vgder: `363.4 mm`
- dh_vgder: `31.75 mm`

#### 1.1.5 Nota tecnica - Altura derivada de placa de extremo

- Ambito: `END_PLATE_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `Hpe_vgizq = d_vgizq + 2*pfo_pe_vgizq + 2*de_pe_vgizq`
- Hpe_vgizq: `827 mm`

#### 1.1.6 Nota tecnica - Geometria placa de extremo de viga a izquierda

- Ambito: `END_PLATE_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 + AISC 360-22 Tabla J3.3`
- Formula: `h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in`
- h1_vgizq: `672.3 mm`
- h2_vgizq: `577.3 mm`
- h3_vgizq: `458.4 mm`
- h4_vgizq: `363.4 mm`
- dh_vgizq: `31.75 mm`

#### 1.1.7 Nota tecnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ambito: `END_PLATE_STIFFENER_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgder = pfo_pe_vgder + de_pe_vgder; L_pest_vgder = h_pest_vgder/tan(30 deg); Ed_pest_vgder = 25 mm`
- h_pest_vgder: `110 mm`
- L_pest_vgder: `190.53 mm`
- edge_detailing (Ed_pest_vgder): `25 mm`

#### 1.1.8 Nota tecnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; L_pest_vgizq = h_pest_vgizq/tan(30 deg); Ed_pest_vgizq = 25 mm`
- h_pest_vgder: `n/a`
- L_pest_vgder: `n/a`
- h_pest_vgizq: `110 mm`
- L_pest_vgizq: `190.53 mm`
- edge_detailing (Ed_pest_vgder): `n/a`
- edge_detailing (Ed_pest_vgizq): `25 mm`

#### 1.1.9 Nota tecnica - Secuencia de soldadura para conexiones placa de extremo rigidizadas

- Ambito: `WELDS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Requisito: `Para conexiones placa de extremo rigidizadas, la soldadura entre el ala de la viga y la placa de extremo debe ejecutarse antes de instalar el rigidizador.`

#### 1.1.10 Nota tecnica - Excepcion de respaldo en la raiz cerca del alma de la viga

- Ambito: `WELDS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Requisito: `No se requiere respaldo en la raiz del ala, directamente por encima y por debajo del alma de la viga, en una longitud igual a 1.5k1. En esa ubicacion se permite una soldadura de ranura PJP de profundidad completa.`

#### 1.1.11 Nota tecnica - Requisitos de instalacion para conjuntos empernados

- Ambito: `BOLTS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.`

#### 1.1.12 Nota tecnica - Control y aseguramiento de calidad para conjuntos empernados

- Ambito: `BOLTS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Familia de perfil de viga permitida para precalificacion (viga izquierda) (`perfil_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `perfil_vgizq in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.2 - Familia de perfil de viga permitida para precalificacion (viga derecha) (`perfil_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `perfil_vgder in {W, HEA, HEB, IPE}; 'W21X68' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.3 - Ancho de placa de extremo vs ancho de ala de viga (left beam) (`bp_pe_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `bp_pe_vgizq >= bf_vgizq + margin (25 mm); 230 mm >= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.4 - Separacion minima de gage de pernos (left beam) (`g_b_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `g_b_vgizq >= 3db; 140 mm >= 85.72 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.5 - Longitud sin conectores de cortante desde la cara de columna (left beam) (`Lnc_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Lnc_vgizq >= 1.5d_vgizq; 1000 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.6 - Criterio de despeje de viga con umbral Sc y S (left beam) (`Sc_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Sc = St_col - pfo - pb; S = 0.5*sqrt(bcf*g); Sc_vgizq > S => 617.004 mm > 102.470 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.7 - Relacion luz libre/peralte por sistema de marco (left beam) (`Llb_vgizq/d_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Llb_vgizq/d_vgizq >= 7 (SMF); 12.36 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.8 - Compacidad ancho-espesor del ala de viga (left beam) (`lambda_f_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `lambda_f_vgizq <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.9 - Compacidad ancho-espesor del alma de viga (left beam) (`lambda_w_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `lambda_w_vgizq <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.10 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `bp_pe_vgder >= bf_vgder + margin (25 mm); 230 mm >= 235 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.11 - Separacion minima de gage de pernos (right beam) (`g_b_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `g_b_vgder >= 3db; 140 mm >= 85.72 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.12 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 804 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.13 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Sc = St_col - pfo - pb; S = 0.5*sqrt(bcf*g); Sc_vgder > S => 617.004 mm > 102.470 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.14 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Llb_vgder/d_vgder >= 7 (SMF); 11.37 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.15 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_f_vgder <= lambda_f_limit; 6.03 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.16 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_w_vgder <= lambda_w_limit; 43.63 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.17 - Familia de perfil de columna permitida para precalificacion (`shape_col`)

- Ambito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'HEB 400' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.18 - Peralte maximo del perfil de columna (W36/W920) (`d_col`)

- Ambito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 400 mm <= 920 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.19 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ambito: `COLUMN`
- Verificacion: `bp <= bcf; 230 mm <= 300 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.20 - Condicion de conexion columna-losa (`col_losa`)

- Ambito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.21 - Proyeccion de columna minima por encima de las vigas (`St_col`)

- Ambito: `COLUMN`
- Verificacion: `St_col >= pfo_pe_vgder + pb_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq + 12.5 mm; 762.000 mm >= 217.496 mm; 762.000 mm >= 217.496 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje superior de columna)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.22 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 6.25 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.23 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 22.07 adim <= 50.81 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.24 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ambito: `END_PLATE_DER`
- Verificacion: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [228.6 mm, 235 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.25 - Desigualdades explicitas de ancho de placa de extremo (left beam) (`bp_pe_vgizq`)

- Ambito: `END_PLATE_IZQ`
- Verificacion: `bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf; [min,max] = [228.6 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.26 - Altura del rigidizador derivada de la geometria de la placa de extremo (right beam) (`h_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder = pfo_pe_vgder + de_pe_vgder; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.27 - Altura del rigidizador derivada de la geometria de la placa de extremo (left beam) (`h_pest_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.28 - Espesor minimo requerido del rigidizador (right beam) (`t_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `t_pest_vgder >= tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 12.7 mm >= 10.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.29 - Limite de pandeo local ancho-espesor del rigidizador (right beam) (`h_pest_vgder/t_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder/t_pest_vgder <= 0.56*sqrt(E_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 8.66 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.30 - Despeje del gage de pernos con espesor del rigidizador (right beam) (`g_b_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `g_b_vgder >= 2emin + t_pest_vgder; 140 mm >= 88.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.31 - Espesor minimo requerido del rigidizador (left beam) (`t_pest_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `t_pest_vgizq >= tw_vgizq*(Fy_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 12.7 mm >= 11.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.32 - Limite de pandeo local ancho-espesor del rigidizador (left beam) (`h_pest_vgizq/t_pest_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq/t_pest_vgizq <= 0.56*sqrt(E_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 8.66 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.33 - Despeje del gage de pernos con espesor del rigidizador (left beam) (`g_b_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `g_b_vgizq >= 2emin + t_pest_vgizq; 140 mm >= 88.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.34 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (`weld_ep_web`)

- Ambito: `WELDS`
- Verificacion: `weld_ep_web in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.35 - Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha) (`tipo_w4_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 0 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 0.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.36 - Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda) (`tipo_w4_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 0 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 0.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.37 - Tamano minimo de soldadura de filete (#1, viga derecha) (`w_w1_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `w_w1_vgder >= wmin_j24_w1_vgder; 9.53 mm >= 5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Tabla J2.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.38 - Tamano maximo de soldadura de filete (#1, viga derecha) (`w_w1_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `w_w1_vgder <= wmax_j2b_w1_vgder; 9.53 mm <= 10.7 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2b`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.39 - Longitud minima de soldadura de filete para diseno por resistencia (#1, viga derecha) (`l_w1_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `l_w1_vgder >= 4*w_w1_vgder; 65.95 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(c)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.40 - Longitud efectiva de soldadura de filete cargada en el extremo (#1, viga derecha) (`l_w1_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `l/w = 6.924; beta = 1.000; l_eff_w1_vgder = 65.950 mm; si l/w<=100 => l_eff=l; si 100<l/w<=300 => l_eff=beta*l; si l/w>300 => l_eff=180w`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(d) + Eq. (J2-1)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.41 - Tamano minimo de soldadura de filete (#2, viga derecha) (`w_w2_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `w_w2_vgder >= wmin_j24_w2_vgder; 9.53 mm >= 5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Tabla J2.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.42 - Tamano maximo de soldadura de filete (#2, viga derecha) (`w_w2_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `w_w2_vgder <= wmax_j2b_w2_vgder; 9.53 mm <= 8.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2b`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.43 - Longitud minima de soldadura de filete para diseno por resistencia (#2, viga derecha) (`l_w2_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `l_w2_vgder >= 4*w_w2_vgder; 146.48 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(c)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.44 - Longitud efectiva de soldadura de filete cargada en el extremo (#2, viga derecha) (`l_w2_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `l/w = 15.378; beta = 1.000; l_eff_w2_vgder = 146.476 mm; si l/w<=100 => l_eff=l; si 100<l/w<=300 => l_eff=beta*l; si l/w>300 => l_eff=180w`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(d) + Eq. (J2-1)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.45 - Tamano minimo de soldadura de filete (#1, viga izquierda) (`w_w1_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `w_w1_vgizq >= wmin_j24_w1_vgizq; 9.53 mm >= 5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Tabla J2.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.46 - Tamano maximo de soldadura de filete (#1, viga izquierda) (`w_w1_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `w_w1_vgizq <= wmax_j2b_w1_vgizq; 9.53 mm <= 10.7 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2b`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.47 - Longitud minima de soldadura de filete para diseno por resistencia (#1, viga izquierda) (`l_w1_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `l_w1_vgizq >= 4*w_w1_vgizq; 65.95 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(c)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.48 - Longitud efectiva de soldadura de filete cargada en el extremo (#1, viga izquierda) (`l_w1_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `l/w = 6.924; beta = 1.000; l_eff_w1_vgizq = 65.950 mm; si l/w<=100 => l_eff=l; si 100<l/w<=300 => l_eff=beta*l; si l/w>300 => l_eff=180w`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(d) + Eq. (J2-1)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.49 - Tamano minimo de soldadura de filete (#2, viga izquierda) (`w_w2_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `w_w2_vgizq >= wmin_j24_w2_vgizq; 9.53 mm >= 5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Tabla J2.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.50 - Tamano maximo de soldadura de filete (#2, viga izquierda) (`w_w2_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `w_w2_vgizq <= wmax_j2b_w2_vgizq; 9.53 mm <= 9.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2b`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.51 - Longitud minima de soldadura de filete para diseno por resistencia (#2, viga izquierda) (`l_w2_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `l_w2_vgizq >= 4*w_w2_vgizq; 146.48 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(c)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.52 - Longitud efectiva de soldadura de filete cargada en el extremo (#2, viga izquierda) (`l_w2_vgizq`)

- Ambito: `WELDS_IZQ`
- Verificacion: `l/w = 15.378; beta = 1.000; l_eff_w2_vgizq = 146.476 mm; si l/w<=100 => l_eff=l; si 100<l/w<=300 => l_eff=beta*l; si l/w>300 => l_eff=180w`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 360-22 Seccion J2.2(d) + Eq. (J2-1)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.53 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.54 - Tipo de soldadura de platina de continuidad cuando el espesor es menor o igual a 10 mm (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {cjp, pjp} => cumple siempre; tcp=15.9 mm; weld_cp='cjp'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.55 - El tipo de apriete del perno debe ser una categoria reconocida (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.56 - Los pernos deben estar pretensionados salvo que una conexion especifica permita lo contrario (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.57 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (`std_bolt`)

- Ambito: `BOLTS`
- Verificacion: `std_bolt in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.58 - Distancia de borde en de (right beam) (`de_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `de_pe_vgder >= emin; 60 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.59 - Limites de distancia en fila exterior de pernos (right beam) (`pfo_pe_vgder - pso_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pso_pe_vgder (=pfo_pe_vgder) >= emin; pfo_pe_vgder <= 51 mm; pfo_pe_vgder >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.60 - Limites de distancia en fila interior de pernos (right beam) (`pfi_pe_vgder - psi_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pfi_pe_vgder >= emin; pfi_pe_vgder <= 51 mm; pfi_pe_vgder >= 41 mm; psi_pe_vgder = pfi_pe_vgder + tf_vgder - tcp_col; psi_pe_vgder > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.61 - Separacion minima vertical entre pernos (right beam) (`pb_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pb_pe_vgder >= 3db; pb_pe_vgder <= 95.000 mm; pb_pe_vgder >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.62 - Limites de espesor del ala de viga (right beam) (`tf_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `tf_vgder in [tf_vgder_min, tf_vgder_max]; 14.29 mm <= 17.4 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.63 - Limites de ancho del ala de viga (right beam) (`bf_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `bf_vgder in [bf_vgder_min, bf_vgder_max]; 190.5 mm <= 210 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.64 - Limites de peralte de la viga conectada (right beam) (`d_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `d_vgder in [d_vgder_min, d_vgder_max]; 457.2 mm <= 536 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.65 - Limites de espesor de placa de extremo (right beam) (`tpe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `tpe_vgder in [tpe_vgder_min, tpe_vgder_max]; 19.05 mm <= 25.4 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.66 - Limites de separacion horizontal de pernos (right beam) (`g_b_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `g_b_vgder in [g_b_vgder_min, g_b_vgder_max]; 127 mm <= 140 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.67 - Distancia de borde en de (left beam) (`de_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `de_pe_vgizq >= emin; 60 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.68 - Limites de distancia en fila exterior de pernos (left beam) (`pfo_pe_vgizq - pso_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `pso_pe_vgizq (=pfo_pe_vgizq) >= emin; pfo_pe_vgizq <= 51 mm; pfo_pe_vgizq >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.69 - Limites de distancia en fila interior de pernos (left beam) (`pfi_pe_vgizq - psi_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `pfi_pe_vgizq >= emin; pfi_pe_vgizq <= 51 mm; pfi_pe_vgizq >= 41 mm; psi_pe_vgizq = pfi_pe_vgizq + tf_vgizq - tcp_col; psi_pe_vgizq > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.70 - Separacion minima vertical entre pernos (left beam) (`pb_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `pb_pe_vgizq >= 3db; pb_pe_vgizq <= 95.000 mm; pb_pe_vgizq >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.71 - Limites de espesor del ala de viga (left beam) (`tf_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `tf_vgizq in [tf_vgizq_min, tf_vgizq_max]; 14.29 mm <= 17.3 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.72 - Limites de ancho del ala de viga (left beam) (`bf_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `bf_vgizq in [bf_vgizq_min, bf_vgizq_max]; 190.5 mm <= 228 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.73 - Limites de peralte de la viga conectada (left beam) (`d_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `d_vgizq in [d_vgizq_min, d_vgizq_max]; 457.2 mm <= 607 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.74 - Limites de espesor de placa de extremo (left beam) (`tpe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `tpe_vgizq in [tpe_vgizq_min, tpe_vgizq_max]; 19.05 mm <= 25.4 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.75 - Limites de separacion horizontal de pernos (left beam) (`g_b_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `g_b_vgizq in [g_b_vgizq_min, g_b_vgizq_max]; 127 mm <= 140 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

## Paso 2 - Momento probable maximo en rotula plastica (Mpr)

Calculo de momento probable por lado usando `Mpr = Cpr * Ry * Fy * Ze` (Ze = Zx del catalogo).

### 2.1 Calculo de Mpr para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr_vgizq = Cpr_vgizq * Ry * Fy * Ze_vgizq`
- Fy_vgizq: `345 MPa`
- Ry: `1.1`
- Ze_vgizq (catalogo): `3280000 mm3`
- Demanda de ductilidad_vgizq: `high`
- Cpr_vgizq: `1.15`
- Mpr_vgizq: `1431.47 kN-m`

### 2.2 Calculo de Mpr para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr_vgder = Cpr_vgder * Ry * Fy * Ze_vgder`
- Fy_vgder: `345 MPa`
- Ry: `1.1`
- Ze_vgder (catalogo): `2620000 mm3`
- Demanda de ductilidad_vgder: `high`
- Cpr_vgder: `1.15`
- Mpr_vgder: `1143.43 kN-m`

## Paso 3 - Distancia de rotula plastica desde la cara de la columna (Sh)

### 3.1 Calculo de Sh para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuacion: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`
- d_vgizq: `607 mm`
- bf_vgizq: `228 mm`
- Sh_vgizq: `215.93 mm`

### 3.2 Calculo de Sh para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`
- d_vgder: `536 mm`
- bf_vgder: `210 mm`
- Sh_vgder: `215.93 mm`

- Lado gobernante Sh: `der`
- Sh adoptado (gobernante): `215.93 mm`

## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.

### 4.1 Calculo de cortante probable para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgizq_max = 2*Mpr/Llb_vgizq + Vg_vgizq; Vh_vgizq_min = 2*Mpr/Llb_vgizq - Vg_vgizq`
- Mpr_vgizq: `1431.47 kN-m`
- Llb_vgizq: `7500 mm`
- Vg_vgizq: `97.11 kN`
- Vh_vgizq_max: `478.84 kN`
- Vh_vgizq_min: `284.62 kN`
- Vhmax adoptado (gobernante): `478.84 kN`

### 4.2 Calculo de cortante probable para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgder_max = 2*Mpr/Llb_vgder + Vg_vgder; Vh_vgder_min = 2*Mpr/Llb_vgder - Vg_vgder`
- Mpr_vgder: `1143.43 kN-m`
- Llb_vgder: `6096 mm`
- Vg_vgder: `44.48 kN`
- Vh_vgder_max: `419.62 kN`
- Vh_vgder_min: `330.66 kN`
- Vhmax adoptado (gobernante): `419.62 kN`

## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.

### 5.1 Calculo de momento probable en cara de columna para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgizq_max = Mpr_vgizq + Vh_vgizq_max*Sh_vgizq; Mf_vgizq_min = Mpr_vgizq + Vh_vgizq_min*Sh_vgizq`
- Mpr_vgizq: `1431.47 kN-m`
- Sh_vgizq: `215.93 mm`
- Mf_vgizq_max: `1534.87 kN-m`
- Mf_vgizq_min: `1492.93 kN-m`

### 5.2 Calculo de momento probable en cara de columna para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgder_max = Mpr_vgder + Vh_vgder_max*Sh_vgder; Mf_vgder_min = Mpr_vgder + Vh_vgder_min*Sh_vgder`
- Mpr_vgder: `1143.43 kN-m`
- Sh_vgder: `215.93 mm`
- Mf_vgder_max: `1234.04 kN-m`
- Mf_vgder_min: `1214.83 kN-m`

## Paso 6 - Revision De Resistencia Pernos (vg_izq)

### 6.1 Revision de capacidad a traccion (vg_izq)

#### 6.1.1 Estado #1: Rotura en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq + h3_pe_vgizq + h4_pe_vgizq)); phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1534.87 kN-m`
- h1_pe_vgizq: `672.3 mm`
- h2_pe_vgizq: `577.3 mm`
- h3_pe_vgizq: `458.4 mm`
- h4_pe_vgizq: `363.4 mm`
- A_b_vgizq: `641.3 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_p+_vgizq: `370.49 kN`
- phi*Rn_b_p+_vgizq: `450.19 kN`
- DCR_b_p+_vgizq: `0.82`
- Resultado: `🟢 Cumple`

### 6.2 Revision de capacidad a cortante (vg_izq)

#### 6.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgizq_critico: `478.84 kN`
- n_b_vgizq: `8`
- A_b_vgizq: `641.3 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_v2_vgizq: `59.85 kN`
- phi*Rn_b_v2_vgizq: `271.27 kN`
- DCR_b_v2_vgizq: `0.22`
- Resultado: `🟢 Cumple`

## Paso 7 - Revision De Resistencia Pernos (vg_der)

### 7.1 Revision de capacidad a traccion (vg_der)

#### 7.1.1 Estado #1: Rotura en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder + h3_pe_vgder + h4_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgder_critico: `1234.04 kN-m`
- h1_pe_vgder: `672.3 mm`
- h2_pe_vgder: `577.3 mm`
- h3_pe_vgder: `458.4 mm`
- h4_pe_vgder: `363.4 mm`
- A_b_vgder: `641.3 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_p+_vgder: `297.88 kN`
- phi*Rn_b_p+_vgder: `450.19 kN`
- DCR_b_p+_vgder: `0.66`
- Resultado: `🟢 Cumple`

### 7.2 Revision de capacidad a cortante (vg_der)

#### 7.2.1 ELR #2: Rotura por cortante en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgder_critico: `419.62 kN`
- n_b_vgder: `8`
- A_b_vgder: `641.3 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_v2_vgder: `52.45 kN`
- phi*Rn_b_v2_vgder: `271.27 kN`
- DCR_b_v2_vgder: `0.19`
- Resultado: `🟢 Cumple`

## Paso 8 - Revision de resistencia platina extremo (vg_izq)

### 8.1. Revision de capacidad a flexion (vg_izq)

#### 8.1.1. ELR #1: Fluencia (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgizq = Mf_vgizq_critico; phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1534.87 kN-m`
- tpe_vgizq: `25.4 mm`
- Fyp_pe_vgizq: `345 MPa`
- Yp_pe_vgizq: `6884 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgizq: `89.72 mm`
- pfi_pe_vgizq_entrada: `50 mm`
- pfi_pe_vgizq_efectivo: `50 mm`
- Ru_pe_m3_vgizq: `1534.87 kN-m`
- phi*Rn_pe_m3_vgizq: `1379.02 kN-m`
- DCR_pe_m3_vgizq: `1.11`
- Resultado: `🔴 No cumple`

### 8.2. Revision de capacidad a cortante perpendicular al plano de la platina (vg_izq)

#### 8.2.1. ELR #1: Fluencia por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Rn_pe_v1_vgizq = Ru_pe_m3_vgizq / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v1_vgizq = phi * 0.6 * Fyp_pe_vgizq * bpe_vgizq * tpe_vgizq (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.75`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `230 mm`
- tpe_vgizq: `25.4 mm`
- Fyp_pe_vgizq: `345 MPa`
- Ru_pe_m3_vgizq: `1534.87 kN-m`
- Rn_pe_v1_vgizq: `1301.4 kN`
- phi*Rn_pe_v1_vgizq: `906.97 kN`
- DCR_pe_v1_vgizq: `1.43`
- Resultado: `🔴 No cumple`

#### 8.2.2. ELR #2: Rotura por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgizq = Ru_pe_m3_vgizq / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v2_vgizq = phi * 0.6 * Fup_pe_vgizq * tpe_vgizq * (bpe_vgizq - 2*(dh_pe_vgizq + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.75`
- Ru_pe_m3_vgizq: `1534.87 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `230 mm`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- dh_pe_vgizq: `31.75 mm`
- Rn_pe_v2_vgizq: `1301.4 kN`
- phi*Rn_pe_v2_vgizq: `839.93 kN`
- DCR_pe_v2_vgizq: `1.55`
- Resultado: `🔴 No cumple`

### 8.3. Revision de capacidad a cortante paralelo al plano de la platina (vg_izq)

#### 8.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgizq = min(pb_pe_vgizq - dh_pe_vgizq, pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq); Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 1.2 * lc_pe_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.75`
- Vh_vgizq_critico: `478.84 kN`
- n_b_vgizq: `8`
- pb_pe_vgizq: `n/a`
- pfo_pe_vgizq: `50 mm`
- pfi_pe_vgizq: `50 mm`
- tf_vgizq: `17.3 mm`
- dh_pe_vgizq: `31.75 mm`
- lc_pe_vgizq: `63.25 mm`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- Ru_pe_v2_vgizq: `59.85 kN`
- phi*Rn_pe_v2_vgizq: `650.61 kN`
- DCR_pe_v2_vgizq: `0.09`
- Resultado: `🟢 Cumple`

#### 8.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 2.4 * d_b_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.75`
- Vh_vgizq_critico: `478.84 kN`
- n_b_vgizq: `8`
- tpe_vgizq: `25.4 mm`
- Fup_pe_vgizq: `450 MPa`
- d_b_vgizq: `28.57 mm`
- Ru_pe_v2_vgizq: `59.85 kN`
- phi*Rn_pe_v2_vgizq: `587.9 kN`
- DCR_pe_v2_vgizq: `0.1`
- Resultado: `🟢 Cumple`

## Paso 9 - Revision de resistencia platina extremo (vg_der)

### 9.1. Revision de capacidad a flexion (vg_der)

#### 9.1.1. ELR #1: Fluencia (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mf_vgder_critico: `1234.04 kN-m`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Yp_pe_vgder: `6884 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgder: `89.72 mm`
- pfi_pe_vgder_entrada: `50 mm`
- pfi_pe_vgder_efectivo: `50 mm`
- Ru_pe_m3_vgder: `1234.04 kN-m`
- phi*Rn_pe_m3_vgder: `1379.02 kN-m`
- DCR_pe_m3_vgder: `0.89`
- Resultado: `🟢 Cumple`

### 9.2. Revision de capacidad a cortante perpendicular al plano de la platina (vg_der)

#### 9.2.1. ELR #1: Fluencia por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Rn_pe_v1_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v1_vgder = phi * 0.6 * Fyp_pe_vgder * bpe_vgder * tpe_vgder (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.75`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- z_vgder = d_vgder - tf_vgder: `518.6 mm`
- bpe_vgder: `230 mm`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Ru_pe_m3_vgder: `1234.04 kN-m`
- Rn_pe_v1_vgder: `1189.78 kN`
- phi*Rn_pe_v1_vgder: `906.97 kN`
- DCR_pe_v1_vgder: `1.31`
- Resultado: `🔴 No cumple`

#### 9.2.2. ELR #2: Rotura por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v2_vgder = phi * 0.6 * Fup_pe_vgder * tpe_vgder * (bpe_vgder - 2*(dh_pe_vgder + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.75`
- Ru_pe_m3_vgder: `1234.04 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- z_vgder = d_vgder - tf_vgder: `518.6 mm`
- bpe_vgder: `230 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- dh_pe_vgder: `31.75 mm`
- Rn_pe_v2_vgder: `1189.78 kN`
- phi*Rn_pe_v2_vgder: `839.93 kN`
- DCR_pe_v2_vgder: `1.42`
- Resultado: `🔴 No cumple`

### 9.3. Revision de capacidad a cortante paralelo al plano de la platina (vg_der)

#### 9.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgder = min(pb_pe_vgder - dh_pe_vgder, pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder); Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.75`
- Vh_vgder_critico: `419.62 kN`
- n_b_vgder: `8`
- pb_pe_vgder: `n/a`
- pfo_pe_vgder: `50 mm`
- pfi_pe_vgder: `50 mm`
- tf_vgder: `17.4 mm`
- dh_pe_vgder: `31.75 mm`
- lc_pe_vgder: `63.25 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- Ru_pe_v2_vgder: `52.45 kN`
- phi*Rn_pe_v2_vgder: `650.61 kN`
- DCR_pe_v2_vgder: `0.08`
- Resultado: `🟢 Cumple`

#### 9.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.75`
- Vh_vgder_critico: `419.62 kN`
- n_b_vgder: `8`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- d_b_vgder: `28.57 mm`
- Ru_pe_v2_vgder: `52.45 kN`
- phi*Rn_pe_v2_vgder: `587.9 kN`
- DCR_pe_v2_vgder: `0.09`
- Resultado: `🟢 Cumple`

## Paso 10 - Revision de Resistencia soldadura #1 (platina extremo vg_izq - rigidizador vg_izq)

### 10.1. Revision de capacidad a traccion (vg_izq)

#### 10.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w1_p+_vgizq = Fys_pest_vgizq * t_pest_vgizq * h_pest_vgizq; l_w1_vgizq = h_pest_vgizq - c_pest_vgizq - 2*w_w1_vgizq; phi*Rn_w1_p+_vgizq = phi * kds_w1_vgizq * nl_w1_vgizq * 0.6 * Fexx_w1_vgizq * 0.707 * l_w1_vgizq * w_w1_vgizq; DCR_w1_p+_vgizq = Ru_w1_p+_vgizq / phi*Rn_w1_p+_vgizq (AISC 360-22 J2.4)`
- tipo_w1_vgizq: `fillet`
- phi usado: `0.75`
- l_w1_vgizq (longitud soldadura calculada): `l_w1_vgizq = h_pest_vgizq - c_pest_vgizq - 2*w_w1_vgizq`
- Fys_pest_vgizq: `345 MPa`
- t_pest_vgizq: `12.7 mm`
- h_pest_vgizq: `110 mm`
- c_pest_vgizq: `25 mm`
- l_w1_vgizq: `65.95 mm`
- Fexx_w1_vgizq: `490 MPa`
- w_w1_vgizq: `9.53 mm`
- nl_w1_vgizq: `2`
- kds_w1_vgizq: `1`
- Ru_w1_p+_vgizq: `481.96 kN`
- phi*Rn_w1_p+_vgizq: `195.86 kN`
- DCR_w1_p+_vgizq: `2.46`
- Resultado: `🔴 No cumple`

## Paso 11 - Revision de Resistencia soldadura #1 (platina extremo vg_der - rigidizador vg_der)

### 11.1. Revision de capacidad a traccion (vg_der)

#### 11.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w1_p+_vgder = Fys_pest_vgder * t_pest_vgder * h_pest_vgder; l_w1_vgder = h_pest_vgder - c_pest_vgder - 2*w_w1_vgder; phi*Rn_w1_p+_vgder = phi * kds_w1_vgder * nl_w1_vgder * 0.6 * Fexx_w1_vgder * 0.707 * l_w1_vgder * w_w1_vgder; DCR_w1_p+_vgder = Ru_w1_p+_vgder / phi*Rn_w1_p+_vgder (AISC 360-22 J2.4)`
- tipo_w1_vgder: `fillet`
- phi usado: `0.75`
- l_w1_vgder (longitud soldadura calculada): `l_w1_vgder = h_pest_vgder - c_pest_vgder - 2*w_w1_vgder`
- Fys_pest_vgder: `345 MPa`
- t_pest_vgder: `12.7 mm`
- h_pest_vgder: `110 mm`
- c_pest_vgder: `25 mm`
- l_w1_vgder: `65.95 mm`
- Fexx_w1_vgder: `490 MPa`
- w_w1_vgder: `9.53 mm`
- nl_w1_vgder: `2`
- kds_w1_vgder: `1`
- Ru_w1_p+_vgder: `481.96 kN`
- phi*Rn_w1_p+_vgder: `195.86 kN`
- DCR_w1_p+_vgder: `2.46`
- Resultado: `🔴 No cumple`

## Paso 12 - Revision de Resistencia soldadura #2 (viga vg_izq - rigidizador vg_izq)

### 12.1. Revision de capacidad a cortante (vg_izq)

#### 12.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w2_v2_vgizq = Fys_pest_vgizq * 0.6 * t_pest_vgizq * l_w2_vgizq; l_w2_vgizq = L_pest_vgizq - c_pest_vgizq - 2*w_w2_vgizq; phi*Rn_w2_v2_vgizq = phi * kds_w2_vgizq * nl_w2_vgizq * 0.6 * Fexx_w2_vgizq * 0.707 * l_w2_vgizq * w_w2_vgizq; DCR_w2_v2_vgizq = Ru_w2_v2_vgizq / phi*Rn_w2_v2_vgizq (AISC 360-22W J2b(g))`
- tipo_w2_vgizq: `fillet`
- phi usado: `0.75`
- l_w2_vgizq (longitud soldadura calculada): `l_w2_vgizq = L_pest_vgizq - c_pest_vgizq - 2*w_w2_vgizq`
- Fys_pest_vgizq: `345 MPa`
- t_pest_vgizq: `12.7 mm`
- h_pest_vgizq: `110 mm`
- L_pest_vgizq: `190.53 mm`
- c_pest_vgizq: `25 mm`
- l_w2_vgizq: `146.48 mm`
- Fexx_w2_vgizq: `490 MPa`
- w_w2_vgizq: `9.53 mm`
- nl_w2_vgizq: `2`
- kds_w2_vgizq: `1`
- Ru_w2_v2_vgizq: `385.07 kN`
- phi*Rn_w2_v2_vgizq: `435 kN`
- DCR_w2_v2_vgizq: `0.89`
- Resultado: `🟢 Cumple`

## Paso 13 - Revision de Resistencia soldadura #2 (viga vg_der - rigidizador vg_der)

### 13.1. Revision de capacidad a cortante (vg_der)

#### 13.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w2_v2_vgder = Fys_pest_vgder * 0.6 * t_pest_vgder * l_w2_vgder; l_w2_vgder = L_pest_vgder - c_pest_vgder - 2*w_w2_vgder; phi*Rn_w2_v2_vgder = phi * kds_w2_vgder * nl_w2_vgder * 0.6 * Fexx_w2_vgder * 0.707 * l_w2_vgder * w_w2_vgder; DCR_w2_v2_vgder = Ru_w2_v2_vgder / phi*Rn_w2_v2_vgder (AISC 360-22W J2b(g))`
- tipo_w2_vgder: `fillet`
- phi usado: `0.75`
- l_w2_vgder (longitud soldadura calculada): `l_w2_vgder = L_pest_vgder - c_pest_vgder - 2*w_w2_vgder`
- Fys_pest_vgder: `345 MPa`
- t_pest_vgder: `12.7 mm`
- h_pest_vgder: `110 mm`
- L_pest_vgder: `190.53 mm`
- c_pest_vgder: `25 mm`
- l_w2_vgder: `146.48 mm`
- Fexx_w2_vgder: `490 MPa`
- w_w2_vgder: `9.53 mm`
- nl_w2_vgder: `2`
- kds_w2_vgder: `1`
- Ru_w2_v2_vgder: `385.07 kN`
- phi*Rn_w2_v2_vgder: `435 kN`
- DCR_w2_v2_vgder: `0.89`
- Resultado: `🟢 Cumple`

## Paso 14 - Revision de Resistencia soldadura #4 (ala vg_izq - platina extremo vg_izq)

### 14.1. Revision de capacidad a traccion (vg_izq)

#### 14.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w4_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 15 - Revision de Resistencia soldadura #4 (ala vg_der - platina extremo vg_der)

### 15.1. Revision de capacidad a traccion (vg_der)

#### 15.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w4_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 16 - Revision de resistencia de la viga (vg_izq)

### 16.1. Revision de capacidad a cortante (vg_izq)

#### 16.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Ru_v2_vgizq = Vh_vgizq_max; Rn_v2_vgizq = 0.6 * Fy_vgizq * tw_vgizq * d_vgizq * Cv1; phi*Rn_v2_vgizq = phi * Rn_v2_vgizq; DCR_v2_vgizq = Ru_v2_vgizq / phi*Rn_v2_vgizq (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgizq_max: `478.84 kN`
- Fy_vgizq: `345 MPa`
- tw_vgizq: `11.2 mm`
- d_vgizq: `607 mm`
- kdes_vgizq: `30 mm`
- E_vgizq: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgizq/tw_vgizq: `48.84`
- h_vgizq: `547 mm`
- Ru_v2_vgizq: `478.84 kN`
- phi*Rn_v2_vgizq: `1407.27 kN`
- DCR_v2_vgizq: `0.34`
- Resultado: `🟢 Cumple`

## Paso 17 - Revision de resistencia de la viga (vg_der)

### 17.1. Revision de capacidad a cortante (vg_der)

#### 17.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Ru_v2_vgder = Vh_vgder_max; Rn_v2_vgder = 0.6 * Fy_vgder * tw_vgder * d_vgder * Cv1; phi*Rn_v2_vgder = phi * Rn_v2_vgder; DCR_v2_vgder = Ru_v2_vgder / phi*Rn_v2_vgder (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgder_max: `419.62 kN`
- Fy_vgder: `345 MPa`
- tw_vgder: `10.9 mm`
- d_vgder: `536 mm`
- kdes_vgder: `30.2 mm`
- E_vgder: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgder/tw_vgder: `43.63`
- h_vgder: `475.6 mm`
- Ru_v2_vgder: `419.62 kN`
- phi*Rn_v2_vgder: `1209.38 kN`
- DCR_v2_vgder: `0.35`
- Resultado: `🟢 Cumple`

## Paso 18 - Revision de Resistencia soldadura #3 (viga alma vg_izq - platina extremo vg_izq)

### 18.1 Revision capacidad a traccion (vg_izq)

#### 18.1.1 ELR #1: Rotura de soldadura (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq; hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm; phi*Rn_w3_p+_vgizq = phi * kds_w3_vgizq * nl_w3_vgizq * 0.6 * Fexx_w3_vgizq * 0.707 * hwef_w3_vgizq * t_w3_vgizq; DCR_w3_p+_vgizq = Ru_w3_p+_vgizq / phi*Rn_w3_p+_vgizq`
- tipo_w3_vgizq: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 19 - Revision de Resistencia soldadura #3 (viga alma vg_der - platina extremo vg_der)

### 19.1 Revision capacidad a traccion (vg_der)

#### 19.1.1 ELR #1: Rotura de soldadura (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w3_p+_vgder = Fy_vgder * tw_vgder * hwef_w3_vgder; hwef_w3_vgder = pfi_pe_vgder + pb_pe_vgder + 150 mm; phi*Rn_w3_p+_vgder = phi * kds_w3_vgder * nl_w3_vgder * 0.6 * Fexx_w3_vgder * 0.707 * hwef_w3_vgder * t_w3_vgder; DCR_w3_p+_vgder = Ru_w3_p+_vgder / phi*Rn_w3_p+_vgder`
- tipo_w3_vgder: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 20 - Revision de resistencia de la aleta de la columna

### 20.1. Revision de capacidad a flexion (vg_izq)

#### 20.1.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); phi*Rn_cf_v2_col_vgizq = phi_ductil * ((tf_col^2 * Fy_col * Y_c)/(1.11 * (d_vgizq - tf_vgizq))); DCR_cf_v2_col_vgizq = Ru_cf_v2_col_vgizq / phi*Rn_cf_v2_col_vgizq`
- phi usado: `1`
- Mf_vgizq_critico: `1534.87 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `n/a`
- z_vgizq = d_vgizq - tf_vgizq: `n/a`
- tf_col: `n/a`
- Fy_col: `345 MPa`
- Y_c usado: `8394.41 mm`
- Tabla Y_c aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_c: `n/a`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgizq)`
- s_col: `n/a`
- usar_pc_col: `no hay platinas de continuidad`
- Ru_cf_v2_col_vgizq: `n/a`
- phi*Rn_cf_v2_col_vgizq: `n/a`
- DCR_cf_v2_col_vgizq: `n/a`
- Resultado: `n/a`

Donde:

- Ecuacion Y_c: `Y_cs = bcf/2*[h1*(1/s) + h2*(1/pso) + h3*(1/psi) + h4*(1/s)] + (2/g)*[h1*(s + pb/4) + h2*(pso + 3pb/4) + h3*(psi + pb/4) + h4*(s + 3pb/4) + pb^2/2] + g`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

### 20.2. Revision de capacidad a flexion (vg_der)

#### 20.2.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); phi*Rn_cf_v2_col_vgder = phi_ductil * ((tf_col^2 * Fy_col * Y_c)/(1.11 * (d_vgder - tf_vgder))); DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado: `1`
- Mf_vgder_critico: `1534.87 kN-m`
- d_vgder: `536 mm`
- tf_vgder: `n/a`
- z_vgder = d_vgder - tf_vgder: `n/a`
- tf_col: `n/a`
- Fy_col: `345 MPa`
- Y_c usado: `8394.41 mm`
- Tabla Y_c aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_c: `n/a`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgder)`
- s_col: `n/a`
- usar_pc_col: `no hay platinas de continuidad`
- Ru_cf_v2_col_vgder: `n/a`
- phi*Rn_cf_v2_col_vgder: `n/a`
- DCR_cf_v2_col_vgder: `n/a`
- Resultado: `n/a`

Donde:

- Ecuacion Y_c: `Y_cs = bcf/2*[h1*(1/s) + h2*(1/pso) + h3*(1/psi) + h4*(1/s)] + (2/g)*[h1*(s + pb/4) + h2*(pso + 3pb/4) + h3*(psi + pb/4) + h4*(s + 3pb/4) + pb^2/2] + g`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

## Paso 21 - Revision de resistencia del alma de la columna

### 21.1. Revision de capacidad a traccion (vg_izq)

#### 21.1.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cf_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cf_v2_col_vgizq = Ru_cf_v2_col_vgizq / phi*Rn_cf_v2_col_vgizq`
- phi usado (phi_ductil): `1`
- Mf_vgizq_critico: `1534.87 kN-m`
- St_col: `762 mm`
- d_col: `400 mm`
- Ct_col: `1`
- kc_col: `51 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- tw_col: `13.5 mm`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- tpe_vgizq: `25.4 mm`
- t_w4_1_vgizq: `0 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `0 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cf_v2_col_vgizq: `2602.79 kN`
- phi*Rn_cf_v2_col_vgizq: `1742.37 kN`
- DCR_cf_v2_col_vgizq: `1.49`
- Resultado: `🔴 No cumple`

### 21.2. Revision de capacidad a compresion (vg_izq)

#### 21.2.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_eq(6.7-19/6.7-20/6.7-21); DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado: `0.75`
- Mf_vgizq_critico: `1534.87 kN-m`
- St_col: `762 mm`
- d_col (dc): `400 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `13.5 mm`
- tf_col: `24 mm`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- tpe_vgizq: `25.4 mm`
- t_w4_1_vgizq: `0 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `0 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgizq: `2602.79 kN`
- phi*Rn_cw_v2_col_vgizq: `1472.07 kN`
- DCR_cw_v2_col_vgizq: `1.77`
- Resultado: `🔴 No cumple`

#### 21.2.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgizq = max(|-Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|, |Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgizq = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgizq: `1257.41 kN-m`
- Mu3_vgder: `1542.49 kN-m`
- Pu_vgizq: `0 kN`
- Pu_vgder: `0 kN`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- termino_condicion_izq: `-2132.29 kN`
- termino_condicion_der: `-2974.33 kN`
- tolerancia_condicion: `1e-9`
- same_sign: `True`
- St_col: `762 mm`
- d_col: `400 mm`
- Ct_col: `1`
- kc_col: `51 mm`
- h_col: `298 mm`
- E_col: `200000 MPa`
- Fy_col: `345 MPa`
- tw_col: `13.5 mm`
- 2w_w4_vgizq: `0 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `2132.29 kN`
- phi*Rn_cw_v2_col_vgizq: `1234.47 kN`
- DCR_cw_v2_col_vgizq: `1.73`
- Resultado: `🔴 No cumple`

### 21.3. Revision de capacidad a traccion (vg_der)

#### 21.3.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cf_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado (phi_ductil): `1`
- Mf_vgder_critico: `1234.04 kN-m`
- St_col: `762 mm`
- d_col: `400 mm`
- Ct_col: `1`
- kc_col: `51 mm`
- lb_col: `68.2 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- tw_col: `13.5 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `0 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `0 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cf_v2_col_vgder: `2379.56 kN`
- phi*Rn_cf_v2_col_vgder: `1742.84 kN`
- DCR_cf_v2_col_vgder: `1.37`
- Resultado: `🔴 No cumple`

### 21.4. Revision de capacidad a compresion (vg_der)

#### 21.4.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_eq(6.7-19/6.7-20/6.7-21); DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado: `0.75`
- Mf_vgder_critico: `1234.04 kN-m`
- St_col: `762 mm`
- d_col (dc): `400 mm`
- lb_col: `68.2 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `13.5 mm`
- tf_col: `24 mm`
- d_vgder: `536 mm`
- tf_vgder: `17.4 mm`
- tpe_vgder: `25.4 mm`
- t_w4_1_vgder: `0 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `0 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgder: `2379.56 kN`
- phi*Rn_cw_v2_col_vgder: `1472.45 kN`
- DCR_cw_v2_col_vgder: `1.62`
- Resultado: `🔴 No cumple`

#### 21.4.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgder = max(|-Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|, |Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgder = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgder: `1257.41 kN-m`
- Mu3_vgder: `n/a`
- Pu_vgder: `0 kN`
- Pu_vgder: `n/a`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- d_vgder: `n/a`
- tf_vgder: `n/a`
- termino_condicion_der: `-2974.33 kN`
- termino_condicion_der: `-2132.29 kN`
- tolerancia_condicion: `1e-9`
- same_sign: `True`
- St_col: `762 mm`
- d_col: `400 mm`
- Ct_col: `1`
- kc_col: `51 mm`
- h_col: `298 mm`
- E_col: `200000 MPa`
- Fy_col: `345 MPa`
- tw_col: `13.5 mm`
- 2w_w4_vgder: `0 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `2974.33 kN`
- phi*Rn_cw_v2_col_vgder: `1234.47 kN`
- DCR_cw_v2_col_vgder: `2.41`
- Resultado: `🔴 No cumple`
