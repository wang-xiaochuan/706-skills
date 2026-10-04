#!/usr/bin/env python3
"""Run resumable GPT vision/OCR annotation batches for extracted archive images."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests


PROMPT = """你在为微信公众号图片建立可检索索引。依次分析下方带 image_key 的图片。
请忠实识别图片中的可见文字并描述视觉内容；不要根据常识猜测人物身份。
结合提供的文章标题、发布日期及相邻段落，只在有证据时填写活动日期、地点和实体。
event_date 只表示图片所宣传或记录的实际活动日期，不是历史年表、书籍出版年、照片年代；必须是 2000—2099 年的 YYYY-MM-DD 或 null。
location 必须是字符串或 null；entities 必须是字符串数组。
ocr_text 尽可能保留原文换行；看不清的字不要臆造。每个 image_key 必须且只能返回一次。"""


SCHEMA = {
    "type": "object",
    "properties": {
        "annotations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "image_key": {"type": "string"},
                    "visual_description": {"type": "string"},
                    "ocr_text": {"type": "string"},
                    "event_date": {"type": ["string", "null"]},
                    "location": {"type": ["string", "null"]},
                    "entities": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["image_key", "visual_description", "ocr_text", "event_date", "location", "entities"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["annotations"],
    "additionalProperties": False,
}


def compact(value: Any, limit: int = 600) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def output_text(payload: dict) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    pieces = []
    for item in payload.get("output", []):
        for part in item.get("content", []) if isinstance(item, dict) else []:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                pieces.append(part["text"])
    if pieces:
        return "\n".join(pieces)
    choices = payload.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content")
        if isinstance(content, str):
            return content
    raise ValueError("API response did not contain output text")


def parse_json_text(value: str) -> dict:
    value = value.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, re.DOTALL)
    if fenced:
        value = fenced.group(1)
    return json.loads(value)


def valid_event_date(value: Any) -> str | None:
    text = str(value or "").strip()
    return text if re.fullmatch(r"20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])", text) else None


def image_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def context_text(key: str, rows: list[dict]) -> str:
    first = rows[0]
    article = first.get("article") or {}
    contexts = []
    for row in rows[:3]:
        contexts.append({
            "article_title": compact((row.get("article") or {}).get("title"), 240),
            "article_published_at": compact((row.get("article") or {}).get("published_at"), 80),
            "previous_paragraph": compact(row.get("previous_paragraph")),
            "original_caption": compact(row.get("original_caption")),
            "next_paragraph": compact(row.get("next_paragraph")),
        })
    return json.dumps({
        "image_key": key,
        "account": compact(article.get("account_name"), 120),
        "contexts": contexts,
    }, ensure_ascii=False)


class Runner:
    def __init__(self, args):
        self.args = args
        self.url = args.base_url.rstrip("/") + "/responses"
        self.headers = {"Authorization": f"Bearer {args.api_key}", "Content-Type": "application/json"}

    def request(self, batch: list[tuple[str, list[dict]]]) -> list[dict]:
        content = [{"type": "input_text", "text": PROMPT}]
        expected = []
        for key, rows in batch:
            expected.append(key)
            content.append({"type": "input_text", "text": context_text(key, rows)})
            content.append({"type": "input_image", "image_url": image_data_url(Path(rows[0]["image_path"])), "detail": self.args.detail})
        base_payload = {
            "model": self.args.model,
            "input": [{"role": "user", "content": content}],
            "reasoning": {"effort": self.args.reasoning_effort},
            "max_output_tokens": self.args.max_output_tokens,
            "store": False,
        }
        structured = {
            **base_payload,
            "text": {"format": {"type": "json_schema", "name": "wechat_image_annotations", "strict": True, "schema": SCHEMA}},
        }
        last_error = None
        for attempt in range(1, self.args.retries + 1):
            try:
                response = requests.post(self.url, headers=self.headers, json=structured, timeout=self.args.timeout)
                if response.status_code == 400 and attempt == 1:
                    fallback = {**base_payload}
                    fallback["input"][0]["content"][0]["text"] += "\n只输出合法 JSON，结构为 {\"annotations\":[...]}。"
                    response = requests.post(self.url, headers=self.headers, json=fallback, timeout=self.args.timeout)
                response.raise_for_status()
                parsed = parse_json_text(output_text(response.json()))
                rows = parsed.get("annotations", [])
                found = [row.get("image_key") for row in rows]
                if sorted(found) != sorted(expected):
                    raise ValueError(f"annotation keys mismatch: expected {expected}, got {found}")
                return rows
            except Exception as exc:
                last_error = exc
                if attempt < self.args.retries:
                    time.sleep(min(2 ** attempt, 20))
        raise RuntimeError(str(last_error))


def load_checkpoint(path: Path) -> dict[str, dict]:
    completed = {}
    if not path.exists():
        return completed
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            completed[row["sha256"]] = row
    return completed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.6-terra")
    parser.add_argument("--detail", choices=("low", "high", "original", "auto"), default="original")
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "high"), default="low")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--max-output-tokens", type=int, default=5000)
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1")
    args = parser.parse_args()
    args.api_key = os.environ.get("OPENAI_API_KEY")
    if not args.api_key:
        print(json.dumps({"status": "failed", "code": "missing_openai_api_key"}))
        return 2

    tasks = json.loads(args.manifest.read_text(encoding="utf-8"))["tasks"]
    by_sha = defaultdict(list)
    for task in tasks:
        by_sha[task["sha256"]].append(task)
    completed = load_checkpoint(args.checkpoint)
    pending = [(sha, rows) for sha, rows in by_sha.items() if sha not in completed]
    if args.limit is not None:
        pending = pending[:args.limit]
    batches = [pending[index:index + args.batch_size] for index in range(0, len(pending), args.batch_size)]
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    failures = []
    runner = Runner(args)

    def process(batch):
        annotations = runner.request(batch)
        mapped = {row["image_key"]: row for row in annotations}
        return [{"sha256": sha, "annotation": mapped[sha]} for sha, _ in batch]

    done_now = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process, batch): batch for batch in batches}
        for future in as_completed(futures):
            batch = futures[future]
            try:
                rows = future.result()
                with lock, args.checkpoint.open("a", encoding="utf-8") as handle:
                    for row in rows:
                        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                        completed[row["sha256"]] = row
                        done_now += 1
                print(json.dumps({"status": "progress", "annotated_unique": len(completed), "completed_now": done_now, "total_unique": len(by_sha)}, ensure_ascii=False), flush=True)
            except Exception as exc:
                failures.append({"sha256": [sha for sha, _ in batch], "error": compact(exc, 1000)})

    expanded = []
    for sha, rows in by_sha.items():
        if sha not in completed:
            continue
        annotation = completed[sha]["annotation"]
        for task in rows:
            expanded.append({
                "html": task["html"], "image_id": task["image_id"],
                "visual_description": annotation.get("visual_description") or "",
                "ocr_text": annotation.get("ocr_text") or "",
                "event_date": valid_event_date(annotation.get("event_date")),
                "location": annotation.get("location"),
                "entities": annotation.get("entities") or [],
            })
    args.annotations.parent.mkdir(parents=True, exist_ok=True)
    args.annotations.write_text(json.dumps({"annotations": expanded, "failures": failures}, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "status": "ok" if not failures else "partial", "task_count": len(tasks),
        "unique_image_count": len(by_sha), "annotated_unique": len(completed),
        "expanded_annotations": len(expanded), "failed_batches": len(failures),
        "checkpoint": str(args.checkpoint), "annotations": str(args.annotations),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if not failures else 4


if __name__ == "__main__":
    raise SystemExit(main())
