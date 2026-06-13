# RPG Turn-Based JRPG Orchestrator Map

Quem faz o que. Este arquivo existe para que a skill orquestradora nao vire catch-all.

## Producao de design de superficie (rpg_turn_based_jrpg_design_contract)

| Secao | Skill delegada | Artefato de saida |
|---|---|---|
| `party` (id, role, class_id, lore_id) | `game-design-planning` (ja no GDD) | `doc/11-gdd.md` |
| `party.members[].party_frame_data_path` | esta skill (orquestra) | `doc/party/<id>/party_frame_data.json` |
| `lore.characters` | `game-design-planning` | `doc/11-gdd.md` |
| `lore.world` (summary, factions) | `game-design-planning` | `doc/11-gdd.md` |
| `modes` (kind, save_model) | `game-design-planning` (GDD) + esta skill (save_model) | GDD + design contract |
| `combat.turn_order` (formula, tiebreaker) | `systems-mechanics-validator` | design contract |
| `combat.action_menu` | `game-design-planning` | design contract |
| `combat.magic_system` (mp_resource, categories) | `systems-mechanics-validator` | design contract |
| `equipment.slots` (weapon, armor, etc) | `character-design` + `game-design-planning` | design contract |
| `equipment.item_categories` (sprite resolution) | `sprite-animation` | design contract (referencia) |
| `progression.xp_curve` | `systems-mechanics-validator` (numeric) | design contract + xp_table_path |
| `progression.skill_tree_policy` | `game-design-planning` | design contract |
| `party.members[].head_metric` (sprite scale) | `character-design` | design contract (advisory) |
| `combat` + `equipment` + `party` VRAM/DMA/scanline budget por cena | `megadrive-vdp-budget-analyst` | `out/logs/vdp_budget_audit.json` |
| `balance.method` | `systems-mechanics-validator` (5 Leis + 5 Pilares) | design contract |
| `balance.evidence_paths` | `sgdk-code-reviewer` (encounter logs) + humano | design contract |
| `audio` (BGM dungeon, SFX hit, ambient town) | `xgm2-audio-director` | design contract (referencia) |

## Producao de party frame data (rpg_party_frame_data)

| Campo | Skill delegada |
|---|---|
| `base_stats` (hp, mp, attack, defense, agility, magic) | `game-design-planning` (GDD) + `systems-mechanics-validator` (numeric) |
| `growth_curve` (per-level) | `systems-mechanics-validator` (stat curve) |
| `learned_abilities[].ability_id`, `display_name` | `game-design-planning` (GDD) |
| `learned_abilities[].category` | `systems-mechanics-validator` (classificacao) |
| `learned_abilities[].mp_cost`, `power` | `systems-mechanics-validator` (numeric) |
| `learned_abilities[].target_type` | `game-design-planning` (alvo) |
| `learned_abilities[].status_inflict` | `sgdk-runtime-coder` (status bitmask) |
| `learned_at_level` | `game-design-planning` (progression) |

## Producao do validator (validate_rpg_turn_based_jrpg_specialization.ps1)

| Passo | Origem |
|---|---|
| Carrega 4 schemas | `tools/sgdk_wrapper/schemas/*.schema.json` |
| Le manifest | `doc/genre_specialization_manifest.json` |
| Le design contract | `doc/rpg_turn_based_jrpg_design_contract.json` (path do manifest) |
| Audita party member | `doc/party/<id>/party_frame_data.json` |
| Determina fase | `doc/project_methodology_manifest.json::claim_ceiling` |
| Aplica 3 blockers phase-aware | registry-driven, gate apenas em ready_for_aaa/closeout |
| Emite report | `out/logs/rpg_specialization_report.json` |

## TDD canonico e o opt-in

`tdd-authoring` nao muda. A unica adicao eh:

- secao 12.1 no SKILL.md do tdd-authoring: "Anexo opt-in por especializacao"
- um campo opcional `tdd_annex_opt_in` no TDD, no formato:
  ```json
  {
    "specialization_id": "rpg_turn_based_jrpg",
    "design_contract_path": "doc/rpg_turn_based_jrpg_design_contract.json",
    "role": "delegate non-runtime concerns (party/lore/modes/combat/equipment/progression) to this contract; runtime/FSM/audio remain in TDD canonico"
  }
  ```

## Limites praticos do MD (referencia rapida)

- Party size 4 -> ate 4 sprites em battle + 4 status bars + 4 MP gauges
- Save SRAM 32KB -> 4-8 save slots max
- 16 magias distintas por membro (4 white + 4 black + 4 summon + 4 misc) eh o teto pratico
- Inventory 8-12 slots visiveis em uma unica tela
- Encounter rate "fixed+random" -> 60% random (10-30 steps), 40% fixed (pre-placed in dungeons)
