---
name: media-ingest
description: 处理 706-media/inbox 中的待分类图片。场景优先二级分类：① 视觉识别判断场景/非场景 → ② 场景照片按活动类型（Tier 1）→ 地点（Tier 2）归档；③ 非场景素材（海报/logo/底图/二维码/截图）→ 宣传物料。支持：文件名中文标注解析、微信本地图片批次（manifest + Ollama/MiniCPM-V + OCR）、无标注散图视觉识别。触发表达：「整理 inbox」「处理 inbox 图片」「inbox 归一下」「把这批图入库」「新加了一批 XX 的文件」「处理微信导入图片」。
---

# Media Ingest — 媒体素材入库

把 `706-media/inbox/` 里的图片按**场景优先**的二级分类系统处理入库。

## 核心路径

```text
MEDIA_ROOT = $706_LOCAL/706-media
INBOX = MEDIA_ROOT/inbox
INDEX_FILE = MEDIA_ROOT/media-index.json
```

`inbox/` 是 706-media 的唯一素材入口。旧 `_inbox/` 目录已删除（2026-06-22 合并），不再使用。

## 分类系统：场景优先 · 二级架构

```
inbox 图片
  │
  ├─ [视觉识别：Ollama/MiniCPM-V]
  │
  ├─ 场景照片（有人/有活动）        → 场景/{活动类型}/{地点}/
  │   Tier 1: 活动类型
  │   Tier 2: 地点
  │
  └─ 非场景素材（海报/logo/截图等）  → 宣传物料/{子类}/
```

### Tier 1 · 场景类型（14 类）

| 场景类型 | 英文 slug | 判定线索 |
|----------|----------|----------|
| 工作坊 | workshop | 分组动手、白板、便签、工具材料 |
| 讲座-分享 | talk | 一人主讲、投影/屏幕、观众面向讲者 |
| 共居-日常 | coliving | 做饭、聊天、放松、非正式居家状态 |
| 论坛-圆桌 | panel | 多人并排/围坐、话筒、台上台下 |
| 放映-展映 | screening | 暗场、大屏幕/投影、电影/视频内容 |
| 读书会-共读 | reading | 围坐读书、书本、讨论文本 |
| 黑客松 | hackathon | 多台电脑、长时间密集、代码/终端界面 |
| 技术共学 | tech-learn | 技术主题、屏幕共享、Web3/AI 内容 |
| 城市客厅 | city-hub | 空间参观、节点营造、城市探索 |
| 户外聚会 | outdoor | 户外/公园/露台、烧烤/野餐/运动 |
| 节庆-派对 | party | 节日装饰、酒水、庆祝氛围 |
| 展览-市集 | exhibition | 展位/摊位、作品展示、市集 |
| 夏校-课程 | summer-school | 田野调研、课程教学、户外学习 |
| 餐会-聚餐 | dinner | 围桌就餐、餐厅/家中用餐 |

### Tier 2 · 地点

上海、清迈、大理、北京、杭州、深圳、广州、成都、重庆、西安、武汉、南京、厦门、天津、长沙、泉州、景德镇、香港、东京、京都、伦敦、巴黎、柏林、墨尔本、丹佛、北美、欧洲多地、东南亚多地、多地联动、全球多地、线上、区域待确认

### 非场景素材路由

| 素材类型 | 目标路径 |
|----------|----------|
| 海报 | `宣传物料/海报/{YYYY-MM}/` |
| Logo | `宣传物料/品牌/logo/` |
| 底图 | `宣传物料/品牌/底图/` |
| 二维码 | `宣传物料/品牌/二维码/` |
| 模板 | `宣传物料/品牌/模板/` |
| 截图 | `宣传物料/截图/` |
| 其他装饰图 | `宣传物料/其他/` |

## 路由：先看文件名

| 文件名特征 | 走哪条路径 |
|-----------|-----------|
| `inbox/wechat-image-import/*/_manifest.json` | **路径 W**：微信图片批次 → manifest 元数据 + 视觉识别/OCR → 用户确认 |
| 含中文描述标注 | **路径 A**：解析标注 → 提取场景类型+地点 → 匹配目标目录 |
| MD5 hash / DSC 编号 / Twitter ID 等无中文名 | **路径 B**：Ollama 视觉识别 → 场景优先分类 → 用户确认 |

---

## 路径 A：文件名标注

### 前置

用户在 `inbox/` 中放了图片，文件名包含中文描述标注。例如：
- `韩国文化之夜场景，位于十五楼，属于上海空间。.jpg`
- `六月五号未来社区论坛第一部分，米歇尔·波文在做分享.jpg`

