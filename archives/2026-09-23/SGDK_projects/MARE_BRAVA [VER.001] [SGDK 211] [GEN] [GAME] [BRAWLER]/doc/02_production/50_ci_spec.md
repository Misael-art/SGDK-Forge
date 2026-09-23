---
status: seed
prd_title: CI and Local CI Spec
last_updated: 2026-07-03
---

# CI and Local CI Spec - MARE_BRAVA

Gate local canonico: `tools/sgdk_wrapper/ci/run_golden_validate.ps1`.
Por iteracao: build wrapper -> validate_resources -> validate_brawler_belt_scroll_specialization ->
audit_game_design_contracts -> evidencia BlastEm. Nenhum passo pulado (AGENTS.md).
Nota de host: neste Linux os validadores rodam com pwsh + USERPROFILE=$HOME (receita na memoria do workspace).
