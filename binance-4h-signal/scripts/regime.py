"""市场状态识别 (Regime Detection)。

基于 ADX(趋势强度) + BB Width 百分位 + EMA 快慢方向,把市场分为:
- trending_up   : ADX>阈值 且 EMA_fast>EMA_slow
- trending_down : ADX>阈值 且 EMA_fast<EMA_slow
- ranging       : ADX<阈值 且 BB Width 百分位低
- unknown       : 介于上述之间,实际按 ranging 应用权重,但记录原貌

regime 决定后续权重矩阵,让趋势市放大 trend/momentum,震荡市放大 volatility/microstructure。
"""
from __future__ import annotations

from typing import Literal

import pandas as pd

Regime = Literal["trending_up", "trending_down", "ranging", "unknown"]


def detect(df_ind: pd.DataFrame, cfg: dict) -> tuple[Regime, dict]:
    """返回 (regime, diag)。diag 含 adx / bbw_pctile / atr_pctile 当前值,供输出引用。"""
    last = df_ind.iloc[-1]
    adx = last.get("adx")
    bbw_pct = last.get("bb_width_pctile")
    atr_pct = last.get("atr_pctile")
    ema_f, ema_s = last.get("ema_fast"), last.get("ema_slow")

    r_cfg = cfg.get("regime", {})
    adx_trend_th = r_cfg.get("adx_trend_th", 25)
    adx_range_th = r_cfg.get("adx_range_th", 20)
    bbw_range_th = r_cfg.get("bbw_range_pctile", 30)

    diag = {
        "adx": None if adx is None or pd.isna(adx) else round(float(adx), 2),
        "bbw_pctile": None if bbw_pct is None or pd.isna(bbw_pct) else round(float(bbw_pct), 1),
        "atr_pctile": None if atr_pct is None or pd.isna(atr_pct) else round(float(atr_pct), 1),
        "ema_fast_gt_slow": bool(ema_f > ema_s) if ema_f is not None and ema_s is not None else None,
    }

    if adx is None or pd.isna(adx):
        return "unknown", diag

    if adx > adx_trend_th:
        if ema_f is None or pd.isna(ema_f) or ema_s is None or pd.isna(ema_s):
            return "unknown", diag
        return ("trending_up", diag) if ema_f > ema_s else ("trending_down", diag)

    if adx < adx_range_th and bbw_pct is not None and not pd.isna(bbw_pct) and bbw_pct < bbw_range_th:
        return "ranging", diag

    return "unknown", diag


def resolve_weights(regime: Regime, cfg: dict) -> dict:
    """unknown regime 按 ranging 应用权重,但分类仍保留为 unknown。"""
    key = "ranging" if regime == "unknown" else regime
    return cfg["weights_by_regime"][key]
