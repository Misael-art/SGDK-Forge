# 91 - Multi-Plane Composition — Mega Drive AAA (v1 DRAFT)

Status: `RASCUNHO` — Aguardando aprovacao humana para FASE 2

---

## Objetivo

Definir regras rigidas para composicao de cena multi-plano no Mega Drive usando BG_A, BG_B e sprites com parallax, profundidade e hierarquia visual. Toda cena produzida no workspace DEVE obedecer este documento.

---

## 1. ARQUITETURA DE PLANOS DO VDP

### 1.1 Estrutura Fixa

O VDP do Mega Drive oferece exatamente:

| Plano | Nome SGDK | Funcao Canonica | Scroll | Prioridade |
|-------|-----------|----------------|--------|------------|
| Plano B | `BG_B` | Fundo distante (ceu, horizonte, montanha) | Independente | Mais atras |
| Plano A | `BG_A` | Cenario proximo (edificios, terreno, estrutura jogavel) | Independente | Intermediario |
| Sprites | SAT | Personagens, inimigos, itens, FX, HUD | Por sprite | Mais a frente |
| Window | `WINDOW` | HUD fixo (quando usado) | Nao tem scroll | Sobrepoe BG_A |

NAO existe terceiro plano de background. Qualquer ilusao de terceiro plano DEVE ser construida por sprite graft (tecnica `avancada_com_tradeoff`).

### 1.2 Regras Absolutas

- BG_B DEVE ser o plano de menor contraste e menor detalhe da cena.
- BG_A DEVE ser o plano de estrutura jogavel com contraste medio.
- Sprites heroicos DEVEM ter o contraste mais alto da cena.
- PROIBIDO: BG_B com mais detalhe ou brilho que BG_A.
- PROIBIDO: BG_A com mais saturacao que o sprite principal.
- A hierarquia de leitura visual DEVE ser: sprite > BG_A > BG_B. Se essa ordem estiver invertida, a cena DEVE ser reprovada.

---

## 2. PARALLAX

### 2.1 Principio

Parallax simula profundidade movendo planos em velocidades diferentes. Objetos distantes se movem mais devagar.

### 2.2 Tabela de Velocidade Canonica

| Plano | Velocidade Relativa | Justificativa |
|-------|--------------------|---------------|
| BG_B (fundo distante) | 0.125x a 0.25x da camera | Ceu, horizonte: quase estatico |
| BG_A (cenario proximo) | 0.5x a 0.75x da camera | Estrutura: acompanha mas nao iguala |
| Gameplay (sprites) | 1.0x | Referencia de velocidade |
| Foreground (quando existir) | 1.25x a 1.5x | Elementos de frente: passam mais rapido |

### 2.3 Modos de Scroll SGDK

| Modo | API | Uso | Custo |
|------|-----|-----|-------|
| Scroll por plano | `VDP_setHorizontalScroll(BG_B, x)` | Parallax basico entre planos | Negligivel |
| Scroll por tile | `HSCROLL_TILE` + `VDP_setHorizontalScrollTile()` | Parallax com faixas horizontais | Medio |
| Scroll por linha | `HSCROLL_LINE` + `VDP_setHorizontalScrollLine()` | Efeitos raster, pseudo-3D | Alto (DMA) |

### 2.4 Implementacao Canonica (Parallax Basico)

```c
// Configuracao inicial
VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

// No game loop:
s16 camera_x = player->x - 160; // camera centrada no jogador

// BG_B: 25% da velocidade da camera
VDP_setHorizontalScroll(BG_B, -(camera_x >> 2));

// BG_A: 50% da velocidade da camera (ou scroll via MAP engine)
VDP_setHorizontalScroll(BG_A, -(camera_x >> 1));

// Sprites: posicao = world_pos - camera_x (gerido pelo sprite engine)
```

### 2.5 Regras Absolutas de Parallax

- OBRIGATORIO: toda cena com mais de 1 plano visivel DEVE ter velocidades de scroll diferentes.
- BG_B DEVE se mover mais devagar que BG_A. A relacao NAO DEVE ser invertida.
- A velocidade de parallax DEVE ser consistente ao longo de toda a fase. PROIBIDO mudar a relacao mid-level sem justificativa de gameplay (ex: transicao de bioma).
- PROIBIDO: parallax que causa seam (borda visivel onde o mapa repete). O tilemap DEVE ser largo o suficiente ou usar wrap correto.

