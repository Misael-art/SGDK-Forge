#!/usr/bin/env python3
"""Quick check: does the source panorama have opaque pixels where the human reference does?"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))

from PIL import Image
from generate_metal_slug_translation_case import (
    crop_resize_runtime, SOURCE_PATH, MANUAL_BG_A_PATH, MANUAL_FG_PATH,
    RUNTIME_SCENE_CROP
)

source = Image.open(SOURCE_PATH).convert("RGBA")
pano_source = crop_resize_runtime(source)
w, h = pano_source.size
print(f"Panorama source size: {w}x{h}")

human_bga = crop_resize_runtime(Image.open(MANUAL_BG_A_PATH).convert("RGBA"))
human_fg = crop_resize_runtime(Image.open(MANUAL_FG_PATH).convert("RGBA"))

print(f"\nRUNTIME_SCENE_CROP = {RUNTIME_SCENE_CROP}")
print(f"Source.png size: {source.size}")

raw_crop = source.crop(RUNTIME_SCENE_CROP)
extrema = raw_crop.convert("RGBA").getextrema()
print(f"Raw crop alpha extrema: min={extrema[3][0]}, max={extrema[3][1]}")

bands = 8
bh = h // bands
print(f"\n{'Band':>12} | {'SRC opaque':>12} | {'HUMAN_A opaque':>14} | {'HUMAN_FG opaque':>15}")
print("-" * 70)
spx = pano_source.load()
hpx = human_bga.load()
fpx = human_fg.load()

for band in range(bands):
    y0 = band * bh
    y1 = min((band + 1) * bh, h)
    src_op = hu_op = fg_op = total = 0
    for y in range(y0, y1):
        for x in range(w):
            total += 1
            if spx[x, y][3] > 0: src_op += 1
            if hpx[x, y][3] > 0: hu_op += 1
            if fpx[x, y][3] > 0: fg_op += 1
    pct = lambda n: f"{n*100//max(1,total)}%"
    label = f"y={y0:>3}-{y1:>3}"
    print(f"{label:>12} | {src_op:>5} ({pct(src_op):>4}) | {hu_op:>5} ({pct(hu_op):>5}) | {fg_op:>5} ({pct(fg_op):>5})")

# Also: sample some pixels from the bottom of each
print("\n--- Sample pixels from bottom row (y=220) ---")
for x in [50, 150, 292, 400, 500]:
    sr, sg, sb, sa = spx[x, 220]
    hr, hg, hb, ha = hpx[x, 220]
    fr, fg_, fb, fa = fpx[x, 220]
    print(f"  x={x}: SRC=({sr},{sg},{sb},a={sa})  HUMAN_A=({hr},{hg},{hb},a={ha})  HUMAN_FG=({fr},{fg_},{fb},a={fa})")
