from __future__ import annotations

from steel_connections.models.diagnostics import DesignError
from steel_connections.models.errors import StructuredError
from steel_connections.models.output import (
    CheckResult,
    CheckStatus as LegacyCheckStatus,
    DetailedRunResult,
    GlobalStatus as LegacyGlobalStatus,
)
from steel_connections.models.results import (
    CheckStatus,
    DesignResult,
    DesignStatus,
    DesignSummary,
    LimitStateResult,
)


def map_legacy_check_status(status: LegacyCheckStatus) -> CheckStatus:
    if status == LegacyCheckStatus.PASS:
        return CheckStatus.OK
    if status == LegacyCheckStatus.FAIL:
        return CheckStatus.NG
    return CheckStatus.ERROR


def map_legacy_global_status(status: LegacyGlobalStatus) -> DesignStatus:
    if status == LegacyGlobalStatus.PASS:
        return DesignStatus.OK
    if status == LegacyGlobalStatus.FAIL:
        return DesignStatus.NG
    return DesignStatus.ERROR


def map_structured_error(error: StructuredError) -> DesignError:
    return DesignError(
        error_code=error.error_code.value,
        stage=error.stage.value,
        rule_id=error.rule_id,
        missing_fields=error.missing_fields,
        message=error.message,
        source_document=error.source_document,
    )


def map_check_result(check: CheckResult) -> LimitStateResult:
    status = map_legacy_check_status(check.status)
    check_errors: list[DesignError] = []
    if check.status in {LegacyCheckStatus.ERROR, LegacyCheckStatus.NOT_IMPLEMENTED}:
        check_errors.append(
            DesignError(
                error_code=check.status.value,
                stage="evaluate",
                rule_id=check.rule_id,
                message=check.notes or f"Legacy check ended with status {check.status.value}.",
                source_document=check.source_document,
            )
        )
    memory = check.calculation_memory
    return LimitStateResult(
        name=check.name,
        rule_id=check.rule_id,
        clause=check.clause,
        source_document=check.source_document,
        status=status,
        demand=check.demand,
        capacity=check.capacity,
        dcr=check.dcr,
        equation=memory.equation,
        inputs=memory.inputs,
        intermediates=memory.intermediates,
        derived_values={},
        design_factors=memory.design_factors,
        units=memory.units_trace,
        final_capacity=memory.final_capacity,
        notes=check.notes,
        errors=check_errors,
        na_reason=None,
    )


def map_detailed_run_result(result: DetailedRunResult) -> DesignResult:
    checks = [map_check_result(check) for check in result.checks]
    errors = [map_structured_error(error) for error in result.errors]
    warning_count = sum(len(check.warnings) for check in checks)
    summary = DesignSummary(
        ok_count=sum(1 for check in checks if check.status == CheckStatus.OK),
        ng_count=sum(1 for check in checks if check.status == CheckStatus.NG),
        na_count=sum(1 for check in checks if check.status == CheckStatus.NA),
        error_count=sum(1 for check in checks if check.status == CheckStatus.ERROR),
        warning_count=warning_count,
        worst_dcr=result.summary.worst_dcr,
    )
    return DesignResult(
        project_id=result.project_id,
        case_id=result.case_id,
        connection_family=result.connection_family,
        connection_type=result.connection_type,
        load_state=result.load_state,
        status=map_legacy_global_status(result.global_status),
        checks=checks,
        errors=errors,
        warnings=[],
        summary=summary,
        legacy_result_type="DetailedRunResult",
    )
