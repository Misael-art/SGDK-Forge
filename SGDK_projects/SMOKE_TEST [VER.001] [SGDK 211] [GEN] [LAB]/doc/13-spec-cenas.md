# 13 - Especificacao Tecnica por Cena - SMOKE_TEST [VER.001] [SGDK 211] [GEN] [LAB]

> Documento canonico para budgets por cena, contrato de evidencia e papel formal de cada surface.
> Menu, title screen e outras telas de front-end contam como cenas formais.

## scene_roadmap

### Cena 0 - Front End Curado

- nome de trabalho: `front_end_main_menu`
- runtime_name na ROM: `front_end_main_menu`
- `app_scene_id`: `1`
- `warmup_frames` inicial de contrato: `90`
- papel: menu
- objetivo: provar que o front-end ja nasce como showcase e ferramenta operacional
- dependencia principal: `front_end_profile`

### Cena 1 - First Playable Slice

- nome de trabalho: `first_playable_slice`
- runtime_name na ROM: `first_playable_slice`
- `app_scene_id`: `2`
- `warmup_frames` inicial de contrato: `90`
- papel: gameplay
- objetivo: provar o loop central com budget e evidencia rastreaveis
- dependencia principal: `core_loop_statement`

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

### Technique usage manifest obrigatorio

- caminho: `doc/technique_usage_manifest.json`
- registry: `doc/05_technical/93_16bit_hardware_mastery_registry.json`
- schema: `tools/sgdk_wrapper/schemas/technique_usage_manifest.schema.json`
- obrigatorio quando a cena usar tecnica catalogada, tag de proficiencia humana ou claim de aprendizado do agente

Regra: tecnica sem `registry_id`, sem tag reconhecida, com status `LABORATORIO` fora de lab/techdemo, com evidencia fora do projeto sem autorizacao ou sem `documentation_sync` bloqueia entrega.

### Contrato de fechamento por cena

- `scene_contract_compile_report.json`: ok
- `res_graph_report.json`: ok
- `validation_report.json`: ok
- `runtime_metrics.json`: ok
- `scene_regression_report.json`: nao requerido para este lab
- `emulator_session.json`: ok
- `freshness_audit_report.json`: ok
- `scene_closeout_gate_report.json`: blocked; todos os passos operacionais passaram

Regra: cena so sobe de `testado_em_emulador` para `validado_budget` quando a evidencia mede a ROM vigente, o `app_scene_id` capturado bate com o esperado e o freshness nao aponta drift bloqueante.

## Cena de Branding Implementada

### Cena `APP_SCENE_BRANDING`

- `app_scene_id`: `0`
- papel: abertura cinematica de assinatura do laboratorio
- timeline NTSC:
  - engine: frames `0..149`
  - autor: frames `150..299`
  - projeto: frames `300..479`
  - teardown para boot: frame `480`
- identidade: forja industrial -> selo autoral em fosforo -> prensa de aprovacao
- runtime:
  - FSM explicita com `enter/update/exit` por slot
  - tres fundos, tres logos, `PRESENTS` e tres fontes bitmap carregados scene-local
  - spark 4 frames, monograma 12, cursor 3, escudo 4, glow 1 e debris 4
  - line scroll com buffer estatico de 224 words e `DMA_QUEUE`
  - cycling, cooldown, shimmer, flash e fade de paleta
  - cinco cues PCM XGM2 com reforco PSG
- budget:
  - grafo `21/21`, zero overlap de VRAM
  - audio estimado em `30.691` bytes (`0,73%` de 4096 KB)
  - captura BlastEm final: 151 frames observados, CPU medio/p95/max `6%`
  - zero frames acima do threshold
  - picos de design: engine 13 sprites, autor 3, projeto 9; probe MDRT atual nao mede SAT real
- evidencia:
  - preview dos tres slots: `out/evidence/blastem_branding_v3_final/three_slot_preview.png`
  - autor final: `out/evidence/blastem_branding_v3_final/author_reveal.png`, `author_hold.png`
  - projeto final: `out/evidence/blastem_branding_v3_final/project_hold.png`
  - canonica: `out/logs/blastem_evidence.json`, `out/logs/emulator_session.json`
  - performance: `out/logs/runtime_metrics.json`
  - visual delivery: `out/logs/visual_delivery_gate_report.json`
- status: `testado_em_emulador`, `validado_budget` e `cabe` para a cena 0; conceito/direcao visual aprovados, closeout bloqueado por GDD minimo e assets `needs_review` para AAA.

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

- classe de problema: gameplay inicial com contrato de prova tecnica e visual
- papel: gameplay
- objetivo visual: provar o loop central sem esconder custo real de VRAM, DMA e sprites
- papel no projeto: primeira entrega jogavel com evidencias minimas rastreaveis
- budget alvo:
  - preload honesto dos assets da cena
  - zero DMA fora de VBlank
  - overlay tecnico fora do plano rolavel
- resource_budget_model:
  - `scene_local_scope`: mapa inicial, actor principal, HUD seguro e efeitos minimos
  - `rom_asset_cost`: `nao_medido`
  - `vram_resident_set`: tiles do slice, fonte/HUD em `WINDOW`, sprites do loop base
  - `load_time_dma_cost`: permitido apenas na entrada da cena
  - `per_frame_dma_cost`: `nao_medido`
  - `active_animation_window`: manter residente so o que participa do loop central
  - `scanline_sprite_pressure`: `nao_medido`
  - `runtime_loading_model`: `scene_local_preload`
  - `fallback_plan`: simplificar composicao antes de vender efeito caro como default
- riscos de VDP:
  - HUD em plano rolavel
  - budget invisivel no doc
  - prova jogavel sem evidencia em BlastEm
- contrato de evidencia:
  - screenshot dedicada em BlastEm
  - `save.sram` com bloco canonico `MDRT`
  - `visual_vdp_dump.bin` quando o fluxo visual canonico estiver habilitado
  - regressao deterministica chegando na cena jogavel
