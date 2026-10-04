# CHANGELOG · 706-long-article-distilling

## 2026-04-19 · v0.5 更名为"长文蒸馏"

- **系统改名**：`706-knowledge-base` → `706-long-article-distilling`；中文名从"706 知识库"改为"706 长文蒸馏"。
- 动机：v0.1–v0.4 跑下来确认这套八段式模板**只适合长文和报告**，对短推文 / 小红书爆款 / 动态会过度填充。改名是诚实地限定适用边界。
- **硬门槛**：SKILL.md §2.2 加入长短判定前置——原文 <2000 字或属短内容类型的，停下提示用户，不蒸馏。
- 路径迁移：
  - `706-knowledge/706知识库/by-topic/knowledge-base/` → `…/by-topic/long-article-distilling/`
  - `706-skills/706-knowledge-base/` → `706-skills/706-long-article-distilling/`
- 短内容系统留待另开，不混进这里。
- `context-bootstrap.md`、`README.md`、`SKILL.md`、engineering log 关键词全部替换。

## 2026-04-19 · v0.4.1 跨 skill 钩子思路落档

- `context-bootstrap.md` §4.3 从一句话占位扩为具体实施路径：三路 Grep（tags / category / related_projects）+ 命中笔记抽核心论点+source_url+作者保留塞进 context。
- 明确**现在不做**，等 3–5 篇真实写作任务跑过再决定是否加 quotes-index / 独立 retrieval skill / 更多 frontmatter 查询字段。
- 动机：v0.4 内容模板定型后，下一个要解决的是"写作端怎么调用"，但现在样本太少，先把思路记下避免过度设计。

## 2026-04-19 · v0.4 延展阅读

- 新增段落 `## 延展阅读（他人相关论述）`，放在"作者的保留"与"为 706 的可用场景"之间。
- 要求 ingest 流程用 WebSearch 找 3–7 条其他作者 / 媒体的相关论述；每条打标签（同向扩展 / 前置文献 / 反方观点 / 实证案例 / 延伸应用 / 生态进展）+ 一句话说与本文的对话点。
- 关键目标：让每篇笔记成为"进入一个话题"的 hub，而非孤立档案。
- 回溯：3 篇 Vitalik 各补 7–9 条延展阅读。

## 2026-04-19 · v0.3 结构重整

- **金句融入论点**：不再单设"关键片段"段，金句（中英对照）分配到每个论点下作为支撑；全文金句总数 **≤ 20**。
- **专名辞典**：从一句话清单升级为 6 个子区——理论 / 人名 / 项目 / 公司 / 国家 / 数据。每条约 3 句话自包含解释（理论区附原文定位引文）。
- **706 可用场景**分 6 子区：研究 / 对外交流 / 活动与工作坊 / 微信公众号 / 小红书短文案 / 社群内部 / 其他衍生。
- **新增 Meta Analysis**：字数、阅读时长、文体、论证结构、高频关键词 Top 10、核心专名频次、可比文本、预设知识门槛、情绪基调。
- **原文独立留存**：主文件删除"原文正文"段；新建 `_archive/` 目录存档，主文件 frontmatter 加 `archive_path` 指向。
- **回溯**：3 篇 Vitalik 重写到 v0.3 规范，并抓取原文存入 `_archive/`（WebFetch 转 markdown 有轻度压缩，注明以 source_url 为准）。

## 2026-04-19 · v0.2 模板加厚

- **问题**：v0.1 对长文（>2000 字）的入库只写了一段短摘要 + 4 条英文金句，下游消费时信息量严重不够。
- **修复**：`context-bootstrap.md` §3 模板扩为八段式——一句话 / 长摘要（按原文章节）/ 核心论点（claim + 依据 + 推论）/ 关键片段（中英对照 8–15 条）/ 数据 & 专名清单 / 原文外链 / 作者保留 / 为 706 的可用场景。
- **抓取策略升级**：SKILL.md §2.2 step 1 的抓取不再只要 "3–5 句摘要"，而要求 `WebFetch` 按结构化 prompt 返回：全部章节、每节 2–5 句要点、所有专名/数据、8–15 条金句、外链清单、作者的保留意见。
- **回溯**：v0.1 入的 3 篇 Vitalik 文章已用新模板重写。

## 2026-04-19 · v0.1 初始版

- 基于 awesome-openclaw-usecases 的 knowledge-base-rag 思路，本地 Markdown 实现
- 主存储：`706-knowledge/706知识库/by-topic/long-article-distilling/by-category/`（7 类）
- 时间维度用 `timeline/YYYY-MM.md` 索引文件，不做双写
- 三种工作模式：Ingest / Retrieve / Maintain
- 统一 frontmatter（title / source_url / published_at / category / tags / related_projects）
- **待验证**：实际跑几条 URL 后再决定是否加 skill 钩子（让写作类 skill 自动检索此库）
