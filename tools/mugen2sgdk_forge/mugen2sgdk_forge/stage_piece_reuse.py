"""Lossless indexed-tile audit. Measures authored pixels; never redraws them."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def variants(tile: bytes) -> tuple[bytes, ...]:
    if len(tile) != 64:
        raise ValueError("an 8x8 tile requires 64 indices")
    rows = [tile[y:y + 8] for y in range(0, 64, 8)]
    return (tile, b"".join(r[::-1] for r in rows),
            b"".join(reversed(rows)), b"".join(r[::-1] for r in reversed(rows)))


def audit(path: Path, regions: dict[str, tuple[int, int, int, int]]) -> dict:
    with Image.open(path) as im:
        if im.mode != "P":
            raise ValueError("requires final indexed palette; RGB similarity is not tile identity")
        if im.width % 8 or im.height % 8:
            raise ValueError("image dimensions must align to the 8x8 grid")
        pixels = im.tobytes()
        def tiles(box):
            x, y, w, h = box
            if min(x, y) < 0 or min(w, h) <= 0 or any(v % 8 for v in box):
                raise ValueError("regions must be positive and aligned to the original 8x8 grid")
            if x+w > im.width or y+h > im.height:
                raise ValueError("region outside image")
            return [b"".join(pixels[(ty+dy)*im.width+tx:(ty+dy)*im.width+tx+8]
                             for dy in range(8))
                    for ty in range(y,y+h,8) for tx in range(x,x+w,8)]
        whole = tiles((0, 0, im.width, im.height))
        canon = lambda t: min(variants(t))
        global_keys = {canon(t) for t in whole}
        result = {}
        for name, box in regions.items():
            part = tiles(box)
            keys = {canon(t) for t in part}
            x,y,w,h = box
            outside = {canon(t) for i,t in enumerate(whole)
                       if not (x <= (i % (im.width//8))*8 < x+w and
                               y <= (i // (im.width//8))*8 < y+h)}
            result[name] = {"box": list(box), "cells": len(part),
                            "unique_exact": len(set(part)), "unique_hv": len(keys),
                            "exclusive_patterns": len(keys-outside),
                            "patterns_shared_with_outside": len(keys&outside)}
        return {"source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size": list(im.size), "palette_sha256": hashlib.sha256(bytes(im.getpalette())).hexdigest(),
                "index_zero_pixels": pixels.count(0),
                "whole": {"cells":len(whole), "unique_exact":len(set(whole)),"unique_hv":len(global_keys)},
                "regions": result, "pixels_changed": 0,
                "claim": "offline indexed-pattern count; not compiled VRAM or visual approval"}


def self_check():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.png"
        a = bytes(range(64)); b = variants(a)[1]
        im = Image.new("P", (16, 8))
        im.putpalette([v for i in range(256) for v in (i,i,i)])
        im.putdata([v for y in range(8) for v in a[y*8:y*8+8]+b[y*8:y*8+8]])
        im.save(path)
        result = audit(path, {"left": (0,0,8,8)})
        assert result["whole"] == {"cells":2,"unique_exact":2,"unique_hv":1}
        assert result["regions"]["left"]["exclusive_patterns"] == 0
        assert len(set(variants(a))) == 4
    return {"self_check": "passed"}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image",type=Path,nargs="?")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--region", action="append",default=[],help="name:x,y,width,height")
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    if args.self_check:
        print(json.dumps(self_check())); return
    if args.image is None or args.output is None: ap.error("image and --output are required")
    regions={}
    for value in args.region:
        name,coords=value.split(":",1)
        if name in regions: ap.error("duplicate region name")
        box=tuple(map(int,coords.split(",")))
        if len(box)!=4: ap.error("region requires four coordinates")
        regions[name]=box
    result=audit(args.image,regions)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__ == "__main__":
    main()
