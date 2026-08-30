---
name: racing-sports-adventure-game-design
description: Use somente com opt-in explícito para racing_arcade e GDD suficiente; não inferir especialização por nome, código ou palavras soltas.
---

# Racing Sports Adventure Game Design

Orquestrador fino da especialização implementada `racing_arcade`.

## Contrato Operacional

### Entrada minima

- manifesto com opt-in
- GDD com veículos, pistas, modos, IA, HUD e tuning
- schema e validator específicos existentes

### Saida minima

- `racing_arcade_design_contract.json`
- frame data por veículo
- `racing_specialization_report.json`

### Passa quando

- specialization id é `racing_arcade`
- contrato valida
- road physics só é claim quando declarado
- pistas, itens e veículos são dimensionados pelo GDD e budgets reais

### Handoff para proxima etapa

- `systems-mechanics-validator`, `level-design-canonical`
- `camera-system-sgdk`, `hscroll` via `shadow-highlight-scroll-fx` quando aplicável
- `megadrive-vdp-budget-analyst`, `tdd-authoring`, `sgdk-runtime-coder`

## Regras

- Sports e adventure permanecem deferred sem implementação própria.
- Não usar contagem fixa de pistas ou slots como limite universal.
- Ativação é humana e explícita.
