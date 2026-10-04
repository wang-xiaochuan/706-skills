---
name: "Navy & Gold"
description: >
  A restrained institutional editorial system for long-form WeChat articles.
  Dual-surface: cream paper for body, deep navy for header blocks.
  Single antique-gold accent, used only on rules, borders, and emphasis.
  Target: WeChat Official Account editor (inline styles, no web fonts).

colors:
  primary: "#C8A870"
  surface-cream: "#F0ECE3"
  surface-navy: "#1C2644"
  ink-navy: "#1C2644"
  ink-bluegray: "#3A4560"
  accent-gold: "#C8A870"
  accent-gold-bright: "#D4B880"
  text-on-navy: "#F0ECE3"
  text-muted: "#8A8D98"
  text-caption: "#9A9DA6"
  rule-soft: "#CAC4B4"
  blockquote-bg: "#E8E4D8"
  surface-navy-deeper: "#1F2858"

typography:
  display-serif:
    fontFamily: "'Times New Roman', 'Songti SC', STSong, serif"
    fontSize: "38px"
    fontWeight: 400
    lineHeight: 1.2
  chapter-label:
    fontFamily: "'Times New Roman', 'Songti SC', STSong, serif"
    fontSize: "16px"
    fontWeight: 700
    letterSpacing: "2px"
  chapter-title:
    fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.4
  body:
    fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 2
  body-bold:
    fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 2
  tag-mono:
    fontFamily: "'SF Mono', 'Menlo', 'Courier New', monospace"
    fontSize: "11px"
    fontWeight: 700
    letterSpacing: "4px"
  subtitle:
    fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
    fontSize: "13px"
    fontWeight: 400
    letterSpacing: "6px"
  caption:
    fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
    fontSize: "11px"
    fontWeight: 400
    letterSpacing: "0.5px"
  footnote-label:
    fontFamily: "'SF Mono', 'Menlo', 'Courier New', monospace"
    fontSize: "12px"
    fontWeight: 700

rounded:
  none: "0px"
  card: "14px"
  full: "9999px"

spacing:
  article-padding-top: "70px"
  article-padding-x: "30px"
  article-padding-bottom: "100px"
  section-gap: "60px"
  paragraph-gap: "16px"
  header-tag-to-title: "30px"
  title-to-subtitle: "25px"
  rule-margin: "40px"
  blockquote-padding: "12px 16px"
  blockquote-margin: "16px 0"
  list-margin: "8px 0 16px 18px"
  image-margin: "16px auto 0"
  caption-margin: "6px 0 20px"

components:
  dark-header-block:
    backgroundColor: "{colors.surface-navy}"
    textColor: "{colors.text-on-navy}"
    padding: "50px 24px"
  gold-rule:
    backgroundColor: "{colors.accent-gold}"
    size: "36px 1px"
  blockquote:
    backgroundColor: "{colors.blockquote-bg}"
    textColor: "{colors.ink-bluegray}"
    padding: "{spacing.blockquote-padding}"
  chapter-header:
    textColor: "{colors.accent-gold}"
    typography: "{typography.chapter-label}"
  link:
    textColor: "{colors.accent-gold}"
  image-caption:
    textColor: "{colors.text-caption}"
    typography: "{typography.caption}"
---

# Navy & Gold

## Overview

Navy & Gold is the institutional voice of 706's visual system — for annual reports, white papers, and deep analysis. It draws from the editorial restraint of *The Economist* crossed with a private intelligence briefing. It says "this has been carefully considered" and never shouts.

Target platform is WeChat Official Account editor, which imposes hard constraints: inline styles only, no web fonts, no CSS variables, no flexbox/grid, no pseudo-elements, every element must carry its own `background-color`.

## Colors

The system operates on exactly two surfaces and one accent:

- **`surface-cream`** (`#F0ECE3`) — the reading surface. All body text and most sections use this as background. This is the default ground.
- **`surface-navy`** (`#1C2644`) — the authority surface. Used exclusively for the article header block (a self-contained dark `<table>`). Never fills the entire article in WeChat — it is always an island.
- **`accent-gold`** (`#C8A870`) — the sole accent. Applied only to: the 36px header rule, chapter number labels, blockquote left borders (3px), list em-dash markers, and link text. **Gold is never a background fill. Gold is never body text.**
- **`primary`** aliases to `accent-gold` — satisfies the spec requirement for a `primary` color token.

