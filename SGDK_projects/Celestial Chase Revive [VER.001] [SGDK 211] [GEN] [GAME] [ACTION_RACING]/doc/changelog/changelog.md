# Changelog - Celestial Chase Revive

## 2026-06-28 - Visual slice v001 para front-end e Sector 01

- Criado `tools/build_visual_slice_v001.py` para gerar uma fatia visual autoral fora de `res/`, sem alterar runtime ou ROM.
- Gerados `data/source_art/revive/visual_slice_v001/title_frontend_source_v001.png` e `data/source_art/revive/visual_slice_v001/sector01_playfield_source_v001.png`.
- Gerado painel de revisao `data/processed/visual_slice_v001/visual_slice_contact_sheet_v001.png`.
- Criados `doc/visual_slice_v001_manifest.json` e `doc/locked_visual_direction_v001.json`.
- Atualizados `doc/source_validity_report.json` e `doc/authoriality_gate_report.json` para source direction apenas; promocao para `res/` continua bloqueada.
- Atualizados `out/logs/scene_tilemap_conversion_report.json`, `out/logs/per_tile_palette_conflict_report.json`, `out/logs/tilemap_flag_report.json` e `out/logs/visual_delivery_gate_report.json`.
- Os PNGs gerados estao em modo `P`, `bitDepth=4`, `colorType=3`, `PLTE=16`, dimensoes multiplas de 8 e cores visiveis no grid 9-bit.
- `validate_resources.ps1` reduziu os blockers para `visual_gate_blocked` e `code_loaded_tiles_unmeasured`; sairam `procedural_fallback_as_final`, `visual_direction_failed` e `scene_tilemap_conversion_report_stale`.
- Nenhuma ROM nova foi buildada ou recapturada; ROM vigente permanece `build_v020`, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.

## 2026-06-27 - Projecao canonica de cutscene_contract no wrapper

- Corrigido `tools/sgdk_wrapper/scene_contract_compiler.ps1` para descobrir contratos de cutscene em `doc/contracts/*_contract.json` e projetar `cutscene_contract` em `doc/scene-contracts.json` por `scene_id`.
- Ampliado `tools/sgdk_wrapper/ci/test_scene_contract_compiler.ps1` com regressao que prova que um contrato de cutscene projetado remove `SC100` no lint de producao.
- Validado wrapper: `test_scene_contract_compiler.ps1` passou 8/8 e `test_cutscene_contract_lint.ps1` passou 7/7.
- Regenerado `doc/scene-contracts.json`: `opening_catalyst_cutscene` e `race_start_handoff` agora possuem `cutscene_contract` no artefato canonico.
- `lint_scene_contract.ps1 -Mode production` ficou com 0 erros e 7 warnings; `SC100` nao aparece mais. Os warnings restantes sao de cenas futuras/unsupported e regressao obrigatoria.
- `validate_resources.ps1` foi reexecutado com timeout maior; o report canonico esta atualizado em 1 erro/5 warnings, com blockers reais de arte/budget: `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`, `code_loaded_tiles_unmeasured`, `scene_tilemap_conversion_report_stale`.
- `freshness_audit.ps1` ficou `status=ok`, `stale=0`, `missing_required=0`.
- Nenhuma ROM nova foi buildada ou recapturada; ROM vigente permanece `build_v020`, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.

## 2026-06-27 - Contratos cinematograficos de abertura e handoff

