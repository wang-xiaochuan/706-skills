---
name: wechat-design
description: >
  706 微信公众号排版设计系统。二维架构：9 套色板 × 排版开关，独立选择、自由组合。
  当用户提到「微信排版」「公众号设计」「配色方案」「排版风格」「设计系统」「文章用什么配色」「换一个排版」「帮我选配色」时触发。
  也当 wechat-publish skill 生成文章前需要确定视觉风格时触发。
version: 2.0
---

# 706 微信排版设计系统

> **核心思想**：颜色组合（色板）和排版模式是两个正交维度，独立选择、自由组合。
> **v2.0 原则**：只保留能真正看出差异的维度。加粗、对齐、列表标记等细微差异已移除——它们在实际渲染中几乎不可见。

## 使用方式

用户说「帮我选配色和排版」→ 你根据文章内容推荐色板+排版组合，用户确认后传给 wechat-publish 生成。

---

## 第一维：色板（9 套）

| ID | 一眼印象 | 底色 | 强调色 | 墨色 |
|----|---------|------|--------|------|
| `green` | 白底微绿 + 深绿 | `rgb(242,247,244)` | `rgb(26,123,90)` | 近黑 |
| `warm-paper` | 暖奶油 + 鼠尾草绿 | `#F2EEDF` | `#B7C7A8` | 暖棕黑 |
| `navy-gold` | 奶油底 + 深蓝字 + 古董金 | `#F0ECE3` | `#C8A870` | 深蓝 |
| `burgundy` | 浅黄油 + 勃艮第红 | `#FCF5E8` | `#F2B6C6` 粉 | 勃艮第 |
| `parchment-indigo` | 羊皮纸 + 靛蓝 + 太阳黄 | `#E9E5DB` | `#F1EE2E` 黄 | 靛蓝 |
| `terracotta` | 黄油 + 陶土锈红 | `#FAF1E2` | `#B53D2A` | 深棕 |
| `ink-orange` | 奶油 + 纯黑 + 火焰橙 | `#F0ECE5` | `#E85D26` | 纯黑 |
| `neo-brutal` | 暖白 + 纯黑 + 霓虹柠檬 | `#F5F4EF` | `#E6FF3D` | 纯黑 |
| `navy-gallery` | 全深蓝底 + 暖黄字 | `#2A3870` | `#3A7878` 灰绿 | 暖黄 |

---

## 第二维：排版开关（12 个维度）

仅保留在实际渲染中**肉眼可辨**的维度。

### ① chapter — 章节编号

| 值 | 效果 |
|----|------|
| `numbered` | `01. ENGLISH  [ 中文 ]` |
| `roman` | `i. english  [ 中文 ]` |
| `jumbo` | 72px 大数字 + 全宽发丝线 |
| `simple` | 仅中文标题，无编号 |

### ② header — 头部样式

文章顶部区域的视觉处理。

| 值 | 效果 |
|----|------|
| `standard` | 栏目标签 + 38px 衬线标题 + 英文副标题 + 30px 装饰线 |
| `dark-block` | 独立深底块 + 亮色标签 + 金线（需色板支持深底色） |
| `minimal` | 纯标题，无标签无装饰线 |

### ③ subtitle — 副标题板式

标题下方那行说明文字的样式（如 "706 上海 · 未来社区月 v1.2"）。这是 v2.0 新增维度。

| 值 | 效果 |
|----|------|
| `left-border` | 左边框 + 浅色背景（默认） |
| `capsule` | 圆角填充背景块，类似文本胶囊 |
| `inline` | 纯文字，无边框无背景，字号略小 |

### ④ quote — 引用块

正文中引用的他人发言、文献摘录的样式。

| 值 | 效果 |
|----|------|
| `left-border` | 左边框 3px 强调色 |
| `filled` | 实色背景填充 + 圆角 |
| `outlined` | 全边框 1.5px 描边 |

### ⑤ pullquote — 追问胶囊（v2.0 新增）

文章中独立成块的修辞追问句的样式。触发条件：整段为 bold + 含 `？`。

| 值 | 效果 |
|----|------|
| `capsule` | 圆角背景填充块，accent 色加粗居中，独立漂浮于段落之间 |
| `left-accent` | 左边框强调，不加背景 |
| `centered` | 纯居中放大文字，无背景无边框 |

### ⑥ dropcap — 首字下沉（v2.0 新增）

文章第一个段落的第一个字的处理。

| 值 | 效果 |
|----|------|
| `none` | 无首字下沉 |
| `accent` | 52px accent 色衬线大写，下沉 2 行 |
| `dark` | 52px 墨色衬线大写，下沉 2 行 |

### ⑦ lead — 首段样式（v2.0 新增）

全文第一个段落的视觉引导。

| 值 | 效果 |
|----|------|
| `normal` | 与正文相同（15px） |
| `larger` | 17px，略大 |
| `bold` | 首段全加粗 |

