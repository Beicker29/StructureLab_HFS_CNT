from __future__ import annotations

import json
from pathlib import Path

from steel_connections.domain.engine.validate import parse_and_validate_payload


EXAMPLE_SPLICE_PATH = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")


def test_parse_splice_payload_with_official_naming() -> None:
    payload = json.loads(EXAMPLE_SPLICE_PATH.read_text(encoding="utf-8"))
    case = parse_and_validate_payload(payload)
    assert case.sections.shape_vg == "W18X35"
    assert case.geometry.gap_sp.value > 0.0
    assert case.geometry.n_blt_web_x >= 1
    assert case.materials.shape_blt_web
