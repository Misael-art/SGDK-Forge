---
name: forward-kinematics-rigging
description: Use quando a tarefa envolver tentaculos, correntes, bracos, cabelo, caudas ou bosses articulados no Mega Drive usando cadeias de juntas, trigonometria em fix16 e budget real de scanline. Nao use para animacao comum frame-a-frame, IK completo ou rig 3D generico.
---

# Forward Kinematics Rigging

Esta skill existe para o gap puro de articulacao procedural no workspace.

## Nao substitui outras skills

- `sprite-animation`
  - continua dona do ciclo frame a frame
- `sgdk-runtime-coder`
  - continua dono da integracao SGDK, loop e scene setup
- `megadrive-vdp-budget-analyst`
  - continua dono do veredito de scanline, VRAM e worst-frame

## Ler antes de agir

1. `doc/05_technical/93_16bit_hardware_mastery_registry.json`
2. `doc/05_technical/92_sgdk_engine_pattern_registry.json`
3. `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/references/sgdk_211_api_reality.json`
4. `sdk/sgdk-2.11/inc/fixmath.h`
5. codigo ou tabela de trigonometria relevante do projeto

## Quando usar

- boss com bracos segmentados
- tentaculos, correntes, chicotes ou cabos articulados
- partes de sprite ligadas por hierarquia `parent -> child`
- rigs que precisam reagir a posicao ou angulo em runtime

## Saidas obrigatorias

- `joint_schema`
- `topology_order`
- `fixed_point_math_plan`
- `scanline_budget_review`
- `blastem_proof_plan`
- `delivery_findings`

## Regras canonicas

- usar somente `fix16` / `fix32`
- seno e cosseno DEVEM vir de LUT ou helper equivalente ja validado
- ordem de update DEVE ser topologica: pai antes de filho
- cada junta DEVE declarar custo de sprite ou metasprite
- cadeia articulada NAO pode ser aprovada sem medir o pior quadro em scanline
- IK completo fica fora de escopo

## Senior Competencies

- `joint chain math`
  - offsets locais, propagacao de angulo e posicao global
- `LUT-driven rotation`
  - nada de `float`, nada de trigonometria direta cara
- `boss articulation tradeoff`
  - quando usar joint chain e quando voltar para frame pre-renderizado
- `scanline-aware rigging`
  - articulacao bonita que ainda cabe no VDP

## Anti-padroes

- recalcular trigonometria pesada por frame sem LUT
- usar `float` ou `double`
- atualizar filho antes do pai
- aprovar cadeia inteira sem medir pior scanline
- usar articulacao procedural quando uma animacao simples resolver melhor

## Integracao

- combinar com `sprite-animation` para preparar pivots e partes
- combinar com `sgdk-runtime-coder` para integrar no loop e no scene update
- combinar com `megadrive-vdp-budget-analyst` antes de aprovar em ROM
