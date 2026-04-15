from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from steel_connections.domain.rules.aisc358 import beam_flange_tension, chapter_06_end_plate, flange_weld_strength
from steel_connections.domain.rules.dg1 import base_plate_anchor
from steel_connections.models.output import CheckResult


@dataclass(frozen=True)
class RuleBinding:
    rule_id: str
    name: str
    source_document: str
    clause: str
    chapter: str
    page: str | None
    connection_family: str
    connection_type: str
    load_state: str
    evaluator: Callable[..., CheckResult | None]


def _bind(
    *,
    rule_id: str,
    name: str,
    clause: str,
    page: str | None,
    connection_type: str,
    evaluator: Callable[..., CheckResult | None],
    source_document: str = "AISC 358-22",
) -> RuleBinding:
    return RuleBinding(
        rule_id=rule_id,
        name=name,
        source_document=source_document,
        clause=clause,
        chapter="6",
        page=page,
        connection_family="moment_prequalified",
        connection_type=connection_type,
        load_state="strength",
        evaluator=evaluator,
    )


def _chapter6_common_steps(connection_type: str) -> list[RuleBinding]:
    return [
        _bind(
            rule_id=f"AISC358.06.3.{connection_type}.prequalification_limits",
            name=f"{connection_type} Section 6.3 prequalification limits",
            clause="Chapter 6 / Section 6.3 + AISC 360-22 Table J3.4",
            page="9.2-24 to 9.2-25",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_section63_prequalification_limits,
        ),
    ]


def _chapter6_4e_specific_steps() -> list[RuleBinding]:
    return []


def _chapter6_stiffened_specific_steps(connection_type: str) -> list[RuleBinding]:
    return []


APPLICABILITY_MATRIX: list[RuleBinding] = [
    RuleBinding(
        rule_id="AISC358.07.7.2.beam_flange_tension_strength",
        name="Beam flange tension strength",
        source_document="AISC 358-22",
        clause="Chapter 7 / Clause 7.2",
        chapter="7",
        page=None,
        connection_family="moment_prequalified",
        connection_type="wuf_w",
        load_state="strength",
        evaluator=beam_flange_tension.run,
    ),
    RuleBinding(
        rule_id="AISC358.07.7.3.flange_weld_strength",
        name="Beam flange weld strength",
        source_document="AISC 358-22",
        clause="Chapter 7 / Clause 7.3",
        chapter="7",
        page=None,
        connection_family="moment_prequalified",
        connection_type="wuf_w",
        load_state="strength",
        evaluator=flange_weld_strength.run,
    ),
    *_chapter6_common_steps("bueep_4e"),
    *_chapter6_4e_specific_steps(),
    *_chapter6_common_steps("bseep_4es"),
    *_chapter6_stiffened_specific_steps("bseep_4es"),
    *_chapter6_common_steps("bseep_8es"),
    *_chapter6_stiffened_specific_steps("bseep_8es"),
    RuleBinding(
        rule_id="DG1.01.1.1.base_plate_anchor_strength",
        name="Base plate and anchor rod design",
        source_document="Design Guide 1 (3rd Edition)",
        clause="Chapter 1 / Scope",
        chapter="1",
        page=None,
        connection_family="base_plate_anchor_rod",
        connection_type="dg1_base_plate",
        load_state="strength",
        evaluator=base_plate_anchor.run,
    ),
]
