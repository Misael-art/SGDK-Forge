"""Sprites/paletas MUGEN -> sheets SGDK (SPRITE do rescomp) + paletas CRAM de 16 cores.

Decisoes (todas registradas no relatorio):
- Paleta do CORPO: os indices usados pelas sprites do personagem que cabem em 15 cores viram
  as cores 1..15 de uma paleta de hardware; indice 0 = transparente. Cada .act (pal1..palN)
  gera uma variante CRAM com o mesmo mapeamento (troca de cor em runtime = PAL_setColors).
- Paleta de EFEITOS (faiscas, projeteis): indices restantes quantizados para 15 cores.
- Cor -> 9 bits do VDP (3 bits/canal), arredondamento ao nivel mais proximo.
- Pixel com indice fora da paleta escolhida = cor mais proxima (aproximado, contado).
- Sheet = 1 grupo de sprites com celula comum ancorada no eixo; celula <= 248 px (limite rescomp).
  Grupos maiores sao divididos; imagem individual > 248 px = nao suportada.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from PIL import Image

MAX_CELL = 248
MAX_HW_SPRITES = 16


def to_vdp(rgb) -> tuple[int, int, int]:
    """RGB 8-bit -> RGB 8-bit ja quantizado nos 8 niveis do VDP (0,36,..,252 aprox.)."""
    return tuple(min(7, (c + 18) // 36) * 36 for c in rgb)


def vdp_word(rgb) -> int:
    r, g, b = (min(7, (c + 18) // 36) for c in rgb)
    return (b << 9) | (g << 5) | (r << 1)


def _dist(a, b):
    # distancia perceptual simples (pesos de luminancia)
    return 2 * (a[0] - b[0]) ** 2 + 4 * (a[1] - b[1]) ** 2 + 3 * (a[2] - b[2]) ** 2


@dataclass
class PaletteMap:
    name: str
    src_indices: list[int]                  # indice MUGEN de cada slot 1..15
    remap: dict[int, int]                   # indice MUGEN -> slot 0..15
    approx_indices: dict[int, int]          # indices fora da paleta -> slot (aproximados)


@dataclass
class SheetImage:
    group: int
    image: int
    frame: int                               # coluna na sheet
    ox: int                                  # deslocamento do eixo MUGEN dentro da celula
    oy: int
    width: int
    height: int
    hw_sprites: int


@dataclass
class Sheet:
    name: str
    palette: str                             # body | fx
    cell_w: int
    cell_h: int
    axis_x: int                              # eixo dentro da celula
    axis_y: int
    images: list[SheetImage]
    png: Image.Image | None = None


@dataclass
class SpriteResult:
    body: PaletteMap
    fx: PaletteMap
    body_variants: list[tuple[str, list[int]]]   # (nome, 16 words CRAM)
    fx_palette: list[int]
    sheets: list[Sheet]
    locate: dict[tuple[int, int], tuple[int, int]]   # (grupo,img) -> (sheet idx, frame)
    report: dict = field(default_factory=dict)


def _nearest(color, pal_colors):
    best, bi = None, 0
    for i, c in enumerate(pal_colors):
        d = _dist(color, c)
        if best is None or d < best:
            best, bi = d, i
    return bi


def _kmeans(weighted: Counter, k: int, rounds: int = 12) -> list[tuple[int, int, int]]:
    """Quantizacao deterministica: k-means ponderado, sementes = cores mais frequentes."""
    pts = sorted(weighted.items(), key=lambda x: (-x[1], x[0]))
    if len(pts) <= k:
        return [c for c, _ in pts]
    cent = [c for c, _ in pts[:k]]
    for _ in range(rounds):
        acc = [[0, 0, 0, 0] for _ in cent]
        for c, w in pts:
            j = _nearest(c, cent)
            a = acc[j]
            a[0] += c[0] * w; a[1] += c[1] * w; a[2] += c[2] * w; a[3] += w
        new = [to_vdp((a[0] // a[3], a[1] // a[3], a[2] // a[3])) if a[3] else cent[j]
               for j, a in enumerate(acc)]
        if new == cent:
            break
        cent = new
    # remove duplicatas mantendo ordem
    out = []
    for c in cent:
        if c not in out:
            out.append(c)
    return out


def _hw_estimate(im: Image.Image) -> int:
    bbox = im.getbbox()
    if not bbox:
        return 0
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    return -(-w // 32) * -(-h // 32)


def convert(ch, used_only: bool = True) -> SpriteResult:
    rep: dict = {"unsupported_images": [], "split_groups": [], "hw_over_limit": []}
    used = {(f.group, f.image) for a in ch.anims.values() for f in a.frames if f.group >= 0}
    sprites = [s for s in ch.sprites if not used_only or (s.group, s.image) in used]
    base_pal = ch.palettes[0][1] if ch.palettes else sprites[0].palette

    # 1) classificar sprites: corpo = subconjunto dos 16 indices mais frequentes do grupo 0 (stand)
    usage = Counter()
    for s in sprites:
        usage.update(set(s.pixels))
    stand = [s for s in sprites if s.group == 0] or sprites
    body_set = set()
    for s in stand:
        body_set |= set(s.pixels)
    body_set.discard(0)
    body_idx = sorted(body_set, key=lambda i: -usage[i])[:15]
    body_idx.sort()
    body_cols = [to_vdp(base_pal[i]) for i in body_idx]

    body_ok = set(body_idx)

    def is_body(s):
        # corpo = maioria (> 50%) dos pixels opacos ja na paleta do corpo; o resto vira a cor mais proxima
        c = Counter(s.pixels)
        c.pop(0, None)
        total = sum(c.values()) or 1
        return sum(n for i, n in c.items() if i in body_ok) / total > 0.5

    kinds = {(s.group, s.image): ("body" if is_body(s) else "fx") for s in sprites}

    def build_map(name, idx, cols, candidates):
        remap = {0: 0}
        for slot, i in enumerate(idx, 1):
            remap[i] = slot
        approx = {}
        for i in sorted(candidates - set(remap)):
            approx[i] = 1 + _nearest(to_vdp(base_pal[i]), cols) if cols else 0
        return PaletteMap(name, idx, remap, approx)

    body_all = set()
    fx_all = Counter()
    for s in sprites:
        if kinds[(s.group, s.image)] == "body":
            body_all |= set(s.pixels)
        else:
            for i, n in Counter(s.pixels).items():
                fx_all[i] += n
    body_all.discard(0)
    body_map = build_map("body", body_idx, body_cols, body_all)

    # 2) paleta de efeitos: 15 cores por mediana simples sobre cores VDP ponderadas por uso
    fx_all.pop(0, None)
    fx_colors = Counter()
    for i, n in fx_all.items():
        fx_colors[to_vdp(base_pal[i])] += n
    fx_cols = _kmeans(fx_colors, 15)
    fx_idx_direct = [i for i in sorted(fx_all) if to_vdp(base_pal[i]) in fx_cols]
    fx_map = PaletteMap("fx", [], {0: 0}, {})
    for i in sorted(fx_all):
        c = to_vdp(base_pal[i])
        if c in fx_cols:
            fx_map.remap[i] = 1 + fx_cols.index(c)
        else:
            fx_map.approx_indices[i] = 1 + _nearest(c, fx_cols)
    fx_map.src_indices = fx_idx_direct

    # 3) variantes de paleta do corpo (uma por .act)
    variants = []
    for name, pal in (ch.palettes or [("sff", base_pal)]):
        words = [0] + [vdp_word(pal[i]) for i in body_idx]
        variants.append((name, (words + [0] * 16)[:16]))
    fx_words = ([0] + [vdp_word(c) for c in fx_cols] + [0] * 16)[:16]

    # 4) sheets por grupo
    by_group: dict[int, list] = {}
    for s in sorted(sprites, key=lambda s: (s.group, s.image)):
        by_group.setdefault((s.group, kinds[(s.group, s.image)]), []).append(s)
    sheets: list[Sheet] = []
    locate = {}
    approx_pixels = Counter()
    for (grp, kind), items in sorted(by_group.items()):
        pmap = body_map if kind == "body" else fx_map
        ok = []
        for s in items:
            if s.width > MAX_CELL or s.height > MAX_CELL:
                rep["unsupported_images"].append(
                    {"sprite": [s.group, s.image], "size": [s.width, s.height],
                     "reason": f"maior que {MAX_CELL}px (limite de frame do rescomp); dividir/reduzir manualmente"})
                continue
            hw = _hw_estimate(Image.frombytes("P", (s.width, s.height), s.pixels))
            if hw > MAX_HW_SPRITES:
                rep["unsupported_images"].append(
                    {"sprite": [s.group, s.image], "size": [s.width, s.height], "hw_sprites": hw,
                     "reason": f"exige {hw} sprites de hardware (limite {MAX_HW_SPRITES} por quadro); dividir manualmente"})
                continue
            ok.append(s)
        chunks, cur = [], []
        for s in ok:
            trial = cur + [s]
            l = max(x.axis_x for x in trial); r = max(x.width - x.axis_x for x in trial)
            t = max(x.axis_y for x in trial); b = max(x.height - x.axis_y for x in trial)
            if cur and (-(-(l + r) // 8) * 8 > MAX_CELL or -(-(t + b) // 8) * 8 > MAX_CELL):
                chunks.append(cur)
                cur = [s]
            else:
                cur = trial
        if cur:
            chunks.append(cur)
        if len(chunks) > 1:
            rep["split_groups"].append({"group": grp, "sheets": len(chunks)})
        for ci, chunk in enumerate(chunks):
            l = max(x.axis_x for x in chunk); r = max(x.width - x.axis_x for x in chunk)
            t = max(x.axis_y for x in chunk); b = max(x.height - x.axis_y for x in chunk)
            cw, chh = -(-(l + r) // 8) * 8, -(-(t + b) // 8) * 8
            name = f"g{grp}" + (f"_{ci}" if len(chunks) > 1 else "") + ("" if kind == "body" else "_fx")
            sheet = Sheet(name, kind, cw, chh, l, t, [])
            png = Image.new("P", (cw * len(chunk), chh), 0)
            for fi, s in enumerate(chunk):
                lut = bytes(pmap.remap.get(i, pmap.approx_indices.get(i, 0)) for i in range(256))
                for i, n in Counter(s.pixels).items():
                    if i not in pmap.remap:
                        approx_pixels[kind] += n
                im = Image.frombytes("P", (s.width, s.height), s.pixels.translate(lut))
                x0, y0 = fi * cw + (l - s.axis_x), t - s.axis_y
                png.paste(im, (x0, y0))
                hw = _hw_estimate(im)
                if hw > MAX_HW_SPRITES:
                    rep["hw_over_limit"].append({"sprite": [s.group, s.image], "estimate": hw})
                sheet.images.append(SheetImage(s.group, s.image, fi, l - s.axis_x, t - s.axis_y,
                                               s.width, s.height, hw))
                locate[(s.group, s.image)] = (len(sheets), fi)
            pal_rgb = body_cols if kind == "body" else fx_cols
            flat = [250, 0, 250] + [c for rgb in pal_rgb for c in rgb]
            png.putpalette((flat + [0] * 48)[:48])
            sheet.png = png
            sheets.append(sheet)

    rep["body_palette"] = {"mugen_indices": body_idx, "approx_indices": body_map.approx_indices,
                           "approx_pixels": approx_pixels["body"]}
    rep["fx_palette"] = {"source_colors": len(fx_colors), "kept": len(fx_cols),
                         "approx_indices": len(fx_map.approx_indices), "approx_pixels": approx_pixels["fx"]}
    rep["sheets"] = len(sheets)
    rep["images"] = len(locate)
    rep["variants"] = [n for n, _ in variants]
    return SpriteResult(body_map, fx_map, variants, fx_words, sheets, locate, rep)
