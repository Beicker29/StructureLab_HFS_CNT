from __future__ import annotations

from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.models.output import CheckStatus, GlobalStatus


def test_run_bueep_4e_case(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.checks) >= 15
    assert any(check.status == CheckStatus.FAIL for check in result.checks)
    assert any(check.status == CheckStatus.NOT_IMPLEMENTED for check in result.checks)


def test_run_bseep_8es_case(bseep_8es_payload: dict) -> None:
    result = run_case_payload(bseep_8es_payload)
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.checks) >= 30
    assert any(check.status == CheckStatus.FAIL for check in result.checks)
    assert any(check.status == CheckStatus.NOT_IMPLEMENTED for check in result.checks)


def test_run_bseep_4es_case(bseep_4es_payload: dict) -> None:
    result = run_case_payload(bseep_4es_payload)
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.checks) >= 30
    assert any(check.status == CheckStatus.FAIL for check in result.checks)
    assert any(check.status == CheckStatus.NOT_IMPLEMENTED for check in result.checks)
