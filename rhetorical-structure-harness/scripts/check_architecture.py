#!/usr/bin/env python3
"""Gate A: validate the Layer-1 architecture of a talk harness.

Usage:
    python3 check_architecture.py <harness-root> [--evidence-root DIR]

Exit code 0 = PASS, 1 = FAIL, 2 = usage/missing file.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import Checker, load_architecture, marker_block, read  # noqa: E402

ARCHETYPES = {
    "discovery-log",
    "thesis-defence",
    "fault-line",
    "contrast-pairs",
    "question-chain",
    "mid-state",
    "invitation",
}

PATH_TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff./~-]+\.(?:md|csv|json|txt|tsv|xlsx|pdf|docx)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate A for rhetorical-structure-harness")
    parser.add_argument("root", help="harness root directory containing architecture.md")
    parser.add_argument("--evidence-root", default=None, help="directory used to resolve material paths")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not (root / "architecture.md").exists():
        print(f"architecture.md not found under {root}", file=sys.stderr)
        return 2

    header, sections = load_architecture(root)
    checker = Checker(f"Gate A · architecture · {root.name}")

    # A1 header present and valid
    if not checker.need(header is not None, "A1 缺少 ARCH:HEADER 标记块或仅有一行"):
        return checker.report()

    for field in ["archetype", "target_minutes", "wpm", "tension", "payoff_section"]:
        checker.need(header.get(field), f"A1 header 字段 `{field}` 为空")

    archetype = (header.get("archetype") or "").strip()
    checker.warn(archetype in ARCHETYPES, f"A1 未知原型 `{archetype}`（不在原型库中，需在 decisions.md 说明）")

    # R5: in revision mode the state chain is reverse-engineered, so A4 cannot
    # really test the original design; make that explicit.
    mode = (header.get("mode") or "staged").strip().lower()
    if mode == "revision":
        checker.note(
            "A4/R5 mode=revision：状态链为反推所得，非原稿显式设计；"
            "A4 只能证明结构可被这样理解，不能证明原稿本来就有这条链"
        )

    minutes = None
    wpm = None
    try:
        minutes = float(header.get("target_minutes") or "")
        checker.need(minutes > 0, "A1 target_minutes 必须为正数")
    except ValueError:
        checker.need(False, "A1 target_minutes 不是数字")
    try:
        wpm = float(header.get("wpm") or "")
        checker.need(wpm > 0, "A1 wpm 必须为正数")
    except ValueError:
        checker.need(False, "A1 wpm 不是数字")

    # A2 sections present, ids unique/contiguous, all cells non-empty
    if not checker.need(sections, "A2 缺少 ARCH:SECTIONS 数据行"):
        return checker.report()

    ids = []
    for section in sections:
        raw_id = (section.get("id") or "").strip()
        if not raw_id:
            checker.need(False, "A2 存在 id 为空的行")
            continue
        try:
            ids.append(int(raw_id))
        except ValueError:
            checker.need(False, f"A2 id `{raw_id}` 不是整数")
            continue
        missing = [k for k in ["title", "job", "from", "to", "material", "turn", "handoff", "budget_chars"]
                   if not (section.get(k) or "").strip()]
        checker.need(not missing, f"A2 第 {raw_id} 节缺少字段：{', '.join(missing)}")
        budget = (section.get("budget_chars") or "").strip()
        if budget:
            try:
                checker.need(int(budget) > 0, f"A2 第 {raw_id} 节 budget_chars 必须为正整数")
            except ValueError:
                checker.need(False, f"A2 第 {raw_id} 节 budget_chars 不是整数")

    checker.need(len(ids) == len(set(ids)), "A2 id 有重复")
    if ids:
        checker.need(ids == list(range(ids[0], ids[0] + len(ids))), "A2 id 不连续")

    # R6: a pure hook may legitimately have no evidence input; accept it but say so.
    for section in sections:
        material = (section.get("material") or "").strip()
        if re.fullmatch(r"无|none|—|-|无[（(].*[）)]", material, flags=re.I):
            checker.warn(False, f"A2 第 {section.get('id')} 节 material 为「{material}」：本节无证据输入")

    # A3 no duplicated job
    jobs = [(s.get("job") or "").strip() for s in sections if (s.get("job") or "").strip()]
    duplicates = {job for job in jobs if jobs.count(job) > 1}
    checker.need(not duplicates, f"A3 job 重复：{'; '.join(sorted(duplicates))}")

    # A4 audience state chain connectivity
    for prev, curr in zip(sections, sections[1:]):
        to_state = (prev.get("to") or "").strip()
        from_state = (curr.get("from") or "").strip()
        linked = from_state.startswith("!") or from_state == to_state
        checker.need(
            linked,
            f"A4 状态链断开：第 {prev.get('id')} 节 to=`{to_state}` ≠ 第 {curr.get('id')} 节 from=`{from_state}`"
            "（确需重置时请在 from 前加 ! 并写入 decisions.md）",
        )

    # A5 payoff section exists
    payoff = (header.get("payoff_section") or "").strip()
    try:
        checker.need(int(payoff) in ids, f"A5 payoff_section `{payoff}` 不指向任何一节")
    except ValueError:
        checker.need(False, "A5 payoff_section 不是整数")

    # A6 budget within +/-10% of target
    if minutes and wpm and ids:
        target = minutes * wpm
        total = 0
        ok = True
        for section in sections:
            try:
                total += int((section.get("budget_chars") or "0").strip())
            except ValueError:
                ok = False
        if ok:
            ratio = abs(total - target) / target
            checker.need(
                ratio <= 0.10,
                f"A6 字数预算合计 {total} 与目标 {int(target)}（{minutes:g} 分钟 × {wpm:g} 字/分）"
                f"相差 {ratio:.0%}，超出 ±10%",
            )
            checker.note(f"预算合计 {total} / 目标 {int(target)}（差 {ratio:.0%}）")

    # A7 materials resolve when an evidence root is provided
    if args.evidence_root:
        evidence_root = Path(args.evidence_root).expanduser().resolve()
        checker.need(evidence_root.is_dir(), f"A7 evidence-root 不存在：{evidence_root}")
        for section in sections:
            for token in PATH_TOKEN_RE.findall(section.get("material") or ""):
                candidate = (evidence_root / token).resolve()
                if not candidate.exists() and not (root / token).exists():
                    checker.need(False, f"A7 第 {section.get('id')} 节 material 指向不存在的路径：{token}")
        checker.note("A7 已按 evidence-root 校验 material 路径")

    # Manual gate reminders
    checker.note("人工门（脚本不判）：原型是否匹配 purpose、job 是否真的改变状态、tension 是否会被这批听众感到、证据密度是否支撑原型")

    return checker.report()


if __name__ == "__main__":
    raise SystemExit(main())
