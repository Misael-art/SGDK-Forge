# 18 - Especificacao de TILESETs dos Planetas

**Versao:** 1.0
**Data:** 2026-03-16
**Contexto:** Fase 1 — Producao de cenarios para substituir tiles procedurais

> Especificacoes de TILESET para B-612, Rei, Lampiao e Deserto, alinhadas aos budgets
> de `doc/13-spec-cenas.md` e regras de `doc/15-diretrizes-producao-assets.md`.

---

## 1. REGRAS COMUNS A TODOS OS PLANETAS

| Regra | Especificacao |
|-------|---------------|
| Formato | PNG ou BMP indexado, 16 cores |
| Index 0 | #FF00FF (transparencia) |
| Grid | 8x8 pixels |
| Cores | Grade VDP 9 bits |
| Contorno | Sepia, nunca preto puro |
| Dithering | Ordenado (xadrez, hachura) — doc/15 |

---

## 2. B-612

### 2.1. Identidade tecnica (doc/13-spec-cenas.md)

- Line scroll curvo simula curvatura do asteroide
- Palette cycling simula ciclo dia/noite
- Hilight mode cria halo de luz
- Budget cenario: **30 tiles** (excluindo marcos e player)

### 2.2. Tiles necessarios

| Tile | Funcao | Substitui | Notas |
|------|--------|-----------|-------|
| Sky base | Ceu preenchimento | PP_TILE_DITHER | Dithering 1x1 para textura |
| Sky variant | Variacao de ceu | - | Para parallax |
| Star | Estrela pequena | PP_TILE_STAR | 1–2 variantes |
| Trace | Linha decorativa | PP_TILE_TRACE | Estrelas/rastros |
| Sun | Sol/luz | PP_TILE_SUN | Usado em sky e orbit map |
| Ground fill | Solo do disco | PP_TILE_GROUND | Textura terra, dithering |
| Ground outline | Borda do disco | PP_TILE_HATCH | Ou borda integrada |
| Ground alt | Variacao | PP_TILE_GROUND_ALT | Para transicao |

### 2.3. Faixas de scroll (doc/15 secao 3.4)

| Linhas | Funcao | Comportamento |
|--------|--------|---------------|
| 0–40 | Ceu estatico | Sem scroll |
| 40–76 | Parallax lento | hscrollB |
| 76–184 | Scroll curvo | hscrollA + hscrollB |

**Arte:** Desenhar em faixas horizontais independentes. Cada faixa deve funcionar visualmente mesmo deslocada 8–16 px.

### 2.4. Paleta e cycling

- PAL0: ceu (6 cores de cycling) — indices 1–6 para gB612Cycle
- PAL1: solo, estrelas, tracos — tons quentes (laranjas, ocres, dourados)

### 2.5. Orcamento

| Recurso | Limite | Nota |
|---------|--------|------|
| Tiles unicos | ≤ 30 | Inclui sky, ground, star, trace, sun |
| Reuso | Maximo | H-flip para simetria |

### 2.6. Declaracao SGDK futura (conceito)

```
TILESET ts_b612_bg "gfx/planets/b612_bg.png" NONE NONE ROW
```

---

## 3. PLANETA DO REI

### 3.1. Identidade tecnica (doc/13-spec-cenas.md)

- Parallax multicamada (BG_A e BG_B)
- Column scroll para colunas do palacio (colunas 8–11)
- Budget cenario: **30 tiles**

### 3.2. Tiles necessarios

| Tile | Funcao | Substitui | Notas |
|------|--------|-----------|-------|
| Paper | Fundo base | PP_TILE_PAPER | Ceu |
| Dither | Textura parallax | PP_TILE_DITHER | BG_B |
| Hatch | Textura parallax | PP_TILE_HATCH | BG_B |
| Trace | Decoracao | PP_TILE_TRACE | BG_B |
| Tower | Coluna palacio | PP_TILE_TOWER | Coluna |
| Tower window | Janela | PP_TILE_TOWER_WINDOW | Alternancia |
| Beacon | Farol | PP_TILE_BEACON | Elemento decorativo |

### 3.3. Faixas de scroll

