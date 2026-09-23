#!/usr/bin/env python3
"""Register the human direction/scale decision without promoting the asset."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "doc/art/characters/taina/native_sprite_production_record.json"
DECISION = ROOT / "doc/art/characters/taina/human_direction_scale_decision_v03.json"
EXPECTED_ASSET = "taina_48x64_challenger_b"
EXPECTED_SHA = "d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa"


def main() -> int:
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    if decision["asset_id"] != EXPECTED_ASSET or decision["sha256"] != EXPECTED_SHA or decision["scale"] != "48x64":
        raise SystemExit("human decision does not match the approved B candidate")
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if record["asset_id"] != EXPECTED_ASSET or record["native_candidate"]["visual_evidence"]["candidate_sha256"] != EXPECTED_SHA:
        raise SystemExit("record no longer points to the approved B candidate")

    approval_path = str(DECISION.relative_to(ROOT))
    record["status"] = "native_authoring"
    record["next_action"] = "complete_native_refinement_basic_elite_then_open_new_visual_gate_before_animation_or_res"
    record["gates"]["human"] = "in_progress"
    record["scale_report"]["status"] = "passed"
    record["scale_report"]["notes"] = "Human approved 48x64 for native refinement only; BASIC/ELITE refined visual decision remains open."
    record["provenance"]["human_approval"] = approval_path
    record["native_candidate"]["visual_evidence"]["human_approval"] = approval_path
    record["visual_report"]["status"] = "pending"
    record["visual_report"]["notes"] = "Direction/scale approval is limited to native refinement; refined BASIC/ELITE gate remains pending."
    record["promotion"] = {"promotable": False, "target": "none"}
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"record": str(RECORD), "status": record["status"], "human_gate": record["gates"]["human"], "promotable": record["promotion"]["promotable"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
