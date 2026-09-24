#!/usr/bin/env python3
"""P3: traduz uma fonte HD com chroma magenta em frame P1 de 32x32.

Mantem a fonte intacta, extrai a silhueta, reduz por nearest-neighbor,
quantiza os pixels visiveis e reserva o indice 0 para #FF00FF.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

MAGENTA = (255, 0, 255)
MD_LEVELS = (0, 36, 73, 109, 146, 182, 219, 255)


def is_chroma_background(rgb: tuple[int, int, int]) -> bool:
    """Aceita a variação de magenta criada pelo gerador, sem tocar no herói."""
    r, g, b = rgb
    return r >= 180 and g <= 120 and b >= 120


def snap(value: int) -> int:
    return min(MD_LEVELS, key=lambda level: abs(level - value))


def palette_color(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    snapped = tuple(snap(channel) for channel in rgb)
    return (255, 0, 219) if snapped == MAGENTA else snapped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    src = Image.open(args.source).convert("RGB")
    pixels = src.load()
    visible = [
        (x, y)
        for y in range(src.height)
        for x in range(src.width)
        if not is_chroma_background(pixels[x, y])
    ]
    if not visible:
        raise SystemExit("fonte sem pixels visiveis fora do magenta")
    left = min(x for x, _ in visible)
    top = min(y for _, y in visible)
    right = max(x for x, _ in visible) + 1
    bottom = max(y for _, y in visible) + 1
    crop = src.crop((left, top, right, bottom))
    mask = Image.new("1", crop.size)
    for y in range(crop.height):
        for x in range(crop.width):
            mask.putpixel((x, y), int(not is_chroma_background(crop.getpixel((x, y)))))

    scale = min(30 / crop.width, 30 / crop.height)
    target = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    crop = crop.resize(target, Image.Resampling.NEAREST)
    mask = mask.resize(target, Image.Resampling.NEAREST)
    indexed = crop.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    raw_palette = indexed.getpalette()

    palette = [MAGENTA]
    remap: dict[tuple[int, int, int], int] = {}
    for index in range(15):
        rgb = tuple(raw_palette[index * 3 : index * 3 + 3])
        snapped = palette_color(rgb)
        if snapped not in remap:
            remap[snapped] = len(palette)
            palette.append(snapped)

    out = Image.new("P", (32, 32), 0)
    out.putpalette([component for color in (palette + [(0, 0, 0)] * (16 - len(palette))) for component in color])
    ox = (32 - target[0]) // 2
    oy = 31 - target[1]
    for y in range(target[1]):
        for x in range(target[0]):
            if mask.getpixel((x, y)):
                source_index = indexed.getpixel((x, y))
                rgb = tuple(raw_palette[source_index * 3 : source_index * 3 + 3])
                out.putpixel((ox + x, oy + y), remap[palette_color(rgb)])
    out.info["transparency"] = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output, bits=4)
    print(f"written={args.output} visible_colors={len(palette) - 1} source_bbox={left},{top},{right},{bottom}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
