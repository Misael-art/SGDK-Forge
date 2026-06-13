# Changelog Canonico - Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

## Estado Inicial

- projeto bootstrapado a partir do wrapper central
- documentacao minima materializada
- scene regression declarada em `doc/scene-regression.json`
- companion inicial esperado em `doc/scene-contracts.json`

## 2026-06-07 - v014 Road polish + evidencia multi-frame

- Corrigido o blocker visual dominante remanescente de BG_A sem promover falso verde: `build_chase_first_playable_assets.py` agora reduz ruido singleton da estrada, reforca guias de perspectiva, adiciona dithering material controlado e mantém indexacao/tile budget sob controle.
- `src/gameplay/chase_road.c` reduziu o streak horizontal por scanline e substituiu VScroll por coluna independente por scroll vertical coeso, evitando a quebra perceptiva das laterais da estrada.
- `chase_contact_shadow_16x8_strip_v011` passou a ser uma elipse conectada multi-tom; teste novo impede regressao para sombra fragmentada.
- Testes de builder: `python -m unittest data.builders.tests.test_chase_v009_assets` passou `11/11`.
- Build canonico gerou `out/rom.bin`, SHA256 `984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9`, `393216` bytes.
- Budget medido: BG_B `480`, BG_A `210`, letterbox `1`, total `691/744`, headroom `53`; `res_graph_audit` passou com 31 declaracoes OK.
- Tilemap audit: BG_A SHA256 `0d32085e02e0e4c47da8b0d0313c1e92e55e704c431bdb3dba35d94da907f995`, `210` tiles finais, `88.28125%` dedup e zero conflitos.
- BlastEm/runtime: `frames_seen=151`, `samples_recorded=32`, `cpu_load_max=75`, `p95=73`, `over_budget_frames=0`, `max_scanline_sprites=9`, `sprite_engine_peak=19`.
- Evidencia visual: `out/evidence/scenes/first_playable_slice/screenshot.png` foi inspecionado e passou `out/logs/visual_screenshot_color_gate_report.json` sem retorno da capsula teal.
- Evidencia multi-frame: `out/evidence/motion/chase_v014_scene_multiframe/chase_v014_scene_multiframe.webp` e `chase_v014_scene_multiframe_report.json` foram gerados de capturas BlastEm reais nos frames 90/120/150/180.
- Regressao de cena: baseline de `first_playable_slice` atualizado somente apos inspecao/gate; matriz final passou `3/3`.
- Status honesto: BG_A melhorou mas permanece `rework` no juiz estetico (`0.5631/0.58`); `creative_ready=false`, `ready_for_aaa=false`, `visual_gate_blocked` e `perceptual_motion_unvalidated` continuam corretos.

## 2026-06-05 - Audio: estados musicais + ownership fixo CH1/CH2/CH3

- `system/audio` refatorado para suportar `AudioMusicState`: `menu`, `intro`, `pressure`, `climax`, `victory`, `failure`.
- Ownership fixo de canais PCM:
  - CH1: cama musical / stinger de estado
  - CH2: FX primario (impacto/pulse/victory/failure como cue legado)
  - CH3: UI/foley (menu/jump/land/pickup/pressure)
- Mapeamento atual sem novos assets: `MENU/INTRO/PRESSURE/CLIMAX` reutilizam `snd_chase_score_loop` com volume e cadencia de `pressure` ajustadas; `VICTORY/FAILURE` reutilizam `snd_chase_victory`/`snd_chase_failure` no CH1.
- Cenas atualizadas:
  - `scene_boot`: entra em `AUDIO_MUSIC_INTRO` e promove `AUDIO_MUSIC_MENU` ao transicionar para o menu.
  - `scene_menu`: entra em `AUDIO_MUSIC_MENU`.
  - `scene_chase`: fases controlam `pressure/climax` via `AUDIO_setIntensity`; resultado troca para `AUDIO_MUSIC_VICTORY/FAILURE`.
  - `scene_demo`: entra em `AUDIO_MUSIC_INTRO`.
- Audio validation: passou (`out/logs/audio_validation_report.json`), 10 recursos, 0 issues, 3,47% do budget de 4 MB.
- Build canonico gerou `out/rom.bin`, SHA256 `cb4121bfb21d6a2f4f4833bf89c120acff5e93e5c0ae322da2bed058d30729f6`, `393216` bytes.
- Evidencia BlastEm canonica via bundle (`out/logs/blastem_evidence.json` + `out/evidence/blastem/session_manifest.json`): `screenshot.png`, `save.sram`, `visual_vdp_dump.bin`.
- Blocker criativo honesto: faltam trilhas dedicadas por estado (menu/intro/pressure/climax) e um design musical aprovado; a implementacao atual simula variacao via volume e cadencia de cue.

## 2026-06-05 - Runtime AAA feel: caps + strips resilientes

- Padronizado clamp defensivo de hitstop para no maximo `6` frames.
- Padronizado clamp defensivo de camera shake para no maximo `5` px em X/Y.
- `chase_player` e `chase_pursuer` agora derivam `numFrame` das `SpriteDefinition` (animacao 0) para suportar strips maiores sem assumir contagem fixa.
- `doc/scene-regression.json` foi reordenado para priorizar `first_playable_slice` como alvo padrao de captura visual (evita screenshot de baixa informacao do menu).
- Build canonico gerou `out/rom.bin`, SHA256 `9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7`, `393216` bytes.
- Evidencia BlastEm fresca: `out/evidence/blastem/screenshot.png`, `out/evidence/blastem/save.sram`, `out/evidence/blastem/visual_vdp_dump.bin`.

## 2026-06-05 - Highscore Endless em SRAM (CCSV v1) + HUD/Result

- Adicionado `system/save_data` (`inc/system/save_data.h`, `src/system/save_data.c`) com schema `CCSV v1` em SRAM offset `0x600`.
- `scene_chase` inicializa o save no enter e submete o `score` apenas no Result e apenas no modo Endless (atualiza highscore quando `score` supera o recorde).
- HUD do Chase passou a exibir `SCORE` e `HI` no Endless durante gameplay (linhas 2/3 quando fora do modo cinematic) e `SCORE/HIGH` no Result, com `NEW RECORD` quando aplicável.
- `chase_result_state` baseline foi atualizado para refletir o novo card de resultado com score/highscore.
- Evidencia BlastEm: `out/evidence/scenes/chase_result_state/save.sram` confirma `CCSV` em `0x600` com `ver=1` e `highscore=1234`; `visual_vdp_dump.bin` extraido do bloco `VLAB` no offset `0x200` (184 bytes).

## 2026-06-04 - VLAB SRAM dump e bootstrap deterministico v015

