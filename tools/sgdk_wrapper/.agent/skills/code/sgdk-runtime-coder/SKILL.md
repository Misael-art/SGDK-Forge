---
name: sgdk-runtime-coder
description: Use quando a tarefa envolver codigo C SGDK 2.11 real, montagem de cena, sprites, BGs, HUD, audio, loop principal, build no Windows, scroll avancado, raster split, pseudo-3D, DMA scheduling e fechamento do ciclo ate ROM com evidencia em emulador. Nao substitui scene-state-architect, sgdk-build-wrapper-operator ou megadrive-vdp-budget-analyst; trabalha entre eles como o programador perito de runtime.
---

# SGDK Runtime Coder

Esta skill existe para o miolo operacional que faltava no framework:

- implementar e corrigir codigo C SGDK 2.11 real
- montar cena, sprites, BGs, HUD, audio e loop principal
- escolher a API certa entre `IMAGE`, `MAP`, `SPR_init`, `SPR_initEx`, `TILE_USER_INDEX`, `PAL_setPalette`, `SPR_setAnimAndFrame`, etc.
- buildar corretamente no Windows
- fechar o ciclo ate ROM + evidencia no emulador

## Nao substitui outras skills

Esta skill senta entre as outras:

- `AGENTS.md` + `rules/SGDK_GLOBAL.md`
  - ponto de entrada e regras sempre ativas do workspace
- `scene-state-architect`
  - modularidade, fronteiras de estado e responsabilidade
- `sgdk-build-wrapper-operator`
  - wrapper, layout e politica de build
- `megadrive-vdp-budget-analyst`
  - decisao de VRAM, DMA, sprites e extrapolacao

## Ler antes de agir

1. `references/sgdk_211_api_reality.json`
2. `references/runtime_scene_contracts.md`
3. `references/windows_toolchain_gotchas.md`
4. `references/pattern_catalog.json`
5. `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md`
6. `doc/05_technical/92_sgdk_engine_pattern_registry.json`
7. `references/build_and_emulator_gate.md`
8. `doc/10-memory-bank.md` do projeto alvo
9. `doc/project_methodology_manifest.json`
10. `doc/project_hygiene_manifest.json`
11. `doc/technique_usage_manifest.json` e `tdd_contract.json > technique_selection`
12. `tools/sgdk_wrapper/schemas/camera_behavior_contract.schema.json` quando camera, scroll, boss room, plataforma, chase ou shake afetarem gameplay
13. header relevante em `sdk/sgdk-2.11/inc/`

Se `doc/10-memory-bank.md` nao existir no projeto, registre o fallback para `doc/06_AI_MEMORY_BANK.md` no `context_pack_manifest`.

## Quando usar

- bug de compilacao ou link em SGDK 2.11
- bug de loop principal, VBlank ou ordem de atualizacao
- integracao de sprite, BG, HUD, texto, audio ou parallax
- escolha entre `VDP_drawImageEx` e `MAP_create`
- reset de estado entre cenas
- tune de `SPR_initEx`
- validacao de runtime com BlastEm
- fechamento de cena via `scene_closeout_gate.ps1`

## Saidas obrigatorias

- `runtime_decision_log`
- `context_pack_manifest` quando a tarefa envolver codigo novo, API SGDK incerta ou arte gerada por sourcing
- `api_reality_check`
- `scene_reset_plan` quando houver transicao de cena
- `scene_transition_runtime_contract` quando houver `scene_transition_card`
- `resource_loading_model` quando houver streaming, preload, animacao grande ou asset scene-local
- `scene_direction_runtime_contract` quando houver `scene_direction_record` monumental, signature-only, bioma-chave ou setpiece de fundo
- `runtime_animation_timing_map` quando houver lutador, ataque, dano, hitstop, smear, flash frame ou animacao premium
- `motion_physics_contract` e `state_transition_motion_contract` quando a animacao depender de gravidade, contato, recovery, landing, hurt/getup ou retorno de cutscene
- `idle_breathing_cycle_contract`, `facial_expression_phase_map`, `cloth_secondary_animation_contract` e `hand_pose_keyframe_contract` quando a animacao premium depender desses sub-contratos
- `cutscene_runtime_contract` quando houver abertura, cutscene, cena de contexto, briefing, painel narrativo ou final
- `production_runtime_contract` quando houver alvo AAA, stable, release, jogo completo ou projeto piloto
- `cpu_frame_budget_report`, `fixed_point_math_contract`, `dma_queue_contract` e `z80_task_ownership_contract` quando tocar hot loop, DMA, audio driver, ASM ou matematica de gameplay
- contratos de game feel (`input_latency_contract`, `movement_curve_report`, `camera_behavior_contract`, `hitbox_sprite_alignment_report`, `enemy_readability_report`, `playable_scene_design_card`) quando a mudanca afetar controle, camera, combate ou leitura
- `visual_delivery_gate_report` quando a ROM usar asset critico e houver alegacao de `AAA`, `pronto` ou `delivery`
- `build_evidence`
- `emulator_evidence`
- `delivery_findings`
- `freshness_audit_report` quando a mudanca tocar ROM, contrato, captura, baseline ou docs

## Contrato Operacional

### Entrada minima

