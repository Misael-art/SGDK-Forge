"""Efeitos de fundo em tela cheia animados por paleta (ex.: fundo de super do MUGEN).

Grupos com imagens de tela cheia que nao cabem como sprite, mas cuja geometria e IDENTICA entre
quadros (so os indices de cor mudam), viram:
  - UMA imagem de plano (BG_B) 320x224 com ate 14 cores (slots 1..14 da PAL0), e
  - uma tabela de paleta por imagem do grupo (animacao por troca de CRAM, ~28 bytes/quadro).

Geometria que nao cabe na VRAM, em ordem de preferencia:
  direct   -> imagem inteira (tiles unicos com flips <= orcamento);
  mirror_h -> metade esquerda espelhada (efeitos radiais/simetricos);
  mirror_4 -> quadrante superior esquerdo espelhado nas 4 direcoes;
  reduce   -> reducao de tiles (k-medianas) ate o orcamento.
O rescomp (IMAGE ... ALL) deduplica os tiles espelhados. Tudo que nao e "direct" e APROXIMACAO
declarada no relatorio (estrategia, simetria medida, tiles).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from PIL import Image

from .sprites import to_vdp, vdp_word

SCREEN_W, SCREEN_H = 320, 224
MAX_COLORS = 14            # PAL0 slots 1..14 (0 = fundo, 15 = texto do HUD)
TILE_BUDGET = 480


@dataclass
class BgFx:
    group: int
    anims: list[int]                       # animacoes que usam o grupo
    png: Image.Image                       # 320x224 indexada (0 nao usado; 1..14 = niveis)
    pals: list[list[int]]                  # por imagem do grupo: 16 words (slot 0 e 15 = 0, ignorados)
    image_ids: list[int]                   # imagem do grupo correspondente a cada linha de pals
    elem_img: dict[int, list[int]]         # anim -> indice em pals de cada elemento (255 = nenhum)
    report: dict = field(default_factory=dict)


def _reduce_tiles(px: bytes, w: int, h: int, budget: int):
    """Agrupamento guloso deterministico (numpy): cada tile vira o representante mais proximo
    (considerando flips H/V) se a distancia L1 de nivel <= limiar; o limiar dobra ate caber."""
    import numpy as np
    a = np.frombuffer(px, dtype=np.uint8).reshape(h // 8, 8, w // 8, 8).transpose(0, 2, 1, 3).reshape(-1, 8, 8)
    tiles = a.astype(np.int16)
    variants = np.stack([tiles, tiles[:, :, ::-1], tiles[:, ::-1, :], tiles[:, ::-1, ::-1]], 1).reshape(-1, 4, 64)
    n = len(tiles)
    thr = 0
    while True:
        reps = np.zeros((budget + 1, 64), np.int16)
        nrep = 0
        assign = np.zeros(n, np.int32)
        over = False
        for i in range(n):
            if nrep:
                d = np.abs(variants[i][:, None, :] - reps[None, :nrep, :]).sum(2)   # (4, nrep)
                j = int(d.min(0).argmin())
                if int(d[:, j].min()) <= thr:
                    assign[i] = j
                    continue
            if nrep == budget:
                over = True
                break
            reps[nrep] = variants[i][0]
            assign[i] = nrep
            nrep += 1
        if not over:
            break
        thr += 2                    # menor limiar que cabe no orcamento (usa a VRAM disponivel)
    # refinamento (k-medianas): representante = mediana dos tiles atribuidos (na orientacao casada);
    # depois reatribui cada tile ao representante mais proximo. Mais fiel que o guloso puro.
    reps = reps[:nrep].copy()
    for _ in range(6):
        d = np.abs(variants[:, :, None, :] - reps[None, None, :, :]).sum(3)      # (n, 4, R)
        best_v = d.argmin(1)                                                       # (n, R)
        dmin = d.min(1)                                                            # (n, R)
        assign = dmin.argmin(1)
        oriented = variants[np.arange(n), best_v[np.arange(n), assign]]            # (n, 64)
        new = reps.copy()
        for r in range(len(reps)):
            m = assign == r
            if m.any():
                new[r] = np.median(oriented[m], axis=0).round().astype(np.int16)
        if np.array_equal(new, reps):
            break
        reps = new
    out = np.empty_like(tiles)
    err = 0
    for i in range(n):
        r = reps[assign[i]].reshape(8, 8)
        rv = [r, r[:, ::-1], r[::-1, :], r[::-1, ::-1]]
        k = int(np.argmin([np.abs(v - tiles[i]).sum() for v in rv]))
        out[i] = rv[k]
        err += int(np.abs(rv[k] - tiles[i]).sum())
    img = out.reshape(h // 8, w // 8, 8, 8).transpose(0, 2, 1, 3).reshape(h, w).astype(np.uint8)
    return img.tobytes(), n, nrep, thr, err / (w * h)


def _unique_tiles(px: bytes, w: int, h: int) -> int:
    seen = set()
    for ty in range(h // 8):
        for tx in range(w // 8):
            t = tuple(tuple(px[(ty * 8 + y) * w + tx * 8:(ty * 8 + y) * w + tx * 8 + 8]) for y in range(8))
            v = (t, tuple(r[::-1] for r in t), t[::-1], tuple(r[::-1] for r in t[::-1]))
            if not any(x in seen for x in v):
                seen.add(t)
    return len(seen)


def _mirror(px: bytes, w: int, h: int, four: bool) -> bytes:
    out = bytearray(px)
    hw, hh = w // 2, h // 2
    for y in range(h):
        sy = y if (not four or y < hh) else h - 1 - y
        for x in range(w):
            sx = x if x < hw else w - 1 - x
            out[y * w + x] = px[sy * w + sx]
    return bytes(out)


def _symmetry(px: bytes, w: int, h: int) -> float:
    return sum(px[y * w + x] == px[y * w + (w - 1 - x)] for y in range(h) for x in range(w)) / (w * h)


def detect(ch, unsupported: list[dict], budget: int = TILE_BUDGET) -> list[BgFx]:
    groups = defaultdict(list)
    for u in unsupported:
        groups[u["sprite"][0]].append(u["sprite"][1])
    by_key = {(s.group, s.image): s for s in ch.sprites}
    base_pal = ch.palettes[0][1] if ch.palettes else None
    out = []
    for g, imgs in sorted(groups.items()):
        frames = [by_key[(g, i)] for i in sorted(imgs) if (g, i) in by_key]
        if not frames or frames[0].width < 256:
            continue
        f0 = frames[0]
        if any((f.width, f.height) != (f0.width, f0.height) for f in frames):
            continue
        idx0 = sorted(set(f0.pixels), key=lambda i: sum(to_vdp((base_pal or f0.palette)[i])))
        if len(idx0) > MAX_COLORS:
            continue
        maps = []
        ok = True
        for f in frames:
            m = defaultdict(Counter)
            for a, b in zip(f0.pixels, f.pixels):
                m[a][b] += 1
            if any(len(c) > 1 for c in m.values()):      # geometria diferente: nao e animacao de paleta
                ok = False
                break
            maps.append({a: c.most_common(1)[0][0] for a, c in m.items()})
        if not ok:
            continue
        slot = {i: k + 1 for k, i in enumerate(idx0)}
        # recorte central 320x224 do quadro MUGEN (tipicamente 320x240)
        x0 = max(0, (f0.width - SCREEN_W) // 2)
        y0 = max(0, (f0.height - SCREEN_H) // 2)
        px = bytearray(SCREEN_W * SCREEN_H)
        for y in range(min(SCREEN_H, f0.height - y0)):
            row = f0.pixels[(y0 + y) * f0.width + x0:(y0 + y) * f0.width + x0 + SCREEN_W]
            px[y * SCREEN_W:y * SCREEN_W + len(row)] = bytes(slot[v] for v in row)
        px = bytes(px)
        strategy, thr, err = "direct", 0, 0.0
        after = _unique_tiles(px, SCREEN_W, SCREEN_H)
        reduced = px
        if after > budget:
            for name, four in (("mirror_h", False), ("mirror_4", True)):
                cand = _mirror(px, SCREEN_W, SCREEN_H, four)
                n = _unique_tiles(cand, SCREEN_W, SCREEN_H)
                if n <= budget:
                    strategy, reduced, after = name, cand, n
                    break
            else:
                strategy = "reduce"
                reduced, _n, after, thr, err = _reduce_tiles(px, SCREEN_W, SCREEN_H, budget)
        pal = base_pal or f0.palette
        pals = []
        for m in maps:
            words = [0] * 16
            for i, k in slot.items():
                words[k] = vdp_word(pal[m[i]])
            pals.append(words)
        im = Image.frombytes("P", (SCREEN_W, SCREEN_H), reduced)
        flat = [0, 0, 0] + [c for i in idx0 for c in to_vdp(pal[i])]
        im.putpalette((flat + [0] * 48)[:48])
        img_ids = [f.image for f in frames]
        anims = sorted(a for a, act in ch.anims.items()
                       if any(fr.group == g for fr in act.frames) and all(fr.group in (g, -1) for fr in act.frames))
        elem_img = {a: [img_ids.index(fr.image) if fr.group == g and fr.image in img_ids else 255
                        for fr in ch.anims[a].frames] for a in anims}
        out.append(BgFx(g, anims, im, pals, img_ids, elem_img, {
            "group": g, "anims": anims, "images": len(frames), "colors": len(idx0),
            "strategy": strategy, "tiles": after, "tile_budget": budget,
            "source_horizontal_symmetry": round(_symmetry(px, SCREEN_W, SCREEN_H), 3),
            "merge_threshold": thr, "mean_level_error_per_pixel": round(err, 4),
            "fidelity": "direct" if strategy == "direct" else "approximate",
            "note": "animacao por paleta: direta (geometria identica, 14 cores); geometria conforme 'strategy'"}))
    return out
