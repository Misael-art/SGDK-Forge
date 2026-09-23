#!/usr/bin/env python3
"""Build curated slice 1 assets for BENCHMARK_VISUAL_LAB_V2.

This is the canonical Scene 1 conversion route once the benchmark contract
already names the forest pack, the Mega Man sheet and the hold-frame staging.
Prefer this builder over OCR, thumbnail heuristics or manual bbox discovery.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

from build_bvl_showcase_assets import (
    blend_layers,
    cover_crop,
    ensure_dir,
    save_indexed_bg,
    save_indexed_sprite,
)


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_PROJECT_ROOT = WORKSPACE_ROOT / "SGDK_projects" / "BENCHMARK_VISUAL_LAB_V2"
DEFAULT_FOREST_ROOT = WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) vertical"
DEFAULT_MEGAMAN_PATH = (
    WORKSPACE_ROOT
    / "SGDK_projects"
    / "data"
    / "Sprite Sheet - Characters"
    / "Custom _ Edited - Mega Man Customs - DLN-001 Mega Man _ Rock - Mega Man (2).png"
)

BOARD_SIZE = (512, 512)
SCREEN_SIZE = (320, 224)
MOMENT1_ORIGIN = (64, 24)
MOMENT3_ORIGIN = (112, 288)
CAPTURE_ORIGIN = MOMENT3_ORIGIN
STREAM_PANEL_STRIDE = 128
STREAM_BANDS = [
    ("sky", 0, 224),
    ("bridge", 144, 368),
    ("forest", 288, 512),
]
BG_B_STREAM_PANEL_SIZE = (160, 224)
BG_A_STREAM_PANEL_SIZE = (128, 224)
SPRITE_CELL_W = 32
SPRITE_CELL_H = 48
SPRITE_BBOXES = [
    [16, 115, 47, 160],
    [52, 115, 83, 160],
]


def open_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def alpha_scale(image: Image.Image, factor: float) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A").point(lambda value: max(0, min(255, int(value * factor))))
    rgba.putalpha(alpha)
    return rgba


def black_to_alpha(image: Image.Image, threshold: int = 6) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, alpha = pixels[x, y]
            if red <= threshold and green <= threshold and blue <= threshold:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                pixels[x, y] = (red, green, blue, alpha)
    return rgba


def count_unique_tiles(image: Image.Image) -> int:
    indexed = image.convert("P")
    tiles: set[bytes] = set()
    for y in range(0, indexed.height, 8):
        for x in range(0, indexed.width, 8):
            tiles.add(bytes(indexed.crop((x, y, x + 8, y + 8)).tobytes()))
    return len(tiles)


def panel_origins(total_width: int, panel_width: int, stride: int) -> list[int]:
    origins = list(range(0, max(1, total_width - panel_width + 1), stride))
    final_origin = max(0, total_width - panel_width)
    if not origins or origins[-1] != final_origin:
        origins.append(final_origin)
    return origins


def export_streaming_panels(
    bg_b: Image.Image,
    bg_a: Image.Image,
    output_root: Path,
) -> dict:
    ensure_dir(output_root)
    planes = [
        ("bg_b", bg_b, BG_B_STREAM_PANEL_SIZE),
        ("bg_a", bg_a, BG_A_STREAM_PANEL_SIZE),
    ]
    manifest: dict[str, object] = {
        "strategy": "banded_horizontal_streaming",
        "panel_stride_px": STREAM_PANEL_STRIDE,
        "bands": [],
    }

    for band_name, y0, y1 in STREAM_BANDS:
        band_entry: dict[str, object] = {
            "band": band_name,
            "source_y_px": [y0, y1],
            "planes": {},
        }
        for plane_name, image, panel_size in planes:
            panel_width, panel_height = panel_size
            origins = panel_origins(image.width, panel_width, STREAM_PANEL_STRIDE)
            plane_entry = {
                "panel_size_px": [panel_width, panel_height],
                "panel_count": len(origins),
                "panels": [],
            }
            band_crop = image.crop((0, y0, image.width, y1)).convert("RGBA")
            for panel_index, origin_x in enumerate(origins):
                panel = band_crop.crop((origin_x, 0, origin_x + panel_width, panel_height)).convert("RGBA")
                panel_path = output_root / f"slice1_forest_vertical_{plane_name}_{band_name}_p{panel_index:02d}.png"
                save_indexed_bg(panel, panel_path, colors=16)
                plane_entry["panels"].append(
                    {
                        "index": panel_index,
                        "origin_px": [origin_x, y0],
                        "size_px": [panel_width, panel_height],
                        "unique_tiles_estimate": count_unique_tiles(panel),
                        "output": str(panel_path),
                    }
                )
            band_entry["planes"][plane_name] = plane_entry
        manifest["bands"].append(band_entry)

    return manifest


def compose_backgrounds(forest_root: Path) -> tuple[Image.Image, Image.Image]:
    sky = cover_crop(open_rgba(forest_root / "4 Forest parallax vertical skybox fulll.png"), BOARD_SIZE, 0.06)
    moon = cover_crop(open_rgba(forest_root / "4-1 Forest parallax vertical forest moon big.png"), BOARD_SIZE, 0.04)
    mountain = cover_crop(open_rgba(forest_root / "3 Forest parallax vertical mountain back.png"), BOARD_SIZE, 0.62)
    slow_cloud_far = cover_crop(open_rgba(forest_root / "8 Forest parallax vertical cloud 5.png"), BOARD_SIZE, 0.03)
    slow_cloud_mid = cover_crop(open_rgba(forest_root / "7 Forest parallax vertical cloud 4.png"), BOARD_SIZE, 0.18)
    fast_cloud_high = cover_crop(open_rgba(forest_root / "6 Forest parallax vertical cloud 3.png"), BOARD_SIZE, 0.38)
    fast_cloud_low = cover_crop(open_rgba(forest_root / "5 Forest parallax vertical cloud 2.png"), BOARD_SIZE, 0.62)
    mid = cover_crop(open_rgba(forest_root / "2 Forest parallax vertical forest mid.png"), BOARD_SIZE, 0.80)
    low = cover_crop(open_rgba(forest_root / "1 Forest parallax vertical forest low.png"), BOARD_SIZE, 0.86)
    front = cover_crop(open_rgba(forest_root / "0 Forest parallax vertical forest tree front.png"), BOARD_SIZE, 0.82)

    bg_b = blend_layers(
        ImageEnhance.Color(sky).enhance(1.08),
        [
            alpha_scale(ImageEnhance.Brightness(moon).enhance(0.95), 0.80),
            alpha_scale(ImageEnhance.Brightness(mountain).enhance(0.92), 0.86),
            alpha_scale(ImageEnhance.Brightness(slow_cloud_far).enhance(1.05), 0.70),
            alpha_scale(ImageEnhance.Brightness(slow_cloud_mid).enhance(1.02), 0.52),
        ],
    )
    bg_b = ImageEnhance.Color(bg_b).enhance(1.10)
    bg_b = ImageEnhance.Contrast(bg_b).enhance(1.04)
    bg_b = bg_b.filter(ImageFilter.GaussianBlur(radius=0.25))

    bg_a = blend_layers(
        Image.new("RGBA", BOARD_SIZE, (0, 0, 0, 0)),
        [
            alpha_scale(ImageEnhance.Brightness(fast_cloud_high).enhance(1.08), 0.84),
            alpha_scale(ImageEnhance.Brightness(fast_cloud_low).enhance(1.12), 0.88),
            ImageEnhance.Brightness(mid).enhance(0.96),
            ImageEnhance.Brightness(low).enhance(1.02),
            front,
        ],
    )
    bg_a = ImageEnhance.Color(bg_a).enhance(1.06)
    bg_a = ImageEnhance.Contrast(bg_a).enhance(1.08)
    bg_a = bg_a.filter(ImageFilter.UnsharpMask(radius=1, percent=65, threshold=2))

    return bg_b, bg_a


def build_stand_sprite_sheet(megaman_path: Path) -> tuple[Image.Image, dict]:
    source = open_rgba(megaman_path)
    sheet = Image.new("RGBA", (SPRITE_CELL_W * len(SPRITE_BBOXES), SPRITE_CELL_H), (0, 0, 0, 0))
    frames: list[dict] = []

    for index, bbox in enumerate(SPRITE_BBOXES):
        crop = source.crop(tuple(bbox)).convert("RGBA")
        paste_x = (SPRITE_CELL_W - crop.width) // 2
        paste_y = SPRITE_CELL_H - crop.height
        sheet.alpha_composite(crop, (index * SPRITE_CELL_W + paste_x, paste_y))
        frames.append(
            {
                "frame_index": index,
                "source_bbox": bbox,
                "crop_size_px": [crop.width, crop.height],
                "paste_offset_px": [paste_x, paste_y],
            }
        )

    manifest = {
        "animation": "stand",
        "frame_count": len(SPRITE_BBOXES),
        "frame_size_px": [SPRITE_CELL_W, SPRITE_CELL_H],
        "frame_size_tiles": [SPRITE_CELL_W // 8, SPRITE_CELL_H // 8],
        "pivot_policy": "bottom_center",
        "pivot_px": [SPRITE_CELL_W // 2, SPRITE_CELL_H - 1],
        "frames": frames,
    }
    return sheet, manifest


def compose_virtual_proof(bg_b: Image.Image, bg_a: Image.Image, origin: tuple[int, int]) -> Image.Image:
    origin_x, origin_y = origin
    bg_b_crop = bg_b.crop((origin_x, origin_y, origin_x + SCREEN_SIZE[0], origin_y + SCREEN_SIZE[1])).convert("RGBA")
    bg_a_crop = black_to_alpha(
        bg_a.crop((origin_x, origin_y, origin_x + SCREEN_SIZE[0], origin_y + SCREEN_SIZE[1])).convert("RGBA")
    )
    proof = Image.alpha_composite(bg_b_crop, bg_a_crop)
    return proof


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the curated Scene 1 asset pack for BENCHMARK_VISUAL_LAB_V2. "
            "Outputs BG_B, BG_A, the Mega Man stand sheet, a virtual proof and source-case manifests."
        )
    )
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT)
    parser.add_argument("--forest-root", type=Path, default=DEFAULT_FOREST_ROOT)
    parser.add_argument("--megaman-path", type=Path, default=DEFAULT_MEGAMAN_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    case_root = project_root / "doc" / "source_cases" / "slice1_multiplane"
    reports_root = case_root / "reports"
    res_bgs = project_root / "res" / "bgs"
    res_bgs_streaming = res_bgs / "streaming"
    res_sprites = project_root / "res" / "sprites"

    for path in (case_root, reports_root, res_bgs, res_bgs_streaming, res_sprites):
        ensure_dir(path)

    bg_b, bg_a = compose_backgrounds(args.forest_root.resolve())
    sprite_sheet, sprite_manifest = build_stand_sprite_sheet(args.megaman_path.resolve())

    bg_b_path = res_bgs / "slice1_forest_vertical_bg_b.png"
    bg_a_path = res_bgs / "slice1_forest_vertical_bg_a.png"
    sprite_path = res_sprites / "spr_megaman_stand_v2.png"

    save_indexed_bg(bg_b, bg_b_path, colors=16)
    save_indexed_bg(bg_a, bg_a_path, colors=16)
    save_indexed_sprite(sprite_sheet, sprite_path, max_colors=16)
    streaming_manifest = export_streaming_panels(bg_b, bg_a, res_bgs_streaming)

    proof_moment1 = compose_virtual_proof(bg_b, bg_a, MOMENT1_ORIGIN)
    proof_moment3 = compose_virtual_proof(bg_b, bg_a, MOMENT3_ORIGIN)
    proof_capture = compose_virtual_proof(bg_b, bg_a, CAPTURE_ORIGIN)
    proof_moment1_path = reports_root / "virtual_proof_moment1.png"
    proof_moment3_path = reports_root / "virtual_proof_moment3.png"
    proof_capture_path = reports_root / "virtual_proof_capture.png"
    proof_hold_path = reports_root / "virtual_proof_hold.png"
    proof_moment1.save(proof_moment1_path)
    proof_moment3.save(proof_moment3_path)
    proof_capture.save(proof_capture_path)
    proof_capture.save(proof_hold_path)

    animation_manifest = {
        "case_id": "slice1_megaman_stand",
        "scene_key": "slice1_multiplane",
        "source_path": str(args.megaman_path.resolve()),
        "generated_asset": str(sprite_path),
        "normalization": {
            "pivot_policy": "bottom_center",
            "frame_size_px": [SPRITE_CELL_W, SPRITE_CELL_H],
            "frame_size_tiles": [SPRITE_CELL_W // 8, SPRITE_CELL_H // 8],
        },
        "sequences": [sprite_manifest],
    }

    case_manifest = {
        "case_id": "slice1_multiplane_vertical_forest",
        "scene_key": "slice1_multiplane",
        "source_original": [
            str(args.forest_root.resolve()),
            str(args.megaman_path.resolve()),
        ],
        "source_type": "vertical_multilayer_background_pack_plus_sprite_sheet",
        "board_size_px": list(BOARD_SIZE),
        "screen_window_px": list(SCREEN_SIZE),
        "hold_window_origin_px": list(CAPTURE_ORIGIN),
        "outputs": {
            "bg_b": str(bg_b_path.relative_to(project_root)),
            "bg_a": str(bg_a_path.relative_to(project_root)),
            "sprite": str(sprite_path.relative_to(project_root)),
            "virtual_proof": str(proof_capture_path.relative_to(project_root)),
            "streaming_panels_root": str(res_bgs_streaming.relative_to(project_root)),
        },
        "contracts": {
            "bg_b_role": "sky_moon_mountain_slow_clouds",
            "bg_a_role": "fast_clouds_mid_low_front_occlusion",
            "sprite_role": "megaman_stand_reference",
            "camera_contract": "loop_4_moments",
            "tilemap_strategy": "banded_horizontal_streaming",
        },
        "artifacts": {
            "sprite_animation_manifest": "doc/source_cases/slice1_multiplane/reports/megaman_stand_animation_manifest.json",
            "virtual_proof": str(proof_capture_path.relative_to(project_root)),
            "virtual_proof_hold_compat": str(proof_hold_path.relative_to(project_root)),
            "virtual_proof_moment1": str(proof_moment1_path.relative_to(project_root)),
            "virtual_proof_moment3": str(proof_moment3_path.relative_to(project_root)),
            "streaming_panel_manifest": "doc/source_cases/slice1_multiplane/reports/streaming_panel_manifest.json",
        },
        "camera_windows": {
            "moment_1_sky_horizontal": list(MOMENT1_ORIGIN),
            "moment_3_forest_horizontal": list(MOMENT3_ORIGIN),
            "capture_window": list(CAPTURE_ORIGIN),
        },
    }

    (reports_root / "megaman_stand_animation_manifest.json").write_text(
        json.dumps(animation_manifest, indent=2),
        encoding="utf-8",
    )
    (reports_root / "streaming_panel_manifest.json").write_text(
        json.dumps(streaming_manifest, indent=2),
        encoding="utf-8",
    )
    (case_root / "case_manifest.json").write_text(json.dumps(case_manifest, indent=2), encoding="utf-8")

    print(f"OK BENCHMARK_VISUAL_LAB_V2 slice1 assets rebuilt at {project_root}.")


if __name__ == "__main__":
    main()
