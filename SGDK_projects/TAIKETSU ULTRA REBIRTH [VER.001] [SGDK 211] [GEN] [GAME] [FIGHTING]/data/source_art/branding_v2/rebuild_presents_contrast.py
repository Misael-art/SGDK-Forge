#!/usr/bin/env python3
"""Rebuild PRESENTS contrast and a soot bar tile from authored pixels only.

Does not invent glyphs. Ink comes from presents_v01. Outline is the authored
edge; body is the authored interior remapped onto PAL2 light slots.
The bar tile is an 8x8 crop of forge_bg_b_320x224 (soot hole at 48,200).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from assemble_branding_v2_assets import (  # noqa: E402
    MAGENTA,
    PAL2,
    content_bbox,
    fit_contain,
    is_key,
    key_from_edges,
    load_rgb,
    new_indexed,
    save_indexed,
)

PROJ = HERE.parent.parent.parent
RES = PROJ / "res" / "branding"
RAW = HERE / "raw"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def remap_presents(src_path: Path) -> Image.Image:
    rgb = key_from_edges(load_rgb(src_path))
    rgb = rgb.crop(content_bbox(rgb, pad=2))
    rgb = fit_contain(rgb, (92, 12))
    canvas = Image.new("RGB", (96, 16), MAGENTA)
    ox = (96 - rgb.size[0]) // 2
    oy = (16 - rgb.size[1]) // 2
    canvas.paste(rgb, (ox, oy))

    w, h = canvas.size
    px = canvas.load()
    ink = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if not is_key(px[x, y]):
                ink[y][x] = 1

    # 1px ring around authored ink (no new silhouette). Thin 16px glyphs have
    # no 4-connected interior, so the original ink is the body.
    ring = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if ink[y][x]:
                continue
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and ink[ny][nx]:
                    ring[y][x] = 1
                    break

    out = new_indexed((96, 16), PAL2)
    op = out.load()
    for y in range(h):
        for x in range(w):
            if ink[y][x]:
                below = (y + 1 >= h) or not ink[y + 1][x]
                op[x, y] = 12 if below else 9
            elif ring[y][x]:
                op[x, y] = 1
            else:
                op[x, y] = 0
    return out


def extract_bar_tile() -> Image.Image:
    src = Image.open(RES / "forge_bg_b_320x224.png").convert("RGB")
    crop = src.crop((48, 200, 56, 208))
    out = new_indexed((8, 8), PAL2)
    # Reuse PAL0-ish dark as PAL2[1] (outline black) so the bar is opaque.
    op = out.load()
    cp = crop.load()
    for y in range(8):
        for x in range(8):
            r, g, b = cp[x, y]
            luma = 0.299 * r + 0.587 * g + 0.114 * b
            if luma < 16:
                op[x, y] = 1
            elif luma < 48:
                op[x, y] = 2
            else:
                op[x, y] = 3
    return out


def main() -> None:
    presents = remap_presents(RAW / "presents_v01.jpg")
    dest_p = RES / "presents_text_96x16.png"
    save_indexed(presents, dest_p)

    bar = extract_bar_tile()
    dest_b = RES / "presents_bar_8x8.png"
    save_indexed(bar, dest_b)

    # Contrast self-check against the brief.
    pal = presents.getpalette() or []
    data = list(presents.getdata())
    ink = [i for i in data if i]
    body = [i for i in ink if i >= 8]
    body_lumas = []
    for i in body:
        r, g, b = pal[i * 3 : i * 3 + 3]
        body_lumas.append(0.299 * r + 0.587 * g + 0.114 * b)
    mean_body = sum(body_lumas) / len(body_lumas) if body_lumas else 0
    from collections import Counter

    counts = Counter(ink)
    top_share = counts.most_common(1)[0][1] / len(ink) if ink else 0
    report = {
        "presents": str(dest_p),
        "presents_sha256": sha256(dest_p),
        "ink_pixels": len(ink),
        "body_pixels": len(body),
        "mean_body_luma": round(mean_body, 1),
        "top_index_share": round(top_share, 3),
        "indices": {str(k): v for k, v in counts.items()},
        "bar": str(dest_b),
        "bar_sha256": sha256(dest_b),
        "pass_luma": mean_body >= 100,
        "pass_spread": top_share <= 0.70,
        "pass_outline": counts.get(1, 0) > 0,
    }
    (HERE / "presents_contrast_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    if not report["pass_luma"] or not report["pass_spread"] or not report["pass_outline"]:
        raise SystemExit("presents contrast still below brief")


if __name__ == "__main__":
    main()