- Adicionado export visual `VLAB` em `src/system/runtime_probe.c`, no offset SRAM `0x200`, preservando `MDRT` e `READY`.
- Atualizado `tools/sgdk_wrapper/lib/blastem_evidence.psm1` para reconhecer `VLAB` nos offsets `0x000`, `0x200` e `0x400` e extrair `visual_vdp_dump.bin` da evidencia canonica BlastEm.
- Adicionado flag SBIS `force_chase_failure_result` para capturar `chase_result_state` sem depender de derrota emergente/timing aos 1800 frames.
- Build canonico SGDK 2.11 gerou `out/rom.bin`, SHA256 `8e41c92794cb5d60f9562dca8ffa335124f0b05b5cd61fa2f5dee919efe7c4c6`, `393216` bytes.
- BlastEm canonico capturou `screenshot.png`, `save.sram` e `visual_vdp_dump.bin`; dump SHA256 `e06a7aac1de470e5c29b55e718f0335eeb986dd023a8c2fb479dc7da1b38b9e3`.
- `visual_delivery_gate_report.json` passou a registrar `measurement_level=vdp_dump_verified`, mas manteve `technical_ready_creative_blocked`.
- A regressao de cenas foi reexecutada e passou `3/3` para menu, first playable e resultado.
- Corrigido o comparador de regressao para aceitar `screenshot_viewport_crop` por cena; o estado de resultado usa crop estavel porque a captura full-window do BlastEm inclui moldura/desktop fora do frame VDP.
- Closeout tecnico executou 7/7 passos com sucesso e permaneceu `blocked` por gate visual/perceptivo e risco conservador de colisao VRAM no `res_graph`.
- Metodologia continua bloqueada por `perceptual_motion_unvalidated`: faltam aprovacao humana e os quatro eixos perceptivos (`fluidez`, `leitura`, `naturalidade`, `impacto`).
- Status honesto: buildado e testado tecnicamente no BlastEm; ainda nao e entrega AAA.

## 2026-06-04 - Celestial Chase v011 Pixel-Exact implementada

- Promovidos BG_A/BG_B v011; BG_A agora popula 512px com gutters laterais tile-aligned e preserva o centro visivel de 320px pixel-identico a v009.
- Unificados deslocamento, abertura de faixa, escala pre-renderizada, bounce/ricochete, sombra, hitbox e colisao dos obstaculos em um unico estado Z deterministico.
- Adicionados torso v011 com gola de seguranca e variantes de patas traseiras, sombras de contato podaveis, fonte HUD customizada e zonas BG_B pelo owner existente de `HSCROLL_LINE`.
- Corrigido o probe de scanline para medir geometria `FrameVDPSprite` real em quatro linhas espacadas por frame, evitando que a propria telemetria destrua o budget.
- Criado enumerador ligado a ROM para trafego/impacto/Pulse; pior caso ficou em `12/20`, com `8` sprites de headroom, e o BlastEm observou pico real `9/20`.
- Residencia medida pelo ResComp/source hash ligado a ROM: BG_B `488`, BG_A `186`, letterbox `1`, total `675/744`, headroom `69`; o gutter custou apenas `1` tile unico.
- Corrigido o `res_graph` para aceitar evidencia medida scene-local ligada ao hash da ROM e ao hash das fontes, sem depender de linhas ResComp apagadas por builds incrementais.
- Reparado o harness SBIS com capture hold v2 e comparacao tolerante estritamente limitada; regressao deterministica passou `3/3`.
- Adicionado `budget_alias_owner` para impedir que o resultado, que compartilha `app_scene_id=4`, roube as metricas do first playable; teste do auditor passou `12/12`.
- Tornados idempotentes os contratos derivados e alinhado o closeout ao modo `production`, impedindo que recompilacao sem mudanca torne a regressao fresca artificialmente stale.
- Corrigidos os validadores de hygiene/resources para usar hash .NET compartilhado em subprocessos PowerShell.
- Build canonico SGDK 2.11 passou com `errors=0` e gerou `out/rom.bin`, SHA256 `950e35dfe1510769c3f9b9b53c45f3a91b3db1c44c273fecc8928e6a18d60a52`, `393216` bytes.
- BlastEm confirmou boot, gameplay basico, resultado de derrota, audio e performance estavel; MDRT curto/partial: `frames_seen=151`, zero overruns, CPU maximo `72`, p95 `70`, scanline real `9`, sprite engine `19`.
- Testes: projeto `23/23`; suites do wrapper de residencia medida, SBIS hold e tolerancia de regressao passaram.
- Status honesto: `implementado`, `buildado`, `testado_em_emulador` e `validado_budget_tecnico_v011`; aprovacao perceptual humana, `visual_vdp_dump.bin`, trace DMA detalhado e rota de vitoria por input permanecem pendentes.

## 2026-06-04 - Avaliacao corretiva v011 Pixel-Exact

- Auditado o feedback visual da v010 contra assets, runtime, contratos e budgets reais.
- Confirmados como P0: continuidade lateral de BG_A, contrato Z compartilhado para obstaculos/colisao, fechamento do dorso do Perseguidor, ciclo das patas traseiras e reparo do loop de regressao/input.
- Corrigido o diagnostico da estrada: o plano ja e `512x256`, mas BG_A popula apenas `320x224` e o line scroll chega a `-64px..+17px`, expondo colunas vazias/BG_B incompativel.
- Classificada a rota de 512px como `cabe_com_recuo`: usar tilemap sparse/deduplicado com gutters, alvo de no maximo 48 tiles unicos adicionais e hard acceptance de 56 sem nova reparticao.
- Corrigido o eixo do parallax: faixas horizontais de BG_B pertencem ao `HSCROLL_LINE`; `VSCROLL_COLUMN` permanece para offsets verticais por coluna.
- Rejeitados para v011 segura: Lua como sprite, multiplexing de estrelas por HBlank/SAT e slot VRAM independente para a garra distante.
- Detectada telemetria enganosa: `max_scanline_sprites` vem de `SPR_getUsedVDPSprite()` total e e limitado artificialmente a 20; cenarios offline vigentes medem 14/9/12, mas precisam ser regenerados na v011.
- Registrado que contato de sombra deve usar sprites simples/dithered com poda, e que o HUD exige `ui_decision_card`, `glyph_manifest` e resolucao da divergencia PAL1/PAL2.
- Criado `doc/superpowers/specs/2026-06-04-celestial-chase-v011-pixel-exact-assessment.md`.
- Nenhum asset/runtime foi alterado, nenhuma ROM foi rebuildada e nenhum status foi promovido.

## 2026-06-04 - Celestial Chase v009 cinematic refactor

