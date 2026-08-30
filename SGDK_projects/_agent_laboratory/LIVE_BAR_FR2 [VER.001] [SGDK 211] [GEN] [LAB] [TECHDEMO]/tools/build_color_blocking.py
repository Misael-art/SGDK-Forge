#!/usr/bin/env python3
"""Color blocking on the locked 48x64 lineart. Does not move silhouette pixels.

Ink that touches empty stays outline/dark_shadow (not a swap slot).
Paper and ink-fill interiors get hue-shift ramps by material.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location("lineart", HERE / "build_lineart_blocking_1px.py")
la = importlib.util.module_from_spec(spec)
sys.modules["lineart"] = la
spec.loader.exec_module(la)

W, H = la.W, la.H
KEY = (0xFF, 0x00, 0xFF)
STEPS = (0x00, 0x22, 0x44, 0x66, 0x88, 0xAA, 0xCC, 0xEE)
OUT = ROOT / "data" / "processed" / "color"
LINEART = ROOT / "data" / "processed" / "lineart"
RES = ROOT / "res" / "sprites"
DOC = ROOT / "doc"


def snap(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    def s(v: int) -> int:
        return min(STEPS, key=lambda t: abs(t - v))

    return s(rgb[0]), s(rgb[1]), s(rgb[2])


# index 0 = key, 1 = outline. Remaining are materials.
HERO_PAL = [
    KEY,
    snap((0x22, 0x00, 0x44)),  # 1 outline / dark_shadow
    snap((0xCC, 0x88, 0x66)),  # 2 skin hi  warm
    snap((0xAA, 0x66, 0x44)),  # 3 skin base
    snap((0x88, 0x44, 0x66)),  # 4 skin sh  cool
    snap((0x66, 0xEE, 0xCC)),  # 5 vest hi  warm-teal (not dock #448888)
    snap((0x22, 0xCC, 0xAA)),  # 6 vest base
    snap((0x22, 0x88, 0xAA)),  # 7 vest sh  cool
    snap((0xEE, 0xCC, 0x44)),  # 8 hair blonde
    snap((0x22, 0xAA, 0xAA)),  # 9 hair teal
    snap((0xAA, 0x88, 0x44)),  # 10 pants base
    snap((0x88, 0x66, 0x44)),  # 11 pants sh
    snap((0x66, 0x44, 0x22)),  # 12 boot
    snap((0xCC, 0xAA, 0x22)),  # 13 rope / lace
    snap((0x44, 0x22, 0x44)),  # 14 bra
    snap((0xEE, 0xEE, 0xEE)),  # 15 eye
]

THUG_PAL = [
    KEY,
    snap((0x44, 0x00, 0x22)),  # 1 outline
    snap((0xEE, 0xCC, 0xAA)),  # 2 skin hi
    snap((0xCC, 0xAA, 0x88)),  # 3 skin base
    snap((0xAA, 0x66, 0x88)),  # 4 skin sh cool
    snap((0xEE, 0x66, 0x44)),  # 5 tank hi warm
    snap((0xCC, 0x22, 0x22)),  # 6 tank base
    snap((0x88, 0x00, 0x44)),  # 7 tank sh cool
    snap((0xAA, 0xCC, 0x44)),  # 8 shorts hi
    snap((0x66, 0x88, 0x22)),  # 9 shorts base
    snap((0x44, 0x66, 0x44)),  # 10 shorts sh
    snap((0x22, 0x00, 0x22)),  # 11 hair/beard
    snap((0x66, 0x44, 0x22)),  # 12 boot
    snap((0xCC, 0x66, 0x22)),  # 13 hook
    snap((0x88, 0x22, 0x00)),  # 14 hook sh
    snap((0xEE, 0xEE, 0xEE)),  # 15 eye
]

# material -> (hi, base, shadow) palette indices
HERO_RAMPS = {
    "skin": (2, 3, 4),
    "vest": (5, 6, 7),
    "hair_blonde": (8, 8, 9),
    "hair_teal": (9, 9, 1),
    "pants": (10, 10, 11),
    "boot": (12, 12, 1),
    "rope": (13, 13, 10),
    "bra": (14, 14, 1),
    "eye": (15, 15, 15),
    "outline": (1, 1, 1),
}

THUG_RAMPS = {
    "skin": (2, 3, 4),
    "tank": (5, 6, 7),
    "shorts": (8, 9, 10),
    "hair": (11, 11, 1),
    "boot": (12, 12, 1),
    "hook": (13, 13, 14),
    "eye": (15, 15, 15),
    "outline": (1, 1, 1),
}


def load_structure(path: Path) -> list[list[int]]:
    """0 empty, 1 paper, 2 ink from the locked lineart PNG."""
    im = Image.open(path)
    if im.mode != "P":
        raise SystemExit(f"{path} is not indexed")
    px = im.load()
    canvas = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            canvas[y][x] = int(px[x, y])
    return canvas


def touches(struct, x, y, val) -> bool:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if not (0 <= nx < W and 0 <= ny < H):
            if val == 0:
                return True
            continue
        if struct[ny][nx] == val:
            return True
    return False


def is_linework(struct, x, y) -> bool:
    """Silhouette ink or interior construction. Solid fills are not linework."""
    if struct[y][x] != 2:
        return False
    return touches(struct, x, y, 0) or touches(struct, x, y, 1)


def in_mask(mask, x, y) -> bool:
    return bool(mask[y][x])


def assign_hero(struct, parts) -> list[list[str]]:
    mat = [["empty"] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if struct[y][x] == 0:
                continue
            if is_linework(struct, x, y):
                mat[y][x] = "outline"
                continue
            if (x, y) in ((26, 8), (25, 8)):
                mat[y][x] = "eye"
            elif in_mask(parts["hair"], x, y):
                mat[y][x] = "hair_blonde" if y <= 6 or x <= 24 else "hair_teal"
            elif in_mask(parts["bra"], x, y):
                mat[y][x] = "bra"
            elif in_mask(parts["vest_l"], x, y) or in_mask(parts["vest_r"], x, y):
                mat[y][x] = "vest"
            elif in_mask(parts["raised"], x, y) and y <= 13 and x >= 36:
                mat[y][x] = "rope"
            elif in_mask(parts["back_boot"], x, y) or in_mask(parts["front_boot"], x, y):
                mat[y][x] = "boot"
            elif in_mask(parts["back_leg"], x, y) or in_mask(parts["front_leg"], x, y):
                mat[y][x] = "pants"
            elif (
                in_mask(parts["head_skin"], x, y)
                or in_mask(parts["neck"], x, y)
                or in_mask(parts["low_arm"], x, y)
                or in_mask(parts["raised"], x, y)
                or in_mask(parts["torso"], x, y)
            ):
                mat[y][x] = "skin"
            elif y >= 58 and 7 <= x <= 14 or y >= 59 and 32 <= x <= 41:
                mat[y][x] = "rope"  # laces
            elif y >= 52:
                mat[y][x] = "boot"
            elif y >= 36:
                mat[y][x] = "pants"
            else:
                mat[y][x] = "skin"
    return mat


def assign_thug(struct, parts) -> list[list[str]]:
    mat = [["empty"] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if struct[y][x] == 0:
                continue
            if is_linework(struct, x, y):
                mat[y][x] = "outline"
                continue
            if (x, y) in ((24, 7), (28, 7)):
                mat[y][x] = "eye"
            elif in_mask(parts["hair"], x, y) or in_mask(parts["beard"], x, y):
                mat[y][x] = "hair"
            elif in_mask(parts["hook"], x, y):
                mat[y][x] = "hook"
            elif in_mask(parts["left_boot"], x, y) or in_mask(parts["right_boot"], x, y):
                mat[y][x] = "boot"
            elif in_mask(parts["left_leg"], x, y) or in_mask(parts["right_leg"], x, y):
                mat[y][x] = "shorts"
            elif in_mask(parts["shorts"], x, y):
                mat[y][x] = "shorts"
            elif in_mask(parts["torso"], x, y) and 14 <= y <= 32:
                mat[y][x] = "tank"
            elif (
                in_mask(parts["head_skin"], x, y)
                or in_mask(parts["neck"], x, y)
                or in_mask(parts["left_arm"], x, y)
                or in_mask(parts["right_arm"], x, y)
            ):
                mat[y][x] = "skin"
            elif y >= 52:
                mat[y][x] = "boot"
            elif y >= 32:
                mat[y][x] = "shorts"
            elif 14 <= y <= 31:
                mat[y][x] = "tank"
            else:
                mat[y][x] = "skin"
    return mat


def shade_index(x, y, mat, ramps, elite: bool) -> int:
    name = mat[y][x]
    if name == "empty":
        return 0
    hi, base, sh = ramps[name]
    if not elite or name in ("outline", "eye"):
        return 1 if name == "outline" else base
    n = mat[y - 1][x] if y else "empty"
    w = mat[y][x - 1] if x else "empty"
    s = mat[y + 1][x] if y < H - 1 else "empty"
    e = mat[y][x + 1] if x < W - 1 else "empty"
    lit = n != name or w != name
    shady = s != name or e != name
    if lit and not shady:
        return hi
    if shady and not lit:
        return sh
    return base


def paint(struct, mat, pal, ramps, elite: bool) -> list[list[int]]:
    out = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if struct[y][x] == 0:
                out[y][x] = 0
            else:
                out[y][x] = shade_index(x, y, mat, ramps, elite)
    return out


def to_indexed(canvas, pal) -> Image.Image:
    im = Image.new("P", (W, H))
    blob = []
    for c in pal:
        blob.extend(c)
    blob.extend([0, 0, 0] * (256 - len(pal)))
    im.putpalette(blob)
    im.putdata([canvas[y][x] for y in range(H) for x in range(W)])
    return im


def visible_mask(canvas) -> list[list[int]]:
    return [[1 if canvas[y][x] else 0 for x in range(W)] for y in range(H)]


def same_silhouette(a, b) -> bool:
    for y in range(H):
        for x in range(W):
            if bool(a[y][x]) != bool(b[y][x]):
                return False
    return True


def used_indices(canvas) -> list[int]:
    s = set()
    for y in range(H):
        for x in range(W):
            s.add(canvas[y][x])
    return sorted(s)


def scale_nn(im: Image.Image, k: int) -> Image.Image:
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def contact(line_h, basic_h, elite_h, line_t, basic_t, elite_t) -> Image.Image:
    sheet = Image.new("RGB", (320, 224), (0x22, 0x22, 0x44))
    def paste(im, x, y):
        sheet.paste(scale_nn(im.convert("RGB"), 2), (x, y))
    paste(line_h, 8, 8)
    paste(basic_h, 112, 8)
    paste(elite_h, 216, 8)
    paste(line_t, 8, 112)
    paste(basic_t, 112, 112)
    paste(elite_t, 216, 112)
    return sheet


def in_scene(hero, thug) -> Image.Image:
    dock = Image.open(ROOT / "res" / "bgs" / "dock_320x224.png").convert("RGB")

    def paste_sprite(dst, spr, x, y):
        pal = spr.getpalette()
        px = spr.load()
        for j in range(spr.height):
            for i in range(spr.width):
                idx = px[i, j]
                r, g, b = pal[idx * 3 : idx * 3 + 3]
                if (r, g, b) == KEY or idx == 0:
                    continue
                dst.putpixel((x + i, y + j), (r, g, b))

    paste_sprite(dock, hero, 72, 144)
    paste_sprite(dock, thug, 200, 144)
    return dock


def assert_nine_bit(pal):
    for i, c in enumerate(pal):
        if i == 0:
            continue
        if any(ch not in STEPS for ch in c):
            raise SystemExit(f"non 9-bit color index {i}: {c}")


def main() -> None:
    assert_nine_bit(HERO_PAL)
    assert_nine_bit(THUG_PAL)
    OUT.mkdir(parents=True, exist_ok=True)

    hero_src = LINEART / "hero_48x64_lineart.png"
    thug_src = LINEART / "thug_48x64_lineart.png"
    hs = load_structure(hero_src)
    ts = load_structure(thug_src)
    hp = la.hero_part_masks()
    tp = la.thug_part_masks()
    hm = assign_hero(hs, hp)
    tm = assign_thug(ts, tp)

    hero_basic = paint(hs, hm, HERO_PAL, HERO_RAMPS, elite=False)
    hero_elite = paint(hs, hm, HERO_PAL, HERO_RAMPS, elite=True)
    thug_basic = paint(ts, tm, THUG_PAL, THUG_RAMPS, elite=False)
    thug_elite = paint(ts, tm, THUG_PAL, THUG_RAMPS, elite=True)

    if not same_silhouette(hs, hero_elite) or not same_silhouette(ts, thug_elite):
        raise SystemExit("silhouette drifted — color blocking moved pixels")

    hero_l = Image.open(hero_src)
    thug_l = Image.open(thug_src)
    hb = to_indexed(hero_basic, HERO_PAL)
    he = to_indexed(hero_elite, HERO_PAL)
    tb = to_indexed(thug_basic, THUG_PAL)
    te = to_indexed(thug_elite, THUG_PAL)

    he.save(OUT / "hero_48x64_elite.png")
    hb.save(OUT / "hero_48x64_basic.png")
    te.save(OUT / "thug_48x64_elite.png")
    tb.save(OUT / "thug_48x64_basic.png")
    scale_nn(he, 8).save(OUT / "hero_48x64_elite_8x.png")
    scale_nn(te, 8).save(OUT / "thug_48x64_elite_8x.png")
    scale_nn(hb, 8).save(OUT / "hero_48x64_basic_8x.png")
    scale_nn(tb, 8).save(OUT / "thug_48x64_basic_8x.png")
    contact(hero_l, hb, he, thug_l, tb, te).save(OUT / "contact_lineart_basic_elite_320x224.png")
    in_scene(he, te).save(OUT / "in_scene_320x224.png")

    he.save(RES / "hero_48x64.png")
    te.save(RES / "thug_48x64.png")

    def mat_counts(mat):
        c = {}
        for y in range(H):
            for x in range(W):
                n = mat[y][x]
                if n != "empty":
                    c[n] = c.get(n, 0) + 1
        return c

    report = {
        "contract": "color_blocking_on_locked_lineart",
        "silhouette_locked": True,
        "nine_bit": True,
        "hero": {
            "used_indices_elite": used_indices(hero_elite),
            "materials": mat_counts(hm),
            "palette": ["#%02X%02X%02X" % c for c in HERO_PAL],
        },
        "thug": {
            "used_indices_elite": used_indices(thug_elite),
            "materials": mat_counts(tm),
            "palette": ["#%02X%02X%02X" % c for c in THUG_PAL],
        },
    }
    (DOC / "color_blocking_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
