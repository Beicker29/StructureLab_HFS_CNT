# Memoria moment prequalified

## Resumen

- Proyecto: `proj_bueep_si_demo`
- Caso: `case_si_bueep_4e_w18x175_w24x76`
- Familia: `moment_prequalified`
- Tipo: `bueep_4e`
- Estado de carga: `strength`
- Estado global: `ERROR`
- Checks OK: `18`
- Checks NG: `10`
- Checks NA: `0`
- Checks ERROR: `2`
- Advertencias: `0`
- Peor DCR: `1.537947`

## Checks criticos

- `AISC358.06.7.bueep_4e.step7_1_1_end_plate_flexural_yielding_vgizq` | Estado: `NG` | DCR: `1.537947`
- `AISC358.06.7.bueep_4e.step7_1_1_end_plate_flexural_yielding_vgder` | Estado: `NG` | DCR: `1.537947`
- `AISC358.06.7.bueep_4e.step6_1_bolt_tension_rupture_vgizq` | Estado: `NG` | DCR: `1.494948`
- `AISC358.06.7.bueep_4e.step6_1_bolt_tension_rupture_vgder` | Estado: `NG` | DCR: `1.494948`
- `AISC358.06.7.bueep_4e.step21_5_1_column_panel_zone_shear_wpzs_col` | Estado: `NG` | DCR: `1.311227`
- `AISC358.06.7.bueep_4e.step7_2_2_end_plate_shear_rupture_vgizq` | Estado: `NG` | DCR: `1.170585`
- `AISC358.06.7.bueep_4e.step7_2_2_end_plate_shear_rupture_vgder` | Estado: `NG` | DCR: `1.170585`
- `AISC358.06.7.bueep_4e.step7_2_1_end_plate_shear_yielding_vgizq` | Estado: `NG` | DCR: `1.011885`
- `AISC358.06.7.bueep_4e.step7_2_1_end_plate_shear_yielding_vgder` | Estado: `NG` | DCR: `1.011885`
- `AISC358.06.7.bueep_4e.step2_probable_moment_plastic_hinge` | Estado: `OK` | DCR: `1`

## Check 1 - bueep_4e Section 6.3 prequalification limits

