from __future__ import annotations

from steel_connections.models.units import Quantity, UnitSystem


def _table61_length(*, us_in: float, unit_system: UnitSystem) -> Quantity:
    if unit_system == UnitSystem.US:
        return Quantity(value=us_in, unit="in")
    # Exact in->mm conversion to keep parity with paired US/SI tabulated values.
    return Quantity(value=us_in * 25.4, unit="mm")


def compute_limites_precalificacion_conexion_tipo_ep(
    *,
    connection_type: str,
    unit_system: UnitSystem,
) -> dict[str, tuple[Quantity, Quantity] | None]:
    """Return Table 6.1 geometric limits for EP prequalified connections.

    Scope:
    - bueep_4e
    - bseep_4es
    - bseep_8es

    The function centralizes Table 6.1 ranges in one reusable location for
    all prequalified EP connection checks.
    """
    table_61_limits: dict[str, dict[str, tuple[Quantity, Quantity] | None]] = {
        "bueep_4e": {
            "tbf": (_table61_length(us_in=3.0 / 8.0, unit_system=unit_system), _table61_length(us_in=3.0 / 4.0, unit_system=unit_system)),
            "bbf": (_table61_length(us_in=6.0, unit_system=unit_system), _table61_length(us_in=9.25, unit_system=unit_system)),
            "d": (_table61_length(us_in=13.75, unit_system=unit_system), _table61_length(us_in=24.0, unit_system=unit_system)),
            "tp": (_table61_length(us_in=0.5, unit_system=unit_system), _table61_length(us_in=2.25, unit_system=unit_system)),
            "bp": (_table61_length(us_in=7.0, unit_system=unit_system), _table61_length(us_in=10.75, unit_system=unit_system)),
            "g": (_table61_length(us_in=4.0, unit_system=unit_system), _table61_length(us_in=6.0, unit_system=unit_system)),
            "pfi": (_table61_length(us_in=1.5, unit_system=unit_system), _table61_length(us_in=4.5, unit_system=unit_system)),
            "pfo": (_table61_length(us_in=1.5, unit_system=unit_system), _table61_length(us_in=4.5, unit_system=unit_system)),
            "pb": None,
        },
        "bseep_4es": {
            "tbf": (_table61_length(us_in=3.0 / 8.0, unit_system=unit_system), _table61_length(us_in=3.0 / 4.0, unit_system=unit_system)),
            "bbf": (_table61_length(us_in=6.0, unit_system=unit_system), _table61_length(us_in=9.0, unit_system=unit_system)),
            "d": (_table61_length(us_in=13.75, unit_system=unit_system), _table61_length(us_in=24.0, unit_system=unit_system)),
            "tp": (_table61_length(us_in=0.5, unit_system=unit_system), _table61_length(us_in=1.5, unit_system=unit_system)),
            "bp": (_table61_length(us_in=7.0, unit_system=unit_system), _table61_length(us_in=10.75, unit_system=unit_system)),
            "g": (_table61_length(us_in=3.25, unit_system=unit_system), _table61_length(us_in=6.0, unit_system=unit_system)),
            "pfi": (_table61_length(us_in=1.75, unit_system=unit_system), _table61_length(us_in=5.5, unit_system=unit_system)),
            "pfo": (_table61_length(us_in=1.75, unit_system=unit_system), _table61_length(us_in=5.5, unit_system=unit_system)),
            "pb": None,
        },
        "bseep_8es": {
            "tbf": (_table61_length(us_in=9.0 / 16.0, unit_system=unit_system), _table61_length(us_in=1.0, unit_system=unit_system)),
            "bbf": (_table61_length(us_in=7.5, unit_system=unit_system), _table61_length(us_in=12.25, unit_system=unit_system)),
            "d": (_table61_length(us_in=18.0, unit_system=unit_system), _table61_length(us_in=36.0, unit_system=unit_system)),
            "tp": (_table61_length(us_in=0.75, unit_system=unit_system), _table61_length(us_in=2.5, unit_system=unit_system)),
            "bp": (_table61_length(us_in=9.0, unit_system=unit_system), _table61_length(us_in=15.0, unit_system=unit_system)),
            "g": (_table61_length(us_in=5.0, unit_system=unit_system), _table61_length(us_in=6.0, unit_system=unit_system)),
            "pfi": (_table61_length(us_in=1.625, unit_system=unit_system), _table61_length(us_in=2.0, unit_system=unit_system)),
            "pfo": (_table61_length(us_in=1.625, unit_system=unit_system), _table61_length(us_in=2.0, unit_system=unit_system)),
            "pb": None,
        },
    }

    normalized = str(connection_type).strip().lower()
    if normalized not in table_61_limits:
        raise ValueError(
            "Unsupported prequalified EP connection type for Table 6.1 limits: "
            f"{connection_type!r}. Expected one of: bueep_4e, bseep_4es, bseep_8es."
        )
    return table_61_limits[normalized]

