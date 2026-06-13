#!/usr/bin/env python3
"""
export_source_structure.py - materializa recortes e metadata a partir da IR estrutural validada.

Uso:
  python export_source_structure.py --ir <derived_structure_ir.json> --output-dir <dir>
"""

from __future__ import annotations

import argparse
from collections import deque
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)

from infer_source_structure import bbox_area, bbox_center_y, bbox_height, bbox_width, load_json, save_json


def contain_on_canvas(image: Image.Image, size: tuple[int, int], background: tuple[int, int, int, int]) -> Image.Image:
    fitted = ImageOps.contain(image.convert("RGBA"), size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", size, background)
    left = max(0, (size[0] - fitted.width) // 2)
    top = max(0, (size[1] - fitted.height) // 2)
    canvas.alpha_composite(fitted, (left, top))
    return canvas


def color_for_region(region: dict[str, Any]) -> tuple[int, int, int, int]:
    action = region.get("action", "keep")
    classification = region.get("classification", "")
    if action == "drop":
        return (228, 74, 62, 255)
    if action == "auxiliary":
        return (255, 153, 51, 255)
    if classification in {"scene_plane_sky", "scene_plane_bg_b"}:
        return (96, 192, 255, 255)
    if classification in {"scene_plane_architecture", "scene_plane_bg_a"}:
        return (112, 232, 128, 255)
    if classification in {"scene_plane_ground", "scene_plane_foreground_composition"}:
        return (255, 214, 92, 255)
    if classification == "actor_sprite_sheet":
        return (194, 137, 255, 255)
    if classification in {"tile_cluster", "overlay_cluster"}:
        return (210, 210, 210, 255)
    if classification == "object_animation_sequence":
        return (255, 142, 92, 255)
    return (220, 220, 220, 255)


def connected_background_mask(image: Image.Image, background_color: list[int] | tuple[int, int, int], threshold: int = 26) -> np.ndarray:
    rgba = image.convert("RGBA")
    data = np.array(rgba)
    background = np.array(background_color[:3], dtype=np.int16)
    delta = np.abs(data[:, :, :3].astype(np.int16) - background)
    candidate = np.max(delta, axis=2) <= threshold
    height, width = candidate.shape
    visited = np.zeros_like(candidate, dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    for x in range(width):
        if candidate[0, x] and not visited[0, x]:
            visited[0, x] = True
            queue.append((x, 0))
        if candidate[height - 1, x] and not visited[height - 1, x]:
            visited[height - 1, x] = True
            queue.append((x, height - 1))
    for y in range(height):
        if candidate[y, 0] and not visited[y, 0]:
            visited[y, 0] = True
            queue.append((0, y))
        if candidate[y, width - 1] and not visited[y, width - 1]:
            visited[y, width - 1] = True
            queue.append((width - 1, y))

    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    while queue:
        current_x, current_y = queue.popleft()
        for delta_x, delta_y in neighbors:
            next_x = current_x + delta_x
            next_y = current_y + delta_y
            if next_x < 0 or next_y < 0 or next_x >= width or next_y >= height:
                continue
            if visited[next_y, next_x] or not candidate[next_y, next_x]:
                continue
            visited[next_y, next_x] = True
            queue.append((next_x, next_y))

    return visited


def enclosed_background_holes_mask(image: Image.Image, background_color: list[int] | tuple[int, int, int], threshold: int = 26) -> np.ndarray:
    rgba = image.convert("RGBA")
    data = np.array(rgba)
    if data.size == 0:
        return np.zeros((0, 0), dtype=bool)

    background = np.array(background_color, dtype=np.int16)
    delta = np.abs(data[:, :, :3].astype(np.int16) - background)
    candidate = np.max(delta, axis=2) <= threshold
    border_connected = connected_background_mask(rgba, background_color, threshold=threshold)
    return candidate & ~border_connected


def background_to_alpha(
    image: Image.Image,
    background_color: list[int] | tuple[int, int, int],
    threshold: int = 26,
    remove_internal_key_holes: bool = False,
) -> Image.Image:
    rgba = image.convert("RGBA")
    data = np.array(rgba)
    mask = connected_background_mask(rgba, background_color, threshold=threshold)
    data[mask, 3] = 0
    if remove_internal_key_holes:
        holes = enclosed_background_holes_mask(rgba, background_color, threshold=threshold)
        data[holes, 3] = 0
    return Image.fromarray(data, "RGBA")


def make_finding(
    finding_type: str,
    severity: str,
    target: str,
    message: str,
    suggestion: str | None = None,
) -> dict[str, Any]:
    finding = {
        "type": finding_type,
        "severity": severity,
        "target": target,
        "message": message,
    }
    if suggestion:
        finding["suggestion"] = suggestion
    return finding


def save_tight_alpha_preview(image: Image.Image, destination: Path) -> tuple[Path, list[int] | None]:
    alpha_bbox = image.getchannel("A").getbbox()
    preview = image.crop(alpha_bbox) if alpha_bbox else image.copy()
    destination.parent.mkdir(parents=True, exist_ok=True)
    preview.save(destination)
    return (destination, list(alpha_bbox) if alpha_bbox else None)


def analyze_scene_layer_delivery(
    extracted_regions: list[dict[str, Any]],
    shared_canvas: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    updated_regions: list[dict[str, Any]] = []
    expected_size = None
    if shared_canvas:
        expected_size = (shared_canvas["width"], shared_canvas["height"])

    scene_regions = [region for region in extracted_regions if region.get("system_role") == "scene_layer"]
    seen_sizes: set[tuple[int, int]] = set()
    for region in extracted_regions:
        if region.get("system_role") != "scene_layer":
            updated_regions.append(region)
            continue

        path = Path(region["path"])
        with Image.open(path) as image:
            rgba = image.convert("RGBA")
            seen_sizes.add(rgba.size)
            preview_path, alpha_bbox = save_tight_alpha_preview(
                rgba,
                path.parent.parent / "layer_previews" / f"{path.stem}_tight.png",
            )
            alpha = np.array(rgba.getchannel("A"))
            alpha_ratio = float((alpha > 0).mean()) if alpha.size else 0.0

        updated = dict(region)
        updated["tight_preview_path"] = str(preview_path)
        updated["alpha_bbox"] = alpha_bbox
        updated["alpha_ratio"] = round(alpha_ratio, 4)
        updated_regions.append(updated)

        if expected_size and rgba.size != expected_size:
            findings.append(
                make_finding(
                    "scene_layer_canvas_mismatch",
                    "error",
                    region["id"],
                    f"layer exportada com tamanho {rgba.size}, mas o canvas esperado era {expected_size}",
                    "Scene layers de review precisam compartilhar o mesmo canvas para recomposicao confiavel.",
                )
            )
        elif alpha_ratio < 0.35:
            findings.append(
                make_finding(
                    "scene_layer_sparse_alpha_expected",
                    "info",
                    region["id"],
                    "layer de cena ocupa apenas parte do canvas comum; o resto esta em alpha por politica de review estrutural",
                    "Use o tight preview para avaliar o conteudo util e nao interpretar o vazio do canvas como buraco de conversao.",
                )
            )

    if scene_regions and len(seen_sizes) > 1:
        findings.append(
            make_finding(
                "scene_layer_canvas_inconsistency",
                "error",
                "scene_layers",
                f"scene layers foram exportadas com tamanhos diferentes: {sorted(seen_sizes)}",
                "Padronizar shared_canvas antes de promover a cena.",
            )
        )

    return (updated_regions, findings)


def analyze_drop_region_delivery(drop_regions: list[dict[str, Any]], source_size: tuple[int, int]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    source_area = max(1, source_size[0] * source_size[1])
    for region in drop_regions:
        area = max(0, (region["bbox"][2] - region["bbox"][0]) * (region["bbox"][3] - region["bbox"][1]))
        ratio = area / source_area
        if ratio >= 0.025:
            findings.append(
                make_finding(
                    "notable_drop_region",
                    "info",
                    region["id"],
                    f"regiao descartada grande ({ratio:.1%} da prancha) preservada em drops/ para inspecao",
                    "Confirmar se o descarte e realmente editorial/nao jogavel antes da traducao final.",
                )
            )
    return findings


def analyze_sequence_delivery(
    source: Image.Image,
    sequences: list[dict[str, Any]],
    background_color: list[int],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for sequence in sequences:
        band_bbox = sequence.get("band_bbox")
        strongest_hole: tuple[int, str] | None = None
        for index, frame_bbox in enumerate(sequence.get("frame_bboxes", [])):
            target = f"{sequence['id']}/frame_{index:03d}"
            if band_bbox and (frame_bbox[1] < band_bbox[1] - 2 or frame_bbox[3] > band_bbox[3] + 2):
                findings.append(
                    make_finding(
                        "frame_band_overflow_risk",
                        "warning",
                        target,
                        "frame bbox extrapola a faixa semantica da sequencia e pode estar puxando pixels da linha vizinha",
                        "Revisar agrupamento da banda antes de promover a spritesheet.",
                    )
                )

            raw_crop = source.crop(tuple(frame_bbox))
            holes = enclosed_background_holes_mask(raw_crop, background_color, threshold=26)
            hole_pixels = int(np.count_nonzero(holes))
            if hole_pixels >= max(120, int(raw_crop.size[0] * raw_crop.size[1] * 0.015)):
                if strongest_hole is None or hole_pixels > strongest_hole[0]:
                    strongest_hole = (hole_pixels, target)
        if strongest_hole is not None:
            findings.append(
                make_finding(
                    "frame_internal_key_hole_candidate",
                    "info",
                    strongest_hole[1],
                    f"sequencia contem frame com {strongest_hole[0]} pixels de cor-chave enclausurada; pode haver oportunidade de alpha interno util",
                    "Comparar o source com o frame exportado e decidir se o vao interno pertence a silhueta final.",
                )
            )
    return findings


def render_overlay_panel(
    source_path: Path,
    output_path: Path,
    regions: list[dict[str, Any]],
    title: str,
    footer_lines: list[str],
) -> Path:
    with Image.open(source_path) as image:
        source = image.convert("RGBA")

    preview = contain_on_canvas(source, (960, 540), (18, 22, 28, 255))
    sx = preview.width / source.width
    sy = preview.height / source.height

    panel_h = preview.height + 120
    panel = Image.new("RGBA", (preview.width + 24, panel_h), (14, 22, 28, 255))
    panel.alpha_composite(preview, (12, 12))
    draw = ImageDraw.Draw(panel)

    for region in regions:
        left, top, right, bottom = region["bbox"]
        box = (12 + int(left * sx), 12 + int(top * sy), 12 + int(right * sx), 12 + int(bottom * sy))
        color = color_for_region(region)
        draw.rectangle(box, outline=color, width=3)
        label = f"{region['id']} | {region.get('classification', 'unknown')}"
        draw.rectangle((box[0], max(12, box[1] - 18), min(box[0] + 320, panel.width - 12), box[1]), fill=(12, 18, 22, 220))
        draw.text((box[0] + 4, max(12, box[1] - 16)), label, fill=color)

    draw.text((12, preview.height + 24), title, fill=(230, 236, 238, 255))
    for index, line in enumerate(footer_lines):
        draw.text((12, preview.height + 48 + (index * 18)), line, fill=(214, 224, 228, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def export_scene_region(
    source: Image.Image,
    region: dict[str, Any],
    background_color: list[int],
    shared_canvas: dict[str, Any],
    destination: Path,
) -> Path:
    crop = source.crop(tuple(region["bbox"]))
    transparent = background_to_alpha(crop, background_color, threshold=26, remove_internal_key_holes=False)
    canvas = Image.new("RGBA", (shared_canvas["width"], shared_canvas["height"]), (0, 0, 0, 0))
    canvas.alpha_composite(transparent, (region["bbox"][0], region["bbox"][1]))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)
    return destination


def export_crop(source: Image.Image, region: dict[str, Any], background_color: list[int], destination: Path) -> Path:
    crop = source.crop(tuple(region["bbox"]))
    remove_internal_key_holes = region.get("classification") in {"actor_sprite_sheet", "object_animation_sequence", "tile_cluster", "overlay_cluster"}
    transparent = background_to_alpha(crop, background_color, threshold=26, remove_internal_key_holes=remove_internal_key_holes)
    destination.parent.mkdir(parents=True, exist_ok=True)
    transparent.save(destination)
    return destination


def build_scene_recomposition(source: Image.Image, regions: list[dict[str, Any]], shared_canvas: dict[str, Any], background_color: list[int]) -> Image.Image:
    layer_order = {"scene_plane_bg_b": 0, "scene_plane_sky": 0, "scene_plane_bg_a": 1, "scene_plane_architecture": 1, "scene_plane_ground": 2, "scene_plane_foreground_composition": 3}
    canvas = Image.new("RGBA", (shared_canvas["width"], shared_canvas["height"]), (0, 0, 0, 0))
    for region in sorted(regions, key=lambda item: (layer_order.get(item.get("classification"), 99), item["bbox"][1])):
        crop = source.crop(tuple(region["bbox"]))
        transparent = background_to_alpha(crop, background_color, threshold=26, remove_internal_key_holes=False)
        canvas.alpha_composite(transparent, (region["bbox"][0], region["bbox"][1]))
    return canvas


def verify_recomposition(source: Image.Image, recomposed: Image.Image, scene_regions: list[dict[str, Any]]) -> tuple[float, list[str], bool]:
    source_arr = np.array(source.convert("RGBA"))
    recomposed_arr = np.array(recomposed.convert("RGBA"))
    mask = recomposed_arr[:, :, 3] > 0
    failures: list[str] = []
    if not mask.any():
        return (0.0, ["recomposition_without_visible_pixels"], False)

    source_visible = source_arr[:, :, :3][mask]
    recomposed_visible = recomposed_arr[:, :, :3][mask]
    mean_delta = float(np.mean(np.abs(source_visible.astype(np.int16) - recomposed_visible.astype(np.int16))) / 255.0)
    score = round(max(0.0, 1.0 - mean_delta), 4)
    if score < 0.935:
        failures.append("low_reconstruction_fidelity")

    alpha_mask = recomposed_arr[:, :, 3]
    row_activity = alpha_mask.mean(axis=1) / 255.0
    if np.max(row_activity) < 0.08:
        failures.append("weak_scene_coverage")

    coverage_ratio = float(mask.mean())
    if coverage_ratio < 0.12:
        failures.append("coverage_too_small")

    classifications = {region.get("classification") for region in scene_regions}
    if not ({"scene_plane_sky", "scene_plane_bg_b"} & classifications):
        failures.append("missing_background_layer")
    if not ({"scene_plane_architecture", "scene_plane_bg_a"} & classifications):
        failures.append("missing_main_scene_layer")

    role_to_region = {region.get("compositional_role") or region.get("classification"): region for region in scene_regions}
    bg_region = role_to_region.get("scene_plane_bg_b")
    main_region = role_to_region.get("scene_plane_bg_a")
    foreground_region = role_to_region.get("scene_plane_foreground_composition")
    ground_region = next((region for region in scene_regions if region.get("classification") == "scene_plane_ground"), None)

    if bg_region and bbox_width(bg_region["bbox"]) < source.width * 0.3:
        failures.append("bg_b_insufficient_horizontal_continuity")
    if main_region and bbox_width(main_region["bbox"]) < source.width * 0.35:
        failures.append("bg_a_insufficient_horizontal_continuity")
    if ground_region and bbox_width(ground_region["bbox"]) < source.width * 0.35:
        failures.append("ground_insufficient_horizontal_continuity")

    if foreground_region and main_region and bbox_center_y(foreground_region["bbox"]) <= bbox_center_y(main_region["bbox"]):
        failures.append("foreground_depth_order_invalid")

    row_peaks = np.where(row_activity > 0.04)[0]
    if row_peaks.size > 0 and (row_peaks[-1] - row_peaks[0]) < source.height * 0.2:
        failures.append("vertical_scene_span_too_small")

    return (score, failures, not failures)


def decide_export_mode(derived_ir: dict[str, Any], recomposition_pass: bool | None) -> tuple[str, list[str], bool]:
    blocked_reasons = list(derived_ir.get("blocked_reasons", []))
    layout_type = derived_ir.get("layout_type")
    keep_regions = [region for region in derived_ir.get("regions", []) if region.get("action") == "keep"]
    auxiliary_regions = [region for region in derived_ir.get("regions", []) if region.get("action") == "auxiliary"]
    needs_review = derived_ir.get("review_required", False)

    blocking_conflicts = [conflict for conflict in derived_ir.get("conflicts", []) if conflict.get("blocks_final_export")]
    if blocking_conflicts:
        blocked_reasons.extend([f"conflict:{conflict.get('type', 'unknown')}" for conflict in blocking_conflicts])

    if layout_type in {"stage_board", "editorial_board"} and recomposition_pass is False:
        blocked_reasons.append("recomposition_visual_fail")

    for region in keep_regions:
        if region.get("confidence_bbox", 0.0) < 0.75:
            blocked_reasons.append(f"{region['id']}:low_bbox_confidence")
        if region.get("confidence_classification", 0.0) < 0.75:
            blocked_reasons.append(f"{region['id']}:low_classification_confidence")
        if region.get("confidence_engine_affordance", 0.0) < 0.75:
            blocked_reasons.append(f"{region['id']}:low_engine_confidence")
        if region.get("compositional_role") and region.get("confidence_composition", 0.0) < 0.75:
            blocked_reasons.append(f"{region['id']}:low_composition_confidence")

    for sequence in derived_ir.get("sequences", []):
        if sequence.get("confidence_sequence_grouping", 0.0) < 0.75:
            blocked_reasons.append(f"{sequence['id']}:low_sequence_grouping_confidence")
        if sequence.get("confidence_pivot", 0.0) < 0.75:
            blocked_reasons.append(f"{sequence['id']}:low_pivot_confidence")

    actionable_review = any(region.get("review_required") for region in keep_regions + auxiliary_regions) or any(
        sequence.get("review_required") for sequence in derived_ir.get("sequences", [])
    )
    needs_review = needs_review or actionable_review

    export_mode = "final" if not blocked_reasons and not needs_review else "provisional"
    return (export_mode, sorted(set(blocked_reasons)), export_mode != "final")


def render_inferred_composition_panel(
    source: Image.Image,
    output_path: Path,
    keep_regions: list[dict[str, Any]],
    recomposed_scene: Image.Image | None,
) -> Path:
    preview_size = (240, 160)
    cards: list[tuple[str, Image.Image]] = [("SOURCE", contain_on_canvas(source, preview_size, (24, 34, 40, 255)))]
    for region in keep_regions:
        crop = source.crop(tuple(region["bbox"]))
        cards.append((region.get("compositional_role") or region.get("classification") or region["id"], contain_on_canvas(crop, preview_size, (24, 34, 40, 255))))
    if recomposed_scene is not None:
        cards.append(("RECOMPOSED", contain_on_canvas(recomposed_scene, preview_size, (24, 34, 40, 255))))

    gap = 12
    header_h = 42
    footer_h = 42
    panel_w = (len(cards) * 240) + ((len(cards) + 1) * gap)
    panel_h = 160 + header_h + footer_h + (gap * 2)
    panel = Image.new("RGBA", (panel_w, panel_h), (14, 22, 28, 255))
    draw = ImageDraw.Draw(panel)
    for index, (label, image) in enumerate(cards):
        x = gap + index * (240 + gap)
        y = gap
        draw.rounded_rectangle((x, y, x + 240, panel_h - gap), radius=10, fill=(20, 30, 36, 255))
        draw.rectangle((x, y, x + 240, y + header_h), fill=(28, 42, 48, 255))
        draw.text((x + 10, y + 12), label, fill=(230, 236, 238, 255))
        panel.alpha_composite(image, (x, y + header_h))
    draw.text((gap + 8, gap + header_h + 160 + 10), "SOURCE -> inferencia estrutural -> recomposicao", fill=(214, 224, 228, 255))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def render_animation_ranges_panel(source: Image.Image, output_path: Path, sequences: list[dict[str, Any]]) -> Path | None:
    if not sequences:
        return None
    preview = contain_on_canvas(source, (960, 540), (18, 22, 28, 255))
    sx = preview.width / source.width
    sy = preview.height / source.height
    panel_h = preview.height + 120
    panel = Image.new("RGBA", (preview.width + 24, panel_h), (14, 22, 28, 255))
    panel.alpha_composite(preview, (12, 12))
    draw = ImageDraw.Draw(panel)
    colors = [(96, 192, 255, 255), (112, 232, 128, 255), (255, 214, 92, 255), (194, 137, 255, 255)]
    for index, sequence in enumerate(sequences):
        color = colors[index % len(colors)]
        band = sequence["band_bbox"]
        box = (12 + int(band[0] * sx), 12 + int(band[1] * sy), 12 + int(band[2] * sx), 12 + int(band[3] * sy))
        draw.rectangle(box, outline=color, width=3)
        draw.rectangle((box[0], max(12, box[1] - 18), min(box[0] + 320, panel.width - 12), box[1]), fill=(12, 18, 22, 220))
        draw.text((box[0] + 4, max(12, box[1] - 16)), sequence["id"], fill=color)
    draw.text((12, preview.height + 24), "SOURCE -> animation ranges", fill=(230, 236, 238, 255))
    draw.text((12, preview.height + 48), "Sequencias inferidas antes de recorte por frame e normalizacao.", fill=(214, 224, 228, 255))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def export_structure(ir_path: Path, output_dir: Path) -> dict[str, Any]:
    derived_ir = load_json(ir_path)
    source_path = Path(derived_ir["source_image"]).resolve()
    with Image.open(source_path) as image:
        source = image.convert("RGBA")

    keep_regions = [region for region in derived_ir.get("regions", []) if region.get("action") == "keep"]
    auxiliary_regions = [region for region in derived_ir.get("regions", []) if region.get("action") == "auxiliary"]
    drop_regions = [region for region in derived_ir.get("regions", []) if region.get("action") == "drop"]
    scene_regions = [region for region in keep_regions if region.get("system_role") == "scene_layer"]
    shared_canvas = derived_ir.get("shared_canvas")
    background_color = derived_ir.get("background_key_color", [0, 0, 0])

    recomposed_scene = None
    recomposition_visual_score = None
    visual_failures: list[str] = []
    recomposition_pass = None
    if scene_regions and shared_canvas:
        recomposed_scene = build_scene_recomposition(source, scene_regions, shared_canvas, background_color)
        recomposition_visual_score, visual_failures, recomposition_pass = verify_recomposition(source, recomposed_scene, scene_regions)

    export_mode, blocked_reasons, needs_review = decide_export_mode(derived_ir, recomposition_pass)
    derived_ir["export_mode"] = export_mode
    derived_ir["review_required"] = needs_review
    derived_ir["blocked_reasons"] = blocked_reasons
    derived_ir["recomposition_visual_score"] = recomposition_visual_score
    derived_ir["visual_failures"] = visual_failures
    derived_ir["recomposition_pass"] = recomposition_pass

    extracts_root = output_dir / "extracts" / export_mode
    extracted_regions: list[dict[str, Any]] = []

    for region in keep_regions + auxiliary_regions:
        if region.get("system_role") == "scene_layer" and shared_canvas:
            destination = extracts_root / "layers" / f"{region['id']}.png"
            export_scene_region(source, region, background_color, shared_canvas, destination)
        elif region.get("classification") == "actor_sprite_sheet":
            destination = extracts_root / "sprite_sources" / f"{region['id']}.png"
            export_crop(source, region, background_color, destination)
        elif region.get("classification") == "palette_strip":
            destination = extracts_root / "auxiliary" / f"{region['id']}.png"
            export_crop(source, region, background_color, destination)
        elif region.get("classification") in {"tile_cluster", "overlay_cluster"}:
            bucket = "tiles/base" if region.get("classification") == "tile_cluster" else "tiles/overlays"
            destination = extracts_root / bucket / f"{region['id']}.png"
            export_crop(source, region, background_color, destination)
        elif region.get("classification") == "object_animation_sequence":
            destination = extracts_root / "objects" / f"{region['id']}.png"
            export_crop(source, region, background_color, destination)
        else:
            destination = extracts_root / "misc" / f"{region['id']}.png"
            export_crop(source, region, background_color, destination)
        extracted_regions.append(
            {
                "id": region["id"],
                "path": str(destination),
                "action": region["action"],
                "classification": region["classification"],
                "system_role": region.get("system_role"),
                "candidate_asset_kind": region.get("candidate_asset_kind"),
                "compositional_role": region.get("compositional_role"),
                "engine_affordance": region.get("engine_affordance"),
                "confidence_bbox": region.get("confidence_bbox"),
                "confidence_classification": region.get("confidence_classification"),
                "confidence_composition": region.get("confidence_composition"),
                "confidence_engine_affordance": region.get("confidence_engine_affordance"),
                "review_required": region.get("review_required"),
            }
        )

    extracted_drop_regions: list[dict[str, Any]] = []
    for region in drop_regions:
        destination = extracts_root / "drops" / f"{region['id']}.png"
        export_crop(source, region, background_color, destination)
        extracted_drop_regions.append(
            {
                "id": region["id"],
                "path": str(destination),
                "action": region["action"],
                "classification": region["classification"],
                "system_role": region.get("system_role"),
                "candidate_asset_kind": region.get("candidate_asset_kind"),
                "compositional_role": region.get("compositional_role"),
                "engine_affordance": region.get("engine_affordance"),
                "confidence_bbox": region.get("confidence_bbox"),
                "confidence_classification": region.get("confidence_classification"),
                "confidence_composition": region.get("confidence_composition"),
                "confidence_engine_affordance": region.get("confidence_engine_affordance"),
                "review_required": region.get("review_required"),
            }
        )

    extracted_regions, scene_layer_findings = analyze_scene_layer_delivery(extracted_regions, shared_canvas)
    drop_region_findings = analyze_drop_region_delivery(drop_regions, source.size)

    extracted_sequences: list[dict[str, Any]] = []
    for sequence in derived_ir.get("sequences", []):
        sequence_dir = extracts_root / "sequences" / sequence["id"]
        envelope_width = max(1, sequence["frame_envelope"][2])
        envelope_height = max(1, sequence["frame_envelope"][3])
        frame_paths: list[str] = []
        for index, frame_bbox in enumerate(sequence["frame_bboxes"]):
            crop = background_to_alpha(source.crop(tuple(frame_bbox)), background_color, threshold=26, remove_internal_key_holes=True)
            canvas = Image.new("RGBA", (envelope_width, envelope_height), (0, 0, 0, 0))
            left = max(0, (envelope_width - crop.width) // 2)
            top = max(0, envelope_height - crop.height)
            canvas.alpha_composite(crop, (left, top))
            destination = sequence_dir / f"frame_{index:03d}.png"
            destination.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(destination)
            frame_paths.append(str(destination))
        extracted_sequences.append({"id": sequence["id"], "paths": frame_paths, "pivot_policy": sequence["pivot_policy"], "confidence_sequence_grouping": sequence["confidence_sequence_grouping"], "confidence_pivot": sequence["confidence_pivot"], "review_required": sequence["review_required"]})

    sequence_findings = analyze_sequence_delivery(source, derived_ir.get("sequences", []), background_color)
    delivery_findings = scene_layer_findings + drop_region_findings + sequence_findings
    derived_ir["delivery_findings"] = delivery_findings

    recomposed_scene_path = None
    if recomposed_scene is not None:
        recomposed_scene_path = output_dir / "recomposed_scene.png"
        recomposed_scene.save(recomposed_scene_path)

    human_panel = render_overlay_panel(source_path, output_dir / "human_semantic_panel.png", keep_regions + auxiliary_regions + drop_regions, "SOURCE -> semantic parse", [f"layout={derived_ir['layout_type']} export={export_mode}", f"keep={len(keep_regions)} aux={len(auxiliary_regions)} drop={len(drop_regions)}"])
    drop_panel = render_overlay_panel(source_path, output_dir / "drop_regions_panel.png", drop_regions, "SOURCE -> drop / ignore regions", ["Regioes vermelhas nao entram na cadeia final do asset."])
    composition_panel = render_inferred_composition_panel(source, output_dir / "inferred_composition_panel.png", keep_regions, recomposed_scene)
    animation_panel = render_animation_ranges_panel(source, output_dir / "animation_ranges_panel.png", derived_ir.get("sequences", []))

    structural_metadata = {
        "source_image": str(source_path),
        "layout_type": derived_ir["layout_type"],
        "export_mode": export_mode,
        "needs_review": needs_review,
        "shared_canvas": shared_canvas,
        "transparency_policy": {"kind": "border_connected_background_key", "background_key_color": background_color},
        "regions": extracted_regions,
        "region_contracts": extracted_regions,
        "drop_regions": extracted_drop_regions,
        "sequences": extracted_sequences,
        "sequence_defs": extracted_sequences,
        "blocked_reasons": blocked_reasons,
        "delivery_findings": delivery_findings,
        "scene_layer_canvas_policy": {
            "kind": "shared_canvas_rgba_review_asset",
            "note": "Layers de cena sao exportadas em canvas comum com alpha fora da area util; isso e valido para review estrutural, nao ainda um tilemap final de VDP.",
        },
    }
    validation_report = {
        "export_mode": export_mode,
        "needs_review": needs_review,
        "conflicts": derived_ir.get("conflicts", []),
        "conflict_count": len(derived_ir.get("conflicts", [])),
        "blocking_conflict_count": len([conflict for conflict in derived_ir.get("conflicts", []) if conflict.get("blocks_final_export")]),
        "blocked_reasons": blocked_reasons,
        "recomposition_visual_score": recomposition_visual_score,
        "visual_failures": visual_failures,
        "recomposition_pass": recomposition_pass,
        "delivery_findings": delivery_findings,
        "region_confidence_summary": [
            {
                "id": region["id"],
                "classification": region["classification"],
                "confidence_bbox": region.get("confidence_bbox"),
                "confidence_classification": region.get("confidence_classification"),
                "confidence_composition": region.get("confidence_composition"),
                "confidence_engine_affordance": region.get("confidence_engine_affordance"),
                "review_required": region.get("review_required"),
            }
            for region in keep_regions + auxiliary_regions
        ],
        "sequence_confidence_summary": [
            {
                "id": sequence["id"],
                "confidence_sequence_grouping": sequence.get("confidence_sequence_grouping"),
                "confidence_pivot": sequence.get("confidence_pivot"),
                "review_required": sequence.get("review_required"),
            }
            for sequence in derived_ir.get("sequences", [])
        ],
    }

    save_json(output_dir / "structural_metadata.json", structural_metadata)
    save_json(output_dir / "validation_report.json", validation_report)
    save_json(output_dir / "derived_structure_ir.json", derived_ir)

    return {
        "structural_metadata": str(output_dir / "structural_metadata.json"),
        "validation_report": str(output_dir / "validation_report.json"),
        "derived_structure_ir": str(output_dir / "derived_structure_ir.json"),
        "human_semantic_panel": str(human_panel),
        "drop_regions_panel": str(drop_panel),
        "inferred_composition_panel": str(composition_panel),
        "animation_ranges_panel": str(animation_panel) if animation_panel else None,
        "recomposed_scene": str(recomposed_scene_path) if recomposed_scene_path else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta recortes e metadata a partir da IR estrutural.")
    parser.add_argument("--ir", required=True, help="Arquivo derived_structure_ir.json")
    parser.add_argument("--output-dir", required=True, help="Diretorio de saida da exportacao.")
    args = parser.parse_args()

    ir_path = Path(args.ir).resolve()
    if not ir_path.is_file():
        print(f"Erro: IR nao encontrada: {ir_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = export_structure(ir_path, output_dir)
    validation = load_json(Path(outputs["validation_report"]))
    print(json.dumps({"export_mode": validation["export_mode"], "needs_review": validation["needs_review"], "recomposition_pass": validation["recomposition_pass"], "blocked_reasons": validation["blocked_reasons"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
