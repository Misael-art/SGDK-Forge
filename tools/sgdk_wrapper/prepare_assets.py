#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import warnings
from collections import Counter, deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageSequence, ImageStat

warnings.filterwarnings("ignore", category=DeprecationWarning)


SCRIPT_VERSION = "2026-03-21-v4"
FRAME_COUNT = 4
SPRITE_BLOCK_SIZE = 8
SPRITE_CONFIDENCE_THRESHOLD = 0.55
BACKGROUND_CONFIDENCE_THRESHOLD = 0.55
BACKGROUND_TARGET_SIZE = (320, 224)
IMAGE_SUFFIXES = {".png", ".gif", ".bmp", ".jpg", ".jpeg", ".webp"}
PREPARATION_LOG_NAME = "asset_preparation.log"
STOPWORDS = {
    "spr",
    "sprite",
    "sprites",
    "bg",
    "bgs",
    "image",
    "images",
    "sheet",
    "sheets",
    "normal",
    "large",
    "small",
    "grande",
    "pequeno",
    "background",
    "backgrounds",
    "stage",
    "idle",
    "char",
    "character",
    "characters",
    "frame",
    "frames",
}


@dataclass
class ResourceSpec:
    kind: str
    name: str
    rel_path: str
    abs_path: Path
    source_res: Path
    line_number: int
    target_width: int | None = None
    target_height: int | None = None


@dataclass
class SourceFile:
    path: Path
    stem: str
    tokens: set[str]
    width: int
    height: int
    mode: str
    frame_count: int
    sha256: str


@dataclass
class PreparedAsset:
    resource_name: str
    kind: str
    source_file: str
    output_file: str
    cache_key: str
    cache_hit: bool
    confidence: float
    status: str
    details: dict[str, object] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare SGDK assets from raw data/")
    parser.add_argument("--project", required=True, help="Project root directory")
    parser.add_argument(
        "--report",
        help="Override report path (defaults to out/logs/asset_preparation_report.json)",
    )
    parser.add_argument(
        "--preview",
        help="Override preview path (defaults to out/logs/asset_preparation_preview.png)",
    )
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_word(token: str) -> str:
    token = token.lower()
    if token.endswith("ies") and len(token) > 4:
        token = token[:-3] + "y"
    elif token.endswith("s") and len(token) > 4:
        token = token[:-1]
    return token


def tokenize(text: str) -> set[str]:
    expanded = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    tokens = set()
    for raw_token in re.split(r"[^A-Za-z0-9]+", expanded):
        token = normalize_word(raw_token)
        if len(token) < 2 or token in STOPWORDS:
            continue
        tokens.add(token)
    return tokens


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def console_rule(title: str, log_lines: list[str]) -> None:
    line = "=" * 78
    print(line)
    print(f"[PREP] {title}")
    print(line)
    log_lines.extend([line, f"[PREP] {title}", line])


def log_event(log_lines: list[str], tag: str, message: str) -> None:
    line = f"[{tag:<8}] {message}"
    print(line)
    log_lines.append(line)


def round_up_to_multiple(value: int, multiple: int = SPRITE_BLOCK_SIZE, maximum: int | None = None) -> int:
    value = max(multiple, int(math.ceil(value / multiple) * multiple))
    if maximum is not None:
        value = min(maximum, value)
    return value


def parse_resources(project_dir: Path) -> list[ResourceSpec]:
    resources: list[ResourceSpec] = []
    res_root = project_dir / "res"
    for res_file in sorted(res_root.rglob("*.res")):
        lines = res_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            image_match = re.match(r'^IMAGE\s+(\w+)\s+"([^"]+)"', stripped)
            if image_match:
                rel_path = image_match.group(2).replace("\\", "/")
                resources.append(
                    ResourceSpec(
                        kind="IMAGE",
                        name=image_match.group(1),
                        rel_path=rel_path,
                        abs_path=(res_file.parent / rel_path).resolve(),
                        source_res=res_file,
                        line_number=line_number,
                    )
                )
                continue

            sprite_match = re.match(r'^SPRITE\s+(\w+)\s+"([^"]+)"\s+(\d+)\s+(\d+)', stripped)
            if sprite_match:
                rel_path = sprite_match.group(2).replace("\\", "/")
                resources.append(
                    ResourceSpec(
                        kind="SPRITE",
                        name=sprite_match.group(1),
                        rel_path=rel_path,
                        abs_path=(res_file.parent / rel_path).resolve(),
                        source_res=res_file,
                        line_number=line_number,
                        target_width=int(sprite_match.group(3)) * 8,
                        target_height=int(sprite_match.group(4)) * 8,
                    )
                )
    return resources


def collect_data_files(data_dir: Path) -> list[SourceFile]:
    files: list[SourceFile] = []
    for path in sorted(data_dir.glob("*")):
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        with Image.open(path) as image:
            files.append(
                SourceFile(
                    path=path,
                    stem=path.stem,
                    tokens=tokenize(path.stem),
                    width=image.width,
                    height=image.height,
                    mode=image.mode,
                    frame_count=getattr(image, "n_frames", 1),
                    sha256=sha256_file(path),
                )
            )
    return files


def collect_recursive_data_files(data_dir: Path, exclude_dir: Path | None = None) -> list[SourceFile]:
    files: list[SourceFile] = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        if exclude_dir is not None:
            try:
                path.relative_to(exclude_dir)
                continue
            except ValueError:
                pass
        with Image.open(path) as image:
            files.append(
                SourceFile(
                    path=path,
                    stem=path.stem,
                    tokens=tokenize(path.stem),
                    width=image.width,
                    height=image.height,
                    mode=image.mode,
                    frame_count=getattr(image, "n_frames", 1),
                    sha256=sha256_file(path),
                )
            )
    return files


def has_transparency(image: Image.Image) -> bool:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    alpha_min, alpha_max = alpha.getextrema()
    return alpha_min < 255 or alpha_max < 255


def inspect_sgdk_image_support(path: Path) -> tuple[bool, list[str], dict[str, object]]:
    with Image.open(path) as image:
        frame = image.copy()
        width, height = frame.size
        reasons = []
        if (width % SPRITE_BLOCK_SIZE) != 0 or (height % SPRITE_BLOCK_SIZE) != 0:
            reasons.append(f"alignment {width}x{height}")

        if frame.mode != "P":
            reasons.append(f"mode {frame.mode}")
            colors = None
        else:
            colors = frame.getcolors(maxcolors=257)
            color_count = len(colors) if colors is not None else 257
            if color_count > 16:
                reasons.append(f"{color_count} colors")

        if colors is None and frame.mode == "P":
            color_count = 257
        elif colors is None:
            rgba_colors = frame.convert("RGBA").getcolors(maxcolors=257)
            color_count = len(rgba_colors) if rgba_colors is not None else 257
            if color_count > 16:
                reasons.append(f"{color_count} colors")
        else:
            color_count = len(colors)

        details = {
            "mode": frame.mode,
            "size": [width, height],
            "color_count": color_count,
        }
        return len(reasons) == 0, reasons, details


