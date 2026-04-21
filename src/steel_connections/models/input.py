from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, Literal, Union

from pydantic import Field, TypeAdapter, field_validator, model_validator

from steel_connections.models.units import Quantity, StrictModel, UnitSystem, validate_quantity_unit


class DesignCodeContext(StrictModel):
    primary_document: str
    supporting_documents: list[str]


class SectionReferences(StrictModel):
    beam_shape: str
    column_shape: str | None = None

    @field_validator("beam_shape")
    @classmethod
    def normalize_beam_shape(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("sections.beam_shape cannot be empty.")
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
    bolt_fabrication_standard: str | None = None
    bolt_description: str | None = None
    bolt_shape: str | None = None
    bolt_thread_condition: str | None = None
    beam_fy: Quantity | None = None
    beam_fu: Quantity | None = None
    weld_fexx: Quantity | None = None
    end_plate_fy: Quantity | None = None
    end_plate_fu: Quantity | None = None
    bolt_fnt: Quantity | None = None
    bolt_fnv: Quantity | None = None
    column_fu: Quantity | None = None
    column_fy: Quantity | None = None
    stiffener_fy: Quantity | None = None
    elastic_modulus: Quantity | None = None
    bolt_grade: str | None = None

    @field_validator(
        "profile_steel_type",
        "plate_steel_type",
        "bolt_fabrication_standard",
        "bolt_description",
        "bolt_shape",
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

    @field_validator("bolt_thread_condition")
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
    column_slab_connection_condition: str | None = None
    end_plate_width: Quantity | None = None
    end_plate_thickness: Quantity | None = None
    de: Quantity | None = None
    pb: Quantity | None = None
    pfo: Quantity | None = None
    pfi: Quantity | None = None
    continuity_plate_thickness: Quantity | None = None
    continuity_plate_weld_type: str | None = None
    bolt_diameter: Quantity | None = None
    bolt_gage: Quantity | None = None
    bolt_tightening_type: str | None = None
    clear_distance_end_plate: Quantity | None = None
    clear_distance_column_flange: Quantity | None = None
    column_end_distance_to_beam_flange: Quantity | None = None
    end_plate_beam_web_weld_type: str | None = None
    end_plate_beam_web_weld_thickness_twe: Quantity | None = None
    end_plate_beam_web_weld_lines_nl: int | None = None
    end_plate_stiffener_weld_type: str | None = None
    end_plate_stiffener_weld_length_lst: Quantity | None = None
    end_plate_stiffener_weld_size_wst: Quantity | None = None
    end_plate_stiffener_weld_lines_nl: int | None = None
    beam_stiffener_weld_type: str | None = None
    beam_stiffener_weld_length_lstw2: Quantity | None = None
    beam_stiffener_weld_size_wst2: Quantity | None = None
    beam_stiffener_weld_lines_nl_w2: int | None = None
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
        "continuity_plate_weld_type",
        "end_plate_beam_web_weld_type",
        "end_plate_stiffener_weld_type",
        "beam_stiffener_weld_type",
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

    @field_validator("end_plate_stiffener_weld_lines_nl")
    @classmethod
    def validate_end_plate_stiffener_weld_lines_nl(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.end_plate_stiffener_weld_lines_nl must be >= 1.")
        return value

    @field_validator("beam_stiffener_weld_lines_nl_w2")
    @classmethod
    def validate_beam_stiffener_weld_lines_nl_w2(cls, value: int | None) -> int | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("geometry.beam_stiffener_weld_lines_nl_w2 must be >= 1.")
        return value

    @field_validator("bolt_tightening_type")
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
    ry: float | None = None
    beam_connection_sides: str | None = None
    member_ductility_demand_beam: str | None = None
    member_ductility_demand_column: str | None = None
    column_beam_moment_ratio_minimum: float | None = None
    column_beam_moment_ratio: float | None = None

    @field_validator(
        "phi_flange_tension",
        "phi_flange_weld",
        "phi_d",
        "phi_n",
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
        if normalized in {"right", "right_only", "der", "derecha", "solo_derecha"}:
            return "right_only"
        if normalized in {"both", "both_sides", "ambas", "ambos_lados", "izq_der"}:
            return "both_sides"
        raise ValueError(
            "design_factors.beam_connection_sides must be 'right_only' or 'both_sides' "
            "(also accepts 'derecha'/'ambas')."
        )

    @field_validator("member_ductility_demand_beam", "member_ductility_demand_column")
    @classmethod
    def validate_member_ductility_demand(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in {"high", "moderate"}:
            raise ValueError("member_ductility_demand_* must be 'high' or 'moderate'.")
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
            "column_fu",
            "column_fy",
            "stiffener_fy",
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
            "end_plate_width",
            "end_plate_thickness",
            "de",
            "pb",
            "pfo",
            "pfi",
            "continuity_plate_thickness",
            "bolt_diameter",
            "bolt_gage",
            "clear_distance_end_plate",
            "clear_distance_column_flange",
            "column_end_distance_to_beam_flange",
            "end_plate_beam_web_weld_thickness_twe",
            "end_plate_stiffener_weld_length_lst",
            "end_plate_stiffener_weld_size_wst",
            "beam_stiffener_weld_length_lstw2",
            "beam_stiffener_weld_size_wst2",
            "stiffener_height",
            "stiffener_thickness",
            "stiffener_length",
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
    beam_left_shape: str
    beam_right_shape: str

    @field_validator("beam_left_shape", "beam_right_shape")
    @classmethod
    def normalize_shape(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("sections.beam_left_shape/beam_right_shape cannot be empty.")
        return normalized


class BeamBeamMomentBoltedMaterials(StrictModel):
    beam_left_steel_type: str
    beam_right_steel_type: str
    plate_steel_type: str
    bolt_fabrication_standard: str
    bolt_fabrication_standard_web: str | None = None
    bolt_fabrication_standard_flange: str | None = None
    bolt_description: str
    bolt_shape: str
    bolt_shape_web: str | None = None
    bolt_shape_flange: str | None = None
    bolt_thread_condition: str
    weld_fexx: Quantity | None = None

    @field_validator(
        "beam_left_steel_type",
        "beam_right_steel_type",
        "plate_steel_type",
        "bolt_fabrication_standard",
        "bolt_fabrication_standard_web",
        "bolt_fabrication_standard_flange",
        "bolt_description",
        "bolt_shape",
        "bolt_shape_web",
        "bolt_shape_flange",
    )
    @classmethod
    def normalize_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Text material fields cannot be empty.")
        return normalized

    @field_validator("bolt_thread_condition")
    @classmethod
    def validate_bolt_thread_condition(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"N", "X"}:
            raise ValueError("materials.bolt_thread_condition must be 'N' or 'X'.")
        return normalized


class BeamBeamMomentBoltedGeometry(StrictModel):
    splice_gap: Quantity
    flange_plate_top_thickness: Quantity
    flange_plate_top_width: Quantity
    flange_plate_top_length: Quantity
    flange_plate_bottom_thickness: Quantity
    flange_plate_bottom_width: Quantity
    flange_plate_bottom_length: Quantity
    web_plate_thickness: Quantity
    web_plate_height: Quantity
    web_plate_length: Quantity
    flange_bolt_gage: Quantity
    flange_bolt_pitch: Quantity
    flange_bolt_pitch_secondary: Quantity | None = None
    flange_bolt_edge_distance_longitudinal: Quantity
    flange_bolt_edge_distance_transverse: Quantity
    flange_bolt_rows_per_side: int
    flange_bolt_lines: int
    web_bolt_gage: Quantity
    web_bolt_pitch: Quantity
    web_bolt_edge_distance: Quantity
    web_bolt_edge_distance_x1: Quantity | None = None
    web_bolt_edge_distance_x2: Quantity | None = None
    web_bolt_edge_distance_y1: Quantity | None = None
    web_bolt_edge_distance_y2: Quantity | None = None
    web_bolt_edge_distance_y3: Quantity | None = None
    flange_bolt_edge_distance_x1: Quantity | None = None
    flange_bolt_edge_distance_x2: Quantity | None = None
    flange_bolt_edge_distance_z1: Quantity | None = None
    flange_bolt_edge_distance_z2: Quantity | None = None
    web_bolt_rows_per_side: int
    web_bolt_lines: int
    web_bolt_tightening_type: str | None = None
    flange_bolt_tightening_type: str | None = None
    beam_surface_condition: str | None = None
    beam_atmospheric_condition: str | None = None
    beam_length_tolerance: Quantity
    web_plate_surface_condition: str | None = None
    web_plate_atmospheric_condition: str | None = None
    flange_plate_surface_condition: str | None = None
    flange_plate_atmospheric_condition: str | None = None

    @field_validator("flange_bolt_lines", "web_bolt_rows_per_side", "web_bolt_lines")
    @classmethod
    def validate_positive_counts(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Bolt layout integer fields must be >= 1.")
        return value

    @field_validator("flange_bolt_rows_per_side")
    @classmethod
    def validate_flange_rows_per_side(cls, value: int) -> int:
        if value < 2:
            raise ValueError("geometry.flange_bolt_rows_per_side must be >= 2.")
        if value % 2 != 0:
            raise ValueError("geometry.flange_bolt_rows_per_side must be an even number (2, 4, 6, ...).")
        return value

    @field_validator(
            "beam_surface_condition",
            "web_plate_surface_condition",
            "flange_plate_surface_condition",
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
        "beam_atmospheric_condition",
        "web_plate_atmospheric_condition",
        "flange_plate_atmospheric_condition",
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

    @field_validator("web_bolt_tightening_type", "flange_bolt_tightening_type")
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


class BeamBeamMomentBoltedLoads(StrictModel):
    moment_right_end: Quantity
    moment_left_end: Quantity
    shear_right_end: Quantity
    shear_left_end: Quantity
    axial_right_end: Quantity
    axial_left_end: Quantity


class BeamBeamMomentBoltedDesignFactors(StrictModel):
    phi_bolt_tension: float
    phi_bolt_shear: float
    phi_plate_yielding: float
    phi_plate_rupture: float
    phi_block_shear: float
    phi_slip_critical: float | None = None

    @field_validator(
        "phi_bolt_tension",
        "phi_bolt_shear",
        "phi_plate_yielding",
        "phi_plate_rupture",
        "phi_block_shear",
        "phi_slip_critical",
    )
    @classmethod
    def validate_phi_range(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if not (0.0 < value <= 1.0):
            raise ValueError("Resistance factor phi must be in (0, 1].")
        return value


class BeamBeamMomentBoltedCase(CaseBase):
    connection_family: Literal["Fully_Restrained_Moment"]
    connection_type: Literal["bbmb_splice"]
    sections: BeamBeamMomentBoltedSections
    materials: BeamBeamMomentBoltedMaterials
    geometry: BeamBeamMomentBoltedGeometry
    loads: BeamBeamMomentBoltedLoads
    design_factors: BeamBeamMomentBoltedDesignFactors

    @model_validator(mode="after")
    def validate_units(self) -> "BeamBeamMomentBoltedCase":
        if self.materials.weld_fexx is not None:
            validate_quantity_unit(
                self.materials.weld_fexx,
                "stress",
                self.units_system,
                "materials.weld_fexx",
            )
        for field_name in (
            "splice_gap",
            "flange_plate_top_thickness",
            "flange_plate_top_width",
            "flange_plate_top_length",
            "flange_plate_bottom_thickness",
            "flange_plate_bottom_width",
            "flange_plate_bottom_length",
            "web_plate_thickness",
            "web_plate_height",
            "web_plate_length",
            "flange_bolt_gage",
            "flange_bolt_pitch",
            "flange_bolt_pitch_secondary",
            "flange_bolt_edge_distance_longitudinal",
            "flange_bolt_edge_distance_transverse",
            "flange_bolt_edge_distance_x1",
            "flange_bolt_edge_distance_x2",
            "flange_bolt_edge_distance_z1",
            "flange_bolt_edge_distance_z2",
            "web_bolt_gage",
            "web_bolt_pitch",
            "web_bolt_edge_distance",
            "web_bolt_edge_distance_x1",
            "web_bolt_edge_distance_x2",
            "web_bolt_edge_distance_y1",
            "web_bolt_edge_distance_y2",
            "web_bolt_edge_distance_y3",
            "beam_length_tolerance",
        ):
            value = getattr(self.geometry, field_name)
            if value is not None:
                validate_quantity_unit(
                    value,
                    "length",
                    self.units_system,
                    f"geometry.{field_name}",
                )
        for field_name in ("shear_right_end", "shear_left_end", "axial_right_end", "axial_left_end"):
            value = getattr(self.loads, field_name)
            validate_quantity_unit(
                value,
                "force",
                self.units_system,
                f"loads.{field_name}",
            )
        expected_moment_unit = "kip-in" if self.units_system == UnitSystem.US else "kN-mm"
        for field_name in ("moment_right_end", "moment_left_end"):
            value = getattr(self.loads, field_name)
            if value.unit != expected_moment_unit:
                raise ValueError(
                    f"Invalid unit at 'loads.{field_name}'. "
                    f"Expected '{expected_moment_unit}' for {self.units_system.value}."
                )
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
    with input_path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    return parse_input_case(payload)
