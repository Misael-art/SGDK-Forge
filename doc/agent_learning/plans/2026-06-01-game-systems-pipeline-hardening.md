# Game Systems Pipeline Hardening Plan

Data: 2026-06-01
Status: validado, em execucao
Workspace: `F:\Projects\MegaDrive_DEV`

## Goal

Transformar o agente canonico de "pipeline de cena/arte/ROM" em pipeline de jogo completo, com mecanicas, fases, inimigos, TDD e musica adaptativa auditaveis.

## Architecture

- Criar contratos e gates novos sem inflar o `aaa_scene_v1.json`.
- O novo `game_production_v1.json` orquestra GDD -> TDD -> Mecanicas -> Level -> Enemy -> Audio -> Scene Pipeline -> QA.
- `aaa_scene_v1.json` permanece intocado e e referenciado como sub-loop.
- Pattern de pastas: `skills/design/` (consolidado por dominio) para 3 skills; `skills/planning/tdd-authoring` segue o pattern existente.

## Stack

PowerShell validators, JSON Schema draft-07, Markdown skills/workflows, SGDK wrapper, existing `.agent` framework.

## Regras de Execucao

- Nao usar `git reset`, `git checkout`, `git restore`, `git clean`, deletes destrutivos ou moves sem manifest.
- Nao fazer stage/commit. Usar `apply_patch` para edicoes.
- Antes de editar arquivo central (`SGDK_GLOBAL.md`, `doc/06_AI_MEMORY_BANK.md`, `validate_resources.ps1`), executar `git diff -- <arquivo>`:
  - Se limpo ou modificacao trivial sem conflito -> editar direto
  - Se modificacao preexistente nao-trivial -> patch em `doc/agent_learning/pending_integration/` e parar a tarefa
- Registrar no relatorio final cada arquivo que foi para `pending_integration/` com motivo.
- Nao implementar gameplay/runtime. Nao criar devlog, Tiled bridge, localization, world map, options/remap, pseudo-3D.

## Decisoes Criticas Fechadas

1. `framework_manifest.json` path corrigido para `tools/sgdk_wrapper/.agent/framework_manifest.json`.
2. `doc/agent_learning/plans/` criado nesta rodada.
3. `audit_game_design_contracts.ps1` recebe spec minima: cross-validation de contratos + checagem de catalogos + exit codes 0/1/2 + report JSON.
4. 18 blockers separados em `blocking_statuses` (tecnico) vs `creative_blocking_statuses` (criativo), com guarda por `product_status`.
5. Worktree sujo: patch + `pending_integration/` para arquivos com modificacao preexistente.

## Arquivos a Criar

### Schemas (10)

- `tools/sgdk_wrapper/schemas/mechanic_contract.schema.json`
- `tools/sgdk_wrapper/schemas/mechanic_validation_report.schema.json`
- `tools/sgdk_wrapper/schemas/level_blueprint.schema.json`
- `tools/sgdk_wrapper/schemas/level_design_report.schema.json`
- `tools/sgdk_wrapper/schemas/enemy_roster.schema.json`
- `tools/sgdk_wrapper/schemas/enemy_design_report.schema.json`
- `tools/sgdk_wrapper/schemas/tdd_contract.schema.json`
- `tools/sgdk_wrapper/schemas/game_production_gate_report.schema.json`
- `tools/sgdk_wrapper/schemas/moodboard_manifest.schema.json`
- `tools/sgdk_wrapper/schemas/adaptive_music_state_map.schema.json`

### Catalogos Auxiliares (3)

- `tools/sgdk_wrapper/.agent/references/enemy_ai_role_catalog.json`
- `tools/sgdk_wrapper/.agent/references/mechanic_role_catalog.json`
- `tools/sgdk_wrapper/.agent/references/head_metric_reference.json`

### Skills (4)

- `tools/sgdk_wrapper/.agent/skills/design/systems-mechanics-validator/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/design/level-design-canonical/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/design/enemy-design-canonical/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/planning/tdd-authoring/SKILL.md`

### Workflows e Pipeline (2)

- `tools/sgdk_wrapper/.agent/workflows/5-stage-production.md`
- `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json`

### Scripts e Testes (2)

- `tools/sgdk_wrapper/audit_game_design_contracts.ps1`
- `tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1`

### Relatorios e Plano (2)

- `doc/agent_learning/plans/2026-06-01-game-systems-pipeline-hardening.md` (este arquivo)
- `doc/agent_learning/game_systems_pipeline_hardening_report.md` (apos execucao)

## Arquivos a Modificar (com classificacao de risco)

### Risco ALTO -> pending_integration/

- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` (worktree sujo preexistente)
- `doc/06_AI_MEMORY_BANK.md` (worktree sujo preexistente)
- `tools/sgdk_wrapper/validate_resources.ps1` (5470 linhas, modificado em 2 rodadas previas)

### Risco MEDIO -> git diff + editar se limpo

- `tools/sgdk_wrapper/.agent/framework_manifest.json` (path corrigido)
- `tools/sgdk_wrapper/.agent/workflows/production-loop.md`

### Risco BAIXO -> edicao isolada direta

- `tools/sgdk_wrapper/.agent/agents/game-director-sgdk.md`
- `tools/sgdk_wrapper/.agent/agents/project-planner-sgdk.md`
- `tools/sgdk_wrapper/.agent/skills/planning/game-design-planning/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/art/art-direction-selector/SKILL.md`
- `tools/sgdk_wrapper/.agent/skills/code/xgm2-audio-director/SKILL.md`

## Contratos Obrigatorios

### mechanic_contract

Obrigatorios: `mechanic_id`, `mechanic_role`, `player_action`, `system_rule`, `goal_link`, `input_binding`, `activation_context`, `space_requirements`, `required_game_elements`, `skill_challenge_type`, `rules_and_limits`, `probability_model`, `versatility_cases`, `level_design_reuse_plan`, `combination_map`, `failure_states`, `feedback_model`, `tutorial_invisible_plan`, `test_scenarios`, `evidence_required`, `mechanic_5_laws_compliance`.

Regras:
- `core` exige `versatility_cases >= 3`.
- `core` exige `level_design_reuse_plan.min_reuses >= 3`.
- `core` exige pelo menos uma entrada em `combination_map`.
- `utility` pode ter `skill_challenge_type=none_utility`.
- `probability_model.type != deterministic` exige `success_rate_percent`.
- `input_binding` nao pode reutilizar o mesmo botao para acoes distintas sem `activation_context.disambiguation_rule`.

### level_blueprint

Obrigatorios: `scope_id`, `golden_path`, `waypoints`, `gates`, `optional_routes`, `risk_markers`, `breathing_zones`, `phase_rhythm_map`, `mechanic_reuse_map`, `tutorial_invisible_beats`, `environmental_narrative_map`, `failure_recovery_model`, `acceptance_tests`.

Regras:
- Toda fase jogavel precisa de `golden_path`.
- Toda mecanica core precisa aparecer em `mechanic_reuse_map`.
- `phase_rhythm_map` precisa conter ao menos `calm`, `pressure`, `payoff` ou justificar `not_applicable`.

### enemy_roster

Obrigatorios por inimigo: `enemy_id`, `role`, `head_metric`, `hp`, `damage`, `movement_model`, `ai_behavior`, `telegraph_model`, `weakness_model`, `synergy_partners`, `level_placement_rules`, `feedback_on_hit`, `feedback_on_alert`.

Roles: `patrulheiro`, `perseguidor`, `atirador`, `guarda`, `voador`, `bloqueador`, `tecnico_suporte`, `boss`.

Regras:
- Todo inimigo precisa de funcao tatica.
- Todo inimigo de combate precisa de `telegraph_model`.
- `boss` precisa de pelo menos 3 estados ou justificar `boss_curto`.
- `synergy_partners` vazio so passa se `role` for `solo_tutorial` (nao usado, mas regra preservada).
- `role=boss` E `head_metric != XL` -> `enemy_head_metric_invalid`.
- `role != boss` E `head_metric == XL` -> `enemy_head_metric_invalid`.

### tdd_contract

Obrigatorios: `scene_manager_scope`, `input_abstraction_scope`, `state_fsm_map`, `memory_pool_map`, `vblank_dma_ownership`, `h_int_ownership`, `audio_ownership`, `save_scope`, `region_timing_scope`, `rom_mastering_scope`, `risk_mitigation_table`.

Regras:
- Produto piloto ou `ready_for_aaa` exige TDD.
- `save_scope=required` exige `sram_magic`, `sram_version`, `sram_checksum`.
- `region_timing_scope` precisa declarar NTSC/PAL ou `not_applicable` com justificativa.

## Skills Novas (contrato operacional)

### systems-mechanics-validator

Entrada: `doc/11-gdd.md`, `doc/13-spec-cenas.md`, `mechanic_contract.json`, player kit, target scene/scope.
Saida: `mechanic_validation_report.json`, `numeric_attribute_table.json`, `mechanic_juice_map.json`.
Bloqueios: `mechanic_contract_missing`, `mechanic_orphaned`, `mechanic_underused`, `mechanic_no_goal_link`, `mechanic_no_skill_expression`, `mechanic_input_ambiguous`, `mechanic_probability_undeclared`, `mechanic_feedback_missing`, `mechanic_test_scenario_missing`.

### level-design-canonical

Entrada: `scene_roadmap`, `mechanic_validation_report.json`, `level_blueprint.json`, GDD/spec.
Saida: `level_design_report.json`, `golden_path_review`, `phase_rhythm_review`, `mechanic_reuse_review`.
Bloqueios: `level_blueprint_missing`, `golden_path_missing`, `phase_rhythm_missing`, `level_mechanic_reuse_missing`, `level_goal_path_unclear`, `level_risk_untelegraphed`.

### enemy-design-canonical

Entrada: `enemy_roster.json`, `level_blueprint.json`, player kit, scene spec.
Saida: `enemy_design_report.json`, `enemy_ai_role_map`, `synergy_composition_map`, `head_metric_audit`.
Bloqueios: `enemy_roster_missing`, `enemy_role_missing`, `enemy_telegraph_missing`, `enemy_synergy_missing`, `enemy_level_function_missing`, `enemy_head_metric_invalid`.

### tdd-authoring

Entrada: GDD, spec de cenas, route decision, runtime target.
Saida: `tdd_contract.json`, `tdd_document.md`, `state_fsm_map`, `memory_pool_map`, `runtime_ownership_map`.
Bloqueios: `tdd_missing_for_product`, `scene_fsm_missing`, `memory_pool_missing`, `runtime_ownership_missing`, `input_contract_missing_for_product`, `region_timing_missing_for_product`.

## Workflow 5-stage-production.md (etapas)

0. Project opening
1. GDD e escopo
2. TDD tecnico
3. Systems/mechanics gate
4. Level design gate
5. Enemy design gate
6. Audio/adaptive music gate
7. AAA scene pipeline como sub-loop
8. Runtime integration
9. QA, BlastEm, freshness, closeout

## Pipeline game_production_v1.json (steps)

- S0_project_opening
- S1_gdd_scope
- S2_tdd_authoring
- S3_mechanics_validation
- S4_level_design
- S5_enemy_design
- S6_audio_adaptive_state
- S7_scene_pipeline_call (referencia `aaa_scene_v1.json`)
- S8_runtime_product_integration
- S9_product_validation_closeout

## Validacao Final

- `python -m json.tool` em todos os 10 schemas + 3 catalogos + pipeline
- Execucao de `audit_game_design_contracts.ps1` em fixture completa
- `test_game_design_contract_gates.ps1` deve passar 11 casos
- Testes pre-existentes nao regrediram: visual_gate, semantic_audit, lab_category, blocking_status_codes
- Validadores Python: `validate_skill_framework.py`, `self_check_agentic_aaa_contracts.py`, `check_route_decision_contract.py`
- `git diff --check` limitado aos arquivos tocados

## Definition of Done

- [ ] 10 schemas + 3 catalogos existem e passam `python -m json.tool`
- [ ] 4 skills existem e estao no framework_manifest.json
- [ ] workflow 5-stage-production.md existe
- [ ] pipeline game_production_v1.json existe, referencia aaa_scene_v1.json, passa json.tool
- [ ] audit_game_design_contracts.ps1 existe com spec
- [ ] test_game_design_contract_gates.ps1 passa 11 casos
- [ ] validate_resources.ps1 consome os 5 reports e emite os 5 status (ou patch em pending_integration)
- [ ] Blockers separados em blocking_statuses vs creative_blocking_statuses
- [ ] 4 booleans novos (mechanics_ready, level_design_ready, enemy_design_ready, tdd_ready) participam de readyForAaaBeforeClaimCeiling
- [ ] framework_manifest.json referencia as 4 skills, o workflow e o pipeline novos
- [ ] Skills existentes atualizadas: game-design-planning, art-direction-selector, xgm2-audio-director, game-director-sgdk, project-planner-sgdk
- [ ] git diff executado para cada arquivo central; conflitos viraram patch em pending_integration
- [ ] Nenhum runtime, ROM ou asset foi alterado
- [ ] Nenhum TODO, TBD ou trailing whitespace
- [ ] Relatorio final em `doc/agent_learning/game_systems_pipeline_hardening_report.md`

## Confirmacao Canonica Final

> O agente canonico agora nao pode promover jogo completo apenas por arte, build, BlastEm ou visual gate. Produto jogavel exige mecanica validada, level blueprint, enemy roster, TDD e evidencia de producao compativel com product_status/scope_id/claim_ceiling.
