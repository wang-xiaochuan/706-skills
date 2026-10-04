#!/usr/bin/env python3
"""Write GPT vision annotations back into self-contained article HTML files."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from lxml import etree

from archive_lib import INDEX_ID, atomic_write, compact_text, extract_index, json_script_payload, parse_html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.annotations.read_text(encoding="utf-8"))
    rows = payload.get("annotations", payload if isinstance(payload, list) else [])
    grouped = defaultdict(list)
    for row in rows:
        grouped[Path(row["html"]).resolve()].append(row)
    updated = 0
    for html_file, annotations in grouped.items():
        doc = parse_html(html_file.read_text(encoding="utf-8"))
        index = extract_index(doc)
        records = {item["image_id"]: item for item in index.get("images", [])}
        for annotation in annotations:
            image_id = annotation["image_id"]
            if image_id not in records:
                raise ValueError(f"unknown image_id {image_id} in {html_file}")
            record = records[image_id]
            description = compact_text(annotation.get("visual_description")) or None
            ocr_text = compact_text(annotation.get("ocr_text")) or None
            if annotation.get("clear_event_date"):
                event_date = None
            else:
                event_date = annotation.get("event_date") or record.get("event_date")
            record.update({
                "visual_description": description,
                "vision_status": "captured_by_gpt" if description else "empty",
                "ocr_text": ocr_text,
                "ocr_status": "captured_by_gpt" if ocr_text else "empty",
                "event_date": event_date,
                "location": compact_text(annotation.get("location")) or record.get("location"),
                "entities": annotation.get("entities") or record.get("entities") or [],
            })
            record.setdefault("evidence", {})["gpt_annotation"] = ["gpt-5.6-vision"]
            nodes = doc.xpath(f'//img[@data-image-id="{image_id}"]')
            if len(nodes) != 1:
                raise ValueError(f"expected one image node for {image_id}")
            node = nodes[0]
            if description:
                node.set("data-description", description[:500])
                node.set("alt", description[:120])
            node.set("data-ocr", ocr_text or "")
            if record.get("event_date"):
                node.set("data-event-date", record["event_date"])
            else:
                node.attrib.pop("data-event-date", None)
            if record.get("location"):
                node.set("data-location", record["location"])
            if record.get("entities"):
                node.set("data-entities", ",".join(str(item) for item in record["entities"]))
            updated += 1
        script = doc.xpath(f'//script[@id="{INDEX_ID}"]')[0]
        script.text = json_script_payload(index)
        atomic_write(html_file, etree.tostring(doc, encoding="unicode", method="html", doctype="<!doctype html>"))
    print(json.dumps({"status": "ok", "html_count": len(grouped), "updated_images": updated}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
