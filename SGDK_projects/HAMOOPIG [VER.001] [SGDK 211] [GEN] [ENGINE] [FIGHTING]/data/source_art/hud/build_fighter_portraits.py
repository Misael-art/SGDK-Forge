"""Translate authored fighter frames into deliberate 24x24 HUD portraits.

The source frames are the project's existing authored/native fighter art.  The
crop coordinates are explicit by design: these are head-and-shoulder identity
panels, not automatic miniatures of the full body.  Nearest scaling preserves
the native pixel language and the source hashes are written into the report.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "res" / "sprite" / "hud"
REPORT = ROOT / "rascunho" / "fighter_portrait_translation_report.json"

# One idle frame per fighter.  The crop boxes were chosen by visual inspection
# at native size; each box includes the face, shoulders, and character cue.
SOURCES = {
    # The source sheet is a 64x104 native cell. These upper-body windows keep
    # the face and shoulders while filling the 32x32 HUD card at native scale.
    "ryo": (ROOT / "res" / "sprite" / "ryo" / "100.png", (0, 0, 32, 40)),
    "ken": (ROOT / "res" / "sprite" / "ken" / "100.png", (0, 0, 32, 40)),
    "musgo": (ROOT / "res" / "sprite" / "musgo" / "100.png", (0, 0, 40, 48)),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def convert(name: str, source: Path, box: tuple[int, int, int, int]) -> dict:
    # Keep the fighter's native index order: PAL2/PAL3 are loaded by the
    # fighter system and the portrait must read with that exact palette.
    image = Image.open(source).convert("P")
    crop = image.crop(box)
    # Source sheets use magenta as the transparent key. Keep it at index 0.
    crop = crop.resize((32, 32), Image.Resampling.NEAREST)
    indexed = crop
    palette = indexed.getpalette()[: 768]
    # Native sheets already use index 0 as magenta transparency.
    indexed.putpalette(palette + [0] * (768 - len(palette)))
    output = OUT / f"portrait_{name}.png"
    indexed.save(output, optimize=False)
    return {
        "fighter": name,
        "source": str(source.relative_to(ROOT)),
        "source_sha256": sha256(source),
        "crop_box_native": list(box),
        "output": str(output.relative_to(ROOT)),
        "output_sha256": sha256(output),
        "dimensions": [32, 32],
        "colors": len(set(indexed.getdata())),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "kind": "procedural_composed_from_authored",
        "purpose": "native 24x24 identity portraits for the fight HUD",
        "entries": [convert(name, *spec) for name, spec in SOURCES.items()],
    }
    # Reuse the authored HUD segment geometry but assign the existing PAL1
    # blue accent (index 9) to the special meter.  This is a composed asset,
    # not a runtime primitive, and keeps life/special semantics distinct.
    source_segment = ROOT / "res" / "sprite" / "hud" / "energy_yellow_segment.png"
    palette_source = Image.open(ROOT / "res" / "sprite" / "hud" / "energy_yellow.png").convert("P")
    source_special = Image.open(source_segment).convert("P")
    # The segment PNG is intentionally compact and only carries its used
    # colors. Reuse the complete PAL1 source palette before assigning index 9;
    # otherwise index 9 would decode as black at runtime.
    source_special.putpalette(palette_source.getpalette())
    source_special.putdata([9 if value == 2 else value for value in source_special.getdata()])
    # Two authored states share the same 16x8 cell geometry: a dim blue
    # track for empty capacity and a brighter cyan fill for charged capacity.
    # Keeping both in one TILESET makes the runtime swap a tile pair instead
    # of painting black holes into BG_A when the meter is empty.
    # Both states are opaque on purpose: transparent index 0 would reveal the
    # default BG_A tile (black) and turn an empty meter into eight black holes.
    special = Image.new("P", (32, 8), 9)
    special.putpalette(palette_source.getpalette())
    special.putdata([9 for _ in source_special.getdata()])
    filled = Image.new("P", (16, 8), 9)
    filled.putpalette(palette_source.getpalette())
    filled.putdata([14 for _ in source_special.getdata()])
    special.paste(filled, (16, 0))
    special.save(OUT / "special_blue_segment.png", optimize=False)
    report["special_segment"] = {
        "source": str(source_segment.relative_to(ROOT)),
        "source_sha256": sha256(source_segment),
        "output": "res/sprite/hud/special_blue_segment.png",
        "output_sha256": sha256(OUT / "special_blue_segment.png"),
        "dimensions": [32, 8],
        "empty_palette_index": 9,
        "filled_palette_index": 14,
        "palette_role": "PAL1 opaque navy track plus bright-cyan fill",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
