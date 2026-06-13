# 97 - Tabela Mestre: 180 Técnicas 16-bit

## Campanha: AAA 180 Técnicas 16-bit
**Data:** 2026-05-22  
**Versão:** 1.0

---

## Resumo Executivo

Esta tabela mestre contém as 180 técnicas 16-bit organizadas nos 17 eixos canônicos do documento `95_16bit_effects_aaa_rom_campaign.md`.

---

## Mapeamento por Eixo

### Eixo 01: Profundidade & Movimento (10 técnicas)
- PM-001: Scroll horizontal liso (line_scrolling) - candidate_with_evidence
- PM-002: Scroll vertical controlado (column_scrolling) - partial
- PM-003: Parallax básico 2 planos (multi-plane-composition) - incorporated
- PM-004: Parallax avançado 3+ camadas - incorporated
- PM-005: Câmera suave com damping (fix16) - proposal_only
- PM-006: Câmera com limites de bounds - proposal_only
- PM-007: Momentum e inércia de personagem - proposal_only
- PM-008: Tilemap streaming por coluna (tile_cache_streaming_refcount) - candidate_with_evidence
- PM-009: Scrolling diagonal composto - proposal_only
- PM-010: Câmera com look-ahead - proposal_only

### Eixo 02: Pseudo-3D (10 técnicas)
- P3D-011: Road stack com Z-map básico (pseudo3d_road_stack) - candidate_with_evidence
- P3D-012: Road stack com curvas - candidate_with_evidence
- P3D-013: Road stack com morros - candidate_with_evidence
- P3D-014: Chão falso com perspectiva - proposal_only
- P3D-015: Affine transform limitado (software_affine_pseudo3d) - gap_pure
- P3D-016: Sprite scaling por troca de frames - proposal_only
- P3D-017: Projeção de sombra em piso falso - proposal_only
- P3D-018: Depth sorting por prioridade - proposal_only
- P3D-019: Viagem estelar / warp - proposal_only
- P3D-020: Recusa honesta de Mode 7 - proposal_only (signature_only)

### Eixo 03: Distorção Raster (H-Int) (10 técnicas)
- DR-021: H-Int básico com callback (h_int_control_plane) - partial
- DR-022: HScroll individual por scanline (line_scrolling) - candidate_with_evidence
- DR-023: VSRAM por linha (column_scrolling) - partial
- DR-024: CRAM split / palette swap mid-frame (hint_palette_blending) - candidate_with_evidence
- DR-025: Wobble de tela controlado - proposal_only
- DR-026: Spotlight por H-Int (hint_palette_blending) - candidate_with_evidence
- DR-027: Glitch raster controlado (procedural_raster_glitch_suite) - partial
- DR-028: Árbitro de H-Int único (h_int_control_plane) - partial
- DR-029: Reset simétrico de H-Int (h_int_control_plane) - partial
- DR-030: Seamless line scroll sem jitter (line_scrolling) - candidate_with_evidence

### Eixo 04: Paleta & Cor (10 técnicas)
- PC-031: Fade in/out de paleta completa (palette_cycling) - partial
- PC-032: Fade parcial por range (palette_cycling) - partial
- PC-033: Color cycling / CRAM rotation (palette_cycling) - partial
- PC-034: Flash de paleta (impacto/dano) - proposal_only
- PC-035: Troca de hue / tonalidade - proposal_only
- PC-036: Escala de cinza (grayscale) - proposal_only
- PC-037: Sepia - proposal_only
- PC-038: Color banding intencional - proposal_only
- PC-039: CRAM shock / palette shock (procedural_raster_glitch_suite) - partial
- PC-040: Paleta dupla (dual palette) - proposal_only

### Eixo 05: Iluminação Dinâmica (10 técnicas)
- ID-041: Shadow/Highlight básico (shadow_highlight_mode) - partial
- ID-042: Lanterna móvel com S/H (masked_shadow_highlight_lighting) - partial
- ID-043: Flash de luz (explosão) - proposal_only
- ID-044: Godrays falsos por tiles - proposal_only
- ID-045: Glow por troca de paleta - proposal_only
- ID-046: Piscada de cor para alerta - proposal_only
- ID-047: Spotlight móvel com máscara (masked_shadow_highlight_lighting) - partial
- ID-048: Iluminação direcional fake - proposal_only
- ID-049: Slot audit S/H (shadow_highlight_slot_rule) - partial
- ID-050: Recusa honesta de alpha blending real - proposal_only (signature_only)

