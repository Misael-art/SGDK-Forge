#!/usr/bin/env python3
"""Slice the SF HUD sheet into SGDK sprites for HAMOOPIG energy bars + KO.

Source is the user-provided CPS HUD atlas (shezzor rip). Yellow = energiaBase
(instant). Red = energia (delayed). 13 frames of 8px depletion match
FUNCAO_BARRAS_DE_ENERGIA. P2 uses hardware HFlip of the P1 bar.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent / "sf_hud_sheet.png"
OUT = ROOT / "res/sprite/hud"
REPORT = ROOT / "rascunho/sf_hud_convert_report.json"
RES = ROOT / "res/hud_gfx.res"

MAGENTA = (255, 0, 255)
SNAP = 34
YELLOW_BOX = (16, 18, 168, 34)
RED_BOX = (16, 4, 168, 20)
KO_BOX = (155, 1, 200, 24)
BAR_W, BAR_H = 128, 16
FRAMES = 13  # 96 energy / 8px


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snap9(c):
    return tuple(max(0, min(238, int(round(v / SNAP) * SNAP))) for v in c)


def to_indexed(im: Image.Image, colors: list[tuple[int, int, int]]) -> Image.Image:
    pal = [MAGENTA] + colors[:15]
    while len(pal) < 16:
        pal.append((0, 0, 0))
    raw = []
    for c in pal:
        raw.extend(c)
    raw.extend([0, 0, 0] * (256 - 16))
    out = Image.new("P", im.size)
    out.putpalette(raw)
    sp = im.load()
    dp = out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = sp[x, y]
            if a < 16 or (r, g, b) == MAGENTA:
                dp[x, y] = 0
                continue
            s = snap9((r, g, b))
            best, bd = 1, 10**9
            for i, c in enumerate(pal):
                if i == 0:
                    continue
                d = sum((s[k] - c[k]) ** 2 for k in range(3))
                if d < bd:
                    bd = d
                    best = i
            dp[x, y] = best
    out.info["transparency"] = 0
    return out, pal


def layer_bar(src: Image.Image, kind: str) -> Image.Image:
    box = YELLOW_BOX if kind == "yellow" else RED_BOX
    crop = src.crop(box).convert("RGBA")
    px = crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, a = px[x, y]
            if a < 16:
                px[x, y] = MAGENTA + (0,)
    canvas = Image.new("RGBA", (BAR_W, BAR_H), MAGENTA + (0,))
    # keep the inner (right) cap that faces KO; clip the outer extra width
    x = min(0, BAR_W - crop.width)
    y = max(0, (BAR_H - crop.height) // 2)
    canvas.paste(crop, (x, y), crop)
    return canvas


def deplete(im: Image.Image, frame: int) -> Image.Image:
    """Hide the inner (right) end of the P1 bar as health drops."""
    canvas = im.copy()
    if frame <= 0:
        return canvas
    hide = int(round(BAR_W * frame / (FRAMES - 1)))
    px = canvas.load()
    x0 = max(0, BAR_W - hide)
    for y in range(BAR_H):
        for x in range(x0, BAR_W):
            px[x, y] = MAGENTA + (0,)
    return canvas


def pad_ko(src: Image.Image) -> Image.Image:
    crop = src.crop(KO_BOX).convert("RGBA")
    px = crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, a = px[x, y]
            if a < 16:
                px[x, y] = MAGENTA + (0,)
    cw = ((crop.width + 7) // 8) * 8
    ch = ((crop.height + 7) // 8) * 8
    canvas = Image.new("RGBA", (cw, ch), MAGENTA + (0,))
    canvas.paste(crop, ((cw - crop.width) // 2, (ch - crop.height) // 2), crop)
    return canvas


def main() -> None:
    src = Image.open(SRC).convert("RGBA")
    OUT.mkdir(parents=True, exist_ok=True)
    yellow = layer_bar(src, "yellow")
    red = layer_bar(src, "red")
    colors = []
    for im in (yellow, red):
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a >= 16 and (r, g, b) != MAGENTA:
                    c = snap9((r, g, b))
                    if c not in colors:
                        colors.append(c)

    y_frames = [deplete(yellow, i) for i in range(FRAMES)]
    r_frames = [deplete(red, i) for i in range(FRAMES)]
    ko = pad_ko(src)

    def save_strip(frames, name):
        w, h = frames[0].size
        strip = Image.new("RGBA", (w * len(frames), h), MAGENTA + (0,))
        for i, fr in enumerate(frames):
            strip.paste(fr, (i * w, 0), fr)
        indexed, pal = to_indexed(strip, colors)
        path = OUT / name
        indexed.save(path)
        return path, pal, w, h, len(frames)

    y_path, pal, yw, yh, yn = save_strip(y_frames, "energy_yellow.png")
    r_path, _, rw, rh, rn = save_strip(r_frames, "energy_red.png")
    ko_idx, _, = to_indexed(ko, colors)[:2]
    ko_path = OUT / "ko.png"
    ko_idx.save(ko_path)

    tw, th = yw // 8, yh // 8
    ktw, kth = ko_idx.size[0] // 8, ko_idx.size[1] // 8
    res = "\n".join(
        [
            "ALIGN",
            "// SF HUD bars + KO from user sheet (placeholder / prototype)",
            f'SPRITE spr_hud_energy_y  "sprite/hud/energy_yellow.png"  {tw}  {th} FAST 0',
            f'SPRITE spr_hud_energy_r  "sprite/hud/energy_red.png"     {tw}  {th} FAST 0',
            f'SPRITE spr_hud_ko        "sprite/hud/ko.png"             {ktw}  {kth} FAST 0',
            "",
        ]
    )
    RES.write_text(res, encoding="utf-8")
    info = {
        "source": str(SRC),
        "source_sha256": sha(SRC),
        "bar_px": [BAR_W, BAR_H],
        "frames": FRAMES,
        "yellow": sha(y_path),
        "red": sha(r_path),
        "ko": sha(ko_path),
        "ko_px": list(ko_idx.size),
        "nearest_resize": True,
        "p2_uses_hflip": True,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
