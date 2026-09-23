from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import struct
import zlib

from PIL import Image, ImageDraw


@dataclass(frozen=True)
class PaletteSpec:
    entries: list[tuple[int, int, int]]


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def load_palettes(project_root: Path) -> dict[str, PaletteSpec]:
    palette_path = project_root / "doc" / "contracts" / "palette_role_map_v001.json"
    payload = json.loads(palette_path.read_text(encoding="utf-8"))

    result: dict[str, PaletteSpec] = {}
    for pal_id, pal_payload in payload["palettes"].items():
        entries: list[tuple[int, int, int]] = []
        for entry in pal_payload["entries"]:
            entries.append(_hex_to_rgb(entry["rgb"]))
        result[pal_id] = PaletteSpec(entries=entries)

    return result


def make_indexed_canvas(w: int, h: int, pal: PaletteSpec) -> Image.Image:
    img = Image.new("P", (w, h), 0)
    palette_bytes: list[int] = []
    for r, g, b in pal.entries:
        palette_bytes.extend([r, g, b])
    while len(palette_bytes) < 256 * 3:
        palette_bytes.extend([0, 0, 0])
    img.putpalette(palette_bytes[: 256 * 3])
    return img


def draw_capsule(img: Image.Image, a: tuple[int, int], b: tuple[int, int], radius: int, color: int) -> None:
    px = img.load()
    ax, ay = a
    bx, by = b
    min_x = min(ax, bx) - radius - 1
    max_x = max(ax, bx) + radius + 1
    min_y = min(ay, by) - radius - 1
    max_y = max(ay, by) + radius + 1

    dx = bx - ax
    dy = by - ay
    denom = dx * dx + dy * dy
    if denom == 0:
        denom = 1

    r2 = radius * radius
    for y in range(min_y, max_y + 1):
        if y < 0 or y >= img.size[1]:
            continue
        for x in range(min_x, max_x + 1):
            if x < 0 or x >= img.size[0]:
                continue
            t_num = (x - ax) * dx + (y - ay) * dy
            t = t_num / denom
            if t < 0:
                cx, cy = ax, ay
            elif t > 1:
                cx, cy = bx, by
            else:
                cx = ax + t * dx
                cy = ay + t * dy
            ddx = x - cx
            ddy = y - cy
            if ddx * ddx + ddy * ddy <= r2:
                px[x, y] = color


def outline_1px(img: Image.Image, outline_color: int) -> None:
    w, h = img.size
    src = img.copy()
    s = src.load()
    d = img.load()
    for y in range(h):
        for x in range(w):
            if s[x, y] != 0:
                continue
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx = x + ox
                ny = y + oy
                if 0 <= nx < w and 0 <= ny < h and s[nx, ny] != 0:
                    d[x, y] = outline_color
                    break