- Reprovada a composicao v008 como referencia visual apesar do build e da estabilidade: mattes opacos, anatomia defeituosa, boss plano e fisica de planos invertida.
- Remasterizados BG_A/BG_B, heroi, estrela, Pulse, nuvens e modulos do Perseguidor em assets v009 source-derived.
- Adicionado `chase_road` como owner de `HSCROLL_LINE`, `VSCROLL_COLUMN`, nuvens diagonais e barra inferior do climax; BG_B deixou de derivar lateralmente.
- Refatorado o Perseguidor para torso, cabeca e duas garras com FK por LUT inteira, uploads escalonados e poda ativa de SAT.
- Adicionados afterimages frame-locked, Pulse animado, estrela animada, camera shake em X/Y, Shadow/Highlight contextual e HUD cinematografico compacto.
- Corrigido o budget estrutural: `SPR_initEx(680)`, duplicatas compartilhando slots de VRAM, pool simultaneo de tres obstaculos, estimativa `648/680` tiles de sprite e `674/744` tiles de background/letterbox.
- Removidos membros externos residuais do torso source-derived para impedir anatomia duplicada quando as garras modulares sao compostas.
- Substituidas multiplicacoes por scanline por diferencas finitas e atualizacao de tabelas a 30 Hz; a carga caiu de cerca de 160% para `cpu_load_max=51`/`p95=50`.
- O preenchimento do letterbox passou a usar tile residente linear e deixou de gerar falso positivo de tiles carregados por codigo no `res_graph`.
- Testes `test_chase_v009_assets` e `test_chase_v009_runtime_contract`: 9 passaram.
- Build canonico SGDK 2.11 passou com `errors=0` e gerou `out/rom.bin`, SHA256 `a685b460d5397f0c4fe809350a9da653f6e322531bd0b7e027922b32bbbe1176`, `393216` bytes.
- BlastEm preservou screenshot ativo, sequencia de quatro quadros e SRAM MDRT fresca em `out/evidence/blastem_gameplay_v009/`.
- Amostra MDRT curta/partial: alvo 60 fps, `frames_seen=151`, zero quadros acima do budget, CPU maximo 51, p95 50, pico de 20 sprites por scanline e 14 sprites do engine.
- Corrigido o wrapper de evidencia para rejeitar `PrintWindow` quase todo preto e para publicar caminhos/frescor de screenshot e SRAM no relatorio estruturado.
- Metodologia passou a reconhecer screenshot, SRAM e GIF; faltam somente aprovacao humana, quatro eixos perceptivos e `visual_vdp_dump.bin`.
- Hygiene passou sem blockers e audio passou com 10 recursos, zero issues e 3,47% do budget de 4 MB.
- Regressao fresca de `first_playable_slice` divergiu do baseline antigo; o baseline nao foi atualizado automaticamente.
- Closeout canonico permaneceu `blocked` por regressao, risco conservador de residencia VRAM, pico de 20 sprites/scanline no limite e gates visuais/perceptivos.
- Status honesto: implementado, buildado e `testado_em_emulador` no escopo curto; VDP dump, rodada completa, `validado_budget` e aprovacao perceptual humana permanecem pendentes.

## 2026-06-04 - First playable chase slice

- Implementado fluxo `BRANDING -> BOOT/title -> MENU -> CHASE -> resultado`, com rodada de 75 segundos, tres faixas, salto, Celestial Pulse, pause, integridade, energia, pressao, tres fases, vitoria e derrota.
- Modularizado runtime em `chase_rules`, `chase_player`, `chase_obstacles`, `chase_pursuer`, `chase_hud`, `scene_chase` e `system/audio`.
- Integrados fundos elite BG_B/BG_A, sprites source-baked aprovados, obstaculos, pickup, FX e 10 recursos XGM2 originais.
- Removidos clears de plano por DMA imediato; line scroll completo, CRAM timeline e SAT usam fila de VBlank.
- Corrigida legibilidade do resultado apos revisao no BlastEm: atores/FX ocultos e BGs escurecidos antes do card.
- Build corrente: `out/rom.bin`, SHA256 `4ca6d83df6ec03d4d614a3fc2ff2ffe1381bffc5ee285acc1392a31c30a14844`, `393216` bytes.
- BlastEm da ROM corrente confirmou gameplay ativo e derrota; amostra MDRT: 60 fps alvo, zero quadros acima do budget, CPU maximo 44, p95 43, pico de 20 sprites por scanline.
- Evidencias preservadas em `out/evidence/blastem/gameplay_active.png`, `failure_result.png`, `screenshot.png` e `save.sram`.
- Ensaio de reinicio/menu por input automatizado ficou inconclusivo porque o harness nao entregou input de gameplay; vitoria, rota completa e aprovacao perceptual humana permanecem pendentes.
- Materializada regressao por bootstrap SRAM para menu, gameplay e resultado; compare real passou menu/resultado e bloqueou `first_playable_slice` porque o runner espera SRAM ate capturar a derrota, enquanto o baseline correto e gameplay ativo.
- Freshness final passou com `stale=0`; closeout permaneceu `blocked` e ROM mastering `mastering_needs_fix` pelos blockers declarados, sem divergencia de hash/checksum/regiao.
- Status honesto: implementado, buildado e observado em BlastEm no escopo acima; `ready_for_aaa=false`.

## 2026-06-02 - Celestial Chase visual benchmark v001

- Adicionada cena `APP_SCENE_CHASE` com entrada direta no runtime para prova visual.
- Promovido `res/gfx/chase_compare_flat.png` como `IMAGE img_chase_compare_flat` em `.res`.
- Ajustado `SPR_initEx(8)` para liberar VRAM ao asset flat de 1110 tiles unicos nesta prova sem sprites.
- Atualizados GDD, spec de cenas, memory bank e report de promocao com status `lab_not_delivery`.
- Corrigida delegacao local de `build/run/clean/rebuild.bat` para `tools/sgdk_wrapper`.
- Restaurados PNGs de branding corrompidos a partir de `tools/sgdk_wrapper/modelo`.
- Removido BOM de `res/resources.res` para o ResComp aceitar o manifesto.
- Build gerou `out/rom.bin` SHA256 `dab33df15904743f7891333370ab29060ac0edfcffa1e69b2fe246533fe3f587`.
- BlastEm capturou `out/evidence/blastem/screenshot.png`; a primeira evidencia foi parcial por falta de heartbeat READY/VLAB.
- Conectado `MDRuntimeProbe_init()` e `MDRuntimeProbe_tick()` no loop principal.
- Recaptura canonica confirmou SRAM `MDRT/READY` para ROM SHA256 `2a63344f4e0c8c5b88eacd737d445496e7dc4ce2095eb29d84aebe94e38d711f`.
- Criado `out/logs/visual_delivery_gate_report.json` com `ready_for_aaa=false`, `lab_not_delivery` e status maximo `technical_lab_validated`.

## 2026-06-02T11:29:12.9543142-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_brand_fx_tiles -> v001 (res/branding/brand_fx_tiles.png)
  - img_brand_engine_logo -> v001 (res/branding/brand_engine_logo.png)
  - img_brand_author_logo -> v001 (res/branding/brand_author_logo.png)
  - img_brand_project_logo -> v001 (res/branding/brand_project_logo.png)
  - img_brand_presents_text -> v001 (res/branding/brand_presents_text.png)
  - img_chase_compare_flat -> v001 (res/gfx/chase_compare_flat.png)
- ROM: build_v001 (sha256 dab33df15904743f7891333370ab29060ac0edfcffa1e69b2fe246533fe3f587, 131072 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_delivery_gate_missing, changelog_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-02T11:29:25.5944273-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 dab33df15904743f7891333370ab29060ac0edfcffa1e69b2fe246533fe3f587, 131072 bytes)
- Validation: errors=0, warnings=5
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_delivery_gate_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

## 2026-06-02T12:35:51.1420066-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 2a63344f4e0c8c5b88eacd737d445496e7dc4ce2095eb29d84aebe94e38d711f, 131072 bytes)
- Validation: errors=0, warnings=7
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-02T12:36:17.8070716-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 2a63344f4e0c8c5b88eacd737d445496e7dc4ce2095eb29d84aebe94e38d711f, 131072 bytes)
- Validation: errors=0, warnings=6
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, visual_delivery_gate_missing, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_missing
- Emulator evidence: fresh_sram_unconfirmed

