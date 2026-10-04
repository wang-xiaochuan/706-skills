# 706 Skills

**41 AI agent skills built by 706 Youth Space while running a real community.**

These are not demo toys. They are things we used, broke, and rewrote in daily operations:
publishing to WeChat, making Xiaohongshu posts, archiving group-chat media, cutting meeting
recordings into publishable clips, writing long research pieces, reviewing résumés, laying out
event pages — finding an automated exit for every repetitive task a community accumulates.

We are open-sourcing them because we think other communities, writers, and researchers can use them.

---

## How this repository was made

This repository was assembled by **Xiaochuan's personal AI assistant**, working from
conversations with him.

To be precise about what that means:

- **The skills are his and 706's work.** They were written, used, and iterated on in real
  operations. The workflows, the design systems, the trigger conditions — those came from
  doing the work.
- **The packaging is the assistant's work.** Sanitizing absolute paths, resolving broken
  internal references, checking provenance, writing this README and `VENDORED.md`,
  and uploading the result.
- **He reviewed and approved it** before publication.

We are stating this plainly because it affects how you should read the repo: the
documentation describes what the skills do, but it has not been battle-tested by a second
team. Treat the *Known gaps* section below as the honest state of things, not as
boilerplate.

<sub>中文：本仓库由王小川的数字助手在与他的交流后整理打包并代为上传，经他本人审阅确认。
skill 本身是他与 706 在真实运营中的工作成果；清理绝对路径、补齐失效引用、核对来源归属、
撰写本文档等工作由助手完成。之所以写清楚，是因为它影响你该怎么读这个仓库 ——
文档描述的是这些 skill 做什么，但它没有经过第二个团队的实战验证。</sub>

## What this repository is

A **collection of skills**. Each directory is one self-contained skill following the common
`SKILL.md` convention:

```
<skill-name>/
├── SKILL.md            # required: trigger conditions + workflow
├── references/         # optional: detailed specs, loaded on demand
├── assets/             # optional: templates
├── scripts/            # optional: runnable scripts
└── evals/              # optional: test cases
```

The `name` and `description` in `SKILL.md`'s YAML frontmatter decide **when the skill fires**.
Writing good trigger words into `description` is what makes a skill usable — it is not decoration.

## Using these

**Option 1 — hand it to an AI assistant that can read files.** Give it the `SKILL.md` plus
the folders it references, or just say "read `<path>/SKILL.md` and follow it".

**Option 2 — drop it into your tool's skill directory.** The location differs per host
(Claude Code, Codex, other agent frameworks) — check your host's docs.

**No extra dependencies.** A skill is just Markdown. Only the scripts under `scripts/` need a
runtime (Python 3 / Node); the requirements are stated in that skill's `SKILL.md`.

## ⚠️ Path conventions — read this before using anything

These skills were extracted from 706's actual workspace and reference our directory layout.
Original absolute paths have been replaced with variables for portability.
**You need to map them to your own directories:**

| Variable | Meaning | Our default |
|----------|---------|-------------|
| `$706_LOCAL` | local workspace root | `~/dev/706-local-os` |
| `$706_CLOUD` | cloud-synced document root | `~/Library/CloudStorage/OneDrive-个人/2026 dev` |
| `$CODEX_HOME` | your agent's skill install directory | `~/.codex` |

**Two ways to adapt:**

1. **Set the environment variables** (preferred) — works if your host passes env vars to scripts
2. **Edit the text** — global-replace `$706_LOCAL` with your own path

You will also see references to `706-knowledge/`, `706-media/`, `706-system/` — that is 706's
seven-layer project structure (`inbox / system / source / outputs / media / knowledge / archive`).
**If your workspace is not laid out that way, map by meaning, not literally.**

If you only want to try one or two skills, start with the ones marked **general-purpose** below —
they do not depend on a specific directory layout.

---

## Skill index

Four groups, one for each kind of work a community actually does:
**operations · media · research · writing.**

<sub>中文：41 个 skill 分四类 —— 运营 · 媒体 · 研究 · 写作。分类标准是"这份工作本身属于哪一类"，不是技术栈。</sub>

### Operations — running the thing

Keeping a community's day-to-day machinery moving: tasks, tooling, events, money signals.

