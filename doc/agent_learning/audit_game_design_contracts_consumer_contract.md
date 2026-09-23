# Consumer Contract: `audit_game_design_contracts_report.json`

> **Schema version**: 2.0.0 (auditor)
> **Aplicavel a partir de**: Canonical Hardening Full Repair (2026-06-02)
> **Consumidores**: `validate_resources.ps1` (chain integration),
> futuros dashboards CI, scripts de promocao de status.

Este documento descreve o **contrato de saida** do
`audit_game_design_contracts.ps1` para consumidores downstream. O contrato
e estavel dentro de uma major version; mudancas adicionam campos, nao
removem.

---

## Localizacao

- **Padrao**: `<wrapper_root>/out/logs/audit_game_design_contracts_report.json`
- **Override**: parametro `-OutputPath` no script.
- **Encapsulado em `validation_report.json`**: bloco
  `audit_game_design_contracts` (sincronizado pela chain integration).

## Top-level fields

| Campo | Tipo | Significado |
|-------|------|-------------|
| `schema_version` | string (semver) | Sempre `"2.0.0"` para esta versao |
| `audit_id` | string | `audit_YYYYMMDD_HHMMSS` |
| `timestamp` | string (ISO 8601) | Momento da emissao |
| `product_status` | enum | `technical_lab_validated \| vertical_slice_candidate \| ready_for_aaa \| technical_incomplete \| unscoped` |
| `status` | enum | `passed \| warn \| blocked` — agregado geral |
| `issues` | array<issue> | Lista completa de issues, cada uma com `code`, `severity`, `bucket`, `message` |
| `blocking_statuses` | array<string> | Codigos que bloqueiam o status (integridade) |
| `creative_blocking_statuses` | array<string> | Codigos criativos (direcao/autoria/visual) |
| `technical_artifact_codes` | array<string> | Codigos de artefato tecnico (lineage/optimization/premium) |
| `technical_artifact_status` | enum | `not_audited \| technical_artifact_ok \| <code>` |
| `semantic_audit_status` | enum | `not_provided \| passed \| failed \| invalid_json` |
| `semantic_audit_repeated_effect_learning_notes` | bool | True se `semantic_audit_report.repeated_effect_learning_notes` nao vazio |
| `technical_ready` | bool | True se nenhum blocker E nenhum technical_artifact |
| `creative_ready` | bool | True se nenhum creative_blocker E `semantic_audit_status != failed` |
| `ready_for_aaa` | bool | AND de todos os ready flags + checks finais |
| `cross_references` | object | Referencias cruzadas entre contratos |
| `catalog_checks` | object | Validacao contra catalogos canonicos |
| `input_paths` | object | Paths de entrada (para debug) |

## Issue shape

```json
{
  "code": "mechanic_underused",
  "severity": "blocker",
  "bucket": "blocker",
  "message": "Core mechanic dash has versatility_cases=2 (< 3)."
}
```

| `severity` | `bucket` | Origem |
|------------|----------|--------|
| `blocker` | `blocker` | Falha de integridade de contrato / runtime |
| `creative_blocker` | `creative_blocker` | Falha de direcao/autoria/visual |
| `technical_artifact` | `technical_artifact` | Falha de asset/lineage/optimization |
| `warn` | `warn` | Observacao sem consequencia de gate |

## Ready flags (logica de computacao)

```
technical_ready = blocking_statuses.Count == 0
                  AND technical_artifact_codes.Count == 0

creative_ready = creative_blocking_statuses.Count == 0
                 AND semantic_audit_status != "failed"

ready_for_aaa = technical_ready
                AND creative_ready
                AND blocking_statuses.Count == 0
                AND creative_blocking_statuses.Count == 0
                AND semantic_audit_status != "failed"
                AND NOT semantic_audit_repeated_effect_learning_notes
```

**Importante**: `ready_for_aaa` aqui e o sinal do **auditor de contratos**.
A promocao efetiva depende de `claim_ceiling` em
`validate_resources.ps1` (cabe a politica de produto).

## Compatibilidade

- v1.x do auditor NAO emitia `creative_blocking_statuses`,
  `technical_artifact_codes`, `technical_artifact_status`, `semantic_audit_status`,
  `semantic_audit_repeated_effect_learning_notes`, `technical_ready`,
  `creative_ready` ou `ready_for_aaa`. Consumidores que checavam apenas
  `status` e `blocking_statuses` continuam funcionando.
