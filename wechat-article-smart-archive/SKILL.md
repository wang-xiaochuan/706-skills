---
name: wechat-article-smart-archive
description: 按微信公众号名称或关键词与时间范围，通过网页搜索发现公开文章、直接抓取 mp.weixin.qq.com 前端并归档；每篇生成图片 Base64 内嵌、可离线分享、可按图片上下文/OCR/视觉描述查询的自包含 HTML。用户提到“下载某公众号一段时间的文章”“批量归档公众号”“抓公开公众号推文”“把微信文章存成单文件 HTML”“查找归档公众号里的某张图”时使用；也支持直接提供文章 URL 或本地 HTML。默认不使用 Browser Use、Chrome Bridge、OpenCLI、公众号后台、Tesseract 或本地视觉模型。
---

# WeChat Article Smart Archive

把公开公众号文章归档为一篇一个、自包含、可检索的 HTML。默认链路是：纯 HTTP 搜狗微信搜索 → 解析公开文章 URL → HTTP 抓文章前端 → Base64 内嵌图片 → 当前 GPT 原生视觉理解 → 写回 HTML。

## 边界

- 只读取公开文章前端，不登录公众号后台，不索取 Cookie 或 token。
- 不使用 Browser Use、Chrome Bridge 或 OpenCLI 作为默认发现方式。
- 搜狗微信／网页搜索索引可能漏文。覆盖状态始终写为 `public_web_index_partial`；未命中不能解释为未发布。
- 候选 URL 必须再次抓取前端，并核验公众号名称和发布时间。无法核验则拒绝归档。
- 遇到验证码、环境异常、访问频繁、删除或权限页时失败关闭，不绕过验证。
- 页面没有互动数据时保存 `null + status`，不写成 0。
- 当前模型能看图时使用原生视觉能力；不要启动 Tesseract、Ollama 或 LLaVA，除非用户另行指定。

## 1. 规范化输入

提取：

- `account`：公众号名称或用户给的精确关键词
- `start`、`end`：转换为 `YYYY-MM-DD`
- `output_dir`：优先使用用户指定目录；否则使用当前项目明确目录或说明采用的下载目录

## 2. 用纯 HTTP 按月份发现文章

直接运行发现脚本，不启动浏览器。脚本把日期范围拆成月份，使用同一个 HTTP Session 请求搜狗微信搜索页、保留公开 Cookie、解析结果页和分段跳转脚本：

```bash
python3 scripts/discover_articles.py \
  --account '<公众号名称>' \
  --start '2026-06-01' \
  --end '2026-07-30' \
  --output /tmp/wechat-manifest.json
```

只保留搜索结果中来源公众号名称精确一致、搜索时间位于范围内的候选。默认每月读取三页；不要高并发或绕过反爬验证。

如果纯 HTTP 搜狗搜索没有候选，可使用当前会话的网页搜索工具补充检索 `site:mp.weixin.qq.com/s`，但仍不启动浏览器。把补充 URL 写入临时候选文件：

```json
{
  "queries": ["实际执行的查询"],
  "results": [{"url": "https://mp.weixin.qq.com/s/...", "search_title": "..."}]
}
```

然后在发现命令中增加 `--candidates /tmp/wechat-candidates.json`。搜索页面只提供候选，不能证明账号、日期或完整覆盖。

### 只知道公众号名称：发现并添加到 WeWe RSS

用户只给出一批公众号名称、并且本机已有用户授权登录的 WeWe RSS 时，可以先找每个账号的一篇公开“种子文章”，交给 WeWe 识别公众号身份。706 本机的永久服务位于 `706-skills/infra/services/wewe-rss/`，默认只监听 `127.0.0.1:4000`；先运行它的 `bin/status`，停止时运行 `bin/start`。本机回环服务不要求授权码，远程 WeWe 服务仍必须显式提供授权码。

默认只核验，不添加：

```bash
python3 scripts/wewe_feed_manager.py \
  '706东京' '706杭州' '706柏林' \
  --output /tmp/wewe-feed-discovery.json
```

网页搜索工具找到候选链接时，写成：

```json
{"results":[
  {"account":"706杭州","url":"https://mp.weixin.qq.com/s/..."},
  {"account":"706柏林","url":"https://mp.weixin.qq.com/s/..."}
]}
```

再执行 `--candidates <文件> --add`。脚本仅接受 `mp.weixin.qq.com/s/<永久文章标识>` 形式的稳定分享链接，并且只在 WeWe 返回的真实公众号名称与查询名称精确一致时添加；搜狗产生的 `s?src=11&signature=...` 短时链接记录为 `candidate_unusable`，不能误报成公众号不存在。同名、转载或只存在城市节点而没有独立公众号时不添加。结果状态包括 `added`、`already_added`、`verified`、`candidate_unusable`、`not_found`、`discovery_failed`。这条链路依赖用户已经授权的本地 WeWe 会话及其第三方中继；不得读取、打印或写入账号 token。非回环地址通过 `WEWE_AUTH_CODE` 或 `--auth-code` 提供授权码。

