from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from steel_connections.data.materials_repository import (
    get_bolt_strength_properties,
    get_hrs_steel_properties,
    get_plate_steel_properties,
)
from steel_connections.data.sections_repository import get_bolt_section_properties
from steel_connections.data.xlsx_sheet_reader import normalize_text
from steel_connections.models.errors import ErrorCode, Stage, StructuredEngineException, StructuredError
from steel_connections.models.input import AISC358MomentCase, InputCase, parse_input_case


def _raise_validation_error(
    *,
    message: str,
    missing_fields: list[str] | None = None,
    source_document: str | None = None,
) -> None:
    raise StructuredEngineException(
        StructuredError(
            error_code=ErrorCode.VALIDATION_ERROR,
            stage=Stage.VALIDATE,
            rule_id=None,
            missing_fields=missing_fields,
            message=message,
            source_document=source_document,
        )
    )


def _require_text(value: str | None, field_path: str, source_document: str) -> str:
    if value is None or not value.strip():
        _raise_validation_error(
            message=f"Required input '{field_path}' is missing for catalog-driven properties.",
            missing_fields=[field_path],
            source_document=source_document,
        )
    return value.strip()


def _require_quantity(value: object | None, field_path: str, source_document: str) -> None:
    if value is None:
        _raise_validation_error(
            message=f"Required input '{field_path}' is missing for applicable Chapter 6 geometry.",
            missing_fields=[field_path],
            source_document=source_document,
        )


def _resolve_catalog_driven_properties(case: AISC358MomentCase) -> None:
    # Profiles: Fy/Fu are always sourced from materials.xlsx/HRS.
    profile_type = _require_text(case.materials.profile_steel_type, "materials.profile_steel_type", "data/materials.xlsx")
    profile_props = get_hrs_steel_properties(steel_type=profile_type, unit_system=case.units_system)
    case.materials.beam_fy = profile_props["fy"]  # type: ignore[assignment]
    case.materials.beam_fu = profile_props["fu"]  # type: ignore[assignment]
    case.materials.column_fy = profile_props["fy"]  # type: ignore[assignment]
    case.materials.column_fu = profile_props["fu"]  # type: ignore[assignment]

    if case.connection_type not in {"bueep_4e", "bseep_4es", "bseep_8es"}:
        return

    # Geometry parameters used in detailed audit diagram and Chapter 6 bolt layout traceability.
    _require_quantity(case.geometry.de, "geometry.de", "AISC 358-22 Section 6.7")
    _require_quantity(case.geometry.pb, "geometry.pb", "AISC 358-22 Section 6.7")
    _require_quantity(case.geometry.pfo, "geometry.pfo", "AISC 358-22 Section 6.7")
    _require_quantity(case.geometry.pfi, "geometry.pfi", "AISC 358-22 Section 6.7")
    _require_quantity(
        case.geometry.continuity_plate_thickness,
        "geometry.continuity_plate_thickness",
        "AISC 358-22 Section 6.7",
    )

    # Plates: Fy/Fu for end plate and stiffener are sourced from materials.xlsx/Platinas.
    plate_type = _require_text(case.materials.plate_steel_type, "materials.plate_steel_type", "data/materials.xlsx")
    plate_props = get_plate_steel_properties(steel_type=plate_type, unit_system=case.units_system)
    case.materials.end_plate_fy = plate_props["fy"]  # type: ignore[assignment]
    case.materials.end_plate_fu = plate_props["fu"]  # type: ignore[assignment]
    case.materials.stiffener_fy = plate_props["fy"]  # type: ignore[assignment]

    # Bolt strength is sourced from materials.xlsx/Pernos.
    bolt_standard = _require_text(
        case.materials.bolt_fabrication_standard,
        "materials.bolt_fabrication_standard",
        "data/materials.xlsx",
    )
    bolt_description = _require_text(
        case.materials.bolt_description,
        "materials.bolt_description",
        "data/materials.xlsx",
    )
    bolt_strength = get_bolt_strength_properties(
        description=bolt_description,
        specification=bolt_standard,
        unit_system=case.units_system,
    )
    case.materials.bolt_fnt = bolt_strength["fnt"]  # type: ignore[assignment]
    bolt_thread_condition = _require_text(
        case.materials.bolt_thread_condition,
        "materials.bolt_thread_condition",
        "data/materials.xlsx",
    ).upper()
    if bolt_thread_condition == "N":
        case.materials.bolt_fnv = bolt_strength["fnv_threads_not_excluded"]  # type: ignore[assignment]
    elif bolt_thread_condition == "X":
        case.materials.bolt_fnv = bolt_strength["fnv_threads_excluded"]  # type: ignore[assignment]
    else:
        _raise_validation_error(
            message=(
                "Invalid input 'materials.bolt_thread_condition'. "
                "Expected 'N' (threads not excluded) or 'X' (threads excluded)."
            ),
            missing_fields=["materials.bolt_thread_condition"],
            source_document="data/materials.xlsx",
        )

    # Bolt geometry is sourced from sections.xlsx/Perno.
    bolt_shape = _require_text(case.materials.bolt_shape, "materials.bolt_shape", "data/sections.xlsx")
    bolt_geom = get_bolt_section_properties(bolt_shape=bolt_shape, unit_system=case.units_system)
    geom_standard = str(bolt_geom["fabrication_standard"])
    geom_description = str(bolt_geom["classification"])
    if normalize_text(geom_standard) != normalize_text(bolt_standard):
        _raise_validation_error(
            message=(
                f"Mismatch between materials.bolt_fabrication_standard='{bolt_standard}' and "
                f"sections/Perno standard '{geom_standard}' for shape '{bolt_shape}'."
            ),
            missing_fields=["materials.bolt_fabrication_standard", "materials.bolt_shape"],
            source_document="data/sections.xlsx",
        )
    if normalize_text(geom_description) != normalize_text(bolt_description):
        _raise_validation_error(
            message=(
                f"Mismatch between materials.bolt_description='{bolt_description}' and "
                f"sections/Perno classification '{geom_description}' for shape '{bolt_shape}'."
            ),
            missing_fields=["materials.bolt_description", "materials.bolt_shape"],
            source_document="data/sections.xlsx",
        )

    derived_db = bolt_geom["diameter_nominal"]  # type: ignore[assignment]
    if case.geometry.bolt_diameter is not None:
        current = case.geometry.bolt_diameter
        if current.unit != derived_db.unit or abs(current.value - derived_db.value) > 1e-9:
            _raise_validation_error(
                message=(
                    "Input 'geometry.bolt_diameter' must not contradict the selected bolt shape. "
                    f"Expected {derived_db.value} {derived_db.unit} from sections/Perno."
                ),
                missing_fields=["geometry.bolt_diameter", "materials.bolt_shape"],
                source_document="data/sections.xlsx",
            )
    case.geometry.bolt_diameter = derived_db

    # Maintain legacy field used by Step 5 (no hidden default because it is derived from selected standard).
    case.materials.bolt_grade = bolt_standard


