"""信号综合引擎 (Stage 2)。

1. aggregate_scores: 把 23 个指标子项聚合成 6 个类别分 ∈ [-2, +2]
2. regime.detect: 识别市场状态
3. 按 regime 权重矩阵加权求和得 total_score
4. total_score 映射到 Action + ATR-based SL/TP
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Literal

import pandas as pd

from indicators import aggregate_scores
from regime import detect as detect_regime, resolve_weights

Action = Literal["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]


@dataclass
class Signal:
    symbol: str
    timestamp: str
    price: float
    action: Action
    score: float
    regime: str
    regime_diag: dict
    category_scores: dict
    components: dict
    components_status: dict
    indicators: dict
    meta: dict
    stop_loss: float | None
    take_profit: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def _classify(score: float, thresholds: dict) -> Action:
    if score >= thresholds["strong_buy"]: return "STRONG_BUY"
    if score >= thresholds["buy"]: return "BUY"
    if score <= thresholds["strong_sell"]: return "STRONG_SELL"
    if score <= thresholds["sell"]: return "SELL"
    return "HOLD"


def generate(
    symbol: str,
    df_ind: pd.DataFrame,
    cfg: dict,
    df_1d: pd.DataFrame | None = None,
    meta: dict | None = None,
    meta_status: dict | None = None,
) -> Signal:
    if len(df_ind) < 2:
        raise ValueError("需要至少 2 根已计算指标的 K 线")

    meta = meta or {}
    meta_status = meta_status or {}

    cat_scores, components, status_from_ind = aggregate_scores(
        df_ind, df_1d, meta, cfg
    )
    # fetcher 状态优先 —— run.py 传入的 meta_status 覆盖 indicators 模块
    # 基于 meta 存在性判断的 status。
    merged_status = {**status_from_ind, **meta_status}

    regime, regime_diag = detect_regime(df_ind, cfg)
    weights = resolve_weights(regime, cfg)

    total_score = sum(cat_scores[k] * weights.get(k, 0.0) for k in cat_scores)
    action = _classify(total_score, cfg["thresholds"])

    last = df_ind.iloc[-1]
    price = float(last["close"])
    atr_val = float(last["atr"]) if not pd.isna(last.get("atr")) else 0.0

    if action in ("BUY", "STRONG_BUY"):
        stop_loss = price - 1.5 * atr_val
        take_profit = price + 3.0 * atr_val
    elif action in ("SELL", "STRONG_SELL"):
        stop_loss = price + 1.5 * atr_val
        take_profit = price - 3.0 * atr_val
    else:
        stop_loss = take_profit = None

    indicators_out = {
        "ema_fast": _r(last.get("ema_fast"), 4),
        "ema_slow": _r(last.get("ema_slow"), 4),
        "ema200": _r(last.get("ema200"), 4),
        "adx": _r(last.get("adx"), 2),
        "rsi": _r(last.get("rsi"), 2),
        "stoch_rsi_k": _r(last.get("stoch_rsi_k"), 2),
        "macd": _r(last.get("macd"), 5),
        "macd_hist": _r(last.get("macd_hist"), 5),
        "roc10": _r(last.get("roc10"), 3),
        "bb_upper": _r(last.get("bb_upper"), 4),
        "bb_lower": _r(last.get("bb_lower"), 4),
        "bb_width": _r(last.get("bb_width"), 5),
        "bb_width_pctile": _r(last.get("bb_width_pctile"), 1),
        "atr": _r(last.get("atr"), 4),
        "atr_pctile": _r(last.get("atr_pctile"), 1),
        "obv_slope": _r(last.get("obv_slope"), 4),
        "taker_buy_ratio": _r(last.get("taker_buy_ratio"), 3),
    }

    return Signal(
        symbol=symbol,
        timestamp=last.name.isoformat(),
        price=price,
        action=action,
        score=round(float(total_score), 3),
        regime=regime,
        regime_diag=regime_diag,
        category_scores={k: round(float(v), 3) for k, v in cat_scores.items()},
        components={k: round(float(v), 3) for k, v in components.items()},
        components_status=merged_status,
        indicators=indicators_out,
        meta={k: (round(v, 6) if isinstance(v, float) else v)
              for k, v in meta.items() if v is not None},
        stop_loss=round(stop_loss, 4) if stop_loss else None,
        take_profit=round(take_profit, 4) if take_profit else None,
    )


def _r(v, n: int):
    if v is None or pd.isna(v): return None
    return round(float(v), n)