| Skill | Files | What it does |
|-------|-------|--------------|
| `task-sync` | 1 | Create, sync, assign, reschedule, close, reopen, and batch-audit task records |
| `task-distribution` | 2 | Reads pending items → determines owning project → writes into that project's task pool |
| `panel-curator` | 2 | Researches panellists and assembles moderation guides |
| `harness-goal-runner` | 5 | Designs a local goal harness that keeps an agent pushing toward one objective |
| `browser` | 1 | Browser automation: navigate, read, click, fill forms, screenshot, inspect console and network |
| `lark-docx-editor` | 1 | Read/write wrapper around the Feishu (Lark) Docx block API |
| `gdocs-mcp` | 2 | Google Docs + Drive MCP server (capability reference, not trigger-based) |
| `md-to-pdf-songti` | 2 | Renders Markdown to PDF via XeLaTeX using Songti SC |
| `binance-4h-signal` | 25 | Synthesises 4H candles from 1H, fuses 23 indicators with regime-dynamic weights, emits trade signals |
| `resume-from-evidence` | 9 | Builds a truthful résumé from chat logs + old résumés + target roles, via experience verification and reverse role analysis |
| `resume-hr-review` | 7 | Simulates a recruiter's initial screen: requirement–evidence comparison, coverage, and revision priorities |
| `skill-creator` | 2 | Skill evaluation and iteration: samples, with-skill/baseline comparison, scoring, trigger testing |
| `skill-optimizer` | 1 | Reviews skill quality across five dimensions and outputs an improvement report |

### Media — getting it out, keeping it

Publishing, archiving, and turning raw recordings into something publishable.

| Skill | Files | What it does |
|-------|-------|--------------|
| `wechat-design` | 5 | WeChat article layout design system: 9 colour palettes × layout switches, freely combined |
| `wechat-publish` | 3 | Turns Notion / Markdown into rich HTML you can paste straight into the WeChat editor |
| `wechat-publish-2.0` | 1 | Visual control panel + live preview + LLM-assisted adjustment |
| `wechat-slides` | 2 | Vertical HTML image cards / screenshot slides, default 750×1334px |
| `xhs-copywriter` | 2 | Xiaohongshu titles, body copy, and topic tags |
| `xiaohongshu-poster` | 2 | Xiaohongshu event cover posters, default HTML 1080×1440px |
| `content-intelligence-search` | 2 | Cross-platform content intelligence: find high-reach posts by view/like thresholds |
| `706-notion-writer` | 6 | Writes event recruitment long-form in Notion, matching 706's community register |
| `media-ingest` | 2 | Sorts incoming media-inbox images: scene detection → event type → location archiving |
| `wechat-image-archive` | 2 | WeChat context sync entry point: image assets, group summaries, relationship maintenance |
| `wechat-article-smart-archive` | 17 | Discovers and archives public WeChat articles by account/keyword and date range; produces offline-shareable HTML |
| `speech-to-attention-video` | 9 | Meeting / interview / lecture footage → narrative cut, thematic cut, attention slices, subtitles, delivery package |
| `706-audio-transcribe-archive` | 3 | Audio to timestamped Chinese transcript, with multi-speaker alignment and corpus archiving |
| `video-download` | 2 | Unified Bilibili + YouTube download and archiving: batch, resumable, subtitle capture |
| `image-ocr` | 1 | Local Tesseract Chinese OCR / batch text extraction |
| `image-to-html` | 2 | Packs an image folder into a Base64-embedded HTML file for feeding images to a model |

### Research — turning experience into something citable

Fieldwork, evidence, and the ability to tell what you actually know.

| Skill | Files | What it does |
|-------|-------|--------------|
| `personal-decision-harness` | 12 | Personal judgement and judgement-training system: do it, don't do it, or do it differently — with evidence and revisit conditions |
| `medium-research-report-harness` | 30 | Build, continue, restructure, audit, translate, and package evidence-rich research reports of roughly 8,000–40,000 Chinese characters |
| `rhetorical-structure-harness` | 20 | Two-layer rhetorical structure for spoken delivery: occasion–audience–purpose → section-by-section topic sentence + rhetorical moves |
| `literature-search` | 2 | Academic literature search with structured archiving; produces a source list with verification status |
| `706-long-article-distilling` | 2 | Distils long articles / PDFs / reports / interviews into eight-part structured notes |

### Writing — finding the voice

Style transfer, narrative design, and the raw material that precedes it.

