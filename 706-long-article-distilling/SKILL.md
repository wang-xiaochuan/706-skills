---
name: 706-long-article-distilling
description: 706 长文章与深度报告蒸馏系统。把散落的长文 URL、PDF、深度博客、研究报告、论文、长访谈蒸馏为 `706-knowledge/706知识库/by-topic/long-article-distilling/` 下的结构化 markdown——八段式（一句话 / 长摘要 / 核心论点 / 专名辞典 / 原文外链 / 作者保留 / 延展阅读 / 706 可用场景 / Meta Analysis），按类别归档、按时间索引，并支持自然语言检索。任何时候用户提到「蒸馏这篇」「把这篇长文蒸馏」「入库这篇长文」「处理一下 inbox」「收藏这篇文章」「扔进长文库」「找一下 706 以前关于 X 的长文」「长文库里有没有 Y」「查一下我存过的 Z」「整理一下 inbox」，或者给出一串长文 URL 要求处理，都触发这个 skill。**不处理短内容**（推文 / 小红书爆款笔记 / 动态）——遇到这类内容要明确告诉用户走另一个系统。
---

# 706 Long Article Distilling · 长文蒸馏与检索

思路起点：[awesome-openclaw-usecases / knowledge-base-rag](https://github.com/hesamsheikh/awesome-openclaw-usecases/blob/main/usecases/knowledge-base-rag.md)。本地 Markdown 版，专攻长文蒸馏。

---

## 0. 库位置

**主目录**：
```
$706_CLOUD/706-knowledge/706知识库/by-topic/long-article-distilling/
```

结构（不存在则按 `context-bootstrap.md` 规范创建）：

```
long-article-distilling/
├── README.md
├── context-bootstrap.md      ← 权威规范，先读这个
├── _inbox/queue.md           ← 待蒸馏队列
├── _archive/                 ← 原文留存（易失内容必抓）
├── by-category/              ← 主存储（一份资料只存一次）
│   ├── ai-agents/
│   ├── longevity-bio/
│   ├── robotics-hardware/
│   ├── culture-community/
│   ├── builder-villages/
│   ├── community-space/
│   └── misc/
└── timeline/YYYY-MM.md       ← 按月索引（只存链接）
```

**第一步永远是**：读 `context-bootstrap.md` 获取当前规范（模板版本 / 分类定义 / frontmatter 可能已更新）。

---

## 1. 识别用户意图

三种模式：

| 模式 | 触发 | 动作 |
|------|------|------|
| **Ingest（蒸馏入库）** | 给了 URL / 粘贴了原文 / 说"蒸馏这篇"/"处理一下 inbox" | 走 §2 |
| **Retrieve（检索）** | 自然语言提问"长文库里有没有…"/"以前蒸馏过关于…" | 走 §3 |
| **Maintain（维护）** | "整理 misc"/"合并重复"/"清理 inbox"/"月度回顾" | 走 §4 |

不确定时，直接问用户是要蒸馏还是查询。

---

## 2. Ingest 流程

### 2.1 输入来源

- 用户直接在对话里贴 URL
- `_inbox/queue.md` 里的队列
- 用户粘贴的原文（PDF / 复制文字）

### 2.2 第一步：判长短（硬门槛）

**这套系统只处理长内容**：长文（>2000 字）/ 报告 / 深度博客 / 论文 / 长访谈转写。

遇到这些情况要**停下来告诉用户**，**不蒸馏**：
- 单条推文或一组短推文串（Twitter / X）
- 小红书爆款笔记（短图文）
- 微信朋友圈 / 短动态
- 正文不足 2000 字的博客或新闻短讯

回复模板：
> "这篇是短内容（约 N 字），不适合走长文蒸馏的八段式模板，会过度填充。建议等短内容收集系统搭好后再处理，或者用户手动摘录关键句。"

只有判定为长内容才继续走 §2.3。

### 2.3 逐条蒸馏

对每条符合长内容门槛的 URL / 素材：

1. **抓取正文**（按来源选工具）
   - 通用网页 / arXiv / Medium / 博客：`WebFetch`（喂结构化 prompt，见下）
   - 微信公众号长文：`WebFetch`；抓不到让用户复制正文
   - YouTube 长访谈：抓字幕（`youtube-transcript` mcp 或用户提供）
   - PDF：用 `pdf` skill / `Read` 工具
   - Notion 页面：`notion-fetch` mcp

   **WebFetch prompt 关键**：不要只要"3–5 句摘要"，要结构化——全部章节 / 每节 2–5 句要点 / 所有专名与数据 / 8–15 条金句（中英对照）/ 外链清单 / 作者的保留意见。否则会信息塌方。

2. **存原文到 `_archive/`**
   - 路径：`_archive/YYYY-MM-DD__slug.source.md`
   - 主文件 frontmatter 加 `archive_path: ../_archive/YYYY-MM-DD__slug.source.md`
   - 稳定博客（Vitalik 官博等）可选抓；易消失内容（微信 / 社交媒体）必抓

3. **判类型 + 判类别**
   - `source_type`: article / youtube / paper / wechat / pdf / other
   - `category`: 按 `context-bootstrap.md` §5 分类边界判断，拿不准放 `misc/`

4. **生成 slug + 文件名**
   - slug：英文小写短横线，从标题提炼 3–6 个词
   - 文件名：`YYYY-MM-DD__slug.md`（日期 = **原文发布日期**，非蒸馏日期）

5. **按八段式模板写入** `by-category/<cat>/YYYY-MM-DD__slug.md`

   frontmatter 必填字段：
   ```yaml
   ---
   title: 原文标题
   source_url: https://…
   archive_path: ../_archive/YYYY-MM-DD__slug.source.md
   author: 作者
   published_at: 2026-03-15
   ingested_at: 今天日期
   source_type: article
   category: ai-agents
   tags: [claude, agent-sdk]
   lang: zh
   related_projects: []        # 若明确服务某 706 项目就填 [2050] / [mushanghai]
   ---
   ```

   正文八段：**一句话 / 长摘要（按原文章节）/ 核心论点（claim + 依据 + 推论 + 金句嵌入）/ 专名辞典（6 子区）/ 原文外链 / 作者的保留 / 延展阅读（WebSearch 找 3–7 条 + 关系标签）/ 为 706 的可用场景（6 子区）/ Meta Analysis**。

   **详细模板见 `context-bootstrap.md` §3，以那边为准**。

6. **追加到月度索引** `timeline/YYYY-MM.md`（蒸馏月份），新条目加在**最上面**：
   ```
   - 2026-04-19 · [原文标题](../by-category/ai-agents/2026-03-15__slug.md) · ai-agents · 一句话为什么蒸馏
   ```

7. **清理 inbox**：如果来自 `_inbox/queue.md`，对应行删掉或前缀 ✅

### 2.4 回报

处理完一次性告诉用户：
- 蒸馏 N 条长文，各归到哪些 category
- 跳过了几条（为什么：短内容 / 重复 / 抓不到）
- 是否有需要用户补原文的条目

---

## 3. Retrieve 流程

### 3.1 解析问题

从问题里提取：
- **主题关键词**（用于 Grep）
- **类别提示**（"生物科技" → `longevity-bio`；"AI" → `ai-agents`）
- **时间范围**（"最近" → 近 1–3 个月索引；"以前" → 全部）
- **用途意图**（"写推文" → 要金句；"做嘉宾准备" → 要专名辞典 + 核心论点；"做研究" → 要延展阅读链路）

### 3.2 检索路径（按顺序）

1. **时间线先过**：读相关 `timeline/YYYY-MM.md`
2. **类别目录筛**：`Glob` 相关 `by-category/<cat>/*.md`
3. **三路 Grep**：tags / category / related_projects 关键词跨整个 `by-category/` 搜，带 `-n`
4. **逐篇 Read**：选 3–5 篇最相关的读 frontmatter + 核心论点 + 延展阅读

### 3.3 返回格式

给用户 **3–5 条**，每条：
```
**标题** · 2026-03-15 · ai-agents
出处: https://原文链接
为什么相关: 一句话
可引用片段（含中英）:
> 摘录原文关键句 / 中译

本地路径: [相对链接](…)
```

**完全没匹配时**：老实说"长文库里没有合适的，建议把以下 URL 先蒸馏：…"，而不是编。

---

## 4. Maintain（维护）

### 4.1 misc 归档

用户说"整理 misc"时：逐篇读 `by-category/misc/`，判断是否已能归到确定类别，能就 `mv` 挪过去，并更新 timeline 里的路径。

### 4.2 重复检测

蒸馏前先 grep `source_url` 是否已存在；若存在提示用户"这条已蒸馏过（文件 xxx），是覆盖/追加/跳过？"。

### 4.3 月度回顾

用户说"回顾 YYYY-MM"时：
- 统计：蒸馏 N 条，各 category 分布
- 列出过去 1 个月被**引用过**（出现在其他文档里）的条目 vs 从未被引用的
- 提示长期不被引用的是否考虑删

---

## 5. 与其他 skill 的协作

- **706-notion-writer / xhs-copywriter / panel-curator**：写作前可主动调用 §3 检索同主题历史蒸馏笔记，把出处塞进 context（暂未强制钩子，用户显式要求时再做；长期计划见 `context-bootstrap.md` §4.3）
- **content-intelligence-search**：搜来的爆款笔记属于短内容，**不走长文蒸馏**
- **wechat-publish / xiaohongshu-poster**：不直接交互

---

## 6. 边界与禁忌

- **没有出处的资料不蒸馏**（无 `source_url` 的零散观点归到对应 project 的笔记区）
- **只服务单个项目的资料不蒸馏**（应放 `by-project/<proj>/03-媒体区/`）
- **短内容不蒸馏**（推文 / 小红书 / 动态 / <2000 字短讯）
- **不抓取需要登录才能访问的私密内容**
- **不编造摘要、金句或延展阅读**——抓不到原文就明确告诉用户"需要补原文"；延展阅读必须是 WebSearch 真实命中的
