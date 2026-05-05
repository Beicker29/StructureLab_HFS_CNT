from __future__ import annotations

from steel_connections.models.materials import CatalogSource
from steel_connections.models.units import Quantity, StrictModel


class Section(StrictModel):
    shape: str
    d: Quantity
    bf: Quantity
    tf: Quantity
    tw: Quantity
    kdes: Quantity | None = None
    k1: Quantity | None = None
    zx: Quantity | None = None
    ag: Quantity | None = None
    T: Quantity | None = None
    source: CatalogSource


class BoltSection(StrictModel):
    shape: str
    classification: str
    fabrication_standard: str
    diameter_nominal: Quantity
    length: Quantity
    width_across_flats: Quantity
    head_diameter: Quantity
    head_height: Quantity
    source: CatalogSource
