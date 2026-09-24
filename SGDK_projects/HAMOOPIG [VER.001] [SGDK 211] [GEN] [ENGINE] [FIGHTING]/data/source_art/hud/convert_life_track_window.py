"""Crop the authored life chassis to the repeating BG_A rail used in combat."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "res" / "sprite" / "hud" / "life_track_empty.png"
OUTPUT = ROOT / "res" / "sprite" / "hud" / "life_track_chassis.png"


def main() -> None:
    source = Image.open(SOURCE).convert("P")
    # The authored 128x16 chassis has an 8px opaque rail centered vertically.
    # Keep authored left cap, body, and right cap cells. The runtime repeats
    # only the body between the caps, reducing BG_A residency from 32 to 3
    # tiles without turning the rail into a procedural primitive.
    rail = Image.new("P", (24, 8), 0)
    rail.putpalette(source.getpalette())
    rail.paste(source.crop((0, 4, 8, 12)), (0, 0))
    rail.paste(source.crop((8, 4, 16, 12)), (8, 0))
    rail.paste(source.crop((120, 4, 128, 12)), (16, 0))
    rail.save(OUTPUT, optimize=False, transparency=0)


if __name__ == "__main__":
    main()
