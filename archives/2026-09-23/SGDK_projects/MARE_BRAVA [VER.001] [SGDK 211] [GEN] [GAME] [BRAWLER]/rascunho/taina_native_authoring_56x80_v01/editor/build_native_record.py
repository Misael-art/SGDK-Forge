#!/usr/bin/env python3
"""Seal the current native candidate into the operational project record."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def ref(root, path, role=None):
    item = {"path": str(path.relative_to(root)), "sha256": sha(path)}
    if role:
        item["role"] = role
    return item


def artifact(root, path, asset_id, source):
    return {"path": str(path.relative_to(root)), "sha256": sha(path), "asset_id": asset_id,
            "scale": "56x80", "source": str(source.relative_to(root))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root.resolve()
    out = args.output.resolve()
    aid = "taina_idle_guard_56x80_native_authoring_v04"
    candidate = root / "rascunho/taina_native_authoring_56x80_v01/exports/taina_idle_guard_56x80_native_authoring_v04.png"
    action_log = root / "rascunho/taina_native_authoring_56x80_v01/exports/taina_idle_guard_56x80_native_authoring_v04.actions.json"
    evidence_root = root / "rascunho/taina_native_authoring_56x80_v01/candidate_v04"
    model = root / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
    direction = root / "data/source_art/visual_producer_outputs/taina_idle_guard_scale_shootout_v01/taina_idle_guard_56x80_visual_source_v01.png"
    challenger = root / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b/taina_48x64_challenger_b.png"
    probe64 = root / "data/source_art/visual_producer_outputs/taina_idle_guard_scale_shootout_v01/taina_idle_guard_64x96_visual_source_v01.png"
    shootout = root / "doc/art/characters/taina/native_scale_shootout_record_v01.json"
    for path in [candidate, action_log, model, direction, challenger, probe64, shootout]:
        if not path.is_file():
            raise FileNotFoundError(path)
    pixel = json.loads((evidence_root / "pixel_compliance_report.json").read_text(encoding="utf-8"))
    shape_report = json.loads((evidence_root / "shape_semantic_map_report.json").read_text(encoding="utf-8"))
    material = json.loads((evidence_root / "material_region_contract.json").read_text(encoding="utf-8"))
    review = evidence_root / "native_visual_review_report.json"
    review_doc = json.loads(review.read_text(encoding="utf-8"))
    material.pop("schema_version", None)
    material.pop("asset_id", None)
    material["material_region_map"] = artifact(root, evidence_root / "material_region_map.png", aid, candidate)
    material["material_boundary_overlay"] = artifact(root, evidence_root / "material_boundary_overlay.png", aid, candidate)
    shape = {
        "silhouette_mask": artifact(root, evidence_root / "shape_block/silhouette_mask.png", aid, candidate),
        "semantic_region_map": artifact(root, evidence_root / "shape_block/semantic_region_map.png", aid, candidate),
        "contour_overlay": artifact(root, evidence_root / "shape_block/contour_overlay.png", aid, candidate),
        "required_semantic_regions": shape_report["required_regions"],
        "semantic_label_legend": shape_report["label_legend"],
        "semantic_label_counts": shape_report["label_counts"],
        "occupancy_metrics": {"filled_pixels": shape_report["filled_pixels"], "canvas_pixels": 56 * 80, "occupancy_pct": shape_report["occupancy_pct"]},
        "bbox": shape_report["bbox"],
        "reason_codes": ["explicit_native_grid_authoring", "agent_curated_diagnostic_annotation", "no_source_pixel_copy"],
    }
    record = {
        "schema_version": "1.4.0",
        "asset_id": aid,
        "asset_kind": "sprite_single",
        "source": {**ref(root, model), "classification": "concept_high_res", "approval_status": "approved_source"},
        "scale_contract": {
            "status": "locked", "target_width": 56, "target_height": 80, "selected_width": 56, "selected_height": 80,
            "probes": [
                {"width": 56, "height": 80, "path": str(candidate.relative_to(root)), "technical_status": "passed", "visual_status": "pending", "promotable": False},
                {"width": 48, "height": 64, "path": str(challenger.relative_to(root)), "technical_status": "passed", "visual_status": "pending", "promotable": False},
                {"width": 64, "height": 96, "path": str(probe64.relative_to(root)), "technical_status": "passed", "visual_status": "pending", "promotable": False},
            ],
        },
        "scale_report": {"status": "passed", "camera_width": 320, "camera_height": 224, "hitbox": "design_seed_16x40_not_gameplay_confirmed", "notes": "56x80 locked by human scale decision; 48x64 and 64x96 remain comparison probes only.", "probes": "scale_contract.probes"},
        "producer_output": {"path": str(candidate.relative_to(root)), "role": "native_candidate", "interaction_channel": "cli_headless", "width": 56, "height": 80, "mode": "P", "visible_rgb_colors": 15, "alpha_values": [0, 255]},
        "provenance": {"interaction_channel": "agent_operated_native_editor_draft", "source_kind": "ai_authored_pixel", "producer_identity": "Codex local native editor route", "action_log": str(action_log.relative_to(root)), "human_approval": "pending_human_decision:not_recorded"},
        "native_candidate": {
            "path": str(candidate.relative_to(root)), "method": "authored_native_pixel", "width": 56, "height": 80,
            "pixel_report": str((evidence_root / "pixel_compliance_report.json").relative_to(root)),
            "visual_evidence": {
                "candidate_sha256": sha(candidate), "native_1x": str((evidence_root / "evidence/native_1x.png").relative_to(root)), "nearest_preview": str((evidence_root / "evidence/nearest_8x.png").relative_to(root)), "light_background": str((evidence_root / "evidence/light_background.png").relative_to(root)), "dark_background": str((evidence_root / "evidence/dark_background.png").relative_to(root)), "chroma_background": str((evidence_root / "evidence/chroma_background.png").relative_to(root)), "preview_scale": 8, "light_rgb": [238, 238, 230], "dark_rgb": [28, 30, 38], "chroma_rgb": [238, 0, 238], "human_approval": "pending_human_decision:not_recorded"
            },
            "shape_block_contract": shape,
            "material_region_contract": material,
        },
        "palette_contract": {"max_visible_colors": 15, "index0_role": "transparent0", "outline_role": "shared_warm_dark_outline", "material_roles": list(material["material_label_legend"].keys())},
        "gates": {"semantic_parse": "passed", "lineart": "passed", "color_blocking": "passed", "material_topology": "passed", "palette_lock": "passed", "pixel_contract": "passed", "native_visual": "in_progress", "scale": "passed", "budget": "in_progress", "human": "in_progress", "sgdk_integration": "not_started", "emulator": "not_started"},
        "runtime_evidence": None,
        "budget_report": {"status": "pending", "tiles": 48, "scanline_px": 264, "notes": "planning_budget only; corrected report is rascunho/taina_native_authoring_56x80_v01/budget/native_scale_runtime_budget_report_v01.json; no native sprite in ROM/res and no validado_budget claim."},
        "visual_report": {"status": "pending", "sha256": sha(review), "notes": "Qualitative comparison only; human visual gate remains open. Route recovery is in progress; claim ceiling is native_candidate_pending_human_decision."},
        "incumbent": {**ref(root, challenger), "role": "comparison_only"},
        "methodology_reference": {**ref(root, shootout), "role": "methodology_reference"},
        "status": "technical_candidate",
        "next_action": "status=in_progress_native_authoring_route_recovery; pending_human_decision_on_native_pose_v04; do not start animation or promotion",
        "promotion": {"promotable": False, "target": "none"},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(out.relative_to(root)), "candidate_sha256": sha(candidate), "action_log_sha256": sha(action_log), "visual_report_sha256": sha(review)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
