# 13 - Especificacao Tecnica por Cena - Celestial Chase Revive

## Status

Specs gerais em planejamento. O Sector 01 possui medicao tecnica da `build_v020`; cenas posteriores continuam apenas documentadas.

## Contratos Transversais

### Technique Usage Sync

IDs do registry selecionados nesta fase documental:

- `dma_transfer_safety`
- `line_scrolling`
- `pseudo3d_road_stack`
- `camera_scroll_management`
- `hitstop_camera_shake_feedback`
- `window_plane_static_hud`
- `palette_state_transitions`
- `prerendered_sprite_scaling`
- `xgm2_audio_architecture`
- `save_sram_checksum_redundancy`

Os IDs continuam sendo o contrato de projeto. No Sector 01, `window_plane_static_hud`, `pseudo3d_road_stack`, camera, feedback e SRAM ja possuem evidencia runtime tecnica. Isso nao promove `ready_for_aaa`, pois arte e audio definitivos continuam bloqueados.

### Route Decision Record

- `context_type`: `aaa_game`.
- `dominant_route`: `scene_architecture`.
- `resource_loading_model`: `scene_local_preload` no primeiro slice.
- `asset_strategy`: arte autoral premium em `data/source_art`, sem copiar benchmark.
- `evidence_required`: build, validation, res graph, runtime metrics, screenshot BlastEm, `save.sram`, `visual_vdp_dump.bin`, freshness e closeout.
- `forbidden_shortcuts_until_evidence`: sem Mode 7, sem fallback procedural como asset final, sem claim de AAA.

### Baseline Arquitetural

Perfil: `aaa_layered`.

Baseline prioritario: tilemap/scene-local preload com divisao clara:

- BG_B: atmosfera, profundidade e horizonte.
- BG_A: estrada, telegraphs, marcas de rota e foreground proximo.
- WINDOW: HUD, texto curto e dialogo quando aplicavel.
- Sprites: Lio, hazards, pickups, boss parts e FX.

Streaming guiado por camera fica como evolucao futura. Primeiro slice deve provar a cena local antes de ampliar mundo.

### Contratos Executaveis

- `doc/track_data_format_contract.json`
- `doc/collision_system_contract.json`
- `doc/hud_layout_contract.json`
- `doc/sprite_animation_contract.json`
- `doc/progression_tuning_tables.json`
- `doc/asset_production_spec.json`
- `doc/boss_attack_pattern_contract.json`
- `doc/game_flow_contract.json`
- `doc/build_system_contract.json`
- `doc/concept_art_brief.md`
- `doc/creative_cohesion_pass.md`
- `doc/pursuer_presence_contract.json`
- `doc/lumen_pressure_economy_contract.json`
- `doc/sector_mechanic_identity_contract.json`
- `doc/signature_setpiece_contract.json`
- `doc/reactive_music_gameplay_contract.json`
- `doc/replayability_score_contract.json`

### Budget Semantics

Todo budget futuro deve separar:

- `rom_asset_cost`;
- `vram_resident_set`;
- `load_time_dma_cost`;
- `per_frame_dma_cost`;
- `active_animation_window`;
- `scene_local_scope`;
- `scanline_sprite_pressure`.

## Scene Roadmap

| ID | Nome | Papel | Status |
|---|---|---|---|
| S00 | `branding_sigil` | abertura de produto | documentado |
| S01 | `title_menu` | front-end | documentado |
| S02 | `opening_catalyst_cutscene` | cutscene | documentado |
| S03 | `race_start_handoff` | transicao cutscene->gameplay | documentado |
| S04 | `sector_01_farol_quebrado` | gameplay | testado_em_emulador_tecnico |
| S05 | `upgrade_beacon_intermission` | upgrade | documentado |
| S06 | `sector_02_meteor_garden` | gameplay | documentado |
| S07 | `sector_03_glass_bridge` | gameplay | futuro_arquitetural |
| S08 | `sector_04_shadow_tunnel` | gameplay | futuro_arquitetural |
| S09 | `boss_approach_crown_road` | setpiece | documentado |
| S10 | `final_boss_master_pursuer` | boss | documentado |
| S11 | `ending_result` | final/resultado | documentado |
| S12 | `credits_roll` | creditos | documentado |

