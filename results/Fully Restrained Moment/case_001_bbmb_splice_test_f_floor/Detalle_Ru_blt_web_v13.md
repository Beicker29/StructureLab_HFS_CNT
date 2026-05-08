# Reporte Metodos Pernos 1 (Splice)

## 1. Informacion General

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Metodo seleccionado en JSON: `icr`
- Metodo efectivo: `icr`

### 1.1 Variables de carga

- Ecuacion base: `Muz_blt_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- Pu_sp: `66.99 kN` (origen: `loads.Pu_sp`)
- Vu2_sp: `250 kN` (origen: `loads.Vu2_sp`)
- ex_blt_web: `76.2 mm` (origen: `formula splice`)
- ey_blt_web: `0 mm` (origen: `input ey`)
- Muz_blt_web: `19050 kN-mm`

## 2. Geometria de pernos derivada

- Ru_blt_web_v23: `58.18 kip` con `sqrt(Pu_sp^2 + Vu2_sp^2)`
- theta_blt_web: `75 deg` con `atan2(Vu2_sp, Pu_sp)`
- e_blt_web: `3 in` con `sqrt(ex_blt_web^2 + ey_blt_web^2)`
- n_blt_web: `6 -` con `conteo pernos activos`
- x_cg_blt_web: `0 in` con `sum(x_i_blt_web)/n_blt_web`
- y_cg_blt_web: `7.5 in` con `sum(y_i_blt_web)/n_blt_web`
- Ix_blt_web: `157.5 in2` con `sum((y_i_blt_web-y_cg_blt_web)^2)`
- Iy_blt_web: `0 in2` con `sum((x_i_blt_web-x_cg_blt_web)^2)`
- J_blt_web: `157.5 in2` con `Ix_blt_web + Iy_blt_web`
- Muz_blt_web: `168.61 kip-in` con `Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- dmax_blt_web: `7.5 in` con `max(sqrt((x_i_blt_web-x_cg_blt_web)^2+(y_i_blt_web-y_cg_blt_web)^2))`

## 3. Geometria del grupo de pernos

- Perno `w1`: x_1_blt_web=`0 in`, y_1_blt_web=`0 in`, dx_cg_1_blt_web=`0 in`, dy_cg_1_blt_web=`-7.5 in`, r_cg_1_blt_web=`7.5 in`
- Perno `w2`: x_2_blt_web=`0 in`, y_2_blt_web=`3 in`, dx_cg_2_blt_web=`0 in`, dy_cg_2_blt_web=`-4.5 in`, r_cg_2_blt_web=`4.5 in`
- Perno `w3`: x_3_blt_web=`0 in`, y_3_blt_web=`6 in`, dx_cg_3_blt_web=`0 in`, dy_cg_3_blt_web=`-1.5 in`, r_cg_3_blt_web=`1.5 in`
- Perno `w4`: x_4_blt_web=`0 in`, y_4_blt_web=`9 in`, dx_cg_4_blt_web=`0 in`, dy_cg_4_blt_web=`1.5 in`, r_cg_4_blt_web=`1.5 in`
- Perno `w5`: x_5_blt_web=`0 in`, y_5_blt_web=`12 in`, dx_cg_5_blt_web=`0 in`, dy_cg_5_blt_web=`4.5 in`, r_cg_5_blt_web=`4.5 in`
- Perno `w6`: x_6_blt_web=`0 in`, y_6_blt_web=`15 in`, dx_cg_6_blt_web=`0 in`, dy_cg_6_blt_web=`7.5 in`, r_cg_6_blt_web=`7.5 in`

## 4. Resumen global por metodo

- Metodo `elastic_superposition`: applicable=`True`, estado=`PASS`, demanda=`14.1 kip`, capacidad=`14.82 kip`, DCR=`0.95`
- Metodo `elastic_ecr`: applicable=`True`, estado=`PASS`, demanda=`58.18 kip`, capacidad=`61.15 kip`, DCR=`0.95`
- Metodo `icr`: applicable=`True`, estado=`PASS`, demanda=`58.18 kip`, capacidad=`363.73 kip`, DCR=`0.16`

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

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_cg_1_blt_web=`0`, dy_cg_1_blt_web=`-7.5`, r_cg_1_blt_web=`7.5`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`3`, dx_cg_2_blt_web=`0`, dy_cg_2_blt_web=`-4.5`, r_cg_2_blt_web=`4.5`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`6`, dx_cg_3_blt_web=`0`, dy_cg_3_blt_web=`-1.5`, r_cg_3_blt_web=`1.5`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`9`, dx_cg_4_blt_web=`0`, dy_cg_4_blt_web=`1.5`, r_cg_4_blt_web=`1.5`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`12`, dx_cg_5_blt_web=`0`, dy_cg_5_blt_web=`4.5`, r_cg_5_blt_web=`4.5`
- `w6`: x_6_blt_web=`0`, y_6_blt_web=`15`, dx_cg_6_blt_web=`0`, dy_cg_6_blt_web=`7.5`, r_cg_6_blt_web=`7.5`

### 5.3 Fuerzas por perno

