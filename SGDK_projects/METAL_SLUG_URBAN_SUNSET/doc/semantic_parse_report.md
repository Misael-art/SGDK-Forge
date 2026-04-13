# Semantic Parse Report — source.png

**Source:** `res/data/source/source.png` (1113x627, RGBA 8-bit)
**Layout Classification:** `editorial_board`
**Skill:** `art-translation-to-vdp`

---

## source_inventory

| # | Região Pixel | Dimensões | Classe Semântica | Decisão |
|---|-------------|-----------|-----------------|---------|
| 1 | (5,9)-(92,18) | 88x10 | `labels_and_names` — texto "BACKGROUND" | DROP |
| 2 | (4,26)-(515,139) | 512x114 | `scene_plane_sky` — gradiente sunset | KEEP → BG_B |
| 3 | (4,140)-(515,168) | 512x29 | `labels_and_names` — texto "FOREGROUND" | DROP |
| 4 | (5,172)-(599,427) | 595x256 | `scene_plane_architecture` — panorama urbano | KEEP → BG_A |
| 5 | (7,442)-(53,451) | 47x10 | `labels_and_names` — texto "DEBRIS" | DROP |
| 6 | (12,460)-(683,600) | 672x141 | `scene_plane_foreground_composition` — massa frontal de destroços | KEEP → sprites |
| 7 | (600,166)-(1020,348) | 421x183 | `mockup_preview` — cena composta com personagem como referência | DROP |
| 8 | (600,350)-(1030,600) | 431x251 | `author_credits` — avatar + "SPRITES RIPPED BY YOSSHO" | DROP |

---

## layout_classification

```json
{
  "source_layout_type": "editorial_board",
  "intent_summary": "Prancha editorial de Metal Slug (arcade rips by Yossho) organizada em secções rotuladas: fundo atmosférico (sky), plano principal (city), massa frontal (debris), mockup de referência e créditos do ripper.",
  "usable_regions": [2, 4, 6],
  "auxiliary_regions": [7],
  "annotation_regions": [1, 3, 5, 8]
}
```

---

## semantic_region_parsing

### Região 2 — scene_plane_sky (KEEP)
- **Conteúdo:** Gradiente de pôr-do-sol. Parte superior escura (índigo/púrpura), transição por laranjas quentes, vermelhos intensos, até horizonte luminoso.
- **Nuvens:** Formas orgânicas em tons escuros recortadas sobre o gradiente quente.
- **Leitura:** Atmosfera dramática, luz vem da direita baixa.
- **Materiais:** Gradiente de gás/atmosfera, edge de nuvem.

### Região 4 — scene_plane_architecture (KEEP)
- **Conteúdo:** Panorama urbano pós-destruição. Edifícios de tijolo/betão com janelas (algumas iluminadas em amarelo quente), postes de iluminação, letreiros japoneses, rua em perspectiva com paralelepípedos/destroços.
- **Estrutura:** Skyline irregular no topo (telhados, antenas) com transparência acima → céu visível.
- **Materiais:** Tijolo (castanho-rosado com dithering), betão (cinza frio), metal (highlights afiados), vidro (janelas quentes), asfalto (escuro com textura).
- **Leitura:** O olho vai primeiro para as janelas iluminadas (pontos focais de luz quente contra massa escura).

### Região 6 — scene_plane_foreground_composition (KEEP)
- **Conteúdo:** Massa escura de destroços, entulho, madeira, pedra fragmentada. Silhueta dominante.
- **Materiais:** Madeira partido (castanho médio), pedra (cinza escuro), terra (ocre). Highlights subtis nas arestas superiores.
- **Leitura:** Funciona como enquadramento inferior que ancora a profundidade. Quase silhueta — NÃO é actor sprite.

### Região 7 — mockup_preview (DROP)
- **Conteúdo:** Composição de referência mostrando os 3 planos montados com um personagem amarelo (provavelmente Marco/Eri do Metal Slug).
- **Motivo DROP:** É apenas preview editorial. Não é arte-fonte para tradução.

### Região 8 — author_credits (DROP)
- **Conteúdo:** Avatar de Diddy Kong (?) + texto "SPRITES RIPPED BY YOSSHO / CREDITS: NO".
- **Motivo DROP:** Metadados do ripper. Ruído semântico absoluto.

---

## drop_policy

```
REGIÕES DESCARTADAS:
  [1] Label "BACKGROUND"    → anotação textual
  [3] Label "FOREGROUND"    → anotação textual
  [5] Label "DEBRIS"        → anotação textual
  [7] Mockup_preview        → referência visual apenas, não arte-fonte
  [8] Author_credits        → metadados do ripper, ruído editorial

POLÍTICA: Nenhum pixel das regiões DROP pode contaminar assets promovidos para /res/gfx/
```

---

## composition_role_assignment

| Região | Papel VDP | Justificação |
|--------|-----------|-------------|
| #2 Sky | BG_B | Massa distante, gradiente atmosférico, parallax lento |
| #4 City | BG_A | Estrutura principal, scroll 1:1, volume arquitectónico |
| #6 Debris | Sprites (foreground_layer) | Massa frontal composicional com parallax mais rápido |

---

## recomposition_hypothesis

```
Passo 1: BG_B preenche o ecrã inteiro com o gradiente de sunset (256x224, wrap)
Passo 2: BG_A sobrepõe com a cidade. Topo transparente revela BG_B (céu).
         A silhueta irregular dos telhados cria separação natural.
Passo 3: Sprites de debris posicionados na franja inferior com priority bit.
         Move mais rápido que a câmera (1.25x) para efeito de profundidade.

Resultado esperado: 3 camadas de profundidade — céu distante, cidade média, destroços próximos.
Compatível com OBJETIVO.png.
```

---

## soul_summary

```json
{
  "soul_summary": "Cena urbana pós-destruição ao entardecer. O contraste entre o céu dramaticamente quente e a cidade escura e fria é a alma da composição. Pontos de luz quente nas janelas conectam os dois mundos tonais.",
  "forma_dominante": "Skyline urbano irregular recortado contra gradiente de sunset",
  "leitura_em_miniatura": "Faixa quente (topo) → massa escura (meio) → silhueta preta (baixo)",
  "ponto_focal": "Janelas iluminadas contra fachadas escuras + horizonte de fogo",
  "material_dominante": "Tijolo/betão urbano (frio) contra luz atmosférica (quente)"
}
```

### must_keep
- Gradiente de sunset (identidade cromática da cena)
- Silhueta dos telhados (forma dominante)
- Janelas iluminadas (pontos focais de contraste)
- Massa escura dos destroços (enquadramento de profundidade)

### can_simplify
- Detalhe interno dos edifícios (pode perder sub-pixel detail sem matar leitura)
- Textura de paralelepípedos na rua (pode ser simplificado para band de cor)
- Nuvens menores (podem ser fundidas em gradiente)

### must_drop
- Labels textuais, mockup, créditos
- Sub-pixel anti-aliasing do source (não existe em MD)
- Gradientes com mais de 15 tons por paleta (devem ser traduzidos para rampas de hardware)

---

## source_region_strategy

| Layer | Extracção | Target MD | Escala |
|-------|-----------|-----------|--------|
| Sky (512x114) | Crop directo do source | 256x224 (tile-bandado) | Reinterpretar como gradiente vertical bandado para máximo tile reuse |
| City (595x256) | Crop + escala proporcional | 448x224 | Preservar skyline, janelas, massa. Ajustar a 224px de altura |
| Debris (672x141) | Crop selectivo de chunks | 3-5 sprites de 64x48 | Extrair silhuetas dominantes como metasprites individuais |
