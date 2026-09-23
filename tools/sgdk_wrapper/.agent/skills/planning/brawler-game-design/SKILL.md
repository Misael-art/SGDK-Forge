---
name: brawler-game-design
description: Use somente com opt-in explícito para brawler_belt_scroll e GDD suficiente; não inferir especialização por nome, código ou palavras soltas.
---

# Brawler Game Design

Orquestrador fino da especialização implementada `brawler_belt_scroll`.

## Contrato Operacional

### Entrada minima

- `genre_specialization_manifest.json` com opt-in
- GDD com roster, combate, inimigos, pickups e fases
- schemas e validator específicos existentes

### Saida minima

- `brawler_belt_scroll_design_contract.json`
- frame data por archetype
- `brawler_specialization_report.json`
- anexos TDD apenas quando solicitados

### Passa quando

- specialization id é `brawler_belt_scroll`
- contrato valida no schema específico
- mechanics, animation, budget, audio e runtime têm owners delegados
- números de roster, fases e ondas vêm do GDD e do budget, não da skill

### Handoff para proxima etapa

- `systems-mechanics-validator` para combate
- `enemy-design-canonical` para archetypes
- `sprite-animation`, `megadrive-vdp-budget-analyst`, `xgm2-audio-director`
- `tdd-authoring` e `sgdk-runtime-coder`

## Regras

- `brawler_run_and_gun_2d` e `brawler_run_and_gun_topdown` ficam deferred até
  possuírem schema, validator e testes próprios.
- A skill delega; não duplica contratos especialistas.
- Ativação é humana e explícita.
