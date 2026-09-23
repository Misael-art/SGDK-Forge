# PATCH PENDENTE: tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md

> **Status**: worktree sujo preexistente (HEAD = 223 linhas; working = 327 linhas).  
> **Origem**: Game Systems Pipeline Hardening (2026-06-01).  
> **Acao humana necessaria**: revisar `git diff` no arquivo e aplicar este patch quando o worktree for limpo.  
> **Aplicar apos**: resolver os 39+ linhas de diff ja presentes em SGDK_GLOBAL.md (sem relacao com este patch).

---

## Patch: adicionar secao 1.0.2 Chain de Producao canonico

Inserir imediatamente apos a secao 1.0.1 (Context Pack antes de geracao), antes da secao 1.1 (Prioridade arquitetural para cenas AAA compostas).

```markdown
### 1.0.2 Chain de Producao canonico (GDD -> TDD -> Mec -> Level -> Enemy -> Audio -> Art -> Runtime -> QA)

- Quando o alvo for `vertical_slice_candidate`, `ready_for_aaa`, `product_mastering` ou `product_release`, a producao segue o Chain canonico materializado em `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json` (e referenciado por `workflows/5-stage-production.md`).
- A ordem obrigatoria eh: S1 GDD scope -> S2 TDD -> S3 Mecanica -> S4 Level -> S5 Enemy -> S6 Audio adaptativo -> S7 cena (reaproveita `pipelines/aaa_scene_v1.json`) -> S8 Runtime -> S9 QA/Product closeout.
- Nenhuma etapa do Chain pode ser pulada. Em especial:
  - TDD nasce ANTES de codigo C (`sgdk-runtime-coder` nao pode improvisar ownership).
  - Mecanica core precisa de `versatility_cases >= 3`, `min_reuses >= 3`, `combination_map >= 1` (validado por `tools/sgdk_wrapper/audit_game_design_contracts.ps1`).
  - Toda mecanica core precisa aparecer em `level_blueprint.mechanic_reuse_map`.
  - Toda entrada de `enemy_roster` precisa de role, telegraph_model com `telegraph_frames >= 1`, synergy_partners (exceto `solo_tutorial` e `boss`) e head_metric compativel (boss exige XL).
- A promocao a `ready_for_aaa` exige `audit_game_design_contracts_report.json` com `status=passed`.
- Lab (`technical_lab_validated`) nao exige o Chain completo; so precisa provar que o componente tecnico existe.
- As skills que materializam o Chain sao:
  - `planning/tdd-authoring`
  - `design/systems-mechanics-validator`
  - `design/level-design-canonical`
  - `design/enemy-design-canonical`
  - `code/xgm2-audio-director` (anexo adaptive music)
- A cross-validation entre os 4 contratos (`mechanic_contract.json`, `level_blueprint.json`, `enemy_roster.json`, `tdd_contract.json`) e os catalogos canonicos (`enemy_ai_role_catalog.json`, `mechanic_role_catalog.json`, `head_metric_reference.json`) eh executada por `tools/sgdk_wrapper/audit_game_design_contracts.ps1`.
- Os 18 codigos de blocker separados em `blocking_statuses` (tecnico) e `creative_blocking_statuses` (criativo) estao documentados no schema `tools/sgdk_wrapper/schemas/game_production_gate_report.schema.json`.

```

---

## Diff esperado (formato unidiff simplificado)

```diff
@@ -24,6 +24,7 @@
 - Nao solicite nem exponha Chain of Thought; use `route_decision_record`, `art_generation_brief`, `master_style_manifest`, `qa_findings` e `correction_request`.

+### 1.0.2 Chain de Producao canonico (GDD -> TDD -> Mec -> Level -> Enemy -> Audio -> Art -> Runtime -> QA)
+
+- Quando o alvo for `vertical_slice_candidate`, `ready_for_aaa`, `product_mastering` ou `product_release`, a producao segue o Chain canonico materializado em `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json` (e referenciado por `workflows/5-stage-production.md`).
+- A ordem obrigatoria eh: S1 GDD scope -> S2 TDD -> S3 Mecanica -> S4 Level -> S5 Enemy -> S6 Audio adaptativo -> S7 cena (reaproveita `pipelines/aaa_scene_v1.json`) -> S8 Runtime -> S9 QA/Product closeout.
+- Nenhuma etapa do Chain pode ser pulada. Em especial:
+  - TDD nasce ANTES de codigo C (`sgdk-runtime-coder` nao pode improvisar ownership).
+  - Mecanica core precisa de `versatility_cases >= 3`, `min_reuses >= 3`, `combination_map >= 1` (validado por `tools/sgdk_wrapper/audit_game_design_contracts.ps1`).
+  - Toda mecanica core precisa aparecer em `level_blueprint.mechanic_reuse_map`.
+  - Toda entrada de `enemy_roster` precisa de role, telegraph_model com `telegraph_frames >= 1`, synergy_partners (exceto `solo_tutorial` e `boss`) e head_metric compativel (boss exige XL).
+- A promocao a `ready_for_aaa` exige `audit_game_design_contracts_report.json` com `status=passed`.
+- Lab (`technical_lab_validated`) nao exige o Chain completo; so precisa provar que o componente tecnico existe.
+- As skills que materializam o Chain sao:
+  - `planning/tdd-authoring`
+  - `design/systems-mechanics-validator`
+  - `design/level-design-canonical`
+  - `design/enemy-design-canonical`
+  - `code/xgm2-audio-director` (anexo adaptive music)
+- A cross-validation entre os 4 contratos (`mechanic_contract.json`, `level_blueprint.json`, `enemy_roster.json`, `tdd_contract.json`) e os catalogos canonicos (`enemy_ai_role_catalog.json`, `mechanic_role_catalog.json`, `head_metric_reference.json`) eh executada por `tools/sgdk_wrapper/audit_game_design_contracts.ps1`.
+- Os 18 codigos de blocker separados em `blocking_statuses` (tecnico) e `creative_blocking_statuses` (criativo) estao documentados no schema `tools/sgdk_wrapper/schemas/game_production_gate_report.schema.json`.
+
 ## 1.1 Prioridade arquitetural para cenas AAA compostas
```

---

## Validacao esperada apos aplicacao

- `python -m json.tool tools/sgdk_wrapper/.agent/framework_manifest.json` continua OK.
- `pwsh -File tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1` continua com 19/19 PASS.
- `python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py` (se existir) continua OK.
- Nenhum header SGDK eh violado (este patch so adiciona uma secao em markdown, sem codigo C).
