#!/usr/bin/env python3
"""Validate the structure and stage-state invariants of a research harness."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


EXPECTED_STAGES = [
    ("00", "scope"),
    ("01", "corpus"),
    ("02", "evidence-map"),
    ("03", "coverage"),
    ("04", "structured-research"),
    ("05", "prewriting"),
    ("06", "architecture"),
    ("07", "primary-draft"),
    ("08", "research-audit"),
    ("09", "narrative-audit"),
    ("10", "visuals"),
    ("11", "translation"),
    ("12", "publication"),
    ("13", "release"),
]

REQUIRED_DIRS = [
    "source/raw",
    "source/extracted",
    "research",
    "prewriting",
    "writing",
    "media/images",
    "publication/build",
    "publication/share-package",
    "publication/reader-package",
    "audit",
    "stages",
]

REQUIRED_FILES = ["README.md", "goal.md", "decisions.md", "state.csv", "audit/audit-summary.md"]

CSV_HEADERS = {
    "source/corpus-manifest.csv": {"corpus_id", "filename", "source_type", "sha256", "raw_path", "derived_path"},
    "source/source-register.csv": {"source_id", "source_type", "evidence_grade", "can_support", "cannot_support"},
    "research/coverage-matrix.csv": {"coverage_id", "dimension", "unit", "query_set", "no_result_note", "status"},
    "research/claim-evidence-register.csv": {"claim_id", "claim_text", "claim_type", "source_ids", "evidence_relation", "status"},
    "research/case-register.csv": {"case_id", "name", "location", "status", "source_ids", "unknowns"},
    "research/unknowns.csv": {"unknown_id", "object_id", "question", "needed_evidence", "status"},
    "research/removal-log.csv": {"record_id", "disposition", "reason", "decided_at"},
    "writing/content-conservation.csv": {"block_id", "decision", "new_location", "verification_status"},
    "writing/chapter-audit.csv": {"chapter_id", "claim", "evidence_ids", "mechanism", "boundary", "transition_out", "status"},
    "media/image-register.csv": {"figure_id", "filename", "sha256", "claim_supported", "source_url", "internal_notes", "public_notes"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--complete", action="store_true", help="Require all stages and the overall audit to be PASS")
    return parser.parse_args()


def read_state(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate(root: Path, complete: bool = False) -> list[str]:
    errors: list[str] = []

    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            errors.append(f"missing directory: {rel}")
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing file: {rel}")

    state_path = root / "state.csv"
    if state_path.is_file():
        try:
            rows = read_state(state_path)
        except (OSError, csv.Error) as exc:
            errors.append(f"cannot read state.csv: {exc}")
            rows = []

        actual = [(row.get("stage_id", ""), row.get("stage_name", "")) for row in rows]
        if actual != EXPECTED_STAGES:
            errors.append(f"stage sequence mismatch: {actual}")

        statuses = [row.get("status", "") for row in rows]
        bad_statuses = sorted(set(statuses) - {"PASSED", "ACTIVE", "LOCKED"})
        if bad_statuses:
            errors.append(f"invalid statuses: {bad_statuses}")

        active = [i for i, status in enumerate(statuses) if status == "ACTIVE"]
        if active:
            if len(active) != 1:
                errors.append(f"expected exactly one ACTIVE stage, found {len(active)}")
            else:
                idx = active[0]
                if any(status != "PASSED" for status in statuses[:idx]):
                    errors.append("all stages before ACTIVE must be PASSED")
                if any(status != "LOCKED" for status in statuses[idx + 1 :]):
                    errors.append("all stages after ACTIVE must be LOCKED")
        elif statuses and any(status != "PASSED" for status in statuses):
            errors.append("no ACTIVE stage is allowed only when every stage is PASSED")

        for row in rows:
            handoff = row.get("handoff_path", "")
            handoff_path = Path(handoff)
            if handoff_path.is_absolute() or ".." in handoff_path.parts:
                errors.append(f"unsafe handoff path for stage {row.get('stage_id', '?')}: {handoff}")
            elif not handoff or not (root / handoff_path).is_file():
                errors.append(f"missing handoff for stage {row.get('stage_id', '?')}: {handoff}")

        if complete and statuses != ["PASSED"] * len(EXPECTED_STAGES):
            errors.append("--complete requires every stage to be PASSED")

    for rel, required in CSV_HEADERS.items():
        path = root / rel
        if not path.is_file():
            errors.append(f"missing register: {rel}")
            continue
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                header = set(next(csv.reader(handle)))
        except (OSError, StopIteration, csv.Error) as exc:
            errors.append(f"cannot read CSV header {rel}: {exc}")
            continue
        missing = sorted(required - header)
        if missing:
            errors.append(f"missing CSV fields in {rel}: {missing}")

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".csv", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if "{{" in text or "}}" in text:
            errors.append(f"unresolved template token: {path.relative_to(root)}")

    if complete:
        summary = root / "audit/audit-summary.md"
        if summary.is_file():
            content = summary.read_text(encoding="utf-8")
            if "## Overall" not in content or "`PASS`" not in content or "PENDING" in content:
                errors.append("audit/audit-summary.md does not record a complete PASS")

    return errors


def main() -> int:
    args = parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"HARNESS_CHECK: FAIL — not a directory: {root}", file=sys.stderr)
        return 1
    errors = validate(root, complete=args.complete)
    if errors:
        print(f"HARNESS_CHECK: FAIL — {len(errors)} issue(s)", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"HARNESS_CHECK: PASS — {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
