---
name: fighting-game-design
description: Use SOMENTE quando o projeto declarou opt-in por `fighting_2d_traditional` em `doc/genre_specialization_manifest.json` E a secao de luta do GDD ja identifica roster, modos e stances basicas. Esta skill NAO cria o GDD; ela orquestra `systems-mechanics-validator`, `character-design`, `sprite-animation`, `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst`, `xgm2-audio-director` e `tdd-authoring` para produzir `fighting_2d_design_contract.json`, `fighting_moveset_frame_data.json` por personagem e `fighting_specialization_report.json`. Emite tambem o tdd_annex_opt_in opcional referenciado pelo TDD canonico. NAO use em projetos sem manifesto; nesse caso a pipeline generalista continua valendo. NAO infere ativacao por nome de pasta, palavras do codigo ou regex.
---

# Fighting Game Design (Orchestrator)

Orquestrador fino. Delega; nao duplica.

## Quando usar

- projeto opt-in por `fighting_2d_traditional` declarado em `doc/genre_specialization_manifest.json`
- GDD ja tem secao de luta com `roster` e `modes` apontando para o design de superficie (nao implementacao)
- TDD ja foi escrito (ou sera escrito em paralelo) e referencia o `fighting_2d_design_contract.json` por `path`

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

Piso da cena viva (escola HAMOOPIG / Daniel Moura): `doc/03_art/18_live_scene_bar.md`
axiomas H1-H5. Lutador sem FSM, hitbox e frame data e fantasia. A engine
ja existe no workspace; nao reescrever luta ruim nem copiar roster dos
videos. Palco de luta tambem puxa Pyron/Chev/MX (Y1, C1-C4, M1-M4).

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/genre_specialization_registry.schema.json`
2. `tools/sgdk_wrapper/schemas/genre_specialization_manifest.schema.json`
3. `tools/sgdk_wrapper/schemas/fighting_2d_design_contract.schema.json`
4. `tools/sgdk_wrapper/schemas/fighting_moveset_frame_data.schema.json`
5. `tools/sgdk_wrapper/schemas/fighting_specialization_report.schema.json`
6. `doc/07_game_design/genre_specialization_registry.json`
7. `doc/07_game_design/curation_sources/SOURCES_INDEX.md`
8. `references/fighting_design_lexicon.md` (este diretorio)
9. `references/fighting_orchestrator_map.md` (este diretorio)
10. `doc/11-gdd.md` (secao de luta)
11. `doc/technique_usage_manifest.json`

## Entrada minima

- `doc/genre_specialization_manifest.json` com `active_specializations[0].specialization_id == "fighting_2d_traditional"`
- GDD com secao de luta (mes que rascunho)
- `doc/project_methodology_manifest.json` (para `claim_ceiling` -> fase)

## Saida minima

- `doc/fighting_2d_design_contract.json` (design de superficie; NAO implementacao)
- `doc/characters/<character_id>/moveset_frame_data.json` por personagem
- `out/logs/fighting_specialization_report.json` (via `validate_fighting_specialization.ps1`)
- `tdd_annex_opt_in` opcional dentro do TDD canonico (apenas referencia por `path`)

## Secoes Obrigatorias do Contrato

| Secao | Origem | Funcao |
|---|---|---|
| `roster` | GDD | tamanho, personagens, role, archetype, `moveset_frame_data_path`, `lore_id`, `head_metric` (advisory) |
| `lore.characters` | GDD | id, summary, `ip_status` (original/homage/public_domain/licensed) |
| `modes` | GDD | kind, opponent, round_config; `training_features` quando `kind=training` |
| `stages` | GDD | `camera_bounds_px`, `floor_y_px`, `hazard_policy` |
| `balance` | playtest | method + `evidence_paths`; `tier_targets` advisory |

## Politicas fixas (nao negociaveis)

- `time_unit = "frames"` (sempre)
- `head_metric_policy = "advisory"` (validator nunca bloqueia sozinho)
- `archetype_policy = "design_tool_not_law"`
- `balance_evidence_required = true`
- `rollback_netcode = "not_applicable"` (v1)
- Primary character: 5 frame fields obrigatorios em todo move nao-system/movement
- Phase-aware blockers disparam apenas em `ready_for_aaa`/`closeout`:
  - `fighting_training_mode_missing_for_product`
  - `fighting_lore_moveset_unbound`
  - `fighting_balance_evidence_missing`

## Inferencias proibidas

Esta skill NAO eh ativada por:
- nome de pasta, nome curto de projeto, extensao de arquivo
- regex em codigo (`if (x == y && buttons & ...)`, `state = ROUND_FIGHTING`)
- keywords em GDD/TDD sem manifesto opt-in
- matchup matrix, frame data table, hitbox viewer

Ativacao SOMENTE por `doc/genre_specialization_manifest.json` com `human_authorization` preenchido.

## Curadoria (fontes secundarias)

Biblias, livros, wikis e guias usados como base precisam:
- ter copia local em `doc/07_game_design/curation_sources/<sha256>_<descriptive>.txt`
- ser listados em `doc/07_game_design/curation_sources/SOURCES_INDEX.md` com `verification_status`
- `unverified_secondary_text` NAO pode virar `promotion_allowed=true`
- nenhum caminho absoluto externo pode aparecer em material ativo

## Promocao de especializacao (LABORATORIO -> ... -> MESTRE_*)

- v1 inicia em `LABORATORIO`
- `TEORICA_STANDARD` exige curadoria humana assinada em `SOURCES_INDEX.md`
- `TEORICA_PRIORITARIA` exige projeto com ROM, BlastEm evidence, doc/10-memory-bank.md
- `MESTRE_STANDARD` exige todas as 4 acima + validator report `ok` em closeout
- `MESTRE_PRIORITARIA` exige todos os 4 + comando canonico em 2+ projetos
- Sem promocao automatica. Toda promocao exige atualizacao de `doc/07_game_design/genre_specialization_registry.json` com evidencia rastreavel.

## Verificacao

```powershell
# canonical validator (top-level)
& tools/sgdk_wrapper/validate_fighting_specialization.ps1 -ProjectRoot <project>
```

Sucesso = `status=ok` em `out/logs/fighting_specialization_report.json`, todos os 5 schemas validados, todos os 3 blockers phase-aware `fired=false` (ou `phase=vertical_slice`).

## Passa quando

- `doc/genre_specialization_manifest.json` ativa `fighting_2d_traditional` com autorizacao humana rastreavel
- o GDD declara roster, modos, stances basicas e papel da especializacao sem substituir o pipeline generalista
- `doc/fighting_2d_design_contract.json` valida no schema e referencia frame data por personagem
- cada `moveset_frame_data.json` exigido pelo roster valida no schema
- `out/logs/fighting_specialization_report.json` existe e esta coerente com a fase do projeto
- blockers phase-aware ficam resolvidos ou declarados como nao aplicaveis para a fase atual

## Handoff

- `planning/tdd-authoring`: consumir o `tdd_annex_opt_in` por `path`, sem copiar regras da especializacao para o TDD
- `design/systems-mechanics-validator`: validar agency, feedback, flow, consistency e reward das mecanicas de combate
- `art/character-design` e `art/sprite-animation`: produzir model sheets, poses, timing e frame data visual
- `hardware/megadrive-vdp-budget-analyst`: auditar sprites por linha, SAT, VRAM, DMA e paletas
- `code/sgdk-runtime-coder` + `architecture/scene-state-architect`: implementar FSM, inputs, hit/hurt windows e teardown
- `code/xgm2-audio-director`: reservar canais, stingers e prioridades de SFX
- `operation/rom-mastering` e `code/sgdk-code-reviewer`: fechar build, BlastEm, validacao e revisao
