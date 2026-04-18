"""
Generate Mega Drive-compliant indexed PNG assets for the platformer_gm template.
All colors use the 9-bit VDP palette grid (channels are multiples of 0x22).
player.png: 24x96 sprite sheet (3x4 tiles per frame, 4 frames: idle, walk1, walk2, jump)
             => total image: 96x32 (4 frames side-by-side, each 24x32)
level.png:  320x224 tileset/map image (40x28 tiles of 8x8)
jump.wav:   minimal valid WAV placeholder (silence, 8kHz mono)
"""

import struct
import zlib
import os

# ── MD 9-bit Palette (hex values are multiples of 0x22) ────────────────────────
# Index 0 = transparent (magenta convention)
PALETTE = [
    (0xFF, 0x00, 0xFF),  # 0: transparent (magenta)
    (0x00, 0x22, 0x44),  # 1: dark navy
    (0x00, 0x44, 0x88),  # 2: medium blue
    (0x00, 0x88, 0xCC),  # 3: bright blue
    (0x00, 0xAA, 0x44),  # 4: green
    (0x22, 0xCC, 0x66),  # 5: bright green
    (0x88, 0x44, 0x00),  # 6: brown (ground)
    (0xAA, 0x66, 0x22),  # 7: light brown
    (0xCC, 0x88, 0x44),  # 8: sand
    (0xEE, 0xEE, 0xEE),  # 9: near-white
    (0x44, 0x44, 0x44),  # 10: dark gray
    (0x88, 0x88, 0x88),  # 11: medium gray
    (0xEE, 0x44, 0x44),  # 12: red (player accent)
    (0x00, 0x00, 0x00),  # 13: black
    (0xCC, 0xCC, 0x00),  # 14: yellow
    (0x44, 0xAA, 0xEE),  # 15: sky blue
]


def write_indexed_png(path, width, height, pixels, palette):
    """Write an 8-bit indexed color PNG (no dependencies)."""

    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))

    plte_data = b""
    for r, g, b in palette:
        plte_data += struct.pack("BBB", r, g, b)
    plte = chunk(b"PLTE", plte_data)

    # tRNS: index 0 is fully transparent
    trns = chunk(b"tRNS", b"\x00")

    raw = b""
    for y in range(height):
        raw += b"\x00"  # filter: none
        raw += bytes(pixels[y * width : (y + 1) * width])

    compressed = zlib.compress(raw, 9)
    idat = chunk(b"IDAT", compressed)
    iend = chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(sig + ihdr + plte + trns + idat + iend)


def generate_player_png(path):
    """
    96x32 sprite sheet: 4 frames of 24x32 each (3x4 tiles).
    Frames: idle, walk1, walk2, jump.
    Uses palette indices: 0=transparent, 1-3=blue tones (body),
    9=white (eyes/highlight), 12=red (accent), 13=black (outline).
    """
    W, H = 96, 32
    FW, FH = 24, 32
    pixels = [0] * (W * H)

    def set_px(fx, x, y, idx):
        """Set pixel in frame fx at local coords (x,y)."""
        gx = fx * FW + x
        gy = y
        if 0 <= gx < W and 0 <= gy < H:
            pixels[gy * W + gx] = idx

    def draw_character(fx, offset_x=0, offset_y=0, legs_spread=False, arms_up=False):
        """Draw a simple character silhouette."""
        # Head (6x6 centered at top)
        hx, hy = 9 + offset_x, 2 + offset_y
        for dy in range(6):
            for dx in range(6):
                set_px(fx, hx + dx, hy + dy, 2)
        # Eyes
        set_px(fx, hx + 1, hy + 2, 9)
        set_px(fx, hx + 4, hy + 2, 9)

        # Body (8x10)
        bx, by = 8 + offset_x, 8 + offset_y
        for dy in range(10):
            for dx in range(8):
                set_px(fx, bx + dx, by + dy, 3)
        # Belt accent
        for dx in range(8):
            set_px(fx, bx + dx, by + 5, 12)

        # Legs
        if legs_spread:
            # Left leg shifted left
            for dy in range(8):
                for dx in range(3):
                    set_px(fx, 7 + offset_x + dx, 18 + offset_y + dy, 1)
            # Right leg shifted right
            for dy in range(8):
                for dx in range(3):
                    set_px(fx, 14 + offset_x + dx, 18 + offset_y + dy, 1)
        else:
            # Legs together
            for dy in range(8):
                for dx in range(6):
                    set_px(fx, 9 + offset_x + dx, 18 + offset_y + dy, 1)

        # Arms
        if arms_up:
            # Arms raised
            for dy in range(6):
                for dx in range(2):
                    set_px(fx, 5 + offset_x + dx, 4 + offset_y + dy, 2)
                    set_px(fx, 17 + offset_x + dx, 4 + offset_y + dy, 2)
        else:
            # Arms down
            for dy in range(6):
                for dx in range(2):
                    set_px(fx, 5 + offset_x + dx, 10 + offset_y + dy, 2)
                    set_px(fx, 17 + offset_x + dx, 10 + offset_y + dy, 2)

        # Outline (black border - top of head)
        for dx in range(8):
            set_px(fx, hx - 1 + dx, hy - 1, 13)

    # Frame 0: Idle
    draw_character(0)
    # Frame 1: Walk 1 (legs spread)
    draw_character(1, legs_spread=True)
    # Frame 2: Walk 2 (shifted slightly)
    draw_character(2, offset_x=0, legs_spread=True)
    # Frame 3: Jump (arms up, shifted up)
    draw_character(3, offset_y=-2, arms_up=True)

    write_indexed_png(path, W, H, pixels, PALETTE)


