#!/usr/bin/env python3
"""Build the approved epic branding v3 asset set for SMOKE_TEST.

The builder is deterministic and intentionally pixel-native. It generates
compact scene-local backgrounds, display logos, fonts, and sprite sheets that
turn the three branding slots into distinct Mega Drive setpieces.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "SGDK_projects" / "SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]"
DEFAULT_OUTPUT = PROJECT / "res" / "branding"
DEFAULT_LOGS = PROJECT / "out" / "logs"
TRANSPARENT = (238, 0, 238)


GLYPHS: dict[str, tuple[str, ...]] = {
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
GLYPH_ORDER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "


PALETTES = {
    "engine_bg": [
        (0, 0, 0), (34, 0, 0), (68, 0, 0), (102, 34, 0),
        (136, 34, 0), (170, 68, 0), (204, 102, 0), (238, 170, 34),
        (34, 34, 34), (68, 68, 68), (102, 102, 102), (136, 136, 136),
        (0, 34, 68), (0, 68, 102), (34, 102, 136), (238, 238, 238),
    ],
    "author_bg": [
        (0, 0, 0), (0, 34, 34), (0, 68, 68), (0, 102, 102),
        (0, 136, 102), (0, 170, 136), (34, 204, 170), (102, 238, 204),
        (34, 34, 34), (68, 68, 68), (102, 68, 0), (136, 102, 0),
        (170, 136, 0), (204, 170, 34), (238, 204, 68), (238, 238, 204),
    ],
    "project_bg": [
        (0, 0, 0), (34, 34, 34), (68, 68, 68), (102, 102, 102),
        (136, 136, 136), (170, 170, 170), (204, 204, 204), (238, 238, 238),
        (34, 0, 0), (68, 0, 0), (102, 0, 0), (136, 0, 0),
        (170, 34, 0), (204, 68, 0), (238, 102, 0), (238, 204, 68),
    ],
    "engine": [
        TRANSPARENT, (0, 0, 0), (34, 34, 34), (68, 68, 68),
        (102, 102, 102), (136, 136, 136), (170, 170, 170), (204, 204, 204),
        (238, 238, 238), (68, 0, 0), (136, 0, 0), (204, 68, 0),
        (238, 136, 0), (0, 68, 102), (34, 170, 204), (170, 238, 238),
    ],
    "author": [
        TRANSPARENT, (0, 0, 0), (0, 34, 34), (0, 68, 68),
        (0, 102, 68), (0, 170, 102), (34, 238, 170), (170, 238, 204),
        (68, 34, 0), (102, 68, 0), (136, 102, 0), (170, 136, 0),
        (204, 170, 34), (238, 204, 68), (238, 238, 170), (238, 238, 238),
    ],
    "project": [
        TRANSPARENT, (0, 0, 0), (34, 0, 0), (68, 0, 0),
        (102, 0, 0), (136, 0, 0), (170, 34, 0), (204, 68, 0),
        (238, 102, 0), (102, 68, 0), (136, 102, 0), (170, 136, 0),
        (204, 170, 34), (238, 204, 68), (238, 238, 170), (238, 238, 238),
    ],
}


def pixel_text_width(text: str, scale: int) -> int:
    return max(0, len(text) * 6 * scale - scale)


def draw_pixel_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    scale: int,
    fill: tuple[int, int, int, int],
    shadow: tuple[int, int, int, int] | None = None,
    highlight: tuple[int, int, int, int] | None = None,
) -> None:
    x, y = xy
    for char in text.upper():
        glyph = GLYPHS.get(char, GLYPHS[" "])
        if shadow:
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        draw.rectangle(
                            (x + gx * scale + scale, y + gy * scale + scale,
                             x + (gx + 1) * scale - 1 + scale,
                             y + (gy + 1) * scale - 1 + scale),
                            fill=shadow,
                        )
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    color = highlight if highlight and (gy == 0 or gx == 0) else fill
                    draw.rectangle(
                        (x + gx * scale, y + gy * scale,
                         x + (gx + 1) * scale - 1, y + (gy + 1) * scale - 1),
                        fill=color,
                    )
        x += 6 * scale


def draw_centered_text(draw, text, y, width, scale, fill, shadow=None, highlight=None):
    draw_pixel_text(
        draw, text, ((width - pixel_text_width(text, scale)) // 2, y),
        scale, fill, shadow, highlight
    )


def draw_dither_rect(draw, rect, dark, light, step=2):
    x0, y0, x1, y1 = rect
    draw.rectangle(rect, fill=dark)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if ((x + y) % step) == 0:
                draw.point((x, y), fill=light)


def build_engine_bg() -> Image.Image:
    img = Image.new("RGBA", (128, 64), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 127, 63), fill=(0, 0, 0, 255))
    for x in range(0, 128, 32):
        d.rectangle((x + 2, 0, x + 7, 63), fill=(34, 34, 34, 255))
        d.line((x + 7, 0, x + 7, 63), fill=(102, 102, 102, 255), width=1)
        for y in (8, 32, 56):
            d.rectangle((x + 3, y, x + 5, y + 2), fill=(170, 68, 0, 255))
    for y in range(8, 64, 16):
        d.rectangle((10, y, 118, y + 5), fill=(34, 0, 0, 255))
        for x in range(12 + ((y // 16) & 1) * 8, 118, 16):
            d.rectangle((x, y + 1, x + 8, y + 3), fill=(102, 34, 0, 255))
            d.point((x + 3, y + 1), fill=(238, 170, 34, 255))
    for x in range(18, 128, 32):
        d.line((x, 0, x + 12, 63), fill=(0, 68, 102, 255), width=1)
    return img


def build_author_bg() -> Image.Image:
    img = Image.new("RGBA", (128, 64), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, 64, 8):
        d.line((0, y, 127, y), fill=(0, 34, 34, 255), width=1)
    for x in range(0, 128, 16):
        d.line((x, 0, x, 63), fill=(0, 68, 68, 255), width=1)
    for x, y in ((8, 8), (40, 24), (72, 8), (104, 40), (24, 56), (88, 56)):
        d.rectangle((x - 2, y - 2, x + 2, y + 2), fill=(0, 102, 102, 255))
        d.point((x, y), fill=(102, 238, 204, 255))
        d.line((x + 3, y, x + 11, y), fill=(0, 136, 102, 255))
    for y in range(3, 64, 4):
        d.line((0, y, 127, y), fill=(0, 34, 34, 255), width=1)
    return img


def build_project_bg() -> Image.Image:
    img = Image.new("RGBA", (128, 64), (0, 0, 0, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 127, 63), fill=(0, 0, 0, 255))
    for x in range(0, 128, 32):
        d.rectangle((x + 1, 0, x + 7, 63), fill=(68, 68, 68, 255))
        d.line((x + 2, 0, x + 2, 63), fill=(170, 170, 170, 255), width=2)
        d.line((x + 7, 0, x + 7, 63), fill=(34, 0, 0, 255), width=1)
        for y in (7, 31, 55):
            d.rectangle((x + 3, y, x + 6, y + 3), fill=(204, 204, 204, 255))

        d.rectangle((x + 10, 3, x + 29, 12), fill=(68, 0, 0, 255))
        d.line((x + 11, 4, x + 28, 4), fill=(238, 102, 0, 255), width=2)
        d.polygon(
            [(x + 12, 12), (x + 27, 12), (x + 23, 18), (x + 16, 18)],
            fill=(136, 0, 0, 255),
        )
        d.rectangle((x + 17, 18, x + 22, 47), fill=(68, 68, 68, 255))
        d.line((x + 18, 18, x + 18, 47), fill=(170, 170, 170, 255), width=1)
        d.rectangle((x + 11, 48, x + 28, 58), fill=(34, 0, 0, 255))
        d.line((x + 12, 48, x + 27, 48), fill=(238, 102, 0, 255), width=2)
        d.line((x + 14, 60, x + 25, 60), fill=(136, 0, 0, 255), width=2)
    return img


def draw_anvil(d: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    d.polygon(
        [(cx - 72, cy - 15), (cx + 55, cy - 15), (cx + 77, cy - 5),
         (cx + 52, cy + 8), (cx - 60, cy + 8), (cx - 78, cy - 1)],
        fill=(102, 102, 102, 255),
    )
    d.line((cx - 69, cy - 13, cx + 54, cy - 13), fill=(238, 238, 238, 255), width=3)
    d.line((cx - 61, cy + 7, cx + 50, cy + 7), fill=(34, 34, 34, 255), width=3)
    d.polygon([(cx - 26, cy + 8), (cx + 26, cy + 8), (cx + 18, cy + 27), (cx - 18, cy + 27)],
              fill=(68, 68, 68, 255))
    d.rectangle((cx - 38, cy + 27, cx + 38, cy + 33), fill=(34, 34, 34, 255))


def build_engine_logo() -> Image.Image:
    img = Image.new("RGBA", (240, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_anvil(d, 120, 43)
    draw_centered_text(d, "MEGA FORGE", 7, 240, 3, (204, 204, 204, 255),
                       (68, 0, 0, 255), (238, 238, 238, 255))
    draw_centered_text(d, "ENGINE", 34, 240, 2, (34, 170, 204, 255),
                       (0, 34, 68, 255), (170, 238, 238, 255))
    d.line((58, 59, 182, 59), fill=(238, 136, 0, 255), width=2)
    d.point((120, 2), fill=(238, 238, 238, 255))
    return img


def build_author_signature() -> Image.Image:
    img = Image.new("RGBA", (240, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((5, 9, 234, 58), outline=(0, 102, 68, 255), width=1)
    d.rectangle((10, 14, 229, 53), outline=(0, 170, 102, 255), width=1)
    d.line((18, 7, 94, 7), fill=(0, 170, 102, 255), width=2)
    d.line((146, 7, 222, 7), fill=(0, 170, 102, 255), width=2)
    d.polygon([(112, 7), (120, 2), (128, 7), (120, 12)], fill=(204, 170, 34, 255))
    d.point((120, 7), fill=(238, 238, 170, 255))
    for x in (10, 229):
        d.line((x, 14, x + (-5 if x > 120 else 5), 9), fill=(204, 170, 34, 255), width=2)
        d.line((x, 53, x + (-5 if x > 120 else 5), 58), fill=(204, 170, 34, 255), width=2)
    draw_centered_text(d, "MISAEL OLIVEIRA", 19, 240, 2, (34, 238, 170, 255),
                       (0, 34, 34, 255), (170, 238, 204, 255))
    d.line((31, 42, 209, 42), fill=(204, 170, 34, 255), width=2)
    draw_centered_text(d, "AUTHOR SEAL", 47, 240, 1, (238, 204, 68, 255),
                       (68, 34, 0, 255), (238, 238, 170, 255))
    return img


def build_project_logo() -> Image.Image:
    img = Image.new("RGBA", (240, 88), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((5, 6, 234, 81), fill=(0, 0, 0, 220), outline=(68, 68, 68, 255), width=3)
    d.rectangle((12, 13, 227, 74), outline=(136, 0, 0, 255), width=3)
    d.line((18, 19, 222, 19), fill=(238, 102, 0, 255), width=2)
    d.line((18, 68, 222, 68), fill=(102, 0, 0, 255), width=2)
    draw_centered_text(d, "MEGA MASTER", 25, 240, 3, (238, 204, 68, 255),
                       (68, 0, 0, 255), (238, 238, 170, 255))
    draw_centered_text(d, "GAMES", 51, 240, 3, (204, 68, 0, 255),
                       (34, 0, 0, 255), (238, 102, 0, 255))
    for x in (18, 222):
        d.rectangle((x - 3, 39, x + 3, 45), fill=(170, 136, 0, 255))
        d.point((x, 42), fill=(238, 238, 170, 255))
    return img


def build_presents() -> Image.Image:
    img = Image.new("RGBA", (128, 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    draw_centered_text(d, "PRESENTS", 3, 128, 2, (204, 68, 0, 255),
                       (34, 0, 0, 255), (238, 102, 0, 255))
    d.line((7, 20, 121, 20), fill=(238, 204, 68, 255), width=2)
    d.rectangle((2, 18, 6, 22), fill=(136, 0, 0, 255))
    d.rectangle((122, 18, 126, 22), fill=(136, 0, 0, 255))
    return img


def build_font(kind: str) -> Image.Image:
    img = Image.new("RGBA", (296, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for index, char in enumerate(GLYPH_ORDER):
        x0 = index * 8 + 1
        glyph = GLYPHS[char]
        for y, row in enumerate(glyph):
            for x, bit in enumerate(row):
                if bit != "1":
                    continue
                px = x0 + x
                py = 4 + y
                if kind == "forge":
                    d.point((px + 1, py + 1), fill=(68, 68, 68, 255))
                    d.point((px, py), fill=(204, 204, 204, 255))
                    if y == 0 or x == 0:
                        d.point((px, py), fill=(238, 238, 238, 255))
                elif kind == "terminal":
                    d.point((px + 1, py), fill=(0, 102, 68, 255))
                    d.point((px, py + 1), fill=(0, 68, 68, 255))
                    d.point((px, py), fill=(34, 238, 170, 255))
                else:
                    d.point((px + 1, py + 1), fill=(68, 0, 0, 255))
                    d.point((px, py), fill=(204, 170, 34, 255))
                    if y == 0 or x == 0:
                        d.point((px, py), fill=(238, 238, 170, 255))
        if kind == "forge" and char != " ":
            d.line((x0, 12, x0 + 5, 12), fill=(102, 102, 102, 255))
        elif kind == "crest" and char != " ":
            d.line((x0, 3, x0 + 5, 3), fill=(204, 68, 0, 255))
    return img


def build_spark() -> Image.Image:
    img = Image.new("RGBA", (32, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    patterns = [
        [(3, 3, 15), (4, 3, 14), (3, 4, 14), (4, 4, 13)],
        [(3, 0, 14), (3, 2, 15), (0, 3, 13), (2, 3, 15), (3, 3, 15),
         (5, 3, 14), (7, 3, 13), (3, 5, 14), (3, 7, 13)],
        [(0, 0, 13), (2, 2, 14), (3, 3, 15), (5, 1, 13), (6, 4, 14),
         (4, 6, 13), (1, 6, 12)],
        [(0, 1, 12), (3, 0, 13), (7, 2, 12), (1, 5, 11), (5, 6, 12), (7, 7, 11)],
    ]
    pal = PALETTES["engine"]
    for frame, points in enumerate(patterns):
        for x, y, color in points:
            d.point((frame * 8 + x, y), fill=(*pal[color], 255))
    return img


def build_monogram() -> Image.Image:
    img = Image.new("RGBA", (384, 32), (0, 0, 0, 0))
    for frame in range(12):
        cell = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(cell)
        cosine = math.cos(frame * math.pi / 6.0)
        width = max(5, int(abs(cosine) * 28))
        x0 = 16 - width // 2
        x1 = 16 + width // 2
        edge = 3 if cosine >= 0 else -3
        outer = [
            (x0, 8), (x0 + 4, 3), (x1 - 4, 3), (x1, 8),
            (x1, 23), (x1 - 4, 29), (x0 + 4, 29), (x0, 23),
        ]
        inner = [
            (x0 + 2, 9), (x0 + 5, 6), (x1 - 5, 6), (x1 - 2, 9),
            (x1 - 2, 22), (x1 - 5, 26), (x0 + 5, 26), (x0 + 2, 22),
        ]
        d.polygon([(x + 2, min(31, y + 2)) for x, y in outer], fill=(68, 34, 0, 255))
        d.polygon(outer, fill=(204, 170, 34, 255), outline=(238, 238, 170, 255))
        d.polygon(inner, fill=(0, 0, 0, 255), outline=(102, 68, 0, 255))
        d.line((x0 + 4, 5, x1 - 4, 5), fill=(238, 238, 170, 255), width=1)
        d.line((x0 + 4, 27, x1 - 4, 27), fill=(102, 68, 0, 255), width=1)
        if width >= 18:
            draw_centered_text(d, "MO", 10, 32, 2, (204, 170, 34, 255),
                               (68, 34, 0, 255), (238, 238, 170, 255))
        else:
            d.line((16, 7, 16, 25), fill=(238, 238, 170, 255), width=2)
            d.point((15, 16), fill=(34, 238, 170, 255))
        d.line((x1, 9, x1 + edge, 12), fill=(170, 136, 0, 255), width=2)
        d.line((x1, 23, x1 + edge, 20), fill=(102, 68, 0, 255), width=2)
        d.point((x0 + 2, 16), fill=(34, 238, 170, 255))
        img.alpha_composite(cell, (frame * 32, 0))
    return img


def build_cursor() -> Image.Image:
    img = Image.new("RGBA", (24, 16), (0, 0, 0, 0))
    for frame in range(3):
        d = ImageDraw.Draw(img)
        ox = frame * 8
        d.line((ox + 6, 1 + frame, ox + 2, 12 + frame), fill=(204, 170, 34, 255), width=2)
        d.polygon([(ox + 6, 1 + frame), (ox + 2, 3 + frame), (ox + 4, 7 + frame)],
                  fill=(238, 238, 170, 255))
        d.point((ox + 1, 14), fill=(34, 238, 170, 255))
        d.point((ox + 2, 14), fill=(0, 102, 68, 255))
    return img


def build_shield() -> Image.Image:
    img = Image.new("RGBA", (256, 32), (0, 0, 0, 0))
    sizes = [(22, 14), (38, 22), (52, 28), (60, 30)]
    for frame, (width, height) in enumerate(sizes):
        cell = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(cell)
        cx, cy = 32, 16
        hw, hh = width // 2, height // 2
        pts = [(cx, cy - hh), (cx + hw, cy - hh // 2), (cx + hw - 3, cy + hh // 2),
               (cx, cy + hh), (cx - hw + 3, cy + hh // 2), (cx - hw, cy - hh // 2)]
        shadow = [(x + 2, min(31, y + 2)) for x, y in pts]
        d.polygon(shadow, fill=(34, 0, 0, 255))
        d.polygon(pts, fill=(102, 0, 0, 255), outline=(238, 102, 0, 255))
        inner = [(cx, cy - hh + 4), (cx + hw - 7, cy - hh // 2 + 3),
                 (cx + hw - 9, cy + hh // 2 - 2), (cx, cy + hh - 4),
                 (cx - hw + 9, cy + hh // 2 - 2), (cx - hw + 7, cy - hh // 2 + 3)]
        d.polygon(inner, fill=(0, 0, 0, 255), outline=(204, 170, 34, 255))
        if width >= 38:
            scale = 2 if width < 52 else 3
            draw_centered_text(d, "MMG", cy - (7 * scale) // 2, 64, scale,
                               (204, 170, 34, 255), (68, 0, 0, 255), (238, 238, 170, 255))
        else:
            d.rectangle((cx - 2, cy - 2, cx + 2, cy + 2), fill=(238, 204, 68, 255))
        img.alpha_composite(cell, (frame * 64, 0))
    return img


def build_glow() -> Image.Image:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    colors = PALETTES["author"]
    for y in range(32):
        for x in range(32):
            dx, dy = x - 16, y - 16
            d2 = dx * dx + dy * dy
            if 78 <= d2 < 142 and ((x + y) & 1) == 0:
                color = colors[14]
            elif 142 <= d2 < 210 and ((x * 3 + y) & 3) == 0:
                color = colors[12]
            elif 210 <= d2 < 270 and ((x + y * 3) & 7) == 0:
                color = colors[10]
            else:
                continue
            img.putpixel((x, y), (*color, 255))
    for point in ((16, 4), (16, 5), (16, 27), (16, 28), (4, 16), (5, 16), (27, 16), (28, 16)):
        img.putpixel(point, (*colors[15], 255))
    return img


def build_debris() -> Image.Image:
    img = Image.new("RGBA", (32, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    patterns = [
        [(3, 3), (4, 3), (3, 4), (4, 4)],
        [(1, 3), (3, 1), (5, 3), (3, 5)],
        [(0, 1), (2, 5), (5, 0), (7, 6)],
        [(0, 7), (7, 0)],
    ]
    for frame, pts in enumerate(patterns):
        for i, (x, y) in enumerate(pts):
            color = (204, 204, 204, 255) if i & 1 else (238, 102, 0, 255)
            d.rectangle((frame * 8 + x, y, frame * 8 + min(7, x + 1), min(7, y + 1)), fill=color)
    return img


def nearest_index(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]], start: int) -> int:
    return min(
        range(start, len(palette)),
        key=lambda i: sum((rgb[channel] - palette[i][channel]) ** 2 for channel in range(3)),
    )


def save_indexed(image: Image.Image, path: Path, palette_name: str, transparent: bool) -> dict:
    palette = PALETTES[palette_name]
    indexed = Image.new("P", image.size)
    pixels = []
    for r, g, b, a in image.convert("RGBA").getdata():
        if transparent and a < 16:
            pixels.append(0)
        else:
            pixels.append(nearest_index((r, g, b), palette, 1 if transparent else 0))
    indexed.putdata(pixels)
    flat = [channel for color in palette for channel in color]
    indexed.putpalette(flat)
    if transparent:
        indexed.info["transparency"] = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    indexed.save(path, format="PNG", optimize=False, bits=4)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "name": path.name,
        "path": str(path),
        "dimensions": list(image.size),
        "palette_entries": len(palette),
        "used_indexes": len(set(indexed.getdata())),
        "transparent_index_0": transparent,
        "sha256": sha,
    }


def build_preview(output_dir: Path, log_dir: Path) -> Path:
    preview = Image.new("RGBA", (320, 672), (0, 0, 0, 255))
    slots = [
        ("brand_engine_bg_v3.png", "brand_engine_logo_v3.png", 72),
        ("brand_author_bg_v3.png", "brand_author_signature_v3.png", 132),
        ("brand_project_bg_v3.png", "brand_project_logo_v3.png", 76),
    ]
    for slot, (bg_name, logo_name, y) in enumerate(slots):
        bg = Image.open(output_dir / bg_name).convert("RGBA")
        logo = Image.open(output_dir / logo_name).convert("RGBA")
        screen = Image.new("RGBA", (320, 224), (0, 0, 0, 255))
        for by in range(0, 224, bg.height):
            for bx in range(0, 320, bg.width):
                screen.alpha_composite(bg, (bx, by))
        screen.alpha_composite(logo, ((320 - logo.width) // 2, y))
        if slot == 1:
            glow = Image.open(output_dir / "fx_glow_v3.png").convert("RGBA")
            mono = Image.open(output_dir / "fx_monogram_mo_v3.png").convert("RGBA").crop((0, 0, 32, 32))
            screen.alpha_composite(glow, (144, 56))
            screen.alpha_composite(mono, (144, 56))
        if slot == 2:
            shield = Image.open(output_dir / "fx_shield_v3.png").convert("RGBA").crop((192, 0, 256, 32))
            screen.alpha_composite(shield, (128, 34))
        preview.alpha_composite(screen, (0, slot * 224))
    path = log_dir / "branding_v3_preview.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    preview.save(path)
    return path


def build_assets(output_dir: Path = DEFAULT_OUTPUT, log_dir: Path = DEFAULT_LOGS) -> dict:
    recipes = [
        ("brand_engine_bg_v3.png", build_engine_bg(), "engine_bg", False),
        ("brand_author_bg_v3.png", build_author_bg(), "author_bg", False),
        ("brand_project_bg_v3.png", build_project_bg(), "project_bg", False),
        ("brand_engine_logo_v3.png", build_engine_logo(), "engine", True),
        ("brand_author_signature_v3.png", build_author_signature(), "author", True),
        ("brand_project_logo_v3.png", build_project_logo(), "project", True),
        ("brand_presents_v3.png", build_presents(), "project", True),
        ("font_forge_v3.png", build_font("forge"), "engine", True),
        ("font_terminal_v3.png", build_font("terminal"), "author", True),
        ("font_crest_v3.png", build_font("crest"), "project", True),
        ("fx_spark_v3.png", build_spark(), "engine", True),
        ("fx_monogram_mo_v3.png", build_monogram(), "author", True),
        ("fx_cursor_v3.png", build_cursor(), "author", True),
        ("fx_shield_v3.png", build_shield(), "project", True),
        ("fx_glow_v3.png", build_glow(), "author", True),
        ("fx_debris_v3.png", build_debris(), "project", True),
    ]
    outputs = []
    errors = []
    for name, image, palette, transparent in recipes:
        output = save_indexed(image, output_dir / name, palette, transparent)
        outputs.append(output)
        width, height = output["dimensions"]
        if width % 8 or height % 8:
            errors.append(f"{name}: dimensions are not 8px aligned")
        if output["palette_entries"] > 16:
            errors.append(f"{name}: PLTE exceeds 16 entries")
        if output["used_indexes"] > 16:
            errors.append(f"{name}: uses more than 16 indexes")
    preview = build_preview(output_dir, log_dir)
    report = {
        "asset_set": "branding_v3_epic_setpieces",
        "profile": "pixel_native_three_slot_cinematic",
        "references": {
            "engine": ["Thunder Force IV", "Streets of Rage 3", "Sonic 3 & Knuckles"],
            "author": ["Rare 16-bit publisher marks", "Treasure logo motion", "Phantasy Star IV terminals"],
            "project": ["EA industrial intros", "ADK impact FX", "Sunsoft audio-weighted presentation"],
        },
        "outputs": outputs,
        "preview": str(preview),
        "validation_errors": errors,
    }
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / "branding_v3_lineage.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    report = build_assets()
    print(json.dumps(report, indent=2))
    return 2 if report["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
