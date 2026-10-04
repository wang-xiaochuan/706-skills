from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
import discover_articles  # noqa: E402
import wewe_feed_manager  # noqa: E402
import archive_lib  # noqa: E402
PNG_DATA_URI = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="


def run_script(name: str, *args: str, env: dict | None = None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )


def sample_html() -> str:
    return f'''<!doctype html><html><head>
    <meta property="og:title" content="706 东京活动回顾">
    <meta name="author" content="706青年空间">
    </head><body>
    <h1 id="activity-name">706 东京活动回顾</h1>
    <span id="js_name">706青年空间</span><span id="publish_time">2026-07-04</span>
    <div id="js_content" class="rich_media_content">
      <p>2026年7月2日，706在东京举办了一场社区交流活动。</p>
      <p><img data-src="{PNG_DATA_URI}"></p>
      <p>参与者随后围绕跨城市社区网络展开讨论。</p>
    </div></body></html>'''


def hidden_sample_html() -> str:
    return sample_html().replace(
        'class="rich_media_content"',
        'class="rich_media_content" style="visibility: hidden; opacity: 0;"',
    )


class ArticleHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/sample-article":
            data = sample_html().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        else:
            self.send_response(404)
            self.end_headers()
            return


class MockResponse:
    def __init__(self, text: str, url: str = "https://mp.weixin.qq.com/s/example"):
        self.text = text
        self.content = text.encode()
        self.apparent_encoding = "utf-8"
        self.encoding = "utf-8"
        self.url = url

    def raise_for_status(self):
        return None


class FakeSogouSession:
    def get(self, url, **_kwargs):
        if "/link?" in url:
            return MockResponse("<script>var url=''; url += 'https://mp.'; url += 'weixin.qq.com/s/example';</script>", url)
        return MockResponse('''<html><body><ul class="news-list"><li>
        <h3><a href="/link?token=test">七月活动</a></h3>
        <div class="s-p"><span>706青年空间</span><span><script>document.write(timeConvert('1784614676'))</script></span></div>
        </li></ul></body></html>''', url)


