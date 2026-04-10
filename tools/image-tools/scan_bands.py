import sys
from pathlib import Path
from PIL import Image

def find_fighting_stance_bbox():
    src_path = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/fighters_gaira_anim/reports/inspect_top.png")
    img = Image.open(src_path).convert("RGBA")
    
    # We know the fighting stance is somewhere between Y=400 and Y=600 based on average sprite sheet layout.
    # Let's write a simple bounding box scanner:
    # 1. Project alpha values horizontally
    w, h = img.size
    px = img.load()
    rows = []
    for y in range(h):
        has_pixel = False
        for x in range(w):
            if px[x, y][3] > 0:
                has_pixel = True
                break
        rows.append(has_pixel)
        
    # Find contiguous bands of pixels
    bands = []
    in_band = False
    start = 0
    for y, has_px in enumerate(rows):
        if has_px and not in_band:
            in_band = True
            start = y
        elif not has_px and in_band:
            in_band = False
            bands.append((start, y))
            
    print("Found pixel bands (Y-axis):")
    for b in bands:
        print(f"Band {b}: Height = {b[1]-b[0]}")

if __name__ == "__main__":
    find_fighting_stance_bbox()
