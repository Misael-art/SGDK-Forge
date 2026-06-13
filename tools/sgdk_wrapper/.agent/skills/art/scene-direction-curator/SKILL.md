---
name: scene-direction-curator
description: Use quando um cenario, fase, setpiece, boss arena, bioma, abertura ou showcase visual precisa decidir se sera minimal, competente, monumental ou signature-only antes da traducao e do runtime SGDK.
---

# Scene Direction Curator

Esta skill decide se um cenario sera apenas funcional ou se deve virar um ator dramatico da cena. Ela nao substitui `multi-plane-composition`: ela escolhe a intencao monumental, os arquetipos tecnicos e os cards que a composicao, budget e runtime precisam consumir.

## Ler antes de agir

1. `tools/sgdk_wrapper/.agent/references/scene_archetype_catalog.json`
2. `tools/sgdk_wrapper/.agent/references/art_style_catalog.json`
3. `doc/11-gdd.md`
4. `doc/13-spec-cenas.md`
5. `art_direction_decision_record` quando existir
6. `depth_role_map`, `composition_schema`, `layer_plan` e `shared_canvas_contract`
7. `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md`
8. `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`

## Quando usar

- cena com `scene_profile=aaa_layered`, `boss_arena`, `showcase`, `signature_moment`, `biome_transition`, `shmup_stage`, `racing`, `water`, `lava`, `sky`, `alien_ecology`, `cutscene` ou pedido de "cenario monumental"
- projeto que cita Sonic 2, Shinobi III, Alien Soldier, Super Metroid, Thunder Force, Donkey Kong Country, Castlevania ou efeitos de Mode 7 como referencia de impacto
- qualquer promessa de parallax extremo, line scroll, agua, calor, nevoa, godrays, destruicao, background vivo, pseudo-3D, palette cycling ou palco narrativo

## Perfis de saida

- `minimal`: uma cena funcional. Sem promessa de espetaculo.
- `competent`: dois ou tres planos, boa leitura, parallax simples, sem risco de runtime.
- `monumental`: pelo menos uma tecnica assinada com papel de gameplay/narrativa e budget dedicado.
- `signature_only`: efeito caro, raro ou experimental. Exige fallback, budget e possivel experimental override.

## Artefatos obrigatorios

### `scene_direction_record`

Campos minimos:

```yaml
schema_version: 1
scene_id: string
scene_role: gameplay | boss_arena | cutscene | title | menu | transition | showcase
selected_profile: minimal | competent | monumental | signature_only
selected_archetype_id: string
catalog_path: tools/sgdk_wrapper/.agent/references/scene_archetype_catalog.json
auto_selected: true | false
confidence: 0.0-1.0
confidence_threshold: 0.65
scene_narrative_function: risk | wonder | speed | isolation | scale | threat | transition | mood
gameplay_visual_link: string
top_candidates:
  - archetype_id: string
    score: number
    why_fit: string
    risks: string
rejected_candidates:
  - archetype_id: string
    reason: string
signature_techniques:
  - technique_id: string
fallback_profile: string
mode7_claim_redirected: true | false
budget_preconditions:
  vram_pressure: low | medium | high
  cpu_pressure: low | medium | high
  h_int_required: true | false
blocking_statuses: []
```

### `parallax_layer_contract`

Use quando o perfil for `monumental` e houver `parallax_extreme` ou `line_scroll`.

Campos minimos:

- `layers[]`: semantic_role, plane, scroll_ratio, line_scroll_enabled, owner
- `scroll_ratio_set`: ex. 0.125x, 0.25x, 0.5x, 1.0x
- `line_scroll_table_size_bytes`
- `seam_policy`
- `reset_on_scene_exit`
- `worst_frame_cost_estimate`
- `measurement_level`

### `palette_cycle_decision_card`

Use quando houver agua, lava, neon, ceu, flash, bioluminescencia ou ciclo de clima.

Campos minimos:

- `cycles[]`: cram_slot_range, cadence_frames, palette_owner, narrative_purpose
- `interaction_with_shadow_highlight`
- `ui_and_sprite_conflict_policy`
- `teardown_plan`

### `raster_fx_ownership_map`

Use quando houver H-Int, line scroll, heat, water, palette split, pseudo-3D ou raster UI.

Campos minimos:

