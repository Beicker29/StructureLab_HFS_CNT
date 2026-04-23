"""Reusable utilization equations (demand/capacity checks)."""

from __future__ import annotations

from typing import Any

from steel_connections.models.units import Quantity


def compute_dcr_ratio(*, demand: Quantity, capacity: Quantity) -> dict[str, Any]:
    """Compute demand-capacity ratio.

    Equation:
        DCR = demand / capacity

    Reference:
        Generic LRFD/strength-check utilization format used across AISC checks.
    """
    if demand.unit != capacity.unit:
        raise ValueError("Demand and capacity must share the same units to compute DCR.")
    if capacity.value == 0:
        raise ValueError("Capacity must be non-zero to compute DCR.")
    dcr = demand.value / capacity.value
    return {
        "dcr": dcr,
        "passes": dcr <= 1.0,
        "equation": "DCR = demand / capacity",
    }

