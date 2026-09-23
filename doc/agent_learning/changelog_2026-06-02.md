# Changelog — 2026-06-02 (Canonical Hardening Full Repair)

> **Escopo**: registro estavel de mudancas nao-comportamentais desta data.
> **Auditado por**: `audit_game_design_contracts.ps1` v2.0.0.
> **Relatorio detalhado**: `canonical_hardening_full_repair_report.md`.

---

## BREAKING

### Auditor de contratos: v1.x → v2.0.0

**Arquivo**: `tools/sgdk_wrapper/audit_game_design_contracts.ps1`

- **Schema version do report**: `1.x` (string ausente ou `1.0.0`) → **`2.0.0`**.
- **3 buckets adicionados** (separados):
  - `blocking_statuses` (existente; renomeado de "blockers" para deixar
    explicito que NAO inclui creative ou technical_artifact).
  - `creative_blocking_statuses` (NOVO).
  - `technical_artifact_codes` (NOVO).
- **6 ready flags adicionados**:
  - `technical_ready` (NOVO).
  - `creative_ready` (NOVO).
  - `ready_for_aaa` (NOVO; consumivel por `validate_resources.ps1`).
  - `technical_artifact_status` (NOVO; enum: `not_audited` /
    `technical_artifact_ok` / `<code>`).
  - `semantic_audit_status` (NOVO; enum: `not_provided` / `passed` /
    `failed` / `invalid_json`).
  - `semantic_audit_repeated_effect_learning_notes` (NOVO; bool).
- **Parametro novo**: `-SemanticAuditPath <path>` (opcional; alimenta
  `semantic_audit_status` e `repeated_effect_learning_notes`).

**Compatibilidade**: Consumidores que leem apenas `status` e
`blocking_statuses` continuam funcionando. Consumidores devem usar
`??null` ou `??[]` ao ler campos novos para nao quebrar em v1.x.

**Documentacao**: `doc/agent_learning/audit_game_design_contracts_consumer_contract.md`.

---

## ADDED

### `validate_resources.ps1` — chain integration com auditor

- Bloco `GAME_PRODUCTION_CHAIN_INTEGRATION` adicionado antes do
  `WriteAllText` final.
- Chama `audit_game_design_contracts.ps1` quando `product_status != lab`
  e ha pelo menos 1 contrato em `doc/contracts/`.
- Sincroniza 3 arrays no `validation_report.json`:
  `audit_game_design_contracts.status`,
  `audit_game_design_contracts.blocking_statuses`,
  `audit_game_design_contracts.technical_artifact_codes`.
- Adiciona `audit_game_design_contracts_blocked` em
  `$results.blocking_status_codes` quando o auditor reporta
  `technical_ready=false`.

### Schemas Draft-07 corrigidos (3)

- `mechanic_contract.schema.json`: `allOf` no top-level com
  `core_constraints` e `probability_constraints` (versatility<3,
  min_reuses<3, combos=[] rejeitados; probability random exige
  success_rate_percent).
- `level_blueprint.schema.json`: `allOf` no top-level com
  `rhythm_constraint` (phase enum, intensity enum) e
  `golden_path_min_waypoints` (waypoint_sequence>=2).
- `enemy_roster.schema.json`: `allOf` no top-level com
  `boss_state_constraint` (boss_state_count>=3 OU
  boss_curto_justification) e `head_metric_role_constraint`.

### CI: orchestrator e suite Python

- `tools/sgdk_wrapper/ci/run_all_contract_gates.ps1` (NOVO):
  roda audit + schema, gera `out/ci/contract_gates_report.json`.
  -Modes: `full` (default) / `audit` / `schema` / `smoke`.
- `tools/sgdk_wrapper/ci/test_schema_contract_gates.py` (NOVO):
  14 tests pareando com o auditor PowerShell.
- `tools/sgdk_wrapper/ci/README.md` (NOVO): documenta toda a
  infraestrutura de testes.

### Pipeline AAA — stages criativos

- `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`:
  +224/-2. Adicionados `S0b_art_direction` e `S2b_scene_direction`
  referenciando `art-direction-selector` e `scene-direction-curator`.

### Imagegen — defensive checks

- `tools/ai_imagegen/imagegen_tool.py`: `main()` propaga exit code
  nao-zero quando `result["ok"]==False` (map stage→code: license=2,
  scope=3, host=4, timeout/serve_offline/send_request=6,
  no_output/missing_*_script=7; default=2).
- `tools/ai_imagegen/imagegen_circuit.py`: `run_imagegen_tool()`
  faz defensive check adicional: se rc=0 mas stdout/stderr contem
  `{"ok": false}`, trata como falha (rc=2).

---

## CHANGED

### `imagegen_profiles.json`

- Profiles `bonsai_4b_ternary` e `bonsai_4b_binary` agora apontam
  para `scripts/setup.{ps1,sh}`, `scripts/serve.{ps1,sh}`,
  `scripts/send_request.{ps1,sh}` (paths canonicos do repositorio
  Bonsai, nao caminhos locais de maquina).

### `models/manifest.json`

- 2 entries Bonsai adicionadas com `license_status:
  pending_license_validation` e `source_status:
  pending_source_verification` (1210MB bonsai-4b-ternary + 850MB
  bonsai-4b-binary).

### `imagegen_tool.py` README

- 2 secoes novas: "Exit codes e persistencia" e "Status de licenca
  no manifest".

### `5-stage-production.md`

- Referencia `art-direction-selector` e `scene-direction-curator`
  skills em S0 e S2.

---

## PATCHES APLICADOS (pending_integration/)

- `patch_validate_resources_chain_integration_v1.md` — header
  atualizado para "APLICADO em 2026-06-02" (aplicacao manual com
  pequenas divergencias; ver `STATUS_2026-06-02.md`).

---

## DEFERRED (nao alterado nesta sessao)

- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md` — dirty
  preexistente; nao tocado.
- `doc/06_AI_MEMORY_BANK.md` — dirty preexistente; nao tocado.
- Aa pipeline `game_production_v1.json` ja estava alinhado; sem diff.
- Skills `art-direction-selector` e `scene-direction-curator` ja
  existem; sem diff.

---

## NAO FEITO (intencionalmente)

- Nenhum stage, commit, reset, checkout, restore, delete, rollback.
- Nenhum projeto SGDK foi declarado `ready_for_aaa` ou
  `game_complete`.
- Nenhuma ROM foi rodada em BlastEm.
- Nenhum asset foi convertido para `res/`.
- Nenhum modelo Bonsai foi baixado ou executado.
- Nenhuma promocao automatica foi feita em `validate_resources`.

---

## SUITE FINAL

- `test_game_design_contract_gates.ps1`: 60/60 PASS
- `test_schema_contract_gates.py`: 14/14 PASS
- `run_all_contract_gates.ps1 -Mode full`: combined_status=passed
- Smoke E2E positivo (4 contratos validos): status=passed,
  ready_for_aaa=true
- Smoke E2E negativo (mechanic underused): status=blocked,
  ready_for_aaa=false, exit=2
