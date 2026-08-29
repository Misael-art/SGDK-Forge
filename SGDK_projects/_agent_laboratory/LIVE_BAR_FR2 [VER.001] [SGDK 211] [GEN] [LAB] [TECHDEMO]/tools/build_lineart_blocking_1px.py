#!/usr/bin/env python3
"""Native 48x64 lineart_blocking_1px for LIVE_BAR_FR2 hero/thug.

Reconstructs on the target grid from Imagine construction drawings.
Does not downscale the painting. Single dark temp ink + paper fill.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 48, 64
INK = (0x22, 0x00, 0x44)
INK_THUG = (0x44, 0x00, 0x22)
PAPER = (0xEE, 0xEE, 0xCC)
KEY = (0xFF, 0x00, 0xFF)

EMPTY, PAPER_I, INK_I = 0, 1, 2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "lineart"
RES = ROOT / "res" / "sprites"
DOC = ROOT / "doc"


def raster(polygons=None, ellipses=None, pixels=None, lines=None) -> list[list[int]]:
    im = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(im)
    for poly in polygons or []:
        if len(poly) >= 3:
            d.polygon(poly, fill=1)
        elif len(poly) == 2:
            d.line(poly, fill=1)
        elif len(poly) == 1:
            d.point(poly[0], fill=1)
    for box in ellipses or []:
        d.ellipse(box, fill=1)
    for a, b in lines or []:
        d.line([a, b], fill=1)
    mask = [[1 if im.getpixel((x, y)) else 0 for x in range(W)] for y in range(H)]
    for x, y in pixels or []:
        if 0 <= x < W and 0 <= y < H:
            mask[y][x] = 1
    return mask


def outline(mask: list[list[int]]) -> list[list[int]]:
    out = [[0] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if not mask[y][x]:
                continue
            edge = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < W and 0 <= ny < H) or not mask[ny][nx]:
                    edge = True
                    break
            out[y][x] = 1 if edge else 0
    return out


def stamp_part(canvas: list[list[int]], mask: list[list[int]], fill: int = PAPER_I) -> None:
    ol = outline(mask)
    for y in range(H):
        for x in range(W):
            if ol[y][x]:
                canvas[y][x] = INK_I
            elif mask[y][x]:
                canvas[y][x] = fill


def ink_line(canvas: list[list[int]], points: list[tuple[int, int]]) -> None:
    im = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(im)
    if len(points) == 1:
        d.point(points[0], fill=1)
    else:
        d.line(points, fill=1)
    for y in range(H):
        for x in range(W):
            if im.getpixel((x, y)) and canvas[y][x] != EMPTY:
                canvas[y][x] = INK_I


def ink_pixels(canvas: list[list[int]], pts: list[tuple[int, int]], only_on=None) -> None:
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H:
            if only_on is None or canvas[y][x] in only_on:
                if canvas[y][x] != EMPTY:
                    canvas[y][x] = INK_I


def paper_pixels(canvas: list[list[int]], pts: list[tuple[int, int]]) -> None:
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H and canvas[y][x] != EMPTY:
            canvas[y][x] = PAPER_I


def clear_pixels(canvas: list[list[int]], pts: list[tuple[int, int]]) -> None:
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H:
            canvas[y][x] = EMPTY


def neighbors8(canvas, x, y, val):
    n = 0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and canvas[ny][nx] == val:
                n += 1
    return n


def neighbors4(canvas, x, y, val):
    n = 0
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and canvas[ny][nx] == val:
            n += 1
    return n


def clean_orphans(canvas: list[list[int]]) -> int:
    removed = 0
    changed = True
    while changed:
        changed = False
        for y in range(H):
            for x in range(W):
                if canvas[y][x] != INK_I:
                    continue
                if neighbors8(canvas, x, y, INK_I) == 0:
                    canvas[y][x] = PAPER_I if neighbors4(canvas, x, y, PAPER_I) else EMPTY
                    removed += 1
                    changed = True
    return removed


def clean_double_corners(canvas: list[list[int]]) -> int:
    """Thin fat *outline* 2x2s. Never punch holes in ink fills (hair/bra/beard)."""
    removed = 0
    for y in range(H - 1):
        for x in range(W - 1):
            block = [
                (x, y),
                (x + 1, y),
                (x, y + 1),
                (x + 1, y + 1),
            ]
            if any(canvas[py][px] != INK_I for px, py in block):
                continue
            if any(neighbors4(canvas, px, py, EMPTY) == 0 for px, py in block):
                continue
            scores = []
            for px, py in block:
                scores.append((neighbors4(canvas, px, py, INK_I), px, py))
            scores.sort(reverse=True)
            _, rx, ry = scores[0]
            canvas[ry][rx] = PAPER_I if neighbors4(canvas, rx, ry, PAPER_I) else EMPTY
            removed += 1
    return removed


def visible(canvas: list[list[int]]) -> list[list[int]]:
    return [[1 if canvas[y][x] != EMPTY else 0 for x in range(W)] for y in range(H)]


def bbox(mask: list[list[int]]) -> tuple[int, int, int, int] | None:
    xs, ys = [], []
    for y in range(H):
        for x in range(W):
            if mask[y][x]:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def to_image(canvas: list[list[int]], silhouette: bool = False, ink=INK) -> Image.Image:
    im = Image.new("P", (W, H))
    pal = list(KEY) + list(PAPER) + list(ink)
    pal += [0, 0, 0] * (256 - 3)
    if silhouette:
        pal = list(KEY) + [0, 0, 0] + [0, 0, 0]
        pal += [0, 0, 0] * (256 - 3)
    im.putpalette(pal)
    data = []
    for y in range(H):
        for x in range(W):
            v = canvas[y][x]
            if silhouette:
                data.append(1 if v != EMPTY else 0)
            else:
                data.append(v)
    im.putdata(data)
    return im


def scale_nn(im: Image.Image, k: int) -> Image.Image:
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def audit(canvas: list[list[int]]) -> dict:
    ink_n = paper_n = empty_n = 0
    orphans = 0
    outline_2x2 = 0
    for y in range(H):
        for x in range(W):
            v = canvas[y][x]
            if v == INK_I:
                ink_n += 1
                if neighbors8(canvas, x, y, INK_I) == 0:
                    orphans += 1
            elif v == PAPER_I:
                paper_n += 1
            else:
                empty_n += 1
    for y in range(H - 1):
        for x in range(W - 1):
            block = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
            if any(canvas[py][px] != INK_I for px, py in block):
                continue
            if all(neighbors4(canvas, px, py, EMPTY) > 0 for px, py in block):
                outline_2x2 += 1
    vis = visible(canvas)
    box = bbox(vis)
    return {
        "ink_pixels": ink_n,
        "paper_pixels": paper_n,
        "empty_pixels": empty_n,
        "orphan_ink": orphans,
        "outline_ink_2x2_blocks": outline_2x2,
        "bbox": box,
        "bbox_area": None if box is None else (box[2] - box[0] + 1) * (box[3] - box[1] + 1),
        "filled_ratio": round((ink_n + paper_n) / (W * H), 3),
    }


def build_hero() -> list[list[int]]:
    canvas = [[EMPTY] * W for _ in range(H)]

    back_leg = raster(
        polygons=[
            [(16, 36), (24, 36), (22, 45), (18, 52), (12, 55), (9, 55), (12, 47), (15, 40)],
        ]
    )
    back_boot = raster(
        polygons=[
            [(6, 52), (16, 52), (16, 59), (6, 59)],
            [(4, 59), (18, 59), (18, 63), (3, 63)],
        ]
    )
    torso = raster(
        polygons=[
            [(17, 16), (24, 14), (30, 16), (31, 22), (28, 32), (26, 36), (19, 36), (17, 28), (16, 20)],
        ]
    )
    neck = raster(polygons=[[(21, 14), (26, 14), (26, 17), (21, 17)]])
    head_skin = raster(ellipses=[(18, 3, 30, 16)])
    hair = raster(
        polygons=[
            [(19, 0), (25, 0), (28, 2), (29, 6), (26, 5), (22, 2), (18, 2), (17, 1)],
            [(26, 6), (32, 7), (34, 12), (33, 18), (29, 17), (27, 12), (26, 8)],
            [(17, 3), (20, 3), (20, 8), (17, 7)],
        ]
    )
    front_leg = raster(
        polygons=[
            [(24, 36), (32, 36), (36, 44), (38, 52), (32, 53), (28, 45), (25, 39)],
        ]
    )
    front_boot = raster(
        polygons=[
            [(30, 51), (42, 51), (42, 58), (30, 58)],
            [(28, 58), (45, 58), (46, 63), (28, 63)],
        ]
    )
    vest_l = raster(
        polygons=[
            [(13, 16), (20, 15), (20, 22), (19, 35), (12, 34), (11, 22)],
        ]
    )
    vest_r = raster(
        polygons=[
            [(26, 15), (33, 16), (34, 23), (32, 35), (25, 35), (25, 21)],
        ]
    )
    bra = raster(polygons=[[(20, 19), (26, 19), (26, 25), (20, 25)]])
    low_arm = raster(
        polygons=[
            [(15, 16), (21, 17), (20, 24), (16, 28), (17, 22)],
            [(9, 24), (18, 24), (19, 32), (16, 35), (8, 35), (7, 29)],
            [(16, 24), (19, 22), (20, 26), (17, 28)],
        ]
    )
    raised = raster(
        polygons=[
            [(28, 15), (34, 14), (40, 9), (40, 5), (35, 5), (31, 11), (27, 14)],
            [(37, 2), (45, 2), (46, 10), (44, 13), (37, 13), (36, 7)],
            [(35, 3), (38, 3), (38, 8), (35, 7)],
        ],
        pixels=[(45, 12), (46, 13), (46, 14), (45, 15), (44, 15)],
    )

    stamp_part(canvas, back_leg)
    stamp_part(canvas, back_boot)
    stamp_part(canvas, torso)
    stamp_part(canvas, neck)
    stamp_part(canvas, head_skin)
    stamp_part(canvas, hair, fill=INK_I)
    stamp_part(canvas, front_leg)
    stamp_part(canvas, front_boot)
    stamp_part(canvas, vest_l)
    stamp_part(canvas, vest_r)
    stamp_part(canvas, bra, fill=INK_I)
    stamp_part(canvas, low_arm)
    stamp_part(canvas, raised)

    ink_line(canvas, [(23, 6), (28, 6)])
    ink_pixels(canvas, [(25, 8), (26, 8), (27, 8)])
    paper_pixels(canvas, [(26, 8)])
    ink_pixels(canvas, [(27, 10)])
    ink_line(canvas, [(24, 12), (27, 13)])
    ink_line(canvas, [(19, 8), (19, 11)])
    ink_line(canvas, [(21, 5), (24, 6)])

    ink_line(canvas, [(20, 16), (20, 19)])
    ink_line(canvas, [(25, 16), (25, 19)])
    ink_line(canvas, [(15, 23), (18, 25)])
    ink_line(canvas, [(19, 35), (25, 35)])

    ink_line(canvas, [(14, 42), (18, 42), (18, 46), (14, 46), (14, 42)])
    ink_line(canvas, [(31, 47), (34, 50)])

    ink_line(canvas, [(37, 5), (44, 5)])
    ink_line(canvas, [(37, 8), (44, 8)])
    ink_line(canvas, [(36, 11), (43, 11)])

    ink_pixels(canvas, [(8, 27), (10, 27), (12, 27)])
    ink_pixels(canvas, [(39, 3), (41, 3), (43, 3)])

    ink_line(canvas, [(6, 59), (16, 59)])
    ink_line(canvas, [(30, 58), (42, 58)])
    ink_line(canvas, [(8, 61), (13, 61)])
    ink_line(canvas, [(33, 60), (40, 60)])

    clear_pixels(canvas, [(35, 11)])

    clean_double_corners(canvas)
    clean_orphans(canvas)
    return canvas


def build_thug() -> list[list[int]]:
    canvas = [[EMPTY] * W for _ in range(H)]

    left_leg = raster(
        polygons=[
            [(12, 42), (21, 42), (20, 50), (14, 55), (9, 55), (11, 48)],
        ]
    )
    left_boot = raster(
        polygons=[
            [(6, 52), (17, 52), (17, 59), (6, 59)],
            [(4, 59), (19, 59), (19, 63), (3, 63)],
        ]
    )
    right_leg = raster(
        polygons=[
            [(26, 42), (36, 42), (38, 50), (37, 55), (30, 55), (28, 48)],
        ]
    )
    right_boot = raster(
        polygons=[
            [(30, 52), (42, 52), (42, 59), (30, 59)],
            [(28, 59), (45, 59), (45, 63), (28, 63)],
        ]
    )
    shorts = raster(
        polygons=[
            [(11, 32), (37, 32), (36, 44), (13, 44)],
            [(6, 34), (13, 33), (14, 43), (6, 42)],
            [(34, 34), (42, 36), (41, 44), (34, 43)],
        ]
    )
    torso = raster(
        ellipses=[(10, 16, 38, 34)],
        polygons=[
            [(14, 12), (22, 11), (32, 12), (36, 18), (14, 18)],
        ],
    )
    neck = raster(polygons=[[(22, 13), (30, 13), (30, 16), (22, 16)]])
    head_skin = raster(ellipses=[(19, 2, 32, 15)])
    hair = raster(
        polygons=[
            [(21, 0), (30, 0), (31, 5), (20, 5), (20, 2)],
        ]
    )
    beard = raster(
        polygons=[
            [(21, 11), (31, 11), (30, 17), (26, 18), (22, 17)],
        ]
    )
    hook = raster(
        polygons=[
            [(9, 30), (14, 30), (14, 34), (12, 34), (12, 31), (9, 31)],
            [(10, 33), (13, 33), (12, 40), (8, 44), (6, 42), (9, 37), (10, 34)],
        ]
    )
    left_arm = raster(
        polygons=[
            [(13, 13), (20, 14), (19, 21), (13, 19), (12, 15)],
            [(4, 7), (12, 6), (13, 14), (11, 16), (4, 15), (3, 10)],
            [(11, 8), (14, 8), (14, 13), (11, 12)],
        ]
    )
    right_arm = raster(
        polygons=[
            [(28, 13), (36, 12), (37, 18), (31, 20), (28, 16)],
            [(36, 5), (45, 5), (45, 14), (42, 16), (36, 15), (35, 9)],
            [(34, 7), (37, 7), (37, 12), (34, 11)],
        ]
    )

    stamp_part(canvas, left_leg)
    stamp_part(canvas, left_boot)
    stamp_part(canvas, right_leg)
    stamp_part(canvas, right_boot)
    stamp_part(canvas, shorts)
    stamp_part(canvas, torso)
    stamp_part(canvas, neck)
    stamp_part(canvas, head_skin)
    stamp_part(canvas, hair, fill=INK_I)
    stamp_part(canvas, beard, fill=INK_I)
    stamp_part(canvas, hook)
    stamp_part(canvas, left_arm)
    stamp_part(canvas, right_arm)

    ink_line(canvas, [(22, 5), (29, 5)])
    ink_pixels(canvas, [(23, 7), (24, 7), (27, 7), (28, 7)])
    paper_pixels(canvas, [(24, 7), (28, 7)])
    ink_pixels(canvas, [(23, 6)])
    ink_pixels(canvas, [(26, 9)])
    ink_line(canvas, [(31, 7), (31, 10)])

    ink_line(canvas, [(21, 13), (30, 13)])
    ink_line(canvas, [(16, 14), (19, 21)])
    ink_line(canvas, [(32, 14), (30, 21)])
    ink_line(canvas, [(13, 24), (18, 26), (28, 26), (34, 24)])
    ink_line(canvas, [(12, 32), (36, 32)])
    ink_pixels(canvas, [(23, 32), (24, 32), (23, 33), (24, 33)])

    ink_line(canvas, [(13, 43), (34, 43)])
    ink_line(canvas, [(7, 37), (12, 37), (12, 41), (7, 40)])

    ink_pixels(canvas, [(5, 7), (7, 7), (9, 7)])
    ink_pixels(canvas, [(38, 6), (40, 6), (42, 6)])

    ink_line(canvas, [(6, 59), (17, 59)])
    ink_line(canvas, [(30, 59), (42, 59)])
    ink_line(canvas, [(8, 61), (14, 61)])
    ink_line(canvas, [(33, 61), (40, 61)])

    clear_pixels(canvas, [(15, 7), (15, 8), (15, 9), (33, 7), (33, 8), (33, 9)])

    clean_double_corners(canvas)
    clean_orphans(canvas)
    return canvas


def must_preserve_hero(canvas) -> list[str]:
    fails = []
    vis = visible(canvas)
    box = bbox(vis)
    if box is None or box[3] < 60 or box[2] - box[0] < 36:
        fails.append("silhouette_does_not_fill_48x64")
    # raised fist cluster near top-right
    fist = sum(vis[y][x] for y in range(0, 15) for x in range(35, 47))
    if fist < 20:
        fails.append("raised_fist_missing")
    # two boots
    boot_l = sum(vis[y][x] for y in range(52, 64) for x in range(0, 20))
    boot_r = sum(vis[y][x] for y in range(52, 64) for x in range(26, 48))
    if boot_l < 20 or boot_r < 20:
        fails.append("boots_missing")
    # open vest gap around chest
    gap = sum(1 for y in range(18, 28) for x in range(21, 25) if canvas[y][x] == PAPER_I)
    if gap < 6:
        fails.append("vest_opening_unreadable")
    # eye present
    if canvas[8][26] != INK_I and canvas[8][27] != INK_I:
        fails.append("eye_missing")
    return fails


def must_preserve_thug(canvas) -> list[str]:
    fails = []
    vis = visible(canvas)
    box = bbox(vis)
    if box is None or box[3] < 60 or box[2] - box[0] < 38:
        fails.append("silhouette_does_not_fill_48x64")
    fist_l = sum(vis[y][x] for y in range(4, 19) for x in range(0, 15))
    fist_r = sum(vis[y][x] for y in range(4, 19) for x in range(33, 48))
    if fist_l < 18 or fist_r < 18:
        fails.append("guard_fists_missing")
    hook = sum(vis[y][x] for y in range(28, 45) for x in range(5, 12))
    if hook < 10:
        fails.append("hook_missing")
    belly = sum(vis[y][x] for y in range(18, 32) for x in range(12, 38))
    if belly < 80:
        fails.append("barrel_torso_missing")
    return fails


def contact_sheet(hero: Image.Image, thug: Image.Image) -> Image.Image:
    sheet = Image.new("RGB", (320, 224), (0x44, 0x22, 0x44))
    h3 = scale_nn(hero.convert("RGB"), 3)
    t3 = scale_nn(thug.convert("RGB"), 3)
    sheet.paste(h3, (8, 16))
    sheet.paste(t3, (168, 16))
    return sheet


def in_scene(hero: Image.Image, thug: Image.Image) -> Image.Image:
    dock = ROOT / "res" / "bgs" / "dock_320x224.png"
    if dock.exists():
        scene = Image.open(dock).convert("RGB")
    else:
        scene = Image.new("RGB", (320, 224), (0x22, 0x22, 0x44))
    def paste_sprite(dst, spr, x, y):
        rgba = spr.convert("RGBA")
        px = rgba.load()
        for j in range(spr.height):
            for i in range(spr.width):
                r, g, b, a = px[i, j]
                if (r, g, b) == KEY:
                    continue
                dst.putpixel((x + i, y + j), (r, g, b))
    paste_sprite(scene, hero, 72, 144)
    paste_sprite(scene, thug, 200, 144)
    return scene


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)

    hero_c = build_hero()
    thug_c = build_thug()
    hero_fail = must_preserve_hero(hero_c)
    thug_fail = must_preserve_thug(thug_c)
    hero_audit = audit(hero_c)
    thug_audit = audit(thug_c)

    hero_im = to_image(hero_c, ink=INK)
    thug_im = to_image(thug_c, ink=INK_THUG)
    hero_sil = to_image(hero_c, silhouette=True)
    thug_sil = to_image(thug_c, silhouette=True)

    hero_im.save(OUT / "hero_48x64_lineart.png")
    thug_im.save(OUT / "thug_48x64_lineart.png")
    hero_sil.save(OUT / "hero_48x64_silhouette.png")
    thug_sil.save(OUT / "thug_48x64_silhouette.png")
    scale_nn(hero_im, 8).save(OUT / "hero_48x64_lineart_8x.png")
    scale_nn(thug_im, 8).save(OUT / "thug_48x64_lineart_8x.png")
    scale_nn(hero_sil, 8).save(OUT / "hero_48x64_silhouette_8x.png")
    scale_nn(thug_sil, 8).save(OUT / "thug_48x64_silhouette_8x.png")
    contact_sheet(hero_im, thug_im).save(OUT / "contact_sheet_320x224.png")
    in_scene(hero_im, thug_im).save(OUT / "in_scene_320x224.png")

    hero_im.save(RES / "hero_48x64.png")
    thug_im.save(RES / "thug_48x64.png")

    report = {
        "contract": "lineart_blocking_1px",
        "grid": [48, 64],
        "ink_hero": "#220044",
        "ink_thug": "#440022",
        "paper": "#EEEECC",
        "index0": "#FF00FF",
        "color_blocking_started": False,
        "method": "native_part_clusters_then_1px_outline",
        "not_used": [
            "photo_downscale",
            "obsolete_downscale_sprites_as_generation_source",
            "pixel_art_prompted_as_final",
        ],
        "hero": {
            "audit": hero_audit,
            "must_preserve_failures": hero_fail,
            "pass": not hero_fail and hero_audit["orphan_ink"] == 0,
        },
        "thug": {
            "audit": thug_audit,
            "must_preserve_failures": thug_fail,
            "pass": not thug_fail and thug_audit["orphan_ink"] == 0,
        },
        "palette_role_map_preview": {
            "index0": "transparent",
            "paper_temp": "construction fill; discarded at color blocking",
            "ink_temp": "maps to outline/dark_shadow; not a palette-swap slot",
        },
    }
    (DOC / "lineart_blocking_1px.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if hero_fail or thug_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
