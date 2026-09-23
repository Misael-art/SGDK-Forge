---
name: platformer-puzzle-game-design
description: Use somente com opt-in explícito para platformer_precision_2d e GDD suficiente; não inferir especialização por nome, código ou palavras soltas.
---

# Platformer Puzzle Game Design

Orquestrador fino da especialização implementada `platformer_precision_2d`.

## Contrato Operacional

### Entrada minima

- manifesto com opt-in
- GDD com movimento, hazards, segmentos, collectibles e modos
- schema e validator específicos existentes

### Saida minima

- `platformer_precision_2d_design_contract.json`
- frame data por segmento
- `platformer_specialization_report.json`

### Passa quando

- specialization id é `platformer_precision_2d`
- contrato valida
- câmera, colisão e movimento crítico possuem owners
- quantidade de níveis e conteúdo deriva do GDD, save encoding e budgets

### Handoff para proxima etapa

- `systems-mechanics-validator`, `level-design-canonical`
- `camera-system-sgdk`, `collision-system-architect`
- `sprite-animation`, `megadrive-vdp-budget-analyst`
- `tdd-authoring` e `sgdk-runtime-coder`

## Regras

- Metroidvania e puzzles permanecem deferred sem schema/validator próprios.
- Não transformar recomendação de conteúdo em teto de hardware.
- Ativação é humana e explícita.
