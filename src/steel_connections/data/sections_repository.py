from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

from steel_connections.data.xlsx_sheet_reader import normalize_text, read_sheet_rows
from steel_connections.models.errors import ErrorCode, Stage, StructuredEngineException, StructuredError
from steel_connections.models.units import Quantity, UnitSystem

XLSX_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _col_ref_to_index(col_ref: str) -> int:
    value = 0
    for char in col_ref:
        value = value * 26 + (ord(char.upper()) - ord("A") + 1)
    return value


def _shared_strings_from_archive(archive: zipfile.ZipFile) -> list[str]:
    shared_path = "xl/sharedStrings.xml"
    if shared_path not in archive.namelist():
        return []

    root = ET.fromstring(archive.read(shared_path))
    strings: list[str] = []
    for si in root.findall(f"{{{XLSX_NS}}}si"):
        text_parts = [node.text or "" for node in si.findall(f".//{{{XLSX_NS}}}t")]
        strings.append("".join(text_parts))
    return strings


def _cell_value(cell: ET.Element, shared_strings: list[str]) -> str | float | None:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        text_node = cell.find(f".//{{{XLSX_NS}}}t")
        return text_node.text if text_node is not None else None

    value_node = cell.find(f"{{{XLSX_NS}}}v")
    if value_node is None or value_node.text is None:
        return None

    raw_value = value_node.text
    if cell_type == "s":
        index = int(raw_value)
        if 0 <= index < len(shared_strings):
            return shared_strings[index]
        return None

    try:
        return float(raw_value)
    except ValueError:
        return raw_value


@lru_cache(maxsize=1)
def _load_sections_index() -> dict[str, dict[str, float]]:
    path = _repo_root() / "data" / "sections.xlsx"
    if not path.exists():
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["data/sections.xlsx"],
                message="Sections catalog not found at data/sections.xlsx.",
                source_document="data/sections.xlsx",
            )
        )

    try:
        archive = zipfile.ZipFile(path, "r")
    except Exception as exc:  # pragma: no cover - defensive branch
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=None,
                message=f"Unable to read sections workbook: {exc}",
                source_document="data/sections.xlsx",
            )
        ) from exc

    shapes: dict[str, dict[str, float]] = {}
    required_headers = {"shape", "d", "bf", "tf", "tw"}
    shared_strings = _shared_strings_from_archive(archive)

    try:
        for worksheet_name in archive.namelist():
            if not worksheet_name.startswith("xl/worksheets/sheet") or not worksheet_name.endswith(".xml"):
                continue

            root = ET.fromstring(archive.read(worksheet_name))
            sheet_data = root.find(f"{{{XLSX_NS}}}sheetData")
            if sheet_data is None:
                continue

            row_elements = sheet_data.findall(f"{{{XLSX_NS}}}row")
            if not row_elements:
                continue

            header_map: dict[str, int] = {}
            header_map_exact: dict[str, int] = {}
            for cell in row_elements[0].findall(f"{{{XLSX_NS}}}c"):
                cell_ref = cell.attrib.get("r", "")
                col_ref = "".join(char for char in cell_ref if char.isalpha())
                if not col_ref:
                    continue
                raw_header = _cell_value(cell, shared_strings)
                if raw_header is None:
                    continue
                header_exact = str(raw_header).strip()
                if not header_exact:
                    continue
                header = header_exact.lower()
                header_map[header] = _col_ref_to_index(col_ref)
                header_map_exact[header_exact] = _col_ref_to_index(col_ref)

            if not required_headers.issubset(header_map.keys()):
                continue

            idx_shape = header_map["shape"]
            idx_d = header_map["d"]
            idx_bf = header_map["bf"]
            idx_tf = header_map["tf"]
            idx_tw = header_map["tw"]
            idx_kdes = header_map.get("kdes")
            idx_k1 = header_map.get("k1")
            idx_zx = header_map.get("zx")
            idx_a = header_map.get("a") or header_map.get("ag")
            idx_t_cap = header_map_exact.get("T")

            for row in row_elements[1:]:
                row_values: dict[int, str | float | None] = {}
                for cell in row.findall(f"{{{XLSX_NS}}}c"):
                    cell_ref = cell.attrib.get("r", "")
                    col_ref = "".join(char for char in cell_ref if char.isalpha())
                    if not col_ref:
                        continue
                    row_values[_col_ref_to_index(col_ref)] = _cell_value(cell, shared_strings)

                raw_shape = row_values.get(idx_shape)
                if raw_shape is None:
                    continue

                shape = str(raw_shape).strip().upper()
                if not shape:
                    continue

                try:
                    d_mm = float(row_values[idx_d])  # type: ignore[arg-type]
                    bf_mm = float(row_values[idx_bf])  # type: ignore[arg-type]
                    tf_mm = float(row_values[idx_tf])  # type: ignore[arg-type]
                    tw_mm = float(row_values[idx_tw])  # type: ignore[arg-type]
                except (KeyError, TypeError, ValueError):
                    continue

                kdes_mm: float | None = None
                if idx_kdes is not None:
                    kdes_raw = row_values.get(idx_kdes)
                    try:
                        kdes_mm = float(kdes_raw) if kdes_raw is not None else None
                    except (TypeError, ValueError):
                        kdes_mm = None

                k1_mm: float | None = None
                if idx_k1 is not None:
                    k1_raw = row_values.get(idx_k1)
                    try:
                        k1_mm = float(k1_raw) if k1_raw is not None else None
                    except (TypeError, ValueError):
                        k1_mm = None

                zx_cm3: float | None = None
                if idx_zx is not None:
                    zx_raw = row_values.get(idx_zx)
                    try:
                        zx_cm3 = float(zx_raw) if zx_raw is not None else None
                    except (TypeError, ValueError):
                        zx_cm3 = None

                ag_mm2: float | None = None
                if idx_a is not None:
                    ag_raw = row_values.get(idx_a)
                    try:
                        ag_mm2 = float(ag_raw) if ag_raw is not None else None
                    except (TypeError, ValueError):
                        ag_mm2 = None

                t_cap_mm: float | None = None
                if idx_t_cap is not None:
                    t_cap_raw = row_values.get(idx_t_cap)
                    try:
                        t_cap_mm = float(t_cap_raw) if t_cap_raw is not None else None
                    except (TypeError, ValueError):
                        t_cap_mm = None

                if shape not in shapes:
                    record = {
                        "d_mm": d_mm,
                        "bf_mm": bf_mm,
                        "tf_mm": tf_mm,
                        "tw_mm": tw_mm,
                    }
                    if kdes_mm is not None:
                        record["kdes_mm"] = kdes_mm
                    if k1_mm is not None:
                        record["k1_mm"] = k1_mm
                    if zx_cm3 is not None:
                        record["zx_cm3"] = zx_cm3
                    if ag_mm2 is not None:
                        record["ag_mm2"] = ag_mm2
                    if t_cap_mm is not None:
                        record["t_cap_mm"] = t_cap_mm
                    shapes[shape] = record
    finally:
        archive.close()

    if not shapes:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["data/sections.xlsx"],
                message="No valid shape properties were loaded from data/sections.xlsx.",
                source_document="data/sections.xlsx",
            )
        )
    return shapes


