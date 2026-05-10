# Reporte Metodos Pernos 1 (Splice)

## 1. Informacion General

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Metodo seleccionado en JSON: `icr`
- Metodo efectivo: `icr`

### 1.1 Variables de carga

- Ecuacion base: `Muz_blt_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- Pu_sp: `0 kN` (origen: `loads.Pu_sp`)
- Vu2_sp: `260 kN` (origen: `loads.Vu2_sp`)
- ex_blt_web: `140 mm` (origen: `formula splice`)
- ey_blt_web: `0 mm` (origen: `input ey`)
- Muz_blt_web: `36400 kN-mm`

## 2. Geometria de pernos derivada

- Ru_blt_web_v23: `58.45 kip` con `sqrt(Pu_sp^2 + Vu2_sp^2)`
- theta_blt_web: `90 deg` con `atan2(Vu2_sp, Pu_sp)`
- e_blt_web: `5.51 in` con `sqrt(ex_blt_web^2 + ey_blt_web^2)`
- n_blt_web: `12 -` con `conteo pernos activos`
- x_cg_blt_web: `1.18 in` con `sum(x_i_blt_web)/n_blt_web`
- y_cg_blt_web: `5.91 in` con `sum(y_i_blt_web)/n_blt_web`
- Ix_blt_web: `195.3 in2` con `sum((y_i_blt_web-y_cg_blt_web)^2)`
- Iy_blt_web: `16.74 in2` con `sum((x_i_blt_web-x_cg_blt_web)^2)`
- J_blt_web: `212.04 in2` con `Ix_blt_web + Iy_blt_web`
- Muz_blt_web: `322.17 kip-in` con `Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- dmax_blt_web: `6.02 in` con `max(sqrt((x_i_blt_web-x_cg_blt_web)^2+(y_i_blt_web-y_cg_blt_web)^2))`

## 3. Geometria del grupo de pernos

- Perno `w1`: x_1_blt_web=`0 in`, y_1_blt_web=`0 in`, dx_cg_1_blt_web=`-1.18 in`, dy_cg_1_blt_web=`-5.91 in`, r_cg_1_blt_web=`6.02 in`
- Perno `w2`: x_2_blt_web=`0 in`, y_2_blt_web=`2.36 in`, dx_cg_2_blt_web=`-1.18 in`, dy_cg_2_blt_web=`-3.54 in`, r_cg_2_blt_web=`3.73 in`
- Perno `w3`: x_3_blt_web=`0 in`, y_3_blt_web=`4.72 in`, dx_cg_3_blt_web=`-1.18 in`, dy_cg_3_blt_web=`-1.18 in`, r_cg_3_blt_web=`1.67 in`
- Perno `w4`: x_4_blt_web=`0 in`, y_4_blt_web=`7.09 in`, dx_cg_4_blt_web=`-1.18 in`, dy_cg_4_blt_web=`1.18 in`, r_cg_4_blt_web=`1.67 in`
- Perno `w5`: x_5_blt_web=`0 in`, y_5_blt_web=`9.45 in`, dx_cg_5_blt_web=`-1.18 in`, dy_cg_5_blt_web=`3.54 in`, r_cg_5_blt_web=`3.73 in`
- Perno `w6`: x_6_blt_web=`0 in`, y_6_blt_web=`11.81 in`, dx_cg_6_blt_web=`-1.18 in`, dy_cg_6_blt_web=`5.91 in`, r_cg_6_blt_web=`6.02 in`
- Perno `w7`: x_7_blt_web=`2.36 in`, y_7_blt_web=`0 in`, dx_cg_7_blt_web=`1.18 in`, dy_cg_7_blt_web=`-5.91 in`, r_cg_7_blt_web=`6.02 in`
- Perno `w8`: x_8_blt_web=`2.36 in`, y_8_blt_web=`2.36 in`, dx_cg_8_blt_web=`1.18 in`, dy_cg_8_blt_web=`-3.54 in`, r_cg_8_blt_web=`3.73 in`
- Perno `w9`: x_9_blt_web=`2.36 in`, y_9_blt_web=`4.72 in`, dx_cg_9_blt_web=`1.18 in`, dy_cg_9_blt_web=`-1.18 in`, r_cg_9_blt_web=`1.67 in`
- Perno `w10`: x_10_blt_web=`2.36 in`, y_10_blt_web=`7.09 in`, dx_cg_10_blt_web=`1.18 in`, dy_cg_10_blt_web=`1.18 in`, r_cg_10_blt_web=`1.67 in`
- Perno `w11`: x_11_blt_web=`2.36 in`, y_11_blt_web=`9.45 in`, dx_cg_11_blt_web=`1.18 in`, dy_cg_11_blt_web=`3.54 in`, r_cg_11_blt_web=`3.73 in`
- Perno `w12`: x_12_blt_web=`2.36 in`, y_12_blt_web=`11.81 in`, dx_cg_12_blt_web=`1.18 in`, dy_cg_12_blt_web=`5.91 in`, r_cg_12_blt_web=`6.02 in`

## 4. Resumen global por metodo

- Metodo `elastic_superposition`: applicable=`True`, estado=`PASS`, demanda=`11.18 kip`, capacidad=`14.82 kip`, DCR=`0.75`
- Metodo `elastic_ecr`: applicable=`True`, estado=`PASS`, demanda=`58.45 kip`, capacidad=`77.49 kip`, DCR=`0.75`
- Metodo `icr`: applicable=`True`, estado=`PASS`, demanda=`58.45 kip`, capacidad=`478.18 kip`, DCR=`0.12`

## 5. Elastic Method - Superposition

### 5.1 Formulacion

- Ecuaciones:
- `Ru_i_blt_web_v3 = -Pu_sp/n_blt_web`
- `Ru_i_blt_web_v2 = -Vu2_sp/n_blt_web`
- `Ru_mz_i_blt_web_v3 = Muz_blt_web*dy_cg_i_blt_web/J_blt_web`
- `Ru_mz_i_blt_web_v2 = -Muz_blt_web*dx_cg_i_blt_web/J_blt_web`
- `Ru_i_blt_web = sqrt((Ru_i_blt_web_v3+Ru_mz_i_blt_web_v3)^2 + (Ru_i_blt_web_v2+Ru_mz_i_blt_web_v2)^2)`
- Geometria por perno:

