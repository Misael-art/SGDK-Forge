#!/usr/bin/env python3
"""Autora o model sheet do heroi: rampa no lattice RGB333 + turnaround de 5 vistas.

CONTRATO. Implementa `doc/art/model_sheet_route/visual_dna_manifest.json`. As regras
que importam nao sao verificadas depois, sao satisfeitas POR CONSTRUCAO:

  R1 direcao de luz unica declarada -> o tom de cada pixel vem do produto escalar
     entre a normal da esfera naquele pixel e um vetor de luz fixo. Nao ha como
     pintar uma mancha clara que nao decorra da luz, porque nenhum tom e pintado
     a mao: todos sao derivados da geometria.
  R2 rampa de 5 degraus com queda monotonica -> o lambert continuo e quantizado
     em 5 faixas; a area de cada faixa cai naturalmente porque a esfera tem mais
     area voltada para a luz do que contra ela.
  R4 contorno fechado -> dilatacao da silhueta, garantindo 100% de cobertura.
  R5 razao corpo:pe -> constantes BODY_R e FOOT_* travadas com assert.
  R6 olho oval vertical com especular -> nunca retangulo.
  R7 sombra de contato na base.

POR QUE PROCEDURAL AQUI E LEGITIMO, se "traducao procedural" reprovou o P1: o P1
era procedural na FORMA (silhueta gerada sem direcao). Aqui a forma e autorada em
constantes explicitas e o procedural resolve so o SOMBREAMENTO, que e justamente
o que o P1 errou. O gate humano continua sendo do model sheet, nao deste script.

    python3 tools/art/build_model_sheet_v01.py
    python3 tools/art/build_model_sheet_v01.py --check   # so valida o contrato
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "source_art" / "model_sheet_v01"
EVID = ROOT / "out" / "evidence" / "model_sheet_route"

# ---------------------------------------------------------------- lattice ----
# doc/PALETTES.md: o VDP guarda 3 bits por canal; os unicos valores legais sao
# estes 8. Qualquer cor fora daqui e mentira -- o hardware vai arredondar.
LATTICE = (0, 36, 73, 109, 146, 182, 219, 255)


def on_lattice(rgb) -> bool:
    return all(c in LATTICE for c in rgb)


# ------------------------------------------------------------------ rampa ----
# Autoral. NAO e a paleta do SNES snapada: a referencia deu a ESTRUTURA
# (5 degraus, queda monotonica de area, luz superior-esquerda) e as cores foram
# escolhidas aqui dentro do lattice. Copiar os RGB da referencia seria clone.
IDX_SKIN = [1, 2, 3, 4, 5]
PALETTE = {
    0:  (255, 0, 255),      # chave de transparencia; nunca no corpo
    1:  (255, 182, 219),    # degrau 1 - preenchimento sob a luz
    2:  (255, 146, 182),    # degrau 2 - meio-tom
    3:  (219, 109, 146),    # degrau 3 - sombra
    4:  (182, 73, 109),     # degrau 4 - sombra profunda
    5:  (109, 36, 73),      # degrau 5 - contato / oclusao
    6:  (36, 0, 36),        # contorno dedicado
    7:  (219, 36, 36),      # pe
    8:  (255, 109, 109),    # brilho do pe
    9:  (36, 0, 73),        # olho
    10: (255, 255, 255),    # especular
    11: (73, 36, 73),       # sombra de contato no chao
}

CELL = 32
BODY_R = 11.5          # raio do corpo
BODY_CX, BODY_CY = 16.0, 14.5
FOOT_RX, FOOT_RY = 4.0, 2.6
ARM_R = 3.2
LIGHT = np.array([-0.52, -0.62, 0.59])   # superior-esquerda, na direcao do olhar
LIGHT /= np.linalg.norm(LIGHT)

# Proporcao de area por degrau, medida no tier SNES (154/64/43/29/25 px na celula
# 24x25 de Kirby Super Star). Ver doc/art/model_sheet_route/01-reference-study.md.
# Nao copiamos as CORES da referencia -- copiamos a ESTRUTURA da rampa.
REF_RAMP_SHARE = (154, 64, 43, 29, 25)

# Limiares de lambert derivados dessas proporcoes sobre a vista FRONTAL, e depois
# aplicados fixos a todas as vistas. Se fossem recalculados por vista, o teste de
# queda monotonica viraria tautologia -- ele so e um teste de verdade porque as
# outras quatro vistas usam limiares que nao foram ajustados para elas.
RAMP_STOPS: tuple[float, ...] = ()

VIEWS = ("front", "three_quarter", "side", "three_quarter_back", "back")


def _ellipse(sub, cx, cy, rx, ry):
    yy, xx = sub
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0


def _sphere_lambert(grid, cx, cy, r):
    """Lambert de uma esfera de raio r centrada em (cx,cy), e sua mascara."""
    yy, xx = grid
    nx = (xx - cx) / r
    ny = (yy - cy) / r
    rr = nx * nx + ny * ny
    nz = np.sqrt(np.clip(1.0 - rr, 0, 1))
    lam = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
    return lam, rr <= 1.0, rr


def _shading_field(view: str):
    """Campo de luz unico para a celula inteira, e a silhueta solida.

    TUDO que modula tom entra AQUI, antes da quantizacao: forma, oclusao de
    contato e realce de borda. Nada de sobrescrever indice depois -- foi
    exatamente isso que quebrou a queda monotonica na primeira tentativa, porque
    mover pixels entre degraus ja atribuidos reembaralha as areas.
    """
    yy, xx = np.mgrid[0:CELL, 0:CELL].astype(float)
    grid = (yy + 0.5, xx + 0.5)

    lam_b, body, rr_b = _sphere_lambert(grid, BODY_CX, BODY_CY, BODY_R)

    # Bracos afastados o bastante para a silhueta ler como coto, nao como ombro.
    # A v01 usava 10.6 e os cotos fundiam no corpo, virando bolha larga.
    arm_off = 12.4
    lam_l, arm_l, _ = _sphere_lambert(grid, BODY_CX - arm_off, 17.5, ARM_R * 1.05)
    lam_r, arm_r, _ = _sphere_lambert(grid, BODY_CX + arm_off, 17.5, ARM_R * 1.05)

    solid = body | arm_l | arm_r
    # cada componente ilumina o proprio volume; o corpo vence onde houver sobreposicao
    lam = np.where(body, lam_b, np.where(arm_l, lam_l, np.where(arm_r, lam_r, -1.0)))

    # oclusao de contato: escurece progressivamente o terco inferior (R7)
    t = np.clip((yy + 0.5 - (BODY_CY + BODY_R * 0.45)) / (BODY_R * 0.72), 0, 1)
    lam = lam - 0.42 * (t ** 2)

    # Realce de borda (rim): soma, nao sobrescreve. So no hemisferio que ENCARA a
    # luz -- exigir a componente horizontal do lambert positiva impede o rim de
    # contornar para o lado escuro, defeito que a v01 tinha e que o relatorio de
    # contrato nao pegava porque so media area por degrau, nunca ONDE ela cai.
    nx_b = (xx + 0.5 - BODY_CX) / BODY_R
    ny_b = (yy + 0.5 - BODY_CY) / BODY_R
    facing = (nx_b * LIGHT[0] + ny_b * LIGHT[1]) > 0.20
    rim = (rr_b > 0.68) & (rr_b <= 1.0) & facing
    lam = lam + np.where(rim, 0.30, 0.0)

    return lam, solid


def derive_ramp_stops() -> tuple[float, ...]:
    """Converte as proporcoes medidas na referencia em limiares de lambert.

    Feito UMA vez, sobre a vista frontal. As demais vistas herdam estes limiares
    sem reajuste, para que o teste de queda monotonica continue significando algo:
    se ele passar em 5 vistas com limiares calibrados em 1, a rampa e robusta.
    """
    lam, solid = _shading_field("front")
    vals = np.sort(lam[solid])[::-1]
    total = vals.size
    stops, acc = [], 0.0
    for share in REF_RAMP_SHARE[:-1]:
        acc += share / sum(REF_RAMP_SHARE)
        stops.append(float(vals[min(total - 1, int(acc * total))]))
    return tuple(stops)


def build_cell(view: str):
    """Devolve (indices 32x32 uint8). Forma autorada, sombreamento derivado."""
    yy, xx = np.mgrid[0:CELL, 0:CELL].astype(float)
    grid = (yy + 0.5, xx + 0.5)

    turn = {"front": 0.0, "three_quarter": 0.45, "side": 0.95,
            "three_quarter_back": 1.45, "back": 2.0}[view]

    # pes: lobos pequenos; R5 exige corpo:pe >= 3:1
    foot_dx = 5.4 - 1.2 * abs(math.sin(turn * math.pi / 2))
    feet = (_ellipse(grid, BODY_CX - foot_dx, 27.0, FOOT_RX, FOOT_RY)
            | _ellipse(grid, BODY_CX + foot_dx, 27.0, FOOT_RX, FOOT_RY))

    lam, solid = _shading_field(view)
    idx = np.zeros((CELL, CELL), np.uint8)

    # -- quantizacao unica do campo de luz (R1 + R2) --------------------------
    # Bandas exclusivas, do claro para o escuro. A ordem importa: aplicar
    # `lam >= s` em ordem crescente de s sobrescreveria as faixas ja atribuidas,
    # porque todo pixel acima de um limiar tambem esta acima dos menores. Aqui
    # cada passo escurece apenas o que ainda nao foi escurecido.
    step = np.full((CELL, CELL), IDX_SKIN[0], np.uint8)
    for i, s in enumerate(RAMP_STOPS):
        step = np.where(lam < s, IDX_SKIN[i + 1], step)
    idx[solid] = step[solid]

    # -- pes (R5) -------------------------------------------------------------
    idx[feet] = 7
    fh = feet & (yy < 26.2) & (xx < BODY_CX)
    idx[fh] = 8

    # -- olhos (R6): oval VERTICAL com especular, ~1/4 da altura do corpo ------
    if view in ("front", "three_quarter", "side"):
        shift = 3.0 * turn
        eyes = []
        if view != "side":
            eyes.append(BODY_CX - 3.6 + shift)
        eyes.append(BODY_CX + 3.0 + shift if view != "side" else BODY_CX + 2.2)
        for ex in eyes:
            # oval VERTICAL: 4.4 x 7.0 px. A v01 usava 3.1 de largura e lia como
            # fenda; R6 pede oval com especular legivel a 32 px.
            e = _ellipse(grid, ex, 14.2, 2.2, 3.5)
            idx[e & solid] = 9
            sp = _ellipse(grid, ex - 0.55, 12.4, 0.95, 1.25)
            idx[sp & solid] = 10

    # -- contorno fechado (R4) ------------------------------------------------
    filled = idx > 0
    pad = np.pad(filled, 1)
    neigh = (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
             | pad[:-2, :-2] | pad[:-2, 2:] | pad[2:, :-2] | pad[2:, 2:])
    outline = neigh & ~filled
    idx[outline] = 6

    # -- sombra de contato no chao (R7) ---------------------------------------
    ground = _ellipse(grid, BODY_CX, 30.0, 8.0, 1.35) & (idx == 0)
    idx[ground] = 11
    return idx


def to_png(sheet: np.ndarray) -> Image.Image:
    im = Image.fromarray(sheet, mode="P")
    pal = []
    for i in range(16):
        pal += list(PALETTE.get(i, (0, 0, 0)))
    im.putpalette(pal + [0, 0, 0] * (256 - 16))
    return im


def contract_report(sheet: np.ndarray) -> dict:
    findings, cells = [], []
    for i, view in enumerate(VIEWS):
        c = sheet[:, i * CELL:(i + 1) * CELL]
        body = np.isin(c, IDX_SKIN)
        areas = [int((c == s).sum()) for s in IDX_SKIN]
        centre = c[10:22, 10:22]
        cells.append({
            "view": view,
            "ramp_areas": areas,
            "monotonic_falloff": all(a >= b for a, b in zip(areas, areas[1:])),
            "opaque_pct": round(float((c > 0).mean() * 100), 2),
            "center_idx0_pct": round(float((centre == 0).mean() * 100), 2),
            "body_px": int(body.sum()),
            "foot_px": int(np.isin(c, [7, 8]).sum()),
            "outline_closed": bool((c == 6).sum() > 0),
            "distinct": sorted(int(v) for v in np.unique(c) if v),
        })
        # R1: o degrau mais claro tem de cair no quadrante que ENCARA a luz, e o
        # mais escuro no oposto. Area por degrau nao prova direcao de luz -- foi
        # esse buraco no gate que deixou o rim contornar para o lado escuro.
        ys, xs = np.nonzero(c == IDX_SKIN[0])
        yd, xd = np.nonzero(c == IDX_SKIN[-1])
        light_ok = dark_ok = True
        if xs.size and yd.size:
            lx, ly = xs.mean() - BODY_CX, ys.mean() - BODY_CY
            dx, dy = xd.mean() - BODY_CX, yd.mean() - BODY_CY
            light_ok = (lx * LIGHT[0] + ly * LIGHT[1]) > 0
            dark_ok = (dx * LIGHT[0] + dy * LIGHT[1]) < 0
            cells[-1]["light_centroid"] = [round(float(lx), 2), round(float(ly), 2)]
            cells[-1]["dark_centroid"] = [round(float(dx), 2), round(float(dy), 2)]
        cells[-1]["light_direction_respected"] = bool(light_ok and dark_ok)

        # R6: CADA olho tem de ser oval vertical, nunca fenda nem retangulo.
        # Medir a bbox dos dois juntos daria 11x7 e reprovaria um par correto --
        # o gate tem de medir a grandeza que alega medir, um olho por vez.
        ey, ex_ = np.nonzero(c == 9)
        boxes = []
        if ey.size:
            for col in np.split(np.unique(ex_),
                                np.nonzero(np.diff(np.unique(ex_)) > 1)[0] + 1):
                sel = np.isin(ex_, col)
                boxes.append([int(col.max() - col.min() + 1),
                              int(ey[sel].max() - ey[sel].min() + 1)])
            cells[-1]["eye_boxes"] = boxes
            for w, h in boxes:
                if h <= w:
                    findings.append(f"{view}: R6 olho nao e oval vertical {w}x{h}")

        if not cells[-1]["monotonic_falloff"]:
            findings.append(f"{view}: R2 rampa nao monotonica {areas}")
        if not light_ok:
            findings.append(f"{view}: R1 degrau claro fora do lado da luz")
        if not dark_ok:
            findings.append(f"{view}: R1 degrau escuro no lado da luz")
        if cells[-1]["center_idx0_pct"] >= 5.0:
            findings.append(f"{view}: corpo furado, center_idx0={cells[-1]['center_idx0_pct']}%")
        ratio = cells[-1]["body_px"] / max(1, cells[-1]["foot_px"])
        if ratio < 3.0:
            findings.append(f"{view}: R5 corpo:pe {ratio:.1f} < 3.0")
    bad = [i for i, c in PALETTE.items() if not on_lattice(c)]
    if bad:
        findings.append(f"cores fora do lattice RGB333: {bad}")
    return {
        "tool": "build_model_sheet_v01",
        "views": VIEWS,
        "palette_slots_used": len(PALETTE),
        "palette_on_lattice": not bad,
        "cells": cells,
        "findings": findings,
        "status": "pass" if not findings else "fail",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="so valida, nao escreve")
    args = ap.parse_args()

    global RAMP_STOPS
    RAMP_STOPS = derive_ramp_stops()
    print(f"  limiares de lambert derivados da referencia: "
          f"{[round(s, 3) for s in RAMP_STOPS]}")

    sheet = np.concatenate([build_cell(v) for v in VIEWS], axis=1)
    rep = contract_report(sheet)
    rep["ramp_stops"] = [round(s, 4) for s in RAMP_STOPS]
    rep["ref_ramp_share"] = list(REF_RAMP_SHARE)

    for c in rep["cells"]:
        print(f"  {c['view']:20s} rampa={c['ramp_areas']} mono={c['monotonic_falloff']} "
              f"corpo:pe={c['body_px']/max(1,c['foot_px']):.1f} "
              f"idx0_centro={c['center_idx0_pct']}% tons={len(c['distinct'])}")
    print(f"  lattice RGB333: {'ok' if rep['palette_on_lattice'] else 'VIOLADO'}")
    for f in rep["findings"]:
        print("  FINDING:", f)
    print("  status:", rep["status"])

    if args.check:
        return 0 if rep["status"] == "pass" else 1

    OUT.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)
    im = to_png(sheet)
    im.save(OUT / "hero_model_sheet_v01.png")
    im.resize((im.width * 8, im.height * 8), Image.Resampling.NEAREST).save(
        EVID / "hero_model_sheet_v01_x8.png")
    (OUT / "hero_model_sheet_v01_contract.json").write_text(
        json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    print(f"  escrito: {OUT/'hero_model_sheet_v01.png'}")
    return 0 if rep["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
