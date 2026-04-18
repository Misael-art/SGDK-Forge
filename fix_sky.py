import sys
from PIL import Image

def create_banded_sky(img_path):
    img = Image.open(img_path)
    w, h = img.size
    
    # Base color is [175, 208, 225]
    c0 = (0, 0, 0) # Transparent index 0
    c1 = (175, 208, 225) # Bottom
    c2 = (144, 180, 216) # Mid
    c3 = (108, 144, 180) # Top
    c4 = (72, 108, 144)  # Very top
    
    new_img = Image.new('P', (w, h))
    palette = list(c0) + list(c1) + list(c2) + list(c3) + list(c4)
    # Fill rest with 0s
    palette += [0] * (256 * 3 - len(palette))
    new_img.putpalette(palette)
    
    # Dither matrix 4x4 (Bayer)
    dither = [
        [ 0,  8,  2, 10],
        [12,  4, 14,  6],
        [ 3, 11,  1,  9],
        [15,  7, 13,  5]
    ]
    
    pixels = []
    for y in range(h):
        for x in range(w):
            d_val = dither[y % 4][x % 4] / 16.0
            
            if y < 40:
                idx = 4 # c4
            elif y < 80:
                val = (y - 40) / 40.0 # 0.0 to 1.0 (c4 to c3)
                idx = 3 if d_val > val else 4
            elif y < 140:
                val = (y - 80) / 60.0 # c3 to c2
                idx = 2 if d_val > val else 3
            elif y < 200:
                val = (y - 140) / 60.0 # c2 to c1
                idx = 1 if d_val > val else 2
            else:
                idx = 1 # c1
                
            pixels.append(idx)
            
    new_img.putdata(pixels)
    new_img.save(img_path)
    print(f"Updated {img_path}")

create_banded_sky('F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/res/gfx/urban_linefirst_balanced_bg_b.png')
