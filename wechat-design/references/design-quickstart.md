# 706 微信排版设计系统 — 快速上手指南

## 从零到一的 3 步

### Step 1：准备好文章 MD

文章放在 `03-媒体区/` 下，标准 Obsidian Markdown 格式：
- `## 标题` → 文章主标题
- `### N · 章节名` → 章节
- `**加粗**` `*斜体*` `[链接](url)` → inline
- `> 引用` → 引用块
- `- 列表` → 列表
- `![[图片名|caption]]` → 图片

### Step 2：选色板 + 选排版 → 一行命令

```bash
cd 03-媒体区/

# 最快路径：用预设（自动选色板+排版）
python3 md_to_wechat_design.py --preset deep-article

# 或者手动组合
python3 md_to_wechat_design.py --palette warm-paper --modes chapter=roman,card=rounded
```

### Step 3：浏览器打开预览 → 复制到微信

```bash
open 微信推文-v3_preview.html
# 页面里点「复制全文到微信」→ 微信公众号后台 Ctrl+V
```

---

## 你可以做的选择

共两个维度，彼此独立，自由组合：

### 第一维：9 套色板（`--palette`）

| ID | 一眼印象 | 适合 |
|----|---------|------|
| `green` | 白底微绿 + 深绿点缀 | 通用、默认 |
| `warm-paper` | 暖奶油纸 + 鼠尾草绿 | 深度长文、人物访谈 |
| `navy-gold` | 奶油底 + 深蓝字 + 古董金 | 年度报告、机构内容 |
| `burgundy` | 浅黄油底 + 勃艮第红字 | 文化评论、论坛回顾 |
| `parchment-indigo` | 羊皮纸底 + 靛蓝字 + 太阳黄 | 艺术展览、创意活动 |
| `terracotta` | 黄油底 + 陶土锈红（单色系统）| 小型聚会、亲密场合 |
| `ink-orange` | 奶油底 + 纯黑字 + 火焰橙 | 宣言、活动召集 |
| `neo-brutal` | 暖白底 + 纯黑字 + 霓虹柠檬 | 科技评论、批判内容 |
| `navy-gallery` | 全深蓝底 + 暖黄字 + 灰绿 | 哲学思辨、深夜阅读 |

### 第二维：9 个排版开关（`--modes key=value,...`）

#### 1. 章节编号 `chapter=`
| 值 | 效果 |
|----|------|
| `numbered` | `01. ENGLISH  [ 中文 ]` — 默认 |
| `roman` | `i. english  [ 中文 ]` — 文学感 |
| `jumbo` | 72px 大数字 + 全宽发丝线 — 艺术感 |
| `simple` | 只有中文标题，无编号 — 极简 |

#### 2. 头部样式 `header=`
| 值 | 效果 |
|----|------|
| `standard` | 栏目标签 + 38px 衬线标题 + 副标题 + 装饰线 |
| `dark-block` | 独立深色块 + 亮色标签 + 金色线 + 亮色标题（需色板有深色面） |
| `minimal` | 纯标题，无标签无装饰线 |

> `dark-block` 需要色板提供 `bg_dark` / `text_on_dark`。支持：`navy-gold`、`ink-orange`、`navy-gallery`、`neo-brutal`（降级）

#### 3. 卡片形状 `card=`
| 值 | 效果 |
|----|------|
| `sharp` | 直角 — 默认 |
| `rounded` | 14px 圆角 — Soft Editorial 风格 |
| `pill` | 999px 药丸 — 适合标签/按钮 |

#### 4. 引用块 `quote=`
| 值 | 效果 |
|----|------|
| `left-border` | 左边框 3px accent 色 — 默认 |
| `outlined` | 全边框描边 1.5px — Long Table 风格 |
| `filled` | 实色 accent_bg 底 — 更醒目 |

#### 5. 列表标记 `bullet=`
| 值 | 效果 |
|----|------|
| `dot` | 默认圆点 · |
| `dash` | 全角破折号 — |
| `numbered-mono` | 等宽字体数字计数 |

#### 6. 分隔线 `divider=`
| 值 | 效果 |
|----|------|
| `accent-short` | 30px × 1px — 默认 |
| `gold-rule` | 36px × 1px — Signal 风格 |
| `hairline-full` | 全宽 1px — Biennale Yellow 风格 |
| `dashed` | 虚线 — Long Table 风格 |

#### 7. 强调方式 `emphasis=`
| 值 | 效果（`**加粗**` 怎么渲染）|
|----|------|
| `bold-dark` | 深色加粗 — 默认 |
| `color-switch` | 换 accent 色（CJK 无 italic 补偿）|
| `mark-highlight` | 荧光笔背景色块 — Neo-Grid Bold 风格 |

#### 8. 段落密度 `density=`
| 值 | 段落间距 |
|----|---------|
| `sparse` | 24px — 宽松呼吸感 |
| `normal` | 16px — 默认 |
| `dense` | 8px — 信息密度优先 |

#### 9. 对齐方式 `alignment=`
| 值 | 效果 |
|----|------|
| `justify` | 两端对齐 — 默认 |
| `left` | 左对齐 |
| `center` | 居中 — 哲学/实验性内容 |

---

## 选择指南

### 我不想选太多 → 用预设

```bash
python3 md_to_wechat_design.py --preset <type>
```

| preset | 自动组合 |
|--------|---------|
| `deep-article` | warm-paper + roman + rounded |
| `annual-report` | navy-gold + dark-block + dash + gold-rule |
| `culture-review` | burgundy + rounded + filled + color-switch |
| `art-exhibition` | parchment-indigo + jumbo + hairline-full |
| `intimate-gathering` | terracotta + minimal + outlined + pill + dashed |
| `manifesto` | ink-orange + dark-block + simple + filled + dash |
| `tech-critique` | neo-brutal + sharp + hairline-full + mark-highlight |
| `philosophy` | navy-gallery + center + numbered-mono + color-switch |
| `general` | green + 全默认（= 当前 706 经典绿）|

### 我想自己调 → 先选色板，再加排版开关

```bash
# 思路：色板决定「气质底色」，排版开关决定「结构表情」

# 例：暖色底但想要结构感
python3 md_to_wechat_design.py --palette warm-paper --modes chapter=jumbo,header=standard

# 例：深色底极简留白
python3 md_to_wechat_design.py --palette navy-gallery --modes chapter=simple,header=minimal,alignment=center

# 例：亮色底粗野直接
python3 md_to_wechat_design.py --palette neo-brutal --modes chapter=numbered,emphasis=mark-highlight,card=sharp
```

### 只有排版开关不指定色板 → 色板用默认 green

```bash
python3 md_to_wechat_design.py --modes chapter=jumbo,card=rounded
# 等价于 --palette green --modes chapter=jumbo,card=rounded
```

---

## 文件位置

| 文件 | 说明 |
|------|------|
| `design-presets.json` | 色板 + 排版模式 + 预设（唯一配置源） |
| `design-quickstart.md` | 本文档 |
| `design-upgrade-analysis.md` | 34 套模板分析原文 |
| `template-spec.md` | 706 经典绿排版规格（参考实现） |
| `md_to_wechat_design.py` | 生成器脚本 |
