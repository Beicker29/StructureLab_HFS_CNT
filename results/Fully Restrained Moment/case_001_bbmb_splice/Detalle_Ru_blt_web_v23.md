# Reporte Metodos Pernos 1 (Splice)

## 1. Informacion General

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Metodo seleccionado en JSON: `icr`

### 1.1 Variables de carga

- Ecuacion base: `Muz_blt_web = Vu2_sp*ex_blt_web - Pu_sp*ey_blt_web`
- Pu_sp: `0 kN` (origen: `loads.Pu_sp`)
- Vu2_sp: `250 kN` (origen: `loads.Vu2_sp`)
- ex_blt_web: `152.4 mm` (origen: `formula splice`)
- ey_blt_web: `0 mm` (origen: `input ey`)
- Muz_blt_web: `38100 kN-mm`

## 2. Geometria de pernos derivada

- Ru_blt_web_v23: `56.2 kip` con `sqrt(Pu_sp^2 + Vu2_sp^2)`
- theta_blt_web: `90 deg` con `atan2(Vu2_sp, Pu_sp)`
- e_blt_web: `6 in` con `sqrt(ex_blt_web^2 + ey_blt_web^2)`
- n_blt_web: `12 -` con `conteo pernos activos`
- x_cg_blt_web: `1.5 in` con `sum(x_i_blt_web)/n_blt_web`
- y_cg_blt_web: `7.5 in` con `sum(y_i_blt_web)/n_blt_web`
- Ix_blt_web: `315 in2` con `sum((y_i_blt_web-y_cg_blt_web)^2)`
- Iy_blt_web: `27 in2` con `sum((x_i_blt_web-x_cg_blt_web)^2)`
- J_blt_web: `342 in2` con `Ix_blt_web + Iy_blt_web`
- Muz_blt_web: `337.21 kip-in` con `Vu2_sp*ex_blt_web - Pu_sp*ey_blt_web`
- dmax_blt_web: `7.65 in` con `max(sqrt((x_i_blt_web-x_cg_blt_web)^2+(y_i_blt_web-y_cg_blt_web)^2))`

## 3. Geometria del grupo de pernos

- Perno `w1`: x_1_blt_web=`0 in`, y_1_blt_web=`0 in`, dx_cg_1_blt_web=`-1.5 in`, dy_cg_1_blt_web=`-7.5 in`, r_cg_1_blt_web=`7.65 in`
- Perno `w2`: x_2_blt_web=`0 in`, y_2_blt_web=`3 in`, dx_cg_2_blt_web=`-1.5 in`, dy_cg_2_blt_web=`-4.5 in`, r_cg_2_blt_web=`4.74 in`
- Perno `w3`: x_3_blt_web=`0 in`, y_3_blt_web=`6 in`, dx_cg_3_blt_web=`-1.5 in`, dy_cg_3_blt_web=`-1.5 in`, r_cg_3_blt_web=`2.12 in`
- Perno `w4`: x_4_blt_web=`0 in`, y_4_blt_web=`9 in`, dx_cg_4_blt_web=`-1.5 in`, dy_cg_4_blt_web=`1.5 in`, r_cg_4_blt_web=`2.12 in`
- Perno `w5`: x_5_blt_web=`0 in`, y_5_blt_web=`12 in`, dx_cg_5_blt_web=`-1.5 in`, dy_cg_5_blt_web=`4.5 in`, r_cg_5_blt_web=`4.74 in`
- Perno `w6`: x_6_blt_web=`0 in`, y_6_blt_web=`15 in`, dx_cg_6_blt_web=`-1.5 in`, dy_cg_6_blt_web=`7.5 in`, r_cg_6_blt_web=`7.65 in`
- Perno `w7`: x_7_blt_web=`3 in`, y_7_blt_web=`0 in`, dx_cg_7_blt_web=`1.5 in`, dy_cg_7_blt_web=`-7.5 in`, r_cg_7_blt_web=`7.65 in`
- Perno `w8`: x_8_blt_web=`3 in`, y_8_blt_web=`3 in`, dx_cg_8_blt_web=`1.5 in`, dy_cg_8_blt_web=`-4.5 in`, r_cg_8_blt_web=`4.74 in`
- Perno `w9`: x_9_blt_web=`3 in`, y_9_blt_web=`6 in`, dx_cg_9_blt_web=`1.5 in`, dy_cg_9_blt_web=`-1.5 in`, r_cg_9_blt_web=`2.12 in`
- Perno `w10`: x_10_blt_web=`3 in`, y_10_blt_web=`9 in`, dx_cg_10_blt_web=`1.5 in`, dy_cg_10_blt_web=`1.5 in`, r_cg_10_blt_web=`2.12 in`
- Perno `w11`: x_11_blt_web=`3 in`, y_11_blt_web=`12 in`, dx_cg_11_blt_web=`1.5 in`, dy_cg_11_blt_web=`4.5 in`, r_cg_11_blt_web=`4.74 in`
- Perno `w12`: x_12_blt_web=`3 in`, y_12_blt_web=`15 in`, dx_cg_12_blt_web=`1.5 in`, dy_cg_12_blt_web=`7.5 in`, r_cg_12_blt_web=`7.65 in`

## 4. Resumen global por metodo

- Metodo `elastic_superposition`: applicable=`True`, estado=`PASS`, demanda=`9.63 kip`, capacidad=`14.82 kip`, DCR=`0.65`
- Metodo `elastic_ecr`: applicable=`True`, estado=`PASS`, demanda=`56.2 kip`, capacidad=`86.51 kip`, DCR=`0.65`
- Metodo `icr`: applicable=`True`, estado=`PASS`, demanda=`56.2 kip`, capacidad=`530.92 kip`, DCR=`0.11`

## 5. Elastic Method - Superposition

### 5.1 Formulacion

- Ecuaciones:
- `Ru_i_blt_web_v2 = -Pu_sp/n_blt_web`
- `Ru_i_blt_web_v3 = -Vu2_sp/n_blt_web`
- `Ru_mz_i_blt_web_v2 = Muz_blt_web*dy_cg_i_blt_web/J_blt_web`
- `Ru_mz_i_blt_web_v3 = -Muz_blt_web*dx_cg_i_blt_web/J_blt_web`
- `Ru_i_blt_web = sqrt((Ru_i_blt_web_v2+Ru_mz_i_blt_web_v2)^2 + (Ru_i_blt_web_v3+Ru_mz_i_blt_web_v3)^2)`
- Geometria por perno:

