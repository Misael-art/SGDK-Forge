#!/usr/bin/env python3
"""Punch a 1px dark outline and remap interior ink to the PAL2 gold ramp.

Does not invent silhouette. Authored ink stays; dark plate-fill (idx 2/3/4)
becomes metal body so MISAEL/MASTER read on the brick wall.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
RES = HERE.parent.parent.parent / "res" / "branding"

TARGETS = (
    RES / "logo_author_192x32.png",
    RES / "logo_project_224x48.png",
)


def remap(path: Path) -> None:
    im = Image.open(path)
    if im.mode != "P":
        raise SystemExit(f"{path} is not indexed")
    pal = im.getpalette() or []
    w, h = im.size
    src = im.load()
    out = Image.new("P", (w, h), 0)
    out.putpalette(pal)
    dst = out.load()

    ink = [[src[x, y] != 0 for x in range(w)] for y in range(h)]

    for y in range(h):
        for x in range(w):
            if not ink[y][x]:
                dst[x, y] = 0
                continue
            edge = False
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if ny < 0 or ny >= h or nx < 0 or nx >= w or not ink[ny][nx]:
                    edge = True
                    break
            idx = src[x, y]
            if edge:
                dst[x, y] = 1
                continue
            if idx >= 8:
                dst[x, y] = idx
            elif idx <= 2:
                dst[x, y] = 8
            elif idx == 3:
                dst[x, y] = 9
            else:
                dst[x, y] = 10

    out.save(path)
    print(f"remapped {path.name}")


def main() -> None:
    for path in TARGETS:
        remap(path)


if __name__ == "__main__":
    main()
