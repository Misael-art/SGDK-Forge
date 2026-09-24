#!/usr/bin/env python3
"""Measure whether a character sheet is SOLID, or hollow at the index level.

WHY THIS EXISTS. On the VDP, index 0 of a palette line is hardware
transparency -- the pixel is not drawn, and whatever is behind shows through.
So a sheet can be a perfectly legal 4bpp indexed PNG, pass every palette /
VRAM / sprite-count gate, and still render as an empty silhouette in the ROM,
because the conversion mapped the character's BODY onto index 0.

That failure is invisible in a PNG preview: the viewer paints index 0 with
whatever RGB sits in slot 0, so the sheet looks filled while the hardware sees
a hole. The eye is fooled; the index histogram is not.

Ported from the sibling project KIRBY_FAN GAME GROK BUILD, which diagnosed
exactly this (doc/diagnostics/2026-08-08-kirby-index0-transparency.md: a
too-broad transparency classifier swallowed the base pink of the body, and
~80% of the character centre became index 0). Two deliberate changes here:

  1. STANDALONE. There it lives inside the sheet generator, so the producer
     grades its own output. Here it takes any sheet from any source.
  2. HONEST ABOUT MODE. An RGB/HD master has no palette indices, so the same
     question cannot be asked of it. Rather than silently measuring something
     else and reporting one number, this tool reports which mode it ran in and
     refuses to call an RGB result a VDP verdict.

    python3 tools/harness/sprite_solidity.py res/sprites/ph_kirby.png
    python3 tools/harness/sprite_solidity.py SHEET --cell 32x32 --json OUT
    python3 tools/harness/sprite_solidity.py --self-test

Exit code is non-zero when a sheet in indexed mode fails the gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError as exc:  # pragma: no cover - environment problem, not logic
    print(f"sprite_solidity: missing dependency: {exc}", file=sys.stderr)
    raise SystemExit(2)

# Thresholds inherited from the GROK BUILD forensic. They are not arbitrary:
# the placeholder that renders correctly measures 0.0% index-0 in the centre,
# and the broken AI sheet measured 80-87%. 5% leaves room for a stray pixel of
# interior detail without admitting a hollow body.
CENTER_IDX0_MAX_PCT = 5.0
OPAQUE_MIN_PCT = 35.0

# Fraction of the cell used as "the centre". 12/32 in the original.
CENTER_FRACTION = 0.375


def parse_cell(text: str) -> tuple[int, int]:
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except Exception:
        raise argparse.ArgumentTypeError(f"--cell expects WxH, got {text!r}")


def centre_slice(cell_w: int, cell_h: int):
    """The central box, as a fraction of the cell rather than hardcoded 12px."""
    cw = max(1, int(round(cell_w * CENTER_FRACTION)))
    ch = max(1, int(round(cell_h * CENTER_FRACTION)))
    x0 = (cell_w - cw) // 2
    y0 = (cell_h - ch) // 2
    return slice(y0, y0 + ch), slice(x0, x0 + cw)


def measure_indexed(arr, cell_w: int, cell_h: int) -> list[dict]:
    """The real gate. arr is a 2-D array of palette indices."""
    frames = []
    n = arr.shape[1] // cell_w
    ys, xs = centre_slice(cell_w, cell_h)
    for fi in range(n):
        cell = arr[0:cell_h, fi * cell_w : (fi + 1) * cell_w]
        centre = cell[ys, xs]
        rep = {
            "frame": fi,
            "opaque_pct": round(float((cell > 0).mean() * 100), 3),
            "center_idx0_pct": round(float((centre == 0).mean() * 100), 3),
            "center_indices": [int(v) for v in np.unique(centre)],
        }
        rep["gate"] = (
            "PASS"
            if rep["center_idx0_pct"] < CENTER_IDX0_MAX_PCT
            and rep["opaque_pct"] > OPAQUE_MIN_PCT
            else "FAIL"
        )
        frames.append(rep)
    return frames


def measure_unindexed(im: Image.Image, cell_w: int, cell_h: int) -> list[dict]:
    """RGB/RGBA source. This is NOT the VDP gate and must not be read as one.

    There are no palette indices yet, so "body landed on index 0" is not a
    question this image can answer. What we can measure is how much of the
    centre is alpha-transparent or sits on the magenta key -- i.e. whether the
    image would even survive conversion. Reported under different key names so
    the two can never be confused in a report.
    """
    rgba = im.convert("RGBA")
    a = np.asarray(rgba)
    ys, xs = centre_slice(cell_w, cell_h)
    frames = []
    n = a.shape[1] // cell_w
    for fi in range(n):
        cell = a[0:cell_h, fi * cell_w : (fi + 1) * cell_w]
        centre = cell[ys, xs]
        alpha0 = centre[..., 3] < 8
        key = (
            (centre[..., 0] > 240) & (centre[..., 1] < 16) & (centre[..., 2] > 240)
        )
        frames.append(
            {
                "frame": fi,
                "center_alpha0_pct": round(float(alpha0.mean() * 100), 3),
                "center_key_pct": round(float(key.mean() * 100), 3),
                "distinct_colours": int(
                    len(np.unique(cell[..., :3].reshape(-1, 3), axis=0))
                ),
                "gate": "NOT_APPLICABLE",
            }
        )
    return frames


def analyse(path: Path, cell_w: int, cell_h: int) -> dict:
    im = Image.open(path)
    indexed = im.mode == "P"
    w, h = im.size
    out = {
        "sheet": str(path),
        "mode": "indexed" if indexed else f"unindexed:{im.mode}",
        "size": [w, h],
        "cell": [cell_w, cell_h],
    }

    if w < cell_w or h < cell_h:
        out["status"] = "unmeasurable"
        out["reason"] = f"sheet {w}x{h} smaller than cell {cell_w}x{cell_h}"
        out["frames"] = []
        return out

    if indexed:
        arr = np.asarray(im)
        out["palette_entries"] = len(im.getpalette() or []) // 3
        out["frames"] = measure_indexed(arr, cell_w, cell_h)
        failed = [f for f in out["frames"] if f["gate"] == "FAIL"]
        # A sheet with zero measurable frames is not a pass. This trap has
        # already cost this project once: "0 of 0" read as success.
        if not out["frames"]:
            out["status"] = "empty"
        else:
            out["status"] = "fail" if failed else "pass"
        out["frames_failed"] = len(failed)
    else:
        out["frames"] = measure_unindexed(im, cell_w, cell_h)
        out["status"] = "not_applicable"
        out["reason"] = (
            "source is not palette-indexed; the index-0 gate cannot be "
            "evaluated until conversion to 4bpp"
        )
    return out


def _self_test() -> int:
    """Prove the gate detects the bug it claims to detect.

    A gate nobody has seen fail is not evidence. Two synthetic sheets: one
    solid disc (must PASS), one hollow ring whose interior is index 0 -- the
    exact GROK failure (must FAIL).
    """
    import tempfile

    pal = [0, 0, 0] + [255, 146, 182] * 255
    yy, xx = np.mgrid[0:32, 0:32]
    disc = ((yy - 16) ** 2 + (xx - 16) ** 2) < 13**2
    ring = disc & (((yy - 16) ** 2 + (xx - 16) ** 2) > 10**2)

    cases = [
        ("solid disc", disc, "pass"),
        ("hollow ring (body on index 0)", ring, "fail"),
    ]
    ok = True
    with tempfile.TemporaryDirectory() as td:
        for name, mask, expected in cases:
            arr = np.where(mask, 1, 0).astype(np.uint8)
            im = Image.fromarray(arr, mode="P")
            im.putpalette(pal)
            p = Path(td) / "case.png"
            im.save(p)
            got = analyse(p, 32, 32)
            frame = got["frames"][0]
            good = got["status"] == expected
            ok &= good
            print(
                f"  [{'ok' if good else 'FAILED'}] {name}: "
                f"status={got['status']} (expected {expected}) "
                f"center_idx0={frame['center_idx0_pct']}% "
                f"opaque={frame['opaque_pct']}%"
            )
    print("self-test", "passed" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheets", nargs="*", type=Path,
                    help="indexed PNG sheet(s) to measure")
    ap.add_argument("--cell", type=parse_cell, default=(32, 32),
                    help="cell size WxH (default 32x32)")
    ap.add_argument("--json", type=Path, help="write full report here")
    ap.add_argument("--self-test", action="store_true",
                    help="verify the gate detects a hollow sheet")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if not args.sheets:
        ap.error("give at least one sheet, or --self-test")

    cell_w, cell_h = args.cell
    reports = [analyse(p, cell_w, cell_h) for p in args.sheets]

    for r in reports:
        head = f"{r['sheet']}  [{r['mode']}]  {r['status'].upper()}"
        print(head)
        for f in r["frames"]:
            if "center_idx0_pct" in f:
                print(
                    f"   frame{f['frame']}: opaque={f['opaque_pct']:.1f}% "
                    f"center_idx0={f['center_idx0_pct']:.1f}% "
                    f"idx={f['center_indices']} {f['gate']}"
                )
            else:
                print(
                    f"   frame{f['frame']}: center_alpha0={f['center_alpha0_pct']:.1f}% "
                    f"center_key={f['center_key_pct']:.1f}% "
                    f"colours={f['distinct_colours']} {f['gate']}"
                )
        if r.get("reason"):
            print(f"   note: {r['reason']}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(
                {
                    "tool": "sprite_solidity",
                    "thresholds": {
                        "center_idx0_max_pct": CENTER_IDX0_MAX_PCT,
                        "opaque_min_pct": OPAQUE_MIN_PCT,
                        "center_fraction": CENTER_FRACTION,
                    },
                    "sheets": reports,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    return 1 if any(r["status"] == "fail" for r in reports) else 0


if __name__ == "__main__":
    raise SystemExit(main())
