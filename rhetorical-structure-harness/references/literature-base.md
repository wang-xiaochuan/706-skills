# 文献底座与设计映射

本文件回答一个问题：**harness 里的每条规则，凭什么这么定。**

引用状态分三级，防止把"我记得"当"已核"：

- ✅ **已核**：本轮通过 Crossref／DOI 核对了作者、年份、题名与出处。
- ◻︎ **经典待核**：公认经典，本环境未取到干净元数据（多为会议论文或早期专著），引用时保留出处但不冒称已核。
- 新增引用前先核，核不到就标 ◻︎，不编 DOI。

---

## 1. 修辞情境：Layer 0 brief 从哪来

| 文献 | 核心概念 | 落在 harness 哪里 |
|---|---|---|
| Bitzer, L. F. (1968). The Rhetorical Situation. *Philosophy & Rhetoric*, 1(1), 1–14. ◻︎ | 修辞情境三要素：exigence（可被话语改变的迫切问题）、audience（能被影响、能成为行动中介的人）、constraints（人物、事件、物件、信念构成的限制） | `brief.md` 的 purpose / audience / constraints 三格；"可被改变的迫切问题"决定 purpose 必须是**一个**改变 |
| Vatz, L. J. (1973). The Myth of the Rhetorical Situation. *Philosophy & Rhetoric*, 6(3), 154–161. ◻︎ | 情境不是被给予的，是被修辞者选择与建构的 | brief 增加一格：**我们要让听众感到什么在利害上**（stake 的来源） |
| Burke, K. (1945/1969). *A Grammar of Motives*. University of California Press. ✅ doi:10.1525/9780520341715 | 戏剧五元（act / scene / agent / agency / purpose）；identification；terministic screen | purpose 用"谁在什么场景下做什么"写，而不是写主题词；认同（identification）决定 stake 的措辞 |

**推导出的规则**：brief 六格缺一不出大纲；purpose 与 takeaway 各恰好一句。来源是与 Bitzer 三要素 + Vatz 补充一一对应。

---

## 2. 全局安排：Layer 1 原型库的祖先

| 文献 | 核心概念 | 落在 harness 哪里 |
|---|---|---|
| Aristotle, *Rhetoric*. ◻︎ | 三种诉求 ethos / pathos / logos；五艺 inventio–dispositio–elocutio–memoria–pronuntiatio | 生命周期：dispositio = Layer 1，elocutio = Layer 2，pronuntiatio = delivery；ethos 做成独立检查项，pathos 落在 `stake`，logos 落在 `mechanism`/`evidence` |
| Cicero, *De Oratore*；*Rhetorica ad Herennium*. ◻︎ | 六段式：exordium / narratio / partitio / confirmatio / refutatio / peroratio | 原型的古典祖先：`主张—反驳`＝confirmatio+refutatio，`发现日志`＝narratio+confirmatio |
| Swales, J. M. (1990). *Genre Analysis: English in Academic and Research Settings*. Cambridge UP. ◻︎ | CARS 模型：establishing a territory → establishing a niche（counter-claiming / indicating a gap）→ occupying the niche | `研究型主张` 原型的三段状态链：承认共识 → 指出缺口 → 占位 |
| Labov, W., & Waletzky, J. (1967/1997). Narrative Analysis: Oral Versions of Personal Experience. *Journal of Narrative and Life History*, 7(1–4), 3–38. ✅ doi:10.1075/jnlh.7.02nar | 口头叙事的六成分：abstract / orientation / complicating action / evaluation / resolution / coda | `发现日志` 原型的链；`anchor` 的祖先＝orientation，`turn` 的祖先＝complicating action，`restate` 的祖先＝coda |
| Hoey, M. (1983). *On the Surface of Discourse*. Allen & Unwin. ✅（经 Biber 1985 书评 doi:10.2307/414437 核对） | 段落关系模式：problem–solution、general–particular、matching | 节与节之间的默认衔接语法（`handoff` 的形态库） |
| Monroe, A. H., *Principles and Types of Speech*（motivated sequence）. ◻︎ | attention → need → satisfaction → visualization → action | `邀请型` 原型；`call` move 只允许出现在中段与结尾 |

**推导出的规则**：原型必须**按规则选**（purpose × audience 立场 × 证据密度），不能按喜好选；每个原型必须给出可追溯的祖先，否则不进库。

