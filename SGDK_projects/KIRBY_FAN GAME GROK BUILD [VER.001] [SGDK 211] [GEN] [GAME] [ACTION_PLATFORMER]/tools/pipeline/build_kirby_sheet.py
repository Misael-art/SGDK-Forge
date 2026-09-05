#!/usr/bin/env python3
"""Convert AI Kirby sheet → SGDK 256×32 indexed sprite (8 frames × 32×32).

HARD RULES (L-013 / VDP sprite keying):
  - Palette index 0 = hardware transparency ONLY
  - Body pinks NEVER written as 0 (indices 1–5)
  - Key detection: strict magenta (high R, high B, LOW G ≤73) — not skin
  - Gate per frame: center 12×12 idx0 < 5% AND opaque > 35%
  - Refuse install if any frame fails

Usage:
  python3 tools/pipeline/build_kirby_sheet.py
  python3 tools/pipeline/build_kirby_sheet.py --install
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RAW_DEFAULT = ROOT / "data" / "source_art" / "ai_raw" / "r1" / "kirby_sheet.jpg"
OUT_DIR = ROOT / "data" / "source_art" / "ai_quantized" / "r2"

LATTICE = np.array([0, 36, 73, 109, 146, 182, 219, 255], dtype=np.int16)
PAL2 = [
    (255, 0, 255),  # 0 KEY
    (255, 219, 255),
    (255, 182, 219),
    (255, 146, 182),
    (219, 73, 146),
    (146, 36, 109),
    (109, 36, 73),
    (219, 73, 73),
    (146, 36, 36),
    (36, 36, 73),
    (255, 255, 255),
    (146, 146, 146),
    (255, 146, 182),
    (255, 219, 146),
    (182, 109, 219),
    (109, 219, 219),
]


def snap(rgb: np.ndarray) -> np.ndarray:
    out = rgb.astype(np.int16)
    for c in range(3):
        d = np.abs(out[..., c : c + 1] - LATTICE[None, None, :])
        out[..., c] = LATTICE[d.argmin(-1)]
    return out.astype(np.uint8)


def is_sheet_key(rgb: np.ndarray) -> np.ndarray:
    r, g, b = (
        rgb[..., 0].astype(np.int16),
        rgb[..., 1].astype(np.int16),
        rgb[..., 2].astype(np.int16),
    )
    return (r >= 182) & (b >= 146) & (g <= 73) & (np.abs(r - b) <= 109)


def flood_key_from_edges(key_mask: np.ndarray) -> np.ndarray:
    h, w = key_mask.shape
    vis = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            if key_mask[y, x] and not vis[y, x]:
                vis[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if key_mask[y, x] and not vis[y, x]:
                vis[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and not vis[ny, nx] and key_mask[ny, nx]:
                vis[ny, nx] = True
                q.append((ny, nx))
    return vis


def to_indexed(indices: np.ndarray) -> Image.Image:
    im = Image.fromarray(indices, mode="P")
    flat: list[int] = []
    for c in PAL2:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - 16))
    im.putpalette(flat[:768])
    return im


def build(raw_path: Path) -> tuple[Image.Image, dict]:
    raw = snap(np.array(Image.open(raw_path).convert("RGB")))
    key_all = is_sheet_key(raw)
    content = ~key_all
    rows = np.where(content.any(1))[0]
    cols = np.where(content.any(0))[0]
    crop = raw[int(rows[0]) : int(rows[-1]) + 1, int(cols[0]) : int(cols[-1]) + 1]

    n = 6
    cw = max(1, crop.shape[1] // n)
    frames: list[np.ndarray] = []
    for i in range(n):
        cell = crop[:, i * cw : (i + 1) * cw if i < n - 1 else crop.shape[1]]
        nm = ~is_sheet_key(cell)
        if nm.any():
            rr = np.where(nm.any(1))[0]
            cc = np.where(nm.any(0))[0]
            sub = cell[rr[0] : rr[-1] + 1, cc[0] : cc[-1] + 1]
        else:
            sub = cell
        ch, cw2 = sub.shape[:2]
        scale = 26 / max(ch, cw2)
        nh, nw = max(1, int(ch * scale)), max(1, int(cw2 * scale))
        scaled = np.array(Image.fromarray(sub).resize((nw, nh), Image.Resampling.NEAREST))
        canvas = np.zeros((32, 32, 3), dtype=np.uint8)
        canvas[:] = (255, 0, 255)
        oy, ox = (32 - nh) // 2, (32 - nw) // 2
        canvas[oy : oy + nh, ox : ox + nw] = scaled
        frames.append(snap(canvas))

    order = [0, 1, 2, 1, 3, 4, 5, 5]
    sheet = np.zeros((32, 256), dtype=np.uint8)
    reports: list[dict] = []

    for fi, si in enumerate(order):
        fr = frames[si]
        key = is_sheet_key(fr)
        key |= (fr[..., 0] == 255) & (fr[..., 1] == 0) & (fr[..., 2] == 255)
        key |= (fr[..., 0] >= 219) & (fr[..., 2] >= 182) & (fr[..., 1] <= 36)

        bg = flood_key_from_edges(key)
        character = ~bg
        for _ in range(4):
            nxt = character.copy()
            for y in range(1, 31):
                for x in range(1, 31):
                    if not character[y, x] and character[y - 1 : y + 2, x - 1 : x + 2].sum() >= 5:
                        nxt[y, x] = True
            character = nxt
        character[0, :] = character[-1, :] = character[:, 0] = character[:, -1] = False

        r = fr[..., 0].astype(np.int16)
        g = fr[..., 1].astype(np.int16)
        b = fr[..., 2].astype(np.int16)
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        yy = np.arange(32)[:, None]

        indices = np.zeros((32, 32), dtype=np.uint8)
        if character.any():
            pl = lum[character]
            t = (pl - pl.min()) / (pl.max() - pl.min() + 1e-6)
            bins = np.clip((1.0 - t) * 4.0, 0, 4).astype(int) + 1
            indices[character] = bins.astype(np.uint8)

        eyes = character & (lum < 70) & (yy < 18)
        indices[eyes] = 9
        feet = character & (yy >= 24) & (r > g + 5)
        indices[feet] = 7
        for y in range(1, 31):
            for x in range(1, 31):
                if character[y, x] and indices[y, x] in (1, 2, 3, 4, 5):
                    if not (
                        character[y - 1, x]
                        and character[y + 1, x]
                        and character[y, x - 1]
                        and character[y, x + 1]
                    ):
                        indices[y, x] = 6
        indices[character & (r > 230) & (g > 220) & (b > 220)] = 10
        indices[character & (indices == 0)] = 2
        indices[~character] = 0

        sheet[:, fi * 32 : (fi + 1) * 32] = indices
        center = indices[10:22, 10:22]
        rep = {
            "frame": fi,
            "opaque_pct": float((indices > 0).mean() * 100),
            "idx0_center_pct": float((center == 0).mean() * 100),
            "center_unique": [int(x) for x in np.unique(center)],
        }
        rep["gate"] = (
            "PASS"
            if rep["idx0_center_pct"] < 5.0 and rep["opaque_pct"] > 35.0
            else "FAIL"
        )
        reports.append(rep)

    all_pass = all(r["gate"] == "PASS" for r in reports)
    return to_indexed(sheet), {"all_pass": all_pass, "frames": reports}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW_DEFAULT)
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    im, report = build(args.raw)
    path = OUT_DIR / "kirby_sheet_r3.png"
    im.save(path)
    im.resize((1024, 128), Image.Resampling.NEAREST).save(OUT_DIR / "kirby_sheet_r3_x4.png")
    (OUT_DIR / "kirby_r3_gate.json").write_text(json.dumps(report, indent=2) + "\n")
    for r in report["frames"]:
        print(
            f"frame{r['frame']}: opaque={r['opaque_pct']:.1f}% "
            f"center_idx0={r['idx0_center_pct']:.1f}% {r['gate']}"
        )
    print("ALL", report["all_pass"])
    if args.install:
        if not report["all_pass"]:
            print("REFUSED install")
            return 1
        im.save(ROOT / "res" / "sprites" / "ph_kirby.png")
        im.save(ROOT / "res" / "sprites" / "kirby_r3_candidate.png")
        print("INSTALLED res/sprites/ph_kirby.png")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
