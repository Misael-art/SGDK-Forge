#!/usr/bin/env python3
"""Measure unique 8x8 patterns required by camera windows.

This is a planning/measurement tool, not a runtime streamer.  It deliberately
works on the converted PNG so the report describes the patterns that the
current SGDK resource exposes.  Camera positions are sampled on tile
boundaries; a preload margin expands the 40x28 viewport without inventing a
non-tile-aligned window.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

TILE = 8
LAB_CACHE_REFERENCE = 1151
LAB_CACHE_MARGIN = 64


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def measure(image_path: Path, viewport_w: int, viewport_h: int, preload: int) -> dict:
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    if width % TILE or height % TILE:
        raise ValueError("stage dimensions must be multiples of 8")
    if viewport_w % TILE or viewport_h % TILE:
        raise ValueError("viewport dimensions must be multiples of 8")
    if viewport_w > width or viewport_h > height:
        raise ValueError("viewport is larger than the stage")

    tiles_w, tiles_h = width // TILE, height // TILE
    viewport_tiles_w, viewport_tiles_h = viewport_w // TILE, viewport_h // TILE
    signatures = []
    for tile_y in range(tiles_h):
        for tile_x in range(tiles_w):
            box = (tile_x * TILE, tile_y * TILE,
                   tile_x * TILE + TILE, tile_y * TILE + TILE)
            signatures.append(image.crop(box).tobytes())

    windows = []
    max_unique = -1
    max_window = None
    for camera_y in range(0, height - viewport_h + 1, TILE):
        for camera_x in range(0, width - viewport_w + 1, TILE):
            x0 = max(0, camera_x // TILE - preload)
            y0 = max(0, camera_y // TILE - preload)
            x1 = min(tiles_w, camera_x // TILE + viewport_tiles_w + preload)
            y1 = min(tiles_h, camera_y // TILE + viewport_tiles_h + preload)
            unique = len({signatures[y * tiles_w + x]
                          for y in range(y0, y1)
                          for x in range(x0, x1)})
            window = {
                "camera_px": [camera_x, camera_y],
                "window_tiles": [x1 - x0, y1 - y0],
                "unique_tiles": unique,
            }
            windows.append(window)
            if unique > max_unique:
                max_unique = unique
                max_window = window

    return {
        "schema_version": "1.0.0",
        "report_kind": "stage_camera_window_occupancy",
        "status": "measurement_only",
        "runtime_streamer_implemented": False,
        "source": {
            "path": str(image_path),
            "sha256": sha256(image_path),
            "dimensions_px": [width, height],
            "global_unique_tiles": len(set(signatures)),
        },
        "viewport_px": [viewport_w, viewport_h],
        "preload_tiles": preload,
        "sampling": {
            "camera_step_px": TILE,
            "window_count": len(windows),
            "camera_max_px": [width - viewport_w, height - viewport_h],
        },
        "occupancy": {
            "max_window_unique_tiles": max_unique,
            "max_window": max_window,
            "min_window_unique_tiles": min(w["unique_tiles"] for w in windows),
            "mean_window_unique_tiles": round(sum(w["unique_tiles"] for w in windows) / len(windows), 3),
        },
        "lab_reference": {
            "cache_capacity_tiles": LAB_CACHE_REFERENCE,
            "margin_tiles": LAB_CACHE_MARGIN,
            "fits_reference_capacity": max_unique + LAB_CACHE_MARGIN <= LAB_CACHE_REFERENCE,
            "warning": "training-lab capacity is reference data; current runtime cache is not implemented or certified",
        },
        "windows": windows,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=root / "res/gfx/showdown.png")
    parser.add_argument("--output", type=Path, default=root / "out/logs/showdown_stream_window_report.json")
    parser.add_argument("--viewport-w", type=int, default=320)
    parser.add_argument("--viewport-h", type=int, default=224)
    parser.add_argument("--preload", type=int, default=1)
    args = parser.parse_args()
    report = measure(args.image, args.viewport_w, args.viewport_h, args.preload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "global_unique_tiles": report["source"]["global_unique_tiles"],
        "max_window_unique_tiles": report["occupancy"]["max_window_unique_tiles"],
        "max_window": report["occupancy"]["max_window"],
        "fits_lab_reference": report["lab_reference"]["fits_reference_capacity"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