- `res/resources.res`
- codigo de runtime alvo
- laudo vigente de `megadrive-vdp-budget-analyst`
- `visual_delivery_gate_report` sem blockers quando a tarefa pedir entrega visual AAA ou prototipo final
- `context_pack_manifest` quando a decisao depender de docs, source cases, memoria operacional, engine profiles ou headers SGDK
- contexto de build e emulador
- `route_decision_record` ou `scene_architecture_triage` quando a cena envolver assets grandes, parallax, foreground/oclusao ou familia tecnica ainda nao congelada
- `ui_decision_card` quando houver HUD/UI formal
- `text_presentation_profile` quando texto, fala, alerta cinetico ou flavor tiver peso dramatico
- `cutscene_fsm_script`, `cutscene_panel_layout`, `cutscene_resource_plan`, `cutscene_text_timing_map`, `cutscene_motion_beat_map` e `cutscene_teardown_plan` quando `scene_role=cutscene`
- contratos de animacao viva aplicaveis (`idle_breathing_cycle_contract`, `facial_expression_phase_map`, `cloth_secondary_animation_contract`, `hand_pose_keyframe_contract`) quando o alvo for AAA e o personagem for hero/fighter/boss
- `motion_physics_contract` e `state_transition_motion_contract` quando locomocao, pulo, queda, golpe, dano, boss ou transicao de estado forem criticos
- `production_runtime_contract`, `scene_manager_contract`, `input_abstraction_contract`, `save_system_contract` e `region_timing_contract` quando o alvo for AAA/stable/release
- `scene_transition_card` quando houver transicao formal
- `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` ou `audio_architecture_card` quando houver espetaculo runtime formal
- `scene_direction_record`, `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` e `background_ecology_card` quando houver cenario monumental, signature-only, bioma-chave ou setpiece de fundo
- `project_methodology_manifest.json` classificado; claims `critical_motion`, `road_physics` e `modular_boss` em `required` acionam obrigatoriamente seus contratos e owner skills antes do runtime
- `tdd_contract.json > technique_selection.application_plan` cobrindo cada tecnica a implementar; runtime nao inventa tecnica fora do TDD/manifesto
- `camera_behavior_contract` quando a cena tiver scroll jogavel, plataforma, chase, boss room, camera trigger, look-ahead, screen shake ou culling dependente de viewport

### Saida minima

- `runtime_decision_log`
- `context_pack_manifest` quando gerado para esta iteracao
- `api_reality_check`
- `scene_reset_plan` quando houver transicao de cena
- `debug_order_check` quando estiver corrigindo visibilidade, tilemap, sprite ou composicao
- `fixed_point_math_contract` se qualquer movimento, camera ou FX usar sub-pixel
- `camera_runtime_report` quando houver `camera_behavior_contract`, citando dead zone, look-ahead, smoothing, clamp, triggers, shake, culling e snap final
- `dma_queue_contract` validado por `tools/sgdk_wrapper/.agent/scripts/dma_queue_planner.py` quando houver DMA por frame
- `cpu_frame_budget_report` com `float_or_double=false`, `heap_in_loop=false` e justificativa de ASM ou fallback C quando aplicavel

## Ordem Conservadora de Debug Grafico

Antes de atacar VRAM, paleta, rescomp, compressao ou WINDOW, valide nesta ordem:

1. existencia do objeto/asset no runtime
2. posicao real na tela e semantica de unidades do SGDK (pixels vs tiles)
3. composicao entre BG_B, BG_A, WINDOW e sprites
4. budget residente e DMA por frame
5. paleta, compressao, corte interno e artefatos de build

Se essa ordem for quebrada, registre o motivo no `runtime_decision_log`. Debug sofisticado cedo demais e regressao operacional, nao demonstracao de rigor.

## Fechamento de Runtime

- depois de buildar, rode o validator e freshness antes de promover status
- se a cena tiver `SceneId` e `TargetScene`, use `scene_closeout_gate.ps1` para fechar a sequencia inteira
- se `runtime_metrics` apontar `over_budget_frames`, `cpu_load_max` acima do alvo ou cena errada em MDRT, volte para runtime/budget antes de atualizar baseline
- `resource_loading_model` quando houver diferenca entre asset total, set residente e upload por frame
- `build_evidence`
- `emulator_evidence`
- `delivery_findings`

### Passa quando

