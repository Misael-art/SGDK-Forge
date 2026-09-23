#!/usr/bin/env python3
"""Build Celestial Chase animation approval candidate v003.

This builder stays in data/processed. It does not promote anything to res/.
The goal is a human-reviewable animation board with strict 4bpp indexed strips,
pivot evidence, timing reports and a modular boss impact contract.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


MAGENTA = (255, 0, 255)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


ROOT = repo_root()
BASE = ROOT / "data/processed/celestial_chase_v001/source_baked_pixel_art_candidates_v001"
PIXEL_LOCK = BASE / "pixel_lock_v002"
VARIANTS = BASE / "pixel_lock_v002_variants"
OUT = BASE / "animation_strip_candidates_v003"


def load_p(path: Path) -> Image.Image:
    im = Image.open(path)
    if im.mode != "P":
        raise ValueError(f"{path} is not indexed P mode")
    im.info["transparency"] = 0
    return im


def palette16(im: Image.Image) -> list[tuple[int, int, int]]:
    pal = im.getpalette()
    if not pal:
        raise ValueError("indexed image has no PLTE")
    colors = [tuple(pal[i : i + 3]) for i in range(0, min(len(pal), 48), 3)]
    if len(colors) < 16:
        colors.extend([(0, 0, 0)] * (16 - len(colors)))
    return colors[:16]


def put_palette16(im: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    flat: list[int] = []
    for rgb in palette[:16]:
        flat.extend(rgb)
    im.putpalette(flat)
    im.info["transparency"] = 0
    return im


def p_to_rgba(im: Image.Image) -> Image.Image:
    pal = palette16(im)
    src = list(im.getdata())
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    pix = out.load()
    w, _ = im.size
    for i, idx in enumerate(src):
        x = i % w
        y = i // w
        if idx == 0:
            pix[x, y] = (0, 0, 0, 0)
        else:
            r, g, b = pal[idx]
            pix[x, y] = (r, g, b, 255)
    return out


def nearest_index(rgb: tuple[int, int, int], palette: list[tuple[int, int, int]]) -> int:
    best = 1
    best_dist = 10**9
    r, g, b = rgb
    for idx, (pr, pg, pb) in enumerate(palette[1:], start=1):
        dist = (r - pr) * (r - pr) + (g - pg) * (g - pg) + (b - pb) * (b - pb)
        if dist < best_dist:
            best = idx
            best_dist = dist
    return best


def rgba_to_p(im: Image.Image, palette: list[tuple[int, int, int]]) -> Image.Image:
    im = im.convert("RGBA")
    out = Image.new("P", im.size, 0)
    src = im.load()
    dst = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = src[x, y]
            if a < 128:
                dst[x, y] = 0
            else:
                dst[x, y] = nearest_index((r, g, b), palette)
    return put_palette16(out, palette)


def save_p_png(im: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True, transparency=0, bits=4)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def paste_clipped(dst: Image.Image, src: Image.Image, dx: int, dy: int) -> None:
    sx = max(0, -dx)
    sy = max(0, -dy)
    tx = max(0, dx)
    ty = max(0, dy)
    w = min(src.width - sx, dst.width - tx)
    h = min(src.height - sy, dst.height - ty)
    if w <= 0 or h <= 0:
        return
    dst.alpha_composite(src.crop((sx, sy, sx + w, sy + h)), (tx, ty))


def mask_indices(im: Image.Image, indices: set[int], keep: bool) -> Image.Image:
    pal = palette16(im)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    src = list(im.getdata())
    pix = out.load()
    w, _ = im.size
    for i, idx in enumerate(src):
        in_mask = idx in indices
        if idx != 0 and in_mask == keep:
            r, g, b = pal[idx]
            pix[i % w, i // w] = (r, g, b, 255)
    return out


def lower_layer(im: Image.Image, y_start: int) -> Image.Image:
    pal = palette16(im)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    src = list(im.getdata())
    pix = out.load()
    w, _ = im.size
    for i, idx in enumerate(src):
        x = i % w
        y = i // w
        if idx != 0 and y >= y_start:
            r, g, b = pal[idx]
            pix[x, y] = (r, g, b, 255)
    return out


def nonzero_bbox(im: Image.Image) -> tuple[int, int, int, int] | None:
    if im.mode == "P":
        mask = Image.new("L", im.size, 0)
        src = list(im.getdata())
        pix = mask.load()
        w, _ = im.size
        for i, idx in enumerate(src):
            if idx != 0:
                pix[i % w, i // w] = 255
        return mask.getbbox()
    return im.getchannel("A").getbbox()


def alpha_centroid(im: Image.Image, exclude_indices: set[int] | None = None) -> tuple[float, float]:
    if im.mode == "P":
        src = list(im.getdata())
        w, _ = im.size
        total = 0
        sx = 0
        sy = 0
        for i, idx in enumerate(src):
            if idx != 0 and (exclude_indices is None or idx not in exclude_indices):
                x = i % w
                y = i // w
                total += 1
                sx += x
                sy += y
        if total:
            return (sx / total, sy / total)
        return (im.width / 2, im.height / 2)
    rgba = im.convert("RGBA")
    total = 0
    sx = 0
    sy = 0
    pix = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if pix[x, y][3] >= 128:
                total += 1
                sx += x
                sy += y
    if total:
        return (sx / total, sy / total)
    return (im.width / 2, im.height / 2)


def contact_point(im: Image.Image) -> tuple[float, int]:
    bbox = nonzero_bbox(im)
    if bbox is None:
        return (im.width / 2, 0)
    y = bbox[3] - 1
    xs: list[int] = []
    if im.mode == "P":
        pix = im.load()
        for yy in range(max(0, y - 2), y + 1):
            for x in range(im.width):
                if pix[x, yy] != 0:
                    xs.append(x)
    else:
        pix = im.convert("RGBA").load()
        for yy in range(max(0, y - 2), y + 1):
            for x in range(im.width):
                if pix[x, yy][3] >= 128:
                    xs.append(x)
    return ((sum(xs) / len(xs)) if xs else im.width / 2, y)


def strip(frames: list[Image.Image], palette: list[tuple[int, int, int]]) -> Image.Image:
    if not frames:
        raise ValueError("empty strip")
    w, h = frames[0].size
    out = Image.new("P", (w * len(frames), h), 0)
    put_palette16(out, palette)
    for i, frame in enumerate(frames):
        out.paste(frame, (i * w, 0))
    return out


def scaled_content(im: Image.Image, scale: float, palette: list[tuple[int, int, int]], cell: tuple[int, int]) -> Image.Image:
    rgba = p_to_rgba(im)
    bbox = rgba.getchannel("A").getbbox()
    out = Image.new("RGBA", cell, (0, 0, 0, 0))
    if bbox is None:
        return rgba_to_p(out, palette)
    content = rgba.crop(bbox)
    nw = max(1, int(round(content.width * scale)))
    nh = max(1, int(round(content.height * scale)))
    content = content.resize((nw, nh), Image.Resampling.NEAREST)
    x = (cell[0] - nw) // 2
    y = cell[1] - nh
    paste_clipped(out, content, x, y)
    return rgba_to_p(out, palette)


def normalize_hero_cell(im: Image.Image, palette: list[tuple[int, int, int]], desired_bottom: int) -> Image.Image:
    rgba = p_to_rgba(im)
    bbox = rgba.getchannel("A").getbbox()
    out = Image.new("RGBA", (64, 80), (0, 0, 0, 0))
    if bbox is None:
        return rgba_to_p(out, palette)
    content = rgba.crop(bbox)
    max_w = 62
    max_h = max(1, desired_bottom)
    scale = min(max_w / content.width, max_h / content.height, 1.0)
    nw = max(1, int(math.floor(content.width * scale)))
    nh = max(1, int(math.floor(content.height * scale)))
    content = content.resize((nw, nh), Image.Resampling.NEAREST)
    x = (64 - nw) // 2
    y = desired_bottom - nh + 1
    paste_clipped(out, content, x, y)
    return rgba_to_p(out, palette)


def draw_dust_frame(size: tuple[int, int], frame: int, palette: list[tuple[int, int, int]]) -> Image.Image:
    w, h = size
    rgba = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rgba)
    gold = palette[8] + (255,)
    grey = palette[4] + (255,)
    purple = palette[10] + (255,)
    if frame == 1:
        d.line((18, 24, 31, 19), fill=grey, width=1)
        d.line((36, 24, 51, 20), fill=grey, width=1)
    elif frame == 2:
        d.line((8, 25, 27, 16), fill=grey, width=2)
        d.line((33, 26, 61, 15), fill=grey, width=2)
        d.line((20, 29, 8, 30), fill=purple, width=1)
        d.line((45, 29, 60, 30), fill=purple, width=1)
        d.line((25, 21, 32, 11), fill=gold, width=1)
        d.line((39, 21, 33, 10), fill=gold, width=1)
    elif frame == 3:
        d.line((5, 26, 25, 22), fill=grey, width=1)
        d.line((38, 24, 62, 22), fill=grey, width=1)
        d.point((16, 19), fill=purple)
        d.point((48, 18), fill=purple)
        d.point((32, 14), fill=gold)
    return rgba_to_p(rgba, palette)


def png_ihdr(path: Path) -> dict[str, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not PNG")
    length, chunk = struct.unpack(">I4s", data[8:16])
    if length != 13 or chunk != b"IHDR":
        raise ValueError(f"{path} has invalid IHDR")
    w, h, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", data[16:29])
    return {
        "width": w,
        "height": h,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "compression": compression,
        "filter": filter_method,
        "interlace": interlace,
    }


def tile_count_unique_nonempty(im: Image.Image, frame_w: int, frame_h: int) -> tuple[int, int]:
    seen: set[bytes] = set()
    nonempty = 0
    frames = im.width // frame_w
    for f in range(frames):
        frame = im.crop((f * frame_w, 0, (f + 1) * frame_w, frame_h))
        for y in range(0, frame_h, 8):
            for x in range(0, frame_w, 8):
                tile = frame.crop((x, y, x + 8, y + 8))
                data = bytes(tile.getdata())
                if any(v != 0 for v in data):
                    nonempty += 1
                    seen.add(data)
    return len(seen), nonempty


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = ["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"]
    for name in names:
        p = Path("C:/Windows/Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


F_TITLE = load_font(34, True)
F_H = load_font(22, True)
F_BODY = load_font(16)
F_SMALL = load_font(13)
F_TINY = load_font(11)


def checker(size: tuple[int, int], cell: int = 8) -> Image.Image:
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a = (54, 57, 63, 255)
    b = (40, 43, 49, 255)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=a if ((x // cell + y // cell) & 1) == 0 else b)
    return im


def paste_scaled_p(board: Image.Image, p_img: Image.Image, xy: tuple[int, int], scale: int) -> None:
    rgba = p_to_rgba(p_img)
    scaled = rgba.resize((rgba.width * scale, rgba.height * scale), Image.Resampling.NEAREST)
    x, y = xy
    board.alpha_composite(checker(scaled.size), (x, y))
    board.alpha_composite(scaled, (x, y))


def draw_overlay_strip(frames: list[Image.Image], cogs: list[tuple[float, float]], contacts: list[tuple[float, int]], palette: list[tuple[int, int, int]], ground_y: int) -> Image.Image:
    w, h = frames[0].size
    rgba = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        tile = p_to_rgba(frame)
        rgba.alpha_composite(tile, (i * w, 0))
        d = ImageDraw.Draw(rgba)
        ox = i * w
        d.line((ox + 32, 0, ox + 32, h), fill=(255, 255, 0, 220), width=1)
        d.line((ox, ground_y, ox + w - 1, ground_y), fill=(0, 255, 255, 220), width=1)
        cx, cy = cogs[i]
        d.ellipse((ox + cx - 2, cy - 2, ox + cx + 2, cy + 2), fill=(255, 64, 64, 255))
        px, py = contacts[i]
        d.rectangle((ox + px - 2, py - 2, ox + px + 2, py + 2), outline=(255, 220, 0, 255), width=1)
        d.text((ox + 2, 2), f"F{i}", fill=(255, 255, 255, 255), font=F_TINY)
    return rgba_to_p(rgba, palette)


def draw_board(report: dict, hero_strip: Image.Image, hero_overlay: Image.Image, boss_strips: dict[str, Image.Image]) -> Image.Image:
    W, H = 1900, 1580
    bg = (12, 14, 18, 255)
    panel = (24, 29, 34, 255)
    line = (70, 79, 86, 255)
    text = (232, 235, 238, 255)
    muted = (172, 180, 185, 255)
    accent = (238, 170, 34, 255)
    board = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(board)

    def box(x: int, y: int, w: int, h: int, title: str) -> None:
        d.rectangle((x, y, x + w, y + h), fill=panel, outline=line, width=1)
        d.text((x + 18, y + 14), title, fill=text, font=F_H)

    d.text((30, 26), "Celestial Chase - Animation Strip Candidate v003", fill=text, font=F_TITLE)
    d.text((30, 66), "Approval board: timing, pivot, contact frames, cape follow-through and modular boss impact contract", fill=muted, font=F_BODY)
    d.rounded_rectangle((1450, 36, 1770, 74), radius=5, fill=(68, 40, 18, 255), outline=(130, 88, 32, 255))
    d.text((1464, 45), "PENDING HUMAN ANIMATION APPROVAL", fill=(255, 224, 170, 255), font=F_SMALL)
    d.line((30, 100, W - 30, 100), fill=line, width=1)

    box(30, 125, 1320, 330, "Hero run_toward strip 64x80 - 8 frames")
    paste_scaled_p(board, hero_strip, (56, 184), 2)
    d.text((56, 358), "Transparent strip, frame cells 64x80. Frame cadence: 4,3,3,4,4,3,3,4 ticks at 60 FPS.", fill=muted, font=F_SMALL)
    d.text((56, 382), "Contact frames F0/F4 sit lowest; pass frames rise; cape reaches high point one frame after body contact.", fill=muted, font=F_SMALL)

    box(30, 480, 1320, 300, "Hero pivot proof")
    paste_scaled_p(board, hero_overlay, (56, 540), 2)
    d.text((56, 716), "cyan = ground/pivot line y78, yellow = centerline x32, red = measured body COG, gold square = foot/contact point", fill=muted, font=F_SMALL)

    box(1380, 125, 470, 780, "Timing table")
    y = 184
    headers = ["Frame", "Ticks", "Phase", "Contact", "Cape"]
    xs = [1400, 1460, 1520, 1640, 1720]
    for x, h in zip(xs, headers):
        d.text((x, y), h, fill=accent, font=F_SMALL)
    y += 28
    for item in report["hero"]["frames"]:
        vals = [
            item["id"],
            str(item["duration_ticks"]),
            item["phase"],
            "yes" if item["foot_contact"] else "no",
            str(item["cape_offset"]),
        ]
        for x, val in zip(xs, vals):
            d.text((x, y), val, fill=muted, font=F_SMALL)
        y += 24
    y += 16
    d.text((1400, y), "Boss scale sync", fill=accent, font=F_SMALL)
    y += 30
    d.text((1400, y), "Frame", fill=accent, font=F_SMALL)
    d.text((1470, y), "Scale", fill=accent, font=F_SMALL)
    d.text((1540, y), "Ticks", fill=accent, font=F_SMALL)
    d.text((1615, y), "Impact", fill=accent, font=F_SMALL)
    y += 28
    for item in report["pursuer"]["scale_curve"]:
        d.text((1400, y), item["id"], fill=muted, font=F_SMALL)
        d.text((1470, y), f"{item['scale_percent']}%", fill=muted, font=F_SMALL)
        d.text((1540, y), str(item["duration_ticks"]), fill=muted, font=F_SMALL)
        d.text((1615, y), "shake" if item["impact"] else "-", fill=muted, font=F_SMALL)
        y += 24
    y += 20
    d.text((1400, y), "Shake contract", fill=accent, font=F_SMALL)
    y += 26
    for line_text in [
        "impact frame: B3",
        "curve px: +2, -2, +1, -1, 0",
        "API verified: VDP_setVerticalScroll",
        "restore scroll to zero after sequence",
    ]:
        d.text((1400, y), line_text, fill=muted, font=F_SMALL)
        y += 22

    box(30, 815, 1320, 420, "Pursuer modular strips - synchronized Z scale")
    paste_scaled_p(board, boss_strips["body"], (56, 874), 1)
    d.text((56, 962), "body mid 96x80 z-loop", fill=muted, font=F_SMALL)
    paste_scaled_p(board, boss_strips["head"], (56, 1002), 1)
    d.text((56, 1074), "head/horns 112x64 uses the same scale curve", fill=muted, font=F_SMALL)
    paste_scaled_p(board, boss_strips["hoof"], (56, 1114), 1)
    d.text((56, 1186), "hoof module 96x64, synchronized with head/body", fill=muted, font=F_SMALL)
    paste_scaled_p(board, boss_strips["dust"], (760, 1088), 2)
    d.text((760, 1160), "separate impact dust FX 64x32, clean lines", fill=muted, font=F_SMALL)
    d.text((760, 1182), "B3 triggers shake contract, FX not baked into character sheet", fill=muted, font=F_SMALL)

    box(30, 1270, 1820, 250, "Gate report")
    lines = [
        "Status: animation_strip_candidate_generated_in_data_processed; not promoted to res/; not ResComp validated; not tested in emulator.",
        "Hero: 8-frame run_toward candidate, fixed 64x80 cells, pivot overlay and foot-contact report included.",
        "Pursuer: modular scale curve is identical for body/head/hoof; impact frame B3 owns the camera-shake trigger contract.",
        "Budget reading: cabe com recuo. Active animation window only; full review pack is not resident runtime policy.",
    ]
    y = 1325
    for line_text in lines:
        d.text((54, y), line_text, fill=muted, font=F_BODY)
        y += 30

    return board.convert("RGB")


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    hero_ref = load_p(PIXEL_LOCK / "hero_run_toward_64x80_pixel_lock_v002.png")
    hero_palette = palette16(hero_ref)
    hero_sources = {
        "c1": load_p(VARIANTS / "hero_component_1_box_64x80_pixel_lock_v002.png"),
        "c2": load_p(VARIANTS / "hero_component_2_box_64x80_pixel_lock_v002.png"),
        "c3": load_p(VARIANTS / "hero_component_3_box_64x80_pixel_lock_v002.png"),
    }

    cape_indices = {2, 3, 4}
    hero_plan = [
        {"id": "F0", "src": "c2", "mirror": False, "body": (0, 2), "cape": (-2, -1), "bottom": 78, "ticks": 4, "phase": "contact_down", "contact": True},
        {"id": "F1", "src": "c3", "mirror": False, "body": (0, 0), "cape": (-3, -4), "bottom": 77, "ticks": 3, "phase": "recoil", "contact": False},
        {"id": "F2", "src": "c3", "overlay_lower": "c1", "mirror": False, "body": (0, -2), "cape": (-2, -2), "bottom": 75, "ticks": 3, "phase": "z_pass", "contact": False},
        {"id": "F3", "src": "c3", "mirror": False, "body": (0, -1), "cape": (-1, 1), "bottom": 76, "ticks": 4, "phase": "recovery", "contact": False},
        {"id": "F4", "src": "c2", "mirror": True, "body": (0, 2), "cape": (2, -1), "bottom": 78, "ticks": 4, "phase": "contact_down", "contact": True},
        {"id": "F5", "src": "c3", "mirror": True, "body": (0, 0), "cape": (3, -4), "bottom": 77, "ticks": 3, "phase": "recoil", "contact": False},
        {"id": "F6", "src": "c3", "overlay_lower": "c1", "mirror": True, "body": (0, -2), "cape": (2, -2), "bottom": 75, "ticks": 3, "phase": "z_pass", "contact": False},
        {"id": "F7", "src": "c3", "mirror": True, "body": (0, -1), "cape": (1, 1), "bottom": 76, "ticks": 4, "phase": "recovery", "contact": False},
    ]

    hero_frames: list[Image.Image] = []
    hero_report_frames: list[dict] = []
    cogs: list[tuple[float, float]] = []
    contacts: list[tuple[float, int]] = []
    for item in hero_plan:
        src = hero_sources[item["src"]]
        if item["mirror"]:
            src = src.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        body = mask_indices(src, cape_indices, keep=False)
        cape = mask_indices(src, cape_indices, keep=True)
        frame_rgba = Image.new("RGBA", (64, 80), (0, 0, 0, 0))
        body_dx, body_dy = item["body"]
        cape_dx, cape_dy = item["cape"]
        paste_clipped(frame_rgba, body, body_dx, body_dy)
        paste_clipped(frame_rgba, cape, body_dx + cape_dx, body_dy + cape_dy)
        if item.get("overlay_lower"):
            lower_src = hero_sources[item["overlay_lower"]]
            if item["mirror"]:
                lower_src = lower_src.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            paste_clipped(frame_rgba, lower_layer(lower_src, 36), body_dx, body_dy)
        frame_p = normalize_hero_cell(rgba_to_p(frame_rgba, hero_palette), hero_palette, item["bottom"])
        hero_frames.append(frame_p)
        cog = alpha_centroid(frame_p, exclude_indices=cape_indices)
        contact = contact_point(frame_p)
        cogs.append(cog)
        contacts.append(contact)
        bbox = nonzero_bbox(frame_p)
        hero_report_frames.append(
            {
                "id": item["id"],
                "source_key_pose": item["src"],
                "overlay_lower_key_pose": item.get("overlay_lower"),
                "mirrored_for_cycle_study": item["mirror"],
                "duration_ticks": item["ticks"],
                "phase": item["phase"],
                "foot_contact": item["contact"],
                "body_offset": list(item["body"]),
                "cape_offset": list(item["cape"]),
                "desired_bottom_y": item["bottom"],
                "measured_bbox": list(bbox) if bbox else None,
                "measured_body_cog": [round(cog[0], 2), round(cog[1], 2)],
                "measured_contact_point": [round(contact[0], 2), contact[1]],
            }
        )

    hero_strip = strip(hero_frames, hero_palette)
    hero_overlay = draw_overlay_strip(hero_frames, cogs, contacts, hero_palette, 78)
    hero_strip_path = OUT / "hero_run_toward_64x80_strip_v003.png"
    hero_overlay_path = OUT / "hero_run_toward_pivot_overlay_v003.png"
    save_p_png(hero_strip, hero_strip_path)
    save_p_png(hero_overlay, hero_overlay_path)

    gif_frames: list[Image.Image] = []
    for frame, plan in zip(hero_frames, hero_plan):
        duration = plan["ticks"] * (1000 // 60)
        rgba = p_to_rgba(frame).resize((128, 160), Image.Resampling.NEAREST)
        gif_frames.extend([rgba] * max(1, round(duration / 16)))
    hero_gif_path = OUT / "hero_run_toward_preview_v003.gif"
    gif_frames[0].save(hero_gif_path, save_all=True, append_images=gif_frames[1:], duration=16, loop=0, disposal=2, transparency=0)

    pursuer_ref = load_p(PIXEL_LOCK / "pursuer_3q_front_mid_96x80_pixel_lock_v002.png")
    pursuer_palette = palette16(pursuer_ref)
    pursuer_body = load_p(PIXEL_LOCK / "pursuer_3q_front_mid_96x80_pixel_lock_v002.png")
    pursuer_head = load_p(PIXEL_LOCK / "pursuer_head_horns_modular_112x64_pixel_lock_v002.png")
    pursuer_hoof = load_p(PIXEL_LOCK / "pursuer_attack_hoof_modular_96x64_pixel_lock_v002.png")
    scale_curve = [
        {"id": "B0", "scale": 0.96, "ticks": 6, "impact": False},
        {"id": "B1", "scale": 1.00, "ticks": 5, "impact": False},
        {"id": "B2", "scale": 1.04, "ticks": 5, "impact": False},
        {"id": "B3", "scale": 1.08, "ticks": 7, "impact": True},
        {"id": "B4", "scale": 1.04, "ticks": 5, "impact": False},
        {"id": "B5", "scale": 1.00, "ticks": 5, "impact": False},
    ]
    body_frames = [scaled_content(pursuer_body, item["scale"], pursuer_palette, (96, 80)) for item in scale_curve]
    head_frames = [scaled_content(pursuer_head, item["scale"], pursuer_palette, (112, 64)) for item in scale_curve]
    hoof_frames = [scaled_content(pursuer_hoof, item["scale"], pursuer_palette, (96, 64)) for item in scale_curve]
    dust_frames = [draw_dust_frame((64, 32), i if item["impact"] else (1 if i == 4 else 0), pursuer_palette) for i, item in enumerate(scale_curve)]
    # Strong impact should be the third dust drawing regardless of curve index.
    dust_frames[3] = draw_dust_frame((64, 32), 2, pursuer_palette)
    dust_frames[4] = draw_dust_frame((64, 32), 3, pursuer_palette)

    body_strip = strip(body_frames, pursuer_palette)
    head_strip = strip(head_frames, pursuer_palette)
    hoof_strip = strip(hoof_frames, pursuer_palette)
    dust_strip = strip(dust_frames, pursuer_palette)
    body_path = OUT / "pursuer_3q_front_mid_96x80_zloop_strip_v003.png"
    head_path = OUT / "pursuer_head_horns_112x64_zloop_strip_v003.png"
    hoof_path = OUT / "pursuer_attack_hoof_96x64_zloop_strip_v003.png"
    dust_path = OUT / "pursuer_impact_dust_fx_64x32_strip_v003.png"
    for im, path in [(body_strip, body_path), (head_strip, head_path), (hoof_strip, hoof_path), (dust_strip, dust_path)]:
        save_p_png(im, path)

    report: dict = {
        "schema": "celestial_chase_animation_strip_candidate_v3",
        "status": "animation_strip_candidate_generated_pending_human_approval",
        "standard": "Source_Baked_Pixel_Art_Standard",
        "source_pixel_lock": str(PIXEL_LOCK / "pixel_lock_report_v002.json"),
        "blocking_statuses": [
            "not_promoted_to_res",
            "not_rescomp_validated",
            "not_tested_in_emulator",
            "pending_human_animation_approval",
        ],
        "hero": {
            "asset_id": "hero_run_toward",
            "cell_size": [64, 80],
            "frame_count": len(hero_frames),
            "total_cycle_ticks": sum(item["ticks"] for item in hero_plan),
            "playback_fps_basis": 60,
            "strip": str(hero_strip_path),
            "pivot_overlay": str(hero_overlay_path),
            "preview_gif": str(hero_gif_path),
            "pivot_contract": {
                "runtime_anchor": "top_left_constant_with_internal_bob",
                "centerline_x": 32,
                "ground_reference_y": 78,
                "contact_frames": ["F0", "F4"],
                "cape_follow_through": "cape reaches highest offset one frame after contact_down",
            },
            "frames": hero_report_frames,
        },
        "pursuer": {
            "asset_id": "clockwork_stag_modular_z_rig",
            "module_strips": {
                "body_mid": str(body_path),
                "head_horns": str(head_path),
                "attack_hoof": str(hoof_path),
                "impact_dust_fx": str(dust_path),
            },
            "scale_curve": [
                {
                    "id": item["id"],
                    "scale_percent": int(round(item["scale"] * 100)),
                    "scale_float": item["scale"],
                    "duration_ticks": item["ticks"],
                    "impact": item["impact"],
                }
                for item in scale_curve
            ],
            "sync_rule": "body_mid, head_horns and attack_hoof use the same scale curve per frame",
            "impact_frame_contract": {
                "frame_id": "B3",
                "dust_fx_frame": "D3",
                "camera_shake_trigger": "CHASE_SHAKE_BOSS_HOOF_IMPACT",
                "scroll_api_verified": "void VDP_setVerticalScroll(VDPPlane plane, s16 value)",
                "preferred_runtime_reset": "restore both affected planes to 0 after shake sequence",
                "shake_offsets_px": [2, -2, 1, -1, 0],
                "implementation_gate": "contract_only_no_code_written",
            },
        },
        "budget_decision": "cabe_com_recuo",
        "budget_notes": [
            "Animation pack is a review candidate; runtime must use active animation window, not every review asset resident.",
            "Impact dust is a separate FX strip to preserve character palette/material integrity.",
            "Mirrored hero frames are marked as cycle study candidates and require human review before source redraw/runtime promotion.",
        ],
    }

    outputs = {
        "hero_strip": hero_strip_path,
        "hero_overlay": hero_overlay_path,
        "hero_preview_gif": hero_gif_path,
        "pursuer_body_strip": body_path,
        "pursuer_head_strip": head_path,
        "pursuer_hoof_strip": hoof_path,
        "pursuer_dust_strip": dust_path,
    }
    validations: dict[str, dict] = {}
    for key, path in outputs.items():
        if path.suffix.lower() == ".png":
            im = load_p(path)
            frame_w = 64
            frame_h = im.height
            if "hero" in key:
                frame_w = 64
                frame_h = 80
            elif "body" in key:
                frame_w = 96
                frame_h = 80
            elif "head" in key:
                frame_w = 112
                frame_h = 64
            elif "hoof" in key:
                frame_w = 96
                frame_h = 64
            elif "dust" in key:
                frame_w = 64
                frame_h = 32
            unique_tiles, nonempty_tiles = tile_count_unique_nonempty(im, frame_w, frame_h)
            validations[key] = {
                "path": str(path),
                "sha256": sha256(path),
                "png": png_ihdr(path),
                "plte_entries": len(palette16(im)),
                "transparency": im.info.get("transparency"),
                "unique_nonempty_tiles_est": unique_tiles,
                "nonempty_tiles": nonempty_tiles,
            }
        else:
            validations[key] = {"path": str(path), "sha256": sha256(path)}
    report["validation"] = validations

    board = draw_board(report, hero_strip, hero_overlay, {"body": body_strip, "head": head_strip, "hoof": hoof_strip, "dust": dust_strip})
    board_path = OUT / "animation_strip_approval_board_v003.png"
    board.save(board_path, optimize=True)
    report["approval_board"] = str(board_path)
    report["approval_board_sha256"] = sha256(board_path)

    report_path = OUT / "animation_strip_candidate_report_v003.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    contracts = {
        "animation_direction_contract_v003.json": {
            "schema": "animation_direction_contract_v1",
            "status": "candidate_pending_human_approval",
            "hero_motion_principles": ["foot_contact_weight", "z_axis_limb_depth", "cape_follow_through"],
            "pursuer_motion_principles": ["synchronized_modular_scale", "impact_frame_weight", "separate_dust_fx"],
            "source": str(report_path),
        },
        "timing_spacing_report_v003.json": {
            "schema": "timing_spacing_report_v1",
            "status": "candidate_pending_human_approval",
            "hero_total_cycle_ticks": report["hero"]["total_cycle_ticks"],
            "hero_frames": hero_report_frames,
            "pursuer_scale_curve": report["pursuer"]["scale_curve"],
        },
        "pivot_and_scale_contract_v003.json": {
            "schema": "pivot_and_scale_contract_v1",
            "status": "candidate_pending_human_approval",
            "hero_pivot_contract": report["hero"]["pivot_contract"],
            "pursuer_sync_rule": report["pursuer"]["sync_rule"],
            "scale_curve": report["pursuer"]["scale_curve"],
        },
        "foot_contact_report_v003.json": {
            "schema": "foot_contact_report_v1",
            "status": "candidate_pending_human_approval",
            "contact_frames": ["F0", "F4"],
            "hero_frames": hero_report_frames,
        },
        "impact_frame_contract_v003.json": {
            "schema": "impact_frame_contract_v1",
            "status": "candidate_pending_human_approval",
            "pursuer_impact": report["pursuer"]["impact_frame_contract"],
        },
        "modular_boss_rig_contract_v003.json": {
            "schema": "modular_boss_rig_contract_v1",
            "status": "candidate_pending_human_approval",
            "modules": report["pursuer"]["module_strips"],
            "scale_curve": report["pursuer"]["scale_curve"],
            "sync_rule": report["pursuer"]["sync_rule"],
        },
    }
    for name, data in contracts.items():
        (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps({"report": str(report_path), "board": str(board_path), "outputs": {k: str(v) for k, v in outputs.items()}}, indent=2))


if __name__ == "__main__":
    build()
