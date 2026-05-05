from __future__ import annotations

from pathlib import Path

from steel_connections.adapters.legacy_input import design_input_from_payload, load_legacy_design_input
from steel_connections.domain.engine.validate import (
    load_input_payload,
    parse_and_validate_payload,
)
from steel_connections.domain.engine.result_mapping import (
    map_check_result,
    map_legacy_global_status,
    map_structured_error,
)
from steel_connections.domain.registry import default_registry
from steel_connections.models.errors import StructuredEngineException
from steel_connections.models.design_input import DesignInput
from steel_connections.models.output import (
    CheckStatus,
    DetailedRunResult,
    GlobalStatus,
    RunSummary,
)
from steel_connections.models.results import CheckStatus as DesignCheckStatus
from steel_connections.models.results import DesignResult, DesignSummary


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
    checks, errors = default_registry().evaluate(case)

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


def _build_design_summary(checks: list, worst_dcr: float | None) -> DesignSummary:
    return DesignSummary(
        ok_count=sum(1 for check in checks if check.status == DesignCheckStatus.OK),
        ng_count=sum(1 for check in checks if check.status == DesignCheckStatus.NG),
        na_count=sum(1 for check in checks if check.status == DesignCheckStatus.NA),
        error_count=sum(1 for check in checks if check.status == DesignCheckStatus.ERROR),
        warning_count=sum(len(check.warnings) for check in checks),
        worst_dcr=worst_dcr,
    )


def run_design_input_result(design_input: DesignInput) -> DesignResult:
    """Evaluate a DesignInput and emit DesignResult without building DetailedRunResult."""
    legacy_checks, structured_errors = default_registry().evaluate(design_input)
    legacy_summary = _build_summary(
        [check.status for check in legacy_checks],
        [check.dcr for check in legacy_checks],
    )
    checks = [map_check_result(check) for check in legacy_checks]
    return DesignResult(
        project_id=design_input.project_id,
        case_id=design_input.case_id,
        connection_family=design_input.connection_family,
        connection_type=design_input.connection_type,
        load_state=design_input.load_state,
        status=map_legacy_global_status(_global_status(legacy_summary)),
        checks=checks,
        errors=[map_structured_error(error) for error in structured_errors],
        warnings=[],
        summary=_build_design_summary(checks, legacy_summary.worst_dcr),
        legacy_result_type="CheckResult bridge",
    )


def run_case_payload_design_result(payload: dict) -> DesignResult:
    return run_design_input_result(design_input_from_payload(payload))


def run_case_file_design_result(path: str | Path) -> DesignResult:
    return run_design_input_result(load_legacy_design_input(path))
