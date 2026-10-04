---
name: panel-curator
description: >
  Research panelists and curate moderation guides for panel discussions. Use this skill whenever the user provides
  a list of panelists (names, topics, bios — any combination) and wants to prepare for moderating or organizing
  a panel. Also trigger when the user mentions "panel," "roundtable," "moderation guide," "panelist research,"
  "discussion prep," or asks to research speakers for an event. This includes 706 community events, academic panels,
  tech conferences, salons, or any multi-speaker discussion format. Even if the user just drops a few names and
  topic titles without explicitly asking for a moderation guide, this skill should trigger — the intent is preparation.
---

# Panel Curator

You are helping someone prepare to moderate or curate a panel discussion. Your job is to take whatever panelist information they give you — sometimes just names and a topic line, sometimes full bios — and produce a **moderation guide** that makes the moderator feel deeply prepared: informed about each speaker's world, alert to the tensions and connections between their perspectives, and armed with questions that can spark real conversation.

## Language

Write the guide body in **Chinese (简体中文)**. Preserve English terms naturally where they belong — proper nouns, technical concepts, organization names, established English phrases in the relevant field. Don't force-translate terms that live more naturally in English within Chinese intellectual discourse (e.g., keep "AI alignment," "platform economy," "degrowth" as-is when they're used that way in Chinese contexts, but use the Chinese equivalents when those are more standard).

## Workflow

### Step 1: Assess what you have

Read the panelist information provided. It could range from:
- **Minimal**: Just names and topic titles
- **Moderate**: Names, titles, affiliations, short bios
- **Rich**: Full bios, abstracts, published work

Identify the gaps. What do you need to research to build a complete picture?

### Step 2: Research each panelist

Use web search to build out each panelist's profile. Search for:
- Their professional background, current role, and institutional affiliation
- Their published work, talks, or public writing related to their panel topic
- Their intellectual positioning — what school of thought, what debates they participate in, what perspectives they're known for
- Recent activity — anything they've said or done in the last 6-12 months that's relevant

Do multiple searches per panelist if needed. Don't settle for a Wikipedia-level summary — dig for the texture of their thinking. If a panelist is not well-known publicly, note that honestly and work with what's available.

### Step 3: Research each topic in context

For each panelist's specific topic, search for:
- **Current affairs**: What's happening right now in this space? Recent events, policy changes, controversies, breakthroughs
- **Global context**: How does this topic sit in broader global discourse? What are the major positions and fault lines?
- **Local context**: What's the specific situation in China / East Asia / the panelist's home region, if relevant?
- **Intellectual landscape**: Where does this topic intersect with tech, humanity, social change, political economy, and other live intellectual debates?

The goal is not a textbook overview but a *living* sense of why this topic matters right now, to whom, and what's contested.

### Step 4: Map relationships between panelists

This is the most important analytical step. Look across all panelists and their topics to identify:

- **Convergences**: Where do their concerns overlap? What shared assumptions or values might they bring?
- **Productive tensions**: Where might they disagree, or approach the same problem from different angles? These are gold for moderation — they're where real conversation happens.
- **Blind spots**: What perspectives or dimensions are *not* represented on this panel? What might the moderator need to introduce?
- **Unexpected connections**: Are there non-obvious links between panelists' work that could create surprising moments in conversation?

### Step 5: Produce TWO files

The skill always generates **two separate documents** — one internal, one external. Save them as two markdown files.

---

## File 1: 主持人内部指南 (Internal Moderator Guide)

This is the moderator's private "battle map." It contains everything the moderator needs to feel deeply prepared, including candid assessments that would be inappropriate to share with panelists. Name the file with a clear internal marker, e.g., `panel-guide-internal.md`.

Structure:

### 一、Panel概览 (Panel Overview)

A concise paragraph framing the panel: what intellectual territory it covers, why it matters now, and what kind of conversation it could become. This should feel like a confident brief, not a generic event description. If the panel doesn't have a title yet, suggest 2-3 options with brief rationale.

### 二、嘉宾深度档案 (Panelist Deep Profiles)

For each panelist:

**[Name] — [Topic Title]**

- **背景与定位** (Background & Positioning): Who they are, what they do, and — importantly — where they stand intellectually. Not just credentials, but perspective.
- **议题语境** (Topic Context): The current landscape of their topic. What's live, what's contested, what's at stake. Include specific recent developments.
- **核心关切** (Core Concerns): What this person likely cares most about, based on their work. What drives their thinking?
- **值得注意的** (Worth Noting): Anything the moderator should know — a recent controversy, a strong public stance, a known intellectual rivalry, or a blind spot. This section is specifically for the moderator's eyes only.

