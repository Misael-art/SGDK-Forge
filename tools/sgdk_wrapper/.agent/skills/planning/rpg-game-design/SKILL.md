---
name: rpg-game-design
description: Use SOMENTE quando o projeto declarou opt-in por `rpg_turn_based_jrpg` (ou `rpg_action_topdown` em Wave 2+) em `doc/genre_specialization_manifest.json` E a secao de RPG do GDD ja identifica party, lore, modos, combate, equipamento e progressao. Esta skill NAO cria o GDD; ela orquestra `systems-mechanics-validator`, `character-design`, `sprite-animation`, `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst`, `xgm2-audio-director` e `tdd-authoring` para produzir `rpg_turn_based_jrpg_design_contract.json`, `rpg_party_frame_data.json` por membro e `rpg_specialization_report.json`. Emite tambem o tdd_annex_opt_in opcional referenciado pelo TDD canonico. NAO use em projetos sem manifesto; nesse caso a pipeline generalista continua valendo. NAO infere ativacao por nome de pasta, palavras do codigo ou regex.
---

# RPG Game Design (Orchestrator)

Orquestrador fino para `rpg_turn_based_jrpg` (Wave 1) e `rpg_action_topdown` (Wave 2). Delega; nao duplica.

## Quando usar

- projeto opt-in por `rpg_turn_based_jrpg` (ou `rpg_action_topdown`) declarado em `doc/genre_specialization_manifest.json`
- GDD ja tem secao de RPG com `party`, `lore`, `modes`, `combat`, `equipment`, `progression` apontando para o design de superficie (nao implementacao)
- TDD ja foi escrito (ou sera escrito em paralelo) e referencia o `rpg_turn_based_jrpg_design_contract.json` por `path`

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
3. `tools/sgdk_wrapper/schemas/rpg_turn_based_jrpg_design_contract.schema.json`
4. `tools/sgdk_wrapper/schemas/rpg_party_frame_data.schema.json`
5. `tools/sgdk_wrapper/schemas/rpg_specialization_report.schema.json`
6. `doc/07_game_design/genre_specialization_registry.json`
7. `doc/07_game_design/curation_sources/SOURCES_INDEX.md`
8. `references/rpg_design_lexicon.md` (este diretorio)
9. `references/rpg_orchestrator_map.md` (este diretorio)
10. `doc/11-gdd.md` (secao de RPG)
11. `doc/technique_usage_manifest.json`

## Entrada minima

- `doc/genre_specialization_manifest.json` com `active_specializations[0].specialization_id == "rpg_turn_based_jrpg"`
- GDD com secao de RPG (mes que rascunho)
- `doc/project_methodology_manifest.json` (para `claim_ceiling` -> fase)

## Saida minima

- `doc/rpg_turn_based_jrpg_design_contract.json` (design de superficie; NAO implementacao)
- `doc/party/<member_id>/party_frame_data.json` por membro
- `out/logs/rpg_specialization_report.json` (via `validate_rpg_turn_based_jrpg_specialization.ps1`)
- `tdd_annex_opt_in` opcional dentro do TDD canonico (apenas referencia por `path`)

## Secoes Obrigatorias do Contrato

| Secao | Origem | Funcao |
|---|---|---|
| `party` | GDD | size (1-4), members (id, role, class_id, `party_frame_data_path`, `lore_id`, `head_metric` advisory) |
| `lore.characters` | GDD | id, summary, `ip_status` (original/homage/public_domain/licensed) |
| `lore.world` | GDD | summary, factions |
| `modes` | GDD | kind (main_story/side_quest/arena/etc), `save_model` |
| `combat` | GDD | turn_order, action_menu, magic_system, status_effects |
| `equipment` | GDD | slot_based=true, slots, item_categories |
| `progression` | GDD | xp_curve, level_cap, xp_table_path, skill_tree_policy |
| `balance` | playtest | method + `evidence_paths`; `tier_targets` advisory |

## Politicas fixas (nao negociaveis)

- `time_unit = "ticks (turn)"` (sempre)
- `party_size_max = 4` (constante; mudar exige nova rodada de curadoria)
- `equipment_grid = "slot_based"` (constante)
- `encounter_trigger = "fixed+random"` (combina encontros pre-definidos e aleatorios)
- `permadeath = "off"` (constante; JRPG canonico nao tem permadeath real)
- `narrative_branching = "linear_with_optional_scenes"` (default; pode ir a branching se justificado)
- Primary leader member: 3+ learned_abilities obrigatorias; non-leader: 1+ ability obrigatoria
- Phase-aware blockers disparam apenas em `ready_for_aaa`/`closeout`:
  - `rpg_party_size_unbounded`
  - `rpg_encounter_resolution_ambiguous`
  - `rpg_save_corruption_risk`

## Inferencias proibidas

Esta skill NAO eh ativada por:
- nome de pasta, nome curto de projeto, extensao de arquivo
- regex em codigo (`if (turn_count > 0)`, `state = COMBAT`)
- keywords em GDD/TDD sem manifesto opt-in
- presence of `xp`, `level`, `class` fields em GDD
- presence of stat curve tables

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

- Party size maximo: 4 (5+ quebra VRAM/scanline em cenas com 4-5 sprites)
- Magias distintas: 16-32 (32 eh o teto pratico)
- Inventario: 8-12 slots (16+ exige sub-telas que custam ciclos VBlank)
- Save: 8-32KB de save data (SRAM 32KB canonica do MD)
- 4-6 encontros visiveis simultaneos (sprite ceiling)
- 2-3 fases de boss (4+ causa pattern overflow)

## Subgeneros cobertos por esta skill

| Subgenero | Status v2 | Schema proprio |
|---|---|---|
| `rpg_turn_based_jrpg` | active | `rpg_turn_based_jrpg_design_contract.schema.json` |
| `rpg_action_topdown` | active | `rpg_action_topdown_design_contract.schema.json` (Wave 2) |
| `rpg_c_rpg_classic` | future_knowledge | nao (Wave 4+) |
| `rpg_narrative_dialogue` | future_knowledge | nao (Wave 4+) |

Ate Wave 2+, esta skill cobre apenas `rpg_turn_based_jrpg` em `active`. Os outros
4 estao em `future_knowledge` e so ganham design contract via nova rodada de
curadoria.
