#!/usr/bin/env python3
"""The reset stress route must state exactly what it does and does not prove."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "tests/run_scene_reset_cycles.py").read_text(encoding="utf-8")
assert "cycles_completed" in source
assert "round_reset_cycles" in source
assert "not_exercised_by_this_route" in source
assert "rom_sha256" in source
print("PASS: 100-cycle scene reset stress route keeps round-reset claim bounded")