### 5.2 Geometria por perno

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_cg_1_blt_web=`-1.5`, dy_cg_1_blt_web=`-7.5`, r_cg_1_blt_web=`7.65`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`3`, dx_cg_2_blt_web=`-1.5`, dy_cg_2_blt_web=`-4.5`, r_cg_2_blt_web=`4.74`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`6`, dx_cg_3_blt_web=`-1.5`, dy_cg_3_blt_web=`-1.5`, r_cg_3_blt_web=`2.12`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`9`, dx_cg_4_blt_web=`-1.5`, dy_cg_4_blt_web=`1.5`, r_cg_4_blt_web=`2.12`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`12`, dx_cg_5_blt_web=`-1.5`, dy_cg_5_blt_web=`4.5`, r_cg_5_blt_web=`4.74`
- `w6`: x_6_blt_web=`0`, y_6_blt_web=`15`, dx_cg_6_blt_web=`-1.5`, dy_cg_6_blt_web=`7.5`, r_cg_6_blt_web=`7.65`
- `w7`: x_7_blt_web=`3`, y_7_blt_web=`0`, dx_cg_7_blt_web=`1.5`, dy_cg_7_blt_web=`-7.5`, r_cg_7_blt_web=`7.65`
- `w8`: x_8_blt_web=`3`, y_8_blt_web=`3`, dx_cg_8_blt_web=`1.5`, dy_cg_8_blt_web=`-4.5`, r_cg_8_blt_web=`4.74`
- `w9`: x_9_blt_web=`3`, y_9_blt_web=`6`, dx_cg_9_blt_web=`1.5`, dy_cg_9_blt_web=`-1.5`, r_cg_9_blt_web=`2.12`
- `w10`: x_10_blt_web=`3`, y_10_blt_web=`9`, dx_cg_10_blt_web=`1.5`, dy_cg_10_blt_web=`1.5`, r_cg_10_blt_web=`2.12`
- `w11`: x_11_blt_web=`3`, y_11_blt_web=`12`, dx_cg_11_blt_web=`1.5`, dy_cg_11_blt_web=`4.5`, r_cg_11_blt_web=`4.74`
- `w12`: x_12_blt_web=`3`, y_12_blt_web=`15`, dx_cg_12_blt_web=`1.5`, dy_cg_12_blt_web=`7.5`, r_cg_12_blt_web=`7.65`

### 5.3 Fuerzas por perno

- `w1`: Ru_dir_1_blt_web_v2=`-0`, Ru_dir_1_blt_web_v3=`-4.68`, Ru_rot_1_blt_web_v2=`-7.4`, Ru_rot_1_blt_web_v3=`1.48`, Ru_1_blt_web=`8.06`
- `w2`: Ru_dir_2_blt_web_v2=`-0`, Ru_dir_2_blt_web_v3=`-4.68`, Ru_rot_2_blt_web_v2=`-4.44`, Ru_rot_2_blt_web_v3=`1.48`, Ru_2_blt_web=`5.47`
- `w3`: Ru_dir_3_blt_web_v2=`-0`, Ru_dir_3_blt_web_v3=`-4.68`, Ru_rot_3_blt_web_v2=`-1.48`, Ru_rot_3_blt_web_v3=`1.48`, Ru_3_blt_web=`3.53`
- `w4`: Ru_dir_4_blt_web_v2=`-0`, Ru_dir_4_blt_web_v3=`-4.68`, Ru_rot_4_blt_web_v2=`1.48`, Ru_rot_4_blt_web_v3=`1.48`, Ru_4_blt_web=`3.53`
- `w5`: Ru_dir_5_blt_web_v2=`-0`, Ru_dir_5_blt_web_v3=`-4.68`, Ru_rot_5_blt_web_v2=`4.44`, Ru_rot_5_blt_web_v3=`1.48`, Ru_5_blt_web=`5.47`
- `w6`: Ru_dir_6_blt_web_v2=`-0`, Ru_dir_6_blt_web_v3=`-4.68`, Ru_rot_6_blt_web_v2=`7.4`, Ru_rot_6_blt_web_v3=`1.48`, Ru_6_blt_web=`8.06`
- `w7`: Ru_dir_7_blt_web_v2=`-0`, Ru_dir_7_blt_web_v3=`-4.68`, Ru_rot_7_blt_web_v2=`-7.4`, Ru_rot_7_blt_web_v3=`-1.48`, Ru_7_blt_web=`9.63`
- `w8`: Ru_dir_8_blt_web_v2=`-0`, Ru_dir_8_blt_web_v3=`-4.68`, Ru_rot_8_blt_web_v2=`-4.44`, Ru_rot_8_blt_web_v3=`-1.48`, Ru_8_blt_web=`7.59`
- `w9`: Ru_dir_9_blt_web_v2=`-0`, Ru_dir_9_blt_web_v3=`-4.68`, Ru_rot_9_blt_web_v2=`-1.48`, Ru_rot_9_blt_web_v3=`-1.48`, Ru_9_blt_web=`6.34`
- `w10`: Ru_dir_10_blt_web_v2=`-0`, Ru_dir_10_blt_web_v3=`-4.68`, Ru_rot_10_blt_web_v2=`1.48`, Ru_rot_10_blt_web_v3=`-1.48`, Ru_10_blt_web=`6.34`
- `w11`: Ru_dir_11_blt_web_v2=`-0`, Ru_dir_11_blt_web_v3=`-4.68`, Ru_rot_11_blt_web_v2=`4.44`, Ru_rot_11_blt_web_v3=`-1.48`, Ru_11_blt_web=`7.59`
- `w12`: Ru_dir_12_blt_web_v2=`-0`, Ru_dir_12_blt_web_v3=`-4.68`, Ru_rot_12_blt_web_v2=`7.4`, Ru_rot_12_blt_web_v3=`-1.48`, Ru_12_blt_web=`9.63`

### 5.4 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v2=`-7.4`, Ru_1_blt_web_v3=`-3.2`, Ru_1_blt_web=`8.06`
- `w2`: Ru_2_blt_web_v2=`-4.44`, Ru_2_blt_web_v3=`-3.2`, Ru_2_blt_web=`5.47`
- `w3`: Ru_3_blt_web_v2=`-1.48`, Ru_3_blt_web_v3=`-3.2`, Ru_3_blt_web=`3.53`
- `w4`: Ru_4_blt_web_v2=`1.48`, Ru_4_blt_web_v3=`-3.2`, Ru_4_blt_web=`3.53`
- `w5`: Ru_5_blt_web_v2=`4.44`, Ru_5_blt_web_v3=`-3.2`, Ru_5_blt_web=`5.47`
- `w6`: Ru_6_blt_web_v2=`7.4`, Ru_6_blt_web_v3=`-3.2`, Ru_6_blt_web=`8.06`
- `w7`: Ru_7_blt_web_v2=`-7.4`, Ru_7_blt_web_v3=`-6.16`, Ru_7_blt_web=`9.63`
- `w8`: Ru_8_blt_web_v2=`-4.44`, Ru_8_blt_web_v3=`-6.16`, Ru_8_blt_web=`7.59`
- `w9`: Ru_9_blt_web_v2=`-1.48`, Ru_9_blt_web_v3=`-6.16`, Ru_9_blt_web=`6.34`
- `w10`: Ru_10_blt_web_v2=`1.48`, Ru_10_blt_web_v3=`-6.16`, Ru_10_blt_web=`6.34`
- `w11`: Ru_11_blt_web_v2=`4.44`, Ru_11_blt_web_v3=`-6.16`, Ru_11_blt_web=`7.59`
- `w12`: Ru_12_blt_web_v2=`7.4`, Ru_12_blt_web_v3=`-6.16`, Ru_12_blt_web=`9.63`

## 6. Elastic Method - Center of Rotation (ECR)

### 6.1 Formulacion

- Ecuaciones:
- `dx_ecr_i_blt_web = x_i_blt_web - x_ecr_blt_web`
- `dy_ecr_i_blt_web = y_i_blt_web - y_ecr_blt_web`
- `r_ecr_i_blt_web = sqrt(dx_ecr_i_blt_web^2 + dy_ecr_i_blt_web^2)`
- `Ru_i_blt_web_v2 = k_ecr_blt_web*dy_ecr_i_blt_web`
- `Ru_i_blt_web_v3 = -k_ecr_blt_web*dx_ecr_i_blt_web`
- Geometria por perno respecto al ECR:

