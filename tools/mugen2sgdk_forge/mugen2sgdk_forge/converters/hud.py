"""HUD de luta a partir de um pacote de lifebars MUGEN (fight.def + fight.sff + .fnt).

Saida (tudo arte do pacote, nada desenhado por codigo):
  - hud_tiles.png: tileset em ordem fixa (TILESET ... NONE) com segmentos de barra estilo Street
    Fighter (vida/fantasma/vazio em 8 limites de pixel), a MESMA arte de segmento remapeada para azul
    (especial), digitos do tempo 2x2 tiles, digitos/letras do combo 2x2 tiles, icone de vitoria.
  - msg_*.png: mensagens (ROUND n, FIGHT!, K.O., TIME OVER, DRAW GAME) como sprites (metades <= 248 px).
  - paleta do HUD em PAL0 slots FIRST_SLOT..15 (o estagio usa 1..FIRST_SLOT-1).

Recortes e simplificacoes sao declarados no relatorio (moldura da barra omitida; barra com 8 linhas).
"""
from __future__ import annotations

import io
import struct
import zipfile
from collections import Counter
from dataclasses import dataclass, field

from PIL import Image

from ..parsers import ini, sff
from .sprites import _kmeans, _nearest, to_vdp, vdp_word

FIRST_SLOT = 9                       # PAL0 9..15 = 7 cores do HUD
N_COLORS = 16 - FIRST_SLOT


@dataclass
class Hud:
    tiles: Image.Image                  # tileset 8px de altura, indices = slots da PAL0
    tile_index: dict[str, int]          # nome -> indice do primeiro tile
    messages: dict[str, list[Image.Image]]   # nome -> partes (<= 248 px)
    palette: list[int]                  # 16 words (so FIRST_SLOT..15 significativos)
    report: dict = field(default_factory=dict)


def _read_fnt(data: bytes):
    """MUGEN FNT v1: PCX + texto [Def]/[Map] (char x largura)."""
    po, ps, to, ts = struct.unpack_from("<IIII", data, 16)
    img = Image.open(io.BytesIO(data[po:po + ps]))
    text = data[to:to + ts].decode("latin-1")
    size = (8, 8)
    glyphs = {}
    section = None
    for raw in text.splitlines():
        line = raw.split(";", 1)[0].strip()
        if not line:
            continue
        if line.startswith("["):
            section = line.strip("[]").lower()
            continue
        if section == "def" and line.lower().startswith("size"):
            size = tuple(int(x) for x in line.split("=", 1)[1].split(","))
        elif section == "map":
            parts = line.split()
            if len(parts) >= 3:
                glyphs[parts[0]] = (int(parts[1]), int(parts[2]))
            elif len(parts) == 1:
                glyphs[parts[0]] = (0, size[0])
    return img, size, glyphs


def _to_rgb_pixels(im: Image.Image):
    """(largura, altura, lista de RGB ou None p/ transparente) de uma imagem paletizada (indice 0 = transp.)."""
    p = im.convert("P") if im.mode != "P" else im
    pal = p.getpalette()
    w, h = p.size
    px = p.tobytes()
    return w, h, [None if v == 0 else tuple(pal[v * 3:v * 3 + 3]) for v in px]


def _sprite_rgb(s):
    return s.width, s.height, [None if v == 0 else tuple(s.palette[v]) for v in s.pixels]


