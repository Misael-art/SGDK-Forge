---
name: megadrive-vdp-budget-analyst
description: Analisa VRAM, DMA, sprites, paletas, scroll, scanline pressure, H-Int singleton budget, giant boss plane takeover e worst-frame cost para hardware real do Mega Drive.
---

# Mega Drive VDP Budget Analyst

Use esta skill antes de aprovar efeitos visuais, assets, transicoes ou mudancas de render.

## Verifique sempre

- VRAM total e tiles residentes
- teto real de tiles uteis antes da regiao de mapas do VDP
- DMA por VBlank
- sprites por scanline
- total de links de sprite
- uso de PAL0-PAL3
- H-Int unico por frame
- custo de line scroll e column scroll
- particao real entre background e sprite engine
- custo de enxerto de sprites para simular profundidade extra
- custo de animacao de tiles em VRAM por VBlank
- largura real do stage versus teto pratico do plano antes de streaming
- worst-frame budget quando a cena tiver dois lutadores, HUD e FX grandes
- separacao entre custo ROM, set residente em VRAM, DMA de preload e DMA por frame
- `vram_residency_report` para cenas com personagens grandes, dois lutadores, HUD e FX; `res_graph_report` sozinho so prova existencia de recursos, nao prova que o resident set cabe
- `sprite_scanline_pressure_report`, `palette_slot_audit`, `h_int_ownership_map`, `vram_residency_report` e `constraint_budget_report` quando a cena pedir entrega AAA/stable/release ou envolver VDP pesado

## Decisao

Responda sempre em um destes formatos:

- `cabe`
- `cabe com recuo`
- `nao cabe`

Se responder `cabe com recuo`, explicite qual recuo desbloqueia a cena:

- reduzir tiles unicos do background
- reorganizar paletas em `3+1`
- ajustar reserva do sprite engine com `SPR_initEx(u16 vramSize)`
- mover parte da profundidade para `sprite grafts`
- promover a prova de ROM para `compare_flat`

Antes do parecer, confira `tdd_contract.json > technique_selection.application_plan`.
Tecnica sem funcao de gameplay/narrativa, owner, budget/evidencia e fallback recebe
`nao cabe` como decisao metodologica, mesmo que pareca caber isoladamente.

## Resource Budget Semantics

Todo parecer deve separar limite fisico, residencia e custo por frame. Nao reprovar uma proposta so porque "o mundo inteiro nao cabe residente" antes de avaliar escopo local, preload, streaming e janela ativa.

Termos canonicos:

- `rom_asset_cost`: custo do asset compactado ou bruto em ROM; `FAST`, `BEST` e `NONE` mudam ROM/decompress/load behavior, nao o numero final de tiles descompactados que ocupam VRAM.
- `vram_resident_set`: tiles, fontes, sprites, mapas e tabelas que precisam estar simultaneamente residentes na cena atual.
- `load_time_dma_cost`: uploads feitos em boot, loading screen, troca de cena ou trecho sem gameplay responsivo; pode ser alto se houver tela/estado de carregamento honesto.
- `per_frame_dma_cost`: uploads por VBlank durante gameplay ou controle ativo; deve caber no pior quadro sem roubar uploads criticos.
- `active_animation_window`: subconjunto de frames/ciclos realmente necessario no intervalo atual; nao confundir sheet completa do personagem com residencia obrigatoria.
- `scene_local_scope`: assets permitidos para a cena/fase atual; assets de outra cena devem sair do budget residente.
- `scanline_sprite_pressure`: limite perceptivo e fisico de sprites por scanline; multiplexing/flicker e tradeoff declarado, nao mascara de overflow.

Regra de leitura de sprites:

- `SPR_getUsedVDPSprite()` informa uso total/maximo de sprites VDP pelas sprites ativas, nao pressao por scanline.
- nunca preencher `max_sprites_per_scanline` com esse valor; claim de scanline precisa vir de `vdp_scanline_simulator.py`, dump/telemetria equivalente ou auditoria de pior quadro com posicoes reais.
- total de sprites VDP e limite por scanline sao dois eixos separados: passar em 80 sprites totais nao prova que cada linha ficou abaixo de 20, e bater 20 numa linha nao significa que a cena usou apenas 20 sprites no total.

Regra de eixo de scroll:

- bandas horizontais de parallax pertencem a `HSCROLL_LINE` ou `HSCROLL_TILE`, com dono unico da tabela de HScroll e limites de banda autorados na arte.
- `VSCROLL_COLUMN` altera offset vertical por colunas; nao deve ser usado como atalho para velocidades horizontais por faixa.
- se uma cena combina HScroll, shake, estrada, horizonte ou foreground, o laudo deve declarar qual sistema escreve a tabela de scroll e como evita rasgar silhuetas nos limites das bandas.

## Curadoria 2026-06-03: sprites grandes, CRAM e DMA

Quando o projeto usar tecnicas do lote `curation_2026_06_03_megadrive_video_text_batch`, trate o material como curadoria rica, mas nao como prova operacional. A decisao maxima continua limitada pelo registry e pela evidencia real.

- `large_metasprite_vblank_fit_audit`
  - calcular `tiles_unicos_do_frame * 32` antes de aprovar qualquer upload de frame de sprite;
  - comparar o pior frame com o envelope seguro de DMA por VBlank declarado no projeto;
  - se o frame nao couber, responder `nao cabe` ou `cabe com recuo` usando `animation_window_streaming`, partes estaticas, reducao de tiles ou preload honesto.
