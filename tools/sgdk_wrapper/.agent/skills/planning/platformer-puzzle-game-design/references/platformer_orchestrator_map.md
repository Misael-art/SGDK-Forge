# Platformer Precision 2D Orchestrator Map

Quem faz o que. Este arquivo existe para que a skill orquestradora nao vire catch-all.

## Producao de design de superficie (platformer_precision_2d_design_contract)

| Secao | Skill delegada | Artefato de saida |
|---|---|---|
| `player_profile` (run_speed, jump_velocity, gravity, coyote_time) | `game-design-planning` (ja no GDD) + `systems-mechanics-validator` (numeric) | `doc/11-gdd.md` + design contract |
| `player_profile.dash_enabled`, `wall_jump_enabled` (sprite logic) | `sgdk-runtime-coder` (FSM) + `character-design` (sprite resolution) | design contract (referencia) |
| `player_profile.voxel_size` (16x16, 16x24) | `megadrive-pixel-strict-rules` (sprite budget) | design contract (advisory) |
| `ability_set[].frames_active`, `frames_cooldown` | `sgdk-runtime-coder` (FSM de ability) + `systems-mechanics-validator` (numeric) | design contract (referencia) |
| `hazard_catalog[].damage`, `respawn_pattern` | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `collectible_catalog[].value`, `respawn_pattern` | `systems-mechanics-validator` (numeric) | design contract |
| `level_catalog[].level_segment_frame_data_path` | esta skill (orquestra) | `doc/levels/<id>/level_segment_frame_data.json` |
| `level_catalog[].par_time_seconds` (speedrun) | `game-design-planning` (GDD) | design contract |
| `level_catalog` (VRAM/sprite budget por level) | `megadrive-vdp-budget-analyst` | `out/logs/vdp_budget_audit.json` |
| `modes` (kind, lives_policy, score_policy) | `game-design-planning` (GDD) | design contract |
| `balance.method` | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `balance.evidence_paths` | `sgdk-code-reviewer` (clear time logs) + humano | design contract |
| `audio` (BGM stage, SFX jump, SFX coin, ambient wind) | `xgm2-audio-director` | design contract (referencia) |

## Producao de level segment frame data (platformer_level_segment_frame_data)

| Campo | Skill delegada |
|---|---|
| `layout.width_tiles`, `height_tiles` | `level-design-canonical` (mapa) + `multi-plane-composition` (BG) |
| `layout.tile_size_px` | `megadrive-pixel-strict-rules` (sprite budget) |
| `layout.gravity_zone_count` | `sgdk-runtime-coder` (gravity FSM) |
| `parallax_layers[].parallax_factor` | `multi-plane-composition` (camadas) |
| `parallax_layers[].animation_idle_frames` | `sprite-animation` |
| `hazard_zones[].hazard_id` (foreign key) | `game-design-planning` (GDD) |
| `hazard_zones[].frames_active`, `frames_idle` | `sgdk-runtime-coder` (hazard FSM) |
| `collectible_zones[].collectible_id` (foreign key) | `game-design-planning` (GDD) |
| `checkpoint_zones[].frames_respawn` | `sgdk-runtime-coder` (save FSM) |
| `jump_arcs[].max_height_tiles`, `horizontal_distance_tiles` | `sgdk-runtime-coder` (physics) + `systems-mechanics-validator` (numeric) |
| `jump_arcs[].frames_to_apex` | `sgdk-runtime-coder` (physics FSM) |

## Producao do validator (validate_platformer_precision_2d_specialization.ps1)

| Passo | Origem |
|---|---|
| Carrega 4 schemas | `tools/sgdk_wrapper/schemas/*.schema.json` |
| Le manifest | `doc/genre_specialization_manifest.json` |
| Le design contract | `doc/platformer_precision_2d_design_contract.json` (path do manifest) |
| Audita level segment frame data | `doc/levels/<id>/level_segment_frame_data.json` |
| Determina fase | `doc/project_methodology_manifest.json::claim_ceiling` |
| Aplica 3 blockers phase-aware | registry-driven, gate apenas em ready_for_aaa/closeout |
| Emite report | `out/logs/platformer_specialization_report.json` |

## TDD canonico e o opt-in

`tdd-authoring` nao muda. A unica adicao eh:

- secao 12.1 no SKILL.md do tdd-authoring: "Anexo opt-in por especializacao"
- um campo opcional `tdd_annex_opt_in` no TDD, no formato:
  ```json
  {
    "specialization_id": "platformer_precision_2d",
    "design_contract_path": "doc/platformer_precision_2d_design_contract.json",
    "role": "delegate non-runtime concerns (player_profile/abilities/hazards/collectibles/levels/modes) to this contract; runtime/FSM/audio remain in TDD canonico"
  }
  ```

## Limites praticos do MD (referencia rapida)

- 16x16 player sprite (max 24x24 boss)
- 2-6 px/frame run speed (max 6)
- 3-6 tiles jump height (acima de 6 exige gravity tuning)
- 4-6 frames coyote time (acima de 6 quebra desafio)
- 4-6 frames jump buffer (acima de 6 quebra desafio)
- 4-30 frames ability duration (acima de 30 quebra ritmo precision)
- 50-100 levels por game (acima exige save data > 32KB)
- 30-60 frames death restart (0.5-1s)
- 5-100 levels canonico range
- 4-6 frames best time per level (4 bytes = 65535 centiseconds = 10.9 min cap)
