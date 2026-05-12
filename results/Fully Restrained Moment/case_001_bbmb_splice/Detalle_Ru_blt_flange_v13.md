# Reporte Metodos Pernos 2 (Flange)

## 1. Informacion General

- Proyecto: `proj_bbmb_demo`
- Caso: `case_001_bbmb_splice_si`
- Metodo seleccionado en JSON: `elastic_superposition`
- Metodo efectivo: `elastic_superposition`

### 1.1 Variables de carga

- Ecuacion base: `Muz_blt_web = Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- Pu_sp: `851.43 kN` (origen: `loads.Pu_sp`)
- Vu2_sp: `0 kN` (origen: `loads.Vu2_sp`)
- ex_blt_web: `320 mm` (origen: `formula splice`)
- ey_blt_web: `0 mm` (origen: `input ey`)
- Muz_blt_web: `0 kN-mm`

## 2. Geometria de pernos derivada

- Ru_blt_web_v23: `191.41 kip` con `sqrt(Pu_sp^2 + Vu2_sp^2)`
- theta_blt_web: `0 deg` con `atan2(Vu2_sp, Pu_sp)`
- e_blt_web: `12.6 in` con `sqrt(ex_blt_web^2 + ey_blt_web^2)`
- n_blt_web: `8 -` con `conteo pernos activos`
- x_cg_blt_web: `4.13 in` con `sum(x_i_blt_web)/n_blt_web`
- y_cg_blt_web: `0 in` con `sum(y_i_blt_web)/n_blt_web`
- Ix_blt_web: `43.9 in2` con `sum((y_i_blt_web-y_cg_blt_web)^2)`
- Iy_blt_web: `75.95 in2` con `sum((x_i_blt_web-x_cg_blt_web)^2)`
- J_blt_web: `119.85 in2` con `Ix_blt_web + Iy_blt_web`
- Muz_blt_web: `0 kip-in` con `Vu2_sp*ex_blt_web - alpha_Pu_web*Pu_sp*ey_blt_web`
- dmax_blt_web: `4.75 in` con `max(sqrt((x_i_blt_web-x_cg_blt_web)^2+(y_i_blt_web-y_cg_blt_web)^2))`

## 3. Geometria del grupo de pernos

- Perno `f1`: x_1_blt_web=`0 in`, y_1_blt_web=`-2.34 in`, dx_cg_1_blt_web=`-4.13 in`, dy_cg_1_blt_web=`-2.34 in`, r_cg_1_blt_web=`4.75 in`
- Perno `f2`: x_2_blt_web=`0 in`, y_2_blt_web=`2.34 in`, dx_cg_2_blt_web=`-4.13 in`, dy_cg_2_blt_web=`2.34 in`, r_cg_2_blt_web=`4.75 in`
- Perno `f3`: x_3_blt_web=`2.76 in`, y_3_blt_web=`-2.34 in`, dx_cg_3_blt_web=`-1.38 in`, dy_cg_3_blt_web=`-2.34 in`, r_cg_3_blt_web=`2.72 in`
- Perno `f4`: x_4_blt_web=`2.76 in`, y_4_blt_web=`2.34 in`, dx_cg_4_blt_web=`-1.38 in`, dy_cg_4_blt_web=`2.34 in`, r_cg_4_blt_web=`2.72 in`
- Perno `f5`: x_5_blt_web=`5.51 in`, y_5_blt_web=`-2.34 in`, dx_cg_5_blt_web=`1.38 in`, dy_cg_5_blt_web=`-2.34 in`, r_cg_5_blt_web=`2.72 in`
- Perno `f6`: x_6_blt_web=`5.51 in`, y_6_blt_web=`2.34 in`, dx_cg_6_blt_web=`1.38 in`, dy_cg_6_blt_web=`2.34 in`, r_cg_6_blt_web=`2.72 in`
- Perno `f7`: x_7_blt_web=`8.27 in`, y_7_blt_web=`-2.34 in`, dx_cg_7_blt_web=`4.13 in`, dy_cg_7_blt_web=`-2.34 in`, r_cg_7_blt_web=`4.75 in`
- Perno `f8`: x_8_blt_web=`8.27 in`, y_8_blt_web=`2.34 in`, dx_cg_8_blt_web=`4.13 in`, dy_cg_8_blt_web=`2.34 in`, r_cg_8_blt_web=`4.75 in`

## 4. Resumen global por metodo

- Metodo `elastic_superposition`: applicable=`True`, estado=`PASS`, demanda=`23.93 kip`, capacidad=`29.04 kip`, DCR=`0.82`
- Metodo `elastic_ecr`: applicable=`False`, estado=`PASS`, demanda=`n/a kip`, capacidad=`n/a kip`, DCR=`n/a`
- Metodo `icr`: applicable=`False`, estado=`PASS`, demanda=`n/a kip`, capacidad=`n/a kip`, DCR=`n/a`

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

- `f1`: x_1_blt_web=`0`, y_1_blt_web=`-2.34`, dx_cg_1_blt_web=`-4.13`, dy_cg_1_blt_web=`-2.34`, r_cg_1_blt_web=`4.75`
- `f2`: x_2_blt_web=`0`, y_2_blt_web=`2.34`, dx_cg_2_blt_web=`-4.13`, dy_cg_2_blt_web=`2.34`, r_cg_2_blt_web=`4.75`
- `f3`: x_3_blt_web=`2.76`, y_3_blt_web=`-2.34`, dx_cg_3_blt_web=`-1.38`, dy_cg_3_blt_web=`-2.34`, r_cg_3_blt_web=`2.72`
- `f4`: x_4_blt_web=`2.76`, y_4_blt_web=`2.34`, dx_cg_4_blt_web=`-1.38`, dy_cg_4_blt_web=`2.34`, r_cg_4_blt_web=`2.72`
- `f5`: x_5_blt_web=`5.51`, y_5_blt_web=`-2.34`, dx_cg_5_blt_web=`1.38`, dy_cg_5_blt_web=`-2.34`, r_cg_5_blt_web=`2.72`
- `f6`: x_6_blt_web=`5.51`, y_6_blt_web=`2.34`, dx_cg_6_blt_web=`1.38`, dy_cg_6_blt_web=`2.34`, r_cg_6_blt_web=`2.72`
- `f7`: x_7_blt_web=`8.27`, y_7_blt_web=`-2.34`, dx_cg_7_blt_web=`4.13`, dy_cg_7_blt_web=`-2.34`, r_cg_7_blt_web=`4.75`
- `f8`: x_8_blt_web=`8.27`, y_8_blt_web=`2.34`, dx_cg_8_blt_web=`4.13`, dy_cg_8_blt_web=`2.34`, r_cg_8_blt_web=`4.75`

### 5.3 Fuerzas por perno

- `f1`: Ru_dir_1_blt_web_v3=`-23.93`, Ru_dir_1_blt_web_v2=`-0`, Ru_rot_1_blt_web_v3=`-0`, Ru_rot_1_blt_web_v2=`0`, Ru_1_blt_web=`23.93`
- `f2`: Ru_dir_2_blt_web_v3=`-23.93`, Ru_dir_2_blt_web_v2=`-0`, Ru_rot_2_blt_web_v3=`0`, Ru_rot_2_blt_web_v2=`0`, Ru_2_blt_web=`23.93`
- `f3`: Ru_dir_3_blt_web_v3=`-23.93`, Ru_dir_3_blt_web_v2=`-0`, Ru_rot_3_blt_web_v3=`-0`, Ru_rot_3_blt_web_v2=`0`, Ru_3_blt_web=`23.93`
- `f4`: Ru_dir_4_blt_web_v3=`-23.93`, Ru_dir_4_blt_web_v2=`-0`, Ru_rot_4_blt_web_v3=`0`, Ru_rot_4_blt_web_v2=`0`, Ru_4_blt_web=`23.93`
- `f5`: Ru_dir_5_blt_web_v3=`-23.93`, Ru_dir_5_blt_web_v2=`-0`, Ru_rot_5_blt_web_v3=`-0`, Ru_rot_5_blt_web_v2=`-0`, Ru_5_blt_web=`23.93`
- `f6`: Ru_dir_6_blt_web_v3=`-23.93`, Ru_dir_6_blt_web_v2=`-0`, Ru_rot_6_blt_web_v3=`0`, Ru_rot_6_blt_web_v2=`-0`, Ru_6_blt_web=`23.93`
- `f7`: Ru_dir_7_blt_web_v3=`-23.93`, Ru_dir_7_blt_web_v2=`-0`, Ru_rot_7_blt_web_v3=`-0`, Ru_rot_7_blt_web_v2=`-0`, Ru_7_blt_web=`23.93`
- `f8`: Ru_dir_8_blt_web_v3=`-23.93`, Ru_dir_8_blt_web_v2=`-0`, Ru_rot_8_blt_web_v3=`0`, Ru_rot_8_blt_web_v2=`-0`, Ru_8_blt_web=`23.93`

### 5.4 Resumen de fuerzas en pernos

- `f1`: Ru_1_blt_web_v3=`-23.93`, Ru_1_blt_web_v2=`0`, Ru_1_blt_web=`23.93`
- `f2`: Ru_2_blt_web_v3=`-23.93`, Ru_2_blt_web_v2=`0`, Ru_2_blt_web=`23.93`
- `f3`: Ru_3_blt_web_v3=`-23.93`, Ru_3_blt_web_v2=`0`, Ru_3_blt_web=`23.93`
- `f4`: Ru_4_blt_web_v3=`-23.93`, Ru_4_blt_web_v2=`0`, Ru_4_blt_web=`23.93`
- `f5`: Ru_5_blt_web_v3=`-23.93`, Ru_5_blt_web_v2=`-0`, Ru_5_blt_web=`23.93`
- `f6`: Ru_6_blt_web_v3=`-23.93`, Ru_6_blt_web_v2=`-0`, Ru_6_blt_web=`23.93`
- `f7`: Ru_7_blt_web_v3=`-23.93`, Ru_7_blt_web_v2=`-0`, Ru_7_blt_web=`23.93`
- `f8`: Ru_8_blt_web_v3=`-23.93`, Ru_8_blt_web_v2=`-0`, Ru_8_blt_web=`23.93`

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
- Pu_sp (componente aplicada en direccion v3): `191.41 kip`
- Vu2_sp (componente aplicada en direccion v2): `0 kip`
- n_blt_web: `8`
- J_blt_web: `119.85 in2`
- Muz_blt_web: `0 kip-in`
- ax_blt_web: `n/a in`
- ay_blt_web: `n/a in`
- x_ecr_blt_web: `n/a in`
- y_ecr_blt_web: `n/a in`

### 6.3 Geometria por perno respecto al ECR

- Sin datos de geometria para ECR.

### 6.4 Fuerzas por perno en ECR

- Sin datos de fuerzas para ECR.

### 6.5 Resumen de fuerzas en pernos

- Sin resumen de fuerzas resultantes para ECR.

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
- `x_icr_final_blt_web = 4.13 in`
- `y_icr_final_blt_web = 0 in`
- Coordenadas por iteracion (`estimacion -> resultado`):
- Sin coordenadas iterativas ICR reportadas.
- Iteraciones del ICR:

### 7.2 Iteraciones globales (residuales)

- Sin iteraciones ICR.

### 7.3 Parametros auxiliares por iteracion

- Sin parametros auxiliares ICR.

### 7.4 Bolt Detail ICR por iteracion

- Sin datos de detalle por iteracion en ICR.
