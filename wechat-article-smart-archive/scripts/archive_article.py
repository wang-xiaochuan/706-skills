#!/usr/bin/env python3
"""Create one self-contained, semantically indexed WeChat article HTML."""

from __future__ import annotations

import argparse
import html as html_std
import io
import json
import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
from lxml import etree, html

from archive_lib import (
    INDEX_ID,
    SCHEMA_VERSION,
    atomic_write,
    compact_text,
    encode_data_uri,
    first_text,
    json_script_payload,
    parse_html,
    sha256_bytes,
)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)
BLOCK_PATTERNS = {
    "environment_abnormal": ("环境异常", "完成验证后即可继续访问"),
    "rate_limited": ("访问过于频繁", "操作频繁"),
    "deleted": ("该内容已被发布者删除", "此内容因违规无法查看"),
    "not_found": ("页面不存在", "内容不存在"),
}
TEXT_TAGS = ("p", "section", "div", "span", "figcaption", "blockquote", "h1", "h2", "h3", "h4", "li")
DATE_PATTERNS = (
    re.compile(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})日?"),
    re.compile(r"(?<!\d)(\d{1,2})月(\d{1,2})日"),
)
LOCATIONS = (
    "东京", "Tokyo", "上海", "Shanghai", "北京", "Beijing", "杭州", "Hangzhou",
    "深圳", "Shenzhen", "广州", "Guangzhou", "香港", "Hong Kong", "成都", "Chengdu",
)


class CaptureError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def fetch_html(url: str, timeout: int) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Referer": "https://mp.weixin.qq.com/"},
        timeout=timeout,
    )
    response.raise_for_status()
    if len(response.content) > 15 * 1024 * 1024:
        raise CaptureError("html_too_large", "article HTML exceeds 15 MB")
    response.encoding = response.apparent_encoding or "utf-8"
    return response.text


def reject_block_page(raw_html: str) -> None:
    text = compact_text(parse_html(raw_html).text_content())[:12000]
    for code, phrases in BLOCK_PATTERNS.items():
        if any(phrase in text for phrase in phrases):
            raise CaptureError(code, f"WeChat returned a non-article page: {code}")


def article_metadata(doc, source_url: str) -> dict:
    title = first_text(doc, [
        '//meta[@property="og:title"]/@content', '//*[@id="activity-name"]',
        '//h1[contains(@class,"rich_media_title")]', '//title',
    ])
    account = first_text(doc, [
        '//*[@id="js_name"]', '//*[contains(@class,"profile_nickname")]',
        '//meta[@name="author"]/@content',
    ])
    author = first_text(doc, [
        '//*[@id="js_author_name"]', '//*[contains(@class,"rich_media_meta_text")][1]',
    ])
    published_at = first_text(doc, [
        '//*[@id="publish_time"]', '//meta[@property="article:published_time"]/@content',
    ])
    if not published_at:
        raw = etree.tostring(doc, encoding="unicode")
        timestamp = re.search(r"(?:ct|create_time)\s*[:=]\s*['\"]?(\d{10})", raw)
        if timestamp:
            published_at = datetime.fromtimestamp(int(timestamp.group(1)), tz=timezone.utc).isoformat()
        else:
            picture_date = re.search(
                r"create_time\s*:\s*['\"]((?:20\d{2})-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)['\"]",
                raw,
            )
            if picture_date:
                published_at = picture_date.group(1)
    return {
        "title": title or "未命名公众号文章",
        "account_name": account or None,
        "author": author or None,
        "published_at": published_at or None,
        "source_url": source_url or None,
    }


def decode_js_string(value: str) -> str:
    """Decode the limited JS string escapes used in picture-message payloads."""
    value = re.sub(r"\\x([0-9a-fA-F]{2})", lambda match: chr(int(match.group(1), 16)), value)
    value = re.sub(r"\\u([0-9a-fA-F]{4})", lambda match: chr(int(match.group(1), 16)), value)
    return html_std.unescape(value.replace(r"\'", "'").replace(r'\"', '"').replace(r"\\", "\\"))