- Criado `doc/contracts/opening_cinematic_storyboard_contract.json` para modelar a abertura como FSM cinematica table-driven com sete estados, ownership de WINDOW/CRAM/scroll/audio, budget planejado por estado, plano de texto, gate visual e evidencia BlastEm futura.
- Atualizado `doc/contracts/opening_cutscene_contract.json` com ponteiros para FSM, resource plan, panel layout, palette script, text timing, audio cue map, teardown, evidence plan, glyph manifest e storyboard cinematico.
- Criado pacote de contratos para `race_start_handoff`: `race_start_handoff_contract.json`, FSM, resource plan, panel layout, text timing, palette script, teardown, evidence plan e storyboard cinematico.
- Atualizado `doc/13-spec-cenas.md` para apontar explicitamente os contratos de cutscene da Cena 2 e da Cena 3.
- Rodado `art_diagnostic.py`: cenario `2_res_exists_check`; 11 assets em `res/`, 11 tecnicamente carregaveis, mas com avisos de paleta/transparencia e sprites/metasprites que ainda bloqueiam promocao visual final.
- `scene_contract_compiler.ps1 -Mode production` continua emitindo `SC100` para `opening_catalyst_cutscene` e `race_start_handoff`, porque o wrapper ainda nao projeta `cutscene_contract` de `doc/contracts/` para `doc/scene-contracts.json`.
- Criado `out/logs/scene_contract_overlay_probe.json` apenas como prova tecnica: ao injetar os contratos no manifest compilado, `SC100`/`SC107` deixam de aparecer para abertura e handoff; o artefato canonico real nao foi mascarado.
- Registrada curadoria local em `doc/agent_learning/cutscene_contract_compiler_curation_candidate.md`, `failure_patterns.md` e `skill_promotion_candidates.md`; nenhuma promocao canonica foi aplicada.
- Validadores atualizados: `project_context=ok`, `project_methodology=passed`, `project_hygiene=passed`, `validate_resources=1 erro/5 warnings`; `ready_for_aaa=false`.
- Nenhuma ROM nova foi buildada ou recapturada; ROM vigente permanece `build_v020`, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.

## 2026-06-27 - Reavaliacao das premissas canonicas e alinhamento de status

