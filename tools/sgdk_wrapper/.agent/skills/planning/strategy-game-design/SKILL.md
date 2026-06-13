---
name: strategy-game-design
description: Use SOMENTE quando o projeto declarou opt-in por `strategy_tower_defense` (ou `strategy_tactical_turn_based` em Wave 2+) em `doc/genre_specialization_manifest.json` E a secao de Strategy do GDD ja identifica grid, torre/enemy catalog, wave composition, economy, modes e progression. Esta skill NAO cria o GDD; ela orquestra `systems-mechanics-validator`, `megadrive-vdp-budget-analyst`, `xgm2-audio-director`, `sgdk-runtime-coder` e `tdd-authoring` para produzir `strategy_tower_defense_design_contract.json`, `strategy_tower_frame_data.json` por torre e `strategy_specialization_report.json`. Emite tambem o tdd_annex_opt_in opcional referenciado pelo TDD canonico. NAO use em projetos sem manifesto; nesse caso a pipeline generalista continua valendo. NAO infere ativacao por nome de pasta, palavras do codigo ou regex.
---

# Strategy Game Design (Orchestrator)

Orquestrador fino para `strategy_tower_defense` (Wave 1) e `strategy_tactical_turn_based` (Wave 2). Delega; nao duplica.

## Quando usar

- projeto opt-in por `strategy_tower_defense` (ou `strategy_tactical_turn_based`) declarado em `doc/genre_specialization_manifest.json`
- GDD ja tem secao de Strategy com `grid_layout`, `tower_catalog`, `enemy_catalog`, `wave_composition`, `modes`, `economy`, `balance` apontando para o design de superficie (nao implementacao)
- TDD ja foi escrito (ou sera escrito em paralelo) e referencia o `strategy_tower_defense_design_contract.json` por `path`

## Nao use