def picture_message_data(raw: str) -> tuple[str, list[str]]:
    """Extract description HTML and top-level image URLs from cgiDataNew."""
    content_match = re.search(r"content_noencode\s*:\s*'((?:\\.|[^'])*)'", raw, re.DOTALL)
    content = decode_js_string(content_match.group(1)) if content_match else ""

    marker = re.search(r"picture_page_info_list\s*:\s*\[", raw)
    if not marker:
        return content, []
    start = marker.end() - 1
    quote = None
    escaped = False
    square_depth = 0
    brace_depth = 0
    object_start = None
    objects = []
    for offset, char in enumerate(raw[start:], start=start):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
        elif char == "[":
            square_depth += 1
        elif char == "]":
            square_depth -= 1
            if square_depth == 0:
                break
        elif char == "{" and square_depth == 1:
            if brace_depth == 0:
                object_start = offset
            brace_depth += 1
        elif char == "}" and square_depth == 1 and brace_depth:
            brace_depth -= 1
            if brace_depth == 0 and object_start is not None:
                objects.append(raw[object_start:offset + 1])
                object_start = None

    urls = []
    for item in objects:
        match = re.search(r"cdn_url\s*:\s*'((?:\\.|[^'])*)'", item)
        if match:
            url = decode_js_string(match.group(1))
            if url:
                urls.append(url.replace("http://", "https://", 1))
    return content, urls


def build_picture_article_root(doc):
    """Materialize WeChat picture-message pages whose raw image container is empty."""
    raw = etree.tostring(doc, encoding="unicode")
    content, image_urls = picture_message_data(raw)
    if not image_urls:
        return None
    root = html.Element("article", id="js_content")
    root.set("class", "rich_media_content picture_message_content")
    if content:
        try:
            content_node = html.fragment_fromstring(content, create_parent="div")
            root.append(content_node)
        except (etree.ParserError, ValueError):
            paragraph = html.Element("p")
            paragraph.text = compact_text(content)
            root.append(paragraph)
    for position, url in enumerate(image_urls, start=1):
        figure = html.Element("figure")
        image = html.Element("img")
        image.set("data-src", url)
        image.set("alt", f"图片消息第 {position} 张图")
        caption = html.Element("figcaption")
        caption.text = f"图 {position}"
        figure.extend((image, caption))
        root.append(figure)
    return root


def pick_article_root(doc):
    roots = doc.xpath('//*[@id="js_content"]')
    if not roots:
        roots = doc.xpath('//div[contains(@class,"rich_media_content")]')
    if not roots:
        roots = doc.xpath('//article')
    if not roots:
        picture_root = build_picture_article_root(doc)
        if picture_root is not None:
            roots = [picture_root]
        else:
            raise CaptureError("article_body_missing", "could not find WeChat article body")
    root = roots[0]
    # WeChat also publishes image-only posts. Treat a short text body as empty
    # only when it contains no substantive visual/media content.
    media_nodes = root.xpath('.//img|.//video|.//mp-common-videosnap|.//iframe')
    if len(compact_text(root.text_content())) < 20 and not media_nodes:
        raise CaptureError("article_body_empty", "article body is empty or too short")
    for node in root.xpath('.//script|.//noscript|.//form'):
        node.getparent().remove(node)
    normalize_article_visibility(root)
    return root


def normalize_article_visibility(root) -> None:
    """Remove WeChat's pre-render hiding from an offline article body."""
    declarations = []
    for declaration in (root.get("style") or "").split(";"):
        if not declaration.strip():
            continue
        name, separator, value = declaration.partition(":")
        if separator and name.strip().lower() in {"visibility", "opacity"}:
            continue
        if separator and name.strip().lower() == "display" and value.strip().lower().startswith("none"):
            continue
        declarations.append(declaration.strip())
    declarations.extend(("visibility: visible !important", "opacity: 1 !important"))
    root.set("style", "; ".join(declarations) + ";")


def nearest_context(img, direction: str) -> str:
    axis = "preceding" if direction == "previous" else "following"
    predicate = " or ".join(f"self::{tag}" for tag in TEXT_TAGS)
    nodes = img.xpath(f"{axis}::*[{predicate}]")
    if direction == "previous":
        nodes = reversed(nodes)
    for node in nodes:
        if img in node.xpath('.//img'):
            continue
        text = compact_text(node.text_content())
        if 2 <= len(text) <= 500:
            return text
    return ""


def infer_date(text: str, article_date: str | None) -> tuple[str | None, list[str]]:
    match = DATE_PATTERNS[0].search(text)
    if match:
        year, month, day = map(int, match.groups())
        return f"{year:04d}-{month:02d}-{day:02d}", ["image_context"]
    match = DATE_PATTERNS[1].search(text)
    if match:
        year_match = re.search(r"20\d{2}", article_date or "")
        year = int(year_match.group()) if year_match else datetime.now().year
        month, day = map(int, match.groups())
        return f"{year:04d}-{month:02d}-{day:02d}", ["image_context", "article_year"]
    return None, []


def infer_location(text: str) -> tuple[str | None, list[str]]:
    lower = text.lower()
    for candidate in LOCATIONS:
        if candidate.lower() in lower:
            canonical = {"Tokyo": "东京", "Shanghai": "上海", "Beijing": "北京",
                         "Hangzhou": "杭州", "Shenzhen": "深圳", "Guangzhou": "广州",
                         "Hong Kong": "香港", "Chengdu": "成都"}.get(candidate, candidate)
            return canonical, ["image_context"]
    return None, []


