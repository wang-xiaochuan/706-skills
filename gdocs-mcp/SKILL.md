---
name: gdocs-mcp
description: >
  Google Docs + Drive MCP 服务器。始终在后台运行，无需触发词——所有工具通过 mcp__gdocs__* 前缀直接调用。
  不是触发型 Skill，是 MCP 能力参考文件。放在 706-skills 里是为了 Obsidian 可浏览、706 体系可追踪。
---

# gdocs-mcp · Google Docs MCP

## 类型

**MCP 服务器**（非触发型 Skill）。Claude 启动时自动拉起，工具始终可用。

## 配置

| 项 | 值 |
|----|-----|
| 包 | `gdocs-mcp` v0.5.3（npm: [gdocs-mcp](https://www.npmjs.com/package/gdocs-mcp)） |
| 仓库 | [github.com/Apurwa/gdocs-mcp](https://github.com/Apurwa/gdocs-mcp) |
| 注册位置 | `~/.claude/.mcp.json` → `mcpServers.gdocs` |
| 启动命令 | `npx gdocs-mcp` |
| Google Cloud 项目 | `gen-lang-client-0495225468` |
| OAuth Client ID | `879666853200-hdh4b6nmc2fd2566135bu0chrb2snblv.apps.googleusercontent.com` |

## 文件分布

```
~/.claude/.mcp.json                     ← MCP 注册（Claude 启动时读取）
~/.gdocs-mcp/
├── credentials.json   (600)            ← OAuth 客户端凭证
├── token.json         (600)            ← access/refresh token（自动刷新）
└── styles.json                         ← 自定义样式预设（保存后生成）
~/.npm/_npx/*/node_modules/gdocs-mcp/   ← npx 自动缓存的程序本体
```

全部本地存储，无第三方中转。Token 路径 `~/.gdocs-mcp/token.json` 为源码硬编码，不可更改。

## OAuth Scopes

| Scope | 用途 |
|-------|------|
| `https://www.googleapis.com/auth/documents` | 文档读写、样式、格式 |
| `https://www.googleapis.com/auth/drive` | 搜索、导出、复制、删除、评论 |
| `https://www.googleapis.com/auth/spreadsheets.readonly` | `get_charts` 工具 |

只读模式：设置 `GDOCS_MCP_READONLY=1` 环境变量可将 `drive` 降级为 `drive.readonly`。

## 前置条件

Google Cloud 项目 `gen-lang-client-0495225468` 必须启用以下 API：

- **Google Docs API**
- **Google Drive API**
- **Google Sheets API**

缺少任一 API 时，所有 Google API 调用返回 403。

## 工具清单（28 个）

### 文档读写

| 工具 | 说明 |
|------|------|
| `read_document` | 读取完整文档内容 |
| `read_document_structure` | 读取文档结构大纲（段落、表格、标题层级） |
| `create_document` | 创建新文档（支持 Markdown） |
| `update_document_markdown` | 用 Markdown 替换整个文档 |
| `update_document_section_markdown` | 用 Markdown 替换文档片段 |
| `update_document` | 批量更新（insertText, updateTextStyle 等原生 API） |
| `insert_text` | 在指定位置插入文本 |
| `replace_all_text` | 全文查找替换 |
| `delete_content_range` | 删除指定范围内容 |

### 导出/搜索/管理

| 工具 | 说明 |
|------|------|
| `search_documents` | 搜索文档（标题+内容） |
| `export_document` | 导出为 PDF / DOCX / TXT / HTML |
| `copy_document` | 复制文档 |
| `delete_document` | 删除文档（需确认标题） |

### 样式

| 工具 | 说明 |
|------|------|
| `list_style_presets` | 列出所有样式预设 |
| `apply_style_preset` | 应用样式预设到文档 |
| `extract_document_styles` | 从文档提取样式并保存为预设 |
| `set_active_preset` | 设置默认样式预设 |
| `delete_style_preset` | 删除自定义预设 |
| `update_document_style` | 更新页面尺寸、边距 |

### 内容元素

| 工具 | 说明 |
|------|------|
| `insert_image` | 插入图片（URL） |
| `insert_table` | 创建表格 |
| `write_table` | 一步创建+填充+样式表格 |
| `update_table_style` | 表格样式调整 |
| `insert_table_row` / `delete_table_row` | 表格行增删 |
| `insert_table_column` / `delete_table_column` | 表格列增删 |
| `unmerge_table_cells` | 取消合并单元格 |
| `insert_link` | 添加超链接 |
| `insert_page_break` | 插入分页符 |
| `create_footnote` | 创建脚注 |

### 页眉/页脚/列表/评论

| 工具 | 说明 |
|------|------|
| `update_header_footer` | 更新页眉/页脚（支持 `{{pageNumber}}`） |
| `delete_header_footer` | 删除页眉/页脚 |
| `format_list` | 项目符号/编号列表格式化 |
| `get_comments` | 获取文档评论 |
| `add_comment` | 添加评论（锚定文本） |

### 其他

| 工具 | 说明 |
|------|------|
| `replace_image` | 替换已有图片 |
| `get_charts` | 获取 Google Sheets 图表列表 |
| `execute_script` | 执行 Google Apps Script |

## 认证维护

### Token 过期

Access token 自动用 refresh token 刷新，无需手动操作。

### 重新认证

如果 refresh token 也过期了（7 天未使用），运行：

```bash
npx gdocs-mcp auth
```

会打开浏览器重新走 Google 登录流程，token 写回 `~/.gdocs-mcp/token.json`。

### 切换账号

```bash
rm ~/.gdocs-mcp/token.json
npx gdocs-mcp auth
```

## 故障排查

| 症状 | 可能原因 | 修复 |
|------|----------|------|
| 所有 API 返回 403 | Google Cloud 项目缺 API | 启用 Docs/Drive/Sheets API |
| `search_documents` 403 但其他正常 | Drive API 未启用 | 启用 Google Drive API |
| 401 `Auth expired` | Token 过期且刷新失败 | `npx gdocs-mcp auth` |
| 429 | API 配额超限 | 等 60 秒重试 |
| MCP 工具列表里没有 gdocs | MCP 启动失败 | 检查 `npx gdocs-mcp` 是否能独立运行 |
