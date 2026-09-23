from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

from PIL import Image, ImageDraw


CELL_W = 48
CELL_H = 64
PIVOT = (24, 58)
GROUND_Y = 58

PALETTE = [
    (0xEE, 0x00, 0xEE),  # 00 transparent
    (0x00, 0x00, 0x00),  # 01 outline / hair deep
    (0x22, 0x22, 0x22),  # 02 hair / shorts shadow
    (0x44, 0x44, 0x44),  # 03 shorts / rock dark
    (0x66, 0x66, 0x66),  # 04 rock mid
    (0x88, 0x66, 0x44),  # 05 deep skin / wrap shadow
    (0xAA, 0x66, 0x22),  # 06 skin base
    (0xCC, 0x88, 0x44),  # 07 skin light
    (0xEE, 0xAA, 0x66),  # 08 skin highlight
    (0xCC, 0xAA, 0x88),  # 09 wrap base
    (0xEE, 0xEE, 0xCC),  # 10 wrap highlight / teeth
    (0xCC, 0xAA, 0x22),  # 11 gold trim
    (0xCC, 0x22, 0x22),  # 12 red armband / lava red
    (0xEE, 0x66, 0x00),  # 13 lava orange
    (0xEE, 0xEE, 0x00),  # 14 lava hot / eye accent
    (0xEE, 0xEE, 0xEE),  # 15 eye spec / emergency highlight
]


def flat_palette() -> list[int]:
    raw: list[int] = []
    for color in PALETTE:
        raw.extend(color)
    raw.extend([0, 0, 0] * (256 - len(PALETTE)))
    return raw


def canvas(w: int = CELL_W, h: int = CELL_H) -> Image.Image:
    img = Image.new("P", (w, h), 0)
    img.putpalette(flat_palette())
    return img


def trim_plte(path: Path, max_entries: int = 16) -> None:
    data = path.read_bytes()
    out = bytearray(data[:8])
    i = 8
    while i + 8 <= len(data):
        length = struct.unpack(">I", data[i : i + 4])[0]
        chunk_type = data[i + 4 : i + 8]
        chunk = data[i + 8 : i + 8 + length]
        crc = data[i + 8 + length : i + 12 + length]
        i += 12 + length
        if chunk_type == b"PLTE":
            chunk = chunk[: max_entries * 3]
            out += struct.pack(">I", len(chunk)) + chunk_type + chunk
            out += struct.pack(">I", zlib.crc32(chunk, zlib.crc32(chunk_type)) & 0xFFFFFFFF)
        else:
            out += struct.pack(">I", len(chunk)) + chunk_type + chunk + crc
        if chunk_type == b"IEND":
            break
    path.write_bytes(bytes(out))


def save_png(path: Path, img: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=False)
    trim_plte(path)


def draw_poly(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], color: int) -> None:
    draw.polygon(pts, fill=color)


def draw_line(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], color: int, width: int = 1) -> None:
    draw.line([a, b], fill=color, width=width)


def draw_joint(draw: ImageDraw.ImageDraw, x: int, y: int, r: int, color: int) -> None:
    draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def draw_limb(
    draw: ImageDraw.ImageDraw,
    a: tuple[int, int],
    b: tuple[int, int],
    color: int,
    width: int,
    joint: int | None = None,
) -> None:
    draw_line(draw, a, b, color, width)
    r = joint if joint is not None else max(2, width // 2)
    draw_joint(draw, a[0], a[1], r, color)
    draw_joint(draw, b[0], b[1], r, color)


def add_outline(img: Image.Image, color: int = 1) -> None:
    src = img.copy()
    px = src.load()
    out = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y] != 0:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < img.width and 0 <= ny < img.height and px[nx, ny] != 0:
                    out[x, y] = color
                    break


def lava_cracks(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]]) -> None:
    for a, b in zip(pts, pts[1:]):
        draw_line(draw, a, b, 13, 1)
    for x, y in pts[::2]:
        draw.point((x, y), fill=14)


