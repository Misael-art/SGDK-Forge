# 10 - Memory Bank — LIVE_BAR_FR2

**Ultima atualizacao:** 2026-08-29
**Fase:** laboratorio F-R2 fase 2 (cais nativo 8x8 + sprites coloridos)
**lab_not_delivery:** true

## O que e

Fixture R2: PAL0 jogador, PAL1 inimigo, PAL2 cais, PAL3 FX folga.

## Fontes

- Concept Imagine: `data/source_art/{hero,thug,dock}_source.jpg`
- Sprites: lineart + color blocking nativos 48x64
- Cais: `tools/build_native_dock.py` (vocabulario 8x8, PAL2)
- Quantize v001: `data/processed/obsolete_downscale/` (nao e fonte)

## Status

- documentado: sim
- implementado: sim
- buildado: sim (`out/rom.bin` 131072 B, sha256 `2411a37d0472f59aaccf1228ec3811b5ef0128ee97ceb350b27ccff70663b3ed`)
- testado_em_emulador: parcial — BlastEm screenshot + SRAM + semantic gate `passed` (`blastem-linux-20260829T145400Z-2004886`); bundle canonico rejeitado
- ready_for_aaa: false
- live_scene_bar: `needs_review` (pixel nativo da cena passou; motion falhou; compare_flat)

Evidencia v004 (cais nativo): `out/evidence/blastem-linux-20260829T145400Z-2004886/screenshot.png`
