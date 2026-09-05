#!/usr/bin/env python3
"""Meta-gate: toda ferramenta de medicao precisa de um self-check que PASSE.

Origem: curadoria de 2026-08-17. Tres ferramentas de medicao apresentaram defeito
na mesma sessao, e as tres davam leituras plausiveis:

  - `vdp_scanline_simulator.py` media contagem de sprites e ignorava o limite de
    320 px por linha, deixando descoberta metade do orcamento por scanline;
  - `runtime_probe.c` amostrava 4 de 224 scanlines por quadro e reportou 6 onde a
    varredura media 23 — falso verde para configuracao que causaria dropout;
  - dois campos da mesma probe exportavam a constante `1` sob o nome
    `active_sprite_count`.

Duas delas produziram bug reportado que nao existia. Uma quase aprovou hardware
estourado. Nenhuma acusou defeito por conta propria.

A regra que sai disso: **antes de a leitura de uma ferramenta valer em qualquer
claim, o self-check dela precisa passar.** E o self-check precisa exercitar os
DOIS sentidos — uma fixture que passa e uma que reprova. Ferramenta que so sabe
dizer "ok" nao esta medindo nada.

Este gate nao julga a qualidade do self-check; ele garante que existe, que roda e
que passa. Ler o que o self-check afirma continua sendo trabalho humano.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ferramentas cuja SAIDA vira numero em contrato, report ou claim.
# Injetores e geradores ficam fora: eles nao produzem medicao.
MEASUREMENT_TOOLS = [
    "tools/sgdk_wrapper/audit_procedural_asset_provenance.py",
    "tools/sgdk_wrapper/audit_tile_residency.py",
    "tools/sgdk_wrapper/audit_scene_headroom.py",
    "tools/sgdk_wrapper/validate_model_sheet_contract.py",
    "tools/sgdk_wrapper/validate_brand_comprehension_gate.py",
    "tools/sgdk_wrapper/audit_stage_occupancy.py",
    "tools/sgdk_wrapper/audit_luma_floor.py",
    "tools/sgdk_wrapper/seal_fresh_evidence_bundle.py",
    "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py",
    # forge-art P0.1: a conversao de cor produz numero que vira claim de
    # conformidade, entao ela se submete a secao 34 como qualquer instrumento.
    "tools/sgdk_wrapper/forge_art/vdp_color.py",
    "tools/sgdk_wrapper/forge_art/pixel_contract.py",
    # job.py orquestra, mas emite `source_intact` e cache hit — dois claims.
    # Na duvida entre instrumento e gerador, entra na lista: a secao 34 so
    # conhece um erro caro, e e o de nao medir.
    "tools/sgdk_wrapper/forge_art/job.py",
    "tools/sgdk_wrapper/forge_art/__main__.py",
    # Revalida dimensoes, modo, PLTE, lineage, escala e gates de uma sprite;
    # o report fornecido pelo produtor nao e aceito como prova de si mesmo.
    "tools/sgdk_wrapper/validate_native_sprite_production.py",
    # Gate de animacao ligado ao artefato: celula/lineart/movimento/claim sao
    # medidos novamente, em vez de confiar em reports auto-declarados.
    "tools/sgdk_wrapper/.agent/scripts/validate_lineart_topology.py",
    "tools/sgdk_wrapper/.agent/scripts/validate_animation_strip_artifact.py",
    "tools/sgdk_wrapper/.agent/scripts/validate_motion_semantics.py",
    "tools/sgdk_wrapper/.agent/scripts/validate_animation_candidate.py",
]

TIMEOUT_SECONDS = 120

# Instrumentos que NAO sao ferramenta de medicao em Python: sao fonte em C que
# cada projeto carrega uma copia, nascida do template em `new_project.sh`.
# A canonica e a do modelo, porque e de la que o script copia.
#
# PORQUE: a deriva de copia ja era detectada para os .py da lista acima, e por
# isso as 4 copias defasadas do simulador apareceram. A probe nunca esteve no
# radar — e C, e por projeto — e quando fui olhar na mao, 10 de 11 projetos
# estavam com versao anterior ao quadro-do-pico. Deriva que nenhum gate mede so
# aparece quando alguem vai procurar.
PROJECT_SOURCE_MIRRORS = [
    "tools/sgdk_wrapper/modelo/src/system/runtime_probe.c",
    "tools/sgdk_wrapper/modelo/inc/system/runtime_probe.h",
]

# Diretorios onde copia local de ferramenta e legitima como backup morto, nao
# como instrumento em uso.
COPY_SCAN_SKIP = {"out", "rascunho", "__pycache__", ".git"}


def run_self_check(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    entry: dict[str, Any] = {"tool": rel}

    if not path.is_file():
        entry.update(status="missing", detail="arquivo nao encontrado")
        return entry

    source = path.read_text(encoding="utf-8", errors="replace")
    if "--self-check" not in source and "self_check" not in source:
        entry.update(status="no_self_check",
                     detail="ferramenta de medicao sem self-check: a leitura dela nao "
                            "pode sustentar claim")
        return entry

    try:
        proc = subprocess.run(
            [sys.executable, "-W", "ignore", str(path), "--self-check"],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS, cwd=root,
        )
    except subprocess.TimeoutExpired:
        entry.update(status="timeout", detail=f"self-check passou de {TIMEOUT_SECONDS}s")
        return entry
    except OSError as exc:
        entry.update(status="error", detail=str(exc))
        return entry

    out = (proc.stdout + proc.stderr).strip().splitlines()
    entry["exit_code"] = proc.returncode
    entry["output"] = out[-1][:160] if out else ""
    entry["status"] = "passed" if proc.returncode == 0 else "failed"
    return entry


def _normalized(path: Path) -> bytes:
    """Conteudo com fim de linha normalizado.

    Comparar byte a byte acusaria toda copia CRLF como defasada, e o GOTHAM usa
    CRLF de proposito enquanto o modelo usa LF. Fim de linha nao e deriva de
    versao: reprovar por isso e o gate que grita lobo da secao 37.
    """
    return path.read_bytes().replace(b"\r\n", b"\n")


def scan_copies(root: Path, tools: list[str], mirrors: list[str] | None = None) -> list[dict[str, Any]]:
    """Encontra copias locais defasadas das ferramentas canonicas.

    PORQUE: self-check que passa nao prova que a ferramenta esta atual. Uma copia
    da v1.0.0 do simulador passa no proprio self-check — porque ele so testa o
    que aquela versao faz — e aprova uma cena com 512 px numa linha contra um
    teto de 320. Ferramenta obsoleta com self-check verde e pior que ferramenta
    sem self-check, porque parece verificada.
    """
    import hashlib
    import re as _re

    out: list[dict[str, Any]] = []
    for kind, group in (("tool", tools), ("project_source", mirrors or [])):
        for rel in group:
            canon = root / rel
            if not canon.is_file():
                continue
            canon_hash = hashlib.sha256(_normalized(canon)).hexdigest()
            canon_text = canon.read_text(errors="replace")
            name = Path(rel).name
            for copy in sorted(root.rglob(name)):
                if copy == canon or not copy.is_file():
                    continue
                parts = {q.lower() for q in copy.relative_to(root).parts}
                entry: dict[str, Any] = {
                    "copy": copy.relative_to(root).as_posix(),
                    "canonical": rel,
                    "kind": kind,
                    "archived": bool(parts & COPY_SCAN_SKIP),
                }
                same = hashlib.sha256(_normalized(copy)).hexdigest() == canon_hash
                entry["in_sync"] = same
                if not same:
                    m = _re.search(r'TOOL_VERSION = "([\d.]+)"', copy.read_text(errors="replace"))
                    entry["local_version"] = m.group(1) if m else "unknown"
                    m2 = _re.search(r'TOOL_VERSION = "([\d.]+)"', canon_text)
                    entry["canonical_version"] = m2.group(1) if m2 else "unknown"
                out.append(entry)
    return out


def audit(root: Path, tools: list[str]) -> dict[str, Any]:
    results = [run_self_check(root, t) for t in tools]
    copies = scan_copies(root, tools, PROJECT_SOURCE_MIRRORS if tools is MEASUREMENT_TOOLS else [])
    blocking = sorted({
        f"measurement_tool_self_check_{r['status']}"
        for r in results if r["status"] != "passed"
    })
    for c in copies:
        if c["in_sync"] or c["archived"]:
            continue
        blocking.append("measurement_tool_stale_copy" if c["kind"] == "tool"
                        else "project_source_mirror_stale")
    blocking = sorted(set(blocking))
    return {
        "schema_version": "1.0.0",
        "tool": "validate_measurement_tools",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule_ref": "SGDK_GLOBAL.md secao 34",
        "tools_checked": len(results),
        "passed": len([r for r in results if r["status"] == "passed"]),
        "results": results,
        "local_copies": copies,
        "stale_copies": len([c for c in copies if not c["in_sync"] and not c["archived"]]),
        "archived_stale_copies": len([c for c in copies if not c["in_sync"] and c["archived"]]),
        "limitation": "Garante que o self-check existe, roda e passa. Nao julga se o "
                      "self-check cobre o que deveria: isso continua sendo leitura humana.",
        "blocking": bool(blocking),
        "blocking_statuses": blocking,
    }


def self_check() -> int:
    """O proprio meta-gate se submete a regra que aplica."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "t").mkdir()

        good = root / "t" / "good.py"
        good.write_text(
            "import sys\n"
            "if '--self-check' in sys.argv:\n"
            "    print('ok'); sys.exit(0)\n"
            "sys.exit(2)\n", encoding="utf-8")
        bad = root / "t" / "bad.py"
        bad.write_text(
            "import sys\n"
            "if '--self-check' in sys.argv:\n"
            "    print('quebrou'); sys.exit(1)\n"
            "sys.exit(2)\n", encoding="utf-8")
        none = root / "t" / "none.py"
        none.write_text("print('sem self-check')\n", encoding="utf-8")

        r_good = audit(root, ["t/good.py"])
        r_bad = audit(root, ["t/bad.py"])
        r_none = audit(root, ["t/none.py"])
        r_missing = audit(root, ["t/ausente.py"])

        # copia local divergente da canonica
        (root / "proj").mkdir()
        (root / "proj" / "good.py").write_text(
            "import sys\n"
            "if '--self-check' in sys.argv:\n"
            "    print('ok antigo'); sys.exit(0)\n", encoding="utf-8")
        r_stale = audit(root, ["t/good.py"])

    if r_good["blocking"]:
        print("self-check failed: ferramenta sadia reprovada", file=sys.stderr); return 1
    if "measurement_tool_self_check_failed" not in r_bad["blocking_statuses"]:
        print("self-check failed: self-check quebrado nao detectado", file=sys.stderr); return 1
    if "measurement_tool_self_check_no_self_check" not in r_none["blocking_statuses"]:
        print("self-check failed: ausencia de self-check nao detectada", file=sys.stderr); return 1
    if "measurement_tool_self_check_missing" not in r_missing["blocking_statuses"]:
        print("self-check failed: arquivo ausente nao detectado", file=sys.stderr); return 1
    if "measurement_tool_stale_copy" not in r_stale["blocking_statuses"]:
        print("self-check failed: copia local defasada nao detectada", file=sys.stderr); return 1

    # Espelho de fonte por projeto: deriva reprova, fim de linha NAO.
    import tempfile as _tf
    with _tf.TemporaryDirectory() as td2:
        r2 = Path(td2)
        (r2 / "modelo").mkdir()
        (r2 / "proj_igual").mkdir()
        (r2 / "proj_crlf").mkdir()
        (r2 / "proj_velho").mkdir()
        corpo = b"void probe(void)\n{\n    peak_frame();\n}\n"
        (r2 / "modelo" / "probe.c").write_bytes(corpo)
        (r2 / "proj_igual" / "probe.c").write_bytes(corpo)
        (r2 / "proj_crlf" / "probe.c").write_bytes(corpo.replace(b"\n", b"\r\n"))
        (r2 / "proj_velho" / "probe.c").write_bytes(b"void probe(void)\n{\n}\n")

        found = scan_copies(r2, [], ["modelo/probe.c"])
        by = {c["copy"]: c for c in found}
        if not by.get("proj_igual/probe.c", {}).get("in_sync"):
            print("self-check failed: copia identica acusada como defasada", file=sys.stderr)
            return 1
        if not by.get("proj_crlf/probe.c", {}).get("in_sync"):
            print("self-check failed: diferenca so de CRLF acusada como deriva — "
                  "isso e o gate gritando lobo", file=sys.stderr)
            return 1
        if by.get("proj_velho/probe.c", {}).get("in_sync", True):
            print("self-check failed: fonte defasada passou", file=sys.stderr)
            return 1
        if by["proj_velho/probe.c"]["kind"] != "project_source":
            print("self-check failed: espelho classificado como ferramenta", file=sys.stderr)
            return 1
    print("validate_measurement_tools self-check passed (sadia, quebrada, sem check, "
          "ausente, copia defasada, espelho de fonte defasado, CRLF nao acusa)")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--tool", action="append", default=[],
                    help="Verifica apenas estas ferramentas, em vez da lista canonica.")
    ap.add_argument("--output", default="")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return self_check()

    root = Path(args.root).expanduser().resolve()
    report = audit(root, args.tool or MEASUREMENT_TOOLS)

    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        for r in report["results"]:
            mark = "OK  " if r["status"] == "passed" else "FALHA"
            print(f"  [{mark}] {r['tool'][:56]:58}{r['status']}")
            if r["status"] != "passed" and r.get("detail"):
                print(f"           {r['detail']}")
            elif r.get("output"):
                print(f"           {r['output']}")
        stale = [c for c in report["local_copies"] if not c["in_sync"]]
        if stale:
            print()
            for c in stale:
                tag = "arquivada" if c["archived"] else "EM USO"
                ver = ""
                if c.get("local_version", "unknown") != "unknown":
                    ver = (f" v{c['local_version']} != v{c.get('canonical_version','?')}")
                print(f"  [{'aviso' if c['archived'] else 'FALHA'}] {c['kind']} {tag}{ver}")
                print(f"           {c['copy'][:100]}")
        print(f"\n[measurement-tools] {report['passed']}/{report['tools_checked']} com "
              f"self-check passando  verdict="
              f"{'BLOCKED' if report['blocking'] else 'OK'}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
