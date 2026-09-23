# 13 - Especificacao Tecnica por Cena - __PROJECT_NAME__

> Documento canonico para budgets por cena, contrato de evidencia e papel formal de cada surface.
> Menu, title screen e outras telas de front-end contam como cenas formais.

## scene_roadmap

### Cena 0 - `branding_sequence`

- nome de trabalho: `branding_sequence`
- runtime_name na ROM: `APP_SCENE_BRANDING`
- `app_scene_id`: `0`
- `warmup_frames` inicial de contrato: `90`
- papel: abertura/assinatura
- objetivo: provar a sequencia padrao engine/autor/projeto antes do boot normal
- dependencia principal: `branding_sequence_contract.json`

### Cena 1 - Front End Curado

- nome de trabalho: `front_end_main_menu`
- runtime_name na ROM: `front_end_main_menu`
- `app_scene_id`: `1`
- `warmup_frames` inicial de contrato: `90`
- papel: menu
- objetivo: provar que o front-end ja nasce como showcase e ferramenta operacional
- dependencia principal: `front_end_profile`

### Cena 2 - First Playable Slice

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

- `scene_contract_compile_report.json`: [pendente/ok/stale/falha]
- `res_graph_report.json`: [pendente/ok/stale/falha]
- `validation_report.json`: [pendente/ok/stale/falha]
- `runtime_metrics.json`: [pendente/ok/stale/falha]
- `scene_regression_report.json`: [pendente/ok/stale/falha]
- `emulator_session.json`: [pendente/ok/stale/falha]
- `freshness_audit_report.json`: [pendente/ok/stale/falha]
- `scene_closeout_gate_report.json`: [pendente/ok/falha]

Regra: cena so sobe de `testado_em_emulador` para `validado_budget` quando a evidencia mede a ROM vigente, o `app_scene_id` capturado bate com o esperado e o freshness nao aponta drift bloqueante.

## Detalhamento do Slice Inicial

### Cena 0 - `branding_sequence`

- classe de problema: abertura de assinatura com assets reais, scroll/paleta e audio XGM2
- papel: abertura/assinatura
- objetivo visual: apresentar engine, autor e label do projeto sem depender de texto placeholder dominante
- papel no projeto: primeira cena da ROM, antes do boot/menu
- budget alvo:
  - preload local dos cinco `IMAGE` atuais de branding
  - nenhum sprite runtime no baseline
  - zero DMA por frame; animacao por scroll, HScroll line table e CRAM CPU writes
  - audio por WAV XGM2 13300/6650 com PSG tonal como reforco
- resource_budget_model:
  - `scene_local_scope`: `brand_fx_tiles`, logos engine/author/project, presents text e cinco WAVs XGM2
  - `rom_asset_cost`: medido por `res_graph_report.json` e `audio_validation_report.json`
  - `vram_resident_set`: BG_A/B com 347 tiles unicos estimados no baseline atual; sprite reserve default 420
  - `load_time_dma_cost`: permitido apenas na entrada/troca de slot
  - `per_frame_dma_cost`: zero declarado no baseline
  - `active_animation_window`: palette cycling, VScroll/plane scroll e HScroll line no slot project
  - `scanline_sprite_pressure`: 0 sprites no baseline
  - `runtime_loading_model`: `scene_local_preload`
  - `fallback_plan`: manter PSG/scroll/palette baseline e nao promover monograma/sprites 3D sem novo budget
- riscos de VDP:
  - `HSCROLL_LINE` precisa resetar para `HSCROLL_PLANE` no teardown
  - texto temporario do cursor em BG_A deve permanecer fora de claims AAA visuais
  - `visual_vdp_dump.bin` pode ser opcional se a evidencia canonica corrente for MDRT + screenshot, mas ausencia deve ser registrada
- contrato de evidencia:
  - screenshot dedicada em BlastEm no `APP_SCENE_BRANDING`
  - `save.sram` com bloco canonico `MDRT`
  - `runtime_metrics.json` com `scene_id=0`
  - `audio_validation_report.json` depois dos WAVs XGM2
  - `freshness_audit_report.json` e `scene_closeout_gate_report.json`

### Cena 1 - `front_end_main_menu`

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

### Cena 2 - `first_playable_slice`

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

## Vibe Playable Birth Defaults

- `visual_route_required=unknown_until_router`
- `critical_asset_default_status=blocked_no_premium_source`
- `runtime_evidence_default_status=missing`
