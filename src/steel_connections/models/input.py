from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Any, Literal, Union

from pydantic import Field, TypeAdapter, field_validator, model_validator

from steel_connections.models.units import Quantity, StrictModel, UnitSystem, validate_quantity_unit


class DesignCodeContext(StrictModel):
    primary_document: str
    supporting_documents: list[str]


class SectionReferences(StrictModel):
    beam_shape: str
    beam_shape_der: str | None = None
    beam_shape_izq: str | None = None
    column_shape: str | None = None

    @field_validator("beam_shape", "beam_shape_der", "beam_shape_izq")
    @classmethod
    def normalize_beam_shape(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("sections.beam_shape/beam_shape_der/beam_shape_izq cannot be empty.")
        return normalized

    @field_validator("column_shape")
    @classmethod
    def normalize_column_shape(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("sections.column_shape cannot be empty when provided.")
        return normalized


class AISC358MomentMaterials(StrictModel):
    profile_steel_type: str | None = None
    plate_steel_type: str | None = None
    continuity_plate_steel_type: str | None = None
    doubler_plate_steel_type: str | None = None
    stiffener_steel_type_vgder: str | None = None
    stiffener_steel_type_vgizq: str | None = None
    bolt_fabrication_standard: str | None = None
    bolt_fabrication_standard_vgder: str | None = None
    bolt_fabrication_standard_vgizq: str | None = None
    bolt_description: str | None = None
    bolt_description_vgder: str | None = None
    bolt_description_vgizq: str | None = None
    bolt_shape: str | None = None
    bolt_shape_vgder: str | None = None
    bolt_shape_vgizq: str | None = None
    bolt_thread_condition: str | None = None
    bolt_thread_condition_vgder: str | None = None
    bolt_thread_condition_vgizq: str | None = None
    beam_fy: Quantity | None = None
    beam_fu: Quantity | None = None
    weld_fexx: Quantity | None = None
    weld_fexx_w4_vgder: Quantity | None = None
    weld_fexx_w4_vgizq: Quantity | None = None
    end_plate_fy: Quantity | None = None
    end_plate_fu: Quantity | None = None
    bolt_fnt: Quantity | None = None
    bolt_fnv: Quantity | None = None
    bolt_fnt_vgder: Quantity | None = None
    bolt_fnt_vgizq: Quantity | None = None
    bolt_fnv_vgder: Quantity | None = None
    bolt_fnv_vgizq: Quantity | None = None
    column_fu: Quantity | None = None
    column_fy: Quantity | None = None
    stiffener_fy: Quantity | None = None
    stiffener_fy_vgder: Quantity | None = None
    stiffener_fy_vgizq: Quantity | None = None
    elastic_modulus: Quantity | None = None
    bolt_grade: str | None = None

    @field_validator(
        "profile_steel_type",
        "plate_steel_type",
        "continuity_plate_steel_type",
        "doubler_plate_steel_type",
        "stiffener_steel_type_vgder",
        "stiffener_steel_type_vgizq",
        "bolt_fabrication_standard",
        "bolt_fabrication_standard_vgder",
        "bolt_fabrication_standard_vgizq",
        "bolt_description",
        "bolt_description_vgder",
        "bolt_description_vgizq",
        "bolt_shape",
        "bolt_shape_vgder",
        "bolt_shape_vgizq",
        "bolt_grade",
    )
    @classmethod
    def normalize_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Text material fields cannot be empty when provided.")
        return normalized

    @field_validator("bolt_thread_condition", "bolt_thread_condition_vgder", "bolt_thread_condition_vgizq")
    @classmethod
    def validate_bolt_thread_condition(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in {"N", "X"}:
            raise ValueError("materials.bolt_thread_condition must be 'N' or 'X'.")
        return normalized


class AISC358MomentGeometry(StrictModel):
    beam_flange_area: Quantity | None = None
    weld_effective_area: Quantity | None = None
    beam_clear_span_length_der: Quantity | None = None
    beam_clear_span_length_izq: Quantity | None = None
    beam_shear_connector_free_length_from_column_face_der: Quantity | None = None
    beam_shear_connector_free_length_from_column_face_izq: Quantity | None = None
    beam_clear_span_length: Quantity | None = None
    beam_shear_connector_free_length_from_column_face: Quantity | None = None
    end_plate_width_vgder: Quantity | None = None
    end_plate_width_vgizq: Quantity | None = None
    end_plate_thickness_vgder: Quantity | None = None
    end_plate_thickness_vgizq: Quantity | None = None
    de_vgder: Quantity | None = None
    de_vgizq: Quantity | None = None
    pb_vgder: Quantity | None = None
    pb_vgizq: Quantity | None = None
    pfo_vgder: Quantity | None = None
    pfo_vgizq: Quantity | None = None
    pfi_vgder: Quantity | None = None
    pfi_vgizq: Quantity | None = None
    cond_pe_vgder: str | None = None
    cond_pe_vgizq: str | None = None
    cond_amb_pe_vgder: str | None = None
    cond_amb_pe_vgizq: str | None = None
    cond_col: str | None = None
    cond_amb_col: str | None = None
    bolt_gage_vgder: Quantity | None = None
    bolt_gage_vgizq: Quantity | None = None
    stiffener_thickness_vgder: Quantity | None = None
    stiffener_thickness_vgizq: Quantity | None = None
    column_slab_connection_condition: str | None = None
    panel_zone_inelastic_deformation_considered: bool | None = None
    panel_zone_equation_package: str | None = None
    end_plate_width: Quantity | None = None
    end_plate_thickness: Quantity | None = None
    de: Quantity | None = None
    pb: Quantity | None = None
    pfo: Quantity | None = None
    pfi: Quantity | None = None
    continuity_plate_thickness: Quantity | None = None
    continuity_plate_width_b1: Quantity | None = None
    continuity_plate_count: int | None = None
    continuity_plate_enabled: bool | None = None
    continuity_plate_weld_type: str | None = None
    continuity_plate_weld_type_col: str | None = None
    continuity_plate_web_weld_type_col: str | None = None
    t_w5_col: Quantity | None = None
    w_w5_col: Quantity | None = None
    nl_w5_col: int | None = None
    L_gap_w5_col: Quantity | None = None
    kds_w5_col: float | None = None
    t_w6_col: Quantity | None = None
    w_w6_col: Quantity | None = None
    nl_w6_col: int | None = None
    L_gap_w6_col: Quantity | None = None
    kds_w6_col: float | None = None
    use_weld_7_col: bool | None = None
    tipo_w8_col: str | None = None
    t_w8_col: Quantity | None = None
    w_w8_col: Quantity | None = None
    nl_w8_col: int | None = None
    L_gap_w8_col: Quantity | None = None
    kds_w8_col: float | None = None
    tipo_w9_col: str | None = None
    use_weld_9_col: bool | None = None
    t_w9_col: Quantity | None = None
    w_w9_col: Quantity | None = None
    nl_w9_col: int | None = None
    L_gap_w9_col: Quantity | None = None
    kds_w9_col: float | None = None
    doubler_plate_thickness: Quantity | None = None
    doubler_plate_count: int | None = None
    gap_dp_col: Quantity | None = None
    extended_dp_col: bool | None = None
    doubler_plate_enabled: bool | None = None
    doubler_plate_web_plug_weld_type: str | None = None
    doubler_plate_web_plug_weld_size: Quantity | None = None
    w_w7_col: Quantity | None = None
    d_hole_w7_col: Quantity | None = None
    nfilas_w7_col: int | None = None
    ncolumna_w7_col: int | None = None
    doubler_plate_web_plug_weld_lines_nl: int | None = None
    bolt_diameter: Quantity | None = None
    bolt_diameter_vgder: Quantity | None = None
    bolt_diameter_vgizq: Quantity | None = None
    bolt_gage: Quantity | None = None
    bolt_tightening_type: str | None = None
    bolt_tightening_type_vgder: str | None = None
    bolt_tightening_type_vgizq: str | None = None
    clear_distance_end_plate: Quantity | None = None
    clear_distance_end_plate_vgder: Quantity | None = None
    clear_distance_end_plate_vgizq: Quantity | None = None
    clear_distance_column_flange: Quantity | None = None
    clear_distance_column_flange_vgder: Quantity | None = None
    clear_distance_column_flange_vgizq: Quantity | None = None
    column_end_distance_to_beam_flange: Quantity | None = None
    hb_col: Quantity | None = None
    ht_col: Quantity | None = None
    end_plate_beam_web_weld_type: str | None = None
    end_plate_beam_web_weld_type_vgder: str | None = None
    end_plate_beam_web_weld_type_vgizq: str | None = None
    end_plate_beam_web_weld_thickness_twe: Quantity | None = None
    end_plate_beam_web_weld_thickness_twe_vgder: Quantity | None = None
    end_plate_beam_web_weld_thickness_twe_vgizq: Quantity | None = None
    end_plate_beam_web_weld_lines_nl: int | None = None
    end_plate_beam_web_weld_lines_nl_vgder: int | None = None
    end_plate_beam_web_weld_lines_nl_vgizq: int | None = None
    end_plate_stiffener_weld_type: str | None = None
    end_plate_stiffener_weld_type_vgder: str | None = None
    end_plate_stiffener_weld_type_vgizq: str | None = None
    L_gap_w1: Quantity | None = None
    L_gap_w1_vgder: Quantity | None = None
    L_gap_w1_vgizq: Quantity | None = None
    end_plate_stiffener_weld_length_lst: Quantity | None = None
    end_plate_stiffener_weld_size_wst: Quantity | None = None
    end_plate_stiffener_weld_size_wst_vgder: Quantity | None = None
    end_plate_stiffener_weld_size_wst_vgizq: Quantity | None = None
    end_plate_stiffener_weld_lines_nl: int | None = None
    end_plate_stiffener_weld_lines_nl_vgder: int | None = None
    end_plate_stiffener_weld_lines_nl_vgizq: int | None = None
    beam_stiffener_weld_type: str | None = None
    beam_stiffener_weld_type_vgder: str | None = None
    beam_stiffener_weld_type_vgizq: str | None = None
    L_gap_w2: Quantity | None = None
    L_gap_w2_vgder: Quantity | None = None
    L_gap_w2_vgizq: Quantity | None = None
    beam_stiffener_weld_length_lstw2: Quantity | None = None
    beam_stiffener_weld_size_wst2: Quantity | None = None
    beam_stiffener_weld_size_wst2_vgder: Quantity | None = None
    beam_stiffener_weld_size_wst2_vgizq: Quantity | None = None
    beam_stiffener_weld_lines_nl_w2: int | None = None
    beam_stiffener_weld_lines_nl_w2_vgder: int | None = None
    beam_stiffener_weld_lines_nl_w2_vgizq: int | None = None
    kds_w1_vgder: float | None = None
    kds_w1_vgizq: float | None = None
    kds_w2_vgder: float | None = None
    kds_w2_vgizq: float | None = None
    kds_w3_vgder: float | None = None
    kds_w3_vgizq: float | None = None
    tipo_w4_vgder: str | None = None
    tipo_w4_vgizq: str | None = None
    t_w4_vgder: Quantity | None = None
    t_w4_vgizq: Quantity | None = None
    nl_w4_vgder: int | None = None
    nl_w4_vgizq: int | None = None
    t_w4_1_vgder: Quantity | None = None
    t_w4_1_vgizq: Quantity | None = None
    kds_w4_vgder: float | None = None
    kds_w4_vgizq: float | None = None
    stiffener_height: Quantity | None = None
    stiffener_thickness: Quantity | None = None
    stiffener_length: Quantity | None = None

    @field_validator("column_slab_connection_condition")
    @classmethod
    def validate_column_slab_connection_condition(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"isolated", "aislada"}:
            return "isolated"
        if normalized in {"not_isolated", "no_aislada"}:
            return "not_isolated"
        raise ValueError(
            "geometry.column_slab_connection_condition must be "
            "'isolated' or 'not_isolated' (also accepts 'aislada'/'no_aislada')."
        )

    @field_validator(
        "cond_pe_vgder",
        "cond_pe_vgizq",
        "cond_col",
    )
    @classmethod
    def normalize_surface_condition_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"painted", "pintada"}:
            return "painted"
        if normalized in {"unpainted", "not_painted", "no_pintada", "sin_pintura"}:
            return "unpainted"
        raise ValueError("Surface condition must be 'painted'/'pintada' or 'unpainted'/'no pintada'.")

    @field_validator(
        "cond_amb_pe_vgder",
        "cond_amb_pe_vgizq",
        "cond_amb_col",
    )
    @classmethod
    def normalize_atmospheric_condition_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"corrosive", "corrosiva"}:
            return "corrosive"
        if normalized in {"non_corrosive", "not_corrosive", "no_corrosiva"}:
            return "non_corrosive"
        raise ValueError(
            "Atmospheric condition must be 'corrosive'/'corrosiva' or 'non_corrosive'/'no corrosiva'."
        )

    @field_validator("panel_zone_equation_package")
    @classmethod
    def validate_panel_zone_equation_package(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower().replace(" ", "").replace("_", "")
        if normalized in {"a", "(a)", "paquetea"}:
            return "a"
        if normalized in {"b", "(b)", "paqueteb"}:
            return "b"
        raise ValueError(
            "geometry.panel_zone_equation_package must be 'a' or 'b' "
            "(also accepts '(a)'/'(b)' and 'paquete_a'/'paquete_b')."
        )

    @field_validator(
        "continuity_plate_weld_type",
        "continuity_plate_weld_type_col",
        "continuity_plate_web_weld_type_col",
        "end_plate_beam_web_weld_type",
        "end_plate_beam_web_weld_type_vgder",
        "end_plate_beam_web_weld_type_vgizq",
        "end_plate_stiffener_weld_type",
        "end_plate_stiffener_weld_type_vgder",
        "end_plate_stiffener_weld_type_vgizq",
        "beam_stiffener_weld_type",
        "beam_stiffener_weld_type_vgder",
        "beam_stiffener_weld_type_vgizq",
        "tipo_w4_vgder",
        "tipo_w4_vgizq",
        "doubler_plate_web_plug_weld_type",
        "tipo_w8_col",
        "tipo_w9_col",
    )
    @classmethod
    def normalize_weld_type_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        return normalized

    @field_validator("end_plate_beam_web_weld_lines_nl")
    @classmethod
    def validate_end_plate_beam_web_weld_lines_nl(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.end_plate_beam_web_weld_lines_nl must be >= 1.")
        return value

    @field_validator("doubler_plate_web_plug_weld_lines_nl")
    @classmethod
    def validate_doubler_plate_web_plug_weld_lines_nl(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.doubler_plate_web_plug_weld_lines_nl must be >= 1.")
        return value

    @field_validator("nfilas_w7_col", "ncolumna_w7_col")
    @classmethod
    def validate_w7_grid_counts(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.nfilas_w7_col / geometry.ncolumna_w7_col must be >= 1.")
        return value

    @field_validator("doubler_plate_count")
    @classmethod
    def validate_doubler_plate_count(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value < 0:
            raise ValueError("geometry.doubler_plate_count must be >= 0.")
        return value

    @field_validator("continuity_plate_count")
    @classmethod
    def validate_continuity_plate_count(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.continuity_plate_count must be >= 1.")
        return value

    @field_validator("nl_w5_col")
    @classmethod
    def validate_continuity_plate_weld_lines(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.nl_w5_col must be >= 1.")
        return value

    @field_validator("nl_w6_col")
    @classmethod
    def validate_continuity_plate_web_weld_lines(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.nl_w6_col must be >= 1.")
        return value

    @field_validator("nl_w8_col")
    @classmethod
    def validate_continuity_plate_extra_weld_lines(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.nl_w8_col must be >= 1.")
        return value

    @field_validator("nl_w9_col")
    @classmethod
    def validate_continuity_plate_extra_weld_lines_9(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.nl_w9_col must be >= 1.")
        return value

    @field_validator("end_plate_beam_web_weld_lines_nl_vgder", "end_plate_beam_web_weld_lines_nl_vgizq")
    @classmethod
    def validate_end_plate_beam_web_weld_lines_nl_side(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.end_plate_beam_web_weld_lines_nl_vg<lado> must be >= 1.")
        return value

    @field_validator("end_plate_stiffener_weld_lines_nl")
    @classmethod
    def validate_end_plate_stiffener_weld_lines_nl(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.end_plate_stiffener_weld_lines_nl must be >= 1.")
        return value

    @field_validator("end_plate_stiffener_weld_lines_nl_vgder", "end_plate_stiffener_weld_lines_nl_vgizq")
    @classmethod
    def validate_end_plate_stiffener_weld_lines_nl_side(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.end_plate_stiffener_weld_lines_nl_vg<lado> must be >= 1.")
        return value

    @field_validator("beam_stiffener_weld_lines_nl_w2")
    @classmethod
    def validate_beam_stiffener_weld_lines_nl_w2(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.beam_stiffener_weld_lines_nl_w2 must be >= 1.")
        return value

    @field_validator("beam_stiffener_weld_lines_nl_w2_vgder", "beam_stiffener_weld_lines_nl_w2_vgizq")
    @classmethod
    def validate_beam_stiffener_weld_lines_nl_w2_side(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.beam_stiffener_weld_lines_nl_w2_vg<lado> must be >= 1.")
        return value

    @field_validator("nl_w4_vgder", "nl_w4_vgizq")
    @classmethod
    def validate_weld_4_lines(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.nl_w4_<lado> must be >= 1.")
        return value

    @field_validator(
        "kds_w1_vgder",
        "kds_w1_vgizq",
        "kds_w2_vgder",
        "kds_w2_vgizq",
        "kds_w3_vgder",
        "kds_w3_vgizq",
        "kds_w4_vgder",
        "kds_w4_vgizq",
        "kds_w5_col",
        "kds_w9_col",
    )
    @classmethod
    def validate_kds_positive(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if value <= 0.0:
            raise ValueError("geometry.kds_wi_<lado> must be > 0.")
        return value

    @field_validator("bolt_tightening_type", "bolt_tightening_type_vgder", "bolt_tightening_type_vgizq")
    @classmethod
    def normalize_bolt_tightening_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if not normalized:
            return None
        if normalized in {"pretensioned", "pretensionado", "pretensado", "apriete_pretensionado"}:
            return "pretensioned"
        if normalized in {"snug_tight", "snugtight", "apriete_justo"}:
            return "snug_tight"
        return normalized


class AISC358MomentLoads(StrictModel):
    beam_flange_tension: Quantity | None = None
    pu_viga_right: Quantity | None = None
    pu_viga_left: Quantity | None = None
    pu_viga: Quantity | None = None
    Vu2_vgder: Quantity | None = None
    Vu2_vgizq: Quantity | None = None
    Mu3_vgder: Quantity | None = None
    Mu3_vgizq: Quantity | None = None
    pu_columna: Quantity | None = None
    probable_moment_column_face: Quantity | None = None
    probable_moment_plastic_hinge: Quantity | None = None
    shear_plastic_hinge_dermax: Quantity | None = None
    shear_plastic_hinge_dermin: Quantity | None = None
    shear_plastic_hinge_izqmax: Quantity | None = None
    shear_plastic_hinge_izqmin: Quantity | None = None
    shear_plastic_hinge: Quantity | None = None
    beam_right_vgravity: Quantity | None = None
    beam_left_vgravity: Quantity | None = None
    beam_gravity_shear_between_hinges_der: Quantity | None = None
    beam_gravity_shear_between_hinges_izq: Quantity | None = None
    beam_gravity_shear_between_hinges: Quantity | None = None
    beam_gravity_shear_face_segment: Quantity | None = None


class AISC358MomentDesignFactors(StrictModel):
    phi_flange_tension: float | None = None
    phi_flange_weld: float | None = None
    phi_d: float | None = None
    phi_n: float | None = None
    phi_f: float | None = None
    ry: float | None = None
    beam_connection_sides: str | None = None
    member_ductility_demand_beam: str | None = None
    member_ductility_demand_beam_vgder: str | None = None
    member_ductility_demand_beam_vgizq: str | None = None
    member_ductility_demand_column: str | None = None
    column_beam_moment_ratio_minimum: float | None = None
    column_beam_moment_ratio: float | None = None

    @field_validator(
        "phi_flange_tension",
        "phi_flange_weld",
        "phi_d",
        "phi_n",
        "phi_f",
    )
    @classmethod
    def validate_phi_range(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if not (0.0 < value <= 1.0):
            raise ValueError("Resistance factor phi must be in (0, 1].")
        return value

    @field_validator("ry")
    @classmethod
    def validate_ry(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if value < 1.0:
            raise ValueError("Ry must be >= 1.0.")
        return value

    @field_validator("beam_connection_sides")
    @classmethod
    def normalize_beam_connection_sides(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"left", "left_only", "izq", "izquierda", "solo_izquierda"}:
            return "left_only"
        if normalized in {"right", "right_only", "der", "derecha", "solo_derecha"}:
            return "right_only"
        if normalized in {"both", "both_sides", "ambas", "ambos_lados", "izq_der"}:
            return "both_sides"
        raise ValueError(
            "design_factors.beam_connection_sides must be 'left_only', 'right_only' or 'both_sides' "
            "(also accepts 'izquierda'/'derecha'/'ambas')."
        )

    @field_validator(
        "member_ductility_demand_beam",
        "member_ductility_demand_beam_vgder",
        "member_ductility_demand_beam_vgizq",
        "member_ductility_demand_column",
    )
    @classmethod
    def validate_member_ductility_demand(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in {"high", "moderate", "low"}:
            raise ValueError("member_ductility_demand_* must be 'high', 'moderate' or 'low'.")
        return normalized

    @field_validator("column_beam_moment_ratio_minimum", "column_beam_moment_ratio")
    @classmethod
    def validate_moment_ratio_minimum(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if value <= 0.0:
            raise ValueError("column_beam_moment_ratio_* must be > 0.")
        return value


class AISC358MomentProcedure(StrictModel):
    beam_plastic_section_modulus_ze: Quantity | None = None
    beam_span_between_plastic_hinges_lh: Quantity | None = None
    yield_line_parameter_yp: Quantity | None = None
    column_yield_line_parameter_yc_unstiffened: Quantity | None = None
    column_yield_line_parameter_yc_stiffened: Quantity | None = None
    flange_weld_available_strength: Quantity | None = None
    web_weld_available_strength: Quantity | None = None
    continuity_plate_available_strength: Quantity | None = None
    panel_zone_capacity: Quantity | None = None


class DG1Materials(StrictModel):
    column_fy: Quantity | None
    plate_fy: Quantity | None
    anchor_fu: Quantity | None


class DG1Geometry(StrictModel):
    base_plate_area: Quantity | None
    anchor_area: Quantity | None


class DG1Loads(StrictModel):
    axial_compression: Quantity | None


class DG1DesignFactors(StrictModel):
    phi_bearing: float

    @field_validator("phi_bearing")
    @classmethod
    def validate_phi_range(cls, value: float) -> float:
        if not (0.0 < value <= 1.0):
            raise ValueError("Resistance factor phi must be in (0, 1].")
        return value


class CaseBase(StrictModel):
    project_id: str
    case_id: str
    design_code_context: DesignCodeContext
    units_system: UnitSystem
    connection_family: str
    connection_type: str
    load_state: str


class AISC358MomentCase(CaseBase):
    connection_family: Literal["moment_prequalified"]
    connection_type: Literal["wuf_w", "bueep_4e", "bseep_4es", "bseep_8es"]
    sections: SectionReferences
    materials: AISC358MomentMaterials
    geometry: AISC358MomentGeometry
    loads: AISC358MomentLoads
    design_factors: AISC358MomentDesignFactors
    procedure: AISC358MomentProcedure | None = None

    @model_validator(mode="after")
    def validate_units(self) -> "AISC358MomentCase":
        if self.materials.beam_fy is not None:
            validate_quantity_unit(
                self.materials.beam_fy,
                "stress",
                self.units_system,
                "materials.beam_fy",
            )
        if self.materials.weld_fexx is not None:
            validate_quantity_unit(
                self.materials.weld_fexx,
                "stress",
                self.units_system,
                "materials.weld_fexx",
            )
        for field_name in (
            "beam_fu",
            "end_plate_fy",
            "end_plate_fu",
            "bolt_fnt",
            "bolt_fnv",
            "bolt_fnt_vgder",
            "bolt_fnt_vgizq",
            "bolt_fnv_vgder",
            "bolt_fnv_vgizq",
            "column_fu",
            "column_fy",
            "stiffener_fy",
            "stiffener_fy_vgder",
            "stiffener_fy_vgizq",
            "elastic_modulus",
        ):
            value = getattr(self.materials, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "stress",
                    self.units_system,
                    f"materials.{field_name}",
                )
        if self.geometry.beam_flange_area is not None:
            validate_quantity_unit(
                self.geometry.beam_flange_area,
                "area",
                self.units_system,
                "geometry.beam_flange_area",
            )
        if self.geometry.weld_effective_area is not None:
            validate_quantity_unit(
                self.geometry.weld_effective_area,
                "area",
                self.units_system,
                "geometry.weld_effective_area",
            )
        if self.loads.beam_flange_tension is not None:
            validate_quantity_unit(
                self.loads.beam_flange_tension,
                "force",
                self.units_system,
                "loads.beam_flange_tension",
            )
        for field_name in (
            "beam_clear_span_length_der",
            "beam_clear_span_length_izq",
            "beam_shear_connector_free_length_from_column_face_der",
            "beam_shear_connector_free_length_from_column_face_izq",
            "beam_clear_span_length",
            "beam_shear_connector_free_length_from_column_face",
            "end_plate_width_vgder",
            "end_plate_width_vgizq",
            "end_plate_thickness_vgder",
            "end_plate_thickness_vgizq",
            "de_vgder",
            "de_vgizq",
            "pb_vgder",
            "pb_vgizq",
            "pfo_vgder",
            "pfo_vgizq",
            "pfi_vgder",
            "pfi_vgizq",
            "bolt_gage_vgder",
            "bolt_gage_vgizq",
            "stiffener_thickness_vgder",
            "stiffener_thickness_vgizq",
            "end_plate_width",
            "end_plate_thickness",
            "de",
            "pb",
            "pfo",
            "pfi",
            "continuity_plate_thickness",
            "continuity_plate_width_b1",
            "doubler_plate_thickness",
            "gap_dp_col",
            "bolt_diameter",
            "bolt_diameter_vgder",
            "bolt_diameter_vgizq",
            "bolt_gage",
            "clear_distance_end_plate",
            "clear_distance_end_plate_vgder",
            "clear_distance_end_plate_vgizq",
            "clear_distance_column_flange",
            "clear_distance_column_flange_vgder",
            "clear_distance_column_flange_vgizq",
            "column_end_distance_to_beam_flange",
            "end_plate_beam_web_weld_thickness_twe",
            "end_plate_beam_web_weld_thickness_twe_vgder",
            "end_plate_beam_web_weld_thickness_twe_vgizq",
            "end_plate_stiffener_weld_length_lst",
            "L_gap_w1",
            "L_gap_w1_vgder",
            "L_gap_w1_vgizq",
            "end_plate_stiffener_weld_size_wst",
            "end_plate_stiffener_weld_size_wst_vgder",
            "end_plate_stiffener_weld_size_wst_vgizq",
            "beam_stiffener_weld_length_lstw2",
            "L_gap_w2",
            "L_gap_w2_vgder",
            "L_gap_w2_vgizq",
            "beam_stiffener_weld_size_wst2",
            "beam_stiffener_weld_size_wst2_vgder",
            "beam_stiffener_weld_size_wst2_vgizq",
            "stiffener_height",
            "stiffener_thickness",
            "stiffener_length",
            "t_w4_vgder",
            "t_w4_vgizq",
            "t_w4_1_vgder",
            "t_w4_1_vgizq",
            "t_w5_col",
            "w_w5_col",
            "L_gap_w5_col",
            "t_w6_col",
            "w_w6_col",
            "t_w8_col",
            "w_w8_col",
            "L_gap_w8_col",
            "t_w9_col",
            "w_w9_col",
            "L_gap_w9_col",
            "w_w7_col",
            "d_hole_w7_col",
            "doubler_plate_web_plug_weld_size",
        ):
            value = getattr(self.geometry, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "length",
                    self.units_system,
                    f"geometry.{field_name}",
                )
        for field_name in (
            "pu_viga_right",
            "pu_viga_left",
            "pu_viga",
            "Vu2_vgder",
            "Vu2_vgizq",
            "pu_columna",
            "shear_plastic_hinge_dermax",
            "shear_plastic_hinge_dermin",
            "shear_plastic_hinge_izqmax",
            "shear_plastic_hinge_izqmin",
            "shear_plastic_hinge",
            "beam_right_vgravity",
            "beam_left_vgravity",
            "beam_gravity_shear_between_hinges_der",
            "beam_gravity_shear_between_hinges_izq",
            "beam_gravity_shear_between_hinges",
            "beam_gravity_shear_face_segment",
        ):
            value = getattr(self.loads, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "force",
                    self.units_system,
                    f"loads.{field_name}",
                )
        for field_name in ("Mu3_vgder", "Mu3_vgizq"):
            value = getattr(self.loads, field_name)
            if value is not None:
                if self.units_system == UnitSystem.US:
                    if value.unit != "kip-in":
                        raise ValueError(
                            f"Invalid unit at 'loads.{field_name}'. "
                            f"Expected 'kip-in' for {self.units_system.value}."
                        )
                else:
                    if value.unit not in {"kN-mm", "kN-m"}:
                        raise ValueError(
                            f"Invalid unit at 'loads.{field_name}'. "
                            f"Expected 'kN-mm' or 'kN-m' for {self.units_system.value}."
                        )
        if self.loads.probable_moment_column_face is not None:
            expected_unit = "kip-in" if self.units_system == UnitSystem.US else "kN-mm"
            if self.loads.probable_moment_column_face.unit != expected_unit:
                raise ValueError(
                    "Invalid unit at 'loads.probable_moment_column_face'. "
                    f"Expected '{expected_unit}' for {self.units_system.value}."
                )
        if self.loads.probable_moment_plastic_hinge is not None:
            expected_unit = "kip-in" if self.units_system == UnitSystem.US else "kN-mm"
            if self.loads.probable_moment_plastic_hinge.unit != expected_unit:
                raise ValueError(
                    "Invalid unit at 'loads.probable_moment_plastic_hinge'. "
                    f"Expected '{expected_unit}' for {self.units_system.value}."
                )
        if self.procedure is not None:
            if self.procedure.beam_plastic_section_modulus_ze is not None:
                expected_ze_unit = "in3" if self.units_system == UnitSystem.US else "mm3"
                if self.procedure.beam_plastic_section_modulus_ze.unit != expected_ze_unit:
                    raise ValueError(
                        "Invalid unit at 'procedure.beam_plastic_section_modulus_ze'. "
                        f"Expected '{expected_ze_unit}'."
                    )
            for field_name in (
                "beam_span_between_plastic_hinges_lh",
                "yield_line_parameter_yp",
                "column_yield_line_parameter_yc_unstiffened",
                "column_yield_line_parameter_yc_stiffened",
            ):
                value = getattr(self.procedure, field_name)
                if value is not None:
                    validate_quantity_unit(
                        value,
                        "length",
                        self.units_system,
                        f"procedure.{field_name}",
                    )
            for field_name in (
                "flange_weld_available_strength",
                "web_weld_available_strength",
                "continuity_plate_available_strength",
                "panel_zone_capacity",
            ):
                value = getattr(self.procedure, field_name)
                if value is not None:
                    validate_quantity_unit(
                        value,
                        "force",
                        self.units_system,
                        f"procedure.{field_name}",
                    )
        return self


class BeamBeamMomentBoltedSections(StrictModel):
    shape_vg: str

    @field_validator("shape_vg")
    @classmethod
    def normalize_shape(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("sections.shape_vg cannot be empty.")
        return normalized


class BeamBeamMomentBoltedMaterials(StrictModel):
    steel_vg: str
    steel_plt_web: str | None = None
    steel_plt_flange: str | None = None
    Fy_vg: Quantity | None = None
    Fu_vg: Quantity | None = None
    E_vg: Quantity | None = None
    shape_blt_web: str
    std_blt_web: str
    desc_blt_web: str
    thread_blt_web: str
    shape_blt_flange: str
    std_blt_flange: str
    desc_blt_flange: str
    thread_blt_flange: str

    @field_validator(
        "steel_vg",
        "shape_blt_web",
        "std_blt_web",
        "desc_blt_web",
        "shape_blt_flange",
        "std_blt_flange",
        "desc_blt_flange",
    )
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Text material fields cannot be empty.")
        return normalized

    @field_validator("steel_plt_web", "steel_plt_flange")
    @classmethod
    def normalize_optional_steel_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Optional steel material fields cannot be empty when provided.")
        return normalized

    @field_validator("thread_blt_web", "thread_blt_flange")
    @classmethod
    def validate_bolt_thread_condition(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"N", "X"}:
            raise ValueError("materials.thread_blt_web/thread_blt_flange must be 'N' or 'X'.")
        return normalized


class BeamBeamMomentBoltedGeometry(StrictModel):
    gap_sp: Quantity
    tol_L_vg: Quantity
    cond_sup_vg: str | None = None
    cond_amb_vg: str | None = None
    c3_clearance_type: str = "circular"
    t_plt_web: Quantity
    type_hole_plt_web: str
    cond_sup_plt_web: str | None = None
    cond_amb_plt_web: str | None = None
    t_plt_flange: Quantity
    type_hole_plt_flange: str
    cond_sup_plt_flange: str | None = None
    cond_amb_plt_flange: str | None = None
    n_blt_web_x: int
    n_blt_web_y: int
    g_blt_web: Quantity
    p_blt_web: Quantity
    Le_blt_web_x1: Quantity
    Le_blt_web_x2: Quantity
    Le_blt_web_y1: Quantity
    Le_blt_web_y2: Quantity
    type_tight_blt_web: str | None = None
    svc_hole_deformation_design_web: bool = False
    Ubs_web_v2_vg: float = 1.0
    Ubs_web_v3_vg: float = 1.0
    Cb_plt_m1_web: float = 1.0
    n_blt_flange_x: int
    n_blt_flange_z: int
    p_blt_flange: Quantity
    g_blt_flange: Quantity
    Le_blt_flange_x1: Quantity
    Le_blt_flange_x2: Quantity
    Le_blt_flange_z1: Quantity
    Le_blt_flange_z2: Quantity
    Le_blt_flange_z3: Quantity
    type_tight_blt_flange: str | None = None
    svc_hole_deformation_design_flange: bool = False

    @field_validator("n_blt_web_x", "n_blt_web_y", "n_blt_flange_x", "n_blt_flange_z")
    @classmethod
    def validate_positive_counts(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Bolt layout integer fields must be >= 1.")
        return value

    @field_validator("n_blt_flange_z")
    @classmethod
    def validate_flange_rows_per_side(cls, value: int) -> int:
        if value < 1:
            raise ValueError("geometry.n_blt_flange_z must be >= 1.")
        return value

    @field_validator(
            "cond_sup_vg",
            "cond_sup_plt_web",
            "cond_sup_plt_flange",
    )
    @classmethod
    def normalize_surface_condition(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"painted", "pintada"}:
            return "painted"
        if normalized in {"unpainted", "not_painted", "no_pintada", "sin_pintura"}:
            return "unpainted"
        raise ValueError("Surface condition must be 'painted'/'pintada' or 'unpainted'/'no pintada'.")

    @field_validator(
        "cond_amb_vg",
        "cond_amb_plt_web",
        "cond_amb_plt_flange",
    )
    @classmethod
    def normalize_atmospheric_condition(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"corrosive", "corrosiva"}:
            return "corrosive"
        if normalized in {"non_corrosive", "not_corrosive", "no_corrosiva"}:
            return "non_corrosive"
        raise ValueError(
            "Atmospheric condition must be 'corrosive'/'corrosiva' or 'non_corrosive'/'no corrosiva'."
        )

    @field_validator("c3_clearance_type")
    @classmethod
    def normalize_c3_clearance_type(cls, value: str) -> str:
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"circular", "circulo", "circular_hole"}:
            return "circular"
        if normalized in {"clipped", "clip", "recortado"}:
            return "clipped"
        raise ValueError("geometry.c3_clearance_type must be 'circular' or 'clipped'.")

    @field_validator("type_tight_blt_web", "type_tight_blt_flange")
    @classmethod
    def normalize_bolt_tightening_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"slip_critical", "slipcritical", "deslizamiento_critico"}:
            return "slip_critical"
        if normalized in {"pretensioned", "pretensionado", "pretensado", "apriete_pretensionado"}:
            return "pretensioned"
        if normalized in {"snug_tight", "snugtight", "apriete_justo"}:
            return "snug_tight"
        raise ValueError("Bolt tightening type must be 'pretensioned', 'snug_tight', or 'slip_critical'.")

    @field_validator("svc_hole_deformation_design_web", "svc_hole_deformation_design_flange", mode="before")
    @classmethod
    def normalize_service_hole_deformation_design_flag(cls, value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "si", "s", "y"}:
                return True
            if normalized in {"false", "0", "no", "n"}:
                return False
        if value is None:
            return False
        raise ValueError(
            "svc_hole_deformation_design_web/svc_hole_deformation_design_flange must be boolean (or true/false text)."
        )

    @field_validator("Ubs_web_v2_vg", "Ubs_web_v3_vg")
    @classmethod
    def validate_ubs_web_factor(cls, value: float) -> float:
        if value <= 0.0:
            raise ValueError("geometry.Ubs_web_v2_vg/Ubs_web_v3_vg must be > 0.")
        return value

    @field_validator("Cb_plt_m1_web")
    @classmethod
    def validate_cb_plt_m1_web(cls, value: float) -> float:
        if value <= 0.0:
            raise ValueError("geometry.Cb_plt_m1_web must be > 0.")
        return value

    @field_validator("type_hole_plt_web", "type_hole_plt_flange")
    @classmethod
    def normalize_hole_type(cls, value: str) -> str:
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "standard": "standard",
            "estandar": "standard",
            "oversize": "oversize",
            "sobredimensionado": "oversize",
            "short_slot": "short_slot",
            "ranura_corta": "short_slot",
            "long_slot": "long_slot",
            "ranura_larga": "long_slot",
        }
        canonical = aliases.get(normalized)
        if canonical is None:
            raise ValueError(
                "Hole type must be one of: standard, oversize, short_slot, long_slot."
            )
        return canonical


class BeamBeamMomentBoltedLoads(StrictModel):
    Pu_sp: Quantity
    Vu2_sp: Quantity
    Vu3_sp: Quantity
    Mu3_sp: Quantity
    Mu2_sp: Quantity
    Tu_sp: Quantity
    alpha_Pu_web: float = 0.0
    e2_blt_web: Quantity | None = None
    e1_blt_flange: Quantity | None = None


class BeamBeamMomentBoltedDesignFactors(StrictModel):
    phi_bt: float
    phi_bv: float
    phi_py: float
    phi_pr: float
    phi_bs: float
    phi_sc: float | None = None

    @field_validator(
        "phi_bt",
        "phi_bv",
        "phi_py",
        "phi_pr",
        "phi_bs",
        "phi_sc",
    )
    @classmethod
    def validate_phi_range(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if not (0.0 < value <= 1.0):
            raise ValueError("Resistance factor phi must be in (0, 1].")
        return value


class BeamBeamMomentBoltedICRSettings(StrictModel):
    # Grupo 1 (pernos de alma)
    method_1: str | None = None
    tolerance_1: float = 0.01
    max_iterations_1: int = 1000
    rult_1_kip: Quantity | None = None

    # Grupo 2 (pernos de ala)
    method_2: str | None = None
    tolerance_2: float = 0.01
    max_iterations_2: int = 1000
    rult_2_kip: Quantity | None = None

    # Legacy/global method (kept for backward compatibility).
    method: str | None = None

    @classmethod
    def _normalize_method_value(cls, value: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
        aliases = {
            "icr": "icr",
            "instant_center_of_rotation_method": "icr",
            "instant_center_of_rotation": "icr",
            "instantaneous_center_of_rotation_method": "icr",
            "nstant_center_of_rotation_method": "icr",
            "elastic_superposition": "elastic_superposition",
            "elastic_method_superposition": "elastic_superposition",
            "elastic_ecr": "elastic_ecr",
            "elastic_method_center_of_rotation": "elastic_ecr",
        }
        canonical = aliases.get(normalized)
        if canonical is None:
            if "superposition" in normalized:
                canonical = "elastic_superposition"
            elif "center_of_rotation" in normalized:
                if "instant" in normalized or "nstant" in normalized or normalized.startswith("icr"):
                    canonical = "icr"
                else:
                    canonical = "elastic_ecr"
        if canonical is None:
            raise ValueError(
                "procedure.method/method_1/method_2 must be "
                "'icr', 'elastic_superposition', or 'elastic_ecr'."
            )
        return canonical

    @field_validator("method", "method_1", "method_2")
    @classmethod
    def normalize_method(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return cls._normalize_method_value(value)

    @field_validator("tolerance_1", "tolerance_2")
    @classmethod
    def validate_tolerance(cls, value: float) -> float:
        if value <= 0.0:
            raise ValueError("procedure.tolerance_1/tolerance_2 must be > 0.")
        return value

    @field_validator("max_iterations_1", "max_iterations_2")
    @classmethod
    def validate_max_iterations(cls, value: int) -> int:
        if value < 1:
            raise ValueError("procedure.max_iterations_1/max_iterations_2 must be >= 1.")
        return value

    @model_validator(mode="after")
    def validate_conditional_rult(self) -> "BeamBeamMomentBoltedICRSettings":
        method_1 = self.method_1 or self.method or "elastic_superposition"
        method_2 = self.method_2 or self.method or "elastic_superposition"

        object.__setattr__(self, "method_1", method_1)
        object.__setattr__(self, "method_2", method_2)

        if method_1 == "icr" and self.rult_1_kip is None:
            raise ValueError("procedure.rult_1_kip is required when procedure.method_1='icr'.")
        if method_2 == "icr" and self.rult_2_kip is None:
            raise ValueError("procedure.rult_2_kip is required when procedure.method_2='icr'.")
        return self


class BeamBeamMomentBoltedProcedure(BeamBeamMomentBoltedICRSettings):
    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_icr_block(cls, data: object) -> object:
        if isinstance(data, dict):
            icr_block = data.get("icr")
            if isinstance(icr_block, dict):
                merged = dict(icr_block)
                for key, value in data.items():
                    if key != "icr":
                        merged[key] = value
                return merged
        return data


class BeamBeamMomentBoltedCase(CaseBase):
    connection_family: Literal["Fully_Restrained_Moment"]
    connection_type: Literal["bbmb_splice"]
    sections: BeamBeamMomentBoltedSections
    materials: BeamBeamMomentBoltedMaterials
    geometry: BeamBeamMomentBoltedGeometry
    loads: BeamBeamMomentBoltedLoads
    design_factors: BeamBeamMomentBoltedDesignFactors
    procedure: BeamBeamMomentBoltedProcedure | None = None

    @model_validator(mode="after")
    def validate_units(self) -> "BeamBeamMomentBoltedCase":
        for field_name in ("Fy_vg", "Fu_vg", "E_vg"):
            value = getattr(self.materials, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "stress",
                    self.units_system,
                    f"materials.{field_name}",
                )
        for field_name in (
            "gap_sp",
            "tol_L_vg",
            "t_plt_web",
            "t_plt_flange",
            "g_blt_web",
            "p_blt_web",
            "Le_blt_web_x1",
            "Le_blt_web_x2",
            "Le_blt_web_y1",
            "Le_blt_web_y2",
            "p_blt_flange",
            "g_blt_flange",
            "Le_blt_flange_x1",
            "Le_blt_flange_x2",
            "Le_blt_flange_z1",
            "Le_blt_flange_z2",
            "Le_blt_flange_z3",
        ):
            value = getattr(self.geometry, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "length",
                    self.units_system,
                    f"geometry.{field_name}",
                )
        for field_name in ("Pu_sp", "Vu2_sp", "Vu3_sp"):
            value = getattr(self.loads, field_name)
            validate_quantity_unit(
                value,
                "force",
                self.units_system,
                f"loads.{field_name}",
            )
        if self.loads.e2_blt_web is not None:
            validate_quantity_unit(
                self.loads.e2_blt_web,
                "length",
                self.units_system,
                "loads.e2_blt_web",
            )
        if self.loads.e1_blt_flange is not None:
            validate_quantity_unit(
                self.loads.e1_blt_flange,
                "length",
                self.units_system,
                "loads.e1_blt_flange",
            )
        expected_moment_unit = "kip-in" if self.units_system == UnitSystem.US else "kN-mm"
        for field_name in ("Mu3_sp", "Mu2_sp", "Tu_sp"):
            value = getattr(self.loads, field_name)
            if value.unit != expected_moment_unit:
                raise ValueError(
                    f"Invalid unit at 'loads.{field_name}'. "
                    f"Expected '{expected_moment_unit}' for {self.units_system.value}."
                )
        if self.procedure is not None and self.procedure.rult_1_kip is not None:
            if self.procedure.rult_1_kip.unit != "kip":
                raise ValueError("Invalid unit at 'procedure.rult_1_kip'. Expected 'kip'.")
        if self.procedure is not None and self.procedure.rult_2_kip is not None:
            if self.procedure.rult_2_kip.unit != "kip":
                raise ValueError("Invalid unit at 'procedure.rult_2_kip'. Expected 'kip'.")
        return self


class DG1BasePlateCase(CaseBase):
    connection_family: Literal["base_plate_anchor_rod"]
    connection_type: Literal["dg1_base_plate"]
    materials: DG1Materials
    geometry: DG1Geometry
    loads: DG1Loads
    design_factors: DG1DesignFactors

    @model_validator(mode="after")
    def validate_units(self) -> "DG1BasePlateCase":
        for field_name in ("column_fy", "plate_fy", "anchor_fu"):
            value = getattr(self.materials, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "stress",
                    self.units_system,
                    f"materials.{field_name}",
                )
        for field_name in ("base_plate_area", "anchor_area"):
            value = getattr(self.geometry, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "area",
                    self.units_system,
                    f"geometry.{field_name}",
                )
        if self.loads.axial_compression is not None:
            validate_quantity_unit(
                self.loads.axial_compression,
                "force",
                self.units_system,
                "loads.axial_compression",
            )
        return self


InputCase = Annotated[
    Union[AISC358MomentCase, BeamBeamMomentBoltedCase, DG1BasePlateCase],
    Field(discriminator="connection_family"),
]
INPUT_CASE_ADAPTER = TypeAdapter(InputCase)


def parse_input_case(payload: dict[str, Any]) -> InputCase:
    return INPUT_CASE_ADAPTER.validate_python(payload)


def parse_input_case_file(path: str | Path) -> InputCase:
    input_path = Path(path)
    # Use utf-8-sig so payloads saved with UTF-8 BOM are also accepted.
    with input_path.open("r", encoding="utf-8-sig") as stream:
        payload = json.load(stream)
    return parse_input_case(payload)
