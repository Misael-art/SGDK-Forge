#!/usr/bin/env python3
"""Add a 4-frame punch row under idle+walk on the locked 48x64 sheet.

Phases from Imagine punch video (coil / extend / recover). Pixels are
not video downscale. Rope stays a wrapped fist, not a lasso.
Feet planted at y=63.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

W, H = 48, 64
N = 4
BOOT_Y = 54
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "res" / "sprites"
OUT = ROOT / "data" / "processed" / "motion"
DOC = ROOT / "doc"
OUTLINE = 1
SKIN_H = 2
ROPE = 13  # hero pal


def load_p(path: Path):
    im = Image.open(path)
    pal = im.getpalette()[: 16 * 3]
    px = im.load()
    grid = [[int(px[x, y]) for x in range(im.width)] for y in range(im.height)]
    return grid, pal


def copy_grid(g):
    return [row[:] for row in g]


def rows_of(sheet, row, n=N):
    y0 = row * H
    return [[sheet[y0 + y][i * W:(i + 1) * W] for y in range(H)] for i in range(n)]


def to_im(grid, pal) -> Image.Image:
    im = Image.new("P", (len(grid[0]), len(grid)))
    blob = list(pal) + [0] * (768 - len(pal))
    im.putpalette(blob)
    im.putdata([grid[y][x] for y in range(len(grid)) for x in range(len(grid[0]))])
    return im


def foot_y(g) -> int:
    for y in range(H - 1, -1, -1):
        if any(g[y]):
            return y
    return H - 1


def move_cluster(g, x0, y0, x1, y1, dx, dy):
    src = copy_grid(g)
    cluster = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if src[y][x]:
                cluster.append((x, y, src[y][x]))
                g[y][x] = 0
    for x, y, v in cluster:
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < BOOT_Y:
            g[ny][nx] = v


def shift_torso(g, dx):
    src = copy_grid(g)
    for y in range(0, BOOT_Y):
        for x in range(W):
            g[y][x] = 0
    for y in range(0, BOOT_Y):
        for x in range(W):
            v = src[y][x]
            if not v:
                continue
            nx = x + dx
            if 0 <= nx < W:
                g[y][nx] = v
    for y in range(BOOT_Y, H):
        g[y] = src[y][:]


def arm(g, x0, y0, x1, y1, c, rad=2):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i // n
        y = y0 + (y1 - y0) * i // n
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < BOOT_Y and dx * dx + dy * dy <= rad * rad:
                    if g[yy][xx] == 0:
                        g[yy][xx] = c


def hero_punch(rest):
    # Signature: rope-wrapped fist (right of sprite).
    f0 = copy_grid(rest)
    shift_torso(f0, -2)
    move_cluster(f0, 32, 0, W, 18, -3, 1)  # coil

    f1 = copy_grid(rest)
    shift_torso(f1, -1)
    move_cluster(f1, 32, 0, W, 18, 2, 1)  # extend
    arm(f1, 30, 16, 42, 10, SKIN_H, 2)
    arm(f1, 30, 16, 42, 10, OUTLINE, 1)

    f2 = copy_grid(rest)
    shift_torso(f2, -1)
    move_cluster(f2, 32, 0, W, 18, 3, 2)  # hitstop
    arm(f2, 29, 16, 44, 11, SKIN_H, 2)
    arm(f2, 29, 16, 44, 11, OUTLINE, 1)

    f3 = copy_grid(rest)
    move_cluster(f3, 32, 0, W, 18, -1, 0)  # recover
    return [f0, f1, f2, f3]


def thug_punch(rest):
    # Left-hand cross: more travel than the already-edge right fist.
    f0 = copy_grid(rest)
    shift_torso(f0, -1)
    move_cluster(f0, 0, 4, 16, 20, -1, 1)
    arm(f0, 14, 16, 6, 12, 3, 2)
    arm(f0, 14, 16, 6, 12, OUTLINE, 1)

    f1 = copy_grid(rest)
    shift_torso(f1, 1)
    move_cluster(f1, 0, 4, 16, 20, 10, 2)  # fist shoots across
    arm(f1, 14, 16, 24, 12, 3, 2)  # skin base idx 3
    arm(f1, 14, 16, 24, 12, OUTLINE, 1)

    f2 = copy_grid(rest)
    shift_torso(f2, 2)
    move_cluster(f2, 0, 4, 16, 20, 14, 3)
    arm(f2, 16, 16, 28, 14, 3, 2)
    arm(f2, 16, 16, 28, 14, OUTLINE, 1)

    f3 = copy_grid(rest)
    move_cluster(f3, 0, 4, 16, 20, 4, 1)
    return [f0, f1, f2, f3]


def compose(idle, walk, punch, pal) -> Image.Image:
    im = Image.new("P", (W * N, H * 3))
    blob = list(pal) + [0] * (768 - len(pal))
    im.putpalette(blob)
    for i, g in enumerate(idle):
        im.paste(to_im(g, pal), (i * W, 0))
    for i, g in enumerate(walk):
        im.paste(to_im(g, pal), (i * W, H))
    for i, g in enumerate(punch):
        im.paste(to_im(g, pal), (i * W, H * 2))
    return im


def gif(frames, pal, path: Path, scale=4, durations=None):
    imgs = [
        to_im(g, pal).convert("RGB").resize((W * scale, H * scale), Image.NEAREST)
        for g in frames
    ]
    durs = durations or [150] * len(frames)
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durs, loop=0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hg, hpal = load_p(RES / "hero_48x64.png")
    tg, tpal = load_p(RES / "thug_48x64.png")
    n_rows = len(hg) // H
    idle_h, walk_h = rows_of(hg, 0), rows_of(hg, 1 if n_rows > 1 else 0)
    idle_t, walk_t = rows_of(tg, 0), rows_of(tg, 1 if n_rows > 1 else 0)
    rest_h, rest_t = idle_h[0], idle_t[0]

    hp = hero_punch(rest_h)
    tp = thug_punch(rest_t)
    for i, g in enumerate(hp + tp):
        if foot_y(g) < 62:
            raise SystemExit(f"punch lost plant frame {i} fy={foot_y(g)}")

    hs = compose(idle_h, walk_h, hp, hpal)
    ts = compose(idle_t, walk_t, tp, tpal)
    hs.save(OUT / "hero_iwp_sheet.png")
    ts.save(OUT / "thug_iwp_sheet.png")
    hs.save(RES / "hero_48x64.png")
    ts.save(RES / "thug_48x64.png")
    gif(hp, hpal, OUT / "hero_punch.gif", durations=[130, 70, 170, 200])
    gif(tp, tpal, OUT / "thug_punch.gif", durations=[130, 70, 170, 200])
    hs.convert("RGB").resize((W * N * 2, H * 3 * 2), Image.NEAREST).save(OUT / "hero_iwp_2x.png")
    ts.convert("RGB").resize((W * N * 2, H * 3 * 2), Image.NEAREST).save(OUT / "thug_iwp_2x.png")

    report = {
        "asset_kind": "animation_strip",
        "action": "punch_straight",
        "phases": ["anticipation", "active", "hitstop", "recovery"],
        "timing_vblank": [8, 4, 10, 12],
        "sheet": [W * N, H * 3],
        "anims": ["idle", "walk", "punch"],
        "source_motion": [
            "data/source_art/motion/hero_punch_source.mp4",
            "data/source_art/motion/thug_punch_source.mp4",
        ],
        "pixel_route": "locked_48x64_not_video_downscale",
        "hero_weapon": "rope_wrap_stays_on_fist_not_lasso",
        "pivot": {"y": 63, "role": "foot_plant"},
        "not_aaa_claim": True,
    }
    (DOC / "punch_strip_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
