# Memoria de Calculo

- Proyecto: `proj_bueep_si_demo`
- Caso: `case_si_bueep_4e_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bueep_4e`
- Estado global: `PASS`

## Revision conexion viga a derecha de columna

## Paso 1 - PREQUALIFICATION LIMITS

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### Nota tecnica - Protected zone length measured from column face

- Ambito: `BEAM`
- Clausula: `Section 2.3.4 (8)`
- Formula: `Lpz = min(d, 3bf)`
- Candidato A (d): `607 mm`
- Candidato B (3bf): `684 mm`
- Alcance: `aplica para viga derecha`
- Longitud zona protegida viga derecha: `607 mm`

### Nota tecnica - End-plate connection location on column

- Ambito: `COLUMN`
- Clausula: `Section 6.3 (2)`
- Requisito: `The end plate shall be connected to the flange of the column.`

### Nota tecnica - Derived end-plate height reference

- Ambito: `END_PLATE`
- Clausula: `Section 6.3`
- Requisito: `hp = d + 2*pfo + 2*de`
- Formula: `hp = d + 2*pfo + 2*de`
- Candidato A (d): `607 mm`
- Candidato B (2*pfo + 2*de): `220 mm`
- Valor derivado: `827 mm`

### Nota tecnica - Geometria end-plate de viga a derecha

- Ambito: `END_PLATE`
- Clausula: `Section 6.3 + AISC 360-22 Table J3.3`
- Requisito: `h1_vgder, h2_vgder, h3_vgder, h4_vgder y dh_vgder para trazabilidad geometrica`
- Formula: `h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in`
- h1_vgder: `743.35 mm`
- h2_vgder: `648.35 mm`
- h3_vgder: `529.65 mm`
- h4_vgder: `434.65 mm`
- dh_vgder: `31.75 mm`

### Nota tecnica - Derived end-plate stiffener geometry and detailing edge requirement

- Ambito: `END_PLATE_STIFFENER`
- Clausula: `Section 6.3`
- Requisito: `hst = pfo + de; Lst = hst/tan(30 deg); clip_st (Cst) = 25 mm; edge detailing >= 25 mm`
- Formula: `hst = pfo + de; Lst = hst / tan(30 deg)`
- stiffener_height (hst): `110 mm`
- stiffener_widht(Lst): `190.53 mm`
- clip_st (Cst): `25 mm`
- edge detailing: `25 mm`

### Nota tecnica - Requisitos de soldadura entre ala de viga y placa de extremo

- Ambito: `WELDS`
- Clausula: `Section 6.7`
- Requisito: `La unión entre el ala de la viga y la placa de extremo debe ejecutarse con una soldadura de ranura CJP sin respaldo. La soldadura de ranura CJP debe realizarse de modo que la raíz de la soldadura quede del lado del alma de la viga respecto del ala. La cara interior del ala debe tener una soldadura de filete de c in. (8 mm). Estas soldaduras deben ser de demanda crítica.`

### Nota tecnica - Secuencia de soldadura para conexiones end-plate rigidizadas

- Ambito: `WELDS`
- Clausula: `Section 6.7`
- Requisito: `Para conexiones end-plate rigidizadas, la soldadura entre el ala de la viga y la placa de extremo debe ejecutarse antes de instalar el rigidizador.`

### Nota tecnica - Excepcion de respaldo en la raiz cerca del alma de la viga

- Ambito: `WELDS`
- Clausula: `Section 6.7`
- Requisito: `No se requiere respaldo en la raiz del ala, directamente por encima y por debajo del alma de la viga, en una longitud igual a 1.5k1. En esa ubicacion se permite una soldadura de ranura PJP de profundidad completa.`

### Nota tecnica - Installation requirements for bolted assemblies

- Ambito: `BOLTS`
- Clausula: `Section 4.2`
- Requisito: `Installation requirements shall be in accordance with the AISC Seismic Provisions and the RCSC Specification, except as otherwise specifically indicated in this standard.`

### Nota tecnica - Quality control and quality assurance for bolted assemblies

- Ambito: `BOLTS`
- Clausula: `Section 4.3`
- Requisito: `Quality control and quality assurance shall be in accordance with the AISC Seismic Provisions.`

### Chequeo 1.1 - Beam profile family allowed for prequalification (`shape_beam`)

