"""Pacote de passagem do piloto de FX para o agente grafico (REGRA 1, orcamento 8+6+1).

Gera, para UMA familia de acoes AIR:
- pixels (fora do Git: conteudo de terceiros) em `rascunho/processado/fx_pilot_<nome>/`:
  fonte original RGB do SFF, quadro convertido atual (indices da linha de efeitos compartilhada),
  amostras da paleta alvo e da paleta atual;
- documentos versionados em `doc/mugen/fx_pilot_<nome>/`: contrato de quadros (AIR: tempo, deslocamento,
  eixo, Clsn, quadros vazios), papeis da paleta alvo em palavras VDP, orcamento (tiles/DMA por quadro),
  uso de cores de efeito do CATALOGO inteiro (o slot de FX e unico para todas as familias) e hashes.
Nada aqui aprova arte: a saida do agente e candidata; o aceite do piloto nao e aceite do personagem.
"""
from __future__ import annotations

import collections
import hashlib
import io
import json
from pathlib import Path

from PIL import Image

from . import character
from .converters import sprites as spr_conv
from .converters.sprites import vdp_rgb
from .source import Source


def _png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def _tiles(im: Image.Image) -> int:
    w, h = im.size
    px = im.load()
    return sum(1 for ty in range(0, h, 8) for tx in range(0, w, 8)
               if any(px[x, y] for y in range(ty, min(ty + 8, h)) for x in range(tx, min(tx + 8, w))))


def _swatch(words: list[int], labels: list[str]) -> Image.Image:
    im = Image.new("RGB", (16 * len(words), 16))
    for k, w in enumerate(words):
        im.paste(vdp_rgb(w), (16 * k, 0, 16 * k + 16, 16))
    return im