### Cena 0 - `branding_sigil`

- Papel: front-end curto.

Objetivo: apresentar identidade sem parecer template.

Contratos:

- `doc/brand_identity_manifest.json`
- `doc/ui_pixel_surface_contract.json`
- `doc/text_presentation_profile.json`

Surfaces:

- BG_B: gradiente tileado discreto ou fundo estatico autoral.
- BG_A: sigilo/logo.
- WINDOW: livre.
- Sprites: brilho opcional.

Logo:

- Texto principal: `CELESTIAL CHASE REVIVE`.
- Metafora visual: estrada luminosa dobrando sob coroa escura.
- Leitura vence ornamento: o nome precisa sobreviver em silhueta, monocromatico, thumbnail e fundo dinamico.
- SGDK default font e proibida para identidade final.

Budget alvo:

- BG total <= 320 tiles.
- Sprites <= 8 links.
- Sem H-Int.

Evidencia futura: screenshot BlastEm e regressao de menu.

### Cena 1 - `title_menu`

- Papel: menu.

Objetivo: comunicar corrida celeste e Mestre Perseguidor desde a primeira tela.

Contratos:

- `doc/front_end_menu_contract.json`
- `doc/brand_identity_manifest.json`
- `doc/ui_pixel_surface_contract.json`
- `doc/glyph_manifest.json`

Surfaces:

- BG_B: ceu profundo e farois distantes.
- BG_A: estrada ou arco do Farol-Matriz.
- WINDOW: comandos curtos.
- Sprites: cursor e pulso de selecao.

Budget alvo:

- BG_B <= 320 tiles.
- BG_A <= 260 tiles.
- Fonte/cursor <= 48 tiles.
- Per-frame DMA quase zero.

Entradas:

- `START RUN`
- `UPGRADES`
- `RECORDS`
- `CREDITS`

Politica de fonte:

- Fonte custom bitmap obrigatoria para entrega visual.
- Corpo de menu em 8px, baseline de 8px e sombra de 1px quando o fundo tiver movimento.
- Fonte SGDK default fica restrita a smoke test/debug.

Riscos:

- menu parecer debug;
- texto competir com logo;
- one-note palette.

### Cena 12 - `credits_roll`

- Papel: menu de creditos e fechamento autoral/legal.

Objetivo: permitir creditos desde o primeiro slice sem comprometer leitura pixel-perfect.

Contratos:

- `doc/credits_contract.json`
- `doc/text_presentation_profile.json`
- `doc/ui_pixel_surface_contract.json`

Surfaces:

- BG_B: ceu revivido calmo com farois distantes.
- BG_A ou WINDOW: cards paginados de creditos.
- Sprites: cursor/indicador opcional.

Budget alvo:

- Fonte/cards <= 96 tiles.
- Sprites <= 2 links.
- DMA apenas em troca de pagina ou transicao.

Regras:

- Credit roll inicial usa paginas, nao scroll subpixel.
- START so retorna ao title apos a primeira pagina ficar visivel por 60 frames.
- Nomes reais podem expandir charset apenas apos revisao de budget.

Riscos:

- creditos com scroll irregular;
- texto pequeno demais em 320x224;
- nomes finais ausentes;
- SGDK default font aparecer em entrega.

### Cena 2 - `opening_catalyst_cutscene`

- Papel: cutscene de alta qualidade.

Objetivo: introduzir evento catalizador e entregar controle em ritmo cinematografico.

FSM: definida em `doc/12-roteiro.md` e `doc/contracts/opening_cutscene_contract.json`.

Contrato de cutscene:

- `fsm_script`: `doc/contracts/opening_cutscene_fsm_script.json`
- `resource_plan`: `doc/contracts/opening_cutscene_resource_plan.json`
- `panel_layout`: `doc/contracts/opening_cutscene_panel_layout.json`
- `palette_script`: `doc/contracts/opening_cutscene_palette_script.json`
- `text_timing_map`: `doc/contracts/opening_cutscene_text_timing_map.json`
- `audio_cue_map`: `doc/contracts/opening_cutscene_audio_cue_map.json`
- `teardown_plan`: `doc/contracts/opening_cutscene_teardown_plan.json`
- `evidence_plan`: `doc/contracts/opening_cutscene_evidence_plan.json`
- `cinematic_storyboard_contract`: `doc/contracts/opening_cinematic_storyboard_contract.json`

