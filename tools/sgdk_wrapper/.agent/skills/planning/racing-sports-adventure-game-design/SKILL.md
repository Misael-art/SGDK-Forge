---
name: racing-sports-adventure-game-design
description: Use SOMENTE quando o projeto declarou opt-in por `racing_arcade` (ou `sports_action_direct` em Wave 4+ / `adventure_action_2d` em Wave 4+) em `doc/genre_specialization_manifest.json` E a secao de Racing/Sports/Adventure do GDD ja identifica vehicle catalog, track catalog, race modes, item catalog, AI profile, HUD, e balance. Esta skill NAO cria o GDD; ela orquestra `systems-mechanics-validator`, `character-design`, `sprite-animation`, `megadrive-vdp-budget-analyst`, `xgm2-audio-director`, `sgdk-runtime-coder` e `tdd-authoring` para produzir `racing_arcade_design_contract.json`, `racing_vehicle_frame_data.json` por veiculo e `racing_specialization_report.json`. Emite tambem o tdd_annex_opt_in opcional referenciado pelo TDD canonico. NAO use em projetos sem manifesto; nesse caso a pipeline generalista continua valendo. NAO infere ativacao por nome de pasta, palavras do codigo ou regex.
---

# Racing/Sports/Adventure Game Design (Orchestrator)

Orquestrador fino para `racing_arcade` (Wave 1), `sports_action_direct` (Wave 4+), `adventure_action_2d` (Wave 4+). Delega; nao duplica.

## Quando usar

- projeto opt-in por `racing_arcade` (ou `sports_action_direct`/`adventure_action_2d`) declarado em `doc/genre_specialization_manifest.json`
- GDD ja tem secao de Racing/Sports/Adventure com `vehicle_catalog`, `track_catalog`, `race_modes`, `item_catalog`, `ai_profile`, `hud_config`, `balance` apontando para o design de superficie (nao implementacao)
- TDD ja foi escrito (ou sera escrito em paralelo) e referencia o `racing_arcade_design_contract.json` por `path`

## Nao use

