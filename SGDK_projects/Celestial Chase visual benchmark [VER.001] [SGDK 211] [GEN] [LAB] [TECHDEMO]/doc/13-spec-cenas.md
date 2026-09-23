# 13 - Especificacao Tecnica por Cena - Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

> Documento canonico para budgets por cena, contrato de evidencia e papel formal de cada surface.
> Menu, title screen e outras telas de front-end contam como cenas formais.

## Estado P1-002 - Audio XGM2 FM/PSG

- ROM vigente: `8eeef763a86f0997b83d9305971bf9aef6e598d18afd3151604e47117f02d450`, `262144` bytes, build SGDK 2.11 Linux nativo.
- `mus_chase_core` e compilada como XGM2 a partir de `res/audio/chase/chase_core_fm_psg.vgm`: duas vozes YM2612 FM e pulso SN76489 PSG, loop NTSC de 8 segundos.
- Ownership: XGM2 possui FM/PSG; PCM_CH1 fica reservado; PCM_CH2 possui cues criticos e PCM_CH3 possui movimento/UI/pressao.
- Budget: 1 musica + 9 SFX, 39,5 KiB estimados, 0,96% da ROM de 4 MiB; maximo de dois PCM simultaneos.
- BlastEm `blastem-linux-20260720T032218Z-267076`: 270 amostras, 8 com musica+SFX simultaneos, 5/5 SFX aceitos, DMA wait maximo 0.
- Warning: 1 frame XGM2 perdido em 1.363 frames de driver; revisao auditiva humana segue pendente.
- Tecnicas: `xgm2_audio_architecture` e `xgm2_pcm_multiplexing`; fallback remove pressure/pickup antes de alterar ownership critico.

## Estado v014 - Road Polish, Evidencia Multi-Frame e Gate Honesto

- ROM vigente observada no BlastEm: `984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9`, `393216` bytes.
- Mudanca visual significativa: BG_A recebeu polimento v014 no builder para reduzir singleton noise, reforcar linhas de fuga e aproximar a leitura da estrada de `res/gfx/chase_compare_flat.png` sem trocar numero de build por vaidade.
- Mudanca runtime associada: `chase_road` reduziu a intensidade do streak horizontal por linha e removeu o VScroll por coluna independente que rasgava visualmente as laterais da estrada; a estrada passa a se mover como plano coeso.
- Sombra de contato: `chase_contact_shadow_16x8_strip_v011` foi redesenhada como elipse conectada multi-tom; o teste unitario impede retorno a blocos desconexos sem massa de sombra.
- Budget vigente medido: BG_B `480` + BG_A `210` + letterbox `1` = `691/744`, headroom `53`; `res_graph_audit` passou com 31 declaracoes OK.
- Tilemap: `scene_tilemap_conversion_report.json` atualizado para BG_A SHA256 `0d32085e02e0e4c47da8b0d0313c1e92e55e704c431bdb3dba35d94da907f995`, `210` tiles finais, `88.28125%` de dedup e zero conflitos de paleta.
- Evidencia BlastEm: `out/logs/runtime_metrics.json` mede `scene_id=4`, `frames_seen=151`, `samples_recorded=32`, `cpu_load_max=75`, `p95=73`, `over_budget_frames=0`, `max_scanline_sprites=9`, `sprite_engine_peak=19`.
- Evidencia visual: `out/evidence/scenes/first_playable_slice/screenshot.png` mostra o heroi sem capsula opaca e a estrada com convergencia mais limpa.
- Evidencia multi-frame: `out/evidence/motion/chase_v014_scene_multiframe/chase_v014_scene_multiframe.webp` e `chase_v014_scene_multiframe_report.json` empacotam capturas BlastEm dos frames 90/120/150/180; os deltas temporais sao reais, mas `perceptual_check` continua zerado ate revisao humana.
- Gate de cor: `out/logs/visual_screenshot_color_gate_report.json` passou apos a nova captura; nenhum relatorio pode promover screenshot estatico a aprovacao de movimento.
- Regressao de cena: baseline de `first_playable_slice` foi atualizado somente apos inspecao visual e gate de cor; nova matriz passou `3/3`.
- Recuo honesto: BG_A melhorou, mas ainda esta `rework` no juiz estetico (`0.5631` contra `0.58`) por dithering material insuficiente e alinhamento de referencia ainda incompleto. `creative_ready=false`, `ready_for_aaa=false` e `visual_gate_blocked` permanecem corretos.

