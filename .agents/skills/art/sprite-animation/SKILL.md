---
name: sprite-animation
description: Use quando a tarefa envolver desenho, traducao, revisao, recorte ou validacao de sprite sheets e ciclos de animacao para Mega Drive. Cobre timing em VBlank, pivot, massa, economia de VRAM por frame, ordem canonica de bandas, e criterios de aprovacao em ROM. Nao use para composicao de cenario ou design geral de roster sem foco na animacao.
---

# Sprite Animation

Esta skill existe para garantir que animacao de sprite no Mega Drive seja:

- legivel frame a frame
- estavel por pivot e massa
- economica em VRAM
- coerente com o genero
- pronta para integracao SGDK

## Ler antes de agir

1. `doc/03_art/07_sprite_animation_standards.md`
2. `doc/03_art/02_visual_feedback_bank.md`
3. `tools/sgdk_wrapper/.agent/skills/art/megadrive-pixel-strict-rules/SKILL.md`
4. `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md` quando houver risco de budget

## Quando usar

- criacao ou traducao de `sprite_sheet`
- revisao de ciclo `idle`, `walk`, `run`, `jump`, `attack`, `hurt`, `death`
- normalizacao de frames por pivot
- validacao de timing, massa e reuso
- integracao de sprite sheet em `.res`

## Entregas obrigatorias

- `animation_spec`
- `pivot_policy`
- `frame_envelope`
- `timing_table`
- `tile_reuse_summary`
- `delivery_findings`

## Regras canonicas

- o pivot e definido uma vez e nao flutua dentro do ciclo
- o frame envelope e unico por sequencia
- timing e em VBlank, nunca em intuicao vaga
- anticipation e follow-through sao obrigatorios em acoes
- flip horizontal e hardware, nao duplicacao de sheet
- frame bonito em zoom nao vale se falhar em 320x224 nativo

## Gates de aprovacao

- `mass_consistency`
- `pivot_stability`
- `timing_feel`
- `frame_economy`
- `readability_at_native`
- `rom_playback` quando a iteracao chegar ao benchmark

## Anti-padroes

- sheet com frames desalinhados
- mesma duracao para todos os frames
- golpe sem anticipation
- golpe sem follow-through
- duplicar direcao esquerda/direita em PNG
- aprovar animacao sem calcular tiles unicos do ciclo

## Integracao

- combinar com `character-design` quando a tarefa mexer na identidade do personagem
- combinar com `art-translation-to-vdp` quando a sheet vier de uma fonte high-res ou editorial
- combinar com `megadrive-elite` quando a tarefa entrar em runtime, `.res`, callbacks ou troca de animacao em C
