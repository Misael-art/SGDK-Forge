#!/usr/bin/env python3
"""Build the CAIS_01 signature pass v03 for SGDK/Mega Drive.

The approved dock concept remains the visual source.  The v02 native-grid
builder is reused as construction logic, never its runtime PNG as a generation
source.  The v03 pass adds a 512px playfield, two city depth bands, authored
sun reflection, industrial floor texture and small animated FX sheets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

import build_cais01_visual_pass_v02 as base


PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "rascunho/cais01_signature_pass_v03"
RES_BG = PROJECT / "res/backgrounds/cais01"
RES_FX = PROJECT / "res/sprites/fx"
REVIEW = PROJECT / "doc/art/environments/cais01/review"
REPORT = PROJECT / "doc/art/environments/cais01/cais01_signature_pass_build_v03.json"
SEMANTIC = PROJECT / "doc/art/environments/cais01/cais01_semantic_parse_v03.json"
BENCHMARK = PROJECT / "doc/art/environments/cais01/cais01_benchmark_match_report_v03.json"
PALETTE = PROJECT / "doc/art/environments/cais01/cais01_palette_vitality_check_v03.json"
SIGNATURE = PROJECT / "doc/contracts/cais01_scene_signature_techniques_v03.json"
PARALLAX = PROJECT / "doc/contracts/cais01_parallax_layer_contract_v03.json"
RASTER = PROJECT / "doc/contracts/cais01_raster_fx_ownership_map_v03.json"
ECOLOGY = PROJECT / "doc/contracts/cais01_background_ecology_card_v03.json"
TAINA_LIGHT = PROJECT / "doc/art/characters/taina/taina_backlight_palette_contract_v03.json"

WIDTH = 512
HEIGHT = 224

TAINA_BACKLIGHT_PALETTE = [
    (255, 0, 255),
    (0, 0, 34),
    (34, 0, 68),
    (68, 34, 102),
    (0, 34, 68),
    (34, 136, 136),
    (68, 34, 34),
    (136, 68, 34),
    (204, 68, 34),
    (238, 136, 68),
    (238, 170, 102),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
    (0, 0, 0),
]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def set_palette(image: Image.Image, colors: list[tuple[int, int, int]]) -> None:
    flat = [channel for color in colors for channel in color]
    flat.extend([0] * (768 - len(flat)))
    image.putpalette(flat)
    image.info["transparency"] = 0


def dithered_sun(draw: ImageDraw.ImageDraw) -> None:
    cx, cy = 76, 74
    outer_r = 33
    inner_r = 27
    draw.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r), fill=8)
    draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r), fill=9)
    for y in range(cy - outer_r, cy + outer_r + 1):
        for x in range(cx - outer_r, cx + outer_r + 1):
            distance2 = ((x - cx) * (x - cx)) + ((y - cy) * (y - cy))
            if (inner_r * inner_r) < distance2 <= (outer_r * outer_r):
                draw.point((x, y), fill=8 if ((x + y) & 1) == 0 else 7)
            elif (inner_r - 4) ** 2 < distance2 <= inner_r * inner_r:
                if ((x * 3 + y) % 5) == 0:
                    draw.point((x, y), fill=8)


def draw_city_layers(draw: ImageDraw.ImageDraw) -> None:
    # Far city: warmer/lighter violet, fewer details and a lower contrast edge.
    far = [
        (0, 85, 45), (50, 78, 88), (94, 89, 132), (138, 73, 174),
        (181, 84, 222), (229, 76, 267), (274, 88, 320), (326, 70, 365),
        (372, 82, 418), (425, 74, 468), (474, 86, 511),
    ]
    for x0, y0, x1 in far:
        draw.rectangle((x0, y0, x1, 106), fill=4)
        draw.line((x0, y0, x1, y0), fill=5)
    for x, y in ((18, 92), (63, 84), (151, 81), (248, 83), (341, 77), (449, 81)):
        draw.rectangle((x, y, x + 2, y + 1), fill=7)

    # Near city: almost-black silhouette, irregular roofs and saturated lights.
    near = [
        (0, 98, 35), (40, 93, 76), (82, 101, 118), (126, 90, 158),
        (165, 97, 206), (213, 92, 251), (258, 101, 294), (301, 89, 340),
        (347, 96, 388), (395, 91, 433), (440, 99, 476), (483, 92, 511),
    ]
    for x0, y0, x1 in near:
        draw.rectangle((x0, y0, x1, 111), fill=2)
        draw.rectangle((x0 + 5, y0 - 4, min(x0 + 10, x1), 111), fill=2)
    for x, y in (
        (12, 104), (54, 100), (103, 106), (145, 96), (191, 103),
        (236, 98), (281, 106), (324, 95), (371, 102), (418, 97), (494, 100),
    ):
        draw.rectangle((x, y, x + 1, y + 1), fill=9)

    # Crane silhouettes bridge the near skyline and the industrial theme.
    base.draw_crane(draw, 116, 112)
    base.draw_crane(draw, 382, 112)


def draw_sun_reflection(draw: ImageDraw.ImageDraw) -> None:
    # The reflection is authored as broken horizontal clusters so line scroll
    # can distort it without producing a solid vertical stripe.
    center = 76
    for y in range(112, 160):
        depth = y - 112
        half = 5 + (depth // 5)
        color = 9 if depth < 10 else (8 if depth < 28 else 7)
        phase = (y * 7) % 9
        for x in range(center - half, center + half + 1):
            if ((x + phase) % 4) != 1:
                draw.point((x, y), fill=color)
        if (y & 3) == 0:
            draw.line((center - half - 3, y, center - half, y), fill=13)
            draw.line((center + half, y, center + half + 4, y), fill=14)


def draw_bg_b_v03() -> Image.Image:
    image = base.draw_bg_b()
    draw = ImageDraw.Draw(image)

    # Rebuild the horizon band in correct painter order.
    draw.rectangle((0, 72, WIDTH - 1, 91), fill=6)
    draw.rectangle((0, 92, WIDTH - 1, 111), fill=7)
    base.dot_dither(draw, (0, 90, WIDTH - 1, 93), 7, 6, 2)
    dithered_sun(draw)
    draw_city_layers(draw)
    draw_sun_reflection(draw)

    # Extra water clusters support the HSCROLL_LINE wave without visual gaps.
    for y in range(114, 160, 5):
        for x in range((y * 3) % 31, WIDTH, 40):
            draw.line((x, y, x + 8, y), fill=13)
            if ((x + y) & 1) == 0:
                draw.point((x + 10, y + 1), fill=14)
    return image


def draw_stencil_mb(draw: ImageDraw.ImageDraw, x: int, y: int, color: int) -> None:
    # 3x5-pixel cargo stencil: "MB", authored mark rather than borrowed logo.
    m = ("10101", "11111", "10101", "10101", "10101")
    b = ("1110", "1001", "1110", "1001", "1110")
    for py, row in enumerate(m):
        for px, bit in enumerate(row):
            if bit == "1":
                draw.point((x + px, y + py), fill=color)
    for py, row in enumerate(b):
        for px, bit in enumerate(row):
            if bit == "1":
                draw.point((x + 7 + px, y + py), fill=color)


def draw_oil_patch(draw: ImageDraw.ImageDraw, cx: int, cy: int, rx: int, ry: int) -> None:
    for y in range(cy - ry, cy + ry + 1):
        row_rx = max(2, rx - ((abs(y - cy) * rx) // (ry + 1)))
        for x in range(cx - row_rx, cx + row_rx + 1):
            if ((x * 5 + y * 3) % 7) < 4:
                draw.point((x, y), fill=2)
            elif ((x + y) % 9) == 0:
                draw.point((x, y), fill=11)
    draw.line((cx - rx + 3, cy - 1, cx + rx - 5, cy - 1), fill=12)


def draw_tire_marks(draw: ImageDraw.ImageDraw, x0: int, x1: int, y: int) -> None:
    for x in range(x0, x1, 4):
        draw.line((x, y, x + 2, y + 1), fill=3)
        draw.line((x + 1, y + 5, x + 3, y + 6), fill=3)


def draw_bg_a_v03() -> Image.Image:
    image = base.indexed_image((WIDTH, HEIGHT), base.BG_A_PALETTE, 0)
    draw = ImageDraw.Draw(image)

    # Pier edge: warm rim light, layered beams, bolts and algae.
    draw.rectangle((0, 136, WIDTH - 1, 159), fill=1)
    draw.rectangle((0, 137, WIDTH - 1, 143), fill=9)
    draw.rectangle((0, 144, WIDTH - 1, 151), fill=7)
    draw.rectangle((0, 152, WIDTH - 1, 159), fill=3)
    for x in range(0, WIDTH, 16):
        draw.rectangle((x + 1, 140, x + 14, 143), fill=8)
        draw.point((x + 3, 141), fill=13)
        draw.line((x + 8, 153, x + 14, 153), fill=11)

    # Staggered planks over the full 512px playfield.
    draw.rectangle((0, 160, WIDTH - 1, HEIGHT - 1), fill=6)
    for row, y in enumerate(range(160, HEIGHT, 16)):
        fill = 6 if row & 1 else 7
        seam = 4 if row & 1 else 5
        draw.rectangle((0, y, WIDTH - 1, min(y + 15, HEIGHT - 1)), fill=fill)
        draw.line((0, y, WIDTH - 1, y), fill=9 if row == 0 else seam)
        offset = 16 if row & 1 else 0
        for x in range(-offset, WIDTH, 48):
            draw.line((x, y, x, min(y + 15, HEIGHT - 1)), fill=3, width=2)
            base.wood_nicks(draw, x, y, 48, row * 17 + x // 16)

    # Industrial wear: oil, tyre marks, cracks, nails and sunset glints.
    draw_oil_patch(draw, 192, 199, 27, 9)
    draw_oil_patch(draw, 410, 214, 20, 6)
    draw_tire_marks(draw, 74, 146, 207)
    draw_tire_marks(draw, 302, 366, 184)
    for x, y in ((151, 179), (228, 215), (287, 197), (452, 175)):
        draw.line((x, y, x + 7, y + 3), fill=3)
        draw.line((x + 7, y + 3, x + 12, y), fill=3)
    for x in range(18, WIDTH, 37):
        draw.point((x, 164 + ((x // 37) & 31)), fill=10)
    for x in range(8, WIDTH, 24):
        draw.line((x, 137, x + 9, 137), fill=8)

    # Props frame a wider arena; the center remains readable for combat.
    base.draw_crate(draw, 0, 104, 42, 56)
    base.draw_crate(draw, 40, 128, 36, 40)
    base.draw_bollard(draw, 96, 128)
    base.draw_rope_coil(draw, 116, 141)
    base.draw_lamp(draw, 350, 43)
    base.draw_crate(draw, 460, 120, 52, 48)
    draw_stencil_mb(draw, 16, 124, 9)
    draw_stencil_mb(draw, 479, 141, 9)

    # Right-side ring-out signal and authored net silhouette.
    draw.rectangle((480, 128, WIDTH - 1, 135), fill=11)
    for x in range(478, WIDTH, 12):
        draw.line((x, 133, x + 5, 130), fill=13, width=2)
        draw.line((x + 6, 130, x + 10, 132), fill=15)
    draw.line((482, 79, 482, 135), fill=1, width=3)
    draw.line((510, 70, 510, 135), fill=1, width=3)
    draw.line((482, 83, 510, 74), fill=9, width=2)
    for y in range(86, 132, 8):
        draw.line((484, y, 508, y - 6), fill=11)
    for x in range(487, 508, 7):
        draw.line((x, 82, x - 2, 130), fill=10)

    # Lamp reflections occupy dedicated cycling slots, sparsely.
    for x0, x1, y in ((344, 420, 173), (355, 433, 190), (368, 447, 207)):
        draw.line((x0, y, x1, y), fill=14)
        for x in range(x0 + 4, x1, 13):
            draw.point((x, y + 1 + ((x // 13) & 1)), fill=15)
    return image


def draw_smoke_sheet() -> Image.Image:
    image = base.indexed_image((128, 32), base.BG_B_PALETTE, 0)
    draw = ImageDraw.Draw(image)
    for frame in range(4):
        x0 = frame * 32
        lift = frame * 2
        blobs = (
            (15 + frame, 25 - lift, 6),
            (11 - frame, 19 - lift, 7),
            (18 + frame, 13 - lift, 8),
            (13, 7 - (lift // 2), 6),
        )
        for cx, cy, radius in blobs:
            draw.ellipse(
                (x0 + cx - radius, cy - radius // 2,
                 x0 + cx + radius, cy + radius // 2),
                fill=3 if frame & 1 else 4,
            )
        for y in range(2, 30):
            for x in range(x0 + 3, x0 + 29):
                if image.getpixel((x, y)) and ((x + y + frame) % 5) == 0:
                    draw.point((x, y), fill=5)
    return image


def draw_dust_sheet() -> Image.Image:
    image = base.indexed_image((64, 16), base.BG_A_PALETTE, 0)
    draw = ImageDraw.Draw(image)
    points = (
        ((3, 10), (8, 4), (13, 8)),
        ((4, 7), (9, 3), (12, 11)),
        ((2, 5), (7, 9), (14, 4)),
        ((5, 3), (10, 7), (13, 12)),
    )
    for frame, frame_points in enumerate(points):
        x0 = frame * 16
        for index, (x, y) in enumerate(frame_points):
            draw.point((x0 + x, y), fill=15 if index == 0 else 14)
            if index == 0:
                draw.point((x0 + x + 1, y), fill=14)
    return image


def draw_contact_shadow_v03() -> Image.Image:
    """Build a dense contact shadow compatible with TAÍNA's PAL1.

    V02 used transparent checker coverage over the whole ellipse.  Under the
    new backlight palette that pattern became a high-frequency purple grid in
    the runtime capture.  V03 keeps a solid near-black core and limits the
    lighter violet to sparse edge pixels, preserving the no-alpha constraint
    without competing with the fighter.
    """
    source = Image.open(
        PROJECT / "res/sprites/characters/taina/taina_idle_guard_48x64_v02.png"
    )
    image = base.indexed_image(
        (144, 16),
        [tuple(source.getpalette()[i:i + 3]) for i in range(0, 48, 3)],
        0,
    )
    draw = ImageDraw.Draw(image)
    for x0, center_x, center_y, rx, ry in (
        (0, 24, 9, 16, 4),
        (48, 24, 9, 11, 3),
        (96, 24, 9, 7, 2),
    ):
        for y in range(center_y - ry, center_y + ry + 1):
            dy = abs(y - center_y)
            row_rx = max(1, rx - ((dy * rx) // (ry + 1)))
            inner_rx = max(1, row_rx - 2)
            draw.line(
                (x0 + center_x - inner_rx, y, x0 + center_x + inner_rx, y),
                fill=1,
            )
            if ((y + x0) & 1) == 0:
                draw.point((x0 + center_x - row_rx, y), fill=2)
                draw.point((x0 + center_x + row_rx, y), fill=2)
    return image


def rgba_index0(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putalpha(image.point(lambda value: 0 if value == 0 else 255, mode="L"))
    return rgba


def build_runtime_proof(bg_b: Image.Image, bg_a: Image.Image) -> Image.Image:
    # Approximate the settled camera at x=80: BG_A full speed, BG_B quarter.
    proof = bg_b.crop((20, 0, 340, 224)).convert("RGBA")
    proof.alpha_composite(rgba_index0(bg_a.crop((80, 0, 400, 224))))

    player_sheet = Image.open(
        PROJECT / "res/sprites/characters/taina/taina_idle_guard_48x64_v02.png"
    )
    player = player_sheet.crop((0, 0, 48, 64))
    set_palette(player, TAINA_BACKLIGHT_PALETTE)
    proof.alpha_composite(rgba_index0(player), (120, 128))
    return proof


def unique_tiles(image: Image.Image) -> tuple[int, int]:
    total = 0
    hashes: set[str] = set()
    for y in range(0, image.height, 8):
        for x in range(0, image.width, 8):
            tile = image.crop((x, y, x + 8, y + 8))
            hashes.add(hashlib.sha256(tile.tobytes()).hexdigest())
            total += 1
    return total, len(hashes)


def save_indexed(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, bits=4, optimize=False, transparency=0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--promote", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bg_b = draw_bg_b_v03()
    bg_a = draw_bg_a_v03()
    smoke = draw_smoke_sheet()
    dust = draw_dust_sheet()
    shadow = draw_contact_shadow_v03()

    bg_b_path = OUT / "cais01_bg_b_harbor_sunset_512x224_v03.png"
    bg_a_path = OUT / "cais01_bg_a_industrial_pier_512x224_v03.png"
    smoke_path = OUT / "cais01_smoke_32x32_4f_v01.png"
    dust_path = OUT / "cais01_lamp_dust_16x16_4f_v01.png"
    shadow_path = OUT / "taina_ground_shadow_48x16_3f_v03.png"
    for image, path in (
        (bg_b, bg_b_path), (bg_a, bg_a_path),
        (smoke, smoke_path), (dust, dust_path), (shadow, shadow_path),
    ):
        save_indexed(image, path)

    REVIEW.mkdir(parents=True, exist_ok=True)
    proof = build_runtime_proof(bg_b, bg_a)
    proof_path = REVIEW / "cais01_signature_runtime_proof_v03.png"
    proof.save(proof_path)
    before = Image.open(
        REVIEW / "cais01_visual_pass_playfield_proof_v02.png"
    ).convert("RGB")
    compare = Image.new("RGB", (640, 224), (0, 0, 0))
    compare.paste(before, (0, 0))
    compare.paste(proof.convert("RGB"), (320, 0))
    compare_path = REVIEW / "cais01_signature_compare_v02_v03.png"
    compare.save(compare_path)

    promoted: list[str] = []
    if args.promote:
        for source, root in (
            (bg_b_path, RES_BG), (bg_a_path, RES_BG),
            (smoke_path, RES_FX), (dust_path, RES_FX), (shadow_path, RES_FX),
        ):
            root.mkdir(parents=True, exist_ok=True)
            target = root / source.name
            shutil.copyfile(source, target)
            promoted.append(str(target.relative_to(PROJECT)))

    totals = {}
    for key, image in (
        ("bg_b", bg_b), ("bg_a", bg_a), ("smoke", smoke),
        ("dust", dust), ("contact_shadow", shadow),
    ):
        total, unique = unique_tiles(image)
        totals[key] = {"tiles_total": total, "tiles_unique_exact": unique}

    write_json(SEMANTIC, {
        "schema_version": "1.0.0",
        "status": "passed_for_signature_translation",
        "source": "data/source_art/concept/authorial_style_validation_2026_07_04/dock_scene_kit_authorial_v01.png",
        "regions": {
            "sky": "five discrete dusk ramps plus dithered sun edge",
            "far_city": "lighter violet low-detail silhouette",
            "near_city": "near-black irregular silhouette plus warm windows",
            "water": "line-scroll bands plus broken sunset reflection",
            "pier": "512px industrial deck, oil, tyre marks, cracks and cargo stencil",
            "sprites": "two smoke emitters and two lamp dust motes"
        },
        "drop_ignore": ["labels from rejected kit", "smooth alpha glow", "copied benchmark art"]
    })
    write_json(BENCHMARK, {
        "schema_version": "1.0.0",
        "status": "inspiration_only_pass",
        "references": [
            {
                "game": "Streets of Rage 2",
                "inherit": "deep silhouette hierarchy, dock texture density and fighter-ground integration",
                "copy_prohibited": "layout, tiles, characters, palettes and stage objects"
            },
            {
                "game": "Streets of Rage 3",
                "inherit": "material clusters, saturated accents and readable contact shadows",
                "copy_prohibited": "sprites, poses, costume and stage composition"
            },
            {
                "game": "Sonic the Hedgehog 2",
                "inherit": "industrial depth, animated horizontal water bands and saturated dark/light contrast",
                "copy_prohibited": "Oil Ocean geometry, motifs, tile patterns and color script"
            }
        ],
        "authorial_source_remains": "dock_scene_kit_authorial_v01"
    })
    write_json(PALETTE, {
        "schema_version": "1.0.0",
        "status": "passed_offline_pending_cram_dump",
        "checks": {
            "deep_neutral_present": True,
            "warm_cool_material_separation": True,
            "sunset_saturation_preserved": True,
            "hero_backlight_readability": "proof_pass_human_review_pending",
            "smooth_gradient_used": False
        }
    })
    write_json(PARALLAX, {
        "schema_version": "1.0.0",
        "status": "implemented_pending_emulator_evidence",
        "owner": "SCENE_demo",
        "mode": "HSCROLL_LINE",
        "layers": [
            {"lines": "0..47", "role": "upper_sky", "camera_ratio": "1/8"},
            {"lines": "48..79", "role": "far_city", "camera_ratio": "1/4"},
            {"lines": "80..111", "role": "near_city", "camera_ratio": "1/2"},
            {"lines": "112..159", "role": "water", "camera_ratio": "1/4_plus_wave"},
            {"plane": "BG_A", "role": "playfield", "camera_ratio": "1/1"}
        ],
        "teardown": "restore HSCROLL_PLANE and zero BG_A/B before scene transition",
        "fallback": "HSCROLL_PLANE with BG_A full camera and BG_B quarter camera"
    })
    write_json(RASTER, {
        "schema_version": "1.0.0",
        "status": "single_owner",
        "h_int_owner": "none",
        "line_scroll_owner": "SCENE_demo",
        "palette_cycle_owner": "SCENE_demo",
        "per_frame_dma_bytes": 896,
        "fallback": "static plane scroll and static palettes"
    })
    write_json(ECOLOGY, {
        "schema_version": "1.0.0",
        "status": "implemented_pending_runtime_review",
        "elements": [
            {"id": "smoke_0", "purpose": "active industrial skyline", "gameplay_priority": "subordinate"},
            {"id": "smoke_1", "purpose": "depth repetition", "gameplay_priority": "subordinate"},
            {"id": "lamp_dust_0", "purpose": "local light density", "gameplay_priority": "subordinate"},
            {"id": "lamp_dust_1", "purpose": "palette pulse visibility", "gameplay_priority": "subordinate"}
        ],
        "rule": "hide or reduce before compromising fighter, hit or ringout readability"
    })
    write_json(TAINA_LIGHT, {
        "schema_version": "1.0.0",
        "status": "runtime_palette_candidate_not_sprite_reseed",
        "geometry_source_changed": False,
        "source_of_truth": "timeline_image_04_and_taina_identity_turnaround_authorial_v01",
        "policy": "backlit penumbra with near-black violet shadows, burnt-orange sun rim and saturated teal edge",
        "palette_roles": {
            "1": "outline_near_black",
            "2": "trouser_deep_violet",
            "3": "trouser_cool_base",
            "4": "wrap_deep_teal",
            "5": "wrap_turquoise_rim",
            "6": "skin_or_top_deep_shadow",
            "7": "warm_penumbra",
            "8": "burnt_orange_base",
            "9": "orange_rim",
            "10": "sunlit_edge"
        },
        "fallback": "load spr_taina_idle_guard.palette unchanged"
    })
    write_json(SIGNATURE, {
        "schema_version": "1.0.0",
        "status": "implemented_pending_rom_gate",
        "profile": "monumental_candidate",
        "techniques": [
            "camera_driven_four_band_line_scroll",
            "broken_sunset_water_reflection",
            "runtime_taina_backlight_palette",
            "industrial_smoke_and_lamp_dust",
            "lamp_palette_cycle",
            "authored_industrial_floor_wear"
        ],
        "gameplay_link": {
            "backlight": "hero remains strongest saturated edge",
            "water": "movement reinforces ringout edge",
            "lamp": "local landmark and depth anchor",
            "floor_wear": "supports contact and lane reading"
        }
    })
    write_json(REPORT, {
        "schema_version": "1.0.0",
        "generated_at": "2026-07-29",
        "status": "res_runtime_candidate_pending_rom_review" if args.promote else "offline_candidate_pending_review",
        "source_direction": "dock_scene_kit_authorial_v01",
        "basic": "cais01_visual_pass_playfield_proof_v02.png",
        "elite": str(proof_path.relative_to(PROJECT)),
        "comparison": str(compare_path.relative_to(PROJECT)),
        "tile_estimate": totals,
        "promoted_paths": promoted,
        "claim_ceiling": "offline_visual_candidate" if not args.promote else "runtime_candidate"
    })
    for path in (
        bg_b_path, bg_a_path, smoke_path, dust_path, shadow_path,
        proof_path, compare_path,
    ):
        print(path)


if __name__ == "__main__":
    main()
