#!/usr/bin/env python3
"""CLI do forge-art. `python3 -m forge_art <comando>`.

A CLI e a autoridade da suite. GIMP, Aseprite, Oeste e Ether sao frontends
opcionais e nunca dependencia de nucleo.

Estado honesto dos comandos — o proprio `--help` diz o que existe:

  IMPLEMENTADOS   inspect, validate, palette, convert, source-audit,
                  route-shootout, route-verify, workset-validate, self-check,
                  gimp-batch-preflight
  PROBE PROCEDURAL native-edit (nao e autoria artistica nem fonte promovivel)
  NAO IMPLEMENTADOS  atlas, tiles, compare, promote
  ROTEADO PARA HUMANO  translate

Um comando nao implementado **falha fechado** com codigo 2 e nomeia a proxima
acao causal. Ele nunca devolve resultado plausivel, nunca degrada em silencio e
nunca escreve nada. Isso e deliberado: a alternativa — um `convert` que faz
resize+quantize e chama o resultado de asset — e exatamente o defeito que esta
suite existe para eliminar.

`translate` (rota B, traducao nativa assistida) e um caso a parte e nao vai ser
"implementado" no sentido de gerar pixel automaticamente. Um modelo que nao e
capaz de produzir a imagem no padrao exigido deve REGISTRAR a demanda para
quem e capaz, e nao produzir grafico ruim por codigo. E o que ele faz: escreve
um registro de encaminhamento e sai reprovado.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from forge_art import convert, foreground_matte, gimp_batch, job, native_edit, pixel_contract, source_route_triage, vdp_color, visual_workset
except ImportError:  # execucao pelo caminho do arquivo
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from forge_art import convert, foreground_matte, gimp_batch, job, native_edit, pixel_contract, source_route_triage, vdp_color, visual_workset

CLI_VERSION = "1.3.0"

#: Comandos declarados no plano que ainda nao existem. Cada um carrega o
#: motivo de nao ter sido escrito e a proxima acao causal, para que a
#: mensagem de erro seja acionavel em vez de "nao foi possivel".
NOT_IMPLEMENTED = {
    "atlas": (
        "empacotamento com pivot e footline nao implementado",
        "declare pivots e footline no contrato do asset e monte o atlas a mao; "
        "`validate` ja mede o PNG resultante",
    ),
    "tiles": (
        "dedup de tile por SHA-256 e relatorio de residencia nao implementados",
        "nao declare economia de tile sem esse relatorio; ela nao esta medida",
    ),
    "compare": (
        "contact sheet e comparacao 8x nao implementados",
        "faca a comparacao 8x manualmente antes de qualquer aprovacao humana",
    ),
    "promote": (
        "promocao para res/ nao implementada, e por ora e melhor assim",
        "promocao exige technical_candidate E visually_approved registrado; "
        "faca a copia manualmente depois de registrar a decisao humana no job",
    ),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _emit(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))


# ---------------------------------------------------------------------------
# Comandos implementados
# ---------------------------------------------------------------------------

def cmd_inspect(args) -> int:
    """Mede e relata. Nao emite veredito e nao escreve nada."""
    info = pixel_contract.read_png_chunks(Path(args.png))
    _emit({
        "command": "inspect", "file": str(args.png),
        "width": info["width"], "height": info["height"],
        "bit_depth": info["bit_depth"], "color_type": info["color_type"],
        "plte_entries": info["plte_entries"],
        "has_trns": info["has_trns"], "trns": list(info["trns"]),
        "scope": "observacao crua; inspect nao aprova nem reprova",
        "next_action": "rode `validate --index0-role <papel>` para medir contra o contrato",
    })
    return 0


def cmd_validate(args) -> int:
    report = pixel_contract.validate_png(
        Path(args.png), args.index0_role, oracle=args.oracle,
        require_multiple_of_8=not args.allow_odd_dimensions)
    _emit(report)
    if report["blocking"]:
        print(f"[FAIL] {report['blocking_statuses']}", file=sys.stderr)
        return 1
    print("[OK] technical_candidate — NAO e aprovacao visual; a promocao para "
          "res/ ainda exige decisao humana registrada", file=sys.stderr)
    return 0


def cmd_palette(args) -> int:
    if args.snap:
        rgb = tuple(int(v, 0) for v in args.snap.split(","))
        snapped = vdp_color.snap_rgb_to_vdp_grid(rgb, oracle=args.oracle)
        _emit({"command": "palette", "input": list(rgb), "oracle": args.oracle,
               "snapped": list(snapped),
               "vdp_word": f"0x{vdp_color.rgb24_to_vdp_color(rgb, oracle=args.oracle):04X}",
               "on_grid": vdp_color.is_on_grid(rgb, vdp_color.GRID_AUTHORING)})
        return 0
    _emit({"command": "palette", "cram_combinations": len(vdp_color.all_cram_colors()),
           "authoring_levels": [f"0x{v:02X}" for v in vdp_color.AUTHORING_LEVELS],
           "display_levels": [f"0x{v:02X}" for v in vdp_color.DISPLAY_LEVELS],
           "next_action": "use --snap R,G,B para trazer uma cor para a grade"})
    return 0


def cmd_translate(args) -> int:
    """Rota B: nao gera pixel. Encaminha para quem e capaz.

    Este comando existe justamente para NAO produzir grafico ruim por codigo.
    Ele escreve um registro de encaminhamento com tudo que o proximo executor
    precisa e sai reprovado.
    """
    record = {
        "schema_version": "1.0.0",
        "command": "translate",
        "route": job.ROUTE_ASSISTED,
        "asset_id": args.asset_id,
        "source": str(args.source) if args.source else None,
        "recorded_at": _now(),
        "status": "blocked_pending_capable_producer",
        "why": (
            "Rota B e construcao em canvas nativo com decisao de silhueta, "
            "anatomia, material e leitura. Quantizar ou vetorizar a fonte "
            "high-res nao produz isso: produz um asset tecnicamente conforme e "
            "visualmente reprovado. Ferramenta nenhuma desta suite substitui "
            "essa decisao."
        ),
        "handoff_to": "pixel artist humano, ou agente com capacidade de "
                      "producao nativa comprovada em referencia da mesma geracao",
        "required_from_producer": [
            "construcao no canvas nativo declarado (ex.: 48x64), nunca downscale",
            "regioes semanticas declaradas antes do primeiro pixel",
            "paleta escolhida por funcao (luz, material, leitura), nao por "
            "frequencia estatistica",
            "comparacao ampliada 8x anexada",
            "aprovacao humana registrada ANTES de qualquer animacao ou promocao",
        ],
        "forbidden_shortcuts": [
            "resize interpolado (Lanczos/bilinear/bicubico) da fonte high-res",
            "quantizacao direta da ilustracao como se fosse asset final",
            "dithering em lineart, rosto, olhos, maos ou sprite 48x64",
            "composicao sobre preto para 'resolver' transparencia",
        ],
        "claim_ceiling": "documentado — nenhum pixel foi produzido por esta chamada",
        "next_action": (
            "encaminhe este registro ao produtor capaz; quando a imagem "
            "existir, meça com `python3 -m forge_art validate` e so entao "
            "registre a decisao humana no diretorio do job"
        ),
    }
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        record["written_to"] = str(out)
    _emit(record)
    print("[BLOCKED] translate nao gera pixel por design; encaminhamento "
          "registrado. Ver next_action.", file=sys.stderr)
    return 3


def cmd_self_check(args) -> int:
    reports = {
        "vdp_color": vdp_color.self_check(),
        "pixel_contract": pixel_contract.self_check(),
        "job": job.self_check(),
        "convert": convert.self_check(),
        "foreground_matte": foreground_matte.self_check(),
        "source_route_triage": source_route_triage.self_check(),
        # Deterministic contract fixtures only.  The optional host probe is a
        # separate command so forge-art never depends on GIMP being installed.
        "gimp_batch_contract": gimp_batch.self_check(),
        "native_edit_contract": native_edit.self_check(),
        "visual_workset": visual_workset.self_check(),
    }
    summary = {
        name: {"passed": r["fixtures_passed"], "total": r["fixtures_total"],
               "blocking": r["blocking"]}
        for name, r in reports.items()
    }
    blocking = any(r["blocking"] for r in reports.values())
    _emit({"command": "self-check", "cli_version": CLI_VERSION,
           "summary": summary, "blocking": blocking})
    total = sum(s["total"] for s in summary.values())
    passed = sum(s["passed"] for s in summary.values())
    print(f"{'[FAIL]' if blocking else '[OK]'} {passed}/{total} fixtures",
          file=sys.stderr)
    return 1 if blocking else 0


def cmd_not_implemented(name: str) -> int:
    why, next_action = NOT_IMPLEMENTED[name]
    _emit({"command": name, "status": "not_implemented", "why": why,
           "next_action": next_action,
           "note": "falha fechado por design; um resultado plausivel aqui "
                   "seria pior que nenhum resultado"})
    print(f"[NOT IMPLEMENTED] {name}: {why} | proxima acao: {next_action}",
          file=sys.stderr)
    return 2

def cmd_convert(args) -> int:
    try: state=convert.convert(Path(args.project_root),Path(args.spec))
    except Exception as exc:
        blocker = getattr(exc, "blocker", "conversion_rejected")
        next_action = (
            "mantenha o projeto congelado; reativacao exige decisao humana e novo workset"
            if blocker == "visual_production_frozen"
            else "corrija o spec declarativo ou a fonte"
        )
        _emit({"command":"convert","status":"rejected","blocking":True,
               "blocker": blocker, "blockers":[str(exc)],
               "next_action": next_action}); return 1
    _emit(state); return 0


def cmd_gimp_batch_preflight(args) -> int:
    try:
        report = gimp_batch.preflight(args.gimp, args.timeout_seconds)
    except Exception as exc:
        _emit({
            "command": "gimp-batch-preflight",
            "status": "failed",
            "blocking": True,
            "blockers": [str(exc)],
            "next_action": "corrija o host ou use forge-art/Pillow/ImageMagick; nao abra a GUI por automacao",
        })
        return 3
    _emit(report)
    return 3 if report["blocking"] else 0


def cmd_native_edit(args) -> int:
    try:
        report = native_edit.native_edit(
            Path(args.project_root), Path(args.actions), Path(args.out)
        )
    except Exception as exc:
        _emit({
            "command": "native-edit",
            "status": "rejected",
            "blocking": True,
            "blocker": getattr(exc, "blocker", "native_edit_failed"),
            "error": str(exc),
            "next_action": (
                "corrija o action file e respeite o visual workset; projeto "
                "congelado nao aceita producao. Nenhuma saida parcial foi publicada"
            ),
        })
        return 1
    _emit(report)
    return 0


def cmd_workset_validate(args) -> int:
    try:
        report = visual_workset.validate_project_workset(Path(args.project_root))
    except Exception as exc:
        _emit({
            "command": "workset-validate",
            "status": "rejected",
            "blocking": True,
            "blocker": getattr(exc, "blocker", "visual_workset_validation_failed"),
            "error": str(exc),
        })
        return 1
    _emit(report)
    return 0


def cmd_source_audit(args) -> int:
    try:
        report = source_route_triage.write_source_audit(
            Path(args.project_root), Path(args.spec), Path(args.out))
    except Exception as exc:
        _emit({
            "command": "source-audit", "status": "rejected", "blocking": True,
            "blockers": [str(exc)],
            "next_action": "corrija o spec ou forneca fonte limpa; nao tente inferir anatomia sob sombra, poeira, fumaça, checkerboard ou oclusao",
        })
        return 1
    _emit(report)
    return 1 if report["blocking"] else 0


def cmd_route_shootout(args) -> int:
    try:
        report = source_route_triage.run_shootout_from_spec(
            Path(args.project_root), Path(args.spec))
    except Exception as exc:
        blocker = getattr(exc, "blocker", "route_shootout_rejected")
        next_action = (
            "mantenha o projeto congelado; reativacao exige decisao humana e novo workset"
            if blocker == "visual_production_frozen"
            else "passe primeiro source-audit e use novo output_dir em out/ ou rascunho/; nenhuma rota escreve em data/ ou res/"
        )
        _emit({
            "command": "route-shootout", "status": "rejected", "blocking": True,
            "blocker": blocker,
            "blockers": [str(exc)],
            "next_action": next_action,
        })
        return 1
    _emit({
        "command": "route-shootout", "status": "completed",
        "executed": report["executed"], "skipped": report["skipped"],
        "board": report["board"], "verification": report["verification"],
        "automatic_winner": None,
        "next_action": "selecione no maximo um underlay principal, um challenger e um controle; prossiga como native_reauthoring_over_<route>_guide",
        "claim_ceiling": report["claim_ceiling"],
    })
    return 1 if report["verification"]["blocking"] else 0


def cmd_route_verify(args) -> int:
    try:
        report = source_route_triage.verify_shootout_file(
            Path(args.project_root), Path(args.report))
    except Exception as exc:
        _emit({"command": "route-verify", "status": "failed", "blocking": True,
               "blockers": [str(exc)]})
        return 1
    _emit(report)
    return 1 if report["blocking"] else 0


# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="forge-art", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"forge-art {CLI_VERSION}")
    # Alias de flag para o meta-gate de ferramentas de medicao, que invoca
    # todo instrumento como `<tool> --self-check`.
    p.add_argument("--self-check", dest="selfcheck_flag", action="store_true",
                   help="igual ao subcomando self-check")
    sub = p.add_subparsers(dest="command")

    ins = sub.add_parser("inspect", help="mede um PNG e relata; nao julga")
    ins.add_argument("png")

    val = sub.add_parser("validate", help="mede um PNG contra o contrato pixel-strict")
    val.add_argument("png")
    val.add_argument("--index0-role", required=True, choices=pixel_contract.INDEX0_ROLES)
    val.add_argument("--oracle", default=vdp_color.ORACLE_RESCOMP)
    val.add_argument("--allow-odd-dimensions", action="store_true")

    pal = sub.add_parser("palette", help="biblioteca de cor canonica do VDP")
    pal.add_argument("--snap", metavar="R,G,B")
    pal.add_argument("--oracle", default=vdp_color.ORACLE_RESCOMP)

    tr = sub.add_parser("translate",
                        help="rota B: NAO gera pixel; registra encaminhamento")
    tr.add_argument("--asset-id", required=True)
    tr.add_argument("--source")
    tr.add_argument("--out", help="caminho do registro de encaminhamento")

    sub.add_parser("self-check", help="roda os self-checks dos modulos canonicos")

    cv=sub.add_parser("convert",help="technical conversion in immutable staging only")
    cv.add_argument("--project-root",required=True); cv.add_argument("--spec",required=True)
    gb = sub.add_parser(
        "gimp-batch-preflight",
        help="prova opcional do Python-Fu headless; nunca abre GUI nem converte asset",
    )
    gb.add_argument("--gimp", help="executavel GIMP 3; default: descoberta no PATH")
    gb.add_argument("--timeout-seconds", type=int, default=gimp_batch.DEFAULT_TIMEOUT_SECONDS)
    ne = sub.add_parser(
        "native-edit",
        help=(
            "rasteriza acoes coordenadas em staging como procedural_code_probe; "
            "nao comprova autoria artistica e nunca e promovivel"
        ),
    )
    ne.add_argument("--project-root", required=True)
    ne.add_argument("--actions", required=True)
    ne.add_argument("--out", required=True)
    wv = sub.add_parser(
        "workset-validate",
        help="valida fontes elegiveis, referencias e congelamento visual do projeto",
    )
    wv.add_argument("--project-root", required=True)
    sa = sub.add_parser(
        "source-audit",
        help="classifica contaminacao visual e elegibilidade antes de qualquer rota",
    )
    sa.add_argument("--project-root", required=True)
    sa.add_argument("--spec", required=True)
    sa.add_argument("--out", required=True)
    rs = sub.add_parser(
        "route-shootout",
        help="executa rotas mecanicas causais e gera painel; nunca produz arte nativa",
    )
    rs.add_argument("--project-root", required=True)
    rs.add_argument("--spec", required=True)
    rv = sub.add_parser(
        "route-verify",
        help="revalida hashes, rotulos causais e dimensoes de um shootout",
    )
    rv.add_argument("--project-root", required=True)
    rv.add_argument("--report", required=True)
    for name, (why, _n) in NOT_IMPLEMENTED.items():
        sub.add_parser(name, help=f"NAO IMPLEMENTADO — {why}")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "selfcheck_flag", False) or args.command == "self-check":
        return cmd_self_check(args)
    if args.command is None:
        parser.print_help()
        return 2
    if args.command in NOT_IMPLEMENTED:
        return cmd_not_implemented(args.command)
    return {
        "inspect": cmd_inspect, "validate": cmd_validate, "palette": cmd_palette,
        "translate": cmd_translate, "convert": cmd_convert,
        "gimp-batch-preflight": cmd_gimp_batch_preflight,
        "native-edit": cmd_native_edit,
        "workset-validate": cmd_workset_validate,
        "source-audit": cmd_source_audit,
        "route-shootout": cmd_route_shootout,
        "route-verify": cmd_route_verify,
        "self-check": lambda a: cmd_self_check(a),
    }[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