### 1. 列出 inbox
```bash
ls -la "MEDIA_ROOT/inbox/"
```
排除 `README.md`、`.DS_Store` 和 `wechat-image-import/` 子目录。

### 2. 解析每张图的标注

从文件名中提取：

| 标注线索 | 解析为 |
|----------|--------|
| 日期（"六月五号"、"6月8日"） | 拍摄日期 YYYY-MM-DD |
| 活动类型线索（"工作坊"、"分享"、"论坛"、"观影"、"共居"） | Tier 1 场景类型 |
| 地点线索（"上海"、"清迈"、"大理"、"十五楼"） | Tier 2 地点 |
| 人名（"米歇尔·波文"、"悠洋"） | 人物标注（写入 index tags，不改变路由） |
| "海报"、"logo"、"底图"、"二维码" | 非场景 → 宣传物料路由 |
| "室内"、"户外"、"线上" | venue_scope 补充信息 |

### 3. 匹配目标目录

**场景照片**：`场景/{场景类型}/{地点}/`

**非场景素材**：`宣传物料/{子类}/`

**人物肖像**：`人物/`（嘉宾/常驻角色头像，独立维度）

### 4. 文件重命名

**场景照片**：`{YYYY-MM-DD}-{scene-slug-en}-{location-slug-en}-{seq}.{ext}`

示例：
- `2026-06-15-workshop-shanghai-01.jpg`
- `2026-05-10-talk-chiangmai-03.jpeg`
- `2026-04-20-coliving-dali-01.png`

**非场景素材**：`{YYYY-MM}-{type-en}-{desc-slug}-{seq}.{ext}`

示例：
- `2026-06-poster-mushanghai-01.jpg`
- `706-logo-high-res.svg`

### 5. 移动 + 更新索引 + 清空 inbox

---

## 路径 W：微信本地图片批次 → 视觉识别 + OCR + 确认

### 适用场景

`wechat-image-archive` 或本地扫描器已经把微信缓存图片复制到：

```text
inbox/wechat-image-import/<YYYYMMDD-HHMMSS>/
├── images/
├── _manifest.json
└── _scan-report.md
```

### Step 1: 读取 manifest

读取 `_manifest.json`，每张图至少使用：

- `staged_path`：当前 inbox 图片路径
- `original_path`：微信缓存原路径（只写进 provenance，不修改）
- `cache_family`：`MessageTemp/Image` 或 `xwechat_files/cache/Message/Thumb`
- `mtime_iso`：优先作为图片消息时间线索
- `width` / `height` / `size_bytes` / `sha256`

如果 manifest 里有 `source_label`，把它作为可选 `chat_name` 或批次说明写进待确认表。

### Step 2: 前置检查

```bash
command -v ollama
curl -s http://127.0.0.1:11434/api/tags
command -v tesseract
```

如果 Ollama 服务未启动或没有可用视觉模型，停止在"待启动视觉识别服务"状态；不要跳过识别直接归档。tesseract 不可用时可以继续，但要在确认表里标注"未跑 OCR"。

### Step 3: 场景优先视觉识别 + OCR 补充

对每张 `images/*` 调用 Ollama/MiniCPM-V，使用**场景优先识别 prompt**：

```
请用中文描述这张图片，按以下顺序逐项回答：

1. 内容类型：这是一张【场景照片】（有人在活动、聚会、事件中）
   还是【非场景素材】（海报、传单、Logo、二维码、截图、设计图）？

2. 如果是场景照片：
   a. 正在发生什么活动？从下面选最接近的一项：
      工作坊 / 讲座-分享 / 共居-日常 / 论坛-圆桌 / 放映-展映 /
      读书会-共读 / 黑客松 / 技术共学 / 城市客厅 / 户外聚会 /
      节庆-派对 / 展览-市集 / 夏校-课程 / 餐会-聚餐
   b. 室内还是户外？
   c. 大概多少人？（1-5人 / 6-15人 / 16-50人 / 50人以上）
   d. 有没有可见的地点线索？（路牌、地标、城市名、场地特征）

3. 如果是非场景素材：是哪一类？
   海报 / Logo / 底图 / 二维码 / 截图 / 模板 / 其他

4. 描述画面中出现的文字内容（中文和英文都包括）。
```

对疑似海报、截图、二维码、PPT 投影、横幅、聊天截图等含文字图片，补跑 `image-ocr` / tesseract。

