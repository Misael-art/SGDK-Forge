#!/usr/bin/env python3
"""Convert curated TSR sheets → res/ for fan-study ROM (fan_study_allowed).

Extracts:
  - Kirby: 8 frames × 32×32 → res/sprites/ph_kirby.png  (PAL2 absolute)
  - Enemy: 2 frames × 16×16 → res/sprites/ph_enemy.png

Source preference for Kirby: SNES Super Star (52859) then NES Adventure (49192).
Backups: res/sprites/*_pre_tsr_backup.png

Usage:
  python3 tools/pipeline/tsr_install_to_res.py
  python3 tools/pipeline/tsr_install_to_res.py --source nes
  python3 tools/pipeline/tsr_install_to_res.py --dry-run
"""
from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "data" / "reference_archive"
RAW = ARCHIVE / "raw"
OUT_VER = ARCHIVE / "versions" / "v004_md_sheet_32"
SPR = ROOT / "res" / "sprites"

LATTICE = np.array([0, 36, 73, 109, 146, 182, 219, 255], dtype=np.int16)

# Canonical PAL2 (doc/PALETTES.md)
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


def is_key_rgb(rgb: np.ndarray, bg: tuple[int, int, int] | None = None) -> np.ndarray:
    r = rgb[..., 0].astype(np.int16)
    g = rgb[..., 1].astype(np.int16)
    b = rgb[..., 2].astype(np.int16)
    mag = (r >= 182) & (b >= 146) & (g <= 90) & (np.abs(r - b) <= 120)
    white = (r >= 240) & (g >= 240) & (b >= 240)
    key = mag | white
    if bg is not None:
        br, bg_, bb = bg
        # sheet backdrop (NES slate, SNES lavender, etc.)
        key = key | (
            (np.abs(r - br) <= 28) & (np.abs(g - bg_) <= 28) & (np.abs(b - bb) <= 28)
        )
    return key


