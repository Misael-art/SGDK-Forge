from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps


RAW_RECOLOR_PALETTE: list[tuple[int, int, int]] = [
    (175, 208, 225),
    (249, 234, 179),
    (245, 190, 151),
    (215, 193, 160),
    (224, 175, 56),
    (183, 101, 63),
    (155, 108, 62),
    (120, 82, 45),
    (86, 54, 29),
    (84, 132, 132),
    (51, 107, 78),
    (44, 37, 81),
    (0, 2, 1),
]

COHESIVE_RECOLOR_MAP: dict[tuple[int, int, int], tuple[int, int, int]] = {
    (175, 208, 225): (24, 62, 78),
    (249, 234, 179): (234, 219, 170),
    (245, 190, 151): (223, 176, 138),
    (215, 193, 160): (194, 171, 140),
    (224, 175, 56): (224, 175, 56),
    (183, 101, 63): (171, 94, 58),
    (155, 108, 62): (143, 101, 60),
    (120, 82, 45): (108, 73, 41),
    (86, 54, 29): (79, 49, 27),
    (84, 132, 132): (72, 118, 120),
    (51, 107, 78): (44, 94, 68),
    (44, 37, 81): (44, 37, 81),
    (0, 2, 1): (0, 2, 1),
}

OUTPUT_SIZE = (448, 224)
SKY_BG_SIZE = (256, 224)


@dataclass(frozen=True)
class Profile:
    slug: str
    block_threshold: int
    display_threshold: int
    use_cohesive_palette: bool
    sky_colors: list[tuple[int, int, int]]


PROFILES: dict[str, Profile] = {
    "balanced": Profile(
        slug="balanced",
        block_threshold=64,
        display_threshold=105,
        use_cohesive_palette=False,
        sky_colors=[(175, 208, 225)],
    ),
    "cohesive": Profile(
        slug="cohesive",
        block_threshold=56,
        display_threshold=120,
        use_cohesive_palette=True,
        sky_colors=[(12, 45, 62), (18, 58, 74), (24, 72, 86)],
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promove uma rota anime line-first para BG_A/BG_B SGDK-validos."
    )
    parser.add_argument("--line-art", required=True, help="Board em line art.")
    parser.add_argument("--recolor", required=True, help="Board recolorido por massas amplas.")
    parser.add_argument(
        "--anime-style",
        help="Board anime intermediario. Opcional; usado apenas para rastreio no report.",
    )
    parser.add_argument("--out-dir", required=True, help="Diretorio de saida.")
    parser.add_argument(
        "--profile",
        choices=["balanced", "cohesive", "all"],
        default="all",
        help="Perfil a gerar. 'all' gera os dois perfis canônicos.",
    )
    return parser.parse_args()


def resize_rgb(path: str) -> Image.Image:
    return Image.open(path).convert("RGB").resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)


def build_line_density(path: str) -> Image.Image:
    line_src = Image.open(path).convert("L")
    return ImageOps.invert(line_src).resize(OUTPUT_SIZE, Image.Resampling.BOX)


