"""Convert the authored KO banner into a compact PAL1 SGDK sprite."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "data" / "source_art" / "hud" / "generated_ko_banner_v01.png"
OUTPUT = ROOT / "res" / "sprite" / "hud" / "ko_banner.png"


def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    bbox = source.getchannel("A").getbbox()
    if bbox is None:
        raise SystemExit("KO banner has no opaque pixels")
    source = source.crop(bbox).resize((48, 24), Image.Resampling.NEAREST)
    out = Image.new("P", source.size, 0)
    # PAL1 is the HUD carrier: keep the banner restricted to slots already
    # present in the runtime palette instead of introducing an untracked CRAM.
    palette = [
        (255, 0, 255), (238, 238, 238), (255, 204, 0), (0, 0, 0),
        (255, 136, 0), (255, 255, 255), (204, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 68, 170), (255, 68, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    ]
    out.putpalette([channel for color in palette for channel in color] + [0] * (768 - 48))
    mapped = []
    for r, g, b, a in source.getdata():
        if a < 128:
            mapped.append(0)
        elif r < 40 and g < 45 and b < 65:
            mapped.append(11)
        elif r > 245 and g > 235 and b > 180:
            mapped.append(5)
        elif r > 220 and g > 145 and b < 80:
            mapped.append(2)
        elif r > 180 and g < 100 and b < 90:
            mapped.append(10)
        elif r > 150 and g < 45 and b < 70:
            mapped.append(6)
        else:
            mapped.append(4)
    out.putdata(mapped)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUTPUT, optimize=False, transparency=0)
    print(f"source={SOURCE}")
    print(f"output={OUTPUT}")


if __name__ == "__main__":
    main()