---

## 3. DISTRIBUICAO DE PALETA

### 3.1 Alocacao Canonica

| Paleta | Funcao | Cores |
|--------|--------|-------|
| PAL0 | BG_B (fundo distante) | 15 cores: tons frios, baixa saturacao, atmosferico |
| PAL1 | BG_A (cenario proximo) | 15 cores: tons medios, estrutura legivel |
| PAL2 | Sprites (heroi + inimigos) | 15 cores: tons quentes/vibrantes, alto contraste |
| PAL3 | HUD + FX + itens | 15 cores: funcional, legivel sobre tudo |

### 3.2 Regras de Paleta entre Planos

- BG_B DEVE usar cores de menor luminancia media que BG_A.
- BG_A DEVE usar cores de menor saturacao media que os sprites.
- Os planos NAO DEVEM compartilhar paleta, exceto quando a cena exigir `3+1 palette split` (3 paletas para fundos, 1 para sprite principal).
- Quando `3+1` for necessario, a decisao DEVE ser registrada no `hardware_budget_review` da cena.
- PROIBIDO: BG_B e BG_A usando a mesma paleta sem justificativa (resultado: planos colados).

### 3.3 Hierarquia de Brilho (OBRIGATORIA)

```
Luminancia media: BG_B < BG_A < Sprite principal

Regra pratica:
- BG_B: luminancia media 30-50% do maximo
- BG_A: luminancia media 50-70% do maximo
- Sprite: luminancia media 60-85% do maximo
- Highlight do sprite: 90-100% do maximo
```

---

## 4. DISTRIBUICAO DE VRAM

### 4.1 Budget Canonico

VRAM total: 64KB = 2048 tiles de 32 bytes.

Area util real (apos reservas do SGDK):

| Reserva | Tiles | Bytes |
|---------|-------|-------|
| Mapa BG_A (64x32 = 2048 words) | ~64 tiles equivalentes | 2048 bytes |
| Mapa BG_B (64x32 = 2048 words) | ~64 tiles equivalentes | 2048 bytes |
| Sprite Attribute Table | ~10 tiles equivalentes | 320 bytes |
| H-Scroll Table | ~7 tiles equivalentes | 224 bytes |
| Fonte padrao | 96 tiles | 3072 bytes |
| **Total reservado** | **~241 tiles** | **~7716 bytes** |
| **Tiles livres para arte** | **~1807 tiles** | **~57,824 bytes** |

### 4.2 Distribuicao Recomendada

| Componente | Tiles | Regra |
|-----------|-------|-------|
| Tileset BG_B | 200-400 | BG_B DEVE ser o mais economico (reuso por flip, repeticao) |
| Tileset BG_A | 400-800 | BG_A aceita mais detalhe mas DEVE reusar por modularidade |
| Sprites (total residentes) | 200-400 | Ciclo de animacao completo do protagonista + inimigos visiveis |
| Reserva | ~200 | Buffer para FX, transicoes, tile streaming |

### 4.3 Regras Absolutas de VRAM

- A soma de tiles de BG_A + BG_B + sprites residentes NAO DEVE exceder 1600 tiles. Os 200 restantes DEVEM ficar como reserva.
- Se a cena exceder 1600 tiles, o agente DEVE propor: (a) reducao de tiles por reuso/flip, (b) `SPR_initEx` para ajustar particao, ou (c) `plane size tuning` para reduzir tabela de mapa.
- PROIBIDO: aprovar cena sem medir tiles unicos reais. "Parece que cabe" NAO e validacao.
- Quando a soma de tiles de BG exceder 1200 combinados, o laudo DEVE emitir `COMPARE_FLAT_CANDIDATE` para considerar prova single-plane em ROM.

---

## 5. CONFIGURACAO DE PRIORIDADE

### 5.1 Prioridade de Sprite vs Background

O VDP usa bits de prioridade para controlar sobreposicao:

