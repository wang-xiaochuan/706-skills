---
name: lark-docx-editor
description: >
  飞书文档（Docx）完整编辑能力。封装了飞书开放平台 Docx block API，支持读取、创建、更新、删除文档 block。
  当用户提到「在飞书写文档」「编辑飞书文档」「飞书文档上加一段」「修改飞书文档内容」「飞书文档排版」
  「帮我写进飞书」「更新飞书文档」「飞书 docx 编辑」「lark 文档编辑」时触发。
  也当用户给了飞书文档链接或 document_id 并想操作内容时触发。
  注意：当前 MCP 只有 rawContent（读纯文本）和 import（导入 Markdown 创建新文档）两个能力，
  本 skill 补齐了 block 级增删改查。
---

> ⚠️ **本 skill 尚未完整。** 它封装的 `scripts/lark_docx.py`
> （飞书 Docx block API 的 Python 封装，仅用标准库 `urllib` + `json`）未随仓库提供。
> 下面记录的是 API 用法与 block 结构的规格，**需要你按此实现该脚本**才能实际运行。

# Lark Docx Editor

## 你在做什么

你正在通过飞书开放平台 REST API 操作飞书文档（Docx）的 block 结构。
你有完整的 block 级 CRUD 能力：读取文档结构、创建段落/标题/列表、更新文本、删除内容。

## 核心工具

`scripts/lark_docx.py` — 飞书 Docx API 的 Python 封装，零外部依赖（仅用标准库 `urllib` + `json`）。

### 命令速查

```bash
# 获取文档所有 block 结构
python scripts/lark_docx.py blocks <document_id>

# 获取某个 block 的子节点
python scripts/lark_docx.py children <document_id> <block_id>

# 获取某个 block 的内容
python scripts/lark_docx.py get <document_id> <block_id>

# 获取文档纯文本
python scripts/lark_docx.py raw <document_id>

# 创建 block（在指定 block 下添加子节点）
python scripts/lark_docx.py create <document_id> <block_id> '<json_payload>'

# 快捷创建：追加文本段落
python scripts/lark_docx.py append-text <document_id> <block_id> '<text_content>'

# 快捷创建：追加标题 (heading1-9)
python scripts/lark_docx.py append-heading <document_id> <block_id> <level> '<text>'

# 快捷创建：追加无序列表
python scripts/lark_docx.py append-bullet <document_id> <block_id> '<text>'

# 快捷创建：追加有序列表
python scripts/lark_docx.py append-ordered <document_id> <block_id> '<text>'

# 更新 block 文本内容
python scripts/lark_docx.py update-text <document_id> <block_id> '<new_text>'

# 批量更新 block
python scripts/lark_docx.py batch-update <document_id> '<json_payload>'

# 删除 block 的子节点
python scripts/lark_docx.py delete <document_id> <block_id> '<json_payload>'

# 替换文档全部内容（先用 Markdown 写，再导入）
python scripts/lark_docx.py replace-content <document_id> '<markdown_content>'
```

## 工作流

### 1. 了解文档结构

先获取文档 block 树，了解现有结构：

```bash
python scripts/lark_docx.py blocks <document_id>
```

文档的根 block（Page）的 `block_id` 与 `document_id` 相同。
从返回的树结构中可以看到每个 block 的类型（text/heading1/bullet 等）、内容和父子关系。

### 2. 确定操作位置

根据 block 树找到要操作的目标 block_id：
- 要在段落下追加内容 → 使用该段落的 `block_id` 作为父节点
- 要修改某段文字 → 使用该段的 `block_id`
- 要在整个文档末尾追加 → 使用 `document_id` 作为父节点

### 3. 执行编辑操作

使用上述快捷命令或 `create`/`update-text`/`delete` 命令执行操作。

### 4. 验证结果

操作后重新获取 block 结构，确认改动生效。

## Block 类型参考

| BlockType | 说明 | 支持创建 |
|-----------|------|:---:|
| `page` | 文档根节点 | - |
| `text` | 文本段落 | 是 |
| `heading1`-`heading9` | 标题 | 是 |
| `bullet` | 无序列表 | 是 |
| `ordered` | 有序列表 | 是 |
| `code` | 代码块 | 是 |
| `quote` | 引用 | 是 |
| `callout` | 高亮块 | 是 |
| `divider` | 分割线 | 是 |
| `image` | 图片 | 是 |
| `table` | 表格 | 是 |
| `grid` | 分栏 | 是 |
| `todo` | 待办 | 是 |
| `task` | 任务 | 否 |
| `diagram` | 流程图 | 否 |
| `bitable` | 多维表格 | 是 |
| `sheet` | 电子表格 | 是 |

## 认证

脚本自动从 `~/.config/opencode/lark-mcp.json` 读取 appId/appSecret，
通过飞书 Open API 获取 tenant_access_token。
Token 在进程生命周期内缓存，过期自动刷新。

## 配套 Skill

- `wechat-publish` — 从飞书/Notion 文档生成微信公众号推文
- `706-notion-writer` — 在 Notion 上撰写活动文章
- 其他需要读写飞书文档内容的 skill 均可调用本脚本