- `w1`: Ru_dir_1_blt_web_v3=`-2.51`, Ru_dir_1_blt_web_v2=`-9.37`, Ru_rot_1_blt_web_v3=`-8.03`, Ru_rot_1_blt_web_v2=`-0`, Ru_1_blt_web=`14.1`
- `w2`: Ru_dir_2_blt_web_v3=`-2.51`, Ru_dir_2_blt_web_v2=`-9.37`, Ru_rot_2_blt_web_v3=`-4.82`, Ru_rot_2_blt_web_v2=`-0`, Ru_2_blt_web=`11.89`
- `w3`: Ru_dir_3_blt_web_v3=`-2.51`, Ru_dir_3_blt_web_v2=`-9.37`, Ru_rot_3_blt_web_v3=`-1.61`, Ru_rot_3_blt_web_v2=`-0`, Ru_3_blt_web=`10.23`
- `w4`: Ru_dir_4_blt_web_v3=`-2.51`, Ru_dir_4_blt_web_v2=`-9.37`, Ru_rot_4_blt_web_v3=`1.61`, Ru_rot_4_blt_web_v2=`-0`, Ru_4_blt_web=`9.41`
- `w5`: Ru_dir_5_blt_web_v3=`-2.51`, Ru_dir_5_blt_web_v2=`-9.37`, Ru_rot_5_blt_web_v3=`4.82`, Ru_rot_5_blt_web_v2=`-0`, Ru_5_blt_web=`9.65`
- `w6`: Ru_dir_6_blt_web_v3=`-2.51`, Ru_dir_6_blt_web_v2=`-9.37`, Ru_rot_6_blt_web_v3=`8.03`, Ru_rot_6_blt_web_v2=`-0`, Ru_6_blt_web=`10.87`

### 5.4 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v3=`-10.54`, Ru_1_blt_web_v2=`-9.37`, Ru_1_blt_web=`14.1`
- `w2`: Ru_2_blt_web_v3=`-7.33`, Ru_2_blt_web_v2=`-9.37`, Ru_2_blt_web=`11.89`
- `w3`: Ru_3_blt_web_v3=`-4.12`, Ru_3_blt_web_v2=`-9.37`, Ru_3_blt_web=`10.23`
- `w4`: Ru_4_blt_web_v3=`-0.9`, Ru_4_blt_web_v2=`-9.37`, Ru_4_blt_web=`9.41`
- `w5`: Ru_5_blt_web_v3=`2.31`, Ru_5_blt_web_v2=`-9.37`, Ru_5_blt_web=`9.65`
- `w6`: Ru_6_blt_web_v3=`5.52`, Ru_6_blt_web_v2=`-9.37`, Ru_6_blt_web=`10.87`

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
- Pu_sp (componente aplicada en direccion v3): `15.06 kip`
- Vu2_sp (componente aplicada en direccion v2): `56.2 kip`
- n_blt_web: `6`
- J_blt_web: `157.5 in2`
- Muz_blt_web: `168.61 kip-in`
- ax_blt_web: `8.75 in`
- ay_blt_web: `2.34 in`
- x_ecr_blt_web: `8.75 in`
- y_ecr_blt_web: `9.84 in`

### 6.3 Geometria por perno respecto al ECR

- `w1`: x_1_blt_web=`0`, y_1_blt_web=`0`, dx_ecr_1_blt_web=`-8.75`, dy_ecr_1_blt_web=`-9.84`, r_ecr_1_blt_web=`13.17`
- `w2`: x_2_blt_web=`0`, y_2_blt_web=`3`, dx_ecr_2_blt_web=`-8.75`, dy_ecr_2_blt_web=`-6.84`, r_ecr_2_blt_web=`11.11`
- `w3`: x_3_blt_web=`0`, y_3_blt_web=`6`, dx_ecr_3_blt_web=`-8.75`, dy_ecr_3_blt_web=`-3.84`, r_ecr_3_blt_web=`9.56`
- `w4`: x_4_blt_web=`0`, y_4_blt_web=`9`, dx_ecr_4_blt_web=`-8.75`, dy_ecr_4_blt_web=`-0.84`, r_ecr_4_blt_web=`8.79`
- `w5`: x_5_blt_web=`0`, y_5_blt_web=`12`, dx_ecr_5_blt_web=`-8.75`, dy_ecr_5_blt_web=`2.16`, r_ecr_5_blt_web=`9.01`
- `w6`: x_6_blt_web=`0`, y_6_blt_web=`15`, dx_ecr_6_blt_web=`-8.75`, dy_ecr_6_blt_web=`5.16`, r_ecr_6_blt_web=`10.16`

### 6.4 Fuerzas por perno en ECR

- `w1`: Ru_1_blt_web_v3=`4.36`, Ru_1_blt_web_v2=`-3.88`, Ru_1_blt_web=`5.83`, x_ecr_blt_web=`8.75`, y_ecr_blt_web=`9.84`
- `w2`: Ru_2_blt_web_v3=`3.03`, Ru_2_blt_web_v2=`-3.88`, Ru_2_blt_web=`4.92`, x_ecr_blt_web=`8.75`, y_ecr_blt_web=`9.84`
- `w3`: Ru_3_blt_web_v3=`1.7`, Ru_3_blt_web_v2=`-3.88`, Ru_3_blt_web=`4.23`, x_ecr_blt_web=`8.75`, y_ecr_blt_web=`9.84`
- `w4`: Ru_4_blt_web_v3=`0.37`, Ru_4_blt_web_v2=`-3.88`, Ru_4_blt_web=`3.89`, x_ecr_blt_web=`8.75`, y_ecr_blt_web=`9.84`
- `w5`: Ru_5_blt_web_v3=`-0.95`, Ru_5_blt_web_v2=`-3.88`, Ru_5_blt_web=`3.99`, x_ecr_blt_web=`8.75`, y_ecr_blt_web=`9.84`
- `w6`: Ru_6_blt_web_v3=`-2.28`, Ru_6_blt_web_v2=`-3.88`, Ru_6_blt_web=`4.5`, x_ecr_blt_web=`8.75`, y_ecr_blt_web=`9.84`

### 6.5 Resumen de fuerzas en pernos

