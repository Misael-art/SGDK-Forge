"""Medicao de viabilidade de um stage MUGEN no Mega Drive (E4.0). Nao converte nada.

- por camada: tamanho, cores MD (RGB 3-3-3), tiles 8x8 unicos (com espelhos), pior tile, pior bloco 16x16;
- por PLANO composto (o que realmente vai a VRAM): varias estrategias de delta/largura;
- orcamento real da luta: le do rom.bin + symbol.txt os maxNumTile/numTile que o runtime reserva.

Tudo e medido nos indices da paleta do SFF; nenhuma decisao de reducao e tomada aqui.
"""
from __future__ import annotations

import re
import struct
import zipfile
from pathlib import Path

from .parsers import sff, stage as stage_parser

MD_H = 224
TILES_VRAM = 0xC000 // 32          # SGDK 2.11, planos 64x32: mapas a partir de 0xC000
FONT_LEN, SYSTEM_TILES = 96, 16


def _md(rgb) -> tuple[int, int, int]:
    return tuple(round(v / 255 * 7) for v in rgb)


def _canon(t):
    h = tuple(r[::-1] for r in t)
    v = t[::-1]
    return min(t, h, v, tuple(r[::-1] for r in v))


def _tiles(get, w, h):
    """Itera tiles 8x8 (tuplas de linhas de indices) de uma superficie w x h."""
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            yield tuple(tuple(get(tx + x, ty + y) for x in range(8)) for y in range(8))


