# Workflow: 5-Stage Production

Orquestra o pipeline completo de um jogo SGDK: GDD -> TDD -> Mecanicas -> Level -> Enemy -> Audio -> Scene Pipeline -> Runtime -> QA.

Esta workflow referencia:

- `pipelines/game_production_v1.json` (machine-readable)
- `pipelines/aaa_scene_v1.json` (sub-loop para cada cena)
- `workflows/production-loop.md` (loop principal)
- `workflows/project-opening.md` (classificacao inicial)
- `workflows/build-validate.md` (build + evidencia)

Regra: `aaa_scene_v1.json` continua sendo o pipeline de CENA. `game_production_v1.json` eh o pipeline de JOGO. Os dois coexistem.

---

## 0. Project Opening

- `workflows/project-opening.md` classifica:
  - `projeto_existente` - continua iteracao
  - `reseed` - preserva aprendizado, reabre base
  - `projeto_novo` - exige fundacao documental minima
- `workflows/route-decision-gate.md` quando rota tecnica ainda nao congelada
- Se for `projeto_novo` ou `reseed`, abrir `game-design-planning` para emitir seeds

## 1. GDD e Escopo

Skill: `skills/planning/game-design-planning`

Emite:
- `project_brief`
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `front_end_profile`
- `roteiro_scope`
- `mechanic_contract_seed` (NOVO)
- `level_blueprint_seed` (NOVO)
- `enemy_roster_seed` (NOVO)
- `tdd_contract_seed` (NOVO)
- `adaptive_music_state_seed` (NOVO)

Passa quando: GDD substancial, seeds minimos para proximas etapas.

## 2. TDD Tecnico

Skill: `skills/planning/tdd-authoring`

Emite:
- `tdd_contract.json` (machine-readable)
- `tdd_document.md` (narrativo)
- `state_fsm_map`
- `memory_pool_map`
- `runtime_ownership_map`

Bloqueios: `tdd_missing_for_product`, `scene_fsm_missing`, `memory_pool_missing`, `runtime_ownership_missing`, `input_contract_missing_for_product`, `region_timing_missing_for_product`.

Passa quando: FSM cobre todas as cenas, pools declarados, ownership unico, save_scope decidido, region declarada.

## 3. Systems/Mechanics Gate

Skill: `skills/design/systems-mechanics-validator`

Emite:
- `mechanic_validation_report.json` (status por mecanica + 5 leis + 5 pilares)
- `numeric_attribute_table.json`
- `mechanic_juice_map.json`

Bloqueios: `mechanic_contract_missing`, `mechanic_orphaned`, `mechanic_underused`, `mechanic_no_goal_link`, `mechanic_no_skill_expression`, `mechanic_input_ambiguous`, `mechanic_probability_undeclared`, `mechanic_feedback_missing`, `mechanic_test_scenario_missing`.

Passa quando: cada mecanica core tem versatility_cases >= 3, min_reuses >= 3, combination_map >= 1, 5 leis declaradas.

## 4. Level Design Gate

Skill: `skills/design/level-design-canonical`

Emite:
- `level_design_report.json`
- `golden_path_review`
- `phase_rhythm_review`
- `mechanic_reuse_review`
- opcional: `pattern_break_audit` (vs cena anterior)

Bloqueios: `level_blueprint_missing`, `golden_path_missing`, `phase_rhythm_missing`, `level_mechanic_reuse_missing`, `level_goal_path_unclear`, `level_risk_untelegraphed`.

Passa quando: golden_path visivel, ritmo calm/pressure/payoff, core mechanics reusadas, narrative ambiental.

## 5. Enemy Design Gate

Skill: `skills/design/enemy-design-canonical`

Emite:
- `enemy_design_report.json`
- `enemy_ai_role_map`
- `synergy_composition_map`
- `head_metric_audit`

Bloqueios: `enemy_roster_missing`, `enemy_role_missing`, `enemy_telegraph_missing`, `enemy_synergy_missing`, `enemy_level_function_missing`, `enemy_head_metric_invalid`.

Passa quando: cada inimigo tem role + head_metric + telegraph + synergy (ou `solo_tutorial`), boss=XL, head metric compliance 100%.

## 6. Audio/Adaptive Music Gate

