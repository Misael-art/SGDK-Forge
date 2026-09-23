#!/usr/bin/env python3
"""Remap the clock atlas onto the shared PAL1 HUD palette.

The original clock sheet carries a private palette.  At runtime PAL1 is
owned by the HUD bar, so the sheet's dominant background index became an
opaque rectangle.  The mask is derived from the source index (not from an
RGB guess): index 11 is the documented background and becomes sprite index 0.
All remaining pixels are mapped to the nearest colour in the shared palette,
keeping dark glyph contours available at PAL1 index 11.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "res/sprite/hud/clock_digits_window.png"
HUD_PALETTE = ROOT / "res/sprite/hud/energy_yellow.png"
OUTPUT = ROOT / "res/sprite/hud/clock_digits_transparent.png"
REPORT = Path(__file__).resolve().parent / "clock_mask_report.json"
BACKGROUND_INDEX = 11


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def palette16(image: Image.Image) -> list[tuple[int, int, int]]:
    raw = image.getpalette()
    return [tuple(raw[i * 3 : i * 3 + 3]) for i in range(16)]


def main() -> None:
    src = Image.open(SOURCE).convert("P")
    shared = palette16(Image.open(HUD_PALETTE).convert("P"))
    src_palette = palette16(src)
    out = Image.new("P", src.size)
    out.putpalette([v for rgb in shared for v in rgb] + [0] * (3 * 240))
    sp, dp = src.load(), out.load()
    mask_pixels = 0
    for y in range(src.height):
        for x in range(src.width):
            source_index = int(sp[x, y])
            if source_index == BACKGROUND_INDEX:
                dp[x, y] = 0
                mask_pixels += 1
                continue
            rgb = src_palette[source_index]
            # Index 0 is reserved for transparency; use opaque PAL1 entries
            # for every visible contour/highlight.
            best = min(range(1, 16), key=lambda i: sum((rgb[k] - shared[i][k]) ** 2 for k in range(3)))
            dp[x, y] = best
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUTPUT, format="PNG")
    report = {
        "schema_version": "1.0.0",
        "asset": "hud_clock_digits",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "shared_palette": str(HUD_PALETTE.relative_to(ROOT)),
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": sha256(OUTPUT),
        "dimensions": list(src.size),
        "source_background_index": BACKGROUND_INDEX,
        "transparent_output_index": 0,
        "masked_pixels": mask_pixels,
        "source_indices": dict(Counter(src.getdata())),
        "output_indices": dict(Counter(out.getdata())),
        "palette_owner": "PAL1_spr_hud_energy_y",
        "claim_ceiling": "transparent_sprite_contract",
        "visual_review_required": True,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