| Prioridade Sprite | Prioridade BG | Resultado |
|-------------------|---------------|-----------|
| LOW (0) | LOW (0) | Sprite na frente do BG |
| LOW (0) | HIGH (1) | BG na frente do sprite |
| HIGH (1) | LOW (0) | Sprite na frente do BG |
| HIGH (1) | HIGH (1) | Sprite na frente do BG |

### 5.2 Regras de Prioridade

- Sprites de gameplay (heroi, inimigos) DEVEM usar prioridade LOW por padrao.
- Tiles de BG_A que devem cobrir sprites (teto, arvore de frente) DEVEM usar prioridade HIGH.
- Sprites decorativos de foreground DEVEM usar prioridade HIGH.
- PROIBIDO: todos os tiles de BG com mesma prioridade (perde-se a possibilidade de foreground via tiles).

### 5.3 Foreground via Prioridade de Tile

Para simular foreground sem gastar sprites:
- Tiles de BG_A com prioridade HIGH funcionam como foreground que cobre sprites.
- Estes tiles DEVEM ter transparencia parcial (index 0 nos pixels onde o sprite deve aparecer por baixo).
- Uso canonico: copa de arvore, teto de caverna, grade de prisao.

---

## 6. RECEITA CANONICA DE IMPLEMENTACAO

### 6.1 Inicializacao da Cena

```c
// 1. Configurar scroll
VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);

// 2. Carregar paletas com hierarquia de brilho
PAL_setPalette(PAL0, bg_b_palette.data, DMA);  // fundo: frio, escuro
PAL_setPalette(PAL1, bg_a_palette.data, DMA);  // cenario: medio
PAL_setPalette(PAL2, sprite_palette.data, DMA); // sprites: quente, vibrante
PAL_setPalette(PAL3, hud_palette.data, DMA);    // HUD: funcional

// 3. Carregar tilesets
u16 ind = TILE_USER_INDEX;
VDP_loadTileSet(&bg_b_tileset, ind, DMA);
u16 bg_b_start = ind;
ind += bg_b_tileset.numTile;

VDP_loadTileSet(&bg_a_tileset, ind, DMA);
u16 bg_a_start = ind;
ind += bg_a_tileset.numTile;

// 4. Carregar mapas
MAP_create(&map_bg_b, BG_B, TILE_ATTR_FULL(PAL0, FALSE, FALSE, FALSE, bg_b_start));
MAP_create(&map_bg_a, BG_A, TILE_ATTR_FULL(PAL1, FALSE, FALSE, FALSE, bg_a_start));

// 5. Inicializar sprite engine
SPR_init();
Sprite* player = SPR_addSprite(&player_def, 160, 112, TILE_ATTR(PAL2, FALSE, FALSE, FALSE));
```

### 6.2 Game Loop com Parallax

```c
while (TRUE)
{
    // Input e logica de gameplay
    handleInput();
    updateGameplay();
    
    // Atualizar camera
    s16 cam_x = player_world_x - 160;
    s16 cam_y = player_world_y - 112;
    
    // Parallax: BG_B = 25%, BG_A gerido pelo MAP engine
    VDP_setHorizontalScroll(BG_B, -(cam_x >> 2));
    VDP_setVerticalScroll(BG_B, cam_y >> 2);
    
    // MAP engine gerencia scroll de BG_A automaticamente
    MAP_scrollTo(map_bg_a, cam_x, cam_y);
    
    // Atualizar sprites
    SPR_update();
    
    // Sincronizar com VBlank
    SYS_doVBlankProcess();
}
```

---

## 7. METRICAS DE VALIDACAO

| Metrica | Threshold de Aprovacao | Metodo de Medicao |
|---------|----------------------|-------------------|
| `depth_perception` | 3 planos distintos visiveis em screenshot (BG_B, BG_A, sprite) | Inspecao visual em BlastEm: cada plano DEVE ter brilho/contraste distinguivel |
| `parallax_smoothness` | Zero seams, zero corrupcao de mapa durante scroll | Mover camera em todas as direcoes por 30 segundos em BlastEm |
| `vram_utilization` | Tiles usados <= 1600 com >= 200 de reserva | Contagem de tiles unicos via ferramentas de debug |
| `brightness_hierarchy` | Luminancia media: BG_B < BG_A < sprite | Medir luminancia media de cada plano isoladamente |
| `priority_correctness` | Foreground cobre sprites quando esperado, sprites aparecem sobre BG normalmente | Inspecao visual com sprite movendo atras e na frente de tiles de alta prioridade |
| `performance` | 60fps estaveis durante scroll continuo | Frame counter em BlastEm |

