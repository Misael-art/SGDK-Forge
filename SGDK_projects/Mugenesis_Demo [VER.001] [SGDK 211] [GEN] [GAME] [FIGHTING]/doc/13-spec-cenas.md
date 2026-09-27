# 13 - Especificacao Tecnica por Cena - Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

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

### Adendo de cena — Suzaku Castle (pre-producao, atualizado em 2026-09-26)

- Estado atualizado 2026-09-26: frame âncora source-derived de 8 cores integrado em BG_B com lutadores/HUD; câmera/parallax e arte expandida continuam pendentes.
- Canvas: Mega Drive H40 320x224; `localcoord` da fonte 320x240; recorte superior16 e provisório até revisão do horizonte e dos pés.
- Mundo proposto: 768 px, câmera `[0,448]`, início224; runtime permanece atualmente em 640 px. O contrato `doc/camera_behavior_contract.json` separa o estado proposto do que já roda.
- Candidato BG_A: `BG 3` linhas `[0,176)` delta0.671875; `BG 4a` `[176,212)` delta0.792410; `BG 4b` `[212,224)` delta1.102678, por `line_scrolling` (`LINE_SCROLL`, `PARALLAX`). Nenhuma tabela ou custo DMA foi implementado.
- BG_B e transparência: a composição estática exige mais de dois grupos de velocidade em 72/32/72 scanlines nas câmeras left/center/right, até quatro; uma partição em BG_A/B ainda não foi construída. Correção técnica: `BG 3 mask=1` é representável porque color code 0 nos planos MD é transparente e revela a camada inferior (Genesis Software Manual, rev. 1992-02-20, p.62; nota/hash em `rascunho/entrada_bruta/sega_genesis_software_manual_transparency_note_2026_09_25.md`).
- O agregado anterior de três câmeras foi substituído por sweep de todas as 449 posições inteiras: 32.184.320 amostras visíveis. O perfil discreto remapeia 5,03%, com erro médio estimado 0,02415 px/amostra/frame e drift máximo 45px; o perfil minimax com velocidades intermediárias remapeia 14,33%, erra 0,04757px/amostra/frame e limita o máximo a 22,5px. Ambos alteram a relação telhado/castelo nas bordas; nenhum foi aprovado ou promovido. Relatórios/hash e análise em `doc/mugen/stage_suzaku_route_2026_09_25.md`.
- Perfis semânticos layer-aware de 2026-09-26 localizaram os conflitos em y0–111: y0–39 tem três speeds, y40–111 tem quatro, y112–175 tem dois e as faixas 176–223 mostram uma layer por linha. `castle_anchor_front_preserve` mantém BG2/BG3 e move sky/BG1 (43,73% das amostras; drift120,5px; lua parcialmente cortada). `sky_anchor_castle_front_merge` mantém o céu e junta castelo/muro/telhado (28,57%; drift45px; vazio magenta no extremo direito). Ambos passam a contagem de dois rates, mas falham a leitura/coverage em seus previews e seguem rejeitados em `rascunho`; nenhum perfil define ownership BG_A/B ou prioridade. Detalhes e hashes: `doc/mugen/stage_plane_ownership_study_2026_09_26.md`.
- BG5: três eventos com 51 frames, 278 ticks e janelas BGCtrl no relatório `rascunho/processado/stage_takeover/suzaku_measure_v2.json`. A conversão precisa preservar a agenda e offsets; não está em ROM.
- Budget atual: estudo anterior estimou 446 tiles de palco e até845 padrões visíveis na rota composta; a estimativa de source pattern do relatório novo é diferente e não substitui ResComp/viewport. Errata: o retângulo WINDOW y=0..55 não deve ser contado como oclusão opaca; a HUD limpa o mapa e desenha células esparsas. Usar o frame completo ate uma captura do stage com VDP/mapa provar outra mascara. A paleta atual reserva PAL0 slots1..8 ao palco e9..15 ao HUD; a candidata de15 cores requer migrar/revisar HUD e FX (hoje em PAL3) antes da integração. `scene_tilemap_conversion_report`, `per_tile_palette_conflict_report`, `tilemap_flag_report`, orçamento H-scroll e janela simultânea permanecem pendentes.
- Técnicas declaradas para investigação: `dma_transfer_safety`, `camera_scroll_management`, `line_scrolling`, `advanced_tilemap_design` e `palette_state_transitions`; owners e evidência em `doc/technique_usage_manifest.json` e `doc/tdd_contract.json`.
- Alternativas para liberar recursos (multiplexar sombras separadas durante pico medido, reusar valores CRAM existentes sem escrever sobre HUD, multiplexar apenas adornos de especiais e outras opções de tile/FX) estão catalogadas como fallback condicional em `doc/mugen/vdp_optimization_options_2026_09_26.md`; nenhuma foi testada nem autoriza flicker do corpo dos golpes.
- Rascunho de storyboard para revisão: `doc/mugen/suzaku_plane_storyboard_draft_2026_09_26.json`. Propõe BG_B céu/lua a delta0 e BG_A castelo/muro/telhado a delta0.671875 até y175; documenta viewport/HUD, posições iniciais, prioridade baixa dos backgrounds MUGEN layerno0 e lacunas ainda abertas. Próximo passo é revisar a 1x e completar ownership/prioridade por tile, contato dos pés e bleed/fill sob HUD/fighters; só então fechar contrato de asset e medir ResComp, paleta por tile, residência e DMA/VBlank. Não usar nenhum perfil de scroll como asset pronto.
- Fallback: manter fundo atual e mundo640 enquanto paleta, composição, câmera e orçamento não fecharem. Nenhum recuo pode remover o piso de luta ou quebrar contato visual.
- Fechamento obrigatório: ROM exata em BlastEm; câmera centro/cantos/reversão/push/super; sem costura/tremor; HUD fixa; DMA/VRAM/scanline medidos; áudio habilitado e ouvido; review visual hash-bound.

