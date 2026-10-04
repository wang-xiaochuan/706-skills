"""趋势类指标:EMA 快慢线 + EMA200 位置 + ADX + 1D HTF 对齐。"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ._base import ema, true_range, clip_score, safe_mean


def compute(df_4h: pd.DataFrame, df_1h: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """在 df_4h 上附加趋势指标列。"""
    out = df_4h.copy()
    ic = cfg["indicators"]
    out["ema_fast"] = ema(out["close"], ic["ema_fast"])
    out["ema_slow"] = ema(out["close"], ic["ema_slow"])
    out["ema200"] = ema(out["close"], 200) if len(out) >= 50 else np.nan
    out["adx"] = _adx(out, period=14)
    return out


def _adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Welles Wilder ADX。"""
    high, low = df["high"], df["low"]
    up = high.diff()
    down = -low.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    tr = true_range(df)
    atr_s = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(
        alpha=1 / period, adjust=False).mean() / atr_s.replace(0, np.nan)
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(
        alpha=1 / period, adjust=False).mean() / atr_s.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False).mean()


# ───────── 子指标评分 ─────────

def _score_ema_cross(last: pd.Series, prev: pd.Series) -> float:
    diff = last["ema_fast"] - last["ema_slow"]
    diff_pct = diff / last["close"]
    score = 1.0 if diff > 0 else -1.0
    prev_diff = prev["ema_fast"] - prev["ema_slow"]
    if prev_diff <= 0 < diff: score += 1.0
    elif prev_diff >= 0 > diff: score -= 1.0
    if abs(diff_pct) > 0.01: score *= 1.2
    return clip_score(score)


def _score_ema200_position(last: pd.Series) -> float | None:
    e200 = last.get("ema200")
    if e200 is None or pd.isna(e200): return None
    diff_pct = (last["close"] - e200) / last["close"]
    if diff_pct > 0.05: return 2.0
    if diff_pct > 0.01: return 1.0
    if diff_pct < -0.05: return -2.0
    if diff_pct < -0.01: return -1.0
    return 0.0


def _score_adx(last: pd.Series, prev: pd.Series) -> float | None:
    """ADX 本身非方向性,结合 EMA 快慢方向给出"趋势强度加权"。"""
    adx = last.get("adx")
    if adx is None or pd.isna(adx): return None
    direction = 1.0 if last["ema_fast"] > last["ema_slow"] else -1.0
    if adx > 30: return direction * 2.0
    if adx > 25: return direction * 1.0
    if adx < 15: return 0.0
    return direction * 0.3


def _score_htf_alignment(df_1d: pd.DataFrame | None) -> float | None:
    """日 K 线 EMA50 方向。最近 10 天对比 10 天前的 EMA50。"""
    if df_1d is None or len(df_1d) < 20:
        return None
    e50 = ema(df_1d["close"], 50) if len(df_1d) >= 50 else df_1d["close"].rolling(20).mean()
    latest = e50.iloc[-1]
    past = e50.iloc[-10] if len(e50) >= 10 else e50.iloc[0]
    if pd.isna(latest) or pd.isna(past) or past == 0:
        return None
    slope = (latest - past) / past
    if slope > 0.03: return 2.0
    if slope > 0.005: return 1.0
    if slope < -0.03: return -2.0
    if slope < -0.005: return -1.0
    return 0.0


def score(df_ind: pd.DataFrame, df_1d: pd.DataFrame | None, cfg: dict
          ) -> tuple[float, dict, dict]:
    """返回 (类别分, 子项分, 子项状态)。类别分 = 有效子项等权平均 clip 到 [-2, +2]。"""
    enabled = cfg.get("features_enabled", {})
    last, prev = df_ind.iloc[-1], df_ind.iloc[-2]

    raw = {}
    status = {}

    def add(flag: str, key: str, value: float | None):
        if not enabled.get(flag, True):
            raw[key] = None
            status[key] = "disabled"
            return
        raw[key] = value
        status[key] = "ok" if value is not None else "missing"

    add("ema_cross", "ema_cross", _score_ema_cross(last, prev))
    add("ema200", "ema200", _score_ema200_position(last))
    add("adx", "adx", _score_adx(last, prev))
    add("htf_align", "htf_align", _score_htf_alignment(df_1d))

    return safe_mean(list(raw.values())), {k: (0.0 if v is None else v)
                                            for k, v in raw.items()}, status
