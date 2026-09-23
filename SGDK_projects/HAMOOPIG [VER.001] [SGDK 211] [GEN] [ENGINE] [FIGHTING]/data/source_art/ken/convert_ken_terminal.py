#!/usr/bin/env python3
"""Translate authored Ken terminal poses to indexed Mega Drive sprites."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = Path(__file__).resolve().parent
OUT = ROOT / "res/sprite/ken"
REPORT = ROOT / "rascunho/ken_terminal_convert_report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def indexed_palette() -> tuple[list[tuple[int, int, int]], list[int]]:
    base = Image.open(OUT / "100.png")
    raw = base.getpalette()[:48]
    colors = [tuple(raw[i : i + 3]) for i in range(0, 48, 3)]
    full = list(raw) + [0, 0, 0] * (256 - 16)
    return colors, full


def crop_alpha(im: Image.Image) -> Image.Image:
    alpha = im.getchannel("A")
    box = alpha.getbbox()
    if box is None:
        raise SystemExit("terminal source contains no visible pixels")
    return im.crop(box)


def nearest_index(rgb: tuple[int, int, int], colors: list[tuple[int, int, int]]) -> int:
    best = 1
    best_d = 10**12
    for i, c in enumerate(colors[1:], 1):
        d = sum((int(rgb[k]) - int(c[k])) ** 2 for k in range(3))
        if d < best_d:
            best_d = d
            best = i
    return best


def convert(src: Path, dst: Path, cell: tuple[int, int], colors: list[tuple[int, int, int]], raw: list[int]) -> dict:
    im = crop_alpha(Image.open(src).convert("RGBA"))
    cw, ch = cell
    scale = min((cw - 8) / im.width, (ch - 8) / im.height)
    if scale <= 0:
        raise SystemExit(f"invalid scale for {src}")
    size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    im = im.resize(size, Image.Resampling.NEAREST)
    out = Image.new("P", (cw, ch), 0)
    out.putpalette(raw)
    px = im.load()
    dp = out.load()
    ox = (cw - im.width) // 2
    oy = ch - im.height
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a >= 16:
                dp[ox + x, oy + y] = nearest_index((r, g, b), colors)
    out.info["transparency"] = 0
    out.save(dst)
    return {
        "source": str(src.relative_to(ROOT)),
        "source_sha256": sha256(src),
        "output": str(dst.relative_to(ROOT)),
        "output_sha256": sha256(dst),
        "cell": [cw, ch],
        "visible_source_bbox": [im.width, im.height],
        "scale": scale,
        "visible_colors": len({p for p in out.getdata() if p != 0}),
    }


def main() -> None:
    colors, raw = indexed_palette()
    outputs = {
        "victory_v1.png": ("ken_terminal_victory_source_v1.png", (96, 128)),
        "defeat_v1.png": ("ken_terminal_defeat_source_v1.png", (128, 96)),
    }
    report = {
        "status": "source_candidate",
        "tool": "built-in image_gen plus indexed nearest-palette conversion",
        "palette_source": "res/sprite/ken/100.png",
        "outputs": {},
    }
    for name, (source_name, cell) in outputs.items():
        report["outputs"][name] = convert(SRC_DIR / source_name, OUT / name, cell, colors, raw)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
