from __future__ import annotations

from steel_connections.models.output import CheckStatus
from steel_connections.models.output import DetailedRunResult


def render_terminal_summary(result: DetailedRunResult) -> str:
    summary = result.summary
    worst_dcr = "n/a" if summary.worst_dcr is None else f"{summary.worst_dcr:.4f}"
    lines = [
        f"CASE: {result.project_id}/{result.case_id}",
        f"FAMILY: {result.connection_family} | TYPE: {result.connection_type} | LOAD STATE: {result.load_state}",
        f"GLOBAL STATUS: {result.global_status.value}",
        (
            "COUNTS: "
            f"PASS={summary.pass_count} "
            f"FAIL={summary.fail_count} "
            f"ERROR={summary.error_count} "
            f"NOT_IMPLEMENTED={summary.not_implemented_count}"
        ),
        f"WORST DCR: {worst_dcr}",
    ]

    prequalification_checks = [check for check in result.checks if ".06.3." in check.rule_id]
    if prequalification_checks:
        prequalification_status = CheckStatus.PASS
        if any(check.status == CheckStatus.ERROR for check in prequalification_checks):
            prequalification_status = CheckStatus.ERROR
        elif any(check.status == CheckStatus.FAIL for check in prequalification_checks):
            prequalification_status = CheckStatus.FAIL
        elif any(check.status == CheckStatus.NOT_IMPLEMENTED for check in prequalification_checks):
            prequalification_status = CheckStatus.NOT_IMPLEMENTED
        worst_prequalification_dcr = max(
            (check.dcr for check in prequalification_checks if check.dcr is not None),
            default=None,
        )
        prequalification_worst = "n/a" if worst_prequalification_dcr is None else f"{worst_prequalification_dcr:.4f}"
        lines.append(f"PREQUALIFICATION 6.3: {prequalification_status.value} | WORST DCR: {prequalification_worst}")

    return "\n".join(lines)
