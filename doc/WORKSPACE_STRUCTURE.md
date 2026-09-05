# Workspace Structure

Estado canonico de referencia para o workspace ativo `F:\Projects\Sgdk Forge`.

## Diretorios principais

| Caminho | Papel | Politica |
|---|---|---|
| `doc/` | Documentacao canonica do workspace | Novos indices e politicas entram aqui. Nao reescrever historico sem motivo. |
| `doc/07_game_design/` | Curadoria canonica de design de jogo por especializacao opt-in | Apenas material explicitamente opt-in por especializacao registrada. Curacao de fontes vive em `curation_sources/`. |
| `tools/sgdk_wrapper/` | Fonte unica da logica de build, validacao e framework `.agent` | Alterar somente com justificativa e validacao. |
| `sdk/sgdk-2.11/` | Toolchain SGDK | Nao mover, renomear ou arquivar automaticamente. |
| `tools/emuladores/` | Emuladores e suporte de execucao | Nao mover automaticamente; BlastEm continua gate canonico. |
| `SGDK_projects/` | Jogos, labs e prototipos SGDK | Conteudo pode ser trabalho ativo; nao mover sem revisao humana. |
| `SGDK_Engines/` | Engines, estudos e colecoes SGDK | Conteudo pode ser trabalho ativo; nao mover sem revisao humana. |
| `sgdk_templates/` | Templates locais existentes | Nome diverge de referencias antigas `SGDK_templates`; nao renomear sem rodada propria. |
| `assets/`, `data/`, `SGDK_projects/data/` | Assets fonte e packs brutos | Entram em review antes de qualquer arquivamento. |
| `out/` | Evidencias, reports e saidas geradas | Pode conter evidencia de QA; arquivar somente por plano com manifest. |
| `_archive/workspace_curation/` | Arquivo permanente de curadoria | Todo move deve ter manifest, checksum e rollback. |

## Registries estruturais