- projeto sem `doc/genre_specialization_manifest.json`. A generalista vale.
- para redigir GDD: use `game-design-planning` antes
- para TDD canonico: use `tdd-authoring` (consome este opt-in por `path` no `tdd_annex_opt_in`)
- para projetar mecanicas: use `systems-mechanics-validator` (5 Leis + 5 Pilares)
- para grid/VDP budget/scanline pressure: use `megadrive-vdp-budget-analyst`
- para IA inimiga: use `sgdk-runtime-coder` (FSM de waves)
- para runtime/FSM/scene state: use `sgdk-runtime-coder` + `scene-state-architect`
- para audio: use `xgm2-audio-director`
- para QA/playtest: use `rom-mastering` e `sgdk-code-reviewer`

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/genre_specialization_registry.schema.json`
2. `tools/sgdk_wrapper/schemas/genre_specialization_manifest.schema.json`
3. `tools/sgdk_wrapper/schemas/strategy_tower_defense_design_contract.schema.json`
4. `tools/sgdk_wrapper/schemas/strategy_tower_frame_data.schema.json`
5. `tools/sgdk_wrapper/schemas/strategy_specialization_report.schema.json`
6. `doc/07_game_design/genre_specialization_registry.json`
7. `doc/07_game_design/curation_sources/SOURCES_INDEX.md`
8. `references/strategy_design_lexicon.md` (este diretorio)
9. `references/strategy_orchestrator_map.md` (este diretorio)
10. `doc/11-gdd.md` (secao de Strategy)
11. `doc/technique_usage_manifest.json`

## Entrada minima

- `doc/genre_specialization_manifest.json` com `active_specializations[0].specialization_id == "strategy_tower_defense"`
- GDD com secao de Strategy (mes que rascunho)
- `doc/project_methodology_manifest.json` (para `claim_ceiling` -> fase)

## Saida minima

- `doc/strategy_tower_defense_design_contract.json` (design de superficie; NAO implementacao)
- `doc/towers/<tower_id>/tower_frame_data.json` por torre
- `out/logs/strategy_specialization_report.json` (via `validate_strategy_tower_defense_specialization.ps1`)
- `tdd_annex_opt_in` opcional dentro do TDD canonico (apenas referencia por `path`)

## Secoes Obrigatorias do Contrato

| Secao | Origem | Funcao |
|---|---|---|
| `grid_layout` | GDD | width_tiles, height_tiles, path_tile_count, tower_slot_count, path_geometry, vram_budget_estimate_kb |
| `tower_catalog` | GDD | 3-8 torres (id, category, tier, base_cost, damage, range_tiles, fire_rate_frames, `tower_frame_data_path`, upgrade_paths) |
| `enemy_catalog` | GDD | 3-8 inimigos (id, archetype, hp, speed, resistance, gold_reward, special_ability) |
| `wave_composition` | GDD | wave_count, goal_lives, boss_wave_interval, waves[] (spawn_groups) |
| `modes` | GDD | kind (campaign/endless/challenge/puzzle_td/daily_seed), starting_resources, save_model |
| `economy` | GDD | starting_currency, kill_reward_multiplier, wave_clear_bonus, combo/perfect/speed bonuses |
| `balance` | playtest | method + `evidence_paths`; `dps_target_per_tower` advisory |

## Politicas fixas (nao negociaveis)

- `time_unit = "frames"` (sempre)
- `grid = "fixed_path"` (sempre; nao procedural)
- `lane_count = "1_to_3"` (default; pode estreitar para 1/2/3 por mapa)
- `tower_slots_max = 24` (constante)
- `wave_spawner = "scripted"` (sempre; RNG seeded com tabelas)
- `resource_currency` ∈ {`gold`, `energy`, `gold_and_energy`}
- `victory = "survive_N_waves"` (sempre)
- Phase-aware blockers disparam apenas em `ready_for_aaa`/`closeout`:
  - `strategy_grid_vram_overflow`
  - `strategy_unit_ap_unbounded` (no TD: cada torre com `fire_rate_frames >= 6`)
  - `strategy_fog_of_war_race` (wave_composition deve ter >=5 waves para VBlank-deterministic spawn)

## Inferencias proibidas

Esta skill NAO eh ativada por:
- nome de pasta, nome curto de projeto, extensao de arquivo
- regex em codigo (`wave_spawner`, `tier_id`)
- keywords em GDD/TDD sem manifesto opt-in
- presence of `tower`, `wave`, `grid` fields em GDD
- presence of balance DPS tables

Ativacao SOMENTE por `doc/genre_specialization_manifest.json` com `human_authorization` preenchido.

## Curadoria (fontes secundarias)

Biblias, livros, wikis e guias usados como base precisam:
- ter copia local em `doc/07_game_design/curation_sources/<sha256>_<descriptive>.txt`
- ser listados em `doc/07_game_design/curation_sources/SOURCES_INDEX.md` com `verification_status`
- `unverified_secondary_text` NAO pode virar `promotion_allowed=true`
- nenhum caminho absoluto externo pode aparecer em material ativo

## Promocao de especializacao (LABORATORIO -> ... -> MESTRE_*)

- v1 inicia em `LABORATORIO`
- `TEORICA_STANDARD` exige curadoria humana assinada em `SOURCES_INDEX.md` + matrix revisado
- `TEORICA_PRIORITARIA` exige 1 projeto com ROM validado em BlastEm + `doc/10-memory-bank.md` + validator `ok` em closeout
- `MESTRE_STANDARD` exige 1 projeto adicional (total 2) + 2+ design contracts distintos + validator `ok` em ambos
- `MESTRE_PRIORITARIA` exige curadoria humana explicita + matriz firmada em changelog do wrapper

Sem auto-promocao.

## Limites de Mega Drive (nao negociaveis)

- Wave count maximo: 30-50 (mais que isso exige save data grande)
- Tipos de torre: 4-8 (mais que isso polui a UI)
- Slots por mapa: 8-24 (mais que isso exige sub-menus)
- Inimigos na tela: 8-16 (sprite ceiling do VDP)
- Inimigos em wave: 20-50 (acima de 50 exige pool de objetos)
- Fire rate: minimo 6 frames entre ataques (CPU saturation)
- VRAM do grid: max 64KB (BG_A + BG_B + tiles de path)

## Subgeneros cobertos por esta skill

| Subgenero | Status v2 | Schema proprio |
|---|---|---|
| `strategy_tower_defense` | active | `strategy_tower_defense_design_contract.schema.json` |
| `strategy_tactical_turn_based` | active | `strategy_tactical_turn_based_design_contract.schema.json` (Wave 2) |
| `strategy_rts_compact` | future_knowledge | nao (Wave 3+) |
| `strategy_grand_strategy` | future_architetural | nao |
| `strategy_4x_turn_based` | future_architetural | nao |

Ate Wave 2+, esta skill cobre apenas `strategy_tower_defense` em `active`. Os outros
4 estao em `future_knowledge` ou `future_architetural` e so ganham design contract
via nova rodada de curadoria.