- a decisao de runtime cita explicitamente o budget que a autorizou
- `api_reality_check` cita header, referencia local ou fonte canonica antes de usar API SGDK sensivel
- runtime nao comeca por tentativa local quando `route_decision_record` ainda esta ausente ou contraditorio
- a escolha entre `IMAGE`, `MAP`, streaming e `SPR_initEx` fica rastreavel
- o `runtime_decision_log` declara qual modelo foi usado: `full_resident`, `scene_local_preload`, `animation_window_streaming`, `tilemap_streaming` ou `fallback_reduced_residency`
- runtime separa custo ROM/compressao, tiles residentes em VRAM, DMA de loading/preload e DMA por frame
- runtime usa `fix16`, `fix32`, LUT ou inteiros explicitos para gameplay; `float`/`double` continuam bloqueados
- camera de gameplay nao gruda rigidamente no player por habito: se usar follow direto, precisa justificar `fixed_room`, `fighting_stage_lock` ou outro modelo no `camera_behavior_contract`
- camera com scroll usa coordenada interna `integer`, `fix16` ou `fix32`, mas a posicao final enviada a scroll/sprite space deve ser `integer_pixels_only`
- `dead_zone`, `lookahead`, `smoothing`, `clamp`, `trigger_zones`, `screen_shake` e `culling_policy` devem vir do contrato; runtime nao inventa valores silenciosos
- `screen_shake` e aplicado como evento de gameplay com offset limitado, decaimento declarado, snap inteiro final e sem mostrar vazio fora do mapa
- culling baseado em camera usa margem segura e nao pode remover telegraph, projeteis ativos, boss ou hazard antes de ficarem legiveis
- runtime nao agenda DMA fora do VBlank/loading; `dma_queue_planner.py` precisa passar quando o contrato existir
- polling de input acontece no inicio do frame e o `input_latency_contract` declara resposta em ate 1 frame quando possivel
- quando houver UI formal, o runtime cita `ui_architecture_choice`, ownership e fallback usados
- quando houver texto expressivo, o runtime cita `text_surface_class`, timing, owner, audio, teardown e fallback usados
- quando houver cutscene, o runtime cita `cutscene_fsm_script`, estado inicial, triggers, text timing, resource plan, palette script, audio cue map e teardown usados
- quando houver alvo AAA/stable/release, o runtime cita scene manager, input abstraction, save/SRAM, region/timing e como eles foram provados na ROM
- quando houver transicao formal, o runtime cita `continuity_model`, `runtime_state_handoff`, `teardown_reset_plan` e fallback usados
- quando houver espetaculo runtime formal, o runtime cita cards, owners, budget, teardown e fallback usados
- quando houver cenario monumental, o runtime cita `scene_direction_record`, tecnicas assinadas, owners de scroll/CRAM/H-Int/tiles, fallback e downgrade usado
- runtime implementa parallax, palette cycle, raster FX e ecologia de fundo somente com owner unico, reset simetrico e budget aceito
- runtime recusa tecnica `LABORATORIO` fora de lab e recusa otimização de baixo nivel sem benchmark isolado, fallback C/seguro e evidencia planejada
- todo arquivo especifico, script auxiliar, log, experimento ou rascunho criado durante runtime fica dentro do projeto; temporarios ficam em `rascunho/`
- runtime nunca declara Mode 7 no Mega Drive; referencias desse tipo ficam redirecionadas para `pseudo3d_road_stack`, line scroll, zmap ou paineis pre-renderizados
- quando houver golpe/dano premium, o runtime implementa o `runtime_animation_timing_map` a partir de `animation_direction_contract`: startup, anticipation, active, hitstop, follow-through, recovery, cancel/return e frame hold nao podem virar cadencia uniforme por habito
- quando houver `motion_physics_contract` ou `state_transition_motion_contract`, o runtime preserva center of mass, foot contact, landing, recovery, cancel/return, bridge frames e frame holds; reduzir isso por budget exige fallback documentado e rebaixa status visual
- quando houver contratos de animacao viva, o runtime preserva loops, duracoes, holds, expression frames, cloth settle e hand pose transitions declarados; reduzir por budget exige `fallback_reduced_residency` e rebaixa o status visual
- hit spark, dust, flash e camera shake sao eventos de gameplay sincronizados ao `impact_frame_contract`, nao pixels baked-in no personagem
- quando houver anexo tipografico, o runtime cita `font_render_mode`, `font_owner` e `fallback_font_plan` usados
- build, validacao e evidencia apontam para a mesma ROM
- o runtime nao declara `pronto`, `AAA`, `delivery` ou `ready_for_aaa=true` se o gate visual tiver `needs_review`, `perceptual_quality=nao_medido`, `source_to_rom_visual_match < 8`, `benchmark_match` abaixo de `benchmark_profile.required_match`, `blocked_image_tooling`, `blocked_no_premium_source`, `lab_not_delivery`, ou `local_author_pixel_rasterization` como fonte final de asset critico
- o runtime nao declara `pronto`, `AAA`, `delivery` ou `ready_for_aaa=true` quando uma animacao critica tiver `animation_direction_contract` ausente, hitstop nao implementado, active/recovery divergente do mapa ou FX/flash acoplado indevidamente a paleta do personagem
- o runtime nao declara `pronto`, `AAA`, `delivery` ou `ready_for_aaa=true` se `scene_role=cutscene` nao possuir FSM, resource plan por estado, text timing map, owner de surfaces e evidencia da cena correta
- o runtime nao inicia implementacao de road physics, boss modular ou movimento critico com claim `review_required`, nem cria claim por inferencia textual
- o runtime nao declara `pronto`, `AAA`, `stable`, `release`, `delivery` ou `ready_for_aaa=true` sem scene manager, input abstraction, save/SRAM quando aplicavel, region/timing, ROM mastering, code review e CI/local CI reportados
- o runtime nao declara `pronto`, `AAA`, `delivery` ou `ready_for_aaa=true` se `res/resources.res` estiver ausente em projeto visual/gameplay, se `res_graph_report.method=no_res_files`, ou se `res_graph_report.vram.status=code_loaded_tiles_unmeasured`
- a captura BlastEm registra `runtime_metrics.json` ou evidencia equivalente sem vazar para fora de `out/blastem_env_*`
- a captura BlastEm precisa provar a cena certa: `TargetScene`, bootstrap SRAM/MDRT e `runtime_metrics.scene_id` devem coincidir antes de screenshot/baseline serem usados como evidencia
- screenshot dedicado com `<=3` cores unicas, quase vazio ou sem informacao de gameplay e `blank_or_low_information_capture`; deve ser refeito antes de fechar QA
- `visual_vdp_dump.bin` com hash igual ao `save.sram` e evidencia invalida (`invalid_visual_vdp_dump`), nao fallback aceitavel

### Handoff para proxima etapa

- entregar a ROM e o `runtime_decision_log` para `validate_resources.ps1`
- entregar identidade da ROM e evidencia para `doc/changelog` e `doc/10-memory-bank.md`
- atualizar `doc/10-memory-bank.md` e `doc/changelog/changelog.md` sempre que implementacao ou arquitetura mudar, antes do closeout

## Regras canonicas imediatas

