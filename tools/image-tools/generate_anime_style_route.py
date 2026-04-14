from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

from PIL import Image, ImageFilter


PALETTE = [
    (26, 18, 32),    # 0 outline / deep plum
    (88, 108, 176),  # 1 sky top
    (144, 188, 232), # 2 sky mid
    (244, 224, 188), # 3 sky horizon
    (244, 208, 120), # 4 warm window
    (252, 244, 208), # 5 hot window
    (70, 40, 28),    # 6 warm dark
    (144, 92, 52),   # 7 warm mid
    (208, 148, 72),  # 8 warm light
    (18, 52, 34),    # 9 bridge dark
    (56, 104, 68),   # 10 bridge mid
    (74, 82, 92),    # 11 neutral dark
    (118, 126, 134), # 12 neutral mid
    (198, 202, 206), # 13 neutral light
    (120, 84, 160),  # 14 accent purple
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um estudo de rota anime_style com pintura cel-shaded e paleta travada."
    )
    parser.add_argument("--input", required=True, help="PNG base da cena/crop.")
    parser.add_argument("--output", required=True, help="PNG indexado 15 cores.")
    parser.add_argument("--output-rgb", help="Preview RGB opcional.")
    parser.add_argument("--report", help="JSON opcional com metadados da geracao.")
    return parser.parse_args()


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def smooth_horizon(horizon: list[int], radius: int = 5) -> list[int]:
    result: list[int] = []
    length = len(horizon)
    for i in range(length):
        left = clamp(i - radius, 0, length - 1)
        right = clamp(i + radius, 0, length - 1)
        result.append(int(median(horizon[left : right + 1])))
    return result


def luminance(pixel: tuple[int, int, int]) -> int:
    r, g, b = pixel
    return int((r * 299 + g * 587 + b * 114) / 1000)


def is_warm_light(pixel: tuple[int, int, int], lum: int) -> bool:
    r, g, b = pixel
    return lum > 105 and r >= g - 12 and g > b


def is_purple_region(x: int, y: int, pixel: tuple[int, int, int]) -> bool:
    r, g, b = pixel
    if 105 <= x <= 145 and 124 <= y <= 177 and luminance(pixel) > 24:
        return True
    return b > r + 20 and r > g + 5


def build_horizon(img: Image.Image) -> list[int]:
    width, height = img.size
    horizon: list[int] = []
    for x in range(width):
        top = height
        for y in range(height):
            if sum(img.getpixel((x, y))) > 24:
                top = y
                break
        horizon.append(top)
    return smooth_horizon(horizon)


def choose_sky_index(y: int, height: int) -> int:
    if y < int(height * 0.32):
        return 1
    if y < int(height * 0.66):
        return 2
    return 3


def assign_region(
    x: int,
    y: int,
    pixel: tuple[int, int, int],
    lum: int,
) -> str:
    r, g, b = pixel
    if y >= 154:
        return "road"
    if 110 < x < 408 and y < 178:
        if g >= r - 8 and g > b:
            return "bridge"
        if 225 < x < 408 and r <= g + 10:
            return "neutral"
    if x < 214 and y < 188:
        return "warm"
    if x >= 214 and y < 188:
        if r > g + 10 or lum < 96:
            return "warm"
        return "neutral"
    return "neutral"


def build_palette_bytes() -> list[int]:
    flat: list[int] = []
    for r, g, b in PALETTE:
        flat.extend([r, g, b])
    flat.extend([0] * (768 - len(flat)))
    return flat


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(input_path).convert("RGB")
    if img.size != (448, 224):
        img = img.resize((448, 224), Image.NEAREST)

    smoothed = img.filter(ImageFilter.MedianFilter(3))
    edges = smoothed.convert("L").filter(ImageFilter.FIND_EDGES)
    horizon = build_horizon(smoothed)

    width, height = smoothed.size
    indices: list[int] = []
    usage = {str(i): 0 for i in range(len(PALETTE))}

    for y in range(height):
        for x in range(width):
            src = smoothed.getpixel((x, y))
            src_lum = luminance(src)
            edge_strength = edges.getpixel((x, y))

            if y < horizon[x]:
                index = choose_sky_index(y, height)
            else:
                region = assign_region(x, y, src, src_lum)
                if is_purple_region(x, y, src):
                    index = 14
                elif is_warm_light(src, src_lum) and region != "road":
                    index = 5 if src_lum > 180 else 4
                elif edge_strength > 48 and src_lum < 108:
                    index = 0
                elif region == "bridge":
                    index = 9 if src_lum < 82 else 10
                elif region == "warm":
                    if src_lum < 58:
                        index = 6
                    elif src_lum < 110:
                        index = 7
                    else:
                        index = 8
                else:
                    if src_lum < 62:
                        index = 11
                    elif src_lum < 116:
                        index = 12
                    else:
                        index = 13

            indices.append(index)
            usage[str(index)] += 1

    indexed = Image.new("P", (width, height))
    indexed.putpalette(build_palette_bytes())
    indexed.putdata(indices)
    indexed.save(output_path, optimize=False)

    if args.output_rgb:
        rgb_path = Path(args.output_rgb)
        rgb_path.parent.mkdir(parents=True, exist_ok=True)
        indexed.convert("RGB").save(rgb_path, optimize=False)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "route": "anime_style",
            "input": str(input_path),
            "output": str(output_path),
            "size": [width, height],
            "palette_size": len(PALETTE),
            "palette_rgb": PALETTE,
            "usage_by_index": usage,
            "notes": [
                "Recomposicao cel-shaded com ceu em bandas largas.",
                "A filosofia e anime background: leitura de massas, sombra chapada e highlights quentes.",
                "O objetivo e testar uma rota rica sem depender de muitos degrades."
            ],
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
