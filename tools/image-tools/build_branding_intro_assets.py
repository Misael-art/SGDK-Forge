#!/usr/bin/env python3
"""Build deterministic SGDK-safe branding intro assets.

The source art may be AI-generated, but the shipped PNGs are composed here:
fixed text, fixed palettes, MD color snapping, indexed PNG output, and lineage.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "tools" / "sgdk_wrapper" / "modelo"
SOURCE_DIR = PROJECT / "data" / "source_art" / "branding_intro" / "production"
PROCESSED_DIR = PROJECT / "data" / "processed" / "branding_intro"
RES_DIR = PROJECT / "res" / "branding"
LOG_DIR = PROJECT / "out" / "logs"

TRANSPARENT = (238, 0, 238)

PROMPTS = {
    "engine": (
        "Original 16-bit console startup logo art, metallic forge engine emblem, "
        "anvil and gear fused into a heroic mark, cyan blue molten core, polished "
        "steel highlights, black negative space, hard pixel-art readable shapes, "
        "arcade quality, no text, no letters, no watermark, no licensed character, "
        "no real brand, clean isolated composition."
    ),
    "author": (
        "Original 16-bit tech noir signature panel, phosphor green and amber terminal "
        "geometry, thin HUD lines, elegant digital signature frame, black background, "
        "crisp pixel-art shapes, premium console intro mood, no text, no letters, "
        "no watermark, no real brand, no character."
    ),
    "project": (
        "Original 16-bit arcade publisher crest, crimson and gold seal, bold "
        "symmetrical emblem, dramatic black shadow, premium 1990s console "
        "presents-screen energy, strong silhouette, hard pixel-art edges, no text, "
        "no letters, no watermark, no licensed imagery."
    ),
}

NEGATIVE_PROMPT = (
    "text, letters, numbers, watermark, logo typo, real brand, licensed character, "
    "celebrity, realistic photo, 3d render, blurry, noisy, abstract, gradients"
)


FONT_5X7: dict[str, tuple[str, ...]] = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("10010", "10010", "10010", "11111", "00010", "00010", "00010"),
    "5": ("11111", "10000", "10000", "11110", "00001", "00001", "11110"),
    "6": ("01111", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "11110"),
    " ": ("000", "000", "000", "000", "000", "000", "000"),
}


PALETTES = {
    "engine": [
        TRANSPARENT,
        (0, 0, 0),
        (34, 34, 34),
        (68, 68, 68),
        (102, 102, 102),
        (136, 136, 136),
        (170, 170, 170),
        (204, 204, 204),
        (238, 238, 238),
        (0, 34, 68),
        (0, 68, 136),
        (0, 102, 170),
        (0, 170, 204),
        (34, 204, 238),
        (136, 238, 238),
        (238, 238, 204),
    ],
    "author": [
        TRANSPARENT,
        (0, 0, 0),
        (0, 34, 34),
        (0, 68, 34),
        (0, 102, 34),
        (0, 170, 68),
        (68, 238, 102),
        (170, 238, 170),
        (238, 238, 204),
        (68, 68, 68),
        (102, 102, 68),
        (136, 102, 0),
        (204, 136, 0),
        (238, 204, 68),
        (34, 102, 136),
        (0, 204, 170),
    ],
    "project": [
        TRANSPARENT,
        (0, 0, 0),
        (34, 0, 0),
        (68, 0, 0),
        (102, 0, 0),
        (136, 0, 0),
        (170, 34, 0),
        (204, 68, 0),
        (238, 102, 0),
        (238, 170, 0),
        (238, 204, 68),
        (238, 238, 170),
        (238, 238, 238),
        (102, 68, 34),
        (68, 68, 68),
        (136, 136, 102),
    ],
    "fx": [
        (0, 0, 0),
        (34, 34, 34),
        (68, 68, 68),
        (0, 34, 68),
        (0, 68, 136),
        (0, 102, 170),
        (0, 170, 204),
        (34, 204, 238),
        (0, 68, 34),
        (0, 170, 68),
        (204, 136, 0),
        (238, 204, 68),
        (68, 0, 0),
        (136, 0, 0),
        (204, 68, 0),
        (238, 238, 238),
    ],
}


@dataclass(frozen=True)
class BuiltAsset:
    name: str
    file: Path
    size: tuple[int, int]
    palette_entries: int
    used_indexes: int
    transparent_index_0: bool
    sha256: str


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def snap_channel(value: int) -> int:
    return max(0, min(238, int(round(value / 34.0)) * 34))


def snap_rgb(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(snap_channel(v) for v in rgb)


def nearest_color_index(
    rgb: tuple[int, int, int],
    palette: list[tuple[int, int, int]],
    first: int,
) -> int:
    best_index = first
    best_dist = 1 << 62
    for idx in range(first, len(palette)):
        pr, pg, pb = palette[idx]
        dr = rgb[0] - pr
        dg = rgb[1] - pg
        db = rgb[2] - pb
        dist = (dr * dr) + (dg * dg) + (db * db)
        if dist < best_dist:
            best_dist = dist
            best_index = idx
    return best_index


def save_indexed(
    rgba: Image.Image,
    path: Path,
    palette_name: str,
    transparent: bool,
) -> BuiltAsset:
    palette = [snap_rgb(color) for color in PALETTES[palette_name]]
    out = Image.new("P", rgba.size)
    pixels: list[int] = []

    first_visible = 1 if transparent else 0
    for r, g, b, a in rgba.convert("RGBA").getdata():
        if transparent and a < 16:
            pixels.append(0)
        else:
            pixels.append(nearest_color_index(snap_rgb((r, g, b)), palette, first_visible))

    out.putdata(pixels)
    flat: list[int] = []
    for color in palette:
        flat.extend(color)
    out.putpalette(flat)
    if transparent:
        out.info["transparency"] = 0
    else:
        out.info.pop("transparency", None)

    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path, format="PNG", optimize=False)

    with Image.open(path) as saved:
        palette_entries = len(saved.getpalette() or []) // 3
        used_indexes = len(set(saved.getdata()))
        transparent0 = int(saved.info.get("transparency", -1)) == 0

    return BuiltAsset(
        name=path.name,
        file=path,
        size=rgba.size,
        palette_entries=palette_entries,
        used_indexes=used_indexes,
        transparent_index_0=transparent0,
        sha256=sha256(path),
    )


def draw_pixel_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    scale: int,
    fill: tuple[int, int, int, int],
    shadow: tuple[int, int, int, int] | None = None,
) -> None:
    x0, y0 = xy
    cursor = x0
    for char in text.upper():
        glyph = FONT_5X7.get(char, FONT_5X7[" "])
        glyph_width = len(glyph[0])
        if shadow is not None:
            for yy, row in enumerate(glyph):
                for xx, bit in enumerate(row):
                    if bit == "1":
                        draw.rectangle(
                            (
                                cursor + (xx * scale) + scale,
                                y0 + (yy * scale) + scale,
                                cursor + ((xx + 1) * scale) - 1 + scale,
                                y0 + ((yy + 1) * scale) - 1 + scale,
                            ),
                            fill=shadow,
                        )
        for yy, row in enumerate(glyph):
            for xx, bit in enumerate(row):
                if bit == "1":
                    draw.rectangle(
                        (
                            cursor + (xx * scale),
                            y0 + (yy * scale),
                            cursor + ((xx + 1) * scale) - 1,
                            y0 + ((yy + 1) * scale) - 1,
                        ),
                        fill=fill,
                    )
        cursor += (glyph_width + 1) * scale


def text_size(text: str, scale: int) -> tuple[int, int]:
    width = 0
    for char in text.upper():
        glyph = FONT_5X7.get(char, FONT_5X7[" "])
        width += (len(glyph[0]) + 1) * scale
    if width:
        width -= scale
    return width, 7 * scale


def centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    width: int,
    scale: int,
    fill: tuple[int, int, int, int],
    shadow: tuple[int, int, int, int],
) -> None:
    tw, _ = text_size(text, scale)
    draw_pixel_text(draw, text, ((width - tw) // 2, y), scale, fill, shadow)


def subject_from_source(path: Path, size: tuple[int, int], threshold: int) -> Image.Image:
    src = Image.open(path).convert("RGBA")
    src = ImageOps.contain(src, size, Image.Resampling.LANCZOS)
    rgba = Image.new("RGBA", size, (0, 0, 0, 0))
    rgba.alpha_composite(src, ((size[0] - src.width) // 2, (size[1] - src.height) // 2))

    data = []
    for r, g, b, a in rgba.getdata():
        mx = max(r, g, b)
        mn = min(r, g, b)
        keep = (mx >= threshold) or ((mx - mn) >= 24 and mx >= 28)
        data.append((r, g, b, a if keep else 0))
    cut = Image.new("RGBA", size)
    cut.putdata(data)
    return cut.filter(ImageFilter.ModeFilter(size=3))


def draw_frame(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    dark: tuple[int, int, int, int],
    mid: tuple[int, int, int, int],
    hi: tuple[int, int, int, int],
) -> None:
    x0, y0, x1, y1 = rect
    draw.rectangle((x0, y0, x1, y1), fill=dark)
    draw.rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), outline=mid, width=2)
    draw.line((x0 + 5, y0 + 5, x1 - 5, y0 + 5), fill=hi, width=1)
    draw.line((x0 + 5, y1 - 5, x1 - 5, y1 - 5), fill=mid, width=1)


def build_engine() -> Image.Image:
    canvas = Image.new("RGBA", (224, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    mark = subject_from_source(SOURCE_DIR / "engine_mark_source.png", (72, 72), 34)
    canvas.alpha_composite(mark, (3, 4))
    draw_frame(
        draw,
        (64, 10, 219, 70),
        (0, 0, 0, 235),
        (68, 68, 68, 255),
        (204, 204, 204, 255),
    )
    draw.line((72, 61, 211, 61), fill=(34, 204, 238, 255), width=2)
    draw.line((75, 64, 180, 64), fill=(0, 102, 170, 255), width=1)
    centered_text(draw, "MEGA FORGE", 22, 284, 2, (238, 238, 238, 255), (0, 68, 136, 255))
    centered_text(draw, "ENGINE", 46, 284, 2, (136, 238, 238, 255), (0, 34, 68, 255))
    return canvas


def build_author() -> Image.Image:
    canvas = Image.new("RGBA", (224, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    panel = subject_from_source(SOURCE_DIR / "author_panel_source.png", (224, 64), 28)
    canvas.alpha_composite(panel, (0, 0))
    draw.rectangle((6, 6, 217, 57), outline=(0, 170, 68, 255), width=1)
    draw.rectangle((36, 15, 187, 55), fill=(0, 0, 0, 255))
    draw.line((12, 14, 68, 14), fill=(238, 204, 68, 255), width=1)
    draw.line((156, 50, 211, 50), fill=(0, 204, 170, 255), width=1)
    draw.line((20, 54, 74, 54), fill=(0, 102, 34, 255), width=1)
    centered_text(draw, "MISAEL", 17, 224, 2, (170, 238, 170, 255), (0, 68, 34, 255))
    centered_text(draw, "OLIVEIRA", 37, 224, 2, (238, 204, 68, 255), (68, 34, 0, 255))
    return canvas


def build_project() -> Image.Image:
    canvas = Image.new("RGBA", (240, 88), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw_frame(
        draw,
        (10, 8, 229, 79),
        (0, 0, 0, 228),
        (136, 0, 0, 255),
        (238, 204, 68, 255),
    )
    crest = subject_from_source(SOURCE_DIR / "project_crest_source.png", (86, 86), 30)
    canvas.alpha_composite(crest, (77, 1))
    draw.rectangle((42, 17, 198, 59), fill=(0, 0, 0, 255))
    draw.rectangle((18, 16, 221, 71), outline=(238, 170, 0, 255), width=1)
    draw.line((34, 62, 206, 62), fill=(238, 204, 68, 255), width=1)
    centered_text(draw, "MEGA MASTER", 21, 240, 2, (238, 238, 170, 255), (102, 0, 0, 255))
    centered_text(draw, "GAMES", 45, 240, 2, (238, 204, 68, 255), (34, 0, 0, 255))
    return canvas


def build_presents() -> Image.Image:
    canvas = Image.new("RGBA", (112, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    centered_text(draw, "PRESENTS", 5, 112, 2, (238, 238, 170, 255), (102, 0, 0, 255))
    draw.line((12, 22, 99, 22), fill=(238, 170, 0, 255), width=1)
    return canvas


def build_fx_tiles() -> Image.Image:
    canvas = Image.new("RGBA", (128, 32), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(0, 32, 8):
        for x in range(0, 128, 8):
            band = ((x // 8) + (y // 8)) & 3
            if band == 0:
                color = (0, 34, 68, 255)
            elif band == 1:
                color = (34, 34, 34, 255)
            elif band == 2:
                color = (68, 0, 0, 255)
            else:
                color = (0, 68, 34, 255)
            draw.rectangle((x, y, x + 7, y + 7), fill=color)

    for x in range(0, 128, 16):
        draw.line((x, 0, x + 7, 31), fill=(0, 170, 204, 255), width=1)
    for x in range(8, 128, 24):
        draw.line((x, 31, x + 14, 5), fill=(238, 204, 68, 255), width=1)
    for y in (7, 15, 23):
        draw.line((0, y, 127, y), fill=(68, 68, 68, 255), width=1)
    for x in range(4, 128, 29):
        draw.rectangle((x, 13, x + 3, 16), fill=(238, 238, 238, 255))
    return canvas


def validate_dimensions(asset: BuiltAsset, transparent_expected: bool) -> list[str]:
    errors: list[str] = []
    w, h = asset.size
    if w % 8 != 0 or h % 8 != 0:
        errors.append(f"{asset.name}: dimensions not multiple of 8")
    if asset.palette_entries > 16:
        errors.append(f"{asset.name}: PLTE has {asset.palette_entries} entries")
    if asset.used_indexes > 16:
        errors.append(f"{asset.name}: uses {asset.used_indexes} indexes")
    if transparent_expected and not asset.transparent_index_0:
        errors.append(f"{asset.name}: index 0 is not transparent")
    return errors


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def write_preview(files: Iterable[Path]) -> Path:
    preview = Image.new("RGBA", (320, 288), (0, 0, 0, 255))
    y = 12
    for path in files:
        img = Image.open(path).convert("RGBA")
        preview.alpha_composite(img, ((320 - img.width) // 2, y))
        y += img.height + 8
    out = PROJECT / "out" / "branding_intro_preview.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    preview.save(out)
    return out


def main() -> int:
    for directory in (PROCESSED_DIR, RES_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    sources = {
        "engine": SOURCE_DIR / "engine_mark_source.png",
        "author": SOURCE_DIR / "author_panel_source.png",
        "project": SOURCE_DIR / "project_crest_source.png",
    }
    missing = [str(path) for path in sources.values() if not path.exists()]
    if missing:
        raise SystemExit("Missing source art: " + ", ".join(missing))

    recipes = [
        ("brand_engine_logo.png", "engine", build_engine(), True),
        ("brand_author_logo.png", "author", build_author(), True),
        ("brand_project_logo.png", "project", build_project(), True),
        ("brand_presents_text.png", "project", build_presents(), True),
        ("brand_fx_tiles.png", "fx", build_fx_tiles(), False),
    ]

    built: list[BuiltAsset] = []
    validation_errors: list[str] = []
    for filename, palette_name, image, transparent in recipes:
        processed_path = PROCESSED_DIR / filename
        res_path = RES_DIR / filename
        asset = save_indexed(image, processed_path, palette_name, transparent)
        asset = save_indexed(image, res_path, palette_name, transparent)
        built.append(asset)
        validation_errors.extend(validate_dimensions(asset, transparent))

    preview_path = write_preview([asset.file for asset in built])

    lineage = {
        "asset_set": "branding_intro",
        "profile": "native_image_gen_plus_deterministic_builder",
        "negative_prompt": NEGATIVE_PROMPT,
        "source_art": {
            name: {
                "path": relative(path),
                "sha256": sha256(path),
                "prompt": PROMPTS[name],
            }
            for name, path in sources.items()
        },
        "outputs": [
            {
                "name": asset.name,
                "path": relative(asset.file),
                "sha256": asset.sha256,
                "dimensions": list(asset.size),
                "palette_entries": asset.palette_entries,
                "used_indexes": asset.used_indexes,
                "transparent_index_0": asset.transparent_index_0,
            }
            for asset in built
        ],
        "preview_path": relative(preview_path),
        "aesthetic_decision": (
            "Use compact authored emblems with deterministic exact lettering. "
            "Generated source art supplies texture and silhouette; the builder "
            "keeps SGDK-safe palettes, tile-aligned dimensions, and readable text."
        ),
        "rejections": {
            "raw_ai_direct_to_res": "Rejected: text/PLTE/VDP budget cannot be trusted from raw generation.",
            "fullscreen_static_logo": "Rejected: too expensive and less cinematic than small assets plus VDP motion.",
            "tools_ai_imagegen_default": "Rejected for premium source path after prior unreadable output.",
        },
        "validation_errors": validation_errors,
    }

    report_path = LOG_DIR / "branding_intro_lineage.json"
    report_path.write_text(json.dumps(lineage, indent=2), encoding="utf-8")

    print(json.dumps(lineage, indent=2))
    if validation_errors:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
