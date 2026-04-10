#!/usr/bin/env python3
"""
Gera uma passada semanticamente decomposta do caso metal_slug_urban_sunset_scene.

Licao central:
- A = por do sol / atmosfera (BG_B)
- B = edificacoes / rua base (BG_A)
- C = destrocos frontais (massa frontal isolada)

Saidas:
- basic/layer_a_bg_b_basic.png
- basic/layer_b_bg_a_basic.png
- basic/layer_c_front_basic.png
- elite/layer_a_bg_b_elite.png
- elite/layer_b_bg_a_elite.png
- elite/layer_c_front_elite.png
- reports/translation_pass_02_semantic_layers.json
"""

from __future__ import annotations

import numpy as np
import sgdk_semantic_parser

# Type aliases for SGDK parity
u16 = np.uint16
u32 = np.uint32
import json
from collections import OrderedDict, deque
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageStat


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CANONICAL_CASE_ROOT = WORKSPACE_ROOT / "assets" / "reference" / "translation_curation" / "metal_slug_urban_sunset_scene"
ARCHIVE_CASE_ROOT = CANONICAL_CASE_ROOT / "-archive_old_não contaminar"


def resolve_case_root() -> Path:
    if (CANONICAL_CASE_ROOT / "truth" / "manual_authoritative_layers").is_dir():
        return CANONICAL_CASE_ROOT
    return ARCHIVE_CASE_ROOT


CASE_ROOT = resolve_case_root()
LIB_CASE_SOURCE_PATH = (
    WORKSPACE_ROOT
    / "tools"
    / "sgdk_wrapper"
    / ".agent"
    / "lib_case"
    / "art-translation"
    / "case_editorial_board"
    / "source.png"
)
SOURCE_PATH = LIB_CASE_SOURCE_PATH if LIB_CASE_SOURCE_PATH.is_file() else CASE_ROOT / "source" / "source.png"
MANUAL_TRUTH_ROOT = CASE_ROOT / "truth" / "manual_authoritative_layers"
MANUAL_BG_A_PATH = MANUAL_TRUTH_ROOT / "BG-A (Plano principal).png"
MANUAL_BG_B_PATH = MANUAL_TRUTH_ROOT / "BG-B (Plano de fundo).png"
MANUAL_FG_PATH = MANUAL_TRUTH_ROOT / "COMPISIÇÃO DO PLANO PRINCIPAL.png"
MANUAL_COMPOSITE_PATH = MANUAL_TRUTH_ROOT / "CENA MONTADA.png"
BASIC_DIR = CANONICAL_CASE_ROOT / "basic"
ELITE_DIR = CANONICAL_CASE_ROOT / "elite"
REPORTS_DIR = CANONICAL_CASE_ROOT / "reports"
PROJECT_RUNTIME_GFX_DIR = WORKSPACE_ROOT / "SGDK_projects" / "METAL_SLUG_URBAN_SUNSET" / "res" / "gfx"
TARGET_SIZE = (320, 224)
RUNTIME_PANORAMA_SIZE = (584, 224)
RUNTIME_SIZE = RUNTIME_PANORAMA_SIZE
RUNTIME_VIEWPORT_SIZE = (320, 224)
RUNTIME_EXPORT_BOX = (0, 0, 584, 224)
RUNTIME_BG_B_EXPORT_BOX = (32, 0, 160, 224)
MD_LEVELS = [0, 34, 68, 102, 136, 170, 204, 238]

A_BOX = (4, 26, 516, 154)
B_BOX = (5, 172, 677, 428)
C_BOX = (12, 458, 684, 601)
PREVIEW_BOX = (717, 189, 1021, 413)
RUNTIME_SCENE_CROP = (8, 251, 684, 510)


