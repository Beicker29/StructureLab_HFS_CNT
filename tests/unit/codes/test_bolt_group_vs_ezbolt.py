from __future__ import annotations

import math

import pytest

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


ezbolt = pytest.importorskip("ezbolt")


def _build_case() -> tuple[list[tuple[float, float]], float]:
    points: list[tuple[float, float]] = []
    sx = 2.5
    sy = 3.0
    for ix in range(2):
        for iy in range(6):
            points.append((ix * sx, iy * sy))
    return points, 17.9


def test_internal_solver_matches_ezbolt_reference() -> None:
    points, bolt_capacity = _build_case()
    vx = 12.0
    vy = 40.0
    torsion = 120.0

    # ezbolt reference
    group = ezbolt.BoltGroup()
    for x, y in points:
        group.add_bolt_single(x, y)
    ez = group.solve(Vx=vx, Vy=vy, torsion=torsion, bolt_capacity=bolt_capacity, verbose=False, ecc_method="AISC")

    # internal solver
    bolts = tuple(BoltCoordinate(tag=f"b{i+1}", x=x, y=y) for i, (x, y) in enumerate(points))
    geometry = build_bolt_group_geometry(bolts)
    load = build_in_plane_load(vx=vx, vy=vy, mz=torsion, eccentricity_mode="aisc")
    options = BoltGroupSolverOptions(tolerance=0.01, max_iterations=1000)

    super_res = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        geometry=geometry,
        load=load,
        bolt_capacity=bolt_capacity,
        options=options,
    )
    assert isinstance(super_res, ElasticSuperpositionResult)
    assert super_res.dcr == pytest.approx(ez["Elastic Method - Superposition"]["DCR"], rel=1e-8, abs=1e-8)

    ecr_res = solve_bolt_group_method(
        method=BoltGroupMethod.ELASTIC_ECR,
        geometry=geometry,
        load=load,
        bolt_capacity=bolt_capacity,
        options=options,
    )
    assert isinstance(ecr_res, ElasticECRResult)
    ez_ecr = ez["Elastic Method - Center of Rotation"]
    assert isinstance(ez_ecr, dict)
    assert ecr_res.applicable is True
    assert ecr_res.dcr is not None
    assert ecr_res.dcr == pytest.approx(ez_ecr["DCR"], rel=1e-8, abs=1e-8)

    icr_res = solve_bolt_group_method(
        method=BoltGroupMethod.ICR,
        geometry=geometry,
        load=load,
        bolt_capacity=bolt_capacity,
        options=options,
    )
    assert isinstance(icr_res, ICRResult)
    ez_icr = ez["Instant Center of Rotation Method"]
    assert isinstance(ez_icr, dict)
    if isinstance(ez_icr.get("DCR"), (float, int)):
        # Iterative paths can vary slightly by step adaptation; keep practical tolerance.
        assert icr_res.dcr is not None
        assert icr_res.dcr == pytest.approx(float(ez_icr["DCR"]), rel=3e-2, abs=2e-2)


def test_internal_solver_matches_ezbolt_pure_torsion_icr() -> None:
    points, bolt_capacity = _build_case()
    vx = 0.0
    vy = 0.0
    torsion = 150.0

    group = ezbolt.BoltGroup()
    for x, y in points:
        group.add_bolt_single(x, y)
    ez = group.solve(Vx=vx, Vy=vy, torsion=torsion, bolt_capacity=bolt_capacity, verbose=False, ecc_method="AISC")
    ez_icr = ez["Instant Center of Rotation Method"]
    assert isinstance(ez_icr, dict)

    bolts = tuple(BoltCoordinate(tag=f"b{i+1}", x=x, y=y) for i, (x, y) in enumerate(points))
    geometry = build_bolt_group_geometry(bolts)
    load = build_in_plane_load(vx=vx, vy=vy, mz=torsion, eccentricity_mode="aisc")
    options = BoltGroupSolverOptions(tolerance=0.01, max_iterations=1000)
    icr_res = solve_bolt_group_method(
        method=BoltGroupMethod.ICR,
        geometry=geometry,
        load=load,
        bolt_capacity=bolt_capacity,
        options=options,
    )
    assert isinstance(icr_res, ICRResult)
    assert icr_res.converged is True
    assert icr_res.dcr is not None
    assert icr_res.dcr == pytest.approx(float(ez_icr["DCR"]), rel=1e-8, abs=1e-8)
    assert math.isclose(icr_res.icr_x, geometry.centroid_x, abs_tol=1e-9)
    assert math.isclose(icr_res.icr_y, geometry.centroid_y, abs_tol=1e-9)
