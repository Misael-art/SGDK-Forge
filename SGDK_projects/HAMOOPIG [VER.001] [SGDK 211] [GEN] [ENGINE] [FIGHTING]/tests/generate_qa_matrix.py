#!/usr/bin/env python3
"""Generate the ordered matchup matrix without claiming unrun emulator cases."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "doc/engine/p10_qa_matrix.json"
FIGHTERS = ("ryo", "ken", "musgo")
STAGES = ("showdown_park", "stage2_swamp_dock")
REGIONS = ("NTSC", "PAL")
OBSERVED_RUNTIME = {
    "ryo_vs_musgo_stage2_swamp_dock_ntsc": {
        "status": "pending_visual_review",
        "runtime_status": "passed",
        "rom_sha256": "14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440",
        "bundle": "out/emulator_evidence/visual_ko_20260915T080351Z/",
        "notes": "same-ROM route reached Stage 2, 21 HIT events, KO and restored round; visual/audio axes remain pending",
    }
}


def main() -> None:
    cases = []
    for p1 in FIGHTERS:
        for p2 in FIGHTERS:
            for stage in STAGES:
                for region in REGIONS:
                    case = {
                        "id": f"{p1}_vs_{p2}_{stage}_{region.lower()}",
                        "p1": p1,
                        "p2": p2,
                        "stage": stage,
                        "region": region,
                        "status": "not_run",
                        "rom_sha256": None,
                        "bundle": None,
                        "notes": "requires real keyboard/emulator evidence",
                    }
                    case.update(OBSERVED_RUNTIME.get(case["id"], {}))
                    cases.append(case)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "schema_version": "1.0.0",
        "task": "P10",
        "claim_ceiling": "prototype",
        "generated_by": "tests/generate_qa_matrix.py",
        "required_cases": len(cases),
        "statuses": {
            "not_run": sum(case["status"] == "not_run" for case in cases),
            "passed": sum(case["status"] == "passed" for case in cases),
            "failed": sum(case["status"] == "failed" for case in cases),
            "pending_visual_review": sum(case["status"] == "pending_visual_review" for case in cases),
        },
        "cases": cases,
        "required_per_case": ["boot", "movement", "jump", "hit", "hud", "round_end"],
        "global_pending": [
            "audio audition",
            "visual comparison",
            "100 scene/reset cycles",
            "worst-frame with all effects and audio",
        ],
    }, indent=2) + "\n", encoding="utf-8")
    print(f"generated {OUT} ({len(cases)} cases)")


if __name__ == "__main__":
    main()
