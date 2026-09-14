#!/usr/bin/env python3
"""Build HAMOOPIG Musgo strips from authorial swamp-golem sources.

Musgo is an original grappler. The CPS2 heavy-fighter sheet is a technical
reference for mass, timing language and cell budget only — never a pixel
source. Art faces RIGHT so direcao==1 + SPR_setHFlip(FALSE) looks at P2.
Idle cell is larger than Ken 64x96, capped at 128px for ResComp SPRITE.
Acceptance: source_candidate / placeholder prototype, not native pixel final.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent
OUT_SPR = ROOT / "res/sprite/musgo"
OUT_PAL = OUT_SPR / "palettes"
OUT_RES = ROOT / "res/musgo.res"
OUT_H = ROOT / "inc/player_musgo_table.h"
REPORT = ROOT / "rascunho/musgo_convert_report.json"

MAGENTA = (255, 0, 255)
SNAP = 34
MAX_CELL = 128
MAX_FRAMES = 12

# Visible height target per action (then pad to 8). Grappler > Ken idle 96.
TARGET_H = {
    "100": 104,
    "101": 104,
    "102": 104,
    "104": 120,
    "105": 104,
    "106": 104,
    "151": 104,
    "200": 88,
    "201": 88,
    "300": 112,
    "420": 104,
    "501": 96,
    "550": 88,
    "606": 88,
    "700": 120,
    "710": 120,
    "720": 104,
    "730": 112,
}

TIMING = {
    "100": [8, 8, 8, 8],
    "101": [8],
    "102": [4, 4, 8],
    "104": [6, 10],
    "105": [4, 4, 8],
    "106": [4, 4],
    "151": [4, 4, 8],
    "200": [8],
    "201": [6, 6, 6],
    "300": [4, 4, 99],
    "420": [6, 6, 6, 6, 6, 6],
    "501": [6, 8],
    "550": [4, 4, 99],
    "606": [8],
    "700": [4, 10],
    "710": [3, 4, 8],
    "720": [3, 3, 3, 6],
    "730": [3, 3, 8],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def is_chroma(rgb) -> bool:
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    if (r, g, b) == MAGENTA:
        return True
    # JPEG/video magenta and hot pink matte
    if r >= 170 and b >= 150 and g <= 140 and r + b > g * 2 + 80:
        return True
    if r >= 210 and b >= 190 and g <= 170:
        return True
    return False


def snap9(c: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(max(0, min(238, int(round(v / SNAP) * SNAP))) for v in c)


def load_keyed(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 16 or is_chroma((r, g, b)):
                px[x, y] = MAGENTA + (0,)
    return im


def tight_crop(im: Image.Image) -> Image.Image:
    px = im.load()
    w, h = im.size
    minx, miny, maxx, maxy = w, h, 0, 0
    found = False
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= 16 and not is_chroma((r, g, b)):
                found = True
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x)
                maxy = max(maxy, y)
    if not found:
        raise SystemExit("empty frame after chroma key")
    return im.crop((minx, miny, maxx + 1, maxy + 1))


def scale_to_height(im: Image.Image, target_h: int, max_w: int) -> Image.Image:
    w, h = im.size
    scale = target_h / float(h)
    nw = max(8, int(round(w * scale)))
    nh = max(8, int(round(h * scale)))
    if nw > max_w:
        scale = max_w / float(w)
        nw = max_w
        nh = max(8, int(round(h * scale)))
    nw = min(nw, MAX_CELL)
    nh = min(nh, MAX_CELL)
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def pad8(im: Image.Image, cell: tuple[int, int]) -> Image.Image:
    cw, ch = cell
    canvas = Image.new("RGBA", (cw, ch), MAGENTA + (0,))
    src = im.convert("RGBA")
    px = src.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if is_chroma((r, g, b)) or a < 16:
                px[x, y] = MAGENTA + (0,)
    x = (cw - src.width) // 2
    y = ch - src.height
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
                if a < 16 or (r, g, b) == MAGENTA or is_chroma((r, g, b)):
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
            if a < 16 or (r, g, b) == MAGENTA or is_chroma((r, g, b)):
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


def make_pal_png(palette: list[tuple[int, int, int]], path: Path, p2: bool) -> None:
    img = Image.new("P", (8, 8))
    raw = []
    for i, c in enumerate(palette):
        if p2 and i > 0:
            r, g, b = c
            # P2: moss toward teal, peat toward violet
            c = (
                max(0, min(238, int(r * 0.55 + b * 0.25))),
                max(0, min(238, int(g * 0.85 + b * 0.20))),
                max(0, min(238, int(b * 0.45 + g * 0.40 + 40))),
            )
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


def prepare_frame(path: Path, target_h: int) -> Image.Image:
    keyed = load_keyed(path)
    crop = tight_crop(keyed)
    return scale_to_height(crop, target_h, MAX_CELL - 8)


def concat_strip(frames: list[Image.Image]) -> Image.Image:
    w, h = frames[0].size
    sheet = Image.new("P", (w * len(frames), h))
    sheet.putpalette(frames[0].getpalette())
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * w, 0))
    sheet.info["transparency"] = 0
    return sheet


def main() -> None:
    vf = SRC / "video_frames"
    poses = SRC / "poses"
    sources = {
        "100": [vf / "idle" / "f001.png", vf / "idle" / "f013.png",
                vf / "idle" / "f024.png", vf / "idle" / "f036.png"],
        "101": [poses / "haymaker.jpg"],
        "102": [vf / "punch" / "f010.png", poses / "haymaker.jpg",
                vf / "idle" / "f001.png"],
        "104": [poses / "overhead_slam.jpg", poses / "haymaker.jpg"],
        "105": [vf / "punch" / "f010.png", poses / "haymaker.jpg",
                vf / "idle" / "f001.png"],
        "106": [vf / "punch" / "f010.png", poses / "haymaker.jpg"],
        "151": [vf / "punch" / "f010.png", poses / "haymaker.jpg",
                vf / "idle" / "f001.png"],
        "200": [poses / "crouch.jpg"],
        "201": [poses / "crouch.jpg", vf / "walk" / "f008.png", poses / "crouch.jpg"],
        "300": [vf / "walk" / "f008.png", poses / "idle_side_master.jpg",
                vf / "walk" / "f008.png"],
        "420": [vf / "walk" / "f001.png", vf / "walk" / "f008.png",
                vf / "walk" / "f016.png", vf / "walk" / "f024.png",
                vf / "walk" / "f032.png", vf / "walk" / "f040.png"],
        "501": [vf / "punch" / "f010.png", poses / "crouch.jpg"],
        "550": [poses / "crouch.jpg", vf / "punch" / "f010.png", poses / "crouch.jpg"],
        "606": [poses / "crouch.jpg"],
        "700": [poses / "overhead_slam.jpg", poses / "haymaker.jpg"],
        "710": [vf / "punch" / "f010.png", poses / "overhead_slam.jpg",
                poses / "haymaker.jpg"],
        "720": [vf / "walk" / "f008.png", poses / "haymaker.jpg",
                vf / "walk" / "f032.png", vf / "idle" / "f001.png"],
        "730": [vf / "walk" / "f008.png", poses / "haymaker.jpg",
                vf / "walk" / "f008.png"],
    }

    OUT_SPR.mkdir(parents=True, exist_ok=True)
    OUT_PAL.mkdir(parents=True, exist_ok=True)

    prepared = {}
    for state, paths in sources.items():
        th = TARGET_H[state]
        frames = [prepare_frame(p, th) for p in paths]
        max_w = max(f.width for f in frames)
        max_h = max(f.height for f in frames)
        cw = min(((max_w + 7) // 8) * 8, MAX_CELL)
        ch = min(((max_h + 7) // 8) * 8, MAX_CELL)
        padded = [pad8(f, (cw, ch)) for f in frames]
        prepared[state] = {
            "frames": padded,
            "cw": cw,
            "ch": ch,
            "native_bbox": [max_w, max_h],
            "sources": [str(p.relative_to(ROOT)) for p in paths],
        }

    all_frames = [f for st in prepared.values() for f in st["frames"]]
    palette = extract_palette(all_frames)
    raw = palette_bytes(palette)

    report = {
        "character_id": "musgo",
        "ip_status": "original",
        "style_id": "angular_cps2_fighter",
        "facing": "right",
        "claim_ceiling": "source_candidate_runtime_prototype",
        "reference_policy": "cps2_heavy_grappler_used_as_scale_timing_mass_only",
        "max_cell_px": MAX_CELL,
        "shared_palette": [list(c) for c in palette],
        "states": {},
    }

    res_lines = [
        "ALIGN",
        "// Musgo original swamp grappler. Faces right. PAL shared with pal1.png",
        'SPRITE spr_musgo_pal1  "sprite/musgo/palettes/pal1.png"  1  1 FAST 0',
        'SPRITE spr_musgo_pal2  "sprite/musgo/palettes/pal2.png"  1  1 FAST 0',
        "",
    ]
    h_lines = [
        "#ifndef PLAYER_MUSGO_TABLE_H",
        "#define PLAYER_MUSGO_TABLE_H",
        '#include "musgo.h"',
        "",
        "typedef struct {",
        "    const SpriteDefinition *def;",
        "    u16 w;",
        "    u16 h;",
        "    s16 axisX;",
        "    s16 axisY;",
        "    u8 frames;",
        "    u8 timing[12];",
        "} MusgoStateAnim;",
        "",
        "static inline const MusgoStateAnim *musgo_anim_for(u16 state) {",
        "    switch(state) {",
    ]

    make_pal_png(palette, OUT_PAL / "pal1.png", False)
    make_pal_png(palette, OUT_PAL / "pal2.png", True)

    def_map = {}
    for state in sorted(prepared.keys(), key=lambda s: int(s)):
        meta = prepared[state]
        qframes = [remap(fr, palette, raw) for fr in meta["frames"]]
        strip = concat_strip(qframes)
        out_png = OUT_SPR / f"{state}.png"
        strip.save(out_png)
        tw = meta["cw"] // 8
        th = meta["ch"] // 8
        n = len(qframes)
        res_lines.append(
            f'SPRITE spr_musgo_{state}  "sprite/musgo/{state}.png"  {tw}  {th} FAST 0'
        )
        timing = (TIMING.get(state) or [8] * n)[:n]
        timing = timing + [0] * (12 - len(timing))
        axis_x = meta["cw"] // 2
        axis_y = meta["ch"]
        h_lines.append(f"    case {int(state)}: {{")
        h_lines.append("        static const MusgoStateAnim a = {")
        h_lines.append(
            f"            &spr_musgo_{state}, {meta['cw']}, {meta['ch']}, "
            f"{axis_x}, {axis_y}, {n},"
        )
        h_lines.append(
            "            { " + ", ".join(str(t) for t in timing) + " }"
        )
        h_lines.append("        };")
        h_lines.append("        return &a;")
        h_lines.append("    }")
        def_map[state] = n
        report["states"][state] = {
            "png": str(out_png.relative_to(ROOT)),
            "sha256": sha256(out_png),
            "cell_px": [meta["cw"], meta["ch"]],
            "frames": n,
            "sources": meta["sources"],
        }

    aliases = [
        ("    case 610: case 607: case 611: case 612: case 615: return musgo_anim_for(100);",),
        ("    case 608: case 209: case 207: case 208: return musgo_anim_for(200);",),
        ("    case 103: case 113: case 107: case 108: case 109: case 110: case 152: return musgo_anim_for(102);",),
        ("    case 154: return musgo_anim_for(104);",),
        ("    case 155: return musgo_anim_for(105);",),
        ("    case 202: case 204: case 205: return musgo_anim_for(201);",),
        ("    case 301: case 302: case 304: case 305: case 306:",),
        ("    case 310: case 311: case 312: case 314: case 315: case 316:",),
        ("    case 320: case 321: case 322: case 324: case 325: case 326:",),
        ("        return musgo_anim_for(300);",),
        ("    case 410: case 471: case 472: return musgo_anim_for(420);",),
        ("    case 502: case 503: case 506: case 511: case 512:",),
        ("    case 551: case 552: case 570: return musgo_anim_for(550);",),
        ("    case 800: case 801: case 802: case 803: return musgo_anim_for(102);",),
        ("    default: return musgo_anim_for(100);",),
    ]
    for line in aliases:
        h_lines.append(line[0])
    h_lines += ["    }", "}", "", "#endif", ""]

    OUT_RES.write_text("\n".join(res_lines) + "\n", encoding="utf-8")
    OUT_H.write_text("\n".join(h_lines) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {OUT_RES} {OUT_H} states={len(prepared)} pal={palette[1:5]}")


if __name__ == "__main__":
    main()
