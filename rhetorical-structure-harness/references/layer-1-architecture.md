# Layer 1：架构（大纲为什么是这个顺序）

第一层的产物不是"章节标题列表"，是**一条听众信念状态的转移链**。

学术依据：Bitzer 的修辞情境（exigence / audience / constraints）、Cicero 的六段式、Swales 的 CARS、Labov 的叙事六成分、Hoey 的段落关系、Monroe 的 motivated sequence。映射见 [literature-base.md](literature-base.md) §1–2。

---

## 1. brief：六格，缺一不出大纲

| 格 | 问法 | 不合格 |
|---|---|---|
| occasion | 谁办的、为什么办、讲完现场会发生什么 | "一个大会" |
| audience | 他们已经信什么、怀疑什么、能当场做什么 | "年轻人" |
| purpose | **一个**改变：信念／决定／行动／关系 | "介绍我的研究" |
| takeaway | 听众离开时能复述的**一句** | 空缺 |
| constraints | 时长、形式、有无 PPT、有无 Q&A、语言 | 漏掉 Q&A |
| evidence | 手上有哪些真材料、各自边界 | "数据很多" |

**purpose 与 takeaway 各恰好一句**（Grice 的量准则；也是 Gate 0）。purpose 用 Burke 的五元写：谁、在什么场景、想推动什么。

---

## 2. 原型库：按规则选，不按喜好选

每个原型必须给出来源。选型公式：

```text
archetype = f(purpose, audience_stance, evidence_density)
```

| 原型 | 适用 | 状态链 | 祖先 | 失败形态 |
|---|---|---|---|---|
| `discovery-log` 发现日志 | 让人相信一个判断该被关心 | 我以为 → 我查了 → 我发现 → 所以我问你 | Labov 六成分 | 流水账 |
| `thesis-defence` 主张—反驳 | 说服怀疑的技术听众 | 承认共识 → 指出缺口 → 主张 → 最强反驳 → 回应 | Cicero confirmatio+refutatio；Swales CARS | 自负或回避 |
| `fault-line` 裂缝—新世界 | 引出邀请／行动 | 旧默认 → 裂缝 → 已有人动手 → 邀请 | Hoey problem–solution | 变成宣传 |
| `contrast-pairs` 反直觉对照 | 给一个洞见 | 你以为 A → 其实 B → 为什么 → 所以 | Perelman dissociation | 猎奇 |
| `question-chain` 问题链 | 圆桌／对谈 | 一问 → 追问 → 再问 | 苏格拉底式 | 无结论感 |
| `mid-state` 中间态 | 行业／政策听众 | 两种叙事都不对 → 中间状态 → 含义 | Adam 解释序列 | 含糊骑墙 |
| `invitation` 邀请 | 招募／合作 | 问题 → 张力 → 已存在的答案 → 邀请 | Monroe motivated sequence | 说教 |

**硬规则**：原型一旦选定，`brief.md` 与 `architecture.md` 都要记；中途换原型视为重新走 Gate A。

---

## 3. 节卡：五个字段决定一节

```markdown
## 第 N 节：标题
- job：这一节必须完成的一件事（动词开头）
- from→to：听众从什么状态到什么状态
- material：消费哪些证据／资产（必须真实存在）
- turn：把听众推离哪个默认预期
- handoff：留给下一节的问题
- budget_chars：汉字预算
```

**状态链纪律**：第 N 节的 `to` 必须**等于**第 N+1 节的 `from`。听众状态是连续变量，不允许无声跳变。若确要重置（例如从数据转到邀请），在该节 `from` 前加 `!`，并在 `decisions.md` 写明理由。这条是 Gate A 的机器检查项。

---

## 4. architecture.md 的可检格式

控制面用管道表放在注释标记里，脚本只读标记内内容，正文随便写。

```markdown
<!-- ARCH:HEADER:BEGIN -->
archetype | target_minutes | wpm | tension | payoff_section | mode | trace_mode
thesis-defence | 6 | 280 | 退出与等待同时发生 | 5 | staged | appendix
<!-- ARCH:HEADER:END -->

<!-- ARCH:SECTIONS:BEGIN -->
id | title | job | from | to | material | turn | handoff | budget_chars
1 | 开场 | 让听众承认这是个问题 | 没想过这个问题 | 想听下去 | B站总量2.70倍 | 我以为这是技术话题 | 为什么会这样 | 167
2 | 研究方法 | 让人相信材料可靠 | 想听下去 | 接受材料的边界 | 279项目名录 | 四块材料口径不同 | 地面上发生了什么 | 130
<!-- ARCH:SECTIONS:END -->
```

可选两列：`mode`（`plan_only`／`staged`／`continuous`／`revision`）与 `trace_mode`（`appendix` 口述稿默认／`inline`）。`mode: revision` 时 Gate A 的 A4 只作提示（R5）。

---

## 5. Gate A（`scripts/check_architecture.py` 执行）

| # | 检查 | 依据 |
|---|---|---|
| A1 | header 必需五格非空；`target_minutes`、`wpm`、`payoff_section` 合法；`mode`／`trace_mode` 可选 | Bitzer |
| A2 | 节 id 连续、唯一；九列全非空。`material` 写 `无`／`none` 时接受，但记一条 warning（R6） | — |
| A3 | 没有两节 `job` 相同 | 分工不清＝状态不推进 |
| A4 | 状态链连通：`to[i] == from[i+1]`，或 `from[i+1]` 以 `!` 开头。**`mode: revision` 时只作提示**：反推者总能追认这条链，A4 不构成对原稿的检验（R5） | Halliday & Hasan 衔接 |
| A5 | `payoff_section` 指向存在的节 | takeaway 必须由某节交付 |
| A6 | `budget_chars` 合计 = `target_minutes × wpm` ±10% | Chafe／Kintsch 负荷 |
| A7 | 每节 `material` 指向真实存在的文件或数据（可用 `--evidence-root` 校验） | 证据纪律 |

脚本输出 `PASS`／`FAIL` 与逐条理由，退出码非零即失败。语义类判断（tension 是否真是张力、job 是否真的推进）仍由人过，脚本不假装能判。

---

## 6. 人工门（脚本不判，必须写进 audit）

- 原型选择与 purpose 是否真的匹配（选型公式是启发式，不是定理）。
- 每个 `job` 是否真的改变听众状态，还是只是"讲了一件事"。
- tension 是否会让**这批**听众感到，而不是讲者自己感到。
- 证据密度是否足以支撑该原型；不足时应降级为 `plan_only` 或换原型。
- **revision 模式额外要求**：每节 `job` 能对应回原稿的具体句子；否则 `from`/`to` 只是审计者的构造，不代表原稿结构。
