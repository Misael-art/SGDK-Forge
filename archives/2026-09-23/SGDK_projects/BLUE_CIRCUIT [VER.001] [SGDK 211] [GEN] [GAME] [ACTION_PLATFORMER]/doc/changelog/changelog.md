# Changelog Canonico - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

## 2026-06-27 - human_visual_gates_approved_for_vdp_translation

- Registrada aprovacao humana dos tres gates visuais: storyboard, model sheet e spritesheet.
- `premium_source_manifest`, `human_approval_record`, `human_visual_gate_plan` e `asset-register` agora permitem traducao VDP dos candidatos aprovados.
- Mantidos bloqueios de entrega: sem conversao VDP validada, sem promocao para `res/`, sem build vigente, sem BlastEm e sem budget final.

## 2026-06-27 - visual_candidates_three_human_gates

- Ambiente de agente recuperado apos reinstalar `graphifyy` via `uv tool install graphifyy --force`; a falha era do shim Graphify/uv, nao do projeto.
- Criados tres candidatos visuais locais em `data/source_art/`:
  - `storyboard/blue_circuit_storyboard_candidate_v001.png`
  - `model_sheet/blue_circuit_model_sheet_candidate_v001.png`
  - `spritesheet/blue_circuit_spritesheet_candidate_v001.png`
- Registrados hashes SHA-256 no `premium_source_manifest`, `doc/18-asset-register.json` e `doc/human_approval_record.md`.
- Adicionado `doc/contracts/human_visual_gate_plan.json` para limitar validacao humana a storyboard, model sheet e spritesheet.
- Atualizados GDD, TDD, spec de cenas, QA, roteiro, LDD e memory para refletir que os assets sao candidatos de revisao, nao arte final.
- Mantidos bloqueios: sem aprovacao humana, sem conversao VDP, sem promocao para `res/`, sem runtime de entrega, sem build vigente e sem evidencia BlastEm.

## 2026-06-25 - bootstrap_documental_vibe_playable

- Projeto criado a partir do template canonico com `new_project.bat`.
- Ambiente de agente validado apos correccao temporaria do shim Graphify bloqueado pelo host.
- Contexto classificado como `aaa_game` com teto `vertical_slice`.
- GDD, TDD, spec de cenas, QA, asset register, methodology e memory atualizados antes de runtime.
- Direcao do jogo registrada: action platformer curto, autoral, com correr, pular, atirar, um inimigo comum, um mini-boss, title e fim.
- `camera_scroll_management` declarada em `doc/technique_usage_manifest.json` como tecnica documentada, sem promocao ou runtime.
- Rota Vibe Playable mantida bloqueada ate fonte premium, aprovacao humana, conversao VDP, build canonico e evidencia BlastEm.
- Validacoes de governanca passaram: contexto, metodologia, higiene e preflight host.
- `validate_resources` gerou report bloqueado com blockers esperados: visual gate, direcao visual, audio validation, res_graph/budget, conversao tilemap/paleta, freshness e scene closeout.
- Nenhuma ROM, screenshot, SRAM, VDP dump, audio final ou asset final foi criado nesta entrada.
- Entradas herdadas de build/captura do template nao sao evidencia deste projeto novo e foram removidas do changelog canonico ativo.
## 2026-06-27T19:53:33.8571531-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_bc_title_logo -> v001 (res/blue_circuit/title_logo.png)
  - img_bc_stage_bg -> v001 (res/blue_circuit/stage_01_bg.png)
  - img_bc_stage_fg -> v001 (res/blue_circuit/stage_01_fg.png)
  - spr_bc_player_idle -> v001 (res/blue_circuit/player_idle.png)
  - spr_bc_player_run -> v001 (res/blue_circuit/player_run.png)
  - spr_bc_player_jump -> v001 (res/blue_circuit/player_jump.png)
  - spr_bc_player_shoot -> v001 (res/blue_circuit/player_shoot.png)
  - spr_bc_line_sentry_idle -> v001 (res/blue_circuit/line_sentry_idle.png)
  - spr_bc_breaker_core_idle -> v001 (res/blue_circuit/breaker_core_idle.png)
  - spr_bc_projectile_pulse -> v001 (res/blue_circuit/projectile_pulse.png)
