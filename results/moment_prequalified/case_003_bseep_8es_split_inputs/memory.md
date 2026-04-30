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
- Lpz_vgder: `494.03 mm`
- Lpz_vgizq: `494.03 mm`

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
- Formula: `h1=d-0.5tf+pfo+pb; h2=d-0.5tf+pfo; h3=d-1.5tf-pfi; h4=d-1.5tf-pfi-pb; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in`
- h1_vgder: `743.35 mm`
- h2_vgder: `648.35 mm`
- h3_vgder: `531.05 mm`
- h4_vgder: `436.05 mm`
- dh_vgder: `28.57 mm`

#### 1.1.5 Nota tecnica - Altura derivada de placa de extremo

- Ambito: `END_PLATE_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `Hpe_vgizq = d_vgizq + 2*pfo_pe_vgizq + 2*de_pe_vgizq`
- Hpe_vgizq: `827 mm`

#### 1.1.6 Nota tecnica - Geometria placa de extremo de viga a izquierda

- Ambito: `END_PLATE_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 + AISC 360-22 Tabla J3.3`
- Formula: `h1=d-0.5tf+pfo+pb; h2=d-0.5tf+pfo; h3=d-1.5tf-pfi; h4=d-1.5tf-pfi-pb; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in`
- h1_vgizq: `743.35 mm`
- h2_vgizq: `648.35 mm`
- h3_vgizq: `531.05 mm`
- h4_vgizq: `436.05 mm`
- dh_vgizq: `28.57 mm`

#### 1.1.7 Nota tecnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ambito: `END_PLATE_STIFFENER_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgder = pfo_pe_vgder + pb_pe_vgder + de_pe_vgder; L_pest_vgder = h_pest_vgder/tan(30 deg); Ed_pest_vgder = 25 mm`
- h_pest_vgder: `205 mm`
- L_pest_vgder: `360 mm`
- edge_detailing (Ed_pest_vgder): `25 mm`

#### 1.1.8 Nota tecnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgizq = pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq; L_pest_vgizq = h_pest_vgizq/tan(30 deg); Ed_pest_vgizq = 25 mm`
- h_pest_vgizq: `205 mm`
- L_pest_vgizq: `360 mm`
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

### 1.2 Ambito `BEAM_IZQ`

#### Chequeo 1.2.1 - Familia de perfil de viga permitida para precalificacion (viga izquierda) (`perfil_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `perfil_vgizq in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.2 - Ancho de placa de extremo vs ancho de ala de viga (left beam) (`bp_pe_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `bp_pe_vgizq <= bf_vgizq + margin (25 mm); 270 mm <= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

#### Chequeo 1.2.3 - Separacion minima de gage de pernos (left beam) (`g_b_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `g_b_vgizq >= 3db; 140 mm >= 76.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.4 - Longitud sin conectores de cortante desde la cara de columna (left beam) (`Lnc_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Lnc_vgizq >= 1.5d_vgizq; 1500 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.5 - Criterio de despeje de viga con umbral Sc y S (left beam) (`Sc_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Sc_vgizq = St_col - pfo_vgizq - pb_vgizq; S_vgizq = 0.5*sqrt(bcf*g_vgizq); Sc_vgizq > S_vgizq => 1105.000 mm > 100.747 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.6 - Relacion luz libre/peralte por sistema de marco (left beam) (`Llb_vgizq/d_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `Llb_vgizq/d_vgizq >= 7 (SMF); 9.38 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.7 - Compacidad ancho-espesor del ala de viga (left beam) (`lambda_f_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `lambda_f_vgizq <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.8 - Compacidad ancho-espesor del alma de viga (left beam) (`lambda_w_vgizq`)

- Ambito: `BEAM_IZQ`
- Verificacion: `lambda_w_vgizq <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### 1.3 Ambito `BEAM_DER`

#### Chequeo 1.3.1 - Familia de perfil de viga permitida para precalificacion (viga derecha) (`perfil_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `perfil_vgder in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.3.2 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `bp_pe_vgder <= bf_vgder + margin (25 mm); 270 mm <= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

#### Chequeo 1.3.3 - Separacion minima de gage de pernos (right beam) (`g_b_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `g_b_vgder >= 3db; 140 mm >= 76.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.3.4 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 1.3.5 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Sc_vgder = St_col - pfo_vgder - pb_vgder; S_vgder = 0.5*sqrt(bcf*g_vgder); Sc_vgder > S_vgder => 1105.000 mm > 100.747 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 1.3.6 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Llb_vgder/d_vgder >= 7 (SMF); 9.38 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 1.3.7 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_f_vgder <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.3.8 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_w_vgder <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### 1.4 Ambito `COLUMN`

#### Chequeo 1.4.1 - Familia de perfil de columna permitida para precalificacion (`shape_col`)

- Ambito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'W18X175' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.4.2 - Peralte maximo del perfil de columna (W36/W920) (`d_col`)

