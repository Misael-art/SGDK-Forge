# Changelog Canonico - MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

## Estado Inicial

- projeto bootstrapado a partir do wrapper central
- documentacao minima materializada
- scene regression declarada em `doc/scene-regression.json`
- companion inicial esperado em `doc/scene-contracts.json`
## 2026-06-03T10:55:11.3513283-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_brand_fx_tiles -> v001 (res/branding/brand_fx_tiles.png)
  - img_brand_engine_logo -> v001 (res/branding/brand_engine_logo.png)
  - img_brand_author_logo -> v001 (res/branding/brand_author_logo.png)
  - img_brand_project_logo -> v001 (res/branding/brand_project_logo.png)
  - img_brand_presents_text -> v001 (res/branding/brand_presents_text.png)
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=10
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, changelog_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: report_older_than_rom

## 2026-06-03T10:55:35.2022830-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

## 2026-06-03T10:56:07.3006878-03:00 - branding_sequence_xgm2_probe

- Task: branding_sequence_xgm2_probe
- Skills: sgdk-build-wrapper-operator, sgdk-runtime-coder, scene-state-architect, megadrive-vdp-budget-analyst, xgm2-audio-director
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Fase 0 branding: preserved existing brand_* PNG baseline, added WAV XGM2 cue declarations/assets, integrated runtime_probe boot/tick, generated explicit blocked visual_delivery_gate_report.

## 2026-06-03T11:09:40.7744181-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=9
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T11:10:00.1427886-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, emulator_evidence_stale, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale

## 2026-06-03T11:11:36.1661598-03:00 - branding_sequence_xgm2_probe_capture

- Task: branding_sequence_xgm2_probe_capture
- Skills: sgdk-build-wrapper-operator, sgdk-runtime-coder, scene-state-architect, megadrive-vdp-budget-analyst, xgm2-audio-director
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, emulator_evidence_stale, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale
- Notes: Fase 0/branding: preserved brand_* PNG baseline, added XGM2 WAV cues, integrated MDRuntimeProbe boot/tick, reduced inactive line-scroll uploads, rebuilt ROM SHA256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, captured TargetScene 0 in BlastEm with screenshot/save.sram/runtime_metrics partial; one CPU budget spike remains at frame_index 128 so performance gate stays blocked.


## 2026-07-03 - project_birth_fase1

- Task: nascimento canonico + FASE 1 (GDD e first playable slice)
- Projeto criado via `new_project.sh` (template `tools/sgdk_wrapper/modelo`, rota Vibe Playable `blocked_no_premium_source`)
- NOTA DE VERDADE: as entradas de changelog acima desta (2026-06-03) foram herdadas do template e descrevem builds do projeto-modelo, nao deste projeto; `out/` foi removido no nascimento
- `doc/project_context_manifest.json` classificado `aaa_game`/`active` (validado: blockers=0)
- `doc/genre_specialization_manifest.json` criado com opt-in humano `brawler_belt_scroll`
- FASE 1 escrita: `doc/00-project-brief.md`, `doc/11-gdd.md`, `doc/12-roteiro.md` (roteiro scope), `doc/13-spec-cenas.md` (CAIS_01 + seeds S2-S6)
- Tecnicas do slice: `line_scrolling`, `camera_scroll_management`, `hitstop_camera_shake_feedback`; adiadas: `palette_cycling`, `shadow_highlight_mode` (status LABORATORIO)
- Host de producao: Manjaro Linux com loop build->BlastEm provado via SMOKE_TEST nesta mesma sessao (Wine/binfmt)
- Status geral do projeto: `documentado`; sem build, sem arte, sem evidencia (correto para FASE 1)
- Proxima fase: FASE 2 (tdd_contract + brawler design contract) e FASE 3 (direcao de arte CAIS_01)

## 2026-07-03 - fase2_fase3_contratos_e_direcao_de_arte

- Task: FASE 2 (architecture first) + FASE 3 (direção de arte)
- FASE 2: emitidos e validados doc/contracts/{tdd_contract, brawler_belt_scroll_design_contract, mechanic_contract, level_blueprint, enemy_roster}.json + frame_data/ (6 arquetipos)
- doc/genre_specialization_manifest.json reescrito schema-conform (opt-in humano, freeze_axes_acknowledgement)
- Gates: audit_game_design_contracts=passed blockers=0; brawler validator passed=11 failed=0 (CI 23/23); schemas 100% via jsonschema
- FASE 3: doc/art/ completo (decision record angular_cps2_fighter conf 0.70, master_style_manifest, moodboard, brand_identity planned, drift policy, diagnostic 3_no_art, art_generation_brief)
- 16 PRDs materializados; check_prd_readiness=ok blockers=0 (prototype)
- Higiene: corrigido compiled_from com caminho absoluto de drive Windows herdado do template; validate_project_hygiene=passed
- Metodologia: claims classificados (critical_motion not_applicable em planning, road_physics/modular_boss not_applicable); validate_project_methodology=passed
- BLOCKER ATIVO: canal de geração de imagem indisponível no host (generation_channel_decision.json); premium source aguarda canal
- Fix canônico correlato (tools/sgdk_wrapper): validate_brawler_belt_scroll_specialization.ps1 corrigido para pwsh 7.5+ (OrderedDictionary + DateKind String), CI 23/23

## 2026-07-03 - resposta_ao_parecer_curatorial

- Task: correcoes curatoriais (parecer humano de 2026-07-03)
- Status renomeado: pre_producao_documentada_com_template_tecnico (nao e prototipo/slice/jogo)
- Novos contratos: slice_scope_contract.json (anti-falso-verde) e tilemap_streaming_contract.json (cais 1344px: janela 64x32, max 2 colunas/frame, seam policy, fallbacks; scene_local_preload vetado)
- Direcao de arte: trio de prova MD-nativo (SOR2/Shinobi III/Comix Zone) + human_ratification=pending + vdp_survival_proof (contact sheet 320x224) + fallback vibrant_16bit_pixel
- Rota de arte corrigida: IA apenas concept_art; doc/art/prompt_pack/ com 6 docs de prompts especificos para geracao humana; sequencia autoral model sheet -> lineart 1px -> key poses -> strips
- art_gameplay_direction_gate.json preenchido (producao autorizada so para Etapa A)
- TDD: audio_ownership corrigido para XGM2 real (FM+PSG do driver, SFX via PCM, sem acesso direto), tilemap_column_streamer no DMA ownership, riscos r5/r6
- Divida declarada: scene_branding.c viola ownership (CRAM/HScroll CPU no update + PSG direto) - refatorar antes do runtime
- Wrappers locais .bat corrigidos (profundidade de delegacao corrigida de tres para dois niveis); metadados build_v001/v002 herdados removidos
- Framework canonico: 4 correcoes encaminhadas (ready_for_aaa em planning, source/res no diagnostico, higiene vs texto historico, visual gate em out/logs)
- validation_report regenerado: de 4 erros para 1 (res_graph ausente, honesto ate a conversao de arte). Corrigidos: doc_refs verificaveis das tecnicas (spec+memory bank+changelog), .agent local como symlink canonico, marcadores do GDD (kit do jogador, ensino invisivel, qualidade visual, direcao sonora). Blockers restantes sao estado honesto de pre-producao (gates visuais sem arte, closeout sem cena)