- `sprite_frame_vram_slot_streaming` e `animation_lookahead_dma_queue`
  - exigir `active_animation_window`, mapa de slots fixos de VRAM, proximo frame previsto e `dma_queue_contract`;
  - delayed update so e aceitavel para animacao nao critica; hitbox, input, hitstop e leitura de golpe nao podem atrasar sem contrato.
- `rescomp_metasprite_decomposition_audit`
  - exigir decomposicao em hardware sprites, bbox transparente cortado, tiles unicos e `sprite_scanline_pressure_report`;
  - nao aceitar atlas grande ou screenshot como prova de que o metasprite cabe.
- `sprite_band_slot_allocator`, `ghost_afterimage_sprites` e multiplexing
  - medir HUD, personagens, projeteis, FX e afterimages no mesmo pior scanline;
  - personagens principais, HUD e projeteis criticos precisam de reserva explicita de slots.
- `cram_dot_masking_strategy` e `hint_palette_blending`
  - mid-frame CRAM write exige mapa de linhas, owner unico de H-Int, plano de mascara e screenshot BlastEm;
  - CRAM dots nao podem ser ignorados so porque outro emulador nao mostrou o artefato.
- `sat_double_buffering` e `sprite_midframe_sat_reuse`
  - sempre `LABORATORIO`; nao aprovar entrega sem benchmark isolado, ausencia de corrupcao de SAT e conflito zero com `SPR_update`.

## Contrato Operacional

### Entrada minima

- `resources.res`
- dimensoes dos assets promovidos
- `build_output.log` quando existir
- configuracao real de `SPR_initEx`
- layout real de planos
- `ui_decision_card` quando houver HUD/UI formal
- `text_presentation_profile` quando texto, fala, alerta cinetico ou flavor tiver peso dramatico
- `cutscene_scene_contract`, `cutscene_resource_plan`, `cutscene_palette_script` e `cutscene_text_timing_map` quando houver abertura, cutscene, cena de contexto, briefing ou final
- `asset_optimization_report` quando houver compressao `.res`, dedup/reuse ou alegacao de economia ROM/VRAM
- para cenario/tilemap critico (>=320x224, ou tecnica declarada, ou entrega): ler `scene_tilemap_conversion_report.json` e nao declarar `validado_budget` sem ele
- quando houver dedup/HV flip ou otimizacao de tilemap: exigir `tilemap_flag_report.json`
- exigir `per_tile_palette_conflict_report.json`; `conflicts_total > 0` bloqueia entrega
- `scene_transition_card` quando houver transicao formal
- `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` ou `audio_architecture_card` quando houver espetaculo runtime formal
- `scene_direction_record`, `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` e `background_ecology_card` quando houver cenario monumental, signature-only, bioma-chave ou setpiece de fundo

### Saida minima

- laudo deterministico `cabe`, `cabe com recuo` ou `nao cabe`
- numeros de VRAM usados no parecer
- separacao explicita entre `rom_asset_cost`, `vram_resident_set`, `load_time_dma_cost`, `per_frame_dma_cost`, `active_animation_window`, `scene_local_scope` e `scanline_sprite_pressure`
- `budget_decision` alinhado ao `ui_architecture_choice` quando houver UI formal
- `budget_decision` alinhado a paineis, baloes, retratos, texto cinetico, glyph cache e SFX de texto quando houver apresentacao expressiva
- `budget_decision` alinhado ao resource plan por estado quando houver cutscene
- leitura de `asset_optimization_report` separando compressao ROM/load de tiles residentes em VRAM
- `budget_decision` alinhado ao `continuity_model` quando houver transicao formal
- `budget_decision` alinhado aos cards de feedback FX, boss/setpiece, tilemap avancado e audio senior quando existirem
- `budget_decision` alinhado ao `scene_direction_record` e aos cards de cenario monumental quando existirem
- decisao explicita se o perfil `monumental` cabe, precisa de recuo ou deve ser rebaixado para `competent`
- `glyph_budget_class` alinhado ao `font_render_mode` quando houver anexo tipografico
- leitura de `runtime_metrics.json` quando a ROM ja foi capturada
- decisao sobre `over_budget_frames`, `cpu_load_max`, piores quadros e tradeoff de preload/streaming
- decisao explicita sobre `vram_residency_status` quando houver sprites grandes ou garbage tiles na captura
- `res_graph_report.vram` com `tile_ranges`, `sprite_reserve_tiles` e `overlaps[]` quando a cena usa BG_A/B mais Sprite Engine; qualquer overlap com reserva de sprites/fonte exige recuo antes de delivery
- se `res_graph_report.method=no_res_files`, isso significa `asset_pipeline_not_started`, nao budget validado
- se `res_graph_report.vram.status=code_loaded_tiles_unmeasured`, tiles carregados/desenhados por C ainda precisam de budget proprio, screenshot util e/ou dump VDP antes de `validado_budget`
- `sprite_scanline_pressure_report` gerado ou conferido com `tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py` quando houver sprites, boss modular, projeteis, FX ou HUD por sprites
- `dma_queue_contract` e plano gerado por `tools/sgdk_wrapper/.agent/scripts/dma_queue_planner.py` quando houver upload por VBlank, preload ou streaming
- exemplos canonicos em `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/examples/`

