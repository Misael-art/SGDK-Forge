#!/usr/bin/env python3
"""Contract test for the versioned HPRB combat-event extension."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("analyze_hprb_probe", ROOT / "tests/analyze_hprb_probe.py")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def main():
    assert MODULE.SCHEMA_SIZE[6] == (68, 30)
    assert MODULE.self_check() == 0
    decoded = MODULE.decode(MODULE._schema6(events=7, hits=5, guards=1, throws=1,
                                            projectiles=2, double=1, ko=1,
                                            last_events=1, last_ko=1))
    assert decoded["combat_total_events"] == 7
    assert decoded["combat_total_projectiles"] == 2
    assert decoded["combat_last_tick_ko"] == 1
    print("PASS: HPRB schema 6 exports combat event telemetry without breaking legacy schemas")


if __name__ == "__main__":
    main()
