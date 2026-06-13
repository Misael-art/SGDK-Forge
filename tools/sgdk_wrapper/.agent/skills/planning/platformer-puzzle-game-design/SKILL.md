---
name: platformer-puzzle-game-design
description: Use SOMENTE quando o projeto declarou opt-in por `platformer_precision_2d` (ou `metroidvania_ability_gated` em Wave 2+ / `puzzle_sokoban_grid` em Wave 3+ / `puzzle_tile_matching` em Wave 3+) em `doc/genre_specialization_manifest.json` E a secao de Platformer/Puzzle do GDD ja identifica player profile, level catalog, abilities, hazards, collectibles, modes e balance. Esta skill NAO cria o GDD; ela orquestra `systems-mechanics-validator`, `character-design`, `sprite-animation`, `megadrive-vdp-budget-analyst`, `xgm2-audio-director`, `sgdk-runtime-coder` e `tdd-authoring` para produzir `platformer_precision_2d_design_contract.json`, `platformer_level_segment_frame_data.json` por nivel e `platformer_specialization_report.json`. Emite tambem o tdd_annex_opt_in opcional referenciado pelo TDD canonico. NAO use em projetos sem manifesto; nesse caso a pipeline generalista continua valendo. NAO infere ativacao por nome de pasta, palavras do codigo ou regex.
---

# Platformer/Puzzle Game Design (Orchestrator)

Orquestrador fino para `platformer_precision_2d` (Wave 1), `metroidvania_ability_gated` (Wave 2+), `puzzle_sokoban_grid` (Wave 3+), `puzzle_tile_matching` (Wave 3+). Delega; nao duplica.

## Quando usar

- projeto opt-in por `platformer_precision_2d` (ou `metroidvania_ability_gated`/`puzzle_sokoban_grid`/`puzzle_tile_matching`) declarado em `doc/genre_specialization_manifest.json`
- GDD ja tem secao de Platformer/Puzzle com `player_profile`, `ability_set`, `hazard_catalog`, `collectible_catalog`, `level_catalog`, `modes`, `balance` apontando para o design de superficie (nao implementacao)
- TDD ja foi escrito (ou sera escrito em paralelo) e referencia o `platformer_precision_2d_design_contract.json` por `path`

## Nao use

