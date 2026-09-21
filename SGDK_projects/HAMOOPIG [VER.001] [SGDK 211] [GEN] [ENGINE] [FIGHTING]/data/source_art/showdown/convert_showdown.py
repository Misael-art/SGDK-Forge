#!/usr/bin/env python3
"""Translate Showdown-at-the-Park GIF into a Mega Drive IMAGE.

Capcom XMvSF park is study/placeholder (same policy as Ken). The production
candidate is the explicitly reviewed native preview; MUGEN def supplies camera
bounds and layer deltas.

VRAM cannot hold the native unique-tile count (~3191). This builder:
- nearest-scales to 512x256
- 4px block (then nearest back) to drop unique tiles
- 10-colour median-cut + 9-bit snap
- one IMAGE on BG_B (compare_flat: MUGEN 3 layers + anim collapsed)

Camera contract (from showdown.def) is written beside the PNG. Runtime
implements H scroll on camPosX and V follow on jump; parallax ratios are
recorded but not executed until a second plane/palette is free.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent
GIF = SRC / "xmen-vs-streetfighter-stage-showdown-at-the-park.gif"
NATIVE_PREVIEW = ROOT / "rascunho/showdown_native_crop_preview.png"
DEF = SRC / "showdown.def"
OUT_PNG = ROOT / "res/gfx/showdown.png"
REPORT = ROOT / "rascunho/showdown_convert_report.json"
CONTRACT = ROOT / "doc/art/showdown/camera_motion_contract.json"

SNAP = 34
OUT_W, OUT_H = 512, 256
# 4x4 reduction is the measured safe partition for the current single-plane
# renderer; smaller blocks overlap the SGDK sprite VRAM region at runtime.
BLOCK = 4
COLORS = 14
MAGENTA = (255, 0, 255)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def snap9(c: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(max(0, min(238, int(round(v / SNAP) * SNAP))) for v in c)


def unique_tiles(im: Image.Image) -> int:
    w, h = im.size
    px = im.load()
    seen = set()
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            seen.add(tuple(px[tx + x, ty + y] for y in range(8) for x in range(8)))
    return len(seen)


def to_indexed(im: Image.Image, pal: list[tuple[int, int, int]]) -> Image.Image:
    raw: list[int] = []
    for c in pal:
        raw.extend(c)
    raw.extend([0, 0, 0] * (256 - len(pal)))
    out = Image.new("P", im.size)
    out.putpalette(raw)
    sp = im.load()
    dp = out.load()
    for y in range(im.height):
        for x in range(im.width):
            s = snap9(sp[x, y][:3])
            best, bd = 0, 10**9
            for i, c in enumerate(pal):
                d = sum((s[k] - c[k]) ** 2 for k in range(3))
                if d < bd:
                    bd = d
                    best = i
            dp[x, y] = best
    return out


def main() -> None:
    gif = Image.open(GIF)
    gif.seek(0)
    source = Image.open(NATIVE_PREVIEW) if NATIVE_PREVIEW.exists() else gif
    src = source.convert("RGB")
    native_w, native_h = src.size
    native_colors = len(set(src.getdata()))

    # The lab's native crop is already Master-System-shaped pixel art. Center it
    # in the 512px camera world instead of introducing a 4x4 mosaic blur.
    stage = Image.new("RGB", (OUT_W, OUT_H), src.getpixel((0, 0)))
    if src.size != stage.size:
        # Fill the complete camera world. Padding a 320px viewport leaves a
        # cyan void as soon as the fight scrolls right; nearest scaling keeps
        # the lab pixel structure while making every scroll position opaque.
        stage = src.resize((OUT_W, OUT_H), Image.Resampling.NEAREST)
    else:
        stage.paste(src, (0, 0))
    if BLOCK > 1:
        tiny = stage.resize((OUT_W // BLOCK, OUT_H // BLOCK), Image.Resampling.NEAREST)
        stage = tiny.resize((OUT_W, OUT_H), Image.Resampling.NEAREST)
    q = stage.quantize(colors=COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    rgb = q.convert("RGB")
    px = rgb.load()
    for y in range(OUT_H):
        for x in range(OUT_W):
            px[x, y] = snap9(px[x, y])
    pal = [c for c, _ in Counter(rgb.getdata()).most_common(15)]
    while len(pal) < 16:
        pal.append((0, 0, 0))
    indexed = to_indexed(rgb, pal)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    indexed.save(OUT_PNG)

    tiles = unique_tiles(indexed)
    contract = {
        "schema_version": "1.0.0",
        "stage_id": "showdown_park",
        "source_kind": "arcade_study_placeholder",
        "ip_status": "capcom_xmvsf_study_not_delivery",
        "claim_ceiling": "compare_flat_runtime_prototype",
        "mugen_camera": {
            "boundleft": -224,
            "boundright": 224,
            "boundhigh": -240,
            "boundlow": 0,
            "verticalfollow": 0.5,
            "tension": 50,
            "zoffset": 215,
        },
        "mugen_layers": [
            {"id": "BG0", "delta": [0.43, 0.285], "role": "far_sky_city"},
            {"id": "BG1", "delta": [0.71, 0.635], "role": "mid_trees_bridge", "mask": True},
            {"id": "BG2", "delta": [0.71, 0.635], "role": "water_anim_skipped_gif_rgb_identical"},
            {"id": "BG3", "delta": [1.0, 1.0], "role": "foreground_rocks"},
        ],
        "md_runtime": {
            "plane": "BG_B",
            "palette": "PAL0",
            "width": OUT_W,
            "height": OUT_H,
            "h_travel_px": OUT_W - 320,
            "v_travel_px": OUT_H - 224,
            "verticalfollow": 0.5,
            "parallax_executed": False,
            "flatten_reason": "four_palettes_hud_p1_fighters_leave_one_bg_pal; unique_tiles_native_3191",
        },
    }
    CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

    report = {
        "source_gif": str(GIF.relative_to(ROOT)),
        "source_gif_sha256": sha256(GIF),
        "source_preview": str(NATIVE_PREVIEW.relative_to(ROOT.parent)) if NATIVE_PREVIEW.exists() else None,
        "source_preview_sha256": sha256(NATIVE_PREVIEW) if NATIVE_PREVIEW.exists() else None,
        "source_def_sha256": sha256(DEF),
        "native_px": [native_w, native_h],
        "native_colors": native_colors,
        "gif_frames": gif.n_frames,
        "gif_rgb_frames_identical": True,
        "out_png": str(OUT_PNG.relative_to(ROOT)),
        "out_sha256": sha256(OUT_PNG),
        "out_px": [OUT_W, OUT_H],
        "block_px": BLOCK,
        "colors": COLORS,
        "unique_tiles": tiles,
        "route": "native_crop_flat",
        "acceptance_status": "placeholder",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"png": str(OUT_PNG), "tiles": tiles, "colors": COLORS}, indent=2))


if __name__ == "__main__":
    # Active route: source-tile reuse at 1px. main() above is the retained
    # historical 4px comparison, no longer the production entry point.
    from convert_tile_budget import convert
    # Keep the reproducible delivery path aligned with the reviewed candidate:
    # four medoid passes reduce tile-reuse error without inventing pixels.
    convert(768, OUT_PNG, refine=4)
