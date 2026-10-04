---
name: 706-audio-transcribe-archive
description: >
  706 音频转录、多人说话人对齐与原始语料归档流程。把本地音频/播客/会议录音/访谈录音（m4a、mp3、wav 等）用本机正式保存的 MLX Whisper 模型转成中文时间戳转录稿，归档到 706 knowledge vault 的对应项目 `05-source/`，并提取后续回顾文、活动复盘、prewriting、narrative crafting 可用的详细素材笔记。用户提到「转录这个音频」「音频转文字」「播客转录」「会议录音整理」「访谈录音归档」「原始语料」「提取回顾文素材」「多人讲话」「谁说了什么」「说话人对齐」「按活动名单/metadata 对齐」「把录音放进 706 / muShanghai / 2050 项目」或给出本地音频路径时触发。
---

# 706 Audio Transcribe Archive

把本地音频变成可长期使用的 706 原始语料包：原音频、严格版时间戳转录、说话人归属稿、素材学习笔记、索引记录。

## 适用场景

- 用户给出本地音频路径，要“相对准确转录”。
- 用户说这是一段活动/播客/会议/访谈的“原始语料”，后续要写回顾文。
- 用户希望把转录结果归档进某个 706 项目目录，如 `by-project/mushanghai`、`by-project/2050`。
- 用户问本地 Whisper / MLX 转录模型怎么复用、如何避免缓存丢失。
- 音频有多人发言，用户需要根据活动名单、日程、截图、Luma 页面、现场笔记等 metadata 对齐“谁说了什么”。
- 用户后续纠正 speaker identity 时，需要更新归档文档，把纠错依据写入 README/notes，避免后续再误归属。

不适用：短语音随手听写、公开视频字幕抓取、无需归档的临时转写。

## 固定本地资产

优先使用已经正式保存的本地模型和工具，不依赖 cache：

```bash
MODEL_DIR="$HOME/.local/share/transcription-models/mlx-community/whisper-large-v3-turbo"
TOOL_DIR="$HOME/.local/share/transcription-tools/mlx-whisper"
```

- 模型约 1.5GB。
- 工具 venv 约 941MB，包含 `mlx_whisper` 和固定 ffmpeg。
- 如果路径不存在，先提醒用户需要安装/恢复模型；不要假装可以离线运行。

## 归档位置

在目标项目内新建：

```text
05-source/<slug>-<YYYY-MM-DD>/
├── README.md
├── audio/
│   └── <original-audio>
├── transcription-rerun-strict/
│   └── <raw whisper outputs>
└── notes/
    ├── <slug>-transcript-timestamped.md
    ├── <slug>-speaker-attributed.md
    └── project-study-notebook.md
```

若用户没有指定项目，按上下文判断；不确定时问一次。对 muShanghai，默认使用当前项目的 `05-source/`。

## 工作流

### 1. 检查音频

用 macOS 自带工具优先检查，避免 Homebrew ffmpeg 断链：

```bash
afinfo "/path/to/audio.m4a" | sed -n '1,80p'
```

记录：格式、声道、采样率、时长、文件大小。若需要转 wav，可用：

```bash
afconvert -f WAVE -d LEI16@16000 input.m4a /tmp/<slug>.wav
```

### 2. 复制原音频入库

把原音频复制到 `audio/`，不要只保留微信/下载目录引用。

### 3. 跑严格版转录

优先使用脚本：

```bash
$CODEX_HOME/skills/706-audio-transcribe-archive/scripts/transcribe_mlx_whisper.sh \
  "/path/to/audio.m4a" \
  "05-source/<slug>-<YYYY-MM-DD>/transcription-rerun-strict" \
  "<slug>-transcript"
```

脚本会使用正式模型目录、正式 venv、固定 ffmpeg，并输出 `all` 格式。

若手动执行，核心命令是：

