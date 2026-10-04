"""指标聚合入口。

用法:
    df_ind = compute_all(df_4h, df_1h, df_1d, cfg)
    cat_scores, components, status = aggregate_scores(df_ind, df_1d, meta, cfg)
"""
from __future__ import annotations

import pandas as pd

from . import microstructure, momentum, sentiment, trend, volatility, volume

__all__ = ["compute_all", "aggregate_scores"]


def compute_all(
    df_4h: pd.DataFrame,
    df_1h: pd.DataFrame,
    df_1d: pd.DataFrame | None,
    cfg: dict,
) -> pd.DataFrame:
    """把所有序列级指标附加到 df_4h 的副本上并返回。

    链式调用:每个类别 compute 都接收/返回一个 DataFrame 副本,列单调增加。
    df_1d 目前只用于 HTF 评分,不落到序列里,所以 compute_all 不消费它。
    """
    out = trend.compute(df_4h, df_1h, cfg)
    out = momentum.compute(out, cfg)
    out = volatility.compute(out, cfg)
    out = volume.compute(out, cfg)
    return out


def aggregate_scores(
    df_ind: pd.DataFrame,
    df_1d: pd.DataFrame | None,
    meta: dict,
    cfg: dict,
) -> tuple[dict, dict, dict]:
    """返回 (category_scores, components_flat, components_status)。

    - category_scores: {"trend": X, "momentum": X, ...} ∈ [-2, +2]
    - components_flat: 所有子项名 → 分值(便于审计和可解释)
    - components_status: 所有子项名 → 状态("ok"/"missing"/"disabled"/"error:...")
    """
    cat_scores, flat, status = {}, {}, {}

    callers = [
        ("trend", lambda: trend.score(df_ind, df_1d, cfg)),
        ("momentum", lambda: momentum.score(df_ind, cfg)),
        ("volatility", lambda: volatility.score(df_ind, cfg)),
        ("volume", lambda: volume.score(df_ind, cfg)),
        ("microstructure", lambda: microstructure.score(meta, cfg)),
        ("sentiment", lambda: sentiment.score(meta, cfg)),
    ]
    for name, call in callers:
        try:
            cat, comp, st = call()
        except Exception as e:
            cat_scores[name] = 0.0
            status[f"{name}:category"] = f"error:{type(e).__name__}"
            continue
        cat_scores[name] = cat
        flat.update(comp)
        status.update(st)

    return cat_scores, flat, status
