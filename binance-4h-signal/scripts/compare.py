"""跨次运行对比 —— 读取最近 N 次的 run_record,输出横向对比。

用法:
    from compare import build_comparison
    print_text = build_comparison(log_dir, last_n=5, symbols=None)

主程序里被 run.py --compare / --compare-only 调用。
"""
from __future__ import annotations

import json
from pathlib import Path

CATEGORY_KEYS = ["trend", "momentum", "volatility",
                 "volume", "microstructure", "sentiment"]


def _load_recent_runs(log_dir: Path, last_n: int) -> list[dict]:
    """从最近的 signals_YYYY-MM-DD.json 里倒着取 last_n 条 run_record。
    自动跨日期(如果今天不够,往前取昨天)。"""
    files = sorted(log_dir.glob("signals_*.json"), reverse=True)
    runs: list[dict] = []
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        runs = list(data) + runs
        if len(runs) >= last_n:
            break
    return runs[-last_n:] if len(runs) >= last_n else runs


def _arrow(delta: float) -> str:
    if delta > 0.15: return "↗"
    if delta < -0.15: return "↘"
    return "→"


def build_comparison(log_dir: Path, last_n: int = 5,
                     symbols: list[str] | None = None) -> str:
    """返回一个多行字符串,展示最近 N 次每个币对的信号演变。"""
    runs = _load_recent_runs(log_dir, last_n)
    if not runs:
        return "(没有历史记录,先跑一次 run.py)"

    per_symbol: dict[str, list[dict]] = {}
    for r in runs:
        for s in r.get("signals", []):
            if "error" in s: continue
            sym = s["symbol"]
            if symbols and sym not in symbols: continue
            per_symbol.setdefault(sym, []).append({
                "time": r["run_at"][:16],
                "action": s["action"],
                "score": s["score"],
                "regime": s.get("regime", "unknown"),
                "category_scores": s.get("category_scores", {}),
                "price": s["price"],
                "components": s.get("components", {}),
            })

    lines = [f"# 跨次对比 · 最近 {len(runs)} 次 · "
             f"{runs[0]['run_at'][:16]} → {runs[-1]['run_at'][:16]}\n"]

    for sym, entries in per_symbol.items():
        if len(entries) < 1: continue
        lines.append(f"## {sym}")
        lines.append("")
        lines.append("| UTC 时间 | Action | Score | Regime | "
                     "Trend | Mom | Vol | VolFlow | Micro | Sent | Price |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for e in entries:
            cs = e["category_scores"]
            lines.append(
                f"| {e['time']} | {e['action']} | {e['score']:+.2f} | "
                f"{e['regime']} | "
                f"{cs.get('trend', 0):+.2f} | {cs.get('momentum', 0):+.2f} | "
                f"{cs.get('volatility', 0):+.2f} | {cs.get('volume', 0):+.2f} | "
                f"{cs.get('microstructure', 0):+.2f} | {cs.get('sentiment', 0):+.2f} | "
                f"{e['price']} |"
            )
        # 末次相对前一次 + 相对首次的变化
        if len(entries) >= 2:
            last, prev = entries[-1], entries[-2]
            first = entries[0]
            d1_score = last["score"] - prev["score"]
            dN_score = last["score"] - first["score"]
            d1_price_pct = (last["price"] - prev["price"]) / prev["price"] * 100 if prev["price"] else 0
            dN_price_pct = (last["price"] - first["price"]) / first["price"] * 100 if first["price"] else 0
            lines += [
                "",
                f"**变化**(末次 vs 前次 / 末次 vs 首次):",
                f"- Score: {_arrow(d1_score)} {d1_score:+.2f}  /  "
                f"{_arrow(dN_score)} {dN_score:+.2f}",
                f"- Price: {_arrow(d1_price_pct/5)} {d1_price_pct:+.2f}%  /  "
                f"{_arrow(dN_price_pct/5)} {dN_price_pct:+.2f}%",
            ]
            # 类别分变化(末次 vs 前次)
            cat_deltas = []
            for k in CATEGORY_KEYS:
                d = last["category_scores"].get(k, 0) - prev["category_scores"].get(k, 0)
                if abs(d) >= 0.3:
                    cat_deltas.append(f"{k} {_arrow(d)} {d:+.2f}")
            if cat_deltas:
                lines.append(f"- 类别变化(|Δ|≥0.3): {' · '.join(cat_deltas)}")
            # regime 变化
            if last["regime"] != prev["regime"]:
                lines.append(f"- ⚠️ Regime 切换: `{prev['regime']}` → `{last['regime']}`")
        lines.append("")

    return "\n".join(lines)