### 6.2 Calculo de ax, ay y coordenadas ECR

- Ecuaciones:
- `ax_blt_web = (Vu2_sp*J_blt_web)/(n_blt_web*Muz_blt_web)`
- `ay_blt_web = (Pu_sp*J_blt_web)/(n_blt_web*Muz_blt_web)`
- `x_ecr_blt_web = x_cg_blt_web + ax_blt_web`
- `y_ecr_blt_web = y_cg_blt_web + ay_blt_web`
- Pu_sp (componente aplicada en direccion v2): `0 kip`
- Vu2_sp (componente aplicada en direccion v3): `56.2 kip`
- n_blt_web: `12`
- J_blt_web: `342 in2`
- Muz_blt_web: `337.21 kip-in`
- ax_blt_web: `4.75 in`
- ay_blt_web: `0 in`
- x_ecr_blt_web: `6.25 in`
- y_ecr_blt_web: `7.5 in`

### 6.3 Geometria por perno respecto al ECR

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_ecr_1_blt_web=`-6.25`, dy_ecr_1_blt_web=`-7.5`, r_ecr_1_blt_web=`9.76`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`3`, dx_ecr_2_blt_web=`-6.25`, dy_ecr_2_blt_web=`-4.5`, r_ecr_2_blt_web=`7.7`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`6`, dx_ecr_3_blt_web=`-6.25`, dy_ecr_3_blt_web=`-1.5`, r_ecr_3_blt_web=`6.43`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`9`, dx_ecr_4_blt_web=`-6.25`, dy_ecr_4_blt_web=`1.5`, r_ecr_4_blt_web=`6.43`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`12`, dx_ecr_5_blt_web=`-6.25`, dy_ecr_5_blt_web=`4.5`, r_ecr_5_blt_web=`7.7`
- `w6`: x_6_blt_web=`0`, y_6_blt_web=`15`, dx_ecr_6_blt_web=`-6.25`, dy_ecr_6_blt_web=`7.5`, r_ecr_6_blt_web=`9.76`
- `w7`: x_7_blt_web=`3`, y_7_blt_web=`0`, dx_ecr_7_blt_web=`-3.25`, dy_ecr_7_blt_web=`-7.5`, r_ecr_7_blt_web=`8.17`
- `w8`: x_8_blt_web=`3`, y_8_blt_web=`3`, dx_ecr_8_blt_web=`-3.25`, dy_ecr_8_blt_web=`-4.5`, r_ecr_8_blt_web=`5.55`
- `w9`: x_9_blt_web=`3`, y_9_blt_web=`6`, dx_ecr_9_blt_web=`-3.25`, dy_ecr_9_blt_web=`-1.5`, r_ecr_9_blt_web=`3.58`
- `w10`: x_10_blt_web=`3`, y_10_blt_web=`9`, dx_ecr_10_blt_web=`-3.25`, dy_ecr_10_blt_web=`1.5`, r_ecr_10_blt_web=`3.58`
- `w11`: x_11_blt_web=`3`, y_11_blt_web=`12`, dx_ecr_11_blt_web=`-3.25`, dy_ecr_11_blt_web=`4.5`, r_ecr_11_blt_web=`5.55`
- `w12`: x_12_blt_web=`3`, y_12_blt_web=`15`, dx_ecr_12_blt_web=`-3.25`, dy_ecr_12_blt_web=`7.5`, r_ecr_12_blt_web=`8.17`

### 6.4 Fuerzas por perno en ECR

