from __future__ import annotations

from dataclasses import dataclass

from steel_connections.models.results import DesignResult, LimitStateResult


@dataclass(frozen=True)
class CheckProjection:
    index: int
    check: LimitStateResult


@dataclass(frozen=True)
class CriticalCheckProjection:
    rule_id: str
    name: str
    status: str
    dcr: float


@dataclass(frozen=True)
class ReportProjection:
    result: DesignResult
    checks: tuple[CheckProjection, ...]
    critical_checks: tuple[CriticalCheckProjection, ...]

    def check_by_rule_id(self, rule_id: str) -> LimitStateResult | None:
        for item in self.checks:
            if item.check.rule_id == rule_id:
                return item.check
        return None


def build_report_projection(result: DesignResult, *, critical_limit: int = 10) -> ReportProjection:
    checks = tuple(CheckProjection(index=index, check=check) for index, check in enumerate(result.checks, start=1))
    critical = sorted(
        (
            CriticalCheckProjection(
                rule_id=check.rule_id,
                name=check.name,
                status=check.status.value,
                dcr=float(check.dcr),
            )
            for check in result.checks
            if check.dcr is not None
        ),
        key=lambda item: item.dcr,
        reverse=True,
    )
    return ReportProjection(
        result=result,
        checks=checks,
        critical_checks=tuple(critical[:critical_limit]),
    )
