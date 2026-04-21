from __future__ import annotations

from typing import Any

from steel_connections.models.errors import not_implemented_error


def solve_bolt_group_with_ezbolt(
    *,
    bolt_points_in: list[tuple[float, float]],
    vx_kip: float,
    vy_kip: float,
    torsion_kip_in: float,
    bolt_capacity_kip: float,
    rule_id: str,
    source_document: str,
) -> dict[str, Any]:
    if not bolt_points_in:
        raise ValueError("At least one bolt coordinate is required to run ezbolt.")

    try:
        import ezbolt  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - dependency gate
        raise not_implemented_error(
            rule_id=rule_id,
            source_document=source_document,
            message=(
                "Optional dependency 'ezbolt' is required for bbmb_splice method selection. "
                "Install with project extra 'icr' (for example: pip install .[icr]). "
                f"Import error: {exc}"
            ),
        )

    bolt_group = ezbolt.BoltGroup()
    for x, y in bolt_points_in:
        bolt_group.add_bolt_single(float(x), float(y))

    results = bolt_group.solve(
        Vx=float(vx_kip),
        Vy=float(vy_kip),
        torsion=float(torsion_kip_in),
        bolt_capacity=float(bolt_capacity_kip),
        verbose=False,
        ecc_method="AISC",
    )
    residual = getattr(bolt_group, "residual", None)
    if isinstance(residual, list):
        n_iterations = len(residual)
        final_residual = float(residual[-1]) if residual else None
    else:
        n_iterations = None
        final_residual = None

    return {
        "results": results,
        "residual": residual,
        "n_iterations": n_iterations,
        "final_residual": final_residual,
    }
