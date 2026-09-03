#!/usr/bin/env python3
"""Validate that a declared native 1 px lineart is not a filled silhouette."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from animation_validation_common import connected_components, erosion_depth, image_mask, sha256_file


TOOL_VERSION = "1.0.0"


def _enclosed_holes(mask: list[list[bool]]) -> int:
    if not mask:
        return 0
    inverse = [[not value for value in row] for row in mask]
    height, width = len(mask), len(mask[0])
    holes = 0
    for component in connected_components(inverse):
        if component and not any(x in {0, width - 1} or y in {0, height - 1} for x, y in component):
            holes += 1
    return holes


def measure(path: Path, transparent_index: int = 0, max_interior_ratio: float = 0.02) -> dict[str, Any]:
    blockers: list[str] = []
    if not path.is_file():
        return {"status": "error", "blockers": ["lineart_file_missing"], "metrics": {}}
    with Image.open(path) as image:
        mask = image_mask(image, transparent_index)
        mode = image.mode
        size = [image.width, image.height]
    visible = sum(sum(1 for value in row if value) for row in mask)
    if visible == 0:
        blockers.append("lineart_empty")
    depth, interior = erosion_depth(mask)
    interior_ratio = interior / max(1, visible)
    components = connected_components(mask)
    enclosed_holes = _enclosed_holes(mask)
    if interior_ratio > 0.20 and enclosed_holes == 0:
        blockers.append("lineart_fill_masquerading_as_contour")
    elif interior_ratio > max_interior_ratio or depth > 0:
        blockers.append("lineart_stroke_over_1px")
    return {
        "tool_name": "validate_lineart_topology",
        "tool_version": TOOL_VERSION,
        "status": "ok" if not blockers else "error",
        "asset_sha256": sha256_file(path),
        "blockers": blockers,
        "metrics": {
            "mode": mode,
            "size": size,
            "visible_pixels": visible,
            "connected_components": len(components),
            "largest_component_pixels": max((len(c) for c in components), default=0),
            "first_erosion_interior_pixels": interior,
            "interior_ratio": round(interior_ratio, 8),
            "max_erosion_depth": depth,
            "enclosed_negative_space_components": enclosed_holes,
        },
    }


def self_check() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        outline = Image.new("P", (24, 24), 0)
        outline.putpalette([0, 0, 0, 255, 255, 255] + [0, 0, 0] * 254)
        draw = ImageDraw.Draw(outline)
        draw.rectangle((4, 4, 19, 19), outline=1, width=1)
        outline_path = root / "outline.png"
        outline.save(outline_path, bits=4, transparency=0)
        filled = Image.new("P", (24, 24), 0)
        filled.putpalette(outline.getpalette())
        ImageDraw.Draw(filled).rectangle((4, 4, 19, 19), fill=1)
        filled_path = root / "filled.png"
        filled.save(filled_path, bits=4, transparency=0)
        thick = Image.new("P", (24, 24), 0)
        thick.putpalette(outline.getpalette())
        ImageDraw.Draw(thick).rectangle((4, 4, 19, 19), outline=1, width=3)
        thick_path = root / "thick.png"
        thick.save(thick_path, bits=4, transparency=0)

        positive = measure(outline_path)
        negative_fill = measure(filled_path)
        negative_thick = measure(thick_path)
    checks = [
        positive["status"] == "ok",
        "lineart_fill_masquerading_as_contour" in negative_fill["blockers"],
        "lineart_stroke_over_1px" in negative_thick["blockers"],
    ]
    if not all(checks):
        print(json.dumps({"positive": positive, "fill": negative_fill, "thick": negative_thick}, indent=2), file=sys.stderr)
        return 1
    print("validate_lineart_topology self-check passed (outline, filled silhouette, thick stroke)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--transparent-index", type=int, default=0)
    parser.add_argument("--max-interior-ratio", type=float, default=0.02)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if not args.input:
        parser.error("--input is required unless --self-check is used")
    report = measure(args.input.resolve(), args.transparent_index, args.max_interior_ratio)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
