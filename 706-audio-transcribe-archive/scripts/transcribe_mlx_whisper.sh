#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <audio_path> <output_dir> <output_name> [initial_prompt]" >&2
  exit 2
fi

AUDIO_PATH="$1"
OUTPUT_DIR="$2"
OUTPUT_NAME="$3"
INITIAL_PROMPT="${4:-中文现场分享/访谈/问答。保留 706、muShanghai、The Mu、人名、项目名等专名。不要把静音或掌声转成重复语气词。}"

MODEL_DIR="${MODEL_DIR:-$HOME/.local/share/transcription-models/mlx-community/whisper-large-v3-turbo}"
TOOL_DIR="${TOOL_DIR:-$HOME/.local/share/transcription-tools/mlx-whisper}"

if [[ ! -f "$AUDIO_PATH" ]]; then
  echo "Audio not found: $AUDIO_PATH" >&2
  exit 1
fi

if [[ ! -d "$MODEL_DIR" ]]; then
  echo "Model directory not found: $MODEL_DIR" >&2
  exit 1
fi

if [[ ! -x "$TOOL_DIR/venv/bin/mlx_whisper" ]]; then
  echo "mlx_whisper not found: $TOOL_DIR/venv/bin/mlx_whisper" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

PATH="$TOOL_DIR/bin:$PATH" "$TOOL_DIR/venv/bin/mlx_whisper" "$AUDIO_PATH" \
  --model "$MODEL_DIR" \
  --language zh \
  --task transcribe \
  --output-format all \
  --output-dir "$OUTPUT_DIR" \
  --output-name "$OUTPUT_NAME" \
  --initial-prompt "$INITIAL_PROMPT" \
  --condition-on-previous-text False \
  --compression-ratio-threshold 1.6 \
  --logprob-threshold -0.8 \
  --no-speech-threshold 0.5 \
  --word-timestamps True \
  --hallucination-silence-threshold 2