- Regla: `AISC358.06.3.bueep_4e.prequalification_limits`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.3 + AISC 360-22 Table J3.4`
- Estado: `NG`
- Demanda: `n/a`
- Capacidad: `n/a`
- Capacidad final: `n/a`
- DCR: `n/a`
- Ecuacion: `Step 1 PREQUALIFICATION LIMITS: compute each geometric value and compare directly against Table 6.1 limits using calculated vs limit checks (>= or <=, no DCR format).`

### Inputs

```json
{
  "Encr_w8_col": null,
  "Encr_w8_col_fuente": null,
  "Fexx_w5_col": {
    "unit": "MPa",
    "value": 490.0
  },
  "Fexx_w6_col": {
    "unit": "MPa",
    "value": 490.0
  },
  "Fexx_w7_col": {
    "unit": "MPa",
    "value": 490.0
  },
  "Fexx_w8_col": {
    "unit": "MPa",
    "value": 490.0
  },
  "L2_pc_col": {
    "unit": "mm",
    "value": 328.0
  },
  "L_gap_w1_vgder": null,
  "L_gap_w1_vgizq": null,
  "L_gap_w2_vgder": null,
  "L_gap_w2_vgizq": null,
  "L_gap_w5_col": {
    "unit": "mm",
    "value": 0.0
  },
  "L_gap_w6_col": {
    "unit": "mm",
    "value": 0.0
  },
  "L_gap_w8_col": null,
  "L_gap_w9_col": null,
  "L_w5_col": null,
  "L_w8_col": null,
  "L_w9_col": {
    "unit": "mm",
    "value": 0.0
  },
  "ag_columna": {
    "unit": "mm2",
    "value": 33200.0
  },
  "ag_viga": {
    "unit": "mm2",
    "value": 14500.0
  },
  "b1_pc_col": null,
  "b2_pc_col": null,
  "b_dp_col": {
    "unit": "mm",
    "value": 407.0
  },
  "b_dp_col_formula": "d_col - 2*kdet_col",
  "beam_clear_span_length": {
    "unit": "mm",
    "value": 6096.0
  },
  "beam_clear_span_length_der": {
    "unit": "mm",
    "value": 6096.0
  },
  "beam_clear_span_length_izq": {
    "unit": "mm",
    "value": 6096.0
  },
  "beam_connection_sides": "both_sides",
  "beam_ductility_demand": "high",
  "beam_flange_width_bf": {
    "unit": "mm",
    "value": 228.0
  },
  "beam_s_threshold_vgder": {
    "unit": "mm",
    "value": 105.11422358558332
  },
  "beam_s_threshold_vgizq": {
    "unit": "mm",
    "value": 105.11422358558332
  },
  "beam_sc_vgder": {
    "unit": "mm",
    "value": 712.0
  },
  "beam_sc_vgizq": {
    "unit": "mm",
    "value": 712.0
  },
  "beam_shear_connector_free_length_from_column_face": {
    "unit": "mm",
    "value": 1000.0
  },
  "beam_shear_connector_free_length_from_column_face_der": {
    "unit": "mm",
    "value": 1000.0
  },
  "beam_shear_connector_free_length_from_column_face_izq": {
    "unit": "mm",
    "value": 1000.0
  },
  "bolt_diameter": {
    "unit": "mm",
    "value": 28.575
  },
  "bolt_fabrication_standard": "ASTM A490",
  "bolt_gage_g": {
    "unit": "mm",
    "value": 152.4
  },
  "bolt_tightening_type": "pretensioned",
  "column_depth_d_col": {
    "unit": "mm",
    "value": 508.0
  },
  "column_depth_limit_max": {
    "unit": "mm",
    "value": 920.0
  },
  "column_ductility_demand": "high",
  "column_end_distance_to_beam_flange_st_col": {
    "unit": "mm",
    "value": 762.0
  },
  "column_flange_width_bcf": {
    "unit": "mm",
    "value": 290.0
  },
  "column_slab_connection_condition": "isolated",
  "column_st_col_min": {
    "unit": "mm",
    "value": 122.5
  },
  "compactness_ca_beam_calculated": 0.0,
  "compactness_ca_column_calculated": 0.0,
  "continuity_plate_enabled": true,
  "continuity_plate_thickness_tcp": {
    "unit": "mm",
    "value": 15.9
  },
  "continuity_plate_weld_type": "CJP",
  "d_col": {
    "unit": "mm",
    "value": 508.0
  },
  "d_hole_w7_col": null,
  "doubler_plate_enabled": false,
  "dz_dp_col": {
    "unit": "mm",
    "value": 427.2
  },
  "edge_de": {
    "unit": "mm",
    "value": 60.0
  },
  "edge_pfi": {
    "unit": "mm",
    "value": 50.0
  },
  "edge_pfo": {
    "unit": "mm",
    "value": 50.0
  },
  "elastic_modulus": {
    "unit": "MPa",
    "value": 199947.965
  },
  "end_plate_beam_web_weld_lines_nl": 2,
  "end_plate_beam_web_weld_thickness_twe": {
    "unit": "mm",
    "value": 8.0
  },
  "end_plate_beam_web_weld_type": "CJP",
  "end_plate_height": {
    "unit": "mm",
    "value": 827.0
  },
  "end_plate_width_bp": {
    "unit": "mm",
    "value": 253.0
  },
  "estado_contacto_dp_col": "en_contacto_con_alma",
  "extended_dp_col": false,
  "gap_dp_col": {
    "unit": "mm",
    "value": 0.0
  },
  "h_dp_col": {
    "unit": "mm",
    "value": 873.8000000000001
  },
  "h_dp_col_formula": "300 + max(d-tf) - t_pc_col",
  "k1_col": {
    "unit": "mm",
    "value": 31.8
  },
  "kdes_col": {
    "unit": "mm",
    "value": 50.5
  },
  "kdet_col": {
    "unit": "mm",
    "value": 50.5
  },
  "kds_w1_vgder": null,
  "kds_w1_vgizq": null,
  "kds_w2_vgder": null,
  "kds_w2_vgizq": null,
  "kds_w5_col": 1.0,
  "kds_w6_col": 1.0,
  "kds_w8_col": 1.0,
  "kds_w9_col": null,
  "n_dp_col": 1,
  "n_pc_col": null,
  "ncolumna_w7_col": 1,
  "nfilas_w7_col": 1,
  "nl_w1_vgder": null,
  "nl_w1_vgizq": null,
  "nl_w2_vgder": 2,
  "nl_w2_vgizq": 2,
  "nl_w5_col": null,
  "nl_w6_col": null,
  "nl_w7_col": 1,
  "nl_w8_col": null,
  "nl_w9_col": null,
  "nl_wdp_plug": 1,
  "phi_fragil": 0.75,
  "pitch_pb": {
    "unit": "mm",
    "value": 0.0
  },
  "pu_columna": {
    "unit": "kN",
    "value": 0.0
  },
  "pu_viga": {
    "unit": "kN",
    "value": 0.0
  },
  "sh_w7_col": null,
  "stiffener_height": {
    "unit": "mm",
    "value": 110.0
  },
  "stiffener_length": {
    "unit": "mm",
    "value": 200.0
  },
  "sv_w7_col": null,
  "t_dp_col": {
    "unit": "mm",
    "value": 22.6
  },
  "t_part_w7_col": {
    "unit": "mm",
    "value": 15.9
  },
  "t_pc_col": {
    "unit": "mm",
    "value": 15.9
  },
  "t_w5_col": null,
  "t_w6_col": null,
  "t_w7_col": {
    "unit": "mm",
    "value": 8.0
  },
  "t_w8_col": null,
  "t_w9_col": null,
  "t_wdp_plug": {
    "unit": "mm",
    "value": 8.0
  },
  "tf_col": {
    "unit": "mm",
    "value": 40.4
  },
  "tfdet_col": {
    "unit": "mm",
    "value": 40.4
  },
  "tipo_acero_dp_col": "ASTM A572 Gr 50",
  "tipo_acero_pc_col": "ASTM A572 Gr 50",
  "tipo_acero_perfil_col": "ASTM A572 Gr 50",
  "tipo_w1_vgder": null,
  "tipo_w1_vgizq": null,
  "tipo_w2_vgder": null,
  "tipo_w2_vgizq": null,
  "tipo_w5_col": "CJP",
  "tipo_w6_col": "CJP",
  "tipo_w7_col": "plug",
  "tipo_w8_col": "CJP",
  "tipo_w9_col": null,
  "tipo_wdp_plug": "plug",
  "tw_col": {
    "unit": "mm",
    "value": 22.6
  },
  "usar_pc_col": true,
  "use_weld_9_col": null,
  "w_w1_vgder": null,
  "w_w1_vgizq": null,
  "w_w2_vgder": {
    "unit": "mm",
    "value": 8.0
  },
  "w_w2_vgizq": {
    "unit": "mm",
    "value": 8.0
  },
  "w_w5_col": null,
  "w_w6_col": null,
  "w_w7_col": {
    "unit": "mm",
    "value": 8.0
  },
  "w_w8_col": null,
  "w_w9_col": null,
  "weld_fexx": {
    "unit": "MPa",
    "value": 490.0
  },
  "wz_dp_col": {
    "unit": "mm",
    "value": 572.4
  }
}
```

### Intermedios

```json
{
  "L_w5_col": null,
  "L_w5_col_formula": "L_w5_col = b2_pc_col - 2*(L_gap_w5_col)",
  "L_w6_col": {
    "unit": "mm",
    "value": 328.0
  },
  "L_w6_col_formula": "L_w6_col = L2_pc_col - 2*(L_gap_w6_col)",
  "L_w8_col": null,
  "L_w8_col_formula": "L_w8_col = h_dp_col - 2*(L_gap_w8_col)",
  "L_w9_col": {
    "unit": "mm",
    "value": 0.0
  },
  "L_w9_col_formula": "L_w9_col = b_dp_col - 2*(L_gap_w9_col) si usar_weld_9_col=true; L_w9_col = 0 si usar_weld_9_col=false",
  "beam_flange_compactness_limit": 6.8861084600317,
  "beam_flange_compactness_ratio_der": 6.589595375722543,
  "beam_flange_compactness_ratio_izq": 6.589595375722543,
  "beam_web_compactness_limit": 56.23655242359222,
  "beam_web_compactness_ratio_der": 48.839285714285715,
  "beam_web_compactness_ratio_izq": 48.839285714285715,
  "bp_margin": 25.0,
  "ca_beam_trace": {
    "ag": {
      "unit": "mm2",
      "value": 14500.0
    },
    "denominator_base": 5502750.000000001,
    "denominator_force_units": 5502.750000000001,
    "formula": "Ca = Pu / (Ry * Ag * Fy)",
    "fy": {
      "unit": "MPa",
      "value": 345.0
    },
    "pu": {
      "unit": "kN",
      "value": 0.0
    },
    "ry": 1.1
  },
  "ca_column_trace": {
    "ag": {
      "unit": "mm2",
      "value": 33200.0
    },
    "denominator_base": 12599400.0,
    "denominator_force_units": 12599.4,
    "formula": "Ca = Pu / (Ry * Ag * Fy)",
    "fy": {
      "unit": "MPa",
      "value": 345.0
    },
    "pu": {
      "unit": "kN",
      "value": 0.0
    },
    "ry": 1.1
  },
  "clear_span_to_depth_limit": {
    "unit": "ratio",
    "value": 7.0
  },
  "clear_span_to_depth_ratio_der": {
    "unit": "ratio",
    "value": 10.042833607907744
  },
  "clear_span_to_depth_ratio_izq": {
    "unit": "ratio",
    "value": 10.042833607907744
  },
  "column_flange_compactness_limit": 6.8861084600317,
  "column_flange_compactness_ratio": 3.589108910891089,
  "column_web_compactness_limit": 56.23655242359222,
  "column_web_compactness_ratio": 18.008849557522122,
  "continuity_plate_weld_thickness_limit": {
    "unit": "mm",
    "value": 10.0
  },
  "frame_system_for_span_ratio": "SMF",
  "j34_lookup": {
    "db_in": 1.125,
    "in_to_mm": 25.4,
    "table_row": "db=1.125 in"
  },
  "j34_lookup_vgizq": {
    "db_in": 1.125,
    "in_to_mm": 25.4,
    "table_row": "db=1.125 in"
  },
  "minimum_bp_bf_plus_margin": {
    "unit": "mm",
    "value": 253.0
  },
  "minimum_edge_distance_j34": {
    "unit": "mm",
    "value": 38.099999999999994
  },
  "minimum_edge_distance_j34_vgizq": {
    "unit": "mm",
    "value": 38.099999999999994
  },
  "minimum_spacing_3db": {
    "unit": "mm",
    "value": 85.725
  },
  "minimum_spacing_3db_vgizq": {
    "unit": "mm",
    "value": 85.725
  },
  "prequalification_limits": [
    {
      "allowed_families": [
        "W",
        "HEA",
        "HEB",
        "IPE"
      ],
      "calculated_symbol": "perfil_vgizq",
      "calculated_text": "W24X76",
      "clause": "Section 2.3.4",
      "comparison": "family_in",
      "comparison_text": "in",
      "description": "Familia de perfil de viga permitida para precalificacion (viga izquierda)",
      "id": "beam_izq.shape_family",
      "limit_symbol": "{W, HEA, HEB, IPE}",
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_families": [
        "W",
        "HEA",
        "HEB",
        "IPE"
      ],
      "calculated_symbol": "perfil_vgder",
      "calculated_text": "W24X76",
      "clause": "Section 2.3.4",
      "comparison": "family_in",
      "comparison_text": "in",
      "description": "Familia de perfil de viga permitida para precalificacion (viga derecha)",
      "id": "beam_der.shape_family",
      "limit_symbol": "{W, HEA, HEB, IPE}",
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgizq",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "End-plate width vs beam flange width (left beam)",
      "id": "beam_izq.bp_ge_bf_plus_margin",
      "limit": {
        "unit": "mm",
        "value": 253.0
      },
      "limit_symbol": "bf_vgizq + margin (25 mm)",
      "margin": {
        "unit": "mm",
        "value": 0.0
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgizq",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Bolt gage minimum spacing (left beam)",
      "id": "beam_izq.bolt_gage_g_ge_3db",
      "limit": {
        "unit": "mm",
        "value": 85.725
      },
      "limit_symbol": "3db",
      "margin": {
        "unit": "mm",
        "value": 66.67500000000001
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 1000.0
      },
      "calculated_symbol": "Lnc_vgizq",
      "clause": "Section 2.3.4 (2)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Length without shear connectors from column face (left beam)",
      "id": "section_2_3_4.no_shear_connectors_zone_izq",
      "limit": {
        "unit": "mm",
        "value": 910.5
      },
      "limit_symbol": "1.5d_vgizq",
      "margin": {
        "unit": "mm",
        "value": 89.5
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 712.0
      },
      "calculated_symbol": "Sc_vgizq",
      "clause": "Section 6.3.1 (beam clearance criterion)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Beam clearance criterion using Sc and S threshold (left beam)",
      "id": "section_6_3_1.beam_sc_greater_than_s_threshold_izq",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1",
      "verification_text": "Sc_vgizq = St_col - pfo_vgizq; S_vgizq = 0.5*sqrt(bcf*g_vgizq); Sc_vgizq > S_vgizq => 712.000 mm > 105.114 mm"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 10.042833607907744
      },
      "calculated_symbol": "Llb_vgizq/d_vgizq",
      "clause": "Section 2.3.4 (5)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Clear span-to-depth ratio by frame system (left beam)",
      "id": "section_2_3_4.clear_span_to_depth_ratio_izq",
      "limit": {
        "unit": "ratio",
        "value": 7.0
      },
      "limit_symbol": "7 (SMF)",
      "margin": {
        "unit": "ratio",
        "value": 3.0428336079077436
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 6.589595375722543
      },
      "calculated_symbol": "lambda_f_vgizq",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam flange width-to-thickness compactness (left beam)",
      "id": "section_2_3_4.beam_flange_width_to_thickness_izq",
      "limit": {
        "unit": "ratio",
        "value": 6.8861084600317
      },
      "limit_symbol": "lambda_f_limit",
      "margin": {
        "unit": "ratio",
        "value": 0.296513084309157
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 48.839285714285715
      },
      "calculated_symbol": "lambda_w_vgizq",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam web width-to-thickness compactness (left beam)",
      "id": "section_2_3_4.beam_web_width_to_thickness_izq",
      "limit": {
        "unit": "ratio",
        "value": 56.23655242359222
      },
      "limit_symbol": "lambda_w_limit",
      "margin": {
        "unit": "ratio",
        "value": 7.397266709306507
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgder",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "End-plate width vs beam flange width (right beam)",
      "id": "beam_der.bp_ge_bf_plus_margin",
      "limit": {
        "unit": "mm",
        "value": 253.0
      },
      "limit_symbol": "bf_vgder + margin (25 mm)",
      "margin": {
        "unit": "mm",
        "value": 0.0
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgder",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Bolt gage minimum spacing (right beam)",
      "id": "beam_der.bolt_gage_g_ge_3db",
      "limit": {
        "unit": "mm",
        "value": 85.725
      },
      "limit_symbol": "3db",
      "margin": {
        "unit": "mm",
        "value": 66.67500000000001
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 1000.0
      },
      "calculated_symbol": "Lnc_vgder",
      "clause": "Section 2.3.4 (2)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Length without shear connectors from column face (right beam)",
      "id": "section_2_3_4.no_shear_connectors_zone_der",
      "limit": {
        "unit": "mm",
        "value": 910.5
      },
      "limit_symbol": "1.5d_vgder",
      "margin": {
        "unit": "mm",
        "value": 89.5
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 712.0
      },
      "calculated_symbol": "Sc_vgder",
      "clause": "Section 6.3.1 (beam clearance criterion)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Beam clearance criterion using Sc and S threshold (right beam)",
      "id": "section_6_3_1.beam_sc_greater_than_s_threshold_der",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1",
      "verification_text": "Sc_vgder = St_col - pfo_vgder; S_vgder = 0.5*sqrt(bcf*g_vgder); Sc_vgder > S_vgder => 712.000 mm > 105.114 mm"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 10.042833607907744
      },
      "calculated_symbol": "Llb_vgder/d_vgder",
      "clause": "Section 2.3.4 (5)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Clear span-to-depth ratio by frame system (right beam)",
      "id": "section_2_3_4.clear_span_to_depth_ratio_der",
      "limit": {
        "unit": "ratio",
        "value": 7.0
      },
      "limit_symbol": "7 (SMF)",
      "margin": {
        "unit": "ratio",
        "value": 3.0428336079077436
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 6.589595375722543
      },
      "calculated_symbol": "lambda_f_vgder",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam flange width-to-thickness compactness (right beam)",
      "id": "section_2_3_4.beam_flange_width_to_thickness_der",
      "limit": {
        "unit": "ratio",
        "value": 6.8861084600317
      },
      "limit_symbol": "lambda_f_limit",
      "margin": {
        "unit": "ratio",
        "value": 0.296513084309157
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 48.839285714285715
      },
      "calculated_symbol": "lambda_w_vgder",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam web width-to-thickness compactness (right beam)",
      "id": "section_2_3_4.beam_web_width_to_thickness_der",
      "limit": {
        "unit": "ratio",
        "value": 56.23655242359222
      },
      "limit_symbol": "lambda_w_limit",
      "margin": {
        "unit": "ratio",
        "value": 7.397266709306507
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_families": [
        "W",
        "HEA",
        "HEB",
        "IPE"
      ],
      "calculated_symbol": "shape_col",
      "calculated_text": "W18X175",
      "clause": "Section 2.3.4",
      "comparison": "family_in",
      "comparison_text": "in",
      "description": "Column profile family allowed for prequalification",
      "id": "column.shape_family",
      "limit_symbol": "{W, HEA, HEB, IPE}",
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 508.0
      },
      "calculated_symbol": "d_col",
      "clause": "Section 6.3 (3)",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Column profile depth maximum (W36/W920)",
      "id": "section_6_3.column_depth_maximum",
      "limit": {
        "unit": "mm",
        "value": 920.0
      },
      "limit_symbol": "W36/W920",
      "margin": {
        "unit": "mm",
        "value": 412.0
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "End-plate fit within column flange width",
      "id": "column.bp_le_bcf",
      "limit": {
        "unit": "mm",
        "value": 290.0
      },
      "limit_symbol": "bcf",
      "margin": {
        "unit": "mm",
        "value": 37.0
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "col_losa",
      "calculated_text": "isolated",
      "clause": "Section 2.3.4 (3)",
      "comparison": "equals",
      "comparison_text": "==",
      "description": "Column-slab connection condition",
      "expected_text": "isolated",
      "id": "section_2_3_4.slab_isolation_condition",
      "limit_symbol": "isolated",
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 762.0
      },
      "calculated_symbol": "St_col",
      "clause": "Section 6.3.1 (column top clearance criterion)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Proyeccion de columna minima por encima de las vigas",
      "id": "section_6_3_1.column_stc_minimum_requirement",
      "limit_symbol": "compound",
      "minimum": {
        "unit": "mm",
        "value": 122.5
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1",
      "verification_text": "St_col >= pfo_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + de_pe_vgizq + 12.5 mm; 762.000 mm >= 122.500 mm; 762.000 mm >= 122.500 mm"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 3.589108910891089
      },
      "calculated_symbol": "lambda_f_col",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Column flange width-to-thickness compactness",
      "id": "section_2_3_4.column_flange_width_to_thickness",
      "limit": {
        "unit": "ratio",
        "value": 6.8861084600317
      },
      "limit_symbol": "lambda_f_limit",
      "margin": {
        "unit": "ratio",
        "value": 3.2969995491406108
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 18.008849557522122
      },
      "calculated_symbol": "lambda_w_col",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Column web width-to-thickness compactness",
      "id": "section_2_3_4.column_web_width_to_thickness",
      "limit": {
        "unit": "ratio",
        "value": 56.23655242359222
      },
      "limit_symbol": "lambda_w_limit",
      "margin": {
        "unit": "ratio",
        "value": 38.2277028660701
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 22.6
      },
      "calculated_symbol": "tw_col",
      "clause": "AISC 341-22w E3.6e.2",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Espesor individual minimo del alma de columna",
      "id": "section_e3_6_2.column_web_thickness_minimum",
      "limit": {
        "unit": "mm",
        "value": 11.106666666666666
      },
      "limit_symbol": "(dz_dp_col + wz_dp_col)/90; si use_weld_7_col=false: dz_dp_col=d_col-2*tf_col, wz_dp_col=max{d_lado-2*tf_lado}; si use_weld_7_col=true: dz_dp_col=h_dp_col/(nfilas_w7_col + 1), wz_dp_col=b_dp_col/(ncolumna_w7_col + 1)",
      "margin": {
        "unit": "mm",
        "value": 11.493333333333336
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgder",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate width explicit dual inequalities (right beam)",
      "id": "section_6_3.end_plate_width_dual_limit_der",
      "limit_symbol": "compound",
      "maximum": {
        "unit": "mm",
        "value": 253.0
      },
      "minimum": {
        "unit": "mm",
        "value": 177.79999999999998
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1",
      "verification_text": "bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.3
      },
      "calculated_symbol": "deh_pe_vgder",
      "clause": "Section 6.3 / Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal edge distance from plate edge to bolt line (right beam)",
      "id": "section_6_3.end_plate_horizontal_edge_distance_ge_emin_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.200000000000003
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgizq",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate width explicit dual inequalities (left beam)",
      "id": "section_6_3.end_plate_width_dual_limit_izq",
      "limit_symbol": "compound",
      "maximum": {
        "unit": "mm",
        "value": 253.0
      },
      "minimum": {
        "unit": "mm",
        "value": 177.79999999999998
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1",
      "verification_text": "bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.3
      },
      "calculated_symbol": "deh_pe_vgizq",
      "clause": "Section 6.3 / Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal edge distance from plate edge to bolt line (left beam)",
      "id": "section_6_3.end_plate_horizontal_edge_distance_ge_emin_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.200000000000003
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 110.0
      },
      "calculated_symbol": "h_pest_vgder",
      "clause": "Section 6.3",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate stiffener height derived from end-plate geometry (right beam)",
      "id": "section_6_3.end_plate_stiffener_height_derived_der",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "end_plate_stiffener_der",
      "status": "PASS",
      "step": "1",
      "verification_text": "h_pest_vgder = pfo_pe_vgder + de_pe_vgder; 110.000 mm = 50.000 mm + 60.000 mm"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 110.0
      },
      "calculated_symbol": "h_pest_vgizq",
      "clause": "Section 6.3",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate stiffener height derived from end-plate geometry (left beam)",
      "id": "section_6_3.end_plate_stiffener_height_derived_izq",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "end_plate_stiffener_izq",
      "status": "PASS",
      "step": "1",
      "verification_text": "h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; 110.000 mm = 50.000 mm + 60.000 mm"
    },
    {
      "calculated_symbol": "tipo_w4_vgder",
      "clause": "Section 6.7",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha)",
      "id": "section_6_7.beam_flange_to_end_plate_weld_requirement_vgder",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_4_vgder",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 8 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 0.000 mm"
    },
    {
      "calculated_symbol": "tipo_w4_vgizq",
      "clause": "Section 6.7",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda)",
      "id": "section_6_7.beam_flange_to_end_plate_weld_requirement_vgizq",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_4_vgizq",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 8 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 0.000 mm"
    },
    {
      "allowed_values": [
        "cjp",
        "double_sided_fillet",
        "single_sided_fillet"
      ],
      "calculated_symbol": "weld_ep_web_vgder",
      "calculated_text": "cjp",
      "clause": "Section 6.7",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "End-plate to beam-web weld type shall be an allowed category (right beam)",
      "id": "section_6_7.end_plate_beam_web_weld_type_allowed_vgder",
      "limit_symbol": "{cjp, double_sided_fillet, single_sided_fillet}",
      "result": "OK",
      "scope": "weld_3_vgder",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tipo_w1_vgder",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de end-plate con rigidizador segun espesor del rigidizador (viga derecha)",
      "id": "section_6_7.weld_1_type_vs_stiffener_thickness_vgder",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_1_vgder",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgder > 10.000 mm: tipo_w1_vgder == cjp; dato faltante: t_pest_vgder"
    },
    {
      "calculated_symbol": "tipo_w2_vgder",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga derecha)",
      "id": "section_6_7.weld_2_type_vs_stiffener_thickness_vgder",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_2_vgder",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgder > 10.000 mm: tipo_w2_vgder == cjp; dato faltante: t_pest_vgder"
    },
    {
      "allowed_values": [
        "cjp",
        "double_sided_fillet",
        "single_sided_fillet"
      ],
      "calculated_symbol": "weld_ep_web_vgizq",
      "calculated_text": "cjp",
      "clause": "Section 6.7",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "End-plate to beam-web weld type shall be an allowed category (left beam)",
      "id": "section_6_7.end_plate_beam_web_weld_type_allowed_vgizq",
      "limit_symbol": "{cjp, double_sided_fillet, single_sided_fillet}",
      "result": "OK",
      "scope": "weld_3_vgizq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tipo_w1_vgizq",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de end-plate con rigidizador segun espesor del rigidizador (viga izquierda)",
      "id": "section_6_7.weld_1_type_vs_stiffener_thickness_vgizq",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_1_vgizq",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgizq > 10.000 mm: tipo_w1_vgizq == cjp; dato faltante: t_pest_vgizq"
    },
    {
      "calculated_symbol": "tipo_w2_vgizq",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga izquierda)",
      "id": "section_6_7.weld_2_type_vs_stiffener_thickness_vgizq",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_2_vgizq",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgizq > 10.000 mm: tipo_w2_vgizq == cjp; dato faltante: t_pest_vgizq"
    },
    {
      "allowed_values": [
        "cjp",
        "pjp",
        "fillet"
      ],
      "calculated_symbol": "tipo_w6_col",
      "calculated_text": "cjp",
      "clause": "Section 6.7",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Tipo de soldadura #6 permitido",
      "id": "section_6_7.weld_6_type_allowed_col",
      "limit_symbol": "{cjp, pjp, fillet}",
      "result": "OK",
      "scope": "weld_6_col",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "fillet",
        "cjp"
      ],
      "calculated_symbol": "tipo_w5_col",
      "calculated_text": "cjp",
      "clause": "Section 6.3 (continuity plate weld detail)",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Continuity-plate weld type shall be explicitly declared with an allowed weld category",
      "id": "section_6_3.continuity_plate_weld_type_declared",
      "limit_symbol": "{fillet, cjp}",
      "result": "OK",
      "scope": "weld_5_col",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "fillet",
        "cjp"
      ],
      "calculated_symbol": "tipo_w5_col",
      "calculated_text": "cjp",
      "clause": "Section 6.3 (continuity plate weld detail)",
      "comparison": "conditional_allowed_set",
      "comparison_text": "in_if",
      "condition_applies": false,
      "description": "Tamano minimo de soldadura #5 cuando tipo_w5_col es fillet",
      "governing_condition": "cjp_always_permitted",
      "id": "section_6_3.continuity_plate_weld_type_for_thin_plate",
      "limit_symbol": "{fillet, cjp}; si fillet => w_w5_col >= 0.75*t_pc_col",
      "required_weld_size": {
        "unit": "mm",
        "value": 11.925
      },
      "result": "OK",
      "scope": "weld_5_col",
      "status": "PASS",
      "step": "1",
      "thickness": {
        "unit": "mm",
        "value": 15.9
      },
      "weld_size": null
    },
    {
      "allowed_values": [
        "pretensioned",
        "snug_tight"
      ],
      "calculated_symbol": "tight_bolt_vgder",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt tightening type must be one recognized category (right beam)",
      "id": "section_4_1.bolt_tightening_type_valid_der",
      "limit_symbol": "{pretensioned, snug_tight}",
      "result": "OK",
      "scope": "bolts_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tight_bolt_vgder",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "equals",
      "comparison_text": "==",
      "description": "Bolts shall be pretensioned unless a specific connection permits otherwise (right beam)",
      "expected_text": "pretensioned",
      "id": "section_4_1.bolt_tightening_required_pretensioned_der",
      "limit_symbol": "pretensioned",
      "result": "OK",
      "scope": "bolts_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "ASTM F3125/F3125M",
        "ASTM A325",
        "ASTM A325M",
        "ASTM A490",
        "ASTM A490M",
        "ASTM F1852",
        "ASTM F2280"
      ],
      "calculated_symbol": "std_bolt_vgder",
      "calculated_text": "ASTM A490",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt fabrication standard must be an allowed high-strength ASTM designation (right beam)",
      "id": "section_4_1.bolt_fabrication_standard_permitted_der",
      "limit_symbol": "{ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}",
      "result": "OK",
      "scope": "bolts_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "pretensioned",
        "snug_tight"
      ],
      "calculated_symbol": "tight_bolt_vgizq",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt tightening type must be one recognized category (left beam)",
      "id": "section_4_1.bolt_tightening_type_valid_izq",
      "limit_symbol": "{pretensioned, snug_tight}",
      "result": "OK",
      "scope": "bolts_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tight_bolt_vgizq",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "equals",
      "comparison_text": "==",
      "description": "Bolts shall be pretensioned unless a specific connection permits otherwise (left beam)",
      "expected_text": "pretensioned",
      "id": "section_4_1.bolt_tightening_required_pretensioned_izq",
      "limit_symbol": "pretensioned",
      "result": "OK",
      "scope": "bolts_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "ASTM F3125/F3125M",
        "ASTM A325",
        "ASTM A325M",
        "ASTM A490",
        "ASTM A490M",
        "ASTM F1852",
        "ASTM F2280"
      ],
      "calculated_symbol": "std_bolt_vgizq",
      "calculated_text": "ASTM A490",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt fabrication standard must be an allowed high-strength ASTM designation (left beam)",
      "id": "section_4_1.bolt_fabrication_standard_permitted_izq",
      "limit_symbol": "{ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}",
      "result": "OK",
      "scope": "bolts_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Edge distance at de (right beam)",
      "id": "table_6_1.edge_de_ge_emin_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 21.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Maximum edge distance at de (right beam)",
      "id": "table_6_1.edge_de_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 90.0
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside bolt-row distance minimum (right beam)",
      "id": "table_6_1.edge_pfo_ge_pfo_min_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfo_pe_vgder_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside bolt-row distance maximum (right beam)",
      "id": "table_6_1.edge_pfo_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfo_pe_vgder_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside adjusted edge distance minimum (right beam)",
      "id": "table_6_1.edge_pso_ge_emin_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.600000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgder",
      "clause": "AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside adjusted edge distance maximum (right beam)",
      "id": "table_6_1.edge_pso_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 99.30000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Inside bolt-row distance minimum (right beam)",
      "id": "table_6_1.edge_pfi_ge_pfi_min_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfi_pe_vgder_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Inside bolt-row distance maximum (right beam)",
      "id": "table_6_1.edge_pfi_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfi_pe_vgder_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 228.0
      },
      "calculated_symbol": "bf_vgder",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Beam flange width limits (right beam)",
      "id": "table_6_1.bbf.range_der",
      "limit_symbol": "[bf_vgder_min, bf_vgder_max]",
      "margin": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 75.60000000000002
      },
      "maximum": {
        "unit": "mm",
        "value": 234.95
      },
      "minimum": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 607.0
      },
      "calculated_symbol": "d_vgder",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Connecting beam depth limits (right beam)",
      "id": "table_6_1.d.range_der",
      "limit_symbol": "[d_vgder_min, d_vgder_max]",
      "margin": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 257.75
      },
      "maximum": {
        "unit": "mm",
        "value": 609.5999999999999
      },
      "minimum": {
        "unit": "mm",
        "value": 349.25
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 25.4
      },
      "calculated_symbol": "tpe_vgder",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "End-plate thickness limits (right beam)",
      "id": "table_6_1.tp.range_der",
      "limit_symbol": "[tpe_vgder_min, tpe_vgder_max]",
      "margin": {
        "unit": "mm",
        "value": 12.7
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 31.75
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 12.7
      },
      "maximum": {
        "unit": "mm",
        "value": 57.15
      },
      "minimum": {
        "unit": "mm",
        "value": 12.7
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.3 (compute_minimum_bolt_spacing_j33)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal bolt spacing minimum (right beam)",
      "id": "table_6_1.g.ge_min_der",
      "limit": {
        "unit": "mm",
        "value": 101.6
      },
      "limit_symbol": "max(g_b_vgder_min, 3db_j33)",
      "margin": {
        "unit": "mm",
        "value": 50.80000000000001
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Horizontal bolt spacing maximum (right beam)",
      "id": "table_6_1.g.le_max_der",
      "limit": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "limit_symbol": "min(g_b_vgder_max, smax_j36)",
      "margin": {
        "unit": "mm",
        "value": -2.842170943040401e-14
      },
      "result": "NO_OK",
      "scope": "end_plate_der",
      "status": "FAIL",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Edge distance at de (left beam)",
      "id": "table_6_1.edge_de_ge_emin_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 21.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Maximum edge distance at de (left beam)",
      "id": "table_6_1.edge_de_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 90.0
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside bolt-row distance minimum (left beam)",
      "id": "table_6_1.edge_pfo_ge_pfo_min_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfo_pe_vgizq_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside bolt-row distance maximum (left beam)",
      "id": "table_6_1.edge_pfo_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfo_pe_vgizq_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside adjusted edge distance minimum (left beam)",
      "id": "table_6_1.edge_pso_ge_emin_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.600000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgizq",
      "clause": "AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside adjusted edge distance maximum (left beam)",
      "id": "table_6_1.edge_pso_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 99.30000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Inside bolt-row distance minimum (left beam)",
      "id": "table_6_1.edge_pfi_ge_pfi_min_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfi_pe_vgizq_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Inside bolt-row distance maximum (left beam)",
      "id": "table_6_1.edge_pfi_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfi_pe_vgizq_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 228.0
      },
      "calculated_symbol": "bf_vgizq",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Beam flange width limits (left beam)",
      "id": "table_6_1.bbf.range_izq",
      "limit_symbol": "[bf_vgizq_min, bf_vgizq_max]",
      "margin": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 75.60000000000002
      },
      "maximum": {
        "unit": "mm",
        "value": 234.95
      },
      "minimum": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 607.0
      },
      "calculated_symbol": "d_vgizq",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Connecting beam depth limits (left beam)",
      "id": "table_6_1.d.range_izq",
      "limit_symbol": "[d_vgizq_min, d_vgizq_max]",
      "margin": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 257.75
      },
      "maximum": {
        "unit": "mm",
        "value": 609.5999999999999
      },
      "minimum": {
        "unit": "mm",
        "value": 349.25
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 25.4
      },
      "calculated_symbol": "tpe_vgizq",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "End-plate thickness limits (left beam)",
      "id": "table_6_1.tp.range_izq",
      "limit_symbol": "[tpe_vgizq_min, tpe_vgizq_max]",
      "margin": {
        "unit": "mm",
        "value": 12.7
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 31.75
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 12.7
      },
      "maximum": {
        "unit": "mm",
        "value": 57.15
      },
      "minimum": {
        "unit": "mm",
        "value": 12.7
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.3 (compute_minimum_bolt_spacing_j33)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal bolt spacing minimum (left beam)",
      "id": "table_6_1.g.ge_min_izq",
      "limit": {
        "unit": "mm",
        "value": 101.6
      },
      "limit_symbol": "max(g_b_vgizq_min, 3db_j33)",
      "margin": {
        "unit": "mm",
        "value": 50.80000000000001
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Horizontal bolt spacing maximum (left beam)",
      "id": "table_6_1.g.le_max_izq",
      "limit": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "limit_symbol": "min(g_b_vgizq_max, smax_j36)",
      "margin": {
        "unit": "mm",
        "value": -2.842170943040401e-14
      },
      "result": "NO_OK",
      "scope": "end_plate_izq",
      "status": "FAIL",
      "step": "1"
    }
  ],
  "step_1_limits": [
    {
      "allowed_families": [
        "W",
        "HEA",
        "HEB",
        "IPE"
      ],
      "calculated_symbol": "perfil_vgizq",
      "calculated_text": "W24X76",
      "clause": "Section 2.3.4",
      "comparison": "family_in",
      "comparison_text": "in",
      "description": "Familia de perfil de viga permitida para precalificacion (viga izquierda)",
      "id": "beam_izq.shape_family",
      "limit_symbol": "{W, HEA, HEB, IPE}",
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_families": [
        "W",
        "HEA",
        "HEB",
        "IPE"
      ],
      "calculated_symbol": "perfil_vgder",
      "calculated_text": "W24X76",
      "clause": "Section 2.3.4",
      "comparison": "family_in",
      "comparison_text": "in",
      "description": "Familia de perfil de viga permitida para precalificacion (viga derecha)",
      "id": "beam_der.shape_family",
      "limit_symbol": "{W, HEA, HEB, IPE}",
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgizq",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "End-plate width vs beam flange width (left beam)",
      "id": "beam_izq.bp_ge_bf_plus_margin",
      "limit": {
        "unit": "mm",
        "value": 253.0
      },
      "limit_symbol": "bf_vgizq + margin (25 mm)",
      "margin": {
        "unit": "mm",
        "value": 0.0
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgizq",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Bolt gage minimum spacing (left beam)",
      "id": "beam_izq.bolt_gage_g_ge_3db",
      "limit": {
        "unit": "mm",
        "value": 85.725
      },
      "limit_symbol": "3db",
      "margin": {
        "unit": "mm",
        "value": 66.67500000000001
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 1000.0
      },
      "calculated_symbol": "Lnc_vgizq",
      "clause": "Section 2.3.4 (2)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Length without shear connectors from column face (left beam)",
      "id": "section_2_3_4.no_shear_connectors_zone_izq",
      "limit": {
        "unit": "mm",
        "value": 910.5
      },
      "limit_symbol": "1.5d_vgizq",
      "margin": {
        "unit": "mm",
        "value": 89.5
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 712.0
      },
      "calculated_symbol": "Sc_vgizq",
      "clause": "Section 6.3.1 (beam clearance criterion)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Beam clearance criterion using Sc and S threshold (left beam)",
      "id": "section_6_3_1.beam_sc_greater_than_s_threshold_izq",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1",
      "verification_text": "Sc_vgizq = St_col - pfo_vgizq; S_vgizq = 0.5*sqrt(bcf*g_vgizq); Sc_vgizq > S_vgizq => 712.000 mm > 105.114 mm"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 10.042833607907744
      },
      "calculated_symbol": "Llb_vgizq/d_vgizq",
      "clause": "Section 2.3.4 (5)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Clear span-to-depth ratio by frame system (left beam)",
      "id": "section_2_3_4.clear_span_to_depth_ratio_izq",
      "limit": {
        "unit": "ratio",
        "value": 7.0
      },
      "limit_symbol": "7 (SMF)",
      "margin": {
        "unit": "ratio",
        "value": 3.0428336079077436
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 6.589595375722543
      },
      "calculated_symbol": "lambda_f_vgizq",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam flange width-to-thickness compactness (left beam)",
      "id": "section_2_3_4.beam_flange_width_to_thickness_izq",
      "limit": {
        "unit": "ratio",
        "value": 6.8861084600317
      },
      "limit_symbol": "lambda_f_limit",
      "margin": {
        "unit": "ratio",
        "value": 0.296513084309157
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 48.839285714285715
      },
      "calculated_symbol": "lambda_w_vgizq",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam web width-to-thickness compactness (left beam)",
      "id": "section_2_3_4.beam_web_width_to_thickness_izq",
      "limit": {
        "unit": "ratio",
        "value": 56.23655242359222
      },
      "limit_symbol": "lambda_w_limit",
      "margin": {
        "unit": "ratio",
        "value": 7.397266709306507
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgder",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "End-plate width vs beam flange width (right beam)",
      "id": "beam_der.bp_ge_bf_plus_margin",
      "limit": {
        "unit": "mm",
        "value": 253.0
      },
      "limit_symbol": "bf_vgder + margin (25 mm)",
      "margin": {
        "unit": "mm",
        "value": 0.0
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgder",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Bolt gage minimum spacing (right beam)",
      "id": "beam_der.bolt_gage_g_ge_3db",
      "limit": {
        "unit": "mm",
        "value": 85.725
      },
      "limit_symbol": "3db",
      "margin": {
        "unit": "mm",
        "value": 66.67500000000001
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 1000.0
      },
      "calculated_symbol": "Lnc_vgder",
      "clause": "Section 2.3.4 (2)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Length without shear connectors from column face (right beam)",
      "id": "section_2_3_4.no_shear_connectors_zone_der",
      "limit": {
        "unit": "mm",
        "value": 910.5
      },
      "limit_symbol": "1.5d_vgder",
      "margin": {
        "unit": "mm",
        "value": 89.5
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 712.0
      },
      "calculated_symbol": "Sc_vgder",
      "clause": "Section 6.3.1 (beam clearance criterion)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Beam clearance criterion using Sc and S threshold (right beam)",
      "id": "section_6_3_1.beam_sc_greater_than_s_threshold_der",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1",
      "verification_text": "Sc_vgder = St_col - pfo_vgder; S_vgder = 0.5*sqrt(bcf*g_vgder); Sc_vgder > S_vgder => 712.000 mm > 105.114 mm"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 10.042833607907744
      },
      "calculated_symbol": "Llb_vgder/d_vgder",
      "clause": "Section 2.3.4 (5)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Clear span-to-depth ratio by frame system (right beam)",
      "id": "section_2_3_4.clear_span_to_depth_ratio_der",
      "limit": {
        "unit": "ratio",
        "value": 7.0
      },
      "limit_symbol": "7 (SMF)",
      "margin": {
        "unit": "ratio",
        "value": 3.0428336079077436
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 6.589595375722543
      },
      "calculated_symbol": "lambda_f_vgder",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam flange width-to-thickness compactness (right beam)",
      "id": "section_2_3_4.beam_flange_width_to_thickness_der",
      "limit": {
        "unit": "ratio",
        "value": 6.8861084600317
      },
      "limit_symbol": "lambda_f_limit",
      "margin": {
        "unit": "ratio",
        "value": 0.296513084309157
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 48.839285714285715
      },
      "calculated_symbol": "lambda_w_vgder",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Beam web width-to-thickness compactness (right beam)",
      "id": "section_2_3_4.beam_web_width_to_thickness_der",
      "limit": {
        "unit": "ratio",
        "value": 56.23655242359222
      },
      "limit_symbol": "lambda_w_limit",
      "margin": {
        "unit": "ratio",
        "value": 7.397266709306507
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_families": [
        "W",
        "HEA",
        "HEB",
        "IPE"
      ],
      "calculated_symbol": "shape_col",
      "calculated_text": "W18X175",
      "clause": "Section 2.3.4",
      "comparison": "family_in",
      "comparison_text": "in",
      "description": "Column profile family allowed for prequalification",
      "id": "column.shape_family",
      "limit_symbol": "{W, HEA, HEB, IPE}",
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 508.0
      },
      "calculated_symbol": "d_col",
      "clause": "Section 6.3 (3)",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Column profile depth maximum (W36/W920)",
      "id": "section_6_3.column_depth_maximum",
      "limit": {
        "unit": "mm",
        "value": 920.0
      },
      "limit_symbol": "W36/W920",
      "margin": {
        "unit": "mm",
        "value": 412.0
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "End-plate fit within column flange width",
      "id": "column.bp_le_bcf",
      "limit": {
        "unit": "mm",
        "value": 290.0
      },
      "limit_symbol": "bcf",
      "margin": {
        "unit": "mm",
        "value": 37.0
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "col_losa",
      "calculated_text": "isolated",
      "clause": "Section 2.3.4 (3)",
      "comparison": "equals",
      "comparison_text": "==",
      "description": "Column-slab connection condition",
      "expected_text": "isolated",
      "id": "section_2_3_4.slab_isolation_condition",
      "limit_symbol": "isolated",
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 762.0
      },
      "calculated_symbol": "St_col",
      "clause": "Section 6.3.1 (column top clearance criterion)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Proyeccion de columna minima por encima de las vigas",
      "id": "section_6_3_1.column_stc_minimum_requirement",
      "limit_symbol": "compound",
      "minimum": {
        "unit": "mm",
        "value": 122.5
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1",
      "verification_text": "St_col >= pfo_pe_vgder + de_pe_vgder + 12.5 mm; St_col >= pfo_pe_vgizq + de_pe_vgizq + 12.5 mm; 762.000 mm >= 122.500 mm; 762.000 mm >= 122.500 mm"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 3.589108910891089
      },
      "calculated_symbol": "lambda_f_col",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Column flange width-to-thickness compactness",
      "id": "section_2_3_4.column_flange_width_to_thickness",
      "limit": {
        "unit": "ratio",
        "value": 6.8861084600317
      },
      "limit_symbol": "lambda_f_limit",
      "margin": {
        "unit": "ratio",
        "value": 3.2969995491406108
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "ratio",
        "value": 18.008849557522122
      },
      "calculated_symbol": "lambda_w_col",
      "clause": "AISC 341-22w / AISC 358-22w Section 2.3.4 (6) + AISC Seismic Provisions",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Column web width-to-thickness compactness",
      "id": "section_2_3_4.column_web_width_to_thickness",
      "limit": {
        "unit": "ratio",
        "value": 56.23655242359222
      },
      "limit_symbol": "lambda_w_limit",
      "margin": {
        "unit": "ratio",
        "value": 38.2277028660701
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 22.6
      },
      "calculated_symbol": "tw_col",
      "clause": "AISC 341-22w E3.6e.2",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Espesor individual minimo del alma de columna",
      "id": "section_e3_6_2.column_web_thickness_minimum",
      "limit": {
        "unit": "mm",
        "value": 11.106666666666666
      },
      "limit_symbol": "(dz_dp_col + wz_dp_col)/90; si use_weld_7_col=false: dz_dp_col=d_col-2*tf_col, wz_dp_col=max{d_lado-2*tf_lado}; si use_weld_7_col=true: dz_dp_col=h_dp_col/(nfilas_w7_col + 1), wz_dp_col=b_dp_col/(ncolumna_w7_col + 1)",
      "margin": {
        "unit": "mm",
        "value": 11.493333333333336
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgder",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate width explicit dual inequalities (right beam)",
      "id": "section_6_3.end_plate_width_dual_limit_der",
      "limit_symbol": "compound",
      "maximum": {
        "unit": "mm",
        "value": 253.0
      },
      "minimum": {
        "unit": "mm",
        "value": 177.79999999999998
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1",
      "verification_text": "bp_pe_vgder <= bbf_vgder + 25 mm; bp_pe_vgder <= bcf"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.3
      },
      "calculated_symbol": "deh_pe_vgder",
      "clause": "Section 6.3 / Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal edge distance from plate edge to bolt line (right beam)",
      "id": "section_6_3.end_plate_horizontal_edge_distance_ge_emin_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.200000000000003
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 253.0
      },
      "calculated_symbol": "bp_pe_vgizq",
      "clause": "Section 6.3 / Table 6.1",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate width explicit dual inequalities (left beam)",
      "id": "section_6_3.end_plate_width_dual_limit_izq",
      "limit_symbol": "compound",
      "maximum": {
        "unit": "mm",
        "value": 253.0
      },
      "minimum": {
        "unit": "mm",
        "value": 177.79999999999998
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1",
      "verification_text": "bp_pe_vgizq <= bbf_vgizq + 25 mm; bp_pe_vgizq <= bcf"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.3
      },
      "calculated_symbol": "deh_pe_vgizq",
      "clause": "Section 6.3 / Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal edge distance from plate edge to bolt line (left beam)",
      "id": "section_6_3.end_plate_horizontal_edge_distance_ge_emin_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.200000000000003
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 110.0
      },
      "calculated_symbol": "h_pest_vgder",
      "clause": "Section 6.3",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate stiffener height derived from end-plate geometry (right beam)",
      "id": "section_6_3.end_plate_stiffener_height_derived_der",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "end_plate_stiffener_der",
      "status": "PASS",
      "step": "1",
      "verification_text": "h_pest_vgder = pfo_pe_vgder + de_pe_vgder; 110.000 mm = 50.000 mm + 60.000 mm"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 110.0
      },
      "calculated_symbol": "h_pest_vgizq",
      "clause": "Section 6.3",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "End-plate stiffener height derived from end-plate geometry (left beam)",
      "id": "section_6_3.end_plate_stiffener_height_derived_izq",
      "limit_symbol": "compound",
      "result": "OK",
      "scope": "end_plate_stiffener_izq",
      "status": "PASS",
      "step": "1",
      "verification_text": "h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; 110.000 mm = 50.000 mm + 60.000 mm"
    },
    {
      "calculated_symbol": "tipo_w4_vgder",
      "clause": "Section 6.7",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Requisitos de soldadura entre ala de viga y placa de extremo (viga derecha)",
      "id": "section_6_7.beam_flange_to_end_plate_weld_requirement_vgder",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_4_vgder",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si demanda_ductilidad_vgder in {high, moderate}: tipo_w4_vgder == cjp; t_w4_1_vgder == 8 mm; demanda_ductilidad_vgder = high; tipo_w4_vgder = cjp; t_w4_1_vgder = 0.000 mm"
    },
    {
      "calculated_symbol": "tipo_w4_vgizq",
      "clause": "Section 6.7",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Requisitos de soldadura entre ala de viga y placa de extremo (viga izquierda)",
      "id": "section_6_7.beam_flange_to_end_plate_weld_requirement_vgizq",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_4_vgizq",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si demanda_ductilidad_vgizq in {high, moderate}: tipo_w4_vgizq == cjp; t_w4_1_vgizq == 8 mm; demanda_ductilidad_vgizq = high; tipo_w4_vgizq = cjp; t_w4_1_vgizq = 0.000 mm"
    },
    {
      "allowed_values": [
        "cjp",
        "double_sided_fillet",
        "single_sided_fillet"
      ],
      "calculated_symbol": "weld_ep_web_vgder",
      "calculated_text": "cjp",
      "clause": "Section 6.7",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "End-plate to beam-web weld type shall be an allowed category (right beam)",
      "id": "section_6_7.end_plate_beam_web_weld_type_allowed_vgder",
      "limit_symbol": "{cjp, double_sided_fillet, single_sided_fillet}",
      "result": "OK",
      "scope": "weld_3_vgder",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tipo_w1_vgder",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de end-plate con rigidizador segun espesor del rigidizador (viga derecha)",
      "id": "section_6_7.weld_1_type_vs_stiffener_thickness_vgder",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_1_vgder",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgder > 10.000 mm: tipo_w1_vgder == cjp; dato faltante: t_pest_vgder"
    },
    {
      "calculated_symbol": "tipo_w2_vgder",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga derecha)",
      "id": "section_6_7.weld_2_type_vs_stiffener_thickness_vgder",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_2_vgder",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgder > 10.000 mm: tipo_w2_vgder == cjp; dato faltante: t_pest_vgder"
    },
    {
      "allowed_values": [
        "cjp",
        "double_sided_fillet",
        "single_sided_fillet"
      ],
      "calculated_symbol": "weld_ep_web_vgizq",
      "calculated_text": "cjp",
      "clause": "Section 6.7",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "End-plate to beam-web weld type shall be an allowed category (left beam)",
      "id": "section_6_7.end_plate_beam_web_weld_type_allowed_vgizq",
      "limit_symbol": "{cjp, double_sided_fillet, single_sided_fillet}",
      "result": "OK",
      "scope": "weld_3_vgizq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tipo_w1_vgizq",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de end-plate con rigidizador segun espesor del rigidizador (viga izquierda)",
      "id": "section_6_7.weld_1_type_vs_stiffener_thickness_vgizq",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_1_vgizq",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgizq > 10.000 mm: tipo_w1_vgizq == cjp; dato faltante: t_pest_vgizq"
    },
    {
      "calculated_symbol": "tipo_w2_vgizq",
      "clause": "Section 6.7 (item 6)",
      "comparison": "compound",
      "comparison_text": "compound",
      "description": "Tipo de soldadura de viga con rigidizador segun espesor del rigidizador (viga izquierda)",
      "id": "section_6_7.weld_2_type_vs_stiffener_thickness_vgizq",
      "limit_symbol": "verification_only",
      "result": "NO_OK",
      "scope": "weld_2_vgizq",
      "status": "FAIL",
      "step": "1",
      "verification_text": "si t_pest_vgizq > 10.000 mm: tipo_w2_vgizq == cjp; dato faltante: t_pest_vgizq"
    },
    {
      "allowed_values": [
        "cjp",
        "pjp",
        "fillet"
      ],
      "calculated_symbol": "tipo_w6_col",
      "calculated_text": "cjp",
      "clause": "Section 6.7",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Tipo de soldadura #6 permitido",
      "id": "section_6_7.weld_6_type_allowed_col",
      "limit_symbol": "{cjp, pjp, fillet}",
      "result": "OK",
      "scope": "weld_6_col",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "fillet",
        "cjp"
      ],
      "calculated_symbol": "tipo_w5_col",
      "calculated_text": "cjp",
      "clause": "Section 6.3 (continuity plate weld detail)",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Continuity-plate weld type shall be explicitly declared with an allowed weld category",
      "id": "section_6_3.continuity_plate_weld_type_declared",
      "limit_symbol": "{fillet, cjp}",
      "result": "OK",
      "scope": "weld_5_col",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "fillet",
        "cjp"
      ],
      "calculated_symbol": "tipo_w5_col",
      "calculated_text": "cjp",
      "clause": "Section 6.3 (continuity plate weld detail)",
      "comparison": "conditional_allowed_set",
      "comparison_text": "in_if",
      "condition_applies": false,
      "description": "Tamano minimo de soldadura #5 cuando tipo_w5_col es fillet",
      "governing_condition": "cjp_always_permitted",
      "id": "section_6_3.continuity_plate_weld_type_for_thin_plate",
      "limit_symbol": "{fillet, cjp}; si fillet => w_w5_col >= 0.75*t_pc_col",
      "required_weld_size": {
        "unit": "mm",
        "value": 11.925
      },
      "result": "OK",
      "scope": "weld_5_col",
      "status": "PASS",
      "step": "1",
      "thickness": {
        "unit": "mm",
        "value": 15.9
      },
      "weld_size": null
    },
    {
      "allowed_values": [
        "pretensioned",
        "snug_tight"
      ],
      "calculated_symbol": "tight_bolt_vgder",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt tightening type must be one recognized category (right beam)",
      "id": "section_4_1.bolt_tightening_type_valid_der",
      "limit_symbol": "{pretensioned, snug_tight}",
      "result": "OK",
      "scope": "bolts_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tight_bolt_vgder",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "equals",
      "comparison_text": "==",
      "description": "Bolts shall be pretensioned unless a specific connection permits otherwise (right beam)",
      "expected_text": "pretensioned",
      "id": "section_4_1.bolt_tightening_required_pretensioned_der",
      "limit_symbol": "pretensioned",
      "result": "OK",
      "scope": "bolts_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "ASTM F3125/F3125M",
        "ASTM A325",
        "ASTM A325M",
        "ASTM A490",
        "ASTM A490M",
        "ASTM F1852",
        "ASTM F2280"
      ],
      "calculated_symbol": "std_bolt_vgder",
      "calculated_text": "ASTM A490",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt fabrication standard must be an allowed high-strength ASTM designation (right beam)",
      "id": "section_4_1.bolt_fabrication_standard_permitted_der",
      "limit_symbol": "{ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}",
      "result": "OK",
      "scope": "bolts_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "pretensioned",
        "snug_tight"
      ],
      "calculated_symbol": "tight_bolt_vgizq",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt tightening type must be one recognized category (left beam)",
      "id": "section_4_1.bolt_tightening_type_valid_izq",
      "limit_symbol": "{pretensioned, snug_tight}",
      "result": "OK",
      "scope": "bolts_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated_symbol": "tight_bolt_vgizq",
      "calculated_text": "pretensioned",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "equals",
      "comparison_text": "==",
      "description": "Bolts shall be pretensioned unless a specific connection permits otherwise (left beam)",
      "expected_text": "pretensioned",
      "id": "section_4_1.bolt_tightening_required_pretensioned_izq",
      "limit_symbol": "pretensioned",
      "result": "OK",
      "scope": "bolts_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "allowed_values": [
        "ASTM F3125/F3125M",
        "ASTM A325",
        "ASTM A325M",
        "ASTM A490",
        "ASTM A490M",
        "ASTM F1852",
        "ASTM F2280"
      ],
      "calculated_symbol": "std_bolt_vgizq",
      "calculated_text": "ASTM A490",
      "clause": "Section 4.1 FASTENER ASSEMBLIES",
      "comparison": "in_set",
      "comparison_text": "in",
      "description": "Bolt fabrication standard must be an allowed high-strength ASTM designation (left beam)",
      "id": "section_4_1.bolt_fabrication_standard_permitted_izq",
      "limit_symbol": "{ASTM F3125/F3125M, ASTM A325, ASTM A325M, ASTM A490, ASTM A490M, ASTM F1852, ASTM F2280}",
      "result": "OK",
      "scope": "bolts_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Edge distance at de (right beam)",
      "id": "table_6_1.edge_de_ge_emin_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 21.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Maximum edge distance at de (right beam)",
      "id": "table_6_1.edge_de_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 90.0
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside bolt-row distance minimum (right beam)",
      "id": "table_6_1.edge_pfo_ge_pfo_min_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfo_pe_vgder_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside bolt-row distance maximum (right beam)",
      "id": "table_6_1.edge_pfo_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfo_pe_vgder_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside adjusted edge distance minimum (right beam)",
      "id": "table_6_1.edge_pso_ge_emin_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.600000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgder",
      "clause": "AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside adjusted edge distance maximum (right beam)",
      "id": "table_6_1.edge_pso_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 99.30000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Inside bolt-row distance minimum (right beam)",
      "id": "table_6_1.edge_pfi_ge_pfi_min_der",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfi_pe_vgder_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Inside bolt-row distance maximum (right beam)",
      "id": "table_6_1.edge_pfi_le_emax_der",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfi_pe_vgder_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 228.0
      },
      "calculated_symbol": "bf_vgder",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Beam flange width limits (right beam)",
      "id": "table_6_1.bbf.range_der",
      "limit_symbol": "[bf_vgder_min, bf_vgder_max]",
      "margin": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 75.60000000000002
      },
      "maximum": {
        "unit": "mm",
        "value": 234.95
      },
      "minimum": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 607.0
      },
      "calculated_symbol": "d_vgder",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Connecting beam depth limits (right beam)",
      "id": "table_6_1.d.range_der",
      "limit_symbol": "[d_vgder_min, d_vgder_max]",
      "margin": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 257.75
      },
      "maximum": {
        "unit": "mm",
        "value": 609.5999999999999
      },
      "minimum": {
        "unit": "mm",
        "value": 349.25
      },
      "result": "OK",
      "scope": "beam_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 25.4
      },
      "calculated_symbol": "tpe_vgder",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "End-plate thickness limits (right beam)",
      "id": "table_6_1.tp.range_der",
      "limit_symbol": "[tpe_vgder_min, tpe_vgder_max]",
      "margin": {
        "unit": "mm",
        "value": 12.7
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 31.75
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 12.7
      },
      "maximum": {
        "unit": "mm",
        "value": 57.15
      },
      "minimum": {
        "unit": "mm",
        "value": 12.7
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgder",
      "clause": "Table 6.1 + AISC 360 Table J3.3 (compute_minimum_bolt_spacing_j33)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal bolt spacing minimum (right beam)",
      "id": "table_6_1.g.ge_min_der",
      "limit": {
        "unit": "mm",
        "value": 101.6
      },
      "limit_symbol": "max(g_b_vgder_min, 3db_j33)",
      "margin": {
        "unit": "mm",
        "value": 50.80000000000001
      },
      "result": "OK",
      "scope": "end_plate_der",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgder",
      "clause": "Table 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Horizontal bolt spacing maximum (right beam)",
      "id": "table_6_1.g.le_max_der",
      "limit": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "limit_symbol": "min(g_b_vgder_max, smax_j36)",
      "margin": {
        "unit": "mm",
        "value": -2.842170943040401e-14
      },
      "result": "NO_OK",
      "scope": "end_plate_der",
      "status": "FAIL",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Edge distance at de (left beam)",
      "id": "table_6_1.edge_de_ge_emin_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 21.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 60.0
      },
      "calculated_symbol": "de_pe_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Maximum edge distance at de (left beam)",
      "id": "table_6_1.edge_de_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 90.0
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside bolt-row distance minimum (left beam)",
      "id": "table_6_1.edge_pfo_ge_pfo_min_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfo_pe_vgizq_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfo_pe_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside bolt-row distance maximum (left beam)",
      "id": "table_6_1.edge_pfo_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfo_pe_vgizq_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Outside adjusted edge distance minimum (left beam)",
      "id": "table_6_1.edge_pso_ge_emin_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "emin",
      "margin": {
        "unit": "mm",
        "value": 12.600000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.699999999999996
      },
      "calculated_symbol": "pso_pe_vgizq",
      "clause": "AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Outside adjusted edge distance maximum (left beam)",
      "id": "table_6_1.edge_pso_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 150.0
      },
      "limit_symbol": "emax_j36",
      "margin": {
        "unit": "mm",
        "value": 99.30000000000001
      },
      "result": "OK",
      "scope": "column",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.4",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Inside bolt-row distance minimum (left beam)",
      "id": "table_6_1.edge_pfi_ge_pfi_min_izq",
      "limit": {
        "unit": "mm",
        "value": 38.099999999999994
      },
      "limit_symbol": "max(pfi_pe_vgizq_min, emin)",
      "margin": {
        "unit": "mm",
        "value": 11.900000000000006
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 50.0
      },
      "calculated_symbol": "pfi_pe_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Inside bolt-row distance maximum (left beam)",
      "id": "table_6_1.edge_pfi_le_emax_izq",
      "limit": {
        "unit": "mm",
        "value": 114.3
      },
      "limit_symbol": "min(pfi_pe_vgizq_max, emax_j36)",
      "margin": {
        "unit": "mm",
        "value": 64.3
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 228.0
      },
      "calculated_symbol": "bf_vgizq",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Beam flange width limits (left beam)",
      "id": "table_6_1.bbf.range_izq",
      "limit_symbol": "[bf_vgizq_min, bf_vgizq_max]",
      "margin": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 6.949999999999989
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 75.60000000000002
      },
      "maximum": {
        "unit": "mm",
        "value": 234.95
      },
      "minimum": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 607.0
      },
      "calculated_symbol": "d_vgizq",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "Connecting beam depth limits (left beam)",
      "id": "table_6_1.d.range_izq",
      "limit_symbol": "[d_vgizq_min, d_vgizq_max]",
      "margin": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 2.599999999999909
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 257.75
      },
      "maximum": {
        "unit": "mm",
        "value": 609.5999999999999
      },
      "minimum": {
        "unit": "mm",
        "value": 349.25
      },
      "result": "OK",
      "scope": "beam_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 25.4
      },
      "calculated_symbol": "tpe_vgizq",
      "clause": "Table 6.1",
      "comparison": "range",
      "comparison_text": "in",
      "description": "End-plate thickness limits (left beam)",
      "id": "table_6_1.tp.range_izq",
      "limit_symbol": "[tpe_vgizq_min, tpe_vgizq_max]",
      "margin": {
        "unit": "mm",
        "value": 12.7
      },
      "margin_to_max": {
        "unit": "mm",
        "value": 31.75
      },
      "margin_to_min": {
        "unit": "mm",
        "value": 12.7
      },
      "maximum": {
        "unit": "mm",
        "value": 57.15
      },
      "minimum": {
        "unit": "mm",
        "value": 12.7
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgizq",
      "clause": "Table 6.1 + AISC 360 Table J3.3 (compute_minimum_bolt_spacing_j33)",
      "comparison": "ge",
      "comparison_text": ">=",
      "description": "Horizontal bolt spacing minimum (left beam)",
      "id": "table_6_1.g.ge_min_izq",
      "limit": {
        "unit": "mm",
        "value": 101.6
      },
      "limit_symbol": "max(g_b_vgizq_min, 3db_j33)",
      "margin": {
        "unit": "mm",
        "value": 50.80000000000001
      },
      "result": "OK",
      "scope": "end_plate_izq",
      "status": "PASS",
      "step": "1"
    },
    {
      "calculated": {
        "unit": "mm",
        "value": 152.4
      },
      "calculated_symbol": "g_b_vgizq",
      "clause": "Table 6.1 + AISC 360-22 J3.6 (compute_maximum_bolt_spacing_j36)",
      "comparison": "le",
      "comparison_text": "<=",
      "description": "Horizontal bolt spacing maximum (left beam)",
      "id": "table_6_1.g.le_max_izq",
      "limit": {
        "unit": "mm",
        "value": 152.39999999999998
      },
      "limit_symbol": "min(g_b_vgizq_max, smax_j36)",
      "margin": {
        "unit": "mm",
        "value": -2.842170943040401e-14
      },
      "result": "NO_OK",
      "scope": "end_plate_izq",
      "status": "FAIL",
      "step": "1"
    }
  ],
  "step_1_notes": [
    {
      "beam_connection_sides": "both_sides",
      "clause": "Section 2.3.4 (8)",
      "description": "Protected zone length measured from column face",
      "formula": "Lpz_vgder = min(d_vgder, 3*bf_vgder); Lpz_vgizq = min(d_vgizq, 3*bf_vgizq)",
      "id": "section_2_3_4.protected_zone_length",
      "protected_zone_length": {
        "unit": "mm",
        "value": 607.0
      },
      "protected_zone_length_vgder": {
        "unit": "mm",
        "value": 607.0
      },
      "protected_zone_length_vgizq": {
        "unit": "mm",
        "value": 607.0
      },
      "scope": "beam",
      "step": "1"
    },
    {
      "clause": "Section 6.3 (2)",
      "description": "End-plate connection location on column",
      "id": "section_6_3.end_plate_connection_location",
      "requirement": "La placa de extremo debe conectarse al ala de la columna.",
      "scope": "column",
      "step": "1"
    },
    {
      "clause": "Section 6.3",
      "description": "Altura derivada de placa de extremo",
      "formula": "Hpe_vgder = d_vgder + 2*pfo_pe_vgder + 2*de_pe_vgder",
      "hpe_vgder": {
        "unit": "mm",
        "value": 827.0
      },
      "id": "section_6_3.end_plate_height_derived",
      "scope": "end_plate_der",
      "step": "1"
    },
    {
      "clause": "Section 6.3 + AISC 360-22 Table J3.3",
      "description": "Geometria end-plate de viga a derecha",
      "dh_vgder": {
        "unit": "mm",
        "value": 31.75
      },
      "formula": "h1=d-0.5tf+pfo; h2=d-1.5tf-pfi; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in",
      "h1_vgder": {
        "unit": "mm",
        "value": 648.35
      },
      "h2_vgder": {
        "unit": "mm",
        "value": 531.05
      },
      "h3_vgder": null,
      "h4_vgder": null,
      "id": "section_6_3.end_plate_geometry_vgder_note",
      "requirement": "h1_vgder, h2_vgder y dh_vgder para trazabilidad geometrica",
      "scope": "end_plate_der",
      "step": "1"
    },
    {
      "clause": "Section 6.3",
      "description": "Altura derivada de placa de extremo",
      "formula": "Hpe_vgizq = d_vgizq + 2*pfo_pe_vgizq + 2*de_pe_vgizq",
      "hpe_vgizq": {
        "unit": "mm",
        "value": 827.0
      },
      "id": "section_6_3.end_plate_height_derived_izq",
      "scope": "end_plate_izq",
      "step": "1"
    },
    {
      "clause": "Section 6.3 + AISC 360-22 Table J3.3",
      "description": "Geometria end-plate de viga a izquierda",
      "dh_vgizq": {
        "unit": "mm",
        "value": 31.75
      },
      "formula": "h1=d-0.5tf+pfo; h2=d-1.5tf-pfi; dh=d+1/16 in (db<=7/8 in) else dh=d+1/8 in",
      "h1_vgizq": {
        "unit": "mm",
        "value": 648.35
      },
      "h2_vgizq": {
        "unit": "mm",
        "value": 531.05
      },
      "h3_vgizq": null,
      "h4_vgizq": null,
      "id": "section_6_3.end_plate_geometry_vgizq_note",
      "requirement": "h1_vgizq, h2_vgizq y dh_vgizq para trazabilidad geometrica",
      "scope": "end_plate_izq",
      "step": "1"
    },
    {
      "clause": "Section 6.3",
      "description": "Derived end-plate stiffener geometry and detailing edge requirement",
      "ed_pest_vgder": {
        "unit": "mm",
        "value": 25.0
      },
      "formula": "h_pest_vgder = pfo_pe_vgder + de_pe_vgder; L_pest_vgder = h_pest_vgder/tan(30 deg); Ed_pest_vgder = 25 mm",
      "h_pest_vgder": {
        "unit": "mm",
        "value": 110.0
      },
      "id": "section_6_3.end_plate_stiffener_geometry_note",
      "l_pest_vgder": {
        "unit": "mm",
        "value": 200.0
      },
      "scope": "end_plate_stiffener_der",
      "step": "1"
    },
    {
      "clause": "Section 6.3",
      "description": "Derived end-plate stiffener geometry and detailing edge requirement",
      "ed_pest_vgizq": {
        "unit": "mm",
        "value": 25.0
      },
      "formula": "h_pest_vgizq = pfo_pe_vgizq + de_pe_vgizq; L_pest_vgizq = h_pest_vgizq/tan(30 deg); Ed_pest_vgizq = 25 mm",
      "h_pest_vgizq": {
        "unit": "mm",
        "value": 110.0
      },
      "id": "section_6_3.end_plate_stiffener_geometry_vgizq_note",
      "l_pest_vgizq": {
        "unit": "mm",
        "value": 200.0
      },
      "scope": "end_plate_stiffener_izq",
      "step": "1"
    },
    {
      "clause": "Section 6.7",
      "description": "Secuencia de soldadura para conexiones end-plate rigidizadas",
      "id": "section_6_7.stiffened_end_plate_weld_sequence_note",
      "requirement": "Para conexiones end-plate rigidizadas, la soldadura entre el ala de la viga y la placa de extremo debe ejecutarse antes de instalar el rigidizador.",
      "scope": "welds",
      "step": "1"
    },
    {
      "clause": "Section 6.7",
      "description": "Excepcion de respaldo en la raiz cerca del alma de la viga",
      "id": "section_6_7.flange_root_backing_exception_note",
      "requirement": "No se requiere respaldo en la raiz del ala, directamente por encima y por debajo del alma de la viga, en una longitud igual a 1.5k1. En esa ubicacion se permite una soldadura de ranura PJP de profundidad completa.",
      "scope": "welds",
      "step": "1"
    },
    {
      "clause": "Section 4.2",
      "description": "Installation requirements for bolted assemblies (right beam)",
      "id": "section_4_2.installation_requirements_der",
      "requirement": "Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.",
      "scope": "bolts_der",
      "step": "1"
    },
    {
      "clause": "Section 4.3",
      "description": "Quality control and quality assurance for bolted assemblies (right beam)",
      "id": "section_4_3.quality_control_assurance_der",
      "requirement": "El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.",
      "scope": "bolts_der",
      "step": "1"
    },
    {
      "clause": "Section 4.2",
      "description": "Installation requirements for bolted assemblies (left beam)",
      "id": "section_4_2.installation_requirements_izq",
      "requirement": "Los requisitos de instalacion deben cumplir con las AISC Seismic Provisions y con la especificacion RCSC, salvo que este estandar indique lo contrario.",
      "scope": "bolts_izq",
      "step": "1"
    },
    {
      "clause": "Section 4.3",
      "description": "Quality control and quality assurance for bolted assemblies (left beam)",
      "id": "section_4_3.quality_control_assurance_izq",
      "requirement": "El control de calidad y el aseguramiento de calidad deben cumplir con las AISC Seismic Provisions.",
      "scope": "bolts_izq",
      "step": "1"
    }
  ]
}
```

### Unidades

```json
{
  "bcf": "mm",
  "bf": "mm",
  "bp": "mm",
  "db": "mm",
  "de": "mm",
  "g": "mm",
  "pb": "mm",
  "pfi": "mm",
  "pfo": "mm"
}
```

## Check 2 - bueep_4e Step 2 probable maximum moment at plastic hinge

- Regla: `AISC358.06.7.bueep_4e.step2_probable_moment_plastic_hinge`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 2 + Eq. (2.4-1) and Eq. (2.4-2)`
- Estado: `OK`
- Demanda: `1431474 kN-mm`
- Capacidad: `1431474 kN-mm`
- Capacidad final: `1431474 kN-mm`
- DCR: `1`
- Ecuacion: `Mpr = Cpr * Ry * Fy * Ze`

