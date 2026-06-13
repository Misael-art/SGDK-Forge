#!/usr/bin/env python3
"""
Gera os assets autorais do BENCHMARK_VISUAL_LAB.

Saidas:
- referencia high-res do armored sentinel
- 4 paines half-screen indexados para BG_A / BG_B
- 2 sprite sheets indexados (basic / elite)
- manifesto do caso visual para o agregador
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_NAME = "BENCHMARK_VISUAL_LAB [VER.001] [SGDK 211] [GEN] [TOOL] [TEST]"
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
PROJECT_ROOT = WORKSPACE_ROOT / "SGDK_projects" / PROJECT_NAME
REFERENCE_DIR = PROJECT_ROOT / "doc" / "03_art" / "reference"
BG_DIR = PROJECT_ROOT / "res" / "bgs"
SPRITE_DIR = PROJECT_ROOT / "res" / "sprites"
DATA_DIR = PROJECT_ROOT / "res" / "data"

HALF_W = 160
SCREEN_H = 224
SPR_W = 32
SPR_H = 48
SPR_FRAMES = 3

BASIC_BG_PALETTE = [
    (36, 40, 52),
    (50, 56, 68),
    (58, 64, 78),
    (70, 78, 94),
    (82, 92, 108),
    (94, 104, 118),
    (108, 116, 126),
    (120, 126, 134),
    (128, 118, 110),
    (136, 126, 118),
    (144, 134, 126),
    (154, 144, 138),
    (162, 154, 146),
    (174, 164, 156),
    (186, 176, 166),
    (204, 194, 184),
]

ELITE_BG_PALETTE = [
    (10, 12, 20),
    (18, 22, 34),
    (26, 34, 46),
    (32, 44, 58),
    (44, 56, 70),
    (56, 68, 78),
    (68, 78, 84),
    (82, 90, 92),
    (96, 96, 88),
    (112, 104, 88),
    (126, 112, 90),
    (142, 124, 96),
    (164, 138, 104),
    (184, 154, 114),
    (206, 182, 138),
    (228, 214, 176),
]

BASIC_SPRITE_PALETTE = [
    (255, 0, 255),
    (62, 70, 82),
    (74, 84, 96),
    (86, 94, 106),
    (100, 108, 118),
    (112, 118, 126),
    (124, 128, 136),
    (138, 140, 146),
    (152, 152, 154),
    (168, 134, 126),
    (182, 144, 136),
    (196, 154, 146),
    (212, 164, 154),
    (96, 76, 84),
    (122, 94, 100),
    (146, 114, 114),
]

ELITE_SPRITE_PALETTE = [
    (255, 0, 255),
    (6, 8, 14),
    (20, 24, 34),
    (40, 48, 62),
    (70, 84, 98),
    (110, 126, 136),
    (154, 168, 176),
    (214, 224, 230),
    (80, 28, 34),
    (118, 38, 42),
    (164, 52, 56),
    (208, 82, 70),
    (92, 74, 34),
    (134, 104, 42),
    (180, 148, 58),
    (236, 216, 142),
]


def ensure_dirs() -> None:
    for path in (REFERENCE_DIR, BG_DIR, SPRITE_DIR, DATA_DIR):
        path.mkdir(parents=True, exist_ok=True)


def palette_bytes(colors: list[tuple[int, int, int]]) -> list[int]:
    flat: list[int] = []
    for rgb in colors:
        flat.extend(rgb)
    while len(flat) < 768:
        flat.extend((0, 0, 0))
    return flat[:768]


def make_indexed(size: tuple[int, int], palette: list[tuple[int, int, int]], transparent: bool = False) -> Image.Image:
    img = Image.new("P", size, 0 if transparent else 1)
    img.putpalette(palette_bytes(palette))
    return img


def fill_vertical_gradient(img: Image.Image, top_idx: int, bottom_idx: int) -> None:
    width, height = img.size
    pixels = img.load()
    span = max(1, height - 1)
    for y in range(height):
        alpha = y / span
        index = round(top_idx + ((bottom_idx - top_idx) * alpha))
        for x in range(width):
            pixels[x, y] = index


def checker_fill(img: Image.Image, box: tuple[int, int, int, int], color_a: int, color_b: int, step: int = 2, offset: int = 0) -> None:
    pixels = img.load()
    left, top, right, bottom = box
    for y in range(top, bottom):
        for x in range(left, right):
            tile = (((x + offset) // step) + ((y + offset) // step)) & 1
            pixels[x, y] = color_a if tile == 0 else color_b


def scatter_noise(img: Image.Image, box: tuple[int, int, int, int], colors: list[int], stride: int) -> None:
    pixels = img.load()
    left, top, right, bottom = box
    for y in range(top, bottom):
        for x in range(left, right):
            if ((x * 3) + (y * 5)) % stride == 0:
                pixels[x, y] = colors[((x + y) // stride) % len(colors)]


def draw_basic_bg_b() -> Image.Image:
    img = make_indexed((HALF_W, SCREEN_H), BASIC_BG_PALETTE)
    fill_vertical_gradient(img, 3, 5)
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, HALF_W, 88), fill=4)
    draw.rectangle((0, 88, HALF_W, 148), fill=5)

    for idx, x in enumerate((10, 28, 46, 72, 102, 126, 142)):
        tower_h = 56 + (idx * 4)
        draw.rectangle((x, 82, x + 10, 82 + tower_h), fill=6)
        draw.rectangle((x + 2, 72, x + 8, 82), fill=7)

    for band_y in (26, 42, 58):
        for x in range(0, HALF_W, 16):
            draw.ellipse((x - 8, band_y - 6, x + 28, band_y + 12), fill=5)

    draw.rectangle((0, 148, HALF_W, SCREEN_H), fill=7)
    for x in range(0, HALF_W, 8):
        draw.line((x, 170, x + 6, 168), fill=8)
        draw.line((x, 190, x + 6, 188), fill=8)
    return img


def draw_basic_bg_a() -> Image.Image:
    img = make_indexed((HALF_W, SCREEN_H), BASIC_BG_PALETTE)
    fill_vertical_gradient(img, 0, 0)
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, HALF_W, SCREEN_H), fill=0)
    floor_y = 176
    draw.rectangle((0, floor_y, HALF_W, SCREEN_H), fill=9)
    for x in range(0, HALF_W, 20):
        draw.rectangle((x, 92, x + 12, floor_y), fill=10 + ((x // 20) % 2))
        draw.rectangle((x + 2, 88, x + 10, 96), fill=12)
        draw.arc((x - 6, 108, x + 18, 150), start=0, end=180, fill=13)

    draw.rectangle((54, 58, 106, floor_y), fill=8)
    draw.rectangle((60, 66, 100, 84), fill=11)
    draw.rectangle((66, 86, 94, 122), fill=9)
    draw.rectangle((50, 128, 110, 136), fill=11)

    checker_fill(img, (0, 86, HALF_W, floor_y), 8, 9, step=2)
    scatter_noise(img, (0, 80, HALF_W, SCREEN_H), [10, 11, 12, 13, 14], 5)
    return img


def draw_elite_bg_b() -> Image.Image:
    img = make_indexed((HALF_W, SCREEN_H), ELITE_BG_PALETTE)
    fill_vertical_gradient(img, 1, 5)
    draw = ImageDraw.Draw(img)

    checker_fill(img, (0, 0, HALF_W, 110), 2, 3, step=4)
    for band_y in (18, 34, 52):
        for x in range(-8, HALF_W + 8, 24):
            draw.ellipse((x, band_y, x + 34, band_y + 14), fill=4 if (x // 24) % 2 == 0 else 5)

    for idx, x in enumerate((8, 22, 48, 76, 102, 132)):
        peak = 112 - (idx * 6)
        draw.polygon([(x, 148), (x + 10, peak), (x + 24, 148)], fill=3 + (idx % 2))
        draw.rectangle((x + 4, peak + 18, x + 18, 148), fill=4 + (idx % 3))

    draw.rectangle((0, 150, HALF_W, SCREEN_H), fill=2)
    for x in range(0, HALF_W, 16):
        draw.line((x, 182, x + 10, 178), fill=4)
    checker_fill(img, (0, 150, HALF_W, SCREEN_H), 2, 4, step=2, offset=1)
    return img


def draw_elite_bg_a() -> Image.Image:
    img = make_indexed((HALF_W, SCREEN_H), ELITE_BG_PALETTE)
    fill_vertical_gradient(img, 0, 0)
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, HALF_W, SCREEN_H), fill=0)
    floor_y = 180
    draw.rectangle((0, 120, HALF_W, SCREEN_H), fill=2)
    draw.rectangle((0, floor_y, HALF_W, SCREEN_H), fill=6)
    checker_fill(img, (0, floor_y, HALF_W, SCREEN_H), 6, 8, step=2)

    for y in (18, 34, 52, 70, 88):
        draw.ellipse((-12, y, 76, y + 18), fill=1)
        draw.ellipse((44, y + 6, 132, y + 24), fill=1)
        draw.ellipse((100, y, 176, y + 18), fill=2)

    draw.rectangle((8, 102, 152, floor_y), fill=4)
    draw.rectangle((16, 108, 144, floor_y - 10), fill=5)

    for x in (16, 48, 80, 112, 136):
        draw.rectangle((x, 94, x + 8, floor_y), fill=7)
        draw.rectangle((x + 1, 92, x + 7, 100), fill=10)
    for x in (26, 58, 90, 122):
        draw.arc((x - 8, 126, x + 22, 170), start=0, end=180, fill=9)

    draw.rectangle((52, 60, 108, 136), fill=5)
    draw.rectangle((60, 70, 100, 86), fill=9)
    draw.rectangle((68, 92, 92, 126), fill=4)
    draw.rectangle((46, 136, 114, 144), fill=8)
    draw.line((58, 74, 100, 74), fill=13)
    draw.line((54, 140, 106, 140), fill=11)
    checker_fill(img, (8, 102, 152, floor_y), 5, 6, step=3)

    for x in range(0, HALF_W, 20):
        draw.line((x, 164, x + 18, 156), fill=4)
    return img


def _draw_body_base(draw: ImageDraw.ImageDraw, ox: int, palette: dict[str, int], frame: int, elite: bool) -> None:
    head_y = 6 - (1 if elite and frame == 1 else 0)
    torso_shift = -1 if frame == 2 else 0
    cape_shift = 1 if frame == 1 else 0

    draw.rectangle((ox + 11, head_y, ox + 20, head_y + 8), fill=palette["steel_mid"])
    draw.rectangle((ox + 10, head_y + 2, ox + 11, head_y + 7), fill=palette["outline"])
    draw.rectangle((ox + 20, head_y + 2, ox + 21, head_y + 7), fill=palette["outline"])

    draw.rectangle((ox + 8, 14 + torso_shift, ox + 23, 31 + torso_shift), fill=palette["steel_dark"])
    draw.rectangle((ox + 12, 16 + torso_shift, ox + 19, 28 + torso_shift), fill=palette["steel_mid"])
    draw.rectangle((ox + 13, 18 + torso_shift, ox + 18, 23 + torso_shift), fill=palette["steel_light"])
    draw.rectangle((ox + 5, 16, ox + 8, 28), fill=palette["arm"])
    draw.rectangle((ox + 23, 16, ox + 26, 28), fill=palette["arm"])
    draw.rectangle((ox + 9, 31, ox + 14, 44), fill=palette["leg"])
    draw.rectangle((ox + 17, 31, ox + 22, 44), fill=palette["leg"])
    draw.rectangle((ox + 7, 12, ox + 24, 14), fill=palette["outline"])
    draw.rectangle((ox + 10, 44, ox + 14, 47), fill=palette["outline"])
    draw.rectangle((ox + 17, 44, ox + 21, 47), fill=palette["outline"])

    draw.polygon(
        [
            (ox + 7, 16),
            (ox + 4, 26 + cape_shift),
            (ox + 6, 40 + cape_shift),
            (ox + 10, 44 + cape_shift),
            (ox + 12, 28),
        ],
        fill=palette["cape_dark"],
    )
    draw.polygon(
        [
            (ox + 24, 16),
            (ox + 27, 28 - cape_shift),
            (ox + 26, 40),
            (ox + 22, 44),
            (ox + 20, 28),
        ],
        fill=palette["cape_mid"],
    )


def draw_basic_sentinel_sheet() -> Image.Image:
    img = make_indexed((SPR_W * SPR_FRAMES, SPR_H), BASIC_SPRITE_PALETTE, transparent=True)
    draw = ImageDraw.Draw(img)
    palette = {
        "outline": 3,
        "steel_dark": 4,
        "steel_mid": 4,
        "steel_light": 5,
        "arm": 5,
        "leg": 5,
        "cape_dark": 4,
        "cape_mid": 4,
    }

    for frame in range(SPR_FRAMES):
        ox = frame * SPR_W
        _draw_body_base(draw, ox, palette, frame, elite=False)
        draw.rectangle((ox + 11, 9, ox + 20, 10), fill=6)
        draw.rectangle((ox + 10, 21, ox + 21, 24), fill=5)
        draw.rectangle((ox + 9, 31, ox + 22, 33), fill=5)
        draw.rectangle((ox + 12, 24, ox + 19, 27), fill=6)
        draw.rectangle((ox + 13, 34, ox + 18, 40), fill=6)
    return img


def _dither_block(img: Image.Image, ox: int, box: tuple[int, int, int, int], color_a: int, color_b: int, phase: int = 0) -> None:
    pixels = img.load()
    left, top, right, bottom = box
    for y in range(top, bottom):
        for x in range(left, right):
            pixels[ox + x, y] = color_a if ((x + y + phase) & 1) == 0 else color_b


def draw_elite_sentinel_sheet() -> Image.Image:
    img = make_indexed((SPR_W * SPR_FRAMES, SPR_H), ELITE_SPRITE_PALETTE, transparent=True)
    draw = ImageDraw.Draw(img)
    palette = {
        "outline": 1,
        "steel_dark": 2,
        "steel_mid": 4,
        "steel_light": 7,
        "arm": 13,
        "leg": 4,
        "cape_dark": 8,
        "cape_mid": 10,
    }

    for frame in range(SPR_FRAMES):
        ox = frame * SPR_W
        _draw_body_base(draw, ox, palette, frame, elite=True)

        draw.rectangle((ox + 9, 5, ox + 22, 14), outline=1, fill=2)
        draw.line((ox + 13, 8, ox + 18, 8), fill=7)
        draw.line((ox + 10, 14, ox + 21, 14), fill=1)
        draw.line((ox + 11, 17, ox + 20, 17), fill=15)
        draw.line((ox + 11, 30, ox + 20, 30), fill=1)
        draw.rectangle((ox + 10, 15, ox + 21, 30), outline=1)
        draw.rectangle((ox + 12, 18, ox + 19, 26), fill=4)
        draw.rectangle((ox + 13, 19, ox + 18, 23), fill=7)
        draw.rectangle((ox + 13, 33, ox + 18, 42), fill=4)
        draw.rectangle((ox + 9, 31, ox + 14, 44), outline=1)
        draw.rectangle((ox + 17, 31, ox + 22, 44), outline=1)
        draw.rectangle((ox + 8, 16, ox + 11, 24), fill=13)
        draw.rectangle((ox + 20, 16, ox + 23, 24), fill=13)
        draw.rectangle((ox + 12, 15, ox + 16, 18), fill=14)
        draw.rectangle((ox + 17, 15, ox + 20, 18), fill=14)
        draw.line((ox + 7, 15, ox + 10, 13), fill=15)
        draw.line((ox + 21, 13, ox + 24, 15), fill=15)

        _dither_block(img, ox, (11, 18, 20, 26), 4, 7, phase=frame)
        _dither_block(img, ox, (9, 31, 14, 44), 2, 4, phase=frame)
        _dither_block(img, ox, (17, 31, 22, 44), 2, 7, phase=frame + 1)

        draw.polygon([(ox + 6, 17), (ox + 1, 26), (ox + 2, 46), (ox + 11, 47), (ox + 13, 29)], fill=8)
        draw.polygon([(ox + 25, 17), (ox + 30, 28), (ox + 29, 46), (ox + 20, 47), (ox + 19, 29)], fill=10)
        draw.polygon([(ox + 4, 16), (ox + 1, 22), (ox + 4, 28), (ox + 8, 20)], fill=8)
        draw.polygon([(ox + 27, 16), (ox + 30, 22), (ox + 27, 28), (ox + 23, 20)], fill=10)
        draw.polygon([(ox + 2, 40), (ox + 6, 47), (ox + 13, 47), (ox + 10, 39)], fill=8)
        draw.polygon([(ox + 29, 40), (ox + 25, 47), (ox + 18, 47), (ox + 21, 39)], fill=10)
        draw.line((ox + 3, 24, ox + 2, 45), fill=1)
        draw.line((ox + 29, 24, ox + 28, 45), fill=1)
        draw.line((ox + 7, 45, ox + 11, 47), fill=11)
        draw.line((ox + 20, 47, ox + 24, 45), fill=11)
        draw.line((ox + 5, 15, ox + 1, 22), fill=15)
        draw.line((ox + 26, 15, ox + 30, 22), fill=15)
        draw.line((ox + 6, 38, ox + 10, 41), fill=15)
        draw.line((ox + 21, 41, ox + 25, 38), fill=15)
    return img


def draw_reference_image() -> Image.Image:
    width = 640
    height = 448
    img = Image.new("RGB", (width, height), (8, 10, 18))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        if y < 170:
            color = (18 + (y // 10), 24 + (y // 8), 42 + (y // 6))
        else:
            color = (32 + (y // 12), 28 + (y // 14), 24 + (y // 18))
        draw.line((0, y, width, y), fill=color)

    for cloud_y in (56, 92, 128):
        for x in range(-40, width + 40, 72):
            tone = 60 + ((x // 72) % 3) * 12
            draw.ellipse((x, cloud_y, x + 140, cloud_y + 38), fill=(tone, tone + 8, tone + 20))

    for idx, x in enumerate((42, 96, 178, 244, 352, 438, 520)):
        draw.polygon(
            [(x, 320), (x + 36, 182 - idx * 6), (x + 82, 320)],
            fill=(28 + idx * 4, 34 + idx * 3, 42 + idx * 2),
        )

    body_x = 236
    draw.rectangle((body_x + 74, 120, body_x + 126, 166), fill=(86, 100, 122))
    draw.rectangle((body_x + 62, 166, body_x + 138, 274), fill=(54, 66, 84))
    draw.rectangle((body_x + 80, 180, body_x + 122, 250), fill=(132, 150, 164))
    draw.rectangle((body_x + 54, 176, body_x + 66, 260), fill=(118, 92, 40))
    draw.rectangle((body_x + 134, 176, body_x + 146, 260), fill=(118, 92, 40))
    draw.rectangle((body_x + 70, 274, body_x + 96, 388), fill=(70, 84, 98))
    draw.rectangle((body_x + 106, 274, body_x + 132, 388), fill=(70, 84, 98))
    draw.polygon([(body_x + 58, 176), (body_x + 28, 246), (body_x + 52, 380), (body_x + 84, 394), (body_x + 98, 270)], fill=(126, 42, 46))
    draw.polygon([(body_x + 142, 176), (body_x + 170, 254), (body_x + 154, 384), (body_x + 124, 394), (body_x + 108, 270)], fill=(192, 76, 58))
    draw.rectangle((body_x + 68, 146, body_x + 132, 156), fill=(228, 216, 158))
    draw.rectangle((body_x + 84, 168, body_x + 116, 188), fill=(214, 224, 232))

    for x in range(body_x + 80, body_x + 122, 6):
        draw.line((x, 186, x + 18, 198), fill=(190, 200, 208), width=2)
    for x in range(body_x + 74, body_x + 96, 4):
        draw.line((x, 292, x + 18, 356), fill=(104, 116, 126), width=2)
    for x in range(body_x + 110, body_x + 130, 4):
        draw.line((x, 292, x - 18, 356), fill=(104, 116, 126), width=2)

    draw.rectangle((0, 390, width, height), fill=(58, 52, 44))
    for x in range(0, width, 24):
        draw.line((x, 416, x + 20, 410), fill=(94, 86, 76), width=2)

    return img


def write_manifest() -> None:
    manifest = {
        "benchmark_id": "armored-sentinel-side-by-side",
        "reference_asset": "doc/03_art/reference/armored_sentinel_reference.png",
        "reference_profile": "generic-megadrive-elite",
        "minimum_delta": 0.12,
        "asset_weights": {
            "sprite": 0.45,
            "bg_a": 0.35,
            "bg_b": 0.20,
        },
        "lanes": {
            "basic": {
                "label": "BASIC",
                "critical_visual": True,
                "bg_b": "res/bgs/basic_bg_b.png",
                "bg_a": "res/bgs/basic_bg_a.png",
                "sprite": "res/sprites/spr_basic_sentinel.png",
                "reference_profile": "generic-megadrive-elite",
                "tags": ["flat", "weak-depth", "poor-separation"],
            },
            "elite": {
                "label": "ELITE",
                "critical_visual": True,
                "bg_b": "res/bgs/elite_bg_b.png",
                "bg_a": "res/bgs/elite_bg_a.png",
                "sprite": "res/sprites/spr_elite_sentinel.png",
                "reference_profile": "generic-megadrive-elite",
                "tags": ["dithered", "strong-silhouette", "depth-separated"],
            },
        },
        "modes": [
            "silhouette_lab",
            "layer_contrast_lab",
            "animation_readability_lab",
        ],
    }
    (DATA_DIR / "visual_lab_case.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    ensure_dirs()

    draw_reference_image().save(REFERENCE_DIR / "armored_sentinel_reference.png", "PNG")
    draw_basic_bg_b().save(BG_DIR / "basic_bg_b.png", "PNG")
    draw_basic_bg_a().save(BG_DIR / "basic_bg_a.png", "PNG")
    draw_elite_bg_b().save(BG_DIR / "elite_bg_b.png", "PNG")
    draw_elite_bg_a().save(BG_DIR / "elite_bg_a.png", "PNG")
    draw_basic_sentinel_sheet().save(SPRITE_DIR / "spr_basic_sentinel.png", "PNG")
    draw_elite_sentinel_sheet().save(SPRITE_DIR / "spr_elite_sentinel.png", "PNG")
    write_manifest()

    print(json.dumps(
        {
            "project_root": str(PROJECT_ROOT),
            "reference": str(REFERENCE_DIR / "armored_sentinel_reference.png"),
            "assets_generated": 7,
            "manifest": str(DATA_DIR / "visual_lab_case.json"),
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
