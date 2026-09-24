"""Deterministic border-connected matte extraction for raster art sources.

This module removes only background pixels that are color-compatible with the
image border *and connected to that border*.  It deliberately does not guess a
character from a global lightness/saturation threshold: enclosed light colors
remain foreground.  The output is a binary mask plus measurements that allow a
caller to fail closed before native sprite conversion.
"""
from __future__ import annotations

from collections import Counter, deque
from typing import Any

from PIL import Image


TOOL_NAME = "forge_art.foreground_matte"
TOOL_VERSION = "1.0.0"


def _rgb_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def _border_pixels(rgb: Image.Image) -> list[tuple[int, int, int]]:
    px = rgb.load()
    w, h = rgb.size
    values = [px[x, 0] for x in range(w)] + [px[x, h - 1] for x in range(w)]
    if h > 2:
        values += [px[0, y] for y in range(1, h - 1)]
        values += [px[w - 1, y] for y in range(1, h - 1)]
    return values


def _prototypes(rgb: Image.Image, limit: int = 8) -> list[tuple[int, int, int]]:
    """Return representative border colors, robust to modest gradients."""
    buckets: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {}
    for color in _border_pixels(rgb):
        key = tuple(channel // 16 for channel in color)
        buckets.setdefault(key, []).append(color)
    ranked = sorted(buckets.values(), key=len, reverse=True)[:limit]
    return [tuple(round(sum(c[i] for c in group) / len(group)) for i in range(3))
            for group in ranked]


def extract_foreground_mask(image: Image.Image, tolerance: int = 34) -> tuple[Image.Image, dict[str, Any]]:
    """Extract a binary foreground mask and return an auditable report.

    Pixels are background only when close to a sampled border prototype and
    reachable from the border through other compatible pixels.  This prevents
    white eyes, cloth highlights and enclosed pale materials from disappearing.
    """
    rgb = image.convert("RGB")
    w, h = rgb.size
    prototypes = _prototypes(rgb)
    src = rgb.load()
    background = bytearray(w * h)
    queue: deque[tuple[int, int]] = deque()

    def compatible(x: int, y: int) -> bool:
        return bool(prototypes) and min(_rgb_distance(src[x, y], p) for p in prototypes) <= tolerance

    def seed(x: int, y: int) -> None:
        index = y * w + x
        if not background[index] and compatible(x, y):
            background[index] = 1
            queue.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(1, h - 1):
        seed(0, y)
        seed(w - 1, y)

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h:
                index = ny * w + nx
                if not background[index] and compatible(nx, ny):
                    background[index] = 1
                    queue.append((nx, ny))

    raw = bytearray(255 if not value else 0 for value in background)
    mask = Image.frombytes("L", (w, h), bytes(raw))
    bbox = mask.getbbox()
    filled = sum(1 for value in raw if value)
    occupancy = filled / (w * h) if w and h else 0.0
    blockers: list[str] = []
    if not bbox or filled == 0:
        blockers.append("foreground_not_found")
    if occupancy >= 0.90:
        blockers.append("background_extraction_failed_high_occupancy")
    if bbox == (0, 0, w, h):
        blockers.append("foreground_touches_all_canvas_edges")

    report = {
        "schema_version": "1.0.0",
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "width": w,
        "height": h,
        "method": "border_connected_color_flood_v1",
        "tolerance": tolerance,
        "border_prototypes_rgb": [list(p) for p in prototypes],
        "foreground_pixels": filled,
        "canvas_pixels": w * h,
        "foreground_occupancy_pct": round(occupancy * 100, 2),
        "bbox": list(bbox) if bbox else None,
        "status": "passed" if not blockers else "rejected",
        "blocking_statuses": blockers,
    }
    return mask, report


def self_check() -> dict[str, Any]:
    fixtures: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        fixtures.append({"fixture": name, "status": "passed" if passed else "failed",
                         "detail": detail})

    clean = Image.new("RGB", (32, 32), (238, 238, 230))
    px = clean.load()
    for y in range(6, 28):
        for x in range(10, 22):
            px[x, y] = (34, 68, 102)
    # Enclosed pale material must remain foreground.
    px[15, 12] = (238, 238, 230)
    mask, report = extract_foreground_mask(clean)
    add("border_background_removed", report["status"] == "passed" and mask.getpixel((0, 0)) == 0,
        str(report))
    add("enclosed_pale_pixel_preserved", mask.getpixel((15, 12)) == 255,
        "border connectivity, not color alone, decides background")

    full = Image.new("RGB", (16, 16), (34, 34, 34))
    full_mask, full_report = extract_foreground_mask(full, tolerance=0)
    add("uniform_canvas_fails_closed", full_report["status"] == "rejected"
        and full_mask.getbbox() is None, str(full_report))

    failed = [f for f in fixtures if f["status"] != "passed"]
    return {"tool": TOOL_NAME, "tool_version": TOOL_VERSION,
            "fixtures_total": len(fixtures), "fixtures_passed": len(fixtures) - len(failed),
            "fixtures": fixtures, "blocking": bool(failed)}
