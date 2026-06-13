import sys
from pathlib import Path
from PIL import Image

base_dir = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/underwater_scene/source")

def extract_colors(img_path):
    img = Image.open(img_path).convert('RGBA')
    colors = set()
    for px in img.getdata():
        if px[3] > 128:  # consider only opaque
            colors.add((px[0], px[1], px[2]))
    return colors

far_colors = extract_colors(base_dir / "layers" / "far.png")
sand_colors = extract_colors(base_dir / "layers" / "sand.png")
fg_colors = extract_colors(base_dir / "layers" / "foregound-merged.png")

print(f"Far colors ({len(far_colors)}): {far_colors}")
print(f"Sand colors ({len(sand_colors)}): {sand_colors}")
print(f"FG colors ({len(fg_colors)}): {fg_colors}")

intersection_far_sand = far_colors.intersection(sand_colors)
intersection_sand_fg = sand_colors.intersection(fg_colors)

print(f"Shared Far-Sand: {intersection_far_sand}")
print(f"Shared Sand-FG: {intersection_sand_fg}")