### Eixo 06: Transparência & Composição (10 técnicas)
- TC-051: Index 0 como transparência - proposal_only
- TC-052: Priority bit para sobreposição - proposal_only
- TC-053: Dithering como transparência fake (dithering_crt_smearing) - partial
- TC-054: Mesh transparency - proposal_only
- TC-055: Pseudo-alfa por tiles intercalados - proposal_only
- TC-056: Premix honesto de sprites/tiles - proposal_only
- TC-057: Composição BG_A + BG_B (multi-plane-composition) - incorporated
- TC-058: Cruciform de prioridade - proposal_only
- TC-059: Recusa de transparência real por canal - proposal_only (signature_only)
- TC-060: Dithering + S/H combinado (dithering_crt_smearing) - partial

### Eixo 07: Zoom & Escala (10 técnicas)
- ZE-061: Sprite zoom por troca de frames - proposal_only
- ZE-062: Prerender de zoom multi-frame - proposal_only
- ZE-063: Raster zoom por H-Int (fake) - proposal_only
- ZE-064: Scaling de tiles por repetição - proposal_only
- ZE-065: Recusa de sprite scaling por hardware - proposal_only (signature_only)
- ZE-066: Escala de boss por mosaico (bg_b_bypassing) - partial
- ZE-067: Zoom de câmera com troca de tiles - proposal_only
- ZE-068: Miniatura de mundo por tilemap - proposal_only
- ZE-069: Escala por skip de pixels - proposal_only
- ZE-070: Escala por duplicação de pixels - proposal_only

### Eixo 08: Rotação (10 técnicas)
- RO-071: Rotação prerenderizada 8 direções - proposal_only
- RO-072: Rotação prerenderizada 16 direções - proposal_only
- RO-073: Sheet angular 360/16 - proposal_only
- RO-074: Rotação por tile remapping (fake) - proposal_only
- RO-075: Recusa de rotação por hardware - proposal_only (signature_only)
- RO-076: Rotação de background por HScroll - proposal_only
- RO-077: Sprite rotation por blit software - proposal_only (hazardous_experimental)
- RO-078: Rotação 180° por flip (tile_flipping) - incorporated
- RO-079: Rotação de paleta para efeito - proposal_only
- RO-080: Simulação de roda girando - proposal_only

### Eixo 09: Foreground / Background (10 técnicas)
- FB-081: Priority bit para foreground (priority_split_foreground) - candidate_with_evidence
- FB-082: Foreground destrutivo (priority_split_foreground) - candidate_with_evidence
- FB-083: Sticky decor - proposal_only
- FB-084: Tile masks para oclusão - proposal_only
- FB-085: Mutação de tiles (mutable_tile_decal_mutation) - gap_pure
- FB-086: Multicamadas BG_A + BG_B + sprites (multi-plane-composition) - incorporated
- FB-087: Boss como tilemap (bg_b_bypassing) - partial
- FB-088: Decomposição de tiles em camadas - proposal_only
- FB-089: Foreground animado (vento) - proposal_only
- FB-090: Parallax de nuvens (multi-plane-composition) - incorporated

### Eixo 10: Background Animado (10 técnicas)
- BA-091: Tile animation de água (palette_cycling) - partial
- BA-092: Tile animation de lava (palette_cycling) - partial
- BA-093: Ecologia de background (aves, nuvens) - proposal_only
- BA-094: Cloud scroll com parallax - proposal_only
- BA-095: Waterfall por tile animation + palette cycling (palette_cycling) - partial
- BA-096: Background reativo (mudança por estado) - proposal_only
- BA-097: Fog/nevoeiro por tile dithering - proposal_only
- BA-098: Estrelas cintilantes por palette cycling (palette_cycling) - partial
- BA-099: Fogo de fundo por tile animation + S/H (shadow_highlight_mode) - partial
- BA-100: Background scrolling infinito (tile_cache_streaming_refcount) - candidate_with_evidence

### Eixo 11: HUD / UI (10 técnicas)
- HU-101: HUD básico com WINDOW (window_plane_static_hud) - candidate_with_evidence
- HU-102: Lifebar com tiles graduados (window_plane_static_hud) - candidate_with_evidence
- HU-103: Score com fonte custom - proposal_only
- HU-104: Minimapa de tiles - proposal_only
- HU-105: Retículo de mira - proposal_only
- HU-106: Ícones de status de sprite - proposal_only
- HU-107: Barra de energia com cores dinâmicas - proposal_only
- HU-108: Contador de tempo em tiles - proposal_only
- HU-109: Feedback visual de combo - proposal_only
- HU-110: HUD com contraste de leitura - proposal_only

