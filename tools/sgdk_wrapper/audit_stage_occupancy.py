#!/usr/bin/env python3
"""Mede ocupacao de faixa da tela por quadro. Fecha a metade mecanica da secao 35.

Nenhum outro validador deste workspace olha para ONDE as coisas estao na tela. O
ato 3 do branding do modelo tinha 0 sprites, 865 de 1740 tiles e over_budget 0 —
todos os gates verdes — com quatro wordmarks empilhados na mesma faixa y=80..128
no quadro 451. A cena estava ilegivel e nenhum numero acusou.

Esta ferramenta le a planta baixa declarada (zonas com capacidade, elementos com
faixa e janela de quadros), varre quadro a quadro e reporta o pior. Ela tambem
compara a faixa declarada contra as constantes do runtime, porque declaracao
envelhece: quando esta varredura foi escrita, o `vertical_rhythm` do storyboard
ainda dizia baseline y=128 com author_tile [8,12], enquanto o codigo ja estava em
[8,3] — a declaracao descrevia uma cena que nao existia mais.

Limite declarado: isto mede SOBREPOSICAO DE FAIXA, que e a metade geometrica da
composicao. Ele nao le hierarquia, peso, direcao de leitura nem ritmo. Cena com
ocupacao 1 pode continuar mal composta; a secao 35 continua exigindo captura.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOL_VERSION = "1.0.0"

BAND_RE = re.compile(r"y\s*(\d+)\s*\.\.\s*(\d+)")
DEFINE_RE = re.compile(r"^#define\s+(\w+)\s+(\d+)", re.M)


def parse_band(value: Any) -> tuple[int, int] | None:
    """Aceita [y0, y1] ou a prosa 'y 56..144' usada em screen_zones."""
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return int(value[0]), int(value[1])
    match = BAND_RE.search(str(value))
    return (int(match.group(1)), int(match.group(2))) if match else None


def overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def runtime_defines(path: Path) -> dict[str, int]:
    try:
        return {m.group(1): int(m.group(2)) for m in DEFINE_RE.finditer(
            path.read_text(encoding="utf-8", errors="replace"))}
    except OSError:
        return {}


def check_runtime_band(elem: dict[str, Any], root: Path) -> dict[str, Any] | None:
    """Compara a faixa declarada com a que sai das constantes do runtime."""
    ref = elem.get("runtime_ref")
    if not ref:
        return None
    src = root / ref.get("file", "")
    defs = runtime_defines(src)
    if not defs:
        return {"element": elem["id"], "issue": "runtime_source_unreadable",
                "detail": ref.get("file", "")}
    try:
        y0 = defs[ref["tile_y"]] * 8
        y1 = y0 + defs[ref["tile_h"]] * 8
    except KeyError as exc:
        return {"element": elem["id"], "issue": "runtime_define_missing",
                "detail": str(exc)}
    declared = parse_band(elem.get("band"))
    if declared != (y0, y1):
        return {"element": elem["id"], "issue": "declared_band_diverges_from_runtime",
                "declared": list(declared) if declared else None,
                "runtime": [y0, y1],
                "detail": f"{ref['tile_y']}*8 .. +{ref['tile_h']}*8"}
    return None


def audit_block(block: dict[str, Any], root: Path, source: str) -> dict[str, Any]:
    zones = [{"id": z["id"], "band": parse_band(z.get("band")),
              "max_concurrent": int(z.get("max_concurrent", 1))}
             for z in block.get("zones", [])]
    elements = block.get("elements", [])

    divergences = [d for d in (check_runtime_band(e, root) for e in elements) if d]
    no_exit = [e["id"] for e in elements if not str(e.get("exit", "")).strip()]

    spans = []
    for e in elements:
        band = parse_band(e.get("band"))
        frames = e.get("frames") or [0, 0]
        if band:
            spans.append((e["id"], int(frames[0]), int(frames[1]), band))

    findings: list[dict[str, Any]] = []
    for zone in zones:
        if not zone["band"]:
            continue
        worst_frame, worst_set = None, []
        frame_lo = min((s[1] for s in spans), default=0)
        frame_hi = max((s[2] for s in spans), default=0)
        for f in range(frame_lo, frame_hi + 1):
            live = [s[0] for s in spans
                    if s[1] <= f < s[2] and overlaps(s[3], zone["band"])]
            if len(live) > len(worst_set):
                worst_set, worst_frame = live, f
        entry = {
            "zone": zone["id"],
            "band": list(zone["band"]),
            "max_concurrent": zone["max_concurrent"],
            "worst_frame": worst_frame,
            "worst_occupancy": len(worst_set),
            "elements_at_worst_frame": worst_set,
        }
        if len(worst_set) > zone["max_concurrent"]:
            entry["finding"] = "stage_zone_over_capacity"
        findings.append(entry)

    blocking = sorted({f["finding"] for f in findings if f.get("finding")})
    if divergences:
        blocking.append("declared_band_diverges_from_runtime")
    if no_exit:
        blocking.append("element_without_declared_exit")

    return {
        "source": source,
        "zones": findings,
        "band_divergences": divergences,
        "elements_without_exit": no_exit,
        "blocking_statuses": sorted(set(blocking)),
    }


def audit(root: Path) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    for path in sorted(root.rglob("doc/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        found: list[tuple[str, dict[str, Any]]] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                if "stage_occupancy" in node and isinstance(node["stage_occupancy"], dict):
                    found.append((path.relative_to(root).as_posix(), node["stage_occupancy"]))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(data)
        for source, block in found:
            blocks.append(audit_block(block, root, source))

    blocking = sorted({b for blk in blocks for b in blk["blocking_statuses"]})
    return {
        "schema_version": "1.0.0",
        "tool": "audit_stage_occupancy",
        "tool_version": TOOL_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule_ref": "SGDK_GLOBAL.md secao 35",
        "limitation": "Mede sobreposicao de faixa, que e a metade geometrica da composicao. "
                      "Nao le hierarquia, peso, direcao de leitura nem ritmo. Ocupacao 1 nao "
                      "significa cena bem composta; a secao 35 continua exigindo captura.",
        "declarations_found": len(blocks),
        "blocks": blocks,
        "blocking": bool(blocking),
        "blocking_statuses": blocking,
    }


def self_check() -> int:
    """Reproduz o defeito historico do ato 3 e o estado corrigido."""
    defeito = {
        "zones": [{"id": "palco", "band": "y 56..144", "max_concurrent": 1}],
        "elements": [
            {"id": "bigorna", "frames": [0, 520], "band": [80, 128], "exit": "hold"},
            {"id": "FORGE", "frames": [203, 520], "band": [80, 128], "exit": "nenhuma"},
            {"id": "MISAEL", "frames": [330, 520], "band": [96, 128], "exit": "nenhuma"},
            {"id": "MASTER", "frames": [440, 520], "band": [80, 128], "exit": "nenhuma"},
        ],
    }
    corrigido = {
        "zones": [{"id": "palco", "band": "y 56..144", "max_concurrent": 1}],
        "elements": [
            {"id": "FORGE", "frames": [203, 330], "band": [80, 128], "exit": "varredura F318-330"},
            {"id": "MISAEL", "frames": [330, 440], "band": [80, 128], "exit": "varredura F428-440"},
            {"id": "MASTER", "frames": [440, 520], "band": [80, 128], "exit": "fade na entrega"},
        ],
    }
    root = Path(".")
    bad = audit_block(defeito, root, "fixture")
    good = audit_block(corrigido, root, "fixture")

    if "stage_zone_over_capacity" not in bad["blocking_statuses"]:
        print("self-check failed: empilhamento de 4 elementos nao detectado", file=sys.stderr)
        return 1
    if bad["zones"][0]["worst_occupancy"] != 4:
        print(f"self-check failed: ocupacao {bad['zones'][0]['worst_occupancy']}, esperado 4",
              file=sys.stderr)
        return 1
    if not (440 <= bad["zones"][0]["worst_frame"] < 520):
        print(f"self-check failed: pior quadro {bad['zones'][0]['worst_frame']} fora de 440..520",
              file=sys.stderr)
        return 1
    if good["blocking_statuses"]:
        print(f"self-check failed: cena corrigida reprovada por {good['blocking_statuses']}",
              file=sys.stderr)
        return 1
    if good["zones"][0]["worst_occupancy"] != 1:
        print("self-check failed: sucessao corrigida deveria medir ocupacao 1", file=sys.stderr)
        return 1

    # faixa declarada divergindo do runtime
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        (r / "src").mkdir()
        (r / "src" / "s.c").write_text("#define A_Y 3\n#define A_H 4\n", encoding="utf-8")
        drift = audit_block({
            "zones": [{"id": "z", "band": [0, 224], "max_concurrent": 9}],
            "elements": [{"id": "A", "frames": [0, 10], "band": [96, 128], "exit": "fade",
                          "runtime_ref": {"file": "src/s.c", "tile_y": "A_Y", "tile_h": "A_H"}}],
        }, r, "fixture")
        if "declared_band_diverges_from_runtime" not in drift["blocking_statuses"]:
            print("self-check failed: divergencia declaracao/runtime nao detectada", file=sys.stderr)
            return 1
        if drift["band_divergences"][0]["runtime"] != [24, 56]:
            print("self-check failed: faixa derivada do runtime incorreta", file=sys.stderr)
            return 1

    # elemento sem saida declarada
    if "element_without_declared_exit" not in audit_block({
            "zones": [], "elements": [{"id": "X", "frames": [0, 1], "band": [0, 8]}]},
            root, "fixture")["blocking_statuses"]:
        print("self-check failed: elemento sem saida nao detectado", file=sys.stderr)
        return 1

    print("audit_stage_occupancy self-check passed "
          "(empilhamento 4x, sucessao limpa, deriva de runtime, saida ausente)")
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
        if not report["declarations_found"]:
            print("[stage-occupancy] nenhum bloco stage_occupancy declarado. "
                  "Sem planta baixa nao ha o que medir: a secao 35 fica em prosa.")
        for blk in report["blocks"]:
            print(f"  {blk['source']}")
            for z in blk["zones"]:
                mark = "FALHA" if z.get("finding") else "OK  "
                print(f"    [{mark}] zona {z['zone']:12} y{z['band'][0]}..{z['band'][1]:<4} "
                      f"pico {z['worst_occupancy']}/{z['max_concurrent']} no quadro "
                      f"{z['worst_frame']}  {z['elements_at_worst_frame']}")
            for d in blk["band_divergences"]:
                print(f"    [FALHA] {d['element']}: {d['issue']} "
                      f"declarado={d.get('declared')} runtime={d.get('runtime')}")
            for e in blk["elements_without_exit"]:
                print(f"    [FALHA] {e}: sem saida declarada")
        print(f"\n[stage-occupancy] verdict={'BLOCKED' if report['blocking'] else 'OK'}"
              f"  {report['blocking_statuses'] or ''}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
