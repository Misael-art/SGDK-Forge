#!/usr/bin/env python3
"""Prepare the title backdrop and a transparent logo overlay.

The generated backdrop is kept as source art and reduced to Mega Drive 9-bit
colours plus a bounded tile set.  The legal/logo artwork is not redrawn: its
border-connected black field is made transparent so it can sit over the
backdrop while preserving internal black outlines.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "title_backdrop_generated_v01.png"
LOGO_SOURCE = ROOT / "res/gfx/room_0_bgb.png"
BACKDROP = ROOT / "res/gfx/title_backdrop.png"
LOGO = ROOT / "res/gfx/title_logo_overlay.png"
SCENE = ROOT / "res/gfx/title_scene.png"
REPORT = HERE / "title_assets_report.json"
OUT_W, OUT_H = 320, 224
COLOURS = 14
TILE_BUDGET = 384
SNAP = 34


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snap9(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(max(0, min(238, int(round(int(v) / SNAP) * SNAP))) for v in rgb)


def reduce_backdrop() -> tuple[int, int, list[tuple[int, int, int]]]:
    # Build the backdrop directly on the 40x28 name-table grid and expand
    # each cell to one 8x8 tile.  This gives a clean, saturated blue field
    # with a handful of reusable tiles, leaving VRAM for the logo and menu.
    src = Image.open(SOURCE).convert("RGB").resize((OUT_W // 8, OUT_H // 8), Image.Resampling.LANCZOS)
    src = src.resize((OUT_W, OUT_H), Image.Resampling.NEAREST)
    quant = src.quantize(colors=COLOURS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    raw = quant.getpalette()
    palette: list[tuple[int, int, int]] = []
    for i in range(COLOURS):
        colour = snap9((raw[i * 3], raw[i * 3 + 1], raw[i * 3 + 2]))
        if colour == (0, 0, 0):
            colour = (0, 0, 34)
        if colour not in palette:
            palette.append(colour)
    while len(palette) < COLOURS:
        palette.append((0, 0, 34 + min(204, len(palette) * 17)))
    # Use 32-bit arithmetic: 8-bit channel deltas squared can exceed the
    # signed 16-bit range and otherwise invert nearest-colour decisions.
    rgb = np.asarray(src, dtype=np.int32)
    colours = np.asarray(palette, dtype=np.int32)
    distances = ((rgb[:, :, None, :] - colours[None, None, :, :]) ** 2).sum(axis=3)
    indexed = distances.argmin(axis=2).astype(np.uint8)
    tiles = indexed.reshape(OUT_H // 8, 8, OUT_W // 8, 8).transpose(0, 2, 1, 3).reshape(-1, 64)
    unique, inverse, counts = np.unique(tiles, axis=0, return_inverse=True, return_counts=True)
    before = len(unique)
    if before > TILE_BUDGET:
        vectors = unique.astype(np.float32)
        nearest = np.full(before, np.inf, dtype=np.float32)
        assignment = np.zeros(before, dtype=np.int32)
        selected: list[int] = []
        idx = int(counts.argmax())
        for _ in range(TILE_BUDGET):
            selected.append(idx)
            dist = np.sum((vectors - vectors[idx]) ** 2, axis=1)
            mask = dist < nearest
            nearest[mask] = dist[mask]
            assignment[mask] = idx
            score = nearest * np.sqrt(counts)
            score[selected] = -1
            idx = int(np.argmax(score))
        indexed = unique[assignment[inverse]].reshape(OUT_H // 8, OUT_W // 8, 8, 8).transpose(0, 2, 1, 3)
    resident_pixels = indexed.reshape(OUT_H, OUT_W)
    resident = Image.fromarray(resident_pixels, mode="P")
    resident.putpalette([v for colour in palette for v in colour] + [0] * (3 * (256 - len(palette))))
    BACKDROP.parent.mkdir(parents=True, exist_ok=True)
    resident.save(BACKDROP, format="PNG")
    measured_tiles = resident_pixels.reshape(OUT_H // 8, 8, OUT_W // 8, 8).transpose(0, 2, 1, 3).reshape(-1, 64)
    return before, len(np.unique(measured_tiles, axis=0)), palette


def transparent_logo() -> tuple[int, int]:
    src = Image.open(LOGO_SOURCE).convert("P")
    palette = src.getpalette()
    pixels = src.load()
    background = (0, 0, 0)
    seen: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()
    for x in range(src.width):
        queue.extend(((x, 0), (x, src.height - 1)))
    for y in range(src.height):
        queue.extend(((0, y), (src.width - 1, y)))
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or not (0 <= x < src.width and 0 <= y < src.height):
            continue
        seen.add((x, y))
        index = int(pixels[x, y])
        r, g, b = palette[index * 3:index * 3 + 3]
        if (r, g, b) != background:
            continue
        # Reserve palette index 15 for transparency.  Keeping index 0 as
        # opaque black preserves the logo's enclosed outlines after the
        # border-connected background is removed.
        pixels[x, y] = 15
        queue.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    # The legal block belongs exclusively to OPENING.  Remove its measured
    # left-side rectangle from the title overlay so a page redraw can restore
    # the artwork without resurrecting credits behind the menu.  The pig/logo
    # begins at x=190 and is outside this crop.
    for y in range(112, src.height):
        for x in range(0, 190):
            pixels[x, y] = 15
    # Keep the wordmark at native scale while giving the pig its own anchored
    # crop. The previous full-sheet half-scale copy made the title read as a
    # small prototype card and mixed the legal/credit region into the logo.
    # Both crops originate from the authored room_0_bgb source.
    canvas = Image.new("P", (OUT_W, OUT_H), 15)
    canvas.putpalette(palette)
    wordmark = src.crop((0, 0, 190, 104))
    wordmark_mask = Image.fromarray(
        (np.asarray(wordmark, dtype=np.uint8) != 15).astype(np.uint8) * 255,
        mode="L",
    )
    canvas.paste(wordmark, (8, 12), wordmark_mask)
    pig = src.crop((190, 0, src.width, src.height)).resize((108, 96), Image.Resampling.NEAREST)
    pig_mask = Image.fromarray(
        (np.asarray(pig, dtype=np.uint8) != 15).astype(np.uint8) * 255,
        mode="L",
    )
    canvas.paste(pig, (208, 10), pig_mask)
    # The source wordmark carries one detached white source pixel below its
    # last credit line. It is outside the authored lettering envelope and would
    # read as a stray UI glyph after the native-scale composition.
    for y in range(96, 116):
        for x in range(180, 208):
            canvas.putpixel((x, y), 15)
    src = canvas
    LOGO.parent.mkdir(parents=True, exist_ok=True)
    src.putpalette(palette)
    src.save(LOGO, format="PNG", optimize=False)
    return len(seen), sum(1 for pixel in src.getdata() if pixel == 15)


def build_composite_scene() -> tuple[int, int]:
    """Composite backdrop and cleaned logo, then reduce as one palette.

    Keeping both layers in one indexed image avoids plane-order and per-image
    palette conflicts on the VDP while preserving the logo text over colour.
    """
    backdrop = Image.open(BACKDROP).convert("RGB")
    logo = Image.open(LOGO).convert("P")
    logo_rgb = logo.convert("RGB")
    mask = Image.fromarray((np.asarray(logo, dtype=np.uint8) != 15).astype(np.uint8) * 255, mode="L")
    backdrop.paste(logo_rgb, (0, 0), mask)
    # A fixed Mega Drive palette keeps the blue backdrop dominant while
    # reserving readable light, skin, red and green tones for the logo.
    palette: list[tuple[int, int, int]] = [
        (0, 0, 0), (0, 0, 68), (0, 34, 102), (0, 34, 136),
        (0, 34, 170), (0, 68, 204), (0, 102, 238), (34, 34, 102),
        (102, 102, 136), (238, 238, 238), (204, 204, 204),
        (238, 204, 170), (204, 102, 68), (170, 34, 34), (34, 170, 204),
    ]
    rgb = np.asarray(backdrop, dtype=np.int32)
    colours = np.asarray(palette, dtype=np.int32)
    distances = ((rgb[:, :, None, :] - colours[None, None, :, :]) ** 2).sum(axis=3)
    indexed = distances.argmin(axis=2).astype(np.uint8)
    tiles = indexed.reshape(28, 8, 40, 8).transpose(0, 2, 1, 3).reshape(-1, 64)
    unique, inverse, counts = np.unique(tiles, axis=0, return_inverse=True, return_counts=True)
    if len(unique) > TILE_BUDGET:
        vectors = unique.astype(np.float32)
        nearest = np.full(len(unique), np.inf, dtype=np.float32)
        assignment = np.zeros(len(unique), dtype=np.int32)
        selected: list[int] = []
        # Never approximate tiles that contain logo pixels.  The backdrop can
        # be reduced aggressively, but replacing a logo tile with a nearby
        # floor tile destroys letterforms and sprite silhouettes.
        logo_mask = np.asarray(mask, dtype=np.uint8).reshape(28, 8, 40, 8)
        logo_tiles = logo_mask.transpose(0, 2, 1, 3).reshape(-1, 64).any(axis=1)
        protected = list(np.unique(inverse[logo_tiles]))
        if len(protected) > TILE_BUDGET:
            protected = protected[:TILE_BUDGET]
        for idx in protected:
            selected.append(int(idx))
            dist = np.sum((vectors - vectors[idx]) ** 2, axis=1)
            mask_selected = dist < nearest
            nearest[mask_selected] = dist[mask_selected]
            assignment[mask_selected] = idx
        while len(selected) < TILE_BUDGET:
            score = nearest * np.sqrt(counts)
            score[selected] = -1
            idx = int(np.argmax(score))
            selected.append(idx)
            dist = np.sum((vectors - vectors[idx]) ** 2, axis=1)
            mask_selected = dist < nearest
            nearest[mask_selected] = dist[mask_selected]
            assignment[mask_selected] = idx
        indexed = unique[assignment[inverse]].reshape(28, 40, 8, 8).transpose(0, 2, 1, 3)
    pixels = indexed.reshape(OUT_H, OUT_W)
    out = Image.fromarray(pixels, mode="P")
    out.putpalette([v for colour in palette for v in colour] + [0] * (3 * (256 - len(palette))))
    out.save(SCENE, format="PNG")
    measured = pixels.reshape(28, 8, 40, 8).transpose(0, 2, 1, 3).reshape(-1, 64)
    return len(unique), len(np.unique(measured, axis=0))


def main() -> None:
    before, after, palette = reduce_backdrop()
    flood_seen, transparent = transparent_logo()
    scene_before, scene_after = build_composite_scene()
    report = {
        "schema_version": "1.0.0",
        "asset_kind": "title_backdrop_and_logo_overlay",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "logo_source": str(LOGO_SOURCE.relative_to(ROOT)),
        "logo_source_sha256": sha256(LOGO_SOURCE),
        "backdrop": str(BACKDROP.relative_to(ROOT)),
        "backdrop_sha256": sha256(BACKDROP),
        "logo_overlay": str(LOGO.relative_to(ROOT)),
        "logo_overlay_sha256": sha256(LOGO),
        "scene": str(SCENE.relative_to(ROOT)),
        "scene_sha256": sha256(SCENE),
        "dimensions": [OUT_W, OUT_H],
        "palette_snap": "Mega Drive 9-bit, step 34; pure black avoided in backdrop",
        "palette_rgb": palette,
        "unique_tiles_before_reuse": before,
        "unique_tiles_after_reuse": after,
        "tile_budget": TILE_BUDGET,
        "scene_unique_tiles_before_reuse": scene_before,
        "scene_unique_tiles_after_reuse": scene_after,
        "logo_background_flood_pixels": flood_seen,
        "logo_transparent_pixels": transparent,
        "provenance": "title_backdrop_generated_with_imagegen_prompt; logo_overlay_derived_from_existing_room_0_bgb_by_border_flood_only; native_scale_wordmark_and_anchored_pig_crop; fixed_palette_int32_mapping",
        "claim_ceiling": "prototype_title_candidate",
        "visual_review_required": True,
        "emulator_validated": False,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
