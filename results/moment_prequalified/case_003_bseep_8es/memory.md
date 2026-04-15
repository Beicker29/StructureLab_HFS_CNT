# Memoria de Calculo

- Proyecto: `proj_bseep_si_demo`
- Caso: `case_si_bseep_8es_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bseep_8es`
- Estado global: `PASS`

## Paso 1 - PREQUALIFICATION LIMITS

Comparacion directa de valor calculado contra limite normativo (sin formato DCR).

### Nota tecnica - Protected zone length measured from column face

- Ambito: `BEAM`
- Clausula: `Section 2.3.4 (8)`
- Formula: `Lpz = min(lst + 0.5d, 3bf)`
- Candidato A (lst + 0.5d): `494.026 mm`
- Candidato B (3bf): `684.000 mm`
- Longitud zona protegida requerida: `494.026 mm`

### Nota tecnica - End-plate connection location on column

- Ambito: `COLUMN`
- Clausula: `Section 6.3 (2)`
- Requisito: `The end plate shall be connected to the flange of the column.`

### Nota tecnica - Derived end-plate height reference

- Ambito: `END_PLATE`
- Clausula: `Section 6.3`
- Requisito: `end_plate_height = pfo + de`
- Formula: `h_ep = pfo + de`
- Candidato A (pfo): `50.000 mm`
- Candidato B (de): `60.000 mm`
- Valor derivado: `110.000 mm`

### Nota tecnica - Derived end-plate stiffener geometry and detailing edge requirement

- Ambito: `END_PLATE_STIFFENER`
- Clausula: `Section 6.3`
- Requisito: `hst = pfo + de; Lst = hst/tan(30 deg); edge detailing >= 25 mm`
- Formula: `hst = pfo + de; Lst = hst / tan(30 deg)`
- stiffener_height (hst): `110.000 mm`
- stiffener_widht(Lst): `190.526 mm`
- edge detailing: `25.000 mm`

### Nota tecnica - Requisitos de soldadura entre ala de viga y placa de extremo

- Ambito: `WELDS`
- Clausula: `Section 6.7`
- Requisito: `La unión entre el ala de la viga y la placa de extremo debe ejecutarse con una soldadura de ranura CJP sin respaldo. La soldadura de ranura CJP debe realizarse de modo que la raíz de la soldadura quede del lado del alma de la viga respecto del ala. La cara interior del ala debe tener una soldadura de filete de c in. (8 mm). Estas soldaduras deben ser de demanda crítica.`

### Nota tecnica - Secuencia de soldadura para conexiones end-plate rigidizadas

- Ambito: `WELDS`
- Clausula: `Section 6.7`
- Requisito: `Para conexiones end-plate rigidizadas, la soldadura entre el ala de la viga y la placa de extremo debe ejecutarse antes de instalar el rigidizador.`

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
- Verificacion: `bp >= bf + margin; 253.000 mm >= 253.000 mm`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.3 - Bolt gage minimum spacing (`g`)

- Ambito: `BEAM`
- Verificacion: `g >= 3db; 152.400 mm >= 85.725 mm`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.4 - Length without shear connectors from column face (`Lsc`)

- Ambito: `BEAM`
- Verificacion: `Lsc >= 1.5d; 1000.000 mm >= 910.500 mm`
- Clausula: `Section 2.3.4 (2)`
- Resultado: 🟢 Cumple

### Chequeo 1.5 - Clear span-to-depth ratio by frame system (`Lclear/d`)

- Ambito: `BEAM`
- Verificacion: `Lclear/d >= 7 (SMF); 10.043 ratio >= 7.000 ratio`
- Clausula: `Section 2.3.4 (5)`
- Resultado: 🟢 Cumple

### Chequeo 1.6 - Beam flange width-to-thickness compactness (`lambda_f_beam`)

- Ambito: `BEAM`
- Verificacion: `lambda_f_beam <= lambda_f_limit; 6.590 ratio <= 6.887 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.7 - Beam web width-to-thickness compactness (`lambda_w_beam`)

- Ambito: `BEAM`
- Verificacion: `lambda_w_beam <= lambda_w_limit; 48.839 ratio <= 56.244 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.8 - Column profile family allowed for prequalification (`shape_col`)

- Ambito: `COLUMN`
- Verificacion: `shape_col in {W, HEA, HEB, IPE}; 'W18X175' in {W, HEA, HEB, IPE}`
- Clausula: `Section 2.3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.9 - Column profile depth maximum (W36/W920) (`d_col`)

- Ambito: `COLUMN`
- Verificacion: `d_col <= W36/W920; 508.000 mm <= 920.000 mm`
- Clausula: `Section 6.3 (3)`
- Resultado: 🟢 Cumple

### Chequeo 1.10 - End-plate fit within column flange width (`bp`)

- Ambito: `COLUMN`
- Verificacion: `bp <= bcf; 253.000 mm <= 290.000 mm`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.11 - Column-slab connection condition (`col_losa`)

- Ambito: `COLUMN`
- Verificacion: `col_losa == isolated; 'isolated' == 'isolated'`
- Clausula: `Section 2.3.4 (3)`
- Resultado: 🟢 Cumple

### Chequeo 1.12 - Column flange width-to-thickness compactness (`lambda_f_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_f_col <= lambda_f_limit; 3.589 ratio <= 6.887 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.13 - Column web width-to-thickness compactness (`lambda_w_col`)

