---
name: strategy-game-design
description: Use somente com opt-in explícito para strategy_tower_defense e GDD suficiente; não inferir especialização por nome, código ou palavras soltas.
---

# Strategy Game Design

Orquestrador fino da especialização implementada `strategy_tower_defense`.

## Contrato Operacional

### Entrada minima

- manifesto com opt-in
- GDD com grid, torres, inimigos, ondas, economia e modos
- schema e validator específicos existentes

### Saida minima

- `strategy_tower_defense_design_contract.json`
- frame data por torre
- `strategy_specialization_report.json`

### Passa quando

- specialization id é `strategy_tower_defense`
- contrato valida
- quantidade de torres, ondas e entidades deriva de UX e budgets
- input, HUD, save e pior quadro possuem owners

### Handoff para proxima etapa

- `systems-mechanics-validator`, `entity-polymorphism-architect`
- `input-system-sgdk`, `megadrive-vdp-budget-analyst`
- `xgm2-audio-director`, `tdd-authoring`, `sgdk-runtime-coder`

## Regras

- Tactical e demais variantes ficam deferred sem schema/validator próprios.
- Não usar wave count ou tower count fixos como limites universais.
- Ativação é humana e explícita.