```bash
PATH="$TOOL_DIR/bin:$PATH" "$TOOL_DIR/venv/bin/mlx_whisper" "/path/to/audio.m4a" \
  --model "$MODEL_DIR" \
  --language zh \
  --task transcribe \
  --output-format all \
  --output-dir "transcription-rerun-strict" \
  --output-name "<slug>-transcript" \
  --initial-prompt "中文现场分享/访谈/问答。保留 706、muShanghai、The Mu、人名、项目名等专名。不要把静音或掌声转成重复语气词。" \
  --condition-on-previous-text False \
  --compression-ratio-threshold 1.6 \
  --logprob-threshold -0.8 \
  --no-speech-threshold 0.5 \
  --word-timestamps True \
  --hallucination-silence-threshold 2
```

### 4. 质量检查

检查是否有 Whisper 幻觉：

- 大段重复“呃呃呃”“咱咱咱”“谢谢大家”。
- 明显长静音被转成重复语气词。
- 专名系统性错识别，如 `706` 被识别成“青六/金六/新六”。

如果质量差，重跑时：

- 关闭 `condition-on-previous-text`。
- 降低 `compression-ratio-threshold`。
- 使用更明确的 `initial-prompt`。
- 必要时先用 `afconvert` 转 16k mono wav。

### 5. 生成可读完整转录稿

从严格版 JSON 生成 `notes/<slug>-transcript-timestamped.md`。保留时间戳，开头写明：

- 来源音频。
- 转录模型。
- 质量说明。
- 自动归一化提示，例如 `706`、`关怀小组` 等。

### 6. 提取素材学习笔记

如果用户说要写回顾文、复盘、长文或“原始语料”，同时触发/参考 `prewriting` skill，输出 `notes/project-study-notebook.md`。至少包含：

- 一句话材料定位。
- 材料清单与缺口。
- 人物档案。
- 时间线。
- 可引用表达（标时间戳，提醒需回听复核）。
- 组织/流程/制度细节。
- 活动案例。
- 情感地形。
- 物与空间。
- 数字与数据。
- 叙事富矿。
- 对目标项目的可用启发。
- 待复核与待补材料。

### 7. 多人说话人对齐

当音频包含多人讲话时，额外输出 `notes/<slug>-speaker-attributed.md`。不要假装 Whisper 能自动识别人物；用上下文推断和外部 metadata 对齐，并明确置信度。

对齐顺序：

1. 先依据音频内部线索：自我介绍、主持串场、互相称呼、问答结构、主题连续性、时长。
2. 再吸收外部 metadata：活动名单截图、日程、报名页、Luma/Notion 页面、现场笔记、用户补充纠错。
3. 只在证据足够时给出姓名；不确定时使用功能标签，如 `主持`、`嘉宾 A`、`观众提问`。
4. 对每个 speaker block 标注置信度：`高`、`中`、`低`。
5. 如果名单里的人没有在音频中形成可靠可切分发言，写为“名单存在，但当前音频不可可靠切出”，不要硬分配。
6. 用户后续纠正时，以用户核实信息为准，更新所有相关文件中的 speaker map、标题、素材笔记和 README 质量说明。

`speaker-attributed.md` 建议结构：

```text
# <title> 说话人归属转译稿（上下文推断版）

## 整理说明
- 未做声纹 diarization。
- 使用了哪些 metadata。
- 哪些归属来自用户后续人工核实。

## 说话人地图
- `00:00 - 00:10` Speaker（置信度：高/中/低）：说明。

## 逐段转译
### [00:00 - 00:10] Speaker（置信度：高/中/低）
...
```

### 8. 更新索引

更新目标项目的 `INDEX.md` 或对应 README，把新语料目录登记进去。不要移动无关文件。

## 清理规则

- 可清理：`~/.cache/huggingface`、`~/.cache/uv`，前提是正式模型和工具目录已存在。
- 不清理：`~/.local/share/transcription-models/...`、`~/.local/share/transcription-tools/...`，除非用户明确要求。
- 不误删：项目内 `notes/*transcript-timestamped.md` 是完整可读转录稿，`notes/project-study-notebook.md` 是写作素材，不属于缓存。

## 交付时说明

最终回复要告诉用户：

- 原音频、完整转录稿、素材笔记分别在哪里。
- 如果有多人发言，说明说话人归属稿在哪里，以及哪些姓名来自 metadata 或后续人工核实。
- 转录质量是否有风险，哪些专名/数字需要回听复核。
- 是否清理了缓存，以及保留了哪些正式本地资产。
