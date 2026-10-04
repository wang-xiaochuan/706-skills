#!/usr/bin/env python3
"""Shared helpers for self-contained WeChat article archives."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from lxml import html

INDEX_ID = "wechat-article-index"
SCHEMA_VERSION = "1.0"


def parse_html(text: str):
    # Base64-inlined article images can make a single HTML document tens or
    # hundreds of megabytes. The default libxml2 limits may silently truncate
    # such documents while parsing a large data-URI attribute.
    parser = html.HTMLParser(huge_tree=True)
    return html.document_fromstring(text, parser=parser)


def compact_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def first_text(doc, xpaths: list[str]) -> str:
    for expression in xpaths:
        values = doc.xpath(expression)
        for value in values:
            if hasattr(value, "text_content"):
                value = value.text_content()
            text = compact_text(str(value))
            if text:
                return text
    return ""


def extract_index(doc) -> dict[str, Any]:
    nodes = doc.xpath(f'//script[@id="{INDEX_ID}"]')
    if not nodes or not nodes[0].text:
        raise ValueError(f"missing embedded index #{INDEX_ID}")
    return json.loads(nodes[0].text)


def encode_data_uri(data: bytes, mime_type: str) -> str:
    return f"data:{mime_type};base64,{base64.b64encode(data).decode('ascii')}"


def decode_data_uri(uri: str) -> tuple[str, bytes]:
    match = re.fullmatch(r"data:([^;,]+);base64,(.+)", uri, re.DOTALL)
    if not match:
        raise ValueError("not a base64 data URI")
    return match.group(1), base64.b64decode(match.group(2), validate=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def json_script_payload(value: Any) -> str:
    # Prevent an article string from closing the script element.
    return json.dumps(value, ensure_ascii=False, indent=2).replace("</", "<\\/")


def slugify(value: str, fallback: str = "wechat-article") -> str:
    value = compact_text(value)
    value = re.sub(r"[\\/:*?\"<>|]+", "-", value)
    value = re.sub(r"\s+", "-", value).strip(".- ")
    return (value[:80] or fallback)


def iter_html_files(path: Path):
    if path.is_file():
        yield path
    elif path.is_dir():
        yield from sorted(path.rglob("*.html"))
    else:
        raise FileNotFoundError(path)
