# 13 - Especificacao Tecnica por Cena - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

> Documento canonico para budgets por cena, contrato de evidencia e papel formal de cada surface.
> Menu, title screen e telas de fim contam como cenas formais.

## scene_roadmap

### Cena 0 - `title_screen`

- runtime_name previsto: `APP_SCENE_TITLE`
- app_scene_id previsto: `0`
- papel: front-end/title
- objetivo: comunicar identidade autoral e iniciar a fase com feedback de press start.
- status: `storyboard_candidate_created`, bloqueado por validacao humana,
  conversao VDP, runtime e BlastEm.

### Cena 1 - `stage_01_blue_circuit`

- runtime_name vigente: `APP_SCENE_DEMO`
- app_scene_id vigente: `3`
- papel: gameplay principal.
- objetivo: provar correr, pular, atirar, inimigo comum, mini-boss simples e transicao para fim.
- status: `runtime_measured_creative_blocked`; runtime e budget da primeira
  fatia jogavel foram observados no BlastEm, sem remover os blockers criativos.

### Cena 2 - `ending_screen`

- runtime_name previsto: `APP_SCENE_ENDING`
- app_scene_id previsto: `2`
- papel: encerramento do slice.
- objetivo: confirmar estabilizacao do circuito e terminar a vertical slice sem prometer release.
- status: `storyboard_candidate_created`, bloqueado por validacao humana,
  asset final convertido e runtime.

## Contratos Canonicos Transversais

### Route decision obrigatorio por cena

- `route_decision_record.context_type=projeto_novo`
- `route_decision_record.dominant_route=planning`
- `route_decision_record.first_skill=art/art-asset-diagnostic`
- `route_decision_record.first_tool=validate_project_context.ps1`
- `route_decision_record.resource_loading_model=scene_local_preload`
- `route_decision_record.asset_strategy=mixed`
- `route_decision_record.evidence_required=build + validation + BlastEm + freshness`
- `route_decision_record.forbidden_shortcuts_until_evidence=runtime final, placeholder final, clone visual/audio, ready_for_aaa`

### Semantica de budget obrigatoria por cena

- `rom_asset_cost`: `nao_medido` ate conversao VDP.
- `vram_resident_set`: `nao_medido` ate art pass.
- `load_time_dma_cost`: permitido apenas em entrada/troca de cena.
- `per_frame_dma_cost`: alvo inicial zero streaming; qualquer excecao exige card e budget.
- `active_animation_window`: player, inimigo, projeteis e mini-boss.
- `scene_local_scope`: preload local por cena.
- `scanline_sprite_pressure`: `nao_medido` ate sprite sheet real.

### Runtime decision log obrigatorio por cena

- `debug_order_check`: existencia -> posicao -> composicao -> budget -> paleta/rescomp/build.
- `resource_loading_model`: `scene_local_preload`.
- `builder_route`: wrapper central; sem build logic dentro do projeto.
- `fallback_plan`: reduzir detalhe visual e simultaneidade antes de adicionar streaming/FX.
- `evidence_required`: build, validation, runtime_metrics, scene_regression, emulator_session, freshness, closeout.

### Technique usage manifest obrigatorio

- caminho: `doc/technique_usage_manifest.json`
- status atual: `camera_scroll_management` selecionada para a fase jogavel, sem promocao ate contrato, budget e BlastEm.
- regra: se H-Int, parallax avancado, palette cycling de gameplay, streaming ou boss setpiece entrar, o manifesto deve ser atualizado antes do runtime.

## Detalhamento das Cenas

### Cena 0 - `title_screen`

- classe de problema: front-end autoral com leitura imediata.
- papel no projeto: primeira interacao do jogador.
- `ui_decision_card`:
  - `profile_kind`: `front_end_profile`
  - owner de input: `input-system-sgdk`
  - owner de surface: cena title
  - feedback: pulse curto no press start
  - teardown: limpar input buffers e qualquer palette/scroll antes da fase
- budget alvo:
  - BG_B ou BG_A para title art.
  - WINDOW livre ou reservado conforme HUD futuro.
  - Sprites apenas se o logo/press start exigir e budget aprovar.
- riscos de VDP:
  - fonte generica virar identidade final.
  - logo derivativo.
  - animacao de title sem reset de scroll/paleta.
- contrato de evidencia:
  - screenshot dedicada em BlastEm no title.
  - `save.sram` com cena observada quando runtime probe estiver ativo.
  - freshness e closeout antes de promover.
