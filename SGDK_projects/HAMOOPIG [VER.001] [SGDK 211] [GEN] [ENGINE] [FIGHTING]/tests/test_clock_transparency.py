#!/usr/bin/env python3
"""Static contract for the PAL1-shared transparent clock atlas."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    res = (ROOT / "res/hud_gfx.res").read_text(encoding="utf-8")
    hud = (ROOT / "src/hud.c").read_text(encoding="utf-8")
    config = (ROOT / "inc/config.h").read_text(encoding="utf-8")
    title = (ROOT / "src/title.c").read_text(encoding="utf-8")
    assert "clock_digits_transparent.png" in res
    path = ROOT / "res/sprite/hud/clock_digits_transparent.png"
    report = json.loads((ROOT / "data/source_art/sf_hud/clock_mask_report.json").read_text())
    src = Image.open(ROOT / "res/sprite/hud/clock_digits_window.png")
    im = Image.open(path)
    assert im.mode == "P" and im.size == (160, 16)
    assert 0 in set(im.get_flattened_data())
    assert report["output_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert report["source_sha256"] == hashlib.sha256((ROOT / report["source"]).read_bytes()).hexdigest()
    assert report["transparent_output_index"] == 0
    assert report["masked_pixels"] == sum(1 for value in src.get_flattened_data() if value == 11)
    assert "hudTimerBg" in config and "HUD_CLK_BG_COLS" in hud and "HUD_CLK_BG_X" in hud
    assert "hud_clock_background_update" in hud and "TBG ON" in title
    assert "gConfig.hudTimerBg ? TILE_ATTR_FULL" in hud
    print("PASS: clock background masked to PAL1 index 0 with shared HUD palette")


if __name__ == "__main__":
    main()