## Fechamento por Evidencia

- `cabe` documental nao promove `validado_budget`; precisa de ROM capturada sem over-budget no intervalo alvo
- se `runtime_metrics.json` apontar `over_budget_frames > 0`, a decisao maxima e `cabe com recuo` ate nova captura provar o contrario
- se `cpu_load_max` exceder o alvo de 60fps, priorize reduzir redraw, DMA por frame, sprites por scanline ou janela ativa antes de aumentar complexidade visual
- apos nova captura, rode `freshness_audit.ps1` para garantir que o laudo de budget e a evidencia medem a mesma ROM
- recuo explicito quando necessario

### Passa quando

- o parecer consegue ser reconstruido por outra IA a partir dos mesmos numeros
- o laudo identifica claramente se o problema dominante e asset, recurso SGDK ou arquitetura
- o laudo nao confunde asset compactado em ROM com tiles residentes em VRAM
- o laudo nao confunde `res_graph_report` com prova de VRAM; ele deve estimar BG_A/BG_B, fonte/HUD, sprite engine, P1/P2 e FX simultaneos
- o laudo nao promove `validado_budget` quando nao ha `.res` e o runtime usa `VDP_loadTileData`, `TILE_USER_INDEX`, arrays de tiles ou nametable manual sem medicao de runtime
- o laudo nao aceita dedup, cache ou compressao como economia sem report medido; compressao `.res` nunca reduz automaticamente VRAM residente
- se `res_graph_report.vram.status=collision_risk` ou `overlaps[]` nao estiver vazio, a decisao maxima e `cabe com recuo` ate remapear planos, reduzir tiles unicos ou ajustar `SPR_initEx`
- o laudo nao confunde DMA de preload/loading com DMA por frame em gameplay
- o laudo considera scene-local loading, streaming e active animation window antes de concluir `nao cabe`
- quando houver UI formal, ownership e fallback nao contradizem o laudo
- quando houver texto expressivo, glyph cache, tiles temporarios, sprites, CRAM, SFX e teardown nao contradizem o laudo
- quando houver cutscene, o laudo mede cada estado da FSM separadamente e nao soma a cutscene inteira como se tudo estivesse residente
- quando houver transicao formal, `fx_ownership_map`, `teardown_reset_plan` e `fallback_plan` nao contradizem o laudo
- quando houver espetaculo runtime formal, pior quadro, scanline pressure, H-Int, CRAM, DMA, sprites, tile churn e audio ownership ficam auditados
- `sprite_scanline_pressure_report.max_sprites_per_scanline <= 20` e `total_sprite_links <= 80`
- `h_int_ownership_map` declara owner unico, teardown e fallback quando H-Int existir
- `palette_slot_audit` rejeita alpha blending real, slot de highlight estrutural inseguro em Shadow/Highlight e conflito PAL0-PAL3
- `dma_queue_planner.py` nao reporta `dma_outside_vblank` nem `vblank_dma_bytes_over_budget`
- HBlank DMA, active-display FIFO scheduling, CRAM overdrive, SAT rewrite mid-frame, direct vector patching, SMC e register pinning permanecem `LABORATORIO` ate benchmark isolado; nunca contornam a regra canonica de DMA seguro em VBlank
- quando houver `scene_direction_record`, o pior quadro inclui parallax, line scroll tables, H-Int/raster, palette cycling, tile mutation, ecology loops e teardown/reset
- `monumental_promised_without_budget` bloqueia `cabe` ate o laudo provar o custo ou rebaixar o perfil
- `mode7_claim_on_megadrive` bloqueia budget; use pseudo3d/line scroll/zmap real ou declare signature-only com fallback
- quando houver anexo tipografico, `glyph_manifest`, `charset_profile` e `fallback_font_plan` nao contradizem o laudo

### Handoff para proxima etapa

- entregar o laudo vigente para `sgdk-runtime-coder`
- bloquear runtime se o laudo nao existir ou estiver contradizendo codigo/docs
- quando houver UI formal, entregar o veredito junto do `ui_decision_card`
- quando houver UI pixel-perfect, health bar, fonte, caixa, micro-icone, cursor ou atlas de entrega, entregar o veredito junto do `ui_pixel_surface_contract`
- quando houver transicao formal, entregar o veredito junto do `scene_transition_card`
- quando houver cards de espetaculo runtime, entregar veredito junto dos cards e do pior quadro

## Quando houver HUD/UI formal

- ler `ui_architecture_choice` antes de aprovar custo
- ler `ui_pixel_surface_contract` quando existir e auditar atlas, surface VDP, paleta, fonte, motion inteiro e evidencia esperada
- usar `budget_decision` como veredito oficial do card
- se a rota for `window_plane_static_hud`, auditar `WINDOW fixa + oclusao de BG_A`
- se a rota for `sprite_hud`, medir scanline pressure contra o pior quadro de gameplay
- se a rota for `raster_enhanced_ui`, exigir `fx_ownership_map`, reset simetrico e fallback honesto
- se houver anexo tipografico, ler `font_render_mode`, `charset_profile` e `glyph_budget_class` antes de aprovar custo
- se houver `text_presentation_profile`, auditar `text_surface_class`, `layout_anchor`, `text_audio_plan`, `asset_budget_plan`, `teardown_reset_plan` e fallback
- `fixed_custom_hud_font`
  - auditar residency de tiles, custo de `WINDOW` e subset real de glifos
