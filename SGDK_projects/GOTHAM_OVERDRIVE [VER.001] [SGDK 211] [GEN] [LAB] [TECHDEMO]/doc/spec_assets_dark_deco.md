# Documento de Especificação de Assets Gráficos AAA — GOTHAM_OVERDRIVE

> **Projeto:** `SGDK_projects/GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]`
> **Estilo Visual:** Dark Deco dos Anos 90 (The Adventures of Batman & Robin / Batman TAS)
> **Hardware Alvo:** Sega Genesis / Mega Drive (VDP Yamaha YM7101, 320x224, 60 FPS)
> **Status:** Especificação Final para Injeção de Imagens Externas

---

## 1. Regras Rigorosas de Produção de Imagens (Mega Drive VDP Compliance)

1. **Formato de Arquivo:** PNG indexado a 4 bits por pixel (exatamente 16 cores por arquivo).
2. **Alinhamento de Dimensões:** Todas as dimensões de spritesheets e tilesets devem ser múltiplos exatos de 8 pixels (1 tile VDP = 8x8 pixels).
3. **Índice 0 (Transparência):** O primeiro slot de cor (índice 0 da paleta) é reservado estritamente como cor transparente para sprites e plano `BG_A` (recomendado: `RGB(0, 0, 0)` ou cor magenta `RGB(255, 0, 255)` identificada como transparent color).
4. **Quantização de Cores (9-bit RGB):** Todos os canais R, G e B devem pertencer ao conjunto discreto `{0, 34, 68, 102, 136, 170, 204, 238}` (equivalente a 3 bits: `0, 2, 4, 6, 8, 10, 12, 14` no hardware original).
5. **Dithering Obrigatório:** Não utilizar gradientes contínuos ou formas planas sólidas. Todas as transições de luz, fumaça, reflexos no asfalto e sombras volumétricas devem empregar *ordered dithering* (padrão xadrez 50%/25%/75%).

---

## 2. Tabela Mestra de Especificação de Assets

| # | Caminho / Nome do Arquivo | Tipo no SGDK | Dimensões Totais (L x A) | Dimensões por Quadro | Qtd. Quadros | Paleta Alocada | Função no Jogo / Descrição Visual |
|---|---------------------------|--------------|--------------------------|----------------------|:------------:|:--------------:|-----------------------------------|
| **1** | `res/bgs/img_gotham_skyline_bgb.png` | `IMAGE` (BEST) | `320 x 224` px | `320 x 224` px | 1 | `PAL0` | Céu noturno Dark Deco de Gotham City com silhueta gótica dos arranha-céus, vitrais iluminados, gárgulas, lua colossal e feixe do Bat-Sinal dithered. |
| **2** | `res/bgs/img_gotham_roadway_bga.png` | `IMAGE` (BEST) | `320 x 224` px | `320 x 224` px | 1 | `PAL1` | Tabuleiro da ponte suspensa de Gotham em perspectiva 3D (Y=0..79 transparente; Y=80..223 asfalto com faixas neon, divisores ciano e vigas de aço). |
| **3** | `res/sprites/spr_batmobile.png` | `SPRITE` (6x3 tiles) | `192 x 24` px | `48 x 24` px | 4 | `PAL2` | Batmóvel do jogador. Quadro 0: Neutro; Quadro 1: Inclinação Esquerda; Quadro 2: Inclinação Direita; Quadro 3: Turbo Afterburner com chama de plasma. |
| **4** | `res/sprites/spr_boss_chassis.png` | `SPRITE` (8x6 tiles) | `64 x 48` px | `64 x 48` px | 1 | `PAL3` | Chassi principal do Tanque Biônico do Duas-Caras (Divisão assimétrica: metade esquerda carmesim esfolada, metade direita verde-ácido com faixas zebradas). |
| **5** | `res/sprites/spr_boss_turret.png` | `SPRITE` (4x4 tiles) | `256 x 32` px | `32 x 32` px | 8 | `PAL3` | Torre giratória com canhão duplo de plasma pesado. 8 quadros angulares cobrindo rotação de -45° a +45° para rastrear o Batmóvel na pista. |
| **6** | `res/sprites/spr_boss_tread_left.png` | `SPRITE` (4x2 tiles) | `128 x 16` px | `32 x 16` px | 4 | `PAL3` | Esteira blindada esquerda do tanque com 4 quadros em loop contínuo de rotação dos elos de aço e engrenagens motrizes. |
| **7** | `res/sprites/spr_boss_tread_right.png` | `SPRITE` (4x2 tiles) | `128 x 16` px | `32 x 16` px | 4 | `PAL3` | Esteira blindada direita do tanque com 4 quadros em loop contínuo de rotação dos elos de aço e engrenagens motrizes. |
| **8** | `res/sprites/spr_boss_missile_pod.png` | `SPRITE` (3x3 tiles) | `48 x 24` px | `24 x 24` px | 2 | `PAL3` | Pod lançador de mísseis. Quadro 0: Escotilha blindada fechada; Quadro 1: Escotilha aberta revelando 4 tubos de mísseis incandescentes. |
| **9** | `res/sprites/spr_drone.png` | `SPRITE` (3x2 tiles) | `48 x 16` px | `24 x 16` px | 2 | `PAL3` | Drones biônicos de escolta aérea. Quadro 0: Voo padrão com visor óptico vermelho; Quadro 1: Propulsores em alta potência com labaredas. |
| **10** | `res/sprites/spr_projectiles.png` | `SPRITE` (2x2 tiles) | `64 x 16` px | `16 x 16` px | 4 | `PAL2` / `PAL3` | Atlas de Projéteis. Q0: Vulcan do Batmóvel; Q1: Micromíssil Batarang; Q2: Esfera pesada de Plasma do Chefe; Q3: Dardo Laser dos Drones. |
| **11** | `res/sprites/spr_particles.png` | `SPRITE` (2x2 tiles) | `64 x 16` px | `16 x 16` px | 4 | `PAL3` | Atlas de Partículas. Q0: Centelha elétrica estrela; Q1: Estilhaço metálico; Q2: Bola de fogo de explosão; Q3: Fumaça volumétrica dithered. |

