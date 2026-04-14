from __future__ import annotations

from steel_connections.domain.routing.applicability_matrix import RuleBinding
from steel_connections.models.errors import (
    ErrorCode,
    Stage,
    StructuredEngineException,
    StructuredError,
)
from steel_connections.models.input import InputCase
from steel_connections.models.output import CalculationMemory, CheckResult, CheckStatus


def _check_from_error(binding: RuleBinding, error: StructuredError) -> CheckResult:
    status = CheckStatus.ERROR
    if error.error_code == ErrorCode.NOT_IMPLEMENTED:
        status = CheckStatus.NOT_IMPLEMENTED
    return CheckResult(
        name=binding.name,
        rule_id=binding.rule_id,
        clause=binding.clause,
        source_document=binding.source_document,
        demand=None,
        capacity=None,
        dcr=None,
        status=status,
        calculation_memory=CalculationMemory(
            inputs={},
            intermediates={},
            design_factors={},
            equation="not_available_due_to_error",
            units_trace={},
            final_capacity=None,
        ),
        notes=error.message,
    )


def evaluate_rules(
    *,
    case: InputCase,
    applicable_rules: list[RuleBinding],
) -> tuple[list[CheckResult], list[StructuredError]]:
    checks: list[CheckResult] = []
    errors: list[StructuredError] = []

    for binding in applicable_rules:
        try:
            result = binding.evaluator(case, binding)
        except StructuredEngineException as exc:
            errors.append(exc.error)
            checks.append(_check_from_error(binding, exc.error))
            break
        except Exception as exc:  # pragma: no cover - defensive branch
            internal_error = StructuredError(
                error_code=ErrorCode.INTERNAL_ERROR,
                stage=Stage.EVALUATE,
                rule_id=binding.rule_id,
                missing_fields=None,
                message=f"Unexpected engine error: {exc}",
                source_document=binding.source_document,
            )
            errors.append(internal_error)
            checks.append(_check_from_error(binding, internal_error))
            break

        if result is None:
            internal_error = StructuredError(
                error_code=ErrorCode.INTERNAL_ERROR,
                stage=Stage.EVALUATE,
                rule_id=binding.rule_id,
                missing_fields=None,
                message="Rule evaluator returned no result.",
                source_document=binding.source_document,
            )
            errors.append(internal_error)
            checks.append(_check_from_error(binding, internal_error))
            break

        checks.append(result)

    return checks, errors
