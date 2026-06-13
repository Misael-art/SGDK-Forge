#!/usr/bin/env python3
"""Build SGDK-safe lab assets for the Neon Rain Ninja rooftop slice.

The premium source concept is stored separately in the project. This builder
creates strict 4-bit indexed runtime assets with small resident sets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


BG_PALETTE = [
    (255, 0, 255),
    (2, 6, 20),
    (5, 14, 35),
    (7, 29, 48),
    (9, 48, 76),
    (12, 83, 111),
    (16, 136, 156),
    (20, 202, 210),
    (82, 18, 112),
    (150, 22, 154),
    (229, 38, 170),
    (86, 50, 12),
    (180, 112, 22),
    (238, 210, 74),
    (88, 128, 160),
    (218, 236, 230),
]

FG_PALETTE = [
    (255, 0, 255),
    (1, 5, 12),
    (5, 13, 26),
    (8, 32, 42),
    (14, 64, 74),
    (16, 116, 132),
    (18, 210, 212),
    (62, 20, 80),
    (132, 22, 130),
    (228, 32, 168),
    (78, 46, 12),
    (160, 94, 18),
    (238, 194, 58),
    (74, 84, 92),
    (150, 166, 170),
    (232, 238, 220),
]

SPR_PALETTE = [
    (255, 0, 255),
    (2, 5, 12),
    (5, 14, 28),
    (10, 31, 55),
    (13, 74, 92),
    (18, 174, 190),
    (42, 226, 224),
    (76, 18, 92),
    (190, 32, 170),
    (244, 64, 188),
    (92, 58, 18),
    (194, 124, 28),
    (242, 206, 78),
    (148, 158, 166),
    (224, 232, 224),
    (238, 44, 54),
]


def apply_palette(img: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    paletted = img.convert("P")
    flat: list[int] = []
    for color in palette:
        flat.extend(color)
    paletted.putpalette(flat)
    return paletted


def save_p4(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if img.mode == "P":
        img.info["transparency"] = 0
    img.save(path, bits=4, optimize=False)


def make_bg_back() -> Image.Image:
    img = Image.new("P", (512, 224), 1)
    img.putpalette([v for rgb in BG_PALETTE for v in rgb])
    d = ImageDraw.Draw(img)

    d.rectangle((0, 0, 511, 223), fill=1)
    d.rectangle((0, 88, 511, 223), fill=2)
    d.rectangle((0, 148, 511, 223), fill=3)

    # Distant skyline, deliberately aligned to tile-ish columns.
    buildings = [
        (18, 96, 38, 176, 3), (46, 72, 70, 176, 4), (82, 108, 100, 176, 3),
        (116, 58, 148, 176, 4), (160, 82, 184, 176, 3), (198, 42, 230, 176, 4),
        (246, 90, 270, 176, 3), (284, 64, 318, 176, 4), (332, 76, 354, 176, 3),
        (372, 52, 410, 176, 4), (426, 100, 448, 176, 3), (462, 68, 500, 176, 4),
    ]
    for x0, y0, x1, y1, col in buildings:
        d.rectangle((x0, y0, x1, y1), fill=col)
        d.line((x0, y0, (x0 + x1) // 2, y0 - 10), fill=5)
        for wy in range(y0 + 10, y1 - 6, 16):
            for wx in range(x0 + 4, x1 - 4, 10):
                if ((wx + wy) // 10) & 1:
                    d.rectangle((wx, wy, wx + 2, wy + 5), fill=7)
                else:
                    d.rectangle((wx, wy, wx + 2, wy + 5), fill=9)

    # Tropical silhouettes.
    d.rectangle((0, 150, 24, 223), fill=1)
    for y in range(70, 156, 8):
        d.line((12, y, 34 + (y & 15), y - 24), fill=1)
        d.line((12, y, 0, y - 18), fill=1)
    d.rectangle((448, 154, 462, 223), fill=1)
    for y in range(122, 170, 10):
        d.line((455, y, 490, y - 18), fill=1)
        d.line((455, y, 426, y - 12), fill=1)

    # Rain and skyline atmosphere, pattern repeats to keep tiles sane.
    for x in range(-16, 528, 16):
        for y in range((x * 3) & 15, 224, 32):
            d.line((x, y, x - 4, y + 10), fill=14)
            d.point((x - 5, y + 11), fill=7)
    for x in range(0, 512, 32):
        d.rectangle((x + 2, 186, x + 18, 188), fill=6)
        d.rectangle((x + 8, 196, x + 28, 197), fill=9)

    return img


def draw_roof_tiles(d: ImageDraw.ImageDraw, x0: int, y0: int, x1: int, y1: int) -> None:
    d.rectangle((x0, y0, x1, y1), fill=2)
    d.rectangle((x0, y0, x1, y0 + 5), fill=5)
    for x in range(x0, x1 + 1, 16):
        d.line((x, y0 + 6, x - 8, y1), fill=1)
        d.line((x + 8, y0 + 6, x, y1), fill=3)
    for y in range(y0 + 10, y1, 12):
        d.line((x0, y, x1, y), fill=4)
    for x in range(x0 + 6, x1, 48):
        d.rectangle((x, y0 + 8, x + 22, y0 + 10), fill=6)
        d.rectangle((x + 4, y0 + 14, x + 18, y0 + 15), fill=9)


def make_bg_front() -> Image.Image:
    img = Image.new("P", (512, 224), 0)
    img.putpalette([v for rgb in FG_PALETTE for v in rgb])
    d = ImageDraw.Draw(img)

    draw_roof_tiles(d, 0, 176, 511, 223)
    draw_roof_tiles(d, 250, 128, 408, 159)
    d.rectangle((280, 154, 430, 192), fill=1)
    d.rectangle((296, 150, 430, 160), fill=4)
    for x in range(300, 430, 14):
        d.line((x, 151, x - 16, 184), fill=5)
    d.rectangle((316, 160, 424, 184), fill=2)
    d.rectangle((332, 162, 356, 176), fill=4)
    d.rectangle((382, 163, 396, 184), fill=3)
    d.rectangle((382, 163, 396, 165), fill=6)

    # Generator and cuttable cable.
    d.rectangle((174, 148, 216, 180), fill=3)
    d.rectangle((180, 154, 210, 176), fill=13)
    d.rectangle((186, 158, 200, 171), fill=1)
    d.rectangle((202, 160, 207, 166), fill=12)
    d.line((0, 116, 66, 128), fill=1, width=2)
    d.line((66, 128, 132, 136), fill=1, width=2)
    d.line((132, 136, 194, 148), fill=1, width=2)
    d.line((214, 152, 296, 126), fill=1, width=2)
    d.line((296, 126, 454, 116), fill=1, width=2)
    d.rectangle((190, 143, 202, 155), fill=12)
    d.line((190, 143, 202, 155), fill=15)
    d.line((202, 143, 190, 155), fill=15)

    # Light pools and shadow route cues. No alpha exists on the VDP, so the
    # cones are broken into scanline/dither cues instead of solid wedges.
    for row, y in enumerate(range(130, 176, 6)):
        half = 8 + (row * 7)
        col = 5 if (row & 1) else 6
        d.line((190 - half, y, 190 + half, y), fill=col)
        for x in range(190 - half + 4, 190 + half, 12):
            if ((x + y) & 16) == 0:
                d.point((x, y + 2), fill=9)
    for row, y in enumerate(range(102, 176, 7)):
        half = 5 + (row * 5)
        col = 7 if (row & 1) else 8
        d.line((480 - half, y, min(511, 480 + half), y), fill=col)
        for x in range(480 - half + 2, min(511, 480 + half), 14):
            if ((x ^ y) & 8) == 0:
                d.point((x, y + 2), fill=9)
    for x in range(0, 126, 12):
        d.rectangle((x, 170, x + 8, 175), fill=3)
    for x in range(252, 408, 12):
        d.rectangle((x, 122, x + 7, 127), fill=5)

    # Dragon sign scaffold and core at far right.
    d.rectangle((454, 76, 510, 176), fill=1)
    d.rectangle((464, 96, 496, 164), fill=3)
    d.rectangle((472, 116, 488, 148), fill=6)
    d.rectangle((476, 120, 492, 152), fill=9)
    d.line((464, 92, 488, 82), fill=9, width=2)
    d.line((488, 82, 506, 94), fill=9, width=2)
    d.line((466, 108, 504, 120), fill=6, width=2)
    d.line((462, 132, 502, 146), fill=9, width=2)
    d.rectangle((482, 88, 488, 94), fill=12)

    # Foreground pipes and plants for depth.
    d.rectangle((0, 204, 511, 223), fill=1)
    d.line((0, 200, 511, 200), fill=4)
    for x in range(16, 512, 64):
        d.rectangle((x, 196, x + 36, 202), fill=13)
        d.line((x, 202, x + 36, 202), fill=5)
    for x in (36, 430):
        for i in range(6):
            d.line((x, 214, x + 8 + (i * 5), 188 + (i * 2)), fill=4)
            d.line((x, 214, x - 10 - (i * 4), 190 + (i * 3)), fill=3)

    for x in range(10, 500, 37):
        y = 186 + ((x * 5) & 7)
        d.rectangle((x, y, x + 10, y + 1), fill=6 if (x & 16) else 9)
        d.point((x + 12, y + 2), fill=15)

    return img


def sprite_sheet(width: int = 128, height: int = 32) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("P", (width, height), 0)
    img.putpalette([v for rgb in SPR_PALETTE for v in rgb])
    return img, ImageDraw.Draw(img)


def draw_ninja_frame(d: ImageDraw.ImageDraw, ox: int, pose: int) -> None:
    # Wide cloak silhouette keeps the 32x32 frame readable on real hardware.
    d.polygon(
        [
            (ox + 10, 4), (ox + 21, 4), (ox + 29, 17), (ox + 27, 28),
            (ox + 18, 31), (ox + 4, 28), (ox + 3, 17)
        ],
        fill=1,
    )
    d.polygon([(ox + 8, 12), (ox + 24, 10), (ox + 29, 27), (ox + 10, 29)], fill=2)
    d.polygon([(ox + 5, 16), (ox + 14, 8), (ox + 12, 28), (ox + 2, 26)], fill=3)
    d.rectangle((ox + 12, 6, ox + 21, 14), fill=1)
    d.rectangle((ox + 15, 7, ox + 21, 9), fill=6)
    d.rectangle((ox + 11, 14, ox + 23, 22), fill=4)
    d.rectangle((ox + 13, 16, ox + 21, 25), fill=2)
    d.line((ox + 3, 26, ox + 27, 28), fill=5)
    d.line((ox + 5, 18, ox + 25, 12), fill=6)
    d.line((ox + 22, 8, ox + 31, 5), fill=8)
    d.line((ox + 22, 10, ox + 31, 9), fill=9)
    for px in range(6, 28, 4):
        d.point((ox + px, 20 + ((px + pose) & 3)), fill=5 if (px & 4) else 7)
    if pose == 1:
        d.line((ox + 10, 24, ox + 2, 31), fill=1, width=3)
        d.line((ox + 21, 23, ox + 31, 27), fill=1, width=3)
        d.line((ox + 11, 16, ox + 2, 14), fill=5, width=2)
    elif pose == 2:
        d.line((ox + 11, 24, ox + 1, 27), fill=1, width=3)
        d.line((ox + 20, 22, ox + 29, 31), fill=1, width=3)
        d.line((ox + 22, 14, ox + 31, 12), fill=6, width=2)
    elif pose == 3:
        d.rectangle((ox + 18, 11, ox + 31, 15), fill=14)
        d.rectangle((ox + 22, 10, ox + 31, 12), fill=15)
        d.line((ox + 8, 23, ox + 1, 30), fill=1, width=3)
        d.line((ox + 21, 22, ox + 28, 31), fill=1, width=3)
    else:
        d.line((ox + 10, 23, ox + 6, 31), fill=1, width=3)
        d.line((ox + 21, 23, ox + 26, 31), fill=1, width=3)


def make_ninja() -> Image.Image:
    img, d = sprite_sheet()
    for frame in range(4):
        draw_ninja_frame(d, frame * 32, frame)
    return img


def draw_guard_frame(d: ImageDraw.ImageDraw, ox: int, state: int) -> None:
    visor = [12, 12, 15, 4][state]
    body = 13 if state != 3 else 3
    dark = 1
    if state == 3:
        d.rectangle((ox + 7, 22, ox + 25, 26), fill=dark)
        d.rectangle((ox + 11, 18, ox + 21, 22), fill=body)
        d.rectangle((ox + 16, 16, ox + 23, 18), fill=4)
        return
    d.rectangle((ox + 8, 4, ox + 23, 15), fill=dark)
    d.rectangle((ox + 11, 7, ox + 22, 11), fill=visor)
    d.rectangle((ox + 7, 14, ox + 24, 27), fill=body)
    d.rectangle((ox + 10, 16, ox + 22, 25), fill=2)
    d.line((ox + 7, 17, ox + 1, 27), fill=dark, width=3)
    d.line((ox + 24, 17, ox + 31, 26), fill=dark, width=3)
    d.line((ox + 11, 27, ox + 7, 31), fill=dark, width=3)
    d.line((ox + 20, 27, ox + 27, 31), fill=dark, width=3)
    d.line((ox + 8, 20, ox + 24, 20), fill=5)
    d.point((ox + 13, 18), fill=6)
    d.point((ox + 18, 23), fill=6)
    if state == 1:
        d.rectangle((ox + 22, 4, ox + 24, 8), fill=12)
    if state == 2:
        d.rectangle((ox + 22, 4, ox + 25, 8), fill=15)
        d.line((ox + 24, 18, ox + 31, 18), fill=15)


def make_guard() -> Image.Image:
    img, d = sprite_sheet()
    for frame in range(4):
        draw_guard_frame(d, frame * 32, frame)
    return img


def make_dragon_core() -> Image.Image:
    img, d = sprite_sheet()
    for frame in range(4):
        ox = frame * 32
        d.rectangle((ox + 7, 4, ox + 25, 28), fill=1)
        d.rectangle((ox + 10, 8, ox + 22, 24), fill=3)
        d.rectangle((ox + 12, 10, ox + 24, 22), fill=5 if frame != 2 else 15)
        d.rectangle((ox + 14, 12, ox + 26, 20), fill=8 if frame != 1 else 12)
        d.rectangle((ox + 17, 14, ox + 24, 18), fill=9)
        d.line((ox + 4, 8, ox + 14, 4), fill=9, width=2)
        d.line((ox + 14, 4, ox + 28, 8), fill=6, width=2)
        d.line((ox + 4, 24, ox + 18, 28), fill=6, width=2)
        d.line((ox + 18, 28, ox + 30, 22), fill=9, width=2)
        if frame == 3:
            d.rectangle((ox + 11, 11, ox + 22, 23), fill=2)
            d.line((ox + 8, 16, ox + 26, 16), fill=15)
    return img


def make_spark() -> Image.Image:
    img, d = sprite_sheet()
    for frame in range(4):
        ox = frame * 32
        c = 12 if frame < 2 else 15
        d.polygon([(ox + 16, 1), (ox + 23, 11), (ox + 31, 16), (ox + 22, 21), (ox + 16, 31), (ox + 9, 21), (ox + 1, 16), (ox + 10, 10)], fill=6)
        d.polygon([(ox + 16, 5), (ox + 20, 13), (ox + 27, 16), (ox + 20, 19), (ox + 16, 27), (ox + 12, 19), (ox + 5, 16), (ox + 12, 13)], fill=9)
        d.line((ox + 16, 1, ox + 16, 31), fill=c, width=2)
        d.line((ox + 1, 16, ox + 31, 16), fill=15, width=2)
        d.line((ox + 5, 5, ox + 27, 27), fill=c, width=2)
        d.line((ox + 27, 5, ox + 5, 27), fill=15, width=2)
        d.rectangle((ox + 13, 13, ox + 19, 19), fill=12 if frame & 1 else 15)
        d.point((ox + 3 + frame, 8), fill=15)
        d.point((ox + 28 - frame, 24), fill=12)
    return img


def make_basic_bg_back() -> Image.Image:
    img = Image.new("P", (512, 224), 1)
    img.putpalette([v for rgb in BG_PALETTE for v in rgb])
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 511, 223), fill=2)
    d.rectangle((0, 176, 511, 223), fill=3)
    for x in range(32, 512, 96):
        d.rectangle((x, 96, x + 34, 176), fill=4)
    return img


def make_basic_bg_front() -> Image.Image:
    img = Image.new("P", (512, 224), 0)
    img.putpalette([v for rgb in FG_PALETTE for v in rgb])
    d = ImageDraw.Draw(img)
    d.rectangle((0, 176, 511, 223), fill=2)
    d.rectangle((180, 150, 210, 180), fill=4)
    d.line((0, 128, 511, 116), fill=1, width=1)
    return img


def make_basic_sprite() -> Image.Image:
    img, d = sprite_sheet()
    for frame in range(4):
        ox = frame * 32
        d.rectangle((ox + 13, 8, ox + 20, 25), fill=1)
        d.rectangle((ox + 11, 5, ox + 22, 12), fill=2)
        d.rectangle((ox + 15, 7, ox + 20, 8), fill=6)
    return img


def write_visual_lab_manifest(project: Path) -> None:
    manifest_path = project / "res" / "data" / "visual_lab_case.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "benchmark_id": "neon_rain_rooftop_slice_basic_vs_elite_v1",
        "reference_profile": "generic-megadrive-elite",
        "reference_asset": "data/source_art/neon_rooftop_slice/v001/neon_rooftop_slice_source.png",
        "minimum_delta": 0.04,
        "asset_weights": {"sprite": 0.42, "bg_a": 0.38, "bg_b": 0.20},
        "lanes": {
            "basic": {
                "label": "flat textual/blockout baseline",
                "bg_b": "res/data/visual_lab_basic/bg_basic_back.png",
                "bg_a": "res/data/visual_lab_basic/bg_basic_front.png",
                "sprite": "res/data/visual_lab_basic/spr_basic_ninja.png",
                "tags": ["blockout", "pre_aaa"]
            },
            "elite": {
                "label": "runtime rooftop slice",
                "bg_b": "res/neon/bg_neon_rooftop_back.png",
                "bg_a": "res/neon/bg_neon_rooftop_front.png",
                "sprite": "res/neon/spr_neon_ninja.png",
                "tags": ["runtime", "sgdk_safe", "playable"]
            }
        }
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()

    out = args.project / "res" / "neon"
    basic_out = args.project / "res" / "data" / "visual_lab_basic"
    save_p4(make_bg_back(), out / "bg_neon_rooftop_back.png")
    save_p4(make_bg_front(), out / "bg_neon_rooftop_front.png")
    save_p4(make_ninja(), out / "spr_neon_ninja.png")
    save_p4(make_guard(), out / "spr_neon_guard.png")
    save_p4(make_dragon_core(), out / "spr_neon_dragon_core.png")
    save_p4(make_spark(), out / "spr_neon_spark.png")
    save_p4(make_basic_bg_back(), basic_out / "bg_basic_back.png")
    save_p4(make_basic_bg_front(), basic_out / "bg_basic_front.png")
    save_p4(make_basic_sprite(), basic_out / "spr_basic_ninja.png")
    write_visual_lab_manifest(args.project)
    print(f"[OK] Neon Rain Ninja slice assets written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