合并字段：

```json
{
  "image": "images/...",
  "mtime_iso": "...",
  "visual_caption": "...",
  "ocr_text": "...",
  "scene_type": "工作坊 | 讲座-分享 | ... | null (if non-scene)",
  "asset_category": "scene | promotional | portrait | other",
  "indoor": true,
  "location": "上海 | 清迈 | ... | 区域待确认",
  "confidence": "高 | 中 | 低",
  "source": {
    "kind": "wechat-local-cache",
    "original_path": "...",
    "cache_family": "...",
    "chat_name": "...",
    "sha256": "..."
  }
}
```

### Step 4: 生成待确认分类表

把 manifest 元数据、视觉 caption、OCR 文本、用户给的线索合并判断：

- `asset_category`：scene / promotional / portrait / other
- `scene_type`：Tier 1 场景类型（14 类之一，非场景为 null）
- `location`：Tier 2 地点
- `confidence`：高 / 中 / 低
- `target_path`：确认后目标路径

**低置信度**保留在 `区域待确认` 或要求用户补充线索，不硬猜。

必须先打印确认表，用户确认后再入库。

### Step 5: 入库与清理

确认后一次性执行：

1. 复制到正式目录（场景照片 → `场景/{类型}/{地点}/`，非场景 → `宣传物料/{子类}/`）。
2. 为每张图追加 `media-index.json` 条目，新增字段：`scene_type`、`asset_category`、`indoor`、`location`。`source.kind` 固定为 `wechat-local-cache`。
3. 读回校验目标文件存在、index 新条目存在。
4. 确认复制和 index 更新都成功后，删除该批次 `inbox/wechat-image-import/<batch>/` 中已处理源文件；保留异常文件和说明。

---

## 路径 B：无标注文件 → 场景优先视觉识别

### 适用场景

文件名是 MD5 hash（`09afda9166c2c2c4962e0230dede3867.jpg`）、DSC 相机编号（`DSC07938.jpg`）、Twitter/X media ID（`G17hp47asAAaaix.jpeg`）等，没有人工标注。

### 前提

- `ollama` 已安装，`minicpm-v:8b` 模型已 pull
- 验证：`curl -s http://127.0.0.1:11434/api/tags | python3 -c "import json,sys; print([m['name'] for m in json.load(sys.stdin)['models']])"`
- 如果 Ollama 服务未启动，停止并提示用户启动；不要直接归档无标注图片。

### Step 1: 扫描 inbox + 获取元数据

```bash
for f in inbox/*.jpg inbox/*.jpeg inbox/*.png; do
    sips -g pixelWidth -g pixelHeight "$f"
    ls -lh "$f"
done
```

### Step 2: Ollama + MiniCPM-V 场景优先 caption

写临时 Python 脚本（不要改项目文件），对每张图调用 Ollama API：

```python
import base64, json, urllib.request
from pathlib import Path

INBOX = Path(".../inbox")
SCENE_PROMPT = (
    "请用中文描述这张图片，按以下顺序逐项回答：\n"
    "1. 内容类型：这是场景照片（有人在活动/聚会）还是非场景素材（海报/Logo/二维码/截图/设计图）？\n"
    "2. 如果是场景照片：什么活动？从下面选最接近的："
    "工作坊/讲座-分享/共居-日常/论坛-圆桌/放映-展映/读书会-共读/"
    "黑客松/技术共学/城市客厅/户外聚会/节庆-派对/展览-市集/夏校-课程/餐会-聚餐\n"
    "   室内还是户外？大概多少人？\n"
    "3. 如果是场景照片：有没有可见的地点线索？（路牌、地标、城市名）\n"
    "4. 如果是非场景素材：海报/Logo/底图/二维码/截图/模板/其他？\n"
    "5. 描述画面中出现的文字内容。"
)

for img in INBOX.glob("*.jpg"):
    payload = json.dumps({
        "model": "minicpm-v:8b",
        "prompt": SCENE_PROMPT,
        "images": [base64.b64encode(img.read_bytes()).decode("ascii")],
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:11434/api/generate",
        data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        caption = json.load(resp)["response"]
    # 写入 /tmp/inbox_captions.json
```

Prompt 应根据已知上下文定制。例如用户说了"这是清迈的文件"，就在 prompt 里加 `"The user says these are from Chiang Mai. Prioritize this location clue."`

### Step 3: 读 caption → 场景优先分类

基于 caption 内容，按二级系统推断：

**Tier 1 — 场景类型**（14 类，见上文分类表）

