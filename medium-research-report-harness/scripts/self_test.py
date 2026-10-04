#!/usr/bin/env python3
"""Deterministic smoke test for initialization, validation, advancement, and corruption detection."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != expect:
        raise RuntimeError(
            f"command returned {result.returncode}, expected {expect}: {' '.join(args)}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="medium-research-harness-") as temp:
        root = Path(temp) / "sample-report"
        run(
            sys.executable,
            str(HERE / "init_harness.py"),
            "--root",
            str(root),
            "--title",
            "Sample Medium Research Report",
            "--slug",
            "sample-medium-report",
            "--mode",
            "continuous",
            "--primary-language",
            "zh-CN",
            "--audience",
            "international project partners",
        )
        run(sys.executable, str(HERE / "check_harness.py"), str(root))

        handoff = root / "stages/00-scope/handoff.md"
        handoff.write_text(handoff.read_text(encoding="utf-8").replace("Status: PENDING", "Status: PASS"), encoding="utf-8")
        run(
            sys.executable,
            str(HERE / "advance_stage.py"),
            str(root),
            "--handoff",
            "stages/00-scope/handoff.md",
        )
        run(sys.executable, str(HERE / "check_harness.py"), str(root))

        state_path = root / "state.csv"
        with state_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
            fields = list(rows[0].keys())
        rows[2]["status"] = "ACTIVE"
        with state_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        result = run(sys.executable, str(HERE / "check_harness.py"), str(root), expect=1)
        if "expected exactly one ACTIVE stage" not in result.stderr:
            raise RuntimeError("validator did not report the expected multiple-ACTIVE failure")

    print("SELF_TEST: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
