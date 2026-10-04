#!/usr/bin/env python3
"""Restore embedded images to a temporary directory for GPT vision review."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
from pathlib import Path

from archive_lib import decode_data_uri, extract_index, iter_html_files, parse_html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--deduplicate", action="store_true", help="Store identical images once by SHA-256")
    parser.add_argument("--pending-only", action="store_true", help="Skip images already reviewed by GPT")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tasks = []
    unique_outputs = {}
    for html_file in iter_html_files(args.path):
        if html_file.name == "_collection.html":
            continue
        doc = parse_html(html_file.read_text(encoding="utf-8"))
        index = extract_index(doc)
        records = {item["image_id"]: item for item in index.get("images", [])}
        for node in doc.xpath('//img[@data-image-id]'):
            image_id = node.get("data-image-id")
            if image_id not in records or not node.get("src", "").startswith("data:"):
                continue
            item = records[image_id]
            if args.pending_only and item.get("vision_status") in ("captured_by_gpt", "empty") and item.get("ocr_status") in ("captured_by_gpt", "empty"):
                continue
            mime, data = decode_data_uri(node.get("src"))
            suffix = mimetypes.guess_extension(mime) or ".img"
            digest = item.get("sha256") or hashlib.sha256(data).hexdigest()
            if args.deduplicate:
                output = unique_outputs.get(digest) or args.output_dir / f"{digest}{suffix}"
                unique_outputs[digest] = output
            else:
                output = args.output_dir / f"{html_file.stem}__{image_id}{suffix}"
                unique_outputs[f"{html_file.resolve()}::{image_id}"] = output
            if not output.exists():
                output.write_bytes(data)
            tasks.append({
                "html": str(html_file.resolve()),
                "image_id": image_id,
                "image_path": str(output.resolve()),
                "sha256": digest,
                "article": index.get("article", {}),
                "previous_paragraph": item.get("previous_paragraph"),
                "original_caption": item.get("original_caption"),
                "next_paragraph": item.get("next_paragraph"),
            })
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ok", "manifest": str(args.manifest), "image_count": len(tasks),
        "unique_image_count": len(unique_outputs),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
