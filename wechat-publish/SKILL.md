---
name: wechat-publish
description: "将 Notion 或 Markdown 文章排成可粘贴到微信公众号编辑器的富文本 HTML，并处理图片与本地预览。目标明确为公众号排版、Notion/MD 转微信时使用。竖版图片卡片由 wechat-slides 处理；一般文案、普通 Notion/MD 编辑和未明确平台的“发出去”不自动触发。"
---

# WeChat Publish — Markdown 到微信公众号发布工作流

把内容（Notion 页面或 Markdown 文件）转换成微信公众号编辑器可直接粘贴的 HTML。
输出浏览器预览页面（`xxx_preview.html`），打开后点「复制全文到微信」→ 微信公众号后台 Ctrl+V 粘贴。

**排版规格详见 `references/template-spec.md`**——记录了 706 编辑风格的 inline style 规范（颜色、标题、段落、图片、引用块）。
如果为自己的品牌使用，替换其中的颜色方案和字体即可。

---

## 环境配置（使用前必读）

### 1. 设置工作路径

skill 脚本需要知道两个根路径。在首次使用时告诉 LLM，或写入环境变量：

```bash
# 知识库根目录（Markdown 文件、Obsidian vault）
export VAULT_ROOT="$HOME/path/to/your/knowledge-vault"

# 媒体素材库根目录（可选，如果有 706-media 风格的素材库）
export MEDIA_VAULT="$HOME/path/to/your/media-vault"
```

如果 `MEDIA_VAULT` 未设置，skill 会自动跳过媒体库检索，仅使用传统路径搜索。

**706 项目当前使用的路径**（供团队成员参考）：
```
VAULT_ROOT  = $706_CLOUD/706-knowledge/706知识库
MEDIA_VAULT = ~/Dev/706-local-os/706-media
```

### 2. 需要的 LLM 能力

这个 skill 不绑定特定的 LLM。需要的**最低能力集**：

| 能力 | 用途 | 哪些 LLM 有 |
|------|------|------------|
| 读文件 | 读取 MD 文件和图片 | Claude, GPT-4, Gemini |
| 运行 Python 脚本 | 图片处理、base64 编码、生成 HTML | Claude Code, Cursor, Codex, OpenCode |
| 写文件 | 输出 `_preview.html` | 同上 |
| 多模态看图（推荐） | 自动标注图片 caption | Claude, GPT-4V, Gemini |
| Web fetch（可选） | 从 Notion 获取内容 | Claude, Cursor + MCP |

**LLM 适配说明**：

- **Claude Code / Claude Desktop**：所有能力原生支持，直接按本 skill 执行
- **Cursor / Codex / OpenCode**：有文件读写和 Python 执行能力，可直接用。没有多模态的话，caption 走文本启发式规则
- **ChatGPT / Gemini 网页版**：可以对话方式完成大部分操作，但需要手动运行 Python 脚本和粘贴 HTML
- **纯 API 调用**：按本 skill 的工作流描述写代码调用即可

### 3. Python 依赖

```bash
pip install Pillow   # 图片处理（resize、格式转换、base64）
```

---

## 输入来源

### 来源 A：Notion 页面

用户提供 Notion 页面链接或 ID，用 Notion API / MCP 获取内容。

### 来源 B：Markdown 文件

用户提供本地 `.md` 文件路径。**参考实现**：`706-knowledge/by-project/2050/03-媒体区/md_to_wechat.py`

**先通读 MD 全文 → 识别结构 → 再写解析器。不要假设结构。**

---

## MD 结构灵活性（重要）

每篇文章的结构可能完全不同。必须识别：

| 元素 | 可能的形式 |
|------|-----------|
| 章节分隔 | `### N · 标题` / 裸数字 `0`, `1`, `2` / `## 标题` |
| 章节标题 | `###` 的内容 / 第一个斜体段落 / blockquote 首句 |
| 歌词引用 | `> *斜体诗句*` + `> 作者，来源，年代` |
| 图片 | `![[path]]` / `![ ](path)` / `![[vault-relative/path]]` |
| 脚注 | `[^1]` 正文引用 + `[^1]: 定义` 文末 |

**原则**：先通读全文 → 画出结构树 → 再写解析器。

---

## 工作流

### Step 1: 确认输入和配置

