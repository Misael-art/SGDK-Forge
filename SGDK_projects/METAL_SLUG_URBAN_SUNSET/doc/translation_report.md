# Translation Report — art-translation-to-vdp

**Projecto:** METAL_SLUG_URBAN_SUNSET
**Source:** `res/data/source/source.png` (1113x627, editorial_board)
**Skill:** `art-translation-to-vdp`
**Tipo:** `scene_slice`

---

## Entradas

| Campo | Valor |
|-------|-------|
| source_image | `res/data/source/source.png` |
| translation_target | `scene_slice` |
| reference_profile | Metal Slug (arcade), Streets of Rage 2/3 (MD) |
| hardware_spec | Mega Drive VDP: 64KB VRAM, 4 paletas × 16 cores, 2 BG planes + sprites |
| intent_notes | Cena urbana pós-destruição ao pôr-do-sol com 3 camadas de profundidade |

---

## Semantic Parse Summary

- **Layout**: `editorial_board` com 5 classes de regiões
- **KEEP**: sky (512x114), city (595x256), debris (672x141)
- **DROP**: labels, mockup_preview, author_credits
- **Parsing completo**: ver `doc/semantic_parse_report.md`

---

## Palette Plans (curadoria manual semântica)

### PAL0 — BG_B Sky (15 cores + transparent)

| Idx | Cor (hex) | Papel Semântico |
|-----|-----------|----------------|
| 0 | FF00FF | Transparente |
| 1 | 000022 | Índigo profundo (topo do céu) |
| 2 | 220022 | Púrpura escuro |
| 3 | 440022 | Vinho profundo |
| 4 | 440000 | Castanho-vermelho escuro |
| 5 | 660000 | Vermelho profundo |
| 6 | 662200 | Vermelho-laranja escuro |
| 7 | 882200 | Vermelho |
| 8 | 882222 | Vermelho quente |
| 9 | AA4400 | Laranja escuro |
| 10 | AA6600 | Laranja |
| 11 | CC6600 | Laranja brilhante |
| 12 | CC8822 | Laranja quente |
| 13 | EEAA22 | Dourado |
| 14 | EECC66 | Ouro brilhante |
| 15 | EEEE88 | Ouro pálido (horizonte) |

**Lógica da rampa**: transição contínua de índigo escuro (topo) → vermelho → laranja → ouro (horizonte). Cada cor conquista o seu slot por função tonal na rampa atmosférica. Nenhuma cor repetida ou desperdiçada.

### PAL1 — BG_A City (15 cores + transparent)

| Idx | Cor (hex) | Papel Semântico |
|-----|-----------|----------------|
| 0 | FF00FF | Transparente (céu visível) |
| 1 | 000000 | Preto puro (outlines, sombra máxima) |
| 2 | 220000 | Near-black quente (sombra profunda) |
| 3 | 222200 | Oliva escuro (chão escuro) |
| 4 | 222222 | Cinza escuro (sombra fria, betão) |
| 5 | 442200 | Castanho escuro (sombra do tijolo) |
| 6 | 442222 | Castanho quente escuro (base de fachada) |
| 7 | 444444 | Cinza médio (betão, metal) |
| 8 | 664444 | Warm medium (face iluminada do tijolo) |
| 9 | 886644 | Castanho claro quente (areia, tijolo lit) |
| 10 | 886666 | Warm light (highlight do tijolo) |
| 11 | AA8866 | Areia clara (superfícies iluminadas) |
| 12 | CCAA66 | Ouro quente (base de luz de janela) |
| 13 | CCCCAA | Creme (superfície brilhante) |
| 14 | EECC66 | Ouro brilhante (luz de janela) |
| 15 | EEEE88 | Quente brilhante (highlight máximo) |

**Lógica**: 6 tons escuros para a massa de sombra urbana (dominante), 4 tons médios para materiais (tijolo, betão), 5 tons quentes para iluminação (janelas = pontos focais). A rampa garante 3 níveis por material: sombra → base → luz.

### PAL2 — Debris Sprites (15 cores + transparent)

