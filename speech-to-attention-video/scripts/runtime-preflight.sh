#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
failures=0

for command_name in ffmpeg ffprobe node; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'required:%s:ok:%s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf 'required:%s:missing\n' "$command_name" >&2
    failures=$((failures + 1))
  fi
done

for command_name in magick whisper qwen; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf 'optional:%s:ok:%s\n' "$command_name" "$(command -v "$command_name")"
  else
    printf 'optional:%s:missing\n' "$command_name"
  fi
done

ffmpeg_filters="$(ffmpeg -hide_banner -filters 2>/dev/null || true)"
ffmpeg_encoders="$(ffmpeg -hide_banner -encoders 2>/dev/null || true)"
for filter_name in overlay subtitles drawtext; do
  if printf '%s\n' "$ffmpeg_filters" | rg -q "[[:space:]]${filter_name}[[:space:]]"; then
    printf 'ffmpeg-filter:%s:available\n' "$filter_name"
  else
    printf 'ffmpeg-filter:%s:unavailable\n' "$filter_name"
  fi
done
if printf '%s\n' "$ffmpeg_encoders" | rg -q '[[:space:]]qtrle[[:space:]]'; then
  printf 'ffmpeg-encoder:qtrle:available\n'
else
  printf 'ffmpeg-encoder:qtrle:unavailable\n'
fi

if command -v magick >/dev/null 2>&1 \
  && printf '%s\n' "$ffmpeg_filters" | rg -q '[[:space:]]overlay[[:space:]]' \
  && printf '%s\n' "$ffmpeg_encoders" | rg -q '[[:space:]]qtrle[[:space:]]'; then
  printf 'subtitle-renderer:png-qtrle-overlay:available\n'
elif printf '%s\n' "$ffmpeg_filters" | rg -q '[[:space:]]subtitles[[:space:]]'; then
  printf 'subtitle-renderer:ffmpeg-subtitles:available\n'
else
  printf 'subtitle-renderer:unavailable\n'
fi

if [[ -f "$skill_dir/SKILL.md" ]] && rg -q '^name: speech-to-attention-video$' "$skill_dir/SKILL.md"; then
  printf 'skill-metadata:ok:%s\n' "$skill_dir/SKILL.md"
else
  printf 'skill-metadata:invalid:%s\n' "$skill_dir/SKILL.md" >&2
  failures=$((failures + 1))
fi

for reference_name in artifact-contract.md employee-contract.md multicam-distribution.md subtitle-rendering.md; do
  if [[ -f "$skill_dir/references/$reference_name" ]]; then
    printf 'reference:ok:%s\n' "$reference_name"
  else
    printf 'reference:missing:%s\n' "$reference_name" >&2
    failures=$((failures + 1))
  fi
done

if [[ "$failures" -eq 0 ]]; then
  printf 'runtime-preflight:pass\n'
else
  printf 'runtime-preflight:fail:%s\n' "$failures" >&2
fi

exit "$failures"
