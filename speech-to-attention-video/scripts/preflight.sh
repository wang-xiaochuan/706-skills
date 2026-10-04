#!/usr/bin/env bash
set -u

media_path="${1:-}"
transcript_path="${2:-}"
failed=0

if [[ -z "$media_path" ]]; then
  echo "usage: bash scripts/preflight.sh /absolute/path/media [transcript]" >&2
  exit 2
fi

for command_name in ffmpeg ffprobe node; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'required:%s:ok:%s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf 'required:%s:missing\n' "$command_name" >&2
    failed=1
  fi
done

for command_name in magick whisper; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'optional:%s:ok:%s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf 'optional:%s:missing\n' "$command_name"
  fi
done

if [[ -f "$media_path" ]]; then
  printf 'media:ok:%s\n' "$media_path"
  ffprobe -v error \
    -show_entries 'format=duration,size:stream=index,codec_type,codec_name,width,height,sample_rate,channels' \
    -of json "$media_path"
else
  printf 'media:missing:%s\n' "$media_path" >&2
  failed=1
fi

if [[ -n "$transcript_path" ]]; then
  if [[ -f "$transcript_path" ]]; then
    printf 'transcript:ok:%s\n' "$transcript_path"
  else
    printf 'transcript:missing:%s\n' "$transcript_path" >&2
    failed=1
  fi
else
  printf 'transcript:not-provided\n'
fi

exit "$failed"
