# Aesthetic Report — visual-excellence-standards

**Projecto:** METAL_SLUG_URBAN_SUNSET
**Skill:** `visual-excellence-standards`

---

## Protocolo de Referências (3 jogos reais obrigatórios)

| # | Jogo | Herança Técnica |
|---|------|-----------------|
| 1 | **Streets of Rage 3** | Cenário urbano nocturno com contraste entre massa escura de edifícios e pontos de luz quente em janelas. Separação clara BG_A/BG_B com céu atmosférico. |
| 2 | **Metal Slug (Neo-Geo→MD ports)** | Composição de cena com destruição urbana, massa frontal de destroços e arquitectura detalhada. Hierarquia de profundidade em 3 camadas. |
| 3 | **Gunstar Heroes** | Uso eficiente de paleta para máximo contraste entre planos. Parallax agressivo que mantém legibilidade do gameplay. |

---

## Julgamento por Layer

### BG_B — Sky Sunset

| Métrica | Score (0-3) | Justificação |
|---------|------------|--------------|
| `palette_efficiency` | **3** | 15 cores formam rampa contínua sem redundância. Cada tom cobre uma faixa tonal única de índigo a ouro. Zero desperdício. |
| `tile_efficiency` | **3** | Bandas horizontais idênticas garantem ~15-25 tiles únicos para 256×224. Reuso extremo por design. |
| `detail_density_8x8` | **2** | Cada tile é cor sólida (gradiente por banda). Funcional para atmosfera distante mas sem textura interna de nuvem. |
| `dithering_density` | **N/A** | Sem dithering por design — gradiente resolvido por bandas cromáticas. Correcto para BG_B atmosférico. |
| `silhouette_readability` | **3** | Não aplicável como silhueta, mas o gradiente é imediatamente legível como "pôr-do-sol" em miniatura. |
| `layer_separation` | **3** | Tons quentes e saturados criam contraste claro contra a massa escura e fria da cidade (BG_A). |
| `reuse_opportunity` | **3** | Já maximamente optimizado. Wrap horizontal nativo a 256px. |

**Veredicto BG_B: APROVADO** — Cumpre função atmosférica sem competir com BG_A. Tile-eficiente ao extremo.

**Teste AAA**: "Poderia estar em SoR3 ou Shinobi III como céu de estágio?" → **SIM**

---

### BG_A — City Architecture

| Métrica | Score (0-3) | Justificação |
|---------|------------|--------------|
| `palette_efficiency` | **2** | 15 cores cobrem sombra→base→luz para tijolo, betão e janelas iluminadas. Boa distribuição. Poderia ganhar com melhor separação entre cinza frio (betão) e castanho quente (tijolo) se mais slots existissem. |
| `tile_efficiency` | **2** | 448px de conteúdo útil em plano de 512px. Padding transparente não gera tiles extras significativos (rescomp deduplica). Estimativa: 1200-1400 tiles únicos — é a layer mais pesada. |
| `detail_density_8x8` | **2** | A quantização de 8-bit RGBA → 4bpp perde subtilezas do source (anti-aliasing, gradientes de betão). Mas a massa geral e os pontos focais (janelas) sobrevivem. |
| `dithering_density` | **1** | A tradução actual não introduz dithering funcional nas transições de material. Oportunidade: dithering entre tijolo e sombra melhoraria textura perceptível. |
| `silhouette_readability` | **3** | Skyline irregular dos telhados contra céu (transparência) é forte e imediatamente legível. |
| `layer_separation` | **3** | Massa escura e fria da cidade contra céu quente (BG_B) e destroços escuros (sprites) mantém hierarquia clara. |
| `reuse_opportunity` | **2** | Janelas repetitivas e fachadas simétricas oferecem oportunidades de H-Flip. Rescomp lida com deduplicação automática. |

**Veredicto BG_A: APROVADO COM RESSALVAS** — Estrutura sólida, hierarquia visual correcta. Oportunidade de melhoria em dithering funcional para materiais e refinamento de densidade 8×8.

