# 13 - Especificacao Tecnica por Cena — METAL_SLUG_URBAN_SUNSET

> Este documento define os limites tecnicos de cada cena.
> Nao altere sem ordem expressa do usuario.
> Toda mudanca de efeito visual deve respeitar estes budgets.

## Cena: METAL_SLUG_URBAN_SUNSET

| Recurso | Budget | Uso medido (build 2026-04-12 streaming) |
|---------|--------|-----------------------------------------|
| VRAM BG_B | 242 tiles | 242 tiles (IMAGE 128x224, PAL0) |
| VRAM BG_A Bank A | max 535 tiles | strip 0: 509 / strip 2: 533 |
| VRAM BG_A Bank B | max 535 tiles | strip 1: 363 / strip 3: 264 |
| **VRAM pior caso** | **1070 tiles** | **strips 1+2: 896 tiles (margem 174)** |
| SPR_initEx | 100 tiles reservados | debris=48 + player=32 = 80 usados |
| DMA por frame | line scroll 224 + strip swap (1 strip DMA por transicao) | ~17KB por strip swap |
| Sprites SAT | ate 8 links | 8 VDP sprites (6 debris + 2 player) |
| Paletas | 4 maximas | PAL0=BG_B, PAL1=BG_A, PAL2=debris, PAL3=player |
| Efeito dominante | line scroll BG_B + strip streaming BG_A | BG_B: ceu 1/8x, skyline 1/4x |
| **Scroll horizontal** | **264px** (584 - 320) | **panorama completa 584px via 4 strips** |

### Arquitectura de streaming (padrao BLAZE_ENGINE)

```
Panorama 584px = 4 strips IMAGE de 160px (ultimo: 104px + padding)
Strip 0: 509 tiles | Strip 1: 363 tiles | Strip 2: 533 tiles | Strip 3: 264 tiles

VRAM Layout (64x32, maps_addr=0xC000):
  System:   16 tiles (0-15)
  BG_B:    242 tiles (16-257)
  Bank A:  535 tiles (258-792)   ← strips pares (0, 2)
  Bank B:  535 tiles (793-1327)  ← strips impares (1, 3)
  Sprites: 100 tiles (1340-1439)
  Font:     96 tiles (1440-1535)
  VDP tables: 0xC000-0xFFFF

Logica: strip N → bank (N % 2). Max 2 strips simultaneos.
Tilemap: VDP_setTileMapEx no plano 64x32 (wrapping automatico).
Scroll: VDP_setHorizontalScroll(BG_A, -camPosX).
```

### Observacoes

- Streaming eliminou a restricao de VRAM para panoramas largas. A 584px com 1660 tiles totais, apenas 2 strips sao carregados por vez (max 896 tiles).
- `SPR_initEx(100)` em vez de 128 para acomodar os bancos. Margem de 20 tiles sobre o pico real (80).
- O plano VDP 64x32 (512px) actua como buffer circular. O strip 3 (colunas 60-72) wrapa sobre as colunas 0-8 do strip 0, que ja esta fora do viewport nesse ponto.
- DMA de strip swap: ~17KB por strip (worst case strip 2 = 17056 bytes). Cabe em ~2.5 VBlanks.

---

## Cena: PRE-GATE VISUAL

| Recurso | Budget | Uso atual |
|---------|--------|-----------|
| Transparencia indice 0 | obrigatoria em todo asset com alpha | implementada — indice 0 = magenta (255,0,255) em todos os assets |
| Resolucao alvo | 320x224 ou bbox validada | 320x224 confirmada |
| PNG format | 4bpp indexed, max 16 cores por paleta | validado em todos os assets (build 2026-04-12) |
| Evidencia BlastEm | screenshot + save.sram + visual_vdp_dump.bin | ROM gerada, aguardando teste visual |
| Status QA | 7 eixos completos | parcial — falta validacao visual em emulador |