### 5.2 Geometria por perno

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_cg_1_blt_web=`-1.18`, dy_cg_1_blt_web=`-5.91`, r_cg_1_blt_web=`6.02`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`2.36`, dx_cg_2_blt_web=`-1.18`, dy_cg_2_blt_web=`-3.54`, r_cg_2_blt_web=`3.73`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`4.72`, dx_cg_3_blt_web=`-1.18`, dy_cg_3_blt_web=`-1.18`, r_cg_3_blt_web=`1.67`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`7.09`, dx_cg_4_blt_web=`-1.18`, dy_cg_4_blt_web=`1.18`, r_cg_4_blt_web=`1.67`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`9.45`, dx_cg_5_blt_web=`-1.18`, dy_cg_5_blt_web=`3.54`, r_cg_5_blt_web=`3.73`
- `w6`: x_6_blt_web=`0`, y_6_blt_web=`11.81`, dx_cg_6_blt_web=`-1.18`, dy_cg_6_blt_web=`5.91`, r_cg_6_blt_web=`6.02`
- `w7`: x_7_blt_web=`2.36`, y_7_blt_web=`0`, dx_cg_7_blt_web=`1.18`, dy_cg_7_blt_web=`-5.91`, r_cg_7_blt_web=`6.02`
- `w8`: x_8_blt_web=`2.36`, y_8_blt_web=`2.36`, dx_cg_8_blt_web=`1.18`, dy_cg_8_blt_web=`-3.54`, r_cg_8_blt_web=`3.73`
- `w9`: x_9_blt_web=`2.36`, y_9_blt_web=`4.72`, dx_cg_9_blt_web=`1.18`, dy_cg_9_blt_web=`-1.18`, r_cg_9_blt_web=`1.67`
- `w10`: x_10_blt_web=`2.36`, y_10_blt_web=`7.09`, dx_cg_10_blt_web=`1.18`, dy_cg_10_blt_web=`1.18`, r_cg_10_blt_web=`1.67`
- `w11`: x_11_blt_web=`2.36`, y_11_blt_web=`9.45`, dx_cg_11_blt_web=`1.18`, dy_cg_11_blt_web=`3.54`, r_cg_11_blt_web=`3.73`
- `w12`: x_12_blt_web=`2.36`, y_12_blt_web=`11.81`, dx_cg_12_blt_web=`1.18`, dy_cg_12_blt_web=`5.91`, r_cg_12_blt_web=`6.02`

### 5.3 Fuerzas por perno

- `w1`: Ru_dir_1_blt_web_v3=`-0`, Ru_dir_1_blt_web_v2=`-4.87`, Ru_rot_1_blt_web_v3=`-8.97`, Ru_rot_1_blt_web_v2=`1.79`, Ru_1_blt_web=`9.49`
- `w2`: Ru_dir_2_blt_web_v3=`-0`, Ru_dir_2_blt_web_v2=`-4.87`, Ru_rot_2_blt_web_v3=`-5.38`, Ru_rot_2_blt_web_v2=`1.79`, Ru_2_blt_web=`6.2`
- `w3`: Ru_dir_3_blt_web_v3=`-0`, Ru_dir_3_blt_web_v2=`-4.87`, Ru_rot_3_blt_web_v3=`-1.79`, Ru_rot_3_blt_web_v2=`1.79`, Ru_3_blt_web=`3.56`
- `w4`: Ru_dir_4_blt_web_v3=`-0`, Ru_dir_4_blt_web_v2=`-4.87`, Ru_rot_4_blt_web_v3=`1.79`, Ru_rot_4_blt_web_v2=`1.79`, Ru_4_blt_web=`3.56`
- `w5`: Ru_dir_5_blt_web_v3=`-0`, Ru_dir_5_blt_web_v2=`-4.87`, Ru_rot_5_blt_web_v3=`5.38`, Ru_rot_5_blt_web_v2=`1.79`, Ru_5_blt_web=`6.2`
- `w6`: Ru_dir_6_blt_web_v3=`-0`, Ru_dir_6_blt_web_v2=`-4.87`, Ru_rot_6_blt_web_v3=`8.97`, Ru_rot_6_blt_web_v2=`1.79`, Ru_6_blt_web=`9.49`
- `w7`: Ru_dir_7_blt_web_v3=`-0`, Ru_dir_7_blt_web_v2=`-4.87`, Ru_rot_7_blt_web_v3=`-8.97`, Ru_rot_7_blt_web_v2=`-1.79`, Ru_7_blt_web=`11.18`
- `w8`: Ru_dir_8_blt_web_v3=`-0`, Ru_dir_8_blt_web_v2=`-4.87`, Ru_rot_8_blt_web_v3=`-5.38`, Ru_rot_8_blt_web_v2=`-1.79`, Ru_8_blt_web=`8.57`
- `w9`: Ru_dir_9_blt_web_v3=`-0`, Ru_dir_9_blt_web_v2=`-4.87`, Ru_rot_9_blt_web_v3=`-1.79`, Ru_rot_9_blt_web_v2=`-1.79`, Ru_9_blt_web=`6.9`
- `w10`: Ru_dir_10_blt_web_v3=`-0`, Ru_dir_10_blt_web_v2=`-4.87`, Ru_rot_10_blt_web_v3=`1.79`, Ru_rot_10_blt_web_v2=`-1.79`, Ru_10_blt_web=`6.9`
- `w11`: Ru_dir_11_blt_web_v3=`-0`, Ru_dir_11_blt_web_v2=`-4.87`, Ru_rot_11_blt_web_v3=`5.38`, Ru_rot_11_blt_web_v2=`-1.79`, Ru_11_blt_web=`8.57`
- `w12`: Ru_dir_12_blt_web_v3=`-0`, Ru_dir_12_blt_web_v2=`-4.87`, Ru_rot_12_blt_web_v3=`8.97`, Ru_rot_12_blt_web_v2=`-1.79`, Ru_12_blt_web=`11.18`

