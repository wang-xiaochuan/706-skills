---
name: wechat-image-archive
description: 微信上下文同步入口。用于从指定微信群/联系人/本地微信缓存中同步上下文，支持三类下游：① 媒体素材 route：扫描微信图片文件夹到 706-media/inbox，再交给 media-ingest 做图像识别、OCR、确认入库；② 群总结 route：按用户自然语言描述的范围总结群聊主题、共识、分歧、任务和可转发摘要，例如“最近一百条”“昨天到今天早上”“从上次同步后继续”“只看报名相关”；③ 关系维护 route：读取指定对话或用户提供的聊天 transcript，总结关系上下文、承诺、风险、下一步跟进，并更新客户/伙伴关系维护文档。触发表达：「整理 X 群最近的图」「扫描微信图片缓存」「同步这个微信对话」「总结这个群」「写群总结」「看一下昨天聊了什么」「接着上次同步」「总结这个客户聊天」「更新客户关系文档」。必须兼容 Claude CLI：没有 MCP 时接受本地 transcript 文件或用户粘贴聊天文本。
---

# WeChat Context Sync — 微信上下文同步入口

这个 skill 是一个 **WeChat 上下文端口**，不是单纯的图片归档器。它负责把微信里的某个对话、群聊或本地缓存转成 706 工作系统可以继续使用的结构化上下文。

## 三条 Route

| Route | 什么时候用 | 输出 |
|------|------------|------|
| **媒体素材 route** | 用户要整理微信群图片、扫描微信图片缓存、把图片入库 | `706-media/inbox/wechat-image-import/<batch>/`，再交给 `media-ingest` |
| **群总结 route** | 用户要总结某个群最近讨论、沉淀共识、提取任务、写群周报/日报 | 群总结 markdown、任务清单、可转发摘要；可写入项目 `inbox/` 或用户指定文档 |
| **关系维护 route** | 用户要同步某个客户/伙伴/联系人对话，总结上下文、更新关系维护文档、提取跟进事项 | 用户指定 CRM/伙伴文档；若无指定，先写入对应 partnership 项目 `inbox/` |

多条 route 可以同时发生：例如先总结某个群过去一天上下文，再把同一批图片入库，并把对外合作线索写进关系维护文档。

## 输入

- `chat_name` 可选：微信群名或联系人名。有 MCP 时可直接抓；没有 MCP 时让用户提供 transcript。
- `transcript_path` 可选：Claude CLI 下推荐提供本地 `.txt` / `.md` 聊天记录文件。
- `chat_text` 可选：用户直接粘贴的聊天文本。
- `target_doc` 可选：客户关系维护文档、伙伴项目 `people.md`、CRM markdown、Notion 导出等。
- `route` 可选：`media` / `group_summary` / `relationship` / `all`。用户没说清时按需求判断。
- 范围原话可选：用户可以直接说“最近 100 条”“昨天到今天早上”“上周五之后”“从上次同步后继续”“把这次活动期间的讨论扫一下”。内部可记录为 `scope_hint`，但不要要求用户说参数名。
- 媒体参数可选：时间窗默认最近 24 小时，最大处理张数默认 200，`source_label` 作为批次说明。

## 关键路径常量

- 活跃媒体库：`$706_LOCAL/706-media/`
- 新素材入口：`$706_LOCAL/706-media/inbox/`
- 媒体索引：`$706_LOCAL/706-media/media-index.json`
- 微信图片扫描脚本：`scripts/media/scan_wechat_image_folders.py`
- 伙伴关系默认工作区：`$706_CLOUD/706/706-partnership/`
- 对话同步 checkpoint 默认文件：目标文档同目录 `.wechat-context-sync-state.json`；没有目标文档时写到对应项目 `system/wechat-context-sync-state.json`。

不要把新材料写到同级旧库 `$706_CLOUD/706-media/`。

### 扫描器运行须知（2026-09 实测）

