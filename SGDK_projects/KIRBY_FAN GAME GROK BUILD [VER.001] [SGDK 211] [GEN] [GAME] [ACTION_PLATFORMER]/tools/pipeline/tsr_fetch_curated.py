#!/usr/bin/env python3
"""Download curated Spriters Resource assets into reference_archive (lab only).

Reads catalog/selection_v1.json, fetches each asset page, resolves media URL,
saves under raw/<folder>/<filename>, writes MANIFEST.json with sha256.

Fan-study project: may install to res/ via tsr_install_to_res.py. See LEGAL.md. See data/reference_archive/LEGAL.md.

Usage:
  python3 tools/pipeline/tsr_fetch_curated.py
  python3 tools/pipeline/tsr_fetch_curated.py --only 49192,52859
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "data" / "reference_archive"
CATALOG = ARCHIVE / "catalog" / "selection_v1.json"
RAW = ARCHIVE / "raw"
VERSIONS = ARCHIVE / "versions" / "v001_raw"
MANIFEST_PATH = ARCHIVE / "MANIFEST.json"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 GrokBuild-RefArchive/1.0"
BASE = "https://www.spriters-resource.com"


def fetch(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,image/png,image/*,*/*",
            "Referer": BASE + "/",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def resolve_media_url(page_url: str, asset_id: int) -> str:
    html = fetch(page_url).decode("utf-8", "replace")
    # download href or img media/assets
    patterns = [
        rf'href="(/media/assets/\d+/{asset_id}\.(?:png|gif|jpg))[^"]*"',
        rf'src="(/media/assets/\d+/{asset_id}\.(?:png|gif|jpg))[^"]*"',
        rf'(/media/assets/\d+/{asset_id}\.(?:png|gif|jpg))',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.I)
        if m:
            path = m.group(1)
            if path.startswith("http"):
                return path
            return BASE + path
    raise RuntimeError(f"media URL not found for asset {asset_id} on {page_url}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=str, default="", help="comma-separated asset ids")
    ap.add_argument("--sleep", type=float, default=0.8, help="delay between downloads")
    args = ap.parse_args()

    catalog = json.loads(CATALOG.read_text())
    only = {int(x) for x in args.only.split(",") if x.strip()} if args.only else None

    RAW.mkdir(parents=True, exist_ok=True)
    VERSIONS.mkdir(parents=True, exist_ok=True)

    manifest: dict = {
        "ship_allowed": False,
        "created": datetime.now(timezone.utc).isoformat(),
        "source": "https://www.spriters-resource.com/",
        "legal": "data/reference_archive/LEGAL.md",
        "plan": "doc/plans/PARALLEL_TSR_REFERENCE_LEARNING_PLAN.md",
        "assets": [],
    }

    for entry in catalog["assets"]:
        aid = int(entry["id"])
        if only is not None and aid not in only:
            continue
        folder = RAW / entry["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / entry["filename"]
        page = entry["page"]
        print(f"[{aid}] {entry['name']} …", flush=True)
        try:
            media = resolve_media_url(page, aid)
            data = fetch(media)
            # normalize extension from actual bytes if gif
            if data[:6] in (b"GIF87a", b"GIF89a") and dest.suffix.lower() != ".gif":
                dest = dest.with_suffix(".gif")
                entry = dict(entry)
                entry["filename"] = dest.name
            dest.write_bytes(data)
            # versioned immutable copy
            vdest = VERSIONS / entry["folder"]
            vdest.mkdir(parents=True, exist_ok=True)
            (vdest / dest.name).write_bytes(data)
            rec = {
                **entry,
                "media_url": media,
                "local_path": str(dest.relative_to(ROOT)),
                "bytes": len(data),
                "sha256": sha256(data),
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
                "status": "ok",
            }
            print(f"  OK {dest.name} {len(data)} B sha={rec['sha256'][:12]}…")
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, TimeoutError) as e:
            rec = {**entry, "status": "error", "error": str(e)}
            print(f"  FAIL {e}")
        manifest["assets"].append(rec)
        time.sleep(args.sleep)

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")
    ok = sum(1 for a in manifest["assets"] if a.get("status") == "ok")
    fail = sum(1 for a in manifest["assets"] if a.get("status") != "ok")
    print(f"\nMANIFEST {MANIFEST_PATH}  ok={ok} fail={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
