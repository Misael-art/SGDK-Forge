# Genre Specialization Matrix

Estado canonico de subgeneros do framework de especializacoes. v2 cobre **8 familias** e **38 subgeneros**:
- **20 `active`** (MD-viaveis, opt-in por projeto, design contract ativo, validator ativo)
- **8 `future_knowledge`** (MD-viaveis, em pesquisa, sem design contract, sem validator)
- **10 `future_architetural`** (MD-NAO-viaveis, listados para proficiencia taxonomica, sem skill/schema/validator)

Toda subgenero vira **1 especializacao propria** (nao bundleado em genero pai). Wave 1 entrega os 5 mais diversos; Waves 2-4 cobrem o resto.

## Ativacao

| Estado | Significado | Promovido por |
|---|---|---|
| `active` | Especializacao opt-in disponivel. Projeto pode declarar manifesto. | N/A (ja vira active) |
| `deferred` future_knowledge | MD-viavel mas em pesquisa. Nenhum design contract ativo. Nenhum validator dispara. | Humano + curadoria + projeto piloto + ROM + BlastEm |
| `deferred` future_architetural | MD-NAO-viavel. Listado para proficiencia taxonomica. Nenhum skill/schema/validator. | N/A (limitacao de hardware) |

## Familias (8)

| Familia | Definicao | Subgeneros no v2 |
|---|---|---|
| `fighting` | Luta 1v1 em plano 2D com frame data, neutral, okizeme, round-based | 6 (1 active + 2 fk + 3 fa) |
| `rpg` | Party, progressao por XP, resolucao de combate (turnos ou acao), inventario, narrativa | 4 (2 active + 2 fk) |
| `strategy` | Unidades, economia, vitoria por condicao (aniquilacao, captura, construcao), tatico ou RTS | 5 (2 active + 1 fk + 2 fa) |
| `horror` | Ameaca (inimigo ou ambiente), inventario escasso, recursos (municao/vida/sanity), resolucao de medo | 6 (5 active + 1 fk) |
| `brawler` | Wave combat, iframe, escape move, encounter design, progressao linear | 3 (3 active) |
| `fps` | First-person, armas com recarga, combate a distancia, level design labirintico | 4 (0 active + 1 fk + 3 fa) |
| `platformer_puzzle` | Traversal 2D, ability gates, fisica simples, logica espacial, puzzles | 5 (4 active + 1 fk) |
| `racing_sports_adventure` | Fisica de veiculo, controle de atleta, exploracao de mundo | 5 (3 active + 2 fa) |

`fk` = future_knowledge (MD-viavel, diferido). `fa` = future_architetural (MD-nao-viavel, diferido).

## Mega Drive feasibility legend

| Bucket | Significado | Skill/Schema/Validator |
|---|---|---|
| `active` | MD-viavel (64KB RAM, 7.67MHz 68K, 64KB VRAM). Cabe no budget. | SIM |
| `future_knowledge` | MD-viavel mas pendente de curadoria/projeto. | NAO (Wave 2+ pode promover) |
| `future_architetural` | NAO-viavel em MD (3D livre, IA complexa, persistencia macica, multi-thread). | NAO (limitacao de hardware) |

## Subgeneros `active` (20)

