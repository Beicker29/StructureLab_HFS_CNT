from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from steel_connections.data.xlsx_sheet_reader import normalize_text, read_sheet_rows
from steel_connections.models.errors import ErrorCode, Stage, StructuredEngineException, StructuredError
from steel_connections.models.units import Quantity, UnitSystem

MPA_PER_KSI = 6.894757293168361


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _materials_path() -> Path:
    return _repo_root() / "data" / "materials.xlsx"


def _stress_from_mpa(value_mpa: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.SI:
        return Quantity(value=value_mpa, unit="MPa")
    return Quantity(value=value_mpa / MPA_PER_KSI, unit="ksi")


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return None


@lru_cache(maxsize=1)
def _hrs_index() -> dict[str, dict[str, float]]:
    rows = read_sheet_rows(xlsx_path=_materials_path(), sheet_name="HRS")
    index: dict[str, dict[str, float]] = {}

    for row in rows:
        normalized = {normalize_text(k): v for k, v in row.items()}
        steel_type_raw = normalized.get("tipo de acero")
        if steel_type_raw is None:
            continue
        steel_type = str(steel_type_raw).strip()
        if not steel_type:
            continue

        fy = _to_float(normalized.get("esfuerzo de fluencia minimo (fy) [mpa]"))
        fu = _to_float(normalized.get("resistencia a traccion minima (fu) [mpa]"))
        ry = _to_float(normalized.get("relacion de resistencia a la fluencia (ry)"))
        rt = _to_float(normalized.get("relacion de resistencia a la rotura (rt)"))
        if fy is None or fu is None:
            continue

        index[normalize_text(steel_type)] = {
            "fy_mpa": fy,
            "fu_mpa": fu,
            "ry": ry if ry is not None else 0.0,
            "rt": rt if rt is not None else 0.0,
            "steel_type": steel_type,
        }
    return index


@lru_cache(maxsize=1)
def _plate_index() -> dict[str, dict[str, float]]:
    rows = read_sheet_rows(xlsx_path=_materials_path(), sheet_name="Platinas")
    index: dict[str, dict[str, float]] = {}

    for row in rows:
        normalized = {normalize_text(k): v for k, v in row.items()}
        steel_type_raw = normalized.get("tipo de acero")
        if steel_type_raw is None:
            continue
        steel_type = str(steel_type_raw).strip()
        if not steel_type:
            continue

        fy = _to_float(normalized.get("esfuerzo de fluencia minimo (fy) [mpa]"))
        fu = _to_float(normalized.get("resistencia a traccion minima (fu) [mpa]"))
        ry = _to_float(normalized.get("relacion de resistencia a la fluencia (ry)"))
        rt = _to_float(normalized.get("relacion de resistencia a la rotura (rt)"))
        if fy is None or fu is None:
            continue

        index[normalize_text(steel_type)] = {
            "fy_mpa": fy,
            "fu_mpa": fu,
            "ry": ry if ry is not None else 0.0,
            "rt": rt if rt is not None else 0.0,
            "steel_type": steel_type,
        }
    return index


@lru_cache(maxsize=1)
def _bolt_strength_index() -> dict[tuple[str, str], dict[str, float | str]]:
    rows = read_sheet_rows(xlsx_path=_materials_path(), sheet_name="Pernos")
    index: dict[tuple[str, str], dict[str, float | str]] = {}

    for row in rows:
        description = None
        specification = None
        fnt_mpa = None
        fnv_n_mpa = None
        fnv_x_mpa = None

        for header, raw_value in row.items():
            key = normalize_text(header)
            if "descripcion" in key:
                description = str(raw_value).strip() if raw_value is not None else None
            elif key == "especificacion" or "norma de fabricacion" in key:
                specification = str(raw_value).strip() if raw_value is not None else None
            elif "esfuerzo de tension nominal" in key:
                fnt_mpa = _to_float(raw_value)
            elif "esfuerzo cortante nominal" in key and "no excluidas" in key:
                fnv_n_mpa = _to_float(raw_value)
            elif "esfuerzo cortante nominal" in key and "excluidas" in key:
                fnv_x_mpa = _to_float(raw_value)

        if not description or not specification:
            continue
        if fnt_mpa is None or fnv_n_mpa is None or fnv_x_mpa is None:
            continue

        index[(normalize_text(description), normalize_text(specification))] = {
            "description": description,
            "specification": specification,
            "fnt_mpa": fnt_mpa,
            "fnv_n_mpa": fnv_n_mpa,
            "fnv_x_mpa": fnv_x_mpa,
        }
    return index


def get_hrs_steel_properties(*, steel_type: str, unit_system: UnitSystem) -> dict[str, Quantity | float | str]:
    record = _hrs_index().get(normalize_text(steel_type))
    if record is None:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.MISSING_REQUIRED_INPUT,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["materials.profile_steel_type"],
                message=f"HRS steel type '{steel_type}' was not found in data/materials.xlsx (sheet HRS).",
                source_document="data/materials.xlsx",
            )
        )
    return {
        "steel_type": record["steel_type"],
        "fy": _stress_from_mpa(float(record["fy_mpa"]), unit_system),
        "fu": _stress_from_mpa(float(record["fu_mpa"]), unit_system),
        "ry": float(record["ry"]),
        "rt": float(record["rt"]),
    }


def get_plate_steel_properties(*, steel_type: str, unit_system: UnitSystem) -> dict[str, Quantity | float | str]:
    record = _plate_index().get(normalize_text(steel_type))
    if record is None:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.MISSING_REQUIRED_INPUT,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["materials.plate_steel_type"],
                message=f"Plate steel type '{steel_type}' was not found in data/materials.xlsx (sheet Platinas).",
                source_document="data/materials.xlsx",
            )
        )
    return {
        "steel_type": record["steel_type"],
        "fy": _stress_from_mpa(float(record["fy_mpa"]), unit_system),
        "fu": _stress_from_mpa(float(record["fu_mpa"]), unit_system),
        "ry": float(record["ry"]),
        "rt": float(record["rt"]),
    }


def get_bolt_strength_properties(
    *,
    description: str,
    specification: str,
    unit_system: UnitSystem,
) -> dict[str, Quantity | str]:
    record = _bolt_strength_index().get((normalize_text(description), normalize_text(specification)))
    if record is None:
        raise StructuredEngineException(
            StructuredError(
                error_code=ErrorCode.MISSING_REQUIRED_INPUT,
                stage=Stage.VALIDATE,
                rule_id=None,
                missing_fields=["materials.bolt_description", "materials.bolt_fabrication_standard"],
                message=(
                    "Bolt strength record was not found in data/materials.xlsx (sheet Pernos) "
                    f"for description '{description}' and specification '{specification}'."
                ),
                source_document="data/materials.xlsx",
            )
        )
    return {
        "description": str(record["description"]),
        "specification": str(record["specification"]),
        "fnt": _stress_from_mpa(float(record["fnt_mpa"]), unit_system),
        "fnv_threads_not_excluded": _stress_from_mpa(float(record["fnv_n_mpa"]), unit_system),
        "fnv_threads_excluded": _stress_from_mpa(float(record["fnv_x_mpa"]), unit_system),
    }
