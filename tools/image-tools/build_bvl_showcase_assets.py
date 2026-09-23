#!/usr/bin/env python3
"""Build BENCHMARK_VISUAL_LAB showcase assets and source-case manifests."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from export_source_structure import background_to_alpha
from infer_source_structure import build_color_mask, connected_components, dominant_border_color


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
PROJECT_ROOT = WORKSPACE_ROOT / "SGDK_projects" / "BENCHMARK_VISUAL_LAB"
CASE_ROOT = PROJECT_ROOT / "doc" / "source_cases"
RES_ROOT = PROJECT_ROOT / "res"
SPRITES_ROOT = RES_ROOT / "sprites"
BGS_ROOT = RES_ROOT / "bgs"

MAGENTA = (255, 0, 255)
MD_LEVELS = [0, 34, 68, 102, 136, 170, 204, 238]


@dataclass
class SpriteCaseConfig:
    case_id: str
    scene_key: str
    menu_slot: int
    source_path: Path
    source_type: str
    output_path: Path
    preview_path: Path
    animation_manifest_path: Path
    case_manifest_path: Path
    labels: list[str]
    frame_count: int
    target_cell_w: int
    target_cell_h: int
    min_area: int
    row_tolerance: int
    min_frames_per_row: int
    width_range: tuple[int, int] | None = None
    height_range: tuple[int, int] | None = None


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def round_up(value: int, step: int) -> int:
    return ((value + step - 1) // step) * step


def snap_channel(value: int) -> int:
    return min(MD_LEVELS, key=lambda level: abs(level - value))


def snap_palette_rgba(image: Image.Image, colors: int, dither: bool) -> Image.Image:
    dither_mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    paletted = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors, dither=dither_mode)
    palette = paletted.getpalette()
    used_indices = sorted(set(paletted.tobytes()))
    for index in used_indices:
        base = index * 3
        palette[base + 0] = snap_channel(palette[base + 0])
        palette[base + 1] = snap_channel(palette[base + 1])
        palette[base + 2] = snap_channel(palette[base + 2])
    paletted.putpalette(palette)
    return paletted.convert("RGBA")


def save_indexed_sprite(image: Image.Image, destination: Path, max_colors: int = 16) -> None:
    rgba = image.convert("RGBA")
    flat = Image.new("RGBA", rgba.size, (*MAGENTA, 255))
    flat.alpha_composite(rgba)
    indexed = flat.convert("P", palette=Image.Palette.ADAPTIVE, colors=max_colors, dither=Image.Dither.NONE)
    palette = indexed.getpalette()
    used_indices = sorted(set(indexed.tobytes()))

    magenta_index = 0
    best_distance = 999999
    for index in used_indices:
        base = index * 3
        color = palette[base : base + 3]
        distance = abs(color[0] - MAGENTA[0]) + abs(color[1] - MAGENTA[1]) + abs(color[2] - MAGENTA[2])
        if distance < best_distance:
            best_distance = distance
            magenta_index = index

    if magenta_index != 0:
        for channel in range(3):
            palette[channel], palette[(magenta_index * 3) + channel] = palette[(magenta_index * 3) + channel], palette[channel]

        pixels = list(indexed.tobytes())
        remapped: list[int] = []
        for pixel in pixels:
            if pixel == 0:
                remapped.append(magenta_index)
            elif pixel == magenta_index:
                remapped.append(0)
            else:
                remapped.append(pixel)
        indexed.putdata(remapped)

    palette[0] = 0xEE
    palette[1] = 0x00
    palette[2] = 0xEE

    for index in used_indices:
        base = index * 3
        palette[base + 0] = snap_channel(palette[base + 0])
        palette[base + 1] = snap_channel(palette[base + 1])
        palette[base + 2] = snap_channel(palette[base + 2])

    indexed.putpalette(palette)
    ensure_dir(destination.parent)
    indexed.save(destination, transparency=0)


def build_opaque_palette(image: Image.Image, colors: int) -> Image.Image:
    rgba = image.convert("RGBA")
    opaque_pixels = [
        (red, green, blue)
        for red, green, blue, alpha in rgba.getdata()
        if alpha > 0
    ]

    if not opaque_pixels:
        palette_source = Image.new("P", (1, 1))
        palette = [0] * (256 * 3)
        palette_source.putpalette(palette)
        return palette_source

    sample = Image.new("RGB", (len(opaque_pixels), 1))
    sample.putdata(opaque_pixels)
    return sample.quantize(colors=max(1, colors - 1), dither=Image.Dither.NONE)


def build_shared_opaque_palette(images: Iterable[Image.Image], colors: int) -> Image.Image:
    opaque_pixels: list[tuple[int, int, int]] = []

    for image in images:
        rgba = image.convert("RGBA")
        opaque_pixels.extend(
            (red, green, blue)
            for red, green, blue, alpha in rgba.getdata()
            if alpha > 0
        )

    if not opaque_pixels:
        palette_source = Image.new("P", (1, 1))
        palette = [0] * (256 * 3)
        palette_source.putpalette(palette)
        return palette_source

    sample = Image.new("RGB", (len(opaque_pixels), 1))
    sample.putdata(opaque_pixels)
    return sample.quantize(colors=max(1, colors - 1), dither=Image.Dither.NONE)


def save_indexed_bg(
    image: Image.Image,
    destination: Path,
    colors: int = 16,
    palette_image: Image.Image | None = None,
) -> None:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    opaque_mask = alpha.point(lambda value: 255 if value > 0 else 0)
    visible_rgb = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    visible_rgb.paste(rgba, mask=opaque_mask)
    palette_source = palette_image if palette_image is not None else build_opaque_palette(rgba, colors)
    indexed_visible = visible_rgb.convert("RGB").quantize(
        palette=palette_source,
        dither=Image.Dither.NONE,
    )
    palette = indexed_visible.getpalette()
    visible_pixels = list(indexed_visible.tobytes())
    alpha_pixels = list(alpha.tobytes())
    remapped: list[int] = []

    final_palette = [0] * (256 * 3)
    # Keep index 0 reserved for structural transparency and serialize that
    # contract in the PNG itself as well. SGDK already treats palette entry 0
    # as transparent at render time; writing tRNS keeps downstream validators
    # aligned with the same intent.
    final_palette[0] = 0x00
    final_palette[1] = 0x00
    final_palette[2] = 0x00

    for index in range(max(1, colors - 1)):
        src = index * 3
        dst = (index + 1) * 3
        final_palette[dst + 0] = snap_channel(palette[src + 0])
        final_palette[dst + 1] = snap_channel(palette[src + 1])
        final_palette[dst + 2] = snap_channel(palette[src + 2])

    for alpha_value, pixel in zip(alpha_pixels, visible_pixels):
        if alpha_value == 0:
            remapped.append(0)
        else:
            remapped.append(min(pixel + 1, colors - 1))

    indexed = Image.new("P", rgba.size)
    indexed.putpalette(final_palette[: colors * 3])
    indexed.putdata(remapped)

    ensure_dir(destination.parent)
    indexed.save(destination, bits=4, transparency=0)


def cover_crop(image: Image.Image, target_size: tuple[int, int], vertical_bias: float = 0.5) -> Image.Image:
    src_w, src_h = image.size
    dst_w, dst_h = target_size
    scale = max(dst_w / src_w, dst_h / src_h)
    scaled = image.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
    left = max(0, (scaled.width - dst_w) // 2)
    top = max(0, round((scaled.height - dst_h) * vertical_bias))
    top = min(top, max(0, scaled.height - dst_h))
    return scaled.crop((left, top, left + dst_w, top + dst_h))


def blend_layers(base: Image.Image, overlays: list[Image.Image]) -> Image.Image:
    result = base.convert("RGBA")
    for layer in overlays:
        result.alpha_composite(layer.convert("RGBA"))
    return result


def detect_source_rgba(path: Path) -> tuple[Image.Image, tuple[int, int, int]]:
    image = Image.open(path).convert("RGBA")
    border = dominant_border_color(np.array(image))
    if image.getchannel("A").getbbox() is None:
        image = background_to_alpha(image, border, threshold=24, remove_internal_key_holes=True)
    elif image.getchannel("A").getextrema() == (255, 255):
        image = background_to_alpha(image, border, threshold=24, remove_internal_key_holes=True)
    return image, border


def filter_components(
    components: list[dict[str, Any]],
    width_range: tuple[int, int] | None,
    height_range: tuple[int, int] | None,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for item in components:
        width = item["width"]
        height = item["height"]
        if width_range is not None and not (width_range[0] <= width <= width_range[1]):
            continue
        if height_range is not None and not (height_range[0] <= height <= height_range[1]):
            continue
        filtered.append(item)
    return filtered


def group_rows(components: list[dict[str, Any]], tolerance: int, min_frames_per_row: int) -> list[list[dict[str, Any]]]:
    rows: list[list[dict[str, Any]]] = []
    for component in sorted(components, key=lambda item: (item["bbox"][3], item["bbox"][0])):
        bottom = component["bbox"][3]
        placed = False
        for row in rows:
            row_bottom = int(sum(entry["bbox"][3] for entry in row) / len(row))
            if abs(row_bottom - bottom) <= tolerance:
                row.append(component)
                placed = True
                break
        if not placed:
            rows.append([component])

    normalized: list[list[dict[str, Any]]] = []
    for row in rows:
        ordered = sorted(row, key=lambda item: item["bbox"][0])
        if len(ordered) >= min_frames_per_row:
            normalized.append(ordered)

    normalized.sort(key=lambda row: (-len(row), row[0]["bbox"][1]))
    return normalized


def pick_frames(row: list[dict[str, Any]], frame_count: int) -> list[dict[str, Any]]:
    if len(row) == frame_count:
        return row
    if len(row) < frame_count:
        padded = list(row)
        while len(padded) < frame_count:
            padded.append(padded[-1])
        return padded

    result: list[dict[str, Any]] = []
    for index in range(frame_count):
        sample = round((index * (len(row) - 1)) / max(1, frame_count - 1))
        result.append(row[sample])
    return result


def crop_component(source: Image.Image, bbox: list[int]) -> Image.Image:
    return source.crop(tuple(bbox)).convert("RGBA")


def save_contact_sheet(rows: list[list[dict[str, Any]]], source: Image.Image, destination: Path) -> None:
    swatch_w = 64
    swatch_h = 64
    width = swatch_w * max(1, max(len(row) for row in rows))
    height = swatch_h * max(1, len(rows))
    canvas = Image.new("RGBA", (width, height), (20, 24, 34, 255))
    for row_index, row in enumerate(rows):
        for col_index, component in enumerate(row):
            crop = crop_component(source, component["bbox"])
            fitted = ImageOps.contain(crop, (swatch_w - 4, swatch_h - 4), Image.Resampling.NEAREST)
            tile = Image.new("RGBA", (swatch_w, swatch_h), (28, 34, 46, 255))
            tile.alpha_composite(fitted, ((swatch_w - fitted.width) // 2, swatch_h - fitted.height - 2))
            canvas.alpha_composite(tile, (col_index * swatch_w, row_index * swatch_h))
    ensure_dir(destination.parent)
    canvas.save(destination)


def build_sprite_case(config: SpriteCaseConfig) -> dict[str, Any]:
    source, border = detect_source_rgba(config.source_path)
    alpha = np.array(source.getchannel("A"))
    mask = build_color_mask(np.array(source), border, threshold=24)
    if alpha.size and alpha.max() > 0:
        mask = mask | (alpha > 0)

    components = connected_components(mask, min_area=config.min_area)
    components = filter_components(components, config.width_range, config.height_range)
    rows = group_rows(components, config.row_tolerance, config.min_frames_per_row)
    selected_rows = rows[: len(config.labels)]
    if len(selected_rows) < len(config.labels):
        raise RuntimeError(f"{config.case_id}: rows insuficientes detectadas ({len(selected_rows)}).")

    max_w = max(config.target_cell_w, max(item["width"] for row in selected_rows for item in row))
    max_h = max(config.target_cell_h, max(item["height"] for row in selected_rows for item in row))
    cell_w = round_up(max_w, 8)
    cell_h = round_up(max_h, 8)

    sheet = Image.new("RGBA", (cell_w * config.frame_count, cell_h * len(config.labels)), (0, 0, 0, 0))
    manifest_sequences: list[dict[str, Any]] = []

    for row_index, label in enumerate(config.labels):
        picked = pick_frames(selected_rows[row_index], config.frame_count)
        frames_payload: list[dict[str, Any]] = []
        for col_index, component in enumerate(picked):
            crop = crop_component(source, component["bbox"])
            paste_x = (cell_w - crop.width) // 2
            paste_y = cell_h - crop.height
            sheet.alpha_composite(crop, (col_index * cell_w + paste_x, row_index * cell_h + paste_y))
            frames_payload.append(
                {
                    "frame_index": col_index,
                    "source_bbox": component["bbox"],
                    "crop_size_px": [crop.width, crop.height],
                    "paste_offset_px": [paste_x, paste_y],
                }
            )

        manifest_sequences.append(
            {
                "animation": label,
                "frame_count": config.frame_count,
                "frame_size_px": [cell_w, cell_h],
                "frame_size_tiles": [cell_w // 8, cell_h // 8],
                "pivot_policy": "bottom_center",
                "pivot_px": [cell_w // 2, cell_h - 1],
                "frames": frames_payload,
            }
        )

    save_indexed_sprite(sheet, config.output_path)
    save_contact_sheet(selected_rows, source, config.preview_path)

    animation_manifest = {
        "case_id": config.case_id,
        "scene_key": config.scene_key,
        "menu_slot": config.menu_slot,
        "source_path": str(config.source_path),
        "source_type": config.source_type,
        "normalization": {
            "pivot_policy": "bottom_center",
            "frame_size_px": [cell_w, cell_h],
            "frame_size_tiles": [cell_w // 8, cell_h // 8],
            "background_key_rgb": list(border),
        },
        "sequences": manifest_sequences,
        "generated_asset": str(config.output_path),
        "preview": str(config.preview_path),
        "scripts_used": [
            "tools/image-tools/infer_source_structure.py",
            "tools/image-tools/export_source_structure.py",
            "tools/image-tools/analyze_source_semantics.py",
            "tools/image-tools/build_bvl_showcase_assets.py",
        ],
    }
    ensure_dir(config.animation_manifest_path.parent)
    config.animation_manifest_path.write_text(json.dumps(animation_manifest, indent=2), encoding="utf-8")

    case_manifest = {
        "case_id": config.case_id,
        "scene_key": config.scene_key,
        "menu_slot": config.menu_slot,
        "source_original": str(config.source_path),
        "source_type": config.source_type,
        "output_expected": [
            "sgdk_ready_sprite_sheet",
            "animation_manifest",
            "contact_sheet_preview",
        ],
        "scripts_used": animation_manifest["scripts_used"],
        "assets_generated_in_res": [str(config.output_path.relative_to(PROJECT_ROOT))],
        "artifacts": {
            "animation_manifest": str(config.animation_manifest_path),
            "preview": str(config.preview_path),
        },
    }
    ensure_dir(config.case_manifest_path.parent)
    config.case_manifest_path.write_text(json.dumps(case_manifest, indent=2), encoding="utf-8")
    return animation_manifest


def compose_forest_case() -> None:
    case_dir = CASE_ROOT / "case_04_forest_baby_mario"
    ensure_dir(case_dir)
    target = (512, 256)

    sky = cover_crop(Image.open(WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) horizontal" / "forest_sky.png").convert("RGBA"), target, 0.0)
    back = cover_crop(Image.open(WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) horizontal" / "forest_back.png").convert("RGBA"), target, 0.18)
    long_layer = cover_crop(Image.open(WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) horizontal" / "forest_long.png").convert("RGBA"), target, 0.2)
    mid = cover_crop(Image.open(WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) horizontal" / "forest_mid.png").convert("RGBA"), target, 0.22)
    short_layer = cover_crop(Image.open(WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) horizontal" / "forest_short.png").convert("RGBA"), target, 0.28)

    bg_b = blend_layers(sky, [ImageEnhance.Brightness(back).enhance(0.88), ImageEnhance.Brightness(long_layer).enhance(0.82)])
    bg_b = ImageEnhance.Color(bg_b).enhance(0.78)
    bg_b = ImageEnhance.Contrast(bg_b).enhance(0.92)

    bg_a = blend_layers(Image.new("RGBA", target, (0, 0, 0, 0)), [mid, short_layer])
    bg_a = ImageEnhance.Color(bg_a).enhance(0.92)
    bg_a = ImageEnhance.Contrast(bg_a).enhance(1.08)
    bg_a = bg_a.filter(ImageFilter.UnsharpMask(radius=1, percent=70, threshold=2))

    bg_b_path = BGS_ROOT / "forest_showcase_bg_b.png"
    bg_a_path = BGS_ROOT / "forest_showcase_bg_a.png"
    save_indexed_bg(bg_b, bg_b_path, colors=16)
    save_indexed_bg(bg_a, bg_a_path, colors=16)

    baby_case = SpriteCaseConfig(
        case_id="case_04_forest_baby_mario_sprite",
        scene_key="scene_multiplane",
        menu_slot=4,
        source_path=WORKSPACE_ROOT / "SGDK_projects" / "data" / "Sprites Organizados" / "Rips de Jogos" / "Game Boy Advance" / "Super Mario Advance 3_ Yoshi's Island" / "Playable Characters" / "Game Boy Advance - Super Mario Advance 3_ Yoshi's Island - Playable Characters - Baby Mario.png",
        source_type="sprite_sheet",
        output_path=SPRITES_ROOT / "spr_baby_mario_showcase.png",
        preview_path=case_dir / "reports" / "baby_mario_contact_sheet.png",
        animation_manifest_path=case_dir / "reports" / "baby_mario_animation_manifest.json",
        case_manifest_path=case_dir / "sprite_case_manifest.json",
        labels=["idle", "walk", "walk_fast", "celebrate"],
        frame_count=6,
        target_cell_w=32,
        target_cell_h=32,
        min_area=24,
        row_tolerance=8,
        min_frames_per_row=3,
        width_range=(8, 40),
        height_range=(12, 40),
    )
    baby_manifest = build_sprite_case(baby_case)

    case_manifest = {
        "case_id": "case_04_forest_baby_mario",
        "scene_key": "scene_multiplane",
        "menu_slot": 4,
        "source_original": [
            str(WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) horizontal"),
            str(baby_case.source_path),
        ],
        "source_type": "multilayer_background_pack_plus_sprite_sheet",
        "output_expected": [
            "bg_b_showcase",
            "bg_a_showcase",
            "sprite_sheet_bottom_center",
        ],
        "scripts_used": [
            "tools/image-tools/build_bvl_showcase_assets.py",
            "tools/image-tools/infer_source_structure.py",
            "tools/image-tools/export_source_structure.py",
            "tools/image-tools/analyze_source_semantics.py",
        ],
        "assets_generated_in_res": [
            str(bg_b_path.relative_to(PROJECT_ROOT)),
            str(bg_a_path.relative_to(PROJECT_ROOT)),
            str(baby_case.output_path.relative_to(PROJECT_ROOT)),
        ],
        "contracts": {
            "overlay_mode": "window_toggle_hidden",
            "ground_baseline_px": 184,
            "hero_pivot_policy": "bottom_center",
            "hero_manifest": str(baby_case.animation_manifest_path),
        },
        "artifacts": {
            "sprite_manifest": baby_manifest,
        },
    }
    (case_dir / "case_manifest.json").write_text(json.dumps(case_manifest, indent=2), encoding="utf-8")


def compose_desert_case() -> None:
    case_dir = CASE_ROOT / "case_09_desert_mount_depth"
    ensure_dir(case_dir)
    target = (512, 256)
    base = WORKSPACE_ROOT / "SGDK_projects" / "data" / "Sprites Organizados" / "Asset Packs" / "BG_DesertMountains"

    bg1 = cover_crop(Image.open(base / "background1.png").convert("RGBA"), target, 0.1)
    bg2 = cover_crop(Image.open(base / "background2.png").convert("RGBA"), target, 0.18)
    bg3 = cover_crop(Image.open(base / "background3.png").convert("RGBA"), target, 0.24)

    bg_b = ImageEnhance.Color(bg1).enhance(0.72)
    bg_b = ImageEnhance.Brightness(bg_b).enhance(0.95)
    bg_b = bg_b.filter(ImageFilter.GaussianBlur(radius=0.7))

    bg_a = blend_layers(Image.new("RGBA", target, (0, 0, 0, 0)), [bg2, bg3])
    bg_a = ImageEnhance.Color(bg_a).enhance(0.95)
    bg_a = ImageEnhance.Contrast(bg_a).enhance(1.08)

    bg_b_path = BGS_ROOT / "desert_tower_bg_b.png"
    bg_a_path = BGS_ROOT / "desert_tower_bg_a.png"
    save_indexed_bg(bg_b, bg_b_path, colors=16)
    save_indexed_bg(bg_a, bg_a_path, colors=16)

    case_manifest = {
        "case_id": "case_09_desert_mount_depth",
        "scene_key": "scene_pseudo3d_tower_lab",
        "menu_slot": 9,
        "source_original": str(base),
        "source_type": "multilayer_background_pack",
        "output_expected": ["bg_b_depth_backdrop", "bg_a_depth_band"],
        "scripts_used": [
            "tools/image-tools/build_bvl_showcase_assets.py",
            "tools/image-tools/infer_source_structure.py",
            "tools/image-tools/export_source_structure.py",
            "tools/image-tools/analyze_source_semantics.py",
        ],
        "assets_generated_in_res": [
            str(bg_b_path.relative_to(PROJECT_ROOT)),
            str(bg_a_path.relative_to(PROJECT_ROOT)),
        ],
        "contracts": {
            "overlay_mode": "window_toggle_hidden",
            "vscroll_mode": "column_depth",
            "base_scroll_range_px": [-24, 24],
        },
    }
    (case_dir / "case_manifest.json").write_text(json.dumps(case_manifest, indent=2), encoding="utf-8")


def compose_hill_case() -> None:
    case_dir = CASE_ROOT / "case_10_hill_masked_light"
    ensure_dir(case_dir)
    target = (512, 256)
    base = WORKSPACE_ROOT / "SGDK_projects" / "data" / "Sprites Organizados" / "Asset Packs" / "Free Pixel Art Hill" / "PNG"

    layers = [cover_crop(Image.open(base / f"Hills Layer 0{i}.png").convert("RGBA"), target, 0.25) for i in range(1, 7)]
    bg_b = blend_layers(layers[0], [ImageEnhance.Brightness(layers[1]).enhance(0.92)])
    bg_b = ImageEnhance.Color(bg_b).enhance(0.78)
    bg_b = ImageEnhance.Brightness(bg_b).enhance(0.98)

    bg_a = blend_layers(Image.new("RGBA", target, (0, 0, 0, 0)), layers[2:])
    bg_a = ImageEnhance.Color(bg_a).enhance(0.95)
    bg_a = ImageEnhance.Contrast(bg_a).enhance(1.08)

    bg_b_path = BGS_ROOT / "hill_light_bg_b.png"
    bg_a_path = BGS_ROOT / "hill_light_bg_a.png"
    save_indexed_bg(bg_b, bg_b_path, colors=16)
    save_indexed_bg(bg_a, bg_a_path, colors=16)

    case_manifest = {
        "case_id": "case_10_hill_masked_light",
        "scene_key": "scene_masked_light_lab",
        "menu_slot": 10,
        "source_original": str(base),
        "source_type": "multilayer_background_pack",
        "output_expected": ["bg_b_far_hill", "bg_a_light_receiver"],
        "scripts_used": [
            "tools/image-tools/build_bvl_showcase_assets.py",
            "tools/image-tools/infer_source_structure.py",
            "tools/image-tools/export_source_structure.py",
            "tools/image-tools/analyze_source_semantics.py",
        ],
        "assets_generated_in_res": [
            str(bg_b_path.relative_to(PROJECT_ROOT)),
            str(bg_a_path.relative_to(PROJECT_ROOT)),
        ],
        "contracts": {
            "overlay_mode": "window_toggle_hidden",
            "hint_palette_split": True,
            "split_line_default_px": 104,
        },
    }
    (case_dir / "case_manifest.json").write_text(json.dumps(case_manifest, indent=2), encoding="utf-8")


def build_sprite_cases() -> None:
    cases = [
        SpriteCaseConfig(
            case_id="case_02_earthquake_sheet",
            scene_key="scene_sprite_anim",
            menu_slot=2,
            source_path=WORKSPACE_ROOT / "SGDK_projects" / "data" / "Sprite Sheet - Figthing games" / "Sprite Sheet Earthquake_large.png",
            source_type="large_sprite_sheet",
            output_path=SPRITES_ROOT / "spr_earthquake_showcase.png",
            preview_path=CASE_ROOT / "case_02_earthquake_sheet" / "reports" / "contact_sheet.png",
            animation_manifest_path=CASE_ROOT / "case_02_earthquake_sheet" / "reports" / "animation_manifest.json",
            case_manifest_path=CASE_ROOT / "case_02_earthquake_sheet" / "case_manifest.json",
            labels=["idle", "walk", "attack", "impact", "jump"],
            frame_count=6,
            target_cell_w=64,
            target_cell_h=80,
            min_area=120,
            row_tolerance=14,
            min_frames_per_row=4,
            width_range=(20, 120),
            height_range=(24, 120),
        ),
        SpriteCaseConfig(
            case_id="case_03_megaman_pose_viewer",
            scene_key="scene_character_design",
            menu_slot=3,
            source_path=WORKSPACE_ROOT / "SGDK_projects" / "data" / "Sprite Sheet - Characters" / "Sprite Sheet MegaMan_8.png",
            source_type="sprite_sheet",
            output_path=SPRITES_ROOT / "spr_megaman_showcase.png",
            preview_path=CASE_ROOT / "case_03_megaman_pose_viewer" / "reports" / "contact_sheet.png",
            animation_manifest_path=CASE_ROOT / "case_03_megaman_pose_viewer" / "reports" / "animation_manifest.json",
            case_manifest_path=CASE_ROOT / "case_03_megaman_pose_viewer" / "case_manifest.json",
            labels=["idle", "walk", "shoot", "jump", "pose"],
            frame_count=6,
            target_cell_w=40,
            target_cell_h=48,
            min_area=60,
            row_tolerance=10,
            min_frames_per_row=4,
            width_range=(12, 56),
            height_range=(20, 64),
        ),
        SpriteCaseConfig(
            case_id="case_08_boss_kinematics_core",
            scene_key="scene_boss_kinematics_lab",
            menu_slot=8,
            source_path=Path(r"F:\Projects\MEGADR~1\SGDK_P~1\data\SPRITE~2\RIPSDE~1\GAMEBO~1\ASTERI~1\PLAYAB~2\GAMEBO~2.GIF"),
            source_type="sprite_sheet_gif",
            output_path=SPRITES_ROOT / "spr_boss_core_showcase.png",
            preview_path=CASE_ROOT / "case_08_boss_kinematics" / "reports" / "boss_contact_sheet.png",
            animation_manifest_path=CASE_ROOT / "case_08_boss_kinematics" / "reports" / "boss_animation_manifest.json",
            case_manifest_path=CASE_ROOT / "case_08_boss_kinematics" / "boss_case_manifest.json",
            labels=["idle", "walk", "run", "attack"],
            frame_count=6,
            target_cell_w=48,
            target_cell_h=64,
            min_area=80,
            row_tolerance=10,
            min_frames_per_row=4,
            width_range=(16, 72),
            height_range=(24, 80),
        ),
        SpriteCaseConfig(
            case_id="case_08_medama_orbiters",
            scene_key="scene_boss_kinematics_lab",
            menu_slot=8,
            source_path=WORKSPACE_ROOT / "SGDK_projects" / "data" / "Sprites Organizados" / "Rips de Jogos" / "Game Boy Advance" / "GeGeGe no Kitarou (JPN)" / "Playable Characters" / "Game Boy Advance - GeGeGe no Kitarou (JPN) - Playable Characters - Medama Oyaji.png",
            source_type="sprite_sheet",
            output_path=SPRITES_ROOT / "spr_medama_orbiter.png",
            preview_path=CASE_ROOT / "case_08_boss_kinematics" / "reports" / "medama_contact_sheet.png",
            animation_manifest_path=CASE_ROOT / "case_08_boss_kinematics" / "reports" / "medama_animation_manifest.json",
            case_manifest_path=CASE_ROOT / "case_08_boss_kinematics" / "medama_case_manifest.json",
            labels=["hover", "blink"],
            frame_count=4,
            target_cell_w=24,
            target_cell_h=24,
            min_area=16,
            row_tolerance=8,
            min_frames_per_row=2,
            width_range=(6, 28),
            height_range=(6, 28),
        ),
    ]

    manifests = [build_sprite_case(case) for case in cases]

    case_dir = CASE_ROOT / "case_08_boss_kinematics"
    ensure_dir(case_dir)
    case_manifest = {
        "case_id": "case_08_boss_kinematics",
        "scene_key": "scene_boss_kinematics_lab",
        "menu_slot": 8,
        "source_original": [
            str(cases[2].source_path),
            str(cases[3].source_path),
        ],
        "source_type": "sprite_sheet_plus_orbiters",
        "output_expected": [
            "central_character_sheet",
            "orbiter_sheet",
            "animation_manifests",
        ],
        "scripts_used": [
            "tools/image-tools/build_bvl_showcase_assets.py",
            "tools/image-tools/infer_source_structure.py",
            "tools/image-tools/export_source_structure.py",
            "tools/image-tools/analyze_source_semantics.py",
        ],
        "assets_generated_in_res": [
            str(cases[2].output_path.relative_to(PROJECT_ROOT)),
            str(cases[3].output_path.relative_to(PROJECT_ROOT)),
        ],
        "contracts": {
            "overlay_mode": "window_toggle_hidden",
            "boss_pivot_policy": "bottom_center",
            "orbiter_motion": "orbit_and_run",
        },
        "artifacts": manifests[2:],
    }
    (case_dir / "case_manifest.json").write_text(json.dumps(case_manifest, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dir(CASE_ROOT)
    build_sprite_cases()
    compose_forest_case()
    compose_desert_case()
    compose_hill_case()
    print("OK BENCHMARK_VISUAL_LAB showcase assets rebuilt.")


if __name__ == "__main__":
    main()