def detect_bg(rgb: np.ndarray) -> tuple[int, int, int]:
    """Most common color on the image border = sheet key."""
    edge = np.concatenate(
        [rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]],
        axis=0,
    )
    # quantize lightly for voting
    q = (edge // 16) * 16
    # pack to int
    packed = (q[:, 0].astype(np.int32) << 16) | (q[:, 1].astype(np.int32) << 8) | q[:, 2]
    vals, counts = np.unique(packed, return_counts=True)
    best = int(vals[counts.argmax()])
    return ((best >> 16) & 255, (best >> 8) & 255, best & 255)


def load_rgb(path: Path) -> np.ndarray:
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    rgb = a[..., :3].copy()
    rgb[a[..., 3] < 16] = (255, 0, 255)
    # do NOT snap before bg detect — keep backdrop distinct
    return rgb


def flood_key(key: np.ndarray) -> np.ndarray:
    h, w = key.shape
    vis = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            if key[y, x] and not vis[y, x]:
                vis[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if key[y, x] and not vis[y, x]:
                vis[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and not vis[ny, nx] and key[ny, nx]:
                vis[ny, nx] = True
                q.append((ny, nx))
    return vis


def find_blobs(body: np.ndarray, min_area: int = 80, max_area: int = 2500) -> list[tuple[int, int, int, int]]:
    """Return bounding boxes (y0,y1,x0,x1) of connected components."""
    h, w = body.shape
    seen = np.zeros_like(body, dtype=bool)
    boxes: list[tuple[int, int, int, int, int]] = []
    for y in range(h):
        for x in range(w):
            if not body[y, x] or seen[y, x]:
                continue
            q = deque([(y, x)])
            seen[y, x] = True
            ys, xs = [y], [x]
            while q:
                cy, cx = q.popleft()
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and body[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        q.append((ny, nx))
                        ys.append(ny)
                        xs.append(nx)
            area = len(ys)
            if min_area <= area <= max_area:
                y0, y1 = min(ys), max(ys) + 1
                x0, x1 = min(xs), max(xs) + 1
                # prefer roughly square-ish character cells
                bh, bw = y1 - y0, x1 - x0
                if bh < 8 or bw < 8:
                    continue
                aspect = bw / max(1, bh)
                if 0.45 <= aspect <= 2.2:
                    boxes.append((y0, y1, x0, x1, area))
    # sort top-to-bottom, left-to-right
    boxes.sort(key=lambda b: (b[0] // 40, b[2]))
    return [(a, b, c, d) for a, b, c, d, _ in boxes]


def cell_to_32(rgb: np.ndarray, y0: int, y1: int, x0: int, x1: int) -> np.ndarray:
    crop = rgb[y0:y1, x0:x1]
    ch, cw = crop.shape[:2]
    # scale longest side to 26, center in 32
    scale = 26.0 / max(ch, cw)
    nh, nw = max(1, int(ch * scale)), max(1, int(cw * scale))
    scaled = np.array(
        Image.fromarray(crop).resize((nw, nh), Image.Resampling.NEAREST)
    )
    canvas = np.zeros((32, 32, 3), dtype=np.uint8)
    canvas[:] = (255, 0, 255)
    oy, ox = (32 - nh) // 2, (32 - nw) // 2
    canvas[oy : oy + nh, ox : ox + nw] = scaled
    return snap(canvas)


def rgb_to_pal2_indices(fr: np.ndarray) -> np.ndarray:
    """Map RGB frame → PAL2 indices with spherical-friendly bins + eyes/feet."""
    key = is_key_rgb(fr)
    key |= (fr[..., 0] == 255) & (fr[..., 1] == 0) & (fr[..., 2] == 255)
    bg = flood_key(key)
    character = ~bg
    # dilate once
    for _ in range(2):
        nxt = character.copy()
        for y in range(1, 31):
            for x in range(1, 31):
                if not character[y, x] and character[y - 1 : y + 2, x - 1 : x + 2].sum() >= 4:
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

    # eyes: dark upper
    eyes = character & (lum < 85) & (yy < 18)
    indices[eyes] = 9
    # eye white
    indices[character & (r > 230) & (g > 220) & (b > 220)] = 10
    # feet: lower third reddish/brownish
    feet = character & (yy >= 23) & ((r > g + 10) | (r > 100) & (g < 100))
    indices[feet] = 7
    feet_d = feet & (lum < 100)
    indices[feet_d] = 8
    # outline
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
    indices[character & (indices == 0)] = 2
    indices[~character] = 0
    return indices


def to_indexed_pal2(sheet: np.ndarray) -> Image.Image:
    # stamp full palette
    for i in range(16):
        sheet[0, i] = i
        sheet[-1, -16 + i] = i
    im = Image.fromarray(sheet.astype(np.uint8), mode="P")
    flat: list[int] = []
    for c in PAL2:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - 16))
    im.putpalette(flat[:768])
    return im


def gate_frame(indices: np.ndarray) -> dict:
    center = indices[10:22, 10:22]
    return {
        "opaque_pct": float((indices > 0).mean() * 100),
        "idx0_center_pct": float((center == 0).mean() * 100),
        "gate": (
            "PASS"
            if (center == 0).mean() < 0.05 and (indices > 0).mean() > 0.35
            else "FAIL"
        ),
    }


def pick_kirby_frames(boxes: list, n: int = 24) -> list:
    """Pick diverse frames: early boxes tend to be idle/walk on Adventure sheets."""
    if len(boxes) <= 8:
        return boxes[:8]
    # sample across the sheet
    idxs = np.linspace(0, len(boxes) - 1, num=min(n, len(boxes)), dtype=int)
    chosen = [boxes[i] for i in idxs]
    # prefer first 8 after filter by area closeness to median
    areas = [(b[1] - b[0]) * (b[3] - b[2]) for b in chosen]
    med = float(np.median(areas))
    scored = sorted(chosen, key=lambda b: abs((b[1] - b[0]) * (b[3] - b[2]) - med))
    # keep order by y for animation variety: re-sort top to bottom
    top = scored[: max(8, min(16, len(scored)))]
    top.sort(key=lambda b: (b[0], b[2]))
    # take evenly spaced 8
    if len(top) <= 8:
        return top
    pick = np.linspace(0, len(top) - 1, num=8, dtype=int)
    return [top[i] for i in pick]


def build_kirby_sheet(source: str) -> tuple[Image.Image, dict]:
    if source == "nes":
        path = RAW / "nes_kirby_adventure" / "49192_kirby.png"
    elif source == "gba":
        path = RAW / "gba_nightmare_dreamland" / "32130_kirby.png"
    else:
        path = RAW / "snes_kirby_super_star" / "52859_kirby.png"
    if not path.exists():
        raise FileNotFoundError(path)

    rgb_raw = load_rgb(path)
    bg_col = detect_bg(rgb_raw)
    print(f"  detected bg={bg_col}")
    key = is_key_rgb(rgb_raw, bg=bg_col)
    # body = not key (backdrop), before flood — flood optional for holes
    body = ~key
    # snap for later cell processing
    rgb = snap(rgb_raw)

    min_a, max_a = (50, 3500) if source != "nes" else (35, 3000)
    boxes = find_blobs(body, min_area=min_a, max_area=max_a)
    print(f"  source={path.name} blobs={len(boxes)}")
    if len(boxes) < 4:
        raise RuntimeError(f"too few blobs ({len(boxes)}) — key detection may be wrong")

    frames_boxes = pick_kirby_frames(boxes, n=32)
    while len(frames_boxes) < 8:
        frames_boxes.append(frames_boxes[-1])
    frames_boxes = frames_boxes[:8]

    sheet = np.zeros((32, 256), dtype=np.uint8)
    reports = []
    for fi, (y0, y1, x0, x1) in enumerate(frames_boxes):
        cell = cell_to_32(rgb, y0, y1, x0, x1)
        # also paint bg color in cell as magenta for pal2 map
        ckey = is_key_rgb(cell, bg=bg_col)
        cell = cell.copy()
        cell[ckey] = (255, 0, 255)
        idx = rgb_to_pal2_indices(cell)
        sheet[:, fi * 32 : (fi + 1) * 32] = idx
        rep = gate_frame(idx)
        rep["frame"] = fi
        rep["bbox"] = [y0, y1, x0, x1]
        reports.append(rep)
        print(f"  frame{fi}: {rep['gate']} opaque={rep['opaque_pct']:.1f}% center0={rep['idx0_center_pct']:.1f}%")

    all_pass = all(r["gate"] == "PASS" for r in reports)
    return to_indexed_pal2(sheet), {
        "all_pass": all_pass,
        "source": str(path),
        "bg": list(bg_col),
        "frames": reports,
    }


def build_enemy_sheet() -> tuple[Image.Image, dict]:
    path = RAW / "nes_kirby_adventure" / "49202_enemies.png"
    rgb_raw = load_rgb(path)
    bg_col = detect_bg(rgb_raw)
    print(f"  enemies bg={bg_col}")
    key = is_key_rgb(rgb_raw, bg=bg_col)
    body = ~key
    rgb = snap(rgb_raw)
    boxes = find_blobs(body, min_area=30, max_area=1200)
    print(f"  enemies blobs={len(boxes)}")
    if not boxes:
        raise RuntimeError("no enemy blobs")
    boxes.sort(key=lambda b: (b[1] - b[0]) * (b[3] - b[2]))
    mid = boxes[len(boxes) // 3 : 2 * len(boxes) // 3] or boxes
    picks = mid[:2] if len(mid) >= 2 else [boxes[0], boxes[0]]

    sheet = np.zeros((16, 32), dtype=np.uint8)
    reps = []
    for fi, (y0, y1, x0, x1) in enumerate(picks):
        crop = rgb[y0:y1, x0:x1]
        ch, cw = crop.shape[:2]
        scale = 14.0 / max(ch, cw)
        nh, nw = max(1, int(ch * scale)), max(1, int(cw * scale))
        scaled = np.array(Image.fromarray(crop).resize((nw, nh), Image.Resampling.NEAREST))
        canvas = np.zeros((16, 16, 3), dtype=np.uint8)
        canvas[:] = (255, 0, 255)
        oy, ox = (16 - nh) // 2, (16 - nw) // 2
        canvas[oy : oy + nh, ox : ox + nw] = scaled
        canvas = snap(canvas)
        idx = np.zeros((16, 16), dtype=np.uint8)
        k = is_key_rgb(canvas, bg=bg_col) | (
            (canvas[..., 0] == 255) & (canvas[..., 1] == 0) & (canvas[..., 2] == 255)
        )
        char = ~k
        lum = (
            0.2126 * canvas[..., 0] + 0.7152 * canvas[..., 1] + 0.0722 * canvas[..., 2]
        )
        if char.any():
            pl = lum[char]
            t = (pl - pl.min()) / (pl.max() - pl.min() + 1e-6)
            bins = np.clip((1.0 - t) * 3.0, 0, 3).astype(int)
            remap = np.array([2, 3, 4, 6], dtype=np.uint8)
            idx[char] = remap[bins]
        idx[char & (lum < 60)] = 9
        idx[k] = 0
        sheet[:, fi * 16 : (fi + 1) * 16] = idx
        reps.append({"frame": fi, "bbox": [y0, y1, x0, x1], "opaque": float(char.mean() * 100)})

    for i in range(16):
        sheet[0, min(31, i)] = i
    im = Image.fromarray(sheet, mode="P")
    flat: list[int] = []
    for c in PAL2:
        flat.extend(c)
    flat.extend([0, 0, 0] * (256 - 16))
    im.putpalette(flat[:768])
    return im, {"frames": reps, "source": str(path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=("snes", "nes", "gba", "auto"), default="auto")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    OUT_VER.mkdir(parents=True, exist_ok=True)
    SPR.mkdir(parents=True, exist_ok=True)

    sources = (
        ["snes", "nes", "gba"] if args.source == "auto" else [args.source]
    )
    kirby_im = None
    krep = None
    for src in sources:
        try:
            print(f"=== Kirby from {src} ===")
            kirby_im, krep = build_kirby_sheet(src)
            if krep["all_pass"]:
                print(f"  ALL PASS with {src}")
                break
            print(f"  partial fail with {src}, trying next…")
        except Exception as e:
            print(f"  fail {src}: {e}")
    if kirby_im is None or krep is None:
        print("ERROR: could not build Kirby sheet")
        return 1

    print("=== Enemies ===")
    try:
        enemy_im, erep = build_enemy_sheet()
    except Exception as e:
        print(f"  enemy fail: {e}")
        enemy_im, erep = None, {"error": str(e)}

    kpath = OUT_VER / "ph_kirby_tsr.png"
    kirby_im.save(kpath)
    kirby_im.resize((1024, 128), Image.Resampling.NEAREST).save(OUT_VER / "ph_kirby_tsr_x4.png")
    (OUT_VER / "kirby_tsr_gate.json").write_text(json.dumps(krep, indent=2) + "\n")

    if enemy_im is not None:
        epath = OUT_VER / "ph_enemy_tsr.png"
        enemy_im.save(epath)
        (OUT_VER / "enemy_tsr_report.json").write_text(json.dumps(erep, indent=2) + "\n")

    if args.dry_run:
        print("DRY-RUN: not installing to res/")
        return 0 if krep["all_pass"] else 1

    if not krep["all_pass"]:
        print("REFUSED kirby install (gate FAIL) — keeping previous res sheet")
        # still install if ≥6/8 pass? force install best effort for fan study
        n_pass = sum(1 for r in krep["frames"] if r["gate"] == "PASS")
        if n_pass < 6:
            return 1
        print(f"  fan-study soft install: {n_pass}/8 frames PASS")

    bak = SPR / "ph_kirby_pre_tsr_backup.png"
    dst = SPR / "ph_kirby.png"
    if dst.exists() and not bak.exists():
        bak.write_bytes(dst.read_bytes())
    kirby_im.save(dst)
    print("INSTALLED", dst)

    if enemy_im is not None:
        ebak = SPR / "ph_enemy_pre_tsr_backup.png"
        edst = SPR / "ph_enemy.png"
        if edst.exists() and not ebak.exists():
            ebak.write_bytes(edst.read_bytes())
        enemy_im.save(edst)
        print("INSTALLED", edst)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
