import sys
from PIL import Image

def to_md_color(c):
    return tuple(int(round(v / 36.0) * 36) for v in c)

def process_mission1(img_path):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    
    # Let's get the original transparent mask
    orig_p = Image.open(img_path)
    transparent_mask = [p == 0 for p in orig_p.getdata()]
    
    pixels = list(img.getdata())
    
    # Collect unique MD colors from the image
    unique_md = set()
    for c in pixels:
        unique_md.add(to_md_color(c))
    unique_md.discard((0,0,0)) # 0 will be transparent
    
    # Sort them (or whatever)
    md_palette = [(0,0,0)] + sorted(list(unique_md))
    if len(md_palette) > 16:
        # We need to drop some. Let's just keep the 15 most common
        from collections import Counter
        md_pixels = [to_md_color(c) for c in pixels]
        counts = Counter(md_pixels)
        del counts[(0,0,0)]
        most_common = [mc[0] for mc in counts.most_common(15)]
        md_palette = [(0,0,0)] + most_common
        
    print("MD Palette size:", len(md_palette))
    
    # We will map colors to the nearest md_palette color using Euclidean distance
    def nearest_color(c):
        best_dist = 1e9
        best_idx = 0
        for i, mc in enumerate(md_palette):
            if i == 0: continue # Skip transparent for normal pixels
            dist = sum((c[j] - mc[j])**2 for j in range(3))
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        return best_idx
        
    # Apply Floyd-Steinberg dithering
    # Convert pixels to a mutable 2D list
    img_data = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(list(pixels[y*w + x]))
        img_data.append(row)
        
    new_pixels = []
    
    for y in range(h):
        for x in range(w):
            if transparent_mask[y*w + x]:
                new_pixels.append(0)
                continue
                
            old_c = img_data[y][x]
            idx = nearest_color(old_c)
            new_c = md_palette[idx]
            new_pixels.append(idx)
            
            # Error diffusion
            err = [old_c[i] - new_c[i] for i in range(3)]
            
            if x + 1 < w and not transparent_mask[y*w + x + 1]:
                for i in range(3): img_data[y][x+1][i] += err[i] * 7 / 16.0
            if y + 1 < h:
                if x > 0 and not transparent_mask[(y+1)*w + x - 1]:
                    for i in range(3): img_data[y+1][x-1][i] += err[i] * 3 / 16.0
                if not transparent_mask[(y+1)*w + x]:
                    for i in range(3): img_data[y+1][x][i] += err[i] * 5 / 16.0
                if x + 1 < w and not transparent_mask[(y+1)*w + x + 1]:
                    for i in range(3): img_data[y+1][x+1][i] += err[i] * 1 / 16.0
                    
    # Rebuild palette for PIL
    flat_pal = []
    for c in md_palette:
        flat_pal.extend(c)
    flat_pal.extend([0] * (256 * 3 - len(flat_pal)))
    
    new_img = Image.new('P', (w, h))
    new_img.putpalette(flat_pal)
    new_img.putdata(new_pixels)
    new_img.save(img_path)
    print(f"Saved {img_path}")

process_mission1('F:/Projects/MegaDrive_DEV/SGDK_projects/METAL_SLUG_URBAN_SUNSET/res/gfx/mission1_skylift_bg_a.png')
