from __future__ import annotations

from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.models.output import CheckStatus, GlobalStatus


def test_dg1_applicable_rule_not_implemented_is_blocking(dg1_payload: dict) -> None:
    result = run_case_payload(dg1_payload)

    assert result.global_status == GlobalStatus.ERROR
    assert result.summary.not_implemented_count == 1
    assert len(result.errors) == 1
    assert result.checks[0].status == CheckStatus.NOT_IMPLEMENTED
