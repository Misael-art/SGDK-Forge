# 10 - Memory Bank — LIVE_BAR_FR2

**Ultima atualizacao:** 2026-08-29
**Fase:** laboratorio F-R2 fase 2 (lineart nativo 48x64)
**lab_not_delivery:** true

## O que e

Fixture da barra viva, axioma R2: PAL0 jogador, PAL1 inimigo, PAL2 cais,
PAL3 FX folga. Nao e vertical slice nem AAA.

## Fontes

- Concept Imagine: `data/source_art/{hero,thug,dock}_source.jpg`
- Construction drawings: `data/source_art/{hero,thug}_lineart_source.jpg`
- Native lineart: `tools/build_lineart_blocking_1px.py` → `res/sprites/{hero,thug}_48x64.png`
- Downscale v001: `data/processed/obsolete_downscale/` (`obsolete_for_generation_source`)

## Status

- documentado: sim
- implementado: sim (`src/main.c` + lineart 48x64)
- buildado: sim (`out/rom.bin` 131072 B, sha256 `4c07c842ab5509c79a05743836e663ffcb9bb1f5d3f359e25ee8069749f5642d`)
- testado_em_emulador: parcial — BlastEm Linux screenshot + SRAM + semantic gate `passed` (`blastem-linux-20260829T140943Z-1899126`); bundle canonico rejeitado (`vlab_block_missing`, `vdp_dump` ausente)
- validado_budget: nao
- ready_for_aaa: false
- live_scene_bar: `needs_review` (R2 visivel; sprites nativos em lineart; dock ainda quantize; rampa de material nao comecou)

Evidencia v002 (lineart): `out/evidence/blastem-linux-20260829T140943Z-1899126/screenshot.png`
Evidencia v001 (downscale, `obsolete_for_generation_source` para sprites): `out/evidence/blastem-linux-20260829T134220Z-1830965/screenshot.png`
