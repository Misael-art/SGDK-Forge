# 10 - Memory Bank — LIVE_BAR_FR2

**Ultima atualizacao:** 2026-08-29
**Fase:** laboratorio F-R2 (paleta com papel)
**lab_not_delivery:** true

## O que e

Fixture da barra viva, axioma R2: PAL0 jogador, PAL1 inimigo, PAL2 cais,
PAL3 FX folga. Nao e vertical slice nem AAA.

## Fontes

Imagine (Ramo A) → `data/source_art/*_source.jpg` → conversao 9-bit
indexada em `res/`. Sprites sao traducao por chroma+quantize, nao
redesenho elite. Status visual maximo: `needs_review`.

## Status

- documentado: sim
- implementado: sim (`src/main.c`)
- buildado: sim (`out/rom.bin` 131072 B, sha256 `292004cc024618828cbb6430d1e569fa3449abc38a5290c67428692965e63b59`)
- testado_em_emulador: parcial — BlastEm Linux screenshot + SRAM + semantic gate `passed`; bundle canonico rejeitado (`vlab_block_missing`, `vdp_dump` ausente)
- validado_budget: nao
- ready_for_aaa: false
- live_scene_bar: `needs_review` (R2 visivel; pixel nativo falhou — downscale)

Evidencia: `out/evidence/blastem-linux-20260829T134220Z-1830965/screenshot.png`
