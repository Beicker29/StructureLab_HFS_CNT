from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from steel_connections.data.sections_repository import (
    get_beam_profile_properties,
    get_bolt_section_properties,
    get_column_profile_properties,
    get_shape_profile_properties,
)
from steel_connections.models.materials import CatalogSource
from steel_connections.models.sections import BoltSection, Section
from steel_connections.models.units import UnitSystem


def default_sections_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "sections.xlsx"


@lru_cache(maxsize=8)
def _sha256_for_path(path_text: str) -> str:
    digest = sha256()
    with Path(path_text).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


class XlsxSectionsCatalog:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_sections_path()

    def _source(self, *, sheet: str, key: str) -> CatalogSource:
        return CatalogSource(
            catalog="sections",
            file=str(self.path),
            sheet=sheet,
            key=key,
            checksum_sha256=_sha256_for_path(str(self.path)),
        )

    def get_section(self, *, shape: str, unit_system: UnitSystem) -> Section:
        record = get_shape_profile_properties(shape=shape, unit_system=unit_system)
        return Section(
            shape=shape.strip().upper(),
            d=record["d"],
            bf=record["bf"],
            tf=record["tf"],
            tw=record["tw"],
            kdes=record.get("kdes"),
            k1=record.get("k1"),
            zx=record.get("zx"),
            ag=record.get("ag"),
            T=record.get("T"),
            source=self._source(sheet="profiles", key=shape.strip().upper()),
        )

    def get_beam_section(self, *, beam_shape: str, unit_system: UnitSystem) -> Section:
        record = get_beam_profile_properties(beam_shape=beam_shape, unit_system=unit_system)
        section = self.get_section(shape=beam_shape, unit_system=unit_system)
        return section.model_copy(
            update={
                "d": record["d"],
                "bf": record["bf"],
                "tf": record["tf"],
                "tw": record["tw"],
                "kdes": record.get("kdes"),
                "k1": record.get("k1"),
                "zx": record.get("zx"),
                "ag": record.get("ag"),
                "T": record.get("T"),
            }
        )

    def get_column_section(self, *, column_shape: str, unit_system: UnitSystem) -> Section:
        record = get_column_profile_properties(column_shape=column_shape, unit_system=unit_system)
        section = self.get_section(shape=column_shape, unit_system=unit_system)
        return section.model_copy(
            update={
                "d": record["d"],
                "bf": record["bf"],
                "tf": record["tf"],
                "tw": record["tw"],
                "kdes": record.get("kdes"),
                "k1": record.get("k1"),
                "zx": record.get("zx"),
                "ag": record.get("ag"),
                "T": record.get("T"),
            }
        )

    def get_bolt_section(
        self,
        *,
        bolt_shape: str,
        unit_system: UnitSystem,
        bolt_description: str | None = None,
        bolt_fabrication_standard: str | None = None,
    ) -> BoltSection:
        record = get_bolt_section_properties(
            bolt_shape=bolt_shape,
            unit_system=unit_system,
            bolt_description=bolt_description,
            bolt_fabrication_standard=bolt_fabrication_standard,
        )
        return BoltSection(
            shape=str(record["shape"]),
            classification=str(record["classification"]),
            fabrication_standard=str(record["fabrication_standard"]),
            diameter_nominal=record["diameter_nominal"],  # type: ignore[arg-type]
            length=record["length"],  # type: ignore[arg-type]
            width_across_flats=record["width_across_flats"],  # type: ignore[arg-type]
            head_diameter=record["head_diameter"],  # type: ignore[arg-type]
            head_height=record["head_height"],  # type: ignore[arg-type]
            source=self._source(sheet="Perno", key=str(record["shape"])),
        )
