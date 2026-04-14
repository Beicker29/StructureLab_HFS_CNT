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
            rule_id=f"AISC358.06.7.1.{connection_type}.step1_mpr",
            name=f"{connection_type} Step 1 probable moment at plastic hinge",
            clause="Chapter 6 / Section 6.7.1 Step 1 + Section 2.4.3 Eq. 2.4-1/2.4-2",
            page="9.2-8 to 9.2-9",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step1_probable_moment_plastic_hinge,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step1a_compactness",
            name=f"{connection_type} Step 1a member compactness by ductility demand",
            clause="AISC 341-22 / Table D1.1 (Cases for flange and web compactness)",
            page=None,
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step1a_member_compactness,
            source_document="AISC 341-22",
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step2_sh",
            name=f"{connection_type} Step 2 plastic hinge distance",
            clause="Chapter 6 / Section 6.7.1 Step 2 Eq. 6.7-1/6.7-2",
            page="9.2-29",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step2_plastic_hinge_distance,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step3_vh",
            name=f"{connection_type} Step 3 shear at plastic hinge",
            clause="Chapter 6 / Section 6.7.1 Step 3 + Section 2.4.4 Eq. 2.4-3",
            page="9.2-8",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step3_shear_at_plastic_hinge,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step4_mf",
            name=f"{connection_type} Step 4 probable moment at column face",
            clause="Chapter 6 / Section 6.7.1 Step 4 + Section 2.4.5 Eq. 2.4-4",
            page="9.2-9",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step4_probable_moment_face_column,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step5_preliminary_geometry",
            name=f"{connection_type} Step 5 preliminary geometry and bolt grade",
            clause="Chapter 6 / Section 6.7.1 Step 5",
            page="9.2-29",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step5_preliminary_geometry_selection,
        ),
        _bind(
            rule_id=f"AISC358.06.3.{connection_type}.prequalification_limits",
            name=f"{connection_type} Section 6.3 prequalification limits",
            clause="Chapter 6 / Section 6.3 + AISC 360-22 Table J3.4",
            page="9.2-24 to 9.2-25",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_section63_prequalification_limits,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step6_db_required",
            name=f"{connection_type} Step 6 required bolt diameter",
            clause="Chapter 6 / Section 6.7.1 Step 6 Eq. 6.7-3/6.7-4",
            page="9.2-30",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step6_required_bolt_diameter,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step7_db_trial",
            name=f"{connection_type} Step 7 trial bolt diameter",
            clause="Chapter 6 / Section 6.7.1 Step 7",
            page="9.2-30",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step7_select_trial_bolt,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step8_tp_required",
            name=f"{connection_type} Step 8 required end-plate thickness",
            clause="Chapter 6 / Section 6.7.1 Step 8 Eq. 6.7-5",
            page="9.2-30",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step8_required_end_plate_thickness,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step9_tp_trial",
            name=f"{connection_type} Step 9 trial end-plate thickness",
            clause="Chapter 6 / Section 6.7.1 Step 9",
            page="9.2-30",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step9_select_end_plate_thickness,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step10_ffu",
            name=f"{connection_type} Step 10 factored beam flange force",
            clause="Chapter 6 / Section 6.7.1 Step 10 Eq. 6.7-6",
            page="9.2-30",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step10_factored_beam_flange_force,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step14_beam_shear_strength",
            name=f"{connection_type} Step 14 beam shear strength",
            clause="Chapter 6 / Section 6.7.1 Step 14 + Section 2.5",
            page="9.2-35",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step14_beam_shear_strength,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step15_connection_shear",
            name=f"{connection_type} Step 15 connection shear requirement",
            clause="Chapter 6 / Section 6.7.1 Step 15",
            page="9.2-35",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step15_connection_shear_requirement,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step16_bolt_shear_rupture",
            name=f"{connection_type} Step 16 bolt shear rupture",
            clause="Chapter 6 / Section 6.7.1 Step 16 Eq. 6.7-11",
            page="9.2-35",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_bolt_shear_rupture,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step17_bearing_tearout_end_plate",
            name=f"{connection_type} Step 17 bolt bearing/tearout end plate",
            clause="Chapter 6 / Section 6.7.1 Step 17 Eq. 6.7-12",
            page="9.2-35",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_bolt_bearing_tearout_end_plate,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step17_bearing_tearout_column_flange",
            name=f"{connection_type} Step 17 bolt bearing/tearout column flange",
            clause="Chapter 6 / Section 6.7.1 Step 17 Eq. 6.7-12",
            page="9.2-35",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_bolt_bearing_tearout_column_flange,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step18_weld_design",
            name=f"{connection_type} Step 18 weld design",
            clause="Chapter 6 / Section 6.7.1 Step 18 + Section 6.6.6",
            page="9.2-29",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step18_weld_design,
        ),
        _bind(
            rule_id=f"AISC358.06.7.2.{connection_type}.step1_column_flange_yielding",
            name=f"{connection_type} Column Step 1 column flange yielding",
            clause="Chapter 6 / Section 6.7.2 Step 1 Eq. 6.7-13",
            page="9.2-35",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step1_flange_yielding,
        ),
        _bind(
            rule_id=f"AISC358.06.7.2.{connection_type}.step2_column_stiffener_force",
            name=f"{connection_type} Column Step 2 stiffener force",
            clause="Chapter 6 / Section 6.7.2 Step 2 Eq. 6.7-14/6.7-15",
            page="9.2-36",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step2_stiffener_force,
        ),
        _bind(
            rule_id=f"AISC358.06.7.2.{connection_type}.step3_column_web_local_yielding",
            name=f"{connection_type} Column Step 3 web local yielding",
            clause="Chapter 6 / Section 6.7.2 Step 3 Eq. 6.7-16/6.7-17",
            page="9.2-38",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step3_web_local_yielding,
        ),
        _bind(
            rule_id=f"AISC358.06.7.2.{connection_type}.step4_column_web_local_crippling",
            name=f"{connection_type} Column Step 4 web local crippling",
            clause="Chapter 6 / Section 6.7.2 Step 4 Eq. 6.7-18 to 6.7-21",
            page="9.2-38 to 9.2-39",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step4_web_local_crippling,
        ),
        _bind(
            rule_id=f"AISC358.06.7.2.{connection_type}.step5_continuity_plate_strength",
            name=f"{connection_type} Column Step 5 continuity plate strength",
            clause="Chapter 6 / Section 6.7.2 Step 5 Eq. 6.7-22",
            page="9.2-39",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step5_continuity_plate_strength,
        ),
        _bind(
            rule_id=f"AISC358.06.7.2.{connection_type}.step6_panel_zone",
            name=f"{connection_type} Column Step 6 panel zone",
            clause="Chapter 6 / Section 6.7.2 Step 6 + Section 2.7",
            page="9.2-39",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step6_panel_zone,
        ),
        _bind(
            rule_id=f"AISC358.06.7.2.{connection_type}.step7_column_beam_moment_ratio",
            name=f"{connection_type} Column Step 7 column-beam moment ratio",
            clause="Chapter 6 / Section 6.7.2 Step 7 + Section 2.8",
            page="9.2-39 to 9.2-10",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step7_column_beam_moment_ratio,
        ),
    ]


