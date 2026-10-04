# Capture fallbacks

## 文章发现

1. 使用会话内网页搜索，按公众号名称和月份检索 `site:mp.weixin.qq.com/s`。
2. 用户提供该公众号任意文章 URL，先核验账号，再围绕标题、账号名和月份补充网页搜索。
3. 用户直接提供文章 URL 列表。

三种都属于公开索引／用户提供的候选，覆盖状态不得高于 `public_web_index_partial`。

## 正文取得

1. `archive_article.py --url` 直接 HTTP 请求公开文章前端。
2. 用户使用 SingleFile 保存完整页面后，把本地 HTML 交给 `--input-html`；这是直接 HTTP 失败时的首选高保真入口。

默认不调用 Browser Use、OpenCLI、公众号后台或登录服务。

## 图片理解

1. 从最终 HTML 临时恢复 Base64 图片。
2. 使用当前 GPT 原生视觉理解图片，并结合上下配文。
3. 通过 annotations JSON 写回同一 HTML。
4. 删除临时恢复图片；HTML 仍然自包含。

## 必须停止

- 环境异常／需要验证
- 访问过于频繁
- 已删除／违规不可查看
- 页面不存在
- 权限或登录页

保存结构化失败原因。不要解验证码、轮换代理、模拟账号池或保存凭据。
