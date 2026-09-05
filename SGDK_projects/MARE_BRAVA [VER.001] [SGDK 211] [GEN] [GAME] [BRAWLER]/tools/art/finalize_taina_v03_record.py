#!/usr/bin/env python3
"""Bind the assembled TAINA record to v03 measurement and review evidence."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "doc/art/characters/taina/native_sprite_production_record.json"
MANIFEST = ROOT / "rascunho/taina_visual_challengers_v03/candidates/challenger_package_manifest.json"
BUDGET = ROOT / "rascunho/taina_visual_challengers_v03/scale_budget_report_v03.json"


def main() -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    budget = json.loads(BUDGET.read_text(encoding="utf-8"))
    selected_id = record["asset_id"]
    item = next(candidate for candidate in manifest["candidates"] if candidate["asset_id"] == selected_id)
    measured = next(scale for scale in budget["scales"] if scale["asset_id"] == selected_id)
    record["schema_version"] = "1.3.0"
    record["scale_contract"]["probes"] = []
    for probe_id in (selected_id, "taina_64x96_challenger_b"):
        probe = next(candidate for candidate in manifest["candidates"] if candidate["asset_id"] == probe_id)
        record["scale_contract"]["probes"].append({
            "width": probe["width"], "height": probe["height"], "path": probe["candidate_path"],
            "technical_status": "passed", "visual_status": "pending", "promotable": False,
        })
    record["native_candidate"]["foreground_matte_report"] = item["foreground_matte_report_path"]
    record["native_candidate"]["visual_evidence"]["candidate_sha256"] = item["candidate_sha256"]
    record["native_candidate"]["visual_evidence"]["native_1x"] = item["native_1x_path"]
    record["native_candidate"]["visual_evidence"]["nearest_preview"] = item["nearest_path"]
    record["native_candidate"]["visual_evidence"]["light_background"] = item["light_path"]
    record["native_candidate"]["visual_evidence"]["dark_background"] = item["dark_path"]
    record["native_candidate"]["visual_evidence"]["chroma_background"] = item["chroma_path"]
    record["native_candidate"]["shape_block_contract"]["semantic_region_map"] = item["shape_artifacts"]["semantic_region_map"]
    record["native_candidate"]["shape_block_contract"]["semantic_label_counts"] = item["semantic_label_counts"]
    record["producer_output"]["path"] = item["candidate_path"]
    record["producer_output"]["visible_rgb_colors"] = json.loads((ROOT / item["pixel_report_path"]).read_text(encoding="utf-8"))["visible_colors"]
    record["gates"].update({
        "semantic_parse": "passed",
        "lineart": "in_progress",
        "color_blocking": "in_progress",
        "palette_lock": "in_progress",
        "pixel_contract": "passed",
        "native_visual": "in_progress",
        "scale": "in_progress",
        "budget": "passed",
        "human": "not_started",
        "sgdk_integration": "not_started",
        "emulator": "not_started",
    })
    record["scale_report"] = {
        "status": "pending", "camera_width": 320, "camera_height": 224,
        "hitbox": "undeclared_requires_collision_contract",
        "notes": "v03 corrected camera comparison; 48x64 vs 64x96 remains a human scale decision",
        "probes": str(BUDGET.relative_to(ROOT)),
    }
    record["budget_report"] = {
        "status": "passed", "tiles": measured["tile_metrics"]["unique_tiles"],
        "scanline_px": measured["scenarios"]["hero_plus_four_enemies"]["max_sprite_pixels_per_scanline"],
        "notes": "v03 corrected vdp_scanline_simulator 1.2.0; required 4-enemy case passes, 6-enemy next degree overflows pixels; see scale_budget_report_v03.json",
    }
    record["visual_report"] = {
        "status": "pending", "sha256": item["candidate_sha256"],
        "notes": "v03 panel is evidence for human review; no aesthetic score or automatic recommendation",
    }
    record["status"] = "technical_candidate"
    record["next_action"] = "human_gate_select_asset_id_sha256_and_scale_before_native_refinement_animation_or_res"
    record["promotion"] = {"promotable": False, "target": "none"}
    RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(RECORD), "asset_id": selected_id, "status": record["status"], "promotable": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
