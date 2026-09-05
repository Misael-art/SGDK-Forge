#!/usr/bin/env python3
"""Build the P1/A1 Kirby strip as native-grid authored pixel art.

The previous P1 draft was intentionally retired as
``technical_pass_visual_fail``: its radial ellipses kept the same acting across
the run cycle, collapsed jump into idle and produced broken FLOAT/INHALE
silhouettes.  This builder starts again from the approved R2 model sheet and
the generated key-pose board.  Each frame has a distinct silhouette and limb
plan before colour is applied.

Output contract (doc/art/PRODUCTION_ASSET_PACK.md A1):
  256x32 indexed PNG, eight 32x32 cells, PAL2, transparency index 0.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "source_art" / "p1" / "A1"
OUT = OUT_DIR / "ph_kirby.png"

PAL2 = {
    0: (255, 0, 255),
    1: (255, 219, 255),
    2: (255, 182, 219),
    3: (255, 146, 182),
    4: (219, 73, 146),
    5: (146, 36, 109),
    6: (109, 36, 73),
    7: (219, 73, 73),
    8: (146, 36, 36),
    9: (36, 36, 73),
    10: (255, 255, 255),
}
LEGAL = {0, 36, 73, 109, 146, 182, 219, 255}
FRAME_NAMES = ["idle", "run1", "run2", "run3", "run4", "jump", "float", "inhale"]
W = H = 32


def ellipse(box: tuple[int, int, int, int]) -> set[tuple[int, int]]:
    mask = Image.new("1", (W, H), 0)
    ImageDraw.Draw(mask).ellipse(box, fill=1)
    return {(x, y) for y in range(H) for x in range(W) if mask.getpixel((x, y))}


def polygon(points: list[tuple[int, int]]) -> set[tuple[int, int]]:
    mask = Image.new("1", (W, H), 0)
    ImageDraw.Draw(mask).polygon(points, fill=1)
    return {(x, y) for y in range(H) for x in range(W) if mask.getpixel((x, y))}


def union(*parts: set[tuple[int, int]]) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for part in parts:
        result.update(part)
    return result


def dilate(mask: set[tuple[int, int]]) -> set[tuple[int, int]]:
    result = set(mask)
    for x, y in mask:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H:
                    result.add((nx, ny))
    return result


@dataclass(frozen=True)
class Pose:
    name: str
    body: set[tuple[int, int]]
    arms: set[tuple[int, int]]
    feet_light: set[tuple[int, int]]
    feet_back: set[tuple[int, int]]
    center: tuple[int, int]
    eyes: tuple[tuple[int, int], tuple[int, int]]
    mouth: str = "neutral"


def make_poses() -> list[Pose]:
    return [
        Pose(
            "idle",
            ellipse((6, 5, 25, 23)),
            union(ellipse((3, 12, 9, 19)), ellipse((23, 12, 28, 19))),
            ellipse((17, 21, 26, 27)),
            ellipse((6, 21, 15, 27)),
            (16, 14), ((13, 11), (18, 11)), "smile",
        ),
        Pose(
            "run1_contact",
            union(ellipse((7, 6, 26, 23)), polygon([(8, 9), (5, 12), (6, 19), (11, 20)])),
            union(polygon([(8, 12), (3, 14), (3, 18), (9, 18)]), ellipse((23, 12, 29, 18))),
            polygon([(18, 22), (26, 21), (29, 24), (27, 27), (19, 27), (16, 25)]),
            polygon([(10, 21), (15, 23), (13, 27), (5, 27), (3, 25), (5, 22)]),
            (17, 14), ((15, 11), (20, 11)), "focused",
        ),
        Pose(
            "run2_passage",
            union(ellipse((7, 5, 26, 22)), polygon([(8, 8), (4, 11), (5, 18), (11, 19)])),
            union(ellipse((4, 10, 10, 16)), polygon([(23, 14), (28, 11), (29, 14), (25, 19)])),
            polygon([(17, 21), (24, 20), (28, 22), (27, 25), (20, 26), (16, 24)]),
            polygon([(11, 20), (16, 23), (14, 27), (8, 27), (6, 25), (8, 22)]),
            (17, 13), ((15, 10), (20, 10)), "focused",
        ),
        Pose(
            "run3_opposite_contact",
            union(ellipse((7, 6, 26, 23)), polygon([(8, 9), (5, 12), (6, 19), (11, 20)])),
            union(polygon([(8, 12), (4, 10), (3, 13), (7, 18)]), ellipse((23, 14, 29, 20))),
            polygon([(8, 22), (15, 21), (18, 24), (16, 27), (7, 27), (3, 25), (4, 23)]),
            polygon([(19, 21), (25, 22), (29, 24), (27, 27), (20, 27), (17, 25)]),
            (17, 14), ((15, 11), (20, 11)), "focused",
        ),
        Pose(
            "run4_opposite_passage",
            union(ellipse((7, 5, 26, 22)), polygon([(8, 8), (4, 11), (5, 18), (11, 19)])),
            union(polygon([(8, 14), (4, 17), (6, 20), (11, 18)]), ellipse((23, 10, 29, 16))),
            polygon([(10, 20), (16, 22), (15, 26), (8, 27), (5, 25), (7, 22)]),
            polygon([(18, 21), (24, 21), (28, 23), (27, 26), (21, 27), (17, 24)]),
            (17, 13), ((15, 10), (20, 10)), "focused",
        ),
        Pose(
            "jump_rising",
            ellipse((7, 3, 25, 21)),
            union(polygon([(9, 8), (4, 6), (3, 10), (8, 14), (11, 12)]), polygon([(22, 8), (27, 5), (29, 9), (25, 14), (22, 13)])),
            polygon([(17, 19), (23, 20), (25, 23), (22, 25), (17, 23)]),
            polygon([(10, 19), (16, 21), (14, 25), (8, 24), (7, 22)]),
            (16, 12), ((13, 9), (18, 9)), "effort",
        ),
        Pose(
            "float_inflated",
            ellipse((7, 5, 24, 22)),
            union(ellipse((2, 11, 12, 21)), ellipse((20, 10, 29, 21))),
            polygon([(16, 21), (21, 22), (23, 26), (20, 28), (15, 25)]),
            polygon([(9, 21), (14, 23), (13, 27), (7, 26), (6, 23)]),
            (16, 14), ((13, 9), (18, 9)), "puffed",
        ),
        Pose(
            "inhale",
            union(ellipse((4, 5, 22, 23)), ellipse((17, 7, 29, 22))),
            ellipse((2, 12, 8, 19)),
            polygon([(15, 21), (21, 22), (24, 25), (21, 28), (15, 26)]),
            polygon([(7, 21), (14, 23), (13, 27), (6, 27), (4, 25)]),
            (14, 14), ((13, 9), (17, 10)), "inhale",
        ),
    ]


def paint(frame: Image.Image, points: set[tuple[int, int]], colour: int) -> None:
    px = frame.load()
    for x, y in points:
        px[x, y] = colour


def paint_body_shading(frame: Image.Image, pose: Pose, body_mass: set[tuple[int, int]]) -> None:
    cx, cy = pose.center
    # A compact lower-right shadow describes volume without radial banding.
    shadow = {
        (x, y) for x, y in body_mass
        if y >= cy + 5 + abs(x - cx) // 4
        or (x >= cx + 6 and y >= cy + 1 + abs(x - cx) // 5)
    }
    deep = {
        (x, y) for x, y in shadow
        if y >= cy + 7 + abs(x - cx) // 5 and x <= cx + 3
    }
    paint(frame, shadow, 4)
    paint(frame, deep, 5)

    # One deliberate specular cluster; never a gradient or AA fringe.
    highlight = {
        (x, y) for x, y in body_mass
        if (x - (cx - 5)) ** 2 + (y - (cy - 5)) ** 2 <= 7
    }
    paint(frame, highlight, 1)


def paint_foot(frame: Image.Image, foot_mask: set[tuple[int, int]], back: bool) -> None:
    paint(frame, foot_mask, 8 if back else 7)
    if not foot_mask:
        return
    min_x = min(x for x, _ in foot_mask)
    max_y = max(y for _, y in foot_mask)
    shine = {(x, y) for x, y in foot_mask if not back and x <= min_x + 2 and y <= max_y - 2}
    shade = {(x, y) for x, y in foot_mask if y >= max_y - 1}
    paint(frame, shine, 3)
    paint(frame, shade, 8)


def dot(frame: Image.Image, x: int, y: int, colour: int) -> None:
    if not (0 <= x < W and 0 <= y < H):
        raise ValueError(f"pixel outside frame: {(x, y)}")
    frame.putpixel((x, y), colour)


def draw_eye(frame: Image.Image, x: int, y: int, narrowed: bool = False) -> None:
    if narrowed:
        for dx, dy in ((-1, 0), (0, 0), (1, 1), (0, 1), (1, 2)):
            dot(frame, x + dx, y + dy, 9)
        dot(frame, x - 1, y, 10)
        return
    for dx, dy in ((0, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 2)):
        dot(frame, x + dx, y + dy, 9)
    dot(frame, x - 1, y - 1, 10)


def draw_face(frame: Image.Image, pose: Pose) -> None:
    narrowed = pose.mouth == "focused"
    draw_eye(frame, *pose.eyes[0], narrowed=narrowed)
    draw_eye(frame, *pose.eyes[1], narrowed=narrowed)
    cx, cy = pose.center
    if pose.mouth == "smile":
        dot(frame, cx + 3, cy + 3, 5)
        dot(frame, cx + 4, cy + 3, 5)
        dot(frame, cx + 4, cy + 2, 6)
    elif pose.mouth == "focused":
        dot(frame, cx + 5, cy + 3, 6)
        dot(frame, cx + 6, cy + 3, 6)
    elif pose.mouth == "effort":
        dot(frame, cx + 3, cy + 3, 9)
        dot(frame, cx + 4, cy + 4, 9)
    elif pose.mouth == "puffed":
        # Cheek seams make the two protruding lobes readable at 1x.
        for x, y in ((9, 14), (10, 16), (11, 18), (21, 13), (20, 16), (20, 18)):
            dot(frame, x, y, 6)
        dot(frame, 19, 15, 9)
        dot(frame, 19, 16, 9)
    elif pose.mouth == "inhale":
        mouth = ellipse((19, 10, 28, 21))
        inner = ellipse((21, 13, 27, 20))
        paint(frame, mouth, 9)
        paint(frame, inner, 8)
        paint(frame, {(23, 18), (24, 18), (25, 18), (24, 19)}, 7)

    # Blush stays behind the acting and is kept to compact 2px clusters.
    if pose.mouth not in {"inhale", "puffed"}:
        for x, y in ((cx - 6, cy + 2), (cx - 5, cy + 2), (cx + 7, cy + 2), (cx + 8, cy + 2)):
            dot(frame, x, y, 7)


def enforce_midtone(frame: Image.Image, pose: Pose, eligible: set[tuple[int, int]]) -> None:
    """Keep PAL2[3] at 10% of visible pixels with one coherent body band."""
    visible = sum(1 for value in frame.get_flattened_data() if value != 0)
    target = round(visible * 0.10)
    current = sum(1 for value in frame.get_flattened_data() if value == 3)
    needed = max(0, target - current)
    cx, cy = pose.center
    candidates = [
        (x, y) for x, y in eligible
        if frame.getpixel((x, y)) == 2 and y >= cy + 1 and x >= cx - 7
    ]
    # A curved lower-body crescent follows the sphere instead of creating the
    # flat horizontal band that made the retired draft look procedural.
    candidates.sort(
        key=lambda p: (
            abs(p[1] - (cy + 4 + abs(p[0] - cx) // 4)),
            abs(p[0] - (cx + 2)),
        )
    )
    paint(frame, set(candidates[:needed]), 3)


def build_frame(pose: Pose) -> Image.Image:
    frame = Image.new("P", (W, H), 0)
    body_mass = union(pose.body, pose.arms)
    silhouette = union(body_mass, pose.feet_light, pose.feet_back)
    outline = dilate(silhouette) - silhouette
    if any(x in (0, W - 1) or y in (0, H - 1) for x, y in outline):
        raise ValueError(f"{pose.name}: outline touches cell edge")
    paint(frame, outline, 6)
    paint(frame, body_mass, 2)
    paint_body_shading(frame, pose, body_mass)
    paint_foot(frame, pose.feet_back, back=True)
    paint_foot(frame, pose.feet_light, back=False)

    # Interior separation at the shoe/body junction preserves both feet.
    for foot in (pose.feet_back, pose.feet_light):
        top = min(y for _, y in foot)
        seam = {(x, y) for x, y in foot if y <= top + 1 and (x, y - 1) in body_mass}
        paint(frame, seam, 6)

    draw_face(frame, pose)
    enforce_midtone(frame, pose, body_mass)
    return frame


def indexed_sheet(frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new("P", (W * len(frames), H), 0)
    palette: list[int] = []
    for index in range(256):
        palette.extend(PAL2.get(index, (0, 0, 0)))
    sheet.putpalette(palette)
    for index, frame in enumerate(frames):
        frame.putpalette(palette)
        sheet.paste(frame, (index * W, 0))
    return sheet


def validate(sheet: Image.Image) -> dict:
    rgb = sheet.convert("RGB")
    used = set(rgb.get_flattened_data())
    illegal = [colour for colour in used if colour != PAL2[0] and any(channel not in LEGAL for channel in colour)]
    frames = []
    for index, name in enumerate(FRAME_NAMES):
        cell = sheet.crop((index * W, 0, (index + 1) * W, H))
        values = list(cell.get_flattened_data())
        visible = [value for value in values if value != 0]
        midtone = sum(value == 3 for value in visible)
        ratio = (midtone / len(visible)) if visible else 0.0
        frames.append({
            "index": index,
            "name": name,
            "visible_pixels": len(visible),
            "midtone_pixels": midtone,
            "midtone_ratio": round(ratio, 6),
            "used_indices": sorted(set(values)),
            "edge_clear": not any(cell.getpixel((x, y)) != 0 for x in range(W) for y in (0, H - 1))
                          and not any(cell.getpixel((x, y)) != 0 for y in range(H) for x in (0, W - 1)),
        })
    idle_values = list(sheet.crop((0, 0, W, H)).get_flattened_data())
    float_values = list(sheet.crop((6 * W, 0, 7 * W, H)).get_flattened_data())
    idle_mask = {index for index, value in enumerate(idle_values) if value != 0}
    float_mask = {index for index, value in enumerate(float_values) if value != 0}
    union_mask = idle_mask | float_mask
    silhouette_delta = len(idle_mask ^ float_mask) / max(1, len(union_mask))
    silhouette_iou = len(idle_mask & float_mask) / max(1, len(union_mask))
    silhouette_pass = silhouette_delta >= 0.12
    return {
        "schema": "native_grid_translation_report.v1",
        "asset_id": "P1-A1",
        "source_of_truth": "data/source_art/r2/r2-01/concept.png",
        "pose_reference": "data/source_art/p1/A1/reference/generated_key_pose_board.png",
        "obsolete_source_excluded": "data/source_art/p1/A1/obsolete_technical_pass_visual_fail/ph_kirby_pre_rework.png",
        "dimensions": [sheet.width, sheet.height],
        "mode": sheet.mode,
        "visible_colour_count": len(used - {PAL2[0]}),
        "illegal_rgb333_colours": illegal,
        "float_silhouette_test": {
            "comparison": "frame_0_idle_vs_frame_6_float",
            "symmetric_difference_over_union": round(silhouette_delta, 6),
            "intersection_over_union": round(silhouette_iou, 6),
            "minimum_difference": 0.12,
            "status": "passed" if silhouette_pass else "failed"
        },
        "frames": frames,
        "status": "passed" if not illegal and silhouette_pass and all(0.08 <= f["midtone_ratio"] <= 0.12 and f["edge_clear"] for f in frames) else "failed",
    }


def make_silhouette_evidence(sheet: Image.Image) -> None:
    evidence = OUT_DIR / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    board = Image.new("RGB", (W * 16 + 48, H * 8 + 40), (238, 238, 238))
    draw = ImageDraw.Draw(board)
    for slot, (frame_index, label) in enumerate(((0, "IDLE"), (6, "FLOAT"))):
        cell = sheet.crop((frame_index * W, 0, (frame_index + 1) * W, H))
        silhouette = Image.new("RGB", (W, H), (255, 255, 255))
        pixels = silhouette.load()
        for y in range(H):
            for x in range(W):
                if cell.getpixel((x, y)) != 0:
                    pixels[x, y] = (0, 0, 0)
        preview = silhouette.resize((W * 8, H * 8), Image.Resampling.NEAREST)
        x = 16 + slot * (W * 8 + 16)
        board.paste(preview, (x, 24))
        draw.text((x, 6), label, fill=(20, 20, 20))
    board.save(evidence / "idle_vs_float_silhouette.png")


def main() -> int:
    poses = make_poses()
    frames = [build_frame(pose) for pose in poses]
    sheet = indexed_sheet(frames)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, optimize=False)
    make_silhouette_evidence(sheet)
    report = validate(sheet)
    report["sheet_sha256"] = sha256(OUT.read_bytes()).hexdigest()
    (OUT_DIR / "native_grid_translation_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    for frame in report["frames"]:
        print(
            f"{frame['index']} {frame['name']:7} visible={frame['visible_pixels']:3} "
            f"midtone={frame['midtone_ratio'] * 100:5.2f}% edge_clear={frame['edge_clear']}"
        )
    print(f"status={report['status']} output={OUT.relative_to(ROOT)} sha256={report['sheet_sha256']}")
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
