#!/usr/bin/env python3
"""Build branding v4 asset set: authored-quality logos and fonts.

Improvements over v3:
- 7x13 glyph bitmaps with serifs (forge/crest) and clean mono (terminal)
- Multi-layer letter rendering: outline -> fill -> highlight -> specular
- Logo compositions with decorative frames, material dithering, depth
- Proper hue shift per slot identity
- Backgrounds, sprites and FX unchanged from v3 (reused directly)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "SGDK_projects" / "SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]"
DEFAULT_OUTPUT = PROJECT / "res" / "branding"
DEFAULT_LOGS = PROJECT / "out" / "logs"
TRANSPARENT = (238, 0, 238)

# ---------- palettes (same domain as v3, refined hue shifts) ----------

PALETTES = {
    "engine": [
        TRANSPARENT, (0, 0, 0), (34, 17, 0), (68, 34, 0),
        (102, 51, 0), (136, 68, 0), (170, 102, 34), (204, 136, 34),
        (238, 170, 68), (238, 238, 204), (34, 51, 68), (0, 68, 102),
        (34, 102, 136), (68, 136, 170), (170, 204, 238), (238, 238, 238),
    ],
    "author": [
        TRANSPARENT, (0, 0, 0), (0, 17, 17), (0, 34, 34),
        (0, 68, 51), (0, 102, 68), (0, 136, 102), (34, 170, 136),
        (68, 204, 170), (102, 238, 204), (68, 51, 0), (102, 68, 0),
        (136, 102, 0), (170, 136, 34), (204, 170, 68), (238, 238, 170),
    ],
    "project": [
        TRANSPARENT, (0, 0, 0), (34, 0, 0), (68, 0, 0),
        (102, 0, 0), (136, 17, 0), (170, 34, 0), (204, 68, 0),
        (238, 102, 0), (238, 170, 34), (102, 68, 0), (136, 102, 0),
        (170, 136, 34), (204, 170, 68), (238, 204, 102), (238, 238, 204),
    ],
    "font_forge": [
        TRANSPARENT, (0, 0, 0), (34, 17, 0), (68, 34, 0),
        (102, 68, 34), (136, 102, 34), (170, 136, 68), (204, 170, 102),
        (238, 204, 136), (238, 238, 204), (34, 34, 34), (68, 68, 68),
        (102, 102, 102), (136, 136, 136), (204, 204, 204), (238, 238, 238),
    ],
    "font_terminal": [
        TRANSPARENT, (0, 0, 0), (0, 17, 0), (0, 34, 17),
        (0, 68, 34), (0, 102, 68), (0, 136, 102), (34, 170, 136),
        (68, 204, 170), (102, 238, 204), (170, 238, 204), (238, 238, 238),
        (0, 34, 34), (0, 51, 51), (0, 68, 68), (34, 102, 102),
    ],
    "font_crest": [
        TRANSPARENT, (0, 0, 0), (34, 0, 0), (68, 17, 0),
        (102, 51, 0), (136, 68, 0), (170, 102, 34), (204, 136, 34),
        (238, 170, 68), (238, 204, 102), (238, 238, 170), (238, 238, 238),
        (34, 34, 34), (68, 68, 68), (102, 102, 102), (170, 170, 170),
    ],
}

# ---------- improved 7x13 glyph bitmaps ----------

GLYPHS_7x13: dict[str, tuple[str, ...]] = {
    "A": ("0011100", "0100010", "1000001", "1000001", "1000001", "1111111",
          "1000001", "1000001", "1000001", "1000001", "0000000", "0000000", "0000000"),
    "B": ("1111100", "1000010", "1000010", "1000010", "1111100", "1000010",
          "1000001", "1000001", "1000010", "1111100", "0000000", "0000000", "0000000"),
    "C": ("0011110", "0100001", "1000000", "1000000", "1000000", "1000000",
          "1000000", "1000000", "0100001", "0011110", "0000000", "0000000", "0000000"),
    "D": ("1111100", "1000010", "1000001", "1000001", "1000001", "1000001",
          "1000001", "1000001", "1000010", "1111100", "0000000", "0000000", "0000000"),
    "E": ("1111111", "1000000", "1000000", "1000000", "1111100", "1000000",
          "1000000", "1000000", "1000000", "1111111", "0000000", "0000000", "0000000"),
    "F": ("1111111", "1000000", "1000000", "1000000", "1111100", "1000000",
          "1000000", "1000000", "1000000", "1000000", "0000000", "0000000", "0000000"),
    "G": ("0011110", "0100001", "1000000", "1000000", "1001111", "1000001",
          "1000001", "1000001", "0100001", "0011110", "0000000", "0000000", "0000000"),
    "H": ("1000001", "1000001", "1000001", "1000001", "1111111", "1000001",
          "1000001", "1000001", "1000001", "1000001", "0000000", "0000000", "0000000"),
    "I": ("0111110", "0001000", "0001000", "0001000", "0001000", "0001000",
          "0001000", "0001000", "0001000", "0111110", "0000000", "0000000", "0000000"),
    "J": ("0011111", "0000100", "0000100", "0000100", "0000100", "0000100",
          "0000100", "1000100", "1000100", "0111000", "0000000", "0000000", "0000000"),
    "K": ("1000010", "1000100", "1001000", "1010000", "1100000", "1010000",
          "1001000", "1000100", "1000010", "1000001", "0000000", "0000000", "0000000"),
    "L": ("1000000", "1000000", "1000000", "1000000", "1000000", "1000000",
          "1000000", "1000000", "1000000", "1111111", "0000000", "0000000", "0000000"),
    "M": ("1000001", "1100011", "1010101", "1001001", "1000001", "1000001",
          "1000001", "1000001", "1000001", "1000001", "0000000", "0000000", "0000000"),
    "N": ("1000001", "1100001", "1010001", "1001001", "1000101", "1000011",
          "1000001", "1000001", "1000001", "1000001", "0000000", "0000000", "0000000"),
    "O": ("0011100", "0100010", "1000001", "1000001", "1000001", "1000001",
          "1000001", "1000001", "0100010", "0011100", "0000000", "0000000", "0000000"),
    "P": ("1111100", "1000010", "1000001", "1000001", "1000010", "1111100",
          "1000000", "1000000", "1000000", "1000000", "0000000", "0000000", "0000000"),
    "Q": ("0011100", "0100010", "1000001", "1000001", "1000001", "1000001",
          "1001001", "1000101", "0100010", "0011101", "0000000", "0000000", "0000000"),
    "R": ("1111100", "1000010", "1000001", "1000001", "1000010", "1111100",
          "1001000", "1000100", "1000010", "1000001", "0000000", "0000000", "0000000"),
    "S": ("0111110", "1000001", "1000000", "0100000", "0011100", "0000010",
          "0000001", "0000001", "1000001", "0111110", "0000000", "0000000", "0000000"),
    "T": ("1111111", "0001000", "0001000", "0001000", "0001000", "0001000",
          "0001000", "0001000", "0001000", "0001000", "0000000", "0000000", "0000000"),
    "U": ("1000001", "1000001", "1000001", "1000001", "1000001", "1000001",
          "1000001", "1000001", "0100010", "0011100", "0000000", "0000000", "0000000"),
    "V": ("1000001", "1000001", "1000001", "0100010", "0100010", "0100010",
          "0010100", "0010100", "0001000", "0001000", "0000000", "0000000", "0000000"),
    "W": ("1000001", "1000001", "1000001", "1000001", "1000001", "1001001",
          "1010101", "1010101", "0100010", "0100010", "0000000", "0000000", "0000000"),
    "X": ("1000001", "0100010", "0010100", "0001000", "0001000", "0001000",
          "0010100", "0100010", "1000001", "1000001", "0000000", "0000000", "0000000"),
    "Y": ("1000001", "0100010", "0010100", "0001000", "0001000", "0001000",
          "0001000", "0001000", "0001000", "0001000", "0000000", "0000000", "0000000"),
    "Z": ("1111111", "0000001", "0000010", "0000100", "0001000", "0010000",
          "0100000", "1000000", "1000000", "1111111", "0000000", "0000000", "0000000"),
    "0": ("0011100", "0100010", "1000001", "1000011", "1000101", "1001001",
          "1010001", "1100001", "0100010", "0011100", "0000000", "0000000", "0000000"),
    "1": ("0001000", "0011000", "0101000", "0001000", "0001000", "0001000",
          "0001000", "0001000", "0001000", "0111110", "0000000", "0000000", "0000000"),
    "2": ("0111110", "1000001", "0000001", "0000010", "0000100", "0001000",
          "0010000", "0100000", "1000000", "1111111", "0000000", "0000000", "0000000"),
    "3": ("0111110", "1000001", "0000001", "0000001", "0011110", "0000001",
          "0000001", "0000001", "1000001", "0111110", "0000000", "0000000", "0000000"),
    "4": ("0000110", "0001010", "0010010", "0100010", "1000010", "1111111",
          "0000010", "0000010", "0000010", "0000010", "0000000", "0000000", "0000000"),
    "5": ("1111111", "1000000", "1000000", "1111110", "0000001", "0000001",
          "0000001", "0000001", "1000001", "0111110", "0000000", "0000000", "0000000"),
    "6": ("0011110", "0100000", "1000000", "1000000", "1111110", "1000001",
          "1000001", "1000001", "0100010", "0011100", "0000000", "0000000", "0000000"),
    "7": ("1111111", "0000001", "0000010", "0000100", "0001000", "0010000",
          "0010000", "0010000", "0010000", "0010000", "0000000", "0000000", "0000000"),
    "8": ("0011100", "0100010", "1000001", "0100010", "0011100", "0100010",
          "1000001", "1000001", "0100010", "0011100", "0000000", "0000000", "0000000"),
    "9": ("0011100", "0100010", "1000001", "1000001", "0111111", "0000001",
          "0000001", "0000001", "0000010", "0111100", "0000000", "0000000", "0000000"),
    " ": ("0000000", "0000000", "0000000", "0000000", "0000000", "0000000",
          "0000000", "0000000", "0000000", "0000000", "0000000", "0000000", "0000000"),
}
GLYPH_ORDER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "


def draw_glyph_multilayer(
    draw: ImageDraw.ImageDraw,
    glyph_rows: tuple[str, ...],
    x0: int, y0: int,
    outline: tuple[int, ...],
    fill: tuple[int, ...],
    highlight: tuple[int, ...],
    specular: tuple[int, ...] | None = None,
) -> None:
    """Render a glyph with outline, fill, top-edge highlight, and optional specular."""
    for gy, row in enumerate(glyph_rows):
        for gx, bit in enumerate(row):
            if bit != "1":
                continue
            px, py = x0 + gx, y0 + gy
            # shadow/outline
            draw.point((px + 1, py + 1), fill=outline)
            # fill
            draw.point((px, py), fill=fill)
            # highlight on top and left edges
            if gy == 0 or (gy > 0 and glyph_rows[gy - 1][gx] == "0"):
                draw.point((px, py), fill=highlight)
            elif gx == 0 or (gx > 0 and row[gx - 1] == "0"):
                draw.point((px, py), fill=highlight)
            # specular on peak pixels
            if specular and gy == 0 and bit == "1":
                draw.point((px, py), fill=specular)


def draw_text_multilayer(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int, y: int,
    outline: tuple[int, ...],
    fill: tuple[int, ...],
    highlight: tuple[int, ...],
    specular: tuple[int, ...] | None = None,
    spacing: int = 8,
) -> int:
    """Draw text using 7x13 glyphs with multi-layer shading. Returns width."""
    cx = x
    for char in text.upper():
        glyph = GLYPHS_7x13.get(char, GLYPHS_7x13[" "])
        draw_glyph_multilayer(draw, glyph, cx, y, outline, fill, highlight, specular)
        cx += spacing
    return cx - x


def center_x(text: str, width: int, spacing: int = 8) -> int:
    return (width - len(text) * spacing) // 2


# ---------- logo builders ----------

def build_engine_logo() -> Image.Image:
    W, H = 240, 80
    pal = PALETTES["engine"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # decorative anvil base
    cx, cy = 120, 52
    d.polygon([(cx-80, cy-8), (cx+80, cy-8), (cx+90, cy), (cx+75, cy+10),
               (cx-75, cy+10), (cx-90, cy)], fill=(*pal[5], 255))
    d.line((cx-78, cy-7, cx+78, cy-7), fill=(*pal[8], 255), width=2)
    d.line((cx-73, cy+9, cx+73, cy+9), fill=(*pal[3], 255), width=2)
    d.polygon([(cx-30, cy+10), (cx+30, cy+10), (cx+22, cy+22), (cx-22, cy+22)],
              fill=(*pal[4], 255))
    d.rectangle((cx-40, cy+22, cx+40, cy+27), fill=(*pal[3], 255))
    d.line((cx-38, cy+22, cx+38, cy+22), fill=(*pal[7], 255), width=1)

    # horizontal heat bar
    d.rectangle((30, 64, 210, 68), fill=(*pal[6], 255))
    for x in range(32, 210, 4):
        d.point((x, 65), fill=(*pal[8], 255))
    d.line((30, 64, 210, 64), fill=(*pal[8], 255), width=1)

    # "MEGA FORGE" main title
    tx = center_x("MEGA FORGE", W, 8)
    draw_text_multilayer(d, "MEGA FORGE", tx, 6,
                         (*pal[3], 255), (*pal[7], 255), (*pal[8], 255), (*pal[9], 255))

    # "ENGINE" subtitle
    tx = center_x("ENGINE", W, 8)
    draw_text_multilayer(d, "ENGINE", tx, 24,
                         (*pal[10], 255), (*pal[12], 255), (*pal[13], 255), (*pal[14], 255))

    # accent line
    d.line((60, 42, 180, 42), fill=(*pal[8], 255), width=1)
    d.point((120, 4), fill=(*pal[15], 255))
    return img


def build_author_signature() -> Image.Image:
    W, H = 240, 64
    pal = PALETTES["author"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # circuit board frame
    d.rectangle((4, 8, 235, 58), outline=(*pal[5], 255), width=1)
    d.rectangle((8, 12, 231, 54), outline=(*pal[7], 255), width=1)
    # corner accents
    for cx, cy in [(8, 12), (231, 12), (8, 54), (231, 54)]:
        d.rectangle((cx-2, cy-2, cx+2, cy+2), fill=(*pal[13], 255))
    # top decorative lines
    d.line((16, 6, 100, 6), fill=(*pal[6], 255), width=1)
    d.line((140, 6, 224, 6), fill=(*pal[6], 255), width=1)
    # diamond center
    d.polygon([(116, 6), (120, 2), (124, 6), (120, 10)], fill=(*pal[13], 255))
    d.point((120, 6), fill=(*pal[15], 255))

    # "MISAEL OLIVEIRA" name
    tx = center_x("MISAEL OLIVEIRA", W, 8)
    draw_text_multilayer(d, "MISAEL OLIVEIRA", tx, 18,
                         (*pal[3], 255), (*pal[8], 255), (*pal[9], 255), (*pal[15], 255))

    # separator
    d.line((30, 38, 210, 38), fill=(*pal[13], 255), width=1)

    # "AUTHOR SEAL" subtitle
    tx = center_x("AUTHOR SEAL", W, 8)
    draw_text_multilayer(d, "AUTHOR SEAL", tx, 43,
                         (*pal[10], 255), (*pal[13], 255), (*pal[14], 255), (*pal[15], 255))
    return img


def build_project_logo() -> Image.Image:
    W, H = 240, 88
    pal = PALETTES["project"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # outer frame with press columns
    d.rectangle((4, 4, 235, 83), fill=(*pal[1], 200), outline=(*pal[5], 255), width=3)
    d.rectangle((10, 10, 229, 77), outline=(*pal[8], 255), width=2)
    # top accent bar
    d.line((14, 14, 225, 14), fill=(*pal[8], 255), width=2)
    d.line((14, 73, 225, 73), fill=(*pal[4], 255), width=1)
    # rivets
    for x in (18, 222):
        for y in (20, 40, 60):
            d.rectangle((x-2, y-2, x+2, y+2), fill=(*pal[12], 255))
            d.point((x, y), fill=(*pal[14], 255))

    # "MEGA MASTER" main
    tx = center_x("MEGA MASTER", W, 8)
    draw_text_multilayer(d, "MEGA MASTER", tx, 22,
                         (*pal[3], 255), (*pal[9], 255), (*pal[13], 255), (*pal[14], 255))

    # "GAMES" main
    tx = center_x("GAMES", W, 8)
    draw_text_multilayer(d, "GAMES", tx, 42,
                         (*pal[3], 255), (*pal[7], 255), (*pal[8], 255), (*pal[9], 255))

    # bottom separator
    d.line((30, 60, 210, 60), fill=(*pal[13], 255), width=1)
    return img


def build_presents() -> Image.Image:
    W, H = 128, 24
    pal = PALETTES["project"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tx = center_x("PRESENTS", W, 8)
    draw_text_multilayer(d, "PRESENTS", tx, 4,
                         (*pal[3], 255), (*pal[7], 255), (*pal[8], 255), (*pal[9], 255))
    d.line((8, 20, 120, 20), fill=(*pal[13], 255), width=1)
    d.rectangle((2, 18, 6, 22), fill=(*pal[5], 255))
    d.rectangle((122, 18, 126, 22), fill=(*pal[5], 255))
    return img


# ---------- font builders ----------

def build_font(kind: str) -> Image.Image:
    """Build a 296x16 font sheet (37 glyphs, 8x16 each)."""
    img = Image.new("RGBA", (296, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pal_name = f"font_{kind}"
    pal = PALETTES[pal_name]

    for index, char in enumerate(GLYPH_ORDER):
        x0 = index * 8
        glyph = GLYPHS_7x13.get(char, GLYPHS_7x13[" "])
        for gy, row in enumerate(glyph[:10]):
            for gx, bit in enumerate(row):
                if bit != "1":
                    continue
                px, py = x0 + gx, 2 + gy
                if kind == "forge":
                    d.point((px + 1, py + 1), fill=(*pal[4], 255))
                    d.point((px, py), fill=(*pal[7], 255))
                    if gy == 0 or (gy > 0 and glyph[gy - 1][gx] == "0"):
                        d.point((px, py), fill=(*pal[8], 255))
                elif kind == "terminal":
                    d.point((px, py + 1), fill=(*pal[4], 255))
                    d.point((px, py), fill=(*pal[8], 255))
                    if gy == 0:
                        d.point((px, py), fill=(*pal[9], 255))
                else:  # crest
                    d.point((px + 1, py + 1), fill=(*pal[3], 255))
                    d.point((px, py), fill=(*pal[8], 255))
                    if gy == 0 or gx == 0:
                        d.point((px, py), fill=(*pal[9], 255))

        # underline accent per font identity
        if char != " ":
            if kind == "forge":
                d.line((x0, 13, x0 + 6, 13), fill=(*pal[5], 255))
            elif kind == "crest":
                d.line((x0, 1, x0 + 6, 1), fill=(*pal[6], 255))
    return img


# ---------- indexing and save ----------

def nearest_index(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]], start: int) -> int:
    return min(
        range(start, len(palette)),
        key=lambda i: sum((rgb[c] - palette[i][c]) ** 2 for c in range(3)),
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
    flat = [ch for color in palette for ch in color]
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


def build_assets(output_dir: Path = DEFAULT_OUTPUT, log_dir: Path = DEFAULT_LOGS) -> dict:
    recipes = [
        ("brand_engine_logo_v4.png", build_engine_logo(), "engine", True),
        ("brand_author_signature_v4.png", build_author_signature(), "author", True),
        ("brand_project_logo_v4.png", build_project_logo(), "project", True),
        ("brand_presents_v4.png", build_presents(), "project", True),
        ("font_forge_v4.png", build_font("forge"), "font_forge", True),
        ("font_terminal_v4.png", build_font("terminal"), "font_terminal", True),
        ("font_crest_v4.png", build_font("crest"), "font_crest", True),
    ]
    outputs = []
    for name, image, palette, transparent in recipes:
        output = save_indexed(image, output_dir / name, palette, transparent)
        outputs.append(output)
        w, h = output["dimensions"]
        print(f"  {name}: {w}x{h}, {output['used_indexes']} colors, sha256={output['sha256'][:16]}...")

    lineage = {
        "builder": "build_branding_v4_assets.py",
        "version": "4.0.0",
        "assets": outputs,
    }
    lineage_path = log_dir / "branding_v4_lineage.json"
    lineage_path.parent.mkdir(parents=True, exist_ok=True)
    lineage_path.write_text(json.dumps(lineage, indent=2), encoding="utf-8")
    print(f"\nLineage: {lineage_path}")
    return lineage


if __name__ == "__main__":
    print("Building branding v4 assets...")
    build_assets()
    print("Done.")