- 遍历微信容器很慢：实测 **2–3 分钟墙钟**、CPU 不到 1 秒，几乎全是 I/O 等待。`--max-count` 只限制入选张数，**不缩短目录遍历**。所以在有超时限制的环境里必须**放后台任务跑**，不要用 3 分钟内的前台调用。
- 微信 4.x 的 `msg/attach/**/Img/*.dat` 是加密的，需要 `--key-file`（默认位置 `706-skills/infra/wechat-dat-decrypt/wechat_image_keys.json`）。**本机目前没有这个 key 文件**，因此 .dat 会以 `decrypted: false` 返回，只有 `cache/*/Message/*/Thumb` 下的 jpg 可以直接看。没有 key 时不要假装能读图，直接告诉用户「这批是加密 .dat，需要先补 key」。
- 需要解密时显式传：`--key-file <path>`，或 `--aes-key <16位hex> --xor-key <十进制或0xhex>`。
- 偶发 `InterruptedError: [Errno 4] Interrupted system call`（微信容器 I/O 被系统中断）属正常抖动，重跑一次即可，不要判定脚本损坏。
- 工作区根目录默认已跟随到活跃系统 `~/dev/706-local-os`（旧 OneDrive 路径仅作回退，可用环境变量 `SEVENOS_WORKSPACE` 覆盖）。

## 获取对话上下文

### 自然语言范围解析

用户可以自然地描述扫描范围。先理解用户想要的边界，再归一化成内部扫描计划，并在输出 frontmatter 或执行记录里写明 `normalized_scope`。不要要求用户学习内部字段名。

| 用户可能怎么说 | 归一化意图 | 执行方式 |
|---------------|------------|----------|
| “最近 100 条”“往前看 200 条”“先扫一小段看看” | 按消息数量 | MCP 调 `fetch_messages_by_chat(chat_name, last_n=N)`；CLI transcript 取末尾 N 条消息 |
| “今天”“昨天到今天早上”“过去 24 小时”“这一周” | 按时间窗口 | 需要时间戳；MCP 若只返回无时间消息，先多抓一段再标注“时间过滤能力有限” |
| “从上次同步后继续”“扫到上次没扫到的地方”“接着上次来” | 按 checkpoint 增量 | 读取 checkpoint，跳过已处理消息；用户确认本次总结可用后再更新 checkpoint |
| “从活动开始到现在”“6 月 15 之后”“周五下午那段”“某人发通知之后” | 按事件/锚点 | 在 transcript 里找时间或锚点消息；找不到时先让用户补一个锚点或改用最近 N 条 |
| “把这次合作相关的都扫一下”“只看报名/财务/场地相关” | 按主题过滤 | 先抓较宽范围，再按主题筛选；在摘要中说明可能漏掉隐晦表达 |
| “粗略看一下”“先别太细” | 低成本概览 | 默认最近 50-100 条，只输出主题和风险 |
| “完整整理”“做成可归档版本” | 高完整度整理 | 抓更大范围，保留证据节选，必要时分批处理并建立 checkpoint |

Checkpoint 建议记录：

```json
{
  "chat_name": "群名或联系人",
  "last_synced_at": "2026-06-17T15:40:00+08:00",
  "last_message_fingerprint": "sha256(sender|text|rough_time)",
  "last_message_excerpt": "最后一条已处理消息摘录",
  "last_route": "group_summary"
}
```

内部记录建议使用：

```json
{
  "scope_hint": "用户原话",
  "normalized_scope": {
    "mode": "message_count | time_window | checkpoint_delta | explicit_anchor | topic_filter",
    "last_n": 100,
    "time_window": "past_24h",
    "anchor": "某人发通知之后",
    "confidence": "high | medium | low"
  }
}
```

MCP 当前返回字段可能只有 `sender` 和 `text`，没有可靠时间戳。遇到这种情况，“最近 N 条”是最可靠模式；时间窗口、事件锚点和 checkpoint 增量要依赖 transcript 文件、用户粘贴的带时间聊天记录，或未来增强版 MCP 才能严格执行。

### MCP 可用时

如果当前环境有 `mcp__wechat_mcp__fetch_messages_by_chat`，并且用户给了 `chat_name`：

1. 根据用户的自然语言范围推导 `last_n`。默认群总结 100 条、关系维护 50 条；不确定时先抓 100 条。
2. 只读取，不发送任何微信消息。
3. 返回 `candidates` 时让用户选择精确群名，不要打开相似群。
4. 返回 `error` 时转入 Claude CLI fallback：请用户提供 transcript 文件或粘贴文本。