- 来源：Notion 链接 还是 本地 MD 文件
- **颜色方案**：默认 706 标准配色（见 `references/template-spec.md`），可按需替换为自定义品牌色
- **图片处理**：MD 来源 → base64 内嵌；Notion 来源 → 已有公网 URL 或上传图床

### Step 2: 获取内容 & 分析结构

**Notion 来源**：用 Notion API / MCP fetch 页面，解析 Markdown。

**MD 来源**：直接读取 `.md` 文件。

标准 MD 语法映射：
- `# h1`：跳过（工作区标题）
- `## h2`：文章主标题 → 头部区块（栏目标签 + 38px 标题 + 英文副标题 + 装饰线）
- `### N · 中文标题`：章节 → `01. ENGLISH [ 中文 ]` 标题行 + 20px 中文大标题
- `#### 子标题`：小节标题
- `**加粗**`、`*斜体*`、`[链接](url)`：inline 格式
- `> 引用块`：带左边框的引用样式
- `- 列表项`：`<ul><li>`
- `| 表格 |`：inline styled `<table>`
- `---`：跳过
- `![[path|caption]]`：场景图（有 caption = 场景图，无 caption = 头像圆形裁切）

### Step 3: 构建文章 HTML

**必须先阅读 `references/template-spec.md`**，按规格逐元素生成 inline-styled HTML。

关键结构（详见 template-spec.md）：
- 外层用 `<table>` 包裹，padding: 70px 30px 100px
- 头部：栏目标签 → 38px 衬线主标题 → 英文副标题 → 30px×1px 装饰线
- 章节：`<section style="margin-bottom:60px">` 包裹，首章节加 `margin-top:80px`
- 正文：`<section>` 元素，15px，line-height:2，非首段 `margin-top:16px`
- **每个元素必须带 `background-color`**

### Step 4: 处理图片

#### 4a. 媒体库优先检索（如果有 MEDIA_VAULT）

生成 HTML 之前，先查 `MEDIA_VAULT/media-index.json` 是否有可用素材：

```python
import json, os

media_root = os.environ.get("MEDIA_VAULT")
if media_root and os.path.exists(os.path.join(media_root, "media-index.json")):
    with open(os.path.join(media_root, "media-index.json")) as f:
        index = json.load(f)
    # 按场景检索：
    # 空间场景 → category: "上海空间" (品牌自定义)
    # 活动现场 → project + event 匹配
    # 嘉宾头像 → category: "嘉宾"
    # 文末底图 → category: "品牌素材"
    # 二维码   → category: "品牌素材"
```

媒体库命中 → 直接加载文件做 base64。未命中 → 走传统搜索。

#### 4b. 图片路径多源搜索

```python
SEARCH_DIRS = [
    MD_DIR / "images",          # 文章同级 images/ 子目录
    MEDIA_VAULT,                 # 媒体素材库（如果设置了环境变量）
    VAULT_ROOT / "media",       # vault 根 media/ 目录
    VAULT_ROOT,                 # vault 根
]
```

文件名修正：空格 → 下划线；提取纯文件名。

#### 4c. 图片尺寸与质量

```python
MAX_WIDTH = 800     # 微信 feed 流约 600px，编辑器约 800px
JPEG_QUALITY = 75   # 清晰度和体积最佳平衡
```

- 原图 > 800px 宽 → resize
- PNG → 转 JPEG
- 总 HTML < 10MB（微信粘贴上限）
- Base64 缓存到 `_cache/` 目录

#### 4d. 图片 Caption 检测

图片下方文本判断是 caption 还是独立段落：

1. **Lookahead**：跳过空白行找到下一个有内容的行
2. **排除规则**（以下情况不作为 caption）：
   - 以 `>` 开头（blockquote）
   - 以 `*...*` 包裹（italic 段落）
   - 是章节标记（单数字 `0`-`9`）
   - 以 `感谢`、`撰文`、`摄影` 等元信息开头
3. **拆分规则**：如果匹配行含 `。！？`，在第一句处拆分为 caption + 余段
4. **短文本**：无句号且 < 40 字符 → 整体作 caption

### Step 5: 生成预览 HTML

预览框架（本地预览用，不进入微信）：
- 深色背景（`#1a1a1a`）
- 375px 手机预览框，border-radius:12px
- sticky 顶部工具栏 + 「复制全文到微信」按钮
- `copyContent()` 用 Selection+Range 复制 `#article-content` 内容

```html
<div class="phone-frame">
  <div id="article-content">
    <!-- 文章 HTML（全 inline style，会被复制到微信） -->
  </div>
</div>
```

