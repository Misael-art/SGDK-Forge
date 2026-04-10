# 19 - Especificacao de TILESETs para UI e Travel

**Versao:** 1.0
**Data:** 2026-03-16
**Contexto:** Fase 1 — Assets leves para telas de texto e cena Travel

> TILESETs compartilhados com reuso maximo e paletas consistentes com gUiPalette.
> Prioridade baixa na Fase 1 (apos player e planetas).

---

## 1. CENA TRAVEL (Cena atual do slice)

### 1.1. Budget (doc/13-spec-cenas.md)

| Recurso | Alocado | Usado (atual) |
|---------|---------|---------------|
| Tiles VRAM | 30 | ~20 procedurais |
| DMA/frame | 1000 bytes | ~200 bytes |
| Sprites HW | 0 | 0 |

### 1.2. Elementos a substituir

| Elemento | Tiles procedurais | Funcao |
|----------|-------------------|--------|
| Ceu | PP_TILE_PAPER | Render_drawSky |
| Estrelas | PP_TILE_STAR, PP_TILE_TRACE | BG_B |
| Discos (planetas) | PP_TILE_GROUND, PP_TILE_GROUND_ALT, PP_TILE_HATCH | Render_drawDisc |
| Sol/Anel | PP_TILE_SUN, PP_TILE_RING | Orbit map |
| Painel | PP_TILE_PAPER, PP_TILE_HATCH, PP_TILE_DITHER, PP_TILE_FILL | Render_drawPanel |

### 1.3. Especificacao do TILESET Travel

| Tile | Funcao | Substitui |
|------|--------|-----------|
| Sky | Ceu espaco | PP_TILE_PAPER |
| Star | Estrela | PP_TILE_STAR |
| Trace | Rastro | PP_TILE_TRACE |
| Planet fill | Disco planeta | PP_TILE_GROUND (2 variantes) |
| Planet outline | Contorno | PP_TILE_HATCH |
| Sun | Sol/luz | PP_TILE_SUN |
| Ring | Anel | PP_TILE_RING |

**Paleta:** Alinhada a gTravelPal0 e gTravelPal1 (ou substituir por paletas de asset).

**Orcamento:** ≤ 20 tiles unicos.

### 1.4. Declaracao SGDK futura (conceito)

```
TILESET ts_travel_bg "gfx/travel/travel_bg.png" NONE NONE ROW
```

---

## 2. TELAS DE UI (Title, Story, Pause, Codex, Credits, Boot)

### 2.1. Budget compartilhado (doc/13-spec-cenas.md)

| Recurso | Alocado |
|---------|---------|
| Tiles VRAM | Font SGDK + ~10 decorativos |
| Paletas | PAL0 |
| DMA/frame | < 200 bytes |
| Scroll | Nenhum |

### 2.2. Elementos comuns

Todas as telas usam:
- `Render_drawPanel`, `Render_drawTextScreen`, `Render_drawPresentationBase`
- Tiles: PP_TILE_PAPER, PP_TILE_DITHER, PP_TILE_HATCH, PP_TILE_FILL
- Render_drawDisc, Render_drawOrbitMap: PP_TILE_GROUND, PP_TILE_GROUND_ALT, PP_TILE_HATCH, PP_TILE_SUN, PP_TILE_RING, PP_TILE_STAR, PP_TILE_TRACE

### 2.3. TILESET unico de UI

Um unico pacote de decoração reutilizavel:

| Tile | Funcao | Uso |
|------|--------|-----|
| Paper | Fundo solido | Painel, texto |
| Dither | Borda/textura | Painel |
| Hatch | Borda superior/inferior | Painel |
| Fill | Preenchimento | Painel |
| Ground | Disco | Title, Story, Credits |
| Ground alt | Disco alternativo | Title |
| Sun | Sol/planeta ativo | Orbit map |
| Ring | Planeta | Orbit map |
| Star | Estrela | Orbit map |
| Trace | Linha | Orbit map |
| Beacon | Farol | Story |

**Total:** ~16 tiles reutilizaveis.

### 2.4. Paleta

Consistente com `gUiPalette` (gPresentationPal0, gPresentationPal1):
- Tons neutros, pasteis
- Contorno sepia

### 2.5. Declaracao SGDK futura (conceito)

```
TILESET ts_ui_panels "gfx/ui/ui_panels.png" NONE NONE ROW
```

---

## 3. DIALOGOS (Window plane)

### 3.1. Uso atual

- `Dialogue_init` em `src/ui/dialogue.c`:
  - PP_TILE_DITHER (borda)
  - PP_TILE_PAPER (fundo)
  - PP_TILE_HATCH (topo/base)
  - PP_TILE_FILL (linha)

### 3.2. Estrategia

Reutilizar tiles do `ts_ui_panels` para os mesmos propositos. O dialogo usa PAL2 (gUiPalette). Os mesmos 4 tiles (paper, dither, hatch, fill) servem para painel e dialogo.

---

## 4. PRIORIDADE DE IMPLEMENTACAO

| Prioridade | Asset | Cenas afetadas |
|------------|-------|----------------|
| 1 (baixa) | ts_travel_bg | Travel |
| 2 (baixa) | ts_ui_panels | Boot, Title, Story, Pause, Codex, Credits, Dialogos |

**Nota:** Estes assets podem vir depois dos planetas e do player. A Fase 1 pode manter os tiles procedurais para Travel e UI se o budget de producao for limitado.

---

## 5. REFERENCIAS

- `doc/13-spec-cenas.md` — Budget Travel e telas de texto
- `src/render/render.c` — Render_drawTravelScene, Render_drawPanel, etc.
- `src/ui/dialogue.c` — Dialogue_init
