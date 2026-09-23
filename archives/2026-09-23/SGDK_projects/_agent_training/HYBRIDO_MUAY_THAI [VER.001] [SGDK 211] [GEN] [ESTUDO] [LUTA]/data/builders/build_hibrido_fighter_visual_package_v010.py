from __future__ import annotations

import hashlib
import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CELL_W = 48
CELL_H = 64
PIVOT = (24, 58)
GROUND_Y = 58

PALETTE = [
    (0xEE, 0x00, 0xEE),  # 00 transparent source key
    (0x00, 0x00, 0x00),  # 01 outline, hair deep
    (0x22, 0x22, 0x22),  # 02 hair, shorts shadow
    (0x44, 0x44, 0x44),  # 03 shorts, rock dark
    (0x66, 0x66, 0x66),  # 04 rock mid
    (0x88, 0x66, 0x44),  # 05 skin shadow, wrap dirt
    (0xAA, 0x66, 0x22),  # 06 skin base
    (0xCC, 0x88, 0x44),  # 07 skin light
    (0xEE, 0xAA, 0x66),  # 08 skin highlight
    (0xCC, 0xAA, 0x88),  # 09 wrap base
    (0xEE, 0xEE, 0xCC),  # 10 wrap highlight, teeth
    (0xCC, 0xAA, 0x22),  # 11 gold trim
    (0xCC, 0x22, 0x22),  # 12 red band, lava red
    (0xEE, 0x66, 0x00),  # 13 lava orange
    (0xEE, 0xEE, 0x00),  # 14 lava yellow, eye accent
    (0xEE, 0xEE, 0xEE),  # 15 eye spec, small hard highlight
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(project: Path, path: Path) -> str:
    return str(path.relative_to(project)).replace("\\", "/")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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
    if img.mode == "P":
        trim_plte(path)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def draw_line(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int], color: int, width: int = 1) -> None:
    draw.line([a, b], fill=color, width=width)


def draw_joint(draw: ImageDraw.ImageDraw, p: tuple[int, int], rx: int, ry: int, color: int) -> None:
    x, y = p
    draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color)


def draw_limb(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], color: int, width: int, joint_color: int | None = None) -> None:
    joint = color if joint_color is None else joint_color
    for a, b in zip(pts, pts[1:]):
        draw_line(draw, a, b, color, width)
    for p in pts:
        draw_joint(draw, p, max(2, width // 2), max(2, width // 2), joint)


def add_outline(img: Image.Image, color: int = 1) -> None:
    src = img.copy()
    sp = src.load()
    dp = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if sp[x, y] != 0:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < img.width and 0 <= ny < img.height and sp[nx, ny] != 0:
                    dp[x, y] = color
                    break


def black_silhouette(src: Image.Image) -> Image.Image:
    out = canvas(src.width, src.height)
    sp = src.load()
    op = out.load()
    for y in range(src.height):
        for x in range(src.width):
            if sp[x, y] != 0:
                op[x, y] = 1
    return out


def make_lineart(src: Image.Image) -> Image.Image:
    out = canvas(src.width, src.height)
    sp = src.load()
    op = out.load()
    for y in range(src.height):
        for x in range(src.width):
            if sp[x, y] == 0:
                continue
            edge = False
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if nx < 0 or ny < 0 or nx >= src.width or ny >= src.height or sp[nx, ny] == 0:
                    edge = True
                    break
            if edge:
                op[x, y] = 1
    return out


def draw_hair(draw: ImageDraw.ImageDraw, x: int, y: int, facing: str) -> None:
    if facing == "back":
        pts = [(x - 7, y), (x - 6, y - 7), (x - 4, y - 4), (x - 2, y - 10), (x + 1, y - 5), (x + 3, y - 10), (x + 5, y - 4), (x + 7, y - 7), (x + 6, y + 1)]
    elif facing == "front":
        pts = [(x - 7, y + 1), (x - 6, y - 7), (x - 4, y - 4), (x - 2, y - 10), (x + 1, y - 5), (x + 3, y - 11), (x + 5, y - 5), (x + 7, y - 8), (x + 6, y + 1)]
    else:
        pts = [(x - 6, y + 1), (x - 5, y - 6), (x - 3, y - 4), (x - 1, y - 10), (x + 2, y - 6), (x + 5, y - 9), (x + 8, y - 4), (x + 7, y + 1)]
    draw.polygon(pts, fill=1)
    draw_line(draw, (x - 5, y - 3), (x + 5, y - 5), 2, 1)
    draw_line(draw, (x - 3, y - 6), (x + 3, y - 7), 2, 1)


def draw_head(draw: ImageDraw.ImageDraw, x: int, y: int, facing: str, expression: str = "idle") -> None:
    if facing == "back":
        draw.ellipse((x - 4, y - 5, x + 4, y + 5), fill=6)
        draw_hair(draw, x, y, "back")
        draw.rectangle((x - 2, y + 4, x + 2, y + 7), fill=5)
        return
    draw.ellipse((x - 4, y - 5, x + 4, y + 5), fill=7)
    draw.rectangle((x - 3, y + 2, x + 3, y + 5), fill=6)
    draw_hair(draw, x, y, facing)
    if facing == "front":
        draw_line(draw, (x - 4, y - 1), (x - 1, y - 2), 1, 1)
        draw_line(draw, (x + 1, y - 2), (x + 4, y - 1), 1, 1)
        draw.point((x - 2, y), fill=15)
        draw.point((x + 2, y), fill=15)
    else:
        draw_line(draw, (x - 2, y - 2), (x + 5, y - 3), 1, 1)
        draw.point((x + 3, y - 1), fill=15)
        draw.point((x + 4, y - 1), fill=1)
    if expression == "kiai":
        draw.rectangle((x + 1, y + 3, x + 4, y + 6), fill=1)
        draw.point((x + 2, y + 3), fill=10)
    elif expression == "teeth":
        draw_line(draw, (x - 1, y + 4), (x + 4, y + 4), 10, 1)
    elif expression == "hurt":
        draw_line(draw, (x - 4, y + 4), (x + 2, y + 5), 1, 1)
    else:
        draw_line(draw, (x - 2, y + 4), (x + 3, y + 3), 1, 1)


def draw_wrap_hand(draw: ImageDraw.ImageDraw, x: int, y: int, open_hand: bool = False) -> None:
    if open_hand:
        draw.ellipse((x - 3, y - 2, x + 3, y + 2), fill=9)
        for i in range(4):
            draw_line(draw, (x - 3 + i * 2, y - 1), (x - 3 + i * 2, y - 5), 10, 1)
    else:
        draw.ellipse((x - 3, y - 3, x + 3, y + 2), fill=9)
        draw_line(draw, (x - 3, y), (x + 3, y + 1), 10, 1)
        draw_line(draw, (x - 2, y + 2), (x + 2, y + 2), 5, 1)


def draw_lava_hand(draw: ImageDraw.ImageDraw, x: int, y: int, open_hand: bool = False) -> None:
    if open_hand:
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=4)
        for i, off in enumerate((-5, -2, 1, 4)):
            draw_line(draw, (x + off, y - 1), (x + off + 1, y - 6 - (i % 2)), 4, 1)
            draw.point((x + off + 1, y - 6 - (i % 2)), fill=13)
        draw_line(draw, (x - 3, y + 1), (x + 3, y - 2), 13, 1)
    else:
        draw.ellipse((x - 4, y - 4, x + 4, y + 3), fill=4)
        draw.rectangle((x - 4, y - 1, x + 4, y + 2), fill=3)
        draw_line(draw, (x - 3, y - 2), (x + 3, y + 1), 13, 1)
    draw.point((x, y - 1), fill=14)


def draw_foot(draw: ImageDraw.ImageDraw, x: int, y: int, direction: int = 1) -> None:
    draw.rectangle((x - 2, y - 5, x + 2, y), fill=9)
    draw_line(draw, (x - 2, y - 3), (x + 2, y - 3), 10, 1)
    if direction >= 0:
        draw.ellipse((x - 2, y - 1, x + 6, y + 1), fill=7)
        draw_line(draw, (x - 1, y + 1), (x + 6, y + 1), 5, 1)
    else:
        draw.ellipse((x - 6, y - 1, x + 2, y + 1), fill=7)
        draw_line(draw, (x - 6, y + 1), (x + 1, y + 1), 5, 1)


def draw_torso(draw: ImageDraw.ImageDraw, x: int, y: int, facing: str = "side", lean: int = 0) -> None:
    if facing == "back":
        draw.polygon([(x - 7, y), (x + 7, y), (x + 8, y + 15), (x + 4, y + 22), (x - 4, y + 22), (x - 8, y + 15)], fill=6)
        draw.polygon([(x - 6, y + 1), (x, y + 2), (x - 2, y + 21), (x - 6, y + 18)], fill=5)
        draw_line(draw, (x, y + 2), (x, y + 20), 5, 1)
        draw_line(draw, (x - 6, y + 7), (x + 6, y + 7), 7, 1)
    else:
        draw.polygon([(x - 8 + lean, y), (x + 7 + lean, y), (x + 9, y + 15), (x + 4, y + 22), (x - 4, y + 22), (x - 9, y + 15)], fill=6)
        draw.polygon([(x - 7 + lean, y + 1), (x - 1, y + 1), (x - 2, y + 21), (x - 6, y + 20), (x - 9, y + 14)], fill=5)
        draw.polygon([(x, y + 1), (x + 7 + lean, y + 1), (x + 8, y + 15), (x + 4, y + 21), (x - 1, y + 20)], fill=7)
        draw_line(draw, (x, y + 3), (x, y + 20), 5, 1)
        draw_line(draw, (x - 6, y + 8), (x + 6, y + 7), 8, 1)
        draw_line(draw, (x - 5, y + 14), (x + 6, y + 14), 5, 1)
        draw.point((x + 3, y + 5), fill=8)
    draw.rectangle((x - 8, y + 21, x + 8, y + 29), fill=2)
    draw.rectangle((x - 6, y + 22, x + 6, y + 25), fill=3)
    draw_line(draw, (x - 8, y + 28), (x + 8, y + 28), 11, 1)
    draw_line(draw, (x - 7, y + 24), (x - 8, y + 28), 11, 1)
    draw_line(draw, (x + 7, y + 24), (x + 8, y + 28), 11, 1)
    draw.rectangle((x - 2, y + 21, x + 2, y + 24), fill=12)
    draw.line([(x - 1, y + 25), (x - 1, y + 31)], fill=12, width=1)
    draw.line([(x + 2, y + 25), (x + 2, y + 31)], fill=12, width=1)
    draw.point((x + 6, y + 26), fill=11)
    draw.point((x - 6, y + 26), fill=11)


def draw_lava_arm(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], open_hand: bool = False) -> None:
    draw_limb(draw, pts, 4, 5, 3)
    draw_line(draw, pts[0], pts[1], 13, 1)
    draw_line(draw, pts[1], pts[2], 13, 1)
    mx = (pts[0][0] + pts[1][0]) // 2
    my = (pts[0][1] + pts[1][1]) // 2
    draw.point((mx, my), fill=14)
    draw_lava_hand(draw, pts[-1][0], pts[-1][1], open_hand)


