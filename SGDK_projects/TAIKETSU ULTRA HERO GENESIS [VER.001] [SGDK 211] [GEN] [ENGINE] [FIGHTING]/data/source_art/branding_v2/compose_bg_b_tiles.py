#!/usr/bin/env python3
"""Rebuild forge BG_B from authored 8x8 crops until unique tiles fit the budget.

Every output pixel comes from an 8x8 crop of the remapped source (or an H/V
flip of that crop). No primitive drawing.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

TARGET_UNIQUE = 644
FIRE_ROW0 = 21  # y >= 168
COLS = 40
ROWS = 28


def _flip_h(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        row = tile[y * 8 : y * 8 + 8]
        out[y * 8 : y * 8 + 8] = row[::-1]
    return bytes(out)


def _flip_v(tile: bytes) -> bytes:
    out = bytearray(64)
    for y in range(8):
        out[y * 8 : y * 8 + 8] = tile[(7 - y) * 8 : (7 - y) * 8 + 8]
    return bytes(out)


def orientations(tile: bytes) -> list[bytes]:
    h = _flip_h(tile)
    v = _flip_v(tile)
    return [tile, h, v, _flip_h(v)]


def l1(a: bytes, b: bytes) -> int:
    return sum(abs(a[i] - b[i]) for i in range(64))


def extract_tiles(img: Image.Image) -> list[bytes]:
    px = img.load()
    tiles: list[bytes] = []
    for ty in range(ROWS):
        for tx in range(COLS):
            buf = bytearray(64)
            for y in range(8):
                for x in range(8):
                    buf[y * 8 + x] = px[tx * 8 + x, ty * 8 + y]
            tiles.append(bytes(buf))
    return tiles


def count_unique(tiles: list[bytes], *, flips: bool = True) -> int:
    seen: set[bytes] = set()
    for tile in tiles:
        keys = orientations(tile) if flips else [tile]
        canon = min(keys)
        if canon not in seen:
            seen.add(canon)
    return len(seen)


def zone_scale(index: int) -> float:
    ty, tx = divmod(index, COLS)
    if ty >= FIRE_ROW0:
        return 0.38
    # timber beam occupies the upper-right triangle
    if tx >= 18 and ty <= (tx - 14) // 2 + 2:
        return 0.55
    return 1.0


def _best_match(tile: bytes, medoids: list[bytes], threshold: float) -> tuple[int, int] | None:
    best_i = -1
    best_d = 10**9
    best_ori = 0
    for i, med in enumerate(medoids):
        for ori, cand in enumerate(orientations(med)):
            d = l1(tile, cand)
            if d < best_d:
                best_d = d
                best_i = i
                best_ori = ori
                if d == 0:
                    return i, ori
    if best_i >= 0 and best_d <= threshold:
        return best_i, best_ori
    return None


def cluster(tiles: list[bytes], threshold: float) -> tuple[list[bytes], list[tuple[int, int]]]:
    medoids: list[bytes] = []
    assign: list[tuple[int, int]] = []
    for i, tile in enumerate(tiles):
        scaled = threshold * zone_scale(i)
        hit = _best_match(tile, medoids, scaled)
        if hit is None:
            medoids.append(tile)
            assign.append((len(medoids) - 1, 0))
        else:
            assign.append(hit)
    return medoids, assign


def apply_assign(img: Image.Image, medoids: list[bytes], assign: list[tuple[int, int]]) -> Image.Image:
    out = img.copy()
    px = out.load()
    for index, (mid, ori) in enumerate(assign):
        ty, tx = divmod(index, COLS)
        tile = orientations(medoids[mid])[ori]
        for y in range(8):
            for x in range(8):
                px[tx * 8 + x, ty * 8 + y] = tile[y * 8 + x]
    return out


def compose_tile_budget(img: Image.Image, target: int = TARGET_UNIQUE) -> tuple[Image.Image, dict]:
    if img.mode != "P":
        raise ValueError("compose_tile_budget expects an indexed image")
    if img.size != (320, 224):
        raise ValueError(f"expected 320x224, got {img.size}")

    tiles = extract_tiles(img)
    before = {
        "raw": len(tiles),
        "unique": count_unique(tiles, flips=False),
        "unique_with_flip": count_unique(tiles, flips=True),
    }

    lo, hi = 0, 96
    best_img = img
    best_meta = {"threshold": 0, "unique_with_flip": before["unique_with_flip"]}
    # Exact-flip collapse first (threshold 0).
    for _ in range(10):
        mid = (lo + hi) / 2
        medoids, assign = cluster(tiles, mid)
        composed = apply_assign(img, medoids, assign)
        unique = count_unique(extract_tiles(composed), flips=True)
        if unique > target:
            lo = mid
        else:
            hi = mid
            best_img = composed
            best_meta = {
                "threshold": mid,
                "medoids": len(medoids),
                "unique_with_flip": unique,
            }
        if abs(unique - target) <= 8:
            best_img = composed
            best_meta = {
                "threshold": mid,
                "medoids": len(medoids),
                "unique_with_flip": unique,
            }
            break

    after_tiles = extract_tiles(best_img)
    report = {
        "before": before,
        "after": {
            "raw": len(after_tiles),
            "unique": count_unique(after_tiles, flips=False),
            "unique_with_flip": count_unique(after_tiles, flips=True),
        },
        "target_unique": target,
        "threshold": best_meta.get("threshold"),
        "medoids": best_meta.get("medoids"),
        "pixels_are_authored_crops": True,
    }
    return best_img, report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dest")
    parser.add_argument("--target", type=int, default=TARGET_UNIQUE)
    parser.add_argument("--report")
    args = parser.parse_args()
    img = Image.open(args.src)
    out, report = compose_tile_budget(img, args.target)
    Path(args.dest).parent.mkdir(parents=True, exist_ok=True)
    out.save(args.dest, format="PNG", transparency=0)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
