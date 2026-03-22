from pathlib import Path

from PIL import Image, ImageSequence

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
SPRITE_DIR = PROJECT_DIR / "res" / "sprites"
BG_DIR = PROJECT_DIR / "res" / "bgs"

SPRITE_DIR.mkdir(parents=True, exist_ok=True)
BG_DIR.mkdir(parents=True, exist_ok=True)

# Legacy helper kept for manual experiments.
# The canonical path for this repository is the shared sgdk_wrapper pipeline.
def crop_grid(image_path, frame_w, frame_h, num_frames, output_name):
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception as e:
        print(f"Failed to open {image_path}: {e}")
        return

    frames = []
    width, height = img.size
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

    strip_w = frame_w * num_frames
    strip_h = frame_h
    strip = Image.new("RGBA", (strip_w, strip_h), (255, 0, 255, 255))

    for i, frame in enumerate(frames):
        strip.paste(frame, (i * frame_w, 0), frame)

    out_path = SPRITE_DIR / f"{output_name}.png"
    strip = strip.convert("RGB").quantize(colors=16)
    strip.save(out_path)
    print(f"Saved sprite strip: {out_path}")


bg_path = DATA_DIR / "MetalSlug_Backgrounds.png"
if bg_path.exists():
    img = Image.open(bg_path).convert("RGB")
    bg_frame = img.crop((0, 0, 320, 224))
    out_bg = BG_DIR / "bg_metal_slug.png"
    bg_frame = bg_frame.quantize(colors=16)
    bg_frame.save(out_bg)
    print(f"Saved background: {out_bg}")

crop_grid(DATA_DIR / "MegaMan_pequeno.png", 64, 64, 4, "spr_megaman")
crop_grid(DATA_DIR / "KenMasters_normal.png", 128, 128, 4, "spr_ken")
crop_grid(DATA_DIR / "Earthquake_large.png", 128, 128, 4, "spr_earthquake")

bh_path = DATA_DIR / "Blackheart_grande.gif"
if bh_path.exists():
    try:
        img = Image.open(bh_path)
        frames = []
        for i, frame in enumerate(ImageSequence.Iterator(img)):
            if i >= 4:
                break
            rgba = frame.convert("RGBA")
            rgba = rgba.crop((0, 0, 128, 128))
            frames.append(rgba)

        strip_w = 128 * len(frames)
        strip = Image.new("RGBA", (strip_w, 128), (255, 0, 255, 255))
        for i, frame in enumerate(frames):
            strip.paste(frame, (i * 128, 0), frame)

        out_bh = SPRITE_DIR / "spr_blackheart.png"
        strip = strip.convert("RGB").quantize(colors=16)
        strip.save(out_bh)
        print(f"Saved GIF strip: {out_bh}")
    except Exception as e:
        print(f"Failed to process Blackheart: {e}")
