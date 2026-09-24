# Memory bank - Shadow Dancer Revisitado

## Estado operacional - 2026-09-21

- origem preservada em `SGDK_Engines/shadowdancer_revisitado`.
- copia ativa em `SGDK_projects/SHADOWDANCER_REVISITADO [VER.001] [SGDK 211] [GEN] [ENGINE] [BEAT_EM_UP]`.
- SGDK alvo: `sdk/sgdk-2.11`.
- contexto: `technical_demo`; teto atual: `technical_demo`.
- arte ativa: 9 simbolos de recurso; diagnostico sem blockers, com avisos de grid 9-bit.
- runtime convertido: input centralizado, fixed-point sem literais float, colisao com bounds, camera com dead zone.
- cache convertido: armazenamento estatico; `DMA_queueDma` no callback em vez de DMA imediato.
- build SGDK 2.11 concluido pela rota `linux_wine_bridge`; ROM em `out/rom.bin`, 524288 bytes, SHA-256 `ee071686940c7f2f853b3f3120f9f2baf8d1bc4e5e0d3aeaf8081501a725eb54`.
- snapshot de build e metadados dos 17 simbolos visuais registrados em `doc/changelog/`.
- auditorias de nome, contexto, higiene, metodologia, proveniencia procedural e grafo `.res` concluidas sem blockers.
- ultima validacao de recursos: 1 erro de closeout/claims e 10 avisos esperados por falta de BlastEm e gate visual; nenhum erro de compilacao ou recurso SGDK.
- estado operacional atualizado em `2026-09-21T04:10:29Z` apos a renomeacao para `BEAT_EM_UP`.
- revisao formal registrada em `out/logs/code_review_report.json`: `review_passed_with_risk`, com riscos restritos a evidencia BlastEm, budget DMA e semantica de colisao ainda nao observados em runtime.

## Claims permitidos

`documentado` para arquitetura e contratos; `implementado` para o codigo convertido; `buildado` somente quando a ROM nova existir; `testado_em_emulador` somente com evidencia BlastEm vinculada ao hash; nenhuma alegacao de AAA, audio ou release.

## Pendencias ordenadas

1. Reexecutar o validator completo apos o fechamento dos snapshots de changelog.
2. Capturar BlastEm e medir fila DMA/camera antes de promover status.
3. Registrar screenshot, SRAM e dump VDP vinculados ao hash da ROM.
