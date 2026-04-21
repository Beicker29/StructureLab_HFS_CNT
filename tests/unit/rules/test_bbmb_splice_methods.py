from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from steel_connections.codes.engineering.common.bolt_group_types import (
    BoltGroupGeometry,
    BoltGroupMethod,
    ElasticECRResult,
    ElasticSuperpositionResult,
    ICRIteration,
    ICRResult,
    InPlaneLoad,
)
from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.domain.rules.aisc360 import bbmb_splice_methods
from steel_connections.models.output import CheckStatus
from steel_connections.models.units import Quantity


EXAMPLE_SPLICE_PATH = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")


def _binding() -> SimpleNamespace:
    return SimpleNamespace(
        rule_id="AISC360.J3.bbmb_splice.step2_pernos1_method",
        name="bbmb splice step2",
        clause="method selector",
        source_document="AISC 360-22",
    )


def _load_case(method: str, *, include_rult: bool) -> object:
    payload = json.loads(EXAMPLE_SPLICE_PATH.read_text(encoding="utf-8"))
    payload.setdefault("procedure", {}).setdefault("icr", {})
    payload["procedure"]["icr"]["method"] = method
    payload["procedure"]["icr"]["tolerance_1"] = 0.01
    payload["procedure"]["icr"]["max_iterations_1"] = 1000
    if include_rult:
        payload["procedure"]["icr"]["rult_1_kip"] = {"value": 25.0, "unit": "kip"}
    else:
        payload["procedure"]["icr"].pop("rult_1_kip", None)
    return parse_and_validate_payload(payload)


def _minimal_geometry() -> BoltGroupGeometry:
    return BoltGroupGeometry(
        bolt_count=2,
        centroid_x=0.0,
        centroid_y=0.0,
        ix=1.0,
        iy=1.0,
        ixy=0.0,
        ip=2.0,
        bolts=tuple(),
    )


def _minimal_load() -> InPlaneLoad:
    return InPlaneLoad(vx=10.0, vy=20.0, mz=50.0, ex=2.5, ey=0.0, resultant=22.360679775)


def test_step2_method_elastic_superposition_governs_status(monkeypatch) -> None:
    case = _load_case("elastic_superposition", include_rult=False)
    active = ElasticSuperpositionResult(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        bolt_forces=tuple(),
        bolt_demand=10.0,
        bolt_capacity=20.0,
        dcr=0.5,
        sum_fx=0.0,
        sum_fy=0.0,
        sum_mz=0.0,
    )
    icr_compare = ICRResult(
        method=BoltGroupMethod.ICR,
        converged=True,
        note=None,
        icr_x=0.1,
        icr_y=-0.2,
        cu=1.5,
        demand=15.0,
        capacity=30.0,
        dcr=0.5,
        final_residual=0.005,
        iterations=(
            ICRIteration(
                iteration=1,
                icr_x=0.1,
                icr_y=-0.2,
                residual_fx=0.0,
                residual_fy=0.0,
                residual_norm=0.005,
                step_dx=0.0,
                step_dy=0.0,
            ),
        ),
        bolt_forces=tuple(),
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_derive_elastic_bolt_capacity_kip",
        lambda *_args, **_kwargs: (20.0, {"phi_bolt_shear": 0.9}),
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_solve_bolt_group_methods",
        lambda **_: {
            "geometry": _minimal_geometry(),
            "load": _minimal_load(),
            "active_result": active,
            "icr_compare": icr_compare,
        },
    )
    result = bbmb_splice_methods.run_step2_pernos1_method(case, _binding())
    assert result.status == CheckStatus.PASS
    assert result.dcr is not None and result.dcr <= 1.0
    assert result.calculation_memory.intermediates["method_report"]["method_selected"] == "elastic_superposition"
    assert result.calculation_memory.intermediates["method_report"]["icr_compare_capacity"] is not None