Text hierarchy on cream is two-tier: `ink-navy` (`#1C2644`) for titles and bold, `ink-bluegray` (`#3A4560`) for body paragraphs. On navy, all text uses `text-on-navy` (`#F0ECE3`, cream-white).

Supporting colors: `text-muted` for aux labels, `text-caption` for image captions, `rule-soft` for hairline dividers, `blockquote-bg` for quote backgrounds. A deeper navy variant `surface-navy-deeper` (`#1F2858`) exists for nested dark sections but is rarely used in WeChat.

**Critical constraint**: gold is the only chromatic accent in this system. No second accent color. No green, no blue, no red. This is the Signal-derived discipline.

## Typography

Three type families, strictly role-separated:

1. **Serif** — Times New Roman / Songti SC. Article title (`display-serif`, 38px normal weight) and chapter number labels (`chapter-label`, 16px bold). Editorial gravitas. Never used for body text.
2. **Sans-serif** — PingFang SC / Microsoft YaHei. Body text (`body`, 15px, line-height 2), chapter titles (`chapter-title`, 20px bold), subtitles, captions. The workhorse for Chinese reading.
3. **Monospace** — SF Mono / Menlo. Column tags (`tag-mono`, 11px uppercase) and footnote numbers (`footnote-label`, 12px). Metadata only.

**CJK emphasis rule**: Chinese has no italic axis. Where the Latin Signal system uses gold italic for mid-sentence emphasis, this CJK adaptation uses **gold color-switch** — bold text rendered in `accent-gold` instead of `ink-navy`. This is the `emphasis=color-switch` layout mode.

Body text at 15px with line-height 2 is tuned for mobile reading on WeChat (effective content width ~315px in a 375px phone frame).

## Layout

Single-column, table-wrapped (WeChat requirement). Content area is 315px within a 375px phone frame.

Spacing rhythm: 70px top padding, 30px horizontal, 100px bottom. 60px between sections. 16px between paragraphs within a section. 30px from header tag to title. 40px around the decorative gold rule.

The dark header block is the system's signature structural move — a nested `<table>` with `surface-navy` background, containing the column tag (gold mono), a 36px gold rule, the article title (cream serif), and the English subtitle (gold). It visually asserts authority at the top of the article.

## Elevation & Depth

Completely flat. No shadows, no gradients, no blur. The WeChat editor strips `box-shadow` and `backdrop-filter` anyway.

Depth comes from: surface contrast (navy block against cream body), the 1px gold rule, the 3px gold blockquote left-border, and the two-tier text color hierarchy (ink-navy → ink-bluegray → text-muted).

## Shapes

- Blockquotes: sharp (`rounded: none`, 0px) by default; can opt into `card` (14px) via layout mode
- Headshots: `rounded: full` (50% circle)
- Gold rule: strict rectangle, 36px × 1px
- No pill-shaped elements in this system

## Components

### dark-header-block
Self-contained `<table>` with navy background. Contains: column tag in gold mono, 36px gold rule, article title in cream serif, English subtitle in gold. Never on cream background — always a dark island.

### gold-rule
36px wide × 1px tall, gold background. The system's primary decorative element. Separates tag from title in dark header. A 30px variant is used on cream surfaces.

### blockquote
3px gold left border (applied via inline `border-left`) on `blockquote-bg` warm cream background. Body text inside at `ink-bluegray`. Sharp corners by default.

### chapter-header
Two-line structure: numbered label (`01. ENGLISH`) in gold serif bold, right-floated Chinese label in muted. Second line: Chinese title in 20px bold navy.

### link
Gold text, no underline. Applied via inline `<a style="color:...">`.

### image-caption
11px right-aligned muted text below images. Letter-spacing 0.5px.

## Do's and Don'ts

- DO use the dark header block for institutional content (annual reports, white papers)
- DO use gold ONLY on rules, borders, chapter numbers, list markers, and links
- DO keep body text in `ink-bluegray` on `surface-cream` — never reverse body text out of navy
- DO use em-dash (`—`) list markers for restrained feel
- DO maintain 60px section gaps
- DO NOT use gold as a background fill or section background
- DO NOT place body paragraphs on navy background
- DO NOT use rounded corners on blockquotes by default (sharp is the system default)
- DO NOT use borders thicker than 1px except the 3px blockquote left-border
- DO NOT mix gold with any other accent color in the same article
- DO NOT use serif for body text or sans-serif for article title
- DO NOT omit the gold rule in the dark header — it is load-bearing
