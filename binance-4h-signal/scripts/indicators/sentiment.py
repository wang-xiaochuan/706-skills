"""情绪类:顶级交易者 L/S(顺向)、散户 L/S(反向)、F&G 指数、精明钱-散户背离。"""
from __future__ import annotations

from ._base import safe_mean


def _score_top_trader_ls(ratio: float | None) -> float | None:
    if ratio is None: return None
    if ratio > 1.5: return 1.5
    if ratio > 1.2: return 0.8
    if ratio < 0.7: return -1.5
    if ratio < 0.85: return -0.8
    return 0.0


def _score_retail_ls(ratio: float | None) -> float | None:
    """散户反向指标。"""
    if ratio is None: return None
    if ratio > 2.0: return -1.5
    if ratio > 1.5: return -0.8
    if ratio < 0.5: return 1.5
    if ratio < 0.7: return 0.8
    return 0.0


def _score_fear_greed(fg: int | None) -> float | None:
    if fg is None: return None
    if fg < 20: return 2.0
    if fg < 40: return 1.0
    if fg > 80: return -2.0
    if fg > 60: return -1.0
    return 0.0


def _score_smart_retail_divergence(top_ls: float | None, retail_ls: float | None
                                    ) -> float | None:
    """精明钱和散户立场相反 = 高置信度信号。
    - 精明钱看多(>1.2) 且 散户看空(<0.8) → 大机会反弹 +2
    - 精明钱看空(<0.85) 且 散户看多(>1.5)  → 大机会回调 -2
    - 同向或中性 → 0
    """
    if top_ls is None or retail_ls is None: return None
    if top_ls > 1.2 and retail_ls < 0.8: return 2.0
    if top_ls > 1.05 and retail_ls < 1.0: return 1.0
    if top_ls < 0.85 and retail_ls > 1.5: return -2.0
    if top_ls < 0.95 and retail_ls > 1.2: return -1.0
    return 0.0


def score(meta: dict, cfg: dict) -> tuple[float, dict, dict]:
    enabled = cfg.get("features_enabled", {})
    raw, status = {}, {}

    def add(flag: str, meta_key: str, key: str, value_or_none: float | None):
        if not enabled.get(flag, True):
            raw[key] = None; status[key] = "disabled"; return
        if meta.get(meta_key) is None:
            raw[key] = None; status[key] = "missing"; return
        raw[key] = value_or_none
        status[key] = "ok" if value_or_none is not None else "missing"

    add("top_trader_ls", "top_trader_ls", "top_trader_ls",
        _score_top_trader_ls(meta.get("top_trader_ls")))
    add("retail_ls", "retail_ls", "retail_ls",
        _score_retail_ls(meta.get("retail_ls")))
    add("fear_greed", "fear_greed", "fear_greed",
        _score_fear_greed(meta.get("fear_greed")))

    # 背离需要两个子数据源都存在
    div_key = "smart_retail_div"
    if not enabled.get("smart_retail_div", True):
        raw[div_key] = None; status[div_key] = "disabled"
    elif meta.get("top_trader_ls") is None or meta.get("retail_ls") is None:
        raw[div_key] = None; status[div_key] = "missing"
    else:
        v = _score_smart_retail_divergence(meta.get("top_trader_ls"),
                                           meta.get("retail_ls"))
        raw[div_key] = v
        status[div_key] = "ok" if v is not None else "missing"

    return safe_mean(list(raw.values())), {k: (0.0 if v is None else v)
                                            for k, v in raw.items()}, status
