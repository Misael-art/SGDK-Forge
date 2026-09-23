#!/usr/bin/env python3
"""Build native-grid P0 locomotion candidates for TAÍNA.

The builder deliberately starts from the human-approved idle v02 key pose,
never from the rejected v05/v06/v07 lineart or the obsolete 6x8 sheet.  The
head, torso, palette and costume anchors remain inherited from the approved
48x64 source; locomotion is redrawn as integer-pixel clusters.

Outputs remain in ``rascunho`` until visual review promotes them to ``res``.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT = Path(__file__).resolve().parents[2]
SOURCE = (
    PROJECT
    / "rascunho/taina_idle_guard_v02/"
    "taina_idle_guard_key_pose_clean_48x64_v02.png"
)
OUT = PROJECT / "rascunho/taina_p0_locomotion_v01"
REVIEW = PROJECT / "doc/art/characters/taina/review"
RES = PROJECT / "res/sprites/characters/taina"

TRANSPARENT = 0
OUTLINE = 1
PANTS_DARK = 2
PANTS_BASE = 3
WRAP_DARK = 4
SASH = 5
SKIN_DARK = 6
SKIN_BASE = 7
SKIN_LIGHT = 8
SKIN_HIGHLIGHT = 9


def indexed_canvas(size: tuple[int, int], source: Image.Image) -> Image.Image:
    image = Image.new("P", size, TRANSPARENT)
    image.putpalette(source.getpalette())
    image.info["transparency"] = TRANSPARENT
    return image


def paste_indexed(
    dst: Image.Image, src: Image.Image, xy: tuple[int, int] = (0, 0)
) -> None:
    mask = src.point(lambda value: 255 if value else 0, mode="L")
    dst.paste(src, xy, mask)


def polygon(
    draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], fill: int
) -> None:
    draw.polygon(points, fill=fill)


def line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    fill: int,
    width: int,
) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def clear_lower(frame: Image.Image, y: int = 28) -> None:
    ImageDraw.Draw(frame).rectangle((0, y, frame.width - 1, frame.height - 1), fill=0)


def draw_waist(draw: ImageDraw.ImageDraw, x_shift: int = 0, y_shift: int = 0) -> None:
    draw.rectangle(
        (22 + x_shift, 25 + y_shift, 27 + x_shift, 29 + y_shift),
        fill=OUTLINE,
    )
    draw.rectangle(
        (23 + x_shift, 25 + y_shift, 26 + x_shift, 28 + y_shift),
        fill=SKIN_DARK,
    )
    # Dark pelvis bridges torso, belt and both leg roots.  Keeping this mass
    # explicit prevents the "floating belt" artifact found in the first pass.
    polygon(
        draw,
        [
            (17 + x_shift, 27 + y_shift),
            (32 + x_shift, 27 + y_shift),
            (31 + x_shift, 35 + y_shift),
            (19 + x_shift, 35 + y_shift),
        ],
        OUTLINE,
    )
    polygon(
        draw,
        [
            (18 + x_shift, 29 + y_shift),
            (31 + x_shift, 29 + y_shift),
            (29 + x_shift, 34 + y_shift),
            (20 + x_shift, 34 + y_shift),
        ],
        PANTS_DARK,
    )
    polygon(
        draw,
        [
            (16 + x_shift, 27 + y_shift),
            (33 + x_shift, 27 + y_shift),
            (34 + x_shift, 30 + y_shift),
            (31 + x_shift, 32 + y_shift),
            (18 + x_shift, 32 + y_shift),
            (14 + x_shift, 30 + y_shift),
        ],
        OUTLINE,
    )
    polygon(
        draw,
        [
            (17 + x_shift, 28 + y_shift),
            (32 + x_shift, 28 + y_shift),
            (33 + x_shift, 30 + y_shift),
            (30 + x_shift, 31 + y_shift),
            (18 + x_shift, 31 + y_shift),
            (16 + x_shift, 30 + y_shift),
        ],
        SASH,
    )


def draw_baggy_leg(
    draw: ImageDraw.ImageDraw,
    hip: tuple[int, int],
    knee: tuple[int, int],
    ankle: tuple[int, int],
    foot_tip: tuple[int, int],
    near: bool,
    lifted: bool = False,
) -> None:
    """Draw one connected baggy trouser leg, wrap and bare foot."""

    thigh_outline = 12 if near else 11
    thigh_base = 9 if near else 8
    shin_outline = 9 if near else 8
    shin_base = 6 if near else 5
    line(draw, [hip, knee], OUTLINE, thigh_outline)
    line(draw, [hip, knee], PANTS_BASE, thigh_base)
    line(draw, [knee, ankle], OUTLINE, shin_outline)
    line(draw, [knee, ankle], PANTS_BASE, shin_base)

    # Cool interior shadow follows the rear/lower edge of the mass.
    shadow_points = [
        (hip[0] - 2, hip[1] + 1),
        (knee[0] - 2, knee[1] + 1),
        (ankle[0] - 1, ankle[1]),
    ]
    line(draw, shadow_points[:2], PANTS_DARK, 3)
    line(draw, shadow_points[1:], PANTS_DARK, 2)

    # Trouser cuff and wrapped shin remain connected to the ankle.
    cuff_y = ankle[1] - 6
    draw.rectangle(
        (ankle[0] - 4, cuff_y - 1, ankle[0] + 3, cuff_y + 2),
        fill=OUTLINE,
    )
    draw.rectangle(
        (ankle[0] - 3, cuff_y, ankle[0] + 2, cuff_y + 1),
        fill=PANTS_DARK,
    )
    line(
        draw,
        [(ankle[0], cuff_y + 2), (ankle[0], ankle[1] - 1)],
        OUTLINE,
        6,
    )
    line(
        draw,
        [(ankle[0], cuff_y + 3), (ankle[0], ankle[1] - 1)],
        WRAP_DARK,
        3,
    )

    # Bare foot: a short warm wedge. Lifted feet point slightly downward.
    heel = (ankle[0] - (2 if foot_tip[0] >= ankle[0] else -2), ankle[1])
    toe_y = foot_tip[1] if lifted else ankle[1]
    polygon(
        draw,
        [
            (heel[0] - 2, heel[1] - 2),
            (ankle[0] + 2, ankle[1] - 2),
            (foot_tip[0], toe_y - 1),
            (foot_tip[0] + (1 if foot_tip[0] >= ankle[0] else -1), toe_y + 1),
            (ankle[0] - 1, ankle[1] + 1),
        ],
        OUTLINE,
    )
    line(draw, [(ankle[0], ankle[1] - 1), (foot_tip[0], toe_y)], SKIN_DARK, 3)
    draw.point((foot_tip[0], toe_y - 1), fill=SKIN_LIGHT)


def make_walk(source: Image.Image) -> list[Image.Image]:
    # contact, down, passing, opposite contact, down, passing
    poses = [
        ((20, 32), (17, 44), (13, 59), (8, 60), (28, 32), (31, 45), (37, 57), (42, 58), False),
        ((20, 33), (18, 46), (15, 60), (10, 60), (28, 33), (29, 47), (33, 58), (37, 59), False),
        ((20, 32), (20, 45), (22, 60), (17, 60), (28, 32), (27, 44), (27, 55), (31, 57), True),
        ((20, 32), (17, 45), (12, 57), (7, 58), (28, 32), (31, 44), (36, 59), (42, 60), False),
        ((20, 33), (19, 47), (16, 58), (12, 59), (28, 33), (30, 46), (34, 60), (40, 60), False),
        ((20, 32), (21, 44), (21, 55), (17, 57), (28, 32), (28, 45), (27, 60), (33, 60), True),
    ]
    frames: list[Image.Image] = []
    for index, pose in enumerate(poses):
        frame = indexed_canvas((48, 64), source)
        # Alternate approved idle upper-body phases for a subtle shoulder beat.
        paste_indexed(frame, source, (0, 1 if index in (1, 4) else 0))
        clear_lower(frame)
        d = ImageDraw.Draw(frame)
        draw_waist(d, y_shift=1 if index in (1, 4) else 0)
        (
            lhip,
            lknee,
            lankle,
            lfoot,
            rhip,
            rknee,
            rankle,
            rfoot,
            lifted,
        ) = pose
        draw_baggy_leg(d, rhip, rknee, rankle, rfoot, near=False, lifted=lifted)
        draw_baggy_leg(d, lhip, lknee, lankle, lfoot, near=True, lifted=lifted)
        # Sash trails the hip direction one beat later.
        sash_dx = (-2, -1, 1, 2, 1, -1)[index]
        polygon(
            d,
            [(30, 29), (35, 31), (37 + sash_dx, 39), (34 + sash_dx, 44),
             (31, 39), (28, 33)],
            OUTLINE,
        )
        polygon(
            d,
            [(31, 30), (34, 32), (35 + sash_dx, 39), (33 + sash_dx, 42),
             (31, 38), (29, 33)],
            SASH,
        )
        frames.append(frame)
    return frames


def make_dash(source: Image.Image) -> list[Image.Image]:
    # anticipation, launch, full stride, deceleration/recovery
    frames: list[Image.Image] = []
    shifts = (0, 2, 5, 3)
    upper_y = (2, 1, 0, 1)
    leg_poses = [
        ((20, 34), (18, 47), (15, 60), (10, 60), (28, 34), (31, 47), (36, 60), (42, 60)),
        ((22, 33), (18, 44), (10, 57), (5, 58), (30, 33), (36, 43), (43, 57), (49, 58)),
        ((25, 32), (18, 42), (7, 56), (2, 57), (33, 32), (40, 42), (50, 58), (57, 59)),
        ((23, 33), (20, 45), (15, 59), (9, 60), (31, 33), (35, 46), (42, 59), (48, 60)),
    ]
    for index, pose in enumerate(leg_poses):
        frame = indexed_canvas((64, 64), source)
        # Row-wise integer shear leans the guard into acceleration without
        # resampling, blur or scale drift.
        upper = indexed_canvas(source.size, source)
        src_px = source.load()
        dst_px = upper.load()
        top_lean = (1, 4, 7, 4)[index]
        bottom_lean = shifts[index]
        for y in range(28):
            dx = round(top_lean + (bottom_lean - top_lean) * (y / 27))
            for x in range(source.width):
                value = src_px[x, y]
                tx = x + dx
                if value and 0 <= tx < upper.width:
                    dst_px[tx, y] = value
        paste_indexed(frame, upper, (0, upper_y[index]))
        clear_lower(frame)
        d = ImageDraw.Draw(frame)
        draw_waist(d, x_shift=shifts[index], y_shift=upper_y[index])
        lhip, lknee, lankle, lfoot, rhip, rknee, rankle, rfoot = pose
        draw_baggy_leg(d, rhip, rknee, rankle, rfoot, near=False)
        draw_baggy_leg(d, lhip, lknee, lankle, lfoot, near=True)
        # Long sash lag is the speed signal; body leads, cloth follows.
        tail = (10, 6, 2, 8)[index]
        polygon(
            d,
            [(31 + shifts[index], 29), (35 + shifts[index], 32),
             (tail + shifts[index], 38), (tail - 3 + shifts[index], 35),
             (27 + shifts[index], 31)],
            OUTLINE,
        )
        polygon(
            d,
            [(31 + shifts[index], 30), (34 + shifts[index], 32),
             (tail + shifts[index], 36), (tail - 1 + shifts[index], 35),
             (28 + shifts[index], 31)],
            SASH,
        )
        frames.append(frame)
    return frames


def make_jump(source: Image.Image) -> list[Image.Image]:
    # compression, takeoff, rise, apex, fall, prepare, landing, recovery
    frames: list[Image.Image] = []
    configs = [
        (3, ((20, 34), (17, 46), (14, 58), (9, 59), (28, 34), (31, 46), (35, 58), (41, 59))),
        (0, ((20, 31), (18, 43), (17, 57), (12, 58), (28, 31), (30, 43), (32, 57), (38, 58))),
        (0, ((20, 29), (16, 39), (19, 48), (24, 50), (28, 29), (33, 39), (31, 48), (26, 50))),
        (0, ((20, 28), (15, 37), (20, 45), (25, 47), (28, 28), (34, 37), (30, 45), (25, 47))),
        (0, ((20, 29), (16, 39), (20, 49), (25, 51), (28, 29), (33, 39), (30, 49), (25, 51))),
        (0, ((20, 30), (17, 42), (14, 54), (9, 56), (28, 30), (31, 42), (35, 54), (41, 56))),
        (3, ((20, 34), (17, 46), (13, 59), (8, 60), (28, 34), (31, 46), (36, 59), (42, 60))),
        (1, ((20, 32), (18, 45), (15, 60), (10, 60), (28, 32), (30, 45), (34, 60), (40, 60))),
    ]
    for index, (body_y, pose) in enumerate(configs):
        frame = indexed_canvas((48, 64), source)
        paste_indexed(frame, source, (0, body_y))
        clear_lower(frame, max(23, 28 + body_y))
        d = ImageDraw.Draw(frame)
        draw_waist(d, y_shift=body_y)
        lhip, lknee, lankle, lfoot, rhip, rknee, rankle, rfoot = pose
        airborne = index in (2, 3, 4, 5)
        draw_baggy_leg(d, rhip, rknee, rankle, rfoot, near=False, lifted=airborne)
        draw_baggy_leg(d, lhip, lknee, lankle, lfoot, near=True, lifted=airborne)
        # Sash rises after takeoff, floats at apex, then points upward on fall.
        tail_dx = (-1, -3, -5, -4, -2, 1, 3, 1)[index]
        tail_dy = (5, 2, -1, -3, -1, 1, 5, 3)[index]
        polygon(
            d,
            [(30, 29 + body_y), (35, 31 + body_y),
             (37 + tail_dx, 39 + body_y + tail_dy),
             (33 + tail_dx, 43 + body_y + tail_dy),
             (29, 34 + body_y)],
            OUTLINE,
        )
        polygon(
            d,
            [(31, 30 + body_y), (34, 32 + body_y),
             (35 + tail_dx, 39 + body_y + tail_dy),
             (33 + tail_dx, 41 + body_y + tail_dy),
             (30, 34 + body_y)],
            SASH,
        )
        frames.append(frame)
    return frames


def save_indexed(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=False, bits=4, transparency=0)


def save_strip(name: str, frames: list[Image.Image]) -> Path:
    width = frames[0].width
    strip = indexed_canvas((width * len(frames), frames[0].height), frames[0])
    for index, frame in enumerate(frames):
        strip.paste(frame, (index * width, 0))
    path = OUT / f"taina_{name}_v01.png"
    save_indexed(strip, path)
    return path


def rgba_frame(frame: Image.Image) -> Image.Image:
    out = frame.convert("RGBA")
    out.putalpha(frame.point(lambda value: 255 if value else 0, mode="L"))
    return out


def save_gif(name: str, frames: list[Image.Image], timing: list[int]) -> Path:
    rgba = [rgba_frame(frame).resize(
        (frame.width * 6, frame.height * 6), Image.Resampling.NEAREST
    ) for frame in frames]
    path = OUT / f"taina_{name}_preview_v01.gif"
    rgba[0].save(
        path,
        save_all=True,
        append_images=rgba[1:],
        duration=[round(value * 1000 / 60) for value in timing],
        loop=0,
        disposal=2,
    )
    return path


def save_contact_sheet(
    name: str, frames: list[Image.Image], pivot: tuple[int, int]
) -> tuple[Path, Path]:
    scale = 6
    cell_w = frames[0].width * scale
    cell_h = frames[0].height * scale
    sheet = Image.new("RGB", (cell_w * len(frames), cell_h), (10, 18, 34))
    overlay = sheet.copy()
    for index, frame in enumerate(frames):
        sprite = rgba_frame(frame).resize((cell_w, cell_h), Image.Resampling.NEAREST)
        sheet.paste(sprite, (index * cell_w, 0), sprite)
        overlay.paste(sprite, (index * cell_w, 0), sprite)
        d = ImageDraw.Draw(overlay)
        x = index * cell_w + pivot[0] * scale
        y = pivot[1] * scale
        d.line((x - 12, y, x + 12, y), fill=(255, 255, 0), width=2)
        d.line((x, y - 12, x, y + 12), fill=(255, 255, 0), width=2)
    sheet_path = REVIEW / f"taina_{name}_contact_6x_v01.png"
    overlay_path = REVIEW / f"taina_{name}_pivot_overlay_6x_v01.png"
    REVIEW.mkdir(parents=True, exist_ok=True)
    sheet.save(sheet_path)
    overlay.save(overlay_path)
    return sheet_path, overlay_path


def bbox(frame: Image.Image) -> tuple[int, int, int, int] | None:
    mask = frame.point(lambda value: 255 if value else 0, mode="L")
    return mask.getbbox()


def pixel_delta(a: Image.Image, b: Image.Image) -> int:
    return sum(1 for av, bv in zip(a.getdata(), b.getdata()) if av != bv)


def write_report(
    animations: dict[str, tuple[list[Image.Image], list[int], tuple[int, int]]],
    paths: dict[str, dict[str, str]],
    promoted: bool,
) -> None:
    report: dict[str, object] = {
        "schema_version": "1.0.0",
        "report_id": "taina_p0_locomotion_build_v01",
        "generated_at": "2026-07-29",
        "status": (
            "runtime_candidates_promoted_pending_emulator_visual_review"
            if promoted
            else "runtime_candidates_pending_visual_review"
        ),
        "source_of_truth": str(SOURCE.relative_to(PROJECT)),
        "forbidden_sources_used": [],
        "asset_kind": "animation_strip",
        "animations": {},
    }
    rows: dict[str, object] = {}
    for name, (frames, timing, pivot) in animations.items():
        rows[name] = {
            "frame_count": len(frames),
            "cell_px": {"w": frames[0].width, "h": frames[0].height},
            "timing_vblanks": timing,
            "pivot_px": {"x": pivot[0], "y": pivot[1]},
            "frame_bboxes": [bbox(frame) for frame in frames],
            "adjacent_pixel_deltas": [
                pixel_delta(frames[i], frames[(i + 1) % len(frames)])
                for i in range(len(frames))
            ],
            "unique_frame_hashes": len(
                {frame.tobytes() for frame in frames}
            ),
            "evidence": paths[name],
            "promotion_status": (
                "res_runtime_candidate_not_final"
                if promoted
                else "candidate_not_res"
            ),
        }
    report["animations"] = rows
    report_path = (
        PROJECT
        / "doc/art/characters/taina/animation/"
        "taina_p0_locomotion_build_v01.json"
    )
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--promote",
        action="store_true",
        help="Copy validated candidate strips into res as runtime candidates.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Image.open(SOURCE)
    if source.mode != "P" or source.size != (48, 64):
        raise RuntimeError("Approved TAÍNA idle source must remain indexed 48x64.")

    OUT.mkdir(parents=True, exist_ok=True)
    animations = {
        "walk_combat_step_48x64": (make_walk(source), [5, 4, 5, 5, 4, 5], (24, 60)),
        "dash_or_step_in_64x64": (make_dash(source), [3, 2, 3, 4], (24, 60)),
        "jump_rise_fall_landing_48x64": (
            make_jump(source),
            [4, 3, 4, 4, 4, 4, 3, 5],
            (24, 60),
        ),
    }
    paths: dict[str, dict[str, str]] = {}
    for name, (frames, timing, pivot) in animations.items():
        strip = save_strip(name, frames)
        gif = save_gif(name, frames, timing)
        contact, overlay = save_contact_sheet(name, frames, pivot)
        paths[name] = {
            "strip": str(strip.relative_to(PROJECT)),
            "motion_gif": str(gif.relative_to(PROJECT)),
            "contact_sheet": str(contact.relative_to(PROJECT)),
            "pivot_overlay": str(overlay.relative_to(PROJECT)),
        }
        print(strip)
        print(gif)
        print(contact)
        print(overlay)
        if args.promote:
            RES.mkdir(parents=True, exist_ok=True)
            target = RES / strip.name
            shutil.copyfile(strip, target)
            paths[name]["res_runtime_candidate"] = str(target.relative_to(PROJECT))
            print(target)
    write_report(animations, paths, args.promote)


if __name__ == "__main__":
    main()