## Estado v013 - Correcao P0 de Transparencia/Matte do Heroi

- ROM vigente observada no BlastEm: `ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908`, `393216` bytes.
- Regressao reconhecida: a v022 pintou um envelope azul/teal opaco no canvas do heroi; a causa real foi escrita de pixels visiveis fora da silhueta pelo `velocity_mantle`, nao falha de compilacao.
- Correcao aplicada: `add_hero_velocity_mantle()` agora so altera pixels da silhueta ou borda imediata; nenhum preenchimento de canvas transparente e permitido.
- Gate novo de sprite: `out/logs/sprite_transparency_gate_report.json` valida `index0_rgb=[255,0,255]`, `transparent_index=0`, ocupacao de borda controlada e ausencia de frame tocando a largura inteira.
- Gate novo de screenshot: `out/logs/visual_screenshot_color_gate_report_pre_fix.json` reprova a evidencia antiga; `out/logs/visual_screenshot_color_gate_report.json` passa na captura BlastEm nova de `first_playable_slice`.
- Evidencia visual nova: `out/evidence/scenes/first_playable_slice/screenshot.png` mostra o heroi sem capsula opaca, com estrada/sombra novamente visiveis ao redor do sprite.
- Evidencia motion nova: `out/evidence/motion/chase_hero_silhouette_velocity_v013.gif/.webp`, `out/evidence/motion/chase_hero_ghost_silhouette_velocity_v013.gif/.webp` e `hero_silhouette_transparency_fix_motion_report_v013.json`.
- Regressao de cena: o baseline de `first_playable_slice` foi atualizado apenas apos a correcao P0; nova comparacao passou `3/3`.
- Budget historico v013: `res_graph_report.json` passou com 31 declaracoes OK, zero overlaps; o budget de audio vigente foi atualizado no estado P1-002 acima.
- Recuo honesto: `runtime_metrics.json` tem `perceptual_check` zerado ate revisao humana; `creative_ready=false`, `ready_for_aaa=false` e `visual_gate_blocked` permanecem corretos.
- Divida visual ativa: BG_A/estrada ainda precisa rework contra `res/gfx/chase_compare_flat.png` para reduzir ruido de tiles, suavizar profundidade e alinhar melhor o mockup. Esta correcao nao promove a estrada.

## Estado v012 - Vertical Slice Perceptual/Visual Gate Reduction

- ROM vigente observada no BlastEm: `9b8fdb32b8b949c85e99f13d31f2504dcf6c3432c84bb2c42b8c2357ff2ddcf1`, `393216` bytes.
- Rota visual congelada para a proxima entrega: `first_playable_slice` jogavel, nao `compare_flat` nem plate de laboratorio.
- Mudanca visual significativa: `spr_chase_hero_run_v009` e `spr_chase_hero_ghost_v009` foram remasterizados como `velocity_mantle` source-baked; ambos passaram para `elite_ready` no juiz estetico (`0.7913` e `0.7937`).
- Evidencia motion/perceptual: GIF/WebP em `out/evidence/motion/`, `runtime_metrics.json` com `perceptual_check` preenchido, screenshot BlastEm, `save.sram` e `visual_vdp_dump.bin` frescos.
- Regressao de cena: `3/3` em modo compare apos refresh intencional do baseline de `first_playable_slice`.
- Budget vigente: `res_graph_report.json` passou com zero overlap; residencia medida BG_B `488` + BG_A `186` + letterbox `1` = `675/744`, headroom `69`; runtime curto mediu `cpu_load_max=80`, `p95=77`, `over_budget_frames=0`, `max_scanline_sprites=9`, `sprite_engine_peak=19`.
- Recuo honesto: `critical_motion` ainda nao passa o gate metodologico por falta de `human_approval_record`; `ready_for_aaa=false` e `creative_ready=false` permanecem corretos.
- Blockers dominantes removidos/reduzidos: `procedural_fallback_as_final=false`, `visual_direction_failed` removido, `scene_regression_incomplete` removido, `vram_residency_collision_risk` resolvido por refresh de evidencia medida, `perceptual_motion_unvalidated` reduzido somente a aprovacao humana.

