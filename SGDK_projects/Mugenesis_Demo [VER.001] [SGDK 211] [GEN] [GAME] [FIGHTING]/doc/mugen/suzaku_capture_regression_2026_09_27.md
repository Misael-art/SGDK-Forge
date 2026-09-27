# Suzaku: regressão dos candidatos de captura — 2026-09-27

## Veredito

Os dois candidatos chegaram à cena de luta no BlastEm, mas não inicializaram o cenário. O fundo aparece vazio e SRAM registra `stage_ready=0`. A captura válida como evidência de falha não transforma esses builds em ROM jogável com cenário.

## Builds observados

| Rota | SHA-256 da ROM | SRAM / resultado | Métricas VLAB | Bundle local |
|---|---|---|---|---|
| Streaming com sweep de câmera | `2c62c7f52c383954ad01dbd6d32dfd429576cfc4d095ba606b7de49ec8b97b19` | capacidade 456 tiles; residentes e pico 0; overflow 0; restaurações 0; `stage_ready=0` | 50/1200 quadros acima do orçamento; CPU máx. 124; snapshot de 59,9 FPS não prova cadência | `out/mugenesis_evidence/suzaku_stream/canonical` — sessão `blastem-linux-20260927T020859Z-1815492` |
| Estático em dois planos | `c1b03a491848803ccecc56c678b09c88c040069db132e61c6030610500788c9a` | `stage_ready=0`; restaurações 0; falhas de sprite 0; menor bloco contíguo 94 tiles | 82/1200 quadros acima do orçamento; CPU máx. 141; snapshot de 59,5 FPS não prova cadência | `out/mugenesis_evidence/suzaku_static_planes/canonical` — sessão `blastem-linux-20260927T022756Z-1860145` |

## Diagnóstico disponível

Na rota de streaming, o BGFX de 272 tiles não foi reservado no estado atual do alocador. A capacidade que sobrou foi 456 tiles. A conta anterior tratava o empréstimo como capacidade adicional, embora ele ocupe a mesma faixa de VRAM do pool-base; essa soma era inválida. O sweep, portanto, não testou movimento real do cenário: não houve cache residente nem mapa carregado.

Isso não explica por que a inicialização estática em dois planos também retornou falso. A causa dessa falha permanece aberta; não atribuir a compressão dos recursos nem outra condição sem observar os campos reais gerados e o motivo exato do retorno.

## Próximas ações

1. Adicionar telemetria de diagnóstico que informe, na própria captura, o código de retorno de `FIGHT_STAGE_init`, base VRAM, limite do pool de sprites, contagens de tiles e flags/dimensões dos recursos usados.
2. Verificar nos headers/recursos gerados pelo SGDK 2.11 se os `IMAGE` usados estão comprimidos e se mapas e tilesets têm exatamente as dimensões esperadas pelo runtime.
3. Comparar com a ROM âncora anterior que registrou `stage_ready=1`; recuperar primeiro a rota fixa conhecida antes de retomar a complexidade de streaming.
4. Capturar novamente o hash corrigido no BlastEm. O gate visual exige cenário visível, e o gate temporal exige cadência estável em 1200 quadros com áudio.

Até esses passos passarem, ambas as rotas são experimentais e bloqueadas para promoção.
