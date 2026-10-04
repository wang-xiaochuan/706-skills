#!/usr/bin/env python3
"""Discover WeChat account seed articles and optionally add verified WeWe RSS feeds."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests

from archive_article import USER_AGENT
from archive_lib import atomic_write, compact_text, parse_html
from discover_articles import is_wechat_article_url, resolve_sogou_link


def load_seed_candidates(path: Path | None) -> dict[str, list[str]]:
    if not path:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("results", []) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("candidate file must contain a results list")
    grouped: dict[str, list[str]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        account = compact_text(str(row.get("account", "")))
        url = compact_text(str(row.get("url", "")))
        if account and is_wechat_article_url(url):
            grouped.setdefault(account.casefold(), []).append(url)
    return grouped


def is_stable_seed_url(url: str) -> bool:
    """WeWe accepts stable share links such as /s/<slug>, not signed search redirects."""
    parsed = urlparse(url)
    return is_wechat_article_url(url) and parsed.path.startswith("/s/")


def sogou_seed_candidates(account: str, timeout: int, pages: int) -> list[str]:
    session = requests.Session()
    candidates: list[str] = []
    seen: set[str] = set()
    for page in range(1, pages + 1):
        search_url = f"https://weixin.sogou.com/weixin?type=2&query={quote(account)}&page={page}"
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
            hrefs = item.xpath('.//h3/a/@href')
            if not hrefs:
                continue
            try:
                url = resolve_sogou_link(session, search_url, hrefs[0], timeout)
            except Exception:
                continue
            if url not in seen:
                seen.add(url)
                candidates.append(url)
    return candidates


def is_loopback_base_url(base_url: str) -> bool:
    host = (urlparse(base_url).hostname or "").casefold()
    return host in {"127.0.0.1", "localhost", "::1"}


class WeWeClient:
    def __init__(self, base_url: str, auth_code: str | None, timeout: int):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"Authorization": auth_code} if auth_code else {}

    def _data(self, response: requests.Response) -> Any:
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            raise ValueError(compact_text(str(payload["error"])))
        return payload.get("result", {}).get("data")

    def feeds(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/trpc/feed.list",
            headers=self.headers,
            params={"input": json.dumps({"limit": 1000}, ensure_ascii=False)},
            timeout=self.timeout,
        )
        data = self._data(response) or {}
        return data.get("items", [])

    def identify(self, article_url: str) -> list[dict[str, Any]]:
        response = requests.post(
            f"{self.base_url}/trpc/platform.getMpInfo",
            headers=self.headers,
            json={"wxsLink": article_url},
            timeout=self.timeout,
        )
        return self._data(response) or []

    def add(self, feed: dict[str, Any]) -> dict[str, Any]:
        body = {
            "id": feed["id"],
            "mpName": feed["name"],
            "mpCover": feed.get("cover", ""),
            "mpIntro": feed.get("intro", ""),
            "updateTime": feed.get("updateTime", 0),
            "status": 1,
        }
        response = requests.post(
            f"{self.base_url}/trpc/feed.add",
            headers=self.headers,
            json=body,
            timeout=self.timeout,
        )
        return self._data(response) or body


def process_account(
    account: str,
    supplied_urls: list[str],
    client: WeWeClient,
    timeout: int,
    pages: int,
    add: bool,
    existing_ids: set[str],
) -> dict[str, Any]:
    row: dict[str, Any] = {"query": account, "status": "not_found", "candidates": []}
    try:
        urls = supplied_urls or sogou_seed_candidates(account, timeout, pages)
        row["discovery"] = "provided_candidates" if supplied_urls else "sogou_weixin_direct_http"
    except Exception as exc:
        row.update(status="discovery_failed", error=compact_text(str(exc)))
        return row
    row["candidates"] = urls
    mismatches: list[dict[str, str]] = []
    for url in urls:
        if not is_stable_seed_url(url):
            mismatches.append({"url": url, "error": "noncanonical_search_url"})
            continue
        try:
            matches = client.identify(url)
        except Exception as exc:
            mismatches.append({"url": url, "error": compact_text(str(exc))})
            continue
        for match in matches:
            actual = compact_text(str(match.get("name", "")))
            if actual.casefold() != compact_text(account).casefold():
                mismatches.append({"url": url, "actual_account": actual})
                continue
            row.update(
                status="verified",
                seed_url=url,
                account={
                    "id": match.get("id"),
                    "name": actual,
                    "intro": match.get("intro"),
                    "cover": match.get("cover"),
                    "updateTime": match.get("updateTime"),
                },
            )
            if match.get("id") in existing_ids:
                row["status"] = "already_added"
            elif add:
                client.add(match)
                existing_ids.add(str(match.get("id")))
                row["status"] = "added"
            return row
    row["rejected"] = mismatches
    if urls:
        row["status"] = "candidate_unusable"
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("accounts", nargs="+", help="Exact public-account names")
    parser.add_argument("--candidates", type=Path, help="JSON results with account and article URL")
    parser.add_argument("--base-url", default="http://127.0.0.1:4000")
    parser.add_argument("--auth-code", default=os.environ.get("WEWE_AUTH_CODE"))
    parser.add_argument("--sogou-pages", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--add", action="store_true", help="Add exact-name verified accounts")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.auth_code and not is_loopback_base_url(args.base_url):
        print(json.dumps({"status": "failed", "code": "missing_auth_code_for_remote_service"}, ensure_ascii=False))
        return 2
    try:
        grouped = load_seed_candidates(args.candidates)
        client = WeWeClient(args.base_url, args.auth_code, args.timeout)
        existing_ids = {str(item.get("id")) for item in client.feeds()}
        results = [
            process_account(
                account,
                grouped.get(compact_text(account).casefold(), []),
                client,
                args.timeout,
                args.sogou_pages,
                args.add,
                existing_ids,
            )
            for account in args.accounts
        ]
        payload = {
            "status": "ok",
            "coverage": "public_web_index_partial",
            "coverage_note": "网页搜索未命中不代表公众号不存在；只有账号名精确匹配才会添加。",
            "results": results,
        }
        atomic_write(args.output, json.dumps(payload, ensure_ascii=False, indent=2))
        counts: dict[str, int] = {}
        for row in results:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
        print(json.dumps({"status": "ok", "output": str(args.output), "counts": counts}, ensure_ascii=False))
        return 0
    except Exception as exc:
        payload = {"status": "failed", "code": "unexpected_error", "error": compact_text(str(exc))}
        atomic_write(args.output, json.dumps(payload, ensure_ascii=False, indent=2))
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