### 5.4 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v3=`-8.97`, Ru_1_blt_web_v2=`-3.08`, Ru_1_blt_web=`9.49`
- `w2`: Ru_2_blt_web_v3=`-5.38`, Ru_2_blt_web_v2=`-3.08`, Ru_2_blt_web=`6.2`
- `w3`: Ru_3_blt_web_v3=`-1.79`, Ru_3_blt_web_v2=`-3.08`, Ru_3_blt_web=`3.56`
- `w4`: Ru_4_blt_web_v3=`1.79`, Ru_4_blt_web_v2=`-3.08`, Ru_4_blt_web=`3.56`
- `w5`: Ru_5_blt_web_v3=`5.38`, Ru_5_blt_web_v2=`-3.08`, Ru_5_blt_web=`6.2`
- `w6`: Ru_6_blt_web_v3=`8.97`, Ru_6_blt_web_v2=`-3.08`, Ru_6_blt_web=`9.49`
- `w7`: Ru_7_blt_web_v3=`-8.97`, Ru_7_blt_web_v2=`-6.67`, Ru_7_blt_web=`11.18`
- `w8`: Ru_8_blt_web_v3=`-5.38`, Ru_8_blt_web_v2=`-6.67`, Ru_8_blt_web=`8.57`
- `w9`: Ru_9_blt_web_v3=`-1.79`, Ru_9_blt_web_v2=`-6.67`, Ru_9_blt_web=`6.9`
- `w10`: Ru_10_blt_web_v3=`1.79`, Ru_10_blt_web_v2=`-6.67`, Ru_10_blt_web=`6.9`
- `w11`: Ru_11_blt_web_v3=`5.38`, Ru_11_blt_web_v2=`-6.67`, Ru_11_blt_web=`8.57`
- `w12`: Ru_12_blt_web_v3=`8.97`, Ru_12_blt_web_v2=`-6.67`, Ru_12_blt_web=`11.18`

## 6. Elastic Method - Center of Rotation (ECR)

### 6.1 Formulacion

- Ecuaciones:
- `dx_ecr_i_blt_web = x_i_blt_web - x_ecr_blt_web`
- `dy_ecr_i_blt_web = y_i_blt_web - y_ecr_blt_web`
- `r_ecr_i_blt_web = sqrt(dx_ecr_i_blt_web^2 + dy_ecr_i_blt_web^2)`
- `Ru_i_blt_web_v3 = k_ecr_blt_web*dy_ecr_i_blt_web`
- `Ru_i_blt_web_v2 = -k_ecr_blt_web*dx_ecr_i_blt_web`
- Geometria por perno respecto al ECR:

### 6.2 Calculo de ax, ay y coordenadas ECR

- Ecuaciones:
- `ax_blt_web = (Vu2_sp*J_blt_web)/(n_blt_web*Muz_blt_web)`
- `ay_blt_web = (Pu_sp*J_blt_web)/(n_blt_web*Muz_blt_web)`
- `x_ecr_blt_web = x_cg_blt_web + ax_blt_web`
- `y_ecr_blt_web = y_cg_blt_web + ay_blt_web`
- Pu_sp (componente aplicada en direccion v3): `0 kip`
- Vu2_sp (componente aplicada en direccion v2): `58.45 kip`
- n_blt_web: `12`
- J_blt_web: `212.04 in2`
- Muz_blt_web: `322.17 kip-in`
- ax_blt_web: `3.21 in`
- ay_blt_web: `0 in`
- x_ecr_blt_web: `4.39 in`
- y_ecr_blt_web: `5.91 in`

### 6.3 Geometria por perno respecto al ECR

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_ecr_1_blt_web=`-4.39`, dy_ecr_1_blt_web=`-5.91`, r_ecr_1_blt_web=`7.36`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`2.36`, dx_ecr_2_blt_web=`-4.39`, dy_ecr_2_blt_web=`-3.54`, r_ecr_2_blt_web=`5.64`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`4.72`, dx_ecr_3_blt_web=`-4.39`, dy_ecr_3_blt_web=`-1.18`, r_ecr_3_blt_web=`4.54`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`7.09`, dx_ecr_4_blt_web=`-4.39`, dy_ecr_4_blt_web=`1.18`, r_ecr_4_blt_web=`4.54`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`9.45`, dx_ecr_5_blt_web=`-4.39`, dy_ecr_5_blt_web=`3.54`, r_ecr_5_blt_web=`5.64`
- `w6`: x_6_blt_web=`0`, y_6_blt_web=`11.81`, dx_ecr_6_blt_web=`-4.39`, dy_ecr_6_blt_web=`5.91`, r_ecr_6_blt_web=`7.36`
- `w7`: x_7_blt_web=`2.36`, y_7_blt_web=`0`, dx_ecr_7_blt_web=`-2.02`, dy_ecr_7_blt_web=`-5.91`, r_ecr_7_blt_web=`6.24`
- `w8`: x_8_blt_web=`2.36`, y_8_blt_web=`2.36`, dx_ecr_8_blt_web=`-2.02`, dy_ecr_8_blt_web=`-3.54`, r_ecr_8_blt_web=`4.08`
- `w9`: x_9_blt_web=`2.36`, y_9_blt_web=`4.72`, dx_ecr_9_blt_web=`-2.02`, dy_ecr_9_blt_web=`-1.18`, r_ecr_9_blt_web=`2.34`
- `w10`: x_10_blt_web=`2.36`, y_10_blt_web=`7.09`, dx_ecr_10_blt_web=`-2.02`, dy_ecr_10_blt_web=`1.18`, r_ecr_10_blt_web=`2.34`
- `w11`: x_11_blt_web=`2.36`, y_11_blt_web=`9.45`, dx_ecr_11_blt_web=`-2.02`, dy_ecr_11_blt_web=`3.54`, r_ecr_11_blt_web=`4.08`
- `w12`: x_12_blt_web=`2.36`, y_12_blt_web=`11.81`, dx_ecr_12_blt_web=`-2.02`, dy_ecr_12_blt_web=`5.91`, r_ecr_12_blt_web=`6.24`

### 6.4 Fuerzas por perno en ECR

