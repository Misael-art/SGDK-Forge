# Suzaku: regressão dos candidatos de captura — 2026-09-27

## Veredito

Os dois candidatos chegaram à cena de luta no BlastEm, mas não inicializaram o cenário. O fundo aparece vazio e SRAM registra `stage_ready=0`. A captura válida como evidência de falha não transforma esses builds em ROM jogável com cenário.

## Builds observados

| Rota | SHA-256 da ROM | SRAM / resultado | Métricas VLAB | Bundle local |
|---|---|---|---|---|
| Streaming com sweep de câmera | `2c62c7f52c383954ad01dbd6d32dfd429576cfc4d095ba606b7de49ec8b97b19` | capacidade 456 tiles; residentes e pico 0; overflow 0; restaurações 0; `stage_ready=0` | 50/1200 quadros acima do orçamento; CPU máx. 124; snapshot de 59,9 FPS não prova cadência | `out/mugenesis_evidence/suzaku_stream/canonical` — sessão `blastem-linux-20260927T020859Z-1815492` |
| Estático em dois planos | `c1b03a491848803ccecc56c678b09c88c040069db132e61c6030610500788c9a` | `stage_ready=0`; restaurações 0; falhas de sprite 0; menor bloco contíguo 94 tiles | 82/1200 quadros acima do orçamento; CPU máx. 141; snapshot de 59,5 FPS não prova cadência | `out/mugenesis_evidence/suzaku_static_planes/canonical` — sessão `blastem-linux-20260927T022756Z-1860145` |

## Diagnóstico disponível

Correção de diagnóstico: os 456 tiles eram o ponto de interrupção da guarda `TILE_MAX_NUM=1536`, antes de alcançar D000, F800 ou consultar o empréstimo BGFX. Não demonstravam ausência de reserva nem dupla contagem. O layout medido reserva BGFX em 220–491, HUD em 492–649 e pool baixo em 650–1009. Os bancos fixos somam 648 tiles; o empréstimo disjunto de 272 permite 920 durante sua vigência. O sweep anterior não testou movimento real do cenário: não houve cache residente nem mapa carregado. A correção da guarda passou em teste host; streaming completo e restauração do empréstimo continuam sem aprovação.

Isso não explica por que a inicialização estática em dois planos também retornou falso. A causa dessa falha permanece aberta; não atribuir a compressão dos recursos nem outra condição sem observar os campos reais gerados e o motivo exato do retorno.

## Próximas ações

1. Adicionar telemetria de diagnóstico que informe, na própria captura, o código de retorno de `FIGHT_STAGE_init`, base VRAM, limite do pool de sprites, contagens de tiles e flags/dimensões dos recursos usados.
2. Verificar nos headers/recursos gerados pelo SGDK 2.11 se os `IMAGE` usados estão comprimidos e se mapas e tilesets têm exatamente as dimensões esperadas pelo runtime.
3. Comparar com a ROM âncora anterior que registrou `stage_ready=1`; recuperar primeiro a rota fixa conhecida antes de retomar a complexidade de streaming.
4. Capturar novamente o hash corrigido no BlastEm. O gate visual exige cenário visível, e o gate temporal exige cadência estável em 1200 quadros com áudio.

Até esses passos passarem, ambas as rotas são experimentais e bloqueadas para promoção.


## Captura da guarda corrigida — resultado parcial

ROM `8bf3b933943ad4cda3292ef3952d76ad2c53c1c9ef6f0eae1022dae618f02890`; sessão `out/mugenesis_evidence/piece_stream_guard/sessions/blastem-linux-20260927T105449Z-1338066`. Build concluído. Screenshot inspecionado: cenário presente com jogadores/HUD, mas cores erradas e artefatos nas barras inferiores. Bundle rejeitado: vlab_block_missing, artifact_missing:vdp_dump, artifact_missing:runtime_metrics. Não sustenta teste completo, movimento, orçamento ou FPS.

Causa concreta adicional: `source_stream_pattern_atlas.png` tem paleta diferente de `source_anchor_8_bleed.png`, mas `FIGHT_STAGE_init` carrega `img_suzaku_anchor.palette`. Índice1 do atlas é (102,136,136), enquanto a âncora fornece (34,68,102). A guarda corrigida apenas expôs esse defeito antes invisível. Próxima correção deve vincular explicitamente a paleta do atlas e conferir todos os índices, sem confundir o problema com perda inevitável do VDP.

Ainda investigar separadamente o tempo até telemetria, alinhamento de scroll por linha versus origem comum da tile-row, ordem de vscroll far/near, overlay do HUD e restauração BGFX. O piso isolado em BG_B permite testar perspectiva original sem congelar suas linhas sob a barra. Não promover o streaming completo antes desses testes.