## 2026-06-02T12:51:09.2582034-03:00 - visual_gate_refresh

- Task: visual_gate_refresh
- Skills: "visual-excellence-standards","megadrive-vdp-budget-analyst","sgdk-build-wrapper-operator"
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 2a63344f4e0c8c5b88eacd737d445496e7dc4ce2095eb29d84aebe94e38d711f, 131072 bytes)
- Validation: errors=0, warnings=6
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_closeout_gate_missing
- Emulator evidence: ok
- Notes: visual_delivery_gate_report criado para marcar CHASE como benchmark visual validado em BlastEm, com lab_not_delivery preservado.

## 2026-06-02T12:56:40.1382795-03:00 - scene_closeout_blocked

- Task: scene_closeout_blocked
- Skills: "sgdk-build-wrapper-operator","visual-excellence-standards","megadrive-vdp-budget-analyst"
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 2a63344f4e0c8c5b88eacd737d445496e7dc4ce2095eb29d84aebe94e38d711f, 131072 bytes)
- Validation: errors=0, warnings=5
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed
- Emulator evidence: ok
- Notes: scene_closeout_gate_report gerado como blocked; blockers restantes sao de GDD, gate visual e promocao AAA, nao de evidencia ausente.

## 2026-06-02 - elite_split_scene approval candidate v005

- Gerada prancha `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\elite_split_scene\chase_elite_split_approval_board_v005.png`.
- Escopo de aprovacao: direcao de composicao BG_B/BG_A, separacao da estrada e leitura geral do split.
- Fora do escopo desta aprovacao: extracao runtime de sprites, contrato final de paleta e validacao final de VRAM.
- v001, v003 e v004 foram autoreprovadas antes de chegar ao usuario por contaminacao de swatches, erro de transparencia e residuo de ceu no BG_A.

## 2026-06-02 - locked visual direction and runtime candidates

- Congelada `elite_split_scene_candidate_v005` como direcao visual aprovada pelo usuario em `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\elite_split_scene\locked_visual_direction_v005.json`.
- Gerada candidata tecnica `runtime_split_candidates_v007` com BG_B completo e BG_A baixo da estrada; estimativa `975 + 381 = 1356` tiles, folga de 60 tiles contra teto util 1416.
- Gerado pacote `sprite_runtime_candidates_v003` para aprovacao: heroi `run_toward` 64x80/48x64, boss far 64x48 e boss mid 80x64, todos como PNG 4bpp/PLTE16.
- Boss large/near foi autoreprovado como sprite unico por contaminacao de matte e custo; proxima rota correta e rig modular com head/horns, torso, hooves e dust FX separado.
- Rodado `art_diagnostic.py`; cenario `2_res_inadequate_check` por tres PNGs fonte em `res/` que precisam conversao, sem promocao nova para ROM nesta etapa.

## 2026-06-02 - graphics rework directive and v006 candidate

- Feedback humano retornou protagonista e perseguidor para rework grafico refinado.
- Registrada diretriz em `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\rework_directive_graphics_v001.json`.
- Atualizado `doc/03_art/02_visual_feedback_bank.md` com `Contorno Escuro Antes do Dither` e `Perseguidor Precisa Atacar no Eixo Z`.
- Mantido heroi 64x80 como alvo preferido por decisao de gameplay: perseguidor ataca em profundidade, nao disputa corrida lateral colada.
- Gerada candidata `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\sprite_rework_outline_zaxis_v006\chase_graphics_rework_approval_board_v006.png`.
- v004 autoreprovada por contorno interno pesado; v005 autoreprovada por board sobreposto e fragmentos laterais do perseguidor; v006 e a candidata visual atual.
- Fundo runtime v007 permanece em standby; nenhuma promocao para `res/`, nenhum build e nenhum BlastEm nesta etapa.

## 2026-06-02 - Source_Baked_Pixel_Art_Standard

- Usuario rejeitou definitivamente a v006 com status `User_Rejected_Heavy_Line_Art`.
- Ativada nova heuristica `Source_Baked_Pixel_Art_Standard`: toda inteligencia grafica deve nascer no desenho original; conversor SGDK atua apenas como empacotador de indices para o VDP.
- Atualizado `doc/03_art/02_visual_feedback_bank.md` com a regra `Source-Baked Pixel Art Standard`.
- Criado manifesto `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\source_baked_pixel_art_candidates_v001\source_baked_pixel_art_standard_manifest.json`.
- Bloqueada qualquer promocao baseada em edge detection por luminancia, dilatacao de mascara, dither automatico ou reconstrucao matematica de line art.
- Gerados novos conceitos fonte em `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\source_baked_pixel_art_candidates_v001\hero_source_baked_pixel_art_candidate_v001.png` e `pursuer_source_baked_pixel_art_candidate_v001.png`.
- Montada prancha `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\source_baked_pixel_art_candidates_v001\source_baked_pixel_art_approval_board_v001.png`.
- Status do lote: `concept_source_candidate`; ainda nao e 4bpp final, nao foi promovido para `res/`, nao foi buildado e nao foi testado em emulador.

## 2026-06-03 - Source-baked pixel-lock v002

