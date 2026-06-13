# Changelog Canonico - SCENE_TILEMAP_CURATION_FIXTURE

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

## 2026-06-06T09:20:00-03:00 - tilemap_fixture_reports_and_scene

- Task: tilemap_fixture_reports_and_scene
- Asset snapshots:
  - img_fixture_scene_tilemap -> v001 (res/bgs/fixture_scene_320x224_indexed.png)
- Notes: Added a 320x224 indexed scene input in rascunho/, generated scene_tilemap_conversion_report + tilemap_flag_report + per_tile_palette_conflict_report in out/logs/, and added runtime scene APP_SCENE_TILEMAP_FIXTURE.

## 2026-06-06T23:43:15.3091022-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_fixture_scene_tilemap -> v001 (res/bgs/fixture_scene_320x224_indexed.png)
- ROM: build_v003 (sha256 18aec2f55902aa572a7c49fbc15de27c2e2c8e8ad2f2693a691537f1289459ae, 262144 bytes)
- Validation: errors=0, warnings=12
- Blockers: project_naming_invalid, project_methodology_manifest_invalid, gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: report_older_than_rom

## 2026-06-06T23:43:37.7179979-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 18aec2f55902aa572a7c49fbc15de27c2e2c8e8ad2f2693a691537f1289459ae, 262144 bytes)
- Validation: errors=0, warnings=10
- Blockers: project_naming_invalid, project_methodology_manifest_invalid, gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

