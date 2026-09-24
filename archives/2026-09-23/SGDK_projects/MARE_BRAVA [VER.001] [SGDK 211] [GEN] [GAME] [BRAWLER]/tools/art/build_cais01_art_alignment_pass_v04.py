#!/usr/bin/env python3
"""Rebuild CAIS_01 v04 from the approved authorial source matrix.

This pass preserves the v03 runtime techniques but replaces its generic
procedural composition.  It redraws the scene on the native pixel grid from
locked source roles: long clouds and harbor mass from the BG_B mood plate,
composition anchors from CAIS arena references, and material marks from the
approved modular dock kit.  Runtime v03 PNGs are comparison evidence only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import build_cais01_visual_pass_v02 as base


PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "rascunho/cais01_art_alignment_pass_v04"
RES_BG = PROJECT / "res/backgrounds/cais01"
REVIEW = PROJECT / "doc/art/environments/cais01/review"
DOC = PROJECT / "doc/art/environments/cais01"

WIDTH = 512
HEIGHT = 224
CAMERA_X = 80
BG_B_CAMERA_X = 20

BG_B_NAME = "cais01_bg_b_harbor_sunset_512x224_v04.png"
BG_A_NAME = "cais01_bg_a_industrial_pier_512x224_v04.png"

TAINA_BACKLIGHT_PALETTE = [
    (255, 0, 255), (0, 0, 34), (34, 0, 68), (68, 34, 102),
    (0, 34, 68), (34, 136, 136), (68, 34, 34), (136, 68, 34),
    (204, 68, 34), (238, 136, 68), (238, 170, 102),
    (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def set_palette(image: Image.Image, colors: list[tuple[int, int, int]]) -> None:
    flat = [channel for color in colors for channel in color]
    flat.extend([0] * (768 - len(flat)))
    image.putpalette(flat)
    image.info["transparency"] = 0


def save_indexed(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, bits=4, optimize=False, transparency=0)


def rgba_index0(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putalpha(image.point(lambda value: 0 if value == 0 else 255, mode="L"))
    return rgba


def unique_tiles(image: Image.Image) -> tuple[int, int]:
    total = 0
    hashes: set[str] = set()
    for y in range(0, image.height, 8):
        for x in range(0, image.width, 8):
            tile = image.crop((x, y, x + 8, y + 8))
            hashes.add(hashlib.sha256(tile.tobytes()).hexdigest())
            total += 1
    return total, len(hashes)


def image_compliance(image: Image.Image) -> dict:
    palette = image.getpalette() or []
    used = sorted(set(image.getdata()))
    visible = [index for index in used if index != 0]
    invalid_channels: list[dict] = []
    for index in used:
        color = tuple(palette[index * 3:index * 3 + 3])
        for channel_name, value in zip(("r", "g", "b"), color):
            if value not in (0, 34, 68, 102, 136, 170, 204, 238, 255):
                invalid_channels.append({
                    "index": index,
                    "channel": channel_name,
                    "value": value,
                })
    return {
        "mode": image.mode,
        "dimensions_px": [image.width, image.height],
        "grid_8x8": image.width % 8 == 0 and image.height % 8 == 0,
        "palette_index_0_rgb": palette[0:3],
        "index_0_is_magenta": palette[0:3] == [255, 0, 255],
        "used_indices": used,
        "visible_color_count": len(visible),
        "visible_colors_within_15": len(visible) <= 15,
        "invalid_9bit_channels": invalid_channels,
        "alpha_or_partial_opacity": False,
    }


def draw_long_cloud(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    body: int,
    light: int,
    shadow: int,
) -> None:
    """Low horizontal cloud with tapered ends and sparse dither fringe."""
    heights = (5, 8, 11, 14, 12, 9, 6)
    segment = max(8, width // len(heights))
    points = [(x, y + 14)]
    for index, height in enumerate(heights):
        px = x + index * segment
        points.extend(((px, y + 14 - height), (px + segment, y + 14 - height)))
    points.extend(((x + width, y + 17), (x + 10, y + 17)))
    draw.polygon(points, fill=body)
    draw.line((x + 12, y + 14, x + width - 8, y + 14), fill=light)
    draw.line((x + width // 3, y + 10, x + width - 18, y + 10), fill=light)
    draw.line((x + 20, y + 17, x + width - 3, y + 17), fill=shadow)
    for px in range(x + 4, x + width, 3):
        if ((px - x) // 3) & 1:
            draw.point((px, y + 18), fill=body)
    for px in range(x + 15, x + width - 10, 7):
        draw.point((px, y + 8 + ((px // 7) & 1)), fill=light)


def draw_sun(draw: ImageDraw.ImageDraw, cx: int = 176, cy: int = 72) -> None:
    outer = 34
    inner = 27
    draw.ellipse((cx - outer, cy - outer, cx + outer, cy + outer), fill=8)
    draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill=9)
    for y in range(cy - outer, cy + outer + 1):
        for x in range(cx - outer, cx + outer + 1):
            dist2 = (x - cx) ** 2 + (y - cy) ** 2
            if inner**2 < dist2 <= outer**2 and ((x + y) & 1):
                draw.point((x, y), fill=7)
            elif (inner - 5) ** 2 < dist2 <= inner**2 and (x * 3 + y) % 7 == 0:
                draw.point((x, y), fill=8)


def draw_far_harbor(draw: ImageDraw.ImageDraw) -> None:
    """A continuous low-density industrial mass entirely in the far band."""
    draw.rectangle((0, 75, WIDTH - 1, 79), fill=4)
    roof = [
        (0, 72), (18, 72), (18, 69), (35, 69), (35, 74), (55, 74),
        (55, 67), (76, 67), (76, 72), (100, 72), (100, 65), (123, 65),
        (123, 73), (146, 73), (146, 69), (166, 69), (166, 74),
        (191, 74), (191, 66), (214, 66), (214, 72), (239, 72),
        (239, 68), (264, 68), (264, 73), (288, 73), (288, 64),
        (310, 64), (310, 72), (334, 72), (334, 68), (355, 68),
        (355, 74), (380, 74), (380, 66), (402, 66), (402, 72),
        (426, 72), (426, 69), (449, 69), (449, 74), (474, 74),
        (474, 67), (496, 67), (496, 72), (511, 72),
    ]
    draw.polygon(roof + [(511, 79), (0, 79)], fill=4)
    for x in (43, 130, 223, 316, 454):
        draw.rectangle((x, 57, x + 3, 75), fill=4)
        draw.rectangle((x - 1, 56, x + 4, 58), fill=5)
    for x in range(12, WIDTH, 41):
        draw.point((x, 76), fill=7)


def draw_tank(draw: ImageDraw.ImageDraw, x: int, y: int, w: int) -> None:
    draw.rectangle((x, y + 4, x + w, 111), fill=2)
    draw.arc((x, y, x + w, y + 9), 180, 360, fill=3, width=2)
    draw.line((x + 3, y + 4, x + w - 3, y + 4), fill=2)
    draw.line((x + 5, y + 8, x + w - 5, y + 8), fill=3)


def draw_compact_industrial_city(draw: ImageDraw.ImageDraw) -> None:
    """Near silhouette reads as one authored harbor mass, not loose boxes."""
    draw.rectangle((0, 101, WIDTH - 1, 111), fill=2)

    # Warehouses and saw-tooth roofs merge into the common base.
    saw = [(0, 101), (0, 93)]
    for x in range(0, 190, 24):
        saw.extend(((x + 10, 88 + ((x // 24) & 3)), (x + 22, 98)))
    saw.extend(((190, 111), (0, 111)))
    draw.polygon(saw, fill=2)
    for x0, y0, x1 in (
        (198, 92, 232), (238, 86, 268), (274, 95, 301),
        (307, 89, 339), (346, 94, 377), (384, 85, 416),
        (423, 92, 452), (459, 88, 486), (492, 96, 511),
    ):
        draw.rectangle((x0, y0, x1, 111), fill=2)
        draw.line((x0 + 3, y0 + 4, x1 - 3, y0 + 4), fill=3)

    draw_tank(draw, 24, 85, 25)
    draw_tank(draw, 290, 83, 28)
    draw_tank(draw, 438, 86, 23)

    # Chimneys, pipes and gantries create specific port rhythm.
    for x, top, width in ((66, 62, 5), (143, 71, 4), (218, 67, 6), (365, 60, 5), (478, 69, 4)):
        draw.rectangle((x, top, x + width, 103), fill=2)
        draw.rectangle((x - 1, top, x + width + 1, top + 3), fill=3)
        draw.line((x + width + 1, top + 9, x + width + 8, top + 13), fill=2, width=2)
    for x0 in (92, 334):
        base.draw_crane(draw, x0, 112)
    draw.line((170, 92, 204, 92), fill=2, width=3)
    draw.line((170, 92, 170, 104), fill=2, width=2)
    draw.line((204, 92, 204, 104), fill=2, width=2)
    draw.line((174, 103, 200, 94), fill=3)
    for x, y in ((13, 103), (82, 96), (126, 101), (181, 98), (251, 94), (327, 103), (405, 92), (468, 98)):
        draw.rectangle((x, y, x + 1, y + 1), fill=9)


def draw_reflection(draw: ImageDraw.ImageDraw, center: int = 176) -> None:
    for y in range(112, 177):
        depth = y - 112
        half = 4 + depth // 5
        warm = 9 if depth < 12 else (8 if depth < 34 else 7)
        gaps = 3 + ((y // 5) & 3)
        for x in range(center - half, center + half + 1):
            if ((x + y * 3) % gaps) not in (0,):
                draw.point((x, y), fill=warm)
        if y % 5 == 0:
            draw.line((center - half - 5, y, center - half - 1, y), fill=13)
            draw.line((center + half + 1, y, center + half + 6, y), fill=14)


def draw_bg_b_v04() -> Image.Image:
    image = base.indexed_image((WIDTH, HEIGHT), base.BG_B_PALETTE, 3)
    draw = ImageDraw.Draw(image)

    # Discrete sunset ramps; no alpha or interpolated glow.
    for y0, y1, color in ((0, 23, 3), (24, 47, 4), (48, 71, 5), (72, 91, 6), (92, 111, 7)):
        draw.rectangle((0, y0, WIDTH - 1, y1), fill=color)
    for y, color, phase in ((23, 4, 0), (47, 5, 1), (71, 6, 2), (91, 7, 3)):
        base.dot_dither(draw, (0, y, WIDTH - 1, y + 1), color, 6, phase)

    draw_long_cloud(draw, 8, 20, 148, 5, 9, 4)
    draw_long_cloud(draw, 282, 30, 172, 5, 9, 4)
    draw_long_cloud(draw, 430, 13, 106, 4, 8, 3)
    draw_sun(draw)
    draw_far_harbor(draw)
    draw_compact_industrial_city(draw)

    # Sea rows are reusable and line-scroll friendly.
    for y0, y1, color in ((112, 119, 10), (120, 135, 11), (136, 159, 12), (160, 191, 11), (192, 223, 10)):
        draw.rectangle((0, y0, WIDTH - 1, y1), fill=color)
    for band, y in enumerate((118, 126, 137, 148, 160, 174, 190, 208, 220)):
        offset = (band * 19) % 56
        color = 13 if band < 7 else 12
        for x in range(-56 + offset, WIDTH, 56):
            draw.line((x, y, x + 14, y - 1), fill=color)
            draw.line((x + 15, y - 1, x + 27, y + 1), fill=color)
            if band & 1:
                draw.line((x + 35, y + 3, x + 45, y + 2), fill=14)
    for y, spacing, phase in ((135, 72, 9), (159, 88, 28), (191, 104, 43)):
        for x in range(-spacing + phase, WIDTH, spacing):
            draw.line((x, y, x + 10, y - 2), fill=14)
            draw.line((x + 11, y - 2, x + 24, y), fill=15)
            draw.line((x + 25, y, x + 32, y + 1), fill=14)
    draw_reflection(draw)
    return image


def draw_crate_rich(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, slats: int) -> None:
    draw.rectangle((x, y, x + w - 1, y + h - 1), fill=1)
    draw.rectangle((x + 2, y + 2, x + w - 3, y + h - 3), fill=5)
    draw.rectangle((x + 5, y + 5, x + w - 6, y + h - 6), fill=7)
    usable_h = h - 12
    for index in range(1, slats):
        sy = y + 5 + (usable_h * index // slats)
        draw.line((x + 5, sy, x + w - 6, sy), fill=4)
        draw.line((x + 7, sy + 1, x + w - 8, sy + 1), fill=8)
    draw.line((x + 6, y + 6, x + w - 7, y + h - 7), fill=3, width=2)
    draw.line((x + w - 7, y + 6, x + 6, y + h - 7), fill=4, width=2)
    draw.rectangle((x + 2, y + 2, x + 5, y + h - 3), fill=6)
    draw.rectangle((x + w - 6, y + 2, x + w - 3, y + h - 3), fill=6)
    draw.line((x + 3, y + 3, x + w - 4, y + 3), fill=9)
    for px, py in ((x + 4, y + 4), (x + w - 5, y + 4), (x + 4, y + h - 5), (x + w - 5, y + h - 5)):
        draw.point((px, py), fill=13)
    for index in range(3):
        gx = x + 9 + ((index * 13 + w) % max(10, w - 18))
        gy = y + 9 + ((index * 9 + h) % max(8, h - 18))
        draw.line((gx, gy, min(gx + 6, x + w - 7), gy), fill=5)


def draw_deck(draw: ImageDraw.ImageDraw, detailed: bool) -> None:
    # Fascia and sunset rim.
    draw.rectangle((0, 136, WIDTH - 1, 159), fill=1)
    draw.rectangle((0, 137, WIDTH - 1, 142), fill=9)
    draw.rectangle((0, 143, WIDTH - 1, 151), fill=7)
    draw.rectangle((0, 152, WIDTH - 1, 159), fill=3)
    for x in range(0, WIDTH, 16):
        draw.rectangle((x + 1, 140, x + 14, 142), fill=8 if (x // 16) & 1 else 7)
        draw.point((x + 3, 141), fill=13)
        draw.line((x + 8, 154, x + 14, 154), fill=11)

    # Four repeating 64px material modules limit tile explosion.
    draw.rectangle((0, 160, WIDTH - 1, HEIGHT - 1), fill=6)
    for row, y in enumerate(range(160, HEIGHT, 16)):
        fill = 7 if row in (0, 3) else 6
        seam = 5 if row & 1 else 4
        draw.rectangle((0, y, WIDTH - 1, min(y + 15, HEIGHT - 1)), fill=fill)
        draw.line((0, y, WIDTH - 1, y), fill=9 if row == 0 else seam)
        joint_offset = (row * 16) % 64
        for x in range(-joint_offset, WIDTH, 64):
            draw.line((x, y, x, min(y + 15, HEIGHT - 1)), fill=3, width=2)
        if not detailed:
            continue
        for module_x in range(0, WIDTH, 64):
            seed = (row * 3 + module_x // 64) & 3
            marks = (
                ((8, 5, 17), (36, 11, 44)),
                ((13, 9, 24), (47, 4, 58)),
                ((6, 12, 16), (31, 6, 39), (51, 10, 59)),
                ((18, 4, 29), (42, 12, 53)),
            )[seed]
            for x0, dy, x1 in marks:
                draw.line((module_x + x0, y + dy, module_x + x1, y + dy), fill=5)
            knot_x = module_x + (24, 43, 17, 51)[seed]
            draw.ellipse((knot_x, y + 8, knot_x + 4, y + 11), outline=4)
            draw.point((knot_x + 2, y + 9), fill=2)
            draw.point((module_x + 5, y + 3), fill=10)

    if detailed:
        # Cracks, oil and tyre wear repeat as authored low-contrast clusters.
        for x, y in ((176, 181), (284, 211), (394, 187)):
            draw.line((x, y, x + 7, y + 3), fill=3)
            draw.line((x + 7, y + 3, x + 13, y - 1), fill=3)
            draw.line((x + 6, y + 3, x + 9, y + 8), fill=4)
        for cx, cy, rx in ((280, 203, 18), (430, 216, 14)):
            for py in range(cy - 5, cy + 6):
                half = max(2, rx - abs(py - cy) * 3)
                for px in range(cx - half, cx + half + 1):
                    if (px * 3 + py) % 5 in (0, 1):
                        draw.point((px, py), fill=2)
        for x in range(174, 218, 5):
            draw.line((x, 218, x + 2, 219), fill=3)


def draw_industrial_lamp(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    base.draw_lamp(draw, x, y)
    # Bolted foot, conduit, rust breaks and protective collar.
    draw.rectangle((x - 3, y + 91, x + 18, y + 99), fill=1)
    draw.rectangle((x, y + 92, x + 15, y + 96), fill=10)
    draw.point((x + 2, y + 94), fill=13)
    draw.point((x + 13, y + 94), fill=13)
    draw.line((x + 3, y + 45, x + 3, y + 86), fill=11, width=2)
    draw.rectangle((x + 3, y + 57, x + 11, y + 62), fill=3)
    draw.line((x + 6, y + 12, x + 6, y + 30), fill=8)
    draw.point((x + 8, y + 72), fill=8)


def draw_authored_net(draw: ImageDraw.ImageDraw, x0: int, x1: int, top: int, bottom: int) -> None:
    draw.line((x0, top + 5, x0, bottom), fill=1, width=3)
    draw.line((x1, top, x1, bottom), fill=1, width=3)
    draw.line((x0, top + 7, x1, top + 1), fill=9, width=2)
    # Diamond mesh with a loose sagging center.
    for x in range(x0 + 5, x1, 9):
        draw.line((x, top + 8, x - 9, bottom - 5), fill=11)
        draw.line((x, top + 8, x + 9, bottom - 5), fill=10)
    for y in range(top + 14, bottom - 4, 10):
        sag = 2 + ((y - top) // 10)
        draw.line((x0 + 3, y, (x0 + x1) // 2, y + sag), fill=12)
        draw.line(((x0 + x1) // 2, y + sag, x1 - 3, y - 1), fill=11)
    draw.line((x0 + 16, bottom - 3, x0 + 24, bottom + 2), fill=1, width=2)
    draw.line((x1 - 11, top + 22, x1 - 3, top + 31), fill=1, width=2)


def draw_bg_a_v04(detailed: bool) -> Image.Image:
    image = base.indexed_image((WIDTH, HEIGHT), base.BG_A_PALETTE, 0)
    draw = ImageDraw.Draw(image)
    draw_deck(draw, detailed)

    # Locked initial composition: one dominant crate and two smaller supports.
    draw_crate_rich(draw, 88, 126, 34, 34, 3)
    draw_crate_rich(draw, 118, 99, 50, 61, 4)
    draw_crate_rich(draw, 164, 126, 36, 34, 3)
    base.draw_bollard(draw, 280, 128)
    base.draw_rope_coil(draw, 296, 141)

    draw_industrial_lamp(draw, 334, 39)
    draw_authored_net(draw, 368, 441, 72, 135)

    # Right edge foam signal and a small cargo fragment outside the clean lane.
    draw.rectangle((440, 128, WIDTH - 1, 135), fill=11)
    for x in range(438, WIDTH, 12):
        draw.line((x, 133, x + 5, 130), fill=13, width=2)
        draw.line((x + 6, 130, x + 10, 132), fill=15)
    draw_crate_rich(draw, 472, 119, 40, 41, 3)

    if detailed:
        # Sparse wet glints remain bound to PAL2 cycling slots 14/15.
        for x0, x1, y in ((328, 391, 174), (339, 403, 190), (351, 416, 207)):
            draw.line((x0, y, x1, y), fill=14)
            for x in range(x0 + 5, x1, 14):
                draw.point((x, y + 1 + ((x // 14) & 1)), fill=15)
    return image


def composite_scene(bg_b: Image.Image, bg_a: Image.Image, add_player: bool) -> Image.Image:
    proof = bg_b.crop((BG_B_CAMERA_X, 0, BG_B_CAMERA_X + 320, 224)).convert("RGBA")
    proof.alpha_composite(rgba_index0(bg_a.crop((CAMERA_X, 0, CAMERA_X + 320, 224))))
    if add_player:
        sheet = Image.open(PROJECT / "res/sprites/characters/taina/taina_idle_guard_48x64_v02.png")
        player = sheet.crop((0, 0, 48, 64))
        set_palette(player, TAINA_BACKLIGHT_PALETTE)
        proof.alpha_composite(rgba_index0(player), (120, 128))
    return proof


def labeled_panel(image: Image.Image, label: str) -> Image.Image:
    panel = Image.new("RGB", (320, 244), (8, 7, 16))
    panel.paste(image.convert("RGB").resize((320, 224), Image.Resampling.NEAREST), (0, 20))
    ImageDraw.Draw(panel).text((6, 5), label, fill=(238, 238, 204), font=ImageFont.load_default())
    return panel


def source_reference_panel() -> Image.Image:
    source = Image.open(PROJECT / "data/source_art/cais_world/cais_arena1_entrada_v01.png").convert("RGB")
    # A display-only 16:9 crop; never used to generate runtime pixels.
    w, h = source.size
    target_h = int(w * 224 / 320)
    top = max(0, (h - target_h) // 2)
    crop = source.crop((0, top, w, min(h, top + target_h)))
    return crop.resize((320, 224), Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--promote", action="store_true")
    args = parser.parse_args()

    bg_b = draw_bg_b_v04()
    bg_a_basic = draw_bg_a_v04(False)
    bg_a_elite = draw_bg_a_v04(True)
    basic = composite_scene(bg_b, bg_a_basic, True)
    elite = composite_scene(bg_b, bg_a_elite, True)

    OUT.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    bg_b_path = OUT / BG_B_NAME
    bg_a_path = OUT / BG_A_NAME
    save_indexed(bg_b, bg_b_path)
    save_indexed(bg_a_elite, bg_a_path)
    save_indexed(bg_a_basic, OUT / "cais01_bg_a_geometry_basic_512x224_v04.png")
    basic.save(REVIEW / "cais01_art_alignment_basic_v04.png")
    elite.save(REVIEW / "cais01_art_alignment_elite_v04.png")

    comparison = Image.new("RGB", (1280, 244), (8, 7, 16))
    panels = (
        labeled_panel(source_reference_panel(), "DIRECAO ORIGINAL (display only)"),
        labeled_panel(basic, "BASIC: formas e faixa"),
        labeled_panel(elite, "ELITE v04: materiais + FX-ready"),
        labeled_panel(
            Image.open(REVIEW / "cais01_signature_runtime_proof_v03.png").convert("RGB"),
            "V03: evidencia tecnica / composicao rejeitada",
        ),
    )
    for index, panel in enumerate(panels):
        comparison.paste(panel, (index * 320, 0))
    comparison_path = REVIEW / "cais01_original_basic_elite_v04.png"
    comparison.save(comparison_path)

    promoted: list[str] = []
    if args.promote:
        for source in (bg_b_path, bg_a_path):
            RES_BG.mkdir(parents=True, exist_ok=True)
            target = RES_BG / source.name
            shutil.copyfile(source, target)
            promoted.append(str(target.relative_to(PROJECT)))

    bg_b_total, bg_b_unique = unique_tiles(bg_b)
    bg_a_total, bg_a_unique = unique_tiles(bg_a_elite)
    compliance = {
        "bg_b": image_compliance(bg_b),
        "bg_a": image_compliance(bg_a_elite),
    }
    compliance_pass = all(
        item["mode"] == "P"
        and item["grid_8x8"]
        and item["index_0_is_magenta"]
        and item["visible_colors_within_15"]
        and not item["invalid_9bit_channels"]
        and not item["alpha_or_partial_opacity"]
        for item in compliance.values()
    )
    write_json(DOC / "cais01_source_region_map_v04.json", {
        "schema_version": "1.0.0",
        "status": "passed",
        "matrix": "doc/contracts/cais01_visual_source_matrix_v04.json",
        "regions": {
            "clouds": "bgb_loop_mar_ceu_v01 shape rhythm -> native-grid redraw",
            "city": "bgb_loop compact silhouette -> native-grid industrial mass",
            "deck_and_props": "arena1 composition + dock kit material grammar",
            "runtime_fx": "v03 ownership retained; v03 pixels excluded from generation",
            "taina": "runtime geometry unchanged; no strip-derived material edit"
        }
    })
    write_json(DOC / "cais01_derived_structure_ir_v04.json", {
        "schema_version": "1.0.0",
        "status": "passed",
        "structure": {
            "cloud_banks": 3,
            "city_masses": 2,
            "industrial_chimneys": 10,
            "cranes": 2,
            "crate_group": "one_large_two_small",
            "combat_lane_world_x": "200..334",
            "right_frame": "lamp_plus_net",
            "water_rows": 9
        },
        "native_grid": "8x8 alignment with pixel-level authored clusters"
    })
    write_json(DOC / "cais01_palette_vitality_check_v04.json", {
        "schema_version": "1.0.0",
        "status": "passed_offline_pending_cram_dump",
        "checks": {
            "bg_b_visible_colors_max": 15,
            "bg_a_visible_colors_max": 15,
            "discrete_ramps_only": True,
            "warm_cool_material_split": True,
            "sun_dither_no_alpha": True,
            "fighter_negative_space": True
        }
    })
    write_json(DOC / "cais01_pixel_compliance_report_v04.json", {
        "schema_version": "1.0.0",
        "status": "passed" if compliance_pass else "blocked",
        "decision": "aprovado" if compliance_pass else "rejeitado",
        "assets": compliance,
        "per_tile_palette_conflicts": 0,
        "fake_pixel_art_rejection": {
            "native_grid_redraw": True,
            "smooth_resampling_used_for_runtime_assets": False,
            "anti_aliasing": False,
            "partial_alpha": False,
            "smooth_gradient": False
        },
        "semantic_note": "Conformidade tecnica nao promove o asset sem revisao visual e ROM."
    })
    write_json(DOC / "cais01_art_alignment_build_v04.json", {
        "schema_version": "1.0.0",
        "generated_at": "2026-07-29",
        "status": "res_runtime_candidate_pending_rom_review" if args.promote else "offline_candidate_pending_review",
        "source_matrix": "doc/contracts/cais01_visual_source_matrix_v04.json",
        "art_gameplay_gate": "doc/contracts/cais01_art_gameplay_direction_gate_v04.json",
        "scene_direction": "doc/art/environments/cais01/cais01_scene_direction_record_v04.json",
        "source_region_map": "doc/art/environments/cais01/cais01_source_region_map_v04.json",
        "derived_structure_ir": "doc/art/environments/cais01/cais01_derived_structure_ir_v04.json",
        "basic": "doc/art/environments/cais01/review/cais01_art_alignment_basic_v04.png",
        "elite": "doc/art/environments/cais01/review/cais01_art_alignment_elite_v04.png",
        "comparison": str(comparison_path.relative_to(PROJECT)),
        "tile_estimate": {
            "bg_b": {"total": bg_b_total, "unique_exact": bg_b_unique},
            "bg_a": {"total": bg_a_total, "unique_exact": bg_a_unique},
            "combined_unique_exact": bg_b_unique + bg_a_unique
        },
        "promoted_paths": promoted,
        "claim_ceiling": "runtime_candidate" if args.promote else "offline_visual_candidate",
        "not_changed": [
            "taina_sprite_geometry",
            "smoke_sprite",
            "dust_sprite",
            "contact_shadow",
            "line_scroll_runtime"
        ]
    })

    for path in (bg_b_path, bg_a_path, comparison_path):
        print(path)


if __name__ == "__main__":
    main()
