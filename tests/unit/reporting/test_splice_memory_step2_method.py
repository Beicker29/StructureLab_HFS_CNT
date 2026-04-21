from __future__ import annotations

import json
from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_payload
from steel_connections.domain.rules.aisc360 import bbmb_splice_methods
from steel_connections.reporting.markdown_writer import render_memory_markdown


EXAMPLE_SPLICE_PATH = Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json")


def _solved_stub() -> dict:
    return {
        "results": {
            "Elastic Method - Superposition": {
                "Bolt Demand": 9.0,
                "Bolt Capacity": 20.0,
                "DCR": 0.45,
            },
            "Elastic Method - Center of Rotation": {
                "Connection Demand": 11.0,
                "Connection Capacity": 20.0,
                "DCR": 0.55,
            },
            "Instant Center of Rotation Method": {
                "Connection Demand": 13.0,
                "Connection Capacity": 20.0,
                "DCR": 0.65,
                "Cu": 5.9,
            },
        },
        "residual": [0.005],
        "n_iterations": 1,
        "final_residual": 0.005,
    }


def test_splice_memory_includes_step2_method_block(monkeypatch) -> None:
    payload = json.loads(EXAMPLE_SPLICE_PATH.read_text(encoding="utf-8"))
    payload.setdefault("procedure", {}).setdefault("icr", {})
    payload["procedure"]["icr"]["method"] = "Elastic Method - Superposition"

    monkeypatch.setattr(
        bbmb_splice_methods,
        "solve_bolt_group_with_ezbolt",
        lambda **_: _solved_stub(),
    )
    result = run_case_payload(payload)
    memory = render_memory_markdown(result)
    assert "### Punto 2 - Metodo ICR/Elastic" in memory
    assert "Metodo seleccionado: `elastic_superposition`" in memory
    assert "Picr comparativo" in memory
