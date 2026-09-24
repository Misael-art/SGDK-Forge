#!/usr/bin/env python3
"""Translate starfield_v02b.jpg into a Mega Drive 320x224 indexed plate.

The AI source is composition only. The plate is rebuilt on an 8x8 grid with a
16-color 9-bit palette. PAL0[1] and PAL0[2] stay the pulsing star slots.
Index 0 is black backdrop. Not final; placeholder pending human review.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent / "raw" / "starfield_v02b.jpg"
OUT_RES = ROOT / "res" / "branding" / "starfield_320x224.png"
OUT_PROC = ROOT / "data" / "processed" / "branding_v2" / "starfield_v02.png"
REPORT = Path(__file__).resolve().parent / "starfield_v02_translate_report.json"

W, H = 320, 224
PAL = [
    (0x00, 0x00, 0x00),  # 0 backdrop
    (0x66, 0x88, 0xAA),  # 1 dim star (pulsed)
    (0xCC, 0xEE, 0xEE),  # 2 bright star (pulsed)
    (0x00, 0x00, 0x22),  # 3 deep navy field
    (0x00, 0x00, 0x44),  # 4 navy lift
    (0x22, 0x00, 0x44),  # 5 violet
    (0x44, 0x00, 0x44),  # 6 magenta dust
    (0x66, 0x22, 0x44),  # 7 warm dust
    (0x22, 0x00, 0x22),  # 8 column shadow
    (0x44, 0x22, 0x44),  # 9 column mid
    (0x66, 0x44, 0x66),  # 10 column lift
    (0x22, 0x22, 0x44),  # 11 field grain
    (0x88, 0x88, 0xAA),  # 12 cluster
    (0xAA, 0xAA, 0xCC),  # 13 pale
    (0xCC, 0xAA, 0x66),  # 14 gold
    (0xEE, 0xEE, 0xEE),  # 15 white core
]


def lum(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def unique_tiles(img: Image.Image) -> int:
    px = img.load()
    seen: set[bytes] = set()
    for ty in range(0, H, 8):
        for tx in range(0, W, 8):
            cells = []
            for y in range(8):
                for x in range(8):
                    cells.append(px[tx + x, ty + y])
            seen.add(bytes(cells))
    return len(seen)


def main() -> None:
    src = Image.open(SRC).convert("RGB")
    # Center-crop 16:9 to 10:7 then nearest to native.
    sw, sh = src.size
    target_ratio = W / H
    if sw / sh > target_ratio:
        nw = int(sh * target_ratio)
        left = (sw - nw) // 2
        src = src.crop((left, 0, left + nw, sh))
    else:
        nh = int(sw / target_ratio)
        top = (sh - nh) // 2
        src = src.crop((0, top, sw, top + nh))
    src = src.resize((W, H), Image.NEAREST)
    sp = src.load()

    out = Image.new("P", (W, H))
    out.putpalette([c for rgb in PAL for c in rgb] + [0] * (3 * (256 - 16)))
    op = out.load()

    # Navy field, not empty black. A 24px violet dither at the bottom hints
    # at heat without drawing a planet floor.
    band0 = H - 24
    for y in range(H):
        for x in range(W):
            op[x, y] = 3
    for y in range(band0, H):
        for x in range(W):
            checker = ((x >> 1) & 1) ^ ((y >> 1) & 1)
            op[x, y] = 5 if checker else 4

    # Bright stars from the source, plus a sparse authored field so Act I reads.
    stars: list[tuple[int, int, float]] = []
    for y in range(4, band0 - 6):
        for x in range(W):
            lv = lum(sp[x, y])
            if lv >= 90:
                stars.append((x, y, lv))
    stars.sort(key=lambda t: t[2], reverse=True)
    placed: list[tuple[int, int]] = []
    for x, y, lv in stars[:80]:
        if any(abs(x - px) < 6 and abs(y - py) < 6 for px, py in placed):
            continue
        placed.append((x, y))
        gold = lv > 200 and ((x * 3 + y) & 7) == 0
        core = 15 if lv > 190 else 2
        ring = 14 if gold else 1
        op[x, y] = core
        if 0 < x < W - 1 and 0 < y < H - 1 and lv > 150:
            op[x - 1, y] = ring
            op[x + 1, y] = ring
            op[x, y - 1] = ring
            op[x, y + 1] = ring

    dim = 0
    seed = [
        (18, 22), (46, 14), (72, 36), (98, 10), (150, 18), (186, 28),
        (214, 12), (246, 34), (278, 20), (302, 40), (28, 58), (60, 74),
        (88, 52), (168, 48), (198, 66), (232, 54), (268, 72), (296, 60),
        (12, 96), (40, 118), (70, 104), (176, 92), (206, 110), (240, 98),
        (274, 116), (306, 88), (22, 140), (54, 132), (190, 136), (252, 144),
    ]
    for x, y in seed:
        if any(abs(x - px) < 5 and abs(y - py) < 5 for px, py in placed):
            continue
        if 0 <= x < W and 0 <= y < band0:
            op[x, y] = 1
            placed.append((x, y))
            dim += 1

    OUT_PROC.parent.mkdir(parents=True, exist_ok=True)
    OUT_RES.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT_PROC, format="PNG", optimize=False, bits=4)
    out.save(OUT_RES, format="PNG", optimize=False, bits=4)

    report = {
        "source": str(SRC.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "out_res": str(OUT_RES.relative_to(ROOT)),
        "size": [W, H],
        "mode": out.mode,
        "colors": len({out.getpixel((x, y)) for y in range(H) for x in range(W)}),
        "unique_tiles_8x8": unique_tiles(out),
        "stars_stamped": len(placed),
        "dim_field_stars": dim,
        "index0": "black_backdrop",
        "pulse_slots": [1, 2],
        "acceptance_status": "placeholder",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