- `w1`: Ru_1_blt_web_v2=`-0.86`, Ru_1_blt_web_v3=`0.72`, Ru_1_blt_web=`1.12`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w2`: Ru_2_blt_web_v2=`-0.52`, Ru_2_blt_web_v3=`0.72`, Ru_2_blt_web=`0.88`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w3`: Ru_3_blt_web_v2=`-0.17`, Ru_3_blt_web_v3=`0.72`, Ru_3_blt_web=`0.74`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w4`: Ru_4_blt_web_v2=`0.17`, Ru_4_blt_web_v3=`0.72`, Ru_4_blt_web=`0.74`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w5`: Ru_5_blt_web_v2=`0.52`, Ru_5_blt_web_v3=`0.72`, Ru_5_blt_web=`0.88`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w6`: Ru_6_blt_web_v2=`0.86`, Ru_6_blt_web_v3=`0.72`, Ru_6_blt_web=`1.12`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w7`: Ru_7_blt_web_v2=`-0.86`, Ru_7_blt_web_v3=`0.37`, Ru_7_blt_web=`0.94`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w8`: Ru_8_blt_web_v2=`-0.52`, Ru_8_blt_web_v3=`0.37`, Ru_8_blt_web=`0.64`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w9`: Ru_9_blt_web_v2=`-0.17`, Ru_9_blt_web_v3=`0.37`, Ru_9_blt_web=`0.41`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w10`: Ru_10_blt_web_v2=`0.17`, Ru_10_blt_web_v3=`0.37`, Ru_10_blt_web=`0.41`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w11`: Ru_11_blt_web_v2=`0.52`, Ru_11_blt_web_v3=`0.37`, Ru_11_blt_web=`0.64`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`
- `w12`: Ru_12_blt_web_v2=`0.86`, Ru_12_blt_web_v3=`0.37`, Ru_12_blt_web=`0.94`, x_ecr_blt_web=`6.25`, y_ecr_blt_web=`7.5`

### 6.5 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v2=`-0.86`, Ru_1_blt_web_v3=`0.72`, Ru_1_blt_web=`1.12`
- `w2`: Ru_2_blt_web_v2=`-0.52`, Ru_2_blt_web_v3=`0.72`, Ru_2_blt_web=`0.88`
- `w3`: Ru_3_blt_web_v2=`-0.17`, Ru_3_blt_web_v3=`0.72`, Ru_3_blt_web=`0.74`
- `w4`: Ru_4_blt_web_v2=`0.17`, Ru_4_blt_web_v3=`0.72`, Ru_4_blt_web=`0.74`
- `w5`: Ru_5_blt_web_v2=`0.52`, Ru_5_blt_web_v3=`0.72`, Ru_5_blt_web=`0.88`
- `w6`: Ru_6_blt_web_v2=`0.86`, Ru_6_blt_web_v3=`0.72`, Ru_6_blt_web=`1.12`
- `w7`: Ru_7_blt_web_v2=`-0.86`, Ru_7_blt_web_v3=`0.37`, Ru_7_blt_web=`0.94`
- `w8`: Ru_8_blt_web_v2=`-0.52`, Ru_8_blt_web_v3=`0.37`, Ru_8_blt_web=`0.64`
- `w9`: Ru_9_blt_web_v2=`-0.17`, Ru_9_blt_web_v3=`0.37`, Ru_9_blt_web=`0.41`
- `w10`: Ru_10_blt_web_v2=`0.17`, Ru_10_blt_web_v3=`0.37`, Ru_10_blt_web=`0.41`
- `w11`: Ru_11_blt_web_v2=`0.52`, Ru_11_blt_web_v3=`0.37`, Ru_11_blt_web=`0.64`
- `w12`: Ru_12_blt_web_v2=`0.86`, Ru_12_blt_web_v3=`0.37`, Ru_12_blt_web=`0.94`

## 7. Instant Center of Rotation (ICR)

### 7.1 Formulacion

- Ecuaciones:
- `delta_i_blt_web = (r_icr_i_blt_web/dmax_icr_blt_web)*delta_max_blt_web`
- `phi_i_blt_web = (1-exp(-mu_blt_web*delta_i_blt_web))^lambda_blt_web`
- `sum(phi_i_blt_web*r_icr_i_blt_web)`
- `Rult_blt_web = M_icr_blt_web/sum(phi_i_blt_web*r_icr_i_blt_web)`
- Coordenadas ICR:
- `x_icr_final_blt_web = -2.39 in`
- `y_icr_final_blt_web = 7.5 in`
- Coordenadas por iteracion (`estimacion -> resultado`):
- Iter `1`: estimacion=`(6.25, 7.5) in` -> resultado=`(-3.25, 7.5) in`
- Iter `2`: estimacion=`(-3.25, 7.5) in` -> resultado=`(-3.01, 7.5) in`
- Iter `3`: estimacion=`(-3.01, 7.5) in` -> resultado=`(-2.82, 7.5) in`
- Iter `4`: estimacion=`(-2.82, 7.5) in` -> resultado=`(-2.69, 7.5) in`
- Iter `5`: estimacion=`(-2.69, 7.5) in` -> resultado=`(-2.59, 7.5) in`
- Iter `6`: estimacion=`(-2.59, 7.5) in` -> resultado=`(-2.53, 7.5) in`
- Iter `7`: estimacion=`(-2.53, 7.5) in` -> resultado=`(-2.48, 7.5) in`
- Iter `8`: estimacion=`(-2.48, 7.5) in` -> resultado=`(-2.45, 7.5) in`
- Iter `9`: estimacion=`(-2.45, 7.5) in` -> resultado=`(-2.43, 7.5) in`
- Iter `10`: estimacion=`(-2.43, 7.5) in` -> resultado=`(-2.41, 7.5) in`
- Iter `11`: estimacion=`(-2.41, 7.5) in` -> resultado=`(-2.4, 7.5) in`
- Iter `12`: estimacion=`(-2.4, 7.5) in` -> resultado=`(-2.4, 7.5) in`
- Iter `13`: estimacion=`(-2.4, 7.5) in` -> resultado=`(-2.39, 7.5) in`
- Iter `14`: estimacion=`(-2.39, 7.5) in` -> resultado=`(-2.39, 7.5) in`
- Iter `15`: estimacion=`(-2.39, 7.5) in` -> resultado=`(-2.39, 7.5) in`
- Iter `16`: estimacion=`(-2.39, 7.5) in` -> resultado=`(-2.39, 7.5) in`
- Iter `17`: estimacion=`(-2.39, 7.5) in` -> resultado=`(-2.39, 7.5) in`
- Iter `18`: estimacion=`(-2.39, 7.5) in` -> resultado=`(-2.39, 7.5) in`
- Iteraciones del ICR:

### 7.2 Iteraciones globales (residuales)

- Iter `1`: x_icr_blt_web=`-3.25`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-5.73`, res_norm_blt_web=`5.73`
- Iter `2`: x_icr_blt_web=`-3.01`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-4.35`, res_norm_blt_web=`4.35`
- Iter `3`: x_icr_blt_web=`-2.82`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-3.19`, res_norm_blt_web=`3.19`
- Iter `4`: x_icr_blt_web=`-2.69`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-2.28`, res_norm_blt_web=`2.28`
- Iter `5`: x_icr_blt_web=`-2.59`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-1.59`, res_norm_blt_web=`1.59`
- Iter `6`: x_icr_blt_web=`-2.53`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-1.09`, res_norm_blt_web=`1.09`
- Iter `7`: x_icr_blt_web=`-2.48`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.74`, res_norm_blt_web=`0.74`
- Iter `8`: x_icr_blt_web=`-2.45`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.5`, res_norm_blt_web=`0.5`
- Iter `9`: x_icr_blt_web=`-2.43`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.34`, res_norm_blt_web=`0.34`
- Iter `10`: x_icr_blt_web=`-2.41`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.22`, res_norm_blt_web=`0.22`
- Iter `11`: x_icr_blt_web=`-2.4`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.15`, res_norm_blt_web=`0.15`
- Iter `12`: x_icr_blt_web=`-2.4`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.1`, res_norm_blt_web=`0.1`
- Iter `13`: x_icr_blt_web=`-2.39`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.07`, res_norm_blt_web=`0.07`
- Iter `14`: x_icr_blt_web=`-2.39`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.04`, res_norm_blt_web=`0.04`
- Iter `15`: x_icr_blt_web=`-2.39`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.03`, res_norm_blt_web=`0.03`
- Iter `16`: x_icr_blt_web=`-2.39`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.02`, res_norm_blt_web=`0.02`
- Iter `17`: x_icr_blt_web=`-2.39`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.01`, res_norm_blt_web=`0.01`
- Iter `18`: x_icr_blt_web=`-2.39`, y_icr_blt_web=`7.5`, res_Ru_blt_web_v2=`0`, res_Ru_blt_web_v3=`-0.01`, res_norm_blt_web=`0.01`

### 7.3 Parametros auxiliares por iteracion

- Iter `1`: dmax_icr_blt_web=`9.76`, sum(phi_i_blt_web*r_icr_i_blt_web)=`78.01`, Rult_blt_web=`-7.75`, Cu_blt_web=`7.26`, M_icr_blt_web=`-604.17`
- Iter `2`: dmax_icr_blt_web=`9.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`75.96`, Rult_blt_web=`-7.78`, Cu_blt_web=`7.23`, M_icr_blt_web=`-590.56`
- Iter `3`: dmax_icr_blt_web=`9.5`, sum(phi_i_blt_web*r_icr_i_blt_web)=`74.43`, Rult_blt_web=`-7.8`, Cu_blt_web=`7.21`, M_icr_blt_web=`-580.24`
- Iter `4`: dmax_icr_blt_web=`9.41`, sum(phi_i_blt_web*r_icr_i_blt_web)=`73.33`, Rult_blt_web=`-7.81`, Cu_blt_web=`7.2`, M_icr_blt_web=`-572.66`
- Iter `5`: dmax_icr_blt_web=`9.36`, sum(phi_i_blt_web*r_icr_i_blt_web)=`72.56`, Rult_blt_web=`-7.82`, Cu_blt_web=`7.19`, M_icr_blt_web=`-567.25`
- Iter `6`: dmax_icr_blt_web=`9.32`, sum(phi_i_blt_web*r_icr_i_blt_web)=`72.03`, Rult_blt_web=`-7.82`, Cu_blt_web=`7.18`, M_icr_blt_web=`-563.47`
- Iter `7`: dmax_icr_blt_web=`9.29`, sum(phi_i_blt_web*r_icr_i_blt_web)=`71.66`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.18`, M_icr_blt_web=`-560.87`
- Iter `8`: dmax_icr_blt_web=`9.27`, sum(phi_i_blt_web*r_icr_i_blt_web)=`71.41`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.18`, M_icr_blt_web=`-559.11`
- Iter `9`: dmax_icr_blt_web=`9.26`, sum(phi_i_blt_web*r_icr_i_blt_web)=`71.25`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.18`, M_icr_blt_web=`-557.91`
- Iter `10`: dmax_icr_blt_web=`9.25`, sum(phi_i_blt_web*r_icr_i_blt_web)=`71.14`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.18`, M_icr_blt_web=`-557.12`
- Iter `11`: dmax_icr_blt_web=`9.24`, sum(phi_i_blt_web*r_icr_i_blt_web)=`71.06`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.18`, M_icr_blt_web=`-556.58`
- Iter `12`: dmax_icr_blt_web=`9.24`, sum(phi_i_blt_web*r_icr_i_blt_web)=`71.01`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.18`, M_icr_blt_web=`-556.23`
- Iter `13`: dmax_icr_blt_web=`9.24`, sum(phi_i_blt_web*r_icr_i_blt_web)=`70.98`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.17`, M_icr_blt_web=`-555.99`
- Iter `14`: dmax_icr_blt_web=`9.24`, sum(phi_i_blt_web*r_icr_i_blt_web)=`70.96`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.17`, M_icr_blt_web=`-555.83`
- Iter `15`: dmax_icr_blt_web=`9.23`, sum(phi_i_blt_web*r_icr_i_blt_web)=`70.94`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.17`, M_icr_blt_web=`-555.73`
- Iter `16`: dmax_icr_blt_web=`9.23`, sum(phi_i_blt_web*r_icr_i_blt_web)=`70.93`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.17`, M_icr_blt_web=`-555.66`
- Iter `17`: dmax_icr_blt_web=`9.23`, sum(phi_i_blt_web*r_icr_i_blt_web)=`70.93`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.17`, M_icr_blt_web=`-555.62`
- Iter `18`: dmax_icr_blt_web=`9.23`, sum(phi_i_blt_web*r_icr_i_blt_web)=`70.92`, Rult_blt_web=`-7.83`, Cu_blt_web=`7.17`, M_icr_blt_web=`-555.59`