- ROM: build_v003 (sha256 9aae82eca82141aac46e6aa194808482729de01d7c57cc0f291553aba8201ffa, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: visual_gate_blocked, visual_direction_failed, audio_validation_missing, changelog_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: report_older_than_rom

## 2026-06-27T19:54:32.6481405-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 9aae82eca82141aac46e6aa194808482729de01d7c57cc0f291553aba8201ffa, 262144 bytes)
- Validation: errors=0, warnings=6
- Blockers: visual_gate_blocked, visual_direction_failed, audio_validation_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

## 2026-06-27T22:55:42.3266941-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 7339b17d7706aa576c1bf3dce7ddd01c0e154a4260bb30bf30e09c4861a4557f, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_direction_failed, audio_validation_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-27T22:56:05.9773603-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 7339b17d7706aa576c1bf3dce7ddd01c0e154a4260bb30bf30e09c4861a4557f, 262144 bytes)
- Validation: errors=0, warnings=6
- Blockers: visual_gate_blocked, visual_direction_failed, audio_validation_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

## 2026-06-27T23:02:04.3632485-03:00 - blastem_scene3_technical_closeout

- Task: blastem_scene3_technical_closeout
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 7339b17d7706aa576c1bf3dce7ddd01c0e154a4260bb30bf30e09c4861a4557f, 262144 bytes)
- Validation: errors=0, warnings=4
- Blockers: visual_gate_blocked, visual_direction_failed, scene_closeout_gate_stale
- Emulator evidence: ok
- Notes: ROM build_v004 hash 7339b17d7706aa576c1bf3dce7ddd01c0e154a4260bb30bf30e09c4861a4557f captured in BlastEm with SDL_AUDIODRIVER=dummy; target_scene=3 matched runtime_scene_id=3; screenshot and fresh save.sram recorded. Status remains technical_ready_creative_blocked because visual_gate_blocked and visual_direction_failed remain active; scene_closeout_gate_report is stale after report refresh.

## 2026-06-28T10:44:54.0500416-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_bc_stage_bg -> v002 (res/blue_circuit/stage_01_bg.png)
  - spr_bc_player_idle -> v002 (res/blue_circuit/player_idle.png)
  - spr_bc_player_run -> v002 (res/blue_circuit/player_run.png)
  - spr_bc_player_jump -> v002 (res/blue_circuit/player_jump.png)
  - spr_bc_player_shoot -> v002 (res/blue_circuit/player_shoot.png)
  - spr_bc_line_sentry_idle -> v002 (res/blue_circuit/line_sentry_idle.png)
  - spr_bc_breaker_core_idle -> v002 (res/blue_circuit/breaker_core_idle.png)
  - spr_bc_projectile_pulse -> v002 (res/blue_circuit/projectile_pulse.png)