- projeto sem `doc/genre_specialization_manifest.json`. A generalista vale.
- para redigir GDD: use `game-design-planning` antes
- para TDD canonico: use `tdd-authoring` (consome este opt-in por `path` no `tdd_annex_opt_in`)
- para projetar mecanicas: use `systems-mechanics-validator` (5 Leis + 5 Pilares)
- para projetar personagens visualmente: use `character-design`
- para sprite sheet e animacao: use `sprite-animation`
- para runtime/FSM/scene state: use `sgdk-runtime-coder` + `scene-state-architect`
- para budget de cena: use `megadrive-vdp-budget-analyst`
- para audio: use `xgm2-audio-director`
- para QA/playtest: use `rom-mastering` e `sgdk-code-reviewer`

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/genre_specialization_registry.schema.json`
2. `tools/sgdk_wrapper/schemas/genre_specialization_manifest.schema.json`
3. `tools/sgdk_wrapper/schemas/platformer_precision_2d_design_contract.schema.json`
4. `tools/sgdk_wrapper/schemas/platformer_level_segment_frame_data.schema.json`
5. `tools/sgdk_wrapper/schemas/platformer_specialization_report.schema.json`
6. `doc/07_game_design/genre_specialization_registry.json`
7. `doc/07_game_design/curation_sources/SOURCES_INDEX.md`
8. `references/platformer_design_lexicon.md` (este diretorio)
9. `references/platformer_orchestrator_map.md` (este diretorio)
10. `doc/11-gdd.md` (secao de Platformer/Puzzle)
11. `doc/technique_usage_manifest.json`

## Entrada minima

- `doc/genre_specialization_manifest.json` com `active_specializations[0].specialization_id == "platformer_precision_2d"`
- GDD com secao de Platformer (mes que rascunho)
- `doc/project_methodology_manifest.json` (para `claim_ceiling` -> fase)

## Saida minima

- `doc/platformer_precision_2d_design_contract.json` (design de superficie; NAO implementacao)
- `doc/levels/<level_id>/level_segment_frame_data.json` por nivel
- `out/logs/platformer_specialization_report.json` (via `validate_platformer_precision_2d_specialization.ps1`)
- `tdd_annex_opt_in` opcional dentro do TDD canonico (apenas referencia por `path`)

## Secoes Obrigatorias do Contrato

| Secao | Origem | Funcao |
|---|---|---|
| `player_profile` | GDD | run_speed, jump_velocity, gravity, coyote_time_frames, jump_buffer_frames, dash/wall_jump, voxel_size |
| `ability_set` | GDD | 1+ abilities (movement/combat/special/utility), frames_active, frames_cooldown, stamina_cost |
| `hazard_catalog` | GDD | 1+ hazards (spike/fire/water/pit/saw/moving/projectile), damage, respawn_pattern |
| `collectible_catalog` | GDD | 1+ collectibles (coin/gem/key/checkpoint_token/extra_life/secret), value, respawn_pattern |
| `level_catalog` | GDD | 5-100 levels (level_id, length_tiles, hazards_count, collectibles_count, `level_segment_frame_data_path`, par_time_seconds) |
| `modes` | GDD | kind (story/challenge/speedrun/practice/level_editor), lives_policy, score_policy |
| `balance` | playtest | method + `evidence_paths`; `difficulty_curve_path` |

## Politicas fixas (nao negociaveis)

- `time_unit = "frames"` (sempre)
- `camera = "side_scroll_with_lookahead"` (sempre)
- `run_speed_horizontal = "2x_player"` (constante)
- `jump_count` ∈ {`1`, `1_to_2`, `2`}
- `coyote_time = "on"` (constante)
- `death_loop = "on"` (constante)
- `level_length = "short_tight"` (constante)
- coyote_time_frames <= 6 (constraint phase-aware)
- jump_buffer_frames <= 6 (constraint phase-aware)
- Boss level: 2+ jump_arcs obrigatorios (constraint allOf no schema)
- Phase-aware blockers disparam apenas em `ready_for_aaa`/`closeout`:
  - `platformer_coyote_time_overflow`
  - `metroidvania_ability_unlock_path` (sub-rule: precision_2d abilities devem ter frames_active <= 30)
  - `puzzle_undo_count_unbounded` (sub-rule: precision_2d tem no undo; dormant)

## Inferencias proibidas

Esta skill NAO eh ativada por:
- nome de pasta, nome curto de projeto, extensao de arquivo
- regex em codigo (`if (coyote > 0)`, `state = JUMPING`)
- keywords em GDD/TDD sem manifesto opt-in
- presence of `jump`, `run`, `gravity` fields em GDD
- presence of `level_*`, `parallax_*` tables

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

- Player sprite: 16x16 (max 24x24)
- Run speed: 2-6 px/frame (max 6)
- Jump height: 3-6 tiles (acima exige gravity tuning)
- Coyote time: 4-6 frames (acima de 6 quebra desafio)
- Jump buffer: 4-6 frames (acima de 6 quebra desafio)
- Death restart: 30-60 frames (0.5-1s) de animacao
- Level count: 50-100 (acima exige save data > 32KB)
- Wall jump/dash: implementacao adicional; sem mudanca de frozen axes
- Save data: SRAM 32KB canonica (best time per level)
- VRAM por level: tilemap BG_A 32x32 (acima scroll)

## Subgeneros cobertos por esta skill

| Subgenero | Status v2 | Schema proprio |
|---|---|---|
| `platformer_precision_2d` | active | `platformer_precision_2d_design_contract.schema.json` |
| `metroidvania_ability_gated` | active | `metroidvania_ability_gated_design_contract.schema.json` (Wave 2+) |
| `puzzle_sokoban_grid` | active | `puzzle_sokoban_grid_design_contract.schema.json` (Wave 3+) |
| `puzzle_tile_matching` | active | `puzzle_tile_matching_design_contract.schema.json` (Wave 3+) |
| `puzzle_physics_2d` | future_knowledge | nao (MD-NAO-viavel borderline) |

Ate Wave 3+, esta skill cobre apenas `platformer_precision_2d` em `active` com biblia+schemas+validator+skill. Os outros 4 entram progressivamente.
