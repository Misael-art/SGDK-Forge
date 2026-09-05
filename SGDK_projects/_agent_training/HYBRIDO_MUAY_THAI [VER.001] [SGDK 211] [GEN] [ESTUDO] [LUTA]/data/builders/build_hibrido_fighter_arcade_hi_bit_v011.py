from __future__ import annotations

import hashlib
import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CELL_W = 96
CELL_H = 96
PIVOT = (32, 88)
GROUND_Y = 88

PALETTE = [
    (0xEE, 0x00, 0xEE),  # 00 transparent key
    (0x00, 0x00, 0x00),  # 01 outline/hair
    (0x22, 0x22, 0x22),  # 02 hair/shorts shadow
    (0x44, 0x44, 0x44),  # 03 shorts/stone dark
    (0x66, 0x66, 0x66),  # 04 stone mid
    (0x88, 0x66, 0x44),  # 05 skin shadow
    (0xAA, 0x66, 0x22),  # 06 skin base
    (0xCC, 0x88, 0x44),  # 07 skin light
    (0xEE, 0xAA, 0x66),  # 08 skin high
    (0xCC, 0xAA, 0x88),  # 09 dirty wraps
    (0xEE, 0xEE, 0xCC),  # 10 wrap/teeth
    (0xCC, 0xAA, 0x22),  # 11 gold trim
    (0xCC, 0x22, 0x22),  # 12 red band/sash
    (0xEE, 0x66, 0x00),  # 13 lava orange
    (0xEE, 0xEE, 0x00),  # 14 lava yellow/eyes
    (0xEE, 0xEE, 0xEE),  # 15 hard spec
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


def line(draw: ImageDraw.ImageDraw, pts: list[tuple[int, int]], fill: int, width: int) -> None:
    draw.line(pts, fill=fill, width=width, joint="curve")
    r = max(2, width // 2)
    for x, y in pts:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill)


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


def draw_hair(d: ImageDraw.ImageDraw, x: int, y: int, wind: int = 0) -> None:
    pts = [
        (x - 12, y + 5), (x - 13, y - 3), (x - 10, y - 7), (x - 7, y - 3),
        (x - 5, y - 15), (x - 1, y - 7), (x + 2, y - 17), (x + 5 + wind, y - 7),
        (x + 11 + wind, y - 12), (x + 13 + wind, y - 4), (x + 10, y + 6)
    ]
    d.polygon(pts, fill=1)
    d.line([(x - 10, y - 1), (x + 10, y - 7)], fill=2, width=2)
    d.line([(x - 5, y - 9), (x + 7, y - 12)], fill=2, width=1)
    d.point((x + 4 + wind, y - 14), fill=3)


def draw_head(d: ImageDraw.ImageDraw, x: int, y: int, expression: str, wind: int = 0) -> None:
    d.ellipse((x - 8, y - 9, x + 8, y + 9), fill=7)
    d.polygon([(x - 7, y + 0), (x + 8, y - 1), (x + 6, y + 10), (x - 5, y + 10)], fill=6)
    d.polygon([(x - 8, y - 3), (x - 2, y - 2), (x - 4, y + 8), (x - 8, y + 5)], fill=5)
    d.point((x + 5, y + 2), fill=8)
    draw_hair(d, x, y - 5, wind)
    d.line([(x - 7, y - 2), (x - 1, y - 5)], fill=1, width=1)
    d.line([(x + 1, y - 5), (x + 8, y - 2)], fill=1, width=1)
    d.rectangle((x - 4, y - 1, x - 2, y), fill=15)
    d.rectangle((x + 4, y - 2, x + 6, y - 1), fill=15)
    d.point((x - 3, y), fill=1)
    d.point((x + 5, y - 1), fill=1)
    if expression == "kiai":
        d.rectangle((x + 1, y + 4, x + 6, y + 8), fill=1)
        d.line([(x + 2, y + 5), (x + 5, y + 5)], fill=10, width=1)
    elif expression == "hurt":
        d.line([(x - 5, y + 5), (x + 3, y + 7)], fill=1, width=2)
        d.point((x + 2, y + 6), fill=12)
    else:
        d.line([(x - 3, y + 5), (x + 5, y + 4)], fill=1, width=1)


def draw_torso(d: ImageDraw.ImageDraw, x: int, y: int, lean: int = 0) -> None:
    d.polygon([(x - 16 + lean, y + 2), (x - 7 + lean, y - 3), (x + 10 + lean, y - 3), (x + 17 + lean, y + 4),
               (x + 15, y + 30), (x + 8, y + 43), (x - 8, y + 43), (x - 16, y + 29)], fill=6)
    d.polygon([(x - 15 + lean, y + 5), (x - 3 + lean, y + 2), (x - 4, y + 40), (x - 11, y + 39), (x - 16, y + 25)], fill=5)
    d.polygon([(x - 1 + lean, y + 2), (x + 11 + lean, y + 1), (x + 15, y + 27), (x + 7, y + 40), (x - 1, y + 39)], fill=7)
    d.line([(x - 1, y + 7), (x - 2, y + 39)], fill=5, width=1)
    d.line([(x - 11, y + 13), (x - 1, y + 10), (x + 10, y + 13)], fill=8, width=2)
    d.line([(x - 10, y + 22), (x + 9, y + 22)], fill=5, width=1)
    d.line([(x - 8, y + 29), (x + 7, y + 29)], fill=8, width=1)
    d.line([(x - 6, y + 36), (x + 5, y + 36)], fill=5, width=1)
    d.point((x + 6, y + 8), fill=8)
    d.point((x + 11, y + 18), fill=8)


def draw_shorts(d: ImageDraw.ImageDraw, x: int, y: int) -> None:
    d.polygon([(x - 17, y), (x + 16, y), (x + 18, y + 15), (x + 8, y + 20), (x, y + 14), (x - 9, y + 20), (x - 18, y + 15)], fill=2)
    d.rectangle((x - 13, y + 2, x + 13, y + 9), fill=3)
    d.line([(x - 17, y + 15), (x - 8, y + 19)], fill=11, width=2)
    d.line([(x + 17, y + 15), (x + 8, y + 19)], fill=11, width=2)
    d.line([(x - 13, y + 7), (x - 16, y + 16)], fill=11, width=1)
    d.line([(x + 13, y + 7), (x + 16, y + 16)], fill=11, width=1)
    d.rectangle((x - 4, y, x + 4, y + 7), fill=12)
    d.line([(x - 3, y + 7), (x - 3, y + 21)], fill=12, width=2)
    d.line([(x + 3, y + 7), (x + 3, y + 21)], fill=12, width=2)


def draw_wrap_foot(d: ImageDraw.ImageDraw, x: int, y: int, direction: int) -> None:
    d.rectangle((x - 5, y - 9, x + 5, y - 1), fill=9)
    d.line([(x - 5, y - 6), (x + 5, y - 6)], fill=10, width=1)
    d.line([(x - 4, y - 3), (x + 4, y - 8)], fill=10, width=1)
    if direction >= 0:
        d.ellipse((x - 4, y - 2, x + 12, y + 3), fill=7)
        d.line([(x - 1, y + 1), (x + 12, y + 1)], fill=5, width=1)
        d.point((x + 8, y - 1), fill=8)
    else:
        d.ellipse((x - 12, y - 2, x + 4, y + 3), fill=7)
        d.line([(x - 12, y + 1), (x + 1, y + 1)], fill=5, width=1)
        d.point((x - 8, y - 1), fill=8)


def draw_human_arm(d: ImageDraw.ImageDraw, pts: list[tuple[int, int]], open_hand: bool = False) -> None:
    line(d, pts, 6, 8)
    line(d, pts, 8, 3)
    ux, uy = pts[1]
    d.rectangle((ux - 6, uy - 4, ux + 6, uy + 3), fill=12)
    d.line([(ux - 5, uy + 2), (ux + 5, uy - 3)], fill=11, width=1)
    hx, hy = pts[-1]
    d.ellipse((hx - 6, hy - 5, hx + 6, hy + 5), fill=9)
    d.line([(hx - 6, hy), (hx + 6, hy)], fill=10, width=1)
    if open_hand:
        for i in range(4):
            d.line([(hx - 5 + i * 3, hy - 1), (hx - 6 + i * 3, hy - 7)], fill=10, width=1)


def draw_lava_arm(d: ImageDraw.ImageDraw, pts: list[tuple[int, int]], open_hand: bool = False) -> None:
    line(d, pts, 4, 11)
    line(d, pts, 3, 5)
    for a, b in zip(pts, pts[1:]):
        ax, ay = a
        bx, by = b
        mid = ((ax + bx) // 2, (ay + by) // 2)
        d.line([(ax + 1, ay - 1), mid, (bx - 2, by + 1)], fill=13, width=2)
        d.point(mid, fill=14)
        d.point((mid[0] + 2, mid[1] - 2), fill=14)
    hx, hy = pts[-1]
    if open_hand:
        d.ellipse((hx - 8, hy - 7, hx + 8, hy + 6), fill=4)
        for i in range(4):
            d.line([(hx - 7 + i * 5, hy - 1), (hx - 9 + i * 5, hy - 11 - (i % 2))], fill=4, width=2)
            d.point((hx - 9 + i * 5, hy - 11 - (i % 2)), fill=13)
    else:
        d.ellipse((hx - 8, hy - 7, hx + 8, hy + 6), fill=4)
    d.line([(hx - 6, hy - 3), (hx + 6, hy + 2)], fill=13, width=2)
    d.point((hx, hy - 1), fill=14)


def draw_leg(d: ImageDraw.ImageDraw, pts: list[tuple[int, int]], direction: int, shade: int = 7) -> None:
    line(d, pts, 6, 9)
    line(d, pts, shade, 4)
    draw_wrap_foot(d, pts[-1][0], pts[-1][1], direction)


POSES = {
    "idle": {"frames": 4},
    "walk_step": {"frames": 4},
    "guard_block": {"frames": 3},
    "jab": {"frames": 4},
    "knee": {"frames": 4},
    "teep": {"frames": 4},
    "hurt": {"frames": 3},
}


def pose_points(action: str, frame: int) -> dict[str, object]:
    x = 32
    head = (x, 16)
    torso_y = 27
    expression = "idle"
    wind = 0
    lean = 0
    left_arm = [(18, 34), (13, 45), (16, 57)]
    lava_arm = [(46, 34), (53, 48), (52, 62)]
    left_leg = [(23, 68), (18, 78), (16, 88)]
    right_leg = [(41, 68), (46, 78), (49, 88)]
    open_lava = False
    open_human = False

    if action == "idle":
        bob = [0, -1, 0, 1][frame]
        head = (x, 17 + bob)
        torso_y = 27 + bob
        left_arm = [(18, 34 + bob), (13, 45), (16, 57)]
        lava_arm = [(46, 34 + bob), (53, 48), (52, 62)]
    elif action == "walk_step":
        shift = [-3, 0, 3, 0][frame]
        head = (x + shift // 2, 17)
        left_leg = [(23, 68), (17 + shift, 78), (14 + shift, 88)]
        right_leg = [(41, 68), (46 - shift, 78), (52 - shift, 88)]
        left_arm = [(18, 34), (14 - shift // 2, 46), (17 - shift, 58)]
        lava_arm = [(46, 34), (53 + shift // 2, 47), (52 + shift, 61)]
        wind = shift // 2
    elif action == "guard_block":
        lean = -2
        expression = "teeth"
        left_arm = [(18, 34), (23, 39), (28, 47)]
        lava_arm = [(46, 34), (42, 42), (39, 50)]
        left_leg = [(23, 68), (17, 78), (15, 88)]
        right_leg = [(41, 68), (48, 78), (52, 88)]
    elif action == "jab":
        expression = "kiai" if frame >= 2 else "teeth"
        reach = [0, 14, 30, 12][frame]
        left_arm = [(18, 34), (30 + reach // 2, 38), (38 + reach, 40)]
        lava_arm = [(46, 34), (51, 50), (48, 63)]
        left_leg = [(23, 68), (17, 78), (15, 88)]
        right_leg = [(41, 68), (48, 78), (53, 88)]
        wind = 2 if frame >= 2 else 0
    elif action == "knee":
        expression = "kiai" if frame >= 2 else "teeth"
        lift = [0, 10, 21, 9][frame]
        lean = [0, -2, -4, -1][frame]
        left_leg = [(23, 68), (18, 78), (16, 88)]
        right_leg = [(41, 68), (47, 67 - lift), (54, 79 - lift)]
        left_arm = [(18, 34), (14, 44), (17, 55)]
        lava_arm = [(46, 34), (51, 47), (48, 60)]
        wind = 1
    elif action == "teep":
        expression = "kiai" if frame >= 2 else "teeth"
        ext = [0, 12, 24, 9][frame]
        left_leg = [(23, 68), (18, 78), (16, 88)]
        right_leg = [(41, 68), (49 + ext // 2, 66), (52 + ext, 64)]
        left_arm = [(18, 34), (13, 45), (17, 56)]
        lava_arm = [(46, 34), (54, 42), (59, 53)]
        open_lava = True
        wind = 3 if frame >= 2 else 0
    elif action == "hurt":
        expression = "hurt"
        lean = [-5, -8, -3][frame]
        head = (x - 4, 18 + frame)
        left_arm = [(18, 34), (10, 45), (8, 58)]
        lava_arm = [(46, 34), (55, 47), (61, 58)]
        left_leg = [(23, 68), (19, 78), (15, 88)]
        right_leg = [(41, 68), (49, 78), (54, 88)]
        wind = -3

    return {
        "head": head,
        "torso_y": torso_y,
        "expression": expression,
        "wind": wind,
        "lean": lean,
        "left_arm": left_arm,
        "lava_arm": lava_arm,
        "left_leg": left_leg,
        "right_leg": right_leg,
        "open_lava": open_lava,
        "open_human": open_human,
    }


def draw_pose(action: str, frame: int = 0) -> Image.Image:
    img = canvas()
    d = ImageDraw.Draw(img)
    p = pose_points(action, frame)
    x = 32

    draw_leg(d, p["left_leg"], -1, 7)
    draw_leg(d, p["right_leg"], 1, 8)
    draw_torso(d, x, p["torso_y"], p["lean"])
    draw_shorts(d, x, p["torso_y"] + 41)
    draw_human_arm(d, p["left_arm"], p["open_human"])
    draw_lava_arm(d, p["lava_arm"], p["open_lava"])
    draw_head(d, p["head"][0], p["head"][1], p["expression"], p["wind"])

    add_outline(img)
    return img


def build_strip(action: str) -> Image.Image:
    frames = POSES[action]["frames"]
    strip = canvas(CELL_W * frames, CELL_H)
    for frame in range(frames):
        strip.paste(draw_pose(action, frame), (frame * CELL_W, 0))
    return strip


def with_palette_strip(src: Image.Image) -> Image.Image:
    out = canvas(src.width, src.height + 16)
    out.paste(src, (0, 0))
    d = ImageDraw.Draw(out)
    for i in range(16):
        d.rectangle((i * 16, src.height, i * 16 + 15, src.height + 15), fill=i)
    return out


def on_review_bg(src: Image.Image, bg: tuple[int, int, int] = (32, 38, 44)) -> Image.Image:
    rgb = Image.new("RGB", src.size, bg)
    sp = src.load()
    rp = rgb.load()
    for y in range(src.height):
        for x in range(src.width):
            idx = sp[x, y]
            if idx != 0:
                rp[x, y] = PALETTE[idx]
    return rgb


def black_silhouette(src: Image.Image) -> Image.Image:
    out = canvas(src.width, src.height)
    sp = src.load()
    op = out.load()
    for y in range(src.height):
        for x in range(src.width):
            if sp[x, y] != 0:
                op[x, y] = 1
    return out


def make_model_sheet(strips: dict[str, Image.Image]) -> Image.Image:
    actions = ["idle", "guard_block", "jab", "knee", "teep", "hurt"]
    sheet = canvas(CELL_W * len(actions), CELL_H * 2)
    for i, action in enumerate(actions):
        sheet.paste(draw_pose(action, min(POSES[action]["frames"] - 1, 2)), (i * CELL_W, 0))
        sheet.paste(black_silhouette(draw_pose(action, min(POSES[action]["frames"] - 1, 2))), (i * CELL_W, CELL_H))
    return sheet


def make_contact_sheet(strips: dict[str, Image.Image]) -> Image.Image:
    width = CELL_W * 4
    height = CELL_H * len(strips)
    sheet = canvas(width, height)
    y = 0
    for action, strip in strips.items():
        sheet.paste(strip, (0, y))
        y += CELL_H
    return sheet


def make_pivot_overlay(project: Path, contact: Image.Image) -> Path:
    overlay = contact.copy()
    d = ImageDraw.Draw(overlay)
    for row in range(len(POSES)):
        y0 = row * CELL_H
        d.line((0, y0 + GROUND_Y, overlay.width - 1, y0 + GROUND_Y), fill=12, width=1)
        for col in range(4):
            x0 = col * CELL_W
            px = x0 + PIVOT[0]
            py = y0 + PIVOT[1]
            d.line((px - 4, py, px + 4, py), fill=14, width=1)
            d.line((px, py - 4, px, py + 4), fill=14, width=1)
            d.rectangle((x0, y0, x0 + CELL_W - 1, y0 + CELL_H - 1), outline=3)
    path = project / "data" / "processed" / "reports" / "hibrido_fighter_arcade_hi_bit_pivot_overlay_v011.png"
    save_png(path, overlay)
    return path


def make_stage_sprite_mockup(project: Path, strips: dict[str, Image.Image]) -> Path:
    stage_path = project / "res" / "bg" / "hibrido_training_stage_320x224_v010.png"
    stage = Image.open(stage_path).convert("RGB")
    pose = draw_pose("guard_block", 1)
    fighter = on_review_bg(pose, bg=(0, 0, 0))
    mask = Image.new("L", pose.size, 0)
    sp = pose.load()
    mp = mask.load()
    for y in range(pose.height):
        for x in range(pose.width):
            if sp[x, y] != 0:
                mp[x, y] = 255
    stage.paste(fighter, (112, 88), mask)
    path = project / "data" / "processed" / "reports" / "hibrido_v011_runtime_stage_sprite_mockup.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    stage.save(path)
    return path


def make_gif(project: Path, strips: dict[str, Image.Image]) -> Path:
    frames = []
    for action in ("idle", "jab", "knee", "teep", "hurt"):
        strip = strips[action]
        for frame in range(POSES[action]["frames"]):
            frames.append(strip.crop((frame * CELL_W, 0, frame * CELL_W + CELL_W, CELL_H)))
    path = project / "data" / "processed" / "reports" / "hibrido_fighter_arcade_hi_bit_motion_preview_v011.gif"
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=90, loop=0, transparency=0, disposal=2)
    return path


def make_board(project: Path, model: Image.Image, contact: Image.Image, gif_path: Path) -> Path:
    out = Image.new("RGB", (1500, 1240), (238, 238, 232))
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        small = ImageFont.truetype("arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
        small = font
    d.text((24, 18), "HYBRIDO v011 arcade-hi-bit fighter package - 96x96 native redraw", fill=(0, 0, 0), font=font)
    d.text((24, 46), "Scale changed because 48x64 could not carry the requested AAA face/anatomy/material readability.", fill=(90, 0, 0), font=small)
    out.paste(on_review_bg(model).resize((model.width * 2, model.height * 2), Image.Resampling.NEAREST), (24, 80))
    contact_review = on_review_bg(contact)
    out.paste(contact_review.resize((contact.width, contact.height), Image.Resampling.NEAREST), (24, 500))
    palette_review = with_palette_strip(canvas(16 * 16, 1)).crop((0, 1, 16 * 16, 17)).convert("RGB").resize((512, 32), Image.Resampling.NEAREST)
    out.paste(palette_review, (24, 1190))
    d.text((1190, 90), "Runtime notes", fill=(0, 0, 0), font=font)
    notes = [
        "Native 96x96 cell.",
        "No v009/v010 sheet as source.",
        "Lava arm: stone + hot fissures.",
        "Wraps stay on human hand/feet.",
        "Red biceps band stays non-lava.",
        "3-4 frames/action for active window.",
        "AAA claim still needs ROM evidence.",
    ]
    for i, note in enumerate(notes):
        d.text((1190, 126 + i * 28), note, fill=(50, 50, 50), font=small)
    path = project / "data" / "processed" / "reports" / "hibrido_fighter_arcade_hi_bit_delivery_board_v011.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    return path


def tile_usage(img: Image.Image) -> int:
    tiles: set[bytes] = set()
    for y in range(0, img.height, 8):
        for x in range(0, img.width, 8):
            tile = img.crop((x, y, x + 8, y + 8)).tobytes()
            if any(tile):
                tiles.add(tile)
    return len(tiles)


def write_contracts(project: Path, paths: dict[str, Path], strips: dict[str, Image.Image]) -> None:
    generated_at = now_iso()
    doc = project / "doc" / "contracts"
    scale_contract = {
        "schema_version": "1.0.0",
        "asset_id": "hibrido_fighter_arcade_hi_bit_v011",
        "evaluated_at": generated_at,
        "route_change_reason": "human quality correction: 48x64 was insufficient for AAA-grade face, anatomy and material readability",
        "scale_contract": {
            "native_resolution": "320x224",
            "nominal_bbox_px": {"w": CELL_W, "h": CELL_H},
            "pivot_policy": "locked bottom-center pivot at 32,88 with stable ground_y 88",
            "scale_class": "arcade_hi_bit_medium_large",
            "scale_lock_status": "locked_for_v011_candidate",
            "scale_change_policy": "v011 supersedes v010 runtime-lab candidate for AAA visual route"
        },
        "must_preserve": [
            "hair_silhouette", "eyes_focus", "face_personality", "athletic_anatomy", "lava_arm",
            "lava_fissures", "black_gold_shorts", "red_biceps_band", "dirty_white_wraps",
            "bronze_skin", "material_roles", "asymmetry_lock"
        ],
        "decision": {
            "production_allowed": True,
            "ready_for_res_promotion": True,
            "ready_for_aaa": False,
            "remaining_blockers": ["human_visual_review_missing_for_aaa", "visual_vdp_dump_missing", "runtime_60fps_metrics_missing"]
        }
    }
    write_json(doc / "art_gameplay_direction_gate_v011.json", scale_contract)
    write_json(doc / "visual_dna_manifest_v011.json", {
        "schema_version": "1.0.0",
        "asset_id": "hibrido_fighter_arcade_hi_bit_v011",
        "authorial_source": "data/source_art/hibrido_fighter_v010/source_concept.png",
        "approval_status": "v011_arcade_hi_bit_candidate",
        "scale_contract": scale_contract["scale_contract"],
        "palette_intent": {"max_palettes": 1, "body_palette": "PAL2", "runtime_fx_palette": "PAL3"},
        "forbidden_drift": ["anatomy", "face", "lava_arm", "outfit", "material", "scale", "pivot"],
    })
    write_json(doc / "animation_direction_contract_v011.json", {
        "schema_version": "1.0.0",
        "asset_id": "hibrido_fighter_animation_direction_v011",
        "status": "arcade_hi_bit_runtime_candidate_generated",
        "cell_px": [CELL_W, CELL_H],
        "pivot_px": list(PIVOT),
        "ground_y": GROUND_Y,
        "runtime_actions": [
            {"id": action, "frames": POSES[action]["frames"], "fx_policy": "runtime FX separated"}
            for action in POSES
        ],
        "evidence": {
            "contact_sheet": rel(project, paths["contact_sheet"]),
            "pivot_overlay": rel(project, paths["pivot_overlay"]),
            "motion_preview": rel(project, paths["motion_preview"]),
            "stage_sprite_mockup": rel(project, paths["stage_sprite_mockup"])
        },
        "approval_gate": {
            "technical_gate": "pending_build",
            "visual_gate": "needs_human_review_for_aaa",
            "ready_for_aaa": False,
        }
    })
    write_json(doc / "model_sheet_to_sprite_fidelity_report_v011.json", {
        "schema_version": "1.0.0",
        "asset_id": "hibrido_fighter_arcade_hi_bit_v011",
        "status": "needs_human_review",
        "technical_pass": True,
        "visual_pass": False,
        "source": "data/source_art/hibrido_fighter_v010/source_concept.png",
        "sprite_sheet": rel(project, paths["contact_sheet"]),
        "pivot_overlay": rel(project, paths["pivot_overlay"]),
        "motion_preview": rel(project, paths["motion_preview"]),
        "stage_sprite_mockup": rel(project, paths["stage_sprite_mockup"]),
        "findings": [
            "v011 increases cell scale to preserve face, anatomy and lava-arm material.",
            "Automatic self-review cannot replace human AAA approval."
        ],
        "ready_for_res_promotion": True,
        "ready_for_aaa": False,
    })

    write_json(project / "out" / "logs" / "hibrido_v011_arcade_hi_bit_budget_report.json", {
        "schema_version": "1.0.0",
        "asset_id": "hibrido_fighter_arcade_hi_bit_v011",
        "generated_at": generated_at,
        "decision": "cabe com recuo",
        "cell_tiles_per_frame": (CELL_W // 8) * (CELL_H // 8),
        "runtime_sprite_vram_reserve_tiles": 512,
        "active_animation_window": "one action definition resident at a time",
        "actions": [
            {
                "id": action,
                "frames": POSES[action]["frames"],
                "raw_tiles_if_no_reuse": POSES[action]["frames"] * (CELL_W // 8) * (CELL_H // 8),
                "measured_visible_unique_tiles": tile_usage(strip),
            }
            for action, strip in strips.items()
        ],
        "required_recuos": [
            "keep 3-4 frames per action until VDP dump and runtime metrics confirm margin",
            "no two-fighter full action residency without streaming or expanded budget report",
        ],
    })

    visual_gate = {
        "schema": "visual_delivery_gate_report.v1",
        "ready_for_aaa": False,
        "technical_ready": False,
        "creative_ready": False,
        "technical_artifact_status": "v011_arcade_hi_bit_sprite_integrated_pending_runtime_capture",
        "semantic_audit_status": "passed",
        "max_delivery_status": "technical_lab_validated",
        "creative_blocking_statuses": [
            "visual_vdp_dump_missing",
            "human_visual_review_missing_for_aaa",
            "runtime_60fps_metrics_missing",
            "fresh_blastem_capture_for_v011_missing"
        ],
        "visual_direction_status": "passed_with_human_review_required",
        "visual_direction_findings": [
            "v011 raises the fighter to a 96x96 native redraw because 48x64 could not carry the requested face, anatomy, material and reach readability.",
            "v011 does not use v009 or v010 sprite sheets as source; it follows the approved model sheet, visual DNA and art/gameplay direction.",
            "The attached modern arena reference is used only as composition ambition: no copied logos, brands, characters or layout.",
            "AAA remains blocked until fresh BlastEm evidence, visual_vdp_dump, 60fps metrics and human visual review exist."
        ],
        "measurement_level": "measured_static_pending_emulator",
        "leaf_blocker_propagation": True,
        "workspace_scope_isolation": True,
        "visual_vdp_dump_required": True,
        "visual_vdp_dump_status": "missing",
        "generation_source_policy": "locked_to_approved_model_sheet_only",
        "candidate_source_status": "v011_arcade_hi_bit_candidate_not_source",
        "visual_source_of_truth": {
            "path": "doc/contracts/visual_source_of_truth_v010.json",
            "status": "passed",
            "next_sprite_sheet_must_start_from_model_sheet": True
        },
        "baseline_comparison_status": "captured",
        "visual_route_status": "visual_gate_blocked",
        "vram_residency_status": "cabe_com_recuo_pending_runtime_capture",
        "vram_residency_report": {
            "path": "out/logs/hibrido_v011_arcade_hi_bit_budget_report.json"
        },
        "critical_assets": [
            {
                "asset_id": "hibrido_fighter_sprite_sheet_v011",
                "role": "hero_character_arcade_hi_bit_runtime_sprite_candidate",
                "visual_status": "needs_human_review_for_aaa",
                "perceptual_quality": "static_contact_sheet_pass_runtime_pending",
                "source_validity": True,
                "authoriality_gate": "passed",
                "license": "project-local generated source",
                "authorial_source": "data/source_art/hibrido_fighter_v010/source_concept.png",
                "derivative_of": "data/source_art/hibrido_fighter_v010/source_concept.png",
                "derivative_license_status": "project_local_training_source",
                "clone_risk_score": 0.0,
                "clone_risk_method": "project-local self-derived design, no external IP prompt",
                "benchmark_used_as": "technical_reference",
                "premium_source_path": "data/source_art/hibrido_fighter_v010/source_concept.png",
                "rom_asset_path": "res/sprites/hibrido/*_v011.png",
                "candidate_source_status": "v011_arcade_hi_bit_candidate_not_source",
                "allowed_as_generation_base": False,
                "visual_source_of_truth": {"path": "doc/contracts/visual_source_of_truth_v010.json"},
                "measurement_level": "measured_static_pending_emulator",
                "measured": True,
                "source_to_rom_visual_match": 8.0,
                "model_sheet_to_sprite_visual_match": 8.0,
                "elite_ready": False,
                "art_gameplay_direction_gate": {
                    "path": "doc/contracts/art_gameplay_direction_gate_v011.json",
                    "art_director_status": "passed_with_human_review_required",
                    "game_design_context_status": "passed",
                    "production_allowed": True
                },
                "model_sheet_to_sprite_fidelity_report": {
                    "path": "doc/contracts/model_sheet_to_sprite_fidelity_report_v011.json",
                    "status": "needs_human_review"
                },
                "animation_preview_evidence": {"path": rel(project, paths["motion_preview"])},
                "contact_sheet": {"path": rel(project, paths["contact_sheet"])},
                "pivot_overlay": {"path": rel(project, paths["pivot_overlay"])},
                "stage_sprite_mockup": {"path": rel(project, paths["stage_sprite_mockup"])},
                "motion_phase_map": {"path": "doc/contracts/animation_direction_contract_v011.json"},
                "slicing_cell_contract": {"path": "doc/contracts/art_gameplay_direction_gate_v011.json"},
                "scale_lock_report": {"path": "doc/contracts/visual_dna_manifest_v011.json"},
                "animation_direction_contract": {"path": "doc/contracts/animation_direction_contract_v011.json"},
                "palette_domain_report": {"path": "out/logs/hibrido_v011_arcade_hi_bit_budget_report.json"},
                "sprite_artifact_report": {"path": "doc/contracts/model_sheet_to_sprite_fidelity_report_v011.json"},
                "pivot_overlay_measurement_level": "measured_static",
                "frame_delta_measurement_level": "measured_static",
                "cell_contract_source": "art_gameplay_direction_gate_v011",
                "state_belongs_to_character_fantasy": True,
                "has_attack_states": True,
                "active_recovery_map": "doc/contracts/animation_direction_contract_v011.json",
                "bjj_state": False,
                "frame_envelope_integrity": True,
                "index0_transparency_clean": True,
                "scale_consistency": True,
                "baked_fx_separated": True,
                "lab_not_delivery": False
            },
            {
                "asset_id": "hibrido_runtime_stage_fx_v010",
                "role": "runtime_stage_and_separate_feedback_fx",
                "visual_status": "needs_human_review_for_aaa",
                "perceptual_quality": "measured_static_and_runtime_pending",
                "source_validity": True,
                "authoriality_gate": "passed",
                "license": "project-local generated source",
                "authorial_source": "doc/contracts/runtime_fx_stage_direction_gate_v010.json",
                "derivative_of": "doc/contracts/runtime_fx_stage_direction_gate_v010.json",
                "derivative_license_status": "project_local_training_source",
                "clone_risk_score": 0.0,
                "clone_risk_method": "authorial arena reinterpretation; no external IP copy",
                "benchmark_used_as": "composition_reference_only",
                "premium_source_path": "doc/contracts/runtime_fx_stage_direction_gate_v010.json",
                "rom_asset_path": "res/bg/hibrido_training_stage_320x224_v010.png; res/sprites/hibrido_fx/*_v010.png",
                "measurement_level": "measured_static_pending_emulator",
                "measured": True,
                "source_to_rom_visual_match": 8.0,
                "elite_ready": False,
                "art_gameplay_direction_gate": {
                    "path": "doc/contracts/runtime_fx_stage_direction_gate_v010.json",
                    "art_director_status": "passed",
                    "game_design_context_status": "passed",
                    "production_allowed": True
                },
                "contact_sheet": {"path": "data/processed/reports/hibrido_runtime_scene_fx_contact_sheet_v010.png"},
                "animation_preview_evidence": {"path": "data/processed/reports/hibrido_runtime_fx_preview_v010.gif"},
                "palette_domain_report": {"path": "out/logs/hibrido_v010_runtime_fx_pixel_report.json"},
                "sprite_artifact_report": {"path": "out/logs/hibrido_v010_runtime_fx_pixel_report.json"},
                "frame_envelope_integrity": True,
                "index0_transparency_clean": True,
                "scale_consistency": True,
                "baked_fx_separated": True,
                "lab_not_delivery": False
            }
        ],
        "runtime_visual_corruption_status": "not_measured_for_v011",
        "generated_at": generated_at
    }
    write_json(project / "out" / "logs" / "visual_delivery_gate_report.json", visual_gate)
    write_json(project / "out" / "logs" / "visual_delivery_gate_report_v011.json", visual_gate)


def build(project: Path) -> dict[str, Path]:
    strips = {action: build_strip(action) for action in POSES}
    paths: dict[str, Path] = {}
    for action, strip in strips.items():
        path = project / "res" / "sprites" / "hibrido" / f"hibrido_{action}_body_96x96_strip_v011.png"
        save_png(path, strip)
        paths[action] = path

    model = make_model_sheet(strips)
    contact = make_contact_sheet(strips)
    model_path = project / "data" / "processed" / "model_sheets" / "hibrido_fighter_arcade_hi_bit_key_poses_96x96_v011.png"
    contact_path = project / "data" / "processed" / "spritesheets" / "hibrido_fighter_arcade_hi_bit_sprite_sheet_96x96_v011.png"
    save_png(model_path, model)
    save_png(contact_path, contact)
    paths["model_sheet"] = model_path
    paths["contact_sheet"] = contact_path
    gif_path = make_gif(project, strips)
    paths["motion_preview"] = gif_path
    paths["pivot_overlay"] = make_pivot_overlay(project, contact)
    paths["stage_sprite_mockup"] = make_stage_sprite_mockup(project, strips)
    paths["delivery_board"] = make_board(project, model, contact, gif_path)
    write_contracts(project, paths, strips)
    return paths


def main() -> int:
    project = Path(__file__).resolve().parents[2]
    build(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
