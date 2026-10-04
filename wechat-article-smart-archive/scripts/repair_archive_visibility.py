#!/usr/bin/env python3
"""Reveal hidden WeChat article bodies in existing self-contained archives."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from archive_lib import atomic_write, iter_html_files


ROOT_TAG = re.compile(
    r'(<(?P<tag>[a-z][\w:-]*)\b(?=[^>]*\bid\s*=\s*(["\'])js_content\3)[^>]*\bstyle\s*=\s*)'
    r'(?P<quote>["\'])(?P<style>.*?)(?P=quote)',
    re.IGNORECASE | re.DOTALL,
)
ROOT_OPEN = re.compile(
    r'<[a-z][\w:-]*\b(?=[^>]*\bid\s*=\s*(["\'])js_content\1)[^>]*>',
    re.IGNORECASE | re.DOTALL,
)


def visible_style(style: str) -> str:
    declarations = []
    had_display_none = False
    for declaration in style.split(";"):
        if not declaration.strip():
            continue
        name, separator, value = declaration.partition(":")
        normalized_name = name.strip().lower()
        normalized_value = value.strip().lower().replace("!important", "").strip()
        if separator and normalized_name in {"visibility", "opacity"}:
            continue
        if separator and normalized_name == "display" and normalized_value == "none":
            had_display_none = True
            continue
        declarations.append(declaration.strip())
    if had_display_none:
        declarations.append("display: block !important")
    declarations.extend(("visibility: visible !important", "opacity: 1 !important"))
    return "; ".join(declarations) + ";"


def style_is_hidden(style: str) -> bool:
    declarations = {}
    for declaration in style.split(";"):
        name, separator, value = declaration.partition(":")
        if separator:
            declarations[name.strip().lower()] = value.strip().lower().replace("!important", "").strip()
    return (
        declarations.get("visibility") in {"hidden", "collapse"}
        or declarations.get("display") == "none"
        or declarations.get("opacity") in {"0", "0.0", ".0"}
    )


def repair(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        style = match.group("style")
        if not style_is_hidden(style):
            return match.group(0)
        repaired = visible_style(style)
        if repaired == style:
            return match.group(0)
        return f'{match.group(1)}{match.group("quote")}{repaired}{match.group("quote")}'

    updated, count = ROOT_TAG.subn(replace, text, count=1)
    if count == 0:
        return "already_visible" if ROOT_OPEN.search(text) else "missing_root"
    if updated == text:
        return "already_visible"
    atomic_write(path, updated)
    return "repaired"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    results = []
    for path in iter_html_files(args.path):
        if path.name == "_collection.html":
            continue
        results.append({"path": str(path), "status": repair(path)})
    counts = {status: sum(item["status"] == status for item in results) for status in {
        "repaired", "already_visible", "missing_root"
    }}
    print(json.dumps({"counts": counts, "results": results}, ensure_ascii=False, indent=2))
    return 0 if not counts["missing_root"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