def read_image(source: str, base_url: str, input_path: Path | None, timeout: int) -> tuple[bytes, str, str]:
    if source.startswith("data:"):
        match = re.fullmatch(r"data:([^;,]+);base64,(.+)", source, re.DOTALL)
        if not match:
            raise ValueError("unsupported data URI")
        import base64
        return base64.b64decode(match.group(2)), match.group(1), "embedded_source"

    resolved = urljoin(base_url, source) if base_url else source
    parsed = urlparse(resolved)
    if parsed.scheme in ("http", "https"):
        response = requests.get(
            resolved,
            headers={"User-Agent": USER_AGENT, "Referer": base_url or "https://mp.weixin.qq.com/"},
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.content
        mime = response.headers.get("Content-Type", "").split(";", 1)[0]
    else:
        if input_path is None:
            raise ValueError("remote article cannot read a local image path")
        local = Path(unquote(parsed.path)) if parsed.scheme == "file" else Path(source)
        if not local.is_absolute() and input_path:
            local = input_path.parent / local
        data = local.read_bytes()
        mime = mimetypes.guess_type(local.name)[0] or "application/octet-stream"
        # A shared archive must not disclose the creator's absolute local path.
        resolved = f"local-input:{local.name}"
    if not mime.startswith("image/"):
        mime = mimetypes.guess_type(parsed.path)[0] or "image/jpeg"
    return data, mime, resolved


def optimize_image(data: bytes, mime: str, max_dimension: int, quality: int) -> tuple[bytes, str, bool]:
    """Optionally shrink static raster images for storage-constrained legacy upgrades."""
    if max_dimension <= 0 or mime in {"image/gif", "image/svg+xml"}:
        return data, mime, False
    try:
        from PIL import Image, ImageOps

        image = Image.open(io.BytesIO(data))
        if getattr(image, "is_animated", False):
            return data, mime, False
        image = ImageOps.exif_transpose(image)
        image.thumbnail(
            (max_dimension, max_dimension),
            Image.Resampling.LANCZOS,
        )
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        output = io.BytesIO()
        image.save(output, "WEBP", quality=quality, method=6)
        candidate = output.getvalue()
        if len(candidate) >= len(data):
            return data, mime, False
        return candidate, "image/webp", True
    except Exception:
        return data, mime, False


def extract_public_metrics(doc) -> list[dict]:
    mapping = {
        "read_count": ('//*[@id="readNum"]/text()', '//*[@id="js_read_area"]/@data-read-num'),
        "like_count": ('//*[@id="likeNum"]/text()', '//*[@id="old_like"]/text()'),
        "wow_count": ('//*[@id="js_like_btn"]/text()',),
    }
    values = {}
    for key, paths in mapping.items():
        text = first_text(doc, list(paths))
        match = re.search(r"[\d,.]+", text)
        values[key] = int(match.group().replace(",", "")) if match else None
    captured = any(value is not None for value in values.values())
    return [{
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **values,
        "share_count": None,
        "comment_count": None,
        "source": "public_rendered_page",
        "status": "captured_partial" if captured else "not_visible",
    }]


def archive(
    raw_html: str,
    source_url: str,
    input_path: Path | None,
    timeout: int,
    max_image_dimension: int = 0,
    image_quality: int = 82,
) -> tuple[str, dict]:
    reject_block_page(raw_html)
    source_doc = parse_html(raw_html)
    metadata = article_metadata(source_doc, source_url)
    metrics = extract_public_metrics(source_doc)
    root = pick_article_root(source_doc)
    clean_root = html.fromstring(etree.tostring(root, encoding="unicode"))

    image_records = []
    image_failures = []
    for position, img in enumerate(clean_root.xpath('.//img'), start=1):
        image_id = f"img-{position:03d}"
        source = img.get("data-src") or img.get("data-original") or img.get("src") or ""
        previous = nearest_context(img, "previous")
        following = nearest_context(img, "following")
        parent_text = compact_text(img.getparent().text_content()) if img.getparent() is not None else ""
        caption = parent_text if 2 <= len(parent_text) <= 200 else ""
        context = "\n".join(filter(None, (previous, caption, following)))
        try:
            data, mime, resolved = read_image(source, source_url, input_path, timeout)
            if len(data) > 20 * 1024 * 1024:
                raise ValueError("image exceeds 20 MB")
            original_size = len(data)
            data, mime, optimized = optimize_image(
                data, mime, max_image_dimension, image_quality
            )
            digest = sha256_bytes(data)
            combined = context
            event_date, date_evidence = infer_date(combined, metadata["published_at"])
            location, location_evidence = infer_location(combined)
            entities = ["706"] if "706" in combined else []
            description = caption or previous or following or "公众号正文配图，等待 GPT 视觉描述"
            img.set("src", encode_data_uri(data, mime))
            for lazy_attr in ("data-src", "data-original", "srcset", "data-srcset"):
                img.attrib.pop(lazy_attr, None)
            img.set("data-image-id", image_id)
            img.set("data-ocr", "")
            img.set("data-description", description[:500])
            if event_date:
                img.set("data-event-date", event_date)
            if location:
                img.set("data-location", location)
            if entities:
                img.set("data-entities", ",".join(entities))
            if not compact_text(img.get("alt")):
                img.set("alt", description[:120])
            image_records.append({
                "image_id": image_id,
                "position": position,
                "mime_type": mime,
                "sha256": digest,
                "original_size_bytes": original_size,
                "embedded_size_bytes": len(data),
                "storage_optimized": optimized,
                "original_url": resolved,
                "base64_image_ref": f'[data-image-id="{image_id}"]',
                "previous_paragraph": previous or None,
                "original_caption": caption or None,
                "next_paragraph": following or None,
                "ocr_text": None,
                "ocr_status": "pending_gpt",
                "visual_description": None,
                "vision_status": "pending_gpt",
                "event_date": event_date,
                "location": location,
                "entities": entities,
                "evidence": {"event_date": date_evidence, "location": location_evidence},
            })
        except Exception as exc:  # Preserve article text even if one image fails.
            image_failures.append({"image_id": image_id, "source": source, "error": str(exc)})
            for source_attr in ("src", "data-src", "data-original", "srcset", "data-srcset"):
                img.attrib.pop(source_attr, None)
            img.set("data-image-id", image_id)
            img.set("data-capture-status", "failed")
            img.set("alt", compact_text(img.get("alt")) or "图片归档失败；原始远程依赖已移除")

    index = {
        "schema_version": SCHEMA_VERSION,
        "article": metadata,
        "images": image_records,
        "image_failures": image_failures,
        "engagement_snapshots": metrics,
        "comments": [],
        "comments_status": "not_visible",
        "capture": {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "mode": "url" if source_url else "local_html",
            "status": "partial" if image_failures else "complete",
            "image_total": len(clean_root.xpath('.//img')),
            "image_embedded": len(image_records),
        },
    }
    article_html = etree.tostring(clean_root, encoding="unicode", method="html")
    document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html_std.escape(metadata["title"])}</title>