- projeto sem `doc/genre_specialization_manifest.json`. A generalista vale.
- para redigir GDD: use `game-design-planning` antes
- para TDD canonico: use `tdd-authoring` (consome este opt-in por `path` no `tdd_annex_opt_in`)
- para projetar mecanicas: use `systems-mechanics-validator` (5 Leis + 5 Pilares)
- para projetar veiculos visualmente: use `character-design` (sprite scale)
- para sprite sheet e animacao: use `sprite-animation`
- para runtime/FSM/scene state: use `sgdk-runtime-coder` + `scene-state-architect`
- para budget de cena: use `megadrive-vdp-budget-analyst`
- para audio: use `xgm2-audio-director`
- para QA/playtest: use `rom-mastering` e `sgdk-code-reviewer`

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/genre_specialization_registry.schema.json`
2. `tools/sgdk_wrapper/schemas/genre_specialization_manifest.schema.json`
3. `tools/sgdk_wrapper/schemas/racing_arcade_design_contract.schema.json`
4. `tools/sgdk_wrapper/schemas/racing_vehicle_frame_data.schema.json`
5. `tools/sgdk_wrapper/schemas/racing_specialization_report.schema.json`
6. `doc/07_game_design/genre_specialization_registry.json`
7. `doc/07_game_design/curation_sources/SOURCES_INDEX.md`
8. `references/racing_design_lexicon.md` (este diretorio)
9. `references/racing_orchestrator_map.md` (este diretorio)
10. `doc/11-gdd.md` (secao de Racing/Sports/Adventure)
11. `doc/technique_usage_manifest.json`

## Entrada minima

- `doc/genre_specialization_manifest.json` com `active_specializations[0].specialization_id == "racing_arcade"`
- GDD com secao de Racing (mes que rascunho)
- `doc/project_methodology_manifest.json` (para `claim_ceiling` -> fase)

## Saida minima

- `doc/racing_arcade_design_contract.json` (design de superficie; NAO implementacao)
- `doc/vehicles/<vehicle_id>/vehicle_frame_data.json` por veiculo
- `out/logs/racing_specialization_report.json` (via `validate_racing_arcade_specialization.ps1`)
- `tdd_annex_opt_in` opcional dentro do TDD canonico (apenas referencia por `path`)

## Secoes Obrigatorias do Contrato

| Secao | Origem | Funcao |
|---|---|---|
| `vehicle_catalog` | GDD | 4-12 veiculos (id, weight_class, `vehicle_frame_data_path`, starting_position, lore_id, head_metric advisory) |
| `track_catalog` | GDD | 4-16 tracks (track_id, length_pixels, lane_count, shortcut_count, weather_policy, recommended_lap_count, par_lap_time_frames, track_music_loop_seconds) |
| `race_modes` | GDD | kind (grand_prix/single_race/time_trial/battle/endurance/split_screen), laps, ai_count, item_box_enabled, rubber_banding_enabled |
| `item_catalog` | GDD | 0-8 items (rocket/shield/oil_slick/lightning/ghost/machine_gun/boost/trap), duration_frames, stack_max |
| `ai_profile` | GDD | difficulty_levels (3-5 levels), drafting_enabled, rubber_banding_enabled, rubber_band_strength_pct, ai_top_speed_variance_pct |
| `hud_config` | GDD | show_position/lap_counter/lap_time/minimap/speed_kmh/boost_meter/item_slot |
| `balance` | playtest | method + `evidence_paths`; `difficulty_curve_path` |

## Politicas fixas (nao negociaveis)

- `time_unit = "frames"` (sempre)
- `camera` ∈ {`behind`, `chase`, `behind_or_chase`}
- `track_count_max = 16` (constante)
- `lap_count_max = 5` (constante)
- `ai_opponents` ∈ {`3`, `5`, `5_to_7`, `7`}
- `boost_on_drift = "on"` (constante)
- `collision_model` ∈ {`arcade_forgiving`, `sim_fair`} (NAO `realistic_full`; MD-nao-viavel)
- Light/formula vehicles: drift_factor >= 30 (constraint allOf no schema)
- Heavy vehicles: drift_factor >= 10 (constraint allOf no schema)
- Phase-aware blockers disparam apenas em `ready_for_aaa`/`closeout`:
  - `racing_collision_model_audit`
  - `adventure_inventory_overflow` (sub-rule: item_catalog <= 5 items, max_stack <= 3)
  - `adventure_save_overflow` (sub-rule: track_count * 16 bytes <= 32KB SRAM)

## Inferencias proibidas

Esta skill NAO eh ativada por:
- nome de pasta, nome curto de projeto, extensao de arquivo
- regex em codigo (`if (lap_count > 0)`, `state = RACE_FINISHED`)
- keywords em GDD/TDD sem manifesto opt-in
- presence of `vehicle`, `track`, `lap` fields em GDD
- presence of `top_speed`, `ai_profile` tables

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

- AI opponents: 5-7 (sprite ceiling; max 8)
- Track count: 4-16 (acima exige save data)
- Lap count: 3-5 (acima eh muito longo)
- Items: 1-3 slots (4+ polui UI)
- HUD: position + lap + time + minimap
- Top speed: 256 km/h (u8 cap)
- Boost: 100% (u8 cap)
- SRAM: 32KB canonica (best lap + total time + ghost data = 16 bytes/track)
- VRAM: tilemap BG_A 32x32 (track tiles), sprites 8 carros + UI

## Subgeneros cobertos por esta skill

| Subgenero | Status v2 | Schema proprio |
|---|---|---|
| `racing_arcade` | active | `racing_arcade_design_contract.schema.json` |
| `sports_action_direct` | active | `sports_action_direct_design_contract.schema.json` (Wave 4+) |
| `adventure_action_2d` | active | `adventure_action_2d_design_contract.schema.json` (Wave 4+) |
| `racing_sim_hardcore` | future_architetural | nao |
| `sports_manager_data` | future_architetural | nao |

Ate Wave 4+, esta skill cobre apenas `racing_arcade` em `active` com biblia+schemas+validator+skill. Os outros 2 active entram progressivamente em Waves 2-4. Os 2 future_architetural NUNCA terao design contract.