### Inputs

```json
{
  "beam_fy": {
    "unit": "MPa",
    "value": 345.0
  },
  "beam_steel_type": "ASTM A572 Gr 50",
  "member_ductility_demand_vgder": "high",
  "member_ductility_demand_vgizq": "high",
  "ry": 1.1,
  "stated_mpr": null,
  "ze_input": null,
  "ze_source": "sections_catalog_zx_by_side",
  "ze_vgder": {
    "unit": "mm3",
    "value": 3280000.0
  },
  "ze_vgizq": {
    "unit": "mm3",
    "value": 3280000.0
  }
}
```

### Intermedios

```json
{
  "cpr_der": 1.15,
  "cpr_izq": 1.15,
  "governing_side_mpr": "der",
  "member_ductility_demand_beam_der": "high",
  "member_ductility_demand_beam_izq": "high",
  "mpr_der": 1431473.9999999998,
  "mpr_izq": 1431473.9999999998
}
```

### Unidades

```json
{
  "mpr_computed": "kN-mm",
  "mpr_stated": "kN-mm"
}
```

## Check 3 - bueep_4e Step 3 plastic hinge distance from column face

- Regla: `AISC358.06.7.bueep_4e.step3_plastic_hinge_distance`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 3 + Eq. (6.7-1) and Eq. (6.7-2)`
- Estado: `OK`
- Demanda: `303.5 mm`
- Capacidad: `303.5 mm`
- Capacidad final: `303.5 mm`
- DCR: `1`
- Ecuacion: `Sh_vglado = min(d_vglado/2, 3*bf_vglado) [4E] o Sh_vglado = L_pest_vglado + tpe_vglado [4ES/8ES]`

### Inputs

```json
{
  "bf_vgder": {
    "unit": "mm",
    "value": 228.0
  },
  "bf_vgizq": {
    "unit": "mm",
    "value": 228.0
  },
  "connection_type": "bueep_4e",
  "d_vgder": {
    "unit": "mm",
    "value": 607.0
  },
  "d_vgizq": {
    "unit": "mm",
    "value": 607.0
  },
  "governing_side_sh": "der"
}
```

### Intermedios

```json
{
  "sh_der": 303.5,
  "sh_izq": 303.5
}
```

### Unidades

```json
{
  "sh": "mm"
}
```

## Check 4 - bueep_4e Step 4 shear force at plastic hinge

- Regla: `AISC358.06.7.bueep_4e.step4_shear_at_plastic_hinge`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 4 + Eq. (2.4-3)`
- Estado: `OK`
- Demanda: `514.125701 kN`
- Capacidad: `514.125701 kN`
- Capacidad final: `514.125701 kN`
- DCR: `1`
- Ecuacion: `Vhmax = 2*Mpr/Lh + Vgravity; Vhmin = 2*Mpr/Lh - Vgravity (Eq. 2.4-3, side-specific der/izq)`

