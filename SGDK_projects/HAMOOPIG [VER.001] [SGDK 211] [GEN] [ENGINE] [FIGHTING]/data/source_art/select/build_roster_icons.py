#!/usr/bin/env python3
"""Build a readable shared-palette roster rail from authored HUD portraits.

The three source portraits already carry the project's fighter identity. This
builder performs nearest-neighbor reduction to 24x24 and adds a thin
identity frame around each persisted portrait. All three icons can coexist in
one PAL0 sprite resource without consuming the preview palettes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/source_art/select/roster_icons_v01.png"
REPORT = ROOT / "data/source_art/select/roster_icons_v01_report.json"
ACTIVE = ROOT / "res/sprite/select/roster_icons.png"

SOURCES = {
    "ryo": ROOT / "res/sprite/hud/portrait_ryo.png",
    "ken": ROOT / "res/sprite/hud/portrait_ken.png",
    "musgo": ROOT / "res/sprite/hud/portrait_musgo.png",
}

# Index 0 is transparency. The visible ramp deliberately shares deep navy,
# cool blue, warm gold/orange and swamp green so the rail belongs to the
# selection surface and keeps all identities readable at 1x.
PALETTE = [
    (0, 0, 0),
    (0, 0, 34), (0, 34, 68), (34, 68, 102), (68, 102, 136),
    (102, 136, 170), (170, 170, 170), (238, 238, 204),
    (238, 170, 68), (204, 102, 34), (136, 68, 34), (102, 68, 34),
    (68, 102, 68), (136, 136, 102), (204, 204, 136), (238, 238, 238),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nearest(rgb: tuple[int, int, int]) -> int:
    return min(range(1, len(PALETTE)), key=lambda i: sum((rgb[c] - PALETTE[i][c]) ** 2 for c in range(3)))


FRAME_COLORS = (8, 5, 12)  # Ryo gold, Ken cool blue, Musgo swamp green


def convert(source: Path, frame_color: int) -> Image.Image:
    src = Image.open(source).convert("P")
    small = src.resize((24, 24), Image.Resampling.NEAREST)
    rgb = small.convert("RGB")
    out = Image.new("P", (24, 24), 0)
    for y in range(24):
        for x in range(24):
            value = small.getpixel((x, y))
            if value == 0:
                out.putpixel((x, y), 0)
            else:
                out.putpixel((x, y), nearest(tuple(rgb.getpixel((x, y)))))
    for x in range(2, 22):
        out.putpixel((x, 0), frame_color)
        out.putpixel((x, 23), frame_color)
    for y in range(2, 22):
        out.putpixel((0, y), frame_color)
        out.putpixel((23, y), frame_color)
    for x, y in ((0, 0), (1, 0), (0, 1), (23, 0), (22, 0), (23, 1),
                 (0, 23), (1, 23), (0, 22), (23, 23), (22, 23), (23, 22)):
        out.putpixel((x, y), 7)
    out.putpalette([channel for color in PALETTE for channel in color])
    return out


def main() -> None:
    rail = Image.new("P", (72, 24), 0)
    rail.putpalette([channel for color in PALETTE for channel in color])
    entries = []
    for slot, (name, source) in enumerate(SOURCES.items()):
        icon = convert(source, FRAME_COLORS[slot])
        rail.paste(icon, (slot * 24, 0))
        entries.append({
            "fighter": name,
            "source": str(source.relative_to(ROOT)),
            "source_sha256": sha256(source),
            "frame": slot,
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE.parent.mkdir(parents=True, exist_ok=True)
    rail.save(OUT, optimize=False, transparency=0)
    ACTIVE.write_bytes(OUT.read_bytes())
    report = {
        "schema_version": "1.0.0",
        "kind": "procedural_composed_from_authored",
        "purpose": "selection roster rail, three framed 24x24 identity icons, shared PAL0",
        "source_kind": "existing authored HUD portraits",
        "output": str(OUT.relative_to(ROOT)),
        "active_output": str(ACTIVE.relative_to(ROOT)),
        "output_sha256": sha256(OUT),
        "dimensions": [72, 24],
        "frame_size": [24, 24],
        "palette_entries": len(PALETTE),
        "index0_role": "transparent",
        "entries": entries,
        "acceptance_status": "placeholder",
        "visual_review_required": True,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
