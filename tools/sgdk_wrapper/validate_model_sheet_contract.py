#!/usr/bin/env python3
"""Validate a branding_v2 model sheet against its contract-specific constraints.

Deliberately does NOT re-check what art_diagnostic.py already covers (indexed
mode, <=15 visible colours, 9-bit grid, index 0 transparency, multiple-of-8
dimensions). Run that first. This gate checks only what is specific to the
`branding_sequence_v2` model sheet, and it exists so the acceptance criteria are
measurable BEFORE the art agent starts rather than argued about afterwards.

Six checks:

  1. canvas is exactly 512x384
  2. the five panel regions each carry content
  3. panel B is silhouette-only (transparent plus one dark ink)
  4. PAL1[13..14] keep highlight headroom  <- without this the act 2 specular
     sweep cannot exist, because the VDP highlight operator has nowhere to
     brighten into
  5. PAL0[9..12] close as a cycle          <- the runtime rotates these four in
     CRAM; if the last step does not meet the first, a visible jump appears
  6. panel E carries real 16x16 detail rather than upscaled blocks

Palette layout read from the PNG: entries 0-15 = PAL0, 16-31 = PAL1,
32-47 = PAL2, 48-63 = PAL3, as fixed by doc/branding_v2_art_direction.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("[model-sheet] ERROR: Pillow nao disponivel")
    sys.exit(2)

CANVAS = (512, 384)

# (id, x0, y0, x1, y1) conforme a secao 9 da direcao de arte
PANELS = [
    ("A", 0, 0, 256, 160),
    ("B", 256, 0, 512, 160),
    ("C", 0, 160, 512, 224),
    ("D", 0, 224, 256, 320),
    ("E", 256, 224, 512, 320),
]

PAL_GROUPS = {"PAL0": 0, "PAL1": 16, "PAL2": 32, "PAL3": 48}

MD_MAX = 0xEE           # canal maximo do CRAM de 9 bits
HEADROOM_CEILING = 0xCC  # folga de highlight: nenhum canal pode passar disto
HEADROOM_INDICES = (13, 14)
# Acima desta fracao de pixels no teto, a varredura especular morre no corpo do metal.
# Abaixo dela e glint: fica marcado, nao reprova.
SPECULAR_BODY_SHARE = 0.15
EMBER_INDICES = (9, 10, 11, 12)
# Uniformidade do ciclo: os 4 passos, INCLUINDO o de fechamento, precisam ser
# comparaveis. Comparar o fechamento contra o maior passo interno era furado —
# uma rampa com um salto interno gigante fazia qualquer fechamento passar.
CYCLE_UNIFORMITY = 3.0
UPSCALE_BLOCK = 4       # se todo bloco NxN for uniforme, o conteudo foi ampliado


def palette_rgb(img: Image.Image) -> list[tuple[int, int, int]]:
    raw = img.getpalette() or []
    return [tuple(raw[i : i + 3]) for i in range(0, len(raw), 3)]  # type: ignore[misc]


def region_indices(img: Image.Image, box: tuple[int, int, int, int]) -> list[int]:
    return list(img.crop(box).getdata())


def dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def audit(path: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    def add(code: str, severity: str, subject: str, message: str) -> None:
        findings.append(
            {"code": code, "severity": severity, "subject": subject, "message": message}
        )

    img = Image.open(path)

    if img.mode != "P":
        add(
            "model_sheet_not_indexed",
            "blocking",
            "mode",
            f"PNG precisa ser indexado (modo P), veio {img.mode}. Rode art_diagnostic.py primeiro.",
        )
        return finish(path, img, findings, {})

    if img.size != CANVAS:
        add(
            "model_sheet_canvas_mismatch",
            "blocking",
            "canvas",
            f"canvas precisa ser {CANVAS[0]}x{CANVAS[1]}, veio {img.size[0]}x{img.size[1]}. "
            "As regioes dos 5 paineis sao posicionais e nao podem ser conferidas em outro tamanho.",
        )
        return finish(path, img, findings, {})

    pal = palette_rgb(img)
    panel_stats: dict[str, Any] = {}

    # 2. cada painel carrega conteudo
    for pid, x0, y0, x1, y1 in PANELS:
        data = region_indices(img, (x0, y0, x1, y1))
        used = sorted(set(data))
        non_transparent = [i for i in used if i % 16 != 0]
        panel_stats[pid] = {"indices_used": len(used), "non_transparent": len(non_transparent)}
        if not non_transparent:
            add(
                "model_sheet_panel_empty",
                "blocking",
                f"painel {pid}",
                "regiao vazia: o painel precisa provar a decisao que lhe cabe",
            )

    # 3. painel B e silhueta
    b_data = region_indices(img, (256, 0, 512, 160))
    b_ink = sorted({i for i in b_data if i % 16 != 0})
    panel_stats["B"]["ink_indices"] = b_ink
    if len(b_ink) > 2:
        add(
            "model_sheet_panel_b_not_silhouette",
            "blocking",
            "painel B",
            f"painel de silhueta usa {len(b_ink)} indices de tinta; esperado 1 (no maximo 2). "
            "Silhueta e preto puro sobre transparente: se ha shading, ela nao esta provando "
            "os silhouette_hooks.",
        )

    # 4. folga de highlight em PAL1
    base = PAL_GROUPS["PAL1"]
    headroom: dict[str, Any] = {}
    for idx in HEADROOM_INDICES:
        slot = base + idx
        if slot >= len(pal):
            add(
                "model_sheet_palette_group_missing",
                "blocking",
                f"PAL1[{idx}]",
                f"paleta do PNG tem {len(pal)} entradas e nao alcanca a entrada {slot}. "
                "Ordene a paleta como PAL0=0-15, PAL1=16-31, PAL2=32-47, PAL3=48-63.",
            )
            continue
        rgb = pal[slot]
        peak = max(rgb)
        headroom[f"PAL1[{idx}]"] = {"rgb": list(rgb), "peak_channel": peak}
        if peak > HEADROOM_CEILING:
            add(
                "model_sheet_highlight_headroom_violated",
                "blocking",
                f"PAL1[{idx}]",
                f"canal maximo {peak:#04x} passa de {HEADROOM_CEILING:#04x}. Sem folga, o operador "
                "de Shadow/Highlight do VDP nao tem para onde clarear e a varredura especular do "
                "ato 2 desaparece.",
            )

    # 4b. folga de highlight nas cores REALMENTE pintadas
    #
    # Conferir so os slots declarados 13-14 media a declaracao, nao a realidade: o
    # wordmark pode nunca pintar esses slots e mesmo assim encostar no teto por outro
    # indice. O operador de highlight do VDP clareia a cor de saida do pixel, entao o
    # que decide e a cor que o pixel tem, nao o slot que o contrato reservou.
    d_box = (0, 224, 256, 320)
    d_used = sorted({i for i in region_indices(img, d_box) if base <= i <= base + 15})
    capped = [(i - base, pal[i]) for i in d_used if i < len(pal) and max(pal[i]) > HEADROOM_CEILING]
    if d_used:
        total_d = len([i for i in region_indices(img, d_box) if base <= i <= base + 15])
        capped_px = len(
            [i for i in region_indices(img, d_box) if i in {base + n for n, _ in capped}]
        )
        share = capped_px / total_d if total_d else 0.0
        evidence_headroom_used = {
            "used_indices": [i - base for i in d_used],
            "peak_channel_used": max((max(pal[i]) for i in d_used if i < len(pal)), default=0),
            "capped_indices": [n for n, _ in capped],
            "capped_pixel_share": round(share, 3),
        }
        headroom["used_colors"] = evidence_headroom_used
        if capped:
            names = ", ".join(f"PAL1[{n}]={tuple(c)}" for n, c in capped)
            # Proporcionalidade: um glint no teto e escolha legitima de artista e a
            # varredura ainda le no resto da letra. O que mata o efeito e o CORPO no
            # teto. Reprovar 1% seria gate gritando em asset saudavel.
            severity = "blocking" if share >= SPECULAR_BODY_SHARE else "warning"
            consequence = (
                "o corpo do metal esta no teto e a varredura especular do ato 2 morre"
                if severity == "blocking"
                else "e um glint, nao o corpo: a varredura ainda le no resto da letra, mas "
                     "esses pixels ficam mortos sob o highlight"
            )
            add(
                "model_sheet_specular_headroom_unusable",
                severity,
                "painel D",
                f"{share:.0%} dos pixels de metal pintam cor com canal acima de "
                f"{HEADROOM_CEILING:#04x} ({names}); limite de corpo {SPECULAR_BODY_SHARE:.0%}. "
                f"O operador de highlight clareia a cor de saida do pixel, entao {consequence}. "
                "A folga precisa estar na cor pintada, nao apenas nos slots reservados.",
            )

    # 5. ciclo de brasa em PAL0
    base0 = PAL_GROUPS["PAL0"]
    cycle_info: dict[str, Any] = {}
    slots = [base0 + i for i in EMBER_INDICES]
    if max(slots) < len(pal):
        colors = [pal[s] for s in slots]
        # Os 4 passos do anel, com o wrap 12->9 no mesmo pe de igualdade.
        ring = [dist(colors[i], colors[(i + 1) % len(colors)]) for i in range(len(colors))]
        widest, tightest = max(ring), min(ring)
        uniformity = (widest / tightest) if tightest > 0 else float("inf")
        cycle_info = {
            "colors": [list(c) for c in colors],
            "ring_steps": [round(s, 1) for s in ring],
            "closing_step": round(ring[-1], 1),
            "uniformity_ratio": None if tightest == 0 else round(uniformity, 2),
            "limit": CYCLE_UNIFORMITY,
        }
        if tightest == 0:
            add(
                "model_sheet_ember_cycle_not_closed",
                "blocking",
                "PAL0[9..12]",
                "dois indices do ciclo tem a mesma cor: um passo morto no anel faz a brasa "
                "travar em vez de correr.",
            )
        elif uniformity > CYCLE_UNIFORMITY:
            add(
                "model_sheet_ember_cycle_not_closed",
                "blocking",
                "PAL0[9..12]",
                f"anel desigual: maior passo {widest:.0f} contra menor {tightest:.0f} "
                f"(razao {uniformity:.1f}, limite {CYCLE_UNIFORMITY}). O runtime rotaciona estes "
                "4 indices em CRAM; passos desiguais aparecem como tranco na brasa, e um "
                "fechamento largo aparece como salto.",
            )
    else:
        add(
            "model_sheet_palette_group_missing",
            "blocking",
            "PAL0[9..12]",
            f"paleta do PNG tem {len(pal)} entradas e nao alcanca o ciclo de brasa",
        )

    # 6. painel E em escala real
    e_box = (256, 224, 512, 320)
    e_img = img.crop(e_box)
    w, h = e_img.size
    px = e_img.load()
    blocks = uniform = 0
    for by in range(0, h - UPSCALE_BLOCK + 1, UPSCALE_BLOCK):
        for bx in range(0, w - UPSCALE_BLOCK + 1, UPSCALE_BLOCK):
            vals = {
                px[bx + dx, by + dy]
                for dy in range(UPSCALE_BLOCK)
                for dx in range(UPSCALE_BLOCK)
            }
            if len(vals) == 1 and next(iter(vals)) % 16 != 0:
                uniform += 1
            if len(vals) > 1 or next(iter(vals)) % 16 != 0:
                blocks += 1
    ratio = (uniform / blocks) if blocks else 0.0
    panel_stats["E"]["uniform_block_ratio"] = round(ratio, 3)
    if blocks and ratio > 0.9:
        add(
            "model_sheet_panel_e_upscaled_only",
            "blocking",
            "painel E",
            f"{ratio:.0%} dos blocos {UPSCALE_BLOCK}x{UPSCALE_BLOCK} com conteudo sao uniformes: "
            "o painel parece ampliacao, nao arte a 16x16 real. Brasa e estilhaco precisam aparecer "
            "em tamanho real; a ampliacao e permitida ao lado, marcada como ampliacao.",
        )

    return finish(
        path,
        img,
        findings,
        {"panels": panel_stats, "highlight_headroom": headroom, "ember_cycle": cycle_info},
    )


def finish(
    path: Path, img: Image.Image, findings: list[dict[str, Any]], evidence: dict[str, Any]
) -> dict[str, Any]:
    blocking = sorted({f["code"] for f in findings if f["severity"] == "blocking"})
    return {
        "schema_version": "1.0.0",
        "gate": "model_sheet_contract",
        "contract_ref": "doc/branding_sequence_contract.json#branding_sequence_v2",
        "direction_ref": "doc/branding_v2_art_direction.md",
        "model_sheet_path": path.as_posix(),
        "canvas": list(img.size),
        "mode": img.mode,
        "palette_entries": len(palette_rgb(img)) if img.mode == "P" else 0,
        "evidence": evidence,
        "findings": findings,
        "complements": "art_diagnostic.py cobre formato tecnico geral; art_quality_gate.py cobre "
                       "qualidade artistica. Este gate cobre so o contrato do model sheet v2.",
        "human_judgement_still_required": "Nenhum destes checks julga se a luz esta correta. "
                                         "Direcao de luz coerente na rampa e aprovacao humana.",
        "blocking": bool(blocking),
        "blocking_statuses": blocking,
    }


def self_check() -> int:
    """Folha conforme passa; folha violando dispara os blockers esperados."""
    import tempfile

    def build(path, headroom_ok, cycle_ok, panel_e_real):
        pal = [0] * (64 * 3)
        def setc(slot, rgb):
            pal[slot * 3:slot * 3 + 3] = list(rgb)
        for g in (0, 16, 32, 48):
            setc(g, (255, 0, 255))
        for i in range(1, 16):
            v = 0x22 * (i // 2)
            setc(i, (v, v // 2, 0)); setc(16 + i, (v, v, v))
            setc(32 + i, (v // 2, v // 2, v)); setc(48 + i, (v, 0, v // 2))
        cyc = ([(0x88, 0x44, 0), (0xAA, 0x44, 0), (0xAA, 0x66, 0), (0x88, 0x66, 0)]
               if cycle_ok else
               [(0x22, 0, 0), (0x44, 0x22, 0), (0x66, 0x44, 0), (0xEE, 0xCC, 0xAA)])
        for n, c in zip(EMBER_INDICES, cyc):
            setc(n, c)
        hr = ([(0xAA, 0xAA, 0xCC), (0xCC, 0xCC, 0xCC)] if headroom_ok
              else [(0xEE, 0xEE, 0xEE), (0xEE, 0xEE, 0xEE)])
        for n, c in zip(HEADROOM_INDICES, hr):
            setc(16 + n, c)
        im = Image.new("P", CANVAS, 0); im.putpalette(pal); px = im.load()
        def detail(x0, y0, x1, y1, a, b):
            for y in range(y0, y1):
                for x in range(x0, x1):
                    px[x, y] = a if (x + y) % 2 else b
        detail(8, 8, 248, 152, 5, 6)
        for y in range(8, 152):
            for x in range(264, 504):
                px[x, y] = 15
        detail(8, 168, 504, 216, 17, 18)
        detail(8, 232, 248, 312, 33, 34)
        if panel_e_real:
            detail(264, 232, 504, 312, 49, 50)
        else:
            for by in range(232, 312, 4):
                for bx in range(264, 504, 4):
                    for y in range(by, by + 4):
                        for x in range(bx, bx + 4):
                            px[x, y] = 49
        im.save(path)

    with tempfile.TemporaryDirectory() as td:
        ok_p, bad_p = Path(td) / "ok.png", Path(td) / "bad.png"
        build(ok_p, True, True, True)
        build(bad_p, False, False, False)
        ok, bad = audit(ok_p), audit(bad_p)

    if ok["blocking"]:
        print(f"self-check failed: folha conforme reprovada {ok['blocking_statuses']}", file=sys.stderr)
        return 1
    for code in ("model_sheet_highlight_headroom_violated",
                 "model_sheet_ember_cycle_not_closed",
                 "model_sheet_panel_e_upscaled_only"):
        if code not in bad["blocking_statuses"]:
            print(f"self-check failed: {code} nao detectado", file=sys.stderr)
            return 1
    print("validate_model_sheet_contract self-check passed (passa e reprova headroom, ciclo e escala)")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-sheet", default="")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--output", default="")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return self_check()
    if not args.model_sheet:
        print("[model-sheet] ERROR: passe --model-sheet ou --self-check"); return 2
    path = Path(args.model_sheet).expanduser().resolve()
    if not path.is_file():
        print(f"[model-sheet] ERROR: arquivo nao encontrado: {path}")
        return 2

    report = audit(path)

    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        print(f"[model-sheet] {path.name} {report['canvas']} modo={report['mode']} "
              f"paleta={report['palette_entries']}")
        for f in report["findings"]:
            print(f"[{f['severity'].upper()}] {f['code']} :: {f['subject']} :: {f['message']}")
        verdict = "BLOCKED" if report["blocking"] else "OK"
        print(f"[model-sheet] verdict={verdict} blocking={report['blocking_statuses']}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
