#!/usr/bin/env python3
"""Mede contraste de luma entre tinta e fundo. Fecha a metade mecanica da secao 36.

Adjetivo de direcao sem piso numerico vira defeito reproduzivel. "Leve, sem
chanfro" para o PRESENTS produziu 99% da tinta num indice de luma 38 contra fundo
de luma 46 — contraste de -8, texto mais escuro que o fundo. O artista entregou a
discricao que foi pedida; o brief e que confundiu dois eixos. "Discreto" e sobre
tamanho e peso, nunca sobre contraste.

O fundo e composto camada a camada (indice 0 e transparente), porque a tinta nao
se apoia num PNG isolado: ela se apoia no que sobrou depois de BG_B, BG_A e o que
mais estiver sob ela na regiao exata onde o elemento e carimbado.

Piso padrao: 34 de luma. Nao e numero escolhido a gosto — os componentes de cor do
Mega Drive andam de 34 em 34 (0,34,68,...,238), entao 34 e exatamente UM degrau de
cinza da rampa do hardware. Contraste abaixo de um degrau nao existe no console.

Limite declarado: isto mede LUMA, nao legibilidade. Tinta e fundo podem ter luma
distante e ainda brigarem por matiz, e um elemento pode passar aqui e continuar
ilegivel por serifa fina ou por ruido do fundo. A secao 36 continua exigindo
captura.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_VERSION = "1.0.0"

MD_COMPONENT_STEP = 34
DEFAULT_FLOOR = MD_COMPONENT_STEP
# Massa de tinta perdida que reprova o elemento. O piso de 34 e fato de hardware;
# esta fracao e convencao declarada — acima de um terco, o elemento esta sendo lido
# por menos de dois tercos de si mesmo.
INK_MASS_FAIL_SHARE = 1.0 / 3.0
# Massa minima com contraste POSITIVO acima do piso, para intencao de realce.
HIGHLIGHT_MASS_MIN = 0.20
BRIGHT_INTENTS = ("leve", "claro", "light", "bright", "destaque", "realce")
TRANSPARENT_INDEX = 0


def luma(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.299 * r + 0.587 * g + 0.114 * b


def load_indexed(path: Path):
    from PIL import Image
    im = Image.open(path)
    if im.mode != "P":
        raise ValueError(f"{path.name}: modo {im.mode}, esperado P (indexado)")
    pal = im.getpalette() or []
    table = {i: (pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2])
             for i in range(len(pal) // 3)}
    return im, table


def composite_background(layers: list[Path], region: tuple[int, int, int, int]) -> list[float]:
    """Compoe as camadas de tras para frente na regiao e devolve a luma por pixel.

    Indice 0 e transparente: a camada de cima so cobre onde tem tinta. Pixel que
    fica descoberto em todas as camadas nao entra na media — medir o vazio como
    se fosse preto inventaria contraste que a tela nao mostra.
    """
    x, y, w, h = region
    out: list[float | None] = [None] * (w * h)
    for path in layers:
        im, table = load_indexed(path)
        px = im.load()
        for j in range(h):
            for i in range(w):
                sx, sy = x + i, y + j
                if sx >= im.width or sy >= im.height:
                    continue
                idx = px[sx, sy]
                if idx == TRANSPARENT_INDEX:
                    continue
                out[j * w + i] = luma(table[idx])
    return [v for v in out if v is not None]


def measure_pair(pair: dict[str, Any], root: Path, floor: int) -> dict[str, Any]:
    element = root / pair["element"]
    region = tuple(pair["region"])
    layers = [root / p for p in pair.get("background_layers", [])]

    entry: dict[str, Any] = {
        "element": pair["element"],
        "region": list(region),
        "intent": pair.get("intent", ""),
        "floor": floor,
    }

    missing = [p.as_posix() for p in [element, *layers] if not p.is_file()]
    if missing:
        entry.update(finding="asset_missing", detail=missing[:3])
        return entry

    try:
        im, table = load_indexed(element)
        bg_samples = composite_background(layers, region)
    except (ValueError, OSError) as exc:
        entry.update(finding="asset_unreadable", detail=str(exc))
        return entry

    if not bg_samples:
        entry.update(finding="background_fully_transparent",
                     detail="nenhuma camada cobre a regiao; nao ha fundo contra o que medir")
        return entry

    bg_luma = sum(bg_samples) / len(bg_samples)
    entry["background_luma"] = round(bg_luma, 1)
    entry["background_coverage"] = round(len(bg_samples) / (region[2] * region[3]), 3)

    counts: dict[int, int] = {}
    px = im.load()
    for j in range(im.height):
        for i in range(im.width):
            idx = px[i, j]
            if idx != TRANSPARENT_INDEX:
                counts[idx] = counts.get(idx, 0) + 1
    ink_total = sum(counts.values())
    if not ink_total:
        entry.update(finding="element_has_no_ink")
        return entry

    below = 0
    positive = 0
    breakdown = []
    for idx, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        li = luma(table[idx])
        contrast = li - bg_luma
        if abs(contrast) < floor:
            below += n
        elif contrast > 0:
            positive += n
        breakdown.append({"index": idx, "luma": round(li, 1),
                          "contrast": round(contrast, 1),
                          "share": round(n / ink_total, 3)})
    entry["ink_pixels"] = ink_total
    entry["ink_luma_mean"] = round(
        sum(luma(table[i]) * n for i, n in counts.items()) / ink_total, 1)
    entry["ink_contrast_mean"] = round(entry["ink_luma_mean"] - bg_luma, 1)
    entry["ink_below_floor_share"] = round(below / ink_total, 3)
    entry["highlight_mass_share"] = round(positive / ink_total, 3)
    entry["by_index"] = breakdown[:6]

    # A media de luma da tinta NAO decide nada. Texto com contorno preto sobre
    # preenchimento claro tem media baixa e le otimo: o contorno e recurso de
    # legibilidade, nao defeito. O que decide e massa — quanta tinta desaparece
    # contra o fundo, e quanta sobra puxando para cima.
    if below / ink_total > INK_MASS_FAIL_SHARE:
        entry["finding"] = "luma_contrast_below_floor"
    elif (pair.get("intent", "").lower() in BRIGHT_INTENTS
          and positive / ink_total < HIGHLIGHT_MASS_MIN):
        entry["finding"] = "no_readable_highlight_mass"
    return entry


def audit(root: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for path in sorted(root.rglob("doc/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        found: list[dict[str, Any]] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                if isinstance(node.get("luma_floor"), dict):
                    found.append(node["luma_floor"])
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(data)
        base = path.parent.parent
        for block in found:
            floor = int(block.get("floor", DEFAULT_FLOOR))
            for pair in block.get("pairs", []):
                entry = measure_pair(pair, base, int(pair.get("floor", floor)))
                entry["declared_in"] = path.relative_to(root).as_posix()
                results.append(entry)

    blocking = sorted({r["finding"] for r in results if r.get("finding")})
    return {
        "schema_version": "1.0.0",
        "tool": "audit_luma_floor",
        "tool_version": TOOL_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule_ref": "SGDK_GLOBAL.md secao 36",
        "default_floor": DEFAULT_FLOOR,
        "ink_mass_fail_share": round(INK_MASS_FAIL_SHARE, 3),
        "highlight_mass_min": HIGHLIGHT_MASS_MIN,
        "floor_rationale": "Um degrau de componente do Mega Drive vale 34. Contraste abaixo "
                           "de um degrau nao existe no hardware.",
        "limitation": "O piso de 34 e fato de hardware; a fracao de massa que reprova e "
                      "convencao declarada e sobrescrevivel por par. Mede luma, nao legibilidade. Tinta e fundo podem ter luma distante e "
                      "brigar por matiz; serifa fina ou fundo ruidoso continuam ilegiveis com "
                      "contraste alto. A secao 36 continua exigindo captura.",
        "pairs_measured": len(results),
        "results": results,
        "blocking": bool(blocking),
        "blocking_statuses": blocking,
    }


def _fixture(tmp: Path, name: str, size, colors, painter) -> Path:
    from PIL import Image
    im = Image.new("P", size, 0)
    flat = []
    for c in colors:
        flat.extend(c)
    im.putpalette(flat + [0, 0, 0] * (256 - len(colors)))
    painter(im.load(), *size)
    path = tmp / name
    im.save(path)
    return path


def self_check() -> int:
    """Reproduz o PRESENTS de contraste -8 e uma versao com contraste real."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "doc").mkdir()

        # fundo chapado em luma 68 (indice 1 = cinza 68)
        _fixture(tmp, "bg.png", (32, 32), [(255, 0, 255), (68, 68, 68)],
                 lambda px, w, h: [px.__setitem__((i, j), 1)
                                   for j in range(h) for i in range(w)])
        # tinta em luma 68 tambem: contraste 0, abaixo do degrau do hardware
        _fixture(tmp, "timido.png", (16, 16), [(255, 0, 255), (68, 68, 68)],
                 lambda px, w, h: [px.__setitem__((i, j), 1)
                                   for j in range(h) for i in range(w)])
        # tinta em luma 238: contraste +170, sete degraus
        _fixture(tmp, "legivel.png", (16, 16), [(255, 0, 255), (238, 238, 238)],
                 lambda px, w, h: [px.__setitem__((i, j), 1)
                                   for j in range(h) for i in range(w)])
        # tinta em luma 34 com intencao "leve": mais escura que o fundo
        _fixture(tmp, "invertido.png", (16, 16), [(255, 0, 255), (34, 34, 34)],
                 lambda px, w, h: [px.__setitem__((i, j), 1)
                                   for j in range(h) for i in range(w)])

        # texto claro com contorno preto: media de luma baixa, legibilidade alta.
        # Foi este caso que reprovou na primeira versao desta ferramenta, por usar
        # media em vez de massa. Ele precisa PASSAR.
        def paint_outlined(px, w, h):
            for j in range(h):
                for i in range(w):
                    px[i, j] = 1 if (i < 3 or i >= w - 3 or j < 3 or j >= h - 3) else 2
        _fixture(tmp, "contorno.png", (16, 16),
                 [(255, 0, 255), (0, 0, 0), (238, 238, 238)], paint_outlined)

        def run(name: str, intent: str = "") -> dict[str, Any]:
            return measure_pair({"element": name, "region": [0, 0, 16, 16],
                                 "background_layers": ["bg.png"], "intent": intent},
                                tmp, DEFAULT_FLOOR)

        contorno = run("contorno.png", intent="destaque")
        timido = run("timido.png")
        legivel = run("legivel.png")
        invertido = run("invertido.png", intent="leve")

        if timido.get("finding") != "luma_contrast_below_floor":
            print(f"self-check failed: tinta sem contraste passou ({timido.get('finding')})",
                  file=sys.stderr)
            return 1
        if timido["ink_below_floor_share"] != 1.0:
            print("self-check failed: massa de tinta sob o piso deveria ser 100%", file=sys.stderr)
            return 1
        if contorno.get("finding"):
            print(f"self-check failed: texto com contorno preto reprovado por "
                  f"{contorno['finding']} — media de luma nao pode decidir", file=sys.stderr)
            return 1
        if contorno["ink_below_floor_share"] != 0.0:
            print("self-check failed: contorno e preenchimento estao ambos acima do piso",
                  file=sys.stderr)
            return 1
        if legivel.get("finding"):
            print(f"self-check failed: tinta legivel reprovada por {legivel['finding']}",
                  file=sys.stderr)
            return 1
        if legivel["ink_contrast_mean"] <= DEFAULT_FLOOR:
            print("self-check failed: contraste de +170 nao foi medido", file=sys.stderr)
            return 1
        if invertido.get("finding") != "no_readable_highlight_mass":
            print(f"self-check failed: tinta sem massa de realce sob intencao 'leve' passou "
                  f"({invertido.get('finding')})", file=sys.stderr)
            return 1

        # fundo totalmente transparente nao pode virar contraste inventado
        vazio = measure_pair({"element": "legivel.png", "region": [0, 0, 16, 16],
                              "background_layers": ["timido.png"]}, tmp, DEFAULT_FLOOR)
        _ = vazio  # timido.png tem tinta; cobertura total, entao nao e o caso vazio
        nada = measure_pair({"element": "legivel.png", "region": [0, 0, 16, 16],
                             "background_layers": []}, tmp, DEFAULT_FLOOR)
        if nada.get("finding") != "background_fully_transparent":
            print("self-check failed: fundo ausente deveria recusar a medicao", file=sys.stderr)
            return 1

    print("audit_luma_floor self-check passed (contraste 0 reprova, +170 passa, "
          "contorno preto passa, sem massa de realce reprova, fundo vazio recusa)")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--output", default="")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return self_check()

    root = Path(args.root).expanduser().resolve()
    report = audit(root)

    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        if not report["pairs_measured"]:
            print("[luma-floor] nenhum bloco luma_floor declarado. Sem par elemento/fundo "
                  "nao ha o que medir: a secao 36 fica em prosa.")
        for r in report["results"]:
            mark = "FALHA" if r.get("finding") else "OK  "
            head = f"  [{mark}] {Path(r['element']).name:34}"
            if r.get("finding") in ("asset_missing", "asset_unreadable",
                                    "background_fully_transparent"):
                print(f"{head} {r['finding']}: {r.get('detail')}")
                continue
            print(f"{head} fundo {r['background_luma']:6.1f}  "
                  f"perdida {r['ink_below_floor_share']:5.0%}  "
                  f"realce {r['highlight_mass_share']:5.0%}  {r.get('finding','')}")
        print(f"\n[luma-floor] piso {report['default_floor']} "
              f"({report['floor_rationale']})")
        print(f"[luma-floor] verdict={'BLOCKED' if report['blocking'] else 'OK'}"
              f"  {report['blocking_statuses'] or ''}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
