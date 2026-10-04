
# 706 微信推文排版规格 — Template Spec

> 本文档记录了经过实际出版验证的 706 编辑风格排版规格。
> 参考文件：`四月底杭州见_wechat_fixed.html`（2025-04 确认版）
> 实现参考：`706知识库/by-project/2050/03-媒体区/md_to_wechat.py`

---

## 颜色方案

| 角色 | CSS 值 | 用途 |
|------|--------|------|
| `bg` | `rgb(242,247,244)` | 全局背景、每个元素的 background-color |
| `accent` | `rgb(26,123,90)` | 强调色：标签、边框、链接、装饰线 |
| `body` | `rgb(102,102,102)` | 正文段落文字 |
| `title` | `rgb(26,26,26)` | 标题、加粗文字 |
| `aux` | `rgb(153,153,153)` | 辅助文字：英文副标题、章节中文标签 |
| `caption` | `rgb(170,170,170)` | 图注文字 |
| `divider` | `rgb(217,234,227)` | 分隔线、表格边框 |
| `accent_bg` | `rgb(233,243,238)` | 引用块背景 |

---

## 文章外层容器

```html
<table cellpadding="0" cellspacing="0" border="0"
       style="background-color:rgb(242,247,244);border-collapse:collapse;width:100%;">
<tr>
<td style="padding:70px 30px 100px;
           background-color:rgb(242,247,244);
           font-family:'PingFang SC','Microsoft YaHei',sans-serif;
           color:rgb(102,102,102);
           line-height:1.6;
           word-break:break-all;">
  <!-- 文章内容 -->
</td>
</tr>
</table>
```

---

## 文章头部区块（一次性，文章开头）

### 1. 栏目标签

```html
<p style="margin:0;
          font-size:11px;
          letter-spacing:4px;
          color:rgb(26,123,90);
          font-weight:bold;
          text-transform:uppercase;
          background-color:rgb(242,247,244);">
  706 × WAY TO AGI / 2050
</p>
```

> 格式：`{社群} × {专题} / {类型}`，全大写，4px 字间距

### 2. 主标题（38px 衬线）

```html
<p style="margin:30px 0 0;
          font-family:'Times New Roman','Source Han Serif SC',STSong,'Songti SC',serif;
          font-size:38px;
          font-weight:normal;
          color:rgb(26,26,26);
          line-height:1.2;
          background-color:rgb(242,247,244);">
  文章主标题
</p>
```

> 注意：`font-weight:normal`（不加粗），衬线字体优先 Times New Roman

### 3. 英文副标题

```html
<p style="margin:25px 0 0;
          font-size:13px;
          letter-spacing:6px;
          color:rgb(153,153,153);
          text-transform:uppercase;
          background-color:rgb(242,247,244);">
  ENGLISH SUBTITLE HERE
</p>
```

> 格式：概括文章主旨的英文短句，全大写，6px 字间距

### 4. 细装饰线

```html
<section style="width:30px;height:1px;background-color:rgb(26,123,90);margin:40px 0;">
   
</section>
```

> 30px 宽、1px 高，accent 绿色，上下各 40px 间距

---

## 章节结构

每个 `###` 级章节包裹在 `<section style="margin-bottom:60px">` 中。
第一个章节额外加 `margin-top:80px`。

### 章节标题行（英文编号 + 中文标签）

```html
<p style="margin:0 0 15px;
          background-color:rgb(242,247,244);
          overflow:hidden;">
  <span style="font-size:12px;
               color:rgb(153,153,153);
               font-family:Arial;
               float:right;">
    [ 中文标签 ]
  </span>
  <span style="font-family:'Times New Roman',serif;
               font-size:16px;
               color:rgb(26,123,90);
               font-weight:bold;
               letter-spacing:2px;">
    01. ENGLISH
  </span>
</p>
```

> 英文编号：Times New Roman 16px，accent 绿色，bold，2px 字间距
> 中文标签：Arial 12px，aux 灰色，float:right（在 p 内部右对齐）

### 章节中文大标题

```html
<p style="margin:0 0 20px;
          font-size:20px;
          font-weight:bold;
          color:rgb(26,26,26);
          line-height:1.4;
          background-color:rgb(242,247,244);">
  章节中文标题
</p>
```

### 本文 8 章节的英文/中文标签映射

