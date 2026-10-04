# 706 Skills

**706 青年空间在运营一个真实社区时积累的一套 AI agent 技能集。41 个 skill。**

这些不是演示用的玩具 skill。它们是我们在真实运营里反复用、反复改出来的东西：
写公众号、做小红书、归档微信群素材、剪会议视频、写研究长文、审简历、做活动排版、
给社区里的重复劳动找自动化出口。

我们希望它们对别的社区、写作者和研究者也用得上，所以开源出来。

---

## 这个仓库是什么

一个 **skill 集合**。每个目录是一个独立的 skill，遵循通用的 `SKILL.md` 约定：

```
<skill-name>/
├── SKILL.md            # 必需：触发条件 + 工作流
├── references/         # 可选：按需加载的详细规格
├── assets/             # 可选：模板
├── scripts/            # 可选：可执行脚本
└── evals/              # 可选：测试用例
```

`SKILL.md` 的 YAML frontmatter 里 `name` 与 `description` 决定这个 skill **什么时候被触发**——
`description` 里写清触发词是让 skill 好用的关键，不是装饰。

## 怎么用

**方式一：交给能读文件的 AI 助手。** 把 `SKILL.md` 和它引用的文件夹一起给它，
或在对话里直接说"读 `<路径>/SKILL.md` 并按它执行"。

**方式二：放进你的工具支持的 skill 目录。** 不同宿主（Claude Code、Codex、其他 agent 框架）
的 skill 目录位置不同，按你的宿主文档放。

**没有额外依赖。** skill 本身是 Markdown；只有 `scripts/` 里的脚本需要对应运行时
（Python 3 / Node），`requirements` 或依赖会在该 skill 的 `SKILL.md` 里写明。

## ⚠️ 路径约定（用之前先读这一段）

这些 skill 是从 706 的实际工作区里抽出来的，里面引用了我们自己的目录布局。
为了可移植，原始绝对路径已替换成变量。**你需要把它们映射到自己的目录：**

| 变量 | 含义 | 我们机器上的默认值 |
|------|------|------------------|
| `$706_LOCAL` | 本地工作区根目录 | `~/dev/706-local-os` |
| `$706_CLOUD` | 云同步区的资料根 | `~/Library/CloudStorage/OneDrive-个人/2026 dev` |
| `$CODEX_HOME` | Codex/agent 的 skill 安装目录 | `~/.codex` |

**两种改法：**

1. **设环境变量**（推荐）——如果你的宿主会把环境变量传给脚本，设好即可
2. **直接改文本**——把 `$706_LOCAL` 全局替换成你自己的路径

另外这些 skill 里会提到 `706-knowledge/`、`706-media/`、`706-system/` 这类目录名，
那是 706 的七层项目结构（`inbox / system / source / outputs / media / knowledge / archive`）。
**如果你的工作区不是这个布局，请按语义对应调整**，不要照搬。

如果你只想试一两个 skill，建议先挑下面标了「通用」的那些——它们不依赖特定目录布局。

---

## Skill 清单

### 写作与风格迁移

| Skill | 文件 | 一句话 |
|-------|-----|--------|
| `author-style-mimicry` | 6 | 以特定外国作家（中文译本）的文学声口改写公共发布内容；把"作家×译者"当复合风格单元 |
| `debotton-chen-nan-rewrite` | 2 | 改写成阿兰·德波顿（陈广兴/南治国译本《工作颂歌》）的声口，支持多轮迭代收敛 |
| `debotton-chen-nan-write` | 3 | 为活动回顾长文设计叙事、研究简报与大纲，并执行写作 |
| `scholar-analyst-rewrite` | 2 | 改写成关注中国技术社会的人类学家/社会学者/分析员的写作传统（项飙、何伟、Dan Wang） |
| `706-ghostwriter` | 2 | 通过阅读建立判断力的写作伙伴：知识摄入 → 四层审视 → 协作写作 |
| `prewriting` | 12 | 为活动或项目写作整理原始素材，产出可追溯的项目学习笔记 |
| `moments-work-diary` | 2 | 生成和迭代朋友圈/微博式工作日报，含 tone check |

