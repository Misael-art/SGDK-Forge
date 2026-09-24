"""Gera definicoes vazias (host) para os simbolos declarados em arquivos .res do rescomp.

Le o .res (fonte de verdade) em vez do .h gerado pelo rescomp, que so e atualizado no build da ROM.
Uso: stub_res.py <saida.c> <saida.h> arquivo.res...
"""
import re
import sys

out_c, out_h, *res = sys.argv[1:]
syms = []
for path in res:
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\s*(SPRITE|WAV|IMAGE|TILESET)\s+(\w+)\s", line)
        if m:
            # SPRITE: maxNumTile = celula w*h (teto do rescomp), para o host exercitar a reserva de VRAM
            cell = re.match(r'\s*SPRITE\s+\w+\s+"[^"]*"\s+(\d+)\s+(\d+)', line)
            syms.append((*m.groups(), int(cell.group(1)) * int(cell.group(2)) if cell else 0))
with open(out_h, "w") as h, open(out_c, "w") as c:
    h.write('#include "genesis.h"\n')
    c.write('#include "genesis.h"\n')
    for kind, name, tiles in syms:
        if kind == "IMAGE":
            h.write(f"extern const Image {name};\n")
            c.write(f"static TileSet {name}_ts = {{ 0, 272, 0 }};\nconst Image {name} = {{ 0, &{name}_ts, 0 }};\n")
        elif kind == "TILESET":
            h.write(f"extern const TileSet {name};\n")
            c.write(f"const TileSet {name} = {{ 0, 16, 0 }};\n")
        elif kind == "SPRITE":
            h.write(f"extern const SpriteDefinition {name};\n")
            c.write(f"const SpriteDefinition {name} = {{ 0, {tiles} }};\n")
        else:
            h.write(f"extern const u8 {name}[64];\n")
            c.write(f"const u8 {name}[64];\n")