def draw_body_frame(pal: PaletteSpec, pose: dict) -> tuple[Image.Image, Image.Image]:
    w, h = 48, 64
    body = make_indexed_canvas(w, h, pal)
    fx = make_indexed_canvas(w, h, pal)

    b = ImageDraw.Draw(body)

    stone_base = 4
    stone_shadow = 3
    stone_light = 5
    skin_base = 8
    bandage_base = 11
    accent = 13

    cx = 24 + int(pose.get("shift_x", 0))
    cy = 36 + int(pose.get("shift_y", 0))
    lean = int(pose.get("lean", 0))

    head_cx = cx + lean
    head_top = 8 + int(pose.get("head_y", 0))
    b.ellipse((head_cx - 6, head_top, head_cx + 6, head_top + 12), fill=skin_base)

    torso_top = 18
    torso_bottom = 50
    torso_w_top = 16
    torso_w_bottom = 12
    b.polygon(
        [
            (cx - torso_w_top + lean, torso_top),
            (cx + torso_w_top + lean, torso_top),
            (cx + torso_w_bottom, torso_bottom),
            (cx - torso_w_bottom, torso_bottom),
        ],
        fill=stone_base,
    )

    shoulder_y = 22
    hip_y = 46

    left_shoulder = (cx - 14 + lean, shoulder_y)
    right_shoulder = (cx + 14 + lean, shoulder_y)

    left_elbow = (cx - 18 + lean + int(pose.get("l_elbow_x", 0)), 32 + int(pose.get("l_elbow_y", 0)))
    right_elbow = (cx + 18 + lean + int(pose.get("r_elbow_x", 0)), 32 + int(pose.get("r_elbow_y", 0)))

    left_hand = (cx - 18 + lean + int(pose.get("l_hand_x", 0)), 44 + int(pose.get("l_hand_y", 0)))
    right_hand = (cx + 18 + lean + int(pose.get("r_hand_x", 0)), 44 + int(pose.get("r_hand_y", 0)))

    draw_capsule(body, left_shoulder, left_elbow, 4, stone_base)
    draw_capsule(body, left_elbow, left_hand, 4, stone_shadow)
    draw_capsule(body, right_shoulder, right_elbow, 4, stone_base)
    draw_capsule(body, right_elbow, right_hand, 4, stone_shadow)

    b.rectangle((left_hand[0] - 4, left_hand[1] - 2, left_hand[0] + 4, left_hand[1] + 4), fill=bandage_base)
    b.rectangle((right_hand[0] - 4, right_hand[1] - 2, right_hand[0] + 4, right_hand[1] + 4), fill=bandage_base)

    left_hip = (cx - 8, hip_y)
    right_hip = (cx + 8, hip_y)

    l_knee = (cx - 10 + int(pose.get("l_knee_x", 0)), 56 + int(pose.get("l_knee_y", 0)))
    r_knee = (cx + 10 + int(pose.get("r_knee_x", 0)), 56 + int(pose.get("r_knee_y", 0)))
    l_foot = (cx - 12 + int(pose.get("l_foot_x", 0)), 60 + int(pose.get("l_foot_y", 0)))
    r_foot = (cx + 12 + int(pose.get("r_foot_x", 0)), 60 + int(pose.get("r_foot_y", 0)))

    draw_capsule(body, left_hip, l_knee, 5, stone_base)
    draw_capsule(body, l_knee, l_foot, 5, stone_shadow)
    draw_capsule(body, right_hip, r_knee, 5, stone_base)
    draw_capsule(body, r_knee, r_foot, 5, stone_shadow)

    b.rectangle((cx - 10, torso_top + 6, cx + 10, torso_top + 10), fill=stone_light)
    b.point((cx - 6, torso_top + 14), fill=accent)
    b.point((cx - 5, torso_top + 15), fill=accent)
    b.point((cx - 4, torso_top + 16), fill=accent)

    outline_1px(body, 1)

    fx_draw = ImageDraw.Draw(fx)
    fx_draw.point((cx - 6, torso_top + 14), fill=8)
    fx_draw.point((cx - 5, torso_top + 15), fill=8)
    fx_draw.point((cx - 4, torso_top + 16), fill=8)

    flame_color = int(pose.get("flame", 0))
    if flame_color:
        for hx, hy in (left_hand, right_hand):
            fx_draw.polygon(
                [(hx - 6, hy + 4), (hx, hy - 10), (hx + 6, hy + 4), (hx, hy + 2)],
                fill=flame_color,
            )

    outline_1px(fx, 1)

    return body, fx


def make_strip(pal: PaletteSpec, frames: list[dict], mode: str) -> Image.Image:
    cell_w, cell_h = 48, 64
    strip = make_indexed_canvas(cell_w * len(frames), cell_h, pal)
    for i, pose in enumerate(frames):
        body, fx = draw_body_frame(pal, pose)
        src = body if mode == "body" else fx
        strip.paste(src, (i * cell_w, 0))
    return strip


def save_png(path: Path, img: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=False)
    trim_plte_chunk(path, max_entries=16)


def trim_plte_chunk(path: Path, max_entries: int) -> None:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return

    out = bytearray()
    out += data[:8]

    i = 8
    while i + 8 <= len(data):
        length = struct.unpack(">I", data[i : i + 4])[0]
        ctype = data[i + 4 : i + 8]
        chunk_data = data[i + 8 : i + 8 + length]
        crc = data[i + 8 + length : i + 12 + length]
        i = i + 12 + length

        if ctype == b"PLTE":
            trimmed = chunk_data[: max_entries * 3]
            out += struct.pack(">I", len(trimmed))
            out += ctype
            out += trimmed
            new_crc = zlib.crc32(ctype)
            new_crc = zlib.crc32(trimmed, new_crc)
            out += struct.pack(">I", new_crc & 0xFFFFFFFF)
            continue

        out += struct.pack(">I", length)
        out += ctype
        out += chunk_data
        out += crc

        if ctype == b"IEND":
            break

    path.write_bytes(bytes(out))


