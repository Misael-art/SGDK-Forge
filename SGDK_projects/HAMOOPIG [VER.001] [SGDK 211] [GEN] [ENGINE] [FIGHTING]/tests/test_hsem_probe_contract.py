#!/usr/bin/env python3
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("analyze_hsem_probe", ROOT / "tests/analyze_hsem_probe.py")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

assert MODULE.self_check() == 0
fixture = MODULE.decode(MODULE._block([0, 99, 99, 8, 160, 0, 13, 40, 12]))
assert fixture["video_frame"] == 99
assert fixture["min_distance"] == 8
assert fixture["guard_frames_p2"] == 13
assert fixture["evidence_scope"].startswith("HSEM SRAM")
print("PASS: HSEM decoder contrato e fixtures válidos")
