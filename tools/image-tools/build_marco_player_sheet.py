#!/usr/bin/env python3
"""Build SGDK-ready Marco sprite sheet from source GIF sheet."""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Tuple

try:
    from PIL import Image
except ImportError as exc:
    print("ERRO: Pillow necessario (pip install Pillow).", file=sys.stderr)
    raise SystemExit(1) from exc

MAGENTA = (255, 0, 255)


@dataclass
class Component:
    x0: int
    y0: int
    x1: int
    y1: int
    area: int

    @property
    def w(self) -> int:
        return self.x1 - self.x0 + 1

    @property
    def h(self) -> int:
        return self.y1 - self.y0 + 1


def _crc32_chunk(typ: bytes, body: bytes) -> int:
    import zlib

    return zlib.crc32(typ + body) & 0xFFFFFFFF


def _read_png_palette_rgba(path: str) -> List[Tuple[int, int, int, int]]:
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return []
    pos = 8
    pal: List[Tuple[int, int, int, int]] = []
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if ctype == b"PLTE":
            for i in range(0, len(chunk), 3):
                pal.append((chunk[i], chunk[i + 1], chunk[i + 2], 255))
        elif ctype == b"tRNS":
            for i, alpha in enumerate(chunk):
                if i < len(pal):
                    r, g, b, _ = pal[i]
                    pal[i] = (r, g, b, alpha)
        elif ctype == b"IEND":
            break
    return pal


def _normalize_indexed_png(path: str, max_entries: int = 16) -> None:
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        return

    pos = 8
    chunks: List[Tuple[bytes, bytes]] = []
    while pos < len(raw):
        ln = struct.unpack(">I", raw[pos : pos + 4])[0]
        typ = raw[pos + 4 : pos + 8]
        body = raw[pos + 8 : pos + 8 + ln]
        pos += 12 + ln
        chunks.append((typ, body))
        if typ == b"IEND":
            break

    plte = None
    trns = None
    out_chunks: List[Tuple[bytes, bytes]] = []
    for typ, body in chunks:
        if typ == b"PLTE":
            plte = body
            continue
        if typ == b"tRNS":
            trns = body
            continue
        out_chunks.append((typ, body))

    if plte is None:
        return
    n_colors = len(plte) // 3
    keep = min(max_entries, n_colors)
    plte = plte[: keep * 3]
    old_trns = trns or b""
    trns_buf = bytearray([255] * keep)
    for i in range(min(len(old_trns), keep)):
        trns_buf[i] = old_trns[i]
    trns_buf[0] = 0
    trns = bytes(trns_buf)

    rebuilt: List[Tuple[bytes, bytes]] = []
    inserted = False
    for typ, body in out_chunks:
        rebuilt.append((typ, body))
        if typ == b"IHDR" and not inserted:
            rebuilt.append((b"PLTE", plte))
            rebuilt.append((b"tRNS", trns))
            inserted = True

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        for typ, body in rebuilt:
            f.write(struct.pack(">I", len(body)))
            f.write(typ)
            f.write(body)
            f.write(struct.pack(">I", _crc32_chunk(typ, body)))