- Usuario aprovou o lote conceitual `Source_Baked_Pixel_Art_Standard` para reducao estrita a 15 cores + transparente.
- `pixel_lock_v001` foi autoreprovado por contaminacao de crop no heroi; a promocao desse lock foi bloqueada.
- Gerado `pixel_lock_v002` com heroi 64x80 usando a pose limpa `component_2`, perseguidor 3/4 frontal e modulos near/head/hoof.
- Todos os produtos do v002 foram mantidos em `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\source_baked_pixel_art_candidates_v001\pixel_lock_v002\`.
- Validacao local dos PNGs: modo `P`, PLTE 16, transparencia `tRNS=0`, indices 0-15, sem dithering automatico.
- Status: `pixel_lock_generated_pending_runtime_promotion`; nenhuma promocao para `res/`, nenhum ResComp, nenhum build e nenhum BlastEm nesta etapa.

## 2026-06-03 - Animation strip candidate v003

- Usuario bloqueou promocao para `res/` ate aprovacao de movimento: contato de pe, peso, eixo Z, follow-through da capa, rig modular sincronizado e impacto com shake.
- Atualizado `doc/03_art/02_visual_feedback_bank.md` com as heuristicas `Corrida em Eixo Z Precisa de Contato e Pivot`, `Capa Heroica Precisa de Follow Through` e `Boss Modular Precisa de Escala Sincronizada e Impacto`.
- Criado builder rastreavel `rascunho\entrada_bruta\legacy_megadrive_dev\tools\image-tools\build_celestial_chase_animation_v003.py`.
- Gerada prancha `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\source_baked_pixel_art_candidates_v001\animation_strip_candidates_v003\animation_strip_approval_board_v003.png`.
- Gerados strips: heroi `hero_run_toward_64x80_strip_v003.png`, pivot overlay, preview GIF, body/head/hoof modular do perseguidor e `pursuer_impact_dust_fx_64x32_strip_v003.png`.
- Criados contratos JSON de direcao, timing/spacing, pivot/scale, contato de pe, impacto e rig modular.
- Validacao local: PNGs de strip em modo `P`, PLTE16, bit depth 4, colorType 3, `tRNS=0`; `hero_run_toward_strip_integrity_v003.json` retornou `passed`.
- Status: `animation_strip_candidate_generated_pending_human_approval`; nenhuma promocao para `res/`, nenhum ResComp, nenhum build e nenhum BlastEm nesta etapa.

## 2026-06-03T10:54:35.0912530-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_chase_anim_runtime_bg -> v001 (res/gfx/chase_anim_runtime_bg_v004.png)
  - spr_chase_hero_run_toward -> v001 (res/sprites/chase/hero_run_toward_64x80_strip_v003.png)
  - spr_chase_pursuer_body_zloop -> v001 (res/sprites/chase/pursuer_3q_front_mid_96x80_zloop_strip_v003.png)
  - spr_chase_pursuer_head_zloop -> v001 (res/sprites/chase/pursuer_head_horns_112x64_zloop_strip_v003.png)
  - spr_chase_pursuer_hoof_zloop -> v001 (res/sprites/chase/pursuer_attack_hoof_96x64_zloop_strip_v003.png)
  - spr_chase_pursuer_dust_impact -> v001 (res/sprites/chase/pursuer_impact_dust_fx_64x32_strip_v003.png)
- ROM: build_v003 (sha256 e43892dd739cdfafd1507873c350d7b8a1f17736a4bfefa5819b4cd8cfcb9efc, 262144 bytes)
- Validation: errors=0, warnings=10
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, budget_doc_mismatch, changelog_missing, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T10:55:08.4326519-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 e43892dd739cdfafd1507873c350d7b8a1f17736a4bfefa5819b4cd8cfcb9efc, 262144 bytes)
- Validation: errors=0, warnings=9
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, budget_doc_mismatch, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T11:04:35.6960169-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 e43892dd739cdfafd1507873c350d7b8a1f17736a4bfefa5819b4cd8cfcb9efc, 262144 bytes)
- Validation: errors=0, warnings=9
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T11:04:58.4545083-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 e43892dd739cdfafd1507873c350d7b8a1f17736a4bfefa5819b4cd8cfcb9efc, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T14:59:14.3597795-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - spr_chase_pursuer_dust_impact -> v002 (res/sprites/chase/pursuer_impact_dust_fx_64x32_strip_v005.png)
- ROM: build_v004 (sha256 9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed, 262144 bytes)
- Validation: errors=0, warnings=9
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, changelog_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T14:59:51.1715977-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed, 262144 bytes)
- Validation: errors=0, warnings=9
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-03T15:04:42.8887178-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - spr_chase_pursuer_dust_impact -> v003 (res/sprites/chase/pursuer_impact_dust_fx_64x32_strip_v005.png)
- ROM: build_v004 (sha256 9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed, 262144 bytes)
- Validation: errors=0, warnings=11
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, changelog_missing, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T15:05:41.7486839-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v004 (sha256 9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-03T15:14:31.9247457-03:00 - runtime_animation_v005_blastem_closeout

- Task: runtime_animation_v005_blastem_closeout
- GIF de observacao preservado no projeto em `out/evidence/motion/chase_runtime_like_animation_observation_v005.gif`.
- Observacao visual do GIF detectou que a poeira v003 estava quase estatica/fraca quando congelada em D3; o movimento do heroi ficou coerente.
- Criado builder `rascunho\entrada_bruta\legacy_megadrive_dev\tools\image-tools\build_celestial_chase_impact_fx_v005.py`.
- Promovido `spr_chase_pursuer_dust_impact` para `res/sprites/chase/pursuer_impact_dust_fx_64x32_strip_v005.png`, PLTE16, transparencia index 0, sem dither automatico.
- `SCENE_chase` atualizado para burst de poeira D0-D4 com ticks `2,2,2,3,3`, independente do boss, disparado no B3 junto ao shake `+2,-2,+1,-1,0`.
- ROM: build_v004 (sha256 9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed, 262144 bytes).
- BlastEm: target_scene_match=true, fresh_sram_confirmed=true, gameplay_basico=funcional, performance=estavel, audio=ok.
- Runtime metrics: capture_status=partial, frames_seen=151, samples_recorded=32, over_budget_frames=0, cpu_load_max=21, max_scanline_sprites=16, sprite_engine_peak=3, fx_peak_concurrency=1.
- Validation: errors=0, warnings=5.
- Blockers restantes: gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed.
- Status: technical_ready/testado_em_emulador/validado_budget; nao e AAA final ate aprovacao humana do GIF e desbloqueio do gate visual/GDD.

## 2026-06-04 - methodology_adoption

- Materializados `doc/project_methodology_manifest.json` e `doc/technique_usage_manifest.json`.
- Claim vigente: `critical_motion=required`.
- Claims explicitamente nao aplicaveis ao runtime atual: `road_physics`, `modular_boss`.
- Evidencia GIF migrada para dentro do projeto.
- `.mddev/project.json` integrado ao contrato metodologico e ao report correspondente.
- `freshness_audit` mantido como validacao base; nenhum claim foi inferido por texto.
- Preflight confirmado sem avisos; metodologia bloqueada somente por `perceptual_motion_unvalidated`.
- Closeout reprovado corretamente e `ready_for_aaa` permaneceu falso.
- Nenhuma tecnica promovida para `MESTRE_*`.

## 2026-06-04 - project_hygiene_adoption

- Materializados `doc/project_hygiene_manifest.json` e `rascunho/README.md` sem sobrescrever artefatos existentes.
- Adicionado `project_hygiene` as validacoes obrigatorias do manifesto metodologico.
- Higiene passou com zero blockers; metodologia continua bloqueada honestamente por `perceptual_motion_unvalidated`.
- Nenhuma ROM, captura ou status de proficiencia foi promovido nesta alteracao.

### Closeout observado

- `validate_resources.ps1 -CloseoutGate` confirmou `project_hygiene_ready=true`, `technique_usage_ready=true` e `ready_for_aaa=false`.
- O blocker `perceptual_motion_unvalidated` e os blockers visuais/GDD permanecem ativos.
- `scene_contract_compile_report.json` permanece stale; nenhuma ROM ou captura foi regenerada nesta rodada.

## 2026-06-04 - legacy_path_encapsulation

- Copiados source art, derivados historicos e scripts usados pelo projeto para subpastas organizadas de `rascunho/`.
- Gerados tres `_external_input_inventory.json` com hashes por arquivo e registrados em `doc/project_hygiene_manifest.json`.
- Inventarios passaram por verificacao arquivo a arquivo; alteracao posterior de copia passa a bloquear higiene.
- Materializado `naming_policy=portable_descriptive_v1`; nenhum nome ativo nao canonico foi encontrado.
- Migradas referencias ativas do workspace antigo para caminhos locais do projeto.
- Novo gate `external_path_reference_outside_project` impede que codigo, scripts, manifestos ou docs ativos dependam de outro workspace.
- Preflight passou a resolver `sdk/sgdk-2.11/` local antes de qualquer `GDK` herdado.
- Closeout confirmou `project_hygiene_ready=true`, `technique_usage_ready=true` e `ready_for_aaa=false`.
- Logs historicos em `out/` foram preservados; nenhuma ROM ou evidencia BlastEm foi regenerada.

## 2026-06-04T05:19:52.7249075-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_chase_bg_b_elite -> v001 (res/gfx/chase/chase_bg_b_elite.png)
  - img_chase_bg_a_elite -> v001 (res/gfx/chase/chase_bg_a_elite.png)
  - spr_chase_obstacle_boulder -> v001 (res/sprites/chase/chase_obstacle_boulder_64x48.png)
  - spr_chase_obstacle_brand -> v001 (res/sprites/chase/chase_obstacle_brand_64x48.png)
  - spr_chase_energy_star -> v001 (res/sprites/chase/chase_energy_star_32x32.png)
  - spr_chase_pulse_impact -> v001 (res/sprites/chase/chase_pulse_impact_64x48.png)
- ROM: build_v005 (sha256 4dd8b6d21637f678412c18dbde35583542741e97e82ceea98cfa525324dd02c7, 393216 bytes)
- Validation: errors=0, warnings=15
- Blockers: perceptual_motion_unvalidated, gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_missing, budget_doc_mismatch, changelog_missing, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_path_mismatch

## 2026-06-04T05:20:58.7320441-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v005 (sha256 4dd8b6d21637f678412c18dbde35583542741e97e82ceea98cfa525324dd02c7, 393216 bytes)
- Validation: errors=0, warnings=11
- Blockers: perceptual_motion_unvalidated, gdd_substantial_insufficient, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_missing, budget_doc_mismatch, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T05:47:44.0029069-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v006 (sha256 bfbb7adffd586edc8f5f065b1c623a44250b806a17a73470223ae3ce73480850, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, budget_doc_mismatch, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_path_mismatch

## 2026-06-04T05:48:52.9372721-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v006 (sha256 bfbb7adffd586edc8f5f065b1c623a44250b806a17a73470223ae3ce73480850, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, budget_doc_mismatch, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T05:57:34.0648557-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v007 (sha256 f2e3fa1d9720da611ad378f19e75a19018ee62425d6e47ad07e8ceb4307819f5, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_path_mismatch

## 2026-06-04T05:58:20.9477683-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v007 (sha256 f2e3fa1d9720da611ad378f19e75a19018ee62425d6e47ad07e8ceb4307819f5, 393216 bytes)
- Validation: errors=0, warnings=9
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T06:03:42.0920256-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v008 (sha256 4ca6d83df6ec03d4d614a3fc2ff2ffe1381bffc5ee285acc1392a31c30a14844, 393216 bytes)
- Validation: errors=0, warnings=11
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-04T06:04:29.8834127-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v008 (sha256 4ca6d83df6ec03d4d614a3fc2ff2ffe1381bffc5ee285acc1392a31c30a14844, 393216 bytes)
- Validation: errors=0, warnings=9
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T09:54:54.6240098-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_chase_bg_b_v009 -> v001 (res/gfx/chase/chase_bg_b_v009.png)
  - img_chase_bg_a_v009 -> v001 (res/gfx/chase/chase_bg_a_v009.png)
  - ts_chase_letterbox_v009 -> v001 (res/gfx/chase/chase_letterbox_tile_v009.png)
  - spr_chase_cloud_v009 -> v001 (res/sprites/chase/chase_cloud_64x32_strip_v009.png)
  - spr_chase_hero_run_v009 -> v001 (res/sprites/chase/hero_run_toward_64x80_strip_v009.png)
  - spr_chase_hero_ghost_v009 -> v001 (res/sprites/chase/hero_ghost_64x80_strip_v009.png)
  - spr_chase_pursuer_torso_v009 -> v001 (res/sprites/chase/pursuer_torso_96x80_strip_v009.png)
  - spr_chase_pursuer_head_v009 -> v001 (res/sprites/chase/pursuer_head_80x64_strip_v009.png)
  - spr_chase_pursuer_claw_v009 -> v001 (res/sprites/chase/pursuer_claw_64x64_strip_v009.png)
  - spr_chase_energy_star_v009 -> v001 (res/sprites/chase/chase_energy_star_32x32_strip_v009.png)
  - spr_chase_pulse_impact_v009 -> v001 (res/sprites/chase/chase_pulse_impact_64x48_strip_v009.png)
- ROM: build_v009 (sha256 52932953124b5ed193ec238730112f1e40884a240292c77cfd09e8bd573ff6de, 393216 bytes)
- Validation: errors=0, warnings=13
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, changelog_missing, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-04T09:55:53.6422459-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v009 (sha256 52932953124b5ed193ec238730112f1e40884a240292c77cfd09e8bd573ff6de, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T10:34:19.8462857-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - spr_chase_pursuer_torso_v009 -> v002 (res/sprites/chase/pursuer_torso_96x80_strip_v009.png)
- ROM: build_v010 (sha256 a685b460d5397f0c4fe809350a9da653f6e322531bd0b7e027922b32bbbe1176, 393216 bytes)
- Validation: errors=0, warnings=11
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, changelog_missing, scene_regression_incomplete, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-04T10:36:54.8361440-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v010 (sha256 a685b460d5397f0c4fe809350a9da653f6e322531bd0b7e027922b32bbbe1176, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T16:35:32.2272856-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_chase_bg_b_v011 -> v001 (res/gfx/chase/chase_bg_b_v011.png)
  - img_chase_bg_a_v011 -> v001 (res/gfx/chase/chase_bg_a_v011.png)
  - spr_chase_obstacle_boulder_v011 -> v001 (res/sprites/chase/chase_obstacle_boulder_64x48_strip_v011.png)
  - spr_chase_obstacle_brand_v011 -> v001 (res/sprites/chase/chase_obstacle_brand_64x48_strip_v011.png)
- ROM: build_v011 (sha256 125734700637531c91d7bdf0dc6dad85d5d58705d3129e8554676f9590482c65, 393216 bytes)
- Validation: errors=0, warnings=11
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, changelog_missing, scene_regression_incomplete, freshness_audit_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-04T16:38:14.0007200-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v011 (sha256 125734700637531c91d7bdf0dc6dad85d5d58705d3129e8554676f9590482c65, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T17:03:53.5320573-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - ts_chase_hud_font_v011 -> v001 (res/gfx/chase/chase_hud_font_v011.png)
  - spr_chase_pursuer_torso_v011 -> v001 (res/sprites/chase/pursuer_torso_96x80_strip_v011.png)
  - spr_chase_contact_shadow_v011 -> v001 (res/sprites/chase/chase_contact_shadow_16x8_strip_v011.png)
- ROM: build_v012 (sha256 f843ea54da3f09a454d3d763147a9f69e18a91b8038a47071d500c3f9d66dcda, 393216 bytes)
- Validation: errors=0, warnings=14
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, changelog_missing, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-04T17:04:27.3641032-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v012 (sha256 f843ea54da3f09a454d3d763147a9f69e18a91b8038a47071d500c3f9d66dcda, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T17:28:49.0427818-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v013 (sha256 950e35dfe1510769c3f9b9b53c45f3a91b3db1c44c273fecc8928e6a18d60a52, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, scene_regression_incomplete, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-04T17:29:31.1505917-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v013 (sha256 950e35dfe1510769c3f9b9b53c45f3a91b3db1c44c273fecc8928e6a18d60a52, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, audio_validation_stale, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T22:59:31.5114102-03:00 - vlab_scene_regression_refresh

- Task: vlab_scene_regression_refresh
- Skills: sgdk-runtime-coder, sgdk-build-wrapper-operator, megadrive-vdp-budget-analyst, visual-excellence-standards
- Asset snapshots: nenhum hash novo
- ROM: build_v014 (sha256 c4071a5fcf5567d274ab1168a89168650f785c5f7849381eb61067db2a119427, 393216 bytes)
- Validation: errors=0, warnings=9
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, changelog_missing, freshness_audit_stale, project_documentation_sync_stale, scene_closeout_gate_stale
- Emulator evidence: ok
- Notes: VLAB SRAM block captured as visual_vdp_dump.bin for current ROM; scene regression refreshed 3/3 with stable result-scene viewport comparison; AAA remains blocked by perceptual/human visual gate.

## 2026-06-04T23:28:24.1891965-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v015 (sha256 8e41c92794cb5d60f9562dca8ffa335124f0b05b5cd61fa2f5dee919efe7c4c6, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, freshness_audit_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-04T23:30:21.6707038-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v015 (sha256 8e41c92794cb5d60f9562dca8ffa335124f0b05b5cd61fa2f5dee919efe7c4c6, 393216 bytes)
- Validation: errors=0, warnings=9
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-04T23:42:14.0718278-03:00 - qa_bootstrap_result_v015

- Task: qa_bootstrap_result_v015
- Skills: sgdk-runtime-coder, scene-state-architect, sgdk-build-wrapper-operator, megadrive-vdp-budget-analyst
- Asset snapshots: nenhum hash novo
- ROM: build_v015 (sha256 8e41c92794cb5d60f9562dca8ffa335124f0b05b5cd61fa2f5dee919efe7c4c6, 393216 bytes)
- Validation: errors=0, warnings=5
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed
- Emulator evidence: ok
- Notes: ROM now exports VLAB and supports SBIS flag force_chase_failure_result for deterministic result-state regression; scene regression passed 3/3 on current ROM; closeout remains blocked by perceptual/visual gates and conservative VRAM collision-risk report.

## 2026-06-05T06:34:59.1671608-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v016 (sha256 50f2f68710879a3eb6d7f23198df3907ca28b32302771f9801a222fd8b32c3bf, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, freshness_audit_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T06:36:28.3754155-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v016 (sha256 50f2f68710879a3eb6d7f23198df3907ca28b32302771f9801a222fd8b32c3bf, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T07:53:28.3842370-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v016 (sha256 50f2f68710879a3eb6d7f23198df3907ca28b32302771f9801a222fd8b32c3bf, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T07:53:53.9863894-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v016 (sha256 50f2f68710879a3eb6d7f23198df3907ca28b32302771f9801a222fd8b32c3bf, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T08:04:32.8761191-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v017 (sha256 936fa3fb9941b747007092b6b9d12e9d7a7f49a78b57d616011aad3fab132fd9, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T08:05:08.6199033-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v017 (sha256 936fa3fb9941b747007092b6b9d12e9d7a7f49a78b57d616011aad3fab132fd9, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T08:22:46.4699107-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v018 (sha256 a13fbace547f67c11ae88671079bbd12410e53b6cfd12ed3e8bc44ea4c798331, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T08:23:17.3401978-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v018 (sha256 a13fbace547f67c11ae88671079bbd12410e53b6cfd12ed3e8bc44ea4c798331, 393216 bytes)
- Validation: errors=0, warnings=10
- Blockers: perceptual_motion_unvalidated, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T12:45:00.1959675-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v019 (sha256 fd05c0f4db73130f1faa89e296fcecc11963b3679d6a4630e3ddca9a1336d383, 393216 bytes)
- Validation: errors=0, warnings=13
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T12:45:48.2242279-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v019 (sha256 fd05c0f4db73130f1faa89e296fcecc11963b3679d6a4630e3ddca9a1336d383, 393216 bytes)
- Validation: errors=0, warnings=11
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T12:48:05.1202428-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v019 (sha256 fd05c0f4db73130f1faa89e296fcecc11963b3679d6a4630e3ddca9a1336d383, 393216 bytes)
- Validation: errors=0, warnings=13
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T12:48:36.8760908-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v019 (sha256 fd05c0f4db73130f1faa89e296fcecc11963b3679d6a4630e3ddca9a1336d383, 393216 bytes)
- Validation: errors=0, warnings=11
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T13:40:12.7276434-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=14
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T13:41:06.6356185-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T13:47:55.9269218-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T13:48:54.6145564-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T13:53:14.4381029-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T13:53:52.0454151-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T14:00:56.3030774-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=11
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: ok

## 2026-06-05T14:02:27.0017061-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v020 (sha256 9599476b90fc9e067dfe27ba2c9295d931582c6341f0317ec798dd9d1eb482c7, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T15:41:10.7310563-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v021 (sha256 cb4121bfb21d6a2f4f4833bf89c120acff5e93e5c0ae322da2bed058d30729f6, 393216 bytes)
- Validation: errors=0, warnings=15
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-05T15:43:55.2016402-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v021 (sha256 cb4121bfb21d6a2f4f4833bf89c120acff5e93e5c0ae322da2bed058d30729f6, 393216 bytes)
- Validation: errors=0, warnings=12
- Blockers: perceptual_motion_unvalidated, orphan_project_root_entry, noncanonical_project_entry_name, external_path_reference_outside_project, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T19:00:24.3918985-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v021 (sha256 cb4121bfb21d6a2f4f4833bf89c120acff5e93e5c0ae322da2bed058d30729f6, 393216 bytes)
- Validation: errors=0, warnings=8
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-05T19:01:01.1963615-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v021 (sha256 cb4121bfb21d6a2f4f4833bf89c120acff5e93e5c0ae322da2bed058d30729f6, 393216 bytes)
- Validation: errors=0, warnings=9
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, scene_regression_incomplete, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-07T01:07:20.7740983-03:00 - v012_perceptual_visual_gate_reduction

- Task: v012_perceptual_visual_gate_reduction
- Skills: "visual-excellence-standards","art-translation-to-vdp","multi-plane-composition","megadrive-vdp-budget-analyst","scene-state-architect","sgdk-runtime-coder","sgdk-build-wrapper-operator","rom-mastering"
- Asset snapshots:
  - spr_chase_hero_run_v009 -> v002 (res/sprites/chase/hero_run_toward_64x80_strip_v009.png)
  - spr_chase_hero_ghost_v009 -> v002 (res/sprites/chase/hero_ghost_64x80_strip_v009.png)
- ROM: build_v022 (sha256 9b8fdb32b8b949c85e99f13d31f2504dcf6c3432c84bb2c42b8c2357ff2ddcf1, 393216 bytes)
- Validation: errors=0, warnings=8
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, changelog_missing, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: ok
- Notes: Remasterizou os dois assets criticos de foreground motion; ROM hash 9b8fdb32b8b949c85e99f13d31f2504dcf6c3432c84bb2c42b8c2357ff2ddcf1 observado em BlastEm com screenshot, save.sram, visual_vdp_dump.bin, regressao 3/3 e perceptual_check preenchido. ready_for_aaa permanece false; critical_motion ainda requer aprovacao humana.

## 2026-06-07T01:19:31.4777784-03:00 - v012_final_gate_sync

- Task: v012_final_gate_sync
- Skills: "visual-excellence-standards","art-translation-to-vdp","multi-plane-composition","megadrive-vdp-budget-analyst","scene-state-architect","sgdk-runtime-coder","sgdk-build-wrapper-operator","rom-mastering"
- Asset snapshots: nenhum hash novo
- ROM: build_v022 (sha256 9b8fdb32b8b949c85e99f13d31f2504dcf6c3432c84bb2c42b8c2357ff2ddcf1, 393216 bytes)
- Validation: errors=0, warnings=3
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked
- Emulator evidence: ok
- Notes: Sincronizacao final apos docs/manifest: validation errors=0 warnings=3; blockers restantes sao perceptual_motion_unvalidated por ausencia de human_approval_record e visual_gate_blocked por rework criativo nao critico/promocao AAA bloqueada. scene regression 3/3, res_graph ok, audio ok, freshness ok antes do doc sync.

## 2026-06-07T01:25:14.3807447-03:00 - v012_final_validation_state

- Task: v012_final_validation_state
- Skills: "visual-excellence-standards","art-translation-to-vdp","multi-plane-composition","megadrive-vdp-budget-analyst","scene-state-architect","sgdk-runtime-coder","sgdk-build-wrapper-operator","rom-mastering"
- Asset snapshots: nenhum hash novo
- ROM: build_v022 (sha256 9b8fdb32b8b949c85e99f13d31f2504dcf6c3432c84bb2c42b8c2357ff2ddcf1, 393216 bytes)
- Validation: errors=0, warnings=3
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked
- Emulator evidence: ok
- Notes: Estado final da sessao: validation errors=0 warnings=3; blockers restantes sao perceptual_motion_unvalidated por ausencia de human_approval_record e visual_gate_blocked por assets nao criticos/review comercial. Freshness ok, scene regression 3/3, res_graph ok, audio ok, BlastEm evidence ok, ready_for_aaa=false.

## 2026-06-07T08:07:58.9283326-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - spr_chase_hero_run_v009 -> v003 (res/sprites/chase/hero_run_toward_64x80_strip_v009.png)
  - spr_chase_hero_ghost_v009 -> v003 (res/sprites/chase/hero_ghost_64x80_strip_v009.png)
- ROM: build_v023 (sha256 ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908, 393216 bytes)
- Validation: errors=0, warnings=7
- Blockers: perceptual_motion_unvalidated, external_path_reference_outside_project, visual_gate_blocked, changelog_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-07T08:08:30.0852128-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v023 (sha256 ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908, 393216 bytes)
- Validation: errors=0, warnings=7
- Blockers: perceptual_motion_unvalidated, external_path_reference_outside_project, visual_gate_blocked, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-07T08:40:27.0681494-03:00 - v013_sprite_transparency_p0_fix

- Task: v013_sprite_transparency_p0_fix
- Skills: art-asset-diagnostic, art-conversion-pipeline, visual-excellence-standards, sgdk-build-wrapper-operator, rom-mastering
- Asset snapshots: nenhum hash novo
- ROM: build_v023 (sha256 ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908, 393216 bytes)
- Validation: errors=0, warnings=6
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, freshness_audit_stale, project_documentation_sync_stale, scene_closeout_gate_stale
- Emulator evidence: ok
- Notes: Corrigido P0 visual: hero_run_toward_64x80_strip_v009 e hero_ghost_64x80_strip_v009 deixaram de pintar canvas opaco. Adicionado gate de contrato de sprite index0/edge/capsule e gate de screenshot por amostragem de cor proibida. ROM hash BA5D99A7DDB261B0E6625C1BEC90FD0ADEDAFCA62AF0D29B0CBF6F39A9143908; regressao de cena BlastEm passou 3/3; visual_screenshot_color_gate passou. Road/BG_A e perceptual/human review continuam bloqueando AAA.

## 2026-06-07T08:49:56.7092242-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v023 (sha256 ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908, 393216 bytes)
- Validation: errors=0, warnings=5
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, scene_tilemap_conversion_report_stale, freshness_audit_stale
- Emulator evidence: ok

## 2026-06-07T08:50:34.6098266-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v023 (sha256 ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908, 393216 bytes)
- Validation: errors=0, warnings=7
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, emulator_evidence_stale, scene_tilemap_conversion_report_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-07T08:59:03.3330230-03:00 - v013_post_rebuild_evidence_sync

- Task: v013_post_rebuild_evidence_sync
- Skills: sgdk-build-wrapper-operator, rom-mastering, visual-excellence-standards
- Asset snapshots: nenhum hash novo
- ROM: build_v023 (sha256 ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908, 393216 bytes)
- Validation: errors=0, warnings=5
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: ok
- Notes: Rebuild pos-correcao manteve SHA256 BA5D99A7DDB261B0E6625C1BEC90FD0ADEDAFCA62AF0D29B0CBF6F39A9143908. Evidencia BlastEm/runtime/scene regression foi recapturada apos rebuild; screenshot color gate passou novamente. Freshness ok antes deste sync; blockers restantes seguem perceptual_motion_unvalidated e visual_gate_blocked, com road/BG_A e revisao humana pendentes.

## 2026-06-07T10:50:13.8166801-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_chase_bg_b_v011 -> v002 (res/gfx/chase/chase_bg_b_v011.png)
  - img_chase_bg_a_v011 -> v002 (res/gfx/chase/chase_bg_a_v011.png)
- ROM: build_v024 (sha256 810cfa169bd847e04c7530424b2990d4f0cc43477384a58469a362c779fd81a8, 393216 bytes)
- Validation: errors=0, warnings=7
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, changelog_missing, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-07T10:50:52.8536264-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v024 (sha256 810cfa169bd847e04c7530424b2990d4f0cc43477384a58469a362c779fd81a8, 393216 bytes)
- Validation: errors=0, warnings=6
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-07T11:06:30.6320689-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_chase_bg_a_v011 -> v003 (res/gfx/chase/chase_bg_a_v011.png)
  - spr_chase_contact_shadow_v011 -> v002 (res/sprites/chase/chase_contact_shadow_16x8_strip_v011.png)
- ROM: build_v025 (sha256 984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9, 393216 bytes)
- Validation: errors=0, warnings=7
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, changelog_missing, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: rom_identity_mismatch

## 2026-06-07T11:06:57.9502731-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v025 (sha256 984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9, 393216 bytes)
- Validation: errors=0, warnings=6
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale

## 2026-06-07T11:29:39.5880232-03:00 - v014 road polish and motion evidence

- Task: v014 road polish and motion evidence
- Skills: visual-excellence-standards,art-translation-to-vdp,multi-plane-composition,megadrive-vdp-budget-analyst,sgdk-runtime-coder,rom-mastering
- Asset snapshots: nenhum hash novo
- ROM: build_v025 (sha256 984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9, 393216 bytes)
- Validation: errors=0, warnings=6
- Blockers: perceptual_motion_unvalidated, visual_gate_blocked, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Emulator evidence: runtime_metrics_stale
- Notes: BG_A road polish and cohesive road VScroll; ROM 984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9; scene regression 3/3; motion frame stack generated; visual gate remains blocked honestly.

