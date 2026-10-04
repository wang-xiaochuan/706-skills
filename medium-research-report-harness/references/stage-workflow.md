# 十四阶段工作流

本文件是执行手册。先确定当前阶段，再读取对应输入；不要把后续阶段提前产出的半成品当作完成。

## 状态规则

`state.csv` 使用三种状态：

- `PASSED`：交接物存在，门禁通过。
- `ACTIVE`：当前唯一允许新增正式产出的阶段。
- `LOCKED`：上游未通过，不得创建正式交付；可以记录想法到 `decisions.md`，不能抢跑。

执行中恰好一个 `ACTIVE`。全部完成时可以没有 `ACTIVE`，但所有行必须为 `PASSED`。

用户明确要求连续执行时，不需要在每一阶段停下来聊天；仍需在文件中完成交接与门禁。

## 00 Scope

### 输入

- 用户请求、已有材料路径、现有稿件与历史决定。

### 动作

- 写清研究对象、排除对象、地理／时间范围、目标读者、主语言、长度、语体、交付格式。
- 定义术语，尤其是相邻但不能混同的对象。
- 写完成条件、隐私边界、外部发布边界和执行模式。
- 若任务是 revision，冻结旧稿并记录哈希、字数、章节、图片、注释和来源数量。

### 交接

- `goal.md`

### Gate

- 所有必填字段非空；“研究完成”和“文章完成”有可检验定义。

## 01 Corpus

### 动作

- 原件复制归档，不在 Downloads 或外部库上直接改写。
- 网页保存 raw HTML、抽取正文、图片和元数据；PDF／Word／音频保留原件并生成派生文本。
- `corpus-manifest.csv` 登记文件、原始路径／URL、来源类型、日期、大小、SHA-256、抽取状态。
- 区分 `raw` 和 `derived`；摘要、OCR 和模型抽取不是原始证据。

### 交接

- `source/corpus-manifest.csv`
- `source/raw/`
- `source/extracted/`

### Gate

- manifest 中每个原件路径存在；哈希非空；派生材料可回指原件。

## 02 Evidence map

### 动作

- 给来源分配稳定 ID。
- 分开：原始档案／法律、官方或项目自述、独立报道、同行评审、聚合目录、口述、文学影视、作者推论。
- 建立 `claim-evidence-register.csv`，先登记高风险主张：数字、因果、法律效力、现状、规模、代表性、人物行为。
- 把“来源能证明什么”和“不能证明什么”写成字段。

### 交接

- `source/source-register.csv`
- `research/claim-evidence-register.csv`

### Gate

- source ID 唯一；硬事实没有只靠不相干来源；自述和独立证据可区分。

## 03 Coverage

### 动作

- 根据研究问题建立地域、时间、平台、语言、学科或群体矩阵。
- 每个单元写最小检索式、搜索日期、工具／数据库、命中、排除和下一步。
- 新闻与时效事实执行在线复核；特定论文、网页或政策优先原页。
- 保存检索日志和必要的网页快照；不要把搜索摘要当完整证据。

### 交接

- `research/search-protocol.md`
- `research/coverage-matrix.csv`

### Gate

- 计划覆盖单元无空白；未命中有明确记录；没有由覆盖缺口推导不存在。

## 04 Structured research

### 动作

- 按研究对象建立 case、policy、timeline 或其他母表。
- 一行只代表一个定义清楚的单位；品牌、物理节点、活动、计划和历史版本不要强行合并。
- 使用受控状态词；用 `unknown` 代替猜测。
- 所有候选获得 `retained / merged / excluded / lead_only` 之一；删除理由写入 removal log。
- 发现同名错名、重复、地域不匹配或规模口径冲突时先修母表，再改正文。

### 交接

- `research/case-register.csv`
- `research/unknowns.csv`
- `research/removal-log.csv`
- 项目需要的政策／年表母表

### Gate

- ID、状态、必要字段、来源链接、计数口径和跨表关系通过自动检查。

## 05 Prewriting

对全量登记材料做八维抽取；不是八篇独立文章：

1. **时间**：长时段、加速／悬置、Before/After、状态冲突。
2. **话语**：逐字引语、术语、命名权、回避带、翻译风险。
3. **物与空间**：空间谱系、物件链、非人事件、视觉证据。
4. **情感**：氛围变化、身体动作、疲惫、退出和未解决张力。
5. **组织**：钱、房、准入、劳动、权力、扩张／关闭／再生。
6. **上下文**：历史、经济、政策、平行案例、外国读者概念。
7. **品味**：行动者、时间、尺度、负空间、因果、道德框架、AI 腔。
8. **数据**：数字、单位、口径、冲突、不能相加项、未知量。

