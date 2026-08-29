# 10 - Memory Bank — LIVE_BAR_FR2

**Ultima atualizacao:** 2026-08-29
**Fase:** laboratorio F-R2 fase 2 (color blocking sobre lineart 48x64)
**lab_not_delivery:** true

## O que e

Fixture da barra viva, axioma R2: PAL0 jogador, PAL1 inimigo, PAL2 cais,
PAL3 FX folga. Nao e vertical slice nem AAA.

## Fontes

- Concept Imagine: `data/source_art/{hero,thug,dock}_source.jpg`
- Construction drawings: `data/source_art/{hero,thug}_lineart_source.jpg`
- Native lineart: `tools/build_lineart_blocking_1px.py`
- Color blocking: `tools/build_color_blocking.py` → `res/sprites/{hero,thug}_48x64.png`
- Downscale v001: `data/processed/obsolete_downscale/` (`obsolete_for_generation_source`)

## Status

- documentado: sim
- implementado: sim (`src/main.c` + lineart + color blocking)
- buildado: sim (`out/rom.bin` 131072 B, sha256 `f694b841e8f1450b481d45b5be5a35ac1a25eb3dc96fe5d24e00a592e10c73f9`)
- testado_em_emulador: parcial — BlastEm Linux screenshot + SRAM + semantic gate `passed` (`blastem-linux-20260829T142829Z-1942264`); bundle canonico rejeitado (`vlab_block_missing`, `vdp_dump` ausente)
- validado_budget: nao
- ready_for_aaa: false
- live_scene_bar: `needs_review` (R2 visivel; sprites nativos com rampas; dock ainda quantize)

Evidencia v003 (color): `out/evidence/blastem-linux-20260829T142829Z-1942264/screenshot.png`
Evidencia v002 (lineart): `out/evidence/blastem-linux-20260829T140943Z-1899126/screenshot.png`
Evidencia v001 (downscale, obsolete): `out/evidence/blastem-linux-20260829T134220Z-1830965/screenshot.png`
