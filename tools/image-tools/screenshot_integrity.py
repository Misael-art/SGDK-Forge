#!/usr/bin/env python3
"""
Integridade de screenshot de evidencia de emulador.

Detecta telas brancas/solidas/vazias em screenshots de BlastEm para que o
pipeline de evidencia nunca declare claims positivos (gameplay_basico,
boot_emulador, etc.) sobre um quadro sem conteudo visivel.

A motivacao e estrutural: a telemetria MDRT prova que a ROM rodou o loop de
CPU, mas nao prova que o VDP desenhou pixels. Um screenshot em branco
dissociado de metricas plausiveis (ex.: Blue Circuit) e a falha de
integridade que esta ferramenta fecha.

Discriminador principal: densidade de bordas (edge_density). Arte real -
mesmo pixel art indexada de 16 cores - tem estrutura espacial
(transicoes entre cores vizinhas). Uma tela branca/solida, por definicao,
nao tem bordas. Contagem de cores unicas NAO serve como discriminador
aqui porque pixel art de Mega Drive e indexada de proposito em poucas
cores; foi o erro da primeira versao.

Medidas:
  - edge_density: fracao de celulas amostradas com vizinho horizontal ou
    vertical cuja diferenca de cor soma > EDGE_THRESHOLD. Sinal primario.
  - dominant_color_fraction: fracao da cor mais frequente. Sinal
    secundario (tela solida = ~1.0).
  - variance: variancia da luminancia. Sinal secundario (solida = ~0).
  - unique_colors: informativo, nao discriminador.

Uso:
  python screenshot_integrity.py --path <screenshot.png> [--json]
  python screenshot_integrity.py --path <screenshot.png> --strict --json

Saida JSON:
  {
    "parse_ok": true,
    "is_blank_or_solid": true,
    "edge_density": 0.011,
    "dominant_color_fraction": 0.902,
    "dominant_color": [255, 255, 255],
    "variance": 2070.2,
    "unique_colors": 210,
    "width": 656,
    "height": 519,
    "reason": "edge_density_below_threshold"
  }

Thresholds (conservadores, calibrados em assets reais do workspace):
  EDGE_DENSITY_THRESHOLD = 0.04   (branco=0.011, bg=0.26, sprite=0.36)
  DOMINANT_FRACTION_THRESHOLD = 0.985
  VARIANCE_THRESHOLD = 1.0

A flag --strict aperta edge_density para 0.08 em gates criticos.

Requisito: pip install Pillow
"""

import argparse
import json
import sys

EDGE_COLOR_THRESHOLD = 48  # soma |dr|+|dg|+|db| que define uma borda
EDGE_DENSITY_THRESHOLD = 0.04
DOMINANT_FRACTION_THRESHOLD = 0.985
VARIANCE_THRESHOLD = 1.0

STRICT_EDGE_DENSITY_THRESHOLD = 0.08
STRICT_DOMINANT_FRACTION_THRESHOLD = 0.97
STRICT_VARIANCE_THRESHOLD = 5.0


