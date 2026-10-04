---
name: wechat-slides
description: "把内容做成用于微信传播的竖版 HTML 图片卡片或截图幻灯片，默认 750×1334px。用户需要分张图片、长图卡片、截图推文、竖版幻灯片或明确调用 wechat-slides 时使用。公众号富文本 HTML 排版由 wechat-publish 处理；仅说“做个推文”不确定为图片卡片。"
---

# 微信竖版幻灯片 Skill

## 你在做什么

帮用户生成一个本地 .html 文件，内含若干张竖版幻灯片（每张 750x1334px）。用户在浏览器里打开，逐张截图，截出的图片直接插入微信公众号图文。这样做完全不受微信编辑器渲染限制，可以实现任意字体、配色、布局和视觉效果。

---

## Step 1：问清楚内容和风格

先从已有素材和会话中提取内容与风格。只询问会改变关键结果的缺失信息；没有指定风格或张数时，自主提出适合内容的方案并说明假设。

### 1a. 内容
- 这篇推文/活动是关于什么的？
- 大概需要几张幻灯片？有没有大纲或草稿？
- 有没有具体的活动信息（时间、地点、嘉宾等）？

### 1b. 设计风格
根据内容选择视觉风格；用户希望比较方向时，可提供这些参考：

| 风格关键词 | 特征 |
|-----------|------|
| 波普/大胆 | 高饱和色块、粗黑边框、强对比、pop-art 感 |
| 极简/清冷 | 大量留白、细线条、单色或双色、无衬线字体 |
| 优雅/文学 | 衬线字体、米白/深墨配色、诗意排版 |
| 暗黑/高级 | 深色背景、金色/荧光色点缀、夜间氛围 |
| 自定义 | 用户提供参考图或色号 |

如果用户已经在对话里给了参考图或色系描述，直接从中提取，不用再问。

---

## Step 2：规划幻灯片结构

根据内容自主规划每张幻灯片的主题，通常的结构：

Slide 01 — 封面（标题 + 核心信息 + 日期）
Slide 02 — 钩子/开场白（一个引人入胜的问题或陈述）
Slide 03 — 嘉宾/主角介绍
Slide 04 — 核心议程或内容预告
Slide 05 — 深度内容（概念、亮点、四格等）
Slide 06 — 金句/情绪高潮
Slide 07 — 活动信息/行动号召（时间、地点、报名）

张数根据内容量灵活增减（一般 5-9 张）。简要说明结构后生成；用户要求先选方案时，在选择点等待。

---

## Step 3：生成 HTML 文件

### 必须遵守的技术规范

- 每张幻灯片：width: 750px; height: 1334px; overflow: hidden;（这是微信截图的标准尺寸，不得改变）
- 字体：必须引用 Google Fonts，Noto Sans SC（标题）+ Noto Serif SC（正文）
- 序号标签：每张幻灯片上方必须有 .slide-label，显示 "01 / N · 内容名称"（帮用户识别截图顺序）
- 外层容器：深色背景 #111，幻灯片垂直居中排列，间距 40px

### 文件模板骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>[活动名] · 竖版幻灯片</title>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:ital,wght@0,400;0,600;0,700;1,400&family=Noto+Sans+SC:wght@400;700;900&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #111; display: flex; flex-direction: column; align-items: center; padding: 48px 0 80px; gap: 40px; }
    .page-header { width: 750px; font-family: monospace; font-size: 12px; color: #444; letter-spacing: 2px; text-align: center; padding-bottom: 20px; border-bottom: 1px solid #2a2a2a; line-height: 1.8; }
    .slide-wrap { display: flex; flex-direction: column; gap: 10px; }
    .slide-label { font-family: monospace; font-size: 11px; color: #3a3a3a; letter-spacing: 3px; }
    .slide { width: 750px; height: 1334px; position: relative; overflow: hidden; flex-shrink: 0; }
  </style>
</head>
<body>
  <div class="page-header">[活动名] · 竖版幻灯片 · 共 N 张<br>在浏览器中打开，逐张截图即可用于微信图文</div>
  <div class="slide-wrap">
    <div class="slide-label">01 / N · 封面</div>
    <div class="slide s1">...</div>
  </div>
</body>
</html>
```

### 设计原则

颜色：每张全出血背景，全套 2-4 个主色，高对比度

排版：标题 Noto Sans SC 900（不小于 28px），正文 Noto Serif SC（不小于 14px），行高 1.8-2

装饰：用纯 CSS 实现——::before/::after 做水印/装饰圆，border-left 做引用线，色块做高亮

### 图片占位符

当某张幻灯片需要放图片时，用这个占位符：

```html
<!--图片替换：将下方 div 替换为 <img src="你的路径" style="width:100%;height:320px;object-fit:cover;">-->
<div style="width:100%;height:320px;background:#2a2a2a;display:flex;align-items:center;justify-content:center;border:2px dashed #444;color:#555;font-family:monospace;font-size:13px;letter-spacing:2px;">[ 图片：说明文字 ]</div>
```

---

## Step 4：输出文件

- 保存到用户当前工作目录，文件名 [活动名]_slides.html
- 告知：文件路径、张数、截图方法

截图方法告知用户：
- Mac 自带：Cmd + Shift + 4 框选每张幻灯片
- Chrome 扩展：GoFullPage 或 Awesome Screenshot（可精准截取）
- 截图后建议保存为 PNG，按顺序命名

---

## Step 5：支持迭代调整

每次调整后直接覆盖保存同一文件，说明改了什么。
支持：调整字号、更换配色、增删幻灯片、替换图片路径、修改文案等。

---

## 质量自查

在交付前确认：
- 每张幻灯片刚好 750x1334px，内容不溢出
- Google Fonts 已引用（fonts.googleapis.com）
- 每张幻灯片有 slide-label 序号标签
- 图片位置有占位符和替换说明
- 整套视觉风格一致
- HTML 可在浏览器直接打开无报错