- Ambito: `COLUMN`
- Verificacion: `lambda_w_col <= lambda_w_limit; 18.009 ratio <= 53.010 ratio`
- Clausula: `Section 2.3.4 (6) + AISC Seismic Provisions`
- Resultado: 🟢 Cumple

### Chequeo 1.14 - End-plate width explicit dual inequalities (`bp`)

- Ambito: `END_PLATE`
- Verificacion: `bp <= bbf + 25 mm; bp <= bcf; [min,max] = [228.600 mm, 253.000 mm]`
- Clausula: `Section 6.3 / Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.15 - End-plate stiffener height derived from end-plate geometry (`hst`)

- Ambito: `END_PLATE_STIFFENER`
- Verificacion: `hst = pfo + de; 110.000 mm = 50.000 mm + 60.000 mm`
- Clausula: `Section 6.3`
- Resultado: 🟢 Cumple

### Chequeo 1.16 - End-plate to beam-web weld type shall be an allowed category (`weld_ep_web`)

- Ambito: `WELDS`
- Verificacion: `weld_ep_web in {cjp, double_sided_fillet, single_sided_fillet}; 'cjp' in {cjp, double_sided_fillet, single_sided_fillet}`
- Clausula: `Section 6.7`
- Resultado: 🟢 Cumple

### Chequeo 1.17 - Continuity-plate weld type shall be explicitly declared with an allowed weld category (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {double_sided_fillet, cjp, pjp}; 'cjp' in {double_sided_fillet, cjp, pjp}`
- Clausula: `Section 6.3 (continuity plate weld detail)`
- Resultado: 🟢 Cumple

### Chequeo 1.18 - Continuity-plate weld type when plate thickness is less than or equal to 3/8 in (10 mm) (`weld_cp`)

- Ambito: `CONTINUITY_PLATE`
- Verificacion: `weld_cp in {cjp, pjp} => cumple siempre; tcp=15.900 mm; weld_cp='cjp'`
- Clausula: `Section 6.3 (continuity plate weld detail)`
- Resultado: 🟢 Cumple

### Chequeo 1.19 - Bolt tightening type must be one recognized category (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt in {pretensioned, snug_tight}; 'pretensioned' in {pretensioned, snug_tight}`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.20 - Bolts shall be pretensioned unless a specific connection permits otherwise (`tight_bolt`)

- Ambito: `BOLTS`
- Verificacion: `tight_bolt == pretensioned; 'pretensioned' == 'pretensioned'`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.21 - Bolt fabrication standard must be an allowed high-strength ASTM designation (`std_bolt`)

- Ambito: `BOLTS`
- Verificacion: `std_bolt in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}; 'ASTM A490' in {ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}`
- Clausula: `Section 4.1 FASTENER ASSEMBLIES`
- Resultado: 🟢 Cumple

### Chequeo 1.22 - Vertical pitch minimum spacing (`pb`)

- Ambito: `TABLE_6_1`
- Verificacion: `pb >= 3db; pb <= 95.000 mm; pb >= 89 mm; [min,max] = [89.000 mm, 95.000 mm]`
- Clausula: `Table 6.1 (BSEEP-8ES)`
- Resultado: 🟢 Cumple

### Chequeo 1.23 - Edge distance at de (`de`)

- Ambito: `TABLE_6_1`
- Verificacion: `de >= emin; 60.000 mm >= 38.100 mm`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.24 - Outside bolt-row distance limits (`pfo - pso`)

- Ambito: `TABLE_6_1`
- Verificacion: `pso (=pfo) >= emin; pfo <= 51 mm; pfo >= 41 mm; [min,max] = [41.275 mm, 50.800 mm]`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.25 - Inside bolt-row distance limits (`pfi - psi`)

- Ambito: `TABLE_6_1`
- Verificacion: `pfi >= emin; pfi <= 51 mm; pfi >= 41 mm; psi = pfi + tfb - tcp; psi > 0; [min,max] = [41.275 mm, 50.800 mm]`
- Clausula: `Table 6.1 + AISC 360 Table J3.4`
- Resultado: 🟢 Cumple

### Chequeo 1.26 - Beam flange thickness limits (`tbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `tbf in [tbf_min, tbf_max]; 14.287 mm <= 17.300 mm <= 25.400 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.27 - Beam flange width limits (`bbf`)

- Ambito: `TABLE_6_1`
- Verificacion: `bbf in [bbf_min, bbf_max]; 190.500 mm <= 228.000 mm <= 311.150 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.28 - Connecting beam depth limits (`d`)

- Ambito: `TABLE_6_1`
- Verificacion: `d in [d_min, d_max]; 457.200 mm <= 607.000 mm <= 914.400 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.29 - End-plate thickness limits (`tp`)

- Ambito: `TABLE_6_1`
- Verificacion: `tp in [tp_min, tp_max]; 19.050 mm <= 25.400 mm <= 63.500 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple

### Chequeo 1.30 - Horizontal bolt spacing limits (`g`)

- Ambito: `TABLE_6_1`
- Verificacion: `g in [g_min, g_max]; 127.000 mm <= 152.400 mm <= 152.400 mm`
- Clausula: `Table 6.1`
- Resultado: 🟢 Cumple
