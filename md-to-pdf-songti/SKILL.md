---
name: md-to-pdf-songti
description: >
  将 Markdown 文件通过 XeLaTeX 渲染为 PDF，使用宋体（Songti SC）作为正文字体。
  当用户提到「生成 PDF」「导出 PDF」「Markdown 转 PDF」「渲染 PDF」「用宋体输出 PDF」
  「LaTeX 渲染」「XeLaTeX 排版」「md to pdf」「白皮书 PDF」「报告 PDF」「打印 PDF」时触发。
  也当用户给了一个 .md 文件路径要求转成 PDF 时触发。
---

# MD to PDF · XeLaTeX + 宋体

将 Markdown 文件用 XeLaTeX 渲染为排版级 PDF，使用 macOS 系统自带 Songti SC（宋体-简）作为正文字体。

## 依赖检查

渲染前确认以下工具可用：

```bash
# XeLaTeX（BasicTeX 或 MacTeX）
which xelatex || find /Library/TeX -name xelatex 2>/dev/null

# pandoc
which pandoc

# Songti SC 字体
fc-list :lang=zh | grep -i song
```

- **XeLaTeX 路径**：BasicTeX 默认为 `/Library/TeX/texbin/xelatex`，不在默认 PATH 中，需显式指定。
- **字体**：Songti SC 在 macOS 系统自带（`/System/Library/Fonts/Supplemental/Songti.ttc`），无需额外安装。
- **包依赖**（BasicTeX 已含）：`fontspec`、`geometry`、`hyperref`、`longtable`、`booktabs`、`array`、`calc`、`xcolor`。

## 工作流

### Step 1：定制模板

从 `references/songti-template.tex` 读取模板，修改 `\title{}` 和 `\author{}` 为目标文档的标题和作者。模板中其他设置（页边距 2.5cm、行距 1.8、A4、11pt）保持不变，除非用户另有要求。

可选自定义项：
- `\setmainfont{Songti SC}` → 可改为 `STSong`（华文宋体）、`SimSun` 等
- `\renewcommand{\baselinestretch}{1.8}` → 行距
- `geometry{margin=2.5cm}` → 页边距

### Step 2：Pandoc 生成 .tex

```bash
pandoc "输入文件.md" -o "/tmp/输出文件名.tex" --standalone \
  --template=/path/to/songti-template.tex
```

### Step 3：XeLaTeX 两遍编译

```bash
XELATEX=/Library/TeX/texbin/xelatex  # 或 which xelatex
$XELATEX -output-directory=/tmp -interaction=nonstopmode "/tmp/输出文件名.tex"
$XELATEX -output-directory=/tmp -interaction=nonstopmode "/tmp/输出文件名.tex"
```

第二遍用于解决交叉引用（标签、目录等）。

### Step 4：输出

将 `/tmp/输出文件名.pdf` 复制到目标目录（默认与源 .md 同目录同名 .pdf）。

## 模板关键设置说明

| 设置 | 值 | 作用 |
|------|-----|------|
| `\XeTeXlinebreaklocale "zh"` | — | 启用中文断行（最重要，否则文本溢出右边距） |
| `\XeTeXlinebreakskip` | `0pt plus 1pt` | 字符间可拉伸，保证两端对齐 |
| `\emergencystretch` | `3em` | 断行困难时额外弹性空间 |
| `\tolerance` | `1000` | 换行容忍度 |
| `\newcounter{none}` | — | 兼容 pandoc 无标题 longtable 表格 |

## 已知问题

- **BasicTeX 是 Minimal 安装**：`xeCJK`、`ctex`、`enumitem`、`setspace` 等包不包含在内。本模板仅使用 BasicTeX 自带的包，因此不依赖 `xeCJK`——中文断行通过 XeTeX 原生命令 `\XeTeXlinebreaklocale "zh"` 实现。
- **`tlmgr` 需要 sudo**：如需安装额外 LaTeX 包，用户需自行 `sudo tlmgr install <package>`。
- **macOS Only**：模板字体 `Songti SC` 是 macOS 系统字体，其他平台需替换为对应宋体名称（如 Linux 的 `Noto Serif CJK SC`、Windows 的 `SimSun`）。