- SGDK 2.11 real vence memoria do agente
- `extern` em header e definicao unica em `.c`
- `SYS_doVBlankProcess()` no loop principal
- ordem canonica:
  - `INPUT_update()`
  - `scene update`
  - `SPR_update()`
  - `SYS_doVBlankProcess()`
- reset de cena e obrigatorio ao sair
- index `0` realmente transparente nos PNGs integrados
- `TILE_USER_INDEX` e empilhamento de tilesets devem ser declarados
- compressao `.res` (`FAST`, `BEST`, `NONE`) nao reduz o set residente em VRAM depois do load; registrar ROM/load separado de VRAM
- asset de outra cena nao entra no budget residente da cena atual se houver unload/preload claro
- no Windows, build sempre com caminho absoluto e `cmd //c`
- runtime sem laudo de budget vigente e erro de processo, nao apenas erro de estilo
- para smoke/gate em BlastEm, usar a lib canonica `tools/sgdk_wrapper/lib/blastem_automation.psm1`
- heartbeat canonico de readiness e `READY` em SRAM `0x100` em rolling (re-assinado pos-warmup); emissao unica e anti-padrao
- referencia ROM-side do heartbeat canonico vive em `tools/sgdk_wrapper/modelo/src/system/runtime_probe.c`
- `press_until_ready:*` e o unico passo oficial para chegar em cena antes de captura; suporta `flush_every=` para forcar flush de SRAM e `rotate_key=` para recuperar de timeout
- `FileSystemWatcher` em `$SaveRoots` e fast-path oficial; polling continua como backstop
- GDB stub do BlastEm nao suporta `Z2`/`Z3`/`Z4` (watchpoints); nao construir rota de heartbeat live via GDB
- `fresh_sram_confirmed` precisa ser verdadeiro para promover evidencia de runtime BlastEm
- logs operacionais do BlastEm devem sair em JSONL e entrar no handoff como evidencia rastreavel
- no Windows, o sandbox do BlastEm deve alinhar `HOME/USERPROFILE` com `AppData\\Local` e gravar `blastem.cfg` no ramo efetivo que o emulador resolve
- `save_path` e `screenshot_path` precisam viver dentro de `ui {}` no cfg gerado; fora disso o BlastEm pode cair no default `$USERDATA/blastem/$ROMNAME`

## Roteamento antes de runtime

Antes de alterar C, `.res` ou builder, confirme qual rota autorizou a cena:

- `full_resident`: cena pequena, tiles unicos medidos e preload suficiente
- `scene_local_preload`: asset grande no projeto, mas recortado para a cena atual
- `tilemap_streaming` ou `panel streaming`: mundo/cenario maior que a janela visivel
- `animation_window_streaming`: sheet/ciclo maior que a janela ativa necessaria
- `fallback_reduced_residency`: reducao assumida, registrada e visualmente honesta

Se a cena for `aaa_layered` e nao houver `route_decision_record`/`scene_architecture_triage`, pare o runtime e produza esse registro. O agente deve escolher a familia tecnica antes de tentar encaixar assets por tentativa e erro.

## Curadoria 2026-06-03: streaming, SAT e CRAM

Quando o registry apontar uma tecnica com `curation_source_ids` do lote `curation_2026_06_03_megadrive_video_text_batch`, implemente apenas o que estiver autorizado pelo status humano e pelo manifesto do projeto.

- `sprite_frame_vram_slot_streaming`
  - so escreva runtime depois de existir `resource_loading_model=animation_window_streaming`, `active_animation_window`, mapa de slots de VRAM e `dma_queue_contract`;
  - nao trate sheet inteira de lutador/boss como residente por reflexo; se o frame atual/proximo nao couber, use recuo documentado.
- `animation_lookahead_dma_queue`
  - prever o proximo frame durante a logica normal e disparar upload apenas no VBlank/loading;
  - `DMA` nao e processamento em background gratuito: durante DMA ha disputa de barramento e o pior quadro precisa caber.
- `large_metasprite_vblank_fit_audit`
  - antes de chamar APIs de sprite ou `VDP_loadTileData`, conferir `tiles_unicos * 32` contra o envelope seguro do VBlank.
- `sat_double_buffering` e `sprite_midframe_sat_reuse`
  - ficam `LABORATORIO`; nao usar em projeto de entrega sem benchmark isolado, ownership de `SPR_update` e prova BlastEm de SAT limpa.
- `cram_dot_masking_strategy`
  - mid-frame CRAM exige `h_int_ownership_map`, linhas de escrita, plano de mascaramento e teardown; screenshot sem dots visiveis em BlastEm e gate minimo.
- `sprite_band_slot_allocator` e `ghost_afterimage_sprites`
  - reservar slots de HUD, personagens, projeteis e hitboxes antes de adicionar rastro, blur, particulas ou multiplexing.

## Classificacao de conhecimento

- `hard_fact_blocker`
  - quebra build, linker ou runtime se errar
- `canonical_pattern`
  - padrao seguro e reutilizavel
- `advanced_pattern_candidate`
  - padrao forte vindo do scan de engines, mas ainda sem promocao humana explicita
- `experimental_pattern`
  - so com prova forte e intencao explicita

## Modelos de carga e residencia

Use exatamente um modelo dominante no `runtime_decision_log` quando o budget depender de residencia ou streaming:

