#!/usr/bin/env python3
"""Derive TAÍNA's five-frame combo jab from the approved native key pose."""

from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_taina_combo_hit_1_jab_key_pose_v01 import (  # noqa: E402
    IDLE,
    PROJECT,
    build_native,
    polygon,
    rectangle,
    save_indexed,
)


OUT_DIR = PROJECT / "rascunho/taina_combo_hit_1_jab_v01"
REVIEW_DIR = PROJECT / "doc/art/characters/taina/review"
ANIM_DIR = PROJECT / "doc/art/characters/taina/animation"

STRIP = OUT_DIR / "taina_combo_hit_1_jab_native_64x64_v01.png"
GIF = OUT_DIR / "taina_combo_hit_1_jab_native_preview_8x_v01.gif"
CONTACT = REVIEW_DIR / "taina_combo_hit_1_jab_contact_sheet_6x_v01.png"
PIVOT = REVIEW_DIR / "taina_combo_hit_1_jab_pivot_overlay_4x_v01.png"
ONION = REVIEW_DIR / "taina_combo_hit_1_jab_onion_skin_f01_f02_f03_6x_v01.png"
METRICS = ANIM_DIR / "taina_combo_hit_1_jab_metrics_v01.json"

PHASES = [
    "anticipation",
    "launch",
    "active_contact",
    "follow_through_recoil",
    "recovery_bridge",
]
HOLDS = [3, 2, 2, 3, 4]


def indexed_canvas(idle: Image.Image) -> Image.Image:
    frame = Image.new("P", (64, 64), 0)
    frame.putpalette(idle.getpalette())
    frame.info["transparency"] = 0
    frame.paste(idle, (0, 0))
    return frame


def draw_reach_frame(idle: Image.Image, endpoint_x: int, y_offset: int = 0) -> Image.Image:
    """Build a shortened jab using the same clusters as the approved active."""
    frame = indexed_canvas(idle)
    d = ImageDraw.Draw(frame)
    rectangle(d, (34, 12, 63, 25), 0)

    polygon(d, [(30, 14), (34, 15), (36, 19), (35, 24), (32, 27),
                (29, 26), (30, 20)], 1)
    polygon(d, [(31, 15), (33, 16), (35, 19), (34, 23), (32, 25),
                (30, 24), (31, 19)], 7)
    polygon(d, [(32, 16), (34, 18), (34, 21), (32, 22)], 9)

    fist_l = endpoint_x - 8
    top = 16 + y_offset
    bottom = 21 + y_offset
    polygon(d, [(28, 13), (33, 13), (37, 15), (fist_l + 1, top),
                (fist_l + 3, top - 1), (endpoint_x - 2, top),
                (endpoint_x, top + 2), (endpoint_x, bottom),
                (endpoint_x - 2, bottom + 2), (fist_l + 3, bottom + 2),
                (fist_l, bottom), (37, 20), (31, 18), (28, 17)], 1)
    polygon(d, [(30, 14), (33, 14), (37, 16), (fist_l + 1, top + 1),
                (fist_l + 2, bottom - 1), (37, 19), (32, 17),
                (29, 16)], 7)
    polygon(d, [(34, 15), (38, 17), (fist_l + 1, top + 2),
                (fist_l + 1, bottom - 1), (37, 18)], 8)

    polygon(d, [(fist_l + 3, top - 1), (endpoint_x - 2, top),
                (endpoint_x, top + 2), (endpoint_x, bottom),
                (endpoint_x - 2, bottom + 2), (fist_l + 3, bottom + 2),
                (fist_l, bottom - 1), (fist_l + 1, top + 1)], 1)
    polygon(d, [(fist_l + 3, top), (endpoint_x - 3, top + 1),
                (endpoint_x - 1, top + 2), (endpoint_x - 1, bottom - 1),
                (endpoint_x - 3, bottom + 1), (fist_l + 3, bottom + 1),
                (fist_l + 1, bottom - 1), (fist_l + 2, top + 1)], 5)
    rectangle(d, (fist_l + 3, top, endpoint_x - 3, top + 1), 9)
    rectangle(d, (fist_l + 2, top + 2, fist_l + 3, bottom - 1), 4)
    rectangle(d, (endpoint_x - 2, bottom - 2, endpoint_x - 1, bottom - 1), 2)

    polygon(d, [(27, 13), (31, 13), (33, 15), (32, 18), (29, 18),
                (27, 16)], 1)
    polygon(d, [(28, 14), (30, 14), (32, 15), (31, 17), (29, 17),
                (28, 16)], 8)
    polygon(d, [(32, 16), (36, 16), (39, 18), (37, 20), (33, 19)], 7)
    rectangle(d, (33, 16, 35, 17), 9)
    return frame