def convert(pkg_path) -> Hud:
    z = zipfile.ZipFile(pkg_path)
    names = {n.lower(): n for n in z.namelist()}
    def_name = next(n for n in z.namelist() if n.lower().endswith("fight.def"))
    base = def_name.rsplit("/", 1)[0] + "/" if "/" in def_name else ""
    secs = {s.name.lower(): s for s in ini.parse(ini.decode(z.read(def_name)))}
    files = secs["files"]

    def zread(rel):
        rel = rel.replace("\\", "/")
        for cand in (base + rel, rel):
            if cand.lower() in names:
                return z.read(names[cand.lower()])
        raise FileNotFoundError(rel)

    sprites, _ = sff.parse(zread(files.get("sff")))
    by = {(s.group, s.image): s for s in sprites}
    life = secs["lifebar"]

    def spr(key):
        g, i = (int(x) for x in life.get(key).split(","))
        return by[(g, i)]

    front, mid, empty = spr("p1.front.spr"), spr("p1.mid.spr"), by.get((1, 3)) or spr("p1.front.spr")
    rnd = secs["round"]

    def rspr(key):
        v = rnd.get(key)
        if not v:
            return None
        g, i = (int(x) for x in v.split(","))
        return by.get((g, i))

    msgs_src = {"round1": rspr("round1.spr"), "round2": rspr("round2.spr"), "round3": rspr("round3.spr"),
                "fight": rspr("fight.spr"), "timeover": rspr("to.spr"), "draw": rspr("draw.spr"),
                "doubleko": rspr("dko.spr")}
    ko_anim_first = next((s for s in sprites if s.group == 80), None)
    # K.O.: o quadro da animacao 80 com mais pixels opacos no centro (texto), recortado ao conteudo
    ko_frames = sorted((s for s in sprites if s.group == 80), key=lambda s: -sum(1 for v in s.pixels if v))
    msgs_src["ko"] = ko_frames[0] if ko_frames else ko_anim_first
    win_icon = by.get((100, 0))

    fonts = {}
    for k, v, _ in files.items:
        if k.startswith("font"):
            try:
                fonts[k] = _read_fnt(zread(v))
            except (FileNotFoundError, OSError, struct.error):
                pass
    time_font = fonts.get(f"font{(secs['time'].get('counter.font') or '2').split(',')[0].strip()}")
    combo_font = fonts.get(f"font{(secs['combo'].get('counter.font') or '6').split(',')[0].strip()}")

    # ----------------------------------------------------------- paleta do HUD (7 cores)
    color_use = Counter()
    for s in [front, mid, empty] + [m for m in msgs_src.values() if m] + ([win_icon] if win_icon else []):
        for c in _sprite_rgb(s)[2]:
            if c:
                color_use[to_vdp(c)] += 1
    for f in (time_font, combo_font):
        if f:
            for c in _to_rgb_pixels(f[0])[2]:
                if c:
                    color_use[to_vdp(c)] += 1
    # paleta fixada nas cores REAIS da arte das barras (vida/fantasma/vazio: conversao direta);
    # mensagens e fontes usam a cor mais proxima dessas. Especial = mesma arte, azul por paleta.
    bar_use = Counter()
    for s in (front, mid, empty):
        for c in _sprite_rgb(s)[2]:
            if c:
                bar_use[to_vdp(c)] += 1
    base_cols = [c for c, _ in sorted(bar_use.items(), key=lambda kv: (-kv[1], kv[0]))][:N_COLORS - 2]
    if len(base_cols) < N_COLORS - 2:                 # sobra de slot: completa com cores das mensagens
        extra = [c for c in _kmeans(color_use, N_COLORS - 2) if c not in base_cols]
        base_cols = (base_cols + extra)[:N_COLORS - 2]
    blue = [(36, 108, 252), (0, 36, 180)]
    cols = (base_cols + [(0, 0, 0)] * (N_COLORS - 2))[:N_COLORS - 2] + blue
    slot_of = lambda c: FIRST_SLOT + _nearest(to_vdp(c), cols[:N_COLORS - 2])
    words = [0] * 16
    for k, c in enumerate(cols):
        words[FIRST_SLOT + k] = vdp_word(c)

    tiles: list[list[int]] = []            # cada tile = 64 indices
    index: dict[str, int] = {}

    def add(name, tlist):
        index[name] = len(tiles)
        tiles.extend(tlist)

    def rows8(s):
        """Linhas internas da barra (sem a moldura de 1 px em cima/baixo), 8 linhas."""
        w, h, px = _sprite_rgb(s)
        y0 = max(0, (h - 8) // 2)
        return [[px[(y0 + y) * w + x] for x in range(w)] for y in range(8)]

    def column(rows, x):
        return [rows[y][x] for y in range(8)]

    lr, mr, er = rows8(front), rows8(mid), rows8(empty)
    mid_x = len(lr[0]) // 2
    life_col = [column(lr, mid_x + k % 2) for k in range(8)]     # segmento: 8 colunas centrais da arte
    ghost_col = [column(mr, mid_x + k % 2) for k in range(8)]
    empty_col = [column(er, mid_x + k % 2) for k in range(8)]

    def tile_from_cols(cols8, remap=None):
        t = [0] * 64
        for x in range(8):
            for y in range(8):
                c = cols8[x][y]
                v = slot_of(c) if c else 0
                if remap and v in remap:
                    v = remap[v]
                t[y * 8 + x] = v
        return t

    kinds = {"L": life_col, "G": ghost_col, "E": empty_col}
    # barra: tile com "a" pixels do tipo A (lado do centro da tela) e o resto do tipo B (lado externo)
    for a_kind, b_kind in (("L", "G"), ("L", "E"), ("G", "E")):
        seq = []
        for a in range(9):
            seq.append(tile_from_cols([kinds[a_kind][x] if x >= 8 - a else kinds[b_kind][x] for x in range(8)]))
        add(f"bar_{a_kind}{b_kind}", seq)
    # especial: mesma arte do segmento de vida, amarelos -> azul (slots de azul) por remapeamento de paleta
    life_slots = sorted({v for t in tiles[index["bar_LE"]:index["bar_LE"] + 9] for v in t if v}, key=lambda v:
                        sum(cols[v - FIRST_SLOT]))
    empty_slots = {v for t in [tiles[index["bar_LE"]]] for v in t if v}
    remap = {}
    for v in life_slots:
        if v in empty_slots:
            continue
        remap[v] = FIRST_SLOT + N_COLORS - 1 if sum(cols[v - FIRST_SLOT]) < 380 else FIRST_SLOT + N_COLORS - 2
    seq = []
    for a in range(9):
        seq.append(tile_from_cols([life_col[x] if x >= 8 - a else empty_col[x] for x in range(8)], remap))
    add("bar_SE", seq)

    def glyph_tiles(font, ch, cell_w=16, cell_h=16):
        img, size, glyphs = font
        if ch not in glyphs:
            return [[0] * 64 for _ in range((cell_w // 8) * (cell_h // 8))]
        gx, gw = glyphs[ch]
        w, h, px = _to_rgb_pixels(img)
        gh = min(size[1], h)
        out = []
        ox = (cell_w - min(gw, cell_w)) // 2
        oy = (cell_h - gh) // 2
        for ty in range(cell_h // 8):
            for tx in range(cell_w // 8):
                t = [0] * 64
                for y in range(8):
                    for x in range(8):
                        sx, sy = tx * 8 + x - ox, ty * 8 + y - oy
                        if 0 <= sx < min(gw, cell_w) and 0 <= sy < gh:
                            c = px[sy * w + gx + sx]
                            t[y * 8 + x] = slot_of(c) if c else 0
                out.append(t)
        return out

    if time_font:
        for d in "0123456789":
            add(f"time_{d}", glyph_tiles(time_font, d))
    if combo_font:
        for ch in "0123456789":
            add(f"combo_{ch}", glyph_tiles(combo_font, ch))
        for ch in "HITS":
            add(f"combo_{ch}", glyph_tiles(combo_font, ch))
    if win_icon:
        w, h, px = _sprite_rgb(win_icon)
        seq = []
        for ty in range(2):
            for tx in range(2):
                t = [0] * 64
                for y in range(8):
                    for x in range(8):
                        sx, sy = tx * 8 + x, ty * 8 + y
                        if sx < w and sy < h and px[sy * w + sx]:
                            t[y * 8 + x] = slot_of(px[sy * w + sx])
                seq.append(t)
        add("win", seq)

    sheet = Image.new("P", (8 * len(tiles), 8), 0)
    buf = bytearray(8 * len(tiles) * 8)
    W = 8 * len(tiles)
    for i, t in enumerate(tiles):
        for y in range(8):
            for x in range(8):
                buf[y * W + i * 8 + x] = t[y * 8 + x]
    sheet = Image.frombytes("P", (W, 8), bytes(buf))
    flat = []
    for k in range(16):
        c = cols[k - FIRST_SLOT] if k >= FIRST_SLOT else (250, 0, 250)
        flat += list(c)
    sheet.putpalette(flat)

    # mensagens: recorte ao conteudo, quantizacao nos slots do HUD, metades <= 248 px, 8-alinhado
    messages = {}
    for name, s in msgs_src.items():
        if s is None:
            continue
        w, h, px = _sprite_rgb(s)
        xs = [i % w for i, c in enumerate(px) if c]
        ys = [i // w for i, c in enumerate(px) if c]
        if not xs:
            continue
        x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
        cw, chh = x1 - x0, y1 - y0
        # faixas de ate 128 px: com altura <= 128 cada parte usa <= 16 sprites de hardware
        nparts = -(-cw // 128)
        step = -(-cw // nparts)
        halves = [(x0 + k * step, min(x1, x0 + (k + 1) * step)) for k in range(nparts)]
        parts = []
        for a, b in halves:
            pw, ph = -(-(b - a) // 8) * 8, -(-chh // 8) * 8
            im = Image.new("P", (pw, ph), 0)
            data = bytearray(pw * ph)
            for y in range(chh):
                for x in range(b - a):
                    c = px[(y0 + y) * w + a + x]
                    if c:
                        data[y * pw + x] = slot_of(c)
            im = Image.frombytes("P", (pw, ph), bytes(data))
            im.putpalette(flat)
            parts.append(im)
        messages[name] = parts

    rep = {"palette_slots": f"PAL0 {FIRST_SLOT}..15", "colors": [list(c) for c in cols], "tiles": len(tiles),
           "tile_index": index, "messages": {k: [p.size for p in v] for k, v in messages.items()},
           "simplifications": ["moldura da barra (1 px em cima/baixo) omitida: barra com 8 linhas",
                               "especial usa a arte do segmento de vida remapeada para azul (cor por paleta)",
                               f"arte quantizada em {N_COLORS} cores (PAL0 {FIRST_SLOT}..15)",
                               "K.O.: um quadro da animacao 80 (a elipse animada nao e reproduzida)"]}
    return Hud(sheet, index, messages, words, rep)
