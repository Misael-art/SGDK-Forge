#!/usr/bin/env python3
"""
analyze_aesthetic.py - Juiz estetico orientado a hardware para Mega Drive.

O objetivo nao e medir "beleza subjetiva", mas conformidade visual AAA
dentro da logica do VDP: paleta, densidade por tile 8x8, silhueta,
separacao de planos e oportunidade de reuso em VRAM.

Uso:
  python analyze_aesthetic.py --asset <png> --role sprite|bg_a|bg_b|hud \
    --reference-profile <slug> [--paired-bg <png>] [--critical-visual] \
    --output <json>
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_PROFILES_PATH = SCRIPT_DIR / "reference_profiles.json"
THRESHOLDS_PATH = SCRIPT_DIR / "aesthetic_thresholds.json"
TILE_SIZE = 8


@dataclass
class Issue:
    code: str
    severity: str
    message: str
    value: float | None = None
    threshold: float | None = None


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def score_range(value: float, minimum: float, maximum: float) -> float:
    if maximum <= minimum:
        return 1.0 if value >= minimum else 0.0
    if minimum <= value <= maximum:
        return 1.0
    if value < minimum:
        return clamp(value / minimum if minimum > 0 else 0.0)
    overflow = value - maximum
    span = max(1e-6, 1.0 - maximum)
    return clamp(1.0 - (overflow / span))


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.2126 * r) + (0.7152 * g) + (0.0722 * b)


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_configs() -> tuple[dict, dict]:
    return load_json(REFERENCE_PROFILES_PATH), load_json(THRESHOLDS_PATH)


def open_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def pad_to_tile_grid(image: Image.Image) -> Image.Image:
    width, height = image.size
    padded_w = math.ceil(width / TILE_SIZE) * TILE_SIZE
    padded_h = math.ceil(height / TILE_SIZE) * TILE_SIZE
    if (padded_w, padded_h) == image.size:
        return image
    padded = Image.new("RGBA", (padded_w, padded_h), (0, 0, 0, 0))
    padded.paste(image, (0, 0))
    return padded


def alpha_mask(image: Image.Image) -> list[list[bool]]:
    width, height = image.size
    pixels = image.load()
    has_alpha_variation = any(pixels[x, y][3] < 255 for y in range(height) for x in range(width))
    mask = []
    for y in range(height):
        row: list[bool] = []
        for x in range(width):
            visible = pixels[x, y][3] > 0 if has_alpha_variation else True
            row.append(visible)
        mask.append(row)
    return mask


def visible_rgb_counter(image: Image.Image, mask: list[list[bool]]) -> Counter:
    counter: Counter = Counter()
    pixels = image.load()
    for y, row in enumerate(mask):
        for x, visible in enumerate(row):
            if visible:
                counter[pixels[x, y][:3]] += 1
    return counter


def iter_tiles(image: Image.Image, mask: list[list[bool]]) -> Iterable[dict]:
    pixels = image.load()
    width, height = image.size
    for top in range(0, height, TILE_SIZE):
        for left in range(0, width, TILE_SIZE):
            tile_pixels = []
            tile_mask = []
            for y in range(top, top + TILE_SIZE):
                for x in range(left, left + TILE_SIZE):
                    tile_pixels.append(pixels[x, y])
                    tile_mask.append(mask[y][x])
            yield {
                "left": left,
                "top": top,
                "pixels": tuple(tile_pixels),
                "mask": tuple(tile_mask),
                "empty": not any(tile_mask)
            }


def bbox_from_mask(mask: list[list[bool]]) -> tuple[int, int, int, int] | None:
    points = [(x, y) for y, row in enumerate(mask) for x, visible in enumerate(row) if visible]
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def boundary_pixels(mask: list[list[bool]]) -> list[tuple[int, int]]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    points = []
    for y in range(height):
        for x in range(width):
            if not mask[y][x]:
                continue
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if nx < 0 or ny < 0 or nx >= width or ny >= height or not mask[ny][nx]:
                    points.append((x, y))
                    break
    return points


def connected_components(mask: list[list[bool]]) -> int:
    height = len(mask)
    width = len(mask[0]) if height else 0
    seen = [[False for _ in range(width)] for _ in range(height)]
    components = 0
    for y in range(height):
        for x in range(width):
            if not mask[y][x] or seen[y][x]:
                continue
            components += 1
            queue = deque([(x, y)])
            seen[y][x] = True
            while queue:
                cx, cy = queue.popleft()
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        queue.append((nx, ny))
    return components


def palette_efficiency(counter: Counter, cfg: dict) -> tuple[float, dict]:
    visible_pixels = sum(counter.values())
    if visible_pixels == 0:
        return 0.0, {"color_count": 0, "tonal_span": 0.0, "redundancy_ratio": 1.0, "low_usage_ratio": 1.0}

    color_count = len(counter)
    target_min, target_max = cfg["target_color_range"]
    tonal_span_target = cfg["min_tonal_span"]
    redundant_delta = cfg["redundant_luma_delta"]
    low_usage_limit = cfg["low_usage_ratio"]

    count_score = score_range(color_count, target_min, target_max)
    lumas = sorted(luminance(color) for color in counter)
    tonal_span = lumas[-1] - lumas[0] if len(lumas) > 1 else 0.0
    tonal_span_score = clamp(tonal_span / tonal_span_target if tonal_span_target > 0 else 0.0)
    redundant_pairs = sum(1 for a, b in zip(lumas, lumas[1:]) if abs(b - a) < redundant_delta)
    redundancy_ratio = redundant_pairs / max(1, len(lumas) - 1)
    low_usage_colors = sum(1 for count in counter.values() if (count / visible_pixels) < low_usage_limit)
    low_usage_ratio = low_usage_colors / max(1, color_count)

    score = clamp((0.4 * count_score) + (0.35 * tonal_span_score) + (0.25 * (1.0 - max(redundancy_ratio, low_usage_ratio))))
    return score, {
        "color_count": color_count,
        "tonal_span": tonal_span,
        "redundancy_ratio": redundancy_ratio,
        "low_usage_ratio": low_usage_ratio
    }


def tile_efficiency(mask: list[list[bool]], tiles: list[dict], cfg: dict) -> tuple[float, dict]:
    bbox = bbox_from_mask(mask)
    total_tiles = len(tiles)
    empty_tiles = sum(1 for tile in tiles if tile["empty"])
    empty_ratio = empty_tiles / max(1, total_tiles)

    if bbox is None:
        bbox_waste = 1.0
    else:
        min_x, min_y, max_x, max_y = bbox
        bbox_area = (max_x - min_x + 1) * (max_y - min_y + 1)
        used_pixels = sum(1 for row in mask for visible in row if visible)
        bbox_waste = 1.0 - (used_pixels / max(1, bbox_area))

    empty_score = clamp(1.0 - (empty_ratio / max(cfg["max_empty_ratio"], 1e-6)))
    bbox_score = clamp(1.0 - (bbox_waste / max(cfg["max_bbox_waste"], 1e-6)))
    return clamp((0.55 * empty_score) + (0.45 * bbox_score)), {
        "empty_ratio": empty_ratio,
        "bbox_waste": bbox_waste,
        "total_tiles": total_tiles,
        "empty_tiles": empty_tiles
    }


def detail_density(image: Image.Image, mask: list[list[bool]], tiles: list[dict], cfg: dict) -> tuple[float, dict]:
    width, height = image.size
    pixels = image.load()
    transition_samples: list[float] = []
    isolated_samples: list[float] = []

    for tile in tiles:
        if tile["empty"]:
            continue
        left = tile["left"]
        top = tile["top"]
        comparisons = 0
        transitions = 0
        isolated = 0
        visible_count = 0
        for y in range(top, min(top + TILE_SIZE, height)):
            for x in range(left, min(left + TILE_SIZE, width)):
                if not mask[y][x]:
                    continue
                visible_count += 1
                same_neighbors = 0
                current = pixels[x, y][:3]
                for nx, ny in ((x + 1, y), (x, y + 1)):
                    if nx < width and ny < height and mask[ny][nx]:
                        comparisons += 1
                        if pixels[nx, ny][:3] != current:
                            transitions += 1
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and pixels[nx, ny][:3] == current:
                        same_neighbors += 1
                if same_neighbors == 0:
                    isolated += 1

        if visible_count == 0:
            continue
        transition_samples.append(transitions / max(1, comparisons))
        isolated_samples.append(isolated / visible_count)

    avg_transition = sum(transition_samples) / max(1, len(transition_samples))
    avg_isolated = sum(isolated_samples) / max(1, len(isolated_samples))
    transition_score = score_range(avg_transition, cfg["min_transition_density"], cfg["max_transition_density"])
    isolated_score = clamp(1.0 - (avg_isolated / max(cfg["max_isolated_ratio"], 1e-6)))
    return clamp((0.7 * transition_score) + (0.3 * isolated_score)), {
        "avg_transition_density": avg_transition,
        "avg_isolated_ratio": avg_isolated,
        "non_empty_tiles": len(transition_samples)
    }


def dithering_density(image: Image.Image, mask: list[list[bool]], cfg: dict) -> tuple[float, dict]:
    width, height = image.size
    pixels = image.load()
    dither_blocks = 0
    noisy_blocks = 0
    total_blocks = 0
    for y in range(height - 1):
        for x in range(width - 1):
            coords = ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))
            if not all(mask[cy][cx] for cx, cy in coords):
                continue
            colors = [pixels[cx, cy][:3] for cx, cy in coords]
            unique_colors = list(dict.fromkeys(colors))
            total_blocks += 1
            if len(unique_colors) == 2:
                a, b = unique_colors
                if colors[0] == colors[3] == a and colors[1] == colors[2] == b:
                    dither_blocks += 1
                elif colors[0] == colors[3] == b and colors[1] == colors[2] == a:
                    dither_blocks += 1
            elif len(unique_colors) >= 3:
                noisy_blocks += 1

    if total_blocks == 0:
        return 1.0, {"dither_ratio": 0.0, "noise_ratio": 0.0, "samples": 0}

    dither_ratio = dither_blocks / total_blocks
    noise_ratio = noisy_blocks / total_blocks
    preferred_min = cfg["preferred_min"]
    preferred_max = cfg["preferred_max"]
    noise_guard = cfg["noise_guard_max"]
    dither_score = score_range(dither_ratio, preferred_min, preferred_max) if preferred_min > 0 else 1.0
    noise_score = clamp(1.0 - (noise_ratio / max(noise_guard, 1e-6)))
    return clamp((0.65 * dither_score) + (0.35 * noise_score)), {
        "dither_ratio": dither_ratio,
        "noise_ratio": noise_ratio,
        "samples": total_blocks
    }


def silhouette_readability(image: Image.Image, mask: list[list[bool]], cfg: dict) -> tuple[float, dict]:
    bbox = bbox_from_mask(mask)
    if bbox is None:
        return 0.0, {"boundary_contrast": 0.0, "fill_ratio": 0.0, "components": 0}

    width, height = image.size
    pixels = image.load()
    min_x, min_y, max_x, max_y = bbox
    bbox_area = (max_x - min_x + 1) * (max_y - min_y + 1)
    fill_ratio = sum(1 for row in mask for visible in row if visible) / max(1, bbox_area)
    components = connected_components(mask)

    boundary = boundary_pixels(mask)
    contrast_samples = []
    for x, y in boundary:
        inner_lumas = []
        current_luma = luminance(pixels[x, y][:3])
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height and mask[ny][nx]:
                inner_lumas.append(luminance(pixels[nx, ny][:3]))
        if inner_lumas:
            contrast_samples.append(abs(current_luma - (sum(inner_lumas) / len(inner_lumas))))

    boundary_contrast = sum(contrast_samples) / max(1, len(contrast_samples))
    contrast_score = clamp(boundary_contrast / max(cfg["min_boundary_contrast"], 1e-6))
    fill_score = clamp(fill_ratio / max(cfg["min_fill_ratio"], 1e-6))
    component_score = clamp(1.0 - max(0, components - cfg["max_components"]) / max(1, cfg["max_components"]))
    return clamp((0.4 * contrast_score) + (0.35 * fill_score) + (0.25 * component_score)), {
        "boundary_contrast": boundary_contrast,
        "fill_ratio": fill_ratio,
        "components": components
    }


def layer_separation(
    image: Image.Image,
    mask: list[list[bool]],
    paired_bg: Path | None,
    role_cfg: dict,
    role: str
) -> tuple[float, dict]:
    if not paired_bg:
        default_score = role_cfg["default_unpaired_score"]
        return default_score, {"contrast_value": 0.0, "source": "unpaired_estimate"}

    background = open_rgba(paired_bg).resize(image.size, Image.Resampling.NEAREST)
    img_pixels = image.load()
    bg_pixels = background.load()
    width, height = image.size
    deltas = []

    for y in range(height):
        for x in range(width):
            if not mask[y][x]:
                continue
            asset_luma = luminance(img_pixels[x, y][:3])
            bg_luma = luminance(bg_pixels[x, y][:3])
            deltas.append(abs(asset_luma - bg_luma))

    contrast_value = sum(deltas) / max(1, len(deltas))
    contrast_score = clamp(contrast_value / max(role_cfg["min_contrast_with_pair"], 1e-6))
    return contrast_score, {"contrast_value": contrast_value, "source": "paired_bg"}


def reuse_opportunity(tiles: list[dict]) -> tuple[float, dict]:
    non_empty = [tile["pixels"] for tile in tiles if not tile["empty"]]
    if not non_empty:
        return 1.0, {"non_empty_tiles": 0, "exact_duplicates": 0, "flip_reuse_ratio": 0.0}

    exact_unique = {tile for tile in non_empty}

    def flip_h(tile: tuple) -> tuple:
        rows = [tile[index:index + TILE_SIZE] for index in range(0, len(tile), TILE_SIZE)]
        flipped_rows = [tuple(reversed(row)) for row in rows]
        return tuple(pixel for row in flipped_rows for pixel in row)

    def flip_v(tile: tuple) -> tuple:
        rows = [tile[index:index + TILE_SIZE] for index in range(0, len(tile), TILE_SIZE)]
        return tuple(pixel for row in reversed(rows) for pixel in row)

    def canonical(tile: tuple) -> tuple:
        candidates = (tile, flip_h(tile), flip_v(tile), flip_v(flip_h(tile)))
        return min(candidates)

    flip_unique = {canonical(tile) for tile in non_empty}
    exact_duplicates = len(non_empty) - len(exact_unique)
    flip_savings = len(non_empty) - len(flip_unique)
    flip_reuse_ratio = flip_savings / max(1, len(non_empty))
    return clamp(flip_reuse_ratio), {
        "non_empty_tiles": len(non_empty),
        "exact_duplicates": exact_duplicates,
        "flip_reuse_ratio": flip_reuse_ratio
    }


def recommendation_for_issue(code: str) -> str:
    mapping = {
        "PALETTE_WASTE": "Consolidar tons redundantes e preservar apenas diferencas tonais que melhoram leitura material.",
        "LOW_TILE_DENSITY": "Aumentar leitura por tile 8x8 com plano de luz, sombra e textura funcional, sem virar ruido.",
        "OVER_EMPTY_TILES": "Apertar bounding box, cortar bordas vazias e revisar custo de VRAM do asset.",
        "WEAK_SILHOUETTE": "Fortalecer massa principal, outline e contraste interno para leitura em 1 frame.",
        "LOW_LAYER_SEPARATION": "Separar melhor o valor medio do asset em relacao ao plano pareado.",
        "MISSING_DITHERING_FOR_MATERIAL": "Adicionar dithering apenas onde ele descreve material ou transicao tonal real.",
        "NOISY_TEXTURE": "Limpar ruido de alta frequencia e reorganizar o detalhe para que ele explique materia.",
        "LOW_REFERENCE_ALIGNMENT": "Comparar o asset com o benchmark escolhido e ajustar o equilibrio entre leitura, detalhe e paleta."
    }
    return mapping.get(code, "Revisar o asset contra a skill visual-excellence-standards e o benchmark selecionado.")


def build_issues(
    metrics: dict,
    inputs: dict,
    role_cfg: dict,
    score: float,
    reference_alignment: float
) -> list[Issue]:
    issues: list[Issue] = []

    if metrics["palette_efficiency"] < 0.55:
        issues.append(Issue("PALETTE_WASTE", "warning", "Paleta com baixa eficiencia tonal ou cores redundantes.", metrics["palette_efficiency"], 0.55))
    if metrics["tile_efficiency"] < 0.55 or inputs["tile_efficiency"]["empty_ratio"] > role_cfg["tile"]["max_empty_ratio"]:
        issues.append(Issue("OVER_EMPTY_TILES", "warning", "O asset desperdiça tiles com vazio ou bounding box frouxo.", inputs["tile_efficiency"]["empty_ratio"], role_cfg["tile"]["max_empty_ratio"]))
    if metrics["detail_density_8x8"] < 0.52:
        issues.append(Issue("LOW_TILE_DENSITY", "warning", "Os tiles 8x8 estao com detalhe insuficiente para a meta de leitura.", metrics["detail_density_8x8"], 0.52))
    if inputs["detail_density_8x8"]["avg_isolated_ratio"] > role_cfg["detail"]["max_isolated_ratio"] or inputs["dithering_density"]["noise_ratio"] > role_cfg["dithering"]["noise_guard_max"]:
        issues.append(Issue("NOISY_TEXTURE", "warning", "A textura esta operando como ruido, nao como material.", inputs["detail_density_8x8"]["avg_isolated_ratio"], role_cfg["detail"]["max_isolated_ratio"]))
    if role_cfg["dithering"]["preferred_min"] > 0 and inputs["dithering_density"]["dither_ratio"] < role_cfg["dithering"]["preferred_min"]:
        issues.append(Issue("MISSING_DITHERING_FOR_MATERIAL", "warning", "O asset esta abaixo da densidade minima de dithering esperada para o papel informado.", inputs["dithering_density"]["dither_ratio"], role_cfg["dithering"]["preferred_min"]))
    if metrics["silhouette_readability"] < 0.56:
        issues.append(Issue("WEAK_SILHOUETTE", "warning", "A silhueta nao sustenta leitura forte em escala nativa.", metrics["silhouette_readability"], 0.56))
    if inputs["layer_separation"]["source"] == "paired_bg" and metrics["layer_separation"] < 0.55:
        issues.append(Issue("LOW_LAYER_SEPARATION", "warning", "O asset nao se separa o suficiente do plano pareado.", inputs["layer_separation"]["contrast_value"], role_cfg["layer"]["min_contrast_with_pair"]))
    if reference_alignment < role_cfg["status"]["needs_review_min"] or score < role_cfg["status"]["needs_review_min"]:
        issues.append(Issue("LOW_REFERENCE_ALIGNMENT", "warning", "O asset ainda nao se sustenta contra o benchmark escolhido.", reference_alignment, role_cfg["status"]["needs_review_min"]))

    return issues


def analyze(asset_path: Path, role: str, reference_profile: str, paired_bg: Path | None, critical_visual: bool) -> dict:
    profiles_data, thresholds = load_configs()
    profiles = profiles_data["profiles"]
    selected_profile = profiles.get(reference_profile) or profiles[profiles_data["default_profile"]]
    role_cfg = thresholds["roles"][role]
    image = pad_to_tile_grid(open_rgba(asset_path))
    mask = alpha_mask(image)
    tiles = list(iter_tiles(image, mask))
    counter = visible_rgb_counter(image, mask)

    palette_score, palette_inputs = palette_efficiency(counter, role_cfg["palette"])
    tile_score, tile_inputs = tile_efficiency(mask, tiles, role_cfg["tile"])
    detail_score, detail_inputs = detail_density(image, mask, tiles, role_cfg["detail"])
    dither_score, dither_inputs = dithering_density(image, mask, role_cfg["dithering"])
    silhouette_score, silhouette_inputs = silhouette_readability(image, mask, role_cfg["silhouette"])
    layer_score, layer_inputs = layer_separation(image, mask, paired_bg, role_cfg["layer"], role)
    reuse_value, reuse_inputs = reuse_opportunity(tiles)
    reuse_efficiency = 1.0 - reuse_value

    weights = selected_profile["weights"].get(role) or profiles[profiles_data["default_profile"]]["weights"][role]
    weighted_metrics = {
        "palette_efficiency": palette_score,
        "tile_efficiency": tile_score,
        "detail_density_8x8": detail_score,
        "dithering_density": dither_score,
        "silhouette_readability": silhouette_score,
        "layer_separation": layer_score,
        "reuse_efficiency": reuse_efficiency
    }
    reference_alignment = sum(weighted_metrics[key] * weight for key, weight in weights.items())

    metrics = {
        "palette_efficiency": round(palette_score, 4),
        "tile_efficiency": round(tile_score, 4),
        "detail_density_8x8": round(detail_score, 4),
        "dithering_density": round(dither_score, 4),
        "silhouette_readability": round(silhouette_score, 4),
        "layer_separation": round(layer_score, 4),
        "reuse_opportunity": round(reuse_value, 4),
        "reference_alignment": round(reference_alignment, 4),
        "visual_excellence_score": round(reference_alignment, 4)
    }
    metric_inputs = {
        "palette_efficiency": palette_inputs,
        "tile_efficiency": tile_inputs,
        "detail_density_8x8": detail_inputs,
        "dithering_density": dither_inputs,
        "silhouette_readability": silhouette_inputs,
        "layer_separation": layer_inputs,
        "reuse_opportunity": reuse_inputs
    }

    issues = build_issues(metrics, metric_inputs, role_cfg, reference_alignment, reference_alignment)
    error_issue_count = sum(1 for issue in issues if issue.severity == "error")
    elite_min = role_cfg["status"]["elite_ready_min"]
    review_min = role_cfg["status"]["needs_review_min"]
    if reference_alignment >= elite_min and error_issue_count == 0 and len(issues) <= 1:
        status = "elite_ready"
    elif reference_alignment >= review_min and error_issue_count == 0:
        status = "needs_review"
    else:
        status = "rework"

    recommendations = []
    seen_recommendations = set()
    for issue in issues:
        recommendation = recommendation_for_issue(issue.code)
        if recommendation not in seen_recommendations:
            recommendations.append(recommendation)
            seen_recommendations.add(recommendation)

    return {
        "asset_path": str(asset_path),
        "role": role,
        "reference_profile": reference_profile if reference_profile in profiles else profiles_data["default_profile"],
        "critical_visual": critical_visual,
        "paired_bg": str(paired_bg) if paired_bg else None,
        "status": status,
        "metrics": metrics,
        "metric_inputs": metric_inputs,
        "issues": [asdict(issue) for issue in issues],
        "recommendations": recommendations,
        "benchmarks": selected_profile["benchmarks"]
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Juiz estetico orientado a hardware para assets de Mega Drive.")
    parser.add_argument("--asset", required=True, help="PNG do asset principal.")
    parser.add_argument(
        "--role",
        required=True,
        choices=("sprite", "bg_a", "bg_b", "hud", "midground_layer", "foreground_layer"),
        help="Papel do asset."
    )
    parser.add_argument("--reference-profile", required=True, help="Slug do perfil de benchmark.")
    parser.add_argument("--paired-bg", default=None, help="Asset pareado para medir layer separation.")
    parser.add_argument("--critical-visual", action="store_true", help="Marca o asset como visualmente critico.")
    parser.add_argument("--output", required=True, help="Arquivo JSON de saida.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    asset_path = Path(args.asset).resolve()
    if not asset_path.is_file():
        print(f"Erro: asset nao encontrado: {asset_path}", file=sys.stderr)
        return 1

    paired_bg = Path(args.paired_bg).resolve() if args.paired_bg else None
    if paired_bg and not paired_bg.is_file():
        print(f"Erro: paired-bg nao encontrado: {paired_bg}", file=sys.stderr)
        return 1

    result = analyze(
        asset_path=asset_path,
        role=args.role,
        reference_profile=args.reference_profile,
        paired_bg=paired_bg,
        critical_visual=args.critical_visual
    )

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)

    print(json.dumps({
        "asset_path": result["asset_path"],
        "status": result["status"],
        "visual_excellence_score": result["metrics"]["visual_excellence_score"]
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
