---
name: image-ocr
description: "使用本地 Tesseract 对图片执行可重复的中文 OCR 或批量文字提取。用户要求本地 OCR、批量识别或可运行文字提取流程时使用；单张图片理解可直接使用模型视觉。"
---

# Image OCR — 图片中文文字提取

> 用本地 tesseract 从截图/图片中提取中文文字。当用户需要从微信截图、Notion 截图、PDF 截图等图片中提取中文内容时触发。

## 触发表达

- "提取这张图里的文字"
- "OCR 一下"
- "截图里写了什么"
- "图片转文字"
- 用户发送截图且需要识别其中中文内容时

## 依赖

- `tesseract` (Homebrew): `brew install tesseract`
- 中文语言包: `brew install tesseract-lang`（或单独 `tesseract --list-langs` 确认已有 `chi_sim`）

## 用法

### 单张图片

```
tesseract <图片路径> stdout -l chi_sim
```

### 批量处理

```bash
for f in /path/to/*.png; do
  echo "===== $(basename "$f") ====="
  tesseract "$f" stdout -l chi_sim 2>/dev/null
  echo ""
done
```

### 繁体中文

使用 `-l chi_tra` 替代 `-l chi_sim`。

## 已知局限

- 对竖排文字支持一般（可尝试 `-l chi_sim_vert`）
- 对低分辨率/模糊图片准确率下降
- 不保留原始排版格式，只输出纯文本
- 混合中英文场景下可能需要对输出做后处理

## 输出落点

- 临时性提取：直接在对话中展示 OCR 结果
- 归档需求：写入对应项目 `source/` 或 `706-knowledge/04-706语料/`
