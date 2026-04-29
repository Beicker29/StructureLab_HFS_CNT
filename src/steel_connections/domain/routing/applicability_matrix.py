from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from steel_connections.domain.rules.aisc358 import beam_flange_tension, chapter_06_end_plate, flange_weld_strength
from steel_connections.domain.rules.aisc360 import bbmb_splice_detailing, bbmb_splice_methods
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
    common: list[RuleBinding] = [
        _bind(
            rule_id=f"AISC358.06.3.{connection_type}.prequalification_limits",
            name=f"{connection_type} Section 6.3 prequalification limits",
            clause="Chapter 6 / Section 6.3 + AISC 360-22 Table J3.4",
            page="9.2-24 to 9.2-25",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_section63_prequalification_limits,
        ),
        _bind(
            rule_id=f"AISC358.06.7.{connection_type}.step2_probable_moment_plastic_hinge",
            name=f"{connection_type} Step 2 probable maximum moment at plastic hinge",
            clause="Chapter 6 / Section 6.7.1 Step 2 + Eq. (2.4-1) and Eq. (2.4-2)",
            page="9.2-24",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step1_probable_moment_plastic_hinge,
        ),
        _bind(
            rule_id=f"AISC358.06.7.{connection_type}.step3_plastic_hinge_distance",
            name=f"{connection_type} Step 3 plastic hinge distance from column face",
            clause="Chapter 6 / Section 6.7.1 Step 3 + Eq. (6.7-1) and Eq. (6.7-2)",
            page="9.2-24",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step2_plastic_hinge_distance,
        ),
        _bind(
            rule_id=f"AISC358.06.7.{connection_type}.step4_shear_at_plastic_hinge",
            name=f"{connection_type} Step 4 shear force at plastic hinge",
            clause="Chapter 6 / Section 6.7.1 Step 4 + Eq. (2.4-3)",
            page="9.2-24",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step3_shear_at_plastic_hinge,
        ),
        _bind(
            rule_id=f"AISC358.06.7.{connection_type}.step5_probable_moment_face_column",
            name=f"{connection_type} Step 5 probable maximum moment at face of column",
            clause="Chapter 6 / Section 6.7.1 Step 5 + Eq. (2.4-4)",
            page="9.2-24",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_step4_probable_moment_face_column,
        ),
        _bind(
            rule_id=f"AISC358.06.7.{connection_type}.step21_5_1_column_panel_zone_shear_wpzs_col",
            name=f"{connection_type} Step 21.5.1 column panel-zone web shear (WPZS)",
            clause="AISC 360-22w Section J10.6 + Eq. (J10-9) to Eq. (J10-12)",
            page="16.1-120",
            connection_type=connection_type,
            evaluator=chapter_06_end_plate.run_column_step5_panel_zone_shear_wpzs,
            source_document="AISC 360-22w",
        ),
    ]
    for side_suffix, side_label, eval_6_1, eval_6_2, eval_7_1_1, eval_7_2_1, eval_7_2_2, eval_7_3_1, eval_7_3_2, eval_12, eval_13, eval_14_2_1, eval_14_2_2 in (
        (
            "vgizq",
            "left",
            chapter_06_end_plate.run_step6_1_bolt_tension_rupture_vgizq,
            chapter_06_end_plate.run_step6_2_bolt_shear_rupture_vgizq,
            chapter_06_end_plate.run_step7_1_1_end_plate_flexural_yielding_vgizq,
            chapter_06_end_plate.run_step7_2_1_end_plate_shear_yielding_vgizq,
            chapter_06_end_plate.run_step7_2_2_end_plate_shear_rupture_vgizq,
            chapter_06_end_plate.run_step7_3_1_end_plate_hole_tearout_vgizq,
            chapter_06_end_plate.run_step7_3_2_end_plate_hole_bearing_vgizq,
            chapter_06_end_plate.run_column_step1_flange_yielding_vgizq,
            chapter_06_end_plate.run_column_step3_web_local_yielding_vgizq,
            chapter_06_end_plate.run_column_step4_web_local_crippling_vgizq,
            chapter_06_end_plate.run_column_step4_2_web_local_buckling_vgizq,
        ),
        (
            "vgder",
            "right",
            chapter_06_end_plate.run_step6_1_bolt_tension_rupture_vgder,
            chapter_06_end_plate.run_step6_2_bolt_shear_rupture_vgder,
            chapter_06_end_plate.run_step7_1_1_end_plate_flexural_yielding_vgder,
            chapter_06_end_plate.run_step7_2_1_end_plate_shear_yielding_vgder,
            chapter_06_end_plate.run_step7_2_2_end_plate_shear_rupture_vgder,
            chapter_06_end_plate.run_step7_3_1_end_plate_hole_tearout_vgder,
            chapter_06_end_plate.run_step7_3_2_end_plate_hole_bearing_vgder,
            chapter_06_end_plate.run_column_step1_flange_yielding_vgder,
            chapter_06_end_plate.run_column_step3_web_local_yielding_vgder,
            chapter_06_end_plate.run_column_step4_web_local_crippling_vgder,
            chapter_06_end_plate.run_column_step4_2_web_local_buckling_vgder,
        ),
    ):
        common.extend(
            [
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step6_1_bolt_tension_rupture_{side_suffix}",
                    name=f"{connection_type} Step 6.1 bolt tension rupture capacity ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 6.1 + AISC 360-22 J3.7",
                    page="9.2-24",
                    connection_type=connection_type,
                    evaluator=eval_6_1,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step6_2_bolt_shear_rupture_{side_suffix}",
                    name=f"{connection_type} Step 6.2 bolt shear rupture capacity ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 6.2 + AISC 360-22 J3.7",
                    page="9.2-24",
                    connection_type=connection_type,
                    evaluator=eval_6_2,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step7_1_1_end_plate_flexural_yielding_{side_suffix}",
                    name=f"{connection_type} Step 7.1.1 end-plate flexural yielding ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 7.1.1 + Eq. (6.7-8)",
                    page="9.2-24",
                    connection_type=connection_type,
                    evaluator=eval_7_1_1,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step7_2_1_end_plate_shear_yielding_{side_suffix}",
                    name=f"{connection_type} Step 7.2.1 end-plate shear yielding ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 7.2.1 + Eq. (6.7-10)",
                    page="9.2-24",
                    connection_type=connection_type,
                    evaluator=eval_7_2_1,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step7_2_2_end_plate_shear_rupture_{side_suffix}",
                    name=f"{connection_type} Step 7.2.2 end-plate shear rupture ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 7.2.2 + Eq. (6.7-12)",
                    page="9.2-24",
                    connection_type=connection_type,
                    evaluator=eval_7_2_2,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step7_3_1_end_plate_hole_tearout_{side_suffix}",
                    name=f"{connection_type} Step 7.3.1 end-plate hole tearout ({side_label})",
                    clause="Chapter 6 / Section 7.3.1 + AISC 360-22 J3.11(a)",
                    page="16.1-113",
                    connection_type=connection_type,
                    evaluator=eval_7_3_1,
                    source_document="AISC 360-22",
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step7_3_2_end_plate_hole_bearing_{side_suffix}",
                    name=f"{connection_type} Step 7.3.2 end-plate hole bearing ({side_label})",
                    clause="Chapter 6 / Section 7.3.2 + AISC 360-22 J3.11(a)",
                    page="16.1-113",
                    connection_type=connection_type,
                    evaluator=eval_7_3_2,
                    source_document="AISC 360-22",
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step12_1_1_column_flange_local_bending_{side_suffix}",
                    name=f"{connection_type} Step 12.1.1 column flange local bending (LFB) ({side_label})",
                    clause="Chapter 6 / Section 6.7.2 + Eq. (6.7-13)",
                    page="9.2-25",
                    connection_type=connection_type,
                    evaluator=eval_12,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step13_1_1_column_web_local_yielding_{side_suffix}",
                    name=f"{connection_type} Step 13.1.1 column web local yielding (WLY) ({side_label})",
                    clause="Chapter 6 / Section 6.7.2 + Eq. (6.7-17)",
                    page="9.2-25",
                    connection_type=connection_type,
                    evaluator=eval_13,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step14_2_1_column_web_local_crippling_{side_suffix}",
                    name=f"{connection_type} Step 14.2.1 column web local crippling (WLC) ({side_label})",
                    clause="Chapter 6 / Section 6.7.2 + Eq. (6.7-19) to Eq. (6.7-21)",
                    page="9.2-25",
                    connection_type=connection_type,
                    evaluator=eval_14_2_1,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step14_2_2_column_web_local_buckling_{side_suffix}",
                    name=f"{connection_type} Step 14.2.2 column web local buckling (WCB) ({side_label})",
                    clause="Chapter 6 / Section 6.7.2 + Eq. (6.7-18)",
                    page="9.2-25",
                    connection_type=connection_type,
                    evaluator=eval_14_2_2,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step11_1_1_beam_web_end_plate_weld_tension_rupture_{side_suffix}",
                    name=f"{connection_type} Step 11.1.1 beam web-to-end-plate weld tension rupture ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 + AISC 360-22 J2.4",
                    page="16.1-66",
                    connection_type=connection_type,
                    evaluator=(
                        chapter_06_end_plate.run_step11_1_1_beam_web_end_plate_weld_tension_rupture_vgizq
                        if side_suffix == "vgizq"
                        else chapter_06_end_plate.run_step11_1_1_beam_web_end_plate_weld_tension_rupture_vgder
                    ),
                    source_document="AISC 360-22",
                ),
            ]
        )
    return common