- Reavaliadas as premissas do agente canonico contra `production_truth_protocol`: host, wrapper, ROM/runtime e qualidade criativa continuam sendo camadas independentes.
- `assert_agent_environment.ps1` encontrou falha consultiva no Graphify (`graphify_update_failed` por `uv trampoline failed to canonicalize script path`); Graphify nao foi usado como fonte de decisao nesta rodada.
- Contexto, metodologia e higiene do projeto foram validados novamente: `project_context=ok`, `project_methodology=passed`, `project_hygiene=passed`.
- `audit_project_learning.ps1 -Mode Audit` confirmou contexto de aprendizado presente, 16 licoes/candidatos e `canonical_promotion_performed=false`.
- A ROM vigente permanece `build_v020`, 131072 bytes, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`; nenhuma ROM nova foi buildada nesta rodada.
- O closeout tecnico do Sector 01 continua sustentado por rotas BlastEm seladas, mas isso nao promove arte final, audio final, mastering, Sector 02 ou `ready_for_aaa`.
- Regenerado `doc/scene-contracts.json` via `scene_contract_compiler.ps1 -Mode production`; o compilador reconheceu 14 cenas e manteve o contrato compilado sem mudanca estrutural.
- O lint de cenas revelou blockers de planejamento para as proximas etapas: `opening_catalyst_cutscene` e `race_start_handoff` ainda precisam de `cutscene_contract` em modo production/AAA; varias cenas futuras seguem com `boot_mode=unsupported` e sem regressao obrigatoria.
- `validate_resources.ps1` permanece bloqueado para promocao de produto: 1 erro, 7 warnings, blockers `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`, `code_loaded_tiles_unmeasured`, `scene_tilemap_conversion_report_stale`, `freshness_audit_stale` e `project_documentation_sync_stale`.
- Premissa corrigida para retomada: o projeto correto deve aceitar o Sector 01 como prova tecnica de jogabilidade, mas a proxima fatia de producao deve atacar o blocker dominante de direcao visual/contratos de cena, nao criar conteudo novo em cima de placeholders.

## 2026-06-19 - Closeout Tecnico do Sector 01 na build_v020

- Congelada a ROM `build_v020`, 131072 bytes, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.
- Confirmada a causa exata do crash: `spr_lumen_orb` possui `numFrame=3` na animacao 0 e recebia o frame invalido 3 por modulo hardcoded de 4.
- Corrigido somente o seletor confirmado em `race_scene.c`, derivando o frame count da `SpriteDefinition` e usando `SPR_setAnimAndFrame`.
- Corrigidos contratos de estrada, resultado e metricas: tile attributes completos, `pressure_sum` em `u32` e resultado distinto para sucesso/falha.
- Corrigido o HUD/WINDOW: fundo opaco, prioridade alta, limpeza por preenchimento e clipping de hazards/pickups antes da faixa do HUD.
- Restaurado o executor do Windows; `CreateProcessAsUserW failed: 5` nao voltou a ocorrer.
- Criado driver local de rota BlastEm com input dirigido a janela SDL, sem rebuild.
- Capturadas na mesma ROM: Title, abertura, inicio/meio da corrida, salto, Pulse, Beacon, resultado de sucesso, retorno ao Title e resultado de falha.
- Evidencias de sucesso: `out/evidence/blastem/routes/success/`.
- Evidencias de falha: `out/evidence/blastem/routes/failure/`.
- Evidencias Title/abertura: `out/evidence/blastem/scenes/title_opening/`.
- Selagem de evidencia: `status=ok`, `seal_status=sealed`, hash capturado igual ao hash vigente.
- Performance medida em duas rotas de 1800 amostras: zero overbudget, CPU max 53%, p95 34%, pico de 15 sprites e 9 por scanline.
- Budget: 17 tiles exatos residentes para a estrada, zero overlap de VRAM, 10.720 bytes de RAM estatica e zero conflito de sub-paleta.
- Regressao: Python 14/14; contratos PowerShell `PASS`.
- Reports de conversao, paleta, VRAM, sprites, memoria, runtime, freshness e scene closeout foram materializados.
- O wrapper central continua emitindo um warning conservador `code_loaded_tiles_unmeasured` porque inclui chamadas de nametable no detector; nenhuma mudanca foi feita no framework central.
- Status: first playable tecnico do Sector 01 fechado e testado em BlastEm; nao e claim de AAA, arte final, audio final, mastering ou release.
- Arte definitiva, audio, Upgrade Intermission e Sector 02 permanecem bloqueados ate aceitacao humana do closeout.

## 2026-06-18 - Auditoria de Recuperacao da V014

- Auditada a ROM `v014`, sha256 `167d4f6937099b542e84f0d64dc6ddf258ba32091c9e874988e01c45a760eafd`.
- Captura fresca de boot/title selada em `out/evidence/blastem_audit_v014/`.
- Captura observacional da corrida registrada em `out/evidence/blastem_audit_v014_route2/`.
- Confirmadas corrupcao visual no title/corrida e queda `ADDRESS ERROR` antes do fechamento.
- Criados `doc/code_review_report.json`, `doc/aaa_pipeline_gate_report.json` e `doc/agent_learning/v014_recovery_audit.md`.
- Rebaixado `doc/scene_closeout_report.json` para `review_blocked`.
- Normalizado `out/logs/emulator_session.json` para escopo honesto `boot_title_only`.
- Corrigida higiene local: `tools/` classificado e caminhos absolutos removidos de `doc/operational_loop_decision.json`.
- Status correto: buildado; boot/title testado com corrupcao; Sector 01 parcial observado com crash; first playable, budget, performance e AAA nao aprovados.

## 2026-06-19 - Recuperacao Sector 01: guarda de sprite nulo

- Corrigidos dois caminhos em `src/scenes/race_scene.c` que podiam chamar
  `SPR_setVisibility` com `Sprite* == NULL` apos falha de alocacao.
- Adicionada regressao estatica em `tools/tests/test_sector01_recovery.py`.
- Estado: `implementado`, ainda nao `buildado` nem `testado_em_emulador`.
- O PC `0x00F516` foi mapeado a `SPR_update+0x284`, no upload do tileset.
- A causa raiz final continua pendente de nova reproducao no BlastEm.

## 2026-06-17 - Runtime Seed Fase B OPENING para RACE para TITLE Validado

- Validada no BlastEm a rota `TITLE -> OPENING_CUTSCENE -> RACE -> TITLE`.
- Prova `OPENING_CUTSCENE -> RACE`: `scene_id=3`, screenshot `out/evidence/blastem/opening_to_race.png` sha256 `7cd4d82c1e9ac43edcf0f9f0c58ff5c34252c3d28d45804b6304e0db983a124d`, SRAM sha256 `87148cb563cb3dbf9141af7bcb542e352f7ccb09f2caa2418976f560d3102382`.
- Prova `RACE -> TITLE`: `scene_id=1`, screenshot canonico `out/evidence/blastem/screenshot.png` sha256 `90ba0fe3853efbafe9f4dca72d794f92322a29f3f1e4448fa44f31c8edfc05b4`, SRAM canonico sha256 `6720ab42dcdab34840e7b1a71f4545fae29570912c6e9f693f9cbbd4234434fa`.
- Input observado pela ROM: `observed_input=128` via transporte `wm_key_message_to_sdl_window`.
- Atualizado `doc/blastem_input_script.json` para a rota completa.
- Normalizados `out/logs/emulator_session.json` e `out/logs/blastem_evidence.json` para o contrato do wrapper, mantendo `out/logs/opening_race_title_route_report.json` como evidencia detalhada.
- ROM vigente: `out/rom.bin`, 131072 bytes, sha256 `e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64`.
- `freshness_audit`: `status=ok`, `stale=0`.
- `validate_resources`: errors=0, warnings=5.
- `rom_mastering_report`: `mastering_needs_fix`; faltam closeout, budget, reports de conversao/paleta, visual delivery e header de produto.
- Status correto: rota de cenas testada em emulador; `race_scene` ainda e placeholder, sem Sector 01 jogavel.

## 2026-06-17 - Runtime Seed Fase B TITLE para OPENING Validado

- Validada no BlastEm a transicao `TITLE -> OPENING_CUTSCENE`.
- Atualizada camada de input para inicializar/atualizar joystick explicitamente com `JOY_init()` e `JOY_update()`.
- Adicionado probe SRAM `INP` em `0x110` para registrar input bruto, input observado e lock.
- Diagnostico: transporte `SendInput` do wrapper chegou na janela SDL, mas nao foi observado pela ROM (`observed_input=0`); transporte `wm_key_message_to_sdl_window` foi observado como `BUTTON_START`.
- ROM vigente: `out/rom.bin`, 131072 bytes, sha256 `e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64`.
- Evidencia BlastEm: screenshot `out/evidence/blastem/screenshot.png`, sha256 `f6ff6c31590cbf861c330238da2c477b85766c0c8fbfb2a1b3007c0daae3b15e`; SRAM `out/evidence/blastem/save.sram`, sha256 `273e4aae2b37689ebb2ad4f7343c54a6859d91c089b194a603fd36d6a0c4ca8c`.
- Probe de cena: `scene_id=2` (`APP_SCENE_OPENING_CUTSCENE`), `observed_input=128`.
- `freshness_audit`: `status=ok`, `stale=0`.
- `validate_resources`: errors=0, warnings=5.
- `rom_mastering_report`: `mastering_needs_fix`, ainda bloqueado por closeout visual, budget e identidade de header.
- Proximo passo: provar `OPENING_CUTSCENE -> RACE -> TITLE`; depois iniciar Sector 01 jogavel.

## 2026-06-16 - Fundacao de Specs

- Criado projeto canonico `Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]`.
- Registrada decisao de nao usar o nome solicitado sem `[TIPO] [GENERO]`, pois o validador canonico reprova esse formato.
- Classificado contexto como `aaa_game` com teto `vertical_slice`.
- Criados manifests de metodologia, tecnica, memoria, GDD, roteiro, TDD, specs de cenas, QA, asset register e roadmap.
- Benchmark Celestial Chase foi analisado como referencia tecnica, mantendo seus blockers criativos e de laboratorio fora do Revive.
- Sincronizadas tecnicas planejadas: `dma_transfer_safety`, `line_scrolling`, `pseudo3d_road_stack`, `camera_scroll_management`, `hitstop_camera_shake_feedback`, `window_plane_static_hud`, `palette_state_transitions`, `prerendered_sprite_scaling`, `xgm2_audio_architecture` e `save_sram_checksum_redundancy`.
- Reforcado GDD com regras sistemicas, progressao da fase, mapa de secoes, ritmo, tutorial invisivel, tecnicas escolhidas e direcao sonora.
- Validados JSON, contexto, metodologia, higiene, GDD substancial e technique usage para fase de specs.
- Registrados blockers materiais restantes: sem `.res`, sem grafo de recursos, sem gate visual, sem reports de conversao/paleta, sem freshness audit e sem scene closeout.
- Status do Revive permanece `documentado`; nenhuma ROM foi buildada ou vista no emulador.

## 2026-06-16 - Auditoria de Front-End

- Verificados fonte, logo, menu e creditos.
- Criados `brand_identity_manifest.json`, `ui_pixel_surface_contract.json`, `front_end_menu_contract.json`, `credits_contract.json`, `text_presentation_profile.json` e `front_end_element_audit.json`.
- Atualizados GDD, roteiro, specs de cenas, TDD, arquitetura, QA, asset register, scene contracts e scene regression.
- Creditos passaram de ausentes para `documentado`; fonte/logo/menu passaram de parcial/alto nivel para contratos planejados.
- Status permanece `documentado`; assets, atlas `.res`, legibilidade nativa e capturas BlastEm ainda nao existem.

## 2026-06-16 - Fechamento de Lacunas Criticas

- Criados contratos de track data, `SECTOR_01`, colisao, entidades, HUD, animacao, tuning, asset production, boss, game flow e build.
- Adicionados `22-production-spec-gap-closure.md` e `critical_gap_audit.json` com a reflexao e auditoria das decisoes tecnicas.
- Criados mockups SVG locais para logo, HUD, Setor 1 e boss em `data/source_art/revive/concept/`.
- Criado `concept_art_pack_manifest.json` com hashes dos mockups.
- Atualizados GDD, LDD, TDD, arquitetura, specs de cenas, QA, runtime contract, scene contracts, scene regression, asset register, boss card e scene manager.
- Decisao de build registrada: wrapper central e `makefile.gen.elite` sao a fonte canonica; Makefile local custom continua proibido.
- Status permanece `documentado`; ainda nao ha `.res`, runtime seed, ROM, budget medido ou evidencia BlastEm.

## 2026-06-16 - Handoff de Curadoria Canonica

- Criado `canonical_planning_curation_handoff.json` para avaliacao do agente canonico.
- Criado `doc/agent_learning/planning_mode_curation_candidate.md`.
- Atualizados `skill_promotion_candidates.md`, `canonical_promotion_review.md` e `learning_ledger.json`.
- Registrados quatro candidatos: fechamento pre-runtime de specs, contrato minimo de front-end, contrato de build centralizado e manifesto de mockups locais.
- Nenhuma mudanca foi feita em `tools/sgdk_wrapper/.agent/`; promocao canonica continua pendente de revisao humana.
- Auditor de aprendizado confirmou `lessons=4`, `candidates=4` e `canonical_promotion_performed=false`.
## 2026-06-16T13:58:32.2871789-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 8de2fef56a1db9b6992e4ebce4e76022576052721984d3482d5f21dc91ac8bf7, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: report_older_than_rom

## 2026-06-16T13:58:58.3972483-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 8de2fef56a1db9b6992e4ebce4e76022576052721984d3482d5f21dc91ac8bf7, 131072 bytes)
- Validation: errors=0, warnings=6
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

## 2026-06-17T05:10:44.8195263-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_brand_engine_logo -> v001 (res/branding_image.png)
- ROM: build_v002 (sha256 c053f0a2d40ec297e3a532efa2d1c7b1a6207e67812b48e3411913f47e51f77d, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, changelog_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T05:11:19.6790793-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 c053f0a2d40ec297e3a532efa2d1c7b1a6207e67812b48e3411913f47e51f77d, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T05:18:02.4324832-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 954e140458fe31a25efb5a0b446048708cdcfd3188a99669fd9d8f1680389d85, 131072 bytes)
- Validation: errors=0, warnings=8
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T05:19:38.3014056-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 954e140458fe31a25efb5a0b446048708cdcfd3188a99669fd9d8f1680389d85, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T05:29:55.4478522-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 06b63c6be59b86947506cca94ff17dd7104eff366bc11b68b65187e5f2464796, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T05:30:18.1229794-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 06b63c6be59b86947506cca94ff17dd7104eff366bc11b68b65187e5f2464796, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17 - Runtime Seed Fase B Parcial Validado no BlastEm

- Implementado scene manager com cenas `branding`, `title`, `opening_cutscene`, `race` e `credits` em placeholder.
- Corrigida compatibilidade SGDK 2.11 em `Image.tilemap->w/h` e `TILE_USER_INDEX`.
- Atualizado loop principal para chamar `SPR_update()` antes de `SYS_doVBlankProcess()`.
- Corrigida legibilidade do font SGDK reservando a cor 15 da PAL0 como branco nas paletas de texto.
- Removido `sprintf` por frame do placeholder de corrida, usando `uintToStr` e redraw apenas quando o segundo muda.
- Adicionado probe SRAM de cena: assinatura `SCN` em `0x108` e `scene_id` em `0x10B`.
- ROM vigente: `out/rom.bin`, 131072 bytes, sha256 `06b63c6be59b86947506cca94ff17dd7104eff366bc11b68b65187e5f2464796`.
- BlastEm: `boot_emulador=ok`, `blastem_gate=true`, `testado_em_emulador=true`.
- Evidencia: `out/evidence/blastem/screenshot.png` sha256 `90ba0fe3853efbafe9f4dca72d794f92322a29f3f1e4448fa44f31c8edfc05b4`; `save.sram` sha256 `16d0af3cfdfbe48a6ba6a674db89a8a34e4be626b9b01ae2b18d38200859af54`.
- SRAM confirmou `READY`, counter `174`, e `SCN scene_id=1` (`APP_SCENE_TITLE`).
- Validacao final: errors=0, warnings=5; freshness `ok`, stale=0, missing_required=0.
- Mastering segue `mastering_needs_fix`: faltam gate visual, visual delivery, reports de tilemap/paleta, scene closeout, budget e header ROM de produto.
- Pendente: provar `TITLE -> OPENING_CUTSCENE` por input automatizado ou probe equivalente.

## 2026-06-17T05:50:39.6674384-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 06b63c6be59b86947506cca94ff17dd7104eff366bc11b68b65187e5f2464796, 131072 bytes)
- Validation: errors=0, warnings=5
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, scene_closeout_gate_missing
- Emulator evidence: ok

## 2026-06-17T05:52:01.8299213-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 06b63c6be59b86947506cca94ff17dd7104eff366bc11b68b65187e5f2464796, 131072 bytes)
- Validation: errors=0, warnings=6
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: ok

## 2026-06-17T06:05:31.1126982-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v005 (sha256 e1fd9f3b0d1e0c5658b75cdc2d3335190826a774866a9b38c1c0a9fff632ad99, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T06:06:11.3271503-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v005 (sha256 e1fd9f3b0d1e0c5658b75cdc2d3335190826a774866a9b38c1c0a9fff632ad99, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: evidence_outside_sandbox

## 2026-06-17T06:13:58.4377696-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v006 (sha256 e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64, 131072 bytes)
- Validation: errors=0, warnings=8
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T06:14:47.4455426-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v006 (sha256 e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T06:23:42.2989515-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v007 (sha256 c0352f5f42b3a04084a4f02d7327297ccfd6fd80405a7b94d1465ba4b1f32a7b, 131072 bytes)
- Validation: errors=0, warnings=8
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T06:24:05.7739163-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v007 (sha256 c0352f5f42b3a04084a4f02d7327297ccfd6fd80405a7b94d1465ba4b1f32a7b, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T12:20:23.8647428-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v008 (sha256 e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T12:21:08.7445805-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v008 (sha256 e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64, 131072 bytes)
- Validation: errors=0, warnings=6
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: ok

## 2026-06-17T13:41:33.2399428-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v009 (sha256 4a53859dc224fd28b7cde486e073b4ea1ad16576dc81ce28b19dbc639f662e73, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T13:42:05.9865478-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v009 (sha256 4a53859dc224fd28b7cde486e073b4ea1ad16576dc81ce28b19dbc639f662e73, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T13:49:15.5854654-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v010 (sha256 c4c5dc61044e78fec7a5e842033348b72995a339503f7ceb2fb1706b2e662d52, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T13:49:47.5135765-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v010 (sha256 c4c5dc61044e78fec7a5e842033348b72995a339503f7ceb2fb1706b2e662d52, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T13:54:13.1157471-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v011 (sha256 30016105da3087206a49c2d1bdffc19328a1a2f52471b23f4d19072b3d2b8f06, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T13:54:45.4625900-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v011 (sha256 30016105da3087206a49c2d1bdffc19328a1a2f52471b23f4d19072b3d2b8f06, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T13:57:23.3383270-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v012 (sha256 c050db5b14405dd7af56a86547b17420cf3acd72392f1acb6ce5da7cdd4475a2, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T13:57:54.9769310-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v012 (sha256 c050db5b14405dd7af56a86547b17420cf3acd72392f1acb6ce5da7cdd4475a2, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T23:43:21.8142677-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v013 (sha256 ae5a3b25b3b1a65894fa7396925f3f2750707ac6ffcf16aeb32f7c313a82295e, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: external_path_reference_outside_project, visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-17T23:43:49.3521144-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v013 (sha256 ae5a3b25b3b1a65894fa7396925f3f2750707ac6ffcf16aeb32f7c313a82295e, 131072 bytes)
- Validation: errors=0, warnings=8
- Blockers: external_path_reference_outside_project, visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-18T00:04:23.7498600-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_road_tiles -> v001 (res/tiles/road_tiles.png)
  - img_hud_elements -> v001 (res/tiles/hud_elements.png)
  - img_title_bg -> v001 (res/bg/title_bg.png)
  - img_title_logo -> v001 (res/bg/title_logo.png)
  - spr_lio_all -> v001 (res/sprites/lio_all.png)
  - spr_lumen_orb -> v001 (res/sprites/lumen_orb.png)
  - spr_low_stone -> v001 (res/sprites/low_stone.png)
  - spr_astral_mark -> v001 (res/sprites/astral_mark.png)
  - spr_beacon_key -> v001 (res/sprites/beacon_key.png)
  - spr_pursuer_shadow -> v001 (res/sprites/pursuer_shadow.png)
- ROM: build_v014 (sha256 167d4f6937099b542e84f0d64dc6ddf258ba32091c9e874988e01c45a760eafd, 131072 bytes)
- Validation: errors=0, warnings=12
- Blockers: orphan_project_root_entry, external_path_reference_outside_project, visual_gate_blocked, visual_delivery_gate_missing, changelog_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-18T00:04:52.0251484-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v014 (sha256 167d4f6937099b542e84f0d64dc6ddf258ba32091c9e874988e01c45a760eafd, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: orphan_project_root_entry, external_path_reference_outside_project, visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-18T05:30:02.1243541-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v015 (sha256 427f472a8d078f475752c538d39034c005eec50aebdde5bd56434930c17c87f9, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-18T05:31:07.1590825-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v015 (sha256 427f472a8d078f475752c538d39034c005eec50aebdde5bd56434930c17c87f9, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-18T05:35:26.6060894-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v015 (sha256 427f472a8d078f475752c538d39034c005eec50aebdde5bd56434930c17c87f9, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-18T05:36:11.0496694-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v015 (sha256 427f472a8d078f475752c538d39034c005eec50aebdde5bd56434930c17c87f9, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-19T11:13:28.4959098-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v016 (sha256 1ddb1a3155dd288e78dcf814776435512abf0ceb0ebd8e1a13d161597b8b2729, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-19T11:13:57.6102105-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v016 (sha256 1ddb1a3155dd288e78dcf814776435512abf0ceb0ebd8e1a13d161597b8b2729, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: session_not_captured

## 2026-06-19T11:24:58.4801404-03:00 - sprite_animationframe_recovery

- Escopo runtime restrito a helpers e chamadas de animacao/frame em `src/scenes/race_scene.c`.
- Causa confirmada: `spr_lumen_orb` gerado com `numFrame=3` recebia frame 3 por modulo hardcoded de 4.
- Correcao minima: frame count derivado de `SpriteDefinition` e instalacao atomica via `SPR_setAnimAndFrame`.
- Regressao especifica adicionada; suite Python: 8/8.
- Suite PowerShell: falha preexistente no contrato da tilemap da estrada; nao corrigida nesta rodada.
- ROM preservada apos build central: build_v016, sha256 `1ddb1a3155dd288e78dcf814776435512abf0ceb0ebd8e1a13d161597b8b2729`.
- BlastEm: Title observado na mesma ROM; SRAM com `READY` e `SCN=1`.
- Captura completa bloqueada por foreground do Windows no modulo canonico; abertura, corrida, Beacon, resultado e retorno ao Title permanecem sem evidencia v016.
- `res_graph`: estimado, 1004 tiles de usuario, reserva de sprites 420, overlaps 0.
- `audit_scene_budget`: `warn`, sem metricas de frame; status nao promove `validado_budget`.
- `scene_contract_compiler`: reconheceu 10 entradas de regressao, mas compilou zero cenas do formato atual da spec; blocker documental preservado.
- Validacao observacional final: errors=0, warnings=6; freshness=`ok`.
- Closeout permanece bloqueado. Arte definitiva, audio, Upgrade Intermission e Sector 02 nao liberados.

## 2026-06-19T14:12:50.3350967-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v017 (sha256 0dcbde94a7335efac814370b9b91932ab9860e8f44e6b8b26c4fab89604ce54e, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-19T14:13:14.4972634-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v017 (sha256 0dcbde94a7335efac814370b9b91932ab9860e8f44e6b8b26c4fab89604ce54e, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: session_not_captured

## 2026-06-19T14:42:08.6472995-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v018 (sha256 a85f46074fe53294b052318ba666733488c7884edf87f71fa4dbd2d8c14fc431, 131072 bytes)
- Validation: errors=0, warnings=8
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-19T14:42:41.8618646-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v018 (sha256 a85f46074fe53294b052318ba666733488c7884edf87f71fa4dbd2d8c14fc431, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale

## 2026-06-19T14:47:17.3254458-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v019 (sha256 2ab3f9f08e141b6eaf19a9762db8f1fcf57140a59c54713579f0a8d8dbfd26bc, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-19T14:47:57.5484801-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v019 (sha256 2ab3f9f08e141b6eaf19a9762db8f1fcf57140a59c54713579f0a8d8dbfd26bc, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale

## 2026-06-19T14:52:04.2941237-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e, 131072 bytes)
- Validation: errors=0, warnings=9
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-19T14:52:37.1564465-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale

## 2026-07-19T23:44:00-03:00 - p0_005_fresh_linux_evidence

- ROM `build_v020` nao foi rebuildada nem alterada.
- BlastEm Linux oficial executou a ROM e mostrou o front-end.
- Sessao `blastem-linux-20260720T023600Z-152199` selou ROM, screenshot, SRAM,
  VLAB e metricas com hashes completos e timestamps.
- Auditor pos-selagem passou; fixtures de tamper e ROM divergente bloquearam.
- Screenshot passou integridade semantica; nenhuma aprovacao criativa foi
  inferida.
- Performance permanece `unproven` e mastering permanece
  `mastering_needs_fix`.

## 2026-07-24T00:50:00-03:00 - damage_runtime_and_sprite_rejection

- Reprovado `lio_all.png` como `technical_pass_visual_fail`: 19 frames, 77
  blockers no auditor obrigatório.
- Corrigido `race_scene.c` para usar `ANIM_DAMAGE` real, com 3 frames, hold de
  6 frames, prioridade sobre salto/pulso e blink esparso.
- Regressao estatica passou e a ROM SGDK 2.11 compilou com SHA-256
  `a69050c105c6da29ff47dc098438e2da07b93a34cf03916949168b249adccd26`,
  131072 bytes.
- Sessao BlastEm `blastem-linux-20260724T034731Z-512798` capturou GIF e
  contact sheet do dano em runtime.
- O gate semantico reprovou a composicao da cena por baixa informacao; nenhuma
  aprovacao visual de Lio ou da cena foi emitida.
