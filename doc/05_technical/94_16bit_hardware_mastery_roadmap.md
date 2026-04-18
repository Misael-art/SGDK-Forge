# 94 - 16-bit Hardware Mastery Roadmap

Status: `implementation_backlog`

---

## Objetivo

Dar a outra IA um roteiro fechado para elevar o agente de dominio parcial para pericia senior absoluta nas tecnicas hardware-level relevantes para Mega Drive.

Este roadmap assume:

- `93_16bit_hardware_mastery_matrix.md` como mapa humano
- `93_16bit_hardware_mastery_registry.json` como indice machine-readable
- `BENCHMARK_VISUAL_LAB` como unico laboratorio oficial

## Regra de progresso

Nenhuma tecnica sobe de estado sem passar por:

1. skill owner explicito
2. regra ou doc clara
3. artefato reproduzivel
4. build no laboratorio
5. evidence bundle em BlastEm
6. aprovacao humana

## Trilhas canonicas de maestria

### 1. Raster Control

- `h_int_control_plane`
- `line_scrolling`
- `column_scrolling`
- `hint_palette_blending`
- `procedural_raster_glitch_suite`

### 2. Display Architecture

- `window_plane_static_hud`
- `interlaced_448_display_mode`

### 3. Sprite Overflow Engineering

- `sprite_temporal_multiplexing`
- `sprite_midframe_sat_reuse`
- `bg_b_bypassing`
- `priority_split_foreground`

### 4. Pseudo-3D Spectrum

- `pseudo3d_road_stack`
- `software_affine_pseudo3d`

### 5. Surface Mutation and Simulation

- `masked_shadow_highlight_lighting`
- `mutable_tile_decal_mutation`
- `cellular_microbuffer_sim`

## Wave 0 - Auditoria canonica

Entregas:

- manter `93_matrix` e `93_registry` sincronizados
- confirmar dono de skill para cada tecnica
- ligar cada entrada a `lib_case`, `registry_ids` e `benchmark_scene`
- adicionar `operational_policy` e `prerequisite_ids` ao registry

Saida esperada:

- nenhuma tecnica relevante fica sem `owner_skills`
- nenhum gap puro fica escondido como se fosse competencia madura
- `H-Int`, `WINDOW`, `interlaced` e multiplexing deixam de aparecer como categoria misturada

## Wave 1 - Consolidacao do que ja existe

Entregas:

- expandir skills atuais com secao `Senior Competencies`
- unificar linguagem de pericia em:
  - `sgdk-runtime-coder`
  - `megadrive-vdp-budget-analyst`
  - `multi-plane-composition`
  - `visual-excellence-standards`
  - `sprite-animation`
  - `scene-state-architect`
- declarar DMA safety e worst-frame budget como checklist obrigatorio
- registrar `WINDOW` como plano fixo seguro e `window alias` como tecnica separada

Gate:

- nenhuma tecnica parcialmente coberta continua invisivel dentro da skill dona

## Wave 2 - Raster Control e iluminacao

Scenes obrigatorias no `BENCHMARK_VISUAL_LAB`:

- `fx_line_scroll_lab`
- `fx_column_scroll_lab`
- `fx_hint_palette_split_lab`
- `fx_hint_arbiter_lab`
- `fx_shadow_highlight_lab`
- `fx_palette_cycling_lab`
- `fx_procedural_glitch_lab`
- `fx_masked_light_lab`

Entregas:

- `h_int_control_plane` vira competencia formal do agente
- budget lines em `doc/13-spec-cenas.md`
- validation axes preenchidos
- evidence bundle por scene
- `procedural_raster_glitch_suite` nasce como linguagem dramatica formal de `S2.1`
- `masked_shadow_highlight_lighting` nasce como nome honesto para spotlight, lanterna e weak spot de boss em `S2.2`

Gate:

- linha, coluna, split e cycling rodam sem glitch e com budget declarado
- apenas um owner de H-Int fica ativo por scene
- glitch raster continua legivel durante gameplay
- spotlight mascarado nao vende alpha blending nem iluminacao global inexistente