### 7.4 Bolt Detail ICR por iteracion

#### 7.4.1 Iteracion 1

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`3.25`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`8.17`, delta_1_blt_web=`0.28`
- `w2`: dx_icr_2_blt_web=`3.25`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.55`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`3.25`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`3.58`, delta_3_blt_web=`0.12`
- `w4`: dx_icr_4_blt_web=`3.25`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`3.58`, delta_4_blt_web=`0.12`
- `w5`: dx_icr_5_blt_web=`3.25`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.55`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`3.25`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`8.17`, delta_6_blt_web=`0.28`
- `w7`: dx_icr_7_blt_web=`6.25`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.76`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`6.25`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.7`, delta_8_blt_web=`0.27`
- `w9`: dx_icr_9_blt_web=`6.25`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`6.43`, delta_9_blt_web=`0.22`
- `w10`: dx_icr_10_blt_web=`6.25`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`6.43`, delta_10_blt_web=`0.22`
- `w11`: dx_icr_11_blt_web=`6.25`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.7`, delta_11_blt_web=`0.27`
- `w12`: dx_icr_12_blt_web=`6.25`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.76`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.49`, Ru_1_blt_web_v2=`-6.88`, Ru_1_blt_web_v3=`-2.98`
- `w2`: phi_2_blt_web=`0.92`, Ru_2_blt_web=`-7.11`, Ru_2_blt_web_v2=`-5.76`, Ru_2_blt_web_v3=`-4.16`
- `w3`: phi_3_blt_web=`0.83`, Ru_3_blt_web=`-6.43`, Ru_3_blt_web_v2=`-2.69`, Ru_3_blt_web_v3=`-5.84`
- `w4`: phi_4_blt_web=`0.83`, Ru_4_blt_web=`-6.43`, Ru_4_blt_web_v2=`2.69`, Ru_4_blt_web_v3=`-5.84`
- `w5`: phi_5_blt_web=`0.92`, Ru_5_blt_web=`-7.11`, Ru_5_blt_web_v2=`5.76`, Ru_5_blt_web_v3=`-4.16`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.49`, Ru_6_blt_web_v2=`6.88`, Ru_6_blt_web_v3=`-2.98`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.6`, Ru_7_blt_web_v2=`-5.84`, Ru_7_blt_web_v3=`-4.87`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.45`, Ru_8_blt_web_v2=`-4.35`, Ru_8_blt_web_v3=`-6.05`
- `w9`: phi_9_blt_web=`0.94`, Ru_9_blt_web=`-7.28`, Ru_9_blt_web_v2=`-1.7`, Ru_9_blt_web_v3=`-7.08`
- `w10`: phi_10_blt_web=`0.94`, Ru_10_blt_web=`-7.28`, Ru_10_blt_web_v2=`1.7`, Ru_10_blt_web_v3=`-7.08`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.45`, Ru_11_blt_web_v2=`4.35`, Ru_11_blt_web_v3=`-6.05`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.6`, Ru_12_blt_web_v2=`5.84`, Ru_12_blt_web_v3=`-4.87`

#### 7.4.2 Iteracion 2

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`3.01`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`8.08`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`3.01`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.41`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`3.01`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`3.36`, delta_3_blt_web=`0.12`
- `w4`: dx_icr_4_blt_web=`3.01`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`3.36`, delta_4_blt_web=`0.12`
- `w5`: dx_icr_5_blt_web=`3.01`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.41`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`3.01`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`8.08`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`6.01`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.61`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`6.01`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.51`, delta_8_blt_web=`0.27`
- `w9`: dx_icr_9_blt_web=`6.01`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`6.19`, delta_9_blt_web=`0.22`
- `w10`: dx_icr_10_blt_web=`6.01`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`6.19`, delta_10_blt_web=`0.22`
- `w11`: dx_icr_11_blt_web=`6.01`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.51`, delta_11_blt_web=`0.27`
- `w12`: dx_icr_12_blt_web=`6.01`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.61`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.53`, Ru_1_blt_web_v2=`-6.99`, Ru_1_blt_web_v3=`-2.8`
- `w2`: phi_2_blt_web=`0.92`, Ru_2_blt_web=`-7.12`, Ru_2_blt_web_v2=`-5.92`, Ru_2_blt_web_v3=`-3.96`
- `w3`: phi_3_blt_web=`0.82`, Ru_3_blt_web=`-6.37`, Ru_3_blt_web_v2=`-2.84`, Ru_3_blt_web_v3=`-5.7`
- `w4`: phi_4_blt_web=`0.82`, Ru_4_blt_web=`-6.37`, Ru_4_blt_web_v2=`2.84`, Ru_4_blt_web_v3=`-5.7`
- `w5`: phi_5_blt_web=`0.92`, Ru_5_blt_web=`-7.12`, Ru_5_blt_web_v2=`5.92`, Ru_5_blt_web_v3=`-3.96`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.53`, Ru_6_blt_web_v2=`6.99`, Ru_6_blt_web_v3=`-2.8`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.63`, Ru_7_blt_web_v2=`-5.96`, Ru_7_blt_web_v3=`-4.77`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.47`, Ru_8_blt_web_v2=`-4.48`, Ru_8_blt_web_v3=`-5.98`
- `w9`: phi_9_blt_web=`0.94`, Ru_9_blt_web=`-7.28`, Ru_9_blt_web_v2=`-1.76`, Ru_9_blt_web_v3=`-7.07`
- `w10`: phi_10_blt_web=`0.94`, Ru_10_blt_web=`-7.28`, Ru_10_blt_web_v2=`1.76`, Ru_10_blt_web_v3=`-7.07`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.47`, Ru_11_blt_web_v2=`4.48`, Ru_11_blt_web_v3=`-5.98`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.63`, Ru_12_blt_web_v2=`5.96`, Ru_12_blt_web_v3=`-4.77`

