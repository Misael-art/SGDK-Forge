#!/usr/bin/env python3
"""Normalize the compact HUD segment to SGDK's index-0 transparency contract."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "res/sprite/hud/energy_yellow_segment.png"


def main() -> None:
    image = Image.open(SOURCE).convert("RGB")
    output = Image.new("P", image.size, 0)
    output.putpalette([255, 0, 255, 238, 238, 238, 238, 238, 0] + [0, 0, 0] * 253)
    pixels = output.load()
    yellow = (238, 238, 0)
    for y in range(image.height):
        for x in range(image.width):
            # PAL1 is shared with the legacy energy palette: index 2 is the
            # authored yellow entry, while index 0 remains transparent.
            pixels[x, y] = 2 if image.getpixel((x, y)) == yellow else 0
    output.info["transparency"] = 0
    output.save(SOURCE, format="PNG", optimize=False)


if __name__ == "__main__":
    main()
