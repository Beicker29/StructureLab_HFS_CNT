from __future__ import annotations

from copy import deepcopy
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
from steel_connections.models.units import Quantity


def _normalize_moment_geometry_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    if normalized.get("connection_family") != "moment_prequalified":
        return normalized

    geometry = normalized.get("geometry")
    if not isinstance(geometry, dict):
        return normalized

    grouped_aliases: dict[str, list[str]] = {
        "beam": ["beam", "viga"],
        "column": ["column", "columna"],
        "end_plate": ["end_plate", "placa_extremo", "placa_extrema"],
        "continuity_plate": ["continuity_plate", "platina_continuidad", "platinas_continuidad"],
        "stiffener": ["stiffener", "rigidizador"],
        "bolts": ["bolts", "pernos"],
        "welds": ["welds", "soldaduras"],
    }
    all_group_keys = {alias for aliases in grouped_aliases.values() for alias in aliases}
    has_grouped_blocks = any(isinstance(geometry.get(group_key), dict) for group_key in all_group_keys)
    if not has_grouped_blocks:
        return normalized

    # Keep any legacy flat geometry fields unless overwritten by grouped blocks.
    flat_geometry: dict[str, Any] = {
        key: value for key, value in geometry.items() if key not in all_group_keys
    }

    def _group_block(group_name: str) -> dict[str, Any]:
        for alias in grouped_aliases[group_name]:
            value = geometry.get(alias)
            if isinstance(value, dict):
                return value
        return {}

    mapping: dict[str, tuple[str, ...]] = {
        "beam": (
            "beam_flange_area",
            "beam_clear_span_length",
            "beam_shear_connector_free_length_from_column_face",
        ),
        "column": (
            "column_end_distance_to_beam_flange",
            "column_slab_connection_condition",
        ),
        "end_plate": ("end_plate_width", "end_plate_thickness", "de", "pb", "pfo", "pfi"),
        "continuity_plate": ("continuity_plate_thickness", "continuity_plate_weld_type"),
        "stiffener": ("stiffener_height", "stiffener_thickness", "stiffener_length"),
        "bolts": (
            "bolt_diameter",
            "bolt_gage",
            "bolt_tightening_type",
            "clear_distance_end_plate",
            "clear_distance_column_flange",
        ),
        "welds": (
            "weld_leg_size_w",
            "weld_effective_area",
            "end_plate_beam_web_weld_type",
            "end_plate_beam_web_weld_length_lwe",
            "end_plate_beam_web_weld_thickness_twe",
        ),
    }
    for group_name, field_names in mapping.items():
        block = _group_block(group_name)
        if group_name == "beam":
            if "clear_span_length" in block and "beam_clear_span_length" not in block:
                flat_geometry["beam_clear_span_length"] = block["clear_span_length"]
            if "luz_libre" in block and "beam_clear_span_length" not in block:
                flat_geometry["beam_clear_span_length"] = block["luz_libre"]
            if "luz_libre_viga" in block and "beam_clear_span_length" not in block:
                flat_geometry["beam_clear_span_length"] = block["luz_libre_viga"]
            if (
                "shear_connector_free_length_from_column_face" in block
                and "beam_shear_connector_free_length_from_column_face" not in block
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face"] = block[
                    "shear_connector_free_length_from_column_face"
                ]
            if (
                "longitud_sin_conectores_desde_cara_columna" in block
                and "beam_shear_connector_free_length_from_column_face" not in block
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face"] = block[
                    "longitud_sin_conectores_desde_cara_columna"
                ]
        if group_name == "column":
            if "slab_connection_condition" in block and "column_slab_connection_condition" not in block:
                flat_geometry["column_slab_connection_condition"] = block["slab_connection_condition"]
            if "union_columna_losa" in block and "column_slab_connection_condition" not in block:
                flat_geometry["column_slab_connection_condition"] = block["union_columna_losa"]
        if group_name == "continuity_plate":
            if "weld_type" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["weld_type"]
            if "tipo_soldadura" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["tipo_soldadura"]
        if group_name == "welds":
            if "continuity_plate_weld_type" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["continuity_plate_weld_type"]
            if "weld_type_continuity_plate" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["weld_type_continuity_plate"]
            if "end_plate_beam_web_weld_type" in block and "end_plate_beam_web_weld_type" not in flat_geometry:
                flat_geometry["end_plate_beam_web_weld_type"] = block["end_plate_beam_web_weld_type"]
            if "weld_type_end_plate_beam_web" in block and "end_plate_beam_web_weld_type" not in flat_geometry:
                flat_geometry["end_plate_beam_web_weld_type"] = block["weld_type_end_plate_beam_web"]
            if (
                "tipo_soldadura_end_plate_beam_web" in block
                and "end_plate_beam_web_weld_type" not in flat_geometry
            ):
                flat_geometry["end_plate_beam_web_weld_type"] = block["tipo_soldadura_end_plate_beam_web"]
            if (
                "end_plate_beam_web_weld_length_lwe" in block
                and "end_plate_beam_web_weld_length_lwe" not in flat_geometry
            ):
                flat_geometry["end_plate_beam_web_weld_length_lwe"] = block["end_plate_beam_web_weld_length_lwe"]
            if "lwe" in block and "end_plate_beam_web_weld_length_lwe" not in flat_geometry:
                flat_geometry["end_plate_beam_web_weld_length_lwe"] = block["lwe"]
            if (
                "end_plate_beam_web_weld_thickness_twe" in block
                and "end_plate_beam_web_weld_thickness_twe" not in flat_geometry
            ):
                flat_geometry["end_plate_beam_web_weld_thickness_twe"] = block["end_plate_beam_web_weld_thickness_twe"]
            if "twe" in block and "end_plate_beam_web_weld_thickness_twe" not in flat_geometry:
                flat_geometry["end_plate_beam_web_weld_thickness_twe"] = block["twe"]
        if group_name == "bolts":
            if "tightening_type" in block and "bolt_tightening_type" not in flat_geometry:
                flat_geometry["bolt_tightening_type"] = block["tightening_type"]
            if "tipo_apriete" in block and "bolt_tightening_type" not in flat_geometry:
                flat_geometry["bolt_tightening_type"] = block["tipo_apriete"]
            if "bolt_tightening_type" in block:
                flat_geometry["bolt_tightening_type"] = block["bolt_tightening_type"]
        for field_name in field_names:
            if field_name in block:
                flat_geometry[field_name] = block[field_name]

    # Move bolt metadata to materials for catalog resolution.
    bolt_block = _group_block("bolts")
    materials = normalized.get("materials")
    if not isinstance(materials, dict):
        materials = {}
        normalized["materials"] = materials
    if "bolt_shape" in bolt_block and not materials.get("bolt_shape"):
        materials["bolt_shape"] = bolt_block["bolt_shape"]
    if "bolt_thread_condition" in bolt_block and not materials.get("bolt_thread_condition"):
        materials["bolt_thread_condition"] = bolt_block["bolt_thread_condition"]

    normalized["geometry"] = flat_geometry
    return normalized


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
        case.geometry.beam_shear_connector_free_length_from_column_face,
        "geometry.beam_shear_connector_free_length_from_column_face",
        "AISC 358-22 Section 2.3.4",
    )
    _require_quantity(
        case.geometry.beam_clear_span_length,
        "geometry.beam_clear_span_length",
        "AISC 358-22 Section 2.3.4",
    )
    _require_text(
        case.geometry.column_slab_connection_condition,
        "geometry.column_slab_connection_condition",
        "AISC 358-22 Section 2.3.4",
    )
    _require_quantity(
        case.geometry.continuity_plate_thickness,
        "geometry.continuity_plate_thickness",
        "AISC 358-22 Section 6.7",
    )
    _require_text(
        case.geometry.end_plate_beam_web_weld_type,
        "geometry.end_plate_beam_web_weld_type",
        "AISC 358-22 Section 6.7",
    )
    _require_quantity(
        case.geometry.end_plate_beam_web_weld_length_lwe,
        "geometry.end_plate_beam_web_weld_length_lwe",
        "AISC 358-22 Section 6.7",
    )
    weld_type_end_plate_web = (case.geometry.end_plate_beam_web_weld_type or "").strip().lower().replace("-", "_")
    if weld_type_end_plate_web in {"double_sided_fillet", "single_sided_fillet", "single_sided_fille"}:
        _require_quantity(
            case.geometry.end_plate_beam_web_weld_thickness_twe,
            "geometry.end_plate_beam_web_weld_thickness_twe",
            "AISC 358-22 Section 6.7",
        )
    _require_quantity(
        case.materials.weld_fexx,
        "materials.weld_fexx",
        "AISC 358-22 Section 6.7",
    )
    if case.geometry.stiffener_height is not None:
        _raise_validation_error(
            message=(
                "Input 'geometry.stiffener_height' is no longer allowed. "
                "It is now derived automatically as hst = pfo + de."
            ),
            missing_fields=["geometry.stiffener_height"],
            source_document="AISC 358-22 Section 6.7",
        )
    if case.geometry.stiffener_length is not None:
        _raise_validation_error(
            message=(
                "Input 'geometry.stiffener_length' is no longer allowed. "
                "It is now derived automatically as Lst = hst/tan(30 deg)."
            ),
            missing_fields=["geometry.stiffener_length"],
            source_document="AISC 358-22 Section 6.7",
        )
    de = case.geometry.de
    pfo = case.geometry.pfo
    if de is None or pfo is None:
        _raise_validation_error(
            message="Inputs 'geometry.de' and 'geometry.pfo' are required to derive stiffener_height = pfo + de.",
            missing_fields=["geometry.de", "geometry.pfo"],
            source_document="AISC 358-22 Section 6.7",
        )
    case.geometry.stiffener_height = Quantity(
        value=pfo.value + de.value,
        unit=pfo.unit,
    )
    tan_30 = 0.5773502691896257
    case.geometry.stiffener_length = Quantity(
        value=case.geometry.stiffener_height.value / tan_30,
        unit=case.geometry.stiffener_height.unit,
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
        "geometry.bolts.bolt_thread_condition",
        "data/materials.xlsx",
    ).upper()
    if bolt_thread_condition == "N":
        case.materials.bolt_fnv = bolt_strength["fnv_threads_not_excluded"]  # type: ignore[assignment]
    elif bolt_thread_condition == "X":
        case.materials.bolt_fnv = bolt_strength["fnv_threads_excluded"]  # type: ignore[assignment]
    else:
        _raise_validation_error(
            message=(
                "Invalid input 'geometry.bolts.bolt_thread_condition'. "
                "Expected 'N' (threads not excluded) or 'X' (threads excluded)."
            ),
            missing_fields=["geometry.bolts.bolt_thread_condition"],
            source_document="data/materials.xlsx",
        )

    # Bolt geometry is sourced from sections.xlsx/Perno.
    bolt_shape = _require_text(case.materials.bolt_shape, "geometry.bolts.bolt_shape", "data/sections.xlsx")
    bolt_geom = get_bolt_section_properties(bolt_shape=bolt_shape, unit_system=case.units_system)
    geom_standard = str(bolt_geom["fabrication_standard"])
    geom_description = str(bolt_geom["classification"])
    if normalize_text(geom_standard) != normalize_text(bolt_standard):
        _raise_validation_error(
            message=(
                f"Mismatch between materials.bolt_fabrication_standard='{bolt_standard}' and "
                f"sections/Perno standard '{geom_standard}' for shape '{bolt_shape}'."
            ),
            missing_fields=["materials.bolt_fabrication_standard", "geometry.bolts.bolt_shape"],
            source_document="data/sections.xlsx",
        )
    if normalize_text(geom_description) != normalize_text(bolt_description):
        _raise_validation_error(
            message=(
                f"Mismatch between materials.bolt_description='{bolt_description}' and "
                f"sections/Perno classification '{geom_description}' for shape '{bolt_shape}'."
            ),
            missing_fields=["materials.bolt_description", "geometry.bolts.bolt_shape"],
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
                missing_fields=["geometry.bolt_diameter", "geometry.bolts.bolt_shape"],
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
    normalized_payload = _normalize_moment_geometry_payload(payload)
    try:
        case = parse_input_case(normalized_payload)
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
