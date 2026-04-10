import sys
from pathlib import Path
from PIL import Image

sys.path.append(str(Path("F:/Projects/MegaDrive_DEV/tools/image-tools")))
import sgdk_semantic_parser

src_path = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/fighters_gaira_anim/source.png")

def inspect():
    img = Image.open(src_path).convert("RGBA")
    
    # Run chromakey to remove purple bg. Left-top is part of the "Selection" banner, let's use
    # a safe pixel near the left margin below the banners.
    px = img.load()
    key_color = (px[10, 500][0], px[10, 500][1], px[10, 500][2])
    print(f"Detected Background Key Color: {key_color}")

    # Let's do a fast crop just of the top 800 pixels and save it transparent to let me see it.
    cropped = img.crop((0, 0, img.width, 1400))
    alpha_img = sgdk_semantic_parser.chromakey_to_alpha(cropped, key_color=key_color)
    
    out_dir = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/fighters_gaira_anim/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "inspect_top.png"
    alpha_img.save(out_path)
    print(f"Saved investigative crop to {out_path}")

if __name__ == "__main__":
    inspect()
