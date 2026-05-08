from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow "python -m src.steel_connections.run ..." without external PYTHONPATH setup.
SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.models.output import GlobalStatus
from steel_connections.reporting.json_writer import write_detailed_result
from steel_connections.reporting.markdown_writer import (
    write_memory_markdown,
    write_splice_methods_table_markdown,
    write_splice_methods_table_markdown_flange,
)


def _print_errors_to_terminal(result) -> None:
    if not result.errors:
        return
    print("ERRORS:")
    for idx, error in enumerate(result.errors, start=1):
        print(f"  [{idx}] code={error.error_code.value} stage={error.stage.value}")
        if error.rule_id:
            print(f"      rule_id: {error.rule_id}")
        if error.source_document:
            print(f"      source: {error.source_document}")
        if error.missing_fields:
            print(f"      missing_fields: {', '.join(error.missing_fields)}")
        print(f"      message: {error.message}")


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


def _derive_example_id(input_path: Path) -> str:
    parts = list(input_path.parts)
    for idx, part in enumerate(parts):
        if part.lower() == "examples":
            rel = Path(*parts[idx + 1 :]).with_suffix("")
            return rel.as_posix()
    return input_path.stem


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    example_id = _derive_example_id(input_path)

    result = run_case_file(str(input_path))
    output_path = write_detailed_result(result, args.out, example_id=example_id)
    memory_path = write_memory_markdown(result, output_path.parent)
    splice_table_path = write_splice_methods_table_markdown(result, output_path.parent)
    splice_table_flange_path = write_splice_methods_table_markdown_flange(result, output_path.parent)

    print(f"DETAIL FILE: {output_path}")
    print(f"MEMORY FILE: {memory_path}")
    if splice_table_path is not None:
        print(f"SPLICE METHODS TABLE FILE: {splice_table_path}")
    if splice_table_flange_path is not None:
        print(f"SPLICE METHODS TABLE FLANGE FILE: {splice_table_flange_path}")
    if result.global_status == GlobalStatus.ERROR:
        _print_errors_to_terminal(result)

    if result.global_status == GlobalStatus.PASS:
        return 0
    if result.global_status == GlobalStatus.FAIL:
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
