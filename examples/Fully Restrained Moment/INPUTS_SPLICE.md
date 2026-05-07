# Inputs Splice (`bbmb_splice`)

Fuente oficial de nomenclatura: [`/VARIABLES_SPLICE_NAMING.txt`](/D:/Users/byomayusa/Documents/GitHub/StructureLab_HFS_CNT/VARIABLES_SPLICE_NAMING.txt)

## Estructura JSON
- `sections`: propiedades de seccion.
- `materials`: materiales y pernos.
- `geometry`: geometria de viga/platinas/patrones de pernos.
- `loads`: acciones de diseno del splice.
- `design_factors`: factores `phi`.
- `procedure.icr`: selector de metodo (`elastic_superposition`, `elastic_ecr`, `icr`).

## Variables implementadas

### `sections`
- `shape_vg`

### `materials`
- `steel_vg`
- `steel_plt_web` (opcional)
- `steel_plt_flange` (opcional)
- `Fy_vg` (opcional)
- `Fu_vg` (opcional)
- `E_vg` (opcional)
- `shape_blt_web`
- `std_blt_web`
- `desc_blt_web`
- `thread_blt_web` (`N` o `X`)
- `shape_blt_flange`
- `std_blt_flange`
- `desc_blt_flange`
- `thread_blt_flange` (`N` o `X`)

### `geometry`
- `gap_sp`
- `tol_L_vg`
- `cond_sup_vg`
- `cond_amb_vg`
- `t_plt_web`
- `type_hole_plt_web`
- `cond_sup_plt_web`
- `cond_amb_plt_web`
- `t_plt_flange`
- `type_hole_plt_flange`
- `cond_sup_plt_flange`
- `cond_amb_plt_flange`
- `n_blt_web_x`
- `n_blt_web_y`
- `g_blt_web`
- `p_blt_web`
- `Le_blt_web_x1`
- `Le_blt_web_x2`
- `Le_blt_web_y1`
- `Le_blt_web_y2`
- `type_tight_blt_web` (`snug_tight`, `pretensioned`, `slip_critical`)
- `svc_hole_deformation_design_web` (bool; alias de entrada: `deformation_at_bolt_hole_service_load_is_design`)
- `n_blt_flange_x`
- `n_blt_flange_z` (`>= 1`)
- `p_blt_flange`
- `g_blt_flange`
- `Le_blt_flange_x1`
- `Le_blt_flange_x2`
- `Le_blt_flange_z1`
- `Le_blt_flange_z2`
- `Le_blt_flange_z3`
- `type_tight_blt_flange` (`snug_tight`, `pretensioned`, `slip_critical`)
- `svc_hole_deformation_design_flange` (bool; alias de entrada: `deformation_at_bolt_hole_service_load_is_design`)

Variables derivadas (no input):
- `Le_blt_web_y3 = 0.5*(d_vg - (n_blt_web_y-1)*p_blt_web)`

### `loads`
- `Pu_sp`
- `Vu2_sp`
- `Vu3_sp`
- `Mu3_sp`
- `Mu2_sp`
- `Tu_sp`
- `alpha_Pu_web` (default `0.0`)
- `ey_blt_web` (opcional, default interno `0`)

### `design_factors`
- `phi_bt`
- `phi_bv`
- `phi_py`
- `phi_pr`
- `phi_bs`
- `phi_sc` (opcional)

### `procedure.icr`
- `method`
- `tolerance_1`
- `max_iterations_1`
- `rult_1_kip` (requerido solo con `method=icr`)

## Excentricidad usada por el metodo de pernos 1
- `ex = gap_sp + 2*Le_blt_web_x1 + (n_blt_web_x-1)*g_blt_web`
- `ey = ey_blt_web` (o `0` si no se entrega)
- `Mz = Vy*ex - Vx*ey`