#### 7.4.3 Iteracion 3

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.82`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`8.01`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.82`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.31`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.82`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`3.2`, delta_3_blt_web=`0.11`
- `w4`: dx_icr_4_blt_web=`2.82`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`3.2`, delta_4_blt_web=`0.11`
- `w5`: dx_icr_5_blt_web=`2.82`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.31`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.82`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`8.01`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.82`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.5`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.82`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.36`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.82`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`6.01`, delta_9_blt_web=`0.22`
- `w10`: dx_icr_10_blt_web=`5.82`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`6.01`, delta_10_blt_web=`0.22`
- `w11`: dx_icr_11_blt_web=`5.82`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.36`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.82`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.5`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.55`, Ru_1_blt_web_v2=`-7.06`, Ru_1_blt_web_v3=`-2.66`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.13`, Ru_2_blt_web_v2=`-6.04`, Ru_2_blt_web_v3=`-3.79`
- `w3`: phi_3_blt_web=`0.81`, Ru_3_blt_web=`-6.31`, Ru_3_blt_web_v2=`-2.96`, Ru_3_blt_web_v3=`-5.58`
- `w4`: phi_4_blt_web=`0.81`, Ru_4_blt_web=`-6.31`, Ru_4_blt_web_v2=`2.96`, Ru_4_blt_web_v3=`-5.58`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.13`, Ru_5_blt_web_v2=`6.04`, Ru_5_blt_web_v3=`-3.79`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.55`, Ru_6_blt_web_v2=`7.06`, Ru_6_blt_web_v3=`-2.66`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.65`, Ru_7_blt_web_v2=`-6.04`, Ru_7_blt_web_v3=`-4.69`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.48`, Ru_8_blt_web_v2=`-4.58`, Ru_8_blt_web_v3=`-5.92`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.28`, Ru_9_blt_web_v2=`-1.82`, Ru_9_blt_web_v3=`-7.05`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.28`, Ru_10_blt_web_v2=`1.82`, Ru_10_blt_web_v3=`-7.05`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.48`, Ru_11_blt_web_v2=`4.58`, Ru_11_blt_web_v3=`-5.92`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.65`, Ru_12_blt_web_v2=`6.04`, Ru_12_blt_web_v3=`-4.69`

#### 7.4.4 Iteracion 4

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.69`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.97`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.69`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.24`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.69`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`3.08`, delta_3_blt_web=`0.11`
- `w4`: dx_icr_4_blt_web=`2.69`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`3.08`, delta_4_blt_web=`0.11`
- `w5`: dx_icr_5_blt_web=`2.69`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.24`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.69`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.97`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.69`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.41`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.69`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.25`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.69`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.88`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.69`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.88`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.69`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.25`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.69`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.41`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.56`, Ru_1_blt_web_v2=`-7.12`, Ru_1_blt_web_v3=`-2.55`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.14`, Ru_2_blt_web_v2=`-6.13`, Ru_2_blt_web_v3=`-3.66`
- `w3`: phi_3_blt_web=`0.8`, Ru_3_blt_web=`-6.27`, Ru_3_blt_web_v2=`-3.05`, Ru_3_blt_web_v3=`-5.48`
- `w4`: phi_4_blt_web=`0.8`, Ru_4_blt_web=`-6.27`, Ru_4_blt_web_v2=`3.05`, Ru_4_blt_web_v3=`-5.48`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.14`, Ru_5_blt_web_v2=`6.13`, Ru_5_blt_web_v3=`-3.66`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.56`, Ru_6_blt_web_v2=`7.12`, Ru_6_blt_web_v3=`-2.55`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.66`, Ru_7_blt_web_v2=`-6.11`, Ru_7_blt_web_v3=`-4.63`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.49`, Ru_8_blt_web_v2=`-4.65`, Ru_8_blt_web_v3=`-5.88`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.28`, Ru_9_blt_web_v2=`-1.86`, Ru_9_blt_web_v3=`-7.04`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.28`, Ru_10_blt_web_v2=`1.86`, Ru_10_blt_web_v3=`-7.04`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.49`, Ru_11_blt_web_v2=`4.65`, Ru_11_blt_web_v3=`-5.88`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.66`, Ru_12_blt_web_v2=`6.11`, Ru_12_blt_web_v3=`-4.63`

#### 7.4.5 Iteracion 5

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.59`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.94`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.59`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.19`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.59`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`3`, delta_3_blt_web=`0.11`
- `w4`: dx_icr_4_blt_web=`2.59`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`3`, delta_4_blt_web=`0.11`
- `w5`: dx_icr_5_blt_web=`2.59`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.19`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.59`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.94`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.59`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.36`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.59`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.18`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.59`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.79`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.59`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.79`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.59`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.18`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.59`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.36`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.57`, Ru_1_blt_web_v2=`-7.16`, Ru_1_blt_web_v3=`-2.47`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.14`, Ru_2_blt_web_v2=`-6.19`, Ru_2_blt_web_v3=`-3.57`
- `w3`: phi_3_blt_web=`0.8`, Ru_3_blt_web=`-6.24`, Ru_3_blt_web_v2=`-3.12`, Ru_3_blt_web_v3=`-5.4`
- `w4`: phi_4_blt_web=`0.8`, Ru_4_blt_web=`-6.24`, Ru_4_blt_web_v2=`3.12`, Ru_4_blt_web_v3=`-5.4`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.14`, Ru_5_blt_web_v2=`6.19`, Ru_5_blt_web_v3=`-3.57`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.57`, Ru_6_blt_web_v2=`7.16`, Ru_6_blt_web_v3=`-2.47`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.67`, Ru_7_blt_web_v2=`-6.15`, Ru_7_blt_web_v3=`-4.59`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.7`, Ru_8_blt_web_v3=`-5.84`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.28`, Ru_9_blt_web_v2=`-1.89`, Ru_9_blt_web_v3=`-7.03`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.28`, Ru_10_blt_web_v2=`1.89`, Ru_10_blt_web_v3=`-7.03`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.7`, Ru_11_blt_web_v3=`-5.84`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.67`, Ru_12_blt_web_v2=`6.15`, Ru_12_blt_web_v3=`-4.59`

#### 7.4.6 Iteracion 6

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.53`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.91`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.53`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.16`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.53`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.94`, delta_3_blt_web=`0.11`
- `w4`: dx_icr_4_blt_web=`2.53`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.94`, delta_4_blt_web=`0.11`
- `w5`: dx_icr_5_blt_web=`2.53`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.16`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.53`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.91`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.53`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.32`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.53`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.13`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.53`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.73`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.53`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.73`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.53`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.13`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.53`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.32`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.58`, Ru_1_blt_web_v2=`-7.18`, Ru_1_blt_web_v3=`-2.42`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.14`, Ru_2_blt_web_v2=`-6.23`, Ru_2_blt_web_v3=`-3.5`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.21`, Ru_3_blt_web_v2=`-3.17`, Ru_3_blt_web_v3=`-5.34`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.21`, Ru_4_blt_web_v2=`3.17`, Ru_4_blt_web_v3=`-5.34`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.14`, Ru_5_blt_web_v2=`6.23`, Ru_5_blt_web_v3=`-3.5`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.58`, Ru_6_blt_web_v2=`7.18`, Ru_6_blt_web_v3=`-2.42`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.68`, Ru_7_blt_web_v2=`-6.18`, Ru_7_blt_web_v3=`-4.55`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.73`, Ru_8_blt_web_v3=`-5.81`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.28`, Ru_9_blt_web_v2=`-1.91`, Ru_9_blt_web_v3=`-7.02`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.28`, Ru_10_blt_web_v2=`1.91`, Ru_10_blt_web_v3=`-7.02`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.73`, Ru_11_blt_web_v3=`-5.81`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.68`, Ru_12_blt_web_v2=`6.18`, Ru_12_blt_web_v3=`-4.55`

