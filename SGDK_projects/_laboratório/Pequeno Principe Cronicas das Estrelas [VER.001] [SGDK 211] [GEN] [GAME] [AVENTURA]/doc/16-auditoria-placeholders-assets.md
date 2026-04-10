# 16 - Auditoria de Placeholders e Assets Reais

**Versao:** 1.0
**Data:** 2026-03-16
**Contexto:** Fase 1 — Substituicao de tiles procedurais por assets reais (Yoshi's Island Style)

> Este documento mapeia precisamente o que e procedural e o que e asset real no slice atual,
> por cena, para orientar a producao e integracao dos novos graficos.

---

## 1. TILES PROCEDURAIS (Gerados em `Render_buildTiles`)

### 1.1. Inventario completo

| Constante | Indice VRAM | Tiles | Uso | Plano |
|-----------|-------------|-------|-----|-------|
| PP_TILE_PAPER | BASE+0 | 1 | Fundo solido claro | BG_A, BG_B, WINDOW |
| PP_TILE_DITHER | BASE+1 | 1 | Xadrez 1x1 (textura) | BG_A, BG_B, WINDOW |
| PP_TILE_HATCH | BASE+2 | 1 | Cruz diagonal (borda) | BG_A, BG_B |
| PP_TILE_STAR | BASE+3 | 1 | Estrela pequena | BG_B |
| PP_TILE_GROUND | BASE+4 | 1 | Solo com borda | BG_A, BG_B |
| PP_TILE_GROUND_ALT | BASE+5 | 1 | Solo alternativo | BG_A, BG_B |
| PP_TILE_CROWN | BASE+6 | 1 | Coroa (nao usado em draw) | - |
| PP_TILE_TOWER | BASE+7 | 1 | Coluna do palacio | BG_A |
| PP_TILE_TOWER_WINDOW | BASE+8 | 1 | Janela da torre | BG_A |
| PP_TILE_LAMP | BASE+9 | 1 | Poste do lampiao (nao usado) | - |
| PP_TILE_BEACON | BASE+10 | 1 | Farol/beacon | BG_A |
| PP_TILE_DUNE | BASE+11 | 1 | Duna de areia | BG_A |
| PP_TILE_RING | BASE+12 | 1 | Anel/planeta | BG_B |
| PP_TILE_FILL | BASE+13 | 1 | Preenchimento painel | BG_A, WINDOW |
| PP_TILE_SUN | BASE+14 | 1 | Sol/luz | BG_A, BG_B |
| PP_TILE_TRACE | BASE+15 | 1 | Traco/linha decorativa | BG_A, BG_B |
| PP_TILE_PLAYER | BASE+16 | 6 | Corpo do principe (2x3 sprites) | Sprites |
| PP_TILE_SCARF | BASE+22 | 1 | Segmento do cachecol | Sprites |
| PP_TILE_HALO | BASE+23 | 4 | Quadrantes do halo (2x2) | Sprites |

**Total procedural:** 27 tiles (`PP_TOTAL_GENERATED_TILES`)

**Nota:** PP_TILE_CROWN e PP_TILE_LAMP sao construidos em `Render_buildTiles` mas nao aparecem em nenhuma chamada de draw no codigo atual. PP_TILE_LAMP seria usado por `Render_drawLamppost`, que nao e invocado por nenhum planeta (o lampiao e o marco PP_TILE_LAMP_MARK como sprite).

---

## 2. ASSETS REAIS (Carregados via ResComp)

### 2.1. TILESETs de marcos

| Recurso | Arquivo | Tiles | VRAM Base | Uso |
|---------|---------|-------|-----------|-----|
| ts_rose_mark | gfx/landmarks/rose_mark.bmp | 4 | PP_TILE_ROSE_MARK | Marco B-612 (rosa) |
| ts_throne_mark | gfx/landmarks/throne_mark.bmp | 4 | PP_TILE_THRONE_MARK | Marco Rei (trono) |
| ts_lamp_mark | gfx/landmarks/lamp_mark.bmp | 4 | PP_TILE_LAMP_MARK | Marco Lampiao |
| ts_desert_mark | gfx/landmarks/desert_mark.bmp | 4 | PP_TILE_DESERT_MARK | Marco Deserto |

**Total marcos:** 16 tiles

### 2.2. Paleta

| Recurso | Uso |
|---------|-----|
| pal_sprite_stage | PAL3 — sprites de player, cachecol, halo e marcos |

---

## 3. USO POR CENA

### 3.1. B-612 (Planeta-tutorial)

| Elemento | Tiles | Plano | Funcao |
|----------|-------|-------|--------|
| Ceu | PP_TILE_DITHER (fill) + PP_TILE_STAR/TRACE (estrelas) | BG_B | Render_drawSky |
| Sol | PP_TILE_SUN | BG_B | VDP_setTileMapXY |
| Disco planeta | PP_TILE_GROUND (fill), PP_TILE_HATCH (contorno) | BG_A | Render_drawDisc |
| Traces | PP_TILE_TRACE | BG_A | 2 posicoes |
| Player corpo | PP_TILE_PLAYER (6 tiles) | Sprites | Player_render |
| Cachecol | PP_TILE_SCARF (1 tile x 5 sprites) | Sprites | Player_render |
| Halo | PP_TILE_HALO (4 tiles, 2x2) | Sprites | Player_render |
| Marco rosa | PP_TILE_ROSE_MARK (4 tiles) | Sprites | Player_render |

**Tiles procedurais usados:** PAPER(0), DITHER, HATCH, STAR, GROUND, TRACE, SUN, PLAYER(6), SCARF, HALO(4) = 17 unicos + 4 marcos = 21 tiles ativos na cena.

### 3.2. Planeta do Rei

| Elemento | Tiles | Plano | Funcao |
|----------|-------|-------|--------|
| Ceu | PP_TILE_PAPER (fill) + PP_TILE_STAR/TRACE | BG_B | Render_drawSky |
| Parallax BG_B | PP_TILE_DITHER, PP_TILE_HATCH, PP_TILE_TRACE | BG_B | Loop em Planet_drawKingBase |
| Torre | PP_TILE_TOWER, PP_TILE_TOWER_WINDOW | BG_A | Render_drawTower |
| Beacon | PP_TILE_BEACON | BG_A | Render_drawBeacon |
| Player + cachecol | PP_TILE_PLAYER, PP_TILE_SCARF | Sprites | Player_render |
| Marco trono | PP_TILE_THRONE_MARK | Sprites | Player_render |

**Halo:** desabilitado nesta cena.

**Tiles procedurais usados:** PAPER, DITHER, HATCH, STAR, TRACE, TOWER, TOWER_WINDOW, BEACON, PLAYER(6), SCARF = 14 unicos + 4 marcos = 18 tiles.

### 3.3. Planeta do Lampiao

| Elemento | Tiles | Plano | Funcao |
|----------|-------|-------|--------|
| Ceu | PP_TILE_PAPER (fill) + estrelas | BG_B | Render_drawSky |
| Disco | PP_TILE_GROUND_ALT, PP_TILE_HATCH | BG_A | Render_drawDisc |
| Beacon | PP_TILE_BEACON | BG_A | Render_drawBeacon |
| Player + cachecol | PP_TILE_PLAYER, PP_TILE_SCARF | Sprites | Player_render |
| Halo | PP_TILE_HALO | Sprites | Player_render (quando lampLit) |
| Marco lampiao | PP_TILE_LAMP_MARK | Sprites | Player_render |

**Tiles procedurais usados:** PAPER, HATCH, GROUND_ALT, BEACON, PLAYER(6), SCARF, HALO(4) = 14 unicos + 4 marcos = 18 tiles.

### 3.4. Deserto das Estrelas

| Elemento | Tiles | Plano | Funcao |
|----------|-------|-------|--------|
| Ceu | PP_TILE_DITHER + estrelas | BG_B | Render_drawSky |
| Anel | PP_TILE_RING | BG_B | VDP_setTileMapXY |
| Dunas | PP_TILE_DUNE, PP_TILE_GROUND_ALT | BG_A | Render_drawDunes |
| Traces | PP_TILE_TRACE | BG_A | 2 posicoes |
| Player + cachecol | PP_TILE_PLAYER, PP_TILE_SCARF | Sprites | Player_render |
| Marco deserto | PP_TILE_DESERT_MARK | Sprites | Player_render |

**Halo:** desabilitado.

**Tiles procedurais usados:** DITHER, STAR, TRACE, RING, DUNE, GROUND_ALT, PLAYER(6), SCARF = 12 unicos + 4 marcos = 16 tiles.

### 3.5. Travel (Cena de transicao)

| Elemento | Tiles | Plano | Funcao |
|----------|-------|-------|--------|
| Ceu | PP_TILE_PAPER + estrelas | BG_B | Render_drawSky |
| Painel | PP_TILE_PAPER, PP_TILE_HATCH, PP_TILE_DITHER, PP_TILE_FILL | BG_A | Render_drawPanel |
| Orbit map | PP_TILE_SUN, PP_TILE_RING, PP_TILE_STAR, PP_TILE_TRACE | BG_B | Render_drawOrbitMap |
| Discos | PP_TILE_GROUND, PP_TILE_GROUND_ALT, PP_TILE_HATCH, PP_TILE_SUN, PP_TILE_RING | BG_A | Render_drawDisc |

**Player:** oculto (Player_hideSprites chamado antes de entrar em travel).

**Tiles procedurais usados:** PAPER, DITHER, HATCH, FILL, STAR, TRACE, GROUND, GROUND_ALT, SUN, RING = 10 unicos. Sem sprites de player.

### 3.6. Telas de texto (Boot, Title, Story, Pause, Codex, Credits)

| Tela | Tiles usados | Funcoes |
|------|--------------|---------|
| Boot | PAPER, DITHER, HATCH, FILL | Render_drawTextScreen |
| Title | PAPER, DITHER, HATCH, FILL, GROUND, GROUND_ALT | Render_drawTitleScene |
| Story | PAPER, DITHER, HATCH, FILL, GROUND, BEACON, SUN, TRACE | Render_drawStoryScene |
| Pause | PAPER, DITHER, HATCH, FILL, SUN, RING, STAR, TRACE | Render_drawPauseScreen |
| Codex | PAPER, DITHER, HATCH, FILL, SUN, RING, STAR, TRACE | Render_drawCodexScreen |
| Credits | PAPER, DITHER, HATCH, FILL, GROUND_ALT, SUN, RING, STAR, TRACE | Render_drawCreditsScreen |

**Dialogos (window plane):** PAPER, DITHER, HATCH, FILL — usados em todas as cenas de planeta quando dialogo ativo.

---

## 4. RESUMO DE ORCAMENTO ATUAL

| Cena | Tiles procedural | Tiles marcos | Total tiles | Sprites HW |
|------|------------------|--------------|-------------|------------|
| B-612 | 17 | 4 | 21 | 8 (corpo 1 + cachecol 5 + halo 1 + marco 1) |
| Rei | 14 | 4 | 18 | 7 (corpo 1 + cachecol 5 + marco 1) |
| Lampiao | 14 | 4 | 18 | 8 (corpo 1 + cachecol 5 + halo 1 + marco 1) |
| Deserto | 12 | 4 | 16 | 7 |
| Travel | 10 | 0 | 10 | 0 |
| Texto | ~10 | 0 | ~10 | 0 |

**Nota:** O corpo do player usa 1 meta-sprite de 2x3 tiles (SPRITE_SIZE(2,3)), referenciando PP_TILE_PLAYER que ocupa 6 tiles na VRAM. Os marcos usam SPRITE_SIZE(2,2) = 4 tiles cada.

---

## 5. PRIORIDADE DE SUBSTITUICAO (Fase 1)

1. **Alta:** Player (corpo + cachecol + halo) — impacto em todas as cenas de planeta.
2. **Alta:** Cenarios dos 4 planetas (B-612, Rei, Lampiao, Deserto).
3. **Media:** Cena Travel (discos e estrelas).
4. **Baixa:** Telas de texto e UI (painéis, bordas) — manter procedurais ou pacote unico leve.

---

## 6. REFERENCIAS

- `doc/13-spec-cenas.md` — Budget por cena
- `doc/15-diretrizes-producao-assets.md` — Regras tecnicas de arte
- `inc/project.h` — Definicoes PP_TILE_*
- `src/render/render.c` — Render_buildTiles, funcoes de draw
- `src/game/player.c` — Player_render, marcos
- `src/game/planets.c` — Planet_draw*Base
