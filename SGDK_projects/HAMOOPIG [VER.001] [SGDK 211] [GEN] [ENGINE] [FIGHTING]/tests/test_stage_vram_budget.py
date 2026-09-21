#!/usr/bin/env python3
"""Keep the measured Showdown tile ceiling tied to SGDK's real guard."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "res/gfx/showdown.json").read_text())
init = (ROOT / "src/init.c").read_text()
assert report["unique_output_tiles"] == 864
assert "stageTiles + hudTiles > TILE_SPRITE_INDEX" in init
assert "SYS_die(\"Fight tiles overlap sprite VRAM\")" in init
for rejected in ("rascunho/showdown_candidate_1024.json",):
    data = json.loads((ROOT / rejected).read_text())
    assert data["unique_output_tiles"] > report["unique_output_tiles"]
print("PASS: safe Showdown tile ceiling remains guarded; 864-tile candidate fits measured runtime envelope")
