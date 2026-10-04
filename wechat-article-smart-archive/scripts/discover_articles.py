#!/usr/bin/env python3
"""Verify web-search candidate URLs against WeChat article frontends."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urljoin, urlparse

import requests

from archive_article import USER_AGENT, article_metadata, pick_article_root, reject_block_page
from archive_lib import atomic_write, compact_text, parse_html


def parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    text = compact_text(str(value))
    if text.isdigit():
        number = int(text)
        if number > 10_000_000_000:
            number //= 1000
        return datetime.fromtimestamp(number, tz=timezone.utc).date()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text[:19], fmt).date()
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def load_candidates(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    queries = payload.get("queries", []) if isinstance(payload, dict) else []
    rows = payload.get("results", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("candidates must be a list or an object containing results")
    normalized = []
    for row in rows:
        if isinstance(row, str):
            normalized.append({"url": row})
        elif isinstance(row, dict) and row.get("url"):
            normalized.append(row)
    return [compact_text(str(item)) for item in queries], normalized


def is_wechat_article_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.hostname == "mp.weixin.qq.com" and parsed.path.startswith("/s")


def month_queries(account: str, start: date, end: date) -> list[str]:
    queries = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        queries.append(f"{account} {year}年{month}月")
        month = month + 1
        if month == 13:
            year, month = year + 1, 1
    return queries


def resolve_sogou_link(session: requests.Session, search_url: str, href: str, timeout: int) -> str:
    response = session.get(
        urljoin(search_url, href),
        headers={"User-Agent": USER_AGENT, "Referer": search_url},
        timeout=timeout,
    )
    response.raise_for_status()
    if is_wechat_article_url(response.url):
        return response.url
    parts = re.findall(r"url\s*\+=\s*'([^']*)';", response.text)
    resolved = "".join(parts).replace("@", "")
    if not is_wechat_article_url(resolved):
        raise ValueError("Sogou result did not resolve to a WeChat article frontend")
    return resolved


def sogou_candidates(account: str, start: date, end: date, timeout: int, pages: int) -> tuple[list[str], list[dict]]:
    session = requests.Session()
    queries = month_queries(account, start, end)
    candidates, seen = [], set()
    for query in queries:
        for page in range(1, pages + 1):
            search_url = f"https://weixin.sogou.com/weixin?type=2&query={quote(query)}&page={page}"
            response = session.get(search_url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
            response.raise_for_status()
            if "请输入验证码" in response.text or "antispider" in response.url:
                raise ValueError("Sogou returned an anti-spider verification page")
            doc = parse_html(response.text)
            items = doc.xpath('//ul[contains(@class,"news-list")]/li')
            if not items:
                break
            for item in items:
                source = compact_text(" ".join(item.xpath('.//div[contains(@class,"s-p")]/*[1]//text()')))
                if source.casefold() != compact_text(account).casefold():
                    continue
                raw = " ".join(item.xpath('.//text()'))
                timestamp = re.search(r"timeConvert\('(\d+)'\)", raw)
                published = parse_date(timestamp.group(1)) if timestamp else None
                if not published or not start <= published <= end:
                    continue
                hrefs = item.xpath('.//h3/a/@href')
                if not hrefs:
                    continue
                try:
                    url = resolve_sogou_link(session, search_url, hrefs[0], timeout)
                except Exception:
                    continue
                if url in seen:
                    continue
                seen.add(url)
                candidates.append({
                    "url": url,
                    "search_title": compact_text(" ".join(item.xpath('.//h3//text()'))),
                    "search_account": source,
                    "search_published_at": published.isoformat(),
                })
    return queries, candidates


def verify_candidate(row: dict[str, Any], account: str, start: date, end: date, timeout: int, session: requests.Session | None = None) -> tuple[dict | None, dict | None]:
    url = str(row["url"])
    if not is_wechat_article_url(url):
        return None, {"url": url, "code": "not_wechat_article_url"}
    try:
        response = (session or requests).get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        response.raise_for_status()
        if len(response.content) > 15 * 1024 * 1024:
            raise ValueError("article HTML exceeds 15 MB")
        response.encoding = response.apparent_encoding or "utf-8"
        reject_block_page(response.text)
        doc = parse_html(response.text)
        metadata = article_metadata(doc, url)
        pick_article_root(doc)
    except Exception as exc:
        return None, {"url": url, "code": "frontend_fetch_failed", "error": compact_text(str(exc))}

    actual_account = compact_text(metadata.get("account_name"))
    if not actual_account:
        return None, {"url": url, "code": "account_unverified"}
    if actual_account.casefold() != compact_text(account).casefold():
        return None, {"url": url, "code": "account_mismatch", "actual_account": actual_account}
    published = parse_date(metadata.get("published_at"))
    if not published:
        return None, {"url": url, "code": "date_unverified"}
    if not start <= published <= end:
        return None, {"url": url, "code": "outside_date_range", "published_at": published.isoformat()}
    return {
        "title": metadata["title"],
        "url": url,
        "published_at": published.isoformat(),
        "author": metadata.get("author"),
        "account_name": actual_account,
        "provider": "web_search_frontend_verified",
    }, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", required=True)
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--candidates", type=Path, help="Optional candidates from another web search provider")
    parser.add_argument("--sogou-pages", type=int, default=3, help="Pages per month for direct HTTP Sogou search")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    if args.start > args.end:
        print(json.dumps({"status": "failed", "code": "invalid_date_range"}, ensure_ascii=False))
        return 2
    try:
        if args.candidates:
            queries, candidates = load_candidates(args.candidates)
            source_provider = "provided_web_candidates"
        else:
            queries, candidates = sogou_candidates(args.account, args.start, args.end, args.timeout, args.sogou_pages)
            source_provider = "sogou_weixin_direct_http"
        articles, rejected, seen = [], [], set()
        verification_session = requests.Session()
        for row in candidates:
            url = str(row["url"])
            if url in seen:
                continue
            seen.add(url)
            accepted, failure = verify_candidate(row, args.account, args.start, args.end, args.timeout, verification_session)
            if accepted:
                articles.append(accepted)
            elif failure:
                rejected.append(failure)
        manifest = {
            "status": "ok",
            "provider": source_provider,
            "coverage": "public_web_index_partial",
            "coverage_note": "网页搜索索引可能漏文；未命中不能解释为公众号未发布。",
            "account_query": args.account,
            "selected_account": {"nickname": args.account, "verification": "article_frontend_exact_match"} if articles else None,
            "date_range": {"start": args.start.isoformat(), "end": args.end.isoformat()},
            "search_queries": queries,
            "candidate_count": len(candidates),
            "articles": sorted(articles, key=lambda item: item["published_at"], reverse=True),
            "rejected": rejected,
        }
        atomic_write(args.output, json.dumps(manifest, ensure_ascii=False, indent=2))
        print(json.dumps({"status": "ok", "output": str(args.output), "candidate_count": len(candidates), "article_count": len(articles), "rejected_count": len(rejected), "coverage": manifest["coverage"]}, ensure_ascii=False))
        return 0
    except Exception as exc:
        payload = {"status": "failed", "code": "unexpected_error", "error": compact_text(str(exc))}
        atomic_write(args.output, json.dumps(payload, ensure_ascii=False, indent=2))
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
