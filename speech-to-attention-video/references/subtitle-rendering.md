# 多语言字幕渲染

仅在需要烧录字幕、标题或姓名条时读取。

## 先检测，后选路

运行 `scripts/runtime-preflight.sh`，根据实际输出选择：

1. `subtitles` 可用：可直接烧录 SRT/ASS，但仍先检查字体和 10–15 秒样片。
2. `subtitles` 不可用，且 `overlay`、`qtrle`、ImageMagick、Node.js 可用：使用 `scripts/render-subtitle-overlay.mjs`。
3. 两条路径都不可用：停止渲染并准确报告缺失能力，不反复尝试同一命令。

`drawtext`、`subtitles` 缺失通常是 FFmpeg 编译选项差异，不是中文、韩文或日文字体导致。用 `ffmpeg -filters` 证明能力，不能凭之前的机器或项目经验假设。

## 稳定路径：透明 PNG + qtrle + overlay

1. 保留独立 UTF-8 SRT。
2. 用 ImageMagick 和明确的字体文件把每条 cue 渲染为透明 PNG。
3. 用 concat 时间线生成 qtrle/argb 透明字幕轨。
4. 用 FFmpeg `overlay` 叠加；默认保持原视频宽高，不增加黑边、不缩放、不改变画幅。
5. 抽查明暗背景、最长字幕、第一条和最后一条，再渲染全片。

示例：

```bash
node scripts/render-subtitle-overlay.mjs \
  --input "/absolute/path/input.mp4" \
  --srt "/absolute/path/subtitles.ko.srt" \
  --output "/absolute/path/preview.mp4" \
  --font "/absolute/path/Korean-Bold.otf" \
  --single-line \
  --overlay-height 44 \
  --bottom-margin 10 \
  --limit-seconds 15
```

样片通过后去掉 `--limit-seconds` 生成全片。脚本输出透明 PNG、qtrle 字幕轨和最终 MP4，便于复现和排错。

## 已有烧录字幕时

- 先抽帧确认原画面实际语言和位置；容器没有字幕流不等于画面没有烧录字幕。
- 新语言默认直接叠加到现有字幕附近的安全区，不因增加一种语言自动加黑色字幕带。
- 空间不足时先缩短翻译、改单行和自适应字号；只有用户明确同意时才扩画布、加底栏或覆盖原字幕。
- 用 `--single-line`、`--overlay-height` 和 `--bottom-margin` 控制第三行字幕。最长 cue 必须进入视觉抽查。

## 字体

- 用 `fc-match :lang=ko`、`:lang=ja`、`:lang=zh` 或系统字体目录找到实际字体文件。
- 生成前用 ImageMagick 渲染一条目标语言样字；方框、缺字或空白时换字体。
- 白字使用粗体与稳定暗阴影/细描边，禁止仅凭一张暗底截图判定可读性。

## 防卡住规则

- 首次只渲染 10–15 秒；不要直接启动长片。
- 同一错误最多尝试一次修正；第二次仍失败就检查 `ffmpeg -filters`、`ffmpeg -encoders`、字体文件和透明 PNG，而不是继续换引号。
- 命令运行超过 60 秒时给用户状态更新；没有输出时检查进程和日志。
- 启动/字幕渲染阶段不委派子 Agent，避免简单任务扩展为代理循环。
