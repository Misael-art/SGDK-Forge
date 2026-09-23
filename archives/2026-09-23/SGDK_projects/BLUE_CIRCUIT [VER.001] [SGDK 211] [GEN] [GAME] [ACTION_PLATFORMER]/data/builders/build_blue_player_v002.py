#!/usr/bin/env python3
"""Pixel-authored 24x32 translation of the approved BLUE_CIRCUIT model sheet."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
CELL_W = 24
CELL_H = 32
GROUND_Y = 29

COLORS = [
    (238, 0, 238),
    (0, 0, 0),
    (34, 34, 34),
    (68, 68, 102),
    (68, 204, 238),
    (204, 238, 238),
    (238, 170, 34),
    (238, 102, 0),
    (136, 238, 34),
    (238, 34, 170),
    (34, 102, 204),
    (238, 170, 102),
    (102, 68, 34),
    (238, 238, 238),
    (136, 136, 136),
    (238, 34, 68),
]

OUTLINE = 1
HAIR = 2
PANTS = 3
CYAN = 4
JACKET = 5
AMBER = 6
ORANGE = 7
SKIN = 11
BROWN = 12
WHITE = 13
GRAY = 14


def palette_bytes() -> list[int]:
    values: list[int] = []
    for color in COLORS:
        values.extend(color)
    values.extend([0, 0, 0] * (256 - len(COLORS)))
    return values


def new_frame() -> Image.Image:
    image = Image.new("P", (CELL_W, CELL_H), 0)
    image.putpalette(palette_bytes())
    image.info["transparency"] = 0
    return image


def line(draw: ImageDraw.ImageDraw, points, fill: int, width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")


def limb(draw: ImageDraw.ImageDraw, points, inner: int, outer_width: int = 5, inner_width: int = 3) -> None:
    line(draw, points, OUTLINE, outer_width)
    line(draw, points, inner, inner_width)


def draw_boot(draw: ImageDraw.ImageDraw, foot: tuple[int, int], direction: int) -> None:
    x, y = foot
    if direction < 0:
        outer = [(x + 1, y - 2), (x - 3, y - 1), (x - 4, y + 1), (x + 2, y + 1)]
        inner = [(x, y - 1), (x - 2, y), (x + 1, y)]
    else:
        outer = [(x - 1, y - 2), (x + 3, y - 1), (x + 4, y + 1), (x - 2, y + 1)]
        inner = [(x, y - 1), (x + 2, y), (x - 1, y)]
    outer = [(max(1, min(22, px)), max(1, min(30, py))) for px, py in outer]
    inner = [(max(1, min(22, px)), max(1, min(30, py))) for px, py in inner]
    draw.polygon(outer, fill=OUTLINE)
    draw.line(inner, fill=GRAY, width=1)
    draw.point((x, y), fill=CYAN)


def draw_character(
    *,
    legs: tuple[tuple[tuple[int, int], tuple[int, int]], tuple[tuple[int, int], tuple[int, int]]],
    arms: tuple[tuple[tuple[int, int], tuple[int, int]], tuple[tuple[int, int], tuple[int, int]]],
    body_y: int = 0,
    lean: int = 0,
    tool_active: bool = False,
    recoil: bool = False,
) -> Image.Image:
    image = new_frame()
    draw = ImageDraw.Draw(image)
    hip_left = (10 + lean, 18 + body_y)
    hip_right = (14 + lean, 18 + body_y)

    # Legs and boots are drawn first so every limb joins the hip mass.
    for hip, (knee, foot) in zip((hip_left, hip_right), legs):
        limb(draw, [hip, knee, foot], PANTS, 5, 3)
        draw_boot(draw, foot, -1 if foot[0] < knee[0] else 1)

    # Torso: black envelope, white jacket, cyan seam, amber belt.
    torso = [
        (8 + lean, 9 + body_y),
        (15 + lean, 9 + body_y),
        (17 + lean, 13 + body_y),
        (15 + lean, 19 + body_y),
        (9 + lean, 19 + body_y),
        (7 + lean, 14 + body_y),
    ]
    draw.polygon(torso, fill=OUTLINE)
    jacket = [
        (9 + lean, 10 + body_y),
        (14 + lean, 10 + body_y),
        (15 + lean, 13 + body_y),
        (14 + lean, 17 + body_y),
        (9 + lean, 17 + body_y),
        (8 + lean, 14 + body_y),
    ]
    draw.polygon(jacket, fill=JACKET)
    draw.line((11 + lean, 10 + body_y, 11 + lean, 17 + body_y), fill=WHITE)
    draw.line((12 + lean, 11 + body_y, 12 + lean, 16 + body_y), fill=CYAN)
    draw.rectangle((9 + lean, 17 + body_y, 15 + lean, 19 + body_y), fill=OUTLINE)
    draw.line((10 + lean, 18 + body_y, 14 + lean, 18 + body_y), fill=AMBER)
    draw.point((12 + lean, 18 + body_y), fill=ORANGE)

    shoulder_left = (9 + lean, 11 + body_y)
    shoulder_right = (15 + lean, 11 + body_y)
    for side, (shoulder, arm) in enumerate(zip((shoulder_left, shoulder_right), arms)):
        elbow, hand = arm
        limb(draw, [shoulder, elbow, hand], JACKET, 5, 3)
        draw.rectangle((hand[0] - 2, hand[1] - 2, hand[0] + 2, hand[1] + 2), fill=OUTLINE)
        draw.rectangle((hand[0] - 1, hand[1] - 1, hand[0] + 1, hand[1] + 1), fill=SKIN)
        if side == 1:
            draw.point(hand, fill=CYAN)
            if tool_active:
                draw.line((hand[0] - 1, hand[1] - 2, hand[0] + 1, hand[1] - 2), fill=CYAN)
                draw.point((min(22, hand[0] + 2), hand[1]), fill=WHITE)

    # Side-facing head and hair retain the model-sheet identity at small size.
    head_x = 11 + lean
    head_y = 6 + body_y
    draw.polygon(
        [
            (head_x - 4, head_y - 3),
            (head_x - 1, head_y - 5),
            (head_x + 3, head_y - 4),
            (head_x + 5, head_y - 1),
            (head_x + 4, head_y + 4),
            (head_x - 2, head_y + 5),
            (head_x - 4, head_y + 2),
        ],
        fill=OUTLINE,
    )
    draw.polygon(
        [
            (head_x - 2, head_y - 2),
            (head_x + 2, head_y - 2),
            (head_x + 4, head_y),
            (head_x + 2, head_y + 3),
            (head_x - 1, head_y + 3),
        ],
        fill=SKIN,
    )
    draw.polygon(
        [
            (head_x - 3, head_y - 3),
            (head_x - 1, head_y - 5),
            (head_x, head_y - 3),
            (head_x + 2, head_y - 5),
            (head_x + 4, head_y - 2),
            (head_x + 1, head_y - 1),
            (head_x - 2, head_y),
        ],
        fill=HAIR,
    )
    draw.point((head_x + 3, head_y), fill=OUTLINE)
    draw.point((head_x + 4, head_y + 2), fill=BROWN)
    if recoil:
        draw.line((head_x + 2, head_y + 3, head_x + 4, head_y + 4), fill=OUTLINE)
    return image


def run_frames() -> list[Image.Image]:
    poses = [
        (((8, 23), (3, 28)), ((16, 23), (20, 29)), ((8, 14), (5, 18)), ((17, 13), (19, 9))),
        (((9, 23), (6, 29)), ((15, 22), (18, 26)), ((8, 13), (6, 10)), ((17, 14), (19, 18))),
        (((11, 23), (12, 29)), ((15, 23), (17, 29)), ((8, 14), (5, 18)), ((17, 13), (19, 9))),
        (((8, 22), (5, 26)), ((16, 23), (19, 29)), ((8, 13), (6, 9)), ((17, 14), (20, 18))),
        (((8, 23), (4, 29)), ((15, 23), (19, 28)), ((8, 14), (5, 18)), ((17, 13), (19, 9))),
        (((9, 22), (6, 26)), ((16, 23), (20, 29)), ((8, 13), (6, 9)), ((17, 14), (20, 18))),
    ]
    return [
        draw_character(
            legs=((pose[0], pose[1])),
            arms=((pose[2], pose[3])),
            lean=1,
        )
        for pose in poses
    ]


def shoot_frames() -> list[Image.Image]:
    frames = []
    for extension, lean in ((17, 0), (18, 1), (19, 1)):
        frames.append(
            draw_character(
                legs=(((9, 23), (7, 29)), ((15, 23), (18, 29))),
                arms=(((8, 14), (6, 18)), ((17, 12), (extension, 12))),
                lean=lean,
                tool_active=True,
            )
        )
    return frames


def jump_frames() -> list[Image.Image]:
    return [
        draw_character(
            legs=(((9, 23), (7, 29)), ((15, 23), (18, 29))),
            arms=(((8, 14), (6, 18)), ((17, 14), (19, 18))),
            body_y=0,
        ),
        draw_character(
            legs=(((8, 21), (5, 24)), ((16, 21), (19, 24))),
            arms=(((8, 13), (6, 9)), ((17, 13), (20, 9))),
            body_y=0,
        ),
        draw_character(
            legs=(((8, 21), (6, 22)), ((16, 21), (18, 22))),
            arms=(((8, 13), (5, 12)), ((17, 13), (20, 12))),
            body_y=0,
        ),
        draw_character(
            legs=(((9, 23), (7, 29)), ((15, 23), (18, 29))),
            arms=(((8, 14), (6, 18)), ((17, 14), (19, 18))),
            body_y=0,
        ),
    ]


def idle_frames() -> list[Image.Image]:
    return [
        draw_character(
            legs=(((10, 23), (9, 29)), ((14, 23), (16, 29))),
            arms=(((8, 14), (7, 18)), ((17, 14), (18, 18))),
        )
    ]


def save_strip(path: Path, frames: list[Image.Image]) -> None:
    strip = Image.new("P", (CELL_W * len(frames), CELL_H), 0)
    strip.putpalette(palette_bytes())
    strip.info["transparency"] = 0
    for index, frame in enumerate(frames):
        strip.paste(frame, (index * CELL_W, 0))
    path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(path, transparency=0, bits=4)


def main() -> int:
    groups = {
        "run": run_frames(),
        "shoot": shoot_frames(),
        "jump": jump_frames(),
        "idle": idle_frames(),
    }
    runtime = ROOT / "res/blue_circuit"
    for name, frames in groups.items():
        save_strip(runtime / f"player_{name}.png", frames)

    combined = Image.new("P", (CELL_W * 6, CELL_H * 4), 0)
    combined.putpalette(palette_bytes())
    combined.info["transparency"] = 0
    for row, name in enumerate(("run", "shoot", "jump", "idle")):
        for index, frame in enumerate(groups[name]):
            combined.paste(frame, (index * CELL_W, row * CELL_H))
    evidence = ROOT / "out/evidence/sprite_rework_20260723"
    evidence.mkdir(parents=True, exist_ok=True)
    combined.save(evidence / "blue_player_all_v002.png", transparency=0, bits=4)
    print("generated blue player v002: idle=1 run=6 jump=4 shoot=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
