# video-download · CHANGELOG

## 2026-08-14 · v1.0 创建（合并 B 站 + YouTube）

- 把本机已装的 yt-dlp（2026.03.17）+ ffmpeg（8.1.1）裸工具链封装为统一视频下载 skill
- 双平台差异总表：画质分层、Cookie 增益、字幕策略、风控特征（B 站 412 vs YouTube 429 节流）
- 与平台数据爬取明确分工：本 skill 只下载视频本体；元数据走项目里的 requests/API 脚本
- 采纳《大退出》bilibili 语料经验：先采元数据、按需下载本体，不整库拉视频
- 下游衔接：下载的音频/视频交给 `706-audio-transcribe-archive` 走 Whisper 转录
- 归档边界：视频本体入项目 media/ 或 706-media，语料层只存平台 ID 引用；不对外再分发

## 命名沿革

- 初稿以 `bilibili-video-download` 命名（仅 B 站）；同日按"统一视频下载方案"需求扩展为 `video-download`，旧目录废弃不保留
