#!/usr/bin/env python3
"""Phase D.1 — n-gram originality check between draft and profile sample passages.

Detects continuous overlaps between the rewritten draft and the few-shot sample
passages embedded in a style profile. The model is supposed to draw on the
samples for "feel" without lifting their phrasing; this script enforces that
constraint deterministically.

Usage:
    python3 originality_check.py \
        --draft path/to/draft.md \
        --profile path/to/style-profiles/[作家]-[译者].md \
        [--mode public|internal]

Output: JSON to stdout.
    {"flagged": [{"phrase": "...", "matched_in_sample": "...", "sample_id": N}, ...],
     "char_threshold": 7, "token_threshold": 5, "mode": "public",
     "tokenizer": "jieba"|"naive_char"}

Exit codes:
    0 — no overlaps OR overlaps found (always 0; caller checks JSON.flagged)
    2 — input file not found / unreadable
    3 — profile structure unparseable (no §五 section found)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import jieba

    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False


THRESHOLDS = {
    "public": {"char": 7, "token": 5},
    "internal": {"char": 10, "token": 7},
}

STOPWORDS_4GRAM = {
    "归根结底", "在某种程度上", "事实上", "换言之", "不言而喻",
    "众所周知", "毋庸置疑", "理所当然", "归根到底", "由此可见",
    "也就是说", "可以这么说", "在我看来", "不管怎样", "无论如何",
    "退一步说", "话说回来", "另一方面", "与此同时", "正因如此",
    "正如", "只不过", "然而", "因此", "所以",
}


def read_text(path: Path) -> str:
    if not path.exists() or not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    return path.read_text(encoding="utf-8")


def extract_samples_from_profile(profile_text: str) -> list[dict]:
    """Pull example passages from §五 of the profile.

    Section format (matches profile-schema.md):
        ## §五 示例段落 ...
        ### 示例 1 · ...
        > [actual passage text]

        **结构标注**: ...

    Returns a list of {"id": int, "text": str}.
    """
    section_match = re.search(r"##\s*§五.*", profile_text)
    if not section_match:
        section_match = re.search(r"##\s*五\s*·.*示例段落.*", profile_text)
    if not section_match:
        print("error: §五 示例段落 section not found in profile", file=sys.stderr)
        sys.exit(3)

    section_start = section_match.start()
    next_section = re.search(
        r"\n##\s*§六|\n##\s*六\s*·", profile_text[section_start:]
    )
    section_end = (
        section_start + next_section.start() if next_section else len(profile_text)
    )
    section_text = profile_text[section_start:section_end]

    examples = []
    blocks = re.split(r"###\s*示例\s*(\d+)", section_text)
    for i in range(1, len(blocks), 2):
        sample_id = int(blocks[i])
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        passage_lines: list[str] = []
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped.startswith(">"):
                passage_lines.append(stripped.lstrip(">").strip())
            elif passage_lines and not stripped:
                continue
            elif passage_lines:
                break
        passage = " ".join(passage_lines).strip()
        passage = re.sub(r"\[.*?\]", "", passage).strip()
        if passage:
            examples.append({"id": sample_id, "text": passage})
    return examples


def tokenize_jieba(text: str) -> list[str]:
    return [t for t in jieba.lcut(text) if t.strip()]


def tokenize_naive(text: str) -> list[str]:
    """Fallback tokenizer: split on whitespace and punctuation, char-by-char for CJK."""
    tokens: list[str] = []
    buffer: list[str] = []
    for ch in text:
        if "一" <= ch <= "鿿":
            if buffer:
                tokens.extend("".join(buffer).split())
                buffer = []
            tokens.append(ch)
        elif ch.isspace() or not ch.isalnum():
            if buffer:
                tokens.extend("".join(buffer).split())
                buffer = []
        else:
            buffer.append(ch)
    if buffer:
        tokens.extend("".join(buffer).split())
    return [t for t in tokens if t]


def char_only(text: str) -> str:
    """Strip everything except CJK characters and ASCII alphanum."""
    return "".join(ch for ch in text if "一" <= ch <= "鿿" or ch.isalnum())


def char_ngrams(text: str, n: int) -> set[str]:
    s = char_only(text)
    if len(s) < n:
        return set()
    return {s[i : i + n] for i in range(len(s) - n + 1)}


def token_ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def find_char_overlaps(
    draft: str, samples: list[dict], threshold: int
) -> list[dict]:
    """Find continuous CJK-char overlaps of length >= threshold."""
    sample_lookup: dict[str, dict] = {}
    for sample in samples:
        sample_chars = char_only(sample["text"])
        for n in range(threshold, min(len(sample_chars) + 1, threshold + 20)):
            for i in range(len(sample_chars) - n + 1):
                phrase = sample_chars[i : i + n]
                if phrase not in sample_lookup:
                    sample_lookup[phrase] = {
                        "id": sample["id"],
                        "context": sample["text"][:80],
                    }

    flagged: list[dict] = []
    seen: set[str] = set()
    draft_chars = char_only(draft)
    i = 0
    while i < len(draft_chars):
        best_match = None
        for n in range(min(len(draft_chars) - i, threshold + 20), threshold - 1, -1):
            phrase = draft_chars[i : i + n]
            if phrase in sample_lookup:
                best_match = (phrase, sample_lookup[phrase])
                break
        if best_match:
            phrase, info = best_match
            if phrase in STOPWORDS_4GRAM or any(
                stop in phrase and len(phrase) <= len(stop) + 2
                for stop in STOPWORDS_4GRAM
            ):
                i += 1
                continue
            if phrase not in seen:
                flagged.append(
                    {
                        "phrase": phrase,
                        "matched_in_sample": info["context"],
                        "sample_id": info["id"],
                        "type": "char",
                    }
                )
                seen.add(phrase)
            i += len(phrase)
        else:
            i += 1
    return flagged


def find_token_overlaps(
    draft_tokens: list[str], samples: list[dict], threshold: int, tokenizer
) -> list[dict]:
    """Find continuous token overlaps of length >= threshold."""
    sample_token_sets: list[tuple[int, set[tuple[str, ...]], str]] = []
    for sample in samples:
        sample_tokens = tokenizer(sample["text"])
        ngrams = set(token_ngrams(sample_tokens, threshold))
        sample_token_sets.append((sample["id"], ngrams, sample["text"][:80]))

    flagged: list[dict] = []
    seen: set[tuple[str, ...]] = set()
    for ngram in token_ngrams(draft_tokens, threshold):
        for sample_id, sample_ngrams, context in sample_token_sets:
            if ngram in sample_ngrams and ngram not in seen:
                phrase = "".join(ngram) if all(len(t) <= 2 for t in ngram) else " ".join(ngram)
                if phrase in STOPWORDS_4GRAM:
                    continue
                flagged.append(
                    {
                        "phrase": phrase,
                        "matched_in_sample": context,
                        "sample_id": sample_id,
                        "type": "token",
                    }
                )
                seen.add(ngram)
                break
    return flagged


def main() -> int:
    parser = argparse.ArgumentParser(
        description="N-gram originality check between draft and profile samples."
    )
    parser.add_argument("--draft", required=True, type=Path, help="Path to draft markdown")
    parser.add_argument(
        "--profile", required=True, type=Path, help="Path to profile markdown"
    )
    parser.add_argument(
        "--mode",
        default="public",
        choices=["public", "internal"],
        help="Threshold mode (default: public, stricter)",
    )
    args = parser.parse_args()

    draft_text = read_text(args.draft)
    profile_text = read_text(args.profile)
    samples = extract_samples_from_profile(profile_text)

    if not samples:
        print(
            json.dumps(
                {
                    "flagged": [],
                    "warning": "no samples found in profile §五",
                    "mode": args.mode,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    char_threshold = THRESHOLDS[args.mode]["char"]
    token_threshold = THRESHOLDS[args.mode]["token"]

    char_flagged = find_char_overlaps(draft_text, samples, char_threshold)

    token_flagged: list[dict] = []
    if HAS_JIEBA:
        tokenizer_name = "jieba"
        draft_tokens = tokenize_jieba(draft_text)
        token_flagged = find_token_overlaps(
            draft_tokens, samples, token_threshold, tokenize_jieba
        )
    else:
        tokenizer_name = "naive_char (token-level skipped — install jieba for word-level check)"

    all_flagged: list[dict] = []
    seen_phrases: set[str] = set()
    char_covered_spans: list[str] = [item["phrase"] for item in char_flagged]
    for item in char_flagged + token_flagged:
        if item["phrase"] in seen_phrases:
            continue
        if item["type"] == "token" and any(
            item["phrase"] in span for span in char_covered_spans
        ):
            continue
        all_flagged.append(item)
        seen_phrases.add(item["phrase"])

    output = {
        "flagged": all_flagged,
        "char_threshold": char_threshold,
        "token_threshold": token_threshold,
        "mode": args.mode,
        "tokenizer": tokenizer_name,
        "samples_loaded": len(samples),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
