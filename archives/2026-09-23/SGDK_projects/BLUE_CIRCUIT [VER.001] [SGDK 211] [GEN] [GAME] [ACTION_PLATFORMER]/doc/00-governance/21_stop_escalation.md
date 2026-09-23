---
prd_id: PRD-01
title: Stop And Escalation Protocol
status: seed
applies_to: [prototype, AAA, stable, release, delivery]
unlocks: [fallback_authority, blocked_status_classification]
owner: agent
last_validated: null
---

# Stop And Escalation Protocol

## Tentar Fallback E Continuar

- falha de gerador de imagem quando existir rota alternativa autoral persistivel
- asset pesado demais quando houver reducao conservadora sem quebrar a fantasia
- CI remoto ausente quando `local_ci_gate_report` valido cobrir o gate
- save/SRAM ausente quando `persistence_scope=none`

## Bloquear Producao Visual Ou AAA

- `source_validity_failed`
- `visual_gate_blocked`
- `critical_asset_needs_review`
- `benchmark_derived_source`
- `vdp_dump_missing_required`
- `scene_regression_baseline_missing` em entrega AAA
- `save_system_contract_missing_when_persistence_required`

## Proibido Mascarar Como Sucesso

- ROM textual/proxy como entrega visual
- screenshot de cena errada como evidencia
- build limpo como prova de qualidade visual
- budget estimado como VDP dump
- assets `debug_lab` promovidos para `res/` final

## Registro Obrigatorio

Todo fallback deve registrar:

- motivo
- rota rejeitada
- rota escolhida
- risco residual
- status maximo permitido
