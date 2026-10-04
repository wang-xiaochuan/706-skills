"""Binance 永续合约元数据:资金费率 / 持仓量 / 基差 / 清算。

所有端点来自 `fapi.binance.com`(公开,无需 API Key)。
每个函数返回标量或 None。异常由 cache.hit_or_fetch 包装,调用方透传 status。
"""
from __future__ import annotations

from ._http import get_json

FAPI = "https://fapi.binance.com"


def _get(path: str, params: dict):
    return get_json(f"{FAPI}{path}", params=params)


def fetch_funding_rate(symbol: str) -> float | None:
    """当前/最新资金费率(小数形式,如 0.0001 = 0.01%)。"""
    data = _get("/fapi/v1/fundingRate", {"symbol": symbol.upper(), "limit": 1})
    if not data:
        return None
    return float(data[0]["fundingRate"])


def fetch_oi_change_24h(symbol: str) -> float | None:
    """24 小时持仓量变化百分比(正 = OI 增长)。用 1h 粒度历史计算。"""
    data = _get(
        "/futures/data/openInterestHist",
        {"symbol": symbol.upper(), "period": "1h", "limit": 25},
    )
    if not data or len(data) < 2:
        return None
    latest = float(data[-1]["sumOpenInterest"])
    earliest = float(data[0]["sumOpenInterest"])
    if earliest == 0:
        return None
    return (latest - earliest) / earliest


def fetch_basis(symbol: str) -> float | None:
    """永续 vs 指数价格的相对溢价(小数形式)。
    > 0 = 永续价高于现货指数(看多过度风险);< 0 = 倒挂(恐慌)。"""
    data = _get("/fapi/v1/premiumIndex", {"symbol": symbol.upper()})
    if not data:
        return None
    mark = float(data["markPrice"])
    index = float(data["indexPrice"])
    if index == 0:
        return None
    return (mark - index) / index


def fetch_liq_stats(symbol: str, window_h: int = 1) -> dict | None:
    """清算统计 —— **当前不可用**。

    Binance 自 2021 起限制了公开历史清算 REST 端点(`allForceOrders` / `forceOrders`
    都需要 API Key 和签名)。公开实时流仅通过 WebSocket `!forceOrder@arr` 提供,
    不适配本 skill 每小时一次的 REST 抓取模式。

    保留此函数作为 stub,始终返回 None,让调用方走降级分支(score=0,
    components_status="unavailable")。后续若接入 Coinglass 免费 API 或
    自建 WS 缓冲,再填充真实实现。
    """
    return None
