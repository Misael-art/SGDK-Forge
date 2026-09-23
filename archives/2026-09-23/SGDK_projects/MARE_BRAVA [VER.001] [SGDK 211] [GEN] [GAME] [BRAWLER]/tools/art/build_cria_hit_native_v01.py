#!/usr/bin/env python3
"""Native 48x64 CRIA haymaker: armed rear fist fires left after telegraph.

Imagine video is motion reference only. Harvest punched with the FRONT
arm and left the wristband on the rear (same drift as telegraph). Native
keeps the wristband on the armed arm and travels that fist from the
telegraph cock (right of cell) across the torso to the left edge.
Both flip-flops planted. Facing left, no H-flip.
Phases: launch / active / hitstop / recover. Times 3-4-6-5.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "cria_telegraph", HERE / "build_cria_telegraph_native_v01.py"
)
tel = importlib.util.module_from_spec(spec)
sys.modules["cria_telegraph"] = tel
spec.loader.exec_module(tel)

walk = tel.walk
idle = walk.idle
W, H = walk.W, walk.H
N = 4
PAL = walk.PAL
I_SK = walk.I_SK
I_SK_HI = walk.I_SK_HI
I_SK_SH = walk.I_SK_SH
I_RED = walk.I_RED
ROOT, RES, PROC, DOC, MOTION = walk.ROOT, walk.RES, walk.PROC, walk.DOC, walk.MOTION
HIP_L, HIP_R = 20, 28


def stamp_over(c, mask, fill: int, ink: int = walk.I_OUT) -> None:
    """Punch arm sits in front of the tank; idle.stamp refuses occupied cells."""
    ol = idle.outline(mask)
    for y in range(H):
        for x in range(W):
            if ol[y][x]:
                c[y][x] = ink
            elif mask[y][x]:
                c[y][x] = fill


def arm_armed(c, fist_x: int, fist_y: int) -> None:
    """Wristband arm: rear shoulder to any fist. Wristband stays on this arm."""
    sx, sy = 26, 20
    if fist_x >= 26:
        ex, ey = 32, 28
    else:
        ex = (sx + fist_x) // 2 + 2
        ey = (sy + fist_y) // 2 + 3
    stamp_over(c, idle.limb(sx, sy, ex, ey, 3), I_SK)
    stamp_over(c, idle.limb(ex, ey, fist_x, fist_y, 3), I_SK)
    idle.paint(c, [(ex, ey), (fist_x, fist_y - 2)], I_SK_SH)
    stamp_over(
        c,
        idle.raster(ellipses=[(fist_x - 3, fist_y - 3, fist_x + 3, fist_y + 3)]),
        I_SK,
    )
    idle.paint(c, [(fist_x - 2, fist_y - 1), (fist_x - 1, fist_y)], I_SK_HI)
    # Wristband on the forearm, behind the knuckles (right of a leftward fist).
    bx = fist_x + (2 if fist_x < sx else -1)
    idle.paint(
        c,
        [
            (bx, fist_y - 1),
            (bx + 1, fist_y - 1),
            (bx, fist_y),
            (bx + 1, fist_y),
            (bx, fist_y + 1),
        ],
        I_RED,
    )


def arm_counter(c, hx: int, hy: int, reach: bool) -> None:
    """Non-punching arm: reach on launch, pull-back as counterweight after."""
    if reach:
        tel.hand_reach(c, hx, hy)
        return
    idle.stamp(c, idle.limb(15, 20, 18, 28, 3), I_SK)
    idle.stamp(c, idle.limb(18, 28, hx, hy, 3), I_SK)
    idle.paint(c, [(17, 24), (hx, hy - 2)], I_SK_SH)
    idle.stamp(c, idle.raster(ellipses=[(hx - 2, hy - 2, hx + 2, hy + 2)]), I_SK)


def build_frame(phase: int):
    """
    0 launch   armed fist leaves the telegraph cock, crossing the chest
    1 active   fist extends left toward Taina
    2 hitstop  max extension, freeze-readable
    3 recover  fist comes back, body unloads
    """
    c = idle.empty()
    lean = [-2, -3, -3, -1][phase]
    fist = [(16, 20), (8, 19), (4, 18), (14, 28)][phase]
    walk.legs(c, HIP_L, 8, HIP_R, 26, 0)
    walk.shorts(c, lean)
    walk.torso(c, lean)
    if phase == 0:
        arm_counter(c, 7, 40, True)
        walk.head_cap(c)
        arm_armed(c, fist[0], fist[1])
    else:
        arm_counter(c, [30, 32, 12][phase - 1], [36, 34, 38][phase - 1], False)
        walk.head_cap(c)
        arm_armed(c, fist[0], fist[1])
    return c


def planted_count(grid) -> int:
    xs = [x for x in range(W) if grid[59][x] or grid[60][x]]
    if not xs:
        return 0
    xs.sort()
    groups = 1
    for i in range(1, len(xs)):
        if xs[i] > xs[i - 1] + 3:
            groups += 1
    return groups


def fist_max_x(grid) -> int:
    """Rightmost skin/red pixel in the upper half — telegraph cock lives here."""
    mx = -1
    for y in range(0, 36):
        for x in range(W):
            if grid[y][x] in (I_SK, I_SK_HI, I_SK_SH, I_RED) and x > mx:
                mx = x
    return mx


def fist_min_x(grid) -> int:
    mn = W
    for y in range(0, 36):
        for x in range(W):
            if grid[y][x] in (I_SK, I_SK_HI, I_SK_SH, I_RED) and x < mn:
                mn = x
    return mn


def main() -> None:
    frames = [build_frame(i) for i in range(N)]
    sheet = Image.new("P", (W * N, H))
    blob = []
    for rgb in PAL:
        blob.extend(rgb)
    blob += [0] * (768 - len(blob))
    sheet.putpalette(blob)
    for i, g in enumerate(frames):
        sheet.paste(idle.to_im(g), (i * W, 0))

    res_path = RES / "cria_hit_lean_48x64_v01.png"
    proc_path = PROC / "animation" / "cria_hit_lean_48x64_v01.png"
    gif_path = MOTION / "cria_hit.gif"
    sheet2_path = MOTION / "cria_hit_2x.png"
    contact_path = PROC / "review" / "cria_hit_contact_native_v01.png"

    idle.write_png(sheet, res_path)
    idle.write_png(sheet, proc_path)

    preview = [idle.to_im(g).convert("RGB").resize((W * 4, H * 4), Image.NEAREST) for g in frames]
    preview[0].save(
        gif_path,
        save_all=True,
        append_images=preview[1:],
        duration=[50, 67, 100, 83],
        loop=0,
        disposal=2,
    )
    idle.write_png(
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).convert("RGB"),
        sheet2_path,
    )
    contact = Image.new("RGB", (W * N * 2, H * 2), (40, 40, 40))
    for i, g in enumerate(frames):
        contact.paste(
            idle.to_im(g).convert("RGB").resize((W * 2, H * 2), Image.NEAREST),
            (i * W * 2, 0),
        )
    idle.write_png(contact, contact_path)

    boxes = [idle.bbox(g) for g in frames]
    feet = [idle.foot_y(g) for g in frames]
    plants = [planted_count(g) for g in frames]
    report = {
        "asset_kind": "animation_strip",
        "action": "haymaker_armed_rear_fist",
        "character": "cria",
        "cell": [W, H],
        "frames": N,
        "phases": ["launch", "active", "hitstop", "recover"],
        "timing_vblank": [3, 4, 6, 5],
        "chain": "APPROACH->TELEGRAPH->ATTACK->RECOVER",
        "pivot": {"x": 24, "y": 60, "role": "foot_plant"},
        "facing": "left_opponent",
        "pixel_route": "locked_48x64_not_video_downscale",
        "source_construction": [
            "data/source_art/concept/cria_identity_model_sheet/cria_hit_construction_34_v01.png",
            "data/source_art/concept/cria_identity_model_sheet/cria_telegraph_construction_34_v01.png",
        ],
        "source_motion_ref_only": "data/source_art/motion/cria_hit_source.mp4",
        "video_drift": "harvest_punched_with_front_arm_wristband_stayed_rear_refused_as_pixel_source",
        "must_preserve": [
            "forward_lean",
            "backwards_cap_red_visor",
            "armed_fist_travels_right_to_left",
            "wristband_on_armed_arm",
            "both_flipflops_planted",
            "red_star",
        ],
        "bbox": [list(b) if b else None for b in boxes],
        "foot_y": feet,
        "planted_groups_y59": plants,
        "fist_min_x": [fist_min_x(g) for g in frames],
        "fist_max_x": [fist_max_x(g) for g in frames],
        "palette_slot": "PAL3_enemy_roster",
        "not_aaa_claim": True,
        "res": str(res_path.relative_to(ROOT)),
    }
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / "cria_hit_native_v01_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if min(feet) < 59:
        raise SystemExit("hit lost ground contact")
    if min(plants) < 2:
        raise SystemExit("hit must keep both flip-flops planted")
    # Active/hitstop must read further left than launch (travel, not a twitch).
    if fist_min_x(frames[2]) >= fist_min_x(frames[0]):
        raise SystemExit("haymaker did not travel left of launch")
    if fist_min_x(frames[2]) > 8:
        raise SystemExit("hitstop fist never reached the left of the cell")
    if any(b[0] <= 0 for b in boxes if b):
        raise SystemExit("haymaker clipped the left cell edge")


if __name__ == "__main__":
    main()
