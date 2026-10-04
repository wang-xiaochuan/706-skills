# 外部引入的 Skill（未收录）

这个仓库**只放 706 自己写的 skill**。下面 14 个是从外部引入的，
它们有自己的上游、许可与更新渠道 —— 收录进来会造成两套来源混在一起、
上游更新也无法追溯。所以留在本地，不公开转发。

**如果你要用它们，请直接去上游取。**

## 名单

| Skill | 上游 | 作者 | 许可 |
|-------|------|------|------|
| `citation-management` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | K-Dense Inc. | MIT |
| `hypothesis-generation` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | K-Dense Inc. | MIT |
| `networkx` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | K-Dense Inc. | MIT |
| `scientific-critical-thinking` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | K-Dense Inc. | MIT |
| `simpy` | [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | K-Dense Inc. | MIT |
| `json-canvas` | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | Steph Ango (@kepano) | MIT |
| `obsidian-bases` | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | Steph Ango (@kepano) | MIT |
| `obsidian-markdown` | [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) | Steph Ango (@kepano) | MIT |
| `cli-creator` | [openai/skills](https://github.com/openai/skills) | OpenAI | Apache-2.0 |
| `jupyter-notebook` | [openai/skills](https://github.com/openai/skills) | OpenAI | Apache-2.0 |
| `mcp-builder` | [anthropics/skills](https://github.com/anthropics/skills) | Anthropic | Apache-2.0 |
| `remotion-best-practices` | [remotion-dev/skills](https://github.com/remotion-dev/skills) | Remotion | 见上游 |
| `research-lab-notebook` | [osteele/research-notebook](https://github.com/osteele/research-notebook) | Oliver Steele | MIT |
| `research-writing-coach` | [tizzy916/humanities-writing-companion](https://github.com/tizzy916/humanities-writing-companion) | tizzy916 | **CC-BY-NC-4.0** |

### ⚠️ 两个需要注意的

**`research-writing-coach` 是 CC-BY-NC-4.0 —— 非商业许可。**
不能在商业场景使用。它是本地改编版（改编记录见其 `UPSTREAM.json`），
不是上游官方发布版。

**`remotion-best-practices` 在上游没有独立 LICENSE 文件**，
许可条款需自行向上游确认。

## 本地对引入 skill 的处理方式

从外部引入的 skill 一律保留原始 `LICENSE` 文件，并附一份 `UPSTREAM.json` 记录：

```json
{
  "upstream": {
    "repository": "https://github.com/<owner>/<repo>",
    "author": "<author>",
    "commit": "<被引入时的上游 commit>",
    "license": "<SPDX>"
  },
  "adapted_on": "<日期>",
  "changes": ["相对上游做了哪些本地改动"],
  "source_files": [{ "path": "...", "sha256": "..." }]
}
```

这样做的目的：**任何时候都能回答"这个 skill 从哪来、改了什么、依据哪个版本"**。
`research-writing-coach` 的 `UPSTREAM.json` 是目前最完整的一份，可以当模板。

## 为什么这件事值得单独写一份文档

因为"这到底是不是我写的"是开源里最容易出错、也最伤人的一步。

一个反向的例子就在这个仓库的历史里：我们曾计划开源一个本地项目，
因为它文档最全、形态最标准，看起来最适合发布 ——
后来才发现它是**某公司已经开源的公开项目**（上游已有 990 star），
本地那份只是一份复制来的快照。

**形态完备 ≠ 归属正确。** 引入别人的东西没有问题，
把别人的东西当成自己的、或者把上游项目重新发一份，才有问题。
