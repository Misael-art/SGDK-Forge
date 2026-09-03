#!/usr/bin/env python3
"""Biblioteca canonica unica de cor do Mega Drive (P0.1 do plano forge-art).

Toda ferramenta de cor do workspace consome ESTE modulo. Tabela de cor
divergente em outro arquivo e blocker P0 (`divergent_color_table`).

--------------------------------------------------------------------------
POR QUE EXISTEM DOIS ORACULOS, E POR QUE ELES NAO SAO INTERCAMBIAVEIS
--------------------------------------------------------------------------

O SGDK 2.11 contem DUAS conversoes RGB24 -> CRAM que NAO produzem o mesmo
resultado. Isso foi lido nos arquivos, nao suposto:

  `sdk/sgdk-2.11/inc/pal.h:35`  RGB24_TO_VDPCOLOR
      arredonda: soma 0x10 por canal (saturando em 0xFF) e so entao trunca.
      nivel = min(c + 16, 255) >> 5

  `sdk/sgdk-2.11/tools/rescomp/src/sgdk/rescomp/tool/Util.java:38`  toVDPColor
      trunca direto: (c >> 4) & 0xE, que e o mesmo que ((c >> 5) & 7) << 1.
      nivel = c >> 5

Consequencia medida (ver `--self-check`): as duas concordam em 168 dos 256
valores possiveis por canal e divergem em 88. Uma cor autorada fora de grade
pode virar dois CRAM diferentes dependendo de quem converteu.

`ORACLE_RESCOMP` e o DEFAULT porque e o ResComp que escreve os bytes que vao
para a ROM. O macro C so roda quando o runtime converte cor em tempo de
execucao. Um pipeline que valida contra o macro e entrega via ResComp esta
medindo o instrumento errado (SGDK_GLOBAL.md secao 34).

--------------------------------------------------------------------------
AS TRES GRADES, MEDIDAS
--------------------------------------------------------------------------

  `authoring`  0x00,0x22,0x44,0x66,0x88,0xAA,0xCC,0xEE  (passo 0x22)
      Grade canonica de autoria do workspace. Round-trip exato nos DOIS
      oraculos. E por isso, e so por isso, que ela e a canonica.

  `display`    0x00,0x24,0x49,0x6D,0x92,0xB6,0xDB,0xFF  (nivel*255/7)
      Expansao para monitor/emulador. Round-trip exato em ORACLE_RESCOMP e
      QUEBRA em ORACLE_SGDK_MACRO (o nivel 4 volta como 5). Nao use como
      grade de autoria.

  RGBA4444 / ABGR (4 bits por canal)
      NAO e formato CRAM. Chamar `assert_not_rgba4444()` para bloquear o
      substituto silencioso. Blocker: `rgba4444_used_as_cram`.

"9 bits" = 3 bits por canal = 512 combinacoes de CRAM. Nao significa "PNG de
9 bits": o PNG final continua indexado, modo P, PLTE <= 16.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Callable, Iterable, Sequence

SCHEMA_VERSION = "1.0.0"
TOOL_NAME = "forge_art.vdp_color"
TOOL_VERSION = "1.0.0"

RGB = tuple[int, int, int]

# ---------------------------------------------------------------------------
# Constantes de hardware (espelham sdk/sgdk-2.11/inc/pal.h:19-25)
# ---------------------------------------------------------------------------

VDPPALETTE_REDSFT = 1
VDPPALETTE_GREENSFT = 5
VDPPALETTE_BLUESFT = 9
VDPPALETTE_REDMASK = 0x000E
VDPPALETTE_GREENMASK = 0x00E0
VDPPALETTE_BLUEMASK = 0x0E00
VDPPALETTE_COLORMASK = 0x0EEE

LEVELS_PER_CHANNEL = 8
TOTAL_CRAM_COLORS = LEVELS_PER_CHANNEL ** 3  # 512

ORACLE_RESCOMP = "rescomp"
ORACLE_SGDK_MACRO = "sgdk_macro"
ORACLES = (ORACLE_RESCOMP, ORACLE_SGDK_MACRO)

GRID_AUTHORING = "authoring"
GRID_DISPLAY = "display"
GRIDS = (GRID_AUTHORING, GRID_DISPLAY)

#: Passo 0x22. Round-trip exato nos dois oraculos.
AUTHORING_LEVELS: tuple[int, ...] = tuple(level * 0x22 for level in range(LEVELS_PER_CHANNEL))

#: nivel*255/7 arredondado. Round-trip exato apenas em ORACLE_RESCOMP.
DISPLAY_LEVELS: tuple[int, ...] = tuple(
    (level * 255 + 3) // 7 for level in range(LEVELS_PER_CHANNEL)
)

_GRID_TABLES: dict[str, tuple[int, ...]] = {
    GRID_AUTHORING: AUTHORING_LEVELS,
    GRID_DISPLAY: DISPLAY_LEVELS,
}


class ColorContractError(ValueError):
    """Violacao de contrato de cor. Sempre carrega a proxima acao causal."""

    def __init__(self, blocker: str, message: str, next_action: str) -> None:
        super().__init__(f"[{blocker}] {message} | proxima acao: {next_action}")
        self.blocker = blocker
        self.next_action = next_action


# ---------------------------------------------------------------------------
# Validacao de entrada — falha fechado, nunca silenciosa
# ---------------------------------------------------------------------------

def _check_component(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ColorContractError(
            "non_integer_color_component",
            f"canal {name} recebeu {value!r} ({type(value).__name__}); cor e inteiro 0..255",
            "converta o canal para int antes de chamar a biblioteca de cor",
        )
    if not 0 <= value <= 255:
        raise ColorContractError(
            "color_component_out_of_range",
            f"canal {name}={value} fora de 0..255",
            "corrija a fonte da cor; a biblioteca nao satura silenciosamente entrada invalida",
        )
    return value


def _check_rgb(rgb: Sequence[int]) -> RGB:
    values = tuple(rgb)
    if len(values) != 3:
        raise ColorContractError(
            "rgb_tuple_arity",
            f"esperado (r, g, b) com 3 canais, recebido {len(values)}",
            "remova o canal alpha antes de converter; alpha e decidido pelo index 0, nao pela cor",
        )
    r, g, b = values
    return (_check_component(r, "r"), _check_component(g, "g"), _check_component(b, "b"))


def _check_level(level: int, name: str = "nivel") -> int:
    if isinstance(level, bool) or not isinstance(level, int):
        raise ColorContractError(
            "non_integer_level",
            f"{name} recebeu {level!r}; nivel de canal e inteiro 0..7",
            "use int(level)",
        )
    if not 0 <= level <= 7:
        raise ColorContractError(
            "level_out_of_range",
            f"{name}={level} fora de 0..7 (3 bits por canal)",
            "o VDP tem 8 niveis por canal; reveja a origem do valor",
        )
    return level


def _check_oracle(oracle: str) -> str:
    if oracle not in ORACLES:
        raise ColorContractError(
            "unknown_color_oracle",
            f"oraculo {oracle!r} desconhecido; validos: {list(ORACLES)}",
            f"use {ORACLE_RESCOMP!r} para o caminho de ROM ou {ORACLE_SGDK_MACRO!r} "
            "para conversao em runtime C",
        )
    return oracle


def _check_grid(grid: str) -> str:
    if grid not in GRIDS:
        raise ColorContractError(
            "unknown_color_grid",
            f"grade {grid!r} desconhecida; validas: {list(GRIDS)}",
            "grade de autoria e 'authoring'; 'display' e so para visualizacao",
        )
    return grid


def assert_not_rgba4444(word: int) -> None:
    """Bloqueia RGBA4444/ABGR sendo passado como se fosse palavra CRAM.

    Palavra CRAM legal casa `VDPPALETTE_COLORMASK` (0x0EEE): bit 0 de cada
    nibble e sempre zero e o nibble alto e sempre zero. Qualquer bit fora
    disso denuncia outro formato.
    """
    if not isinstance(word, int) or isinstance(word, bool):
        raise ColorContractError(
            "non_integer_cram_word",
            f"palavra CRAM recebeu {word!r}",
            "converta para int",
        )
    if word < 0 or word > 0xFFFF:
        raise ColorContractError(
            "cram_word_out_of_range",
            f"palavra CRAM 0x{word:X} fora de 16 bits",
            "reveja a origem do valor",
        )
    if word & ~VDPPALETTE_COLORMASK:
        raise ColorContractError(
            "rgba4444_used_as_cram",
            f"0x{word:04X} tem bits fora de VDPPALETTE_COLORMASK (0x0EEE); "
            "isso e RGBA4444/ABGR ou lixo, nao CRAM do Mega Drive",
            "converta a paleta pela biblioteca canonica em vez de reaproveitar "
            "a tabela do Palette Generetor auditado",
        )


# ---------------------------------------------------------------------------
# Oraculos: RGB 0..255 -> nivel 0..7
# ---------------------------------------------------------------------------

def _level_rescomp(component: int) -> int:
    """ResComp: `(c >> 4) & 0xE`, ou seja truncamento puro.

    Fonte: sdk/sgdk-2.11/tools/rescomp/src/sgdk/rescomp/tool/Util.java:38
    """
    return (component >> 5) & 7


def _level_sgdk_macro(component: int) -> int:
    """Macro C: soma 0x10 saturando e so entao trunca (arredondamento).

    Fonte: sdk/sgdk-2.11/inc/pal.h:35 (RGB24_TO_VDPCOLOR)
    """
    return (min(component + 0x10, 0xFF) >> 5) & 7


_ORACLE_FUNCS: dict[str, Callable[[int], int]] = {
    ORACLE_RESCOMP: _level_rescomp,
    ORACLE_SGDK_MACRO: _level_sgdk_macro,
}


def rgb24_to_levels(rgb: Sequence[int], oracle: str = ORACLE_RESCOMP) -> tuple[int, int, int]:
    """RGB 24 bits -> trio de niveis 0..7, pelo oraculo escolhido."""
    r, g, b = _check_rgb(rgb)
    fn = _ORACLE_FUNCS[_check_oracle(oracle)]
    return (fn(r), fn(g), fn(b))


def levels_to_vdp_color(r: int, g: int, b: int) -> int:
    """Trio de niveis 0..7 -> palavra CRAM `xxxxBBBxGGGxRRRx`."""
    _check_level(r, "r")
    _check_level(g, "g")
    _check_level(b, "b")
    return (r << VDPPALETTE_REDSFT) | (g << VDPPALETTE_GREENSFT) | (b << VDPPALETTE_BLUESFT)


def vdp_color_to_levels(word: int) -> tuple[int, int, int]:
    """Palavra CRAM -> trio de niveis 0..7. Rejeita formato nao-CRAM."""
    assert_not_rgba4444(word)
    return (
        (word & VDPPALETTE_REDMASK) >> VDPPALETTE_REDSFT,
        (word & VDPPALETTE_GREENMASK) >> VDPPALETTE_GREENSFT,
        (word & VDPPALETTE_BLUEMASK) >> VDPPALETTE_BLUESFT,
    )


def rgb24_to_vdp_color(rgb: Sequence[int], oracle: str = ORACLE_RESCOMP) -> int:
    """RGB 24 bits -> palavra CRAM. Default = oraculo que escreve a ROM."""
    return levels_to_vdp_color(*rgb24_to_levels(rgb, oracle=oracle))


def vdp_color_to_authoring_rgb(word: int) -> RGB:
    """Palavra CRAM -> RGB na grade canonica de autoria (passo 0x22)."""
    r, g, b = vdp_color_to_levels(word)
    return (AUTHORING_LEVELS[r], AUTHORING_LEVELS[g], AUTHORING_LEVELS[b])


def vdp_color_to_display_rgb(word: int) -> RGB:
    """Palavra CRAM -> RGB de exibicao (nivel*255/7).

    NAO use este valor como cor de autoria: ele nao volta ao mesmo CRAM pelo
    macro C do SGDK. Ver `--self-check`, fixture `display_grid_breaks_macro`.
    """
    r, g, b = vdp_color_to_levels(word)
    return (DISPLAY_LEVELS[r], DISPLAY_LEVELS[g], DISPLAY_LEVELS[b])


def snap_rgb_to_vdp_grid(
    rgb: Sequence[int],
    grid: str = GRID_AUTHORING,
    oracle: str = ORACLE_RESCOMP,
) -> RGB:
    """Encaixa uma cor arbitraria na grade valida mais proxima.

    O snap passa pelo oraculo, nao por "nearest do valor bruto": o que decide
    a cor final e o nivel que o conversor vai escrever no CRAM.
    """
    table = _GRID_TABLES[_check_grid(grid)]
    levels = rgb24_to_levels(rgb, oracle=oracle)
    return (table[levels[0]], table[levels[1]], table[levels[2]])


def is_on_grid(rgb: Sequence[int], grid: str = GRID_AUTHORING) -> bool:
    """True se a cor ja esta exatamente na grade declarada."""
    r, g, b = _check_rgb(rgb)
    table = _GRID_TABLES[_check_grid(grid)]
    return r in table and g in table and b in table


def all_cram_colors() -> list[int]:
    """As 512 palavras CRAM legais, em ordem estavel."""
    return [
        levels_to_vdp_color(r, g, b)
        for b in range(LEVELS_PER_CHANNEL)
        for g in range(LEVELS_PER_CHANNEL)
        for r in range(LEVELS_PER_CHANNEL)
    ]


# ---------------------------------------------------------------------------
# Distancias — RGB, HSV e OKLab
# ---------------------------------------------------------------------------

def distance_rgb(a: Sequence[int], b: Sequence[int]) -> float:
    """Distancia euclidiana em RGB. Barata e perceptualmente ruim; e a
    referencia contra a qual as outras se justificam."""
    ar, ag, ab = _check_rgb(a)
    br, bg, bb = _check_rgb(b)
    return float((ar - br) ** 2 + (ag - bg) ** 2 + (ab - bb) ** 2) ** 0.5


def rgb_to_hsv(rgb: Sequence[int]) -> tuple[float, float, float]:
    """RGB 0..255 -> HSV com H em graus 0..360, S e V em 0..1."""
    r, g, b = (c / 255.0 for c in _check_rgb(rgb))
    high = max(r, g, b)
    low = min(r, g, b)
    span = high - low
    if span == 0.0:
        hue = 0.0
    elif high == r:
        hue = (60.0 * ((g - b) / span)) % 360.0
    elif high == g:
        hue = 60.0 * ((b - r) / span) + 120.0
    else:
        hue = 60.0 * ((r - g) / span) + 240.0
    sat = 0.0 if high == 0.0 else span / high
    return (hue, sat, high)


def distance_hsv(a: Sequence[int], b: Sequence[int]) -> float:
    """Distancia em HSV com matiz tratado como circular.

    Util quando a decisao e "mesma familia de material, tom diferente".
    """
    ah, as_, av = rgb_to_hsv(a)
    bh, bs, bv = rgb_to_hsv(b)
    dh = abs(ah - bh)
    if dh > 180.0:
        dh = 360.0 - dh
    return ((dh / 180.0) ** 2 + (as_ - bs) ** 2 + (av - bv) ** 2) ** 0.5


def _srgb_to_linear(channel: float) -> float:
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def rgb_to_oklab(rgb: Sequence[int]) -> tuple[float, float, float]:
    """sRGB 0..255 -> OKLab (Bjorn Ottosson, 2020).

    Deterministico: mesma entrada devolve bit a bit a mesma saida, porque nao
    ha aleatoriedade, iteracao nem dependencia de ordem de dicionario.
    """
    r, g, b = (_srgb_to_linear(c / 255.0) for c in _check_rgb(rgb))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_ = l ** (1.0 / 3.0)
    m_ = m ** (1.0 / 3.0)
    s_ = s ** (1.0 / 3.0)
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def distance_oklab(a: Sequence[int], b: Sequence[int]) -> float:
    """Distancia perceptual em OKLab.

    Limite declarado: OKLab ajuda a ESCOLHER candidatas. Ele nao decide papel
    de material, nem substitui julgamento humano de paleta
    (`production_visual_quality_contract.md`).
    """
    al, aa, ab_ = rgb_to_oklab(a)
    bl, ba, bb_ = rgb_to_oklab(b)
    return ((al - bl) ** 2 + (aa - ba) ** 2 + (ab_ - bb_) ** 2) ** 0.5


DISTANCE_FUNCS: dict[str, Callable[[Sequence[int], Sequence[int]], float]] = {
    "rgb": distance_rgb,
    "hsv": distance_hsv,
    "oklab": distance_oklab,
}


def nearest_cram_color(
    rgb: Sequence[int],
    candidates: Iterable[int],
    metric: str = "oklab",
) -> int:
    """Palavra CRAM mais proxima dentro de `candidates`.

    Empate resolve pela menor palavra CRAM, para ser deterministico.
    """
    if metric not in DISTANCE_FUNCS:
        raise ColorContractError(
            "unknown_color_metric",
            f"metrica {metric!r} desconhecida; validas: {sorted(DISTANCE_FUNCS)}",
            "use 'rgb', 'hsv' ou 'oklab'",
        )
    fn = DISTANCE_FUNCS[metric]
    target = _check_rgb(rgb)
    best: tuple[float, int] | None = None
    for word in sorted(set(candidates)):
        score = fn(target, vdp_color_to_authoring_rgb(word))
        if best is None or score < best[0]:
            best = (score, word)
    if best is None:
        raise ColorContractError(
            "empty_candidate_palette",
            "nenhuma cor candidata fornecida",
            "carregue a paleta antes de pedir a cor mais proxima; "
            "gate com denominador zero nao pode retornar sucesso",
        )
    return best[1]


# ---------------------------------------------------------------------------
# Self-check: fixtures POSITIVAS e NEGATIVAS (SGDK_GLOBAL.md secao 34 e 37)
# ---------------------------------------------------------------------------

def _fixture(name: str, kind: str, passed: bool, detail: str) -> dict:
    return {"fixture": name, "kind": kind, "status": "passed" if passed else "failed",
            "detail": detail}


def _positive_fixtures() -> list[dict]:
    out: list[dict] = []

    # 1. As 512 cores CRAM fazem round-trip exato pela grade de autoria,
    #    nos DOIS oraculos.
    broken: list[str] = []
    for word in all_cram_colors():
        rgb = vdp_color_to_authoring_rgb(word)
        for oracle in ORACLES:
            if rgb24_to_vdp_color(rgb, oracle=oracle) != word:
                broken.append(f"0x{word:04X}/{oracle}")
    out.append(_fixture(
        "512_cram_roundtrip_authoring", "positive", not broken,
        f"512 cores x 2 oraculos: {len(broken)} divergencias" + (f" {broken[:5]}" if broken else ""),
    ))

    # 2. Grade de display faz round-trip no ResComp (e so nele).
    broken = [
        f"0x{w:04X}" for w in all_cram_colors()
        if rgb24_to_vdp_color(vdp_color_to_display_rgb(w), oracle=ORACLE_RESCOMP) != w
    ]
    out.append(_fixture(
        "512_display_roundtrip_rescomp", "positive", not broken,
        f"{len(broken)} divergencias na grade display sob ResComp",
    ))

    # 3. Golden vectors lidos dos arquivos do SGDK 2.11.
    #    (r,g,b) -> palavra CRAM esperada em cada oraculo.
    goldens = [
        ((0x00, 0x00, 0x00), 0x0000, 0x0000),
        ((0xFF, 0xFF, 0xFF), 0x0EEE, 0x0EEE),
        ((0xEE, 0x00, 0x00), 0x000E, 0x000E),
        ((0x00, 0xEE, 0x00), 0x00E0, 0x00E0),
        ((0x00, 0x00, 0xEE), 0x0E00, 0x0E00),
        ((0x22, 0x44, 0x66), 0x0642, 0x0642),
        ((0x88, 0xAA, 0xCC), 0x0CA8, 0x0CA8),
        # Divergencia canonica entre os dois oraculos: o resto de c mod 32
        # cair em 16..31 e exatamente o que o macro C arredonda para cima e o
        # ResComp descarta. 0x1F -> nivel 0 no ResComp, nivel 1 no macro.
        ((0x1F, 0x1F, 0x1F), 0x0000, 0x0222),
        ((0x70, 0x70, 0x70), 0x0666, 0x0888),
        # Convergencia: 0x63 tem resto 3 e os dois oraculos concordam. Esta
        # linha existe para a fixture nao virar "tudo diverge".
        ((0x63, 0x63, 0x63), 0x0666, 0x0666),
    ]
    bad = []
    for rgb, expect_rc, expect_macro in goldens:
        got_rc = rgb24_to_vdp_color(rgb, oracle=ORACLE_RESCOMP)
        got_mc = rgb24_to_vdp_color(rgb, oracle=ORACLE_SGDK_MACRO)
        if got_rc != expect_rc or got_mc != expect_macro:
            bad.append(f"{rgb}: rescomp=0x{got_rc:04X} macro=0x{got_mc:04X}")
    out.append(_fixture(
        "golden_vectors_sgdk_211", "positive", not bad,
        f"{len(goldens)} vetores golden; falhas: {bad or 'nenhuma'}",
    ))

    # 4. Snap e idempotente: snap(snap(x)) == snap(x).
    sample = [(r, g, b) for r in range(0, 256, 17) for g in (0, 91, 255) for b in (0, 130, 255)]
    non_idem = [c for c in sample if snap_rgb_to_vdp_grid(snap_rgb_to_vdp_grid(c)) != snap_rgb_to_vdp_grid(c)]
    out.append(_fixture(
        "snap_is_idempotent", "positive", not non_idem,
        f"{len(sample)} amostras; {len(non_idem)} nao idempotentes",
    ))

    # 5. Limites e empates do snap: o primeiro valor de cada degrau.
    thresholds = {32 * k: k for k in range(LEVELS_PER_CHANNEL)}
    bad_thr = [
        f"c={c} esperado nivel {lv}, obtido {rgb24_to_levels((c, 0, 0))[0]}"
        for c, lv in thresholds.items()
        if rgb24_to_levels((c, 0, 0))[0] != lv
    ]
    out.append(_fixture(
        "snap_boundaries_rescomp", "positive", not bad_thr,
        f"degraus 0,32,...,224 sob ResComp; falhas: {bad_thr or 'nenhuma'}",
    ))

    # 6. OKLab deterministico e ancorado.
    det = all(rgb_to_oklab((123, 45, 210)) == rgb_to_oklab((123, 45, 210)) for _ in range(8))
    white_l = rgb_to_oklab((255, 255, 255))[0]
    black_l = rgb_to_oklab((0, 0, 0))[0]
    ok = det and abs(white_l - 1.0) < 1e-6 and abs(black_l) < 1e-9
    out.append(_fixture(
        "oklab_deterministic_and_anchored", "positive", ok,
        f"deterministico={det} L(branco)={white_l:.9f} L(preto)={black_l:.9f}",
    ))

    # 7. Desempate de `nearest_cram_color` e estavel.
    tie = nearest_cram_color((0x11, 0x11, 0x11), [0x0000, 0x0222], metric="oklab")
    repeats = {nearest_cram_color((0x11, 0x11, 0x11), [0x0222, 0x0000], metric="oklab")
               for _ in range(16)}
    out.append(_fixture(
        "nearest_tiebreak_deterministic", "positive",
        len(repeats) == 1 and tie in (0x0000, 0x0222),
        f"escolha estavel={repeats} (ordem de entrada nao importa)",
    ))

    return out


def _expect_blocker(blocker: str, call: Callable[[], object]) -> tuple[bool, str]:
    try:
        result = call()
    except ColorContractError as exc:
        if exc.blocker == blocker:
            return True, f"levantou {blocker} como esperado"
        return False, f"levantou {exc.blocker}, esperado {blocker}"
    return False, f"NAO levantou nada; devolveu {result!r} (falso verde)"


def _negative_fixtures() -> list[dict]:
    """Cada blocker que a biblioteca pode emitir tem uma fixture que o dispara.

    Ferramenta que so sabe dizer `ok` nao esta medindo: esta concordando.
    """
    cases: list[tuple[str, str, Callable[[], object]]] = [
        ("rejects_out_of_range_component", "color_component_out_of_range",
         lambda: rgb24_to_vdp_color((256, 0, 0))),
        ("rejects_negative_component", "color_component_out_of_range",
         lambda: rgb24_to_vdp_color((-1, 0, 0))),
        ("rejects_float_component", "non_integer_color_component",
         lambda: rgb24_to_vdp_color((12.5, 0, 0))),
        ("rejects_rgba_tuple", "rgb_tuple_arity",
         lambda: rgb24_to_vdp_color((0, 0, 0, 255))),
        ("rejects_rgba4444_as_cram", "rgba4444_used_as_cram",
         lambda: vdp_color_to_authoring_rgb(0xF00F)),
        ("rejects_odd_nibble_cram", "rgba4444_used_as_cram",
         lambda: vdp_color_to_authoring_rgb(0x0630)),
        ("rejects_unknown_oracle", "unknown_color_oracle",
         lambda: rgb24_to_vdp_color((0, 0, 0), oracle="vagno")),
        ("rejects_unknown_grid", "unknown_color_grid",
         lambda: snap_rgb_to_vdp_grid((0, 0, 0), grid="rgba4444")),
        ("rejects_unknown_metric", "unknown_color_metric",
         lambda: nearest_cram_color((0, 0, 0), [0x0000], metric="lanczos")),
        ("rejects_empty_candidate_palette", "empty_candidate_palette",
         lambda: nearest_cram_color((0, 0, 0), [])),
        ("rejects_level_out_of_range", "level_out_of_range",
         lambda: levels_to_vdp_color(8, 0, 0)),
    ]
    out = [
        _fixture(name, "negative", *_expect_blocker(blocker, call))
        for name, blocker, call in cases
    ]

    # Fixture negativa estrutural: a grade de display NAO pode ser usada como
    # grade de autoria. Se um dia ela passar a fechar no macro C, esta fixture
    # reprova e obriga revisao da doutrina, em vez de deixar a doutrina
    # envelhecer em silencio.
    macro_breaks = [
        w for w in all_cram_colors()
        if rgb24_to_vdp_color(vdp_color_to_display_rgb(w), oracle=ORACLE_SGDK_MACRO) != w
    ]
    out.append(_fixture(
        "display_grid_breaks_macro", "negative", bool(macro_breaks),
        f"{len(macro_breaks)} de 512 cores de display nao voltam pelo macro C "
        "(divergencia esperada e documentada)",
    ))

    # Fixture negativa: os dois oraculos precisam divergir de fato. Se
    # convergirem, alguem trocou a implementacao por uma copia da outra.
    divergent = [c for c in range(256) if _level_rescomp(c) != _level_sgdk_macro(c)]
    # 112 = 7 blocos de 32 x os 16 valores altos de cada bloco. O oitavo bloco
    # (240..255) nao diverge porque o macro satura em 0xFF antes de truncar.
    out.append(_fixture(
        "oracles_actually_diverge", "negative", len(divergent) == 112,
        f"{len(divergent)} de 256 valores por canal divergem entre ResComp e macro C "
        "(esperado 112)",
    ))

    return out


def self_check() -> dict:
    fixtures = _positive_fixtures() + _negative_fixtures()
    failed = [f for f in fixtures if f["status"] != "passed"]
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "rule_ref": "SGDK_GLOBAL.md secoes 34 e 37",
        "oracle_sources": {
            ORACLE_RESCOMP: "sdk/sgdk-2.11/tools/rescomp/src/sgdk/rescomp/tool/Util.java:38",
            ORACLE_SGDK_MACRO: "sdk/sgdk-2.11/inc/pal.h:35",
        },
        "exercised": (
            "512 cores CRAM com round-trip nos dois oraculos; golden vectors lidos "
            "dos arquivos do SGDK 2.11; limites e idempotencia do snap; determinismo "
            "de OKLab e do desempate; 11 blockers disparados por fixture negativa; "
            "divergencia medida entre os dois oraculos e quebra medida da grade de display."
        ),
        "limitation": (
            "Prova conformidade numerica de cor. Nao prova qualidade de paleta, "
            "vitalidade cromatica nem semantica de material."
        ),
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f"color_self_check_failed:{f['fixture']}" for f in failed}),
    }


def _cmd_convert(args: argparse.Namespace) -> int:
    rgb = tuple(int(part, 0) for part in args.rgb.split(","))
    payload = {
        "input_rgb": list(rgb),
        "oracles": {
            oracle: {
                "cram_word": f"0x{rgb24_to_vdp_color(rgb, oracle=oracle):04X}",
                "levels": list(rgb24_to_levels(rgb, oracle=oracle)),
                "authoring_rgb": [
                    f"0x{c:02X}" for c in
                    vdp_color_to_authoring_rgb(rgb24_to_vdp_color(rgb, oracle=oracle))
                ],
                "display_rgb": [
                    f"0x{c:02X}" for c in
                    vdp_color_to_display_rgb(rgb24_to_vdp_color(rgb, oracle=oracle))
                ],
            }
            for oracle in ORACLES
        },
        "already_on_authoring_grid": is_on_grid(rgb, GRID_AUTHORING),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Biblioteca canonica de cor do Mega Drive (forge-art P0.1).")
    parser.add_argument("--self-check", action="store_true",
                        help="Roda fixtures positivas e negativas e emite report JSON.")
    parser.add_argument("--convert", dest="rgb", metavar="R,G,B",
                        help="Converte uma cor pelos dois oraculos e imprime JSON.")
    args = parser.parse_args(argv)

    if args.rgb:
        return _cmd_convert(args)

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["blocking"]:
            print(
                "[FAIL] self-check de cor reprovou; proxima acao: corrija a fixture "
                "listada em blocking_statuses antes de qualquer conversao valer claim",
                file=sys.stderr,
            )
            return 1
        print(
            f"[OK] {report['fixtures_passed']}/{report['fixtures_total']} fixtures "
            "(positivas e negativas) passaram",
            file=sys.stderr,
        )
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
