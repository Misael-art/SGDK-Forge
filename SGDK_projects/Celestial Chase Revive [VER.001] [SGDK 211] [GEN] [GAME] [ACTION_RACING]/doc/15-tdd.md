# 15 - TDD - Celestial Chase Revive

## Status

TDD de especificacao. Nenhum modulo ainda foi implementado.

## Objetivo Tecnico

Construir um runtime SGDK 2.11 com cenas formais, corrida por faixas, cutscene em FSM, upgrade intermission, boss setpiece e evidencia BlastEm.

## Contrato de Runtime de Producao

- `scene_manager_contract`: obrigatorio antes do primeiro build.
- `input_abstraction_contract`: 3/6 botoes, buffer, pause e remap basico.
- `track_data_format_contract`: formato de dados de pista antes de `SECTOR_01`.
- `collision_system_contract`: hitboxes, layers, resposta e fixtures.
- `hud_layout_contract`: coordenadas exatas do HUD em 320x224.
- `sprite_animation_contract`: estados, frame timing e tile budget de sprites.
- `progression_tuning_tables`: numeros de velocidade, pressao, upgrades e spawns.
- `boss_attack_pattern_contract`: fases, ataques, weakpoints e dano do boss.
- `game_flow_contract`: pause, game over e continue.
- `build_system_contract`: entrada canonica de build via wrapper central.
- `creative_cohesion_pass`: direcao de coesao, descoberta e memorabilidade.
- `pursuer_presence_contract`: presenca visual/sonora do perseguidor por Pressure.
- `lumen_pressure_economy_contract`: Lumen como risco sistemico.
- `sector_mechanic_identity_contract`: regra unica por setor.
- `signature_setpiece_contract`: momento assinatura Setor 3 -> 4.
- `reactive_music_gameplay_contract`: musica reativa a Pressure/Lumen/boss.
- `replayability_score_contract`: estrelas, score e unlockables.
- `persistence_scope`: `required` para upgrades/highscore a partir do slice 2.
- `region_timing_contract`: NTSC 60 FPS alvo; PAL ajusta timers por `SYS_isPAL()`.
- `asset_optimization_report`: obrigatorio antes de promover arte.
- `rom_mastering_report`: obrigatorio antes de qualquer entrega.
- `code_review_report`: obrigatorio antes de closeout.
- `local_ci_gate_report`: obrigatorio enquanto nao houver CI remoto.

## State FSM Map

| Scene | Enter | Update | Exit | Recursos Criticos |
|---|---|---|---|---|
| `BRANDING` | logos e paleta | hold/pular | clear/fade | BG_A/B, audio stinger |
| `TITLE` | title art, menu | input/menu pulse | teardown WINDOW | WINDOW, cursor sprite |
| `OPENING_CUTSCENE` | paineis por estado | FSM/typewriter | reset texto/paleta | BG_A/B, WINDOW, sprites retrato |
| `RACE` | preload setor | regras, road, HUD | congelar/resultado | BG_A/B, HScroll, sprites, audio |
| `UPGRADE` | cards e opcoes | selecao | aplicar upgrade | WINDOW, BG_A |
| `BOSS_APPROACH` | estrada especial | pressao/setpiece | handoff boss | line scroll, sprites boss |
| `FINAL_BOSS` | arena boss | fases/weak points | resultado | boss sprites/planes, HUD |
| `RESULT` | card final | reiniciar/menu | clear state | WINDOW, save |
| `CREDITS` | cards paginados | trocar pagina/voltar title | clear WINDOW/BG_A | BG_A/WINDOW, glyph subset |
| `PAUSE` | overlay/estado congelado | menu curto | resume/retry/title | WINDOW, audio duck |
| `GAME_OVER` | failure card | escolha continue/title | clear pools | WINDOW, save opcional |
| `CONTINUE` | countdown/card | confirmar/timeout | reload checkpoint | scene manager, input |

## Memory Pool Map

- hazards ativos: 6 slots no primeiro slice, ate 10 no produto.
- pickups: 4 slots.
- particles/poeira: 12 slots com lifetime curto.
- boss parts: 0 no primeiro slice; planejar 5 a 7 partes quando modular claim virar required.
- cutscene panels: carregamento por estado, nao tudo residente.
- text glyph cache: subset real por cena.
- front-end glyph cache: title/menu/credits separado de HUD para evitar vazamento de atlas.
- track events live: ate 10 no primeiro slice, ate 14 no produto.

## VBlank DMA Ownership

Owner unico por frame:

- `scene_manager`: durante transicao/loading.
- `opening_cutscene`: paineis/texto quando gameplay pausado.
- `race_road`: HScroll table e pequenos CRAM updates durante corrida.
- `race_hud`: updates de WINDOW apenas quando valor muda.
- `boss_setpiece`: boss effects, com recuo se competir com HUD/sprites.

## H-Int Ownership

Primeiro slice evita H-Int. Se uma cena exigir:

- owner unico declarado no `raster_fx_ownership_map`;
- callback instalado no enter;
- callback removido no exit;
- fallback sem H-Int.

