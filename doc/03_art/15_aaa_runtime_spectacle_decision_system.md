# AAA Runtime Spectacle Decision System

Status: `canonico / doutrina operacional`
Trilhas cobertas: `S2.1`, `S2.2`, `S2.3`, `S2.4`, `S3.1`, `S4.1`, `S5.2`

---

## Objetivo

Dar ao agente dominio pratico para usar espetaculo tecnico de Mega Drive sem virar enfeite, excesso ou mentira de hardware.

Este documento cobre:

- raster, H-Int, line scroll, palette split e pseudo-3D
- Shadow/Highlight, silhueta, backlight, spotlight, dano, noite, lanterna e weak point
- hit sparks, poeira, explosao, impacto, fumaca, debris, energia, magia e particulas
- boss visual, setpieces, plane takeover, partes, telegraph e weak points
- tilemap avancado, streaming, metatiles, parallax regional, foreground priority e leitura de rota
- audio senior com XGM2, PCM ownership, stingers, ambience, fades, boss cues e prioridade de SFX

## Regra principal

FX AAA no Mega Drive nao e "mais coisa na tela".

E efeito com:

- funcao de gameplay
- funcao dramatica
- leitura imediata
- owner unico
- budget medido
- reset simetrico
- fallback honesto

Se o efeito nao muda leitura, risco, impacto, ritmo ou contexto, recusar.

## Artefatos canonicos

Emitir estes cards quando a cena tocar o dominio correspondente:

- `feedback_fx_decision_card`
  - raster, luz, Shadow/Highlight, palette cycling, hit sparks, particulas, camera impact e feedback de dano
- `boss_setpiece_card`
  - boss grande, boss composto, setpiece, weak point, telegraph, plane takeover ou arena especial
- `advanced_tilemap_design_card`
  - streaming, metatiles, parallax regional, priority foreground, destruicao local, colisao visual ou rota complexa
- `audio_architecture_card`
  - XGM2, BGM, SFX prioritario, ambience, stinger, boss cue, fade, pause/resume ou audio handoff entre cenas

## `feedback_fx_decision_card`

Campos obrigatorios:

```yaml
fx_surface_id: scene_01_combat_fx
fx_role: "comunicar impacto, risco, estado ou atmosfera"
gameplay_signal: "dano recebido / ataque perfeito / perigo / magia carregada"
fx_class: "raster_distortion | lighting_state | palette_cycle | sprite_particles | tile_particles | camera_impact | mixed"
readability_target: "jogador, inimigo, projetil, weak point ou rota"
owner_map:
  H-Int: "scene_fx_owner | none"
  CRAM: "palette_fx_owner | none"
  VSRAM: "scroll_fx_owner | none"
  SPRITES: "particle_owner | none"
  BG_A_tiles: "tile_fx_owner | none"
budget_decision: "cabe | cabe com recuo | nao cabe"
teardown_reset_plan: "callbacks, scroll, paleta, sprites, tiles e shadow/highlight"
fallback_plan: "palette pulse, sprite spark simples, hard cut justificado ou sem FX"
```

Classes permitidas:

- `raster_distortion`
  - agua, calor, sonho, choque, vento, corrida, dano psiquico
- `lighting_state`
  - silhueta, backlight, spotlight, lanterna, weak point, noite, alarme
- `palette_cycle`
  - energia, agua, fogo, neon, warning, carga, terminal vivo
- `sprite_particles`
  - hit sparks, poeira, debris pequeno, impacto localizado
- `tile_particles`
  - debris de cenario, rachadura, explosao em setor, dano persistente local
- `camera_impact`
  - shake por scroll curto, recoil, stomp, explosao, queda
- `mixed`
  - so quando cada sub-FX tiver owner e reset

Bloquear:

- FX que esconde hitbox critica
- particula que compete com projetil
- Shadow/Highlight sem `palette_slot_audit`
- H-Int sem owner unico
- palette cycling em paleta compartilhada sem dono
- camera shake que prejudica input ou plataforma

## `boss_setpiece_card`

Campos obrigatorios:

```yaml
boss_or_setpiece_id: boss_01_gatekeeper
setpiece_role: "intimidar, ensinar padrao, quebrar ritmo ou encerrar arco"
body_architecture: "composite_sprite | plane_takeover | hybrid | small_boss"
residency_policy: "full_resident | scene_local_preload | animation_window_streaming | fallback_reduced_residency"
weak_point_model: "visual_slot | exposed_state | lighting_gate | timed_window"
telegraph_profile: "startup, active, recovery e leitura cromatica"
plane_ownership_map: "BG_A/BG_B/WINDOW/SPRITES durante boss"
scanline_budget: "pior quadro com jogador, boss, HUD, FX e projeteis"
feedback_fx_ref: "feedback_fx_decision_card quando houver FX"
teardown_reset_plan: "sprites, planos, H-Int, paletas, camera e audio"
fallback_plan: "reduzir partes, mover para plano, cortar FX ou simplificar arena"
```

