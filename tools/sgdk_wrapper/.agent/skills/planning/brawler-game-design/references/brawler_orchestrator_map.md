# Brawler Belt-Scroll Orchestrator Map

Quem faz o que. Este arquivo existe para que a skill orquestradora nao vire catch-all.

## Producao de design de superficie (brawler_belt_scroll_design_contract)

| Secao | Skill delegada | Artefato de saida |
|---|---|---|
| `player_roster` (id, role, archetype, lore_id) | `game-design-planning` (ja no GDD) | `doc/11-gdd.md` |
| `player_roster[].special_move_id` (frame data) | `sprite-animation` (animacao) + `sgdk-runtime-coder` (FSM) | design contract (referencia) |
| `player_roster[].head_metric` (sprite scale) | `character-design` | design contract (advisory) |
| `enemy_archetypes[].enemy_archetype_frame_data_path` | esta skill (orquestra) | `doc/enemies/<id>/enemy_archetype_frame_data.json` |
| `pickup_catalog` (id, category, drop_chance_pct) | `systems-mechanics-validator` (numeric) | design contract |
| `pickup_catalog[].max_on_screen` (sprite ceiling) | `megadrive-vdp-budget-analyst` | design contract (referencia) |
| `stages` (lane_count, wave_count, boss_archetype_id) | `level-design-canonical` (mapa) + `multi-plane-composition` (BG) | `level_blueprint.json` + design contract |
| `stages[].bg_music_loop_seconds` | `xgm2-audio-director` | design contract (referencia) |
| `stages` VRAM/sprite budget por stage | `megadrive-vdp-budget-analyst` | `out/logs/vdp_budget_audit.json` |
| `modes` (kind, starting_lives, continue_policy) | `game-design-planning` (GDD) | design contract |
| `combat.move_set` (3-6 moves) | `sgdk-runtime-coder` (FSM) + `character-design` (anim) | design contract (referencia) |
| `combat.iframe_window_frames` (>=8) | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `combat.super_bar_max` (50-200) | `game-design-planning` + `systems-mechanics-validator` | design contract |
| `balance.method` | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `balance.evidence_paths` | `sgdk-code-reviewer` (wave clear logs) + humano | design contract |
| `audio` (BGM stage, BGM boss, SFX hit, SFX pickup) | `xgm2-audio-director` | design contract (referencia) |

## Producao de enemy archetype frame data (brawler_enemy_archetype_frame_data)

| Campo | Skill delegada |
|---|---|
| `base_stats.hp`, `damage` | `systems-mechanics-validator` (numeric) |
| `base_stats.move_speed_px_per_second` | `sgdk-runtime-coder` (FSM pathfinding) |
| `base_stats.score_reward` | `systems-mechanics-validator` (economy) |
| `base_stats.hit_stun_frames` | `sgdk-runtime-coder` (FSM hit reaction) |
| `drop_table.drop_pool[].pickup_id` (foreign key) | `game-design-planning` (GDD) |
| `drop_table.guaranteed_drop` (foreign key) | `game-design-planning` (GDD) |
| `animation.animation_idle_frames` | `sprite-animation` |
| `animation.voxel_size` (16x16, 16x24, etc) | `megadrive-pixel-strict-rules` (sprite budget) |
| `boss_phases[].behavior` | `sgdk-runtime-coder` (boss FSM) |
| `boss_phases[].attack_pattern_frames` | `sgdk-runtime-coder` (telegraph pattern) |

## Producao do validator (validate_brawler_belt_scroll_specialization.ps1)

| Passo | Origem |
|---|---|
| Carrega 4 schemas | `tools/sgdk_wrapper/schemas/*.schema.json` |
| Le manifest | `doc/genre_specialization_manifest.json` |
| Le design contract | `doc/brawler_belt_scroll_design_contract.json` (path do manifest) |
| Audita enemy archetype frame data | `doc/enemies/<id>/enemy_archetype_frame_data.json` |
| Determina fase | `doc/project_methodology_manifest.json::claim_ceiling` |
| Aplica 3 blockers phase-aware | registry-driven, gate apenas em ready_for_aaa/closeout |
| Emite report | `out/logs/brawler_specialization_report.json` |

## TDD canonico e o opt-in

`tdd-authoring` nao muda. A unica adicao eh:

- secao 12.1 no SKILL.md do tdd-authoring: "Anexo opt-in por especializacao"
- um campo opcional `tdd_annex_opt_in` no TDD, no formato:
  ```json
  {
    "specialization_id": "brawler_belt_scroll",
    "design_contract_path": "doc/brawler_belt_scroll_design_contract.json",
    "role": "delegate non-runtime concerns (roster/enemies/pickups/stages/modes/combat) to this contract; runtime/FSM/audio remain in TDD canonico"
  }
  ```

## Limites praticos do MD (referencia rapida)

- 8 inimigos simultaneos na tela (cap frozen)
- 1-2 jogadores (cap frozen; 3+ quebra sprite ceiling)
- 1-3 lanes (4+ exige camera split)
- 2-8 waves por stage (acima de 8 waves quebra ritmo)
- 1-3 boss phases (4+ sem telegraph fica ilegivel)
- 1-2 special moves por personagem
- Iframe 8-60 frames (abaixo de 8 eh hit stacking; acima de 60 quebra ritmo)
- 4-6 enemy archetypes (acima exige IA complexa)
- 3-5 stages (acima exige save data > 32KB SRAM)
- 4-8 pickups por categoria (acima polui UI)
