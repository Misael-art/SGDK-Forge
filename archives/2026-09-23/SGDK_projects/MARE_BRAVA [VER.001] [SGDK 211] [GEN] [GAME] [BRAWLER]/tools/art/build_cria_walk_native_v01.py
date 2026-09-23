#!/usr/bin/env python3
"""Native 48x64 CRIA walk, 4 gait phases on the locked idle identity.

Imagine walk-in-place video is motion reference only. Harvest lifted both
feet (run/air); native walk keeps one flip-flop planted and a ~4px pass.
Phases: contact_L / pass_R / contact_R / pass_L. Facing left, no H-flip.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cria_idle", HERE / "build_cria_idle_native_v01.py")
idle = importlib.util.module_from_spec(spec)
sys.modules["cria_idle"] = idle
spec.loader.exec_module(idle)

W, H = idle.W, idle.H
N = 4
PAL = idle.PAL
I_OUT = idle.I_OUT
I_SK_HI, I_SK, I_SK_SH = idle.I_SK_HI, idle.I_SK, idle.I_SK_SH
I_TK_HI, I_TK, I_TK_SH = idle.I_TK_HI, idle.I_TK, idle.I_TK_SH
I_SH_HI, I_SH, I_SH_SH = idle.I_SH_HI, idle.I_SH, idle.I_SH_SH
I_RED, I_HAIR, I_FF, I_STR, I_EYE = (
    idle.I_RED,
    idle.I_HAIR,
    idle.I_FF,
    idle.I_STR,
    idle.I_EYE,
)

ROOT = idle.ROOT
RES = idle.RES
PROC = idle.PROC
DOC = idle.DOC
MOTION = idle.MOTION
PASS_LIFT = 4  # px; F-R2 lesson: not 8


def flop(c, x0: int, sole_y: int) -> None:
    idle.stamp(
        c,
        idle.raster(
            polygons=[[(x0, sole_y - 2), (x0 + 11, sole_y - 2), (x0 + 11, sole_y), (x0 - 1, sole_y)]]
        ),
        I_FF,
    )
    idle.paint(
        c,
        [(x0 + 3, sole_y - 2), (x0 + 4, sole_y - 2), (x0 + 5, sole_y - 3)],
        I_STR,
    )


def head_cap(c) -> None:
    idle.stamp(c, idle.raster(polygons=[[(17, 16), (23, 16), (23, 21), (16, 21)]]), I_SK)
    idle.stamp(c, idle.raster(ellipses=[(12, 6, 26, 20)]), I_SK)
    idle.paint(c, [(15, 10), (16, 11), (17, 12), (14, 13)], I_SK_HI)
    idle.paint(c, [(21, 14), (22, 15), (20, 16)], I_SK_SH)
    idle.stamp(c, idle.raster(polygons=[[(14, 13), (24, 12), (25, 17), (15, 18)]]), I_HAIR)
    idle.stamp(
        c,
        idle.raster(polygons=[[(12, 5), (24, 4), (26, 8), (25, 13), (13, 14), (11, 9)]]),
        I_TK,
    )
    idle.paint(c, [(14, 6), (15, 6), (16, 7), (17, 6), (18, 7)], I_TK_HI)
    idle.stamp(c, idle.raster(polygons=[[(23, 7), (30, 8), (29, 12), (22, 11)]]), I_RED)
    idle.paint(c, [(24, 9), (25, 10)], I_TK_SH)
    idle.ink(c, [(13, 10), (15, 10), (16, 10), (17, 10)])
    idle.paint(c, [(13, 12), (14, 12), (15, 12)], I_EYE)
    idle.ink(c, [(13, 12)])
    idle.ink(c, [(12, 13), (13, 14), (14, 15)])
    idle.ink(c, [(13, 17), (15, 17), (16, 17)])


def torso(c, dx: int) -> None:
    idle.stamp(
        c,
        idle.raster(
            polygons=[
                [
                    (15 + dx, 19),
                    (27 + dx, 20),
                    (29 + dx, 26),
                    (28 + dx, 34),
                    (17 + dx, 35),
                    (13 + dx, 28),
                    (13 + dx, 22),
                ]
            ]
        ),
        I_TK,
    )
    idle.paint(
        c,
        [(16 + dx, 21), (17 + dx, 22), (18 + dx, 23), (19 + dx, 22), (20 + dx, 21)],
        I_TK_HI,
    )
    idle.paint(c, [(25 + dx, 27), (26 + dx, 28), (27 + dx, 30), (15 + dx, 30)], I_TK_SH)
    idle.paint(
        c,
        [(21 + dx, 26), (22 + dx, 26), (23 + dx, 26), (22 + dx, 27), (21 + dx, 27)],
        I_RED,
    )
    idle.paint(c, [(15 + dx, 20), (16 + dx, 21), (26 + dx, 22)], I_SK_HI)


def shorts(c, dx: int) -> None:
    idle.stamp(
        c,
        idle.raster(
            polygons=[
                [
                    (16 + dx, 33),
                    (31 + dx, 33),
                    (34 + dx, 38),
                    (33 + dx, 47),
                    (24 + dx, 48),
                    (16 + dx, 47),
                    (14 + dx, 39),
                ]
            ]
        ),
        I_SH,
    )
    idle.paint(c, [(17 + dx, 35), (18 + dx, 36), (30 + dx, 35), (31 + dx, 36)], I_SH_HI)
    idle.paint(c, [(22 + dx, 40), (23 + dx, 41), (24 + dx, 42), (20 + dx, 45), (28 + dx, 45)], I_SH_SH)
    idle.stamp(c, idle.raster(polygons=[[(14 + dx, 46), (22 + dx, 46), (22 + dx, 49), (14 + dx, 49)]]), I_SH_HI)
    idle.stamp(c, idle.raster(polygons=[[(26 + dx, 46), (34 + dx, 46), (34 + dx, 49), (26 + dx, 49)]]), I_SH_HI)


def arm_near(c, fist_x: int, fist_y: int) -> None:
    idle.stamp(c, idle.limb(15, 20, 12, 30, 3), I_SK)
    idle.stamp(c, idle.limb(12, 30, fist_x, fist_y, 3), I_SK)
    idle.paint(c, [(12, 25), (fist_x, fist_y - 3)], I_SK_SH)
    idle.stamp(c, idle.raster(ellipses=[(fist_x - 3, fist_y - 3, fist_x + 3, fist_y + 3)]), I_SK)


def arm_far(c, fist_x: int, fist_y: int) -> None:
    idle.stamp(c, idle.limb(27, 21, 32, 30, 3), I_SK)
    idle.stamp(c, idle.limb(32, 30, fist_x, fist_y, 3), I_SK)
    idle.paint(c, [(31, 27), (fist_x, fist_y - 3)], I_SK_SH)
    idle.paint(c, [(fist_x - 1, fist_y - 4), (fist_x, fist_y - 4), (fist_x + 1, fist_y - 4)], I_RED)


def legs(c, lead_hip: int, lead_x: int, trail_hip: int, trail_x: int, trail_lift: int) -> None:
    """Lead foot toward travel (left of cell). Trailing may lift PASS_LIFT px."""
    lead_sole = 60
    trail_sole = 60 - trail_lift
    lead_knee_x = (lead_hip + lead_x + 4) // 2
    trail_knee_x = (trail_hip + trail_x + 5) // 2
    lead_knee_y = 48 if trail_lift == 0 else 47
    trail_knee_y = 48 - trail_lift // 2

    idle.stamp(c, idle.limb(trail_hip, 38, trail_knee_x, trail_knee_y, 4), I_SK)
    idle.stamp(c, idle.limb(trail_knee_x, trail_knee_y, trail_x + 6, trail_sole - 2, 3), I_SK)
    idle.paint(c, [(trail_knee_x + 1, trail_knee_y - 2), (trail_x + 7, trail_sole - 6)], I_SK_SH)

    idle.stamp(c, idle.limb(lead_hip, 37, lead_knee_x, lead_knee_y, 4), I_SK)
    idle.stamp(c, idle.limb(lead_knee_x, lead_knee_y, lead_x + 5, lead_sole - 2, 3), I_SK)
    idle.paint(c, [(lead_knee_x - 1, lead_knee_y - 2), (lead_x + 4, lead_sole - 6)], I_SK_SH)

    flop(c, trail_x, trail_sole)
    flop(c, lead_x, lead_sole)


def build_frame(phase: int):
    """
    0 contact_L  lead L planted, trail R planted
    1 pass_R     lead L planted, trail R passing
    2 contact_R  lead R planted (now in front), trail L planted
    3 pass_L     lead R planted, trail L passing
    """
    c = idle.empty()
    hip_l, hip_r = 20, 28
    if phase == 0:
        legs(c, hip_l, 8, hip_r, 26, 0)
        shorts(c, 0)
        torso(c, 0)
        arm_far(c, 31, 40)
        arm_near(c, 8, 36)
        head_cap(c)
    elif phase == 1:
        legs(c, hip_l, 10, hip_r, 18, PASS_LIFT)
        shorts(c, -1)
        torso(c, -1)
        arm_far(c, 33, 36)
        arm_near(c, 7, 34)
        head_cap(c)
    elif phase == 2:
        legs(c, hip_r, 8, hip_l, 26, 0)
        shorts(c, 0)
        torso(c, 0)
        arm_far(c, 28, 30)
        arm_near(c, 11, 42)
        head_cap(c)
    else:
        legs(c, hip_r, 10, hip_l, 18, PASS_LIFT)
        shorts(c, 0)
        torso(c, 0)
        arm_far(c, 30, 32)
        arm_near(c, 9, 40)
        head_cap(c)
    return c


def planted_count(grid) -> int:
    """How many distinct foot masses touch y>=59."""
    xs = [x for x in range(W) if grid[59][x] or grid[60][x]]
    if not xs:
        return 0
    xs.sort()
    groups = 1
    for i in range(1, len(xs)):
        if xs[i] > xs[i - 1] + 3:
            groups += 1
    return groups


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

    res_path = RES / "cria_walk_lean_48x64_v01.png"
    proc_path = PROC / "animation" / "cria_walk_lean_48x64_v01.png"
    gif_path = MOTION / "cria_walk.gif"
    sheet2_path = MOTION / "cria_walk_2x.png"
    contact_path = PROC / "review" / "cria_walk_contact_native_v01.png"

    idle.write_png(sheet, res_path)
    idle.write_png(sheet, proc_path)

    preview = [idle.to_im(g).convert("RGB").resize((W * 4, H * 4), Image.NEAREST) for g in frames]
    preview[0].save(
        gif_path,
        save_all=True,
        append_images=preview[1:],
        duration=[100, 80, 100, 80],
        loop=0,
        disposal=2,
    )
    idle.write_png(sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).convert("RGB"), sheet2_path)

    contact = Image.new("RGB", (W * N * 2, H * 2), (40, 40, 40))
    for i, g in enumerate(frames):
        contact.paste(idle.to_im(g).convert("RGB").resize((W * 2, H * 2), Image.NEAREST), (i * W * 2, 0))
    idle.write_png(contact, contact_path)

    boxes = [idle.bbox(g) for g in frames]
    feet = [idle.foot_y(g) for g in frames]
    plants = [planted_count(g) for g in frames]
    report = {
        "asset_kind": "animation_strip",
        "action": "walk_34_rusher",
        "character": "cria",
        "cell": [W, H],
        "frames": N,
        "walk_phases": ["contact_L", "pass_R", "contact_R", "pass_L"],
        "timing_vblank": [5, 4, 5, 4],
        "pivot": {"x": 24, "y": 60, "role": "foot_plant"},
        "facing": "left_opponent",
        "pass_lift_px": PASS_LIFT,
        "pixel_route": "locked_48x64_not_video_downscale",
        "source_construction": [
            "data/source_art/concept/cria_identity_model_sheet/cria_walk_construction_34_v01.png"
        ],
        "source_motion_ref_only": "data/source_art/motion/cria_walk_source.mp4",
        "video_drift": "harvest_airborne_both_feet_refused_as_pixel_source",
        "must_preserve": [
            "forward_lean",
            "backwards_cap_red_visor",
            "pointy_elbows",
            "one_flipflop_planted",
            "red_star_and_wrist",
            "wiry_thin_mass",
        ],
        "bbox": [list(b) if b else None for b in boxes],
        "foot_y": feet,
        "planted_groups_y59": plants,
        "palette_slot": "PAL3_enemy_roster",
        "not_aaa_claim": True,
        "res": str(res_path.relative_to(ROOT)),
    }
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / "cria_walk_native_v01_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if min(feet) < 59:
        raise SystemExit("walk lost ground contact")


if __name__ == "__main__":
    main()
