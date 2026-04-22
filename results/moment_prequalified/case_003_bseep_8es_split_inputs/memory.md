# Memoria de Calculo

- Proyecto: `proj_bseep_si_demo`
- Caso: `case_si_bseep_8es_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bseep_8es`
- Estado global: `No cumple`

## Revision conexion viga a derecha de columna

## Paso 1 - Limites de precalificacion

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### 1.1 Notas tecnicas

#### 1.1.1 Nota tecnica - Longitud de zona protegida medida desde la cara de la columna

- Ambito: `BEAM`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (8)`
- Formula: `Lpz_vgder = min(L_pest_vgder + 0.5*d_vgder, 3*bf_vgder); Lpz_vgizq = min(L_pest_vgizq + 0.5*d_vgizq, 3*bf_vgizq)`
- Lpz_vgder: `494.03 mm`
- Lpz_vgizq: `421.53 mm`

#### 1.1.2 Nota tecnica - Ubicacion de la conexion de placa de extremo en columna

- Ambito: `COLUMN`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (2)`
- Requisito: `La placa de extremo debe conectarse al ala de la columna.`

#### 1.1.3 Nota tecnica - Altura derivada de placa de extremo

- Ambito: `END_PLATE_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `Hpe_vgder = d_vgder + 2*pfo_pe_vgder + 2*de_pe_vgder`
- Hpe_vgder: `827 mm`

#### 1.1.4 Nota tecnica - Geometria placa de extremo de viga a derecha

- Ambito: `END_PLATE_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 + AISC 360-22 Tabla J3.3`
- Formula: `h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in`
- h1_vgder: `743.35 mm`
- h2_vgder: `648.35 mm`
- h3_vgder: `529.65 mm`
- h4_vgder: `434.65 mm`
- dh_vgder: `31.75 mm`

#### 1.1.5 Nota tecnica - Altura derivada de placa de extremo

- Ambito: `END_PLATE_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `Hpe_vgizq = d_vgizq + 2*pfo_pe_vgizq + 2*de_pe_vgizq`
- Hpe_vgizq: `682 mm`

#### 1.1.6 Nota tecnica - Geometria placa de extremo de viga a izquierda

- Ambito: `END_PLATE_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 + AISC 360-22 Tabla J3.3`
- Formula: `h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in`
- h1_vgizq: `743.35 mm`
- h2_vgizq: `648.35 mm`
- h3_vgizq: `529.65 mm`
- h4_vgizq: `434.65 mm`
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

#### 1.1.9 Nota tecnica - Requisitos de soldadura entre ala de viga y placa de extremo

- Ambito: `WELDS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Requisito: `La union entre el ala de la viga y la placa de extremo debe ejecutarse con una soldadura de ranura CJP sin respaldo. La soldadura de ranura CJP debe realizarse de modo que la raiz de la soldadura quede del lado del alma de la viga respecto del ala. La cara interior del ala debe tener una soldadura de filete de c in. (8 mm). Estas soldaduras deben ser de demanda critica.`

#### 1.1.10 Nota tecnica - Secuencia de soldadura para conexiones placa de extremo rigidizadas

- Ambito: `WELDS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Requisito: `Para conexiones placa de extremo rigidizadas, la soldadura entre el ala de la viga y la placa de extremo debe ejecutarse antes de instalar el rigidizador.`

#### 1.1.11 Nota tecnica - Excepcion de respaldo en la raiz cerca del alma de la viga

