#!/usr/bin/env python3
"""Upload images to freeimage.host and return public URLs.

Usage:
    python upload_image.py image1.jpg [image2.png ...]

Output:
    image1.jpg → https://iili.io/xxx.jpg
    image2.png → https://iili.io/yyy.png

Falls back to catbox.moe if freeimage.host fails.
"""

import sys
import json
import subprocess
import os


FREEIMAGE_API = "https://freeimage.host/api/1/upload"
FREEIMAGE_KEY = "6d207e02198a847aa98d0a2a901485a5"
CATBOX_API = "https://catbox.moe/user/api.php"


def upload_freeimage(filepath: str) -> str | None:
    """Upload to freeimage.host. Returns URL or None on failure."""
    try:
        result = subprocess.run(
            [
                "curl", "-s", "-X", "POST", FREEIMAGE_API,
                "-F", f"key={FREEIMAGE_KEY}",
                "-F", f"source=@{filepath}",
                "-F", "format=json",
            ],
            capture_output=True, text=True, timeout=60,
        )
        data = json.loads(result.stdout)
        if data.get("status_code") == 200:
            return data["image"]["url"]
    except Exception as e:
        print(f"  freeimage.host error: {e}", file=sys.stderr)
    return None


def upload_catbox(filepath: str) -> str | None:
    """Upload to catbox.moe. Returns URL or None on failure."""
    try:
        result = subprocess.run(
            [
                "curl", "-s",
                "-F", "reqtype=fileupload",
                "-F", f"fileToUpload=@{filepath}",
                CATBOX_API,
            ],
            capture_output=True, text=True, timeout=60,
        )
        url = result.stdout.strip()
        if url.startswith("https://"):
            return url
    except Exception as e:
        print(f"  catbox.moe error: {e}", file=sys.stderr)
    return None


def upload(filepath: str) -> str:
    """Upload image with fallback chain. Returns URL or error string."""
    if not os.path.exists(filepath):
        return f"ERROR: file not found: {filepath}"

    # Try freeimage.host first
    url = upload_freeimage(filepath)
    if url:
        return url

    # Fallback to catbox.moe
    print(f"  freeimage.host failed, trying catbox.moe...", file=sys.stderr)
    url = upload_catbox(filepath)
    if url:
        return url

    return "ERROR: all upload services failed"


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_image.py image1.jpg [image2.png ...]")
        sys.exit(1)

    for filepath in sys.argv[1:]:
        url = upload(filepath)
        print(f"{filepath} → {url}")


if __name__ == "__main__":
    main()