| 编号 | 英文标签 | 中文标签 |
|------|----------|----------|
| 01 | PREFACE | 背景 |
| 02 | FRIDAY | 4/24 |
| 03 | SATURDAY | 4/25 |
| 04 | SUNDAY | 4/26 |
| 05 | BOOTH | 摊位 |
| 06 | LOGISTICS | 行程 |
| 07 | JOIN US | 参会 |
| 08 | FIND US | 到场 |

---

## 正文段落

```html
<!-- 第一段（section 内无 margin-top） -->
<section style="font-size:15px;
                color:rgb(102,102,102);
                line-height:2;
                text-align:justify;
                background-color:rgb(242,247,244);">
  段落内容
</section>

<!-- 后续段落（加 margin-top:16px） -->
<section style="font-size:15px;
                color:rgb(102,102,102);
                line-height:2;
                text-align:justify;
                background-color:rgb(242,247,244);
                margin-top:16px;">
  段落内容
</section>
```

> 重要：使用 `<section>` 而非 `<p>`，微信对两者的渲染行为一致，但 section 更易控制间距。
> `margin-top:16px` 只加在同一 section 内的非首段落。遇到新的 `###` 标题时重置计数。

### Inline 格式

```html
<!-- 加粗 -->
<strong style="color:rgb(26,26,26);font-weight:bold;">加粗文字</strong>

<!-- 斜体 -->
<em style="color:rgb(153,153,153);font-style:italic;">斜体文字</em>

<!-- 链接 -->
<a href="URL" style="color:rgb(26,123,90);text-decoration:none;">链接文字</a>
```

---

## 引用块

### 标准引用块

```html
<section style="border-left:3px solid rgb(26,123,90);
                padding:12px 16px;
                margin:16px 0;
                background-color:rgb(233,243,238);">
  <p style="font-size:15px;
            line-height:2;
            color:rgb(102,102,102);
            margin:0;
            background-color:rgb(233,243,238);
            text-align:justify;">
    引用内容
  </p>
</section>
```

### 歌词引用块（诗句 + 署名）

用于文章中的歌词/诗句引用，斜体内容 + 灰色右对齐署名：

```html
<section style="border-left:3px solid rgb(26,123,90);
                padding:12px 16px;
                margin:16px 0;
                background-color:rgb(233,243,238);">
  <p style="font-size:15px;
            line-height:2;
            color:rgb(102,102,102);
            margin:0;
            background-color:rgb(233,243,238);
            text-align:justify;
            font-style:italic;">
    望西湖，胜景依然在，只觉得，新旧交替气象改。
  </p>
</section>
<p style="font-size:11px;
          color:rgb(170,170,170);
          text-align:right;
          margin:4px 0 14px;
          letter-spacing:0.5px;
          background-color:rgb(242,247,244);">
  沈俭安《开篇·西湖景》，1920年代
</p>
```

> 注意：署名行不属于引用块内部，而是独立段落右对齐于引用块下方。

### 卷首语/题记（斜体引用）

文章开头或章节开头的斜体题记，无左边框，全段斜体：

```html
<section style="font-size:15px;
                color:rgb(102,102,102);
                line-height:2;
                text-align:justify;
                background-color:rgb(242,247,244);
                font-style:italic;
                margin-bottom:40px;">
  五百个明天同时摊在你面前。你活完了其中一次。
</section>
```

---

## 子标题（#### 级别）

```html
<p style="font-size:15px;
          font-weight:bold;
          color:rgb(26,26,26);
          margin:20px 0 8px;
          background-color:rgb(242,247,244);
          line-height:1.5;
          letter-spacing:0.3px;">
  子标题文字
</p>
```

---

## 图片

### 场景图（带 caption）

```html
<img src="图片URL或base64" style="max-width:100%;height:auto;display:block;margin:16px auto 0;" />
<p style="font-size:11px;
          color:rgb(170,170,170);
          text-align:right;
          margin:6px 0 20px;
          letter-spacing:0.5px;
          background-color:rgb(242,247,244);">
  图注文字
</p>
```

> 本地图片：base64 内嵌（data URI），不依赖网络。
> 图片宽度默认 max-width:100%，特殊图片（如二维码）可设为 50% 等。

#### Caption 拆分规则

图片下方的多句段落按第一句话拆分为 caption + 正文段落：

