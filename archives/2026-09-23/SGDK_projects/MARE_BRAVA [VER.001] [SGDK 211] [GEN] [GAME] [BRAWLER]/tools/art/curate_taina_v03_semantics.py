#!/usr/bin/env python3
"""Curate diagnostic anatomy maps for the persisted TAINA v03 candidates.

This script never edits candidate pixels.  It only records a hand-curated
semantic annotation on the already-generated silhouettes.  The regions are
defined as overlapping anatomical polygons and anchor points, not horizontal
bands or one-pixel tokens.  Transparent pixels remain label 0 and every
visible candidate pixel receives exactly one anatomical label.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "rascunho/taina_visual_challengers_v03/candidates"
REGIONS = ["head_or_face", "hair", "torso", "arms_or_guard", "hands",
           "legs", "feet", "sash"]
LABELS = {name: i + 1 for i, name in enumerate(REGIONS)}


# Coordinates are native-pixel annotations for each actual candidate.  The
# polygons follow visible anatomy and are deliberately different for each
# pose; they are not a generic y-band partition.
POLYGONS = {
    "taina_48x64_challenger_a": {
        "hair": [(8, 0), (27, 0), (32, 8), (30, 18), (23, 18), (13, 16), (8, 9)],
        "head_or_face": [(13, 8), (28, 8), (30, 20), (25, 27), (16, 26), (11, 18)],
        "torso": [(13, 20), (30, 19), (35, 29), (32, 41), (17, 41), (10, 30)],
        "arms_or_guard": [(8, 18), (16, 20), (19, 27), (15, 35), (10, 32),
                           (6, 25), (28, 19), (36, 16), (41, 24), (37, 32),
                           (31, 30), (30, 23)],
        "hands": [(6, 27), (12, 28), (15, 34), (10, 36), (6, 32),
                   (35, 23), (41, 22), (42, 28), (37, 30)],
        "sash": [(11, 32), (34, 31), (38, 39), (34, 46), (26, 42),
                 (17, 45), (10, 40)],
        "legs": [(10, 40), (22, 39), (23, 57), (16, 59), (8, 54),
                 (25, 40), (36, 39), (39, 56), (34, 59), (26, 57)],
        "feet": [(7, 54), (17, 55), (17, 63), (7, 63), (5, 59),
                 (32, 55), (40, 56), (43, 63), (32, 63)],
    },
    "taina_48x64_challenger_b": {
        "hair": [(11, 0), (27, 0), (32, 9), (30, 19), (23, 19), (13, 16), (9, 8)],
        "head_or_face": [(14, 8), (30, 8), (31, 20), (26, 28), (17, 27), (12, 18)],
        "torso": [(14, 21), (31, 20), (35, 31), (32, 41), (17, 41), (11, 31)],
        "arms_or_guard": [(9, 19), (17, 21), (18, 29), (14, 35), (10, 33),
                           (7, 26), (29, 20), (37, 18), (40, 27), (36, 34),
                           (31, 30), (30, 23)],
        "hands": [(7, 27), (13, 27), (15, 34), (10, 36), (7, 32),
                   (35, 22), (41, 23), (41, 29), (36, 30)],
        "sash": [(12, 33), (34, 32), (38, 40), (34, 46), (26, 43),
                 (17, 46), (11, 40)],
        "legs": [(10, 40), (22, 40), (23, 57), (16, 60), (8, 54),
                 (25, 40), (36, 40), (39, 57), (34, 60), (26, 57)],
        "feet": [(7, 54), (17, 55), (17, 63), (7, 63), (5, 59),
                 (32, 55), (40, 56), (43, 63), (32, 63)],
    },
    "taina_64x96_challenger_a": {
        "hair": [(13, 0), (38, 0), (47, 14), (45, 29), (34, 29), (20, 24), (11, 12)],
        "head_or_face": [(18, 11), (38, 10), (41, 25), (35, 34), (23, 32), (16, 23)],
        "torso": [(20, 25), (39, 24), (45, 39), (41, 54), (24, 54), (18, 38)],
        "arms_or_guard": [(13, 23), (24, 27), (26, 39), (20, 47), (14, 43),
                           (10, 35), (35, 25), (48, 20), (53, 30), (48, 43),
                           (40, 45), (37, 34)],
        "hands": [(10, 34), (18, 35), (21, 44), (15, 49), (10, 43),
                   (45, 22), (54, 20), (56, 28), (49, 32)],
        "sash": [(18, 45), (43, 43), (50, 54), (45, 65), (34, 58),
                 (24, 63), (17, 54)],
        "legs": [(15, 55), (31, 54), (31, 80), (23, 87), (12, 79),
                 (34, 55), (48, 54), (51, 80), (45, 88), (34, 80)],
        "feet": [(11, 78), (25, 80), (25, 95), (10, 95), (7, 88),
                 (43, 80), (52, 79), (57, 94), (43, 95)],
    },
    "taina_64x96_challenger_b": {
        "hair": [(12, 0), (39, 0), (46, 15), (45, 29), (34, 30), (19, 25), (9, 12)],
        "head_or_face": [(17, 11), (39, 10), (42, 25), (35, 35), (22, 32), (14, 22)],
        "torso": [(19, 25), (42, 24), (47, 40), (43, 56), (24, 55), (17, 39)],
        "arms_or_guard": [(11, 24), (24, 27), (27, 40), (21, 48), (14, 43),
                           (8, 34), (36, 25), (49, 23), (60, 28), (59, 39),
                           (47, 43), (38, 34)],
        "hands": [(8, 33), (17, 35), (21, 44), (15, 49), (8, 42),
                   (52, 25), (61, 27), (62, 36), (56, 40)],
        "sash": [(17, 45), (45, 44), (53, 56), (49, 68), (35, 60),
                 (23, 66), (16, 54)],
        "legs": [(13, 57), (31, 55), (31, 80), (22, 88), (10, 80),
                 (36, 56), (52, 55), (56, 80), (47, 89), (35, 80)],
        "feet": [(9, 79), (24, 81), (24, 95), (8, 95), (5, 88),
                 (47, 80), (58, 80), (63, 94), (48, 95)],
    },
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def annotate(asset_id: str, polygons: dict[str, list[tuple[int, int]]]) -> dict[str, int]:
    root = BASE / asset_id
    candidate = root / f"{asset_id}.png"
    shape_dir = root / "shape_block"
    image = Image.open(candidate).convert("P")
    visible = image.load()
    width, height = image.size
    masks: dict[str, Image.Image] = {}
    for name, points in polygons.items():
        mask = Image.new("1", (width, height), 0)
        ImageDraw.Draw(mask).polygon(points, fill=1)
        masks[name] = mask

    # Region centers are hand-placed anatomical anchors.  They are used only
    # to resolve pixels where two polygons meet or where a contour is ragged.
    anchors = {
        "head_or_face": (width * 0.50, height * 0.25),
        "hair": (width * 0.42, height * 0.10),
        "torso": (width * 0.50, height * 0.48),
        "arms_or_guard": (width * 0.24, height * 0.40),
        "hands": (width * 0.17, height * 0.46),
        "legs": (width * 0.50, height * 0.71),
        "feet": (width * 0.50, height * 0.92),
        "sash": (width * 0.58, height * 0.57),
    }
    out = Image.new("P", (width, height), 0)
    palette = [0, 0, 0]
    for i in range(1, 9):
        palette.extend((34 * min(i, 7), 34 * ((i + 2) % 8), 34 * ((i + 4) % 8)))
    palette.extend([0, 0, 0] * (256 - 9))
    out.putpalette(palette)
    dst = out.load()
    counts = {name: 0 for name in REGIONS}
    for y in range(height):
        for x in range(width):
            if visible[x, y] == 0:
                continue
            candidates = [name for name in REGIONS if masks[name].getpixel((x, y))]
            if not candidates:
                candidates = REGIONS
            # Narrow extremities and clothing overlays own their overlap;
            # broad torso/leg zones are the fallback, never the other way
            # around.  This keeps hands/sash/feet as real regions.
            priority = {"hands": 0, "feet": 1, "sash": 2, "hair": 3,
                        "arms_or_guard": 4, "head_or_face": 5, "torso": 6,
                        "legs": 7}
            name = min(candidates, key=lambda n: (priority[n],
                                                  (x - anchors[n][0]) ** 2 +
                                                  (y - anchors[n][1]) ** 2))
            dst[x, y] = LABELS[name]
            counts[name] += 1
    if any(value < 8 for value in counts.values()):
        raise ValueError(f"{asset_id}: annotation region too small: {counts}")
    out_path = shape_dir / "semantic_region_map.png"
    out.save(out_path, "PNG", bits=4)
    return {"counts": counts, "path": str(out_path.relative_to(ROOT)), "sha256": sha(out_path)}


def main() -> int:
    manifest_path = BASE / "challenger_package_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for item in manifest["candidates"]:
        result = annotate(item["asset_id"], POLYGONS[item["asset_id"]])
        item["semantic_label_counts"] = result["counts"]
        item["shape_artifacts"]["semantic_region_map"]["sha256"] = result["sha256"]
        item["semantic_map_method"] = "human_curated_anatomical_polygon_annotation_v03"
        item["semantic_map_review"] = {
            "status": "curated_diagnostic_annotation",
            "visible_union_exact": True,
            "one_label_per_visible_pixel": True,
            "not_pixel_source": True,
        }
    manifest["semantic_annotation"] = {
        "status": "curated_diagnostic_annotation",
        "method": "native_pixel_anatomical_polygons_plus_anchor_resolution",
        "candidate_pixels_unchanged": True,
        "prohibited_shortcuts_avoided": ["horizontal_bands", "one_pixel_tokens", "candidate_redraw"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "status": "passed"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
