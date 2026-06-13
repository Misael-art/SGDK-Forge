---
name: tdd-authoring
description: Use quando a tarefa envolver redacao do Technical Design Document (TDD) para um projeto SGDK: arquitetura, FSM de cena, memory pool, VBlank/DMA ownership, H-Int ownership, audio ownership, save scope, region timing, ROM mastering, risk mitigation. Emite tdd_contract.json, tdd_document.md, state_fsm_map, memory_pool_map, runtime_ownership_map. Obrigatorio para produto piloto, vertical slice ou ready_for_aaa. Nao use para projetar gameplay (use systems-mechanics-validator) ou para implementar runtime (use sgdk-runtime-coder).
---

# TDD Authoring

Esta skill existe para impedir que arquitetura tecnica vire decisao improvisada em PR. Todo produto jogavel precisa de TDD fechado antes de runtime.

## Quando usar

- projeto piloto, vertical slice, ready_for_aaa
- reseed de produto que perdeu coerencia tecnica
- adicao de sistema novo (save, multiplayer, replay) que requer ownership
- audit pre-AAA de TDD contra hardware real

## Nao use

- para projetar gameplay: use `systems-mechanics-validator` antes
- para projetar fases: use `level-design-canonical` antes
- para projetar inimigos: use `enemy-design-canonical` antes
- para implementar runtime: use `sgdk-runtime-coder` depois
- para laboratorio tecnico isolado sem cenario de produto: TDD nao e obrigatorio, mas o documento ainda ajuda

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/tdd_contract.schema.json`
2. `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`
3. `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md` (especialmente `references/sgdk_211_api_reality.json`)
4. `tools/sgdk_wrapper/.agent/skills/code/xgm2-audio-director/SKILL.md`
5. `tools/sgdk_wrapper/.agent/architecture/scene-state-architect/SKILL.md`
6. `mechanic_validation_report.json` (para state_fsm_map)
7. `level_blueprint.json` (para state_fsm_map por cena)
8. `enemy_design_report.json` (para memory_pool_map)
9. `tools/sgdk_wrapper/schemas/audio_architecture_card.schema.json` quando audio senior
10. `sdk/sgdk-2.11/inc/` para validar API antes de qualquer decisao

## Entrada minima

- GDD
- spec de cenas
- route_decision_record
- runtime_target (`pilot`, `vertical_slice`, `ready_for_aaa`)

## Saida minima

- `tdd_contract.json` (formato canonico machine-readable)
- `tdd_document.md` (formato narrativo para humanos)
- `state_fsm_map` (mapa de FSM por cena)
- `memory_pool_map` (pools de objetos)
- `runtime_ownership_map` (VBlank/DMA/H-Int/Audio)

## Secoes Obrigatorias

### 1. Arquitetura Logica

- engine target (SGDK 2.11 fixo)
- linguagem (C)
- padroes: FSM, pooling, observer, ECS (raro no Mega Drive)
- como entidades se comunicam

### 2. Scene Manager Scope

- topology: `linear`, `hub`, `free`, `stacked`
- deterministic: `true` (obrigatorio)
- transition_handling: fade, cut, palette swap
- boot_to_first_scene_ms_target: < 3000ms tipico

### 3. Input Abstraction Scope

- abstraction_layer: nome do modulo (ex: `input_director.c`)
- latency_target_ms: < 16 (1 frame NTSC)
- supported_devices: 3-button pad, 6-button pad
- rebind_support: tipicamente false no Mega Drive (pouca memoria)

### 4. State FSM Map

- 1 entrada por cena jogavel
- states[]: minimo 2
- transitions[]: com trigger explicito
- `scene_id` deve casar com `level_blueprint.json.scope_id`

### 5. Memory Pool Map

- 1 entrada por pool
- type: sprite, enemy, projectile, particle, sfx_channel, ui, string_buffer
- size: limite estatico
- owner: arquivo C responsavel
- lifecycle: alloc/free strategy

### 6. VBlank/DMA Ownership

- vblank_owner: arquivo/funcao
- dma_owners: lista
- max_pending_dma: limite
- safety_pattern: como garantir DMA fora de VBlank nao acontece

### 7. H-Int Ownership

- h_int_in_use: true/false
- singleton_owner: arquivo/funcao (quando h_int_in_use=true)
- slices: lista de line hooks

### 8. Audio Ownership

- driver: `xgm2`, `z80_custom`, `pwm_only`, `psg_only`, `hybrid`
- channel_owners: lista
- sample_rate_hz: tipico 14000-22000
- adaptive_music_state_map_ref: caminho para `adaptive_music_state_map.json`

### 9. Save Scope

- `required`, `optional`, `none`, `not_applicable`
- quando `required`:
  - `sram_magic` (4 bytes hex)
  - `sram_version` (u8)
  - `sram_checksum` (xor, crc16, crc32)
  - `size_bytes`

### 10. Region/Timing Scope

- region: `NTSC`, `PAL`, `both`, `not_applicable`
- frame_budget_ms: 16.67 (NTSC) ou 20.00 (PAL)
- justification: quando `not_applicable`

### 11. ROM Mastering Scope

- size_target_kb: limite
- header_validated: true (sempre)
- checksum_validated: true (sempre)
- sram_size_bytes: derivado de save_contract

### 12. Risk Mitigation Table

- risk_id, risk, mitigation, severity (low/medium/high/critical)
- cobre: VRAM overflow, DMA starvation, sprite limit, palette collision, audio channel clash, save corruption

## Bloqueios emitidos

- `tdd_missing_for_product` (tecnico) - quando `product_status != technical_lab_validated` e TDD ausente
- `scene_fsm_missing` (tecnico) - state_fsm_map vazio ou com 1 estado so
- `memory_pool_missing` (tecnico) - memory_pool_map vazio
- `runtime_ownership_missing` (tecnico) - vblank_owner ou audio_ownership ausentes
- `input_contract_missing_for_product` (tecnico)
- `region_timing_missing_for_product` (tecnico)

## Passa quando

- produto piloto, vertical_slice_candidate ou ready_for_aaa: TDD obrigatorio
- `save_scope=required` tem `sram_magic`, `sram_version`, `sram_checksum`
- `region_timing_scope.region` declarado
- `state_fsm_map` cobre todas as cenas de `level_blueprint.json`
- `runtime_ownership_map` declara owner unico de VBlank, DMA, audio
- `risk_mitigation_table` cobre pelo menos 3 riscos (VRAM, DMA, audio)

## Handoff

- para `megadrive-vdp-budget-analyst`: entregar `memory_pool_map` + `runtime_ownership_map` para budget
- para `scene-state-architect`: entregar `state_fsm_map` para modularidade
- para `sgdk-runtime-coder`: entregar TDD completo para implementacao
- para `rom-mastering`: entregar `rom_mastering_scope` + `save_scope`
- para `xgm2-audio-director`: entregar `audio_ownership` + referencia ao `adaptive_music_state_map`

## Anti-padroes

- TDD sem memory_pool_map (nada declara onde alocar)
- TDD sem runtime_ownership (quem cuida do VBlank? quem dispara DMA?)
- TDD sem region_timing (frame budget varia NTSC vs PAL)
- TDD com `save_scope=required` mas sem sram_magic
- TDD com FSM de 1 estado so (nao e FSM, e loop)
- TDD com risk_mitigation_table vazia (nada planejado, tudo improvisa depois)
- TDD com referencias a API SGDK 1.60 (migrado errado)

## Senior Competencies

- `state_machine_discipline` - FSM explicita por cena, sem estado magico
- `pool_planning` - limite estatico declarado, nao `malloc/free`
- `ownership_uniqueness` - cada recurso (VBlank, DMA, audio, palette) tem 1 dono
- `save_invariants` - magic + version + checksum sempre que save_scope=required
- `region_awareness` - NTSC vs PAL tem budget de frame diferente
- `risk_proactive_listing` - mitigation table lista ANTES do problema
