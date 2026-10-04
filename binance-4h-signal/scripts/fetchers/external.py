"""外部数据源:Alternative.me 加密恐慌贪婪指数。预留插件槽。"""
from __future__ import annotations

from ._http import get_json

FNG_URL = "https://api.alternative.me/fng/"


def fetch_fear_greed() -> int | None:
    """返回当前 Fear & Greed Index 值(0-100)。日更新。"""
    data = get_json(FNG_URL, params={"limit": 1, "format": "json"})
    rows = data.get("data", [])
    if not rows:
        return None
    return int(rows[0]["value"])