def _chapter6_4e_specific_steps() -> list[RuleBinding]:
    return [
        _bind(
            rule_id="AISC358.06.6.1.bueep_4e_bolt_gage_limit",
            name="BUEEP 4E bolt gage limit",
            clause="Chapter 6 / Section 6.6.1",
            page="9.2-24 to 9.2-25",
            connection_type="bueep_4e",
            evaluator=chapter_06_end_plate.run_bolt_gage_limit,
        ),
        _bind(
            rule_id="AISC358.06.7.1.bueep_4e.step11_end_plate_shear_yielding",
            name="BUEEP 4E Step 11 end-plate shear yielding",
            clause="Chapter 6 / Section 6.7.1 Step 11 Eq. 6.7-7",
            page="9.2-30",
            connection_type="bueep_4e",
            evaluator=chapter_06_end_plate.run_end_plate_shear_yielding_4e,
        ),
        _bind(
            rule_id="AISC358.06.7.1.bueep_4e.step12_end_plate_shear_rupture",
            name="BUEEP 4E Step 12 end-plate shear rupture",
            clause="Chapter 6 / Section 6.7.1 Step 12 Eq. 6.7-8",
            page="9.2-34",
            connection_type="bueep_4e",
            evaluator=chapter_06_end_plate.run_end_plate_shear_rupture_4e,
        ),
    ]


def _chapter6_stiffened_specific_steps(connection_type: str) -> list[RuleBinding]:
    return [
        _bind(
            rule_id=f"AISC358.06.6.1.{connection_type}_bolt_gage_limit",
            name=f"{connection_type.upper()} bolt gage limit",
            clause="Chapter 6 / Section 6.6.1",
            page="9.2-24 to 9.2-25",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_bolt_gage_limit,
        ),
        _bind(
            rule_id=f"AISC358.06.6.4.{connection_type}_stiffener_minimum_length",
            name=f"{connection_type.upper()} stiffener minimum length",
            clause="Chapter 6 / Section 6.6.4 Eq. 6.6-1",
            page="9.2-27",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_stiffener_minimum_length,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step13_stiffener_thickness",
            name=f"{connection_type.upper()} Step 13 stiffener thickness",
            clause="Chapter 6 / Section 6.7.1 Step 13 Eq. 6.7-9",
            page="9.2-34",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_stiffener_thickness,
        ),
        _bind(
            rule_id=f"AISC358.06.7.1.{connection_type}.step13_stiffener_local_buckling",
            name=f"{connection_type.upper()} Step 13 stiffener local buckling",
            clause="Chapter 6 / Section 6.7.1 Step 13 Eq. 6.7-10",
            page="9.2-34",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_stiffener_local_buckling,
        ),
    ]


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