def _chapter6_4e_specific_steps() -> list[RuleBinding]:
    return []


def _chapter6_stiffened_specific_steps(connection_type: str) -> list[RuleBinding]:
    steps: list[RuleBinding] = []
    for side_suffix, side_label, eval_8, eval_9, eval_10, eval_11 in (
        (
            "vgizq",
            "left",
            chapter_06_end_plate.run_step8_1_1_stiffener_weld_tension_rupture_vgizq,
            chapter_06_end_plate.run_step9_1_1_stiffener_beam_weld_shear_rupture_vgizq,
            chapter_06_end_plate.run_step10_1_1_beam_flange_end_plate_weld_tension_rupture_vgizq,
            chapter_06_end_plate.run_step11_1_1_beam_shear_yielding_vgizq,
        ),
        (
            "vgder",
            "right",
            chapter_06_end_plate.run_step8_1_1_stiffener_weld_tension_rupture_vgder,
            chapter_06_end_plate.run_step9_1_1_stiffener_beam_weld_shear_rupture_vgder,
            chapter_06_end_plate.run_step10_1_1_beam_flange_end_plate_weld_tension_rupture_vgder,
            chapter_06_end_plate.run_step11_1_1_beam_shear_yielding_vgder,
        ),
    ):
        steps.extend(
            [
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step8_1_1_stiffener_weld_tension_rupture_{side_suffix}",
                    name=f"{connection_type} Step 8.1.1 stiffener weld tension rupture ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 8.1.1 + AISC 360-22 J2.4",
                    page="9.2-24",
                    connection_type=connection_type,
                    evaluator=eval_8,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step9_1_1_stiffener_beam_weld_shear_rupture_{side_suffix}",
                    name=f"{connection_type} Step 9.1.1 stiffener-beam weld shear rupture ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 9.1.1 + AISC 360-22 J2.4",
                    page="9.2-24",
                    connection_type=connection_type,
                    evaluator=eval_9,
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step10_1_1_beam_flange_end_plate_weld_tension_rupture_{side_suffix}",
                    name=f"{connection_type} Step 10.1.1 beam flange-to-end-plate weld rupture ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 10.1.1 + AISC 360-22 J2.4",
                    page="16.1-66",
                    connection_type=connection_type,
                    evaluator=eval_10,
                    source_document="AISC 360-22",
                ),
                _bind(
                    rule_id=f"AISC358.06.7.{connection_type}.step11_1_1_beam_shear_yielding_{side_suffix}",
                    name=f"{connection_type} Step 11.1.1 beam shear yielding ({side_label})",
                    clause="Chapter 6 / Section 6.7.1 Step 11.1.1 + AISC 360-22 G2.1",
                    page="16.1-77",
                    connection_type=connection_type,
                    evaluator=eval_11,
                    source_document="AISC 360-22",
                ),
            ]
        )
    return steps


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
        rule_id="AISC360.J3.bbmb_splice.step1_detailing_viga",
        name="bbmb_splice Step 1 revision geometrica de detalle - viga",
        source_document="AISC 360-22",
        clause="AISC 360-22 J3.3 / Tabla J3.4 + criterio constructivo definido por usuario",
        chapter="J3",
        page="16.1-112 to 16.1-113",
        connection_family="Fully_Restrained_Moment",
        connection_type="bbmb_splice",
        load_state="strength",
        evaluator=bbmb_splice_detailing.run_step1_viga_detailing,
    ),
    RuleBinding(
        rule_id="AISC360.J3.bbmb_splice.step2_pernos1_method",
        name="bbmb_splice Punto 2 pernos 1 metodo ICR/Elastic",
        source_document="AISC 360-22 (motor interno ICR/Elastic)",
        clause="Metodo configurable de pernos grupo 1 (ICR / Elastic)",
        chapter="J3",
        page=None,
        connection_family="Fully_Restrained_Moment",
        connection_type="bbmb_splice",
        load_state="strength",
        evaluator=bbmb_splice_methods.run_step2_pernos1_method,
    ),
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
