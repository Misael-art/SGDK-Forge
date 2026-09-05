---
prd_id: PRD-02
title: Definition Of Done
status: seed
applies_to: [prototype, AAA, stable, release, delivery]
unlocks: [delivery_gate, ready_for_aaa]
owner: agent
last_validated: null
---

# Definition Of Done

## Prototype Playable

- `out/rom.bin` existe
- build executado via wrapper central
- BlastEm abriu a ROM
- controles minimos funcionam
- `doc/10-memory-bank.md` e changelog refletem o estado real

## AAA / Stable / Release

So pode ser declarado quando todos existirem, estiverem frescos e sem blocker:

- `production_runtime_contract`
- `scene_manager_contract`
- `input_abstraction_contract`
- `save_system_contract` quando `persistence_scope=required` ou `sram_policy!=none`
- `region_timing_contract`
- `asset_optimization_report`
- `rom_mastering_report`
- `code_review_report`
- `ci_gate_report` ou `local_ci_gate_report`
- `visual_delivery_gate_report` limpo
- `scene_regression_report` com baseline quando houver entrega visual AAA
- screenshot BlastEm da cena correta
- `visual_vdp_dump.bin` quando AAA ou quando houver suspeita visual

## Status Maximo Permitido

- com asset critico `needs_review`: `visual_gate_blocked`
- com runtime sem fonte visual premium: `prototype_playable`
- com evidencia stale: `blocked_stale_evidence`
- com PRD obrigatorio em `seed`: `documentado` ou `prototype_playable`, nunca AAA
