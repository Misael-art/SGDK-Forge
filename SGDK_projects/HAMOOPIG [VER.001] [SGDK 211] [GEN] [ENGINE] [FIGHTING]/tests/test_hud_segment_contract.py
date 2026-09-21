#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "res/sprite/hud/energy_yellow_segment.png"


def main():
    image = Image.open(ASSET).convert("P")
    assert image.size == (16, 8)
    assert image.getpixel((0, 0)) == 0
    used = set(image.get_flattened_data())
    assert used <= {0, 2}
    assert 2 in used
    palette = image.getpalette()
    assert tuple(palette[0:3]) == (255, 0, 255)
    assert tuple(palette[6:9]) == (238, 238, 0)
    print("PASS: HUD segment uses SGDK index-0 transparency and shared PAL1 yellow index 2")


if __name__ == "__main__":
    main()
