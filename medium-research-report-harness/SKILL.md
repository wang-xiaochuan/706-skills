---
name: medium-research-report-harness
description: >
  Build, continue, restructure, audit, translate, and package evidence-rich medium-length research reports, usually about 8,000–40,000 Chinese characters or 5,000–25,000 English words. Use this skill whenever the user asks for a 中型研究报告、叙事研究、研究型长文、约一万字且多引用的文章、案例目录或法规年表、一步一步的 research harness、先收集再写作再事实核查，或要求把研究做成中英双语 HTML/Word/PDF 分享包—even when they do not explicitly call it a skill. It is designed for mixed local and web corpora, source-graded claims, narrative continuity, appendices, images, revision conservation, and publication QA. Do not use it for a one-paragraph answer, a pure translation, or a short activity recap with no research apparatus.
---

# Medium Research Report Harness

把一次容易失控的长研究，变成一个可恢复、可审计、可继续迭代的双轨生产系统。

它不是固定文章模板。它管理的是研究从问题到证据、从证据到叙事、从叙事到出版的生命周期。

运行初始化与校验脚本需要 filesystem、`rg` 和 Python 3；DOCX／PDF 交付可再调用 documents、pdf 或等价本地渲染工具。

## 1. 核心模型

始终维护三层，不能混成一个文件夹：

1. **证据轨**：原始语料、抽取文本、检索日志、来源登记、案例／政策／事件母表、未知项与排除记录。
2. **叙事轨**：预写作、结构方案、内容守恒、章节论证卡、母语正文、翻译稿、声口与逻辑审计。
3. **出版层**：图片登记、注释、HTML、Word、PDF、紧凑附录、完整研究包和项目方阅读包。

证据轨回答“我们凭什么这样写”；叙事轨回答“读者为什么愿意一路读下去”；出版层证明“交付物真的能打开、能引用、能发送”。

## 2. 开始前的最短读取路径

每次触发后：

1. 读取当前工作区的 `AGENTS.md`、bootstrap、README、current-state 或用户指定权威文件。
2. 读取 [references/stage-workflow.md](references/stage-workflow.md)，选择阶段和执行模式。
3. 若涉及事实、案例目录、法规或统计，读取 [references/evidence-model.md](references/evidence-model.md)。
4. 若涉及重写、提纲、声口或逻辑，读取 [references/narrative-and-audit.md](references/narrative-and-audit.md)。
5. 若涉及 HTML、Word、PDF、图片或分享包，读取 [references/publication-packaging.md](references/publication-packaging.md)。
6. 只有在需要理解这套方法为何如此设计时，才读取 [references/cohousing-v13-retrospective.md](references/cohousing-v13-retrospective.md)。

不要为了“了解项目”一次性加载所有语料。先读控制面和登记表，再按当前阶段选择原件。

## 3. 判断执行模式

将用户请求归入一种模式，并写入 `goal.md`：

- **plan_only**：只设计研究路径和产出物。不得开始抓取、写正文或外部写入。
- **staged**：每个重要阶段交付后等待用户确认。适合尚未锁定范围、叙事方向或隐私边界的项目。
- **continuous**：用户明确要求“不要停”“自动执行”“从收集做到交付”时，连续推进所有可安全执行的阶段；只有缺少会改变结果的授权或事实时才停。
- **revision**：已有长稿，目标是审计、重编或双语出版。先冻结基线和建立内容守恒矩阵，不能直接在旧稿上做伪结构改写。

模式决定停不停，不改变证据标准。

## 4. 初始化 Harness

新项目优先运行：

```bash
python3 <skill-dir>/scripts/init_harness.py \
  --root /absolute/path/to/project \
  --title "项目标题" \
  --slug project-slug \
  --mode staged \
  --primary-language zh-CN \
  --audience "目标读者"
python3 <skill-dir>/scripts/check_harness.py /absolute/path/to/project
```