Surfaces por estado:

- BG_B: painel distante ou fundo atmosferico.
- BG_A: painel principal, close-up ou objeto.
- WINDOW: texto typewriter.
- Sprites: olhos/blink, brilho do Nucleo Lumen, shards.

Budget alvo por estado:

- Painel fullscreen apenas se tile count e paleta passarem; default e painel/crop.
- Glyph subset por estado.
- Preload permitido entre estados com controle bloqueado.
- Sprite pressure <= 12 links.

Motion beats obrigatorios:

- pan no Farol-Matriz;
- blink/reaction no close de Lio;
- palette pulse no Nucleo;
- shake/flash no rompimento;
- handoff limpo para corrida.

Evidencia futura:

- screenshot dedicada da cutscene;
- runtime_metrics com `scene_id` correto;
- baseline visual;
- `visual_vdp_dump.bin` se houver suspeita de paleta/VRAM.

### Cena 3 - `race_start_handoff`

- Papel: cutscene de transicao formal para gameplay.

Objetivo: transformar a ultima composicao da cutscene na primeira leitura jogavel.

Contrato:

- `doc/contracts/race_start_handoff_contract.json`
- `fsm_script`: `doc/contracts/race_start_handoff_fsm_script.json`
- `resource_plan`: `doc/contracts/race_start_handoff_resource_plan.json`
- `panel_layout`: `doc/contracts/race_start_handoff_panel_layout.json`
- `palette_script`: `doc/contracts/race_start_handoff_palette_script.json`
- `text_timing_map`: `doc/contracts/race_start_handoff_text_timing_map.json`
- `teardown_plan`: `doc/contracts/race_start_handoff_teardown_plan.json`
- `evidence_plan`: `doc/contracts/race_start_handoff_evidence_plan.json`
- `cinematic_storyboard_contract`: `doc/contracts/race_start_handoff_cinematic_storyboard_contract.json`
- input bloqueado durante 60 frames finais da cutscene;
- letterbox recolhe;
- HUD aparece apenas apos reset do owner de WINDOW;
- musica troca de `opening_crack` para `race_intro`;
- scrolls iniciam zerados e aceleram por LUT.

Risco: fade mascarar falta de teardown.

Nota operacional: `scene_contract_compiler.ps1` ainda nao compila `cutscene_contract`
a partir desta lista. Ate o wrapper receber essa melhoria, estes contratos sao
a fonte de planejamento da cena, enquanto `doc/scene-contracts.json` continua
um artefato compilado limitado.

### Cena 4 - `sector_01_farol_quebrado`

- Papel: gameplay first playable.

Objetivo: provar corrida basica, Pulse e pressao.

Contratos:

- `doc/track_data_format_contract.json`
- `doc/sector_01_track_plan.json`
- `doc/collision_system_contract.json`
- `doc/entity_archetype_manifest.json`
- `doc/hud_layout_contract.json`
- `doc/sprite_animation_contract.json`
- `doc/progression_tuning_tables.json`

Mecanicas:

- 3 faixas;
- salto;
- coleta Lumen;
- Pulse;
- dano;
- pressao;
- resultado curto.

Surfaces:

- BG_B: ceu/farol distante.
- BG_A: estrada, telegraphs e marcas.
- WINDOW: HUD de integridade, Lumen, pressao.
- Sprites: Lio, sombra, hazards, pickups, FX.

Budget alvo:

- BG_B <= 360 tiles.
- BG_A <= 280 tiles.
- HUD/fonte <= 64 tiles.
- Sprite reserve inicial >= 640 tiles, a calibrar por `SPR_initEx`.
- Max scanline sprites alvo <= 18.
- Total links alvo <= 72.
- Per-frame DMA: HScroll table + SAT + pequenos updates; sem streaming pesado.

Snapshot medido `build_v020` (2026-06-19):

