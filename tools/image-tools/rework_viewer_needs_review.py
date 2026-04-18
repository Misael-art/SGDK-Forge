#!/usr/bin/env python3
"""Canonical aesthetic rework for METAL_SLUG_URBAN_SUNSET viewer variants.

This script upgrades the remaining `needs_review` viewer assets with
deterministic, Mega-Drive-aware transforms:

- BG_B backdrops become banded atmospheric gradients with controlled boundary dithering
- MISSION 1 flat studies get palette consolidation plus light ordered dithering
- MISSION 1 skylift default gets modal smoothing plus palette consolidation
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter


BAYER_4X4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.2126 * r) + (0.7152 * g) + (0.0722 * b)


def get_used_palette(image: Image.Image) -> list[tuple[int, int, int]]:
    if image.mode != "P":
        image = image.convert("P")
    palette = image.getpalette() or []
    used = sorted(image.getcolors(maxcolors=1_000_000) or [], reverse=True)
    colors: list[tuple[int, int, int]] = []
    for _, index in used:
        rgb = tuple(palette[index * 3 : index * 3 + 3])
        if rgb not in colors:
            colors.append(rgb)
    return colors


def build_luma_spaced_palette(source: Image.Image, count: int, min_gap: float = 10.0) -> list[tuple[int, int, int]]:
    ranked = sorted(get_used_palette(source), key=luminance)
    if not ranked:
        return [(0, 0, 0)]

    selected: list[tuple[int, int, int]] = [ranked[0]]
    for color in ranked[1:]:
        if len(selected) >= count:
            break
        if min(abs(luminance(color) - luminance(existing)) for existing in selected) >= min_gap:
            selected.append(color)

    for color in ranked:
        if len(selected) >= count:
            break
        if color not in selected:
            selected.append(color)

    selected = sorted(selected, key=luminance)
    while len(selected) < count:
        if len(selected) == 1:
            selected.append(selected[0])
        else:
            darkest = selected[0]
            brightest = selected[-1]
            mix_ratio = len(selected) / max(1, count - 1)
            mixed = tuple(
                int(round((darkest[i] * (1.0 - mix_ratio)) + (brightest[i] * mix_ratio)))
                for i in range(3)
            )
            selected.insert(-1, mixed)
        selected = sorted(selected, key=luminance)

    return selected[:count]


def make_indexed_image(size: tuple[int, int], palette: list[tuple[int, int, int]]) -> Image.Image:
    image = Image.new("P", size)
    flat_palette: list[int] = []
    for color in palette:
        flat_palette.extend(color)
    flat_palette.extend([0] * (768 - len(flat_palette)))
    image.putpalette(flat_palette)
    return image


def build_transition_bands(size: tuple[int, int], palette: list[tuple[int, int, int]]) -> Image.Image:
    width, height = size
    image = make_indexed_image(size, palette)
    segment_height = height / max(1, len(palette))
    transition_height = max(6, int(segment_height * 0.25))
    pixels: list[int] = []

    for y in range(height):
        band = min(len(palette) - 1, int(y / segment_height))
        local_y = y - int(band * segment_height)
        if band > 0 and local_y < transition_height:
            frac = local_y / max(1, transition_height - 1)
            threshold = 1.0 - frac
            for x in range(width):
                use_previous = (BAYER_4X4[y % 4][x % 4] / 15.0) < threshold
                pixels.append(band - 1 if use_previous else band)
        else:
            pixels.extend([band] * width)

    image.putdata(pixels)
    return image


def nearest_two(color: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> tuple[tuple[int, int], tuple[int, int]]:
    ranked = sorted(
        (
            (sum((color[i] - palette_color[i]) ** 2 for i in range(3)), index)
            for index, palette_color in enumerate(palette)
        ),
        key=lambda item: item[0],
    )
    first = ranked[0]
    second = ranked[1] if len(ranked) > 1 else ranked[0]
    return first, second


def recolor_with_ordered_dither(source: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    rgb = source.convert("RGB")
    out = make_indexed_image(rgb.size, palette)
    pixels: list[int] = []

    for y in range(rgb.height):
        for x in range(rgb.width):
            color = rgb.getpixel((x, y))
            (dist_a, idx_a), (dist_b, idx_b) = nearest_two(color, palette)
            if dist_a == dist_b:
                pixels.append(idx_a)
                continue

            mix = dist_a / max(1.0, dist_a + dist_b)
            threshold = BAYER_4X4[y % 4][x % 4] / 15.0
            pixels.append(idx_b if threshold > (1.0 - mix) else idx_a)

    out.putdata(pixels)
    return out


def smooth_and_reduce(source: Image.Image, palette_size: int) -> Image.Image:
    smoothed = source.convert("P").filter(ImageFilter.ModeFilter(size=3))
    palette = build_luma_spaced_palette(smoothed, palette_size, min_gap=10.0)
    out = make_indexed_image(smoothed.size, palette)
    rgb = smoothed.convert("RGB")

    pixels: list[int] = []
    for color in list(rgb.getdata()):
        distances = [
            sum((color[i] - palette_color[i]) ** 2 for i in range(3))
            for palette_color in palette
        ]
        pixels.append(min(range(len(palette)), key=lambda idx: distances[idx]))

    out.putdata(pixels)
    return out


def rework_urban_default_bg_b(path: Path) -> None:
    source = Image.open(path)
    palette = build_luma_spaced_palette(source, count=6, min_gap=12.0)
    build_transition_bands(source.size, palette).save(path, format="PNG")


def rework_urban_linefirst_cohesive_bg_b(path: Path) -> None:
    palette = [
        (6, 24, 36),
        (12, 45, 62),
        (18, 58, 74),
        (24, 72, 86),
        (42, 100, 116),
    ]
    source = Image.open(path)
    build_transition_bands(source.size, palette).save(path, format="PNG")


def rework_mission_shared_bg_b(path: Path) -> None:
    source = Image.open(path)
    palette = build_luma_spaced_palette(source, count=5, min_gap=9.0)
    build_transition_bands(source.size, palette).save(path, format="PNG")


def rework_mission_flat(path: Path) -> None:
    source = Image.open(path)
    palette = build_luma_spaced_palette(source, count=12, min_gap=10.0)
    recolor_with_ordered_dither(source, palette).save(path, format="PNG")


def rework_mission_skylift_bg_a(path: Path) -> None:
    source = Image.open(path)
    smooth_and_reduce(source, palette_size=10).save(path, format="PNG")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rework the remaining viewer `needs_review` assets.")
    parser.add_argument(
        "--project-root",
        default=r"F:\Projects\MegaDrive_DEV\SGDK_projects\METAL_SLUG_URBAN_SUNSET",
        help="Project root containing res/gfx.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    gfx = project_root / "res" / "gfx"

    rework_urban_default_bg_b(gfx / "sky_bg_b.png")
    rework_urban_linefirst_cohesive_bg_b(gfx / "urban_linefirst_cohesive_bg_b.png")
    rework_mission_shared_bg_b(gfx / "mission1_skylift_bg_b.png")
    rework_mission_flat(gfx / "mission1_flat_strict15.png")
    rework_mission_flat(gfx / "mission1_flat_snap_700.png")
    rework_mission_skylift_bg_a(gfx / "mission1_skylift_bg_a.png")

    print("[OK] Reworked viewer needs_review assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
