#!/usr/bin/env python3
"""Build the CAIS_01 visual-density pass v02 on the native Mega Drive grid.

The pass reconstructs the approved authorial dock direction as two VDP plane
domains.  It does not downscale the concept board and does not use the v01
runtime PNGs as generation sources.  The v01 proof is used only as the
before-image in the comparison board.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "rascunho/cais01_visual_pass_v02"
RES_BG = PROJECT / "res/backgrounds/cais01"
RES_FX = PROJECT / "res/sprites/fx"
REVIEW = PROJECT / "doc/art/environments/cais01/review"
REPORT = PROJECT / "doc/art/environments/cais01/cais01_visual_pass_build_v02.json"
SEMANTIC = PROJECT / "doc/art/environments/cais01/cais01_semantic_parse_v02.json"
SCROLL_CONTRACT = PROJECT / "doc/contracts/cais01_scroll_fx_contract_v02.json"
PALETTE_AUDIT = PROJECT / "doc/contracts/cais01_palette_slot_audit_v02.json"
BUDGET = PROJECT / "doc/art/environments/cais01/cais01_vdp_budget_estimate_v02.json"

BG_B_SIZE = (512, 224)
BG_A_SIZE = (320, 224)
MAGENTA = (255, 0, 255)

# Every channel is snapped to the Mega Drive's practical 3-bit steps.
BG_B_PALETTE = [
    MAGENTA,
    (0, 0, 34),       # 01 ink
    (34, 0, 68),      # 02 deepest violet
    (68, 34, 102),    # 03 upper dusk
    (102, 34, 102),   # 04 dusk violet
    (136, 68, 102),   # 05 rose haze
    (170, 68, 68),    # 06 hot horizon
    (204, 102, 68),   # 07 orange
    (238, 136, 68),   # 08 sun rim
    (238, 170, 102),  # 09 sun/cloud light
    (0, 34, 68),      # 10 sea deep
    (0, 68, 102),     # 11 sea shadow
    (34, 102, 102),   # 12 sea base
    (68, 136, 136),   # 13 sea light
    (170, 204, 170),  # 14 foam shadow
    (238, 238, 204),  # 15 foam/spark
]

BG_A_PALETTE = [
    MAGENTA,
    (0, 0, 34),       # 01 outline
    (34, 0, 34),      # 02 deepest purple
    (68, 34, 68),     # 03 cool wood shadow
    (102, 34, 34),    # 04 red wood shadow
    (102, 68, 34),    # 05 wood dark
    (136, 68, 34),    # 06 wood base
    (170, 102, 34),   # 07 wood warm
    (204, 136, 68),   # 08 wood highlight
    (238, 170, 102),  # 09 fresh cut/rope light
    (136, 102, 68),   # 10 rope/metal
    (0, 68, 68),      # 11 oxidized metal dark
    (34, 102, 102),   # 12 oxidized metal base
    (170, 204, 170),  # 13 foam/cool glint
    (238, 170, 68),   # 14 lamp pulse
    (238, 238, 204),  # 15 lamp core
]


def indexed_image(
    size: tuple[int, int],
    palette: list[tuple[int, int, int]],
    fill: int,
) -> Image.Image:
    image = Image.new("P", size, fill)
    flat = [channel for color in palette for channel in color]
    flat.extend([0] * (768 - len(flat)))
    image.putpalette(flat)
    image.info["transparency"] = 0
    return image


def dot_dither(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    color: int,
    period: int = 4,
    phase: int = 0,
) -> None:
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if ((x + (y * 2) + phase) % period) == 0:
                draw.point((x, y), fill=color)


def draw_cloud(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    dark: int,
    light: int,
) -> None:
    draw.ellipse((x + 7, y + 3, x + width // 2, y + 16), fill=dark)
    draw.ellipse((x + width // 3, y, x + width - 10, y + 17), fill=dark)
    draw.rectangle((x + 5, y + 10, x + width, y + 18), fill=dark)
    draw.line((x + 10, y + 17, x + width - 3, y + 17), fill=light, width=2)
    draw.line((x + width // 3, y + 14, x + width - 16, y + 14), fill=light)


def draw_crane(draw: ImageDraw.ImageDraw, x: int, horizon: int, scale: int = 1) -> None:
    ink = 2
    mast_h = 52 * scale
    draw.rectangle((x, horizon - mast_h, x + (4 * scale), horizon), fill=ink)
    draw.line(
        (x + 2 * scale, horizon - mast_h + 4, x + 45 * scale, horizon - mast_h + 15),
        fill=ink,
        width=3 * scale,
    )
    draw.line(
        (x + 43 * scale, horizon - mast_h + 15, x + 43 * scale, horizon - 4),
        fill=ink,
        width=2 * scale,
    )
    draw.line(
        (x + 8 * scale, horizon - mast_h + 8, x + 25 * scale, horizon - 2),
        fill=ink,
        width=2 * scale,
    )
    draw.line(
        (x + 25 * scale, horizon - 2, x + 43 * scale, horizon - mast_h + 15),
        fill=ink,
        width=2 * scale,
    )


def draw_bg_b() -> Image.Image:
    image = indexed_image(BG_B_SIZE, BG_B_PALETTE, 3)
    d = ImageDraw.Draw(image)
    width, height = image.size

    # Five authored ramps plus sparse dither.  These are discrete color bands,
    # never interpolated gradients.
    d.rectangle((0, 0, width - 1, 23), fill=3)
    d.rectangle((0, 24, width - 1, 47), fill=4)
    d.rectangle((0, 48, width - 1, 71), fill=5)
    d.rectangle((0, 72, width - 1, 91), fill=6)
    d.rectangle((0, 92, width - 1, 111), fill=7)
    for y, color, phase in ((23, 4, 0), (47, 5, 1), (71, 6, 2), (91, 7, 3)):
        dot_dither(d, (0, y, width - 1, y + 1), color, 6, phase)

    # Offset sun and cloud masses keep the center behind the fighter quieter.
    d.ellipse((44, 43, 105, 104), fill=8)
    d.ellipse((50, 49, 99, 99), fill=9)
    dot_dither(d, (52, 88, 98, 104), 8, 3)
    draw_cloud(d, 145, 26, 76, 4, 9)
    draw_cloud(d, 346, 50, 92, 5, 9)

    # Distant city is a compound silhouette rather than a single rectangle.
    horizon = 112
    d.rectangle((0, 101, width - 1, horizon - 1), fill=2)
    skyline = [
        (0, 91, 38), (43, 96, 72), (79, 84, 107), (112, 94, 148),
        (154, 88, 186), (194, 98, 228), (235, 90, 276), (283, 96, 318),
        (326, 82, 364), (370, 93, 412), (420, 86, 459), (466, 95, 511),
    ]
    for x0, y0, x1 in skyline:
        d.rectangle((x0, y0, x1, horizon - 1), fill=2)
    for x in (91, 173, 258, 340, 430):
        d.rectangle((x, 96, x + 2, 111), fill=1)
    draw_crane(d, 116, horizon)
    draw_crane(d, 382, horizon)

    # Tiny industrial lights are rare hierarchy accents.
    for x, y in ((20, 96), (66, 102), (167, 94), (208, 102), (327, 91), (451, 94)):
        d.rectangle((x, y, x + 1, y + 1), fill=9)

    # Layered sea.  Each 8px row is safe to scroll independently at runtime.
    d.rectangle((0, 112, width - 1, height - 1), fill=10)
    d.rectangle((0, 120, width - 1, 135), fill=11)
    d.rectangle((0, 136, width - 1, 159), fill=12)
    d.rectangle((0, 160, width - 1, 191), fill=11)
    d.rectangle((0, 192, width - 1, height - 1), fill=10)
    wave_rows = (119, 128, 141, 151, 166, 181, 197, 211)
    for band, y in enumerate(wave_rows):
        offset = (band * 17) % 48
        color = 13 if band < 6 else 12
        for x in range(-48 + offset, width, 48):
            d.line((x, y, x + 12, y - 1), fill=color)
            d.line((x + 13, y - 1, x + 22, y + 1), fill=color)
            d.line((x + 30, y + 3, x + 39, y + 2), fill=color)
    for y, spacing, phase in ((136, 64, 0), (160, 80, 21), (192, 96, 37)):
        for x in range(-spacing + phase, width, spacing):
            d.line((x, y, x + 9, y - 2), fill=14)
            d.line((x + 10, y - 2, x + 22, y), fill=15)
            d.line((x + 23, y, x + 30, y + 1), fill=14)

    # A distant work boat supplies a mid-distance landmark.
    d.polygon([(258, 98), (300, 98), (293, 108), (264, 108)], fill=1)
    d.rectangle((271, 90, 289, 98), fill=2)
    d.rectangle((278, 84, 281, 90), fill=1)
    d.point((287, 93), fill=9)
    return image


def wood_nicks(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, seed: int) -> None:
    for index in range(4):
        px = x + 5 + ((seed * 11 + index * 17) % max(6, w - 10))
        py = y + 4 + ((seed * 7 + index * 5) % 10)
        draw.line((px, py, min(px + 5 + (index & 1), x + w - 3), py), fill=5)
    knot_x = x + 8 + ((seed * 13) % max(4, w - 16))
    draw.ellipse((knot_x, y + 9, knot_x + 4, y + 12), outline=4)
    draw.point((knot_x + 2, y + 10), fill=2)


def draw_crate(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    draw.rectangle((x, y, x + w - 1, y + h - 1), fill=1)
    draw.rectangle((x + 2, y + 2, x + w - 3, y + h - 3), fill=5)
    draw.rectangle((x + 5, y + 5, x + w - 6, y + h - 6), fill=7)
    draw.line((x + 5, y + 5, x + w - 6, y + h - 6), fill=3, width=2)
    draw.line((x + w - 6, y + 5, x + 5, y + h - 6), fill=4, width=2)
    draw.line((x + 3, y + 3, x + w - 4, y + 3), fill=9)
    for px, py in ((x + 3, y + 3), (x + w - 4, y + 3), (x + 3, y + h - 4)):
        draw.point((px, py), fill=13)


def draw_bollard(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rectangle((x + 5, y + 2, x + 12, y + 27), fill=1)
    draw.rectangle((x + 7, y + 5, x + 10, y + 24), fill=3)
    draw.rectangle((x + 1, y, x + 16, y + 5), fill=1)
    draw.rectangle((x + 4, y + 1, x + 13, y + 2), fill=10)
    draw.arc((x - 5, y + 11, x + 22, y + 24), 15, 170, fill=9, width=2)
    draw.arc((x - 4, y + 14, x + 21, y + 25), 190, 350, fill=5, width=2)


def draw_rope_coil(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    for inset, color in ((0, 1), (2, 9), (4, 5), (6, 10)):
        draw.ellipse(
            (x + inset, y + inset // 2, x + 34 - inset, y + 17 - inset // 2),
            outline=color,
            width=2,
        )
    draw.line((x + 28, y + 14, x + 45, y + 20), fill=1, width=3)
    draw.line((x + 28, y + 13, x + 44, y + 19), fill=9)


def draw_lamp(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rectangle((x + 5, y + 8, x + 9, y + 86), fill=1)
    draw.rectangle((x + 6, y + 10, x + 7, y + 83), fill=10)
    draw.line((x + 7, y + 10, x + 25, y + 10), fill=1, width=3)
    draw.line((x + 24, y + 10, x + 24, y + 22), fill=1, width=2)
    draw.polygon(
        [(x + 16, y + 21), (x + 30, y + 21), (x + 28, y + 39), (x + 18, y + 39)],
        fill=1,
    )
    draw.rectangle((x + 19, y + 24, x + 27, y + 35), fill=14)
    draw.rectangle((x + 21, y + 26, x + 25, y + 33), fill=15)
    draw.rectangle((x + 1, y + 91, x + 14, y + 96), fill=2)


def draw_bg_a() -> Image.Image:
    image = indexed_image(BG_A_SIZE, BG_A_PALETTE, 0)
    d = ImageDraw.Draw(image)
    width, height = image.size

    # Pier fascia uses layered beams, bolts and algae rather than a flat stripe.
    d.rectangle((0, 128, width - 1, 151), fill=1)
    d.rectangle((0, 129, width - 1, 136), fill=8)
    d.rectangle((0, 137, width - 1, 144), fill=6)
    d.rectangle((0, 145, width - 1, 151), fill=3)
    for x in range(0, width, 16):
        d.rectangle((x + 1, 130, x + 14, 135), fill=7 if (x // 16) & 1 else 8)
        d.point((x + 3, 132), fill=13)
        d.line((x + 8, 145, x + 14, 145), fill=11)
    d.line((0, 128, width - 1, 128), fill=9)

    # Staggered 16px deck courses create perspective and tile reuse together.
    d.rectangle((0, 152, width - 1, height - 1), fill=6)
    for row, y in enumerate(range(152, height, 16)):
        base = 6 if (row & 1) else 7
        shadow = 4 if (row & 1) else 5
        d.rectangle((0, y, width - 1, min(y + 15, height - 1)), fill=base)
        d.line((0, y, width - 1, y), fill=9 if row == 0 else shadow)
        offset = 16 if row & 1 else 0
        for x in range(-offset, width, 48):
            d.line((x, y, x, min(y + 15, height - 1)), fill=3, width=2)
            wood_nicks(d, x, y, 48, row * 13 + x // 16)

    # Wet patches and lamp pool reserve palette slots 14/15 for runtime cycling.
    for x0, x1, y in ((238, 294, 166), (246, 306, 181), (258, 314, 197)):
        d.line((x0, y, x1, y), fill=14)
        for x in range(x0 + 5, x1, 13):
            d.point((x, y + 1 + ((x // 13) & 1)), fill=15)
    for y in range(157, 209, 8):
        half_width = max(4, (y - 153) // 3)
        center = 272
        for x in range(center - half_width, center + half_width + 1):
            if ((x * 3 + y) % 23) == 0:
                d.point((x, y), fill=14)

    # Ring-out foam is localized and brighter than decorative water.
    d.rectangle((278, 120, width - 1, 127), fill=11)
    for x in range(276, width, 12):
        d.line((x, 125, x + 5, 122), fill=13, width=2)
        d.line((x + 6, 122, x + 10, 124), fill=15)

    # Props frame a clean combat window from x=72..244.
    draw_crate(d, 0, 104, 42, 48)
    draw_crate(d, 35, 124, 34, 36)
    draw_crate(d, 282, 116, 38, 44)
    draw_bollard(d, 75, 120)
    draw_rope_coil(d, 96, 133)
    draw_lamp(d, 245, 35)

    # Net silhouette and broken rope produce authorial asymmetry at the edge.
    d.line((286, 72, 286, 119), fill=1, width=3)
    d.line((317, 65, 317, 119), fill=1, width=3)
    d.line((286, 76, 317, 68), fill=9, width=2)
    for y in range(80, 116, 8):
        d.line((288, y, 315, y - 6), fill=11)
    for x in range(291, 316, 8):
        d.line((x, 76, x - 2, 116), fill=10)
    d.line((305, 93, 313, 103), fill=1, width=2)
    return image


def draw_ground_shadow() -> Image.Image:
    source = Image.open(
        PROJECT / "res/sprites/characters/taina/taina_idle_guard_48x64_v02.png"
    )
    image = indexed_image((144, 16), [
        tuple(source.getpalette()[i:i + 3]) for i in range(0, 48, 3)
    ], 0)
    d = ImageDraw.Draw(image)
    for frame, (x0, center_x, center_y, rx, ry) in enumerate((
        (0, 24, 9, 16, 4),
        (48, 24, 9, 11, 3),
        (96, 24, 9, 7, 2),
    )):
        for y in range(center_y - ry, center_y + ry + 1):
            dy = y - center_y
            row_rx = max(1, rx - ((abs(dy) * rx) // (ry + 1)))
            for x in range(center_x - row_rx, center_x + row_rx + 1):
                # Transparent checker coverage reads as a soft contact shadow
                # without alpha blending or Shadow/Highlight operators.
                if ((x + y + frame) & 1) == 0:
                    d.point((x0 + x, y), fill=1)
                elif abs(x - center_x) < (row_rx // 2) and ((x + y) & 3) == 1:
                    d.point((x0 + x, y), fill=2)
    return image


def save_indexed(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, bits=4, optimize=False, transparency=0)


def rgba_with_index0_transparent(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgba.putalpha(image.point(lambda value: 0 if value == 0 else 255, mode="L"))
    return rgba


def unique_tiles(image: Image.Image) -> tuple[int, int]:
    hashes: set[str] = set()
    total = 0
    for y in range(0, image.height, 8):
        for x in range(0, image.width, 8):
            tile = image.crop((x, y, x + 8, y + 8))
            hashes.add(hashlib.sha256(tile.tobytes()).hexdigest())
            total += 1
    return total, len(hashes)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--promote", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bg_b = draw_bg_b()
    bg_a = draw_bg_a()
    shadow = draw_ground_shadow()
    bg_b_path = OUT / "cais01_bg_b_mar_ceu_512x224_v02.png"
    bg_a_path = OUT / "cais01_bg_a_pier_modular_320x224_v02.png"
    shadow_path = OUT / "taina_ground_shadow_48x16_3f_v02.png"
    save_indexed(bg_b, bg_b_path)
    save_indexed(bg_a, bg_a_path)
    save_indexed(shadow, shadow_path)

    proof = bg_b.crop((0, 0, 320, 224)).convert("RGBA")
    proof.alpha_composite(rgba_with_index0_transparent(bg_a))
    REVIEW.mkdir(parents=True, exist_ok=True)
    proof_path = REVIEW / "cais01_visual_pass_virtual_proof_v02.png"
    proof.save(proof_path)

    playfield = proof.copy()
    player_sheet = Image.open(
        PROJECT / "res/sprites/characters/taina/taina_idle_guard_48x64_v02.png"
    )
    player_frame = player_sheet.crop((0, 0, 48, 64)).convert("RGBA")
    player_frame.putalpha(
        player_sheet.crop((0, 0, 48, 64)).point(
            lambda value: 0 if value == 0 else 255,
            mode="L",
        )
    )
    playfield.alpha_composite(player_frame, (136, 128))
    playfield_path = REVIEW / "cais01_visual_pass_playfield_proof_v02.png"
    playfield.save(playfield_path)

    before = Image.open(
        REVIEW / "cais01_modular_slice_virtual_proof_v01.png"
    ).convert("RGB")
    comparison = Image.new("RGB", (640, 224), (0, 0, 0))
    comparison.paste(before.crop((0, 0, 320, 224)), (0, 0))
    comparison.paste(proof.convert("RGB"), (320, 0))
    comparison_path = REVIEW / "cais01_visual_pass_compare_v01_v02.png"
    comparison.save(comparison_path)

    bg_b_total, bg_b_unique = unique_tiles(bg_b)
    bg_a_total, bg_a_unique = unique_tiles(bg_a)
    shadow_total, shadow_unique = unique_tiles(shadow)
    promoted_paths: list[str] = []
    if args.promote:
        for source, root in (
            (bg_b_path, RES_BG),
            (bg_a_path, RES_BG),
            (shadow_path, RES_FX),
        ):
            root.mkdir(parents=True, exist_ok=True)
            target = root / source.name
            shutil.copyfile(source, target)
            promoted_paths.append(str(target.relative_to(PROJECT)))

    write_json(SEMANTIC, {
        "schema_version": "1.0.0",
        "report_id": "cais01_semantic_parse_v02",
        "status": "passed_for_native_grid_translation",
        "approved_source_direction": (
            "data/source_art/concept/authorial_style_validation_2026_07_04/"
            "dock_scene_kit_authorial_v01.png"
        ),
        "plane_roles": {
            "BG_B": [
                "dusk_ramps", "cloud_masses", "distant_industry",
                "crane_landmarks", "work_boat", "four_water_bands",
            ],
            "BG_A": [
                "pier_fascia", "walkable_deck", "modular_props",
                "ringout_foam", "lamp_and_wet_light_pool",
            ],
            "SPRITES": ["taina", "three_state_contact_shadow"],
        },
        "visual_hierarchy": [
            "taina_silhouette", "walkable_deck_and_ringout_edge",
            "lamp/props", "distant_harbor", "sky/sea_texture",
        ],
        "forbidden_shortcuts_used": [],
    })
    write_json(SCROLL_CONTRACT, {
        "schema_version": "1.0.0",
        "contract_id": "cais01_scroll_fx_v02",
        "status": "implemented_pending_emulator_evidence",
        "owner": "SCENE_demo",
        "mode": "HSCROLL_TILE",
        "h_int_owner": "none",
        "bands": [
            {"rows": "0..7", "role": "sky_clouds", "speed": "static"},
            {"rows": "8..13", "role": "skyline_horizon", "speed": "very_slow"},
            {"rows": "14..17", "role": "far_water", "speed": "slow_positive"},
            {"rows": "18..21", "role": "mid_water", "speed": "slow_negative"},
            {"rows": "22..27", "role": "near_water", "speed": "medium_positive"},
        ],
        "update_method": "28 s16 rows per plane through DMA_QUEUE before VBlank",
        "teardown": "restore HSCROLL_PLANE and zero both planes before scene change",
        "fallback": "static v02 planes with HSCROLL_PLANE",
    })
    write_json(PALETTE_AUDIT, {
        "schema_version": "1.0.0",
        "report_id": "cais01_palette_slot_audit_v02",
        "status": "implemented_pending_cram_dump",
        "domains": {
            "PAL0": "BG_B dusk/industry/sea; 15 visible colors",
            "PAL1": "TAINA plus contact shadow using existing dark indices",
            "PAL2": "BG_A wood/metal/foam/lamp; slots 14-15 cycle",
            "PAL3": "debug text only",
        },
        "runtime_cycle": {
            "indices": [46, 47],
            "meaning": "PAL2 local lamp core and authored wet reflections",
            "cadence_vblanks": 8,
            "states": 4,
        },
        "shadow_highlight_mode": "disabled",
        "fallback": "keep source PAL2 slots 14-15 static",
    })
    write_json(BUDGET, {
        "schema_version": "1.0.0",
        "report_id": "cais01_vdp_budget_estimate_v02",
        "status": "offline_estimate_pending_rescomp_and_emulator_metrics",
        "tiles": {
            "bg_b_total": bg_b_total,
            "bg_b_unique_exact": bg_b_unique,
            "bg_a_total": bg_a_total,
            "bg_a_unique_exact": bg_a_unique,
            "shadow_total": shadow_total,
            "shadow_unique_exact": shadow_unique,
        },
        "unique_bytes_before_rescomp": (
            bg_b_unique + bg_a_unique + shadow_unique
        ) * 32,
        "per_frame_dma": {
            "hscroll_tables_bytes": 112,
            "palette_cycle_bytes_every_8_vblanks": 4,
            "sprite_shadow": "normal SGDK sprite frame update",
        },
        "scanline_delta": "one additional shadow metasprite below fighter",
    })
    write_json(REPORT, {
        "schema_version": "1.0.0",
        "report_id": "cais01_visual_pass_build_v02",
        "generated_at": "2026-07-29",
        "status": (
            "res_runtime_candidate_pending_rom_visual_review"
            if args.promote else "offline_candidate_pending_review"
        ),
        "route": "art_translation_to_vdp_and_multi_plane_composition",
        "source_direction": (
            "data/source_art/concept/authorial_style_validation_2026_07_04/"
            "dock_scene_kit_authorial_v01.png"
        ),
        "basic_control": "cais01_modular_slice_virtual_proof_v01.png",
        "elite_candidate": str(proof_path.relative_to(PROJECT)),
        "playfield_proof": str(playfield_path.relative_to(PROJECT)),
        "comparison": str(comparison_path.relative_to(PROJECT)),
        "promoted_paths": promoted_paths,
        "delivery_findings": [
            "background and FX are runtime candidates, not final art",
            "TAINA sprite-detail reseed remains blocked on pixel model-sheet gate",
            "ResComp measurements and BlastEm evidence are required",
        ],
    })
    print(bg_b_path)
    print(bg_a_path)
    print(shadow_path)
    print(proof_path)
    print(playfield_path)
    print(comparison_path)


if __name__ == "__main__":
    main()
