# Memoria de Calculo

- Proyecto: `proj_bseep_si_demo`
- Caso: `case_si_bseep_8es_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bseep_8es`
- Estado global: `FAIL`

## Revision conexion viga a derecha de columna

## Paso 1 - PREQUALIFICATION LIMITS

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### Nota tecnica - Protected zone length measured from column face

- Ambito: `BEAM`
- Clausula: `Section 2.3.4 (8)`
- Formula: `Lpz = min(lst + 0.5d, 3bf)`
- Candidato A (lst + 0.5d): `494.03 mm`
- Candidato B (3bf): `684 mm`
- Longitud zona protegida requerida: `494.03 mm`

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

### Nota tecnica - Distancias verticales h1, h2, h3 y h4 para trazabilidad geometrica

- Ambito: `END_PLATE`
- Clausula: `Section 6.3`
- Requisito: `h1, h2, h3 y h4 medidos desde la mitad del espesor del ala inferior de la viga`
- Formula: `h1=d-0.5tf+pso+pb; h2=d-0.5tf+pso; h3=d-1.5tf-psi; h4=d-1.5tf-psi-pb`
- h1: `743.35 mm`
- h2: `648.35 mm`
- h3: `529.65 mm`
- h4: `434.65 mm`

### Nota tecnica - Diametro estandar de perforacion (dh) para pernos en end plate

- Ambito: `END_PLATE`
- Clausula: `AISC 360-22 Table J3.3`
- Requisito: `dh segun tabla de agujero estandar: d+1/16 (hasta 7/8 in); d+1/8 (>=1 in)`
- Formula: `dh = d + 1/16 in (db<=7/8 in) else dh = d + 1/8 in`
- db (diametro perno): `28.57 mm`
- dh (agujero estandar): `31.75 mm`
- Incremento aplicado (in): `0.12`

### Nota tecnica - Derived end-plate stiffener geometry and detailing edge requirement

- Ambito: `END_PLATE_STIFFENER`
- Clausula: `Section 6.3`
- Requisito: `hst = pfo + de; Lst = hst/tan(30 deg); edge detailing >= 25 mm`
- Formula: `hst = pfo + de; Lst = hst / tan(30 deg)`
- stiffener_height (hst): `110 mm`
- stiffener_widht(Lst): `190.53 mm`
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
- Verificacion: `g >= 3db; 140 mm >= 85.72 mm`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.4 - Length without shear connectors from column face (`Lsc`)

- Ambito: `BEAM`
- Verificacion: `Lsc >= 1.5d; 1000 mm >= 910.5 mm`
- Clausula: `Section 2.3.4 (2)`
- Resultado: 🟢 Cumple

### Chequeo 1.5 - Beam clearance criterion using Sc and S threshold (`Sc`)

- Ambito: `BEAM`
- Verificacion: `Sc = Stc - pfo - pb; S = 0.5*sqrt(bcf*g); Sc > S => 617.004 mm > 100.747 mm`
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

### Chequeo 1.13 - Stc >= pfo + pb + de + 12.5 mm (`Stc`)

- Ambito: `COLUMN`
- Verificacion: `Stc >= Stc_min; 762 mm >= 217.5 mm`
- Clausula: `Section 6.3.1 (column top clearance criterion)`
- Resultado: 🟢 Cumple

### Chequeo 1.14 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.59 ratio <= 6.89 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.15 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.01 ratio <= 53.01 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.16 - End-plate width explicit dual inequalities (`bp`)

- Ambito: `END_PLATE`
- Verificacion: `bp <= bbf + 25 mm; bp <= bcf; [min,max] = [228.6 mm, 253 mm]`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.17 - End-plate stiffener height derived from end-plate geometry (`hst`)

- Ambito: `END_PLATE_STIFFENER`
- Verificacion: `hst = pfo + de; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Section 6.3`
- Resultado: 🟢 Cumple

### Chequeo 1.18 - Stiffener thickness minimum requirement (`ts`)

- Ambito: `END_PLATE_STIFFENER`
- Verificacion: `ts >= tbw*(Fyb/Fys); 12.7 mm >= 11.2 mm`
- Clausula: `Section 6.7.1 Eq. (6.7-9)`
- Resultado: 🟢 Cumple

### Chequeo 1.19 - Stiffener local buckling width-thickness limit (`hst/ts`)

