"""轻量级 sqlite KV 缓存,带 TTL。用于持久化外部 API 响应。"""
from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class Cache:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), isolation_level=None)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS cache ("
            "  key TEXT PRIMARY KEY,"
            "  value TEXT NOT NULL,"
            "  expires_at REAL NOT NULL"
            ")"
        )

    def get(self, key: str) -> Any | None:
        row = self._conn.execute(
            "SELECT value, expires_at FROM cache WHERE key = ?", (key,)
        ).fetchone()
        if not row:
            return None
        value, expires_at = row
        if expires_at < time.time():
            self._conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            return None
        return json.loads(value)

    def set(self, key: str, value: Any, ttl_s: int) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
            (key, json.dumps(value), time.time() + ttl_s),
        )

    def hit_or_fetch(self, key: str, ttl_s: int, fetcher) -> tuple[Any | None, str]:
        """查缓存,未命中则调 fetcher()。返回 (value, status)。
        status ∈ {"cached", "ok", "missing", "error:<Type>"}"""
        cached = self.get(key)
        if cached is not None:
            return cached, "cached"
        try:
            value = fetcher()
            if value is None:
                return None, "missing"
            self.set(key, value, ttl_s)
            return value, "ok"
        except Exception as e:
            return None, f"error:{type(e).__name__}"

    def close(self) -> None:
        self._conn.close()
