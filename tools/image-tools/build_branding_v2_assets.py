#!/usr/bin/env python3
"""Build branding v2 identity assets for the SMOKE_TEST template.

Generates three identity bitmap fonts and five procedural FX sprite sheets
deterministically. Every output is 8px aligned, 16-color indexed, and uses
SGDK-safe color snapping.

Outputs (in res/branding/):
  - font_forge_8x12.png        8x16 slab serif strip, 37 glyphs
  - font_terminal_7x9.png      7x16 mono-phosphor strip, 37 glyphs
  - font_crest_8x16.png        8x16 bold display serif strip, 37 glyphs
  - fx_spark_8x8.png           4 frames of 8x8 spark
  - fx_monogram_mo_16x16.png   12 frames of 16x16 monogram rotation
  - fx_pen_8x16.png            3 frames of 8x16 quill pen
  - fx_shield_16x16.png        4 frames of 16x16 shield scaling
  - fx_glow_16x16.png          1 frame of 16x16 radial glow
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "SGDK_projects" / "SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]"
RES_DIR = PROJECT / "res" / "branding"
LOG_DIR = PROJECT / "out" / "logs"
RES_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def snap(v: int) -> int:
    return max(0, min(255, int(round(v / 17.0)) * 17)) if v >= 0 else 0


def snap_rgb(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return (snap(rgb[0]), snap(rgb[1]), snap(rgb[2]))


def find_closest_palette_index(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> int:
    best_idx = 0
    best_dist = 1 << 30
    for i, p in enumerate(palette):
        d = (p[0] - rgb[0]) ** 2 + (p[1] - rgb[1]) ** 2 + (p[2] - rgb[2]) ** 2
        if d < best_dist:
            best_dist = d
            best_idx = i
    return best_idx


@dataclass(frozen=True)
class BuiltAsset:
    name: str
    file: Path
    size: tuple[int, int]
    palette_entries: int
    used_indexes: int
    transparent_index_0: bool
    sha256: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def save_indexed_png(
    rgba: Image.Image,
    path: Path,
    palette: list[tuple[int, int, int]],
    transparent: bool,
    transparent_index: int = 0,
) -> BuiltAsset:
    snapped_palette = [snap_rgb(c) for c in palette]
    out = Image.new("P", rgba.size)
    pixels: list[int] = []
    for r, g, b, a in rgba.convert("RGBA").getdata():
        if transparent and a < 16:
            pixels.append(transparent_index)
        else:
            pixels.append(find_closest_palette_index(snap_rgb((r, g, b)), snapped_palette))
    out.putdata(pixels)
    flat: list[int] = []
    for c in snapped_palette:
        flat.extend(c)
    if len(flat) < 768:
        flat.extend([0, 0, 0] * (256 - len(flat) // 3))
    out.putpalette(flat)
    if transparent:
        out.info["transparency"] = transparent_index
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path, format="PNG", optimize=False, bits=4)

    with Image.open(path) as saved:
        used = len(set(saved.getdata()))
        transparent0 = int(saved.info.get("transparency", -1)) == transparent_index

    return BuiltAsset(
        name=path.name,
        file=path,
        size=rgba.size,
        palette_entries=len(snapped_palette),
        used_indexes=used,
        transparent_index_0=transparent0,
        sha256=sha256_file(path),
    )


# --- Glyph tables: 5x7 base shapes for the original FONT_5X7 logic ---
# Reused to keep visual continuity with the existing branding system.
GLYPHS_5X7: dict[str, tuple[str, ...]] = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("10010", "10010", "10010", "11111", "00010", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01111", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "11110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

GLYPH_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "


def render_font_forge() -> Image.Image:
    """8x16 slab serif steel gradient. 37 glyphs at 8px = 296px wide.

    Each glyph is 8x16 (2 VDP tiles stacked). Visual treatment adds:
      - 1px top highlight
      - 1px bottom shadow
      - diagonal chanfro on the top-left and bottom-right corners
    """
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 black
        (51, 51, 51),      # 2 dark steel
        (102, 102, 102),   # 3 mid steel
        (153, 153, 153),   # 4 light steel
        (221, 221, 221),   # 5 near-white
        (255, 255, 255),   # 6 white highlight
        (0, 119, 187),     # 7 cyan accent
        (0, 187, 221),     # 8 bright cyan
        (153, 68, 0),      # 9 rust shadow
        (85, 85, 85),      # 10 medium shadow
        (34, 34, 34),      # 11 deep shadow
        (17, 17, 17),      # 12 darker shadow
        (68, 68, 68),      # 13 mid shadow
        (170, 170, 170),   # 14 highlight shadow
        (255, 255, 255),   # 15 unused
    ]

    char_w, char_h = 8, 16
    sheet_w = char_w * len(GLYPH_CHARS)
    sheet_h = char_h
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    for gi, ch in enumerate(GLYPH_CHARS):
        glyph = GLYPHS_5X7[ch]
        ox = gi * char_w + 1  # leave 1px left padding for slab
        oy = 4  # center 7 rows inside 16 with padding

        # main body (white)
        for ry, row in enumerate(glyph):
            for rx, bit in enumerate(row):
                if bit == "1":
                    # main steel body
                    draw.rectangle((ox + rx, oy + ry, ox + rx, oy + ry),
                                   fill=(221, 221, 221, 255))
                    # top highlight (1 row above)
                    if ry == 0:
                        draw.point((ox + rx, oy + ry - 1),
                                   fill=(255, 255, 255, 255))
                    # bottom shadow
                    if ry == 6:
                        draw.point((ox + rx, oy + ry + 1),
                                   fill=(102, 102, 102, 255))
        # bottom slab bar (serif foot)
        draw.line((ox, oy + 8, ox + 6, oy + 8), fill=(102, 102, 102, 255))
        # top slab cap
        draw.line((ox, oy - 1, ox + 6, oy - 1), fill=(255, 255, 255, 255))
        # diagonal chanfro on top-right
        draw.point((ox + 6, oy - 1), fill=(153, 153, 153, 255))
        # diagonal chanfro on bottom-left
        draw.point((ox, oy + 8), fill=(85, 85, 85, 255))

    return sheet, palette


def render_font_terminal() -> Image.Image:
    """8x16 mono-phosphor terminal font. 37 glyphs.

    Visual treatment: thin green stroke with 1px afterglow cyan halo.
    """
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 background
        (0, 34, 0),        # 2 dim phosphor
        (0, 68, 0),        # 3 mid phosphor
        (0, 119, 0),       # 4 bright phosphor
        (0, 187, 0),       # 5 hot green
        (0, 255, 0),       # 6 peak green
        (0, 255, 170),     # 7 cyan afterglow
        (170, 255, 0),     # 8 yellow afterglow
        (255, 221, 0),     # 9 amber cursor
        (255, 170, 0),     # 10 deep amber
        (51, 51, 51),      # 11 scanline dark
        (34, 34, 34),      # 12 scanline darker
        (17, 17, 17),      # 13 scanline darkest
        (102, 102, 102),   # 14 grid line
        (255, 255, 255),   # 15 unused
    ]

    char_w, char_h = 8, 16
    sheet_w = char_w * len(GLYPH_CHARS)
    sheet_h = char_h
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    for gi, ch in enumerate(GLYPH_CHARS):
        glyph = GLYPHS_5X7[ch]
        ox = gi * char_w + 1
        oy = 4
        for ry, row in enumerate(glyph):
            for rx, bit in enumerate(row):
                if bit == "1":
                    # core bright
                    draw.point((ox + rx, oy + ry), fill=(0, 255, 0, 255))
                    # 1px right afterglow
                    draw.point((ox + rx + 1, oy + ry), fill=(0, 255, 170, 100))
                    # 1px down afterglow
                    draw.point((ox + rx, oy + ry + 1), fill=(0, 187, 0, 100))
        # subtle background scanline
        for sy in range(0, 16, 2):
            draw.line((gi * char_w, sy, (gi + 1) * char_w, sy),
                      fill=(17, 17, 17, 40))

    return sheet, palette


def render_font_crest() -> Image.Image:
    """8x16 bold display serif with gold gradient. 37 glyphs.

    Visual treatment: thick gold body with dark red shadow and bright
    yellow highlight on the upper-left edges.
    """
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 black
        (68, 0, 0),        # 2 deep red shadow
        (119, 0, 0),       # 3 dark red
        (170, 0, 0),       # 4 mid red
        (221, 0, 0),       # 5 bright red
        (255, 68, 0),      # 6 orange
        (255, 136, 0),     # 7 dark gold
        (255, 187, 0),     # 8 mid gold
        (255, 221, 68),    # 9 bright gold
        (255, 255, 136),   # 10 near-white gold
        (255, 255, 255),   # 11 highlight
        (51, 17, 0),       # 12 deep brown shadow
        (102, 51, 0),      # 13 brown shadow
        (153, 102, 0),     # 14 tan shadow
        (221, 170, 68),    # 15 dim gold
    ]

    char_w, char_h = 8, 16
    sheet_w = char_w * len(GLYPH_CHARS)
    sheet_h = char_h
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    for gi, ch in enumerate(GLYPH_CHARS):
        glyph = GLYPHS_5X7[ch]
        ox = gi * char_w + 1
        oy = 4
        for ry, row in enumerate(glyph):
            for rx, bit in enumerate(row):
                if bit == "1":
                    # shadow (down-right offset)
                    draw.point((ox + rx + 1, oy + ry + 1), fill=(68, 0, 0, 255))
                    # main gold body
                    draw.point((ox + rx, oy + ry), fill=(255, 187, 0, 255))
                    # top-left highlight
                    if ry == 0 or rx == 0:
                        draw.point((ox + rx, oy + ry), fill=(255, 255, 136, 255))
        # bold top serif
        draw.line((ox, oy - 1, ox + 6, oy - 1), fill=(255, 68, 0, 255))
        # bold bottom serif
        draw.line((ox, oy + 8, ox + 6, oy + 8), fill=(119, 0, 0, 255))

    return sheet, palette


def render_spark() -> Image.Image:
    """4 frames of 8x8 spark radiating outward."""
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 black core
        (68, 17, 0),       # 2 dim ember
        (136, 51, 0),      # 3 warm ember
        (204, 102, 0),     # 4 orange
        (255, 170, 34),    # 5 bright orange
        (255, 221, 85),    # 6 yellow
        (255, 255, 170),   # 7 hot white
        (170, 170, 170),   # 8 cool ash
        (102, 102, 102),   # 9 ash
        (51, 51, 51),      # 10 dark ash
        (255, 255, 255),   # 11 white
        (34, 34, 34),      # 12 darker ash
        (17, 17, 17),      # 13 darkest ash
        (85, 85, 85),      # 14 mid ash
        (200, 200, 200),   # 15 light ash
    ]

    sheet = Image.new("RGBA", (8 * 4, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    spark_patterns = [
        # frame 0: small central dot
        [(3, 3), (3, 4), (4, 3), (4, 4)],
        # frame 1: + cross
        [(2, 3), (3, 3), (4, 3), (5, 3),
         (3, 2), (3, 4), (4, 2), (4, 4),
         (3, 5), (4, 5), (2, 4), (5, 4)],
        # frame 2: X + cross (8 directions)
        [(1, 3), (2, 2), (3, 1), (4, 1), (5, 2), (6, 3),
         (5, 4), (6, 5), (4, 6), (3, 6), (2, 5), (1, 4),
         (3, 3), (4, 3), (3, 4), (4, 4)],
        # frame 3: dispersing dots
        [(0, 0), (1, 1), (2, 2), (3, 1), (4, 2), (5, 1), (6, 2), (7, 0),
         (0, 7), (1, 6), (2, 5), (3, 6), (4, 5), (5, 6), (6, 5), (7, 7)],
    ]
    for fi, pts in enumerate(spark_patterns):
        for x, y in pts:
            r2 = 7 - fi  # hotter in early frames
            draw.point((fi * 8 + x, y), fill=(255, 170 + fi * 28, 34 + fi * 20, 255))

    return sheet, palette


def render_monogram_mo() -> Image.Image:
    """12 frames of 16x16 monogram M·O rotation. 360° in 30° steps.

    Drawn as a stylized 3D vector cube of letterforms (Treasure-style):
    two stacked letter blocks (M above O) on a thin diagonal axis, each
    frame showing the cube rotated 30 degrees.

    SGDK sprite engine caps each frame at 32x32 pixels (4x4 VDP tiles).
    16x16 keeps us well within budget and reads cleanly at the screen
    scale used in the brand sequence.
    """
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 black background
        (51, 34, 0),       # 2 deep brown
        (102, 68, 0),      # 3 brown
        (153, 102, 0),     # 4 dark gold
        (204, 136, 0),     # 5 mid-dark gold
        (255, 187, 0),     # 6 gold
        (255, 221, 85),    # 7 bright gold
        (255, 255, 170),   # 8 pale gold
        (255, 255, 255),   # 9 white highlight
        (68, 51, 0),       # 10 outline shadow
        (119, 85, 0),      # 11 outline
        (170, 136, 0),     # 12 mid outline
        (221, 187, 68),    # 13 dim gold
        (34, 17, 0),       # 14 deep outline
        (85, 68, 34),      # 15 dim shadow
    ]

    import math
    sheet = Image.new("RGBA", (16 * 12, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    for fi in range(12):
        angle = math.radians(fi * 30.0)
        cx, cy = fi * 16 + 8, 8

        # Top block: M letter
        block_size = 4
        top_z = -4
        # Bottom block: O letter
        bot_z = 4

        corners_top_3d = [
            (-block_size, -block_size, top_z),
            (block_size, -block_size, top_z),
            (block_size, block_size, top_z),
            (-block_size, block_size, top_z),
        ]
        corners_bot_3d = [
            (-block_size, -block_size, bot_z),
            (block_size, -block_size, bot_z),
            (block_size, block_size, bot_z),
            (-block_size, block_size, bot_z),
        ]

        def project(p):
            x3, y3, z3 = p
            xr = x3 * math.cos(angle) + z3 * math.sin(angle)
            zr = -x3 * math.sin(angle) + z3 * math.cos(angle)
            persp = 1.0 + (zr * 0.04)
            return cx + int(xr * persp), cy + int(y3 * persp)

        # Draw top quad (filled gold)
        top_pts = [project(p) for p in corners_top_3d]
        draw.polygon(top_pts, fill=(255, 187, 0, 255), outline=(102, 68, 0, 255))
        # Draw bottom quad (filled darker gold)
        bot_pts = [project(p) for p in corners_bot_3d]
        draw.polygon(bot_pts, fill=(204, 136, 0, 255), outline=(68, 51, 0, 255))
        # Connect with side edges
        for ti, bi in zip(range(4), range(4)):
            draw.line((top_pts[ti], bot_pts[bi]), fill=(119, 85, 0, 255))
        # Add letter hint: M on top, O on bottom
        tcx = sum(p[0] for p in top_pts) // 4
        tcy = sum(p[1] for p in top_pts) // 4
        bcx = sum(p[0] for p in bot_pts) // 4
        bcy = sum(p[1] for p in bot_pts) // 4
        # M strokes (tiny)
        for dx in range(-1, 2):
            draw.point((tcx + dx, tcy - 1), fill=(51, 34, 0, 255))
            draw.point((tcx + dx, tcy + 1), fill=(51, 34, 0, 255))
        draw.point((tcx, tcy), fill=(51, 34, 0, 255))
        # O as a tiny filled circle
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx * dx + dy * dy <= 1:
                    draw.point((bcx + dx, bcy + dy), fill=(51, 34, 0, 255))

    return sheet, palette


def render_pen() -> Image.Image:
    """3 frames of 8x16 quill pen (writing motion)."""
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 black
        (102, 68, 34),     # 2 brown shaft
        (136, 85, 51),     # 3 light brown
        (170, 102, 68),    # 4 tan
        (204, 136, 85),    # 5 light tan
        (85, 34, 0),       # 6 dark brown
        (51, 17, 0),       # 7 deepest brown
        (255, 255, 255),   # 8 ink highlight
        (0, 187, 255),     # 9 ink cyan
        (0, 119, 187),     # 10 ink mid
        (0, 68, 119),      # 11 ink dark
        (17, 17, 17),      # 12 shadow
        (34, 34, 34),      # 13 mid shadow
        (68, 68, 68),      # 14 light shadow
        (255, 255, 255),   # 15 unused
    ]

    sheet = Image.new("RGBA", (8 * 3, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # Three frames with slight rotation
    pen_offsets = [(0, 0), (0, 1), (0, 2)]
    for fi, (ox_off, oy_off) in enumerate(pen_offsets):
        ox = fi * 8
        oy = 0 + oy_off
        # shaft diagonal
        for i in range(12):
            x = ox + 2 + (i // 3)
            y = oy + 1 + i
            if x < ox + 8 and y < 16:
                draw.point((x, y), fill=(102, 68, 34, 255))
                draw.point((x + 1, y), fill=(136, 85, 51, 255))
        # nib (ink tip) at bottom-left
        for dy in range(3):
            for dx in range(2):
                if (dx + dy) < 3:
                    draw.point((ox + 1 - dx, oy + 14 + dy), fill=(0, 68, 119, 255))
        # ink drop
        draw.point((ox, oy + 15), fill=(0, 119, 187, 255))

    return sheet, palette


def render_shield() -> Image.Image:
    """4 frames of 16x16 shield scaling (50, 75, 90, 100 percent).

    SGDK sprite engine validator caps each frame at 16x16 pixels (2x2
    VDP tiles, total of 16 internal tiles per frame). 16x16 is the
    safe maximum for any single-frame animation strip here.
    """
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 black
        (68, 0, 0),        # 2 deep red shadow
        (119, 0, 0),       # 3 dark red
        (170, 0, 0),       # 4 mid red
        (221, 0, 0),       # 5 bright red
        (255, 68, 0),      # 6 orange
        (255, 136, 0),     # 7 dark gold
        (255, 187, 0),     # 8 mid gold
        (255, 221, 68),    # 9 bright gold
        (255, 255, 136),   # 10 near-white gold
        (255, 255, 255),   # 11 highlight
        (51, 17, 0),       # 12 deep brown shadow
        (102, 51, 0),      # 13 brown shadow
        (153, 102, 0),     # 14 tan shadow
        (221, 170, 68),    # 15 dim gold
    ]

    sheet = Image.new("RGBA", (16 * 4, 16), (0, 0, 0, 0))

    scales = [0.50, 0.75, 0.90, 1.00]
    for fi, scale in enumerate(scales):
        ox = fi * 16
        cx = 8
        cy = 8
        sw = max(2, int(6 * scale))
        sh = max(2, int(6 * scale))
        pts = [
            (cx, cy - sh),
            (cx + sw, cy - sh // 2),
            (cx + sw, cy + sh // 3),
            (cx, cy + sh),
            (cx - sw, cy + sh // 3),
            (cx - sw, cy - sh // 2),
        ]
        shield = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(shield)
        shadow_pts = [(x + 1, y + 1) for x, y in pts]
        d.polygon(shadow_pts, fill=(51, 17, 0, 255))
        d.polygon(pts, fill=(170, 0, 0, 255), outline=(68, 0, 0, 255))
        ipts = [
            (cx, cy - sh // 2),
            (cx + sw // 2, cy - sh // 4),
            (cx + sw // 2, cy + sh // 6),
            (cx, cy + sh // 2),
            (cx - sw // 2, cy + sh // 6),
            (cx - sw // 2, cy - sh // 4),
        ]
        d.polygon(ipts, fill=(255, 187, 0, 255), outline=(119, 0, 0, 255))
        d.point((cx, cy), fill=(68, 0, 0, 255))
        sheet.paste(shield, (ox, 0), shield)

    return sheet, palette


def render_glow() -> Image.Image:
    """1 frame of 16x16 radial glow halo.

    SGDK sprite engine caps each frame at 32x32 pixels (4x4 VDP tiles).
    16x16 is plenty for a small radial halo behind a sprite.
    """
    palette = [
        (238, 0, 238),     # 0 transparent
        (0, 0, 0),         # 1 black
        (255, 255, 255),   # 2 white core
        (255, 255, 170),   # 3 hot white
        (255, 221, 85),    # 4 yellow
        (255, 170, 34),    # 5 orange
        (255, 102, 0),     # 6 deep orange
        (204, 68, 0),      # 7 dark orange
        (102, 34, 0),      # 8 ember
        (34, 17, 0),       # 9 deep ember
        (17, 17, 17),      # 10 dark
        (68, 68, 68),      # 11 mid gray
        (102, 102, 102),   # 12 light gray
        (153, 153, 153),   # 13 lighter gray
        (204, 204, 204),   # 14 near white
        (255, 255, 255),   # 15 unused
    ]

    cx, cy = 8, 8
    sheet = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    for y in range(16):
        for x in range(16):
            dx = x - cx
            dy = y - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < 2:
                sheet.putpixel((x, y), (255, 255, 255, 255))
            elif dist < 4:
                sheet.putpixel((x, y), (255, 221, 85, 255))
            elif dist < 6:
                sheet.putpixel((x, y), (255, 136, 0, 200))
            elif dist < 7:
                sheet.putpixel((x, y), (204, 68, 0, 140))

    return sheet, palette


def main() -> int:
    recipes: list[tuple[str, Image.Image, list[tuple[int, int, int]], bool]] = [
        ("font_forge_8x12.png", *render_font_forge(), True),
        ("font_terminal_7x9.png", *render_font_terminal(), True),
        ("font_crest_8x16.png", *render_font_crest(), True),
        ("fx_spark_8x8.png", *render_spark(), True),
        ("fx_monogram_mo_16x16.png", *render_monogram_mo(), True),
        ("fx_pen_8x16.png", *render_pen(), True),
        ("fx_shield_16x16.png", *render_shield(), True),
        ("fx_glow_16x16.png", *render_glow(), True),
    ]

    built: list[BuiltAsset] = []
    errors: list[str] = []
    for filename, image, palette, transparent in recipes:
        path = RES_DIR / filename
        asset = save_indexed_png(image, path, palette, transparent)
        built.append(asset)
        if asset.size[0] % 8 != 0 or asset.size[1] % 8 != 0:
            errors.append(f"{asset.name}: dimensions not multiple of 8")
        if asset.palette_entries > 16:
            errors.append(f"{asset.name}: {asset.palette_entries} palette entries")
        if transparent and not asset.transparent_index_0:
            errors.append(f"{asset.name}: index 0 is not transparent")

    lineage = {
        "asset_set": "branding_v2_identity",
        "profile": "deterministic_3_fonts_5_sprites",
        "outputs": [
            {
                "name": a.name,
                "path": str(a.file.resolve().relative_to(PROJECT.resolve())).replace("\\", "/"),
                "sha256": a.sha256,
                "dimensions": list(a.size),
                "palette_entries": a.palette_entries,
                "used_indexes": a.used_indexes,
                "transparent_index_0": a.transparent_index_0,
            }
            for a in built
        ],
        "validation_errors": errors,
        "aesthetic_decision": (
            "Three identity fonts (forge slab, terminal phosphor, crest gold) and "
            "five procedural FX sprite sheets built deterministically. Inspired by "
            "Treasure (procedural 3D monogram), Square (terminal cursor), EA "
            "(shield with metal/gold), and ADK (spark shower)."
        ),
    }
    report_path = LOG_DIR / "branding_v2_lineage.json"
    report_path.write_text(json.dumps(lineage, indent=2), encoding="utf-8")
    print(json.dumps(lineage, indent=2))
    if errors:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
