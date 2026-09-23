#!/usr/bin/env python3
"""Translate the authored selection surface into the measured VDP window."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / "generated_select_surface_v02.png"
OUTPUT = Path(__file__).resolve().parent / "generated_select_surface_v03.png"
REPORT = Path(__file__).resolve().parent / "convert_select_surface_report.json"
W, H = 320, 224
TILE_BUDGET = 220


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def select_representatives(vectors: np.ndarray, counts: np.ndarray, budget: int) -> np.ndarray:
    if len(vectors) <= budget:
        return np.arange(len(vectors), dtype=np.int32)
    nearest = np.full(len(vectors), np.inf, dtype=np.float32)
    selected: list[int] = []
    index = int(counts.argmax())
    for _ in range(budget):
        selected.append(index)
        distance = np.sum((vectors - vectors[index]) ** 2, axis=1)
        nearest = np.minimum(nearest, distance)
        score = nearest * np.sqrt(counts)
        score[selected] = -1
        index = int(np.argmax(score))
    return np.asarray(selected, dtype=np.int32)


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")
    reduced = source.resize((W // 2, H // 2), Image.Resampling.NEAREST)
    stage = reduced.resize((W, H), Image.Resampling.NEAREST)
    quant = stage.quantize(colors=15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    palette_data = quant.getpalette()
    palette = [(0, 0, 0)]
    for i in range(15):
        color = tuple(int(round(palette_data[i * 3 + c] / 34.0) * 34) for c in range(3))
        color = tuple(max(0, min(238, value)) for value in color)
        if color not in palette:
            palette.append(color)
    palette = (palette + [(0, 0, 0)] * 16)[:16]
    indexed = Image.new("P", (W, H))
    indexed.putpalette([channel for color in palette for channel in color] + [0] * (3 * 240))
    src = np.asarray(stage, dtype=np.uint8)
    dst = np.asarray(indexed, dtype=np.uint8).copy()
    opaque = max(1, len(palette) - 1)
    for y in range(H):
        for x in range(W):
            rgb = src[y, x].astype(np.int32)
            distances = [int(np.sum((rgb - np.asarray(palette[i], dtype=np.int32)) ** 2)) for i in range(1, opaque + 1)]
            dst[y, x] = 1 + int(np.argmin(distances))
    indexed = Image.fromarray(dst, mode="P")
    indexed.putpalette([channel for color in palette for channel in color] + [0] * (3 * 240))

    grid_h, grid_w = H // 8, W // 8
    tiles = np.asarray(indexed).reshape(grid_h, 8, grid_w, 8).transpose(0, 2, 1, 3).reshape(grid_h, grid_w, 64)
    unique, inverse = np.unique(tiles.reshape(-1, 64), axis=0, return_inverse=True)
    ids_grid = inverse.reshape(grid_h, grid_w)
    mapped = np.empty_like(ids_grid)
    for ry in range(2):
        for rx in range(4):
            x0, x1 = grid_w * rx // 4, grid_w * (rx + 1) // 4
            y0, y1 = grid_h * ry // 2, grid_h * (ry + 1) // 2
            local_ids = ids_grid[y0:y1, x0:x1].reshape(-1)
            ids, counts = np.unique(local_ids, return_counts=True)
            chosen = ids[select_representatives(unique[ids].astype(np.float32), counts, TILE_BUDGET // 8)]
            vectors = unique[chosen].astype(np.float32)
            local_vectors = unique[local_ids].astype(np.float32)
            distance = np.sum((local_vectors[:, None, :] - vectors[None, :, :]) ** 2, axis=2)
            mapped[y0:y1, x0:x1] = chosen[np.argmin(distance, axis=1)].reshape(y1 - y0, x1 - x0)
    output_tiles = unique[mapped]
    output_pixels = output_tiles.reshape(grid_h, grid_w, 8, 8).transpose(0, 2, 1, 3).reshape(H, W)
    output = Image.fromarray(output_pixels.astype(np.uint8), mode="P")
    output.putpalette(indexed.getpalette())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    output.save(OUTPUT, format="PNG")
    report = {
        "schema_version": "1.0.0",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": sha256(OUTPUT),
        "dimensions": [W, H],
        "pre_tile_reduction": "2x_nearest_then_mega_drive_9bit_palette",
        "tile_reuse_mode": "regional_material_preserving",
        "unique_tiles_before_reuse": int(len(unique)),
        "unique_tiles_after_reuse": int(len(np.unique(output_tiles.reshape(-1, 64), axis=0))),
        "tile_budget": TILE_BUDGET,
        "claim_ceiling": "translated_selection_surface_candidate",
        "visual_review_required": True,
        "emulator_validated": False,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