def delay_sash_tip(frame: Image.Image) -> None:
    """One-pixel flare on the connected sash edge during recoil."""
    px = frame.load()
    moving = []
    for y in range(39, 45):
        for x in range(35, 38):
            if px[x, y] in (1, 5):
                moving.append((x, y, px[x, y]))
    for x, y, value in moving:
        if px[x + 1, y] == 0:
            px[x + 1, y] = value


def rgba_with_mask(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    mask = Image.new("L", image.size)
    mask.putdata([0 if value == 0 else 255 for value in image.getdata()])
    rgba.putalpha(mask)
    return rgba


def bbox(image: Image.Image) -> list[int]:
    px = image.load()
    points = [
        (x, y)
        for y in range(image.height)
        for x in range(image.width)
        if px[x, y] != 0
    ]
    return [
        min(x for x, _ in points),
        min(y for _, y in points),
        max(x for x, _ in points),
        max(y for _, y in points),
    ]


def components(image: Image.Image) -> list[int]:
    px = image.load()
    remaining = {
        (x, y)
        for y in range(image.height)
        for x in range(image.width)
        if px[x, y] != 0
    }
    sizes = []
    while remaining:
        queue = deque([remaining.pop()])
        size = 0
        while queue:
            x, y = queue.popleft()
            size += 1
            for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if point in remaining:
                    remaining.remove(point)
                    queue.append(point)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def frame_delta(a: Image.Image, b: Image.Image) -> int:
    return sum(1 for av, bv in zip(a.getdata(), b.getdata()) if av != bv)


def tile_metrics(frames: list[Image.Image]) -> tuple[list[dict], int]:
    global_tiles: set[bytes] = set()
    per_frame = []
    for frame_index, frame in enumerate(frames):
        px = frame.load()
        tiles = []
        nonempty_positions = 0
        for ty in range(0, 64, 8):
            for tx in range(0, 64, 8):
                tile = bytes(
                    px[x, y]
                    for y in range(ty, ty + 8)
                    for x in range(tx, tx + 8)
                )
                if any(tile):
                    nonempty_positions += 1
                    tiles.append(tile)
                    global_tiles.add(tile)
        per_frame.append(
            {
                "frame": frame_index,
                "nonempty_tile_positions": nonempty_positions,
                "unique_nonempty_tiles": len(set(tiles)),
                "uncompressed_tile_bytes": len(set(tiles)) * 32,
            }
        )
    return per_frame, len(global_tiles)


def make_strip(frames: list[Image.Image]) -> Image.Image:
    strip = Image.new("P", (64 * len(frames), 64), 0)
    strip.putpalette(frames[0].getpalette())
    strip.info["transparency"] = 0
    for index, frame in enumerate(frames):
        strip.paste(frame, (index * 64, 0))
    return strip


def save_review(frames: list[Image.Image]) -> None:
    zoom = 6
    contact = Image.new("RGB", (64 * len(frames) * zoom, 64 * zoom), (10, 18, 34))
    for index, frame in enumerate(frames):
        rgba = rgba_with_mask(frame).resize(
            (64 * zoom, 64 * zoom), Image.Resampling.NEAREST
        )
        contact.paste(rgba, (index * 64 * zoom, 0), rgba)
    contact.save(CONTACT)

    pivot = contact.resize(
        (64 * len(frames) * 4, 64 * 4), Image.Resampling.NEAREST
    )
    pd = ImageDraw.Draw(pivot)
    for index in range(len(frames)):
        ox = index * 64 * 4
        pd.line((ox + 24 * 4, 0, ox + 24 * 4, 255), fill=(255, 50, 80), width=1)
        pd.line((ox, 60 * 4, ox + 64 * 4 - 1, 60 * 4), fill=(80, 220, 255), width=1)
    pivot.save(PIVOT)

    onion = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    colors = [(40, 180, 255), (255, 235, 80), (255, 70, 120)]
    for frame, color in zip(frames[1:4], colors):
        src = frame.load()
        layer = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        dst = layer.load()
        for y in range(64):
            for x in range(64):
                if src[x, y] != 0:
                    dst[x, y] = (*color, 110)
        onion = Image.alpha_composite(onion, layer)
    onion.resize((384, 384), Image.Resampling.NEAREST).save(ONION)

    gif_frames = [
        rgba_with_mask(frame).resize((512, 512), Image.Resampling.NEAREST)
        for frame in frames
    ]
    durations = [hold * 1000 // 60 for hold in HOLDS]
    gif_frames[0].save(
        GIF,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        transparency=0,
    )


def write_metrics(frames: list[Image.Image], strip: Image.Image) -> None:
    per_frame_tiles, global_unique_tiles = tile_metrics(frames)
    frame_rows = []
    for index, frame in enumerate(frames):
        box = bbox(frame)
        comps = components(frame)
        frame_rows.append(
            {
                "frame": index,
                "phase": PHASES[index],
                "hold_vblanks": HOLDS[index],
                "bbox_xyxy": box,
                "visible_width_px": box[2] - box[0] + 1,
                "visible_height_px": box[3] - box[1] + 1,
                "component_count": len(comps),
                "largest_component_pixels": comps[0],
                "primary_ground_y": 60,
                "pivot": [24, 60],
            }
        )
    report = {
        "schema_version": "1.0.0",
        "report_id": "taina_combo_hit_1_jab_metrics_v01",
        "generated_at": "2026-07-29",
        "status": "offline_metrics_generated",
        "strip": str(STRIP.relative_to(PROJECT)).replace("\\", "/"),
        "strip_sha256": sha256(STRIP.read_bytes()).hexdigest(),
        "strip_dimensions": list(strip.size),
        "frame_cell": [64, 64],
        "frame_count": len(frames),
        "total_vblanks": sum(HOLDS),
        "frames": frame_rows,
        "adjacent_pixel_deltas": [
            {
                "from": index,
                "to": index + 1,
                "changed_pixels": frame_delta(frames[index], frames[index + 1]),
            }
            for index in range(len(frames) - 1)
        ],
        "tile_budget_offline": {
            "per_frame": per_frame_tiles,
            "global_unique_nonempty_tiles": global_unique_tiles,
            "global_uncompressed_tile_bytes": global_unique_tiles * 32,
            "measurement_level": "offline_png_tiles_not_rescomp",
        },
        "claim_limit": "ResComp and BlastEm evidence remain required after res promotion.",
    }
    METRICS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    ANIM_DIR.mkdir(parents=True, exist_ok=True)
    idle = Image.open(IDLE)
    frame0 = indexed_canvas(idle)
    frame1 = draw_reach_frame(idle, 47)
    frame2 = build_native()
    frame3 = draw_reach_frame(idle, 45, 1)
    delay_sash_tip(frame3)
    frame4 = indexed_canvas(idle)
    frames = [frame0, frame1, frame2, frame3, frame4]
    for index, frame in enumerate(frames):
        save_indexed(frame, OUT_DIR / f"taina_combo_hit_1_jab_frame_{index:02d}_v01.png")
    strip = make_strip(frames)
    save_indexed(strip, STRIP)
    save_review(frames)
    write_metrics(frames, strip)
    for path in (STRIP, GIF, CONTACT, PIVOT, ONION, METRICS):
        print(path)


if __name__ == "__main__":
    main()