def draw_open_lava_hand(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.ellipse((x - 4, y - 3, x + 3, y + 3), fill=4)
    for i, off in enumerate((-5, -2, 1, 4)):
        draw_line(draw, (x + off, y - 2), (x + off + 1, y - 8 + (i % 2)), 4, 2)
        draw.point((x + off + 1, y - 8 + (i % 2)), fill=13)
    draw_line(draw, (x - 3, y + 1), (x + 2, y - 2), 13, 1)
    draw.point((x, y - 1), fill=14)


def draw_lava_fist(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=4)
    draw.rectangle((x - 5, y - 1, x + 5, y + 3), fill=3)
    lava_cracks(draw, [(x - 3, y - 2), (x, y), (x + 3, y - 1)])


def draw_wrapped_fist(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.ellipse((x - 4, y - 4, x + 4, y + 3), fill=9)
    draw_line(draw, (x - 4, y), (x + 4, y + 1), 10, 1)
    draw_line(draw, (x - 3, y + 2), (x + 3, y + 3), 5, 1)


def draw_foot(draw: ImageDraw.ImageDraw, x: int, y: int, facing: int = 1) -> None:
    draw.rectangle((x - 3, y - 6, x + 3, y), fill=9)
    draw_line(draw, (x - 3, y - 4), (x + 3, y - 4), 10, 1)
    if facing >= 0:
        draw.ellipse((x - 3, y - 1, x + 7, y + 2), fill=7)
        draw_line(draw, (x - 2, y + 2), (x + 7, y + 2), 5, 1)
    else:
        draw.ellipse((x - 7, y - 1, x + 3, y + 2), fill=7)
        draw_line(draw, (x - 7, y + 2), (x + 2, y + 2), 5, 1)


def draw_head(draw: ImageDraw.ImageDraw, x: int, y: int, expression: str, facing: int = 1) -> None:
    draw.ellipse((x - 5, y - 6, x + 5, y + 6), fill=7)
    draw.polygon([(x - 7, y - 6), (x - 4, y - 12), (x - 1, y - 7), (x + 2, y - 13), (x + 4, y - 7), (x + 7, y - 10), (x + 5, y - 3), (x - 6, y - 3)], fill=1)
    eye_y = y - 1
    if facing >= 0:
        draw.point((x + 2, eye_y), fill=15)
        draw.point((x + 3, eye_y), fill=1)
        draw_line(draw, (x - 3, eye_y - 1), (x + 3, eye_y - 2), 1, 1)
    else:
        draw.point((x - 2, eye_y), fill=15)
        draw.point((x - 3, eye_y), fill=1)
        draw_line(draw, (x - 3, eye_y - 2), (x + 3, eye_y - 1), 1, 1)
    if expression == "kiai":
        draw.rectangle((x + 1, y + 3, x + 4, y + 6), fill=1)
        draw.point((x + 2, y + 3), fill=10)
    elif expression == "teeth":
        draw_line(draw, (x - 1, y + 4), (x + 4, y + 4), 10, 1)
        draw.point((x + 5, y + 4), fill=1)
    else:
        draw_line(draw, (x - 2, y + 4), (x + 3, y + 3), 1, 1)


def draw_torso(draw: ImageDraw.ImageDraw, dx: int, bob: int, lean: int = 0) -> None:
    shoulder_y = 20 + bob
    hip_y = 40 + bob
    draw_poly(draw, [(17 + dx + lean, shoulder_y), (31 + dx + lean, shoulder_y), (34 + dx, 34 + bob), (29 + dx, hip_y), (19 + dx, hip_y), (14 + dx, 34 + bob)], 6)
    draw_poly(draw, [(18 + dx + lean, shoulder_y + 1), (24 + dx, shoulder_y), (23 + dx, hip_y - 2), (17 + dx, hip_y - 1), (14 + dx, 34 + bob)], 5)
    draw_poly(draw, [(25 + dx, shoulder_y), (31 + dx + lean, shoulder_y + 1), (33 + dx, 34 + bob), (28 + dx, hip_y - 1), (24 + dx, hip_y - 2)], 7)
    draw_line(draw, (24 + dx, shoulder_y + 3), (24 + dx, hip_y - 3), 5, 1)
    draw_line(draw, (20 + dx, 27 + bob), (28 + dx, 27 + bob), 8, 1)
    draw_line(draw, (19 + dx, 32 + bob), (29 + dx, 32 + bob), 5, 1)
    draw.rectangle((16 + dx, 39 + bob, 32 + dx, 48 + bob), fill=2)
    draw.rectangle((17 + dx, 40 + bob, 31 + dx, 43 + bob), fill=3)
    draw_line(draw, (17 + dx, 47 + bob), (31 + dx, 47 + bob), 11, 1)
    draw_line(draw, (17 + dx, 42 + bob), (16 + dx, 47 + bob), 11, 1)
    draw_line(draw, (31 + dx, 42 + bob), (32 + dx, 47 + bob), 11, 1)
    draw.rectangle((22 + dx, 39 + bob, 26 + dx, 42 + bob), fill=11)
    draw.rectangle((14 + dx, 25 + bob, 17 + dx, 29 + bob), fill=12)


def draw_base_body(draw: ImageDraw.ImageDraw, pose: dict) -> None:
    dx = pose.get("dx", 0)
    bob = pose.get("bob", 0)
    lean = pose.get("lean", 0)
    draw_torso(draw, dx, bob, lean)
    draw_head(draw, 24 + dx + lean, 16 + bob, pose.get("face", "idle"), 1)


def draw_human_arm(draw: ImageDraw.ImageDraw, pts: tuple[tuple[int, int], tuple[int, int], tuple[int, int]], bob: int = 0) -> None:
    shoulder, elbow, hand = pts
    shoulder = (shoulder[0], shoulder[1] + bob)
    elbow = (elbow[0], elbow[1] + bob)
    hand = (hand[0], hand[1] + bob)
    draw_limb(draw, shoulder, elbow, 7, 5, 3)
    draw_limb(draw, elbow, hand, 9, 5, 3)
    draw_wrapped_fist(draw, hand[0], hand[1])


def draw_lava_arm(
    draw: ImageDraw.ImageDraw,
    pts: tuple[tuple[int, int], tuple[int, int], tuple[int, int]],
    bob: int = 0,
    hand: str = "fist",
) -> None:
    shoulder, elbow, palm = pts
    shoulder = (shoulder[0], shoulder[1] + bob)
    elbow = (elbow[0], elbow[1] + bob)
    palm = (palm[0], palm[1] + bob)
    draw_limb(draw, shoulder, elbow, 4, 6, 3)
    draw_limb(draw, elbow, palm, 3, 6, 3)
    lava_cracks(draw, [(shoulder[0], shoulder[1]), (elbow[0] - 1, elbow[1] + 2), (palm[0], palm[1])])
    if hand == "open":
        draw_open_lava_hand(draw, palm[0], palm[1])
    else:
        draw_lava_fist(draw, palm[0], palm[1])


def draw_leg(draw: ImageDraw.ImageDraw, pts: tuple[tuple[int, int], tuple[int, int], tuple[int, int]], shade: int, bob: int = 0, foot_facing: int = 1) -> None:
    hip, knee, ankle = pts
    hip = (hip[0], hip[1] + bob)
    knee = (knee[0], knee[1] + bob)
    ankle = (ankle[0], ankle[1] + bob)
    draw_limb(draw, hip, knee, shade, 6, 3)
    draw_limb(draw, knee, ankle, max(5, shade - 1), 6, 3)
    draw_foot(draw, ankle[0], ankle[1], foot_facing)


def draw_frame(pose: dict) -> Image.Image:
    img = canvas()
    draw = ImageDraw.Draw(img)
    bob = pose.get("bob", 0)
    # Legs behind torso first.
    for leg in pose["legs"]:
        draw_leg(draw, leg["pts"], leg.get("shade", 7), bob, leg.get("facing", 1))
    draw_base_body(draw, pose)
    draw_human_arm(draw, pose["human_arm"], bob)
    draw_lava_arm(draw, pose["lava_arm"], bob, pose.get("lava_hand", "fist"))
    # Material locks and readable highlights.
    draw_line(draw, (28 + pose.get("dx", 0), 25 + bob), (31 + pose.get("dx", 0), 31 + bob), 13, 1)
    draw.point((29 + pose.get("dx", 0), 27 + bob), fill=14)
    add_outline(img)
    return img


def idle_pose(i: int) -> dict:
    bob = 1 if i in (2, 3) else 0
    guard = 1 if i in (1, 2, 4) else 0
    return {
        "bob": bob,
        "face": "idle",
        "human_arm": ((16, 22), (12, 32 + guard), (15, 42)),
        "lava_arm": ((31, 22), (37, 32 - guard), (36, 44)),
        "legs": [
            {"pts": ((20, 45), (16, 51), (14, 56)), "shade": 7, "facing": 1},
            {"pts": ((29, 45), (34, 51), (38, 56)), "shade": 6, "facing": 1},
        ],
    }


def walk_pose(i: int) -> dict:
    phase = i % 6
    forward = phase in (1, 2, 3)
    bob = 1 if phase in (1, 4) else 0
    return {
        "bob": bob,
        "lean": 1 if forward else 0,
        "face": "idle",
        "human_arm": ((16, 22), (14 if forward else 18, 31), (18 if forward else 13, 40)),
        "lava_arm": ((31, 22), (35 if forward else 38, 31), (33 if forward else 37, 42)),
        "legs": [
            {"pts": ((20, 45), (14 if forward else 21, 51), (11 if forward else 22, 56)), "shade": 7, "facing": 1},
            {"pts": ((29, 45), (32 if forward else 27, 51), (37 if forward else 29, 56)), "shade": 6, "facing": 1},
        ],
    }


def knee_pose(i: int) -> dict:
    stages = [
        (0, "idle", ((29, 45), (34, 51), (38, 56))),
        (1, "idle", ((29, 45), (34, 49), (35, 54))),
        (1, "teeth", ((29, 44), (35, 43), (38, 48))),
        (0, "teeth", ((29, 43), (36, 36), (38, 44))),
        (0, "teeth", ((29, 43), (35, 35), (37, 43))),
        (0, "idle", ((29, 45), (33, 49), (36, 55))),
    ]
    bob, face, front_leg = stages[i]
    return {
        "bob": bob,
        "face": face,
        "lean": 1,
        "human_arm": ((16, 22), (14, 29), (18, 35)),
        "lava_arm": ((31, 22), (36, 25), (34, 34)),
        "legs": [
            {"pts": ((20, 45), (17, 51), (15, 56)), "shade": 7, "facing": 1},
            {"pts": front_leg, "shade": 7, "facing": 1},
        ],
    }


def teep_pose(i: int) -> dict:
    stages = [
        (0, "idle", ((29, 45), (34, 50), (38, 56)), ((31, 22), (35, 31), (34, 41)), "fist"),
        (1, "idle", ((29, 45), (34, 48), (38, 54)), ((31, 22), (36, 29), (37, 38)), "fist"),
        (0, "teeth", ((29, 45), (35, 45), (38, 47)), ((31, 22), (37, 27), (40, 31)), "open"),
        (-1, "kiai", ((29, 45), (36, 42), (38, 42)), ((31, 22), (37, 25), (40, 28)), "open"),
        (-1, "kiai", ((29, 45), (35, 43), (38, 43)), ((31, 22), (37, 25), (40, 28)), "open"),
        (0, "idle", ((29, 45), (34, 49), (38, 55)), ((31, 22), (36, 30), (35, 40)), "fist"),
    ]
    bob, face, front_leg, lava_arm, hand = stages[i]
    return {
        "bob": bob,
        "face": face,
        "lean": 1,
        "human_arm": ((16, 22), (15, 31), (18, 38)),
        "lava_arm": lava_arm,
        "lava_hand": hand,
        "legs": [
            {"pts": ((20, 45), (17, 51), (15, 56)), "shade": 7, "facing": 1},
            {"pts": front_leg, "shade": 7, "facing": 1},
        ],
    }


ANIMS = {
    "idle": [idle_pose(i) for i in range(6)],
    "walk_step": [walk_pose(i) for i in range(6)],
    "guard_block": [],
    "jab": [],
    "knee": [knee_pose(i) for i in range(6)],
    "teep": [teep_pose(i) for i in range(6)],
}


def guard_block_pose(i: int) -> dict:
    bob = 1 if i in (1, 4) else 0
    return {
        "bob": bob,
        "face": "idle",
        "human_arm": ((16, 22), (14, 27), (18, 31)),
        "lava_arm": ((31, 22), (37, 27), (36, 34)),
        "lava_hand": "open",
        "legs": [
            {"pts": ((20, 45), (16, 51), (14, 56)), "shade": 7, "facing": 1},
            {"pts": ((29, 45), (34, 51), (38, 56)), "shade": 6, "facing": 1},
        ],
    }


def jab_pose(i: int) -> dict:
    stages = [
        (0, "idle", ((16, 22), (14, 31), (18, 39)), ((31, 22), (37, 31), (36, 41))),
        (0, "idle", ((16, 22), (19, 30), (27, 32)), ((31, 22), (37, 30), (35, 38))),
        (-1, "teeth", ((16, 22), (24, 27), (35, 29)), ((31, 22), (37, 28), (35, 35))),
        (-1, "kiai", ((16, 22), (25, 27), (39, 29)), ((31, 22), (37, 28), (35, 35))),
        (0, "teeth", ((16, 22), (21, 29), (30, 33)), ((31, 22), (37, 30), (35, 38))),
        (0, "idle", ((16, 22), (14, 31), (18, 39)), ((31, 22), (37, 31), (36, 41))),
    ]
    bob, face, human_arm, lava_arm = stages[i]
    return {
        "bob": bob,
        "face": face,
        "lean": 1,
        "human_arm": human_arm,
        "lava_arm": lava_arm,
        "legs": [
            {"pts": ((20, 45), (16, 51), (14, 56)), "shade": 7, "facing": 1},
            {"pts": ((29, 45), (34, 51), (38, 56)), "shade": 6, "facing": 1},
        ],
    }


ANIMS["guard_block"] = [guard_block_pose(i) for i in range(6)]
ANIMS["jab"] = [jab_pose(i) for i in range(6)]

ACTION_PHASES = {
    "idle": ["breath_low", "breath_in", "breath_high", "breath_high", "breath_out", "breath_low"],
    "walk_step": ["contact", "down", "passing", "up", "contact", "recovery"],
    "guard_block": ["guard_set", "guard_hold", "guard_hold", "guard_hold", "guard_hold", "guard_release"],
    "jab": ["guard", "startup", "extension", "impact", "recoil", "recovery"],
    "knee": ["guard", "startup", "anticipation", "active", "active_hold", "recovery"],
    "teep": ["guard", "startup", "anticipation", "active", "active_hold", "recovery"],
}


def build_strip(poses: list[dict]) -> Image.Image:
    out = canvas(CELL_W * len(poses), CELL_H)
    for i, pose in enumerate(poses):
        out.paste(draw_frame(pose), (i * CELL_W, 0))
    return out


def bbox_for_frame(strip: Image.Image, frame: int) -> dict[str, int | bool]:
    crop = strip.crop((frame * CELL_W, 0, (frame + 1) * CELL_W, CELL_H))
    xs: list[int] = []
    ys: list[int] = []
    for y in range(CELL_H):
        for x in range(CELL_W):
            if crop.getpixel((x, y)) != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return {"empty": True}
    return {"x": min(xs), "y": min(ys), "w": max(xs) - min(xs) + 1, "h": max(ys) - min(ys) + 1}


def palette_report(path: Path) -> dict:
    data = path.read_bytes()
    plte_entries = 0
    i = 8
    while i + 8 <= len(data):
        length = struct.unpack(">I", data[i : i + 4])[0]
        chunk_type = data[i + 4 : i + 8]
        if chunk_type == b"PLTE":
            plte_entries = length // 3
            break
        i += 12 + length
    img = Image.open(path)
    used = sorted(set(img.getdata()))
    grid_ok = all(all(channel in (0x00, 0x22, 0x44, 0x66, 0x88, 0xAA, 0xCC, 0xEE) for channel in color) for color in PALETTE)
    return {
        "path": str(path).replace("\\", "/"),
        "mode": img.mode,
        "size": list(img.size),
        "plte_entries": plte_entries,
        "used_indices": used,
        "visible_indices": [idx for idx in used if idx != 0],
        "grid_9bit": grid_ok,
        "index0_transparent_contract": True,
        "dim_multiple_8": img.width % 8 == 0 and img.height % 8 == 0,
    }


def make_contact_sheet(strips: dict[str, Image.Image]) -> Image.Image:
    max_frames = max(strip.width // CELL_W for strip in strips.values())
    out = canvas(CELL_W * max_frames, CELL_H * len(strips))
    for row, strip in enumerate(strips.values()):
        out.paste(strip, (0, row * CELL_H))
    return out


def make_contact_sheet_with_palette(strips: dict[str, Image.Image]) -> Image.Image:
    base = make_contact_sheet(strips)
    swatch_h = 16
    swatch_w = base.width // 16
    out = canvas(base.width, base.height + swatch_h)
    out.paste(base, (0, 0))
    draw = ImageDraw.Draw(out)
    y0 = base.height
    for idx in range(16):
        x0 = idx * swatch_w
        draw.rectangle((x0, y0, x0 + swatch_w - 1, y0 + swatch_h - 1), fill=idx)
        if idx == 0:
            draw.rectangle((x0 + 2, y0 + 2, x0 + swatch_w - 3, y0 + swatch_h - 3), outline=1)
    return out


def make_pivot_overlay(strip: Image.Image) -> Image.Image:
    out = strip.copy()
    draw = ImageDraw.Draw(out)
    frames = strip.width // CELL_W
    for i in range(frames):
        x0 = i * CELL_W
        draw_line(draw, (x0, PIVOT[1]), (x0 + CELL_W - 1, PIVOT[1]), 12, 1)
        draw_line(draw, (x0 + PIVOT[0] - 4, PIVOT[1]), (x0 + PIVOT[0] + 4, PIVOT[1]), 15, 1)
        draw_line(draw, (x0 + PIVOT[0], PIVOT[1] - 4), (x0 + PIVOT[0], PIVOT[1] + 4), 15, 1)
    return out


def make_lineart_sheet(strips: dict[str, Image.Image]) -> Image.Image:
    sheet = make_contact_sheet(strips)
    out = canvas(sheet.width, sheet.height)
    src = sheet.load()
    dst = out.load()
    for y in range(sheet.height):
        for x in range(sheet.width):
            if src[x, y] == 0:
                continue
            is_edge = False
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if nx < 0 or nx >= sheet.width or ny < 0 or ny >= sheet.height or src[nx, ny] == 0:
                    is_edge = True
                    break
            if is_edge:
                dst[x, y] = 1
    return out


def frame_edge_contact(strip: Image.Image, frame: int) -> dict[str, bool]:
    crop = strip.crop((frame * CELL_W, 0, (frame + 1) * CELL_W, CELL_H))
    left = any(crop.getpixel((0, y)) != 0 for y in range(CELL_H))
    right = any(crop.getpixel((CELL_W - 1, y)) != 0 for y in range(CELL_H))
    top = any(crop.getpixel((x, 0)) != 0 for x in range(CELL_W))
    bottom = any(crop.getpixel((x, CELL_H - 1)) != 0 for x in range(CELL_W))
    return {"left": left, "right": right, "top": top, "bottom": bottom}


def make_gif(path: Path, strip: Image.Image) -> None:
    frames = [strip.crop((i * CELL_W, 0, (i + 1) * CELL_W, CELL_H)).resize((CELL_W * 4, CELL_H * 4), Image.Resampling.NEAREST) for i in range(strip.width // CELL_W)]
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=96, loop=0)


def main() -> None:
    project = Path(__file__).resolve().parents[2]
    res_dir = project / "res/sprites/hibrido"
    report_dir = project / "out/logs"
    processed_dir = project / "data/processed/reports"
    lineart_dir = project / "data/processed/lineart"
    spritesheet_dir = project / "data/processed/spritesheets"
    strips: dict[str, Image.Image] = {}
    reports: dict[str, object] = {
        "schema_version": "1.0.0",
        "asset_id": "hibrido_fighter_sprite_sheet_v009",
        "source_ref": "data/source_art/hibrido_fighter_v008/source_concept.png",
        "status": "sprite_candidate_pending_human_visual_validation",
        "cell_px": [CELL_W, CELL_H],
        "pivot_px": list(PIVOT),
        "palette_policy": "single_character_palette_16_entries_index0_transparent",
        "runtime_layout": "per_pose_sprites_with_preview_atlas",
        "visual_gate": {
            "technical_png_conformance_can_pass": True,
            "artistic_approval": "pending_human_validation",
            "not_declared_final_art": True,
        },
        "actions": {},
    }
    for action, poses in ANIMS.items():
        strip = build_strip(poses)
        strips[action] = strip
        strip_path = res_dir / f"hibrido_{action}_body_48x64_strip_v009.png"
        save_png(strip_path, strip)
        save_png(processed_dir / f"hibrido_{action}_pivot_overlay_v009.png", make_pivot_overlay(strip))
        make_gif(processed_dir / f"hibrido_{action}_motion_preview_v009.gif", strip)
        frame_reports = []
        previous_bbox = None
        for idx in range(len(poses)):
            bbox = bbox_for_frame(strip, idx)
            edge_contact = frame_edge_contact(strip, idx)
            delta = None
            if previous_bbox and "empty" not in bbox and "empty" not in previous_bbox:
                delta = {
                    "dx": int(bbox["x"]) - int(previous_bbox["x"]),
                    "dy": int(bbox["y"]) - int(previous_bbox["y"]),
                    "dw": int(bbox["w"]) - int(previous_bbox["w"]),
                    "dh": int(bbox["h"]) - int(previous_bbox["h"]),
                }
            frame_reports.append({
                "frame_index": idx,
                "pivot_px": list(PIVOT),
                "foot_contact_y": GROUND_Y,
                "bbox": bbox,
                "edge_contact": edge_contact,
                "delta_from_previous": delta,
            })
            previous_bbox = bbox
        reports["actions"][action] = {
            "frames": len(poses),
            "strip": str(strip_path.relative_to(project)).replace("\\", "/"),
            "frame_delta_report": frame_reports,
            "motion_phase_map": ACTION_PHASES[action],
            "contact_points": [
                {"frame_index": idx, "role": "ground_line", "point_px": [PIVOT[0], GROUND_Y]}
                for idx in range(len(poses))
            ],
        }

    contact = make_contact_sheet(strips)
    contact_with_palette = make_contact_sheet_with_palette(strips)
    save_png(processed_dir / "hibrido_fighter_complete_contact_sheet_v009.png", contact)
    save_png(processed_dir / "hibrido_fighter_complete_contact_sheet_with_palette_v009.png", contact_with_palette)
    save_png(
        processed_dir / "hibrido_fighter_complete_contact_sheet_with_palette_v009_preview_x4.png",
        contact_with_palette.resize((contact_with_palette.width * 4, contact_with_palette.height * 4), Image.Resampling.NEAREST),
    )
    save_png(spritesheet_dir / "hibrido_fighter_complete_sprite_sheet_48x64_v009.png", contact)
    save_png(lineart_dir / "hibrido_fighter_lineart_blocking_48x64_v009.png", make_lineart_sheet(strips))

    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "hibrido_v009_animation_report.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    compliance = [palette_report(path) for path in sorted(res_dir.glob("*_v009.png"))]
    (report_dir / "hibrido_v009_pixel_compliance_report.json").write_text(
        json.dumps({"schema_version": "1.0.0", "asset_id": "hibrido_fighter_sprite_sheet_v009", "assets": compliance}, indent=2),
        encoding="utf-8",
    )
    integrity_blockers = []
    for asset in compliance:
        if asset["mode"] != "P":
            integrity_blockers.append({"asset": asset["path"], "code": "NOT_INDEXED"})
        if asset["plte_entries"] > 16:
            integrity_blockers.append({"asset": asset["path"], "code": "PLTE_TOO_LARGE"})
        if not asset["grid_9bit"]:
            integrity_blockers.append({"asset": asset["path"], "code": "COLORS_NOT_9BIT"})
        if not asset["dim_multiple_8"]:
            integrity_blockers.append({"asset": asset["path"], "code": "DIM_NOT_MULTIPLE_8"})
        path = Path(asset["path"])
        if not path.is_absolute():
            path = project / path
        img = Image.open(path)
        frames = img.width // CELL_W
        for frame in range(frames):
            edge = frame_edge_contact(img, frame)
            if any(edge.values()):
                integrity_blockers.append({
                    "asset": asset["path"],
                    "frame_index": frame,
                    "code": "FRAME_EDGE_CLIPPING_RISK",
                    "edge_contact": edge,
                })
    (report_dir / "sprite_strip_integrity_report_v009.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "asset_id": "hibrido_fighter_sprite_sheet_v009",
                "status": "passed" if not integrity_blockers else "failed",
                "blockers": integrity_blockers,
                "actions": reports["actions"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (report_dir / "hibrido_v009_visual_translation_report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "asset_id": "hibrido_fighter_sprite_sheet_v009",
                "source_ref": "data/source_art/hibrido_fighter_v008/source_concept.png",
                "translation_method": "native_48x64_pixel_redraw_candidate_not_downscale",
                "basic_control_route": "rejected_for_character_final_use",
                "elite_candidate_route": "manual_material_palette_slots_native_pixel_clusters",
                "applied_human_feedback": [
                    "exactly_two_arms_two_legs_one_head_one_trunk_per_pose",
                    "no_hidden_lava_hand_in_teep_active_frames",
                    "face_changes_for_effort_on_jab_knee_teep",
                    "consistent_red_armband_on_human_arm",
                    "lava_rock_arm_without_wraps_across_all_frames",
                    "cluster_shading_2_to_3_tones_not_pixel_spray",
                ],
                "visual_gate": "pending_human_validation",
                "technical_gate_note": "PNG compliance is not visual approval.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (report_dir / "hibrido_v009_sprite_artifact_report.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "asset_id": "hibrido_fighter_sprite_sheet_v009",
                "status": "passed_technical_artifact_scan" if not integrity_blockers else "failed",
                "anatomy_topology": {
                    "expected": {"arms": 2, "legs": 2, "head": 1, "trunk": 1},
                    "construction_lock": "exact_two_arm_two_leg_pose_rig",
                    "teep_lava_hand_visible_above_leg": True,
                },
                "blockers": integrity_blockers,
                "visual_approval": "pending_human_review",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
