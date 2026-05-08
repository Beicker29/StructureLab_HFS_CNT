from __future__ import annotations

import math
from typing import Any


def compute_plate_combined_force_interaction(
    *,
    dcr_plt_m1_web: float,
    dcr_plt_v3_web: float,
    dcr_plt_v2_web: float,
    dcr_plt_p3_minus_web: float,
) -> dict[str, Any]:
    """Compute combined-force interaction checks for web splice plate.

    Case 1:
        DCR_case1 = DCR_plt_m1_web + (DCR_plt_v3_web)^2 + (DCR_plt_v2_web)^4
    Case 2:
        DCR_case2 = DCR_plt_m1_web + (DCR_plt_p3(-)_web)^2 + (DCR_plt_v2_web)^4
    Governing:
        DCR_plt_Fcomb_web = max(DCR_case1, DCR_case2)
    """

    values = {
        "dcr_plt_m1_web": float(dcr_plt_m1_web),
        "dcr_plt_v3_web": float(dcr_plt_v3_web),
        "dcr_plt_v2_web": float(dcr_plt_v2_web),
        "dcr_plt_p3_minus_web": float(dcr_plt_p3_minus_web),
    }
    for key, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{key} must be a finite float.")
        if value < 0.0:
            raise ValueError(f"{key} must be >= 0.0.")

    dcr_case_1 = values["dcr_plt_m1_web"] + (values["dcr_plt_v3_web"] ** 2.0) + (values["dcr_plt_v2_web"] ** 4.0)
    dcr_case_2 = (
        values["dcr_plt_m1_web"] + (values["dcr_plt_p3_minus_web"] ** 2.0) + (values["dcr_plt_v2_web"] ** 4.0)
    )
    dcr_fcomb = max(dcr_case_1, dcr_case_2)
    controlling_case = "Caso 1" if dcr_case_1 >= dcr_case_2 else "Caso 2"

    return {
        "dcr_case_1": dcr_case_1,
        "dcr_case_2": dcr_case_2,
        "dcr_fcomb": dcr_fcomb,
        "controlling_case": controlling_case,
        "passes": dcr_fcomb <= 1.0,
        "equation_case_1": "DCR_case_1 = DCR_plt_m1_web + (DCR_plt_v3_web)^2 + (DCR_plt_v2_web)^4",
        "equation_case_2": "DCR_case_2 = DCR_plt_m1_web + (DCR_plt_p3(-)_web)^2 + (DCR_plt_v2_web)^4",
        "equation_governing": "DCR_plt_Fcomb_web = max(DCR_case_1, DCR_case_2)",
    }


def compute_member_combined_interaction_h11(
    *,
    pr_over_pc: float,
    mrx_over_mcx: float,
    mry_over_mcy: float = 0.0,
) -> dict[str, Any]:
    """Compute AISC 360-22 H1 interaction for axial + flexure members.

    H1-1a (when Pr/Pc >= 0.2):
        DCR = Pr/Pc + (8/9) * (Mrx/Mcx + Mry/Mcy)

    H1-1b (when Pr/Pc < 0.2):
        DCR = Pr/(2*Pc) + (Mrx/Mcx + Mry/Mcy)
    """

    values = {
        "pr_over_pc": float(pr_over_pc),
        "mrx_over_mcx": float(mrx_over_mcx),
        "mry_over_mcy": float(mry_over_mcy),
    }
    for key, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{key} must be a finite float.")
    for key in ("mrx_over_mcx", "mry_over_mcy"):
        if values[key] < 0.0:
            raise ValueError(f"{key} must be >= 0.0.")

    sum_m = values["mrx_over_mcx"] + values["mry_over_mcy"]
    if values["pr_over_pc"] >= 0.2:
        dcr = values["pr_over_pc"] + (8.0 / 9.0) * sum_m
        equation = "H1-1a"
    else:
        dcr = (values["pr_over_pc"] / 2.0) + sum_m
        equation = "H1-1b"

    return {
        "pr_over_pc": values["pr_over_pc"],
        "mrx_over_mcx": values["mrx_over_mcx"],
        "mry_over_mcy": values["mry_over_mcy"],
        "dcr": dcr,
        "equation_used": equation,
        "passes": dcr <= 1.0,
        "equation_h11a": "DCR = Pr/Pc + (8/9)*(Mrx/Mcx + Mry/Mcy)",
        "equation_h11b": "DCR = Pr/(2*Pc) + (Mrx/Mcx + Mry/Mcy)",
    }