#### 7.4.7 Iteracion 7

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.48`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.9`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.48`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.14`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.48`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.9`, delta_3_blt_web=`0.11`
- `w4`: dx_icr_4_blt_web=`2.48`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.9`, delta_4_blt_web=`0.11`
- `w5`: dx_icr_5_blt_web=`2.48`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.14`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.48`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.9`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.48`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.29`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.48`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.09`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.48`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.68`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.48`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.68`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.48`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.09`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.48`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.29`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.58`, Ru_1_blt_web_v2=`-7.2`, Ru_1_blt_web_v3=`-2.38`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.26`, Ru_2_blt_web_v3=`-3.45`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.2`, Ru_3_blt_web_v2=`-3.21`, Ru_3_blt_web_v3=`-5.3`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.2`, Ru_4_blt_web_v2=`3.21`, Ru_4_blt_web_v3=`-5.3`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.26`, Ru_5_blt_web_v3=`-3.45`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.58`, Ru_6_blt_web_v2=`7.2`, Ru_6_blt_web_v3=`-2.38`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.68`, Ru_7_blt_web_v2=`-6.2`, Ru_7_blt_web_v3=`-4.53`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.76`, Ru_8_blt_web_v3=`-5.8`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.92`, Ru_9_blt_web_v3=`-7.01`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.92`, Ru_10_blt_web_v3=`-7.01`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.76`, Ru_11_blt_web_v3=`-5.8`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.68`, Ru_12_blt_web_v2=`6.2`, Ru_12_blt_web_v3=`-4.53`

#### 7.4.8 Iteracion 8

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.45`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.89`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.45`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.12`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.45`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.87`, delta_3_blt_web=`0.11`
- `w4`: dx_icr_4_blt_web=`2.45`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.87`, delta_4_blt_web=`0.11`
- `w5`: dx_icr_5_blt_web=`2.45`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.12`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.45`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.89`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.45`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.27`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.45`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.07`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.45`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.65`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.45`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.65`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.45`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.07`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.45`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.27`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.21`, Ru_1_blt_web_v3=`-2.35`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.28`, Ru_2_blt_web_v3=`-3.42`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.18`, Ru_3_blt_web_v2=`-3.23`, Ru_3_blt_web_v3=`-5.27`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.18`, Ru_4_blt_web_v2=`3.23`, Ru_4_blt_web_v3=`-5.27`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.28`, Ru_5_blt_web_v3=`-3.42`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.21`, Ru_6_blt_web_v3=`-2.35`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.68`, Ru_7_blt_web_v2=`-6.22`, Ru_7_blt_web_v3=`-4.52`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.78`, Ru_8_blt_web_v3=`-5.78`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.93`, Ru_9_blt_web_v3=`-7.01`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.93`, Ru_10_blt_web_v3=`-7.01`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.78`, Ru_11_blt_web_v3=`-5.78`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.68`, Ru_12_blt_web_v2=`6.22`, Ru_12_blt_web_v3=`-4.52`

#### 7.4.9 Iteracion 9

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.43`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.88`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.43`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.11`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.43`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.85`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.43`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.85`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.43`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.11`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.43`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.88`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.43`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.26`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.43`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.05`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.43`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.63`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.43`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.63`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.43`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.05`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.43`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.26`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.22`, Ru_1_blt_web_v3=`-2.34`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.29`, Ru_2_blt_web_v3=`-3.39`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.18`, Ru_3_blt_web_v2=`-3.25`, Ru_3_blt_web_v3=`-5.25`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.18`, Ru_4_blt_web_v2=`3.25`, Ru_4_blt_web_v3=`-5.25`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.29`, Ru_5_blt_web_v3=`-3.39`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.22`, Ru_6_blt_web_v3=`-2.34`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.23`, Ru_7_blt_web_v3=`-4.51`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.79`, Ru_8_blt_web_v3=`-5.77`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.94`, Ru_9_blt_web_v3=`-7.01`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.94`, Ru_10_blt_web_v3=`-7.01`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.79`, Ru_11_blt_web_v3=`-5.77`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.23`, Ru_12_blt_web_v3=`-4.51`

#### 7.4.10 Iteracion 10

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.41`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.88`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.41`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.11`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.41`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.84`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.41`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.84`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.41`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.11`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.41`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.88`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.41`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.25`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.41`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.04`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.41`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.62`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.41`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.62`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.41`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.04`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.41`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.25`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.23`, Ru_1_blt_web_v3=`-2.32`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.3`, Ru_2_blt_web_v3=`-3.38`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.17`, Ru_3_blt_web_v2=`-3.26`, Ru_3_blt_web_v3=`-5.24`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.17`, Ru_4_blt_web_v2=`3.26`, Ru_4_blt_web_v3=`-5.24`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.3`, Ru_5_blt_web_v3=`-3.38`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.23`, Ru_6_blt_web_v3=`-2.32`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.23`, Ru_7_blt_web_v3=`-4.5`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.8`, Ru_8_blt_web_v3=`-5.77`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.94`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.94`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.8`, Ru_11_blt_web_v3=`-5.77`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.23`, Ru_12_blt_web_v3=`-4.5`

#### 7.4.11 Iteracion 11

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.4`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.88`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.4`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.1`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.4`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.83`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.4`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.83`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.4`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.1`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.4`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.88`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.4`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.24`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.4`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.03`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.4`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.61`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.4`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.61`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.4`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.03`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.4`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.24`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.23`, Ru_1_blt_web_v3=`-2.32`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.31`, Ru_2_blt_web_v3=`-3.37`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.17`, Ru_3_blt_web_v2=`-3.26`, Ru_3_blt_web_v3=`-5.23`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.17`, Ru_4_blt_web_v2=`3.26`, Ru_4_blt_web_v3=`-5.23`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.31`, Ru_5_blt_web_v3=`-3.37`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.23`, Ru_6_blt_web_v3=`-2.32`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.24`, Ru_7_blt_web_v3=`-4.49`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.8`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.94`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.94`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.8`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.24`, Ru_12_blt_web_v3=`-4.49`

#### 7.4.12 Iteracion 12

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.4`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.87`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.4`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.1`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.4`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.83`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.4`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.83`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.4`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.1`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.4`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.87`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.4`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.24`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.4`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.03`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.4`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.6`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.4`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.6`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.4`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.03`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.4`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.24`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.23`, Ru_1_blt_web_v3=`-2.31`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.31`, Ru_2_blt_web_v3=`-3.36`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.16`, Ru_3_blt_web_v2=`-3.27`, Ru_3_blt_web_v3=`-5.22`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.16`, Ru_4_blt_web_v2=`3.27`, Ru_4_blt_web_v3=`-5.22`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.31`, Ru_5_blt_web_v3=`-3.36`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.23`, Ru_6_blt_web_v3=`-2.31`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.24`, Ru_7_blt_web_v3=`-4.49`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.8`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.95`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.95`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.8`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.24`, Ru_12_blt_web_v3=`-4.49`

