"""带重试的 HTTP GET,用于所有 fetcher 共享。

Binance 期货 API (fapi.binance.com) 偶发 SSL handshake timeout,需要退避重试。
"""
from __future__ import annotations

import time
from typing import Any

import requests

DEFAULT_TIMEOUT = 15


def get_json(
    url: str,
    params: dict | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = 3,
) -> Any:
    """GET + raise_for_status + json,失败指数退避重试。"""
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1.5 ** attempt)
    raise RuntimeError(f"GET {url} failed after {retries} retries: {last_err}")