- ROM: build_v005 (sha256 ff8fb909620a13f5fdf402f03b1bdac292244a23096dac50ac80f3ad98bdd160, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: visual_gate_blocked, visual_direction_failed, audio_validation_stale, changelog_missing, whole_image_unique_ratio_high_without_justification, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-28T10:45:20.2166254-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v005 (sha256 ff8fb909620a13f5fdf402f03b1bdac292244a23096dac50ac80f3ad98bdd160, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: visual_gate_blocked, visual_direction_failed, audio_validation_stale, emulator_evidence_stale, whole_image_unique_ratio_high_without_justification, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-07-20T01:13:00-03:00 - p1_003_full_window_performance

- ROM: p1_003_full_window (sha256 40b924f7895386458c7810204464fe47207c40b7f97d0c4585e840ee8d21bbf5, 262144 bytes)
- Corrigido o probe MDRT que limitava a captura a 32 amostras: agora registra 900 quadros NTSC ou 750 PAL em buffer estatico.
- A medicao passou a ocorrer depois de `SPR_update` e antes de `SYS_doVBlankProcess`, preservando os picos reais da fila DMA.
- O bloco VLAB foi normalizado para 24 metricas + 64 cores e movido para `SRAM 0x1000`.
- O heartbeat deixa de escrever depois da exportacao final, evitando corrupcao da serie ja selada.
- O parser agora exige contagem completa + `probe_window_complete`, distingue NTSC/PAL, registra DMA e reconcilia agregados com a serie bruta.
- Build SGDK 2.11 limpo: ROM SHA-256 `40b924f7895386458c7810204464fe47207c40b7f97d0c4585e840ee8d21bbf5`, 262144 bytes.
- BlastEm NTSC: sessao `blastem-linux-20260720T040940Z-424385`, 900/900 amostras, P95 44, maximo 44, 0 over-budget, titulo 61.0 fps.
- BlastEm PAL forcado com `-r E`: sessao `blastem-linux-20260720T041233Z-435741`, 750/750 amostras, P95 17, maximo 17, 0 over-budget, titulo 50.3 fps.
- Ambos os bundles passaram freshness com zero blockers; screenshot NTSC passou o gate semantico.
- Claim limitado: performance estavel apenas nas janelas observadas da cena 3; audio, outras cenas, hardware real, FPGA, release e AAA continuam sem promocao.

## 2026-07-20T01:32:00-03:00 - p1_004_hardware_gate

- Adicionados schema, protocolo e validador de sessao em console Mega Drive real ou FPGA.
- O gate exige dispositivo/regiao/revisao, metodo de carga/firmware, hash da ROM igual ao bundle BlastEm, captura de boot/input/audio/gameplay, decisoes de timing/audio e atestacao externa.
- Regressao passou 3/3: sessao valida aceita, sessao pendente bloqueada e ROM divergente bloqueada.
- Mastering observou ROM de 262144 bytes alinhada, header JUE, SRAM de probe e checksum SGDK `sizebnd` `0x1527` valido.
- Estado real permanece `mastering_blocked` e `blocked_external_hardware_evidence`: nenhum console, flashcart, MiSTer/FPGA, video ou atestacao externa foi fornecido.
- Nenhum claim de hardware real, release ou AAA foi promovido.

## 2026-07-20T20:46:37-03:00 - learning_curation_checkpoint

- Registrados padroes locais de falha e sucesso com evidencia e limites de
  escopo em `doc/agent_learning/`.
- Registrados cinco candidatos de promocao, todos pendentes ou condicionados a
  maturidade; nenhum foi aplicado automaticamente.
- O Capture consolidou 15 licoes e 10 candidatos; 6 propostas foram roteadas
  para owners existentes e todas permanecem `not_applied`.
- Schema do ledger, Audit read-only e regressao do ciclo 34/34 passaram.
- A revisao canonica agora diferencia mecanismos ja integrados, prova local,
  bloqueio externo, trabalho em andamento e item nao executado.
- A retomada comeca por P2-001 doc sync; P2-002 depende de fontes coerentes e
  os demais candidatos dependem de prova cross-project ou externa.
- Nenhuma ROM foi rebuildada e nenhum claim de runtime, hardware, release ou
  `ready_for_aaa` foi promovido por esta entrada.

## 2026-07-24T00:50:00-03:00 - sprite_artifact_revalidation

- Retraidos os strips anteriores como `technical_pass_visual_fail` e
  preservados em evidencia historica.
- Adicionado `sprite_artifact_report.v2` obrigatorio com seis controles:
  clipping, ilhas, anatomia, pivot, contato de pes e delta entre frames.
- Player v002 reconstruido em 24x32 a partir do model sheet aprovado; 14
  frames passaram com zero findings.
- Gerados contact sheet e GIFs de idle, corrida, tiro e salto.
- Build SGDK 2.11 pelo bridge Linux/Wine: ROM SHA-256
  `b2fbb1bcc916bd30e26693064e4d5371df7ede2216b72b0a85dd6700c022e0b5`,
  262144 bytes.
- Sessao BlastEm fresca `blastem-linux-20260724T034450Z-505289` selou
  screenshot, SRAM, VLAB e metricas sem blockers.
- Promocao limitada a `sprite_visual_pass`; full-game, hardware real e
  `ready_for_aaa` continuam bloqueados.
