"""Compose the delayed-damage HUD cell from the authored life cell."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "res" / "sprite" / "hud" / "energy_yellow_segment.png"
OUTPUT = ROOT / "res" / "sprite" / "hud" / "energy_damage_segment.png"


def main() -> None:
    image = Image.open(SOURCE).convert("P")
    pixels = [3 if value == 2 else value for value in image.getdata()]
    image.putdata(pixels)
    image.save(OUTPUT, optimize=False, transparency=0)


if __name__ == "__main__":
    main()