- blockers atuais:
  - `blocked_no_premium_source`
  - `blocked_no_human_asset_approval`
  - `blocked_no_vdp_conversion`
  - `blocked_no_blastem_evidence`

### Cena 1 - `stage_01_blue_circuit`

- classe de problema: gameplay curto side-view com prova de loop.
- papel no projeto: vertical slice principal.
- secoes:
  1. `entry_conduit`: aprende correr e pular.
  2. `sentry_lane`: encontra `line_sentry` e aprende tiro.
  3. `charge_bridge`: combina pulo e tiro com hazard simples.
  4. `breaker_core_arena`: mini-boss single body.
- entidades:
  - player: 1
  - `line_sentry`: inimigo comum, ate 4 simultaneos
  - `breaker_core`: mini-boss simples
  - projeteis jogador: ate 3
  - projeteis inimigos: ate 4
- performance medida em 2026-07-20:
  - NTSC: 900/900 quadros, P95 CPU 44, maximo 44, 0 over-budget.
  - PAL: 750/750 quadros, P95 CPU 17, maximo 17, 0 over-budget.
  - pico observado: 4 sprites ativos, 3 sprites por scanline.
  - fila DMA observada antes do VBlank: 1 entrada, 40 bytes.
  - evidencia: `out/logs/performance_capture_report.json` e
    `out/logs/performance_budget_report.json`.
  - limite do claim: apenas a cena 3/`first_playable_slice`; outras cenas nao
    herdam estabilidade por inferencia.
- camera:
  - side-view platform
  - dead zone horizontal
  - bounds fechados na fase
  - sem camera paralela por layer
  - registry `camera_scroll_management`
- colisao:
  - solido, vazio, hazard
  - sem slopes e sem one-way no primeiro slice
  - hit/hurt/push separados
- budget alvo:
  - `scene_local_scope`: tiles da fase, player, inimigo, mini-boss, HUD e SFX minimos.
  - `rom_asset_cost`: `nao_medido`
  - `vram_resident_set`: `nao_medido`
  - `load_time_dma_cost`: preload na entrada da cena
  - `per_frame_dma_cost`: `nao_medido`, alvo zero streaming
  - `scanline_sprite_pressure`: `nao_medido`
  - `fallback_plan`: remover hit sparks, reduzir drones, simplificar background.
- contrato de evidencia:
  - build canonico e `validation_report.json`.
  - screenshot dedicada em BlastEm na fase.
  - prova de input observado pela ROM quando navegacao for roteirizada.
  - runtime metrics sem pico bloqueante.
  - scene regression chegando a mini-boss/end.
  - freshness e closeout.
- blockers atuais:
  - `blocked_no_premium_source`
  - `blocked_no_collision_fixtures`
  - `blocked_no_runtime`
  - `blocked_no_blastem_evidence`

### Cena 2 - `ending_screen`

- classe de problema: encerramento simples e autoral.
- papel no projeto: fechamento da vertical slice.
- `scene_transition_card`:
  - entrada: derrota do `breaker_core`
  - estado herdado: nenhum save, apenas resultado da sessao
  - teardown: limpar pools, camera, HUD e input buffers
  - fallback: tela estatica com logo/texto aprovado
- budget alvo:
  - uma composicao simples, sem sprites obrigatorios.
  - audio stinger futuro se aprovado.
- contrato de evidencia:
  - regressao title -> stage -> ending.
  - screenshot BlastEm da tela de fim.
  - freshness e closeout.
- blockers atuais:
  - `blocked_no_premium_source`
  - `blocked_no_runtime`
  - `blocked_no_blastem_evidence`

## Vibe Playable Birth Defaults

- `visual_route_required=true`
- `critical_asset_default_status=awaiting_human_validation`
- `runtime_evidence_default_status=missing`
- `ready_for_aaa=false`

## Human Visual Gate Binding

- Gate 1 - Storyboard controla a leitura macro das tres cenas e das quatro
  secoes jogaveis.
- Gate 2 - Model sheet controla a identidade do player, `line_sentry` e
  `breaker_core`.
- Gate 3 - Spritesheet controla a animacao candidata antes de conversao VDP.
- Todos os gates estao em `doc/contracts/human_visual_gate_plan.json`; nenhum
  candidato visual entra em `res/` ate o gate correspondente ser aprovado.
