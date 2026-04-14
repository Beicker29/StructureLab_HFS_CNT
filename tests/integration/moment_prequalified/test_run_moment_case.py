from __future__ import annotations

import json
import shutil
from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.models.output import CheckStatus, GlobalStatus
from steel_connections.reporting.json_writer import write_detailed_result


def test_run_moment_case_and_write_result(moment_payload: dict) -> None:
    result = run_case_payload(moment_payload)
    out_root = Path(".tmp_test_outputs")
    output_path = write_detailed_result(result, out_root)

    assert result.global_status in (GlobalStatus.PASS, GlobalStatus.FAIL)
    assert len(result.checks) == 2
    assert all(check.status in (CheckStatus.PASS, CheckStatus.FAIL) for check in result.checks)
    assert output_path.exists()

    dumped = json.loads(output_path.read_text(encoding="utf-8"))
    assert dumped["case_id"] == "case_001"
    assert len(dumped["checks"]) == 2
    if out_root.exists():
        shutil.rmtree(out_root, ignore_errors=True)
