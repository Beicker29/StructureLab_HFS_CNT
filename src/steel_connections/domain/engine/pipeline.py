from __future__ import annotations

from pathlib import Path

from steel_connections.domain.engine.evaluate import evaluate_rules
from steel_connections.domain.engine.validate import (
    load_input_payload,
    parse_and_validate_payload,
)
from steel_connections.domain.routing.dispatcher import resolve_applicable_rules
from steel_connections.models.errors import StructuredEngineException
from steel_connections.models.output import (
    CheckStatus,
    DetailedRunResult,
    GlobalStatus,
    RunSummary,
)


def _build_summary(statuses: list[CheckStatus], dcr_values: list[float | None]) -> RunSummary:
    filtered_dcr = [value for value in dcr_values if value is not None]
    worst_dcr = max(filtered_dcr) if filtered_dcr else None
    return RunSummary(
        pass_count=sum(1 for s in statuses if s == CheckStatus.PASS),
        fail_count=sum(1 for s in statuses if s == CheckStatus.FAIL),
        error_count=sum(1 for s in statuses if s == CheckStatus.ERROR),
        not_implemented_count=sum(1 for s in statuses if s == CheckStatus.NOT_IMPLEMENTED),
        worst_dcr=worst_dcr,
    )


def _global_status(summary: RunSummary) -> GlobalStatus:
    if summary.error_count > 0 or summary.not_implemented_count > 0:
        return GlobalStatus.ERROR
    if summary.fail_count > 0:
        return GlobalStatus.FAIL
    return GlobalStatus.PASS


def run_case_payload(payload: dict) -> DetailedRunResult:
    case = parse_and_validate_payload(payload)
    applicable_rules = resolve_applicable_rules(case)
    checks, errors = evaluate_rules(case=case, applicable_rules=applicable_rules)

    summary = _build_summary([check.status for check in checks], [check.dcr for check in checks])
    return DetailedRunResult(
        project_id=case.project_id,
        case_id=case.case_id,
        connection_family=case.connection_family,
        connection_type=case.connection_type,
        load_state=case.load_state,
        global_status=_global_status(summary),
        checks=checks,
        errors=errors,
        summary=summary,
    )


def run_case_file(path: str | Path) -> DetailedRunResult:
    try:
        payload = load_input_payload(path)
    except StructuredEngineException as exc:
        input_path = Path(path)
        summary = RunSummary(
            pass_count=0,
            fail_count=0,
            error_count=1,
            not_implemented_count=0,
            worst_dcr=None,
        )
        return DetailedRunResult(
            project_id="unknown_project",
            case_id=input_path.stem,
            connection_family="unknown_family",
            connection_type="unknown_type",
            load_state="unknown_load_state",
            global_status=GlobalStatus.ERROR,
            checks=[],
            errors=[exc.error],
            summary=summary,
        )
    try:
        return run_case_payload(payload)
    except StructuredEngineException as exc:
        project_id = payload.get("project_id", "unknown_project")
        case_id = payload.get("case_id", "unknown_case")
        connection_family = payload.get("connection_family", "unknown_family")
        connection_type = payload.get("connection_type", "unknown_type")
        load_state = payload.get("load_state", "unknown_load_state")
        summary = RunSummary(
            pass_count=0,
            fail_count=0,
            error_count=1,
            not_implemented_count=0,
            worst_dcr=None,
        )
        return DetailedRunResult(
            project_id=project_id,
            case_id=case_id,
            connection_family=connection_family,
            connection_type=connection_type,
            load_state=load_state,
            global_status=GlobalStatus.ERROR,
            checks=[],
            errors=[exc.error],
            summary=summary,
        )
