---
name: rhetorical-structure-harness
description: >
  为口述场景（演讲、路演、答辩、圆桌、开场分享、TED 式短讲）搭建两层修辞结构 harness：
  第一层把「场合—听众—目的」推导成大纲（audience state machine），第二层把每一节推导成
  topic sentence + bullet 修辞动作。结构依据来自修辞学、叙事学与话语研究的公开文献
  （Bitzer、Toulmin、Mann & Thompson 的 RST、Perelman、Labov、Swales、Atkinson 等）。
  触发：用户说「按修辞结构搭」「rhetorical structure」「这个演讲的骨架」「提纲→逐节→口播稿」
  「为什么这条 bullet 放这里」「把这篇稿子反推成结构」，或在准备一场有听众、有目的、有时长的口述交付时。
  不用于：成片剪辑、素材提取、书面长文、纯翻译、没有听众与时长的自由写作。
version: 0.1.0
---

# 口述修辞结构 Harness（Rhetorical Structure Harness）

把「我想讲的东西」变成「听众会当场被推动的结构」。

它不替你写词，它管两件容易混在一起的事：

```text
brief（薄输入）  →  Layer 1 架构：为什么是这个顺序
                 →  Layer 2 修辞：为什么是这个说法
                 →  script / delivery（薄输出）
```

**两层的分工**：第一层的对象是**听众的信念状态**，产出大纲；第二层的对象是**每一节的论证体**，产出 topic sentence 与 bullet。第二层填不动时，说明第一层那节的状态转移是错的——回上一层，不许硬填。

## 这套结构的依据

设计不是凭手感。每一处规则都能追到文献，映射表见 [references/literature-base.md](references/literature-base.md)。最吃重的四块：

- **Bitzer (1968) 的 rhetorical situation** → brief 的三格：exigence / audience / constraints。
- **Toulmin (1958) 的论证模型** → 每节的 topic sentence 是 claim，bullet 是 data / warrant / backing / qualifier / rebuttal。
- **Mann & Thompson (1988) 的 Rhetorical Structure Theory** → 每条 bullet 是一个 nucleus–satellite 关系，不是一条事实。
- **Atkinson (1984) / Heritage & Greatbatch (1986) 对现场掌声的研究** → 口述独有的可听装置：三段式列举、对照对、谜题—解答、标题—重击。

## 最短读取路径

1. 读本文件，确定执行模式与当前阶段。
2. 第一层：读 [references/layer-1-architecture.md](references/layer-1-architecture.md)。
3. 第二层：读 [references/layer-2-rhetoric.md](references/layer-2-rhetoric.md)。
4. 涉及时长、朗读、Q&A、口述语言特征：读 [references/oral-delivery.md](references/oral-delivery.md)。
5. 需要判断「这条规则为什么存在」：读 [references/literature-base.md](references/literature-base.md)，不要为写稿全量加载。

## 判断执行模式

写入 `brief.md`，模式决定停不停，不改变结构标准：

- **plan_only**：只产 brief 与架构，不逐节展开、不写口播稿。
- **staged**：每个门禁后停下等确认。默认。
- **continuous**：用户明确要求「一次做到口播稿」时连续推进，只在缺会改变结果的授权或事实时停。
- **revision**：已有讲稿，先反推成 Layer-1 卡与 Layer-2 moves，再做结构审计与重建；不得直接在旧稿上改词。

## 生命周期与门禁

| 阶段 | 产出 | 门禁 |
|---|---|---|
| 00 brief | `brief.md` | Gate 0：六格非空，purpose 与 takeaway 各一句 |
| 01 architecture | `architecture.md`（Layer 1） | **Gate A**，见 layer-1 文件 |
| 02 rhetoric | `sections/NN-*.md`（Layer 2） | **Gate B**，见 layer-2 文件 |
| 03 script | `script.md` 口播稿 | Gate C：字数／时长、口述特征、边界表齐全 |
| 04 delivery | `delivery-notes.md` | Gate D：朗读实测、hook、landing、Q&A |
| 05 package | 提词版／PDF／slides 骨架 | 用户指定格式 |

机器可检的门禁优先用脚本，不靠自评：

```bash
python3 scripts/init_talk_harness.py --root /abs/path --title "标题" --minutes 6
python3 scripts/check_architecture.py /abs/path
python3 scripts/check_moves.py /abs/path
```

## 核心控制面

- `brief.md`：场合、听众、目的、takeaway、约束、证据入口。
- `architecture.md`：原型、张力、状态链、每节卡、预算。
- `sections/NN-*.md`：每节的 claim 与 moves。
- `state.csv`：阶段状态，进行中恰好一个 `ACTIVE`。
- `decisions.md`：用户修正、命名、删减决定。
- `audit/audit-summary.md`：各门禁当前结论与未通过项。

## 修辞边界（硬检查，非道德声明）

口述修辞只用于**让真实判断被听见**。以下做成检查项，不是提醒：

- 禁：伪造紧迫感、隐去不确定性、把相关写成因果、用权威或情绪顶替证据、立稻草人。
- 必：每条 `evidence` 配一条 `limit`（能证什么／不能证什么），全场边界单列成表。
- 必：`turn` 不得建立在被裁剪的事实上；反稻草人检查见 layer-2 Gate B。

## 与邻近技能的分工

- `medium-research-report-harness`：书面长文的证据轨／叙事轨／出版层。本 skill **消费**它的来源与 claim 登记，不管理语料。
- `prewriting`：把材料提成可追溯笔记。本 skill 的上游，不重复提取。
- `rhetorical-structure-harness` 与 `706-ghostwriter`：后者是对话式代笔，前者是结构推导。
- `speech-to-attention-video`：讲完之后从录像剪片。本 skill 管讲之前的结构。
- `research-writing-coach`：陪练用户自己写。本 skill 可被用作其结构工具，但不代替其判断归属。

## 验收

- 每一节都能回答：它让听众从什么状态到什么状态、凭什么、留下什么问题。
- 每条 bullet 有唯一修辞动作；关键动作齐全且顺序合法。
- 时长预算与实际口播在 ±10% 内。
- 全部数字能追到证据入口，或显式标为「断言」。
- 边界表完整，讲者能逐条复述自己不能 claim 的东西。