def layer_stats(s: sff.Sprite, pal) -> dict:
    W, H, px = s.width, s.height, s.pixels
    get = lambda x, y: px[y * W + x] if x < W and y < H else 0  # noqa: E731
    uniq, worst = set(), 0
    for t in _tiles(get, W, H):
        uniq.add(_canon(t))
        worst = max(worst, len({_md(pal[p]) for r in t for p in r if p}))
    blk = 0
    for by in range(0, H, 16):
        for bx in range(0, W, 16):
            blk = max(blk, len({_md(pal[get(x, y)]) for y in range(by, by + 16) for x in range(bx, bx + 16)
                                if x < W and y < H and get(x, y)}))
    used = set(px) - {0}
    return {"size": [W, H], "sff_indices": len(used), "md_colours": len({_md(pal[i]) for i in used}),
            "tiles_total": ((W + 7) // 8) * ((H + 7) // 8), "tiles_unique_with_flip": len(uniq),
            "max_md_colours_per_tile": worst, "max_md_colours_per_16px_block": blk}


def compose(st, sprites, names: list[str], delta: float, width: int, crop_top: int) -> list[list[int]]:
    """Plano composto: coluna u mostra o mundo com a camera no limite esquerdo (boundleft)."""
    layers = {la.name: la for la in st.layers}
    buf = [[0] * width for _ in range(MD_H)]
    cam = -st.camera["boundleft"]
    half = st.localcoord[0] // 2
    for n in names:
        la = layers[n]
        s = sprites[tuple(la.spriteno)]
        ox = half + int(la.start[0]) - s.axis_x + round(cam * delta)
        oy = int(la.start[1]) - s.axis_y - crop_top
        reps = range(-3, 4) if la.tile[0] == 1 else (0,)
        for y in range(s.height):
            yy = oy + y
            if not 0 <= yy < MD_H:
                continue
            row = s.pixels[y * s.width:(y + 1) * s.width]
            for k in reps:
                base = ox + k * (s.width + int(la.tilespacing[0]))
                for x, p in enumerate(row):
                    if la.mask and p == 0:
                        continue
                    u = base + x
                    if 0 <= u < width:
                        buf[yy][u] = p
    return buf


def plane_stats(buf, pal, rows=(0, MD_H)) -> dict:
    W = len(buf[0])
    uniq, cols, empty = set(), set(), 0
    for t_i, t in enumerate(_tiles(lambda x, y: buf[y][x] if x < W else 0, W, MD_H)):
        ty = (t_i // ((W + 7) // 8)) * 8
        if not rows[0] <= ty < rows[1]:
            continue
        if not any(any(r) for r in t):
            empty += 1
            continue
        uniq.add(_canon(t))
        cols |= {_md(pal[p]) for r in t for p in r if p}
    return {"width": W, "tiles_unique_with_flip": len(uniq), "empty_cells": empty, "md_colours": len(cols)}


def fight_vram(rom: Path, symbols: Path, res: Path, sprite_pool: int,
               body_reservation: bool = True, bgfx_loan: bool = True) -> dict:
    """Orcamento da luta lido da ROM: o que o runtime reserva antes de qualquer stage."""
    data = rom.read_bytes()
    sym = {}
    for line in symbols.read_text().splitlines():
        m = re.match(r"([0-9a-fA-F]+)\s+\S\s+(\S+)", line)
        if m:
            sym[m.group(2)] = int(m.group(1), 16)
    text = res.read_text()
    sheets = []
    for n in re.findall(r"SPRITE (\S+) ", text):
        if n in sym:
            a = sym[n]
            sheets.append((struct.unpack(">H", data[a + 14:a + 16])[0], n))    # SpriteDefinition.maxNumTile
    sheets.sort(reverse=True)
    body = next(s for s in sheets if not s[1].endswith("_fx"))
    tileset = lambda a: struct.unpack(">H", data[a + 2:a + 4])[0]          # noqa: E731  TileSet.numTile
    bgfx = [n for n in re.findall(r"IMAGE (\S+) ", text) if n in sym]
    bgfx_tiles = sum(tileset(struct.unpack(">I", data[sym[n] + 4:sym[n] + 8])[0]) for n in bgfx)
    hud = tileset(sym["mg_hud_tiles"]) if "mg_hud_tiles" in sym else 0
    portrait = tileset(sym[p]) if (p := next((n for n in sym if n.endswith("_portrait")), None)) else 0
    user = TILES_VRAM - FONT_LEN - sprite_pool - SYSTEM_TILES
    # o runtime reserva o maior sheet de CORPO (sufixo _fx == pal 1, conferido nos 87 sheets do Ken);
    # a regiao do fundo de super e emprestada: tiles so sobem durante o super, o palco oculto
    fixed = body[0] if body_reservation else sheets[0][0]
    used = 2 * fixed + bgfx_tiles + hud + 2 * portrait
    free = user - used
    return {"tile_space": TILES_VRAM, "font": FONT_LEN, "sprite_pool": sprite_pool, "system": SYSTEM_TILES,
            "user_area": user, "fighter_fixed_each": fixed,
            "fighter_fixed_driver": body[1] if body_reservation else sheets[0][1],
            "largest_sheet_any": list(sheets[0]), "largest_body_sheet": list(body), "bgfx_tiles": bgfx_tiles,
            "hud_tiles": hud, "portrait_tiles_each": portrait, "used": used, "free_for_stage": free,
            "stage_region_with_bgfx_loan": free + (bgfx_tiles if bgfx_loan else 0),
            "rules": {"body_reservation": body_reservation, "bgfx_loan": bgfx_loan}}


PLANS = [
    ("BG_B ceu+castelo+muro, delta 0.43 (maior que cabe em 512 px)", ["BG 0b", "BG 1", "BG 2"], 0.43, None),
    ("BG_B ceu+castelo+muro, delta 0.50", ["BG 0b", "BG 1", "BG 2"], 0.50, None),
    ("BG_A telhados+chao, delta 0.67", ["BG 3", "BG 4a", "BG 4b"], 0.67, None),
    ("BG_A telhados+chao, delta 1.0 (1:1 como no briefing)", ["BG 3", "BG 4a", "BG 4b"], 1.0, None),
    ("S1 BG_B estatico 320 (sem scroll)", ["BG 0b", "BG 1", "BG 2"], 0.0, 320),
    ("S1 BG_A estatico 320 (sem scroll)", ["BG 3", "BG 4a", "BG 4b"], 0.0, 320),
    ("so chao (4a+4b), delta 1.0", ["BG 4a", "BG 4b"], 1.0, None),
    ("so telhados, delta 0.67", ["BG 3"], 0.67, None),
]


def measure(zip_path: Path, def_name: str, sff_name: str, crop_top: int = 8) -> dict:
    with zipfile.ZipFile(zip_path) as z:
        st = stage_parser.parse(z.read(def_name).decode("latin-1"), def_name)
        sprites_list, warn = sff.parse(z.read(sff_name))
    sprites = {(s.group, s.image): s for s in sprites_list}
    pal = sprites_list[0].palette
    span = st.camera["boundright"] - st.camera["boundleft"]
    layers = {}
    for la in st.layers:
        if la.spriteno:
            layers[la.name] = {"type": la.type, "spriteno": list(la.spriteno), "delta_x": la.delta[0],
                               **layer_stats(sprites[tuple(la.spriteno)], pal)}
    all_idx = set()
    for s in sprites_list:
        all_idx |= set(s.pixels) - {0}
    plans = []
    for name, names, d, w in PLANS:
        width = w or (st.localcoord[0] + round(span * d) + 7) // 8 * 8
        plans.append({"plan": name, "delta": d, **plane_stats(compose(st, sprites, names, d, width, crop_top), pal)})
    sky = compose(st, sprites, ["BG 0b", "BG 1", "BG 2"], 0.43, 520, crop_top)
    return {"stage": st.name, "localcoord": list(st.localcoord), "camera_span": span, "crop_top": crop_top,
            "parser_warnings": st.warnings, "sff_warnings": warn, "stage_md_colours": len({_md(pal[i]) for i in all_idx}),
            "stage_sff_indices": len(all_idx), "layers": layers, "planes": plans,
            "bg_b_bands_delta_0_43": {"ceu linhas 0-47": plane_stats(sky, pal, (0, 48)),
                                      "castelo+muro linhas 48-223": plane_stats(sky, pal, (48, MD_H))}}