- `variable_width_tidytext`
  - auditar churn de tiles temporarios, DMA por update, cadence de redraw e reset do cache
- sem `glyph_manifest`, reprovar charset expandido ou compositor proporcional como rota canonica
- health bar reprova sem budget para container, buffer latente, fill ativo e low-HP feedback no pior quadro
- UI que depende de free-scale, subpixel motion ou interpolacao nao recebe aprovacao VDP; isso e erro de arte/runtime, nao budget
- `panel_sequence_text` reprova sem budget de tiles por painel e fallback
- `diegetic_speech_balloon` reprova se aumentar scanline pressure ou cobrir HUD/jogador sem politica
- `animated_portrait_dialog` reprova sem medir retrato, mouth frames, blink e cache residente
- `kinetic_hype_text` reprova se competir com gameplay ou depender de H-Int/CRAM sem owner
- `typewriter_voice_text` reprova se SFX de texto competir com dano, alerta ou boss cue

## Quando houver cutscene

- usar `cutscene_resource_plan` como fonte primaria de residencia por estado
- medir cada estado: BG_B/BG_A/WINDOW/sprites, glyph cache, retratos, mouth/blink frames, palette domains e FX
- diferenciar painel residente, painel streamado no load, pan de imagem alta e fullscreen justificado
- fullscreen bitmap so recebe `cabe` se tile count, paletas e fallback estiverem declarados
- H-Int/raster/palette split em cutscene exige owner unico e reset, mesmo fora de gameplay
- palette cycling e fade seletivo devem declarar quais slots mudam e quais surfaces sao afetadas
- `SAT reuse` e permitido apenas como tecnica opt-in de cena especial, com sprite engine controlado e evidencia em BlastEm
- texto temporizado precisa de budget de fonte/glyph subset e cadence de redraw; texto nao e custo zero
- se a cutscene depende de estado anterior sem `state_handoff`, a decisao maxima e `cabe com recuo`

## Quando houver transicao formal

- ler `continuity_model`, `player_control_policy`, `camera_motion_contract`, `fx_ownership_map`, `runtime_state_handoff`, `teardown_reset_plan` e `fallback_plan`
- usar `budget_decision` como veredito oficial do `scene_transition_card`
- `palette_fade_bridge`
  - auditar CRAM/audio fade e garantir que nao esteja mascarando uma transicao espacial que deveria ser planejada
- `spatial_scroll_bridge`
  - auditar mapa visivel, streaming, plane size, seam oculto e custo de camera no pior quadro
- `scripted_avatar_bridge`
  - auditar sprites, controle do jogador, colisao temporaria, camera scriptada e handoff de estado
- `tile_mask_mosaic_transition`
  - reprovar sem backup/restauro de tileset, budget de DMA, dirty region e fallback barato
- `raster_distortion_bridge`
  - reprovar sem owner unico de H-Int, reset de callback, custo de line scroll/VSRAM e prova de legibilidade
- `lighting_state_transition`
  - auditar CRAM, Shadow/Highlight, palette split, slots criticos e legibilidade de sprite/HUD
- `pseudo3d_perspective_bridge`
  - tratar como `advanced_tradeoff`; exigir budget proprio e fallback seguro
- sem `scene_transition_card`, reprovar transicao avancada como rota canonica

## Quando houver espetaculo runtime AAA

- ler `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` e `audio_architecture_card` quando existirem
- usar `budget_decision` como veredito oficial de cada card
- `feedback_fx_decision_card`
  - auditar H-Int, CRAM, VSRAM, sprite particles, tile particles, camera shake e reset
  - medir se FX compete com HUD, jogador, projetil ou hitbox no pior quadro
- `boss_setpiece_card`
  - auditar boss + jogador + HUD + projeteis + FX no mesmo scanline budget
  - se houver `plane_takeover`, declarar perda de parallax e custo de tiles residentes
- `advanced_tilemap_design_card`
  - auditar metatile reuse, streaming boundary, dirty uploads, foreground priority e colisao visual
  - separar mundo total, janela visivel, resident set local e DMA de streaming
  - reprovar streaming sem seam budget e fallback
- `route_decision_record`
  - confirmar se o modelo declarado (`full_resident`, `scene_local_preload`, `tilemap_streaming`, `animation_window_streaming`, `fallback_reduced_residency`) bate com os numeros medidos
  - bloquear runtime quando a rota declara streaming mas o budget foi calculado como imagem residente inteira, ou vice-versa
- `audio_architecture_card`
  - auditar ownership de canal, prioridade de SFX, ambience, stinger, pause/resume e custo de PCM
- sem card formal, reprovar tecnica avancada como rota canonica

## Quando houver cenario monumental

- ler `scene_direction_record` antes de validar `layer_plan`
- se `selected_profile=monumental`, exigir pelo menos um card aplicavel: `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` ou `background_ecology_card`
- se `selected_profile=signature_only`, exigir fallback e, quando aplicavel, experimental override
- `parallax_layer_contract`
  - auditar numero de layers, ratios, custo de line scroll table, seam policy e reset
- `palette_cycle_decision_card`
  - auditar slots CRAM, cadence, owner, conflito com player/HUD/FX e teardown
- `raster_fx_ownership_map`
  - auditar owner unico de H-Int, scanline ranges, VBlank updates e fallback se outro sistema precisar de H-Int
