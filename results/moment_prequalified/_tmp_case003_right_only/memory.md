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

#### 1.1.5 Nota tecnica - Geometria derivada del rigidizador de placa de extremo y requisito de borde

- Ambito: `END_PLATE_STIFFENER_DER`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Formula: `h_pest_vgder = pfo_pe_vgder + de_pe_vgder; L_pest_vgder = h_pest_vgder/tan(30 deg); Ed_pest_vgder = 25 mm`
- h_pest_vgder: `110 mm`
- L_pest_vgder: `190.53 mm`
- edge_detailing (Ed_pest_vgder): `25 mm`

#### 1.1.6 Nota tecnica - Secuencia de soldadura para conexiones placa de extremo rigidizadas

- Ambito: `WELDS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Requisito: `Para conexiones placa de extremo rigidizadas, la soldadura entre el ala de la viga y la placa de extremo debe ejecutarse antes de instalar el rigidizador.`

#### 1.1.7 Nota tecnica - Excepcion de respaldo en la raiz cerca del alma de la viga

- Ambito: `WELDS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Requisito: `No se requiere respaldo en la raiz del ala, directamente por encima y por debajo del alma de la viga, en una longitud igual a 1.5k1. En esa ubicacion se permite una soldadura de ranura PJP de profundidad completa.`

#### 1.1.8 Nota tecnica - Requisitos de instalacion para conjuntos empernados

- Ambito: `BOLTS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.2`
- Requisito: `Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.`

#### 1.1.9 Nota tecnica - Control y aseguramiento de calidad para conjuntos empernados

