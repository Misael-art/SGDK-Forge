# PATCH PENDENTE: doc/06_AI_MEMORY_BANK.md

> **Status**: worktree sujo preexistente (HEAD = 232 linhas; working = 671 linhas).  
> **Origem**: Game Systems Pipeline Hardening (2026-06-01).  
> **Acao humana necessaria**: revisar `git diff` no arquivo e aplicar este patch quando o worktree for limpo.  
> **Aplicar apos**: resolver os 439+ linhas de diff ja presentes em doc/06_AI_MEMORY_BANK.md (sem relacao com este patch).

---

## Patch: adicionar bloco "5.b Chain de Producao canonico" no estado atual

Inserir na secao 5 (estados de pipelines) ou criar nova sub-secao dedicada. A insercao deve preservar o formato narrativo/operacional do documento existente.

```markdown
### 5.b Chain de Producao canonico (GDD -> TDD -> Mec -> Level -> Enemy -> Audio -> Art -> Runtime -> QA)

A partir de 2026-06-01, o workspace adiciona 10 schemas, 3 catalogos, 4 skills, 1 workflow, 1 pipeline machine-readable e 1 auditor cross-references para o Chain de Producao canonico. As skills vivem em `tools/sgdk_wrapper/.agent/skills/design/` e `tools/sgdk_wrapper/.agent/skills/planning/tdd-authoring/`. O pipeline machine-readable vive em `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json`. O auditor vive em `tools/sgdk_wrapper/audit_game_design_contracts.ps1`. O teste de gate vive em `tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1` (19/19 PASS).

Os 4 contratos novos sao:

- `mechanic_contract.json` (5 Leis Fundamentais: Agency, Feedback, Flow, Consistency, Reward; 5 Pilares)
- `level_blueprint.json` (golden path + phase rhythm + reuse_map)
- `enemy_roster.json` (6 roles + 2 extras + head_metric)
- `tdd_contract.json` (state_fsm_map + memory_pool_map + vblank_dma_ownership + region/timing + ROM mastering)

Os 18 codigos de blocker separados em `blocking_statuses` (tecnico, 10 itens) e `creative_blocking_statuses` (criativo, 8+ itens) estao documentados em `tools/sgdk_wrapper/schemas/game_production_gate_report.schema.json`.

A promocao a `ready_for_aaa`, `product_mastering` ou `product_release` exige `audit_game_design_contracts_report.json` com `status=passed`. Lab (`technical_lab_validated`) nao exige o Chain completo.

Os 2 anexos para skills preexistentes sao:

- `moodboard_manifest.schema.json` (anexo de `art-direction-selector`)
- `adaptive_music_state_map.schema.json` (anexo de `xgm2-audio-director`)

Nenhuma das mudancas altera o wrapper de build (`tools/sgdk_wrapper/build.bat`, `build_inner.bat`, `clean.bat`, `run.bat`, `env.bat`). Nenhuma copia ou fork de arquivo foi criado. A canonicalizacao do Chain foi feita in-place no diretorio `.agent/`, preservando o principio de correcao in-place do `doc/AGENTS.md`.

```

---

## Diff esperado (formato unidiff simplificado)

```diff
@@ -XX,YY +XX,YY @@
 ### 5.a Algum bloco preexistente ja registrado
 
+### 5.b Chain de Producao canonico (GDD -> TDD -> Mec -> Level -> Enemy -> Audio -> Art -> Runtime -> QA)
+
+A partir de 2026-06-01, o workspace adiciona 10 schemas, 3 catalogos, 4 skills, 1 workflow, 1 pipeline machine-readable e 1 auditor cross-references para o Chain de Producao canonico. As skills vivem em `tools/sgdk_wrapper/.agent/skills/design/` e `tools/sgdk_wrapper/.agent/skills/planning/tdd-authoring/`. O pipeline machine-readable vive em `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json`. O auditor vive em `tools/sgdk_wrapper/audit_game_design_contracts.ps1`. O teste de gate vive em `tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1` (19/19 PASS).
+
+Os 4 contratos novos sao:
+
+- `mechanic_contract.json` (5 Leis Fundamentais: Agency, Feedback, Flow, Consistency, Reward; 5 Pilares)
+- `level_blueprint.json` (golden path + phase rhythm + reuse_map)
+- `enemy_roster.json` (6 roles + 2 extras + head_metric)
+- `tdd_contract.json` (state_fsm_map + memory_pool_map + vblank_dma_ownership + region/timing + ROM mastering)
+
+Os 18 codigos de blocker separados em `blocking_statuses` (tecnico, 10 itens) e `creative_blocking_statuses` (criativo, 8+ itens) estao documentados em `tools/sgdk_wrapper/schemas/game_production_gate_report.schema.json`.
+
+A promocao a `ready_for_aaa`, `product_mastering` ou `product_release` exige `audit_game_design_contracts_report.json` com `status=passed`. Lab (`technical_lab_validated`) nao exige o Chain completo.
+
+Os 2 anexos para skills preexistentes sao:
+
+- `moodboard_manifest.schema.json` (anexo de `art-direction-selector`)
+- `adaptive_music_state_map.schema.json` (anexo de `xgm2-audio-director`)
+
+Nenhuma das mudancas altera o wrapper de build (`tools/sgdk_wrapper/build.bat`, `build_inner.bat`, `clean.bat`, `run.bat`, `env.bat`). Nenhuma copia ou fork de arquivo foi criado. A canonicalizacao do Chain foi feita in-place no diretorio `.agent/`, preservando o principio de correcao in-place do `doc/AGENTS.md`.
+
 ## 6. Alguma proxima secao preexistente
```

---

## Validacao esperada apos aplicacao

- O numero de linhas em `doc/06_AI_MEMORY_BANK.md` cresce em ~28 linhas (1 secao nova + 1 linha em branco).
- `git diff --stat doc/06_AI_MEMORY_BANK.md` continua reportando o trabalho sujo preexistente, mais este patch.
- Nenhum link interno quebrado: o patch nao remove nem renomeia secoes.
- A data no frontmatter do documento (se houver) NAO precisa ser alterada — este patch nao mexe em timestamp; quem fechar o worktree sujo deve decidir se atualiza "Ultima atualizacao".
