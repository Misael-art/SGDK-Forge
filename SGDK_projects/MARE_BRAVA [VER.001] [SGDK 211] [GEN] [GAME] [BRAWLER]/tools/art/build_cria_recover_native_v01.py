#!/usr/bin/env python3
"""Native 48x64 CRIA recover: armed fist recoils after haymaker hitstop.

Imagine video is motion reference only. Harvest started as a recoil then
drifted into a walk (head up, stride). Native recover keeps both flip-flops
planted and the wristband on the armed arm as it travels back from the
left edge toward the chest / rear hang.
Facing left, no H-flip.
Phases: follow / retract / settle / hold. Times 4-5-6-8.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "cria_hit", HERE / "build_cria_hit_native_v01.py"
)
hit = importlib.util.module_from_spec(spec)
sys.modules["cria_hit"] = hit
spec.loader.exec_module(hit)

walk = hit.walk
idle = walk.idle
W, H = walk.W, walk.H
N = 4
PAL = walk.PAL
I_SK = walk.I_SK
I_RED = walk.I_RED
ROOT, RES, PROC, DOC, MOTION = walk.ROOT, walk.RES, walk.PROC, walk.DOC, walk.MOTION
HIP_L, HIP_R = 20, 28


def build_frame(phase: int):
    """
    0 follow   fist leaves hitstop, still left of the chest
    1 retract  fist at the chest (construction pose)
    2 settle   fist dropping, lean easing
    3 hold     armed arm hanging rear-ish, readable unload not idle
    """
    c = idle.empty()
    lean = [-2, -1, 0, 0][phase]
    fist = [(10, 20), (16, 22), (20, 30), (28, 38)][phase]
    walk.legs(c, HIP_L, 8, HIP_R, 26, 0)
    walk.shorts(c, lean)
    walk.torso(c, lean)
    if phase < 3:
        hit.arm_counter(c, [30, 26, 14][phase], [36, 38, 40][phase], False)
        walk.head_cap(c)
        hit.arm_armed(c, fist[0], fist[1])
    else:
        hit.arm_armed(c, fist[0], fist[1])
        hit.arm_counter(c, 10, 40, False)
        walk.head_cap(c)
    return c


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

    res_path = RES / "cria_recover_lean_48x64_v01.png"
    proc_path = PROC / "animation" / "cria_recover_lean_48x64_v01.png"
    gif_path = MOTION / "cria_recover.gif"
    sheet2_path = MOTION / "cria_recover_2x.png"
    contact_path = PROC / "review" / "cria_recover_contact_native_v01.png"

    idle.write_png(sheet, res_path)
    idle.write_png(sheet, proc_path)

    preview = [idle.to_im(g).convert("RGB").resize((W * 4, H * 4), Image.NEAREST) for g in frames]
    preview[0].save(
        gif_path,
        save_all=True,
        append_images=preview[1:],
        duration=[67, 83, 100, 133],
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
    plants = [hit.planted_count(g) for g in frames]
    report = {
        "asset_kind": "animation_strip",
        "action": "recover_after_haymaker",
        "character": "cria",
        "cell": [W, H],
        "frames": N,
        "phases": ["follow", "retract", "settle", "hold"],
        "timing_vblank": [4, 5, 6, 8],
        "chain": "APPROACH->TELEGRAPH->ATTACK->RECOVER",
        "pivot": {"x": 24, "y": 60, "role": "foot_plant"},
        "facing": "left_opponent",
        "pixel_route": "locked_48x64_not_video_downscale",
        "source_construction": [
            "data/source_art/concept/cria_identity_model_sheet/cria_recover_construction_34_v01.png",
            "data/source_art/concept/cria_identity_model_sheet/cria_hit_construction_34_v01.png",
        ],
        "source_motion_ref_only": "data/source_art/motion/cria_recover_source.mp4",
        "video_drift": "harvest_recoil_then_walk_stride_head_up_refused_as_pixel_source",
        "must_preserve": [
            "forward_lean_easing",
            "backwards_cap_red_visor",
            "armed_fist_recoils_left_to_chest",
            "wristband_on_armed_arm",
            "both_flipflops_planted",
            "red_star",
        ],
        "bbox": [list(b) if b else None for b in boxes],
        "foot_y": feet,
        "planted_groups_y59": plants,
        "fist_min_x": [hit.fist_min_x(g) for g in frames],
        "fist_max_x": [hit.fist_max_x(g) for g in frames],
        "palette_slot": "PAL3_enemy_roster",
        "not_aaa_claim": True,
        "res": str(res_path.relative_to(ROOT)),
    }
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / "cria_recover_native_v01_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if min(feet) < 59:
        raise SystemExit("recover lost ground contact")
    if min(plants) < 2:
        raise SystemExit("recover must keep both flip-flops planted")
    # Fist must travel rightward (recoil), not stay at hitstop.
    if hit.fist_min_x(frames[0]) >= hit.fist_min_x(frames[2]):
        raise SystemExit("recover fist did not recoil right of follow")
    if hit.fist_min_x(frames[0]) > 12:
        raise SystemExit("recover follow lost the left-side punch silhouette")


if __name__ == "__main__":
    main()