---

## 3. Especificação Detalhada por Paleta (9-Bit RGB)

### 3.1 `PAL0`: Gotham Skyline & Atmosfera Dark Deco (`bgs/img_gotham_skyline_bgb.png`)
```
Índice 00: RGB(  0,   0,   0) [Transparente / Preto Absoluto]
Índice 01: RGB(  0,   0,  34) [Azul Noturno Profundo]
Índice 02: RGB(  0,  34,  68) [Azul Meia-Noite]
Índice 03: RGB( 34,  34,  68) [Ardósia Gótica]
Índice 04: RGB( 34,  68, 102) [Azul Névoa Urbana]
Índice 05: RGB( 68,  68, 102) [Sombra de Pináculo]
Índice 06: RGB( 68, 102, 136) [Meio-tom Arranha-Céu]
Índice 07: RGB(102, 136, 170) [Destaque de Borda Arranha-Céu]
Índice 08: RGB( 34,   0,  68) [Violeta Crepúsculo]
Índice 09: RGB(102,  34, 102) [Nuvem Roxa]
Índice 10: RGB(170, 136,  34) [Vitral Âmbar Dark Deco]
Índice 11: RGB(238, 204,  68) [Luz de Janela Ouro Brilhante]
Índice 12: RGB(136, 170, 204) [Borda Prateada de Nuvem]
Índice 13: RGB(204, 238, 238) [Feixe de Holofote Bat-Sinal]
Índice 14: RGB(238, 238, 238) [Luar Branco Puro]
Índice 15: RGB(  0,   0,   0) [Preto Sombra Profunda]
```

### 3.2 `PAL1`: Pista em Perspectiva & Deck da Ponte (`bgs/img_gotham_roadway_bga.png`)
```
Índice 00: RGB(  0,   0,   0) [Transparente / Céu Superior]
Índice 01: RGB( 34,  34,  34) [Asfalto Escuro com Textura]
Índice 02: RGB( 68,  68,  68) [Asfalto Meio-Tom]
Índice 03: RGB(102, 102, 102) [Guia / Concreto da Pista]
Índice 04: RGB(136, 136, 136) [Guarda-Corpo Metálico]
Índice 05: RGB(170, 170, 170) [Treliça de Aço da Ponte]
Índice 06: RGB(  0,  68, 102) [Sombra de Vigas da Rodovia]
Índice 07: RGB(  0, 136, 170) [Cabo de Sustentação Ciano]
Índice 08: RGB(  0, 204, 238) [Faixas Divisórias Ciano Neon]
Índice 09: RGB(238, 170,   0) [Refletor Âmbar de Pista]
Índice 10: RGB(238, 238,   0) [Faixa Central Amarela Brilhante]
Índice 11: RGB(136,  34,  34) [Reflexo Vermelho no Asfalto]
Índice 12: RGB(204,  68,  68) [Sinalizador de Alerta Vermelho]
Índice 13: RGB( 34,  68,  68) [Pilar Distante na Bruma]
Índice 14: RGB(204, 204, 204) [Brilho em Viga de Aço]
Índice 15: RGB(238, 238, 238) [Texto de Telemetria / Luz Forte]
```