- `full_resident`: todos os tiles/frames necessarios ficam residentes durante a cena.
- `scene_local_preload`: assets da cena atual carregam em boot/loading/troca de cena e assets externos ficam fora da residencia.
- `animation_window_streaming`: apenas a janela ativa de animacao fica residente; trocas de ciclo usam SGDK auto VRAM alloc ou DMA manual validado.
- `tilemap_streaming`: mapa maior que a VRAM visivel entra por chunks/colunas/blocos com seam control.
- `fallback_reduced_residency`: rota reduzida por budget, com menos frames, menos tiles unicos, menor parallax ou `compare_flat`.

Regra:

- `load_time_dma_cost` pode ser alto quando a cena esta em loading honesto.
- `per_frame_dma_cost` precisa caber no pior VBlank de gameplay.
- `scanline_sprite_pressure` continua limite de leitura e hardware mesmo quando VRAM cabe.

## Curadoria 2026-06-03 - Celestial Chase: status declarativos e visual_lab_static_floor

Licao extraida do projeto `Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]`: o sistema antigo aceitava "ta rodando no BlastEm" como prova suficiente para promover runtime a entregue. O resultado foi `gameplay_basico=funcional` + `performance=estavel` + `audio=ok` mas `creative_ready=false` e 4 blockers ativos. Faltava separar "rodou" de "esta pronto".

### Taxonomia obrigatoria de status de runtime

Toda cena/projeto em laboratorio ou entrega deve declarar explicitamente, no `doc/10-memory-bank.md` e em `validation_report.json`, o estado de cada dimensao:

| Dimensao | Valores | Significado |
|---|---|---|
| `runtime_funcional` | `true` / `false` | Build compila e roda sem crash no BlastEm |
| `animacao_observada` | `true` / `false` | Animacao de sprites foi observada em screenshot multi-frame ou VDP dump (nao so declarada em codigo) |
| `movimento_aprovado` | `true` / `false` | `motion_gif` ou `visual_vdp_dump.bin` foi revisado por humano e registrado em `human_approval_record.md` |
| `visual_aprovado` | `true` / `false` | `perceptual_check` (fluidez/leitura/naturalidade/impacto) com valores nao-zero; `visual_aesthetic_report.critical_assets[*].status != rework` (ou override documentado) |
| `gameplay_aprovado` | `true` / `false` | Game loop completo (input -> sim -> render -> feedback) com `gameplay_basico=funcional`, `performance=estavel`, `audio=ok`, `hardware_real=blastem_reference_emulator` |

Hierarquia obrigatoria: `runtime_funcional` -> `animacao_observada` -> `movimento_aprovado` -> `visual_aprovado` -> `gameplay_aprovado`. Pular estagio exige `human_approval_record.md` explicito e registrado em `agent_learning/success_patterns.md` ou `failure_patterns.md`.

### Piso `visual_lab_static_floor` para LAB/TECHDEMO

Em projetos com `claim_ceiling=technical_lab_validated` (LAB/TECHDEMO), o piso de aceitacao e:

- `runtime_funcional=true` e `animacao_observada=true` sao suficientes para `technical_ready=true`.
- `movimento_aprovado`, `visual_aprovado` e `gameplay_aprovado` NAO precisam ser todos `true` para `technical_ready`.
- `ready_for_aaa` permanece `false` ate o projeto sair de `LAB/TECHDEMO`.
- A promocao de qualquer asset critico para `MESTRE_*` continua exigindo todos os 5 estagios `true` + benchmark dedicado + BlastEm + budget + docs.

Esse piso existe para nao bloquear pesquisa de runtime honesta, sem contaminar a barra de entrega.

### Flag `asset_promovido_nao_usado`

Quando o painel humano promove um asset para `MESTRE_*` ou `elite_ready` mas o codigo de runtime nao instancia o asset (sprite nao eh `SPR_addSprite`, image nao eh `VDP_drawImage`, sample nao eh `XGM2_*`), registrar `asset_promovido_nao_usado` em `doc/agent_learning/failure_patterns.md` com:

- `asset_id`
- `data_promocao`
- `data_constatacao`
- `motivo` (ex.: asset nao cabe no plano, asset substituido por procedural, asset fora de escopo da cena)
- `decisao` (rebaixar para `TEORICA_PRIORITARIA`, abrir bug, realocar)

Sintoma tipico: `out/logs/visual_aesthetic_report.json` lista asset como `elite_ready` mas `out/rom.bin` nao contem referencia a ele no `resources.res`. Cross-check via `res_graph_report.json`.

## Senior Competencies

Esta skill deve ser lida como dona operacional das seguintes competencias seniores:

- `h_int_control_plane`
  - ownership unico de callback, arbitro de efeitos e contrato de reset
- `line scroll`
  - arrays por scanline, `DMA` e seam control
- `column scroll`
  - uso disciplinado de `VSRAM` e custo por frame
- `H-Int palette split`
  - split mid-frame, alias visual `mid-frame palette swap`, reset simetrico e risco de callback unico
- `procedural_raster_glitch_suite`
  - rasgo dirigido por `HScroll`, shock de paleta, corrupcao controlada de HUD e leitura dramatica sob controle
- `masked_shadow_highlight_lighting`
  - spotlight, lanterna ou weak spot de boss como ilusao de hardware; nunca vender como alpha blending ou iluminacao global
- `palette cycling`
  - escrita segura em `CRAM`, timing tables e ownership de paleta
- `window_plane_static_hud`
  - `WINDOW` como plano fixo para HUD, lifebar e score sem consumir sprite slot
- `interlaced_448 orchestration`
  - modo 448 como tecnica `special_scene_only`, nunca como default de cena
- `BG_B bypassing`
  - boss gigante como tilemap, tradeoff com parallax e plane takeover
- `pseudo-3D`
  - `zmap`, curves, hills, banding e budget de raster
