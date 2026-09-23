#!/usr/bin/env python3
"""Reconcile v03 provenance, annotation naming, budget scope and scale lock."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V02 = ROOT / "rascunho/taina_visual_challengers_v02/candidates/challenger_package_manifest.json"
V03 = ROOT / "rascunho/taina_visual_challengers_v03/candidates/challenger_package_manifest.json"
BUDGET = ROOT / "rascunho/taina_visual_challengers_v03/scale_budget_report_v03.json"
RECORD = ROOT / "doc/art/characters/taina/native_sprite_production_record.json"
APPROVAL = ROOT / "doc/art/characters/taina/human_direction_scale_decision_v03.json"
MODEL = "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
APPROVED_SHA = "d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa"


def main() -> int:
    v02 = json.loads(V02.read_text(encoding="utf-8"))
    v03 = json.loads(V03.read_text(encoding="utf-8"))
    budget = json.loads(BUDGET.read_text(encoding="utf-8"))
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    approval = json.loads(APPROVAL.read_text(encoding="utf-8"))

    if approval["sha256"] != APPROVED_SHA or approval["scale"] != "48x64":
        raise SystemExit("human approval does not match the exact B/48x64 decision")

    v02_by_id = {item["asset_id"]: item for item in v02["candidates"]}
    v03["identity_source"] = {"path": MODEL, "sha256": MODEL_SHA, "role": "approved_model_sheet_identity_source"}
    v03["translation_input_sources"] = []
    for item in v03["candidates"]:
        source = v02_by_id[item["asset_id"]]
        v03["translation_input_sources"].append({
            "asset_id": item["asset_id"],
            "path": source["source_path"],
            "sha256": source["source_sha256"],
            "role": "producer_output_persisted_v02",
            "used_as": "translation_input_only",
        })
        item["semantic_map_method"] = "agent_curated_diagnostic_annotation"
        item["semantic_map_review"]["status"] = "agent_curated_diagnostic_annotation"
        item["comparison_only"] = item["scale"] == "64x96"
    v03["generation_source"] = "identity_model_sheet_plus_persisted_v02_producer_outputs"
    v03["semantic_annotation"] = {
        "method": "agent_curated_diagnostic_annotation",
        "role": "diagnostic_shape_contract_not_human_visual_approval",
        "visible_union_exact": True,
        "one_label_per_visible_pixel": True,
    }
    v03["scale_contract"] = {
        "status": "locked",
        "selected_scale": "48x64",
        "selected_asset_id": "taina_48x64_challenger_b",
        "comparison_only_scales": ["64x96"],
        "human_decision": str(APPROVAL.relative_to(ROOT)),
    }
    v03["budget_pass_scope"] = "static_scale_case_taina_plus_four_enemies_only"
    v03["review_only"] = True
    V03.write_text(json.dumps(v03, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    budget["measurement_scope"] = "TAINA static scale case + 2 CRIA + 2 ESTIVADOR (four enemies only)"
    budget["budget_pass_scope"] = "hero_plus_four_enemies_only"
    budget["next_degree"] = {
        "status": "comparison_only_not_budget_pass",
        "scenario": "3 CRIA + 3 ESTIVADOR",
        "note": "Retained as measured ambition evidence; cannot change the four-enemy budget_pass."
    }
    budget["decision"] = {
        "scale_lock": "48x64 locked by human direction/scale decision; 64x96 comparison_only",
        "budget_pass": "static TAINA + four enemies only",
        "next_degree": "comparison_only; measured overflow does not invalidate the required four-enemy case",
    }
    BUDGET.write_text(json.dumps(budget, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    record["scale_contract"]["status"] = "locked"
    record["scale_contract"]["selected_width"] = 48
    record["scale_contract"]["selected_height"] = 64
    record["scale_report"]["notes"] = "48x64 locked by exact human direction/scale decision for this slice; 64x96 remains comparison_only."
    record["budget_report"]["notes"] = "budget_pass is limited to static TAINA + four enemies; next degree 3+3 is comparison_only evidence."
    record["next_action"] = "complete_native_refinement_basic_elite_then_open_new_visual_gate_before_animation_or_res"
    record["promotion"] = {"promotable": False, "target": "none"}
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"v03": "reconciled", "identity_source": MODEL, "translation_inputs": len(v03["translation_input_sources"]), "annotation": v03["semantic_annotation"]["method"], "scale_lock": "48x64", "comparison_only": ["64x96"], "budget_pass_scope": budget["budget_pass_scope"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