### 研究与判断

| Skill | 文件 | 一句话 |
|-------|-----|--------|
| `personal-decision-harness` | 12 | 个人判断与判断能力训练系统：做、不做、换种方式做，附证据与改判条件 |
| `medium-research-report-harness` | 30 | 构建/续写/重构/审计/翻译/打包 8000–40000 字证据型研究报告 |
| `rhetorical-structure-harness` | 20 | 为演讲/路演/答辩搭两层修辞结构：场合—听众—目的 → 逐节 topic sentence |
| `literature-search` | 2 | 学术文献检索与结构化归档，产出带来源与核验状态的素材清单 |
| `706-long-article-distilling` | 2 | 把长文/PDF/报告/访谈蒸馏成八段式结构化笔记 |
| `skill-creator` | 2 | skill 评测与迭代：样例、with-skill/baseline 对照、评分与触发测试 |
| `skill-optimizer` | 1 | 从五个维度系统审查 skill 质量并输出优化报告 |

### 内容发布（公众号 / 小红书）

| Skill | 文件 | 一句话 |
|-------|-----|--------|
| `wechat-design` | 5 | 公众号排版设计系统：9 套色板 × 排版开关，自由组合 |
| `wechat-publish` | 3 | 把 Notion / Markdown 排成可粘贴进公众号编辑器的富文本 HTML |
| `wechat-publish-2.0` | 1 | 视觉控制面板 + 实时预览 + LLM 辅助调整 |
| `wechat-slides` | 2 | 竖版 HTML 图片卡片 / 截图幻灯片，默认 750×1334px |
| `xhs-copywriter` | 2 | 小红书标题、正文与话题标签 |
| `xiaohongshu-poster` | 2 | 小红书活动封面海报，默认 HTML 1080×1440px |
| `content-intelligence-search` | 2 | 跨平台内容情报：找高传播内容（阅读量/点赞量门槛） |
| `706-notion-writer` | 6 | 在 Notion 上撰写活动招募长文，遵循 706 社群调性 |

### 媒体与素材

| Skill | 文件 | 一句话 |
|-------|-----|--------|
| `media-ingest` | 2 | 处理媒体库 inbox 的待分类图片：场景识别 → 活动类型 → 地点归档 |
| `wechat-image-archive` | 2 | 微信上下文同步入口：图片素材、群总结、关系维护三条下游 |
| `wechat-article-smart-archive` | 17 | 按公众号名/关键词与时间范围发现并归档公开文章，产出可离线分享的 HTML |
| `speech-to-attention-video` | 9 | 会议/访谈/讲座素材 → 叙事版、主题版、注意力切片、字幕与交付包 |
| `706-audio-transcribe-archive` | 3 | 音频转中文时间戳转录稿，含多人说话人对齐与语料归档 |
| `video-download` | 2 | B 站 + YouTube 统一下载归档，支持批量、断点续跑、字幕抓取 |
| `image-ocr` | 1 | 本地 Tesseract 中文 OCR / 批量文字提取 |
| `image-to-html` | 2 | 图片文件夹打包成 Base64 内嵌 HTML，便于喂给模型 |

### 文档与工具

| Skill | 文件 | 一句话 |
|-------|-----|--------|
| `md-to-pdf-songti` | 2 | Markdown 经 XeLaTeX 渲染为宋体 PDF |
| `lark-docx-editor` | 1 | 飞书文档 block API 的读写编辑封装 |
| `gdocs-mcp` | 2 | Google Docs + Drive MCP 服务器（能力参考，非触发型） |
| `browser` | 1 | 浏览器自动化：导航、读取、点击、填表、截图、看控制台与网络请求 |
| `harness-goal-runner` | 5 | 设计本地 goal harness，让 agent 持续朝一个目标推进 |

### 职业

| Skill | 文件 | 一句话 |
|-------|-----|--------|
| `resume-from-evidence` | 9 | 从聊天记录 + 旧简历 + 目标岗位，经经历核验与岗位逆向分析产出真实简历 |
| `resume-hr-review` | 7 | 模拟招聘初筛 HR 做要求—证据对比，输出覆盖度与修改优先级 |

