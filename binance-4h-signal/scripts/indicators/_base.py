"""共享的底层指标原语。所有类别模块共用这些低层函数。"""
from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(period).mean()


def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI。"""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)


def atr_wilder(df: pd.DataFrame, period: int = 14) -> pd.Series:
    return true_range(df).ewm(alpha=1 / period, adjust=False).mean()


def percentile_rank(series: pd.Series, window: int = 100) -> pd.Series:
    """最近 window 根里,当前值的百分位 (0-100)。"""
    return series.rolling(window, min_periods=max(10, window // 4)).apply(
        lambda x: (x.rank(pct=True).iloc[-1]) * 100.0,
        raw=False,
    )


def clip_score(value: float, lo: float = -2.0, hi: float = 2.0) -> float:
    return float(np.clip(value, lo, hi))


def safe_mean(values: list[float | None]) -> float:
    """忽略 None,求平均。全部 None 则返回 0.0。"""
    present = [v for v in values if v is not None]
    if not present:
        return 0.0
    return float(np.clip(sum(present) / len(present), -2.0, 2.0))