def ensure_dirs() -> None:
    for directory in (BASIC_DIR, ELITE_DIR, REPORTS_DIR, PROJECT_RUNTIME_GFX_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def snap_channel(value: int) -> int:
    return min(MD_LEVELS, key=lambda level: abs(level - value))


def snap_palette_image(image: Image.Image, colors: int, dither: bool, return_indexed: bool = False) -> Image.Image:
    rgba_source = image.convert("RGBA")
    alpha = rgba_source.getchannel("A")
    dither_mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    has_transparency = alpha.getextrema()[0] < 255

    if has_transparency:
        opaque_bbox = alpha.getbbox()
        if opaque_bbox is None:
            paletted = Image.new("P", rgba_source.size, 0)
            paletted.putpalette([255, 0, 255] + ([0] * (256 * 3 - 3)))
            paletted.info["transparency"] = 0
            if return_indexed:
                return paletted
            transparent = paletted.convert("RGBA")
            transparent.putalpha(alpha)
            return transparent

        visible_budget = max(1, min(15, colors))
        rgb_source = Image.new("RGB", rgba_source.size, (0, 0, 0))
        rgb_source.paste(rgba_source.convert("RGB"), mask=alpha)
        palette_probe = rgb_source.crop(opaque_bbox).convert(
            "P",
            palette=Image.Palette.ADAPTIVE,
            colors=visible_budget,
            dither=dither_mode,
        )
        probe_palette = palette_probe.getpalette()
        visible_colors: list[tuple[int, int, int]] = []
        for index in sorted(set(palette_probe.tobytes())):
            base = index * 3
            snapped = (
                snap_channel(probe_palette[base + 0]),
                snap_channel(probe_palette[base + 1]),
                snap_channel(probe_palette[base + 2]),
            )
            if color_distance(snapped, (255, 0, 255)) < 24:
                continue
            if snapped not in visible_colors:
                visible_colors.append(snapped)
            if len(visible_colors) >= 15:
                break

        if not visible_colors:
            visible_colors.append((0, 0, 0))

        palette_values = [255, 0, 255]
        for rgb in visible_colors:
            palette_values.extend(rgb)
        palette_values.extend([0] * (256 * 3 - len(palette_values)))

        palette_seed = Image.new("P", (1, 1), 0)
        palette_seed.putpalette(palette_values)
        paletted = rgb_source.quantize(palette=palette_seed, dither=dither_mode)
        paletted.putpalette(palette_values)

        pixel_data = bytearray(paletted.tobytes())
        alpha_data = alpha.tobytes()
        for i in range(len(pixel_data)):
            if alpha_data[i] < 128:
                pixel_data[i] = 0
        paletted.frombytes(bytes(pixel_data))
        paletted.info["transparency"] = 0
    else:
        rgb_source = rgba_source.convert("RGB")
        paletted = rgb_source.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors, dither=dither_mode)
        palette = paletted.getpalette()

        used_indices = sorted(set(paletted.tobytes()))
        for index in used_indices:
            base = index * 3
            palette[base + 0] = snap_channel(palette[base + 0])
            palette[base + 1] = snap_channel(palette[base + 1])
            palette[base + 2] = snap_channel(palette[base + 2])

        paletted.putpalette(palette)

    if return_indexed:
        return paletted
    quantized = paletted.convert("RGBA")
    quantized.putalpha(alpha)
    return quantized


def save_png(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    save_kwargs: dict[str, Any] = {}
    if image.mode == "P" and "transparency" in image.info:
        save_kwargs["transparency"] = image.info["transparency"]
    image.save(destination, **save_kwargs)


def remap_to_fixed_palette(image: Image.Image, palette: list[tuple[int, int, int, int]]) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    snapped = [tuple(snap_channel(channel) for channel in color[:3]) + (color[3],) for color in palette]
    visible_palette = [color for color in snapped if color[3] > 0]

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            best = min(
                visible_palette,
                key=lambda color: ((r - color[0]) ** 2) + ((g - color[1]) ** 2) + ((b - color[2]) ** 2),
            )
            pixels[x, y] = best
    return rgba


def collect_palette(image: Image.Image) -> list[tuple[int, int, int, int]]:
    ordered: OrderedDict[tuple[int, int, int, int], None] = OrderedDict()
    rgba = image.convert("RGBA")
    raw = rgba.tobytes()
    for index in range(0, len(raw), 4):
        pixel = (raw[index], raw[index + 1], raw[index + 2], raw[index + 3])
        if pixel not in ordered:
            ordered[pixel] = None
    return list(ordered.keys())


def save_palette_strip(image: Image.Image, destination: Path, swatch_size: int = 16) -> Path:
    colors = collect_palette(image)
    strip = Image.new("RGBA", (max(1, len(colors)) * swatch_size, swatch_size), (0, 0, 0, 0))
    for index, color in enumerate(colors):
        swatch = Image.new("RGBA", (swatch_size, swatch_size), color)
        strip.alpha_composite(swatch, (index * swatch_size, 0))
    destination.parent.mkdir(parents=True, exist_ok=True)
    strip.save(destination)
    return destination


def tile_signature(tile: Image.Image) -> bytes:
    return tile.convert("RGBA").tobytes()


def tile_signature_flip(tile: Image.Image) -> bytes:
    return tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT).convert("RGBA").tobytes()


