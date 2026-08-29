#!/usr/bin/env python3
"""Native 48x64 CRIA telegraph: inclined rush wind-up, armed rear fist.

Contract: 12 VBlanks, cue 'corrida inclinada com braco armado'.
Imagine video is motion reference only. Wristband stays on the rear armed
arm (idle/walk identity); harvest swapped it to the front hand.
Both flip-flops planted. Facing left, no H-flip.
Phases: coil / load / peak / hold. Times 3-3-4-2.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cria_walk", HERE / "build_cria_walk_native_v01.py")
walk = importlib.util.module_from_spec(spec)
sys.modules["cria_walk"] = walk
spec.loader.exec_module(walk)

idle = walk.idle
W, H = walk.W, walk.H
N = 4
PAL = walk.PAL
I_SK = walk.I_SK
I_SK_SH = walk.I_SK_SH
I_RED = walk.I_RED
ROOT, RES, PROC, DOC, MOTION = walk.ROOT, walk.RES, walk.PROC, walk.DOC, walk.MOTION
HIP_L, HIP_R = 20, 28


def hand_reach(c, hx: int, hy: int) -> None:
    """Front reaching hand — telegraph warning, not a walk fist."""
    idle.stamp(c, idle.limb(15, 20, 11, 32, 3), I_SK)
    idle.stamp(c, idle.limb(11, 32, hx, hy, 2), I_SK)
    idle.paint(c, [(12, 25), (hx, hy - 2)], I_SK_SH)
    idle.stamp(
        c,
        idle.raster(
            pixels=[
                (hx, hy),
                (hx - 2, hy - 1),
                (hx - 3, hy),
                (hx - 2, hy + 2),
                (hx, hy + 2),
            ]
        ),
        I_SK,
    )


def build_frame(phase: int):
    """
    0 coil  stance, rear fist starts loading
    1 load  more lean, rear fist further back
    2 peak  extreme lean, armed rear fist, front hand reaching
    3 hold  peak held (readable threat)
    """
    c = idle.empty()
    lean = [0, -1, -2, -2][phase]
    far = [(32, 38), (36, 32), (39, 28), (39, 27)][phase]
    walk.legs(c, HIP_L, 8, HIP_R, 26, 0)
    walk.shorts(c, lean)
    walk.torso(c, lean)
    walk.arm_far(c, far[0], far[1])
    if phase == 0:
        walk.arm_near(c, 8, 38)
    else:
        hand_reach(c, 6 if phase == 1 else 5, 40 + phase)
    walk.head_cap(c)
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

    res_path = RES / "cria_telegraph_lean_48x64_v01.png"
    proc_path = PROC / "animation" / "cria_telegraph_lean_48x64_v01.png"
    gif_path = MOTION / "cria_telegraph.gif"
    sheet2_path = MOTION / "cria_telegraph_2x.png"
    contact_path = PROC / "review" / "cria_telegraph_contact_native_v01.png"

    idle.write_png(sheet, res_path)
    idle.write_png(sheet, proc_path)

    preview = [idle.to_im(g).convert("RGB").resize((W * 4, H * 4), Image.NEAREST) for g in frames]
    preview[0].save(
        gif_path,
        save_all=True,
        append_images=preview[1:],
        duration=[50, 50, 67, 33],
        loop=0,
        disposal=2,
    )
    idle.write_png(
        sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).convert("RGB"),
        sheet2_path,
    )
    contact = Image.new("RGB", (W * N * 2, H * 2), (40, 40, 40))
    for i, g in enumerate(frames):
        contact.paste(idle.to_im(g).convert("RGB").resize((W * 2, H * 2), Image.NEAREST), (i * W * 2, 0))
    idle.write_png(contact, contact_path)

    boxes = [idle.bbox(g) for g in frames]
    feet = [idle.foot_y(g) for g in frames]
    plants = [planted_count(g) for g in frames]
    report = {
        "asset_kind": "animation_strip",
        "action": "telegraph_rush_armed",
        "character": "cria",
        "cell": [W, H],
        "frames": N,
        "phases": ["coil", "load", "peak", "hold"],
        "timing_vblank": [3, 3, 4, 2],
        "telegraph_frames_contract": 12,
        "visual_cue": "corrida inclinada com braco armado",
        "pivot": {"x": 24, "y": 60, "role": "foot_plant"},
        "facing": "left_opponent",
        "pixel_route": "locked_48x64_not_video_downscale",
        "source_construction": [
            "data/source_art/concept/cria_identity_model_sheet/cria_telegraph_construction_34_v01.png"
        ],
        "source_motion_ref_only": "data/source_art/motion/cria_telegraph_source.mp4",
        "video_drift": "harvest_moved_wristband_to_front_arm_refused_as_pixel_source",
        "must_preserve": [
            "forward_lean",
            "backwards_cap_red_visor",
            "armed_rear_fist",
            "wristband_on_rear_arm",
            "both_flipflops_planted",
            "red_star",
        ],
        "bbox": [list(b) if b else None for b in boxes],
        "foot_y": feet,
        "planted_groups_y59": plants,
        "palette_slot": "PAL3_enemy_roster",
        "not_aaa_claim": True,
        "res": str(res_path.relative_to(ROOT)),
    }
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / "cria_telegraph_native_v01_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if min(feet) < 59:
        raise SystemExit("telegraph lost ground contact")
    if min(plants) < 2:
        raise SystemExit("telegraph must keep both flip-flops planted")


if __name__ == "__main__":
    main()