Skill: `skills/code/xgm2-audio-director` (audio senior)
Skill: `skills/code/z80-pcm-custom-driver` (quando XGM2 nao cobre)

Emite:
- `audio_architecture_card.json` (saida senior)
- `adaptive_music_state_map.json` (NOVO, anexo do audio_architecture_card)
- `sfx_priority_matrix`
- `channel_ownership_report`

Estados minimos do adaptive_music_state_map: `exploration`, `stealth`, `suspicion`, `alert`, `boss`, `blackout`, `victory_or_release`.

Passa quando: cada estado tem trigger, transicoes declaradas, canais afetados, prioridade SFX, fallback.

## 7. AAA Scene Pipeline (Sub-Loop)

Pipeline: `pipelines/aaa_scene_v1.json`

Este sub-loop e executado por CENA. Para cada cena:

0. Escopo humano
0b. `art-direction-selector`
1. `art-asset-diagnostic`
1a. `art-creation-sourcing` (quando 3_no_art)
1b. `authoriality_gate`
2. `multi-plane-composition` (+ anexos `golden_path_seed`, `phase_rhythm_map`)
2b. `scene-direction-curator` (quando monumental)
3. `art-translation-to-vdp`
4. `visual-excellence-standards`
5. `megadrive-vdp-budget-analyst`
6. `sgdk-runtime-coder`
7. `validate_resources.ps1` + `freshness_audit.ps1`
8. BlastEm + `scene_closeout_gate.ps1` + `build-validate.md`

Nenhuma etapa pode ser pulada.

## 8. Runtime Integration

Skill: `skills/code/sgdk-runtime-coder`
Skill: `skills/architecture/scene-state-architect`
Skill: `skills/operation/sgdk-build-wrapper-operator`

Emite:
- `runtime_decision_log`
- `runtime_animation_timing_map` quando ha combate premium
- `api_reality_check` (citando header SGDK)
- build limpo
- ROM gerada

Regra: ROM nao pode estar em `ready_for_aaa` sem gate visual + gates de design.

## 9. QA, BlastEm, Freshness, Closeout

Ferramentas:
- `validate_resources.ps1` (consome 5 reports novos)
- `audit_effect_campaign_semantics.ps1`
- `audit_game_design_contracts.ps1` (NOVO)
- `freshness_audit.ps1`
- `scene_closeout_gate.ps1`
- BlastEm (obrigatorio)
- `workflows/build-validate.md`

Saidas:
- `validation_report.json` (com 5 novos status: `mechanics_ready`, `level_design_ready`, `enemy_design_ready`, `tdd_ready`, `game_production_ready`)
- `freshness_audit_report.json`
- `scene_closeout_gate_report.json`
- `emulator_session.json`
- `qa_emulator_report.json`
- changelog atualizado
- `doc/10-memory-bank.md` coerente

Regra de promocao:
- `ready_for_aaa=true` exige: `technical_ready`, `creative_ready`, `mechanics_ready`, `level_design_ready`, `enemy_design_ready`, `tdd_ready` (quando `product_status != technical_lab_validated`).
- Sem 5 reports de design, nao ha como calcular os 5 booleans.
- Sem BlastEm, gate de evidencia falha.
- Sem `visual_delivery_gate_report` limpo, gate visual bloqueia.

---

## Regras do Workflow

- nenhum passo pode ser pulado
- mecanica sem 5 leis nao pode virar codigo
- level sem golden path nao pode virar implementacao
- enemy sem telegraph nao pode virar sprite jogavel
- TDD ausente bloqueia `ready_for_aaa` (quando `product_status != lab`)
- audio sem adaptive state map nao fecha audio senior
- AAA scene pipeline e sub-loop obrigatorio
- runtime nao substitui gate visual
- BlastEm fecha gate de entrega
- 5 booleans de design precisam estar verdes para `ready_for_aaa`
- memoria operacional coerente eh obrigatoria

## Quando usar este workflow

- produto piloto, vertical slice, ready_for_aaa
- jogo completo, nao laboratorio isolado
- quando o escopo precisa passar por todos os 5 dominios (TDD, Mec, Level, Enemy, Audio)

## Quando NAO usar

- laboratorio tecnico isolado (use `production-loop.md` direto)
- cena visual sem gameplay (use `aaa-scene-pipeline.md` direto)
- prototipo de feature unica (use `production-loop.md`)
