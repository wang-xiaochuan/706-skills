"""量价类:Volume/MA20, OBV Trend, Taker Buy Ratio。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ._base import sma, clip_score, safe_mean


def compute(df_4h: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = df_4h.copy()
    out["vol_ma"] = sma(out["volume"], 20)
    out["obv"] = _obv(out)
    out["obv_slope"] = out["obv"].diff(10) / out["obv"].abs().rolling(10).mean().replace(0, np.nan)
    if "taker_buy_base" in out.columns:
        out["taker_buy_ratio"] = out["taker_buy_base"] / out["volume"].replace(0, np.nan)
    return out


def _obv(df: pd.DataFrame) -> pd.Series:
    direction = np.sign(df["close"].diff()).fillna(0)
    return (direction * df["volume"]).cumsum()


# ───────── 评分 ─────────

def _score_volume(last: pd.Series, prev: pd.Series) -> float | None:
    vol_ma = last.get("vol_ma")
    if vol_ma is None or pd.isna(vol_ma) or vol_ma == 0:
        return None
    ratio = last["volume"] / vol_ma
    price_up = last["close"] > prev["close"]
    if ratio > 1.5 and price_up: return 2.0
    if ratio > 1.2 and price_up: return 1.0
    if ratio > 1.5 and not price_up: return -2.0
    if ratio > 1.2 and not price_up: return -1.0
    return 0.0


def _score_obv_trend(last: pd.Series) -> float | None:
    slope = last.get("obv_slope")
    if slope is None or pd.isna(slope): return None
    if slope > 0.15: return 1.5
    if slope > 0.05: return 0.8
    if slope < -0.15: return -1.5
    if slope < -0.05: return -0.8
    return 0.0


def _score_taker_buy_ratio(last: pd.Series) -> float | None:
    """taker_buy_base / volume。>0.55 买盘主动,<0.45 卖盘主动。"""
    r = last.get("taker_buy_ratio")
    if r is None or pd.isna(r): return None
    if r > 0.60: return 2.0
    if r > 0.55: return 1.0
    if r < 0.40: return -2.0
    if r < 0.45: return -1.0
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

    add("volume", "volume", _score_volume(last, prev))
    add("obv", "obv", _score_obv_trend(last))
    add("taker_ratio", "taker_ratio", _score_taker_buy_ratio(last))

    return safe_mean(list(raw.values())), {k: (0.0 if v is None else v)
                                            for k, v in raw.items()}, status
