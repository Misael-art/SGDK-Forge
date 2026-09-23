#!/usr/bin/env python3
"""Quantize an image to Mega Drive RGB 3-3-3 lattice and indexed 4bpp-friendly PNG.

Order (PALETTES.md):
  1) reduce color count first (target 15 + transparency key)
  2) snap each channel to nearest of 8 MD levels
  3) never snap before reduce

Index 0 = transparency key (magenta by default for sprites, or first bg color).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image
import numpy as np

# MD levels in 8-bit: round(n * 255 / 7) for n in 0..7
MD_LEVELS = np.array([0, 36, 73, 109, 146, 182, 219, 255], dtype=np.int16)


def snap_channel(v: np.ndarray) -> np.ndarray:
    # nearest MD level
    d = np.abs(v[..., None].astype(np.int16) - MD_LEVELS[None, :])
    return MD_LEVELS[d.argmin(axis=-1)].astype(np.uint8)


def snap_rgb333(rgb: np.ndarray) -> np.ndarray:
    out = rgb.copy()
    out[..., 0] = snap_channel(rgb[..., 0])
    out[..., 1] = snap_channel(rgb[..., 1])
    out[..., 2] = snap_channel(rgb[..., 2])
    return out


def is_key_color(rgb: np.ndarray, key=(255, 0, 255), tol=40) -> np.ndarray:
    return (
        (np.abs(rgb[..., 0].astype(np.int16) - key[0]) <= tol)
        & (np.abs(rgb[..., 1].astype(np.int16) - key[1]) <= tol)
        & (np.abs(rgb[..., 2].astype(np.int16) - key[2]) <= tol)
    )


def quantize(
    src: Path,
    dst: Path,
    *,
    max_colors: int = 15,
    target_size: tuple[int, int] | None = None,
    key_magenta: bool = True,
    align: int = 8,
) -> dict:
    im = Image.open(src).convert("RGBA")
    if target_size:
        im = im.resize(target_size, Image.Resampling.NEAREST)

    arr = np.array(im)
    rgb = arr[..., :3]
    alpha = arr[..., 3]

    if key_magenta:
        mask_key = is_key_color(rgb) | (alpha < 128)
    else:
        mask_key = alpha < 128

    work = rgb.copy()
    # Neutral fill for keyed pixels so they don't steal palette slots
    work[mask_key] = (0, 0, 0)

    # Step 1: reduce colors on non-key pixels via adaptive palette
    solid = Image.fromarray(work, mode="RGB")
    # Use adaptive palette of max_colors
    pal_im = solid.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    reduced = np.array(pal_im.convert("RGB"))

    # Step 2: snap to RGB333
    snapped = snap_rgb333(reduced)

    # Rebuild with key as pure magenta (index 0 candidate)
    final_rgb = snapped.copy()
    final_rgb[mask_key] = (255, 0, 255)

    # Align dimensions to tile boundary
    h, w = final_rgb.shape[:2]
    nw = (w // align) * align
    nh = (h // align) * align
    if nw < 8:
        nw = 8
    if nh < 8:
        nh = 8
    final_rgb = final_rgb[:nh, :nw]

    # Index: put magenta as index 0
    flat = final_rgb.reshape(-1, 3)
    # unique colors with magenta first
    mag = (255, 0, 255)
    colors = []
    seen = set()
    colors.append(mag)
    seen.add(mag)
    for c in map(tuple, flat):
        if c not in seen:
            seen.add(c)
            colors.append(c)
            if len(colors) >= 16:
                break
    # If more unique after snap, remap extras to nearest in palette
    palette_arr = np.array(colors, dtype=np.int16)
    mapped = np.zeros((nh, nw), dtype=np.uint8)
    for y in range(nh):
        for x in range(nw):
            pix = final_rgb[y, x]
            t = tuple(pix)
            if t in seen and colors.index(t) < 16:
                mapped[y, x] = colors.index(t)
            else:
                d = np.sum((palette_arr - pix.astype(np.int16)) ** 2, axis=1)
                mapped[y, x] = int(d.argmin())

    # Build indexed PNG
    out = Image.fromarray(mapped, mode="P")
    # palette: 768 bytes RGB
    pal = []
    for c in colors:
        pal.extend(c)
    while len(pal) < 768:
        pal.extend((0, 0, 0))
    out.putpalette(pal[:768])
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)

    # legality: all non-key colors on lattice
    illegal = 0
    for c in colors[1:]:
        for ch in c:
            if ch not in set(MD_LEVELS.tolist()):
                illegal += 1
                break

    report = {
        "src": str(src),
        "dst": str(dst),
        "size": [int(nw), int(nh)],
        "colors": len(colors),
        "palette": [[int(x) for x in c] for c in colors],
        "illegal_rgb333": int(illegal),
        "key_pixels": int(mask_key[:nh, :nw].sum()) if mask_key.shape[0] >= nh else 0,
    }
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--max-colors", type=int, default=15)
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--no-key", action="store_true")
    args = ap.parse_args()
    target = None
    if args.width and args.height:
        target = (args.width, args.height)
    rep = quantize(
        Path(args.src),
        Path(args.dst),
        max_colors=args.max_colors,
        target_size=target,
        key_magenta=not args.no_key,
    )
    import json
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
