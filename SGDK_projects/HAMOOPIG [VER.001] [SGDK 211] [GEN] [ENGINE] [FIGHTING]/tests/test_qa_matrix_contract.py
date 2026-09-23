#!/usr/bin/env python3
"""The P10 matrix must enumerate every ordered fighter/stage/region case."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "doc/engine/p10_qa_matrix.json").read_text())
assert DATA["required_cases"] == 36
assert len(DATA["cases"]) == 36
assert len({case["id"] for case in DATA["cases"]}) == 36
assert set(DATA["statuses"]) == {"not_run", "passed", "failed", "pending_visual_review"}
assert DATA["statuses"]["pending_visual_review"] >= 1
assert DATA["statuses"]["failed"] == 0
observed = next(case for case in DATA["cases"] if case["id"] == "ryo_vs_musgo_stage2_swamp_dock_ntsc")
assert observed["runtime_status"] in {"passed", "selection_passed", "probe_passed"}
assert observed["status"] == "pending_visual_review"
print("PASS: P10 enumerates 36 ordered matchup cases without false completion")
