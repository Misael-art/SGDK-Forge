#!/usr/bin/env python3
"""Slice the arcade Ken sheet at native pixel size (no SMS 32x64 shrink).

Source: MSSF2T ken_arcade_st_v1.png copied into this folder. Blue (0,85,127)
matte becomes index 0 magenta. Each HAMOOPIG state is one horizontal strip,
cell = max bbox of that action padded to 8x8, capped at 128x128 (ResComp
SPRITE tile grid). Shared 15-colour 9-bit PAL1. Capcom SSF2 Ken is study
material; acceptance stays placeholder / prototype.
"""
from __future__ import annotations

import json
import hashlib
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent / "ken_arcade_st_v1.png"
OUT_SPR = ROOT / "res/sprite/ken"
OUT_PAL = OUT_SPR / "palettes"
OUT_RES = ROOT / "res/ken.res"
OUT_H = ROOT / "inc/player_ken_table.h"
REPORT = ROOT / "rascunho/ken_arcade_convert_report.json"

BG = (0, 85, 127)
MAGENTA = (255, 0, 255)
SNAP = 34  # 0x22
MAX_CELL = 128  # 16 tiles; ResComp SPRITE and scanline sanity
MAX_FRAMES = 12

# Band indices from the 1549x11279 arcade sheet (content rows, labels skipped).
# Native Ken is ~64-144px wide and 96-128px tall; Ryo idle is 64x104.
STATE_BANDS = {
    "100": 10,   # standing guard (idle)
    "101": 18,   # jab
    "102": 19,   # strong punch
    "104": 21,   # fierce
    "105": 22,   # close fierce / upper
    "106": 32,   # high kick
    "151": 29,   # roundhouse
    "200": 11,   # crouch
    "201": 16,   # crouch advance
    "300": 44,   # jump / air
    "420": 14,   # walk (used for 410/420; band 13 is a 64px dwarf cycle)
    "501": 40,   # hit / crumple
    "550": 41,   # knockdown
    "606": 52,   # KO
    "700": 19,   # hadouken body (same punch extend)
    "710": 43,   # shoryuken
    "720": 75,   # tatsu / spinning kick
    "730": 80,   # jump kick chain
}