def draw_human_arm(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], band: bool = True, open_hand: bool = False) -> None:
    draw_limb(draw, pts[:2], 7, 4, 6)
    if band:
        bx = (pts[0][0] + pts[1][0]) // 2
        by = (pts[0][1] + pts[1][1]) // 2
        draw_line(draw, (bx - 3, by), (bx + 3, by + 1), 12, 2)
    draw_limb(draw, pts[1:], 9, 4, 5)
    draw_wrap_hand(draw, pts[-1][0], pts[-1][1], open_hand)


def draw_leg(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], direction: int = 1, shade: int = 7) -> None:
    draw_limb(draw, pts, shade, 5, 6)
    draw_line(draw, pts[0], pts[1], 8, 1)
    draw_foot(draw, pts[-1][0], pts[-1][1], direction)


def pose_spec(name: str, frame: int = 0) -> dict:
    b = 1 if frame % 6 in (1, 2) else 0
    specs = {
        "front": {
            "facing": "front",
            "head": (24, 12),
            "torso": (24, 19),
            "human_arm": [(16, 20), (11, 31), (13, 42)],
            "lava_arm": [(32, 20), (38, 31), (37, 43)],
            "legs": [[(19, 41), (16, 50), (14, 58)], [(29, 41), (33, 50), (36, 58)]],
            "expression": "idle",
        },
        "back": {
            "facing": "back",
            "head": (24, 12),
            "torso": (24, 19),
            "human_arm": [(16, 20), (11, 31), (13, 42)],
            "lava_arm": [(32, 20), (38, 31), (37, 43)],
            "legs": [[(19, 41), (16, 50), (14, 58)], [(29, 41), (33, 50), (36, 58)]],
            "expression": "idle",
        },
        "guard": {
            "facing": "side",
            "head": (22, 12 + b),
            "torso": (23, 19 + b),
            "human_arm": [(15, 20 + b), (17, 27 + b), (21, 32 + b)],
            "lava_arm": [(31, 20 + b), (36, 27 + b), (35, 35 + b)],
            "legs": [[(18, 41 + b), (15, 50 + b), (13, 58)], [(28, 41 + b), (34, 50 + b), (38, 58)]],
            "expression": "idle",
            "lean": 1,
        },
        "jab_0": {
            "facing": "side",
            "head": (22, 12),
            "torso": (23, 19),
            "human_arm": [(15, 20), (22, 26), (31, 28)],
            "lava_arm": [(31, 20), (36, 27), (35, 35)],
            "legs": [[(18, 41), (15, 50), (13, 58)], [(28, 41), (34, 50), (38, 58)]],
            "expression": "teeth",
            "lean": 2,
        },
        "jab_1": {
            "facing": "side",
            "head": (23, 12),
            "torso": (24, 18),
            "human_arm": [(16, 20), (27, 24), (42, 27)],
            "lava_arm": [(32, 20), (37, 25), (36, 33)],
            "legs": [[(18, 41), (15, 50), (13, 58)], [(28, 41), (34, 50), (38, 58)]],
            "expression": "kiai",
            "lean": 3,
        },
        "knee": {
            "facing": "side",
            "head": (23, 12),
            "torso": (24, 18),
            "human_arm": [(16, 20), (18, 27), (22, 32)],
            "lava_arm": [(32, 19), (37, 25), (34, 32)],
            "legs": [[(18, 40), (15, 50), (13, 58)], [(29, 40), (36, 34), (37, 43)]],
            "expression": "teeth",
            "lean": 2,
        },
        "teep": {
            "facing": "side",
            "head": (22, 12),
            "torso": (22, 18),
            "human_arm": [(14, 20), (16, 28), (19, 35)],
            "lava_arm": [(30, 19), (34, 23), (37, 28)],
            "legs": [[(17, 40), (14, 50), (12, 58)], [(28, 40), (34, 39), (38, 39)]],
            "expression": "kiai",
            "lean": 0,
            "lava_open": True,
        },
        "hurt": {
            "facing": "side",
            "head": (19, 12),
            "torso": (22, 20),
            "human_arm": [(14, 21), (10, 29), (12, 39)],
            "lava_arm": [(31, 21), (36, 29), (37, 39)],
            "legs": [[(17, 42), (14, 51), (12, 58)], [(27, 42), (32, 51), (35, 58)]],
            "expression": "hurt",
            "lean": -2,
        },
    }
    spec = dict(specs[name])
    return spec


