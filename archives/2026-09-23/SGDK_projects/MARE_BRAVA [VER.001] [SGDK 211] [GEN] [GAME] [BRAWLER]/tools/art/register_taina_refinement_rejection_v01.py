#!/usr/bin/env python3
"""Register the human rejection without deleting technical evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "doc/art/characters/taina/native_sprite_production_record.json"
MANIFEST = ROOT / "rascunho/taina_native_refinement_v01/native_refinement_manifest_v01.json"
DECISION = ROOT / "doc/art/characters/taina/human_refinement_rejection_v01.json"
BASIC = "e78f77d92614eb0ec2c7a0ec529d7649db025a0a793b93f3b749323708a7b403"
ELITE = "0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13"


def main() -> int:
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    rejected = {item["sha256"] for item in decision["rejected_assets"]}
    if rejected != {BASIC, ELITE} or decision["best_technical_control"]["sha256"] != ELITE:
        raise SystemExit("rejection record does not match the two exact refinement hashes")
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decision_path = str(DECISION.relative_to(ROOT))

    record["status"] = "rework"
    record["next_action"] = "change_native_refinement_hypothesis_before_new_candidate_generation; keep elite_as_technical_control; no_animation_or_res"
    record["gates"]["native_visual"] = "failed"
    record["gates"]["human"] = "failed"
    record["provenance"]["human_approval"] = decision_path
    record["native_candidate"]["visual_evidence"]["human_approval"] = decision_path
    record["visual_report"]["status"] = "pending"
    record["visual_report"]["notes"] = "Final native pose rejected: procedural palette cleanup without material-native geometry refinement. New hypothesis required."
    record["scale_report"]["notes"] = "48x64 remains locked; rejection concerns native geometry refinement, not scale. 64x96 remains comparison_only."
    record["promotion"] = {"promotable": False, "target": "none"}
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    manifest["status"] = "refinement_candidates_rejected"
    manifest["rejection"] = {
        "decision": decision["decision"],
        "reason": decision["reason"],
        "decision_record": decision_path,
        "rejected_sha256": sorted(rejected),
        "best_technical_control": decision["best_technical_control"],
    }
    manifest["review"]["human_status"] = "rejected"
    manifest["review"]["automatic_winner"] = None
    manifest["review"]["best_technical_control"] = decision["best_technical_control"]
    manifest["review"]["res_eligible"] = False
    manifest["review"]["animation_eligible"] = False
    manifest["review"]["aaa_claim_eligible"] = False
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"record_status": record["status"], "native_visual": record["gates"]["native_visual"], "human": record["gates"]["human"], "technical_control": ELITE, "scale": "48x64", "promotable": record["promotion"]["promotable"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