### Inputs

```json
{
  "beam_connection_sides": "both_sides",
  "governing_side_vhmax": "der",
  "lh_der": {
    "unit": "mm",
    "value": 6096.0
  },
  "lh_der_source": "geometry.beam_clear_span_length_der",
  "lh_izq": {
    "unit": "mm",
    "value": 6096.0
  },
  "lh_izq_source": "geometry.beam_clear_span_length_izq",
  "selected_vh_dermax_source": "step4_computed_vhmax_der",
  "selected_vh_izqmax_source": "step4_computed_vhmax_izq",
  "selected_vhmax_source": "step4_computed_vhmax_der (governing_side=der)",
  "stated_vh_dermax": null,
  "stated_vh_izqmax": null,
  "vgravity_between_hinges_der": {
    "unit": "kN",
    "value": 44.482
  },
  "vgravity_between_hinges_der_source": "loads.beam_right_vgravity",
  "vgravity_between_hinges_izq": {
    "unit": "kN",
    "value": 44.482
  },
  "vgravity_between_hinges_izq_source": "loads.beam_left_vgravity"
}
```

### Intermedios

```json
{
  "2mpr_over_lh_der": 469.6437007874015,
  "2mpr_over_lh_izq": 469.6437007874015,
  "mpr": 1431473.9999999998,
  "mpr_der": 1431473.9999999998,
  "mpr_izq": 1431473.9999999998,
  "vh_dermax": 514.1257007874015,
  "vh_dermax_adopted": 514.1257007874015,
  "vh_dermin": 425.1617007874015,
  "vh_izqmax": 514.1257007874015,
  "vh_izqmax_adopted": 514.1257007874015,
  "vh_izqmin": 425.1617007874015
}
```