---

## 3. 论证体：Layer 2 的两根支柱

### 3.1 Toulmin：一节里必须有哪几样

| 文献 | 核心概念 | 落在 harness 哪里 |
|---|---|---|
| Toulmin, S. E. (1958/2003). *The Uses of Argument*. Cambridge UP. ✅ doi:10.1017/cbo9780511840005 | claim / data（grounds） / warrant / backing / qualifier / rebuttal | topic sentence = **claim**；`evidence` = data；`mechanism` = warrant；`limit` = qualifier；`turn` = rebuttal；backing 并入 `mechanism` 的出处 |

**推导出的规则**：
- 每节恰好一个 claim（TS），否则 Toulmin 的 claim–data 结构不成立。
- 有 `evidence` 必须有 `limit`——Toulmin 的 qualifier 是模型内建项，不是客气话。
- `limit` 必须出现在第一条 `evidence` 之后：先立后限，credibility 才成立。

### 3.2 RST：bullet 是关系，不是事实

| 文献 | 核心概念 | 落在 harness 哪里 |
|---|---|---|
| Mann, W. C., & Thompson, S. A. (1988). Rhetorical Structure Theory: Toward a functional theory of text organization. *Text*, 8(3), 243–281. ✅ doi:10.1515/text.1.1988.8.3.243 | nucleus–satellite 关系；Evidence、Elaboration、Concession、Antithesis、Justify、Motivation、Enablement、Circumstance、Background、Restatement、Summary、Solutionhood 等 | move 分类表；`claim` = nucleus，其余 bullet = satellite；节内顺序＝关系可成立性 |
| Taboada, M., & Mann, W. C. (2006). Rhetorical Structure Theory: Looking back and moving ahead. *Discourse Studies*, 8(3), 423–454. ✅ doi:10.1177/1461445606061881 | RST 的关系清单、应用边界、对人际关系的补充 | 说明为何只借关系表、**不做**完整 RST 自动解析：口述稿要的是可讲性，不是篇章树 |

**推导出的规则**：相邻两条 bullet 不得是同一 move；`claim` 之外至少一个 satellite 承载论证（不能全是 `frame`）。

### 3.3 Perelman：`turn` 的机制

| 文献 | 核心概念 | 落在 harness 哪里 |
|---|---|---|
| Perelman, C., & Olbrechts-Tyteca, L. (1958/1969). *The New Rhetoric: A Treatise on Argumentation*. University of Notre Dame Press. ✅ doi:10.1353/book.129845 | 受众是论辩的构造物；association / dissociation；"appearance–reality""means–end""theory–practice"等概念分裂 | `turn` = 一次 dissociation：把听众原本合在一起看的东西拆开；brief 的 audience 是构造物，因此要写"他们已信什么／怀疑什么" |

**推导出的规则**：每节恰好一个 `turn`，且出现在前半段；`turn` 必须能用"你以为 A，其实是 A′＋B"表述。

---

## 4. 口述：为什么不能照搬书面结构

| 文献 | 核心概念 | 落在 harness 哪里 |
|---|---|---|
| Ong, W. J. (1982). *Orality and Literacy: The Technologizing of the Word*. Routledge. ✅ doi:10.4324/9780203328064 | 口述文化的冗余、公式化、agonistic 特征；书面才有"去冗余" | `restate` 是**必需** move，不是啰嗦；口播稿允许并需要重复核心判断 |
| Chafe, W. (1982). Integration and Involvement in Speaking, Writing, and Oral Literature. In Tannen (ed.), *Spoken and Written Language*. ◻︎；Chafe, W. (1994). *Discourse, Consciousness, and Time*. Chicago UP. ◻︎ | idea unit / intonation unit；involvement vs detachment；口语的在线生成压力 | 时长按 **idea unit** 估，不只看汉字数；一节的信息块数设上限 |
| Tannen, D. (1989/2007). *Talking Voices: Repetition, Dialogue, and Imagery in Conversational Discourse*. Cambridge UP. ✅ doi:10.1017/cbo9780511618987 | 重复、对话、意象作为 involvement 装置 | `restate`、直接引语式 `anchor`；involvement 检查项 |
| Biber, D. (1988). *Variation across Speech and Writing*. Cambridge UP. ✅ doi:10.1017/cbo9780511621024 | 口语/书面多维差异（第一二人称、现在时、缩略、that 省略等） | Gate C 的"口述语言特征"清单 |
| Atkinson, J. M. (1984). *Our Masters' Voices: The Language and Body Language of Politics*. Methuen/Routledge. ◻︎ | 现场掌声的结构装置：三段式列举、对照对（contrastive pair）、谜题—解答（puzzle–solution）、标题—重击（headline–punchline）、立场宣示 | 口述 elocutio 装置清单；bullet 的"可听性"检查 |
| Heritage, J., & Greatbatch, D. (1986). Generating Applause: A Study of Rhetoric and Response at Party Political Conferences. *American Journal of Sociology*, 92(1), 110–129. ✅ doi:10.1086/228465 | 掌声可由上述装置稳定预测；"pursuit"式追问 | 为什么把 `turn` 与 `stake` 标为必检动作；结尾 `call` 的位置规则 |
| Kintsch, W. (1998). *Comprehension: A Paradigm for Cognition*. Cambridge UP. ✅（经 Graesser & Whitten 2000 书评 doi:10.1016/s0378-2166(99)00090-9 核对） | construction–integration；工作记忆与推理负荷 | 每节独立信息块上限；为什么 bullet 宜少而具体 |

