#!/usr/bin/env python3
"""4-frame 3/4 walk on the locked 48x64 colored sprites.

Gait phases from Imagine walk-in-place video. Pixels are not video
downscale. Row0 of the sheet stays idle; row1 is walk. Planted sole y=63.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

W, H = 48, 64
N = 4
ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "res" / "sprites"
OUT = ROOT / "data" / "processed" / "motion"
DOC = ROOT / "doc"

# hero pal: pants 10/11, boot 12, outline 1
# thug pal: shorts 8/9/10, boot 12, outline 1
OUTLINE = 1


def load_p(path: Path):
    im = Image.open(path)
    if im.mode != "P":
        raise SystemExit(f"{path} not indexed")
    pal = im.getpalette()[: 16 * 3]
    px = im.load()
    grid = [[int(px[x, y]) for x in range(im.width)] for y in range(im.height)]
    return grid, pal


def cell0(grid):
    return [row[:W] for row in grid]


def copy_grid(g):
    return [row[:] for row in g]


def to_im(grid, pal) -> Image.Image:
    im = Image.new("P", (len(grid[0]), len(grid)))
    blob = list(pal) + [0] * (768 - len(pal))
    im.putpalette(blob)
    im.putdata([grid[y][x] for y in range(len(grid)) for x in range(len(grid[0]))])
    return im


def stamp(dst, src, sx, sy, sw, sh, dx, dy):
    for j in range(sh):
        for i in range(sw):
            v = src[sy + j][sx + i]
            if not v:
                continue
            x, y = dx + i, dy + j
            if 0 <= x < W and 0 <= y < H:
                dst[y][x] = v


def clear(g, x0, y0, x1, y1):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            g[y][x] = 0


def line(g, x0, y0, x1, y1, c, rad=2):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i // n
        y = y0 + (y1 - y0) * i // n
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < W and 0 <= yy < H and yy < 63:
                    if dx * dx + dy * dy <= rad * rad:
                        if g[yy][xx] == 0:
                            g[yy][xx] = c


def foot_y(g) -> int:
    for y in range(H - 1, -1, -1):
        if any(g[y]):
            return y
    return H - 1


def planted(g) -> bool:
    return foot_y(g) >= 62


def hero_walk(base):
    # boot stamps from rest pose
    # L: (3,52) 16x12  R: (28,51) 18x13
    pants, boot = 10, 12
    frames = []

    def body(rest=True):
        g = copy_grid(base)
        clear(g, 0, 36, W, H)
        # keep a hip cap from original
        for y in range(36, 40):
            for x in range(W):
                g[y][x] = base[y][x]
        return g

    # F0 contact R (original legs)
    f0 = copy_grid(base)
    frames.append(f0)

    # F1 pass: lift back (left) boot forward/up, right stays
    f1 = body()
    stamp(f1, base, 28, 51, 18, 13, 28, 51)  # right plant
    stamp(f1, base, 3, 52, 16, 12, 8, 48)  # left passing
    line(f1, 18, 38, 14, 52, pants, 4)
    line(f1, 26, 38, 34, 51, pants, 4)
    line(f1, 18, 38, 14, 52, OUTLINE, 1)
    line(f1, 26, 38, 34, 51, OUTLINE, 1)
    frames.append(f1)

    # F2 opposite contact: left forward, right back
    f2 = body()
    stamp(f2, base, 3, 52, 16, 12, 28, 51)  # left boot now forward plant
    stamp(f2, base, 28, 51, 18, 13, 2, 51)  # right boot back plant
    line(f2, 20, 38, 34, 51, pants, 4)
    line(f2, 24, 38, 12, 51, pants, 4)
    line(f2, 20, 38, 34, 51, OUTLINE, 1)
    line(f2, 24, 38, 12, 51, OUTLINE, 1)
    frames.append(f2)

    # F3 pass: lift the back (right, now at left) up
    f3 = body()
    stamp(f3, base, 3, 52, 16, 12, 28, 51)  # left plant forward
    stamp(f3, base, 28, 51, 18, 13, 6, 48)  # right passing
    line(f3, 20, 38, 34, 51, pants, 4)
    line(f3, 22, 38, 14, 52, pants, 4)
    line(f3, 20, 38, 34, 51, OUTLINE, 1)
    line(f3, 22, 38, 14, 52, OUTLINE, 1)
    frames.append(f3)
    return frames


def thug_walk(base):
    shorts = 9
    frames = []

    def body():
        g = copy_grid(base)
        clear(g, 0, 42, W, H)
        for y in range(42, 46):
            for x in range(W):
                g[y][x] = base[y][x]
        return g

    frames.append(copy_grid(base))

    f1 = body()
    stamp(f1, base, 28, 52, 17, 12, 28, 52)
    stamp(f1, base, 4, 52, 16, 12, 8, 48)
    line(f1, 16, 44, 14, 52, shorts, 5)
    line(f1, 30, 44, 34, 52, shorts, 5)
    frames.append(f1)

    f2 = body()
    stamp(f2, base, 4, 52, 16, 12, 28, 51)
    stamp(f2, base, 28, 52, 17, 12, 3, 51)
    line(f2, 18, 44, 34, 52, shorts, 5)
    line(f2, 28, 44, 12, 52, shorts, 5)
    frames.append(f2)

    f3 = body()
    stamp(f3, base, 4, 52, 16, 12, 28, 51)
    stamp(f3, base, 28, 52, 17, 12, 6, 48)
    line(f3, 18, 44, 34, 52, shorts, 5)
    line(f3, 24, 44, 14, 52, shorts, 5)
    frames.append(f3)
    return frames


def sheet(idle_frames, walk_frames, pal) -> Image.Image:
    im = Image.new("P", (W * N, H * 2))
    blob = list(pal) + [0] * (768 - len(pal))
    im.putpalette(blob)
    for i, g in enumerate(idle_frames):
        im.paste(to_im(g, pal), (i * W, 0))
    for i, g in enumerate(walk_frames):
        im.paste(to_im(g, pal), (i * W, H))
    return im


def gif(frames, pal, path: Path, scale=4):
    imgs = [
        to_im(g, pal).convert("RGB").resize((W * scale, H * scale), Image.NEAREST)
        for g in frames
    ]
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=120, loop=0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hg, hpal = load_p(RES / "hero_48x64.png")
    tg, tpal = load_p(RES / "thug_48x64.png")
    h0 = cell0(hg)
    t0 = cell0(tg)

    # idle already in row of current strip
    idle_h = [ [row[i * W:(i + 1) * W] for row in hg] for i in range(N) ]
    idle_t = [ [row[i * W:(i + 1) * W] for row in tg] for i in range(N) ]
    if len(hg[0]) == W:
        idle_h = [h0] * N
        idle_t = [t0] * N

    hw = hero_walk(h0)
    tw = thug_walk(t0)

    for i, g in enumerate(hw):
        if not planted(g):
            raise SystemExit(f"hero walk frame {i} lost ground contact fy={foot_y(g)}")
    for i, g in enumerate(tw):
        if not planted(g):
            raise SystemExit(f"thug walk frame {i} lost ground contact fy={foot_y(g)}")

    hs = sheet(idle_h, hw, hpal)
    ts = sheet(idle_t, tw, tpal)
    hs.save(OUT / "hero_idle_walk_sheet.png")
    ts.save(OUT / "thug_idle_walk_sheet.png")
    hs.save(RES / "hero_48x64.png")
    ts.save(RES / "thug_48x64.png")
    gif(hw, hpal, OUT / "hero_walk.gif")
    gif(tw, tpal, OUT / "thug_walk.gif")
    hs.convert("RGB").resize((W * N * 3, H * 2 * 3), Image.NEAREST).save(OUT / "hero_sheet_3x.png")
    ts.convert("RGB").resize((W * N * 3, H * 2 * 3), Image.NEAREST).save(OUT / "thug_sheet_3x.png")

    report = {
        "asset_kind": "animation_strip",
        "actions": ["idle_guard_breathing", "walk_34_inplace"],
        "sheet": [W * N, H * 2],
        "cell": [W, H],
        "anims": 2,
        "frames_per_anim": N,
        "time_vblank": 12,
        "source_motion": [
            "data/source_art/motion/hero_walk_source.mp4",
            "data/source_art/motion/thug_walk_source.mp4",
        ],
        "pixel_route": "locked_48x64_gait_stamps_not_video_downscale",
        "walk_phases": ["contact_R", "pass_L", "contact_L", "pass_R"],
        "pivot": {"role": "foot_plant", "y": 63},
        "not_aaa_claim": True,
    }
    (DOC / "walk_strip_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
