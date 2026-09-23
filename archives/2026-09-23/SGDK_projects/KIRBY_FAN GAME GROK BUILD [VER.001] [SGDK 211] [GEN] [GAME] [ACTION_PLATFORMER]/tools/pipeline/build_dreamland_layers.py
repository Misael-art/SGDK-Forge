#!/usr/bin/env python3
"""Build AAA-leaning Dream Land BG layers with ABSOLUTE PAL0/PAL1 indices.

R5 density pass (post blind-critic R2): solid mountain faces (no Bayer soup),
varied tree silhouettes, broken forest skyline, grass clusters + dirt strata.

Lesson L-011: absolute indices matching doc/PALETTES.md + pal0/1_master.png.
No shared-palette AI remapping.

Usage:
  python3 tools/pipeline/build_dreamland_layers.py --install
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GFX = ROOT / "res" / "gfx"
OUT = ROOT / "data" / "source_art" / "ai_quantized" / "r5_layers"

KEY = (255, 0, 255)
# Must match res/gfx/pal0_master.png / pal1_master.png pixel-for-pixel.
PAL0 = [
    KEY,
    (109, 182, 255),  # 1 sky deep
    (146, 182, 255),  # 2 sky mid
    (182, 219, 255),  # 3 sky light
    (219, 219, 255),  # 4 sky pale
    (255, 219, 182),  # 5 horizon cream warm
    (255, 255, 182),  # 6 horizon cream
    (255, 255, 255),  # 7 cloud white
    (219, 219, 255),  # 8 cloud soft / shade
    (146, 146, 182),  # 9 mountain light / far forest
    (109, 109, 146),  # 10 mountain dark / mid forest
    (109, 182, 73),  # 11 hill light
    (73, 146, 73),  # 12 hill mid
    (36, 109, 36),  # 13 hill dark
    (109, 73, 36),  # 14 trunk
    (36, 36, 73),  # 15 outline / near forest
]
PAL1 = [
    KEY,
    (73, 182, 73),  # 1 grass light
    (36, 146, 36),  # 2 grass mid
    (36, 109, 36),  # 3 grass dark
    (146, 109, 73),  # 4 dirt light
    (109, 73, 36),  # 5 dirt mid
    (73, 36, 0),  # 6 dirt deep
    (36, 36, 36),  # 7 outline
    (109, 182, 255),  # 8 water (reserved cycle)
    (182, 219, 255),  # 9 water mid
    (255, 255, 255),  # 10 water/white
    (146, 146, 146),  # 11 stone
    (255, 182, 219),  # 12 flower pink
    (255, 255, 146),  # 13 flower yellow
    (36, 109, 36),  # 14 FG dark green
    (0, 73, 36),  # 15 FG deeper
]


def new_indexed(w: int, h: int, palette: list[tuple[int, int, int]], fill: int = 0) -> Image.Image:
    im = Image.new("P", (w, h), fill)
    flat: list[int] = []
    for c in palette:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - len(palette)))
    im.putpalette(flat)
    return im


def put(im: Image.Image, x: int, y: int, idx: int) -> None:
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), idx)


def stamp_full_palette(im: Image.Image) -> Image.Image:
    """First-occurrence 0..15 top-left so shared-palette packing stays absolute."""
    a = np.array(im)
    for i in range(16):
        a[0, i] = i
        a[-1, -16 + i] = i
    out = Image.fromarray(a, mode="P")
    out.putpalette(im.getpalette())
    return out


def _hash01(x: int, y: int, seed: int = 0) -> float:
    """Deterministic 0..1 hash (no float in game — only offline art)."""
    n = (x * 374761393 + y * 668265263 + seed * 1274126177) & 0x7FFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def _smooth_height(xs: np.ndarray, peaks: list[tuple[float, float, float]]) -> np.ndarray:
    """Sum of smooth gaussian-ish lobes for organic ridgelines (not rigid triangles)."""
    h = np.zeros_like(xs, dtype=np.float64)
    for cx, amp, width in peaks:
        h += amp * np.exp(-0.5 * ((xs - cx) / width) ** 2)
    return h


def _bayer4(x: int, y: int) -> float:
    """4x4 Bayer threshold 0..1 for soft MD dither (not harsh diagonal hatch)."""
    m = (
        (0, 8, 2, 10),
        (12, 4, 14, 6),
        (3, 11, 1, 9),
        (15, 7, 13, 5),
    )
    return m[y & 3][x & 3] / 16.0


# ---------------------------------------------------------------------------
# SKY — soft fluffy multi-blob cumulus (not concentric rings)
# ---------------------------------------------------------------------------


def _blob_cloud(im: Image.Image, cx: int, cy: int, rx: int, ry: int, fill: int, edge: int) -> None:
    """Filled ellipse with 3-tone volume (white / soft / pale sky rim)."""
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            nx = dx / max(1, rx)
            ny = dy / max(1, ry)
            d = nx * nx + ny * ny
            if d <= 1.0:
                # top-left highlight, bottom shade, outer pale rim
                if d > 0.78 and dy > 0:
                    put(im, cx + dx, cy + dy, 4)  # pale sky rim for soft edge
                elif d > 0.65 and dy > 0:
                    put(im, cx + dx, cy + dy, edge)
                elif d > 0.50 and dy > ry // 4:
                    put(im, cx + dx, cy + dy, edge if (dx + dy) & 1 else fill)
                elif d < 0.25 and dy < 0 and dx < 0:
                    put(im, cx + dx, cy + dy, fill)  # highlight core
                else:
                    put(im, cx + dx, cy + dy, fill)


def build_sky() -> Image.Image:
    """512×80 transparent sky strip; fluffy organic clouds on absolute 7/8."""
    im = new_indexed(512, 80, PAL0, 0)
    # Cumulus clusters: several overlapping lobes per cloud (classic MD look).
    clusters = (
        # (base_cx, base_cy, lobes as (ox, oy, rx, ry))
        (70, 30, ((0, 4, 28, 12), (-22, 8, 18, 10), (24, 10, 16, 9), (-8, -6, 14, 8), (12, -4, 12, 7))),
        (180, 22, ((0, 2, 32, 14), (-26, 6, 20, 11), (28, 8, 18, 10), (-10, -8, 16, 9), (14, -6, 14, 8), (0, 12, 22, 8))),
        (300, 34, ((0, 0, 24, 11), (-18, 6, 16, 9), (20, 7, 15, 8), (-4, -5, 12, 7))),
        (410, 26, ((0, 2, 30, 13), (-24, 8, 18, 10), (26, 6, 17, 9), (-8, -7, 14, 8), (10, -5, 13, 7))),
        (500, 32, ((0, 0, 20, 10), (-14, 5, 14, 8), (12, 6, 12, 7))),
        (240, 48, ((0, 0, 18, 8), (-12, 3, 12, 6), (10, 4, 11, 6))),  # lower soft
    )
    for cx, cy, lobes in clusters:
        for ox, oy, rx, ry in lobes:
            _blob_cloud(im, cx + ox, cy + oy, rx, ry, fill=7, edge=8)
    return stamp_full_palette(im)


# ---------------------------------------------------------------------------
# MOUNTAINS — organic ridgeline + smooth slope shading (Bayer, not hatch)
# ---------------------------------------------------------------------------


def build_mountains() -> Image.Image:
    """512×56: solid faces + edge dither only (R5 — no Bayer soup)."""
    im = new_indexed(512, 56, PAL0, 0)
    xs = np.arange(512, dtype=np.float64)
    peaks = [
        (36, 42, 18),
        (88, 50, 20),
        (145, 34, 16),
        (198, 52, 22),
        (255, 38, 17),
        (310, 48, 19),
        (365, 44, 18),
        (420, 50, 21),
        (475, 36, 16),
        (515, 40, 17),
        (100, 10, 36),
        (260, 9, 40),
        (430, 10, 38),
    ]
    height = _smooth_height(xs, peaks)
    for x in range(512):
        # Stepped crest: quantize to 2px vertical bands for MD pixel stairs
        height[x] += 1.8 * math.sin(x * 0.13) + 0.9 * math.sin(x * 0.37 + 1.1)
        height[x] = float(int(height[x] / 2) * 2)

    base_y = 55
    # Precompute slope-facing: light left, dark right — solid regions
    for x in range(512):
        h = int(max(0, min(54, height[x])))
        if h < 8:
            if h >= 4:
                for y in range(base_y - h, base_y + 1):
                    put(im, x, y, 10)
            continue
        crest = base_y - h
        h_l = height[max(0, x - 1)]
        h_r = height[min(511, x + 1)]
        slope = (h_r - h_l) * 0.45
        # Find ridge x of nearest peak for overhang decoration
        for y in range(crest, base_y + 1):
            t = (y - crest) / max(1, h)
            # SOLID face choice — dither only in a thin transition band near slope=0
            if abs(slope) < 0.35 and 0.25 < t < 0.75:
                # edge blend only
                thr = _bayer4(x, y)
                idx = 9 if thr > 0.5 else 10
            elif slope < 0:
                idx = 9  # lit face
            else:
                idx = 10  # shadow face
            # snow patches (not single-pixel tips)
            if t < 0.12 and h > 30 and abs(slope) < 0.8:
                idx = 7
            elif t < 0.18 and h > 36 and slope < 0:
                idx = 7 if (x + y) & 1 else 9
            if t > 0.90:
                idx = 10
            put(im, x, y, idx)
        # crest outline + occasional overhang pixel (cliff step)
        if h > 24:
            put(im, x, crest, 15 if (x % 5) == 0 else 9)
        if h > 36 and slope > 0.6 and (x % 17) == 3:
            # overhang shadow blob on right faces
            put(im, x, crest + 3, 15)
            put(im, x + 1, crest + 4, 10)
    return stamp_full_palette(im)


# ---------------------------------------------------------------------------
# FOREST mid-band (G5) — dense cool pines, 3 depth tones (9 / 10 / 15)
# ---------------------------------------------------------------------------


def _pine(im: Image.Image, tx: int, base_y: int, h: int, idx: int, style: int = 0) -> None:
    """Pine variants: 0=classic stack, 1=tall skinny, 2=wide squat."""
    layers = max(2, h // 6)
    top = base_y - h
    if style == 1:
        layers = max(3, h // 5)
    for li in range(layers):
        cy = top + 2 + li * (h // (layers + 1))
        if style == 1:
            half = 1 + li + (h // 14)
            depth = 5 + li
        elif style == 2:
            half = 3 + li * 3 + (h // 8)
            depth = 4 + li // 2
        else:
            half = 2 + li * 2 + (h // 10)
            depth = 6 + li
        for dy in range(0, depth):
            y = cy + dy
            w = half - dy // 2
            if w < 1:
                continue
            for x in range(tx - w, tx + w + 1):
                put(im, x, y, idx)
    for yy in range(base_y - 4, base_y + 1):
        for xx in range(tx - 1, tx + 2):
            put(im, xx, yy, 15 if idx == 15 else 10)


def build_forest() -> Image.Image:
    """512×40 pine band with sky holes at tops (R5 — not a solid wall)."""
    im = new_indexed(512, 40, PAL0, 0)
    # Irregular x positions (not fixed stride) for organic density
    def place_row(seed: int, count: int, base_span: int, h0: int, h1: int, idx: int) -> None:
        x = 2 + int(4 * _hash01(seed, 0, 1))
        for i in range(count):
            style = int(3 * _hash01(x, i, seed + 3)) % 3
            h = h0 + int((h1 - h0) * _hash01(x, i, seed + 5))
            # occasional short tree leaves a sky notch
            if _hash01(x, i, seed + 7) < 0.12:
                h = max(8, h // 2)
            jitter = int(5 * _hash01(x, i, seed + 9)) - 2
            _pine(im, x + jitter, 39, h, idx, style=style)
            step = base_span + int(5 * _hash01(x, i, seed + 11)) - 2
            x += max(5, step)
            if x >= 510:
                break

    place_row(3, 55, 11, 12, 18, 9)   # far
    place_row(11, 70, 8, 16, 24, 10)  # mid
    place_row(17, 60, 9, 18, 30, 15)  # near
    # ground mist (keep band filled at base only — tops stay open)
    for x in range(512):
        for y in range(36, 40):
            if im.getpixel((x, y)) == 0:
                put(im, x, y, 10 if (x + y) & 1 else 9)
    return stamp_full_palette(im)


# ---------------------------------------------------------------------------
# HILLS — lush organic mounds + canopy trees (512×56 to match scene row 18)
# ---------------------------------------------------------------------------


def build_hills() -> Image.Image:
    im = new_indexed(512, 56, PAL0, 0)
    xs = np.arange(512, dtype=np.float64)
    # Rolling Dream Land mounds — continuous base so no holes, but scalloped crest.
    mounds = [
        (40, 28, 32),
        (110, 36, 34),
        (185, 24, 30),
        (250, 38, 36),
        (320, 30, 32),
        (390, 36, 34),
        (460, 28, 30),
        (520, 32, 32),
        # continuous low base so band doesn't go transparent
        (256, 16, 200),
    ]
    height = _smooth_height(xs, mounds)
    for x in range(512):
        height[x] += 2.2 * math.sin(x * 0.05 + 0.4) + 1.0 * math.sin(x * 0.19)

    base_y = 55
    for x in range(512):
        h = int(max(14, min(48, height[x])))
        crest = base_y - h
        for y in range(crest, base_y + 1):
            t = (y - crest) / max(1, h)
            if t < 0.15:
                idx = 11  # light crest
            elif t < 0.50:
                idx = 11 if _bayer4(x, y) < (0.50 - t * 0.6) else 12
            else:
                idx = 13 if t > 0.80 or _bayer4(x, y) > 0.5 else 12
            put(im, x, y, idx)
        # scalloped grass tufts on crest
        if x % 4 == 0:
            put(im, x, crest - 1, 11)
        if x % 7 == 2:
            put(im, x, crest - 2, 12)
        if x % 11 == 5:
            put(im, x, crest - 1, 13)

    # 3 silhouettes: round / tall / wide — irregular spacing + Y offset (R2-G2)
    tree_specs = (
        # (tx, style 0=round 1=tall 2=wide, trunk_lean)
        (38, 0, 0),
        (72, 1, -1),
        (118, 2, 0),
        (155, 0, 1),
        (198, 1, 0),
        (240, 2, -1),
        (278, 0, 0),
        (325, 1, 1),
        (368, 2, 0),
        (410, 0, -1),
        (455, 1, 0),
        (492, 2, 0),
    )
    for tx, style, lean in tree_specs:
        local_h = int(max(14, min(48, height[min(511, tx)])))
        base = base_y - local_h + 6 + int(3 * _hash01(tx, style, 99))
        trunk_h = 12 if style != 1 else 16
        for yy in range(base - trunk_h, base + 1):
            xx0 = tx + lean * ((base - yy) // 6)
            for xx in range(xx0 - 1, xx0 + 2):
                put(im, xx, yy, 14)
        if style == 0:  # round canopy
            lobes = ((base - 16, 8, 12), (base - 22, 6, 11), (base - 12, 7, 13), (base - 18, 4, 11))
        elif style == 1:  # tall poplar-ish
            lobes = ((base - 20, 5, 12), (base - 28, 4, 11), (base - 14, 5, 13), (base - 24, 3, 11))
        else:  # wide oak-ish
            lobes = ((base - 14, 10, 12), (base - 18, 8, 11), (base - 10, 9, 13), (base - 16, 6, 11))
        for cy, cr, ci in lobes:
            for yy in range(cy - cr, cy + cr + 1):
                for xx in range(tx - cr, tx + cr + 1):
                    if (xx - tx) * (xx - tx) + (yy - cy) * (yy - cy) <= cr * cr:
                        put(im, xx, yy, ci)
    return stamp_full_palette(im)


# ---------------------------------------------------------------------------
# TERRAIN — organic dirt, grass tufts, rocks, vines (not rigid checker)
# ---------------------------------------------------------------------------


def build_terrain() -> Image.Image:
    """512×64 playable strip with gaps and organic texture (PAL1)."""
    im = new_indexed(512, 64, PAL1, 0)
    gaps = ((150, 198), (300, 340), (420, 448))

    def in_gap(x: int) -> bool:
        return any(a <= x < b for a, b in gaps)

    for x in range(512):
        if in_gap(x):
            continue
        # top outline
        put(im, x, 0, 7)
        # grass band 1..8 — thicker + cluster blades (R2-G4)
        for y in range(1, 8):
            n = _hash01(x, y, 31)
            if y <= 2:
                idx = 1 if n > 0.30 else 2
            elif y <= 5:
                idx = 2 if n > 0.4 else 3
            else:
                idx = 3 if n > 0.35 else 2
            put(im, x, y, idx)
        # irregular tuft clusters (not fixed every N px)
        if _hash01(x, 0, 33) > 0.55:
            put(im, x, 1, 1)
            put(im, x, 0, 1)
        if _hash01(x, 1, 35) > 0.72:
            put(im, x, 1, 2)
            put(im, x, 0, 2)
        if _hash01(x, 2, 37) > 0.85:
            put(im, x, 0, 1)
            if x + 1 < 512 and not in_gap(x + 1):
                put(im, x + 1, 0, 1)
        # dirt with HORIZONTAL strata + sparse pebbles (not pure hash soup)
        for y in range(8, 62):
            depth = (y - 8) / 54.0
            # strata bands ~8px
            band = (y // 8) % 3
            n2 = _hash01(x, y // 3, 43)
            if n2 < 0.05:
                idx = 11  # stone
            elif band == 0:
                idx = 4 if n2 < 0.55 else 5
            elif band == 1:
                idx = 5 if n2 < 0.6 else 6
            else:
                idx = 6 if depth > 0.35 else 5
            # occasional root/vein
            if n2 > 0.93 and y > 18:
                idx = 6
            put(im, x, y, idx)
        put(im, x, 63, 6)
        # flowers irregular
        if _hash01(x, 3, 51) > 0.92:
            put(im, x, 2, 12)
            put(im, x, 3, 3)
        if _hash01(x, 4, 53) > 0.94:
            put(im, x, 2, 13)
        # vine roots near gaps
        for a, b in gaps:
            if abs(x - a) < 3 or abs(x - b) < 3:
                for vy in range(1, 14):
                    if _hash01(x, vy, 47) > 0.45:
                        put(im, x, vy, 3 if vy < 6 else 14)

    # cliff faces
    for a, b in gaps:
        for y in range(1, 28):
            put(im, a - 1, y, 7)
            put(im, b, y, 7)
            if y > 6:
                put(im, a - 2, y, 6 if y & 1 else 5)
                put(im, b + 1, y, 6 if y & 1 else 5)
        # hanging vine
        for k in range(10):
            put(im, a, 1 + k, 3 if k < 4 else 14)
            put(im, b - 1, 2 + k, 3 if k < 5 else 14)

    # larger surface rocks
    for rx, ry in ((40, 18), (80, 30), (220, 22), (270, 36), (370, 20), (400, 40), (480, 28)):
        if in_gap(rx):
            continue
        for dy in range(-2, 3):
            for dx in range(-3, 4):
                if dx * dx + dy * dy * 2 <= 10:
                    put(im, rx + dx, ry + dy, 11 if dy < 1 else 7)
    return stamp_full_palette(im)


# ---------------------------------------------------------------------------
# PARTICLE dust (G6 polish) — 3 frames expansion/dissipation, 8×8 cells
# ---------------------------------------------------------------------------


def build_particle() -> Image.Image:
    """24×8 sheet: 3 frames of soft dust puff (PAL2-safe warm greys via PAL1 indices)."""
    # Particle sprite uses its own embedded palette; use warm dirt-ish tones.
    # Indices for spr_ph_particle — keep absolute 0..15 with body in 4-7 / 11.
    pal = list(PAL1)
    im = new_indexed(24, 8, pal, 0)
    # Frame 0: tight core
    for f, (cx, size, hollow) in enumerate(
        (
            (4, 2, False),
            (12, 3, False),
            (20, 3, True),
        )
    ):
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                d2 = dx * dx + dy * dy
                if hollow and d2 < (size - 1) * (size - 1):
                    continue
                if d2 <= size * size:
                    idx = 4 if d2 <= 1 else (5 if d2 <= 4 else 11)
                    put(im, cx + dx, 4 + dy, idx)
        # dissipating dots frame 2
        if f == 2:
            for ox, oy in ((-4, -2), (4, -1), (-3, 2), (3, 3), (0, -3)):
                put(im, cx + ox, 4 + oy, 11)
    return stamp_full_palette(im)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    GFX.mkdir(parents=True, exist_ok=True)
    SPR = ROOT / "res" / "sprites"
    SPR.mkdir(parents=True, exist_ok=True)

    layers = {
        "sky": build_sky(),
        "mount": build_mountains(),
        "forest": build_forest(),
        "hills": build_hills(),
        "terrain": build_terrain(),
    }
    report: dict = {}
    for name, im in layers.items():
        path = OUT / f"ph_{name}_r5.png"
        im.save(path)
        a = np.array(im)
        report[name] = {
            "path": str(path),
            "size": [im.width, im.height],
            "opaque_pct": float((a > 0).mean() * 100),
            "unique": [int(x) for x in np.unique(a)],
        }
        print(name, f"{report[name]['opaque_pct']:.1f}%", "idx", report[name]["unique"])
        if args.install:
            bak = GFX / f"ph_{name}_pre_r5_backup.png"
            dst = GFX / f"ph_{name}.png"
            if dst.exists() and not bak.exists():
                bak.write_bytes(dst.read_bytes())
            im.save(dst)
            print("  installed", dst.name)

    part = build_particle()
    ppath = OUT / "ph_particle_r5.png"
    part.save(ppath)
    report["particle"] = {
        "path": str(ppath),
        "size": [part.width, part.height],
    }
    print("particle", report["particle"]["size"])
    if args.install:
        bak = SPR / "ph_particle_pre_r5_backup.png"
        dst = SPR / "ph_particle.png"
        if dst.exists() and not bak.exists():
            bak.write_bytes(dst.read_bytes())
        part.save(dst)
        print("  installed", dst.name)

    (OUT / "layers_r5_report.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
