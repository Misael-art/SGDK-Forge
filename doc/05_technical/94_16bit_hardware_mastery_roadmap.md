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

### 6. Scene Flow Architecture

- `contextual_scene_transition_system`
- `scene_transition_card`

### 7. Agent Proficiency Roadmap

- `aaa_agent_proficiency_roadmap`
- `expressive_text_presentation_system`
- `feedback_fx_decision_system`
- `boss_setpiece_design`
- `advanced_tilemap_design`
- `xgm2_audio_architecture`

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
- registrar `scene_transition_card` como contrato obrigatorio para transicoes formais antes de arte/runtime

Gate:

- nenhuma tecnica parcialmente coberta continua invisivel dentro da skill dona

## Wave 1.5 - Transicoes contextualizadas

Scenes futuras no `BENCHMARK_VISUAL_LAB`:

- `scene_transition_lab`

Entregas:

- manter `S3.4 Scene Transition Design` como doutrina integrada, sem skill nova
- validar `scene_transition_card` contra `palette_fade_bridge`, `spatial_scroll_bridge`, `scripted_avatar_bridge`, `tile_mask_mosaic_transition`, `raster_distortion_bridge`, `lighting_state_transition`, `pseudo3d_perspective_bridge` e `meta_cut_bridge`
- exigir `runtime_state_handoff`, `teardown_reset_plan`, `audio_transition_plan`, owner unico de FX e fallback antes do runtime
- tratar `tile_mask_transition_fade`, H-Int wobble/scaling, palette split, pseudo-3D e audio fade como referencias, nao defaults universais

Gate:

- nenhuma transicao avancada sobe sem causa dramatica, budget aprovado, reset simetrico e prova BlastEm
- fallback padrao e `palette_fade_bridge` contextualizado, nao fade preto generico

## Wave 1.6 - Texto narrativo expressivo

Scene futura no `BENCHMARK_VISUAL_LAB`:

- `expressive_text_lab`

Entregas:

- usar `expressive_text_presentation_system` como doutrina S3.5 ja incorporada
- validar `text_presentation_profile` dentro do `ui_decision_card`, sem artefato paralelo
- cobrir `panel_sequence_text`, `diegetic_speech_balloon`, `animated_portrait_dialog`, `kinetic_hype_text`, `typewriter_voice_text` e `flavor_text_interaction`
- exigir `glyph_manifest`, `text_audio_plan`, owner de tiles/sprites/WINDOW/audio, budget e fallback antes do runtime

Gate:

- texto expressivo continua legivel em 320x224 e nao cobre gameplay critico
- typewriter voice nao rouba SFX critico nem boss cue
- paineis, baloes e retratos resetam sem vazamento de tiles, sprites, paleta ou audio

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

## Wave 2.5 - Feedback FX e Particulas

Scenes futuras no `BENCHMARK_VISUAL_LAB`:

- `fx_feedback_suite_lab`
- `fx_hit_spark_particle_lab`
- `fx_palette_cycling_lab`

Entregas:

- usar `feedback_fx_decision_system` como doutrina P0 ja incorporada
- definir quando usar sprite particles, tile animation, palette cycling, raster shock, screen shake e hit sparks
- exigir `fx_ownership_map`, `readability_gate`, `budget_decision`, `teardown_reset_plan` e `fallback_plan`
- recusar particula ou FX que seja so bonito e nao comunique impacto, risco, recompensa ou estado de gameplay

Gate:

- hit sparks, poeira, explosao, energia e feedback de dano permanecem legiveis em pior quadro
- nenhum FX compete com HUD, jogador ou colisao critica sem justificativa e budget
- BlastEm confirma ausencia de flicker, callback vazado ou palette leak

## Wave 3 - Display Architecture, Boss/Setpieces e Sprite Overflow Engineering

Scenes obrigatorias:

- `hud_window_plane_lab`
- `display_interlaced_448_lab`
- `boss_setpiece_lab`
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
- `boss_setpiece_design` guia contrato de setpiece com telegraph, weak point, impacto e fallback
- `interlaced_448_display_mode` tratado como `special_scene_only`
- worst-frame budget para scanline pressure

