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
    "tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py",
]

TIMEOUT_SECONDS = 120


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


def audit(root: Path, tools: list[str]) -> dict[str, Any]:
    results = [run_self_check(root, t) for t in tools]
    blocking = sorted({
        f"measurement_tool_self_check_{r['status']}"
        for r in results if r["status"] != "passed"
    })
    return {
        "schema_version": "1.0.0",
        "tool": "validate_measurement_tools",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule_ref": "SGDK_GLOBAL.md secao 34",
        "tools_checked": len(results),
        "passed": len([r for r in results if r["status"] == "passed"]),
        "results": results,
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

    if r_good["blocking"]:
        print("self-check failed: ferramenta sadia reprovada", file=sys.stderr); return 1
    if "measurement_tool_self_check_failed" not in r_bad["blocking_statuses"]:
        print("self-check failed: self-check quebrado nao detectado", file=sys.stderr); return 1
    if "measurement_tool_self_check_no_self_check" not in r_none["blocking_statuses"]:
        print("self-check failed: ausencia de self-check nao detectada", file=sys.stderr); return 1
    if "measurement_tool_self_check_missing" not in r_missing["blocking_statuses"]:
        print("self-check failed: arquivo ausente nao detectado", file=sys.stderr); return 1
    print("validate_measurement_tools self-check passed (sadia, quebrada, sem check, ausente)")
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
        print(f"\n[measurement-tools] {report['passed']}/{report['tools_checked']} com "
              f"self-check passando  verdict="
              f"{'BLOCKED' if report['blocking'] else 'OK'}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