- `w1`: Ru_1_blt_web_v3=`-2.37`, Ru_1_blt_web_v2=`1.76`, Ru_1_blt_web=`2.96`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w2`: Ru_2_blt_web_v3=`-1.42`, Ru_2_blt_web_v2=`1.76`, Ru_2_blt_web=`2.27`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w3`: Ru_3_blt_web_v3=`-0.47`, Ru_3_blt_web_v2=`1.76`, Ru_3_blt_web=`1.83`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w4`: Ru_4_blt_web_v3=`0.47`, Ru_4_blt_web_v2=`1.76`, Ru_4_blt_web=`1.83`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w5`: Ru_5_blt_web_v3=`1.42`, Ru_5_blt_web_v2=`1.76`, Ru_5_blt_web=`2.27`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w6`: Ru_6_blt_web_v3=`2.37`, Ru_6_blt_web_v2=`1.76`, Ru_6_blt_web=`2.96`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w7`: Ru_7_blt_web_v3=`-2.37`, Ru_7_blt_web_v2=`0.81`, Ru_7_blt_web=`2.51`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w8`: Ru_8_blt_web_v3=`-1.42`, Ru_8_blt_web_v2=`0.81`, Ru_8_blt_web=`1.64`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w9`: Ru_9_blt_web_v3=`-0.47`, Ru_9_blt_web_v2=`0.81`, Ru_9_blt_web=`0.94`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w10`: Ru_10_blt_web_v3=`0.47`, Ru_10_blt_web_v2=`0.81`, Ru_10_blt_web=`0.94`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w11`: Ru_11_blt_web_v3=`1.42`, Ru_11_blt_web_v2=`0.81`, Ru_11_blt_web=`1.64`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`
- `w12`: Ru_12_blt_web_v3=`2.37`, Ru_12_blt_web_v2=`0.81`, Ru_12_blt_web=`2.51`, x_ecr_blt_web=`4.39`, y_ecr_blt_web=`5.91`

### 6.5 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v3=`-2.37`, Ru_1_blt_web_v2=`1.76`, Ru_1_blt_web=`2.96`
- `w2`: Ru_2_blt_web_v3=`-1.42`, Ru_2_blt_web_v2=`1.76`, Ru_2_blt_web=`2.27`
- `w3`: Ru_3_blt_web_v3=`-0.47`, Ru_3_blt_web_v2=`1.76`, Ru_3_blt_web=`1.83`
- `w4`: Ru_4_blt_web_v3=`0.47`, Ru_4_blt_web_v2=`1.76`, Ru_4_blt_web=`1.83`
- `w5`: Ru_5_blt_web_v3=`1.42`, Ru_5_blt_web_v2=`1.76`, Ru_5_blt_web=`2.27`
- `w6`: Ru_6_blt_web_v3=`2.37`, Ru_6_blt_web_v2=`1.76`, Ru_6_blt_web=`2.96`
- `w7`: Ru_7_blt_web_v3=`-2.37`, Ru_7_blt_web_v2=`0.81`, Ru_7_blt_web=`2.51`
- `w8`: Ru_8_blt_web_v3=`-1.42`, Ru_8_blt_web_v2=`0.81`, Ru_8_blt_web=`1.64`
- `w9`: Ru_9_blt_web_v3=`-0.47`, Ru_9_blt_web_v2=`0.81`, Ru_9_blt_web=`0.94`
- `w10`: Ru_10_blt_web_v3=`0.47`, Ru_10_blt_web_v2=`0.81`, Ru_10_blt_web=`0.94`
- `w11`: Ru_11_blt_web_v3=`1.42`, Ru_11_blt_web_v2=`0.81`, Ru_11_blt_web=`1.64`
- `w12`: Ru_12_blt_web_v3=`2.37`, Ru_12_blt_web_v2=`0.81`, Ru_12_blt_web=`2.51`

## 7. Instant Center of Rotation (ICR)

### 7.1 Formulacion

- Ecuaciones:
- `delta_i_blt_web = (r_icr_i_blt_web/dmax_icr_blt_web)*delta_max_blt_web`
- `phi_i_blt_web = (1-exp(-mu_blt_web*delta_i_blt_web))^lambda_blt_web`
- `sum(phi_i_blt_web*r_icr_i_blt_web)`
- `Rult_blt_web = M_icr_blt_web/sum(phi_i_blt_web*r_icr_i_blt_web)`
- Nota tecnica de momentos:
- `sum(Ru_i_blt_web*r_icr_i_blt_web)` corresponde a `M_icr_blt_web` (respecto al ICR), no a `Mu1_blt_web`.
- Para validar `Mu1_blt_web` se debe usar momento respecto al CG: `sum(-Ru_i_blt_web_v3*dy_cg_i_blt_web + Ru_i_blt_web_v2*dx_cg_i_blt_web) ~= -Mu1_blt_web`.
- Coordenadas ICR:
- `x_icr_final_blt_web = -1.41 in`
- `y_icr_final_blt_web = 5.91 in`
- Coordenadas por iteracion (`estimacion -> resultado`):
- Iter `1`: estimacion=`(4.39, 5.91) in` -> resultado=`(-2.02, 5.91) in`
- Iter `2`: estimacion=`(-2.02, 5.91) in` -> resultado=`(-1.82, 5.91) in`
- Iter `3`: estimacion=`(-1.82, 5.91) in` -> resultado=`(-1.68, 5.91) in`
- Iter `4`: estimacion=`(-1.68, 5.91) in` -> resultado=`(-1.58, 5.91) in`
- Iter `5`: estimacion=`(-1.58, 5.91) in` -> resultado=`(-1.51, 5.91) in`
- Iter `6`: estimacion=`(-1.51, 5.91) in` -> resultado=`(-1.47, 5.91) in`
- Iter `7`: estimacion=`(-1.47, 5.91) in` -> resultado=`(-1.45, 5.91) in`
- Iter `8`: estimacion=`(-1.45, 5.91) in` -> resultado=`(-1.43, 5.91) in`
- Iter `9`: estimacion=`(-1.43, 5.91) in` -> resultado=`(-1.42, 5.91) in`
- Iter `10`: estimacion=`(-1.42, 5.91) in` -> resultado=`(-1.42, 5.91) in`
- Iter `11`: estimacion=`(-1.42, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `12`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `13`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `14`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `15`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `16`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `17`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `18`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `19`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iter `20`: estimacion=`(-1.41, 5.91) in` -> resultado=`(-1.41, 5.91) in`
- Iteraciones del ICR:

### 7.2 Iteraciones globales (residuales)

- Iter `1`: x_icr_blt_web=`-2.02`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-7.44`, res_norm_blt_web=`7.44`
- Iter `2`: x_icr_blt_web=`-1.82`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-5.29`, res_norm_blt_web=`5.29`
- Iter `3`: x_icr_blt_web=`-1.68`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-3.58`, res_norm_blt_web=`3.58`
- Iter `4`: x_icr_blt_web=`-1.58`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-2.34`, res_norm_blt_web=`2.34`
- Iter `5`: x_icr_blt_web=`-1.51`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-1.49`, res_norm_blt_web=`1.49`
- Iter `6`: x_icr_blt_web=`-1.47`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.93`, res_norm_blt_web=`0.93`
- Iter `7`: x_icr_blt_web=`-1.45`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.58`, res_norm_blt_web=`0.58`
- Iter `8`: x_icr_blt_web=`-1.43`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.35`, res_norm_blt_web=`0.35`
- Iter `9`: x_icr_blt_web=`-1.42`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.22`, res_norm_blt_web=`0.22`
- Iter `10`: x_icr_blt_web=`-1.42`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.13`, res_norm_blt_web=`0.13`
- Iter `11`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.08`, res_norm_blt_web=`0.08`
- Iter `12`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.05`, res_norm_blt_web=`0.05`
- Iter `13`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.03`, res_norm_blt_web=`0.03`
- Iter `14`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.02`, res_norm_blt_web=`0.02`
- Iter `15`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.01`
- Iter `16`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.01`
- Iter `17`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `18`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `19`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `20`: x_icr_blt_web=`-1.41`, y_icr_blt_web=`5.91`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`

### 7.3 Parametros auxiliares por iteracion

- Iter `1`: dmax_icr_blt_web=`7.36`, sum(phi_i_blt_web*r_icr_i_blt_web)=`57`, Rult_blt_web=`-8.94`, Cu_blt_web=`6.54`, M_icr_blt_web=`-509.55`
- Iter `2`: dmax_icr_blt_web=`7.24`, sum(phi_i_blt_web*r_icr_i_blt_web)=`55.4`, Rult_blt_web=`-8.98`, Cu_blt_web=`6.51`, M_icr_blt_web=`-497.62`
- Iter `3`: dmax_icr_blt_web=`7.15`, sum(phi_i_blt_web*r_icr_i_blt_web)=`54.3`, Rult_blt_web=`-9.01`, Cu_blt_web=`6.49`, M_icr_blt_web=`-489.15`
- Iter `4`: dmax_icr_blt_web=`7.1`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.57`, Rult_blt_web=`-9.02`, Cu_blt_web=`6.48`, M_icr_blt_web=`-483.4`
- Iter `5`: dmax_icr_blt_web=`7.06`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.1`, Rult_blt_web=`-9.03`, Cu_blt_web=`6.47`, M_icr_blt_web=`-479.65`
- Iter `6`: dmax_icr_blt_web=`7.04`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.81`, Rult_blt_web=`-9.04`, Cu_blt_web=`6.47`, M_icr_blt_web=`-477.26`
- Iter `7`: dmax_icr_blt_web=`7.03`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.62`, Rult_blt_web=`-9.04`, Cu_blt_web=`6.47`, M_icr_blt_web=`-475.76`
- Iter `8`: dmax_icr_blt_web=`7.02`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.51`, Rult_blt_web=`-9.04`, Cu_blt_web=`6.46`, M_icr_blt_web=`-474.84`
- Iter `9`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.44`, Rult_blt_web=`-9.04`, Cu_blt_web=`6.46`, M_icr_blt_web=`-474.27`
- Iter `10`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.4`, Rult_blt_web=`-9.04`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.93`
- Iter `11`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.37`, Rult_blt_web=`-9.04`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.72`
- Iter `12`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.36`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.59`
- Iter `13`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.35`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.51`
- Iter `14`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.34`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.46`
- Iter `15`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.34`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.43`
- Iter `16`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.34`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.42`
- Iter `17`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.34`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.41`
- Iter `18`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.34`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.4`
- Iter `19`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.34`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.4`
- Iter `20`: dmax_icr_blt_web=`7.01`, sum(phi_i_blt_web*r_icr_i_blt_web)=`52.34`, Rult_blt_web=`-9.05`, Cu_blt_web=`6.46`, M_icr_blt_web=`-473.39`

### 7.4 Bolt Detail ICR por iteracion

#### 7.4.1 Iteracion 1

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`2.02`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.24`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`2.02`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`4.08`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`2.02`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`2.34`, delta_3_blt_web=`0.11`
- `w4`: dx_icr_4_blt_web=`2.02`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`2.34`, delta_4_blt_web=`0.11`
- `w5`: dx_icr_5_blt_web=`2.02`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`4.08`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`2.02`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.24`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`4.39`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.36`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`4.39`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.64`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`4.39`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`4.54`, delta_9_blt_web=`0.21`
- `w10`: dx_icr_10_blt_web=`4.39`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`4.54`, delta_10_blt_web=`0.21`
- `w11`: dx_icr_11_blt_web=`4.39`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.64`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`4.39`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.36`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.66`, Ru_1_blt_web_v3=`-8.19`, Ru_1_blt_web_v2=`-2.81`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.17`, Ru_2_blt_web_v3=`-7.09`, Ru_2_blt_web_v2=`-4.05`
- `w3`: phi_3_blt_web=`0.8`, Ru_3_blt_web=`-7.12`, Ru_3_blt_web_v3=`-3.59`, Ru_3_blt_web_v2=`-6.15`
- `w4`: phi_4_blt_web=`0.8`, Ru_4_blt_web=`-7.12`, Ru_4_blt_web_v3=`3.59`, Ru_4_blt_web_v2=`-6.15`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.17`, Ru_5_blt_web_v3=`7.09`, Ru_5_blt_web_v2=`-4.05`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.66`, Ru_6_blt_web_v3=`8.19`, Ru_6_blt_web_v2=`-2.81`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.77`, Ru_7_blt_web_v3=`-7.04`, Ru_7_blt_web_v2=`-5.23`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-8.57`, Ru_8_blt_web_v3=`-5.39`, Ru_8_blt_web_v2=`-6.67`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-8.32`, Ru_9_blt_web_v3=`-2.16`, Ru_9_blt_web_v2=`-8.03`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-8.32`, Ru_10_blt_web_v3=`2.16`, Ru_10_blt_web_v2=`-8.03`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-8.57`, Ru_11_blt_web_v3=`5.39`, Ru_11_blt_web_v2=`-6.67`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.77`, Ru_12_blt_web_v3=`7.04`, Ru_12_blt_web_v2=`-5.23`

#### 7.4.2 Iteracion 2

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.82`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.82`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.98`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.82`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`2.17`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`1.82`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`2.17`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`1.82`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.98`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.82`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.18`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`4.18`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.24`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`4.18`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.48`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`4.18`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`4.35`, delta_9_blt_web=`0.2`
- `w10`: dx_icr_10_blt_web=`4.18`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`4.35`, delta_10_blt_web=`0.2`
- `w11`: dx_icr_11_blt_web=`4.18`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.48`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`4.18`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.24`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.71`, Ru_1_blt_web_v3=`-8.32`, Ru_1_blt_web_v2=`-2.57`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.19`, Ru_2_blt_web_v3=`-7.29`, Ru_2_blt_web_v2=`-3.74`
- `w3`: phi_3_blt_web=`0.78`, Ru_3_blt_web=`-7.02`, Ru_3_blt_web_v3=`-3.82`, Ru_3_blt_web_v2=`-5.89`
- `w4`: phi_4_blt_web=`0.78`, Ru_4_blt_web=`-7.02`, Ru_4_blt_web_v3=`3.82`, Ru_4_blt_web_v2=`-5.89`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.19`, Ru_5_blt_web_v3=`7.29`, Ru_5_blt_web_v2=`-3.74`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.71`, Ru_6_blt_web_v3=`8.32`, Ru_6_blt_web_v2=`-2.57`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.82`, Ru_7_blt_web_v3=`-7.19`, Ru_7_blt_web_v2=`-5.1`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-8.6`, Ru_8_blt_web_v3=`-5.56`, Ru_8_blt_web_v2=`-6.56`
- `w9`: phi_9_blt_web=`0.93`, Ru_9_blt_web=`-8.32`, Ru_9_blt_web_v3=`-2.26`, Ru_9_blt_web_v2=`-8.01`
- `w10`: phi_10_blt_web=`0.93`, Ru_10_blt_web=`-8.32`, Ru_10_blt_web_v3=`2.26`, Ru_10_blt_web_v2=`-8.01`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-8.6`, Ru_11_blt_web_v3=`5.56`, Ru_11_blt_web_v2=`-6.56`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.82`, Ru_12_blt_web_v3=`7.19`, Ru_12_blt_web_v2=`-5.1`

#### 7.4.3 Iteracion 3

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.68`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.14`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.68`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.92`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.68`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`2.05`, delta_3_blt_web=`0.1`
- `w4`: dx_icr_4_blt_web=`1.68`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`2.05`, delta_4_blt_web=`0.1`
- `w5`: dx_icr_5_blt_web=`1.68`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.92`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.68`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.14`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`4.04`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.15`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`4.04`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.37`, delta_8_blt_web=`0.26`
- `w9`: dx_icr_9_blt_web=`4.04`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`4.21`, delta_9_blt_web=`0.2`
- `w10`: dx_icr_10_blt_web=`4.04`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`4.21`, delta_10_blt_web=`0.2`
- `w11`: dx_icr_11_blt_web=`4.04`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.37`, delta_11_blt_web=`0.26`
- `w12`: dx_icr_12_blt_web=`4.04`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.15`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.74`, Ru_1_blt_web_v3=`-8.41`, Ru_1_blt_web_v2=`-2.39`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.21`, Ru_2_blt_web_v3=`-7.42`, Ru_2_blt_web_v2=`-3.51`
- `w3`: phi_3_blt_web=`0.77`, Ru_3_blt_web=`-6.94`, Ru_3_blt_web_v3=`-4`, Ru_3_blt_web_v2=`-5.67`
- `w4`: phi_4_blt_web=`0.77`, Ru_4_blt_web=`-6.94`, Ru_4_blt_web_v3=`4`, Ru_4_blt_web_v2=`-5.67`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.21`, Ru_5_blt_web_v3=`7.42`, Ru_5_blt_web_v2=`-3.51`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.74`, Ru_6_blt_web_v3=`8.41`, Ru_6_blt_web_v2=`-2.39`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.84`, Ru_7_blt_web_v3=`-7.3`, Ru_7_blt_web_v2=`-4.99`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-8.62`, Ru_8_blt_web_v3=`-5.68`, Ru_8_blt_web_v2=`-6.48`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.32`, Ru_9_blt_web_v3=`-2.33`, Ru_9_blt_web_v2=`-7.98`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.32`, Ru_10_blt_web_v3=`2.33`, Ru_10_blt_web_v2=`-7.98`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-8.62`, Ru_11_blt_web_v3=`5.68`, Ru_11_blt_web_v2=`-6.48`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.84`, Ru_12_blt_web_v3=`7.3`, Ru_12_blt_web_v2=`-4.99`

#### 7.4.4 Iteracion 4

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.58`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.11`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.58`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.88`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.58`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.97`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.58`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.97`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.58`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.88`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.58`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.11`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.94`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.1`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.94`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.3`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.94`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`4.11`, delta_9_blt_web=`0.2`
- `w10`: dx_icr_10_blt_web=`3.94`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`4.11`, delta_10_blt_web=`0.2`
- `w11`: dx_icr_11_blt_web=`3.94`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.3`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.94`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.1`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.75`, Ru_1_blt_web_v3=`-8.46`, Ru_1_blt_web_v2=`-2.26`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.22`, Ru_2_blt_web_v3=`-7.51`, Ru_2_blt_web_v2=`-3.34`
- `w3`: phi_3_blt_web=`0.76`, Ru_3_blt_web=`-6.88`, Ru_3_blt_web_v3=`-4.12`, Ru_3_blt_web_v2=`-5.51`
- `w4`: phi_4_blt_web=`0.76`, Ru_4_blt_web=`-6.88`, Ru_4_blt_web_v3=`4.12`, Ru_4_blt_web_v2=`-5.51`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.22`, Ru_5_blt_web_v3=`7.51`, Ru_5_blt_web_v2=`-3.34`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.75`, Ru_6_blt_web_v3=`8.46`, Ru_6_blt_web_v2=`-2.26`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.86`, Ru_7_blt_web_v3=`-7.37`, Ru_7_blt_web_v2=`-4.92`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-8.62`, Ru_8_blt_web_v3=`-5.77`, Ru_8_blt_web_v2=`-6.41`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.31`, Ru_9_blt_web_v3=`-2.39`, Ru_9_blt_web_v2=`-7.96`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.31`, Ru_10_blt_web_v3=`2.39`, Ru_10_blt_web_v2=`-7.96`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-8.62`, Ru_11_blt_web_v3=`5.77`, Ru_11_blt_web_v2=`-6.41`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.86`, Ru_12_blt_web_v3=`7.37`, Ru_12_blt_web_v2=`-4.92`

#### 7.4.5 Iteracion 5

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.51`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.1`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.51`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.85`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.51`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.92`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.51`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.92`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.51`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.85`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.51`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.1`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.88`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.06`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.88`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.25`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.88`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`4.05`, delta_9_blt_web=`0.2`
- `w10`: dx_icr_10_blt_web=`3.88`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`4.05`, delta_10_blt_web=`0.2`
- `w11`: dx_icr_11_blt_web=`3.88`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.25`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.88`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.06`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.77`, Ru_1_blt_web_v3=`-8.49`, Ru_1_blt_web_v2=`-2.18`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.56`, Ru_2_blt_web_v2=`-3.23`
- `w3`: phi_3_blt_web=`0.76`, Ru_3_blt_web=`-6.84`, Ru_3_blt_web_v3=`-4.21`, Ru_3_blt_web_v2=`-5.39`
- `w4`: phi_4_blt_web=`0.76`, Ru_4_blt_web=`-6.84`, Ru_4_blt_web_v3=`4.21`, Ru_4_blt_web_v2=`-5.39`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.56`, Ru_5_blt_web_v2=`-3.23`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.77`, Ru_6_blt_web_v3=`8.49`, Ru_6_blt_web_v2=`-2.18`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.87`, Ru_7_blt_web_v3=`-7.41`, Ru_7_blt_web_v2=`-4.86`
- `w8`: phi_8_blt_web=`0.96`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.82`, Ru_8_blt_web_v2=`-6.37`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.3`, Ru_9_blt_web_v3=`-2.42`, Ru_9_blt_web_v2=`-7.94`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.3`, Ru_10_blt_web_v3=`2.42`, Ru_10_blt_web_v2=`-7.94`
- `w11`: phi_11_blt_web=`0.96`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.82`, Ru_11_blt_web_v2=`-6.37`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.87`, Ru_12_blt_web_v3=`7.41`, Ru_12_blt_web_v2=`-4.86`

#### 7.4.6 Iteracion 6

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.47`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.09`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.47`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.84`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.47`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.89`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.47`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.89`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.47`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.84`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.47`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.09`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.83`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.04`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.83`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.22`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.83`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`4.01`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.83`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`4.01`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.83`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.22`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.83`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.04`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.77`, Ru_1_blt_web_v3=`-8.51`, Ru_1_blt_web_v2=`-2.12`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.6`, Ru_2_blt_web_v2=`-3.16`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.81`, Ru_3_blt_web_v3=`-4.26`, Ru_3_blt_web_v2=`-5.31`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.81`, Ru_4_blt_web_v3=`4.26`, Ru_4_blt_web_v2=`-5.31`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.6`, Ru_5_blt_web_v2=`-3.16`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.77`, Ru_6_blt_web_v3=`8.51`, Ru_6_blt_web_v2=`-2.12`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.87`, Ru_7_blt_web_v3=`-7.44`, Ru_7_blt_web_v2=`-4.83`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.86`, Ru_8_blt_web_v2=`-6.34`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.3`, Ru_9_blt_web_v3=`-2.44`, Ru_9_blt_web_v2=`-7.93`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.3`, Ru_10_blt_web_v3=`2.44`, Ru_10_blt_web_v2=`-7.93`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.86`, Ru_11_blt_web_v2=`-6.34`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.87`, Ru_12_blt_web_v3=`7.44`, Ru_12_blt_web_v2=`-4.83`

#### 7.4.7 Iteracion 7

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.45`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.08`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.45`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.83`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.45`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.87`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.45`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.87`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.45`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.83`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.45`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.08`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.81`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.03`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.81`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.2`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.81`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.99`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.81`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.99`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.81`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.2`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.81`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.03`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.52`, Ru_1_blt_web_v2=`-2.09`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.62`, Ru_2_blt_web_v2=`-3.11`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.79`, Ru_3_blt_web_v3=`-4.3`, Ru_3_blt_web_v2=`-5.26`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.79`, Ru_4_blt_web_v3=`4.3`, Ru_4_blt_web_v2=`-5.26`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.62`, Ru_5_blt_web_v2=`-3.11`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.52`, Ru_6_blt_web_v2=`-2.09`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.87`, Ru_7_blt_web_v3=`-7.46`, Ru_7_blt_web_v2=`-4.81`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.88`, Ru_8_blt_web_v2=`-6.32`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.46`, Ru_9_blt_web_v2=`-7.92`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.46`, Ru_10_blt_web_v2=`-7.92`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.88`, Ru_11_blt_web_v2=`-6.32`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.87`, Ru_12_blt_web_v3=`7.46`, Ru_12_blt_web_v2=`-4.81`

#### 7.4.8 Iteracion 8

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.43`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.08`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.43`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.82`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.43`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.86`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.43`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.86`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.43`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.82`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.43`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.08`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.79`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.02`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.79`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.19`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.79`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.97`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.79`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.97`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.79`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.19`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.79`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.02`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.53`, Ru_1_blt_web_v2=`-2.07`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.63`, Ru_2_blt_web_v2=`-3.08`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.78`, Ru_3_blt_web_v3=`-4.32`, Ru_3_blt_web_v2=`-5.23`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.78`, Ru_4_blt_web_v3=`4.32`, Ru_4_blt_web_v2=`-5.23`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.63`, Ru_5_blt_web_v2=`-3.08`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.53`, Ru_6_blt_web_v2=`-2.07`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.47`, Ru_7_blt_web_v2=`-4.8`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.89`, Ru_8_blt_web_v2=`-6.31`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.46`, Ru_9_blt_web_v2=`-7.92`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.46`, Ru_10_blt_web_v2=`-7.92`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.89`, Ru_11_blt_web_v2=`-6.31`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.47`, Ru_12_blt_web_v2=`-4.8`

#### 7.4.9 Iteracion 9

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.42`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.42`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.82`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.42`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.85`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.42`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.85`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.42`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.82`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.42`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.78`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.78`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.18`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.78`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.96`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.78`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.96`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.78`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.18`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.78`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.05`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.64`, Ru_2_blt_web_v2=`-3.06`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.78`, Ru_3_blt_web_v3=`-4.33`, Ru_3_blt_web_v2=`-5.21`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.78`, Ru_4_blt_web_v3=`4.33`, Ru_4_blt_web_v2=`-5.21`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.64`, Ru_5_blt_web_v2=`-3.06`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.05`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.47`, Ru_7_blt_web_v2=`-4.79`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.9`, Ru_8_blt_web_v2=`-6.3`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.47`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.47`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.9`, Ru_11_blt_web_v2=`-6.3`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.47`, Ru_12_blt_web_v2=`-4.79`

#### 7.4.10 Iteracion 10

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.42`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.42`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.82`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.42`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.42`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.42`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.82`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.42`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.78`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.78`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.18`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.78`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.96`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.78`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.96`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.78`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.18`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.78`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.05`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.05`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.34`, Ru_3_blt_web_v2=`-5.2`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.34`, Ru_4_blt_web_v2=`-5.2`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.05`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.05`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.3`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.47`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.47`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.3`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.11 Iteracion 11

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.18`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.18`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.04`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.05`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.34`, Ru_3_blt_web_v2=`-5.19`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.34`, Ru_4_blt_web_v2=`-5.19`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.05`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.04`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.12 Iteracion 12

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.18`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.18`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.04`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.19`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.19`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.04`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.13 Iteracion 13

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.04`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.19`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.19`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.04`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.14 Iteracion 14

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.04`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.18`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.18`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.04`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.15 Iteracion 15

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.03`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.18`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.18`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.03`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.16 Iteracion 16

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.03`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.18`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.18`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.03`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.17 Iteracion 17

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.03`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.18`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.18`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.03`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.18 Iteracion 18

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.03`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.18`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.18`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.03`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.19 Iteracion 19

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.03`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.18`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.18`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.03`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`

#### 7.4.20 Iteracion 20

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.41`, dy_icr_1_blt_web=`-5.91`, r_icr_1_blt_web=`6.07`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`1.41`, dy_icr_2_blt_web=`-3.54`, r_icr_2_blt_web=`3.81`, delta_2_blt_web=`0.19`
- `w3`: dx_icr_3_blt_web=`1.41`, dy_icr_3_blt_web=`-1.18`, r_icr_3_blt_web=`1.84`, delta_3_blt_web=`0.09`
- `w4`: dx_icr_4_blt_web=`1.41`, dy_icr_4_blt_web=`1.18`, r_icr_4_blt_web=`1.84`, delta_4_blt_web=`0.09`
- `w5`: dx_icr_5_blt_web=`1.41`, dy_icr_5_blt_web=`3.54`, r_icr_5_blt_web=`3.81`, delta_5_blt_web=`0.19`
- `w6`: dx_icr_6_blt_web=`1.41`, dy_icr_6_blt_web=`5.91`, r_icr_6_blt_web=`6.07`, delta_6_blt_web=`0.29`
- `w7`: dx_icr_7_blt_web=`3.77`, dy_icr_7_blt_web=`-5.91`, r_icr_7_blt_web=`7.01`, delta_7_blt_web=`0.34`
- `w8`: dx_icr_8_blt_web=`3.77`, dy_icr_8_blt_web=`-3.54`, r_icr_8_blt_web=`5.17`, delta_8_blt_web=`0.25`
- `w9`: dx_icr_9_blt_web=`3.77`, dy_icr_9_blt_web=`-1.18`, r_icr_9_blt_web=`3.95`, delta_9_blt_web=`0.19`
- `w10`: dx_icr_10_blt_web=`3.77`, dy_icr_10_blt_web=`1.18`, r_icr_10_blt_web=`3.95`, delta_10_blt_web=`0.19`
- `w11`: dx_icr_11_blt_web=`3.77`, dy_icr_11_blt_web=`3.54`, r_icr_11_blt_web=`5.17`, delta_11_blt_web=`0.25`
- `w12`: dx_icr_12_blt_web=`3.77`, dy_icr_12_blt_web=`5.91`, r_icr_12_blt_web=`7.01`, delta_12_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.78`, Ru_1_blt_web_v3=`-8.54`, Ru_1_blt_web_v2=`-2.03`
- `w2`: phi_2_blt_web=`0.91`, Ru_2_blt_web=`-8.23`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-3.04`
- `w3`: phi_3_blt_web=`0.75`, Ru_3_blt_web=`-6.77`, Ru_3_blt_web_v3=`-4.35`, Ru_3_blt_web_v2=`-5.18`
- `w4`: phi_4_blt_web=`0.75`, Ru_4_blt_web=`-6.77`, Ru_4_blt_web_v3=`4.35`, Ru_4_blt_web_v2=`-5.18`
- `w5`: phi_5_blt_web=`0.91`, Ru_5_blt_web=`-8.23`, Ru_5_blt_web_v3=`7.65`, Ru_5_blt_web_v2=`-3.04`
- `w6`: phi_6_blt_web=`0.97`, Ru_6_blt_web=`-8.78`, Ru_6_blt_web_v3=`8.54`, Ru_6_blt_web_v2=`-2.03`
- `w7`: phi_7_blt_web=`0.98`, Ru_7_blt_web=`-8.88`, Ru_7_blt_web_v3=`-7.48`, Ru_7_blt_web_v2=`-4.78`
- `w8`: phi_8_blt_web=`0.95`, Ru_8_blt_web=`-8.63`, Ru_8_blt_web_v3=`-5.91`, Ru_8_blt_web_v2=`-6.29`
- `w9`: phi_9_blt_web=`0.92`, Ru_9_blt_web=`-8.29`, Ru_9_blt_web_v3=`-2.48`, Ru_9_blt_web_v2=`-7.91`
- `w10`: phi_10_blt_web=`0.92`, Ru_10_blt_web=`-8.29`, Ru_10_blt_web_v3=`2.48`, Ru_10_blt_web_v2=`-7.91`
- `w11`: phi_11_blt_web=`0.95`, Ru_11_blt_web=`-8.63`, Ru_11_blt_web_v3=`5.91`, Ru_11_blt_web_v2=`-6.29`
- `w12`: phi_12_blt_web=`0.98`, Ru_12_blt_web=`-8.88`, Ru_12_blt_web_v3=`7.48`, Ru_12_blt_web_v2=`-4.78`
