from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow "python -m src.steel_connections.run ..." without external PYTHONPATH setup.
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.domain.engine.validate import parse_and_validate_file
from steel_connections.models.errors import StructuredEngineException
from steel_connections.models.output import GlobalStatus
from steel_connections.reporting.json_writer import write_detailed_result
from steel_connections.reporting.geometry_artifact import write_connection_geometry_artifact
from steel_connections.reporting.terminal import render_terminal_summary


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.steel_connections.run",
        description="Run a steel connection case from a JSON input file.",
    )
    parser.add_argument("input", help="Path to case JSON file.")
    parser.add_argument(
        "out",
        nargs="?",
        default="results",
        help="Output root directory. Defaults to 'results'.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    example_id = input_path.stem

    result = run_case_file(str(input_path))
    output_path = write_detailed_result(result, args.out, example_id=example_id)
    try:
        case = parse_and_validate_file(str(input_path))
    except StructuredEngineException:
        case = None
    geometry_path = write_connection_geometry_artifact(case, output_path.parent) if case is not None else None

    print(render_terminal_summary(result))
    print(f"DETAIL FILE: {output_path}")
    if geometry_path is not None:
        print(f"GEOMETRY FILE: {geometry_path}")

    if result.global_status == GlobalStatus.PASS:
        return 0
    if result.global_status == GlobalStatus.FAIL:
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