### Unidades

```json
{
  "vhmax_governing": "kN",
  "vhmax_selected": "kN"
}
```

## Check 5 - bueep_4e Step 5 probable maximum moment at face of column

- Regla: `AISC358.06.7.bueep_4e.step5_probable_moment_face_column`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 5 + Eq. (2.4-4)`
- Estado: `OK`
- Demanda: `1587511.150189 kN-mm`
- Capacidad: `1587511.150189 kN-mm`
- Capacidad final: `1587511.150189 kN-mm`
- DCR: `1`
- Ecuacion: `Mfmax = Mpr + Vhmax*Sh; Mfmin = Mpr + Vhmin*Sh (Eq. 2.4-4, side-specific der/izq)`

### Inputs

```json
{
  "beam_connection_sides": "both_sides",
  "governing_side_mfmax": "der",
  "selected_mfmax_source": "loads.probable_moment_column_face (legacy)",
  "stated_mf_dermax": {
    "unit": "kN-mm",
    "value": 677908.974
  },
  "stated_mf_izqmax": null
}
```

### Intermedios

```json
{
  "mf_dermax": 1587511.1501889762,
  "mf_dermin": 1560510.5761889762,
  "mf_izqmax": 1587511.1501889762,
  "mf_izqmin": 1560510.5761889762,
  "mpr": 1431473.9999999998,
  "mpr_der": 1431473.9999999998,
  "mpr_izq": 1431473.9999999998,
  "sh": 303.5,
  "sh_der": 303.5,
  "sh_izq": 303.5,
  "vh_dermax": 514.1257007874015,
  "vh_dermin": 425.1617007874015,
  "vh_izqmax": 514.1257007874015,
  "vh_izqmin": 425.1617007874015
}
```

### Unidades

```json
{
  "mfmax_governing": "kN-mm",
  "mfmax_selected": "kN-mm"
}
```

## Check 6 - bueep_4e Step 21.5.1 column panel-zone web shear (WPZS)

- Regla: `AISC358.06.7.bueep_4e.step21_5_1_column_panel_zone_shear_wpzs_col`
- Documento: `AISC 360-22w`
- Clausula: `AISC 360-22w Section J10.6 + Eq. (J10-9) to Eq. (J10-12)`
- Estado: `NG`
- Demanda: `3116.165503 kN`
- Capacidad: `2376.5256 kN`
- Capacidad final: `2376.5256 kN`
- DCR: `1.311227`
- Ecuacion: `Rn1_wpz_v2_col = 0.60*Fy_col*d_col*tw_col; Rn2_wpz_v2_col = 0.60*Fy_col*d_col*(n_dp_col*t_dp_col); Rn_wpz_v2_col = min{Rn1_wpz_v2_col, Rn2_wpz_v2_col} (J10-9)`

### Inputs

```json
{
  "ag_col": {
    "unit": "mm2",
    "value": 33200.0
  },
  "alpha": 1.0,
  "alpha_pr_col": {
    "unit": "kN",
    "value": 0.0
  },
  "bcf_col": {
    "unit": "mm",
    "value": 290.0
  },
  "consideracion_deformacion_inelastica_zona_panel": false,
  "d_col": {
    "unit": "mm",
    "value": 508.0
  },
  "db_col": {
    "unit": "mm",
    "value": 607.0
  },
  "db_col_source_side": "der",
  "db_vgder": {
    "unit": "mm",
    "value": 607.0
  },
  "db_vgizq": {
    "unit": "mm",
    "value": 607.0
  },
  "eq_case_wpzs": "J10-9",
  "fy_col": {
    "unit": "MPa",
    "value": 345.0
  },
  "hb_col": {
    "unit": "mm",
    "value": 762.0
  },
  "ht_col": {
    "unit": "mm",
    "value": 762.0
  },
  "mbe_col_vgder_max": {
    "unit": "kN-mm",
    "value": 1718099.078188976
  },
  "mbe_col_vgder_min": {
    "unit": "kN-mm",
    "value": 1668501.648188976
  },
  "mbe_col_vgizq_max": {
    "unit": "kN-mm",
    "value": 1718099.078188976
  },
  "mbe_col_vgizq_min": {
    "unit": "kN-mm",
    "value": 1668501.648188976
  },
  "mf_vgder_max": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_vgder_min": {
    "unit": "kN-mm",
    "value": 1560510.5761889762
  },
  "mf_vgizq_max": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_vgizq_min": {
    "unit": "kN-mm",
    "value": 1560510.5761889762
  },
  "mpr_vgder": {
    "unit": "kN-mm",
    "value": 1431473.9999999998
  },
  "mpr_vgizq": {
    "unit": "kN-mm",
    "value": 1431473.9999999998
  },
  "n_dp_col": 1,
  "package_wpzs": "a",
  "phi_wpzs": 1.0,
  "pr_col": {
    "unit": "kN",
    "value": 0.0
  },
  "pu_col": {
    "unit": "kN",
    "value": 0.0
  },
  "py_col": {
    "unit": "kN",
    "value": 11454.0
  },
  "rn1_wpz_v2_col": {
    "unit": "kN",
    "value": 2376.5256
  },
  "rn2_wpz_v2_col": {
    "unit": "kN",
    "value": 2376.5256
  },
  "ru_wpzs_col": {
    "unit": "kN",
    "value": 3116.1655028279874
  },
  "sh_vgder": {
    "unit": "mm",
    "value": 303.5
  },
  "sh_vgizq": {
    "unit": "mm",
    "value": 303.5
  },
  "sum_mbe_col": {
    "unit": "kN-mm",
    "value": 3386600.726377952
  },
  "sum_mf_over_z_col": {
    "unit": "kN",
    "value": 5338.344457144229
  },
  "t_dp_col": {
    "unit": "mm",
    "value": 22.6
  },
  "t_dp_total_col": {
    "unit": "mm",
    "value": 22.6
  },
  "tcf_col": {
    "unit": "mm",
    "value": 40.4
  },
  "tf_vgder": {
    "unit": "mm",
    "value": 17.3
  },
  "tf_vgizq": {
    "unit": "mm",
    "value": 17.3
  },
  "tw_col": {
    "unit": "mm",
    "value": 22.6
  },
  "tw_wpz_effective_col": {
    "unit": "mm",
    "value": 22.6
  },
  "use_weld_7_col": false,
  "vc2_col": {
    "unit": "kN",
    "value": 2222.1789543162413
  },
  "vh_vgder_max": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgder_min": {
    "unit": "kN",
    "value": 425.1617007874015
  },
  "vh_vgizq_max": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgizq_min": {
    "unit": "kN",
    "value": 425.1617007874015
  }
}
```

### Intermedios

```json
{
  "alpha_pr_over_py": 0.0,
  "arm_center_col_vgder": 557.5,
  "arm_center_col_vgizq": 557.5,
  "eq_case_wpzs": "J10-9",
  "f_mf_vgder_max": 2692.0657116991283,
  "f_mf_vgder_min": 2646.278745445101,
  "f_mf_vgizq_max": 2692.0657116991283,
  "f_mf_vgizq_min": 2646.278745445101,
  "package_wpzs": "a",
  "panel_factor": 1.0,
  "rn_nominal_wpzs_col": 2376.5256,
  "ru_wpz_formula": "Ru_wpz_v2_col = sum_Mf_col/(db - tf) - Vc2_col",
  "sum_mbe_col_combo_1": 3386600.726377952,
  "sum_mbe_col_combo_2": 3386600.726377952,
  "sum_mbe_over_hb_plus_ht_formula": "Vc2_col = sum_Mbe_col/(hb_col + ht_col)",
  "sum_mf_over_z_col_combo_1": 5338.344457144229,
  "sum_mf_over_z_col_combo_2": 5338.344457144229,
  "z_vgder": 589.7,
  "z_vgizq": 589.7
}
```

### Factores de diseno

```json
{
  "alpha": 1.0,
  "phi_wpzs": 1.0
}
```

### Unidades

```json
{
  "capacity": "kN",
  "demand": "kN"
}
```

## Check 7 - bueep_4e Step 6.1 bolt tension rupture capacity (left)

- Regla: `AISC358.06.7.bueep_4e.step6_1_bolt_tension_rupture_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 6.1 + AISC 360-22 J3.7`
- Estado: `NG`
- Demanda: `673.016428 kN`
- Capacidad: `450.193761 kN`
- Capacidad final: `450.193761 kN`
- DCR: `1.494948`
- Ecuacion: `Ru_b_p+_vgizq = Mf_vgizq_critico/(2*(h1_pe_vgizq + h2_pe_vgizq)); phi*Rn_b_p+_vgizq = phi * Rn_b_p+_vgizq, Rn_b_p+_vgizq = A_b_vgizq * Fnt_b_vgizq, A_b_vgizq = pi*db^2/4 (AISC 360-22 J3.7)`

### Inputs

```json
{
  "bolt_diameter": {
    "unit": "mm",
    "value": 28.575
  },
  "bolt_fnt": {
    "unit": "MPa",
    "value": 780.0
  },
  "connection_type": "bueep_4e",
  "fnt_b_vgizq": {
    "unit": "MPa",
    "value": 780.0
  },
  "h1_pe_vgizq": {
    "unit": "mm",
    "value": 648.35
  },
  "h2_pe_vgizq": {
    "unit": "mm",
    "value": 531.05
  },
  "h3_pe_vgizq": null,
  "h4_pe_vgizq": null,
  "mf": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgizq_max, Mf_vgizq_min)",
  "mf_vgizq_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  }
}
```

### Intermedios

```json
{
  "a_b_vgizq": {
    "unit": "mm2",
    "value": 641.3016532327706
  },
  "bolt_area": 641.3016532327706,
  "nominal_tension_capacity_per_bolt": 500.2152895215611,
  "phi_rn_b_p_pos": 450.193760569405,
  "rnt_b": 500.2152895215611,
  "ru_b_p_pos": 673.0164279247821,
  "sum_h": 1179.4
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_b_p_pos": "kN",
  "ru_b_p_pos": "kN"
}
```

## Check 8 - bueep_4e Step 6.2 bolt shear rupture capacity (left)

- Regla: `AISC358.06.7.bueep_4e.step6_2_bolt_shear_rupture_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 6.2 + AISC 360-22 J3.7`
- Estado: `OK`
- Demanda: `128.531425 kN`
- Capacidad: `271.270599 kN`
- Capacidad final: `271.270599 kN`
- DCR: `0.473813`
- Ecuacion: `Ru_b_v2_vgizq = Vh_vgizq_critico/n_b_vgizq, phi*Rn_b_v2_vgizq = phi * Rn_b_v2_vgizq, Rn_b_v2_vgizq = A_b_vgizq * Fnv_b_vgizq, A_b_vgizq = pi*db^2/4, n_b_vgizq = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`

### Inputs

```json
{
  "bolt_diameter": {
    "unit": "mm",
    "value": 28.575
  },
  "bolt_fnv": {
    "unit": "MPa",
    "value": 470.0
  },
  "connection_type": "bueep_4e",
  "fnv_b_vgizq": {
    "unit": "MPa",
    "value": 470.0
  },
  "n_b_vgizq": 4,
  "thread_b_vgizq": "N",
  "vh_vgizq_critico": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgizq_critico_source": "max(Vh_vgizq_max, Vh_vgizq_min)"
}
```

### Intermedios

```json
{
  "a_b_vgizq": {
    "unit": "mm2",
    "value": 641.3016532327706
  },
  "bolt_area": 641.3016532327706,
  "nominal_shear_capacity_per_bolt": 301.41177701940217,
  "phi_rn_b_v2_vgizq": 271.270599317462,
  "rnv_b": 301.41177701940217,
  "ru_b_v2_vgizq": 128.53142519685036
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_b_v2_vgizq": "kN",
  "ru_b_v2_vgizq": "kN"
}
```

## Check 9 - bueep_4e Step 7.1.1 end-plate flexural yielding (left)

- Regla: `AISC358.06.7.bueep_4e.step7_1_1_end_plate_flexural_yielding_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 7.1.1 + Eq. (6.7-8)`
- Estado: `NG`
- Demanda: `1587511.150189 kN-mm`
- Capacidad: `1032227.56401 kN-mm`
- Capacidad final: `1032227.56401 kN-mm`
- DCR: `1.537947`
- Ecuacion: `Ru_pe_m3_vgizq = Mf_vgizq_critico; phi*Rn_pe_m3_vgizq = phi * tpe_vgizq^2 * Fyp_pe_vgizq * Yp_pe_vgizq (AISC 358-22 Eq. 6.7-8)`

### Inputs

```json
{
  "fyp_pe_vgizq": {
    "unit": "MPa",
    "value": 345.0
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgizq_max, Mf_vgizq_min)",
  "mf_vgizq_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "tpe_vgizq": {
    "unit": "mm",
    "value": 25.4
  },
  "yp_pe_vgizq": {
    "unit": "mm",
    "value": 4637.553403268875
  },
  "yp_pe_vgizq_case": "N/A",
  "yp_pe_vgizq_is_hardcoded": false,
  "yp_pe_vgizq_source": "derived_from_aisc358_tables_6_2_6_3_6_4",
  "yp_pe_vgizq_table": "AISC 358-22 Table 6.2"
}
```

### Intermedios

```json
{
  "case_reference": "N/A",
  "de": {
    "unit": "mm",
    "value": 60.0
  },
  "de_le_s": true,
  "design_moment": 1032227.5640102667,
  "formula": "Yp = bp/2*[h2*(1/pfi + 1/s) + h1*(1/pfo) - 1/2] + (2/g)*[h2*(pfi + s)]",
  "is_hardcoded": false,
  "nominal_moment": 1032227.5640102667,
  "pfi_effective": {
    "unit": "mm",
    "value": 50.0
  },
  "pfi_input": {
    "unit": "mm",
    "value": 50.0
  },
  "s": {
    "unit": "mm",
    "value": 98.17993685066212
  },
  "table_reference": "AISC 358-22 Table 6.2"
}
```

### Factores de diseno

```json
{
  "phi": 1.0
}
```

### Unidades

```json
{
  "phi_rn_pe_m3_vgizq": "kN-mm",
  "ru_pe_m3_vgizq": "kN-mm"
}
```

## Check 10 - bueep_4e Step 7.3.1 end-plate hole tearout (left)

- Regla: `AISC358.06.7.bueep_4e.step7_3_1_end_plate_hole_tearout_vgizq`
- Documento: `AISC 360-22`
- Clausula: `Chapter 6 / Section 7.3.1 + AISC 360-22 J3.11(a)`
- Estado: `OK`
- Demanda: `128.531425 kN`
- Capacidad: `1056.06342 kN`
- Capacidad final: `1056.06342 kN`
- DCR: `0.121708`
- Ecuacion: `lc_pe_vgizq = pfo_pe_vgizq + pfi_pe_vgizq + tf_vgizq - dh_pe_vgizq; Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 1.2 * lc_pe_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`

### Inputs

```json
{
  "dh_pe_vgizq": {
    "unit": "mm",
    "value": 31.75
  },
  "fup_pe_vgizq": {
    "unit": "MPa",
    "value": 450.0
  },
  "lc_pe_vgizq": {
    "unit": "mm",
    "value": 85.55
  },
  "n_b_vgizq": 4,
  "pb_pe_vgizq": {
    "unit": "mm",
    "value": 0.0
  },
  "pfi_pe_vgizq": {
    "unit": "mm",
    "value": 50.0
  },
  "pfo_pe_vgizq": {
    "unit": "mm",
    "value": 50.0
  },
  "tf_vgizq": {
    "unit": "mm",
    "value": 17.3
  },
  "tpe_vgizq": {
    "unit": "mm",
    "value": 25.4
  },
  "vh_vgizq_critico": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgizq_critico_source": "max(Vh_vgizq_max, Vh_vgizq_min)"
}
```

### Intermedios

```json
{
  "db": 28.575,
  "db_in": 1.125,
  "design_strength": 1056.0634200000002,
  "dh": 31.75,
  "hole_add_in": 0.125,
  "lc_1_pb_minus_dh": -31.75,
  "lc_2_pfo_plus_pfi_plus_tbf_minus_dh": 85.55,
  "lc_rule_selector": 2.0,
  "nominal_strength": 1173.4038,
  "ru_pe_v2_vgizq": 128.53142519685036,
  "table_case": "db>=1.125 in"
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_pe_v2_vgizq": "kN",
  "ru_pe_v2_vgizq": "kN"
}
```

## Check 11 - bueep_4e Step 7.3.2 end-plate hole bearing (left)

- Regla: `AISC358.06.7.bueep_4e.step7_3_2_end_plate_hole_bearing_vgizq`
- Documento: `AISC 360-22`
- Clausula: `Chapter 6 / Section 7.3.2 + AISC 360-22 J3.11(a)`
- Estado: `OK`
- Demanda: `128.531425 kN`
- Capacidad: `705.48246 kN`
- Capacidad final: `705.48246 kN`
- DCR: `0.182189`
- Ecuacion: `Ru_pe_v2_vgizq = Vh_vgizq_critico / n_b_vgizq; phi*Rn_pe_v2_vgizq = phi * 2.4 * d_b_vgizq * tpe_vgizq * Fup_pe_vgizq (AISC 360-22 J3.11a)`

### Inputs

```json
{
  "d_b_vgizq": {
    "unit": "mm",
    "value": 28.575
  },
  "fup_pe_vgizq": {
    "unit": "MPa",
    "value": 450.0
  },
  "n_b_vgizq": 4,
  "tpe_vgizq": {
    "unit": "mm",
    "value": 25.4
  },
  "vh_vgizq_critico": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgizq_critico_source": "max(Vh_vgizq_max, Vh_vgizq_min)"
}
```

### Intermedios

```json
{
  "design_strength": 705.48246,
  "nominal_strength": 783.8693999999999,
  "ru_pe_v2_vgizq": 128.53142519685036
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_pe_v2_vgizq": "kN",
  "ru_pe_v2_vgizq": "kN"
}
```

## Check 12 - bueep_4e Step 12.1.1 column flange local bending (LFB) (left)

- Regla: `AISC358.06.7.bueep_4e.step12_1_1_column_flange_local_bending_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-13)`
- Estado: `OK`
- Demanda: `0.000485 mm`
- Capacidad: `40.4 mm`
- Capacidad final: `40.4 mm`
- DCR: `0.000012`
- Ecuacion: `tcf >= 1.11 Mf / (phi_d * d * Fyc * Yc) (Eq. 6.7-13)`

### Inputs

```json
{
  "beam_depth": {
    "unit": "mm",
    "value": 607.0
  },
  "column_fy": {
    "unit": "MPa",
    "value": 345.0
  },
  "column_shape": "W18X175",
  "continuity_plate_enabled": true,
  "mf": {
    "unit": "kN-mm",
    "value": 677908.974
  },
  "mf_source": "loads.probable_moment_column_face (legacy)",
  "yc": {
    "unit": "mm",
    "value": 7411.607168175533
  },
  "yc_case_reference": "Case 1 (psi <= s)",
  "yc_formula": "Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]",
  "yc_is_hardcoded": false,
  "yc_table_reference": "AISC 358-22 Table 6.5"
}
```

### Intermedios

```json
{
  "bcf": {
    "unit": "mm",
    "value": 290.0
  },
  "c": {
    "unit": "mm",
    "value": 117.3
  },
  "case_reference": "Case 1 (psi <= s)",
  "continuity_plate_enabled": true,
  "continuity_plate_thickness": {
    "unit": "mm",
    "value": 15.9
  },
  "formula": "Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]",
  "g": {
    "unit": "mm",
    "value": 152.4
  },
  "h1": {
    "unit": "mm",
    "value": 648.35
  },
  "h2": {
    "unit": "mm",
    "value": 531.05
  },
  "h3": null,
  "h4": null,
  "is_hardcoded": false,
  "psi_computed": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "psi_effective": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "psi_input": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "pso": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "s": {
    "unit": "mm",
    "value": 105.11422358558332
  },
  "table_reference": "AISC 358-22 Table 6.5"
}
```

### Factores de diseno

```json
{
  "phi_d": 1.0
}
```

### Unidades

```json
{
  "tcf": "mm",
  "tcf_req": "mm"
}
```

## Check 13 - bueep_4e Step 13.1.1 column web local yielding (WLY) (left)

- Regla: `AISC358.06.7.bueep_4e.step13_1_1_column_web_local_yielding_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-17)`
- Estado: `OK`
- Demanda: `2692.065712 kN`
- Capacidad: `2893.4667 kN`
- Capacidad final: `2893.4667 kN`
- DCR: `0.930395`
- Ecuacion: `Ru_cf_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cf_v2_col_vgizq = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col`

### Inputs

```json
{
  "column_fy": {
    "unit": "MPa",
    "value": 345.0
  },
  "column_shape": "W18X175",
  "ct_col": 1.0,
  "d_col": {
    "unit": "mm",
    "value": 508.0
  },
  "d_vgizq": {
    "unit": "mm",
    "value": 607.0
  },
  "ductility_vgizq": "high",
  "fy_col": {
    "unit": "MPa",
    "value": 345.0
  },
  "kc_col": {
    "unit": "mm",
    "value": 50.5
  },
  "kc_from_sections_kdes": {
    "unit": "mm",
    "value": 50.5
  },
  "lb": {
    "unit": "mm",
    "value": 68.1
  },
  "lb_col": {
    "unit": "mm",
    "value": 68.1
  },
  "lb_col_formula": "lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq",
  "mf_vgizq_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "nl_w4_vgizq": 2,
  "ru_cf_v2_col_vgizq": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cf_v2_col_vgizq_adoptado": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cf_v2_col_vgizq_base": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cf_v2_col_vgizq_source": "continuity_plate_enabled => Ru_adoptado = min(Ru_base, phi*Rn_cf_v2_col_vgizq)",
  "st_col": {
    "unit": "mm",
    "value": 762.0
  },
  "t_w4_1_vgizq": {
    "unit": "mm",
    "value": 0.0
  },
  "tf_vgizq": {
    "unit": "mm",
    "value": 17.3
  },
  "total_weld_thickness_w4_formula": "2w = t_w4.1",
  "total_weld_thickness_w4_vgizq": {
    "unit": "mm",
    "value": 0.0
  },
  "tpe_vgizq": {
    "unit": "mm",
    "value": 25.4
  },
  "tw_col": {
    "unit": "mm",
    "value": 22.6
  }
}
```

### Intermedios

```json
{
  "continuity_plate_enabled": true,
  "phi_rn_cf_v2_col_vgizq": 2893.466700000001,
  "rn_nominal_cf_v2_col_vgizq": 2893.466700000001
}
```

### Factores de diseno

```json
{
  "phi_d": 1.0
}
```

### Unidades

```json
{
  "capacity": "kN",
  "ffu": "kN"
}
```

## Check 14 - bueep_4e Step 14.2.1 column web local crippling (WLC) (left)

- Regla: `AISC358.06.7.bueep_4e.step14_2_1_column_web_local_crippling_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Estado: `OK`
- Demanda: `2692.065712 kN`
- Capacidad: `3975.705548 kN`
- Capacidad final: `3975.705548 kN`
- DCR: `0.677129`
- Ecuacion: `Ru_cw_v2_col_vgizq = Mf_vgizq_critico/(d_vgizq - tf_vgizq); lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq; phi*Rn_cw_v2_col_vgizq = phi_wlc * Rn_eq(6.7-19/6.7-20/6.7-21); DCR_cw_v2_col_vgizq = Ru_cw_v2_col_vgizq / phi*Rn_cw_v2_col_vgizq`

