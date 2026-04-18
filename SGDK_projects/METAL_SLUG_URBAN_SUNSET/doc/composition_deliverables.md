# Multi-Plane Composition — Entregas Obrigatórias

**Projecto:** METAL_SLUG_URBAN_SUNSET
**Fonte:** `res/data/source/source.png` (1113x627, editorial_board)
**Guia:** `res/data/source/MAPA_COMPOSIÇÃO.png` (671x258)
**Objectivo:** `res/data/source/OBJETIVO.png` (677x259)
**Skill:** `multi-plane-composition`

---

## 1. depth_role_map

```
PLANO B  (vermelho no MAPA_COMPOSIÇÃO)
  ├─ Região: faixa superior da cena
  ├─ Conteúdo: céu sunset com gradiente quente + nuvens dramáticas
  ├─ Papel VDP: BG_B
  └─ Profundidade: DISTANTE — atmosfera e respiração visual

PLANO A  (azul no MAPA_COMPOSIÇÃO)
  ├─ Região: massa central e inferior da cena
  ├─ Conteúdo: arquitectura urbana — edifícios, rua, postes, letreiros, pontos de luz
  ├─ Papel VDP: BG_A
  └─ Profundidade: MÉDIA — palco principal da acção

PLANO C  (amarelo-verde no MAPA_COMPOSIÇÃO)
  ├─ Região: franja inferior da cena
  ├─ Conteúdo: destroços, entulho, massa frontal de destruição urbana
  ├─ Papel VDP: sprites (foreground_layer composicional)
  └─ Profundidade: PRÓXIMO — foreground que ancora profundidade
```

### Hierarquia visual

```
  LONGE                                          PERTO
  ─────────────────────────────────────────────────►
  BG_B (céu)  ──►  BG_A (cidade)  ──►  C (debris como sprites)
  parallax 0.25x    parallax 1.0x       parallax 1.25x
  PAL0 (quente)     PAL1 (neutro)       PAL2 (escuro)
```

---

## 2. composition_schema

```json
{
  "scene_type": "scene_slice",
  "source_taxonomy": "editorial_board",
  "viewport": { "w": 320, "h": 224 },
  "scroll_direction": "horizontal",
  "scroll_range_px": 128,
  "planes": [
    {
      "id": "sky",
      "vdp_plane": "BG_B",
      "z_order": 0,
      "priority": false,
      "parallax_ratio": 0.25,
      "wraps_horizontal": true,
      "image_width": 256,
      "image_height": 224,
      "notes": "Céu sunset com gradiente. Wrap natural a 256px garante infinito horizontal."
    },
    {
      "id": "city",
      "vdp_plane": "BG_A",
      "z_order": 1,
      "priority": false,
      "parallax_ratio": 1.0,
      "wraps_horizontal": false,
      "image_width": 448,
      "image_height": 224,
      "notes": "Arquitectura urbana. Topo transparente deixa BG_B visível. Largura 448px dá 128px de scroll."
    },
    {
      "id": "debris",
      "vdp_plane": "SPRITES",
      "z_order": 2,
      "priority": true,
      "parallax_ratio": 1.25,
      "wraps_horizontal": false,
      "sprite_count_estimate": "3-5 metasprites",
      "notes": "Massa frontal de destroços. Classificado como foreground_layer, NÃO como actor sprite."
    }
  ],
  "palette_assignment": {
    "PAL0": "sky (BG_B) — gradiente sunset quente",
    "PAL1": "city (BG_A) — tons urbanos neutros/frios",
    "PAL2": "debris (sprites) — silhuetas escuras e terra",
    "PAL3": "player + HUD — reservado"
  }
}
```

---

## 3. layer_plan

### BG_B — Céu Sunset

| Atributo | Valor |
|----------|-------|
| Papel | Atmosfera distante, gradiente de pôr-do-sol |
| Plano VDP | BG_B |
| Parallax | 0.25x (scroll lento = profundidade distante) |
| Dimensões | 256x224 (wrap horizontal nativo) |
| Paleta | PAL0: 15 cores + transparente. Rampas: laranja quente → vermelho profundo → púrpura/índigo escuro |
| Tile strategy | Gradiente horizontal bandado = alto reuso de tiles (estimativa: ~20-40 tiles únicos) |
| Prioridade | LOW — BG_B sem bit priority |
| Scroll mode | HSCROLL_PLANE |
| Regra | Nunca competir com BG_A em atenção visual. Atmosfera, não detalhe. |

### BG_A — Cidade Urbana

| Atributo | Valor |
|----------|-------|
| Papel | Estrutura principal — edifícios, rua, postes, letreiros |
| Plano VDP | BG_A |
| Parallax | 1.0x (scroll principal da câmera) |
| Dimensões | 448x224 conteúdo útil em plano de 512x224 (64 tiles × 28 tiles) |
| Paleta | PAL1: 15 cores + transparente. Rampas: cinza-escuro (sombra) → cinza-médio (base) → bege/amarelo quente (janelas iluminadas) |
| Tile strategy | Arquitectura com repetição parcial (janelas, tijolos) mas alta variação. Estimativa: 1200-1400 tiles únicos |
| Prioridade | MEDIUM — sem bit priority, mas acima de BG_B pelo z-order do VDP |
| Scroll mode | HSCROLL_PLANE |
| Transparência | Topo transparente (index 0 = magenta FF00FF) para deixar o céu visível |
| Regra | Sustentar a cena. Volume, massa, legibilidade estrutural. |