## scene_roadmap

### Marco 0 - Branding e Front End Curado

- nome de trabalho: `branding_title_menu`
- runtime_name na ROM: `BRAND` -> `BOOT` -> `MENU`
- `app_scene_id`: `0`, `1`, `2`
- `warmup_frames` inicial de contrato: `90`
- papel: menu
- objetivo: provar que o front-end ja nasce como showcase e ferramenta operacional
- dependencia principal: `front_end_profile`

### Marco 1 - First Playable Slice Promovido

- nome de trabalho: `chase_first_playable`
- runtime_name na ROM: `CHASE`
- `app_scene_id`: `4`
- `warmup_frames` inicial de contrato: `90`
- papel: gameplay
- objetivo: provar o loop central com budget e evidencia rastreaveis
- dependencia principal: `core_loop_statement`

### Cena 2 - `chase_result_state`

- nome de trabalho: `chase_result_state`
- runtime_name na ROM: `CHASE`
- `app_scene_id`: `4`
- `warmup_frames` inicial de contrato: `90`
- regressao: `sram_bootstrap` com `bootstrap_flags=["force_chase_failure_result"]`, `capture_frame=120`, `capture_hold_frame=120`
- papel: resultado
- objetivo: provar vitoria, falha, reinicio e retorno ao menu sem softlock
- dependencia principal: `chase_first_playable`

## Contratos Canonicos Transversais

### Route decision obrigatorio por cena

- `route_decision_record.context_type`
- `route_decision_record.dominant_route`
- `route_decision_record.first_skill`
- `route_decision_record.first_tool`
- `route_decision_record.resource_loading_model`
- `route_decision_record.asset_strategy`
- `route_decision_record.evidence_required`
- `route_decision_record.forbidden_shortcuts_until_evidence`

Regra: cena com parallax, foreground/oclusao, source grande, spritesheet grande ou referencia interna nao abre runtime antes de declarar se usa `full_resident`, `scene_local_preload`, `tilemap_streaming`, `animation_window_streaming` ou `fallback_reduced_residency`.

### Semantica de budget obrigatoria por cena

- `rom_asset_cost`
- `vram_resident_set`
- `load_time_dma_cost`
- `per_frame_dma_cost`
- `active_animation_window`
- `scene_local_scope`
- `scanline_sprite_pressure`

### Runtime decision log obrigatorio por cena

- `debug_order_check`: existencia -> posicao -> composicao -> budget -> paleta/rescomp/build
- `resource_loading_model`: `full_resident`, `scene_local_preload`, `tilemap_streaming`, `animation_window_streaming` ou `fallback_reduced_residency`
- `builder_route`: builder dedicado, builder reaproveitado ou justificativa de ausencia
- `fallback_plan`: recuo conservador antes de aumentar complexidade
- `evidence_required`: build, res_graph, validation, runtime_metrics, scene_regression, emulator_session, freshness, closeout

### Contrato de fechamento por cena

- `scene_contract_compile_report.json`: deve ser recompilado apos os contratos finais.
- `res_graph_report.json`: deve confirmar zero overlap e residencia coerente.
- `validation_report.json`: deve ficar sem blockers tecnicos; blockers humanos permanecem explicitos.
- `runtime_metrics.json`: deve registrar `target_scene_match=true`, `over_budget_frames=0` e FPS alvo estavel.
- `scene_regression_report.json`: deve comparar baseline da cena jogavel e do resultado.
- `emulator_session.json`: deve registrar BlastEm capturado e fechado para a ROM vigente.
- `freshness_audit_report.json`: deve ficar sem stale.
- `scene_closeout_gate_report.json`: so pode ficar `ok` quando gates criativos e humanos tambem passarem.

