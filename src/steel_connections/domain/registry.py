from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from steel_connections.domain.engine.evaluate import evaluate_rules
from steel_connections.domain.routing.applicability_matrix import APPLICABILITY_MATRIX, RuleBinding
from steel_connections.models.design_input import DesignInput
from steel_connections.models.errors import ErrorCode, Stage, StructuredEngineException, StructuredError
from steel_connections.models.input import InputCase
from steel_connections.models.output import CheckResult


RuleSpec = RuleBinding


@dataclass(frozen=True)
class DesignContext:
    fail_fast: bool = True
    code_context: str | None = None


@dataclass(frozen=True)
class DesignInputDescriptor:
    connection_family: str
    connection_type: str
    load_state: str


class DesignStrategy(Protocol):
    strategy_id: str

    def supports(self, design_input: InputCase | DesignInput) -> bool: ...

    def applicable_rules(self, design_input: InputCase | DesignInput) -> list[RuleSpec]: ...

    def evaluate(
        self,
        design_input: InputCase | DesignInput,
        context: DesignContext | None = None,
    ) -> tuple[list[CheckResult], list[StructuredError]]: ...


def coerce_legacy_case(design_input: InputCase | DesignInput) -> InputCase:
    if isinstance(design_input, DesignInput):
        return design_input.to_legacy_case()
    return design_input


def describe_design_input(design_input: InputCase | DesignInput) -> DesignInputDescriptor:
    if isinstance(design_input, DesignInput):
        return DesignInputDescriptor(
            connection_family=design_input.connection_family,
            connection_type=design_input.connection_type,
            load_state=design_input.load_state,
        )
    return DesignInputDescriptor(
        connection_family=design_input.connection_family,
        connection_type=design_input.connection_type,
        load_state=design_input.load_state,
    )


def _side_filtered_rules(design_input: InputCase | DesignInput, rules: list[RuleBinding]) -> list[RuleBinding]:
    case = coerce_legacy_case(design_input)
    if (
        case.connection_family == "moment_prequalified"
        and hasattr(case, "design_factors")
        and getattr(case.design_factors, "beam_connection_sides", None) is not None
    ):
        sides = str(case.design_factors.beam_connection_sides)
        filtered: list[RuleBinding] = []
        for item in rules:
            rule_id = str(item.rule_id).lower()
            if rule_id.endswith("_vgizq") and sides not in {"left_only", "both_sides"}:
                continue
            if rule_id.endswith("_vgder") and sides not in {"right_only", "both_sides"}:
                continue
            filtered.append(item)
        return filtered
    return rules


def select_rule_bindings(
    design_input: InputCase | DesignInput,
    *,
    connection_family: str,
    connection_types: tuple[str, ...],
    load_state: str = "strength",
) -> list[RuleSpec]:
    descriptor = describe_design_input(design_input)
    matches = [
        item
        for item in APPLICABILITY_MATRIX
        if item.connection_family == connection_family
        and item.connection_type in connection_types
        and item.connection_family == descriptor.connection_family
        and item.connection_type == descriptor.connection_type
        and item.load_state == descriptor.load_state
        and item.load_state == load_state
    ]
    return _side_filtered_rules(design_input, matches)


def evaluate_strategy_rules(
    strategy: DesignStrategy,
    design_input: InputCase | DesignInput,
    context: DesignContext | None = None,
) -> tuple[list[CheckResult], list[StructuredError]]:
    _ = context or DesignContext()
    case = coerce_legacy_case(design_input)
    return evaluate_rules(case=case, applicable_rules=strategy.applicable_rules(design_input))


def _routing_error(case: InputCase) -> StructuredEngineException:
    return StructuredEngineException(
        StructuredError(
            error_code=ErrorCode.ROUTING_ERROR,
            stage=Stage.ROUTE,
            rule_id=None,
            missing_fields=None,
            message=(
                "No applicable rules found for "
                f"{case.connection_family}/{case.connection_type}/{case.load_state}."
            ),
            source_document=None,
        )
    )


@dataclass
class DesignRegistry:
    strategies: list[DesignStrategy]

    def register(self, strategy: DesignStrategy) -> None:
        self.strategies.append(strategy)

    def resolve(self, design_input: InputCase | DesignInput) -> DesignStrategy:
        case = coerce_legacy_case(design_input)
        for strategy in self.strategies:
            if strategy.supports(design_input):
                return strategy
        raise _routing_error(case)

    def applicable_rules(self, design_input: InputCase | DesignInput) -> list[RuleSpec]:
        case = coerce_legacy_case(design_input)
        rules = self.resolve(design_input).applicable_rules(design_input)
        if not rules:
            raise _routing_error(case)
        return rules

    def evaluate(
        self,
        design_input: InputCase | DesignInput,
        context: DesignContext | None = None,
    ) -> tuple[list[CheckResult], list[StructuredError]]:
        strategy = self.resolve(design_input)
        return strategy.evaluate(design_input, context)


def build_default_registry() -> DesignRegistry:
    from steel_connections.domain.strategies.aisc358_end_plate import AISC358EndPlateStrategy
    from steel_connections.domain.strategies.aisc358_wufw import AISC358WufWStrategy
    from steel_connections.domain.strategies.aisc360_bbmb_splice import AISC360BBMBSpliceStrategy
    from steel_connections.domain.strategies.dg1_base_plate import DG1BasePlateStrategy

    return DesignRegistry(
        strategies=[
            AISC358WufWStrategy(),
            AISC358EndPlateStrategy(),
            AISC360BBMBSpliceStrategy(),
            DG1BasePlateStrategy(),
        ]
    )


_DEFAULT_REGISTRY: DesignRegistry | None = None


def default_registry() -> DesignRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = build_default_registry()
    return _DEFAULT_REGISTRY
