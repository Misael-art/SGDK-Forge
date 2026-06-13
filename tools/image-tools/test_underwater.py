import sys
from pathlib import Path
from PIL import Image
import json

src_path = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/underwater_scene/source/source.png")
src = Image.open(src_path).convert('RGB')
colors = src.getcolors(maxcolors=1024)

print(f"Size: {src.size}")
if not colors:
    print("More than 1024 colors!")
else:
    print(f"Total tight colors: {len(colors)}")
    sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
    for count, color in sorted_colors[:15]:
        print(f"Color {color}: {count} pixels")
