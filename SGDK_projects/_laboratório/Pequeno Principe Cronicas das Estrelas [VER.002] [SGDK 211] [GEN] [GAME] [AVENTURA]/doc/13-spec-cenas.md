# Spec de Cenas — Pequeno Príncipe VER.002

## Budget VRAM Global

| Pool | Tiles | Bytes |
|------|-------|-------|
| Plano A (64×32) | 2048 refs | — |
| Plano B (64×32) | 2048 refs | — |
| Window (40×28) | 1120 refs | — |
| Sprites HW | 128 slots | — |
| TILE_USER_INDEX base | 0 | — |
| **Tiles disponíveis** | **1344** | **21504 bytes** |
| **DMA budget/frame** | — | **7680 bytes (60fps)** |

---

## CENA: B-612

### Budget
| Recurso | Alocado | Máx | Status |
|---------|---------|-----|--------|
| Tiles BG | 320 | 400 | ok |
| Tiles FG | 128 | 256 | ok |
| Sprites HW | 12 | 20 | ok |
| DMA/frame | 3200 bytes | 7680 | ok |
| Paletas | PAL0 (bg) + PAL1 (player) + PAL2 (fx) | 4 | ok |

### Técnicas VDP ativas
- `HSCROLL_LINE` + `VSCROLL_PLANE` — line scroll para curvatura do planeta
- H-Int na linha 192: split entre planeta e HUD
- Palette cycling PAL0 (céu): rotação a cada 4 frames entre 4 variações
- Shadow/Highlight: PAL3 com cores de sombra para borda do planeta

### Scroll
- hscrollA[y]: `sinFix16(frame * 2 + y * 3) >> 4` — leve ondulação do terreno
- hscrollB[y]: `sinFix16(frame + y * 2) >> 5` — parallax de nuvens
- vscroll: fixo, sem column scroll nesta cena

### FX de Assinatura (Experimental Override)
- H-Int a cada linha para criar gradiente de pôr do sol no céu (16 trocas de paleta por frame)
- Custo: ~1600 ciclos M68K por frame (15% da DMA budget) — aceito como Signature Moment

### Sprites
- Player: 4×4 tiles (32×32) — `SPR_FLAG_AUTO_VRAM_ALLOC`
- Scarf[5]: 1×1 tile (8×8) cada — 5 sprites
- Rosa: 2×2 tiles (16×16) — posição fixa
- HUD elements: via Window Plane (não usa sprites)

---

## CENA: Planeta do Rei

### Budget
| Recurso | Alocado | Máx | Status |
|---------|---------|-----|--------|
| Tiles BG (sky) | 256 | 512 | ok |
| Tiles FG (trono) | 192 | 300 | ok |
| Sprites HW | 8 | 20 | ok |
| DMA/frame | 4096 bytes | 7680 | ok |

### Técnicas VDP ativas
- `VSCROLL_COLUMN` — scroll por coluna de tiles (Plano A)
- `HSCROLL_LINE` no Plano B — parallax de nuvens
- 3 camadas de parallax: sky (velocidade 1), clouds (velocidade 2), mountains (velocidade 4)
- Window Plane na linha 176: HUD isolado

### Scroll
- vscrollA[col]: `cameraX / (col + 2)` — parallax colunar suave
- hscrollB[y]: `cameraX * 3 / 4` — bg uniforme mais lento
- Velocidade câmera: `fix32ToInt(camX)` avança com input

---

## CENA: Travel A — Pseudo-3D Space Harrier

### Budget
| Recurso | Alocado | Máx | Status |
|---------|---------|-----|--------|
| Tiles floor (gerados) | 64 | 128 | ok |
| Sprites estrelas | 32 | 48 | ok |
| Sprites player | 4 | 8 | ok |
| DMA/frame | 5120 bytes | 7680 | ok |

### Técnicas VDP ativas
- `HSCROLL_LINE` no Plano B: floor perspective a cada linha
- Linha do horizonte: y = 112
- Convergência: `hscroll[y] = (y - 112) * (frame / 2)` — perspectiva linear
- Escala de sprites por Z: tabela pré-calculada `scale_lut[256]`

### Floor line scroll formula
```c
// y de 112 a 224 = floor
// y de 0 a 112 = sky (fixo, estrelas)
s16 perspective = (s16)(y - 112) * travelFrame / 256;
hscrollB[y] = (y >= 112) ? perspective : 0;
```

### Asteroides
- 8 asteroides máx em cena
- Posição x,y,z em fix32, projetado: `screenX = (worldX << 8) / z`
- Detecção colisão: box 16×16

---

## CENA: Planeta do Acendedor (H-Int hardcore)

### Técnicas VDP ativas
- H-Int a cada linha do céu (y=0 a y=160): alternar PAL0 entre "dia" e "noite"
- A cada 60 frames: 1 ciclo completo (acender + apagar)
- Rate de H-Int: 1 (interrupt a cada scanline)
- Cost: ~220 ciclos por H-Int = 220×160 = 35200 ciclos (28% do budget)

### FX de Assinatura
- Linha de split varia suavemente seguindo posição do acendedor
- Quando jogador acerta timing: flash de paleta branca (2 frames) + PCM chime

---

## CENA: Geógrafo (MAP API)

### Budget MAP
- Mapa: 512×224 pixels (64×28 tiles) — horizontal scroll
- `MAP_create()` com tileset de 192 tiles únicos
- Scroll: `MAP_scrollTo(mapHandle, cameraX, 0)` a cada frame
- Camera bounds: [0, 512-320] = [0, 192] pixels

---

## HUD (Window Plane — todas as cenas)

```
Linha Window split: y = 196 (linhas 196-223 = 7 tiles = Window)
Window tiles:       40 × 7 = 280 tiles
Conteúdo:
  - Indicador de planeta (ícone + nome): col 0-9, row 0
  - Dica de ação (A=Interagir / C=Pular): col 10-29, row 0
  - Indicador de codex desbloqueados: col 30-39, row 0
  - Caixa de diálogo: rows 1-6 (quando ativa)
```

---

## Painel de Status por Cena

| Cena | documentado | implementado | buildado | testado | budget_ok |
|------|-------------|--------------|----------|---------|-----------|
| B-612 | sim | sim | pendente | pendente | ok |
| Rei | sim | sim | pendente | pendente | ok |
| Vaidoso | sim | parcial | pendente | pendente | ok |
| Bêbado | sim | parcial | pendente | pendente | ok |
| Contador | sim | placeholder | pendente | pendente | ok |
| Acendedor | sim | sim | pendente | pendente | ok |
| Geógrafo | sim | sim | pendente | pendente | ok |
| Serpente | sim | placeholder | pendente | pendente | ok |
| Deserto | sim | placeholder | pendente | pendente | ok |
| Jardim | sim | placeholder | pendente | pendente | ok |
| Poço | sim | placeholder | pendente | pendente | ok |
| B-612 Ret | sim | parcial | pendente | pendente | ok |
| Travel A | sim | sim | pendente | pendente | ok |
| Travel B-K | sim | placeholder | pendente | pendente | futuro |