Regra: cena so sobe de `testado_em_emulador` para `validado_budget` quando a evidencia mede a ROM vigente, o `app_scene_id` capturado bate com o esperado e o freshness nao aponta drift bloqueante.

## First Playable Slice Contract

- `target_scene`: `APP_SCENE_CHASE`
- `target_duration_ntsc_frames`: `4500`
- `target_duration_seconds`: `75`
- `flow`: `branding -> boot/title -> menu -> chase_playing -> chase_result -> restart/menu`
- `input_contract`: `left/right lane`, `A jump`, `B Pulse`, `START pause`, `MODE menu only outside active run`
- `lane_count`: `3`
- `integrity_max`: `3`
- `pressure_range`: `0..100`
- `pulse_range`: `0..100`
- `success_condition`: sobreviver ate o frame final com pressao abaixo de 100
- `failure_condition`: pressao 100 ou integridade 0
- `softlock_policy`: todo estado aceita ao menos um caminho determinista de continuidade

### Phase Rhythm Map

| Fase | Janela NTSC | Funcao | Ameacas | Audio State | Paleta |
|---|---:|---|---|---|---|
| `intro_tutorial` | 0-1199 | ensinar faixa, salto e coleta | isoladas | `intro` | fria/luminosa |
| `rising_pressure` | 1200-2999 | combinar respostas e cobrar Pulse | pares e alternancia | `pressure` | quente |
| `climax_escape` | 3000-4499 | teste final com respiracao curta | golpes do perseguidor + obstaculos | `climax` | alto contraste |

### Runtime Ownership

- `APP/core`: transicoes de cena, frame global e dispatch.
- `chase_rules`: FSM da rodada, fases, pause, resultado, integridade, pressao e Pulse.
- `chase_player`: faixa, troca, salto, invulnerabilidade e sprite do heroi.
- `chase_obstacles`: pool estatico, spawn determinista, telegrafo e colisao.
- `chase_pursuer`: proximidade, sprite, poeira, Pulse e impacto.
- `chase_hud`: HUD de entrega e cards curtos.
- `scene_chase`: composicao, entrada/saida e orquestracao dos modulos.
- `system/audio`: XGM2 possui FM/PSG; PCM_CH2/CH3 possuem SFX com prioridades e telemetria AUD2.
- DMA/CRAM/scroll: somente chamadas SGDK seguras e commit no VBlank; sem callback concorrente.

### Transition Contract

- Branding termina em boot/title; A/START acelera sem pular teardown.
- Boot/title termina em menu.
- Menu inicia CHASE.
- CHASE entra em resultado sem trocar de cena, preservando composicao e congelando spawns.
- Resultado reinicia CHASE por reentrada ou volta ao menu.
- Toda saida zera scrolls, sprites, pause e cues ativos.

## Detalhamento do Slice Inicial

### Cena 0 - `front_end_main_menu`

- classe de problema: menu curado com hierarquia visual forte e overlay seguro
- papel: menu
- objetivo visual: sustentar identidade de front-end sem competir com a leitura tecnica
- papel no projeto: porta de entrada, seletor de fluxo e primeira prova de curadoria
- budget alvo:
  - leitura forte em `WINDOW`
  - custo de preload controlado
  - zero dependencia de pseudo-terceiro-plano
- resource_budget_model:
  - `scene_local_scope`: moldura do menu, fonte tecnica, cursor e atmosfera local
  - `rom_asset_cost`: `nao_medido`
  - `vram_resident_set`: BG_A, BG_B, fonte/overlay em `WINDOW` e cursor
  - `load_time_dma_cost`: preload completo permitido na entrada
  - `per_frame_dma_cost`: `nao_medido`
  - `active_animation_window`: animacao so do cursor e micro-vida de front-end
  - `scanline_sprite_pressure`: `nao_medido`
  - `runtime_loading_model`: `scene_local_preload`
  - `fallback_plan`: reduzir animacao e detalhe antes de perder legibilidade
