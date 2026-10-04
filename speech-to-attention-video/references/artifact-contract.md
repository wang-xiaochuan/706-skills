# Artifact Contract

## 最小 EDL JSON

```json
{
  "schema_version": "1.0",
  "publication_status": "internal-review-only",
  "source_media": "/absolute/path/source.mp4",
  "clips": [
    {
      "id": "c01-01",
      "source_in": 12.34,
      "source_out": 28.91,
      "speaker": "待确认",
      "text_raw": "原始口语",
      "text_clean": "清理后口语",
      "removed_tokens": [
        {"text": "嗯", "reason": "isolated_filler", "confidence": 0.98}
      ],
      "chapter": "主题章节",
      "segment_topic": "这一段的具体主题",
      "narrative_role": "hook",
      "attention_scores": {
        "proposition": 4,
        "specificity": 3,
        "tension": 5,
        "novelty": 4,
        "quotability": 4,
        "narrative_function": 5,
        "ethics_evidence": 5
      },
      "review_status": "human-review-needed"
    }
  ],
  "versions": [
    {
      "id": "attention-75s",
      "target_seconds": 75,
      "clip_ids": ["c01-01"],
      "ordering_note": "核心命题开场，随后给出证据和收束"
    }
  ]
}
```

时间统一使用秒数浮点值，以原始媒体时间轴为准。显示层可另外生成 `HH:MM:SS.mmm`，但不要用字符串替代机器计算字段。

## 最小 Manifest

```json
{
  "schema_version": "1.0",
  "status": "render-complete",
  "publication_status": "internal-review-only",
  "source_edl": "/absolute/path/edl.json",
  "outputs": [
    {
      "video": "/absolute/path/output.mp4",
      "subtitle": "/absolute/path/output.zh-CN.srt",
      "duration_seconds": 75.2,
      "width": 1280,
      "height": 720,
      "video_codec": "h264",
      "audio_codec": "aac",
      "full_decode_passed": true
    }
  ],
  "qa": {
    "visual_contact_sheet": "/absolute/path/contact-sheet.jpg",
    "subtitle_review": "pending-human-review",
    "publication_gate": "permission-reconfirmation-required"
  }
}
```

## 阶段目录建议

```text
speech-to-attention-analysis/
├── source-register.json
├── aligned-transcript.json
├── planning/
│   ├── candidate-quotes.json
│   └── edit-decision-list.json
├── stage3-audio-roughcut/
├── stage4-visual-system/
├── stage5-review-render/
├── stage6-distribution-pack/
└── scripts/
```

已有项目采用不同编号时不强行迁移；记录映射即可，避免为了形式整齐破坏可复现路径。