- `software_affine_pseudo3d`
  - transformacao por software tratada como trilha separada do road-stack
- `road_stack_runtime_budget`
  - nao multiplicar/dividir dentro de loop de 224 linhas por frame quando a mesma curva pode virar tabela, diferenca finita ou acumulador fix16/fix32
  - quando a tabela visual puder atualizar a 30 Hz sem quebrar leitura, manter gameplay/input/collision a 60 Hz e registrar o tradeoff
  - qualquer mudanca em equacao de estrada, line scroll ou deformacao por scanline exige nova amostra `runtime_metrics`/MDRT antes de alegar 60fps
- `mutable_tile_decal_mutation`
  - dano persistente local via `RAM shadow copy`, `mutable tile pool` e dirty uploads limitados
- `cellular_microbuffer_sim`
  - microframebuffer local, solver delimitado e update cadence declarada; nunca tratar como sandbox global
- `DMA scheduling`
  - uploads no VBlank, leakage control e worst-frame discipline
- `XGM/XGM2 integration boundaries`
  - ownership de canal, pause/resume e limites de integracao com gameplay

Regra:

- esta skill pode orquestrar todas essas tecnicas
- ela NAO as promove para default sozinha
- promocao para `senior_default` exige `lib_case`, scene dedicada no `BENCHMARK_VISUAL_LAB`, `validation_report` com `blastem_gate = true` e gate humano
- `WINDOW` normal e plano fixo legitimo; `window alias` continua tecnica separada e nao-default
- `pseudo3d_road_stack` e `software_affine_pseudo3d` nunca devem compartilhar status
- `sprite_midframe_sat_reuse` depende formalmente de `h_int_control_plane`

## Regra para engine scan

- padrao vindo de `SGDK_Engines` nao vira canon so porque apareceu em codigo real
- o front door em `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md` define a leitura correta
- o registry em `doc/05_technical/92_sgdk_engine_pattern_registry.json` e a fonte machine-readable dos candidatos
- se um padrao estiver como `candidate_for_canon` ou `verified_example`, trate como referencia valiosa, nao como default obrigatorio
- nenhum padrao novo deve entrar como `canonical_pattern` sem `lib_case` correspondente e gate humano explicito

## Como decidir

### `IMAGE` vs `MAP`

- usar `IMAGE` quando a arte cabe no plano efetivo e nao pede streaming de mapa
- usar `MAP_create` quando o cenario for maior que o plano, precisar de scroll de mapa ou streaming
- nao usar `MAP_create` por reflexo se `VDP_drawImageEx` resolver com menos complexidade
- nao promover imagem grande como `IMAGE` inteira so porque compila; se o mundo excede a janela efetiva, medir paineis/metatiles e usar streaming antes de integrar

### `SPR_init` vs `SPR_initEx`

- `SPR_init()` para reserva padrao
- `SPR_initEx(n)` quando o fundo estiver pressionando VRAM e o budget real pedir ajuste
- a escolha deve citar custo e impacto

### Escada forense antes de mudar arquitetura

Antes de trocar `IMAGE`, `MAP` ou streaming, o agente deve anexar:

1. numeros de `rescomp`
2. formula real de VRAM
3. separacao entre ROM/compressao, VRAM residente, DMA de preload, DMA por frame e pior scanline
4. configuracao atual de `SPR_initEx`
5. motivo da troca

Sem isso, a mudanca de arquitetura e tentativa cega.

### Escada visual antes de mexer em recursos

Quando sprite/BG existe mas nao aparece ou parece corrompido, investigue nesta ordem:

1. existencia do objeto no runtime (`SPR_addSprite`, ponteiro, contador, callback)
2. posicao real na tela apos camera/scroll
3. contrato de coordenadas e dimensoes da API
4. prioridade/oclusao entre BG_A, BG_B, WINDOW e sprites
5. paleta e indice transparente
6. VRAM/tile index/tileset
7. `resources.res`, compressao e troca de formato

Regra SGDK critica: em `SpriteDefinition`, `w` e `h` no runtime gerado representam dimensoes em pixels, nao contagem de tiles da declaracao `.res`. Nao multiplique por 8 sem verificar o header/struct gerado.

`WINDOW` nao e rota de oclusao de cenario por default. Use `WINDOW` para HUD/dialogo/plano fixo; foreground com oclusao deve ser BG_A com prioridade, sprite graft validado ou outra tecnica declarada no `route_decision_record`.

### Scene exit reset

Ao sair de cena, avaliar obrigatoriamente:

- `SPR_reset()`
- `VDP_clearPlane()`
- `VDP_setHorizontalScroll(BG_B, 0)` e equivalentes
- limpeza de HUD / WINDOW / texto

## Contrato de runtime para transicoes formais

Quando houver `scene_transition_card`, o runtime deve:

- consumir `continuity_model`, `player_control_policy`, `camera_motion_contract`, `plane_ownership_map`, `fx_ownership_map`, `audio_transition_plan`, `runtime_state_handoff`, `fallback_plan` e `teardown_reset_plan`
- registrar no `runtime_decision_log` se a rota final ficou elite, fallback ou bloqueada por budget
- tratar `palette_fade_bridge` como fallback contextualizado, nao como fade preto generico automatico
- para `spatial_scroll_bridge`, garantir que camera, streaming e seam oculto estejam sob um unico contrato de estado
- para `scripted_avatar_bridge`, garantir que perda de controle tenha motivo dramatico, duracao curta e handoff limpo
- para `tile_mask_mosaic_transition`, implementar backup/restauro de tileset ou reprovar a rota
- para `raster_distortion_bridge`, declarar owner unico de H-Int, arrays de scroll/VSRAM e reset simetrico do callback
- para `lighting_state_transition`, resetar CRAM, Shadow/Highlight, palette split e qualquer slot especial
- para `pseudo3d_perspective_bridge`, manter fallback seguro e nao misturar com gameplay normal sem benchmark proprio
- se tocar HUD, menu, title, overlay ou texto, consumir tambem `ui_decision_card`
- sem teardown verificavel, nao declarar a transicao pronta