| `specialization_id` | Familia | Eixos congelados |
|---|---|---|
| `fighting_2d_traditional` | fighting | time_unit=frames; head_metric_policy=advisory; archetype_policy=design_tool_not_law; balance_evidence_required=true; rollback_netcode=not_applicable |
| `rpg_turn_based_jrpg` | rpg | time_unit=ticks (turn); party_size_max=4; equipment_grid=slot_based; encounter_trigger=fixed+random; permadeath=off; narrative_branching=linear_with_optional_scenes |
| `rpg_action_topdown` | rpg | time_unit=frames; camera=topdown_fixed; party_size_max=2; encounter_trigger=overworld_realtime; combat_resolution=action_realtime_with_pause; equipment_grid=slot_based |
| `strategy_tactical_turn_based` | strategy | time_unit=ticks; grid=square_or_hex; fog_of_war=on; unit_count_max=20; per_unit_ap_max=4; permadeath=on; victory_objective=objective_based |
| `strategy_tower_defense` | strategy | time_unit=frames; grid=fixed_path; lane_count=1_to_3; tower_slots_max=24; wave_spawner=scripted; resource_currency=energy_or_gold; victory=survive_N_waves |
| `horror_survival_inventory` | horror | time_unit=frames; camera=2d_third_person; inventory_slots_max=8; ammo_scarcity=on; save_stations=typewriter; enemy_count_active=1_to_3; sanity_meter=on |
| `horror_stealth_avoid` | horror | time_unit=frames; camera=fixed_angles; enemy_patrol_visibility=cone; distraction_items=yes; one_shot_kill=enemy; no_combat_loop=true |
| `horror_action_horde` | horror | time_unit=frames; camera=over_shoulder; enemy_count_active=10_to_40; melee_priority=primary; ranged_ammo=scarce; arenas=closed_rooms_with_chokepoints |
| `horror_mascot_static` | horror | time_unit=frames; camera=fixed_first_person_or_static; enemy_count_active=1; movement_speed=enemy_faster_than_player; objective=survive_or_collect; tone=creepy_pastoral |
| `horror_retro_short_form` | horror | time_unit=frames; camera=fixed_or_topdown; run_length_max=10_min; enemy_count_active=1_to_2; save_model=password_or_replay; tone=pixel_art_lowpoly |
| `brawler_belt_scroll` | brawler | time_unit=frames; camera=horizontal_lanes; player_count=1_to_2; enemy_count_on_screen_max=8; pickup_drop=health_and_score; stage_progression=linear_with_bosses; iframe_on_hit=on |
| `brawler_run_and_gun_2d` | brawler | time_unit=frames; camera=horizontal_sidescroll; player_count=1_to_2; weapon_pickup=drop_and_swap; ammo_count_max=99; enemy_spawn=continuous_waves; cover_mechanic=on |
| `brawler_run_and_gun_topdown` | brawler | time_unit=frames; camera=topdown; player_count=1_to_2; aim_direction=8_way; ammo_count_max=99; enemy_spawn=room_based; destructible_cover=on |
| `platformer_precision_2d` | platformer_puzzle | time_unit=frames; camera=side_scroll_with_lookahead; run_speed_horizontal=2x_player; jump_count=1_to_2; coyote_time=on; death_loop=on; level_length=short_tight |
| `metroidvania_ability_gated` | platformer_puzzle | time_unit=frames; camera=side_scroll_with_room_transitions; ability_count=4_to_8; map_size=large_interconnected; backtracking=on; save_stations=mandatory |
| `puzzle_sokoban_grid` | platformer_puzzle | time_unit=moves; grid_size_max=12x12; box_count_max=8; undo_count=10; move_counter=on; level_set=handcrafted_or_200+ |
| `puzzle_tile_matching` | platformer_puzzle | time_unit=frames; grid_size=8x8; tile_colors=4_to_6; match_count_min=3; cascade=on; time_pressure=optional; special_tile_rainbow=optional |
| `racing_arcade` | racing_sports_adventure | time_unit=frames; camera=behind_or_chase; track_count_max=16; lap_count_max=5; ai_opponents=5_to_7; boost_on_drift=on; collision_model=arcade_forgiving |
| `sports_action_direct` | racing_sports_adventure | time_unit=frames; camera=side_or_isometric; player_count=2; match_length_max=4_min; input_mapping=analog_or_2_button; ai_difficulty=scripted_or_adaptive; ruleset=arcade_stylized |
| `adventure_action_2d` | racing_sports_adventure | time_unit=frames; camera=side_or_topdown; world_map=hub_or_connected; puzzle_density=moderate; combat_density=light_to_moderate; inventory_size=10_to_15 |

## Subgeneros `future_knowledge` (8)

Subgeneros MD-viaveis, diferidos ate curadoria humana + projeto piloto + ROM validado em BlastEm. Promocao para `active` segue as regras da secao "Promocao de fase" abaixo.