- riscos de VDP:
  - texto fora de `WINDOW`
  - hierarquia fraca de paleta
  - menu parecer placeholder
- contrato de evidencia:
  - screenshot dedicada em BlastEm
  - `save.sram` com bloco canonico `MDRT`
  - `visual_vdp_dump.bin` quando o fluxo visual canonico estiver habilitado
  - regressao deterministica com captura `overlay_off` e `overlay_on`

### Cena 1 - `first_playable_slice`

- classe de problema: gameplay de perseguicao com tres faixas e pressao crescente
- papel: gameplay
- objetivo visual: provar o loop central sem esconder custo real de VRAM, DMA e sprites
- papel no projeto: primeira entrega jogavel com evidencias minimas rastreaveis
- budget alvo:
  - preload honesto dos assets da cena
  - zero DMA fora de VBlank
  - overlay tecnico fora do plano rolavel
- resource_budget_model:
  - `scene_local_scope`: atmosfera, overlay de estrada, heroi, perseguidor, ameacas, energia, HUD e FX
  - `rom_asset_cost`: ROM v014 com `393216` bytes, SHA256 `984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9`
  - `vram_resident_set`: BG_B `480` + BG_A 512px `210` + letterbox `1` = `691/744`, headroom `53`, sprite reserve `680`
  - `load_time_dma_cost`: permitido apenas na entrada da cena
  - `per_frame_dma_cost`: sprite engine + CRAM/scroll pequenos; planejamento `6404/7168`, trace detalhado pendente; runtime v014 observado sem over-budget (`cpu_load_max=75`, `p95=73`)
  - `active_animation_window`: heroi, perseguidor modular, pool estatico de tres slots com ate 2 hazards e 1 pickup ativos, sombras, poeira e Pulse
  - `scanline_sprite_pressure`: runtime v012 observado `9/20`; enumerador ligado a geometria da ROM mede pior caso `12/20`, com `8` de headroom
  - `runtime_loading_model`: `scene_local_preload`
  - `fallback_plan`: simplificar composicao antes de vender efeito caro como default
- riscos de VDP:
  - HUD em plano rolavel
  - budget invisivel no doc
  - prova jogavel sem evidencia em BlastEm
- contrato de evidencia:
  - screenshot dedicada em BlastEm em `out/evidence/scenes/first_playable_slice/screenshot.png`
  - `save.sram` com bloco canonico `MDRT` e captura hold `SBIS v2`
  - `visual_vdp_dump.bin` fresco em `out/evidence/blastem/visual_vdp_dump.bin`
  - regressao deterministica `3/3` para menu, gameplay e resultado
  - `out/logs/sprite_scanline_pressure_report.json` ligado ao hash da ROM
  - `out/logs/res_graph_report.json` com zero overlaps/issues
  - `out/evidence/motion/chase_hero_silhouette_velocity_v013.gif` e `out/evidence/motion/chase_hero_ghost_silhouette_velocity_v013.gif` como evidencia de motion asset-level; nao substituem aprovacao humana
  - `out/evidence/motion/chase_v014_scene_multiframe/chase_v014_scene_multiframe.webp` como evidencia multi-frame de output BlastEm; tambem nao substitui aprovacao humana
  - `out/logs/sprite_transparency_gate_report.json` e `out/logs/visual_screenshot_color_gate_report.json` bloqueiam retorno de matte/capsula opaca nos sprites criticos

## Cena Legada - `chase_visual_benchmark`

