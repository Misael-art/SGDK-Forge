#!/usr/bin/env python3
"""Authorial 1:1 pixel stamp for TAÍNA's native lineart blocking.

The raster below is an explicit hand-authored mark map.  It is intentionally
not a downscale, trace, crop, quantization, primitive drawing, or repair of a
rejected candidate.  Six 8px columns by eight 8px rows are kept visible in the
source notation so the authoring canvas remains auditable as a 48x64 VDP grid.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / "data/processed/characters/taina/lineart/taina_reseed_native_lineart_48x64_v01.png"
REPORT = PROJECT / "doc/art/characters/taina/native_author_stamp_report_v01.json"

# One row is six 8px stamps separated by '|'. '#' is the single temporary ink
# color; '.' is the transparent authoring matte.  No shape primitive is used.
BANDS = [
    [
        "........|........|....##..|..##....|........|........",
        "........|......##|..####..|..####..|........|........",
        ".......#|....####|.######.|.######.|..#.....|........",
        "......##|...#####|########|########|##......|........",
        ".....###|..######|########|########|###.....|........",
        ".....###|.#######|########|########|####....|........",
        "....####|.#######|########|########|#####...|........",
        "....####|..#####.|########|########|####....|........",
    ],
    [
        "....####|..#####.|########|########|####....|........",
        "....####|.#######|########|########|####....|........",
        "....###.|..######|########|########|###.....|........",
        ".....##.|...#####|..####..|.#####..|##......|........",
        "......#.|...####.|.######.|.#####..|.#......|........",
        "........|....###.|.######.|.####...|........|........",
        "........|....###.|..####..|..###...|........|........",
        "........|.....##.|..####..|...##...|........|........",
    ],
    [
        ".....###|...####.|..####..|...###..|........|........",
        "....####|..#####.|.##..##.|..####..|........|........",
        "....####|..#####.|.##..##.|.######.|..##....|........",
        ".....###|...##.##|.######.|.##.##..|..###...|........",
        "........|..##.##.|..####..|.##.##..|.#####..|........",
        "........|..#####.|..####..|..#####.|..###...|........",
        "........|...####.|...##...|...####.|...##...|........",
        "........|....##..|...##...|....##..|....#...|........",
    ],
    [
        ".....#..|....##..|..####..|...##...|....#...|........",
        "....###.|....###.|.######.|..####..|...###..|........",
        "....###.|...####.|########|.#####..|...###..|........",
        "....##..|...####.|########|.#####..|...##...|........",
        "...###..|...####.|########|.#####..|..###...|........",
        "...##...|....###.|.######.|..####..|..##....|........",
        "..###...|.....##.|..####..|...##...|.###....|........",
        "..##....|......#.|...##...|....#...|.##.....|........",
    ],
    [
        "........|......##|..####..|..##....|........|........",
        "........|.....###|########|.###....|.......#|........",
        ".......#|.....###|########|.###....|......##|........",
        "......##|......##|########|.##.....|.....###|........",
        ".....###|......##|########|..##....|....####|........",
        "....####|.....###|.######.|...##...|...#####|........",
        "...#####|.....###|..####..|....#...|..####..|........",
        "...####.|......##|...##...|........|..###...|........",
    ],
    [
        "..#####.|...####.|..####..|..####..|.#####..|........",
        ".######.|..######|.######.|.######.|######..|........",
        ".#####..|..######|########|.######.|.#####..|........",
        "..####..|..#####.|########|.#####..|..####..|........",
        "..####..|..#####.|########|.#####..|..####..|........",
        "..###...|...####.|########|..####..|...###..|........",
        "..###...|....###.|.######.|...###..|...##...|........",
        "..##....|....##..|..####..|....##..|...##...|........",
    ],
    [
        "..###...|...###..|..####..|..###...|...##...|........",
        "..###...|...###..|..####..|..###...|...##...|........",
        "..##....|...###..|..####..|...###..|...##...|........",
        "..##....|....##..|..####..|....##..|...##...|........",
        "..##....|....##..|..####..|....##..|...##...|........",
        "..##....|....##..|..####..|....##..|...##...|........",
        "...#....|....##..|...##...|....#...|....#...|........",
        "........|....#...|...##...|........|........|........",
    ],
    [
        "........|....##..|...##...|........|........|........",
        "........|....##..|...##...|........|........|........",
        "........|...###..|...###..|........|........|........",
        ".......#|..#####.|..#####.|.....#..|........|........",
        "......##|.######.|.######.|....##..|........|........",
        ".....###|..####..|..####..|...###..|........|........",
        "....####|........|........|..####..|........|........",
        "....###.|........|........|..###...|........|........",
    ],
]


def expand_stamp_grid() -> list[str]:
    rows: list[str] = []
    for band in BANDS:
        if len(band) != 8:
            raise ValueError("cada banda deve ter 8 linhas")
        for row in band:
            parts = row.split("|")
            if len(parts) != 6 or any(len(part) != 8 for part in parts):
                raise ValueError(f"linha fora da grade 6x8: {row!r}")
            if any(char not in ".#" for char in row.replace("|", "")):
                raise ValueError(f"caractere nao autorado: {row!r}")
            rows.append("".join(parts))
    if len(rows) != 64 or any(len(row) != 48 for row in rows):
        raise ValueError("canvas nativo nao e 48x64")
    return rows


def main() -> None:
    rows = expand_stamp_grid()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    # Index 0 is the transparent slot.  Its RGB entry is VDP-grid black; the
    # authoring matte is conceptually magenta and is not emitted as visible art.
    img = Image.new("P", (48, 64), 0)
    img.putpalette([0x00, 0x00, 0x00, 0x22, 0x00, 0x22])
    indices = [1 if char == "#" else 0 for row in rows for char in row]
    img.putdata(indices)
    img.info["transparency"] = 0
    img.save(OUT, "PNG", bits=4, transparency=0)

    ink = sum(indices)
    REPORT.write_text(json.dumps({
        "schema_version": "1.0.0",
        "report_id": "taina_native_author_stamp_v01",
        "status": "authored_native_candidate",
        "route": "author_stamp_8x8_grid",
        "source_of_truth": "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png",
        "source_policy": "approved_model_sheet_only; rejected_candidates_not_read",
        "output": "data/processed/characters/taina/lineart/taina_reseed_native_lineart_48x64_v01.png",
        "canvas_px": {"w": 48, "h": 64},
        "tile_grid": {"cols": 6, "rows": 8, "tile_px": 8},
        "scale": "1:1",
        "ink_model": "single hard-edge 1px temporary dark ink",
        "transparent_slot": {"index": 0, "authoring_matte": "magenta_key_only", "png_encoding": "tRNS index 0"},
        "ink_pixels": ink,
        "checks_before_pixel_contract": {
            "dimensions_multiple_of_8": True,
            "anti_aliasing": False,
            "interpolation": False,
            "trace_or_crop_of_rejected_candidate": False,
            "procedural_primitives": False,
        },
        "next_owner": "megadrive-pixel-strict-rules",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
