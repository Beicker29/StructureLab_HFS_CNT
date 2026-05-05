from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from steel_connections.data.materials_repository import (
    get_bolt_strength_properties,
    get_hrs_steel_properties,
    get_plate_steel_properties,
)
from steel_connections.models.materials import BoltMaterial, CatalogSource, SteelMaterial
from steel_connections.models.units import Quantity, UnitSystem


def default_materials_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "materials.xlsx"


@lru_cache(maxsize=8)
def _sha256_for_path(path_text: str) -> str:
    digest = sha256()
    with Path(path_text).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


class XlsxMaterialsCatalog:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_materials_path()

    def _source(self, *, sheet: str, key: str) -> CatalogSource:
        return CatalogSource(
            catalog="materials",
            file=str(self.path),
            sheet=sheet,
            key=key,
            checksum_sha256=_sha256_for_path(str(self.path)),
        )

    def get_hrs_steel(self, *, steel_type: str, unit_system: UnitSystem) -> SteelMaterial:
        record = get_hrs_steel_properties(steel_type=steel_type, unit_system=unit_system)
        return SteelMaterial(
            steel_type=str(record["steel_type"]),
            fy=record["fy"],  # type: ignore[arg-type]
            fu=record["fu"],  # type: ignore[arg-type]
            ry=float(record["ry"]),
            rt=float(record["rt"]),
            source=self._source(sheet="HRS", key=str(record["steel_type"])),
        )

    def get_plate_steel(self, *, steel_type: str, unit_system: UnitSystem) -> SteelMaterial:
        record = get_plate_steel_properties(steel_type=steel_type, unit_system=unit_system)
        return SteelMaterial(
            steel_type=str(record["steel_type"]),
            fy=record["fy"],  # type: ignore[arg-type]
            fu=record["fu"],  # type: ignore[arg-type]
            ry=float(record["ry"]),
            rt=float(record["rt"]),
            source=self._source(sheet="Platinas", key=str(record["steel_type"])),
        )

    def get_bolt_material(
        self,
        *,
        description: str,
        specification: str,
        unit_system: UnitSystem,
    ) -> BoltMaterial:
        record = get_bolt_strength_properties(
            description=description,
            specification=specification,
            unit_system=unit_system,
        )
        return BoltMaterial(
            description=str(record["description"]),
            specification=str(record["specification"]),
            fnt=record["fnt"],  # type: ignore[arg-type]
            fnv_threads_not_excluded=record["fnv_threads_not_excluded"],  # type: ignore[arg-type]
            fnv_threads_excluded=record["fnv_threads_excluded"],  # type: ignore[arg-type]
            source=self._source(
                sheet="Pernos",
                key=f"{record['description']}|{record['specification']}",
            ),
        )


def weld_material_from_fexx(
    *,
    fexx: Quantity,
    electrode: str | None = None,
    source: CatalogSource | None = None,
):
    from steel_connections.models.materials import WeldMaterial

    return WeldMaterial(electrode=electrode, fexx=fexx, source=source)
