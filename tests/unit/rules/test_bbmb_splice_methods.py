from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from steel_connections.domain.engine.validate import parse_and_validate_payload
from steel_connections.domain.rules.aisc360 import bbmb_splice_methods
from steel_connections.models.output import CheckStatus


EXAMPLE_SPLICE_PATH = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")


def _binding() -> SimpleNamespace:
    return SimpleNamespace(
        rule_id="AISC360.J3.bbmb_splice.step2_pernos1_method",
        name="bbmb splice step2",
        clause="method selector",
        source_document="AISC 360-22 + ezbolt",
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


def _solved_stub(*, dcr_super: float = 0.6, dcr_ecr: float = 0.7, dcr_icr: float = 0.8, residual: float = 0.005) -> dict:
    return {
        "results": {
            "Elastic Method - Superposition": {
                "Bolt Demand": 10.0,
                "Bolt Capacity": 20.0,
                "DCR": dcr_super,
            },
            "Elastic Method - Center of Rotation": {
                "Connection Demand": 12.0,
                "Connection Capacity": 20.0,
                "DCR": dcr_ecr,
            },
            "Instant Center of Rotation Method": {
                "Connection Demand": 16.0,
                "Connection Capacity": 20.0,
                "DCR": dcr_icr,
                "Cu": 6.2,
            },
        },
        "residual": [residual],
        "n_iterations": 1,
        "final_residual": residual,
    }


def test_step2_method_elastic_superposition_governs_status(monkeypatch) -> None:
    case = _load_case("elastic_superposition", include_rult=False)
    monkeypatch.setattr(
        bbmb_splice_methods,
        "solve_bolt_group_with_ezbolt",
        lambda **_: _solved_stub(dcr_super=0.95),
    )
    result = bbmb_splice_methods.run_step2_pernos1_method(case, _binding())
    assert result.status == CheckStatus.PASS
    assert result.dcr is not None and result.dcr <= 1.0
    assert result.calculation_memory.intermediates["method_report"]["method_selected"] == "elastic_superposition"
    assert result.calculation_memory.intermediates["method_report"]["icr_compare_capacity"] is not None


def test_step2_method_elastic_ecr_governs_status(monkeypatch) -> None:
    case = _load_case("elastic_ecr", include_rult=False)
    monkeypatch.setattr(
        bbmb_splice_methods,
        "solve_bolt_group_with_ezbolt",
        lambda **_: _solved_stub(dcr_ecr=1.15),
    )
    result = bbmb_splice_methods.run_step2_pernos1_method(case, _binding())
    assert result.status == CheckStatus.FAIL
    assert result.dcr is not None and result.dcr > 1.0
    assert result.calculation_memory.intermediates["method_report"]["method_selected"] == "elastic_ecr"


def test_step2_method_icr_checks_convergence_acceptance(monkeypatch) -> None:
    case = _load_case("icr", include_rult=True)
    monkeypatch.setattr(
        bbmb_splice_methods,
        "solve_bolt_group_with_ezbolt",
        lambda **_: _solved_stub(dcr_icr=0.8, residual=0.02),
    )
    result = bbmb_splice_methods.run_step2_pernos1_method(case, _binding())
    assert result.status == CheckStatus.FAIL
    assert result.notes is not None
    assert "convergence acceptance" in result.notes
