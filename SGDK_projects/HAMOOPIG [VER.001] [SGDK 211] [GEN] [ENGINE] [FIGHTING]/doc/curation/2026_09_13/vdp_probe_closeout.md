# Probe VDP/DMA/SAT — 2026-09-13

## Identidade

- ROM: `out/rom.bin`
- SHA-256: `ae6f5dab51c6c50b9e5ad94315f2bf8d89dcedfef724b83f6ab41277c59c1a62`
- Build: wrapper SGDK 2.11, exit 0.
- Sessão BlastEm: `out/emulator_evidence/visual_ko_20260914T000840Z/`
- SRAM: `userdata/blastem/rom/save.sram`, bloco HPRB em `0x500`.
- Decoder: `rascunho/temporario/analyze_hprb_probe.py`; relatório completo em
  `out/logs/hprb_probe_report_20260914_long.json`.

## Medição real

O probe foi chamado depois de `SPR_update()` e antes de
`SYS_doVBlankProcess()`, acumulando o pior valor da sessão.

| Métrica | Pico | Referência | Leitura |
|---|---:|---:|---|
| DMA pendente por quadro | 10.064 bytes | ~7.782 bytes NTSC H40 | acima do envelope |
| links VDP de sprite | 70 | 80 | dentro |
| sprites na mesma scanline | 12 | 20 | dentro |
| sprites ativos SGDK | 39 | informativo | observado |
| amostras | 5.250 | — | janela longa |

O pico DMA foi localizado no frame 3480; o pico de scanline ocorreu no frame
3158. A inspeção do vídeo mostra o impacto grande/KO (`spr_spark3`) no primeiro
instante e a pose de combate/efeito no segundo; esse trecho é o alvo do recuo.

## Comparação PAL

Uma janela curta PAL (`visual_ko_20260914T001135Z`) na mesma ROM registrou
1.950 amostras: DMA máximo 7.984 B contra o envelope PAL de aproximadamente
17 KiB, 38 links VDP, 8 sprites/scanline e 22 sprites ativos. O laudo PAL é
`cabe`; o recuo permanece necessário para o pior quadro NTSC.

Relatório PAL: `out/logs/hprb_probe_report_20260914_pal_latest.json`.

### Decisão

Eixo técnico: **cabe com recuo**. A pressão de sprites está dentro do limite,
mas o pior DMA excede o envelope NTSC. O recuo recomendado é reduzir ou
parcelar uploads de tiles de animação/efeitos (janela ativa, preload em estado
de loading ou fila menor) antes de qualquer promoção visual. Não foi usado
`SPR_getUsedVDPSprite()` como proxy de scanline; os dois eixos foram medidos
separadamente.

O primeiro finalizador de evidências rejeitou este pacote por um screenshot
precoce preto (`00_select.png`), não por divergência de ROM. A medição HPRB
continua rastreável pelo SRAM e pelo hash acima, mas permanece sem selo
canônico até uma captura limpa ser refeita.

## Atribuição HPRB v3 (2026-09-14)

Build diagnóstico `8544c31dc7ad4edb42dbdf84585499837c705c692ce90696f86180d4da5b8214`
mediu a fila imediatamente antes e depois de `SPR_update()`. Na captura
`visual_ko_20260914T003949Z`, o total continuou em 10.064 B (frame 1.790),
com delta máximo de sprites de 7.176 B e fila prévia máxima de 5.536 B.
Isso atribui a maior parcela aos uploads de sprites e orienta o próximo ciclo
para preload/janela ativa de frames. A ROM é diagnóstica; não altera o veredito
`cabe com recuo` nem promove budget.
### Comparação PAL v3

PAL repetido no mesmo HPRB v3 (`visual_ko_20260914T004240Z`) confirmou 7.984 B
totais, com 5.720 B de delta em `SPR_update()` e 5.536 B prévios; links 38,
scanline 8 e decisão `cabe`. Relatório: `out/logs/hprb_probe_report_20260914_attribution_pal.json`.

### Pico no mesmo frame — HPRB v5

Na captura `visual_ko_20260914T012538Z` (ROM `e91823b7…`), o frame 4.469
registrou 10.064 B: 4.576 B pré-fila e 5.488 B de `SPR_update()`. O marcador
de etapas encontrou 480 B na mensagem HUD; o restante é backlog de sprites
acumulado. Links VDP 54 e 9 sprites/scanline permaneceram dentro dos limites.
