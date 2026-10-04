# Changelog

## 2026-08-08 · 视觉模型升级 llava:7b → MiniCPM-V 8B

- 默认视觉模型从 `llava:7b` (2023) 切换到 `minicpm-v:8b`（MiniCPM-V 4.5 8B）。
- MiniCPM-V 4.5 中文 OCR 评分满分，超越 GPT-4o-latest 和 Gemini 2.5。
- 所有场景识别 prompt 从英文切换为中文（MiniCPM-V 中文本地优化，中文 prompt 效果更好）。
- 路径 W 和路径 B 的 Ollama API 调用示例同步更新。
- 关联技能 wechat-image-archive 同步更新引用。

## 2026-06-26 · Inbox 工作流重配

- 场景优先二级分类系统上线：Tier 1 场景类型（14 类）→ Tier 2 地点 + 宣传物料并行文件夹。
- 统一 inbox 为 `706-media/inbox/`，移除所有 `_inbox/` 和 `LEGACY_INBOX` 引用。
- 路径 A/B/W 全部更新目标目录为新结构。
- 新增场景优先 Ollama visual prompt（区分场景/非场景、14 类活动类型、室内/户外、地点线索）。
- 文件命名规范更新：场景 `{YYYY-MM-DD}-{scene-slug}-{location-slug}-{seq}.{ext}`，非场景 `{YYYY-MM}-{type}-{desc}-{seq}.{ext}`。
- 上海空间双归属规则移除：新结构下场景→地点已覆盖原需求。
- 路径 W（微信批次）和路径 B（无标注散图）的 OCR 补充逻辑保留。
- 修复 `wechat-publish` / `wechat-publish-2.0` 中指向旧 `2026 dev/706-media/`（706 外部）的硬编码路径。

## 2026-06-17

- Treat `706/706-media/inbox/` as the primary new-media intake path and keep `_inbox/` for legacy or unclear materials.
- Add the WeChat image import batch workflow for `inbox/wechat-image-import/*/_manifest.json`.
- Require Ollama/LLaVA captions for unlabelled image batches and use tesseract OCR only as supporting evidence.
- Preserve `wechat-local-cache` provenance fields for future `media-index.json` entries.
- Keep user confirmation as the gate before moving any staged media into the formal archive.

## Known limits

- The skill describes the ingest workflow; the actual batch execution still depends on an agent writing/running the final per-batch copy/index script after user confirmation.
- Ollama must be running locally before the visual caption stage can proceed.
