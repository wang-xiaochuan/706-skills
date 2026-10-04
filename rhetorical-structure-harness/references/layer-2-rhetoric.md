# Layer 2：修辞（每节的说法为什么成立）

第二层的单位是**一节的论证体**：一个 topic sentence（claim），下面若干条 bullet；每条 bullet 承担**恰好一个修辞动作**。

依据：Toulmin 论证模型（claim / data / warrant / backing / qualifier / rebuttal）、Mann & Thompson 的 RST（nucleus–satellite 关系）、Perelman 的概念分裂、Hyland 的元话语、Atkinson／Heritage 的现场掌声装置。映射见 [literature-base.md](literature-base.md) §3、§4、§5。

---

## 1. Topic sentence 规则（Toulmin 的 claim）

一条 TS 必须：一个主张；主语＋动词＋利害；可被该节的证据反驳；无铺垫；≤ 40 汉字。

| | 例 |
|---|---|
| ✗ | 下面我讲讲 B 站的数据。 |
| ✗ | B 站观看量从 81.7 亿涨到 220.9 亿。（这是 data，不是 claim） |
| ✓ | 这些话被听见的次数，五年翻了一倍还多。 |

判据：把 TS 单独念出来，听众应能说出"讲者要我接受什么"。说不出，就不是 claim。

**为什么必须一个主张**：Toulmin 的 claim–data–warrant 结构要求唯一 claim；两个主张会让 data 的归属含糊，也让 `turn` 无处安放。

---

## 2. Move 表：每条 bullet 一个动作

| move | 修辞功能 | RST 关系 | Toulmin 角色 | 硬规则 |
|---|---|---|---|---|
| `anchor` 锚 | 给一个能抓住的具体物／数／场景 | Circumstance, Background | — | 每节 ≥1；必须具体到可复述 |
| `turn` 转 | 把听众推离默认预期，制造张力 | Antithesis, Contrast | rebuttal | 每节**恰好 1**，且在前半段 |
| `mechanism` 机制 | 解释"为什么会这样" | Explanation, Justify | warrant | 有 `evidence` 的节必须有 |
| `evidence` 证 | 证据 | Evidence, Elaboration | data | 数字／事实能追到证据入口 |
| `limit` 限 | 主动说出自己不能 claim 的 | Concession | qualifier | 有 `evidence` 必须有；且在首条 evidence 之后 |
| `disclaimer` 预驳 | 开口前先把听衆会有的质疑说出来 | Concession（前瞻式） | qualifier 的变体 | 可与 `limit` 并存；**不受先立后限约束**（可出现在 evidence 之前） |
| `stake` 利害 | 对**这批听众**意味着什么 | Motivation, Enablement | — | 必须点名听众；按 Du Bois 三元写 |
| `frame` 路标 | 导航，不承载论证 | （元话语） | — | 每节 ≤1 |
| `restate` 重述 | 让核心判断被记住 | Restatement, Summary | — | ≥1；口述的冗余是特性不是缺陷 |
| `call` 邀 | 要听众做什么 | Motivation | — | 全场 ≤2，不得在第一节 |

**RST 只借关系表，不做完整篇章树解析**——口述稿要的是可讲性与可成立性，不是自动篇章分析（Taboada & Mann 2006 已说明关系判定依赖读者意图）。

---

## 3. 节内语法（相邻与顺序）

1. 相邻两条 bullet 不得是同一 move。
2. `limit` 必须在首条 `evidence` 之后：先立后限（Toulmin qualifier 的顺序）。**`disclaimer` 不受此限**：样本免责、方法免责等预驳（prolepsis）本就应先说（R2）。
3. `turn` 必须落在节的前半段（含中点）：`turn_index ≤ ceil(n/2)`。后半段才转，听众来不及消化。
4. 论证类节必须同时有 `mechanism` 与 `evidence`：只有数据是罗列，只有机制是断言。
5. `stake` 必须出现在末条 `evidence` 之后；`restate` 收尾。
6. `frame` 全场不得连续两节都出现，避免"讲流程不讲内容"。
7. `call` 不得出现在第一节；全场 ≤2。
8. 同 kind 的连续上限：`evidence` 允许最多 3 连（RST 允许多个 Evidence satellite，R3）；其余 kind 不得相邻重复。