#### 7.4.13 Iteracion 13

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.39`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.87`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.39`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.1`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.39`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.82`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.39`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.82`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.39`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.1`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.39`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.87`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.39`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.24`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.39`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.02`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.39`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.6`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.39`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.6`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.39`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.02`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.39`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.24`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.23`, Ru_1_blt_web_v3=`-2.31`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.31`, Ru_2_blt_web_v3=`-3.36`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.16`, Ru_3_blt_web_v2=`-3.27`, Ru_3_blt_web_v3=`-5.22`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.16`, Ru_4_blt_web_v2=`3.27`, Ru_4_blt_web_v3=`-5.22`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.31`, Ru_5_blt_web_v3=`-3.36`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.23`, Ru_6_blt_web_v3=`-2.31`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.24`, Ru_7_blt_web_v3=`-4.49`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.81`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.95`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.95`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.81`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.24`, Ru_12_blt_web_v3=`-4.49`

#### 7.4.14 Iteracion 14

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.39`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.87`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.39`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.1`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.39`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.82`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.39`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.82`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.39`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.1`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.39`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.87`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.39`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.24`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.39`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.02`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.39`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.59`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.39`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.59`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.39`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.02`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.39`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.24`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.23`, Ru_1_blt_web_v3=`-2.31`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.31`, Ru_2_blt_web_v3=`-3.35`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.16`, Ru_3_blt_web_v2=`-3.27`, Ru_3_blt_web_v3=`-5.22`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.16`, Ru_4_blt_web_v2=`3.27`, Ru_4_blt_web_v3=`-5.22`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.31`, Ru_5_blt_web_v3=`-3.35`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.23`, Ru_6_blt_web_v3=`-2.31`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.24`, Ru_7_blt_web_v3=`-4.49`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.81`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.95`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.95`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.81`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.24`, Ru_12_blt_web_v3=`-4.49`

#### 7.4.15 Iteracion 15

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.39`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.87`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.39`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.09`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.39`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.82`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.39`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.82`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.39`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.09`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.39`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.87`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.39`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.23`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.39`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.02`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.39`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.59`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.39`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.59`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.39`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.02`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.39`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.23`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.23`, Ru_1_blt_web_v3=`-2.3`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.31`, Ru_2_blt_web_v3=`-3.35`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.16`, Ru_3_blt_web_v2=`-3.28`, Ru_3_blt_web_v3=`-5.22`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.16`, Ru_4_blt_web_v2=`3.28`, Ru_4_blt_web_v3=`-5.22`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.31`, Ru_5_blt_web_v3=`-3.35`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.23`, Ru_6_blt_web_v3=`-2.3`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.24`, Ru_7_blt_web_v3=`-4.49`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.81`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.95`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.95`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.81`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.24`, Ru_12_blt_web_v3=`-4.49`

#### 7.4.16 Iteracion 16

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.39`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.87`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.39`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.09`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.39`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.82`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.39`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.82`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.39`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.09`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.39`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.87`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.39`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.23`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.39`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.02`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.39`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.59`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.39`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.59`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.39`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.02`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.39`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.23`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.24`, Ru_1_blt_web_v3=`-2.3`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.32`, Ru_2_blt_web_v3=`-3.35`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.16`, Ru_3_blt_web_v2=`-3.28`, Ru_3_blt_web_v3=`-5.21`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.16`, Ru_4_blt_web_v2=`3.28`, Ru_4_blt_web_v3=`-5.21`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.32`, Ru_5_blt_web_v3=`-3.35`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.24`, Ru_6_blt_web_v3=`-2.3`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.24`, Ru_7_blt_web_v3=`-4.49`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.81`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.95`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.95`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.81`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.24`, Ru_12_blt_web_v3=`-4.49`

#### 7.4.17 Iteracion 17

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.39`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.87`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.39`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.09`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.39`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.82`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.39`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.82`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.39`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.09`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.39`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.87`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.39`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.23`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.39`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.02`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.39`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.59`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.39`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.59`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.39`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.02`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.39`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.23`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.24`, Ru_1_blt_web_v3=`-2.3`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.32`, Ru_2_blt_web_v3=`-3.35`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.16`, Ru_3_blt_web_v2=`-3.28`, Ru_3_blt_web_v3=`-5.21`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.16`, Ru_4_blt_web_v2=`3.28`, Ru_4_blt_web_v3=`-5.21`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.32`, Ru_5_blt_web_v3=`-3.35`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.24`, Ru_6_blt_web_v3=`-2.3`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.25`, Ru_7_blt_web_v3=`-4.48`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.81`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.95`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.95`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.81`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.25`, Ru_12_blt_web_v3=`-4.48`

#### 7.4.18 Iteracion 18

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.39`, dy_icr_1_blt_web=`-7.5`, r_icr_1_blt_web=`7.87`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.39`, dy_icr_2_blt_web=`-4.5`, r_icr_2_blt_web=`5.09`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.39`, dy_icr_3_blt_web=`-1.5`, r_icr_3_blt_web=`2.82`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`2.39`, dy_icr_4_blt_web=`1.5`, r_icr_4_blt_web=`2.82`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`2.39`, dy_icr_5_blt_web=`4.5`, r_icr_5_blt_web=`5.09`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.39`, dy_icr_6_blt_web=`7.5`, r_icr_6_blt_web=`7.87`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`5.39`, dy_icr_7_blt_web=`-7.5`, r_icr_7_blt_web=`9.23`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`5.39`, dy_icr_8_blt_web=`-4.5`, r_icr_8_blt_web=`7.02`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`5.39`, dy_icr_9_blt_web=`-1.5`, r_icr_9_blt_web=`5.59`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`5.39`, dy_icr_10_blt_web=`1.5`, r_icr_10_blt_web=`5.59`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`5.39`, dy_icr_11_blt_web=`4.5`, r_icr_11_blt_web=`7.02`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`5.39`, dy_icr_12_blt_web=`7.5`, r_icr_12_blt_web=`9.23`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-7.59`, Ru_1_blt_web_v2=`-7.24`, Ru_1_blt_web_v3=`-2.3`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-7.15`, Ru_2_blt_web_v2=`-6.32`, Ru_2_blt_web_v3=`-3.35`
- `w3`: phi_3_blt_web=`0.79`, Ru_3_blt_web=`-6.16`, Ru_3_blt_web_v2=`-3.28`, Ru_3_blt_web_v3=`-5.21`
- `w4`: phi_4_blt_web=`0.79`, Ru_4_blt_web=`-6.16`, Ru_4_blt_web_v2=`3.28`, Ru_4_blt_web_v3=`-5.21`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-7.15`, Ru_5_blt_web_v2=`6.32`, Ru_5_blt_web_v3=`-3.35`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-7.59`, Ru_6_blt_web_v2=`7.24`, Ru_6_blt_web_v3=`-2.3`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-7.69`, Ru_7_blt_web_v2=`-6.25`, Ru_7_blt_web_v3=`-4.48`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-7.5`, Ru_8_blt_web_v2=`-4.81`, Ru_8_blt_web_v3=`-5.76`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-7.27`, Ru_9_blt_web_v2=`-1.95`, Ru_9_blt_web_v3=`-7`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-7.27`, Ru_10_blt_web_v2=`1.95`, Ru_10_blt_web_v3=`-7`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-7.5`, Ru_11_blt_web_v2=`4.81`, Ru_11_blt_web_v3=`-5.76`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-7.69`, Ru_12_blt_web_v2=`6.25`, Ru_12_blt_web_v3=`-4.48`
