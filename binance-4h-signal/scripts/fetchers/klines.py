"""Binance 公开 K 线抓取 —— 无需 API Key。"""
from __future__ import annotations

import time

import pandas as pd
import requests

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "trades",
    "taker_buy_base", "taker_buy_quote", "ignore",
]

_NUMERIC = ["open", "high", "low", "close", "volume",
            "quote_volume", "taker_buy_base", "taker_buy_quote"]

_OUT_COLS = ["open", "high", "low", "close", "volume", "taker_buy_base", "close_time"]


def fetch_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 200,
    base_url: str = "https://api.binance.com",
    timeout: int = 10,
    retries: int = 3,
) -> pd.DataFrame:
    """拉取最近 N 根 K 线，返回索引为 UTC open_time 的 OHLCV(+taker_buy_base) DataFrame。"""
    url = f"{base_url}/api/v3/klines"
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            resp.raise_for_status()
            raw = resp.json()
            break
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(1.5 ** attempt)
    else:
        raise RuntimeError(f"Binance API failed after {retries} retries: {last_err}")

    df = pd.DataFrame(raw, columns=KLINE_COLUMNS)
    df[_NUMERIC] = df[_NUMERIC].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    df = df.set_index("open_time")
    return df[_OUT_COLS]


def fetch_1d(
    symbol: str,
    limit: int = 60,
    base_url: str = "https://api.binance.com",
) -> pd.DataFrame:
    """拉取日 K 线,常用于计算 HTF EMA50 方向。"""
    return fetch_klines(symbol, interval="1d", limit=limit, base_url=base_url)


def synthesize_rolling(df_1h: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    """把 1H OHLCV 滚动合成"滚动 4H"——每根 = 过去 window 根 1H。

    与普通 resample("4H") 不同:这里是滑动窗口,每小时都产出一根新的"滚动 4H",
    使 4H 级指标能以 1H 频率刷新。
    """
    if len(df_1h) < window:
        raise ValueError(f"需要至少 {window} 根 1H K 线，实际 {len(df_1h)}")

    out = pd.DataFrame(index=df_1h.index)
    out["open"] = df_1h["open"].shift(window - 1)
    out["high"] = df_1h["high"].rolling(window).max()
    out["low"] = df_1h["low"].rolling(window).min()
    out["close"] = df_1h["close"]
    out["volume"] = df_1h["volume"].rolling(window).sum()
    if "taker_buy_base" in df_1h.columns:
        out["taker_buy_base"] = df_1h["taker_buy_base"].rolling(window).sum()
    return out.dropna()


def fetch_and_synth(
    symbol: str,
    limit: int = 200,
    window: int = 4,
    base_url: str = "https://api.binance.com",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """一步到位:拉 1H + 合成滚动 4H。返回 (df_1h, df_roll4h)。"""
    df_1h = fetch_klines(symbol, "1h", limit, base_url)
    df_roll4h = synthesize_rolling(df_1h, window)
    return df_1h, df_roll4h


if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    df_1h, df_4h = fetch_and_synth(sym, limit=50)
    print(f"[1H] 最近 3 根 {sym}")
    print(df_1h.tail(3))
    print(f"\n[滚动 4H] 最近 3 根 {sym}")
    print(df_4h.tail(3))