### Inputs

```json
{
  "d_col": {
    "unit": "mm",
    "value": 508.0
  },
  "d_vgizq": {
    "unit": "mm",
    "value": 607.0
  },
  "ductility_vgizq": "high",
  "e_col": {
    "unit": "MPa",
    "value": 199947.965
  },
  "fy_col": {
    "unit": "MPa",
    "value": 345.0
  },
  "lb_col": {
    "unit": "mm",
    "value": 68.1
  },
  "lb_col_formula": "lb_col = tf_vgizq + 2w_w4_vgizq + 2*tpe_vgizq",
  "mf_vgizq_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "nl_w4_vgizq": 2,
  "ru_cw_v2_col_vgizq_adoptado": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cw_v2_col_vgizq_base": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cw_v2_col_vgizq_source": "continuity_plate_enabled => Ru_adoptado = min(Ru_base, phi*Rn_cw_v2_col_vgizq)",
  "st_col": {
    "unit": "mm",
    "value": 762.0
  },
  "t_w4_1_vgizq": {
    "unit": "mm",
    "value": 0.0
  },
  "tf_col": {
    "unit": "mm",
    "value": 40.4
  },
  "tf_vgizq": {
    "unit": "mm",
    "value": 17.3
  },
  "total_weld_thickness_w4_formula": "2w = t_w4.1",
  "total_weld_thickness_w4_vgizq": {
    "unit": "mm",
    "value": 0.0
  },
  "tpe_vgizq": {
    "unit": "mm",
    "value": 25.4
  },
  "tw_col": {
    "unit": "mm",
    "value": 22.6
  }
}
```

