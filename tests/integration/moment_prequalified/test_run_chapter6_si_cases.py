from __future__ import annotations

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.models.output import CheckStatus, GlobalStatus


def test_run_si_bueep_4e_case() -> None:
    result = run_case_file("examples/moment_prequalified/case_002_bueep_4e.json")
    assert result.global_status == GlobalStatus.PASS
    assert len(result.checks) == 28
    assert all(check.status == CheckStatus.PASS for check in result.checks)


def test_run_si_bseep_4es_case() -> None:
    result = run_case_file("examples/moment_prequalified/case_004_bseep_4es.json")
    assert result.global_status == GlobalStatus.PASS
    assert len(result.checks) == 29
    assert all(check.status == CheckStatus.PASS for check in result.checks)


def test_run_si_bseep_8es_case() -> None:
    result = run_case_file("examples/moment_prequalified/case_003_bseep_8es.json")
    assert result.global_status == GlobalStatus.PASS
    assert len(result.checks) == 29
    assert all(check.status == CheckStatus.PASS for check in result.checks)
