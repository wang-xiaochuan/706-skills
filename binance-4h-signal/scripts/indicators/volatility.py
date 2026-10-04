"""波动类:Bollinger %B, BB Width %ile, ATR%, Keltner Squeeze。"""
from __future__ import annotations

import pandas as pd

from ._base import sma, atr_wilder, percentile_rank, clip_score, safe_mean


def compute(df_4h: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = df_4h.copy()
    ic = cfg["indicators"]
    mid = sma(out["close"], ic["bb_period"])
    sd = out["close"].rolling(ic["bb_period"]).std()
    upper = mid + ic["bb_std"] * sd
    lower = mid - ic["bb_std"] * sd
    out["bb_mid"] = mid
    out["bb_upper"] = upper
    out["bb_lower"] = lower
    out["bb_width"] = (upper - lower) / mid
    out["bb_width_pctile"] = percentile_rank(out["bb_width"], window=100)

    out["atr"] = atr_wilder(out, ic["atr_period"])
    out["atr_pct"] = out["atr"] / out["close"]
    out["atr_pctile"] = percentile_rank(out["atr_pct"], window=100)

    # Keltner Channel = EMA(20) ± 1.5 * ATR
    ema20 = out["close"].ewm(span=20, adjust=False).mean()
    out["kc_upper"] = ema20 + 1.5 * out["atr"]
    out["kc_lower"] = ema20 - 1.5 * out["atr"]
    return out


# ───────── 评分 ─────────

def _score_bollinger_pctb(last: pd.Series) -> float:
    upper, lower = last["bb_upper"], last["bb_lower"]
    rng = upper - lower
    if rng <= 0: return 0.0
    pct_b = (last["close"] - lower) / rng
    if pct_b < 0.1: return 2.0
    if pct_b < 0.3: return 1.0
    if pct_b > 0.9: return -2.0
    if pct_b > 0.7: return -1.0
    return 0.0


def _score_bb_width_pctile(last: pd.Series) -> float | None:
    """BB 带宽百分位,本身非方向性——<20 提示"挤压即将突破",价格偏移方向由其他维度决定。"""
    pct = last.get("bb_width_pctile")
    if pct is None or pd.isna(pct): return None
    # 作为中性信号,不给方向性分;但极端低挤压下提示"准备好"——给小分让调用方察觉
    if pct < 10: return 0.5   # 极度挤压
    if pct > 90: return -0.5  # 极度扩张,反转风险
    return 0.0


def _score_atr_pctile(last: pd.Series) -> float | None:
    """ATR 百分位。极低 → 等待突破;极高 → 回归压力。偏弱方向性信号。"""
    pct = last.get("atr_pctile")
    if pct is None or pd.isna(pct): return None
    if pct < 15: return 0.3
    if pct > 85: return -0.3
    return 0.0


def _score_keltner_squeeze(last: pd.Series) -> float | None:
    """BB 完全套入 KC 内 = Squeeze,即将释放。方向由价格相对中轨决定。"""
    bb_u, bb_l = last["bb_upper"], last["bb_lower"]
    kc_u, kc_l = last.get("kc_upper"), last.get("kc_lower")
    if any(pd.isna(v) for v in [bb_u, bb_l, kc_u, kc_l]):
        return None
    squeeze = (bb_u < kc_u) and (bb_l > kc_l)
    if not squeeze:
        return 0.0
    # squeeze 中,看价格相对 BB 中轨的方向
    bb_mid = last.get("bb_mid")
    if pd.isna(bb_mid): return 0.0
    return 1.5 if last["close"] > bb_mid else -1.5


def score(df_ind: pd.DataFrame, cfg: dict) -> tuple[float, dict, dict]:
    enabled = cfg.get("features_enabled", {})
    last = df_ind.iloc[-1]
    raw, status = {}, {}

    def add(flag, key, value):
        if not enabled.get(flag, True):
            raw[key] = None; status[key] = "disabled"; return
        raw[key] = value
        status[key] = "ok" if value is not None else "missing"

    add("bollinger", "bb_pctb", _score_bollinger_pctb(last))
    add("bb_width", "bb_width_pct", _score_bb_width_pctile(last))
    add("atr_pct", "atr_pct", _score_atr_pctile(last))
    add("keltner", "keltner_squeeze", _score_keltner_squeeze(last))

    return safe_mean(list(raw.values())), {k: (0.0 if v is None else v)
                                            for k, v in raw.items()}, status
