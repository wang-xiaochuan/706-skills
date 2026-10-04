# Embedded schema

每篇 HTML 含：

```html
<script type="application/json" id="wechat-article-index">…</script>
```

顶层字段：

- `schema_version`
- `article`: title、account_name、author、published_at、source_url
- `images`: 图片级索引
- `image_failures`: 未能内嵌的图片与原因
- `engagement_snapshots`: 指标快照；必须有 source、status、observed_at
- `comments`: 已取得评论；没有则空数组
- `comments_status`
- `capture`: 抓取模式、时间、图片数量

图片字段：

- `image_id`、`position`、`mime_type`、`sha256`
- `original_url`、`base64_image_ref`
- `previous_paragraph`、`original_caption`、`next_paragraph`
- `ocr_text`、`ocr_status`：默认先为 `pending_gpt`，GPT 看图写回后为 `captured_by_gpt` 或 `empty`
- `visual_description`、`vision_status`：默认先为 `pending_gpt`，GPT 看图写回后为 `captured_by_gpt` 或 `empty`
- `event_date`、`location`、`entities`
- `evidence`: 日期和地点来自上下文、OCR 还是视觉描述

缺失值规则：

- 不知道：`null`
- 未请求：`not_requested`
- 页面不可见：`not_visible`
- 等待 GPT 图片理解：`pending_gpt`
- GPT 原生视觉完成：`captured_by_gpt`
- 成功：`captured` 或 `captured_partial`

不要用空字符串或 0 代替未知互动数据。
