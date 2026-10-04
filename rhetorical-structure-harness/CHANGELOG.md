# CHANGELOG

## 0.1.0 — 2026-09-15

骨架首版。口述优先，两层结构，规则均有文献出处。

### 新增

- `SKILL.md`：核心模型（brief → Layer 1 → Layer 2 → script/delivery）、执行模式（plan_only / staged / continuous / revision）、生命周期与 Gate 0–D、修辞边界（做成硬检查）、与邻近技能的分工。
- `references/literature-base.md`：文献底座与**设计映射**。每条规则追到出处，引用分「已核（含 DOI）／经典待核」三级。核心：Bitzer 修辞情境、Toulmin 论证模型、Mann & Thompson RST、Perelman 概念分裂、Labov 叙事六成分、Swales CARS、Atkinson/Heritage 现场掌声装置、Ong 口述性、Chafe idea unit、Tannen involvement、Biber 口语维度、Kintsch 理解负荷、Hyland 元话语、Du Bois 立场三角、Halliday & Hasan 衔接、Grice 准则、Sperber & Wilson 关联、Goffman footing、van Eemeren 语用辩证、Adam 文本序列。
- `references/layer-1-architecture.md`：brief 六格、七种原型（含祖先与失败形态）、选型公式、节卡五字段、状态链纪律（`to[i] == from[i+1]`）、Gate A 七项。
- `references/layer-2-rhetoric.md`：TS 规则、九种 move（映射 RST 关系与 Toulmin 角色）、节内语法七条、口述装置表、Gate B 九项、反稻草人与边界表。
- `references/oral-delivery.md`：字符预算 × idea unit 预算、Biber 口述特征清单、朗读实测协议、开场/收束、Q&A、提词版格式。
- `scripts/_common.py`：标记块与管道表解析、汉字计数、Checker 报告器。
- `scripts/check_architecture.py`：Gate A 机器检查（A1–A7），支持 `--evidence-root` 校验 material 路径。
- `scripts/check_moves.py`：Gate B 机器检查（B1–B9），含相邻同类、turn 位置、evidence→limit 顺序、预算偏差、证据可追溯。
- `scripts/init_talk_harness.py`：从模板初始化实例，拒绝覆盖非空目录。
- `assets/talk-template/`：brief / architecture / sections / state.csv / decisions / audit / delivery-notes / goal。

### 已验证

- 空模板跑 Gate A → FAIL（正确）。
- 合法三节样例：Gate A PASS（补齐证据后）、Gate B PASS。
- 负例（删 limit、turn 挪到后半段）→ Gate B 报出 B4 / B6 / B8 三项 FAIL。

### 未做

- 未安装到宿主技能目录（`~/.claude/skills`、`~/.codex/skills`），未登记 `706-system/05-CAPABILITIES.md`。
- 未写 `evals/`。
- 未接入具体项目实例（上海区块链周演讲尚未用本 harness 重建）。
- 未实现 Gate C（script）与 Gate D（delivery）的自动检查；当前只有人工清单。

## 0.1.0 试运行 · 2026-09-15 · revision 模式首跑

对象：上海区块链周 v12 六分钟稿（逐句反推，不改词）。实例位于
`706-production-research/emerging-social-forms-micro-observations/system/shanghai-blockchain-week/harness/`。

结果：**Gate A PASS，Gate B FAIL 43 项**（B9 16｜B3 16｜B7 5｜B6 3｜B4 2｜B5 1）。

抓到两个系统性结构缺陷（非误报）：
1. 七节中六节无 `anchor` —— 全篇没有可记住的具体画面。
2. 七节中五节无 `stake` —— 除结尾外没有一处点明听众利害。

暴露 6 项规则问题（待修订，未擅自改）：
- R1 `B9` 对纯口播稿过严：来源在附录，正文不念文件名 → 16 项全误报。
- R2 `B5` 与预驳（prolepsis）冲突：应先区分 claim-qualifier 与 framing-disclaimer。
- R3 `B7` 禁止相邻同 kind 缺文献依据：RST 允许多个 Evidence satellite 连续。
- R4 `B3` 每节 turn==1 对方法/清单型节需允许 `type: method` 降级为警告。
- R5 `A4` 状态链在 revision 模式下由反推者追认，几乎不构成检验。
- R6 `A2` material 可用"无（纯钩子）"字面通过，门禁失效。

审计全文：该实例 `audit/gate-b-findings.md`。

## 0.2.0 — 2026-09-15 · 规则修订（R1–R6）与复跑验收

依据 revision 模式首跑暴露的 6 项规则问题修订，未改动被审计的讲稿。

### 变更
- `_common.py`：新增 `disclaimer` move；新增 `MAX_RUN`（evidence ≤3，其余 ≤1）与 `max_run()`；新增 `load_evidence_register()`；`parse_section_file()` 改为按表头取值，支持可选 `type` 列。
- `check_moves.py`：B9 支持 `trace_mode: appendix` + `evidence/register.csv`（降为 warning）；B5 将 `disclaimer` 排除在先立后限之外；B7 改为按 kind 的连续上限；B3 支持 `type: method|list` 时 turn 降级为 warning。
- `check_architecture.py`：ARCH header 支持 `mode`／`trace_mode`；`mode: revision` 时 A4 输出保留意见；`material: 无|none` 接受但记 warning。
- `references/layer-1-architecture.md`、`references/layer-2-rhetoric.md`：Gate A/B 表与格式说明同步更新。
- `assets/talk-template/`：ARCH header 加 `mode`／`trace_mode`；SECTION 表加可选 `type`；新增 `evidence/register.csv`。

### 复跑验收（上海区块链周 v12 实例）
| | 修订前 | 修订后 |
|---|---:|---:|
| 总失败 | 43 | 23 |
| B9 | 16 | 0（转 16 warning） |
| B5 | 1 | 0 |
| B7 | 5 | 2（frame×2） |
| B3/B4/B6 | 16/2/3 | 16/2/3 |

误报 20 项清零，真实结构缺陷全部保留。回归测试：合法样例 PASS，空模板 FAIL，均符合预期。

## 安装与登记 · 2026-09-15

- 安装：`~/.agents/skills/rhetorical-structure-harness` 与 `~/.claude/skills/rhetorical-structure-harness` 均建为指向 `706-skills/rhetorical-structure-harness/` 的符号链接（与 `research-writing-coach`、`wechat-image-archive` 同一形态；不增设 Codex 副本）。
- 验证：`706-skills/infra/scripts/config-doctor.py` 报告两个 runtime 的 `entrypoint_same` 与 `same_target` 均为 true，`duplicate_discoverable_names` 为空；通过软链回读 `SKILL.md` 与运行 `check_moves.py --help` 均正常。
- 登记：`706-system/05-CAPABILITIES.md` §4 的「706 专有」行新增本技能，并新增小节「2026-09-15 口述修辞结构 harness（迭代中）」，记录用途、文献依据、安装形态、验收结果与边界。
- 状态：**迭代中**，规则与模板可能破坏性变更；Gate C / Gate D 未实现。
