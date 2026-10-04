# 706 微信排版设计升级分析

> 基于 [beautiful-html-templates](https://github.com/zarazhangrui/beautiful-html-templates) 34 套设计系统，
> 结合微信编辑器渲染约束，为 706 wechat-publish 提供可落地的设计混搭升级方案。

---

## 一、当前 706 设计 DNA

| 维度 | 当前值 |
|------|--------|
| **风格定位** | 文学期刊 / 小出版社编辑风 |
| **底色** | `rgb(242,247,244)` — 微绿冷调纸色 |
| **强调色** | `rgb(26,123,90)` — 单一深绿 |
| **标题字体** | Times New Roman / Source Han Serif SC（衬线） |
| **正文字体** | PingFang SC（无衬线） |
| **装饰语言** | 30px × 1px 绿色细线、左边框引用块、圆形头像 |
| **结构** | table 包裹、section 分段、`01. ENGLISH [ 中文 ]` 章节编号 |
| **气质** | 安静、克制、知识分子气 |

**问题**：单一配色方案缺乏变化，所有文章看起来一样。活动预告、深度长文、招募文案共用一套视觉语言。

---

## 二、beautiful-html-templates 设计分类学

34 套模板按设计基因可分为以下族群：

### 族群 A：编辑文学风（与 706 基因最接近）
| 模板 | 核心色板 | 关键设计信号 |
|------|---------|------------|
| **Soft Editorial** | `#F2EEDF` 暖纸 + sage/blush/pink/lemon 四粉彩 | Cormorant Garamond 衬线主导、半透明圆角卡片、罗马数字编号 |
| **Editorial Tri-Tone** | `#F2B6C6` 粉 + `#F2D86A` 黄油 + `#7A1F35` 勃艮第 | 严格三色约束、Bricolage + Instrument Serif 双字体、em-规则 |
| **Editorial Forest** | 森林绿 + 尘土粉 + 暖奶油 | Source Serif 4，季度汇报气质 |
| **Emerald Editorial** | 祖母绿 + 深蓝 + 纸白 | 杂志封面式、双线刊头装饰、Bodoni 风展示衬线 |

### 族群 B：深色权威风（适合重磅长文、年度报告）
| 模板 | 核心色板 | 关键设计信号 |
|------|---------|------------|
| **Signal** | `#1C2644` 深蓝 + `#F0ECE3` 奶油 + `#C8A870` 古董金 | 单一金色点缀、金色斜体强调、em-dash 列表标记、36px 金线分隔 |
| **Vellum** | `#2A3870` 长春花蓝 + `#E8D85C` 暖黄 + `#3A7878` 灰绿 | 全斜体基线（反转惯例）、pin-annotation 每页签名、全居中 |
| **Broadside** | `#111111` 近黑 + `#F0ECE5` 奶油 + `#E85D26` 火焰橙 | 标语海报能量、Barlow 单字体、双注册器（暗/橙）、全部小写 |
| **Studio** | 纯黑底 + 电黄字 | 高压设计工作室美学 |

### 族群 C：活泼暖调风（适合活动招募、社群内容）
| 模板 | 核心色板 | 关键设计信号 |
|------|---------|------------|
| **Biennale Yellow** | `#E9E5DB` 羊皮纸 + `#F1EE2E` 太阳黄 + `#1B2566` 靛蓝墨 | 太阳光晕径向渐变、仅 1px 发丝线、无圆角无阴影 |
| **Long Table** | `#FAF1E2` 奶油 + `#B53D2A` 陶土锈红（单墨色） | 晚餐俱乐部美学、描边语言（无填充）、Fraunces italic 默认、虚线分隔 |
| **Playful** | 桃色底 + Syne 展示体 | 阳光独立产品发布风 |
| **Daisy Days** | 粉彩 + 手绘雏菊/星星/彩虹 | 欢快、柔软、温暖 |

### 族群 D：粗野/结构风（适合强调态度、宣言式内容）
| 模板 | 核心色板 | 关键设计信号 |
|------|---------|------------|
| **Neo-Grid Bold** | `#F5F4EF` 纸 + `#0A0A0A` 墨 + `#E6FF3D` 霓虹柠檬 | 12×8 网格面板、零圆角、`<mark>` 荧光笔强调、Space Grotesk 全大写 |
| **Raw Grid** | 粉/鼠尾草/墨水 | 粗边框、偏移阴影 |
| **BlockFrame** | 粉彩霓虹色块 + 粗黑边框 | 新粗野主义 |

### 族群 E：极简/专业风
| 模板 | 核心色板 | 关键设计信号 |
|------|---------|------------|
| **Monochrome** | 象牙账本纸 + 全黑字 | 纯黑白、Lora 衬线标题 + Jost 正文、无彩色 |
| **Cartesian** | 暖中性调 + Playfair 衬线 | 安静、古典、不慌不忙 |
| **Blue Professional** | 奶油纸 + 电钴蓝 | 干净现代专业 |

---

## 三、微信渲染约束过滤器

### 可以直接迁移的设计手段

| 设计元素 | 微信支持 | 迁移方式 |
|---------|---------|---------|
| **色板** | ✅ 完全支持 | 直接替换 hex 色值为 inline `color`/`background-color` |
| **字体层次** | ⚠️ 仅系统字体 | PingFang SC / Microsoft YaHei / STSong / Songti SC / Times New Roman / Arial |
| **字号阶梯** | ✅ px 单位 | 按比例缩小（桌面 1920px → 微信 375px ≈ 缩小 5 倍） |
| **字间距** | ✅ `letter-spacing` px | 保留，但要缩小 |
| **1px 发丝线** | ✅ | `<section>` 或 `<hr>` 带 inline style |
| **边框** | ✅ `border`/`border-left` | 引用块、描边卡片 |
| **圆角** | ⚠️ 部分支持 | `border-radius` 可用，但不要依赖它做关键区分 |
| **背景色块** | ✅ | 每个元素带 `background-color`（微信强制要求） |
| **`<mark>` 荧光笔** | ✅ | Neo-Grid Bold 的黄色高亮可直接使用 |
| **表格布局** | ✅ | 外层 `<table>` 包裹（706 已经在用）|
| **Section 分段** | ✅ | 用 `<section>` 分隔内容块 |
| **Em-dash 列表标记** | ✅ | Signal 的 `—` 替换 bullet 点 |
| **描边按钮/标签** | ✅ | Long Table 的 pill-shaped outlined buttons |
| **双色文字强调** | ✅ | 用 `<span style="color:...">` 做句子内强调色切换 |
| **虚线分隔** | ✅ | `border-top: 1px dashed ...` |
| **粗黑边框** | ✅ | Raw Grid/BlockFrame 的粗框风格 |

### 必须变通/降级的设计手段

| 设计元素 | 微信限制 | 降级方案 |
|---------|---------|---------|
| **Google Fonts** | ❌ 无法加载外部字体 | → 系统字体栈：Songti SC 替代 Cormorant/Instrument Serif，PingFang SC 替代 Work Sans/DM Sans |
| **CSS 变量** | ❌ 不支持 | → 所有色值直接内联写死 |
| **`::before`/`::after`** | ❌ 不支持 | → 用真实 DOM 元素（如 `<span>` 或空 `<section>`）替代伪元素装饰 |
| **绝对定位 chrome** | ❌ 微信剥离 | → pin-annotation、页眉页脚等改为内联流式元素 |
| **径向渐变 sun-bloom** | ❌ 不支持复杂渐变 | → 用纯色块 + 透明度模拟，或放弃渐变效果 |
| **`clamp()`/vw 单位** | ❌ | → 固定 px 值，移动端 375px 基准 |
| **Flexbox/Grid** | ❌ | → `<table>` 布局、`text-align`、`float` |
| **`backdrop-filter`** | ❌ | → 纯色不透明背景替代毛玻璃 |
| **`box-shadow`** | ❌ 微信剥离 | → 用边框或背景色差替代阴影深度 |
| **CSS counter 自动编号** | ❌ | → 手动写死编号 |
| **斜体轴切换** | ⚠️ CJK 无 italic | → 用颜色切换替代字体切换（Signal/Broadside 的 CJK 策略）|
| **垂直旋转文字** | ❌ | → 改为水平标签 |
| **半透明卡片** | ⚠️ RGBA 支持不稳定 | → 用实色背景替代 `rgba(255,255,255,0.55)` |
| **纹理叠加** | ❌ 不支持伪元素 | → 用实际背景图片（base64）或放弃 |

---

## 四、8 套设计混搭配方

每套配方给出：**灵感来源 → 色板替换 → 字体映射 → 结构变化 → 适用场景**。

### 配方 1：温润文学（Soft Editorial × 706）

**灵感**：Soft Editorial 的暖纸 + 多粉彩系统

**色板替换**（替代当前绿色系）：
```
bg:       #F2EEDF  ← 暖奶油纸（替代 rgb(242,247,244) 冷调纸）
title:    #2A241B  ← 暖近黑（替代 rgb(26,26,26)）
body:     #5C5345  ← 暖灰褐（替代 rgb(102,102,102)）
accent:   #B7C7A8  ← 鼠尾草绿（替代 rgb(26,123,90) 深绿）
accent2:  #E8C9B6  ← 柔和桃（新增第二强调色）
accent3:  #E1A4C2  ← 尘土玫瑰（新增第三强调色）
accent4:  #D6DD63  ← 黄绿柠檬（最亮强调色）
aux:      #8A8276  ← 暖灰
caption:  #A0988A
divider:  rgba(42,36,27,0.18)
accent_bg: #F5F0E3  ← 暖调引用块背景
```

**字体映射**：
```
Cormorant Garamond → 'Times New Roman', 'Songti SC', STSong, serif
Work Sans           → 'PingFang SC', 'Microsoft YaHei', sans-serif
```

**结构变化**：
- 引用块卡片加 `border-radius: 14px`（圆角卡片感）
- 章节编号用中文小写数字（一、二、三...）替代阿拉伯数字
- 每个 `<section>` 段落之间增加间距到 24px（更宽松的呼吸感）

**适用场景**：深度长文、文学性内容、人物访谈

---

### 配方 2：智库权威（Signal × 706）

**灵感**：Signal 的双表面 + 单一金色点缀

**色板替换**：
```
-- 浅色面（默认）--
bg:       #F0ECE3  ← 奶油（替代绿调纸）
title:    #1C2644  ← 深蓝（替代纯黑）
body:     #3A4560  ← 蓝灰（替代灰）
accent:   #C8A870  ← 古董金（替代绿）
aux:      #8A8D98
caption:  #9A9DA6
divider:  #CAC4B4
accent_bg: #E8E4D8  ← 暖调引用块背景

-- 深色面（用于头部或重点章节）--
bg_dark:  #1C2644  ← 深蓝底
text_on_dark: #F0ECE3  ← 奶油字
accent_on_dark: #C8A870  ← 金（不变）
```

**字体映射**：
```
Source Serif 4 → 'Times New Roman', 'Songti SC', serif
DM Sans         → 'PingFang SC', sans-serif
IBM Plex Mono   → 'SF Mono', 'Menlo', 'Courier New', monospace  ← 用于元数据/编号
```

**结构变化**：
- 文章头部区块切换为深蓝背景 + 奶油色标题 + 金色装饰线
- 章节编号改用等宽字体（`font-family: 'SF Mono', monospace`）
- 列表标记从 `•` 改为 `—`（em-dash，金色）
- 增加「36px 金色短装饰线」作为章节标题与正文之间的分隔
- 斜体强调改为金色着色（CJK 无 italic 轴的补偿策略）

**HTML 头部深色区块示例**：
```html
<table cellpadding="0" cellspacing="0" border="0"
       style="background-color:#1C2644;border-collapse:collapse;width:100%;">
<tr>
<td style="padding:70px 30px;
           background-color:#1C2644;
           font-family:'PingFang SC','Microsoft YaHei',sans-serif;
           color:#F0ECE3;">
  <!-- 栏目标签（金色等宽体） -->
  <p style="margin:0;font-size:11px;letter-spacing:4px;
            color:#C8A870;font-family:'SF Mono','Menlo',monospace;
            font-weight:bold;text-transform:uppercase;
            background-color:#1C2644;">
    706 × 2050
  </p>
  <!-- 36px 金色装饰线 -->
  <section style="width:36px;height:1px;background-color:#C8A870;margin:24px 0;"></section>
  <!-- 主标题 -->
  <p style="margin:0;font-family:'Times New Roman','Songti SC',serif;
            font-size:38px;color:#F0ECE3;line-height:1.2;
            background-color:#1C2644;">
    文章主标题
  </p>
</td>
</tr>
</table>
```

**适用场景**：年度报告、深度分析、机构/品牌向内容

---

### 配方 3：三色文学（Editorial Tri-Tone × 706）

**灵感**：严格三色约束 + 颜色角色语义化

**色板替换**（三个颜色承担所有角色）：
```
墨水色:  #7A1F35  ← 深勃艮第（承担 title/body/line 角色）
暖中间:  #F2D86A  ← 金黄黄油（承担 浅底/accent2 角色）
亮强调:  #F2B6C6  ← 尘土粉（承担 accent/链接/highlight 角色）

实际映射：
bg:       #FCF5E8  ← 极浅黄油调（保留可读性）
title:    #7A1F35
body:     #7A1F35（降低到 85% 不透明度 → 实际用 #8B3A4A）
accent:   #F2B6C6 → 但链接需要可读，实际用 #7A1F35 + bold
aux:      #A0727E（勃艮第的淡化版本）
divider:  #E8D5C0（黄油 + 纸的混合）
accent_bg: #FDF0E8（极浅粉）
highlight_text: #C82650 ← 亮化后的勃艮第，用于句子内强调
```

**字体映射**：
```
Bricolage Grotesque → 'PingFang SC', sans-serif（bold 700-800 用于标题）
Instrument Serif    → 'Times New Roman', 'Songti SC', serif（italic 用于引语）
JetBrains Mono      → 'SF Mono', 'Menlo', monospace（用于标签/元数据）
```

**结构变化**：
- 双色交替卡片：奇数段浅黄油底 + 勃艮第字，偶数段深勃艮第底 + 黄油字
- 章节编号的英文部分用衬线 italic（Times New Roman italic）
- 引语块用 `"` 大字标记（需用一个真实 `<span>` 元素放大的引号）
- 链接改为深勃艮第加粗 + 下划线（不用绿色）

**三色交替卡片示例**：
```html
<!-- 浅底卡片 -->
<section style="background-color:#FCF5E8;padding:20px 16px;
                margin:16px 0;border-radius:4px;
                font-size:15px;color:#7A1F35;line-height:2;text-align:justify;">
  段落内容在浅黄油底上
</section>

<!-- 深底卡片 -->
<section style="background-color:#7A1F35;padding:20px 16px;
                margin:16px 0;border-radius:4px;
                font-size:15px;color:#FCF5E8;line-height:2;text-align:justify;">
  段落内容在深勃艮第底上
</section>
```

**适用场景**：论坛回顾、文化评论、有态度的内容

---

### 配方 4：双年展黄（Biennale Yellow × 706）

**灵感**：荷兰编辑海报的太阳黄 + 靛蓝墨

**色板替换**：
```
bg:       #E9E5DB  ← 暖羊皮纸（替代绿调纸）
title:    #1B2566  ← 深靛蓝（替代纯黑，更温暖）
body:     #1B2566  ← 正文也用靛蓝（单墨色哲学）
accent:   #F1EE2E  ← 太阳黄（替代绿，非常亮）
aux:      #5C6180（靛蓝淡化）
caption:  #8A8D9E
divider:  #1B2566  ← 靛蓝 1px 发丝线
accent_bg: #F1EE2E（15% 不透明度 → 实际用 #F6F5E8）
```

**字体映射**：
```
Instrument Serif → 'Times New Roman', 'Songti SC', serif
Archivo          → 'PingFang SC', sans-serif
```

**结构变化**：
- 所有分隔线严格 1px，颜色为靛蓝 `#1B2566`
- 章节标题数字使用超大衬线（如 `font-size: 72px` 的 "01" 作为章节入口）
- 关键引用或金句用黄色背景高亮块 + 靛蓝字（类似 `<mark>` 的强化版）
- 文章头部下方增加一个黄色色块 + 靛蓝字的日期/地点信息条

**章首大数字示例**：
```html
<!-- 章节大数字入口 -->
<p style="margin:60px 0 0;
          font-family:'Times New Roman','Songti SC',serif;
          font-size:72px;line-height:1;
          color:#1B2566;font-weight:bold;
          background-color:#E9E5DB;">
  01
</p>
<!-- 1px 靛蓝发丝线 -->
<section style="width:100%;height:1px;background-color:#1B2566;margin:12px 0 24px;"></section>
<!-- 章节标题 -->
<p style="margin:0 0 20px;font-size:20px;font-weight:bold;
          color:#1B2566;background-color:#E9E5DB;">
  章节中文标题
</p>
```

**适用场景**：艺术展览预告、文化活动报道、设计/创意类内容

---

### 配方 5：晚宴菜单（Long Table × 706）

**灵感**：单墨色陶土锈红 + 描边语言 + 奶油底

**色板替换**（全篇只用一种强调色！）：
```
bg:          #FAF1E2  ← 黄油奶油纸
title/body:  #3D2018  ← 深棕（替代纯黑，更暖）
accent:      #B53D2A  ← 陶土锈红（唯一强调色，替代绿）
aux:         #9B7B70（棕色淡化）
caption:     #B0A090
divider:     #B53D2A（32% → #E2C8B8 或虚线 #D4A090）
accent_bg:   #FDF5EC（极浅暖调引用块）
```

**字体映射**：
```
Bricolage Grotesque → 'PingFang SC', sans-serif（bold 用于标题，全大写 → 中文不加粗）
Fraunces italic      → 'Times New Roman', 'Songti SC', serif（italic 用于元数据、图注）
```

**结构变化**：
- **描边卡片**：不用背景色填充，用 `border: 1.5px solid #B53D2A` + `border-radius: 999px` 做药丸标签
- **虚线分隔**：章节之间用 `border-top: 1px dashed #D4A090` 替代实线
- **描边按钮**：行动召唤链接用 `border: 1.5px solid #B53D2A; border-radius: 999px; padding: 8px 24px` 的药丸按钮
- **版次编号**：文末加一个 Fraunces-style 的大号斜体数字（如 "No. 12"）

**描边药丸标签示例**：
```html
<!-- 药丸标签（用于栏目标签或活动类型） -->
<span style="display:inline-block;
             border:1.5px solid #B53D2A;
             border-radius:999px;
             padding:6px 20px;
             font-size:12px;color:#B53D2A;
             letter-spacing:4px;
             font-family:'PingFang SC',sans-serif;
             background-color:#FAF1E2;
             margin-bottom:24px;">
  706 × 2050
</span>
```

**适用场景**：晚宴/聚会回顾、小型活动邀请、亲密场合

---

### 配方 6：宣言海报（Broadside × 706）

**灵感**：标语海报的暗底 + 单强调色 + 巨大标题

**色板替换**：
```
-- 暗色注册器 --
bg_dark:   #111111
text_dark: #F0ECE5  ← 奶油白字
accent:    #E85D26  ← 火焰橙（替代绿）

-- 亮色注册器（用于封面/重点） --
bg_accent: #E85D26  ← 满铺火焰橙
text_on_accent: #111111  ← 近黑字
```

**字体映射**：
```
Barlow 900  → 'PingFang SC', sans-serif（bold/black weight）
Barlow 400  → 'PingFang SC', sans-serif（regular weight）
IBM Plex Mono → 'SF Mono', monospace（用于标签/编号）
```

**结构变化**：
- **双注册器系统**：文章在「暗底 + 橙字」和「橙底 + 黑字」两种模式之间切换
- 头部使用暗底 + 极大标题（38px → 可到 48-56px）
- 关键引语用橙色底 + 黑字的反转卡片
- 段落间距扩大（24-32px），信息密度降低——「密度在于冲击力，不在于信息量」
- 元数据标签用等宽字体大写 + 宽字间距

**反转卡片示例**：
```html
<!-- 橙底反转引语卡片 -->
<section style="background-color:#E85D26;padding:24px 20px;
                margin:32px 0;
                font-size:20px;line-height:1.6;
                color:#111111;text-align:center;
                font-family:'Times New Roman','Songti SC',serif;
                font-style:italic;">
  "五百个明天同时摊在你面前。你活完了其中一次。"
</section>
```

**适用场景**：宣言式文章、大型活动召集、青年文化/态度内容

---

### 配方 7：深蓝画廊（Vellum × 706）

**灵感**：单深蓝场域 + 暖黄字 + 灰绿点缀 + 全居中

**色板替换**（全篇深蓝底！）：
```
bg:       #2A3870  ← 长春花深蓝（全篇统一背景）
title:    #E8D85C  ← 暖黄
body:     #E8D85C  ← 暖黄（正文也用黄色，降低不透明度做层次）
body_dim: 黄色 62% → 实际用 #B8AD80（第二级正文）
body_faint: 黄色 32% → 实际用 #8A8466（第三级/辅助文字）
accent:   #3A7878  ← 灰绿（仅用于 kicker、编号标记、装饰线）
accent_bright: #F5E168  ← 亮黄（用于标题内重点词强调）
```

**字体映射**：
```
Cormorant Garamond italic → 'Times New Roman', 'Songti SC', serif（italic）
DM Sans                    → 'PingFang SC', sans-serif
Courier Prime              → 'SF Mono', 'Menlo', monospace ← 用于 pin-annotation
```

**结构变化**：
- 全局背景从浅色切换为深蓝（`#2A3870`），所有文字用暖黄色系
- **居中布局**：`text-align: center` 应用于标题和关键段落
- 每段末尾加一个「灰绿色 pin 标注」（等宽字体、小号、灰绿色 `#3A7878`），像档案标签
- 编号列表用等宽字体计数器（灰绿色）
- 引语用大字灰绿引号标记
- 装饰线是灰绿色 `#3A7878` 而非金色

**pin-annotation 示例**（Vellum 标志性元素在微信中的降级实现）：
```html
<!-- 段落末尾的档案式标注 -->
<p style="text-align:right;font-size:11px;color:#3A7878;
          font-family:'SF Mono','Menlo',monospace;
          letter-spacing:1px;margin:8px 0 0;
          background-color:#2A3870;">
  03 / 09 · 706 知识档案
</p>
```

**适用场景**：哲学/思辨长文、知识档案、深夜阅读内容

---

### 配方 8：新粗野（Neo-Grid Bold × 706）

**灵感**：三色网格面板 + 零圆角 + 霓虹黄荧光笔

**色板替换**：
```
bg:       #F5F4EF  ← 偏暖纸（替代绿调纸）
title:    #0A0A0A  ← 纯黑
body:     #0A0A0A  ← 正文也用纯黑（高对比）
accent:   #E6FF3D  ← 霓虹柠檬黄（替代绿，极度醒目）
aux:      #6B6B6B
accent_bg: #E6FF3D  ← 霓虹黄背景（用于高亮标记）
```

**字体映射**：
```
Space Grotesk 700 → 'PingFang SC', sans-serif（bold/heavy weight）
Space Grotesk 400 → 'PingFang SC', sans-serif（regular）
JetBrains Mono    → 'SF Mono', 'Menlo', monospace
```

**结构变化**：
- **零圆角**：所有元素 `border-radius: 0`（与当前 706 的圆角头像形成反差）
- **`<mark>` 荧光笔**：关键句子用霓虹黄 `background-color: #E6FF3D` + `padding: 0 4px` 高亮
- **黑色反转块**：用纯黑底 + 白字 + 霓虹黄点缀的信息卡片
- **表格网格面板**：用 `<table>` 做 2 列布局（微信唯一支持的多列方式）
- 页码标记用等宽字体：`01 / 12` 格式

**荧光笔高亮示例**：
```html
<!-- 句子内霓虹黄高亮 -->
<section style="font-size:15px;color:#0A0A0A;line-height:2;
                background-color:#F5F4EF;">
  安德鲁看到的东西，<span style="background-color:#E6FF3D;padding:0 4px;">更像一层一层剥开的截面</span>。第一层，物质世界：全球三亿个岗位面临自动化冲击。
</section>
```

**双列表格面板示例**（利用微信对 `<table>` 的支持）：
```html
<table cellpadding="0" cellspacing="0" border="0"
       style="width:100%;border-collapse:collapse;
              background-color:#F5F4EF;table-layout:fixed;">
<tr>
  <td style="width:50%;padding:16px;vertical-align:top;
             background-color:#0A0A0A;color:#F5F4EF;
             font-size:14px;line-height:1.8;">
    <p style="margin:0;font-size:36px;font-weight:bold;color:#E6FF3D;
              background-color:#0A0A0A;line-height:1.2;">
      300M
    </p>
    <p style="margin:8px 0 0;font-size:13px;color:#F5F4EF;
              background-color:#0A0A0A;">
      全球面临自动化冲击的岗位
    </p>
  </td>
  <td style="width:8px;background-color:#F5F4EF;"></td>
  <td style="width:50%;padding:16px;vertical-align:top;
             background-color:#F5F4EF;color:#0A0A0A;
             font-size:14px;line-height:1.8;
             border:2px solid #0A0A0A;">
    <p style="margin:0;font-size:36px;font-weight:bold;color:#0A0A0A;
              background-color:#F5F4EF;line-height:1.2;">
      47%
    </p>
    <p style="margin:8px 0 0;font-size:13px;color:#0A0A0A;
              background-color:#F5F4EF;">
      预计在未来 5 年内受到影响
    </p>
  </td>
</tr>
</table>
```

**适用场景**：科技评论、数据驱动文章、青年态度/亚文化内容

---

## 五、实现架构建议

### 5.1 设计配方即配置

在 `template-spec.md` 同级创建一个 `design-presets.json`：

```json
{
  "706-default": {
    "name": "706 经典绿",
    "inherits": null,
    "colors": {
      "bg": "rgb(242,247,244)",
      "accent": "rgb(26,123,90)",
      "body": "rgb(102,102,102)",
      "title": "rgb(26,26,26)",
      "aux": "rgb(153,153,153)",
      "caption": "rgb(170,170,170)",
      "divider": "rgb(217,234,227)",
      "accent_bg": "rgb(233,243,238)"
    }
  },
  "warm-literary": {
    "name": "温润文学",
    "inspiration": "Soft Editorial",
    "inherits": "706-default",
    "colors": {
      "bg": "#F2EEDF",
      "accent": "#B7C7A8",
      "body": "#5C5345",
      "title": "#2A241B",
      "aux": "#8A8276",
      "caption": "#A0988A",
      "divider": "#D9D2C2",
      "accent_bg": "#F5F0E3"
    },
    "font": {
      "serif": "'Times New Roman','Songti SC',STSong,serif",
      "sans": "'PingFang SC','Microsoft YaHei',sans-serif",
      "mono": "'SF Mono','Menlo',monospace"
    },
    "structural_flags": {
      "rounded_cards": true,
      "roman_numeral_chapters": true,
      "paragraph_gap": 24
    }
  },
  "institutional-gold": { "...": "Signal 映射" },
  "tri-tone-literary": { "...": "Editorial Tri-Tone 映射" },
  "biennale-sun": { "...": "Biennale Yellow 映射" },
  "supper-club": { "...": "Long Table 映射" },
  "manifesto-orange": { "...": "Broadside 映射" },
  "deep-blue-gallery": { "...": "Vellum 映射" },
  "neo-brutal": { "...": "Neo-Grid Bold 映射" }
}
```

### 5.2 文章 → 配方匹配逻辑

```
文章类型检测 → 推荐配色方案：

深度长文 / 人物访谈  → warm-literary（温润文学）
年度报告 / 白皮书    → institutional-gold（智库权威）
论坛回顾 / 文化评论  → tri-tone-literary（三色文学）
艺术展览 / 创意活动  → biennale-sun（双年展黄）
小型聚会 / 亲密场合  → supper-club（晚宴菜单）
宣言 / 态度 / 亚文化 → manifesto-orange（宣言海报）
哲学思辨 / 知识档案  → deep-blue-gallery（深蓝画廊）
科技评论 / 数据文章  → neo-brutal（新粗野）
活动预告 / 社群招募  → playful / daisy（待补充）
```

### 5.3 渐进式升级路径

| 阶段 | 内容 | 工作量 |
|------|------|--------|
| **Phase 1** | 在现有 template-spec 基础上新增 3 套配色预设（warm-literary / institutional-gold / tri-tone-literary） | 1 天 |
| **Phase 2** | 实现 `design-presets.json` 配置加载 + `md_to_wechat.py` 支持 `--preset` 参数 | 1 天 |
| **Phase 3** | 为每种配色新增对应的结构变体（深色头部、描边卡片、大数字章节等） | 2-3 天 |
| **Phase 4** | 文章类型自动检测 + 配方推荐 | 1 天 |
| **Phase 5** | 补充 dark mode 全系列（Broadside/Vellum 完整深色版） | 2 天 |

---

## 六、关键设计原则（跨配方不变）

以下原则来自 beautiful-html-templates 的分析，且与微信渲染兼容：

1. **每篇文章一个色彩人格** — 不要在一篇文章内混用不同配方的色板
2. **强调色唯一性** — 每套配方只有一个主强调色（Signal 的金、Broadside 的橙、Long Table 的锈红）
3. **字体角色严格分离** — 衬线做标题/引语，无衬线做正文，等宽做元数据
4. **装饰线 ≤ 1px** — Biennale Yellow 和 Signal 的规则：只做发丝线，不做粗分隔
5. **CJK 无 italic 轴 → 颜色切换替代** — 这是 Vellum/Signal/Tri-Tone 的 CJK 策略，也适用于微信
6. **密度控制** — Signal 的"不超过半页内容"、Broadside 的"一句一张"、Neo-Grid 的"不满格就是坏了"——选哪个取决于文章气质
7. **每个元素带 `background-color`** — 微信铁律，不变

---

## 七、优先推荐

按**视觉差异化程度 × 实现成本 × 微信兼容性**排序：

| 优先级 | 配方 | 理由 |
|--------|------|------|
| **P0** | 温润文学 | 与当前 706 基因最近，改动小，马上能出效果 |
| **P0** | 智库权威 | 深色头部 + 金色点缀，差异度高，适合"重磅"文章 |
| **P1** | 三色文学 | 三色约束 + 交替卡片，视觉识别度极高 |
| **P1** | 双年展黄 | 太阳黄 + 靛蓝，色彩组合独特，适合艺术类 |
| **P2** | 宣言海报 | 暗底反转，适合态度内容但全暗底在微信阅读体验待验证 |
| **P2** | 新粗野 | 荧光笔 + 零圆角 + 双列面板，新鲜感强 |
| **P3** | 深蓝画廊 | 全深蓝底阅读体验需用户测试 |
| **P3** | 晚宴菜单 | 单色描边语言优雅但差异度不如前几个明显 |
