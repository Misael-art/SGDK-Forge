#!/usr/bin/env python3
"""R3-02: collapse only the five declared R2 palette-noise colors."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

NOISE = ((36, 73, 73), (73, 73, 36), (73, 109, 109), (146, 109, 109), (146, 146, 109))
GRID = {0, 36, 73, 109, 146, 182, 219, 255}


def rgb(path):
    return Image.open(path).convert("RGB")


def indexed(pixels, size, output):
    colors = sorted(set(pixels))
    palette = [channel for color in colors for channel in color] + [0] * (768 - len(colors) * 3)
    lookup = {color: index for index, color in enumerate(colors)}
    image = Image.new("P", size)
    image.putpalette(palette)
    image.putdata([lookup[pixel] for pixel in pixels])
    image.save(output, optimize=False)
    return len(colors)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main(project_root):
    root = Path(project_root)
    source = root / "data/source_art/r2/r2-02/layers.png"
    output = root / "data/source_art/r3/r3-02/layers.png"
    before = rgb(source)
    width, height = before.size
    source_pixels = list(before.getdata())
    counts = Counter(source_pixels)
    existing = sorted(color for color in counts if color not in NOISE)
    mapping = {}
    for noisy in NOISE:
        # Squared Euclidean RGB distance; lexicographic RGB is the stable tie-break.
        mapping[noisy] = min(
            existing,
            key=lambda candidate: (sum((a - b) ** 2 for a, b in zip(noisy, candidate)), candidate),
        )
    result_pixels = [mapping.get(pixel, pixel) for pixel in source_pixels]
    palette_colors = indexed(result_pixels, before.size, output)
    after_pixels = list(rgb(output).getdata())
    y_split = 730
    upper = width * y_split
    luma = lambda color: (0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]) / 255.0
    result_counts = Counter(after_pixels)
    report = {
        "generated_by": "Codex",
        "scope": "R3-02 only; source candidate only; no res/ promotion",
        "source": str(source),
        "output": str(output),
        "method": "exact palette collapse of five declared noise colors to nearest existing RGB neighbor; squared RGB distance, lexicographic tie-break",
        "noise_to_existing_palette_map": [
            {"from": list(color), "to": list(mapping[color]), "distance_squared": sum((a - b) ** 2 for a, b in zip(color, mapping[color])), "pixels_collapsed": counts[color]}
            for color in NOISE
        ],
        "palette_colors_before": len(counts),
        "palette_colors_after": palette_colors,
        "new_colors": [],
        "layers_1_to_4_pixel_diff": sum(a != b for a, b in zip(source_pixels[:upper], after_pixels[:upper])),
        "layer_5_luminance_srgb_weighted": round(sum(luma(color) for color in after_pixels[upper:]) / len(after_pixels[upper:]), 6),
        "illegal_rgb333_project_grid_pixels": sum(count for color, count in result_counts.items() if any(channel not in GRID for channel in color)),
        "sha256": sha256(output),
    }
    report_path = root / "data/source_art/r3/r3_validation_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="ascii")
    print(json.dumps(report, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: r3_palette_collapse.py <project-root>")
    main(sys.argv[1])