<style>body{{max-width:760px;margin:2rem auto;padding:0 1rem;font:16px/1.8 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;color:#222}}#js_content{{visibility:visible!important;opacity:1!important}}img{{max-width:100%;height:auto}}.archive-meta{{color:#666;border-bottom:1px solid #ddd;padding-bottom:1rem;margin-bottom:2rem}}pre{{white-space:pre-wrap}}</style>
</head><body>
<header class="archive-meta"><h1>{html_std.escape(metadata["title"])}</h1><p>{html_std.escape(metadata.get("account_name") or "未知公众号")} · {html_std.escape(metadata.get("published_at") or "发布时间未知")}</p></header>
<script type="application/json" id="{INDEX_ID}">{json_script_payload(index)}</script>
{article_html}
</body></html>'''
    return document, index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url")
    source.add_argument("--input-html", type=Path)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument(
        "--max-image-dimension",
        type=int,
        default=0,
        help="Optional maximum width/height for static raster images; 0 preserves originals",
    )
    parser.add_argument("--image-quality", type=int, default=82)
    args = parser.parse_args()

    if args.max_image_dimension < 0:
        parser.error("--max-image-dimension must be 0 or greater")
    if not 1 <= args.image_quality <= 100:
        parser.error("--image-quality must be between 1 and 100")

    try:
        if args.url:
            raw = fetch_html(args.url, args.timeout)
            source_url = args.url
            input_path = None
        else:
            raw = args.input_html.read_text(encoding="utf-8")
            source_url = args.source_url
            input_path = args.input_html
        document, index = archive(
            raw,
            source_url,
            input_path,
            args.timeout,
            args.max_image_dimension,
            args.image_quality,
        )
        atomic_write(args.output, document)
        print(json.dumps({"status": "ok", "output": str(args.output), "capture": index["capture"]}, ensure_ascii=False))
        return 0
    except CaptureError as exc:
        print(json.dumps({"status": "failed", "code": exc.code, "error": str(exc)}, ensure_ascii=False))
        return 2
    except Exception as exc:
        print(json.dumps({"status": "failed", "code": "unexpected_error", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