## Wave 3 - Display Architecture e Sprite Overflow Engineering

Scenes obrigatorias:

- `hud_window_plane_lab`
- `display_interlaced_448_lab`
- `fx_sprite_temporal_multiplex_lab`
- `fx_sat_midframe_reuse_lab`
- `boss_bg_b_bypass_lab`
- `priority_split_foreground_lab`

Entregas:

- regra binaria por tecnica:
  - `permitida`
  - `proibida`
  - `fallback`
- `window_plane_static_hud` promovido a competencia formal
- `interlaced_448_display_mode` tratado como `special_scene_only`
- worst-frame budget para scanline pressure

Gate:

- `WINDOW` e `window alias` deixam de ser confundidos
- `interlaced_448` so permanece no core roadmap se provar ganho real contra 224p
- `sprite_midframe_sat_reuse` nao sobe sem prova isolada sem corrupcao

## Wave 4 - Pseudo-3D Spectrum e articulacao

Scenes obrigatorias:

- `pseudo3d_road_lab`
- `pseudo3d_affine_lab`
- `boss_kinematics_lab`

Entregas:

- promover `pseudo3d_road_stack` para `blastem_proven`
- manter `software_affine_pseudo3d` como trilha separada
- criar skill `forward-kinematics-rigging`
- benchmark minimo de tentaculo, corrente ou braco articulado

Gate:

- road-stack e affine software deixam de compartilhar status
- articulacao em `fix16` estavel
- prova em ROM sem queda perceptivel de desempenho

## Wave 5 - Surface Mutation experimental

Scenes obrigatorias:

- `fx_decal_mutation_lab`

Entregas:

- formalizar `mutable_tile_decal_mutation` como trilha experimental de setor local
- exigir `RAM shadow copy`, `mutable tile pool` e politica de persistencia por sala
- provar que a tecnica nao depende de readback livre de `VRAM`
- manter `cellular_microbuffer_sim` bloqueado ate haver prova de mutacao local e dirty upload disciplinado

Gate:

- tiles mutaveis ficam limitados a setores explicitamente damageable
- budget de dirty uploads cabe no pior quadro
- persistencia local nao explode unicidade de tiles
- `cellular_microbuffer_sim` permanece fora do build principal ate benchmark proprio em ilha pequena

## Wave 6 - Audio senior

Scene obrigatoria:

- `audio_xgm2_lab`

Entregas:

- criar skill `xgm2-audio-director`
- provar BGM + 2 SFX + 1 ambiente
- provar `pause`, `resume`, `loop` e ownership de canal

Gate:

- audio deixa de ser categoria ausente do framework

## Wave 7 - Certificacao senior absoluta

Para cada tecnica:

- `lib_case` existe
- scene dedicada existe
- `validation_report` confirma `blastem_gate = true`
- budget esta aprovado
- aprovacao humana esta registrada

Somente entao o `current_status` pode virar `senior_default`.

## Ordem obrigatoria de implementacao

1. consolidar skill owners
2. consolidar benchmark contract
3. promover tecnicas candidatas fortes e suites compostas honestas
4. abrir trilhas experimentais de mutacao local antes de microbuffers celulares
5. abrir skills novas apenas para gaps puros ja aprovados
6. certificar por BlastEm e regressao

## Ordem obrigatoria dos quatro efeitos especulativos

1. `procedural_raster_glitch_suite`
2. `masked_shadow_highlight_lighting`
3. `mutable_tile_decal_mutation`
4. `cellular_microbuffer_sim`

Regra:

- `cellular_microbuffer_sim` nao entra antes de `mutable_tile_decal_mutation`
- nenhum dos quatro sobe sem causa de gameplay e benchmark proprio

## Regressao obrigatoria

Toda wave deve reexecutar:

- checklist das tecnicas ja promovidas
- evidence bundle das scenes correlatas
- leitura do `validation_report`

Falha de regressao:

- rebaixa a tecnica para `candidate_with_evidence` ou `partial`
- nunca manter `senior_default` com falha escondida
