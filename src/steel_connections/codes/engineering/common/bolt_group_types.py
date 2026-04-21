from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BoltGroupMethod(str, Enum):
    ELASTIC_SUPERPOSITION = "elastic_superposition"
    ELASTIC_ECR = "elastic_ecr"
    ICR = "icr"


@dataclass(frozen=True)
class BoltCoordinate:
    """Bolt coordinate in a 2D connection plane."""

    tag: str
    x: float
    y: float


@dataclass(frozen=True)
class BoltOffset:
    """Bolt location expressed relative to a reference center."""

    tag: str
    x: float
    y: float
    dx: float
    dy: float
    radius: float


@dataclass(frozen=True)
class BoltGroupGeometry:
    """Geometric properties of a bolt group with unit-bolt assumption."""

    bolt_count: int
    centroid_x: float
    centroid_y: float
    ix: float
    iy: float
    ixy: float
    ip: float
    bolts: tuple[BoltOffset, ...]


@dataclass(frozen=True)
class InPlaneLoad:
    """Applied in-plane load and eccentricity measured from bolt-group centroid."""

    vx: float
    vy: float
    mz: float
    ex: float
    ey: float
    resultant: float


@dataclass(frozen=True)
class BoltForce:
    """Per-bolt force result."""

    tag: str
    fx: float
    fy: float
    resultant: float
    moment_about_cg: float


@dataclass(frozen=True)
class ElasticSuperpositionResult:
    """Elastic method based on direct-shear + torsion superposition."""

    method: BoltGroupMethod
    bolt_forces: tuple[BoltForce, ...]
    bolt_demand: float
    bolt_capacity: float
    dcr: float
    sum_fx: float
    sum_fy: float
    sum_mz: float


@dataclass(frozen=True)
class ElasticECRResult:
    """Elastic center-of-rotation result."""

    method: BoltGroupMethod
    applicable: bool
    note: str | None
    center_x: float | None
    center_y: float | None
    ce: float | None
    demand: float | None
    capacity: float | None
    dcr: float | None
    bolt_forces: tuple[BoltForce, ...]
    sum_fx: float | None
    sum_fy: float | None
    sum_mz: float | None


@dataclass(frozen=True)
class ICRIteration:
    """Single iteration snapshot for ICR search."""

    iteration: int
    icr_x: float
    icr_y: float
    residual_fx: float
    residual_fy: float
    residual_norm: float
    step_dx: float
    step_dy: float


@dataclass(frozen=True)
class ICRResult:
    """Instantaneous center of rotation method result."""

    method: BoltGroupMethod
    converged: bool
    note: str | None
    icr_x: float
    icr_y: float
    cu: float | None
    demand: float | None
    capacity: float | None
    dcr: float | None
    final_residual: float
    iterations: tuple[ICRIteration, ...]
    bolt_forces: tuple[BoltForce, ...]
