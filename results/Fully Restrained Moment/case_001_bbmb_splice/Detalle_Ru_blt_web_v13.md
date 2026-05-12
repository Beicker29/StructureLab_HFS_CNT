# Reporte Metodos Pernos 1 (Splice)

## 1. Informacion General

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Metodo seleccionado en JSON: `icr`
- Metodo efectivo: `icr`

### 1.1 Variables de carga

- Ecuacion base: `Muz_blt_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- Pu_sp: `0 kN` (origen: `loads.Pu_sp`)
- Vu2_sp: `202.75 kN` (origen: `loads.Vu2_sp`)
- ex_blt_web: `145 mm` (origen: `formula splice`)
- ey_blt_web: `0 mm` (origen: `input ey`)
- Muz_blt_web: `29398.21 kN-mm`

## 2. Geometria de pernos derivada

- Ru_blt_web_v23: `45.58 kip` con `sqrt(Pu_sp^2 + Vu2_sp^2)`
- theta_blt_web: `90 deg` con `atan2(Vu2_sp, Pu_sp)`
- e_blt_web: `5.71 in` con `sqrt(ex_blt_web^2 + ey_blt_web^2)`
- n_blt_web: `10 -` con `conteo pernos activos`
- x_cg_blt_web: `1.28 in` con `sum(x_i_blt_web)/n_blt_web`
- y_cg_blt_web: `5.12 in` con `sum(y_i_blt_web)/n_blt_web`
- Ix_blt_web: `130.98 in2` con `sum((y_i_blt_web-y_cg_blt_web)^2)`
- Iy_blt_web: `16.37 in2` con `sum((x_i_blt_web-x_cg_blt_web)^2)`
- J_blt_web: `147.35 in2` con `Ix_blt_web + Iy_blt_web`
- Muz_blt_web: `260.2 kip-in` con `Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- dmax_blt_web: `5.28 in` con `max(sqrt((x_i_blt_web-x_cg_blt_web)^2+(y_i_blt_web-y_cg_blt_web)^2))`

## 3. Geometria del grupo de pernos

- Perno `w1`: x_1_blt_web=`0 in`, y_1_blt_web=`0 in`, dx_cg_1_blt_web=`-1.28 in`, dy_cg_1_blt_web=`-5.12 in`, r_cg_1_blt_web=`5.28 in`
- Perno `w2`: x_2_blt_web=`0 in`, y_2_blt_web=`2.56 in`, dx_cg_2_blt_web=`-1.28 in`, dy_cg_2_blt_web=`-2.56 in`, r_cg_2_blt_web=`2.86 in`
- Perno `w3`: x_3_blt_web=`0 in`, y_3_blt_web=`5.12 in`, dx_cg_3_blt_web=`-1.28 in`, dy_cg_3_blt_web=`0 in`, r_cg_3_blt_web=`1.28 in`
- Perno `w4`: x_4_blt_web=`0 in`, y_4_blt_web=`7.68 in`, dx_cg_4_blt_web=`-1.28 in`, dy_cg_4_blt_web=`2.56 in`, r_cg_4_blt_web=`2.86 in`
- Perno `w5`: x_5_blt_web=`0 in`, y_5_blt_web=`10.24 in`, dx_cg_5_blt_web=`-1.28 in`, dy_cg_5_blt_web=`5.12 in`, r_cg_5_blt_web=`5.28 in`
- Perno `w6`: x_6_blt_web=`2.56 in`, y_6_blt_web=`0 in`, dx_cg_6_blt_web=`1.28 in`, dy_cg_6_blt_web=`-5.12 in`, r_cg_6_blt_web=`5.28 in`
- Perno `w7`: x_7_blt_web=`2.56 in`, y_7_blt_web=`2.56 in`, dx_cg_7_blt_web=`1.28 in`, dy_cg_7_blt_web=`-2.56 in`, r_cg_7_blt_web=`2.86 in`
- Perno `w8`: x_8_blt_web=`2.56 in`, y_8_blt_web=`5.12 in`, dx_cg_8_blt_web=`1.28 in`, dy_cg_8_blt_web=`0 in`, r_cg_8_blt_web=`1.28 in`
- Perno `w9`: x_9_blt_web=`2.56 in`, y_9_blt_web=`7.68 in`, dx_cg_9_blt_web=`1.28 in`, dy_cg_9_blt_web=`2.56 in`, r_cg_9_blt_web=`2.86 in`
- Perno `w10`: x_10_blt_web=`2.56 in`, y_10_blt_web=`10.24 in`, dx_cg_10_blt_web=`1.28 in`, dy_cg_10_blt_web=`5.12 in`, r_cg_10_blt_web=`5.28 in`

## 4. Resumen global por metodo