每份抽取标注事实位置、来源 ID、可写用途和缺口。多代理不可用时依次完成，不要假装并行独立验证。

### 交接

- `prewriting/01-time.md` 至 `08-data.md`
- 一份跨维度对齐报告

### Gate

- 高风险事实、核心张力、沉默主体和主要数据冲突都有记录。

## 06 Architecture

### 动作

- 提出 2–4 条叙事 arc，说明主问题、视角、时间结构、关键物件、机制和风险。
- 选定 arc 后写详细 outline；每章说明论点、建材、场景、机制、证据边界、转场和预计长度。
- Revision 模式建立 `content-conservation.csv`：旧内容块逐项映射到新位置。
- 检测只改标题／子标题而段落顺序未变的假重写。
- 附录承担查找，正文承担论证；提前决定哪些信息应迁出正文。

### 交接

- `writing/narrative-options.md`
- `writing/outline.md`
- `writing/content-conservation.csv`

### Gate

- outline 的章节功能真实不同；案例按机制归组；旧内容没有静默消失。

## 07 Primary draft

### 动作

- 以母语写作，避免同时翻译导致事实和结构漂移。
- 每章建立一行 `chapter-audit.csv`，填写 claim、evidence、mechanism、boundary、transition。
- 使用场景和物件承载抽象分析；数字出现时给单位、时间和口径。
- 文化材料作为感受档案或 punch line，不承担硬事实。
- 每次重大用户修正进入 `decisions.md`，同时全局检索同类表述。

### 交接

- `writing/draft-primary.md`
- `writing/chapter-audit.csv`

### Gate

- 全文完整；章节有连接；没有仍以 TODO 代替的核心段落。

## 08 Research audit

### 顺序

1. 事实与时间。
2. 引文逐字与归属。
3. 数字、单位、分母和不可相加项。
4. 因果与代表性。
5. 法律／政策层级。
6. source ID、脚注和链接。
7. 隐私、口述和自述边界。

### 交接

- `audit/research-audit.md`
- 修订后的母表和正文

### Gate

- 所有高风险 claim 有 PASS、REVISE 或 UNKNOWN 处置；无悬空引用。

## 09 Narrative audit

### 动作

- 检查章节间因果桥、时间桥、对象桥和概念桥。
- 标出项目名连续堆叠、重复论断、机械警语、总结先于证据和过度转折词。
- 检查 tone、术语、叙述距离、AI 套话、营销词和道德过度收束。
- 审计 outline 是否真正实施；必要时整体重编，不能只局部补句。

### 交接

- `audit/narrative-audit.md`
- `writing/draft-primary-final.md`

### Gate

- 每章论证链完整，转场有对象，声口稳定，不靠删事实制造流畅。

## 10 Visuals

### 动作

- 图像先服务案例和论点，再服务装饰。
- 每图登记文件名、哈希、来源、caption、图中可见内容、证明任务、语言版本和公开／内部备注。
- 检查案例是否具象化；空间外景与内景、组织标识与集体活动等不同视觉任务不要互相替代。
- 对外 caption 不包含“发布前需授权”“待替换”等内部生产话语。

### 交接

- `media/images/`
- `media/image-register.csv`

### Gate

- 图片文件存在且唯一；图序连续；caption 和段落对应；来源可追踪。

## 11 Translation

### 动作

- 建立术语表与文化解释表。
- 翻译意义和证据边界，不机械复制句法。
- 对目标读者解释本地制度、节日、组织和生活概念。
- 锁定标题层级、图序、脚注调用顺序、专名和数字。

### 交接

- `writing/draft-secondary.md`
- `writing/terminology.csv`

### Gate

- 双语结构与证据序列对齐；译文独立可读；未知项没有在翻译中变确定。

## 12 Publication

### 动作

- 从锁定 Markdown 构建 HTML／DOCX／PDF，不手工维护互相漂移的四套正文。
- 正文与附录分册；完整 CSV 母表继续保留。
- 运行技术检查、可访问性检查、全页渲染和人工联系表审阅。

### 交接

- `publication/build/`
- `audit/publication-audit.md`

### Gate

- 目标格式全部实际生成并通过检查；不能只说“理论上可打开”。

## 13 Release

### 动作

- 创建完整研究包与项目方阅读包。
- README 写入口、文件作用、核验日、证据边界、页数／图数和版本。
- 删除／归档旧稿前列清单，明确目标并使用可恢复方式。
- ZIP 排除系统垃圾和内部中间件，执行解压测试与 SHA-256。

### 交接

- `publication/share-package/`
- `publication/reader-package/`
- ZIP 与 `audit/audit-summary.md`

### Gate

- 单一当前版本；读者无需理解 Harness 即可开始；完整研究链仍可复现。