def test_step2_method_elastic_ecr_governs_status(monkeypatch) -> None:
    case = _load_case("elastic_ecr", include_rult=False)
    active = ElasticECRResult(
        method=BoltGroupMethod.ELASTIC_ECR,
        applicable=True,
        note=None,
        center_x=0.3,
        center_y=0.4,
        ce=1.2,
        demand=12.0,
        capacity=10.0,
        dcr=1.2,
        bolt_forces=tuple(),
        sum_fx=0.0,
        sum_fy=0.0,
        sum_mz=0.0,
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_derive_elastic_bolt_capacity_kip",
        lambda *_args, **_kwargs: (20.0, {"phi_bolt_shear": 0.9}),
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_solve_bolt_group_methods",
        lambda **_: {
            "geometry": _minimal_geometry(),
            "load": _minimal_load(),
            "active_result": active,
            "icr_compare": None,
        },
    )
    result = bbmb_splice_methods.run_step2_pernos1_method(case, _binding())
    assert result.status == CheckStatus.FAIL
    assert result.dcr is not None and result.dcr > 1.0
    assert result.calculation_memory.intermediates["method_report"]["method_selected"] == "elastic_ecr"


def test_step2_method_icr_checks_convergence_acceptance(monkeypatch) -> None:
    case = _load_case("icr", include_rult=True)
    active = ICRResult(
        method=BoltGroupMethod.ICR,
        converged=True,
        note=None,
        icr_x=0.2,
        icr_y=-0.3,
        cu=1.3,
        demand=16.0,
        capacity=20.0,
        dcr=0.8,
        final_residual=0.02,
        iterations=(
            ICRIteration(
                iteration=1,
                icr_x=0.2,
                icr_y=-0.3,
                residual_fx=0.01,
                residual_fy=0.01,
                residual_norm=0.02,
                step_dx=0.0,
                step_dy=0.0,
            ),
        ),
        bolt_forces=tuple(),
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_derive_elastic_bolt_capacity_kip",
        lambda *_args, **_kwargs: (20.0, {"phi_bolt_shear": 0.9}),
    )
    monkeypatch.setattr(
        bbmb_splice_methods,
        "_solve_bolt_group_methods",
        lambda **_: {
            "geometry": _minimal_geometry(),
            "load": _minimal_load(),
            "active_result": active,
            "icr_compare": None,
        },
    )
    result = bbmb_splice_methods.run_step2_pernos1_method(case, _binding())
    assert result.status == CheckStatus.FAIL
    assert result.notes is not None
    assert "convergence acceptance" in result.notes


def test_step2_method_uses_splice_formula_ex_and_input_ey(monkeypatch) -> None:
    case = _load_case("elastic_superposition", include_rult=False)
    case.loads.eccentricity_ey = Quantity(value=40.0, unit="mm")
    case = parse_and_validate_payload(case.model_dump())  # re-validate with explicit fields

    active = ElasticSuperpositionResult(
        method=BoltGroupMethod.ELASTIC_SUPERPOSITION,
        bolt_forces=tuple(),
        bolt_demand=10.0,
        bolt_capacity=20.0,
        dcr=0.5,
        sum_fx=0.0,
        sum_fy=0.0,
        sum_mz=0.0,
    )

    captured: dict[str, float] = {}

    def _capture_solver(**kwargs):  # type: ignore[no-untyped-def]
        captured["ex_in"] = kwargs["ex_in"]
        captured["ey_in"] = kwargs["ey_in"]
        return {
            "geometry": _minimal_geometry(),
            "load": _minimal_load(),
            "active_result": active,
            "icr_compare": None,
        }

    monkeypatch.setattr(
        bbmb_splice_methods,
        "_derive_elastic_bolt_capacity_kip",
        lambda *_args, **_kwargs: (20.0, {"phi_bolt_shear": 0.9}),
    )
    monkeypatch.setattr(bbmb_splice_methods, "_solve_bolt_group_methods", _capture_solver)

    result = bbmb_splice_methods.run_step2_pernos1_method(case, _binding())
    assert result.status == CheckStatus.PASS
    # splice formula: ex = sep + 2*Le1.x1 + (nb1.x-1)*S1.x
    expected_ex_mm = (
        case.geometry.splice_gap.value
        + 2.0 * (case.geometry.web_bolt_edge_distance_x1 or case.geometry.web_bolt_edge_distance).value
        + (case.geometry.web_bolt_lines - 1) * case.geometry.web_bolt_gage.value
    )
    assert captured["ex_in"] == pytest.approx(expected_ex_mm / 25.4)
    assert captured["ey_in"] == pytest.approx(40.0 / 25.4)
    report = result.calculation_memory.intermediates["method_report"]
    assert report["eccentricity_source"] == "splice_formula_ex_plus_input_ey"
