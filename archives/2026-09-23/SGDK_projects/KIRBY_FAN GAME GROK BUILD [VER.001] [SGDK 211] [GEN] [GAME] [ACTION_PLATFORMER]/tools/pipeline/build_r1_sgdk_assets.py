#!/usr/bin/env python3
"""Build R1 AI assets into SGDK-ready indexed PNGs with canonical palettes.

Fixes L-009: AI magenta key was snapped to non-zero pink indices → solid box
behind the sprite. This script forces:

  * flood-fill transparency from image edges
  * optional chroma key (magenta-ish)
  * remap opaque pixels to the project's PAL0/PAL1/PAL2 (doc/PALETTES.md)
  * index 0 = KEY (255,0,255) everywhere

Outputs overwrite res/gfx/ph_*.png and res/sprites/ph_kirby.png only when
--install is passed; otherwise writes under data/source_art/ai_quantized/r2/.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "source_art" / "ai_raw" / "r1"
OUT = ROOT / "data" / "source_art" / "ai_quantized" / "r2"
LATTICE = (0, 36, 73, 109, 146, 182, 219, 255)
KEY = (255, 0, 255)

# Canonical palettes from data/builders/build_placeholder_art.py / PALETTES.md
PAL0 = [
    KEY,
    (109, 182, 255),
    (146, 182, 255),
    (182, 219, 255),
    (219, 219, 255),
    (255, 219, 182),
    (255, 255, 182),
    (255, 255, 255),
    (219, 219, 255),
    (146, 146, 182),
    (109, 109, 146),
    (109, 182, 73),
    (73, 146, 73),
    (36, 109, 36),
    (109, 73, 36),
    (36, 36, 73),
]
PAL1 = [
    KEY,
    (73, 182, 73),
    (36, 146, 36),
    (36, 109, 36),
    (146, 109, 73),
    (109, 73, 36),
    (73, 36, 0),
    (36, 36, 36),
    (109, 182, 255),
    (182, 219, 255),
    (255, 255, 255),
    (146, 146, 146),
    (255, 182, 219),
    (255, 255, 146),
    (36, 109, 36),
    (0, 73, 36),
]
PAL2 = [
    KEY,
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


def snap_rgb333(rgb: np.ndarray) -> np.ndarray:
    levels = np.array(LATTICE, dtype=np.int16)
    out = rgb.astype(np.int16)
    for c in range(3):
        d = np.abs(out[..., c : c + 1] - levels[None, None, :])
        out[..., c] = levels[d.argmin(axis=-1)]
    return out.astype(np.uint8)


def is_magenta_key(rgb: np.ndarray, tol: int = 55) -> np.ndarray:
    r, g, b = rgb[..., 0].astype(np.int16), rgb[..., 1].astype(np.int16), rgb[..., 2].astype(np.int16)
    return (r > 180) & (g < 160) & (b > 140) & (np.abs(r - b) < 120) & (g + 30 < r)


def flood_transparent(rgb: np.ndarray, seed_mask: np.ndarray) -> np.ndarray:
    """Mark connected components reachable from seed_mask (usually edges)."""
    h, w = rgb.shape[:2]
    visited = np.zeros((h, w), dtype=bool)
    out = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    ys, xs = np.where(seed_mask)
    for y, x in zip(ys.tolist(), xs.tolist()):
        q.append((y, x))
        visited[y, x] = True
        out[y, x] = True
    # Similarity threshold for "same background"
    while q:
        y, x = q.popleft()
        base = rgb[y, x].astype(np.int16)
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if ny < 0 or nx < 0 or ny >= h or nx >= w or visited[ny, nx]:
                continue
            pix = rgb[ny, nx].astype(np.int16)
            if int(np.abs(pix - base).sum()) <= 90:
                visited[ny, nx] = True
                out[ny, nx] = True
                q.append((ny, nx))
    return out


def edge_seed(h: int, w: int) -> np.ndarray:
    m = np.zeros((h, w), dtype=bool)
    m[0, :] = m[-1, :] = m[:, 0] = m[:, -1] = True
    return m


def nearest_palette_index(rgb: np.ndarray, palette: list[tuple[int, int, int]], skip0: bool = True) -> np.ndarray:
    pal = np.array(palette, dtype=np.int16)
    start = 1 if skip0 else 0
    sub = pal[start:]
    # rgb HxWx3
    diff = rgb.astype(np.int16)[..., None, :] - sub[None, None, :, :]
    dist = (diff * diff).sum(axis=-1)
    idx = dist.argmin(axis=-1) + start
    return idx.astype(np.uint8)


def to_indexed(indices: np.ndarray, palette: list[tuple[int, int, int]]) -> Image.Image:
    im = Image.fromarray(indices, mode="P")
    flat: list[int] = []
    for c in palette:
        flat.extend(c)
    while len(flat) < 768:
        flat.extend((0, 0, 0))
    im.putpalette(flat[:768])
    return im


def report_image(path: Path, im: Image.Image) -> dict:
    arr = np.array(im)
    uniq = np.unique(arr)
    return {
        "path": str(path),
        "size": [im.width, im.height],
        "mode": im.mode,
        "unique_indices": [int(x) for x in uniq],
        "idx0_pct": float((arr == 0).mean() * 100.0),
        "colors_used": int(len(uniq)),
    }


def build_kirby_sheet() -> tuple[Image.Image, dict]:
    """8 frames x 32 from AI raw sheet with PAL2 + hard transparency."""
    raw = Image.open(RAW / "kirby_sheet.jpg").convert("RGB")
    arr = np.array(raw)
    # Content bbox via magenta-ish key
    key = is_magenta_key(arr)
    content = ~key
    rows = np.where(content.any(axis=1))[0]
    cols = np.where(content.any(axis=0))[0]
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    x0, x1 = int(cols[0]), int(cols[-1]) + 1
    crop = arr[y0:y1, x0:x1]
    nframes_src = 6
    cw = crop.shape[1] // nframes_src
    frames_rgb: list[np.ndarray] = []
    for i in range(nframes_src):
        cell = crop[:, i * cw : (i + 1) * cw if i < nframes_src - 1 else crop.shape[1]]
        # Pad to square on KEY
        side = max(cell.shape[0], cell.shape[1], 32)
        canvas = np.zeros((side, side, 3), dtype=np.uint8)
        canvas[:] = KEY
        oy = (side - cell.shape[0]) // 2
        ox = (side - cell.shape[1]) // 2
        canvas[oy : oy + cell.shape[0], ox : ox + cell.shape[1]] = cell
        # Resize nearest to 32
        fr = np.array(Image.fromarray(canvas).resize((32, 32), Image.Resampling.NEAREST))
        frames_rgb.append(fr)

    # Map source frames to 8 SGDK slots (idle, walk*3, jump, float, inhale, full)
    order = [0, 1, 2, 1, 3, 4, 5, 5]
    sheet = np.zeros((32, 256, 3), dtype=np.uint8)
    sheet[:] = KEY
    idx_sheet = np.zeros((32, 256), dtype=np.uint8)
    stats = []
    for fi, src_i in enumerate(order):
        fr = frames_rgb[src_i]
        fr = snap_rgb333(fr)
        # Transparency: edge flood OR magenta key
        seed = edge_seed(32, 32) | is_magenta_key(fr)
        # Also seed any pure-ish KEY corners
        trans = flood_transparent(fr, seed)
        # Expand transparency one pixel (erode character edge noise)
        from scipy import ndimage  # may not exist

        try:
            trans = ndimage.binary_dilation(trans, iterations=1)
            # but don't eat the character: only dilate if density high
            if trans.mean() > 0.85:
                trans = flood_transparent(fr, seed)  # revert over-dilation
        except Exception:
            pass

        # If still almost no transparency, force: anything not pink-body is key
        if trans.mean() < 0.25:
            r, g, b = fr[..., 0].astype(np.int16), fr[..., 1].astype(np.int16), fr[..., 2].astype(np.int16)
            body = (r > 140) & (g > 40) & (g < 200) & (b > 80) & (b < 230) & (r >= g) & (r >= b - 20)
            # Keep largest connected component of body near center
            body = body & ~is_magenta_key(fr)
            trans = ~body
            # Flood from edges into non-body
            seed2 = edge_seed(32, 32) | trans
            trans = flood_transparent(fr, seed2) | ~body

        opaque = ~trans
        indices = np.zeros((32, 32), dtype=np.uint8)
        if opaque.any():
            indices[opaque] = nearest_palette_index(fr[opaque][None, ...].reshape(-1, 1, 3), PAL2, skip0=True).reshape(-1)
        # Center content slightly (already centered)
        xoff = fi * 32
        sheet[:, xoff : xoff + 32] = fr
        sheet[:, xoff : xoff + 32][trans] = KEY
        idx_sheet[:, xoff : xoff + 32] = indices
        idx_sheet[:, xoff : xoff + 32][trans] = 0
        stats.append({"frame": fi, "idx0_pct": float(trans.mean() * 100)})

    im = to_indexed(idx_sheet, PAL2)
    meta = {"kind": "kirby_sheet", "frames": stats, "idx0_pct": float((idx_sheet == 0).mean() * 100)}
    return im, meta


def _no_scipy_kirby() -> tuple[Image.Image, dict]:
    """Kirby builder without scipy dependency."""
    raw = Image.open(RAW / "kirby_sheet.jpg").convert("RGB")
    arr = np.array(raw)
    key = is_magenta_key(arr)
    content = ~key
    rows = np.where(content.any(axis=1))[0]
    cols = np.where(content.any(axis=0))[0]
    crop = arr[int(rows[0]) : int(rows[-1]) + 1, int(cols[0]) : int(cols[-1]) + 1]
    nframes_src = 6
    cw = crop.shape[1] // nframes_src
    frames_rgb: list[np.ndarray] = []
    for i in range(nframes_src):
        cell = crop[:, i * cw : (i + 1) * cw if i < nframes_src - 1 else crop.shape[1]]
        side = max(cell.shape[0], cell.shape[1], 32)
        canvas = np.full((side, side, 3), KEY, dtype=np.uint8)
        oy = (side - cell.shape[0]) // 2
        ox = (side - cell.shape[1]) // 2
        canvas[oy : oy + cell.shape[0], ox : ox + cell.shape[1]] = cell
        fr = np.array(Image.fromarray(canvas).resize((32, 32), Image.Resampling.NEAREST))
        frames_rgb.append(fr)

    order = [0, 1, 2, 1, 3, 4, 5, 5]
    idx_sheet = np.zeros((32, 256), dtype=np.uint8)
    stats = []
    for fi, src_i in enumerate(order):
        fr = snap_rgb333(frames_rgb[src_i])
        # Primary mask: magenta key
        trans = is_magenta_key(fr, tol=70)
        # Flood from edges through similar background
        seed = edge_seed(32, 32) | trans
        trans = flood_transparent(fr, seed) | is_magenta_key(fr, tol=70)
        # Body recovery: pinkish near center
        r, g, b = fr[..., 0].astype(np.int16), fr[..., 1].astype(np.int16), fr[..., 2].astype(np.int16)
        body = (r > 150) & (g > 50) & (g < 210) & (b > 90) & (r + 10 >= g) & (r + 10 >= b)
        # Soft distance from center
        yy, xx = np.mgrid[0:32, 0:32]
        dist = np.sqrt((xx - 16) ** 2 + (yy - 16) ** 2)
        body = body & (dist < 15)
        # Outline/eyes/feet: dark-ish pixels inside body radius
        dark = (r + g + b < 280) & (dist < 14)
        opaque = (body | dark) & ~is_magenta_key(fr, tol=50)
        # If body is tiny, fall back to non-key circle
        if opaque.mean() < 0.08:
            opaque = (dist < 12) & ~is_magenta_key(fr, tol=60)
        trans = ~opaque
        # Force edge ring transparent
        trans[0, :] = trans[-1, :] = trans[:, 0] = trans[:, -1] = True
        indices = np.zeros((32, 32), dtype=np.uint8)
        if opaque.any():
            # reshape trick for nearest on sparse pixels
            pix = fr[opaque]
            pal = np.array(PAL2[1:], dtype=np.int16)
            d = ((pix.astype(np.int16)[:, None, :] - pal[None, :, :]) ** 2).sum(axis=-1)
            indices[opaque] = (d.argmin(axis=1) + 1).astype(np.uint8)
        xoff = fi * 32
        idx_sheet[:, xoff : xoff + 32] = indices
        idx_sheet[:, xoff : xoff + 32][trans] = 0
        stats.append({"frame": fi, "idx0_pct": float((idx_sheet[:, xoff : xoff + 32] == 0).mean() * 100)})

    im = to_indexed(idx_sheet, PAL2)
    return im, {"kind": "kirby_sheet", "frames": stats, "idx0_pct": float((idx_sheet == 0).mean() * 100)}


def scale_to_width(im: Image.Image, width: int) -> Image.Image:
    h = max(8, int(round(im.height * (width / im.width))))
    h = (h // 8) * 8
    return im.resize((width, max(8, h)), Image.Resampling.NEAREST)


def extract_layer_band(
    rgb: np.ndarray,
    y0: float,
    y1: float,
    out_h: int,
    palette: list[tuple[int, int, int]],
    *,
    keep_bottom_solid: bool = False,
    chroma_sky: bool = False,
) -> Image.Image:
    """Extract vertical fraction [y0,y1] of a full scene and remap to palette."""
    h, w = rgb.shape[:2]
    a, b = int(y0 * h), int(y1 * h)
    band = rgb[a:b]
    # Scale to 512 x out_h
    pil = Image.fromarray(band).resize((512, out_h), Image.Resampling.NEAREST)
    fr = snap_rgb333(np.array(pil))
    # Transparency: for sky, keep only bright clouds; for mount/hills, flood from top
    if chroma_sky:
        r, g, bch = fr[..., 0].astype(np.int16), fr[..., 1].astype(np.int16), fr[..., 2].astype(np.int16)
        # clouds: bright, low saturation-ish white/pink
        cloud = (r > 180) & (g > 160) & (bch > 160) & (np.abs(r.astype(int) - g) < 80)
        opaque = cloud
        # also soft cloud bottoms
        opaque |= (r > 200) & (g > 140) & (bch > 140) & (g > 100)
        trans = ~opaque
    else:
        # Flood from top edge through sky-like colors
        r, g, bch = fr[..., 0].astype(np.int16), fr[..., 1].astype(np.int16), fr[..., 2].astype(np.int16)
        skyish = (bch >= r - 20) & (bch >= g - 20) & (bch > 100) & (g > 80)
        # For green hills, skyish is upper portion
        seed = np.zeros((out_h, 512), dtype=bool)
        seed[0, :] = True
        seed |= skyish & (np.arange(out_h)[:, None] < out_h // 3)
        trans = flood_transparent(fr, seed)
        if keep_bottom_solid:
            # bottom 40% always opaque if not pure sky
            bottom = np.arange(out_h)[:, None] >= int(out_h * 0.45)
            not_sky = ~((bch > 180) & (r > 150) & (g > 150) & (np.abs(r - bch) < 40))
            opaque_force = bottom & not_sky
            trans = trans & ~opaque_force
        # Green/mountain mass
        green = (g > r + 10) & (g > bch - 10) & (g > 60)
        purple_mtn = (bch > g) & (r > 80) & (bch > 80) & (g < 160)
        opaque = green | purple_mtn | ~trans
        # clean: only keep opaque where green/mountain
        if keep_bottom_solid:
            opaque = green | purple_mtn | ((np.arange(out_h)[:, None] > out_h // 2) & ~skyish)
        trans = ~opaque

    indices = np.zeros((out_h, 512), dtype=np.uint8)
    opaque = ~trans
    if opaque.any():
        pix = fr[opaque]
        pal = np.array(palette[1:], dtype=np.int16)
        d = ((pix.astype(np.int16)[:, None, :] - pal[None, :, :]) ** 2).sum(axis=-1)
        indices[opaque] = (d.argmin(axis=1) + 1).astype(np.uint8)
    return to_indexed(indices, palette)


def build_bg_layers() -> dict[str, Image.Image]:
    raw = Image.open(RAW / "bg_dreamland.jpg").convert("RGB")
    # Work at 512-wide master
    master = scale_to_width(raw, 512)
    rgb = snap_rgb333(np.array(master))
    # Fractions of the composition (empirically for this R1 plate):
    # top sky/clouds ~0-0.35, mountains ~0.25-0.55, hills/trees ~0.45-0.85, grass ~0.75-1.0
    sky = extract_layer_band(rgb, 0.0, 0.38, 80, PAL0, chroma_sky=True)
    mount = extract_layer_band(rgb, 0.22, 0.55, 56, PAL0, keep_bottom_solid=True)
    hills = extract_layer_band(rgb, 0.42, 0.82, 88, PAL0, keep_bottom_solid=True)
    terrain = extract_layer_band(rgb, 0.72, 1.0, 64, PAL1, keep_bottom_solid=True)
    return {"sky": sky, "mount": mount, "hills": hills, "terrain": terrain}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true", help="Write into res/gfx and res/sprites")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    reports: dict = {}

    kirby, kmeta = _no_scipy_kirby()
    kpath = OUT / "kirby_sheet_r2.png"
    kirby.save(kpath)
    # preview
    kirby.resize((256 * 4, 32 * 4), Image.Resampling.NEAREST).save(OUT / "kirby_sheet_r2_x4.png")
    reports["kirby"] = {**kmeta, **report_image(kpath, kirby)}

    layers = build_bg_layers()
    for name, im in layers.items():
        p = OUT / f"ph_{name}_r2.png"
        im.save(p)
        reports[name] = report_image(p, im)

    if args.install:
        # Gate install: Kirby must have idx0 >= 35%
        if reports["kirby"]["idx0_pct"] < 35.0:
            raise SystemExit(
                f"REFUSING install: Kirby idx0_pct={reports['kirby']['idx0_pct']:.1f} < 35 "
                "(would reintroduce L-009 solid box)"
            )
        (ROOT / "res" / "sprites" / "ph_kirby.png").write_bytes(kpath.read_bytes())
        for name in ("sky", "mount", "hills", "terrain"):
            dst = ROOT / "res" / "gfx" / f"ph_{name}.png"
            # backup once
            bak = ROOT / "res" / "gfx" / f"ph_{name}_placeholder_backup.png"
            if dst.exists() and not bak.exists():
                bak.write_bytes(dst.read_bytes())
            dst.write_bytes((OUT / f"ph_{name}_r2.png").read_bytes())
        reports["installed"] = True
    else:
        reports["installed"] = False

    (OUT / "r2_report.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(json.dumps(reports, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