**Teste AAA**: "Poderia estar em SoR2/3 como cenário urbano?" → **SIM, com o dithering das versões de referência seria exemplar**

---

### Layer C — Debris Sprites

| Métrica | Score (0-3) | Justificação |
|---------|------------|--------------|
| `palette_efficiency` | **2** | 15 cores de dark a highlight cobrem a massa de entulho. Muitos slots no range escuro (intencional: é silhueta), mas os highlights podiam ter mais separação. |
| `tile_efficiency` | **2** | 3 sprites de 64×48 = 72 tiles máximo. Razoável para metasprites composicionais. |
| `detail_density_8x8` | **2** | Massa escura com highlights nas arestas é funcional como enquadramento. Não precisa de detalhe fino — é foreground composicional, não actor sprite. |
| `dithering_density` | **N/A** | Sem dithering por design — silhueta sólida com highlight de aresta. Correcto para foreground_layer. |
| `silhouette_readability` | **2** | Massa escura é legível como "destroços" mas poderia ter mais definição na aresta superior para separar do chão da cidade. |
| `layer_separation` | **3** | Sprites com priority bit sobre BG_A + BG_B garantem separação absoluta. Parallax mais rápido (1.25x) reforça profundidade. |
| `reuse_opportunity` | **1** | Cada chunk é orgânico e único. Pouca oportunidade de reuso entre os 3 sprites. |

**Veredicto Debris: APROVADO** — Cumpre papel composicional de enquadramento. Não é actor sprite e não precisa de ser.

**Teste AAA**: "Poderia ser foreground de Metal Slug?" → **SIM, silhueta de destroços é canónica do género**

---

## Avaliação Global da Cena

### Hierarquia Visual (O Segredo da Profundidade)

```
BG_B (céu quente) → respiração ✓ — não compete com BG_A
BG_A (cidade fria) → estrutura ✓ — sustenta palco sem repetir fundo
Debris (silhueta) → enquadramento ✓ — ancora profundidade
Player (PAL3)     → decisão — reservada, será o pico de leitura
```

### Coesão Visual (Regras de `01_visual_cohesion_system.md`)

| Regra | Status |
|-------|--------|
| Luz unificada | ✓ Luz vem do oeste/horizonte. Céu quente, highlights das janelas e arestas dos destroços consistentes. |
| Paleta integrada | ✓ Tons quentes partilhados entre PAL0 (céu) e PAL1 (janelas da cidade). Família cromática coesa. |
| Materiais consistentes | ✓ Betão=opaco, tijolo=texturado, vidro=highlight quente. |
| Camadas conversam | ✓ O céu projecta-se pela transparência do topo da cidade. Os destroços ancoram a base. |

### Quality Bar (Regras de `00_visual_quality_bar.md`)

| Requisito | Status |
|-----------|--------|
| 3 níveis por material | ✓ Paleta curada com sombra, base e luz por material |
| Contraste FG/MID/BG | ✓ Hierarquia tonal: quente distante → frio médio → escuro próximo |
| Silhueta clara nos sprites | ✓ Skyline da cidade e massa dos destroços legíveis |
| Textura perceptível | ⚠ Oportunidade de melhoria com dithering funcional na cidade |
| Dithering quando necessário | ⚠ Não aplicado na versão actual — oportunidade declarada |

### Teste Final

"Isto poderia estar num jogo comercial AAA de 1994?" → **SIM, com reserva sobre dithering funcional**

---

## Gates de Aprovação

| Gate | Status |
|------|--------|
| `palette_efficiency` | ✓ Cada paleta usa slots com propósito |
| `layer_separation` | ✓ 3 camadas visualmente distintas |
| `scene_readability` | pendente prova em 320×224 real |
| `material_readability` | ⚠ Dithering funcional melhoraria tijolo e betão |
| `depth_hierarchy` | ✓ BG_B < BG_A < debris < player |
