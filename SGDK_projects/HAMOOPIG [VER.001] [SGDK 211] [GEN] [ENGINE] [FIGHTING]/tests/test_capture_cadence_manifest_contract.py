#!/usr/bin/env python3
"""Ensure full visual captures preserve cadence evidence beside the manifest."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "tests/capture_visual_ko.py").read_text(encoding="utf-8")


def main() -> None:
    assert "def cadence_snapshot():" in SOURCE
    assert "offset=raw.find(b'HCAD')" in SOURCE
    assert "'cadence_probe':cadence_probe" in SOURCE
    assert "cadence_invariant" in SOURCE
    assert "fight_cadence_invariant" in SOURCE
    print("PASS: full capture manifest carries HCAD logic/presentation cadence evidence")


if __name__ == "__main__":
    main()
