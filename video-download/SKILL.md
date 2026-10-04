---
name: video-download
description: >
  统一视频下载与本地归档（B 站 + YouTube）。基于本机已装的 yt-dlp + ffmpeg（brew，免费开源工具），
  支持匿名直下、浏览器 Cookie 登录画质、批量清单下载、断点续跑、字幕抓取、风控应对与归档边界。
  当用户提到「下载视频」「下这个视频」「下载 B 站视频」「下载 YouTube 视频」「下这个 BV / 这个 YouTube 链接」
  「把这条视频存下来」「视频本体下载」「video download」「帮我存一下这个视频」，
  或给出 B 站视频链接 / BV 号 / YouTube URL 要求下载时触发。
  与平台数据爬取（B 站搜索元数据、YouTube API 元数据）是两套东西：数据侧走项目里的 requests/API 脚本，
  本 skill 只负责把视频文件本体落盘。
---

# Video Download

统一处理 B 站与 YouTube 的视频本体下载。工具链不打包进本目录——yt-dlp 与 ffmpeg 已在 brew 安装（`/opt/homebrew/bin/`），本 skill 定义方法、参数与边界。

## 前置检查

```bash
yt-dlp --version   # 本机 2026.03.17，过期时 brew upgrade yt-dlp
ffmpeg -version    # dash 流音视频合并必需，缺失时 brew install ffmpeg
```

两者缺一则先装好再继续，不要试图用 requests 拼视频流。

## 平台差异总表

| 维度 | B 站 | YouTube |
|------|------|---------|
| 匿名可下画质 | 360P / 480P | 1080P 及以下（多数视频） |
| 登录 Cookie 增益 | 720P / 1080P（普通账号）；1080P 高码率 / 4K（大会员） | 年龄限制视频解锁；缓解节流 |
| 专享内容 | 大会员专享需对应 Cookie | 会员/租购内容需对应 Cookie |
| 字幕 | 需 --write-subs 且 UP 上传了字幕 | 自动字幕可用 `--write-auto-subs`（ASR 生成） |
| 风控特征 | 连续请求 412 限流 | 无 Cookie 批量请求被节流（429 变慢） |
| 地区限制 | 少 | 部分视频有地区限制，需要代理 |

Cookie 统一用浏览器现有登录态（`--cookies-from-browser safari` 或 `chrome`），不要导出 Cookie 文件落盘进项目。

## 命令范式

### B 站

```bash
yt-dlp -f "bv*+ba/b" --cookies-from-browser safari \
  -o "%(title)s [%(id)s].%(ext)s" \
  "https://www.bilibili.com/video/BVxxxxxxxx"
```

- `bv*+ba/b`：最佳视频流+最佳音频流合并（ffmpeg），失败回退单文件
- 匿名下载去掉 `--cookies-from-browser` 一行
- 只要音频（讲座/播客转写用）：`-f "ba/b" -x --audio-format m4a`
- 字幕（UP 已上传时）：加 `--write-subs --sub-langs "zh-Hans,zh" --skip-download`

### YouTube

```bash
yt-dlp -f "bv*+ba/b" --cookies-from-browser safari \
  -o "%(title)s [%(id)s].%(ext)s" \
  "https://www.youtube.com/watch?v=xxxxxxxxxxx"
```

- 1080P 以内通常匿名即可；年龄限制/批量场景加 Cookie
- 自动字幕（ASR，转写用）：`--write-auto-subs --sub-langs "zh-Hans,en" --skip-download`
- 字幕+音频一起（转录管线输入）：`-f "ba/b" -x --audio-format m4a --write-auto-subs --sub-langs "zh-Hans,en"`

### 批量下载（两平台通用）

从 URL 清单文件（每行一个视频链接；B 站可用 BV 号清单，数据采集脚本产出）：

```bash
yt-dlp -f "bv*+ba/b" --cookies-from-browser safari \
  --download-archive downloaded.txt \
  -o "%(title)s [%(id)s].%(ext)s" \
  --batch-file url-list.txt
```

- `--download-archive downloaded.txt`：断点续跑不重复下载
- 批量间隔 `--sleep-requests 3 --sleep-interval 5`：B 站防 412、YouTube 缓节流

## 风控与合规

1. **B 站 412 限流**：连续请求必然触发。批量务必加 sleep 参数；被 412 后用浏览器 Cookie 重试（数据侧 buvid3 缓解经验同样适用）
2. **YouTube 节流**：无 Cookie 连续请求会越来越慢（429 降速），批量时带 Cookie 或加大间隔
3. **失败重试**：`--retries 5 --fragment-retries 5`
4. **版权边界**：下载仅限个人研究/学习/存档用途；**不对外再分发**，不把视频文件放入对外发布的资料包。B 站/YouTube 条款均禁止未经许可的下载——这是工具能做什么与应该做什么的分界

## 归档路径

| 场景 | 路径 | 说明 |
|------|------|------|
| 研究项目素材 | `706-production-research/{project}/media/` | 视频本体在本地，不在语料库正文 |
| 媒体素材 | `706-media/inbox/` 待 media-ingest 分流 | 按媒体库惯例 |
| 语料项目引用 | 只记平台 ID（BV / video id）+ 元数据 + 本地路径指针 | 语料 CSV 里不放视频文件 |

《大退出》bilibili 语料的经验同样适用于 YouTube：**先采元数据，按需下载本体**，不要整库拉视频。

## 与上下游的衔接

工作流顺序：

1. **数据侧**（requests/API 脚本，非本 skill）：B 站关键词搜索 → `bilibili-great-exit-master-final.csv` 这类清单；YouTube 侧已有 `collect_youtube_samples.py` 与 `youtube-search-sample-*.csv` 实践
2. **本体侧**（本 skill）：从清单提取链接 → `--batch-file` 批量下载 → 本地归档
3. **转录侧**（`706-audio-transcribe-archive`）：下载的音频/视频 → MLX Whisper 转写 + 说话人对齐 + 入库

本 skill 不重新实现平台元数据采集；已有脚本继续留在项目 source/ 原位。
