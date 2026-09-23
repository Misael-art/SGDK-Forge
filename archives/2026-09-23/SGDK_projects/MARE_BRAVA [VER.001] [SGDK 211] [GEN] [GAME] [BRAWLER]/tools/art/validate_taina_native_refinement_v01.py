#!/usr/bin/env python3
"""Validate TAINA BASIC/ELITE refinement candidates and inherited shape block."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "rascunho/taina_native_refinement_v01"
MANIFEST = BASE / "native_refinement_manifest_v01.json"
APPROVED = ROOT / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b/taina_48x64_challenger_b.png"
APPROVED_SHA = "d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa"
SHAPE_DIR = ROOT / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b/shape_block"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def alpha_mask(path: Path) -> bytes:
    return bytes(1 if value != 0 else 0 for value in Image.open(path).convert("P").getdata())


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    approved = Image.open(APPROVED).convert("RGBA")
    checks: dict[str, object] = {
        "approved_source_sha_matches": sha(APPROVED) == APPROVED_SHA,
        "candidates": [],
        "res_touched": False,
        "automatic_winner": None,
    }
    for name, item in manifest["outputs"].items():
        path = Path(item["path"])
        if not path.is_absolute():
            path = ROOT.parents[1] / path
        image = Image.open(path).convert("P")
        rgba = Image.open(path).convert("RGBA")
        visible = {pixel[:3] for pixel in rgba.getdata() if pixel[3] != 0}
        evidence = {key: ROOT / value for key, value in item["evidence"].items()}
        shape_paths = {key: ROOT / value for key, value in item["shape_block"].items() if key != "matte_report"}
        silhouette = Image.open(shape_paths["silhouette_mask"]).convert("P")
        semantic = Image.open(shape_paths["semantic_region_map"]).convert("P")
        contour = Image.open(shape_paths["contour_overlay"]).convert("P")
        matte = json.loads((ROOT / item["shape_block"]["matte_report"]).read_text(encoding="utf-8"))
        candidate_alpha = alpha_mask(path)
        shape_passed = (
            silhouette.size == (48, 64)
            and semantic.size == (48, 64)
            and contour.size == (48, 64)
            and bytes(1 if value != 0 else 0 for value in silhouette.getdata()) == candidate_alpha
            and bytes(1 if value != 0 else 0 for value in semantic.getdata()) == candidate_alpha
            and set(value for value in semantic.getdata() if value != 0) >= set(range(1, 9))
            and matte.get("status") == "passed"
        )
        candidate = {
            "name": name,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha(path),
            "manifest_sha_matches": sha(path) == item["sha256"],
            "size": list(image.size),
            "size_passed": image.size == (48, 64),
            "alpha_binary": set(pixel[3] for pixel in rgba.getdata()) <= {0, 255},
            "visible_colors": len(visible),
            "visible_colors_passed": len(visible) <= 15,
            "silhouette_preserved_pixel_for_pixel": candidate_alpha == alpha_mask(APPROVED),
            "native_1x_byte_identical": evidence["native_1x"].read_bytes() == path.read_bytes(),
            "nearest_dimensions": list(Image.open(evidence["nearest_8x"]).size),
            "shape_block_reused_from": "taina_48x64_challenger_b",
            "shape_block_source_sha256": APPROVED_SHA,
            "shape_block_valid": shape_passed,
            "matte_report_valid": matte.get("status") == "passed",
        }
        candidate["shape_block_artifacts"] = {
            key: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
            for key, path in shape_paths.items()
        }
        checks["candidates"].append(candidate)

    checks["status"] = "passed" if checks["approved_source_sha_matches"] and all(
        c["manifest_sha_matches"] and c["size_passed"] and c["alpha_binary"] and c["visible_colors_passed"] and c["silhouette_preserved_pixel_for_pixel"] and c["native_1x_byte_identical"] and c["nearest_dimensions"] == [384, 512] and c["shape_block_valid"] and c["matte_report_valid"]
        for c in checks["candidates"]
    ) else "failed"
    checks["human_visual_gate"] = "not_started"
    checks["promotion"] = "blocked_until_basic_elite_visual_decision"
    out = BASE / "native_refinement_validation_report_v01.json"
    out.write_text(json.dumps(checks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest["validation_report"] = str(out.relative_to(ROOT))
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": checks["status"], "report": str(out), "candidates": len(checks["candidates"])}, indent=2))
    return 0 if checks["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
