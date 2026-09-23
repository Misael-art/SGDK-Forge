#!/usr/bin/env python3
"""Mechanical validation of delivered production art (round P1).

Judges what a script CAN judge: exact dimensions, RGB333 legality, the
transparency key, colour ceilings, the value ladder, horizontal tiling, and the
terrain gaps. It does NOT judge whether the art is good -- that stays human.

Every check here corresponds to a line in doc/art/PRODUCTION_ASSET_PACK.md
section 5, so a rejection can always be quoted back with a number.

    python3 tools/harness/validate_assets.py [--round p1] [--json OUT]

Exit code is non-zero when any delivered asset fails a hard check.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

LEGAL = {0, 36, 73, 109, 146, 182, 219, 255}
KEY = (255, 0, 255)

# doc/art/PRODUCTION_ASSET_PACK.md section 2.2. sRGB weights, the formula
# canonised after director and executor measured the same image differently.
def luminance(rgb):
    r, g, b = rgb
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def load_manifest(root: Path) -> dict:
    return json.loads(
        (root / "doc" / "art" / "production_asset_manifest.json")
        .read_text(encoding="utf-8")
    )


def check_asset(root: Path, spec: dict) -> dict:
    from PIL import Image
    import numpy as np

    out = {"id": spec["id"], "file": spec["file"], "checks": [], "status": "pass"}

    def add(name, ok, detail, hard=True):
        out["checks"].append(
            {"check": name, "status": "pass" if ok else ("fail" if hard else "warn"),
             "detail": detail}
        )
        if not ok and hard:
            out["status"] = "fail"

    path = (root / spec["target_dir"] / spec["file"]) if spec.get("_self_test") \
        else (root / spec["output_dir"] / spec["file"])
    if not path.is_file():
        out["status"] = "missing"
        out["checks"].append({"check": "delivered", "status": "missing",
                              "detail": f"not found: {path}"})
        return out

    img = Image.open(path).convert("RGB")
    arr = np.array(img)
    h, w, _ = arr.shape

    add("dimensions", (w, h) == (spec["width"], spec["height"]),
        f"{w}x{h}, expected {spec['width']}x{spec['height']}")

    illegal = int((~np.isin(arr, list(LEGAL)).all(axis=2)).sum())
    add("rgb333_legal", illegal == 0,
        f"{illegal} pixels with a channel off the 8-value lattice")

    flat = arr.reshape(-1, 3)
    colours = {tuple(int(v) for v in c) for c in np.unique(flat, axis=0)}

    # Any magenta that is not the exact key is the R1-03 failure repeating.
    stray = sorted(c for c in colours
                   if c != KEY and c[0] > 150 and c[1] < 80 and c[2] > 150)
    add("transparency_key", not stray,
        f"{len(stray)} magenta-ish colour(s) that are not exactly {KEY}: {stray[:4]}")

    non_key = colours - {KEY}
    add("colour_ceiling", len(non_key) <= spec["max_colors"],
        f"{len(non_key)} colours excluding the key, ceiling {spec['max_colors']}")

    # Horizontal tiling: 512-wide strips wrap on the X axis.
    if spec["width"] == 512:
        seam = int((arr[:, 0] != arr[:, -1]).any(axis=1).sum())
        add("horizontal_tiling", seam <= h // 8,
            f"{seam} of {h} rows differ between the left and right edge",
            hard=False)

    # Value ladder, for the layers that declare one.
    ladder = {"B2": 0.502, "B3": 0.453, "B4": 0.340, "B5": 0.258}
    if spec["id"] in ladder:
        mask = ~(flat == np.array(KEY)).all(axis=1)
        if mask.sum():
            lum = float(np.mean([luminance(tuple(int(v) for v in p))
                                 for p in flat[mask][::37]]))
            target = ladder[spec["id"]]
            add("value_ladder", abs(lum - target) <= 0.06,
                f"mean luminance {lum:.3f}, target {target:.3f} (+/-0.06)")

    # The terrain gaps the level code depends on.
    if spec["id"] == "B4":
        gaps = [(160, 208), (320, 352)]
        bad = []
        for x0, x1 in gaps:
            col = arr[:, x0:x1].reshape(-1, 3)
            solid = int((~(col == np.array(KEY)).all(axis=1)).sum())
            if solid > 0:
                bad.append({"gap": [x0, x1], "solid_pixels": solid})
        add("terrain_gaps", not bad,
            f"{len(bad)} required gap(s) are not transparent: {bad}")

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-root", type=Path, default=None)
    ap.add_argument("--json", dest="json_path", type=Path, default=None)
    ap.add_argument("--self-test", action="store_true",
                    help="validate the CURRENT placeholders in res/ instead of "
                         "the p1 deliveries, to prove the checks actually fire")
    args = ap.parse_args()

    root = (args.project_root or Path(__file__).resolve().parents[2]).resolve()
    manifest = load_manifest(root)

    specs = manifest["assets"]
    if args.self_test:
        specs = [dict(s, _self_test=True) for s in specs]
    results = [check_asset(root, spec) for spec in specs]
    delivered = [r for r in results if r["status"] != "missing"]
    failed = [r for r in delivered if r["status"] == "fail"]

    print("=" * 72)
    print(f"PRODUCTION ASSET VALIDATION  round={manifest['round']}")
    print("=" * 72)
    for r in results:
        if r["status"] == "missing":
            print(f"[ -- ] {r['id']:3} {r['file']:22} not delivered yet")
            continue
        tag = "PASS" if r["status"] == "pass" else "FAIL"
        print(f"[{tag}] {r['id']:3} {r['file']:22}")
        for c in r["checks"]:
            if c["status"] != "pass":
                print(f"         {c['status'].upper():4} {c['check']}: {c['detail']}")
    print("-" * 72)
    print(f"delivered {len(delivered)}/{len(results)}   failed {len(failed)}")
    if not delivered:
        print("VERDICT: NOTHING DELIVERED -- this is not a pass. A validator with "
              "an empty input proves nothing; it is the same vacuous-green trap "
              "the runtime gates already guard against.")
    print("NOTE: this judges CONFORMANCE, never quality. Whether the art is good "
          "is a human call.")

    out = args.json_path or (root / "out" / "logs" / "asset_validation_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(
        {"round": manifest["round"], "delivered": len(delivered),
         "total": len(results), "failed": len(failed),
         "status": ("fail" if failed else ("empty" if not delivered else "pass")),
         "assets": results}, indent=2), encoding="utf-8")
    # An empty run is NOT a pass. Reporting "pass" with zero inputs is exactly
    # how a green board stops meaning anything.
    status = "fail" if failed else ("empty" if not delivered else "pass")
    print(f"asset_validation_status={status} report={out}")
    return 1 if (failed or not delivered) else 0


if __name__ == "__main__":
    raise SystemExit(main())