### 运营与信号（706 专用）

| Skill | 文件 | 一句话 |
|-------|-----|--------|
| `task-sync` | 1 | 任务记录的录入、同步、分配、改期、关闭与批量盘点 |
| `task-distribution` | 2 | 读取待处理条目 → 判断归属项目 → 写入对应项目任务池 |
| `panel-curator` | 2 | 研究圆桌嘉宾并整理主持指南 |
| `binance-4h-signal` | 25 | 1H K 线合成 4H，23 个指标融合 + regime 动态权重，输出交易信号 |

---

## ⚠️ 已知缺失（用之前先看）

整理这个仓库时逐个校验了 `SKILL.md` 里的内部引用，发现 **4 个 skill 引用了未随仓库提供的文件**。
已在各自的 `SKILL.md` 顶部加了说明。分成两类：

### 核心实现缺失 —— 目前是骨架，不能直接跑

| Skill | 缺什么 |
|-------|--------|
| `content-intelligence-search` | `references/wechat.md` 与 `references/xiaohongshu.md`（两个平台各自的搜索实现）。SKILL.md 只有工作流骨架 |
| `lark-docx-editor` | `scripts/lark_docx.py`（飞书 Docx block API 的 Python 封装）。SKILL.md 记录了 API 用法与 block 结构规格，但脚本本身没有 |

**我们的建议是先把它们当设计文档读，要用的话自己补实现。**
（如果你觉得放一个不能跑的 skill 反而减分，删掉这两个是最干净的处理。）

### 参考文件缺失 —— 不影响主流程

| Skill | 缺什么 |
|-------|--------|
| `skill-creator` | `references/schemas.md`（评测 schema 全文）、`assets/eval_review.html`（评审页模板） |
| `xiaohongshu-poster` | `references/template.html`（某一期的完整排版实现，原文即说明"只作参考，不要直接套用"） |

另外修复的：`wechat-image-archive`、`prewriting`、`task-sync` 三个 skill 引用的文件
原本散落在工作区其他位置，已一并打包进来并改成 skill 内相对路径，所以它们是自包含的。
`debotton-chen-nan-write` 与 `skill-creator` 的 frontmatter `name` 原本与目录名不一致，
已对齐（多数宿主的 skill 安装依赖二者一致）。



上面大部分 skill 是通用的——`rhetorical-structure-harness`、`personal-decision-harness`、
`resume-from-evidence`、`speech-to-attention-video`、`md-to-pdf-songti` 这类，
拿过去就能用，最多改一下路径。

标了「706 专用」的几个（`task-sync`、`task-distribution`、`media-ingest`、
`wechat-image-archive`、`706-notion-writer`）**和我们的目录结构、任务系统、媒体库强耦合**。
读它们主要能看的是**方法**——一个社区怎么把重复劳动拆成可自动化的 skill——
而不是直接拿来跑。用之前先看「路径约定」那一节。

## 未收录的 skill

这个仓库**只放我们自己写的**。从外部引入的 skill 有 14 个，
它们有自己的上游、许可与更新渠道，所以没有收进来。

完整名单、上游地址与许可说明见 [`VENDORED.md`](VENDORED.md)。

> 其中 `research-writing-coach` 是 **CC-BY-NC-4.0（非商业）**，
> 用之前请自己确认许可条款。

## 一些背景

706 青年空间是一个由青年自发组织、共同维护的公共空间网络，2012 年至今。
我们不是 AI 公司，只是一群用工具解决自己问题的人。

这套 skill 是我们对"一个社区需要什么基础设施"的部分回答：
把反复发生的事写下来，让它下次不用再从零开始。

## License

MIT（见 [`LICENSE`](LICENSE)）。

- 本仓库中的各 skill 如带有自己的许可声明，以该 skill 目录内的说明为准。
- 从外部引入的 skill **未收录**在本仓库，其许可见 [`VENDORED.md`](VENDORED.md)。
  其中 `research-writing-coach` 是 **CC-BY-NC-4.0（非商业）**，请自行确认条款。
