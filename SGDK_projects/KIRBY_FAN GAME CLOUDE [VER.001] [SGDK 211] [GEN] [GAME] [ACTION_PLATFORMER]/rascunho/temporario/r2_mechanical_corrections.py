#!/usr/bin/env python3
"""Deterministic source-art corrections for R2-02/03/04; never promotes assets."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

GRID = (0, 36, 73, 109, 146, 182, 219, 255)
KEY = (255, 0, 255)


def rgb_image(path):
    return Image.open(path).convert("RGB")


def write_indexed_rgb(pixels, width, height, path):
    colors = sorted(set(pixels))
    if KEY in colors:
        colors.remove(KEY)
        colors.insert(0, KEY)
    if len(colors) > 256:
        raise ValueError(f"palette inflated to {len(colors)} colors")
    palette = []
    for color in colors:
        palette.extend(color)
    palette.extend([0] * (768 - len(palette)))
    index_by_color = {color: index for index, color in enumerate(colors)}
    image = Image.new("P", (width, height))
    image.putpalette(palette)
    image.putdata([index_by_color[pixel] for pixel in pixels])
    image.save(path, optimize=False)
    return len(colors)


def luma(pixel):
    r, g, b = pixel
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def snap_channel(value):
    return min(GRID, key=lambda candidate: (abs(candidate - value), candidate))


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def correct_layer_5(source, output):
    original = rgb_image(source)
    width, height = original.size
    y_start = 730
    source_pixels = list(original.getdata())
    crop = source_pixels[y_start * width:]
    source_colors = sorted(set(crop))
    source_counts = Counter(crop)
    best = None
    for scale_i in range(100, 1001):
        scale = scale_i / 1000.0
        mapping = {
            color: tuple(snap_channel(channel * scale) for channel in color)
            for color in source_colors
        }
        mapped_luma = {color: luma(mapped) for color, mapped in mapping.items()}
        value = sum(source_counts[color] * mapped_luma[color] for color in source_colors) / len(crop)
        candidate = (abs(value - 0.255), scale, mapping, value)
        if best is None or candidate[0] < best[0]:
            best = candidate
    _, scale, mapping, measured = best
    mapped = [mapping[color] for color in crop]
    micro_dither_pixels = 0
    if measured > 0.27:
        # Palette snapping has a discontinuity here.  Darken the smallest
        # deterministic subset of the neutral backing tone to enter the
        # requested interval without changing any other layer or geometry.
        counts = Counter(mapped)
        candidate = max(counts, key=lambda color: (counts[color], luma(color)))
        darker = tuple(snap_channel(max(0, channel - 37)) for channel in candidate)
        delta = luma(candidate) - luma(darker)
        desired = 0.2699
        micro_dither_pixels = int(((measured - desired) * len(mapped)) / delta) + 1
        candidate_positions = [i for i, color in enumerate(mapped) if color == candidate]
        def blue_noise_rank(i):
            x, y = i % width, i // width
            value = ((x * 73856093) ^ (y * 19349663)) & 0xFFFFFFFF
            value ^= value >> 13
            value = (value * 1274126177) & 0xFFFFFFFF
            return value ^ (value >> 16)
        selected = set(sorted(candidate_positions, key=blue_noise_rank)[:micro_dither_pixels])
        mapped = [darker if i in selected else color for i, color in enumerate(mapped)]
        measured = sum(luma(color) for color in mapped) / len(mapped)
    corrected = source_pixels[:y_start * width] + mapped
    palette_count = write_indexed_rgb(corrected, width, height, output)
    output_pixels = list(rgb_image(output).getdata())
    untouched_diff = sum(
        before != after
        for before, after in zip(source_pixels[:y_start * width], output_pixels[:y_start * width])
    )
    return {
        "source": str(source),
        "output": str(output),
        "method": "palette-snapped multiplicative darkening limited to y>=730",
        "layer_5_bounds": {"x": [0, width - 1], "y": [y_start, height - 1]},
        "selected_scale": scale,
        "palette_snap_micro_dither": {
            "pixels": micro_dither_pixels,
            "purpose": "enter the requested luminance interval after discrete RGB333 snapping",
        },
        "layer_5_luminance_srgb_weighted": round(measured, 6),
        "layers_1_to_4_pixel_diff": untouched_diff,
        "palette_colors": palette_count,
    }


def remap_colors(source, output, replacements, forbidden):
    original = rgb_image(source)
    width, height = original.size
    before = list(original.getdata())
    after = [replacements.get(pixel, pixel) for pixel in before]
    palette_count = write_indexed_rgb(after, width, height, output)
    final = list(rgb_image(output).getdata())
    counts = Counter(final)
    return {
        "source": str(source),
        "output": str(output),
        "method": "exact RGB replacement only; no geometry, crop, or resampling",
        "palette_colors": palette_count,
        "forbidden_pixel_counts": {str(color): counts[color] for color in forbidden},
        "key_pixel_count": counts[KEY],
        "changed_pixel_count": sum(a != b for a, b in zip(before, final)),
    }


def rebalance_floating_midtone(source, output):
    image = rgb_image(source)
    width, height = image.size
    pixels = list(image.getdata())
    clear = (255, 182, 219)
    midtone = (255, 146, 182)
    visible = sum(pixel not in (KEY, (255, 255, 255)) for pixel in pixels)
    current = sum(pixel == midtone for pixel in pixels)
    target = round(visible * 0.10)
    required = max(0, target - current)
    eligible = [
        i for i, pixel in enumerate(pixels)
        if pixel == clear
    ]
    # The compact central ellipse reads as the body's mid-plane at 28px;
    # selecting by distance keeps the new tone contiguous rather than noisy.
    def body_score(i):
        x, y = i % width, i // width
        return ((x - 152) / 1.35) ** 2 + (y - 104) ** 2
    selected = set(sorted(eligible, key=body_score)[:required])
    corrected = [midtone if i in selected else pixel for i, pixel in enumerate(pixels)]
    palette_count = write_indexed_rgb(corrected, width, height, output)
    final = list(rgb_image(output).getdata())
    final_visible = sum(pixel not in (KEY, (255, 255, 255)) for pixel in final)
    final_mid = sum(pixel == midtone for pixel in final)
    return {
        "source": str(source),
        "output": str(output),
        "method": "compact central midtone cluster after localized image edit",
        "midtone_rgb": list(midtone),
        "visible_character_pixels": final_visible,
        "midtone_pixels": final_mid,
        "midtone_percent_of_character": round(final_mid * 100.0 / final_visible, 6),
        "palette_colors": palette_count,
    }


def main(project):
    project = Path(project)
    r1 = project / "data/source_art/r1"
    r2 = project / "data/source_art/r2"
    report = {
        "generated_by": "Codex",
        "scope": "R2 mechanical corrections only; source candidates only; no res/ promotion",
        "rgb333_project_grid": list(GRID),
        "luminance_formula": "(0.2126*R + 0.7152*G + 0.0722*B) / 255",
        "r2_02": correct_layer_5(r1 / "r1-02/layers.png", r2 / "r2-02/layers.png"),
        "r2_03": remap_colors(
            r1 / "r1-03/concept.png", r2 / "r2-03/concept.png",
            {(255, 0, 219): KEY, (219, 0, 219): KEY},
            [(255, 0, 219), (219, 0, 219)],
        ),
        "r2_04": remap_colors(
            r1 / "r1-04/concept.png", r2 / "r2-04/concept.png",
            {(219, 0, 219): KEY, (219, 36, 182): KEY},
            [(219, 0, 219), (219, 36, 182)],
        ),
    }
    r2_01_source = r2 / "r2-01/floating_pose_r2_crop.png"
    if r2_01_source.exists():
        report["r2_01"] = rebalance_floating_midtone(r2_01_source, r2_01_source)
    for section in report:
        if not section.startswith("r2_"):
            continue
        report[section]["sha256"] = sha256(report[section]["output"])
    report_path = r2 / "r2_mechanical_validation.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="ascii")
    print(json.dumps(report, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: r2_mechanical_corrections.py <project-root>")
    main(sys.argv[1])
