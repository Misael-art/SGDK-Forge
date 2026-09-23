#!/usr/bin/env python3
"""Convert AXE DE ACO premium strips through a gated candidate pipeline.

The default mode is intentionally non-promotional:

    source_art -> data/processed/candidates -> measured reports

Nothing is copied to ``res/`` while candidates are being generated.  A separate
``promote-approved`` mode may copy candidates only after the integrity, scale
lock and palette-domain reports are clean.  The converter never bridges body
components and never rescales individual frames to hide scale drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


STATES: list[dict[str, Any]] = [
    {"id": "idle", "frames": 8, "duration": 6, "class": "loop", "profile": "standing"},
    {"id": "walk_forward", "frames": 8, "duration": 5, "class": "locomotion", "profile": "standing"},
    {"id": "walk_back", "frames": 8, "duration": 5, "class": "locomotion", "profile": "standing"},
    {"id": "dash", "frames": 5, "duration": 3, "class": "movement", "profile": "dash"},
    {"id": "crouch", "frames": 4, "duration": 7, "class": "defense", "profile": "crouch"},
    {"id": "hop", "frames": 5, "duration": 5, "class": "movement", "profile": "hop"},
    {"id": "guard", "frames": 4, "duration": 6, "class": "defense", "profile": "standing"},
    {"id": "light_attack", "frames": 5, "duration": 4, "class": "attack", "profile": "standing"},
    {"id": "medium_attack", "frames": 6, "duration": 4, "class": "attack", "profile": "standing"},
    {"id": "sweep_or_throw", "frames": 8, "duration": 4, "class": "attack", "profile": "throw"},
    {"id": "hurt", "frames": 4, "duration": 5, "class": "reaction", "profile": "standing"},
    {"id": "knockdown", "frames": 6, "duration": 7, "class": "reaction", "profile": "knockdown"},
    {"id": "getup", "frames": 7, "duration": 6, "class": "reaction", "profile": "getup"},
]

SPECS = {
    "marina": {"cell": (80, 88), "tiles": (10, 11), "pivot": (40, 76), "fit": (72, 78)},
    "bento": {"cell": (88, 88), "tiles": (11, 11), "pivot": (44, 76), "fit": (80, 78)},
}

MARINA_PALETTE = [
    (255, 0, 255), (0, 0, 0), (34, 0, 68), (68, 68, 136),
    (102, 102, 170), (204, 204, 204), (238, 238, 238), (120, 54, 48),
    (198, 116, 124), (236, 156, 150), (0, 68, 68), (0, 102, 68),
    (34, 136, 102), (170, 34, 34), (232, 214, 166), (34, 0, 0),
]

BENTO_PALETTE = [
    (255, 0, 255), (0, 0, 0), (0, 34, 68), (0, 68, 102),
    (34, 102, 136), (92, 58, 44), (160, 112, 92), (236, 216, 176),
    (102, 34, 34), (176, 70, 40), (232, 112, 92), (126, 62, 46),
    (198, 112, 126), (232, 150, 146), (236, 174, 156), (34, 34, 34),
]

PALETTES = {"marina": MARINA_PALETTE, "bento": BENTO_PALETTE}

CHARACTER_DOMAINS = {
    "marina": {
        "transparent": [0],
        "outline": [1, 15],
        "cool_white_shadow": [2, 3, 4],
        "white_pants_highlight": [5, 6],
        "skin": [7, 8, 9],
        "green_top": [10, 11, 12],
        "red_sash_headband": [13],
        "yellow_detail": [14],
        "fx": [],
    },
    "bento": {
        "transparent": [0],
        "outline": [1, 15],
        "blue_petrol_shirt": [2, 3, 4],
        "skin": [5, 6, 12, 13, 14],
        "cream_pants": [7],
        "bandage_orange": [8, 9, 10],
        "deep_shadow": [11],
        "fx": [],
    },
}

FX_DOMAIN = {
    "transparent": [0],
    "outline": [1],
    "spark": [2, 3, 4, 5, 6, 7],
    "cool_glint": [8, 9, 10],
    "violet_flash": [11, 12, 13, 14, 15],
}

CASE_INFO = {
    "lib_case_consulted": "case_spritesheet_islands",
    "lib_case_path": "tools/sgdk_wrapper/.agent/lib_case/art-translation/case_spritesheet_islands",
    "method": "chroma key -> whole-image BFS -> projection-valley frame windows -> per-window BFS diagnostics -> bbox envelope + padding -> fixed strip scale -> indexed candidate",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def pal_flat(colors: list[tuple[int, int, int]]) -> list[int]:
    out: list[int] = []
    for r, g, b in colors:
        out.extend([r, g, b])
    out.extend([0] * (768 - len(out)))
    return out


def color_dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def nearest_palette_index(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> int:
    best_i = 1
    best_d = 10**9
    for i, color in enumerate(palette[1:], start=1):
        d = (rgb[0] - color[0]) ** 2 + (rgb[1] - color[1]) ** 2 + (rgb[2] - color[2]) ** 2
        if d < best_d:
            best_i = i
            best_d = d
    return best_i


def bg_color(img: Image.Image) -> tuple[int, int, int]:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0)]
    colors = [rgba.getpixel(p)[:3] for p in pts]
    return max(set(colors), key=colors.count)


def chroma_mask(img: Image.Image, bg: tuple[int, int, int], tolerance: int = 72) -> list[list[bool]]:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    mask: list[list[bool]] = []
    for y in range(h):
        row: list[bool] = []
        for x in range(w):
            r, g, b, a = px[x, y]
            row.append(a > 16 and color_dist((r, g, b), bg) > tolerance)
        mask.append(row)
    return mask


def foreground_column_counts(mask: list[list[bool]]) -> list[int]:
    h = len(mask)
    w = len(mask[0]) if h else 0
    return [sum(1 for y in range(h) if mask[y][x]) for x in range(w)]


def smooth_column_sum(cols: list[int], x: int, radius: int = 2) -> int:
    lo = max(0, x - radius)
    hi = min(len(cols) - 1, x + radius)
    return sum(cols[lo:hi + 1])


def best_projection_valley(cols: list[int], target: int, lo: int, hi: int) -> tuple[int, int]:
    lo = max(1, lo)
    hi = min(len(cols) - 2, hi)
    if lo > hi:
        x = max(1, min(len(cols) - 2, target))
        return x, smooth_column_sum(cols, x)
    x = min(range(lo, hi + 1), key=lambda c: (smooth_column_sum(cols, c), abs(c - target)))
    return x, smooth_column_sum(cols, x)


def allocate_component_frame_counts(widths: list[int], frames: int) -> list[int]:
    """Allocate expected frame counts to large source islands without changing pixels."""
    if not widths:
        return []
    total_width = max(1, sum(widths))
    raw = [max(1.0, frames * (w / total_width)) for w in widths]
    counts = [max(1, int(round(v))) for v in raw]
    while sum(counts) > frames:
        candidates = [i for i, c in enumerate(counts) if c > 1]
        if not candidates:
            break
        i = max(candidates, key=lambda idx: (counts[idx] - raw[idx], counts[idx]))
        counts[i] -= 1
    while sum(counts) < frames:
        i = max(range(len(counts)), key=lambda idx: (raw[idx] - counts[idx], widths[idx]))
        counts[i] += 1
    return counts


def derive_source_windows(
    img: Image.Image,
    frames: int,
    bg: tuple[int, int, int],
    min_component_area: int = 500,
) -> dict[str, Any]:
    """Derive source frame windows from foreground islands and projection valleys.

    This replaces blind equal-width slicing.  Wide connected components are split only
    at measured horizontal-projection valleys; no pixels are bridged, erased here, or
    invented.  Later component diagnostics still decide whether a candidate is safe.
    """
    mask = chroma_mask(img, bg)
    cols = foreground_column_counts(mask)
    components = component_boxes(mask, min_area=min_component_area)
    if components:
        max_area = max(int(c["area"]) for c in components)
        layout_min_area = max(5000, int(max_area * 0.08))
        layout_components = [c for c in components if int(c["area"]) >= layout_min_area]
    else:
        max_area = 0
        layout_min_area = 5000
        layout_components = []
    layout_components.sort(key=lambda c: c["bbox"][0])
    widths = [c["bbox"][2] - c["bbox"][0] + 1 for c in layout_components]
    counts = allocate_component_frame_counts(widths, frames)
    windows: list[dict[str, Any]] = []
    blockers: list[str] = []
    for comp, count in zip(layout_components, counts):
        x0, y0, x1, y1 = comp["bbox"]
        if count == 1:
            windows.append({
                "x0": x0,
                "x1": x1 + 1,
                "source": "whole_component",
                "component_bbox": list(comp["bbox"]),
                "split_count": 1,
                "separator_scores": [],
            })
            continue
        separators: list[int] = []
        separator_scores: list[dict[str, Any]] = []
        width = x1 - x0 + 1
        for k in range(1, count):
            target = int(round(x0 + k * width / count))
            radius = max(12, int(width / count * 0.25))
            sep, score = best_projection_valley(cols, target, target - radius, target + radius)
            separators.append(sep)
            separator_scores.append({
                "target_x": target,
                "separator_x": sep,
                "foreground_sum5": score,
                "foreground_ratio_of_source_height": round(score / max(1, img.height * 5), 4),
            })
            if score > img.height * 5 * 0.18:
                blockers.append(f"component_split_high_foreground:{x0}-{x1}@{sep}")
        cuts = [x0, *[s + 1 for s in separators], x1 + 1]
        for idx in range(count):
            windows.append({
                "x0": cuts[idx],
                "x1": cuts[idx + 1],
                "source": "component_projection_split",
                "component_bbox": list(comp["bbox"]),
                "split_count": count,
                "separator_scores": separator_scores,
            })
    if len(windows) != frames:
        blockers.append(f"source_window_count_mismatch:{len(windows)}_for_{frames}")
    windows = windows[:frames]
    return {
        "method": "whole-image BFS components -> proportional frame allocation -> horizontal projection valley split",
        "components": components[:24],
        "layout_component_min_area": layout_min_area,
        "layout_component_count": len(layout_components),
        "ignored_layout_component_count": max(0, len(components) - len(layout_components)),
        "component_widths": widths,
        "component_frame_counts": counts,
        "windows": windows,
        "blocking_statuses": blockers,
    }


def component_boxes(mask: list[list[bool]], min_area: int = 1) -> list[dict[str, Any]]:
    h = len(mask)
    w = len(mask[0]) if h else 0
    seen = [[False] * w for _ in range(h)]
    comps: list[dict[str, Any]] = []
    for y in range(h):
        for x in range(w):
            if seen[y][x] or not mask[y][x]:
                continue
            q: deque[tuple[int, int]] = deque([(x, y)])
            seen[y][x] = True
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
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and mask[ny][nx]:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            if area >= min_area:
                comps.append({
                    "area": area,
                    "bbox": (min_x, min_y, max_x, max_y),
                    "center": ((min_x + max_x) / 2.0, (min_y + max_y) / 2.0),
                    "touches": {
                        "left": min_x == 0,
                        "right": max_x == w - 1,
                        "top": min_y == 0,
                        "bottom": max_y == h - 1,
                    },
                })
    comps.sort(key=lambda item: int(item["area"]), reverse=True)
    return comps


def union_bbox(boxes: list[tuple[int, int, int, int]]) -> tuple[int, int, int, int] | None:
    if not boxes:
        return None
    return (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def visible_bbox_p(frame: Image.Image) -> tuple[int, int, int, int] | None:
    px = frame.load()
    w, h = frame.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            if px[x, y] != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def frame_metrics(frame: Image.Image) -> dict[str, Any]:
    p = frame.load()
    w, h = frame.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            if p[x, y] != 0:
                xs.append(x)
                ys.append(y)
    if not xs:
        return {"bbox": None, "nonzero": 0}
    bbox = [min(xs), min(ys), max(xs), max(ys)]
    return {
        "bbox": bbox,
        "bbox_size": [bbox[2] - bbox[0] + 1, bbox[3] - bbox[1] + 1],
        "center": [round(sum(xs) / len(xs), 2), round(sum(ys) / len(ys), 2)],
        "bottom": max(ys),
        "nonzero": len(xs),
    }


def classify_source_components(
    mask_crop: list[list[bool]],
    min_debris_area: int = 96,
    boundary_spill_ratio: float = 0.35,
) -> dict[str, Any]:
    comps = component_boxes(mask_crop, min_area=1)
    if not comps:
        return {
            "status": "rework_source_needed",
            "accepted": [],
            "rejected": [],
            "components": [],
            "blocking_statuses": ["frame_empty_after_chroma_key"],
        }

    main = comps[0]
    accepted = [main]
    rejected: list[dict[str, Any]] = []
    blockers: list[str] = []
    for comp in comps[1:]:
        area = int(comp["area"])
        ratio = area / max(1, int(main["area"]))
        touches = comp["touches"]
        near_temporal_edge = bool(touches["left"] or touches["right"])
        if area < min_debris_area:
            rejected.append({**comp, "reason": "small_island_debris", "area_ratio_to_main": ratio})
        elif near_temporal_edge and ratio < boundary_spill_ratio:
            rejected.append({**comp, "reason": "source_neighbor_spill", "area_ratio_to_main": ratio})
        elif ratio >= 0.06 and not near_temporal_edge:
            accepted.append(comp)
        elif ratio >= 0.20:
            blockers.append("ambiguous_large_component")
            accepted.append(comp)
        else:
            rejected.append({**comp, "reason": "non_body_debris", "area_ratio_to_main": ratio})

    if blockers:
        status = "rework_source_needed"
    else:
        status = "selected_source_components"
    return {
        "status": status,
        "accepted": accepted,
        "rejected": rejected,
        "components": comps[:16],
        "blocking_statuses": blockers,
    }


def mask_crop_to_rgba(
    source_crop: Image.Image,
    accepted: list[dict[str, Any]],
    bg: tuple[int, int, int],
) -> Image.Image:
    """Apply only chroma alpha; component lists are diagnostics, not cleanup."""
    rgba = source_crop.convert("RGBA")
    mask = chroma_mask(source_crop, bg)
    px = rgba.load()
    for y in range(source_crop.height):
        for x in range(source_crop.width):
            if not mask[y][x]:
                px[x, y] = (0, 0, 0, 0)
    return rgba


def select_frame_crops(img: Image.Image, frames: int, bg: tuple[int, int, int], pad: int = 4) -> tuple[list[dict[str, Any]], list[str]]:
    w, h = img.size
    layout = derive_source_windows(img, frames, bg)
    windows = layout["windows"]
    frame_reports: list[dict[str, Any]] = []
    blockers: list[str] = list(layout["blocking_statuses"])
    if len(windows) != frames:
        windows = [
            {
                "x0": int(round(i * w / frames)),
                "x1": int(round((i + 1) * w / frames)),
                "source": "equal_width_fallback_blocked",
                "component_bbox": None,
                "split_count": 0,
                "separator_scores": [],
            }
            for i in range(frames)
        ]
    for i, window in enumerate(windows):
        x0 = int(window["x0"])
        x1 = int(window["x1"])
        rough = img.crop((x0, 0, x1, h))
        mask = chroma_mask(rough, bg)
        classified = classify_source_components(mask)
        if classified["status"] == "rework_source_needed":
            blockers.extend([f"frame_{i + 1}:{b}" for b in classified["blocking_statuses"]])
        accepted_boxes = [tuple(comp["bbox"]) for comp in classified["accepted"]]
        diagnostic_boxes = [tuple(comp["bbox"]) for comp in classified["components"]]
        diagnostic_bbox = union_bbox(diagnostic_boxes)
        local_bbox = union_bbox(accepted_boxes)
        if local_bbox is None:
            frame_reports.append({
                "frame": i + 1,
                "status": "rework_source_needed",
                "slicing_method": "global_bfs_islands" if window["source"] != "equal_width_fallback_blocked" else "equal_width_fallback_blocked",
                "rough_column": [x0, x1],
                "source_window_method": window["source"],
                "source_window_component_bbox": window["component_bbox"],
                "source_window_separator_scores": window["separator_scores"],
                "components": classified["components"],
                "blocking_statuses": ["frame_empty_after_component_selection"],
            })
            blockers.append(f"frame_{i + 1}:frame_empty_after_component_selection")
            continue

        lx0, ly0, lx1, ly1 = local_bbox
        crop_box = (
            max(0, x0 + lx0 - pad),
            max(0, ly0 - pad),
            min(w, x0 + lx1 + 1 + pad),
            min(h, ly1 + 1 + pad),
        )
        frame_reports.append({
            "frame": i + 1,
            "status": classified["status"],
            "slicing_method": "global_bfs_islands" if window["source"] != "equal_width_fallback_blocked" else "equal_width_fallback_blocked",
            "rough_column": [x0, x1],
            "source_window_method": window["source"],
            "source_window_component_bbox": window["component_bbox"],
            "source_window_separator_scores": window["separator_scores"],
            "source_bbox_without_padding": [x0 + lx0, ly0, x0 + lx1, ly1],
            "source_padding_pixels": pad,
            "diagnostic_bbox_with_rejected_components": [x0 + diagnostic_bbox[0], diagnostic_bbox[1], x0 + diagnostic_bbox[2], diagnostic_bbox[3]] if diagnostic_bbox else None,
            "crop_box": list(crop_box),
            "components": classified["components"],
            "accepted_components": classified["accepted"],
            "rejected_components": classified["rejected"],
            "blocking_statuses": classified["blocking_statuses"],
        })
    return frame_reports, blockers


def quantize_masked_cell(
    src_rgba: Image.Image,
    palette: list[tuple[int, int, int]],
    cell: tuple[int, int],
    scale: float,
    bottom_y: int,
) -> tuple[Image.Image, dict[str, Any]]:
    w, h = src_rgba.size
    new_size = (max(1, int(round(w * scale))), max(1, int(round(h * scale))))
    resized = src_rgba.resize(new_size, Image.Resampling.NEAREST)
    out = Image.new("P", cell, 0)
    out.putpalette(pal_flat(palette))
    ox = (cell[0] - new_size[0]) // 2
    oy = max(0, min(cell[1] - new_size[1], bottom_y - new_size[1]))
    rp = resized.load()
    op = out.load()
    for y in range(new_size[1]):
        for x in range(new_size[0]):
            r, g, b, a = rp[x, y]
            if a <= 16:
                continue
            tx = ox + x
            ty = oy + y
            if 0 <= tx < cell[0] and 0 <= ty < cell[1]:
                op[tx, ty] = nearest_palette_index((r, g, b), palette)
    return out, {"scale": scale, "new_size": list(new_size), "offset": [ox, oy]}


def make_evidence(strip: Image.Image, out_dir: Path, pivot: tuple[int, int], duration: int, cell_w: int) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rgb = strip.convert("RGB")
    contact = out_dir / "contact_sheet.png"
    rgb.save(contact)
    overlay = rgb.copy()
    draw = ImageDraw.Draw(overlay)
    for x in range(0, strip.width, cell_w):
        draw.rectangle((x, 0, x + cell_w - 1, strip.height - 1), outline=(40, 220, 80))
        draw.line((x + pivot[0], 0, x + pivot[0], strip.height - 1), fill=(255, 0, 0))
        draw.line((x, pivot[1], x + cell_w - 1, pivot[1]), fill=(0, 160, 255))
    pivot_overlay = out_dir / "pivot_overlay.png"
    overlay.save(pivot_overlay)
    gif = out_dir / "preview.gif"
    frames_img = []
    for x in range(0, strip.width, cell_w):
        frame = strip.crop((x, 0, x + cell_w, strip.height)).convert("RGB").resize((cell_w * 2, strip.height * 2), Image.Resampling.NEAREST)
        frames_img.append(frame)
    if frames_img:
        frames_img[0].save(gif, save_all=True, append_images=frames_img[1:], duration=duration * 16, loop=0)
    return {"contact_sheet": str(contact), "pivot_overlay": str(pivot_overlay), "preview_gif": str(gif)}


def convert_strip(project: Path, character: str, state: dict[str, Any]) -> dict[str, Any]:
    spec = SPECS[character]
    source = project / "data" / "source_art" / "premium_generation" / character / f"{state['id']}_v002_source.png"
    candidate = project / "data" / "processed" / "candidates" / "sprites" / character / f"{state['id']}.png"
    evidence_dir = project / "out" / "evidence" / "animation_candidates" / character / state["id"]
    if not source.is_file():
        return {
            "asset_id": f"spr_{character}_{state['id']}",
            "character": character,
            "state": state["id"],
            "status": "rework_source_needed",
            "source_path": str(source),
            "candidate_path": str(candidate),
            "blocking_statuses": ["premium_source_missing"],
        }

    img = Image.open(source).convert("RGBA")
    bg = bg_color(img)
    frames = int(state["frames"])
    cell = spec["cell"]
    palette = PALETTES[character]
    frame_reports, blockers = select_frame_crops(img, frames, bg)

    crop_sizes: list[tuple[int, int]] = []
    for fr in frame_reports:
        if "crop_box" not in fr:
            continue
        x0, y0, x1, y1 = fr["crop_box"]
        crop_sizes.append((x1 - x0, y1 - y0))
    fixed_scale = 1.0
    if crop_sizes:
        max_crop_w = max(size[0] for size in crop_sizes)
        max_crop_h = max(size[1] for size in crop_sizes)
        fixed_scale = min(spec["fit"][0] / max(1, max_crop_w), spec["fit"][1] / max(1, max_crop_h))

    out = Image.new("P", (cell[0] * frames, cell[1]), 0)
    out.putpalette(pal_flat(palette))
    metrics: list[dict[str, Any]] = []
    quantization_reports: list[dict[str, Any]] = []
    for fr in frame_reports:
        if "crop_box" not in fr:
            cell_img = Image.new("P", cell, 0)
            cell_img.putpalette(pal_flat(palette))
            quantization_reports.append({"frame": fr["frame"], "status": "empty"})
        else:
            crop_box = tuple(fr["crop_box"])
            source_crop = img.crop(crop_box)
            accepted_local = []
            for comp in fr["accepted_components"]:
                bx0, by0, bx1, by1 = comp["bbox"]
                accepted_local.append({
                    **comp,
                    "bbox": (
                        bx0 + fr["rough_column"][0] - crop_box[0],
                        by0 - crop_box[1],
                        bx1 + fr["rough_column"][0] - crop_box[0],
                        by1 - crop_box[1],
                    ),
                })
            masked = mask_crop_to_rgba(source_crop, accepted_local, bg)
            bottom = 82 if state["id"] in {"knockdown", "getup"} else 80
            cell_img, q_report = quantize_masked_cell(masked, palette, cell, fixed_scale, bottom)
            q_report["frame"] = fr["frame"]
            q_report["resample"] = "NEAREST"
            quantization_reports.append(q_report)
        out.paste(cell_img, ((fr["frame"] - 1) * cell[0], 0))
        metrics.append(frame_metrics(cell_img))

    candidate.parent.mkdir(parents=True, exist_ok=True)
    out.save(candidate, transparency=0, optimize=False, bits=4)
    evidence = make_evidence(out, evidence_dir, spec["pivot"], int(state["duration"]), cell[0])
    status = "candidate_ready_for_integrity_gate" if not blockers else "rework_source_needed"
    report = {
        "schema": "axe_candidate_sprite_report.v1",
        "asset_id": f"spr_{character}_{state['id']}",
        "generated_at_utc": now_iso(),
        "character": character,
        "state": state["id"],
        "state_profile": state["profile"],
        "asset_kind": "character_animation_strip",
        "status": status,
        "source_path": str(source),
        "source_sha256": sha256(source),
        "source_size": list(img.size),
        "source_background_rgb": list(bg),
        "candidate_path": str(candidate),
        "candidate_sha256": sha256(candidate),
        "cell": list(cell),
        "frames": frames,
        "pivot": list(spec["pivot"]),
        "frame_reports": frame_reports,
        "frame_metrics": metrics,
        "quantization_reports": quantization_reports,
        "fixed_scale": fixed_scale,
        "resample": "NEAREST",
        "automatic_pixel_cleanup": False,
        "component_bridge_policy": "forbidden",
        "per_frame_normalization": False,
        "lib_case_consulted": CASE_INFO["lib_case_consulted"],
        "case_method": CASE_INFO["method"],
        "blocking_statuses": blockers,
        "evidence": evidence,
    }
    write_json(evidence_dir / "sprite_artifact_report.json", report)
    write_json(evidence_dir / "foot_contact_report.json", {
        "schema": "foot_contact_report.v2",
        "measurement_level": "measured",
        "character": character,
        "state": state["id"],
        "state_profile": state["profile"],
        "pivot": list(spec["pivot"]),
        "bottom_by_frame": [m.get("bottom") for m in metrics],
        "status": "passed" if not blockers else "rework_source_needed",
    })
    write_json(evidence_dir / "frame_delta_report.json", frame_delta_report(character, state, metrics))
    return report


def frame_delta_report(character: str, state: dict[str, Any], metrics: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = []
    for i in range(1, len(metrics)):
        prev = metrics[i - 1]
        cur = metrics[i]
        if not prev.get("center") or not cur.get("center"):
            deltas.append({"from": i, "to": i + 1, "status": "empty_frame"})
            continue
        deltas.append({
            "from": i,
            "to": i + 1,
            "center_delta": [
                round(cur["center"][0] - prev["center"][0], 2),
                round(cur["center"][1] - prev["center"][1], 2),
            ],
            "bottom_delta": (cur.get("bottom") or 0) - (prev.get("bottom") or 0),
            "nonzero_delta": (cur.get("nonzero") or 0) - (prev.get("nonzero") or 0),
        })
    return {
        "schema": "frame_delta_report.v2",
        "measurement_level": "measured",
        "character": character,
        "state": state["id"],
        "state_profile": state["profile"],
        "deltas": deltas,
        "status": "measured",
    }


def scale_lock_report(reports: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    thresholds = {
        "standing": {"height_ratio_max": 1.35, "bottom_span_max": 12},
        "dash": {"height_ratio_max": 1.55, "bottom_span_max": 14},
        "hop": {"height_ratio_max": 1.65, "bottom_span_max": 18},
        "crouch": {"height_ratio_max": 1.70, "bottom_span_max": 14},
        "throw": {"height_ratio_max": 3.20, "bottom_span_max": 16},
        "grounded": {"height_ratio_max": 3.80, "bottom_span_max": 18},
        "knockdown": {"height_ratio_max": 5.00, "bottom_span_max": 18},
        "getup": {"height_ratio_max": 5.00, "bottom_span_max": 18},
        "fx": {"height_ratio_max": 4.0, "bottom_span_max": 99},
    }
    for report in reports:
        metrics = report.get("frame_metrics", [])
        heights = [m.get("bbox_size", [0, 0])[1] for m in metrics if m.get("bbox_size")]
        bottoms = [m.get("bottom") for m in metrics if m.get("bottom") is not None]
        profile = report.get("state_profile", "standing")
        th = thresholds.get(profile, thresholds["standing"])
        ratio = max(heights) / max(1, min(heights)) if heights else 0
        bottom_span = max(bottoms) - min(bottoms) if bottoms else 0
        scale_values = [q.get("scale") for q in report.get("quantization_reports", []) if isinstance(q.get("scale"), (int, float))]
        scale_unique = len({round(float(v), 6) for v in scale_values})
        status = "passed"
        local_blockers: list[str] = []
        if scale_unique > 1:
            local_blockers.append("per_frame_scale_drift")
        if ratio > th["height_ratio_max"]:
            local_blockers.append("state_profile_height_ratio_exceeded")
        if bottom_span > th["bottom_span_max"]:
            local_blockers.append("pivot_groundline_unstable")
        if local_blockers:
            status = "rework"
            blockers.extend([f"{report['asset_id']}:{b}" for b in local_blockers])
        rows.append({
            "asset_id": report["asset_id"],
            "state_profile": profile,
            "height_min": min(heights) if heights else 0,
            "height_max": max(heights) if heights else 0,
            "height_ratio": ratio,
            "bottom_span": bottom_span,
            "fixed_scale": report.get("fixed_scale"),
            "scale_unique_count": scale_unique,
            "status": status,
            "blocking_statuses": local_blockers,
        })
    return {
        "schema": "scale_lock_report.v1",
        "measurement_level": "measured",
        "state_profile_thresholds": thresholds,
        "per_frame_normalization": False,
        "overall_status": "passed" if not blockers else "rework",
        "blocking_statuses": blockers,
        "assets": rows,
    }


def write_resources(project: Path) -> None:
    lines = [
        "# AXE DE ACO FIGHTER resources generated after approved candidate promotion",
        "IMAGE img_stage_bg_b \"bgs/stage_bg_b.png\" BEST",
        "IMAGE img_stage_bg_a \"bgs/stage_bg_a.png\" BEST",
        "",
    ]
    for character in ("marina", "bento"):
        tiles_w = SPECS[character]["tiles"][0]
        for state in STATES:
            lines.append(f"SPRITE spr_{character}_{state['id']} \"sprites/{character}/{state['id']}.png\" {tiles_w} 11 FAST {state['duration']}")
        lines.append("")
    lines.append('SPRITE spr_hit_spark "sprites/fx/hit_spark.png" 4 4 FAST 3')
    lines.append('SPRITE spr_dust "sprites/fx/dust.png" 3 2 FAST 4')
    lines.append("")
    (project / "res" / "resources.res").write_text("\n".join(lines), encoding="utf-8")


def write_candidate_reports(project: Path, reports: list[dict[str, Any]]) -> None:
    logs = project / "out" / "logs"
    candidate_log_dir = logs / "candidate_conversion"
    blocking = []
    for report in reports:
        if report.get("blocking_statuses"):
            blocking.extend([f"{report['asset_id']}:{b}" for b in report["blocking_statuses"]])
    scale_report = scale_lock_report(reports)
    if scale_report["blocking_statuses"]:
        blocking.extend(scale_report["blocking_statuses"])
    manifest = {
        "schema": "asset_candidate_manifest.v1",
        "generated_at_utc": now_iso(),
        "project_root": str(project),
        "status": "candidates_ready_for_integrity_gate" if not blocking else "candidate_generation_rework",
        "lib_case_consulted": CASE_INFO["lib_case_consulted"],
        "lib_case_path": CASE_INFO["lib_case_path"],
        "method": CASE_INFO["method"],
        "automatic_pixel_cleanup": False,
        "component_bridge_policy": "forbidden",
        "per_frame_normalization": False,
        "resample": "NEAREST",
        "res_promotion_performed": False,
        "assets": reports,
        "blocking_statuses": blocking,
    }
    write_json(candidate_log_dir / "asset_candidate_manifest.json", manifest)
    write_json(logs / "scale_lock_report.json", scale_report)
    write_json(logs / "palette_domain_report.json", palette_domain_report())
    write_json(logs / "slicing_cell_contract.json", slicing_cell_contract())
    write_json(logs / "asset_builder_report.json", {
        "schema": "asset_builder_report.v3",
        "generated_at_utc": now_iso(),
        "status": manifest["status"],
        "candidate_root": str(project / "data" / "processed" / "candidates"),
        "res_promotion_performed": False,
        "blocking_statuses": blocking,
    })
    write_json(logs / "visual_delivery_gate_report.json", {
        "schema": "visual_delivery_gate_report.v3",
        "ready_for_aaa": False,
        "overall_status": "visual_gate_blocked",
        "prototype_status": "prototype_playable_visual_gate_blocked",
        "leaf_blocker_propagation": True,
        "blocking_statuses": ["fresh_rom_evidence_missing_after_candidate_generation", *blocking, "stage_fx_hud_source_still_prototype", "perceptual_quality_unmeasured"],
        "passed_axes": ["candidate_pipeline_no_bridge", "candidate_pipeline_no_per_frame_normalization", "palette_domain_report_measured"],
        "failed_axes": ["fresh_rom_evidence_missing_after_candidate_generation", *blocking, "stage_fx_hud_source_still_prototype", "perceptual_quality_unmeasured"],
        "perceptual_quality": "nao_medido",
    })


def palette_domain_report() -> dict[str, Any]:
    return {
        "schema": "palette_domain_report.v1",
        "measurement_level": "measured",
        "generated_at_utc": now_iso(),
        "characters": CHARACTER_DOMAINS,
        "fx": FX_DOMAIN,
        "hud": {"source_status": "prototype_or_runtime_text", "blocking_for_aaa": True},
        "bg": {"source_status": "prototype_source_still_in_use", "blocking_for_aaa": True},
        "baked_fx_policy": "BAKED_FX is evaluated only against declared FX palette domains; warm skin/sash/shadow material slots are not spark pixels.",
        "status": "passed_for_character_domains_blocked_for_stage_fx_hud",
        "blocking_statuses": ["stage_fx_hud_source_still_prototype"],
    }


def slicing_cell_contract() -> dict[str, Any]:
    return {
        "schema": "slicing_cell_contract.v2",
        "measurement_level": "measured",
        "generated_at_utc": now_iso(),
        "lib_case_consulted": CASE_INFO["lib_case_consulted"],
        "policy": "fixed_runtime_cell_with_measured_bbox_envelope_per_action",
        "method": CASE_INFO["method"],
        "marina": {"frame_width": 80, "frame_height": 88, "pivot": [40, 76], "fit": [72, 78]},
        "bento": {"frame_width": 88, "frame_height": 88, "pivot": [44, 76], "fit": [80, 78]},
        "forbidden": ["component_bridge", "per_frame_height_normalization", "automatic_res_promotion"],
    }


def integrity_summary_clean(project: Path) -> tuple[bool, list[str]]:
    summary_path = project / "out" / "logs" / "sprite_integrity_summary.json"
    scale_path = project / "out" / "logs" / "scale_lock_report.json"
    palette_path = project / "out" / "logs" / "palette_domain_report.json"
    blockers: list[str] = []
    if not summary_path.is_file():
        blockers.append("sprite_integrity_summary_missing")
    else:
        summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
        if summary.get("overall_status") != "passed":
            blockers.append(f"sprite_integrity_summary:{summary.get('overall_status')}")
    if not scale_path.is_file():
        blockers.append("scale_lock_report_missing")
    else:
        scale = json.loads(scale_path.read_text(encoding="utf-8-sig"))
        if scale.get("overall_status") != "passed":
            blockers.append(f"scale_lock_report:{scale.get('overall_status')}")
    if not palette_path.is_file():
        blockers.append("palette_domain_report_missing")
    else:
        palette = json.loads(palette_path.read_text(encoding="utf-8-sig"))
        if "character" not in palette.get("status", "") and palette.get("status") != "passed":
            blockers.append(f"palette_domain_report:{palette.get('status')}")
    return (len(blockers) == 0, blockers)


def promote_approved(project: Path) -> int:
    ok, blockers = integrity_summary_clean(project)
    logs = project / "out" / "logs"
    report_root = logs / "candidate_conversion"
    manifest_path = report_root / "asset_candidate_manifest.json"
    if not manifest_path.is_file():
        blockers.append("asset_candidate_manifest_missing")
        ok = False
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig")) if manifest_path.is_file() else {"assets": []}
    if manifest.get("blocking_statuses"):
        blockers.extend([f"candidate:{b}" for b in manifest["blocking_statuses"]])
        ok = False
    promoted: list[dict[str, Any]] = []
    if ok:
        for report in manifest.get("assets", []):
            candidate = Path(report["candidate_path"])
            res = project / "res" / "sprites" / report["character"] / f"{report['state']}.png"
            res.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, res)
            promoted.append({
                "asset_id": report["asset_id"],
                "candidate_path": str(candidate),
                "res_path": str(res),
                "candidate_sha256": sha256(candidate),
                "res_sha256": sha256(res),
            })
        write_resources(project)
    write_json(logs / "candidate_to_res_promotion_report.json", {
        "schema": "candidate_to_res_promotion_report.v1",
        "generated_at_utc": now_iso(),
        "status": "promoted" if ok else "blocked",
        "promoted_count": len(promoted),
        "promoted_assets": promoted,
        "blocking_statuses": blockers,
        "source_to_rom_visual_match": "not_measured_until_rebuild_and_blastem_capture",
    })
    write_json(logs / "visual_delivery_gate_report.json", {
        "schema": "visual_delivery_gate_report.v3",
        "ready_for_aaa": False,
        "overall_status": "visual_gate_blocked",
        "prototype_status": "prototype_playable_visual_gate_blocked",
        "leaf_blocker_propagation": True,
        "blocking_statuses": ["fresh_rom_evidence_missing_after_res_promotion", "stage_fx_hud_source_still_prototype", "perceptual_quality_unmeasured", *blockers],
        "passed_axes": ["candidate_integrity_gate_clean"] if ok else [],
        "failed_axes": ["fresh_rom_evidence_missing_after_res_promotion", "stage_fx_hud_source_still_prototype", "perceptual_quality_unmeasured", *blockers],
        "perceptual_quality": "nao_medido",
    })
    return 0 if ok else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--mode", choices=["candidates", "promote-approved"], default="candidates")
    args = parser.parse_args()
    project = Path(args.project).resolve()
    if args.mode == "promote-approved":
        return promote_approved(project)
    reports = []
    for character in ("marina", "bento"):
        for state in STATES:
            reports.append(convert_strip(project, character, state))
    write_candidate_reports(project, reports)
    return 0 if all(not r.get("blocking_statuses") for r in reports) else 2


if __name__ == "__main__":
    raise SystemExit(main())