TIMING = {
    "100": [8, 8, 8, 8, 8, 8],
    "101": [2, 4, 6],
    "102": [3, 3, 8],
    "104": [3, 4, 8],
    "105": [3, 4, 8],
    "106": [3, 4, 10],
    "151": [3, 3, 4, 6, 8],
    "200": [6, 6, 250],
    "201": [4, 4, 4, 4, 4, 4],
    "300": [4, 4, 4, 4, 4, 8],
    "410": [5, 5, 5, 5, 5],
    "420": [5, 5, 5, 5, 5, 5],
    "501": [4, 6, 8],
    "550": [4, 4, 4, 4, 4, 4, 12],
    "606": [8, 8, 8, 250],
    "700": [4, 4, 10],
    "710": [2, 3, 3, 4, 6, 8],
    "720": [3, 3, 3, 3, 3, 3, 3, 6],
    "730": [3, 3, 3, 3, 3, 3, 3, 8],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def is_sheet_bg(rgb, tol=28) -> bool:
    return sum(abs(int(rgb[i]) - BG[i]) for i in range(3)) < tol


def is_bg(rgb, tol=40) -> bool:
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    if is_sheet_bg((r, g, b), tol):
        return True
    # leftover cyan/blue arcade matte (not gi, hair or skin)
    if b >= 130 and r <= 110 and g >= 70 and b > r + 40:
        return True
    return False


def snap9(c: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(max(0, min(238, int(round(v / SNAP) * SNAP))) for v in c)


def content_bands(im: Image.Image) -> list[tuple[int, int]]:
    px = im.load()
    w, h = im.size
    rows = []
    in_run = False
    start = 0
    for y in range(h):
        has = any(not is_sheet_bg(px[x, y][:3]) for x in range(0, w, 4))
        if has and not in_run:
            in_run = True
            start = y
        elif (not has) and in_run:
            in_run = False
            rows.append((start, y))
    if in_run:
        rows.append((start, h))
    return rows


def blobs_x(im: Image.Image, y0: int, y1: int) -> list[tuple[int, int]]:
    px = im.load()
    w = im.size[0]
    col = [False] * w
    for y in range(y0, y1):
        for x in range(w):
            if not is_sheet_bg(px[x, y][:3]):
                col[x] = True
    blobs = []
    on = False
    s = 0
    for x, v in enumerate(col):
        if v and not on:
            on = True
            s = x
        elif (not v) and on:
            on = False
            if x - s >= 16:
                blobs.append((s, x))
    if on and w - s >= 16:
        blobs.append((s, w))
    return blobs


def tight_crop(im: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    crop = im.crop(box)
    px = crop.load()
    w, h = crop.size
    minx, miny, maxx, maxy = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            if not is_bg(px[x, y][:3]):
                found = True
                if x < minx:
                    minx = x
                if y < miny:
                    miny = y
                if x > maxx:
                    maxx = x
                if y > maxy:
                    maxy = y
    if not found:
        return crop
    return crop.crop((minx, miny, maxx + 1, maxy + 1))


def subsample(frames: list[Image.Image], cap: int) -> list[Image.Image]:
    if len(frames) <= cap:
        return frames
    if cap == 1:
        return [frames[0]]
    out = []
    for i in range(cap):
        idx = round(i * (len(frames) - 1) / (cap - 1))
        out.append(frames[idx])
    return out


def pad8(im: Image.Image, cell: tuple[int, int]) -> Image.Image:
    cw, ch = cell
    canvas = Image.new("RGBA", (cw, ch), MAGENTA + (255,))
    src = im.convert("RGBA")
    px = src.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if is_bg((r, g, b)) or a < 16:
                px[x, y] = MAGENTA + (0,)
    x = (cw - src.width) // 2
    y = ch - src.height  # feet on the cell floor
    canvas.paste(src, (max(0, x), max(0, y)), src)
    return canvas


def extract_palette(frames: list[Image.Image]) -> list[tuple[int, int, int]]:
    acc = Counter()
    for im in frames:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                pix = px[x, y]
                r, g, b = pix[:3]
                a = pix[3] if len(pix) == 4 else 255
                if a < 16 or (r, g, b) == MAGENTA or is_bg((r, g, b)):
                    continue
                acc[snap9((r, g, b))] += 1
    colors = [c for c, _ in acc.most_common(15)]
    while len(colors) < 15:
        colors.append((0, 0, 0))
    return [MAGENTA] + colors[:15]


def palette_bytes(palette: list[tuple[int, int, int]]) -> list[int]:
    raw = []
    for c in palette:
        raw.extend(c)
    raw.extend([0, 0, 0] * (256 - len(palette)))
    return raw


def remap(im: Image.Image, palette: list[tuple[int, int, int]], raw: list[int]) -> Image.Image:
    out = Image.new("P", im.size)
    out.putpalette(raw)
    sp = im.load()
    dp = out.load()
    for y in range(im.height):
        for x in range(im.width):
            pix = sp[x, y]
            r, g, b = pix[:3]
            a = pix[3] if len(pix) == 4 else 255
            if a < 16 or (r, g, b) == MAGENTA or is_bg((r, g, b)):
                dp[x, y] = 0
                continue
            s = snap9((r, g, b))
            best = 1
            bd = 10**9
            for i, c in enumerate(palette):
                if i == 0:
                    continue
                d = sum((s[k] - c[k]) ** 2 for k in range(3))
                if d < bd:
                    bd = d
                    best = i
            dp[x, y] = best
    out.info["transparency"] = 0
    return out


def make_pal_png(palette: list[tuple[int, int, int]], path: Path, blue_swap: bool) -> None:
    img = Image.new("P", (8, 8))
    raw = []
    for i, c in enumerate(palette):
        if blue_swap and i > 0 and c[0] >= 170 and c[2] <= 80:
            c = (c[2], c[1], min(238, c[0]))
        raw.extend(c)
    raw.extend([0, 0, 0] * (256 - 16))
    img.putpalette(raw)
    px = img.load()
    for y in range(8):
        for x in range(8):
            px[x, y] = 0
    px[0, 0] = 1
    img.info["transparency"] = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def main() -> None:
    im = Image.open(SRC).convert("RGBA")
    bands = content_bands(im)
    OUT_SPR.mkdir(parents=True, exist_ok=True)
    OUT_PAL.mkdir(parents=True, exist_ok=True)

    prepared = {}
    for state, band_i in STATE_BANDS.items():
        if band_i >= len(bands):
            raise SystemExit(f"band {band_i} missing for state {state} (have {len(bands)})")
        y0, y1 = bands[band_i]
        xs = blobs_x(im, y0, y1)
        frames = []
        for x0, x1 in xs:
            fr = tight_crop(im, (x0, y0, x1, y1))
            if fr.width >= 16 and fr.height >= 32:
                frames.append(fr)
        if not frames:
            raise SystemExit(f"no frames for state {state} band {band_i}")
        frames = subsample(frames, MAX_FRAMES)
        max_w = max(f.width for f in frames)
        max_h = max(f.height for f in frames)
        cw = min(((max_w + 7) // 8) * 8, MAX_CELL)
        ch = min(((max_h + 7) // 8) * 8, MAX_CELL)
        padded = [pad8(f, (cw, ch)) for f in frames]
        prepared[state] = {"frames": padded, "cw": cw, "ch": ch, "native_bbox": [max_w, max_h]}

    all_frames = [f for st in prepared.values() for f in st["frames"]]
    palette = extract_palette(all_frames)
    raw = palette_bytes(palette)

    report = {
        "source": str(SRC),
        "source_sha256": sha256(SRC),
        "no_sms_shrink": True,
        "max_cell_px": MAX_CELL,
        "shared_palette": [list(c) for c in palette],
        "states": {},
    }
    res_lines = [
        "ALIGN",
        "// Ken arcade sheet, native size (not SMS 32x64), PAL shared with pal1.png",
        'SPRITE spr_ken_pal1  "sprite/ken/palettes/pal1.png"  1  1 FAST 0',
        'SPRITE spr_ken_pal2  "sprite/ken/palettes/pal2.png"  1  1 FAST 0',
        "",
    ]
    h_lines = [
        "#ifndef PLAYER_KEN_TABLE_H",
        "#define PLAYER_KEN_TABLE_H",
        '#include "ken.h"',
        "",
        "typedef struct {",
        "    const SpriteDefinition *def;",
        "    u16 w;",
        "    u16 h;",
        "    s16 axisX;",
        "    s16 axisY;",
        "    u8 frames;",
        "    u8 timing[12];",
        "} KenStateAnim;",
        "",
    ]

    make_pal_png(palette, OUT_PAL / "pal1.png", False)
    make_pal_png(palette, OUT_PAL / "pal2.png", True)

    for state, meta in prepared.items():
        # Arcade Ken faces left; HAMOOPIG/Ryo art faces right. Mirror so
        # direcao==1 + SPR_setHFlip(FALSE) looks toward the opponent.
        qframes = [remap(fr, palette, raw).transpose(Image.FLIP_LEFT_RIGHT) for fr in meta["frames"]]
        strip_w = meta["cw"] * len(qframes)
        strip = Image.new("P", (strip_w, meta["ch"]))
        strip.putpalette(raw)
        strip.info["transparency"] = 0
        x = 0
        for fr in qframes:
            strip.paste(fr, (x, 0))
            x += meta["cw"]
        out_png = OUT_SPR / f"{state}.png"
        strip.save(out_png)
        tw, th = meta["cw"] // 8, meta["ch"] // 8
        nfr = len(qframes)
        res_lines.append(
            f'SPRITE spr_ken_{state}  "sprite/ken/{state}.png"  {tw}  {th} FAST 0'
        )
        report["states"][state] = {
            "band": STATE_BANDS[state],
            "frames": nfr,
            "cell": [meta["cw"], meta["ch"]],
            "native_bbox": meta["native_bbox"],
            "tiles": [tw, th],
            "sha256": sha256(out_png),
        }

    OUT_RES.write_text("\n".join(res_lines) + "\n", encoding="utf-8")

    h_lines.append("static inline const KenStateAnim *ken_anim_for(u16 state) {")
    h_lines.append("    switch(state) {")
    for state in STATE_BANDS:
        nfr = report["states"][state]["frames"]
        cw, ch = report["states"][state]["cell"]
        times = TIMING.get(state, [5] * nfr)[:nfr]
        times12 = (times + [0] * 12)[:12]
        tlit = ", ".join(str(t) for t in times12)
        h_lines.append(f"    case {int(state)}: {{")
        h_lines.append("        static const KenStateAnim a = {")
        h_lines.append(f"            &spr_ken_{state}, {cw}, {ch}, {cw // 2}, {ch}, {nfr},")
        h_lines.append(f"            {{ {tlit} }}")
        h_lines.append("        };")
        h_lines.append("        return &a;")
        h_lines.append("    }")
    h_lines.append("    case 610: case 607: case 611: case 612: case 615: return ken_anim_for(100);")
    h_lines.append("    case 608: case 209: case 207: case 208: return ken_anim_for(200);")
    h_lines.append("    case 103: case 113: case 107: case 108: case 109: case 110: return ken_anim_for(102);")
    h_lines.append("    case 202: case 204: case 205: return ken_anim_for(201);")
    h_lines.append("    case 301: case 302: case 304: case 305: case 306:")
    h_lines.append("    case 310: case 311: case 312: case 314: case 315: case 316:")
    h_lines.append("    case 320: case 321: case 322: case 324: case 325: case 326:")
    h_lines.append("        return ken_anim_for(300);")
    h_lines.append("    case 410: case 471: case 472: return ken_anim_for(420);")
    h_lines.append("    case 502: case 503: case 506: case 511: case 512:")
    h_lines.append("    case 551: case 552: case 570: return ken_anim_for(550);")
    h_lines.append("    case 800: case 801: case 802: case 803: return ken_anim_for(102);")
    h_lines.append("    default: return ken_anim_for(100);")
    h_lines.append("    }")
    h_lines.append("}")
    h_lines.append("#endif")
    OUT_H.write_text("\n".join(h_lines) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "states": len(STATE_BANDS), "report": str(REPORT)}, indent=2))


if __name__ == "__main__":
    main()
