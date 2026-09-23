#!/usr/bin/env python3
"""Assemble branding_v2 model sheet from authored sources.

Allowed operations only: crop, nearest-neighbor scale/rotate, chroma key,
median denoise, 9-bit posterize, palette remap/index, and paste of pixels
that already existed in authored images. Does not draw silhouettes, volumes,
light ramps or lineart.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
CLEAN = ROOT / "raw_png"
OUT = ROOT / "model_sheet_forge_v02.png"
LINEAGE = ROOT / "model_sheet_lineage.json"

# 0x0BGR seed values refined only where the PAL0 ember ring would jump.
# Channel values stay on the Mega Drive 9-bit grid (0x00, 0x22, ... 0xEE).


def bgr_to_rgb(word: int) -> tuple[int, int, int]:
    r_n = word & 0x00F
    g_n = (word >> 4) & 0x00F
    b_n = (word >> 8) & 0x00F
    return (r_n * 0x11, g_n * 0x11, b_n * 0x11)


MAGENTA = (0xFF, 0x00, 0xFF)

PAL0 = [
    MAGENTA,
    bgr_to_rgb(0x0000),
    bgr_to_rgb(0x0200),
    bgr_to_rgb(0x0420),
    bgr_to_rgb(0x0642),
    bgr_to_rgb(0x0864),
    bgr_to_rgb(0x0024),
    bgr_to_rgb(0x0046),
    bgr_to_rgb(0x0068),
    (0x88, 0x44, 0x00),
    (0xAA, 0x88, 0x00),
    (0xEE, 0xAA, 0x00),
    (0xCC, 0x66, 0x00),
    bgr_to_rgb(0x02CE),
    bgr_to_rgb(0x08EE),
    bgr_to_rgb(0x0222),
]

PAL1 = [
    MAGENTA,
    bgr_to_rgb(0x0200),
    bgr_to_rgb(0x0420),
    bgr_to_rgb(0x0620),
    bgr_to_rgb(0x0642),
    bgr_to_rgb(0x0864),
    bgr_to_rgb(0x0A86),
    bgr_to_rgb(0x0CA8),
    bgr_to_rgb(0x0ECA),
    bgr_to_rgb(0x0068),
    bgr_to_rgb(0x008A),
    bgr_to_rgb(0x00AC),
    bgr_to_rgb(0x02CE),
    bgr_to_rgb(0x0AAC),
    bgr_to_rgb(0x0CCC),
    bgr_to_rgb(0x0000),
]

PAL2 = [
    MAGENTA,
    bgr_to_rgb(0x0000),
    bgr_to_rgb(0x0200),
    bgr_to_rgb(0x0422),
    bgr_to_rgb(0x0644),
    bgr_to_rgb(0x0866),
    bgr_to_rgb(0x0A88),
    bgr_to_rgb(0x0CAA),
    bgr_to_rgb(0x0068),
    bgr_to_rgb(0x008A),
    bgr_to_rgb(0x00AC),
    bgr_to_rgb(0x04CE),
    bgr_to_rgb(0x00CE),
    bgr_to_rgb(0x06EE),
    bgr_to_rgb(0x0CEE),
    bgr_to_rgb(0x0422),
]

PAL3 = [
    MAGENTA,
    bgr_to_rgb(0x0200),
    bgr_to_rgb(0x0642),
    bgr_to_rgb(0x0A86),
    bgr_to_rgb(0x0ECA),
    bgr_to_rgb(0x0046),
    bgr_to_rgb(0x0068),
    bgr_to_rgb(0x008A),
    bgr_to_rgb(0x00AC),
    bgr_to_rgb(0x02CE),
    bgr_to_rgb(0x0024),
    bgr_to_rgb(0x0046),
    bgr_to_rgb(0x0068),
    bgr_to_rgb(0x008A),
    bgr_to_rgb(0x08EE),
    bgr_to_rgb(0x0EEE),
]

PALETTE = PAL0 + PAL1 + PAL2 + PAL3
assert len(PALETTE) == 64
assert max(PALETTE[16 + 13]) <= 0xCC and max(PALETTE[16 + 14]) <= 0xCC

# 180 deg == H+V flip, so those angles collapse the 16 runtime orientations.
EMBER_ANGLES = (0, 35, 100, 195)
SHARD_ANGLES = (0, 28, 81, 157)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_key(rgb: tuple[int, int, int]) -> bool:
    """Magenta / hot-pink field, including JPEG-shifted neighbours.

    Iron rust is high-R low-B and must stay. Cool violet shadow is low-R.
    """
    r, g, b = rgb
    if r < 110 or g > 180:
        return False
    if r <= g:
        return False
    # Pink/magenta keeps blue in the field; rust does not.
    if b < max(60, int(g * 0.55)):
        return False
    return True


def dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def snap_9bit(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    def q(c: int) -> int:
        return min(0xEE, int(round(c / 0x22)) * 0x22)

    return (q(rgb[0]), q(rgb[1]), q(rgb[2]))


def clean_rgb(img: Image.Image) -> Image.Image:
    """Kill JPEG ringing before remap. Existing pixels only."""
    rgb = img.convert("RGB")
    # Median on a copy that keeps the key field intact.
    den = rgb.filter(ImageFilter.MedianFilter(size=3))
    sp = rgb.load()
    dp = den.load()
    w, h = rgb.size
    out = Image.new("RGB", (w, h), MAGENTA)
    op = out.load()
    for y in range(h):
        for x in range(w):
            src = sp[x, y]
            if is_key(src):
                op[x, y] = MAGENTA
                continue
            # Prefer the denoised neighbour unless it keyed away the edge.
            cand = dp[x, y]
            op[x, y] = snap_9bit(src if is_key(cand) else cand)
    return out


def persist_cleaned(path: Path) -> Path:
    CLEAN.mkdir(parents=True, exist_ok=True)
    dest = CLEAN / (path.stem + ".png")
    cleaned = clean_rgb(Image.open(path))
    cleaned.save(dest, format="PNG")
    return dest


def load_rgb(path: Path) -> Image.Image:
    return clean_rgb(Image.open(path))


def nearest(rgb: tuple[int, int, int], allowed: list[int]) -> int:
    best_i = allowed[0]
    best_d = 1 << 30
    for i in allowed:
        d = dist(rgb, PALETTE[i])
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def key_from_edges(img: Image.Image) -> Image.Image:
    """Treat the connected field that touches the frame as chroma key."""
    out = img.copy()
    px = out.load()
    w, h = out.size
    seen = bytearray(w * h)
    stack: list[tuple[int, int]] = []

    def push(x: int, y: int) -> None:
        if 0 <= x < w and 0 <= y < h and not seen[y * w + x] and is_key(px[x, y]):
            seen[y * w + x] = 1
            stack.append((x, y))

    for x in range(w):
        push(x, 0)
        push(x, h - 1)
    for y in range(h):
        push(0, y)
        push(w - 1, y)
    while stack:
        x, y = stack.pop()
        px[x, y] = MAGENTA
        push(x + 1, y)
        push(x - 1, y)
        push(x, y + 1)
        push(x, y - 1)
    return out


def content_bbox(img: Image.Image, pad: int = 0) -> tuple[int, int, int, int]:
    px = img.load()
    w, h = img.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(h):
        for x in range(w):
            if not is_key(px[x, y]):
                xs.append(x)
                ys.append(y)
    if not xs:
        return (0, 0, w, h)
    x0 = max(0, min(xs) - pad)
    y0 = max(0, min(ys) - pad)
    x1 = min(w, max(xs) + 1 + pad)
    y1 = min(h, max(ys) + 1 + pad)
    return (x0, y0, x1, y1)


def remap_image(src: Image.Image, allowed: list[int], key_to: int | None = 0) -> Image.Image:
    out = Image.new("P", src.size, 0)
    out.putpalette([c for rgb in PALETTE for c in rgb])
    sp = src.load()
    op = out.load()
    for y in range(src.size[1]):
        for x in range(src.size[0]):
            rgb = sp[x, y]
            if key_to is not None and is_key(rgb):
                op[x, y] = key_to
            else:
                op[x, y] = nearest(rgb, allowed)
    return out


def fit_cover(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = src.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    resized = src.resize((nw, nh), Image.NEAREST)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return resized.crop((left, top, left + tw, top + th))


def fit_contain(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = src.size
    scale = min(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    return src.resize((nw, nh), Image.NEAREST)


def extract_sprite(path: Path, cell: int) -> Image.Image:
    img = key_from_edges(load_rgb(path))
    box = content_bbox(img, pad=2)
    crop = img.crop(box)
    side = max(crop.size)
    square = Image.new("RGB", (side, side), MAGENTA)
    ox = (side - crop.size[0]) // 2
    oy = (side - crop.size[1]) // 2
    square.paste(crop, (ox, oy))
    return square.resize((cell, cell), Image.NEAREST)


def rotate_authored(img: Image.Image, angle: int) -> Image.Image:
    rot = img.rotate(-angle, resample=Image.NEAREST, expand=True, fillcolor=MAGENTA)
    return fit_cover(rot, img.size)


def paste_indexed(dst: Image.Image, src: Image.Image, xy: tuple[int, int]) -> None:
    dp = dst.load()
    sp = src.load()
    x0, y0 = xy
    for y in range(src.size[1]):
        for x in range(src.size[0]):
            idx = sp[x, y]
            if idx % 16 == 0:
                continue
            dx, dy = x0 + x, y0 + y
            if 0 <= dx < dst.size[0] and 0 <= dy < dst.size[1]:
                dp[dx, dy] = idx


def _luma(rgb: tuple[int, int, int]) -> float:
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def _swatch_rows(board: Image.Image) -> list[tuple[int, int]]:
    w, h = board.size
    px = board.load()
    energy = []
    for y in range(h):
        acc = 0.0
        for x in range(0, w, 4):
            acc += _luma(px[x, y])
        energy.append(acc / (w / 4))
    thresh = 28.0
    runs: list[tuple[int, int]] = []
    y = 0
    while y < h:
        if energy[y] >= thresh:
            y0 = y
            while y < h and energy[y] >= thresh:
                y += 1
            if y - y0 >= 12:
                runs.append((y0, y))
        else:
            y += 1
    runs.sort(key=lambda r: r[1] - r[0], reverse=True)
    rows = sorted(runs[:4], key=lambda r: r[0])
    if len(rows) < 4:
        body0, body1 = int(h * 0.16), int(h * 0.96)
        step = (body1 - body0) // 4
        rows = [(body0 + i * step, body0 + (i + 1) * step) for i in range(4)]
    return rows


def extract_glyphs(path: Path) -> dict[str, Image.Image]:
    """Split the authored digit strip on empty columns."""
    img = load_rgb(path)
    box = content_bbox(img, pad=1)
    strip = img.crop(box)
    px = strip.load()
    w, h = strip.size
    col_ink = []
    for x in range(w):
        col_ink.append(any(not is_key(px[x, y]) for y in range(h)))
    spans: list[tuple[int, int]] = []
    x = 0
    while x < w:
        if col_ink[x]:
            x0 = x
            while x < w and col_ink[x]:
                x += 1
            if x - x0 >= 3:
                spans.append((x0, x))
        else:
            x += 1
    labels = list("0123456789P")
    glyphs: dict[str, Image.Image] = {}
    for i, (x0, x1) in enumerate(spans[: len(labels)]):
        glyph = strip.crop((x0, 0, x1, h))
        glyphs[labels[i]] = glyph
    return glyphs


def scale_glyph(glyph: Image.Image, height: int) -> Image.Image:
    scale = height / glyph.size[1]
    nw = max(3, int(round(glyph.size[0] * scale)))
    return glyph.resize((nw, height), Image.NEAREST)


def paste_text(
    dst: Image.Image,
    glyphs: dict[str, Image.Image],
    text: str,
    xy: tuple[int, int],
    height: int,
    ink: int,
) -> int:
    x, y = xy
    for ch in text:
        g = glyphs.get(ch)
        if g is None:
            x += height // 2
            continue
        small = scale_glyph(g, height)
        mapped = remap_image(small, [ink], key_to=0)
        paste_indexed(dst, mapped, (x, y))
        x += small.size[0] + 1
    return x


def panel_c_from_board(board_path: Path, glyph_path: Path) -> Image.Image:
    board = load_rgb(board_path)
    rows = _swatch_rows(board)
    glyphs = extract_glyphs(glyph_path)
    out = Image.new("P", (512, 64), 0)
    out.putpalette([c for rgb in PALETTE for c in rgb])
    op = out.load()
    band_h = 16
    swatch_top = 6
    for row, (y0, y1) in enumerate(rows):
        strip = board.crop((int(board.size[0] * 0.03), y0, int(board.size[0] * 0.97), y1))
        strip = strip.resize((472, band_h - swatch_top), Image.NEAREST)
        sp = strip.load()
        base = row * 16
        dest_y = row * band_h
        # Recolor authored painted pixels onto locked indices. Labels sit above.
        for y in range(strip.size[1]):
            for x in range(472):
                rgb = sp[x, y]
                if _luma(rgb) < 16:
                    continue
                slot = 1 + min(14, x * 15 // 472)
                op[40 + x, dest_y + swatch_top + y] = base + slot
        paste_text(out, glyphs, f"P{row}", (1, dest_y + 3), 9, 31)
        for slot in (1, 5, 9, 13, 15):
            cx = 40 + (slot - 1) * 472 // 15 + 2
            paste_text(out, glyphs, str(slot), (cx, dest_y + 0), 6, 31)
    return out


def build() -> dict:
    sources = {
        "panel_a": RAW / "forge_scene_v06.jpg",
        "panel_b": RAW / "silhouette_v03.jpg",
        "panel_c": RAW / "palette_ramps_v02.jpg",
        "panel_d": RAW / "wordmark_forja_v06.jpg",
        "ember": RAW / "ember_v04.jpg",
        "shard": RAW / "shard_v04.jpg",
        "label_4x": RAW / "label_4x_v01.jpg",
        "glyphs": RAW / "glyphs_v01.jpg",
    }
    for p in sources.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    cleaned_paths = {name: persist_cleaned(path) for name, path in sources.items()}

    sheet = Image.new("P", (512, 384), 0)
    sheet.putpalette([c for rgb in PALETTE for c in rgb])

    scene = fit_cover(load_rgb(sources["panel_a"]), (256, 160))
    panel_a = remap_image(scene, list(range(1, 16)), key_to=0)
    paste_indexed(sheet, panel_a, (0, 0))

    sil = fit_cover(load_rgb(sources["panel_b"]), (256, 160))
    panel_b = Image.new("P", (256, 160), 0)
    panel_b.putpalette([c for rgb in PALETTE for c in rgb])
    sp = sil.load()
    bp = panel_b.load()
    for y in range(160):
        for x in range(256):
            rgb = sp[x, y]
            if not is_key(rgb) and max(rgb) < 80:
                bp[x, y] = 31
    paste_indexed(sheet, panel_b, (256, 0))

    panel_c = panel_c_from_board(sources["panel_c"], sources["glyphs"])
    paste_indexed(sheet, panel_c, (0, 160))

    # D lives on PAL1: this wordmark becomes img_logo_engine_v2.
    mark = key_from_edges(load_rgb(sources["panel_d"]))
    mark = mark.crop(content_bbox(mark, pad=4))
    scale = 64 / mark.size[1]
    nw = max(8, int(round(mark.size[0] * scale)))
    nh = 64
    if nw > 248:
        scale = 248 / mark.size[0]
        nw = 248
        nh = max(8, int(round(mark.size[1] * scale)))
    mark = mark.resize((nw, nh), Image.NEAREST)
    panel_d = remap_image(mark, list(range(17, 32)), key_to=0)
    ox = (256 - nw) // 2
    oy = 224 + (96 - nh) // 2
    paste_indexed(sheet, panel_d, (ox, oy))

    ember = extract_sprite(sources["ember"], 16)
    shard = extract_sprite(sources["shard"], 16)
    ember_frames = [rotate_authored(ember, a) for a in EMBER_ANGLES]
    shard_frames = [rotate_authored(shard, a) for a in SHARD_ANGLES]
    ember_idx = [remap_image(f, list(range(53, 64)), key_to=0) for f in ember_frames]
    shard_idx = [remap_image(f, list(range(49, 64)), key_to=0) for f in shard_frames]
    for i, fr in enumerate(ember_idx):
        paste_indexed(sheet, fr, (264 + i * 18, 228))
    for i, fr in enumerate(shard_idx):
        paste_indexed(sheet, fr, (264 + i * 18, 248))

    ember_4x = ember_idx[0].resize((64, 64), Image.NEAREST)
    shard_4x = shard_idx[0].resize((64, 64), Image.NEAREST)
    paste_indexed(sheet, ember_4x, (344, 228))
    paste_indexed(sheet, shard_4x, (416, 228))

    label_rgb = load_rgb(sources["label_4x"])
    label = label_rgb.crop(content_bbox(label_rgb, pad=2))
    label = fit_contain(label, (48, 24))
    label_idx = remap_image(label, [31, 15, 47], key_to=0)
    paste_indexed(sheet, label_idx, (344, 294))

    sheet.save(OUT, format="PNG", transparency=0)

    lineage = {
        "schema": "asset_lineage_record.v1",
        "asset": "model_sheet_forge_v02.png",
        "supersedes": "model_sheet_forge_v01.png",
        "generation_channel": "native_chat_image_generation_callable",
        "tool_callable": "image_gen+image_edit",
        "procedural_generation_used_as_asset_source": False,
        "assembler": "assemble_model_sheet.py",
        "source_format_decision": {
            "choice": "keep_jpg_then_posterize_denoise_before_remap",
            "persist_cleaned_png_lossless": True,
            "cleaned_dir": "data/source_art/branding_v2/raw_png",
            "reason": "The session image tools write JPEG. Decoding and saving PNG without a clean pass would keep ringing and blocking. A 3x3 median plus snap to the Mega Drive 9-bit grid runs before palette remap; the cleaned PNG is what the sheet consumes.",
        },
        "rotation_policy": {
            "ember_angles_deg": list(EMBER_ANGLES),
            "shard_angles_deg": list(SHARD_ANGLES),
            "note": "Angles avoid 90/180/270 so H/V flip adds orientations instead of repeating a pair.",
        },
        "assembler_ops": [
            "median_denoise",
            "posterize_9bit",
            "crop",
            "nearest_neighbor_resize",
            "nearest_neighbor_rotate",
            "chroma_key",
            "palette_remap",
            "paste",
        ],
        "authored_sources": {
            name: {
                "path": str(path.relative_to(ROOT.parent.parent.parent)),
                "sha256": sha256(path),
                "cleaned_png": str(cleaned_paths[name].relative_to(ROOT.parent.parent.parent)),
                "cleaned_sha256": sha256(cleaned_paths[name]),
            }
            for name, path in sources.items()
        },
        "output_sha256": sha256(OUT),
        "canvas": [512, 384],
        "palette_entries": 64,
        "panel_d_palette": "PAL1",
    }
    LINEAGE.write_text(json.dumps(lineage, indent=2), encoding="utf-8")
    print(f"wrote {OUT} {OUT.stat().st_size} bytes")
    return lineage


if __name__ == "__main__":
    build()
