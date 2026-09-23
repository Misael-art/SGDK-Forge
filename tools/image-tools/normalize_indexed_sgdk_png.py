#!/usr/bin/env python3
"""Normalize indexed PNG assets for SGDK validation.

This utility preserves the visual result while fixing two common issues:

1. Inflated PLTE chunks (e.g. 256 entries while only 14-15 indexes are used)
2. Unsafe use of palette index 0 for visible pixels when the asset should not
   rely on structural transparency

Modes:
  - transparent0: keep/remap used index 0 as transparent and compact the PLTE
  - unused0: reserve index 0 as unused/opaque and shift all visible colors away
             from index 0 while compacting the PLTE
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image


def build_palette_rgb(image: Image.Image) -> list[tuple[int, int, int]]:
    palette = image.getpalette() or []
    entries = len(palette) // 3
    return [
        tuple(palette[index * 3 : index * 3 + 3])
        for index in range(entries)
    ]


def backup_once(path: Path) -> None:
    backup = path.with_suffix(path.suffix + ".normalizebak")
    if not backup.exists():
        shutil.copy2(path, backup)


def normalize_transparent0(image: Image.Image) -> Image.Image:
    used = sorted(set(image.getdata()))
    palette_rgb = build_palette_rgb(image)

    if 0 not in used:
        used = [0] + used

    ordered = [0] + [idx for idx in used if idx != 0]
    if len(ordered) > 16:
        raise ValueError(f"transparent0 needs <=16 palette entries, got {len(ordered)}")

    remap = {old: new for new, old in enumerate(ordered)}
    new_pixels = [remap[pixel] for pixel in image.getdata()]

    normalized = Image.new("P", image.size)
    normalized.putdata(new_pixels)

    palette = []
    for old in ordered:
        if old < len(palette_rgb):
            palette.extend(palette_rgb[old])
        else:
            palette.extend((0, 0, 0))
    normalized.putpalette(palette)
    normalized.info["transparency"] = 0
    return normalized


def normalize_unused0(image: Image.Image) -> Image.Image:
    used = sorted(set(image.getdata()))
    palette_rgb = build_palette_rgb(image)

    ordered_visible = [idx for idx in used if idx != 0]
    if 0 in used:
        ordered_visible = [0] + ordered_visible
    if len(ordered_visible) > 15:
        raise ValueError(f"unused0 needs <=15 visible colors, got {len(ordered_visible)}")

    remap = {old: new for new, old in enumerate(ordered_visible, start=1)}
    new_pixels = [remap[pixel] for pixel in image.getdata()]

    normalized = Image.new("P", image.size)
    normalized.putdata(new_pixels)

    palette = [0, 0, 0]
    for old in ordered_visible:
        if old < len(palette_rgb):
            palette.extend(palette_rgb[old])
        else:
            palette.extend((0, 0, 0))
    normalized.putpalette(palette)
    normalized.info.pop("transparency", None)
    return normalized


def normalize_file(mode: str, path: Path) -> None:
    with Image.open(path) as image:
        if image.mode != "P":
            raise ValueError(f"{path} is not indexed (mode={image.mode})")

        if mode == "transparent0":
            normalized = normalize_transparent0(image)
        elif mode == "unused0":
            normalized = normalize_unused0(image)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        backup_once(path)
        normalized.save(path, format="PNG")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize indexed PNGs for SGDK.")
    parser.add_argument(
        "mode",
        choices=("transparent0", "unused0"),
        help="How index 0 should be treated",
    )
    parser.add_argument("files", nargs="+", help="PNG files to normalize in place")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for raw_path in args.files:
        path = Path(raw_path).resolve()
        normalize_file(args.mode, path)
        print(f"[OK] {args.mode}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