### Intermedios

```json
{
  "case": "eq_6_7_19",
  "continuity_plate_enabled": true,
  "phi": 0.75,
  "phi_rn_cf_v2_col_vgizq_eq1": 3975.705547631561,
  "rn_nominal": 5300.9407301754145,
  "rn_nominal_cf_v2_col_vgizq_eq1": 5300.9407301754145
}
```

### Factores de diseno

```json
{
  "phi_wlc": 0.75
}
```

### Unidades

```json
{
  "capacity": "kN",
  "ffu": "kN"
}
```

## Check 15 - bueep_4e Step 14.2.2 column web local buckling (WCB) (left)

- Regla: `AISC358.06.7.bueep_4e.step14_2_2_column_web_local_buckling_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-18)`
- Estado: `ERROR`
- Demanda: `n/a`
- Capacidad: `n/a`
- Capacidad final: `n/a`
- DCR: `n/a`
- Ecuacion: `No aplica: Faltan datos para evaluar la condicion de aplicabilidad de WCB: loads.Mu3_vgizq, loads.Mu3_vgder`
- Notas: `No aplica`
- Errores:
  - `NOT_IMPLEMENTED` No aplica

### Inputs

```json
{
  "missing_fields": [
    "loads.Mu3_vgizq",
    "loads.Mu3_vgder"
  ]
}
```

## Check 16 - bueep_4e Step 11.1.1 beam web-to-end-plate weld tension rupture (left)

- Regla: `AISC358.06.7.bueep_4e.step11_1_1_beam_web_end_plate_weld_tension_rupture_vgizq`
- Documento: `AISC 360-22`
- Clausula: `Chapter 6 / Section 6.7.1 + AISC 360-22 J2.4`
- Estado: `OK`
- Demanda: `0 ratio`
- Capacidad: `1 ratio`
- Capacidad final: `1 ratio`
- DCR: `0`
- Ecuacion: `CJP => cumple; Ru_w3_p+_vgizq = Fy_vgizq * tw_vgizq * hwef_w3_vgizq, hwef_w3_vgizq = pfi_pe_vgizq + pb_pe_vgizq + 150 mm`

### Inputs

```json
{
  "fy_vgizq": {
    "unit": "MPa",
    "value": 345.0
  },
  "hwef_w3_vgizq": {
    "unit": "mm",
    "value": 200.0
  },
  "ru_w3_p_pos_vgizq": {
    "unit": "kN",
    "value": 772.7999999999998
  },
  "tipo_w3_vgizq": "CJP",
  "tw_vgizq": {
    "unit": "mm",
    "value": 11.2
  }
}
```

### Factores de diseno

```json
{
  "phi": 0.75
}
```

### Unidades

```json
{
  "dcr": "ratio"
}
```

## Check 17 - bueep_4e Step 7.2.1 end-plate shear yielding (left)

- Regla: `AISC358.06.7.bueep_4e.step7_2_1_end_plate_shear_yielding_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.1 + Eq. (6.7-10)`
- Estado: `NG`
- Demanda: `1346.032856 kN`
- Capacidad: `1330.2234 kN`
- Capacidad final: `1330.2234 kN`
- DCR: `1.011885`
- Ecuacion: `Ru_pe_v1_vgizq = Mf_vgizq_critico / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v1_vgizq = phi * 0.6 * Fyp_pe_vgizq * bpe_vgizq * tpe_vgizq (AISC 358-22 Eq. 6.7-10)`

### Inputs

```json
{
  "bpe_vgizq": {
    "unit": "mm",
    "value": 253.0
  },
  "d_vgizq": {
    "unit": "mm",
    "value": 607.0
  },
  "fyp_pe_vgizq": {
    "unit": "MPa",
    "value": 345.0
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgizq_max, Mf_vgizq_min)",
  "mf_vgizq_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "tf_vgizq": {
    "unit": "mm",
    "value": 17.3
  },
  "tpe_vgizq": {
    "unit": "mm",
    "value": 25.4
  }
}
```

### Intermedios

```json
{
  "phi_rn_pe_v1_vgizq": 1330.2233999999999,
  "ru_pe_v1_vgizq": 1330.2233999999999,
  "z_vgizq": 589.7
}
```

### Factores de diseno

```json
{
  "phi": 1.0
}
```

### Unidades

```json
{
  "phi_rn_pe_v1_vgizq": "kN",
  "ru_pe_v1_vgizq": "kN"
}
```

## Check 18 - bueep_4e Step 7.2.2 end-plate shear rupture (left)