- Metodo `elastic_superposition`: applicable=`True`, estado=`PASS`, demanda=`11.32 kip`, capacidad=`14.82 kip`, DCR=`0.76`
- Metodo `elastic_ecr`: applicable=`True`, estado=`PASS`, demanda=`45.58 kip`, capacidad=`59.66 kip`, DCR=`0.76`
- Metodo `icr`: applicable=`True`, estado=`PASS`, demanda=`45.58 kip`, capacidad=`363.21 kip`, DCR=`0.13`

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

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_cg_1_blt_web=`-1.28`, dy_cg_1_blt_web=`-5.12`, r_cg_1_blt_web=`5.28`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`2.56`, dx_cg_2_blt_web=`-1.28`, dy_cg_2_blt_web=`-2.56`, r_cg_2_blt_web=`2.86`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`5.12`, dx_cg_3_blt_web=`-1.28`, dy_cg_3_blt_web=`0`, r_cg_3_blt_web=`1.28`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`7.68`, dx_cg_4_blt_web=`-1.28`, dy_cg_4_blt_web=`2.56`, r_cg_4_blt_web=`2.86`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`10.24`, dx_cg_5_blt_web=`-1.28`, dy_cg_5_blt_web=`5.12`, r_cg_5_blt_web=`5.28`
- `w6`: x_6_blt_web=`2.56`, y_6_blt_web=`0`, dx_cg_6_blt_web=`1.28`, dy_cg_6_blt_web=`-5.12`, r_cg_6_blt_web=`5.28`
- `w7`: x_7_blt_web=`2.56`, y_7_blt_web=`2.56`, dx_cg_7_blt_web=`1.28`, dy_cg_7_blt_web=`-2.56`, r_cg_7_blt_web=`2.86`
- `w8`: x_8_blt_web=`2.56`, y_8_blt_web=`5.12`, dx_cg_8_blt_web=`1.28`, dy_cg_8_blt_web=`0`, r_cg_8_blt_web=`1.28`
- `w9`: x_9_blt_web=`2.56`, y_9_blt_web=`7.68`, dx_cg_9_blt_web=`1.28`, dy_cg_9_blt_web=`2.56`, r_cg_9_blt_web=`2.86`
- `w10`: x_10_blt_web=`2.56`, y_10_blt_web=`10.24`, dx_cg_10_blt_web=`1.28`, dy_cg_10_blt_web=`5.12`, r_cg_10_blt_web=`5.28`

### 5.3 Fuerzas por perno

- `w1`: Ru_dir_1_blt_web_v3=`-0`, Ru_dir_1_blt_web_v2=`-4.56`, Ru_rot_1_blt_web_v3=`-9.04`, Ru_rot_1_blt_web_v2=`2.26`, Ru_1_blt_web=`9.33`
- `w2`: Ru_dir_2_blt_web_v3=`-0`, Ru_dir_2_blt_web_v2=`-4.56`, Ru_rot_2_blt_web_v3=`-4.52`, Ru_rot_2_blt_web_v2=`2.26`, Ru_2_blt_web=`5.07`
- `w3`: Ru_dir_3_blt_web_v3=`-0`, Ru_dir_3_blt_web_v2=`-4.56`, Ru_rot_3_blt_web_v3=`0`, Ru_rot_3_blt_web_v2=`2.26`, Ru_3_blt_web=`2.3`
- `w4`: Ru_dir_4_blt_web_v3=`-0`, Ru_dir_4_blt_web_v2=`-4.56`, Ru_rot_4_blt_web_v3=`4.52`, Ru_rot_4_blt_web_v2=`2.26`, Ru_4_blt_web=`5.07`
- `w5`: Ru_dir_5_blt_web_v3=`-0`, Ru_dir_5_blt_web_v2=`-4.56`, Ru_rot_5_blt_web_v3=`9.04`, Ru_rot_5_blt_web_v2=`2.26`, Ru_5_blt_web=`9.33`
- `w6`: Ru_dir_6_blt_web_v3=`-0`, Ru_dir_6_blt_web_v2=`-4.56`, Ru_rot_6_blt_web_v3=`-9.04`, Ru_rot_6_blt_web_v2=`-2.26`, Ru_6_blt_web=`11.32`
- `w7`: Ru_dir_7_blt_web_v3=`-0`, Ru_dir_7_blt_web_v2=`-4.56`, Ru_rot_7_blt_web_v3=`-4.52`, Ru_rot_7_blt_web_v2=`-2.26`, Ru_7_blt_web=`8.18`
- `w8`: Ru_dir_8_blt_web_v3=`-0`, Ru_dir_8_blt_web_v2=`-4.56`, Ru_rot_8_blt_web_v3=`0`, Ru_rot_8_blt_web_v2=`-2.26`, Ru_8_blt_web=`6.82`
- `w9`: Ru_dir_9_blt_web_v3=`-0`, Ru_dir_9_blt_web_v2=`-4.56`, Ru_rot_9_blt_web_v3=`4.52`, Ru_rot_9_blt_web_v2=`-2.26`, Ru_9_blt_web=`8.18`
- `w10`: Ru_dir_10_blt_web_v3=`-0`, Ru_dir_10_blt_web_v2=`-4.56`, Ru_rot_10_blt_web_v3=`9.04`, Ru_rot_10_blt_web_v2=`-2.26`, Ru_10_blt_web=`11.32`

