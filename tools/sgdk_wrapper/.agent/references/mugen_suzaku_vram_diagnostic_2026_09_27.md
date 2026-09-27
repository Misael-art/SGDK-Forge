# Caso de curadoria: inicializacao e composicao do Suzaku

Escopo: diagnostico transferivel de VRAM, paleta e reuso de tiles. Nao aprova
cenário, streaming, FPS, audio ou conversao MUGEN completa.

## Evidencia e decisao

No Mugenesis_Demo, a rota estatica compilada exigia 685 tiles (far 259,
near 426), enquanto o mapa fisico medido oferecia 648: base baixa 650,
inicio dos sprites 1010, HUD iniciando apos 492. ROM diagnostica
`bef4dba9d29d9abf9d3e3c604229a08a3465e4fbd4b9a6d60c9eb0b25d9f683d`:
SRAM informou `stage_ready=0`, `status=CAPACITY`, `required=685`,
`capacity=648`. Sessao local:
`out/mugenesis_evidence/piece_init/canonical`.

A rota de streaming anterior parava apos 456 tiles porque testava
`base + count > TILE_MAX_NUM` antes de acrescentar bancos D000/F800 ou
consultar BGFX. Portanto, os 456 **nao** demonstravam ausencia de BGFX ou
dupla contagem. Na configuracao medida, bancos fixos disjuntos somam 648
tiles; BGFX reservado em 220..491 fornece emprestimo potencial de 272,
total 920 durante a fase permitida. Os mapas/tabelas reservados precisam
continuar excluidos. Um teste host sobre o alocador C passou para limite
fisico, intervalos proibidos, sobreposicao e falha atomica. 920 ainda nao e
um budget runtime aprovado: faltam prova de residencia por camera, DMA e
restauracao no BlastEm.

ROM experimental `8bf3b933943ad4cda3292ef3952d76ad2c53c1c9ef6f0eae1022dae618f02890`
compilou e mostrou jogadores, HUD e cenario em screenshot. A captura em
`out/mugenesis_evidence/piece_stream_guard/sessions/blastem-linux-20260927T105449Z-1338066`
foi rejeitada por `vlab_block_missing`, `artifact_missing:vdp_dump` e
`artifact_missing:runtime_metrics`. A imagem mostra cores erradas e
artefatos. O atlas `source_stream_pattern_atlas.png` difere da paleta de
`source_anchor_8_bleed.png`, mas o runtime carregava a paleta da ancora.
Indice 1: atlas RGB (102,136,136), ancora RGB (34,68,102). Isso explica
uma causa concreta de cor incorreta; nao explica sozinho todos os artefatos.
Corrigir e capturar de novo antes de inferir FPS ou qualidade.

Auditoria indexada sem modificar pixels: o plano proximo completo produziu
579 tiles exatos e 426 apos H/V; um recorte de piso de 240 celulas produziu
218 exatos e 146 apos H/V, com 39 padroes compartilhados com o restante.
As contagens de recortes nao sao aditivas. O ganho de flip ja aplicado pelo
ResComp nao deve ser reivindicado novamente como economia nova. Baseline:
`doc/mugen/suzaku_piece_reuse_baseline.json`; ferramenta e self-check:
`tools/mugen2sgdk_forge/mugen2sgdk_forge/stage_piece_reuse.py`.

## Regras generalizadas incorporadas

1. Distinguir teto automatico do SGDK de VRAM fisica reclamada manualmente;
   provar ownership, intervalos, lifetime e restauracao para o layout exato.
2. Exportar o primeiro guard que falha e seus operandos. Refazer a triagem
   apos destravar a etapa; a falha seguinte pode ser independente.
3. Vincular explicitamente paleta e atlas pelos indices/CRAM compilados.
4. Medir uniao de padroes do recurso inteiro e compartilhamento das pecas na
   mesma grade8x8. Uma similaridade visual ou crop nao prova deduplicacao.
5. Preservar uma captura rejeitada como diagnostico, com claim limitado.

## Pendencias sem promocao

- Streaming completo, scroll por linha, piso com perspectiva da fonte,
  restauração de BGFX, ownership HUD, desempenho e audio precisam de ROM
  corrigida, telemetria e revisao visual.
- Candidatos de redraw de ornamentos, telhas e madeira requerem variacao
  local medida e aprovacao artistica; nenhum pixel foi aprovado aqui.
- A alteracao de `SUPER` sobre o medidor e proposta de layout, ainda nao
  implementacao validada.

Decisao: promover apenas metodo diagnostico e medicao para os owners
existentes; manter a capacidade artistica e o resultado do jogo bloqueados.
