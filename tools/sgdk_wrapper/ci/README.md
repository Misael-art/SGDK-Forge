# CI & Test Infrastructure — `tools/sgdk_wrapper/ci/`

> **Escopo**: scripts de teste local, gates de contrato, validadores de
> schema, e orchestrators que mantem a infraestrutura do wrapper SGDK
> honesta.
> **Nao substitui**: `validate_resources.ps1` (gate de projeto) nem
> `run_golden_validate.ps1` (validacao historica de pipeline).

---

## Filosofia

Esta pasta existe para responder a uma pergunta simples:

> "Se alguem rodar esses scripts hoje, ainda passam?"

A resposta tem que ser **sim** com 0 surpresa. Para isso, cada script
tem 3 propriedades:

1. **Determinista**: mesmos inputs, mesmos outputs, mesmo exit code.
2. **Auto-contido**: nao requer projeto real, cria fixtures internas.
3. **Rastreavel**: cada teste tem nome, motivo, e (quando relevante)
   reproduz o bug que ele protege contra.

## Layout

| Arquivo | Lingua | Cobre |
|---------|--------|-------|
| `run_all_contract_gates.ps1` | PowerShell | Orchestrator principal: roda audit + schema + metodologia + bootstrap + freshness + higiene + status sync, gera `contract_gates_report.json` |
| `test_agent_startup_environment.ps1` | PowerShell | Guard comum de agentes, preparo automatico, report `AGENT_ENVIRONMENT_REPORT.json` e uso consultivo do Graphify |
| `test_game_design_contract_gates.ps1` | PowerShell | 60 tests do auditor v2.0.0 (3 buckets + 6 ready flags) |
| `test_schema_contract_gates.py` | Python | 21 tests dos schemas (Draft-07, allOf, $ref) |
| `test_project_methodology_governance.ps1` | PowerShell | 16 testes de claims estruturados, adocao segura, naming, freshness e gates de movimento/estrada/boss |
| `test_project_bootstrap_qaproof.ps1` | PowerShell | 18 testes de template limpo, naming, manifests, placeholders, adocao e descoberta Python do preflight |
| `test_project_hygiene_governance.ps1` | PowerShell | Isolamento de projeto, `rascunho/`, orfaos e copia/hash de entradas externas |
| `test_technique_usage_governance.ps1` | PowerShell | Evidencia de tecnica local, refs documentais verificaveis e rejeicao de autorizacao externa legada |
| `test_changelog_status_sync.ps1` | PowerShell | Prova que `-StatusOnly` sincroniza a memoria sem criar snapshots ou alterar o changelog |
| `test_validation_report_*.ps1` | PowerShell | Contrato do `validation_report.json` |
| `test_visual_gate_*.ps1` | PowerShell | Contrato do `visual_delivery_gate_report.json` |
| `test_scene_*.ps1` | PowerShell | Contrato do `scene_contract_report.json` |
| `test_axe_*.ps1`, `test_sprite_strip_*.ps1`, `test_parser_*.ps1` | PowerShell | Validadores especificos de asset/runtime |
| `test_prd_readiness.ps1`, `test_freshness_audit.ps1` | PowerShell | Sondas meta; freshness prova que drift interno bloqueia closeout |
| `test_cutscene_contract_lint.ps1` | PowerShell | Lint de cutscene contracts |
| `test_res_graph_*.ps1` | PowerShell | Auditoria de res/graphs e VRAM residency |
| `test_runtime_capture_blastem_noninteractive.ps1` | PowerShell | Captura nao-interativa via BlastEm |
| `test_lab_category_product_taxonomy.ps1` | PowerShell | Sanidade de product_taxonomy.json |
| `test_effect_campaign_semantic_audit.ps1` | PowerShell | Lint do semantic_audit do effect campaign |
| `test_agent_context_*.ps1` | PowerShell | Bridge entre agente e contexto persistente |
| `test_no_res_and_emulator_evidence_blockers.ps1` | PowerShell | Gate de evidencia (res/ e emulador) |
| `run_golden_validate.ps1` | PowerShell | Validacao de regressao historica do pipeline |
| *(resto dos `test_*.ps1`)* | PowerShell | Cobertura de comportamento historico |

## Execucao

