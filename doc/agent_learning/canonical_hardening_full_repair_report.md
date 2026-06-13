# Canonical Hardening Full Repair — Report

> **Data**: 2026-06-02
> **Escopo**: 8 PARTEs (0, 1, 2, 3, 4, 5, 6, 7, 8) + suite final.
> **Regra de ferro aplicada**: este relatorio documenta um hardening do framework
> `.agent` do wrapper SGDK. NAO declara `ready_for_aaa`, `game_complete`,
> `AAA_validated`, `pronto` ou `final_product_ready` para nenhum projeto.
> Nenhum jogo foi entregue. Apenas o framework foi tornado mais estrito e mais
> observavel.

---

## TL;DR

| PARTE | Foco | Resultado |
|-------|------|-----------|
| 0 | Inspecoes paralelas (patches, schemas, imagegen, pipeline) | OK |
| 1 | Reescrita do `audit_game_design_contracts.ps1` com 3 buckets + ready flags | 60/60 testes PASS |
| 2 | Integracao do auditor em `validate_resources.ps1` (chain opcional) | Syntax OK, splice antes do WriteAllText |
| 3 | Correcao de 3 schemas (`allOf` + `if/then` Draft-07) | 14/14 schema tests PASS |
| 4 | Validacao de `game_production_v1.json` + `5-stage-production.md` | 10 steps, 9 ready axes, refs S0b/S2b |
| 5 | Classificacao do diff `aaa_scene_v1.json` | COMPATIBLE, NAO revertido |
| 6 | Correcoes em `imagegen_tool.py` + profiles + manifest + README | JSON OK, syntax OK |
| 7 | Extensao de `test_game_design_contract_gates.ps1` (12-18) | 7 novos testes, 0 falhas |
| 8 | Este relatorio | Gravado |

**Veredito**: framework `.agent` endurecido em 4 eixos (auditor, schemas,
pipeline, imagegen). Nenhum produto foi promovido. Nenhum status final
positivo foi atribuido.

---

## 1. Mudancas por arquivo

### 1.1 `tools/sgdk_wrapper/audit_game_design_contracts.ps1` (REESCRITO)

**Antes**: 2 buckets (blocker, warn). Sem ready flags.
**Depois**: 3 buckets + 6 ready flags + tabela canonica de severidade.

Nova superficie de saida:

```json
{
  "schema_version": "2.0.0",
  "status": "passed|warn|blocked",
  "blocking_statuses": [...],
  "creative_blocking_statuses": [...],
  "technical_artifact_codes": [...],
  "technical_artifact_status": "not_audited|technical_artifact_ok|<code>",
  "semantic_audit_status": "not_provided|failed|passed|invalid_json",
  "semantic_audit_repeated_effect_learning_notes": false,
  "technical_ready": false,
  "creative_ready": false,
  "ready_for_aaa": false
}
```

Tabela `codeSeverity` cobre ~60 codigos:
- `blocker` (~30): `mechanic_*`, `level_*`, `enemy_*`, `tdd_*`, `region_*`
- `creative_blocker` (~25): `art_direction_undeclared`, `decorative_only_blocked`,
  `mode7_claim_on_megadrive`, `monumental_promised_without_budget`,
  `gdd_substantial_insufficient`, `visual_direction_failed`,
  `animation_gate_failed`, `gameplay_consequence_missing`, etc.
- `technical_artifact` (~25): `style_manifest_missing`, `asset_lineage_missing`,
  `source_validity_failed`, `premium_source_missing`,
  `asset_optimization_unmeasured`, `cutscene_visual_contract_missing`, etc.

A funcao `Add-Issue` agora classifica automaticamente em 3 arrays.
Em modo `technical_lab_validated`, blockers viram warn (mas creative_blockers
e technical_artifacts NAO viram warn — lab pode ter gates criativos ativos
se o usuario pedir).

Exit codes preservados: 0=passed, 1=warn, 2=blocked.

### 1.2 `tools/sgdk_wrapper/validate_resources.ps1` (INTEGRACAO)

Bloco `GAME_PRODUCTION_CHAIN_INTEGRATION` inserido antes do `WriteAllText`
final (linha ~5462). Executa `audit_game_design_contracts.ps1` quando:
1. `auditScript` existe no wrapper.
2. `product_status != technical_lab_validated`.
3. Ha pelo menos um contrato de design em `doc/contracts/` ou na raiz do projeto.