def collect_tile_structure_stats(image: Image.Image) -> dict[str, Any]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    total_tiles = 0
    exact_tiles: OrderedDict[bytes, None] = OrderedDict()
    hflip_tiles: OrderedDict[bytes, None] = OrderedDict()

    for top in range(0, height, 8):
        for left in range(0, width, 8):
            tile = rgba.crop((left, top, left + 8, top + 8))
            total_tiles += 1
            signature = tile_signature(tile)
            exact_tiles.setdefault(signature, None)
            flip_signature = tile_signature_flip(tile)
            canonical = signature if signature <= flip_signature else flip_signature
            hflip_tiles.setdefault(canonical, None)

    unique_exact_tiles = len(exact_tiles)
    unique_hflip_tiles = len(hflip_tiles)
    return {
        "total_tiles": total_tiles,
        "unique_exact_tiles": unique_exact_tiles,
        "unique_hflip_tiles": unique_hflip_tiles,
        "exact_reuse_ratio": round(1.0 - (unique_exact_tiles / max(1, total_tiles)), 4),
        "hflip_reuse_ratio": round(1.0 - (unique_hflip_tiles / max(1, total_tiles)), 4),
        "hflip_savings_tiles": max(0, unique_exact_tiles - unique_hflip_tiles),
    }