| `specialization_id` | Familia | Porque diferido |
|---|---|---|
| `fighting_2d_air_dasher` | fighting | Requer air dash + 8-way mobility + assist rotation + crossup mixup; complexo para MD; sem biblia canonica revisada. |
| `fighting_2d_tag_team` | fighting | Requer 2 personagens simultaneos + assist cooldown + DHC; budget apertado para MD; sem biblia canonica revisada. |
| `rpg_c_rpg_classic` | rpg | Requer party maior + liberdade exploratoria + IA de companheiro + classes avancadas; orcamento de dialogo grande; sem biblia canonica. |
| `rpg_narrative_dialogue` | rpg | Requer sistema de dialogo ramificado denso + estatisticas de relacionamento + flags de historia; sem biblia canonica revisada. |
| `strategy_rts_compact` | strategy | Requer economia continua + multi-unidade simultanea + producao em tempo real; alto custo de CPU 68K; sem biblia canonica. |
| `horror_psychological_suggestion` | horror | Requer audio espacial + eventos scriptados contextuais + ameaca implicita; sem biblia canonica revisada. |
| `fps_boomer_raycast` | fps | Requer raycasting 2.5D + texture mapping em tempo real; CPU 68K borderline; sem biblia canonica revisada. |
| `puzzle_physics_2d` | platformer_puzzle | Requer sim. de rigid body 2D em tempo real; CPU 68K borderline; sem biblia canonica revisada. |

## Subgeneros `future_architetural` (10)

Subgeneros MD-NAO-viaveis (limitacao de hardware: 64KB RAM, 7.67MHz 68K, 64KB VRAM, sem FPU, sem multi-threading, sem 3D livre). Listados **apenas** para fins de proficiencia taxonomica do agente. NAO terao skill/schema/validator/CI.

| `specialization_id` | Familia | Porque nao-viavel em MD |
|---|---|---|
| `fighting_platform` | fighting | Movimento 3D em arena + camera dinamica; exige matriz 3D livre; sem hardware 3D no MD. |
| `fighting_3d` | fighting | Mesh 3D + shading per-vertex + hitbox 3D; sem FPU e sem 3D pipeline. |
| `fighting_arena` | fighting | Ringout em arena 3D + blast zone + knockback %; exige fisica 3D + camera 3D livre. |
| `strategy_grand_strategy` | strategy | Mapa-mundi com 200+ nacoes + IA diplomatica + persistencia macica; excede 64KB RAM. |
| `strategy_4x_turn_based` | strategy | Mapa expandido + exploracao + pesquisa + diplomacia; excede 64KB RAM e exige pathfinding pesado. |
| `fps_tactical_simulation` | fps | IA inimiga cooperativa + command squad + line-of-sight avancado; excede 68K em 7.67MHz. |
| `fps_immersive_sandbox` | fps | Multi-thread IA + multiple objetos dinamicos + gravidade parcial; exige multi-threading. |
| `fps_puzzle_gravitational` | fps | Manipulacao de campo gravitacional em tempo real + multiplos corpos; exige FPU. |
| `racing_sim_hardcore` | racing_sports_adventure | Modelo de pneu avancado + fisica de suspensao + 60Hz telemtria; exige FPU. |
| `sports_manager_data` | racing_sports_adventure | Database de atletas + sim. temporada completa + IA de negocios; excede 64KB RAM. |

## Promocao de fase (todos os active)

Toda subgenero `active` segue a mesma trilha de promocao que `fighting_2d_traditional` v1:

| De | Para | Exige |
|---|---|---|
| LABORATORIO | TEORICA_STANDARD | Curadoria humana assinada em `SOURCES_INDEX.md` + este matrix revisado |
| TEORICA_STANDARD | TEORICA_PRIORITARIA | 1 projeto com ROM validado em BlastEm + `doc/10-memory-bank.md` + validator `ok` em closeout |
| TEORICA_PRIORITARIA | MESTRE_STANDARD | 1 projeto adicional (total 2) + 2+ design contracts distintos + validator `ok` em ambos |
| MESTRE_STANDARD | MESTRE_PRIORITARIA | Curadoria humana explicita + matriz firmada em changelog do wrapper |

Sem auto-promocao. Toda alteracao de fase exige:
- update deste matrix
- update de `doc/07_game_design/genre_specialization_registry.json`
- update de `doc/changelog/changelog.md` no wrapper
- update de `doc/10-memory-bank.md` no projeto (se aplicavel)

## Blockers phase-aware (por familia, so disparam em `ready_for_aaa`/`closeout`)

`vertical_slice` NAO bloqueia por estes. Disparam apenas quando o projeto declara fase avancada.

