#!/usr/bin/env python3
"""Initialize a medium research report harness without overwriting existing work."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path


STAGES = [
    ("00", "scope", ["goal.md"]),
    ("01", "corpus", ["source/corpus-manifest.csv", "source/raw/", "source/extracted/"]),
    ("02", "evidence-map", ["source/source-register.csv", "research/claim-evidence-register.csv"]),
    ("03", "coverage", ["research/search-protocol.md", "research/coverage-matrix.csv"]),
    ("04", "structured-research", ["research/case-register.csv", "research/unknowns.csv", "research/removal-log.csv"]),
    ("05", "prewriting", ["prewriting/alignment-report.md"]),
    ("06", "architecture", ["writing/narrative-options.md", "writing/outline.md", "writing/content-conservation.csv"]),
    ("07", "primary-draft", ["writing/draft-primary.md", "writing/chapter-audit.csv"]),
    ("08", "research-audit", ["audit/research-audit.md"]),
    ("09", "narrative-audit", ["audit/narrative-audit.md", "writing/draft-primary-final.md"]),
    ("10", "visuals", ["media/images/", "media/image-register.csv"]),
    ("11", "translation", ["writing/draft-secondary.md", "writing/terminology.csv"]),
    ("12", "publication", ["publication/build/", "audit/publication-audit.md"]),
    ("13", "release", ["publication/share-package/", "publication/reader-package/", "audit/audit-summary.md"]),
]

EXTRA_DIRS = [
    "source/raw",
    "source/extracted",
    "source/web-archive",
    "prewriting",
    "writing",
    "media/images",
    "publication/build",
    "publication/share-package",
    "publication/reader-package",
    "audit",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="New or empty project directory")
    parser.add_argument("--title", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--mode", choices=["plan_only", "staged", "continuous", "revision"], default="staged")
    parser.add_argument("--primary-language", default="zh-CN")
    parser.add_argument("--audience", default="general informed readers")
    return parser.parse_args()


def validate_slug(slug: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        raise ValueError("slug must use lowercase letters, digits, and hyphens")


def replace_tokens(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".csv", ".txt"}:
            continue
        content = path.read_text(encoding="utf-8")
        for key, value in replacements.items():
            content = content.replace("{{" + key + "}}", value)
        path.write_text(content, encoding="utf-8")


def handoff_text(stage_id: str, name: str, artifacts: list[str]) -> str:
    artifacts_text = "\n".join(f"- `{item}`" for item in artifacts)
    return f"""# Stage {stage_id}: {name}\n\nStatus: PENDING\n\n## Required artifacts\n\n{artifacts_text}\n\n## Gate evidence\n\n- [待填写：运行了什么检查，结果是什么]\n\n## Handoff notes\n\n- [待填写：下阶段需要知道的事实、未知项和限制]\n"""


def initialize(args: argparse.Namespace) -> Path:
    root = args.root.expanduser().resolve()
    validate_slug(args.slug)

    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty directory: {root}")

    template = Path(__file__).resolve().parents[1] / "assets" / "project-template"
    if not template.is_dir():
        raise FileNotFoundError(f"template directory missing: {template}")

    root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, root, dirs_exist_ok=True)

    for rel in EXTRA_DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)

    for stage_id, name, artifacts in STAGES:
        stage_dir = root / "stages" / f"{stage_id}-{name}"
        stage_dir.mkdir(parents=True, exist_ok=True)
        (stage_dir / "handoff.md").write_text(handoff_text(stage_id, name, artifacts), encoding="utf-8")

    replace_tokens(
        root,
        {
            "PROJECT_TITLE": args.title,
            "PROJECT_SLUG": args.slug,
            "MODE": args.mode,
            "PRIMARY_LANGUAGE": args.primary_language,
            "AUDIENCE": args.audience,
            "DATE": date.today().isoformat(),
        },
    )
    return root


def main() -> int:
    try:
        root = initialize(parse_args())
    except (ValueError, FileExistsError, FileNotFoundError, OSError) as exc:
        print(f"INIT_HARNESS: FAIL — {exc}", file=sys.stderr)
        return 1
    print(f"INIT_HARNESS: PASS — {root}")
    print("active_stage=00-scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