## Contrato de runtime para cutscenes

Quando houver `cutscene_scene_contract`, o runtime deve:

- consumir `cutscene_fsm_script`, `cutscene_panel_layout`, `cutscene_resource_plan`, `cutscene_palette_script`, `cutscene_text_timing_map`, `cutscene_audio_cue_map`, `cutscene_teardown_plan` e `cutscene_evidence_plan`
- consumir `cutscene_motion_beat_map` e `cutscene_panel_animation_contract` quando a cutscene tiver painel narrativo expressivo, retrato, pan, blink, mouth, reaction ou impact motion
- implementar a cutscene como tabela de estados, nao como sequencia solta de `if` e timers sem nome
- cada estado deve possuir `enter`, `update`, `advance` e `exit` rastreaveis no `runtime_decision_log`
- declarar owner unico de `BG_B`, `BG_A`, `WINDOW`, sprites, CRAM, H-Int, scroll, audio e glyph cache
- tratar texto como sistema temporizado: cadence, pausas por pontuacao, input para acelerar/avancar e limite de linhas
- tratar portrait blink/mouth frames, pans, holds, palette cycling e fades seletivos como eventos de estado
- justificar explicitamente painel estatico; painel morto sem beat visual ou `stillness_justification` nao fecha cutscene AAA
- carregar apenas o set residente do estado atual ou o bloco explicitamente herdado por `state_handoff`
- full-screen cutscene image so pode entrar se o contrato trouxer justificativa e budget; fallback padrao e painel/pan/crop
- se usar H-Int/raster, registrar callback owner, custo e reset simetrico
- ao sair, resetar scroll, WINDOW, CRAM especial, H-Int, sprites temporarios, glyph cache e audio cue temporario
- screenshot, baseline e metricas devem provar o `scene_id` da cutscene, nao apenas title/menu ou gameplay

Sem esse contrato, a cena pode ficar `documentado` ou `lab`, mas nao fecha como cutscene AAA.

## Contrato de runtime de producao AAA

Quando houver `production_runtime_contract`, o runtime deve:

- implementar ou integrar `scene_manager_contract`: scene id, enter/update/exit, transition/loading/fade, cleanup e boot deterministico
- implementar ou integrar `input_abstraction_contract`: 3/6 botoes, combo/buffer quando o genero pedir, remap, pause/debug, edge/hold/repeat e frame-lag tolerance
- declarar `persistence_scope` e `sram_policy`; implementar ou integrar `save_system_contract` somente quando `persistence_scope=required`, `sram_policy!=none` ou o GDD exigir persistencia: SRAM magic, version, checksum, slots, init, invalid save recovery e teste de leitura/escrita
- implementar ou integrar `region_timing_contract`: `SYS_isPAL()`, alvo 50/60 Hz, duracoes, audio cadence, cooldowns, timers e regressao PAL/NTSC
- declarar se scheduler/multitasking existe, e se for ausente limitar o escopo de AI/FX ou marcar `scheduler_runtime_missing`
- entregar runtime proof, nao apenas header ou stub
- quando `persistence_scope=none`, registrar `save_system_contract_not_applicable`; nao emitir `save_system_contract_missing_when_persistence_required`
- se algum contrato ficar fora do slice, rebaixar para `prototype_playable` e registrar o blocker

Sem esse contrato, projeto pode ser prototipo excelente, mas nao produto AAA/stable/release.

## Contrato de runtime para espetaculo AAA

Quando houver `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` ou `audio_architecture_card`, o runtime deve:

- consumir o card antes de escrever H-Int, CRAM, VSRAM, sprites, tiles, audio ou camera
- registrar no `runtime_decision_log` se a rota ficou elite, fallback ou bloqueada por budget
- impedir segundo owner implicito de H-Int, paleta, sprite particles, tile mutation, boss plane takeover ou audio channel
- para `feedback_fx_decision_card`, resetar callbacks, scroll, palette cycling, Shadow/Highlight, sprites temporarios e tile mutation
- para `boss_setpiece_card`, registrar arquitetura do boss, scanline budget, weak point, telegraph e teardown
- para `advanced_tilemap_design_card`, registrar MAP/IMAGE/streaming, metatile reuse, collision_visual_contract e seam/fallback
  - declarar tambem `scene_local_preload`, `tilemap_streaming` ou `fallback_reduced_residency` quando a cena nao mantiver o mundo inteiro residente
- para `audio_architecture_card`, delegar ownership e eventos a `xgm2-audio-director` quando XGM2/PCM for relevante
- sem fallback honesto, nao implementar rota avancada

## Contrato de runtime para direcao de cenario

Quando houver `scene_direction_record`, o runtime deve:

- consumir `scene_profile`, `scene_signature_techniques`, fallback e budget antes de escrever codigo de cenario
- para `parallax_layer_contract`, declarar donos de BG_A/BG_B/WINDOW, ratios, scroll update cadence, seam policy e reset ao sair
- para `palette_cycle_decision_card`, declarar slots CRAM, cadence, owner, conflitos com HUD/FX/personagem e teardown
- para `raster_fx_ownership_map`, declarar owner unico de H-Int, slices de scanline, custo de pior linha e reset simetrico
- para `background_ecology_card`, declarar atores de fundo, tiles/sprites usados, ligacao com gameplay/narrativa e cadence segura
- se o budget rebaixar `monumental` para `competent`, registrar `fallback_reduced_scene_profile` no `runtime_decision_log`
- nunca vender `line scroll`, `zmap`, paineis pre-renderizados ou pseudo-3D de estrada como Mode 7 nativo