**推导出的规则**：时长＝max(汉字预算, idea unit 预算)；每节信息块 ≤ 工作记忆可承载量；`restate` 不可省。

---

## 5. 衔接、立场与边界

| 文献 | 核心概念 | 落在 harness 哪里 |
|---|---|---|
| Halliday, M. A. K., & Hasan, R. (1976). *Cohesion in English*. Longman/Routledge. ✅ doi:10.4324/9781315836010 | 指称、替代、省略、连接、词汇衔接 | `handoff` 就是节间连接词；Gate A 检查状态链连通 |
| Hyland, K. (2005). *Metadiscourse: Exploring Interaction in Writing*. Continuum/Bloomsbury. ✅ doi:10.5040/9781350063617 | transitions、frame markers、evidentials、hedges、boosters、attitude/engagement markers | `frame`（≤1/节）、`limit`（hedge）、`stake`（engagement marker） |
| Du Bois, J. W. (2007). The Stance Triangle. In Englebretson (ed.), *Stancetaking in Discourse*, 139–182. ✅ doi:10.1075/pbns.164.07du | stance 三元：评价者—对象—评价，外加 alignment | `stake` 的三元检查：谁、对什么、给出什么评价 |
| Martin, J. R., & White, P. R. R. (2005). *The Language of Evaluation: Appraisal in English*. Palgrave. ✅ doi:10.1057/9780230511910 | engagement、graduation、attitude | `limit` 的强度校准；禁止无依据的 booster |
| Grice, H. P. (1975). Logic and Conversation. In *Syntax and Semantics 3*, 41–58. ◻︎ | 量、质、关联、方式准则 | TS ≤ 40 字；一节一个主张 |
| Sperber, D., & Wilson, D. (1986/1995). *Relevance: Communication and Cognition*. Blackwell. ◻︎ | 关联＝语境效果 / 处理努力 | `turn` 必须换来解释收益（否则删）；`mechanism` 存在的理由 |
| Goffman, E. (1981). *Forms of Talk*. University of Pennsylvania Press. ◻︎ | footing；participation framework | 听众站位与 Q&A 设计 |
| van Eemeren, F. H., & Grootendorst, R. (2004). *A Systematic Theory of Argumentation*. Cambridge UP. ◻︎ | 语用辩证；反稻草人 | Gate B 的反稻草人检查项 |
| Adam, J.-M. (1992/2017). *Les textes: types et prototypes*. Armand Colin. ✅ doi:10.3917/arco.adam.2017.01 | 文本序列类型：叙事、论辩、解释、描述、对话 | 每节标注功能类型，防止"全是解释"或"全是叙事" |

---

## 6. 明确**不**采用的做法

- **不做完整 RST 篇章树自动解析**（Taboada & Mann 2006 已说明关系判定依赖读者意图）：harness 只借用关系**词表**与可成立性约束。
- **不采用"修辞即操纵"的强版本**：Atkinson/Heritage 证明装置有效，但本 harness 把有效性限制在"放大真实判断"，用 `limit` 与反稻草人检查约束。
- **不用"演讲技巧"类畅销书替代学理**：装置可以借，但证据等级按上述文献判定。