### ⑧ caption — 图注（v2.0 新增）

图片下方说明文字的样式。

| 值 | 效果 |
|----|------|
| `right-small` | 右对齐，10px，灰色 |
| `center-light` | 居中，10px，斜体，更淡 |
| `right-accent` | 右对齐，10px，accent 色 + 右边框线 |

### ⑨ img-frame — 图片框（v2.0 新增）

图片边缘处理。

| 值 | 效果 |
|----|------|
| `none` | 无框，直角 |
| `rounded` | 8px 圆角 |
| `hairline` | 1px 全边框描边 |

### ⑩ divider — 分隔线

章节或段落之间的视觉分割。

| 值 | 效果 |
|----|------|
| `accent-short` | 30px 强调色短線 |
| `hairline-full` | 全宽 1px 发丝线 |
| `dashed` | 虚线 |

### ⑪ bullet — 列表标记

| 值 | 效果 |
|----|------|
| `dot` | 默认圆点 `·` |
| `dash` | 全角破折号 `——`（德波顿式列表） |
| `accent-dot` | accent 色圆点，比默认更醒目 |
| `numbered` | 等宽数字 `1. 2. 3.` |

### ⑫ density — 段落间距

| 值 | 效果 |
|----|------|
| `sparse` | 22px — 呼吸感 |
| `normal` | 16px — 标准 |
| `dense` | 8px — 紧凑 |

### ⑬ card — 卡片圆角

当文章中出现卡片式内容块（如论坛截面、画像介绍）时的边角处理。

| 值 | 效果 |
|----|------|
| `sharp` | 直角 |
| `rounded` | 14px 圆角 |

---

## 从 v1 移除的维度

| 旧维度 | 移除原因 |
|--------|----------|
| `emphasis`（bold-dark / color-switch / mark-highlight） | 加粗颜色变化在实际渲染中几乎不可见；统一为 bold-dark |
| `alignment`（justify / left / center） | 微信 375px 窄屏上两端对齐和左对齐看不出差异 |

---

## 预设菜单（8 套完整组合）

可直接选用，也可在此基础上调整单个维度。

---

### 01 · 研究手稿 `research`

像一篇打印出来摊在桌上的研究草稿。克制、白底、结构清晰。

```
色板    green
━━━━━━━━━━━━━━━━━
chapter  numbered    01. ENGLISH [ 中文 ]
header   standard    栏目标签 + 衬线标题
subtitle left-border 左边框块
quote    left-border 左边框绿线
pullquote capsule    圆角胶囊
dropcap  accent      首字 accent 色下沉
lead     normal      正文同大
caption  right-small 右小字灰
img-frame none       无框直角
bullet   dot         默认圆点
divider  accent-short 30px 短线
density  normal      16px
card     sharp       直角
```

---

### 02 · 文学期刊 `literary`

拿着咖啡翻开一本纸页微黄的杂志。松、暖、有呼吸感。

```
色板    warm-paper   暖奶油 + 鼠尾草绿
━━━━━━━━━━━━━━━━━
chapter  simple      纯中文，无编号
header   standard    衬线标题
subtitle inline       纯文字无框
quote    filled       实色填充
pullquote centered    居中放大
dropcap  accent       首字 accent 下沉
lead     larger       首段 17px
caption  center-light 居中斜体淡
img-frame rounded     8px 圆角
bullet   dash         —— 破折号
divider  hairline-full 全宽发丝线
density  sparse       22px
card     rounded      14px 圆角
```

---

### 03 · 论坛场刊 `forum`

大数字章节入口，描边引用，追问胶囊。适合活动回顾、论坛记录。

```
色板    burgundy     勃艮第红
━━━━━━━━━━━━━━━━━
chapter  jumbo       72px 大数字
header   standard    衬线标题
subtitle capsule     圆角胶囊
quote    outlined    全边框描边
pullquote capsule    圆角胶囊
dropcap  none        无
lead     bold        首段加粗
caption  right-accent 右 accent + 边线
img-frame none        无框
bullet   accent-dot  accent 色圆点
divider  accent-short 30px 短线
density  normal      16px
card     sharp       直角
```

---

### 04 · 宣言招贴 `manifesto`

落地页质感，号召力强。深色头部砸下来，大数字，填充引用。

```
色板    ink-orange   墨底 + 火焰橙
━━━━━━━━━━━━━━━━━
chapter  jumbo       72px 大数字
header   dark-block  深色头部块
subtitle capsule     圆角胶囊
quote    filled      实色填充
pullquote capsule    圆角胶囊
dropcap  dark        首字墨色下沉
lead     bold        首段加粗
caption  right-accent 右 accent + 边线
img-frame hairline   1px 细框
bullet   accent-dot  accent 圆点
divider  hairline-full 全宽
density  normal      16px
card     sharp       直角
```