- Ambito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 508 mm <= 920 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 1.4.3 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ambito: `COLUMN`
- Verificacion: `bp <= bcf; 270 mm <= 290 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.4.4 - Condicion de conexion columna-losa (`col_losa`)

- Ambito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 1.4.5 - Proyeccion de columna minima por encima de las vigas (`St_col`)

- Ambito: `COLUMN`
- Verificacion: `St_col >= pfo_pe_vgder + pb_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq + 12.5 mm; 1250.000 mm >= 217.500 mm; 1250.000 mm >= 217.500 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje superior de columna)`
- Resultado: 🟢 Cumple

#### Chequeo 1.4.6 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.4.7 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.01 adim <= 50.8 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.4.8 - Espesor individual minimo del alma de columna (`tw_col`)

- Ambito: `COLUMN`
- Verificacion: `tw_col >= (d_z + w_z)/90 con d_z=d_izq-2tf_izq, w_z=bcf_col; 22.6 mm >= 9.58 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

### 1.5 Ambito `END_PLATE_DER`

#### Chequeo 1.5.1 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ambito: `END_PLATE_DER`
- Verificacion: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [228.6 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

### 1.6 Ambito `END_PLATE_IZQ`

#### Chequeo 1.6.1 - Desigualdades explicitas de ancho de placa de extremo (left beam) (`bp_pe_vgizq`)

- Ambito: `END_PLATE_IZQ`
- Verificacion: `bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf; [min,max] = [228.6 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🔴 No cumple

### 1.7 Ambito `END_PLATE_STIFFENER_DER`

#### Chequeo 1.7.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (right beam) (`h_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder = pfo_pe_vgder + pb_pe_vgder + de_pe_vgder; 205.000 mm = 50.000 mm + 95.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.7.2 - Espesor minimo requerido del rigidizador (right beam) (`t_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `t_pest_vgder >= tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 15.9 mm >= 11.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 1.7.3 - Limite de pandeo local ancho-espesor del rigidizador (right beam) (`h_pest_vgder/t_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder/t_pest_vgder <= 0.56*sqrt(E_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 12.89 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 1.7.4 - Despeje del gage de pernos con espesor del rigidizador (right beam) (`g_b_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `g_b_vgder >= 2emin + t_pest_vgder; 140 mm >= 79.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 1.8 Ambito `END_PLATE_STIFFENER_IZQ`

#### Chequeo 1.8.1 - Altura del rigidizador derivada de la geometria de la placa de extremo (left beam) (`h_pest_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq = pfo_pe_vgizq + pb_pe_vgizq + de_pe_vgizq; 205.000 mm = 50.000 mm + 95.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.8.2 - Espesor minimo requerido del rigidizador (left beam) (`t_pest_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `t_pest_vgizq >= tw_vgizq*(Fy_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 15.9 mm >= 11.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 1.8.3 - Limite de pandeo local ancho-espesor del rigidizador (left beam) (`h_pest_vgizq/t_pest_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `h_pest_vgizq/t_pest_vgizq <= 0.56*sqrt(E_vgizq/Fy_pest_vgizq); Fy_pest_vgizq <- tipo_acero_pest_vgizq; 12.89 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 1.8.4 - Despeje del gage de pernos con espesor del rigidizador (left beam) (`g_b_vgizq`)

- Ambito: `END_PLATE_STIFFENER_IZQ`
- Verificacion: `g_b_vgizq >= 2emin + t_pest_vgizq; 140 mm >= 79.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

### 1.9 Ambito `BOLTS`

#### Chequeo 1.9.1 - El tipo de apriete del perno debe ser una categoria reconocida (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.9.2 - Los pernos deben estar pretensionados salvo que una conexion especifica permita lo contrario (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.9.3 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (`std_bolt`)

- Ambito: `BOLTS`
- Verificacion: `std_bolt in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### 1.10 Ambito `TABLE_6_1_DER`

#### Chequeo 1.10.1 - Distancia de borde en de (right beam) (`de_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `de_pe_vgder >= emin; 60 mm >= 31.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.2 - Limites de distancia en fila exterior de pernos (right beam) (`pfo_pe_vgder - pso_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pso_pe_vgder (=pfo_pe_vgder) >= emin; pfo_pe_vgder <= 51 mm; pfo_pe_vgder >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.3 - Limites de distancia en fila interior de pernos (right beam) (`pfi_pe_vgder - psi_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pfi_pe_vgder >= emin; pfi_pe_vgder <= 51 mm; pfi_pe_vgder >= 41 mm; psi_pe_vgder = pfi_pe_vgder + tf_vgder - tcp_col; psi_pe_vgder > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.4 - Separacion minima vertical entre pernos (right beam) (`pb_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pb_pe_vgder >= 3db; pb_pe_vgder <= 95.000 mm; pb_pe_vgder >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.5 - Limites de espesor del ala de viga (right beam) (`tf_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `tf_vgder in [tf_vgder_min, tf_vgder_max]; 14.29 mm <= 17.3 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.6 - Limites de ancho del ala de viga (right beam) (`bf_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `bf_vgder in [bf_vgder_min, bf_vgder_max]; 190.5 mm <= 228 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.7 - Limites de peralte de la viga conectada (right beam) (`d_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `d_vgder in [d_vgder_min, d_vgder_max]; 457.2 mm <= 607 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.8 - Limites de espesor de placa de extremo (right beam) (`tpe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `tpe_vgder in [tpe_vgder_min, tpe_vgder_max]; 19.05 mm <= 40 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.10.9 - Limites de separacion horizontal de pernos (right beam) (`g_b_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `g_b_vgder in [g_b_vgder_min, g_b_vgder_max]; 127 mm <= 140 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 1.11 Ambito `TABLE_6_1_IZQ`

#### Chequeo 1.11.1 - Distancia de borde en de (left beam) (`de_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `de_pe_vgizq >= emin; 60 mm >= 31.75 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.2 - Limites de distancia en fila exterior de pernos (left beam) (`pfo_pe_vgizq - pso_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `pso_pe_vgizq (=pfo_pe_vgizq) >= emin; pfo_pe_vgizq <= 51 mm; pfo_pe_vgizq >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.3 - Limites de distancia en fila interior de pernos (left beam) (`pfi_pe_vgizq - psi_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `pfi_pe_vgizq >= emin; pfi_pe_vgizq <= 51 mm; pfi_pe_vgizq >= 41 mm; psi_pe_vgizq = pfi_pe_vgizq + tf_vgizq - tcp_col; psi_pe_vgizq > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.4 - Separacion minima vertical entre pernos (left beam) (`pb_pe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `pb_pe_vgizq >= 3db; pb_pe_vgizq <= 95.000 mm; pb_pe_vgizq >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.5 - Limites de espesor del ala de viga (left beam) (`tf_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `tf_vgizq in [tf_vgizq_min, tf_vgizq_max]; 14.29 mm <= 17.3 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.6 - Limites de ancho del ala de viga (left beam) (`bf_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `bf_vgizq in [bf_vgizq_min, bf_vgizq_max]; 190.5 mm <= 228 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.7 - Limites de peralte de la viga conectada (left beam) (`d_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `d_vgizq in [d_vgizq_min, d_vgizq_max]; 457.2 mm <= 607 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.8 - Limites de espesor de placa de extremo (left beam) (`tpe_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `tpe_vgizq in [tpe_vgizq_min, tpe_vgizq_max]; 19.05 mm <= 40 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.11.9 - Limites de separacion horizontal de pernos (left beam) (`g_b_vgizq`)

- Ambito: `TABLE_6_1_IZQ`
- Verificacion: `g_b_vgizq in [g_b_vgizq_min, g_b_vgizq_max]; 127 mm <= 140 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

### 1.12 Ambito `WELD_1_VGDER`

#### Chequeo 1.12.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w1_vgder`)

- Ambito: `WELD_1_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w1_vgder == cjp; t_pest_vgder = 15.900 mm; tipo_w1_vgder = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 1.13 Ambito `WELD_1_VGIZQ`

#### Chequeo 1.13.1 - Tipo de soldadura de placa de extremo con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w1_vgizq`)

- Ambito: `WELD_1_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w1_vgizq == cjp; t_pest_vgizq = 15.900 mm; tipo_w1_vgizq = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 1.14 Ambito `WELD_2_VGDER`

#### Chequeo 1.14.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga derecha) (`tipo_w2_vgder`)

- Ambito: `WELD_2_VGDER`
- Verificacion: `si t_pest_vgder > 10.000 mm: tipo_w2_vgder == cjp; t_pest_vgder = 15.900 mm; tipo_w2_vgder = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 1.15 Ambito `WELD_2_VGIZQ`

#### Chequeo 1.15.1 - Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga izquierda) (`tipo_w2_vgizq`)

- Ambito: `WELD_2_VGIZQ`
- Verificacion: `si t_pest_vgizq > 10.000 mm: tipo_w2_vgizq == cjp; t_pest_vgizq = 15.900 mm; tipo_w2_vgizq = cjp`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7 (item 6)`
- Resultado: 🟢 Cumple

### 1.16 Ambito `WELD_3_VGDER`

#### Chequeo 1.16.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (right beam) (`weld_ep_web_vgder`)

- Ambito: `WELD_3_VGDER`
- Verificacion: `weld_ep_web_vgder in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 1.17 Ambito `WELD_3_VGIZQ`

#### Chequeo 1.17.1 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (left beam) (`weld_ep_web_vgizq`)

- Ambito: `WELD_3_VGIZQ`
- Verificacion: `weld_ep_web_vgizq in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

### 1.18 Ambito `WELD_4_VGDER`

#### Chequeo 1.18.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha) (`tipo_w4_vgder`)

- Ambito: `WELD_4_VGDER`
- Verificacion: `si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 0 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 8.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🔴 No cumple

### 1.19 Ambito `WELD_4_VGIZQ`

#### Chequeo 1.19.1 - Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda) (`tipo_w4_vgizq`)

- Ambito: `WELD_4_VGIZQ`
- Verificacion: `si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 0 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 8.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🔴 No cumple

### 1.20 Ambito `WELD_5_COL`

#### Chequeo 1.20.1 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`weld_cp`)

- Ambito: `WELD_5_COL`
- Verificacion: `weld_cp in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 1.20.2 - Tipo de soldadura de platina de continuidad cuando el espesor es menor o igual a 10 mm (`weld_cp`)

- Ambito: `WELD_5_COL`
- Verificacion: `weld_cp in {cjp, pjp} => cumple siempre; tcp=15.9 mm; weld_cp='cjp'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

### 1.21 Ambito `DOUBLER_PLATE_COL`

#### Chequeo 1.21.1 - Espesor individual minimo de doubler plate (`tdp_col`)

- Ambito: `DOUBLER_PLATE_COL`
- Verificacion: `No aplica: usar_dp_col = false`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w E3.6e.2`
- Resultado: 🟢 Cumple

### 1.22 Resumen de chequeos por ambito

- 🔴 `1.2` `BEAM_IZQ`: total=8, cumple=7, no_cumple=1, numerales_no_cumplen=1.2.2
- 🔴 `1.3` `BEAM_DER`: total=8, cumple=7, no_cumple=1, numerales_no_cumplen=1.3.2
- 🟢 `1.4` `COLUMN`: total=8, cumple=8, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `1.5` `END_PLATE_DER`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=1.5.1
- 🔴 `1.6` `END_PLATE_IZQ`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=1.6.1
- 🟢 `1.7` `END_PLATE_STIFFENER_DER`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.8` `END_PLATE_STIFFENER_IZQ`: total=4, cumple=4, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.9` `BOLTS`: total=3, cumple=3, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.10` `TABLE_6_1_DER`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.11` `TABLE_6_1_IZQ`: total=9, cumple=9, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.12` `WELD_1_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.13` `WELD_1_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.14` `WELD_2_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.15` `WELD_2_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.16` `WELD_3_VGDER`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.17` `WELD_3_VGIZQ`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno
- 🔴 `1.18` `WELD_4_VGDER`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=1.18.1
- 🔴 `1.19` `WELD_4_VGIZQ`: total=1, cumple=0, no_cumple=1, numerales_no_cumplen=1.19.1
- 🟢 `1.20` `WELD_5_COL`: total=2, cumple=2, no_cumple=0, numerales_no_cumplen=ninguno
- 🟢 `1.21` `DOUBLER_PLATE_COL`: total=1, cumple=1, no_cumple=0, numerales_no_cumplen=ninguno

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
- Ze_vgder (catalogo): `3280000 mm3`
- Demanda de ductilidad_vgder: `high`
- Cpr_vgder: `1.15`
- Mpr_vgder: `1431.47 kN-m`

## Paso 3 - Distancia de rotula plastica desde la cara de la columna (Sh)

### 3.1 Calculo de Sh para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuacion: `Sh_vgizq = min(d_vgizq/2, 3*bf_vgizq) [4E] o Sh_vgizq = L_pest_vgizq + tpe_vgizq [4ES/8ES]`
- d_vgizq: `607 mm`
- bf_vgizq: `228 mm`
- Sh_vgizq: `400 mm`

### 3.2 Calculo de Sh para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`
- d_vgder: `607 mm`
- bf_vgder: `228 mm`
- Sh_vgder: `400 mm`

## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.

### 4.1 Calculo de cortante probable para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgizq_max = 2*Mpr_vgizq/Llb_vgizq + Vg_vgizq; Vh_vgizq_min = 2*Mpr_vgizq/Llb_vgizq - Vg_vgizq`
- Mpr_vgizq: `1431.47 kN-m`
- Llb_vgizq: `5691 mm`
- Vg_vgizq: `91.43 kN`
- Vh_vgizq_max: `594.5 kN`
- Vh_vgizq_min: `411.64 kN`
- Vhmax_vgizq adoptado: `594.5 kN`

### 4.2 Calculo de cortante probable para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgder_max = 2*Mpr_vgder/Llb_vgder + Vg_vgder; Vh_vgder_min = 2*Mpr_vgder/Llb_vgder - Vg_vgder`
- Mpr_vgder: `1431.47 kN-m`
- Llb_vgder: `5691 mm`
- Vg_vgder: `91.43 kN`
- Vh_vgder_max: `594.5 kN`
- Vh_vgder_min: `411.64 kN`
- Vhmax_vgder adoptado: `594.5 kN`

## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.

### 5.1 Calculo de momento probable en cara de columna para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgizq_max = Mpr_vgizq + Vh_vgizq_max*Sh_vgizq; Mf_vgizq_min = Mpr_vgizq + Vh_vgizq_min*Sh_vgizq`
- Mpr_vgizq: `1431.47 kN-m`
- Sh_vgizq: `400 mm`
- Mf_vgizq_max: `1669.27 kN-m`
- Mf_vgizq_min: `1596.13 kN-m`

### 5.2 Calculo de momento probable en cara de columna para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgder_max = Mpr_vgder + Vh_vgder_max*Sh_vgder; Mf_vgder_min = Mpr_vgder + Vh_vgder_min*Sh_vgder`
- Mpr_vgder: `1431.47 kN-m`
- Sh_vgder: `400 mm`
- Mf_vgder_max: `1669.27 kN-m`
- Mf_vgder_min: `1596.13 kN-m`

## Paso 6 - Revision De Resistencia Pernos (vg_izq)

### 6.1 Revision de capacidad a traccion (vg_izq)

#### 6.1.1 Estado #1: Rotura en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq + h3_pe_vgizq + h4_pe_vgizq)); phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1669.27 kN-m`
- h1_pe_vgizq: `743.35 mm`
- h2_pe_vgizq: `648.35 mm`
- h3_pe_vgizq: `531.05 mm`
- h4_pe_vgizq: `436.05 mm`
- A_b_vgizq: `506.71 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_p+_vgizq: `353.84 kN`
- phi*Rn_b_p+_vgizq: `355.71 kN`
- DCR_b_p+_vgizq: `0.99`
- Resultado: `🟢 Cumple`

### 6.2 Revision de capacidad a cortante (vg_izq)

#### 6.2.1 ELR #2: Rotura por cortante en el perno (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgizq_critico: `594.5 kN`
- n_b_vgizq: `8`
- A_b_vgizq: `506.71 mm2`
- Fnt_b_vgizq: `780 MPa`
- Ru_b_v2_vgizq: `74.31 kN`
- phi*Rn_b_v2_vgizq: `214.34 kN`
- DCR_b_v2_vgizq: `0.35`
- Resultado: `🟢 Cumple`

## Paso 7 - Revision De Resistencia Pernos (vg_der)

### 7.1 Revision de capacidad a traccion (vg_der)

#### 7.1.1 Estado #1: Rotura en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder + h3_pe_vgder + h4_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgder_critico: `1669.27 kN-m`
- h1_pe_vgder: `743.35 mm`
- h2_pe_vgder: `648.35 mm`
- h3_pe_vgder: `531.05 mm`
- h4_pe_vgder: `436.05 mm`
- A_b_vgder: `506.71 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_p+_vgder: `353.84 kN`
- phi*Rn_b_p+_vgder: `355.71 kN`
- DCR_b_p+_vgder: `0.99`
- Resultado: `🟢 Cumple`

### 7.2 Revision de capacidad a cortante (vg_der)

#### 7.2.1 ELR #2: Rotura por cortante en el perno (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgder_critico: `594.5 kN`
- n_b_vgder: `8`
- A_b_vgder: `506.71 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_v2_vgder: `74.31 kN`
- phi*Rn_b_v2_vgder: `214.34 kN`
- DCR_b_v2_vgder: `0.35`
- Resultado: `🟢 Cumple`

## Paso 8 - Revision de resistencia platina extremo (vg_izq)

### 8.1. Revision de capacidad a flexion (vg_izq)

#### 8.1.1. ELR #1: Fluencia (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgizq = Mf_vgizq_critico; phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mf_vgizq_critico: `1669.27 kN-m`
- tpe_vgizq: `40 mm`
- Fyp_pe_vgizq: `345 MPa`
- Yp_pe_vgizq: `8516.42 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgizq: `97.21 mm`
- pfi_pe_vgizq_entrada: `50 mm`
- pfi_pe_vgizq_efectivo: `50 mm`
- Ru_pe_m3_vgizq: `1669.27 kN-m`
- phi*Rn_pe_m3_vgizq: `4230.96 kN-m`
- DCR_pe_m3_vgizq: `0.39`
- Resultado: `🟢 Cumple`

### 8.2. Revision de capacidad a cortante perpendicular al plano de la platina (vg_izq)

#### 8.2.1. ELR #1: Fluencia por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Ru_pe_v1_vgizq = Mf_vgizq_critico / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v1_vgizq = phi * 0.6 * Fyp_pe_vgizq * bpe_vgizq * tpe_vgizq (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.9`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `270 mm`
- tpe_vgizq: `40 mm`
- Fyp_pe_vgizq: `345 MPa`
- Mf_vgizq_critico: `1669.27 kN-m`
- Ru_pe_v1_vgizq: `1415.36 kN`
- phi*Rn_pe_v1_vgizq: `2012.04 kN`
- DCR_pe_v1_vgizq: `0.7`
- Resultado: `🟢 Cumple`

#### 8.2.2. ELR #2: Rotura por cortante (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgizq = Ru_pe_m3_vgizq / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v2_vgizq = phi * 0.6 * Fup_pe_vgizq * tpe_vgizq * (bpe_vgizq - 2*(dh_pe_vgizq + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Ru_pe_m3_vgizq: `1669.27 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- bpe_vgizq: `270 mm`
- tpe_vgizq: `40 mm`
- Fup_pe_vgizq: `450 MPa`
- dh_pe_vgizq: `28.57 mm`
- Rn_pe_v2_vgizq: `1415.36 kN`
- phi*Rn_pe_v2_vgizq: `2037.8 kN`
- DCR_pe_v2_vgizq: `0.69`
- Resultado: `🟢 Cumple`

### 8.3. Revision de capacidad a cortante paralelo al plano de la platina (vg_izq)

#### 8.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgizq = min(pb_pe_vgizq - dh_pe_vgizq, pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq); Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 1.2 * lc_pe_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `594.5 kN`
- n_b_vgizq: `8`
- pb_pe_vgizq: `95 mm`
- pfo_pe_vgizq: `50 mm`
- pfi_pe_vgizq: `50 mm`
- tf_vgizq: `17.3 mm`
- dh_pe_vgizq: `28.57 mm`
- lc_pe_vgizq: `66.42 mm`
- tpe_vgizq: `40 mm`
- Fup_pe_vgizq: `450 MPa`
- Ru_pe_v2_vgizq: `74.31 kN`
- phi*Rn_pe_v2_vgizq: `1291.3 kN`
- DCR_pe_v2_vgizq: `0.06`
- Resultado: `🟢 Cumple`

#### 8.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_izq)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 2.4 * d_b_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgizq_critico: `594.5 kN`
- n_b_vgizq: `8`
- tpe_vgizq: `40 mm`
- Fup_pe_vgizq: `450 MPa`
- d_b_vgizq: `25.4 mm`
- Ru_pe_v2_vgizq: `74.31 kN`
- phi*Rn_pe_v2_vgizq: `987.55 kN`
- DCR_pe_v2_vgizq: `0.08`
- Resultado: `🟢 Cumple`

## Paso 9 - Revision de resistencia platina extremo (vg_der)

### 9.1. Revision de capacidad a flexion (vg_der)

#### 9.1.1. ELR #1: Fluencia (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mf_vgder_critico: `1669.27 kN-m`
- tpe_vgder: `40 mm`
- Fyp_pe_vgder: `345 MPa`
- Yp_pe_vgder: `8516.42 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgder: `97.21 mm`
- pfi_pe_vgder_entrada: `50 mm`
- pfi_pe_vgder_efectivo: `50 mm`
- Ru_pe_m3_vgder: `1669.27 kN-m`
- phi*Rn_pe_m3_vgder: `4230.96 kN-m`
- DCR_pe_m3_vgder: `0.39`
- Resultado: `🟢 Cumple`

### 9.2. Revision de capacidad a cortante perpendicular al plano de la platina (vg_der)

#### 9.2.1. ELR #1: Fluencia por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Ru_pe_v1_vgder = Mf_vgder_critico / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v1_vgder = phi * 0.6 * Fyp_pe_vgder * bpe_vgder * tpe_vgder (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.9`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `589.7 mm`
- bpe_vgder: `270 mm`
- tpe_vgder: `40 mm`
- Fyp_pe_vgder: `345 MPa`
- Mf_vgder_critico: `1669.27 kN-m`
- Ru_pe_v1_vgder: `1415.36 kN`
- phi*Rn_pe_v1_vgder: `2012.04 kN`
- DCR_pe_v1_vgder: `0.7`
- Resultado: `🟢 Cumple`

#### 9.2.2. ELR #2: Rotura por cortante (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v2_vgder = phi * 0.6 * Fup_pe_vgder * tpe_vgder * (bpe_vgder - 2*(dh_pe_vgder + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Ru_pe_m3_vgder: `1669.27 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `589.7 mm`
- bpe_vgder: `270 mm`
- tpe_vgder: `40 mm`
- Fup_pe_vgder: `450 MPa`
- dh_pe_vgder: `28.57 mm`
- Rn_pe_v2_vgder: `1415.36 kN`
- phi*Rn_pe_v2_vgder: `2037.8 kN`
- DCR_pe_v2_vgder: `0.69`
- Resultado: `🟢 Cumple`

### 9.3. Revision de capacidad a cortante paralelo al plano de la platina (vg_der)

#### 9.3.1. ELR #1: Desgarramiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgder = min(pb_pe_vgder - dh_pe_vgder, pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder); Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `594.5 kN`
- n_b_vgder: `8`
- pb_pe_vgder: `95 mm`
- pfo_pe_vgder: `50 mm`
- pfi_pe_vgder: `50 mm`
- tf_vgder: `17.3 mm`
- dh_pe_vgder: `28.57 mm`
- lc_pe_vgder: `66.42 mm`
- tpe_vgder: `40 mm`
- Fup_pe_vgder: `450 MPa`
- Ru_pe_v2_vgder: `74.31 kN`
- phi*Rn_pe_v2_vgder: `1291.3 kN`
- DCR_pe_v2_vgder: `0.06`
- Resultado: `🟢 Cumple`

#### 9.3.2. ELR #2: Aplastamiento en la perforacion del perno (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vh_vgder_critico: `594.5 kN`
- n_b_vgder: `8`
- tpe_vgder: `40 mm`
- Fup_pe_vgder: `450 MPa`
- d_b_vgder: `25.4 mm`
- Ru_pe_v2_vgder: `74.31 kN`
- phi*Rn_pe_v2_vgder: `987.55 kN`
- DCR_pe_v2_vgder: `0.08`
- Resultado: `🟢 Cumple`

## Paso 10 - Revision de Resistencia soldadura #1 (platina extremo vg_izq - rigidizador vg_izq)

### 10.1. Revision de capacidad a traccion (vg_izq)

#### 10.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w1_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 11 - Revision de Resistencia soldadura #1 (platina extremo vg_der - rigidizador vg_der)

### 11.1. Revision de capacidad a traccion (vg_der)

#### 11.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w1_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 12 - Revision de Resistencia soldadura #2 (viga vg_izq - rigidizador vg_izq)

### 12.1. Revision de capacidad a cortante (vg_izq)

#### 12.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_izq)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w2_vgizq: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`

## Paso 13 - Revision de Resistencia soldadura #2 (viga vg_der - rigidizador vg_der)

### 13.1. Revision de capacidad a cortante (vg_der)

#### 13.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4) (vg_der)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w2_vgder: `cjp`
- CJP: `Cumple`
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
- Vh_vgizq_max: `594.5 kN`
- Fy_vgizq: `345 MPa`
- tw_vgizq: `11.2 mm`
- d_vgizq: `607 mm`
- kdes_vgizq: `30 mm`
- E_vgizq: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgizq/tw_vgizq: `48.84`
- h_vgizq: `547 mm`
- Ru_v2_vgizq: `594.5 kN`
- phi*Rn_v2_vgizq: `1407.27 kN`
- DCR_v2_vgizq: `0.42`
- Resultado: `🟢 Cumple`

## Paso 17 - Revision de resistencia de la viga (vg_der)

### 17.1. Revision de capacidad a cortante (vg_der)

#### 17.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1) (vg_der)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Ru_v2_vgder = Vh_vgder_max; Rn_v2_vgder = 0.6 * Fy_vgder * tw_vgder * d_vgder * Cv1; phi*Rn_v2_vgder = phi * Rn_v2_vgder; DCR_v2_vgder = Ru_v2_vgder / phi*Rn_v2_vgder (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgder_max: `594.5 kN`
- Fy_vgder: `345 MPa`
- tw_vgder: `11.2 mm`
- d_vgder: `607 mm`
- kdes_vgder: `30 mm`
- E_vgder: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgder/tw_vgder: `48.84`
- h_vgder: `547 mm`
- Ru_v2_vgder: `594.5 kN`
- phi*Rn_v2_vgder: `1407.27 kN`
- DCR_v2_vgder: `0.42`
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
- Mf_vgizq_critico: `1669.27 kN-m`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- z_vgizq = d_vgizq - tf_vgizq: `589.7 mm`
- tf_col: `40.4 mm`
- Fy_col: `345 MPa`
- Y_c usado: `6613.41 mm`
- Tabla Y_c aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_c: `N/A`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgizq)`
- s_col: `100.75 mm`
- usar_pc_col: `no hay platinas de continuidad`
- Ru_cf_v2_col_vgizq: `2830.71 kN`
- phi*Rn_cf_v2_col_vgizq: `5689.23 kN`
- DCR_cf_v2_col_vgizq: `0.5`
- Resultado: `🟢 Cumple`

Donde:

- Ecuacion Y_c: `Y_c = bcf/2*[h1*(1/s) + h4*(1/s)] + (2/g)*[h1*(pb + c/2 + s) + h2*(pb/2 + c/4) + h3*(pb/2 + c/2) + h4*(s)] + g/2`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

### 20.2. Revision de capacidad a flexion (vg_der)

#### 20.2.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); phi*Rn_cf_v2_col_vgder = phi_ductil * ((tf_col^2 * Fy_col * Y_c)/(1.11 * (d_vgder - tf_vgder))); DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado: `1`
- Mf_vgder_critico: `1669.27 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `589.7 mm`
- tf_col: `40.4 mm`
- Fy_col: `345 MPa`
- Y_c usado: `6613.41 mm`
- Tabla Y_c aplicada: `AISC 358-22 Tabla 6.6`
- Caso Y_c: `N/A`
- Ecuacion s_col: `s_col = 0.5 * sqrt(bcf_col * g_b_vgder)`
- s_col: `100.75 mm`
- usar_pc_col: `no hay platinas de continuidad`
- Ru_cf_v2_col_vgder: `2830.71 kN`
- phi*Rn_cf_v2_col_vgder: `5689.23 kN`
- DCR_cf_v2_col_vgder: `0.5`
- Resultado: `🟢 Cumple`

Donde:

- Ecuacion Y_c: `Y_c = bcf/2*[h1*(1/s) + h4*(1/s)] + (2/g)*[h1*(pb + c/2 + s) + h2*(pb/2 + c/4) + h3*(pb/2 + c/2) + h4*(s)] + g/2`
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
- Nota: `se renderiza Y_c o Y_cs segun usar_pc_col`

## Paso 21 - Revision de resistencia del alma de la columna

### 21.1. Revision de capacidad a traccion (vg_izq)

#### 21.1.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado (phi_ductil): `1`
- Mf_vgizq_critico: `1669.27 kN-m`
- St_col: `1250 mm`
- d_col: `508 mm`
- Ct_col: `1`
- kc_col: `50.5 mm`
- lb_col: `105.3 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- tw_col: `22.6 mm`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- tpe_vgizq: `40 mm`
- t_w4_1_vgizq: `8 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `8 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `2830.71 kN`
- phi*Rn_cw_v2_col_vgizq: `3183.52 kN`
- DCR_cw_v2_col_vgizq: `0.89`
- Resultado: `🟢 Cumple`

### 21.2. Revision de capacidad a compresion (vg_izq)

#### 21.2.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; Rn_cw_v2_col_vgizq = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_cw_v2_col_vgizq; DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`
- phi usado: `0.75`
- Mf_vgizq_critico: `1669.27 kN-m`
- St_col: `1250 mm`
- d_col (dc): `508 mm`
- lb_col: `105.3 mm`
- Ecuacion lb_col: `lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `22.6 mm`
- tf_col: `40.4 mm`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- tpe_vgizq: `40 mm`
- t_w4_1_vgizq: `8 mm`
- nl_w4_vgizq: `2`
- demanda_ductilidad_vgizq: `high`
- 2w_w4_vgizq: `8 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgizq: `2830.71 kN`
- phi*Rn_cw_v2_col_vgizq: `4289.06 kN`
- DCR_cw_v2_col_vgizq: `0.66`
- Resultado: `🟢 Cumple`

#### 21.2.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgizq = max(|-Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|, |Mu3_vgizq/(d_vgizq - tf_vgizq) + Pu_vgizq|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgizq = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgizq: `0.5 kN-m`
- Mu3_vgder: `1542.49 kN-m`
- Pu_vgizq: `0 kN`
- Pu_vgder: `0 kN`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- termino_condicion_izq: `-0.85 kN`
- termino_condicion_der: `-2615.72 kN`
- tolerancia_condicion: `1e-9`
- same_sign: `True`
- St_col: `1250 mm`
- d_col: `508 mm`
- Ct_col: `1`
- kc_col: `50.5 mm`
- h_col: `407 mm`
- E_col: `200000 MPa`
- Fy_col: `345 MPa`
- tw_col: `22.6 mm`
- 2w_w4_vgizq: `8 mm`
- Ecuacion 2w_w4_vgizq: `2w = t_w4.1`
- Ru_cw_v2_col_vgizq: `0.85 kN`
- phi*Rn_cw_v2_col_vgizq: `4240.61 kN`
- DCR_cw_v2_col_vgizq: `0`
- Resultado: `🟢 Cumple`

### 21.3. Revision de capacidad a traccion (vg_der)

#### 21.3.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado (phi_ductil): `1`
- Mf_vgder_critico: `1669.27 kN-m`
- St_col: `1250 mm`
- d_col: `508 mm`
- Ct_col: `1`
- kc_col: `50.5 mm`
- lb_col: `105.3 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- tw_col: `22.6 mm`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- tpe_vgder: `40 mm`
- t_w4_1_vgder: `8 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `8 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `2830.71 kN`
- phi*Rn_cw_v2_col_vgder: `3183.52 kN`
- DCR_cw_v2_col_vgder: `0.89`
- Resultado: `🟢 Cumple`

### 21.4. Revision de capacidad a compresion (vg_der)

#### 21.4.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; Rn_cw_v2_col_vgder = 0.80*tw_col^2 * [1 + 3*(lb_col/d_col)*(tw_col/tf_col)^1.5] * sqrt(E_col*Fy_col*tf_col/tw_col) [Eq. 6.7-19]; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_cw_v2_col_vgder; DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado: `0.75`
- Mf_vgder_critico: `1669.27 kN-m`
- St_col: `1250 mm`
- d_col (dc): `508 mm`
- lb_col: `105.3 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
- tw_col: `22.6 mm`
- tf_col: `40.4 mm`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- tpe_vgder: `40 mm`
- t_w4_1_vgder: `8 mm`
- nl_w4_vgder: `2`
- demanda_ductilidad_vgder: `high`
- 2w_w4_vgder: `8 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ecuacion Rn aplicada: `eq_6_7_19`
- Ru_cw_v2_col_vgder: `2830.71 kN`
- phi*Rn_cw_v2_col_vgder: `4289.06 kN`
- DCR_cw_v2_col_vgder: `0.66`
- Resultado: `🟢 Cumple`

#### 21.4.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder y F_right = -Mu3_vgizq/(d_vgizq - tf_vgizq) + 0.5*Pu_vgizq; Ru_cw_v2_col_vgder = max(|-Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|, |Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgder = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `True`
- phi usado: `0.75`
- Mu3_vgder: `1542.49 kN-m`
- Mu3_vgizq: `0.5 kN-m`
- Pu_vgder: `0 kN`
- Pu_vgizq: `0 kN`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- d_vgizq: `607 mm`
- tf_vgizq: `17.3 mm`
- termino_condicion_der: `-2615.72 kN`
- termino_condicion_izq: `-0.85 kN`
- tolerancia_condicion: `1e-9`
- same_sign: `True`
- St_col: `1250 mm`
- d_col: `508 mm`
- Ct_col: `1`
- kc_col: `50.5 mm`
- h_col: `407 mm`
- E_col: `200000 MPa`
- Fy_col: `345 MPa`
- tw_col: `22.6 mm`
- 2w_w4_vgder: `8 mm`
- Ecuacion 2w_w4_vgder: `2w = t_w4.1`
- Ru_cw_v2_col_vgder: `2615.72 kN`
- phi*Rn_cw_v2_col_vgder: `4240.61 kN`
- DCR_cw_v2_col_vgder: `0.62`
- Resultado: `🟢 Cumple`

### 21.5. Revision de capacidad a cortante (col)

#### 21.5.1. ELR #1: Cortante en la zona del panel del alma (WPZS)

- Clausula: `Documento: AISC 360-22w | Seccion: AISC 360-22w Seccion J10.6 + Eq. (J10-9) to Eq. (J10-12)`
- Ecuacion: `Rn_wpz_v2_col = 0.60*Fy_col*d_col*tw_col (J10-9)`
- Considera deformacion inelastica del panel zone: `No`
- phi_ductil (usado en WPZS): `1`
- hb_col: `1250 mm`
- ht_col: `1250 mm`
- Mbe_col_vgizq_max: `1820.27 kN-m`
- Mbe_col_vgizq_min: `1700.68 kN-m`
- Mbe_col_vgder_max: `1820.27 kN-m`
- Mbe_col_vgder_min: `1700.68 kN-m`
- sum_Mbe_col: `3520.96 kN-m`
- Vc2_col: `1408.38 kN`
- d_vgizq: `607 mm`
- Mf_vgizq_max: `1669.27 kN-m`
- Mf_vgizq_min: `1596.13 kN-m`
- d_vgder: `607 mm`
- Mf_vgder_max: `1669.27 kN-m`
- Mf_vgder_min: `1596.13 kN-m`
- sum_Mf_col/(db-tf): `5537.39 kN`
- Ru_wpz_v2_col: `4129.01 kN`
- Pr_col: `1173.33 kN`
- Py_col: `11454 kN`
- alphaPr/Py: `0.1`
- Ag_col: `33200 mm2`
- Fy_col: `345 MPa`
- d_col: `508 mm`
- tw_col: `22.6 mm`
- bcf_col: `290 mm`
- tcf_col: `40.4 mm`
- Rn_wpz_v2_col: `2376.53 kN`
- DCR_wpz_v2_col: `1.74`
- Resultado: `🔴 No cumple`
