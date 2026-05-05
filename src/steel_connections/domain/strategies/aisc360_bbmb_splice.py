from __future__ import annotations

from dataclasses import dataclass

from steel_connections.domain.registry import (
    DesignContext,
    RuleSpec,
    describe_design_input,
    evaluate_strategy_rules,
    select_rule_bindings,
)
from steel_connections.models.design_input import DesignInput
from steel_connections.models.errors import StructuredError
from steel_connections.models.input import InputCase
from steel_connections.models.output import CheckResult


@dataclass(frozen=True)
class AISC360BBMBSpliceStrategy:
    strategy_id: str = "aisc360.bbmb_splice"
    connection_family: str = "Fully_Restrained_Moment"
    connection_types: tuple[str, ...] = ("bbmb_splice",)
    load_state: str = "strength"

    def supports(self, design_input: InputCase | DesignInput) -> bool:
        descriptor = describe_design_input(design_input)
        return (
            descriptor.connection_family == self.connection_family
            and descriptor.connection_type in self.connection_types
            and descriptor.load_state == self.load_state
        )

    def applicable_rules(self, design_input: InputCase | DesignInput) -> list[RuleSpec]:
        return select_rule_bindings(
            design_input,
            connection_family=self.connection_family,
            connection_types=self.connection_types,
            load_state=self.load_state,
        )

    def evaluate(
        self,
        design_input: InputCase | DesignInput,
        context: DesignContext | None = None,
    ) -> tuple[list[CheckResult], list[StructuredError]]:
        return evaluate_strategy_rules(self, design_input, context)