### 5.4 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v3=`-9.04`, Ru_1_blt_web_v2=`-2.3`, Ru_1_blt_web=`9.33`
- `w2`: Ru_2_blt_web_v3=`-4.52`, Ru_2_blt_web_v2=`-2.3`, Ru_2_blt_web=`5.07`
- `w3`: Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-2.3`, Ru_3_blt_web=`2.3`
- `w4`: Ru_4_blt_web_v3=`4.52`, Ru_4_blt_web_v2=`-2.3`, Ru_4_blt_web=`5.07`
- `w5`: Ru_5_blt_web_v3=`9.04`, Ru_5_blt_web_v2=`-2.3`, Ru_5_blt_web=`9.33`
- `w6`: Ru_6_blt_web_v3=`-9.04`, Ru_6_blt_web_v2=`-6.82`, Ru_6_blt_web=`11.32`
- `w7`: Ru_7_blt_web_v3=`-4.52`, Ru_7_blt_web_v2=`-6.82`, Ru_7_blt_web=`8.18`
- `w8`: Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-6.82`, Ru_8_blt_web=`6.82`
- `w9`: Ru_9_blt_web_v3=`4.52`, Ru_9_blt_web_v2=`-6.82`, Ru_9_blt_web=`8.18`
- `w10`: Ru_10_blt_web_v3=`9.04`, Ru_10_blt_web_v2=`-6.82`, Ru_10_blt_web=`11.32`

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
- Vu2_sp (componente aplicada en direccion v2): `45.58 kip`
- n_blt_web: `10`
- J_blt_web: `147.35 in2`
- Muz_blt_web: `260.2 kip-in`
- ax_blt_web: `2.58 in`
- ay_blt_web: `0 in`
- x_ecr_blt_web: `3.86 in`
- y_ecr_blt_web: `5.12 in`

### 6.3 Geometria por perno respecto al ECR

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_ecr_1_blt_web=`-3.86`, dy_ecr_1_blt_web=`-5.12`, r_ecr_1_blt_web=`6.41`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`2.56`, dx_ecr_2_blt_web=`-3.86`, dy_ecr_2_blt_web=`-2.56`, r_ecr_2_blt_web=`4.63`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`5.12`, dx_ecr_3_blt_web=`-3.86`, dy_ecr_3_blt_web=`0`, r_ecr_3_blt_web=`3.86`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`7.68`, dx_ecr_4_blt_web=`-3.86`, dy_ecr_4_blt_web=`2.56`, r_ecr_4_blt_web=`4.63`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`10.24`, dx_ecr_5_blt_web=`-3.86`, dy_ecr_5_blt_web=`5.12`, r_ecr_5_blt_web=`6.41`
- `w6`: x_6_blt_web=`2.56`, y_6_blt_web=`0`, dx_ecr_6_blt_web=`-1.3`, dy_ecr_6_blt_web=`-5.12`, r_ecr_6_blt_web=`5.28`
- `w7`: x_7_blt_web=`2.56`, y_7_blt_web=`2.56`, dx_ecr_7_blt_web=`-1.3`, dy_ecr_7_blt_web=`-2.56`, r_ecr_7_blt_web=`2.87`
- `w8`: x_8_blt_web=`2.56`, y_8_blt_web=`5.12`, dx_ecr_8_blt_web=`-1.3`, dy_ecr_8_blt_web=`0`, r_ecr_8_blt_web=`1.3`
- `w9`: x_9_blt_web=`2.56`, y_9_blt_web=`7.68`, dx_ecr_9_blt_web=`-1.3`, dy_ecr_9_blt_web=`2.56`, r_ecr_9_blt_web=`2.87`
- `w10`: x_10_blt_web=`2.56`, y_10_blt_web=`10.24`, dx_ecr_10_blt_web=`-1.3`, dy_ecr_10_blt_web=`5.12`, r_ecr_10_blt_web=`5.28`

### 6.4 Fuerzas por perno en ECR