## 3. 直接抓取前端并核验候选

```bash
python3 scripts/discover_articles.py \
  --account '<公众号名称>' \
  --start '2026-06-01' \
  --end '2026-07-30' \
  --output /tmp/wechat-manifest.json
```

脚本解析出 `mp.weixin.qq.com/s...` 后，继续用普通 HTTP 获取文章前端并检查：

- 页面不是限制页；
- 存在公众号正文；
- 页面公众号名称与输入精确一致；
- 页面发布时间位于范围内。

`account_mismatch`、`date_unverified`、`outside_date_range` 和抓取失败都留在 `rejected`，不进入下载批次。

## 4. 下载并生成单篇 HTML

```bash
python3 scripts/archive_range.py \
  --manifest /tmp/wechat-manifest.json \
  --output-dir '<目标目录>'
```

输出：

- 每篇文章一个自包含 HTML；
- 正文图片为 Base64 data URL；
- 图片上下文和初步日期／地点进入内嵌 JSON；
- `_collection.html` 保存批次入口、公开索引覆盖状态与失败清单。

单篇 URL 可直接执行：

```bash
python3 scripts/archive_article.py --url '<文章 URL>' --output '<文章.html>'
```

### 用户使用 SingleFile 时

把 SingleFile 保存出的完整单文件 HTML 当作高保真输入，不再联网抓正文，也不要求 agent 控制浏览器：

```bash
python3 scripts/archive_article.py \
  --input-html '<SingleFile 保存的文章.html>' \
  --source-url '<原始公众号文章 URL>' \
  --output '<智能归档文章.html>'
```

SingleFile 已经内嵌的 CSS、图片和字体可作为原始捕获证据；归档脚本仍提取公众号正文、生成统一图片 ID、哈希和机器索引。不要把 SingleFile 当作“按公众号名称发现历史文章”的工具。

## 5. 用 GPT 原生视觉理解图片

Base64 文本本身不直接作为视觉输入。先把内嵌图片恢复到临时目录：

```bash
python3 scripts/extract_images_for_gpt.py '<归档目录>' \
  --output-dir /tmp/wechat-gpt-images \
  --manifest /tmp/wechat-gpt-image-tasks.json
```

读取 task manifest。使用当前 GPT 的图片理解工具查看每张本地图片，并结合 `previous_paragraph`、`original_caption`、`next_paragraph` 生成：

- `visual_description`：只描述可见内容，不猜身份；
- `ocr_text`：尽可能忠实抄录可见文字；
- `event_date`、`location`、`entities`：只有图片或上下文有证据时填写；
- 无法判断时使用 `null` 或空数组。

写成临时 annotations JSON：

```json
{"annotations":[{"html":"/abs/article.html","image_id":"img-001","visual_description":"...","ocr_text":"...","event_date":null,"location":null,"entities":[]}]}
```

图片量很大、并且当前环境已由用户提供 OpenAI API 凭据时，可以运行可续传批处理。密钥只从环境变量读取，不写入 manifest、checkpoint 或最终 HTML：

```bash
OPENAI_API_KEY='<当前会话密钥>' python3 scripts/run_gpt_vision_annotations.py \
  --manifest /tmp/wechat-gpt-image-tasks.json \
  --checkpoint /tmp/wechat-gpt-checkpoint.jsonl \
  --annotations /tmp/wechat-gpt-annotations.json
```

写回原 HTML：

```bash
python3 scripts/apply_gpt_annotations.py --annotations /tmp/wechat-gpt-annotations.json
```

完成后可删除临时图片和 annotations；最终文章不依赖这些文件。

## 6. 验证与查询

```bash
python3 scripts/validate_archive.py '<目标目录>'

python3 scripts/query_archive.py '<目标目录>' '706 东京' \
  --date 2026-07-02 \
  --extract-dir /tmp/wechat-image-results
```

验证每张成功图片都是 Base64、SHA-256 一致、没有远程 `<img src>`，正文根节点没有保留微信预渲染的隐藏样式，限制页未被保存为文章。

旧归档如果因 `visibility:hidden` 或 `opacity:0` 显示空白，原地解除正文隐藏后再次验证：

```bash
python3 scripts/repair_archive_visibility.py '<目标目录>'
python3 scripts/validate_archive.py '<目标目录>'
```

## 回报

必须告诉用户：

1. 实际搜狗月份查询／补充网页查询和覆盖状态 `public_web_index_partial`；
2. 搜索候选、前端核验通过、归档成功、失败各多少篇；
3. 输出目录和 `_collection.html`；
4. GPT 图片标注数量；
5. 失败原因，且不把失败说成“没有文章”。

详细字段见 `references/schema.md`；失败与降级规则见 `references/capture-fallbacks.md`。
