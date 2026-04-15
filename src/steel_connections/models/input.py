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
    weld_leg_size_w: Quantity | None = None
    end_plate_beam_web_weld_type: str | None = None
    end_plate_beam_web_weld_length_lwe: Quantity | None = None
    end_plate_beam_web_weld_thickness_twe: Quantity | None = None
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

    @field_validator("continuity_plate_weld_type", "end_plate_beam_web_weld_type")
    @classmethod
    def normalize_weld_type_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        return normalized

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
    pu_viga: Quantity | None = None
    pu_columna: Quantity | None = None
    probable_moment_column_face: Quantity | None = None
    probable_moment_plastic_hinge: Quantity | None = None
    shear_plastic_hinge: Quantity | None = None
    beam_gravity_shear_between_hinges: Quantity | None = None
    beam_gravity_shear_face_segment: Quantity | None = None
    required_connection_shear: Quantity | None = None
    required_beam_shear: Quantity | None = None
    required_web_weld_force: Quantity | None = None
    panel_zone_demand: Quantity | None = None


class AISC358MomentDesignFactors(StrictModel):
    phi_flange_tension: float | None = None
    phi_flange_weld: float | None = None
    phi_d: float | None = None
    phi_n: float | None = None
    ry: float | None = None
    member_ductility_demand_beam: str | None = None
    member_ductility_demand_column: str | None = None
    column_beam_moment_ratio_minimum: float | None = None

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

    @field_validator("member_ductility_demand_beam", "member_ductility_demand_column")
    @classmethod
    def validate_member_ductility_demand(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in {"high", "moderate"}:
            raise ValueError("member_ductility_demand_* must be 'high' or 'moderate'.")
        return normalized

    @field_validator("column_beam_moment_ratio_minimum")
    @classmethod
    def validate_moment_ratio_minimum(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if value <= 0.0:
            raise ValueError("column_beam_moment_ratio_minimum must be > 0.")
        return value


class AISC358MomentProcedure(StrictModel):
    beam_plastic_section_modulus_ze: Quantity | None = None
    beam_span_between_plastic_hinges_lh: Quantity | None = None
    yield_line_parameter_yp: Quantity | None = None
    column_yield_line_parameter_yc_unstiffened: Quantity | None = None
    column_yield_line_parameter_yc_stiffened: Quantity | None = None
    tension_bolt_line_distances: list[Quantity] | None = None
    beam_available_shear_strength: Quantity | None = None
    flange_weld_available_strength: Quantity | None = None
    web_weld_available_strength: Quantity | None = None
    continuity_plate_available_strength: Quantity | None = None
    panel_zone_capacity: Quantity | None = None
    column_beam_moment_ratio: float | None = None


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
            "weld_leg_size_w",
            "end_plate_beam_web_weld_length_lwe",
            "end_plate_beam_web_weld_thickness_twe",
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
        if self.loads.required_connection_shear is not None:
            validate_quantity_unit(
                self.loads.required_connection_shear,
                "force",
                self.units_system,
                "loads.required_connection_shear",
            )
        for field_name in (
            "pu_viga",
            "pu_columna",
            "shear_plastic_hinge",
            "beam_gravity_shear_between_hinges",
            "beam_gravity_shear_face_segment",
            "required_beam_shear",
            "required_web_weld_force",
            "panel_zone_demand",
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
            if self.procedure.tension_bolt_line_distances is not None:
                for idx, value in enumerate(self.procedure.tension_bolt_line_distances):
                    validate_quantity_unit(
                        value,
                        "length",
                        self.units_system,
                        f"procedure.tension_bolt_line_distances[{idx}]",
                    )
            for field_name in (
                "beam_available_shear_strength",
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
            if (
                self.procedure.column_beam_moment_ratio is not None
                and self.procedure.column_beam_moment_ratio <= 0.0
            ):
                raise ValueError("procedure.column_beam_moment_ratio must be > 0.")
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
    Union[AISC358MomentCase, DG1BasePlateCase],
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
