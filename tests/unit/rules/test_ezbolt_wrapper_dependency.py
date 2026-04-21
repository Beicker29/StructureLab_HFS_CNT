from __future__ import annotations

import builtins

import pytest

from steel_connections.domain.rules.aisc360.ezbolt_wrapper import solve_bolt_group_with_ezbolt
from steel_connections.models.errors import ErrorCode, StructuredEngineException


def test_ezbolt_wrapper_raises_structured_error_when_dependency_missing(monkeypatch) -> None:
    original_import = builtins.__import__

    def _import_hook(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name == "ezbolt":
            raise ModuleNotFoundError("No module named 'ezbolt'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _import_hook)

    with pytest.raises(StructuredEngineException) as exc_info:
        solve_bolt_group_with_ezbolt(
            bolt_points_in=[(0.0, 0.0), (1.0, 0.0)],
            vx_kip=10.0,
            vy_kip=20.0,
            torsion_kip_in=50.0,
            bolt_capacity_kip=15.0,
            rule_id="AISC360.J3.bbmb_splice.step2_pernos1_method",
            source_document="AISC 360-22 + ezbolt",
        )
    assert exc_info.value.error.error_code == ErrorCode.NOT_IMPLEMENTED
