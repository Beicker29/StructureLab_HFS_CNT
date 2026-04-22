from __future__ import annotations

import argparse
import sys
from pathlib import Path

from steel_connections.domain.engine.pipeline import run_case_file
from steel_connections.models.output import GlobalStatus
from steel_connections.reporting.json_writer import write_detailed_result
from steel_connections.reporting.markdown_writer import write_memory_markdown


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="steel-connections",
        description="Deterministic and auditable steel connection design engine.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate input JSON.")
    validate_parser.add_argument("--input", required=True, help="Path to input JSON.")

    run_parser = subparsers.add_parser("run", help="Run applicable checks.")
    run_parser.add_argument("--input", required=True, help="Path to input JSON.")
    run_parser.add_argument(
        "--out",
        required=False,
        default="results",
        help="Output root for detailed JSON results (default: results).",
    )
    return parser


def _run_validate(input_path: str) -> int:
    from steel_connections.domain.engine.validate import parse_and_validate_file

    parse_and_validate_file(input_path)
    print(f"VALIDATION: PASS ({input_path})")
    return 0


def _derive_example_id(input_path: Path) -> str:
    parts = list(input_path.parts)
    for idx, part in enumerate(parts):
        if part.lower() == "examples":
            rel = Path(*parts[idx + 1 :]).with_suffix("")
            return rel.as_posix()
    return input_path.stem


def _run_case(input_path: str, out_root: str) -> int:
    result = run_case_file(input_path)
    example_id = _derive_example_id(Path(input_path))
    output_path = write_detailed_result(result, out_root, example_id=example_id)
    memory_path = write_memory_markdown(result, output_path.parent)
    print(f"DETAIL FILE: {output_path}")
    print(f"MEMORY FILE: {memory_path}")

    if result.global_status == GlobalStatus.PASS:
        return 0
    if result.global_status == GlobalStatus.FAIL:
        return 2
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return _run_validate(args.input)
    if args.command == "run":
        return _run_case(args.input, args.out)

    parser.error("Unknown command.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
