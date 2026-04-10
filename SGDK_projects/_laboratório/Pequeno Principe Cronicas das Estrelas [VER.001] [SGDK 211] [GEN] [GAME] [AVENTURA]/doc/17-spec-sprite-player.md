# 17 - Especificacao do Sprite do Player

**Versao:** 1.0
**Data:** 2026-03-16
**Contexto:** Fase 1 — Producao de assets para substituir player procedural

> Este documento define especificacoes tecnicas completas do sprite do Pequeno Principe
> para planetas e viagens, sem criar arquivos. Serve para orientar a producao e integracao.

---

## 1. IDENTIDADE VISUAL (referencia doc/08-bible-artistica.md)

- Corpo pequeno
- Cabelo dourado
- Casaco verde
- Cachecol amarelo como assinatura de movimento
- Contorno sepia (nunca preto puro) — regra de doc/15-diretrizes-producao-assets.md

---

## 2. SPRITE DO PLAYER — PLANETAS

### 2.1. Dimensoes e grid

| Parametro | Valor | Justificativa |
|-----------|-------|---------------|
| Tamanho maximo por frame | 32x32 px (4x4 tiles) | Budget doc/13-spec-cenas.md: player max 16 tiles (4x4) |
| Bounding box recomendado | 24x24 ou 24x32 px | Economia de tiles; multiplo de 8 |
| Grid | 8x8 pixels | Obrigatorio SGDK |
| Escala de exportacao | 1x | Nunca 2x ou 4x |

### 2.2. Animacoes minimas (planetas)

| Animacao | Frames | Descricao | Estados do PlayerController |
|----------|--------|------------|-----------------------------|
| idle | 2–3 | Respiração suave, parado | onGround && !moving |
| walk | 4 | Ciclo de passo | onGround && moving |
| jump | 3 | Subida, apice, queda | !onGround |
| glide | 2 | Cachecol e corpo em pose de planar | gliding |
| interact | 2 | Inclinar-se, tocar/olhar o marco | interacting |

**Total bruto:** ~13–15 frames. Reuso agressivo de tiles entre frames para manter ≤ 16 tiles unicos ativos por cena.

### 2.3. Paleta (PAL2 dedicada)

| Indice | Uso | Valor VDP (exemplo) |
|--------|-----|---------------------|
| 0 | Transparencia | #FF00FF (magenta) |
| 1 | Pele | (7,6,5) |
| 2 | Cabelo dourado | (7,6,2) |
| 3 | Casaco verde | (2,5,2) |
| 4 | Cachecol amarelo | (7,7,2) |
| 5 | Contorno sepia | (2,1,0) |
| 6–15 | Sombras, detalhes, dithering | Tons da mesma familia |

**Regras:** Contorno sepia em todas as bordas. Dithering 1x1 ou 2x2 para textura de giz. Cores mapeadas para grade 9 bits do VDP (0x00, 0x22, ..., 0xEE).

### 2.4. Orcamento de tiles e DMA

| Recurso | Limite | Nota |
|---------|--------|------|
| Tiles unicos ativos | ≤ 16 | Reuso entre frames |
| Tiles que mudam por frame | ≤ 8 | Animacao de walk/jump |
| DMA por frame (animacao) | ≤ 128 bytes | 8 tiles x 32 bytes (4bpp) = 256 bytes max; amortizar para ~128 |
| Sprites HW (corpo) | 3–4 | Meta-sprite 2x3 ou 3x2 |

### 2.5. Declaracao SGDK futura (conceito)

```
SPRITE spr_prince_planet "gfx/player/prince_planet.png" 4 4 NONE 0 NONE NONE
```

Ou, se bounding box menor:

```
SPRITE spr_prince_planet "gfx/player/prince_planet.png" 3 4 NONE 0 NONE NONE
```

Paleta: `pal_prince` ou derivada de `pal_sprite_stage`; mapeada em PAL2 via codigo.

---

## 3. SPRITE DO PLAYER — VIAGENS

### 3.1. Variantes por viagem (v2.0)

