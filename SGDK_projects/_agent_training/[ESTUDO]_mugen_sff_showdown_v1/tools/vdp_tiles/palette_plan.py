from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PalettePlanResult:
    tile_palette_id: list[int]
    palettes: list[list[int]]
    violations: list[dict[str, int]]


def plan_4palettes_for_tiles(tile_color_sets: list[set[int]]) -> PalettePlanResult:
    palettes: list[set[int]] = [set() for _ in range(4)]
    tile_palette_id: list[int] = []
    violations: list[dict[str, int]] = []

    for tile_index, colors in enumerate(tile_color_sets):
        if len(colors) > 16:
            violations.append({"tile_index": int(tile_index), "reason": 1, "color_count": int(len(colors))})
            tile_palette_id.append(0)
            continue

        placed = False
        for pid in range(4):
            merged = palettes[pid] | colors
            if len(merged) <= 16:
                palettes[pid] = merged
                tile_palette_id.append(pid)
                placed = True
                break

        if not placed:
            violations.append({"tile_index": int(tile_index), "reason": 2, "color_count": int(len(colors))})
            tile_palette_id.append(0)

    ordered_palettes = [sorted(p) for p in palettes]
    return PalettePlanResult(tile_palette_id=tile_palette_id, palettes=ordered_palettes, violations=violations)
