# Racing Arcade Orchestrator Map

Quem faz o que. Este arquivo existe para que a skill orquestradora nao vire catch-all.

## Producao de design de superficie (racing_arcade_design_contract)

| Secao | Skill delegada | Artefato de saida |
|---|---|---|
| `vehicle_catalog` (id, weight_class, lore_id) | `game-design-planning` (ja no GDD) | `doc/11-gdd.md` |
| `vehicle_catalog[].vehicle_frame_data_path` | esta skill (orquestra) | `doc/vehicles/<id>/vehicle_frame_data.json` |
| `vehicle_catalog[].head_metric` (sprite scale) | `character-design` | design contract (advisory) |
| `track_catalog` (track_id, length_pixels, lane_count) | `level-design-canonical` (pista) + `multi-plane-composition` (BG) | `level_blueprint.json` + design contract |
| `track_catalog[].weather_policy` (clear/rain/night) | `sgdk-runtime-coder` (FSM weather) + `xgm2-audio-director` (BGM) | design contract (referencia) |
| `track_catalog[].track_music_loop_seconds` | `xgm2-audio-director` | design contract (referencia) |
| `track_catalog` VRAM/sprite budget por track | `megadrive-vdp-budget-analyst` | `out/logs/vdp_budget_audit.json` |
| `race_modes` (kind, laps, ai_count) | `game-design-planning` (GDD) | design contract |
| `item_catalog` (category, duration_frames, stack_max) | `systems-mechanics-validator` (numeric) | design contract |
| `ai_profile.difficulty_levels` (3-5 levels) | `systems-mechanics-validator` (balance) | design contract |
| `ai_profile.drafting_enabled`, `rubber_banding_enabled` | `sgdk-runtime-coder` (AI FSM) | design contract (referencia) |
| `hud_config` (show_position/lap_counter/lap_time) | `megadrive-pixel-strict-rules` (HUD layout) | design contract (referencia) |
| `balance.method` | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `balance.evidence_paths` | `sgdk-code-reviewer` (lap time logs) + humano | design contract |
| `audio` (BGM track, SFX drift, SFX boost, SFX crash) | `xgm2-audio-director` | design contract (referencia) |

## Producao de vehicle frame data (racing_vehicle_frame_data)

| Campo | Skill delegada |
|---|---|
| `stats.top_speed_kmh`, `acceleration_frames_to_top` | `systems-mechanics-validator` (numeric) |
| `stats.handling_rad_per_sec` | `sgdk-runtime-coder` (FSM steering) |
| `stats.drift_factor` | `systems-mechanics-validator` (drift curve) |
| `stats.boost_consumption_pct_per_sec` | `sgdk-runtime-coder` (boost FSM) |
| `stats.weight_kg` | `systems-mechanics-validator` (collision mass) |
| `stats.tire_grip_pct`, `downforce_pct` | `sgdk-runtime-coder` (physics FSM) |
| `animation.animation_idle_frames`, `drift_frames`, `boost_frames`, `crash_frames` | `sprite-animation` |
| `animation.voxel_size` | `megadrive-pixel-strict-rules` (sprite budget) |

## Producao do validator (validate_racing_arcade_specialization.ps1)

| Passo | Origem |
|---|---|
| Carrega 4 schemas | `tools/sgdk_wrapper/schemas/*.schema.json` |
| Le manifest | `doc/genre_specialization_manifest.json` |
| Le design contract | `doc/racing_arcade_design_contract.json` (path do manifest) |
| Audita vehicle frame data | `doc/vehicles/<id>/vehicle_frame_data.json` |
| Determina fase | `doc/project_methodology_manifest.json::claim_ceiling` |
| Aplica 3 blockers phase-aware | registry-driven, gate apenas em ready_for_aaa/closeout |
| Emite report | `out/logs/racing_specialization_report.json` |

## TDD canonico e o opt-in

`tdd-authoring` nao muda. A unica adicao eh:

- secao 12.1 no SKILL.md do tdd-authoring: "Anexo opt-in por especializacao"
- um campo opcional `tdd_annex_opt_in` no TDD, no formato:
  ```json
  {
    "specialization_id": "racing_arcade",
    "design_contract_path": "doc/racing_arcade_design_contract.json",
    "role": "delegate non-runtime concerns (vehicles/tracks/modes/items/ai/hud) to this contract; runtime/FSM/audio remain in TDD canonico"
  }
  ```

## Limites praticos do MD (referencia rapida)

- 5-7 AI opponents (cap frozen; max 8 sprite ceiling)
- 4-16 tracks por game (acima exige save data > 32KB)
- 3-5 laps por race (acima eh muito longo)
- 1-3 item slots (4+ polui UI)
- top_speed_kmh <= 256 (u8 cap)
- boost 0-100% (u8 cap)
- SRAM 32KB canonica (best lap + total time + ghost data = 16 bytes/track; max 2048 tracks = 32KB)
- 4 lanes (acima de 4 polui o player de RAM)
- Item duration <= 600 frames (10s)
- Light/formula drift >= 30; heavy drift >= 10
- collision_model must be arcade_forgiving OR sim_fair (NAO realistic_full)