脚本拒绝覆盖非空目录。已有项目不要强行套模板：先把现状映射到同一组逻辑文件，再运行校验。

Harness 的控制面是：

- `goal.md`：目标、读者、范围、证据边界、产出物与完成条件。
- `state.csv`：阶段状态；进行中时恰好一个 `ACTIVE`，此前为 `PASSED`，以后为 `LOCKED`。
- `decisions.md`：用户修正、重要假设、命名与删除决定。
- `audit/audit-summary.md`：所有门禁的当前结论。

推进阶段前运行：

```bash
python3 <skill-dir>/scripts/advance_stage.py /absolute/path/to/project \
  --handoff relative/path/to/completed-handoff
```

该脚本只在当前阶段要求的交接文件存在且非空时推进。

## 5. 十四阶段生命周期

| ID | 阶段 | 核心交付 | 通过条件 |
|---|---|---|---|
| 00 | Scope | `goal.md`、术语和读者边界 | 目标、长度、语言、输出、隐私和停止条件明确 |
| 01 | Corpus | 原件归档、manifest、可检索派生文本 | 原件未被改写；哈希、来源、时间可追溯 |
| 02 | Evidence map | 来源登记、证据等级、claim register | 自述、第三方、政策、口述和推论分开 |
| 03 | Coverage | 检索协议、地域／时间／平台矩阵、日志 | 每个计划单元有结果或有记录的未命中 |
| 04 | Structured research | 案例、法规、事件、未知项、排除表 | ID 唯一、状态词受控、每行有证据或明确 unknown |
| 05 | Prewriting | 时间、话语、物与空间、情感、组织、上下文、品味、数据 | 事实、张力、沉默、冲突和盲区均被抽取 |
| 06 | Architecture | 叙事 arc、详细 outline、内容守恒矩阵 | 不是只换标题；旧内容逐项有去向 |
| 07 | Primary draft | 母语完整初稿、章节论证卡 | 每章有论点—证据—机制—边界—转场链 |
| 08 | Research audit | 事实、引文、统计、脚注、链接和隐私审计 | 硬事实可追溯；未知项没有被写成结论 |
| 09 | Narrative audit | 连接性、逻辑、声口、AI 腔、重复和节奏审计 | 案例服务于机制，不是项目名录式堆砌 |
| 10 | Visuals | 图片资产、caption、来源与图文对应 | 图为论证工作；无错图、断图或公共稿内部备注 |
| 11 | Translation | 第二语言全文与术语表 | 标题、图序、注释、概念解释和证据边界对齐 |
| 12 | Publication | HTML、Word、可选 PDF、独立附录 | 文件可打开；HTML/Word/PDF 通过技术与视觉检查 |
| 13 | Release | 完整研究包、项目方阅读包、ZIP、README | 单一当前版本、无旧稿残留、压缩包通过解压测试 |

详细动作与交接文件见 `references/stage-workflow.md`。

## 6. 证据轨的硬边界

执行研究时遵守以下原则：

- 让每条可公开核实的主张拥有稳定 `source_id`；引用次数和来源登记总数分别统计。
- 项目自述证明“项目怎样描述自己”，不自动证明效果、规模、代表性或长期存续。
- 单一口述保留记忆与措辞；地址、年份、产权、合同和行政过程未核时不得扩写成城市通史。
- `unknown` 是正式数据，不是等待模型补齐的空格。
- “网页未找到”“检索未命中”“近期停更”分别不是“不存在”“当地没有”“已经关闭”。
- 聚合总量、项目节点、品牌门店、参与人数、床位和实际入住不能相加。
- 法律原文、政府政策、智库作者文章、新闻解读和作者推论分层。
- 具名人物目录不是默认附录。涉及住客、邻居、普通员工或照护者时，先做隐私与公共利益判断。

字段与等级模板见 `references/evidence-model.md`。

## 7. 从研究到叙事

事实多不等于文章成立。进入 Stage 06 时执行四个动作：

