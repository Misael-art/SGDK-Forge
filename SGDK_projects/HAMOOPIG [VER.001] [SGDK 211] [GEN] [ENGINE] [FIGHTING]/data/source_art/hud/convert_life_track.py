"""Reduce the generated empty life chassis to a native SGDK sprite asset."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "data" / "source_art" / "hud" / "generated_life_track_v02.png"
OUTPUT = ROOT / "res" / "sprite" / "hud" / "life_track_empty.png"


def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    bbox = source.getchannel("A").getbbox()
    if bbox is None:
        raise SystemExit("life chassis has no opaque pixels")
    source = source.crop(bbox).resize((128, 16), Image.Resampling.NEAREST)
    rgb = Image.new("RGB", source.size, (0, 0, 0))
    rgb.paste(source, mask=source.getchannel("A"))
    quantized = rgb.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    out = Image.new("P", source.size, 0)
    # PAL1 is shared with the authored energy segment. Use only its existing
    # compatible slots: 1=light gray, 9=blue, 11=black. This prevents a
    # source-image blue from being decoded through PAL1's red/orange slots.
    pal1_compatible = [
        (255, 0, 255), (238, 238, 238), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 68, 170), (0, 0, 0), (0, 0, 0),
        (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    ]
    out.putpalette([channel for color in pal1_compatible for channel in color] + [0] * (768 - 48))
    mapped = []
    for pixel, alpha in zip(rgb.getdata(), source.getchannel("A").getdata()):
        if alpha < 128:
            mapped.append(0)
        else:
            r, g, b = pixel
            if r < 24 and g < 28 and b < 38:
                mapped.append(11)
            elif r > b + 42 and r + g > b * 2:
                # PAL1 index 2 is the existing warm-gold accent used by the
                # authored HUD atlas; retain it instead of flattening the
                # chassis into the blue slot.
                mapped.append(2 if r + g < 470 else 8)
            elif r + g + b > 330:
                mapped.append(1)
            else:
                mapped.append(9)
    out.putdata(mapped)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUTPUT, optimize=False, transparency=0)


if __name__ == "__main__":
    main()
