from __future__ import annotations

from steel_connections.codes.engineering.common import BoltCoordinate
from steel_connections.codes.engineering.common import BoltGroupMethod
from steel_connections.codes.engineering.common import BoltGroupSolverOptions
from steel_connections.codes.engineering.common import build_bolt_group_geometry
from steel_connections.codes.engineering.common import build_in_plane_load
from steel_connections.codes.engineering.common import solve_bolt_group_method
from steel_connections.codes.engineering.common.bolt_group_types import (
    ElasticECRResult,
    ElasticSuperpositionResult,
    ICRResult,
)


def _sample_geometry():
    bolts = (
        BoltCoordinate(tag="b1", x=0.0, y=0.0),
        BoltCoordinate(tag="b2", x=2.0, y=0.0),
        BoltCoordinate(tag="b3", x=0.0, y=2.0),
        BoltCoordinate(tag="b4", x=2.0, y=2.0),
    )
    return build_bolt_group_geometry(bolts)


def test_geometry_invariants_for_rectangular_group() -> None:
    geometry = _sample_geometry()
    assert geometry.centroid_x == 1.0
    assert geometry.centroid_y == 1.0
    assert geometry.ix == 4.0
    assert geometry.iy == 4.0
    assert geometry.ip == 8.0


def test_elastic_superposition_returns_resultant_dcr() -> None:
    geometry = _sample_geometry()
    load = build_in_plane_load(vx=40.0, vy=0.0, mz=0.0, eccentricity_mode="aisc")
    result = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        geometry=geometry,
        load=load,
        bolt_capacity=20.0,
        options=BoltGroupSolverOptions(),
    )
    assert isinstance(result, ElasticSuperpositionResult)
    assert result.bolt_demand > 0.0
    assert result.dcr > 0.0


def test_elastic_ecr_not_applicable_when_torsion_is_zero() -> None:
    geometry = _sample_geometry()
    load = build_in_plane_load(vx=40.0, vy=10.0, mz=0.0, eccentricity_mode="aisc")
    result = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_ECR,
        geometry=geometry,
        load=load,
        bolt_capacity=20.0,
        options=BoltGroupSolverOptions(),
    )
    assert isinstance(result, ElasticECRResult)
    assert result.applicable is False


def test_icr_pure_torsion_special_case() -> None:
    geometry = _sample_geometry()
    load = build_in_plane_load(vx=0.0, vy=0.0, mz=80.0, eccentricity_mode="aisc")
    result = solve_bolt_group_method(
        method=BoltGroupMethod.ICR,
        geometry=geometry,
        load=load,
        bolt_capacity=25.0,
        options=BoltGroupSolverOptions(tolerance=0.01, max_iterations=10),
    )
    assert isinstance(result, ICRResult)
    assert result.converged is True
    assert result.capacity is not None
    assert result.dcr is not None


def test_icr_reports_non_convergence_when_iteration_budget_is_too_small() -> None:
    geometry = _sample_geometry()
    load = build_in_plane_load(vx=20.0, vy=80.0, mz=500.0, eccentricity_mode="aisc")
    result = solve_bolt_group_method(
        method=BoltGroupMethod.ICR,
        geometry=geometry,
        load=load,
        bolt_capacity=25.0,
        options=BoltGroupSolverOptions(tolerance=1e-6, max_iterations=1),
    )
    assert isinstance(result, ICRResult)
    assert result.converged is False
    assert result.note is not None