- Ambito: `BEAM`
- Verificacion: `shape_beam in {W, HEA, HEB, IPE}; 'W24X76' in {W, HEA, HEB, IPE}`
- Clausula: `Section 2.3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.2 - End-plate width vs beam flange width (`bp`)

- Ambito: `BEAM`
- Verificacion: `bp >= bf + margin; 253 mm >= 253 mm`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.3 - Bolt gage minimum spacing (`g`)

- Ambito: `BEAM`
- Verificacion: `g >= 3db; 152.4 mm >= 85.72 mm`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.4 - Length without shear connectors from column face (`Lsc`)

- Ambito: `BEAM`
- Verificacion: `Lsc >= 1.5d; 1000 mm >= 910.5 mm`
- Clausula: `Section 2.3.4 (2)`
- Resultado: 🟢 Cumple

### Chequeo 1.5 - Beam clearance criterion using Sc and S threshold (`Sc`)

- Ambito: `BEAM`
- Verificacion: `Sc = Stc - pfo; S = 0.5*sqrt(bcf*g); Sc > S => 712.000 mm > 105.114 mm`
- Clausula: `Section 6.3.1 (beam clearance criterion)`
- Resultado: 🟢 Cumple

### Chequeo 1.6 - Clear span-to-depth ratio by frame system (`Lclear/d`)

- Ambito: `BEAM`
- Verificacion: `Lclear/d >= 7 (SMF); 10.04 ratio >= 7 ratio`
- Clausula: `Section 2.3.4 (5)`
- Resultado: 🟢 Cumple

### Chequeo 1.7 - Beam flange width-to-thickness compactness (`lambda_f_beam`)

- Ambito: `BEAM`
- Verificacion: `lambda_f_beam <= lambda_f_limit; 6.59 ratio <= 6.89 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.8 - Beam web width-to-thickness compactness (`lambda_w_beam`)

- Ambito: `BEAM`
- Verificacion: `lambda_w_beam <= lambda_w_limit; 48.84 ratio <= 56.24 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.9 - Column profile family allowed for prequalification (`shape_col`)

- Ambito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'W18X175' in {W, HEA, HEB, IPE}`
- Clausula: `Section 2.3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.10 - Column profile depth maximum (W36/W920) (`d_col`)

- Ambito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 508 mm <= 920 mm`
- Clausula: `Section 6.3 (3)`
- Resultado: 🟢 Cumple

### Chequeo 1.11 - End-plate fit within column flange width (`bp`)

- Ambito: `COLUMN`
- Verificacion: `bp <= bcf; 253 mm <= 290 mm`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.12 - Column-slab connection condition (`col_losa`)

- Ambito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Section 2.3.4 (3)`
- Resultado: 🟢 Cumple

### Chequeo 1.13 - Stc >= pfo + de + 12.5 mm (`Stc`)

- Ambito: `COLUMN`
- Verificacion: `Stc >= Stc_min; 762 mm >= 122.5 mm`
- Clausula: `Section 6.3.1 (column top clearance criterion)`
- Resultado: 🟢 Cumple

### Chequeo 1.14 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.59 ratio <= 6.89 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.15 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.01 ratio <= 56.24 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.16 - End-plate width explicit dual inequalities (`bp`)

- Ambito: `END_PLATE`
- Verificacion: `bp <= bbf + 25 mm; bp <= bcf; [min,max] = [177.8 mm, 253 mm]`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.17 - End-plate stiffener height derived from end-plate geometry (`hst`)

- Ambito: `END_PLATE_STIFFENER`
- Verificacion: `hst = pfo + de; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Section 6.3`
- Resultado: 🟢 Cumple

### Chequeo 1.18 - End-plate to beam-web weld type shall be an allowed category (`weld_ep_web`)

- Ambito: `WELDS`
- Verificacion: `weld_ep_web in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Section 6.7`
- Resultado: 🟢 Cumple

### Chequeo 1.19 - Continuity-plate weld type shall be explicitly declared with an allowed weld category (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Section 6.3 (continuity plate weld detail)`
- Resultado: 🟢 Cumple

### Chequeo 1.20 - Continuity-plate weld type when plate thickness is less than or equal to 3/8 in (10 mm) (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {cjp, pjp} => cumple siempre; tcp=15.9 mm; weld_cp='cjp'`
- Clausula: `Section 6.3 (continuity plate weld detail)`
- Resultado: 🟢 Cumple

### Chequeo 1.21 - Bolt tightening type must be one recognized category (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.22 - Bolts shall be pretensioned unless a specific connection permits otherwise (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.23 - Bolt fabrication standard must be an allowed high-strength ASTM designation (`std_bolt`)