## Tecnicas Selecionadas

| Registry ID | Aplicacao | Funcao | Owner | Fallback |
|---|---|---|---|---|
| `dma_transfer_safety` | global | impedir DMA inseguro | scene_manager/render | preload maior |
| `line_scrolling` | corrida | velocidade e pista viva | race_road | scroll por plano |
| `pseudo3d_road_stack` | corrida/boss | faixas e profundidade | race_road/level | estrada flat com perspectiva |
| `camera_scroll_management` | corrida | pressao, impacto, lookahead | race_road | offsets zerados |
| `hitstop_camera_shake_feedback` | dano/Pulse/boss | confirmar consequencia | race_rules | palette flash |
| `window_plane_static_hud` | UI | HUD fixo legivel | race_hud | HUD compacto em BG_A |
| `palette_state_transitions` | fase/cutscene | ritmo e estado | scene owner | paleta fixa |
| `prerendered_sprite_scaling` | boss | aproximacao por estagios | boss_setpiece | fewer boss stages |
| `xgm2_audio_architecture` | audio | musica/SFX/stingers | system_audio | PSG/SFX reduzido |
| `save_sram_checksum_redundancy` | persistencia | upgrades e recordes | save_data | persistence_scope=none no slice 1 |

Tecnicas adiadas:

- `forward_kinematics`: adiada ate o boss modular ter contrato e runtime.
- `ghost_afterimage_sprites`: adiada por ser `LABORATORIO`.
- `palette_cycling`: adiada como tecnica ativa de entrega por status `LABORATORIO`; usar `palette_state_transitions` segura primeiro.

## Regras Numericas Iniciais

- Gameplay alvo: 60 FPS NTSC.
- Max scanline sprites: 18 alvo, 20 limite fisico.
- Total sprites VDP: <= 72 alvo, 80 limite.
- BG resident target na corrida: <= 700 tiles antes de mapas/sprites, ajustado por `SPR_initEx`.
- DMA per frame: abaixo do envelope seguro medido pelo wrapper; sem uploads pesados em controle ativo.
- Cutscene pode fazer preload por estado com controle bloqueado.

## Contratos Executaveis de Producao

| Dominio | Arquivo | Decisao |
|---|---|---|
| Track data | `doc/track_data_format_contract.json` | pista por eventos em faixas |
| Sector 01 | `doc/sector_01_track_plan.json` | 96 steps, 17 eventos iniciais |
| Colisao | `doc/collision_system_contract.json` | AABB por layer, tile visual nao e colisao |
| Entidades | `doc/entity_archetype_manifest.json` | pools estaticos e archetypes |
| HUD | `doc/hud_layout_contract.json` | WINDOW 320x24, coordenadas fixas |
| Animacao | `doc/sprite_animation_contract.json` | Lio 24x32, run 6 frames |
| Tuning | `doc/progression_tuning_tables.json` | velocidades/pressao/custos |
| Assets | `doc/asset_production_spec.json` | tile targets e paletas por asset |
| Boss | `doc/boss_attack_pattern_contract.json` | fases/padroes/weakpoints |
| Flow | `doc/game_flow_contract.json` | pause/game over/continue |
| Build | `doc/build_system_contract.json` | wrapper central, sem Makefile local canonico |
| Creative cohesion | `doc/creative_cohesion_pass.md` | tese de perseguicao e memorabilidade |
| Pursuer presence | `doc/pursuer_presence_contract.json` | silhueta/cues por Pressure |
| Lumen economy | `doc/lumen_pressure_economy_contract.json` | moeda que aumenta risco |
| Sector identity | `doc/sector_mechanic_identity_contract.json` | regra unica por setor |
| Signature setpiece | `doc/signature_setpiece_contract.json` | `shattered_lane_gauntlet` |
| Reactive music | `doc/reactive_music_gameplay_contract.json` | audio como feedback |
| Replay | `doc/replayability_score_contract.json` | estrelas e unlocks |

## Save Scope

Slice 1: `optional`, sem dependencia de progresso.

Produto: `required` para:

- upgrades desbloqueados;
- melhor tempo/score;
- flags de setores.

Contrato SRAM fica em `doc/save_system_contract.json`.

## API Reality Check Futuro

Antes de codigo:

- verificar headers SGDK 2.11 em `sdk/sgdk-2.11/inc/`;
- confirmar APIs de paleta como `PAL_setPalette(..., DMA)` e `PAL_getColors(index, dest, count)`;
- usar `SPR_addSprite`, nao APIs antigas;
- nunca chamar texto inseguro sem truncamento.

## Risk Mitigation

- Se line scroll custar demais: usar scroll por plano e reforcar animacao de sprites.
- Se boss gigante estourar scanline: reduzir partes, usar plane takeover ou aproximacao por paineis.
- Se HUD competir com texto/cutscene: WINDOW muda de owner por cena e reseta no exit.
- Se arte premium nao existir: runtime fica smoke test `lab_not_delivery=false` mas `creative_ready=false`; nao usar fallback procedural como final.
