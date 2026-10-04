# Changelog

## 2026-06-17 follow-up

- Broadened the skill from a media-only workflow into a general WeChat context sync port.
- Added the group-summary route for summarizing a group from natural-language scope hints such as "最近一百条", "昨天到今天早上", "接着上次同步", or topic-focused ranges.
- Reframed scan scope as natural-language `scope_hint` first, with internal normalized scope recorded only for execution traceability.
- Added checkpoint guidance so repeat scans can continue from the last confirmed sync without skipping failed runs.
- Added the relationship-maintenance route: summarize a specified chat, extract commitments and follow-ups, and update customer/partner relationship documents.
- Added Claude CLI compatibility guidance: when WeChat MCP is unavailable, use a local transcript file or pasted chat text instead of blocking.
- Kept the media import route as one downstream use case of the broader context-sync entrypoint.

## 2026-06-17

- Reworked the workflow around a low-risk v1: optional chat context, local WeChat cache scanning, staged import into `706-media/inbox/`, then `media-ingest` classification and confirmation.
- Added the active media-root policy: use `706/706-media`, not the older sibling `706-media` vault.
- Added support for the new scanner script under `infra/scripts/media/scan_wechat_image_folders.py`.
- Documented that v1 does not modify `wechat-mcp` and does not parse `Bubble/*.dat`.

## Known limits

- Newer WeChat full-size media may still be unavailable unless WeChat has downloaded it locally; v1 stages directly readable image files only.
- Group context remains optional and depends on the existing `wechat-mcp` desktop automation staying connected.
