from __future__ import annotations

from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.reporting.terminal import render_terminal_summary


def test_terminal_summary_includes_prequalification_status(bueep_4e_payload: dict) -> None:
    result = run_case_payload(bueep_4e_payload)
    text = render_terminal_summary(result)
    assert "PREQUALIFICATION 6.3: PASS" in text
