#!/usr/bin/env python3
"""Static contract for the canonical VLAB evidence block."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/hamoopig_runtime_probe.c").read_text(encoding="utf-8")


def main():
    assert "#define VLAB_OFFSET 0x200u" in SOURCE
    assert "#define HPRB_OFFSET 0x500u" in SOURCE
    assert "#define HSEM_OFFSET 0x580u" in SOURCE
    assert "#define VLAB_SCHEMA 1u" in SOURCE
    assert "#define VLAB_METRIC_WORDS (43u + VLAB_RANGE_WORDS + VLAB_EXTRA_WORDS)" in SOURCE
    assert "PAL_getColors(0, vlabPalette, VLAB_PALETTE_WORDS)" in SOURCE
    assert "SYS_getCPULoad()" in SOURCE
    assert "probePreviousCpuLoad" in SOURCE
    assert "probeHasPreviousCpuLoad" in SOURCE
    assert "probeDiagnosticCooldown" in SOURCE
    assert "HAMOOPIG_probeFightInit" in SOURCE
    assert "probeFightWarmupUntilFrame" in SOURCE
    assert "HAMOOPIG_probeVramRange(TILE_SPRITE_INDEX, spriteVramSize)" in SOURCE
    assert "exportVisualProbe(scene);" in SOURCE
    assert "SRAM_writeByte(offset + 0u, 'V')" in SOURCE
    extended = SOURCE.split("/* words[24..42] preserve the extended VLAB positions. */", 1)[1]
    extended = extended.split("/* words[43..51] are scene-local VRAM ranges:", 1)[0]
    assert len(re.findall(r"writeBE16\(", extended)) == 19
    ranges = SOURCE.split("/* words[43..51] are scene-local VRAM ranges:", 1)[1]
    ranges = ranges.split("/* words[52..54]", 1)[0]
    assert len(re.findall(r"writeBE16\(", ranges)) == 5
    extra = SOURCE.split("/* words[52..54]", 1)[1]
    extra = extra.split("for(i = 0u; i < VLAB_PALETTE_WORDS;", 1)[0]
    assert len(re.findall(r"writeBE16\(", extra)) == 3
    print("PASS: VLAB visual snapshot preserves canonical offsets and CRAM export")


if __name__ == "__main__":
    main()
