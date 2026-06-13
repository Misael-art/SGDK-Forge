import sys
import os
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageColor
import numpy as np

sys.path.append(str(Path("F:/Projects/MegaDev_DEV/tools/image-tools")))  # If needed for global imports, but we will write standalone matrix math

SRC = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/level_tilemaps/PlayStation - Castlevania_ Symphony of the Night - Maps - Underground Caverns (B).png")
OUT = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/level_tilemaps/reports/pilot_sotn")
OUT.mkdir(parents=True, exist_ok=True)

CROP_BOX = (4000, 0, 4512, 512) # x1, y1, x2, y2 (512x512 crop)

def snap_to_md(value):
    """Snaps a single channel 0-255 to Mega Drive /34 grid."""
    return min(255, round(value / 34) * 34)

def simulate_md_highlight(base_rgb):
    """Mega Drive Highlight operator: doubles luminance roughly (+ Luma)"""
    r, g, b = base_rgb
    # In hardware, Highlight acts as if the color was rendered at normal intensity over normal TV, 
    # but the VDP forces the intensity of underlying pixels.
    # An approximation: r = min(255, r + 85)
    return (min(255, r + 136), min(255, g + 136), min(255, b + 136)) # Rough approximation for +50% brightness

def simulate_md_shadow(base_rgb):
    """Mega Drive Shadow operator: half intensity (- Luma)"""
    r, g, b = base_rgb
    return (r // 2, g // 2, b // 2)

def extract_base_and_light_maps(img, water_threshold_b=150, light_threshold=180, shadow_threshold=60):
    """
    Decomposes the image into:
    1. Base Tile Image (quantized to 2 palettes: Rock vs Water)
    2. Shadow Map (1-bit mask)
    3. Highlight Map (1-bit mask)
    """
    img = img.convert("RGB")
    width, height = img.size
    
    # Create mask images
    highlight_mask = Image.new("1", (width, height), 0)
    shadow_mask = Image.new("1", (width, height), 0)
    
    # We will build two arrays to quantize them later separately
    rock_pixels = []
    water_pixels = []
    
    # Arrays holding pixel coordinates for later reconstruction
    pixel_data = np.array(img)
    
    # 1. Analyze Pass
    for y in range(height):
        for x in range(width):
            r, g, b = pixel_data[y, x]
            
            # Simple heuristic for "Luma" perceived brightness
            luma = 0.299*r + 0.587*g + 0.114*b
            
            # Highlight Detection (very bright cyan/white water fx or lights)
            if luma > light_threshold:
                highlight_mask.putpixel((x, y), 1)
                # Reverse engineer the base color underneath the light (approximate - subtract some brightness)
                base_r = max(0, int(r) - 85)
                base_g = max(0, int(g) - 85)
                base_b = max(0, int(b) - 85)
            # Shadow Detection (very dark crevices)
            elif luma < shadow_threshold and luma > 5: # exclude pure black borders if any
                shadow_mask.putpixel((x, y), 1)
                # Reverse engineer the base color (approximate - double the shadow)
                base_r = min(255, int(r) * 2)
                base_g = min(255, int(g) * 2)
                base_b = min(255, int(b) * 2)
            else:
                base_r, base_g, base_b = int(r), int(g), int(b)
            
            # Classify into Rock vs Water Palette spaces
            # SOTN caverns water is predominantly blue/cyanish.
            if base_b > base_r + 20 and base_b > water_threshold_b:
                water_pixels.append((base_r, base_g, base_b))
            else:
                rock_pixels.append((base_r, base_g, base_b))
                
    return rock_pixels, water_pixels, shadow_mask, highlight_mask

def create_palette_image(colors, max_len=15):
    """K-Means clustering mock via PIL adaptive palette to extract representative palette"""
    if not colors:
        return []
        
    flat = []
    for c in colors:
        flat.extend(c)
        
    # We can use PIL to quantize an image made of these colors
    # Make a square image from colors
    side = int(np.ceil(np.sqrt(len(colors))))
    temp_img = Image.new("RGB", (side, side))
    put_data = []
    for i in range(side * side):
        if i < len(colors): put_data.append(colors[i])
        else: put_data.append((0,0,0))
    temp_img.putdata(put_data)
    
    # Quantize to 15 colors
    quant = temp_img.quantize(colors=max_len, method=Image.Quantize.MEDIANCUT)
    return quant.getpalette()[:15*3]

def apply_md_simulation(base_rgb_img, shadow_mask, highlight_mask):
    """Reconstructs the virtual Mega Drive output"""
    result = Image.new("RGB", base_rgb_img.size)
    base_data = np.array(base_rgb_img)
    sh_data = np.array(shadow_mask)
    hl_data = np.array(highlight_mask)
    
    out_data = np.zeros_like(base_data)
    
    h, w = base_rgb_img.size
    for y in range(w):  # height
        for x in range(h): # width
            r, g, b = base_data[y, x]
            
            # Mega Drive Snap Base color unconditionally down to /34
            md_r, md_g, md_b = snap_to_md(r), snap_to_md(g), snap_to_md(b)
            
            if hl_data[y, x]:
                # Apply Hardware Highlight
                out_data[y, x] = simulate_md_highlight((md_r, md_g, md_b))
            elif sh_data[y, x]:
                # Apply Hardware Shadow
                out_data[y, x] = simulate_md_shadow((md_r, md_g, md_b))
            else:
                out_data[y, x] = (md_r, md_g, md_b)
                
    result = Image.fromarray(out_data.astype('uint8'), 'RGB')
    return result

def run():
    print("="*60)
    print("LEVEL TILEMAP AAA CURATION PILOT (Highlight/Shadow)")
    print("="*60)
    
    # 1. Crop original slice
    master = Image.open(SRC).convert("RGB")
    slice_img = master.crop(CROP_BOX)
    slice_img.save(OUT / "01_original_ps1_slice.png")
    print(f"[OK] Recorte {CROP_BOX} extraído.")
    
    # 2. Extract Base maps
    rock_px, water_px, shadow_mask, highlight_mask = extract_base_and_light_maps(slice_img)
    
    shadow_mask.save(OUT / "02_shadow_mask_1bit.png")
    highlight_mask.save(OUT / "03_highlight_mask_1bit.png")
    print(f"[OK] Máscaras de Volume/Luz isoladas.")
    
    # 3. Quantize base palettes
    rock_pal = create_palette_image(rock_px, 15)
    water_pal = create_palette_image(water_px, 15)
    print(f"[OK] Paletas Rock (N={len(rock_px)}) e Water (N={len(water_px)}) inferidas.")
    
    # 4. Generate the Base Quantized Tile Image
    # For the pilot, we'll just snap the base colors to the nearest in our rock/water combined space.
    # To keep the script fast, PIL can quantize using the combined palette.
    combined_pal = rock_pal + water_pal
    if len(combined_pal) < 256 * 3:
        combined_pal += [0] * (256 * 3 - len(combined_pal))
        
    pal_img = Image.new("P", (1,1))
    pal_img.putpalette(combined_pal)
    
    # Snap the original to our 30 colors
    quant_base = slice_img.quantize(palette=pal_img, dither=Image.Dither.NONE)
    base_rgb = quant_base.convert("RGB")
    base_rgb.save(OUT / "04_base_tilemap_30colors.png")
    print("[OK] Tilemap Base chapado (sem efeitos, 30 cores) gerado.")
    
    # 5. Virtual Hardware Prove
    proof_img = apply_md_simulation(base_rgb, shadow_mask, highlight_mask)
    proof_img.save(OUT / "05_virtual_megadrive_proof.png")
    print("[OK] Prova Virtual Mega Drive Renderizada com H/S Nativo!")

if __name__ == "__main__":
    run()