| Arquivo | Papel |
|---|---|
| `doc/template_registry.json` | Registro machine-readable dos templates conhecidos. Define `tools/sgdk_wrapper/modelo` como `CANONICAL_BOOTSTRAP`. |
| `doc/TEMPLATE_REGISTRY.md` | Politica humana para promocao, limpeza e revisao de templates. |
| `doc/ASSET_DATA_REGISTRY_POLICY.md` | Politica para separar raw/source/reference, generated, project-specific e third-party/rejected packs antes de qualquer merge fisico. |
| `doc/asset_data_registry.schema.json` | Contrato JSON para uma futura auditoria de assets/data. |
| `doc/OUTPUT_RETENTION_POLICY.md` | Politica de retencao para `out/` e outputs do wrapper. |
| `doc/ROOT_LOOSE_FILES_POLICY.md` | Politica para arquivos soltos na raiz. |
| `doc/05_technical/93_16bit_hardware_mastery_matrix.md` | Painel vivo humano da proficiencia do agente por tecnica. |
| `doc/05_technical/93_16bit_hardware_mastery_registry.json` | Registry machine-readable das tecnicas, tags humanas, status publico e evidencia de promocao. |
| `tools/sgdk_wrapper/schemas/technique_usage_manifest.schema.json` | Contrato do manifesto por projeto em `doc/technique_usage_manifest.json`. |
| `doc/07_game_design/genre_specialization_registry.json` | Registro machine-readable de especializacoes de genero. v2 = 38 subgeneros em 8 familias: 20 active, 8 future_knowledge, 10 future_architetural. Sem `MESTRE_*` (no auto-promotion). |
| `doc/07_game_design/genre_specialization_matrix.md` | Painel humano das fases de promocao, eixos congelados, blockers phase-aware e legendas de viabilidade MD. v2 = 8 familias. **STALE**: declara 20 active; o registry v3 e o CI declaram 6. |
| `doc/07_game_design/genre_coverage_state.json` | Estado REAL de cobertura de genero por projeto (nivel de evidencia A/B/C, sha256 de ROM, validator status, divergencias abertas). Arquivo de consulta unico para diagnosticos: atualizar, nao duplicar. Consultivo — nao promove status. |
| `doc/07_game_design/curation_sources/SOURCES_INDEX.md` | Indice canonico de fontes secundarias usadas pelas especializacoes. Cada fonte = SHA-256 + `verification_status` + `promotion_allowed`. v2 = 2 fighting + 7 placeholders para Wave 1+. |
| `tools/sgdk_wrapper/schemas/genre_specialization_registry.schema.json` | Contrato do registro de especializacoes. v2 = multi-familia + `families` + `mega_drive_feasibility_legend` + `owner_skill` livre. |
| `tools/sgdk_wrapper/schemas/genre_specialization_manifest.schema.json` | Contrato do opt-in por projeto em `doc/genre_specialization_manifest.json`. |
| `tools/sgdk_wrapper/schemas/fighting_2d_design_contract.schema.json` | Contrato do design de superficie da especializacao fighting. |
| `tools/sgdk_wrapper/schemas/fighting_moveset_frame_data.schema.json` | Contrato do frame data por personagem fighting. |
| `tools/sgdk_wrapper/schemas/fighting_specialization_report.schema.json` | Contrato do report do validator fighting. |
| `tools/sgdk_wrapper/validate_fighting_specialization.ps1` | Validator canonico top-level da especializacao fighting. |
| `tools/sgdk_wrapper/.agent/skills/planning/fighting-game-design/` | Skill orquestradora fina da especializacao fighting. v1 entregue. |
| `tools/sgdk_wrapper/.agent/skills/planning/rpg-game-design/` | Skill orquestradora fina da especializacao rpg. Wave 1 entregue (`rpg_turn_based_jrpg`); Wave 2+ cobre `rpg_action_topdown` e `rpg_c_rpg_classic`. |
| `tools/sgdk_wrapper/.agent/skills/planning/strategy-game-design/` | Skill orquestradora fina da especializacao strategy. Wave 1 entregue (`strategy_tower_defense`); Wave 2+ cobre `strategy_tactical_turn_based` e `strategy_rts_compact`. |
| `tools/sgdk_wrapper/.agent/skills/planning/horror-game-design/` | Skill orquestradora fina da especializacao horror. Wave 2+ (pendente). |
| `tools/sgdk_wrapper/.agent/skills/planning/brawler-game-design/` | Skill orquestradora fina da especializacao brawler. Wave 1 entregue (`brawler_belt_scroll`); Wave 2+ cobre `brawler_run_and_gun_2d` e `brawler_run_and_gun_topdown`. |
| `tools/sgdk_wrapper/.agent/skills/planning/fps-game-design/` | Skill orquestradora fina da especializacao fps. Wave 3+ (pendente; sem subgenero active v2). |
| `tools/sgdk_wrapper/.agent/skills/planning/platformer-puzzle-game-design/` | Skill orquestradora fina da especializacao platformer_puzzle. Wave 1 entregue (`platformer_precision_2d`); Wave 2+ cobre `metroidvania_ability_gated`, `puzzle_sokoban_grid`, `puzzle_tile_matching`. |
| `tools/sgdk_wrapper/.agent/skills/planning/racing-sports-adventure-game-design/` | Skill orquestradora fina da especializacao racing_sports_adventure. Wave 1 entregue (`racing_arcade`); Wave 4+ cobre `sports_action_direct` e `adventure_action_2d`. |
| `tools/sgdk_wrapper/ci/test_genre_specialization_registry.ps1` | CI v2: registro canonico tem 38 entries, 8 families, 20 active, 18 deferred (10 architetural, 6+ future_knowledge), 38 owner_skill unicos, design_contract_schema nao-vazio, >=2 blockers por active, sem MESTRE_*. 155 asserts. |
| `tools/sgdk_wrapper/ci/test_fighting_specialization_orchestrator.ps1` | CI: orquestrador fino nao vira catch-all. Cobre allow_implicit_invocation=false, mapa de delegacao, inferencia zero. |
| `tools/sgdk_wrapper/ci/test_fighting_specialization_contracts.ps1` | CI: 5 schemas parseaveis (Draft-07) + fixture completa passa no validator em vertical_slice + fixture com balance_evidence_missing dispara blocker em ready_for_aaa. |
| `tools/sgdk_wrapper/ci/test_fighting_master_promotion_guard.ps1` | CI: impossivel pular para MESTRE_* sem artifacts + curation_signature. Rogue registry sem manifest cai no caminho generalista. |
| `tools/sgdk_wrapper/ci/test_genre_specialization_generalista_unchanged.ps1` | CI: regression-guard - projeto sem `doc/genre_specialization_manifest.json` continua passando (validator retorna ok, manifest_status=absent, sem blockers). Roda em `run_golden_validate.ps1`. |
| `tools/sgdk_wrapper/ci/test_fighting_specialization_validator_smoke.ps1` | CI: smoke direto do validator em fixture sem manifest. Roda em `run_all_contract_gates.ps1`. |
| `tools/sgdk_wrapper/ci/test_rpg_specialization_orchestrator.ps1` | CI Wave 1: orquestrador fino rpg-game-design. Cobre allow_implicit_invocation=false, mapa de delegacao, inferencia zero, frozen axes (party_size_max=4, permadeath=off). 21 asserts. |
| `tools/sgdk_wrapper/ci/test_rpg_specialization_registry.ps1` | CI Wave 1: rpg_turn_based_jrpg ativo, owner_skill=rpg-game-design, design_contract_schema=rpg_turn_based_jrpg_design_contract.schema.json, 3 blockers rpg_*. 15 asserts. |
| `tools/sgdk_wrapper/ci/test_rpg_specialization_contracts.ps1` | CI Wave 1: 4 RPG schemas parseaveis (Draft-07) + fixture completa passa no validator em vertical_slice + fixture com party.size=10 dispara rpg_party_size_unbounded em ready_for_aaa. 23 asserts. |
| `tools/sgdk_wrapper/ci/test_rpg_master_promotion_guard.ps1` | CI Wave 1: impossivel pular para MESTRE_* sem artifacts + curation_signature. Rogue registry sem manifest cai no caminho generalista. framework_manifest referencia os 4 schemas + validator. 16 asserts. |
| `tools/sgdk_wrapper/ci/test_rpg_specialization_validator_smoke.ps1` | CI Wave 1: smoke direto do validator RPG em fixture sem manifest. 8 asserts. |
| `tools/sgdk_wrapper/ci/test_strategy_specialization_orchestrator.ps1` | CI Wave 1: orquestrador fino strategy-game-design. Cobre allow_implicit_invocation=false, frozen axes (grid=fixed_path, tower_slots_max=24, wave_spawner=scripted, victory=survive_N_waves). 21 asserts. |
| `tools/sgdk_wrapper/ci/test_strategy_specialization_registry.ps1` | CI Wave 1: strategy_tower_defense ativo, owner_skill=strategy-game-design, design_contract_schema=strategy_tower_defense_design_contract.schema.json, 3 blockers strategy_*. 15 asserts. |
| `tools/sgdk_wrapper/ci/test_strategy_specialization_contracts.ps1` | CI Wave 1: 4 strategy schemas parseaveis (Draft-07) + fixture completa passa no validator em vertical_slice + fixture com tower_slot_count=30 dispara strategy_grid_vram_overflow em ready_for_aaa. 25 asserts. |
| `tools/sgdk_wrapper/ci/test_strategy_master_promotion_guard.ps1` | CI Wave 1: impossivel pular para MESTRE_* sem artifacts + curation_signature. framework_manifest referencia os 4 strategy schemas + validator. 15 asserts. |
| `tools/sgdk_wrapper/ci/test_strategy_specialization_validator_smoke.ps1` | CI Wave 1: smoke direto do validator strategy em fixture sem manifest. 8 asserts. |
| `tools/sgdk_wrapper/ci/test_brawler_specialization_orchestrator.ps1` | CI Wave 1: orquestrador fino brawler-game-design. Cobre allow_implicit_invocation=false, frozen axes (camera=horizontal_lanes, enemy_count_on_screen_max=8, stage_progression=linear_with_bosses, iframe_on_hit=on). 22 asserts. |
| `tools/sgdk_wrapper/ci/test_brawler_specialization_registry.ps1` | CI Wave 1: brawler_belt_scroll ativo, owner_skill=brawler-game-design, design_contract_schema=brawler_belt_scroll_design_contract.schema.json, 3 blockers brawler_*. 15 asserts. |
| `tools/sgdk_wrapper/ci/test_brawler_specialization_contracts.ps1` | CI Wave 1: 4 brawler schemas parseaveis (Draft-07) + fixture completa passa no validator em vertical_slice + fixture com iframe_frames=4 dispara brawler_iframe_window_unsafe em ready_for_aaa. 24 asserts. |
| `tools/sgdk_wrapper/ci/test_brawler_master_promotion_guard.ps1` | CI Wave 1: impossivel pular para MESTRE_* sem artifacts + curation_signature. framework_manifest referencia os 4 brawler schemas + validator. 16 asserts. |
| `tools/sgdk_wrapper/ci/test_brawler_specialization_validator_smoke.ps1` | CI Wave 1: smoke direto do validator brawler em fixture sem manifest. 8 asserts. |
| `tools/sgdk_wrapper/ci/test_platformer_specialization_orchestrator.ps1` | CI Wave 1: orquestrador fino platformer-puzzle-game-design. Cobre allow_implicit_invocation=false, frozen axes (camera=side_scroll_with_lookahead, run_speed_horizontal=2x_player, coyote_time=on, death_loop=on, level_length=short_tight). 22 asserts. |
| `tools/sgdk_wrapper/ci/test_platformer_specialization_registry.ps1` | CI Wave 1: platformer_precision_2d ativo, owner_skill=platformer-puzzle-game-design, design_contract_schema=platformer_precision_2d_design_contract.schema.json, 3 blockers (platformer/metroidvania/puzzle). 15 asserts. |
| `tools/sgdk_wrapper/ci/test_platformer_specialization_contracts.ps1` | CI Wave 1: 4 platformer schemas parseaveis (Draft-07) + fixture completa passa no validator em vertical_slice + fixture com coyote_time_frames=12 dispara platformer_coyote_time_overflow em ready_for_aaa. 24 asserts. |
| `tools/sgdk_wrapper/ci/test_platformer_master_promotion_guard.ps1` | CI Wave 1: impossivel pular para MESTRE_* sem artifacts + curation_signature. framework_manifest referencia os 4 platformer schemas + validator. 16 asserts. |
| `tools/sgdk_wrapper/ci/test_platformer_specialization_validator_smoke.ps1` | CI Wave 1: smoke direto do validator platformer em fixture sem manifest. 8 asserts. |
| `tools/sgdk_wrapper/ci/test_racing_specialization_orchestrator.ps1` | CI Wave 1: orquestrador fino racing-sports-adventure-game-design. Cobre allow_implicit_invocation=false, frozen axes (track_count_max=16, lap_count_max=5, boost_on_drift=on, collision_model=arcade_forgiving). 24 asserts. |
| `tools/sgdk_wrapper/ci/test_racing_specialization_registry.ps1` | CI Wave 1: racing_arcade ativo, owner_skill=racing-sports-adventure-game-design, design_contract_schema=racing_arcade_design_contract.schema.json, 3 blockers (racing/adventure). 15 asserts. |
| `tools/sgdk_wrapper/ci/test_racing_specialization_contracts.ps1` | CI Wave 1: 4 racing schemas parseaveis (Draft-07) + fixture completa passa no validator em vertical_slice + fixture com collision_model=realistic_full dispara racing_collision_model_audit em ready_for_aaa. 24 asserts. |
| `tools/sgdk_wrapper/ci/test_racing_master_promotion_guard.ps1` | CI Wave 1: impossivel pular para MESTRE_* sem artifacts + curation_signature. framework_manifest referencia os 4 racing schemas + validator. 16 asserts. |
| `tools/sgdk_wrapper/ci/test_racing_specialization_validator_smoke.ps1` | CI Wave 1: smoke direto do validator racing em fixture sem manifest. 8 asserts. |