def nearest_color(pixel: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return min(
        palette,
        key=lambda c: (pixel[0] - c[0]) ** 2 + (pixel[1] - c[1]) ** 2 + (pixel[2] - c[2]) ** 2,
    )


def build_horizon(block_mask: Image.Image) -> list[int]:
    width, height = block_mask.size
    horizon: list[int] = []
    for x in range(width):
        cut = height
        for y in range(height):
            if block_mask.getpixel((x, y)):
                cut = y
                break
        horizon.append(cut)
    return horizon


def build_labels(
    recolor: Image.Image,
    raw_palette: list[tuple[int, int, int]],
    final_palette_map: dict[tuple[int, int, int], tuple[int, int, int]],
) -> list[list[tuple[int, int, int]]]:
    width, height = recolor.size
    labels: list[list[tuple[int, int, int]]] = []
    for y in range(height):
        row: list[tuple[int, int, int]] = []
        for x in range(width):
            raw = nearest_color(recolor.getpixel((x, y)), raw_palette)
            row.append(final_palette_map[raw])
        labels.append(row)
    return labels


def region_fill_scene(
    labels: list[list[tuple[int, int, int]]],
    block_mask: Image.Image,
    horizon: list[int],
) -> Image.Image:
    width, height = block_mask.size
    region_fill = Image.new("RGB", (width, height), (0, 0, 0))
    visited = [[False] * width for _ in range(height)]

    for y in range(height):
        for x in range(width):
            if visited[y][x]:
                continue
            if block_mask.getpixel((x, y)) or y < horizon[x]:
                visited[y][x] = True
                continue

            queue = deque([(x, y)])
            visited[y][x] = True
            pixels: list[tuple[int, int]] = []
            count = Counter()
            min_x = max_x = x
            min_y = max_y = y

            while queue:
                cx, cy = queue.popleft()
                pixels.append((cx, cy))
                count[labels[cy][cx]] += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    if visited[ny][nx]:
                        continue
                    if block_mask.getpixel((nx, ny)) or ny < horizon[nx]:
                        visited[ny][nx] = True
                    else:
                        visited[ny][nx] = True
                        queue.append((nx, ny))

            fill = count.most_common(1)[0][0]
            if len(pixels) < 12:
                bx0 = max(0, min_x - 2)
                bx1 = min(width - 1, max_x + 2)
                by0 = max(0, min_y - 2)
                by1 = min(height - 1, max_y + 2)
                outer = Counter(
                    labels[yy][xx]
                    for yy in range(by0, by1 + 1)
                    for xx in range(bx0, bx1 + 1)
                    if not (min_x <= xx <= max_x and min_y <= yy <= max_y)
                )
                if outer:
                    fill = outer.most_common(1)[0][0]

            for px, py in pixels:
                region_fill.putpixel((px, py), fill)

    return region_fill


def smooth_region_fill(
    region_fill: Image.Image,
    block_mask: Image.Image,
    display_mask: Image.Image,
    horizon: list[int],
    passes: int = 2,
) -> Image.Image:
    width, height = region_fill.size
    smoothed = region_fill.copy()
    for _ in range(passes):
        prev = smoothed.copy()
        for y in range(height):
            for x in range(width):
                if y < horizon[x] or display_mask.getpixel((x, y)):
                    continue
                count = Counter()
                for ny in range(max(0, y - 1), min(height, y + 2)):
                    for nx in range(max(0, x - 1), min(width, x + 2)):
                        if block_mask.getpixel((nx, ny)) or ny < horizon[nx]:
                            continue
                        count[prev.getpixel((nx, ny))] += 1
                if count:
                    smoothed.putpixel((x, y), count.most_common(1)[0][0])
    return smoothed


def build_bg_b(colors: list[tuple[int, int, int]]) -> Image.Image:
    width, height = SKY_BG_SIZE
    bg_b = Image.new("RGB", SKY_BG_SIZE, colors[0])
    if len(colors) == 1:
        return bg_b

    bands = len(colors)
    for y in range(height):
        idx = min(bands - 1, int(y / (height / bands)))
        color = colors[idx]
        for x in range(width):
            bg_b.putpixel((x, y), color)
    return bg_b.quantize(colors=bands, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")


def build_bg_a(
    smoothed: Image.Image,
    display_mask: Image.Image,
    horizon: list[int],
    use_cohesive_palette: bool,
) -> Image.Image:
    width, height = smoothed.size
    bg_a = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    sky_reserved = (24, 62, 78)

    for y in range(height):
        for x in range(width):
            if y >= horizon[x]:
                color = smoothed.getpixel((x, y))
                if use_cohesive_palette and color == sky_reserved:
                    color = (72, 118, 120)
                bg_a.putpixel((x, y), color + (255,))
            if display_mask.getpixel((x, y)) and y >= max(0, horizon[x] - 1):
                bg_a.putpixel((x, y), (0, 2, 1, 255))

    return bg_a


def compose(bg_a: Image.Image, bg_b: Image.Image) -> Image.Image:
    width, height = bg_a.size
    composite = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    for y in range(height):
        for x in range(width):
            composite.putpixel((x, y), bg_b.getpixel((x % bg_b.width, y)) + (255,))
    composite.alpha_composite(bg_a)
    return composite.convert("RGB")


def unique_tile_count(path: Path) -> int:
    image = Image.open(path).convert("RGBA")
    width, height = image.size
    tiles = set()
    for ty in range(0, height, 8):
        for tx in range(0, width, 8):
            tile = []
            for y in range(8):
                for x in range(8):
                    tile.append(image.getpixel((tx + x, ty + y)))
            tiles.add(tuple(tile))
    return len(tiles)


def save_profile(
    out_dir: Path,
    recolor: Image.Image,
    line_density: Image.Image,
    profile: Profile,
    inputs: dict[str, str],
) -> dict[str, object]:
    raw_palette = RAW_RECOLOR_PALETTE
    final_palette_map = (
        {color: COHESIVE_RECOLOR_MAP[color] for color in raw_palette}
        if profile.use_cohesive_palette
        else {color: color for color in raw_palette}
    )

    block_mask = line_density.point(lambda v, t=profile.block_threshold: 255 if v > t else 0)
    display_mask = line_density.point(lambda v, t=profile.display_threshold: 255 if v > t else 0)
    horizon = build_horizon(block_mask)
    labels = build_labels(recolor, raw_palette, final_palette_map)
    region_fill = region_fill_scene(labels, block_mask, horizon)
    smoothed = smooth_region_fill(region_fill, block_mask, display_mask, horizon)
    bg_b = build_bg_b(profile.sky_colors)
    bg_a = build_bg_a(smoothed, display_mask, horizon, profile.use_cohesive_palette)
    composite = compose(bg_a, bg_b)

    prefix = f"route_anime_linefirst_{profile.slug}"
    bg_a_path = out_dir / f"{prefix}_bg_a.png"
    bg_b_path = out_dir / f"{prefix}_bg_b.png"
    composite_path = out_dir / f"{prefix}_composite.png"
    report_path = out_dir / f"{prefix}_report.json"

    bg_a.save(bg_a_path, optimize=False)
    bg_b.save(bg_b_path, optimize=False)
    composite.save(composite_path, optimize=False)

    report = {
        "route": "anime_linefirst",
        "profile": profile.slug,
        "process": [
            "crop",
            "anime_style",
            "line_art_only",
            "megadrive_line_conversion",
            "intelligent_surface_coloring",
        ],
        "inputs": inputs,
        "thresholds": {
            "block_threshold": profile.block_threshold,
            "display_threshold": profile.display_threshold,
        },
        "palette": {
            "raw_recolor_palette": raw_palette,
            "final_palette": [final_palette_map[color] for color in raw_palette],
        },
        "sky_colors": profile.sky_colors,
        "outputs": {
            "bg_a": str(bg_a_path),
            "bg_b": str(bg_b_path),
            "composite": str(composite_path),
        },
        "budget": {
            "bg_a_unique_exact_tiles": unique_tile_count(bg_a_path),
            "bg_b_unique_exact_tiles": unique_tile_count(bg_b_path),
        },
        "notes": [
            "Line art vira contrato estrutural antes da pintura.",
            "As massas de cor sao preenchidas por regioes delimitadas pelo line art.",
            "O BG_B e gerado separadamente para manter o custo do ceu sob controle.",
        ],
    }
    report["budget"]["total_unique_exact_tiles"] = (
        report["budget"]["bg_a_unique_exact_tiles"] + report["budget"]["bg_b_unique_exact_tiles"]
    )
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def build_board(out_dir: Path, reports: list[dict[str, object]]) -> None:
    composites = []
    labels = []
    for report in reports:
        composite_path = Path(report["outputs"]["composite"])  # type: ignore[index]
        composites.append(Image.open(composite_path).convert("RGB"))
        budget = report["budget"]  # type: ignore[assignment]
        labels.append(
            f"{report['profile']} | {budget['total_unique_exact_tiles']} tiles"
        )

    if not composites:
        return

    width = max(image.width for image in composites)
    height = sum(image.height for image in composites)
    board = Image.new("RGB", (width, height), (0, 0, 0))
    cursor_y = 0
    for image in composites:
        board.paste(image, (0, cursor_y))
        cursor_y += image.height

    board_path = out_dir / "route_anime_linefirst_board.png"
    board.save(board_path, optimize=False)

    labels_path = out_dir / "route_anime_linefirst_board_labels.json"
    labels_path.write_text(json.dumps(labels, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    recolor = resize_rgb(args.recolor)
    line_density = build_line_density(args.line_art)

    profile_names = ["balanced", "cohesive"] if args.profile == "all" else [args.profile]
    reports = []
    inputs = {
        "recolor": str(Path(args.recolor)),
        "line_art": str(Path(args.line_art)),
    }
    if args.anime_style:
        inputs["anime_style"] = str(Path(args.anime_style))

    for name in profile_names:
        reports.append(save_profile(out_dir, recolor, line_density, PROFILES[name], inputs))

    build_board(out_dir, reports)


if __name__ == "__main__":
    main()
