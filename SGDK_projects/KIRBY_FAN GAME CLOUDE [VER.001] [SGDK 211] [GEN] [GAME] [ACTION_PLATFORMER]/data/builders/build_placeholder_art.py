#!/usr/bin/env python3
"""Generate FASE 1 placeholder art that already obeys doc/PALETTES.md.

Placeholder does NOT mean "ignore the contract". Every pixel here is on the
RGB333 lattice and every palette matches the canonical allocation, so the
colour and value-ladder gates are meaningful from the first build. Only the
artistic quality is provisional.

The three PAL0 strips are written with a byte-identical 16-colour palette so
the runtime can load ONE palette into PAL0 and draw all three from it.

Run:  python3 data/builders/build_placeholder_art.py
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("PIL is required: this host already stages it, see ensure_linux_python_deps.sh")

ROOT = Path(__file__).resolve().parents[2]
GFX = ROOT / "res" / "gfx"
SPR = ROOT / "res" / "sprites"
BGS = ROOT / "res" / "bgs"

# --- Legal RGB333 lattice -------------------------------------------------
LATTICE = (0, 36, 73, 109, 146, 182, 219, 255)


def check(*colors: tuple[int, int, int]) -> None:
    for c in colors:
        for ch in c:
            if ch not in LATTICE:
                raise SystemExit(f"ILLEGAL RGB333 channel {ch} in {c}")


def lum(c: tuple[int, int, int]) -> float:
    """Canonical sRGB luminance from doc/PALETTES.md section 1.2."""
    return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255.0


KEY = (255, 0, 255)          # index 0 everywhere: transparent

# --- PAL0: distant background (sky / mountains / hills) -------------------
# doc/PALETTES.md section 4.1
PAL0 = [
    KEY,                     # 0  transparent
    (109, 182, 255),         # 1  sky top
    (146, 182, 255),         # 2  sky
    (182, 219, 255),         # 3  sky
    (219, 219, 255),         # 4  sky
    (255, 219, 182),         # 5  sky low
    (255, 255, 182),         # 6  sky horizon (cream)
    (255, 255, 255),         # 7  cloud light
    (219, 219, 255),         # 8  cloud shadow
    (146, 146, 182),         # 9  mountain light
    (109, 109, 146),         # 10 mountain dark
    (109, 182, 73),          # 11 hill light
    (73, 146, 73),           # 12 hill mid
    (36, 109, 36),           # 13 hill dark
    (109, 73, 36),           # 14 distant trunk
    (36, 36, 73),            # 15 background outline
]

# --- PAL1: near background (terrain) + foreground layer -------------------
PAL1 = [
    KEY,                     # 0  transparent
    (73, 182, 73),           # 1  grass top light
    (36, 146, 36),           # 2  grass top mid
    (36, 109, 36),           # 3  grass top dark
    (146, 109, 73),          # 4  dirt light
    (109, 73, 36),           # 5  dirt mid
    (73, 36, 0),             # 6  dirt dark
    (36, 36, 36),            # 7  terrain outline
    (109, 182, 255),         # 8  waterfall A   (cycling range)
    (182, 219, 255),         # 9  waterfall B   (cycling range)
    (255, 255, 255),         # 10 waterfall C   (cycling range)
    (146, 146, 146),         # 11 rock
    (255, 182, 219),         # 12 flower A
    (255, 255, 146),         # 13 flower B
    (36, 109, 36),           # 14 foreground light
    (0, 73, 36),             # 15 foreground dark
]

# --- PAL2: Kirby + HUD (canonical ramp, doc/PALETTES.md section 3.1) ------
PAL2 = [
    KEY,                     # 0  transparent
    (255, 219, 255),         # 1  pink highlight
    (255, 182, 219),         # 2  pink light   <- carries the body
    (255, 146, 182),         # 3  pink base
    (219, 73, 146),          # 4  pink shadow
    (146, 36, 109),          # 5  pink deep
    (109, 36, 73),           # 6  outline
    (219, 73, 73),           # 7  foot light
    (146, 36, 36),           # 8  foot dark
    (36, 36, 73),            # 9  eye
    (255, 255, 255),         # 10 eye shine / HUD white
    (146, 146, 146),         # 11 HUD bar back
    (255, 146, 182),         # 12 HUD life fill
    (255, 219, 146),         # 13 enemy A
    (182, 109, 219),         # 14 enemy B
    (109, 219, 219),         # 15 enemy C
]

for p in (PAL0, PAL1, PAL2):
    check(*p)


def new_indexed(w: int, h: int, palette: list[tuple[int, int, int]], fill: int = 0) -> Image.Image:
    im = Image.new("P", (w, h), fill)
    flat: list[int] = []
    for c in palette:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - len(palette)))
    im.putpalette(flat)
    return im


def band(im: Image.Image, y0: int, y1: int, idx: int) -> None:
    for y in range(y0, min(y1, im.height)):
        for x in range(im.width):
            im.putpixel((x, y), idx)


# =========================================================================
# CAMADA 1 - sky. 512x80. Flat horizontal bands + a few clouds.
# Bands are flat so rescomp tile dedup collapses this to very few tiles.
# =========================================================================
def build_sky() -> Image.Image:
    # The sky has NO opaque fill: only clouds. The gradient is the VDP backdrop
    # colour, rewritten once per band by the H-interrupt, so it shows through
    # wherever both planes are transparent. Twelve visible gradient bands cost
    # ONE CRAM entry and ZERO tiles. This is the economy documented in
    # doc/PALETTES.md section 4.1, taken further than the doc assumed.
    im = new_indexed(512, 80, PAL0, 0)
    # clouds on the 8px grid so dedup still works well
    for cx in (48, 200, 368):
        for dy, (w, idx) in enumerate(((24, 7), (40, 7), (32, 8))):
            y = 24 + dy * 8
            for x in range(cx, cx + w):
                for yy in range(y, y + 8):
                    if 0 <= x < 512 and 0 <= yy < 80:
                        im.putpixel((x, yy), idx)
    return im


# =========================================================================
# CAMADA 2 - distant mountains. 512x56. Two-tone triangles.
# =========================================================================
def build_mountains() -> Image.Image:
    im = new_indexed(512, 56, PAL0, 0)
    peaks = ((40, 48), (150, 40), (250, 52), (360, 44), (460, 48))
    for px, ph in peaks:
        for dy in range(ph):
            y = 56 - 1 - dy
            half = (ph - dy)
            for x in range(px - half, px + half):
                if 0 <= x < 512:
                    im.putpixel((x, y), 9 if x < px else 10)
    return im


# =========================================================================
# CAMADA 3 - near hills + trees. 512x88. Three-tone rounded mounds.
# =========================================================================
def build_hills() -> Image.Image:
    im = new_indexed(512, 88, PAL0, 0)
    mounds = ((60, 56), (180, 48), (300, 60), (430, 52))
    for mx, mh in mounds:
        for dy in range(mh):
            y = 88 - 1 - dy
            half = int((mh - dy) * 1.6)
            idx = 11 if dy > mh - 12 else (12 if dy > mh // 3 else 13)
            for x in range(mx - half, mx + half):
                if 0 <= x < 512:
                    im.putpixel((x, y), idx)
    # simple round trees
    for tx in (110, 240, 380, 480):
        for yy in range(88 - 34, 88 - 16):
            for xx in range(tx - 3, tx + 3):
                if 0 <= xx < 512:
                    im.putpixel((xx, yy), 14)
        for yy in range(88 - 50, 88 - 30):
            r = 12 - abs(yy - (88 - 40))
            for xx in range(tx - r, tx + r):
                if 0 <= xx < 512:
                    im.putpixel((xx, yy), 13 if abs(xx - tx) > r - 4 else 12)
    return im


# =========================================================================
# CAMADA 4 - playable terrain strip. 512x64, PAL1.
# Row 0-1 grass top, rest dirt. Index 0 stays transparent for gaps.
# =========================================================================
def build_terrain() -> Image.Image:
    im = new_indexed(512, 64, PAL1, 0)
    gaps = ((160, 208), (320, 352))
    for x in range(512):
        if any(a <= x < b for a, b in gaps):
            continue
        im.putpixel((x, 0), 7)
        for y in range(1, 4):
            im.putpixel((x, y), 1)
        for y in range(4, 7):
            im.putpixel((x, y), 2)
        for y in range(7, 9):
            im.putpixel((x, y), 3)
        for y in range(9, 63):
            im.putpixel((x, y), 4 if (x // 8 + y // 8) % 3 == 0 else 5)
        im.putpixel((x, 63), 6)
    return im


# =========================================================================
# CAMADA 5 - foreground grass, drawn as SPRITES (32x16 tuft).
# =========================================================================
def build_foreground() -> Image.Image:
    im = new_indexed(32, 16, PAL1, 0)
    for bx in (2, 10, 18, 26):
        for i in range(14):
            y = 15 - i
            w = max(1, 3 - i // 5)
            for x in range(bx - w, bx + w):
                if 0 <= x < 32:
                    im.putpixel((x, y), 15 if i > 7 else 14)
    return im


# =========================================================================
# KIRBY sprite sheet, PAL2. 8 frames of 32x32 = 256x32.
# idle, run x4, jump, float x2
# =========================================================================
def blob(im: Image.Image, ox: int, cx: int, cy: int, r: int,
         squash: float = 1.0, cheeks: bool = False) -> None:
    for y in range(-r - 2, r + 3):
        for x in range(-r - 4, r + 5):
            yy = y / squash
            d = (x * x + yy * yy) ** 0.5
            px, py = ox + cx + x, cy + y
            if not (0 <= px - ox < 32 and 0 <= py < 32):
                continue
            if d <= r - 3:
                idx = 2
            elif d <= r - 1:
                idx = 3
            elif d <= r:
                idx = 4
            elif d <= r + 0.9:
                idx = 6
            else:
                continue
            im.putpixel((px, py), idx)
    # highlight
    for y in range(cy - r + 3, cy - r + 8):
        for x in range(cx - r + 5, cx - r + 12):
            if 0 <= x < 32 and 0 <= y < 32:
                if im.getpixel((ox + x, y)) in (2, 3):
                    im.putpixel((ox + x, y), 1)
    if cheeks:
        for side in (-1, 1):
            bcx = cx + side * (r - 1)
            for y in range(cy - 2, cy + 6):
                for x in range(bcx - 5, bcx + 6):
                    if 0 <= x < 32 and 0 <= y < 32:
                        d = ((x - bcx) ** 2 + ((y - cy - 2) * 1.4) ** 2) ** 0.5
                        if d <= 4:
                            im.putpixel((ox + x, y), 2 if d < 3 else 6)


def eyes(im: Image.Image, ox: int, cx: int, cy: int, spread: int = 5) -> None:
    for side in (-1, 1):
        ex = cx + side * spread
        for y in range(cy - 6, cy + 1):
            for x in range(ex - 1, ex + 2):
                if 0 <= x < 32 and 0 <= y < 32:
                    im.putpixel((ox + x, y), 9)
        if 0 <= ex < 32 and 0 <= cy - 6 < 32:
            im.putpixel((ox + ex, cy - 6), 10)


def feet(im: Image.Image, ox: int, cx: int, cy: int, phase: int) -> None:
    offsets = {0: (-7, 7), 1: (-9, 5), 2: (-7, 7), 3: (-5, 9)}[phase % 4]
    for fx in offsets:
        for y in range(cy, cy + 5):
            for x in range(cx + fx - 4, cx + fx + 4):
                if 0 <= x < 32 and 0 <= y < 32:
                    d = ((x - (cx + fx)) ** 2 + ((y - cy - 2) * 1.6) ** 2) ** 0.5
                    if d <= 3.2:
                        im.putpixel((ox + x, y), 7 if d < 2.2 else 8)


def build_kirby() -> Image.Image:
    im = new_indexed(256, 32, PAL2, 0)
    # frame 0: idle
    blob(im, 0, 16, 16, 11)
    feet(im, 0, 16, 24, 0)
    eyes(im, 0, 16, 14)
    # frames 1-4: run
    for f in range(4):
        ox = 32 * (1 + f)
        blob(im, ox, 16, 16, 11, squash=1.05)
        feet(im, ox, 16, 24, f)
        eyes(im, ox, 17, 14, 4)
    # frame 5: jump
    blob(im, 160, 16, 15, 11, squash=0.92)
    feet(im, 160, 16, 23, 1)
    eyes(im, 160, 16, 13)
    # frames 6-7: float (inflated cheeks, per R2-01 lesson: cheeks must break
    # the silhouette outward or they vanish at 28px)
    for f in range(2):
        ox = 32 * (6 + f)
        blob(im, ox, 16, 16 + f, 10, squash=0.95, cheeks=True)
        feet(im, ox, 16, 24, 0)
        eyes(im, ox, 16, 13)
    return im


# =========================================================================
# ENEMY (Waddle-Dee-like) + inhale particle, PAL2 indices 13..15 + shared ramp.
# 2 frames of 16x16 = 32x16. One hardware sprite each (2x2 tiles).
# =========================================================================
def build_enemy() -> Image.Image:
    im = new_indexed(32, 16, PAL2, 0)
    for f in range(2):
        ox = f * 16
        for y in range(2, 14):
            for x in range(2, 14):
                d = (((x - 8) ** 2) + ((y - 8) ** 2)) ** 0.5
                if d <= 5.0:
                    im.putpixel((ox + x, y), 13)
                elif d <= 6.0:
                    im.putpixel((ox + x, y), 6)
        # eyes
        for ex in (6, 10):
            im.putpixel((ox + ex, 7), 9)
            im.putpixel((ox + ex, 8), 9)
        # feet alternate between the two frames
        fy = 13
        for fx in ((4, 10) if f == 0 else (5, 9)):
            im.putpixel((ox + fx, fy), 8)
            im.putpixel((ox + fx + 1, fy), 8)
    return im


# Inhale particle: a small 8x8 star pulled toward Kirby. PAL2 whites/pinks.
def build_particle() -> Image.Image:
    im = new_indexed(24, 8, PAL2, 0)
    for f, r in enumerate((3, 2, 1)):
        ox = f * 8
        for y in range(8):
            for x in range(8):
                if abs(x - 4) + abs(y - 4) <= r:
                    im.putpixel((ox + x, y), 10 if r > 2 else 1)
    return im


# =========================================================================
# WHISPY WOODS placeholder art. PAL3 is the boss palette (doc/PALETTES.md 4.2).
# Every piece is separable because the boss is assembled from articulated
# sprites at runtime, not drawn as one image.
# =========================================================================
PAL3_BOSS = [
    (255, 0, 255),      # 0 transparent key
    (182, 109, 73),     # 1 bark light
    (146, 73, 36),      # 2 bark mid
    (109, 36, 0),       # 3 bark dark
    (73, 36, 0),        # 4 bark outline
    (109, 182, 73),     # 5 leaf light
    (73, 146, 36),      # 6 leaf mid
    (36, 109, 36),      # 7 leaf dark
    (255, 255, 255),    # 8 eye white
    (36, 36, 73),       # 9 iris
    (73, 36, 0),        # 10 brow
    (219, 36, 36),      # 11 apple
    (255, 255, 255),    # 12 air puff light
    (182, 219, 255),    # 13 air puff mid
    (255, 219, 146),    # 14 (spare, kept free for the damage flash)
    (255, 255, 255),    # 15 (spare)
]


# One branch segment, 16x16. Seven of these chain into an articulated branch.
# Deliberately symmetric so the same tile reads at any rotation step.
def build_branch_segment() -> Image.Image:
    im = new_indexed(16, 16, PAL3_BOSS, 0)
    for y in range(4, 12):
        for x in range(0, 16):
            edge = (y == 4) or (y == 11)
            im.putpixel((x, y), 4 if edge else (1 if y < 7 else (2 if y < 10 else 3)))
    return im


# Boss face: eyes + brow + mouth as one 48x32 block (2 frames: calm, angry).
def build_boss_face() -> Image.Image:
    im = new_indexed(96, 32, PAL3_BOSS, 0)
    for f in range(2):
        ox = f * 48
        for ex in (10, 30):
            for y in range(8, 20):
                for x in range(ex, ex + 10):
                    im.putpixel((ox + x, y), 8)
            for y in range(12, 18):
                for x in range(ex + 3, ex + 7):
                    im.putpixel((ox + x, y), 9)
        brow_y = 5 if f == 0 else 7
        for x in range(8, 42):
            im.putpixel((ox + x, brow_y), 10)
            im.putpixel((ox + x, brow_y + 1), 10)
        for x in range(16, 34):
            im.putpixel((ox + x, 25), 4)
            im.putpixel((ox + x, 26), 3)
    return im


# Apple projectile, 16x16, 2 frames.
def build_apple() -> Image.Image:
    im = new_indexed(32, 16, PAL3_BOSS, 0)
    for f in range(2):
        ox = f * 16
        for y in range(3, 14):
            for x in range(3, 13):
                d = (((x - 8) ** 2) + ((y - 8) ** 2)) ** 0.5
                if d <= 4.5:
                    im.putpixel((ox + x, y), 11)
                elif d <= 5.4:
                    im.putpixel((ox + x, y), 4)
        im.putpixel((ox + 8, 2 if f == 0 else 3), 7)
    return im


# Trunk tiles for BG_A: 64x96 of bark with vertical grooves.
def build_trunk() -> Image.Image:
    im = new_indexed(64, 96, PAL3_BOSS, 0)
    for y in range(96):
        for x in range(64):
            groove = (x % 8) in (0, 1)
            im.putpixel((x, y), 3 if groove else (2 if (x % 8) < 5 else 1))
    for y in range(0, 96, 16):
        for x in range(64):
            im.putpixel((x, y), 4)
    return im


# =========================================================================
# TITLE SCREEN. Follows doc/art/AI_IMAGE_PROMPT_PACK.md request R1-07:
# night sky in COUNTABLE horizontal bands (they become H-int stops), a dark
# foreground silhouette in few colours, stars in discrete sizes, and deliberate
# empty space in the upper third for the logo.
# =========================================================================
PAL_TITLE = [
    (255, 0, 255),      # 0 transparent key
    (36, 36, 109),      # 1 hill silhouette
    (36, 36, 73),       # 2 hill shadow
    (73, 36, 109),      # 3 tree silhouette
    (255, 255, 255),    # 4 star bright
    (219, 219, 255),    # 5 star dim
    (255, 182, 219),    # 6 logo light   (canonical Kirby ramp)
    (255, 146, 182),    # 7 logo base
    (219, 73, 146),     # 8 logo shadow
    (146, 36, 109),     # 9 logo deep
    (109, 36, 73),      # 10 logo outline
    (255, 219, 255),    # 11 logo highlight
    (146, 146, 219),    # 12 cloud far
    (109, 109, 182),    # 13 cloud far shadow
    (73, 73, 146),      # 14 spare
    (36, 36, 36),       # 15 spare
]


# Hill + tree silhouette strip, 512x64, sits at the bottom of the screen.
def build_title_hill() -> Image.Image:
    import math as _m
    im = new_indexed(512, 64, PAL_TITLE, 0)
    for x in range(512):
        h = 26 + int(14 * _m.sin(x / 61.0)) + int(6 * _m.sin(x / 17.0))
        for y in range(64 - h, 64):
            im.putpixel((x, y), 1 if y < 64 - h + 4 else 2)
    # one tree, deliberately off-centre
    tx = 96
    for y in range(18, 44):
        for x in range(tx - 2, tx + 3):
            im.putpixel((x, y), 3)
    for y in range(4, 24):
        r = int(13 * (1.0 - abs(y - 13) / 13.0)) + 3
        for x in range(tx - r, tx + r + 1):
            if 0 <= x < 512:
                im.putpixel((x, y), 3)
    return im


# Star field, 512x96, transparent background so the sky gradient shows through.
def build_title_stars() -> Image.Image:
    im = new_indexed(512, 96, PAL_TITLE, 0)
    seed = 20260806
    for _ in range(150):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        x = (seed >> 8) % 512
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        y = (seed >> 8) % 96
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        kind = (seed >> 8) % 3
        col = 4 if kind == 0 else 5
        im.putpixel((x, y), col)
        if kind == 2 and x + 1 < 512 and y + 1 < 96:
            im.putpixel((x + 1, y), col)
            im.putpixel((x, y + 1), col)
    return im


# Blocky logo built from the canonical pink ramp. Placeholder lettering: this is
# a shape study, not final typography.
def build_title_logo() -> Image.Image:
    im = new_indexed(224, 48, PAL_TITLE, 0)
    glyphs = {
        "K": ["#..#", "#.#.", "##..", "#.#.", "#..#"],
        "I": ["###", ".#.", ".#.", ".#.", "###"],
        "R": ["###.", "#..#", "###.", "#.#.", "#..#"],
        "B": ["###.", "#..#", "###.", "#..#", "###."],
        "Y": ["#...#", ".#.#.", "..#..", "..#..", "..#.."],
    }
    px = 8
    ox = 6
    for ch in "KIRBY":
        g = glyphs[ch]
        w = len(g[0])
        for gy, row in enumerate(g):
            for gx, c in enumerate(row):
                if c != "#":
                    continue
                for yy in range(px):
                    for xx in range(px):
                        X = ox + gx * px + xx
                        Y = 6 + gy * px + yy
                        if not (0 <= X < 224 and 0 <= Y < 48):
                            continue
                        edge = (xx == 0 or yy == 0 or
                                xx == px - 1 or yy == px - 1)
                        band = (gy * px + yy) * 5 // (5 * px)
                        col = 10 if edge else (11, 6, 7, 8, 9)[min(band, 4)]
                        im.putpixel((X, Y), col)
        ox += (w + 1) * px
    return im


PAL_ABILITY = [
    (255, 0, 255),      # 0 key
    (255, 255, 182),    # 1 fire hot
    (255, 182, 36),     # 2 fire mid
    (219, 73, 0),       # 3 fire deep
    (255, 255, 146),    # 4 beam bright
    (255, 219, 36),     # 5 beam mid
    (219, 219, 255),    # 6 cutter light
    (146, 182, 219),    # 7 cutter mid
    (73, 109, 146),     # 8 cutter dark
    (182, 182, 182),    # 9 stone light
    (109, 109, 109),    # 10 stone mid
    (73, 73, 73),       # 11 stone dark
    (255, 255, 255),    # 12 sword white
    (146, 255, 255),    # 13 sword cyan
    (36, 146, 182),     # 14 sword deep
    (0, 0, 0),          # 15 outline
]


# 5 abilities x 3 frames as one 240x16 strip.
# doc/art/AI_IMAGE_PROMPT_PACK.md R1-04 requires each ability be identifiable by
# SHAPE as well as colour, so a colourblind player can still tell them apart:
# fire is a round plume, beam a jagged bolt, cutter a hollow crescent, stone a
# hard-edged block, sword a thin swept arc.
def build_ability_fx():
    import math as _m
    im = new_indexed(240, 16, PAL_ABILITY, 0)

    def blob(ox, cx, cy, r, cols):
        for y in range(16):
            for x in range(16):
                d = _m.hypot(x - cx, y - cy)
                if d <= r:
                    idx = min(len(cols) - 1, int(d / max(r, 1) * len(cols)))
                    im.putpixel((ox + x, y), cols[idx])

    for f in range(3):
        blob(f * 16, 5 + f * 2, 8, 3 + f * 1.6, [1, 2, 3])

    for f in range(3):
        ox = 48 + f * 16
        for i in range(0, 14):
            x = 2 + i
            y = 8 + int(3 * _m.sin((i + f * 2) * 1.2))
            im.putpixel((ox + x, y), 4)
            im.putpixel((ox + x, y + 1), 5)

    for f in range(3):
        ox = 96 + f * 16
        for y in range(16):
            for x in range(16):
                d = _m.hypot(x - 8, y - 8)
                d2 = _m.hypot(x - (11 + f), y - 8)
                if 5.0 <= d <= 7.0 and d2 > 6.0:
                    im.putpixel((ox + x, y), 6 if d < 6 else 7)
                    if d > 6.6:
                        im.putpixel((ox + x, y), 8)

    for f in range(3):
        ox = 144 + f * 16
        w = 5 + f
        for y in range(8 - w, 8 + w):
            for x in range(8 - w, 8 + w):
                edge = (abs(x - 8) >= w - 1) or (abs(y - 8) >= w - 1)
                im.putpixel((ox + x, y), 11 if edge else (9 if (x + y) % 3 else 10))

    for f in range(3):
        ox = 192 + f * 16
        for i in range(16):
            a = (-0.9 + f * 0.35) + i * 0.11
            x = int(8 + 6.5 * _m.cos(a))
            y = int(8 + 6.5 * _m.sin(a))
            if 0 <= x < 16 and 0 <= y < 16:
                im.putpixel((ox + x, y), 12)
                if y + 1 < 16:
                    im.putpixel((ox + x, y + 1), 13)
                if y + 2 < 16:
                    im.putpixel((ox + x, y + 2), 14)
    return im


# Shadow/Highlight OPERATOR sprite, 32x32, 2 frames.
#
# Every opaque pixel is palette index 14. doc/PALETTES.md 2.3 reserves PAL3[14]
# as the HIGHLIGHT operator and PAL3[15] as the SHADOW operator: on this hardware
# a sprite pixel with those indices does not draw a colour, it BRIGHTENS or
# DARKENS whatever is underneath. That is the only real pseudo-transparency the
# Mega Drive has, and R5 is the effect that finally exercises the reservation.
#
# The pool BRIGHTENS rather than the surroundings darkening, deliberately:
# darkening everything else would need priority-0 background tiles, which gate
# P5 forbids for exactly the right reason (an unintentional priority-0 tile is
# indistinguishable from this). Brightening costs a handful of sprites and keeps
# the P5 contract intact.
def build_light_operator():
    import math as _m
    pal = [(255, 0, 255)] + [(0, 0, 0)] * 13 + [(255, 255, 255), (0, 0, 0)]
    im = new_indexed(64, 32, pal, 0)
    for f in range(2):
        ox = f * 32
        r = 15 - f * 2
        for y in range(32):
            for x in range(32):
                if _m.hypot(x - 16, y - 16) <= r:
                    im.putpixel((ox + x, y), 14)
    return im


def save(im: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    used = {i for _, i in im.getcolors(1 << 16)}
    print(f"  {path.relative_to(ROOT)}  {im.width}x{im.height}  "
          f"indices usados: {len(used)}")


def main() -> int:
    print("gerando arte provisoria da FASE 1 (contrato de cor respeitado)")
    save(build_sky(), GFX / "ph_sky.png")
    save(build_mountains(), GFX / "ph_mount.png")
    save(build_hills(), GFX / "ph_hills.png")
    save(build_terrain(), GFX / "ph_terrain.png")
    save(build_foreground(), SPR / "ph_fg.png")
    save(build_kirby(), SPR / "ph_kirby.png")
    save(build_enemy(), SPR / "ph_enemy.png")
    save(build_particle(), SPR / "ph_particle.png")
    save(build_branch_segment(), SPR / "ph_branch.png")
    save(build_boss_face(), SPR / "ph_boss_face.png")
    save(build_apple(), SPR / "ph_apple.png")
    save(build_trunk(), BGS / "ph_trunk.png")
    save(build_title_hill(), BGS / "ph_title_hill.png")
    save(build_title_stars(), BGS / "ph_title_stars.png")
    save(build_title_logo(), GFX / "ph_title_logo.png")
    save(build_ability_fx(), SPR / "ph_ability_fx.png")
    save(build_light_operator(), SPR / "ph_light.png")

    print("\nescada de valor das camadas (formula canonica sRGB):")
    groups = {
        "1 ceu": [PAL0[i] for i in (1, 2, 3, 4, 5, 6)],
        "2 montanhas": [PAL0[i] for i in (9, 10)],
        "3 colinas": [PAL0[i] for i in (11, 12, 13)],
        "4 terreno": [PAL1[i] for i in (1, 2, 3, 4, 5, 6)],
        "5 primeiro plano": [PAL1[i] for i in (14, 15)],
    }
    prev = None
    ok = True
    for name, cols in groups.items():
        L = sum(lum(c) for c in cols) / len(cols)
        flag = ""
        if prev is not None and L >= prev:
            flag = "  <-- NAO MONOTONICO"
            ok = False
        print(f"  {name:18} L={L:.4f}{flag}")
        prev = L
    print("\nescada monotonica decrescente:", "SIM" if ok else "NAO")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