### Step 6: Pre-flight 校验（必做）

| 检查项 | 方法 | 通过条件 |
|--------|------|---------|
| 图片全量引用 | MD 中 `![` 出现次数 vs HTML 中 `<img` 次数 | 数量一致 |
| Section 标签平衡 | 计数 `<section ` vs `</section>` | 相等 |
| Caption 数量 | 预期 vs 实际 | 接近 |
| 总文件大小 | `stat` 输出 | < 10MB |
| HTML 结构 | `</td></tr></table>` 正确闭合 | 无嵌套错误 |

**发现问题 → 修改脚本 → 重新生成。不要手动改 HTML。**

### Step 7: 保存并告知用户

输出路径：`{来源文件同目录}/{文件名}_preview.html`

告知用户：
1. 浏览器打开预览文件
2. 点击「复制全文到微信」
3. 微信公众号后台 → 新建图文 → Ctrl+V 粘贴
4. 预览确认后发布

---

## 设计控制面板（视觉迭代工作流）

对于需要反复调整排版和配色的文章，706 项目提供了一套本地设计控制面板。

### 启动设计服务器

```bash
cd outputs/articles
python3 design_server.py --port 8000
```

浏览器打开 `http://localhost:8000/`，左侧面板可实时调整：
- **9 套预设配色**（研究手稿 / 文学期刊 / 论坛场刊 / 宣言招贴等）
- **7 个排版开关**（章节编号风格 / 引用块 / 追问胶囊 / 首字下沉 / 图注 / 图片边框 / 首段样式）
- **AI 自然语言调整**：输入"用暖色调，圆角引用块"等自然语言指令

右侧 375px 手机框实时预览微信效果。点击「🔄 刷新预览」即时更新。

### 内容编辑

控制面板支持三种编辑模式（通过 iframe 交互）：
- **✏️ 标记转换**：点击预览中的文字，将其转为追问胶囊 / 二级标题 / 普通正文 / 数据剪报块
- **📷 点击定位插图片**：点击预览位置 + 描述需求 → 写入 `_pending_changes.json`
- **✍️ 标记重写区域**：选择文段 + 描述重写方向 → 写入 `_pending_changes.json`

点击「💾 写入文件」后，在 CLI 告知 Agent "应用 pending changes" 即可执行。

### 一键预发布

点击「🚀 准备预发布」按钮，系统会：
1. 使用当前配色/排版配置生成最终 HTML
2. 保存到 `outputs/html/wechat-publish/`，文件名自动取自文章 H1 标题
3. 在新标签页打开独立页面，可直接复制全文粘贴到微信编辑器

预发布文件同时保存一份 `_publication_latest.html` 作为最新版。

### 关键文件

| 文件 | 用途 |
|------|------|
| `build_research_article.py` | 主构建引擎，含 PRESETS 配色方案和 HTML 生成逻辑 |
| `design_server.py` | HTTP 服务器，处理 /api/build、/api/publish、/api/presets、/api/write、/api/llm |
| `control_panel.html` | 前端控制面板 UI |
| `_preview_latest.html` | 最新预览缓存 |
| `_pending_changes.json` | 待处理的编辑变更 |

---

## 给其他 LLM 使用时的指引

如果你在使用非 Claude 的 LLM，按以下方式适配：

### GPT-4 / GPT-4o
- 有文件读写能力（通过 Code Interpreter），可以直接执行 Python 脚本
- 将 `template-spec.md` 和 MD 文件作为 context 输入
- 让 GPT 生成一个完整的 Python 脚本，然后执行它

### Gemini
- 有 2M token 上下文窗口，可以把整个 template-spec.md + MD 文件一起丢进去
- 让 Gemini 直接生成完整 HTML
- 图片需要你手动处理（用 Pillow 脚本）

### DeepSeek / 开源模型
- 不支持多模态看图，caption 走文本启发式规则
- 其余流程完全适用
- 推荐写一个 Python 脚本而不是让 LLM 逐元素生成 HTML

### 通用适配原则
1. **把这个 SKILL.md 的内容作为 system prompt 喂给 LLM**
2. **把 `references/template-spec.md` 作为第二个 context 附上**
3. **提供输入 MD 文件的完整内容**
4. **让 LLM 输出一个 Python 脚本，而非直接输出 HTML**（图片多时直接输出 HTML 容易超 context）
5. **执行 Python 脚本，检查输出**

