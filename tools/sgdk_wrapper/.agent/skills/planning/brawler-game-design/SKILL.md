---
name: brawler-game-design
description: Use SOMENTE quando o projeto declarou opt-in por `brawler_belt_scroll` (ou `brawler_run_and_gun_2d` em Wave 2+ / `brawler_run_and_gun_topdown` em Wave 3+) em `doc/genre_specialization_manifest.json` E a secao de Brawler do GDD ja identifica player roster, enemy archetypes, pickup catalog, stage progression, modes e combat. Esta skill NAO cria o GDD; ela orquestra `systems-mechanics-validator`, `character-design`, `sprite-animation`, `megadrive-vdp-budget-analyst`, `xgm2-audio-director`, `sgdk-runtime-coder` e `tdd-authoring` para produzir `brawler_belt_scroll_design_contract.json`, `brawler_enemy_archetype_frame_data.json` por arquetipo e `brawler_specialization_report.json`. Emite tambem o tdd_annex_opt_in opcional. NAO use em projetos sem manifesto; nesse caso a pipeline generalista continua valendo. NAO infere ativacao por nome de pasta, palavras do codigo ou regex.
---

# Brawler Game Design (Orchestrator)

Orquestrador fino para `brawler_belt_scroll` (Wave 1), `brawler_run_and_gun_2d` (Wave 2+) e `brawler_run_and_gun_topdown` (Wave 3+). Delega; nao duplica.

## Quando usar

- projeto opt-in por `brawler_belt_scroll` (ou `brawler_run_and_gun_2d`/`brawler_run_and_gun_topdown`) declarado em `doc/genre_specialization_manifest.json`
- GDD ja tem secao de Brawler com `player_roster`, `enemy_archetypes`, `pickup_catalog`, `stages`, `modes`, `combat`, `balance` apontando para o design de superficie (nao implementacao)
- TDD ja foi escrito (ou sera escrito em paralelo) e referencia o `brawler_belt_scroll_design_contract.json` por `path`

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
3. `tools/sgdk_wrapper/schemas/brawler_belt_scroll_design_contract.schema.json`
4. `tools/sgdk_wrapper/schemas/brawler_enemy_archetype_frame_data.schema.json`
5. `tools/sgdk_wrapper/schemas/brawler_specialization_report.schema.json`
6. `doc/07_game_design/genre_specialization_registry.json`
7. `doc/07_game_design/curation_sources/SOURCES_INDEX.md`
8. `references/brawler_design_lexicon.md` (este diretorio)
9. `references/brawler_orchestrator_map.md` (este diretorio)
10. `doc/11-gdd.md` (secao de Brawler)
11. `doc/technique_usage_manifest.json`

## Entrada minima

- `doc/genre_specialization_manifest.json` com `active_specializations[0].specialization_id == "brawler_belt_scroll"`
- GDD com secao de Brawler (mes que rascunho)
- `doc/project_methodology_manifest.json` (para `claim_ceiling` -> fase)

## Saida minima

- `doc/brawler_belt_scroll_design_contract.json` (design de superficie; NAO implementacao)
- `doc/enemies/<archetype_id>/enemy_archetype_frame_data.json` por arquetipo
- `out/logs/brawler_specialization_report.json` (via `validate_brawler_belt_scroll_specialization.ps1`)
- `tdd_annex_opt_in` opcional dentro do TDD canonico (apenas referencia por `path`)

## Secoes Obrigatorias do Contrato

| Secao | Origem | Funcao |
|---|---|---|
| `player_roster` | GDD | id, role, archetype, starting_hp, iframe_frames, special_move_id, lore_id, head_metric (advisory) |
| `enemy_archetypes` | GDD | 4-8 arquetipos (grunt/heavy/thrower/runner/jumper/boss/mini_boss), `enemy_archetype_frame_data_path`, spawn_pattern |
| `pickup_catalog` | GDD | id, category (health/score/weapon/extra_life/special_bar_refill), drop_chance_pct, max_on_screen |
| `stages` | GDD | id, lane_count (1-3), wave_count, boss_archetype_id, boss_phases, hazard_policy, bg_music_loop_seconds |
| `modes` | GDD | kind (arcade/story/survival/boss_rush/versus_coop/time_attack), starting_lives, continue_policy |
| `combat` | GDD | move_set (3-6 moves), iframe_window_frames, grab_throw_enabled, super_bar_max, knockback_px, hit_stun_frames |
| `balance` | playtest | method + `evidence_paths`; `dps_target_per_player` advisory |

## Politicas fixas (nao negociaveis)

- `time_unit = "frames"` (sempre)
- `camera = "horizontal_lanes"` (sempre)
- `player_count = "1_to_2"` (default; pode estreitar para 1 ou 2)
- `enemy_count_on_screen_max = 8` (constante; frozen)
- `pickup_drop` ∈ {`health_and_score`, `health_and_score_and_weapon`, `health_and_score_and_extra_life`}
- `stage_progression = "linear_with_bosses"` (constante)
- `iframe_on_hit = "on"` (constante)
- Boss archetype: 2+ boss_phases obrigatorios (constraint allOf no schema)
- Primary player: iframe_frames >= 8 (constraint phase-aware)
- Phase-aware blockers disparam apenas em `ready_for_aaa`/`closeout`:
  - `brawler_iframe_window_unsafe`
  - `brawler_pickup_drop_unbounded`
  - `brawler_wave_spawner_deterministic`

## Inferencias proibidas

Esta skill NAO eh ativada por:
- nome de pasta, nome curto de projeto, extensao de arquivo
- regex em codigo (`if (iframe > 0)`, `state = WAVE_SPAWNING`)
- keywords em GDD/TDD sem manifesto opt-in
- presence of `boss`, `wave`, `pickup` fields em GDD
- presence of `drop_table`, `iframe_frames` tables

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

- Inimigos simultaneos na tela: max 8 (10+ causa sprite flicker no VDP)
- Player sprite: 16x16 ou 16x24 (per frame)
- Lane count: 1-3 (4+ lanes exige camera split)
- Stage count: 5-8 (acima exige save data)
- Boss phases: 1-3 (4+ sem telegraph fica ilegivel)
- Special moves: 1-2 por personagem (3+ polui o controle)
- Iframe: 8-60 frames (abaixo de 8 eh hit stacking; acima de 60 quebra ritmo)
- HP range: 50-500 (acima de 500 exige 4 digitos em display)

## Subgeneros cobertos por esta skill

| Subgenero | Status v2 | Schema proprio |
|---|---|---|
| `brawler_belt_scroll` | active | `brawler_belt_scroll_design_contract.schema.json` |
| `brawler_run_and_gun_2d` | active | `brawler_run_and_gun_2d_design_contract.schema.json` (Wave 2+) |
| `brawler_run_and_gun_topdown` | active | `brawler_run_and_gun_topdown_design_contract.schema.json` (Wave 3+) |

Ate Wave 2+, esta skill cobre apenas `brawler_belt_scroll` em `active`. Os outros
2 estao em `active` mas ainda sem design contract. Wave 1+ entrega progressivamente.
