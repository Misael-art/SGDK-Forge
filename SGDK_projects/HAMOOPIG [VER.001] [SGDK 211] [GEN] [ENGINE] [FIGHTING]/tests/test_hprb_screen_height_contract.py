#!/usr/bin/env python3
"""Contract for HPRB schema 7's PAL-224/PAL-240 field."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import analyze_hprb_probe as probe


def main():
    assert probe.SCHEMA_SIZE[7] == (70, 31)
    report = probe.decode(probe._schema7(screen_height=240))
    assert report["screen_height"] == 240
    legacy = probe.decode(probe._schema6())
    assert legacy["screen_height"] is None
    print("PASS: HPRB schema 7 exports screen height and preserves schema 6")


if __name__ == "__main__":
    main()
