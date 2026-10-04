---
name: wechat-publish-2.0
description: >
  WeChat 文章设计+发布系统 v2.0。视觉控制面板 + 实时预览 + LLM 辅助调整 + 内容编辑。
  当用户说「微信排版」「设计控制面板」「启动设计服务器」「wechat-publish 2.0」「帮我调排版」时触发。
  是 wechat-publish (v1) 和 wechat-design 的整合升级版。
version: 2.0
---

# WeChat Publish 2.0 — 设计+发布一体化

> v1 是「MD → HTML」。v2 是「MD → 设计面板 → 实时预览 → 发布」。

## 核心架构

```
MD 源文件
  │
  ▼
build_article(config, md_path, media_path)  ← Python 可调用函数
  │  9 套色板 × 8 个排版维度 × LLM 建议
  ▼
design_server.py :8080                      ← 本地 HTTP 服务
  │  /api/presets  /api/build  /api/llm  /api/write
  ▼
control_panel.html                          ← 浏览器控制面板
  │  预设选择 · 色板调整 · 排版切换 · 实时预览 · 内容编辑
  ▼
_pending_changes.json                       ← 写入后 Agent 读取执行
```

## 快速开始

```bash
cd {项目目录}/outputs/articles/
python3 design_server.py
# → http://localhost:8080
```

## 控制面板功能

### 🎨 预设
9 套完整预设（研究手稿/文学期刊/论坛场刊/宣言招贴/新粗野/画廊白立方/陶土笔记/蓝金报告/独立志），一键切换颜色+排版。

### 🖌 色板
- 8 个颜色输入（底色/强调色/正文色/标题色/辅助色/图注色/分隔线色/强调底）
- **预设调色盘**：单独应用任意预设的色板，不改排版
- **🎲 随机**：随机生成配色

### 📐 排版（7 个可见维度）
| 维度 | 选项 |
|------|------|
| 头部+章节 | 标准·数字 / 极简·无编号 / 独立志·灰条 / 深色·大数字 |
| 引用块 | 左边框 / 实色填充 / 全边框描边 |
| 追问胶囊 | 胶囊块 / 左边框 / 居中大字 |
| 首字下沉 | 无 / accent色 / 墨色 |
| 首段样式 | 正常 / 稍大 / 加粗 |
| 图注样式 | 右小字 / 居中斜体 / 右accent线 |
| 图片边框 | 无框 / 圆角 / 细框 |

### 💬 AI 调整
输入自然语言（如"用暖色调，圆角引用块，疏朗一点"），LLM 自动解析为参数变更，控件更新后点刷新即可。

### 📝 内容编辑
- **✏️ 标记转换**：点击预览中文字 → 转换为追问胶囊/二级标题/正文/数据剪报（自动加 `<!-- clip -->` 标记）
- **📷 点击定位插图片**：点击预览中段落 → 描述所需图片 → Agent 搜索 media 文件夹自动匹配插入
- **💾 写入文件**：所有变更保存为 `_pending_changes.json`，同时复制到剪贴板

## Agent 工作流

### 用户说「应用 pending changes」

1. 读取 `_pending_changes.json`
2. 对于 `convert` 类型：在 MD 源文件中找到匹配段落，包裹 `<!-- clip -->` / `<!-- /clip -->` 标记
3. 对于 `image` 类型：在 MD 中找到上下文段落，搜索 `706-media/` 找到相关图片，替换 `_placeholder_` 为真实路径
4. 重建 HTML：`python3 build_research_article.py <scheme>`
5. 重启服务器（自动热加载 control_panel.html）

### 用户说「插入图片」

1. 用户在控制面板点击定位 + 描述图片
2. 写入 `_pending_changes.json`
3. Agent 读取 → 搜索 media 文件夹 → 替换占位符 → 重建

## 设计系统参考

详见 `wechat-design` skill（`~/.claude/skills/wechat-design/SKILL.md`）：
- 9 套色板完整颜色值
- 13 个排版维度（v2.0）
- 8 套预设组合
- 快速匹配表

## 技术细节

### build_article(config, md_path, media_vault_path)
来自 `build_research_article.py`。接收完整 config dict，返回 article body HTML（`<table>` 块）。所有图片内嵌 base64。

### 微信粘贴
控制面板的 iframe 预览是自包含 HTML。点「复制全文」或直接打开 `_preview_latest.html` → Ctrl+A → Ctrl+C → 微信公众号后台 Ctrl+V。

### 剪报块 (`<!-- clip -->`)
在 MD 中包裹 `<!-- clip -->` / `<!-- /clip -->` 标记，渲染为带背景的数据剪报块。适用于文献综述、数据段落。

### 图片占位符 (`_placeholder_`)
Agent 根据上下文描述在 `706-media/` 中搜索匹配图片后替换。

## 依赖

- Python 3 stdlib（http.server, json, re, pathlib）
- Pillow（图片处理）
- requests（LLM API，可选）
- `ANTHROPIC_API_KEY`（LLM 功能，可选）

## 文件位置

| 文件 | 说明 |
|------|------|
| `design_server.py` | HTTP 服务器（4 个 API 端点） |
| `control_panel.html` | 自包含控制面板 UI |
| `build_research_article.py` | 核心构建函数 `build_article()` + 9 套 PRESETS |
| `warmup-article-2-research-plan-draft.md` | MD 源文件 |
| `_pending_changes.json` | Agent 读取的变更清单 |
| `_preview_latest.html` | 最新构建的预览文件 |
