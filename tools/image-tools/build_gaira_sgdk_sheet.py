"""
build_gaira_sgdk_sheet.py — Asset pipeline for Gaira fighter sprite sheet.

Reads 5 pre-assembled action strips from the Gaira translation case,
scales them to Mega Drive resolution, normalizes cell sizes, quantizes
to 15 indexed colors on the 9-bit VDP grid, and outputs a single
SGDK-compliant sprite sheet.

Output: SGDK_projects/BENCHMARK_VISUAL_LAB/res/sprites/spr_gaira.png
Format: 8-bit indexed PNG, index 0 = magenta (#FF00FF), 15 visible colors,
        all RGB values snapped to multiples of 0x22 (9-bit MD color space).
        5 rows (animations) x N columns (max frames), same cell size.

Usage:
    python build_gaira_sgdk_sheet.py
"""

import os
import sys
from pathlib import Path

# Add parent for sgdk_semantic_parser import
sys.path.insert(0, str(Path(__file__).parent))
import sgdk_semantic_parser as ssp
from PIL import Image

# --- Configuration ---

STRIPS_DIR = Path(__file__).parent.parent.parent / \
    "assets/reference/translation_curation/fighters_gaira_anim/reports/gaira_assembled_strips"

OUTPUT_PATH = Path(__file__).parent.parent.parent / \
    "SGDK_projects/BENCHMARK_VISUAL_LAB/res/sprites/spr_gaira.png"

# Strip selection: (filename, semantic_name, expected_frames)
# Selected by visual analysis of 100 assembled strips
STRIP_MAP = [
    ("strip_action_02.png",  "idle",         6),
    ("strip_action_11.png",  "walk",         8),
    ("strip_action_04.png",  "attack_light", 5),
    ("strip_action_110.png", "hurt",         2),
    ("strip_action_69.png",  "jump",         3),
]

# Target cell size for Mega Drive (must be multiples of 8)
TARGET_CELL_W = 56   # 7 tiles wide
TARGET_CELL_H = 72   # 9 tiles tall

MAGENTA = (255, 0, 255)
MAX_COLORS = 15


def load_strip_frames(strip_path: Path, expected_frames: int) -> list[Image.Image]:
    """Load a strip and split into individual RGBA frames."""
    strip = Image.open(strip_path).convert("RGBA")
    w, h = strip.size

    # Estimate frame count from aspect ratio if strip is horizontal
    if expected_frames > 0:
        frame_w = w // expected_frames
    else:
        frame_w = h  # assume square cells
        expected_frames = w // frame_w

    frames = []
    for i in range(expected_frames):
        x0 = i * frame_w
        x1 = min(x0 + frame_w, w)
        frame = strip.crop((x0, 0, x1, h))
        frames.append(frame)

    return frames


def scale_frame_to_cell(frame: Image.Image, cell_w: int, cell_h: int) -> Image.Image:
    """Scale a frame to fit within cell_w x cell_h, preserving aspect ratio,
    then center-bottom align into the cell."""
    fw, fh = frame.size

    # Scale to fit within cell, preserving aspect
    scale = min(cell_w / fw, cell_h / fh)
    new_w = max(1, int(fw * scale))
    new_h = max(1, int(fh * scale))

    scaled = frame.resize((new_w, new_h), Image.Resampling.NEAREST)

    # Create cell canvas and paste bottom-center
    cell = Image.new("RGBA", (cell_w, cell_h), (0, 0, 0, 0))
    paste_x = (cell_w - new_w) // 2
    paste_y = cell_h - new_h  # bottom align
    cell.alpha_composite(scaled, (paste_x, paste_y))

    return cell


