# Strategy Tower Defense Orchestrator Map

Quem faz o que. Este arquivo existe para que a skill orquestradora nao vire catch-all.

## Producao de design de superficie (strategy_tower_defense_design_contract)

| Secao | Skill delegada | Artefato de saida |
|---|---|---|
| `grid_layout` (width, height, slots, geometry) | `level-design-canonical` (mapa) + `multi-plane-composition` (BG) | `level_blueprint.json` + design contract |
| `grid_layout.vram_budget_estimate_kb` | `megadrive-vdp-budget-analyst` | `out/logs/vdp_budget_audit.json` |
| `tower_catalog` (id, category, tier, cost) | `game-design-planning` (GDD) | `doc/11-gdd.md` |
| `tower_catalog[].tower_frame_data_path` | esta skill (orquestra) | `doc/towers/<id>/tower_frame_data.json` |
| `enemy_catalog` (id, archetype, hp, speed) | `game-design-planning` + `systems-mechanics-validator` | `doc/11-gdd.md` + design contract |
| `wave_composition` (wave_count, boss_interval, waves[]) | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `modes` (kind, save_model) | `game-design-planning` (GDD) | design contract |
| `economy` (starting_currency, multipliers, bonuses) | `systems-mechanics-validator` (numeric) | design contract |
| `balance.method` | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `balance.evidence_paths` | `sgdk-code-reviewer` (playtest logs) + humano | design contract |
| `audio` (BGM wave, SFX tower fire, ambient map) | `xgm2-audio-director` | design contract (referencia) |

## Producao de tower frame data (strategy_tower_frame_data)

| Campo | Skill delegada |
|---|---|
| `tier_id`, `tier_name` | `game-design-planning` (GDD) |
| `cost` | `systems-mechanics-validator` (economy curve) |
| `damage`, `range_tiles`, `fire_rate_frames` | `sgdk-runtime-coder` (FSM de ataque) + `systems-mechanics-validator` (DPS table) |
| `projectile_speed_tiles_per_second` | `sgdk-runtime-coder` (projectile FSM) |
| `splash_radius_tiles`, `slow_pct`, `slow_duration_frames`, `chain_targets` | `systems-mechanics-validator` (special mechanics) |
| `support_aura_bonus_pct`, `support_aura_radius_tiles` | `sgdk-runtime-coder` (aura FSM) |
| `economy_gold_per_kill` | `systems-mechanics-validator` (economy curve) |
| `ultimate_unlocked_at_wave` | `game-design-planning` (progression gate) |
| `animation_idle_frames`, `animation_fire_frames` | `sprite-animation` |
| `voxel_size` | `megadrive-pixel-strict-rules` (sprite budget) |

## Producao do validator (validate_strategy_tower_defense_specialization.ps1)

| Passo | Origem |
|---|---|
| Carrega 4 schemas | `tools/sgdk_wrapper/schemas/*.schema.json` |
| Le manifest | `doc/genre_specialization_manifest.json` |
| Le design contract | `doc/strategy_tower_defense_design_contract.json` (path do manifest) |
| Audita tower frame data | `doc/towers/<id>/tower_frame_data.json` |
| Determina fase | `doc/project_methodology_manifest.json::claim_ceiling` |
| Aplica 3 blockers phase-aware | registry-driven, gate apenas em ready_for_aaa/closeout |
| Emite report | `out/logs/strategy_specialization_report.json` |

## TDD canonico e o opt-in

`tdd-authoring` nao muda. A unica adicao eh:

- secao 12.1 no SKILL.md do tdd-authoring: "Anexo opt-in por especializacao"
- um campo opcional `tdd_annex_opt_in` no TDD, no formato:
  ```json
  {
    "specialization_id": "strategy_tower_defense",
    "design_contract_path": "doc/strategy_tower_defense_design_contract.json",
    "role": "delegate non-runtime concerns (grid/towers/enemies/waves/economy) to this contract; runtime/FSM/audio remain in TDD canonico"
  }
  ```

## Limites praticos do MD (referencia rapida)

- 8-24 slots de torre por mapa (acima de 24 quebra a UI)
- 4-8 tipos de torre no catalog (acima de 8 polui o menu)
- 3-8 arquetipos de inimigo (acima de 8 exige IA complexa)
- 5-50 waves por run (acima de 50 exige save data maior que 32KB)
- 8-16 inimigos simultaneos na tela (sprite ceiling do VDP)
- Fire rate minimo 6 frames entre ataques (CPU saturation; constraint phase-aware)
- VRAM grid <= 64KB (BG_A 32x32 + BG_B 32x32 + tiles de path = tipicamente 24-48KB)
