#!/usr/bin/env python3
"""Native 48x64 CRIA idle (lineart 1px + hue-shift color + 4-frame lean).

Source is Imagine construction drawings in data/source_art/. Pixels are
stamped on the 48x64 grid. Harvest video is motion reference only: feet stay
planted (video drifted into a step and is refused as downscale source).
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 48, 64
N = 4
KEY = (0xFF, 0x00, 0xFF)
STEPS = (0x00, 0x22, 0x44, 0x66, 0x88, 0xAA, 0xCC, 0xEE)
FOOT_LOCK = 60

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "res" / "sprites" / "characters" / "cria"
PROC = ROOT / "data" / "processed" / "characters" / "cria"
DOC = ROOT / "doc" / "art" / "characters" / "cria"
MOTION = ROOT / "data" / "processed" / "motion"


def snap(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    def s(v: int) -> int:
        return min(STEPS, key=lambda t: abs(t - v))

    return s(rgb[0]), s(rgb[1]), s(rgb[2])


# PAL3 enemy roster seed (Cria now; Estivador later shares leather/dark).
PAL = [
    KEY,                          # 0
    snap((0x22, 0x00, 0x44)),     # 1 outline
    snap((0xCC, 0x88, 0x66)),     # 2 skin hi
    snap((0xAA, 0x66, 0x44)),     # 3 skin base
    snap((0x88, 0x44, 0x66)),     # 4 skin sh
    snap((0x66, 0x88, 0xCC)),     # 5 tank hi
    snap((0x44, 0x66, 0x88)),     # 6 tank base
    snap((0x22, 0x44, 0x66)),     # 7 tank sh
    snap((0x66, 0x88, 0xAA)),     # 8 shorts hi
    snap((0x44, 0x66, 0xAA)),     # 9 shorts base
    snap((0x22, 0x22, 0x66)),     # 10 shorts sh
    snap((0xCC, 0x22, 0x44)),     # 11 red (brim/star/wrist)
    snap((0x44, 0x22, 0x22)),     # 12 hair
    snap((0x22, 0x22, 0x44)),     # 13 flip-flop
    snap((0x88, 0x66, 0x44)),     # 14 strap / leather seed
    snap((0xEE, 0xEE, 0xEE)),     # 15 eye
]

I_OUT, I_SK_HI, I_SK, I_SK_SH = 1, 2, 3, 4
I_TK_HI, I_TK, I_TK_SH = 5, 6, 7
I_SH_HI, I_SH, I_SH_SH = 8, 9, 10
I_RED, I_HAIR, I_FF, I_STR, I_EYE = 11, 12, 13, 14, 15


def raster(polygons=None, ellipses=None, lines=None, pixels=None) -> list[list[int]]:
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


def stamp(canvas, mask, fill: int, ink: int = I_OUT) -> None:
    ol = outline(mask)
    for y in range(H):
        for x in range(W):
            if ol[y][x]:
                canvas[y][x] = ink
            elif mask[y][x] and canvas[y][x] == 0:
                canvas[y][x] = fill


def paint(canvas, pts, idx: int) -> None:
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H and canvas[y][x] not in (0, I_OUT):
            canvas[y][x] = idx


def ink(canvas, pts) -> None:
    for x, y in pts:
        if 0 <= x < W and 0 <= y < H and canvas[y][x] != 0:
            canvas[y][x] = I_OUT


def disc(cx, cy, r):
    pts = []
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                pts.append((x, y))
    return pts


def limb(x0, y0, x1, y1, rad: int) -> list[list[int]]:
    im = Image.new("1", (W, H), 0)
    d = ImageDraw.Draw(im)
    d.line([(x0, y0), (x1, y1)], fill=1, width=max(2, rad * 2 - 1))
    d.ellipse((x0 - rad, y0 - rad, x0 + rad, y0 + rad), fill=1)
    d.ellipse((x1 - rad, y1 - rad, x1 + rad, y1 + rad), fill=1)
    return [[1 if im.getpixel((x, y)) else 0 for x in range(W)] for y in range(H)]


def empty() -> list[list[int]]:
    return [[0] * W for _ in range(H)]


def build_pose() -> list[list[int]]:
    """3/4 left, 30-degree lean, both flip-flops planted at y=60."""
    c = empty()

    # Flip-flops: soles sit on y=59-60 so pivot 60 matches TAÍNA.
    stamp(c, raster(polygons=[[(26, 58), (39, 58), (39, 60), (25, 60)]]), I_FF)
    stamp(c, raster(polygons=[[(10, 58), (22, 58), (22, 60), (9, 60)]]), I_FF)

    # Thighs first (rad 4) so they are not sausages.
    stamp(c, limb(28, 38, 32, 49, 4), I_SK)
    stamp(c, limb(32, 49, 34, 58, 3), I_SK)
    paint(c, [(30, 43), (31, 44), (33, 51), (34, 54)], I_SK_SH)

    stamp(c, limb(20, 37, 16, 48, 4), I_SK)
    stamp(c, limb(16, 48, 14, 58, 3), I_SK)
    paint(c, [(18, 42), (17, 43), (15, 51), (14, 54)], I_SK_SH)

    stamp(
        c,
        raster(
            polygons=[
                [
                    (16, 33),
                    (31, 33),
                    (34, 38),
                    (33, 47),
                    (24, 48),
                    (16, 47),
                    (14, 39),
                ]
            ]
        ),
        I_SH,
    )
    paint(c, [(17, 35), (18, 36), (19, 36), (30, 35), (31, 36)], I_SH_HI)
    paint(c, [(22, 40), (23, 41), (24, 42), (25, 41), (26, 40), (20, 45), (28, 45)], I_SH_SH)
    stamp(c, raster(polygons=[[(14, 46), (22, 46), (22, 49), (14, 49)]]), I_SH_HI)
    stamp(c, raster(polygons=[[(26, 46), (34, 46), (34, 49), (26, 49)]]), I_SH_HI)

    stamp(
        c,
        raster(
            polygons=[
                [
                    (15, 19),
                    (27, 20),
                    (29, 26),
                    (28, 34),
                    (17, 35),
                    (13, 28),
                    (13, 22),
                ]
            ]
        ),
        I_TK,
    )
    paint(c, [(16, 21), (17, 22), (18, 23), (19, 22), (20, 21), (21, 22)], I_TK_HI)
    paint(c, [(25, 27), (26, 28), (27, 30), (26, 32), (15, 30)], I_TK_SH)
    paint(c, [(21, 26), (22, 26), (23, 26), (22, 27), (21, 27)], I_RED)

    stamp(c, limb(27, 21, 33, 31, 3), I_SK)
    stamp(c, limb(33, 31, 30, 42, 3), I_SK)
    paint(c, [(31, 27), (34, 33), (32, 37)], I_SK_SH)
    paint(c, [(30, 36), (31, 36), (32, 36), (30, 37), (31, 37), (32, 37)], I_RED)

    stamp(c, limb(15, 20, 10, 30, 3), I_SK)
    stamp(c, limb(10, 30, 8, 40, 3), I_SK)
    paint(c, [(12, 25), (9, 33), (8, 36)], I_SK_SH)
    stamp(c, raster(ellipses=[(6, 38, 12, 44)]), I_SK)
    paint(c, [(7, 40), (8, 41)], I_SK_HI)

    stamp(c, raster(polygons=[[(17, 16), (23, 16), (23, 21), (16, 21)]]), I_SK)
    stamp(c, raster(ellipses=[(12, 6, 26, 20)]), I_SK)
    paint(c, [(15, 10), (16, 11), (17, 12), (14, 13)], I_SK_HI)
    paint(c, [(21, 14), (22, 15), (20, 16)], I_SK_SH)

    stamp(c, raster(polygons=[[(14, 13), (24, 12), (25, 17), (15, 18)]]), I_HAIR)

    stamp(
        c,
        raster(polygons=[[(12, 5), (24, 4), (26, 8), (25, 13), (13, 14), (11, 9)]]),
        I_TK,
    )
    paint(c, [(14, 6), (15, 6), (16, 7), (17, 6), (18, 7)], I_TK_HI)
    # Backwards visor is a short nape wedge, not a snout.
    stamp(c, raster(polygons=[[(23, 7), (30, 8), (29, 12), (22, 11)]]), I_RED)
    paint(c, [(24, 9), (25, 10)], I_TK_SH)

    ink(c, [(13, 10), (15, 10), (16, 10), (17, 10)])
    paint(c, [(13, 12), (14, 12), (15, 12)], I_EYE)
    ink(c, [(13, 12)])
    ink(c, [(12, 13), (13, 14), (14, 15)])
    ink(c, [(13, 17), (15, 17), (16, 17)])

    paint(c, [(14, 58), (15, 58), (16, 57), (31, 58), (32, 58), (30, 57)], I_STR)
    paint(c, [(15, 20), (16, 21), (26, 22)], I_SK_HI)
    return c


def copy_grid(g):
    return [row[:] for row in g]


def nudge_pixels(g, pred, dx, dy, protect_y=FOOT_LOCK):
    """Move matching pixels without clearing the whole band (keeps hip/neck)."""
    src = copy_grid(g)
    moving = []
    for y in range(H):
        for x in range(W):
            if pred(x, y, src[y][x]):
                moving.append((x, y, src[y][x]))
    for x, y, _ in moving:
        g[y][x] = src[y][x]
    for x, y, v in moving:
        g[y][x] = 0
    for x, y, v in moving:
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < protect_y and v:
            g[ny][nx] = v
    for y in range(protect_y, H):
        g[y] = src[y][:]
    for y in range(protect_y):
        for x in range(W):
            if g[y][x] != 0:
                continue
            n = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and g[ny][nx]:
                    n.append(g[ny][nx])
            if len(n) >= 3:
                g[y][x] = n[0]


def to_im(grid) -> Image.Image:
    im = Image.new("P", (W, H))
    blob = []
    for rgb in PAL:
        blob.extend(rgb)
    blob += [0] * (768 - len(blob))
    im.putpalette(blob)
    im.putdata([grid[y][x] for y in range(H) for x in range(W)])
    return im


def bbox(grid):
    xs, ys = [], []
    for y in range(H):
        for x in range(W):
            if grid[y][x]:
                xs.append(x)
                ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def foot_y(grid) -> int:
    for y in range(H - 1, -1, -1):
        if any(grid[y]):
            return y
    return H - 1


def unique_colors(grid) -> int:
    return len({v for row in grid for v in row if v})


def write_png(im: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def main() -> None:
    base = build_pose()
    frames = [base]
    # Nervous idle: cap/head 1px, near fist 1px. Flip-flops stay planted.
    f1 = copy_grid(base)
    nudge_pixels(f1, lambda x, y, v: v and y <= 15, 0, -1)
    frames.append(f1)
    f2 = copy_grid(base)
    nudge_pixels(f2, lambda x, y, v: v and x <= 12 and 36 <= y <= 44, -1, 0)
    frames.append(f2)
    f3 = copy_grid(base)
    nudge_pixels(f3, lambda x, y, v: v and y <= 14, 0, -1)
    nudge_pixels(f3, lambda x, y, v: v and x <= 12 and 36 <= y <= 44, 0, 1)
    frames.append(f3)

    sheet = Image.new("P", (W * N, H))
    blob = []
    for rgb in PAL:
        blob.extend(rgb)
    blob += [0] * (768 - len(blob))
    sheet.putpalette(blob)
    for i, g in enumerate(frames):
        sheet.paste(to_im(g), (i * W, 0))

    res_path = RES / "cria_idle_lean_48x64_v01.png"
    proc_path = PROC / "animation" / "cria_idle_lean_48x64_v01.png"
    line_path = PROC / "lineart" / "cria_idle_lineart_48x64_v01.png"
    sil_path = PROC / "review" / "cria_idle_silhouette_48x64_v01.png"
    gif_path = MOTION / "cria_idle.gif"
    sheet2_path = MOTION / "cria_idle_2x.png"
    contact_path = PROC / "review" / "cria_idle_contact_native_v01.png"

    write_png(sheet, res_path)
    write_png(sheet, proc_path)

    line = to_im(base)
    # 3-index lineart export: key / paper / ink
    lim = Image.new("P", (W, H))
    lpal = list(KEY) + [0xEE, 0xEE, 0xCC] + [0x22, 0x00, 0x44] + [0] * (768 - 9)
    lim.putpalette(lpal)
    lim.putdata([0 if base[y][x] == 0 else (2 if base[y][x] == I_OUT else 1) for y in range(H) for x in range(W)])
    write_png(lim, line_path)

    sil = Image.new("P", (W, H))
    sil.putpalette(list(KEY) + [0, 0, 0] + [0] * (768 - 6))
    sil.putdata([0 if base[y][x] == 0 else 1 for y in range(H) for x in range(W)])
    write_png(sil, sil_path)

    preview = []
    durations = [160, 140, 160, 140]
    for g in frames:
        rgb = to_im(g).convert("RGB")
        preview.append(rgb.resize((W * 4, H * 4), Image.NEAREST))
    preview[0].save(gif_path, save_all=True, append_images=preview[1:], duration=durations, loop=0, disposal=2)

    sheet2 = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
    write_png(sheet2.convert("RGB"), sheet2_path)

    contact = Image.new("RGB", (W * N * 2, H * 2), (40, 40, 40))
    for i, g in enumerate(frames):
        contact.paste(to_im(g).convert("RGB").resize((W * 2, H * 2), Image.NEAREST), (i * W * 2, 0))
    write_png(contact, contact_path)

    boxes = [bbox(g) for g in frames]
    feet = [foot_y(g) for g in frames]
    report = {
        "asset_kind": "animation_strip",
        "action": "idle_lean_nervous",
        "character": "cria",
        "cell": [W, H],
        "frames": N,
        "timing_vblank": [8, 7, 8, 7],
        "pivot": {"x": 24, "y": 60, "role": "foot_plant"},
        "facing": "left_opponent",
        "pixel_route": "locked_48x64_not_video_downscale",
        "source_construction": [
            "data/source_art/concept/cria_identity_model_sheet/cria_idle_construction_34_v01.png",
            "data/source_art/concept/cria_identity_model_sheet/cria_idle_lineart_construction_v01.png",
        ],
        "source_motion_ref_only": "data/source_art/motion/cria_idle_source.mp4",
        "video_drift": "harvest_lifted_back_foot_refused_as_pixel_source",
        "must_preserve": [
            "forward_lean",
            "backwards_cap_red_visor",
            "pointy_elbows",
            "flip_flops_planted",
            "red_star_and_wrist",
            "wiry_thin_mass",
        ],
        "bbox_frame0": list(boxes[0]) if boxes[0] else None,
        "visible_height": (boxes[0][3] - boxes[0][1] + 1) if boxes[0] else None,
        "foot_y": feet,
        "unique_indices_frame0": unique_colors(base),
        "palette_slot": "PAL3_enemy_roster",
        "not_aaa_claim": True,
        "res": str(res_path.relative_to(ROOT)),
    }
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / "cria_idle_native_v01_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