- `w1`: Ru_1_blt_web_v3=`4.36`, Ru_1_blt_web_v2=`-3.88`, Ru_1_blt_web=`5.83`
- `w2`: Ru_2_blt_web_v3=`3.03`, Ru_2_blt_web_v2=`-3.88`, Ru_2_blt_web=`4.92`
- `w3`: Ru_3_blt_web_v3=`1.7`, Ru_3_blt_web_v2=`-3.88`, Ru_3_blt_web=`4.23`
- `w4`: Ru_4_blt_web_v3=`0.37`, Ru_4_blt_web_v2=`-3.88`, Ru_4_blt_web=`3.89`
- `w5`: Ru_5_blt_web_v3=`-0.95`, Ru_5_blt_web_v2=`-3.88`, Ru_5_blt_web=`3.99`
- `w6`: Ru_6_blt_web_v3=`-2.28`, Ru_6_blt_web_v2=`-3.88`, Ru_6_blt_web=`4.5`

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
- `x_icr_final_blt_web = -7.58 in`
- `y_icr_final_blt_web = 10.07 in`
- Coordenadas por iteracion (`estimacion -> resultado`):
- Iter `1`: estimacion=`(8.75, 9.84) in` -> resultado=`(-8.75, 9.84) in`
- Iter `2`: estimacion=`(-8.75, 9.84) in` -> resultado=`(-8.43, 10.2) in`
- Iter `3`: estimacion=`(-8.43, 10.2) in` -> resultado=`(-8.22, 10.21) in`
- Iter `4`: estimacion=`(-8.22, 10.21) in` -> resultado=`(-8.06, 10.18) in`
- Iter `5`: estimacion=`(-8.06, 10.18) in` -> resultado=`(-7.94, 10.15) in`
- Iter `6`: estimacion=`(-7.94, 10.15) in` -> resultado=`(-7.85, 10.13) in`
- Iter `7`: estimacion=`(-7.85, 10.13) in` -> resultado=`(-7.78, 10.12) in`
- Iter `8`: estimacion=`(-7.78, 10.12) in` -> resultado=`(-7.73, 10.1) in`
- Iter `9`: estimacion=`(-7.73, 10.1) in` -> resultado=`(-7.69, 10.1) in`
- Iter `10`: estimacion=`(-7.69, 10.1) in` -> resultado=`(-7.66, 10.09) in`
- Iter `11`: estimacion=`(-7.66, 10.09) in` -> resultado=`(-7.64, 10.08) in`
- Iter `12`: estimacion=`(-7.64, 10.08) in` -> resultado=`(-7.62, 10.08) in`
- Iter `13`: estimacion=`(-7.62, 10.08) in` -> resultado=`(-7.61, 10.08) in`
- Iter `14`: estimacion=`(-7.61, 10.08) in` -> resultado=`(-7.6, 10.08) in`
- Iter `15`: estimacion=`(-7.6, 10.08) in` -> resultado=`(-7.6, 10.08) in`
- Iter `16`: estimacion=`(-7.6, 10.08) in` -> resultado=`(-7.59, 10.07) in`
- Iter `17`: estimacion=`(-7.59, 10.07) in` -> resultado=`(-7.59, 10.07) in`
- Iter `18`: estimacion=`(-7.59, 10.07) in` -> resultado=`(-7.59, 10.07) in`
- Iter `19`: estimacion=`(-7.59, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iter `20`: estimacion=`(-7.58, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iter `21`: estimacion=`(-7.58, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iter `22`: estimacion=`(-7.58, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iter `23`: estimacion=`(-7.58, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iter `24`: estimacion=`(-7.58, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iter `25`: estimacion=`(-7.58, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iter `26`: estimacion=`(-7.58, 10.07) in` -> resultado=`(-7.58, 10.07) in`
- Iteraciones del ICR:

### 7.2 Iteraciones globales (residuales)

- Iter `1`: x_icr_blt_web=`-8.75`, y_icr_blt_web=`9.84`, res_Ru_blt_web_v3=`2.27`, res_Ru_blt_web_v2=`-2.06`, res_norm_blt_web=`3.06`
- Iter `2`: x_icr_blt_web=`-8.43`, y_icr_blt_web=`10.2`, res_Ru_blt_web_v3=`0.08`, res_Ru_blt_web_v2=`-1.35`, res_norm_blt_web=`1.35`
- Iter `3`: x_icr_blt_web=`-8.22`, y_icr_blt_web=`10.21`, res_Ru_blt_web_v3=`-0.18`, res_Ru_blt_web_v2=`-1.01`, res_norm_blt_web=`1.03`
- Iter `4`: x_icr_blt_web=`-8.06`, y_icr_blt_web=`10.18`, res_Ru_blt_web_v3=`-0.17`, res_Ru_blt_web_v2=`-0.78`, res_norm_blt_web=`0.8`
- Iter `5`: x_icr_blt_web=`-7.94`, y_icr_blt_web=`10.15`, res_Ru_blt_web_v3=`-0.14`, res_Ru_blt_web_v2=`-0.59`, res_norm_blt_web=`0.61`
- Iter `6`: x_icr_blt_web=`-7.85`, y_icr_blt_web=`10.13`, res_Ru_blt_web_v3=`-0.1`, res_Ru_blt_web_v2=`-0.45`, res_norm_blt_web=`0.46`
- Iter `7`: x_icr_blt_web=`-7.78`, y_icr_blt_web=`10.12`, res_Ru_blt_web_v3=`-0.08`, res_Ru_blt_web_v2=`-0.34`, res_norm_blt_web=`0.34`
- Iter `8`: x_icr_blt_web=`-7.73`, y_icr_blt_web=`10.1`, res_Ru_blt_web_v3=`-0.06`, res_Ru_blt_web_v2=`-0.25`, res_norm_blt_web=`0.26`
- Iter `9`: x_icr_blt_web=`-7.69`, y_icr_blt_web=`10.1`, res_Ru_blt_web_v3=`-0.04`, res_Ru_blt_web_v2=`-0.18`, res_norm_blt_web=`0.19`
- Iter `10`: x_icr_blt_web=`-7.66`, y_icr_blt_web=`10.09`, res_Ru_blt_web_v3=`-0.03`, res_Ru_blt_web_v2=`-0.14`, res_norm_blt_web=`0.14`
- Iter `11`: x_icr_blt_web=`-7.64`, y_icr_blt_web=`10.08`, res_Ru_blt_web_v3=`-0.02`, res_Ru_blt_web_v2=`-0.1`, res_norm_blt_web=`0.1`
- Iter `12`: x_icr_blt_web=`-7.62`, y_icr_blt_web=`10.08`, res_Ru_blt_web_v3=`-0.02`, res_Ru_blt_web_v2=`-0.07`, res_norm_blt_web=`0.07`
- Iter `13`: x_icr_blt_web=`-7.61`, y_icr_blt_web=`10.08`, res_Ru_blt_web_v3=`-0.01`, res_Ru_blt_web_v2=`-0.05`, res_norm_blt_web=`0.05`
- Iter `14`: x_icr_blt_web=`-7.6`, y_icr_blt_web=`10.08`, res_Ru_blt_web_v3=`-0.01`, res_Ru_blt_web_v2=`-0.04`, res_norm_blt_web=`0.04`
- Iter `15`: x_icr_blt_web=`-7.6`, y_icr_blt_web=`10.08`, res_Ru_blt_web_v3=`-0.01`, res_Ru_blt_web_v2=`-0.03`, res_norm_blt_web=`0.03`
- Iter `16`: x_icr_blt_web=`-7.59`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.02`, res_norm_blt_web=`0.02`
- Iter `17`: x_icr_blt_web=`-7.59`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.02`
- Iter `18`: x_icr_blt_web=`-7.59`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.01`
- Iter `19`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.01`
- Iter `20`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0.01`, res_norm_blt_web=`0.01`
- Iter `21`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `22`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `23`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `24`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `25`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`
- Iter `26`: x_icr_blt_web=`-7.58`, y_icr_blt_web=`10.07`, res_Ru_blt_web_v3=`-0`, res_Ru_blt_web_v2=`-0`, res_norm_blt_web=`0`

### 7.3 Parametros auxiliares por iteracion

- Iter `1`: dmax_icr_blt_web=`13.17`, sum(phi_i_blt_web*r_icr_i_blt_web)=`59.33`, Rult_blt_web=`-11.73`, Cu_blt_web=`4.95`, M_icr_blt_web=`-695.68`
- Iter `2`: dmax_icr_blt_web=`13.23`, sum(phi_i_blt_web*r_icr_i_blt_web)=`57.98`, Rult_blt_web=`-11.78`, Cu_blt_web=`4.94`, M_icr_blt_web=`-682.99`
- Iter `3`: dmax_icr_blt_web=`13.11`, sum(phi_i_blt_web*r_icr_i_blt_web)=`56.9`, Rult_blt_web=`-11.8`, Cu_blt_web=`4.93`, M_icr_blt_web=`-671.34`
- Iter `4`: dmax_icr_blt_web=`12.99`, sum(phi_i_blt_web*r_icr_i_blt_web)=`56.06`, Rult_blt_web=`-11.81`, Cu_blt_web=`4.93`, M_icr_blt_web=`-662.05`
- Iter `5`: dmax_icr_blt_web=`12.89`, sum(phi_i_blt_web*r_icr_i_blt_web)=`55.42`, Rult_blt_web=`-11.82`, Cu_blt_web=`4.92`, M_icr_blt_web=`-654.83`
- Iter `6`: dmax_icr_blt_web=`12.82`, sum(phi_i_blt_web*r_icr_i_blt_web)=`54.92`, Rult_blt_web=`-11.82`, Cu_blt_web=`4.92`, M_icr_blt_web=`-649.32`
- Iter `7`: dmax_icr_blt_web=`12.76`, sum(phi_i_blt_web*r_icr_i_blt_web)=`54.55`, Rult_blt_web=`-11.83`, Cu_blt_web=`4.92`, M_icr_blt_web=`-645.15`
- Iter `8`: dmax_icr_blt_web=`12.72`, sum(phi_i_blt_web*r_icr_i_blt_web)=`54.27`, Rult_blt_web=`-11.83`, Cu_blt_web=`4.92`, M_icr_blt_web=`-642.03`
- Iter `9`: dmax_icr_blt_web=`12.69`, sum(phi_i_blt_web*r_icr_i_blt_web)=`54.07`, Rult_blt_web=`-11.83`, Cu_blt_web=`4.92`, M_icr_blt_web=`-639.72`
- Iter `10`: dmax_icr_blt_web=`12.67`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.92`, Rult_blt_web=`-11.83`, Cu_blt_web=`4.92`, M_icr_blt_web=`-638.02`
- Iter `11`: dmax_icr_blt_web=`12.65`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.81`, Rult_blt_web=`-11.83`, Cu_blt_web=`4.92`, M_icr_blt_web=`-636.76`
- Iter `12`: dmax_icr_blt_web=`12.64`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.72`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-635.84`
- Iter `13`: dmax_icr_blt_web=`12.63`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.66`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-635.17`
- Iter `14`: dmax_icr_blt_web=`12.62`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.62`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-634.68`
- Iter `15`: dmax_icr_blt_web=`12.62`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.59`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-634.33`
- Iter `16`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.57`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-634.07`
- Iter `17`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.55`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.88`
- Iter `18`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.54`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.74`
- Iter `19`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.53`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.64`
- Iter `20`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.52`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.57`
- Iter `21`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.52`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.51`
- Iter `22`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.51`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.48`
- Iter `23`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.51`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.45`
- Iter `24`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.51`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.43`
- Iter `25`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.51`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.41`
- Iter `26`: dmax_icr_blt_web=`12.61`, sum(phi_i_blt_web*r_icr_i_blt_web)=`53.51`, Rult_blt_web=`-11.84`, Cu_blt_web=`4.91`, M_icr_blt_web=`-633.4`

### 7.4 Bolt Detail ICR por iteracion

#### 7.4.1 Iteracion 1

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`8.75`, dy_icr_1_blt_web=`-9.84`, r_icr_1_blt_web=`13.17`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`8.75`, dy_icr_2_blt_web=`-6.84`, r_icr_2_blt_web=`11.11`, delta_2_blt_web=`0.29`
- `w3`: dx_icr_3_blt_web=`8.75`, dy_icr_3_blt_web=`-3.84`, r_icr_3_blt_web=`9.56`, delta_3_blt_web=`0.25`
- `w4`: dx_icr_4_blt_web=`8.75`, dy_icr_4_blt_web=`-0.84`, r_icr_4_blt_web=`8.79`, delta_4_blt_web=`0.23`
- `w5`: dx_icr_5_blt_web=`8.75`, dy_icr_5_blt_web=`2.16`, r_icr_5_blt_web=`9.01`, delta_5_blt_web=`0.23`
- `w6`: dx_icr_6_blt_web=`8.75`, dy_icr_6_blt_web=`5.16`, r_icr_6_blt_web=`10.16`, delta_6_blt_web=`0.26`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.51`, Ru_1_blt_web_v3=`-8.6`, Ru_1_blt_web_v2=`-7.65`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.36`, Ru_2_blt_web_v3=`-7`, Ru_2_blt_web_v2=`-8.94`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.17`, Ru_3_blt_web_v3=`-4.49`, Ru_3_blt_web_v2=`-10.23`
- `w4`: phi_4_blt_web=`0.94`, Ru_4_blt_web=`-11.04`, Ru_4_blt_web_v3=`-1.06`, Ru_4_blt_web_v2=`-10.99`
- `w5`: phi_5_blt_web=`0.95`, Ru_5_blt_web=`-11.08`, Ru_5_blt_web_v3=`2.65`, Ru_5_blt_web_v2=`-10.76`
- `w6`: phi_6_blt_web=`0.96`, Ru_6_blt_web=`-11.25`, Ru_6_blt_web_v3=`5.71`, Ru_6_blt_web_v2=`-9.69`

#### 7.4.2 Iteracion 2

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`8.43`, dy_icr_1_blt_web=`-10.2`, r_icr_1_blt_web=`13.23`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`8.43`, dy_icr_2_blt_web=`-7.2`, r_icr_2_blt_web=`11.08`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`8.43`, dy_icr_3_blt_web=`-4.2`, r_icr_3_blt_web=`9.42`, delta_3_blt_web=`0.24`
- `w4`: dx_icr_4_blt_web=`8.43`, dy_icr_4_blt_web=`-1.2`, r_icr_4_blt_web=`8.51`, delta_4_blt_web=`0.22`
- `w5`: dx_icr_5_blt_web=`8.43`, dy_icr_5_blt_web=`1.8`, r_icr_5_blt_web=`8.62`, delta_5_blt_web=`0.22`
- `w6`: dx_icr_6_blt_web=`8.43`, dy_icr_6_blt_web=`4.8`, r_icr_6_blt_web=`9.7`, delta_6_blt_web=`0.25`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.56`, Ru_1_blt_web_v3=`-8.91`, Ru_1_blt_web_v2=`-7.37`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.4`, Ru_2_blt_web_v3=`-7.4`, Ru_2_blt_web_v2=`-8.67`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-4.99`, Ru_3_blt_web_v2=`-10.02`
- `w4`: phi_4_blt_web=`0.94`, Ru_4_blt_web=`-11.03`, Ru_4_blt_web_v3=`-1.55`, Ru_4_blt_web_v2=`-10.92`
- `w5`: phi_5_blt_web=`0.94`, Ru_5_blt_web=`-11.06`, Ru_5_blt_web_v3=`2.31`, Ru_5_blt_web_v2=`-10.81`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.23`, Ru_6_blt_web_v3=`5.56`, Ru_6_blt_web_v2=`-9.76`

#### 7.4.3 Iteracion 3

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`8.22`, dy_icr_1_blt_web=`-10.21`, r_icr_1_blt_web=`13.11`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`8.22`, dy_icr_2_blt_web=`-7.21`, r_icr_2_blt_web=`10.93`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`8.22`, dy_icr_3_blt_web=`-4.21`, r_icr_3_blt_web=`9.23`, delta_3_blt_web=`0.24`
- `w4`: dx_icr_4_blt_web=`8.22`, dy_icr_4_blt_web=`-1.21`, r_icr_4_blt_web=`8.31`, delta_4_blt_web=`0.22`
- `w5`: dx_icr_5_blt_web=`8.22`, dy_icr_5_blt_web=`1.79`, r_icr_5_blt_web=`8.41`, delta_5_blt_web=`0.22`
- `w6`: dx_icr_6_blt_web=`8.22`, dy_icr_6_blt_web=`4.79`, r_icr_6_blt_web=`9.51`, delta_6_blt_web=`0.25`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.58`, Ru_1_blt_web_v3=`-9.02`, Ru_1_blt_web_v2=`-7.26`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.41`, Ru_2_blt_web_v3=`-7.53`, Ru_2_blt_web_v2=`-8.58`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.1`, Ru_3_blt_web_v2=`-9.96`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-11.03`, Ru_4_blt_web_v3=`-1.61`, Ru_4_blt_web_v2=`-10.91`
- `w5`: phi_5_blt_web=`0.94`, Ru_5_blt_web=`-11.05`, Ru_5_blt_web_v3=`2.35`, Ru_5_blt_web_v2=`-10.79`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.24`, Ru_6_blt_web_v3=`5.66`, Ru_6_blt_web_v2=`-9.71`

#### 7.4.4 Iteracion 4

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`8.06`, dy_icr_1_blt_web=`-10.18`, r_icr_1_blt_web=`12.99`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`8.06`, dy_icr_2_blt_web=`-7.18`, r_icr_2_blt_web=`10.8`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`8.06`, dy_icr_3_blt_web=`-4.18`, r_icr_3_blt_web=`9.08`, delta_3_blt_web=`0.24`
- `w4`: dx_icr_4_blt_web=`8.06`, dy_icr_4_blt_web=`-1.18`, r_icr_4_blt_web=`8.15`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`8.06`, dy_icr_5_blt_web=`1.82`, r_icr_5_blt_web=`8.26`, delta_5_blt_web=`0.22`
- `w6`: dx_icr_6_blt_web=`8.06`, dy_icr_6_blt_web=`4.82`, r_icr_6_blt_web=`9.39`, delta_6_blt_web=`0.25`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.59`, Ru_1_blt_web_v3=`-9.09`, Ru_1_blt_web_v2=`-7.2`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.42`, Ru_2_blt_web_v3=`-7.6`, Ru_2_blt_web_v2=`-8.53`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.15`, Ru_3_blt_web_v2=`-9.94`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-11.02`, Ru_4_blt_web_v3=`-1.6`, Ru_4_blt_web_v2=`-10.9`
- `w5`: phi_5_blt_web=`0.94`, Ru_5_blt_web=`-11.04`, Ru_5_blt_web_v3=`2.43`, Ru_5_blt_web_v2=`-10.77`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.24`, Ru_6_blt_web_v3=`5.77`, Ru_6_blt_web_v2=`-9.65`

#### 7.4.5 Iteracion 5

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.94`, dy_icr_1_blt_web=`-10.15`, r_icr_1_blt_web=`12.89`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.94`, dy_icr_2_blt_web=`-7.15`, r_icr_2_blt_web=`10.69`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.94`, dy_icr_3_blt_web=`-4.15`, r_icr_3_blt_web=`8.96`, delta_3_blt_web=`0.24`
- `w4`: dx_icr_4_blt_web=`7.94`, dy_icr_4_blt_web=`-1.15`, r_icr_4_blt_web=`8.02`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.94`, dy_icr_5_blt_web=`1.85`, r_icr_5_blt_web=`8.15`, delta_5_blt_web=`0.22`
- `w6`: dx_icr_6_blt_web=`7.94`, dy_icr_6_blt_web=`4.85`, r_icr_6_blt_web=`9.3`, delta_6_blt_web=`0.25`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.6`, Ru_1_blt_web_v3=`-9.14`, Ru_1_blt_web_v2=`-7.14`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.42`, Ru_2_blt_web_v3=`-7.65`, Ru_2_blt_web_v2=`-8.49`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.19`, Ru_3_blt_web_v2=`-9.92`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-11.01`, Ru_4_blt_web_v3=`-1.58`, Ru_4_blt_web_v2=`-10.9`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.04`, Ru_5_blt_web_v3=`2.5`, Ru_5_blt_web_v2=`-10.75`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.25`, Ru_6_blt_web_v3=`5.86`, Ru_6_blt_web_v2=`-9.6`

#### 7.4.6 Iteracion 6

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.85`, dy_icr_1_blt_web=`-10.13`, r_icr_1_blt_web=`12.82`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.85`, dy_icr_2_blt_web=`-7.13`, r_icr_2_blt_web=`10.6`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.85`, dy_icr_3_blt_web=`-4.13`, r_icr_3_blt_web=`8.87`, delta_3_blt_web=`0.24`
- `w4`: dx_icr_4_blt_web=`7.85`, dy_icr_4_blt_web=`-1.13`, r_icr_4_blt_web=`7.93`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.85`, dy_icr_5_blt_web=`1.87`, r_icr_5_blt_web=`8.07`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.85`, dy_icr_6_blt_web=`4.87`, r_icr_6_blt_web=`9.23`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.6`, Ru_1_blt_web_v3=`-9.17`, Ru_1_blt_web_v2=`-7.11`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.69`, Ru_2_blt_web_v2=`-8.46`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.21`, Ru_3_blt_web_v2=`-9.9`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-11.01`, Ru_4_blt_web_v3=`-1.57`, Ru_4_blt_web_v2=`-10.89`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.04`, Ru_5_blt_web_v3=`2.55`, Ru_5_blt_web_v2=`-10.74`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.25`, Ru_6_blt_web_v3=`5.93`, Ru_6_blt_web_v2=`-9.56`

#### 7.4.7 Iteracion 7

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.78`, dy_icr_1_blt_web=`-10.12`, r_icr_1_blt_web=`12.76`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.78`, dy_icr_2_blt_web=`-7.12`, r_icr_2_blt_web=`10.54`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.78`, dy_icr_3_blt_web=`-4.12`, r_icr_3_blt_web=`8.8`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.78`, dy_icr_4_blt_web=`-1.12`, r_icr_4_blt_web=`7.86`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.78`, dy_icr_5_blt_web=`1.88`, r_icr_5_blt_web=`8`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.78`, dy_icr_6_blt_web=`4.88`, r_icr_6_blt_web=`9.18`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.61`, Ru_1_blt_web_v3=`-9.2`, Ru_1_blt_web_v2=`-7.07`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.72`, Ru_2_blt_web_v2=`-8.43`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.23`, Ru_3_blt_web_v2=`-9.89`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-11`, Ru_4_blt_web_v3=`-1.56`, Ru_4_blt_web_v2=`-10.89`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.6`, Ru_5_blt_web_v2=`-10.72`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.25`, Ru_6_blt_web_v3=`5.98`, Ru_6_blt_web_v2=`-9.53`

#### 7.4.8 Iteracion 8

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.73`, dy_icr_1_blt_web=`-10.1`, r_icr_1_blt_web=`12.72`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.73`, dy_icr_2_blt_web=`-7.1`, r_icr_2_blt_web=`10.5`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.73`, dy_icr_3_blt_web=`-4.1`, r_icr_3_blt_web=`8.75`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.73`, dy_icr_4_blt_web=`-1.1`, r_icr_4_blt_web=`7.8`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.73`, dy_icr_5_blt_web=`1.9`, r_icr_5_blt_web=`7.95`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.73`, dy_icr_6_blt_web=`4.9`, r_icr_6_blt_web=`9.15`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.61`, Ru_1_blt_web_v3=`-9.22`, Ru_1_blt_web_v2=`-7.05`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.74`, Ru_2_blt_web_v2=`-8.41`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.25`, Ru_3_blt_web_v2=`-9.88`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-11`, Ru_4_blt_web_v3=`-1.56`, Ru_4_blt_web_v2=`-10.89`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.63`, Ru_5_blt_web_v2=`-10.71`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.25`, Ru_6_blt_web_v3=`6.02`, Ru_6_blt_web_v2=`-9.51`

#### 7.4.9 Iteracion 9

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.69`, dy_icr_1_blt_web=`-10.1`, r_icr_1_blt_web=`12.69`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.69`, dy_icr_2_blt_web=`-7.1`, r_icr_2_blt_web=`10.46`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.69`, dy_icr_3_blt_web=`-4.1`, r_icr_3_blt_web=`8.71`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.69`, dy_icr_4_blt_web=`-1.1`, r_icr_4_blt_web=`7.76`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.69`, dy_icr_5_blt_web=`1.9`, r_icr_5_blt_web=`7.92`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.69`, dy_icr_6_blt_web=`4.9`, r_icr_6_blt_web=`9.12`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.61`, Ru_1_blt_web_v3=`-9.24`, Ru_1_blt_web_v2=`-7.03`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.75`, Ru_2_blt_web_v2=`-8.4`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.26`, Ru_3_blt_web_v2=`-9.87`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.55`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.65`, Ru_5_blt_web_v2=`-10.71`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.25`, Ru_6_blt_web_v3=`6.05`, Ru_6_blt_web_v2=`-9.49`

#### 7.4.10 Iteracion 10

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.66`, dy_icr_1_blt_web=`-10.09`, r_icr_1_blt_web=`12.67`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.66`, dy_icr_2_blt_web=`-7.09`, r_icr_2_blt_web=`10.44`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.66`, dy_icr_3_blt_web=`-4.09`, r_icr_3_blt_web=`8.68`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.66`, dy_icr_4_blt_web=`-1.09`, r_icr_4_blt_web=`7.74`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.66`, dy_icr_5_blt_web=`1.91`, r_icr_5_blt_web=`7.89`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.66`, dy_icr_6_blt_web=`4.91`, r_icr_6_blt_web=`9.1`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.61`, Ru_1_blt_web_v3=`-9.25`, Ru_1_blt_web_v2=`-7.02`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.77`, Ru_2_blt_web_v2=`-8.39`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.27`, Ru_3_blt_web_v2=`-9.87`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.55`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.67`, Ru_5_blt_web_v2=`-10.7`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.08`, Ru_6_blt_web_v2=`-9.48`

#### 7.4.11 Iteracion 11

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.64`, dy_icr_1_blt_web=`-10.08`, r_icr_1_blt_web=`12.65`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.64`, dy_icr_2_blt_web=`-7.08`, r_icr_2_blt_web=`10.42`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.64`, dy_icr_3_blt_web=`-4.08`, r_icr_3_blt_web=`8.66`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.64`, dy_icr_4_blt_web=`-1.08`, r_icr_4_blt_web=`7.71`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.64`, dy_icr_5_blt_web=`1.92`, r_icr_5_blt_web=`7.87`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.64`, dy_icr_6_blt_web=`4.92`, r_icr_6_blt_web=`9.08`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.26`, Ru_1_blt_web_v2=`-7.01`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.78`, Ru_2_blt_web_v2=`-8.38`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.19`, Ru_3_blt_web_v3=`-5.28`, Ru_3_blt_web_v2=`-9.86`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.55`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.68`, Ru_5_blt_web_v2=`-10.7`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.09`, Ru_6_blt_web_v2=`-9.47`

#### 7.4.12 Iteracion 12

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.62`, dy_icr_1_blt_web=`-10.08`, r_icr_1_blt_web=`12.64`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.62`, dy_icr_2_blt_web=`-7.08`, r_icr_2_blt_web=`10.4`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.62`, dy_icr_3_blt_web=`-4.08`, r_icr_3_blt_web=`8.65`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.62`, dy_icr_4_blt_web=`-1.08`, r_icr_4_blt_web=`7.7`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.62`, dy_icr_5_blt_web=`1.92`, r_icr_5_blt_web=`7.86`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.62`, dy_icr_6_blt_web=`4.92`, r_icr_6_blt_web=`9.07`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.27`, Ru_1_blt_web_v2=`-7.01`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.78`, Ru_2_blt_web_v2=`-8.38`
- `w3`: phi_3_blt_web=`0.95`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.28`, Ru_3_blt_web_v2=`-9.86`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.69`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.1`, Ru_6_blt_web_v2=`-9.46`

#### 7.4.13 Iteracion 13

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.61`, dy_icr_1_blt_web=`-10.08`, r_icr_1_blt_web=`12.63`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.61`, dy_icr_2_blt_web=`-7.08`, r_icr_2_blt_web=`10.39`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.61`, dy_icr_3_blt_web=`-4.08`, r_icr_3_blt_web=`8.63`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.61`, dy_icr_4_blt_web=`-1.08`, r_icr_4_blt_web=`7.69`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.61`, dy_icr_5_blt_web=`1.92`, r_icr_5_blt_web=`7.85`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.61`, dy_icr_6_blt_web=`4.92`, r_icr_6_blt_web=`9.06`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.27`, Ru_1_blt_web_v2=`-7`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.79`, Ru_2_blt_web_v2=`-8.37`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.28`, Ru_3_blt_web_v2=`-9.86`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.7`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.11`, Ru_6_blt_web_v2=`-9.45`

#### 7.4.14 Iteracion 14

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.6`, dy_icr_1_blt_web=`-10.08`, r_icr_1_blt_web=`12.62`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.6`, dy_icr_2_blt_web=`-7.08`, r_icr_2_blt_web=`10.39`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.6`, dy_icr_3_blt_web=`-4.08`, r_icr_3_blt_web=`8.63`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.6`, dy_icr_4_blt_web=`-1.08`, r_icr_4_blt_web=`7.68`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.6`, dy_icr_5_blt_web=`1.92`, r_icr_5_blt_web=`7.84`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.6`, dy_icr_6_blt_web=`4.92`, r_icr_6_blt_web=`9.06`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.27`, Ru_1_blt_web_v2=`-7`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.79`, Ru_2_blt_web_v2=`-8.37`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.86`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.7`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.12`, Ru_6_blt_web_v2=`-9.45`

#### 7.4.15 Iteracion 15

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.6`, dy_icr_1_blt_web=`-10.08`, r_icr_1_blt_web=`12.62`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.6`, dy_icr_2_blt_web=`-7.08`, r_icr_2_blt_web=`10.38`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.6`, dy_icr_3_blt_web=`-4.08`, r_icr_3_blt_web=`8.62`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.6`, dy_icr_4_blt_web=`-1.08`, r_icr_4_blt_web=`7.67`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.6`, dy_icr_5_blt_web=`1.92`, r_icr_5_blt_web=`7.84`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.6`, dy_icr_6_blt_web=`4.92`, r_icr_6_blt_web=`9.05`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.79`, Ru_2_blt_web_v2=`-8.37`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.86`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.71`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.12`, Ru_6_blt_web_v2=`-9.45`

#### 7.4.16 Iteracion 16

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.59`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.59`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.38`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.59`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.62`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.59`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.67`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.59`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.83`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.59`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.05`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.37`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.71`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.13`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.17 Iteracion 17

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.59`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.59`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.59`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.59`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.59`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.83`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.59`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.05`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.71`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.13`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.18 Iteracion 18

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.59`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.59`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.59`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.59`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.59`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.83`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.59`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.05`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.71`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.13`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.19 Iteracion 19

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.83`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.13`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.20 Iteracion 20

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.82`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.13`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.21 Iteracion 21

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.82`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.13`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.22 Iteracion 22

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.82`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.13`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.23 Iteracion 23

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.82`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.14`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.24 Iteracion 24

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.82`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.14`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.25 Iteracion 25

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.82`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.14`, Ru_6_blt_web_v2=`-9.44`

#### 7.4.26 Iteracion 26

- Cinematica por perno:
- `w1`: dx_icr_1_blt_web=`7.58`, dy_icr_1_blt_web=`-10.07`, r_icr_1_blt_web=`12.61`, delta_1_blt_web=`0.34`
- `w2`: dx_icr_2_blt_web=`7.58`, dy_icr_2_blt_web=`-7.07`, r_icr_2_blt_web=`10.37`, delta_2_blt_web=`0.28`
- `w3`: dx_icr_3_blt_web=`7.58`, dy_icr_3_blt_web=`-4.07`, r_icr_3_blt_web=`8.61`, delta_3_blt_web=`0.23`
- `w4`: dx_icr_4_blt_web=`7.58`, dy_icr_4_blt_web=`-1.07`, r_icr_4_blt_web=`7.66`, delta_4_blt_web=`0.21`
- `w5`: dx_icr_5_blt_web=`7.58`, dy_icr_5_blt_web=`1.93`, r_icr_5_blt_web=`7.82`, delta_5_blt_web=`0.21`
- `w6`: dx_icr_6_blt_web=`7.58`, dy_icr_6_blt_web=`4.93`, r_icr_6_blt_web=`9.04`, delta_6_blt_web=`0.24`
- Fuerzas por perno:
- `w1`: phi_1_blt_web=`0.98`, Ru_1_blt_web=`-11.62`, Ru_1_blt_web_v3=`-9.28`, Ru_1_blt_web_v2=`-6.99`
- `w2`: phi_2_blt_web=`0.97`, Ru_2_blt_web=`-11.43`, Ru_2_blt_web_v3=`-7.8`, Ru_2_blt_web_v2=`-8.36`
- `w3`: phi_3_blt_web=`0.94`, Ru_3_blt_web=`-11.18`, Ru_3_blt_web_v3=`-5.29`, Ru_3_blt_web_v2=`-9.85`
- `w4`: phi_4_blt_web=`0.93`, Ru_4_blt_web=`-10.99`, Ru_4_blt_web_v3=`-1.54`, Ru_4_blt_web_v2=`-10.88`
- `w5`: phi_5_blt_web=`0.93`, Ru_5_blt_web=`-11.03`, Ru_5_blt_web_v3=`2.72`, Ru_5_blt_web_v2=`-10.69`
- `w6`: phi_6_blt_web=`0.95`, Ru_6_blt_web=`-11.26`, Ru_6_blt_web_v3=`6.14`, Ru_6_blt_web_v2=`-9.44`