- `w1`: Ru_1_blt_web_v3=`-3.41`, Ru_1_blt_web_v2=`2.57`, Ru_1_blt_web=`4.27`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w2`: Ru_2_blt_web_v3=`-1.7`, Ru_2_blt_web_v2=`2.57`, Ru_2_blt_web=`3.09`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w3`: Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`2.57`, Ru_3_blt_web=`2.57`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w4`: Ru_4_blt_web_v3=`1.7`, Ru_4_blt_web_v2=`2.57`, Ru_4_blt_web=`3.09`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w5`: Ru_5_blt_web_v3=`3.41`, Ru_5_blt_web_v2=`2.57`, Ru_5_blt_web=`4.27`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w6`: Ru_6_blt_web_v3=`-3.41`, Ru_6_blt_web_v2=`0.87`, Ru_6_blt_web=`3.52`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w7`: Ru_7_blt_web_v3=`-1.7`, Ru_7_blt_web_v2=`0.87`, Ru_7_blt_web=`1.91`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w8`: Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`0.87`, Ru_8_blt_web=`0.87`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w9`: Ru_9_blt_web_v3=`1.7`, Ru_9_blt_web_v2=`0.87`, Ru_9_blt_web=`1.91`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`
- `w10`: Ru_10_blt_web_v3=`3.41`, Ru_10_blt_web_v2=`0.87`, Ru_10_blt_web=`3.52`, x_ecr_blt_web=`3.86`, y_ecr_blt_web=`5.12`

### 6.5 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v3=`-3.41`, Ru_1_blt_web_v2=`2.57`, Ru_1_blt_web=`4.27`
- `w2`: Ru_2_blt_web_v3=`-1.7`, Ru_2_blt_web_v2=`2.57`, Ru_2_blt_web=`3.09`
- `w3`: Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`2.57`, Ru_3_blt_web=`2.57`
- `w4`: Ru_4_blt_web_v3=`1.7`, Ru_4_blt_web_v2=`2.57`, Ru_4_blt_web=`3.09`
- `w5`: Ru_5_blt_web_v3=`3.41`, Ru_5_blt_web_v2=`2.57`, Ru_5_blt_web=`4.27`
- `w6`: Ru_6_blt_web_v3=`-3.41`, Ru_6_blt_web_v2=`0.87`, Ru_6_blt_web=`3.52`
- `w7`: Ru_7_blt_web_v3=`-1.7`, Ru_7_blt_web_v2=`0.87`, Ru_7_blt_web=`1.91`
- `w8`: Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`0.87`, Ru_8_blt_web=`0.87`
- `w9`: Ru_9_blt_web_v3=`1.7`, Ru_9_blt_web_v2=`0.87`, Ru_9_blt_web=`1.91`
- `w10`: Ru_10_blt_web_v3=`3.41`, Ru_10_blt_web_v2=`0.87`, Ru_10_blt_web=`3.52`

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
- `x_icr_final_blt_web = -0.82 in`
- `y_icr_final_blt_web = 5.12 in`
- Coordenadas por iteracion (`estimacion -> resultado`):
- Iter `1`: estimacion=`(3.86, 5.12) in` -> resultado=`(-1.3, 5.12) in`
- Iter `2`: estimacion=`(-1.3, 5.12) in` -> resultado=`(-1.12, 5.12) in`
- Iter `3`: estimacion=`(-1.12, 5.12) in` -> resultado=`(-1, 5.12) in`
- Iter `4`: estimacion=`(-1, 5.12) in` -> resultado=`(-0.93, 5.12) in`
- Iter `5`: estimacion=`(-0.93, 5.12) in` -> resultado=`(-0.88, 5.12) in`
- Iter `6`: estimacion=`(-0.88, 5.12) in` -> resultado=`(-0.85, 5.12) in`
- Iter `7`: estimacion=`(-0.85, 5.12) in` -> resultado=`(-0.84, 5.12) in`
- Iter `8`: estimacion=`(-0.84, 5.12) in` -> resultado=`(-0.83, 5.12) in`
- Iter `9`: estimacion=`(-0.83, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `10`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `11`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `12`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `13`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `14`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `15`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `16`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `17`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iter `18`: estimacion=`(-0.82, 5.12) in` -> resultado=`(-0.82, 5.12) in`
- Iteraciones del ICR:

### 7.2 Iteraciones globales (residuales)

- Iter `1`: x_icr_blt_web=`-1.3`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-6.34`, res_norm_blt_web=`6.34`
- Iter `2`: x_icr_blt_web=`-1.12`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-4.21`, res_norm_blt_web=`4.21`
- Iter `3`: x_icr_blt_web=`-1`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-2.66`, res_norm_blt_web=`2.66`
- Iter `4`: x_icr_blt_web=`-0.93`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-1.62`, res_norm_blt_web=`1.62`
- Iter `5`: x_icr_blt_web=`-0.88`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.96`, res_norm_blt_web=`0.96`
- Iter `6`: x_icr_blt_web=`-0.85`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.57`, res_norm_blt_web=`0.57`
- Iter `7`: x_icr_blt_web=`-0.84`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.33`, res_norm_blt_web=`0.33`
- Iter `8`: x_icr_blt_web=`-0.83`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.19`, res_norm_blt_web=`0.19`
- Iter `9`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.11`, res_norm_blt_web=`0.11`
- Iter `10`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.06`, res_norm_blt_web=`0.06`
- Iter `11`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.04`, res_norm_blt_web=`0.04`
- Iter `12`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.02`, res_norm_blt_web=`0.02`
- Iter `13`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.01`
- Iter `14`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.01`
- Iter `15`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `16`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `17`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `18`: x_icr_blt_web=`-0.82`, y_icr_blt_web=`5.12`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`

### 7.3 Parametros auxiliares por iteracion

- Iter `1`: dmax_icr_blt_web=`6.41`, sum(phi_i_blt_web*r_icr_i_blt_web)=`41.09`, Rult_blt_web=`-9.2`, Cu_blt_web=`4.96`, M_icr_blt_web=`-377.84`
- Iter `2`: dmax_icr_blt_web=`6.3`, sum(phi_i_blt_web*r_icr_i_blt_web)=`40.02`, Rult_blt_web=`-9.24`, Cu_blt_web=`4.93`, M_icr_blt_web=`-369.66`
- Iter `3`: dmax_icr_blt_web=`6.24`, sum(phi_i_blt_web*r_icr_i_blt_web)=`39.33`, Rult_blt_web=`-9.26`, Cu_blt_web=`4.92`, M_icr_blt_web=`-364.23`
- Iter `4`: dmax_icr_blt_web=`6.19`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.91`, Rult_blt_web=`-9.27`, Cu_blt_web=`4.92`, M_icr_blt_web=`-360.79`
- Iter `5`: dmax_icr_blt_web=`6.17`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.66`, Rult_blt_web=`-9.28`, Cu_blt_web=`4.91`, M_icr_blt_web=`-358.7`
- Iter `6`: dmax_icr_blt_web=`6.15`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.51`, Rult_blt_web=`-9.28`, Cu_blt_web=`4.91`, M_icr_blt_web=`-357.46`
- Iter `7`: dmax_icr_blt_web=`6.14`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.42`, Rult_blt_web=`-9.28`, Cu_blt_web=`4.91`, M_icr_blt_web=`-356.73`
- Iter `8`: dmax_icr_blt_web=`6.14`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.37`, Rult_blt_web=`-9.28`, Cu_blt_web=`4.91`, M_icr_blt_web=`-356.31`
- Iter `9`: dmax_icr_blt_web=`6.14`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.35`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-356.06`
- Iter `10`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.33`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.92`
- Iter `11`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.32`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.84`
- Iter `12`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.31`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.79`
- Iter `13`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.31`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.77`
- Iter `14`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.31`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.75`
- Iter `15`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.31`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.74`
- Iter `16`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.31`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.74`
- Iter `17`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.31`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.73`
- Iter `18`: dmax_icr_blt_web=`6.13`, sum(phi_i_blt_web*r_icr_i_blt_web)=`38.31`, Rult_blt_web=`-9.29`, Cu_blt_web=`4.91`, M_icr_blt_web=`-355.73`

### 7.4 Bolt Detail ICR por iteracion

#### 7.4.1 Iteracion 1

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.3`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.28`, delta_1_blt_web=`0.28`
- `w2`: dx_icr_2_blt_web=`1.3`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.87`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`1.3`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`1.3`, delta_3_blt_web=`0.07`
- `w4`: dx_icr_4_blt_web=`1.3`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.87`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`1.3`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.28`, delta_5_blt_web=`0.28`
- `w6`: dx_icr_6_blt_web=`3.86`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.41`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.86`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.63`, delta_7_blt_web=`0.25`
- `w8`: dx_icr_8_blt_web=`3.86`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.86`, delta_8_blt_web=`0.2`
- `w9`: dx_icr_9_blt_web=`3.86`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.63`, delta_9_blt_web=`0.25`
- `w10`: dx_icr_10_blt_web=`3.86`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.41`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.88`, Ru_1_blt_web_v3=`-8.61`, Ru_1_blt_web_v2=`-2.19`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.03`, Ru_2_blt_web_v3=`-7.16`, Ru_2_blt_web_v2=`-3.64`
- `w3`: phi_3_blt_web=`0.68`, Ru_3_blt_web=`-6.27`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-6.27`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.03`, Ru_4_blt_web_v3=`7.16`, Ru_4_blt_web_v2=`-3.64`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.88`, Ru_5_blt_web_v3=`8.61`, Ru_5_blt_web_v2=`-2.19`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.03`, Ru_6_blt_web_v3=`-7.21`, Ru_6_blt_web_v2=`-5.44`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.75`, Ru_7_blt_web_v3=`-4.84`, Ru_7_blt_web_v2=`-7.3`
- `w8`: phi_8_blt_web=`0.93`, Ru_8_blt_web=`-8.52`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.52`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.75`, Ru_9_blt_web_v3=`4.84`, Ru_9_blt_web_v2=`-7.3`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.03`, Ru_10_blt_web_v3=`7.21`, Ru_10_blt_web_v2=`-5.44`

#### 7.4.2 Iteracion 2

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1.12`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.24`, delta_1_blt_web=`0.28`
- `w2`: dx_icr_2_blt_web=`1.12`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.79`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`1.12`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`1.12`, delta_3_blt_web=`0.06`
- `w4`: dx_icr_4_blt_web=`1.12`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.79`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`1.12`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.24`, delta_5_blt_web=`0.28`
- `w6`: dx_icr_6_blt_web=`3.68`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.3`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.68`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.48`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.68`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.68`, delta_8_blt_web=`0.2`
- `w9`: dx_icr_9_blt_web=`3.68`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.48`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.68`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.3`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.93`, Ru_1_blt_web_v3=`-8.73`, Ru_1_blt_web_v2=`-1.91`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.05`, Ru_2_blt_web_v3=`-7.37`, Ru_2_blt_web_v2=`-3.23`
- `w3`: phi_3_blt_web=`0.65`, Ru_3_blt_web=`-5.98`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.98`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.05`, Ru_4_blt_web_v3=`7.37`, Ru_4_blt_web_v2=`-3.23`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.93`, Ru_5_blt_web_v3=`8.73`, Ru_5_blt_web_v2=`-1.91`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.07`, Ru_6_blt_web_v3=`-7.36`, Ru_6_blt_web_v2=`-5.29`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.78`, Ru_7_blt_web_v3=`-5.01`, Ru_7_blt_web_v2=`-7.21`
- `w8`: phi_8_blt_web=`0.92`, Ru_8_blt_web=`-8.52`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.52`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.78`, Ru_9_blt_web_v3=`5.01`, Ru_9_blt_web_v2=`-7.21`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.07`, Ru_10_blt_web_v3=`7.36`, Ru_10_blt_web_v2=`-5.29`

#### 7.4.3 Iteracion 3

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`1`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.22`, delta_1_blt_web=`0.28`
- `w2`: dx_icr_2_blt_web=`1`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.75`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`1`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`1`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`1`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.75`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`1`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.22`, delta_5_blt_web=`0.28`
- `w6`: dx_icr_6_blt_web=`3.56`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.24`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.56`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.39`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.56`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.56`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.56`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.39`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.56`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.24`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.96`, Ru_1_blt_web_v3=`-8.79`, Ru_1_blt_web_v2=`-1.72`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.06`, Ru_2_blt_web_v3=`-7.5`, Ru_2_blt_web_v2=`-2.94`
- `w3`: phi_3_blt_web=`0.62`, Ru_3_blt_web=`-5.76`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.76`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.06`, Ru_4_blt_web_v3=`7.5`, Ru_4_blt_web_v2=`-2.94`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.96`, Ru_5_blt_web_v3=`8.79`, Ru_5_blt_web_v2=`-1.72`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.09`, Ru_6_blt_web_v3=`-7.46`, Ru_6_blt_web_v2=`-5.19`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.78`, Ru_7_blt_web_v3=`-5.13`, Ru_7_blt_web_v2=`-7.13`
- `w8`: phi_8_blt_web=`0.92`, Ru_8_blt_web=`-8.5`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.5`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.78`, Ru_9_blt_web_v3=`5.13`, Ru_9_blt_web_v2=`-7.13`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.09`, Ru_10_blt_web_v3=`7.46`, Ru_10_blt_web_v2=`-5.19`

#### 7.4.4 Iteracion 4

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.93`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.2`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.93`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.72`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.93`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.93`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.93`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.72`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.93`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.2`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.49`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.19`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.49`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.32`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.49`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.49`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.49`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.32`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.49`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.19`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.98`, Ru_1_blt_web_v3=`-8.83`, Ru_1_blt_web_v2=`-1.6`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.06`, Ru_2_blt_web_v3=`-7.58`, Ru_2_blt_web_v2=`-2.75`
- `w3`: phi_3_blt_web=`0.6`, Ru_3_blt_web=`-5.59`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.59`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.06`, Ru_4_blt_web_v3=`7.58`, Ru_4_blt_web_v2=`-2.75`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.98`, Ru_5_blt_web_v3=`8.83`, Ru_5_blt_web_v2=`-1.6`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.1`, Ru_6_blt_web_v3=`-7.52`, Ru_6_blt_web_v2=`-5.12`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.2`, Ru_7_blt_web_v2=`-7.08`
- `w8`: phi_8_blt_web=`0.92`, Ru_8_blt_web=`-8.49`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.49`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.2`, Ru_9_blt_web_v2=`-7.08`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.1`, Ru_10_blt_web_v3=`7.52`, Ru_10_blt_web_v2=`-5.12`

#### 7.4.5 Iteracion 5

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.88`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.19`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.88`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.71`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.88`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.88`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.88`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.71`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.88`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.19`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.44`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.17`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.44`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.29`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.44`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.44`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.44`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.29`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.44`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.17`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.98`, Ru_1_blt_web_v3=`-8.85`, Ru_1_blt_web_v2=`-1.53`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.63`, Ru_2_blt_web_v2=`-2.63`
- `w3`: phi_3_blt_web=`0.59`, Ru_3_blt_web=`-5.49`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.49`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.63`, Ru_4_blt_web_v2=`-2.63`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.98`, Ru_5_blt_web_v3=`8.85`, Ru_5_blt_web_v2=`-1.53`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.56`, Ru_6_blt_web_v2=`-5.08`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.24`, Ru_7_blt_web_v2=`-7.05`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.49`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.49`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.24`, Ru_9_blt_web_v2=`-7.05`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.56`, Ru_10_blt_web_v2=`-5.08`

#### 7.4.6 Iteracion 6

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.85`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.19`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.85`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.7`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.85`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.85`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.85`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.7`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.85`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.19`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.41`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.15`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.41`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.27`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.41`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.41`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.41`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.27`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.41`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.15`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.87`, Ru_1_blt_web_v2=`-1.48`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-2.55`
- `w3`: phi_3_blt_web=`0.58`, Ru_3_blt_web=`-5.42`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.42`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.65`, Ru_4_blt_web_v2=`-2.55`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.87`, Ru_5_blt_web_v2=`-1.48`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.58`, Ru_6_blt_web_v2=`-5.05`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.27`, Ru_7_blt_web_v2=`-7.03`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.48`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.48`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.27`, Ru_9_blt_web_v2=`-7.03`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.58`, Ru_10_blt_web_v2=`-5.05`

#### 7.4.7 Iteracion 7

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.84`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.19`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.84`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.84`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.84`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.84`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.84`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.19`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.4`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.14`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.4`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.25`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.4`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.4`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.4`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.25`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.4`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.14`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.87`, Ru_1_blt_web_v2=`-1.45`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.67`, Ru_2_blt_web_v2=`-2.51`
- `w3`: phi_3_blt_web=`0.58`, Ru_3_blt_web=`-5.38`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.38`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.67`, Ru_4_blt_web_v2=`-2.51`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.87`, Ru_5_blt_web_v2=`-1.45`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.59`, Ru_6_blt_web_v2=`-5.04`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.29`, Ru_7_blt_web_v2=`-7.02`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.48`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.48`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.29`, Ru_9_blt_web_v2=`-7.02`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.59`, Ru_10_blt_web_v2=`-5.04`

#### 7.4.8 Iteracion 8

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.83`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.83`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.83`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.83`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.83`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.83`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.39`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.14`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.39`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.25`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.39`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.39`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.39`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.25`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.39`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.14`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.44`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.68`, Ru_2_blt_web_v2=`-2.49`
- `w3`: phi_3_blt_web=`0.58`, Ru_3_blt_web=`-5.36`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.36`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.68`, Ru_4_blt_web_v2=`-2.49`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.44`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.6`, Ru_6_blt_web_v2=`-5.03`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.3`, Ru_7_blt_web_v2=`-7.01`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.3`, Ru_9_blt_web_v2=`-7.01`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.6`, Ru_10_blt_web_v2=`-5.03`

#### 7.4.9 Iteracion 9

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.14`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.14`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.43`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.68`, Ru_2_blt_web_v2=`-2.47`
- `w3`: phi_3_blt_web=`0.58`, Ru_3_blt_web=`-5.35`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.35`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.68`, Ru_4_blt_web_v2=`-2.47`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.43`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.6`, Ru_6_blt_web_v2=`-5.03`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.3`, Ru_7_blt_web_v2=`-7.01`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.3`, Ru_9_blt_web_v2=`-7.01`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.6`, Ru_10_blt_web_v2=`-5.03`

#### 7.4.10 Iteracion 10

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.24`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.24`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.68`, Ru_2_blt_web_v2=`-2.46`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.34`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.34`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.68`, Ru_4_blt_web_v2=`-2.46`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.3`, Ru_7_blt_web_v2=`-7.01`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.3`, Ru_9_blt_web_v2=`-7.01`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.11 Iteracion 11

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.68`, Ru_2_blt_web_v2=`-2.46`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.68`, Ru_4_blt_web_v2=`-2.46`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.12 Iteracion 12

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-2.46`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.69`, Ru_4_blt_web_v2=`-2.46`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.13 Iteracion 13

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-2.45`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.69`, Ru_4_blt_web_v2=`-2.45`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.14 Iteracion 14

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-2.45`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.69`, Ru_4_blt_web_v2=`-2.45`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.15 Iteracion 15

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-2.45`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.69`, Ru_4_blt_web_v2=`-2.45`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.16 Iteracion 16

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-2.45`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.69`, Ru_4_blt_web_v2=`-2.45`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.17 Iteracion 17

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-2.45`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.69`, Ru_4_blt_web_v2=`-2.45`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`

#### 7.4.18 Iteracion 18

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`0.82`, dy_icr_1_blt_web=`-5.12`, r_icr_1_blt_web=`5.18`, delta_1_blt_web=`0.29`
- `w2`: dx_icr_2_blt_web=`0.82`, dy_icr_2_blt_web=`-2.56`, r_icr_2_blt_web=`2.69`, delta_2_blt_web=`0.15`
- `w3`: dx_icr_3_blt_web=`0.82`, dy_icr_3_blt_web=`0`, r_icr_3_blt_web=`0.82`, delta_3_blt_web=`0.05`
- `w4`: dx_icr_4_blt_web=`0.82`, dy_icr_4_blt_web=`2.56`, r_icr_4_blt_web=`2.69`, delta_4_blt_web=`0.15`
- `w5`: dx_icr_5_blt_web=`0.82`, dy_icr_5_blt_web=`5.12`, r_icr_5_blt_web=`5.18`, delta_5_blt_web=`0.29`
- `w6`: dx_icr_6_blt_web=`3.38`, dy_icr_6_blt_web=`-5.12`, r_icr_6_blt_web=`6.13`, delta_6_blt_web=`0.34`
- `w7`: dx_icr_7_blt_web=`3.38`, dy_icr_7_blt_web=`-2.56`, r_icr_7_blt_web=`4.24`, delta_7_blt_web=`0.23`
- `w8`: dx_icr_8_blt_web=`3.38`, dy_icr_8_blt_web=`0`, r_icr_8_blt_web=`3.38`, delta_8_blt_web=`0.19`
- `w9`: dx_icr_9_blt_web=`3.38`, dy_icr_9_blt_web=`2.56`, r_icr_9_blt_web=`4.24`, delta_9_blt_web=`0.23`
- `w10`: dx_icr_10_blt_web=`3.38`, dy_icr_10_blt_web=`5.12`, r_icr_10_blt_web=`6.13`, delta_10_blt_web=`0.34`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.97`, Ru_1_blt_web=`-8.99`, Ru_1_blt_web_v3=`-8.88`, Ru_1_blt_web_v2=`-1.42`
- `w2`: phi_2_blt_web=`0.87`, Ru_2_blt_web=`-8.07`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-2.45`
- `w3`: phi_3_blt_web=`0.57`, Ru_3_blt_web=`-5.33`, Ru_3_blt_web_v3=`0`, Ru_3_blt_web_v2=`-5.33`
- `w4`: phi_4_blt_web=`0.87`, Ru_4_blt_web=`-8.07`, Ru_4_blt_web_v3=`7.69`, Ru_4_blt_web_v2=`-2.45`
- `w5`: phi_5_blt_web=`0.97`, Ru_5_blt_web=`-8.99`, Ru_5_blt_web_v3=`8.88`, Ru_5_blt_web_v2=`-1.42`
- `w6`: phi_6_blt_web=`0.98`, Ru_6_blt_web=`-9.11`, Ru_6_blt_web_v3=`-7.61`, Ru_6_blt_web_v2=`-5.02`
- `w7`: phi_7_blt_web=`0.95`, Ru_7_blt_web=`-8.79`, Ru_7_blt_web_v3=`-5.31`, Ru_7_blt_web_v2=`-7`
- `w8`: phi_8_blt_web=`0.91`, Ru_8_blt_web=`-8.47`, Ru_8_blt_web_v3=`0`, Ru_8_blt_web_v2=`-8.47`
- `w9`: phi_9_blt_web=`0.95`, Ru_9_blt_web=`-8.79`, Ru_9_blt_web_v3=`5.31`, Ru_9_blt_web_v2=`-7`
- `w10`: phi_10_blt_web=`0.98`, Ru_10_blt_web=`-9.11`, Ru_10_blt_web_v3=`7.61`, Ru_10_blt_web_v2=`-5.02`
