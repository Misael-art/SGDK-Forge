#!/usr/bin/env python3
"""Inject the aesthetic blocking directive into a project's agent guidelines.

Any agent that picks up continuity on a project reads doc/00-diretrizes-agente.md
(authority #4 of the truth hierarchy, "regras de processo"). This tool writes a
delimited block there carrying the canonical rule plus the project's own measured
provenance state, so the next agent inherits the blocker instead of rediscovering
it after shipping code-drawn art.

The block is idempotent: re-running replaces it in place and refreshes the
measurement. Everything outside the delimiters is preserved byte for byte.

Usage:
  python3 tools/sgdk_wrapper/apply_aesthetic_directive.py --project-root "<projeto>"
  python3 tools/sgdk_wrapper/apply_aesthetic_directive.py --all-projects SGDK_projects
  python3 tools/sgdk_wrapper/apply_aesthetic_directive.py --project-root <p> --check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_procedural_asset_provenance import audit  # noqa: E402
from audit_scene_headroom import audit as headroom_audit  # noqa: E402

BEGIN = "<!-- BEGIN: diretriz-bloqueio-estetico v4 -->"
END = "<!-- END: diretriz-bloqueio-estetico v4 -->"
# v1 fica reconhecido para que o bloco antigo seja substituido, nao duplicado.
LEGACY_MARKERS = [
    ("<!-- BEGIN: diretriz-bloqueio-estetico v3 -->", "<!-- END: diretriz-bloqueio-estetico v3 -->"),
    ("<!-- BEGIN: diretriz-bloqueio-estetico v2 -->", "<!-- END: diretriz-bloqueio-estetico v2 -->"),
    ("<!-- BEGIN: diretriz-bloqueio-estetico v1 -->", "<!-- END: diretriz-bloqueio-estetico v1 -->"),
]
GUIDELINES_REL = Path("doc") / "00-diretrizes-agente.md"

CANONICAL = """\
## Diretriz de bloqueio estetico — leia antes de tocar em arte

**Nenhum pixel de personagem, inimigo, boss ou cenario pode nascer de codigo.**

Primitiva, poligono, retangulo e preenchimento solido — desenhados em C no runtime ou
em Python por `PIL/ImageDraw` no pipeline de assets — servem **apenas** para telemetria,
debug visual de elemento invisivel ao jogador e elemento transitorio de interface como
barra de progresso simples. Nunca para arte de entrega.

Toda entrega visual consome arquivo de imagem externo importado por `res/resources.res`
(`IMAGE`, `SPRITE`, `TILESET`, `TILEMAP`, `MAP`), em pixel art indexada respeitando 15
cores visiveis por bloco mais o index 0 transparente.

**Um PNG desenhado por primitiva nao satisfaz a regra por estar em disco.** O que decide
e a proveniencia declarada em `doc/asset_provenance_manifest.json` — um registro por
simbolo visual do `.res`:

- `source_kind: procedural_primitive` nunca pode ter `acceptance_status: final`;
- `procedural_composed_from_authored` exige fonte autoral persistida em
  `data/source_art/` com hash: codigo pode montar, recortar e paletizar arte autoral,
  nunca desenha-la;
- declarar `hand_authored_pixel` para arquivo escrito por builder de primitivas e
  detectado e bloqueado — o auditor casa o `.res` com os builders que escrevem cada
  arquivo, nao com o nome do arquivo.

Contrato: `tools/sgdk_wrapper/schemas/asset_provenance_manifest.schema.json`.
Regra completa: `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` secoes 8.2 e 17.
"""

BRAND_GATE = """\
### Cena de marca: eixo `brand_comprehension_consequence`

Branding, title card, selo de autor e credits nao tem gameplay: nao existe rota, risco ou
decisao do jogador para a arte alterar. Nesse escopo — e somente nesse — o eixo canonico de
consequencia jogavel e substituido por `brand_comprehension_consequence`, aprovado pela
curadoria em 2026-08-17:

> cada decisao de arte precisa mudar o que o espectador entende sobre quem fez este jogo.

**Cena jogavel continua obrigada ao eixo canonico.** Nunca use essa substituicao para
escapar dele.

A substituicao so vale porque pode reprovar. Toda tecnica declarada no contrato da cena
carrega `brand_comprehension_claim` + `brand_comprehension_negative_test` +
`brand_comprehension_strength`, ou e classificada `enabling_discipline` (previne artefato,
nao ensina nada ao espectador, isenta mas obrigatoria). Tecnica que nao e nem um nem outro e
espetaculo sem consequencia.

