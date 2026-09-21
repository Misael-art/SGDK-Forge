#!/usr/bin/env python3
"""Build a tiny authored-source water reflection animation for BGB2.

The frames are cut from the reviewed native stage output.  Only the stage's
bright water indices are retained; the surrounding pixels become transparent.
This is a composited derivative of authored stage pixels, not runtime drawing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "res/gfx/bgb2.png"
OUTPUT = ROOT / "res/sprite/stage/water_glint.png"
REPORT = ROOT / "rascunho/stage2_water_glint_report.json"

FRAME_W = 16
FRAME_H = 8
FRAME_ORIGINS = [(220, 160), (236, 160), (252, 160), (268, 160)]
# These are the two light teal entries in the BGB2 palette.  Keeping the
# palette indices identical lets the sprite use PAL0 without a new CRAM slot.
WATER_HIGHLIGHTS = {3, 4}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = Image.open(SOURCE).convert("P")
    palette = source.getpalette()
    out = Image.new("P", (FRAME_W * len(FRAME_ORIGINS), FRAME_H), 0)
    out.putpalette(palette)
    src = source.load()
    dst = out.load()

    for frame, (ox, oy) in enumerate(FRAME_ORIGINS):
        for y in range(FRAME_H):
            for x in range(FRAME_W):
                idx = src[ox + x, oy + y]
                # Preserve only short highlight strokes.  A pixel is kept if
                # it belongs to the selected water colour and touches another
                # selected pixel horizontally or vertically.
                if idx in WATER_HIGHLIGHTS:
                    neighbours = []
                    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                        if 0 <= nx < FRAME_W and 0 <= ny < FRAME_H:
                            neighbours.append(src[ox + nx, oy + ny] in WATER_HIGHLIGHTS)
                    if any(neighbours):
                        dst[frame * FRAME_W + x, y] = idx

    out.info["transparency"] = 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUTPUT)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "asset": str(OUTPUT.relative_to(ROOT)),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "output_sha256": sha256(OUTPUT),
        "frames": len(FRAME_ORIGINS),
        "cell_px": [FRAME_W, FRAME_H],
        "palette_slots": sorted(WATER_HIGHLIGHTS),
        "source_kind": "procedural_composed_from_authored",
        "acceptance_status": "placeholder",
        "runtime_role": "BGB2 ambient water glint",
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "sha256": sha256(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