- Ambito: `END_PLATE_STIFFENER`
- Verificacion: `hst/ts <= 0.56*sqrt(E/Fys); 8.66 ratio <= 13.48 ratio`
- Clausula: `Section 6.7.1 Eq. (6.7-10)`
- Resultado: 🟢 Cumple

### Chequeo 1.20 - Bolt gage clearance with stiffener thickness (`g`)

- Ambito: `END_PLATE_STIFFENER`
- Verificacion: `g >= 2emin + ts; 140 mm >= 88.9 mm`
- Clausula: `Section 6.3 (stiffened) + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.21 - End-plate to beam-web weld type shall be an allowed category (`weld_ep_web`)

- Ambito: `WELDS`
- Verificacion: `weld_ep_web in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Section 6.7`
- Resultado: 🟢 Cumple

### Chequeo 1.22 - Continuity-plate weld type shall be explicitly declared with an allowed weld category (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Section 6.3 (continuity plate weld detail)`
- Resultado: 🟢 Cumple

### Chequeo 1.23 - Continuity-plate weld type when plate thickness is less than or equal to 3/8 in (10 mm) (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {cjp, pjp} => cumple siempre; tcp=15.9 mm; weld_cp='cjp'`
- Clausula: `Section 6.3 (continuity plate weld detail)`
- Resultado: 🟢 Cumple

### Chequeo 1.24 - Bolt tightening type must be one recognized category (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.25 - Bolts shall be pretensioned unless a specific connection permits otherwise (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.26 - Bolt fabrication standard must be an allowed high-strength ASTM designation (`std_bolt`)

- Ambito: `BOLTS`
- Verificacion: `std_bolt in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.27 - Vertical pitch minimum spacing (`pb`)

- Ambito: `TABLE_6_1`
- Verificacion: `pb >= 3db; pb <= 95.000 mm; pb >= 89 mm; [min,max] = [89 mm, 95 mm]`
- Clausula: `Table 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

### Chequeo 1.28 - Edge distance at de (`de`)

- Ambito: `TABLE_6_1`
- Verificacion: `de >= emin; 60 mm >= 38.1 mm`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.29 - Outside bolt-row distance limits (`pfo - pso`)

- Ambito: `TABLE_6_1`
- Verificacion: `pso (=pfo) >= emin; pfo <= 51 mm; pfo >= 41 mm; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.30 - Inside bolt-row distance limits (`pfi - psi`)

- Ambito: `TABLE_6_1`
- Verificacion: `pfi >= emin; pfi <= 51 mm; pfi >= 41 mm; psi = pfi + tfb - tcp; psi > 0; [min,max] = [41.27 mm, 50.8 mm]`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.31 - Beam flange thickness limits (`tbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `tbf in [tbf_min, tbf_max]; 14.29 mm <= 17.3 mm <= 25.4 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.32 - Beam flange width limits (`bbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `bbf in [bbf_min, bbf_max]; 190.5 mm <= 228 mm <= 311.15 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.33 - Connecting beam depth limits (`d`)

- Ambito: `TABLE_6_1`
- Verificacion: `d in [d_min, d_max]; 457.2 mm <= 607 mm <= 914.4 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.34 - End-plate thickness limits (`tp`)

- Ambito: `TABLE_6_1`
- Verificacion: `tp in [tp_min, tp_max]; 19.05 mm <= 25.4 mm <= 63.5 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.35 - Horizontal bolt spacing limits (`g`)

- Ambito: `TABLE_6_1`
- Verificacion: `g in [g_min, g_max]; 127 mm <= 140 mm <= 152.4 mm`
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
- Mpr de comparacion: `1434.18 kN-m`
- Resultado: `PASS`

## Paso 3 - Distancia De Rotula Plastica Desde La Cara De Columna (Sh)

Para 4E: `Sh = min(d/2, 3bf)`. Para 4ES/8ES: `Sh = Lst + tp`.

- Clausula: `Chapter 6 / Section 6.7.1 Step 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Ecuacion: `Sh from connection-specific rules (Eq. 6.7-1 or Eq. 6.7-2)`
- Tipo de conexion: `bseep_8es`
- Beam shape: `W24X76`
- Lst (si aplica): `190.53 mm`
- tp (si aplica): `25.4 mm`
- Sh calculado: `215.93 mm`
- Resultado: `PASS`

## Paso 4 - Cortante Probable En Rotula Plastica (Vhmax, Vhmin)

Calculo segun Eq. (2.4-3): `Vhmax = 2*Mpr/Lh + Vgravity` y `Vhmin = 2*Mpr/Lh - Vgravity` (se reporta lado derecho).

