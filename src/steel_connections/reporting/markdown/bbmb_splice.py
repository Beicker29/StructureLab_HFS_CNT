from __future__ import annotations

from pathlib import Path

from steel_connections.models.results import DesignResult

from .base import render_design_result_markdown, write_design_result_markdown


def render_bbmb_splice_markdown(result: DesignResult) -> str:
    return render_design_result_markdown(result, title="Memoria BBMB splice")


def write_bbmb_splice_markdown(result: DesignResult, target_dir: str | Path) -> Path:
    return write_design_result_markdown(
        result,
        target_dir,
        filename="memory.md",
        title="Memoria BBMB splice",
    )
