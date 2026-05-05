from __future__ import annotations

from pathlib import Path
from typing import Protocol

from steel_connections.models.materials import BoltMaterial, SteelMaterial
from steel_connections.models.sections import BoltSection, Section
from steel_connections.models.units import UnitSystem


class SteelMaterialCatalog(Protocol):
    path: Path

    def get_hrs_steel(self, *, steel_type: str, unit_system: UnitSystem) -> SteelMaterial: ...

    def get_plate_steel(self, *, steel_type: str, unit_system: UnitSystem) -> SteelMaterial: ...


class BoltMaterialCatalog(Protocol):
    path: Path

    def get_bolt_material(
        self,
        *,
        description: str,
        specification: str,
        unit_system: UnitSystem,
    ) -> BoltMaterial: ...


class SectionCatalog(Protocol):
    path: Path

    def get_section(self, *, shape: str, unit_system: UnitSystem) -> Section: ...

    def get_beam_section(self, *, beam_shape: str, unit_system: UnitSystem) -> Section: ...

    def get_column_section(self, *, column_shape: str, unit_system: UnitSystem) -> Section: ...


class BoltSectionCatalog(Protocol):
    path: Path

    def get_bolt_section(
        self,
        *,
        bolt_shape: str,
        unit_system: UnitSystem,
        bolt_description: str | None = None,
        bolt_fabrication_standard: str | None = None,
    ) -> BoltSection: ...