### Layer C — Debris (Foreground Composicional)

| Atributo | Valor |
|----------|-------|
| Papel | Massa frontal de destroços — ancora profundidade e enquadramento |
| Plano VDP | Sprites com priority bit SET |
| Parallax | 1.25x (move mais rápido que a câmera = mais perto) |
| Dimensões | 3-5 metasprites de 64x48 ou similar |
| Paleta | PAL2: 15 cores + transparente. Rampas: preto/castanho escuro → terra → highlight mínimo |
| Classificação | `foreground_layer` — NÃO é actor sprite |
| Regra | Não pode ser tratado como decoração solta. Abraça o enquadramento. |

---

## 4. shared_canvas_contract

```
Quadro espacial comum: 448 × 224 px

Todas as layers partilham esta base:
  - (0,0) = canto superior-esquerdo da cena scrollável
  - (447,223) = canto inferior-direito do conteúdo útil
  - Viewport inicial: x=0..319, y=0..223
  - Scroll máximo: camera_x = 0..128

Regras:
  - BG_B mapeado para 256x224 mas representando o mesmo horizonte
  - BG_A content: 448x224, padding a 512x224 com transparência
  - Debris sprites: posicionados em coordenadas da mesma base espacial
  - NENHUMA layer pode mudar de enquadramento ou escala independente
  - A recomposição deve alinhar céu, arquitectura e debris num único frame
```

---

## 5. hardware_budget_review (primeira estimativa)

```
=== BUDGET ESTIMADO — METAL_SLUG_URBAN_SUNSET ===

Configuração VDP:
  VDP_setPlaneSize(64, 32)
  maps_addr = 0xC000
  TILE_MAX_NUM = 0xC000 / 32 = 1536

Reservas fixas:
  Sistema (SGDK)     =  16 tiles
  Fonte (default)    =  96 tiles
  SPR_initEx(N)      = 100 tiles (debris 3-5 metasprites + player)
  ─────────────────────────────
  Total reservado     = 212 tiles

Tiles disponíveis para BG:
  1536 - 212 = 1324 tiles para BG_B + BG_A

Estimativa por plano:
  BG_B (céu gradiente bandado)  ≈   25 tiles (alto reuso)
  BG_A (cidade 448px)           ≈ 1200-1300 tiles (alta variedade)
  ─────────────────────────────────
  Total BG estimado             ≈ 1225-1325 tiles

Margem:
  1324 - 1325 = -1 (limite justo)
  1324 - 1225 = +99 (cenário optimista)

DECISÃO: cabe com recuo
  - BG_B DEVE ser maximamente tile-eficiente (gradiente bandado, <30 tiles)
  - BG_A pode precisar de recuo de ~50-100 tiles via curadoria de detalhe
  - Se não couber: fallback para compare_flat ou redução de scroll width
  - SPR_initEx(100) é apertado; avaliar se 80 basta
  - Medição REAL com rescomp OBRIGATÓRIA antes de integrar

Sinais:
  - MANUAL_VRAM_PARTITION_CANDIDATE (SPR_initEx ajustável)
  - PLANE_SIZE_TUNING_CANDIDATE (64x32 é o mínimo para 448px scroll)
```

---

## 6. delivery_findings

### Oportunidades

1. **BG_B tile efficiency** — céu sunset é gradiente puro. Com bandas horizontais idênticas, pode descer a <25 tiles únicos, libertando margem para BG_A.
2. **BG_A architectural repetition** — janelas, tijolos e fachadas têm padrões repetíveis. H-Flip de tiles pode poupar 5-15% de tiles únicos.
3. **Debris simplification** — a massa de destroços é maioritariamente silhueta escura com highlight mínimo. Pode ser eficiente como sprites com poucos tiles.
4. **3+1 palette split** — 3 paletas para cena (sky, city, debris) + 1 para player é a repartição canónica segura.

### Riscos

1. **Budget apertado** — a estimativa de BG_A fica no limite. Se a tradução para VDP gerar >1300 tiles, será necessário recuo (crop, simplificação ou compare_flat).
2. **Sprite scanline pressure** — debris sprites na zona inferior podem colidir com o player em scanlines comuns. Limitar debris a 2-3 metasprites largos.
3. **Transparência BG_A** — o topo da cidade é irregular (telhados, antenas). A gestão de alpha/transparência é crítica para não perder a silhueta.
4. **Editorial board parsing** — o source.png NÃO é a cena final. Precisa de desmontagem semântica rigorosa antes de qualquer tradução.

### Técnica escolhida: `canonica_segura`

- `plane size tuning` (64x32)
- `SPR_initEx(100)` ajustável
- `3+1 palette split`
- compare_flat como fallback se multi-plano real não couber

---

## Gates de Aprovação (auto-avaliação preliminar)

| Gate | Estado | Nota |
|------|--------|------|
| depth_separation | ✓ planeado | BG_B=distante, BG_A=médio, C=perto com parallax distintos |
| plane_role_clarity | ✓ planeado | foreground classificado como composicional, não sprite |
| scene_readability | pendente | só pode ser validado após tradução e prova em 320x224 |
| budget_fit | ⚠ apertado | cabe com recuo, medição real obrigatória |
| rom_strategy_declared | ✓ | canonica_segura com compare_flat como fallback |