def analyze(path, strict=False):
    """Analisa um screenshot e retorna um dict de integridade."""
    try:
        from PIL import Image
    except ImportError:
        print("Erro: Pillow nao instalado. Execute: pip install Pillow", file=sys.stderr)
        return {"parse_ok": False, "error": "Pillow nao instalado"}

    try:
        img = Image.open(path)
        img.load()
    except Exception as exc:
        return {"parse_ok": False, "error": "nao_e_png_ou_ilegivel: %s" % str(exc)}

    w, h = img.size
    if w <= 0 or h <= 0 or w * h == 0:
        return {
            "parse_ok": True,
            "is_blank_or_solid": True,
            "edge_density": 0.0,
            "dominant_color_fraction": 1.0,
            "dominant_color": None,
            "variance": 0.0,
            "unique_colors": 0,
            "width": w,
            "height": h,
            "reason": "dimensao_nula",
        }

    rgb = img.convert("RGB")
    px = rgb.load()

    # Amostragem deterministica em grade para imagens grandes: cobre a imagem
    # inteira sem explodir memoria em capturas de janela do SO. step=1 ate
    # ~200k pixels, depois subamostra em grade.
    total = w * h
    step = 1
    if total > 200000:
        step = 2

    counts = {}
    lum_sum = 0.0
    lum_sq_sum = 0.0
    sample_count = 0

    for y in range(0, h, step):
        for x in range(0, w, step):
            r, g, b = px[x, y][:3]
            counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            lum_sum += lum
            lum_sq_sum += lum * lum
            sample_count += 1

    if sample_count == 0:
        return {
            "parse_ok": True,
            "is_blank_or_solid": True,
            "edge_density": 0.0,
            "dominant_color_fraction": 1.0,
            "dominant_color": None,
            "variance": 0.0,
            "unique_colors": 0,
            "width": w,
            "height": h,
            "reason": "amostra_vazia",
        }

    # Densidade de bordas: compara pixel com vizinho direito e inferior na
    # grade amostrada. Bordas = pares com diferenca de cor > limiar.
    edges = 0
    edge_pairs = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            r1, g1, b1 = px[x, y][:3]
            if x + step < w:
                r2, g2, b2 = px[x + step, y][:3]
                if abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2) > EDGE_COLOR_THRESHOLD:
                    edges += 1
                edge_pairs += 1
            if y + step < h:
                r2, g2, b2 = px[x, y + step][:3]
                if abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2) > EDGE_COLOR_THRESHOLD:
                    edges += 1
                edge_pairs += 1

    edge_density = edges / max(1, edge_pairs)

    lum_mean = lum_sum / sample_count
    variance = max(0.0, (lum_sq_sum / sample_count) - (lum_mean * lum_mean))

    dom_color, dom_count = max(counts.items(), key=lambda kv: kv[1])
    dom_fraction = dom_count / sample_count
    unique_colors = len(counts)

    if strict:
        e_thr = STRICT_EDGE_DENSITY_THRESHOLD
        d_thr = STRICT_DOMINANT_FRACTION_THRESHOLD
        v_thr = STRICT_VARIANCE_THRESHOLD
    else:
        e_thr = EDGE_DENSITY_THRESHOLD
        d_thr = DOMINANT_FRACTION_THRESHOLD
        v_thr = VARIANCE_THRESHOLD

    # Dois sinais independentes (OR), cada um cobrindo uma falha distinta:
    #
    # 1. edge_density baixo: a area de renderizacao nao tem estrutura
    #    espacial. Este e o sinal primario e discrimina sozinho: arte real
    #    tem ~0.26+, telas vazias/brancas ~0.01. NAO combinar com variancia
    #    em AND, porque screenshots de janela do SO (ex.: BlastEm) incluem o
    #    title bar escuro, que eleva a variancia global mesmo quando a area
    #    de renderizacao e branca.
    # 2. variancia quase nula + fracao dominante ~1.0: tela solida de uma
    #    unica cor (edge_density tambem seria 0 aqui, mas este ramo torna
    #    explicito o caso de cor unica).
    reason = None
    if edge_density < e_thr:
        reason = "edge_density_below_threshold"
    elif variance < v_thr and dom_fraction > d_thr:
        reason = "solid_single_color"

    is_blank = reason is not None

    return {
        "parse_ok": True,
        "is_blank_or_solid": is_blank,
        "edge_density": round(edge_density, 6),
        "dominant_color_fraction": round(dom_fraction, 6),
        "dominant_color": list(dom_color),
        "variance": round(variance, 6),
        "unique_colors": unique_colors,
        "width": w,
        "height": h,
        "reason": reason,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detecta screenshots brancos/solidos/vazios de evidencia de emulador."
    )
    parser.add_argument("--path", required=True, help="Caminho do screenshot (PNG).")
    parser.add_argument("--json", action="store_true", help="Emite saida em JSON.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Limites mais apertados para capturas de gate critico.",
    )
    args = parser.parse_args()

    result = analyze(args.path, strict=args.strict)

    if args.json:
        print(json.dumps(result))
    else:
        if not result.get("parse_ok"):
            print("ERRO: %s" % result.get("error", "desconhecido"))
        else:
            status = "BLANK/SOLIDO" if result["is_blank_or_solid"] else "CONTEUDO"
            print("Screenshot: %s" % args.path)
            print("Status: %s" % status)
            print("edge_density: %s" % result["edge_density"])
            print("dominant_color_fraction: %s" % result["dominant_color_fraction"])
            print("variance: %s" % result["variance"])
            print("unique_colors: %s" % result["unique_colors"])
            print("dims: %sx%s" % (result["width"], result["height"]))
            if result.get("reason"):
                print("reason: %s" % result["reason"])

    # Exit code: 0 conteudo, 1 blank/solido, 2 erro de parse.
    if not result.get("parse_ok"):
        sys.exit(2)
    sys.exit(1 if result.get("is_blank_or_solid") else 0)


if __name__ == "__main__":
    main()