Cada viagem pode ter sprite proprio:
- Montado em estrela (Viagem A, E)
- Com rede (Viagem B)
- Balancando (Viagem C)
- Deslizando (Viagem D)
- etc.

### 3.2. Especificacao comum

| Parametro | Valor |
|-----------|-------|
| Tiles max por variante | 16 |
| Sprites HW | 4 |
| Paleta | Mesma base de player (PAL2) |

### 3.3. Variante para Travel atual (slice)

Para o slice atual, a cena Travel **oculta** o player. Quando as 11 viagens forem implementadas, cada uma carregara sua variante. Por ora, definir uma variante generica "principe voando" para reuso em Travel D e E:

- 1 sprite sheet: principe visao lateral ou traseira, 2 frames (normal + tropeco)
- Max 16 tiles

### 3.4. Declaracao SGDK futura (conceito)

```
SPRITE spr_prince_travel_d "gfx/player/prince_travel_d.png" 2 2 NONE 0 NONE NONE
SPRITE spr_prince_travel_d_stumble "gfx/player/prince_travel_d_stumble.png" 2 2 NONE 0 NONE NONE
```

---

## 4. CACHECOL (Scarf)

### 4.1. Especificacao

| Parametro | Valor |
|-----------|-------|
| Tamanho | 8x8 px (1 tile) |
| Variacoes | 1 ou 2 (cores alternativas para vento) |
| Paleta | PAL2 ou PAL3 (compartilhada com player) |
| Uso | 5 segmentos em planetas, 3 em viagens |

### 4.2. Arte

- Forma alongada de cachecol (faixa)
- Cor amarela/dourada (identidade do heroi)
- Contorno sepia
- Dithering leve para textura

### 4.3. Declaracao SGDK futura (conceito)

```
SPRITE spr_scarf_segment "gfx/player/scarf_segment.png" 1 1 NONE 0 NONE NONE
```

---

## 5. HALO

### 5.1. Especificacao

| Parametro | Valor |
|-----------|-------|
| Tamanho | 16x16 px (2x2 tiles) |
| Efeito | VDP Hilight mode clareia a area |
| Arte | Sem halo "pintado" — cores medias; o VDP gera o brilho |

### 5.2. Arte

- Desenhar em tons medios (index 4–8) para que o highlight do VDP crie o brilho
- Forma circular ou oval suave
- Dithering nas bordas para transicao suave
- Contorno nao necessario (o halo e suave)

### 5.3. Declaracao SGDK futura (conceito)

```
SPRITE spr_halo_quad "gfx/effects/halo_quad.png" 2 2 NONE 0 NONE NONE
```

---

## 6. MATRIZ DE FRAMES (planetas)

Para orientar o artista, mapeamento estado → frame:

| Estado | Condicao | Frame sugerido |
|--------|----------|----------------|
| idle | onGround, vx == 0 | 0 ou 1 |
| walk | onGround, vx != 0 | 2–5 (ciclo) |
| jump | !onGround, vy < 0 | 6 (subida) |
| jump | !onGround, vy >= 0 | 7 (queda) |
| glide | gliding | 8–9 |
| interact | interacting | 10–11 |

FacingLeft: usar H-flip do sprite, nao duplicar frames.

---

## 7. CHECKLIST PRE-PRODUCAO

Antes de entregar arte do player:

- [ ] PNG indexado, 16 cores, index 0 = #FF00FF
- [ ] Dimensoes multiplo de 8
- [ ] Contorno sepia, sem preto puro
- [ ] Cores na grade VDP 9 bits
- [ ] Bounding box recortado (sem tiles vazios)
- [ ] Barra de paleta numerada (0–15) com hex
- [ ] Contagem de tiles unicos documentada

---

## 8. REFERENCIAS

- `doc/08-bible-artistica.md` — Identidade do heroi
- `doc/13-spec-cenas.md` — Budget do player (secao 2)
- `doc/15-diretrizes-producao-assets.md` — Regras tecnicas
- `src/game/player.c` — Player_render, estados
