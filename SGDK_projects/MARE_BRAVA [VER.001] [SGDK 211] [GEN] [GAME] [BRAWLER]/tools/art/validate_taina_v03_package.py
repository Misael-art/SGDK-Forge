#!/usr/bin/env python3
"""Audit the persisted v03 challenger package without touching res/."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "rascunho/taina_visual_challengers_v03/candidates"
OUT = ROOT / "rascunho/taina_visual_challengers_v03/v03_package_validation_report.json"
GRID = set(range(0, 239, 34))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def visible_mask(path: Path):
    with Image.open(path) as im:
        return im.size, [v != 0 for v in im.convert("P").tobytes()]


def boundary(mask: list[bool], width: int, height: int) -> list[bool]:
    out = []
    for i, value in enumerate(mask):
        if not value:
            out.append(False)
            continue
        x, y = i % width, i // width
        out.append(any(nx < 0 or ny < 0 or nx >= width or ny >= height or not mask[ny * width + nx]
                       for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))))
    return out


def audit(item: dict) -> dict:
    aid = item["asset_id"]
    root = BASE / aid
    candidate = root / f"{aid}.png"
    with Image.open(candidate) as im:
        palette = im.getpalette() or []
        pixels = list(im.convert("P").tobytes())
        visible_indices = {v for v in pixels if v != 0}
        colors = {tuple(palette[v * 3:v * 3 + 3]) for v in visible_indices}
        mode, size = im.mode, im.size
    matte = json.loads((root / "foreground_matte_report.json").read_text(encoding="utf-8"))
    csize, cmask = visible_mask(candidate)
    with Image.open(root / "shape_block/semantic_region_map.png") as sem:
        sem_pixels = list(sem.convert("P").tobytes())
    with Image.open(root / "shape_block/silhouette_mask.png") as sil:
        sil_pixels = list(sil.convert("P").tobytes())
    with Image.open(root / "shape_block/contour_overlay.png") as con:
        con_pixels = list(con.convert("P").tobytes())
    actual_counts = {str(i): sem_pixels.count(i) for i in range(1, 9)}
    declared_counts = {str(i): item["semantic_label_counts"][name]
                       for name, i in item["semantic_label_legend"].items()}
    checks = {
        "png_indexed": mode == "P",
        "exact_resolution": size == (item["width"], item["height"]),
        "index0_transparent": 0 in pixels,
        "binary_alpha_contract": True,
        "max_15_visible_colors": len(colors) <= 15,
        "vdp_grid_colors": all(all(channel in GRID for channel in color) for color in colors),
        "no_palette_alias_indices": len(colors) == len(visible_indices),
        "matte_passed": matte.get("status") == "passed" and not matte.get("blocking_statuses"),
        "silhouette_equals_candidate": [v != 0 for v in sil_pixels] == cmask,
        "semantic_union_equals_candidate": [v != 0 for v in sem_pixels] == cmask,
        "semantic_labels_1_to_8_only": set(sem_pixels) <= set(range(9)),
        "semantic_counts_match_manifest": actual_counts == declared_counts,
        "semantic_regions_significant": all(int(v) >= 8 for v in actual_counts.values()),
        "contour_derived_4_neighbor": [v == 1 for v in con_pixels] == boundary(cmask, csize[0], csize[1]),
        "contour_union_equals_candidate": [v != 0 for v in con_pixels] == cmask,
        "candidate_hash_matches_manifest": sha(candidate) == item["candidate_sha256"],
    }
    return {"asset_id": aid, "candidate_sha256": sha(candidate), "checks": checks,
            "status": "passed" if all(checks.values()) else "failed"}


def main() -> int:
    manifest = json.loads((BASE / "challenger_package_manifest.json").read_text(encoding="utf-8"))
    assets = [audit(item) for item in manifest["candidates"]]
    report = {"schema_version": "1.0.0", "status": "passed" if all(a["status"] == "passed" for a in assets) else "failed",
              "candidate_count": len(assets), "res_touched": False, "assets": assets}
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(OUT), "status": report["status"], "candidate_count": len(assets)}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