def load_input_payload(path: str | Path) -> dict[str, Any]:
    input_path = Path(path)
    try:
        with input_path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except json.JSONDecodeError as exc:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=None,
                message=f"Invalid JSON file: {exc}",
                source_document=None,
            )
        ) from exc
    except OSError as exc:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=None,
                message=f"Cannot read input file: {exc}",
                source_document=None,
            )
        ) from exc


def validate_case(case: InputCase) -> None:
    primary_doc = case.design_code_context.primary_document.lower()
    if case.connection_family == "moment_prequalified" and "358" not in primary_doc:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["design_code_context.primary_document"],
                message="Moment prequalified cases require AISC 358 as primary document.",
                source_document=case.design_code_context.primary_document,
            )
        )
    if case.connection_family == "base_plate_anchor_rod" and "design guide 1" not in primary_doc:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["design_code_context.primary_document"],
                message="DG1 base plate cases require Design Guide 1 as primary document.",
                source_document=case.design_code_context.primary_document,
            )
        )


def parse_and_validate_payload(payload: dict[str, Any]) -> InputCase:
    try:
        case = parse_input_case(payload)
    except ValidationError as exc:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=None,
                message=f"Input validation error: {exc}",
                source_document=None,
            )
        ) from exc
    validate_case(case)
    if isinstance(case, AISC358MomentCase):
        _resolve_catalog_driven_properties(case)
    return case


def parse_and_validate_file(path: str | Path) -> InputCase:
    payload = load_input_payload(path)
    return parse_and_validate_payload(payload)
