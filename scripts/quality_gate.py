from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for path in (ROOT, SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from tests.helpers.golden_compare import compare_detailed_json_files, compare_report_files


@dataclass(frozen=True)
class ApprovedCase:
    name: str
    input_path: Path
    generated_relative_dir: Path
    golden_dir: Path


APPROVED_CASES = [
    ApprovedCase(
        name="case_003_bseep_8es_split_inputs",
        input_path=Path("examples/moment_prequalified/case_003_bseep_8es_split_inputs"),
        generated_relative_dir=Path("moment_prequalified/case_003_bseep_8es_split_inputs"),
        golden_dir=Path("tests/golden/approved/case_003_bseep_8es_split_inputs"),
    ),
    ApprovedCase(
        name="case_001_bbmb_splice",
        input_path=Path("examples/Fully Restrained Moment/case_001_bbmb_splice.json"),
        generated_relative_dir=Path("Fully Restrained Moment/case_001_bbmb_splice"),
        golden_dir=Path("tests/golden/approved/case_001_bbmb_splice"),
    ),
]


def _run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"> {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, text=True)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed


def _prepare_temp_root() -> Path:
    temp_root = ROOT / ".tmp_quality_gate" / "approved"
    workspace_root = ROOT.resolve()
    resolved_temp = temp_root.resolve()
    if workspace_root not in (resolved_temp, *resolved_temp.parents):
        raise RuntimeError(f"Refusing to delete path outside repo: {resolved_temp}")
    if temp_root.exists():
        shutil.rmtree(temp_root)
    temp_root.mkdir(parents=True, exist_ok=True)
    return temp_root


def _generate_case(case: ApprovedCase, output_root: Path) -> Path:
    completed = _run(
        [
            sys.executable,
            "-m",
            "src.steel_connections.run",
            str(case.input_path),
            str(output_root),
        ],
        check=False,
    )
    generated_dir = output_root / case.generated_relative_dir
    if not (generated_dir / "detailed.json").exists() or not (generated_dir / "memory.md").exists():
        raise SystemExit(
            f"Generation failed for {case.name}; exit={completed.returncode}; missing expected artifacts."
        )
    return generated_dir


def _compare_case(case: ApprovedCase, generated_dir: Path) -> None:
    golden_dir = ROOT / case.golden_dir
    compare_detailed_json_files(generated_dir / "detailed.json", golden_dir / "detailed.json")
    compare_report_files(generated_dir / "memory.md", golden_dir / "memory.md")
    print(f"golden approved OK: {case.name}", flush=True)


def main() -> int:
    _run([sys.executable, "-m", "pytest", "-q"])
    output_root = _prepare_temp_root()
    for case in APPROVED_CASES:
        generated_dir = _generate_case(case, output_root)
        _compare_case(case, generated_dir)
    print("quality gate OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
