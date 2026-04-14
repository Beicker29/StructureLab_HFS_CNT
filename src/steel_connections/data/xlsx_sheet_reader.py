from __future__ import annotations

from pathlib import Path
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

from steel_connections.models.errors import ErrorCode, Stage, StructuredEngineException, StructuredError

XLSX_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    no_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    no_hidden = no_accents.replace("\u200b", "").replace("\ufeff", "")
    return " ".join(no_hidden.strip().lower().split())


def _col_ref_to_index(col_ref: str) -> int:
    value = 0
    for char in col_ref:
        value = value * 26 + (ord(char.upper()) - ord("A") + 1)
    return value


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    shared_path = "xl/sharedStrings.xml"
    if shared_path not in archive.namelist():
        return []
    root = ET.fromstring(archive.read(shared_path))
    values: list[str] = []
    for si in root.findall(f"{{{XLSX_NS}}}si"):
        text_parts = [node.text or "" for node in si.findall(f".//{{{XLSX_NS}}}t")]
        values.append("".join(text_parts))
    return values


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
        idx = int(raw_value)
        if 0 <= idx < len(shared_strings):
            return shared_strings[idx]
        return None

    try:
        return float(raw_value)
    except ValueError:
        return raw_value


def _worksheet_xml_path(archive: zipfile.ZipFile, sheet_name: str, source_document: str) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))

    rel_map = {
        rel.attrib.get("Id"): rel.attrib.get("Target")
        for rel in rels.findall(f"{{{PKG_REL_NS}}}Relationship")
    }

    requested = normalize_text(sheet_name)
    sheets = workbook.findall(f".//{{{XLSX_NS}}}sheet")
    for sheet in sheets:
        current_name = normalize_text(str(sheet.attrib.get("name", "")))
        if current_name != requested:
            continue
        rel_id = sheet.attrib.get(f"{{{DOC_REL_NS}}}id")
        target = rel_map.get(rel_id)
        if not target:
            break
        normalized_target = target[1:] if target.startswith("/") else target
        if not normalized_target.startswith("xl/"):
            normalized_target = f"xl/{normalized_target}"
        return normalized_target

    raise StructuredEngineException(
        StructuredError(
            error_code=ErrorCode.VALIDATION_ERROR,
            stage=Stage.VALIDATE,
            rule_id=None,
            missing_fields=[f"sheet:{sheet_name}"],
            message=f"Worksheet '{sheet_name}' was not found in {source_document}.",
            source_document=source_document,
        )
    )


def read_sheet_rows(*, xlsx_path: Path, sheet_name: str) -> list[dict[str, str | float | None]]:
    source_document = str(xlsx_path).replace("\\", "/")
    if not xlsx_path.exists():
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=[source_document],
                message=f"Workbook '{source_document}' was not found.",
                source_document=source_document,
            )
        )

    try:
        archive = zipfile.ZipFile(xlsx_path, "r")
    except Exception as exc:  # pragma: no cover - defensive branch
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.VALIDATION_ERROR,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=None,
                message=f"Unable to read workbook '{source_document}': {exc}",
                source_document=source_document,
            )
        ) from exc

    try:
        worksheet_path = _worksheet_xml_path(archive, sheet_name, source_document)
        root = ET.fromstring(archive.read(worksheet_path))
        sheet_data = root.find(f"{{{XLSX_NS}}}sheetData")
        if sheet_data is None:
            return []

        rows = sheet_data.findall(f"{{{XLSX_NS}}}row")
        if not rows:
            return []

        shared = _shared_strings(archive)
        header_cells = rows[0].findall(f"{{{XLSX_NS}}}c")
        header_map: dict[int, str] = {}
        for cell in header_cells:
            cell_ref = cell.attrib.get("r", "")
            col_ref = "".join(char for char in cell_ref if char.isalpha())
            if not col_ref:
                continue
            raw_header = _cell_value(cell, shared)
            if raw_header is None:
                continue
            header = str(raw_header).strip()
            if header:
                header_map[_col_ref_to_index(col_ref)] = header

        output: list[dict[str, str | float | None]] = []
        for row in rows[1:]:
            values_by_col: dict[int, str | float | None] = {}
            for cell in row.findall(f"{{{XLSX_NS}}}c"):
                cell_ref = cell.attrib.get("r", "")
                col_ref = "".join(char for char in cell_ref if char.isalpha())
                if not col_ref:
                    continue
                values_by_col[_col_ref_to_index(col_ref)] = _cell_value(cell, shared)

            mapped: dict[str, str | float | None] = {}
            for col_idx, header in header_map.items():
                mapped[header] = values_by_col.get(col_idx)
            output.append(mapped)
        return output
    finally:
        archive.close()