- v2.0.0 adiciona 6 ready flags + 2 arrays + 1 enum. Consumidores devem
  usar `??null` ou `??[]` ao ler campos novos para nao quebrar em v1.x.

## Codigos canonicos por bucket

### blocker (~30)

- `mechanic_contract_missing` / `mechanic_contract_invalid_json` /
  `mechanic_contract_invalid_shape`
- `mechanic_role_invalid` / `mechanic_underused` / `mechanic_no_combination`
- `mechanic_probability_undeclared` / `mechanic_input_ambiguous`
- `level_blueprint_missing` / `level_blueprint_invalid_json`
- `golden_path_missing` / `phase_rhythm_missing` / `level_mechanic_reuse_missing`
- `enemy_roster_missing` / `enemy_roster_invalid_json` /
  `enemy_roster_invalid_shape`
- `enemy_role_missing` / `enemy_role_invalid` / `enemy_telegraph_missing`
- `enemy_synergy_missing` / `enemy_head_metric_invalid`
- `tdd_missing_for_product` / `tdd_invalid_json`
- `scene_fsm_missing` / `memory_pool_missing` / `runtime_ownership_missing`
- `region_timing_missing_for_product` / `input_contract_missing_for_product`

### creative_blocker (~25)

- `art_direction_undeclared` / `style_catalog_not_consulted`
- `style_clone_risk_unbounded` / `art_direction_low_confidence`
- `scene_direction_undeclared` / `archetype_catalog_not_consulted`
- `decorative_only_blocked` / `mode7_claim_on_megadrive`
- `monumental_promised_without_budget` / `signature_only_without_fallback`
- `background_ecology_unbounded`
- `gdd_substantial_insufficient` / `gdd_substantial_missing`
- `feature_creep` / `core_loop_undefined`
- `visual_direction_failed` / `animation_gate_failed`
- `gameplay_consequence_missing`
- `visual_gate_blocked` / `visual_delivery_gate_missing`
- `procedural_fallback_as_final` / `decision_log_too_shallow`
- `axis_evidence_missing`

### technical_artifact (~25)

- `style_manifest_missing` / `style_drift_uncorrected` / `style_memory_drift`
- `asset_lineage_missing`
- `premium_source_missing` / `source_validity_failed` /
  `authoriality_gate_failed` / `clone_risk_report_missing`
- `frame_budget_missing` / `pivot_scale_contract_missing`
- `animation_state_plan_missing` / `motion_phase_map_missing` /
  `frame_delta_report_missing`
- `asset_optimization_unmeasured` / `dedup_unmeasured`
- `missing_semantic_parse` / `translation_without_review`
- `raster_fx_owner_collision` / `palette_cycle_ownership_conflict`
- `cutscene_visual_contract_missing` / `cutscene_fullscreen_unjustified` /
  `cutscene_contract_missing`
- `architectural_baseline_undefined` / `level_risk_untelegraphed`

## Modo lab (`technical_lab_validated`)

Quando `product_status == technical_lab_validated`:
- Blockers sao downgraded para `warn` (status = `warn` em vez de `blocked`).
- `blocking_statuses` fica vazio (lab nao exige contratos integros).
- `creative_blocking_statuses` e `technical_artifact_codes` NAO sao
  downgraded — lab pode ter gates criativos ativos se o usuario pedir.
- `ready_for_aaa` continua `true` para fixtures limpas em lab (decisao
  fica com `claim_ceiling` em `validate_resources`).

## Exemplo minimo (fixture completa, sem semantic audit)

```json
{
  "schema_version": "2.0.0",
  "status": "passed",
  "blocking_statuses": [],
  "creative_blocking_statuses": [],
  "technical_artifact_codes": [],
  "technical_artifact_status": "technical_artifact_ok",
  "semantic_audit_status": "not_provided",
  "semantic_audit_repeated_effect_learning_notes": false,
  "technical_ready": true,
  "creative_ready": true,
  "ready_for_aaa": true
}
```

## Versionamento

- Major bump: remocao de campo, mudanca de semantica de campo existente,
  mudanca no schema_version do report.
- Minor bump: adicao de campo opcional.
- Patch bump: correcao de bug sem mudanca de contrato.

Auditor v2.0.0 congela o contrato descrito aqui. Auditor v2.1.x podera
adicionar campos, nao remover.
