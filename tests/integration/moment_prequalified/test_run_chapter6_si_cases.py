from __future__ import annotations

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.models.output import CheckStatus, GlobalStatus


def test_run_si_bueep_4e_case() -> None:
    result = run_case_file("examples/moment_prequalified/case_002_bueep_4e_split_inputs")
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.checks) >= 20
    assert any(check.status == CheckStatus.NOT_IMPLEMENTED for check in result.checks)
    assert any(check.status == CheckStatus.FAIL for check in result.checks)


def test_run_si_bseep_4es_case() -> None:
    result = run_case_file("examples/moment_prequalified/case_004_bseep_4es_split_inputs")
    assert result.global_status == GlobalStatus.ERROR
    assert len(result.checks) == 0
    assert result.summary.error_count >= 1


def test_run_si_bseep_8es_case() -> None:
    result = run_case_file("examples/moment_prequalified/case_003_bseep_8es_split_inputs")
    assert result.global_status == GlobalStatus.FAIL
    assert len(result.checks) >= 30
    assert any(check.status == CheckStatus.FAIL for check in result.checks)
