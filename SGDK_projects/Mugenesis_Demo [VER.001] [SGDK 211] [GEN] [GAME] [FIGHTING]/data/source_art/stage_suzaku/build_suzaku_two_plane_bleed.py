#!/usr/bin/env python3
"""Add reflected shake bleed to the source-derived Suzaku far/near plates.

This is a lossless edge operation on the existing indexed source translation.
The 320x224 center must recompose pixel-identically to the current palette-8
anchor; no scene pixels are invented or recolored here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


WIDTH, HEIGHT = 320, 224
PAD_X, PAD_Y = 8, 16


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def reflected_index(value: int, length: int) -> int:
    if value < 0:
        return -value - 1
    if value >= length:
        return (2 * length) - value - 1
    return value


def canonical_tile(tile: bytes) -> bytes:
    rows = [tile[y * 8:(y + 1) * 8] for y in range(8)]
    return min(
        b"".join(row[::-1] if hflip else row for row in (rows[::-1] if vflip else rows))
        for hflip in (False, True)
        for vflip in (False, True)
    )


def canonical_patterns(image: Image.Image) -> set[bytes]:
    pixels = image.tobytes()
    width = image.width
    result: set[bytes] = set()
    for y in range(0, image.height, 8):
        for x in range(0, width, 8):
            tile = bytes(pixels[(y + py) * width + x + px]
                         for py in range(8) for px in range(8))
            result.add(canonical_tile(tile))
    return result


def _load_indexed(path: Path, *, transparent: bool) -> Image.Image:
    image = Image.open(path)
    if image.mode != "P" or image.size != (WIDTH, HEIGHT):
        raise ValueError(f"Expected indexed {WIDTH}x{HEIGHT} PNG, got {image.mode} {image.size}")
    if transparent and image.info.get("transparency") != 0:
        raise ValueError("near_plane_requires_index0_transparency")
    if not transparent and 0 in set(image.get_flattened_data()):
        raise ValueError("far_plane_index0_must_be_unused")
    return image


def bleed_plane(source_path: Path, output_path: Path, *, transparent: bool,
                pad_x: int = PAD_X, pad_y: int = PAD_Y) -> dict:
    source = _load_indexed(source_path, transparent=transparent)
    if pad_x <= 0 or pad_y <= 0 or pad_x % 8 or pad_y % 8:
        raise ValueError("padding_must_be_positive_and_tile_aligned")
    output = Image.new("P", (WIDTH + 2 * pad_x, HEIGHT + 2 * pad_y), 0)
    palette = source.getpalette()
    if palette is not None:
        output.putpalette(palette)
    if transparent:
        output.info["transparency"] = 0
    src, dst = source.load(), output.load()
    for y in range(output.height):
        sy = reflected_index(y - pad_y, HEIGHT)
        for x in range(output.width):
            dst[x, y] = src[reflected_index(x - pad_x, WIDTH), sy]

    before, after = canonical_patterns(source), canonical_patterns(output)
    if before != after:
        raise AssertionError("edge_bleed_changed_canonical_tile_set")
    if output.crop((pad_x, pad_y, pad_x + WIDTH, pad_y + HEIGHT)).tobytes() != source.tobytes():
        raise AssertionError("center_pixels_changed")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_options = {"optimize": False}
    if transparent:
        save_options["transparency"] = 0
    output.save(output_path, **save_options)
    return {
        "source": source_path.as_posix(),
        "source_sha256": sha256(source_path),
        "output": output_path.as_posix(),
        "output_sha256": sha256(output_path),
        "transparent_index0": transparent,
        "source_dimensions": [WIDTH, HEIGHT],
        "output_dimensions": list(output.size),
        "padding_px": {"left": pad_x, "right": pad_x, "top": pad_y, "bottom": pad_y},
        "center_pixel_mismatches": 0,
        "canonical_tiles_before": len(before),
        "canonical_tiles_after": len(after),
        "new_canonical_tiles": 0,
    }


def compose_planes(far_path: Path, near_path: Path) -> Image.Image:
    far = _load_indexed(far_path, transparent=False).convert("RGBA")
    near = _load_indexed(near_path, transparent=True).convert("RGBA")
    far.alpha_composite(near)
    return far.convert("RGB")


def build(project_root: Path, report_path: Path) -> dict:
    data = project_root / "data/source_art/stage_suzaku"
    res = project_root / "res/bgs/suzaku"
    source_far = data / "palette8_far_anchor_indexed.png"
    source_near = data / "palette8_near_anchor_indexed.png"
    anchor = project_root / "res/bgs/suzaku/source_anchor_8.png"
    out_far = res / "source_far_8_bleed.png"
    out_near = res / "source_near_8_bleed.png"
    far = _load_indexed(source_far, transparent=False)
    near = _load_indexed(source_near, transparent=True)
    if far.getpalette() != near.getpalette():
        raise ValueError("far_near_palette_mismatch")
    reconstructed = compose_planes(source_far, source_near)
    with Image.open(anchor) as expected:
        expected_rgb = expected.convert("RGB")
    if ImageChops.difference(reconstructed, expected_rgb).getbbox():
        raise AssertionError("source_planes_do_not_reconstruct_palette8_anchor")
    far_report = bleed_plane(source_far, out_far, transparent=False)
    near_report = bleed_plane(source_near, out_near, transparent=True)
    report = {
        "schema_version": "suzaku_two_plane_bleed.v1",
        "status": "technical_candidate",
        "approval": "none",
        "source_authority": "MUGEN Suzaku source-derived plates; source package and redistribution status remain in project lineage record",
        "anchor": {"path": "res/bgs/suzaku/source_anchor_8.png", "sha256": sha256(anchor)},
        "palette_match": True,
        "center_reconstruction_pixel_mismatches": 0,
        "far_plane": far_report,
        "near_plane": near_report,
        "shake_coverage_px": {"horizontal": [-PAD_X, PAD_X], "vertical": [-PAD_Y, PAD_Y]},
        "claim_ceiling": "static_source_anchor_with_shake_bleed; no parallax, camera pan, or animation proof",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    project_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--report", type=Path,
                        default=project_root / "doc/art/suzaku_two_plane_bleed_report.json")
    args = parser.parse_args()
    report = build(args.project_root.resolve(), args.report.resolve())
    print(json.dumps({"status": report["status"],
                      "center_reconstruction_pixel_mismatches": report["center_reconstruction_pixel_mismatches"],
                      "far_tiles": report["far_plane"]["canonical_tiles_after"],
                      "near_tiles": report["near_plane"]["canonical_tiles_after"],
                      "report": str(args.report)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
