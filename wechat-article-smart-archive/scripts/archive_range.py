#!/usr/bin/env python3
"""Discover and archive a date range for one WeChat official account."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import subprocess
import sys
from pathlib import Path

from archive_lib import atomic_write, json_script_payload, slugify


def run(command: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)


def collection_html(manifest: dict, completed: list[dict], failures: list[dict]) -> str:
    title = f'{manifest.get("account_query", "公众号")} · {manifest.get("date_range", {}).get("start", "")}—{manifest.get("date_range", {}).get("end", "")}'
    rows = "\n".join(
        f'<li><a href="{html.escape(item["file"])}">{html.escape(item["title"])}</a> · {html.escape(item.get("published_at") or "日期未知")}</li>'
        for item in completed
    ) or "<li>没有成功归档的文章</li>"
    payload = {"schema_version": "1.0", "discovery": manifest, "completed": completed, "failures": failures}
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>body{{max-width:760px;margin:2rem auto;padding:0 1rem;font:16px/1.7 -apple-system,"PingFang SC",sans-serif}}code{{background:#eee;padding:.1rem .3rem}}</style></head><body><h1>{html.escape(title)}</h1><p>数据源：<code>{html.escape(manifest.get("provider", "unknown"))}</code>；覆盖状态：<code>{html.escape(manifest.get("coverage", "unknown"))}</code></p><ul>{rows}</ul><p>失败 {len(failures)} 篇。完整机器清单已嵌入本文件。</p><script type="application/json" id="wechat-collection-index">{json_script_payload(payload)}</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True, help="Verified manifest from discover_articles.py")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    scripts = Path(__file__).resolve().parent
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "ok":
        print(json.dumps(manifest, ensure_ascii=False))
        return 3

    completed = []
    failures = []
    for article in manifest.get("articles", []):
        prefix = article.get("published_at") or "date-unknown"
        digest = hashlib.sha256(article["url"].encode()).hexdigest()[:8]
        filename = f'{prefix}__{slugify(article.get("title") or "article")}__{digest}.html'
        output = args.output_dir / filename
        command = [
            sys.executable, str(scripts / "archive_article.py"), "--url", article["url"],
            "--output", str(output), "--timeout", str(args.timeout),
        ]
        result = run(command, args.timeout + 180)
        if result.returncode == 0 and output.exists():
            completed.append({**article, "file": filename})
        else:
            try:
                detail = json.loads(result.stdout.strip().splitlines()[-1])
            except Exception:
                detail = {"error": result.stderr or result.stdout or "archive failed"}
            failures.append({**article, "detail": detail})

    index_path = args.output_dir / "_collection.html"
    atomic_write(index_path, collection_html(manifest, completed, failures))
    report = {
        "status": "ok" if not failures else "partial",
        "collection": str(index_path),
        "provider": manifest.get("provider"),
        "coverage": manifest.get("coverage"),
        "discovered": len(manifest.get("articles", [])),
        "archived": len(completed),
        "failed": len(failures),
    }
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not failures else 4


if __name__ == "__main__":
    raise SystemExit(main())
