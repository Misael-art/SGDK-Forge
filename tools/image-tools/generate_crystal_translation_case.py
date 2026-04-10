#!/usr/bin/env python3
"""
Gera a primeira passada basic vs elite do caso crystal_cavern_tilemap.

Saidas:
- basic/crystal_tilemap_basic.png
- elite/crystal_tilemap_elite.png
- reports/translation_pass_01.json
- palette strips e tileset sheets para review estrutural
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CASE_ROOT = WORKSPACE_ROOT / "assets" / "reference" / "translation_curation" / "crystal_cavern_tilemap"
SOURCE_PATH = CASE_ROOT / "source" / "source.png"
BASIC_DIR = CASE_ROOT / "basic"
ELITE_DIR = CASE_ROOT / "elite"
REPORTS_DIR = CASE_ROOT / "reports"
TARGET_SIZE = (320, 224)
MD_LEVELS = [0, 34, 68, 102, 136, 170, 204, 238]


def ensure_dirs() -> None:
    for directory in (BASIC_DIR, ELITE_DIR, REPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def cover_crop(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(
        image.convert("RGBA"),
        target_size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


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


def basic_tilemap(base: Image.Image) -> Image.Image:
    img = cover_crop(base, TARGET_SIZE)
    img = ImageEnhance.Color(img).enhance(0.9)
    img = ImageEnhance.Contrast(img).enhance(0.98)
    return snap_palette_image(img, colors=16, dither=False)


def elite_tilemap(base: Image.Image) -> Image.Image:
    img = cover_crop(base, TARGET_SIZE)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = ImageEnhance.Color(img).enhance(0.82)
    img = ImageEnhance.Brightness(img).enhance(0.98)
    img = ImageEnhance.Sharpness(img).enhance(1.4)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=80, threshold=2))
    return snap_palette_image(img, colors=8, dither=False)


def main() -> int:
    ensure_dirs()
    if not SOURCE_PATH.is_file():
        raise FileNotFoundError(f"Source ausente: {SOURCE_PATH}")

    source = Image.open(SOURCE_PATH).convert("RGBA")
    basic = basic_tilemap(source)
    elite = elite_tilemap(source)

    basic_path = BASIC_DIR / "crystal_tilemap_basic.png"
    elite_path = ELITE_DIR / "crystal_tilemap_elite.png"
    basic.save(basic_path)
    elite.save(elite_path)

    basic_pack = build_tileset_sheet(
        basic,
        REPORTS_DIR / "crystal_basic_tileset_sheet.png",
        palette_destination=REPORTS_DIR / "crystal_basic_palette_strip.png",
    )
    elite_pack = build_tileset_sheet(
        elite,
        REPORTS_DIR / "crystal_elite_tileset_sheet.png",
        palette_destination=REPORTS_DIR / "crystal_elite_palette_strip.png",
    )

    report = {
        "case_id": "crystal_cavern_tilemap",
        "status": "generated_pass_01",
        "source_path": str(SOURCE_PATH),
        "target_size": list(TARGET_SIZE),
        "basic": {
            "asset_path": str(basic_path),
            "notes": [
                "Controle de traducao direta com quantizacao simples em 16 cores.",
                "Mantem o brilho geral, mas ainda trata o set como imagem mais do que como recurso de hardware.",
            ],
            "review_pack": basic_pack,
        },
        "elite": {
            "asset_path": str(elite_path),
            "notes": [
                "Reforca contraste estrutural entre rocha e cristal.",
                "Consolida a paleta para um set mais crivel de Mega Drive.",
                "Mantem a modularidade do tilemap sem virar ruido cromatico.",
            ],
            "review_pack": elite_pack,
            "params": {
                "contrast": 1.15,
                "color": 0.82,
                "brightness": 0.98,
                "sharpness": 1.4,
                "colors": 8,
                "dither": False,
            },
        },
    }

    report_path = REPORTS_DIR / "translation_pass_01.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"case_id": report["case_id"], "status": report["status"], "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
