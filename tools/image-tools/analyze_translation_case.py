#!/usr/bin/env python3
"""
analyze_translation_case.py - avaliador generico da skill art-translation-to-vdp.

Compara duas variantes de traducao (`basic` e `elite`) de um mesmo caso,
usa o juiz estetico existente por unidade de analise e produz um laudo
agregado para curadoria e acuracia da skill.

Uso:
  python analyze_translation_case.py --manifest <json> --output <json>
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
AESTHETIC_ANALYZER = SCRIPT_DIR / "analyze_aesthetic.py"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def contain_on_canvas(image: Image.Image, size: tuple[int, int], background: tuple[int, int, int, int]) -> Image.Image:
    fitted = ImageOps.contain(image.convert("RGBA"), size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", size, background)
    left = max(0, (size[0] - fitted.width) // 2)
    top = max(0, (size[1] - fitted.height) // 2)
    canvas.alpha_composite(fitted, (left, top))
    return canvas


def sort_preview_units(units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    role_order = {
        "bg_b": 0,
        "midground_layer": 1,
        "bg_a": 2,
        "foreground_layer": 3,
        "sprite": 4,
        "hud": 5,
    }
    return sorted(units, key=lambda unit: (role_order.get(unit["role"], 99), unit["name"]))


def compose_variant_preview(units: list[dict[str, Any]]) -> Image.Image:
    ordered = sort_preview_units(units)
    first_image = Image.open(ordered[0]["normalized_asset_path"]).convert("RGBA")
    canvas = Image.new("RGBA", first_image.size, (0, 0, 0, 0))

    for unit in ordered:
        layer = Image.open(unit["normalized_asset_path"]).convert("RGBA")
        if layer.size != canvas.size:
            layer = layer.resize(canvas.size, Image.Resampling.NEAREST)
        canvas = Image.alpha_composite(canvas, layer)

    return canvas


def infer_preview_size(source_image: Path | None, variants: dict[str, Any]) -> tuple[int, int]:
    sizes: list[tuple[int, int]] = []
    if source_image and source_image.is_file():
        with Image.open(source_image) as image:
            sizes.append(image.size)

    for variant in variants.values():
        for unit in variant["units"]:
            with Image.open(unit["normalized_asset_path"]) as image:
                sizes.append(image.size)

    if not sizes:
        return (320, 224)

    best = max(sizes, key=lambda item: item[0] * item[1])
    width = min(448, max(256, best[0]))
    height = min(320, max(160, best[1]))
    return (width, height)


def render_human_validation_panel(
    output_path: Path,
    source_image: Path | None,
    variants: dict[str, Any],
    comparison: dict[str, Any]
) -> Path:
    preview_size = infer_preview_size(source_image, variants)
    gap = 12
    header_h = 42
    footer_h = 34
    panel_w = (preview_size[0] * 3) + (gap * 4)
    panel_h = preview_size[1] + header_h + footer_h + (gap * 2)
    panel = Image.new("RGBA", (panel_w, panel_h), (14, 22, 28, 255))
    draw = ImageDraw.Draw(panel)

    cards = [
        ("ORIGINAL", source_image),
        ("BASIC", None),
        ("ELITE", None),
    ]

    previews: list[tuple[str, Image.Image]] = []
    if source_image and source_image.is_file():
        with Image.open(source_image) as image:
            previews.append(("ORIGINAL", contain_on_canvas(image, preview_size, (24, 34, 40, 255))))
    else:
        previews.append(("ORIGINAL", Image.new("RGBA", preview_size, (24, 34, 40, 255))))

    previews.append(("BASIC", contain_on_canvas(compose_variant_preview(variants["basic"]["units"]), preview_size, (24, 34, 40, 255))))
    previews.append(("ELITE", contain_on_canvas(compose_variant_preview(variants["elite"]["units"]), preview_size, (24, 34, 40, 255))))

    score_map = {
        "ORIGINAL": None,
        "BASIC": variants["basic"]["aggregate_score"],
        "ELITE": variants["elite"]["aggregate_score"],
    }

    for index, (label, image) in enumerate(previews):
        x = gap + (index * (preview_size[0] + gap))
        y = gap
        draw.rounded_rectangle((x, y, x + preview_size[0], y + panel_h - (gap * 2)), radius=10, fill=(20, 30, 36, 255))
        draw.rectangle((x, y, x + preview_size[0], y + header_h), fill=(28, 42, 48, 255))
        title = label
        if score_map[label] is not None:
            title = f"{label}  score={score_map[label]:.4f}"
        draw.text((x + 10, y + 12), title, fill=(230, 236, 238, 255))
        panel.alpha_composite(image, (x, y + header_h))

    footer_y = gap + header_h + preview_size[1] + 8
    summary = (
        f"status={comparison['status']}  "
        f"basic={comparison['basic_score']:.4f}  "
        f"elite={comparison['elite_score']:.4f}  "
        f"delta={comparison['elite_minus_basic']:.4f}"
    )
    draw.text((gap + 8, footer_y), summary, fill=(214, 224, 228, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def render_semantic_decomposition_panel(
    output_path: Path,
    source_image: Path | None,
    semantic_map: dict[str, Any] | None,
    variants: dict[str, Any],
) -> Path | None:
    if source_image is None or not source_image.is_file() or not semantic_map:
        return None

    usable_regions = semantic_map.get("usable_regions", [])
    if not usable_regions:
        return None

    elite_units = variants.get("elite", {}).get("units", [])
    if not elite_units:
        return None

    preview_size = (220, 160)
    gap = 12
    header_h = 42
    footer_h = 40

    cards: list[tuple[str, Image.Image]] = []
    with Image.open(source_image) as image:
        cards.append(("ORIGINAL", contain_on_canvas(image, preview_size, (24, 34, 40, 255))))

    for region in usable_regions:
        region_id = region.get("id")
        if not region_id:
            continue
        matched = None
        for unit in elite_units:
            if unit.get("semantic_region_id") == region_id or unit.get("name") == region_id:
                matched = unit
                break
        if matched is None:
            continue
        with Image.open(matched["normalized_asset_path"]) as image:
            label = f"{region_id} | {region.get('kind', 'region')}"
            cards.append((label, contain_on_canvas(image, preview_size, (24, 34, 40, 255))))

    composed = contain_on_canvas(compose_variant_preview(elite_units), preview_size, (24, 34, 40, 255))
    cards.append(("ELITE REMONTADO", composed))

    panel_w = (preview_size[0] * len(cards)) + (gap * (len(cards) + 1))
    panel_h = preview_size[1] + header_h + footer_h + (gap * 2)
    panel = Image.new("RGBA", (panel_w, panel_h), (14, 22, 28, 255))
    draw = ImageDraw.Draw(panel)

    for index, (label, image) in enumerate(cards):
        x = gap + (index * (preview_size[0] + gap))
        y = gap
        draw.rounded_rectangle((x, y, x + preview_size[0], y + panel_h - (gap * 2)), radius=10, fill=(20, 30, 36, 255))
        draw.rectangle((x, y, x + preview_size[0], y + header_h), fill=(28, 42, 48, 255))
        draw.text((x + 10, y + 12), label, fill=(230, 236, 238, 255))
        panel.alpha_composite(image, (x, y + header_h))

    footer_text = "ORIGINAL -> A/B/C extraidos -> ELITE remontado"
    draw.text((gap + 8, gap + header_h + preview_size[1] + 10), footer_text, fill=(214, 224, 228, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def find_project_root(start_path: Path) -> Path | None:
    for parent in [start_path.parent] + list(start_path.parents):
        if (parent / "res").is_dir() and (parent / "src").is_dir():
            return parent
    return None


def resolve_path(manifest_path: Path, project_root: Path | None, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None

    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve() if candidate.exists() else None

    for base in [manifest_path.parent, project_root, WORKSPACE_ROOT]:
        if base is None:
            continue
        resolved = (base / raw_path).resolve()
        if resolved.exists():
            return resolved

    return None


def indexed_zero_to_transparent(source: Path, destination: Path) -> Path:
    image = Image.open(source)

    if image.mode != "P":
        rgba = image.convert("RGBA")
        destination.parent.mkdir(parents=True, exist_ok=True)
        rgba.save(destination)
        return destination

    rgba = image.convert("RGBA")
    index_pixels = image.load()
    rgba_pixels = rgba.load()
    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b, _ = rgba_pixels[x, y]
            alpha = 0 if index_pixels[x, y] == 0 else 255
            rgba_pixels[x, y] = (r, g, b, alpha)

    destination.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(destination)
    return destination


def compose_layers(layer_paths: list[Path], destination: Path) -> Path:
    if not layer_paths:
        raise ValueError("compose_layers requer pelo menos uma camada.")

    composed = Image.open(layer_paths[0]).convert("RGBA")
    for layer_path in layer_paths[1:]:
        layer = Image.open(layer_path).convert("RGBA")
        if layer.size != composed.size:
            layer = layer.resize(composed.size, Image.Resampling.NEAREST)
        composed = Image.alpha_composite(composed, layer)

    destination.parent.mkdir(parents=True, exist_ok=True)
    composed.save(destination)
    return destination


def run_aesthetic_analysis(
    asset_path: Path,
    role: str,
    reference_profile: str,
    output_path: Path,
    paired_bg: Path | None,
    critical_visual: bool
) -> dict[str, Any]:
    args = [
        sys.executable,
        str(AESTHETIC_ANALYZER),
        "--asset",
        str(asset_path),
        "--role",
        role,
        "--reference-profile",
        reference_profile,
        "--output",
        str(output_path),
    ]

    if paired_bg is not None:
        args.extend(["--paired-bg", str(paired_bg)])
    if critical_visual:
        args.append("--critical-visual")

    completed = subprocess.run(args, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"analyze_aesthetic.py falhou para {asset_path}: {stderr}")

    return load_json(output_path)


def aggregate_status(analyses: list[dict[str, Any]]) -> str:
    statuses = {analysis["status"] for analysis in analyses}
    if "rework" in statuses:
        return "rework"
    if "needs_review" in statuses:
        return "needs_review"
    return "elite_ready"


def weighted_score(units: list[dict[str, Any]]) -> float:
    total_weight = sum(float(unit["weight"]) for unit in units)
    if total_weight <= 0:
        return 0.0

    total_score = 0.0
    for unit in units:
        total_score += float(unit["analysis"]["metrics"]["visual_excellence_score"]) * float(unit["weight"])
    return round(total_score / total_weight, 4)


def dominant_color_candidate(image: Image.Image, step: int = 2) -> tuple[int, int, int]:
    counts: dict[tuple[int, int, int], int] = {}
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()

    for y in range(0, height, step):
        for x in range(0, width, step):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            key = (round(r / 16) * 16, round(g / 16) * 16, round(b / 16) * 16)
            counts[key] = counts.get(key, 0) + 1

    if not counts:
        return (0, 0, 0)
    return max(counts.items(), key=lambda item: item[1])[0]


def color_distance(rgb_a: tuple[int, int, int], rgb_b: tuple[int, int, int]) -> float:
    return (
        ((rgb_a[0] - rgb_b[0]) ** 2)
        + ((rgb_a[1] - rgb_b[1]) ** 2)
        + ((rgb_a[2] - rgb_b[2]) ** 2)
    ) ** 0.5


def editorial_sheet_contamination(asset_path: Path, block_size: int = 16) -> tuple[float, dict[str, Any]]:
    image = Image.open(asset_path).convert("RGBA")
    width, height = image.size
    bg = dominant_color_candidate(image)
    pixels = image.load()

    grid_w = max(1, (width + block_size - 1) // block_size)
    grid_h = max(1, (height + block_size - 1) // block_size)
    occupied = [[False for _ in range(grid_w)] for _ in range(grid_h)]

    for gy in range(grid_h):
        for gx in range(grid_w):
            left = gx * block_size
            top = gy * block_size
            changed = 0
            total = 0
            for y in range(top, min(top + block_size, height)):
                for x in range(left, min(left + block_size, width)):
                    r, g, b, a = pixels[x, y]
                    if a == 0:
                        continue
                    total += 1
                    if color_distance((r, g, b), bg) > 42:
                        changed += 1
            if total and (changed / total) >= 0.18:
                occupied[gy][gx] = True

    visited = [[False for _ in range(grid_w)] for _ in range(grid_h)]
    component_sizes: list[int] = []
    occupied_blocks = sum(1 for row in occupied for value in row if value)

    for gy in range(grid_h):
        for gx in range(grid_w):
            if not occupied[gy][gx] or visited[gy][gx]:
                continue
            stack = [(gx, gy)]
            visited[gy][gx] = True
            size = 0
            while stack:
                cx, cy = stack.pop()
                size += 1
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < grid_w and 0 <= ny < grid_h and occupied[ny][nx] and not visited[ny][nx]:
                        visited[ny][nx] = True
                        stack.append((nx, ny))
            if size >= 4:
                component_sizes.append(size)

    component_sizes.sort(reverse=True)
    occupied_ratio = occupied_blocks / max(1, grid_w * grid_h)
    largest_ratio = (component_sizes[0] / max(1, occupied_blocks)) if component_sizes else 0.0
    multi_panel = (
        (len(component_sizes) >= 3 and largest_ratio < 0.82 and occupied_ratio < 0.9)
        or (len(component_sizes) >= 2 and largest_ratio < 0.82 and occupied_ratio < 0.85)
    )

    if not multi_panel:
        return 0.0, {
            "source": "clean_scene_assumption",
            "dominant_background": bg,
            "occupied_ratio": round(occupied_ratio, 4),
            "large_components": len(component_sizes),
            "largest_component_ratio": round(largest_ratio, 4),
        }

    penalty = min(0.22, 0.08 + (0.025 * max(0, len(component_sizes) - 3)) + (0.18 * (1.0 - largest_ratio)))
    return round(penalty, 4), {
        "source": "editorial_sheet_contamination",
        "dominant_background": bg,
        "occupied_ratio": round(occupied_ratio, 4),
        "large_components": len(component_sizes),
        "largest_component_ratio": round(largest_ratio, 4),
        "penalty": round(penalty, 4),
    }


def apply_case_penalties(
    analysis: dict[str, Any],
    asset_path: Path,
    translation_target: str | None,
    role: str
) -> dict[str, Any]:
    if translation_target not in {"scene_slice", "tilemap"}:
        return analysis

    if role in {"midground_layer", "foreground_layer"}:
        analysis.setdefault("case_penalties", []).append(
            {
                "source": "semantic_layer_exemption",
                "role": role,
                "reason": "camada semantica isolada avaliada fora da composicao editorial"
            }
        )
        return analysis

    penalty, details = editorial_sheet_contamination(asset_path)
    if penalty <= 0:
        analysis.setdefault("case_penalties", []).append(details)
        return analysis

    for key in ("reference_alignment", "visual_excellence_score"):
        analysis["metrics"][key] = round(max(0.0, float(analysis["metrics"][key]) - penalty), 4)

    analysis.setdefault("case_penalties", []).append(details)
    analysis.setdefault("issues", []).append(
        {
            "code": "EDITORIAL_SHEET_CONTAMINATION",
            "severity": "warning",
            "message": "A traducao ainda carrega sinais de sheet editorial ou multiplos paineis em vez de um frame jogavel limpo.",
            "value": penalty,
            "threshold": 0.0,
        }
    )

    recommendation = "Isolar a regiao jogavel e desmontar a sheet-fonte antes da traducao final."
    recommendations = analysis.setdefault("recommendations", [])
    if recommendation not in recommendations:
        recommendations.insert(0, recommendation)

    if analysis["status"] == "elite_ready":
        analysis["status"] = "needs_review"

    return analysis


def build_semantic_stage_review(
    manifest: dict[str, Any],
    variants: dict[str, Any],
) -> dict[str, Any]:
    semantic_parse = manifest.get("semantic_parse_report", {}) or {}
    semantic_map = manifest.get("source_semantic_map", {}) or {}
    source_layout_type = semantic_parse.get("source_layout_type") or semantic_map.get("source_layout_type")
    composition_schema = manifest.get("composition_schema", {}) or {}
    source_inventory = manifest.get("source_inventory", {}) or {}
    drop_policy = manifest.get("drop_policy", {}) or {}
    issues: list[dict[str, Any]] = []

    if source_layout_type in {"editorial_board", "scene_sheet", "sprite_sheet", "tilemap_sheet"} and not semantic_parse:
        issues.append(
            {
                "code": "MISSING_SEMANTIC_PARSE_REPORT",
                "message": "Fonte complexa sem `semantic_parse_report`; a traducao pode estar quantizando antes de entender o source.",
            }
        )

    if source_layout_type in {"editorial_board", "scene_sheet", "sprite_sheet", "tilemap_sheet"} and not source_inventory:
        issues.append(
            {
                "code": "MISSING_SOURCE_INVENTORY",
                "message": "Faltou inventario do source para distinguir cena util de ruido editorial.",
            }
        )

    if source_layout_type in {"editorial_board", "scene_sheet", "sprite_sheet", "tilemap_sheet"} and not drop_policy:
        issues.append(
            {
                "code": "MISSING_DROP_POLICY",
                "message": "Faltou politica explicita de descarte para previews, creditos, avatar ou metadata.",
            }
        )

    if manifest.get("translation_target") == "scene_slice" and not composition_schema.get("roles"):
        issues.append(
            {
                "code": "MISSING_COMPOSITION_SCHEMA",
                "message": "Scene slice sem composition schema; a remontagem pode perder quadro espacial comum.",
            }
        )

    dropped_region_ids = {
        item["id"]
        for item in semantic_parse.get("drop_regions", [])
        if item.get("id")
    }
    for item in semantic_map.get("annotation_regions", []):
        if item.get("id") and item.get("action") == "drop":
            dropped_region_ids.add(item["id"])

    region_classifications: dict[str, str] = {}
    for item in semantic_parse.get("semantic_regions", []):
        if item.get("id") and item.get("classification"):
            region_classifications[item["id"]] = item["classification"]
    for item in semantic_map.get("usable_regions", []):
        if item.get("id") and item.get("kind"):
            region_classifications.setdefault(item["id"], item["kind"])

    allowed_roles_by_classification = {
        "scene_plane_bg_b": {"bg_b", "midground_layer"},
        "scene_plane_bg_a": {"bg_a", "midground_layer"},
        "scene_plane_foreground_composition": {"foreground_layer", "midground_layer"},
        "scene_plane_sky": {"bg_b", "midground_layer"},
        "scene_plane_architecture": {"bg_a", "midground_layer"},
        "scene_plane_ground": {"bg_a", "midground_layer", "foreground_layer"},
        "actor_sprite_sheet": {"sprite"},
        "palette_strip": {"hud"},
        "tile_cluster": {"bg_a", "bg_b", "midground_layer", "foreground_layer"},
        "overlay_cluster": {"foreground_layer", "midground_layer"},
        "object_animation_sequence": {"foreground_layer", "sprite"},
    }

    for variant_name, variant in variants.items():
        for unit in variant["units"]:
            region_id = unit.get("semantic_region_id")
            if not region_id:
                continue
            if region_id in dropped_region_ids:
                issues.append(
                    {
                        "code": "DROP_REGION_PROMOTED_TO_SCENE",
                        "variant": variant_name,
                        "unit": unit["name"],
                        "message": f"A unidade `{unit['name']}` usa a regiao descartada `{region_id}` como se fosse cena util.",
                    }
                )
            classification = region_classifications.get(region_id)
            allowed_roles = allowed_roles_by_classification.get(classification)
            if allowed_roles and unit["role"] not in allowed_roles:
                issues.append(
                    {
                        "code": "SEMANTIC_ROLE_MISMATCH",
                        "variant": variant_name,
                        "unit": unit["name"],
                        "message": f"A regiao `{region_id}` foi classificada como `{classification}`, mas a unidade usa o papel `{unit['role']}`.",
                    }
                )

    return {
        "scene_truth_kind": manifest.get("scene_truth_kind", "inferred"),
        "layout_complexity": manifest.get("layout_complexity"),
        "source_layout_type": source_layout_type,
        "source_inventory": source_inventory,
        "drop_policy": drop_policy,
        "composition_schema": composition_schema,
        "issues": issues,
        "status": "ok" if not issues else "needs_review",
    }


def iter_exact_tiles(image: Image.Image) -> list[tuple[tuple[int, int, int, int], ...]]:
    width, height = image.size
    tiles: list[tuple[tuple[int, int, int, int], ...]] = []
    for top in range(0, height, 8):
        for left in range(0, width, 8):
            block: list[tuple[int, int, int, int]] = []
            for y in range(top, min(top + 8, height)):
                for x in range(left, min(left + 8, width)):
                    block.append(image.getpixel((x, y)))
            tiles.append(tuple(block))
    return tiles


def tile_budget_stats(asset_path: Path) -> dict[str, Any]:
    image = Image.open(asset_path).convert("RGBA")
    tiles = iter_exact_tiles(image)
    empty_tile = tuple([(0, 0, 0, 0)] * 64)
    non_empty_tiles = [tile for tile in tiles if tile != empty_tile]
    unique_non_empty_tiles = len(set(non_empty_tiles))
    total_tiles = len(tiles)
    empty_tiles = total_tiles - len(non_empty_tiles)
    duplicate_tiles = len(non_empty_tiles) - unique_non_empty_tiles
    unique_ratio = (unique_non_empty_tiles / max(1, len(non_empty_tiles))) if non_empty_tiles else 0.0
    return {
        "total_tiles": total_tiles,
        "empty_tiles": empty_tiles,
        "non_empty_tiles": len(non_empty_tiles),
        "unique_non_empty_tiles": unique_non_empty_tiles,
        "duplicate_non_empty_tiles": duplicate_tiles,
        "unique_ratio": round(unique_ratio, 4),
    }


def role_group(role: str) -> str:
    if role in {"bg_a", "bg_b", "midground_layer"}:
        return "background"
    if role in {"sprite", "hud", "foreground_layer"}:
        return "foreground"
    return "other"


def build_hardware_budget_review(
    translation_target: str | None,
    variants: dict[str, Any],
) -> dict[str, Any]:
    safe_bg_tile_ceiling = 1536
    whole_image_ratio = 0.85
    heavy_bg_threshold = 1000
    recommendations: list[dict[str, Any]] = []
    variant_summaries: dict[str, Any] = {}

    for variant_name, variant in variants.items():
        background_unique = 0
        foreground_unique = 0
        total_unique = 0
        background_units = 0
        whole_image_risk_units: list[str] = []

        for unit in variant["units"]:
            stats = unit.get("tile_budget", {})
            unique_tiles = int(stats.get("unique_non_empty_tiles", 0))
            total_unique += unique_tiles
            if role_group(unit["role"]) == "background":
                background_unique += unique_tiles
                background_units += 1
                if stats.get("non_empty_tiles", 0) >= 256 and float(stats.get("unique_ratio", 0.0)) >= whole_image_ratio:
                    whole_image_risk_units.append(unit["name"])
            elif role_group(unit["role"]) == "foreground":
                foreground_unique += unique_tiles

        variant_summary = {
            "background_unique_tiles": background_unique,
            "foreground_unique_tiles": foreground_unique,
            "total_unique_tiles": total_unique,
            "safe_bg_tile_ceiling": safe_bg_tile_ceiling,
            "background_units": background_units,
            "whole_image_risk_units": whole_image_risk_units,
        }
        variant_summaries[variant_name] = variant_summary

        if whole_image_risk_units:
            recommendations.append(
                {
                    "variant": variant_name,
                    "code": "WHOLE_IMAGE_CONVERSION_RISK",
                    "severity": "warning",
                    "message": "A variante tem backgrounds com proporcao muito alta de tiles unicos; isso parece compressao de imagem inteira, nao traducao modular.",
                    "evidence": {
                        "units": whole_image_risk_units,
                        "background_unique_tiles": background_unique,
                    },
                    "recommendation": "Rever modularizacao, redistribuir detalhe por plano e evitar promover conversao direta de ilustracao inteira para ROM.",
                }
            )

        if background_unique > safe_bg_tile_ceiling and background_units >= 2 and translation_target in {"scene_slice", "tilemap"}:
            recommendations.append(
                {
                    "variant": variant_name,
                    "code": "COMPARE_FLAT_CANDIDATE",
                    "severity": "warning",
                    "message": "A soma de tiles unicos dos planos de background excede o teto pratico antes da regiao de mapas do VDP.",
                    "evidence": {
                        "background_unique_tiles": background_unique,
                        "safe_bg_tile_ceiling": safe_bg_tile_ceiling,
                    },
                    "recommendation": "Para prova em ROM, considerar `compare_flat` single-plane e manter a curadoria multi-plano offline.",
                }
            )

        if background_unique > heavy_bg_threshold and foreground_unique > 0:
            recommendations.append(
                {
                    "variant": variant_name,
                    "code": "MANUAL_VRAM_PARTITION_CANDIDATE",
                    "severity": "info",
                    "message": "O background desta variante e pesado e divide VRAM com elementos de frente; a reserva padrao do sprite engine pode nao ser a melhor particao.",
                    "evidence": {
                        "background_unique_tiles": background_unique,
                        "foreground_unique_tiles": foreground_unique,
                    },
                    "recommendation": "Medir cena em ROM e, se necessario, testar `SPR_initEx(u16 vramSize)` para devolver mais tiles ao background.",
                }
            )

    return {
        "safe_bg_tile_ceiling": safe_bg_tile_ceiling,
        "variants": variant_summaries,
        "recommendations": recommendations,
    }


def build_evidence(project_root: Path | None) -> dict[str, Any]:
    captures_dir = project_root / "out" / "captures" if project_root else None
    evidence = {
        "captured": False,
        "captures_dir": str(captures_dir) if captures_dir else None,
        "screenshot_path": None,
        "quicksave_path": None,
        "visual_vdp_dump_path": None,
        "save_sram_path": None,
        "quicksave_captured": False,
    }

    if captures_dir is None or not captures_dir.is_dir():
        return evidence

    screenshot = captures_dir / "benchmark_visual.png"
    dump_path = captures_dir / "visual_vdp_dump.bin"
    sram_path = captures_dir / "save.sram"

    quicksave_candidates = [
        item for item in captures_dir.glob("*")
        if item.is_file()
        and item.name not in {"benchmark_visual.png", "visual_vdp_dump.bin", "save.sram"}
    ]
    quicksave = max(quicksave_candidates, key=lambda item: item.stat().st_mtime) if quicksave_candidates else None

    evidence["screenshot_path"] = str(screenshot) if screenshot.is_file() else None
    evidence["quicksave_path"] = str(quicksave) if quicksave else None
    evidence["visual_vdp_dump_path"] = str(dump_path) if dump_path.is_file() else None
    evidence["save_sram_path"] = str(sram_path) if sram_path.is_file() else None
    evidence["quicksave_captured"] = bool(evidence["quicksave_path"])
    evidence["captured"] = all(
        [
            evidence["screenshot_path"],
            evidence["visual_vdp_dump_path"],
            evidence["save_sram_path"],
        ]
    )
    return evidence


def detect_failure_codes(variant_status: str, delta: float, minimum_delta: float) -> list[str]:
    failures: list[str] = []
    if variant_status == "rework":
        failures.append("DIRECT_QUANTIZATION_LOOK")
    if delta <= 0:
        failures.append("NO_ELITE_DELTA")
    elif delta < minimum_delta:
        failures.append("NO_ELITE_DELTA")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Avalia um caso de traducao basic vs elite para a skill art-translation-to-vdp.")
    parser.add_argument("--manifest", required=True, help="Manifesto JSON do caso.")
    parser.add_argument("--output", required=True, help="JSON de saida.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        print(f"Erro: manifesto nao encontrado: {manifest_path}", file=sys.stderr)
        return 1

    if not AESTHETIC_ANALYZER.is_file():
        print(f"Erro: analyzer ausente: {AESTHETIC_ANALYZER}", file=sys.stderr)
        return 1

    manifest = load_json(manifest_path)
    project_root = find_project_root(manifest_path)
    output_path = Path(args.output).resolve()
    output_dir = output_path.parent
    work_dir = output_dir / "translation_case_work"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    reference_profile = manifest.get("reference_profile", "generic-megadrive-elite")
    minimum_delta = float(manifest.get("minimum_delta", 0.08))
    report_variants: dict[str, Any] = {}

    for variant_name, variant in manifest["variants"].items():
        variant_dir = work_dir / variant_name
        variant_dir.mkdir(parents=True, exist_ok=True)
        units_report: list[dict[str, Any]] = []

        for index, unit in enumerate(variant.get("analysis_units", [])):
            unit_name = unit.get("name", f"unit_{index}")
            role = unit["role"]
            asset_path = resolve_path(manifest_path, project_root, unit["asset"])
            if asset_path is None or not asset_path.is_file():
                raise FileNotFoundError(f"Asset da unidade nao encontrado: {unit['asset']}")

            normalized_asset = indexed_zero_to_transparent(asset_path, variant_dir / f"{unit_name}_asset_rgba.png")

            paired_bg: Path | None = None
            paired_bg_path = resolve_path(manifest_path, project_root, unit.get("paired_bg"))
            paired_bg_layers = unit.get("paired_bg_layers", [])
            if paired_bg_path is not None:
                paired_bg = indexed_zero_to_transparent(paired_bg_path, variant_dir / f"{unit_name}_paired_bg_rgba.png")
            elif paired_bg_layers:
                layer_paths: list[Path] = []
                for layer_index, layer in enumerate(paired_bg_layers):
                    layer_path = resolve_path(manifest_path, project_root, layer)
                    if layer_path is None or not layer_path.is_file():
                        raise FileNotFoundError(f"Camada de paired_bg nao encontrada: {layer}")
                    normalized_layer = indexed_zero_to_transparent(
                        layer_path,
                        variant_dir / f"{unit_name}_layer_{layer_index}.png",
                    )
                    layer_paths.append(normalized_layer)
                paired_bg = compose_layers(layer_paths, variant_dir / f"{unit_name}_paired_bg_composed.png")

            analysis_output = variant_dir / f"{unit_name}_analysis.json"
            analysis = run_aesthetic_analysis(
                asset_path=normalized_asset,
                role=role,
                reference_profile=unit.get("reference_profile", reference_profile),
                output_path=analysis_output,
                paired_bg=paired_bg,
                critical_visual=bool(unit.get("critical_visual", False)),
            )
            analysis = apply_case_penalties(
                analysis,
                normalized_asset,
                manifest.get("translation_target"),
                role
            )

            units_report.append(
                {
                    "name": unit_name,
                    "semantic_region_id": unit.get("semantic_region_id"),
                    "role": role,
                    "asset_path": str(asset_path),
                    "normalized_asset_path": str(normalized_asset),
                    "paired_bg_path": str(paired_bg) if paired_bg else None,
                    "weight": float(unit.get("weight", 1.0)),
                    "tile_budget": tile_budget_stats(normalized_asset),
                    "analysis": analysis,
                }
            )

        variant_status = aggregate_status([unit["analysis"] for unit in units_report])
        report_variants[variant_name] = {
            "label": variant.get("label", variant_name.upper()),
            "status": variant_status,
            "units": units_report,
            "aggregate_score": weighted_score(units_report),
        }

    basic_score = report_variants["basic"]["aggregate_score"]
    elite_score = report_variants["elite"]["aggregate_score"]
    delta = round(elite_score - basic_score, 4)

    if delta >= minimum_delta and elite_score > basic_score:
        comparison_status = "elite_delta_confirmed"
    elif elite_score > basic_score:
        comparison_status = "elite_beats_basic_below_delta"
    else:
        comparison_status = "no_elite_advantage"

    report = {
        "case_id": manifest["case_id"],
        "source_image": str(resolve_path(manifest_path, project_root, manifest.get("source_image"))) if manifest.get("source_image") else None,
        "translation_target": manifest.get("translation_target"),
        "reference_profile": reference_profile,
        "minimum_delta": minimum_delta,
        "scene_truth_kind": manifest.get("scene_truth_kind", "inferred"),
        "layout_complexity": manifest.get("layout_complexity"),
        "source_inventory": manifest.get("source_inventory", {}),
        "drop_policy": manifest.get("drop_policy", {}),
        "composition_schema": manifest.get("composition_schema", {}),
        "semantic_parse_report": manifest.get("semantic_parse_report", {}),
        "training_labels": manifest.get("training_labels", {}),
        "hardware_expectations": manifest.get("hardware_expectations", {}),
        "intent_notes": manifest.get("intent_notes", []),
        "soul_contract": manifest.get("soul_contract", {}),
        "variants": report_variants,
        "comparison": {
            "basic_score": basic_score,
            "elite_score": elite_score,
            "elite_minus_basic": delta,
            "status": comparison_status,
            "failure_codes": detect_failure_codes(report_variants["elite"]["status"], delta, minimum_delta),
        },
        "hardware_budget_review": build_hardware_budget_review(manifest.get("translation_target"), report_variants),
        "semantic_stage_review": build_semantic_stage_review(manifest, report_variants),
        "evidence": build_evidence(project_root),
    }

    source_image_path = Path(report["source_image"]) if report["source_image"] else None
    panel_path = render_human_validation_panel(
        output_path=output_dir / "human_validation_panel.png",
        source_image=source_image_path,
        variants=report_variants,
        comparison=report["comparison"],
    )
    semantic_panel_path = render_semantic_decomposition_panel(
        output_path=output_dir / "semantic_decomposition_panel.png",
        source_image=source_image_path,
        semantic_map=manifest.get("source_semantic_map"),
        variants=report_variants,
    )
    report["human_validation"] = {
        "format": "original_basic_elite_side_by_side",
        "panel_path": str(panel_path),
        "semantic_format": "original_semantic_regions_elite_remounted" if semantic_panel_path else None,
        "semantic_panel_path": str(semantic_panel_path) if semantic_panel_path else None,
    }

    save_json(output_path, report)
    print(
        json.dumps(
            {
                "case_id": report["case_id"],
                "status": report["comparison"]["status"],
                "basic_score": basic_score,
                "elite_score": elite_score,
                "elite_minus_basic": delta,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
