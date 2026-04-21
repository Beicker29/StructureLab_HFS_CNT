from __future__ import annotations

import math
from typing import Iterable, Sequence

from steel_connections.codes.engineering.common.bolt_group_types import (
    BoltCoordinate,
    BoltGroupGeometry,
    BoltOffset,
    InPlaneLoad,
)


def build_bolt_group_geometry(bolts: Sequence[BoltCoordinate]) -> BoltGroupGeometry:
    """Build bolt-group geometric invariants from bolt coordinates.

    Assumptions:
    - Unit-bolt inertia model (each bolt has identical weighting in geometry terms).
    - Axes follow the local in-plane system of the connection.

    Equations:
    - x_c = sum(x_i)/n
    - y_c = sum(y_i)/n
    - I_x = sum((y_i - y_c)^2)
    - I_y = sum((x_i - x_c)^2)
    - I_xy = sum((x_i - x_c)*(y_i - y_c))
    - I_p = I_x + I_y
    """

    if not bolts:
        raise ValueError("At least one bolt coordinate is required.")

    count = len(bolts)
    centroid_x = sum(point.x for point in bolts) / float(count)
    centroid_y = sum(point.y for point in bolts) / float(count)

    ix = 0.0
    iy = 0.0
    ixy = 0.0
    offsets: list[BoltOffset] = []

    for point in bolts:
        dx = point.x - centroid_x
        dy = point.y - centroid_y
        radius = math.hypot(dx, dy)
        iy += dx * dx
        ix += dy * dy
        ixy += dx * dy
        offsets.append(
            BoltOffset(
                tag=point.tag,
                x=point.x,
                y=point.y,
                dx=dx,
                dy=dy,
                radius=radius,
            )
        )

    return BoltGroupGeometry(
        bolt_count=count,
        centroid_x=centroid_x,
        centroid_y=centroid_y,
        ix=ix,
        iy=iy,
        ixy=ixy,
        ip=ix + iy,
        bolts=tuple(offsets),
    )


def build_in_plane_load(
    *,
    vx: float,
    vy: float,
    mz: float,
    eccentricity_mode: str = "aisc",
    epsilon: float = 1e-12,
) -> InPlaneLoad:
    """Build in-plane load state at centroid plus equivalent eccentricity.

    Inputs:
    - vx, vy: in-plane force components.
    - mz: in-plane moment about centroid.

    `eccentricity_mode`:
    - `aisc`: aligns with Cu-table convention where either ex or ey is set to zero.
    - `perpendicular`: chooses (ex, ey) such that load line is perpendicular to the
      force resultant.

    Constraint satisfied in all modes:
    - vy*ex - vx*ey = mz
    """

    resultant = math.hypot(vx, vy)
    mode = eccentricity_mode.strip().lower().replace("-", "_").replace(" ", "_")

    if resultant <= epsilon:
        ex = 0.0
        ey = 0.0
    elif mode == "aisc":
        if abs(vy) <= epsilon:
            ex = 0.0
            ey = -mz / vx if abs(vx) > epsilon else 0.0
        else:
            ex = mz / vy
            ey = 0.0
    elif mode == "perpendicular":
        # Equivalent to ezbolt "perpendicular" convention:
        # ex = mz*vy / (vx^2 + vy^2)
        # ey = -mz*vx / (vx^2 + vy^2)
        denom = resultant * resultant
        ex = mz * vy / denom
        ey = -mz * vx / denom
    else:
        raise ValueError("eccentricity_mode must be 'aisc' or 'perpendicular'.")

    return InPlaneLoad(
        vx=vx,
        vy=vy,
        mz=mz,
        ex=ex,
        ey=ey,
        resultant=resultant,
    )


def build_in_plane_load_from_explicit_eccentricity(
    *,
    vx: float,
    vy: float,
    ex: float,
    ey: float,
) -> InPlaneLoad:
    """Build in-plane load when eccentricity components are explicitly defined.

    This is the physically explicit representation for applied load line:
    - Mz = Vy*ex - Vx*ey
    """

    mz = vy * ex - vx * ey
    return InPlaneLoad(
        vx=vx,
        vy=vy,
        mz=mz,
        ex=ex,
        ey=ey,
        resultant=math.hypot(vx, vy),
    )


def build_rectangular_bolt_pattern(
    *,
    nx: int,
    ny: int,
    sx: float,
    sy: float,
    x0: float = 0.0,
    y0: float = 0.0,
    tag_prefix: str = "b",
) -> tuple[BoltCoordinate, ...]:
    """Generate a regular nx-by-ny rectangular bolt layout.

    This helper is optional convenience for callers; the core solvers only
    require explicit coordinates.
    """

    if nx < 1 or ny < 1:
        raise ValueError("nx and ny must be >= 1.")
    if sx < 0.0 or sy < 0.0:
        raise ValueError("sx and sy must be >= 0.")

    bolts: list[BoltCoordinate] = []
    index = 1
    for ix in range(nx):
        for iy in range(ny):
            bolts.append(
                BoltCoordinate(
                    tag=f"{tag_prefix}{index}",
                    x=x0 + float(ix) * sx,
                    y=y0 + float(iy) * sy,
                )
            )
            index += 1
    return tuple(bolts)


def ensure_unique_bolt_tags(bolts: Iterable[BoltCoordinate]) -> None:
    """Guardrail utility for deterministic downstream reporting."""

    seen: set[str] = set()
    for point in bolts:
        if point.tag in seen:
            raise ValueError(f"Duplicated bolt tag '{point.tag}' in bolt group.")
        seen.add(point.tag)
