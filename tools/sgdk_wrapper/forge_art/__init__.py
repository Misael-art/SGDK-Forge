"""forge-art: suite canonica de arte SGDK / Mega Drive.

Ver `doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md`.

Teto de claim, POR PARTE — o pacote como um todo nao tem um teto unico, e
declarar um seria arredondar um gate:

  vdp_color       testado    biblioteca de cor canonica, 20 fixtures
  pixel_contract  testado    contrato pixel-strict medido, 19 fixtures
  job             testado    jobs imutaveis com contencao adversarial
  convert         testado    conversao tecnica staging-only; nunca visual
  gimp_batch      parcial    preflight headless opcional; nenhuma operacao de
                             producao registrada
  source_route_triage testado saneamento de fonte + shootout causal de guias;
                             nao cria ou aprova arte nativa
  __main__        parcial    inspect/validate/palette/translate/convert,
                             source-audit/route-shootout/route-verify,
                             gimp-batch-preflight e self-check existem;
                             atlas/tiles/compare/promote falham fechado

A SUITE `forge-art` continua parcial: `convert` fecha apenas conformidade
tecnica. Atlas, tiles, compare, promote e os casos completos de sprite,
background e tilemap continuam abertos.

Nada aqui sustenta `slice_visual_aprovado` nem `ready_for_aaa`, e nenhuma
saida de maquina nasce `visually_approved`.
"""

__all__ = ["vdp_color", "pixel_contract", "job", "convert", "gimp_batch", "source_route_triage"]
