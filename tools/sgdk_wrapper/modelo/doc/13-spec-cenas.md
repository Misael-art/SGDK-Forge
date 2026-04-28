# 13 - Especificacao Tecnica por Cena - __PROJECT_NAME__

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
