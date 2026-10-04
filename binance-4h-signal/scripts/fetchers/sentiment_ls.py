"""Binance 多空比端点。顶级交易者 = 精明钱,全账户 = 散户情绪。"""
from __future__ import annotations

from ._http import get_json

FAPI = "https://fapi.binance.com"


def _ratio(path: str, symbol: str, period: str = "1h") -> float | None:
    data = get_json(
        f"{FAPI}{path}",
        params={"symbol": symbol.upper(), "period": period, "limit": 1},
    )
    if not data:
        return None
    return float(data[0]["longShortRatio"])


def fetch_top_trader_ls_position(symbol: str, period: str = "1h") -> float | None:
    """顶级交易者持仓多空比。> 1 = 精明钱整体看多。"""
    return _ratio("/futures/data/topLongShortPositionRatio", symbol, period)


def fetch_retail_ls_account(symbol: str, period: str = "1h") -> float | None:
    """全账户多空账户数比(散户情绪镜像)。常作为反向指标。"""
    return _ratio("/futures/data/globalLongShortAccountRatio", symbol, period)