- Ambito: `BOLTS`
- Verificacion: `std_bolt in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.24 - Edge distance at de (`de`)

- Ambito: `TABLE_6_1`
- Verificacion: `de >= emin; 60 mm >= 38.1 mm`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.25 - Outside bolt-row distance limits (`pfo - pso`)

- Ambito: `TABLE_6_1`
- Verificacion: `pso (=pfo) >= emin; pfo <= 114 mm; pfo >= 38 mm; [min,max] = [38.1 mm, 114.3 mm]`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.26 - Inside bolt-row distance limits (`pfi - psi`)

- Ambito: `TABLE_6_1`
- Verificacion: `pfi >= emin; pfi <= 114 mm; pfi >= 38 mm; psi = pfi + tfb - tcp; psi > 0; [min,max] = [38.1 mm, 114.3 mm]`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.27 - Beam flange thickness limits (`tbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `tbf in [tbf_min, tbf_max]; 9.52 mm <= 17.3 mm <= 19.05 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.28 - Beam flange width limits (`bbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `bbf in [bbf_min, bbf_max]; 152.4 mm <= 228 mm <= 234.95 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.29 - Connecting beam depth limits (`d`)

- Ambito: `TABLE_6_1`
- Verificacion: `d in [d_min, d_max]; 349.25 mm <= 607 mm <= 609.6 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.30 - End-plate thickness limits (`tp`)

- Ambito: `TABLE_6_1`
- Verificacion: `tp in [tp_min, tp_max]; 12.7 mm <= 25.4 mm <= 57.15 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.31 - Horizontal bolt spacing limits (`g`)

- Ambito: `TABLE_6_1`
- Verificacion: `g in [g_min, g_max]; 101.6 mm <= 152.4 mm <= 152.4 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

## Paso 2 - Probable Maximum Moment At Plastic Hinge (Mpr)

Calculo de momento probable segun Eq. (2.4-1) y Eq. (2.4-2), usando `Ze = Zx` del catalogo de la viga.

- Clausula: `Chapter 6 / Section 6.7.1 Step 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Ecuacion: `Mpr = Cpr * Ry * Fy * Ze (Eq. 2.4-1 and Eq. 2.4-2)`
- Fy: `345 MPa`
- Fu: `450 MPa`
- Ry: `1.1`
- Ze (catalogo): `3280000 mm3`
- Cpr: `1.15`
- Mpr calculado: `1434.18 kN-m`

## Paso 3 - Distancia De Rotula Plastica Desde La Cara De Columna (Sh)

Para 4E: `Sh = min(d/2, 3bf)`. Para 4ES/8ES: `Sh = Lst + tp`.

- Clausula: `Chapter 6 / Section 6.7.1 Step 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Ecuacion: `Sh from connection-specific rules (Eq. 6.7-1 or Eq. 6.7-2)`
- Tipo de conexion: `bueep_4e`
- Beam shape: `W24X76`
- Lst (si aplica): `190.53 mm`
- tp (si aplica): `25.4 mm`
- Sh calculado: `303.5 mm`

## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Lh + Vgravity` y `Vhmin = 2*Mpr/Lh - Vgravity` (se reporta lado derecho).

- Clausula: `Chapter 6 / Section 6.7.1 Step 4 + Eq. (2.4-3)`
- Ecuacion: `Vhmax.der = 2*Mpr/Lh.der + Vgravity.der; Vhmin.der = 2*Mpr/Lh.der - Vgravity.der`
- Configuracion de vigas: `right_only`
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

- Clausula: `Chapter 6 / Section 6.7.1 Step 5 + Eq. (2.4-4)`
- Ecuacion: `Mfmax.der = Mpr + Vhmax.der*Sh; Mfmin.der = Mpr + Vhmin.der*Sh`
- Definicion para diseno: `Mf = Mfmax gobernante`
- Configuracion de vigas: `right_only`
- Lado gobernante Mfmax: `der`
- Fuente Mfmax seleccionado: `loads.probable_moment_column_face (legacy)`
- Mpr (intermedio): `1434.18 kN-m`
- Sh (intermedio): `303.5 mm`
- Vh.dermax (intermedio): `515.01 kN`
- Vh.dermin (intermedio): `426.05 kN`
- Mf.dermax: `1590.49 kN-m`
- Mf.dermin: `1563.49 kN-m`
- Mf (adoptado) = Mfmax gobernante: `1590.49 kN-m`

## Paso 6 - Revision De Resistencia Pernos

### 6.1 Revision de capacidad a traccion

#### 6.1.1 Estado #1: Rotura en el perno