Sincroniza 3 arrays no `$results`:
- `audit_game_design_contracts.{blocking_statuses, creative_blocking_statuses, technical_artifact_codes, technical_artifact_status, semantic_audit_status, technical_ready, creative_ready, ready_for_aaa}` (novo bloco)
- `results.blocking_statuses` (merge unico)
- `results.status_panel.creative_blocking_statuses` (merge unico)

Quando `status=blocked` no audit, adiciona `audit_game_design_contracts_blocked`
em `results.blocking_statuses` via `Add-BlockingStatus` (padrao canonico do script).

A politica de `claim_ceiling` continua sendo do `validate_resources` — o audit
nao promove `ready_for_aaa` por conta propria; ele so calcula o sinal.

### 1.3 Schemas (3 arquivos — `allOf`/`if/then` Draft-07)

**`mechanic_contract.schema.json`**: adicionado `allOf: [core_constraints, probability_constraints]`
no top-level. `core_constraints` agora exige `versatility_cases[minItems=3]`,
`level_design_reuse_plan.min_reuses[minimum=3]`, `combination_map[minItems=1]`
quando `mechanic_role=core`. `probability_constraints` exige
`success_rate_percent` quando `type != deterministic`.

**`level_blueprint.schema.json`**: adicionado `allOf: [rhythm_constraint, golden_path_min_waypoints]`.
`rhythm_constraint` agora declara `phase` enum explicito
(`calm|pressure|payoff|boss|transition|safe_room`) e exige `intensity` enum.
`golden_path_min_waypoints` exige `waypoint_sequence[minItems=2]`.

**`enemy_roster.schema.json`**: adicionado `allOf: [boss_state_constraint, head_metric_role_constraint]`.
`boss_state_constraint` exige `boss_state_count[minimum=3]` OU
`boss_curto_justification` quando `role=boss`.
`head_metric_role_constraint` documenta a restricao XL=boss (a auditoria ja
faz a checagem runtime).

**Validacao**: `python tools/sgdk_wrapper/ci/test_schema_contract_gates.py`:
**14/14 PASS** (5 mechanic + 5 level + 4 enemy).

### 1.4 `tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1` (EXTENSAO)

7 novos testes (12-18) alem dos 11 originais:

| # | Foco | Assercoes criticas |
|---|------|-------------------|
| 12 | 3-bucket separation (clean fixture) | `technical_ready=true`, `creative_ready=true`, `ready_for_aaa=true`, `semantic_audit_status=not_provided` |
| 13 | lab + fixture completa | `status=passed`, `ready_for_aaa=true` |
| 14 | lab + bad mechanic (versatility=1) | `status=warn` (downgrade), `severity=warn` no issue |
| 15 | Schema fields do report | todos os 9 campos novos presentes |
| 16 | `schema_version=2.0.0` | novo schema versionado |
| 17 | lab sem contracts | `status=passed`, `technical_artifact_status=technical_artifact_ok` |
| 18 | slice + tdd parcial | `technical_ready=false`, `creative_ready=true`, `ready_for_aaa=false` (co-existencia) |

Total: **60/60 PASS** (era 19/19 — agora cobre os 3 buckets + ready flags).

### 1.5 `tools/sgdk_wrapper/ci/test_schema_contract_gates.py` (NOVO)

Python jsonschema Draft-07 validator. Pareia com o test PowerShell:
- PowerShell prova que o audit emite o codigo esperado.
- Python prova que o schema REJEITA o contrato invalido.

14 casos, todos PASS.

### 1.6 `tools/ai_imagegen/imagegen_tool.py` (EXIT CODE FIX)

`main()` agora detecta `result["ok"]==False` e propaga exit code
nao-zero. Mapeamento `stage -> exit`:
- `license` -> 2
- `scope` -> 3
- `host` -> 4
- `timeout` / `serve_offline` / `send_request` -> 6
- `no_output` / `missing_*_script` -> 7
- default -> 2

Antes: `python imagegen_tool.py bonsai serve` retornava exit 0 mesmo quando
a license gate recusava — o usuario nao distinguia sucesso de falha.

### 1.7 `tools/ai_imagegen/config/imagegen_profiles.json` (PATHS)

