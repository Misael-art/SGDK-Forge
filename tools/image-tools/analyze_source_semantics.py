#!/usr/bin/env python3
"""
analyze_source_semantics.py - curadoria supervisionada da alfabetizacao semantica de source.

Uso:
  python analyze_source_semantics.py --manifest <json> --output <json>
"""

from __future__ import annotations

import argparse
import json
import shutil
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

ROLE_ORDER = {
    "stage_board": 0,
    "scene_plane_bg_b": 0,
    "scene_plane_bg_a": 1,
    "scene_plane_foreground_composition": 2,
    "scene_plane_sky": 3,
    "scene_plane_architecture": 4,
    "scene_plane_ground": 5,
    "actor_sprite_sheet": 3,
    "tile_cluster": 6,
    "object_cluster": 7,
    "object_animation_sequence": 8,
    "overlay_cluster": 9,
    "palette_strip": 10,
    "mockup_preview": 11,
}

RANGE_COLORS = [
    (96, 192, 255, 255),
    (112, 232, 128, 255),
    (255, 214, 92, 255),
    (255, 153, 51, 255),
    (194, 137, 255, 255),
    (228, 74, 62, 255),
]

EXPECTED_ENGINE_AFFORDANCE = {
    "scene_plane_sky": "scene_layer_continuous",
    "scene_plane_bg_b": "scene_layer_continuous",
    "scene_plane_architecture": "scene_layer_continuous",
    "scene_plane_bg_a": "scene_layer_continuous",
    "scene_plane_ground": "scene_layer_continuous",
    "scene_plane_foreground_composition": "scene_layer_continuous",
    "actor_sprite_sheet": "sprite_sequence",
    "palette_strip": "auxiliary_reference",
    "metadata_block": "editorial_noise",
    "author_credits": "editorial_noise",
    "avatar_or_icon": "editorial_noise",
    "mockup_preview": "editorial_noise",
    "unrelated_reference": "editorial_noise",
    "tile_cluster": "tile_base_reusable",
    "overlay_cluster": "tile_overlay_dependent",
    "object_animation_sequence": "object_state_sequence",
    "corrupted_region": "corrupted_discard",
}