| Idx | Cor (hex) | Papel Semântico |
|-----|-----------|----------------|
| 0 | FF00FF | Transparente |
| 1 | 000000 | Preto (silhueta base) |
| 2 | 220000 | Near-black quente |
| 3 | 222200 | Oliva escuro |
| 4 | 222222 | Cinza escuro |
| 5 | 442200 | Castanho escuro |
| 6 | 442222 | Warm dark brown |
| 7 | 444422 | Oliva médio |
| 8 | 664422 | Castanho médio |
| 9 | 664444 | Warm medium |
| 10 | 886644 | Castanho claro |
| 11 | 886622 | Ouro escuro |
| 12 | AA8844 | Warm highlight |
| 13 | AA8866 | Areia |
| 14 | CCAA66 | Aresta brilhante |
| 15 | EEAA66 | Highlight máximo |

**Lógica**: Dominância de escuros (80%+ da massa é silhueta). Poucos highlights nas arestas superiores simulam iluminação rasante do pôr-do-sol.

---

## Dithering Plan

| Layer | Estratégia |
|-------|-----------|
| BG_B Sky | SEM dithering — gradiente resolvido por bandas de cor sólida para máximo tile reuse |
| BG_A City | Dithering SUBTIL em transições de material (tijolo/betão) — funcional, não decorativo |
| Debris | SEM dithering — silhueta sólida com highlight de aresta |

---

## Layer Plan (resumo)

| Layer | Plano | Dimensões | Parallax | Tiles est. |
|-------|-------|-----------|----------|-----------|
| Sky | BG_B | 256x224 | 0.25x | ~25 (bandado) |
| City | BG_A | 512x224 (448 úteis) | 1.0x | ~1200-1400 |
| Debris | Sprites | 3× 64x48 | 1.25x | ~72 máx (3×24) |

---

## Tile Reuse Plan

| Layer | Estratégia |
|-------|-----------|
| BG_B | Bandas horizontais idênticas → tiles por fila = 32, reuso ~100% intra-banda. Total único estimado: 15-25 tiles |
| BG_A | Arquitectura com repetição parcial de janelas e tijolos. H-Flip oportunidades em fachadas simétricas. Estimativa: 1200-1400 tiles únicos |
| Debris | Cada sprite é independente. Estimativa: 20-24 tiles por chunk × 3 = 60-72 tiles |

---

## VDP Extrapolation Plan

| Técnica | Classificação | Status |
|---------|--------------|--------|
| `plane size tuning` (64×32) | `canonica_segura` | APLICADA |
| `SPR_initEx(100)` | `canonica_segura` | PLANEADA (ajustável) |
| `3+1 palette split` | `canonica_segura` | APLICADA (sky, city, debris + player) |
| `compare_flat` | `canonica_segura` | FALLBACK se multi-plano estourar VRAM |

---

## Resultados

### Assets Produzidos

| Asset | Tipo | Dimensões | Formato | Localização |
|-------|------|-----------|---------|-------------|
| sky_bg_b.png | BG_B elite | 256x224 | 4bpp indexed | res/gfx/ |
| city_bg_a.png | BG_A elite | 512x224 | 4bpp indexed | res/gfx/ |
| debris_01.png | Sprite elite | 64x48 | 4bpp indexed | res/gfx/ |
| debris_02.png | Sprite elite | 64x48 | 4bpp indexed | res/gfx/ |
| debris_03.png | Sprite elite | 64x48 | 4bpp indexed | res/gfx/ |

### Artefactos Intermédios

| Artefacto | Localização |
|-----------|-------------|
| extracted_sky_raw.png | res/data/ |
| extracted_city_raw.png | res/data/ |
| extracted_debris_raw.png | res/data/ |
| sky_elite_rgba.png | res/data/ |
| city_cropped_448x224.png | res/data/ |
| city_elite_448x224.png | res/data/ |

---

## Basic vs Elite

A versão BASIC seria uma quantização cega usando mediancut ou similar sem curadoria de rampa. O resultado previsível seria:
- Perda dos tons intermédios de tijolo (fundidos com sombra)
- Perda do contraste entre janelas iluminadas e fachadas escuras
- Gradiente de céu com saltos bruscos

A versão ELITE preserva:
- Rampa contínua de 15 tons no céu (transição perceptível de cor a cada 16px)
- 3 níveis por material na cidade (sombra, base, luz)
- Pontos focais de luz quente nas janelas como elemento heroico
- Silhueta de debris com hierarquia clara de profundidade

**Delta esperado: elite >> basic** (salto significativo em leitura de materiais e hierarquia visual)
