#!/usr/bin/env python3
"""Native 320x224 dock for LIVE_BAR_FR2 PAL2.

Reauthored from the Imagine sunset-pier source on an 8x8 tile vocabulary.
Not a downscale of the painting. compare_flat / lab_flattened_reference:
single BG_B IMAGE, no parallax.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

W, H = 320, 224
TW, TH = 40, 28
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "dock"
RES = ROOT / "res" / "bgs"
DOC = ROOT / "doc"

# PAL2 — 9-bit. Index 0 is plane-transparent on the VDP (shows backdrop).
# Never paint 0. 15 visible colors.
PAL = [
    (0x00, 0x00, 0x00),  # 0 unused / plane transparent
    (0xEE, 0x88, 0x44),  # 1 orange hi
    (0xCC, 0x66, 0x22),  # 2 orange
    (0xAA, 0x44, 0x66),  # 3 sky magenta
    (0x44, 0xAA, 0xCC),  # 4 cyan hi
    (0x22, 0x88, 0xCC),  # 5 cyan
    (0x22, 0x66, 0x88),  # 6 water deep
    (0xCC, 0x88, 0x44),  # 7 wood hi
    (0xAA, 0x66, 0x22),  # 8 wood
    (0x66, 0x44, 0x22),  # 9 wood sh
    (0x44, 0x22, 0x00),  # 10 wood dk
    (0x66, 0x88, 0xAA),  # 11 fog
    (0x44, 0x66, 0x88),  # 12 shed
    (0x88, 0x66, 0x44),  # 13 crate
    (0xCC, 0xAA, 0x66),  # 14 rope
    (0xEE, 0xCC, 0x66),  # 15 lamp
]
UNUSED = 0
OR_HI, ORNG, MAG, CY_HI, CYAN, WDEEP = range(1, 7)
WOOD_HI, WOOD, WOOD_SH, WOOD_DK, FOG, SHED, CRATE, ROPE, LAMP = range(7, 16)


def fill8(c):
    return [[c] * 8 for _ in range(8)]


def dither8(a, b):
    t = fill8(a)
    for y in range(8):
        for x in range(8):
            if (x + y) & 1:
                t[y][x] = b
    return t


def bayer8(a, b):
    m = ((0, 2), (3, 1))
    t = fill8(a)
    for y in range(8):
        for x in range(8):
            t[y][x] = a if m[y & 1][x & 1] < 2 else b
    return t


def plank8(hi, base, gap, shift=0):
    t = []
    for y in range(8):
        row = []
        for x in range(8):
            xx = (x + shift) & 7
            if y == 0:
                row.append(gap)
            elif y in (1, 2):
                row.append(hi if xx not in (2, 6) else base)
            elif y == 7:
                row.append(gap)
            else:
                row.append(base if xx != 4 else hi)
        t.append(row)
    return t


def water8(base, hi, deep, phase=0):
    t = fill8(base)
    for x in range(8):
        t[2][(x + phase) & 7] = hi
        t[5][(x + 3 + phase) & 7] = deep
    return t


def wall8(base, sh):
    t = fill8(base)
    for y in range(8):
        t[y][0] = sh
        t[y][7] = sh
        if y == 7:
            t[y] = [sh] * 8
    return t  # sh must not be index 0


def roof8(dk, sh):
    t = fill8(dk)
    for x in range(8):
        t[0][x] = sh
        t[1][x] = sh if x % 2 == 0 else dk
    return t


def window8():
    t = fill8(SHED)
    for y in range(2, 6):
        for x in range(2, 6):
            t[y][x] = LAMP if (x, y) != (5, 5) else WOOD_DK
    return t


TILES = {
    "sky_or": fill8(ORNG),
    "sky_or_hi": fill8(OR_HI),
    "sky_or_d": bayer8(OR_HI, ORNG),
    "sky_mid": bayer8(ORNG, MAG),
    "sky_mag": fill8(MAG),
    "sky_cy": fill8(CYAN),
    "sky_cy_hi": fill8(CY_HI),
    "sky_cy_d": bayer8(CY_HI, CYAN),
    "sky_fog": fill8(FOG),
    "sky_fog_d": dither8(MAG, FOG),
    "horizon": fill8(FOG),
    "water": water8(CYAN, CY_HI, WDEEP, 0),
    "water2": water8(CYAN, CY_HI, WDEEP, 4),
    "water_or": water8(MAG, ORNG, WDEEP, 2),
    "water_dk": fill8(WDEEP),
    "plank": plank8(WOOD_HI, WOOD, WOOD_DK, 0),
    "plank2": plank8(WOOD_HI, WOOD, WOOD_DK, 3),
    "plank_sh": plank8(WOOD, WOOD_SH, WOOD_DK, 1),
    "edge": fill8(WOOD_DK),
    "wall": wall8(SHED, WOOD_DK),
    "roof": roof8(WOOD_DK, WOOD_SH),
    "win": window8(),
    "fog_wall": wall8(FOG, WOOD_DK),
}


def new_canvas(c=FOG):
    return [[c] * W for _ in range(H)]


def blit_tile(cv, tx, ty, name):
    if not (0 <= tx < TW and 0 <= ty < TH):
        return
    t = TILES[name]
    ox, oy = tx * 8, ty * 8
    for y in range(8):
        for x in range(8):
            cv[oy + y][ox + x] = t[y][x]


def fill_tiles(cv, x0, y0, x1, y1, name):
    for ty in range(y0, y1):
        for tx in range(x0, x1):
            blit_tile(cv, tx, ty, name)


def pix(cv, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        cv[y][x] = c


def rect(cv, x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            pix(cv, xx, yy, c)


def vline(cv, x, y0, y1, c):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        pix(cv, x, y, c)


def hline(cv, y, x0, x1, c):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        pix(cv, x, y, c)


def shed(cv, tx, ty, w_tiles=4, h_tiles=3, lit=False):
    fill_tiles(cv, tx, ty, tx + w_tiles, ty + 1, "roof")
    fill_tiles(cv, tx, ty + 1, tx + w_tiles, ty + h_tiles, "wall")
    if lit:
        blit_tile(cv, tx + 1, ty + 1, "win")
        if w_tiles > 3:
            blit_tile(cv, tx + w_tiles - 2, ty + 1, "win")


def pole(cv, x, y_top, y_bot):
    vline(cv, x, y_top, y_bot, WOOD_SH)
    vline(cv, x + 1, y_top, y_bot, WOOD)
    vline(cv, x + 2, y_top, y_bot, WOOD_DK)
    hline(cv, y_top + 2, x - 10, x + 12, WOOD_DK)
    hline(cv, y_top + 3, x - 10, x + 12, WOOD_SH)
    # net lattice
    for i in range(0, 14, 3):
        vline(cv, x - 8 + i, y_top + 4, y_top + 28, ROPE)
        hline(cv, y_top + 8 + i, x - 8, x + 10, ROPE)


def bollard(cv, x, y):
    rect(cv, x + 1, y, 8, 16, WOOD)
    rect(cv, x + 2, y + 1, 6, 3, WOOD_HI)
    rect(cv, x + 1, y + 16, 8, 3, WOOD_DK)
    hline(cv, y + 10, x, x + 9, ROPE)
    hline(cv, y + 11, x, x + 9, WOOD_DK)
    pix(cv, x + 3, y + 2, LAMP)


def crate(cv, x, y):
    rect(cv, x, y, 16, 16, CRATE)
    hline(cv, y, x, x + 15, WOOD_HI)
    vline(cv, x, y, y + 15, WOOD_HI)
    vline(cv, x + 15, y, y + 15, WOOD_DK)
    hline(cv, y + 15, x, x + 15, WOOD_DK)
    hline(cv, y + 7, x, x + 15, WOOD_SH)
    vline(cv, x + 7, y, y + 15, WOOD_SH)


def unique_tiles(cv) -> int:
    seen = set()
    for ty in range(TH):
        for tx in range(TW):
            key = tuple(cv[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
            seen.add(key)
    return len(seen)


def build() -> list[list[int]]:
    cv = new_canvas(FOG)

    # Sky bands, left orange / right cyan, dithered seam (not a hard cut).
    for ty in range(0, 4):
        hi = ty == 0
        for tx in range(0, 14):
            blit_tile(cv, tx, ty, "sky_or_hi" if hi else "sky_or")
        for tx in range(14, 18):
            blit_tile(cv, tx, ty, "sky_or_d")
        for tx in range(18, 22):
            blit_tile(cv, tx, ty, "sky_mid")
        for tx in range(22, 26):
            blit_tile(cv, tx, ty, "sky_cy_d")
        for tx in range(26, 40):
            blit_tile(cv, tx, ty, "sky_cy_hi" if hi else "sky_cy")
    for tx in range(4, 12):
        blit_tile(cv, tx, 2, "sky_or_d")
    for tx in range(28, 36):
        blit_tile(cv, tx, 2, "sky_cy_d")
    for ty in range(4, 7):
        for tx in range(0, 12):
            blit_tile(cv, tx, ty, "sky_or")
        for tx in range(12, 16):
            blit_tile(cv, tx, ty, "sky_or_d")
        for tx in range(16, 24):
            blit_tile(cv, tx, ty, "sky_mid")
        for tx in range(24, 28):
            blit_tile(cv, tx, ty, "sky_cy_d")
        for tx in range(28, 40):
            blit_tile(cv, tx, ty, "sky_cy")
    for ty in range(7, 11):
        fill_tiles(cv, 0, ty, 40, ty + 1, "sky_fog_d" if ty == 7 else "sky_fog")
    fill_tiles(cv, 0, 11, 40, 12, "horizon")

    # Distant sheds
    shed(cv, 3, 8, 5, 4, lit=True)
    shed(cv, 9, 9, 4, 3, lit=False)
    shed(cv, 28, 8, 5, 4, lit=True)
    shed(cv, 34, 9, 4, 3, lit=True)

    # Far water as horizontal bands (row phase, not 8x8 checker).
    fill_tiles(cv, 0, 12, 40, 13, "water_or")
    fill_tiles(cv, 0, 13, 40, 14, "water")
    fill_tiles(cv, 0, 14, 40, 15, "water2")
    fill_tiles(cv, 0, 15, 40, 16, "water_dk")
    fill_tiles(cv, 10, 15, 22, 16, "plank_sh")

    # Playable piers (hero left, thug right). Rows 18-27 = y 144-223.
    fill_tiles(cv, 0, 18, 20, 28, "plank")
    fill_tiles(cv, 0, 21, 20, 22, "plank2")
    fill_tiles(cv, 0, 24, 20, 25, "plank2")
    fill_tiles(cv, 19, 19, 34, 24, "plank_sh")
    fill_tiles(cv, 22, 18, 40, 23, "plank")
    fill_tiles(cv, 22, 20, 40, 21, "plank2")
    # water pocket lower right so the pier reads as fingers
    fill_tiles(cv, 20, 24, 40, 25, "water_or")
    fill_tiles(cv, 20, 25, 40, 26, "water")
    fill_tiles(cv, 20, 26, 40, 28, "water2")
    fill_tiles(cv, 20, 24, 21, 28, "edge")
    fill_tiles(cv, 19, 18, 20, 24, "edge")
    fill_tiles(cv, 33, 23, 34, 24, "edge")

    # Under the thug feet (x=200-248, y=208) keep planks
    fill_tiles(cv, 24, 25, 32, 28, "plank_sh")
    fill_tiles(cv, 24, 26, 32, 27, "plank")

    # Props
    pole(cv, 28, 40, 150)
    pole(cv, 188, 48, 150)
    pole(cv, 292, 56, 148)
    crate(cv, 40, 136)
    crate(cv, 52, 128)
    crate(cv, 224, 128)
    crate(cv, 240, 136)
    crate(cv, 232, 120)
    bollard(cv, 24, 176)
    bollard(cv, 72, 188)
    bollard(cv, 120, 180)
    bollard(cv, 248, 184)
    bollard(cv, 168, 200)

    return cv


def to_indexed(cv) -> Image.Image:
    im = Image.new("P", (W, H))
    blob = []
    for c in PAL:
        blob.extend(c)
    blob.extend([0, 0, 0] * (256 - 16))
    im.putpalette(blob)
    im.putdata([cv[y][x] for y in range(H) for x in range(W)])
    return im


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    cv = build()
    n = unique_tiles(cv)
    zeros = sum(1 for y in range(H) for x in range(W) if cv[y][x] == 0)
    if zeros:
        raise SystemExit(f"painted index 0 on plane ({zeros} px) — VDP would punch backdrop")
    im = to_indexed(cv)
    im.save(OUT / "dock_320x224_native.png")
    im.save(RES / "dock_320x224.png")
    scene = im.convert("RGB")
    for spr_name, xy in (("hero_48x64.png", (72, 144)), ("thug_48x64.png", (200, 144))):
        spr = Image.open(ROOT / "res" / "sprites" / spr_name)
        pal = spr.getpalette()
        px = spr.load()
        sx, sy = xy
        for j in range(spr.height):
            for i in range(spr.width):
                idx = px[i, j]
                r, g, b = pal[idx * 3 : idx * 3 + 3]
                if idx == 0 or (r, g, b) == (255, 0, 255):
                    continue
                scene.putpixel((sx + i, sy + j), (r, g, b))
    scene.save(OUT / "in_scene_320x224.png")
    report = {
        "method": "native_8x8_vocabulary_not_photo_downscale",
        "compare_flat": True,
        "lab_flattened_reference": True,
        "size": [W, H],
        "palette_line": "PAL2",
        "unique_8x8": n,
        "map_cells": TW * TH,
        "reuse_ratio": round(1.0 - n / (TW * TH), 3),
        "previous_quantize_unique_8x8": 931,
        "dither": "2x2 bayer/checker on sky seams and far water, declared material",
        "index0": "unused/transparent on VDP plane; never painted",
    }
    (DOC / "native_dock_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if n > 400:
        raise SystemExit(f"tile explosion still too high: {n}")


if __name__ == "__main__":
    main()