#### Atualização de produção medida — 2026-09-26

- Existe agora uma tradução estática de staging world640 para os planos BG_B/BG_A em `rascunho/processado/stage_takeover/suzaku_panorama_world640_6color_simplified_locked_palette_planes_20260926/`. Isso resolve a ausência de uma partição visual de estudo, mas não substitui o contrato de câmera de 768px nem altera o runtime de 640px.
- Com a paleta anterior fixada, ResComp 3.95 mediu BG_B=186 e BG_A=252, total 438 tiles e 15.876 bytes; o controle achatado mede 408 tiles/14.648 bytes e perde o scroll independente. A estimativa de capacidade é 446, deixando oito tiles estimados; não é evidência de residência em runtime. Relatório reproduzível: `rescomp_measurement_report.json` e `scene_tilemap_conversion_candidate_report.json` no diretório candidato.
- A auditoria percorreu todos os tiles 8x8: zero conflitos de paleta, máximos de quatro índices visíveis em BG_B e cinco em BG_A. O contrato de transparência usa índice 0 somente em BG_A; BG_B deixa o índice 0 sem uso. Relatório: `per_tile_palette_conflict_report.json` no mesmo diretório.
- O MAP gerado ainda tem metatiles/blocos APLIB-packed; não emitimos `tilemap_flag_report` porque tile_index, palette, priority e flips por célula ainda não foram decodificados. Residência, câmera/parallax, seams, DMA/VBlank, scanline, BG5, áudio, aprovação visual e BlastEm permanecem sem prova. A comparação e os limites estão em `doc/mugen/suzaku_candidate_review_2026_09_26.md`.
- Portanto o estado continua pré-produção: nenhum asset foi promovido para `res/`, nenhuma ROM foi construída com este palco e não existe aprovação estética.
- A composição source-derived da camera224 mede 758 tiles pareados em 15 cores (26.736 bytes) e 685 em 8 cores (24.182 bytes). As medições clipped de 516/506 dependem da premissa de opacidade total do WINDOW, agora inválida; ver errata hash-bound em `rascunho/processado/stage_takeover/suzaku_visible_window_residency_20260926_v2/visible_window_report_erratum_20260926.json`.

#### Comparação V1/V2/V3 e mock de contexto — 2026-09-26

- Um segundo conceito mais detalhado do castelo foi testado em 8 cores: 1.664 tiles pareados (BG_B 1.352 + BG_A 312), 58.342 bytes e 1.218 tiles acima da estimativa. Rejeitado para residência com o pool atual; prova que menor erro/mais detalhe pode ser uma rota inviável.
- A alternativa V3 usa nuvem/lua/montanha sobre uma cor-base VDP declarada. Após correção do contrato de opacidade do BG_B, a reconstrução dos planos teve zero mismatch. ResComp 3.95 mediu V3 locked-six em 446 tiles pareados (194+252), exatamente a estimativa de capacidade; flat em 391. Weighted-eight mede 571 tiles (269+302), 125 acima. V3 locked-six tem weighted MSE337,696 contra V1 362,218, mas igualdade ao teto estimado não significa margem segura.
- Mock estático `suzaku_visual_context_mock_20260926.png` compara V1, V3 locked-six e V3 weighted-eight sobre HUD/lutadores de uma captura antiga. É apenas leitura de contraste/composição; não é ROM atual, evidência BlastEm ou aprovação visual. Relatório/hash em `suzaku_visual_context_mock_report.json`.
- A folha anterior de três câmeras sobrepostas repetia landmarks visualmente por usar janelas que se sobrepõem em 160px; a leitura de repetição foi corrigida com coordenadas da fonte antes de qualquer substituição. Análise e hashes em `doc/mugen/suzaku_candidate_review_2026_09_26.md`.
- V3 locked-six é o candidato de arte/custo para próxima revisão; ainda precisa de folga real, tela 1x, MUGEN camera sweep/world-width decidido, tile flags MAP decodificados, residência/DMA/VBlank/scanline, BG5, música e prova BlastEm. Nenhum candidato está em `res/`.
- A separação BG_A/B do V3 reconstrói a imagem com zero pixels divergentes; auditoria de cada 8x8 encontrou zero conflitos de paleta (máximo 2 índices visíveis em BG_B, 5 em BG_A). `per_tile_palette_conflict_report.json` e `scene_tilemap_conversion_candidate_report.json` ficam sob o diretório de planos V3. O relatório de flags de MAP continua ausente por falta de decodificação APLIB validada.

## Vibe Playable Birth Defaults

- `visual_route_required=unknown_until_router`
- `critical_asset_default_status=blocked_no_premium_source`
- `runtime_evidence_default_status=missing`
