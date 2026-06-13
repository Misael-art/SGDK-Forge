from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

from PIL import Image, ImageEnhance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promove uma rota anime guiada por line art + recolor + paleta explícita para prova SGDK."
    )
    parser.add_argument("--recolor", required=True, help="Board recolorido pela IA.")
    parser.add_argument("--line-art", required=True, help="Board com apenas os traços.")
    parser.add_argument("--out-dir", required=True, help="Diretorio de saida.")
    return parser.parse_args()


def resize_scene(img: Image.Image) -> Image.Image:
    return img.convert("RGBA").resize((448, 224), Image.LANCZOS)


def extract_palette_components(img: Image.Image) -> tuple[list[tuple[int, int, int]], tuple[int, int, int]]:
    width, height = img.size
    crop = img.crop((width - 260, height - 210, width - 10, height - 10)).convert("RGB")
    panel = crop.crop((65, 70, 245, 195))
    pw, ph = panel.size

    visited = [[False] * pw for _ in range(ph)]
    components: list[tuple[tuple[int, int, int, int], int, tuple[int, int, int]]] = []

    for y in range(ph):
        for x in range(pw):
            if visited[y][x]:
                continue
            visited[y][x] = True
            r, g, b = panel.getpixel((x, y))
            if r > 235 and g > 235 and b > 235:
                continue
            queue = deque([(x, y)])
            pts: list[tuple[int, int]] = []
            while queue:
                cx, cy = queue.popleft()
                pts.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < pw and 0 <= ny < ph and not visited[ny][nx]:
                        visited[ny][nx] = True
                        rr, gg, bb = panel.getpixel((nx, ny))
                        if not (rr > 235 and gg > 235 and bb > 235):
                            queue.append((nx, ny))
            if len(pts) >= 80:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                x0, x1 = min(xs), max(xs)
                y0, y1 = min(ys), max(ys)
                cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                components.append(((x0, y0, x1, y1), len(pts), panel.getpixel((cx, cy))))

    # First component is usually scene bleed, not swatch.
    swatches = [color for (bbox, _, color) in sorted(components) if not (bbox[0] == 0 and bbox[1] == 0)]
    darkest = min(swatches, key=lambda c: c[0] + c[1] + c[2])
    return swatches, darkest


def nearest_color(pixel: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return min(
        palette,
        key=lambda c: (pixel[0] - c[0]) ** 2 + (pixel[1] - c[1]) ** 2 + (pixel[2] - c[2]) ** 2,
    )


def build_horizon(line_art: Image.Image) -> list[int]:
    gray = line_art.convert("L")
    width, height = gray.size
    horizon: list[int] = []
    for x in range(width):
        cut = height
        for y in range(height):
            if gray.getpixel((x, y)) < 245:
                cut = y
                break
        horizon.append(cut)

    smoothed: list[int] = []
    for i in range(width):
        left = max(0, i - 6)
        right = min(width - 1, i + 6)
        vals = sorted(horizon[left : right + 1])
        smoothed.append(vals[len(vals) // 2])
    return smoothed


def build_line_mask(line_art: Image.Image) -> Image.Image:
    gray = ImageEnhance.Contrast(line_art.convert("L")).enhance(1.2)
    return gray.point(lambda v: 255 if v < 210 else 0)


def compose_guided_scene(
    recolor_src: Image.Image,
    line_src: Image.Image,
    palette: list[tuple[int, int, int]],
    line_color: tuple[int, int, int],
) -> tuple[Image.Image, Image.Image, Image.Image]:
    recolor = resize_scene(recolor_src).convert("RGB")
    line = resize_scene(line_src).convert("RGBA")
    line_mask = build_line_mask(line)
    horizon = build_horizon(line)

    # Map recolor strictly to intended swatch palette.
    mapped = Image.new("RGB", recolor.size)
    for y in range(recolor.height):
        for x in range(recolor.width):
            mapped.putpixel((x, y), nearest_color(recolor.getpixel((x, y)), palette))

    # Reinforce line art after color mapping.
    for y in range(mapped.height):
        for x in range(mapped.width):
            if line_mask.getpixel((x, y)) > 0:
                mapped.putpixel((x, y), line_color)

    # Build BG_B from sampled sky values of mapped scene.
    sky_samples: list[tuple[int, int, int]] = []
    for x in range(0, mapped.width, 8):
        for y in range(0, max(1, horizon[x] - 2), 8):
            sky_samples.append(mapped.getpixel((x, y)))
    if not sky_samples:
        sky_samples = [(198, 224, 240), (120, 170, 210), (70, 120, 170)]

    sky_samples = sorted(sky_samples, key=lambda c: c[0] + c[1] + c[2])

    def pick(frac: float) -> tuple[int, int, int]:
        idx = min(len(sky_samples) - 1, int((len(sky_samples) - 1) * frac))
        return sky_samples[idx]

    sky_top = pick(0.15)
    sky_mid = pick(0.55)
    sky_low = pick(0.9)

    bg_b = Image.new("RGB", (256, 224))
    for y in range(224):
        if y < 110:
            c0, c1 = sky_top, sky_mid
            t = y / 110.0
        else:
            c0, c1 = sky_mid, sky_low
            t = (y - 110) / 114.0
        rgb = tuple(int(c0[i] * (1 - t) + c1[i] * t) for i in range(3))
        for x in range(256):
            bg_b.putpixel((x, y), rgb)

    bg_b = bg_b.quantize(colors=6, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")

    bg_a = Image.new("RGBA", (448, 224), (0, 0, 0, 0))
    for x in range(mapped.width):
        cut = horizon[x]
        for y in range(cut, mapped.height):
            bg_a.putpixel((x, y), mapped.getpixel((x, y)) + (255,))

    composite = Image.new("RGBA", (448, 224), (0, 0, 0, 255))
    for y in range(224):
        for x in range(448):
            composite.putpixel((x, y), bg_b.getpixel((x % 256, y)) + (255,))
    composite.alpha_composite(bg_a)
    return bg_a, bg_b, composite.convert("RGB")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    recolor_src = Image.open(args.recolor)
    line_src = Image.open(args.line_art)
    palette, line_color = extract_palette_components(recolor_src)

    bg_a, bg_b, composite = compose_guided_scene(recolor_src, line_src, palette, line_color)

    bg_a.save(out_dir / "route_anime_guided_bg_a.png", optimize=False)
    bg_b.save(out_dir / "route_anime_guided_bg_b.png", optimize=False)
    composite.save(out_dir / "route_anime_guided_composite.png", optimize=False)

    report = {
        "route": "anime_guided_pipeline",
        "palette": palette,
        "line_color": line_color,
        "inputs": {
            "recolor": str(Path(args.recolor)),
            "line_art": str(Path(args.line_art)),
        },
        "notes": [
            "Paleta extraida do proprio board recolorido.",
            "Line art reaplicado apos o mapeamento para preservar definicao.",
            "Sky promovido para BG_B separado a partir da leitura do line art.",
        ],
    }
    (out_dir / "route_anime_guided_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
