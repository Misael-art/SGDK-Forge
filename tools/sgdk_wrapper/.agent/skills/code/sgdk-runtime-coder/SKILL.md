---
name: sgdk-runtime-coder
description: Use quando a tarefa envolver codigo C SGDK 2.11 real, montagem de cena, sprites, BGs, HUD, audio, loop principal, build no Windows, scroll avancado, raster split, pseudo-3D, DMA scheduling e fechamento do ciclo ate ROM com evidencia em emulador. Nao substitui megadrive-elite, scene-state-architect, sgdk-build-wrapper-operator ou megadrive-vdp-budget-analyst; trabalha entre eles como o programador perito de runtime.
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

- `megadrive-elite`
  - ponto de entrada do workspace
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
9. header relevante em `sdk/sgdk-2.11/inc/`

## Quando usar

- bug de compilacao ou link em SGDK 2.11
- bug de loop principal, VBlank ou ordem de atualizacao
- integracao de sprite, BG, HUD, texto, audio ou parallax
- escolha entre `VDP_drawImageEx` e `MAP_create`
- reset de estado entre cenas
- tune de `SPR_initEx`
- validacao de runtime com BlastEm

## Saidas obrigatorias

- `runtime_decision_log`
- `api_reality_check`
- `scene_reset_plan` quando houver transicao de cena
- `scene_transition_runtime_contract` quando houver `scene_transition_card`
- `resource_loading_model` quando houver streaming, preload, animacao grande ou asset scene-local
- `build_evidence`
- `emulator_evidence`
- `delivery_findings`

## Contrato Operacional

### Entrada minima

- `res/resources.res`
- codigo de runtime alvo
- laudo vigente de `megadrive-vdp-budget-analyst`
- contexto de build e emulador
- `ui_decision_card` quando houver HUD/UI formal
- `scene_transition_card` quando houver transicao formal
- `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` ou `audio_architecture_card` quando houver espetaculo runtime formal

### Saida minima

- `runtime_decision_log`
- `api_reality_check`
- `scene_reset_plan` quando houver transicao de cena
- `resource_loading_model` quando houver diferenca entre asset total, set residente e upload por frame
- `build_evidence`
- `emulator_evidence`
- `delivery_findings`

### Passa quando

- a decisao de runtime cita explicitamente o budget que a autorizou
- a escolha entre `IMAGE`, `MAP`, streaming e `SPR_initEx` fica rastreavel
- o `runtime_decision_log` declara qual modelo foi usado: `full_resident`, `scene_local_preload`, `animation_window_streaming`, `tilemap_streaming` ou `fallback_reduced_residency`
- runtime separa custo ROM/compressao, tiles residentes em VRAM, DMA de loading/preload e DMA por frame
- quando houver UI formal, o runtime cita `ui_architecture_choice`, ownership e fallback usados
- quando houver transicao formal, o runtime cita `continuity_model`, `runtime_state_handoff`, `teardown_reset_plan` e fallback usados
- quando houver espetaculo runtime formal, o runtime cita cards, owners, budget, teardown e fallback usados
- quando houver anexo tipografico, o runtime cita `font_render_mode`, `font_owner` e `fallback_font_plan` usados
- build, validacao e evidencia apontam para a mesma ROM
- a captura BlastEm registra `runtime_metrics.json` ou evidencia equivalente sem vazar para fora de `out/blastem_env_*`

### Handoff para proxima etapa

- entregar a ROM e o `runtime_decision_log` para `validate_resources.ps1`
- entregar identidade da ROM e evidencia para `doc/changelog` e `doc/10-memory-bank.md`

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

## Contrato de runtime para HUD/UI formal

Quando houver `ui_decision_card`, o runtime deve:

- consumir `ui_architecture_choice`, `plane_ownership_map` e `fallback_plan` antes de escrever qualquer HUD
- consumir `fx_ownership_map` antes de ligar split, wobble, palette cycling ou qualquer FX de interface
- registrar no `runtime_decision_log` se a rota final ficou elite ou fallback
- impedir segundo owner implicito de `WINDOW`, `H-Int` ou paleta especial
- tratar `profile_kind=front_end_profile` como menu/title/front-end formal, nao como excecao improvisada
- se houver anexo tipografico, consumir `font_render_mode`, `charset_profile`, `font_owner` e `fallback_font_plan` antes de escolher renderer
- `fixed_custom_hud_font`
  - preferir `VDP_loadFont` ou emissao por tile-index math para HUD, labels e leitura rapida
- `variable_width_tidytext`
  - reservar para dialogo, credito, lore, terminais e front-end controlado
- `display_font_plus_body_font`
  - reservar para title/menu/front-end com `profile_kind=front_end_profile`
- nunca usar compositor proporcional caro por frame em HUD de combate
- `glyph_manifest` fecha o subset real de glifos; sem ele nao subir charset expandido nem cache temporario caro

## Contrato de Runtime para Menus

Menus e title screens devem ser tratados como cenas de primeira classe.

Defaults de implementacao:
- texto e UI critica em `WINDOW` ou superficie fixa equivalente
- fundo vivo por `BG_A` + `BG_B` + tecnica controlada, nunca por gambiarra sem owner
- item selecionado com feedback animado real
- estado de paleta, scroll, `WINDOW` e callbacks especiais resetado ao sair

Nao aprovar por default:
- menu com texto critico em plano rolavel
- selecao so por troca de cor
- idle completamente morto
- efeito especial sem contrato de teardown

Quando houver FX:
- declarar owner de `H-Int`, palette cycling e split visual
- provar que o menu continua legivel e sem flicker

## Anti-padroes

- inventar getter SGDK inexistente
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