### Claude CLI / MCP 不可用时

Claude CLI 前端不一定有 WeChat MCP。此时不要卡住：

1. 接受用户提供的 `transcript_path`，例如 `~/Downloads/wechat-chat.md`。
2. 或接受用户直接粘贴的聊天记录。
3. 如果用户只给了 `chat_name`，说明当前 CLI 无法直接读取微信对话，请用户导出/复制最近聊天文本；媒体扫描仍可通过本地脚本继续。
4. 对话文本可以很粗糙，只要包含时间、发言人、内容即可；没有时间戳时在摘要中标注“时间待确认”。

## Route A：媒体素材入库

运行只读扫描器，默认最近 24 小时、最多 200 张：

```bash
python3 "scripts/media/scan_wechat_image_folders.py" \
  --since-minutes 1440 \
  --max-count 200 \
  --output-root "$706_LOCAL/706-media/inbox" \
  --source-label "<chat_name 或用户给的批次说明>"
```

先不确定范围时 dry-run：

```bash
python3 "scripts/media/scan_wechat_image_folders.py" \
  --since-minutes 1440 \
  --max-count 50 \
  --dry-run
```

扫描器覆盖：

- 旧缓存：`2.0b4.0.9/*/Message/MessageTemp/*/Image`
- 新缓存：`xwechat_files/*/cache/YYYY-MM/Message/*/Thumb`

输出批次：

```text
706-media/inbox/wechat-image-import/<YYYYMMDD-HHMMSS>/
├── images/
├── _manifest.json
└── _scan-report.md
```

然后按 `media-ingest` 的”路径 W”处理：Ollama/MiniCPM-V 视觉 caption、tesseract OCR 补充、用户确认、正式入库、更新 `media-index.json`。

关键原则：图像识别只说明画面像什么，活动归属必须结合聊天上下文、OCR、文件时间、已有 706 项目常识和用户确认。

## Route B：群总结

当用户说“总结这个群”“写群总结”“扫描过去 100 条”“看这个群过去一天聊了什么”“从上次没扫到的地方继续”时，走这个 route。

### 1. 读取范围

优先按用户的自然语言范围执行：

- 他说“最近 N 条”就按数量抓取。
- 他说“过去一天/一周/某个日期之后”就按时间抓取；没有时间戳时说明只能近似。
- 他说“从上次继续”就读取 checkpoint，生成增量总结。
- 他说“某个事件之后”就找锚点消息；找不到锚点时让用户补充。
- 他说“只看某类事”就按主题过滤，但在摘要中说明主题过滤可能漏掉隐晦表达。
- 用户没说范围时，默认最近 100 条。

### 2. 总结结构

群总结默认输出：

```markdown
---
source: wechat-context-sync
route: group_summary
chat_name: <群名>
scope_hint: <用户原话>
normalized_scope: <message_count / time_window / checkpoint_delta / explicit_anchor / topic_filter>
synced_at: <YYYY-MM-DD HH:mm>
---

# <群名> 群总结

## 一句话

## 主要话题
- 话题 1：发生了什么，谁参与，结论是什么

## 共识 / 决定
- ...

## 分歧 / 未定
- ...

## 跟进事项
| 优先级 | 负责人 | 事项 | 截止/建议时间 | 证据 |
|--------|--------|------|----------------|------|

## 可转发摘要
适合发回群里或发给组织者的短版摘要。

## 证据节选
- [时间/发言人] 原话或短摘录

## 待确认
- 时间不明、发言人不明、推断不确定的地方
```

### 3. 写入位置

如果用户给了 `target_doc`，追加到目标文档，不要全文替换。

如果没有目标文档：

- 与具体项目/活动强相关：写到对应项目 `inbox/wechat-summary-<YYYYMMDD>-<slug>.md`。
- 伙伴/合作群：写到 `706-partnership/international-cooperation/inbox/wechat-summary-<YYYYMMDD>-<slug>.md`。
- 归属不明：先在对话里给摘要，不长期写入。