```bash
python3 tools/sgdk_wrapper/validate_brand_comprehension_gate.py \\
  --all-projects SGDK_projects --write-reports
```

Contrato de cena de marca ATIVO sem nenhuma tecnica declarada nao passa: ausencia de
declaracao nao e aprovacao. Se o contrato foi substituido, marque-o inativo em vez de
deixa-lo vazio.

"""

AUDACITY = """\
### Doutrina de audacia — folga nao medida e timidez

O teto do hardware e o **alvo**, nao a margem de seguranca. Entregar a 40% do orcamento sem
ter medido ate onde dava nao e prudencia: e uma decisao que ninguem tomou.

- **audacia e sobre a ambicao, nunca sobre o claim.** Empurre o que voce tenta; meca o que
  voce afirma. Quanto mais ousado o alvo, mais rigorosa precisa ser a medicao;
- **antes de fechar um orcamento, meca o proximo degrau.** Se 32 cabem, meca 48 e 64. Pare
  quando MEDIR o estouro, nao quando sentir receio;
- **direcao de arte, level design e premissas do projeto vencem a densidade** — mas por
  declaracao, nunca por omissao. "Menos porque a cena precisa respirar" e razao legitima;
  silencio nao e;
- **falsa audacia** e a que parece ousada e piora o resultado: flicker para mascarar overflow,
  efeito sem consequencia, densidade que destroi leitura. O canon bloqueia cada uma.

O VDP impoe DOIS limites por scanline ao mesmo tempo (H40: 20 sprites e 320 px; H32: 16 e
256). Para sprites de 16px eles fecham no mesmo ponto, o que faz parecer que existe so um.

```bash
python3 tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py --input <cena>.json
```

`unexploited_headroom` e aviso, nao blocker: limpa-se declarando `headroom_justification`.

Regra completa: `SGDK_GLOBAL.md` secao 30.

"""

EXIT_ROUTE = """\
### Rota de saida — nao contorne, execute

1. Criar/completar `doc/asset_provenance_manifest.json` declarando **cada** simbolo visual
   do `.res`.
2. Asset desenhado por primitiva: declarar `procedural_primitive` + `placeholder`. Isso
   torna o estado honesto; o asset segue bloqueando `ready_for_aaa` e `elite_ready`, o que
   e o resultado correto — nao um contorno.
3. Para promover a `final`: re-autorar a arte por canal externo, ou persistir a fonte
   autoral em `data/source_art/` e declarar `procedural_composed_from_authored` com hash.
4. Rodar o auditor e anexar o report ao closeout:

```bash
python3 tools/sgdk_wrapper/audit_procedural_asset_provenance.py \\
  --project-root "<este projeto>" --shared-builder-root tools/image-tools
```

**Build limpo, ROM no BlastEm e screenshot nao substituem este gate.** Nova build so conta
como progresso visual se reduzir os blockers acima.
"""

FIXTURE_NOTE = """\
### Este projeto e fixture de validador