| Linhas | Velocidade | Comportamento |
|--------|------------|---------------|
| 32–72 | Lento | hscrollB |
| 72–112 | Medio | hscrollB + jitter |
| 112–184 | Rapido | hscrollB |
| Colunas 8–11 | Oscilacao | vscrollA (sine) |

### 3.4. Paleta

- PAL0: ceu (purpuras, vermelhos, dourados)
- PAL1: palacio (colunas, torre, beacon)

### 3.5. Orcamento

| Recurso | Limite |
|---------|--------|
| Tiles unicos | ≤ 30 | Reuso de colunas via H-flip |

### 3.6. Declaracao SGDK futura (conceito)

```
TILESET ts_king_bg "gfx/planets/king_bg.png" NONE NONE ROW
```

---

## 4. PLANETA DO LAMPIAO

### 4.1. Identidade tecnica (doc/13-spec-cenas.md)

- H-Int split na linha 95: ceu frio (topo) / zona quente (base)
- Heat wobble via line scroll local
- Hilight para halo da chama
- Budget cenario: **30 tiles**

### 4.2. Tiles necessarios

| Tile | Funcao | Substitui | Notas |
|------|--------|-----------|-------|
| Paper | Ceu | PP_TILE_PAPER | Topo frio |
| Ground alt | Solo | PP_TILE_GROUND_ALT | Disco |
| Hatch | Contorno | PP_TILE_HATCH | Disco |
| Beacon | Farol | PP_TILE_BEACON | Decorativo |

### 4.3. Paleta (H-Int split)

- **Paleta topo (linhas 0–95):** Cores frias (azul, cinza)
- **Paleta base (linhas 95–224):** Escura (lampiao apagado) ou iluminada (lampiao aceso)

O artista deve fornecer tiles que funcionem com ambas as paletas (mesmos indices, cores trocadas pela engine).

### 4.4. Orcamento

| Recurso | Limite |
|---------|--------|
| Tiles unicos | ≤ 30 |

### 4.5. Declaracao SGDK futura (conceito)

```
TILESET ts_lamp_bg "gfx/planets/lamp_bg.png" NONE NONE ROW
```

---

## 5. DESERTO DAS ESTRELAS

### 5.1. Identidade tecnica (doc/13-spec-cenas.md)

- Line scroll simula vento e miragem
- Cenario mais leve do slice
- Budget cenario: **30 tiles**

### 5.2. Tiles necessarios

| Tile | Funcao | Substitui | Notas |
|------|--------|-----------|-------|
| Dither | Ceu | PP_TILE_DITHER | Estrelas |
| Star | Estrela | PP_TILE_STAR | BG_B |
| Ring | Anel | PP_TILE_RING | BG_B |
| Dune | Duna | PP_TILE_DUNE | Areia |
| Ground alt | Solo alternativo | PP_TILE_GROUND_ALT | Alternancia |
| Trace | Decoracao | PP_TILE_TRACE | BG_A |

### 5.3. Faixas de scroll

| Linhas | Funcao |
|--------|--------|
| 56–120 | Vento (hscrollB) |
| 120–184 | Miragem (hscrollA) — hachura horizontal |

### 5.4. Paleta

- PAL0: ceu (beges, amarelos palidos, azul profundo)
- PAL1: areia, dunas

### 5.5. Orcamento

| Recurso | Limite |
|---------|--------|
| Tiles unicos | ≤ 30 |

### 5.6. Declaracao SGDK futura (conceito)

```
TILESET ts_desert_bg "gfx/planets/desert_bg.png" NONE NONE ROW
```

---

## 6. TABELA RESUMO

| Planeta | Tiles max | Paletas | Scroll | Efeito especial |
|---------|-----------|---------|--------|------------------|
| B-612 | 30 | PAL0 + PAL1 | Line curvo | Palette cycling, Hilight |
| Rei | 30 | PAL0 + PAL1 | Line + Column | Parallax 3 faixas |
| Lampiao | 30 | PAL0 + PAL1 | Line | H-Int split, Hilight |
| Deserto | 30 | PAL0 + PAL1 | Line | Miragem |

---

## 7. REFERENCIAS

- `doc/13-spec-cenas.md` — Budget por cena
- `doc/15-diretrizes-producao-assets.md` — Regras tecnicas
- `doc/08-bible-artistica.md` — Leitmotivs por planeta
- `src/game/planets.c` — Planet_draw*Base
