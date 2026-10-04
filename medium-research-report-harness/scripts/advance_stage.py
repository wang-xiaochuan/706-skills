#!/usr/bin/env python3
"""Advance the single ACTIVE stage after its handoff explicitly records PASS."""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--handoff", required=True, help="Relative handoff path for the ACTIVE stage")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_rows_atomic(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    descriptor, temp_name = tempfile.mkstemp(prefix="state-", suffix=".csv", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    state_path = root / "state.csv"
    if not state_path.is_file():
        print("ADVANCE_STAGE: FAIL — state.csv missing", file=sys.stderr)
        return 1

    try:
        rows, fields = read_rows(state_path)
    except (OSError, csv.Error) as exc:
        print(f"ADVANCE_STAGE: FAIL — {exc}", file=sys.stderr)
        return 1

    active = [index for index, row in enumerate(rows) if row.get("status") == "ACTIVE"]
    if len(active) != 1:
        print(f"ADVANCE_STAGE: FAIL — expected one ACTIVE stage, found {len(active)}", file=sys.stderr)
        return 1

    index = active[0]
    if any(row.get("status") != "PASSED" for row in rows[:index]):
        print("ADVANCE_STAGE: FAIL — every stage before ACTIVE must be PASSED", file=sys.stderr)
        return 1
    if any(row.get("status") != "LOCKED" for row in rows[index + 1 :]):
        print("ADVANCE_STAGE: FAIL — every stage after ACTIVE must be LOCKED", file=sys.stderr)
        return 1

    expected_rel = rows[index].get("handoff_path", "")
    supplied = Path(args.handoff)
    if supplied.is_absolute() or ".." in supplied.parts:
        print("ADVANCE_STAGE: FAIL — handoff must be a safe relative path", file=sys.stderr)
        return 1
    if supplied.as_posix() != expected_rel:
        print(f"ADVANCE_STAGE: FAIL — expected handoff {expected_rel}", file=sys.stderr)
        return 1

    handoff = root / supplied
    if not handoff.is_file():
        print(f"ADVANCE_STAGE: FAIL — handoff missing: {supplied}", file=sys.stderr)
        return 1
    text = handoff.read_text(encoding="utf-8")
    if not re.search(r"^Status:\s*PASS\s*$", text, flags=re.IGNORECASE | re.MULTILINE):
        print(f"ADVANCE_STAGE: FAIL — {supplied} does not contain an exact 'Status: PASS' line", file=sys.stderr)
        return 1

    rows[index]["status"] = "PASSED"
    next_stage = "complete"
    if index + 1 < len(rows):
        if rows[index + 1].get("status") != "LOCKED":
            print("ADVANCE_STAGE: FAIL — next stage is not LOCKED", file=sys.stderr)
            return 1
        rows[index + 1]["status"] = "ACTIVE"
        next_stage = f"{rows[index + 1]['stage_id']}-{rows[index + 1]['stage_name']}"

    if args.dry_run:
        print(f"ADVANCE_STAGE: DRY-RUN — next={next_stage}")
        return 0

    try:
        write_rows_atomic(state_path, rows, fields)
    except OSError as exc:
        print(f"ADVANCE_STAGE: FAIL — {exc}", file=sys.stderr)
        return 1
    print(f"ADVANCE_STAGE: PASS — next={next_stage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