| Skill | Files | What it does |
|-------|-------|--------------|
| `author-style-mimicry` | 6 | Rewrites public-facing content in the literary voice of a specific foreign author (via Chinese translation); treats "author × translator" as one compound style unit |
| `debotton-chen-nan-rewrite` | 2 | Rewrites drafts in Alain de Botton's voice (Chen Guangxing / Nan Zhiguo translation of *The Pleasures and Sorrows of Work*), iterating to convergence |
| `debotton-chen-nan-write` | 3 | Designs narrative, research brief, and outline for event retrospectives, then writes them |
| `scholar-analyst-rewrite` | 2 | Rewrites in the tradition of anthropologists / sociologists / analysts writing on technology and society in China (Xiang Biao, Peter Hessler, Dan Wang) |
| `706-ghostwriter` | 2 | A writing partner that builds judgement through reading: intake → four-layer review → collaborative writing |
| `prewriting` | 12 | Turns raw material into traceable project learning notes covering people, dates, quotes, scenes, organisations, background, numbers |
| `moments-work-diary` | 2 | Generates and iterates short social-media-style work diaries, with a tone check |

---

## ⚠️ Known gaps — read before relying on anything

While packaging this repository we validated every internal reference in every `SKILL.md`.
**Four skills reference files that are not included.** Each has a note at the top of its
`SKILL.md` explaining what is missing. They fall into two groups:

### Missing core implementation — currently skeletons, not runnable

| Skill | Missing |
|-------|---------|
| `content-intelligence-search` | `references/wechat.md` and `references/xiaohongshu.md` — the per-platform search implementations. The `SKILL.md` is only the workflow skeleton |
| `lark-docx-editor` | `scripts/lark_docx.py` — the Python wrapper around the Feishu Docx block API. The `SKILL.md` documents the API usage and block structure, but the script itself is absent |

**Our recommendation is to read these two as design documents and supply your own implementation
if you want to run them.** (If you would rather not ship a skill that cannot run, deleting these
two is the cleanest option.)

### Missing reference files — does not affect the main flow

| Skill | Missing |
|-------|---------|
| `skill-creator` | `references/schemas.md` (full evaluation schema), `assets/eval_review.html` (review page template) |
| `xiaohongshu-poster` | `references/template.html` (one issue's full layout implementation — the text itself says "for reference only, do not copy directly") |

Also fixed during packaging: three skills (`wechat-image-archive`, `prewriting`, `task-sync`)
referenced files that were scattered elsewhere in the workspace. Those files are now bundled in
and the references rewritten as skill-relative paths, so those skills are self-contained.
Two skills (`debotton-chen-nan-write`, `skill-creator`) had frontmatter `name` values that did
not match their directory names; those are now aligned, since most hosts install skills by that match.

## General-purpose vs 706-specific

The four groups above are not a portability rating — they are what the work *is*.
Portability cuts across them:

**General-purpose** (work as-is once you fix the paths): `rhetorical-structure-harness`,
`personal-decision-harness`, `medium-research-report-harness`, `resume-from-evidence`,
`resume-hr-review`, `speech-to-attention-video`, `md-to-pdf-songti`, all seven Writing skills,
and most of Media.

**706-specific** (tightly coupled to our directory structure, task system, and media library):
`task-sync`, `task-distribution`, `media-ingest`, `wechat-image-archive`, `706-notion-writer`.

What is useful in those five is the *method* — how a community breaks repetitive work into
automatable skills — rather than running them directly. Read the *Path conventions* section first.

<sub>中文：上面四类是"工作本身属于哪一类"，不是可移植性评级。可移植性另说 ——
通用的有 `rhetorical-structure-harness`、`personal-decision-harness`、`resume-from-evidence`、
`speech-to-attention-video`、`md-to-pdf-songti` 及写作类全部；强耦合 706 的有
`task-sync`、`task-distribution`、`media-ingest`、`wechat-image-archive`、`706-notion-writer`，
读它们主要看方法而不是直接跑。</sub>

## Skills not included

This repository contains **only skills we wrote ourselves**. Fourteen skills were brought in
from outside; they have their own upstreams, licences, and update channels, so they are not
included here.

The full list with upstream URLs and licence notes is in [`VENDORED.md`](VENDORED.md).

> One of them, `research-writing-coach`, is **CC-BY-NC-4.0 (non-commercial)** —
> check the terms yourself before use.

## Background

706 Youth Space is a self-organised, collectively maintained public space network, running
since 2012. We are not an AI company — just a group of people using tools to solve our own problems.

This skill collection is part of our answer to "what infrastructure does a community need":
write down the things that keep happening, so next time you do not start from zero.

## License

MIT — see [`LICENSE`](LICENSE).

- Any licence notice inside an individual skill's directory takes precedence for that skill.
- Externally sourced skills are **not included** here; see [`VENDORED.md`](VENDORED.md).
  One of them, `research-writing-coach`, is **CC-BY-NC-4.0 (non-commercial)** — verify the terms yourself.