def score_source_match(resource: ResourceSpec, source: SourceFile) -> tuple[float, dict[str, float]]:
    resource_tokens = tokenize(resource.name) | tokenize(resource.rel_path)
    source_tokens = source.tokens
    if not resource_tokens or not source_tokens:
        return 0.0, {"coverage": 0.0, "jaccard": 0.0, "substring": 0.0, "type_hint": 0.0}

    coverage_hits = 0
    substring_hits = 0
    for resource_token in resource_tokens:
        if resource_token in source_tokens:
            coverage_hits += 1
            substring_hits += 1
            continue
        if any(resource_token in source_token or source_token in resource_token for source_token in source_tokens):
            coverage_hits += 1
            substring_hits += 1

    intersection = len(resource_tokens & source_tokens)
    union = len(resource_tokens | source_tokens)
    coverage = coverage_hits / max(len(resource_tokens), 1)
    jaccard = intersection / max(union, 1)
    substring = substring_hits / max(len(resource_tokens), 1)
    source_compact = re.sub(r"[^a-z0-9]", "", source.path.stem.lower())
    compact_bonus = 0.0
    for resource_token in resource_tokens:
        if resource_token in source_compact:
            compact_bonus = 0.15
            break

    type_hint = 0.0
    source_name = source.path.name.lower()
    if resource.kind == "IMAGE":
        if any(token in source_name for token in ("bg", "background", "stage", "scene")):
            type_hint += 0.20
        if source.width >= BACKGROUND_TARGET_SIZE[0] and source.height >= BACKGROUND_TARGET_SIZE[1]:
            type_hint += 0.10
    else:
        if source.frame_count > 1:
            type_hint += 0.10
        if source.height > (resource.target_height or 0) or source.width > (resource.target_width or 0):
            type_hint += 0.10

    score = min(1.0, coverage * 0.40 + jaccard * 0.20 + substring * 0.20 + compact_bonus + type_hint)
    return score, {
        "coverage": round(coverage, 4),
        "jaccard": round(jaccard, 4),
        "substring": round(substring, 4),
        "compact_bonus": round(compact_bonus, 4),
        "type_hint": round(type_hint, 4),
    }


def assign_sources(resources: list[ResourceSpec], sources: list[SourceFile]) -> tuple[dict[str, SourceFile], dict[str, dict[str, object]]]:
    assignments: dict[str, SourceFile] = {}
    diagnostics: dict[str, dict[str, object]] = {}
    unused = set(source.path for source in sources)
    source_lookup = {source.path: source for source in sources}

    candidates = []
    for resource in resources:
        resource_candidates = []
        for source in sources:
            score, parts = score_source_match(resource, source)
            resource_candidates.append((score, source.path, parts))
            candidates.append((score, resource.name, source.path))
        resource_candidates.sort(key=lambda item: item[0], reverse=True)
        diagnostics[resource.name] = {
            "candidates": [
                {
                    "source": str(path),
                    "score": round(score, 4),
                    "parts": parts,
                }
                for score, path, parts in resource_candidates[:3]
            ]
        }

    for _, resource_name, source_path in sorted(candidates, key=lambda item: item[0], reverse=True):
        if resource_name in assignments or source_path not in unused:
            continue
        assignments[resource_name] = source_lookup[source_path]
        unused.remove(source_path)

    return assignments, diagnostics


