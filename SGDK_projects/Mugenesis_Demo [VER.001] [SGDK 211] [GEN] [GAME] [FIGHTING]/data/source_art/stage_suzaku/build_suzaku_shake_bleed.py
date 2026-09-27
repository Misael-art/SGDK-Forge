#!/usr/bin/env python3
"""Build source-derived edge bleed for the locked Suzaku camera anchor.

Only mirrors existing indexed pixels at the image edges. The 320x224 source
window remains byte-for-byte pixel-identical in the center; no new art is
painted or synthesized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


WIDTH, HEIGHT = 320, 224
PAD_X, PAD_Y = 8, 16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reflected_index(value: int, length: int) -> int:
    if value < 0:
        return -value - 1
    if value >= length:
        return (2 * length) - value - 1
    return value


def canonical_tile(tile: tuple[int, ...]) -> tuple[int, ...]:
    rows = [tile[y * 8:(y + 1) * 8] for y in range(8)]
    variants = []
    for vflip in (False, True):
        source_rows = rows[::-1] if vflip else rows
        for hflip in (False, True):
            variants.append(tuple(px for row in source_rows
                                  for px in (row[::-1] if hflip else row)))
    return min(variants)


def canonical_patterns(image: Image.Image) -> set[tuple[int, ...]]:
    pixels = image.load()
    return {
        canonical_tile(tuple(pixels[x + tx, y + ty]
                             for ty in range(8) for tx in range(8)))
        for y in range(0, image.height, 8)
        for x in range(0, image.width, 8)
    }


def create_bleed(source_path: Path, output_path: Path,
                 pad_x: int = PAD_X, pad_y: int = PAD_Y) -> dict:
    source = Image.open(source_path)
    if source.mode != "P" or source.size != (WIDTH, HEIGHT):
        raise ValueError(f"Expected indexed {WIDTH}x{HEIGHT} PNG, got {source.mode} {source.size}")
    if pad_x <= 0 or pad_y <= 0 or pad_x % 8 or pad_y % 8:
        raise ValueError("Padding must be positive and aligned to the 8x8 tile grid")

    output = Image.new("P", (WIDTH + 2 * pad_x, HEIGHT + 2 * pad_y), 0)
    palette = source.getpalette()
    if palette is not None:
        output.putpalette(palette)
    source_pixels = source.load()
    output_pixels = output.load()
    for y in range(output.height):
        source_y = reflected_index(y - pad_y, HEIGHT)
        for x in range(output.width):
            source_x = reflected_index(x - pad_x, WIDTH)
            output_pixels[x, y] = source_pixels[source_x, source_y]

    # Existing edge tiles may be reused through SGDK's H/V flip optimization.
    before, after = canonical_patterns(source), canonical_patterns(output)
    if not after.issubset(before):
        raise AssertionError("Bleed introduced a tile pattern absent from the authored source")
    if before != after:
        raise AssertionError("Bleed changed the source's canonical 8x8 tile-pattern set")

    center = output.crop((pad_x, pad_y, pad_x + WIDTH, pad_y + HEIGHT))
    if center.tobytes() != source.tobytes():
        raise AssertionError("Centered source image changed during bleed composition")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.save(output_path, optimize=False)
    return {
        "schema_version": "suzaku_stage_bleed.v1",
        "status": "source_composed_candidate",
        "source": source_path.as_posix(),
        "source_sha256": sha256(source_path),
        "output": output_path.as_posix(),
        "output_sha256": sha256(output_path),
        "source_dimensions": [WIDTH, HEIGHT],
        "output_dimensions": [output.width, output.height],
        "padding_px": {"left": pad_x, "right": pad_x, "top": pad_y, "bottom": pad_y},
        "center_pixel_mismatches": 0,
        "source_hv_canonical_tile_patterns": len(before),
        "output_hv_canonical_tile_patterns": len(after),
        "new_tile_patterns": 0,
        "method": "reflect_existing_indexed_edge_pixels",
        "claim_ceiling": "shake_overscan_only_static_camera_anchor",
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=project_root / "res/bgs/suzaku/source_anchor_8.png")
    parser.add_argument("--output", type=Path,
                        default=project_root / "res/bgs/suzaku/source_anchor_8_bleed.png")
    parser.add_argument("--report", type=Path,
                        default=project_root / "doc/art/suzaku_stage_bleed_report.json")
    args = parser.parse_args()
    source = args.source if args.source.is_absolute() else project_root / args.source
    output = args.output if args.output.is_absolute() else project_root / args.output
    report = args.report if args.report.is_absolute() else project_root / args.report
    result = create_bleed(source, output)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
