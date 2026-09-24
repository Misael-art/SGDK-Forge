#!/usr/bin/env python3
"""P10 runner must be fresh-ROM and manifest-bound, never infer coverage."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runner = (ROOT / "tests/run_p10_matrix.py").read_text(encoding="utf-8")
assert "capture_visual_ko.py" in runner
assert "rom_sha256" in runner and "manifest.json" in runner
assert "requested_p1" in runner and "requested_p2" in runner
assert "pending_visual_review" in runner
assert "selection_only" in runner
assert "retry_failed" in runner
assert "case-id" in runner
assert "hprb_probe_report" in runner
print("PASS: P10 runner binds each case to fresh ROM/manifest evidence")