Sem esse contrato, o cenario pode ser bonito em asset, mas nao fecha como cenario monumental de runtime.

## Contrato de runtime para HUD/UI formal

Quando houver `ui_decision_card`, o runtime deve:

- consumir `ui_architecture_choice`, `plane_ownership_map` e `fallback_plan` antes de escrever qualquer HUD
- consumir `ui_pixel_surface_contract` quando houver health bar, fonte, caixa, micro-icone, cursor ou atlas pixel-perfect de entrega
- consumir `fx_ownership_map` antes de ligar split, wobble, palette cycling ou qualquer FX de interface
- registrar no `runtime_decision_log` se a rota final ficou elite ou fallback
- impedir segundo owner implicito de `WINDOW`, `H-Int` ou paleta especial
- tratar `profile_kind=front_end_profile` como menu/title/front-end formal, nao como excecao improvisada
- se houver anexo tipografico, consumir `font_render_mode`, `charset_profile`, `font_owner` e `fallback_font_plan` antes de escolher renderer
- se houver `text_presentation_profile`, consumir `text_surface_class`, `narrative_timing_model`, `layout_anchor`, `speaker_binding`, `text_audio_plan`, `asset_budget_plan`, `teardown_reset_plan` e `fallback_plan` antes de desenhar texto
- `fixed_custom_hud_font`
  - preferir `VDP_loadFont` ou emissao por tile-index math para HUD, labels e leitura rapida
- `variable_width_tidytext`
  - reservar para dialogo, credito, lore, terminais e front-end controlado
- `display_font_plus_body_font`
  - reservar para title/menu/front-end com `profile_kind=front_end_profile`
- nunca usar compositor proporcional caro por frame em HUD de combate
- nunca atualizar health bar ou UI por escala fracionaria; fill, cursor, texto e icones devem operar em pixels inteiros no render final
- health bar deve implementar container, buffer de dano latente, fill ativo, threshold critico e fallback conforme `ui_pixel_surface_contract`
- `glyph_manifest` fecha o subset real de glifos; sem ele nao subir charset expandido nem cache temporario caro
- `panel_sequence_text`
  - pre-carregar ou trocar paineis apenas em cadence segura; fallback e painel unico ou caixa fixa
- `diegetic_speech_balloon`
  - usar anchor claro e lifetime curto; nao cobrir hitbox, rota, HUD ou leitura de dano
- `animated_portrait_dialog`
  - separar blink, mouth frames e estado emocional; fallback e retrato estatico
- `kinetic_hype_text`
  - limitar duracao e registrar owner de sprites, tiles, CRAM ou H-Int
- `typewriter_voice_text`
  - revelar texto por cadence declarada e delegar SFX de texto a `xgm2-audio-director` quando houver audio
- `flavor_text_interaction`
  - carregar strings reais do `glyph_manifest` e manter limite de leitura por interacao

## Contrato de Runtime para Menus

Menus e title screens devem ser tratados como cenas de primeira classe.

Defaults de implementacao:
- texto e UI critica em `WINDOW` ou superficie fixa equivalente
- fundo vivo por `BG_A` + `BG_B` + tecnica controlada, nunca por gambiarra sem owner
- item selecionado com feedback animado real
- estado de paleta, scroll, `WINDOW` e callbacks especiais resetado ao sair

Nao aprovar por default:
- menu com texto critico em plano rolavel
- health bar como retangulo simples sem buffer de dano quando o contrato exige leitura de impacto
- UI pixel art com subpixel motion, AA, blur ou free-scale no runtime
- selecao so por troca de cor
- idle completamente morto
- efeito especial sem contrato de teardown

Quando houver FX:
- declarar owner de `H-Int`, palette cycling e split visual
- provar que o menu continua legivel e sem flicker

## Anti-padroes

- inventar getter SGDK inexistente
- prender camera no player sem deadzone, clamp ou justificativa de cena fixa
- suavizar camera com valores fracionarios sem snap inteiro no render final
- usar shake como ruido permanente ou esconder falta de impacto de animacao
- desligar fisica/render de objetos fora da camera sem margem e excecoes de telegraph
- chamar `SYS_doVBlankProcess()` dentro da cena em vez do loop principal
- redeclarar globais em mais de um `.c`
- confiar em build manual sem wrapper e sem caminho absoluto
- chamar a cena de pronta sem ROM rodando em BlastEm
- aceitar `save.sram` fora do sandbox do projeto como prova valida

## Lib case obrigatoria

Antes de generalizar uma tecnica, consulte:

- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/`
- `doc/05_technical/92_sgdk_engine_pattern_registry.json`

Cada caso ali existe para travar um aprendizado real em forma reproduzivel.

## Integracao

- combinar com `sprite-animation` para runtime de animacao
- combinar com `multi-plane-composition` quando a decisao envolver BG_A/BG_B/foreground
- combinar com `character-design` quando uma decisao de runtime depender de palette swap ou escala do roster
- combinar com `forward-kinematics-rigging` quando a tarefa envolver juntas, correntes, tentaculos ou membros articulados
- combinar com `xgm2-audio-director` quando a tarefa envolver ownership de canal, mix de PCM e arquitetura de audio
