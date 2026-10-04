#!/usr/bin/env python3
"""Gate B: validate the Layer-2 rhetoric (topic sentences + bullet moves).

Usage:
    python3 check_moves.py <harness-root>

Rule revisions applied (2026-09-15, see CHANGELOG):
    R1  traceability may live in evidence/register.csv (trace_mode: appendix)
    R2  `disclaimer` is a framing move allowed before evidence (prolepsis)
    R3  consecutive Evidence satellites are allowed up to MAX_RUN
    R4  a section may declare `type: method`; a missing turn is then a warning

Exit code 0 = PASS, 1 = FAIL, 2 = usage/missing files.
"""

from __future__ import annotations

import argparse
import csv
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (  # noqa: E402
    DEFAULT_MAX_RUN,
    MAX_RUN,
    MOVE_KINDS,
    TRACE_RE,
    Checker,
    han,
    load_architecture,
    load_evidence_register,
    max_run,
    parse_section_file,
)

CLAIM_MAX = 40
BUDGET_TOLERANCE = 0.15
METHOD_TYPES = {"method", "list"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate B for rhetorical-structure-harness")
    parser.add_argument("root", help="harness root directory containing sections/*.md")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    sections_dir = root / "sections"
    if not sections_dir.is_dir():
        print(f"sections/ not found under {root}", file=sys.stderr)
        return 2

    files = sorted(p for p in sections_dir.glob("*.md") if not p.name.startswith("_"))
    if not files:
        print(f"no section files under {sections_dir}", file=sys.stderr)
        return 2

    header, arch_sections = load_architecture(root)
    trace_mode = ((header or {}).get("trace_mode") or "appendix").strip().lower()
    register = load_evidence_register(root)

    arch_budget = {}
    for section in arch_sections or []:
        try:
            arch_budget[int(section["id"])] = int((section.get("budget_chars") or "0").strip())
        except (KeyError, ValueError):
            continue

    checker = Checker(f"Gate B · rhetoric · {root.name}")

    parsed = []
    for path in files:
        sinfo, moves = parse_section_file(path)
        if sinfo is None:
            checker.need(False, f"{path.name}: 缺少 SECTION 数据行")
            continue
        try:
            sid = int((sinfo.get("id") or "").strip())
        except ValueError:
            checker.need(False, f"{path.name}: id 不是整数")
            continue
        parsed.append((sid, path, sinfo, moves or []))

    if not parsed:
        return checker.report()

    first_id = min(sid for sid, *_ in parsed)
    call_total = sum(1 for _, _, _, moves in parsed for m in moves if m["kind"] == "call")
    checker.need(call_total <= 2, f"B7 `call` 全场 {call_total} 次，超过 2 次（Monroe：两个 call 等于没有 call）")

    # R1: appendix mode needs a register, otherwise inline markers are mandatory
    if trace_mode == "appendix":
        if register is None:
            checker.warn(
                False,
                "B9 trace_mode=appendix 但缺少 evidence/register.csv；"
                "本轮按 inline 标准检查 evidence 可追溯性",
            )
            trace_mode = "inline"
        else:
            checker.note(f"B9 trace_mode=appendix：已加载 evidence/register.csv（{len(register)} 条来源）")
    else:
        checker.note("B9 trace_mode=inline：每条 evidence 需带文件名 / URL / [E:ID]")

    for sid, path, sinfo, moves in sorted(parsed):
        label = f"第 {sid} 节（{path.name}）"
        stype = (sinfo.get("type") or "argument").strip().lower()

        claim = (sinfo.get("claim") or "").strip()
        checker.need(claim, f"B1 {label} claim 为空")
        if claim:
            checker.need(
                han(claim) <= CLAIM_MAX,
                f"B1 {label} claim 为 {han(claim)} 字，超过 {CLAIM_MAX} 字（Grice 量准则 / Toulmin 单一 claim）",
            )
        checker.need(sid in arch_budget, f"B1 {label} 在 architecture.md 中没有对应节 id")

        if not moves:
            checker.need(False, f"B3 {label} 没有任何 move")
            continue

        kinds = [m["kind"] for m in moves]
        unknown = [k for k in kinds if k not in MOVE_KINDS]
        checker.need(not unknown, f"B2 {label} 未知 move：{', '.join(sorted(set(unknown)))}")

        # B3 required moves (R4: method/list sections may omit turn)
        for required, rule in [("anchor", "≥1"), ("stake", "≥1"), ("restate", "≥1")]:
            checker.need(kinds.count(required) >= 1, f"B3 {label} `{required}` 数量 {kinds.count(required)}，要求 {rule}")

        turn_count = kinds.count("turn")
        if stype in METHOD_TYPES:
            checker.warn(turn_count <= 1, f"B3 {label} type={stype} 但 turn 有 {turn_count} 条，上限 1")
            checker.warn(turn_count >= 1, f"B3 {label} type={stype} 无 turn：本节只告知，不推动听众（已按 R4 降级）")
        else:
            checker.need(turn_count == 1, f"B3 {label} `turn` 数量 {turn_count}，要求 恰好 1")

        # B4 evidence implies mechanism and limit
        if "evidence" in kinds:
            checker.need("mechanism" in kinds, f"B4 {label} 有 evidence 但无 mechanism（Toulmin：data 需 warrant）")
            checker.need(
                "limit" in kinds,
                f"B4 {label} 有 evidence 但无 limit（Toulmin：claim 的 qualifier 不可省；"
                "开场预驳请用 `disclaimer`）",
            )

        # B5 evidence before limit (disclaimer is exempt — R2)
        evidence_idx = [i for i, k in enumerate(kinds) if k == "evidence"]
        limit_idx = [i for i, k in enumerate(kinds) if k == "limit"]
        if evidence_idx and limit_idx:
            checker.need(
                min(evidence_idx) < min(limit_idx),
                f"B5 {label} limit 出现在首条 evidence 之前（claim 的限定应先立后限）",
            )

        # B6 turn in first half
        if "turn" in kinds:
            turn_pos = kinds.index("turn") + 1
            half = math.ceil(len(kinds) / 2)
            checker.need(
                turn_pos <= half,
                f"B6 {label} turn 在第 {turn_pos}/{len(kinds)} 条，落在后半段（应在前半段）",
            )

        # B7 runs, frame cap, call placement (R3)
        for kind in set(kinds):
            allowed = MAX_RUN.get(kind, DEFAULT_MAX_RUN)
            run = max_run(kinds, kind)
            checker.need(
                run <= allowed,
                f"B7 {label} `{kind}` 连续出现 {run} 次，上限 {allowed}"
                + ("（RST 允许多个 Evidence satellite 连续）" if kind == "evidence" else ""),
            )
        checker.need(kinds.count("frame") <= 1, f"B7 {label} frame 出现 {kinds.count('frame')} 次，上限 1")
        if sid == first_id:
            checker.need("call" not in kinds, f"B7 {label} 第一节不得出现 call")

        # B8 spoken budget
        budget = arch_budget.get(sid) or 0
        if not budget:
            try:
                budget = int((sinfo.get("budget_chars") or "0").strip())
            except ValueError:
                budget = 0
        if budget:
            actual = han("".join(m["text"] for m in moves))
            ratio = abs(actual - budget) / budget
            checker.need(
                ratio <= BUDGET_TOLERANCE,
                f"B8 {label} move 文本 {actual} 字，预算 {budget} 字，相差 {ratio:.0%}，超出 ±15%",
            )
        else:
            checker.warn(False, f"B8 {label} 无 budget_chars，跳过字数检查")

        # B9 evidence traceability (R1)
        for i, move in enumerate(moves, 1):
            if move["kind"] != "evidence" or TRACE_RE.search(move["text"]):
                continue
            if trace_mode == "appendix":
                checker.warn(
                    False,
                    f"B9 {label} 第 {i} 条 evidence 无内联标记；已在 appendix 模式下按 register 覆盖",
                )
            else:
                checker.need(
                    False,
                    f"B9 {label} 第 {i} 条 evidence 无可追溯标记（文件名 / URL / [E:ID]）且未标注 [断言]",
                )

    checker.note("人工门（脚本不判）：反稻草人；stake 是否真的点名听众；边界表能否逐条复述")
    return checker.report()


if __name__ == "__main__":
    raise SystemExit(main())
