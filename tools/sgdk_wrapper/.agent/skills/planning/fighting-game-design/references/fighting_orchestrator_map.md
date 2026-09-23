# Fighting 2D Orchestrator Map

Quem faz o que. Este arquivo existe para que a skill orquestradora nao vire catch-all.

## Producao de design de superficie (fighting_2d_design_contract)

| Secao | Skill delegada | Artefato de saida |
|---|---|---|
| `roster` (id, role, archetype, lore_id) | `game-design-planning` (ja no GDD) | `doc/11-gdd.md` |
| `roster.characters[].moveset_frame_data_path` | esta skill (orquestra) | `doc/characters/<id>/moveset_frame_data.json` |
| `lore.characters` | `game-design-planning` | `doc/11-gdd.md` |
| `modes` | `game-design-planning` (GDD) + esta skill (training_features) | GDD + design contract |
| `stages` (camera_bounds, floor_y, hazard_policy) | `level-design-canonical` (cena) + `multi-plane-composition` (BG) | `level_blueprint.json` + design contract |
| `stages` (VRAM/DMA/scanline budget por arena) | `megadrive-vdp-budget-analyst` | `out/logs/vdp_budget_audit.json` |
| `balance.method` | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `balance.evidence_paths` | `sgdk-code-reviewer` (playtest logs) + humano | design contract |
| `audio` (BGM round, SFX hit, ambient arena) | `xgm2-audio-director` | design contract (referencia) |

## Producao de moveset frame data (fighting_moveset_frame_data)

| Campo | Skill delegada |
|---|---|
| `move_id`, `display_name`, `input_motion` | `game-design-planning` (GDD) |
| `category` | `systems-mechanics-validator` (classificacao) |
| `startup_frames`, `active_frames`, `recovery_frames` | `sgdk-runtime-coder` (FSM de animacao) |
| `on_hit_advantage_frames`, `on_block_advantage_frames` | `systems-mechanics-validator` (playtest) |
| `own_displacement_px`, `punish_window_frames` | `sgdk-runtime-coder` (playtest em ROM) |
| `hitbox_summary` | `character-design` + `sprite-animation` (sprite size) |
| `damage`, `stun_frames`, `meter_gain_on_hit/block` | `systems-mechanics-validator` (numeric table) |
| `is_projectile`, `is_invulnerable`, `is_armor` | `sgdk-runtime-coder` (FSM) |
| `cancel_into` | `sgdk-runtime-coder` (cancel rules) |

## Producao do validator (validate_fighting_specialization.ps1)

| Passo | Origem |
|---|---|
| Carrega 5 schemas | `tools/sgdk_wrapper/schemas/*.schema.json` |
| Le manifest | `doc/genre_specialization_manifest.json` |
| Le design contract | `doc/fighting_2d_design_contract.json` (path do manifest) |
| Audita moveset por personagem | `doc/characters/<id>/moveset_frame_data.json` |
| Determina fase | `doc/project_methodology_manifest.json::claim_ceiling` |
| Aplica 3 blockers phase-aware | registry-driven, gate apenas em ready_for_aaa/closeout |
| Emite report | `out/logs/fighting_specialization_report.json` |

## TDD canonico e o opt-in

`tdd-authoring` nao muda. A unica adicao eh:

- secao 12.1 no SKILL.md do tdd-authoring: "Anexo opt-in por especializacao"
- um campo opcional `tdd_annex_opt_in` no TDD, no formato:

```json
"tdd_annex_opt_in": {
  "specialization_id": "fighting_2d_traditional",
  "design_contract_path": "doc/fighting_2d_design_contract.json",
  "validator_report_path": "out/logs/fighting_specialization_report.json"
}
```

Nada mais. FSM, memory pool, ownership continuam 100% no TDD canonico.

## Inferencia zero

Esta skill NAO gera GDD, NAO escreve codigo C, NAO cria sprites, NAO roda emulador. Se voce precisa dessas coisas, va para as skills listadas. Orquestrar != absorver.
