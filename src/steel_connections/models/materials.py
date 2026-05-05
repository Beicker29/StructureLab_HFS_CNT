from __future__ import annotations

from typing import Any

from pydantic import Field

from steel_connections.models.units import Quantity, StrictModel


class CatalogSource(StrictModel):
    catalog: str
    file: str
    sheet: str
    key: str
    checksum_sha256: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SteelMaterial(StrictModel):
    steel_type: str
    fy: Quantity
    fu: Quantity
    ry: float
    rt: float
    source: CatalogSource


class BoltMaterial(StrictModel):
    description: str
    specification: str
    fnt: Quantity
    fnv_threads_not_excluded: Quantity
    fnv_threads_excluded: Quantity
    source: CatalogSource


class WeldMaterial(StrictModel):
    electrode: str | None = None
    fexx: Quantity
    source: CatalogSource | None = None