1. **锁定主问题**：全文持续追踪 3–7 个机制问题，而不是按发现案例的顺序写。
2. **建立内容守恒矩阵**：旧稿每个事实块、案例、图片、注释都有 `keep / move / merge / cut-with-reason` 处置。
3. **重写结构而非标题**：outline 改变后，段落功能、案例位置和因果链也必须改变；用相似度或块序审计发现“只加了新标题”的假重写。
4. **为每章写论证卡**：`claim → evidence → mechanism → boundary → transition`。下一章必须接住上一章留下的对象、资格、矛盾或问题。

文化作品、歌曲、影视和文学可以保存时代感受，不能替代住房、政策、统计或组织事实。

完整审计方法见 `references/narrative-and-audit.md`。

## 8. 审计顺序

不要把所有检查混成一次“润色”。按依赖顺序执行：

1. 内容守恒与结构实施检查。
2. 事实、引文、统计、时间和来源检查。
3. 脚注首次出现顺序、定义／调用、链接检查。
4. 论点—证据—机制—边界链与跨章转场检查。
5. 术语、语义和重复检查。
6. 声口、营销腔、AI 套话和认识论谦逊检查。
7. 图片—段落—caption—来源对齐。
8. 双语结构、图序、注释和文化解释对齐。
9. HTML／Word／PDF 技术、无障碍和全页视觉检查。
10. 包内残留、旧版本、隐私、内部备注和 ZIP 解压检查。

上游失败时回到对应阶段修复，再重跑下游门禁；不要在最终排版层掩盖研究问题。

## 9. 附录与正文的关系

数据母表、读者附录和正文是三种不同产品：

- **CSV 母表**保留完整字段、证据、未知项和排除理由。
- **紧凑附录**服务查找，只显示读者真正需要的少数字段，例如地点、介绍、最近痕迹和链接。
- **正文**只保留对叙事机制有工作的案例。

附录变得比正文长时，优先独立成册，而不是删除研究母表。项目方阅读包只放说明、正文、附录和图片；完整研究包另存。

## 10. 出版与交付

母语结构与事实稳定后才翻译。HTML、Word 和 PDF 是不同渲染目标，应分别检查：

- HTML：自包含资源、锚点、图片和离线打开。
- Word：真实标题层级、可访问性、图片嵌入、注释、表格跨页和页眉页脚。
- PDF：字体嵌入、页数、文本往返、全页渲染和视觉抽检。
- ZIP：无 `__MACOSX`、`.DS_Store`、旧稿或内部说明；执行完整解压测试并记录 SHA-256。

发布包结构和验收清单见 `references/publication-packaging.md`。

## 11. 与其他 skill 的边界

- 需要外层 CLI 自动循环时，可调用 `harness-goal-runner`；本 skill 仍负责研究阶段和证据门禁。
- 原始材料需要穷尽式多维抽取时，可调用 `prewriting`，但受当前会话是否允许子代理影响。
- 短活动回顾或纯叙事设计更适合 `narrative-crafting`。
- 最终中文声口迁移可调用 `debotton-chen-nan-rewrite`，只能在事实与引用锁定后执行。
- DOCX、PDF、图片编辑分别调用对应文档／PDF／图像 skill，并保留本 skill 的研究验收条件。

## 12. 完成定义

只有以下条件同时满足，才称研究报告完成：

- `state.csv` 全部阶段为 `PASSED`；
- 原始语料、研究母表、正文和公开包彼此分层；
- 没有无来源硬事实、悬空脚注、错序图片或未说明推论；
- 结构审计证明新 outline 已实际进入正文；
- 公开文件不含内部生产备注或隐私目录；
- 所有承诺格式已实际生成、打开、渲染和检查；
- 当前版本唯一，旧版删除／归档动作有清单且可恢复；
- README 说明读者从哪里开始、每个文件是什么、核验日期与证据边界。

若任务只是一个阶段，明确报告已完成的阶段、尚未运行的阶段和下一交接物，不能把局部完成称为整项完成。
