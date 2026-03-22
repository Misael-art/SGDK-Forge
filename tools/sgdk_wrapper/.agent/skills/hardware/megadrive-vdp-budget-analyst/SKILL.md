---
name: megadrive-vdp-budget-analyst
description: Analisa VRAM, DMA, sprites, paletas, scroll e H-Int para hardware real do Mega Drive.
---

# Mega Drive VDP Budget Analyst

Use esta skill antes de aprovar efeitos visuais, assets, transicoes ou mudancas de render.

## Verifique sempre

- VRAM total e tiles residentes
- DMA por VBlank
- sprites por scanline
- total de links de sprite
- uso de PAL0-PAL3
- H-Int unico por frame
- custo de line scroll e column scroll

## Decisao

Responda sempre em um destes formatos:

- `cabe`
- `cabe com recuo`
- `nao cabe`

## Alertas classicos

- alpha blending real nao existe
- terceira camada de background nao existe
- DMA fora de VBlank exige justificativa forte
- shadow/highlight tem regras de prioridade e custo de paleta
