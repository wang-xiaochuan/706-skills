#!/usr/bin/env python3
"""Query embedded article/image indexes and optionally restore matched images."""

from __future__ import annotations

import argparse
import json
import mimetypes
from pathlib import Path

from archive_lib import compact_text, decode_data_uri, extract_index, iter_html_files, parse_html


def image_haystack(article: dict, image: dict) -> str:
    fields = [
        article.get("title"), article.get("account_name"), article.get("published_at"),
        image.get("event_date"), image.get("location"), " ".join(image.get("entities") or []),
        image.get("ocr_text"), image.get("visual_description"), image.get("previous_paragraph"),
        image.get("original_caption"), image.get("next_paragraph"),
    ]
    return compact_text(" ".join(str(value or "") for value in fields)).casefold()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--date")
    parser.add_argument("--location")
    parser.add_argument("--entity")
    parser.add_argument("--extract-dir", type=Path)
    args = parser.parse_args()
    terms = [term.casefold() for term in args.query.split() if term]
    results = []
    for html_file in iter_html_files(args.path):
        try:
            doc = parse_html(html_file.read_text(encoding="utf-8"))
            index = extract_index(doc)
        except Exception:
            continue
        article = index.get("article", {})
        for image in index.get("images", []):
            haystack = image_haystack(article, image)
            if terms and not all(term in haystack for term in terms):
                continue
            if args.date and image.get("event_date") != args.date:
                continue
            if args.location and args.location.casefold() not in str(image.get("location") or "").casefold():
                continue
            if args.entity and args.entity.casefold() not in [str(item).casefold() for item in image.get("entities", [])]:
                continue
            record = {"html": str(html_file), "article": article, "image": image}
            if args.extract_dir:
                nodes = doc.xpath(f'//img[@data-image-id="{image["image_id"]}"]')
                if nodes:
                    mime, data = decode_data_uri(nodes[0].get("src", ""))
                    args.extract_dir.mkdir(parents=True, exist_ok=True)
                    suffix = mimetypes.guess_extension(mime) or ".img"
                    output = args.extract_dir / f'{html_file.stem}__{image["image_id"]}{suffix}'
                    output.write_bytes(data)
                    record["extracted_image"] = str(output)
            results.append(record)
    print(json.dumps({"count": len(results), "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
