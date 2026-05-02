from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from steel_connections.data.materials_repository import (
    get_bolt_strength_properties,
    get_hrs_steel_properties,
    get_plate_steel_properties,
)
from steel_connections.data.sections_repository import get_beam_profile_properties, get_bolt_section_properties
from steel_connections.data.xlsx_sheet_reader import normalize_text
from steel_connections.models.errors import ErrorCode, Stage, StructuredEngineException, StructuredError
from steel_connections.models.input import AISC358MomentCase, InputCase, parse_input_case
from steel_connections.models.units import Quantity


def _normalize_connection_family_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    family = normalized.get("connection_family")
    if not isinstance(family, str):
        return normalized
    family_aliases = {
        "Moment_Prequalified": "moment_prequalified",
        "moment_non_prequalified": "Fully_Restrained_Moment",
    }
    normalized["connection_family"] = family_aliases.get(family, family)
    return normalized


def _normalize_moment_geometry_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    if normalized.get("connection_family") != "moment_prequalified":
        return normalized

    geometry = normalized.get("geometry")
    if not isinstance(geometry, dict):
        return normalized

    if "beam_connection_sides" in geometry:
        design_factors = normalized.get("design_factors")
        if not isinstance(design_factors, dict):
            design_factors = {}
            normalized["design_factors"] = design_factors
        if "beam_connection_sides" not in design_factors:
            design_factors["beam_connection_sides"] = geometry["beam_connection_sides"]
        geometry = deepcopy(geometry)
        geometry.pop("beam_connection_sides", None)
        normalized["geometry"] = geometry

    grouped_aliases: dict[str, list[str]] = {
        "beam": ["beam", "viga"],
        "beam_right": ["beam_right", "beam_der", "viga_derecha"],
        "beam_left": ["beam_left", "beam_izq", "viga_izquierda"],
        "column": ["column", "columna"],
        "end_plate": ["end_plate", "placa_extremo", "placa_extrema"],
        "continuity_plate": ["continuity_plate", "platina_continuidad", "platinas_continuidad"],
        "doubler_plate": [
            "doubler_plate",
            "platina_dobladora",
            "platina_enchape_alma",
            "platina_de_enchape_del_alma",
            "placa_dobladora",
            "dobladora",
        ],
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
            "beam_clear_span_length_der",
            "beam_clear_span_length_izq",
            "beam_shear_connector_free_length_from_column_face_der",
            "beam_shear_connector_free_length_from_column_face_izq",
            "beam_flange_area",
            "beam_clear_span_length",
            "beam_shear_connector_free_length_from_column_face",
        ),
        "column": (
            "column_end_distance_to_beam_flange",
            "column_slab_connection_condition",
            "panel_zone_inelastic_deformation_considered",
            "panel_zone_equation_package",
            "hb_col",
            "ht_col",
        ),
        "end_plate": ("end_plate_width", "end_plate_thickness", "de", "pb", "pfo", "pfi"),
        "continuity_plate": (
            "continuity_plate_thickness",
            "continuity_plate_width_b1",
            "continuity_plate_count",
            "continuity_plate_enabled",
            "continuity_plate_weld_type",
            "continuity_plate_weld_type_col",
            "continuity_plate_web_weld_type_col",
            "t_w5_col",
            "w_w5_col",
            "nl_w5_col",
            "L_gap_w5_col",
            "kds_w5_col",
            "t_w6_col",
            "w_w6_col",
            "nl_w6_col",
            "L_gap_w6_col",
            "kds_w6_col",
        ),
        "doubler_plate": (
            "doubler_plate_thickness",
            "doubler_plate_count",
            "doubler_plate_enabled",
            "doubler_plate_web_plug_weld_type",
            "doubler_plate_web_plug_weld_size",
            "doubler_plate_web_plug_weld_lines_nl",
        ),
        "stiffener": ("stiffener_height", "stiffener_thickness", "stiffener_length"),
        "bolts": (
            "bolt_diameter",
            "bolt_gage",
            "bolt_tightening_type",
            "clear_distance_end_plate",
            "clear_distance_column_flange",
        ),
        "welds": (
            "weld_effective_area",
            "end_plate_beam_web_weld_type",
            "end_plate_beam_web_weld_thickness_twe",
            "end_plate_beam_web_weld_lines_nl",
            "end_plate_stiffener_weld_type",
            "L_gap_w1",
            "end_plate_stiffener_weld_length_lst",
            "end_plate_stiffener_weld_size_wst",
            "end_plate_stiffener_weld_lines_nl",
            "beam_stiffener_weld_type",
            "L_gap_w2",
            "beam_stiffener_weld_length_lstw2",
            "beam_stiffener_weld_size_wst2",
            "beam_stiffener_weld_lines_nl_w2",
        ),
    }
    for group_name, field_names in mapping.items():
        block = _group_block(group_name)
        if group_name == "beam":
            beam_right_block = _group_block("beam_right")
            beam_left_block = _group_block("beam_left")
            if "connection_sides" in block and "beam_connection_sides" not in flat_geometry:
                flat_geometry["beam_connection_sides"] = block["connection_sides"]
            if "lados_conexion" in block and "beam_connection_sides" not in flat_geometry:
                flat_geometry["beam_connection_sides"] = block["lados_conexion"]
            if "beam_connection_sides" in block:
                flat_geometry["beam_connection_sides"] = block["beam_connection_sides"]

            def _map_side_block(side_block: dict[str, Any], *, side_suffix: str) -> None:
                if not side_block:
                    return
                clear_span_key = f"beam_clear_span_length_{side_suffix}"
                clear_connect_key = f"beam_shear_connector_free_length_from_column_face_{side_suffix}"
                if "clear_span_length" in side_block:
                    flat_geometry[clear_span_key] = side_block["clear_span_length"]
                if "luz_libre" in side_block and clear_span_key not in flat_geometry:
                    flat_geometry[clear_span_key] = side_block["luz_libre"]
                if "luz_libre_viga" in side_block and clear_span_key not in flat_geometry:
                    flat_geometry[clear_span_key] = side_block["luz_libre_viga"]
                if "clear_span_length_right" in side_block:
                    flat_geometry["beam_clear_span_length_der"] = side_block["clear_span_length_right"]
                if "clear_span_length_left" in side_block:
                    flat_geometry["beam_clear_span_length_izq"] = side_block["clear_span_length_left"]
                if "shear_connector_free_length_from_column_face" in side_block:
                    flat_geometry[clear_connect_key] = side_block["shear_connector_free_length_from_column_face"]
                if (
                    "longitud_sin_conectores_desde_cara_columna" in side_block
                    and clear_connect_key not in flat_geometry
                ):
                    flat_geometry[clear_connect_key] = side_block["longitud_sin_conectores_desde_cara_columna"]
                if "shear_connector_free_length_from_column_face_right" in side_block:
                    flat_geometry["beam_shear_connector_free_length_from_column_face_der"] = side_block[
                        "shear_connector_free_length_from_column_face_right"
                    ]
                if "shear_connector_free_length_from_column_face_left" in side_block:
                    flat_geometry["beam_shear_connector_free_length_from_column_face_izq"] = side_block[
                        "shear_connector_free_length_from_column_face_left"
                    ]

            _map_side_block(beam_right_block, side_suffix="der")
            _map_side_block(beam_left_block, side_suffix="izq")

            if "clear_span_length_der" in block and "beam_clear_span_length_der" not in flat_geometry:
                flat_geometry["beam_clear_span_length_der"] = block["clear_span_length_der"]
            if "luz_libre_der" in block and "beam_clear_span_length_der" not in flat_geometry:
                flat_geometry["beam_clear_span_length_der"] = block["luz_libre_der"]
            if (
                "shear_connector_free_length_from_column_face_der" in block
                and "beam_shear_connector_free_length_from_column_face_der" not in flat_geometry
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face_der"] = block[
                    "shear_connector_free_length_from_column_face_der"
                ]
            if (
                "longitud_sin_conectores_desde_cara_columna_der" in block
                and "beam_shear_connector_free_length_from_column_face_der" not in flat_geometry
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face_der"] = block[
                    "longitud_sin_conectores_desde_cara_columna_der"
                ]
            if "clear_span_length_izq" in block and "beam_clear_span_length_izq" not in flat_geometry:
                flat_geometry["beam_clear_span_length_izq"] = block["clear_span_length_izq"]
            if "luz_libre_izq" in block and "beam_clear_span_length_izq" not in flat_geometry:
                flat_geometry["beam_clear_span_length_izq"] = block["luz_libre_izq"]
            if (
                "shear_connector_free_length_from_column_face_izq" in block
                and "beam_shear_connector_free_length_from_column_face_izq" not in flat_geometry
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face_izq"] = block[
                    "shear_connector_free_length_from_column_face_izq"
                ]
            if (
                "longitud_sin_conectores_desde_cara_columna_izq" in block
                and "beam_shear_connector_free_length_from_column_face_izq" not in flat_geometry
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face_izq"] = block[
                    "longitud_sin_conectores_desde_cara_columna_izq"
                ]
            if "clear_span_length_right" in block and "beam_clear_span_length_der" not in flat_geometry:
                flat_geometry["beam_clear_span_length_der"] = block["clear_span_length_right"]
            if "clear_span_length_left" in block and "beam_clear_span_length_izq" not in flat_geometry:
                flat_geometry["beam_clear_span_length_izq"] = block["clear_span_length_left"]
            if (
                "shear_connector_free_length_from_column_face_right" in block
                and "beam_shear_connector_free_length_from_column_face_der" not in flat_geometry
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face_der"] = block[
                    "shear_connector_free_length_from_column_face_right"
                ]
            if (
                "shear_connector_free_length_from_column_face_left" in block
                and "beam_shear_connector_free_length_from_column_face_izq" not in flat_geometry
            ):
                flat_geometry["beam_shear_connector_free_length_from_column_face_izq"] = block[
                    "shear_connector_free_length_from_column_face_left"
                ]
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
            if (
                "panel_zone_inelastic_deformation_considered" in block
                and "panel_zone_inelastic_deformation_considered" not in flat_geometry
            ):
                flat_geometry["panel_zone_inelastic_deformation_considered"] = block[
                    "panel_zone_inelastic_deformation_considered"
                ]
            if (
                "consideracion_deformacion_inelastica_zona_panel" in block
                and "panel_zone_inelastic_deformation_considered" not in flat_geometry
            ):
                flat_geometry["panel_zone_inelastic_deformation_considered"] = block[
                    "consideracion_deformacion_inelastica_zona_panel"
                ]
            if (
                "considera_deformacion_inelastica_panel_zone" in block
                and "panel_zone_inelastic_deformation_considered" not in flat_geometry
            ):
                flat_geometry["panel_zone_inelastic_deformation_considered"] = block[
                    "considera_deformacion_inelastica_panel_zone"
                ]
            if "panel_zone_equation_package" in block and "panel_zone_equation_package" not in flat_geometry:
                flat_geometry["panel_zone_equation_package"] = block["panel_zone_equation_package"]
            if "paquete_wpzs" in block and "panel_zone_equation_package" not in flat_geometry:
                flat_geometry["panel_zone_equation_package"] = block["paquete_wpzs"]
            if "paquete_wpzs_col" in block and "panel_zone_equation_package" not in flat_geometry:
                flat_geometry["panel_zone_equation_package"] = block["paquete_wpzs_col"]
            if "paquete_ecuaciones_wpzs" in block and "panel_zone_equation_package" not in flat_geometry:
                flat_geometry["panel_zone_equation_package"] = block["paquete_ecuaciones_wpzs"]
            if "hb_col" in block and "hb_col" not in flat_geometry:
                flat_geometry["hb_col"] = block["hb_col"]
            if "h_b_col" in block and "hb_col" not in flat_geometry:
                flat_geometry["hb_col"] = block["h_b_col"]
            if "ht_col" in block and "ht_col" not in flat_geometry:
                flat_geometry["ht_col"] = block["ht_col"]
            if "h_t_col" in block and "ht_col" not in flat_geometry:
                flat_geometry["ht_col"] = block["h_t_col"]
        if group_name == "continuity_plate":
            if "continuity_plate_width_b1" in block and "continuity_plate_width_b1" not in flat_geometry:
                flat_geometry["continuity_plate_width_b1"] = block["continuity_plate_width_b1"]
            if "b1_pc_col" in block and "continuity_plate_width_b1" not in flat_geometry:
                flat_geometry["continuity_plate_width_b1"] = block["b1_pc_col"]
            if "continuity_plate_count" in block and "continuity_plate_count" not in flat_geometry:
                flat_geometry["continuity_plate_count"] = block["continuity_plate_count"]
            if "n_pc_col" in block and "continuity_plate_count" not in flat_geometry:
                flat_geometry["continuity_plate_count"] = block["n_pc_col"]
            if "continuity_plate_enabled" in block and "continuity_plate_enabled" not in flat_geometry:
                flat_geometry["continuity_plate_enabled"] = block["continuity_plate_enabled"]
            if "usar_platinas_continuidad" in block and "continuity_plate_enabled" not in flat_geometry:
                flat_geometry["continuity_plate_enabled"] = block["usar_platinas_continuidad"]
            if "use_continuity_plates" in block and "continuity_plate_enabled" not in flat_geometry:
                flat_geometry["continuity_plate_enabled"] = block["use_continuity_plates"]
            if "weld_type" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["weld_type"]
            if "tipo_soldadura" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["tipo_soldadura"]
            if "continuity_plate_weld_type_col" in block and "continuity_plate_weld_type_col" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type_col"] = block["continuity_plate_weld_type_col"]
            if "tipo_w5_col" in block and "continuity_plate_weld_type_col" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type_col"] = block["tipo_w5_col"]
            if "continuity_plate_web_weld_type_col" in block and "continuity_plate_web_weld_type_col" not in flat_geometry:
                flat_geometry["continuity_plate_web_weld_type_col"] = block["continuity_plate_web_weld_type_col"]
            if "tipo_w6_col" in block and "continuity_plate_web_weld_type_col" not in flat_geometry:
                flat_geometry["continuity_plate_web_weld_type_col"] = block["tipo_w6_col"]
            if "t_w5_col" in block and "t_w5_col" not in flat_geometry:
                flat_geometry["t_w5_col"] = block["t_w5_col"]
            if "w_w5_col" in block and "w_w5_col" not in flat_geometry:
                flat_geometry["w_w5_col"] = block["w_w5_col"]
            if "nl_w5_col" in block and "nl_w5_col" not in flat_geometry:
                flat_geometry["nl_w5_col"] = block["nl_w5_col"]
            if "L_gap_w5_col" in block and "L_gap_w5_col" not in flat_geometry:
                flat_geometry["L_gap_w5_col"] = block["L_gap_w5_col"]
            if "kds_w5_col" in block and "kds_w5_col" not in flat_geometry:
                flat_geometry["kds_w5_col"] = block["kds_w5_col"]
            if "t_w6_col" in block and "t_w6_col" not in flat_geometry:
                flat_geometry["t_w6_col"] = block["t_w6_col"]
            if "w_w6_col" in block and "w_w6_col" not in flat_geometry:
                flat_geometry["w_w6_col"] = block["w_w6_col"]
            if "nl_w6_col" in block and "nl_w6_col" not in flat_geometry:
                flat_geometry["nl_w6_col"] = block["nl_w6_col"]
            if "L_gap_w6_col" in block and "L_gap_w6_col" not in flat_geometry:
                flat_geometry["L_gap_w6_col"] = block["L_gap_w6_col"]
            if "kds_w6_col" in block and "kds_w6_col" not in flat_geometry:
                flat_geometry["kds_w6_col"] = block["kds_w6_col"]
        if group_name == "doubler_plate":
            if "doubler_plate_enabled" in block and "doubler_plate_enabled" not in flat_geometry:
                flat_geometry["doubler_plate_enabled"] = block["doubler_plate_enabled"]
            if "usar_dp_col" in block and "doubler_plate_enabled" not in flat_geometry:
                flat_geometry["doubler_plate_enabled"] = block["usar_dp_col"]
            if "use_doubler_plates" in block and "doubler_plate_enabled" not in flat_geometry:
                flat_geometry["doubler_plate_enabled"] = block["use_doubler_plates"]
            if "doubler_plate_thickness" in block and "doubler_plate_thickness" not in flat_geometry:
                flat_geometry["doubler_plate_thickness"] = block["doubler_plate_thickness"]
            if "t_dp_col" in block and "doubler_plate_thickness" not in flat_geometry:
                flat_geometry["doubler_plate_thickness"] = block["t_dp_col"]
            if "tdp_col" in block and "doubler_plate_thickness" not in flat_geometry:
                flat_geometry["doubler_plate_thickness"] = block["tdp_col"]
            if "doubler_plate_count" in block and "doubler_plate_count" not in flat_geometry:
                flat_geometry["doubler_plate_count"] = block["doubler_plate_count"]
            if "n_dp_col" in block and "doubler_plate_count" not in flat_geometry:
                flat_geometry["doubler_plate_count"] = block["n_dp_col"]
            if (
                "doubler_plate_web_plug_weld_type" in block
                and "doubler_plate_web_plug_weld_type" not in flat_geometry
            ):
                flat_geometry["doubler_plate_web_plug_weld_type"] = block["doubler_plate_web_plug_weld_type"]
            if "tipo_soldadura_plug" in block and "doubler_plate_web_plug_weld_type" not in flat_geometry:
                flat_geometry["doubler_plate_web_plug_weld_type"] = block["tipo_soldadura_plug"]
            if "tipo_w7_col" in block and "doubler_plate_web_plug_weld_type" not in flat_geometry:
                flat_geometry["doubler_plate_web_plug_weld_type"] = block["tipo_w7_col"]
            if (
                "doubler_plate_web_plug_weld_size" in block
                and "doubler_plate_web_plug_weld_size" not in flat_geometry
            ):
                flat_geometry["doubler_plate_web_plug_weld_size"] = block["doubler_plate_web_plug_weld_size"]
            if "t_wdp_plug" in block and "doubler_plate_web_plug_weld_size" not in flat_geometry:
                flat_geometry["doubler_plate_web_plug_weld_size"] = block["t_wdp_plug"]
            if "t_w7_col" in block and "doubler_plate_web_plug_weld_size" not in flat_geometry:
                flat_geometry["doubler_plate_web_plug_weld_size"] = block["t_w7_col"]
            if (
                "doubler_plate_web_plug_weld_lines_nl" in block
                and "doubler_plate_web_plug_weld_lines_nl" not in flat_geometry
            ):
                flat_geometry["doubler_plate_web_plug_weld_lines_nl"] = block[
                    "doubler_plate_web_plug_weld_lines_nl"
                ]
            if "nl_wdp_plug" in block and "doubler_plate_web_plug_weld_lines_nl" not in flat_geometry:
                flat_geometry["doubler_plate_web_plug_weld_lines_nl"] = block["nl_wdp_plug"]
            if "nl_w7_col" in block and "doubler_plate_web_plug_weld_lines_nl" not in flat_geometry:
                flat_geometry["doubler_plate_web_plug_weld_lines_nl"] = block["nl_w7_col"]
        if group_name == "welds":
            def _assign_from_aliases(target_key: str, source_block: dict[str, Any], aliases: tuple[str, ...]) -> None:
                if target_key in flat_geometry:
                    return
                for alias in aliases:
                    if alias in source_block:
                        flat_geometry[target_key] = source_block[alias]
                        return

            def _get_nested_weld_block(*aliases: str) -> dict[str, Any]:
                for alias in aliases:
                    nested = block.get(alias)
                    if isinstance(nested, dict):
                        return nested
                return {}

            # New grouped weld input style:
            # weld_1 = rigidizador con end plate
            # weld_2 = viga con rigidizador
            # weld_3 = viga (alma) con end plate
            # weld_4 = ala de viga con end plate
            weld_1 = _get_nested_weld_block("weld_1", "weld1", "soldadura_1", "soldadura1")
            weld_2 = _get_nested_weld_block("weld_2", "weld2", "soldadura_2", "soldadura2")
            weld_3 = _get_nested_weld_block("weld_3", "weld3", "soldadura_3", "soldadura3")
            weld_4 = _get_nested_weld_block("weld_4", "weld4", "soldadura_4", "soldadura4")
            weld_cp = _get_nested_weld_block(
                "weld_5",
                "weld5",
                "soldadura_5",
                "soldadura5",
                "weld_cp",
                "continuity_plate_weld",
                "weld_4_column",
                "soldadura_cp",
            )
            weld_cw = _get_nested_weld_block(
                "weld_6",
                "weld6",
                "soldadura_6",
                "soldadura6",
                "weld_cw",
                "continuity_plate_web_weld",
                "soldadura_cw",
            )
            weld_dp_plug = _get_nested_weld_block(
                "weld_7",
                "weld7",
                "soldadura_7",
                "soldadura7",
                "weld_dp_plug",
                "weld_dp_plug",
                "doubler_plate_plug_weld",
                "soldadura_plug_dp",
                "soldadura_plug_dobladora",
            )

            if weld_1:
                _assign_from_aliases(
                    "end_plate_stiffener_weld_type",
                    weld_1,
                    (
                        "end_plate_stiffener_weld_type",
                        "stiffener_weld_type",
                        "weld_type",
                        "tipo_soldadura_rigidizador",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "end_plate_stiffener_weld_length_lst",
                    weld_1,
                    (
                        "end_plate_stiffener_weld_length_lst",
                        "stiffener_weld_length_lst",
                        "l_st",
                        "length",
                        "l",
                    ),
                )
                _assign_from_aliases(
                    "end_plate_stiffener_weld_size_wst",
                    weld_1,
                    (
                        "end_plate_stiffener_weld_size_wst",
                        "stiffener_weld_size_wst",
                        "w_st",
                        "size",
                        "w",
                    ),
                )
                _assign_from_aliases(
                    "end_plate_stiffener_weld_lines_nl",
                    weld_1,
                    (
                        "end_plate_stiffener_weld_lines_nl",
                        "stiffener_weld_lines_nl",
                        "n_l",
                        "nl",
                        "lines",
                    ),
                )
                _assign_from_aliases(
                    "L_gap_w1_vgder",
                    weld_1,
                    ("L_gap_w1_vgder", "L_gap_w1", "l_gap_w1_vgder", "l_gap", "gap"),
                )
                _assign_from_aliases(
                    "L_gap_w1_vgizq",
                    weld_1,
                    ("L_gap_w1_vgizq", "L_gap_w1", "l_gap_w1_vgizq", "l_gap", "gap"),
                )
                _assign_from_aliases(
                    "kds_w1_vgder",
                    weld_1,
                    ("kds_w1_vgder",),
                )
                _assign_from_aliases(
                    "kds_w1_vgizq",
                    weld_1,
                    ("kds_w1_vgizq",),
                )

            if weld_2:
                _assign_from_aliases(
                    "beam_stiffener_weld_type",
                    weld_2,
                    (
                        "beam_stiffener_weld_type",
                        "stiffener_beam_weld_type",
                        "weld_type",
                        "tipo_soldadura_viga_rigidizador",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "beam_stiffener_weld_length_lstw2",
                    weld_2,
                    (
                        "beam_stiffener_weld_length_lstw2",
                        "stiffener_beam_weld_length_lstw2",
                        "l_st_w2",
                        "length",
                        "l",
                    ),
                )
                _assign_from_aliases(
                    "beam_stiffener_weld_size_wst2",
                    weld_2,
                    (
                        "beam_stiffener_weld_size_wst2",
                        "stiffener_beam_weld_size_wst2",
                        "w_st_2",
                        "size",
                        "w",
                    ),
                )
                _assign_from_aliases(
                    "beam_stiffener_weld_lines_nl_w2",
                    weld_2,
                    (
                        "beam_stiffener_weld_lines_nl_w2",
                        "stiffener_beam_weld_lines_nl_w2",
                        "n_l_w2",
                        "nl",
                        "lines",
                    ),
                )
                _assign_from_aliases(
                    "L_gap_w2_vgder",
                    weld_2,
                    ("L_gap_w2_vgder", "L_gap_w2", "l_gap_w2_vgder", "l_gap", "gap"),
                )
                _assign_from_aliases(
                    "L_gap_w2_vgizq",
                    weld_2,
                    ("L_gap_w2_vgizq", "L_gap_w2", "l_gap_w2_vgizq", "l_gap", "gap"),
                )
                _assign_from_aliases(
                    "kds_w2_vgder",
                    weld_2,
                    ("kds_w2_vgder",),
                )
                _assign_from_aliases(
                    "kds_w2_vgizq",
                    weld_2,
                    ("kds_w2_vgizq",),
                )

            if weld_3:
                _assign_from_aliases(
                    "end_plate_beam_web_weld_type",
                    weld_3,
                    (
                        "end_plate_beam_web_weld_type",
                        "weld_type_end_plate_beam_web",
                        "tipo_soldadura_end_plate_beam_web",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "end_plate_beam_web_weld_thickness_twe",
                    weld_3,
                    (
                        "end_plate_beam_web_weld_thickness_twe",
                        "twe",
                        "thickness",
                        "size",
                        "w",
                    ),
                )
                _assign_from_aliases(
                    "end_plate_beam_web_weld_lines_nl",
                    weld_3,
                    (
                        "end_plate_beam_web_weld_lines_nl",
                        "nl",
                        "n_l",
                        "lines",
                    ),
                )
                _assign_from_aliases(
                    "kds_w3_vgder",
                    weld_3,
                    ("kds_w3_vgder",),
                )
                _assign_from_aliases(
                    "kds_w3_vgizq",
                    weld_3,
                    ("kds_w3_vgizq",),
                )

            weld_4_side_specific = any(
                key in weld_4
                for key in (
                    "tipo_w4_vgder",
                    "tipo_w4_vgizq",
                    "t_w4_vgder",
                    "t_w4_vgizq",
                    "nl_w4_vgder",
                    "nl_w4_vgizq",
                    "t_w4_1_vgder",
                    "t_w4_1_vgizq",
                    "t_w4.1_vgder",
                    "t_w4.1_vgizq",
                    "kds_w4_vgder",
                    "kds_w4_vgizq",
                )
            )

            if weld_4 and weld_4_side_specific:
                _assign_from_aliases(
                    "tipo_w4_vgder",
                    weld_4,
                    (
                        "tipo_w4_vgder",
                        "weld_type_vgder",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "tipo_w4_vgizq",
                    weld_4,
                    (
                        "tipo_w4_vgizq",
                        "weld_type_vgizq",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "t_w4_vgder",
                    weld_4,
                    ("t_w4_vgder", "thickness_vgder", "thickness", "size", "w"),
                )
                _assign_from_aliases(
                    "t_w4_vgizq",
                    weld_4,
                    ("t_w4_vgizq", "thickness_vgizq", "thickness", "size", "w"),
                )
                _assign_from_aliases(
                    "nl_w4_vgder",
                    weld_4,
                    ("nl_w4_vgder", "nl_vgder", "nl", "n_l", "lines"),
                )
                _assign_from_aliases(
                    "nl_w4_vgizq",
                    weld_4,
                    ("nl_w4_vgizq", "nl_vgizq", "nl", "n_l", "lines"),
                )
                _assign_from_aliases(
                    "t_w4_1_vgder",
                    weld_4,
                    ("t_w4_1_vgder", "t_w4.1_vgder", "backing_thickness_vgder", "backing_thickness"),
                )
                _assign_from_aliases(
                    "t_w4_1_vgizq",
                    weld_4,
                    ("t_w4_1_vgizq", "t_w4.1_vgizq", "backing_thickness_vgizq", "backing_thickness"),
                )
                _assign_from_aliases("kds_w4_vgder", weld_4, ("kds_w4_vgder",))
                _assign_from_aliases("kds_w4_vgizq", weld_4, ("kds_w4_vgizq",))

            if weld_4 and not weld_4_side_specific and not weld_cp:
                _assign_from_aliases(
                    "continuity_plate_weld_type",
                    weld_4,
                    (
                        "continuity_plate_weld_type",
                        "weld_type_continuity_plate",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )

            if weld_cp:
                _assign_from_aliases(
                    "continuity_plate_weld_type",
                    weld_cp,
                    (
                        "continuity_plate_weld_type",
                        "weld_type_continuity_plate",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "continuity_plate_weld_type_col",
                    weld_cp,
                    (
                        "continuity_plate_weld_type_col",
                        "tipo_w5_col",
                        "tipo_w5",
                        "weld_type_continuity_plate",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "t_w5_col",
                    weld_cp,
                    ("w_w5_col", "t_w5_col", "t_w5", "thickness", "size", "w"),
                )
                _assign_from_aliases(
                    "w_w5_col",
                    weld_cp,
                    ("w_w5_col", "t_w5_col", "t_w5", "thickness", "size", "w"),
                )
                _assign_from_aliases(
                    "nl_w5_col",
                    weld_cp,
                    ("nl_w5_col", "nl_w5", "nl", "n_l", "lines"),
                )
                _assign_from_aliases(
                    "L_gap_w5_col",
                    weld_cp,
                    ("L_gap_w5_col", "L_gap_w5", "l_gap_w5_col", "l_gap", "gap"),
                )
                _assign_from_aliases(
                    "kds_w5_col",
                    weld_cp,
                    ("kds_w5_col", "kds_w5"),
                )

            if weld_dp_plug:
                _assign_from_aliases(
                    "doubler_plate_web_plug_weld_type",
                    weld_dp_plug,
                    (
                        "doubler_plate_web_plug_weld_type",
                        "tipo_w7_col",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "doubler_plate_web_plug_weld_size",
                    weld_dp_plug,
                    (
                        "doubler_plate_web_plug_weld_size",
                        "t_w7_col",
                        "t_wdp_plug",
                        "thickness",
                        "size",
                        "w",
                    ),
                )
                _assign_from_aliases(
                    "doubler_plate_web_plug_weld_lines_nl",
                    weld_dp_plug,
                    (
                        "doubler_plate_web_plug_weld_lines_nl",
                        "nl_w7_col",
                        "nl_wdp_plug",
                        "nl",
                        "n_l",
                        "lines",
                    ),
                )

            if weld_cw:
                _assign_from_aliases(
                    "continuity_plate_web_weld_type_col",
                    weld_cw,
                    (
                        "continuity_plate_web_weld_type_col",
                        "tipo_w6_col",
                        "tipo_w6",
                        "weld_type",
                        "tipo_soldadura",
                        "type",
                    ),
                )
                _assign_from_aliases(
                    "t_w6_col",
                    weld_cw,
                    ("w_w6_col", "t_w6_col", "t_w6", "thickness", "size", "w"),
                )
                _assign_from_aliases(
                    "w_w6_col",
                    weld_cw,
                    ("w_w6_col", "t_w6_col", "t_w6", "thickness", "size", "w"),
                )
                _assign_from_aliases(
                    "nl_w6_col",
                    weld_cw,
                    ("nl_w6_col", "nl_w6", "nl", "n_l", "lines"),
                )
                _assign_from_aliases(
                    "L_gap_w6_col",
                    weld_cw,
                    ("L_gap_w6_col", "L_gap_w6", "l_gap_w6_col", "l_gap", "gap"),
                )
                _assign_from_aliases(
                    "kds_w6_col",
                    weld_cw,
                    ("kds_w6_col", "kds_w6"),
                )

            if "continuity_plate_weld_type" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["continuity_plate_weld_type"]
            if "weld_type_continuity_plate" in block and "continuity_plate_weld_type" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type"] = block["weld_type_continuity_plate"]
            if "continuity_plate_weld_type_col" in block and "continuity_plate_weld_type_col" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type_col"] = block["continuity_plate_weld_type_col"]
            if "tipo_w5_col" in block and "continuity_plate_weld_type_col" not in flat_geometry:
                flat_geometry["continuity_plate_weld_type_col"] = block["tipo_w5_col"]
            if "t_w5_col" in block and "t_w5_col" not in flat_geometry:
                flat_geometry["t_w5_col"] = block["t_w5_col"]
            if "w_w5_col" in block and "w_w5_col" not in flat_geometry:
                flat_geometry["w_w5_col"] = block["w_w5_col"]
            if "nl_w5_col" in block and "nl_w5_col" not in flat_geometry:
                flat_geometry["nl_w5_col"] = block["nl_w5_col"]
            if "L_gap_w5_col" in block and "L_gap_w5_col" not in flat_geometry:
                flat_geometry["L_gap_w5_col"] = block["L_gap_w5_col"]
            if "kds_w5_col" in block and "kds_w5_col" not in flat_geometry:
                flat_geometry["kds_w5_col"] = block["kds_w5_col"]
            if (
                "continuity_plate_web_weld_type_col" in block
                and "continuity_plate_web_weld_type_col" not in flat_geometry
            ):
                flat_geometry["continuity_plate_web_weld_type_col"] = block["continuity_plate_web_weld_type_col"]
            if "tipo_w6_col" in block and "continuity_plate_web_weld_type_col" not in flat_geometry:
                flat_geometry["continuity_plate_web_weld_type_col"] = block["tipo_w6_col"]
            if "t_w6_col" in block and "t_w6_col" not in flat_geometry:
                flat_geometry["t_w6_col"] = block["t_w6_col"]
            if "w_w6_col" in block and "w_w6_col" not in flat_geometry:
                flat_geometry["w_w6_col"] = block["w_w6_col"]
            if "nl_w6_col" in block and "nl_w6_col" not in flat_geometry:
                flat_geometry["nl_w6_col"] = block["nl_w6_col"]
            if "L_gap_w6_col" in block and "L_gap_w6_col" not in flat_geometry:
                flat_geometry["L_gap_w6_col"] = block["L_gap_w6_col"]
            if "kds_w6_col" in block and "kds_w6_col" not in flat_geometry:
                flat_geometry["kds_w6_col"] = block["kds_w6_col"]
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
                "end_plate_beam_web_weld_thickness_twe" in block
                and "end_plate_beam_web_weld_thickness_twe" not in flat_geometry
            ):
                flat_geometry["end_plate_beam_web_weld_thickness_twe"] = block["end_plate_beam_web_weld_thickness_twe"]
            if "twe" in block and "end_plate_beam_web_weld_thickness_twe" not in flat_geometry:
                flat_geometry["end_plate_beam_web_weld_thickness_twe"] = block["twe"]
            if (
                "end_plate_beam_web_weld_lines_nl" in block
                and "end_plate_beam_web_weld_lines_nl" not in flat_geometry
            ):
                flat_geometry["end_plate_beam_web_weld_lines_nl"] = block["end_plate_beam_web_weld_lines_nl"]
            if "end_plate_stiffener_weld_type" in block and "end_plate_stiffener_weld_type" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_type"] = block["end_plate_stiffener_weld_type"]
            if "stiffener_weld_type" in block and "end_plate_stiffener_weld_type" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_type"] = block["stiffener_weld_type"]
            if (
                "tipo_soldadura_rigidizador" in block
                and "end_plate_stiffener_weld_type" not in flat_geometry
            ):
                flat_geometry["end_plate_stiffener_weld_type"] = block["tipo_soldadura_rigidizador"]
            if (
                "end_plate_stiffener_weld_length_lst" in block
                and "end_plate_stiffener_weld_length_lst" not in flat_geometry
            ):
                flat_geometry["end_plate_stiffener_weld_length_lst"] = block["end_plate_stiffener_weld_length_lst"]
            if "stiffener_weld_length_lst" in block and "end_plate_stiffener_weld_length_lst" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_length_lst"] = block["stiffener_weld_length_lst"]
            if "l_st" in block and "end_plate_stiffener_weld_length_lst" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_length_lst"] = block["l_st"]
            if "L_gap_w1" in block and "L_gap_w1" not in flat_geometry:
                flat_geometry["L_gap_w1"] = block["L_gap_w1"]
            if "L_gap_w1_vgder" in block and "L_gap_w1_vgder" not in flat_geometry:
                flat_geometry["L_gap_w1_vgder"] = block["L_gap_w1_vgder"]
            if "L_gap_w1_vgizq" in block and "L_gap_w1_vgizq" not in flat_geometry:
                flat_geometry["L_gap_w1_vgizq"] = block["L_gap_w1_vgizq"]
            if (
                "end_plate_stiffener_weld_size_wst" in block
                and "end_plate_stiffener_weld_size_wst" not in flat_geometry
            ):
                flat_geometry["end_plate_stiffener_weld_size_wst"] = block["end_plate_stiffener_weld_size_wst"]
            if "stiffener_weld_size_wst" in block and "end_plate_stiffener_weld_size_wst" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_size_wst"] = block["stiffener_weld_size_wst"]
            if "w_st" in block and "end_plate_stiffener_weld_size_wst" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_size_wst"] = block["w_st"]
            if (
                "end_plate_stiffener_weld_lines_nl" in block
                and "end_plate_stiffener_weld_lines_nl" not in flat_geometry
            ):
                flat_geometry["end_plate_stiffener_weld_lines_nl"] = block["end_plate_stiffener_weld_lines_nl"]
            if "stiffener_weld_lines_nl" in block and "end_plate_stiffener_weld_lines_nl" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_lines_nl"] = block["stiffener_weld_lines_nl"]
            if "n_l" in block and "end_plate_stiffener_weld_lines_nl" not in flat_geometry:
                flat_geometry["end_plate_stiffener_weld_lines_nl"] = block["n_l"]
            if "beam_stiffener_weld_type" in block and "beam_stiffener_weld_type" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_type"] = block["beam_stiffener_weld_type"]
            if "stiffener_beam_weld_type" in block and "beam_stiffener_weld_type" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_type"] = block["stiffener_beam_weld_type"]
            if (
                "tipo_soldadura_viga_rigidizador" in block
                and "beam_stiffener_weld_type" not in flat_geometry
            ):
                flat_geometry["beam_stiffener_weld_type"] = block["tipo_soldadura_viga_rigidizador"]
            if (
                "beam_stiffener_weld_length_lstw2" in block
                and "beam_stiffener_weld_length_lstw2" not in flat_geometry
            ):
                flat_geometry["beam_stiffener_weld_length_lstw2"] = block["beam_stiffener_weld_length_lstw2"]
            if "stiffener_beam_weld_length_lstw2" in block and "beam_stiffener_weld_length_lstw2" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_length_lstw2"] = block["stiffener_beam_weld_length_lstw2"]
            if "l_st_w2" in block and "beam_stiffener_weld_length_lstw2" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_length_lstw2"] = block["l_st_w2"]
            if "L_gap_w2" in block and "L_gap_w2" not in flat_geometry:
                flat_geometry["L_gap_w2"] = block["L_gap_w2"]
            if "L_gap_w2_vgder" in block and "L_gap_w2_vgder" not in flat_geometry:
                flat_geometry["L_gap_w2_vgder"] = block["L_gap_w2_vgder"]
            if "L_gap_w2_vgizq" in block and "L_gap_w2_vgizq" not in flat_geometry:
                flat_geometry["L_gap_w2_vgizq"] = block["L_gap_w2_vgizq"]
            if (
                "beam_stiffener_weld_size_wst2" in block
                and "beam_stiffener_weld_size_wst2" not in flat_geometry
            ):
                flat_geometry["beam_stiffener_weld_size_wst2"] = block["beam_stiffener_weld_size_wst2"]
            if "stiffener_beam_weld_size_wst2" in block and "beam_stiffener_weld_size_wst2" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_size_wst2"] = block["stiffener_beam_weld_size_wst2"]
            if "w_st_2" in block and "beam_stiffener_weld_size_wst2" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_size_wst2"] = block["w_st_2"]
            if (
                "beam_stiffener_weld_lines_nl_w2" in block
                and "beam_stiffener_weld_lines_nl_w2" not in flat_geometry
            ):
                flat_geometry["beam_stiffener_weld_lines_nl_w2"] = block["beam_stiffener_weld_lines_nl_w2"]
            if "stiffener_beam_weld_lines_nl_w2" in block and "beam_stiffener_weld_lines_nl_w2" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_lines_nl_w2"] = block["stiffener_beam_weld_lines_nl_w2"]
            if "n_l_w2" in block and "beam_stiffener_weld_lines_nl_w2" not in flat_geometry:
                flat_geometry["beam_stiffener_weld_lines_nl_w2"] = block["n_l_w2"]
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

    if "beam_connection_sides" in flat_geometry:
        design_factors = normalized.get("design_factors")
        if not isinstance(design_factors, dict):
            design_factors = {}
            normalized["design_factors"] = design_factors
        if "beam_connection_sides" not in design_factors:
            design_factors["beam_connection_sides"] = flat_geometry["beam_connection_sides"]
        flat_geometry.pop("beam_connection_sides", None)

    if "beam_clear_span_length_right" in flat_geometry and "beam_clear_span_length_der" not in flat_geometry:
        flat_geometry["beam_clear_span_length_der"] = flat_geometry.pop("beam_clear_span_length_right")
    if "beam_clear_span_length_left" in flat_geometry and "beam_clear_span_length_izq" not in flat_geometry:
        flat_geometry["beam_clear_span_length_izq"] = flat_geometry.pop("beam_clear_span_length_left")
    if (
        "beam_shear_connector_free_length_from_column_face_right" in flat_geometry
        and "beam_shear_connector_free_length_from_column_face_der" not in flat_geometry
    ):
        flat_geometry["beam_shear_connector_free_length_from_column_face_der"] = flat_geometry.pop(
            "beam_shear_connector_free_length_from_column_face_right"
        )
    if (
        "beam_shear_connector_free_length_from_column_face_left" in flat_geometry
        and "beam_shear_connector_free_length_from_column_face_izq" not in flat_geometry
    ):
        flat_geometry["beam_shear_connector_free_length_from_column_face_izq"] = flat_geometry.pop(
            "beam_shear_connector_free_length_from_column_face_left"
        )

    normalized["geometry"] = flat_geometry
    return normalized


def _normalize_fully_restrained_splice_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    if normalized.get("connection_family") != "Fully_Restrained_Moment":
        return normalized
    if normalized.get("connection_type") != "bbmb_splice":
        return normalized
    # Canonical payload already present.
    if (
        isinstance(normalized.get("sections"), dict)
        and isinstance(normalized.get("materials"), dict)
        and isinstance(normalized.get("geometry"), dict)
    ):
        return normalized

    # Subdivision by scope (as defined in VARIABLES_SPLICE_NAMING.txt).
    viga = _first_dict(normalized, "viga", "beam")
    seccion_material = _first_dict(normalized, "seccion_material", "section_material")
    platina_web = _first_dict(normalized, "platina_web", "platina_1_alma", "web_plate")
    platina_flange = _first_dict(normalized, "platina_flange", "platina_2_ala", "flange_plate")
    pernos_web = _first_dict(
        normalized,
        "pernos_grupo_1_web",
        "pernos_web",
        "pernos_grupo_1_alma",
        "bolts_web",
    )
    pernos_flange = _first_dict(
        normalized,
        "pernos_grupo_2_flange",
        "pernos_flange",
        "pernos_grupo_2_ala",
        "bolts_flange",
    )
    loads = _first_dict(normalized, "loads", "cargas", "cargas_splice")
    design_factors = _first_dict(normalized, "design_factors", "factores_diseno")
    procedure = _first_dict(normalized, "procedure", "procedimiento")

    sections = _compact_dict(
        {
            "shape_vg": _first_present(viga, "shape_vg", "perfil"),
        }
    )
    materials = _compact_dict(
        {
            "steel_vg": _first_present(viga, "steel_vg", "tipo_acero_viga"),
            "Fy_vg": _first_present(seccion_material, "Fy_vg"),
            "Fu_vg": _first_present(seccion_material, "Fu_vg"),
            "E_vg": _first_present(seccion_material, "E_vg"),
            "shape_blt_web": _first_present(pernos_web, "shape_blt_web", "bolt_shape_1"),
            "std_blt_web": _first_present(pernos_web, "std_blt_web", "bolt_fabrication_standard_1"),
            "desc_blt_web": _first_present(pernos_web, "desc_blt_web", "bolt_description_1"),
            "thread_blt_web": _first_present(pernos_web, "thread_blt_web", "bolt_thread_condition_1"),
            "shape_blt_flange": _first_present(pernos_flange, "shape_blt_flange", "bolt_shape_2"),
            "std_blt_flange": _first_present(pernos_flange, "std_blt_flange", "bolt_fabrication_standard_2"),
            "desc_blt_flange": _first_present(pernos_flange, "desc_blt_flange", "bolt_description_2"),
            "thread_blt_flange": _first_present(pernos_flange, "thread_blt_flange", "bolt_thread_condition_2"),
        }
    )
    geometry = _compact_dict(
        {
            "gap_sp": _first_present(viga, "gap_sp", "sep"),
            "tol_L_vg": _first_present(viga, "tol_L_vg", "Tlvg"),
            "cond_sup_vg": _first_present(viga, "cond_sup_vg", "condicion_superficial"),
            "cond_amb_vg": _first_present(viga, "cond_amb_vg", "condicion_atmosferica"),
            "t_plt_web": _first_present(platina_web, "t_plt_web", "tp1"),
            "type_hole_plt_web": _first_present(platina_web, "type_hole_plt_web", "tipo_agujero_p1"),
            "cond_sup_plt_web": _first_present(platina_web, "cond_sup_plt_web", "condicion_superficial"),
            "cond_amb_plt_web": _first_present(platina_web, "cond_amb_plt_web", "condicion_atmosferica"),
            "t_plt_ftop": _first_present(platina_flange, "t_plt_ftop", "tp2"),
            "t_plt_fbot": _first_present(platina_flange, "t_plt_fbot", "tp2"),
            "type_hole_plt_flange": _first_present(platina_flange, "type_hole_plt_flange", "tipo_agujero_p2"),
            "cond_sup_plt_flange": _first_present(platina_flange, "cond_sup_plt_flange", "condicion_superficial"),
            "cond_amb_plt_flange": _first_present(platina_flange, "cond_amb_plt_flange", "condicion_atmosferica"),
            "n_blt_web_x": _first_present(pernos_web, "n_blt_web_x", "nb1_x"),
            "n_blt_web_y": _first_present(pernos_web, "n_blt_web_y", "nb1_y"),
            "g_blt_web": _first_present(pernos_web, "g_blt_web", "S1_x"),
            "p_blt_web": _first_present(pernos_web, "p_blt_web", "S1_y"),
            "Le_blt_web_x1": _first_present(pernos_web, "Le_blt_web_x1", "Le1_x1"),
            "Le_blt_web_x2": _first_present(pernos_web, "Le_blt_web_x2", "Le1_x2"),
            "Le_blt_web_y1": _first_present(pernos_web, "Le_blt_web_y1", "Le1_y1"),
            "Le_blt_web_y2": _first_present(pernos_web, "Le_blt_web_y2", "Le1_y2"),
            "Le_blt_web_y3": _first_present(pernos_web, "Le_blt_web_y3", "Le1_y3", "Le1.y3"),
            "type_tight_blt_web": _first_present(pernos_web, "type_tight_blt_web", "bolt_tightening_type"),
            "n_blt_flange_x": _first_present(pernos_flange, "n_blt_flange_x", "nb2_x"),
            "n_blt_flange_z": _first_present(pernos_flange, "n_blt_flange_z", "nb2_z"),
            "p_blt_flange": _first_present(pernos_flange, "p_blt_flange", "S2_x"),
            "g_blt_flange": _first_present(pernos_flange, "g_blt_flange", "S2_z1"),
            "Le_blt_flange_x1": _first_present(pernos_flange, "Le_blt_flange_x1", "Le2_x1"),
            "Le_blt_flange_x2": _first_present(pernos_flange, "Le_blt_flange_x2", "Le2_x2"),
            "Le_blt_flange_z1": _first_present(pernos_flange, "Le_blt_flange_z1", "Le2_z1"),
            "Le_blt_flange_z2": _first_present(pernos_flange, "Le_blt_flange_z2", "Le2_z2"),
            "Le_blt_flange_z3": _first_present(pernos_flange, "Le_blt_flange_z3"),
            "type_tight_blt_flange": _first_present(
                pernos_flange,
                "type_tight_blt_flange",
                "bolt_tightening_type",
            ),
        }
    )

    top_payload: dict[str, Any] = {}
    for key in (
        "project_id",
        "case_id",
        "design_code_context",
        "units_system",
        "connection_family",
        "connection_type",
        "load_state",
    ):
        if key in normalized:
            top_payload[key] = normalized[key]
    if sections:
        top_payload["sections"] = sections
    if materials:
        top_payload["materials"] = materials
    if geometry:
        top_payload["geometry"] = geometry
    if loads:
        top_payload["loads"] = loads
    if design_factors:
        top_payload["design_factors"] = design_factors
    if procedure:
        top_payload["procedure"] = procedure
    return top_payload


def _normalize_moment_loads_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    if normalized.get("connection_family") != "moment_prequalified":
        return normalized
    loads = normalized.get("loads")
    if not isinstance(loads, dict):
        return normalized

    # Backward compatibility: map legacy single-beam names to right-beam names.
    if "Beam_right_Vgravity" in loads:
        if "beam_right_vgravity" not in loads:
            loads["beam_right_vgravity"] = loads["Beam_right_Vgravity"]
        loads.pop("Beam_right_Vgravity", None)
    if "Beam_left_Vgravity" in loads:
        if "beam_left_vgravity" not in loads:
            loads["beam_left_vgravity"] = loads["Beam_left_Vgravity"]
        loads.pop("Beam_left_Vgravity", None)
    if "beam_right_vgravity" not in loads and "beam_gravity_shear_between_hinges_der" in loads:
        loads["beam_right_vgravity"] = loads["beam_gravity_shear_between_hinges_der"]
    if "beam_left_vgravity" not in loads and "beam_gravity_shear_between_hinges_izq" in loads:
        loads["beam_left_vgravity"] = loads["beam_gravity_shear_between_hinges_izq"]
    if "beam_right_vgravity" not in loads and "beam_gravity_shear_between_hinges" in loads:
        loads["beam_right_vgravity"] = loads["beam_gravity_shear_between_hinges"]
    if "beam_right_vgravity" not in loads and "beam_gravity_shear_between_hinges_right" in loads:
        loads["beam_right_vgravity"] = loads["beam_gravity_shear_between_hinges_right"]
    if "beam_left_vgravity" not in loads and "beam_gravity_shear_between_hinges_left" in loads:
        loads["beam_left_vgravity"] = loads["beam_gravity_shear_between_hinges_left"]
    if "shear_plastic_hinge_dermax" not in loads and "shear_plastic_hinge" in loads:
        loads["shear_plastic_hinge_dermax"] = loads["shear_plastic_hinge"]
    if "shear_plastic_hinge_dermax" not in loads and "shear_plastic_hinge_rightmax" in loads:
        loads["shear_plastic_hinge_dermax"] = loads["shear_plastic_hinge_rightmax"]
    if "shear_plastic_hinge_izqmax" not in loads and "shear_plastic_hinge_leftmax" in loads:
        loads["shear_plastic_hinge_izqmax"] = loads["shear_plastic_hinge_leftmax"]
    if "pu_viga_right" not in loads and "pu_viga" in loads:
        loads["pu_viga_right"] = loads["pu_viga"]
    if "pu_viga_right" not in loads and "pu_viga_der" in loads:
        loads["pu_viga_right"] = loads["pu_viga_der"]
    if "pu_viga_left" not in loads and "pu_viga_izq" in loads:
        loads["pu_viga_left"] = loads["pu_viga_izq"]
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
    if case.design_factors.ry is not None:
        _raise_validation_error(
            message=(
                "Input 'design_factors.ry' is no longer allowed. "
                "Ry is now derived automatically from data/materials.xlsx (sheet HRS) "
                "using materials.profile_steel_type."
            ),
            missing_fields=["design_factors.ry"],
            source_document="data/materials.xlsx",
        )
    case.materials.beam_fy = profile_props["fy"]  # type: ignore[assignment]
    case.materials.beam_fu = profile_props["fu"]  # type: ignore[assignment]
    case.materials.column_fy = profile_props["fy"]  # type: ignore[assignment]
    case.materials.column_fu = profile_props["fu"]  # type: ignore[assignment]
    ry_catalog = float(profile_props["ry"])  # type: ignore[arg-type]
    if ry_catalog < 1.0:
        _raise_validation_error(
            message=(
                f"Invalid Ry='{ry_catalog}' from data/materials.xlsx (sheet HRS) for "
                f"materials.profile_steel_type='{profile_type}'. Expected Ry >= 1.0."
            ),
            missing_fields=["materials.profile_steel_type"],
            source_document="data/materials.xlsx",
        )
    case.design_factors.ry = ry_catalog

    if case.connection_type not in {"bueep_4e", "bseep_4es", "bseep_8es"}:
        return

    # Procedure fields now derived internally from catalog/geometry and are not accepted as input.
    if case.procedure is not None:
        if case.procedure.beam_plastic_section_modulus_ze is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.beam_plastic_section_modulus_ze' is no longer allowed. "
                    "Ze is derived automatically from beam catalog property Zx (sections.xlsx)."
                ),
                missing_fields=["procedure.beam_plastic_section_modulus_ze"],
                source_document="data/sections.xlsx",
            )
        if case.procedure.beam_span_between_plastic_hinges_lh is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.beam_span_between_plastic_hinges_lh' is no longer allowed. "
                    "Lh is derived automatically from geometry.beam_clear_span_length."
                ),
                missing_fields=["procedure.beam_span_between_plastic_hinges_lh"],
                source_document="AISC 358-22",
            )
        if case.procedure.yield_line_parameter_yp is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.yield_line_parameter_yp' is no longer allowed."
                ),
                missing_fields=["procedure.yield_line_parameter_yp"],
                source_document="AISC 358-22",
            )
        if case.procedure.column_yield_line_parameter_yc_unstiffened is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.column_yield_line_parameter_yc_unstiffened' is no longer allowed. "
                    "Yc will be derived internally from AISC 358-22 tables in a later implementation."
                ),
                missing_fields=["procedure.column_yield_line_parameter_yc_unstiffened"],
                source_document="AISC 358-22",
            )
        if case.procedure.column_yield_line_parameter_yc_stiffened is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.column_yield_line_parameter_yc_stiffened' is no longer allowed. "
                    "Yc will be derived internally from AISC 358-22 tables in a later implementation."
                ),
                missing_fields=["procedure.column_yield_line_parameter_yc_stiffened"],
                source_document="AISC 358-22",
            )
        if case.procedure.flange_weld_available_strength is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.flange_weld_available_strength' is no longer allowed. "
                    "This check is currently not required as input."
                ),
                missing_fields=["procedure.flange_weld_available_strength"],
                source_document="AISC 358-22",
            )
        if case.procedure.web_weld_available_strength is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.web_weld_available_strength' is no longer allowed. "
                    "This check is currently not required as input."
                ),
                missing_fields=["procedure.web_weld_available_strength"],
                source_document="AISC 358-22",
            )
        if case.procedure.continuity_plate_available_strength is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.continuity_plate_available_strength' is no longer allowed. "
                    "This check is currently not required as input."
                ),
                missing_fields=["procedure.continuity_plate_available_strength"],
                source_document="AISC 358-22",
            )
        if case.procedure.panel_zone_capacity is not None:
            _raise_validation_error(
                message=(
                    "Input 'procedure.panel_zone_capacity' is no longer allowed. "
                    "This check is currently not required as input."
                ),
                missing_fields=["procedure.panel_zone_capacity"],
                source_document="AISC 358-22",
            )

    beam_connection_sides = case.design_factors.beam_connection_sides
    if beam_connection_sides is None:
        _raise_validation_error(
            message=(
                "Required input 'design_factors.beam_connection_sides' is missing. "
                "No default value is allowed under zero-guess policy."
            ),
            missing_fields=["design_factors.beam_connection_sides"],
            source_document="AISC 358-22",
        )
    case.design_factors.beam_connection_sides = beam_connection_sides

    if case.geometry.beam_clear_span_length_der is None and case.geometry.beam_clear_span_length is not None:
        case.geometry.beam_clear_span_length_der = case.geometry.beam_clear_span_length
    if case.geometry.beam_clear_span_length_izq is None and case.geometry.beam_clear_span_length is not None:
        case.geometry.beam_clear_span_length_izq = case.geometry.beam_clear_span_length

    if (
        case.geometry.beam_shear_connector_free_length_from_column_face_der is None
        and case.geometry.beam_shear_connector_free_length_from_column_face is not None
    ):
        case.geometry.beam_shear_connector_free_length_from_column_face_der = (
            case.geometry.beam_shear_connector_free_length_from_column_face
        )
    if (
        case.geometry.beam_shear_connector_free_length_from_column_face_izq is None
        and case.geometry.beam_shear_connector_free_length_from_column_face is not None
    ):
        case.geometry.beam_shear_connector_free_length_from_column_face_izq = (
            case.geometry.beam_shear_connector_free_length_from_column_face
        )

    if case.loads.beam_right_vgravity is None and case.loads.beam_gravity_shear_between_hinges_der is not None:
        case.loads.beam_right_vgravity = case.loads.beam_gravity_shear_between_hinges_der
    if case.loads.beam_left_vgravity is None and case.loads.beam_gravity_shear_between_hinges_izq is not None:
        case.loads.beam_left_vgravity = case.loads.beam_gravity_shear_between_hinges_izq
    if case.loads.beam_right_vgravity is None and case.loads.beam_gravity_shear_between_hinges is not None:
        case.loads.beam_right_vgravity = case.loads.beam_gravity_shear_between_hinges
    if case.loads.beam_left_vgravity is None and case.loads.beam_gravity_shear_between_hinges is not None:
        case.loads.beam_left_vgravity = case.loads.beam_gravity_shear_between_hinges
    if case.loads.pu_viga_right is None and case.loads.pu_viga is not None:
        case.loads.pu_viga_right = case.loads.pu_viga
    if case.loads.pu_viga_left is None and case.loads.pu_viga is not None:
        case.loads.pu_viga_left = case.loads.pu_viga
    if case.loads.shear_plastic_hinge_dermax is None and case.loads.shear_plastic_hinge is not None:
        case.loads.shear_plastic_hinge_dermax = case.loads.shear_plastic_hinge
    if case.loads.shear_plastic_hinge_izqmax is None and case.loads.shear_plastic_hinge is not None:
        case.loads.shear_plastic_hinge_izqmax = case.loads.shear_plastic_hinge

    include_right = beam_connection_sides in {"right_only", "both_sides"}
    include_left = beam_connection_sides in {"left_only", "both_sides"}

    if include_right:
        for field_path, value, source in (
            (
                "geometry.beam_clear_span_length_der",
                case.geometry.beam_clear_span_length_der,
                "AISC 358-22 Section 2.3.4",
            ),
            (
                "geometry.beam_shear_connector_free_length_from_column_face_der",
                case.geometry.beam_shear_connector_free_length_from_column_face_der,
                "AISC 358-22 Section 2.3.4",
            ),
            (
                "loads.beam_right_vgravity",
                case.loads.beam_right_vgravity,
                "AISC 358-22 Eq. 2.4-3",
            ),
            (
                "loads.pu_viga_right",
                case.loads.pu_viga_right,
                "AISC 358-22 Section 2.3.4",
            ),
        ):
            if value is None:
                _raise_validation_error(
                    message=f"Required input '{field_path}' is missing for beam_connection_sides='{beam_connection_sides}'.",
                    missing_fields=[field_path],
                    source_document=source,
                )

    if include_left:
        for field_path, value, source in (
            (
                "geometry.beam_clear_span_length_izq",
                case.geometry.beam_clear_span_length_izq,
                "AISC 358-22 Section 2.3.4",
            ),
            (
                "geometry.beam_shear_connector_free_length_from_column_face_izq",
                case.geometry.beam_shear_connector_free_length_from_column_face_izq,
                "AISC 358-22 Section 2.3.4",
            ),
            (
                "loads.beam_left_vgravity",
                case.loads.beam_left_vgravity,
                "AISC 358-22 Eq. 2.4-3",
            ),
            (
                "loads.pu_viga_left",
                case.loads.pu_viga_left,
                "AISC 358-22 Section 2.3.4",
            ),
        ):
            if value is None:
                _raise_validation_error(
                    message=f"Required input '{field_path}' is missing for beam_connection_sides='{beam_connection_sides}'.",
                    missing_fields=[field_path],
                    source_document=source,
                )

    def _min_quantity(first: Quantity, second: Quantity, field_name: str) -> Quantity:
        if first.unit != second.unit:
            _raise_validation_error(
                message=(
                    f"Incompatible units in '{field_name}': '{first.unit}' vs '{second.unit}'. "
                    "Use the same unit for right and left beam values."
                ),
                missing_fields=[field_name],
                source_document="AISC 358-22",
            )
        return first if first.value <= second.value else second

    def _max_quantity(first: Quantity, second: Quantity, field_name: str) -> Quantity:
        if first.unit != second.unit:
            _raise_validation_error(
                message=(
                    f"Incompatible units in '{field_name}': '{first.unit}' vs '{second.unit}'. "
                    "Use the same unit for right and left beam values."
                ),
                missing_fields=[field_name],
                source_document="AISC 358-22",
            )
        return first if first.value >= second.value else second

    # Preserve legacy single-beam fields for existing checks (conservative when both sides are present).
    if beam_connection_sides == "both_sides":
        case.geometry.beam_clear_span_length = _min_quantity(
            case.geometry.beam_clear_span_length_der,
            case.geometry.beam_clear_span_length_izq,  # type: ignore[arg-type]
            "geometry.beam_clear_span_length_der/izq",
        )
        case.geometry.beam_shear_connector_free_length_from_column_face = _min_quantity(
            case.geometry.beam_shear_connector_free_length_from_column_face_der,
            case.geometry.beam_shear_connector_free_length_from_column_face_izq,  # type: ignore[arg-type]
            "geometry.beam_shear_connector_free_length_from_column_face_der/izq",
        )
        case.loads.pu_viga = _max_quantity(
            case.loads.pu_viga_right,
            case.loads.pu_viga_left,  # type: ignore[arg-type]
            "loads.pu_viga_right/left",
        )
    elif beam_connection_sides == "right_only":
        case.geometry.beam_clear_span_length = case.geometry.beam_clear_span_length_der
        case.geometry.beam_shear_connector_free_length_from_column_face = (
            case.geometry.beam_shear_connector_free_length_from_column_face_der
        )
        case.loads.pu_viga = case.loads.pu_viga_right
    else:
        case.geometry.beam_clear_span_length = case.geometry.beam_clear_span_length_izq
        case.geometry.beam_shear_connector_free_length_from_column_face = (
            case.geometry.beam_shear_connector_free_length_from_column_face_izq
        )
        case.loads.pu_viga = case.loads.pu_viga_left

    if case.connection_type in {"bueep_4e", "bseep_4es"} and case.geometry.pb is None:
        pb_reference = case.geometry.de or case.geometry.pfo or case.geometry.pfi
        if pb_reference is not None:
            case.geometry.pb = Quantity(value=0.0, unit=pb_reference.unit)

    case.loads.beam_gravity_shear_between_hinges_der = case.loads.beam_right_vgravity
    case.loads.beam_gravity_shear_between_hinges_izq = case.loads.beam_left_vgravity
    if beam_connection_sides == "left_only":
        case.loads.beam_gravity_shear_between_hinges = case.loads.beam_left_vgravity
    else:
        case.loads.beam_gravity_shear_between_hinges = case.loads.beam_right_vgravity
    if case.loads.shear_plastic_hinge is None:
        case.loads.shear_plastic_hinge = case.loads.shear_plastic_hinge_dermax

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
    tan_30 = math.tan(math.radians(30.0))
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
    stiffener_steel_type_vgder = case.materials.stiffener_steel_type_vgder
    stiffener_steel_type_vgizq = case.materials.stiffener_steel_type_vgizq
    if stiffener_steel_type_vgder is not None:
        stiffener_props_der = get_plate_steel_properties(
            steel_type=stiffener_steel_type_vgder,
            unit_system=case.units_system,
        )
        case.materials.stiffener_fy_vgder = stiffener_props_der["fy"]  # type: ignore[assignment]
        case.materials.stiffener_fy = stiffener_props_der["fy"]  # type: ignore[assignment]
    if stiffener_steel_type_vgizq is not None:
        stiffener_props_izq = get_plate_steel_properties(
            steel_type=stiffener_steel_type_vgizq,
            unit_system=case.units_system,
        )
        case.materials.stiffener_fy_vgizq = stiffener_props_izq["fy"]  # type: ignore[assignment]

    # Bolt strength/geometry are sourced from materials.xlsx/Pernos and sections.xlsx/Perno.
    beam_connection_sides = _canonical_beam_connection_sides(case.design_factors.beam_connection_sides)
    if beam_connection_sides is None:
        _raise_validation_error(
            message=(
                "Required input 'design_factors.beam_connection_sides' is missing or invalid for bolt "
                "catalog-driven properties."
            ),
            missing_fields=["design_factors.beam_connection_sides"],
            source_document="AISC 358-22",
        )
    active_side_tags = (
        ("vgder", "vgizq")
        if beam_connection_sides == "both_sides"
        else ("vgder",)
        if beam_connection_sides == "right_only"
        else ("vgizq",)
    )
    primary_side_tag = "vgder" if beam_connection_sides in {"right_only", "both_sides"} else "vgizq"

    def _require_side_or_common_material_text(
        *,
        field_root: str,
        side_tag: str,
        source_document: str,
        required_field_override: str | None = None,
    ) -> tuple[str, str]:
        side_field = f"{field_root}_{side_tag}"
        side_value = getattr(case.materials, side_field, None)
        if isinstance(side_value, str) and side_value.strip():
            return side_value.strip(), f"materials.{side_field}"
        common_value = getattr(case.materials, field_root, None)
        common_field = required_field_override or f"materials.{field_root}"
        common_text = _require_text(common_value, common_field, source_document)
        return common_text, common_field

    derived_db: Quantity | None = None
    for side_tag in active_side_tags:
        bolt_standard, bolt_standard_field = _require_side_or_common_material_text(
            field_root="bolt_fabrication_standard",
            side_tag=side_tag,
            source_document="data/materials.xlsx",
        )
        bolt_description, bolt_description_field = _require_side_or_common_material_text(
            field_root="bolt_description",
            side_tag=side_tag,
            source_document="data/materials.xlsx",
        )
        bolt_thread_condition, _ = _require_side_or_common_material_text(
            field_root="bolt_thread_condition",
            side_tag=side_tag,
            source_document="data/materials.xlsx",
            required_field_override="geometry.bolts.bolt_thread_condition",
        )
        bolt_thread_condition = bolt_thread_condition.upper()
        bolt_shape, bolt_shape_field = _require_side_or_common_material_text(
            field_root="bolt_shape",
            side_tag=side_tag,
            source_document="data/sections.xlsx",
        )

        bolt_strength = get_bolt_strength_properties(
            description=bolt_description,
            specification=bolt_standard,
            unit_system=case.units_system,
        )
        setattr(case.materials, f"bolt_fnt_{side_tag}", bolt_strength["fnt"])
        if bolt_thread_condition == "N":
            bolt_fnv = bolt_strength["fnv_threads_not_excluded"]
        elif bolt_thread_condition == "X":
            bolt_fnv = bolt_strength["fnv_threads_excluded"]
        else:
            _raise_validation_error(
                message=(
                    "Invalid input 'materials.bolt_thread_condition_<lado>'. "
                    "Expected 'N' (threads not excluded) or 'X' (threads excluded)."
                ),
                missing_fields=[f"materials.bolt_thread_condition_{side_tag}"],
                source_document="data/materials.xlsx",
            )
        setattr(case.materials, f"bolt_fnv_{side_tag}", bolt_fnv)

        bolt_geom = get_bolt_section_properties(bolt_shape=bolt_shape, unit_system=case.units_system)
        geom_standard = str(bolt_geom["fabrication_standard"] or "").strip()
        geom_description = str(bolt_geom["classification"])
        if geom_standard and normalize_text(geom_standard) != normalize_text(bolt_standard):
            _raise_validation_error(
                message=(
                    f"Mismatch between {bolt_standard_field}='{bolt_standard}' and sections/Perno standard "
                    f"'{geom_standard}' for shape '{bolt_shape}'."
                ),
                missing_fields=[bolt_standard_field, bolt_shape_field],
                source_document="data/sections.xlsx",
            )
        if normalize_text(geom_description) != normalize_text(bolt_description):
            _raise_validation_error(
                message=(
                    f"Mismatch between {bolt_description_field}='{bolt_description}' and sections/Perno "
                    f"classification '{geom_description}' for shape '{bolt_shape}'."
                ),
                missing_fields=[bolt_description_field, bolt_shape_field],
                source_document="data/sections.xlsx",
            )

        derived_db_side = bolt_geom["diameter_nominal"]  # type: ignore[assignment]
        side_db_field = f"bolt_diameter_{side_tag}"
        current_side_db = getattr(case.geometry, side_db_field, None)
        if current_side_db is not None and (
            current_side_db.unit != derived_db_side.unit or abs(current_side_db.value - derived_db_side.value) > 1e-9
        ):
            _raise_validation_error(
                message=(
                    f"Input 'geometry.{side_db_field}' must not contradict the selected bolt shape. "
                    f"Expected {derived_db_side.value} {derived_db_side.unit} from sections/Perno."
                ),
                missing_fields=[f"geometry.{side_db_field}", bolt_shape_field],
                source_document="data/sections.xlsx",
            )
        setattr(case.geometry, side_db_field, derived_db_side)

        if side_tag == primary_side_tag:
            derived_db = derived_db_side
            case.materials.bolt_fabrication_standard = bolt_standard
            case.materials.bolt_description = bolt_description
            case.materials.bolt_shape = bolt_shape
            case.materials.bolt_thread_condition = bolt_thread_condition
            case.materials.bolt_fnt = bolt_strength["fnt"]  # type: ignore[assignment]
            case.materials.bolt_fnv = bolt_fnv  # type: ignore[assignment]

    if derived_db is None:
        _raise_validation_error(
            message="Cannot derive bolt diameter from sections/Perno for active beam side(s).",
            missing_fields=["materials.bolt_shape"],
            source_document="data/sections.xlsx",
        )
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

    # lc for end plate / column flange is derived per active side under zero-guess policy.
    for side_tag in active_side_tags:
        side_suffix = "der" if side_tag == "vgder" else "izq"
        lc_ep_field = f"clear_distance_end_plate_{side_tag}"
        lc_cf_field = f"clear_distance_column_flange_{side_tag}"
        lc_ep_side = getattr(case.geometry, lc_ep_field, None)
        lc_cf_side = getattr(case.geometry, lc_cf_field, None)
        if lc_ep_side is not None and lc_cf_side is not None:
            continue

        pfo_side = getattr(case.geometry, f"pfo_{side_tag}", None) or case.geometry.pfo
        pfi_side = getattr(case.geometry, f"pfi_{side_tag}", None) or case.geometry.pfi
        pb_side = (
            getattr(case.geometry, f"pb_{side_tag}", None) or case.geometry.pb
            if case.connection_type == "bseep_8es"
            else None
        )
        db_side = getattr(case.geometry, f"bolt_diameter_{side_tag}", None) or derived_db
        if db_side is None:
            _raise_validation_error(
                message=f"Required input 'geometry.bolt_diameter_{side_tag}' is missing to derive clear distance.",
                missing_fields=[f"geometry.bolt_diameter_{side_tag}"],
                source_document="data/sections.xlsx",
            )

        uses_pb_in_lc = case.connection_type == "bseep_8es"
        if pfo_side is None or pfi_side is None or (uses_pb_in_lc and pb_side is None):
            _raise_validation_error(
                message=(
                    f"Cannot derive bolt clear distances on side '{side_suffix}'. Required inputs are missing: "
                    f"'geometry.pb_{side_tag}', 'geometry.pfo_{side_tag}', 'geometry.pfi_{side_tag}'."
                    if uses_pb_in_lc
                    else f"'geometry.pfo_{side_tag}', 'geometry.pfi_{side_tag}'."
                ),
                missing_fields=(
                    [f"geometry.pb_{side_tag}", f"geometry.pfo_{side_tag}", f"geometry.pfi_{side_tag}"]
                    if uses_pb_in_lc
                    else [f"geometry.pfo_{side_tag}", f"geometry.pfi_{side_tag}"]
                ),
                source_document="AISC 358-22 Section 6.7",
            )
        if uses_pb_in_lc and pb_side is not None and (pb_side.unit != pfo_side.unit or pb_side.unit != pfi_side.unit):
            _raise_validation_error(
                message=(
                    "Cannot derive bolt clear distances due to inconsistent units in "
                    f"'geometry.pb_{side_tag}', 'geometry.pfo_{side_tag}', and 'geometry.pfi_{side_tag}'."
                ),
                missing_fields=[f"geometry.pb_{side_tag}", f"geometry.pfo_{side_tag}", f"geometry.pfi_{side_tag}"],
                source_document="AISC 358-22 Section 6.7",
            )

        beam_shape_side = (
            (case.sections.beam_shape_der or case.sections.beam_shape)
            if side_tag == "vgder"
            else (case.sections.beam_shape_izq or case.sections.beam_shape)
        )
        beam_profile_for_lc = get_beam_profile_properties(beam_shape=beam_shape_side, unit_system=case.units_system)
        tbf = beam_profile_for_lc["tf"]
        reference_unit = pb_side.unit if uses_pb_in_lc and pb_side is not None else pfo_side.unit
        if tbf.unit != reference_unit:
            _raise_validation_error(
                message=(
                    "Cannot derive bolt clear distances due to inconsistent units between beam flange thickness "
                    f"(sections.{beam_shape_side}) and end-plate geometry inputs on side '{side_suffix}'."
                ),
                missing_fields=(
                    [f"sections.beam_shape_{side_suffix}", f"geometry.pb_{side_tag}"]
                    if uses_pb_in_lc
                    else [f"sections.beam_shape_{side_suffix}", f"geometry.pfo_{side_tag}"]
                ),
                source_document="data/sections.xlsx",
            )

        is_us = str(case.units_system.value).upper() == "US"
        db_in = db_side.value if is_us else db_side.value / 25.4
        hole_add_in = 1.0 / 16.0 if db_in <= (7.0 / 8.0 + 1e-9) else 1.0 / 8.0
        dh_value = (db_in + hole_add_in) if is_us else (db_in + hole_add_in) * 25.4

        lc_1 = (pb_side.value - dh_value) if uses_pb_in_lc and pb_side is not None else None
        lc_2 = pfo_side.value + pfi_side.value + tbf.value - dh_value
        lc_value = min(lc_1, lc_2) if lc_1 is not None else lc_2
        if lc_value <= 0.0:
            _raise_validation_error(
                message=(
                    f"Derived bolt clear distance is not positive on side '{side_suffix}'. "
                    "Expected min(pb-dh, pfo+pfi+tbf-dh) > 0."
                    if uses_pb_in_lc
                    else f"Derived bolt clear distance is not positive on side '{side_suffix}'. Expected pfo+pfi+tbf-dh > 0."
                ),
                missing_fields=(
                    [f"geometry.pb_{side_tag}", f"geometry.pfo_{side_tag}", f"geometry.pfi_{side_tag}", f"geometry.bolt_diameter_{side_tag}"]
                    if uses_pb_in_lc
                    else [f"geometry.pfo_{side_tag}", f"geometry.pfi_{side_tag}", f"geometry.bolt_diameter_{side_tag}"]
                ),
                source_document="AISC 360-22 Table J3.4 / AISC 358-22 Section 6.7",
            )
        derived_lc_side = Quantity(value=lc_value, unit=reference_unit)
        if lc_ep_side is None:
            setattr(case.geometry, lc_ep_field, derived_lc_side)
        if lc_cf_side is None:
            setattr(case.geometry, lc_cf_field, derived_lc_side)

    primary_lc_ep = getattr(case.geometry, f"clear_distance_end_plate_{primary_side_tag}", None)
    primary_lc_cf = getattr(case.geometry, f"clear_distance_column_flange_{primary_side_tag}", None)
    if primary_lc_ep is not None:
        case.geometry.clear_distance_end_plate = primary_lc_ep
    if primary_lc_cf is not None:
        case.geometry.clear_distance_column_flange = primary_lc_cf

    # Maintain legacy field used by Step 5 (no hidden default because it is derived from selected standard).
    case.materials.bolt_grade = case.materials.bolt_fabrication_standard