Bonsai `setup`/`serve`/`send_request` apontavam para a raiz do repo
Bonsai. Os scripts estao em `scripts/` subdir (confirmado em
`install.repo_files` na mesma profile). Corrigido para `scripts/setup.ps1`
etc. Aplicado em `bonsai_4b_ternary` e `bonsai_4b_binary`.

### 1.8 `tools/ai_imagegen/models/manifest.json` (BONSAI ENTRIES)

Adicionadas 2 entries:
- `bonsai-4b-ternary` (1210 MB, 1.58-bit)
- `bonsai-4b-binary` (850 MB, 1-bit)

Cada uma marcada com `license_status: pending_license_validation` e
`source_status: pending_source_verification` ate o humano emitir
`bonsai_license_ack.json` e o gate de licenca passar. Ate la, o audit
de game design NAO aceita Bonsai como fonte final AAA — apenas
`concept_art`, `tileset_concept`, `dither_mask`, `contrast_study`.

### 1.9 `tools/ai_imagegen/README.md` (DOCS)

Adicionada secao "Exit codes e persistencia" + "Status de licenca no
manifest (Canonical Hardening v2)".

---

## 2. Validacao por eixo

| Eixo | Evidencia | Status |
|------|-----------|--------|
| **build** | `validate_resources.ps1` ainda compila; `audit_game_design_contracts.ps1` parse OK; 3 schemas JSON validos; 2 imagegen JSONs validos | OK |
| **validation_report** | integra audit_game_design_contracts via bloco `GAME_PRODUCTION_CHAIN_INTEGRATION`; readme descreve o split de buckets | OK |
| **boot_emulador** | NAO aplicavel a este hardening (nao ha ROM nova) | N/A |
| **gameplay_basico** | NAO aplicavel (framework apenas) | N/A |
| **performance** | NAO aplicavel | N/A |
| **audio** | NAO aplicavel | N/A |
| **memoria operacional** | `doc/agent_learning/canonical_hardening_full_repair_report.md` (este arquivo) | OK |

Aplica-se a regra: "Se nao foi visto rodando no emulador, nao existe".
O endurecimento do framework NAO e um produto jogavel, entao a regra
nao se aplica literalmente. Mas o `audit_game_design_contracts_report.json`
gerado pelos testes (Test 11: fixture completa) emite `ready_for_aaa=true`
apenas no nivel de CONTRATOS — o BlastEm gate continua obrigatorio para
o produto real.

---

## 3. Mudancas NAO feitas (intencionalmente)

| Item | Por que NAO |
|------|-------------|
| `git stage` / `commit` / `push` | usuario nao pediu; AGENTS.md diz "Nunca commitar sem pedido" |
| Reverter o diff `aaa_scene_v1.json` (224 insercoes) | Classificado como COMPATIBLE em PARTE 5; os novos stages S0b/S2b adicionam creative gates que o auditor precisa reconhecer |
| Aplicar `pending_integration/patch_SGDK_GLOBAL_chain_v1.md` | Worktree dirty preexistente (HEAD=3496 linhas); usuario nao pediu para limpar |
| Aplicar `pending_integration/patch_AI_MEMORY_BANK_chain_v1.md` | Idem |
| Declarar `ready_for_aaa` | PROIBIDO. Canonical Hardening v2 nunca promove esse status sozinho — `claim_ceiling` em `validate_resources` e a fonte da verdade |
| Instalar Bonsai / baixar modelo / escrever em `res/` | PROIBIDO. Bonsai so pode produzir `concept_art`, `tileset_concept`, `dither_mask`, `contrast_study` ate Fase D completa |
| Modificar `doc/AGENTS.md` (ja observado via system reminder) | Sem diff necessario; o doc ja declara as regras de hierarquia e gates |

---

## 4. Riscos preexistentes preservados (worktree dirty)

O `git status` mostra ~8500 linhas modificadas preexistentes. As 3 mais
relevantes ja tem patches em `doc/agent_learning/pending_integration/`:

- `SGDK_GLOBAL.md` (chain v1)
- `doc/06_AI_MEMORY_BANK.md` (chain v1)
- `validate_resources.ps1` (chain integration v1)

