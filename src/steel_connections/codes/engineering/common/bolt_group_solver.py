from __future__ import annotations

from dataclasses import dataclass

from steel_connections.codes.engineering.common.bolt_group_elastic import (
    solve_elastic_center_of_rotation,
    solve_elastic_superposition,
)
from steel_connections.codes.engineering.common.bolt_group_icr import (
    ICRLawParameters,
    solve_instant_center_of_rotation,
)
from steel_connections.codes.engineering.common.bolt_group_types import (
    BoltGroupGeometry,
    BoltGroupMethod,
    ElasticECRResult,
    ElasticSuperpositionResult,
    ICRResult,
    InPlaneLoad,
)


BoltGroupAnalysisResult = ElasticSuperpositionResult | ElasticECRResult | ICRResult


@dataclass(frozen=True)
class BoltGroupSolverOptions:
    """Common solver options used by ICR and elastic methods."""

    tolerance: float = 0.01
    max_iterations: int = 1000
    icr_law: ICRLawParameters = ICRLawParameters()


def solve_bolt_group_method(
    *,
    method: BoltGroupMethod,
    geometry: BoltGroupGeometry,
    load: InPlaneLoad,
    bolt_capacity: float,
    options: BoltGroupSolverOptions | None = None,
) -> BoltGroupAnalysisResult:
    """Minimal production API to invoke a single bolt-group analysis method."""

    opts = options or BoltGroupSolverOptions()
    if method == BoltGroupMethod.ELASTIC_SUPERPOSITION:
        return solve_elastic_superposition(
            geometry=geometry,
            load=load,
            bolt_capacity=bolt_capacity,
        )
    if method == BoltGroupMethod.ELASTIC_ECR:
        return solve_elastic_center_of_rotation(
            geometry=geometry,
            load=load,
            bolt_capacity=bolt_capacity,
        )
    if method == BoltGroupMethod.ICR:
        return solve_instant_center_of_rotation(
            geometry=geometry,
            load=load,
            bolt_capacity=bolt_capacity,
            tolerance=opts.tolerance,
            max_iterations=opts.max_iterations,
            law=opts.icr_law,
        )
    raise ValueError(f"Unsupported bolt-group method '{method}'.")
