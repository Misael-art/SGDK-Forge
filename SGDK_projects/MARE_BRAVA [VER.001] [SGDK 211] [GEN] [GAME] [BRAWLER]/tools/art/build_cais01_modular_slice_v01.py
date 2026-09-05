#!/usr/bin/env python3
"""Build the first native-grid modular CAIS_01 scene slice.

This is not a downscaled panorama.  It reconstructs a 320x224 locked-room
slice from repeatable 8x8/16x16 modules informed by the approved dock scene
kit: sky/sea on BG_B and pier structure/props on BG_A.  Outputs remain
``runtime_candidate`` until the ROM and VDP budget gates are complete.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "rascunho/cais01_modular_slice_v01"
RES = PROJECT / "res/backgrounds/cais01"
REVIEW = PROJECT / "doc/art/environments/cais01/review"
REPORT = PROJECT / "doc/art/environments/cais01/cais01_modular_slice_build_v01.json"
WIDTH = 320
HEIGHT = 224

MAGENTA = (255, 0, 255)

BG_B_PALETTE = [
    MAGENTA,
    (0, 0, 34),
    (34, 34, 68),
    (68, 34, 102),
    (102, 68, 102),
    (136, 68, 102),
    (170, 102, 102),
    (204, 102, 68),
    (238, 136, 68),
    (238, 170, 102),
    (34, 68, 102),
    (34, 102, 102),
    (68, 136, 136),
    (102, 170, 170),
    (170, 204, 170),
    (238, 238, 204),
]

BG_A_PALETTE = [
    MAGENTA,
    (0, 0, 34),
    (34, 34, 68),
    (68, 34, 68),
    (102, 34, 34),
    (102, 68, 34),
    (136, 68, 34),
    (170, 102, 34),
    (204, 102, 34),
    (238, 136, 68),
    (238, 170, 102),
    (34, 68, 68),
    (34, 102, 102),
    (68, 136, 136),
    (170, 204, 170),
    (238, 238, 204),
]


def indexed_image(palette: list[tuple[int, int, int]], fill: int) -> Image.Image:
    image = Image.new("P", (WIDTH, HEIGHT), fill)
    flat = [channel for color in palette for channel in color]
    flat.extend([0] * (768 - len(flat)))
    image.putpalette(flat)
    image.info["transparency"] = 0
    return image


def draw_bg_b() -> Image.Image:
    image = indexed_image(BG_B_PALETTE, 2)
    d = ImageDraw.Draw(image)

    # Discrete dusk ramps; tile-row boundaries make the bands reusable.
    d.rectangle((0, 0, WIDTH - 1, 31), fill=3)
    d.rectangle((0, 32, WIDTH - 1, 63), fill=4)
    d.rectangle((0, 64, WIDTH - 1, 87), fill=6)
    d.rectangle((0, 88, WIDTH - 1, 103), fill=8)

    # Ordered 2x2 dither at the two transitions, never a soft gradient.
    for y, light, dark in ((28, 4, 3), (60, 6, 4), (84, 8, 6)):
        for x in range(0, WIDTH, 2):
            d.point((x + ((y // 4) & 1), y), fill=light)
            d.point((x + (1 - ((y // 4) & 1)), y + 1), fill=dark)

    # Sun and distant industrial silhouette.
    d.ellipse((38, 48, 94, 104), fill=9)
    d.rectangle((0, 92, WIDTH - 1, 111), fill=5)
    d.rectangle((0, 80, 30, 111), fill=4)
    d.rectangle((24, 72, 48, 111), fill=4)
    d.rectangle((250, 84, 319, 111), fill=4)
    d.line((76, 94, 76, 35), fill=3, width=4)
    d.line((76, 37, 118, 56), fill=3, width=3)
    d.line((118, 56, 118, 104), fill=3, width=3)
    d.line((82, 44, 105, 21), fill=3, width=2)
    d.line((105, 21, 121, 56), fill=3, width=2)

    # Sea bands are authored as repeated horizontal 8px modules.
    d.rectangle((0, 104, WIDTH - 1, HEIGHT - 1), fill=10)
    d.rectangle((0, 112, WIDTH - 1, 127), fill=11)
    d.rectangle((0, 128, WIDTH - 1, 151), fill=12)
    d.rectangle((0, 152, WIDTH - 1, HEIGHT - 1), fill=11)
    for band, y in enumerate((112, 124, 138, 150, 166, 182, 198)):
        offset = (band * 11) % 32
        color = 13 if band < 4 else 10
        for x in range(-32 + offset, WIDTH, 32):
            d.line((x, y, x + 12, y - 1), fill=color, width=1)
            d.line((x + 16, y + 2, x + 24, y + 2), fill=color, width=1)
    for x in range(-16, WIDTH, 48):
        d.line((x, 128, x + 9, 126), fill=15, width=1)
        d.line((x + 10, 126, x + 18, 128), fill=14, width=1)
    return image


def draw_crate(d: ImageDraw.ImageDraw, x: int, y: int, w: int = 32, h: int = 32) -> None:
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=1)
    d.rectangle((x + 2, y + 2, x + w - 3, y + h - 3), fill=6)
    d.rectangle((x + 5, y + 5, x + w - 6, y + h - 6), fill=7)
    d.line((x + 5, y + 5, x + w - 6, y + h - 6), fill=3, width=2)
    d.line((x + w - 6, y + 5, x + 5, y + h - 6), fill=4, width=2)
    d.line((x + 3, y + 3, x + w - 4, y + 3), fill=10, width=1)


def draw_bollard(d: ImageDraw.ImageDraw, x: int, y: int) -> None:
    d.rectangle((x + 4, y, x + 11, y + 24), fill=1)
    d.rectangle((x + 5, y + 3, x + 10, y + 21), fill=3)
    d.rectangle((x + 1, y, x + 14, y + 4), fill=1)
    d.rectangle((x + 3, y + 1, x + 12, y + 2), fill=6)
    d.ellipse((x - 3, y + 12, x + 18, y + 21), outline=9, width=2)


def draw_lamp(d: ImageDraw.ImageDraw, x: int, y: int) -> None:
    d.rectangle((x + 5, y + 8, x + 9, y + 80), fill=1)
    d.rectangle((x + 6, y + 9, x + 7, y + 78), fill=6)
    d.line((x + 7, y + 10, x + 22, y + 10), fill=1, width=3)
    d.line((x + 21, y + 10, x + 21, y + 21), fill=1, width=2)
    d.rectangle((x + 15, y + 20, x + 27, y + 34), fill=1)
    d.rectangle((x + 17, y + 22, x + 25, y + 32), fill=10)
    d.rectangle((x + 19, y + 24, x + 23, y + 30), fill=15)
    d.rectangle((x + 2, y + 76, x + 12, y + 82), fill=2)


def draw_rope_coil(d: ImageDraw.ImageDraw, x: int, y: int) -> None:
    for inset, color in ((0, 1), (2, 9), (4, 5), (6, 10)):
        d.ellipse((x + inset, y + inset // 2, x + 31 - inset, y + 15 - inset // 2),
                  outline=color, width=2)
    d.line((x + 25, y + 12, x + 39, y + 19), fill=1, width=3)
    d.line((x + 25, y + 11, x + 39, y + 18), fill=9, width=1)


def draw_bg_a() -> Image.Image:
    image = indexed_image(BG_A_PALETTE, 0)
    d = ImageDraw.Draw(image)

    # Pier edge and clean fighting deck.
    d.rectangle((0, 128, WIDTH - 1, 143), fill=1)
    for x in range(0, WIDTH, 16):
        d.rectangle((x, 128, x + 14, 135), fill=5 if (x // 16) & 1 else 6)
        d.line((x, 136, x + 15, 136), fill=2)
    d.rectangle((0, 144, WIDTH - 1, HEIGHT - 1), fill=7)
    for x in range(0, WIDTH, 32):
        d.rectangle((x, 144, x + 30, HEIGHT - 1), fill=7 if (x // 32) & 1 else 6)
        d.line((x + 30, 144, x + 30, HEIGHT - 1), fill=3, width=2)
        d.line((x + 3, 147, x + 26, 147), fill=9)
        d.line((x + 4, 202, x + 24, 202), fill=5)
    for y in (168, 192, 216):
        d.line((0, y, WIDTH - 1, y), fill=5)

    # Foam is a gameplay signal at the ring-out edge, not decoration everywhere.
    d.rectangle((272, 120, WIDTH - 1, 127), fill=12)
    for x in range(272, WIDTH, 12):
        d.line((x, 122, x + 5, 120), fill=15, width=2)
        d.line((x + 6, 120, x + 10, 123), fill=14, width=1)

    # Modular props frame the arena while preserving a clean center.
    draw_crate(d, 0, 104, 40, 40)
    draw_crate(d, 32, 120, 32, 32)
    draw_crate(d, 280, 112, 40, 40)
    draw_bollard(d, 72, 112)
    draw_rope_coil(d, 92, 125)
    draw_lamp(d, 244, 42)

    # Rope/net frame at far right. Sparse lines avoid covering active telegraphs.
    d.line((284, 80, 284, 127), fill=1, width=3)
    d.line((316, 72, 316, 127), fill=1, width=3)
    d.line((284, 84, 316, 76), fill=9, width=2)
    for y in range(88, 124, 8):
        d.line((286, y, 314, y - 5), fill=3)
    for x in range(288, 315, 8):
        d.line((x, 84, x - 1, 124), fill=3)
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--promote", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bg_b = draw_bg_b()
    bg_a = draw_bg_a()
    bg_b_path = OUT / "cais01_bg_b_mar_ceu_320x224_v01.png"
    bg_a_path = OUT / "cais01_bg_a_pier_modular_320x224_v01.png"
    save_indexed(bg_b, bg_b_path)
    save_indexed(bg_a, bg_a_path)

    proof = bg_b.convert("RGBA")
    proof.alpha_composite(rgba_with_index0_transparent(bg_a))
    REVIEW.mkdir(parents=True, exist_ok=True)
    proof_path = REVIEW / "cais01_modular_slice_virtual_proof_v01.png"
    proof.save(proof_path)

    bg_b_total, bg_b_unique = unique_tiles(bg_b)
    bg_a_total, bg_a_unique = unique_tiles(bg_a)
    promoted_paths: list[str] = []
    if args.promote:
        RES.mkdir(parents=True, exist_ok=True)
        for source in (bg_b_path, bg_a_path):
            target = RES / source.name
            shutil.copyfile(source, target)
            promoted_paths.append(str(target.relative_to(PROJECT)))

    report = {
        "schema_version": "1.0.0",
        "report_id": "cais01_modular_slice_build_v01",
        "generated_at": "2026-07-29",
        "status": (
            "res_runtime_candidate_pending_rom_visual_review"
            if args.promote
            else "offline_candidate_pending_review"
        ),
        "scene_id": "cais_01",
        "route": "level_art_modular_assembly",
        "forbidden_shortcuts_used": [],
        "source_direction": (
            "data/source_art/concept/authorial_style_validation_2026_07_04/"
            "dock_scene_kit_authorial_v01.png"
        ),
        "shared_canvas": {"width": WIDTH, "height": HEIGHT},
        "layers": {
            "bg_b": {
                "role": "dusk_sky_distant_industry_and_four_sea_bands",
                "path": str(bg_b_path.relative_to(PROJECT)),
                "palette_domain": "PAL0",
                "tiles_total": bg_b_total,
                "tiles_unique_exact": bg_b_unique,
            },
            "bg_a": {
                "role": "pier_edge_walkable_deck_and_modular_props",
                "path": str(bg_a_path.relative_to(PROJECT)),
                "palette_domain": "PAL2",
                "tiles_total": bg_a_total,
                "tiles_unique_exact": bg_a_unique,
                "ring_out_signal": "dark_water_plus_pale_foam_at_right_edge",
            },
        },
        "resident_estimate": {
            "unique_tiles_exact_total_before_rescomp": bg_b_unique + bg_a_unique,
            "bytes": (bg_b_unique + bg_a_unique) * 32,
            "measurement_level": "offline_exact_tile_hash_no_flip_dedup",
        },
        "review": str(proof_path.relative_to(PROJECT)),
        "promoted_paths": promoted_paths,
        "delivery_findings": [
            "locked-room first slice only; BG_A streaming world not yet built",
            "foreground occlusion and foam animation remain future modules",
            "runtime and ResComp measurements required before any final status",
        ],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(bg_b_path)
    print(bg_a_path)
    print(proof_path)
    print(REPORT)


if __name__ == "__main__":
    main()
