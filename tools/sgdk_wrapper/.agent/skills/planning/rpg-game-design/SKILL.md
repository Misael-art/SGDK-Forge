---
name: rpg-game-design
description: Use somente com opt-in explícito para rpg_turn_based_jrpg e GDD suficiente; não inferir especialização por nome, código ou palavras soltas.
---

# RPG Game Design

Orquestrador fino da especialização implementada `rpg_turn_based_jrpg`.

## Contrato Operacional

### Entrada minima

- manifesto com opt-in
- GDD com party, combate, progressão, equipamentos, encontros e save
- schema e validator específicos existentes

### Saida minima

- `rpg_turn_based_jrpg_design_contract.json`
- frame data por membro
- `rpg_specialization_report.json`

### Passa quando

- specialization id é `rpg_turn_based_jrpg`
- contrato valida
- party, inventário, magias e encontros são dimensionados por UX, save,
  sprites, VRAM e pior quadro do projeto
- runtime e TDD recebem contratos sem constantes arbitrárias

### Handoff para proxima etapa

- `systems-mechanics-validator`, `character-design`, `sprite-animation`
- `megadrive-vdp-budget-analyst`, `xgm2-audio-director`
- `tdd-authoring` e `sgdk-runtime-coder`

## Regras

- `rpg_action_topdown` e demais variantes ficam deferred sem implementação.
- Nenhuma contagem de conteúdo é teto universal de hardware.
- Ativação é humana e explícita.