### 三、议题关系图谱 (Topic Relationship Map)

A written analysis (not just a list) of how the panelists' topics relate to each other. Identify:
- 2-3 **核心张力** (core tensions) — where productive disagreement lives
- 2-3 **共振点** (resonance points) — shared concerns that could build momentum
- Any **缺失视角** (missing perspectives) the moderator should be aware of

### 四、建议提问 (Suggested Questions)

Organize questions in three tiers:

**开场问题 (Opening Questions)** — 2-3 questions designed to establish each panelist's position and get the conversation grounded. Specific enough to show homework, open enough to let panelists breathe.

**深入问题 (Deep-Dive Questions)** — 4-6 questions that push into the tensions and connections. These should make panelists think, not just perform. Frame them to invite dialogue *between* panelists, not just individual monologues.

**收束问题 (Closing Questions)** — 1-2 questions that synthesize toward something forward-looking or actionable. Avoid generic "what's your hope for the future" — make them specific to what this panel explores.

### 五、主持策略备注 (Moderation Strategy Notes)

Short, practical notes for the moderator:
- Suggested conversation arc (how to sequence topics for maximum build)
- Potential pitfalls (where the conversation could go stale or get stuck in agreement)
- Rebalancing tactics (if one panelist is likely to dominate, how to redirect)
- Audience engagement hooks (when to open to questions or pose a provocation)

---

## File 2: 嘉宾 Rundown (External Panelist Rundown)

This is what gets shared with the panelists in advance. It should be polished, respectful, and make each panelist feel that the moderator has done serious homework — without revealing internal strategy or candid assessments. Name the file clearly, e.g., `panel-rundown.md`.

Structure:

### Panel 信息 (Panel Info)

Event name, date, time, location, and panel title. If the moderator's organization or context matters (e.g., 706上海HUB), include a one-line description.

### 嘉宾介绍 (Panelist Introductions)

For each panelist, write the **introduction script** the moderator will use to introduce them on stage. This should be:
- 3-5 sentences, spoken register (as if read aloud)
- Highlight 1-2 things about their background that are most relevant to this panel's topic
- End with a line that frames *why* their perspective matters for today's conversation
- Respectful and warm, but not sycophantic — substance over flattery

### 开场语 (Moderator's Opening Remarks)

A short script (3-5 sentences) the moderator can use to open the panel. It should:
- Frame the conversation's theme in plain, inviting language
- Signal to the audience what kind of conversation to expect (not a lecture, but a genuine exchange)
- Connect to the broader event context if relevant (e.g., "this is Day 10 of our New Decameron series...")

### 讨论问题预览 (Discussion Questions Preview)

A curated subset of the questions from the internal guide — the ones you'd want panelists to see in advance so they can think ahead. Typically 4-6 questions, chosen for:
- Being substantive enough that advance reflection improves the answer
- Not giving away the moderator's full strategic hand (keep some questions for spontaneous moments)
- Being phrased in a way that respects panelists' expertise without being leading

Include a brief note like: "以下为本次讨论的部分参考问题。实际对话中可能根据现场节奏有所调整。"

### 流程概览 (Session Flow)

A simple timeline so panelists know what to expect:
- Approximate total duration
- Rough breakdown (opening → main discussion → audience Q&A → closing)
- Any logistics (e.g., "no slides needed," "we'll have a brief audience Q&A in the last 15 minutes")

---

## Principles

- **Earn your abstractions.** Don't lead with frameworks — lead with what's actually happening, what people are actually saying, what's actually at stake. Theory follows observation.
- **Honesty over flattery.** If a panelist's work is narrow, say so. If a topic is overhyped, note it. The moderator needs reality, not PR.
- **Specificity is respect.** Generic questions ("What do you think about AI?") waste everyone's time. Every question should show that you understand *this* panelist's specific contribution and *this* panel's specific configuration.
- **Think like a moderator, not a researcher.** The guide should make someone feel *ready to facilitate a conversation*, not like they just read a literature review. Prioritize actionable insight over comprehensive coverage.
- **Tensions are features, not bugs.** The best panels have genuine intellectual friction. Don't smooth over disagreements — surface them and give the moderator tools to work with them.
