---
name: multi-plane-composition
description: Use quando a tarefa envolver composicao de cena em profundidade para Mega Drive, incluindo BG_A, BG_B, foreground composicional, parallax, scene_slice, paired_bg e promocao de traducao offline para prova em ROM. Nao use para sprite sheet isolada ou para build/runtime puro sem decisao visual de planos.
---

# Multi-Plane Composition

Esta skill existe para impedir que cena multi-plano vire soma cega de layers ou compressao de ilustracao inteira.

## Ler antes de agir

1. `doc/03_art/09_multi_plane_composition_standards.md`
2. `doc/03_art/04_art_translation_curation_protocol.md`
3. `doc/03_art/02_visual_feedback_bank.md`
4. `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`

## Quando usar

- traducao de `scene_slice`
- decisao entre `BG_A`, `BG_B`, `midground_layer` e `foreground_layer`
- paired background review
- parallax por planos
- compare entre curadoria offline e prova em ROM
- decisao entre multi-plano real, `compare_flat` ou foreground via sprite graft

## Entregas obrigatorias

- `depth_role_map`
- `composition_schema`
- `layer_plan`
- `shared_canvas_contract`
- `hardware_budget_review`
- `delivery_findings`

## Regras canonicas

- `BG_B` carrega atmosfera e profundidade distante
- `BG_A` carrega estrutura principal sem repetir o fundo inteiro
- foreground composicional nao e actor sprite por default
- toda layer semantica compartilha a mesma base espacial
- composicao e por alpha/matte controlado, nao por soma bruta
- promocao para ROM exige budget honesto e pode pedir `compare_flat`

## Gates de aprovacao

- `depth_separation`
- `plane_role_clarity`
- `scene_readability`
- `budget_fit`
- `rom_strategy_declared`

## Anti-padroes

- BG_A e BG_B contando a mesma historia visual
- foreground tratado como ruido ou sprite compacto sem motivo
- paired_bg aprovado so porque existe camada dupla
- explodir tiles unicos e ainda chamar de prova pronta
- third plane imaginario em vez de decisao real de `WINDOW`, sprite graft ou compare flat

## Integracao

- combinar com `art-translation-to-vdp` para parsing semantico e traducao offline
- combinar com `megadrive-vdp-budget-analyst` antes de promover para runtime
- combinar com `megadrive-elite` quando a decisao sair do laboratorio e entrar em `MAP`, `IMAGE`, scroll, H-Int ou sprite graft real