- ROM: 131072 bytes, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.
- Estrada: 32 tiles fonte, 17 tiles exatos residentes e 16 classes unicas considerando flips.
- Paleta: zero conflito por tile e indices dentro do dominio 4bpp.
- Reserva automatica de sprites: 420 tiles por `SPR_init()` SGDK 2.11.
- Fonte reservada: 96 tiles; sistema: 16 tiles.
- Overlap de ranges VRAM: zero.
- Runtime success: 1800 amostras, zero overbudget, CPU max 53%, media 21,55%, p95 34%.
- Runtime failure: 1800 amostras, zero overbudget, CPU max 53%, media 19,56%, p95 34%.
- Sprite engine peak: 15 links; pior scanline: 9 sprites.
- Work RAM estatica: 10.720 bytes usados de 65.536; 54.816 bytes restantes.
- WINDOW/HUD: observado no BlastEm sem bleed de hazards/pickups na captura do Beacon.
- VLAB e MDRT presentes em SRAM; `visual_vdp_dump.bin` capturado.
- O warning central `code_loaded_tiles_unmeasured` permanece por limitacao do scanner, que classifica chamadas de nametable como carregamento de tiles. O laudo medido acima e os ranges permanecem a evidencia tecnica aplicavel.

Status de budget: `nao_validado`. O resultado acima e estimativa de residencia, nao `validado_budget`.

Dados:

- 96 `track_steps` iniciais.
- 18 eventos autorados, incluindo primeira presenca do perseguidor.
- `track_step` = 16 frames NTSC.
- lane X inicial: 112, 160, 208.
- player Y inicial: 168.

Identidade:

- Mestre Perseguidor aparece como silhueta distante em BG_B quando Pressure cresce.
- Lumen pressure possui grace inicial para ensinar sem punir cedo demais.
- O jogador deve sair do setor sabendo que a luz carregada e percebida pela ameaca.

Recuo:

- remover line scroll fino;
- reduzir hazards simultaneos;
- reduzir largura de BG_A;
- manter leitura antes de detalhe.

### Cena 5 - `upgrade_beacon_intermission`

- Papel: menu de escolha de upgrade.

Objetivo: introduzir evolucao sem quebrar ritmo.

Surfaces:

- BG_B: farol revivido.
- BG_A: duas ou tres cartas de upgrade.
- WINDOW: descricao curta.
- Sprites: cursor, brilho e confirmacao.

Regras:

- 2 escolhas no primeiro slice.
- Cada escolha altera regra jogavel.
- Sem texto longo.

Budget alvo:

- Preload permitido.
- Sem HScroll.
- Sem scanline pressure relevante.

### Cena 6 - `sector_02_meteor_garden`

- Papel: gameplay da segunda corrida.

Objetivo: provar que upgrade muda decisao.

Novidades:

- padroes diagonais;
- pickup tentador fora da rota segura;
- meteoros com telegraph longo;
- meteoros aterrissam e viram bloqueios persistentes por 3 a 5 `track_steps`.

Regra unica:

- `meteor_impact_persistent`: depois do impacto, a faixa fica perigosa por uma janela curta. O jogador precisa lembrar onde caiu, nao apenas reagir ao frame atual.

Recuo:

- se persistencia custar demais, usar 1 meteoro persistente por vez e reduzir FX.

Budget alvo: igual S04 com ate 2 hazards simultaneos extras.

### Cena 7 - `sector_03_glass_bridge`

- Papel: gameplay da terceira corrida.

Objetivo: transformar ritmo visual em regra de rota.

Novidades:

- faixas de vidro somem e retornam em compasso previsivel;
- telegraph por brilho/rachadura antes de a faixa ficar insegura;
- `Comet Veil` protege de um erro, mas nao ignora leitura de ritmo.

Regra unica:

- `glass_lane_missing`: uma faixa fica insegura por janela curta. A rota segura e previsivel, nao aleatoria.

Budget alvo:

- BG_A precisa reservar tiles para rachadura/ausencia de faixa.
- Sem alpha blending; usar troca de tiles/paleta.
- Max 2 faixas inseguras simultaneamente, mas nunca todas as 3.

### Cena 13 - `shattered_lane_gauntlet`

- Papel: gameplay de momento assinatura entre S07 e S08.

Contrato: `doc/signature_setpiece_contract.json`.