def build(pkg: Path, project: Path, name: str, actions: list[int], vivid_clothing: bool = True) -> dict:
    ch = character.load(Source(pkg))
    spr = spr_conv.convert(ch, vivid_clothing=vivid_clothing)
    pix = project / "rascunho" / "processado" / f"fx_pilot_{name}"
    doc = project / "doc" / "mugen" / f"fx_pilot_{name}"
    pix.mkdir(parents=True, exist_ok=True)
    doc.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {"source_package": ch.source_sha256}

    def put(path: Path, data: bytes):
        path.write_bytes(data)
        hashes[str(path.relative_to(project))] = hashlib.sha256(data).hexdigest()

    by = {(s.group, s.image): s for s in ch.sprites}
    frames, used = [], set()
    for a in actions:
        act = ch.anims[a]
        for k, f in enumerate(act.frames):
            used.add((f.group, f.image))
            frames.append({"action": a, "elem": k + 1, "loopstart": k == act.loopstart and act.loopstart > 0,
                           "sprite": [f.group, f.image], "empty": f.group < 0, "time": f.time,
                           "offset": [f.x, f.y], "hflip": f.hflip, "vflip": f.vflip, "blend": f.blend,
                           "clsn1": [list(b) for b in getattr(f, "clsn1", [])],
                           "clsn2": [list(b) for b in getattr(f, "clsn2", [])]})
    sprites_out = []
    for g, i in sorted(u for u in used if u[0] >= 0):
        s = by[(g, i)]
        src = Image.frombytes("P", (s.width, s.height), s.pixels)
        src.putpalette([c for rgb in s.palette for c in rgb])
        put(pix / f"source_{g}_{i}.png", _png_bytes(src.convert("RGBA")))
        # quadro convertido como a ROM tem hoje: corte da celula da sheet (linha de efeitos atual)
        sheet_idx, frame = spr.locate[(g, i)][0]
        sh = spr.sheets[sheet_idx]
        img = next(x for x in sh.images if x.frame == frame)
        cell = sh.png.crop((frame * sh.cell_w, 0, frame * sh.cell_w + sh.cell_w, sh.cell_h))
        # a paleta embutida na sheet PNG nao e a CRAM: aplica as palavras que a ROM carrega na linha
        line = spr.fx_palette if sh.palette == "fx" else spr.body_variants[0][1]
        cell.putpalette([c for w in line for c in vdp_rgb(w)] + [0] * (768 - 48))
        put(pix / f"current_md_{g}_{i}.png", _png_bytes(cell))
        sprites_out.append({"sprite": [g, i], "size": [s.width, s.height], "axis": [s.axis_x, s.axis_y],
                            "sheet": sh.name, "sheet_palette": sh.palette, "cell": [sh.cell_w, sh.cell_h],
                            "cell_axis": [sh.axis_x, sh.axis_y], "tiles_8x8_nonempty": _tiles(cell),
                            "hw_sprites": img.hw_sprites, "dma_bytes_if_uploaded": _tiles(cell) * 32})

    # paleta alvo: variante 0 do corpo apos a fusao; papeis por slot
    words = spr.body_variants[0][1]
    free = set(spr.report.get("free_body_slots", []))
    clothing = {k + 1 for k in spr.report.get("clothing_slots", [])}
    roles = []
    for sl in range(16):
        role = ("transparent" if sl == 0 else "fx_dedicated" if sl in free else
                "clothing_forbidden_for_fx" if sl in clothing else "stable_usable_by_fx")
        roles.append({"slot": sl, "role": role, "vdp_word": f"0x{words[sl]:03X}" if sl not in free else None,
                      "rgb": list(vdp_rgb(words[sl])) if sl not in free else None})
    put(pix / "palette_target_swatch.png", _png_bytes(_swatch(words, [])))
    put(pix / "palette_current_fx_swatch.png", _png_bytes(_swatch(spr.fx_palette, [])))

    # catalogo inteiro: uso de cada cor de efeito por familia (o slot de FX e unico para todas)
    fam = collections.defaultdict(collections.Counter)
    for sh in spr.sheets:
        if sh.palette == "fx" and sh.png is not None:
            for idx, n in collections.Counter(sh.png.get_flattened_data()).items():
                if idx:
                    fam[sh.name][f"0x{spr.fx_palette[idx]:03X}"] += n
    catalog = {k: dict(v.most_common()) for k, v in sorted(fam.items())}

    contract = {"family": name, "actions": actions, "frames": frames, "sprites": sprites_out,
                "rules": ["preservar trajetoria, ponto de origem (eixo), limites de quadro e tempos do AIR",
                          "os quadros vazios (-1) sao parte do desenho (piscar): manter",
                          "nao mudar Clsn, corpo, escala nem hitbox"]}
    palette = {"line": "linha do lutador (PAL1/PAL2)", "budget": "8 estaveis + 6 de roupa + 1 de efeito",
               "stable_usable_by_fx": sorted(r["slot"] for r in roles if r["role"] == "stable_usable_by_fx"),
               "clothing_forbidden_for_fx": sorted(clothing), "fx_dedicated": sorted(free),
               "fx_slot_rule": "o slot de efeito e UM so para todas as familias do personagem: escolher a cor "
                               "olhando o catalogo inteiro (fx_catalog.json), nao so este piloto",
               "slots": roles}
    budget = {"per_sprite": [{k: s[k] for k in ("sprite", "tiles_8x8_nonempty", "hw_sprites", "dma_bytes_if_uploaded")}
                             for s in sprites_out],
              "max_tiles_frame": max(s["tiles_8x8_nonempty"] for s in sprites_out),
              "note": "o candidato nao pode passar do maior quadro atual nem de 16 sprites de hardware por quadro"}
    for fname, obj in (("frame_contract.json", contract), ("palette_roles.json", palette),
                       ("budget_report.json", budget), ("fx_catalog.json", catalog)):
        put(doc / fname, (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode())
    (doc / "source_hashes.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    return {"frames": len(frames), "sprites": len(sprites_out), "pixels_dir": str(pix.relative_to(project)),
            "doc_dir": str(doc.relative_to(project)), "fx_slot": sorted(free)}