def _find_components(rgb: Image.Image) -> List[Component]:
    px = rgb.load()
    w, h = rgb.size
    seen = [[False] * w for _ in range(h)]
    out: List[Component] = []

    for y in range(h):
        for x in range(w):
            if seen[y][x] or px[x, y] == MAGENTA:
                continue
            queue: deque[Tuple[int, int]] = deque([(x, y)])
            seen[y][x] = True
            x0 = x1 = x
            y0 = y1 = y
            area = 0
            while queue:
                cx, cy = queue.popleft()
                area += 1
                x0 = min(x0, cx)
                x1 = max(x1, cx)
                y0 = min(y0, cy)
                y1 = max(y1, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and px[nx, ny] != MAGENTA:
                        seen[ny][nx] = True
                        queue.append((nx, ny))

            comp = Component(x0=x0, y0=y0, x1=x1, y1=y1, area=area)
            if comp.area >= 450 and 22 <= comp.w <= 42 and 34 <= comp.h <= 52:
                out.append(comp)
    out.sort(key=lambda c: (c.y0, c.x0))
    return out


def _crop_component_rgba(rgba: Image.Image, comp: Component) -> Image.Image:
    crop = rgba.crop((comp.x0, comp.y0, comp.x1 + 1, comp.y1 + 1)).convert("RGBA")
    pix = crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            if pix[x, y][:3] == MAGENTA:
                pix[x, y] = (0, 0, 0, 0)
    return crop


def _build_sheet(rgba: Image.Image, components: List[Component], selected: Dict[str, List[int]], frame_w: int, frame_h: int) -> Image.Image:
    cols = max(len(v) for v in selected.values())
    rows = len(selected)
    sheet = Image.new("RGBA", (cols * frame_w, rows * frame_h), (0, 0, 0, 0))

    for row_idx, state in enumerate(("idle", "walk", "jump", "land", "shoot")):
        for col_idx, comp_idx in enumerate(selected[state]):
            comp = components[comp_idx]
            spr = _crop_component_rgba(rgba, comp)
            target_x = col_idx * frame_w + (frame_w - spr.width) // 2
            target_y = row_idx * frame_h + (frame_h - spr.height)
            sheet.paste(spr, (target_x, target_y), spr)
    return sheet


def _to_indexed_16(rgba: Image.Image) -> Image.Image:
    rgb = rgba.convert("RGB")
    alpha = rgba.split()[-1]
    q = rgb.quantize(colors=16, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[:48]
    out = Image.new("P", q.size)
    out.putpalette(pal + [0] * (768 - len(pal)))
    src_idx = q.load()
    src_a = alpha.load()
    dst = out.load()
    w, h = q.size
    for y in range(h):
        for x in range(w):
            dst[x, y] = 0 if src_a[x, y] < 8 else max(1, min(15, src_idx[x, y]))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Marco.gif -> spr_marco.png (SGDK full_core).")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise SystemExit(f"ERRO: arquivo de entrada inexistente: {args.input}")

    rgb = Image.open(args.input).convert("RGB")
    rgba = rgb.convert("RGBA")
    components = _find_components(rgb)
    if len(components) < 120:
        raise SystemExit(f"ERRO: componentes insuficientes detectados ({len(components)}).")

    # Mapeamento curado para full_core no layout SGDK (linha = animacao, colunas = frames).
    selected = {
        "idle": [9, 10, 9, 10, 9, 10],
        "walk": [11, 12, 13, 14, 15, 16],
        "jump": [74, 75, 75, 75, 75, 75],
        "land": [77, 78, 78, 78, 78, 78],
        "shoot": [115, 116, 117, 118, 118, 118],
    }
    frame_w = 40
    frame_h = 48
    sheet_rgba = _build_sheet(rgba, components, selected, frame_w=frame_w, frame_h=frame_h)
    indexed = _to_indexed_16(sheet_rgba)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)
    tmp = args.output + ".tmp.png"
    indexed.save(tmp)
    os.replace(tmp, args.output)
    _normalize_indexed_png(args.output, max_entries=16)

    report = {
        "source": args.input,
        "output": args.output,
        "frame_size_px": [frame_w, frame_h],
        "frame_size_tiles": [frame_w // 8, frame_h // 8],
        "states": selected,
        "detected_components": len(components),
        "sheet_size_px": [frame_w * 6, frame_h * 5],
    }
    report_path = args.report.strip() or os.path.splitext(args.output)[0] + "_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(
        "OK sheet=%s frame=%dx%d tiles=%dx%d states=5x6 report=%s"
        % (args.output, frame_w, frame_h, frame_w // 8, frame_h // 8, report_path)
    )


if __name__ == "__main__":
    main()
