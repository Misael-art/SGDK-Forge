---
name: systems-mechanics-validator
description: Use quando a tarefa envolver validacao de mecanicas de jogo contra as 5 Leis Fundamentais (Agencia, Feedback, Fluxo, Consistencia, Recompensa) e os 5 Pilares de Validacao (espaco, gatilho, desafio, limitacao, probabilidade). Emite mechanic_validation_report, numeric_attribute_table e mechanic_juice_map. Nao use para projetar mecanicas do zero (use game-design-planning) ou para implementar runtime (use sgdk-runtime-coder).
---

# Systems Mechanics Validator

Esta skill existe para impedir que mecanicas entrem em codigo apenas com "ah, isso vai ser legal". Toda mecanica precisa passar pelos 5 Pilares e pelas 5 Leis antes de virar sprite, SFX ou estado de runtime.

## Quando usar

- projeto novo ou reseed precisa validar mecanicas core
- mudanca de mecanica existente em GDD/spec
- feature creep foi bloqueado e mecanica nova precisa ser avaliada
- audit pre-AAA precisa garantir que mecanicas tem contrato formal

## Nao use

- para projetar mecanicas do zero: use `game-design-planning` e `core_loop_statement`
- para implementar runtime: use `sgdk-runtime-coder`
- para validar so arte: use `visual-excellence-standards`
- para validar so audio: use `xgm2-audio-director`

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/mechanic_contract.schema.json`
2. `tools/sgdk_wrapper/schemas/mechanic_validation_report.schema.json`
3. `tools/sgdk_wrapper/.agent/references/mechanic_role_catalog.json`
4. `doc/11-gdd.md`
5. `doc/13-spec-cenas.md`
6. `tools/sgdk_wrapper/.agent/references/head_metric_reference.json` quando a mecanica envolver inimigo
7. `tools/sgdk_wrapper/.agent/references/enemy_ai_role_catalog.json` quando a mecanica for combat

## Entrada minima

- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`
- `mechanic_contract.json` ou bloco equivalente no GDD/spec
- player kit declarado
- target scene/scope

## Saida minima

- `mechanic_validation_report.json` (status por mecanica + 5 leis + 5 pilares)
- `numeric_attribute_table.json` (HP:1420/2500, +42 dano, ranges, formulas)
- `mechanic_juice_map.json` (qual feedback visual/SFX/audio cada mecanica dispara)

## 5 Leis Fundamentais aplicadas

| Lei | Pergunta canonica | Bloqueio se falhar |
|-----|-------------------|---------------------|
| 1 - Agencia | input latency <= 1 frame? cancel window declarada? | `mechanic_no_skill_expression` |
| 2 - Feedback/Juice | toda acao tem resposta visual + SFX + resposta de camera adequada ao impacto? | `mechanic_feedback_missing` |
| 3 - Fluxo | tutorial invisivel? curva de dificuldade dosada? save points? | `mechanic_underused` |
| 4 - Consistencia | contrato de cor/forma respeitado? "vermelho = perigo" mantido? | (sem bloqueio direto; reporta em feedback_model) |
| 5 - Recompensa | drop/chave proporcional ao desafio? gating por drop raro? | `mechanic_no_goal_link` |

## 5 Pilares de Validacao

| Pilar | Pergunta canonica | Bloqueio se falhar |
|-------|-------------------|---------------------|
| 1 - Espaco | ha espaco no mapa para uso repetido da mecanica? | `mechanic_underused` (se reuse_count < min_reuses) |
| 2 - Gatilho | existem elementos/atributos que sirvam de trigger? | `mechanic_no_goal_link` |
| 3 - Desafio | ha desafio real (cognitivo, fisico, social ou mixed)? | `mechanic_no_skill_expression` |
| 4 - Limitacao | regras de limitacao estao claras? | (sem bloqueio direto; reporta em rules_and_limits) |
| 5 - Probabilidade | se nao deterministico, success_rate_percent declarada? | `mechanic_probability_undeclared` |

## Especificidade Numerica

Toda mecanica core deve declarar atributos com valores numericos, nunca subjetivos. Exemplo:

```json
{
  "double_jump": {
    "apex_height_px": 96,
    "horizontal_drift_px": 24,
    "input_window_after_landing_ms": 80,
    "cooldown_ms": 0,
    "energy_cost": 0,
    "combo_with_dash_horizontal_boost_px": 32
  }
}
```

Substituir "alto dano" por "+42 dano fisico" sempre.

## Juices por mecanica

Cada mecanica core deve ter pelo menos 3 layers de feedback:
- visual (flash, smear, palette shift, sprite replacement)
- audio (SFX prioritario ou voice bite)
- camera/haptic (shake, screen freeze, impulse, focus shift ou nenhuma resposta quando justificado)

## Bloqueios emitidos

- `mechanic_contract_missing` (tecnico)
- `mechanic_orphaned` (criativo)
- `mechanic_underused` (criativo)
- `mechanic_no_goal_link` (criativo)
- `mechanic_no_skill_expression` (criativo)
- `mechanic_input_ambiguous` (tecnico)
- `mechanic_probability_undeclared` (tecnico)
- `mechanic_feedback_missing` (criativo)
- `mechanic_test_scenario_missing` (tecnico)

## Passa quando

- cada mecanica core tem `versatility_cases >= 3`
- cada mecanica core tem `level_design_reuse_plan.min_reuses >= 3`
- cada mecanica core tem `combination_map >= 1`
- cada mecanica com `probability_model.type != deterministic` tem `success_rate_percent`
- cada mecanica com mesmo botao mapeado para acoes distintas tem `disambiguation_rule`
- `mechanic_5_laws_compliance` tem 5 status: agency, feedback, flow, consistency, reward

## Handoff

- para `level-design-canonical`: entregar `mechanic_validation_report.json` + lista de core mechanics
- para `enemy-design-canonical`: entregar `numeric_attribute_table.json` para consulta de damage_against_enemy_role
- para `xgm2-audio-director`: entregar `mechanic_juice_map.json` para eventos de audio
- para `sgdk-runtime-coder`: entregar `mechanic_validation_report.json` + juice map para implementacao

## Anti-padroes

- mecanica "legal" sem teste de jogo
- "core" sem versatility_cases, sem reuse plan, sem combination_map
- atributo subjetivo ("muito forte", "fraco", "ok") em vez de numero
- probabilidade "aleatoria" sem success_rate_percent
- feedback so visual sem SFX correlato
- teste de cenario unico sem variacao

## Senior Competencies

- `numeric_discipline` - tudo eh numero, nada eh adjetivo
- `law_compliance_audit` - audita cada mecanica contra as 5 leis
- `pillar_completeness` - audita cada mecanica contra os 5 pilares
- `juice_consistency` - garante feedback multimodal (visual + audio + camera)
- `camera_feedback_discipline` - camera reforca impacto ou legibilidade, mas nao vira ruido padrao
- `rng_modeling` - toda probabilidade documentada com taxa e seed strategy