Template canonico atual: `tools/sgdk_wrapper/modelo`. `sgdk_templates/base-elite` permanece como referencia/fallback ate uma rodada propria de higiene e comparacao.

## Curadoria vigente

Rodada: `20260530_0655_deep_structure_audit`

Artefatos:
- `out/workspace_curation/20260530_0655_deep_structure_audit/`
- `_archive/workspace_curation/20260530_0655_deep_structure_audit/`

Status: `blocked_dirty_state_risk`.

Motivo: o worktree tinha 8188 entradas tracked modificadas e 7721 entradas tracked deletadas no inventario. Por seguranca, nenhum move automatico foi executado.

## Regra operacional

Antes de mover qualquer arquivo do workspace:

1. Gerar inventario.
2. Gerar `move_plan.json`.
3. Confirmar que o arquivo nao e tracked modificado/deletado.
4. Calcular SHA-256 antes do move.
5. Mover para `_archive/workspace_curation/<run>/...`.
6. Confirmar SHA-256 no destino.
7. Registrar em `archive_manifest.json`.
8. Manter `rollback_plan.ps1`.

Antes de promover qualquer projeto:

1. Confirmar que o material operacional esta dentro do projeto.
2. Confirmar `doc/technique_usage_manifest.json` quando houver tecnica catalogada.
3. Bloquear entrega se uma tecnica `LABORATORIO` aparecer fora de lab/techdemo.
4. Bloquear entrega se evidencia de tecnica apontar para fora do projeto, mesmo com autorizacao humana.
5. Exigir `doc/project_hygiene_manifest.json`; entrada externa usada deve possuir copia local e, para diretorios, inventario SHA-256 verificavel.
6. Exigir `sdk/sgdk-2.11/` do workspace ativo como toolchain de build/closeout.