### 3.3 `PAL2`: Batmóvel & Armamento do Jogador (`sprites/spr_batmobile.png`, etc.)
```
Índice 00: RGB(  0,   0,   0) [Transparente]
Índice 01: RGB(  0,   0,   0) [Preto Obsidiana Chassi]
Índice 02: RGB( 34,  34,  68) [Sombra Blindagem Titânio]
Índice 03: RGB( 68,  68, 102) [Meio-Tom Painel Blindado]
Índice 04: RGB(102, 102, 136) [Destaque de Borda Metálica]
Índice 05: RGB(136, 170, 204) [Reflexo de Vidro do Cockpit]
Índice 06: RGB(204, 238, 238) [Moldura do Para-brisa]
Índice 07: RGB(  0, 136, 204) [Painel Neon Ciano]
Índice 08: RGB(  0, 238, 238) [Faróis de Plasma Ciano]
Índice 09: RGB(238, 204,   0) [Emblema Dourado do Morcego]
Índice 10: RGB(238, 102,   0) [Labareda Laranja da Turbina]
Índice 11: RGB(238,  34,   0) [Núcleo Vermelho do Pós-Combustor]
Índice 12: RGB(238, 238,  68) [Traçante Vulcan Amarelo]
Índice 13: RGB( 34,  34,  34) [Borracha dos Pneus]
Índice 14: RGB(170, 170, 170) [Liga Metálica das Rodas]
Índice 15: RGB(238, 238, 238) [Clarão Branco do Disparo]
```

### 3.4 `PAL3`: Chefe Duas-Caras, Drones & Efeitos (`sprites/spr_boss_*.png`, etc.)
```
Índice 00: RGB(  0,   0,   0) [Transparente]
Índice 01: RGB(  0,   0,   0) [Sombra / Interior do Canhão]
Índice 02: RGB( 34,  68,  34) [Sombra Blindagem Verde-Ácido]
Índice 03: RGB( 68, 136,  68) [Meio-Tom Verde Biônico]
Índice 04: RGB(102, 204, 102) [Destaque Verde Tóxico]
Índice 05: RGB( 68,   0,   0) [Sombra Metal Carmesim]
Índice 06: RGB(136,  34,  34) [Metal Carmesim Esfolado]
Índice 07: RGB(204,  68,  68) [Destaque Carmesim de Aço]
Índice 08: RGB(238,  34,  34) [Sensor Laser Vermelho / Mira]
Índice 09: RGB( 51,  51,  51) [Aço Escuro da Esteira]
Índice 10: RGB(102, 102, 102) [Elo da Esteira Metálica]
Índice 11: RGB(170, 136,  68) [Bronze da Torre do Canhão]
Índice 12: RGB(238, 170,   0) [Bola de Fogo de Plasma Laranja]
Índice 13: RGB(238, 238,   0) [Centelha Elétrica Amarela]
Índice 14: RGB(136, 136, 170) [Liga de Blindagem do Pod]
Índice 15: RGB(238, 238, 238) [Onda de Choque Branca]
```

---

## 4. Declarações Canônicas para o `res/resources.res`

```c
// Backgrounds (Tilemaps & Paletas)
IMAGE img_gotham_skyline_bgb "bgs/img_gotham_skyline_bgb.png" BEST
IMAGE img_gotham_roadway_bga "bgs/img_gotham_roadway_bga.png" BEST

// Sprites do Jogador (Batmóvel)
SPRITE spr_batmobile "sprites/spr_batmobile.png" 6 3 NONE 6

// Módulos do Chefe (Two-Face Siege Dreadnought)
SPRITE spr_boss_chassis "sprites/spr_boss_chassis.png" 8 6 NONE 0
SPRITE spr_boss_turret "sprites/spr_boss_turret.png" 4 4 NONE 0
SPRITE spr_boss_tread_left "sprites/spr_boss_tread_left.png" 4 2 NONE 4
SPRITE spr_boss_tread_right "sprites/spr_boss_tread_right.png" 4 2 NONE 4
SPRITE spr_boss_missile_pod "sprites/spr_boss_missile_pod.png" 3 3 NONE 0

// Inimigos e Escolta
SPRITE spr_drone "sprites/spr_drone.png" 3 2 NONE 8

// Projéteis e Efeitos de Partículas
SPRITE spr_projectiles "sprites/spr_projectiles.png" 2 2 NONE 0
SPRITE spr_particles "sprites/spr_particles.png" 2 2 NONE 4
```