### Eixo 12: Texto Narrativo (10 técnicas)
- TN-111: Texto limpo em tiles (TidyText) - proposal_only
- TN-112: Glyph cache para fonte - proposal_only
- TN-113: Typewriter effect - proposal_only
- TN-114: Texto cinematográfico (centered) - proposal_only
- TN-115: Balão de diálogo com sprite - proposal_only
- TN-116: Som de digitação - proposal_only
- TN-117: Multi-linha com quebra automática - proposal_only
- TN-118: Retrato falante com expressão - proposal_only
- TN-119: Texto com cor pulsante - proposal_only
- TN-120: Legibilidade em 320x224 - proposal_only

### Eixo 13: Cinemático / Cutscene (10 técnicas)
- CC-121: FSM de cutscene (contextual_scene_transition_system) - documented
- CC-122: Pan de câmera lento - proposal_only
- CC-123: Wipe transition por tile mask (contextual_scene_transition_system) - documented
- CC-124: Letterbox (barras pretas) - proposal_only
- CC-125: Retrato em painel (manga) - proposal_only
- CC-126: Fullscreen bitmap limitado - proposal_only
- CC-127: Transição com fade + scroll (contextual_scene_transition_system) - documented
- CC-128: Corte seco com som - proposal_only
- CC-129: Teardown simétrico (contextual_scene_transition_system) - documented
- CC-130: Sequência timeline com sincronismo - proposal_only

### Eixo 14: Combate / Impacto (10 técnicas)
- CI-131: Hitstop (congelamento de frames) - proposal_only
- CI-132: Flash de tela no impacto - proposal_only
- CI-133: Sparks de colisão (sprites) - proposal_only
- CI-134: Knockback com inércia - proposal_only
- CI-135: Camera shake (tremor de câmera) - proposal_only
- CI-136: Slow motion parcial - proposal_only
- CI-137: Flash frame de impacto - proposal_only
- CI-138: Screen shake proporcional ao dano - proposal_only
- CI-139: Hit sparks com palette cycling - proposal_only
- CI-140: Combos com feedback visual - proposal_only

### Eixo 15: Partículas & Atmosfera (10 técnicas)
- PA-151: Chuva por sprites - proposal_only
- PA-152: Neve por sprites - proposal_only
- PA-153: Fumaça (sprites com fade) - proposal_only
- PA-154: Bolhas subindo - proposal_only
- PA-155: Folhas caindo - proposal_only
- PA-156: Marcas persistentes de degradação - proposal_only
- PA-157: Estilhaços de colisão - proposal_only
- PA-158: Poeira ao andar - proposal_only
- PA-159: Emanação de energia - proposal_only
- PA-160: Chuva com splash no chão - proposal_only

### Eixo 16: Audio-Visual Sync (10 técnicas)
- AV-161: XGM2 básico com stingers - incorporated
- AV-162: Ducking de BGM para SFX - incorporated
- AV-163: Beat FX sincronizado - incorporated
- AV-164: Voice/lip sync básico - incorporated
- AV-165: Pulse visual por música - proposal_only
- AV-166: PCM multiplexing (xgm2_pcm_multiplexing) - gap_pure
- AV-167: Custom Z80 audio drivers - incorporated
- AV-168: PCM streaming/ring buffer - incorporated
- AV-169: DAC direct manipulation - incorporated
- AV-170: PSG direct control - incorporated

### Eixo 17: Outros / Matemática / Infra (10 técnicas)
- OM-171: LUTs trigonométricas (forward_kinematics) - gap_pure
- OM-172: Slope detection para plataformas - proposal_only
- OM-173: DMA queue organizado - incorporated
- OM-174: SRAM read/write seguro - incorporated
- OM-175: Raycast 2D básico - proposal_only
- OM-176: Interlace 448 mode (interlaced_448_display_mode) - gap_pure (special_scene_only)
- OM-177: Fix16/filtragem de input - proposal_only
- OM-178: Pool de objetos estático - incorporated
- OM-179: Sistema de estados (FSM) - incorporated
- OM-180: Profiling de frame-time - proposal_only

---

## Estatísticas

| Status | Quantidade |
|--------|------------|
| incorporated | 12 |
| candidate_with_evidence | 10 |
| partial | 14 |
| gap_pure | 6 |
| documented | 3 |
| proposal_only | 135 |

**Total: 180 técnicas**
