#!/usr/bin/env python3
"""4-frame idle breathing strip from the locked 48x64 colored sprites.

Motion phases come from Imagine idle video (chest rise, fist bob).
Pixels are NOT video downscale. Frame 0 is the locked sprite.
Feet stay planted (pivot at soles).
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
KEY = (255, 0, 255)


def load_p(path: Path):
    im = Image.open(path)
    if im.mode != "P":
        raise SystemExit(f"{path} not indexed")
    pal = im.getpalette()[: 16 * 3]
    px = im.load()
    grid = [[int(px[x, y]) for x in range(im.width)] for y in range(im.height)]
    return grid, pal


def copy_grid(g):
    return [row[:] for row in g]


def shift_band(g, y0, y1, dy, x0=0, x1=W):
    """Move non-zero pixels in [y0,y1) x [x0,x1) by dy (negative = up). Boots locked."""
    src = copy_grid(g)
    # clear source band (except boots)
    for y in range(max(y0, 0), min(y1, BOOT_Y)):
        for x in range(x0, x1):
            g[y][x] = 0
    for y in range(max(y0, 0), min(y1, H)):
        if y >= BOOT_Y:
            continue
        ny = y + dy
        if ny < 0 or ny >= BOOT_Y:
            continue
        for x in range(x0, x1):
            v = src[y][x]
            if v:
                g[ny][x] = v
    # restore boots always
    for y in range(BOOT_Y, H):
        g[y] = src[y][:]


def to_im(grid, pal) -> Image.Image:
    im = Image.new("P", (W, H))
    blob = list(pal) + [0] * (768 - len(pal))
    im.putpalette(blob)
    im.putdata([grid[y][x] for y in range(H) for x in range(W)])
    return im


def visible(grid):
    return [[1 if grid[y][x] else 0 for x in range(W)] for y in range(H)]


def foot_y(grid) -> int:
    for y in range(H - 1, -1, -1):
        if any(grid[y]):
            return y
    return H - 1


def build_hero_frames(base):
    f0 = copy_grid(base)
    f1 = copy_grid(base)
    shift_band(f1, 14, BOOT_Y, -1)  # inhale: torso/arms up
    f2 = copy_grid(f1)
    shift_band(f2, 0, 18, -1, x0=34, x1=W)  # peak: raised fist bob up
    f3 = copy_grid(f1)
    shift_band(f3, 0, 18, 1, x0=34, x1=W)  # follow: fist settles
    return [f0, f1, f2, f3]


def build_thug_frames(base):
    f0 = copy_grid(base)
    f1 = copy_grid(base)
    shift_band(f1, 12, 34, -1)  # inhale: chest/shoulders up
    f2 = copy_grid(f1)
    shift_band(f2, 4, 20, -1, x0=0, x1=16)  # left fist bob
    shift_band(f2, 4, 20, -1, x0=32, x1=W)  # right fist bob
    f3 = copy_grid(f1)
    return [f0, f1, f2, f3]


def strip(frames, pal) -> Image.Image:
    im = Image.new("P", (W * len(frames), H))
    blob = list(pal) + [0] * (768 - len(pal))
    im.putpalette(blob)
    for i, g in enumerate(frames):
        cell = to_im(g, pal)
        im.paste(cell, (i * W, 0))
    return im


def gif(frames, pal, path: Path, scale=4):
    imgs = [to_im(g, pal).convert("RGB").resize((W * scale, H * scale), Image.NEAREST) for g in frames]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=150, loop=0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hero_g, hero_pal = load_p(RES / "hero_48x64.png")
    thug_g, thug_pal = load_p(RES / "thug_48x64.png")
    # if already a strip, take cell 0
    if len(hero_g[0]) != W:
        hero_g = [row[:W] for row in hero_g]
    if len(thug_g[0]) != W:
        thug_g = [row[:W] for row in thug_g]

    hf = build_hero_frames(hero_g)
    tf = build_thug_frames(thug_g)

    for i, (h, t) in enumerate(zip(hf, tf)):
        if foot_y(h) != foot_y(hf[0]) or foot_y(t) != foot_y(tf[0]):
            raise SystemExit(f"foot plant drifted at frame {i}")

    hs = strip(hf, hero_pal)
    ts = strip(tf, thug_pal)
    hs.save(OUT / "hero_idle_48x64_strip.png")
    ts.save(OUT / "thug_idle_48x64_strip.png")
    hs.save(RES / "hero_48x64.png")
    ts.save(RES / "thug_48x64.png")
    gif(hf, hero_pal, OUT / "hero_idle.gif")
    gif(tf, thug_pal, OUT / "thug_idle.gif")

    # 4x contact of the strip
    hs.convert("RGB").resize((W * N * 4, H * 4), Image.NEAREST).save(OUT / "hero_idle_strip_4x.png")
    ts.convert("RGB").resize((W * N * 4, H * 4), Image.NEAREST).save(OUT / "thug_idle_strip_4x.png")

    report = {
        "asset_kind": "animation_strip",
        "action": "idle_guard_breathing",
        "frames": N,
        "cell": [W, H],
        "time_vblank": 12,
        "source_motion": [
            "data/source_art/motion/hero_idle_source.mp4",
            "data/source_art/motion/thug_idle_source.mp4",
        ],
        "pixel_route": "locked_48x64_deltas_not_video_downscale",
        "phases": [
            {"i": 0, "name": "rest"},
            {"i": 1, "name": "inhale"},
            {"i": 2, "name": "peak_fist_bob"},
            {"i": 3, "name": "settle"},
        ],
        "pivot": {"hero": [24, 63], "thug": [24, 63], "role": "foot_plant"},
        "foot_lock": True,
        "not_aaa_claim": True,
    }
    (DOC / "idle_strip_report.json").write_text(json.dumps(report, indent=2) + "\n")
    pivots = {
        "frames": [
            {"frame_index": i, "role": "foot_plant", "hero": [24, foot_y(hf[i])], "thug": [24, foot_y(tf[i])]}
            for i in range(N)
        ]
    }
    (OUT / "pivots.json").write_text(json.dumps(pivots, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