**Tier 2 — 地点**：从 caption 中的地点线索 + 文件时间戳 + 用户提示推断

**非场景路由**：`asset_category = "promotional"` → 按素材类型分到 `宣传物料/{子类}/`

**如果用户通过任何方式给了线索（"这是清迈的"、"DSC=2050"、"图片左上角有 二零五零"），必须优先采用用户线索，caption 只作补充。**

### Step 4: 用户确认

列出推断分类结果，让用户确认。确认表格式：

```
| 图片 | 场景/非场景 | 场景类型 | 地点 | 置信度 | 目标路径 |
|------|------------|---------|------|--------|---------|
| hash1.jpg | 场景 | 工作坊 | 上海 | 高 | 场景/工作坊/上海/ |
| hash2.jpg | 非场景 | — | — | 高 | 宣传物料/海报/2026-06/ |
```

**不要猜测超过 caption 和用户线索支持的范围。** 如果 caption 模糊，把不确定的点列出来让用户判断。

### Step 5: 批量执行

确认后，写一个完整的 Python 脚本（临时文件）一次完成：
1. 创建目标目录（`场景/{类型}/{地点}/` 或 `宣传物料/{子类}/`）
2. 重命名文件（`{YYYY-MM-DD}-{scene-slug}-{location-slug}-{seq}.{ext}`）
3. 复制到目标目录
4. 为每个文件生成 media-index.json 条目（含 `scene_type`, `asset_category`, `location`, `indoor`, `file`, `tags`, `dimensions`, `format`, `size_kb`, `date_ingested`, `reviewed`, `source`）
5. 追加到 media-index.json

```python
import json, shutil
from pathlib import Path

with open(INDEX_FILE) as f:
    index = json.load(f)

# 对每个分类好的文件：
#   shutil.copy2(src, dst)
#   生成 entry dict
#   index.append(entry)

with open(INDEX_FILE, "w") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
```

### Step 6: 清理 inbox

确认所有文件复制成功、index 更新无误后，删除本次处理的 inbox 源文件。

---

## 硬规则（所有路径通用）

- **场景优先**：先判断场景/非场景，再细分类型和地点
- **先 copy 后 delete**：不要直接 move，copy 成功 + index 更新后，再删除源文件
- **场景照片命名**：`{YYYY-MM-DD}-{scene-slug-en}-{location-slug-en}-{seq}.{ext}`，小写英文 + 连字符
- **非场景命名**：`{YYYY-MM}-{type-en}-{desc-slug}-{seq}.{ext}`
- **人物肖像**：路由到 `人物/`，独立维度，命名 `{人名}-{seq}.{ext}`
- 处理后必须更新 `media-index.json`
- 本批次 inbox 清空或只剩异常说明后才算完成
- **子目录也要处理**：`inbox/` 下的微信导入批次要一并处理并清理
- **同名处理**：如果目标文件已存在，自动追加 `-2`、`-3` 序号
- **清理后验证**：本批次目录 `find ... -type f ! -name '.DS_Store' | wc -l` 应为 0，除非保留了异常文件和说明
- **上海空间不再双存**：新结构下场景→地点已覆盖原上海空间双归属需求。上海空间的场景照直接归档到 `场景/{类型}/上海/`
- **项目关联**：通过 `media-index.json` 的 `project` 字段记录，不影响目录结构

## 场景类型参考

从现有 706-media 的 activity_type 统计中提炼的 14 类（按使用频率排序）：

技术共学（1003）、城市客厅（643）、共居-日常（616）、讲座-分享（428）、工作坊（184）、黑客松（138）、放映-展映（116）、论坛-圆桌（69）、读书会-共读（69）、夏校-课程（47）、驻留-招募（13）、展览-市集（1）、合影 → 合并入对应场景、混合 → 取主导场景

## 已跑通的案例

- 2026-06-14：清迈 29 张（5 hash + 12 DSC + 5 hash subdir + 5 Twitter + 1 风景 + 1 重复），Ollama caption → 用户分类 → 归档到 `在地706/清迈/` 和 `项目活动/2050/`
- 2026-06-14：上海节点 12 张 hash，Ollama caption → 按活动类型拆分 → 归档到 `项目活动/shanghai-node/`
- 2026-06-14：清迈 2026-06 二次整理，用户通过文件名标注纠正分类
- 2026-06-26：inbox 工作流重配 → 场景优先二级分类系统上线。统一 inbox，移除 `_inbox/`，场景→地点二级架构，宣传物料并行。