| Familia | Blocker | Funcao |
|---|---|---|
| fighting | `fighting_training_mode_missing_for_product` | `kind=training` deve existir no design contract antes de `ready_for_aaa` |
| fighting | `fighting_lore_moveset_unbound` | Todo personagem do roster precisa ter `moveset_frame_data_path` valido |
| fighting | `fighting_balance_evidence_missing` | `balance.evidence_paths` deve apontar para arquivos reais antes de closeout |
| rpg | `rpg_party_size_unbounded` | Party size deve respeitar `frozen_design_axes.party_size_max` |
| rpg | `rpg_encounter_resolution_ambiguous` | Encounter trigger e resolution devem ser declarados explicitamente |
| rpg | `rpg_save_corruption_risk` | Save com checksum e versao; sem raw pointer |
| strategy | `strategy_grid_vram_overflow` | Grid tilemap nao pode exceder VRAM disponivel |
| strategy | `strategy_unit_ap_unbounded` | AP por unidade deve respeitar `frozen_design_axes.per_unit_ap_max` |
| strategy | `strategy_fog_of_war_race` | Fog update deve ser deterministico dentro do VBlank |
| horror | `horror_enemy_count_unbounded` | Enemy count deve respeitar budget de sprites e scanline |
| horror | `horror_save_station_audit` | Save stations devem ser typewritter com checksum antes de closeout |
| horror | `horror_scare_loop_ungrounded` | Jump scares devem referenciar trigger explicito no design contract |
| brawler | `brawler_iframe_window_unsafe` | Iframe window deve ter duracao > 8 frames |
| brawler | `brawler_pickup_drop_unbounded` | Pickup drop rate deve respeitar budget de VBlank |
| brawler | `brawler_wave_spawner_deterministic` | Wave spawner deve ser deterministico (scripted) para QA |
| platformer_puzzle | `platformer_coyote_time_overflow` | Coyote time deve ser <= 6 frames |
| platformer_puzzle | `metroidvania_ability_unlock_path` | Backtracking path deve conectar todos os hubs |
| platformer_puzzle | `puzzle_undo_count_unbounded` | Undo stack deve respeitar limite e ser checado por salvamento |
| racing_sports_adventure | `racing_collision_model_audit` | Collision model deve ser arcade (forgiving) ou sim (justa) |
| racing_sports_adventure | `adventure_inventory_overflow` | Inventory size deve respeitar `frozen_design_axes.inventory_size` |
| racing_sports_adventure | `adventure_save_overflow` | Save deve caber em SRAM 32KB canonica |

Waves 1-4 podem adicionar novos blockers por subgenero conforme a pratica revelar gaps.

## Promocao de `future_knowledge` para `active`

A promocao de qualquer um dos 8 `future_knowledge` para `active` exige:
1. Curadoria humana de biblia canonica (nao-IA) copiada para `curation_sources/<sha256>_<descriptive>.txt`.
2. Projeto piloto opt-in com manifesto declarando o subgenero, com ROM rodando em BlastEm.
3. Validacao de hardware (VDP budget, scanline pressure, sprite limit) dentro do `megadrive-vdp-budget-analyst`.
4. Schema novo em `tools/sgdk_wrapper/schemas/<subgen>_design_contract.schema.json`.
5. Validator novo em `tools/sgdk_wrapper/validate_<subgen>_specialization.ps1`.
6. Skill nova em `tools/sgdk_wrapper/.agent/skills/planning/<subgen>-game-design/`.
7. Aprovacao humana explicita registrada em changelog do wrapper.

Ate la: o orquestrador NAO emite design contract para subgeneros `future_knowledge`. Se um projeto tentar declarar `fighting_2d_air_dasher` no manifesto, o validator recusa com `manifest_status=invalid` e reason `specialization_not_active`.

## Promocao de `future_architetural`

NAO promove. Sao declarados para proficiencia taxonomica. Se um projeto realmente quiser atacar um desses em MD, deve primeiro:
1. Promover para `experimental` em projeto isolado (nao canônico), com `deferred` no registry.
2. Documentar explicitamente quais eixos estao sendo **sacrificados** (ex.: 3D -> pre-rendered 2D, IA complexa -> scriptada).
3. Obter aprovacao humana para entrar como `active` com eixos congelados adaptados.

Caso contrario: a entrada fica apenas no registry para o agente conhecer a taxonomia e recusar opt-in com `mega_drive_feasible=false` no design contract.