def edge_pixels(image: Image.Image) -> Iterable[tuple[int, int, int, int]]:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    stride = max(1, max(width, height) // 1024)
    for x in range(0, width, stride):
        yield pixels[x, 0]
        yield pixels[x, height - 1]
    for y in range(0, height, stride):
        yield pixels[0, y]
        yield pixels[width - 1, y]


def infer_transparency_strategy(image: Image.Image) -> tuple[str, tuple[int, int, int] | None, float, dict[str, object]]:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    alpha_min, _ = alpha.getextrema()
    if alpha_min < 255:
        edge_values = [pixel[3] for pixel in edge_pixels(rgba)]
        transparent_edges = sum(1 for alpha_value in edge_values if alpha_value == 0)
        edge_ratio = transparent_edges / max(len(edge_values), 1)
        if edge_ratio >= 0.10 or alpha.getbbox() != (0, 0, rgba.width, rgba.height):
            return "alpha", None, 0.98, {"edge_alpha_ratio": round(edge_ratio, 4)}

    bucket_counts: Counter[tuple[int, int, int]] = Counter()
    exact_counts: Counter[tuple[int, int, int]] = Counter()
    for red, green, blue, alpha_value in edge_pixels(rgba):
        if alpha_value == 0:
            continue
        bucket = (red >> 4, green >> 4, blue >> 4)
        bucket_counts[bucket] += 1
        exact_counts[(red, green, blue)] += 1

    if not bucket_counts:
        return "none", None, 0.0, {"reason": "no opaque edge pixels"}

    dominant_bucket, dominant_bucket_count = bucket_counts.most_common(1)[0]
    bucket_ratio = dominant_bucket_count / max(sum(bucket_counts.values()), 1)
    dominant_exact = max(
        (
            item
            for item in exact_counts.items()
            if (item[0][0] >> 4, item[0][1] >> 4, item[0][2] >> 4) == dominant_bucket
        ),
        key=lambda item: item[1],
    )[0]
    confidence = max(0.20, min(0.92, bucket_ratio))
    return "border_color", dominant_exact, confidence, {
        "bucket_ratio": round(bucket_ratio, 4),
        "color": list(dominant_exact),
    }


def build_foreground_mask(image: Image.Image, strategy: str, background_color: tuple[int, int, int] | None) -> Image.Image:
    rgba = image.convert("RGBA")
    if strategy == "alpha":
        alpha = rgba.getchannel("A")
        return alpha.point(lambda alpha_value: 255 if alpha_value > 0 else 0)

    if strategy != "border_color" or background_color is None:
        raise ValueError("Cannot build a foreground mask without a background color or alpha")

    bg_bucket = (background_color[0] >> 4, background_color[1] >> 4, background_color[2] >> 4)
    bucket_tolerance = 0 if max(background_color) <= 24 else 1
    threshold_sq = 42 * 42 * 3
    data = bytearray()
    for red, green, blue, alpha_value in rgba.getdata():
        if alpha_value == 0:
            data.append(0)
            continue
        pixel_bucket = (red >> 4, green >> 4, blue >> 4)
        if (
            abs(pixel_bucket[0] - bg_bucket[0]) <= bucket_tolerance and
            abs(pixel_bucket[1] - bg_bucket[1]) <= bucket_tolerance and
            abs(pixel_bucket[2] - bg_bucket[2]) <= bucket_tolerance
        ):
            data.append(0)
            continue
        distance_sq = (
            (red - background_color[0]) ** 2
            + (green - background_color[1]) ** 2
            + (blue - background_color[2]) ** 2
        )
        data.append(255 if distance_sq > threshold_sq else 0)
    return Image.frombytes("L", rgba.size, bytes(data))


def build_occupancy_grid(mask: Image.Image, block_size: int = SPRITE_BLOCK_SIZE) -> tuple[int, int, list[int]]:
    grid_width = math.ceil(mask.width / block_size)
    grid_height = math.ceil(mask.height / block_size)
    reduced = mask.resize((grid_width, grid_height), Image.Resampling.BOX)
    values = list(reduced.getdata())
    threshold = 8
    return grid_width, grid_height, [1 if value > threshold else 0 for value in values]


def mask_to_components(mask: Image.Image, block_size: int = SPRITE_BLOCK_SIZE) -> list[dict[str, object]]:
    grid_width, grid_height, values = build_occupancy_grid(mask, block_size)
    visited = [False] * len(values)
    components: list[dict[str, object]] = []

    def index_for(x_value: int, y_value: int) -> int:
        return y_value * grid_width + x_value

    for y_value in range(grid_height):
        for x_value in range(grid_width):
            index = index_for(x_value, y_value)
            if visited[index] or values[index] <= 0:
                continue

            queue = deque([(x_value, y_value)])
            visited[index] = True
            min_x = max_x = x_value
            min_y = max_y = y_value
            area = 0

            while queue:
                current_x, current_y = queue.popleft()
                area += 1
                min_x = min(min_x, current_x)
                max_x = max(max_x, current_x)
                min_y = min(min_y, current_y)
                max_y = max(max_y, current_y)

                for delta_x, delta_y in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    next_x = current_x + delta_x
                    next_y = current_y + delta_y
                    if not (0 <= next_x < grid_width and 0 <= next_y < grid_height):
                        continue
                    neighbor_index = index_for(next_x, next_y)
                    if visited[neighbor_index] or values[neighbor_index] <= 0:
                        continue
                    visited[neighbor_index] = True
                    queue.append((next_x, next_y))

            components.append(
                {
                    "bbox": (
                        min_x * block_size,
                        min_y * block_size,
                        min(mask.width, (max_x + 1) * block_size),
                        min(mask.height, (max_y + 1) * block_size),
                    ),
                    "area_blocks": area,
                }
            )
    return components


def bbox_iou(box_a: tuple[int, int, int, int], box_b: tuple[int, int, int, int]) -> float:
    left = max(box_a[0], box_b[0])
    top = max(box_a[1], box_b[1])
    right = min(box_a[2], box_b[2])
    bottom = min(box_a[3], box_b[3])
    if left >= right or top >= bottom:
        return 0.0
    intersection = (right - left) * (bottom - top)
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - intersection
    return intersection / max(union, 1)


def refine_bbox(mask: Image.Image, bbox: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    crop = mask.crop(bbox)
    inner = crop.getbbox()
    if inner is None:
        return bbox
    left, top, right, bottom = inner
    return (bbox[0] + left, bbox[1] + top, bbox[0] + right, bbox[1] + bottom)


def select_windows_from_grid(
    mask: Image.Image,
    target_size: tuple[int, int],
    block_size: int = SPRITE_BLOCK_SIZE,
) -> list[dict[str, object]]:
    grid_width, grid_height, values = build_occupancy_grid(mask, block_size)
    window_width = min(grid_width, max(1, math.ceil(target_size[0] / block_size)))
    window_height = min(grid_height, max(1, math.ceil(target_size[1] / block_size)))
    step = max(1, min(window_width, window_height) // 3)

    prefix = [[0] * (grid_width + 1) for _ in range(grid_height + 1)]
    for y_value in range(grid_height):
        row_total = 0
        for x_value in range(grid_width):
            row_total += values[y_value * grid_width + x_value]
            prefix[y_value + 1][x_value + 1] = prefix[y_value][x_value + 1] + row_total

    def window_sum(left: int, top: int) -> int:
        right = left + window_width
        bottom = top + window_height
        return prefix[bottom][right] - prefix[top][right] - prefix[bottom][left] + prefix[top][left]

    candidates = []
    min_fill = max(4, int(window_width * window_height * 0.08))
    for top in range(0, max(1, grid_height - window_height + 1), step):
        for left in range(0, max(1, grid_width - window_width + 1), step):
            fill = window_sum(left, top)
            if fill < min_fill:
                continue
            bbox = (
                left * block_size,
                top * block_size,
                min(mask.width, (left + window_width) * block_size),
                min(mask.height, (top + window_height) * block_size),
            )
            refined = refine_bbox(mask, bbox)
            candidates.append(
                {
                    "bbox": refined,
                    "score": fill / max(window_width * window_height, 1),
                    "area_blocks": fill,
                }
            )

    candidates.sort(key=lambda candidate: (-candidate["score"], candidate["bbox"][1], candidate["bbox"][0]))
    chosen = []
    for candidate in candidates:
        if any(bbox_iou(candidate["bbox"], existing["bbox"]) > 0.45 for existing in chosen):
            continue
        chosen.append(candidate)
        if len(chosen) >= FRAME_COUNT:
            break
    chosen.sort(key=lambda candidate: (candidate["bbox"][1], candidate["bbox"][0]))
    return chosen


def fit_crop_to_cell(
    rgba_crop: Image.Image,
    alpha_crop: Image.Image,
    target_size: tuple[int, int],
) -> tuple[Image.Image, dict[str, object]]:
    target_width, target_height = target_size
    max_width = max(1, target_width - 8)
    max_height = max(1, target_height - 8)
    scale = min(max_width / rgba_crop.width, max_height / rgba_crop.height, 1.0)
    if scale < 1.0:
        resized_size = (
            max(1, int(round(rgba_crop.width * scale))),
            max(1, int(round(rgba_crop.height * scale))),
        )
        rgba_crop = rgba_crop.resize(resized_size, Image.Resampling.LANCZOS)
        alpha_crop = alpha_crop.resize(resized_size, Image.Resampling.LANCZOS)

    cell = Image.new("RGBA", target_size, (0, 0, 0, 0))
    paste_x = max(0, (target_width - rgba_crop.width) // 2)
    paste_y = max(0, target_height - rgba_crop.height)
    cell.paste(rgba_crop, (paste_x, paste_y), alpha_crop)
    return cell, {
        "scaled_size": [rgba_crop.width, rgba_crop.height],
        "paste": [paste_x, paste_y],
        "scale": round(scale, 4),
    }


def pad_image_to_block(image: Image.Image, fill: tuple[int, ...]) -> Image.Image:
    width = round_up_to_multiple(image.width)
    height = round_up_to_multiple(image.height)
    if (width, height) == image.size:
        return image
    padded = Image.new(image.mode, (width, height), fill)
    if image.mode == "RGBA":
        padded.paste(image, (0, 0), image)
    else:
        padded.paste(image, (0, 0))
    return padded


def quantize_rgb_for_sgdk(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    padded = pad_image_to_block(rgb, (0, 0, 0))
    return padded.quantize(colors=16, dither=Image.Dither.NONE)


def infer_target_size_from_regions(regions: list[dict[str, object]] | list[tuple[int, int, int, int]]) -> tuple[int, int]:
    widths = []
    heights = []
    for region in regions:
        bbox = region["bbox"] if isinstance(region, dict) else region
        widths.append(max(1, bbox[2] - bbox[0]))
        heights.append(max(1, bbox[3] - bbox[1]))
    if not widths or not heights:
        return (64, 64)
    return (
        round_up_to_multiple(max(widths) + SPRITE_BLOCK_SIZE, maximum=128),
        round_up_to_multiple(max(heights) + SPRITE_BLOCK_SIZE, maximum=128),
    )


def quantize_rgba_for_sgdk(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    has_transparency = alpha.getextrema()[0] < 255

    rgb = Image.new("RGB", rgba.size, (0, 0, 0))
    rgb.paste(rgba, mask=alpha)
    color_budget = 15 if has_transparency else 16
    quantized = rgb.quantize(colors=color_budget, dither=Image.Dither.NONE)

    if not has_transparency:
        return quantized

    palette = quantized.getpalette()[: color_budget * 3]
    shifted_palette = [255, 0, 255] + palette
    shifted_palette.extend([0] * (768 - len(shifted_palette)))

    indexed = Image.new("P", rgba.size, 0)
    output = bytearray(len(alpha.getdata()))
    quantized_data = list(quantized.getdata())
    alpha_data = list(alpha.getdata())
    for index, palette_index in enumerate(quantized_data):
        output[index] = 0 if alpha_data[index] == 0 else min(255, palette_index + 1)
    indexed.putdata(output)
    indexed.putpalette(shifted_palette)
    indexed.info["transparency"] = 0
    return indexed


def build_generic_resource(output_path: Path, kind: str, target_size: tuple[int, int] | None = None) -> ResourceSpec:
    return ResourceSpec(
        kind=kind,
        name=output_path.stem,
        rel_path=output_path.name,
        abs_path=output_path,
        source_res=output_path.parent,
        line_number=0,
        target_width=target_size[0] if target_size else None,
        target_height=target_size[1] if target_size else None,
    )


def classify_generic_asset(source: SourceFile, relative_path: Path) -> str:
    rel_text = str(relative_path).replace("\\", "/").lower()
    sprite_hint = any(token in rel_text for token in ("sprite", "sprites", "char", "character", "fighter", "enemy", "player", "boss"))
    background_hint = any(token in rel_text for token in ("bg/", "bgs/", "background", "stage", "scene"))

    with Image.open(source.path) as image:
        transparency = has_transparency(image)

    if background_hint:
        return "BACKGROUND"
    if source.frame_count > 1:
        return "SPRITE"
    if sprite_hint:
        return "SPRITE"
    if transparency:
        return "SPRITE"
    if source.width >= BACKGROUND_TARGET_SIZE[0] and source.height >= BACKGROUND_TARGET_SIZE[1]:
        return "BACKGROUND"
    return "IMAGE"


def make_backup_path(output_path: Path, backup_root: Path, res_root: Path) -> Path:
    relative = output_path.relative_to(res_root)
    backup_dir = backup_root / relative.parent
    ensure_directory(backup_dir)
    candidate = backup_dir / f"{output_path.stem}_old{output_path.suffix.lower()}"
    index = 2
    while candidate.exists():
        candidate = backup_dir / f"{output_path.stem}_old_{index}{output_path.suffix.lower()}"
        index += 1
    return candidate


def backup_file(output_path: Path, backup_root: Path, res_root: Path) -> Path | None:
    if not output_path.exists():
        return None
    backup_path = make_backup_path(output_path, backup_root, res_root)
    ensure_directory(backup_path.parent)
    output_path.replace(backup_path)
    return backup_path


def sanitize_final_image(
    source_path: Path,
    output_path: Path,
    asset_kind: str,
) -> PreparedAsset:
    with Image.open(source_path) as image:
        first_frame = next(ImageSequence.Iterator(image)).convert("RGBA") if getattr(image, "n_frames", 1) > 1 else image.convert("RGBA")

        if asset_kind == "SPRITE":
            strategy, background_color, confidence, background_meta = infer_transparency_strategy(first_frame)
            if strategy == "none":
                alpha = first_frame.getchannel("A")
                transparent = Image.new("RGBA", first_frame.size, (0, 0, 0, 0))
                transparent.paste(first_frame, mask=alpha)
                background_meta = {"fallback": "alpha_only"}
                confidence = 0.55
            else:
                alpha = build_foreground_mask(first_frame, strategy, background_color)
                transparent = Image.new("RGBA", first_frame.size, (0, 0, 0, 0))
                transparent.paste(first_frame, mask=alpha)
            padded = pad_image_to_block(transparent, (0, 0, 0, 0))
            final_image = quantize_rgba_for_sgdk(padded)
            details = {
                "mode": "sanitize",
                "asset_kind": asset_kind,
                "background_strategy": strategy,
                "background_color": list(background_color) if background_color else None,
                "background_meta": background_meta,
            }
        else:
            flattened = Image.new("RGB", first_frame.size, (0, 0, 0))
            if has_transparency(first_frame):
                flattened.paste(first_frame, mask=first_frame.getchannel("A"))
            else:
                flattened.paste(first_frame)
            final_image = quantize_rgb_for_sgdk(flattened)
            confidence = 0.80
            details = {
                "mode": "sanitize",
                "asset_kind": asset_kind,
            }

    ensure_directory(output_path.parent)
    final_image.save(output_path)
    return PreparedAsset(
        resource_name=output_path.stem,
        kind=asset_kind,
        source_file=str(source_path),
        output_file=str(output_path),
        cache_key="",
        cache_hit=False,
        confidence=round(confidence, 4),
        status="prepared",
        details=details,
    )


def prepare_sprite_sheet(
    source: SourceFile,
    output_path: Path,
    resource: ResourceSpec,
    mapping_confidence: float,
) -> PreparedAsset:
    target_size = None
    if resource.target_width is not None and resource.target_height is not None:
        target_size = (resource.target_width, resource.target_height)
    with Image.open(source.path) as image:
        rgba = image.convert("RGBA")
        strategy, background_color, background_confidence, background_meta = infer_transparency_strategy(rgba)
        if strategy == "none":
            return PreparedAsset(
                resource_name=resource.name,
                kind=resource.kind,
                source_file=str(source.path),
                output_file=str(output_path),
                cache_key="",
                cache_hit=False,
                confidence=0.0,
                status="failed",
                details={"reason": "no transparency strategy available"},
            )

        mask = build_foreground_mask(rgba, strategy, background_color)
        if mask.getbbox() is None:
            return PreparedAsset(
                resource_name=resource.name,
                kind=resource.kind,
                source_file=str(source.path),
                output_file=str(output_path),
                cache_key="",
                cache_hit=False,
                confidence=0.0,
                status="failed",
                details={"reason": "no visible foreground pixels detected"},
            )

        components = mask_to_components(mask)
        if not components:
            return PreparedAsset(
                resource_name=resource.name,
                kind=resource.kind,
                source_file=str(source.path),
                output_file=str(output_path),
                cache_key="",
                cache_hit=False,
                confidence=0.0,
                status="failed",
                details={"reason": "no connected components detected"},
            )

        max_component_area = max(component["area_blocks"] for component in components)
        min_component_area = max(4, int(max_component_area * 0.25))
        if target_size is not None:
            min_component_area = max(
                min_component_area,
                int((target_size[0] * target_size[1]) / (SPRITE_BLOCK_SIZE * SPRITE_BLOCK_SIZE) * 0.05),
            )
        filtered = [
            {
                **component,
                "bbox": refine_bbox(mask, component["bbox"]),
            }
            for component in components
            if component["area_blocks"] >= min_component_area
        ]
        filtered.sort(key=lambda component: (component["bbox"][1], component["bbox"][0]))

        selected: list[dict[str, object]] = []
        for component in filtered:
            if any(bbox_iou(component["bbox"], chosen["bbox"]) > 0.65 for chosen in selected):
                continue
            selected.append(component)
            if len(selected) == FRAME_COUNT:
                break

        if len(selected) < FRAME_COUNT:
            fallback_target = target_size or infer_target_size_from_regions(filtered or components)
            selected = select_windows_from_grid(mask, fallback_target)

        if len(selected) < FRAME_COUNT:
            return PreparedAsset(
                resource_name=resource.name,
                kind=resource.kind,
                source_file=str(source.path),
                output_file=str(output_path),
                cache_key="",
                cache_hit=False,
                confidence=0.0,
                status="failed",
                details={
                    "reason": f"expected {FRAME_COUNT} frames but found {len(selected)}",
                    "component_count": len(components),
                    "filtered_count": len(filtered),
                },
            )

        final_target_size = target_size or infer_target_size_from_regions(selected)
        cells = []
        frame_regions = []
        areas = []
        for component in selected:
            left, top, right, bottom = component["bbox"]
            rgba_crop = rgba.crop((left, top, right, bottom))
            local_strategy, local_bg_color, _, _ = infer_transparency_strategy(rgba_crop)
            if local_strategy == "none":
                alpha_crop = mask.crop((left, top, right, bottom))
            else:
                alpha_crop = build_foreground_mask(rgba_crop, local_strategy, local_bg_color)
            transparent_crop = Image.new("RGBA", rgba_crop.size, (0, 0, 0, 0))
            transparent_crop.paste(rgba_crop, mask=alpha_crop)
            cell, placement = fit_crop_to_cell(transparent_crop, alpha_crop, final_target_size)
            cells.append(cell)
            bbox_area = (right - left) * (bottom - top)
            areas.append(bbox_area)
            frame_regions.append(
                {
                    "bbox": [left, top, right, bottom],
                    "area_blocks": component["area_blocks"],
                    "placement": placement,
                }
            )

        strip = Image.new("RGBA", (final_target_size[0] * FRAME_COUNT, final_target_size[1]), (0, 0, 0, 0))
        for index, cell in enumerate(cells):
            strip.paste(cell, (index * final_target_size[0], 0), cell)

        indexed_strip = quantize_rgba_for_sgdk(strip)
        ensure_directory(output_path.parent)
        indexed_strip.save(output_path)

        area_mean = sum(areas) / max(len(areas), 1)
        area_variance = sum((area - area_mean) ** 2 for area in areas) / max(len(areas), 1)
        area_consistency = 1.0 - min(1.0, math.sqrt(area_variance) / max(area_mean, 1.0))
        detection_confidence = min(1.0, max(len(filtered), len(selected)) / FRAME_COUNT) * max(0.20, area_consistency)
        confidence = min(
            1.0,
            mapping_confidence * 0.35 + background_confidence * 0.25 + detection_confidence * 0.40,
        )
        status = "prepared" if confidence >= SPRITE_CONFIDENCE_THRESHOLD else "failed"

        return PreparedAsset(
            resource_name=resource.name,
            kind=resource.kind,
            source_file=str(source.path),
            output_file=str(output_path),
            cache_key="",
            cache_hit=False,
            confidence=round(confidence, 4),
            status=status,
            details={
                "target_size": list(final_target_size),
                "target_inferred": target_size is None,
                "background_strategy": strategy,
                "background_color": list(background_color) if background_color else None,
                "background_meta": background_meta,
                "component_count": len(components),
                "filtered_count": len(filtered),
                "frame_regions": frame_regions,
            },
        )


def dedupe_gif_frames(frames: list[Image.Image]) -> list[Image.Image]:
    seen_hashes: set[str] = set()
    unique_frames: list[Image.Image] = []
    for frame in frames:
        digest = hashlib.sha1(frame.tobytes()).hexdigest()
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        unique_frames.append(frame)
        if len(unique_frames) == FRAME_COUNT:
            break
    return unique_frames


def prepare_gif_sprite(
    source: SourceFile,
    output_path: Path,
    resource: ResourceSpec,
    mapping_confidence: float,
) -> PreparedAsset:
    target_size = None
    if resource.target_width is not None and resource.target_height is not None:
        target_size = (resource.target_width, resource.target_height)
    with Image.open(source.path) as image:
        raw_frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(image)]
    frames = dedupe_gif_frames(raw_frames)
    if len(frames) < FRAME_COUNT:
        return prepare_sprite_sheet(source, output_path, resource, mapping_confidence)

    strategy, background_color, background_confidence, background_meta = infer_transparency_strategy(frames[0])
    cells = []
    frame_regions = []
    bbox_samples = []
    for frame in frames[:FRAME_COUNT]:
        mask = build_foreground_mask(frame, strategy, background_color)
        bbox = mask.getbbox()
        if bbox is None:
            return PreparedAsset(
                resource_name=resource.name,
                kind=resource.kind,
                source_file=str(source.path),
                output_file=str(output_path),
                cache_key="",
                cache_hit=False,
                confidence=0.0,
                status="failed",
                details={"reason": "GIF frame without visible foreground"},
            )
        bbox_samples.append(bbox)

    final_target_size = target_size or infer_target_size_from_regions(bbox_samples)
    for frame, bbox in zip(frames[:FRAME_COUNT], bbox_samples):
        frame_mask = build_foreground_mask(frame, strategy, background_color)
        rgba_crop = frame.crop(bbox)
        local_strategy, local_bg_color, _, _ = infer_transparency_strategy(rgba_crop)
        if local_strategy == "none":
            alpha_crop = frame_mask.crop(bbox)
        else:
            alpha_crop = build_foreground_mask(rgba_crop, local_strategy, local_bg_color)
        transparent_crop = Image.new("RGBA", rgba_crop.size, (0, 0, 0, 0))
        transparent_crop.paste(rgba_crop, mask=alpha_crop)
        cell, placement = fit_crop_to_cell(transparent_crop, alpha_crop, final_target_size)
        cells.append(cell)
        frame_regions.append({"bbox": list(bbox), "placement": placement})

    strip = Image.new("RGBA", (final_target_size[0] * FRAME_COUNT, final_target_size[1]), (0, 0, 0, 0))
    for index, cell in enumerate(cells):
        strip.paste(cell, (index * final_target_size[0], 0), cell)

    indexed_strip = quantize_rgba_for_sgdk(strip)
    ensure_directory(output_path.parent)
    indexed_strip.save(output_path)

    confidence = min(1.0, mapping_confidence * 0.45 + background_confidence * 0.25 + 0.30)
    status = "prepared" if confidence >= SPRITE_CONFIDENCE_THRESHOLD else "failed"
    return PreparedAsset(
        resource_name=resource.name,
        kind=resource.kind,
        source_file=str(source.path),
        output_file=str(output_path),
        cache_key="",
        cache_hit=False,
        confidence=round(confidence, 4),
        status=status,
        details={
            "target_size": list(final_target_size),
            "target_inferred": target_size is None,
            "background_strategy": strategy,
            "background_color": list(background_color) if background_color else None,
            "background_meta": background_meta,
            "frame_regions": frame_regions,
        },
    )


def score_background_window(
    gray: Image.Image,
    edge: Image.Image,
    alpha: Image.Image | None,
    box: tuple[int, int, int, int],
) -> float:
    edge_stat = ImageStat.Stat(edge.crop(box))
    gray_stat = ImageStat.Stat(gray.crop(box))
    edge_score = edge_stat.mean[0]
    detail_score = gray_stat.stddev[0]
    transparency_penalty = 0.0
    if alpha is not None:
        alpha_stat = ImageStat.Stat(alpha.crop(box))
        transparency_penalty = max(0.0, 255.0 - alpha_stat.mean[0]) / 2.55
    return edge_score * 1.4 + detail_score - transparency_penalty


def prepare_background(
    source: SourceFile,
    output_path: Path,
    mapping_confidence: float,
    resource: ResourceSpec,
) -> PreparedAsset:
    with Image.open(source.path) as image:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        if width < BACKGROUND_TARGET_SIZE[0] or height < BACKGROUND_TARGET_SIZE[1]:
            return PreparedAsset(
                resource_name=resource.name,
                kind=resource.kind,
                source_file=str(source.path),
                output_file=str(output_path),
                cache_key="",
                cache_hit=False,
                confidence=0.0,
                status="failed",
                details={"reason": "background source smaller than 320x224"},
            )

        scale = min(1.0, 512.0 / max(width, height))
        scaled_size = (
            max(1, int(round(width * scale))),
            max(1, int(round(height * scale))),
        )
        scaled = rgba.resize(scaled_size, Image.Resampling.LANCZOS)
        gray = scaled.convert("L")
        edge = gray.filter(ImageFilter.FIND_EDGES)
        alpha = scaled.getchannel("A") if "A" in scaled.getbands() else None
        target_box = (
            max(1, int(round(BACKGROUND_TARGET_SIZE[0] * scale))),
            max(1, int(round(BACKGROUND_TARGET_SIZE[1] * scale))),
        )
        stride = max(8, min(target_box[0], target_box[1]) // 6)

        best_score = None
        best_box = None
        for top in range(0, scaled.height - target_box[1] + 1, stride):
            for left in range(0, scaled.width - target_box[0] + 1, stride):
                box = (left, top, left + target_box[0], top + target_box[1])
                score = score_background_window(gray, edge, alpha, box)
                if best_score is None or score > best_score:
                    best_score = score
                    best_box = box

        if best_box is None or best_score is None:
            return PreparedAsset(
                resource_name=resource.name,
                kind=resource.kind,
                source_file=str(source.path),
                output_file=str(output_path),
                cache_key="",
                cache_hit=False,
                confidence=0.0,
                status="failed",
                details={"reason": "failed to choose a background crop"},
            )

        left = int(round(best_box[0] / scale))
        top = int(round(best_box[1] / scale))
        crop = rgba.crop((left, top, left + BACKGROUND_TARGET_SIZE[0], top + BACKGROUND_TARGET_SIZE[1]))
        flattened = Image.new("RGB", crop.size, (0, 0, 0))
        flattened.paste(crop, mask=crop.getchannel("A"))
        indexed = flattened.quantize(colors=16, dither=Image.Dither.NONE)

        ensure_directory(output_path.parent)
        indexed.save(output_path)

        confidence = min(1.0, mapping_confidence * 0.50 + 0.30)
        status = "prepared" if confidence >= BACKGROUND_CONFIDENCE_THRESHOLD else "failed"
        return PreparedAsset(
            resource_name=resource.name,
            kind=resource.kind,
            source_file=str(source.path),
            output_file=str(output_path),
            cache_key="",
            cache_hit=False,
            confidence=round(confidence, 4),
            status=status,
            details={
                "crop": [left, top, left + BACKGROUND_TARGET_SIZE[0], top + BACKGROUND_TARGET_SIZE[1]],
                "scaled_search_size": list(scaled_size),
                "search_score": round(best_score, 4),
            },
        )


def process_existing_res_images(
    project_dir: Path,
    raw_data_dir: Path,
    backup_dir: Path,
    log_lines: list[str],
) -> list[PreparedAsset]:
    prepared_assets: list[PreparedAsset] = []
    res_root = project_dir / "res"
    mirrored_rel_paths = set()
    if raw_data_dir.exists():
        for raw_file in raw_data_dir.rglob("*"):
            if not raw_file.is_file():
                continue
            if raw_file.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            try:
                raw_file.relative_to(backup_dir)
                continue
            except ValueError:
                pass
            mirrored_rel_paths.add(raw_file.relative_to(raw_data_dir).as_posix())

    for output_path in sorted(res_root.rglob("*")):
        if not output_path.is_file() or output_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        try:
            output_path.relative_to(raw_data_dir)
            continue
        except ValueError:
            pass

        relative_output = output_path.relative_to(res_root).as_posix()
        if relative_output in mirrored_rel_paths:
            log_event(log_lines, "SKIP", f"saida {relative_output} sera regenerada a partir de res/data")
            continue

        supported, reasons, details = inspect_sgdk_image_support(output_path)
        if supported:
            log_event(log_lines, "OK", f"saida ja compativel com SGDK: {relative_output}")
            continue

        asset_kind = "IMAGE"
        rel_text = relative_output.lower()
        if any(token in rel_text for token in ("sprite", "sprites", "char", "fighter", "enemy", "player", "boss")):
            asset_kind = "SPRITE"

        backup_path = backup_file(output_path, backup_dir, res_root)
        source_for_conversion = backup_path or output_path
        if backup_path is not None:
            log_event(log_lines, "BACKUP", f"{relative_output} -> {backup_path.relative_to(project_dir).as_posix()}")

        prepared = sanitize_final_image(source_for_conversion, output_path, asset_kind)
        prepared.resource_name = relative_output
        prepared.kind = f"RES_{asset_kind}"
        prepared.details["source_mode"] = "res_existing"
        prepared.details["original_issues"] = reasons
        prepared.details["original_info"] = details
        if backup_path is not None:
            prepared.details["backup_path"] = str(backup_path)
        prepared_assets.append(prepared)
        log_event(log_lines, "FIX", f"saida incompativel corrigida em {relative_output}")

    return prepared_assets


def process_res_data_mirror(
    project_dir: Path,
    raw_data_dir: Path,
    backup_dir: Path,
    state_path: Path,
    log_lines: list[str],
) -> tuple[list[PreparedAsset], list[str]]:
    prepared_assets: list[PreparedAsset] = []
    failures: list[str] = []
    if not raw_data_dir.exists():
        return prepared_assets, failures

    previous_state = {}
    if state_path.exists():
        previous_state = json.loads(state_path.read_text(encoding="utf-8", errors="ignore"))

    res_root = project_dir / "res"
    raw_sources = collect_recursive_data_files(raw_data_dir, backup_dir)
    if not raw_sources:
        log_event(log_lines, "SCAN", "nenhum asset bruto encontrado em res/data")
        return prepared_assets, failures

    log_event(log_lines, "SCAN", f"{len(raw_sources)} asset(s) bruto(s) encontrados em res/data")
    for source in raw_sources:
        relative_input = source.path.relative_to(raw_data_dir)
        output_path = res_root / relative_input
        classification = classify_generic_asset(source, relative_input)
        state_key = f"mirror::{relative_input.as_posix()}"
        cache_payload = {
            "script_version": SCRIPT_VERSION,
            "mode": "mirror",
            "relative_input": relative_input.as_posix(),
            "classification": classification,
            "source_hash": source.sha256,
        }
        cache_key = hashlib.sha256(json.dumps(cache_payload, sort_keys=True).encode("utf-8")).hexdigest()
        cached = previous_state.get(state_key, {})
        if cached.get("cache_key") == cache_key and output_path.exists() and cached.get("status") == "prepared":
            prepared_assets.append(
                PreparedAsset(
                    resource_name=relative_input.as_posix(),
                    kind=classification,
                    source_file=str(source.path),
                    output_file=str(output_path),
                    cache_key=cache_key,
                    cache_hit=True,
                    confidence=float(cached.get("confidence", 1.0)),
                    status="prepared",
                    details={**cached.get("details", {}), "state_key": state_key},
                )
            )
            log_event(log_lines, "CACHE", f"{relative_input.as_posix()} reaproveitado sem regeneracao")
            continue

        if output_path.exists():
            backup_path = backup_file(output_path, backup_dir, res_root)
            if backup_path is not None:
                log_event(log_lines, "BACKUP", f"{output_path.relative_to(project_dir).as_posix()} -> {backup_path.relative_to(project_dir).as_posix()}")
        else:
            backup_path = None

        if classification == "SPRITE":
            generic_resource = build_generic_resource(output_path, "SPRITE")
            if source.path.suffix.lower() == ".gif":
                prepared = prepare_gif_sprite(source, output_path, generic_resource, 0.9)
            else:
                prepared = prepare_sprite_sheet(source, output_path, generic_resource, 0.9)
        elif classification == "BACKGROUND":
            generic_resource = build_generic_resource(output_path, "IMAGE")
            prepared = prepare_background(source, output_path, 0.9, generic_resource)
        else:
            prepared = sanitize_final_image(source.path, output_path, "IMAGE")

        prepared.resource_name = relative_input.as_posix()
        prepared.kind = classification
        prepared.cache_key = cache_key
        prepared.details["state_key"] = state_key
        prepared.details["source_mode"] = "res_data_mirror"
        prepared.details["relative_input"] = relative_input.as_posix()
        if backup_path is not None:
            prepared.details["backup_path"] = str(backup_path)
        prepared_assets.append(prepared)

        if prepared.status != "prepared":
            failures.append(relative_input.as_posix())
            log_event(log_lines, "FAIL", f"{relative_input.as_posix()} nao pode ser preparado ({prepared.details.get('reason', 'motivo nao informado')})")
        else:
            log_event(log_lines, "WRITE", f"{relative_input.as_posix()} -> {output_path.relative_to(project_dir).as_posix()} [{classification.lower()}]")

    return prepared_assets, failures


def make_preview(project_dir: Path, prepared_assets: list[PreparedAsset], preview_path: Path) -> None:
    rows = []
    for asset in prepared_assets:
        source_path = Path(asset.source_file)
        output_path = Path(asset.output_file)
        if not source_path.exists() or not output_path.exists():
            continue

        with Image.open(source_path) as source_image:
            source_rgba = source_image.convert("RGBA")
            source_preview = ImageOps.contain(source_rgba, (260, 160))
        canvas_source = Image.new("RGBA", (280, 180), (18, 18, 18, 255))
        source_x = (canvas_source.width - source_preview.width) // 2
        source_y = (canvas_source.height - source_preview.height) // 2
        canvas_source.paste(source_preview, (source_x, source_y), source_preview)
        draw = ImageDraw.Draw(canvas_source)
        if "SPRITE" in asset.kind:
            for region in asset.details.get("frame_regions", []):
                bbox = region.get("bbox")
                if not bbox:
                    continue
                scale_x = source_preview.width / max(source_rgba.width, 1)
                scale_y = source_preview.height / max(source_rgba.height, 1)
                draw.rectangle(
                    (
                        source_x + bbox[0] * scale_x,
                        source_y + bbox[1] * scale_y,
                        source_x + bbox[2] * scale_x,
                        source_y + bbox[3] * scale_y,
                    ),
                    outline=(255, 215, 0, 255),
                    width=2,
                )
        else:
            bbox = asset.details.get("crop")
            if bbox:
                scale_x = source_preview.width / max(source_rgba.width, 1)
                scale_y = source_preview.height / max(source_rgba.height, 1)
                draw.rectangle(
                    (
                        source_x + bbox[0] * scale_x,
                        source_y + bbox[1] * scale_y,
                        source_x + bbox[2] * scale_x,
                        source_y + bbox[3] * scale_y,
                    ),
                    outline=(0, 255, 255, 255),
                    width=2,
                )

        with Image.open(output_path) as output_image:
            output_preview = ImageOps.contain(output_image.convert("RGBA"), (260, 160))
        canvas_output = Image.new("RGBA", (280, 180), (10, 10, 10, 255))
        canvas_output.paste(
            output_preview,
            ((canvas_output.width - output_preview.width) // 2, (canvas_output.height - output_preview.height) // 2),
            output_preview,
        )

        row = Image.new("RGBA", (580, 180), (0, 0, 0, 255))
        row.paste(canvas_source, (0, 0))
        row.paste(canvas_output, (300, 0))
        rows.append(row)

    if not rows:
        return

    preview = Image.new("RGBA", (580, len(rows) * 190 - 10), (0, 0, 0, 255))
    for index, row in enumerate(rows):
        preview.paste(row, (0, index * 190))
    ensure_directory(preview_path.parent)
    preview.save(preview_path)


def build_cache_key(resource: ResourceSpec, source: SourceFile) -> str:
    payload = {
        "script_version": SCRIPT_VERSION,
        "resource": resource.name,
        "kind": resource.kind,
        "target_width": resource.target_width,
        "target_height": resource.target_height,
        "source": str(source.path),
        "source_hash": source.sha256,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def process_legacy_resource_mapping(
    project_dir: Path,
    data_dir: Path,
    state_path: Path,
    log_lines: list[str],
) -> tuple[list[PreparedAsset], list[str], dict[str, dict[str, object]]]:
    resources = parse_resources(project_dir)
    if not resources:
        log_event(log_lines, "WARN", "nenhum recurso .res encontrado para o modo legado")
        return [], [], {}

    sources = collect_data_files(data_dir)
    assignments, diagnostics = assign_sources(resources, sources)
    previous_state = {}
    if state_path.exists():
        previous_state = json.loads(state_path.read_text(encoding="utf-8", errors="ignore"))

    log_event(log_lines, "SCAN", f"modo legado encontrou {len(resources)} recurso(s) e {len(sources)} fonte(s) em data/")
    prepared_assets: list[PreparedAsset] = []
    failures: list[str] = []

    for resource in resources:
        assignment = assignments.get(resource.name)
        diag = diagnostics.get(resource.name, {})
        if assignment is None:
            prepared_assets.append(
                PreparedAsset(
                    resource_name=resource.name,
                    kind=resource.kind,
                    source_file="",
                    output_file=str(resource.abs_path),
                    cache_key="",
                    cache_hit=False,
                    confidence=0.0,
                    status="failed",
                    details={"reason": "no matching source file", "candidates": diag.get("candidates", [])},
                )
            )
            failures.append(resource.name)
            log_event(log_lines, "FAIL", f"modo legado sem fonte compativel para {resource.name}")
            continue

        best_score = diag["candidates"][0]["score"] if diag.get("candidates") else 0.0
        second_score = diag["candidates"][1]["score"] if len(diag.get("candidates", [])) > 1 else 0.0
        mapping_confidence = max(0.0, min(1.0, best_score - max(0.0, second_score * 0.25)))
        if best_score < 0.40 or best_score - second_score < 0.04:
            prepared_assets.append(
                PreparedAsset(
                    resource_name=resource.name,
                    kind=resource.kind,
                    source_file=str(assignment.path),
                    output_file=str(resource.abs_path),
                    cache_key="",
                    cache_hit=False,
                    confidence=round(mapping_confidence, 4),
                    status="failed",
                    details={
                        "reason": "source mapping confidence too low",
                        "candidates": diag.get("candidates", []),
                    },
                )
            )
            failures.append(resource.name)
            log_event(log_lines, "FAIL", f"modo legado com baixa confianca para {resource.name}")
            continue

        cache_key = build_cache_key(resource, assignment)
        cached_entry = previous_state.get(resource.name, {})
        if (
            cached_entry.get("cache_key") == cache_key
            and resource.abs_path.exists()
            and cached_entry.get("status") == "prepared"
        ):
            prepared_assets.append(
                PreparedAsset(
                    resource_name=resource.name,
                    kind=resource.kind,
                    source_file=str(assignment.path),
                    output_file=str(resource.abs_path),
                    cache_key=cache_key,
                    cache_hit=True,
                    confidence=float(cached_entry.get("confidence", 1.0)),
                    status="prepared",
                    details={**cached_entry.get("details", {}), "state_key": resource.name},
                )
            )
            log_event(log_lines, "CACHE", f"modo legado reaproveitou {resource.name}")
            continue

        if assignment.path.suffix.lower() == ".gif":
            prepared = prepare_gif_sprite(assignment, resource.abs_path, resource, mapping_confidence)
        elif resource.kind == "SPRITE":
            prepared = prepare_sprite_sheet(assignment, resource.abs_path, resource, mapping_confidence)
        else:
            prepared = prepare_background(assignment, resource.abs_path, mapping_confidence, resource)

        prepared.cache_key = cache_key
        prepared.details["state_key"] = resource.name
        prepared.details["source_mode"] = "legacy_data"
        prepared_assets.append(prepared)
        if prepared.status != "prepared":
            failures.append(resource.name)
            log_event(log_lines, "FAIL", f"modo legado falhou ao preparar {resource.name}")
        else:
            log_event(log_lines, "WRITE", f"modo legado gerou {resource.rel_path} a partir de data/{assignment.path.name}")

    return prepared_assets, failures, diagnostics


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project).resolve()
    res_root = project_dir / "res"
    raw_data_dir = res_root / "data"
    backup_dir = raw_data_dir / "backup"
    legacy_data_dir = project_dir / "data"
    log_dir = project_dir / "out" / "logs"
    ensure_directory(log_dir)
    ensure_directory(backup_dir)

    report_path = Path(args.report).resolve() if args.report else (log_dir / "asset_preparation_report.json")
    preview_path = Path(args.preview).resolve() if args.preview else (log_dir / "asset_preparation_preview.png")
    state_path = log_dir / "asset_prepare_state.json"
    prep_log_path = log_dir / PREPARATION_LOG_NAME

    prepared_assets: list[PreparedAsset] = []
    failures: list[str] = []
    mapping_diagnostics: dict[str, dict[str, object]] = {}
    log_lines: list[str] = []

    console_rule("SGDK Asset Preparation", log_lines)
    log_event(log_lines, "PROJECT", str(project_dir))
    log_event(log_lines, "MODE", "fase 1: corrigir imagens invalidas ja presentes em res/")
    prepared_assets.extend(process_existing_res_images(project_dir, raw_data_dir, backup_dir, log_lines))

    raw_data_sources = collect_recursive_data_files(raw_data_dir, backup_dir) if raw_data_dir.exists() else []
    if raw_data_sources:
        log_event(log_lines, "MODE", "fase 2: espelhar e converter res/data -> res")
        mirrored_assets, mirrored_failures = process_res_data_mirror(project_dir, raw_data_dir, backup_dir, state_path, log_lines)
        prepared_assets.extend(mirrored_assets)
        failures.extend(mirrored_failures)
    elif legacy_data_dir.exists():
        log_event(log_lines, "MODE", "fase 2: fallback legado usando data/ + resources.res")
        legacy_assets, legacy_failures, mapping_diagnostics = process_legacy_resource_mapping(project_dir, legacy_data_dir, state_path, log_lines)
        prepared_assets.extend(legacy_assets)
        failures.extend(legacy_failures)
    else:
        log_event(log_lines, "WARN", "nenhuma fonte bruta encontrada em res/data nem em data/")

    state_payload = {}
    for asset in prepared_assets:
        state_key = asset.details.get("state_key", asset.resource_name)
        state_payload[state_key] = {
            "cache_key": asset.cache_key,
            "status": asset.status,
            "confidence": asset.confidence,
            "details": asset.details,
        }

    summary = {
        "prepared": sum(1 for asset in prepared_assets if asset.status == "prepared" and not asset.cache_hit),
        "cached": sum(1 for asset in prepared_assets if asset.cache_hit),
        "failed": len(failures),
        "backups": sum(1 for asset in prepared_assets if asset.details.get("backup_path")),
        "total_assets": len(prepared_assets),
    }

    console_rule("Preparation Summary", log_lines)
    log_event(log_lines, "SUMMARY", f"prepared={summary['prepared']} cached={summary['cached']} backups={summary['backups']} failed={summary['failed']}")

    report = {
        "status": "failed" if failures else "ok",
        "script_version": SCRIPT_VERSION,
        "project": str(project_dir),
        "summary": summary,
        "prepared_assets": [asdict(asset) for asset in prepared_assets],
        "failures": failures,
        "mapping_diagnostics": mapping_diagnostics,
        "log_file": str(prep_log_path),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    prep_log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    state_path.write_text(json.dumps(state_payload, indent=2), encoding="utf-8")
    make_preview(project_dir, prepared_assets, preview_path)

    if failures:
        print(f"[prepare_assets] failed to prepare: {', '.join(failures)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
