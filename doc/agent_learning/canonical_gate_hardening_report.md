# Canonical Gate Hardening Report

Data: 2026-06-01

Escopo: endurecimento do agente canonico e validadores. Esta rodada nao entrega jogo, ROM ou status de jogo pronto.

## Arquivos alterados

- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/audit_effect_campaign_semantics.ps1`
- `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
- `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
- `tools/sgdk_wrapper/ci/test_visual_gate_lab_fallback_blockers.ps1`
- `tools/sgdk_wrapper/ci/test_effect_campaign_semantic_audit.ps1`
- `tools/sgdk_wrapper/ci/test_validation_report_blocking_status_codes.ps1`
- `tools/sgdk_wrapper/ci/test_validation_report_canonical_summary.ps1`
- `doc/06_AI_MEMORY_BANK.md`
- `doc/agent_learning/canonical_gate_hardening_report.md`

## Novas regras efetivas

- `status_panel.technical_ready` e `status_panel.creative_ready` agora sao sinais separados.
- `technical_artifact_status` substitui o significado antigo de `aggregate_status`.
- `aggregate_status` permanece como alias deprecated e nunca e sinal de AAA.
- `ready_for_aaa=true` exige: `technical_ready=true`, `creative_ready=true`, `summary.errors=0`, `blocking_statuses=[]`, `creative_blocking_statuses=[]` e `semantic_audit_status!=failed`.
- `semantic_audit_report.json` ou `.md` com status `failed` adiciona `semantic_audit_failed`.
- GDD substancial e obrigatorio para AAA/delivery: fantasia, core loop, kit do jogador, regras sistemicas, progressao da fase, mapa/secoes, inimigos, riscos, ritmo, tutorial invisivel, climax e criterios de qualidade visual.
- fallback procedural/debug/lab como asset final adiciona `procedural_fallback_as_final`, bloqueia `creative_ready` e limita `max_delivery_status` a `technical_lab_validated`.
- julgamento visual real adiciona `visual_direction_failed` quando report/screenshot/contact sheet indica padrao repetitivo, painel textual, personagem generico, chuva estatica, mosaico debug ou asset procedural pobre.
- efeito sem consequencia jogavel evidenciada adiciona `gameplay_consequence_missing`.
- personagem premium sem idle, antecipacao, recuperacao, contato de pe, impacto e silhueta adiciona `animation_gate_failed`.
- decision log raso adiciona `decision_log_too_shallow`.
- evidencia por eixo ausente ou global demais adiciona `axis_evidence_missing`.
- `audit_effect_campaign_semantics.ps1` promove `repeated_effect_learning_notes` de warning para blocker.

## Testes executados

- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\sgdk_wrapper\ci\test_visual_gate_lab_fallback_blockers.ps1` passou: 24/24.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\sgdk_wrapper\ci\test_effect_campaign_semantic_audit.ps1` passou: 9/9.
- Suite relacionada a validation/semantic/visual gate passou ou pulou por fixture ausente explicitamente:
  - `test_effect_campaign_semantic_audit.ps1` passou.
  - `test_scene_capture_gate_mdrt_parser.ps1` passou.
  - `test_scene_capture_gate.ps1` passou.
  - `test_scene_closeout_gate.ps1` passou.
  - `test_validation_report_blocking_status_codes.ps1` pulou porque `SGDK_projects\BENCHMARK_VISUAL_LAB_V2` nao existe nesta arvore.
  - `test_validation_report_canonical_summary.ps1` pulou pelo mesmo motivo.
  - `test_validation_report_visual_gate_blocker.ps1` passou.
  - `test_visual_delivery_gate_report_blocks.ps1` passou.
  - `test_visual_delivery_gate_required_fields.ps1` passou.
  - `test_visual_gate_evidence_contracts.ps1` passou.
  - `test_visual_gate_lab_fallback_blockers.ps1` passou.
  - `test_visual_gate_sprite_vram_blockers.ps1` passou.
- `python -m json.tool` passou para `visual_delivery_gate_report.schema.json` e `aaa_scene_v1.json`.
- Validadores Python em `.agent/scripts` executados:
  - `self_check_agentic_aaa_contracts.py --help` passou e cobriu self-checks de strip, VDP, DMA e YM2612.
  - `validate_skill_framework.py --help` passou.
  - `validate_template_registry.py --help` passou com warnings ja existentes de templates contendo `out/`.
  - `check_route_decision_contract.py --help` passou.
- `rg -n "ready_for_aaa|aggregate_status|technical_artifact_status|creative_ready|technical_ready" F:\Projects\MegaDrive_DEV\tools\sgdk_wrapper` executado para conferir superficies.
- `git diff --check` global executado e falhou por whitespace preexistente fora do escopo, começando por `.gitignore` e varios wrappers de `SGDK_Engines`/templates.
- `git diff --check` limitado aos arquivos rastreados alterados nesta rodada passou.
- `rg -n "[ \t]+$"` nos arquivos alterados nesta rodada nao encontrou trailing whitespace.

## Exemplos de bloqueios agora detectados

Fixture `visual_gate_lab_fallback_fixture` produziu:

- `technical_ready=false`
- `creative_ready=false`
- `technical_artifact_status=not_builded`
- `aggregate_status=not_builded`
- `aggregate_status_deprecated=true`
- `semantic_audit_status=failed`
- `max_delivery_status=technical_lab_validated`
- `ready_for_aaa=false`
- `creative_blocking_statuses`: `semantic_audit_failed`, `gdd_substantial_insufficient`, `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`, `decision_log_too_shallow`, `axis_evidence_missing`, `gameplay_consequence_missing`, `animation_gate_failed`

## Riscos residuais

- `git diff --check` global ainda falha por sujeira preexistente fora do escopo. Nao foi corrigido para preservar o worktree sujo.
- Dois testes antigos dependem de `SGDK_projects\BENCHMARK_VISUAL_LAB_V2`; agora pulam de forma explicita quando a fixture nao existe.
- O analisador visual opcional emitiu `Erro: Pillow nao instalado. Execute: pip install Pillow` em fixture de teste, mas os gates canonicos testados passaram sem depender dele.
- Os gates criativos novos validam contratos/reportes declarativos; a qualidade final ainda exige evidencia empirica real, incluindo BlastEm quando se tratar de entrega de ROM.

## Confirmacao canonica

`ready_for_aaa` nao pode mais ser derivado apenas de build, BlastEm, runtime capture, budget, screenshots ou reports tecnicos. A promocao AAA agora exige prontidao tecnica e criativa simultaneas, sem blockers tecnicos, criativos ou semanticos.