**Aplicar**: NAO feito nesta sessao (regra: "preservar trabalho humano,
mudancas cirurgicas com manifesto+relatorio"). Os patches estao
disponiveis; quem limpar o worktree pode aplicá-los depois.

Adicionalmente, `aaa_scene_v1.json` tem 224 linhas diff (PARTE 5: classificado
como COMPATIBLE).

---

## 5. Suite de validacao (replayavel)

```bash
# 1. Auditor + ready flags
powershell -NoProfile -ExecutionPolicy Bypass -File \
  "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\ci\test_game_design_contract_gates.ps1"
# Esperado: 60/60 PASS

# 2. Schemas (Python jsonschema)
python "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\ci\test_schema_contract_gates.py"
# Esperado: 14/14 PASS

# 3. JSON syntax em todos os JSONs tocados
python -m json.tool "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\.agent\pipelines\game_production_v1.json" | Out-Null
python -m json.tool "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\.agent\pipelines\aaa_scene_v1.json" | Out-Null
python -m json.tool "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\schemas\mechanic_contract.schema.json" | Out-Null
python -m json.tool "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\schemas\level_blueprint.schema.json" | Out-Null
python -m json.tool "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\schemas\enemy_roster.schema.json" | Out-Null
python -m json.tool "F:\Projects\MegaDrive_DEV\tools\ai_imagegen\models\manifest.json" | Out-Null
python -m json.tool "F:\Projects\MegaDrive_DEV\tools\ai_imagegen\config\imagegen_profiles.json" | Out-Null

# 4. PowerShell syntax dos scripts editados
powershell -NoProfile -ExecutionPolicy Bypass -File \
  "C:\Users\misae\AppData\Local\Temp\opencode\parse_check.ps1" \
  "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\audit_game_design_contracts.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File \
  "C:\Users\misae\AppData\Local\Temp\opencode\parse_check.ps1" \
  "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\validate_resources.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -File \
  "C:\Users\misae\AppData\Local\Temp\opencode\parse_check.ps1" \
  "F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper\ci\test_game_design_contract_gates.ps1"

# 5. Python syntax
python -c "import ast; ast.parse(open(r'F:\Projects\MegaDrive_DEV\tools\ai_imagegen\imagegen_tool.py', encoding='utf-8').read())"
```

---

## 6. Conclusao

O framework `.agent` esta mais estrito e observavel:
- 3 buckets de severidade (blocker / creative_blocker / technical_artifact)
- 6 ready flags (technical_ready, creative_ready, ready_for_aaa, etc.)
- 3 schemas com constraints `allOf`/`if-then` ativos
- 7 novos testes cobrindo separacao e ready flags
- 1 chain opcional integrando auditor em `validate_resources`
- imagegen com exit codes honestos
- Bonsai marcado como `pending_license_validation`

**NAO houve**:
- Promocao de nenhum projeto a `ready_for_aaa`
- Commit, stage, push, restore, delete
- Instalacao de Bonsai ou download de modelo
- Escrita em `res/` ou `out/rom.bin`
- Declaracao de produto completo

O gate de entrega continua: BlastEm + 5 reports de design + 5 booleans
verdes + memoria operacional canonica. O framework agora exige tudo isso
com mais rigor.

---

## 7. Referencias

- `tools/sgdk_wrapper/audit_game_design_contracts.ps1` (v2.0.0)
- `tools/sgdk_wrapper/validate_resources.ps1` (integracao chain)
- `tools/sgdk_wrapper/schemas/{mechanic,level_blueprint,enemy_roster}.schema.json`
- `tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1` (60/60)
- `tools/sgdk_wrapper/ci/test_schema_contract_gates.py` (14/14, novo)
- `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json` (10 steps)
- `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json` (sub-loop com S0b/S2b)
- `tools/sgdk_wrapper/.agent/workflows/5-stage-production.md` (refs art/scene-direction)
- `tools/ai_imagegen/imagegen_tool.py` (exit code fix)
- `tools/ai_imagegen/config/imagegen_profiles.json` (paths scripts/)
- `tools/ai_imagegen/models/manifest.json` (Bonsai entries com pending_*)
- `tools/ai_imagegen/README.md` (secoes exit codes + manifest status)

Predecessores:
- `doc/agent_learning/canonical_gate_hardening_report.md` (2026-06-01)
- `doc/agent_learning/product_pipeline_hardening_report.md` (2026-06-01)
- `doc/agent_learning/game_systems_pipeline_hardening_report.md` (2026-06-01)