- `background_ecology_card`
  - auditar tile mutation, loops ambientais, event hooks, dirty uploads e se o efeito tem funcao de gameplay/narrativa
- se o custo real estourar, devolver `cabe com recuo` e registrar `monumental_downgrade_record`; nao permita que a cena continue como monumental capenga

## Tecnicas canonicas de extrapolacao segura

### Reparticao intencional de VRAM

- Nao orce contra `2048` tiles brutos como se todos fossem livres para arte.
- Orcar contra a faixa realmente util depois de BG_A, BG_B, window, hscroll, sprite table, fonte e sprite engine.
- Se o background legitimo pede mais tiles unicos do que a particao padrao comporta, preferir `SPR_initEx(u16 vramSize)` a aceitar corrupcao silenciosa.
- Se uma cena so estoura porque o projeto inteiro foi contado como residente, recortar por `scene_local_scope` antes de reduzir a ambicao visual.

**Formula de budget (SGDK 2.11):**
```
maps_addr = endereco mais baixo entre BGB, BGA, Window, SAT, HScroll tables
TILE_MAX_NUM = maps_addr / 32
User tiles = TILE_MAX_NUM - TILE_SYSTEM_LENGTH(16) - FONT_LEN(96) - SPR_initEx(N)
BG_A max = User tiles - BG_B tiles

Configs comuns (maps_addr = 0xC000 em todas):
  64x32 + SPR_initEx(128): user = 1296, com BG_B(242) → BG_A max = 1054
  64x32 + SPR_initEx(420): user =  948, com BG_B(242) → BG_A max =  706
  32x32 + SPR_initEx(128): user = 1296, com BG_B(242) → BG_A max = 1054
```
**OBRIGATORIO: calcular tile count com `rescomp` (IMAGE ou TILESET) ANTES de integrar arte.**

Para jogo de luta com dois personagens grandes:

- declarar `SPR_init` ou `SPR_initEx` usado no codigo
- declarar se strips inteiras ficam residentes ou se ha `active_animation_window`
- calcular pior quadro com P1 + P2 + HUD + hit spark + stage
- quando houver `animation_direction_contract`, calcular tambem custo do pior frame ativo: smear frame, hit spark, dust, flash/runtime CRAM, camera shake, hitstop hold e janelas de recovery que mantem sprites/FX ativos
- quando houver `modular_boss_rig_contract`, calcular boss por partes ativas, pivots, sobreposicao por scanline, CRAM compartilhada e janela de animacao; nao tratar full-body reference como residencia obrigatoria se o runtime usa rig segmentado
- se a screenshot mostrar garbage tiles/faixa corrompida, status maximo e `nao cabe` ou `cabe com recuo` ate haver nova captura limpa
- recuos canonicos: limpar strips, reduzir frame envelope, separar FX, usar `SPR_initEx`, reduzir plane size, reorganizar enderecos de plano, ou streaming por janela ativa

### `Plane size tuning`

- O VDP nao exige sempre o maior mapa possivel para BG_A e BG_B.
- Se a fase nao precisa de toda a extensao vertical ou horizontal, reduzir `VDP_setPlaneSize(..)` e uma forma limpa de recuperar espaco de tabela.
- Isso e tecnica canônica e segura quando o tamanho menor cobre o scroll real da cena.
- Em SGDK, trate isso como primeira resposta estrutural antes de hacks mais agressivos.

### Paleta `3+1`

- Se um foreground importante precisa de identidade propria, considere fundo em 3 paletas e reserve 1 para o elemento de frente.
- Isso melhora composicao sem fingir que o VDP ficou maior.

### `Sprite grafts` para profundidade

- O Mega Drive nao ganha terceira layer real.
- Mas elementos intermediarios podem virar sprites auxiliares para simular profundidade adicional.
- So e canônico se passar em sprites por scanline, total de sprites na tela, custo de VRAM e ausencia de flicker.

### `compare_flat` para prova em ROM

- Se um comparativo multi-plano e didatico offline, mas estoura o budget real em ROM, a prova em emulador pode usar `compare_flat` single-plane.
- Isso e aceitavel quando a memoria operacional registra a decisao e a curadoria offline preserva `original + basic + elite`.

### Animacao de background via VRAM

- Antes de aprovar sprite decorativo so para "animar o fundo", medir se a troca de tiles em VRAM resolve o mesmo efeito com menos pressao de scanline.
- Isso move custo de SAT/sprites para DMA/VBlank e residency de tiles.
- E tecnica `canonica_segura` quando:
  - a troca cabe no VBlank
  - os tiles animados sao residentes ou streamados com seguranca
  - o efeito nao compete com uploads mais criticos do frame

### Streaming de tilemap para stage largo

