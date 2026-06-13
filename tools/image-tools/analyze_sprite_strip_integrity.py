#!/usr/bin/env python3
"""Audit sprite strips before SGDK promotion.

This tool is intentionally conservative. It does not fix art. It reports the
conditions that usually become VDP waste, clipping, bad pivots, or visible
matte artifacts once a generated strip reaches res/.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, deque
from pathlib import Path
from typing import Any

from PIL import Image


BLOCKING_CODES = {
    "FRAME_EMPTY",
    "FRAME_EDGE_CLIPPING",
    "NON_INDEX0_BACKGROUND_MATTE",
    "SMALL_ISLAND_DEBRIS",
    "STRAY_LARGE_COMPONENT",
    "TRANSPARENCY_INDEX0_BACKGROUND_MISMATCH",
    "SCALE_INCONSISTENCY",
    "BAKED_FX_IN_CHARACTER_SHEET",
}

STATE_PROFILE_SCALE_LIMITS = {
    "standing": 1.35,
    "dash": 1.55,
    "hop": 1.65,
    "crouch": 1.70,
    "grounded": 3.80,
    "knockdown": 5.00,
    "getup": 5.00,
    "throw": 3.20,
    "fx": 4.00,
}


def color_to_list(color: tuple[int, ...]) -> list[int]:
    return [int(v) for v in color]


def add_finding(findings: list[dict[str, Any]], code: str, severity: str, message: str, frame: int | None = None, **extra: Any) -> None:
    item: dict[str, Any] = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    if frame is not None:
        item["frame"] = frame
    item.update(extra)
    findings.append(item)


def get_palette_color(image: Image.Image, index: int) -> tuple[int, int, int, int] | None:
    if image.mode != "P":
        return None
    palette = image.getpalette()
    if not palette or index < 0:
        return None
    base = index * 3
    if base + 2 >= len(palette):
        return None
    transparency = image.info.get("transparency")
    alpha = 0 if transparency == index else 255
    return (palette[base], palette[base + 1], palette[base + 2], alpha)


def mask_components(mask: list[list[bool]], min_island_area: int) -> dict[str, Any]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    visited = [[False] * width for _ in range(height)]
    areas: list[int] = []
    boxes: list[tuple[int, int, int, int]] = []

    for y in range(height):
        for x in range(width):
            if visited[y][x] or not mask[y][x]:
                continue
            q: deque[tuple[int, int]] = deque([(x, y)])
            visited[y][x] = True
            area = 0
            min_x = max_x = x
            min_y = max_y = y
            while q:
                cx, cy = q.popleft()
                area += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx] and mask[ny][nx]:
                        visited[ny][nx] = True
                        q.append((nx, ny))
            areas.append(area)
            boxes.append((min_x, min_y, max_x, max_y))

    if not areas:
        return {
            "component_count": 0,
            "small_island_count": 0,
            "small_island_pixels": 0,
            "external_small_island_count": 0,
            "external_small_island_pixels": 0,
            "largest_component_area": 0,
            "non_largest_component_pixels": 0,
            "external_non_largest_component_pixels": 0,
            "largest_stray_component_area": 0,
            "largest_stray_component_box": None,
            "largest_external_stray_component_area": 0,
            "largest_external_stray_component_box": None,
            "component_boxes": [],
        }

    ordered = sorted(zip(areas, boxes), reverse=True)
    largest_area = ordered[0][0]
    largest_box = ordered[0][1]
    non_largest = ordered[1:]
    small = [a for a, _ in non_largest if a < min_island_area]
    pad = 8
    lx0, ly0, lx1, ly1 = largest_box

    def is_external(box: tuple[int, int, int, int]) -> bool:
        x0, y0, x1, y1 = box
        inside_expanded = x0 >= lx0 - pad and y0 >= ly0 - pad and x1 <= lx1 + pad and y1 <= ly1 + pad
        if inside_expanded:
            return False
        dx = max(lx0 - x1, x0 - lx1, 0)
        dy = max(ly0 - y1, y0 - ly1, 0)
        return max(dx, dy) > pad

    external = [(a, b) for a, b in non_largest if is_external(b)]
    external_small = [a for a, _ in external if a < min_island_area]
    return {
        "component_count": len(areas),
        "small_island_count": len(small),
        "small_island_pixels": sum(small),
        "external_small_island_count": len(external_small),
        "external_small_island_pixels": sum(external_small),
        "largest_component_area": largest_area,
        "non_largest_component_pixels": int(sum(area for area, _ in non_largest)),
        "external_non_largest_component_pixels": int(sum(area for area, _ in external)),
        "largest_stray_component_area": int(non_largest[0][0]) if non_largest else 0,
        "largest_stray_component_box": list(non_largest[0][1]) if non_largest else None,
        "largest_external_stray_component_area": int(external[0][0]) if external else 0,
        "largest_external_stray_component_box": list(external[0][1]) if external else None,
        "component_boxes": [
            {"area": int(area), "bbox": list(box)}
            for area, box in ordered[:12]
        ],
    }


def is_fx_yellow_or_orange(color: tuple[int, int, int, int]) -> bool:
    r, g, b, a = color
    if a == 0:
        return False
    mx = max(r, g, b)
    mn = min(r, g, b)
    if mx < 140 or mx - mn < 70:
        return False
    return r >= 180 and g >= 120 and b <= 120


def declared_fx_indices(args: argparse.Namespace) -> set[int] | None:
    if not getattr(args, "palette_domain_report", ""):
        return None
    report_path = Path(args.palette_domain_report)
    if not report_path.is_file():
        return None
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))
    asset_kind = getattr(args, "asset_kind", "")
    palette_domain = getattr(args, "palette_domain", "")
    asset_id = getattr(args, "asset_id", "")
    if asset_kind == "fx":
        domain = report.get("fx", {})
        indices: set[int] = set()
        for values in domain.values():
            if isinstance(values, list):
                indices.update(int(i) for i in values)
        return indices
    if palette_domain:
        domain = report.get("characters", {}).get(palette_domain, {})
        if domain:
            return {int(i) for i in domain.get("fx", [])}
        return set()
    character = ""
    if asset_id.startswith("spr_marina_"):
        character = "marina"
    elif asset_id.startswith("spr_bento_"):
        character = "bento"
    if character:
        domain = report.get("characters", {}).get(character, {})
        return {int(i) for i in domain.get("fx", [])}
    if asset_id.startswith("spr_hit_spark") or asset_id.startswith("spr_dust"):
        domain = report.get("fx", {})
        indices: set[int] = set()
        for values in domain.values():
            if isinstance(values, list):
                indices.update(int(i) for i in values)
        return indices
    return None


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    image_path = Path(args.image)
    original = Image.open(image_path)
    rgba = original.convert("RGBA")
    width, height = rgba.size
    frame_width = args.frame_width
    frame_height = args.frame_height or height
    if frame_width <= 0:
        raise ValueError("--frame-width must be > 0")
    if frame_height <= 0:
        raise ValueError("--frame-height must be > 0")

    frame_count = width // frame_width
    findings: list[dict[str, Any]] = []
    if width % frame_width != 0:
        add_finding(findings, "STRIP_WIDTH_NOT_DIVISIBLE", "error", f"Image width {width} is not divisible by frame width {frame_width}.")
    if height != frame_height:
        add_finding(findings, "FRAME_HEIGHT_MISMATCH", "warning", f"Image height {height} differs from declared frame height {frame_height}.")

    corner_rgba = [
        rgba.getpixel((0, 0)),
        rgba.getpixel((width - 1, 0)),
        rgba.getpixel((0, height - 1)),
        rgba.getpixel((width - 1, height - 1)),
    ]
    bg_rgba = Counter(corner_rgba).most_common(1)[0][0]
    bg_index = None
    if original.mode == "P":
        bg_index = int(original.getpixel((0, 0)))
        if bg_index != 0:
            add_finding(
                findings,
                "TRANSPARENCY_INDEX0_BACKGROUND_MISMATCH",
                "error",
                f"Corner background uses palette index {bg_index}; SGDK sprite transparency must use index 0.",
            )
        index0 = get_palette_color(original, 0)
        if index0 and index0[:3] != bg_rgba[:3]:
            add_finding(
                findings,
                "TRANSPARENCY_INDEX0_COLOR_MISMATCH",
                "warning",
                "Palette index 0 color does not match the dominant corner background color.",
                index0=color_to_list(index0),
                background=color_to_list(bg_rgba),
            )

    frames: list[dict[str, Any]] = []
    bbox_widths: list[int] = []
    bbox_heights: list[int] = []
    matte_frames = 0
    edge_problem_frames = 0
    island_problem_frames = 0
    baked_fx_frames = 0
    edge_margin = args.edge_margin
    fx_indices = declared_fx_indices(args)

    for frame_idx in range(frame_count):
        left = frame_idx * frame_width
        crop = rgba.crop((left, 0, left + frame_width, frame_height))
        indexed_crop = None
        if original.mode == "P":
            indexed_crop = original.crop((left, 0, left + frame_width, frame_height))
        pixels = crop.load()
        index_pixels = indexed_crop.load() if indexed_crop is not None else None
        xs: list[int] = []
        ys: list[int] = []
        colors: Counter[tuple[int, int, int, int]] = Counter()
        mask = [[False] * frame_width for _ in range(frame_height)]

        for y in range(frame_height):
            for x in range(frame_width):
                c = pixels[x, y]
                if c != bg_rgba:
                    xs.append(x)
                    ys.append(y)
                    colors[c] += 1
                    mask[y][x] = True

        frame_number = frame_idx + 1
        if not xs:
            add_finding(findings, "FRAME_EMPTY", "error", "Frame has no visible pixels.", frame=frame_number)
            frames.append({"frame": frame_number, "non_background_pixels": 0, "bbox": None})
            continue

        bbox = (min(xs), min(ys), max(xs), max(ys))
        bbox_w = bbox[2] - bbox[0] + 1
        bbox_h = bbox[3] - bbox[1] + 1
        bbox_widths.append(bbox_w)
        bbox_heights.append(bbox_h)

        edge_counts = {
            "left": sum(1 for y in range(frame_height) for x in range(edge_margin) if pixels[x, y] != bg_rgba),
            "right": sum(1 for y in range(frame_height) for x in range(frame_width - edge_margin, frame_width) if pixels[x, y] != bg_rgba),
            "top": sum(1 for y in range(edge_margin) for x in range(frame_width) if pixels[x, y] != bg_rgba),
            "bottom": sum(1 for y in range(frame_height - edge_margin, frame_height) for x in range(frame_width) if pixels[x, y] != bg_rgba),
        }
        touching_edges = []
        if bbox[0] == 0:
            touching_edges.append("left")
        if bbox[2] == frame_width - 1:
            touching_edges.append("right")
        if bbox[1] == 0:
            touching_edges.append("top")
        if bbox[3] == frame_height - 1:
            touching_edges.append("bottom")
        if touching_edges:
            edge_problem_frames += 1
            add_finding(
                findings,
                "FRAME_EDGE_CLIPPING",
                "error",
                "Visible pixels touch the frame boundary; enlarge or recut the cell before SGDK promotion.",
                frame=frame_number,
                edges=touching_edges,
                bbox=list(bbox),
            )

        component_report = mask_components(mask, args.min_island_area)
        if component_report["external_small_island_count"] >= args.max_small_islands or component_report["external_small_island_pixels"] >= args.max_small_island_pixels:
            island_problem_frames += 1
            add_finding(
                findings,
                "SMALL_ISLAND_DEBRIS",
                "warning",
                "Frame contains many small disconnected islands; likely AI/background cleanup debris or stray cell fragments.",
                frame=frame_number,
                small_island_count=component_report["external_small_island_count"],
                small_island_pixels=component_report["external_small_island_pixels"],
                total_small_island_count=component_report["small_island_count"],
                total_small_island_pixels=component_report["small_island_pixels"],
            )
        total_stray_pixels = int(component_report["non_largest_component_pixels"])
        total_largest_stray = int(component_report["largest_stray_component_area"])
        external_stray_pixels = int(component_report["external_non_largest_component_pixels"])
        external_largest_stray = int(component_report["largest_external_stray_component_area"])
        use_total_large_component = total_largest_stray >= args.max_stray_component_pixels
        stray_pixels = total_stray_pixels if use_total_large_component else external_stray_pixels
        largest_stray = total_largest_stray if use_total_large_component else external_largest_stray
        stray_box = component_report["largest_stray_component_box"] if use_total_large_component else component_report["largest_external_stray_component_box"]
        stray_ratio = stray_pixels / max(1, len(xs))
        if use_total_large_component or stray_ratio >= args.max_stray_component_ratio:
            island_problem_frames += 1
            add_finding(
                findings,
                "STRAY_LARGE_COMPONENT",
                "error",
                "Frame contains significant disconnected mass outside the main body; likely sliced from a neighboring pose or cleanup artifact.",
                frame=frame_number,
                non_largest_component_pixels=stray_pixels,
                largest_stray_component_area=largest_stray,
                largest_stray_component_box=stray_box,
                total_non_largest_component_pixels=component_report["non_largest_component_pixels"],
                total_largest_stray_component_area=component_report["largest_stray_component_area"],
                total_largest_stray_component_box=component_report["largest_stray_component_box"],
                external_non_largest_component_pixels=component_report["external_non_largest_component_pixels"],
                external_largest_stray_component_area=component_report["largest_external_stray_component_area"],
                detection_basis="total_large_component" if use_total_large_component else "external_component_ratio",
                stray_ratio=stray_ratio,
            )

        large_color_findings = []
        frame_area = frame_width * frame_height
        for color, count in colors.most_common(8):
            ratio = count / frame_area
            if ratio < args.large_color_ratio:
                continue
            color_positions = [(x, y) for y in range(frame_height) for x in range(frame_width) if pixels[x, y] == color]
            min_x = min(p[0] for p in color_positions)
            max_x = max(p[0] for p in color_positions)
            min_y = min(p[1] for p in color_positions)
            max_y = max(p[1] for p in color_positions)
            color_bbox_w = max_x - min_x + 1
            color_bbox_h = max_y - min_y + 1
            touches_outer = min_x == 0 or min_y == 0 or max_x == frame_width - 1 or max_y == frame_height - 1
            if touches_outer or color_bbox_h >= frame_height * 0.70 or color_bbox_w >= frame_width * 0.70:
                large_color_findings.append(
                    {
                        "rgba": color_to_list(color),
                        "palette_index": int(index_pixels[color_positions[0][0], color_positions[0][1]]) if index_pixels is not None else None,
                        "pixels": int(count),
                        "coverage": ratio,
                        "bbox": [min_x, min_y, max_x, max_y],
                    }
                )
        if large_color_findings:
            matte_frames += 1
            add_finding(
                findings,
                "NON_INDEX0_BACKGROUND_MATTE",
                "error",
                "Large non-transparent flat color behaves like a baked background matte inside the frame.",
                frame=frame_number,
                colors=large_color_findings,
            )

        if fx_indices is not None and index_pixels is not None:
            fx_pixels = sum(
                1
                for y in range(frame_height)
                for x in range(frame_width)
                if pixels[x, y] != bg_rgba and int(index_pixels[x, y]) in fx_indices
            )
        else:
            fx_pixels = sum(count for color, count in colors.items() if is_fx_yellow_or_orange(color))
        if args.detect_baked_fx and getattr(args, "asset_kind", "character_animation_strip") == "character_animation_strip" and fx_pixels >= args.fx_pixel_threshold:
            baked_fx_frames += 1
            add_finding(
                findings,
                "BAKED_FX_IN_CHARACTER_SHEET",
                "error",
                "Possible hit/impact FX colors are baked into a character frame; export FX as a separate sprite.",
                frame=frame_number,
                fx_pixels=int(fx_pixels),
            )

        frames.append(
            {
                "frame": frame_number,
                "non_background_pixels": len(xs),
                "bbox": list(bbox),
                "bbox_size": [bbox_w, bbox_h],
                "edge_counts": edge_counts,
                "touching_edges": touching_edges,
                "component_report": component_report,
            }
        )

    if bbox_heights:
        median_h = sorted(bbox_heights)[len(bbox_heights) // 2]
        min_h = min(bbox_heights)
        max_h = max(bbox_heights)
        ratio = max_h / max(1, min_h)
        max_scale_ratio = args.max_scale_ratio
        if max_scale_ratio is None:
            max_scale_ratio = STATE_PROFILE_SCALE_LIMITS.get(args.state_profile, STATE_PROFILE_SCALE_LIMITS["standing"])
        if ratio > max_scale_ratio:
            add_finding(
                findings,
                "SCALE_INCONSISTENCY",
                "error",
                "Frame bounding-box height varies beyond tolerance; check character scale and pose extraction.",
                min_height=min_h,
                max_height=max_h,
                ratio=ratio,
                max_allowed=max_scale_ratio,
                state_profile=args.state_profile,
            )
        if args.reference_bbox_height:
            ref_ratio = median_h / args.reference_bbox_height
            if ref_ratio < args.min_reference_scale or ref_ratio > args.max_reference_scale:
                add_finding(
                    findings,
                    "SCALE_INCONSISTENCY",
                    "error",
                    "Median bbox height differs from reference action scale.",
                    median_height=median_h,
                    reference_height=args.reference_bbox_height,
                    ratio=ref_ratio,
                )

    severities = {item["severity"] for item in findings}
    if any(item["code"] in BLOCKING_CODES for item in findings) or "error" in severities:
        status = "rework"
    elif findings:
        status = "needs_review"
    else:
        status = "passed"

    report = {
        "schema": "sprite_strip_integrity_report.v1",
        "tool": "analyze_sprite_strip_integrity.py",
        "image_path": str(image_path),
        "mode": original.mode,
        "size": [width, height],
        "frame_width": frame_width,
        "frame_height": frame_height,
        "frame_count": frame_count,
        "background_rgba": color_to_list(bg_rgba),
        "background_palette_index": bg_index,
        "asset_id": args.asset_id,
        "asset_kind": args.asset_kind,
        "state_profile": args.state_profile,
        "palette_domain": args.palette_domain,
        "palette_domain_report": args.palette_domain_report,
        "declared_fx_indices": sorted(fx_indices) if fx_indices is not None else None,
        "measurement_level": "measured",
        "scale_profile_thresholds": STATE_PROFILE_SCALE_LIMITS,
        "status": status,
        "summary": {
            "edge_problem_frames": edge_problem_frames,
            "matte_problem_frames": matte_frames,
            "island_problem_frames": island_problem_frames,
            "baked_fx_frames": baked_fx_frames,
            "bbox_width_min": min(bbox_widths) if bbox_widths else 0,
            "bbox_width_max": max(bbox_widths) if bbox_widths else 0,
            "bbox_height_min": min(bbox_heights) if bbox_heights else 0,
            "bbox_height_max": max(bbox_heights) if bbox_heights else 0,
        },
        "findings": findings,
        "frames": frames,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--frame-width", type=int, required=True)
    parser.add_argument("--frame-height", type=int, default=0)
    parser.add_argument("--output", default="")
    parser.add_argument("--edge-margin", type=int, default=4)
    parser.add_argument("--min-island-area", type=int, default=16)
    parser.add_argument("--max-small-islands", type=int, default=8)
    parser.add_argument("--max-small-island-pixels", type=int, default=64)
    parser.add_argument("--max-stray-component-pixels", type=int, default=96)
    parser.add_argument("--max-stray-component-ratio", type=float, default=0.015)
    parser.add_argument("--large-color-ratio", type=float, default=0.20)
    parser.add_argument("--max-scale-ratio", type=float, default=None)
    parser.add_argument("--reference-bbox-height", type=float, default=0.0)
    parser.add_argument("--min-reference-scale", type=float, default=0.88)
    parser.add_argument("--max-reference-scale", type=float, default=1.12)
    parser.add_argument("--detect-baked-fx", action="store_true")
    parser.add_argument("--fx-pixel-threshold", type=int, default=20)
    parser.add_argument("--palette-domain-report", default="")
    parser.add_argument("--palette-domain", default="")
    parser.add_argument("--asset-kind", default="character_animation_strip")
    parser.add_argument("--state-profile", default="standing")
    parser.add_argument("--asset-id", default="")
    args = parser.parse_args()

    report = analyze(args)
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