Gate:

- `WINDOW` e `window alias` deixam de ser confundidos
- boss/setpiece nao esconde o estado do jogador nem quebra leitura de ataque
- `interlaced_448` so permanece no core roadmap se provar ganho real contra 224p
- `sprite_midframe_sat_reuse` nao sobe sem prova isolada sem corrupcao

## Wave 4 - Tilemap Avancado, Pseudo-3D Spectrum e Streaming

Scenes obrigatorias:

- `advanced_tilemap_streaming_lab`
- `tile_cache_streaming_lab`
- `pseudo3d_road_lab`
- `pseudo3d_affine_lab`

Entregas:

- usar `advanced_tilemap_design` como doutrina P2 ja incorporada
- provar metatile reuse, streaming boundary, rota legivel e contrato visual de colisao
- promover `pseudo3d_road_stack` para `blastem_proven`
- manter `software_affine_pseudo3d` como trilha separada

Gate:

- streaming nao gera seam, pop de tiles ou rota confusa
- tilemap avancado melhora mundo jogavel, nao so tileset bonito
- road-stack e affine software deixam de compartilhar status

## Wave 5 - Audio senior

Scene obrigatoria:

- `audio_xgm2_lab`
- `audio_z80_pcm_lab`

Entregas:

- usar `xgm2_audio_architecture` como doutrina P3 ate existir benchmark
- usar `z80-pcm-custom-driver` como skill canonica para driver custom, PCM streaming, DAC direto, PSG direto e bank switching
- provar BGM + SFX prioritario + ambiente + stinger
- provar driver customizado, bus protection, PCM streaming e sample format engineering quando a cena exigir audio alem do XGM2 padrao
- provar `pause`, `resume`, `loop` e ownership de canal
- rodar `validate_audio.ps1` com saida em `out/logs/audio_validation_report.json` e absorcao no `validation_report.json`
- declarar fallback quando PCM multiplexing nao couber

Gate:

- audio deixa de ser categoria ausente do framework
- `audio_validation_report.json` nao pode ficar fora de `out/logs` nem fora da cadeia de validacao
- stinger, ambiente e SFX nao roubam canal critico sem ownership declarado

## Wave 6 - Kinematics e Experimentos

Scenes obrigatorias:

- `boss_kinematics_lab`
- `fx_decal_mutation_lab`
- `fx_cellular_microbuffer_lab`

Entregas:

- criar skill `forward-kinematics-rigging` apenas quando Fase 1 autorizar
- formalizar `mutable_tile_decal_mutation` como trilha experimental de setor local
- exigir `RAM shadow copy`, `mutable tile pool` e politica de persistencia por sala
- manter `cellular_microbuffer_sim` bloqueado ate haver prova de mutacao local e dirty upload disciplinado

Gate:

- articulacao em `fix16` estavel
- tiles mutaveis ficam limitados a setores explicitamente damageable
- `cellular_microbuffer_sim` permanece fora do build principal ate benchmark proprio em ilha pequena

## Wave 7 - Certificacao senior absoluta

Para cada tecnica:

- `lib_case` existe
- scene dedicada existe
- `validation_report` confirma `blastem_gate = true`
- budget esta aprovado
- aprovacao humana esta registrada

Somente entao o `current_status` pode virar `senior_default`.

## Ordem obrigatoria de implementacao

1. consolidar skill owners e registry machine-readable
2. consolidar benchmark contract e roadmap de proficiencia
3. canonizar Texto Narrativo Expressivo quando houver fala, alerta, flavor ou painel dramatico
4. canonizar Raster Control e Iluminacao
5. canonizar Feedback FX e Particulas
6. canonizar Display, Boss/Setpieces e Sprite Overflow Engineering
7. canonizar Tilemap Avancado, Pseudo-3D e Streaming
8. canonizar Audio Senior
9. abrir Kinematics e Experimentos apenas depois dos gates anteriores
10. certificar por BlastEm e regressao

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