SCENE_COMPOSITION_ROLES = {
    "scene_plane_bg_b",
    "scene_plane_bg_a",
    "scene_plane_foreground_composition",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def bbox_intersection(a: list[int], b: list[int]) -> int:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    if right <= left or bottom <= top:
        return 0
    return (right - left) * (bottom - top)


def bbox_area(bbox: list[int]) -> int:
    return max(0, bbox[2] - bbox[0]) * max(0, bbox[3] - bbox[1])


def bbox_iou(a: list[int], b: list[int]) -> float:
    intersection = bbox_intersection(a, b)
    if intersection == 0:
        return 0.0
    union = bbox_area(a) + bbox_area(b) - intersection
    return float(intersection / union) if union else 0.0


def resolve_path(manifest_path: Path, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None

    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate.resolve() if candidate.exists() else None

    for base in [manifest_path.parent, WORKSPACE_ROOT]:
        resolved = (base / raw_path).resolve()
        if resolved.exists():
            return resolved
    return None


def contain_on_canvas(image: Image.Image, size: tuple[int, int], background: tuple[int, int, int, int]) -> Image.Image:
    fitted = ImageOps.contain(image.convert("RGBA"), size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", size, background)
    left = max(0, (size[0] - fitted.width) // 2)
    top = max(0, (size[1] - fitted.height) // 2)
    canvas.alpha_composite(fitted, (left, top))
    return canvas


def clamp_bbox(bbox: list[int], width: int, height: int) -> list[int]:
    left, top, right, bottom = bbox
    left = max(0, min(left, width - 1))
    top = max(0, min(top, height - 1))
    right = max(left + 1, min(right, width))
    bottom = max(top + 1, min(bottom, height))
    return [left, top, right, bottom]


def color_for_region(region: dict[str, Any]) -> tuple[int, int, int, int]:
    action = region.get("action", "keep")
    classification = region.get("classification") or region.get("kind") or ""
    if action in {"drop", "ignore"}:
        return (228, 74, 62, 255)
    if action == "auxiliary":
        return (255, 153, 51, 255)
    if classification == "scene_plane_bg_b":
        return (81, 176, 255, 255)
    if classification == "scene_plane_bg_a":
        return (94, 214, 120, 255)
    if classification == "scene_plane_foreground_composition":
        return (255, 196, 67, 255)
    if classification == "scene_plane_sky":
        return (96, 192, 255, 255)
    if classification == "scene_plane_architecture":
        return (112, 232, 128, 255)
    if classification == "scene_plane_ground":
        return (255, 214, 92, 255)
    if classification == "actor_sprite_sheet":
        return (194, 137, 255, 255)
    if classification in {"tile_cluster", "overlay_cluster"}:
        return (210, 210, 210, 255)
    if classification in {"object_cluster", "object_animation_sequence"}:
        return (255, 142, 92, 255)
    if classification in {"palette_strip", "labels_and_names", "metadata_block", "author_credits", "avatar_or_icon", "mockup_preview", "unrelated_reference"}:
        return (255, 153, 51, 255)
    return (220, 220, 220, 255)


def normalize_regions(
    manifest: dict[str, Any],
    source_size: tuple[int, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    semantic = manifest.get("semantic_parse_report", {})
    composition_roles = {
        item["region_id"]: item
        for item in manifest.get("composition_schema", {}).get("roles", [])
        if item.get("region_id")
    }
    errors: list[str] = []
    seen_ids: set[str] = set()
    keep_regions: list[dict[str, Any]] = []
    auxiliary_regions: list[dict[str, Any]] = []
    drop_regions: list[dict[str, Any]] = []

    for bucket_name, action in (("semantic_regions", "keep"), ("auxiliary_regions", "auxiliary"), ("drop_regions", "drop")):
        for raw in semantic.get(bucket_name, []):
            region_id = raw.get("id")
            bbox = raw.get("bbox")
            if not region_id:
                errors.append(f"{bucket_name}: regiao sem id.")
                continue
            if region_id in seen_ids:
                errors.append(f"id duplicado no parsing semantico: {region_id}")
                continue
            if not isinstance(bbox, list) or len(bbox) != 4:
                errors.append(f"bbox invalido para {region_id}")
                continue

            seen_ids.add(region_id)
            normalized = dict(raw)
            normalized["bbox"] = clamp_bbox([int(v) for v in bbox], source_size[0], source_size[1])
            normalized["action"] = raw.get("action", action)

            if region_id in composition_roles:
                normalized["composition_role"] = composition_roles[region_id].get("composition_role")
                normalized["composition_order"] = int(composition_roles[region_id].get("order", 99))
            else:
                normalized["composition_role"] = raw.get("composition_role")
                normalized["composition_order"] = int(raw.get("composition_order", 99))

            if normalized["action"] in {"drop", "ignore"}:
                drop_regions.append(normalized)
            elif normalized["action"] == "auxiliary":
                auxiliary_regions.append(normalized)
            else:
                keep_regions.append(normalized)

    for region_id in composition_roles:
        if region_id not in seen_ids:
            errors.append(f"composition_schema referencia regiao ausente: {region_id}")

    keep_regions.sort(key=lambda item: (item.get("composition_order", 99), item["id"]))
    auxiliary_regions.sort(key=lambda item: (ROLE_ORDER.get(item.get("classification") or "", 99), item["id"]))
    drop_regions.sort(key=lambda item: item["id"])
    return keep_regions, auxiliary_regions, drop_regions, errors


def normalize_animation_ranges(animation_ranges: list[dict[str, Any]], source_height: int) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(animation_ranges):
        frame_range = raw.get("frame_range")
        if not isinstance(frame_range, list) or len(frame_range) != 2:
            continue
        start = max(0, min(int(frame_range[0]), source_height - 1))
        end = max(start + 1, min(int(frame_range[1]), source_height))
        item = dict(raw)
        item["id"] = raw.get("id", f"range_{index + 1:02d}")
        item["label"] = raw.get("label", item["id"])
        item["frame_range"] = [start, end]
        item["group_role"] = raw.get("group_role", "animation_row")
        item["processing_notes"] = raw.get("processing_notes", [])
        normalized.append(item)

    normalized.sort(key=lambda item: (item["frame_range"][0], item["id"]))
    return normalized


def build_structural_contract(
    manifest: dict[str, Any],
    keep_regions: list[dict[str, Any]],
    auxiliary_regions: list[dict[str, Any]],
    drop_regions: list[dict[str, Any]],
    animation_ranges: list[dict[str, Any]],
) -> dict[str, Any]:
    def build_region_contract(region: dict[str, Any], default_usage: str) -> dict[str, Any]:
        return {
            "id": region["id"],
            "classification": region.get("classification"),
            "composition_role": region.get("composition_role"),
            "usage_kind": region.get("usage_kind", default_usage),
            "export_name": region.get("export_name"),
            "normalization": region.get("normalization", []),
            "cleanup_rules": region.get("cleanup_rules", []),
            "tiling_goal": region.get("tiling_goal"),
            "pivot_policy": region.get("pivot_policy"),
            "frame_extraction_excludes": region.get("frame_extraction_excludes", []),
            "notes": region.get("notes"),
        }

    return {
        "source_layout_type": manifest.get("semantic_parse_report", {}).get("source_layout_type"),
        "shared_canvas": manifest.get("composition_schema", {}).get("shared_canvas"),
        "keep_regions": [build_region_contract(region, "scene_or_asset_region") for region in keep_regions],
        "auxiliary_regions": [build_region_contract(region, "auxiliary_data") for region in auxiliary_regions],
        "drop_regions": [
            {
                "id": region["id"],
                "classification": region.get("classification"),
                "action": region.get("action", "drop"),
                "drop_reason": region.get("drop_reason"),
                "notes": region.get("notes"),
            }
            for region in drop_regions
        ],
        "animation_ranges": animation_ranges,
    }


def render_source_overlay(
    source_path: Path,
    output_path: Path,
    keep_regions: list[dict[str, Any]],
    auxiliary_regions: list[dict[str, Any]],
    drop_regions: list[dict[str, Any]],
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

    for region in keep_regions + auxiliary_regions + drop_regions:
        left, top, right, bottom = region["bbox"]
        box = (
            12 + int(left * sx),
            12 + int(top * sy),
            12 + int(right * sx),
            12 + int(bottom * sy),
        )
        color = color_for_region(region)
        draw.rectangle(box, outline=color, width=3)
        label = region["id"]
        if region.get("classification"):
            label = f"{label} | {region['classification']}"
        draw.rectangle((box[0], box[1] - 18, min(box[0] + 260, panel.width - 12), box[1]), fill=(12, 18, 22, 220))
        draw.text((box[0] + 4, box[1] - 16), label, fill=color)

    draw.text((12, preview.height + 24), title, fill=(230, 236, 238, 255))
    for index, line in enumerate(footer_lines):
        draw.text((12, preview.height + 48 + (index * 18)), line, fill=(214, 224, 228, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def render_animation_ranges_panel(
    source_path: Path,
    output_path: Path,
    animation_ranges: list[dict[str, Any]],
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

    for index, band in enumerate(animation_ranges):
        start, end = band["frame_range"]
        color = RANGE_COLORS[index % len(RANGE_COLORS)]
        box = (
            12,
            12 + int(start * sy),
            12 + preview.width,
            12 + int(end * sy),
        )
        draw.rectangle(box, outline=color, width=3)
        label = f"{band['label']} | {band.get('group_role', 'animation_row')}"
        draw.rectangle((box[0], max(12, box[1] - 18), min(box[0] + 320, panel.width - 12), box[1]), fill=(12, 18, 22, 220))
        draw.text((box[0] + 4, max(12, box[1] - 16)), label, fill=color)

    draw.text((12, preview.height + 24), "SOURCE -> animation ranges", fill=(230, 236, 238, 255))
    for index, line in enumerate(footer_lines):
        draw.text((12, preview.height + 48 + (index * 18)), line, fill=(214, 224, 228, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def render_inferred_composition_panel(
    source_path: Path,
    output_path: Path,
    manifest_path: Path,
    keep_regions: list[dict[str, Any]],
    final_scene_reference: Path | None,
    summary: str,
) -> Path:
    with Image.open(source_path) as image:
        source = image.convert("RGBA")

    cards: list[tuple[str, Image.Image]] = [
        ("SOURCE", contain_on_canvas(source, (240, 160), (24, 34, 40, 255)))
    ]

    for region in sorted(keep_regions, key=lambda item: (ROLE_ORDER.get(item.get("composition_role") or "", 99), item.get("composition_order", 99), item["id"])):
        left, top, right, bottom = region["bbox"]
        crop = source.crop((left, top, right, bottom))
        label = region.get("composition_role") or region.get("classification") or region["id"]
        cards.append((label, contain_on_canvas(crop, (240, 160), (24, 34, 40, 255))))

    if final_scene_reference and final_scene_reference.is_file():
        with Image.open(final_scene_reference) as image:
            cards.append(("TARGET SCENE", contain_on_canvas(image.convert("RGBA"), (240, 160), (24, 34, 40, 255))))

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

    draw.text((gap + 8, gap + header_h + 160 + 10), summary, fill=(214, 224, 228, 255))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_path)
    return output_path


def audit_inferred_structure(
    manifest: dict[str, Any],
    inferred_report: dict[str, Any],
) -> dict[str, Any]:
    semantic = manifest.get("semantic_parse_report", {})
    composition_roles = {
        item.get("region_id"): item.get("composition_role")
        for item in manifest.get("composition_schema", {}).get("roles", [])
        if item.get("region_id")
    }
    truth_regions = []
    for bucket_name, action in (("semantic_regions", "keep"), ("auxiliary_regions", "auxiliary"), ("drop_regions", "drop")):
        for item in semantic.get(bucket_name, []):
            truth_regions.append(
                {
                    "id": item["id"],
                    "classification": item.get("classification"),
                    "bbox": item.get("bbox"),
                    "action": item.get("action", action),
                    "composition_role": item.get("composition_role") or composition_roles.get(item.get("id")),
                    "expected_engine_affordance": EXPECTED_ENGINE_AFFORDANCE.get(item.get("classification")),
                }
            )

    inferred_regions = inferred_report.get("regions", [])
    matched: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    used_inferred: set[str] = set()
    classification_hits = 0
    composition_hits = 0
    engine_hits = 0

    for truth in truth_regions:
        candidates = [
            item for item in inferred_regions
            if item.get("classification") == truth["classification"] and item.get("action") == truth["action"]
        ]
        if not candidates:
            missing.append({"truth_region": truth["id"], "classification": truth["classification"], "reason": "missing_classification"})
            continue
        best = max(candidates, key=lambda item: bbox_iou(item["bbox"], truth["bbox"]))
        iou = round(bbox_iou(best["bbox"], truth["bbox"]), 3)
        if iou < 0.15:
            missing.append({"truth_region": truth["id"], "classification": truth["classification"], "reason": "low_iou", "best_match": best["id"], "iou": iou})
            continue
        classification_match = best.get("classification") == truth["classification"]
        composition_match = best.get("compositional_role") == truth.get("composition_role")
        engine_match = best.get("engine_affordance") == truth.get("expected_engine_affordance")
        if classification_match:
            classification_hits += 1
        if truth.get("composition_role") in SCENE_COMPOSITION_ROLES and composition_match:
            composition_hits += 1
        if truth.get("expected_engine_affordance") is not None and engine_match:
            engine_hits += 1
        matched.append(
            {
                "truth_region": truth["id"],
                "predicted_region": best["id"],
                "iou": iou,
                "classification_match": classification_match,
                "composition_match": composition_match,
                "engine_affordance_match": engine_match,
                "confidence_bbox": best.get("confidence_bbox"),
                "confidence_classification": best.get("confidence_classification"),
                "confidence_composition": best.get("confidence_composition"),
                "confidence_engine_affordance": best.get("confidence_engine_affordance"),
            }
        )
        used_inferred.add(best["id"])

    extras = [
        {
            "predicted_region": item["id"],
            "classification": item.get("classification"),
            "action": item.get("action"),
            "engine_affordance": item.get("engine_affordance"),
        }
        for item in inferred_regions
        if item["id"] not in used_inferred
    ]

    average_iou = round(sum(item["iou"] for item in matched) / len(matched), 3) if matched else 0.0
    classification_accuracy = round(classification_hits / len(truth_regions), 3) if truth_regions else 0.0
    composition_truth_count = len([region for region in truth_regions if region.get("composition_role") in SCENE_COMPOSITION_ROLES])
    composition_accuracy = round(composition_hits / max(1, composition_truth_count), 3) if truth_regions else 0.0
    engine_truth_count = len([region for region in truth_regions if region.get("expected_engine_affordance") is not None])
    engine_accuracy = round(engine_hits / max(1, engine_truth_count), 3) if truth_regions else 0.0
    layout_match = inferred_report.get("layout_type") in {
        manifest.get("semantic_parse_report", {}).get("source_layout_type"),
        manifest.get("composition_schema", {}).get("kind"),
        "stage_board" if manifest.get("composition_schema", {}).get("kind") == "scene_layers" else None,
    }

    relaxed_missing_classes = {"author_credits", "unrelated_reference"}
    blocking_missing = [item for item in missing if item.get("classification") not in relaxed_missing_classes]

    return {
        "layout_match": layout_match,
        "truth_region_count": len(truth_regions),
        "matched_region_count": len(matched),
        "missing_region_count": len(missing),
        "extra_region_count": len(extras),
        "average_iou": average_iou,
        "classification_accuracy": classification_accuracy,
        "composition_accuracy": composition_accuracy,
        "engine_affordance_accuracy": engine_accuracy,
        "matched_regions": matched,
        "missing_regions": missing,
        "extra_regions": extras,
        "export_mode": inferred_report.get("export_mode"),
        "review_required": inferred_report.get("review_required"),
        "conflict_count": len(inferred_report.get("conflicts", [])),
        "blocking_conflict_count": len([conflict for conflict in inferred_report.get("conflicts", []) if conflict.get("blocks_final_export")]),
        "blocked_reasons": inferred_report.get("blocked_reasons", []),
        "recomposition_visual_score": inferred_report.get("recomposition_visual_score"),
        "visual_failures": inferred_report.get("visual_failures", []),
        "recomposition_pass": inferred_report.get("recomposition_pass"),
        "delivery_findings": inferred_report.get("delivery_findings", []),
        "delivery_finding_count": len(inferred_report.get("delivery_findings", [])),
        "ok": bool(layout_match)
        and not blocking_missing
        and average_iou >= 0.35
        and (composition_truth_count == 0 or composition_accuracy >= 0.5)
        and engine_accuracy >= 0.5,
    }


def build_report(manifest_path: Path, manifest: dict[str, Any], inferred_structure: dict[str, Any] | None = None) -> dict[str, Any]:
    source_path = resolve_path(manifest_path, manifest.get("source_image"))
    if source_path is None or not source_path.is_file():
        raise FileNotFoundError(f"source_image nao encontrado: {manifest.get('source_image')}")

    with Image.open(source_path) as image:
        source_size = image.size
        source_mode = image.mode

    keep_regions, auxiliary_regions, drop_regions, errors = normalize_regions(manifest, source_size)
    semantic = manifest.get("semantic_parse_report", {})
    animation_ranges = normalize_animation_ranges(semantic.get("animation_ranges", []), source_size[1])
    structural_contract = build_structural_contract(
        manifest=manifest,
        keep_regions=keep_regions,
        auxiliary_regions=auxiliary_regions,
        drop_regions=drop_regions,
        animation_ranges=animation_ranges,
    )
    final_scene_reference = resolve_path(
        manifest_path,
        semantic.get("final_scene_hypothesis", {}).get("reference_image"),
    )

    outputs_dir = Path(manifest.get("reports_dir", "")).resolve() if manifest.get("reports_dir") else None
    if outputs_dir is None:
        outputs_dir = WORKSPACE_ROOT / "assets" / "reference" / "translation_curation" / "composição_de_cenas" / "reports" / manifest["case_id"]
    outputs_dir.mkdir(parents=True, exist_ok=True)

    semantic_panel = render_source_overlay(
        source_path=source_path,
        output_path=outputs_dir / "human_semantic_panel.png",
        keep_regions=keep_regions,
        auxiliary_regions=auxiliary_regions,
        drop_regions=drop_regions,
        title="SOURCE -> semantic parse",
        footer_lines=[
            f"layout={semantic.get('source_layout_type', 'unknown')} complexity={manifest.get('layout_complexity', 'unspecified')}",
            f"keep={len(keep_regions)} aux={len(auxiliary_regions)} drop={len(drop_regions)} truth={manifest.get('scene_truth_kind', 'inferred')}",
        ],
    )
    drop_panel = render_source_overlay(
        source_path=source_path,
        output_path=outputs_dir / "drop_regions_panel.png",
        keep_regions=[],
        auxiliary_regions=[],
        drop_regions=drop_regions,
        title="SOURCE -> drop / ignore regions",
        footer_lines=manifest.get("drop_policy", {}).get("notes", ["Regioes vermelhas nao entram na cena."]),
    )
    inferred_panel = render_inferred_composition_panel(
        source_path=source_path,
        output_path=outputs_dir / "inferred_composition_panel.png",
        manifest_path=manifest_path,
        keep_regions=keep_regions,
        final_scene_reference=final_scene_reference,
        summary=semantic.get("final_scene_hypothesis", {}).get("summary", "Inferred composition hypothesis"),
    )

    animation_ranges_panel = None
    if animation_ranges:
        animation_ranges_panel = render_animation_ranges_panel(
            source_path=source_path,
            output_path=outputs_dir / "animation_ranges_panel.png",
            animation_ranges=animation_ranges,
            footer_lines=[
                "Cada faixa horizontal deve virar sequencia coerente antes do recorte por frame.",
                "A leitura por linha vem antes de pivot, padding e tiles 8x8.",
            ],
        )

    recomposed_scene_path = None
    if final_scene_reference and final_scene_reference.is_file():
        recomposed_scene_path = outputs_dir / "recomposed_scene.png"
        shutil.copyfile(final_scene_reference, recomposed_scene_path)

    report = {
        "case_id": manifest["case_id"],
        "source_image": str(source_path),
        "source_size": {
            "width": source_size[0],
            "height": source_size[1],
            "mode": source_mode,
        },
        "scene_truth_kind": manifest.get("scene_truth_kind", "inferred"),
        "layout_complexity": manifest.get("layout_complexity", "unspecified"),
        "source_inventory": manifest.get("source_inventory", {}),
        "drop_policy": manifest.get("drop_policy", {}),
        "composition_schema": manifest.get("composition_schema", {}),
        "semantic_parse_report": {
            "source_layout_type": semantic.get("source_layout_type"),
            "semantic_regions": keep_regions,
            "auxiliary_regions": auxiliary_regions,
            "drop_regions": drop_regions,
            "animation_ranges": animation_ranges,
            "final_scene_hypothesis": semantic.get("final_scene_hypothesis", {}),
            "notes_on_why": semantic.get("notes_on_why", []),
        },
        "structural_contract": structural_contract,
        "training_labels": manifest.get("training_labels", {}),
        "validation": {
            "ok": not errors,
            "errors": errors,
            "keep_region_count": len(keep_regions),
            "auxiliary_region_count": len(auxiliary_regions),
            "drop_region_count": len(drop_regions),
        },
        "outputs": {
            "semantic_parse_report": str(outputs_dir / "semantic_parse_report.json"),
            "human_semantic_panel": str(semantic_panel),
            "inferred_composition_panel": str(inferred_panel),
            "drop_regions_panel": str(drop_panel),
            "animation_ranges_panel": str(animation_ranges_panel) if animation_ranges_panel else None,
            "recomposed_scene": str(recomposed_scene_path) if recomposed_scene_path else None,
        },
    }
    if inferred_structure is not None:
        report["audit"] = audit_inferred_structure(manifest, inferred_structure)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida e materializa um caso supervisionado de parsing semantico de source.")
    parser.add_argument("--manifest", required=True, help="Manifesto JSON do caso supervisionado.")
    parser.add_argument("--output", required=True, help="JSON de saida.")
    parser.add_argument("--inferred-structure", required=False, help="derived_structure_ir.json opcional para auditoria supervisionada.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.is_file():
        print(f"Erro: manifesto nao encontrado: {manifest_path}", file=sys.stderr)
        return 1

    manifest = load_json(manifest_path)
    inferred_structure = None
    if args.inferred_structure:
        inferred_path = Path(args.inferred_structure).resolve()
        if not inferred_path.is_file():
            print(f"Erro: inferred-structure nao encontrado: {inferred_path}", file=sys.stderr)
            return 1
        inferred_structure = load_json(inferred_path)

    report = build_report(manifest_path, manifest, inferred_structure)
    output_path = Path(args.output).resolve()
    save_json(output_path, report)

    semantic_report_path = Path(report["outputs"]["semantic_parse_report"])
    save_json(semantic_report_path, report)

    print(
        json.dumps(
            {
                "case_id": report["case_id"],
                "ok": report["validation"]["ok"],
                "keep_regions": report["validation"]["keep_region_count"],
                "drop_regions": report["validation"]["drop_region_count"],
                "audit_ok": report.get("audit", {}).get("ok"),
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["validation"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
