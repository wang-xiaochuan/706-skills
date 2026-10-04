"""主入口 (Stage 2):

抓 1H + 1D K 线 → 滚动 4H 合成 → 拉 meta(funding/OI/basis/LS/F&G)
  → compute_all(23 指标) → regime.detect → signal_engine.generate(类别聚合+动态权重)
  → 追加 JSON 日志 + 刷新每日 Markdown 日报
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from cache import Cache  # noqa: E402
from fetchers import fetch_and_synth  # noqa: E402
from fetchers.external import fetch_fear_greed  # noqa: E402
from fetchers.futures_meta import (  # noqa: E402
    fetch_basis, fetch_funding_rate, fetch_oi_change_24h,
)
from fetchers.klines import fetch_1d  # noqa: E402
from fetchers.sentiment_ls import (  # noqa: E402
    fetch_retail_ls_account, fetch_top_trader_ls_position,
)
from indicators import compute_all  # noqa: E402
from signal_engine import generate  # noqa: E402


def load_config(cfg_path: Path) -> dict:
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def fetch_shared_meta(cache: Cache, cfg: dict) -> tuple[dict, dict]:
    """跨符号共享的 meta (目前只有 F&G)。"""
    shared, status = {}, {}
    enabled = cfg["features_enabled"]
    ttl = cfg["cache"]["ttl"]
    if enabled.get("fear_greed"):
        v, s = cache.hit_or_fetch("fear_greed", ttl["fear_greed"], fetch_fear_greed)
        shared["fear_greed"] = v
        status["fear_greed"] = s
    else:
        status["fear_greed"] = "disabled"
    return shared, status


def fetch_symbol_meta(symbol: str, cache: Cache, cfg: dict) -> tuple[dict, dict]:
    """每个币对的微观 + 多空比 meta。"""
    enabled = cfg["features_enabled"]
    ttl = cfg["cache"]["ttl"]
    meta, status = {}, {}
    jobs = [
        ("funding", "funding_rate", ttl["funding"], lambda: fetch_funding_rate(symbol)),
        ("oi_change", "oi_change_24h", ttl["oi"], lambda: fetch_oi_change_24h(symbol)),
        ("basis", "basis", ttl["basis"], lambda: fetch_basis(symbol)),
        ("top_trader_ls", "top_trader_ls", ttl["top_ls"],
         lambda: fetch_top_trader_ls_position(symbol)),
        ("retail_ls", "retail_ls", ttl["retail_ls"],
         lambda: fetch_retail_ls_account(symbol)),
    ]
    for flag_key, meta_key, secs, fn in jobs:
        if not enabled.get(flag_key):
            status[flag_key] = "disabled"
            continue
        v, s = cache.hit_or_fetch(f"{flag_key}:{symbol}", secs, fn)
        meta[meta_key] = v
        status[flag_key] = s
    return meta, status


def fetch_1d_cached(symbol: str, cache: Cache, cfg: dict):
    """1D K 线走缓存,避免每小时都打 klines 接口。"""
    key = f"kline_1d:{symbol}:{cfg.get('fetch_1d_limit', 60)}"
    ttl = cfg["cache"]["ttl"]["kline_1d"]

    cached = cache.get(key)
    if cached is not None:
        import pandas as pd
        from io import StringIO
        df = pd.read_json(StringIO(cached["json"]), orient="split")
        df.index = pd.to_datetime(df.index, utc=True)
        return df, "cached"
    try:
        df = fetch_1d(symbol, limit=cfg.get("fetch_1d_limit", 60),
                      base_url=cfg["api"]["base_url"])
        cache.set(key, {"json": df.to_json(orient="split", date_format="iso")}, ttl)
        return df, "ok"
    except Exception as e:
        return None, f"error:{type(e).__name__}"


def run_once(symbols: list[str], cfg: dict) -> list[dict]:
    log_dir = ROOT / cfg["output"]["log_dir"]
    log_dir.mkdir(parents=True, exist_ok=True)
    cache = Cache(ROOT / cfg["cache"]["db_path"])
    shared_meta, shared_status = fetch_shared_meta(cache, cfg)

    results = []
    for sym in symbols:
        try:
            _, df_4h = fetch_and_synth(
                sym,
                limit=cfg["fetch_limit"],
                window=cfg["synth_window"],
                base_url=cfg["api"]["base_url"],
            )
            df_1d, d1_status = fetch_1d_cached(sym, cache, cfg)

            sym_meta, sym_status = fetch_symbol_meta(sym, cache, cfg)
            meta = {**sym_meta, **shared_meta}
            status = {**sym_status, **shared_status, "kline_1d": d1_status}

            df_ind = compute_all(df_4h, None, df_1d, cfg).dropna(subset=["ema_fast", "rsi"])
            sig = generate(sym, df_ind, cfg, df_1d=df_1d, meta=meta, meta_status=status)

            results.append(sig.to_dict())
            cat = sig.category_scores
            print(
                f"[{sym}] {sig.action:<11} score={sig.score:+.2f}  "
                f"regime={sig.regime:<14} "
                f"T{cat['trend']:+.2f} M{cat['momentum']:+.2f} "
                f"V{cat['volatility']:+.2f} Vol{cat['volume']:+.2f} "
                f"Mi{cat['microstructure']:+.2f} S{cat['sentiment']:+.2f}  "
                f"price={sig.price}"
            )
        except Exception as e:
            print(f"[{sym}] ERROR: {e}", file=sys.stderr)
            results.append({"symbol": sym, "error": str(e),
                            "timestamp": datetime.now(timezone.utc).isoformat()})

    cache.close()
    return results


def append_log(results: list[dict], log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = log_dir / f"signals_{today}.json"
    existing = []
    if log_file.exists():
        existing = json.loads(log_file.read_text(encoding="utf-8"))
    existing.append({
        "run_at": datetime.now(timezone.utc).isoformat(),
        "signals": results,
    })
    log_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    return log_file


def build_daily_report(log_dir: Path, date_str: str | None = None) -> Path:
    today = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_file = log_dir / f"signals_{today}.json"
    if not log_file.exists():
        raise FileNotFoundError(f"No signals log for {today}")

    runs = json.loads(log_file.read_text(encoding="utf-8"))
    per_symbol: dict[str, list[dict]] = {}
    source_health: Counter = Counter()
    regime_total: Counter = Counter()

    for run in runs:
        for s in run["signals"]:
            if "error" in s:
                continue
            sym = s["symbol"]
            per_symbol.setdefault(sym, []).append({
                "time": run["run_at"],
                "action": s["action"],
                "score": s["score"],
                "price": s["price"],
                "regime": s.get("regime", "unknown"),
                "category_scores": s.get("category_scores", {}),
            })
            for src, st in (s.get("components_status") or {}).items():
                key = f"{src}:{st.split(':')[0]}" if st.startswith("error") else f"{src}:{st}"
                source_health[key] += 1
            regime_total[s.get("regime", "unknown")] += 1

    lines = [f"# Binance 4H 信号日报 · {today} UTC\n"]

    if regime_total:
        lines += ["## Regime 分布(全部币对合计)", ""]
        total = sum(regime_total.values())
        for r, n in regime_total.most_common():
            lines.append(f"- **{r}** : {n} 次 ({n/total*100:.0f}%)")
        lines.append("")

    for sym, entries in per_symbol.items():
        lines.append(f"## {sym}\n")
        scores = [e["score"] for e in entries]
        actions = [e["action"] for e in entries]
        regimes = Counter(e["regime"] for e in entries)
        cnt = Counter(actions)
        dist = " · ".join(f"{a}:{n}" for a, n in cnt.most_common())
        reg_dist = " · ".join(f"{r}:{n}" for r, n in regimes.most_common())
        lines += [
            f"- 运行次数: **{len(entries)}** · 最近 regime: **{entries[-1]['regime']}**",
            f"- 平均综合分: **{sum(scores)/len(scores):+.2f}** · 最高/最低: {max(scores):+.2f} / {min(scores):+.2f}",
            f"- 信号分布: {dist}",
            f"- Regime 分布: {reg_dist}",
            f"- 末次价: {entries[-1]['price']} @ {entries[-1]['time']}",
            "",
            "| UTC 时间 | Action | Score | Regime | Trend | Mom | Vol | VolFlow | Micro | Sent | Price |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for e in entries[-24:]:
            cs = e["category_scores"]
            lines.append(
                f"| {e['time'][:16]} | {e['action']} | {e['score']:+.2f} | "
                f"{e['regime']} | {cs.get('trend', 0):+.2f} | {cs.get('momentum', 0):+.2f} | "
                f"{cs.get('volatility', 0):+.2f} | {cs.get('volume', 0):+.2f} | "
                f"{cs.get('microstructure', 0):+.2f} | {cs.get('sentiment', 0):+.2f} | "
                f"{e['price']} |"
            )
        lines.append("")

    if source_health:
        lines += ["## 数据源健康度", "", "| 源:状态 | 次数 |", "|---|---|"]
        for key, n in source_health.most_common():
            lines.append(f"| {key} | {n} |")
        lines.append("")

    report_file = log_dir / f"daily_{today}.md"
    report_file.write_text("\n".join(lines), encoding="utf-8")
    return report_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default=None, help="逗号分隔,例 BTCUSDT,ETHUSDT")
    parser.add_argument("--config", default=str(ROOT / "config.json"))
    parser.add_argument("--daily-only", action="store_true")
    parser.add_argument("--daily-for", default=None, help="指定日期 YYYY-MM-DD")
    parser.add_argument("--compare", type=int, default=0, metavar="N",
                        help="跑一次 + 打印最近 N 次(含当次)的横向对比")
    parser.add_argument("--compare-only", type=int, default=0, metavar="N",
                        help="不跑,只打印最近 N 次的横向对比")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    log_dir = ROOT / cfg["output"]["log_dir"]

    if args.daily_only or args.daily_for:
        report = build_daily_report(log_dir, args.daily_for)
        print(f"日报已生成: {report}")
        return

    symbols = ([s.strip().upper() for s in args.symbols.split(",")]
               if args.symbols else cfg["symbols"])

    if args.compare_only > 0:
        from compare import build_comparison
        print(build_comparison(log_dir, last_n=args.compare_only, symbols=symbols))
        return

    results = run_once(symbols, cfg)
    log_file = append_log(results, log_dir)
    print(f"日志追加: {log_file}")

    try:
        report = build_daily_report(log_dir)
        print(f"日报更新: {report}")
    except FileNotFoundError:
        pass

    if args.compare > 0:
        from compare import build_comparison
        print()
        print(build_comparison(log_dir, last_n=args.compare, symbols=symbols))


if __name__ == "__main__":
    main()