`validator_fixture: true` em `doc/project_context_manifest.json` dispensa o gate de asset
externo. Em troca, `delivery_claim_ceiling` fica preso em `none`, `concept`, `lab` ou
`exercise`: **este projeto nunca sustenta claim de entrega visual, screenshot de vitrine
ou status AAA.** Se ele passar a ter arte de verdade, deixa de ser fixture — remova a flag
e cumpra o gate completo.
"""


def measurement_block(report: dict[str, Any]) -> str:
    s = report["summary"]
    blockers = report["blocking_statuses"]
    lines = [
        f"### Estado medido em {report['generated_at'][:10]}",
        "",
        "| Metrica | Valor |",
        "|---|---|",
        f"| Simbolos visuais no `.res` | {s['pixel_bearing_symbols']} |",
        f"| Rastreados a builder de primitivas | **{s['symbols_traced_to_primitive_builders']}** |",
        f"| Proveniencia declarada | {s['declared_entries']} |",
        f"| Manifesto de proveniencia | `{report['manifest_status']}` |",
        f"| Veredito | **{'BLOCKED' if report['blocking'] else 'OK'}** |",
        "",
    ]
    if blockers:
        lines.append("Blockers ativos:")
        lines.append("")
        for code in blockers:
            lines.append(f"- `{code}`")
        lines.append("")
    traced = [s2 for s2 in report["visual_symbols"] if s2.get("primitive_builders")]
    if traced:
        lines.append(
            f"Simbolos escritos por builder de primitivas ({len(traced)}) — nenhum pode ser "
            "`final`:"
        )
        lines.append("")
        for sym in traced[:40]:
            builders = ", ".join(Path(b).name for b in sym["primitive_builders"])
            lines.append(f"- `{sym['res_symbol']}` <- {builders}")
        if len(traced) > 40:
            lines.append(f"- ... e mais {len(traced) - 40} simbolos, ver report completo")
        lines.append("")
    return "\n".join(lines)



def headroom_block(project_root: Path) -> str:
    """Registro de folga deste projeto, para o agente que assumir continuidade."""
    try:
        report = headroom_audit(project_root)
    except Exception:  # noqa: BLE001
        return ""
    decls = report.get("declarations") or []
    if not decls:
        # Zero declaracoes nao e ausencia de problema: e ausencia de medicao. Se o
        # projeto tem contrato de cena, nao saber a pressao e pior que estar fora do
        # teto, porque nem a pergunta foi feita.
        contracts = list(project_root.glob("doc/scene*contract*.json")) + list(
            project_root.glob("doc/*scene-contracts.json"))
        if not contracts:
            return ""
        return "\n".join([
            "### Registro de folga de sprites — pendente para quem assumir",
            "",
            "Varredura de 2026-08-17 pela curadoria. **Nada foi corrigido neste projeto.**",
            "",
            f"Este projeto tem {len(contracts)} contrato(s) de cena e **nenhuma declaracao de",
            "pressao de sprites por scanline**. Isso nao e ausencia de problema, e ausencia de",
            "medicao: nem a pergunta foi feita. Qualquer claim de budget de sprites aqui e",
            "insustentavel.",
            "",
            "**O que fazer:** preencha `worst_frame_sprite_layout` na cena (campo novo do schema",
            "canonico) e rode o simulador. Ver a doutrina de audacia em `SGDK_GLOBAL.md` secao 30.",
            "",
        ])
    s = report["summary"]
    lines = [
        "### Registro de folga de sprites — pendente para quem assumir",
        "",
        "Varredura de 2026-08-17 pela curadoria. **Nada foi corrigido neste projeto**; isto e",
        "registro para o proximo agente agir.",
        "",
        f"- declaracoes de pressao encontradas: **{s['declarations_found']}**",
        f"- `unexploited_headroom` (abaixo de 60% do teto): **{s['unexploited_headroom']}**",
        f"- `hardware_idle_undeclared` (zero sprites sem declarar que e decisao): **{s['hardware_idle_undeclared']}**",
        f"- `sprite_pressure_unmeasured` (prosa, nada computavel): **{s['unmeasured']}**",
        "",
    ]
    worst = [d for d in decls if d.get("finding") and d.get("finding") != "ok"][:6]
    if worst:
        lines.append("Declaracoes que pedem acao:")
        lines.append("")
        for d in worst:
            util = f"{d['utilization']:.0%}" if d.get("utilization") is not None else "sem numero"
            lines.append(f"- `{d['file']}` -> `{d['field']}` = \"{d['declared'][:56]}\" ({util}) -> `{d['finding']}`")
        lines.append("")
    lines += [
        "**O que fazer quando for atuar aqui:** preencha `worst_frame_sprite_layout` no",
        "`scene-contracts.json` da cena (campo novo do schema canonico, formato do simulador),",
        "rode o simulador, e entao ou empurre a densidade ate medir o teto ou declare",
        "`headroom_justification` dizendo por que a direcao de arte ou o level design pedem menos.",
        "",
        "```bash",
        "python3 tools/sgdk_wrapper/audit_scene_headroom.py --root SGDK_projects",
        "python3 tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py --input <cena>.json",
        "```",
        "",
    ]
    return "\n".join(lines)


def build_block(report: dict[str, Any] | None, project_root: Path | None = None) -> str:
    parts = [BEGIN, "", CANONICAL]
    if report is None:
        parts.append(
            "### Estado medido\n\nAinda nao medido neste projeto. Rode o auditor antes de "
            "qualquer claim visual.\n"
        )
    else:
        if report["validator_fixture"]:
            parts.append(FIXTURE_NOTE)
        parts.append(measurement_block(report))
    parts.append(BRAND_GATE)
    parts.append(AUDACITY)
    if project_root is not None:
        hb = headroom_block(project_root)
        if hb:
            parts.append(hb)
    parts.append(EXIT_ROUTE)
    parts.append(END)
    return "\n".join(parts)


def newline_style(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def apply_to_project(
    project_root: Path,
    shared_builder_roots: list[Path],
    check_only: bool,
    measure: bool = True,
) -> tuple[str, bool]:
    """Return (status, changed)."""
    guidelines = project_root / GUIDELINES_REL
    report: dict[str, Any] | None = None
    if measure:
        try:
            report = audit(project_root, shared_builder_roots)
        except Exception as exc:  # noqa: BLE001 - never let one project abort the sweep
            return (f"audit_failed: {exc}", False)

    block = build_block(report, project_root)

    if guidelines.exists():
        original = guidelines.read_text(encoding="utf-8-sig")
    else:
        original = (
            "# 00 - Diretrizes do Agente\n\n"
            "Regras de processo deste projeto. Autoridade #4 da hierarquia de verdade.\n"
        )

    eol = newline_style(original)
    normalized = original.replace("\r\n", "\n")

    pair = next(
        ((b, e) for b, e in [(BEGIN, END), *LEGACY_MARKERS] if b in normalized and e in normalized),
        None,
    )
    if pair:
        begin_marker, end_marker = pair
        head, rest = normalized.split(begin_marker, 1)
        _, tail = rest.split(end_marker, 1)
        updated = head + block + tail
        action = "updated"
    else:
        separator = "" if normalized.endswith("\n\n") else ("\n" if normalized.endswith("\n") else "\n\n")
        updated = normalized + separator + "\n" + block + "\n"
        action = "inserted"

    changed = updated != normalized
    if changed and not check_only:
        guidelines.parent.mkdir(parents=True, exist_ok=True)
        guidelines.write_text(updated.replace("\n", eol) if eol == "\r\n" else updated, encoding="utf-8")

    verdict = "not_measured" if report is None else ("BLOCKED" if report["blocking"] else "OK")
    if not changed:
        return (f"current ({verdict})", False)
    return (f"{action} ({verdict})", True)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", action="append", default=[])
    parser.add_argument(
        "--all-projects",
        default="",
        help="Sweep every direct child of this directory that has doc/ or res/.",
    )
    parser.add_argument("--shared-builder-root", action="append", default=[])
    parser.add_argument("--check", action="store_true", help="Report drift without writing.")
    parser.add_argument(
        "--no-measure",
        action="store_true",
        help="Insert the canonical rule without a measured state. Use for the template, "
        "whose skeleton has no real assets to measure.",
    )
    args = parser.parse_args(argv)

    targets: list[Path] = [Path(p).expanduser().resolve() for p in args.project_root]
    if args.all_projects:
        # Descoberta em profundidade arbitraria: um viewer SGDK aninhado dentro de um
        # estudo tem doc/ e res/ proprios e precisa da diretriz tanto quanto um projeto
        # de topo. A varredura de um nivel so deixava esses subprojetos descobertos.
        root = Path(args.all_projects).expanduser().resolve()
        skip = {"out", "build", "rascunho", ".git", "__pycache__", "node_modules", "data"}
        seen: set[Path] = set()
        for candidate in sorted(root.rglob("*")):
            if not candidate.is_dir():
                continue
            rel_parts = {p.lower() for p in candidate.relative_to(root).parts}
            if rel_parts & skip:
                continue
            is_project = (candidate / "doc" / GUIDELINES_REL.name).is_file() or (
                (candidate / "res").is_dir() and (candidate / "src").is_dir()
            )
            if is_project and candidate not in seen:
                seen.add(candidate)
                targets.append(candidate)

    if not targets:
        print("[aesthetic-directive] nothing to do: pass --project-root or --all-projects")
        return 2

    shared = [Path(p).expanduser().resolve() for p in args.shared_builder_root]
    shared = [p for p in shared if p.is_dir()]

    changed_any = False
    for project in targets:
        status, changed = apply_to_project(project, shared, args.check, not args.no_measure)
        changed_any = changed_any or changed
        print(f"[aesthetic-directive] {project.name[:44]:46} {status}")

    if args.check and changed_any:
        print("[aesthetic-directive] drift detected: directive missing or stale")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