- classe de problema: prova runtime de animacao source-baked com residencia reduzida
- papel: visual_lab
- objetivo visual: validar em ROM o heroi 64x80, boss frontal 3/4, poeira e shake de impacto sem perder o budget de VRAM
- papel no projeto: primeira prova buildada dos sprites aprovados pelo usuario
- route_decision_record:
  - `context_type`: cena_existente_promovida
  - `dominant_route`: runtime animation lab
  - `first_skill`: sgdk-runtime-coder
  - `resource_loading_model`: fallback_reduced_residency
  - `asset_strategy`: IMAGE low-tile runtime BG + SPRITE source-baked strips
  - `evidence_required`: build, validation_report, res_graph_report, GIF de observacao da animacao, screenshot BlastEm, SRAM READY, runtime_metrics
  - `forbidden_shortcuts_until_evidence`: nao promover como delivery/AAA; nao declarar movimento correto sem observar GIF; nao declarar `testado_em_emulador` sem BlastEm fresco da ROM vigente
- resource_budget_model:
  - `scene_local_scope`: `img_chase_anim_runtime_bg`, `spr_chase_hero_run_toward`, `spr_chase_pursuer_body_zloop`, `spr_chase_pursuer_dust_impact`
  - `rom_asset_cost`: build_v004 gerou ROM de `262144` bytes, SHA256 `9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed`
  - `vram_resident_set`: BG runtime com 258 tiles unicos; res graph final `ok`, sprite reserve `512`, overlaps `0`
  - `load_time_dma_cost`: preload completo permitido na entrada da cena; palettes PAL0/PAL1/PAL2 carregadas na entrada
  - `per_frame_dma_cost`: sprite engine SGDK troca tiles de sprite em mudanca de frame; codigo da cena nao faz DMA manual fora do VBlank
  - `active_animation_window`: heroi 8 frames com ticks `4,3,3,4,4,3,3,4`; boss body 6 frames com ticks `6,5,5,7,5,5`; dust burst independente D0-D4 com ticks `2,2,2,3,3`; shake dispara no B3 com offsets `+2,-2,+1,-1,0`
  - `animation_observation_evidence`: `out/evidence/motion/chase_runtime_like_animation_observation_v005.gif`
  - `scanline_sprite_pressure`: BlastEm/runtime metrics mediu `max_scanline_sprites=16`, `sprite_engine_peak=3`, `fx_peak_concurrency=1`, `over_budget_frames=0`
  - `runtime_loading_model`: fallback_reduced_residency
  - `fallback_plan`: manter head/hoof promovidos mas fora da primeira composicao runtime porque sobreporam anatomia ja presente no body; reabrir rig modular apos prova visual em emulador
- riscos de VDP:
  - `SPR_initEx(512)` reduz a margem para fundos ricos em tiles
  - fundo split v007 nao cabe junto ao pacote animado completo sem nova estrategia de streaming/composicao
  - juiz estetico automatico ainda marca sprites como rework apesar da aprovacao humana; nao usar isso como liberacao AAA
  - `perceptual_quality` ainda esta `nao_medido`; a aprovacao humana do GIF v005 continua obrigatoria para o proximo passo visual
  - `visual_vdp_dump.bin` ainda nao foi capturado para a modalidade visual canonica completa
- contrato de evidencia:
  - GIF dedicado de observacao da animacao runtime-like v005
  - screenshot dedicada em BlastEm da ROM SHA256 `9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed`
  - `save.sram` com bloco canonico `MDRT/READY`
  - validation report da mesma ROM
  - runtime metrics com `target_scene_match=true`, `performance=estavel` e `over_budget_frames=0`
  - freshness audit antes de qualquer promocao de status

## Metodologia estruturada 2026-06-04

- `doc/project_methodology_manifest.json` classifica `critical_motion=required`.
- `road_physics=required`: a cena usa tres faixas, estado Z compartilhado, deformacao de pista e colisao sincronizada pelo contrato `doc/contracts/chase_v009_road_physics_contract.json`.
- `modular_boss=required`: torso, cabeca e garras sao sprites runtime independentes com FK, poda ativa e budget de scanline pelo contrato `doc/contracts/chase_v009_modular_boss_contract.json`.
- tecnicas vigentes e tags estao em `doc/technique_usage_manifest.json`.
