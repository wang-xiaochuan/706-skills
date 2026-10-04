---
name: image-to-html
description: >
  将本地图片文件夹压缩并打包成 Base64 嵌入的 HTML 文件，便于发送给 Claude 处理图片。
  当用户提到「图片转 HTML」「把图片打包」「compress images」「图片 base64」
  「把这个文件夹的图片转成 HTML」「图片嵌入 HTML」「打包图片给 Claude」时触发。
  用户给出一个文件夹路径，skill 输出一个包含所有图片 base64 数据的 HTML 文件。
---

# image-to-html — 图片文件夹打包为 Base64 HTML

## 概述

将本地文件夹中的图片（支持 jpg/jpeg/png/gif/webp/bmp）压缩后以 Base64 嵌入 HTML，
输出单个 HTML 文件，可直接发给 Claude 进行图片内容分析。

支持递归子文件夹，输出文件默认放在 input 文件夹同级目录。

## 工作流

### Step 1: 确认参数

从用户输入中提取以下信息：

- **input_folder**（必填）：图片所在文件夹路径。如果用户没有提供，询问。
- **output**（可选）：输出 HTML 路径。默认为 `{input_folder同级}/{文件夹名}_compressed.html`
- **recursive**（可选）：是否递归子文件夹。默认 false，如果用户提到「子文件夹」「递归」则设为 true。
- **max_size**（可选）：图片最大尺寸，默认 `1024 1024`
- **quality**（可选）：JPEG 压缩质量 1-100，默认 80

### Step 2: 确认 Python 环境

运行以下命令检查依赖：

```bash
python3 -c "from PIL import Image; print('OK')"
```

如果报错 `ModuleNotFoundError`，先安装：

```bash
pip install Pillow
```

### Step 3: 确认脚本存在

脚本路径为：`$706_CLOUD/2026 skills/image_to_html.py`

用以下命令检查是否存在：

```bash
test -f "$706_CLOUD/2026 skills/image_to_html.py" && echo "exists"
```

如果不存在，告知用户脚本丢失，并提示从 skill 所在目录重新生成。

### Step 4: 运行脚本

根据参数拼接命令：

```bash
python3 "$706_CLOUD/2026 skills/image_to_html.py" \
  "{input_folder}" \
  [-o "{output}"] \
  [-r] \
  [--max-size WIDTH HEIGHT] \
  [--quality N]
```

**示例（基本）：**
```bash
python3 ".../image_to_html.py" "~/Desktop/screenshots"
```

**示例（递归 + 自定义输出）：**
```bash
python3 ".../image_to_html.py" "~/Desktop/screenshots" -r -o "~/Desktop/output.html"
```

### Step 5: 报告结果

脚本运行完毕后，输出中会显示：
- 处理了多少张图片
- 输出文件的完整路径

向用户报告这两条信息，并提示可以直接把 HTML 文件拖入 Claude 对话框使用。

## 注意事项

- 所有图片统一转为 JPEG 输出（含 PNG/WEBP），透明背景会变白色
- 图片按文件名字母顺序排列
- 递归模式下子文件夹路径会显示在图片标题中，便于定位
- HTML 文件体积 = 所有图片压缩后总大小 × 约 1.37（Base64 膨胀），注意不要一次打包太多图片