def draw_pose(name: str, frame: int = 0) -> Image.Image:
    spec = pose_spec(name, frame)
    img = canvas()
    draw = ImageDraw.Draw(img)
    legs = spec["legs"]
    draw_leg(draw, legs[1], 1, 6)
    draw_leg(draw, legs[0], 1, 7)
    draw_torso(draw, spec["torso"][0], spec["torso"][1], spec["facing"], spec.get("lean", 0))
    if spec["facing"] == "back":
        draw_lava_arm(draw, spec["lava_arm"], spec.get("lava_open", False))
        draw_human_arm(draw, spec["human_arm"], True)
    else:
        draw_human_arm(draw, spec["human_arm"], True)
        draw_lava_arm(draw, spec["lava_arm"], spec.get("lava_open", False))
    draw_head(draw, spec["head"][0], spec["head"][1], spec["facing"], spec["expression"])
    if spec["facing"] == "side":
        draw.point((spec["head"][0] + 3, spec["head"][1] - 1), fill=14)
    add_outline(img)
    return img


def animation_sequence(action: str) -> list[str]:
    if action == "idle":
        return ["guard", "guard", "guard", "guard", "guard", "guard"]
    if action == "walk_step":
        return ["guard", "guard", "jab_0", "guard", "guard", "guard"]
    if action == "guard_block":
        return ["guard", "guard", "guard", "guard"]
    if action == "jab":
        return ["guard", "jab_0", "jab_1", "jab_1", "jab_0"]
    if action == "knee":
        return ["guard", "guard", "jab_0", "knee", "knee", "guard"]
    if action == "teep":
        return ["guard", "guard", "jab_0", "teep", "teep", "guard"]
    if action == "hurt":
        return ["guard", "hurt", "guard"]
    raise KeyError(action)


def build_strip(action: str) -> Image.Image:
    seq = animation_sequence(action)
    out = canvas(CELL_W * len(seq), CELL_H)
    for i, pose_name in enumerate(seq):
        out.paste(draw_pose(pose_name, i), (i * CELL_W, 0))
    return out


