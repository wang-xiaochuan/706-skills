"""动能类:MACD, RSI, Stoch RSI, ROC。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ._base import ema, rsi_wilder, clip_score, safe_mean


def compute(df_4h: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = df_4h.copy()
    ic = cfg["indicators"]
    macd_line = ema(out["close"], ic["macd_fast"]) - ema(out["close"], ic["macd_slow"])
    signal_line = ema(macd_line, ic["macd_signal"])
    out["macd"] = macd_line
    out["macd_signal_line"] = signal_line
    out["macd_hist"] = macd_line - signal_line

    out["rsi"] = rsi_wilder(out["close"], ic["rsi_period"])
    out[["stoch_rsi_k", "stoch_rsi_d"]] = _stoch_rsi(out["rsi"]).values
    out["roc10"] = out["close"].pct_change(10) * 100.0
    return out


def _stoch_rsi(rsi: pd.Series, period: int = 14, k: int = 3, d: int = 3) -> pd.DataFrame:
    min_rsi = rsi.rolling(period).min()
    max_rsi = rsi.rolling(period).max()
    stoch = 100 * (rsi - min_rsi) / (max_rsi - min_rsi).replace(0, np.nan)
    k_line = stoch.rolling(k).mean()
    d_line = k_line.rolling(d).mean()
    return pd.DataFrame({"k": k_line, "d": d_line})


# ───────── 评分 ─────────

def _score_macd(last: pd.Series, prev: pd.Series) -> float:
    score = 0.0
    score += 0.5 if last["macd"] > last["macd_signal_line"] else -0.5
    score += 0.5 if last["macd_hist"] > prev["macd_hist"] else -0.5
    if prev["macd"] <= 0 < last["macd"]: score += 1.0
    elif prev["macd"] >= 0 > last["macd"]: score -= 1.0
    return clip_score(score)


def _score_rsi(last: pd.Series, cfg: dict) -> float:
    r = last["rsi"]
    ic = cfg["indicators"]
    if r < ic["rsi_oversold"]: return 2.0
    if r < 40: return 1.0
    if r > ic["rsi_overbought"]: return -2.0
    if r > 60: return -1.0
    return 0.0


def _score_stoch_rsi(last: pd.Series, prev: pd.Series) -> float | None:
    k, d = last.get("stoch_rsi_k"), last.get("stoch_rsi_d")
    pk, pd_ = prev.get("stoch_rsi_k"), prev.get("stoch_rsi_d")
    if any(pd.isna(v) for v in [k, d, pk, pd_]):
        return None
    score = 0.0
    if k < 20 and d < 20: score += 1.0
    if k > 80 and d > 80: score -= 1.0
    if pk <= pd_ < k > d: score += 1.0   # 刚金叉(低位加分)
    if pk >= pd_ > k < d: score -= 1.0   # 刚死叉
    return clip_score(score)


def _score_roc(last: pd.Series) -> float | None:
    r = last.get("roc10")
    if r is None or pd.isna(r): return None
    if r > 8: return 2.0
    if r > 3: return 1.0
    if r < -8: return -2.0
    if r < -3: return -1.0
    return 0.0


def score(df_ind: pd.DataFrame, cfg: dict) -> tuple[float, dict, dict]:
    enabled = cfg.get("features_enabled", {})
    last, prev = df_ind.iloc[-1], df_ind.iloc[-2]
    raw, status = {}, {}

    def add(flag, key, value):
        if not enabled.get(flag, True):
            raw[key] = None; status[key] = "disabled"; return
        raw[key] = value
        status[key] = "ok" if value is not None else "missing"

    add("macd", "macd", _score_macd(last, prev))
    add("rsi", "rsi", _score_rsi(last, cfg))
    add("stoch_rsi", "stoch_rsi", _score_stoch_rsi(last, prev))
    add("roc", "roc", _score_roc(last))

    return safe_mean(list(raw.values())), {k: (0.0 if v is None else v)
                                            for k, v in raw.items()}, status
