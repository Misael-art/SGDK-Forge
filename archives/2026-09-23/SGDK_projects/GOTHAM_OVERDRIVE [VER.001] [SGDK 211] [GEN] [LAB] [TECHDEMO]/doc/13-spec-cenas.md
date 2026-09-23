# 13 - Especificação de Cenas — GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

## 1. Mapa de Cenas do Projeto

| Cena | Símbolo | Função | Orçamento VRAM | Técnicas Ativas |
|------|---------|--------|----------------|-----------------|
| `APP_SCENE_TECHDEMO` | `SCENE_techdemo` | Demonstração técnica jogável, combate e telemetria | BG_A: 180 tiles, BG_B: 160 tiles, Sprites: 280 tiles | `line_scrolling`, `column_scrolling`, `modular_boss`, `particles`, `dynamic_palette` |

## 2. Orçamento Detalhado da Cena Principal (`SCENE_techdemo`)

### 2.1 Planos de Fundo
- **Layer B (`BG_B`)**: Céu Dark Deco e Silhueta de Gotham City (`img_gotham_skyline_bgb`, Paleta 0).
  - Scrolling: `HSCROLL_LINE` independente para parallax celestial, oscilação da lua e skyline.
- **Layer A (`BG_A`)**: Pista em Perspectiva e Ponte de Gotham (`img_gotham_roadway_bga`, Paleta 1).
  - Scrolling: `HSCROLL_LINE` com curvatura parabólica e distorção de velocidade; `VSCROLL_COLUMN` com inclinação lateral.

### 2.2 Paletas de Hardware
- **PAL0**: Gotham Skyline (Noturno, roxo gótico, feixe do Bat-Sinal com cycling, preto puro).
- **PAL1**: Pista e Barreiras (Asfalto escuro, faixas amarelas, divisores ciano neon, refletores).
- **PAL2**: Batmóvel e Efeitos do Jogador (Preto obsidiana, blindagem titânio, cockpit ciano, labareda laranja/vermelha, traçantes amarelos).
- **PAL3**: Chefe Two-Face Dreadnought, Drones e Partículas (Verde tóxico biónico, vermelho carmesim esfolado, bronze, orbes de plasma, centelhas).

### 2.3 Sprites e Entidades
- **Batmóvel (Jogador)**: 1 sprite (48x24 px, 4 frames).
- **Chefe Two-Face**: 5 sprites modulares (Chassi 64x48, Torre giratória 32x32, 2 Esteiras 32x16, Pod de mísseis 24x24).
- **Drones de Escolta**: Até 4 sprites (24x16 px).
- **Pool de Projéteis**: Até 24 sprites (16x16 px).
- **Pool de Partículas**: Até 24 sprites (16x16 px).
- **Total de Hardware Sprites no Pico**: ~50 a 60 sprites (dentro do limite seguro de 80 do console).

### 2.4 Contrato de Taxa de Quadros e DMA
- **Target FPS**: 60 FPS estáveis (NTSC) / 50 FPS (PAL).
- **Transfers DMA**: Enfileirados com segurança via `DMA_QUEUE` no VBlank.