- Ambito: `BOLTS`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.3`
- Requisito: `El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.`

### 1.2 Revisiones de propiedades geometricas

#### Chequeo 1.2.1 - Familia de perfil de viga permitida para precalificacion (viga derecha) (`perfil_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `perfil_vgder in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.2 - Ancho de placa de extremo vs ancho de ala de viga (right beam) (`bp_pe_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `bp_pe_vgder >= bf_vgder + margin (25 mm); 253 mm >= 253 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.3 - Separacion minima de gage de pernos (right beam) (`g_b_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `g_b_vgder >= 3db; 140 mm >= 85.72 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.4 - Longitud sin conectores de cortante desde la cara de columna (right beam) (`Lnc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Lnc_vgder >= 1.5d_vgder; 1000 mm >= 910.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (2)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.5 - Criterio de despeje de viga con umbral Sc y S (right beam) (`Sc_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Sc = St_col - pfo - pb; S = 0.5*sqrt(bcf*g); Sc_vgder > S => 617.004 mm > 100.747 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje de viga)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.6 - Relacion luz libre/peralte por sistema de marco (right beam) (`Llb_vgder/d_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `Llb_vgder/d_vgder >= 7 (SMF); 10.04 adim >= 7 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (5)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.7 - Compacidad ancho-espesor del ala de viga (right beam) (`lambda_f_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_f_vgder <= lambda_f_limit; 6.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.8 - Compacidad ancho-espesor del alma de viga (right beam) (`lambda_w_vgder`)

- Ambito: `BEAM_DER`
- Verificacion: `lambda_w_vgder <= lambda_w_limit; 48.84 adim <= 56.24 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.9 - Familia de perfil de columna permitida para precalificacion (`shape_col`)

- Ambito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'W18X175' in {W, HEA, HEB, IPE}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.10 - Peralte maximo del perfil de columna (W36/W920) (`d_col`)

- Ambito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 508 mm <= 920 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.11 - Ajuste de placa de extremo dentro del ala de la columna (`bp`)

- Ambito: `COLUMN`
- Verificacion: `bp <= bcf; 253 mm <= 290 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.12 - Condicion de conexion columna-losa (`col_losa`)

- Ambito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 2.3.4 (3)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.13 - Proyeccion de columna minima por encima de las vigas (`St_col`)

- Ambito: `COLUMN`
- Verificacion: `St_col >= pfo_pe_vgder + pb_pe_vgder + de_pe_vgder + 12.5 mm; 762 mm >= 217.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3.1 (criterio de despeje superior de columna)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.14 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.59 adim <= 6.89 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.15 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.01 adim <= 53.01 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: AISC 341-22w / AISC 358-22w Seccion 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.16 - Desigualdades explicitas de ancho de placa de extremo (right beam) (`bp_pe_vgder`)

- Ambito: `END_PLATE_DER`
- Verificacion: `bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf; [min,max] = [228.6 mm, 253 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 / Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.17 - Altura del rigidizador derivada de la geometria de la placa de extremo (right beam) (`h_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder = pfo_pe_vgder + de_pe_vgder; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.18 - Espesor minimo requerido del rigidizador (right beam) (`t_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `t_pest_vgder >= tw_vgder*(Fy_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 12.7 mm >= 11.2 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.19 - Limite de pandeo local ancho-espesor del rigidizador (right beam) (`h_pest_vgder/t_pest_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `h_pest_vgder/t_pest_vgder <= 0.56*sqrt(E_vgder/Fy_pest_vgder); Fy_pest_vgder <- tipo_acero_pest_vgder; 8.66 adim <= 13.48 adim`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.20 - Despeje del gage de pernos con espesor del rigidizador (right beam) (`g_b_vgder`)

- Ambito: `END_PLATE_STIFFENER_DER`
- Verificacion: `g_b_vgder >= 2emin + t_pest_vgder; 140 mm >= 88.9 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (stiffened) + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.21 - El tipo de soldadura entre placa de extremo y alma de viga debe ser permitido (`weld_ep_web`)

- Ambito: `WELDS`
- Verificacion: `weld_ep_web in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.22 - Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha) (`tipo_w4_vgder`)

- Ambito: `WELDS_DER`
- Verificacion: `si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 0 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 0.000 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.7`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.23 - El tipo de soldadura de platina de continuidad debe declararse y ser permitido (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.24 - Tipo de soldadura de platina de continuidad cuando el espesor es menor o igual a 10 mm (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {cjp, pjp} => cumple siempre; tcp=15.9 mm; weld_cp='cjp'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 6.3 (detalle de soldadura de platina de continuidad)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.25 - El tipo de apriete del perno debe ser una categoria reconocida (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.26 - Los pernos deben estar pretensionados salvo que una conexion especifica permita lo contrario (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.27 - La norma de fabricacion de pernos debe ser una designacion ASTM de alta resistencia permitida (`std_bolt`)

- Ambito: `BOLTS`
- Verificacion: `std_bolt in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Documento: AISC 358-22 | Seccion: Seccion 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.28 - Distancia de borde en de (right beam) (`de_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `de_pe_vgder >= emin; 60 mm >= 38.1 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.29 - Limites de distancia en fila exterior de pernos (right beam) (`pfo_pe_vgder - pso_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pso_pe_vgder (=pfo_pe_vgder) >= emin; pfo_pe_vgder <= 51 mm; pfo_pe_vgder >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.30 - Limites de distancia en fila interior de pernos (right beam) (`pfi_pe_vgder - psi_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pfi_pe_vgder >= emin; pfi_pe_vgder <= 51 mm; pfi_pe_vgder >= 41 mm; psi_pe_vgder = pfi_pe_vgder + tf_vgder - tcp_col; psi_pe_vgder > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 + AISC 360 Tabla J3.4`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.31 - Separacion minima vertical entre pernos (right beam) (`pb_pe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `pb_pe_vgder >= 3db; pb_pe_vgder <= 95.000 mm; pb_pe_vgder >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.32 - Limites de espesor del ala de viga (right beam) (`tf_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `tf_vgder in [tf_vgder_min, tf_vgder_max]; 14.29 mm <= 17.3 mm <= 25.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.33 - Limites de ancho del ala de viga (right beam) (`bf_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `bf_vgder in [bf_vgder_min, bf_vgder_max]; 190.5 mm <= 228 mm <= 311.15 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.34 - Limites de peralte de la viga conectada (right beam) (`d_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `d_vgder in [d_vgder_min, d_vgder_max]; 457.2 mm <= 607 mm <= 914.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.35 - Limites de espesor de placa de extremo (right beam) (`tpe_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `tpe_vgder in [tpe_vgder_min, tpe_vgder_max]; 19.05 mm <= 25.4 mm <= 63.5 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

#### Chequeo 1.2.36 - Limites de separacion horizontal de pernos (right beam) (`g_b_vgder`)

- Ambito: `TABLE_6_1_DER`
- Verificacion: `g_b_vgder in [g_b_vgder_min, g_b_vgder_max]; 127 mm <= 140 mm <= 152.4 mm`
- Clausula: `Documento: AISC 358-22 | Seccion: Tabla 6.1`
- Resultado: 🟢 Cumple

## Paso 2 - Momento probable maximo en rotula plastica (Mpr)

Calculo de momento probable por lado usando `Mpr = Cpr * Ry * Fy * Ze` (Ze = Zx del catalogo).

### 2.1 Calculo de Mpr para viga izquierda

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr_vgizq = Cpr_vgizq * Ry * Fy * Ze_vgizq`
- Fy_vgizq: `345 MPa`
- Ry: `1.1`
- Ze_vgizq (catalogo): `n/a`
- Demanda de ductilidad_vgizq: `n/a`
- Cpr_vgizq: `n/a`
- Mpr_vgizq: `n/a`

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
- d_vgizq: `n/a`
- bf_vgizq: `n/a`
- Sh_vgizq: `n/a`

### 3.2 Calculo de Sh para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Tipo de conexion: `bseep_8es`
- Ecuacion: `Sh_vgder = min(d_vgder/2, 3*bf_vgder) [4E] o Sh_vgder = L_pest_vgder + tpe_vgder [4ES/8ES]`
- d_vgder: `607 mm`
- bf_vgder: `228 mm`
- Sh_vgder: `215.93 mm`

- Lado gobernante Sh: `der`
- Sh adoptado (gobernante): `215.93 mm`

## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Llb + Vg` y `Vhmin = 2*Mpr/Llb - Vg`.

### 4.2 Calculo de cortante probable para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 4 + Eq. (2.4-3)`
- Ecuacion: `Vh_vgder_max = 2*Mpr/Llb_vgder + Vg_vgder; Vh_vgder_min = 2*Mpr/Llb_vgder - Vg_vgder`
- Mpr_vgder: `1431.47 kN-m`
- Llb_vgder: `6096 mm`
- Vg_vgder: `44.48 kN`
- Vh_vgder_max: `514.13 kN`
- Vh_vgder_min: `425.16 kN`
- Vhmax adoptado (gobernante): `514.13 kN`


## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh`.

### 5.2 Calculo de momento probable en cara de columna para viga derecha

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 5 + Eq. (2.4-4)`
- Ecuacion: `Mf_vgder_max = Mpr_vgder + Vh_vgder_max*Sh_vgder; Mf_vgder_min = Mpr_vgder + Vh_vgder_min*Sh_vgder`
- Mpr_vgder: `1431.47 kN-m`
- Sh_vgder: `215.93 mm`
- Mf_vgder_max: `1542.49 kN-m`
- Mf_vgder_min: `1523.28 kN-m`

## Paso 6 - Revision De Resistencia Pernos (vg_der)

### 6.1 Revision de capacidad a traccion

#### 6.1.1 Estado #1: Rotura en el perno

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder + h3_pe_vgder + h4_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Mf_vgder_critico: `1542.49 kN-m`
- h1_pe_vgder: `743.35 mm`
- h2_pe_vgder: `648.35 mm`
- h3_pe_vgder: `529.65 mm`
- h4_pe_vgder: `434.65 mm`
- A_b_vgder: `641.3 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_p+_vgder: `327.35 kN`
- phi*Rn_b_p+_vgder: `450.19 kN`
- DCR_b_p+_vgder: `0.73`
- Resultado: `🟢 Cumple`

### 6.1.2 Revision de capacidad a cortante

#### ELR #2: Rotura por cortante en el perno

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vh_vgder_critico: `514.13 kN`
- n_b_vgder: `8`
- A_b_vgder: `641.3 mm2`
- Fnt_b_vgder: `780 MPa`
- Ru_b_v2_vgder: `64.27 kN`
- phi*Rn_b_v2_vgder: `271.27 kN`
- DCR_b_v2_vgder: `0.24`
- Resultado: `🟢 Cumple`
## Paso 7 - Revision de resistencia platina extremo (vg_der)

### 7.1. Revision de capacidad a flexion

#### 7.1.1. ELR #1: Fluencia

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mf_vgder_critico: `1542.49 kN-m`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Yp_pe_vgder: `8214.25 mm`
- Tabla Yp aplicada: `AISC 358-22 Tabla 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s_pe_vgder: `94.1 mm`
- pfi_pe_vgder_entrada: `50 mm`
- pfi_pe_vgder_efectivo: `50 mm`
- Ru_pe_m3_vgder: `1542.49 kN-m`
- phi*Rn_pe_m3_vgder: `1645.5 kN-m`
- DCR_pe_m3_vgder: `0.94`
- Resultado: `🟢 Cumple`

### 7.2. Revision de capacidad a cortante perpendicular al plano de la platina

#### 7.2.1. ELR #1: Fluencia por cortante

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Rn_pe_v1_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v1_vgder = phi * 0.6 * Fyp_pe_vgder * bpe_vgder * tpe_vgder (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.75`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `589.7 mm`
- bpe_vgder: `253 mm`
- tpe_vgder: `25.4 mm`
- Fyp_pe_vgder: `345 MPa`
- Ru_pe_m3_vgder: `1542.49 kN-m`
- Rn_pe_v1_vgder: `1307.86 kN`
- phi*Rn_pe_v1_vgder: `997.67 kN`
- DCR_pe_v1_vgder: `1.31`
- Resultado: `🔴 No cumple`

#### 7.2.2. ELR #2: Rotura por cortante

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Rn_pe_v2_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v2_vgder = phi * 0.6 * Fup_pe_vgder * tpe_vgder * (bpe_vgder - 2*(dh_pe_vgder + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.75`
- Ru_pe_m3_vgder: `1542.49 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `17.3 mm`
- z_vgder = d_vgder - tf_vgder: `589.7 mm`
- bpe_vgder: `253 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- dh_pe_vgder: `31.75 mm`
- Rn_pe_v2_vgder: `1307.86 kN`
- phi*Rn_pe_v2_vgder: `958.23 kN`
- DCR_pe_v2_vgder: `1.36`
- Resultado: `🔴 No cumple`

### 7.3. Revision de capacidad a cortante paralelo al plano de la platina

#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `lc_pe_vgder = min(pb_pe_vgder - dh_pe_vgder, pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder); Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.75`
- Vh_vgder_critico: `514.13 kN`
- n_b_vgder: `8`
- pb_pe_vgder: `n/a`
- pfo_pe_vgder: `50 mm`
- pfi_pe_vgder: `50 mm`
- tf_vgder: `17.3 mm`
- dh_pe_vgder: `31.75 mm`
- lc_pe_vgder: `63.25 mm`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- Ru_pe_v2_vgder: `64.27 kN`
- phi*Rn_pe_v2_vgder: `650.61 kN`
- DCR_pe_v2_vgder: `0.1`
- Resultado: `🟢 Cumple`

#### 7.3.2. ELR #2: Aplastamiento en la perforacion del perno

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`
- phi usado: `0.75`
- Vh_vgder_critico: `514.13 kN`
- n_b_vgder: `8`
- tpe_vgder: `25.4 mm`
- Fup_pe_vgder: `450 MPa`
- d_b_vgder: `28.57 mm`
- Ru_pe_v2_vgder: `64.27 kN`
- phi*Rn_pe_v2_vgder: `587.9 kN`
- DCR_pe_v2_vgder: `0.11`
- Resultado: `🟢 Cumple`
## Paso 8 - Revision de Resistencia soldadura #1 (platina extremo vg_der - rigidizador vg_der)

### 8.1. Revision de capacidad a traccion

#### 8.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)

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
## Paso 9 - Revision de Resistencia soldadura #2 (viga vg_der - rigidizador vg_der)

### 9.1. Revision de capacidad a cortante

#### 9.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)

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
## Paso 10 - Revision de Resistencia soldadura #4 (ala vg_der - platina extremo vg_der)

### 10.1. Revision de capacidad a traccion

#### 10.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 + AISC 360-22 J2.4`
- Ecuacion: `CJP => cumple (AISC 360-22 J2.4)`
- tipo_w4_vgder: `cjp`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`
## Paso 11 - Revision de resistencia de la viga (vg_der)

### 11.1. Revision de capacidad a cortante

#### 11.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1)

- Clausula: `Documento: AISC 360-22 | Seccion: Capitulo 6 / Seccion 6.7.1 Paso 11.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Ru_v2_vgder = Vh_vgder_max; Rn_v2_vgder = 0.6 * Fy_vgder * tw_vgder * d_vgder * Cv1; phi*Rn_v2_vgder = phi * Rn_v2_vgder; DCR_v2_vgder = Ru_v2_vgder / phi*Rn_v2_vgder (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vh_vgder_max: `514.13 kN`
- Fy_vgder: `345 MPa`
- tw_vgder: `11.2 mm`
- d_vgder: `607 mm`
- kdes_vgder: `30 mm`
- E_vgder: `200000 MPa`
- Cv1: `1`
- kv: `5.34`
- h_vgder/tw_vgder: `48.84`
- h_vgder: `547 mm`
- Ru_v2_vgder: `514.13 kN`
- phi*Rn_v2_vgder: `1407.27 kN`
- DCR_v2_vgder: `0.37`
- Resultado: `🟢 Cumple`
## Paso 12 - Revision de Resistencia soldadura #3 (viga alma vg_der - platina extremo vg_der)

### 12.1 Revision capacidad a traccion

#### 12.1.1 ELR #1: Rotura de soldadura

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Ru_w3_p+_vgder = Fy_vgder * tw_vgder * hwef_w3_vgder; hwef_w3_vgder = pfi_pe_vgder + pb_pe_vgder + 150 mm; phi*Rn_w3_p+_vgder = phi * kds_w3_vgder * nl_w3_vgder * 0.6 * Fexx_w3_vgder * 0.707 * hwef_w3_vgder * t_w3_vgder; DCR_w3_p+_vgder = Ru_w3_p+_vgder / phi*Rn_w3_p+_vgder`
- tipo_w3_vgder: `CJP`
- CJP: `Cumple`
- Resultado: `🟢 Cumple`
## Paso 13 - Revision de resistencia de la aleta de la columna

### 13.1.1. Revision de capacidad a flexion (vg_der)

#### 13.1.1. ELR #1: Flexion local de la aleta (LFB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-13)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); phi*Rn_cf_v2_col_vgder = phi_ductil * ((tf_col^2 * Fy_col * Y_c)/(1.11 * (d_vgder - tf_vgder))); DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado: `1`
- Mf_vgder_critico: `1542.49 kN-m`
- d_vgder: `607 mm`
- tf_vgder: `n/a`
- z_vgder = d_vgder - tf_vgder: `n/a`
- tf_col: `n/a`
- Fy_col: `345 MPa`
- Y_c usado: `9355.9 mm`
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
## Paso 14 - Revision de resistencia del alma de la columna

### 14.1.1. Revision de capacidad a traccion (vg_der)

#### 14.1.1. ELR #1: Fluencia local del alma (WLY)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-17)`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cf_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col; DCR_cf_v2_col_vgder = Ru_cf_v2_col_vgder / phi*Rn_cf_v2_col_vgder`
- phi usado (phi_ductil): `1`
- Mf_vgder_critico: `1542.49 kN-m`
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
- Ru_cf_v2_col_vgder: `2615.71 kN`
- phi*Rn_cf_v2_col_vgder: `2893.47 kN`
- DCR_cf_v2_col_vgder: `0.9`
- Resultado: `🟢 Cumple`

### 14.2.1. Revision de capacidad a compresion (vg_der)

#### 14.2.1. ELR #1: Arrugamiento local del alma (WLC)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_eq(6.7-19/6.7-20/6.7-21); DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`
- phi usado: `0.75`
- Mf_vgder_critico: `1542.49 kN-m`
- St_col: `762 mm`
- d_col (dc): `508 mm`
- lb_col: `68.1 mm`
- Ecuacion lb_col: `lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder`
- Fy_col: `345 MPa`
- E_col: `200000 MPa`
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
- Ru_cw_v2_col_vgder: `2615.71 kN`
- phi*Rn_cw_v2_col_vgder: `3976.22 kN`
- DCR_cw_v2_col_vgder: `0.66`
- Resultado: `🟢 Cumple`

#### 14.2.2. ELR #2: Pandeo local del alma (WCB)

- Clausula: `Documento: AISC 358-22 | Seccion: Capitulo 6 / Seccion 6.7.2 + Eq. (6.7-18)`
- Ecuacion: `Condicion aplicabilidad: same_sign(F_left, F_right), con F_left = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder y F_right = -Mu3_vgder/(d_vgder - tf_vgder) + 0.5*Pu_vgder; Ru_cw_v2_col_vgder = max(|-Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|, |Mu3_vgder/(d_vgder - tf_vgder) + Pu_vgder|); h_col = d_col - 2*kc_col; phi*Rn_cw_v2_col_vgder = phi_wcb * Ct_col * 24 * tw_col^3 * sqrt(E_col * Fy_col) / h_col`
- Condicion aplicabilidad cumplida: `False`
- phi usado: `n/a`
- Mu3_vgder: `n/a`
- Mu3_vgder: `n/a`
- Pu_vgder: `n/a`
- Pu_vgder: `n/a`
- d_vgder: `n/a`
- tf_vgder: `n/a`
- d_vgder: `n/a`
- tf_vgder: `n/a`
- termino_condicion_der: `n/a`
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
- 2w_w4_vgder: `n/a`
- Ecuacion 2w_w4_vgder: `n/a`
- Resultado: `No aplica`