---

## 8. CHECKLIST DE VALIDACAO (SIM/NAO)

- [ ] A cena tem BG_B + BG_A + pelo menos 1 sprite visivel?
- [ ] BG_B se move mais devagar que BG_A?
- [ ] BG_B tem menor brilho e contraste que BG_A?
- [ ] BG_A tem menor saturacao que o sprite principal?
- [ ] O sprite principal e o elemento mais legivel da tela?
- [ ] As paletas de cada plano estao em slots separados (PAL0/1/2/3)?
- [ ] O parallax e suave e sem seams?
- [ ] O total de tiles unicos cabe em 1600 tiles?
- [ ] A cena roda a 60fps estaveis em BlastEm?
- [ ] Tiles de foreground (prioridade HIGH) cobrem corretamente os sprites?
- [ ] A cena NAO apresenta corrupcao de mapa durante scroll?
- [ ] A profundidade visual e clara: o jogador percebe 3+ planos?

---

## 9. ANTI-PADROES (PROIBIDOS)

| Anti-Padrao | Diagnostico | Consequencia |
|-------------|-------------|--------------|
| BG_A e BG_B com mesmo brilho | Planos parecem colados, sem profundidade | REPROVAR — ajustar hierarquia de luminancia |
| Parallax sem relacao de velocidade | BG se move na mesma velocidade ou invertido | REPROVAR — aplicar tabela de velocidade (secao 2.2) |
| Sprite desaparecendo contra fundo | Outline fraco ou paleta proxima do BG | REPROVAR — reforcar contraste sprite vs BG |
| Toda a VRAM gasta sem reserva | FX ou transicoes corrompem a tela | REPROVAR — manter 200 tiles de reserva |
| Imagem inteira como tilemap | Explode tiles unicos, nao modular | REPROVAR — modularizar por plano |
| Foreground usando sprites em vez de tiles high-priority | Gasta sprite budget desnecessariamente | REPROVAR — usar BG_A com prioridade HIGH |
| Paleta compartilhada entre BG_B e BG_A sem justificativa | Planos perdem identidade propria | REPROVAR — paletas separadas obrigatorias |

---

## 10. BENCHMARKS OBRIGATORIOS

| Jogo | Aspecto de Referencia | Quando Usar |
|------|----------------------|-------------|
| Thunder Force IV | Parallax extremo com multiplas velocidades por linha | Referencia maxima de parallax |
| Shinobi III | Profundidade atmosferica entre planos | Cena com fog, floresta, noite |
| Sonic 3 & Knuckles | Parallax por linha, transicoes de bioma | Plataforma com cenarios variados |
| Streets of Rage 2 | Composicao urbana BG_A + BG_B limpa | Beat-em-up, cenario urbano |
| Castlevania Bloodlines | Foreground via prioridade, profundidade gotica | Cena com teto, grade, elementos na frente |
| Contra Hard Corps | Cena de acao intensa com budget de sprites + BG | Acao com muitos sprites + cenario rico |

---

## 11. INTEGRACAO COM SKILLS EXISTENTES

| Skill | Relacao |
|-------|---------|
| `visual-excellence-standards` | "O Segredo da Profundidade" e regra mestra desta composicao |
| `megadrive-vdp-budget-analyst` | Budget de VRAM, DMA e sprites DEVE ser medido para a cena |
| `art-translation-to-vdp` | Assets traduzidos DEVEM respeitar hierarquia de plano |
| `07_sprite_animation_standards` | Sprites na cena DEVEM seguir regras de animacao |
| `08_character_design_standards` | Personagens DEVEM seguir regras de cor e silhueta |
| `01_visual_cohesion_system` | Luz unificada, paleta integrada, materiais consistentes |
| `00_visual_quality_bar` | Barra AAA: 3 niveis de cor por material, contraste entre planos |
