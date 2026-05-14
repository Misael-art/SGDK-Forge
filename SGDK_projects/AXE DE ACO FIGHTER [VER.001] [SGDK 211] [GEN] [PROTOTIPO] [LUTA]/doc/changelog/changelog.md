# Changelog Canonico - AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]

## Estado Inicial

- projeto bootstrapado a partir do wrapper central
- documentacao minima materializada
- scene regression declarada em `doc/scene-regression.json`
- companion inicial esperado em `doc/scene-contracts.json`

## 2026-05-14T05:08:51.2348444-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_stage_bg_b -> v001 (res/bgs/stage_bg_b.png)
  - img_stage_bg_a -> v001 (res/bgs/stage_bg_a.png)
  - spr_marina_idle -> v001 (res/sprites/marina/idle.png)
  - spr_marina_walk_forward -> v001 (res/sprites/marina/walk_forward.png)
  - spr_marina_walk_back -> v001 (res/sprites/marina/walk_back.png)
  - spr_marina_dash -> v001 (res/sprites/marina/dash.png)
  - spr_marina_crouch -> v001 (res/sprites/marina/crouch.png)
  - spr_marina_hop -> v001 (res/sprites/marina/hop.png)
  - spr_marina_guard -> v001 (res/sprites/marina/guard.png)
  - spr_marina_light_attack -> v001 (res/sprites/marina/light_attack.png)
  - spr_marina_medium_attack -> v001 (res/sprites/marina/medium_attack.png)
  - spr_marina_sweep_or_throw -> v001 (res/sprites/marina/sweep_or_throw.png)
  - spr_marina_hurt -> v001 (res/sprites/marina/hurt.png)
  - spr_marina_knockdown -> v001 (res/sprites/marina/knockdown.png)
  - spr_marina_getup -> v001 (res/sprites/marina/getup.png)
  - spr_bento_idle -> v001 (res/sprites/bento/idle.png)
  - spr_bento_walk_forward -> v001 (res/sprites/bento/walk_forward.png)
  - spr_bento_walk_back -> v001 (res/sprites/bento/walk_back.png)
  - spr_bento_dash -> v001 (res/sprites/bento/dash.png)
  - spr_bento_crouch -> v001 (res/sprites/bento/crouch.png)
  - spr_bento_hop -> v001 (res/sprites/bento/hop.png)
  - spr_bento_guard -> v001 (res/sprites/bento/guard.png)
  - spr_bento_light_attack -> v001 (res/sprites/bento/light_attack.png)
  - spr_bento_medium_attack -> v001 (res/sprites/bento/medium_attack.png)
  - spr_bento_sweep_or_throw -> v001 (res/sprites/bento/sweep_or_throw.png)
  - spr_bento_hurt -> v001 (res/sprites/bento/hurt.png)
  - spr_bento_knockdown -> v001 (res/sprites/bento/knockdown.png)
  - spr_bento_getup -> v001 (res/sprites/bento/getup.png)
  - spr_hit_spark -> v001 (res/sprites/fx/hit_spark.png)
  - spr_dust -> v001 (res/sprites/fx/dust.png)
- ROM: build_v001 (sha256 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f, 262144 bytes)
- Validation: errors=0, warnings=5
- Blockers: agent_context_degraded, visual_gate_blocked, changelog_missing
- Emulator evidence: report_older_than_rom

## 2026-05-14T05:09:31.4904217-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f, 262144 bytes)
- Validation: errors=0, warnings=3
- Blockers: agent_context_degraded, visual_gate_blocked
- Emulator evidence: sem_sessao

## 2026-05-14T05:14:24.2814853-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f, 262144 bytes)
- Validation: errors=0, warnings=2
- Blockers: visual_gate_blocked
- Emulator evidence: sem_sessao

## 2026-05-14T05:14:55.9557165-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f, 262144 bytes)
- Validation: errors=0, warnings=2
- Blockers: visual_gate_blocked
- Emulator evidence: runtime_metrics_stale


## 2026-05-14T05:31:03-03:00 - final_real_evidence_closeout

- Task: final_real_evidence_closeout
- ROM: build_v001 sha256 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f, 262144 bytes, path F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\rom.bin
- BlastEm evidence: boot=ok, fresh_sram_confirmed=True, screenshot F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\benchmark_visual.png, sram F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\save.sram
- Runtime capture: status=partial, scene_id=3, frames_seen=151, samples=32, over_budget_frames=0
- Validation: errors=0, warnings=2, blockers=visual_gate_blocked, local_rasterization_used_as_final, source_to_rom_mismatch
- Res graph: status=ok, vram=ok, overlaps=0
- Closeout: status=blocked, substeps ok
- Final classification: prototype_playable + visual_gate_blocked; not Stable, not AAA
