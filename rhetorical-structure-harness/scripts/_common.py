"""Shared helpers for the rhetorical-structure-harness checkers.

Only the content inside explicit comment markers is parsed, so the prose
around the machine-readable tables can be written freely.
"""

from __future__ import annotations

import re
from pathlib import Path

HAN_RE = re.compile(r"[\u4e00-\u9fff]")
TRACE_RE = re.compile(
    r"https?://|\[E:[^\]]+\]|\[断言\]|\S+\.(?:md|csv|json|txt|tsv|xlsx|pdf|docx)"
)

MOVE_KINDS = [
    "anchor",
    "turn",
    "mechanism",
    "evidence",
    "limit",
    "disclaimer",
    "stake",
    "frame",
    "restate",
    "call",
]

# R3: RST allows several Evidence satellites in a row; other kinds do not repeat.
MAX_RUN = {"evidence": 3}
DEFAULT_MAX_RUN = 1


def han(text: str) -> int:
    return len(HAN_RE.findall(text or ""))


def marker_block(text: str, tag: str):
    """Return the raw content between <!-- TAG:BEGIN --> and <!-- TAG:END -->."""
    pattern = re.compile(
        r"<!--\s*" + re.escape(tag) + r":BEGIN\s*-->(.*?)<!--\s*" + re.escape(tag) + r":END\s*-->",
        re.S,
    )
    match = pattern.search(text or "")
    return match.group(1) if match else None


def table(block: str):
    """Parse a pipe-delimited table into a list of rows (each a list of cells).

    The first row is treated as the header by the callers. Blank lines and
    nested comments are ignored.
    """
    rows = []
    for line in (block or "").splitlines():
        line = line.strip()
        if not line or line.startswith("<!--") or line.startswith("#"):
            continue
        rows.append([cell.strip() for cell in line.split("|")])
    return rows


def header_values(block: str):
    """Return (names, values) for a two-row header table, else (names, None)."""
    rows = table(block)
    if not rows:
        return [], None
    return rows[0], (rows[1] if len(rows) > 1 else None)


def section_table(block: str):
    """Return (names, data_rows) for a header + data-row table."""
    rows = table(block)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def max_run(kinds, kind: str) -> int:
    """Longest run of consecutive identical kinds."""
    best = current = 0
    for item in kinds:
        current = current + 1 if item == kind else 0
        best = max(best, current)
    return best


def read(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_evidence_register(root: Path):
    """Optional evidence/register.csv with columns: id,source,boundary.

    R1: oral scripts keep sourcing in an appendix, so traceability may live in
    this register instead of inline in the spoken text.
    """
    path = Path(root) / "evidence" / "register.csv"
    if not path.exists():
        return None
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cells = [c.strip() for c in line.split(",")]
        if cells and cells[0].lower() == "id":
            continue
        if cells:
            rows.append(cells)
    return rows or None


def find_architecture(root: Path) -> Path:
    return Path(root) / "architecture.md"


def load_architecture(root: Path):
    """Parse architecture.md into (header, sections) or (None, None)."""
    path = find_architecture(root)
    if not path.exists():
        return None, None
    text = read(path)
    hb = marker_block(text, "ARCH:HEADER")
    sb = marker_block(text, "ARCH:SECTIONS")
    names, values = header_values(hb) if hb else ([], None)
    header = dict(zip(names, values)) if values else None
    _, rows = section_table(sb) if sb else ([], [])
    sections = []
    for row in rows:
        sections.append(
            dict(
                zip(
                    ["id", "title", "job", "from", "to", "material", "turn", "handoff", "budget_chars"],
                    row,
                )
            )
        )
    return header, sections


def parse_section_file(path: Path):
    text = read(path)
    sb = marker_block(text, "SECTION")
    mb = marker_block(text, "MOVES")
    names, srows = section_table(sb) if sb else ([], [])
    if not srows:
        return None, None
    sinfo = dict(zip(names, srows[0]))
    sinfo.setdefault("type", "argument")
    _, mrows = section_table(mb) if mb else ([], [])
    moves = [
        {"kind": r[0], "text": r[1] if len(r) > 1 else ""}
        for r in mrows
        if r and r[0]
    ]
    return sinfo, moves


class Checker:
    """Collect failures and warnings, print a report, expose an exit code."""

    def __init__(self, title: str):
        self.title = title
        self.failures = []
        self.warnings = []
        self.notes = []

    def need(self, condition, message):
        if not condition:
            self.failures.append(message)
        return bool(condition)

    def warn(self, condition, message):
        if not condition:
            self.warnings.append(message)
        return bool(condition)

    def note(self, message):
        self.notes.append(message)

    def report(self):
        print(f"# {self.title}")
        for note in self.notes:
            print(f"  note: {note}")
        for warning in self.warnings:
            print(f"  WARN: {warning}")
        if self.failures:
            print("FAIL")
            for failure in self.failures:
                print(f"  - {failure}")
            return 1
        print("PASS")
        return 0
