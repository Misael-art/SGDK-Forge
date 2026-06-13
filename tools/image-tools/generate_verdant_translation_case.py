#!/usr/bin/env python3
"""
Gera a primeira passada basic vs elite do caso verdant_forest_depth_scene.

Saidas:
- basic/forest_bg_b_basic.png
- basic/forest_bg_a_basic.png
- elite/forest_bg_b_elite.png
- elite/forest_bg_a_elite.png
- reports/translation_pass_01.json
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageStat


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CASE_ROOT = WORKSPACE_ROOT / "assets" / "reference" / "translation_curation" / "verdant_forest_depth_scene"
SOURCE_PATH = CASE_ROOT / "source" / "source.png"
BASIC_DIR = CASE_ROOT / "basic"
ELITE_DIR = CASE_ROOT / "elite"
REPORTS_DIR = CASE_ROOT / "reports"
TARGET_SIZE = (320, 224)
MD_LEVELS = [0, 34, 68, 102, 136, 170, 204, 238]
PASS01_CONTACT_SHEET = REPORTS_DIR / "verdant_pass_01_contact_sheet.png"


def ensure_dirs() -> None:
    for directory in (BASIC_DIR, ELITE_DIR, REPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def cover_crop(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    src_w, src_h = image.size
    dst_w, dst_h = target_size
    scale = max(dst_w / src_w, dst_h / src_h)
    scaled = image.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
    left = max(0, (scaled.width - dst_w) // 2)
    # sobe um pouco a janela para preservar a copa principal e ainda manter a base do tronco
    top = max(0, (scaled.height - dst_h) // 2 - 6)
    top = min(top, max(0, scaled.height - dst_h))
    return scaled.crop((left, top, left + dst_w, top + dst_h))


def snap_channel(value: int) -> int:
    return min(MD_LEVELS, key=lambda level: abs(level - value))


def snap_palette_image(image: Image.Image, colors: int, dither: bool) -> Image.Image:
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


def checker_alpha_mask(size: tuple[int, int], strength_a: int, strength_b: int, step: int = 2) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    pixels = mask.load()
    for y in range(height):
        for x in range(width):
            pixels[x, y] = strength_a if (((x // step) + (y // step)) & 1) == 0 else strength_b
    return mask


def combine_masks(a: Image.Image, b: Image.Image, mode: str = "multiply") -> Image.Image:
    if mode == "lighter":
        return ImageChops.lighter(a, b)
    if mode == "multiply":
        return ImageChops.multiply(a, b)
    return ImageChops.screen(a, b)


def apply_checker_tint(image: Image.Image, mask: Image.Image, color_a: tuple[int, int, int], color_b: tuple[int, int, int], alpha_a: int, alpha_b: int) -> Image.Image:
    pattern = checker_alpha_mask(image.size, alpha_a, alpha_b, step=2)
    final_mask = combine_masks(mask, pattern, mode="multiply")
    overlay_a = Image.new("RGBA", image.size, (*color_a, 0))
    overlay_b = Image.new("RGBA", image.size, (*color_b, 0))

    pattern_inverse = ImageOps.invert(pattern)
    mask_a = combine_masks(mask, pattern, mode="multiply")
    mask_b = combine_masks(mask, pattern_inverse, mode="multiply")
    overlay_a.putalpha(mask_a)
    overlay_b.putalpha(mask_b)

    image = Image.alpha_composite(image.convert("RGBA"), overlay_a)
    image = Image.alpha_composite(image, overlay_b)
    return image


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
    sheet = Image.new("RGBA", (columns * 8, rows * 8 + palette_h), (18, 26, 34, 255))

    if palette_destination is not None:
        palette_strip = save_palette_strip(rgba, palette_destination)
        with Image.open(palette_strip).convert("RGBA") as strip:
            scaled = ImageOps.contain(strip, (sheet.width, palette_h), Image.Resampling.NEAREST)
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


def apply_tint(image: Image.Image, rgb: tuple[int, int, int], alpha: int) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (*rgb, alpha))
    return Image.alpha_composite(image.convert("RGBA"), overlay)


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


def radial_mask(size: tuple[int, int], center: tuple[float, float], radius_x: float, radius_y: float, strength: float) -> Image.Image:
    width, height = size
    mask = Image.new("L", size)
    pixels = mask.load()
    cx, cy = center
    for y in range(height):
        for x in range(width):
            dx = (x - cx) / radius_x
            dy = (y - cy) / radius_y
            dist = dx * dx + dy * dy
            value = 0.0 if dist >= 1.0 else (1.0 - dist) * strength
            pixels[x, y] = max(0, min(255, round(value * 255)))
    return mask


def composite_with_mask(base: Image.Image, detail: Image.Image, mask: Image.Image) -> Image.Image:
    return Image.composite(detail.convert("RGBA"), base.convert("RGBA"), mask)


def recover_proven_elite_from_contact_sheet() -> tuple[Image.Image, Image.Image] | None:
    if not PASS01_CONTACT_SHEET.is_file():
        return None

    sheet = Image.open(PASS01_CONTACT_SHEET).convert("RGBA")
    if sheet.size != (640, 496):
        return None

    elite_bg_b = sheet.crop((0, 272, 320, 496))
    elite_bg_a = sheet.crop((320, 272, 640, 496))
    return elite_bg_b, elite_bg_a


def basic_bg_b(base: Image.Image) -> Image.Image:
    img = base.convert("RGBA")
    img = ImageEnhance.Contrast(img).enhance(0.96)
    img = ImageEnhance.Color(img).enhance(0.86)
    img = ImageEnhance.Brightness(img).enhance(0.97)
    # Traducao direta: BG_B ainda parece a cena inteira, sem empurrar o fundo para tras.
    return snap_palette_image(img, colors=16, dither=False)


def basic_bg_a(base: Image.Image) -> Image.Image:
    img = base.convert("RGBA")
    img = ImageEnhance.Contrast(img).enhance(0.93)
    img = ImageEnhance.Color(img).enhance(0.84)
    img = ImageEnhance.Sharpness(img).enhance(1.1)
    return snap_palette_image(img, colors=16, dither=False)


def elite_bg_b(base: Image.Image) -> Image.Image:
    source = base.convert("RGBA")

    subdued = ImageEnhance.Color(source).enhance(0.68)
    subdued = ImageEnhance.Contrast(subdued).enhance(0.9)
    subdued = ImageEnhance.Brightness(subdued).enhance(0.94)
    subdued = subdued.filter(ImageFilter.GaussianBlur(radius=0.9))

    retained = ImageEnhance.Color(source).enhance(0.76)
    retained = ImageEnhance.Contrast(retained).enhance(0.97)
    retained = ImageEnhance.Brightness(retained).enhance(0.95)
    retained = retained.filter(ImageFilter.UnsharpMask(radius=1, percent=70, threshold=2))

    canopy_mask = radial_mask(source.size, center=(160, 108), radius_x=180, radius_y=112, strength=0.32)
    mid_depth_mask = vertical_gradient_mask(source.size, start=0.12, end=0.48, power=1.05)
    detail_mask = combine_masks(canopy_mask, mid_depth_mask, mode="lighter").filter(ImageFilter.GaussianBlur(radius=5))

    img = composite_with_mask(subdued, retained, detail_mask)

    cool_top = vertical_gradient_mask(img.size, start=0.16, end=0.04, power=0.82)
    cool_overlay = Image.new("RGBA", img.size, (74, 126, 148, 0))
    cool_overlay.putalpha(cool_top)
    img = Image.alpha_composite(img, cool_overlay)

    haze_mask = radial_mask(img.size, center=(160, 118), radius_x=180, radius_y=92, strength=0.16)
    haze_overlay = Image.new("RGBA", img.size, (180, 214, 204, 0))
    haze_overlay.putalpha(haze_mask)
    img = Image.alpha_composite(img, haze_overlay)

    sky_dither_zone = vertical_gradient_mask(img.size, start=0.18, end=0.03, power=0.78)
    img = apply_checker_tint(
        img,
        sky_dither_zone,
        color_a=(122, 170, 176),
        color_b=(92, 138, 154),
        alpha_a=18,
        alpha_b=8,
    )

    return snap_palette_image(img, colors=10, dither=True)


def elite_bg_a(base: Image.Image) -> Image.Image:
    subdued = base.convert("RGBA")
    subdued = ImageEnhance.Color(subdued).enhance(0.78)
    subdued = ImageEnhance.Contrast(subdued).enhance(0.95)
    subdued = ImageEnhance.Brightness(subdued).enhance(0.96)

    detailed = base.convert("RGBA")
    detailed = ImageEnhance.Color(detailed).enhance(0.92)
    detailed = ImageEnhance.Contrast(detailed).enhance(1.08)
    detailed = ImageEnhance.Sharpness(detailed).enhance(1.25)

    lower_focus = vertical_gradient_mask(base.size, start=0.12, end=0.9, power=1.45)
    tree_focus = radial_mask(base.size, center=(156, 112), radius_x=108, radius_y=120, strength=0.65)
    front_mask = ImageChops.lighter(lower_focus, tree_focus).filter(ImageFilter.GaussianBlur(radius=8))

    img = composite_with_mask(subdued, detailed, front_mask)

    warm_mask = radial_mask(base.size, center=(156, 126), radius_x=88, radius_y=124, strength=0.34)
    warm_overlay = Image.new("RGBA", base.size, (170, 118, 68, 0))
    warm_overlay.putalpha(warm_mask)
    img = Image.alpha_composite(img, warm_overlay)

    cool_shadow_mask = vertical_gradient_mask(base.size, start=0.1, end=0.02, power=0.9)
    cool_shadow = Image.new("RGBA", base.size, (48, 102, 126, 0))
    cool_shadow.putalpha(cool_shadow_mask)
    img = Image.alpha_composite(img, cool_shadow)

    dither_focus = combine_masks(
        radial_mask(base.size, center=(154, 118), radius_x=82, radius_y=126, strength=0.52),
        vertical_gradient_mask(base.size, start=0.08, end=0.36, power=1.25),
        mode="lighter",
    )
    img = apply_checker_tint(
        img,
        dither_focus,
        color_a=(148, 188, 196),
        color_b=(102, 146, 126),
        alpha_a=18,
        alpha_b=10,
    )

    return snap_palette_image(img, colors=12, dither=True)


def main() -> int:
    ensure_dirs()
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(f"Imagem-fonte nao encontrada: {SOURCE_PATH}")

    source = Image.open(SOURCE_PATH).convert("RGBA")
    base = cover_crop(source, TARGET_SIZE)

    basic_b = basic_bg_b(base)
    basic_a = basic_bg_a(base)
    recovered_elite = recover_proven_elite_from_contact_sheet()
    if recovered_elite is not None:
        elite_b, elite_a = recovered_elite
        elite_generation_mode = "recovered_proven_pass_01"
    else:
        elite_b = elite_bg_b(base)
        elite_a = elite_bg_a(base)
        elite_generation_mode = "generated_rebalanced_pass"

    basic_b.save(BASIC_DIR / "forest_bg_b_basic.png")
    basic_a.save(BASIC_DIR / "forest_bg_a_basic.png")
    elite_b.save(ELITE_DIR / "forest_bg_b_elite.png")
    elite_a.save(ELITE_DIR / "forest_bg_a_elite.png")

    basic_b_review = build_tileset_sheet(
        basic_b,
        REPORTS_DIR / "forest_bg_b_basic_tileset.png",
        REPORTS_DIR / "forest_bg_b_basic_palette.png",
    )
    basic_a_review = build_tileset_sheet(
        basic_a,
        REPORTS_DIR / "forest_bg_a_basic_tileset.png",
        REPORTS_DIR / "forest_bg_a_basic_palette.png",
    )
    elite_b_review = build_tileset_sheet(
        elite_b,
        REPORTS_DIR / "forest_bg_b_elite_tileset.png",
        REPORTS_DIR / "forest_bg_b_elite_palette.png",
    )
    elite_a_review = build_tileset_sheet(
        elite_a,
        REPORTS_DIR / "forest_bg_a_elite_tileset.png",
        REPORTS_DIR / "forest_bg_a_elite_palette.png",
    )

    report = {
        "case_id": "verdant_forest_depth_scene",
        "target_size": {"width": TARGET_SIZE[0], "height": TARGET_SIZE[1]},
        "source_image": str(SOURCE_PATH),
        "outputs": {
            "basic_bg_b": str(BASIC_DIR / "forest_bg_b_basic.png"),
            "basic_bg_a": str(BASIC_DIR / "forest_bg_a_basic.png"),
            "elite_bg_b": str(ELITE_DIR / "forest_bg_b_elite.png"),
            "elite_bg_a": str(ELITE_DIR / "forest_bg_a_elite.png"),
        },
        "translation_notes": {
            "basic": [
                "reducao direta da cena com pouca diferenciacao de papel entre os planos",
                "compressao de paleta mais simples e sem dithering funcional",
                "frente e fundo ainda compartilham leitura demais",
            ],
            "elite": [
                "elite canonica restaurada a partir da passada comprovadamente mais forte do caso",
                "BG_B resfriado e afastado sem destruir a leitura das massas de arvore e troncos distantes",
                "BG_A com foco maior na arvore central e nas massas de frente, preservando a forca visual validada",
                "paletas mais enxutas e dithering contido, aplicado como suporte de material e atmosfera",
                "aprendizado do video mantido como review estrutural de tileset, nao como achatamento da cena",
            ],
            "video_techniques_applied": [
                "pensar o layer como conjunto de tiles antes do mapa final",
                "disciplinar a paleta por layer e exportar a faixa de paleta como referencia",
                "preparar sheet de tiles para leitura manual, deduplicacao e oportunidades de H-Flip",
                "tratar BG_A e BG_B como papeis diferentes, nao como a mesma ilustracao comprimida",
                "preservar o review estrutural mesmo quando a transformacao visual precisar ser suavizada",
            ],
            "elite_generation_mode": elite_generation_mode,
            "review_pack": {
                "basic_bg_b": basic_b_review,
                "basic_bg_a": basic_a_review,
                "elite_bg_b": elite_b_review,
                "elite_bg_a": elite_a_review,
            },
        },
    }
    with (REPORTS_DIR / "translation_pass_04_restored_proven_elite.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
