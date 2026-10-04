#!/usr/bin/env python3
"""Initialize a talk harness instance from assets/talk-template.

Usage:
    python3 init_talk_harness.py --root /abs/path/to/talk --title "标题" --minutes 6

Refuses to overwrite a non-empty directory.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "assets" / "talk-template"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a rhetorical-structure talk harness")
    parser.add_argument("--root", required=True, help="target directory for the talk harness")
    parser.add_argument("--title", required=True, help="talk title")
    parser.add_argument("--minutes", type=float, default=6.0, help="target duration in minutes")
    parser.add_argument("--archetype", default="discovery-log", help="outline archetype")
    parser.add_argument("--wpm", type=float, default=280.0, help="speaking rate, characters per minute")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        print(f"refusing to overwrite non-empty directory: {root}", file=sys.stderr)
        return 1
    if not TEMPLATE.is_dir():
        print(f"template missing: {TEMPLATE}", file=sys.stderr)
        return 2

    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE, root, dirs_exist_ok=True)

    replacements = {
        "{{TITLE}}": args.title,
        "{{MINUTES}}": f"{args.minutes:g}",
    }
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        for key, value in replacements.items():
            text = text.replace(key, value)
        if text != original:
            path.write_text(text, encoding="utf-8")

    arch = root / "architecture.md"
    if arch.exists():
        text = arch.read_text(encoding="utf-8")
        text = text.replace("discovery-log |", f"{args.archetype} |", 1)
        text = text.replace("| 280 |", f"| {args.wpm:g} |", 1)
        if args.archetype != "discovery-log":
            text = text.replace("discovery-log |", f"{args.archetype} |", 1)
        arch.write_text(text, encoding="utf-8")

    print(f"initialized: {root}")
    print("next:")
    print(f"  1. fill brief.md (Gate 0)")
    print(f"  2. fill architecture.md sections, then: python3 {SKILL_DIR / 'scripts' / 'check_architecture.py'} {root}")
    print(f"  3. write sections/*.md, then: python3 {SKILL_DIR / 'scripts' / 'check_moves.py'} {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