Escolhas canonicas:

- `composite_sprite`
  - boss medio, partes independentes, animacao expressiva
- `plane_takeover`
  - boss gigante ou estrutura que precisa escala impossivel por sprites
- `hybrid`
  - corpo em plano, partes/weak points em sprites
- `small_boss`
  - leitura e padrao valem mais que tamanho

Bloquear:

- boss grande que causa flicker no jogador
- weak point que nao parece weak point
- telegraph que so funciona pausado
- setpiece que quebra controle sem payoff
- plane takeover sem declarar perda de parallax

## `advanced_tilemap_design_card`

Campos obrigatorios:

```yaml
tilemap_surface_id: stage_02_foundry
world_role: "mundo jogavel, rota, obstaculo, arena ou setpiece"
tilemap_class: "metatile_stage | streaming_stage | priority_foreground | destructible_sector | parallax_region | hybrid"
residency_policy: "full_resident | scene_local_preload | tilemap_streaming | fallback_reduced_residency"
metatile_reuse_plan: "familias, flips, variacoes e limites de tiles unicos"
streaming_boundary_map: "quando e onde novos tiles/map chunks entram"
load_time_dma_plan: "o que carrega em boot/loading/troca de cena"
per_frame_dma_plan: "uploads por VBlank no pior quadro de gameplay"
collision_visual_contract: "o que parece solido, perigoso, passavel ou interativo"
route_readability_gate: "para onde o jogador deve olhar em 1 segundo"
budget_decision: "cabe | cabe com recuo | nao cabe"
fallback_plan: "compare_flat, reduzir tiles, cortar setor mutavel ou reduzir parallax"
```

Classes permitidas:

- `metatile_stage`
  - mundo modular com reuso visual honesto
- `streaming_stage`
  - mapa maior que VRAM visivel; exige seam control, preload honesto e separacao entre mundo total e resident set local
- `priority_foreground`
  - cobertura parcial de sprite por tiles com prioridade
- `destructible_sector`
  - mutacao local com pool de tiles e dirty uploads
- `parallax_region`
  - regiao com ratio proprio de scroll ou coluna/linha
- `hybrid`
  - so se cada tecnica tiver custo e fallback

Bloquear:

- tilemap bonito mas sem leitura de rota
- streaming sem seam plan
- contar mundo inteiro como residente quando a cena usa escopo local ou streaming declarado
- colisao que contradiz visual
- destruicao local sem pool e reset
- foreground priority que confunde profundidade jogavel

## `audio_architecture_card`

Campos obrigatorios:

```yaml
audio_surface_id: scene_02_boss_audio
audio_role: "tensao, recompensa, alerta, continuidade ou assinatura"
xgm2_mode: "bgm_only | bgm_sfx | bgm_sfx_ambience | boss_setpiece"
channel_ownership_map: "BGM, SFX, ambience, voice/stinger"
sfx_priority_table: "impacto > dano > UI > ambiente, ou regra do projeto"
music_stinger_plan: "inicio, boss cue, vitoria, morte, transicao"
audio_transition_plan: "manter, fadeOut, fadeIn, cross cue ou sting"
pause_resume_contract: "o que pausa, o que continua e como retoma"
fallback_plan: "cortar ambience, simplificar stinger, reduzir PCM ou BGM only"
```

Bloquear:

- audio sem owner de canal
- SFX que corta BGM por acidente
- boss cue sem handoff de estado
- ambience que rouba prioridade de gameplay
- pause/resume inconsistente
- loop com clique aceito como final

## Handoff entre skills

- `visual-excellence-standards`
  - julga leitura, impacto, silhueta, excesso visual e coerencia dramatica
- `scene-state-architect`
  - declara owners de H-Int, CRAM, VSRAM, sprites, tiles, audio e teardown
- `megadrive-vdp-budget-analyst`
  - responde `cabe`, `cabe com recuo` ou `nao cabe` por pior quadro
- `multi-plane-composition`
  - decide planos, boss plane takeover, tilemap, parallax e route readability
- `sgdk-runtime-coder`
  - implementa somente cards aprovados, com reset e fallback rastreaveis
- `xgm2-audio-director`
  - controla `audio_architecture_card`, canais, eventos, loop e pause/resume

## Regra final

O agente deve preferir o efeito mais expressivo que ainda preserve:

- leitura de gameplay
- budget de pior quadro
- ownership unico
- teardown limpo
- coerencia com fantasia

Maximalismo aqui nao e excesso. E precisao dramatica com dominio do VDP.