def _mm_to_length_unit(mm_value: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.SI:
        return Quantity(value=mm_value, unit="mm")
    return Quantity(value=mm_value / 25.4, unit="in")


def _cm3_to_section_modulus_unit(cm3_value: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.SI:
        return Quantity(value=cm3_value * 1000.0, unit="mm3")
    return Quantity(value=cm3_value / 16.387064, unit="in3")


def _mm2_to_area_unit(mm2_value: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.SI:
        return Quantity(value=mm2_value, unit="mm2")
    return Quantity(value=mm2_value / 645.16, unit="in2")


def _in_to_length_unit(in_value: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=in_value, unit="in")
    return Quantity(value=in_value * 25.4, unit="mm")


def get_shape_profile_properties(*, shape: str, unit_system: UnitSystem) -> dict[str, Quantity]:
    shapes = _load_sections_index()
    key = shape.strip().upper()
    shape_data = shapes.get(key)
    if shape_data is None:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.MISSING_REQUIRED_INPUT,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["sections.shape"],
                message=f"Shape '{shape}' was not found in data/sections.xlsx.",
                source_document="data/sections.xlsx",
            )
        )

    output = {
        "d": _mm_to_length_unit(shape_data["d_mm"], unit_system),
        "bf": _mm_to_length_unit(shape_data["bf_mm"], unit_system),
        "tf": _mm_to_length_unit(shape_data["tf_mm"], unit_system),
        "tw": _mm_to_length_unit(shape_data["tw_mm"], unit_system),
    }
    kdes_mm = shape_data.get("kdes_mm")
    if kdes_mm is not None:
        output["kdes"] = _mm_to_length_unit(float(kdes_mm), unit_system)
    k1_mm = shape_data.get("k1_mm")
    if k1_mm is not None:
        output["k1"] = _mm_to_length_unit(float(k1_mm), unit_system)
    zx_cm3 = shape_data.get("zx_cm3")
    if zx_cm3 is not None:
        output["zx"] = _cm3_to_section_modulus_unit(float(zx_cm3), unit_system)
    ag_mm2 = shape_data.get("ag_mm2")
    if ag_mm2 is not None:
        output["ag"] = _mm2_to_area_unit(float(ag_mm2), unit_system)
    t_cap_mm = shape_data.get("t_cap_mm")
    if t_cap_mm is not None:
        output["T"] = _mm_to_length_unit(float(t_cap_mm), unit_system)
    return output


@lru_cache(maxsize=1)
def _load_bolt_sections_index() -> dict[str, list[dict[str, float | str]]]:
    rows = read_sheet_rows(xlsx_path=_repo_root() / "data" / "sections.xlsx", sheet_name="Perno")
    index: dict[str, list[dict[str, float | str]]] = {}

    for row in rows:
        normalized = {normalize_text(k): v for k, v in row.items()}
        shape_raw = normalized.get("shape")
        if shape_raw is None:
            continue

        shape = str(shape_raw).strip().upper()
        if not shape:
            continue

        # Backward compatible header resolution for bolt description.
        # Priority requested:
        # 1) classification
        # 2) descripcion
        # 3) legacy alternatives
        classification = str(
            normalized.get("classification")
            or normalized.get("descripcion")
            or normalized.get("clasificacion")
            or normalized.get("descripcion de los pernos")
            or ""
        ).strip()
        standard = str(normalized.get("norma de fabricacion") or "").strip()
        diameter_in_raw = normalized.get("diametro nominal [in]")
        length_in_raw = normalized.get("longitud vastago (l) [in]")
        flats_in_raw = normalized.get("width across flats (f) [in]")
        head_d_in_raw = normalized.get("head diameter (d) [in]")
        head_h_in_raw = normalized.get("height (h1) [in]")

        try:
            diameter_in = float(diameter_in_raw) if diameter_in_raw is not None else None
        except (TypeError, ValueError):
            diameter_in = None
        if diameter_in is None:
            continue

        def _as_float(value: object) -> float | None:
            try:
                return float(value) if value is not None else None
            except (TypeError, ValueError):
                return None

        record = {
            "shape": shape,
            "classification": classification,
            "fabrication_standard": standard,
            "diameter_in": diameter_in,
            "length_in": _as_float(length_in_raw) or 0.0,
            "width_across_flats_in": _as_float(flats_in_raw) or 0.0,
            "head_diameter_in": _as_float(head_d_in_raw) or 0.0,
            "head_height_in": _as_float(head_h_in_raw) or 0.0,
        }
        index.setdefault(shape, []).append(record)

    if not index:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["data/sections.xlsx", "sheet:Perno"],
                message="No bolt records were loaded from data/sections.xlsx sheet 'Perno'.",
                source_document="data/sections.xlsx",
            )
        )
    return index


