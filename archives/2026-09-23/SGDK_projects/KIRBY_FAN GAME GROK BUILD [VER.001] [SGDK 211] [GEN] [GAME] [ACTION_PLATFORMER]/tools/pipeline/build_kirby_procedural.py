#!/usr/bin/env python3
"""Procedural Kirby sheet: 8×32 frames with spherical volume (R2-G5).

Frames (match kirby.c):
  0 idle | 1-4 run | 5 jump | 6 floatA | 7 floatB/inhale

Shading: highlight(1) mid(2) base(3) core-shadow(4) deep(5) outline(6)
         feet(7/8) eyes(9) eye-white(10) + edge bounce light.

Usage:
  python3 tools/pipeline/build_kirby_procedural.py --install
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "source_art" / "ai_quantized" / "r6_kirby"

PAL2 = [
    (255, 0, 255),  # 0 KEY
    (255, 219, 255),  # 1 highlight
    (255, 182, 219),  # 2 light
    (255, 146, 182),  # 3 base
    (219, 73, 146),  # 4 core shadow
    (146, 36, 109),  # 5 deep
    (109, 36, 73),  # 6 outline
    (219, 73, 73),  # 7 foot light
    (146, 36, 36),  # 8 foot dark
    (36, 36, 73),  # 9 eye
    (255, 255, 255),  # 10 eye white / shine
    (146, 146, 146),
    (255, 146, 182),
    (255, 219, 146),
    (182, 109, 219),
    (109, 219, 219),
]


def to_indexed(indices: np.ndarray) -> Image.Image:
    im = Image.fromarray(indices.astype(np.uint8), mode="P")
    flat: list[int] = []
    for c in PAL2:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - 16))
    im.putpalette(flat[:768])
    return im


def _sphere_shade(nx: float, ny: float, nz: float) -> int:
    """Map unit sphere normal → PAL2 pink ramp with bounce light."""
    # Key light from upper-left
    lx, ly, lz = -0.45, -0.55, 0.70
    L = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / L, ly / L, lz / L
    ndotl = max(0.0, nx * lx + ny * ly + nz * lz)
    # rim / bounce from lower-right
    bx, by, bz = 0.55, 0.35, 0.25
    B = math.sqrt(bx * bx + by * by + bz * bz)
    bounce = max(0.0, nx * (bx / B) + ny * (by / B) + nz * (bz / B)) * 0.25
    v = ndotl + bounce
    if v > 0.88:
        return 1
    if v > 0.62:
        return 2
    if v > 0.38:
        return 3
    if v > 0.18:
        return 4
    return 5


def draw_body(
    idx: np.ndarray,
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    squash: float = 1.0,
) -> None:
    ry = ry * squash
    for y in range(32):
        for x in range(32):
            dx = (x + 0.5 - cx) / rx
            dy = (y + 0.5 - cy) / ry
            r2 = dx * dx + dy * dy
            if r2 > 1.0:
                continue
            nz = math.sqrt(max(0.0, 1.0 - r2))
            # outline ring
            if r2 > 0.88:
                idx[y, x] = 6
            else:
                idx[y, x] = _sphere_shade(dx, dy, nz)
    # specular glint (upper-left)
    gx, gy = int(cx - rx * 0.35), int(cy - ry * 0.40)
    for oy in range(-1, 2):
        for ox in range(-1, 2):
            xx, yy = gx + ox, gy + oy
            if 0 <= xx < 32 and 0 <= yy < 32 and idx[yy, xx] in (1, 2, 3):
                if ox * ox + oy * oy <= 1:
                    idx[yy, xx] = 1 if (ox == 0 and oy == 0) else 10


def draw_eyes(idx: np.ndarray, cx: float, cy: float, blink: bool = False) -> None:
    # Two oval eyes
    for side, ox in ((-1, -4), (1, 4)):
        ex, ey = cx + ox, cy - 2
        if blink:
            for x in range(int(ex) - 2, int(ex) + 3):
                if 0 <= x < 32:
                    idx[int(ey), x] = 6
            continue
        for y in range(int(ey) - 4, int(ey) + 4):
            for x in range(int(ex) - 2, int(ex) + 3):
                if not (0 <= x < 32 and 0 <= y < 32):
                    continue
                dx = (x + 0.5 - ex) / 2.2
                dy = (y + 0.5 - ey) / 4.0
                if dx * dx + dy * dy <= 1.0:
                    idx[y, x] = 9
                    # white glint top
                    if dy < -0.2 and dx < 0.2:
                        idx[y, x] = 10
        # cheek blush: outer mid-face, soft (never under-eye bags)
        bx = int(ex + side * 3)
        by = int(ey + 5)
        for y in range(by - 1, by + 2):
            for x in range(bx - 1, bx + 2):
                if 0 <= x < 32 and 0 <= y < 32 and idx[y, x] in (2, 3):
                    if abs(x - bx) + abs(y - by) <= 1:
                        idx[y, x] = 4


def draw_feet(
    idx: np.ndarray,
    cx: float,
    base_y: float,
    stride: float = 0.0,
    jump: bool = False,
) -> None:
    # Two oval feet; stride shifts left/right
    for i, side in enumerate((-1, 1)):
        fx = cx + side * (5.0 + stride * side * 0.5)
        fy = base_y + (1.5 if jump else 0.0) + (stride * 0.4 if i == 0 else -stride * 0.4)
        rw, rh = 5.0, 3.2 if not jump else 2.8
        for y in range(32):
            for x in range(32):
                dx = (x + 0.5 - fx) / rw
                dy = (y + 0.5 - fy) / rh
                if dx * dx + dy * dy <= 1.0:
                    # top of foot lighter, bottom darker
                    idx[y, x] = 7 if dy < 0.15 else 8
                elif 0.9 < dx * dx + dy * dy < 1.15 and abs(dx) < 1.1:
                    if idx[y, x] == 0:
                        idx[y, x] = 6


def draw_arms(
    idx: np.ndarray,
    cx: float,
    cy: float,
    pose: str,
    t: float,
) -> None:
    """Small arm stubs; pose: idle/run/jump/float/inhale."""
    for side in (-1, 1):
        if pose == "run":
            ay = cy + 2 + side * math.sin(t * math.pi) * 3
            ax = cx + side * 11
        elif pose == "jump":
            ax, ay = cx + side * 10, cy - 2
        elif pose == "float":
            ax, ay = cx + side * 12, cy - 1 + side * 1
        elif pose == "inhale":
            ax, ay = cx + side * 9, cy + 1
        else:
            ax, ay = cx + side * 11, cy + 2
        for y in range(int(ay) - 3, int(ay) + 4):
            for x in range(int(ax) - 3, int(ax) + 4):
                if not (0 <= x < 32 and 0 <= y < 32):
                    continue
                dx = (x + 0.5 - ax) / 3.2
                dy = (y + 0.5 - ay) / 3.2
                r2 = dx * dx + dy * dy
                if r2 <= 1.0:
                    if r2 > 0.75:
                        idx[y, x] = 6
                    else:
                        idx[y, x] = _sphere_shade(dx * side, dy, math.sqrt(max(0, 1 - r2)))


def frame_idle() -> np.ndarray:
    idx = np.zeros((32, 32), dtype=np.uint8)
    draw_body(idx, 16, 15, 11.5, 11.0)
    draw_eyes(idx, 16, 13)
    draw_arms(idx, 16, 16, "idle", 0)
    draw_feet(idx, 16, 26.5, 0)
    return idx


def frame_run(phase: int) -> np.ndarray:
    """phase 0..3 of run cycle."""
    idx = np.zeros((32, 32), dtype=np.uint8)
    # bob
    bob = (0, -1, 0, 1)[phase]
    squash = (1.0, 0.92, 1.0, 0.96)[phase]
    stride = (-3.0, -1.0, 3.0, 1.0)[phase]
    draw_body(idx, 16, 15 + bob, 11.5, 11.0, squash=squash)
    draw_eyes(idx, 16, 13 + bob)
    draw_arms(idx, 16, 16 + bob, "run", phase / 4.0)
    draw_feet(idx, 16, 26.5 + bob * 0.3, stride=stride)
    return idx


def frame_jump() -> np.ndarray:
    idx = np.zeros((32, 32), dtype=np.uint8)
    draw_body(idx, 16, 14, 11.0, 11.5, squash=0.95)
    draw_eyes(idx, 16, 12)
    draw_arms(idx, 16, 14, "jump", 0)
    draw_feet(idx, 16, 25.5, jump=True)
    return idx


def frame_float(phase: int) -> np.ndarray:
    idx = np.zeros((32, 32), dtype=np.uint8)
    # puffed — larger body
    scale = 1.08 if phase == 0 else 1.12
    draw_body(idx, 16, 15, 11.5 * scale, 11.5 * scale)
    draw_eyes(idx, 16, 13, blink=(phase == 1))
    draw_arms(idx, 16, 16, "float", phase)
    # no feet visible / tucked
    return idx


def frame_inhale() -> np.ndarray:
    """Reuse floatB slot visually distinct: open mouth suck."""
    idx = np.zeros((32, 32), dtype=np.uint8)
    draw_body(idx, 16, 15, 12.0, 11.5)
    draw_eyes(idx, 16, 12)
    # open mouth (dark oval)
    for y in range(18, 24):
        for x in range(13, 20):
            dx = (x - 16) / 3.5
            dy = (y - 20.5) / 2.5
            if dx * dx + dy * dy <= 1.0:
                idx[y, x] = 5
            elif dx * dx + dy * dy <= 1.3:
                idx[y, x] = 6
    draw_arms(idx, 16, 16, "inhale", 0)
    draw_feet(idx, 16, 26.5, 0)
    return idx


def stamp_palette(indices: np.ndarray) -> np.ndarray:
    """Ensure all 16 indices appear once for absolute packing."""
    out = indices.copy()
    for i in range(16):
        out[0, i] = i
    return out


def build_sheet() -> tuple[Image.Image, dict]:
    frames = [
        frame_idle(),
        frame_run(0),
        frame_run(1),
        frame_run(2),
        frame_run(3),
        frame_jump(),
        frame_float(0),
        frame_inhale(),  # shares slot with floatB/inhale in anim table
    ]
    sheet = np.zeros((32, 256), dtype=np.uint8)
    reports = []
    for fi, fr in enumerate(frames):
        # clean edge: force outer ring transparent where still 0
        sheet[:, fi * 32 : (fi + 1) * 32] = fr
        center = fr[10:22, 10:22]
        rep = {
            "frame": fi,
            "opaque_pct": float((fr > 0).mean() * 100),
            "idx0_center_pct": float((center == 0).mean() * 100),
            "unique": [int(x) for x in np.unique(fr)],
        }
        rep["gate"] = (
            "PASS"
            if rep["idx0_center_pct"] < 5.0 and rep["opaque_pct"] > 35.0
            else "FAIL"
        )
        reports.append(rep)
    # stamp full palette on first pixels of sheet corners (not center)
    for i in range(16):
        sheet[0, i] = i
        sheet[31, 240 + i] = i
    all_pass = all(r["gate"] == "PASS" for r in reports)
    return to_indexed(sheet), {"all_pass": all_pass, "frames": reports}


def build_particle_pal2() -> Image.Image:
    """3×8 dust frames using PAL2 greys/pinks that read as dust on PAL2 CRAM.

    Also authored so PAL1 dirt path works if scene uses PAL1.
    Indices: 11 grey, 6 dark outline, 4 soft pink-dust, 10 white highlight.
    """
    # Use absolute PAL2 table
    sheet = np.zeros((8, 24), dtype=np.uint8)
    # Frame 0 tight
    specs = (
        (4, 3, [(0, 0, 4), (1, 0, 11), (0, 1, 11), (-1, 0, 6), (0, -1, 6)]),
        (12, 4, [
            (0, 0, 11), (1, 0, 4), (-1, 0, 4), (0, 1, 4), (0, -1, 11),
            (2, 1, 6), (-2, 0, 6), (1, -2, 6), (-1, 2, 11),
        ]),
        (20, 4, [
            (-3, -2, 11), (3, -1, 11), (-2, 2, 6), (2, 2, 6),
            (0, -3, 4), (0, 3, 6), (4, 0, 11), (-4, 1, 6),
        ]),
    )
    for cx, _r, dots in specs:
        for dx, dy, col in dots:
            x, y = cx + dx, 4 + dy
            if 0 <= x < 24 and 0 <= y < 8:
                sheet[y, x] = col
    # fuller circles for f0/f1
    for f, (cx, rad) in enumerate(((4, 2), (12, 3))):
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if dx * dx + dy * dy <= rad * rad:
                    x, y = cx + dx, 4 + dy
                    if 0 <= x < 24 and 0 <= y < 8:
                        d2 = dx * dx + dy * dy
                        if d2 <= 1:
                            sheet[y, x] = 11
                        elif d2 <= 4:
                            sheet[y, x] = 4
                        else:
                            sheet[y, x] = 6
    for i in range(16):
        sheet[0, min(23, i)] = i
    return to_indexed(sheet)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    im, report = build_sheet()
    path = OUT / "kirby_sheet_r6.png"
    im.save(path)
    im.resize((1024, 128), Image.Resampling.NEAREST).save(OUT / "kirby_sheet_r6_x4.png")
    (OUT / "kirby_r6_gate.json").write_text(json.dumps(report, indent=2) + "\n")
    for r in report["frames"]:
        print(
            f"frame{r['frame']}: opaque={r['opaque_pct']:.1f}% "
            f"center_idx0={r['idx0_center_pct']:.1f}% uniq={r['unique']} {r['gate']}"
        )
    print("ALL", report["all_pass"])

    part = build_particle_pal2()
    part.save(OUT / "ph_particle_r6.png")
    print("particle", part.size)

    if args.install:
        if not report["all_pass"]:
            print("REFUSED kirby install")
            return 1
        spr = ROOT / "res" / "sprites"
        bak = spr / "ph_kirby_pre_r6_backup.png"
        dst = spr / "ph_kirby.png"
        if dst.exists() and not bak.exists():
            bak.write_bytes(dst.read_bytes())
        im.save(dst)
        im.save(spr / "kirby_r6_candidate.png")
        pbak = spr / "ph_particle_pre_r6_backup.png"
        pdst = spr / "ph_particle.png"
        if pdst.exists() and not pbak.exists():
            pbak.write_bytes(pdst.read_bytes())
        part.save(pdst)
        print("INSTALLED ph_kirby.png + ph_particle.png")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
