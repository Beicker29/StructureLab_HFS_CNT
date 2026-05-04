from __future__ import annotations

import json
from pathlib import Path

from steel_connections.codes.engineering.common.bolt_group_types import (
    BoltGroupGeometry,
    BoltGroupMethod,
    ElasticSuperpositionResult,
    ICRIteration,
    ICRResult,
    InPlaneLoad,
)
from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.domain.rules.aisc360 import bbmb_splice_methods
from steel_connections.reporting.markdown_writer import render_memory_markdown


EXAMPLE_SPLICE_PATH = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")


def _stub_solver_payload() -> dict:
    active = ElasticSuperpositionResult(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        bolt_forces=tuple(),
        bolt_demand=9.0,
        bolt_capacity=20.0,
        dcr=0.45,
        sum_fx=0.0,
        sum_fy=0.0,
        sum_mz=0.0,
    )
    icr_compare = ICRResult(
        method=BoltGroupMethod.ICR,
        converged=True,
        note=None,
        icr_x=0.1,
        icr_y=-0.1,
        cu=1.8,
        demand=13.0,
        capacity=20.0,
        dcr=0.65,
        final_residual=0.005,
        iterations=(
            ICRIteration(
                iteration=1,
                icr_x=0.1,
                icr_y=-0.1,
                residual_fx=0.0,
                residual_fy=0.0,
                residual_norm=0.005,
                step_dx=0.0,
                step_dy=0.0,
            ),
        ),
        bolt_forces=tuple(),
    )
    return {
        "geometry": BoltGroupGeometry(
            bolt_count=2,
            centroid_x=0.0,
            centroid_y=0.0,
            ix=1.0,
            iy=1.0,
            ixy=0.0,
            ip=2.0,
            bolts=tuple(),
        ),
        "load": InPlaneLoad(vx=10.0, vy=20.0, mz=50.0, ex=2.5, ey=0.0, resultant=22.360679775),
        "active_result": active,
        "icr_compare": icr_compare,
    }


def _stub_solver_payload_icr() -> dict:
    active = ICRResult(
        method=BoltGroupMethod.ICR,
        converged=True,
        note=None,
        icr_x=0.1,
        icr_y=-0.1,
        cu=1.75,
        demand=13.0,
        capacity=20.0,
        dcr=0.65,
        final_residual=0.005,
        iterations=(
            ICRIteration(
                iteration=1,
                icr_x=0.1,
                icr_y=-0.1,
                residual_fx=0.0,
                residual_fy=0.0,
                residual_norm=0.005,
                step_dx=0.0,
                step_dy=0.0,
            ),
        ),
        bolt_forces=tuple(),
    )
    return {
        "geometry": BoltGroupGeometry(
            bolt_count=2,
            centroid_x=0.0,
            centroid_y=0.0,
            ix=1.0,
            iy=1.0,
            ixy=0.0,
            ip=2.0,
            bolts=tuple(),
        ),
        "load": InPlaneLoad(vx=10.0, vy=20.0, mz=50.0, ex=2.5, ey=0.0, resultant=22.360679775),
        "active_result": active,
        "icr_compare": None,
    }


def test_splice_memory_includes_step2_method_block(monkeypatch) -> None:
    payload = json.loads(EXAMPLE_SPLICE_PATH.read_text(encoding="utf-8"))
    payload.setdefault("procedure", {}).setdefault("icr", {})
    payload["procedure"]["icr"]["method"] = "Elastic Method - Superposition"

    monkeypatch.setattr(
        bbmb_splice_methods,
        "_derive_elastic_bolt_capacity_kip",
        lambda *_args, **_kwargs: (20.0, {"phi_bv": 0.9}),
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_solve_bolt_group_methods",
        lambda **_: _stub_solver_payload(),
    )
    result = run_case_payload(payload)
    memory = render_memory_markdown(result)
    assert "## Paso 3 - Metodo ICR/Elastic para grupo de pernos 1" in memory
    assert "### 3.1 Metodo ICR/Elastic" in memory
    assert "Metodo seleccionado: `elastic_superposition`" in memory
    assert "Picr comparativo" in memory


def test_splice_memory_prints_cu_when_method_is_icr(monkeypatch) -> None:
    payload = json.loads(EXAMPLE_SPLICE_PATH.read_text(encoding="utf-8"))
    payload.setdefault("procedure", {}).setdefault("icr", {})
    payload["procedure"]["icr"]["method"] = "Instant Center of Rotation Method"
    payload["procedure"]["icr"]["rult_1_kip"] = {"value": 25.0, "unit": "kip"}

    monkeypatch.setattr(
        bbmb_splice_methods,
        "_derive_elastic_bolt_capacity_kip",
        lambda *_args, **_kwargs: (20.0, {"phi_bv": 0.9}),
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_solve_bolt_group_methods",
        lambda **_: _stub_solver_payload_icr(),
    )
    result = run_case_payload(payload)
    memory = render_memory_markdown(result)
    assert "Metodo seleccionado: `icr`" in memory
    assert "Coeficiente Cu (ICR): `1.75`" in memory
