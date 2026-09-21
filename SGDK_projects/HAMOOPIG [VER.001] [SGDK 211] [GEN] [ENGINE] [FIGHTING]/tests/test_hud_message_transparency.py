#!/usr/bin/env python3
"""Contract for stage-visible transient HUD messages."""
from pathlib import Path
from PIL import Image

SRC = Path(__file__).resolve().parents[1] / "src" / "hud.c"
text = SRC.read_text(encoding="utf-8")

assert "if(message >= 7)" in text, "result-message panel guard missing"
assert "sHudBlackTile" in text, "result panel lost its black readability tile"
assert "Round/FIGHT/KO are overlaid on the stage with transparent cells" in text
block_start = text.index("if(message >= 7)")
block_end = text.index("if(message == 1)", block_start)
block = text[block_start:block_end]
assert "for(row=0; row < HUD_MESSAGE_ROWS; row++)" in block
font = Image.open(Path(__file__).resolve().parents[1] / "res/sprite/hud/message_font.png")
pixels = font.tobytes()
assert 0 in pixels, "message atlas must reserve index 0 for transparency"
assert pixels.count(0) > 1000, "message atlas background was not remapped"
print("PASS: ROUND/FIGHT/KO leave the stage visible; result prompt keeps a bounded panel")
