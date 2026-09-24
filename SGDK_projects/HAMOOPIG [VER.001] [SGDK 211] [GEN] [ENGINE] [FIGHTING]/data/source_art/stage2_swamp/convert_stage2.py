#!/usr/bin/env python3
"""Translate the authored Stage 2 source into a bounded SGDK background.

The source is intentionally kept separate from the indexed runtime asset.  The
conversion snaps colours to the Mega Drive 9-bit grid and reuses complete 8x8
source tiles so the result has a measured resident-tile ceiling.
"""
from __future__ import annotations

import hashlib
import json
import argparse
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / "generated_stage2_v02.png"
OUTPUT = ROOT / "res/gfx/bgb2.png"
REPORT = Path(__file__).resolve().parent / "convert_stage2_report.json"
OUT_W, OUT_H = 512, 256
COLORS = 14
# The authored dock contains 1887 source tiles. 864 is the measured resident
# ceiling after the HUD atlas and sprite-engine reservation are accounted for.
# Higher visual candidates (1040/1120/1200) were rejected by the live guard.
TILE_BUDGET = 864
SNAP = 34


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snap9(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(max(0, min(238, int(round(int(v) / SNAP) * SNAP))) for v in rgb)


def fit_stage(source: Image.Image, block: int) -> Image.Image:
    """Preserve the 2:1 composition in the full 512x256 stage world."""
    src = source.convert("RGBA")
    base = Image.new("RGB", src.size, (0, 0, 0))
    base.paste(src, mask=src.getchannel("A"))
    stage = base.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
    if block > 1:
        reduced = stage.resize((OUT_W // block, OUT_H // block),
                               Image.Resampling.NEAREST)
        stage = reduced.resize((OUT_W, OUT_H), Image.Resampling.NEAREST)
    return stage


def indexed_stage(stage: Image.Image) -> tuple[Image.Image, list[tuple[int, int, int]]]:
    quant = stage.quantize(colors=COLORS, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    raw = quant.getpalette()
    candidates: list[tuple[int, int, int]] = []
    for i in range(COLORS):
        c = snap9((raw[i * 3], raw[i * 3 + 1], raw[i * 3 + 2]))
        # Reserve palette index 0 for transparency/backdrop.  Test the
        # snapped colour here (not the pre-snap RGB): near-black source
        # colours can quantize to (0,0,0) on the Mega Drive 9-bit grid and
        # must not become opaque black holes in the bottom of the stage.
        if c not in candidates and c != (0, 0, 0):
            candidates.append(c)
    if not candidates:
        candidates.append((34, 34, 34))
    palette = [(0, 0, 0)] + candidates[:15]
    while len(palette) < 16:
        palette.append((0, 0, 0))
    source_rgb = stage.convert("RGB")
    opaque_count = min(len(candidates), 14)
    out = Image.new("P", stage.size)
    out.putpalette([v for c in palette for v in c] + [0] * (3 * (256 - len(palette))))
    sp, dp = source_rgb.load(), out.load()
    for y in range(OUT_H):
        for x in range(OUT_W):
            rgb = sp[x, y]
            # BG_B index 0 is deliberately reserved for the backdrop/blank
            # convention used by the renderer.  Even near-black source pixels
            # therefore choose the closest opaque entry (1..14).
            # Never search padded palette entries (which are black by
            # construction); only authored opaque colours are legal targets.
            best = min(range(1, opaque_count + 1), key=lambda i: sum((int(rgb[k]) - palette[i][k]) ** 2 for k in range(3)))
            dp[x, y] = best
    return out, palette


def _select_representatives(vectors: np.ndarray, counts: np.ndarray, budget: int) -> np.ndarray:
    """Select a perceptually useful local tile vocabulary.

    The former global vocabulary let a sky tile replace a water or timber tile
    when both had a similar mean error. That is numerically cheap but creates
    large false rectangles at scene boundaries. This selector keeps the most
    frequent tile first and then maximizes weighted visual separation.
    """
    if len(vectors) <= budget:
        return np.arange(len(vectors), dtype=np.int32)
    nearest = np.full(len(vectors), np.inf, dtype=np.float32)
    selected: list[int] = []
    idx = int(counts.argmax())
    for _ in range(budget):
        selected.append(idx)
        dist = np.sum((vectors - vectors[idx]) ** 2, axis=1)
        mask = dist < nearest
        nearest[mask] = dist[mask]
        score = nearest * np.sqrt(counts)
        score[selected] = -1
        idx = int(np.argmax(score))
    return np.asarray(selected, dtype=np.int32)


def tile_reuse(img: Image.Image, local_regions: bool = True) -> tuple[Image.Image, int, int]:
    px = np.asarray(img, dtype=np.uint8)
    grid_h, grid_w = OUT_H // 8, OUT_W // 8
    tiles = px.reshape(grid_h, 8, grid_w, 8).transpose(0, 2, 1, 3).reshape(grid_h, grid_w, 64)
    unique, inverse = np.unique(tiles.reshape(-1, 64), axis=0, return_inverse=True)
    unique_count = len(unique)
    if unique_count <= TILE_BUDGET:
        return img, unique_count, unique_count

	# Allocate the measured vocabulary over broad material neighborhoods.  The
	# regions are large enough to avoid a checkerboard and small enough that a
	# sky tile cannot become the nearest replacement for dock foreground.
    if local_regions:
        region_x, region_y = 4, 2
        budget = TILE_BUDGET // (region_x * region_y)
        mapped_tiles = np.empty((grid_h, grid_w), dtype=np.int32)
        for ry in range(region_y):
            for rx in range(region_x):
                x0, x1 = grid_w * rx // region_x, grid_w * (rx + 1) // region_x
                y0, y1 = grid_h * ry // region_y, grid_h * (ry + 1) // region_y
                region_ids = inverse.reshape(grid_h, grid_w)[y0:y1, x0:x1]
                flat_region_ids = region_ids.reshape(-1)
                ids, counts = np.unique(flat_region_ids, return_counts=True)
                selected = _select_representatives(unique[ids].astype(np.float32), counts, budget)
                chosen_ids = ids[selected]
                vectors = unique[chosen_ids].astype(np.float32)
                region_vectors = unique[flat_region_ids].astype(np.float32)
                dist = np.sum((region_vectors[:, None, :] - vectors[None, :, :]) ** 2, axis=2)
                mapped_tiles[y0:y1, x0:x1] = chosen_ids[np.argmin(dist, axis=1)].reshape(y1 - y0, x1 - x0)
        mapped = unique[mapped_tiles]
    else:
        # Preserve the old global mode as a diagnostic fallback.
        counts = np.bincount(inverse)
        selected = _select_representatives(unique.astype(np.float32), counts, TILE_BUDGET)
        vectors = unique[selected].astype(np.float32)
        dist = np.sum((unique[:, None, :].astype(np.float32) - vectors[None, :, :]) ** 2, axis=2)
        mapped = unique[selected[np.argmin(dist, axis=1)]][inverse].reshape(grid_h, grid_w, 64)
    out_px = mapped.reshape(grid_h, grid_w, 8, 8).transpose(0, 2, 1, 3).reshape(OUT_H, OUT_W)
    out = Image.fromarray(out_px.astype(np.uint8), mode="P")
    out.putpalette(img.getpalette())
    return out, unique_count, len(np.unique(mapped.reshape(-1, 64), axis=0))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", type=int, choices=(1, 2, 3, 4), default=1)
    parser.add_argument("--global-reuse", action="store_true", help="use the legacy cross-material tile vocabulary")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    args = parser.parse_args()
    if not args.output.is_absolute():
        args.output = ROOT / args.output
    if not args.report.is_absolute():
        args.report = ROOT / args.report
    indexed, palette = indexed_stage(fit_stage(Image.open(SOURCE), args.block))
    resident, unique_before, unique_after = tile_reuse(indexed, local_regions=not args.global_reuse)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    resident.save(args.output, format="PNG")
    report = {
        "schema_version": "1.0.0",
        "stage_id": "stage2_swamp_dock_v02",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE),
        "output": str(args.output.relative_to(ROOT)),
        "output_sha256": sha256(args.output),
        "source_kind": "ai_generated_original_candidate",
        "provenance": "imagegen_reauthored_from_local_stage2_v01_composition; original prompt persisted in stage2_prompt_v02.txt",
        "dimensions": [OUT_W, OUT_H],
        "pre_tile_block": args.block,
        "tile_reuse_mode": "global_legacy" if args.global_reuse else "regional_material_preserving",
        "palette_snap": "Mega Drive 9-bit, step 34",
        "palette_rgb": palette[:15],
        "useful_palette_entries": len(set(palette[:15])),
        "unique_tiles_before_reuse": unique_before,
        "unique_tiles_after_reuse": unique_after,
        "tile_budget": TILE_BUDGET,
        "claim_ceiling": "translated_stage_candidate",
        "visual_review_required": True,
        "emulator_validated": False,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