def generate_level_png(path):
    """
    320x224 level tileset/map image (40x28 tiles).
    Creates a vibrant platformer level:
    - Sky background (top)
    - Ground platform (bottom rows 21-27)
    - Some step platforms mid-level
    - Decorative elements
    """
    W, H = 320, 224
    pixels = [15] * (W * H)  # Fill with sky blue (index 15)

    def fill_tile(tx, ty, idx):
        """Fill an 8x8 tile with a single color index."""
        for dy in range(8):
            for dx in range(8):
                px = tx * 8 + dx
                py = ty * 8 + dy
                if 0 <= px < W and 0 <= py < H:
                    pixels[py * W + px] = idx

    def fill_ground_tile(tx, ty):
        """Fill a ground tile with grass on top and dirt below."""
        for dy in range(8):
            for dx in range(8):
                px = tx * 8 + dx
                py = ty * 8 + dy
                if 0 <= px < W and 0 <= py < H:
                    if dy < 2:
                        pixels[py * W + px] = 5  # bright green grass
                    elif dy < 4:
                        pixels[py * W + px] = 4  # green
                    else:
                        pixels[py * W + px] = 6  # brown dirt

    def fill_dirt_tile(tx, ty):
        """Underground dirt tile."""
        for dy in range(8):
            for dx in range(8):
                px = tx * 8 + dx
                py = ty * 8 + dy
                if 0 <= px < W and 0 <= py < H:
                    if (dx + dy) % 3 == 0:
                        pixels[py * W + px] = 7  # light brown variation
                    else:
                        pixels[py * W + px] = 6  # brown

    def fill_platform_tile(tx, ty):
        """Floating platform tile with stone look."""
        for dy in range(8):
            for dx in range(8):
                px = tx * 8 + dx
                py = ty * 8 + dy
                if 0 <= px < W and 0 <= py < H:
                    if dy == 0:
                        pixels[py * W + px] = 11  # gray top edge
                    elif dy < 2:
                        pixels[py * W + px] = 8  # sand top
                    else:
                        pixels[py * W + px] = 10  # dark gray body

    # ── Ground (rows 21-27, full width) ─────────────────────────────────────
    for tx in range(40):
        fill_ground_tile(tx, 21)  # grass surface
        for ty in range(22, 28):
            fill_dirt_tile(tx, ty)  # dirt below

    # ── Gap in the ground (columns 12-14) ───────────────────────────────────
    for tx in range(12, 15):
        for ty in range(21, 28):
            fill_tile(tx, ty, 15)  # sky (hole)

    # ── Step platform 1 (rows 17-18, columns 5-9) ──────────────────────────
    for tx in range(5, 10):
        fill_platform_tile(tx, 17)
        fill_tile(tx, 18, 10)

    # ── Step platform 2 (rows 14-15, columns 18-24) ────────────────────────
    for tx in range(18, 25):
        fill_platform_tile(tx, 14)
        fill_tile(tx, 15, 10)

    # ── Step platform 3 (rows 10-11, columns 30-36) ────────────────────────
    for tx in range(30, 37):
        fill_platform_tile(tx, 10)
        fill_tile(tx, 11, 10)

    # ── High platform (rows 7-8, columns 10-16) ────────────────────────────
    for tx in range(10, 17):
        fill_platform_tile(tx, 7)
        fill_tile(tx, 8, 10)

    # ── Decorative clouds (top area) ────────────────────────────────────────
    for tx in range(3, 7):
        fill_tile(tx, 3, 9)  # white cloud
    for tx in range(20, 23):
        fill_tile(tx, 2, 9)
    for tx in range(33, 38):
        fill_tile(tx, 4, 9)

    write_indexed_png(path, W, H, pixels, PALETTE)


def generate_jump_wav(path):
    """Generate a minimal valid WAV file (short beep for jump SFX)."""
    sample_rate = 8000
    duration_ms = 80
    num_samples = sample_rate * duration_ms // 1000
    # Simple descending tone
    samples = bytearray()
    for i in range(num_samples):
        freq = 800 - (i * 400 // num_samples)
        import math
        val = int(127 + 80 * math.sin(2.0 * math.pi * freq * i / sample_rate))
        val = max(0, min(255, val))
        samples.append(val)

    data_size = len(samples)
    file_size = 36 + data_size

    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", file_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))          # chunk size
        f.write(struct.pack("<H", 1))           # PCM
        f.write(struct.pack("<H", 1))           # mono
        f.write(struct.pack("<I", sample_rate))  # sample rate
        f.write(struct.pack("<I", sample_rate))  # byte rate
        f.write(struct.pack("<H", 1))           # block align
        f.write(struct.pack("<H", 8))           # bits per sample
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(samples)


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(base, "res", "images")
    sound_dir = os.path.join(base, "res", "sound")

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(sound_dir, exist_ok=True)

    generate_player_png(os.path.join(images_dir, "player.png"))
    generate_level_png(os.path.join(images_dir, "level.png"))
    generate_jump_wav(os.path.join(sound_dir, "jump.wav"))

    print("Assets generated successfully:")
    for root, dirs, files in os.walk(os.path.join(base, "res")):
        for name in files:
            full = os.path.join(root, name)
            size = os.path.getsize(full)
            print(f"  {os.path.relpath(full, base)} ({size} bytes)")
