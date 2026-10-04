# Notion MCP 操作模式详解

## 工具清单

这个 skill 使用以下 Notion MCP 工具：
- `notion-fetch` — 读取页面内容
- `notion-update-page` — 修改页面内容（两种模式）
- `notion-create-pages` — 创建新页面
- `notion-search` — 搜索页面

## 两种编辑模式

### `replace_content`：全文替换

**什么时候用：** 初稿阶段，从零写入，或者需要大规模重组结构时。

```json
{
  "page_id": "xxx",
  "replace_content": "完整的新内容（markdown 格式）"
}
```

注意：这会清掉页面上的所有内容，包括图片。只在确实需要全文重写时使用。

### `update_content`：精确替换

**什么时候用：** 迭代打磨阶段，修改特定段落而保留其余内容。

```json
{
  "page_id": "xxx",
  "update_content": {
    "old_str": "要替换的原文（必须完全匹配）",
    "new_str": "替换后的新文本"
  }
}
```

关键注意事项：
1. **必须先 fetch** — 在做 update_content 之前，一定要先 `notion-fetch` 页面，拿到当前的精确文本
2. **完全匹配** — `old_str` 必须和页面上的文本逐字逐符匹配，包括空格、标点、换行
3. **唯一性** — `old_str` 在页面中必须是唯一的。如果有重复，取更长的上下文以确保唯一
4. **不要猜** — 不要凭记忆写 `old_str`，一定要从 fetch 结果中复制

## 常见操作

### 插入图片

在 Notion markdown 中，图片用标准 markdown 语法：
```markdown
![描述](https://image-url.com/xxx.jpg)
```

插入图片 = 用 `update_content` 把目标位置的文本替换为包含图片的文本：
```json
{
  "old_str": "上一段的最后一句话",
  "new_str": "上一段的最后一句话\n\n![活动现场](https://iili.io/xxx.jpg)\n"
}
```

### 设置封面图

```json
{
  "page_id": "xxx",
  "cover_url": "https://image-url.com/cover.jpg"
}
```

### 设置页面 icon

```json
{
  "page_id": "xxx",
  "icon": "emoji-here"
}
```

### 创建新页面

```json
{
  "parent_id": "父页面ID",
  "title": "页面标题",
  "content": "页面内容（markdown）"
}
```

## 内容格式

Notion 的 markdown 支持：
- `#` `##` `###` 标题
- `**粗体**`
- `*斜体*`
- `> 引用`
- `- 列表`
- `1. 有序列表`
- `---` 分割线
- `![alt](url)` 图片
- `` `行内代码` ``

段落之间用空行分隔。

## 调试技巧

如果 `update_content` 失败（通常是 old_str 匹配不到）：
1. 重新 `notion-fetch` 页面
2. 找到目标文本的精确内容
3. 检查是否有隐藏的特殊字符（em dash vs hyphen、全角 vs 半角标点）
4. 如果还是不行，取更长的上下文作为 old_str
