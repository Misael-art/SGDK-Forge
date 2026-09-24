#!/usr/bin/env python3
"""Assemble the review-only TAINA native-sprite production record."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--record", type=Path, required=True)
    ap.add_argument("--selected-asset-id", required=True,
                    help="Explicit human/curator selection; no implicit challenger default")
    ap.add_argument("--comparison-asset-id",
                    help="Optional measured scale challenger kept as comparison_only")
    args = ap.parse_args()
    root = args.project_root.resolve()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    candidates = {item["asset_id"]: item for item in manifest["candidates"]}
    if args.selected_asset_id not in candidates:
        raise SystemExit(f"unknown selected asset_id: {args.selected_asset_id}")
    if args.comparison_asset_id and args.comparison_asset_id not in candidates:
        raise SystemExit(f"unknown comparison asset_id: {args.comparison_asset_id}")
    selected = candidates[args.selected_asset_id]
    comparison = candidates.get(args.comparison_asset_id) if args.comparison_asset_id else None
    record_asset_id = args.selected_asset_id
    candidate = root / selected["candidate_path"]
    pixel_doc = json.loads((root / selected["pixel_report_path"]).read_text(encoding="utf-8"))
    with Image.open(candidate) as img:
        mode = img.mode
        alpha_values = sorted({0 if idx == 0 else 255 for idx in img.tobytes()}) if mode == "P" else sorted(set(img.convert("RGBA").getchannel("A").getdata()))
        visible = [(i % img.width, i // img.width) for i, idx in enumerate(img.tobytes()) if idx != 0]
        bbox = [min(x for x, _ in visible), min(y for _, y in visible), max(x for x, _ in visible) + 1, max(y for _, y in visible) + 1]
        filled = len(visible)
    old = json.loads(args.record.read_text(encoding="utf-8"))
    source = old["source"]
    incumbent = old["incumbent"]
    methodology = old["methodology_reference"]
    shape = {}
    for role, artifact in selected["shape_artifacts"].items():
        shape[role] = dict(artifact, asset_id=record_asset_id)
    selected_w, selected_h = int(selected["width"]), int(selected["height"])
    probes = [{"width": selected_w, "height": selected_h,
               "path": selected["candidate_path"], "technical_status": "passed",
               "visual_status": "pending", "promotable": False}]
    if comparison:
        probes.append({"width": int(comparison["width"]), "height": int(comparison["height"]),
                       "path": comparison["candidate_path"], "technical_status": "passed",
                       "visual_status": "pending", "promotable": False})
    shape_contract = {
        **shape,
        "required_semantic_regions": list(selected["semantic_label_legend"]),
        "semantic_label_legend": selected["semantic_label_legend"],
        "semantic_label_counts": selected["semantic_label_counts"],
        "occupancy_metrics": {"filled_pixels": filled,
                               "canvas_pixels": selected_w * selected_h,
                               "occupancy_pct": round(filled / (selected_w * selected_h) * 100, 2)},
        "bbox": bbox,
        "reason_codes": ["review_only", "assisted_native_translation", "human_visual_gate_pending"]
    }
    record = {
        "schema_version": "1.3.0", "asset_id": record_asset_id, "asset_kind": "sprite_single",
        "source": source,
        "scale_contract": {
            "status": "provisional", "target_width": selected_w, "target_height": selected_h,
            "selected_width": selected_w, "selected_height": selected_h,
            "probes": probes
        },
        "producer_output": {"path": selected["candidate_path"], "role": "native_candidate",
                            "interaction_channel": "native_image_tool", "width": 48, "height": 64,
                            "mode": mode, "visible_rgb_colors": pixel_doc["visible_colors"], "alpha_values": alpha_values},
        "native_candidate": {
            "path": selected["candidate_path"], "method": "assisted_native_translation",
            "width": selected_w, "height": selected_h, "pixel_report": selected["pixel_report_path"],
            "foreground_matte_report": selected["foreground_matte_report_path"],
            "visual_evidence": {"candidate_sha256": selected["candidate_sha256"],
                "native_1x": selected["native_1x_path"], "nearest_preview": selected["nearest_path"],
                "light_background": selected["light_path"], "dark_background": selected["dark_path"],
                "chroma_background": selected["chroma_path"],
                "preview_scale": 8, "light_rgb": [238, 238, 230], "dark_rgb": [28, 30, 38],
                "chroma_rgb": [238, 0, 238],
                "human_approval": ""},
            "shape_block_contract": shape_contract
        },
        "palette_contract": {"max_visible_colors": 15, "index0_role": "transparent0",
                             "outline_role": "single dark marine/purple ink",
                             "material_roles": ["skin", "orange_top", "teal_wraps", "indigo_trousers", "sash"]},
        "gates": {"semantic_parse": "in_progress", "lineart": "in_progress", "color_blocking": "in_progress",
                  "palette_lock": "in_progress", "pixel_contract": "passed", "native_visual": "in_progress",
                  "scale": "in_progress", "budget": "in_progress", "human": "not_started",
                  "sgdk_integration": "not_started", "emulator": "not_started"},
        "runtime_evidence": None,
        "promotion": {"promotable": False, "target": "none"},
        "status": "technical_candidate", "next_action": "validate_matte_semantic_regions_and_budget_before_human_gate",
        "provenance": {"interaction_channel": "native_image_tool", "source_kind": "ai_authored_pixel",
                        "producer_identity": "openai_native_image_generation",
                        "action_log": "doc/contracts/generation_channel_decision.json; approved_model_sheet_only",
                        "human_approval": ""},
        "scale_report": {"status": "pending", "camera_width": 320, "camera_height": 224,
                          "hitbox": "undeclared_requires_collision_contract", "notes": "explicitly selected probe plus optional comparison; visual scale decision pending",
                          "probes": "rascunho/taina_visual_challengers_v02/scale_budget_report.json"},
        "budget_report": {"status": "pending",
                          "notes": "corrected hardware-cell VDP report required before human selection"},
        "visual_report": {"status": "pending", "sha256": selected["candidate_sha256"],
                           "notes": "comparison panel and perceptual/system scoring pending human gate"},
        "incumbent": incumbent,
        "methodology_reference": methodology
    }
    args.record.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(args.record), "asset_id": record_asset_id,
                      "candidate_sha256": selected["candidate_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
