import os
from PIL import Image, ImageSequence

PROJECT_DIR = r"F:\Projects\MegaDrive_DEV\SGDK_projects\teste de conversão e animação de sprites [VER.001] [SGDK 211] [GEN] [AMOSTRA] [ANIMAÇÃO]"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
SPRITE_DIR = os.path.join(PROJECT_DIR, "res", "sprites")
BG_DIR = os.path.join(PROJECT_DIR, "res", "bgs")

os.makedirs(SPRITE_DIR, exist_ok=True)
os.makedirs(BG_DIR, exist_ok=True)

# Helper to crop a grid of frames
def crop_grid(image_path, frame_w, frame_h, num_frames, output_name):
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Failed to open {image_path}: {e}")
        return
    
    frames = []
    width, height = img.size
    cols = width // frame_w
    count = 0
    for y in range(0, height, frame_h):
        for x in range(0, width, frame_w):
            if count >= num_frames:
                break
            box = (x, y, x + frame_w, y + frame_h)
            frame = img.crop(box)
            frames.append(frame)
            count += 1
        if count >= num_frames:
            break
            
    # Save horizontally concatenated frames for SGDK (rescomp expects sprites to be laid out horizontally or vertically depending on SPRITE definition, but horizontal strip is easiest to manage)
    strip_w = frame_w * num_frames
    strip_h = frame_h
    strip = Image.new("RGBA", (strip_w, strip_h), (255, 0, 255, 255)) # Magenta BG
    
    for i, f in enumerate(frames):
        # We need to paste and respect transparency if any
        strip.paste(f, (i * frame_w, 0), f)
        
    out_path = os.path.join(SPRITE_DIR, f"{output_name}.png")
    strip = strip.convert("RGB").quantize(colors=16)
    strip.save(out_path)
    print(f"Saved sprite strip: {out_path}")

# Slice MetalSlug BG
bg_path = os.path.join(DATA_DIR, "MetalSlug_Backgrounds.png")
if os.path.exists(bg_path):
    img = Image.open(bg_path).convert("RGB")
    # Mega Drive resolution
    bg_frame = img.crop((0, 0, 320, 224))
    out_bg = os.path.join(BG_DIR, "bg_metal_slug.png")
    bg_frame = bg_frame.quantize(colors=16)
    bg_frame.save(out_bg)
    print(f"Saved BG: {out_bg}")

# Slice MegaMan (assuming small, let's grab 64x64 grid, 4 frames)
crop_grid(os.path.join(DATA_DIR, "MegaMan_pequeno.png"), 64, 64, 4, "spr_megaman")

# Slice Ken (usually 128x128)
crop_grid(os.path.join(DATA_DIR, "KenMasters_normal.png"), 128, 128, 4, "spr_ken")

# Slice Earthquake (large, try 128x128 or 256x256, SGDK sprite max size is 128x128 composed of 16 hardware sprites max, let's do 128x128)
crop_grid(os.path.join(DATA_DIR, "Earthquake_large.png"), 128, 128, 4, "spr_earthquake")

# Slice Blackheart GIF
bh_path = os.path.join(DATA_DIR, "Blackheart_grande.gif")
if os.path.exists(bh_path):
    try:
        img = Image.open(bh_path)
        frames = []
        for i, frame in enumerate(ImageSequence.Iterator(img)):
            if i >= 4:
                break
            # Convert to RGBA
            f = frame.convert("RGBA")
            # Resize or crop to 128x128
            f = f.crop((0, 0, 128, 128))
            frames.append(f)
            
        strip_w = 128 * len(frames)
        strip = Image.new("RGBA", (strip_w, 128), (255, 0, 255, 255))
        for i, f in enumerate(frames):
            strip.paste(f, (i * 128, 0), f)
        out_bh = os.path.join(SPRITE_DIR, "spr_blackheart.png")
        strip = strip.convert("RGB").quantize(colors=16)
        strip.save(out_bh)
        print(f"Saved GIF strip: {out_bh}")
    except Exception as e:
        print(f"Failed to process Blackheart: {e}")
