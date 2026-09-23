#!/usr/bin/env python3
"""Estimate Mega Drive sprite pressure per scanline.

Input: JSON object with a sprites array. Each logical sprite needs x, y, w, h.
The script decomposes it into real <=32x32 VDP cells, so vertically stacked
cells contribute only to the scanlines they actually cover. An exact
hardware_cells list may be supplied when the engine layout is already known.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.2.0"
VISIBLE_LINES = 224
TOTAL_SPRITE_LINK_LIMIT = 80

# O VDP impoe DOIS limites por scanline ao mesmo tempo, nao um. A v1.0.0 media
# apenas a contagem, entao toda cena validada por ela ficou descoberta no
# orcamento de pixel. Para sprites de 16px os dois limites fecham juntos
# (20 x 16 = 320), o que torna facil acreditar que so existe um.
DISPLAY_MODES = {
    "h40": {"sprites_per_scanline": 20, "pixels_per_scanline": 320},
    "h32": {"sprites_per_scanline": 16, "pixels_per_scanline": 256},
}
DEFAULT_DISPLAY_MODE = "h40"

# Doutrina de audacia: folga nao medida e timidez. Abaixo desta utilizacao o
# projeto pode estar deixando hardware na mesa sem ter decidido isso — vira
# aviso, nunca blocker, e some quando houver justificativa declarada.
HEADROOM_UNEXPLOITED_BELOW = 0.60


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _estimated_links(w: int, h: int) -> int:
    return max(1, math.ceil(max(1, w) / 32) * math.ceil(max(1, h) / 32))


def _geometry_cells(sprite: dict[str, Any]) -> list[dict[str, int]]:
    """Decompose one logical rectangle into legal VDP hardware cells."""
    explicit = sprite.get("hardware_cells")
    if isinstance(explicit, list):
        cells = []
        for cell in explicit:
            if not isinstance(cell, dict):
                continue
            cells.append({"x": _int(cell.get("x")), "y": _int(cell.get("y")),
                          "w": _int(cell.get("w")), "h": _int(cell.get("h"))})
        return cells
    x, y = _int(sprite.get("x")), _int(sprite.get("y"))
    w, h = max(1, _int(sprite.get("w"), 1)), max(1, _int(sprite.get("h"), 1))
    cells = []
    for oy in range(0, h, 32):
        for ox in range(0, w, 32):
            cells.append({"x": x + ox, "y": y + oy,
                          "w": min(32, w - ox), "h": min(32, h - oy)})
    return cells


def simulate(data: dict[str, Any]) -> dict[str, Any]:
    sprites = data.get("sprites") or []
    mode_name = str(data.get("display_mode", DEFAULT_DISPLAY_MODE)).lower()
    mode = DISPLAY_MODES.get(mode_name)
    blockers: list[str] = []
    warnings: list[str] = []
    if mode is None:
        warnings.append(f"unknown_display_mode:{mode_name}_falling_back_to_{DEFAULT_DISPLAY_MODE}")
        mode_name = DEFAULT_DISPLAY_MODE
        mode = DISPLAY_MODES[DEFAULT_DISPLAY_MODE]
    sprite_limit = mode["sprites_per_scanline"]
    pixel_limit = mode["pixels_per_scanline"]

    pressure = [0 for _ in range(VISIBLE_LINES)]
    pixel_pressure = [0 for _ in range(VISIBLE_LINES)]
    total_links = 0

    for idx, sprite in enumerate(sprites):
        if not isinstance(sprite, dict):
            blockers.append(f"invalid_sprite_entry:{idx}")
            continue

        cells = _geometry_cells(sprite)
        if not cells or any(c["w"] <= 0 or c["h"] <= 0 or c["w"] > 32 or c["h"] > 32
                            for c in cells):
            blockers.append(f"invalid_hardware_cells:{idx}")
            continue
        declared_links = sprite.get("sprite_links")
        if declared_links is not None and _int(declared_links) != len(cells):
            warnings.append(f"sprite_links_disagree_with_geometry:{idx}:"
                            f"declared={_int(declared_links)}:derived={len(cells)}")
        total_links += len(cells)
        for cell in cells:
            start = max(0, cell["y"])
            end = min(VISIBLE_LINES, cell["y"] + cell["h"])
            for line in range(start, end):
                pressure[line] += 1
                pixel_pressure[line] += cell["w"]

    max_pressure = max(pressure) if pressure else 0
    max_pixels = max(pixel_pressure) if pixel_pressure else 0

    over_lines = [
        {"scanline": line, "sprite_links": count}
        for line, count in enumerate(pressure)
        if count > sprite_limit
    ]
    over_pixel_lines = [
        {"scanline": line, "sprite_pixels": count}
        for line, count in enumerate(pixel_pressure)
        if count > pixel_limit
    ]

    if over_lines:
        blockers.append(f"sprites_per_scanline_over_{sprite_limit}")
    if over_pixel_lines:
        blockers.append(f"sprite_pixels_per_scanline_over_{pixel_limit}")
    if total_links > TOTAL_SPRITE_LINK_LIMIT:
        blockers.append("total_sprite_links_over_80")
    if max_pressure >= sprite_limit - 2 and not over_lines:
        warnings.append("scanline_pressure_near_limit")
    if max_pixels >= pixel_limit - 32 and not over_pixel_lines:
        warnings.append("scanline_pixel_pressure_near_limit")

    sprite_use = (max_pressure / sprite_limit) if sprite_limit else 0.0
    pixel_use = (max_pixels / pixel_limit) if pixel_limit else 0.0
    binding = "sprite_count" if sprite_use >= pixel_use else "sprite_pixels"
    peak_use = max(sprite_use, pixel_use)

    justification = str(data.get("headroom_justification", "")).strip()
    if sprites and peak_use < HEADROOM_UNEXPLOITED_BELOW and not justification:
        warnings.append("unexploited_headroom")

    return {
        "tool_name": "vdp_scanline_simulator",
        "tool_version": TOOL_VERSION,
        "status": "ok" if not blockers else "error",
        "display_mode": mode_name,
        "limits": {"sprites_per_scanline": sprite_limit, "pixels_per_scanline": pixel_limit},
        "sprite_count": len(sprites),
        "hardware_sprite_count": total_links,
        "total_sprite_links": total_links,
        "max_sprites_per_scanline": max_pressure,
        "max_sprite_pixels_per_scanline": max_pixels,
        "over_limit_lines": over_lines,
        "over_pixel_limit_lines": over_pixel_lines,
        "headroom": {
            "sprite_utilization": round(sprite_use, 3),
            "pixel_utilization": round(pixel_use, 3),
            "binding_limit": binding,
            "peak_utilization": round(peak_use, 3),
            "unexploited_threshold": HEADROOM_UNEXPLOITED_BELOW,
            "justification": justification or None,
            "note": "Folga nao medida e timidez. Utilizacao baixa sem justificativa declarada "
                    "sugere hardware deixado na mesa; empurre a densidade ou declare por que "
                    "a direcao de arte, o level design ou outra premissa pede menos.",
        },
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
    ok = simulate({"sprites": [{"name": "hero", "x": 120, "y": 120, "w": 32, "h": 48}],
                   "headroom_justification": "fixture minima"})
    bad = simulate({"sprites": [{"name": f"s{i}", "x": 0, "y": 50, "w": 32, "h": 16, "sprite_links": 1} for i in range(21)]})
    # 16 sprites de 32px = 512px numa linha: passa na contagem (16 <= 20) e
    # estoura o orcamento de pixel. E o caso que a v1.0.0 nao enxergava.
    pixel_only = simulate({"sprites": [{"name": f"p{i}", "x": i * 8, "y": 60, "w": 32, "h": 16, "sprite_links": 1} for i in range(16)]})
    timid = simulate({"sprites": [{"name": "lone", "x": 10, "y": 10, "w": 16, "h": 16, "sprite_links": 1}]})
    h32 = simulate({"display_mode": "h32",
                    "sprites": [{"name": f"n{i}", "x": 0, "y": 40, "w": 16, "h": 16, "sprite_links": 1} for i in range(17)]})
    tall32 = simulate({"sprites": [{"name": "enemy", "x": 0, "y": 0, "w": 32, "h": 48}],
                       "headroom_justification": "fixture"})
    tall64 = simulate({"sprites": [{"name": "hero", "x": 0, "y": 0, "w": 64, "h": 96}],
                       "headroom_justification": "fixture"})

    if ok["status"] != "ok":
        print("self-check failed: simple scene rejected", file=sys.stderr)
        return 1
    if bad["status"] != "error" or "sprites_per_scanline_over_20" not in bad["blockers"]:
        print("self-check failed: scanline overflow not detected", file=sys.stderr)
        return 1
    if pixel_only["status"] != "error" or "sprite_pixels_per_scanline_over_320" not in pixel_only["blockers"]:
        print("self-check failed: pixel-per-scanline overflow not detected", file=sys.stderr)
        return 1
    if pixel_only["max_sprites_per_scanline"] > 20:
        print("self-check failed: pixel fixture should pass the count limit", file=sys.stderr)
        return 1
    if "unexploited_headroom" not in timid["warnings"]:
        print("self-check failed: unexploited headroom not flagged", file=sys.stderr)
        return 1
    if "unexploited_headroom" in ok["warnings"]:
        print("self-check failed: declared justification did not clear the warning", file=sys.stderr)
        return 1
    if h32["status"] != "error" or "sprites_per_scanline_over_16" not in h32["blockers"]:
        print("self-check failed: h32 limits not applied", file=sys.stderr)
        return 1
    if tall32["total_sprite_links"] != 2 or tall32["max_sprites_per_scanline"] != 1:
        print("self-check failed: 32x48 vertical cells counted on every scanline", file=sys.stderr)
        return 1
    if tall64["total_sprite_links"] != 6 or tall64["max_sprites_per_scanline"] != 2:
        print("self-check failed: 64x96 vertical cells counted on every scanline", file=sys.stderr)
        return 1
    print("vdp_scanline_simulator self-check passed (geometry cells + both limits + headroom + h32)")
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