---

## 4. 口述装置（可选实现，不参与结构判定）

同样的 move，口头表达可以用 Atkinson／Heritage 记录的可听装置。写进 `delivery-notes.md`，不写进结构：

| 装置 | 说明 | 常挂在哪个 move |
|---|---|---|
| 三段式列举 | 三件事一组，第三件落重音 | `anchor`、`evidence` |
| 对照对 | "不是 X，是 Y" | `turn` |
| 谜题—解答 | 先抛反常，再解 | `turn` → `mechanism` |
| 标题—重击 | 一句结论＋一个短句敲下 | `restate`、`call` |
| 立场宣示 | 明确站边，配 `limit` | `stake` |

**注意**：装置放大的是真实判断。Atkinson/Heritage 证明它有效，不证明它可以替代证据。见 §6。

---

## 5. sections/NN-*.md 的可检格式

```markdown
<!-- SECTION:BEGIN -->
id | title | claim | budget_chars | type
1 | 开场 | 这些话被听见的次数五年翻了一倍 | 167 | argument
<!-- SECTION:END -->

<!-- MOVES:BEGIN -->
kind | text
anchor | 大家好，我是 [姓名]，代表 [机构]
turn | 这两年所有人都在谈大语言模型，但我总有个疑问挥不去
mechanism | 我把它叫"退出"，讲的不是我要什么，而是我不要什么
stake | 而这个问题，今天这个场合也躲不开
restate | 那我到底要什么？谁来接住我
<!-- MOVES:END -->
```

`type` 可选：`argument`（默认）／`method`｜`list`（允许无 `turn`，降级为警告，R4）。

---

## 6. Gate B（`scripts/check_moves.py` 执行）

| # | 检查 | 依据 |
|---|---|---|
| B1 | claim 非空、≤40 汉字，且与 `architecture.md` 中该节 `job` 归属同一节 | Toulmin；Grice 量准则 |
| B2 | move kind 全部在词表内 | RST 关系表 |
| B3 | 每节：`anchor`≥1、`stake`≥1、`restate`≥1；`turn`==1（`type: method/list` 时降级为警告） | 结构完整性；R4 |
| B4 | 有 `evidence` ⇒ 有 `mechanism` 且有 `limit` | Toulmin |
| B5 | 首条 `evidence` 的位置 < 首条 `limit` 的位置（`disclaimer` 不计） | Toulmin qualifier 顺序；R2 |
| B6 | `turn` 位置 ≤ ceil(n/2) | 现场理解负荷 |
| B7 | 同 kind 连续上限：`evidence` ≤3，其余 ≤1；`frame` ≤1/节；`call` ≤2 全场且不在第 1 节 | Hyland；Monroe；RST 多卫星；R3 |
| B8 | 节内 move 文本汉字合计 = `budget_chars` ±15% | Chafe／Kintsch |
| B9 | 每条 `evidence` 带内联标记（文件名 / URL / `[E:ID]`）；`trace_mode: appendix` 时可用 `evidence/register.csv` 覆盖并降为 warning | 证据纪律；R1 |

**反稻草人（人工门，脚本只提示）**：`turn` 要拆的是**听众真实持有的**默认预期，不是虚构的对手。若找不到真实持有的版本，这一节应删而不是立靶子（van Eemeren & Grootendorst 语用辩证）。

**边界表（Gate C 强制）**：把全场所有 `limit` 抽成一张表，讲者能逐条复述自己不能 claim 的东西。这张表是 harness 的伦理出口，不是附录装饰。