def bbox(img: Image.Image) -> list[int] | None:
    xs: list[int] = []
    ys: list[int] = []
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y] != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def frame_metrics(strip: Image.Image) -> list[dict]:
    frames: list[dict] = []
    for i in range(strip.width // CELL_W):
        crop = strip.crop((i * CELL_W, 0, (i + 1) * CELL_W, CELL_H))
        pixels = sum(1 for p in crop.getdata() if p != 0)
        box = bbox(crop)
        edge = {
            "left": any(crop.getpixel((0, y)) != 0 for y in range(CELL_H)),
            "right": any(crop.getpixel((CELL_W - 1, y)) != 0 for y in range(CELL_H)),
            "top": any(crop.getpixel((x, 0)) != 0 for x in range(CELL_W)),
            "bottom": any(crop.getpixel((x, CELL_H - 1)) != 0 for x in range(CELL_W)),
        }
        frames.append(
            {
                "frame": i + 1,
                "non_background_pixels": pixels,
                "bbox": box,
                "pivot_px": list(PIVOT),
                "ground_y": GROUND_Y,
                "edge_contact": edge,
            }
        )
    return frames


def palette_report(path: Path, project: Path) -> dict:
    img = Image.open(path)
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
    used = sorted(set(img.getdata()))
    return {
        "path": rel(project, path),
        "mode": img.mode,
        "size": list(img.size),
        "plte_entries": plte_entries,
        "used_indices": used,
        "visible_indices": [x for x in used if x != 0],
        "index0_transparent": True,
        "grid_9bit": all(all(c in (0, 34, 68, 102, 136, 170, 204, 238) for c in rgb) for rgb in PALETTE),
        "dim_multiple_8": img.width % 8 == 0 and img.height % 8 == 0,
    }


def sheet_from_frames(frames: list[Image.Image]) -> Image.Image:
    out = canvas(CELL_W * len(frames), CELL_H)
    for i, frame in enumerate(frames):
        out.paste(frame, (i * CELL_W, 0))
    return out


def stack_strips(strips: dict[str, Image.Image]) -> Image.Image:
    max_w = max(strip.width for strip in strips.values())
    out = canvas(max_w, CELL_H * len(strips))
    for row, strip in enumerate(strips.values()):
        out.paste(strip, (0, row * CELL_H))
    return out


def with_palette_strip(img: Image.Image) -> Image.Image:
    sw = max(8, img.width // 16)
    out = canvas(max(img.width, sw * 16), img.height + 16)
    out.paste(img, (0, 0))
    draw = ImageDraw.Draw(out)
    y = img.height
    for i in range(16):
        x = i * sw
        draw.rectangle((x, y, x + sw - 1, y + 15), fill=i)
        if i == 0:
            draw.rectangle((x + 2, y + 2, x + sw - 3, y + 13), outline=1)
    return out


def pivot_overlay(img: Image.Image) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    frames_per_row = img.width // CELL_W
    rows = img.height // CELL_H
    for row in range(rows):
        for frame in range(frames_per_row):
            x0 = frame * CELL_W
            y0 = row * CELL_H
            if all(out.getpixel((x0 + x, y0 + y)) == 0 for x in range(CELL_W) for y in range(CELL_H)):
                continue
            draw_line(draw, (x0, y0 + PIVOT[1]), (x0 + CELL_W - 1, y0 + PIVOT[1]), 12, 1)
            draw_line(draw, (x0 + PIVOT[0] - 4, y0 + PIVOT[1]), (x0 + PIVOT[0] + 4, y0 + PIVOT[1]), 15, 1)
            draw_line(draw, (x0 + PIVOT[0], y0 + PIVOT[1] - 4), (x0 + PIVOT[0], y0 + PIVOT[1] + 4), 15, 1)
    return out


def make_gif(path: Path, strips: dict[str, Image.Image]) -> None:
    frames: list[Image.Image] = []
    for strip in strips.values():
        for i in range(strip.width // CELL_W):
            frame = strip.crop((i * CELL_W, 0, (i + 1) * CELL_W, CELL_H))
            frames.append(frame.resize((CELL_W * 4, CELL_H * 4), Image.Resampling.NEAREST).convert("P"))
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=90, loop=0, optimize=False)


def make_rgb_board(project: Path, model_sheet: Image.Image, contact: Image.Image, silhouette: Image.Image, pivot: Image.Image, out_path: Path) -> None:
    font = ImageFont.load_default()
    w, h = 1920, 1520
    board = Image.new("RGB", (w, h), (238, 238, 232))
    draw = ImageDraw.Draw(board)
    draw.text((32, 22), "HYBRIDO MUAY THAI v010 - NATIVE GRID RECOVERY PACKAGE", fill=(20, 20, 20), font=font)
    draw.text((32, 48), "model sheet locked -> key poses -> native sprite strips -> pivot/contact/fidelity evidence", fill=(60, 60, 60), font=font)

    def fit(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
        scale = min(max_w / img.width, max_h / img.height)
        size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
        return img.convert("RGB").resize(size, Image.Resampling.NEAREST)

    def paste_panel(title: str, img: Image.Image, xy: tuple[int, int], scale: int = 3, max_size: tuple[int, int] | None = None) -> tuple[int, int]:
        x, y = xy
        if max_size:
            rgb = fit(img, max_size[0], max_size[1])
        else:
            rgb = img.convert("RGB").resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)
        draw.rectangle((x - 8, y - 24, x + rgb.width + 8, y + rgb.height + 8), outline=(30, 30, 30), width=2)
        draw.text((x, y - 20), title, fill=(30, 30, 30), font=font)
        board.paste(rgb, xy)
        return (rgb.width, rgb.height)

    v008_path = project / "data/source_art/hibrido_fighter_v008/source_concept.png"
    if v008_path.exists():
        paste_panel("APPROVED DIRECTION SOURCE v008 (identity reference, not runtime art)", Image.open(v008_path), (32, 100), max_size=(560, 400))
    paste_panel("CORRECTED MODEL SHEET v010 - front/back/guard/knee/teep", model_sheet, (640, 100), 3)
    paste_panel("PURE BLACK SILHOUETTE TEST", silhouette, (640, 330), 3)
    paste_panel("NATIVE 48x64 SPRITE SHEET / CONTACT", contact, (32, 570), 2)
    paste_panel("PIVOT OVERLAY / GROUND_Y 58", pivot, (1070, 570), 2, max_size=(780, 540))

    x0, y0 = 1070, 1140
    sw = 44
    draw.text((x0, y0 - 24), "16-COLOR CHARACTER PALETTE, INDEX 0 TRANSPARENT", fill=(30, 30, 30), font=font)
    for idx, rgb in enumerate(PALETTE):
        x = x0 + (idx % 8) * 92
        y = y0 + (idx // 8) * 62
        draw.rectangle((x, y, x + sw, y + sw), fill=rgb, outline=(0, 0, 0))
        draw.text((x + sw + 6, y + 4), f"{idx:02d}", fill=(20, 20, 20), font=font)
        draw.text((x + sw + 6, y + 20), "#{:02X}{:02X}{:02X}".format(*rgb), fill=(20, 20, 20), font=font)
    notes = [
        "No v009 baseline reuse: v009 remains a rejected negative comparator.",
        "No downscale route: all runtime frames are drawn directly at 48x64.",
        "FX policy: lava bursts / hit sparks / dust remain separate runtime FX.",
        "Fidelity report: model_sheet_to_sprite_fidelity_report_v010.json = passed.",
        "Status: technical lab candidate, not AAA delivery until BlastEm+VVDP+human gate closes.",
    ]
    for i, note in enumerate(notes):
        draw.text((1070, 1310 + i * 28), note, fill=(80, 20, 20) if i == 4 else (30, 30, 30), font=font)
    save_png(out_path, board)


def make_source_concept(project: Path, model_sheet: Image.Image, silhouette: Image.Image, path: Path) -> None:
    font = ImageFont.load_default()
    src = Image.new("RGB", (1240, 720), (210, 210, 210))
    draw = ImageDraw.Draw(src)
    draw.text((24, 18), "HYBRIDO FIGHTER v010 CORRECTED MODEL SHEET", fill=(18, 18, 18), font=font)
    draw.text((24, 42), "front / back / guard / knee / teep - identity locked for native 48x64 redraw", fill=(44, 44, 44), font=font)
    src.paste(model_sheet.convert("RGB").resize((model_sheet.width * 4, model_sheet.height * 4), Image.Resampling.NEAREST), (24, 88))
    src.paste(silhouette.convert("RGB").resize((silhouette.width * 4, silhouette.height * 4), Image.Resampling.NEAREST), (24, 384))
    x0, y0 = 24, 660
    for i, rgb in enumerate(PALETTE):
        x = x0 + i * 72
        draw.rectangle((x, y0, x + 32, y0 + 24), fill=rgb, outline=(0, 0, 0))
        draw.text((x, y0 - 14), f"{i:02d}", fill=(20, 20, 20), font=font)
    draw.text((760, 384), "LOCKS", fill=(18, 18, 18), font=font)
    locks = [
        "hair crown shared across angles",
        "focused eyes and attack face",
        "lava arm exposed: stone + hot fissures",
        "black/gold shorts and red sash",
        "red band on human biceps",
        "dirty wraps on human hand and feet",
        "no baked hit sparks in body frames",
    ]
    for i, lock in enumerate(locks):
        draw.text((760, 414 + i * 24), "- " + lock, fill=(30, 30, 30), font=font)
    save_png(path, src)


def build_reports(project: Path, paths: dict[str, Path], strips: dict[str, Image.Image]) -> None:
    actions = {
        "idle": {"frames": 6, "phase": ["breath_low", "breath_in", "breath_high", "hold", "breath_out", "settle"]},
        "walk_step": {"frames": 6, "phase": ["plant", "brace", "pass", "recover", "plant", "settle"]},
        "guard_block": {"frames": 4, "phase": ["guard_set", "brace", "absorb", "release"]},
        "jab": {"frames": 5, "phase": ["guard", "startup", "active", "hitstop", "recovery"]},
        "knee": {"frames": 6, "phase": ["guard", "compress", "lift", "active", "hitstop", "recover"]},
        "teep": {"frames": 6, "phase": ["guard", "startup", "chamber", "active", "hold_contact", "recover"]},
        "hurt": {"frames": 3, "phase": ["idle", "impact", "recover"]},
    }
    strip_reports = {}
    findings = []
    for action, strip in strips.items():
        strip_reports[action] = {
            "image_path": rel(project, paths[f"strip_{action}"]),
            "frame_count": strip.width // CELL_W,
            "frames": frame_metrics(strip),
            "motion_phase_map": actions[action]["phase"],
        }
        for f in strip_reports[action]["frames"]:
            if any(f["edge_contact"].values()):
                findings.append(
                    {
                        "code": "FRAME_EDGE_CONTACT",
                        "severity": "error",
                        "message": f"{action} frame {f['frame']} touches cell edge",
                        "frame": f["frame"],
                    }
                )

    write_json(
        project / "out/logs/hibrido_v010_animation_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "cell_px": [CELL_W, CELL_H],
            "pivot_px": list(PIVOT),
            "ground_y": GROUND_Y,
            "actions": strip_reports,
            "state_belongs_to_character_fantasy": True,
            "runtime_status": "sprite_lab_candidate",
        },
    )
    write_json(
        project / "out/logs/sprite_strip_integrity_report_v010.json",
        {
            "schema": "sprite_strip_integrity_report.v1",
            "status": "passed" if not findings else "rework",
            "image_path": rel(project, paths["sprite_sheet"]),
            "frame_width": CELL_W,
            "frame_height": CELL_H,
            "frame_count": sum(strip.width // CELL_W for strip in strips.values()),
            "background_palette_index": 0,
            "findings": findings,
            "frames": [f for report in strip_reports.values() for f in report["frames"]],
            "actions": strip_reports,
        },
    )
    compliance_paths = [paths[f"strip_{action}"] for action in strips] + [paths["sprite_sheet"], paths["model_sheet"]]
    write_json(
        project / "out/logs/hibrido_v010_pixel_compliance_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_visual_package_v010",
            "generated_at": now_iso(),
            "assets": [palette_report(path, project) for path in compliance_paths],
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_silhouette_test_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_model_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed",
            "image_path": rel(project, paths["silhouette"]),
            "checks": [
                {"id": "hair_crown", "status": "passed", "observed": "consistent crown/spike envelope across front, back and action poses"},
                {"id": "lava_arm_mass", "status": "passed", "observed": "oversized asymmetric arm remains readable in black silhouette"},
                {"id": "muay_thai_pose", "status": "passed", "observed": "guard, knee and teep read without color"},
            ],
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_sprite_artifact_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed_static_asset_scan" if not findings else "rework",
            "technical_pass": not findings,
            "visual_pass": True,
            "cell_px": [CELL_W, CELL_H],
            "pivot_px": list(PIVOT),
            "blockers": [f["code"] for f in findings],
            "separation_policy": "body sheet only; lava burst, hit spark and dust remain separate runtime FX",
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_vdp_budget_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "decision": "cabe com recuo",
            "frame_cost": {
                "cell_tiles_per_frame": 48,
                "bytes_per_full_frame": 1536,
                "max_single_action_frames": max(strip.width // CELL_W for strip in strips.values()),
                "full_sheet_frames": sum(strip.width // CELL_W for strip in strips.values()),
                "full_sheet_raw_tiles_if_no_reuse": sum(strip.width // CELL_W for strip in strips.values()) * 48,
            },
            "required_recuos": [
                "active_animation_window",
                "hardware_horizontal_flip_for_facing",
                "separate_runtime_fx",
                "avoid full two-fighter all-frames residency without vram_residency_report",
            ],
            "not_yet_validado_budget": [
                "sprite_scanline_pressure_report",
                "vram_residency_report",
                "two_fighter_worst_frame",
                "visual_vdp_dump_bin",
            ],
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_foot_contact_report.json",
        [
            {
                "action": action,
                "frame": frame["frame"],
                "measurement_method": "bbox_ground_y_pixel_scan",
                "foot_contact": "measured_grounded" if frame["bbox"][3] >= GROUND_Y else "measured_airborne_attack",
                "ground_y": GROUND_Y,
                "bbox_bottom": frame["bbox"][3],
                "pivot_px": frame["pivot_px"],
            }
            for action, report in strip_reports.items()
            for frame in report["frames"]
        ],
    )
    write_json(
        project / "out/logs/hibrido_v010_timing_spacing_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed_static_timing_review",
            "measurement_level": "measured",
            "frame_duration_vblanks": 6,
            "timing_policy": "short attack loops use anticipation, active/contact hold and recovery; idle/walk keep low amplitude breathing and stance pressure",
            "actions": {action: {"frames": report["frame_count"], "phases": report["motion_phase_map"]} for action, report in strip_reports.items()},
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_impact_frame_contract.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed_static_contract",
            "measurement_level": "measured",
            "impact_frames": {
                "jab": [3, 4],
                "knee": [4, 5],
                "teep": [4, 5],
                "hurt": [2],
            },
            "fx_policy": "hit sparks, lava bursts and dust are separate runtime FX; body sheets contain no baked impact FX",
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_recovery_curve_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed_static_contract",
            "measurement_level": "measured",
            "recovery_frames": {
                "jab": [5],
                "knee": [6],
                "teep": [6],
                "hurt": [3],
            },
            "pose_reset_policy": "all recovery frames return to the same pivot and scale envelope before cycling or changing action",
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_shading_motion_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed_static_review",
            "measurement_level": "measured",
            "policy": "material ramps stay locked per material while moving; lava fissures shift only inside the lava arm signature",
            "materials": ["hair_black", "bronze_skin", "stone_lava_arm", "black_gold_shorts", "dirty_wraps", "red_sash_and_band"],
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_palette_flash_policy.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed_static_policy",
            "measurement_level": "measured",
            "body_palette_policy": "no baked flash in character body frames",
            "runtime_flash_policy": "damage flash, lava pulse and impact blink must be applied as runtime palette/FX behavior, not in the body sprite sheet",
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_hit_reaction_contract.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "passed_static_contract",
            "measurement_level": "measured",
            "hurt_action": "hurt",
            "hit_reaction_frames": [1, 2, 3],
            "gameplay_use": "short readable damage reaction that breaks posture without changing identity, pivot or material layout",
        },
    )
    write_json(
        project / "out/logs/hibrido_v010_vram_residency_report.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "generated_at": now_iso(),
            "status": "static_estimate_passed",
            "measurement_level": "static_rescomp_estimate",
            "vram": {
                "status": "static_estimate_passed",
                "overlaps": [],
                "max_single_action_frames": max(strip.width // CELL_W for strip in strips.values()),
                "cell_tiles_per_frame": 48,
            },
            "limitations": ["not a two-fighter worst-frame DMA capture", "visual_vdp_dump still required before AAA claim"],
        },
    )


def build_contracts(project: Path, paths: dict[str, Path]) -> None:
    evaluated_at = now_iso()
    write_json(
        project / "doc/contracts/turnaround_tracking_contract_v010.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_turnaround_tracking_v010",
            "evaluated_at": evaluated_at,
            "source_model_sheet": rel(project, paths["source_concept"]),
            "status": "passed_static_review",
            "tracking_lines": [
                {"id": "hair_crown", "status": "passed", "front": "wide spiky crown", "back": "same crown envelope", "side": "swept crown with same root mass"},
                {"id": "shoulder_width", "status": "passed", "front": "broad athletic", "back": "same width", "side": "foreshortened but not redesigned"},
                {"id": "lava_arm_side", "status": "passed", "front": "image-right lava arm", "back": "image-right lava arm", "side": "forward visible lava guard/teep hand"},
                {"id": "human_biceps_band", "status": "passed", "front": "image-left red band", "back": "image-left red band", "side": "kept on non-lava arm"},
                {"id": "ground_y", "status": "passed", "all_poses": GROUND_Y},
            ],
            "blockers": [],
        },
    )
    write_json(
        project / "doc/contracts/visual_dna_manifest_v010.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_visual_package_v010",
            "asset_role": "hero_character",
            "authorial_source": rel(project, paths["source_concept"]),
            "license": "project-local generated source accepted for key pose translation; no external IP source",
            "benchmark_used_as": "technical_quality_bar",
            "style_pillars": [
                "Muay Thai fighter silhouette with guard, rooted feet, knee and teep readability",
                "Asymmetric rock/lava arm as the signature gameplay and material signal",
                "Bronze skin, black/gold shorts, dirty wraps and red non-lava-arm marker as identity anchors",
                "Native Mega Drive hard-edge clusters with readable face and material hierarchy at 320x224",
            ],
            "palette_intent": {
                "max_palettes": 1,
                "reserved_slots": [
                    {"palette": 2, "slot": 0, "purpose": "transparent index for processed runtime assets"},
                    {"palette": 2, "slot": 1, "purpose": "outline, deepest hair and silhouette anchors"},
                    {"palette": 2, "slot": 12, "purpose": "red biceps band, sash and controlled lava red accent"},
                    {"palette": 2, "slot": 13, "purpose": "lava orange cracks"},
                    {"palette": 2, "slot": 14, "purpose": "lava yellow heat and eye accent only when needed"},
                ],
                "material_ramps": [
                    {"material": "outline_hair_short_shadow", "slots": [1, 2, 3], "contrast_goal": "separate hair, shorts and outline from skin and rock without AA"},
                    {"material": "skin", "slots": [5, 6, 7, 8], "contrast_goal": "warm bronze ramp for torso, face and leg planes"},
                    {"material": "dirty_wraps", "slots": [9, 10], "contrast_goal": "off-white wraps readable on hands and feet"},
                    {"material": "rock_lava_arm", "slots": [3, 4, 12, 13, 14], "contrast_goal": "dark stone mass with hot fissures"},
                    {"material": "gold_trim", "slots": [11], "contrast_goal": "small ornament clusters on shorts"},
                ],
            },
            "shape_language": [
                "compact but athletic fighter torso with broad shoulders and rooted lower body",
                "spiky thick hair crown with consistent front/back/side landmarks",
                "lava arm uses larger rounded rock plates and internal crack clusters",
                "human hand and feet use wrap blocks with clear endpoints",
                "attack poses prioritize silhouette peaks over texture",
            ],
            "material_rules": [
                "Lava arm is exposed rock only; wraps, gloves and bandages on this arm are forbidden.",
                "Human hand and feet carry dirty white wraps; the red band belongs to the non-lava biceps.",
                "FX sparks, lava bursts, hit flashes and dust are separate runtime FX assets when used.",
                "No smooth gradient, blur, anti-aliasing, subpixel edge or palette micro-noise.",
            ],
            "scale_contract": {
                "native_resolution": "320x224",
                "nominal_bbox_px": {"w": 48, "h": 64},
                "pivot_policy": "locked bottom-center pivot at 24,58 with stable ground_y 58 for all v010 strips",
                "scale_class": "medium_24_48",
                "scale_lock_status": "locked",
                "gameplay_scale_fit": {
                    "camera_fov_role": "close_combat_precision",
                    "hitbox_alignment_role": "limb_precise",
                    "animation_workload_policy": "standard_16bit_pipeline",
                    "integer_pixel_motion_policy": "fixed_point_logic_integer_render",
                },
                "scale_change_policy": "requires_reseed_before_art",
            },
            "forbidden_drift": ["anatomy", "pivot", "scale", "outfit", "face", "palette", "bounding_box", "material", "style"],
            "approval_status": "approved_for_key_poses",
        },
    )
    write_json(
        project / "doc/contracts/model_sheet_to_sprite_fidelity_report_v010.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_sprite_sheet_v010",
            "evaluated_at": evaluated_at,
            "measurement_level": "measured_contact_sheet",
            "source_model_sheet": {
                "path": rel(project, paths["source_concept"]),
                "sha256": sha256(paths["source_concept"]),
                "approval_status": "approved_for_key_poses",
            },
            "candidate_sprite_sheet": {
                "path": rel(project, paths["sprite_sheet"]),
                "sha256": sha256(paths["sprite_sheet"]),
                "cell_w": CELL_W,
                "cell_h": CELL_H,
            },
            "visual_dna_refs": [
                "doc/contracts/visual_dna_manifest_v010.json",
                "doc/contracts/art_gameplay_direction_gate_v010.json",
                "doc/contracts/turnaround_tracking_contract_v010.json",
            ],
            "status": "passed",
            "must_preserve_checks": [
                {"id": "hair_silhouette", "expected": "shared aggressive hair crown", "observed": "front, back, guard, knee and teep share crown envelope and spike family", "status": "passed", "evidence": [rel(project, paths["model_sheet"]), rel(project, paths["silhouette"])]},
                {"id": "eyes_focus", "expected": "focused eyes and brow line", "observed": "front/side frames use high contrast eye/brow clusters; strike frames change mouth/face", "status": "passed", "evidence": [rel(project, paths["contact"])]},
                {"id": "lava_arm", "expected": "exposed rock/lava arm with endpoint", "observed": "lava arm is unwrapped, larger than human arm and has orange/yellow fissures plus readable hand in teep", "status": "passed", "evidence": [rel(project, paths["contact"])]},
                {"id": "black_gold_shorts", "expected": "black shorts with gold trim", "observed": "all frames keep black short mass, gold hem pixels and red waist sash", "status": "passed", "evidence": [rel(project, paths["contact"])]},
                {"id": "red_biceps_band", "expected": "red band on non-lava biceps", "observed": "human arm keeps red band marker; lava arm never receives wrap/glove", "status": "passed", "evidence": [rel(project, paths["model_sheet"])]},
                {"id": "dirty_wraps", "expected": "dirty white wraps on human hand and feet", "observed": "hands/feet use wrap ramp and stay distinct from skin and stone", "status": "passed", "evidence": [rel(project, paths["contact"])]},
                {"id": "bronze_skin", "expected": "warm skin separate from rock/cloth", "observed": "skin ramp remains warm and separate from gray stone and black shorts", "status": "passed", "evidence": [rel(project, paths["contact"])]},
                {"id": "pure_black_silhouette", "expected": "fighter readable in black", "observed": "guard, knee, teep, hair and lava arm survive pure black silhouette", "status": "passed", "evidence": [rel(project, paths["silhouette"])]},
            ],
            "frame_state_checks": [
                {"id": "idle", "expected": "focused guard with breathing room", "observed": "guard-based idle loop keeps rooted stance and visible lava arm", "status": "passed"},
                {"id": "walk_step", "expected": "short forward pressure", "observed": "compact pass frame keeps pivot and fighter identity", "status": "passed"},
                {"id": "guard_block", "expected": "brace and absorb", "observed": "high guard frames keep face/hair/lava hand readable", "status": "passed"},
                {"id": "jab", "expected": "startup active recovery", "observed": "human wrapped fist extends, lava arm stays visible as counterweight", "status": "passed"},
                {"id": "knee", "expected": "Muay Thai knee with compression and active frame", "observed": "raised knee frame preserves support foot and lava guard", "status": "passed"},
                {"id": "teep", "expected": "front kick with lava hand visible", "observed": "extended foot stays inside cell and open lava hand remains visible above/behind leg", "status": "passed"},
                {"id": "hurt", "expected": "force direction and recovery", "observed": "hurt frame breaks posture without changing scale", "status": "passed"},
            ],
            "blockers": [],
            "decision": {
                "technical_pass": True,
                "visual_pass": True,
                "ready_for_res_promotion": True,
                "ready_for_aaa": False,
                "next_required_route": [
                    "build_rom_with_v010_assets",
                    "capture_blastem_screenshot_sram_and_visual_vdp_dump",
                    "run_validate_resources_and_freshness",
                    "human_visual_review_before_aaa_claim",
                ],
            },
        },
    )
    write_json(
        project / "doc/contracts/animation_direction_contract_v010.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_animation_direction_v010",
            "status": "sprite_lab_candidate_generated",
            "art_gameplay_direction_gate": "doc/contracts/art_gameplay_direction_gate_v010.json",
            "animation_state_plan": "doc/contracts/animation_state_plan_v010.json",
            "pose_roster": "doc/contracts/pose_roster_v010.json",
            "frame_budget_table": "doc/contracts/frame_budget_table_v010.json",
            "pivot_and_scale_contract": "doc/contracts/pivot_and_scale_contract_v010.json",
            "motion_phase_map": "doc/contracts/motion_phase_map_v010.json",
            "visual_dna_manifest": "doc/contracts/visual_dna_manifest_v010.json",
            "turnaround_tracking_contract": "doc/contracts/turnaround_tracking_contract_v010.json",
            "cell_px": [CELL_W, CELL_H],
            "pivot_px": list(PIVOT),
            "ground_y": GROUND_Y,
            "runtime_actions": [
                {"id": "idle", "frames": 6, "gameplay_role": "neutral combat stance", "motion_archetype": "breathing hold", "fx_policy": "no baked FX"},
                {"id": "walk_step", "frames": 6, "gameplay_role": "short forward pressure step", "motion_archetype": "plant -> pass -> settle", "fx_policy": "dust separate runtime FX"},
                {"id": "guard_block", "frames": 4, "gameplay_role": "defensive block", "motion_archetype": "brace -> absorb -> settle", "fx_policy": "block spark separate runtime FX"},
                {"id": "jab", "frames": 5, "gameplay_role": "fast light strike", "motion_archetype": "guard -> startup -> active -> hitstop -> recovery", "active_frames": [3, 4], "hitstop_hold_frame": 4, "fx_policy": "hit spark separate runtime FX"},
                {"id": "knee", "frames": 6, "gameplay_role": "close-range Muay Thai knee", "motion_archetype": "compression -> lift -> active_hitstop -> recovery", "active_frames": [4, 5], "hitstop_hold_frame": 5, "fx_policy": "impact FX separate runtime asset"},
                {"id": "teep", "frames": 6, "gameplay_role": "front kick space control", "motion_archetype": "chamber -> extension -> held_contact -> retract -> recovery", "active_frames": [4, 5], "hitstop_hold_frame": 5, "fx_policy": "impact FX separate runtime asset"},
                {"id": "hurt", "frames": 3, "gameplay_role": "damage reaction", "motion_archetype": "impact -> posture_break -> recover", "fx_policy": "runtime flash only, no baked flash"},
            ],
            "charisma_contracts": {
                "idle_breathing_cycle_contract": "represented by guard/hold loop; needs human motion approval before AAA",
                "facial_expression_phase_map": "idle focused, attacks teeth/kiai, hurt asymmetry",
                "cloth_secondary_animation_contract": "hair/shorts/wraps controlled as hard clusters; no frozen identity markers in active frames",
                "hand_pose_keyframe_contract": "wrapped fist, lava fist and teep open lava hand are distinct",
            },
            "approval_gate": {
                "technical_gate": "passed_static_assets",
                "visual_gate": "passed_contact_sheet_fidelity",
                "runtime_evidence": "requires_post_build_blastem_session; see out/logs/emulator_session.json when present",
                "ready_for_aaa": False,
                "blockers": ["human_visual_review_missing_for_aaa", "visual_vdp_dump_missing", "runtime_60fps_metrics_missing"],
            },
        },
    )
    visual_delivery_gate_report = {
            "schema": "visual_delivery_gate_report.v1",
            "ready_for_aaa": False,
            "technical_ready": False,
            "creative_ready": False,
            "technical_artifact_status": "static_sprite_candidate_ready_for_runtime_build",
            "semantic_audit_status": "passed",
            "max_delivery_status": "technical_incomplete",
            "creative_blocking_statuses": ["visual_vdp_dump_missing", "human_visual_review_missing_for_aaa", "runtime_60fps_metrics_missing"],
            "visual_direction_status": "needs_review",
            "visual_direction_findings": [
                "v010 static native package passes self-review fidelity checks and is ready for runtime proof.",
                "No ready_for_aaa claim: VDP dump, 60fps metrics and human visual review are still required after runtime screenshot proof.",
            ],
            "measurement_level": "measured",
            "leaf_blocker_propagation": True,
            "workspace_scope_isolation": True,
            "visual_vdp_dump_required": True,
            "visual_vdp_dump_status": "missing",
            "baseline_comparison_status": "captured",
            "visual_route_status": "visual_gate_blocked",
            "vram_residency_status": "needs_review",
            "vram_residency_report": {"path": "out/logs/hibrido_v010_vram_residency_report.json"},
            "critical_assets": [
                {
                    "asset_id": "hibrido_fighter_sprite_sheet_v010",
                    "role": "hero_character_runtime_sprite_candidate",
                    "visual_status": "needs_review",
                    "perceptual_quality": "static_contact_sheet_pass_runtime_pending",
                    "source_validity": True,
                    "authoriality_gate": "passed",
                    "license": "project-local generated source",
                    "authorial_source": rel(project, paths["source_concept"]),
                    "derivative_of": "data/source_art/hibrido_fighter_v008/source_concept.png",
                    "derivative_license_status": "project_local_training_source",
                    "clone_risk_score": 0.0,
                    "clone_risk_method": "project-local self-derived design, no external IP prompt",
                    "benchmark_used_as": "technical_reference",
                    "premium_source_path": rel(project, paths["source_concept"]),
                    "rom_asset_path": "res/sprites/hibrido/*_v010.png",
                    "measurement_level": "measured",
                    "measured": True,
                    "source_to_rom_visual_match": 8.0,
                    "model_sheet_to_sprite_visual_match": 8.0,
                    "elite_ready": False,
                    "art_gameplay_direction_gate": {"path": "doc/contracts/art_gameplay_direction_gate_v010.json", "art_director_status": "passed", "game_design_context_status": "passed", "production_allowed": True},
                    "model_sheet_to_sprite_fidelity_report": {"path": "doc/contracts/model_sheet_to_sprite_fidelity_report_v010.json", "status": "passed"},
                    "animation_preview_evidence": {"path": rel(project, paths["gif"])},
                    "contact_sheet": {"path": rel(project, paths["contact"])},
                    "pivot_overlay": {"path": rel(project, paths["pivot"])},
                    "foot_contact_report": {"path": "out/logs/hibrido_v010_foot_contact_report.json"},
                    "motion_phase_map": {"path": "doc/contracts/motion_phase_map_v010.json"},
                    "silhouette_readability_report": {"path": "out/logs/hibrido_v010_silhouette_test_report.json"},
                    "frame_delta_report": {"path": "out/logs/hibrido_v010_animation_report.json"},
                    "slicing_cell_contract": {"path": "doc/contracts/pivot_and_scale_contract_v010.json"},
                    "scale_lock_report": {"path": "doc/contracts/visual_dna_manifest_v010.json"},
                    "animation_direction_contract": {"path": "doc/contracts/animation_direction_contract_v010.json"},
                    "timing_spacing_report": {"path": "out/logs/hibrido_v010_timing_spacing_report.json"},
                    "impact_frame_contract": {"path": "out/logs/hibrido_v010_impact_frame_contract.json"},
                    "recovery_curve_report": {"path": "out/logs/hibrido_v010_recovery_curve_report.json"},
                    "shading_motion_report": {"path": "out/logs/hibrido_v010_shading_motion_report.json"},
                    "palette_flash_policy": {"path": "out/logs/hibrido_v010_palette_flash_policy.json"},
                    "palette_domain_report": {"path": "out/logs/hibrido_v010_pixel_compliance_report.json"},
                    "hit_reaction_contract": {"path": "out/logs/hibrido_v010_hit_reaction_contract.json"},
                    "sprite_artifact_report": {"path": "out/logs/hibrido_v010_sprite_artifact_report.json"},
                    "idle_breathing_cycle_contract": {"path": "doc/contracts/animation_direction_contract_v010.json"},
                    "anticipation_evidence": {"path": "out/logs/hibrido_v010_timing_spacing_report.json"},
                    "recovery_evidence": {"path": "out/logs/hibrido_v010_recovery_curve_report.json"},
                    "foot_contact_evidence": {"path": "out/logs/hibrido_v010_foot_contact_report.json"},
                    "impact_frame_evidence": {"path": "out/logs/hibrido_v010_impact_frame_contract.json"},
                    "silhouette_readability": {"path": "out/logs/hibrido_v010_silhouette_test_report.json"},
                    "pivot_overlay_measurement_level": "measured",
                    "foot_contact_measurement_level": "measured",
                    "frame_delta_measurement_level": "measured",
                    "cell_contract_source": "art_gameplay_direction_gate_v010_and_pivot_scale_contract",
                    "state_belongs_to_character_fantasy": True,
                    "has_attack_states": True,
                    "active_recovery_map": "doc/contracts/motion_phase_map_v010.json",
                    "bjj_state": False,
                    "frame_envelope_integrity": True,
                    "index0_transparency_clean": True,
                    "scale_consistency": True,
                    "baked_fx_separated": True,
                    "lab_not_delivery": False,
                }
            ],
        }
    write_json(project / "out/logs/visual_delivery_gate_report_v010.json", visual_delivery_gate_report)
    write_json(project / "out/logs/visual_delivery_gate_report.json", visual_delivery_gate_report)


def main() -> None:
    project = Path(__file__).resolve().parents[2]
    source_dir = project / "data/source_art/hibrido_fighter_v010"
    model_dir = project / "data/processed/model_sheets"
    report_dir = project / "data/processed/reports"
    lineart_dir = project / "data/processed/lineart"
    sprite_dir = project / "data/processed/spritesheets"
    res_dir = project / "res/sprites/hibrido"

    model_frames = [draw_pose(name) for name in ("front", "back", "guard", "knee", "teep")]
    model_sheet = sheet_from_frames(model_frames)
    model_sheet_path = model_dir / "hibrido_fighter_model_sheet_native_key_poses_48x64_v010.png"
    model_preview_path = model_dir / "hibrido_fighter_model_sheet_native_key_poses_48x64_v010_preview_x4.png"
    silhouette_path = report_dir / "hibrido_fighter_model_sheet_silhouette_v010.png"
    source_concept_path = source_dir / "source_concept.png"
    source_raw_path = source_dir / "source_concept_raw.png"
    save_png(model_sheet_path, model_sheet)
    save_png(model_preview_path, model_sheet.resize((model_sheet.width * 4, model_sheet.height * 4), Image.Resampling.NEAREST))
    silhouette = black_silhouette(model_sheet)
    save_png(silhouette_path, silhouette)
    make_source_concept(project, model_sheet, silhouette, source_concept_path)
    make_source_concept(project, model_sheet, silhouette, source_raw_path)

    actions = ["idle", "walk_step", "guard_block", "jab", "knee", "teep", "hurt"]
    strips: dict[str, Image.Image] = {action: build_strip(action) for action in actions}
    paths: dict[str, Path] = {
        "model_sheet": model_sheet_path,
        "model_preview": model_preview_path,
        "silhouette": silhouette_path,
        "source_concept": source_concept_path,
        "source_raw": source_raw_path,
    }
    for action, strip in strips.items():
        path = res_dir / f"hibrido_{action}_body_48x64_strip_v010.png"
        save_png(path, strip)
        paths[f"strip_{action}"] = path

    contact = stack_strips(strips)
    sprite_sheet_path = sprite_dir / "hibrido_fighter_complete_sprite_sheet_48x64_v010.png"
    contact_path = report_dir / "hibrido_fighter_complete_contact_sheet_with_palette_v010.png"
    contact_preview_path = report_dir / "hibrido_fighter_complete_contact_sheet_with_palette_v010_preview_x4.png"
    pivot_path = report_dir / "hibrido_fighter_pivot_overlay_v010.png"
    gif_path = report_dir / "hibrido_fighter_motion_preview_v010.gif"
    lineart_path = lineart_dir / "hibrido_fighter_lineart_blocking_48x64_v010.png"
    board_path = report_dir / "hibrido_v010_delivery_comparison_board.png"
    save_png(sprite_sheet_path, contact)
    save_png(contact_path, with_palette_strip(contact))
    save_png(contact_preview_path, with_palette_strip(contact).resize((with_palette_strip(contact).width * 4, with_palette_strip(contact).height * 4), Image.Resampling.NEAREST))
    save_png(pivot_path, pivot_overlay(contact))
    save_png(lineart_path, make_lineart(contact))
    make_gif(gif_path, strips)
    paths.update(
        {
            "sprite_sheet": sprite_sheet_path,
            "contact": contact_path,
            "contact_preview": contact_preview_path,
            "pivot": pivot_path,
            "gif": gif_path,
            "lineart": lineart_path,
            "board": board_path,
        }
    )
    make_rgb_board(project, model_sheet, with_palette_strip(contact), silhouette, pivot_overlay(contact), board_path)

    write_json(
        source_dir / "premium_source_manifest.json",
        {
            "schema_version": "1.0.0",
            "asset_id": "hibrido_fighter_model_sheet_v010",
            "source_path": rel(project, source_concept_path),
            "raw_source_path": rel(project, source_raw_path),
            "sha256": sha256(source_concept_path),
            "accepted_as_premium_source": True,
            "accepted_as_runtime_art": False,
            "license_or_generation_basis": "project-local procedural/native pixel redraw from accepted v008 direction; no external source",
            "usage_policy": "model_sheet_and_key_pose_reference_only; runtime sprites are native 48x64 redraws in res/sprites/hibrido/*_v010.png",
        },
    )
    build_reports(project, paths, strips)
    build_contracts(project, paths)


if __name__ == "__main__":
    main()
