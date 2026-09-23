from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reduz uma referencia anime aprovada para uma prova mais cabivel no Mega Drive."
    )
    parser.add_argument("--input", required=True, help="Imagem de referencia aprovada.")
    parser.add_argument("--out-dir", required=True, help="Diretorio de saida.")
    return parser.parse_args()


def smooth_horizon(values: list[int], radius: int = 6) -> list[int]:
    out: list[int] = []
    width = len(values)
    for i in range(width):
        left = max(0, i - radius)
        right = min(width - 1, i + radius)
        chunk = sorted(values[left : right + 1])
        out.append(chunk[len(chunk) // 2])
    return out


def quantize_preserve_alpha(img: Image.Image, colors: int) -> Image.Image:
    alpha = img.getchannel("A")
    rgb = img.convert("RGB").quantize(
        colors=colors,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    ).convert("RGB")
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            if alpha.getpixel((x, y)) > 0:
                out.putpixel((x, y), rgb.getpixel((x, y)) + (255,))
    return out


def build_budget_variant(src: Image.Image) -> tuple[Image.Image, Image.Image, Image.Image, dict]:
    img = src.convert("RGB").resize((448, 224), Image.LANCZOS)
    cleaned = img.filter(ImageFilter.MedianFilter(3))
    cleaned = cleaned.filter(ImageFilter.ModeFilter(5))
    cleaned = ImageEnhance.Color(cleaned).enhance(0.92)
    cleaned = ImageEnhance.Contrast(cleaned).enhance(1.06)

    edges = img.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_mask = edges.point(lambda v: 255 if v > 28 else 0)
    ink_dark = Image.new("RGB", img.size, (22, 14, 12))
    inked = Image.composite(ink_dark, cleaned, edge_mask)

    rgba = inked.convert("RGBA")
    width, height = rgba.size

    horizon_raw: list[int] = []
    for x in range(width):
        cut = height
        for y in range(height):
            r, g, b, _ = rgba.getpixel((x, y))
            is_sky = b > g + 6 and g > r + 2 and b > 48 and y < 170
            if not is_sky:
                cut = y
                break
        horizon_raw.append(cut)
    horizon = smooth_horizon(horizon_raw)

    samples: list[tuple[int, int, int]] = []
    for x in range(0, width, 8):
        for y in range(0, max(1, horizon[x] - 2), 8):
            samples.append(img.getpixel((x, y)))
    samples = sorted(samples, key=lambda c: c[0] + c[1] + c[2]) or [(20, 60, 85)]

    def pick(frac: float) -> tuple[int, int, int]:
        idx = min(len(samples) - 1, int((len(samples) - 1) * frac))
        return samples[idx]

    sky_top = pick(0.15)
    sky_mid = pick(0.5)
    sky_low = pick(0.85)

    bg_b = Image.new("RGB", (256, 224))
    for y in range(224):
        if y < 96:
            c0, c1 = sky_top, sky_mid
            t = y / 96.0
        else:
            c0, c1 = sky_mid, sky_low
            t = (y - 96) / 128.0
        rgb = tuple(int(c0[i] * (1 - t) + c1[i] * t) for i in range(3))
        for x in range(256):
            bg_b.putpixel((x, y), rgb)

    bg_a = Image.new("RGBA", (448, 224), (0, 0, 0, 0))
    for x in range(width):
        cut = horizon[x]
        for y in range(cut, height):
            bg_a.putpixel((x, y), rgba.getpixel((x, y)))

    original_bg_a = bg_a.copy()

    # Road and sidewalk: flatten broad tones, then restore only strong linework.
    road_box = (0, 150, 448, 224)
    road = bg_a.crop(road_box).convert("RGB")
    road_flat = road.resize((224, 37), Image.BILINEAR).resize(road.size, Image.NEAREST)
    road_flat = road_flat.filter(ImageFilter.ModeFilter(5))
    road_edges = road.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 38 else 0)
    road_ink = Image.new("RGB", road.size, (32, 22, 18))
    road_out = Image.composite(road_ink, road_flat, road_edges)
    bg_a.paste(road_out.convert("RGBA"), road_box)

    # Building facades: soften microtexture but keep windows and structural lines.
    facade_boxes = [
        (0, 0, 160, 92),     # left upper building
        (0, 86, 198, 190),   # shop house body
        (320, 22, 448, 184), # right building
    ]
    for box in facade_boxes:
        region = bg_a.crop(box).convert("RGB")
        soft = region.filter(ImageFilter.ModeFilter(5))
        soft = soft.resize((max(1, region.width // 2), max(1, region.height // 2)), Image.BILINEAR)
        soft = soft.resize(region.size, Image.NEAREST)
        region_edges = region.convert("L").filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 34 else 0)
        region_ink = Image.new("RGB", region.size, (28, 18, 16))
        rebuilt = Image.composite(region_ink, soft, region_edges)
        bg_a.paste(rebuilt.convert("RGBA"), box)

    # Restore hotspots from the original so the scene does not go dead.
    restore_boxes = [
        (12, 108, 108, 191),  # storefront glow / entry
        (100, 118, 142, 188), # curtain area
        (206, 52, 342, 130),  # traffic light and central bridge silhouette
    ]
    for box in restore_boxes:
        bg_a.paste(original_bg_a.crop(box), box)

    q_bg_b = bg_b.quantize(colors=12, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q_bg_a = quantize_preserve_alpha(bg_a, colors=13)

    composite = Image.new("RGBA", (448, 224), (0, 0, 0, 255))
    q_bg_b_rgb = q_bg_b.convert("RGB")
    for y in range(224):
        for x in range(448):
            composite.putpixel((x, y), q_bg_b_rgb.getpixel((x % 256, y)) + (255,))
    composite.alpha_composite(q_bg_a)

    report = {
        "source_style": "anime_background_reference",
        "road_box": road_box,
        "facade_boxes": facade_boxes,
        "restore_boxes": restore_boxes,
        "sky_palette_seed": {
            "top": sky_top,
            "mid": sky_mid,
            "low": sky_low,
        },
        "notes": [
            "Reduz microtextura do chao e das fachadas antes da quantizacao final.",
            "Mantem linework forte e hotspots narrativos do original aprovado.",
            "Objetivo: aproximar a referencia anime do budget real do Mega Drive.",
        ],
    }
    return q_bg_a, q_bg_b, composite.convert("RGB"), report


def main() -> None:
    args = parse_args()
    src = Image.open(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    bg_a, bg_b, composite, report = build_budget_variant(src)
    bg_a.save(out_dir / "route_anime_reference_budget_bg_a.png", optimize=False)
    bg_b.save(out_dir / "route_anime_reference_budget_bg_b.png", optimize=False)
    composite.save(out_dir / "route_anime_reference_budget_composite.png", optimize=False)
    (out_dir / "route_anime_reference_budget_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