def get_bolt_section_properties(
    *,
    bolt_shape: str,
    unit_system: UnitSystem,
    bolt_description: str | None = None,
    bolt_fabrication_standard: str | None = None,
) -> dict[str, Quantity | str]:
    key = bolt_shape.strip().upper()
    candidates = _load_bolt_sections_index().get(key)
    if not candidates:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.MISSING_REQUIRED_INPUT,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["materials.bolt_shape"],
                message=f"Bolt shape '{bolt_shape}' was not found in data/sections.xlsx sheet 'Perno'.",
                source_document="data/sections.xlsx",
            )
        )
    selected = candidates[0]
    if bolt_description is not None or bolt_fabrication_standard is not None:
        requested_desc = normalize_text(str(bolt_description or ""))
        requested_std = normalize_text(str(bolt_fabrication_standard or ""))
        filtered: list[dict[str, float | str]] = []
        for item in candidates:
            current_desc = normalize_text(str(item.get("classification") or ""))
            current_std = normalize_text(str(item.get("fabrication_standard") or ""))
            if requested_desc and current_desc != requested_desc:
                continue
            if requested_std and current_std != requested_std:
                continue
            filtered.append(item)
        if not filtered:
            available = ", ".join(
                f"(descripcion='{item.get('classification','')}', norma='{item.get('fabrication_standard','')}')"
                for item in candidates
            )
            raise StructuredEngineException(
                StructuredError(
                    error_code=ErrorCode.VALIDATION_ERROR,
                    stage=Stage.VALIDATE,
                    rule_id=None,
                    missing_fields=["materials.bolt_shape", "materials.bolt_description", "materials.bolt_fabrication_standard"],
                    message=(
                        "No matching bolt record found in sections/Perno for "
                        f"shape='{bolt_shape}', descripcion='{bolt_description}', "
                        f"norma de fabricacion='{bolt_fabrication_standard}'. "
                        f"Available rows for this shape: {available}"
                    ),
                    source_document="data/sections.xlsx",
                )
            )
        selected = filtered[0]

    return {
        "shape": str(selected["shape"]),
        "classification": str(selected["classification"]),
        "fabrication_standard": str(selected["fabrication_standard"]),
        "diameter_nominal": _in_to_length_unit(float(selected["diameter_in"]), unit_system),
        "length": _in_to_length_unit(float(selected["length_in"]), unit_system),
        "width_across_flats": _in_to_length_unit(float(selected["width_across_flats_in"]), unit_system),
        "head_diameter": _in_to_length_unit(float(selected["head_diameter_in"]), unit_system),
        "head_height": _in_to_length_unit(float(selected["head_height_in"]), unit_system),
    }


def get_beam_profile_properties(*, beam_shape: str, unit_system: UnitSystem) -> dict[str, Quantity]:
    return get_shape_profile_properties(shape=beam_shape, unit_system=unit_system)


def get_column_profile_properties(*, column_shape: str, unit_system: UnitSystem) -> dict[str, Quantity]:
    return get_shape_profile_properties(shape=column_shape, unit_system=unit_system)