- Cena acima do teto pratico do plano nao deve depender de wrap acidental.
- Se o stage passar de ~512 px no arranjo do plano usado, tratar streaming guiado pela camera como resposta canônica.
- Imagem/painel grande nao deve ser reprovado nem aprovado pelo tamanho total antes de medir a janela ativa e a topologia de paineis.
- Quando `scene_tilemap_conversion_report.conversion_target=world_tilemap_with_camera_window_streaming`, o report deve declarar `world_dimensions`, `viewport_dimensions` e `runtime_streaming`; campos soltos herdados de experimento nao substituem contrato.
- `BIN_CUSTOM_TILE_GRAPHICS_AND_TILEMAP_WINDOW_STREAMING` descreve empacotamento/rota de runtime, nao prova residencia. Se `res_graph_report` classificar os bins customizados sem medir `VDP_loadTileData`, a decisao maxima e `needs_review` ate existir `visual_vdp_dump`, telemetria VDP/VRAM ou `vram_residency_report` vinculado ao hash da ROM.
- Medir:
  - tamanho do mundo total
  - tamanho da janela visivel
  - candidatos de painel/metatile
  - tiles unicos por candidato no pior trecho
  - resident set simultaneo de BG_A + BG_B + sprites + fonte/HUD
  - bytes por coluna ou bloco
  - tolerancia de velocidade da camera
  - risco de seam

### Painel, mosaico e detalhe central

Para cenas AAA com fonte grande, parallax, foreground/oclusao ou inspiracao em engines internas como BLAZE_ENGINE, o budget deve avaliar a tecnica, nao copiar cegamente o tamanho do asset:

- extrair o principio estrutural da referencia: fatias, cache rotativo, paineis, metatiles, prioridade de foreground, seam escondido
- medir pelo menos 2-3 candidatos de painel antes de escolher a rota
- privilegiar maior detalhe na regiao central/critica da camera e simplificacao honesta nas bordas ou fundos distantes
- separar `world_total_unique_tiles` de `resident_window_unique_tiles`
- bloquear `IMAGE` full-resident quando o board inteiro estoura mas uma janela streamada caberia com margem

Se o laudo disser `nao cabe`, ele deve dizer qual das opcoes falhou: resident set local, DMA por frame, seam/camera, sprites/scanline, paleta ou runtime complexity. Sem isso, o parecer ainda esta incompleto.

### Streaming de animacao e janela ativa

- Sheet completa de personagem nao precisa estar inteira residente se o runtime usa janela ativa, SGDK auto VRAM alloc ou streaming manual validado.
- Medir:
  - frames residentes no pior estado de gameplay
  - tiles unicos do ciclo ativo
  - DMA de troca de frame quando houver upload dinamico
  - fallback para reduzir frames, cadence ou variacao se o pior quadro estourar
- Multiplexing ou flicker controlado so pode entrar para efeito nao-critico; nunca para heroi, hitbox, golpe-chave ou leitura essencial.

### Gate de verdade para raster e paleta

- Efeito raster ou palette split que so "parece bom no editor" nao existe ainda.
- BlastEm e o minimo de gate.
- Se a cena depender fortemente do comportamento mid-frame, pedir tambem prova em hardware real quando possivel.

## Tecnicas avancadas com gate forte

### `Window alias`

- O VDP permite reposicionar a tabela da Window; em teoria ela pode apontar para a mesma regiao de outro plano quando a Window nao estiver sendo usada.
- Isso so entra como tecnica avancada quando:
  - a Window estiver realmente fora da cena
  - nao houver HUD, console, texto de debug ou rotina escrevendo em `WINDOW`
  - a decisao estiver registrada na memoria operacional
- Em SGDK, isso nao e default seguro porque o ecossistema assume layout classico e pode usar `WINDOW` em fluxos auxiliares.

### `H-Scroll slack reuse`

- Em modo `HSCROLL_PLANE`, a tabela de H-Scroll consumida em runtime e menor do que nos modos por tile ou por linha.
- O espaco restante pode parecer reutilizavel, mas isso so e aceitavel quando:
  - a cena estiver travada em `HSCROLL_PLANE`
  - nao houver transicao futura para `HSCROLL_TILE` ou `HSCROLL_LINE`
  - a prova em BlastEm confirmar que nada alem do trecho inicial esta sendo lido
- Trate como tecnica de cena fechada, nao como politica geral de layout.

### Shadow/Highlight ambiental por background

- Beam, fog, smoke ou glow que precisam atravessar fundo e sprite juntos podem justificar Shadow/Highlight de background.
- Isso alivia sprite pressure, mas passa a cobrar:
  - tilemask
  - composicao de planos
  - auditoria de slot de paleta do sprite
  - custo de line scroll se a mascara precisar fugir do 8x8 duro
- Tratar como `avancada_com_tradeoff`.

### Worst-frame budget

- Em jogo de luta, boss fight ou FX massivo, nao orcar por frame "bonito" isolado.
- Orcar pelo pior quadro:
  - dois personagens
  - HUD
  - golpe ou magia
  - hit spark e sub-FX
- Port 1:1 de Neo Geo ou arcade pesado deve ser considerado suspeito ate passar nesse orçamento.

## Tecnicas opt-in de cena especial

### `SAT reuse`

- A Sprite Attribute Table pode parecer reaproveitavel em titulo, menu ou cutscene com poucos sprites.
- Isso nao entra como comportamento padrao do agente.
- So liberar quando:
  - a cena nao depender do sprite engine automatico naquele momento
  - houver controle explicito do ciclo de vida da SAT
  - a tecnica estiver restrita a menu, title screen, cutscene ou benchmark dedicado
  - a evidencia em emulador confirmar ausencia de conflito com sprites futuros

## Taxonomia operacional

- `canonica_segura`
  - `plane size tuning`
  - `SPR_initEx(u16 vramSize)` quando a medicao pedir
  - `3+1 palette split`
  - `compare_flat` como prova honesta de ROM