### Todos os gates de contrato (recomendado)

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode full
```

Modos disponiveis:

- `full` (default) — audit + schema + metodologia + bootstrap + freshness + higiene, exit 0 se todos passarem.
- `audit` — so auditor.
- `schema` — so schemas.
- `smoke` — audit + schema + metodologia + bootstrap + freshness + higiene para PR local.

### Individual

```powershell
# Auditor v2.0.0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_game_design_contract_gates.ps1

# Schemas Draft-07
python tools/sgdk_wrapper/ci/test_schema_contract_gates.py

# Adocao metodologica e claims estruturados
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_project_methodology_governance.ps1
```

## Padroes de output

- Cada script imprime `=== Resumo ===` com `Passou: N / N`.
- `PASS`/`FAIL` por assercao.
- Exit code: 0 (verde), 1 (vermelho), 2 (gate bloqueado).
- Orchestrator grava `out/ci/contract_gates_report.json` com
  `combined_status` (`passed`/`failed`).

## Contratos coberto por cada suite

### `test_game_design_contract_gates.ps1` (60 tests)

- **3-bucket separation**: blockers nao vazam em creative, creative nao
  vaza em tech_artifact.
- **6 ready flags**: technical_ready, creative_ready, ready_for_aaa,
  technical_artifact_status, semantic_audit_status,
  semantic_audit_repeated_effect_learning_notes.
- **lab downgrade**: blocker vira warn, mas creative/tech_artifact NAO.
- **schema_version**: 2.0.0 no report.
- **18 testes de comportamento** + **42 assercoes de contrato**.

### `test_schema_contract_gates.py` (21 tests)

- **mechanic_contract**: versatility<3, min_reuses<3, combos=[] rejeitados;
  probability random exige success_rate_percent.
- **level_blueprint**: waypoint_sequence<2, phase enum invalido
  rejeitados; pressure/calm opcionais via anyOf.
- **enemy_roster**: boss_state_count<3 rejeitado sem justificativa;
  head_metric XL valido para boss.
- **methodology/road/boss**: claims obrigatorios, contratos vazios e boss
  modular de uma unica parte sao rejeitados.

### `test_project_methodology_governance.ps1` (16 tests)

- materializa contratos ausentes sem sobrescrever projetos antigos;
- bloqueia placeholder, lifecycle invalido e ausencia de `freshness_audit`;
- impede inferencia por palavras soltas e bypass perceptual por evidencia isolada;
- exige contratos e simbolos runtime para road physics e boss modular.

### `test_validation_report_*.ps1`

- Forma canonica do `validation_report.json` em projetos.
- Codigos de blocking_status_codes reconhecidos.
- Bloco `audit_game_design_contracts` presente quando chain ativa.

## Adicionando um novo test

1. Criar `<nome>_test.ps1` (PowerShell) ou `<nome>_test.py` (Python).
2. Auto-criar fixtures em `<temp>/ci_fixture_<test_id>/`.
3. Limpar fixtures no fim (mesmo em caso de erro via `try/finally`).
4. Exit 0 verde, 1 vermelho, 2 gate bloqueado.
5. (Opcional) Adicionar chamada em `run_all_contract_gates.ps1` se for
   gate de contrato.

## Adicionando um novo orchestrator

1. Reusar `run_all_contract_gates.ps1` se possivel (parametros
   `-Mode`/`-OutputDir`).
2. Output canonico em `out/ci/<report>.json`.
3. Documentar aqui.

## Quando rodar

- **Antes de PR**: `run_all_contract_gates.ps1 -Mode smoke`.
- **Antes de merge**: `run_all_contract_gates.ps1 -Mode full`.
- **Antes de release**: alem de `full`, rodar o restante dos
  `test_*.ps1` que nao estao agregados no orchestrator.

## Limitacoes conhecidas

- `run_golden_validate.ps1` ainda usa fixtures hardcoded de 2026-05-31;
  novos cenarios devem ser adicionados la antes de virar "golden".
- `test_runtime_capture_blastem_noninteractive.ps1` exige BlastEm
  instalado; CI host sem BlastEm tera failures false-positive.
- `test_no_res_and_emulator_evidence_blockers.ps1` assume layout
  canonico (`res/`, `out/captures/`, `out/saves/`); projetos com
  layout customizado devem ser excluidos via `-ProjectRoot`.

## Historia

- 2026-06-02: orchestrator `run_all_contract_gates.ps1` + consumer
  contract doc + smoke E2E.
- 2026-05-31: suite inicial de 18 tests.
- 2026-04-21: primeira leva de tests historicos.