def build_tileset_sheet(image: Image.Image, destination: Path, palette_destination: Path | None = None) -> dict[str, Any]:
    rgba = image.convert("RGBA")
    unique_tiles: OrderedDict[bytes, Image.Image] = OrderedDict()
    width, height = rgba.size
    for top in range(0, height, 8):
        for left in range(0, width, 8):
            tile = rgba.crop((left, top, left + 8, top + 8))
            signature = tile_signature(tile)
            flip_signature = tile_signature_flip(tile)
            if signature in unique_tiles or flip_signature in unique_tiles:
                continue
            unique_tiles[signature] = tile

    tiles = list(unique_tiles.values())
    columns = 16
    rows = max(1, (len(tiles) + columns - 1) // columns)
    palette_h = 18 if palette_destination is not None else 0
    sheet = Image.new("RGBA", (columns * 8, rows * 8 + palette_h), (18, 24, 30, 255))

    if palette_destination is not None:
        palette_strip = save_palette_strip(rgba, palette_destination)
        with Image.open(palette_strip).convert("RGBA") as strip:
            scale = min(sheet.width / max(1, strip.width), palette_h / max(1, strip.height))
            scaled_width = max(1, round(strip.width * scale))
            scaled_height = max(1, round(strip.height * scale))
            scaled = strip.resize((scaled_width, scaled_height), Image.Resampling.NEAREST)
            left = max(0, (sheet.width - scaled.width) // 2)
            sheet.alpha_composite(scaled, (left, 0))

    offset_y = palette_h
    for index, tile in enumerate(tiles):
        x = (index % columns) * 8
        y = (index // columns) * 8 + offset_y
        sheet.alpha_composite(tile, (x, y))

    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination)
    result: dict[str, Any] = {
        "sheet_path": str(destination),
        "structure": collect_tile_structure_stats(rgba),
    }
    if palette_destination is not None:
        result["palette_path"] = str(palette_destination)
    return result


def crop_box(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    return image.crop(box).convert("RGBA")


def resize_to_target(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.convert("RGBA").resize(size, Image.Resampling.LANCZOS)


def fit_to_size(image: Image.Image, size: tuple[int, int], centering: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image.convert("RGBA"), size, method=Image.Resampling.LANCZOS, centering=centering)


def resize_to_width(image: Image.Image, width: int, height: int | None = None) -> Image.Image:
    src_w, src_h = image.size
    scale = width / max(1, src_w)
    target_h = height if height is not None else max(1, round(src_h * scale))
    return image.resize((width, target_h), Image.Resampling.LANCZOS)


def palette_index_zero_to_alpha(image: Image.Image) -> Image.Image:
    source = image.copy()
    rgba = source.convert("RGBA")
    if source.mode != "P":
        return rgba

    indices = source.load()
    pixels = rgba.load()
    width, height = source.size
    for y in range(height):
        for x in range(width):
            if indices[x, y] == 0:
                r, g, b, _ = pixels[x, y]
                pixels[x, y] = (r, g, b, 0)
    return rgba


def crop_resize_runtime(image: Image.Image) -> Image.Image:
    return image.crop(RUNTIME_SCENE_CROP).resize(RUNTIME_PANORAMA_SIZE, Image.Resampling.LANCZOS)


def crop_runtime_export(image: Image.Image) -> Image.Image:
    return image.crop(RUNTIME_EXPORT_BOX)


def crop_runtime_bg_b_export(image: Image.Image) -> Image.Image:
    return image.crop(RUNTIME_BG_B_EXPORT_BOX)


def build_authoritative_runtime_layers() -> dict[str, Image.Image]:
    if not (MANUAL_BG_A_PATH.is_file() and MANUAL_BG_B_PATH.is_file() and MANUAL_FG_PATH.is_file()):
        raise FileNotFoundError("Camadas manuais autoritativas ausentes para o runtime do metal_slug.")

    panorama_bg_b = crop_resize_runtime(Image.open(MANUAL_BG_B_PATH).convert("RGBA"))
    panorama_bg_a = crop_resize_runtime(palette_index_zero_to_alpha(Image.open(MANUAL_BG_A_PATH)))
    panorama_fg = crop_resize_runtime(palette_index_zero_to_alpha(Image.open(MANUAL_FG_PATH)))
    panorama_bg_a_with_fg = Image.alpha_composite(panorama_bg_a, panorama_fg)
    panorama_composite = Image.alpha_composite(Image.alpha_composite(panorama_bg_b, panorama_bg_a), panorama_fg)

    return {
        "panorama_bg_b_rgba": panorama_bg_b,
        "panorama_bg_a_rgba": panorama_bg_a,
        "panorama_fg_rgba": panorama_fg,
        "panorama_bg_a_with_fg_rgba": panorama_bg_a_with_fg,
        "panorama_composite_rgba": panorama_composite,
        "bg_b_rgba": crop_runtime_bg_b_export(panorama_bg_b),
        "bg_a_rgba": crop_runtime_export(panorama_bg_a),
        "fg_rgba": crop_runtime_export(panorama_fg),
        "bg_a_with_fg_rgba": crop_runtime_export(panorama_bg_a_with_fg),
        "composite_rgba": crop_runtime_export(panorama_composite),
    }


def vertical_gradient_mask(size: tuple[int, int], start: float, end: float, power: float = 1.0) -> Image.Image:
    width, height = size
    mask = Image.new("L", size)
    pixels = mask.load()
    span = max(1, height - 1)
    for y in range(height):
        t = y / span
        value = start + ((end - start) * (t ** power))
        shade = max(0, min(255, round(value * 255)))
        for x in range(width):
            pixels[x, y] = shade
    return mask


def checker_alpha_mask(size: tuple[int, int], a: int, b: int, step: int = 2) -> Image.Image:
    width, height = size
    mask = Image.new("L", size)
    pixels = mask.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = a if (((x // step) + (y // step)) & 1) == 0 else b
    return mask


def apply_overlay(image: Image.Image, color: tuple[int, int, int], mask: Image.Image) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (*color, 0))
    overlay.putalpha(mask)
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def multiply_masks(a: Image.Image, b: Image.Image) -> Image.Image:
    return ImageChops.multiply(a, b)


def union_masks(a: Image.Image, b: Image.Image) -> Image.Image:
    return ImageChops.lighter(a, b)


def subtract_masks(a: Image.Image, b: Image.Image) -> Image.Image:
    return ImageChops.subtract(a, b)


def invert_mask(mask: Image.Image) -> Image.Image:
    return ImageOps.invert(mask.convert("L"))


def alpha_from_near_white(image: Image.Image, threshold: int = 244) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a and r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (r, g, b, 0)
    return rgba


def paste(canvas: Image.Image, layer: Image.Image, x: int, y: int) -> Image.Image:
    result = canvas.copy()
    result.alpha_composite(layer, (x, y))
    return result


def flatten_visible_rgb(image: Image.Image, fill: tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (*fill, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def average_rgb(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    crop = image.crop(box).convert("RGB")
    stat = ImageStat.Stat(crop)
    return tuple(round(value) for value in stat.mean[:3])


def dominant_rgb(image: Image.Image, box: tuple[int, int, int, int], colors: int = 6) -> tuple[int, int, int]:
    crop = image.crop(box).convert("RGBA")
    paletted = crop.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors, dither=Image.Dither.NONE)
    histogram = paletted.histogram()
    palette = paletted.getpalette()
    best_index = max(range(256), key=lambda index: histogram[index])
    base = best_index * 3
    return (
        snap_channel(palette[base + 0]),
        snap_channel(palette[base + 1]),
        snap_channel(palette[base + 2]),
    )


def smooth_mask(mask: Image.Image, expand: int = 3, contract: int = 3, blur_radius: float = 0.8) -> Image.Image:
    result = mask.convert("L")
    if expand > 1:
        result = result.filter(ImageFilter.MaxFilter(expand))
    if contract > 1:
        result = result.filter(ImageFilter.MinFilter(contract))
    if blur_radius > 0:
        result = result.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return result.point(lambda value: 255 if value >= 128 else 0, mode="L")


def build_vertical_fill_mask(size: tuple[int, int], starts: list[int], feather: int = 1) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    pixels = mask.load()
    for x, start_y in enumerate(starts):
        fill_from = max(0, min(height, start_y - feather))
        for y in range(fill_from, height):
            pixels[x, y] = 255
    return mask


def smooth_profile(values: list[int], radius: int) -> list[int]:
    smoothed: list[int] = []
    for index in range(len(values)):
        left = max(0, index - radius)
        right = min(len(values), index + radius + 1)
        neighborhood = values[left:right]
        smoothed.append(round(sum(neighborhood) / max(1, len(neighborhood))))
    return smoothed


def compose_semantic_scene(layer_a: Image.Image, layer_b: Image.Image, layer_c: Image.Image) -> Image.Image:
    composed = layer_a.convert("RGBA")
    composed = Image.alpha_composite(composed, layer_b.convert("RGBA"))
    composed = Image.alpha_composite(composed, layer_c.convert("RGBA"))
    return composed


def build_layer_a_source(source: Image.Image) -> Image.Image:
    return sgdk_semantic_parser.extract_region(source, A_BOX).resize(TARGET_SIZE, Image.Resampling.LANCZOS)
def build_layer_b_source(source: Image.Image) -> Image.Image:
    # Scale to canvas keeping it anchored appropriately or just squashing to target size
    return sgdk_semantic_parser.extract_region(source, B_BOX).resize(TARGET_SIZE, Image.Resampling.LANCZOS)
def build_layer_c_source(source: Image.Image) -> Image.Image:
    img = sgdk_semantic_parser.extract_region(source, C_BOX)
    # We want to put C at the bottom of TARGET_SIZE, just like in original scale
    # But since TARGET_SIZE is generic, we just resize directly as before, but from C_BOX
    img = img.resize((TARGET_SIZE[0], int(TARGET_SIZE[1] * (img.height / TARGET_SIZE[1]))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(img, (0, TARGET_SIZE[1] - img.height))
    return canvas
def luminance_rgb(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.2126 * r) + (0.7152 * g) + (0.0722 * b)


def saturation_rgb(rgb: tuple[int, int, int]) -> int:
    return max(rgb) - min(rgb)


def top_connected_mask(seed_mask: Image.Image, opaque_mask: Image.Image, seed_rows: int = 6) -> Image.Image:
    seed = seed_mask.convert("L")
    solid = opaque_mask.convert("L")
    width, height = seed.size
    result = Image.new("L", seed.size, 0)
    seed_px = seed.load()
    solid_px = solid.load()
    result_px = result.load()
    queue: deque[tuple[int, int]] = deque()

    for y in range(min(seed_rows, height)):
        for x in range(width):
            if solid_px[x, y] > 0 and seed_px[x, y] > 0 and result_px[x, y] == 0:
                result_px[x, y] = 255
                queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx = x + dx
            ny = y + dy
            if nx < 0 or ny < 0 or nx >= width or ny >= height:
                continue
            if result_px[nx, ny] > 0:
                continue
            if solid_px[nx, ny] == 0 or seed_px[nx, ny] == 0:
                continue
            result_px[nx, ny] = 255
            queue.append((nx, ny))

    return result


def build_architecture_alpha(image: Image.Image) -> Image.Image:
    return sgdk_semantic_parser.mask_from_isolated_region(image)
def apply_alpha_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA").copy()
    rgba.putalpha(mask)
    return rgba


def visible_alpha_mask(image: Image.Image) -> Image.Image:
    return image.convert("RGBA").getchannel("A").point(lambda value: 255 if value else 0, mode="L")


def build_debris_alpha(image: Image.Image) -> Image.Image:
    return sgdk_semantic_parser.mask_from_isolated_region(image)
def basic_layer_a_rgba(source: Image.Image) -> Image.Image:
    sky = build_layer_a_source(source)
    sky = ImageEnhance.Color(sky).enhance(0.9)
    sky = ImageEnhance.Contrast(sky).enhance(0.9)
    return sky
def basic_layer_b_rgba(source: Image.Image) -> Image.Image:
    city = build_layer_b_source(source)
    city_mask = sgdk_semantic_parser.mask_from_isolated_region(city)
    city = apply_alpha_mask(city, city_mask)
    return city
def basic_layer_c_rgba(source: Image.Image) -> Image.Image:
    fg = build_layer_c_source(source)
    mask = sgdk_semantic_parser.mask_from_isolated_region(fg)
    bg = apply_alpha_mask(fg, mask)
    return bg
def elite_layer_a_rgba(source: Image.Image) -> Image.Image:
    sky = build_layer_a_source(source)
    sky = ImageEnhance.Color(sky).enhance(1.04)
    sky = ImageEnhance.Contrast(sky).enhance(1.1)
    sky = ImageEnhance.Brightness(sky).enhance(0.98)
    
    warm_horizon = vertical_gradient_mask(TARGET_SIZE, start=0.0, end=0.22, power=2.2)
    sky = apply_overlay(sky, (238, 136, 34), warm_horizon)
    return sky
def elite_layer_b_rgba(source: Image.Image) -> Image.Image:
    city = build_layer_b_source(source)
    city_mask = sgdk_semantic_parser.mask_from_isolated_region(city)
    city = apply_alpha_mask(city, city_mask)
    city = ImageEnhance.Color(city).enhance(0.8)
    city = ImageEnhance.Contrast(city).enhance(1.24)
    city = ImageEnhance.Brightness(city).enhance(0.9)
    return city
def elite_layer_c_rgba(source: Image.Image) -> Image.Image:
    fg = build_layer_c_source(source)
    mask = sgdk_semantic_parser.mask_from_isolated_region(fg)
    fg = apply_alpha_mask(fg, mask)
    fg = ImageEnhance.Color(fg).enhance(0.78)
    fg = ImageEnhance.Contrast(fg).enhance(1.2)
    return fg
def basic_layer_a(source: Image.Image) -> Image.Image:
    return snap_palette_image(basic_layer_a_rgba(source), colors=10, dither=False)


def basic_layer_b(source: Image.Image) -> Image.Image:
    return snap_palette_image(basic_layer_b_rgba(source), colors=10, dither=False)


def basic_layer_c(source: Image.Image) -> Image.Image:
    return snap_palette_image(basic_layer_c_rgba(source), colors=6, dither=False)


def elite_layer_a(source: Image.Image) -> Image.Image:
    return snap_palette_image(elite_layer_a_rgba(source), colors=10, dither=True)


def elite_layer_b(source: Image.Image) -> Image.Image:
    return snap_palette_image(elite_layer_b_rgba(source), colors=10, dither=False)


def elite_layer_c(source: Image.Image) -> Image.Image:
    return snap_palette_image(elite_layer_c_rgba(source), colors=8, dither=False)


def build_review_pack(image: Image.Image, stem: str) -> dict[str, Any]:
    return build_tileset_sheet(
        image,
        REPORTS_DIR / f"{stem}_tileset_sheet.png",
        palette_destination=REPORTS_DIR / f"{stem}_palette_strip.png",
    )


def main() -> int:
    ensure_dirs()
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(f"Source ausente: {SOURCE_PATH}")

    source = Image.open(SOURCE_PATH).convert("RGBA")

    basic_a_rgba = basic_layer_a_rgba(source)
    basic_b_rgba = basic_layer_b_rgba(source)
    basic_c_rgba = basic_layer_c_rgba(source)
    elite_a_rgba = elite_layer_a_rgba(source)
    elite_b_rgba = elite_layer_b_rgba(source)
    elite_c_rgba = elite_layer_c_rgba(source)
    basic_reference = compose_semantic_scene(basic_a_rgba, basic_b_rgba, basic_c_rgba)
    elite_reference = compose_semantic_scene(elite_a_rgba, elite_b_rgba, elite_c_rgba)

    basic_a = snap_palette_image(basic_a_rgba, colors=10, dither=False, return_indexed=True)
    basic_b = snap_palette_image(basic_b_rgba, colors=10, dither=False, return_indexed=True)
    basic_c = snap_palette_image(basic_c_rgba, colors=6, dither=False, return_indexed=True)
    elite_a = snap_palette_image(elite_a_rgba, colors=10, dither=True, return_indexed=True)
    elite_b = snap_palette_image(elite_b_rgba, colors=10, dither=False, return_indexed=True)
    elite_c = snap_palette_image(elite_c_rgba, colors=8, dither=False, return_indexed=True)
    authoritative_runtime = build_authoritative_runtime_layers()
    runtime_panorama_bg_b_rgba = authoritative_runtime["panorama_bg_b_rgba"]
    runtime_panorama_bg_a_layer_rgba = authoritative_runtime["panorama_bg_a_rgba"]
    runtime_panorama_fg_rgba = authoritative_runtime["panorama_fg_rgba"]
    runtime_panorama_composite_rgba = authoritative_runtime["panorama_composite_rgba"]
    runtime_bg_b_rgba = authoritative_runtime["bg_b_rgba"]
    runtime_bg_a_layer_rgba = authoritative_runtime["bg_a_rgba"]
    runtime_fg_rgba = authoritative_runtime["fg_rgba"]
    runtime_bg_a_rgba = authoritative_runtime["bg_a_rgba"]
    runtime_composite_rgba = authoritative_runtime["composite_rgba"]
    runtime_bg_b_fill = dominant_rgb(runtime_bg_b_rgba, (0, 0, runtime_bg_b_rgba.width, max(1, runtime_bg_b_rgba.height // 6)))
    runtime_bg_b_flat = flatten_visible_rgb(runtime_bg_b_rgba, fill=runtime_bg_b_fill).convert("RGBA")
    runtime_bg_b = snap_palette_image(runtime_bg_b_flat, colors=10, dither=True, return_indexed=True)
    runtime_bg_a = snap_palette_image(runtime_bg_a_rgba, colors=15, dither=False, return_indexed=True)
    runtime_fg = snap_palette_image(runtime_fg_rgba, colors=8, dither=False, return_indexed=True)

    basic_a_path = BASIC_DIR / "layer_a_bg_b_basic.png"
    basic_b_path = BASIC_DIR / "layer_b_bg_a_basic.png"
    basic_c_path = BASIC_DIR / "layer_c_front_basic.png"
    elite_a_path = ELITE_DIR / "layer_a_bg_b_elite.png"
    elite_b_path = ELITE_DIR / "layer_b_bg_a_elite.png"
    elite_c_path = ELITE_DIR / "layer_c_front_elite.png"
    runtime_bg_b_path = PROJECT_RUNTIME_GFX_DIR / "city_bg_b_elite.png"
    runtime_bg_a_path = PROJECT_RUNTIME_GFX_DIR / "city_bg_a_elite.png"
    runtime_bg_c_path = PROJECT_RUNTIME_GFX_DIR / "layer_c_front_elite.png"
    basic_reference_path = REPORTS_DIR / "basic_semantic_composite_rgba.png"
    elite_reference_path = REPORTS_DIR / "elite_semantic_composite_rgba.png"
    runtime_composite_path = REPORTS_DIR / "runtime_panorama_composite_rgba.png"
    runtime_scene_composite_path = REPORTS_DIR / "runtime_scene_composite_rgba.png"

    save_png(basic_a, basic_a_path)
    save_png(basic_b, basic_b_path)
    save_png(basic_c, basic_c_path)
    save_png(elite_a, elite_a_path)
    save_png(elite_b, elite_b_path)
    save_png(elite_c, elite_c_path)
    save_png(runtime_bg_b, runtime_bg_b_path)
    save_png(runtime_bg_a, runtime_bg_a_path)
    save_png(runtime_fg, runtime_bg_c_path)
    basic_reference.save(basic_reference_path)
    elite_reference.save(elite_reference_path)
    runtime_panorama_composite_rgba.save(runtime_composite_path)
    runtime_composite_rgba.save(runtime_scene_composite_path)

    report = {
        "case_id": "metal_slug_urban_sunset_scene",
        "status": "generated_pass_07_runtime_semantic_panorama_map",
        "source_path": str(SOURCE_PATH),
        "target_size": list(TARGET_SIZE),
        "source_regions": {
            "A_bg_b_atmosphere": list(A_BOX),
            "B_bg_a_architecture": list(B_BOX),
            "C_foreground_debris": list(C_BOX),
            "preview_reference_only": list(PREVIEW_BOX),
        },
        "basic": {
            "assets": {
                "A": str(basic_a_path),
                "B": str(basic_b_path),
                "C": str(basic_c_path),
            },
            "rgba_reference_composite": str(basic_reference_path),
            "notes": [
                "Decompõe a fonte em A/B/C, mas mantém a leitura ainda próxima de uma conversão direta.",
                "A preserva o céu, B já respeita transparência estrutural, C mantém a massa frontal sem curadoria profunda de volume.",
                "A recomposição RGBA acontece antes da quantização final para manter alinhamento espacial entre as layers.",
            ],
            "review_pack": {
                "A": build_review_pack(basic_a, "metal_slug_basic_A"),
                "B": build_review_pack(basic_b, "metal_slug_basic_B"),
                "C": build_review_pack(basic_c, "metal_slug_basic_C"),
            },
        },
        "elite": {
            "assets": {
                "A": str(elite_a_path),
                "B": str(elite_b_path),
                "C": str(elite_c_path),
            },
            "rgba_reference_composite": str(elite_reference_path),
            "notes": [
                "A vira BG_B de atmosfera com gradiente preservado e palette ramp mais quente perto do horizonte.",
                "B vira layer estrutural com alpha real nas áreas de céu, sombras mais escuras e janelas quentes.",
                "C vira massa frontal recomposta por volume, preservando sombra e textura em vez de só borda ruidosa.",
                "A montagem de referencia acontece inteira em RGBA antes da quantização final por layer.",
            ],
            "review_pack": {
                "A": build_review_pack(elite_a, "metal_slug_elite_A"),
                "B": build_review_pack(elite_b, "metal_slug_elite_B"),
                "C": build_review_pack(elite_c, "metal_slug_elite_C"),
            },
            "params": {
                "A_palette_strategy": "manual_semantic_palette",
                "B_palette_strategy": "manual_semantic_palette",
                "C_palette_strategy": "manual_semantic_palette",
                "A_dither": True,
                "B_dither": False,
                "C_dither": False,
            },
            "runtime_assets": {
                "bg_b": str(runtime_bg_b_path),
                "bg_a": str(runtime_bg_a_path),
                "fg_c": str(runtime_bg_c_path),
            },
            "runtime_scene": {
                "authoritative_sources": {
                    "bg_b": str(MANUAL_BG_B_PATH),
                    "bg_a": str(MANUAL_BG_A_PATH),
                    "fg_c": str(MANUAL_FG_PATH),
                    "composite_truth": str(MANUAL_COMPOSITE_PATH),
                },
                "shared_crop": list(RUNTIME_SCENE_CROP),
                "panorama_size": list(RUNTIME_PANORAMA_SIZE),
                "runtime_export_box": list(RUNTIME_EXPORT_BOX),
                "runtime_size": list(RUNTIME_SIZE),
                "viewport_size": list(RUNTIME_VIEWPORT_SIZE),
                "rom_strategy": "bg_a_large_map_streamed_by_camera",
                "composite_rgba": str(runtime_composite_path),
                "runtime_scene_rgba": str(runtime_scene_composite_path),
                "bg_a_without_fg_rgba": str(REPORTS_DIR / "runtime_bg_a_base_rgba.png"),
                "foreground_policy": "staged_only_until_rom_budget_measurement",
            },
        },
    }

    runtime_bg_a_layer_path = REPORTS_DIR / "runtime_bg_a_base_rgba.png"
    runtime_bg_a_layer_rgba.save(runtime_bg_a_layer_path)
    runtime_panorama_bg_a_layer_path = REPORTS_DIR / "runtime_panorama_bg_a_base_rgba.png"
    runtime_panorama_bg_a_layer_rgba.save(runtime_panorama_bg_a_layer_path)
    runtime_panorama_fg_path = REPORTS_DIR / "runtime_panorama_fg_rgba.png"
    runtime_panorama_fg_rgba.save(runtime_panorama_fg_path)
    runtime_panorama_bg_b_path = REPORTS_DIR / "runtime_panorama_bg_b_rgba.png"
    runtime_panorama_bg_b_rgba.save(runtime_panorama_bg_b_path)

    report_path = REPORTS_DIR / "translation_pass_03_semantic_layers_refined.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"case_id": report["case_id"], "status": report["status"], "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
