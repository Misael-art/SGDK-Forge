#!/usr/bin/env python3
"""Validate the brand_comprehension_consequence axis of art_gameplay_direction_gate.

A brand scene has no gameplay: there is no route, risk, enemy timing or player
decision for the art to change. The canonical gate axis cannot be filled with
invention, so it is substituted by `brand_comprehension_consequence` — approved
by the human curator on 2026-08-17.

The substitution is only legitimate if it can FAIL. This validator enforces the
structural half of that, which is the half a script can honestly judge:

  every technique declared in a brand-scene contract must either
    - carry a comprehension claim WITH a falsifiable negative test, or
    - be classified `enabling_discipline` (prevents an artifact, teaches the
      viewer nothing, therefore exempt but still mandatory).

A technique that is neither is spectacle without consequence. That is the exact
failure the maximalist philosophy blocks, and a brand scene is where it hides
best precisely because no gameplay can expose it.

What this script does NOT do: judge whether a claim is TRUE. That is a human
call at the visual gate. It only proves no technique got a free pass, and
surfaces weak claims instead of letting them read as strong.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROLE_BEARING = "comprehension_bearing"
ROLE_ENABLING = "enabling_discipline"
VALID_STRENGTHS = {"strong", "moderate", "weak"}


def collect_techniques(contract: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """Find every declared technique, whatever the contract shape.

    A recursive walk instead of a fixed path into `acts`: the workspace has v1
    (`screens`), v2 (`acts`) and a divergent v3 in the wild, and hardcoding one
    shape made the gate silently report OK on all the others. A gate that passes
    an empty contract is worse than no gate.
    """
    found: list[tuple[str, dict[str, Any]]] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            if "registry_id" in node and isinstance(node["registry_id"], str):
                found.append((path or "root", node))
                return
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else key)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")

    for key in ("acts", "screens", "techniques", "audio", "scenes", "beats"):
        if key in contract:
            walk(contract[key], key)
    return found


def contract_state(contract: dict[str, Any]) -> str:
    """active | inactive — an inactive contract is exempt, but exempt out loud."""
    declared = str(contract.get("contract_state", "")).strip().lower()
    if declared in {"active", "inactive"}:
        return declared
    blob = " ".join(
        str(contract.get(k, "")) for k in ("status", "contract_id", "note", "purpose")
    ).lower()
    if "inactive" in blob or "superseded_by" in blob or "legacy_template_inactive" in blob:
        return "inactive"
    return "active"


def audit(contract_path: Path) -> dict[str, Any]:
    contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    findings: list[dict[str, Any]] = []
    bearing = enabling = 0
    weak: list[str] = []

    techniques = collect_techniques(contract)
    state = contract_state(contract)

    if not techniques:
        if state == "inactive":
            findings.append({
                "code": "exempt_inactive_contract",
                "severity": "info",
                "subject": str(contract.get("contract_id", "?")),
                "where": "contract",
                "message": "contrato declarado inativo/substituido: isento do eixo. "
                           "A cena de marca ativa deste projeto precisa ser gateada onde ela vive.",
            })
        else:
            findings.append({
                "code": "brand_comprehension_techniques_undeclared",
                "severity": "blocking",
                "subject": str(contract.get("contract_id", "?")),
                "where": "contract",
                "message": "contrato de cena de marca ativo sem NENHUMA tecnica declarada com "
                           "registry_id. O eixo nao tem o que julgar: nao e aprovacao, e ausencia "
                           "de declaracao. Declare as tecnicas com claim e teste negativo, ou "
                           "marque o contrato como inativo se ele foi substituido.",
            })

    for label, tech in techniques:
        rid = tech["registry_id"]
        role = tech.get("brand_comprehension_role")

        if role == ROLE_ENABLING:
            enabling += 1
            if not tech.get("brand_comprehension_note"):
                findings.append({
                    "code": "enabling_discipline_without_note",
                    "severity": "warning",
                    "subject": rid,
                    "where": label,
                    "message": "isento de claim mas sem nota explicando por que nao ensina nada ao espectador",
                })
            continue

        if role == ROLE_BEARING:
            bearing += 1
            claim = (tech.get("brand_comprehension_claim") or "").strip()
            negative = (tech.get("brand_comprehension_negative_test") or "").strip()
            strength = tech.get("brand_comprehension_strength")

            if not claim:
                findings.append({
                    "code": "brand_comprehension_missing",
                    "severity": "blocking",
                    "subject": rid,
                    "where": label,
                    "message": "declarado comprehension_bearing sem claim: o que o espectador entende?",
                })
            if not negative:
                findings.append({
                    "code": "brand_comprehension_not_falsifiable",
                    "severity": "blocking",
                    "subject": rid,
                    "where": label,
                    "message": "claim sem teste negativo: sem ele o eixo nao pode reprovar nada",
                })
            if strength not in VALID_STRENGTHS:
                findings.append({
                    "code": "brand_comprehension_strength_undeclared",
                    "severity": "blocking",
                    "subject": rid,
                    "where": label,
                    "message": f"strength deve ser um de {sorted(VALID_STRENGTHS)}",
                })
            elif strength == "weak":
                weak.append(rid)
            continue

        findings.append({
            "code": "brand_comprehension_unjustified_technique",
            "severity": "blocking",
            "subject": rid,
            "where": label,
            "message": "tecnica sem classificacao: declare um claim com teste negativo, "
                       "classifique como enabling_discipline, ou corte a tecnica. "
                       "Espetaculo sem consequencia nao passa.",
        })

    for rid in weak:
        findings.append({
            "code": "brand_comprehension_claim_weak",
            "severity": "warning",
            "subject": rid,
            "where": "declared",
            "message": "claim fraco: precisa de prova perceptiva no runtime, senao vira decoracao. "
                       "Nao pode ser apresentado como forte no closeout.",
        })

    blocking = sorted({f["code"] for f in findings if f["severity"] == "blocking"})
    return {
        "schema_version": "1.0.0",
        "gate": "art_gameplay_direction_gate",
        "axis": "brand_comprehension_consequence",
        "axis_approved_by": "human_curator",
        "axis_approved_at": "2026-08-17",
        "contract_id": contract.get("contract_id"),
        "contract_state": state,
        "contract_path": contract_path.as_posix(),
        "summary": {
            "techniques_total": bearing + enabling,
            "comprehension_bearing": bearing,
            "enabling_discipline": enabling,
            "weak_claims": len(weak),
        },
        "findings": findings,
        "human_judgement_still_required": "Este validador prova que nenhuma tecnica passou sem "
                                          "justificativa. Ele NAO julga se o claim e verdadeiro: "
                                          "isso e decisao humana no gate visual, contra screenshot "
                                          "e visual_vdp_dump reais.",
        "blocking": bool(blocking),
        "blocking_statuses": blocking,
    }


# Cena de marca = sem decisao do jogador. Menu de front-end tem decisao do jogador e
# portanto continua no eixo canonico de consequencia jogavel; nao entra aqui.
BRAND_SCENE_PATTERNS = ("branding_sequence_contract.json", "credits_contract.json")


def discover(root: Path) -> list[Path]:
    found: list[Path] = []
    for pattern in BRAND_SCENE_PATTERNS:
        found.extend(root.rglob(pattern))
    return sorted(set(found))


def sweep(root: Path, write_reports: bool, quiet: bool) -> int:
    contracts = discover(root)
    if not contracts:
        print(f"[brand-comprehension] nenhum contrato de cena de marca em {root}")
        return 2

    blocked = 0
    rows: list[tuple[str, dict[str, Any]]] = []
    for path in contracts:
        try:
            report = audit(path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[ERROR] {path}: {exc}")
            blocked += 1
            continue
        if write_reports:
            out = path.parent / "brand_comprehension_gate_report.json"
            out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
        if report["blocking"]:
            blocked += 1
        rows.append((path.as_posix(), report))

    if not quiet:
        for path, report in rows:
            try:
                project = Path(path).relative_to(root).parts[0]
            except ValueError:
                project = Path(path).parent.parent.name
            s = report["summary"]
            verdict = "BLOCKED" if report["blocking"] else "OK"
            print(
                "{0:44} {1:26} {2:9} bearing={3:2} enabling={4:2} {5}".format(
                    project[:44],
                    str(report["contract_id"])[:26],
                    report["contract_state"],
                    s["comprehension_bearing"],
                    s["enabling_discipline"],
                    verdict,
                )
            )
            for f in report["findings"]:
                if f["severity"] in ("blocking", "info"):
                    print(f"    [{f['severity']}] {f['code']}")
        print(f"\n[brand-comprehension] {blocked} de {len(rows)} contratos bloqueados")

    return 1 if blocked else 0


def self_check() -> int:
    """Verifica que o gate PASSA no caso valido e REPROVA no invalido."""
    good = {"contract_id": "sc_ok", "acts": [{"act": 1, "id": "a", "techniques": [
        {"registry_id": "t1", "brand_comprehension_role": "comprehension_bearing",
         "brand_comprehension_claim": "c", "brand_comprehension_negative_test": "n",
         "brand_comprehension_strength": "strong"},
        {"registry_id": "t2", "brand_comprehension_role": "enabling_discipline",
         "brand_comprehension_note": "previne artefato"}]}]}
    bad = {"contract_id": "sc_bad", "acts": [{"act": 1, "id": "a", "techniques": [
        {"registry_id": "t3"}]}]}
    empty = {"contract_id": "sc_empty", "status": "active", "acts": []}

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        def run(obj):
            f = Path(td) / "c.json"
            f.write_text(json.dumps(obj), encoding="utf-8")
            return audit(f)
        g, b, e = run(good), run(bad), run(empty)

    if g["blocking"]:
        print("self-check failed: contrato valido reprovado", file=sys.stderr); return 1
    if not b["blocking"] or "brand_comprehension_unjustified_technique" not in b["blocking_statuses"]:
        print("self-check failed: tecnica sem justificativa nao reprovou", file=sys.stderr); return 1
    if "brand_comprehension_techniques_undeclared" not in e["blocking_statuses"]:
        print("self-check failed: contrato ativo e vazio nao reprovou", file=sys.stderr); return 1
    print("validate_brand_comprehension_gate self-check passed (passa, reprova, vazio)")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", default="")
    ap.add_argument(
        "--all-projects",
        default="",
        help="Varre esta arvore procurando contratos de cena de marca e gateia cada um.",
    )
    ap.add_argument(
        "--write-reports",
        action="store_true",
        help="No modo sweep, grava brand_comprehension_gate_report.json ao lado de cada contrato.",
    )
    ap.add_argument("--output", default="")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return self_check()

    if args.all_projects:
        root = Path(args.all_projects).expanduser().resolve()
        if not root.is_dir():
            print(f"[brand-comprehension] ERROR: diretorio nao encontrado: {root}")
            return 2
        return sweep(root, args.write_reports, args.quiet)

    if not args.contract:
        print("[brand-comprehension] ERROR: passe --contract ou --all-projects")
        return 2

    contract_path = Path(args.contract).expanduser().resolve()
    if not contract_path.is_file():
        print(f"[brand-comprehension] ERROR: contract not found: {contract_path}")
        return 2

    report = audit(contract_path)

    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        s = report["summary"]
        print(f"[brand-comprehension] contrato: {report['contract_id']}")
        print(
            "[brand-comprehension] tecnicas={0} bearing={1} enabling={2} weak={3}".format(
                s["techniques_total"], s["comprehension_bearing"],
                s["enabling_discipline"], s["weak_claims"],
            )
        )
        for f in report["findings"]:
            print(
                "[{0}] {1} :: {2} ({3}) :: {4}".format(
                    f["severity"].upper(), f["code"], f["subject"], f["where"], f["message"]
                )
            )
        verdict = "BLOCKED" if report["blocking"] else "OK"
        print(f"[brand-comprehension] verdict={verdict} blocking={report['blocking_statuses']}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
