#!/usr/bin/env python3
"""Convert HAMOOPI GPL sounds and HUD art into SGDK-ready files for the 2.11 port.

Sources stay in rascunho/upstream_reference/hamoopi_gpl (Daniel Moura, GPL v2).
Outputs:
  res/snd/*.wav          16 kHz 16-bit mono PCM for WAV XGM
  res/sprite/hud/n0-n9.png  16x16 indexed, remapped to PAL1
  res/sprite/hud/sombra.png 64x16 indexed, remapped to PAL1
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
HAMOOPI = ROOT / "rascunho/upstream_reference/hamoopi_gpl"
SOUNDS = HAMOOPI / "sounds"
SYSTEM = HAMOOPI / "system"
OUT_SND = ROOT / "res/snd"
OUT_HUD = ROOT / "res/sprite/hud"
PAL_SRC = ROOT / "res/sprite/point.png"
RYO_SRC = ROOT / "res/sprite/ryo/100.png"
TOOLS = Path("/mnt/sdcard/Projects/Sgdk Forge/tools/audio-tools")
sys.path.insert(0, str(TOOLS))
from audio_core import read_wav, resample_samplerate, wav_info, write_wav  # noqa: E402

TARGET_RATE = 16000
MAX_SECONDS = 0.90

SOUND_MAP = {
    "snd_101": "attacklvl1.wav",
    "snd_101b": "attacklvl1.wav",
    "snd_102": "attacklvl2.wav",
    "snd_102b": "attacklvl2.wav",
    "snd_110": "attacklvl3.wav",
    "snd_151": "attacklvl3.wav",
    "snd_300": "cursor.wav",
    "snd_501": "hitlvl1.wav",
    "snd_502": "hitlvl2.wav",
    "snd_551": "hitlvl3.wav",
    "snd_606": "ko.wav",
    "snd_confirm": "confirm.wav",
    "snd_haohmaru_618": "fight.wav",
    "snd_ryo_700": "fight.wav",
    "snd_ryo_710": "round1.wav",
    "snd_ryo_720": "round2.wav",
    "snd_ryo_730": "round3.wav",
}

MAGENTA = (255, 0, 255)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def pal1_colors() -> list[tuple[int, int, int]]:
    im = Image.open(PAL_SRC)
    pal = im.getpalette()
    return [(pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2]) for i in range(16)]


def nearest_pal1(rgb: tuple[int, int, int], colors: list[tuple[int, int, int]]) -> int:
    if rgb[0] >= 250 and rgb[1] <= 5 and rgb[2] >= 250:
        return 0
    best = 1
    best_d = 10**9
    for i, (r, g, b) in enumerate(colors):
        if i == 0:
            continue
        d = (rgb[0] - r) ** 2 + (rgb[1] - g) ** 2 + (rgb[2] - b) ** 2
        if d < best_d:
            best_d = d
            best = i
    return best


def remap_to_pal1(im: Image.Image, colors: list[tuple[int, int, int]], size: tuple[int, int]) -> Image.Image:
    rgba = im.convert("RGBA")
    # Magenta (HAMOOPI trans) and fully-transparent become index 0.
    w, h = rgba.size
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 16 or (r >= 250 and g <= 8 and b >= 250):
                px[x, y] = (0, 0, 0, 0)
    rgba = rgba.resize(size, Image.Resampling.LANCZOS)
    out = Image.new("P", size)
    pal = []
    for r, g, b in colors:
        pal.extend([r, g, b])
    pal.extend([0, 0, 0] * (256 - 16))
    out.putpalette(pal)
    src = rgba.load()
    dst = out.load()
    for y in range(size[1]):
        for x in range(size[0]):
            r, g, b, a = src[x, y]
            dst[x, y] = 0 if a < 16 else nearest_pal1((r, g, b), colors)
    out.info["transparency"] = 0
    return out


def convert_digits(colors: list[tuple[int, int, int]]) -> dict:
    OUT_HUD.mkdir(parents=True, exist_ok=True)
    report = {}
    for i in range(10):
        src = SYSTEM / f"spr_num_{i}.pcx"
        dst = OUT_HUD / f"n{i}.png"
        im = Image.open(src)
        remap_to_pal1(im, colors, (16, 16)).save(dst)
        report[f"spr_n{i}"] = {
            "source": str(src.relative_to(ROOT)),
            "output": str(dst.relative_to(ROOT)),
            "source_sha256": sha256(src),
            "output_sha256": sha256(dst),
        }
    return report


def convert_shadow(colors: list[tuple[int, int, int]]) -> dict:
    """Flatten the first ryo idle frame into a 64x16 ground blob on PAL1."""
    OUT_HUD.mkdir(parents=True, exist_ok=True)
    src = Image.open(RYO_SRC).convert("RGBA")
    # First frame of the walk/idle strip (sheet is 5 frames of 24? wait 100.png is a strip)
    frame_w = 80
    if src.width >= frame_w * 2:
        src = src.crop((0, 0, frame_w, src.height))
    # Build occupancy mask (non-magenta)
    mask = Image.new("L", src.size, 0)
    sp = src.load()
    mp = mask.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = sp[x, y]
            if a >= 16 and not (r >= 250 and g <= 8 and b >= 250):
                mp[x, y] = 255
    mask = mask.resize((64, 8), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
    canvas = Image.new("P", (64, 16))
    pal = []
    for r, g, b in colors:
        pal.extend([r, g, b])
    pal.extend([0, 0, 0] * (256 - 16))
    canvas.putpalette(pal)
    cp = canvas.load()
    mp = mask.load()
    for y in range(16):
        for x in range(64):
            my = min(7, max(0, y - 4))
            v = mp[x, my]
            if v < 40:
                cp[x, y] = 0
            elif v < 120:
                cp[x, y] = 1  # dark red as soft edge
            else:
                cp[x, y] = 4  # black body
    dst = OUT_HUD / "sombra.png"
    canvas.info["transparency"] = 0
    canvas.save(dst)
    return {
        "spr_sombra": {
            "source": str(RYO_SRC.relative_to(ROOT)),
            "output": str(dst.relative_to(ROOT)),
            "source_sha256": sha256(RYO_SRC),
            "output_sha256": sha256(dst),
            "method": "silhouette_flatten_from_ryo_100_first_frame",
        }
    }


def convert_sounds() -> dict:
    OUT_SND.mkdir(parents=True, exist_ok=True)
    report = {}
    for symbol, fname in SOUND_MAP.items():
        src = SOUNDS / fname
        samples = read_wav(src)
        info = wav_info(src)
        samples = resample_samplerate(samples, info["sample_rate"], TARGET_RATE)
        max_n = int(TARGET_RATE * MAX_SECONDS)
        if len(samples) > max_n:
            samples = samples[:max_n]
        dst = OUT_SND / f"{symbol}.wav"
        write_wav(dst, samples, TARGET_RATE)
        report[symbol] = {
            "source": str(src.relative_to(ROOT)),
            "output": str(dst.relative_to(ROOT)),
            "source_sha256": sha256(src),
            "output_sha256": sha256(dst),
            "source_rate": info["sample_rate"],
            "output_rate": TARGET_RATE,
            "samples": len(samples),
        }
    return report


def main() -> None:
    colors = pal1_colors()
    report = {
        "tool": "convert_hamoopi_complements.py",
        "license": "HAMOOPI GPL v2 (Daniel Moura / GameDevBoss)",
        "sounds": convert_sounds(),
        "digits": convert_digits(colors),
        "shadow": convert_shadow(colors),
    }
    out = ROOT / "rascunho/upstream_reference/hamoopi_complement_convert_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(out)}, indent=2))


if __name__ == "__main__":
    main()