class SkillV1Tests(unittest.TestCase):
    def test_archive_reveals_wechat_prerendered_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.html"
            output = root / "archive.html"
            source.write_text(hidden_sample_html(), encoding="utf-8")
            archived = run_script(
                "archive_article.py", "--input-html", str(source), "--output", str(output),
            )
            self.assertEqual(archived.returncode, 0, archived.stdout + archived.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn("visibility: visible !important", text)
            self.assertNotIn("visibility: hidden", text)
            self.assertNotIn("opacity: 0", text)
            validated = run_script("validate_archive.py", str(output))
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

    def test_validator_rejects_hidden_article_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.html"
            output = root / "archive.html"
            source.write_text(sample_html(), encoding="utf-8")
            archived = run_script(
                "archive_article.py", "--input-html", str(source), "--output", str(output),
            )
            self.assertEqual(archived.returncode, 0, archived.stdout + archived.stderr)
            text = output.read_text(encoding="utf-8").replace(
                "visibility: visible !important; opacity: 1 !important;",
                "visibility: hidden; opacity: 0;",
                1,
            )
            output.write_text(text, encoding="utf-8")
            validated = run_script("validate_archive.py", str(output))
            self.assertEqual(validated.returncode, 1, validated.stdout + validated.stderr)
            self.assertIn("article body root is hidden", validated.stdout)

    def test_large_base64_attribute_is_not_truncated(self):
        payload = "A" * (11 * 1024 * 1024)
        doc = archive_lib.parse_html(
            f'<html><body><div id="js_content"><img data-image-id="img-001" '
            f'src="data:image/jpeg;base64,{payload}"></div></body></html>'
        )
        nodes = doc.xpath('//img[@data-image-id="img-001"]')
        self.assertEqual(len(nodes), 1)
        self.assertTrue(nodes[0].get("src", "").endswith(payload))

    def test_archive_validate_query_and_extract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.html"
            output = root / "archive.html"
            extracted = root / "images"
            source.write_text(sample_html(), encoding="utf-8")

            archived = run_script(
                "archive_article.py", "--input-html", str(source),
                "--source-url", "https://mp.weixin.qq.com/s/example",
                "--output", str(output),
            )
            self.assertEqual(archived.returncode, 0, archived.stdout + archived.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn("data:image/png;base64,", text)
            self.assertIn('data-event-date="2026-07-02"', text)
            self.assertIn('data-location="东京"', text)
            self.assertIn('id="wechat-article-index"', text)

            validated = run_script("validate_archive.py", str(output))
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            self.assertTrue(json.loads(validated.stdout)["passed"])

            queried = run_script(
                "query_archive.py", str(output), "706 东京",
                "--date", "2026-07-02", "--extract-dir", str(extracted),
            )
            self.assertEqual(queried.returncode, 0, queried.stdout + queried.stderr)
            result = json.loads(queried.stdout)
            self.assertEqual(result["count"], 1)
            self.assertTrue(Path(result["results"][0]["extracted_image"]).exists())

    def test_block_page_fails_closed_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "blocked.html"
            output = root / "should-not-exist.html"
            source.write_text("<html><body><h1>环境异常</h1><p>完成验证后即可继续访问</p></body></html>", encoding="utf-8")
            result = run_script("archive_article.py", "--input-html", str(source), "--output", str(output))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["code"], "environment_abnormal")
            self.assertFalse(output.exists())

    def test_failed_image_never_leaves_remote_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.html"
            output = root / "archive.html"
            source.write_text('''<html><head><title>缺图测试</title></head><body>
            <div id="js_content"><p>这是一段足够长的公众号正文，用于验证图片失败时仍然生成完全离线的归档。</p>
            <p><img src="missing-image.jpg" alt="原图"></p></div></body></html>''', encoding="utf-8")
            archived = run_script(
                "archive_article.py", "--input-html", str(source),
                "--output", str(output),
            )
            self.assertEqual(archived.returncode, 0, archived.stdout + archived.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertNotIn('src="missing-image.jpg"', text)
            self.assertIn('data-capture-status="failed"', text)
            self.assertEqual(json.loads(archived.stdout)["capture"]["status"], "partial")
            validated = run_script("validate_archive.py", str(output))
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

    def test_image_only_article_is_archived(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "image-only.html"
            output = root / "archive.html"
            source.write_text(f'''<html><head><title>纯图片图文</title></head><body>
            <div id="js_content"><img data-src="{PNG_DATA_URI}"></div>
            </body></html>''', encoding="utf-8")
            archived = run_script(
                "archive_article.py", "--input-html", str(source),
                "--output", str(output),
            )
            self.assertEqual(archived.returncode, 0, archived.stdout + archived.stderr)
            self.assertEqual(json.loads(archived.stdout)["capture"]["image_embedded"], 1)
            validated = run_script("validate_archive.py", str(output))
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)

    def test_web_candidate_verifies_account_and_date(self):
        with patch.object(discover_articles.requests, "get", return_value=MockResponse(sample_html())):
            accepted, failure = discover_articles.verify_candidate(
                {"url": "https://mp.weixin.qq.com/s/example"}, "706青年空间",
                discover_articles.date(2026, 7, 1), discover_articles.date(2026, 7, 31), 30,
            )
        self.assertIsNone(failure)
        self.assertEqual(accepted["published_at"], "2026-07-04")
        self.assertEqual(accepted["account_name"], "706青年空间")

    def test_web_candidate_rejects_account_mismatch(self):
        with patch.object(discover_articles.requests, "get", return_value=MockResponse(sample_html())):
            accepted, failure = discover_articles.verify_candidate(
                {"url": "https://mp.weixin.qq.com/s/example"}, "另一个公众号",
                discover_articles.date(2026, 7, 1), discover_articles.date(2026, 7, 31), 30,
            )
        self.assertIsNone(accepted)
        self.assertEqual(failure["code"], "account_mismatch")

    def test_direct_http_sogou_discovery_resolves_frontend_url(self):
        with patch.object(discover_articles.requests, "Session", return_value=FakeSogouSession()):
            queries, candidates = discover_articles.sogou_candidates(
                "706青年空间", discover_articles.date(2026, 7, 1),
                discover_articles.date(2026, 7, 31), 30, 1,
            )
        self.assertEqual(queries, ["706青年空间 2026年7月"])
        self.assertEqual(candidates[0]["url"], "https://mp.weixin.qq.com/s/example")
        self.assertEqual(candidates[0]["search_published_at"], "2026-07-21")

    def test_wewe_candidate_file_groups_only_valid_article_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidates.json"
            path.write_text(json.dumps({"results": [
                {"account": "706杭州", "url": "https://mp.weixin.qq.com/s/example"},
                {"account": "706杭州", "url": "https://example.com/not-wechat"},
                {"account": "706柏林", "url": "https://mp.weixin.qq.com/s/berlin"},
            ]}, ensure_ascii=False), encoding="utf-8")
            grouped = wewe_feed_manager.load_seed_candidates(path)
        self.assertEqual(grouped["706杭州"], ["https://mp.weixin.qq.com/s/example"])
        self.assertEqual(grouped["706柏林"], ["https://mp.weixin.qq.com/s/berlin"])

    def test_wewe_local_service_does_not_require_auth_code(self):
        self.assertTrue(wewe_feed_manager.is_loopback_base_url("http://127.0.0.1:4000"))
        self.assertTrue(wewe_feed_manager.is_loopback_base_url("http://localhost:4000"))
        self.assertFalse(wewe_feed_manager.is_loopback_base_url("https://wewe.example.com"))
        client = wewe_feed_manager.WeWeClient("http://127.0.0.1:4000", None, 30)
        self.assertEqual(client.headers, {})

    def test_wewe_add_requires_exact_account_name(self):
        class FakeClient:
            def __init__(self):
                self.added = []

            def identify(self, url):
                return [{"id": "mp-1", "name": "706杭州", "intro": "杭州", "updateTime": 1}]

            def add(self, feed):
                self.added.append(feed)

        client = FakeClient()
        rejected = wewe_feed_manager.process_account(
            "706东京", ["https://mp.weixin.qq.com/s/example"], client, 30, 1, True, set()
        )
        self.assertEqual(rejected["status"], "candidate_unusable")
        self.assertEqual(client.added, [])
        accepted = wewe_feed_manager.process_account(
            "706杭州", ["https://mp.weixin.qq.com/s/example"], client, 30, 1, True, set()
        )
        self.assertEqual(accepted["status"], "added")
        self.assertEqual(len(client.added), 1)

    def test_wewe_rejects_transient_sogou_signed_url(self):
        class FakeClient:
            def identify(self, url):
                raise AssertionError("transient URL must not be sent to WeWe")

        row = wewe_feed_manager.process_account(
            "706深圳",
            ["https://mp.weixin.qq.com/s?src=11&signature=temporary"],
            FakeClient(), 30, 1, True, set(),
        )
        self.assertEqual(row["status"], "candidate_unusable")
        self.assertEqual(row["rejected"][0]["error"], "noncanonical_search_url")

    def test_archive_range_creates_collection_and_valid_article(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), ArticleHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                manifest = root / "manifest.json"
                output = root / "archive"
                manifest.write_text(json.dumps({
                    "status": "ok",
                    "provider": "fixture",
                    "coverage": "account_history_complete",
                    "account_query": "706青年空间",
                    "date_range": {"start": "2026-07-01", "end": "2026-07-31"},
                    "articles": [{
                        "title": "706 东京活动回顾",
                        "url": f"http://127.0.0.1:{server.server_port}/sample-article",
                        "published_at": "2026-07-04",
                    }],
                }, ensure_ascii=False), encoding="utf-8")
                result = run_script(
                    "archive_range.py", "--output-dir", str(output), "--manifest", str(manifest),
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue((output / "_collection.html").exists())
                articles = [path for path in output.glob("*.html") if path.name != "_collection.html"]
                self.assertEqual(len(articles), 1)
                validated = run_script("validate_archive.py", str(articles[0]))
                self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
                validated_batch = run_script("validate_archive.py", str(output))
                self.assertEqual(validated_batch.returncode, 0, validated_batch.stdout + validated_batch.stderr)
        finally:
            server.shutdown()
            server.server_close()

    def test_gpt_image_extract_and_annotation_writeback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.html"
            archive = root / "archive.html"
            images = root / "images"
            task_manifest = root / "tasks.json"
            annotations = root / "annotations.json"
            source.write_text(sample_html(), encoding="utf-8")
            created = run_script("archive_article.py", "--input-html", str(source), "--output", str(archive))
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            extracted = run_script(
                "extract_images_for_gpt.py", str(archive), "--output-dir", str(images),
                "--manifest", str(task_manifest),
            )
            self.assertEqual(extracted.returncode, 0, extracted.stdout + extracted.stderr)
            task = json.loads(task_manifest.read_text(encoding="utf-8"))["tasks"][0]
            annotations.write_text(json.dumps({"annotations": [{
                "html": task["html"], "image_id": task["image_id"],
                "visual_description": "706 东京社区活动现场",
                "ocr_text": "706 TOKYO", "event_date": "2026-07-02",
                "location": "东京", "entities": ["706"],
            }]}, ensure_ascii=False), encoding="utf-8")
            applied = run_script("apply_gpt_annotations.py", "--annotations", str(annotations))
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            text = archive.read_text(encoding="utf-8")
            self.assertIn("706 东京社区活动现场", text)
            self.assertIn("captured_by_gpt", text)
            validated = run_script("validate_archive.py", str(archive))
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)


if __name__ == "__main__":
    unittest.main()
