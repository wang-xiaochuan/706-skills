#!/usr/bin/env python3
"""Validate self-contained WeChat article HTML archives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from archive_lib import decode_data_uri, extract_index, iter_html_files, parse_html, sha256_bytes


def article_root_is_hidden(root) -> bool:
    declarations = {}
    for declaration in (root.get("style") or "").split(";"):
        name, separator, value = declaration.partition(":")
        if separator:
            declarations[name.strip().lower()] = value.strip().lower().replace("!important", "").strip()
    return (
        declarations.get("visibility") in {"hidden", "collapse"}
        or declarations.get("display") == "none"
        or declarations.get("opacity") in {"0", "0.0", ".0"}
    )


def validate(path: Path) -> dict:
    errors = []
    doc = parse_html(path.read_text(encoding="utf-8"))
    try:
        index = extract_index(doc)
    except Exception as exc:
        return {"path": str(path), "passed": False, "errors": [str(exc)]}
    images = index.get("images", [])
    if index.get("schema_version") != "1.0":
        errors.append("unsupported schema_version")
    roots = doc.xpath('//*[@id="js_content"]')
    if not roots:
        errors.append("missing article body root")
    elif article_root_is_hidden(roots[0]):
        errors.append("article body root is hidden")
    if len(doc.xpath('//*[@id="js_content"]//img | //div[contains(@class,"rich_media_content")]//img | //article//img')) < len(images):
        errors.append("embedded index contains more images than article body")
    for item in images:
        nodes = doc.xpath(f'//img[@data-image-id="{item.get("image_id", "")}"]')
        if len(nodes) != 1:
            errors.append(f'{item.get("image_id")}: expected exactly one img node')
            continue
        source = nodes[0].get("src", "")
        try:
            _, data = decode_data_uri(source)
            if sha256_bytes(data) != item.get("sha256"):
                errors.append(f'{item.get("image_id")}: sha256 mismatch')
        except Exception as exc:
            errors.append(f'{item.get("image_id")}: invalid data URI: {exc}')
    remote = [value for value in doc.xpath('//img/@src') if value.startswith(("http://", "https://"))]
    if remote:
        errors.append(f"{len(remote)} remote image sources remain")
    article = index.get("article", {})
    if not article.get("title"):
        errors.append("missing article title")
    return {"path": str(path), "passed": not errors, "image_count": len(images), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    results = [validate(path) for path in iter_html_files(args.path) if path.name != "_collection.html"]
    passed = bool(results) and all(item["passed"] for item in results)
    print(json.dumps({"passed": passed, "results": results}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
