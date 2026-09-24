"""REGRA 1 -- contrato de paletas da engine: cada lutador tem UMA linha de CRAM (15 cores + transparente)
para corpo E efeitos. Mede o que um personagem convertido precisa e reprova quem estoura.

Slots necessarios = estaveis do corpo (iguais em todas as variantes .act) + roupa (variam entre
variantes) + cores de efeito sem par estavel a dE76 <= limite (agrupadas entre si no mesmo limite).
Medido nos dados GERADOS (mg_<id>.c + sheets PNG do .res), que e o que vai a ROM.
"""
from __future__ import annotations

import collections
import math
import re
from pathlib import Path

from PIL import Image

LINE_SLOTS = 15

# mapa de posse estatica (REGRA 1). "emprestimo" e declarado, com janela e restauracao.
SLOT_MAP = {
    "PAL0": {"owner": "cenario (BG_A + BG_B)", "loan": "fundo de super enquanto cobre a tela; restaura em bgfx_end/KO/fim de luta"},
    "PAL1": {"owner": "lutador P1 (corpo + efeitos)", "loan": "flash de impacto por tabela de swap pre-declarada, so nesta linha"},
    "PAL2": {"owner": "lutador P2 (corpo + efeitos)", "loan": "flash de impacto por tabela de swap pre-declarada, so nesta linha"},
    "PAL3": {"owner": "HUD", "loan": None},
}


def _rgb(w: int) -> tuple[int, int, int]:
    return tuple(((w >> s) & 0xE) * 255 // 14 for s in (1, 5, 9))


def _lab(c):
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116  # noqa: E731
    r, g, b = [((v / 255 + 0.055) / 1.055) ** 2.4 if v / 255 > 0.04045 else v / 255 / 12.92 for v in c]
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    return (116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z)))


def delta_e(a, b) -> float:
    return math.dist(_lab(a), _lab(b))


def slots_needed(variants: list[list[int]], fxpal: list[int], fx_pixels: dict[int, int], limit: float = 10.0) -> dict:
    """variants: paletas de corpo (16 palavras VDP cada); fxpal: paleta de efeitos; fx_pixels: indice -> pixels."""
    stable = [i for i in range(1, 16) if len({v[i] for v in variants}) == 1]
    clothing = [i for i in range(1, 16) if i not in stable]
    body = [_rgb(variants[0][i]) for i in stable]
    orphan = [i for i in fx_pixels if not body or min(delta_e(_rgb(fxpal[i]), c) for c in body) > limit]
    reps: list[int] = []
    for i in sorted(orphan, key=lambda i: -fx_pixels[i]):
        if not any(delta_e(_rgb(fxpal[i]), _rgb(fxpal[r])) <= limit for r in reps):
            reps.append(i)
    need = len(stable) + len(clothing) + len(reps)
    return {"stable": len(stable), "clothing": len(clothing), "fx_dedicated": len(reps),
            "fx_orphan_colours": len(orphan), "delta_e_limit": limit, "needed": need,
            "line_slots": LINE_SLOTS, "fits": need <= LINE_SLOTS, "over_by": max(0, need - LINE_SLOTS)}


def _array(src: str, name: str) -> list[int]:
    b = src[src.index(name):]
    b = b[:b.index("};")]
    return [int(x, 16) for x in re.findall(r"0x([0-9A-Fa-f]{3,4})", b)]


def check_project(project: Path, char_id: str, limit: float = 10.0) -> dict:
    src = (project / "src" / "mg_gen" / f"mg_{char_id}.c").read_text(encoding="utf-8")
    flat = _array(src, "static const u16 pals[][16]")
    variants = [flat[i:i + 16] for i in range(0, len(flat), 16)]
    fxpal = _array(src, "static const u16 fxpal[]")
    res = (project / "res" / f"mgres_{char_id}.res").read_text(encoding="utf-8")
    px: collections.Counter = collections.Counter()
    for name, path in re.findall(r'SPRITE (\w+) "([^"]+)"', res):
        if name.endswith("_fx"):
            px.update(i for i in Image.open(project / "res" / path).get_flattened_data() if i)
    return {"character": char_id, "variants": len(variants), **slots_needed(variants, fxpal, dict(px), limit)}