---

### 05 · 新粗野 `brutal`

荧光笔、纯黑字、全宽发丝线。适合数据文章、科技评论。

```
色板    neo-brutal   暖白 + 纯黑 + 柠檬黄
━━━━━━━━━━━━━━━━━
chapter  numbered    01. ENGLISH [中文]
header   standard    衬线标题
subtitle left-border 左边框
quote    outlined    全边框描边
pullquote capsule    圆角胶囊
dropcap  none        无
lead     bold        首段加粗
caption  right-accent 右 accent + 边线
img-frame hairline   1px 细框
bullet   numbered    等宽数字 1. 2. 3.
divider  hairline-full 全宽
density  normal      16px
card     sharp       直角
```

---

### 06 · 画廊白立方 `gallery`

深蓝底白字，居中排版。适合深夜阅读、哲学思辨、艺术展。

```
色板    navy-gallery 全深蓝底 + 暖黄字
━━━━━━━━━━━━━━━━━
chapter  roman       i. english [ 中文 ]
header   dark-block  深色头部
subtitle inline       纯文字
quote    filled       实色填充
pullquote centered    居中放大
dropcap  accent       首字 accent 下沉
lead     larger       首段 17px
caption  center-light 居中斜体淡
img-frame rounded     8px 圆角
bullet   dot          默认圆点
divider  accent-short 30px
density  sparse       22px
card     rounded      14px 圆角
```

---

### 07 · 陶土笔记 `terracotta`

黄油底 + 单色锈红。朴实，不炫技。个人叙事、旅行随笔。

```
色板    terracotta   黄油底 + 陶土锈红
━━━━━━━━━━━━━━━━━
chapter  simple      纯中文
header   minimal     无标签无装饰
subtitle inline       纯文字
quote    left-border  左边框
pullquote centered    居中放大
dropcap  accent       首字下沉
lead     larger       首段 17px
caption  center-light 居中斜体淡
img-frame rounded     8px 圆角
bullet   dash         —— 破折号
divider  dashed       虚线
density  sparse       22px
card     rounded      14px 圆角
```

---

### 08 · 蓝金报告 `navy-gold`

深蓝底头 + 古董金线。年度报告、白皮书、正式提案。

```
色板    navy-gold    奶油底 + 深蓝字 + 金
━━━━━━━━━━━━━━━━━
chapter  jumbo       72px 大数字
header   dark-block  深色头部 + 金线
subtitle capsule      圆角胶囊
quote    outlined     全边框描边
pullquote left-accent 左边框强调
dropcap  dark         首字墨色下沉
lead     bold         首段加粗
caption  right-small  右小字
img-frame hairline    1px 细框
bullet   numbered     等宽数字 1. 2. 3.
divider  hairline-full 全宽发丝线
density  normal       16px
card     sharp        直角
```

---

### 09 · 独立志 `zine`

打印出来的独立杂志。黑框、硬阴影、monospace 标签、多色块分区。像一本 punk flyer 或 underground zine。

```
色板    zine          暖白底 + 纯黑 + 金
━━━━━━━━━━━━━━━━━
chapter  numbered    01. ENGLISH [中文]
header   zine        黑框 + 硬阴影 + 旋转标签
subtitle capsule      黑框胶囊
quote    outlined     黑框描边
pullquote capsule     黑框胶囊 + 阴影
dropcap  dark         首字纯黑下沉
lead     bold         首段加粗
caption  right-small  右小字
img-frame hairline    黑框细描边
bullet   dash         —— 破折号
divider  hairline-full 全宽黑线
density  normal       16px
card     sharp        直角
```

---

## 快速匹配

| 你的文章是…… | 试试 |
|-------------|------|
| 研究计划、调查方法、文献综述 | `research` |
| 论坛回顾、文化评论、活动复盘 | `forum` |
| 个人随笔、旅行记录、散文 | `literary` 或 `terracotta` |
| 活动召集、宣言、品牌态度 | `manifesto` 或 `zine` |
| 数据文章、科技评论、分析 | `brutal` |
| 年度报告、白皮书、正式提案 | `navy-gold` |
| 哲学思辨、艺术评论、深夜长文 | `gallery` |
| 独立杂志感、地下刊物、punk 视觉 | `zine` |
| 不确定 / 想从干净的开始 | `research` |

---

## 给用户的回复模版

```
这篇文章适合：
📋 预设：research · 研究手稿
🎨 色板：green 经典绿 — 白底微绿，克制清晰
📐 排版：numbered 章节 + left-border 引用 + capsule 追问 + accent 首字下沉

要我按这个组合生成预览吗？或者你换一个预设看？
```

---

## 配置文件位置

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 本文件（v2.0） |
| `references/design-presets.json` | 配置源 |
| `references/design-quickstart.md` | 快速上手 |
