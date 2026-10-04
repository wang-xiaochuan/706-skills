# 图片上传与嵌入

## 为什么需要图床

Notion 的 markdown 格式支持 `![alt](url)` 插入图片，但需要公开可访问的 URL。用户的本地图片需要先上传到图床，拿到 URL 后才能嵌入。

## 图床优先级

按可靠性排序：

### 1. freeimage.host（首选）

API 上传，免费，无需注册，稳定。

```bash
curl -X POST "https://freeimage.host/api/1/upload" \
  -F "key=6d207e02198a847aa98d0a2a901485a5" \
  -F "source=@/path/to/image.jpg" \
  -F "format=json"
```

返回值中 `response.image.url` 就是可用的公开 URL。

也可以用脚本 `scripts/upload_image.py`：
```bash
python scripts/upload_image.py /path/to/image.jpg
```

### 2. catbox.moe（备选）

匿名上传，简单，但偶尔会暂停匿名上传功能。

```bash
curl -F "reqtype=fileupload" \
     -F "fileToUpload=@/path/to/image.jpg" \
     "https://catbox.moe/user/api.php"
```

返回纯文本 URL。

### 3. 如果以上都不行

提示用户手动上传到任何图床（imgur、postimages 等），把 URL 发回来。

## PDF 转图片

当需要从 PDF 中截取页面作为配图时：

```python
import fitz  # pymupdf

doc = fitz.open("file.pdf")
page = doc[page_number]  # 0-indexed
mat = fitz.Matrix(2, 2)  # 2x zoom for good quality
pix = page.get_pixmap(matrix=mat)
pix.save("output.png")
```

安装：`pip install pymupdf --break-system-packages`

## 上传脚本

`scripts/upload_image.py` 封装了 freeimage.host 的上传逻辑：

```bash
# 单张上传
python scripts/upload_image.py /path/to/photo.jpg

# 批量上传（输出 URL 列表）
python scripts/upload_image.py /path/to/photo1.jpg /path/to/photo2.jpg /path/to/photo3.jpg
```

输出格式：
```
/path/to/photo.jpg → https://iili.io/xxx.jpg
/path/to/photo2.jpg → https://iili.io/yyy.jpg
```

## 图片在文章中的位置

图片不是装饰，是情绪节奏的一部分：
- 放在段落之间，给读者"看完一段话，缓一口气"的空间
- 3-6 张图是一篇长文的舒适区间
- 活动现场照 > 摆拍合照 > 纯风景
- 有人的照片比没人的照片更有说服力
- 如果有 PDF 截图（议程/海报），放在相关段落附近，让读者直观感受内容密度