### 4. 更新 checkpoint

只有用户确认总结质量可以接受后，才更新 checkpoint。checkpoint 更新到目标文档同目录 `.wechat-context-sync-state.json`；没有目标文档但已写入项目 inbox 时，写到该项目 `system/wechat-context-sync-state.json`。

不要因为一次失败总结推进 checkpoint，否则下次会漏扫。

## Route C：关系维护 / 客户上下文同步

当用户说“同步这个对话”“总结这个客户聊天”“更新客户关系维护文档”“看看这个联系人下一步怎么跟进”时，走这个 route。

### 1. 读取材料

优先级：

1. MCP 抓到的对话消息。
2. 用户提供的 transcript 文件。
3. 用户粘贴的聊天文本。

如果还需要媒体上下文，可以同时引用本批图片 `_manifest.json` 和 `_scan-report.md`，但不要把图片识别结果当作关系事实。

### 2. 提取关系状态

从对话中提取：

- 对象：联系人/机构/群名、角色、项目关系。
- 当前关系阶段：新线索、初步沟通、合作推进、等待对方、需要我方回复、沉默/冷却、已完成。
- 对方关心的问题、资源、限制、情绪和隐含需求。
- 我方承诺、对方承诺、明确时间点。
- 待办事项：谁、做什么、何时、依赖什么。
- 风险：误解、延期、敏感信息、还没有被确认的推断。
- 下一次跟进建议：建议话术、发送时间、需要准备的材料。

### 3. 输出确认摘要

更新文档前，先给用户看一个确认摘要：

```markdown
## 对话摘要
- 对象：
- 关系阶段：
- 最近进展：
- 对方关心：
- 我方承诺：
- 对方承诺：
- 风险/不确定：

## 跟进事项
| 优先级 | 负责人 | 事项 | 截止/建议时间 | 证据 |
|--------|--------|------|----------------|------|

## 建议下一步
- 建议话术：
- 需要准备：
```

如果摘要里有高影响推断，明确标注“推断，待确认”。

### 4. 更新目标文档

如果用户给了 `target_doc`，按原有结构追加或更新，不要整篇重写。

如果用户没给目标文档：

- 伙伴/机构/国际合作类：默认写到 `706-partnership/international-cooperation/inbox/wechat-context-<YYYYMMDD>-<slug>.md`。
- 具体活动合作：写到对应 `706-production-event/<project>/inbox/`，如果项目不明确先放 partnership inbox。
- 纯个人 CRM 或不属于 706 的客户关系：先问用户目标路径，不要擅自放进 706 项目库。

文档更新模板：

```markdown
---
source: wechat-context-sync
chat_name: <群名或联系人>
synced_at: <YYYY-MM-DD HH:mm>
route: relationship
---

# <对象> 微信上下文同步

## 本次同步摘要
...

## 跟进事项
...

## 证据节选
- [时间/发言人] 原话或短摘录

## 待确认
...
```

## Claude CLI 使用方式

CLI 下推荐这样调用：

```text
请使用 wechat-image-archive skill。
route: group_summary
transcript_path: /path/to/wechat-chat.md
我想扫的范围：最近 100 条，或者从昨天活动开始之后都看一下
目标：总结这个群，输出主要话题、共识、分歧、任务和可转发摘要。
```

媒体扫描仍可直接在 CLI 里运行扫描脚本；关系同步则依赖用户提供 transcript 文件或粘贴文本。不要要求 CLI 必须能打开桌面微信。

## 硬规则

- 不代发任何微信消息。
- 不修改微信缓存，只读或复制。
- 敏感对话先摘要后确认，再写入长期文档。
- 不把未经确认的推断写成事实。
- 群总结要区分“事实、决定、建议、推断”，不要把热闹聊天误写成已决定事项。
- checkpoint 只有在用户确认总结可用后更新。
- 新微信图片先进入 `706-media/inbox/`，不要直接写正式目录。
- 关系维护文档优先追加小节或更新局部，不要全文替换。
- v1 不修改 `wechat-mcp`；MCP 工具化留到 v2。
- v1 不解析 `Bubble/*.dat`，只处理可直接读取的图片文件。
