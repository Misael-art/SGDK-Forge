#!/usr/bin/env python3
"""Estimate Mega Drive sprite pressure per scanline.

Input: JSON object with a sprites array. Each sprite needs x, y, w, h, and may
provide sprite_links. If sprite_links is omitted, the script estimates hardware
links from 32x32 sprite cells. Output: JSON pressure report.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.0.0"
VISIBLE_LINES = 224
SPRITES_PER_SCANLINE_LIMIT = 20
TOTAL_SPRITE_LINK_LIMIT = 80


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _estimated_links(w: int, h: int) -> int:
    return max(1, math.ceil(max(1, w) / 32) * math.ceil(max(1, h) / 32))


def simulate(data: dict[str, Any]) -> dict[str, Any]:
    sprites = data.get("sprites") or []
    pressure = [0 for _ in range(VISIBLE_LINES)]
    blockers: list[str] = []
    warnings: list[str] = []
    total_links = 0

    for idx, sprite in enumerate(sprites):
        if not isinstance(sprite, dict):
            blockers.append(f"invalid_sprite_entry:{idx}")
            continue

        y = _int(sprite.get("y"))
        h = _int(sprite.get("h"), 1)
        w = _int(sprite.get("w"), 1)
        links = _int(sprite.get("sprite_links"), _estimated_links(w, h))
        total_links += max(0, links)

        start = max(0, y)
        end = min(VISIBLE_LINES, y + h)
        for line in range(start, end):
            pressure[line] += links

    max_pressure = max(pressure) if pressure else 0
    over_lines = [
        {"scanline": line, "sprite_links": count}
        for line, count in enumerate(pressure)
        if count > SPRITES_PER_SCANLINE_LIMIT
    ]

    if over_lines:
        blockers.append("sprites_per_scanline_over_20")
    if total_links > TOTAL_SPRITE_LINK_LIMIT:
        blockers.append("total_sprite_links_over_80")
    if max_pressure >= 18 and not over_lines:
        warnings.append("scanline_pressure_near_limit")

    return {
        "tool_name": "vdp_scanline_simulator",
        "tool_version": TOOL_VERSION,
        "status": "ok" if not blockers else "error",
        "sprite_count": len(sprites),
        "total_sprite_links": total_links,
        "max_sprites_per_scanline": max_pressure,
        "over_limit_lines": over_lines,
        "blockers": blockers,
        "warnings": warnings,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def self_check() -> int:
    ok = simulate({"sprites": [{"name": "hero", "x": 120, "y": 120, "w": 32, "h": 48}]})
    bad = simulate({"sprites": [{"name": f"s{i}", "x": 0, "y": 50, "w": 32, "h": 16, "sprite_links": 1} for i in range(21)]})
    if ok["status"] != "ok":
        print("self-check failed: simple scene rejected", file=sys.stderr)
        return 1
    if bad["status"] != "error" or "sprites_per_scanline_over_20" not in bad["blockers"]:
        print("self-check failed: scanline overflow not detected", file=sys.stderr)
        return 1
    print("vdp_scanline_simulator self-check passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if not args.input:
        parser.error("--input is required unless --self-check is used")
    report = simulate(load_json(args.input))
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