- `avancada_com_tradeoff`
  - `window alias`
  - `hscroll slack reuse`
  - `sprite grafts`
  - Shadow/Highlight ambiental por background
  - alternancia temporal de FX gigante
- `opt_in_de_cena_especial`
  - `SAT reuse`
  - quirks e exploits de sprite

## Curadoria - resposta tecnica vs resposta perceptiva

Licao: o budget classico do VDP (`scanline pressure`, `tile budget`, `palette budget`, `DMA budget`) responde a pergunta "cabe?". Mas o sistema antigo nao separava isso da pergunta "perceptivel?". Resultado: budget aprovado por todos os numeros, mas o jogador nao ve o efeito por causa de FX competindo, sprites muito pequenos, ou paleta colapsando sob Highlight.

### Dois eixos de resposta obrigatorios

Toda analise de cena/projeto deve devolver DOIS veredictos paralelos, nao um so:

#### Eixo tecnico (pergunta: "cabe?")

- `cabe`
  - todos os budgets (scanline, tile, palette, DMA, sprite) dentro do limite nominal do VDP.
- `cabe com recuo`
  - todos os budgets dentro do limite, mas com `worst_frame` proximo do teto (>= 80% do limite nominal). Recomendar reducao proativa ou mover efeito para outra cena.
- `nao cabe`
  - qualquer budget acima do limite nominal. Bloqueia `validado_budget` ate reducao.

#### Eixo perceptivo (pergunta: "perceptivel?")

- `perceptivel`
  - `perceptual_check` (fluidez/leitura/naturalidade/impacto) com valores nao-zero e >= 0.6 na media. Quando `claims.critical_motion=required`, `motion_gif` e `visual_vdp_dump.bin` confirmam juntos que o efeito e visivel sob as condicoes de gameplay (fundo, palette, scanline reais).
- `perceptivel com recuo`
  - `perceptual_check` nao-zero mas < 0.6 em algum eixo. Recomendar reforco de contraste, aumento de sprite, troca de paleta ou isolamento de FX.
- `nao perceptivel`
  - `perceptual_check` zerado em qualquer eixo, OU `perceptual_check` nao registrado. Bloqueia `visual_aprovado` ate medicao real.

### Relacao entre os dois eixos

| Tecnico | Perceptivo | Veredito final |
|---|---|---|
| `cabe` | `perceptivel` | `validado_budget + visual_aprovado` |
| `cabe` | `perceptivel com recuo` | `validado_budget` + `visual_aprovado_com_recuo` (warning) |
| `cabe` | `nao perceptivel` | `validado_budget` mas `visual_aprovado=false` |
| `cabe com recuo` | `perceptivel` | `validado_budget_com_recuo` + `visual_aprovado` (warning tecnico) |
| `cabe com recuo` | `nao perceptivel` | bloqueia ate refazer |
| `nao cabe` | (qualquer) | bloqueia ate refazer |

### Aplicacao em LAB/TECHDEMO

Em projetos com `claim_ceiling=technical_lab_validated`, o eixo tecnico basta para `validado_budget`, mas o eixo perceptivo continua obrigatorio para qualquer asset subir para `elite_ready` ou `delivered`. Em particular, `perceptual_runtime_metrics` exige que `runtime_metrics.json` registre `perceptual_check` com valores reais, nao zeros default.

## Senior Competencies

Esta skill deve ser tratada como dona do budget senior de hardware:

- `scanline pressure`
  - 20 sprites por scanline como verdade de pior quadro
- `H-Int arbitration`
  - uma familia de callback por cena, com owner explicito
- `H-Int singleton budget`
  - uma familia de efeitos por frame, nunca duas assumidas por inercia
- `DMA leakage`
  - custo real por VBlank, inclusive no quadro mais pesado
- `window occupancy / BG_A occlusion`
  - custo real de usar `WINDOW` como HUD e o quanto de `BG_A` fica sacrificado
- `interlaced shimmer budget`
  - medir ganho real de layout versus tremor visual e custo de leitura
- `sprite multiplexing tradeoff`
  - diferenciar alternancia temporal de reuso real de SAT
- `SAT rewrite risk`
  - medir corrupcao potencial, competicao com H-Int e fragilidade de timing
- `giant boss plane takeover`
  - custo e beneficio de mover chefes gigantes para `BG_A/BG_B`
- `worst-frame budgeting`
  - dois personagens, HUD, FX e uploads concorrendo no mesmo quadro
- `shadow/highlight slot audit`
  - risco de operador em slot critico de paleta
- `masked lighting budget`
  - medir custo real de pool emissivo, scanline pressure e perda de leitura em spotlight movel
- `procedural glitch readability budget`
  - garantir que rasgo, flash ou corrupcao de HUD continuem servindo gameplay
- `mutable tile pool budget`
  - quantos tiles unicos uma sala pode sujar sem estourar residency
- `dirty upload discipline`
  - uploads de mutacao local precisam caber no pior quadro
- `cellular microbuffer envelope`
  - regiao maxima, cadence do solver e custo de dirty tiles antes de a tecnica deixar de caber

Regra:

- esta skill responde se a tecnica `cabe`, `cabe com recuo` ou `nao cabe`
- road physics e boss modular so entram no parecer quando declarados como `required` em `doc/project_methodology_manifest.json`; palavras soltas no codigo nao criam claim
- contrato road/boss vazio, sem simbolos runtime ou sem budget mensuravel e blocker, nao documentacao suficiente
- ela deve sempre explicitar o recuo necessario
- nenhuma tecnica de scene special effect pode ser aprovada sem esse parecer
- `interlaced_448` pode entrar no core roadmap, mas o parecer default continua `special_scene_only`

