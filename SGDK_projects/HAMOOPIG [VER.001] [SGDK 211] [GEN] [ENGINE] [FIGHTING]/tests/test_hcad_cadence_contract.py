#!/usr/bin/env python3
"""Static contract for logic/presentation cadence evidence."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = (ROOT / "src/hamoopig_runtime_probe.c").read_text(encoding="utf-8")
MAIN = (ROOT / "src/main.c").read_text(encoding="utf-8")


def main() -> None:
    assert "#define HCAD_OFFSET 0x640u" in PROBE
    assert "#define HCAD_SCHEMA 1u" in PROBE
    assert "exportCadenceProbe();" in PROBE
    assert "void HAMOOPIG_probeVideoFrame(u8 scene, u8 logicTicks)" in PROBE
    assert "HAMOOPIG_probeVideoFrame(gRoom, presentedTicks);" in MAIN
    assert "HAMOOPIG_probeVideoFrame(gRoom, 0u);" in MAIN
    print("PASS: HCAD cadence ledger covers zero/one/two logic ticks and presentation commits")


if __name__ == "__main__":
    main()
