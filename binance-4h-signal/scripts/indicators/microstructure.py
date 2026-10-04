"""微观结构类:资金费率 / OI 变化 / 基差 / 清算脉冲(stub)。

与 trend/momentum 等不同,此类别不依赖 K 线序列,只消费 REST 拉来的 meta 标量。
"""
from __future__ import annotations

from ._base import safe_mean


def _score_funding(fr: float | None) -> float | None:
    """资金费率反向评分。极正=多头拥挤;极负=空头拥挤。"""
    if fr is None: return None
    if fr > 0.0005: return -2.0
    if fr > 0.0002: return -1.0
    if fr < -0.0005: return 2.0
    if fr < -0.0002: return 1.0
    return 0.0


def _score_oi_change(oi_chg: float | None) -> float | None:
    """24h OI 变化。暴增=过热;暴跌=清算后反弹。"""
    if oi_chg is None: return None
    if oi_chg < -0.10: return 1.0
    if oi_chg > 0.10: return -0.5
    return 0.0


def _score_basis(basis: float | None) -> float | None:
    """永续-现货基差。"""
    if basis is None: return None
    if basis > 0.003: return -2.0
    if basis > 0.001: return -1.0
    if basis < -0.003: return 2.0
    if basis < -0.001: return 1.0
    return 0.0


def _score_liquidations(liq: dict | None) -> float | None:
    """清算脉冲:long_liq 主导 → 反弹 +;short_liq 主导 → 回调 -。
    当前 Binance 公开 API 不给数据,fetcher 返回 None。保留接口,一旦未来接入即生效。"""
    if liq is None: return None
    total = liq.get("long_liq", 0.0) + liq.get("short_liq", 0.0)
    if total < 1_000_000:
        return 0.0  # 清算量太小,无信号
    imbalance = (liq["long_liq"] - liq["short_liq"]) / total
    if imbalance > 0.7: return 2.0   # 多头爆仓占压倒性,利多反弹
    if imbalance > 0.3: return 1.0
    if imbalance < -0.7: return -2.0
    if imbalance < -0.3: return -1.0
    return 0.0


def score(meta: dict, cfg: dict) -> tuple[float, dict, dict]:
    """输入 meta 标量 dict。返回 (类别分, 子项分, 子项状态)。"""
    enabled = cfg.get("features_enabled", {})
    raw, status = {}, {}

    def add(flag: str, meta_key: str, key: str, value_or_none: float | None):
        if not enabled.get(flag, True):
            raw[key] = None; status[key] = "disabled"; return
        if meta.get(meta_key) is None:
            raw[key] = None; status[key] = "missing"; return
        raw[key] = value_or_none
        status[key] = "ok" if value_or_none is not None else "missing"

    add("funding", "funding_rate", "funding", _score_funding(meta.get("funding_rate")))
    add("oi_change", "oi_change_24h", "oi_change", _score_oi_change(meta.get("oi_change_24h")))
    add("basis", "basis", "basis", _score_basis(meta.get("basis")))
    add("liquidations", "liquidations", "liquidations", _score_liquidations(meta.get("liquidations")))

    return safe_mean(list(raw.values())), {k: (0.0 if v is None else v)
                                            for k, v in raw.items()}, status