- Clausula: `Chapter 6 / Section 6.7.1 Step 4 + Eq. (2.4-3)`
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
- Resultado: `PASS`

## Paso 5 - Momento Probable En Cara De Columna (Mfmax, Mfmin)

Calculo segun Eq. (2.4-4): `Mfmax = Mpr + Vhmax*Sh` y `Mfmin = Mpr + Vhmin*Sh` (se reporta lado derecho).

- Clausula: `Chapter 6 / Section 6.7.1 Step 5 + Eq. (2.4-4)`
- Ecuacion: `Mfmax.der = Mpr + Vhmax.der*Sh; Mfmin.der = Mpr + Vhmin.der*Sh`
- Configuracion de vigas: `both_sides`
- Lado gobernante Mfmax: `der`
- Fuente Mfmax seleccionado: `step5_computed_mf_dermax (governing_side=der)`
- Mpr (intermedio): `1434.18 kN-m`
- Sh (intermedio): `215.93 mm`
- Vh.dermax (intermedio): `515.01 kN`
- Vh.dermin (intermedio): `426.05 kN`
- Mf.dermax: `1545.38 kN-m`
- Mf.dermin: `1526.17 kN-m`
- Mfmax gobernante: `1545.38 kN-m`
- Resultado: `PASS`

## Paso 6 - Revision De Resistencia Pernos

### 6.1 Revision de capacidad a traccion

#### 6.1.1 Estado #1: Rotura en el perno

- Clausula: `Chapter 6 / Section 6.7.1 Step 6.1 + AISC 360-22 J3.7`
- Ecuacion: `Pub = Mf / (2*(h1 + h2 + h3 + h4)); phiPnb = phi * Ab * Fnt, Ab = pi*db^2/4, phi = 0.9 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- h1: `743.35 mm`
- h2: `648.35 mm`
- h3: `529.65 mm`
- h4: `434.65 mm`
- Pub: `327.97 kN`
- phiPnb: `450.19 kN`
- DCRbt: `0.73`
- Resultado: `PASS`

### 6.2 Revision de capacidad a cortante

#### 6.2.1 ELR #1: Rotura por cortante en el perno

- Clausula: `Chapter 6 / Section 6.7.1 Step 6.2 + AISC 360-22 J3.7`
- Ecuacion: `Vub = Vhmax/nb, phiVnb = phi * Ab * Fnv, Ab = pi*db^2/4, nb = 4 (4E/4ES) or 8 (8ES), phi = 0.9 (AISC 360-22 J3.7)`
- phi usado: `0.9`
- Vhmax: `515.01 kN`
- nb: `8`
- Vub: `64.38 kN`
- phiVnb: `271.27 kN`
- DCRbv: `0.24`
- Resultado: `PASS`

## Paso 7 - Revision de resistencia end plate

### 7.1. Revision de capacidad a flexion

#### 7.1.1. ELR #1: Fluencia (AISC 358-22 .7-8)

- Clausula: `Chapter 6 / Section 6.7.1 Step 7.1.1 + Eq. (6.7-8)`
- Ecuacion: `Mup = Mf; phiMnb = phi * tp^2 * Fyp * Yp (AISC 358-22 Eq. 6.7-8)`
- phi usado: `0.9`
- Mup: `1545.38 kN-m`
- phiMnb: `1645.5 kN-m`
- DCRpm: `0.94`
- Yp calculado: `8214.25 mm`
- Tabla Yp aplicada: `AISC 358-22 Table 6.4`
- Caso Yp: `Case 1 (de <= s)`
- s: `94.1 mm`
- pfi de entrada: `50 mm`
- pfi efectivo: `50 mm`
- Resultado: `PASS`

### 7.2. Revision de capacidad a cortante perpendicular al plano de la platina

#### 7.2.1. Eje #1: Fluencia por cortante (AISC 358-22 G7-10)

- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.1 + Eq. (6.7-10)`
- Ecuacion: `Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fyp * bp * tp (AISC 358-22 Eq. 6.7-10)`
- phi usado: `0.9`
- Vup: `1310.31 kN`
- phiVn1p: `1197.2 kN`
- DCRpv: `1.09`
- d (altura viga): `607 mm`
- Resultado: `FAIL`

#### 7.2.2. Eje #2: Rotura por cortante (AISC 358-22 G7-12)

- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.2 + Eq. (6.7-12)`
- Ecuacion: `Vup = Mf / (2*(d - tbf)); phiVnb = phi * 0.6 * Fup * tp * (bp - 2*dh) (AISC 358-22 Eq. 6.7-12)`
- phi usado: `0.9`
- Vup: `1310.31 kN`
- phiVnb: `1169.63 kN`
- DCRpv: `1.12`
- dh (diametro agujero estandar): `31.75 mm`
- d (altura viga): `607 mm`
- Resultado: `FAIL`

### 7.3. Revision de capacidad a cortante paralelo al plano de la platina

#### 7.3.1. ELR #1: Desgarramiento en la perforacion del perno (AISC 360-22 J3.11a)

- Clausula: `Chapter 6 / Section 7.3.1 + AISC 360-22 J3.11(a)`
- Ecuacion: `Vu2p = Vhmax/nb; phiVn2p = phi * 1.2 * lc * tp * Fup (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vu2p: `64.38 kN`
- phiVn2p: `780.73 kN`
- DCRpn2: `0.08`
- lc: `63.25 mm`
- dh: `31.75 mm`
- db: `28.57 mm`
- Resultado: `PASS`

#### 7.3.2. ELR #2: Aplastamiento en la perforacion del perno (AISC 360-22 J3.11a)

- Clausula: `Chapter 6 / Section 7.3.2 + AISC 360-22 J3.11(a)`
- Ecuacion: `Vu2p = Vhmax/nb; phiVn2p = phi * 2.4 * (db + 1.6 mm) * tp * Fup (AISC 360-22 J3.11a)`
- phi usado: `0.9`
- Vu2p: `64.38 kN`
- phiVn2p: `744.98 kN`
- DCRpn2: `0.09`
- lc: `63.25 mm`
- dh: `31.75 mm`
- db: `28.57 mm`
- Resultado: `PASS`

## Paso 8 - Revision de Resistencia soldadura #1 (end plate con rigidizador)

### 8.1. Revision de capacidad a traccion

#### 8.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)

- Clausula: `Chapter 6 / Section 6.7.1 Step 8.1.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Pust = Fys * ts * hst; phiRnst = phi * nl * 0.6 * FEXX * 0.707 * lst * wst (AISC 360-22 J2.4)`
- phi usado: `0.9`
- Tipo soldadura rigidizador: `fillet`
- Pust: `481.96 kN`
- phiRnst: `677.11 kN`
- DCRst,w1,t: `0.71`
- l_st (longitud soldadura): `190 mm`
- w_st (espesor soldadura): `9.53 mm`
- n_l (lineas soldadura): `2`
- Resultado: `PASS`

## Paso 9 - Revision de resistencia soldadura #2 (viga con rigidizador)

### 9.1. Revision de capacidad a cortante

#### 9.1.1. ELR #1: Rotura de la soldadura (AISC 360-22 J2.4)

- Clausula: `Chapter 6 / Section 6.7.1 Step 9.1.1 + AISC 360-22 J2.4`
- Ecuacion: `Fillet: Vust,w2 = Fys * 0.6 * ts * lst; phiVnst,w2 = phi * nl * 0.6 * FEXX * 0.707 * lst,w2 * wst,2 (AISC 360-22 J2.4)`
- phi usado: `0.9`
- Tipo soldadura viga-rigidizador: `fillet`
- Vust,w2: `499.49 kN`
- phiVnst,w2: `677.11 kN`
- DCRst,w2,v: `0.74`
- l_st,w2 (longitud soldadura): `190 mm`
- w_st,2 (espesor soldadura): `9.53 mm`
- n_l,w2 (lineas soldadura): `2`
- Resultado: `PASS`

## Paso 10 - Revision de resistencia de la viga

### 10.1. Revision de capacidad a cortante

#### 10.1.1. ELR #1: Fluencia por cortante (AISC 360-22 G2.1)

- Clausula: `Chapter 6 / Section 6.7.1 Step 10.1.1 + AISC 360-22 G2.1`
- Ecuacion: `Vubm = Vhmax; phiVnbm = phi * 0.6 * Fybm * tw,bm * d * Cv1 (AISC 360-22 G2.1, Eq. G2-3/G2-4; kv=5.34 for webs without transverse stiffeners)`
- phi usado: `1`
- Vubm: `515.01 kN`
- phiVnbm: `1407.27 kN`
- DCRbm,v: `0.37`
- Cv1: `1`
- kv: `5.34`
- h/tw: `48.84`
- h: `547 mm`
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