Objetivo: o Mestre Perseguidor golpeia a estrada, quebra duas faixas e deixa apenas uma faixa segura por 180 frames.

Regras:

- `lane_mask` controla a faixa segura.
- Destrocos caem sem cobrir a unica faixa.
- Camera shake e hitstop sao visuais; colisao permanece em coordenadas estaveis.
- O momento nao pode virar instant kill.

### Cena 8 - `sector_04_shadow_tunnel`

- Papel: gameplay de corrida de pressao maxima.

Objetivo: cobrar leitura por sombra/audio antes do boss approach.

Novidades:

- telegraph visual mais curto;
- audio ou sombra avisa antes do hazard completo;
- Lumen alto deixa a presenca do perseguidor mais agressiva.

Regra unica:

- `audio_first_warning`: cue sonora/sombra aparece antes do sprite completo. O jogador aprende a ouvir a pista.

Budget alvo:

- reduzir decoracao antes de reduzir telegraph.
- manter HUD e lane sempre legiveis.
- Pressure alto pode intensificar paleta, mas sem alpha blending real.

### Cena 9 - `boss_approach_crown_road`

- Papel: boss setpiece de aproximacao.

Objetivo: mostrar que o Perseguidor deixou de ser fundo e esta invadindo a pista.

Surfaces:

- BG_B: chifres/horizonte.
- BG_A: estrada rachada e weak-point previews.
- Sprites: cascos/sombra/poeira.
- WINDOW: HUD reduzido.

Tecnicas:

- prerendered_sprite_scaling para aproximacao por estagios;
- camera_scroll_management;
- hitstop/shake para impactos;
- palette_state_transitions.

Budget alvo:

- Boss approach <= 16 sprites por scanline.
- Pior quadro considera Lio + hazards + boss shadow + HUD.

### Cena 10 - `final_boss_master_pursuer`

- Papel: boss final.

Objetivo: converter a persecucao em duelo de rota e weak points.

Fases:

1. Chifres: ondas laterais.
2. Cascos: impactos de pista.
3. Nucleo: janela Pulse ofensiva.

Arquitetura visual:

- opcao A: boss por sprites pre-renderizados com poda;
- opcao B: plane takeover parcial em BG_A para torso/chifres;
- opcao C: painel pre-renderizado durante ataques especiais.

Decisao inicial: `cabe com recuo`. Nao implementar boss modular ate contrato runtime existir.

Contrato de ataque:

- `doc/boss_attack_pattern_contract.json`
- weakpoints possuem hits requeridos e janelas Pulse;
- corpo do boss e visual-only;
- dano ao jogador vem de entidades de ataque;
- toda sequencia precisa preservar faixa segura legivel.

Budget alvo:

- Max scanline sprites <= 18 alvo, <= 20 limite.
- Total links <= 72 alvo.
- BG_A pode sacrificar detalhe de estrada durante plane takeover.
- HUD reduzido para 1 linha.

Evidencia obrigatoria futura:

- sprite_scanline_pressure_report;
- vram_residency_report;
- screenshot dedicada;
- motion evidence;
- human perceptual approval antes de AAA.

### Cena 11 - `ending_result`

- Papel: menu de resultado/final.

Objetivo: fechar a corrida sem softlock e registrar score/progresso.

Surfaces:

- BG_B: farois revividos ou sombra falha.
- BG_A: card de resultado.
- WINDOW: opcoes.

Persistencia:

- quando SRAM estiver ativa, salvar upgrade flags e melhor tempo/score com checksum.

## Laudo Preliminar de Budget

Decisao global atual: `sector01_cabe_medido`; cenas futuras continuam `cabe com recuo`.

Motivo:

- a corrida base do Sector 01 foi medida na `build_v020`, sem overbudget, overlap VRAM ou pressao critica de sprites;
- os assets medidos continuam placeholders e nao autorizam promocao visual;
- boss final e o maior risco de scanline/VRAM;
- cutscene e segura se usar FSM por estado, nao fullscreen residente total;
- tecnicas LABORATORIO foram adiadas.

Status: budget tecnico do Sector 01 validado por evidencia independente; `validado_budget` global do produto permanece falso no validador central por bloqueio criativo e pelo falso positivo `code_loaded_tiles_unmeasured`.
