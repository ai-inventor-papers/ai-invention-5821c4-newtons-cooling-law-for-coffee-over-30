#!/usr/bin/env python3
"""Entry point: runs the full pipeline in order and writes results/ and figures/.

Equivalent to ./run_all.sh. Uses the workspace's own .venv interpreter when present,
otherwise the interpreter running this file.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    "src/digitize_figures.py",
    "src/paper_curves.py",
    "src/analysis.py",
    "src/run_tests.py",
    "src/make_figures.py",
    "src/write_method_out.py",
    "src/format_outputs.py",
    "src/audit_headline_numbers.py",
]


def main() -> None:
    venv_python = ROOT / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable
    for step in STEPS:
        print(f"== {step}", flush=True)
        subprocess.run([python, "-W", "ignore", str(ROOT / step)], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
