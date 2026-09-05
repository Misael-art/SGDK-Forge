#!/usr/bin/env python3
"""Assemble branding_sequence_v2 phase-2 assets from authored sources.

Crop, nearest scale/rotate, chroma key, 9-bit posterize, palette remap, paste.
Does not draw silhouettes, volumes, light ramps or lineart.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from assemble_model_sheet import (  # noqa: E402
    EMBER_ANGLES,
    MAGENTA,
    PAL0,
    PAL1,
    PAL2,
    PAL3,
    SHARD_ANGLES,
    clean_rgb,
    content_bbox,
    extract_sprite,
    fit_contain,
    fit_cover,
    is_key,
    key_from_edges,
    load_rgb,
    nearest,
    persist_cleaned,
    remap_image,
    rotate_authored,
    sha256,
)
from compose_bg_b_tiles import TARGET_UNIQUE, compose_tile_budget  # noqa: E402

ROOT = HERE
RAW = HERE / "raw"
PROJ = HERE.parent.parent.parent
RES = PROJ / "res" / "branding"
LINEAGE = HERE / "asset_lineage_v2.json"


def new_indexed(size: tuple[int, int], palette: list[tuple[int, int, int]]) -> Image.Image:
    img = Image.new("P", size, 0)
    img.putpalette([c for rgb in palette for c in rgb] + [0, 0, 0] * (256 - len(palette)))
    return img


def remap_to_palette(
    src: Image.Image, palette: list[tuple[int, int, int]], *, key: bool = True
) -> Image.Image:
    allowed = list(range(1, 16))
    out = Image.new("P", src.size, 0)
    out.putpalette([c for rgb in palette for c in rgb] + [0, 0, 0] * (256 - 16))
    sp = src.load()
    op = out.load()
    for y in range(src.size[1]):
        for x in range(src.size[0]):
            rgb = sp[x, y]
            if key and is_key(rgb):
                op[x, y] = 0
                continue
            best_i, best_d = 1, 1 << 30
            for i in allowed:
                d = sum((rgb[k] - palette[i][k]) ** 2 for k in range(3))
                if d < best_d:
                    best_d = d
                    best_i = i
            op[x, y] = best_i
    return out


def remap_engine_logo(src: Image.Image) -> Image.Image:
    """Hue-aware PAL1 remap so the bottom silver step lands on 13-14."""
    out = Image.new("P", src.size, 0)
    out.putpalette([c for rgb in PAL1 for c in rgb] + [0, 0, 0] * 240)
    sp = src.load()
    op = out.load()
    h = src.size[1]
    for y in range(h):
        for x in range(src.size[0]):
            r, g, b = sp[x, y]
            if is_key((r, g, b)):
                op[x, y] = 0
                continue
            luma = 0.299 * r + 0.587 * g + 0.114 * b
            if luma < 22:
                op[x, y] = 15
                continue
            warm = r >= g + 10 and r >= b + 10
            cool = b >= r + 8
            grayish = abs(r - g) < 28 and abs(g - b) < 28
            lower = y > int(h * 0.55)
            if grayish and lower and luma > 90:
                op[x, y] = 14 if luma > 150 else 13
            elif warm:
                if luma > 190:
                    op[x, y] = 12
                elif luma > 140:
                    op[x, y] = 11
                elif luma > 100:
                    op[x, y] = 10
                else:
                    op[x, y] = 9
            elif cool:
                if luma < 50:
                    op[x, y] = 1
                elif luma < 80:
                    op[x, y] = 2
                else:
                    op[x, y] = 3
            else:
                # rust / mid iron body
                if luma < 70:
                    op[x, y] = 4
                elif luma < 110:
                    op[x, y] = 5
                else:
                    op[x, y] = 6
    return out


def fit_cover_bottom(src: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = src.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    resized = src.resize((nw, nh), Image.NEAREST)
    left = max(0, (nw - tw) // 2)
    top = max(0, nh - th)
    return resized.crop((left, top, left + tw, top + th))


def place_anvil_registered(src: Image.Image) -> Image.Image:
    """Put the anvil on a 320x224 magenta field with face center at (128, 104)."""
    img = key_from_edges(src)
    box = content_bbox(img, pad=2)
    anvil = img.crop(box)
    target_h = 148
    scale = target_h / anvil.size[1]
    nw = max(8, int(round(anvil.size[0] * scale)))
    nh = target_h
    anvil = anvil.resize((nw, nh), Image.NEAREST)
    # Face plate is the upper body, right of the beak.
    face_cx = int(nw * 0.58)
    face_cy = int(nh * 0.28)
    canvas = Image.new("RGB", (320, 224), MAGENTA)
    ox = 128 - face_cx
    oy = 104 - face_cy
    canvas.paste(anvil, (ox, oy))
    return canvas


def wordmark(src_path: Path, size: tuple[int, int], palette: list) -> Image.Image:
    img = key_from_edges(load_rgb(src_path))
    img = img.crop(content_bbox(img, pad=2))
    img = fit_contain(img, (size[0] - 4, size[1] - 4))
    canvas = Image.new("RGB", size, MAGENTA)
    ox = (size[0] - img.size[0]) // 2
    oy = (size[1] - img.size[1]) // 2
    canvas.paste(img, (ox, oy))
    return remap_to_palette(canvas, palette)


def sprite_cell(path: Path, cell: int) -> Image.Image:
    return extract_sprite(path, cell)


def save_indexed(img: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    pal = (img.getpalette() or [])[: 16 * 3]
    pal.extend([0] * (16 * 3 - len(pal)))
    out = Image.new("P", img.size, 0)
    out.putpalette(pal)
    out.putdata(list(img.getdata()))
    out.save(dest, format="PNG", transparency=0)


def build() -> dict:
    RES.mkdir(parents=True, exist_ok=True)
    sources = {
        "bg_b": RAW / "forge_bg_b_v02.jpg",
        "anvil": RAW / "forge_anvil_iso_v01.jpg",
        "logo_engine": RAW / "logo_forge_v02.jpg",
        "logo_author": RAW / "logo_misael_v01.jpg",
        "logo_project": RAW / "logo_master_v01.jpg",
        "presents": RAW / "presents_v01.jpg",
        "hammer_rest": RAW / "hammer_rest_v02.jpg",
        "hammer_down1": RAW / "hammer_frames" / "f008.png",
        "hammer_down2": RAW / "hammer_frames" / "f018.png",
        "hammer_smear": RAW / "hammer_smear_v01.jpg",
        "hammer_recoil": RAW / "hammer_frames" / "f045.png",
        "hammer_settle": RAW / "hammer_frames" / "f055.png",
        "ember": RAW / "ember_v04.jpg",
        "ember_squash": RAW / "ember_squash_v01.jpg",
        "ember_settle": RAW / "ember_settle_v01.jpg",
        "shard": RAW / "shard_v05.jpg",
    }
    for p in sources.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    cleaned = {n: persist_cleaned(p) if p.suffix.lower() in {".jpg", ".jpeg"} else p for n, p in sources.items()}

    outputs: dict[str, Path] = {}

    # 1. BG_A props — anvil registered, no hammer
    bga_rgb = place_anvil_registered(load_rgb(sources["anvil"]))
    bga = remap_to_palette(bga_rgb, PAL0)
    outputs["img_forge_bg_a_props"] = RES / "forge_bg_a_props_320x224.png"
    save_indexed(bga, outputs["img_forge_bg_a_props"])

    # 2. BG_B — interior, then authored-tile collapse to the 644 budget
    bgb_rgb = fit_cover_bottom(load_rgb(sources["bg_b"]), (320, 224))
    bgb = remap_to_palette(bgb_rgb, PAL0, key=False)
    bgb, bgb_tile_report = compose_tile_budget(bgb, TARGET_UNIQUE)
    outputs["img_forge_bg_b"] = RES / "forge_bg_b_320x224.png"
    save_indexed(bgb, outputs["img_forge_bg_b"])
    (HERE / "bg_b_tile_compose_report.json").write_text(
        json.dumps(bgb_tile_report, indent=2), encoding="utf-8"
    )

    # 3. Engine logo — PAL1, 224x64
    outputs["img_logo_engine_v2"] = RES / "logo_engine_224x64.png"
    eng = key_from_edges(load_rgb(sources["logo_engine"]))
    eng = eng.crop(content_bbox(eng, pad=2))
    eng = fit_contain(eng, (220, 60))
    eng_c = Image.new("RGB", (224, 64), MAGENTA)
    eng_c.paste(eng, ((224 - eng.size[0]) // 2, (64 - eng.size[1]) // 2))
    save_indexed(remap_engine_logo(eng_c), outputs["img_logo_engine_v2"])

    # 4. Hammer 7-frame strip 48x48
    frames_h = [
        sprite_cell(sources["hammer_rest"], 48),
        rotate_authored(extract_sprite(sources["hammer_rest"], 48), -22),
        sprite_cell(sources["hammer_down1"], 48),
        sprite_cell(sources["hammer_down2"], 48),
        sprite_cell(sources["hammer_smear"], 48),
        sprite_cell(sources["hammer_recoil"], 48),
        sprite_cell(sources["hammer_settle"], 48),
    ]
    hammer = new_indexed((48 * 7, 48), PAL1)
    hp = hammer.load()
    for i, src_img in enumerate(frames_h):
        cell = remap_to_palette(src_img, PAL1)
        cp = cell.load()
        for y in range(48):
            for x in range(48):
                hp[i * 48 + x, y] = cp[x, y]
    outputs["spr_forge_hammer"] = RES / "spr_forge_hammer_48x48_strip.png"
    save_indexed(hammer, outputs["spr_forge_hammer"])

    # 5. Ember 6 frames
    ember0 = extract_sprite(sources["ember"], 16)
    ember_frames = [rotate_authored(ember0, a) for a in EMBER_ANGLES]
    ember_frames.append(extract_sprite(sources["ember_squash"], 16))
    ember_frames.append(extract_sprite(sources["ember_settle"], 16))
    ember_strip = new_indexed((16 * 6, 16), PAL3)
    ep = ember_strip.load()
    for i, fr in enumerate(ember_frames):
        cell = remap_to_palette(fr, PAL3)
        cp = cell.load()
        for y in range(16):
            for x in range(16):
                ep[i * 16 + x, y] = cp[x, y]
    outputs["spr_forge_ember"] = RES / "spr_forge_ember_16x16_strip.png"
    save_indexed(ember_strip, outputs["spr_forge_ember"])

    # 6. Shard 4 frames
    shard0 = extract_sprite(sources["shard"], 16)
    shard_frames = [rotate_authored(shard0, a) for a in SHARD_ANGLES]
    shard_strip = new_indexed((16 * 4, 16), PAL3)
    sp = shard_strip.load()
    for i, fr in enumerate(shard_frames):
        cell = remap_to_palette(fr, PAL3)
        cp = cell.load()
        for y in range(16):
            for x in range(16):
                sp[i * 16 + x, y] = cp[x, y]
    outputs["spr_forge_shard"] = RES / "spr_forge_shard_16x16_strip.png"
    save_indexed(shard_strip, outputs["spr_forge_shard"])

    # 7-9 wordmarks PAL2
    outputs["img_logo_author_v2"] = RES / "logo_author_192x32.png"
    save_indexed(wordmark(sources["logo_author"], (192, 32), PAL2), outputs["img_logo_author_v2"])
    outputs["img_logo_project_v2"] = RES / "logo_project_224x48.png"
    save_indexed(wordmark(sources["logo_project"], (224, 48), PAL2), outputs["img_logo_project_v2"])
    outputs["img_presents_text_v2"] = RES / "presents_text_96x16.png"
    save_indexed(wordmark(sources["presents"], (96, 16), PAL2), outputs["img_presents_text_v2"])

    lineage = {
        "schema": "asset_lineage_record.v1",
        "phase": "branding_sequence_v2_assets",
        "generation_channel": "native_chat_image_generation_callable",
        "procedural_generation_used_as_asset_source": False,
        "assembler": "assemble_branding_v2_assets.py",
        "source_format_decision": {
            "choice": "keep_jpg_then_posterize_denoise_before_remap",
            "persist_cleaned_png_lossless": True,
        },
        "authored_sources": {
            name: {
                "path": str(path.relative_to(PROJ) if path.is_relative_to(PROJ) else path),
                "sha256": sha256(path),
            }
            for name, path in sources.items()
        },
        "outputs": {
            name: {
                "path": str(path.relative_to(PROJ)),
                "sha256": sha256(path),
                "size": list(Image.open(path).size),
            }
            for name, path in outputs.items()
        },
    }
    LINEAGE.write_text(json.dumps(lineage, indent=2), encoding="utf-8")
    for name, path in outputs.items():
        im = Image.open(path)
        print(f"{name}: {im.size} mode={im.mode}")
    return lineage


if __name__ == "__main__":
    build()
