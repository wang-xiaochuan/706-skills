#!/usr/bin/env python3
"""Scan local WeChat image caches and stage images for 706-media ingest.

The scanner is intentionally read-only against WeChat's folders: it only
copies discovered image files into a timestamped batch under 706-media/inbox.

v2.0 — 新增 V2 加密 .dat 解密支持（msg/attach）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# --- Crypto (optional, only needed for V2 decryption) ---
try:
    from Crypto.Cipher import AES
    from Crypto.Util import Padding
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

# 活跃 706 系统已从 OneDrive 迁到 ~/dev/706-local-os，OneDrive 路径仅作回退。
# 可用环境变量 SEVENOS_WORKSPACE 覆盖。
_ACTIVE_WORKSPACE = Path.home() / "dev/706-local-os"
_LEGACY_WORKSPACE = Path.home() / "Library/CloudStorage/OneDrive-个人/2026 dev/706"
WORKSPACE = Path(
    os.environ.get(
        "SEVENOS_WORKSPACE",
        str(_ACTIVE_WORKSPACE if _ACTIVE_WORKSPACE.exists() else _LEGACY_WORKSPACE),
    )
)
DEFAULT_OUTPUT_ROOT = WORKSPACE / "706-media/inbox"
DEFAULT_OLD_ROOT = (
    Path.home()
    / "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support"
    / "com.tencent.xinWeChat/2.0b4.0.9"
)
DEFAULT_XWECHAT_ROOT = (
    Path.home()
    / "Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files"
)
DEFAULT_KEY_FILE = WORKSPACE / "706-skills/infra/wechat-dat-decrypt/wechat_image_keys.json"
DEFAULT_CHAT_HASH_MAP = WORKSPACE / "706-skills/infra/wechat-dat-decrypt/chat_hash_map.json"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".gif", ".bmp"}

# V2 .dat magic bytes
V2_MAGIC = bytes.fromhex("070856320807")


# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class Candidate:
    source_path: str
    cache_family: str
    mtime: float
    size_bytes: int
    is_thumbnail: bool
    needs_decryption: bool = False
    encryption_format: str | None = None
    chat_hash: str | None = None

@dataclass
class ManifestItem:
    original_path: str
    staged_path: str | None
    cache_family: str
    mtime: float
    mtime_iso: str
    size_bytes: int
    width: int | None
    height: int | None
    format: str
    is_thumbnail: bool
    sha256: str
    decrypted: bool = False


# ── V2 Decryption ───────────────────────────────────────────────────────────

def decrypt_v2_dat(dat_path: Path, aes_key_hex: str, xor_key: int) -> bytes | None:
    """Decrypt a V2 .dat file. Returns raw image bytes or None on failure."""
    if not HAS_CRYPTO:
        return None
    try:
        with open(dat_path, "rb") as f:
            data = f.read()
    except OSError:
        return None

    if len(data) < 15 or data[:6] != V2_MAGIC:
        return None

    try:
        aes_size, xor_size = struct.unpack_from("<LL", data, 6)
    except struct.error:
        return None

    aligned_aes_size = aes_size - ~(~aes_size % 16)  # round up to 16
    if aligned_aes_size < 0:
        return None

    total_header = 15  # 6 (magic) + 4 (aes_size) + 4 (xor_size) + 1 (padding)
    raw_size = len(data) - total_header - aligned_aes_size - xor_size
    if raw_size < 0:
        return None

    aes_data = data[total_header : total_header + aligned_aes_size]
    xor_data = data[total_header + aligned_aes_size + raw_size :]
    raw_data = data[total_header + aligned_aes_size : total_header + aligned_aes_size + raw_size]

    aes_key_bytes = aes_key_hex.encode("ascii")[:16]
    if len(aes_key_bytes) < 16:
        return None

    try:
        cipher = AES.new(aes_key_bytes, AES.MODE_ECB)
        dec_aes = Padding.unpad(cipher.decrypt(aes_data), AES.block_size)
    except (ValueError, KeyError):
        return None

    dec_xor = bytes(b ^ xor_key for b in xor_data)
    return dec_aes + raw_data + dec_xor


def is_v2_dat(path: Path) -> bool:
    """Quick check if a file is a V2-encrypted .dat image."""
    if path.suffix.lower() != ".dat":
        return False
    try:
        with open(path, "rb") as f:
            return f.read(6) == V2_MAGIC
    except OSError:
        return False


# ── Candidate discovery ─────────────────────────────────────────────────────

def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__"}]
        for name in filenames:
            path = Path(current_root) / name
            if path.suffix.lower() in IMAGE_EXTENSIONS or path.suffix.lower() == ".dat":
                yield path


def is_thumb(path: Path) -> bool:
    lowered = str(path).lower()
    return "_thumb" in lowered or "/thumb/" in lowered


def find_old_cache_candidates(root: Path, cutoff: float, include_thumbs: bool) -> list[Candidate]:
    candidates: list[Candidate] = []
    if not root.exists():
        return candidates
    for image_dir in root.glob("*/Message/MessageTemp/*/Image"):
        if not image_dir.is_dir():
            continue
        for path in iter_files(image_dir):
            try:
                stat = path.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff:
                continue
            thumb = is_thumb(path)
            if thumb and not include_thumbs:
                continue
            candidates.append(
                Candidate(
                    source_path=str(path),
                    cache_family="MessageTemp/Image",
                    mtime=stat.st_mtime,
                    size_bytes=stat.st_size,
                    is_thumbnail=thumb,
                )
            )
    return candidates


def find_xwechat_candidates(
    root: Path,
    cutoff: float,
    include_thumbs: bool,
    chat_hashes: set[str] | None = None,
) -> list[Candidate]:
    candidates: list[Candidate] = []
    if not root.exists():
        return candidates
    for thumb_dir in root.glob("*/cache/*/Message/*/Thumb"):
        if not thumb_dir.is_dir():
            continue
        chat_hash = thumb_dir.parent.name
        if chat_hashes is not None and chat_hash not in chat_hashes:
            continue
        for path in iter_files(thumb_dir):
            try:
                stat = path.stat()
            except OSError:
                continue
            if stat.st_mtime < cutoff:
                continue
            thumb = is_thumb(path)
            if thumb and not include_thumbs:
                continue
            candidates.append(
                Candidate(
                    source_path=str(path),
                    cache_family="xwechat_files/cache/Message/Thumb",
                    mtime=stat.st_mtime,
                    size_bytes=stat.st_size,
                    is_thumbnail=thumb,
                    chat_hash=chat_hash,
                )
            )
    return candidates


def find_xwechat_attach_candidates(
    root: Path,
    cutoff: float,
    include_thumbs: bool = False,
    include_originals: bool = True,
    chat_hashes: set[str] | None = None,
) -> list[Candidate]:
    """Find V2-encrypted .dat images in msg/attach/<chat_hash>/YYYY-MM/Img/.

    These are the full-resolution originals (and encrypted thumbnails).
    Requires AES+XOR keys to decrypt during staging.
    """
    candidates: list[Candidate] = []
    if not root.exists():
        return candidates

    # Walk msg/attach/<chat_hash>/YYYY-MM/Img/ for .dat files
    for wxid_dir in root.iterdir():
        if not wxid_dir.is_dir():
            continue
        attach_dir = wxid_dir / "msg" / "attach"
        if not attach_dir.is_dir():
            continue

        for chat_hash_dir in attach_dir.iterdir():
            if not chat_hash_dir.is_dir():
                continue
            chat_hash = chat_hash_dir.name
            if chat_hashes is not None and chat_hash not in chat_hashes:
                continue

            for month_dir in chat_hash_dir.iterdir():
                if not month_dir.is_dir():
                    continue
                img_dir = month_dir / "Img"
                if not img_dir.is_dir():
                    continue

                for path in img_dir.iterdir():
                    if path.suffix.lower() != ".dat":
                        continue
                    try:
                        stat = path.stat()
                    except OSError:
                        continue
                    if stat.st_mtime < cutoff:
                        continue

                    is_thumb_file = path.name.endswith("_t.dat")

                    if is_thumb_file and not include_thumbs:
                        continue
                    if not is_thumb_file and not include_originals:
                        continue

                    # Quick V2 magic check
                    if not is_v2_dat(path):
                        continue

                    candidates.append(
                        Candidate(
                            source_path=str(path),
                            cache_family="xwechat_files/msg/attach/Img",
                            mtime=stat.st_mtime,
                            size_bytes=stat.st_size,
                            is_thumbnail=is_thumb_file,
                            needs_decryption=True,
                            encryption_format="V2",
                            chat_hash=chat_hash,
                        )
                    )

    return candidates


# ── Image helpers ───────────────────────────────────────────────────────────

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_dimensions_from_bytes(data: bytes) -> tuple[int | None, int | None]:
    """Try to get dimensions from raw image bytes using PIL first, then sips."""
    import tempfile

    # Try PIL first
    try:
        from io import BytesIO
        from PIL import Image

        with Image.open(BytesIO(data)) as img:
            return int(img.width), int(img.height)
    except Exception:
        pass

    # Fallback: write to temp file, use sips
    try:
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        result = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", tmp_path],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        os.unlink(tmp_path)

        width = height = None
        for line in result.stdout.splitlines():
            if "pixelWidth:" in line:
                width = int(line.rsplit(":", 1)[1].strip())
            elif "pixelHeight:" in line:
                height = int(line.rsplit(":", 1)[1].strip())
        return width, height
    except Exception:
        return None, None


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        from PIL import Image

        with Image.open(path) as img:
            width, height = img.size
            return int(width), int(height)
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None, None

    width = height = None
    for line in result.stdout.splitlines():
        key, _, raw = line.partition(":")
        raw = raw.strip()
        # sips prints "<nil>" for encrypted/unreadable WeChat thumbnails; skip instead of crashing.
        if not raw or raw == "<nil>" or not raw.lstrip("-").isdigit():
            continue
        if "pixelWidth" in key:
            width = int(raw)
        elif "pixelHeight" in key:
            height = int(raw)
    return width, height


def detect_format(data: bytes) -> str:
    """Detect image format from magic bytes."""
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:4] == b"\x89PNG":
        return "png"
    if data[:4] == b"RIFF":
        return "webp"
    if data[:4] == b"wxgf":
        return "wxgf"
    if data[:3] == b"GIF":
        return "gif"
    return "bin"


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    value = re.sub(r"-+", "-", value).strip("-._")
    return value[:60] or "wechat-image"


def destination_name(path: Path, mtime: float, digest: str) -> str:
    timestamp = datetime.fromtimestamp(mtime).strftime("%Y%m%d-%H%M%S")
    stem = slugify(path.stem)
    return f"{timestamp}-{digest[:10]}-{stem}{path.suffix.lower()}"


def iso_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


# ── Report ──────────────────────────────────────────────────────────────────

def build_report(manifest: dict, items: list[ManifestItem]) -> str:
    lines = [
        "# WeChat Image Import Scan Report",
        "",
        f"- Batch: `{manifest['batch_id']}`",
        f"- Generated: {manifest['generated_at']}",
        f"- Dry run: {manifest['dry_run']}",
        f"- Source label: {manifest.get('source_label') or '(none)'}",
        f"- V2 decryption: {manifest.get('v2_decryption', False)}",
        f"- Items: {len(items)}",
        "",
        "| # | Cache | Thumb | Decrypted | Size KB | Dimensions | Original |",
        "|---|-------|-------|-----------|---------|------------|----------|",
    ]
    for idx, item in enumerate(items, 1):
        size_kb = round(item.size_bytes / 1024, 1)
        dims = (
            f"{item.width}x{item.height}"
            if item.width is not None and item.height is not None
            else "unknown"
        )
        original = Path(item.original_path).name
        lines.append(
            f"| {idx} | {item.cache_family} | {item.is_thumbnail} | "
            f"{item.decrypted} | {size_kb} | {dims} | `{original}` |"
        )
    lines.append("")
    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan local WeChat image caches and stage images for 706-media."
    )
    parser.add_argument("--since-minutes", type=int, default=1440)
    parser.add_argument("--max-count", type=int, default=200)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--source-label", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--include-thumbs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include thumbnail files. Defaults on.",
    )
    parser.add_argument(
        "--include-attach",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Scan msg/attach for V2-encrypted original images. Defaults on.",
    )
    parser.add_argument("--wechat-old-root", type=Path, default=DEFAULT_OLD_ROOT)
    parser.add_argument("--xwechat-root", type=Path, default=DEFAULT_XWECHAT_ROOT)
    parser.add_argument("--batch-id", default=None, help="Override batch id for tests.")

    # V2 decryption keys
    parser.add_argument("--aes-key", default=None, help="V2 AES key (16-char hex string)")
    parser.add_argument("--xor-key", default=None, type=str, help="V2 XOR key (dec or 0x hex)")
    parser.add_argument(
        "--key-file",
        type=Path,
        default=None,
        help=f"JSON file with aes_key/xor_key. Default: {DEFAULT_KEY_FILE}",
    )
    parser.add_argument(
        "--chat-name",
        action="append",
        default=[],
        help="Limit xwechat cache/attach scan to a chat name in chat_hash_map.json. Repeatable.",
    )
    parser.add_argument(
        "--chat-hash",
        action="append",
        default=[],
        help="Limit xwechat cache/attach scan to a known 32-char chat hash. Repeatable.",
    )
    parser.add_argument(
        "--chat-username",
        action="append",
        default=[],
        help="Limit xwechat cache/attach scan to md5(chat username), e.g. 12345@chatroom. Repeatable.",
    )
    parser.add_argument(
        "--chat-hash-map",
        type=Path,
        default=DEFAULT_CHAT_HASH_MAP,
        help=f"JSON chat-name to chat-hash map. Default: {DEFAULT_CHAT_HASH_MAP}",
    )
    return parser.parse_args()


def load_keys(args: argparse.Namespace) -> tuple[str | None, int | None]:
    """Load V2 decryption keys from args or key file. Returns (aes_key_hex, xor_key_int)."""
    aes_key = args.aes_key
    xor_key = args.xor_key

    # Try key file
    if (aes_key is None or xor_key is None) and args.key_file and args.key_file.exists():
        try:
            data = json.loads(args.key_file.read_text(encoding="utf-8"))
            if aes_key is None:
                aes_key = data.get("image_aes_key") or data.get("aes_key")
            if xor_key is None:
                xk = data.get("image_xor_key") or data.get("xor_key")
                if xk is not None:
                    xor_key = str(xk)
        except (OSError, json.JSONDecodeError):
            pass

    # Try default key file
    if (aes_key is None or xor_key is None) and DEFAULT_KEY_FILE.exists():
        try:
            data = json.loads(DEFAULT_KEY_FILE.read_text(encoding="utf-8"))
            if aes_key is None:
                aes_key = data.get("image_aes_key") or data.get("aes_key")
            if xor_key is None:
                xk = data.get("image_xor_key") or data.get("xor_key")
                if xk is not None:
                    xor_key = str(xk)
        except (OSError, json.JSONDecodeError):
            pass

    # Parse xor_key
    xor_key_int = None
    if xor_key is not None:
        if isinstance(xor_key, int):
            xor_key_int = xor_key
        elif isinstance(xor_key, str):
            s = xor_key.strip()
            if s.lower().startswith("0x"):
                xor_key_int = int(s, 16)
            else:
                xor_key_int = int(s)

    # Validate
    if aes_key is not None:
        aes_key = aes_key.strip()
        if len(aes_key) < 16:
            print(f"Warning: AES key too short ({len(aes_key)} chars), need 16", file=sys.stderr)
            aes_key = None

    return aes_key, xor_key_int


def load_chat_hashes(args: argparse.Namespace) -> tuple[set[str] | None, list[str]]:
    """Resolve optional chat filters from explicit hashes and chat_hash_map.json."""
    requested_names = [name.strip() for name in args.chat_name if name.strip()]
    requested_hashes = {value.strip() for value in args.chat_hash if value.strip()}
    requested_usernames = [value.strip() for value in args.chat_username if value.strip()]
    notes: list[str] = []

    if not requested_names and not requested_hashes and not requested_usernames:
        return None, notes

    resolved: set[str] = set(requested_hashes)
    missing: list[str] = []

    for username in requested_usernames:
        resolved.add(hashlib.md5(username.encode()).hexdigest())

    chat_map_path = args.chat_hash_map
    chat_map = {}
    if requested_names and chat_map_path.exists():
        try:
            data = json.loads(chat_map_path.read_text(encoding="utf-8"))
            chat_map = data.get("chats", data)
        except (OSError, json.JSONDecodeError) as exc:
            notes.append(f"Warning: could not read chat hash map {chat_map_path}: {exc}")

    for name in requested_names:
        entry = chat_map.get(name) if isinstance(chat_map, dict) else None
        chat_hash = None
        if isinstance(entry, str):
            chat_hash = entry
        elif isinstance(entry, dict):
            chat_hash = entry.get("chat_hash")
        if chat_hash:
            resolved.add(str(chat_hash).strip())
        else:
            missing.append(name)

    if missing:
        notes.append(
            "Warning: chat name(s) not found in chat hash map: " + ", ".join(missing)
        )

    if not resolved:
        return set(), notes
    return resolved, notes


def main() -> int:
    args = parse_args()
    if args.since_minutes <= 0:
        print("--since-minutes must be positive", file=sys.stderr)
        return 2
    if args.max_count <= 0:
        print("--max-count must be positive", file=sys.stderr)
        return 2

    # Load V2 keys
    aes_key, xor_key = load_keys(args)
    chat_hashes, chat_filter_notes = load_chat_hashes(args)
    for note in chat_filter_notes:
        print(note, file=sys.stderr)
    if chat_hashes == set():
        print("No chat hashes resolved; scan will return no xwechat candidates.", file=sys.stderr)

    v2_available = HAS_CRYPTO and aes_key is not None and xor_key is not None
    if args.include_attach and not v2_available:
        if not HAS_CRYPTO:
            print("Note: pycryptodome not installed, V2 decryption disabled", file=sys.stderr)
        elif aes_key is None:
            print("Note: No AES key provided (--aes-key or --key-file), V2 decryption disabled", file=sys.stderr)
        elif xor_key is None:
            print("Note: No XOR key provided (--xor-key or --key-file), V2 decryption disabled", file=sys.stderr)

    now = datetime.now()
    cutoff = now.timestamp() - args.since_minutes * 60
    batch_id = args.batch_id or now.strftime("%Y%m%d-%H%M%S")

    # Phase 1: Discover candidates from all cache families
    candidates: list[Candidate] = []

    # Old cache has no chat_hash path segment, so skip it when filtering by chat.
    if chat_hashes is None:
        candidates.extend(
            find_old_cache_candidates(args.wechat_old_root, cutoff, args.include_thumbs)
        )

    # New cache: unencrypted thumbnails
    candidates.extend(
        find_xwechat_candidates(
            args.xwechat_root,
            cutoff,
            args.include_thumbs,
            chat_hashes=chat_hashes,
        )
    )

    # New attach: V2-encrypted originals (and optionally thumbnails)
    if args.include_attach:
        candidates.extend(
            find_xwechat_attach_candidates(
                args.xwechat_root,
                cutoff,
                include_thumbs=False,  # _t.dat from attach are redundant with cache/Thumb
                include_originals=True,
                chat_hashes=chat_hashes,
            )
        )

    candidates.sort(key=lambda item: item.mtime, reverse=True)

    # Phase 2: Stage images
    items: list[ManifestItem] = []
    seen_hashes: set[str] = set()
    batch_dir = args.output_root / "wechat-image-import" / batch_id
    image_dir = batch_dir / "images"

    if not args.dry_run:
        image_dir.mkdir(parents=True, exist_ok=True)

    decrypt_errors = 0
    for candidate in candidates:
        if len(items) >= args.max_count:
            break

        source = Path(candidate.source_path)

        # For V2 encrypted files, decrypt and hash the result
        if candidate.needs_decryption and candidate.encryption_format == "V2" and v2_available:
            decrypted = decrypt_v2_dat(source, aes_key, xor_key)  # type: ignore[arg-type]
            if decrypted is None:
                decrypt_errors += 1
                continue
            digest = sha256_bytes(decrypted)
            content_bytes = decrypted
            fmt = detect_format(decrypted)
        else:
            try:
                digest = sha256_file(source)
            except OSError:
                continue
            content_bytes = None
            fmt = source.suffix.lower().lstrip(".")

        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)

        # Dimensions
        if content_bytes is not None:
            width, height = image_dimensions_from_bytes(content_bytes)
        else:
            width, height = image_dimensions(source)

        # Stage
        dest_path: Path | None = None
        if not args.dry_run:
            dest_name = destination_name(source, candidate.mtime, digest)
            # Use detected format extension
            if fmt and fmt != "bin":
                dest_name = dest_name.rsplit(".", 1)[0] + f".{fmt}"
            dest_path = image_dir / dest_name
            suffix = 2
            while dest_path.exists():
                stem_part = dest_name.rsplit(".", 1)[0]
                ext_part = dest_name.rsplit(".", 1)[1] if "." in dest_name else "bin"
                dest_path = image_dir / f"{stem_part}-{suffix}.{ext_part}"
                suffix += 1

            if content_bytes is not None:
                dest_path.write_bytes(content_bytes)
            else:
                shutil.copy2(source, dest_path)

        items.append(
            ManifestItem(
                original_path=str(source),
                staged_path=str(dest_path) if dest_path else None,
                cache_family=candidate.cache_family,
                mtime=candidate.mtime,
                mtime_iso=iso_from_timestamp(candidate.mtime),
                size_bytes=len(content_bytes) if content_bytes is not None else candidate.size_bytes,
                width=width,
                height=height,
                format=fmt,
                is_thumbnail=candidate.is_thumbnail,
                sha256=digest,
                decrypted=candidate.needs_decryption and v2_available,
            )
        )

    # Phase 3: Build manifest
    manifest = {
        "schema_version": 2,
        "kind": "wechat-image-import",
        "batch_id": batch_id,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "dry_run": bool(args.dry_run),
        "source_label": args.source_label,
        "since_minutes": args.since_minutes,
        "max_count": args.max_count,
        "include_thumbs": bool(args.include_thumbs),
        "include_attach": bool(args.include_attach),
        "chat_names": args.chat_name,
        "chat_hashes": sorted(chat_hashes) if chat_hashes is not None else None,
        "chat_hash_map": str(args.chat_hash_map),
        "v2_decryption": v2_available,
        "output_root": str(args.output_root),
        "batch_dir": str(batch_dir) if not args.dry_run else None,
        "wechat_old_root": str(args.wechat_old_root),
        "xwechat_root": str(args.xwechat_root),
        "candidate_count": len(candidates),
        "item_count": len(items),
        "decrypt_errors": decrypt_errors,
        "items": [asdict(item) for item in items],
    }

    report = build_report(manifest, items)
    if args.dry_run:
        print(report)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    else:
        (batch_dir / "_manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (batch_dir / "_scan-report.md").write_text(report, encoding="utf-8")
        print(f"Staged {len(items)} images into {batch_dir}")
        print(f"Manifest: {batch_dir / '_manifest.json'}")
        if decrypt_errors > 0:
            print(f"⚠️  {decrypt_errors} decryption errors (skipped)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
