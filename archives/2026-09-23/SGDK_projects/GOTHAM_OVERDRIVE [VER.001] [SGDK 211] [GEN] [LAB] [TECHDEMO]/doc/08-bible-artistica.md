# 08 - Bíblia Artística — GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

## 1. Concept Art Direction Brief

- **visual_purpose:** Estabelecer uma atmosfera Dark Deco dos anos 90 inspirada em *Batman: The Animated Series* e *The Adventures of Batman & Robin* (Mega Drive), com foco em perseguição em alta velocidade, combate veicular pseudo-3D e escala colossal de chefe modular.
- **gameplay_readability_goal:** O jogador deve identificar instantaneamente em 1 frame a trajetória dos projéteis, o ângulo da torre do chefe, o estado de pós-combustor do Batmóvel e as zonas seguras da pista.
- **style_selection_method:** `tone_driven` e `gameplay_driven` (alto contraste, iluminação dramática, silhuetas fortes e dithering ordenado).
- **hardware_constraints:** 4 paletas de 16 cores (15 visíveis + 1 transparente), VRAM compartilhada entre BG_A, BG_B e Sprites, 80 hardware sprites max, limites VDP H40 (20 sprites/scanline, 320 px/scanline), 60 FPS NTSC estáveis.
- **market_differentiation:** Uso de estética autoral Dark Deco com texturização por dithering ordenado, silhuetas de arquitetura gótica e divisão visual assimétrica do chefe (metade carmesim blindada, metade verde-ácido corroída com listras de perigo).

### 2. Nove Eixos Visuais

1. **dimensionality:** Pseudo-3D multi-eixo com inclinação de pista em perspectiva, horizonte fixo a Y=80 e parallax em BG_B.
2. **fidelity_detail:** Pixel art rigoroso respeitando grid 8x8, com microdetalhes metálicos, frestas de painel e vitrais acesos.
3. **color_theory:** Esquema Dark Deco com azul-meia-noite, ardósia, preto obsidiana, contrastando com luzes âmbar/ouro e detalhes ciano plasma / verde tóxico.
4. **lighting_shadow:** Iluminação volumétrica com ordered dithering (Bayer), luar de alto contraste e feixe dinâmico do Bat-Sinal.
5. **shape_language:** Linhas pontiagudas góticas (pináculos, barbatanas do Batmóvel) combinadas com formas angulares industriais do dreadnought.
6. **surface_material:** Aço escovado, asfalto com ranhuras, titânio fosco, liga de bronze e blindagem acidificada.
7. **ui_integration:** Telemetria limpa em overlay integrada sobreposta sem poluir a ação de combate.
8. **motion_style:** Animação a 60 FPS com rotação de torre de 8 direções, esteiras contínuas e transições suaves de inclinação veicular.
9. **vfx_language:** Efeitos de faíscas elétricas em estrela, estilhaços de metal, labaredas de plasma e fumaça volumétrica dithered.

### 3. Cinco Gates de Aprovação

- **scope_style_constraints:** `pass` (todos os assets consom exatamente 4 bits/pixel e 16 cores).
- **silhouette_shape_language:** `pass` (Batmóvel, chefe e drones claramente distinguíveis).
- **value_hierarchy:** `pass` (fundo com luma mais baixa, pista com linhas de guia neon, sprites com destaque em primeiro plano).
- **palette_role_map:** `pass` (PAL0: Skyline, PAL1: Pista, PAL2: Jogador, PAL3: Chefe/Inimigos/FX).
- **polish_vfx_gameplay_signal:** `pass` (feedback imediato de dano, flashes e partículas com dispersão espacial calculada).

## 4. Diretrizes de Produção de Assets

- Todos os assets são armazenados em PNG indexado 4-bit na pasta `res/`.
- Fontes autorais registradas e rastreadas com hash SHA-256 em `data/source_art/` e `doc/asset_provenance_manifest.json`.
- Quantização estrita no espaço de cores 9-bit RGB do Mega Drive (`{0, 34, 68, 102, 136, 170, 204, 238}`).