- Clausula: `Chapter 6 / Section 6.7.1 Step 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Rut_b = Mf / (2*(h1 + h2)); phiRnt_b = phi * Rnt_b, Rnt_b = Ab * Fnt, Ab = pi*db^2/4 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- h1: `743.35 mm`
- h2: `648.35 mm`
- h3: `529.65 mm`
- h4: `434.65 mm`
- Rut_b: `243.55 kN`
- phiRnt_b: `450.19 kN`
- DCRbt: `0.54`
- Resultado: `PASS`

### 6.2 Revision de capacidad a cortante

#### 6.2.1 ELR #1: Rotura por cortante en el perno

- Clausula: `Chapter 6 / Section 6.7.1 Step 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Ruv2_b = Vhmax/nb, phiRnv_b = phi * Rnv_b, Rnv_b = Ab * Fnv, Ab = pi*db^2/4, nb = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vhmax: `515.01 kN`
- nb: `4`
- Ruv2_b: `128.75 kN`
- phiRnv_b: `271.27 kN`
- DCRbv: `0.47`
- Resultado: `PASS`

## Paso 7 - Revision de resistencia end plate

### 7.1. Revision de capacidad a flexion

#### 7.1.1. ELR #1: Fluencia (AISC 358-22 .7-8)

- Clausula: `Chapter 6 / Section 6.7.1 Step 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Mup = Mf; phiMnb = phi * tp^2 * Fyp * Yp (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mup: `677.91 kN-m`
- phiMnb: `1112.57 kN-m`
- DCRpm: `0.61`
- Yp calculado: `5553.91 mm`
- Tabla Yp aplicada: `AISC 358-22 Table 6.2`
- Caso Yp: `N/A`
- s: `98.18 mm`
- pfi de entrada: `50 mm`
- pfi efectivo: `50 mm`
- Resultado: `PASS`

### 7.2. Revision de capacidad a cortante perpendicular al plano de la platina

#### 7.2.1. Eje #1: Fluencia por cortante (AISC 358-22 G7-10)

- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fyp * bp * tp (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.9`
- Vup: `574.79 kN`
- phiVn1p: `1197.2 kN`
- DCRpv: `0.48`
- d (altura viga): `607 mm`
- Resultado: `PASS`

#### 7.2.2. Eje #2: Rotura por cortante (AISC 358-22 G7-12)

- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fup * tp * (bp - 2*dh) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Vup: `574.79 kN`
- phiVnb: `1169.63 kN`
- DCRpv: `0.49`
- dh (diametro agujero estandar): `31.75 mm`
- d (altura viga): `607 mm`
- Resultado: `PASS`

### 7.3. Revision de capacidad a cortante paralelo al plano de la platina

#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno (AISC 360-22 J3.11a)

- Clausula: `Chapter 6 / Section 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `Vu2p = Vhmax/nb; phiVn2p = phi * 1.2 * lc * tp * Fup (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vu2p: `128.75 kN`
- phiVn2p: `1056.06 kN`
- DCRpn2: `0.12`
- lc: `85.55 mm`
- dh: `31.75 mm`
- db: `28.57 mm`
- Resultado: `PASS`

#### 7.3.2. ELR #2: Aplastamiento en la perforacion del perno (AISC 360-22 J3.11a)

- Clausula: `Chapter 6 / Section 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Vu2p = Vhmax/nb; phiVn2p = phi * 2.4 * (db + 1.6 mm) * tp * Fup (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vu2p: `128.75 kN`
- phiVn2p: `744.98 kN`
- DCRpn2: `0.17`
- lc: `85.55 mm`
- dh: `31.75 mm`
- db: `28.57 mm`
- Resultado: `PASS`

## Paso 11 - Revision de resistencia de soldadura viga-alma a end plate

### 11.1 Revision capacidad a traccion

#### 11.1.1 ELR #1: Rotura de soldadura

- Clausula: `Section 6.7 + AISC 360-22 J2.4`
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

- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-13)`
- M_ucf: `677.91 kN-m`
- phi usado: `1`
- Condicion aplicable: `hay platinas de continuidad`
- s: `98.18 mm`
- Y_cs usado: `6350 mm`
- Ecuacion: `phiM_ncf = phi((t_cf^2 * f_yc * Y_cs)/1.11)`
- phiM_ncf: `3221.31 kN-m`
- Ecuacion DCR: `DCR_cfm = M_ucf/(phiM_ncf)`
- DCR_cfm: `0.21`
- Resultado: `Cumple`

Donde:
- `Y_c`: no hay platinas de continuidad -> Tablas 6.5 y 6.6 (unstiffened column flange).
- `Y_cs`: hay platinas de continuidad -> Tablas 6.5 y 6.6 (stiffened column flange).