_MOMENT_SPLIT_RIGHT_SUFFIX = "_beam_right_only.json"
_MOMENT_SPLIT_LEFT_SUFFIX = "_beam_left_only.json"
_MOMENT_SPLIT_COLUMN_SUFFIX = "_column_and_common.json"


def _canonical_beam_connection_sides(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"left", "left_only", "izq", "izquierda", "solo_izquierda"}:
        return "left_only"
    if normalized in {"right", "right_only", "der", "derecha", "solo_derecha"}:
        return "right_only"
    if normalized in {"both", "both_sides", "ambas", "ambos_lados", "izq_der"}:
        return "both_sides"
    return None


def _first_dict(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] is not None:
            return payload[key]
    return None


def _compact_dict(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def _read_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at '{path}', got {type(payload).__name__}.")
    return payload


def _resolve_moment_prequalified_split_paths(input_path: Path) -> tuple[Path, Path | None, Path | None] | None:
    def _bundle_from_column_file(column_path: Path) -> tuple[Path, Path | None, Path | None] | None:
        name = column_path.name
        if not name.endswith(_MOMENT_SPLIT_COLUMN_SUFFIX):
            return None
        prefix = name[: -len(_MOMENT_SPLIT_COLUMN_SUFFIX)]
        right = column_path.parent / f"{prefix}{_MOMENT_SPLIT_RIGHT_SUFFIX}"
        left = column_path.parent / f"{prefix}{_MOMENT_SPLIT_LEFT_SUFFIX}"
        right_path = right if right.is_file() else None
        left_path = left if left.is_file() else None
        if right_path is not None or left_path is not None:
            return (column_path, right_path, left_path)
        return None

    if input_path.is_dir():
        for column_path in sorted(input_path.glob(f"*{_MOMENT_SPLIT_COLUMN_SUFFIX}")):
            bundle = _bundle_from_column_file(column_path)
            if bundle is not None:
                return bundle
        return None

    if not input_path.is_file():
        return None

    name = input_path.name
    parent = input_path.parent
    if name.endswith(_MOMENT_SPLIT_COLUMN_SUFFIX):
        return _bundle_from_column_file(input_path)
    if name.endswith(_MOMENT_SPLIT_RIGHT_SUFFIX):
        prefix = name[: -len(_MOMENT_SPLIT_RIGHT_SUFFIX)]
        column_path = parent / f"{prefix}{_MOMENT_SPLIT_COLUMN_SUFFIX}"
        left = parent / f"{prefix}{_MOMENT_SPLIT_LEFT_SUFFIX}"
        if column_path.is_file():
            return (column_path, input_path, left if left.is_file() else None)
    if name.endswith(_MOMENT_SPLIT_LEFT_SUFFIX):
        prefix = name[: -len(_MOMENT_SPLIT_LEFT_SUFFIX)]
        column_path = parent / f"{prefix}{_MOMENT_SPLIT_COLUMN_SUFFIX}"
        right = parent / f"{prefix}{_MOMENT_SPLIT_RIGHT_SUFFIX}"
        if column_path.is_file():
            return (column_path, right if right.is_file() else None, input_path)
    return None


def _normalize_moment_split_side_payload(raw_payload: dict[str, Any], *, side: str) -> dict[str, Any]:
    if isinstance(raw_payload.get("geometry"), dict):
        return deepcopy(raw_payload)

    side_tag = "vgder" if side == "right" else "vgizq"
    viga = _first_dict(raw_payload, "viga", "beam")
    factores = _first_dict(raw_payload, "design_factors", "factores_diseno")
    placa_extremo = _first_dict(raw_payload, "placa_extremo", "end_plate")
    platina_cont = _first_dict(raw_payload, "platina_continuidad", "continuity_plate")
    rigidizador = _first_dict(raw_payload, "rigidizador", "stiffener")
    pernos = _first_dict(raw_payload, "pernos", "bolts")
    soldaduras = _first_dict(raw_payload, "soldaduras", "welds")
    cargas = _first_dict(raw_payload, "loads", "cargas")
    weld_1_raw = soldaduras.get("weld_1") if isinstance(soldaduras.get("weld_1"), dict) else {}
    weld_2_raw = soldaduras.get("weld_2") if isinstance(soldaduras.get("weld_2"), dict) else {}
    weld_3_raw = soldaduras.get("weld_3") if isinstance(soldaduras.get("weld_3"), dict) else {}
    weld_4_raw = soldaduras.get("weld_4") if isinstance(soldaduras.get("weld_4"), dict) else {}

    sections = {}
    beam_shape = _first_present(viga, f"perfil_{side_tag}")
    if beam_shape is not None:
        sections["beam_shape"] = beam_shape

    weld_fexx = _first_present(
        weld_3_raw,
        f"Fexx_w3_{side_tag}",
    ) or _first_present(
        weld_2_raw,
        f"Fexx_w2_{side_tag}",
    ) or _first_present(
        weld_1_raw,
        f"Fexx_w1_{side_tag}",
    )

    materials = _compact_dict(
        {
            "profile_steel_type": _first_present(viga, f"tipo_acero_perfil_{side_tag}"),
            "plate_steel_type": _first_present(placa_extremo, "tipo_acero", "plate_steel_type")
            or _first_present(rigidizador, "tipo_acero", "plate_steel_type")
            or _first_present(platina_cont, "tipo_acero", "plate_steel_type"),
            f"stiffener_steel_type_{side_tag}": _first_present(
                rigidizador,
                f"tipo_acero_pest_{side_tag}",
            )
            or _first_present(rigidizador, "tipo_acero"),
            "bolt_fabrication_standard": _first_present(pernos, f"std_b_{side_tag}"),
            f"bolt_fabrication_standard_{side_tag}": _first_present(pernos, f"std_b_{side_tag}"),
            "bolt_description": _first_present(pernos, f"desc_b_{side_tag}"),
            f"bolt_description_{side_tag}": _first_present(pernos, f"desc_b_{side_tag}"),
            "weld_fexx": weld_fexx,
            f"weld_fexx_w4_{side_tag}": _first_present(
                weld_4_raw,
                f"Fexx_w4_{side_tag}",
            ),
            "elastic_modulus": _first_present(viga, f"E_{side_tag}"),
            "bolt_shape": _first_present(pernos, f"shape_b_{side_tag}"),
            f"bolt_shape_{side_tag}": _first_present(pernos, f"shape_b_{side_tag}"),
            "bolt_thread_condition": _first_present(pernos, f"thread_b_{side_tag}"),
            f"bolt_thread_condition_{side_tag}": _first_present(pernos, f"thread_b_{side_tag}"),
        }
    )

    side_block = _compact_dict(
        {
            "clear_span_length": _first_present(viga, f"Llb_{side_tag}"),
            "shear_connector_free_length_from_column_face": _first_present(
                viga,
                f"Lnc_{side_tag}",
            ),
        }
    )

    end_plate = _compact_dict(
        {
            "end_plate_width": _first_present(placa_extremo, f"Bpe_{side_tag}"),
            "end_plate_thickness": _first_present(placa_extremo, f"tpe_{side_tag}"),
            "de": _first_present(placa_extremo, f"de_pe_{side_tag}"),
            "pb": _first_present(placa_extremo, f"pb_pe_{side_tag}"),
            "pfo": _first_present(placa_extremo, f"pfo_pe_{side_tag}"),
            "pfi": _first_present(placa_extremo, f"pfi_pe_{side_tag}"),
        }
    )
    continuity_plate = _compact_dict(
        {
            "continuity_plate_thickness": _first_present(platina_cont, "t_pc_col", "tpc_col"),
            "continuity_plate_enabled": _first_present(
                platina_cont,
                "usar_pc_col",
            ),
        }
    )
    stiffener = _compact_dict(
        {
            "stiffener_thickness": _first_present(
                rigidizador,
                f"t_pest_{side_tag}",
                "stiffener_thickness",
            )
        }
    )
    bolts = _compact_dict(
        {
            "bolt_gage": _first_present(pernos, f"g_b_{side_tag}"),
            "bolt_tightening_type": _first_present(pernos, f"tipo_apriete_b_{side_tag}"),
            f"bolt_tightening_type_{side_tag}": _first_present(pernos, f"tipo_apriete_b_{side_tag}"),
            "clear_distance_end_plate": _first_present(pernos, f"lc_pe_{side_tag}"),
            "clear_distance_column_flange": _first_present(
                pernos,
                f"lc_cf_{side_tag}",
            ),
            "bolt_shape": _first_present(pernos, f"shape_b_{side_tag}"),
            "bolt_thread_condition": _first_present(pernos, f"thread_b_{side_tag}"),
        }
    )
    welds: dict[str, Any] = {}
    weld_1 = _compact_dict(
        {
            "description": _first_present(weld_1_raw, "description"),
            "weld_type": _first_present(weld_1_raw, f"tipo_w1_{side_tag}", "weld_type"),
            "size": _first_present(weld_1_raw, f"w_w1_{side_tag}", "size"),
            "nl": _first_present(weld_1_raw, f"nl_w1_{side_tag}", "nl"),
            f"L_gap_w1_{side_tag}": _first_present(
                weld_1_raw,
                f"L_gap_w1_{side_tag}",
                "L_gap_w1",
                "l_gap",
                "gap",
            ),
            f"kds_w1_{side_tag}": _first_present(weld_1_raw, f"kds_w1_{side_tag}", "kds"),
        }
    )
    if weld_1:
        welds["weld_1"] = weld_1
    weld_2 = _compact_dict(
        {
            "description": _first_present(weld_2_raw, "description"),
            "weld_type": _first_present(weld_2_raw, f"tipo_w2_{side_tag}", "weld_type"),
            "size": _first_present(weld_2_raw, f"w_w2_{side_tag}", "size"),
            "nl": _first_present(weld_2_raw, f"nl_w2_{side_tag}", "nl"),
            f"L_gap_w2_{side_tag}": _first_present(
                weld_2_raw,
                f"L_gap_w2_{side_tag}",
                "L_gap_w2",
                "l_gap",
                "gap",
            ),
            f"kds_w2_{side_tag}": _first_present(weld_2_raw, f"kds_w2_{side_tag}", "kds"),
        }
    )
    if weld_2:
        welds["weld_2"] = weld_2
    weld_3 = _compact_dict(
        {
            "description": _first_present(weld_3_raw, "description"),
            "weld_type": _first_present(weld_3_raw, f"tipo_w3_{side_tag}", "weld_type"),
            "thickness": _first_present(weld_3_raw, f"t_w3_{side_tag}", "thickness"),
            "nl": _first_present(weld_3_raw, f"nl_w3_{side_tag}", "nl"),
            f"kds_w3_{side_tag}": _first_present(weld_3_raw, f"kds_w3_{side_tag}", "kds"),
        }
    )
    if weld_3:
        welds["weld_3"] = weld_3
    weld_4 = _compact_dict(
        {
            "description": _first_present(weld_4_raw, "description"),
            "weld_type": _first_present(weld_4_raw, f"tipo_w4_{side_tag}", "weld_type"),
            "thickness": _first_present(weld_4_raw, f"t_w4_{side_tag}", "thickness"),
            "nl": _first_present(weld_4_raw, f"nl_w4_{side_tag}", "nl"),
            "backing_thickness": _first_present(
                weld_4_raw,
                f"t_w4_1_{side_tag}",
                f"t_w4.1_{side_tag}",
                "backing_thickness",
            ),
            f"kds_w4_{side_tag}": _first_present(weld_4_raw, f"kds_w4_{side_tag}", "kds"),
        }
    )
    if weld_4:
        welds["weld_4"] = weld_4

    geometry: dict[str, Any] = {}
    if side_block:
        geometry[f"beam_{side}"] = side_block
    if end_plate:
        geometry["end_plate"] = end_plate
    if continuity_plate:
        geometry["continuity_plate"] = continuity_plate
    if stiffener:
        geometry["stiffener"] = stiffener
    if bolts:
        geometry["bolts"] = bolts
    if welds:
        geometry["welds"] = welds

    loads = _compact_dict(
        {
            "pu_viga_right" if side == "right" else "pu_viga_left": _first_present(
                cargas,
                f"Pu_{side_tag}",
            )
            or _first_present(viga, f"Pu_{side_tag}"),
            f"Vu2_{side_tag}": _first_present(
                cargas,
                f"Vu2_{side_tag}",
            )
            or _first_present(viga, f"Vu2_{side_tag}"),
            f"Mu3_{side_tag}": _first_present(
                cargas,
                f"Mu3_{side_tag}",
            )
            or _first_present(viga, f"Mu3_{side_tag}"),
            "beam_right_vgravity" if side == "right" else "beam_left_vgravity": _first_present(
                cargas,
                f"Vg_{side_tag}",
            )
            or _first_present(viga, f"Vg_{side_tag}"),
        }
    )

    normalized: dict[str, Any] = {}
    if sections:
        normalized["sections"] = sections
    if materials:
        normalized["materials"] = materials
    if geometry:
        normalized["geometry"] = geometry
    if loads:
        normalized["loads"] = loads
    side_design_factors = _compact_dict(
        {
            "member_ductility_demand_beam": _first_present(viga, f"demanda_ductilidad_{side_tag}")
            or _first_present(factores, f"demanda_ductilidad_{side_tag}"),
            f"member_ductility_demand_beam_{side_tag}": _first_present(viga, f"demanda_ductilidad_{side_tag}")
            or _first_present(factores, f"demanda_ductilidad_{side_tag}"),
        }
    )
    if side_design_factors:
        normalized["design_factors"] = side_design_factors
    return normalized


def _normalize_moment_split_column_payload(raw_payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw_payload.get("geometry"), dict):
        return deepcopy(raw_payload)

    columna = _first_dict(raw_payload, "columna", "column")
    platina_cont = _first_dict(raw_payload, "platina_continuidad", "continuity_plate")
    platina_dobladora = _first_dict(
        raw_payload,
        "platina_enchape_alma",
        "platina_de_enchape_del_alma",
        "platina_dobladora",
        "doubler_plate",
    )
    soldaduras = _first_dict(raw_payload, "soldaduras", "welds")
    cargas = _first_dict(raw_payload, "loads", "cargas")
    factores = _first_dict(raw_payload, "design_factors", "factores_diseno")
    weld_5_raw = _first_dict(raw_payload, "weld_5")
    if not weld_5_raw:
        weld_5_raw = soldaduras.get("weld_5") if isinstance(soldaduras.get("weld_5"), dict) else {}
    if not weld_5_raw:
        # Legacy fallback: column continuity weld was previously stored as weld_4.
        weld_5_raw = soldaduras.get("weld_4") if isinstance(soldaduras.get("weld_4"), dict) else {}
    weld_6_raw = _first_dict(raw_payload, "weld_6")
    if not weld_6_raw:
        weld_6_raw = soldaduras.get("weld_6") if isinstance(soldaduras.get("weld_6"), dict) else {}
    weld_dp_plug_raw = (
        _first_dict(
            raw_payload,
            "weld_7",
            "soldadura_7",
            "weld_dp_plug",
            "soldadura_plug_dp",
            "weld_dp_plugweld_dp_plug",
        )
        or (
            soldaduras.get("weld_7")
            if isinstance(soldaduras.get("weld_7"), dict)
            else (
                soldaduras.get("weld_dp_plug")
                if isinstance(soldaduras.get("weld_dp_plug"), dict)
                else {}
            )
        )
    )
    if not weld_dp_plug_raw:
        weld_dp_plug_raw = (
            soldaduras.get("soldadura_plug_dp")
            if isinstance(soldaduras.get("soldadura_plug_dp"), dict)
            else {}
        )

    normalized: dict[str, Any] = {}
    for key in (
        "project_id",
        "case_id",
        "design_code_context",
        "units_system",
        "connection_family",
        "connection_type",
        "load_state",
    ):
        if key in raw_payload:
            normalized[key] = raw_payload[key]

    sections = _compact_dict({"column_shape": _first_present(columna, "perfil_col")})
    if sections:
        normalized["sections"] = sections

    materials = _compact_dict(
        {
            "profile_steel_type": _first_present(columna, "tipo_acero_perfil_col"),
            "weld_fexx": _first_present(weld_5_raw, "Fexx_w5_col")
            or _first_present(weld_5_raw, "Fexx_w5")
            or _first_present(weld_5_raw, "Fexx_w4")
            or _first_present(weld_6_raw, "Fexx_w6_col")
            or _first_present(weld_6_raw, "Fexx_w6")
            or _first_present(soldaduras, "Fexx_w5_col")
            or _first_present(soldaduras, "Fexx_w5")
            or _first_present(soldaduras, "Fexx_w4")
            or _first_present(soldaduras, "Fexx_w6_col")
            or _first_present(soldaduras, "Fexx_w6")
            or _first_present(weld_dp_plug_raw, "Fexx_wdp_plug")
            or _first_present(weld_dp_plug_raw, "Fexx_w7_col")
            or _first_present(soldaduras, "Fexx_wdp_plug")
            or _first_present(soldaduras, "Fexx_w7_col")
            or _first_present(raw_payload, "Fexx_wdp_plug")
            or _first_present(raw_payload, "Fexx_w7_col"),
            "elastic_modulus": _first_present(columna, "E_col"),
            "plate_steel_type": _first_present(platina_cont, "tipo_acero_pc_col"),
            "continuity_plate_steel_type": _first_present(platina_cont, "tipo_acero_pc_col"),
            "doubler_plate_steel_type": _first_present(platina_dobladora, "tipo_acero_dp_col"),
        }
    )
    if materials:
        normalized["materials"] = materials

    column_block = _compact_dict(
        {
            "column_end_distance_to_beam_flange": _first_present(
                columna,
                "St_col",
            ),
            "slab_connection_condition": _first_present(
                columna,
                "union_col_losa",
            ),
            "panel_zone_inelastic_deformation_considered": _first_present(
                columna,
                "consideracion_deformacion_inelastica_zona_panel",
                "considera_deformacion_inelastica_panel_zone",
                "panel_zone_inelastic_deformation_considered",
            ),
            "panel_zone_equation_package": _first_present(
                columna,
                "paquete_wpzs_col",
                "paquete_wpzs",
                "paquete_ecuaciones_wpzs",
                "panel_zone_equation_package",
            ),
            "hb_col": _first_present(
                columna,
                "hb_col",
                "h_b_col",
            ),
            "ht_col": _first_present(
                columna,
                "ht_col",
                "h_t_col",
            ),
        }
    )
    continuity_plate_enabled = _first_present(
        platina_cont,
        "usar_pc_col",
    )
    if continuity_plate_enabled is None:
        continuity_plate_enabled = _first_present(
            columna,
            "usar_pc_col",
        )
    doubler_plate_enabled = _first_present(
        platina_dobladora,
        "usar_dp_col",
    )
    if doubler_plate_enabled is None:
        doubler_plate_enabled = _first_present(
            columna,
            "usar_dp_col",
        )

    geometry = _compact_dict(
        {
            "column": column_block if column_block else None,
            "continuity_plate": _compact_dict(
                {
                    "continuity_plate_thickness": _first_present(
                        platina_cont,
                        "t_pc_col",
                        "tpc_col",
                    ),
                    "continuity_plate_width_b1": _first_present(
                        platina_cont,
                        "b1_pc_col",
                    ),
                    "continuity_plate_count": _first_present(
                        platina_cont,
                        "n_pc_col",
                        "continuity_plate_count",
                    ),
                    "continuity_plate_enabled": continuity_plate_enabled,
                    "continuity_plate_weld_type": _first_present(
                        weld_5_raw,
                        "tipo_w5_col",
                        "tipo_w5",
                        "tipo_w4",
                        "weld_type",
                        "tipo_soldadura",
                    ),
                    "continuity_plate_weld_type_col": _first_present(
                        weld_5_raw,
                        "tipo_w5_col",
                        "tipo_w5",
                        "weld_type",
                        "tipo_soldadura",
                    ),
                    "w_w5_col": _first_present(
                        weld_5_raw,
                        "w_w5_col",
                        "t_w5_col",
                        "t_w5",
                        "thickness",
                        "size",
                    ),
                    "t_w5_col": _first_present(
                        weld_5_raw,
                        "w_w5_col",
                        "t_w5_col",
                        "t_w5",
                        "thickness",
                        "size",
                    ),
                    "nl_w5_col": _first_present(
                        weld_5_raw,
                        "nl_w5_col",
                        "nl_w5",
                        "nl",
                        "n_l",
                        "lines",
                    ),
                    "L_gap_w5_col": _first_present(
                        weld_5_raw,
                        "L_gap_w5_col",
                        "L_gap_w5",
                        "l_gap",
                        "gap",
                    ),
                    "kds_w5_col": _first_present(
                        weld_5_raw,
                        "kds_w5_col",
                        "kds_w5",
                    ),
                    "continuity_plate_web_weld_type_col": _first_present(
                        weld_6_raw,
                        "tipo_w6_col",
                        "tipo_w6",
                        "weld_type",
                        "tipo_soldadura",
                    ),
                    "w_w6_col": _first_present(
                        weld_6_raw,
                        "w_w6_col",
                        "t_w6_col",
                        "t_w6",
                        "thickness",
                        "size",
                    ),
                    "t_w6_col": _first_present(
                        weld_6_raw,
                        "w_w6_col",
                        "t_w6_col",
                        "t_w6",
                        "thickness",
                        "size",
                    ),
                    "nl_w6_col": _first_present(
                        weld_6_raw,
                        "nl_w6_col",
                        "nl_w6",
                        "nl",
                        "n_l",
                        "lines",
                    ),
                    "L_gap_w6_col": _first_present(
                        weld_6_raw,
                        "L_gap_w6_col",
                        "L_gap_w6",
                        "l_gap",
                        "gap",
                    ),
                    "kds_w6_col": _first_present(
                        weld_6_raw,
                        "kds_w6_col",
                        "kds_w6",
                    ),
                }
            )
            or None,
            "doubler_plate": _compact_dict(
                {
                    "doubler_plate_thickness": _first_present(
                        platina_dobladora,
                        "t_dp_col",
                        "tdp_col",
                    ),
                    "doubler_plate_count": _first_present(
                        platina_dobladora,
                        "n_dp_col",
                    ),
                    "doubler_plate_enabled": doubler_plate_enabled,
                    "doubler_plate_web_plug_weld_type": _first_present(
                        weld_dp_plug_raw,
                        "tipo_w7_col",
                        "tipo_wdp_plug",
                        "weld_type",
                        "tipo_soldadura",
                    ),
                    "doubler_plate_web_plug_weld_size": _first_present(
                        weld_dp_plug_raw,
                        "w_w7_col",
                        "t_w7_col",
                        "t_wdp_plug",
                        "thickness",
                        "size",
                    ),
                    "w_w7_col": _first_present(
                        weld_dp_plug_raw,
                        "w_w7_col",
                        "t_w7_col",
                        "t_wdp_plug",
                        "thickness",
                        "size",
                    ),
                    "doubler_plate_web_plug_weld_lines_nl": _first_present(
                        weld_dp_plug_raw,
                        "nl_w7_col",
                        "nl_wdp_plug",
                        "nl",
                        "n_l",
                        "lines",
                    ),
                }
            )
            or None,
        }
    )
    if geometry:
        normalized["geometry"] = geometry

    pu_columna = _first_present(cargas, "Pu_col") or _first_present(columna, "Pu_col")
    loads: dict[str, Any] = _compact_dict({"pu_columna": pu_columna})
    for key in (
        "probable_moment_column_face",
        "probable_moment_plastic_hinge",
        "shear_plastic_hinge_dermax",
        "shear_plastic_hinge_dermin",
        "shear_plastic_hinge_izqmax",
        "shear_plastic_hinge_izqmin",
        "shear_plastic_hinge",
        "beam_gravity_shear_between_hinges_der",
        "beam_gravity_shear_between_hinges_izq",
        "beam_gravity_shear_between_hinges",
        "beam_gravity_shear_face_segment",
    ):
        value = _first_present(cargas, key)
        if value is not None:
            loads[key] = value
    if loads:
        normalized["loads"] = loads
    design_factors = dict(factores) if factores else {}
    if "lados_conexion" in design_factors and "beam_connection_sides" not in design_factors:
        design_factors["beam_connection_sides"] = design_factors["lados_conexion"]
    if "demanda_ductilidad_col" in design_factors and "member_ductility_demand_column" not in design_factors:
        design_factors["member_ductility_demand_column"] = design_factors["demanda_ductilidad_col"]
    if "ratio_McMb_min" in design_factors and "column_beam_moment_ratio_minimum" not in design_factors:
        design_factors["column_beam_moment_ratio_minimum"] = design_factors["ratio_McMb_min"]
    if "ratio_McMb" in design_factors and "column_beam_moment_ratio" not in design_factors:
        design_factors["column_beam_moment_ratio"] = design_factors["ratio_McMb"]

    phi_no_ductil = _first_present(design_factors, "phi_no_ductil", "phi_non_ductile")
    phi_ductil = _first_present(design_factors, "phi_ductil", "phi_ductile")
    phi_fragil = _first_present(design_factors, "phi_fragil", "phi_fragile")
    if phi_no_ductil is not None and "phi_n" not in design_factors:
        design_factors["phi_n"] = phi_no_ductil
    if phi_ductil is not None and "phi_d" not in design_factors:
        design_factors["phi_d"] = phi_ductil
    if phi_fragil is not None and "phi_f" not in design_factors:
        design_factors["phi_f"] = phi_fragil
    design_factors.pop("phi_no_ductil", None)
    design_factors.pop("phi_non_ductile", None)
    design_factors.pop("phi_ductil", None)
    design_factors.pop("phi_ductile", None)
    design_factors.pop("phi_fragil", None)
    design_factors.pop("phi_fragile", None)
    design_factors.pop("lados_conexion", None)
    design_factors.pop("demanda_ductilidad_col", None)
    design_factors.pop("ratio_McMb_min", None)
    design_factors.pop("ratio_McMb", None)
    if design_factors:
        normalized["design_factors"] = design_factors
    return normalized


def _require_dict_key(payload: dict[str, Any], key: str, context: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Missing object '{key}' in {context}.")
    return value


def _assert_same(right_value: Any, left_value: Any, label: str) -> None:
    if right_value != left_value:
        raise ValueError(
            f"Mismatch between right and left split inputs for '{label}'. "
            "Both sides must provide the same shared values."
        )


def _compose_moment_prequalified_split_payload(
    *,
    column_raw: dict[str, Any],
    right_raw: dict[str, Any] | None,
    left_raw: dict[str, Any] | None,
    beam_connection_sides: str,
) -> dict[str, Any]:
    column_payload = _normalize_moment_split_column_payload(column_raw)
    right_payload = (
        _normalize_moment_split_side_payload(right_raw, side="right")
        if isinstance(right_raw, dict)
        else None
    )
    left_payload = (
        _normalize_moment_split_side_payload(left_raw, side="left")
        if isinstance(left_raw, dict)
        else None
    )

    merged = deepcopy(column_payload)
    connection_family = merged.get("connection_family")
    if not isinstance(connection_family, str) or not connection_family.strip():
        raise ValueError(
            "Missing text field 'connection_family' in column split payload. "
            "No default value is allowed under zero-guess policy."
        )
    load_state = merged.get("load_state")
    if not isinstance(load_state, str) or not load_state.strip():
        raise ValueError(
            "Missing text field 'load_state' in column split payload. "
            "No default value is allowed under zero-guess policy."
        )

    if beam_connection_sides not in {"left_only", "right_only", "both_sides"}:
        raise ValueError(
            "Invalid or missing 'design_factors.beam_connection_sides' in column split payload. "
            "Expected 'left_only', 'right_only' or 'both_sides' (aliases accepted)."
        )
    if beam_connection_sides == "both_sides" and (right_payload is None or left_payload is None):
        raise ValueError(
            "beam_connection_sides='both_sides' requires both split files: "
            "*_beam_right_only.json and *_beam_left_only.json."
        )
    if beam_connection_sides == "right_only" and right_payload is None:
        raise ValueError(
            "beam_connection_sides='right_only' requires split file *_beam_right_only.json."
        )
    if beam_connection_sides == "left_only" and left_payload is None:
        raise ValueError(
            "beam_connection_sides='left_only' requires split file *_beam_left_only.json."
        )

    if not isinstance(merged.get("sections"), dict):
        merged["sections"] = {}
    merged_sections = _require_dict_key(merged, "sections", "column split payload")
    right_sections = (
        _require_dict_key(right_payload, "sections", "right beam split payload")
        if isinstance(right_payload, dict)
        else {}
    )
    left_sections = (
        _require_dict_key(left_payload, "sections", "left beam split payload")
        if isinstance(left_payload, dict)
        else {}
    )
    right_beam_shape = right_sections.get("beam_shape")
    left_beam_shape = left_sections.get("beam_shape")
    if right_beam_shape is not None:
        if not isinstance(right_beam_shape, str) or not right_beam_shape.strip():
            raise ValueError("Invalid text field 'sections.beam_shape' in right beam split payload.")
        merged_sections["beam_shape_der"] = right_beam_shape
    if left_beam_shape is not None:
        if not isinstance(left_beam_shape, str) or not left_beam_shape.strip():
            raise ValueError("Invalid text field 'sections.beam_shape' in left beam split payload.")
        merged_sections["beam_shape_izq"] = left_beam_shape
    if beam_connection_sides in {"right_only", "both_sides"}:
        if not isinstance(merged_sections.get("beam_shape_der"), str):
            raise ValueError("Missing text field 'sections.beam_shape' in right beam split payload.")
        merged_sections["beam_shape"] = merged_sections["beam_shape_der"]
    else:
        if not isinstance(merged_sections.get("beam_shape_izq"), str):
            raise ValueError("Missing text field 'sections.beam_shape' in left beam split payload.")
        merged_sections["beam_shape"] = merged_sections["beam_shape_izq"]

    if not isinstance(merged.get("materials"), dict):
        merged["materials"] = {}
    merged_materials = _require_dict_key(merged, "materials", "column split payload")
    right_materials = (
        _require_dict_key(right_payload, "materials", "right beam split payload")
        if isinstance(right_payload, dict)
        else {}
    )
    left_materials = (
        _require_dict_key(left_payload, "materials", "left beam split payload")
        if isinstance(left_payload, dict)
        else {}
    )
    merged_materials.update(right_materials)
    merged_materials.update(left_materials)

    if not isinstance(merged.get("geometry"), dict):
        merged["geometry"] = {}
    merged_geometry = _require_dict_key(merged, "geometry", "column split payload")
    right_geometry = (
        _require_dict_key(right_payload, "geometry", "right beam split payload")
        if isinstance(right_payload, dict)
        else {}
    )
    left_geometry = (
        _require_dict_key(left_payload, "geometry", "left beam split payload")
        if isinstance(left_payload, dict)
        else {}
    )
    if right_geometry:
        merged_geometry["beam_right"] = _require_dict_key(right_geometry, "beam_right", "right beam split geometry")
    if left_geometry:
        merged_geometry["beam_left"] = _require_dict_key(left_geometry, "beam_left", "left beam split geometry")

    connection_type = str(merged.get("connection_type", "")).strip().lower()
    requires_stiffener = connection_type in {"bseep_4es", "bseep_8es"}

    primary_side = "right" if beam_connection_sides in {"right_only", "both_sides"} else "left"
    primary_geometry = right_geometry if primary_side == "right" else left_geometry

    group_names = ["end_plate", "bolts", "continuity_plate"]
    if requires_stiffener:
        group_names.append("stiffener")
    elif "stiffener" in right_geometry or "stiffener" in left_geometry:
        group_names.append("stiffener")

    for group_name in group_names:
        primary_group = (
            _require_dict_key(primary_geometry, group_name, f"{primary_side} beam split geometry")
            if isinstance(primary_geometry, dict) and group_name in primary_geometry
            else None
        )
        if primary_group is not None:
            merged_geometry[group_name] = primary_group

    right_welds = (
        _require_dict_key(right_geometry, "welds", "right beam split geometry")
        if isinstance(right_geometry, dict) and "welds" in right_geometry
        else {}
    )
    left_welds = (
        _require_dict_key(left_geometry, "welds", "left beam split geometry")
        if isinstance(left_geometry, dict) and "welds" in left_geometry
        else {}
    )
    merged_welds: dict[str, Any] = {}
    required_weld_names = ["weld_3", "weld_4"]
    if requires_stiffener:
        required_weld_names = ["weld_1", "weld_2", "weld_3", "weld_4"]
    for weld_name in required_weld_names:
        right_weld = (
            _require_dict_key(right_welds, weld_name, "right beam split geometry.welds")
            if weld_name in right_welds
            else {}
        )
        left_weld = (
            _require_dict_key(left_welds, weld_name, "left beam split geometry.welds")
            if weld_name in left_welds
            else {}
        )
        if beam_connection_sides == "both_sides" and (not right_weld or not left_weld):
            raise ValueError(f"Missing '{weld_name}' in split weld inputs for both_sides.")
        merged_block: dict[str, Any] = {}
        if primary_side == "left":
            if isinstance(right_weld, dict):
                merged_block.update(right_weld)
            if isinstance(left_weld, dict):
                merged_block.update(left_weld)
        else:
            if isinstance(left_weld, dict):
                merged_block.update(left_weld)
            if isinstance(right_weld, dict):
                merged_block.update(right_weld)
        if merged_block:
            merged_welds[weld_name] = merged_block
    if merged_welds:
        merged_geometry["welds"] = merged_welds

    merged_loads = dict(_require_dict_key(merged, "loads", "column split payload"))
    if isinstance(right_payload, dict):
        merged_loads.update(_require_dict_key(right_payload, "loads", "right beam split payload"))
    if isinstance(left_payload, dict):
        merged_loads.update(_require_dict_key(left_payload, "loads", "left beam split payload"))
    merged["loads"] = merged_loads

    if not isinstance(merged.get("design_factors"), dict):
        merged["design_factors"] = {}
    merged_design_factors = _require_dict_key(merged, "design_factors", "column split payload")

    right_design_factors = right_payload.get("design_factors") if isinstance(right_payload, dict) else None
    if not isinstance(right_design_factors, dict):
        right_design_factors = {}
    left_design_factors = left_payload.get("design_factors") if isinstance(left_payload, dict) else None
    if not isinstance(left_design_factors, dict):
        left_design_factors = {}

    merged_design_factors.update(right_design_factors)
    merged_design_factors.update(left_design_factors)
    merged_design_factors["beam_connection_sides"] = beam_connection_sides

    def _side_group(payload: dict[str, Any], group: str) -> dict[str, Any]:
        value = payload.get(group)
        return value if isinstance(value, dict) else {}

    right_end_plate = _side_group(right_geometry, "end_plate")
    left_end_plate = _side_group(left_geometry, "end_plate")
    right_bolts = _side_group(right_geometry, "bolts")
    left_bolts = _side_group(left_geometry, "bolts")
    right_stiffener = _side_group(right_geometry, "stiffener")
    left_stiffener = _side_group(left_geometry, "stiffener")

    side_flat_map = {
        "vgder": (right_end_plate, right_bolts, right_stiffener, right_welds),
        "vgizq": (left_end_plate, left_bolts, left_stiffener, left_welds),
    }
    for side_tag, (end_plate_group, bolt_group, stiffener_group, welds_group) in side_flat_map.items():
        if end_plate_group:
            merged_geometry[f"end_plate_width_{side_tag}"] = end_plate_group.get("end_plate_width")
            merged_geometry[f"end_plate_thickness_{side_tag}"] = end_plate_group.get("end_plate_thickness")
            merged_geometry[f"de_{side_tag}"] = end_plate_group.get("de")
            merged_geometry[f"pb_{side_tag}"] = end_plate_group.get("pb")
            merged_geometry[f"pfo_{side_tag}"] = end_plate_group.get("pfo")
            merged_geometry[f"pfi_{side_tag}"] = end_plate_group.get("pfi")
        if bolt_group:
            merged_geometry[f"bolt_gage_{side_tag}"] = bolt_group.get("bolt_gage")
            merged_geometry[f"bolt_tightening_type_{side_tag}"] = (
                bolt_group.get(f"bolt_tightening_type_{side_tag}") or bolt_group.get("bolt_tightening_type")
            )
            merged_geometry[f"clear_distance_end_plate_{side_tag}"] = bolt_group.get("clear_distance_end_plate")
            merged_geometry[f"clear_distance_column_flange_{side_tag}"] = bolt_group.get("clear_distance_column_flange")
        if stiffener_group:
            merged_geometry[f"stiffener_thickness_{side_tag}"] = stiffener_group.get("stiffener_thickness")
        if isinstance(welds_group, dict):
            weld_1 = _side_group(welds_group, "weld_1")
            weld_2 = _side_group(welds_group, "weld_2")
            weld_3 = _side_group(welds_group, "weld_3")
            weld_4 = _side_group(welds_group, "weld_4")
            if weld_1:
                merged_geometry[f"end_plate_stiffener_weld_type_{side_tag}"] = weld_1.get("weld_type")
                merged_geometry[f"end_plate_stiffener_weld_size_wst_{side_tag}"] = weld_1.get("size")
                merged_geometry[f"end_plate_stiffener_weld_lines_nl_{side_tag}"] = weld_1.get("nl")
                merged_geometry[f"L_gap_w1_{side_tag}"] = (
                    weld_1.get(f"L_gap_w1_{side_tag}")
                    or weld_1.get("L_gap_w1")
                )
            if weld_2:
                merged_geometry[f"beam_stiffener_weld_type_{side_tag}"] = weld_2.get("weld_type")
                merged_geometry[f"beam_stiffener_weld_size_wst2_{side_tag}"] = weld_2.get("size")
                merged_geometry[f"beam_stiffener_weld_lines_nl_w2_{side_tag}"] = weld_2.get("nl")
                merged_geometry[f"L_gap_w2_{side_tag}"] = (
                    weld_2.get(f"L_gap_w2_{side_tag}")
                    or weld_2.get("L_gap_w2")
                )
            if weld_3:
                merged_geometry[f"end_plate_beam_web_weld_type_{side_tag}"] = weld_3.get("weld_type")
                merged_geometry[f"end_plate_beam_web_weld_thickness_twe_{side_tag}"] = weld_3.get("thickness")
                merged_geometry[f"end_plate_beam_web_weld_lines_nl_{side_tag}"] = weld_3.get("nl")
            if weld_4:
                merged_geometry[f"tipo_w4_{side_tag}"] = weld_4.get("weld_type")
                merged_geometry[f"t_w4_{side_tag}"] = weld_4.get("thickness")
                merged_geometry[f"nl_w4_{side_tag}"] = weld_4.get("nl")
                merged_geometry[f"t_w4_1_{side_tag}"] = weld_4.get("backing_thickness")
    merged["geometry"] = _compact_dict(merged_geometry)

    return merged


def _load_moment_prequalified_split_payload(input_path: Path) -> dict[str, Any] | None:
    split_paths = _resolve_moment_prequalified_split_paths(input_path)
    if split_paths is None:
        return None
    column_path, right_path, left_path = split_paths
    column_raw = _read_json_object(column_path)
    design_factors_raw = column_raw.get("design_factors")
    if not isinstance(design_factors_raw, dict):
        design_factors_raw = column_raw.get("factores_diseno")
    if not isinstance(design_factors_raw, dict):
        raise ValueError(
            "Missing object 'design_factors' (or 'factores_diseno') in column split payload."
        )
    beam_connection_sides = _canonical_beam_connection_sides(
        design_factors_raw.get("beam_connection_sides")
        if design_factors_raw.get("beam_connection_sides") is not None
        else design_factors_raw.get("lados_conexion")
    )
    if beam_connection_sides is None:
        raise ValueError(
            "Invalid or missing 'design_factors.beam_connection_sides' in column split payload. "
            "Expected 'left_only', 'right_only' or 'both_sides' (aliases accepted)."
        )

    right_raw = _read_json_object(right_path) if right_path is not None else None
    left_raw = _read_json_object(left_path) if left_path is not None else None
    return _compose_moment_prequalified_split_payload(
        column_raw=column_raw,
        right_raw=right_raw,
        left_raw=left_raw,
        beam_connection_sides=beam_connection_sides,
    )


def load_input_payload(path: str | Path) -> dict[str, Any]:
    input_path = Path(path)
    try:
        split_payload = _load_moment_prequalified_split_payload(input_path)
        if split_payload is not None:
            return split_payload
        if input_path.is_dir():
            raise OSError(
                "Input path is a directory but no valid split-input bundle was found. "
                "Expected files: *_column_and_common.json plus active side files according to "
                "design_factors.beam_connection_sides "
                "(*_beam_right_only.json, *_beam_left_only.json, or both)."
            )
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
    except ValueError as exc:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=None,
                message=f"Invalid split-input bundle: {exc}",
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
    if case.connection_family == "Fully_Restrained_Moment" and ("aisc" not in primary_doc or "360" not in primary_doc):
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["design_code_context.primary_document"],
                message="Fully restrained moment cases require AISC 360 as primary document.",
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
    normalized_payload = _normalize_connection_family_payload(payload)
    normalized_payload = _normalize_fully_restrained_splice_payload(normalized_payload)
    normalized_payload = _normalize_moment_geometry_payload(normalized_payload)
    normalized_payload = _normalize_moment_loads_payload(normalized_payload)
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