---

## 复杂文章的多 Agent 工作流

文章含大量图片（>20 张）、非标准结构、脚注时，用多 Agent 并行：

```
Agent 1（脚本编写）
  ├── 读取 MD 全文，分析结构
  ├── 编写定制 Python 转换脚本
  └── 执行脚本，生成 HTML

Agent 2（图片验证）  ← 与 Agent 1 并行
  ├── 列出 MD 中所有图片引用
  ├── 逐个验证文件存在
  ├── 报告缺失图片及可能位置
  └── 返回完整映射表

Agent 3（质量检查）  ← Agent 1 完成后触发
  ├── 验证 base64 数据完整性
  ├── 检查 section/footnote/caption 数量
  └── 报告问题及修复建议
```

---

## 微信兼容性要点

1. **所有样式必须 inline**，`<style>` 标签粘贴时会被剥离
2. **每个元素必须有 `background-color`**，微信会剥离外层容器
3. **外层用 `<table>` 包裹**，不用 `<div>` flex
4. **不用 `rem`/`em`/`vw`**，只用 `px`
5. **font-family 空格字体名用单引号**（双引号会破坏 `style="..."` 属性）
6. 导出微信编辑器源代码时注意**嵌套表格**——微信会注入额外 `<table>` 包裹

---

## 文件位置

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 本文件（工作流定义） |
| `references/template-spec.md` | 706 排版规格（颜色、字号、结构），可替换为自有品牌 |
| `706-knowledge/by-project/2050/03-媒体区/md_to_wechat.py` | MD→HTML 参考实现 |

---

## 配套 Skill 生态

这个 skill 不是独立工作的——它在一个内容生产管线里。以下是上下游关系：

### 上游（内容创作 → 本 skill 的输入）

| Skill | 关系 | 说明 |
|-------|------|------|
| **`706-notion-writer`** | 上游 | 在 Notion 上写活动招募长文（1000-3000 字散文体）。写完后导出 MD → 本 skill 排版发布 |
| **`xhs-copywriter`** | 并行 | 写小红书短文案（150-300 字）。不同平台，不同风格——但同一场活动的素材和图片可以复用 |
| **`panel-curator`** | 上游 | 论坛/圆桌主持准备。产出的议程和嘉宾资料 → 可转为推文内容 |
| **`706-long-article-distilling`** | 上游 | 长文结构化蒸馏。蒸馏后的内容 → 本 skill 排版为公众号长文 |

### 素材供给（图片从哪里来）

| Skill | 关系 | 说明 |
|-------|------|------|
| **`wechat-image-archive`** | 素材 | 从微信群抓图归档到 706-media 媒体素材库。本 skill 的 Step 4a 优先从这里检索 |
| **`media-ingest`** | 素材 | 处理 inbox 中的标注图片入库到 706-media。手工补图的标准入口 |
| **`image-captioning`** | 素材（规划中） | 自动给媒体库图片打 caption，提升检索精度 |

### 下游 & 分发（排版后去哪里）

| Skill | 关系 | 说明 |
|-------|------|------|
| **`wechat-slides`** | 并行 | 竖版截图幻灯片，适合朋友圈/群聊转发。同一篇文章可以同时出推文 + 幻灯片两个版本 |
| **`xiaohongshu-poster`** | 下游 | 生成小红书海报图。推文内容可精简为海报文案 |

### 典型工作流

```
活动发生
  │
  ├─→ wechat-image-archive  微信群图 → 706-media 素材库
  ├─→ media-ingest          手动补图 → 706-media 素材库
  │
  ├─→ 706-notion-writer     写活动招募/回顾长文
  │       │
  │       └─→ wechat-publish   排版 → 公众号发布
  │               │
  │               ├─→ wechat-slides      出竖版幻灯片（群聊/朋友圈转发）
  │               └─→ xiaohongshu-poster 出海报图（小红书发布）
  │
  └─→ xhs-copywriter        出小红书短文案（独立分发）
```

### 给别人用时的最小配置

如果你把这个 skill 分享给其他团队，他们至少需要：
- **这个 SKILL.md**（工作流）
- **`references/template-spec.md`**（改色号为自己的品牌色）
- 一个 Markdown 输入文件或 Notion 页面
- Python 3 + Pillow

如果有媒体素材库（706-media 风格），额外需要：
- `media-ingest` skill（入库）
- `wechat-image-archive` skill（从微信群归档）