def build_sheet():
    """Main pipeline: load strips, scale, normalize, quantize, save."""
    print(f"[Pipeline] Strips dir: {STRIPS_DIR}")
    print(f"[Pipeline] Output: {OUTPUT_PATH}")
    print(f"[Pipeline] Target cell: {TARGET_CELL_W}x{TARGET_CELL_H} ({TARGET_CELL_W//8}x{TARGET_CELL_H//8} tiles)")

    all_anim_frames = []
    max_frame_count = 0

    # Phase 1: Load and scale all frames
    for filename, name, expected in STRIP_MAP:
        strip_path = STRIPS_DIR / filename
        if not strip_path.exists():
            print(f"[ERROR] Strip not found: {strip_path}")
            sys.exit(1)

        frames = load_strip_frames(strip_path, expected)
        print(f"  [{name}] {filename}: {len(frames)} frames loaded ({Image.open(strip_path).size})")

        # Scale each frame to target cell
        scaled = [scale_frame_to_cell(f, TARGET_CELL_W, TARGET_CELL_H) for f in frames]
        all_anim_frames.append((name, scaled))
        max_frame_count = max(max_frame_count, len(scaled))

    print(f"[Pipeline] Max frames per anim: {max_frame_count}")
    print(f"[Pipeline] Sheet dimensions: {TARGET_CELL_W * max_frame_count}x{TARGET_CELL_H * len(STRIP_MAP)}")

    # Phase 2: Pad shorter animations by duplicating last frame
    for i, (name, frames) in enumerate(all_anim_frames):
        while len(frames) < max_frame_count:
            frames.append(frames[-1].copy())
        all_anim_frames[i] = (name, frames)

    # Phase 3: Assemble full sheet (rows=anims, cols=frames)
    sheet_w = TARGET_CELL_W * max_frame_count
    sheet_h = TARGET_CELL_H * len(all_anim_frames)
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    for row, (name, frames) in enumerate(all_anim_frames):
        for col, frame in enumerate(frames):
            x = col * TARGET_CELL_W
            y = row * TARGET_CELL_H
            sheet.alpha_composite(frame, (x, y))

    # Phase 4: Flatten transparency to magenta background
    flat = ssp.flatten_visible_rgb(sheet, fill=MAGENTA)

    # Phase 5: Quantize to 15 colors + snap to 9-bit grid
    indexed = ssp.snap_palette_image(flat, colors=MAX_COLORS, dither=False, return_indexed=True)

    # Phase 6: Set index 0 = magenta (transparency color)
    palette = indexed.getpalette()
    pixel_data = list(indexed.tobytes())

    # Find which palette index is closest to magenta
    magenta_idx = None
    min_dist = float('inf')
    num_colors = len(palette) // 3
    for i in range(num_colors):
        r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
        dist = abs(r - 255) + abs(g - 0) + abs(b - 255)
        if dist < min_dist:
            min_dist = dist
            magenta_idx = i

    # Swap palette entries so magenta is at index 0
    if magenta_idx is not None and magenta_idx != 0:
        # Swap palette RGB values
        for c in range(3):
            palette[0*3 + c], palette[magenta_idx*3 + c] = \
                palette[magenta_idx*3 + c], palette[0*3 + c]
        # Swap pixel indices
        new_data = []
        for p in pixel_data:
            if p == 0:
                new_data.append(magenta_idx)
            elif p == magenta_idx:
                new_data.append(0)
            else:
                new_data.append(p)
        pixel_data = new_data

    # Force index 0 to exact magenta (0xEE, 0x00, 0xEE in 9-bit grid)
    palette[0] = 0xEE
    palette[1] = 0x00
    palette[2] = 0xEE

    # Rebuild indexed image
    result = Image.new("P", (sheet_w, sheet_h))
    result.putpalette(palette)
    result.putdata(pixel_data)

    # Save
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.save(OUTPUT_PATH, transparency=0)

    # Report
    print(f"\n[SUCCESS] Sprite sheet saved: {OUTPUT_PATH}")
    print(f"  Dimensions: {sheet_w}x{sheet_h} px")
    print(f"  Cell size:  {TARGET_CELL_W}x{TARGET_CELL_H} px ({TARGET_CELL_W//8}x{TARGET_CELL_H//8} tiles)")
    print(f"  Animations: {len(all_anim_frames)}")
    print(f"  Frames/row: {max_frame_count}")
    print(f"  Total cells: {len(all_anim_frames) * max_frame_count}")
    print(f"  Palette: {MAX_COLORS} visible + index 0 transparent")
    print(f"\n  SGDK resource declaration:")
    print(f"  SPRITE spr_gaira \"sprites/spr_gaira.png\" {TARGET_CELL_W//8} {TARGET_CELL_H//8} FAST 5")

    # Print palette colors
    print(f"\n  Palette (9-bit snapped):")
    for i in range(min(16, num_colors)):
        r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
        label = "TRANSPARENT" if i == 0 else ""
        print(f"    [{i:2d}] #{r:02X}{g:02X}{b:02X}  {label}")


if __name__ == "__main__":
    build_sheet()