def build_model_sheet(project_root: Path, pal_body: PaletteSpec, pal_fx: PaletteSpec) -> None:
    poses = [
        {"lean": 0, "shift_x": 0, "flame": 0},
        {"lean": 2, "shift_x": -1, "flame": 3},
        {"lean": 4, "shift_x": -2, "flame": 4},
        {"lean": -2, "shift_x": 1, "flame": 5},
    ]
    body_cells = [draw_body_frame(pal_body, p)[0] for p in poses]
    fx_cells = [draw_body_frame(pal_fx, p)[1] for p in poses]

    w = 48 * 4
    h = 64 + 32

    sheet_body = make_indexed_canvas(w, h, pal_body)
    sheet_fx = make_indexed_canvas(w, h, pal_fx)

    for i, cell in enumerate(body_cells):
        sheet_body.paste(cell, (i * 48, 0))
    for i, cell in enumerate(fx_cells):
        sheet_fx.paste(cell, (i * 48, 0))

    d = ImageDraw.Draw(sheet_body)
    for i in range(16):
        x0 = i * 12
        d.rectangle((x0, 66, x0 + 11, 87), fill=i)

    d2 = ImageDraw.Draw(sheet_fx)
    for i in range(16):
        x0 = i * 12
        d2.rectangle((x0, 66, x0 + 11, 87), fill=i)

    save_png(project_root / "data" / "processed" / "model_sheets" / "hibrido_model_sheet_body_48x64_v001.png", sheet_body)
    save_png(project_root / "data" / "processed" / "model_sheets" / "hibrido_model_sheet_fx_48x64_v001.png", sheet_fx)


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    palettes = load_palettes(project_root)

    pal2 = palettes["PAL2"]
    pal3 = palettes["PAL3"]

    build_model_sheet(project_root, pal2, pal3)

    actions = [
        (
            "idle",
            8,
            [{"shift_y": (i % 2), "flame": 3 if i in (2, 6) else 0} for i in range(8)],
        ),
        (
            "walk",
            8,
            [
                {"l_knee_x": -2 if i in (1, 2, 3) else 1, "r_knee_x": 2 if i in (5, 6, 7) else -1, "flame": 2 if i % 4 == 0 else 0}
                for i in range(8)
            ],
        ),
        (
            "crouch",
            5,
            [{"shift_y": 6, "head_y": 4, "l_elbow_y": 4, "r_elbow_y": 4, "flame": 0} for _ in range(5)],
        ),
        (
            "jump",
            8,
            [{"shift_y": -6 if 2 <= i <= 5 else -2, "l_foot_y": -4, "r_foot_y": -4, "flame": 0} for i in range(8)],
        ),
        (
            "punch_light",
            6,
            [
                {"r_hand_x": 0 if i < 2 else 8, "r_elbow_x": 0 if i < 2 else 6, "flame": 4 if i >= 2 else 0}
                for i in range(6)
            ],
        ),
        (
            "kick_heavy",
            8,
            [
                {"l_foot_x": -2, "r_foot_x": 12 if 2 <= i <= 5 else 2, "r_knee_x": 10 if 2 <= i <= 5 else 2, "flame": 3 if i in (3, 4) else 0}
                for i in range(8)
            ],
        ),
        (
            "special_overheat",
            12,
            [
                {"l_hand_y": -6 if i >= 4 else 0, "r_hand_y": -6 if i >= 4 else 0, "flame": 5 if i >= 6 else 3 if i >= 3 else 0}
                for i in range(12)
            ],
        ),
    ]

    out_dir = project_root / "res" / "sprites" / "hibrido"

    for action_id, frame_count, frames in actions:
        frames = frames[:frame_count]
        strip_body = make_strip(pal2, frames, "body")
        strip_fx = make_strip(pal3, frames, "fx")

        save_png(out_dir / f"hibrido_{action_id}_body_48x64_strip_v001.png", strip_body)
        save_png(out_dir / f"hibrido_{action_id}_fx_48x64_strip_v001.png", strip_fx)


if __name__ == "__main__":
    main()
