#!/usr/bin/env python3
"""
infer_source_structure.py - infere uma IR estrutural minima a partir de um source.

Uso:
  python infer_source_structure.py --source <png> --output-dir <dir> [--layout-hint auto|stage_board|sprite_sheet|tile_object_sheet|editorial_board]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any

import numpy as np

try:
    from PIL import Image
except ImportError:
    print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
    sys.exit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent

LAYOUT_HINTS = {"auto", "stage_board", "sprite_sheet", "tile_object_sheet", "editorial_board"}

CLASS_TO_REGION_DEFAULTS = {
    "scene_plane_sky": {"action": "keep", "system_role": "scene_layer", "candidate_asset_kind": "scene_layer", "compositional_role": "scene_plane_bg_b", "engine_affordance": "scene_layer_continuous"},
    "scene_plane_bg_b": {"action": "keep", "system_role": "scene_layer", "candidate_asset_kind": "scene_layer", "compositional_role": "scene_plane_bg_b", "engine_affordance": "scene_layer_continuous"},
    "scene_plane_architecture": {"action": "keep", "system_role": "scene_layer", "candidate_asset_kind": "scene_layer", "compositional_role": "scene_plane_bg_a", "engine_affordance": "scene_layer_continuous"},
    "scene_plane_bg_a": {"action": "keep", "system_role": "scene_layer", "candidate_asset_kind": "scene_layer", "compositional_role": "scene_plane_bg_a", "engine_affordance": "scene_layer_continuous"},
    "scene_plane_ground": {"action": "keep", "system_role": "scene_layer", "candidate_asset_kind": "scene_layer", "compositional_role": "scene_plane_bg_a", "engine_affordance": "scene_layer_continuous"},
    "scene_plane_foreground_composition": {"action": "keep", "system_role": "scene_layer", "candidate_asset_kind": "scene_layer", "compositional_role": "scene_plane_foreground_composition", "engine_affordance": "scene_layer_continuous"},
    "actor_sprite_sheet": {"action": "keep", "system_role": "sprite_sequence_source", "candidate_asset_kind": "sprite_sheet", "compositional_role": None, "engine_affordance": "sprite_sequence"},
    "palette_strip": {"action": "auxiliary", "system_role": "auxiliary_reference", "candidate_asset_kind": "auxiliary_data", "compositional_role": None, "engine_affordance": "auxiliary_reference"},
    "metadata_block": {"action": "drop", "system_role": "editorial_noise", "candidate_asset_kind": "editorial_noise", "compositional_role": None, "engine_affordance": "editorial_noise"},
    "author_credits": {"action": "drop", "system_role": "editorial_noise", "candidate_asset_kind": "editorial_noise", "compositional_role": None, "engine_affordance": "editorial_noise"},
    "avatar_or_icon": {"action": "drop", "system_role": "editorial_noise", "candidate_asset_kind": "editorial_noise", "compositional_role": None, "engine_affordance": "editorial_noise"},
    "mockup_preview": {"action": "drop", "system_role": "editorial_noise", "candidate_asset_kind": "editorial_noise", "compositional_role": None, "engine_affordance": "editorial_noise"},
    "unrelated_reference": {"action": "drop", "system_role": "editorial_noise", "candidate_asset_kind": "editorial_noise", "compositional_role": None, "engine_affordance": "editorial_noise"},
    "tile_cluster": {"action": "keep", "system_role": "tile_base_source", "candidate_asset_kind": "tile_cluster", "compositional_role": None, "engine_affordance": "tile_base_reusable"},
    "overlay_cluster": {"action": "keep", "system_role": "overlay_source", "candidate_asset_kind": "overlay_cluster", "compositional_role": None, "engine_affordance": "tile_overlay_dependent"},
    "object_animation_sequence": {"action": "keep", "system_role": "object_state_sequence", "candidate_asset_kind": "object_sequence", "compositional_role": None, "engine_affordance": "object_state_sequence"},
    "corrupted_region": {"action": "drop", "system_role": "editorial_noise", "candidate_asset_kind": "discard", "compositional_role": None, "engine_affordance": "corrupted_discard"},
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def safe_slug(text: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in text).strip("_")


def quantize_color(color: tuple[int, int, int], step: int = 16) -> tuple[int, int, int]:
    return tuple(int((channel // step) * step) for channel in color)


def dominant_border_color(array: np.ndarray) -> tuple[int, int, int]:
    height, width = array.shape[:2]
    thickness = max(2, min(height, width) // 80)
    border = np.concatenate(
        [
            array[:thickness, :, :3].reshape(-1, 3),
            array[-thickness:, :, :3].reshape(-1, 3),
            array[:, :thickness, :3].reshape(-1, 3),
            array[:, -thickness:, :3].reshape(-1, 3),
        ],
        axis=0,
    )
    counts = Counter(quantize_color(tuple(pixel), step=16) for pixel in border)
    return counts.most_common(1)[0][0]


def build_border_connected_background_mask(
    array: np.ndarray,
    background_color: tuple[int, int, int],
    threshold: int = 26,
) -> np.ndarray:
    height, width = array.shape[:2]
    if height == 0 or width == 0:
        return np.zeros((height, width), dtype=bool)

    background = np.array(background_color, dtype=np.int16)
    delta = np.abs(array[:, :, :3].astype(np.int16) - background)
    candidate = np.max(delta, axis=2) <= threshold

    visited = np.zeros((height, width), dtype=bool)
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


def build_color_mask(array: np.ndarray, background_color: tuple[int, int, int], threshold: int = 26) -> np.ndarray:
    alpha_mask = array[:, :, 3] > 0
    connected_background = build_border_connected_background_mask(array, background_color, threshold=threshold)
    return alpha_mask & ~connected_background


def row_activity(mask: np.ndarray) -> np.ndarray:
    return mask.mean(axis=1)


def col_activity(mask: np.ndarray) -> np.ndarray:
    return mask.mean(axis=0)


def find_active_ranges(activity: np.ndarray, threshold: float, min_size: int, merge_gap: int) -> list[tuple[int, int]]:
    active = activity > threshold
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    for index, flag in enumerate(active):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            if index - start >= min_size:
                ranges.append((start, index))
            start = None
    if start is not None and len(activity) - start >= min_size:
        ranges.append((start, len(activity)))

    if not ranges:
        return []

    merged = [ranges[0]]
    for current_start, current_end in ranges[1:]:
        last_start, last_end = merged[-1]
        if current_start - last_end <= merge_gap:
            merged[-1] = (last_start, current_end)
        else:
            merged.append((current_start, current_end))
    return merged


def connected_components(mask: np.ndarray, min_area: int = 32) -> list[dict[str, Any]]:
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=np.uint8)
    components: list[dict[str, Any]] = []
    neighbors = ((1, 0), (-1, 0), (0, 1), (0, -1))
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue
            queue: deque[tuple[int, int]] = deque([(x, y)])
            visited[y, x] = 1
            area = 0
            min_x = max_x = x
            min_y = max_y = y
            while queue:
                current_x, current_y = queue.popleft()
                area += 1
                min_x = min(min_x, current_x)
                max_x = max(max_x, current_x)
                min_y = min(min_y, current_y)
                max_y = max(max_y, current_y)
                for delta_x, delta_y in neighbors:
                    next_x = current_x + delta_x
                    next_y = current_y + delta_y
                    if next_x < 0 or next_y < 0 or next_x >= width or next_y >= height:
                        continue
                    if visited[next_y, next_x] or not mask[next_y, next_x]:
                        continue
                    visited[next_y, next_x] = 1
                    queue.append((next_x, next_y))
            if area >= min_area:
                components.append({"bbox": [min_x, min_y, max_x + 1, max_y + 1], "area": area, "width": (max_x + 1) - min_x, "height": (max_y + 1) - min_y})
    components.sort(key=lambda item: item["area"], reverse=True)
    return components


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


def bbox_width(bbox: list[int]) -> int:
    return max(0, bbox[2] - bbox[0])


def bbox_height(bbox: list[int]) -> int:
    return max(0, bbox[3] - bbox[1])


def bbox_center_in_span(value: float, start: int, end: int, margin: int = 0) -> bool:
    return (start - margin) <= value <= (end + margin)


def bbox_iou(a: list[int], b: list[int]) -> float:
    intersection = bbox_intersection(a, b)
    if intersection == 0:
        return 0.0
    union = bbox_area(a) + bbox_area(b) - intersection
    return float(intersection / union) if union else 0.0


def union_bboxes(boxes: list[list[int]]) -> list[int]:
    return [min(box[0] for box in boxes), min(box[1] for box in boxes), max(box[2] for box in boxes), max(box[3] for box in boxes)]


def bbox_center_x(bbox: list[int]) -> float:
    return (bbox[0] + bbox[2]) / 2.0


def bbox_center_y(bbox: list[int]) -> float:
    return (bbox[1] + bbox[3]) / 2.0


def bbox_overlap_ratio(inner: list[int], outer: list[int]) -> float:
    area = bbox_area(inner)
    if area <= 0:
        return 0.0
    return bbox_intersection(inner, outer) / float(area)


def expand_bbox(bbox: list[int], margin: int, width: int, height: int) -> list[int]:
    return [max(0, bbox[0] - margin), max(0, bbox[1] - margin), min(width, bbox[2] + margin), min(height, bbox[3] + margin)]


def shrink_bbox_right(bbox: list[int], right_edge: int, min_width: int = 24) -> list[int] | None:
    if right_edge - bbox[0] < min_width:
        return None
    return [bbox[0], bbox[1], min(bbox[2], right_edge), bbox[3]]


def extract_crop(array: np.ndarray, bbox: list[int]) -> np.ndarray:
    return array[bbox[1]:bbox[3], bbox[0]:bbox[2]]


def edge_structure_score(region_array: np.ndarray) -> float:
    if region_array.size == 0:
        return 0.0
    rgb = region_array[:, :, :3].astype(np.int16)
    diff_x = np.abs(np.diff(rgb, axis=1)).mean() if region_array.shape[1] > 1 else 0.0
    diff_y = np.abs(np.diff(rgb, axis=0)).mean() if region_array.shape[0] > 1 else 0.0
    return float(clamp((diff_x + diff_y) / 96.0, 0.0, 1.0))


def black_ratio(region_array: np.ndarray) -> float:
    if region_array.size == 0:
        return 0.0
    rgb = region_array[:, :, :3]
    return float(np.mean(np.max(rgb, axis=2) < 32))


def unique_color_score(region_array: np.ndarray) -> float:
    if region_array.size == 0:
        return 0.0
    quantized = (region_array[:, :, :3] // 32).reshape(-1, 3)
    return float(min(1.0, len(np.unique(quantized, axis=0)) / 48.0))


def background_ratio(region_array: np.ndarray, background_color: tuple[int, int, int]) -> float:
    if region_array.size == 0:
        return 0.0
    mask = build_color_mask(region_array, background_color, threshold=26)
    return float(1.0 - mask.mean())


def row_band_membership(bands: list[tuple[int, int]], bbox: list[int]) -> list[int]:
    members: list[int] = []
    for index, (start, end) in enumerate(bands):
        if bbox[1] < end and bbox[3] > start:
            members.append(index)
    return members


def compute_region_signature(
    array: np.ndarray,
    mask: np.ndarray,
    components: list[dict[str, Any]],
    bbox: list[int],
    background_color: tuple[int, int, int],
    bands: list[tuple[int, int]],
) -> dict[str, Any]:
    region_array = extract_crop(array, bbox)
    region_mask = mask[bbox[1]:bbox[3], bbox[0]:bbox[2]]
    intersecting_components = [item for item in components if bbox_intersection(item["bbox"], bbox) > 0]
    content_density = float(region_mask.mean()) if region_mask.size else 0.0
    widths = [item["width"] for item in intersecting_components]
    heights = [item["height"] for item in intersecting_components]
    repeat_score = 0.0
    if len(widths) >= 4 and np.mean(widths) > 0 and np.mean(heights) > 0:
        repeat_score = float(
            clamp(
                (1.0 - min(1.0, float(np.std(widths) / max(1.0, np.mean(widths))))) * 0.5
                + (1.0 - min(1.0, float(np.std(heights) / max(1.0, np.mean(heights))))) * 0.3
                + min(1.0, len(widths) / 16.0) * 0.2,
                0.0,
                1.0,
            )
        )

    text_like = 0.0
    bbox_w = max(1, bbox[2] - bbox[0])
    bbox_h = max(1, bbox[3] - bbox[1])
    if bbox_h <= max(48, array.shape[0] * 0.12):
        text_like = float(clamp((len(intersecting_components) / 24.0) + ((bbox_w / max(1, array.shape[1])) * 0.4), 0.0, 1.0))

    return {
        "bbox": bbox,
        "pixel_signature": {
            "mean_rgb": [int(value) for value in region_array[:, :, :3].mean(axis=(0, 1))] if region_array.size else [0, 0, 0],
            "unique_color_score": unique_color_score(region_array),
            "black_ratio": black_ratio(region_array),
            "background_ratio": background_ratio(region_array, background_color),
        },
        "content_density": content_density,
        "repeat_pattern_score": repeat_score,
        "uniformity_score": float(clamp(1.0 - edge_structure_score(region_array), 0.0, 1.0)),
        "text_like_score": text_like,
        "edge_structure_score": edge_structure_score(region_array),
        "background_key_color": list(background_color),
        "row_band_membership": row_band_membership(bands, bbox),
        "neighbor_relations": [],
        "overlap_relations": [],
        "component_count": len(intersecting_components),
    }


def with_defaults(region_id: str, classification: str, bbox: list[int], signature: dict[str, Any]) -> dict[str, Any]:
    defaults = CLASS_TO_REGION_DEFAULTS[classification]
    return {
        "id": region_id,
        "bbox": bbox,
        "action": defaults["action"],
        "classification": classification,
        "system_role": defaults["system_role"],
        "candidate_asset_kind": defaults["candidate_asset_kind"],
        "compositional_role": defaults["compositional_role"],
        "engine_affordance": defaults["engine_affordance"],
        "confidence_bbox": 0.82,
        "confidence_classification": 0.78,
        "confidence_composition": 0.74 if defaults["compositional_role"] else 0.64,
        "confidence_engine_affordance": 0.78,
        "review_required": False,
        "observed_signature": signature,
    }


def add_confidence(region: dict[str, Any], bbox: float, classification: float, composition: float, engine: float) -> dict[str, Any]:
    region["confidence_bbox"] = round(clamp(bbox, 0.0, 1.0), 3)
    region["confidence_classification"] = round(clamp(classification, 0.0, 1.0), 3)
    region["confidence_composition"] = round(clamp(composition, 0.0, 1.0), 3)
    region["confidence_engine_affordance"] = round(clamp(engine, 0.0, 1.0), 3)
    region["review_required"] = any(value < 0.72 for key, value in region.items() if key.startswith("confidence_"))
    return region


def derive_ref_from_signature(signature: dict[str, Any]) -> str | None:
    for key in ("band_id", "component_id"):
        if signature.get(key):
            return str(signature[key])
    return None


def strip_region_to_derived(region: dict[str, Any]) -> dict[str, Any]:
    derived = {key: value for key, value in region.items() if key != "observed_signature"}
    signature = region.get("observed_signature", {})
    evidence_ref = derive_ref_from_signature(signature)
    if evidence_ref:
        derived["observed_ref"] = evidence_ref
    return derived


def infer_layout_type(array: np.ndarray, background_color: tuple[int, int, int], mask: np.ndarray, hint: str) -> str:
    if hint != "auto":
        return hint

    height, width = array.shape[:2]
    if height > width * 2.0:
        return "sprite_sheet"

    quantized_bg = quantize_color(background_color, step=16)
    if quantized_bg[0] >= 224 and quantized_bg[2] >= 224 and quantized_bg[1] <= 64:
        return "tile_object_sheet"

    bands = find_active_ranges(row_activity(mask), threshold=0.02, min_size=max(8, height // 80), merge_gap=max(4, height // 100))
    large_component_count = len([component for component in connected_components(mask, min_area=max(128, (height * width) // 250)) if component["area"] > (height * width * 0.01)])

    if width > height * 1.3 and large_component_count >= 3:
        return "editorial_board"
    if len(bands) >= 4:
        return "stage_board"
    return "stage_board"


def build_band_bbox(mask: np.ndarray, start: int, end: int) -> list[int] | None:
    band_mask = mask[start:end, :]
    if not band_mask.any():
        return None
    cols = np.where(col_activity(band_mask) > 0.01)[0]
    if len(cols) == 0:
        return None
    return [int(cols[0]), int(start), int(cols[-1] + 1), int(end)]


def maybe_split_architecture_and_ground(
    array: np.ndarray,
    mask: np.ndarray,
    components: list[dict[str, Any]],
    band: dict[str, Any],
    background_color: tuple[int, int, int],
    bands: list[tuple[int, int]],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    bbox = band["bbox"]
    band_h = bbox_height(bbox)
    if band_h < max(56, int(array.shape[0] * 0.22)):
        return None

    lower_h = int(clamp(band_h * 0.24, 32, band_h * 0.38))
    cut_y = bbox[3] - lower_h
    if cut_y <= bbox[1] + 24:
        return None

    architecture_bbox = [bbox[0], bbox[1], bbox[2], cut_y]
    ground_bbox = [bbox[0], cut_y, bbox[2], bbox[3]]
    architecture_signature = compute_region_signature(array, mask, components, architecture_bbox, background_color, bands)
    ground_signature = compute_region_signature(array, mask, components, ground_bbox, background_color, bands)

    if ground_signature["edge_structure_score"] >= architecture_signature["edge_structure_score"] * 0.95 and band_h <= int(array.shape[0] * 0.34):
        return None
    if ground_signature["text_like_score"] > 0.28:
        return None
    return (architecture_signature, ground_signature)


def detect_stage_board(
    array: np.ndarray,
    mask: np.ndarray,
    components: list[dict[str, Any]],
    background_color: tuple[int, int, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    height, width = array.shape[:2]
    bands = find_active_ranges(row_activity(mask), threshold=0.025, min_size=max(10, height // 70), merge_gap=max(4, height // 120))

    observed_bands: list[dict[str, Any]] = []
    for index, (start, end) in enumerate(bands):
        bbox = build_band_bbox(mask, start, end)
        if bbox is None:
            continue
        signature = compute_region_signature(array, mask, components, bbox, background_color, bands)
        signature["band_id"] = f"band_{index + 1:02d}"
        observed_bands.append(signature)

    keep: list[dict[str, Any]] = []
    auxiliary: list[dict[str, Any]] = []
    drop: list[dict[str, Any]] = []
    sequences: list[dict[str, Any]] = []

    right_side_components = [
        component
        for component in components
        if component["bbox"][0] > int(width * 0.78)
        and component["bbox"][1] > int(height * 0.18)
        and component["bbox"][3] < int(height * 0.78)
        and component["area"] > max(48, (height * width) // 18000)
    ]
    preview_bbox: list[int] | None = None
    if right_side_components:
        preview_bbox = union_bboxes([item["bbox"] for item in right_side_components])
        preview_signature = compute_region_signature(array, mask, components, preview_bbox, background_color, bands)
        drop.append(add_confidence(with_defaults("preview_stack", "mockup_preview", preview_bbox, preview_signature), 0.82, 0.78, 0.08, 0.96))

    remaining: list[dict[str, Any]] = []
    for band in observed_bands:
        adjusted_band = band
        if preview_bbox and bbox_intersection(band["bbox"], preview_bbox) > bbox_area(band["bbox"]) * 0.08:
            trimmed_bbox = shrink_bbox_right(band["bbox"], preview_bbox[0] - 2, min_width=max(32, int(width * 0.35)))
            if trimmed_bbox is not None:
                adjusted_band = compute_region_signature(array, mask, components, trimmed_bbox, background_color, bands)
                adjusted_band["band_id"] = band["band_id"]
        remaining.append(adjusted_band)

    if remaining:
        bottom_band = remaining[-1]
        if (
            bottom_band["text_like_score"] > 0.38
            or (
                bottom_band["bbox"][1] > height * 0.84
                and bottom_band["component_count"] >= 4
                and bbox_height(bottom_band["bbox"]) < height * 0.12
            )
        ):
            region = with_defaults("credits_block", "author_credits", bottom_band["bbox"], bottom_band)
            add_confidence(region, 0.88, 0.85, 0.98, 0.98)
            drop.append(region)
            remaining = remaining[:-1]

    actor_like: list[dict[str, Any]] = []
    filtered_remaining: list[dict[str, Any]] = []
    for band in remaining:
        actor_score = 0.0
        actor_score += 0.4 if band["repeat_pattern_score"] > 0.42 else 0.0
        actor_score += 0.25 if band["component_count"] >= 8 else 0.0
        actor_score += 0.15 if band["bbox"][1] > height * 0.68 else 0.0
        actor_score += 0.1 if band["content_density"] < 0.58 else 0.0
        actor_score += 0.1 if bbox_height(band["bbox"]) < height * 0.12 else 0.0
        actor_score += 0.2 if band["text_like_score"] > 0.3 else 0.0
        actor_score += 0.15 if band["edge_structure_score"] > 0.22 else 0.0
        if actor_score >= 0.6:
            actor_like.append(band)
        else:
            filtered_remaining.append(band)
    remaining = filtered_remaining

    for index, band in enumerate(actor_like):
        region = with_defaults(f"actor_strip_{index + 1:02d}", "actor_sprite_sheet", band["bbox"], band)
        add_confidence(region, 0.86, 0.81, 0.1, 0.92)
        region["action"] = "drop"
        region["system_role"] = "editorial_noise"
        region["candidate_asset_kind"] = "editorial_noise"
        region["engine_affordance"] = "editorial_noise"
        drop.append(region)

    if not remaining:
        return observed_bands, keep, auxiliary, drop, sequences

    top_band = min(remaining, key=lambda item: item["bbox"][1])
    split_result = maybe_split_architecture_and_ground(array, mask, components, top_band, background_color, bands)
    if split_result is None and bbox_height(top_band["bbox"]) > int(height * 0.34) and top_band["bbox"][1] < int(height * 0.08):
        bbox = top_band["bbox"]
        lower_h = int(clamp(bbox_height(bbox) * 0.24, 32, bbox_height(bbox) * 0.38))
        cut_y = bbox[3] - lower_h
        architecture_signature = compute_region_signature(array, mask, components, [bbox[0], bbox[1], bbox[2], cut_y], background_color, bands)
        ground_signature = compute_region_signature(array, mask, components, [bbox[0], cut_y, bbox[2], bbox[3]], background_color, bands)
        split_result = (architecture_signature, ground_signature)
    if split_result is not None:
        architecture_signature, ground_signature = split_result
        remaining = [item for item in remaining if item["band_id"] != top_band["band_id"]]
        architecture_signature["band_id"] = f"{top_band['band_id']}_architecture"
        ground_signature["band_id"] = f"{top_band['band_id']}_ground"
        remaining.extend([architecture_signature, ground_signature])

    sky_band = max(
        remaining,
        key=lambda item: (
            (item["pixel_signature"]["mean_rgb"][2] - item["pixel_signature"]["mean_rgb"][0]),
            item["uniformity_score"],
            -item["edge_structure_score"],
            bbox_width(item["bbox"]),
        ),
    )
    remaining = [item for item in remaining if item["band_id"] != sky_band["band_id"]]
    keep.append(add_confidence(with_defaults("sky_strip", "scene_plane_sky", sky_band["bbox"], sky_band), 0.9, 0.84, 0.9, 0.82))

    if remaining:
        ground_band = min(remaining, key=lambda item: (bbox_height(item["bbox"]), abs(bbox_center_y(item["bbox"]) - (height * 0.35)), -bbox_width(item["bbox"])))
        remaining = [item for item in remaining if item["band_id"] != ground_band["band_id"]]
        keep.append(add_confidence(with_defaults("ground_perspective_strip", "scene_plane_ground", ground_band["bbox"], ground_band), 0.88, 0.79, 0.86, 0.83))

    for index, band in enumerate(sorted(remaining, key=lambda item: item["bbox"][1])):
        region_id = "architecture_panel" if index == 0 else f"preview_block_{index:02d}"
        classification = "scene_plane_architecture" if index == 0 else "mockup_preview"
        region = with_defaults(region_id, classification, band["bbox"], band)
        if classification == "scene_plane_architecture":
            keep.append(add_confidence(region, 0.9, 0.83, 0.88, 0.84))
        else:
            drop.append(add_confidence(region, 0.82, 0.72, 0.08, 0.95))

    return observed_bands, keep, auxiliary, drop, sequences


def detect_editorial_board(
    array: np.ndarray,
    mask: np.ndarray,
    components: list[dict[str, Any]],
    background_color: tuple[int, int, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    height, width = array.shape[:2]
    large_components = [component for component in components if component["area"] > (height * width * 0.005)]
    bands = find_active_ranges(row_activity(mask), threshold=0.02, min_size=max(8, height // 80), merge_gap=max(4, height // 100))
    observed_components = [compute_region_signature(array, mask, components, component["bbox"], background_color, bands) for component in large_components]

    keep: list[dict[str, Any]] = []
    auxiliary: list[dict[str, Any]] = []
    drop: list[dict[str, Any]] = []
    sequences: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for component in observed_components:
        bbox = component["bbox"]
        bbox_w = bbox[2] - bbox[0]
        bbox_h = bbox[3] - bbox[1]
        x_center = (bbox[0] + bbox[2]) / 2.0
        area_ratio = bbox_area(bbox) / float(width * height)

        if bbox[1] > height * 0.72 and bbox_w < width * 0.12 and bbox_h < height * 0.16:
            drop.append(add_confidence(with_defaults("avatar_block", "avatar_or_icon", bbox, component), 0.84, 0.78, 0.08, 0.96))
        elif bbox[1] > height * 0.72 and bbox_w > width * 0.16 and bbox_h < height * 0.2:
            drop.append(add_confidence(with_defaults("credits_block", "author_credits", bbox, component), 0.86, 0.8, 0.08, 0.96))
        elif x_center > width * 0.72 and area_ratio > 0.04:
            drop.append(add_confidence(with_defaults("mockup_preview", "mockup_preview", bbox, component), 0.84, 0.78, 0.08, 0.96))
        else:
            candidates.append(component)

    if not any(region["classification"] == "author_credits" for region in drop):
        avatar_region = next((region for region in drop if region["classification"] == "avatar_or_icon"), None)
        avatar_bbox = avatar_region["bbox"] if avatar_region else None
        editorial_components = [
            component
            for component in components
            if component["bbox"][1] > int(height * 0.74)
            and component["bbox"][0] > int(width * 0.68)
            and component["area"] > max(24, (height * width) // 45000)
        ]
        credit_boxes = [
            component["bbox"]
            for component in editorial_components
            if avatar_bbox is None or bbox_iou(component["bbox"], avatar_bbox) < 0.35
        ]
        if credit_boxes:
            credits_bbox = expand_bbox(union_bboxes(credit_boxes), 2, width, height)
            credits_signature = compute_region_signature(array, mask, components, credits_bbox, background_color, bands)
            drop.append(add_confidence(with_defaults("credits_block", "author_credits", credits_bbox, credits_signature), 0.82, 0.76, 0.08, 0.96))

    candidates.sort(key=lambda item: (item["bbox"][1], item["bbox"][0]))
    if candidates:
        top = candidates.pop(0)
        keep.append(add_confidence(with_defaults("bg_b_strip", "scene_plane_bg_b", top["bbox"], top), 0.9, 0.84, 0.91, 0.83))
    if candidates:
        middle = max(candidates, key=lambda item: bbox_area(item["bbox"]))
        candidates = [item for item in candidates if item["bbox"] != middle["bbox"]]
        keep.append(add_confidence(with_defaults("bg_a_main", "scene_plane_bg_a", middle["bbox"], middle), 0.89, 0.82, 0.9, 0.82))
    if candidates:
        bottom = max(candidates, key=lambda item: item["bbox"][1])
        candidates = [item for item in candidates if item["bbox"] != bottom["bbox"]]
        keep.append(add_confidence(with_defaults("foreground_strip", "scene_plane_foreground_composition", bottom["bbox"], bottom), 0.88, 0.81, 0.88, 0.8))

    for index, component in enumerate(candidates):
        drop.append(add_confidence(with_defaults(f"unrelated_reference_{index + 1:02d}", "unrelated_reference", component["bbox"], component), 0.8, 0.72, 0.05, 0.96))

    return observed_components, keep, auxiliary, drop, sequences


def sequence_confidence(frame_bboxes: list[list[int]]) -> tuple[float, float]:
    if not frame_bboxes:
        return (0.0, 0.0)
    widths = np.array([box[2] - box[0] for box in frame_bboxes], dtype=np.float32)
    heights = np.array([box[3] - box[1] for box in frame_bboxes], dtype=np.float32)
    bottoms = np.array([box[3] for box in frame_bboxes], dtype=np.float32)
    centers_x = np.array([bbox_center_x(box) for box in frame_bboxes], dtype=np.float32)
    spacings = np.diff(np.sort(centers_x)) if len(frame_bboxes) >= 2 else np.array([], dtype=np.float32)

    width_stability = 1.0 - min(1.0, float(np.std(widths) / max(1.0, np.mean(widths))))
    height_stability = 1.0 - min(1.0, float(np.std(heights) / max(1.0, np.mean(heights))))
    spacing_stability = 1.0
    if spacings.size:
        spacing_stability = 1.0 - min(1.0, float(np.std(spacings) / max(1.0, np.mean(spacings))))

    grouping = 0.54 + (0.14 * width_stability) + (0.16 * height_stability) + (0.1 * spacing_stability) + (0.1 * min(1.0, len(frame_bboxes) / 5.0))
    pivot = 0.68 + (0.18 * (1.0 - min(1.0, float(np.std(bottoms) / max(1.0, np.mean(heights)))))) + (0.08 * height_stability)
    return (round(clamp(grouping, 0.0, 1.0), 3), round(clamp(pivot, 0.0, 1.0), 3))


def components_in_zone(components: list[dict[str, Any]], zone: list[int], min_overlap_ratio: float = 0.55) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for component in components:
        overlap_ratio = bbox_overlap_ratio(component["bbox"], zone)
        center_y = bbox_center_y(component["bbox"])
        if overlap_ratio >= min_overlap_ratio or (center_y >= zone[1] and center_y <= zone[3]):
            selected.append(component)
    return selected


def isolate_dark_overlay_bbox(
    array: np.ndarray,
    bbox: list[int],
    threshold: int = 48,
    padding: int = 2,
) -> list[int] | None:
    crop = extract_crop(array, bbox)
    if crop.size == 0:
        return None
    dark_mask = np.max(crop[:, :, :3], axis=2) < threshold
    if not dark_mask.any():
        return None

    ys, xs = np.where(dark_mask)
    local_bbox = [
        max(0, int(xs.min()) - padding),
        max(0, int(ys.min()) - padding),
        min(crop.shape[1], int(xs.max()) + 1 + padding),
        min(crop.shape[0], int(ys.max()) + 1 + padding),
    ]
    absolute_bbox = [
        bbox[0] + local_bbox[0],
        bbox[1] + local_bbox[1],
        bbox[0] + local_bbox[2],
        bbox[1] + local_bbox[3],
    ]
    if bbox_area(absolute_bbox) <= 0:
        return None
    return absolute_bbox


def group_frames_from_components(band_bbox: list[int], components: list[dict[str, Any]]) -> list[list[int]]:
    relevant = [component for component in components if bbox_intersection(component["bbox"], band_bbox) > 0]
    if not relevant:
        return []

    relevant.sort(key=lambda item: item["bbox"][0])
    band_height = max(1, bbox_height(band_bbox))
    median_width = max(8.0, float(np.median([item["width"] for item in relevant])))
    gap_threshold = max(3, int(median_width * 0.16))
    support_margin = max(2, int(median_width * 0.08))

    filtered: list[dict[str, Any]] = []
    for component in relevant:
        component_bbox = component["bbox"]
        intersection = bbox_intersection(component_bbox, band_bbox)
        if intersection <= 0:
            continue
        overlap_h = max(0, min(component_bbox[3], band_bbox[3]) - max(component_bbox[1], band_bbox[1]))
        visible_height_ratio = overlap_h / max(1, bbox_height(component_bbox))
        center_inside = bbox_center_in_span(bbox_center_y(component_bbox), band_bbox[1], band_bbox[3])
        if center_inside or visible_height_ratio >= 0.38 or overlap_h >= max(10, int(band_height * 0.34)):
            filtered.append(component)

    if not filtered:
        return []

    clusters: list[list[list[int]]] = []
    current: list[list[int]] = [filtered[0]["bbox"]]
    last_right = filtered[0]["bbox"][2]
    for item in filtered[1:]:
        left = item["bbox"][0]
        if left - last_right <= gap_threshold:
            current.append(item["bbox"])
        else:
            clusters.append(current)
            current = [item["bbox"]]
        last_right = max(last_right, item["bbox"][2])
    clusters.append(current)

    frame_boxes: list[list[int]] = []
    for cluster in clusters:
        cluster_box = union_bboxes(cluster)
        supporting_components = [
            component["bbox"]
            for component in filtered
            if bbox_center_in_span(bbox_center_x(component["bbox"]), cluster_box[0], cluster_box[2], margin=support_margin)
        ]
        frame_boxes.append(union_bboxes(supporting_components or [cluster_box]))

    return frame_boxes


def detect_sprite_sheet(
    array: np.ndarray,
    mask: np.ndarray,
    components: list[dict[str, Any]],
    background_color: tuple[int, int, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    height, width = array.shape[:2]
    bands = find_active_ranges(row_activity(mask), threshold=0.015, min_size=max(12, height // 120), merge_gap=max(6, height // 180))
    observed_bands: list[dict[str, Any]] = []
    for index, (start, end) in enumerate(bands):
        bbox = build_band_bbox(mask, start, end)
        if bbox is None:
            continue
        signature = compute_region_signature(array, mask, components, bbox, background_color, bands)
        signature["band_id"] = f"band_{index + 1:02d}"
        observed_bands.append(signature)

    keep: list[dict[str, Any]] = []
    auxiliary: list[dict[str, Any]] = []
    drop: list[dict[str, Any]] = []
    sequences: list[dict[str, Any]] = []

    if not observed_bands:
        return observed_bands, keep, auxiliary, drop, sequences

    metadata_cut = int(height * 0.905)
    metadata_bbox = [0, metadata_cut, width, height]
    metadata_signature = compute_region_signature(array, mask, components, metadata_bbox, background_color, bands)
    actor_bands = [item for item in observed_bands if item["bbox"][1] < metadata_cut]
    if not actor_bands:
        actor_bands = observed_bands[:]
    if metadata_signature["content_density"] > 0.02:
        drop.append(add_confidence(with_defaults("metadata_block", "metadata_block", metadata_bbox, metadata_signature), 0.92, 0.9, 0.96, 0.98))
    elif observed_bands:
        metadata_band = max(observed_bands, key=lambda item: item["bbox"][1])
        if metadata_band["bbox"][1] > height * 0.88 or metadata_band["text_like_score"] > 0.3:
            drop.append(add_confidence(with_defaults("metadata_block", "metadata_block", metadata_band["bbox"], metadata_band), 0.9, 0.9, 0.96, 0.98))
            actor_bands = [item for item in observed_bands if item["band_id"] != metadata_band["band_id"]]

    actor_bbox = union_bboxes([band["bbox"] for band in actor_bands])
    actor_signature = compute_region_signature(array, mask, components, actor_bbox, background_color, bands)
    actor_region = add_confidence(with_defaults("actor_sheet", "actor_sprite_sheet", actor_bbox, actor_signature), 0.92, 0.86, 0.08, 0.88)
    keep.append(actor_region)

    candidate_palette_components = [
        component
        for component in components
        if bbox_center_x(component["bbox"]) > int(actor_bbox[0] + ((actor_bbox[2] - actor_bbox[0]) * 0.72))
        and bbox_center_y(component["bbox"]) > int(actor_bbox[1] + ((actor_bbox[3] - actor_bbox[1]) * 0.82))
        and component["bbox"][3] < metadata_cut
        and bbox_area(component["bbox"]) < (bbox_area(actor_bbox) * 0.04)
        and bbox_height(component["bbox"]) < max(18, int(actor_bbox[3] - actor_bbox[1]) * 0.14)
    ]
    palette_bbox: list[int] | None = None
    if candidate_palette_components:
        palette_bbox = expand_bbox(union_bboxes([item["bbox"] for item in candidate_palette_components]), 2, width, height)
        palette_signature = compute_region_signature(array, mask, components, palette_bbox, background_color, bands)
        auxiliary.append(add_confidence(with_defaults("palette_block", "palette_strip", palette_bbox, palette_signature), 0.82, 0.72, 0.08, 0.95))

    filtered_actor_bands: list[dict[str, Any]] = []
    for band in actor_bands:
        if palette_bbox is not None and bbox_intersection(band["bbox"], palette_bbox) > bbox_area(band["bbox"]) * 0.65 and len(actor_bands) > 1:
            continue
        filtered_actor_bands.append(band)

    for index, band in enumerate(filtered_actor_bands):
        frame_boxes = group_frames_from_components(band["bbox"], components)
        if len(frame_boxes) < 2:
            continue
        envelope = [0, 0, max(box[2] - box[0] for box in frame_boxes), max(box[3] - box[1] for box in frame_boxes)]
        confidence_grouping, confidence_pivot = sequence_confidence(frame_boxes)
        sequences.append(
            {
                "id": f"sequence_{index + 1:02d}",
                "band_bbox": band["bbox"],
                "frame_bboxes": frame_boxes,
                "frame_envelope": envelope,
                "pivot_policy": "lowest_occupied_pixel_y + stable_center_x",
                "confidence_sequence_grouping": confidence_grouping,
                "confidence_pivot": confidence_pivot,
                "review_required": confidence_grouping < 0.75 or confidence_pivot < 0.75,
            }
        )

    if sequences:
        actor_region["confidence_sequence_grouping"] = round(float(np.mean([seq["confidence_sequence_grouping"] for seq in sequences])), 3)
        actor_region["confidence_pivot"] = round(float(np.mean([seq["confidence_pivot"] for seq in sequences])), 3)
        actor_region["review_required"] = actor_region["review_required"] or any(sequence["review_required"] for sequence in sequences)

    return observed_bands, keep, auxiliary, drop, sequences


def detect_tile_object_sheet(
    array: np.ndarray,
    mask: np.ndarray,
    components: list[dict[str, Any]],
    background_color: tuple[int, int, int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    height, width = array.shape[:2]
    bands = find_active_ranges(row_activity(mask), threshold=0.02, min_size=max(12, height // 90), merge_gap=max(8, height // 100))
    if len(bands) >= 3:
        corrupted_zone = [0, bands[0][0], width, bands[0][1]]
        door_zone = [0, bands[1][0], width, bands[1][1]]
        tile_zone = [0, bands[2][0], width, bands[-1][1]]
    else:
        corrupted_zone = [0, 0, width, int(height * 0.39)]
        door_zone = [0, int(height * 0.39), width, int(height * 0.68)]
        tile_zone = [0, int(height * 0.68), width, height]
    observed_components = [
        compute_region_signature(array, mask, components, corrupted_zone, background_color, bands),
        compute_region_signature(array, mask, components, door_zone, background_color, bands),
        compute_region_signature(array, mask, components, tile_zone, background_color, bands),
    ]

    keep: list[dict[str, Any]] = []
    auxiliary: list[dict[str, Any]] = []
    drop: list[dict[str, Any]] = []
    sequences: list[dict[str, Any]] = []

    drop.append(add_confidence(with_defaults("corrupted_top_region", "corrupted_region", corrupted_zone, observed_components[0]), 0.92, 0.92, 0.98, 0.98))

    door_components = [
        component
        for component in components_in_zone(components, door_zone, min_overlap_ratio=0.6)
        if bbox_height(component["bbox"]) >= max(18, int(bbox_height(door_zone) * 0.45))
        and bbox_width(component["bbox"]) >= max(18, int(width * 0.05))
    ]
    if door_components:
        door_bbox = union_bboxes([component["bbox"] for component in door_components])
        signature = compute_region_signature(array, mask, components, door_bbox, background_color, bands)
        keep.append(add_confidence(with_defaults("door_sequence", "object_animation_sequence", door_bbox, signature), 0.9, 0.88, 0.1, 0.9))
        frame_boxes = [component["bbox"] for component in sorted(door_components, key=lambda item: item["bbox"][0])]
        confidence_grouping, confidence_pivot = sequence_confidence(frame_boxes)
        sequences.append(
            {
                "id": "object_sequence_01",
                "band_bbox": door_bbox,
                "frame_bboxes": frame_boxes,
                "frame_envelope": [0, 0, max((box[2] - box[0]) for box in frame_boxes) if frame_boxes else 0, max((box[3] - box[1]) for box in frame_boxes) if frame_boxes else 0],
                "pivot_policy": "center_lower_edge",
                "confidence_sequence_grouping": confidence_grouping,
                "confidence_pivot": confidence_pivot,
                "review_required": confidence_grouping < 0.75 or confidence_pivot < 0.75,
            }
        )

    tile_components = [
        component
        for component in components_in_zone(components, tile_zone, min_overlap_ratio=0.65)
        if bbox_height(component["bbox"]) >= max(18, int(bbox_height(tile_zone) * 0.35))
        and bbox_width(component["bbox"]) >= max(18, int(width * 0.05))
    ]
    if tile_components:
        base_boxes: list[list[int]] = []
        overlay_boxes: list[list[int]] = []
        for component in tile_components:
            damage_score = black_ratio(extract_crop(array, component["bbox"]))
            if damage_score > 0.08:
                overlay_bbox = isolate_dark_overlay_bbox(array, component["bbox"], threshold=48, padding=2)
                if overlay_bbox is not None:
                    overlay_boxes.append(overlay_bbox)
            if damage_score <= 0.14:
                base_boxes.append(component["bbox"])
        if not base_boxes and tile_components:
            least_damaged = min(tile_components, key=lambda item: black_ratio(extract_crop(array, item["bbox"])))
            base_boxes.append(least_damaged["bbox"])

        if base_boxes:
            bbox = union_bboxes(base_boxes)
            signature = compute_region_signature(array, mask, components, bbox, background_color, bands)
            keep.append(add_confidence(with_defaults("wall_base_tiles", "tile_cluster", bbox, signature), 0.9, 0.86, 0.1, 0.88))
        if overlay_boxes:
            bbox = union_bboxes(overlay_boxes)
            signature = compute_region_signature(array, mask, components, bbox, background_color, bands)
            keep.append(add_confidence(with_defaults("damage_overlay_tiles", "overlay_cluster", bbox, signature), 0.88, 0.86, 0.1, 0.92))

    return observed_components, keep, auxiliary, drop, sequences


def derive_structure(
    array: np.ndarray,
    mask: np.ndarray,
    background_color: tuple[int, int, int],
    layout_type: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    components = connected_components(mask, min_area=max(24, (array.shape[0] * array.shape[1]) // 30000))
    if layout_type == "sprite_sheet":
        return detect_sprite_sheet(array, mask, components, background_color)
    if layout_type == "tile_object_sheet":
        return detect_tile_object_sheet(array, mask, components, background_color)
    if layout_type == "editorial_board":
        return detect_editorial_board(array, mask, components, background_color)
    return detect_stage_board(array, mask, components, background_color)


def validate_region_contracts(regions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for region in regions:
        if region.get("action") == "drop":
            continue
        defaults = CLASS_TO_REGION_DEFAULTS.get(region["classification"])
        if defaults is None:
            continue
        checks = {
            "system_role": defaults["system_role"],
            "candidate_asset_kind": defaults["candidate_asset_kind"],
            "engine_affordance": defaults["engine_affordance"],
        }
        for field_name, expected in checks.items():
            if region.get(field_name) != expected:
                conflicts.append(
                    {
                        "type": "region_contract_conflict",
                        "region_id": region["id"],
                        "severity": "error",
                        "message": f"{field_name} incoerente para {region['classification']}: esperado {expected}, atual {region.get(field_name)}",
                        "blocks_final_export": True,
                        "allows_provisional_export": True,
                    }
                )
    return conflicts


def validate_engine_affordance(regions: list[dict[str, Any]], layout_type: str) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    for region in regions:
        if region.get("action") != "keep":
            continue
        signature = region.get("observed_signature", {})
        classification = region.get("classification")
        black = float(signature.get("pixel_signature", {}).get("black_ratio", 0.0))
        repeat = float(signature.get("repeat_pattern_score", 0.0))
        text_like = float(signature.get("text_like_score", 0.0))
        component_count = int(signature.get("component_count", 0))

        if classification in {"scene_plane_sky", "scene_plane_bg_b", "scene_plane_architecture", "scene_plane_bg_a", "scene_plane_ground"}:
            if repeat > 0.45 and component_count >= 8:
                conflicts.append(
                    {
                        "type": "scene_layer_actor_contamination",
                        "region_id": region["id"],
                        "severity": "error",
                        "message": f"{region['id']} parece contaminada por strip repetida de actor",
                        "blocks_final_export": True,
                        "allows_provisional_export": True,
                    }
                )
            if text_like > 0.38:
                conflicts.append(
                    {
                        "type": "scene_layer_text_contamination",
                        "region_id": region["id"],
                        "severity": "warning",
                        "message": f"{region['id']} parece conter ruido textual/editorial",
                        "blocks_final_export": False,
                        "allows_provisional_export": True,
                    }
                )

        if classification == "tile_cluster" and black > 0.2:
            conflicts.append(
                {
                    "type": "tile_base_too_damaged",
                    "region_id": region["id"],
                    "severity": "warning",
                    "message": "tile base tem dano/oclusao demais para ser tratado como base reutilizavel",
                    "blocks_final_export": False,
                    "allows_provisional_export": True,
                }
            )

        if classification == "overlay_cluster" and black < 0.05:
            conflicts.append(
                {
                    "type": "overlay_without_damage_signal",
                    "region_id": region["id"],
                    "severity": "warning",
                    "message": "overlay nao mostra sinal visual forte de dependencia da base",
                    "blocks_final_export": False,
                    "allows_provisional_export": True,
                }
            )

        if classification == "object_animation_sequence" and component_count < 2:
            conflicts.append(
                {
                    "type": "object_sequence_without_progression",
                    "region_id": region["id"],
                    "severity": "error",
                    "message": "sequencia de objeto sem frames suficientes para progressao de estado",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )

    if layout_type == "tile_object_sheet":
        keep_classes = {region["classification"] for region in regions if region.get("action") == "keep"}
        if "tile_cluster" not in keep_classes or "overlay_cluster" not in keep_classes:
            conflicts.append(
                {
                    "type": "missing_tile_overlay_split",
                    "severity": "error",
                    "message": "tile/object sheet sem separacao confiavel entre base e overlay",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )

    return conflicts


def validate_inter_region_conflicts(regions: list[dict[str, Any]], layout_type: str) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    keep_regions = [region for region in regions if region["action"] == "keep"]
    drop_regions = [region for region in regions if region["action"] == "drop"]

    roles_seen: dict[str, str] = {}
    for region in keep_regions:
        role = region.get("compositional_role")
        if role and role in roles_seen:
            if role == "scene_plane_bg_a":
                same_role_regions = [item for item in keep_regions if item.get("compositional_role") == role]
                same_role_classes = {item.get("classification") for item in same_role_regions}
                if same_role_classes.issubset({"scene_plane_architecture", "scene_plane_bg_a", "scene_plane_ground"}):
                    continue
            conflicts.append(
                {
                    "type": "duplicate_compositional_role",
                    "region_id": region["id"],
                    "severity": "error",
                    "message": f"mais de uma regiao tenta ocupar {role}",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )
        elif role:
            roles_seen[role] = region["id"]

    for keep_region in keep_regions:
        for drop_region in drop_regions:
            overlap = bbox_iou(keep_region["bbox"], drop_region["bbox"])
            if overlap > 0.2:
                conflicts.append(
                    {
                        "type": "keep_drop_overlap",
                        "region_id": keep_region["id"],
                        "related_region_id": drop_region["id"],
                        "severity": "warning" if overlap < 0.45 else "error",
                        "message": f"regiao util sobrepoe ruido editorial ({drop_region['id']})",
                        "blocks_final_export": overlap >= 0.45,
                        "allows_provisional_export": True,
                    }
                )

    if layout_type in {"stage_board", "editorial_board"}:
        roles = {region.get("compositional_role") for region in keep_regions if region.get("system_role") == "scene_layer"}
        classes = {region.get("classification") for region in keep_regions if region.get("system_role") == "scene_layer"}
        required = {"scene_plane_bg_b", "scene_plane_bg_a"}
        if not required.issubset(roles):
            missing = sorted(required - roles)
            conflicts.append(
                {
                    "type": "missing_scene_roles",
                    "severity": "error",
                    "message": f"faltam papeis estruturais obrigatorios: {', '.join(missing)}",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )
        if layout_type == "stage_board" and "scene_plane_ground" not in classes:
            conflicts.append(
                {
                    "type": "missing_ground_layer",
                    "severity": "error",
                    "message": "stage board sem layer explicita de ground/perspective",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )

    if layout_type == "editorial_board":
        roles = {region.get("compositional_role") for region in keep_regions if region.get("system_role") == "scene_layer"}
        if "scene_plane_foreground_composition" not in roles and "scene_plane_bg_a" not in roles:
            conflicts.append(
                {
                    "type": "missing_editorial_composition_roles",
                    "severity": "error",
                    "message": "editorial board sem plano principal suficiente para recomposicao",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )

    if layout_type == "tile_object_sheet":
        base_region = next((region for region in keep_regions if region["classification"] == "tile_cluster"), None)
        overlay_region = next((region for region in keep_regions if region["classification"] == "overlay_cluster"), None)
        if base_region and overlay_region and bbox_area(overlay_region["bbox"]) > (bbox_area(base_region["bbox"]) * 1.4):
            conflicts.append(
                {
                    "type": "overlay_dominates_base",
                    "region_id": overlay_region["id"],
                    "related_region_id": base_region["id"],
                    "severity": "warning",
                    "message": "overlay maior do que a base; pode indicar classificacao estrutural errada",
                    "blocks_final_export": False,
                    "allows_provisional_export": True,
                }
            )

        object_region = next((region for region in keep_regions if region["classification"] == "object_animation_sequence"), None)
        if object_region and base_region and bbox_iou(object_region["bbox"], base_region["bbox"]) > 0.2:
            conflicts.append(
                {
                    "type": "object_tile_overlap_conflict",
                    "region_id": object_region["id"],
                    "related_region_id": base_region["id"],
                    "severity": "warning",
                    "message": "sequencia de objeto invade a base modular de tiles",
                    "blocks_final_export": False,
                    "allows_provisional_export": True,
                }
            )

    return conflicts


def validate_sequence_coverage(layout_type: str, regions: list[dict[str, Any]], sequences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    conflicts: list[dict[str, Any]] = []
    if layout_type == "sprite_sheet":
        actor_region = next((region for region in regions if region.get("classification") == "actor_sprite_sheet" and region.get("action") == "keep"), None)
        if actor_region and not sequences:
            conflicts.append(
                {
                    "type": "missing_animation_sequences",
                    "region_id": actor_region["id"],
                    "severity": "error",
                    "message": "sprite sheet sem bandas/frames suficientes para export final",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )
    if layout_type == "tile_object_sheet":
        object_region = next((region for region in regions if region.get("classification") == "object_animation_sequence" and region.get("action") == "keep"), None)
        if object_region and not sequences:
            conflicts.append(
                {
                    "type": "missing_object_sequence_frames",
                    "region_id": object_region["id"],
                    "severity": "error",
                    "message": "object sequence detectada sem frames derivados",
                    "blocks_final_export": True,
                    "allows_provisional_export": True,
                }
            )
    return conflicts


def assemble_observed_ir(source_path: Path, array: np.ndarray, mask: np.ndarray, background_color: tuple[int, int, int]) -> dict[str, Any]:
    height, width = array.shape[:2]
    components = connected_components(mask, min_area=max(24, (height * width) // 30000))
    bands = find_active_ranges(row_activity(mask), threshold=0.02, min_size=max(8, height // 80), merge_gap=max(4, height // 100))
    observed_regions = []
    for index, component in enumerate(components[:128]):
        observed_regions.append({"id": f"component_{index + 1:03d}", **compute_region_signature(array, mask, components, component["bbox"], background_color, bands)})

    for index, region in enumerate(observed_regions):
        region["neighbor_relations"] = [
            {"region_id": other["id"], "distance_x": abs(region["bbox"][0] - other["bbox"][0]), "distance_y": abs(region["bbox"][1] - other["bbox"][1])}
            for other in observed_regions
            if other["id"] != region["id"]
            and abs(region["bbox"][1] - other["bbox"][1]) < max(region["bbox"][3] - region["bbox"][1], other["bbox"][3] - other["bbox"][1])
        ][:8]
        region["overlap_relations"] = [
            {"region_id": other["id"], "iou": round(bbox_iou(region["bbox"], other["bbox"]), 3)}
            for other in observed_regions
            if other["id"] != region["id"] and bbox_iou(region["bbox"], other["bbox"]) > 0.0
        ][:8]

    return {
        "source_image": str(source_path),
        "source_size": {"width": width, "height": height},
        "background_key_color": list(background_color),
        "row_bands": [{"id": f"band_{index + 1:02d}", "range": [start, end]} for index, (start, end) in enumerate(bands)],
        "regions": observed_regions,
    }


def build_inference(source_path: Path, layout_hint: str) -> tuple[dict[str, Any], dict[str, Any]]:
    with Image.open(source_path) as image:
        rgba = image.convert("RGBA")
    array = np.array(rgba)
    background_color = dominant_border_color(array)
    mask = build_color_mask(array, background_color, threshold=26)
    layout_type = infer_layout_type(array, background_color, mask, layout_hint)

    observed_ir = assemble_observed_ir(source_path, array, mask, background_color)
    observed_regions, keep_regions, auxiliary_regions, drop_regions, sequences = derive_structure(array, mask, background_color, layout_type)
    regions = keep_regions + auxiliary_regions + drop_regions

    conflicts = validate_region_contracts(regions)
    conflicts.extend(validate_engine_affordance(regions, layout_type))
    conflicts.extend(validate_inter_region_conflicts(regions, layout_type))
    conflicts.extend(validate_sequence_coverage(layout_type, regions, sequences))

    derived_regions = [strip_region_to_derived(region) for region in regions]

    derived_ir = {
        "source_image": str(source_path),
        "source_size": {"width": array.shape[1], "height": array.shape[0]},
        "layout_type": layout_type,
        "background_key_color": list(background_color),
        "shared_canvas": {"width": array.shape[1], "height": array.shape[0], "space": "source_canvas"} if layout_type in {"stage_board", "editorial_board"} else None,
        "regions": derived_regions,
        "sequences": sequences,
        "conflicts": conflicts,
        "export_mode": "pending_validation",
        "review_required": any(region["review_required"] for region in derived_regions if region.get("action") != "drop")
        or any(sequence.get("review_required") for sequence in sequences)
        or any(conflict["blocks_final_export"] for conflict in conflicts),
        "blocked_reasons": [conflict["message"] for conflict in conflicts if conflict["blocks_final_export"]],
    }
    return observed_ir, derived_ir


def main() -> int:
    parser = argparse.ArgumentParser(description="Infere IR estrutural minima de um source.")
    parser.add_argument("--source", required=True, help="Imagem-fonte a ser analisada.")
    parser.add_argument("--output-dir", required=True, help="Diretorio de saida.")
    parser.add_argument("--layout-hint", default="auto", help="auto|stage_board|sprite_sheet|tile_object_sheet|editorial_board")
    parser.add_argument("--case-id", default=None, help="ID opcional do caso.")
    args = parser.parse_args()

    if args.layout_hint not in LAYOUT_HINTS:
        print(f"Erro: layout-hint invalido: {args.layout_hint}", file=sys.stderr)
        return 1

    source_path = Path(args.source).resolve()
    if not source_path.is_file():
        print(f"Erro: source nao encontrado: {source_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    observed_ir, derived_ir = build_inference(source_path, args.layout_hint)
    case_id = args.case_id or safe_slug(source_path.stem)
    observed_ir["case_id"] = case_id
    derived_ir["case_id"] = case_id

    save_json(output_dir / "observed_ir.json", observed_ir)
    save_json(output_dir / "derived_structure_ir.json", derived_ir)

    print(json.dumps({"case_id": case_id, "layout_type": derived_ir["layout_type"], "regions": len(derived_ir["regions"]), "conflicts": len(derived_ir["conflicts"]), "review_required": derived_ir["review_required"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