- `single_owner`
- `fx_chain[]`: scanline_range, effect_class, tables, update_timing
- `worst_case_scanline_budget_us`
- `vblank_update_cost`
- `reset_on_scene_exit`
- `fallback_if_owner_conflict`

### `background_ecology_card`

Use quando o cenario precisa parecer vivo: plantas pulsando, lava borbulhando, naves explodindo, luzes, organismos, maquinas, cidade ou mar.

Campos minimos:

- `ecology_loops[]`: element, gameplay_role, cadence, palette_or_tile_owner
- `event_hooks[]`: trigger, visual_response, duration_frames
- `tile_mutation_policy`
- `palette_domain`
- `decorative_only_risk`
- `teardown_plan`

## Regras canonicas

- "Mode 7" em Mega Drive e um blocker semantico. Redirecione para `pseudo3d_road_stack`, `line_scroll_floor`, `zmap_road`, `palette_depth_bands` ou paineis pre-renderizados.
- Cenario monumental precisa de funcao: risco, maravilhamento, velocidade, isolamento, escala, ameaca, transicao ou leitura de rota.
- Parallax sem funcao vira `decorative_only_blocked` em AAA.
- Background ou layer sheet nao nasce isolado: precisa declarar camera,
  profundidade, leitura do sprite, interacoes de gameplay e supervisao do art
  director em `art_gameplay_direction_gate`.
- H-Int e raster FX possuem owner unico. Segundo owner sem chain declarada gera `raster_fx_owner_collision`.
- Palette cycling nao pode disputar slots com jogador, HUD, FX de dano ou Shadow/Highlight sem `palette_cycle_decision_card`.
- `signature_only` exige fallback e budget antes de runtime.
- `monumental` em `prototype_playable` exige confirmacao humana ou rebaixamento para `competent`, salvo pedido explicito de showcase.
- Se o pior quadro nao cabe, o perfil e rebaixado; nao empobreca silenciosamente e continue chamando de monumental.

## Blockers

- `scene_direction_undeclared`
- `archetype_catalog_not_consulted`
- `monumental_promised_without_budget`
- `decorative_only_blocked`
- `mode7_claim_on_megadrive`
- `raster_fx_owner_collision`
- `palette_cycle_ownership_conflict`
- `background_ecology_unbounded`
- `signature_only_without_fallback`

## Contrato Operacional

### Entrada minima

- `doc/11-gdd.md` ou briefing com fantasia e genero
- `doc/13-spec-cenas.md` ou cena alvo
- `art_direction_decision_record` quando existir
- `depth_role_map`, `composition_schema`, `layer_plan` e `shared_canvas_contract`
- `scene_archetype_catalog.json`
- alvo de entrega: lab, prototype_playable, AAA, stable, release ou delivery

### Saida minima

- `scene_direction_record`
- `scene_signature_techniques`
- `fallback_profile`
- `art_gameplay_direction_gate` quando a iteracao produzir background plate,
  layer sheet, foreground, setpiece visual, boss arena, title/menu scenic
  background ou qualquer cenario autoral critico
- `parallax_layer_contract` quando aplicavel
- `palette_cycle_decision_card` quando aplicavel
- `raster_fx_ownership_map` quando aplicavel
- `background_ecology_card` quando aplicavel
- `delivery_findings` com blockers ou rebaixamento honesto

### Passa quando

- o catalogo de arquetipos foi consultado
- o perfil da cena foi declarado como minimal, competent, monumental ou signature_only
- tecnicas assinadas possuem cards e donos quando aplicavel
- Mode 7 foi redirecionado para tecnica real de Mega Drive quando aparecer como referencia
- cenario monumental tem funcao de gameplay ou narrativa, nao apenas decoracao
- fallback e rebaixamento estao documentados antes de runtime
- budget preliminar nao contradiz o perfil escolhido
- `art_gameplay_direction_gate` passa quando a cena gerar background/layers
  criticos; sem isso, o cenario fica `needs_review` mesmo que a imagem seja
  bonita

### Handoff

- para `art-translation-to-vdp`: entregar profile, archetype, signature techniques e cards de cena
- para `visual-excellence-standards`: entregar funcao narrativa, anti-padroes e risco decorative-only
- para `megadrive-vdp-budget-analyst`: entregar cards com custo de pior quadro e ownership
- para `sgdk-runtime-coder`: entregar owner de H-Int/CRAM/scroll/tiles, reset e fallback