- Ambito: `WELDS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Requisito: `No se requiere respaldo en la raiz del ala, directamente por encima y por debajo del alma de la viga, en una longitud igual a 1.5k1. En esa ubicacion se permite una soldadura de ranura PJP de profundidad completa.`

#### 1.1.12 Nota tecnica - Requisitos de instalacion para conjuntos empernados

- Ambito: `BOLTS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.`

#### 1.1.13 Nota tecnica - Control y aseguramiento de calidad para conjuntos empernados

- Ambito: `BOLTS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Familia de perfil de viga permitida para precalificacion (viga izquierda) (`perfil_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `perfil_vgizq in {W, HEA, HEB, IPE}; 'W18X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.2 - Familia de perfil de viga permitida para precalificacion (viga derecha) (`perfil_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `perfil_vgder in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.3 - Ancho de placa de extremo vs ancho de ala de viga (left beam) (`bp_pe_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `bp_pe_vgizq >= bf_vgizq + margin (25 mm); 253 mm >= 304 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.4 - Separacion minima de gage de pernos (left beam) (`g_b_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `g_b_vgizq >= 3db; 140 mm >= 85.72 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.5 - Longitud sin conectores de cortante desde la cara de columna (left beam) (`Lnc_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Lnc_vgizq >= 1.5d_vgizq; 1000 mm >= 693 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.6 - Criterio de despeje de viga con umbral Sc y S (left beam) (`Sc_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Sc = St_col - pfo - pb; S = 0.5*sqrt(bcf*g); Sc_vgizq > S => 617.004 mm > 100.747 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.7 - Relacion luz libre/peralte por sistema de marco (left beam) (`Llb_vgizq/d_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Llb_vgizq/d_vgizq >= 7 (SMF); 13.19 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.8 - Compacidad ancho-espesor del ala de viga (left beam) (`lambda_f_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `lambda_f_vgizq <= lambda_f_limit; 8.06 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.9 - Compacidad ancho-espesor del alma de viga (left beam) (`lambda_w_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `lambda_w_vgizq <= lambda_w_limit; 37.7 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.10 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `bp_pe_vgder >= bf_vgder + margin (25 mm); 253 mm >= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.11 - Separacion minima de gage de pernos (right beam) (`g_b_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `g_b_vgder >= 3db; 140 mm >= 85.72 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.12 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.13 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Sc = St_col - pfo - pb; S = 0.5*sqrt(bcf*g); Sc_vgder > S => 617.004 mm > 100.747 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.14 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Llb_vgder/d_vgder >= 7 (SMF); 10.04 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.15 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_f_vgder <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.16 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_w_vgder <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.17 - Familia de perfil de columna permitida para precalificacion (`shape_col`)

- Ambito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'W18X175' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.18 - Peralte maximo del perfil de columna (W36/W920) (`d_col`)

- Ambito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 508 mm <= 920 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.19 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ambito: `COLUMN`
- Verificacion: `bp <= bcf; 253 mm <= 290 mm`
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
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.23 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.01 adim <= 53.01 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.24 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ambito: `END_PLATE_DER`
- Verificacion: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [228.6 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.25 - Desigualdades explicitas de ancho de placa de extremo (left beam) (`bp_pe_vgizq`)

- Ambito: `END_PLATE_IZQ`
- Verificacion: `bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf; [min,max] = [228.6 mm, 290 mm]`
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
- Verificacion: `t_pest_vgder >= tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 12.7 mm >= 11.2 mm`
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
- Verificacion: `t_pest_vgizq >= tw_vgizq*(Fy_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 12.7 mm >= 10.8 mm`
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

#### Chequeo 1.2.35 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.36 - Tipo de soldadura de platina de continuidad cuando el espesor es menor o igual a 10 mm (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {cjp, pjp} => cumple siempre; tcp=15.9 mm; weld_cp='cjp'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.37 - El tipo de apriete del perno debe ser una categoria reconocida (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.38 - Los pernos deben estar pretensionados salvo que una conexion especifica permita lo contrario (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.39 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (`std_bolt`)

- Ambito: `BOLTS`
- Verificacion: `std_bolt in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.40 - Separacion minima vertical entre pernos (`pb`)

- Ambito: `TABLE_6_1`
- Verificacion: `pb >= 3db; pb <= 95.000 mm; pb >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.41 - Distancia de borde en de (`de`)

- Ambito: `TABLE_6_1`
- Verificacion: `de >= emin; 60 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.42 - Limites de distancia en fila exterior de pernos (`pfo - pso`)

- Ambito: `TABLE_6_1`
- Verificacion: `pso (=pfo) >= emin; pfo <= 51 mm; pfo >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.43 - Limites de distancia en fila interior de pernos (`pfi - psi`)

- Ambito: `TABLE_6_1`
- Verificacion: `pfi >= emin; pfi <= 51 mm; pfi >= 41 mm; psi = pfi + tfb - tcp; psi > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.44 - Limites de espesor del ala de viga (`tbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `tbf in [tbf_min, tbf_max]; 14.29 mm <= 17.3 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.45 - Limites de ancho del ala de viga (`bbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `bbf in [bbf_min, bbf_max]; 190.5 mm <= 228 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.46 - Limites de peralte de la viga conectada (`d`)

- Ambito: `TABLE_6_1`
- Verificacion: `d in [d_min, d_max]; 457.2 mm <= 607 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.47 - Limites de espesor de placa de extremo (`tp`)

- Ambito: `TABLE_6_1`
- Verificacion: `tp in [tp_min, tp_max]; 19.05 mm <= 25.4 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.48 - Limites de separacion horizontal de pernos (`g`)

- Ambito: `TABLE_6_1`
- Verificacion: `g in [g_min, g_max]; 127 mm <= 140 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

## Paso 2 - Momento probable maximo en rotula plastica (Mpr)

Calculo de momento probable segun Eq. (2.4-1) y Eq. (2.4-2), usando `Ze = Zx` del catalogo de la viga.

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr = Cpr * Ry * Fy * Ze (Eq. 2.4-1 and Eq. 2.4-2)`
- Fy: `345 MPa`
- Fu: `450 MPa`
- Ry: `1.1`
- Ze (catalogo): `3280000 mm3`
- Cpr: `1.15`
- Mpr calculado: `1434.18 kN-m`

## Paso 3 - Distancia de rotula plastica desde la cara de la columna (Sh)

Para 4E: `Sh = min(d/2, 3bf)`. Para 4ES/8ES: `Sh = Lst + tp`.

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Ecuacion: `Sh from connection-specific rules (Eq. 6.7-1 or Eq. 6.7-2)`
- Tipo de conexion: `bseep_8es`
- Perfil de viga: `W24X76`
- Lst (si aplica): `190.53 mm`
- tp (si aplica): `25.4 mm`
- Sh calculado: `215.93 mm`

## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Lh + Vgravity` y `Vhmin = 2*Mpr/Lh - Vgravity` (se reporta lado derecho).

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vhmax.der = 2*Mpr/Lh.der + Vgravity.der; Vhmin.der = 2*Mpr/Lh.der - Vgravity.der`
- Configuracion de vigas: `both_sides`
- Lado gobernante Vhmax: `der`
- Fuente Vhmax seleccionado: `step4_computed_vhmax_der (governing_side=der)`
- Mpr: `1434.18 kN-m`
- Lh.der: `6096 mm`
- Beam_right_Vgravity: `44.48 kN`
- 2*Mpr/Lh.der: `470.53 kN`
- Vh.dermax: `515.01 kN`
- Vh.dermin: `426.05 kN`
- Vhmax gobernante: `515.01 kN`

## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh` (se reporta lado derecho).

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mfmax.der = Mpr + Vhmax.der*Sh; Mfmin.der = Mpr + Vhmin.der*Sh`
- Definicion para diseno: `Mf = Mfmax gobernante`
- Configuracion de vigas: `both_sides`
- Lado gobernante Mfmax: `der`
- Fuente Mfmax seleccionado: `step5_computed_mf_dermax (governing_side=der)`
- Mpr (intermedio): `1434.18 kN-m`
- Sh (intermedio): `215.93 mm`
- Vh.dermax (intermedio): `515.01 kN`
- Vh.dermin (intermedio): `426.05 kN`
- Mf.dermax: `1545.38 kN-m`
- Mf.dermin: `1526.17 kN-m`
- Mf (adoptado) = Mfmax gobernante: `1545.38 kN-m`

## Paso 6 - Revision De Resistencia Pernos

### 6.1 Revision de capacidad a traccion

#### 6.1.1 Estado #1: Rotura en el perno

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Rut_b = Mf / (2*(h1 + h2 + h3 + h4)); phiRnt_b = phi * Rnt_b, Rnt_b = Ab * Fnt, Ab = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- h1: `743.35 mm`
- h2: `648.35 mm`
- h3: `529.65 mm`
- h4: `434.65 mm`
- Rut_b: `327.97 kN`
- phiRnt_b: `450.19 kN`
- DCRbt: `0.73`
- Resultado: `Cumple`

### 6.2 Revision de capacidad a cortante

#### 6.2.1 ELR #1: Rotura por cortante en el perno

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ruv2_b = Vhmax/nb, phiRnv_b = phi * Rnv_b, Rnv_b = Ab * Fnv, Ab = pi*db^2/4, nb = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vhmax: `515.01 kN`
- nb: `8`
- Ruv2_b: `64.38 kN`
- phiRnv_b: `271.27 kN`
- DCRbv: `0.24`
- Resultado: `Cumple`

## Paso 7 - Revision de resistencia end plate

### 7.1. Revision de capacidad a flexion

#### 7.1.1. ELR #1: Fluencia (AISC 358-22 .7-8)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Mup = Mf; phiMnb = phi * tp^2 * Fyp * Yp (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mup: `1545.38 kN-m`
- phiMnb: `1645.5 kN-m`
- DCRpm: `0.94`
- Yp calculado: `8214.25 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s: `94.1 mm`
- pfi de entrada: `50 mm`
- pfi efectivo: `50 mm`
- Resultado: `Cumple`

### 7.2. Revision de capacidad a cortante perpendicular al plano de la platina

#### 7.2.1. Eje #1: Fluencia por cortante (AISC 358-22 G7-10)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fyp * bp * tp (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.9`
- Vup: `1310.31 kN`
- phiVn1p: `1197.2 kN`
- DCRpv: `1.09`
- d (altura viga): `607 mm`
- Resultado: `No cumple`

#### 7.2.2. Eje #2: Rotura por cortante (AISC 358-22 G7-12)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fup * tp * (bp - 2*dh) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Vup: `1310.31 kN`
- phiVnb: `1169.63 kN`
- DCRpv: `1.12`
- dh (diametro agujero estandar): `31.75 mm`
- d (altura viga): `607 mm`
- Resultado: `No cumple`

### 7.3. Revision de capacidad a cortante paralelo al plano de la platina

#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno (AISC 360-22 J3.11a)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `Vu2p = Vhmax/nb; phiVn2p = phi * 1.2 * lc * tp * Fup (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vu2p: `64.38 kN`
- phiVn2p: `780.73 kN`
- DCRpn2: `0.08`
- lc: `63.25 mm`
- dh: `31.75 mm`
- db: `28.57 mm`
- Resultado: `Cumple`

#### 7.3.2. ELR #2: Aplastamiento en la perforacion del perno (AISC 360-22 J3.11a)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Vu2p = Vhmax/nb; phiVn2p = phi * 2.4 * (db + 1.6 mm) * tp * Fup (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vu2p: `64.38 kN`
- phiVn2p: `744.98 kN`
- DCRpn2: `0.09`
- lc: `63.25 mm`
- dh: `31.75 mm`
- db: `28.57 mm`
- Resultado: `Cumple`

## Paso 8 - Revision de Resistencia soldadura #1 (end plate con rigidizador)

### 8.1. Revision de capacidad a traccion

#### 8.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 8.1.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Pust = Fys * ts * hst; l_st = hst - clip_st - 2*w_st; phiRnst = phi * nl * 0.6 * FEXX * 0.707 * l_st * w_st (AISC 360-22 J2.4)`
- phi usado: `0.9`
- Tipo soldadura rigidizador: `fillet`
- Pust: `481.96 kN`
- phiRnst: `235.03 kN`
- DCRst,w1,t: `2.05`
- l_st (longitud soldadura calculada): `l_st = hst - clip_st - 2*w_st`
- l_st: `65.95 mm`
- clip_st: `25 mm`
- hst: `110 mm`
- w_st (espesor soldadura): `9.53 mm`
- n_l (lineas soldadura): `2`
- Resultado: `No cumple`

## Paso 9 - Revision de resistencia soldadura #2 (viga con rigidizador)

### 9.1. Revision de capacidad a cortante

#### 9.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 9.1.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Vust,w2 = Fys * 0.6 * ts * l_st,w2; l_st,w2 = Lst - clip_st - 2*w_st; phiVnst,w2 = phi * nl * 0.6 * FEXX * 0.707 * l_st,w2 * w_st (AISC 360-22W J2b(g))`
- phi usado: `0.9`
- Tipo soldadura viga-rigidizador: `fillet`
- Vust,w2: `385.07 kN`
- phiVnst,w2: `522 kN`
- DCRst,w2,v: `0.74`
- l_st,w2 (longitud soldadura calculada): `l_st,w2 = Lst - clip_st - 2*w_st`
- l_st,w2: `146.48 mm`
- Lst: `190.53 mm`
- clip_st: `25 mm`
- w_st,2 (espesor soldadura): `9.53 mm`
- n_l,w2 (lineas soldadura): `2`
- Resultado: `Cumple`

## Paso 10 - Revision de resistencia de la viga

### 10.1. Revision de capacidad a cortante

#### 10.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 10.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Vubm = Vhmax; phiVnbm = phi * 0.6 * Fybm * tw,bm * d * Cv1 (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vubm: `515.01 kN`
- phiVnbm: `1407.27 kN`
- DCRbm,v: `0.37`
- Cv1: `1`
- kv: `5.34`
- h/tw: `48.84`
- h: `547 mm`
- Resultado: `Cumple`

## Paso 11 - Revision de resistencia de soldadura viga-alma a end plate

### 11.1 Revision capacidad a traccion

#### 11.1.1 ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 + AISC 360-22 | Seccion: Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Puww3 = Fybm*tw*hwef; hwef = Pfi + Pb + 150 mm; phiPnww3 = phi*nl*0.6*Fexx*0.707*hwef*ww3; DCRww3p = Puww3/phiPnww3`
- phi usado: `0.9`
- Fuente de input: `geometry.welds.weld_3`
- Soldadura #3: `viga (alma) con end plate`
- Tipo de soldadura viga-end_plate: `CJP`
- CJP: `Cumple`
- Resultado: `Cumple`

## Paso 12 - Revision de resistencia de la aleta de la columna

### 12.1. Revision de capacidad a flexion

#### 12.1.1 ELR # 1: Flexion local de la aleta (LFB) (AISC 358-22 6.7.2)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- M_ucf: `1545.38 kN-m`
- phi usado: `1`
- Condicion aplicable: `hay platinas de continuidad`
- s: `94.1 mm`
- Y_cs usado: `6985 mm`
- Ecuacion: `phiM_ncf = phi((t_cf^2 * f_yc * Y_cs)/1.11)`
- phiM_ncf: `3543.44 kN-m`
- Ecuacion DCR: `DCR_cfm = M_ucf/(phiM_ncf)`
- DCR_cfm: `0.44`
- Resultado: `Cumple`

Donde:
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