## Quirks e exploits do VDP

- Quirk de hardware nunca entra como comportamento padrao do agente.
- So use com intencao declarada, benchmark dedicado e evidencia em BlastEm.

### X = -128 em coordenadas praticas

- Em fluxos SGDK, colocar sprite na faixa off-screen equivalente a `X = -128` pode causar desaparecimento ou mascaramento de outros sprites.
- Por padrao, trate essa faixa como proibida.
- So liberar se o exploit for deliberado e documentado.

## Alertas classicos

- alpha blending real nao existe
- terceira camada de background nao existe
- DMA fora de VBlank exige justificativa forte
- compressao `.res` reduz custo de ROM e pode alterar tempo de load, mas nao reduz o custo final do tile descompactado quando residente em VRAM
- shadow/highlight tem regras de prioridade e custo de paleta
- imagem inteira convertida em tilemap quase sempre explode tiles unicos
- **paleta PNG inflada (>16 entradas PLTE) causa corrupcao silenciosa**: o rescomp usa indices brutos da paleta para gerar tiles; dois pixeis com a mesma cor RGB mas indices diferentes no PNG produzem tiles "unicos" falsos, inflando o tileset sem motivo visual. Verificar SEMPRE byte 24 (bitDepth<=4) e contagem de entradas PLTE (<=16) antes de qualquer trabalho de recursos. Uma imagem com 11 cores unicas mas 256 entradas de paleta e um problema critico
- **VRAM overflow por excesso de tiles unicos e SILENCIOSO**: a ROM compila sem erros mas os tiles invadem sprite VRAM, fonte e nametables do VDP, causando corrupcao total. NUNCA assumir "2048 tiles disponiveis". O budget real depende de `maps_addr` (endereco mais baixo de tabela VDP no VRAM). Para SGDK 2.11 com planos 64x32 OU 32x32: `maps_addr = 0xC000`, `TILE_MAX_NUM = 1536`, user tiles = 1536 - 16(sys) - 96(font) - SPR_initEx. **Calcular ANTES de buildar: BG_B_tiles + BG_A_tiles <= TILE_MAX_NUM - 16 - 96 - SPR_initEx.**
- **maps_addr = 0xC000 para AMBOS 32x32 e 64x32 no SGDK 2.11** — mudar `VDP_setPlaneSize()` NAO aumenta tile space porque BGB nametable fica em 0xC000 em ambos os casos
- **Arte com >80% tiles unicos e incompativel com cenarios largos** — panoramas detalhadas (como cityscapes) facilmente geram 2.8 tiles unicos por pixel-coluna. Para cenas > 320px, exigir ratio de tiles unicos <= 60% OU streaming de segmentos
- `SPR_init()` automatico nao e neutro para cenas pesadas de background
- `VDP_setPlaneSize(..)` costuma ser a primeira otimização estrutural legitima antes de alias ou reciclagem de tabela, mas NAO aumenta tile space no SGDK 2.11
- `window alias` e `hscroll slack reuse` podem funcionar, mas quebram facil se a cena ou o modo de scroll mudarem
- `SAT reuse` so faz sentido em telas especiais; em gameplay normal tende a conflitar com o sprite engine
- `sprite graft` sem medicao de scanline budget vira flicker, nao profundidade
- sprite decorativo demais para "animar fundo" costuma ser pior do que tile animation via DMA
- efeito raster ou palette split sem BlastEm nao deve subir de status
- stage acima do teto do plano pede streaming de tilemap guiado pela camera
- frame critico de luta precisa ser orcado como conjunto; nao por personagem isolado

## Escada forense obrigatoria

1. header PNG / PLTE
2. `rescomp` raw tiles
3. separar `rom_asset_cost`, `vram_resident_set`, `load_time_dma_cost`, `per_frame_dma_cost`, `active_animation_window`, `scene_local_scope` e `scanline_sprite_pressure`
4. formula real de VRAM
5. decisao de arquitetura
6. BlastEm

Se a analise saltar esta ordem, o parecer ainda nao esta maduro.

## Curadoria 2026-06-15 - Mega Drive AAA video techniques

Quando o prompt, PRD, TDD ou entrega acionar claims de tecnica avancada vindos
da curadoria de videos Mega Drive, esta skill deve exigir os novos contratos
antes de responder `cabe`:

- colisao grande/semi-solida: ler `collision_topology_report`
- streaming, dirty tiles ou tile animation: ler `dma_queue_contract`
- Shadow/Highlight, H-Int, VSCROLL_COLUMN, HSCROLL_LINE ou palette cycling:
  ler `scroll_fx_contract`
- catalogo de entidades com function pointers: ler `entity_vtable_plan` quando
  isso afetar pior quadro, spawn, sprites ou ciclo de vida
- transicoes com fade/flush: ler `state_transition_contract`
- claim AAA/release/ready_for_aaa: exigir `aaa_pipeline_gate_report`

Sem esses contratos, o parecer maximo e `needs_review` ou `nao cabe`
metodologico para o claim correspondente. Build verde ou resumo de video nao
substitui budget, owner, fallback e evidencia runtime.
