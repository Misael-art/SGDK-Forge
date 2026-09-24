#!/usr/bin/env python3
"""Static contract for the authored wide Stage 2 candidate."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "res/gfx/bgb2.png"
    report = json.loads((ROOT / "data/source_art/stage2_swamp/convert_stage2_report.json").read_text())
    im = Image.open(path)
    assert im.mode == "P" and im.size == (512, 256)
    indices = set(im.get_flattened_data())
    assert indices and 0 not in indices and max(indices) <= 14
    palette = im.getpalette()
    assert all(palette[3 * i + c] % 34 == 0 for i in indices for c in range(3))
    assert report["output_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert report["source_sha256"] == hashlib.sha256((ROOT / report["source"]).read_bytes()).hexdigest()
    assert report["unique_tiles_after_reuse"] <= report["tile_budget"] == 864
    print("PASS: Stage 2 512x256, opaque 9-bit palette and 864-tile ceiling")


if __name__ == "__main__":
    main()