- Regla: `AISC358.06.7.bueep_4e.step7_2_2_end_plate_shear_rupture_vgizq`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.2 + Eq. (6.7-12)`
- Estado: `NG`
- Demanda: `1346.032856 kN`
- Capacidad: `1149.88086 kN`
- Capacidad final: `1149.88086 kN`
- DCR: `1.170585`
- Ecuacion: `Rn_pe_v2_vgizq = Ru_pe_m3_vgizq / (2*(d_vgizq - tf_vgizq)); phi*Rn_pe_v2_vgizq = phi * 0.6 * Fup_pe_vgizq * tpe_vgizq * (bpe_vgizq - 2*(dh_pe_vgizq + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`

### Inputs

```json
{
  "bpe_vgizq": {
    "unit": "mm",
    "value": 253.0
  },
  "d_vgizq": {
    "unit": "mm",
    "value": 607.0
  },
  "db": {
    "unit": "mm",
    "value": 28.575
  },
  "dh_pe_vgizq": {
    "unit": "mm",
    "value": 31.75
  },
  "fup_pe_vgizq": {
    "unit": "MPa",
    "value": 450.0
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgizq_max, Mf_vgizq_min)",
  "ru_pe_m3_vgizq": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "tf_vgizq": {
    "unit": "mm",
    "value": 17.3
  },
  "tpe_vgizq": {
    "unit": "mm",
    "value": 25.4
  }
}
```

### Intermedios

```json
{
  "db_in": 1.125,
  "design_shear": 1149.8808600000002,
  "edge_allowance": 1.6,
  "hole_add_in": 0.125,
  "net_width": 186.3,
  "nominal_shear": 1277.6454,
  "phi_n": 0.9,
  "table_case": "db>=1.125 in",
  "z_vgizq": 589.7
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_pe_v2_vgizq": "kN",
  "rn_pe_v2_vgizq": "kN"
}
```

## Check 19 - bueep_4e Step 6.1 bolt tension rupture capacity (right)

- Regla: `AISC358.06.7.bueep_4e.step6_1_bolt_tension_rupture_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 6.1 + AISC 360-22 J3.7`
- Estado: `NG`
- Demanda: `673.016428 kN`
- Capacidad: `450.193761 kN`
- Capacidad final: `450.193761 kN`
- DCR: `1.494948`
- Ecuacion: `Ru_b_p+_vgder = Mf_vgder_critico/(2*(h1_pe_vgder + h2_pe_vgder)); phi*Rn_b_p+_vgder = phi * Rn_b_p+_vgder, Rn_b_p+_vgder = A_b_vgder * Fnt_b_vgder, A_b_vgder = pi*db^2/4 (AISC 360-22 J3.7)`

### Inputs

```json
{
  "bolt_diameter": {
    "unit": "mm",
    "value": 28.575
  },
  "bolt_fnt": {
    "unit": "MPa",
    "value": 780.0
  },
  "connection_type": "bueep_4e",
  "fnt_b_vgder": {
    "unit": "MPa",
    "value": 780.0
  },
  "h1_pe_vgder": {
    "unit": "mm",
    "value": 648.35
  },
  "h2_pe_vgder": {
    "unit": "mm",
    "value": 531.05
  },
  "h3_pe_vgder": null,
  "h4_pe_vgder": null,
  "mf": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgder_max, Mf_vgder_min)",
  "mf_vgder_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  }
}
```

### Intermedios

```json
{
  "a_b_vgder": {
    "unit": "mm2",
    "value": 641.3016532327706
  },
  "bolt_area": 641.3016532327706,
  "nominal_tension_capacity_per_bolt": 500.2152895215611,
  "phi_rn_b_p_pos": 450.193760569405,
  "rnt_b": 500.2152895215611,
  "ru_b_p_pos": 673.0164279247821,
  "sum_h": 1179.4
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_b_p_pos": "kN",
  "ru_b_p_pos": "kN"
}
```

## Check 20 - bueep_4e Step 6.2 bolt shear rupture capacity (right)

- Regla: `AISC358.06.7.bueep_4e.step6_2_bolt_shear_rupture_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 6.2 + AISC 360-22 J3.7`
- Estado: `OK`
- Demanda: `128.531425 kN`
- Capacidad: `271.270599 kN`
- Capacidad final: `271.270599 kN`
- DCR: `0.473813`
- Ecuacion: `Ru_b_v2_vgder = Vh_vgder_critico/n_b_vgder, phi*Rn_b_v2_vgder = phi * Rn_b_v2_vgder, Rn_b_v2_vgder = A_b_vgder * Fnv_b_vgder, A_b_vgder = pi*db^2/4, n_b_vgder = 4 (4E/4ES) or 8 (8ES) (AISC 360-22 J3.7)`

### Inputs

```json
{
  "bolt_diameter": {
    "unit": "mm",
    "value": 28.575
  },
  "bolt_fnv": {
    "unit": "MPa",
    "value": 470.0
  },
  "connection_type": "bueep_4e",
  "fnv_b_vgder": {
    "unit": "MPa",
    "value": 470.0
  },
  "n_b_vgder": 4,
  "thread_b_vgder": "N",
  "vh_vgder_critico": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgder_critico_source": "max(Vh_vgder_max, Vh_vgder_min)"
}
```

### Intermedios

```json
{
  "a_b_vgder": {
    "unit": "mm2",
    "value": 641.3016532327706
  },
  "bolt_area": 641.3016532327706,
  "nominal_shear_capacity_per_bolt": 301.41177701940217,
  "phi_rn_b_v2_vgder": 271.270599317462,
  "rnv_b": 301.41177701940217,
  "ru_b_v2_vgder": 128.53142519685036
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_b_v2_vgizq": "kN",
  "ru_b_v2_vgizq": "kN"
}
```

## Check 21 - bueep_4e Step 7.1.1 end-plate flexural yielding (right)

- Regla: `AISC358.06.7.bueep_4e.step7_1_1_end_plate_flexural_yielding_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 7.1.1 + Eq. (6.7-8)`
- Estado: `NG`
- Demanda: `1587511.150189 kN-mm`
- Capacidad: `1032227.56401 kN-mm`
- Capacidad final: `1032227.56401 kN-mm`
- DCR: `1.537947`
- Ecuacion: `Ru_pe_m3_vgder = Mf_vgder_critico; phi*Rn_pe_m3_vgder = phi * tpe_vgder^2 * Fyp_pe_vgder * Yp_pe_vgder (AISC 358-22 Eq. 6.7-8)`

### Inputs

```json
{
  "fyp_pe_vgder": {
    "unit": "MPa",
    "value": 345.0
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgder_max, Mf_vgder_min)",
  "mf_vgder_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "tpe_vgder": {
    "unit": "mm",
    "value": 25.4
  },
  "yp_pe_vgder": {
    "unit": "mm",
    "value": 4637.553403268875
  },
  "yp_pe_vgder_case": "N/A",
  "yp_pe_vgder_is_hardcoded": false,
  "yp_pe_vgder_source": "derived_from_aisc358_tables_6_2_6_3_6_4",
  "yp_pe_vgder_table": "AISC 358-22 Table 6.2"
}
```

### Intermedios

```json
{
  "case_reference": "N/A",
  "de": {
    "unit": "mm",
    "value": 60.0
  },
  "de_le_s": true,
  "design_moment": 1032227.5640102667,
  "formula": "Yp = bp/2*[h2*(1/pfi + 1/s) + h1*(1/pfo) - 1/2] + (2/g)*[h2*(pfi + s)]",
  "is_hardcoded": false,
  "nominal_moment": 1032227.5640102667,
  "pfi_effective": {
    "unit": "mm",
    "value": 50.0
  },
  "pfi_input": {
    "unit": "mm",
    "value": 50.0
  },
  "s": {
    "unit": "mm",
    "value": 98.17993685066212
  },
  "table_reference": "AISC 358-22 Table 6.2"
}
```

### Factores de diseno

```json
{
  "phi": 1.0
}
```

### Unidades

```json
{
  "phi_rn_pe_m3_vgizq": "kN-mm",
  "ru_pe_m3_vgizq": "kN-mm"
}
```

## Check 22 - bueep_4e Step 7.3.1 end-plate hole tearout (right)

- Regla: `AISC358.06.7.bueep_4e.step7_3_1_end_plate_hole_tearout_vgder`
- Documento: `AISC 360-22`
- Clausula: `Chapter 6 / Section 7.3.1 + AISC 360-22 J3.11(a)`
- Estado: `OK`
- Demanda: `128.531425 kN`
- Capacidad: `1056.06342 kN`
- Capacidad final: `1056.06342 kN`
- DCR: `0.121708`
- Ecuacion: `lc_pe_vgder = pfo_pe_vgder + pfi_pe_vgder + tf_vgder - dh_pe_vgder; Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 1.2 * lc_pe_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`

### Inputs

```json
{
  "dh_pe_vgder": {
    "unit": "mm",
    "value": 31.75
  },
  "fup_pe_vgder": {
    "unit": "MPa",
    "value": 450.0
  },
  "lc_pe_vgder": {
    "unit": "mm",
    "value": 85.55
  },
  "n_b_vgder": 4,
  "pb_pe_vgder": {
    "unit": "mm",
    "value": 0.0
  },
  "pfi_pe_vgder": {
    "unit": "mm",
    "value": 50.0
  },
  "pfo_pe_vgder": {
    "unit": "mm",
    "value": 50.0
  },
  "tf_vgder": {
    "unit": "mm",
    "value": 17.3
  },
  "tpe_vgder": {
    "unit": "mm",
    "value": 25.4
  },
  "vh_vgder_critico": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgder_critico_source": "max(Vh_vgder_max, Vh_vgder_min)"
}
```

### Intermedios

```json
{
  "db": 28.575,
  "db_in": 1.125,
  "design_strength": 1056.0634200000002,
  "dh": 31.75,
  "hole_add_in": 0.125,
  "lc_1_pb_minus_dh": -31.75,
  "lc_2_pfo_plus_pfi_plus_tbf_minus_dh": 85.55,
  "lc_rule_selector": 2.0,
  "nominal_strength": 1173.4038,
  "ru_pe_v2_vgder": 128.53142519685036,
  "table_case": "db>=1.125 in"
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_pe_v2_vgizq": "kN",
  "ru_pe_v2_vgizq": "kN"
}
```

## Check 23 - bueep_4e Step 7.3.2 end-plate hole bearing (right)

- Regla: `AISC358.06.7.bueep_4e.step7_3_2_end_plate_hole_bearing_vgder`
- Documento: `AISC 360-22`
- Clausula: `Chapter 6 / Section 7.3.2 + AISC 360-22 J3.11(a)`
- Estado: `OK`
- Demanda: `128.531425 kN`
- Capacidad: `705.48246 kN`
- Capacidad final: `705.48246 kN`
- DCR: `0.182189`
- Ecuacion: `Ru_pe_v2_vgder = Vh_vgder_critico / n_b_vgder; phi*Rn_pe_v2_vgder = phi * 2.4 * d_b_vgder * tpe_vgder * Fup_pe_vgder (AISC 360-22 J3.11a)`

### Inputs

```json
{
  "d_b_vgder": {
    "unit": "mm",
    "value": 28.575
  },
  "fup_pe_vgder": {
    "unit": "MPa",
    "value": 450.0
  },
  "n_b_vgder": 4,
  "tpe_vgder": {
    "unit": "mm",
    "value": 25.4
  },
  "vh_vgder_critico": {
    "unit": "kN",
    "value": 514.1257007874015
  },
  "vh_vgder_critico_source": "max(Vh_vgder_max, Vh_vgder_min)"
}
```

### Intermedios

```json
{
  "design_strength": 705.48246,
  "nominal_strength": 783.8693999999999,
  "ru_pe_v2_vgder": 128.53142519685036
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_pe_v2_vgizq": "kN",
  "ru_pe_v2_vgizq": "kN"
}
```

## Check 24 - bueep_4e Step 12.1.1 column flange local bending (LFB) (right)

- Regla: `AISC358.06.7.bueep_4e.step12_1_1_column_flange_local_bending_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-13)`
- Estado: `OK`
- Demanda: `0.000485 mm`
- Capacidad: `40.4 mm`
- Capacidad final: `40.4 mm`
- DCR: `0.000012`
- Ecuacion: `tcf >= 1.11 Mf / (phi_d * d * Fyc * Yc) (Eq. 6.7-13)`

### Inputs

```json
{
  "beam_depth": {
    "unit": "mm",
    "value": 607.0
  },
  "column_fy": {
    "unit": "MPa",
    "value": 345.0
  },
  "column_shape": "W18X175",
  "continuity_plate_enabled": true,
  "mf": {
    "unit": "kN-mm",
    "value": 677908.974
  },
  "mf_source": "loads.probable_moment_column_face (legacy)",
  "yc": {
    "unit": "mm",
    "value": 7411.607168175533
  },
  "yc_case_reference": "Case 1 (psi <= s)",
  "yc_formula": "Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]",
  "yc_is_hardcoded": false,
  "yc_table_reference": "AISC 358-22 Table 6.5"
}
```

### Intermedios

```json
{
  "bcf": {
    "unit": "mm",
    "value": 290.0
  },
  "c": {
    "unit": "mm",
    "value": 117.3
  },
  "case_reference": "Case 1 (psi <= s)",
  "continuity_plate_enabled": true,
  "continuity_plate_thickness": {
    "unit": "mm",
    "value": 15.9
  },
  "formula": "Y_cs = bcf/2*[h2*(1/s + 1/psi) + h1*(1/s + 1/pso)] + (2/g)*[h2*(s + psi) + h1*(s + pso)]",
  "g": {
    "unit": "mm",
    "value": 152.4
  },
  "h1": {
    "unit": "mm",
    "value": 648.35
  },
  "h2": {
    "unit": "mm",
    "value": 531.05
  },
  "h3": null,
  "h4": null,
  "is_hardcoded": false,
  "psi_computed": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "psi_effective": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "psi_input": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "pso": {
    "unit": "mm",
    "value": 50.699999999999996
  },
  "s": {
    "unit": "mm",
    "value": 105.11422358558332
  },
  "table_reference": "AISC 358-22 Table 6.5"
}
```

### Factores de diseno

```json
{
  "phi_d": 1.0
}
```

### Unidades

```json
{
  "tcf": "mm",
  "tcf_req": "mm"
}
```

## Check 25 - bueep_4e Step 13.1.1 column web local yielding (WLY) (right)

- Regla: `AISC358.06.7.bueep_4e.step13_1_1_column_web_local_yielding_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-17)`
- Estado: `OK`
- Demanda: `2692.065712 kN`
- Capacidad: `2893.4667 kN`
- Capacidad final: `2893.4667 kN`
- DCR: `0.930395`
- Ecuacion: `Ru_cf_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cf_v2_col_vgder = phi_ductil * (6*Ct_col*kc_col + lb_col) * Fy_col * tw_col`

### Inputs

```json
{
  "column_fy": {
    "unit": "MPa",
    "value": 345.0
  },
  "column_shape": "W18X175",
  "ct_col": 1.0,
  "d_col": {
    "unit": "mm",
    "value": 508.0
  },
  "d_vgder": {
    "unit": "mm",
    "value": 607.0
  },
  "ductility_vgder": "high",
  "fy_col": {
    "unit": "MPa",
    "value": 345.0
  },
  "kc_col": {
    "unit": "mm",
    "value": 50.5
  },
  "kc_from_sections_kdes": {
    "unit": "mm",
    "value": 50.5
  },
  "lb": {
    "unit": "mm",
    "value": 68.1
  },
  "lb_col": {
    "unit": "mm",
    "value": 68.1
  },
  "lb_col_formula": "lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder",
  "mf_vgder_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "nl_w4_vgder": 2,
  "ru_cf_v2_col_vgder": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cf_v2_col_vgder_adoptado": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cf_v2_col_vgder_base": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cf_v2_col_vgder_source": "continuity_plate_enabled => Ru_adoptado = min(Ru_base, phi*Rn_cf_v2_col_vgder)",
  "st_col": {
    "unit": "mm",
    "value": 762.0
  },
  "t_w4_1_vgder": {
    "unit": "mm",
    "value": 0.0
  },
  "tf_vgder": {
    "unit": "mm",
    "value": 17.3
  },
  "total_weld_thickness_w4_formula": "2w = t_w4.1",
  "total_weld_thickness_w4_vgder": {
    "unit": "mm",
    "value": 0.0
  },
  "tpe_vgder": {
    "unit": "mm",
    "value": 25.4
  },
  "tw_col": {
    "unit": "mm",
    "value": 22.6
  }
}
```

### Intermedios

```json
{
  "continuity_plate_enabled": true,
  "phi_rn_cf_v2_col_vgder": 2893.466700000001,
  "rn_nominal_cf_v2_col_vgder": 2893.466700000001
}
```

### Factores de diseno

```json
{
  "phi_d": 1.0
}
```

### Unidades

```json
{
  "capacity": "kN",
  "ffu": "kN"
}
```

## Check 26 - bueep_4e Step 14.2.1 column web local crippling (WLC) (right)

- Regla: `AISC358.06.7.bueep_4e.step14_2_1_column_web_local_crippling_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)`
- Estado: `OK`
- Demanda: `2692.065712 kN`
- Capacidad: `3975.705548 kN`
- Capacidad final: `3975.705548 kN`
- DCR: `0.677129`
- Ecuacion: `Ru_cw_v2_col_vgder = Mf_vgder_critico/(d_vgder - tf_vgder); lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder; phi*Rn_cw_v2_col_vgder = phi_wlc * Rn_eq(6.7-19/6.7-20/6.7-21); DCR_cw_v2_col_vgder = Ru_cw_v2_col_vgder / phi*Rn_cw_v2_col_vgder`

### Inputs

```json
{
  "d_col": {
    "unit": "mm",
    "value": 508.0
  },
  "d_vgder": {
    "unit": "mm",
    "value": 607.0
  },
  "ductility_vgder": "high",
  "e_col": {
    "unit": "MPa",
    "value": 199947.965
  },
  "fy_col": {
    "unit": "MPa",
    "value": 345.0
  },
  "lb_col": {
    "unit": "mm",
    "value": 68.1
  },
  "lb_col_formula": "lb_col = tf_vgder + 2w_w4_vgder + 2*tpe_vgder",
  "mf_vgder_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "nl_w4_vgder": 2,
  "ru_cw_v2_col_vgder_adoptado": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cw_v2_col_vgder_base": {
    "unit": "kN",
    "value": 2692.0657116991283
  },
  "ru_cw_v2_col_vgder_source": "continuity_plate_enabled => Ru_adoptado = min(Ru_base, phi*Rn_cw_v2_col_vgder)",
  "st_col": {
    "unit": "mm",
    "value": 762.0
  },
  "t_w4_1_vgder": {
    "unit": "mm",
    "value": 0.0
  },
  "tf_col": {
    "unit": "mm",
    "value": 40.4
  },
  "tf_vgder": {
    "unit": "mm",
    "value": 17.3
  },
  "total_weld_thickness_w4_formula": "2w = t_w4.1",
  "total_weld_thickness_w4_vgder": {
    "unit": "mm",
    "value": 0.0
  },
  "tpe_vgder": {
    "unit": "mm",
    "value": 25.4
  },
  "tw_col": {
    "unit": "mm",
    "value": 22.6
  }
}
```

### Intermedios

```json
{
  "case": "eq_6_7_19",
  "continuity_plate_enabled": true,
  "phi": 0.75,
  "phi_rn_cf_v2_col_vgder_eq1": 3975.705547631561,
  "rn_nominal": 5300.9407301754145,
  "rn_nominal_cf_v2_col_vgder_eq1": 5300.9407301754145
}
```

### Factores de diseno

```json
{
  "phi_wlc": 0.75
}
```

### Unidades

```json
{
  "capacity": "kN",
  "ffu": "kN"
}
```

## Check 27 - bueep_4e Step 14.2.2 column web local buckling (WCB) (right)

- Regla: `AISC358.06.7.bueep_4e.step14_2_2_column_web_local_buckling_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.2 + Eq. (6.7-18)`
- Estado: `ERROR`
- Demanda: `n/a`
- Capacidad: `n/a`
- Capacidad final: `n/a`
- DCR: `n/a`
- Ecuacion: `No aplica: Faltan datos para evaluar la condicion de aplicabilidad de WCB: loads.Mu3_vgder, loads.Mu3_vgizq`
- Notas: `No aplica`
- Errores:
  - `NOT_IMPLEMENTED` No aplica

### Inputs

```json
{
  "missing_fields": [
    "loads.Mu3_vgder",
    "loads.Mu3_vgizq"
  ]
}
```

## Check 28 - bueep_4e Step 11.1.1 beam web-to-end-plate weld tension rupture (right)

- Regla: `AISC358.06.7.bueep_4e.step11_1_1_beam_web_end_plate_weld_tension_rupture_vgder`
- Documento: `AISC 360-22`
- Clausula: `Chapter 6 / Section 6.7.1 + AISC 360-22 J2.4`
- Estado: `OK`
- Demanda: `0 ratio`
- Capacidad: `1 ratio`
- Capacidad final: `1 ratio`
- DCR: `0`
- Ecuacion: `CJP => cumple; Ru_w3_p+_vgder = Fy_vgder * tw_vgder * hwef_w3_vgder, hwef_w3_vgder = pfi_pe_vgder + pb_pe_vgder + 150 mm`

### Inputs

```json
{
  "fy_vgder": {
    "unit": "MPa",
    "value": 345.0
  },
  "hwef_w3_vgder": {
    "unit": "mm",
    "value": 200.0
  },
  "ru_w3_p_pos_vgder": {
    "unit": "kN",
    "value": 772.7999999999998
  },
  "tipo_w3_vgder": "CJP",
  "tw_vgder": {
    "unit": "mm",
    "value": 11.2
  }
}
```

### Factores de diseno

```json
{
  "phi": 0.75
}
```

### Unidades

```json
{
  "dcr": "ratio"
}
```

## Check 29 - bueep_4e Step 7.2.1 end-plate shear yielding (right)

- Regla: `AISC358.06.7.bueep_4e.step7_2_1_end_plate_shear_yielding_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.1 + Eq. (6.7-10)`
- Estado: `NG`
- Demanda: `1346.032856 kN`
- Capacidad: `1330.2234 kN`
- Capacidad final: `1330.2234 kN`
- DCR: `1.011885`
- Ecuacion: `Ru_pe_v1_vgder = Mf_vgder_critico / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v1_vgder = phi * 0.6 * Fyp_pe_vgder * bpe_vgder * tpe_vgder (AISC 358-22 Eq. 6.7-10)`

### Inputs

```json
{
  "bpe_vgder": {
    "unit": "mm",
    "value": 253.0
  },
  "d_vgder": {
    "unit": "mm",
    "value": 607.0
  },
  "fyp_pe_vgder": {
    "unit": "MPa",
    "value": 345.0
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgder_max, Mf_vgder_min)",
  "mf_vgder_critico": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "tf_vgder": {
    "unit": "mm",
    "value": 17.3
  },
  "tpe_vgder": {
    "unit": "mm",
    "value": 25.4
  }
}
```

### Intermedios

```json
{
  "phi_rn_pe_v1_vgder": 1330.2233999999999,
  "ru_pe_v1_vgder": 1330.2233999999999,
  "z_vgder": 589.7
}
```

### Factores de diseno

```json
{
  "phi": 1.0
}
```

### Unidades

```json
{
  "phi_rn_pe_v1_vgizq": "kN",
  "ru_pe_v1_vgizq": "kN"
}
```

## Check 30 - bueep_4e Step 7.2.2 end-plate shear rupture (right)

- Regla: `AISC358.06.7.bueep_4e.step7_2_2_end_plate_shear_rupture_vgder`
- Documento: `AISC 358-22`
- Clausula: `Chapter 6 / Section 6.7.1 Step 7.2.2 + Eq. (6.7-12)`
- Estado: `NG`
- Demanda: `1346.032856 kN`
- Capacidad: `1149.88086 kN`
- Capacidad final: `1149.88086 kN`
- DCR: `1.170585`
- Ecuacion: `Rn_pe_v2_vgder = Ru_pe_m3_vgder / (2*(d_vgder - tf_vgder)); phi*Rn_pe_v2_vgder = phi * 0.6 * Fup_pe_vgder * tpe_vgder * (bpe_vgder - 2*(dh_pe_vgder + 1.6 mm)) (AISC 358-22 Eq. 6.7-12)`

### Inputs

```json
{
  "bpe_vgder": {
    "unit": "mm",
    "value": 253.0
  },
  "d_vgder": {
    "unit": "mm",
    "value": 607.0
  },
  "db": {
    "unit": "mm",
    "value": 28.575
  },
  "dh_pe_vgder": {
    "unit": "mm",
    "value": 31.75
  },
  "fup_pe_vgder": {
    "unit": "MPa",
    "value": 450.0
  },
  "mf_computed": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "mf_source": "max(Mf_vgder_max, Mf_vgder_min)",
  "ru_pe_m3_vgder": {
    "unit": "kN-mm",
    "value": 1587511.1501889762
  },
  "tf_vgder": {
    "unit": "mm",
    "value": 17.3
  },
  "tpe_vgder": {
    "unit": "mm",
    "value": 25.4
  }
}
```

### Intermedios

```json
{
  "db_in": 1.125,
  "design_shear": 1149.8808600000002,
  "edge_allowance": 1.6,
  "hole_add_in": 0.125,
  "net_width": 186.3,
  "nominal_shear": 1277.6454,
  "phi_n": 0.9,
  "table_case": "db>=1.125 in",
  "z_vgder": 589.7
}
```

### Factores de diseno

```json
{
  "phi": 0.9
}
```

### Unidades

```json
{
  "phi_rn_pe_v2_vgizq": "kN",
  "rn_pe_v2_vgizq": "kN"
}
```