```
Markdown:
![ ](图片.jpg)
安德鲁看到的东西，更像一层一层剥开的截面。第一层，物质世界：全球三亿个岗位面临自动化冲击。

生成结果：
<img src="..." />
<p style="...caption-style...">安德鲁看到的东西，更像一层一层剥开的截面。</p>
<section style="...paragraph-style...">第一层，物质世界：全球三亿个岗位面临自动化冲击。</section>
```

> - 拆分标点：`。！？`
> - 如果图片和文字之间有空白行，需要 lookahead 跳过空白行再检测
> - 以下情况跳过 caption 检测：紧跟 `>` blockquote、紧跟 `*...*` italic、紧跟章节标记、以「感谢」「第一层」「第二份」等开头

### 头像（圆形）

```html
<p style="text-align:center;margin:12px 0 8px;background-color:rgb(242,247,244);">
  <img src="base64..." style="width:140px;height:140px;
                               display:inline-block;
                               border-radius:50%;
                               object-fit:cover;" />
</p>
```

> 头像处理规则：
> - 原图 → center-crop 正方形 → resize 300×300 → JPEG（quality=88）→ base64
> - 旋转修正、crop_y_frac 偏移：在 `PER_IMAGE` dict 中配置
> - 显示尺寸：默认 140px，特殊头像可在 `PER_IMAGE` 中配置 `display_px`

---

## 脚注（参考资料区块）

用于文末的注释/参考文献，小号字体，编号用 accent 绿色加粗：

```html
<p style="font-size:14px;
          font-weight:bold;
          color:rgb(26,26,26);
          margin:30px 0 12px;
          background-color:rgb(242,247,244);">
  参考资料
</p>
<section style="font-size:13px;
                color:rgb(102,102,102);
                line-height:1.8;
                text-align:justify;
                background-color:rgb(242,247,244);
                margin-top:8px;">
  <strong style="color:rgb(26,123,90);
                 font-weight:bold;
                 font-size:12px;">
    [1]
  </strong>
  脚注内容正文，使用稍小字号和紧凑行距。
</section>
```

> - 正文中引用：`<sup style="color:rgb(26,123,90);font-size:11px;">[1]</sup>`
> - 脚注按编号排序，每条约 13px 字号，line-height: 1.8
> - 编号用 accent 绿色加粗，正文用 body 灰色

---

## 列表

```html
<ul style="margin:8px 0 16px 18px;padding:0;background-color:rgb(242,247,244);">
  <li style="font-size:15px;line-height:1.8;color:rgb(102,102,102);
             margin:4px 0;background-color:rgb(242,247,244);">
    列表项
  </li>
</ul>
```

---

## 表格

```html
<table style="width:100%;border-collapse:collapse;margin:14px 0 20px;
              background-color:rgb(242,247,244);font-size:13px;table-layout:fixed;">
  <tr>
    <th style="padding:8px 10px;border:1px solid rgb(217,234,227);
               background-color:rgb(233,243,238);color:rgb(26,26,26);
               font-weight:bold;text-align:left;word-break:break-all;">
      表头
    </th>
  </tr>
  <tr>
    <td style="padding:8px 10px;border:1px solid rgb(217,234,227);
               color:rgb(102,102,102);background-color:rgb(242,247,244);
               word-break:break-all;">
      内容
    </td>
  </tr>
</table>
```

---

## 预览框架（不进入微信，仅用于本地预览）

```html
body { background: #1a1a1a; }
.toolbar { position: sticky; top: 0; z-index: 100;
           background: rgba(26,26,26,0.95); backdrop-filter: blur(10px); }
.btn-copy { background: rgb(26,123,90); color: white; border-radius: 6px; }
.phone-frame { width: 375px; background: rgb(242,247,244);
               border-radius: 12px; overflow: hidden;
               box-shadow: 0 0 60px rgba(0,0,0,0.5); }
```

---

## 微信兼容性要点（关键）

1. **所有样式必须 inline**，`<style>` 标签在粘贴时会被剥离
2. **每个元素必须有 `background-color`**，微信会剥离外层容器
3. **外层用 `<table>` 包裹**，不用 `<div>` flex
4. **图片嵌入 base64**（本地预览时），或使用公网 URL（微信会重新托管）
5. **不用 `rem`/`em`/`vw`**，只用 `px`
6. **font-family 中的空格字体名用单引号**（双引号会破坏 `style="..."` 属性）
