<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-06-07T11:45:21-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 21
- Ultimo build versionado: build_v025
- ROM vigente: `984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9` (`393216` bytes)
- Validation summary: errors=0 warnings=3
- Blockers vigentes: perceptual_motion_unvalidated, visual_gate_blocked
- Evidencia de emulador: BlastEm/runtime/scene_regression frescos para ROM vigente
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=testado_em_emulador performance=estavel audio=ok hardware_real=blastem_reference_emulator
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]

**Ultima atualizacao:** 2026-06-07T11:30-03:00
**Fase atual:** v014 reduz o blocker dominante de BG_A/estrada na ROM `984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9`: road polish aplicado no builder, runtime road shearing reduzido, evidencia BlastEm multi-frame gerada, regressao 3/3 e budget VRAM medido em `691/744`.
**Proxima fase:** revisao perceptual humana real da sequencia multi-frame, novo passe artistico em BG_A/HUD/contact shadows se a leitura ainda ficar abaixo do mockup, e somente depois reavaliar `visual_gate_blocked`.

- reprovaÃƒÂ§ÃƒÂ£o reconhecida: a v022 foi tecnicamente verde mas visualmente quebrada; o `velocity_mantle` pintou pixels visiveis no canvas transparente, criando capsula opaca ao redor do protagonista.
- arte/runtime: `spr_chase_hero_run_v009` e `spr_chase_hero_ghost_v009` preservam index 0 transparente; BG_A v014 agora reduz ruido singleton, reforca linhas de fuga e evita scroll vertical por coluna que rasgue as laterais.
- evidencia (BlastEm): `out/evidence/blastem/screenshot.png`, `save.sram` e `visual_vdp_dump.bin` estao frescos para a ROM `984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9`; `out/evidence/scenes/first_playable_slice/screenshot.png` mostra o heroi sem capsula e estrada mais coesa.
- runtime/percepcao: `runtime_metrics.json` mede `scene_id=4`, `frames_seen=151`, `samples_recorded=32`, `cpu_load_max=75`, `p95=73`, `over_budget_frames=0`, `max_scanline_sprites=9`, `sprite_engine_peak=19`; `perceptual_check` permanece zerado ate revisao humana.
- gates novos: `visual_screenshot_color_gate_report_pre_fix.json` reproduz a falha antiga como `blocked`; `visual_screenshot_color_gate_report.json` passa na captura nova. A evidencia multi-frame `out/evidence/motion/chase_v014_scene_multiframe/chase_v014_scene_multiframe.webp` reduz risco de screenshot estatico, mas nao aprova movimento automaticamente.
- blockers honestos: `visual_gate_blocked`, `visual_direction_failed_reduced_not_cleared`, `road_mockup_alignment_needs_review`, `perceptual_motion_unvalidated` e teto `LAB/TECHDEMO`; `ready_for_aaa=false`.

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 0.0F ITERACAO V014 - POLIMENTO DA ESTRADA E EVIDENCIA MULTI-FRAME

- objetivo real: atacar o blocker visual dominante remanescente depois da correcao P0 do heroi, sem gerar ROM apenas por numeracao.
- asset pipeline: `data/builders/build_chase_first_playable_assets.py` passou a aplicar `polish_chase_road_layers()`, `reduce_road_micro_noise()`, `reinforce_road_perspective_overlay()` e `add_road_material_dither()` na BG_A antes da traducao tile-aware.
- runtime: `src/gameplay/chase_road.c` reduziu o streak horizontal por scanline (`>> 8`) e substituiu VScroll por coluna independente por scroll vertical coeso do plano, evitando que as laterais da estrada parecam quebradas.
- sombra: `derive_contact_shadow_strip()` gera elipse conectada multi-tom; `test_contact_shadow_uses_connected_multi_tone_ellipse` bloqueia regressao para sombra fragmentada.
- testes de builder: `python -m unittest data.builders.tests.test_chase_v009_assets` passou `11/11`.
- ROM buildada apos mudanca significativa: `out/rom.bin`, SHA256 `984d31d4256940e371586c85c83d744753d6d08e8257a255129c900ee7de62a9`, `393216` bytes.
- budget: ResComp mediu BG_B `480` tiles, BG_A `210`, letterbox `1`, total `691/744` e headroom `53`; `res_graph_audit` passou com 31 declaracoes OK.
- tilemap: `scene_tilemap_conversion_report.json` registra BG_A SHA256 `0d32085e02e0e4c47da8b0d0313c1e92e55e704c431bdb3dba35d94da907f995`, `210` tiles finais, `88.28125%` dedup e zero conflitos.
- audio: `validate_audio.ps1` no diretorio do projeto passou com 10 declaracoes e `3.47%` do budget ROM; a falha rodada na raiz do workspace foi descartada como escopo errado.
- runtime BlastEm: `frames_seen=151`, `samples_recorded=32`, `cpu_load_max=75`, `p95=73`, `over_budget_frames=0`, `max_scanline_sprites=9`, `sprite_engine_peak=19`.
- evidencia visual: `out/evidence/scenes/first_playable_slice/screenshot.png` foi inspecionado antes do baseline; gate de cor proibida passou com `tall_columns_50=0`.
- regressao: baseline de `first_playable_slice` atualizado apenas apos inspecao visual/gate; matriz final passou `3/3`.
- motion evidence: `out/evidence/motion/chase_v014_scene_multiframe/frame_090.png`, `frame_120.png`, `frame_150.png`, `frame_180.png`, `chase_v014_scene_multiframe.webp` e `chase_v014_scene_multiframe_report.json` foram gerados de capturas BlastEm reais; deltas entre frames ficam entre `0.2546` e `0.32493`.
- status honesto: BG_A melhorou mas continua `rework` no juiz estetico (`0.5631/0.58`) por dithering material e alinhamento de referencia ainda incompletos; `creative_ready=false` e `ready_for_aaa=false`.

---

## 0.0E ITERACAO V013 - CORRECAO P0 DE TRANSPARENCIA E FALSO VERDE

- causa raiz: `add_hero_velocity_mantle()` preenchia pixels `0` do canvas com indices 2/3/4 em um envelope quase full-frame; o PNG continuava indexado e com `transparency=0`, mas a ROM desenhava a capsula porque esses pixels nao eram mais transparentes.
- correcao: o efeito foi rebaixado para acento de silhueta; ele so recolore pixels visiveis ou adiciona pequenos rims colados ao personagem, nunca linhas/bandas sobre o canvas.
- gate de asset: `validate_sprite_canvas_contract()` foi adicionado ao builder e bloqueia `OPAQUE_FRAME_CAPSULE_RISK`, `NON_INDEX0_BACKGROUND_MATTE` e `SPRITE_CANVAS_TOUCHES_FULL_WIDTH`.
- gate de screenshot: `data/builders/validate_chase_visual_screenshot.py` amostra a ROI do heroi no screenshot BlastEm e detecta concentracao/coluna de cores proibidas de matte teal; a evidencia v022 foi salva como `pre_fix` e reprova.
- assets atuais:
  - `hero_run_toward_64x80_strip_v009.png`: SHA256 `d39390640637698874b5e71f854ad4ae63d61f284d56cc32eeb9d745796c7be1`, `visible_ratio` maximo `0.3666`, edge maximo `88`, index 0 magenta/transparente.
  - `hero_ghost_64x80_strip_v009.png`: SHA256 `38528a907077ce074eb3a274c0763c954c9d70f4c7d427b542965320df1ce553`, herda a silhueta sem capsula.
- motion evidence nova: `chase_hero_silhouette_velocity_v013.gif/.webp`, `chase_hero_ghost_silhouette_velocity_v013.gif/.webp` e `hero_silhouette_transparency_fix_motion_report_v013.json`.
- ROM buildada: `out/rom.bin`, SHA256 `ba5d99a7ddb261b0e6625c1bec90fd0adedafca62af0d29b0cbf6f39a9143908`, `393216` bytes.
- BlastEm/scene: captura canonica OK; regressao primeiro falhou somente `first_playable_slice` por mudanca visual intencional, baseline foi atualizado apenas para essa cena, e nova comparacao passou `3/3`.
- budget/audio: `res_graph_audit` passou com 31 declaracoes OK e zero overlaps apos atualizar `doc/vram_residency_report.json`; `validate_audio` passou com 10 declaracoes e 3,47% do budget ROM.
- divida visual nao resolvida: a estrada/BG_A ainda precisa rework perceptual contra `chase_compare_flat`; a correcao do heroi nao libera `creative_ready`.

## 0.0D ITERACAO V012 - REDUCAO DO GATE VISUAL/PERCEPTUAL

- objetivo real: quebrar o ciclo de ROM incremental atacando blockers dominantes, nao trocar numero de build.
- mudanca de arte: o builder `data/builders/build_chase_first_playable_assets.py` agora remasteriza o strip do heroi com envelope `velocity_mantle`, denoise controlado e remap de paleta; o ghost deixou de ser checkerboard deletado e preserva massa coerente.
- testes de builder: `python -m unittest data.builders.tests.test_chase_v009_assets` passou `6/6`.
- assets criticos:
  - `spr_chase_hero_run_v009`: `elite_ready`, score `0.7913`, sem issues.
  - `spr_chase_hero_ghost_v009`: `elite_ready`, score `0.7937`, sem issues.
- motion evidence local:
  - `out/evidence/motion/chase_hero_velocity_mantle_v012.gif`
  - `out/evidence/motion/chase_hero_velocity_mantle_v012.webp`
  - `out/evidence/motion/chase_hero_ghost_velocity_mantle_v012.gif`
  - `out/evidence/motion/chase_hero_ghost_velocity_mantle_v012.webp`
  - `out/evidence/motion/hero_velocity_mantle_motion_report_v012.json`
- ROM buildada apos mudanca significativa: `out/rom.bin`, SHA256 `9b8fdb32b8b949c85e99f13d31f2504dcf6c3432c84bb2c42b8c2357ff2ddcf1`, `393216` bytes.
- BlastEm canonico: `out/logs/blastem_evidence.json` status `ok`, screenshot/SRAM/VDP dump presentes e apontados por campos diretos para o validator.
- regressao: `first_playable_slice` divergiu uma vez do baseline antigo por mudanca visual intencional; baseline foi atualizado somente para essa cena e nova comparacao passou `3/3`.
- VRAM: `doc/vram_residency_report.json` foi atualizado para o hash atual; `res_graph_report.json` voltou a `ok`, `vram.status=ok`, `overlaps=0`.
- visual delivery gate: reclassificado de `lab_not_delivery` obsoleto para `visual_gate_blocked`; isso removeu o falso blocker `procedural_fallback_as_final` sem declarar entrega AAA.
- closeout: passos do closeout executaram `8/8 ok`, mas o status continua `blocked` por `perceptual_motion_unvalidated` e `visual_gate_blocked`; o stale interno de `scene_tilemap_conversion_report` foi um efeito de ordem do closeout e a validacao isolada posterior ficou sem esse blocker.
- status honesto: `implementado`, `buildado`, `testado_em_emulador`, `validado_budget`; ainda nao `creative_ready`, nao `ready_for_aaa` e nao aprovado humanamente.

---

## 0.0C HIGHSCORE ENDLESS EM SRAM (CCSV v1) - IMPLEMENTADO E COM EVIDENCIA BLASTEM

- criado `system/save_data` com schema `CCSV v1` em SRAM offset `0x600`
- highscore e atualizado apenas no Result e apenas no modo Endless; HUD mostra `SCORE/HI` durante gameplay Endless e `SCORE/HIGH` no Result com `NEW RECORD`
- evidencia canonica da cena `chase_result_state` (BlastEm) confirma `CCSV ver=1 highscore=1234` em `0x600` e dump visual `VLAB` extraido de `0x200` (`184` bytes)

## 0.0B INSTRUMENTACAO VLAB, SBIS RESULTADO E REGRESSAO FRESCA - BUILDADA E OBSERVADA NO BLASTEM

- `runtime_probe` agora exporta bloco visual `VLAB` em SRAM no offset `0x200`, preservando `MDRT` no offset `0x000` e `READY` no offset `0x100`
- o bloco `VLAB` usa schema `1`, `184` bytes, 24 palavras de metricas VDP/runtime e 64 palavras de paleta CRAM via `PAL_getColors(0, ..., 64)`
- `tools/sgdk_wrapper/lib/blastem_evidence.psm1` reconhece `VLAB` nos offsets `0x000`, `0x200` e `0x400` e extrai `out/evidence/blastem/visual_vdp_dump.bin` sem destruir a evidencia `MDRT`
- SBIS ganhou flag `force_chase_failure_result`; `chase_result_state` deixou de depender de derrota emergente aos 1800 frames e agora captura o card de falha de forma deterministica em `capture_frame=120`
- build canonico SGDK 2.11 gerou `out/rom.bin`, SHA256 `8e41c92794cb5d60f9562dca8ffa335124f0b05b5cd61fa2f5dee919efe7c4c6`, `393216` bytes
- BlastEm canonico confirmou `screenshot.png`, `save.sram` e `visual_vdp_dump.bin`; dump SHA256 `e06a7aac1de470e5c29b55e718f0335eeb986dd023a8c2fb479dc7da1b38b9e3`, SRAM SHA256 `1f0e57901b49897e3db8adf3fe849f32d0d373e553ccc6ca45fbb13e9ef7452a`
- amostra MDRT curta/partial da ROM atual: `frames_seen=151`, `samples_recorded=32`, `over_budget_frames=0`, `cpu_load_max=72`, `cpu_load_p95=70`, `max_scanline_sprites=9`, `sprite_engine_peak=19`
- regressao de cenas fresca passou `3/3`: menu, first playable e resultado; o estado de resultado usa crop estavel de viewport e bootstrap explicito `force_chase_failure_result`
- `visual_delivery_gate_report.json` foi atualizado para `measurement_level=vdp_dump_verified`; o status maximo continua `technical_ready_creative_blocked`
- `scene_closeout_gate_report.json` executou 7/7 passos com sucesso e permanece `blocked` por `vram_residency_collision_risk`, `perceptual_motion_unvalidated`, `visual_gate_blocked`, `procedural_fallback_as_final` e `visual_direction_failed`
- metodologia ainda esta `blocked` por `perceptual_motion_unvalidated`; sinais ausentes: `human_approval_record`, `perceptual_check.fluidez`, `perceptual_check.leitura`, `perceptual_check.naturalidade`, `perceptual_check.impacto`
- status honesto: `implementado`, `buildado`, `testado_em_emulador` e com dump visual VLAB capturado; ainda nao `ready_for_aaa` nem aprovado perceptualmente

---

## 0.0A ITERACAO V011 PIXEL-EXACT - IMPLEMENTADA, BUILDADA E OBSERVADA NO BLASTEM

- parecer de origem: `doc/superpowers/specs/2026-06-04-celestial-chase-v011-pixel-exact-assessment.md`
- BG_A foi promovido para arte populada em 512px com gutters espelhados tile-aligned; o centro visivel de 320px permanece pixel-identico a v009 e o custo incremental medido foi apenas `1` tile unico
- obstaculos agora derivam Y, abertura de faixa, escala pre-renderizada, bounce/ricochete, sombra, hitbox e janela de colisao de um unico estado Z deterministico
- Perseguidor recebeu torso v011 com gola de seguranca e variantes de patas traseiras; cabeca e garras continuam modulos FK separados com margem de sobreposicao controlada
- heroi, hazards e garras receberam sombras de contato simples e podaveis; HUD usa fonte customizada source-derived em `WINDOW`
- BG_B usa zonas horizontais pelo owner existente de `HSCROLL_LINE`; Lua/estrelas permanecem no fundo e multiplexing HBlank de estrelas continua rejeitado
- ROM final: `out/rom.bin`, SHA256 `950e35dfe1510769c3f9b9b53c45f3a91b3db1c44c273fecc8928e6a18d60a52`, `393216` bytes
- BlastEm confirmou boot, gameplay basico, resultado de derrota, audio e performance estavel para a ROM final; evidencia dedicada da cena esta em `out/evidence/scenes/first_playable_slice/screenshot.png`
- amostra MDRT curta/partial: `frames_seen=151`, `over_budget_frames=0`, `cpu_load_max=72`, `cpu_load_p95=70`, `max_scanline_sprites=9`, `sprite_engine_peak=19`
- enumerador ligado a geometria `FrameVDPSprite` da ROM cobre estados FK/pressao/heroi/FX e mede pior caso `12/20`, com `8` sprites de headroom
- residencia medida pelo ResComp/source hash ligado a ROM: BG_B `488`, BG_A `186`, letterbox `1`, total `675/744`, headroom `69`; `res_graph` passou com zero overlaps/issues
- regressao deterministica usa capture hold SBIS v2 e passou `3/3`: menu, gameplay e resultado
- testes: `23/23` no projeto; suites do wrapper para residencia medida, SBIS hold e tolerancia de regressao passaram
- status honesto: `implementado`, `buildado`, `testado_em_emulador` e `validado_budget_tecnico_v011`; ainda nao aprovado perceptualmente nem `ready_for_aaa`
- pendencias: trace DMA detalhado, aprovacao perceptual humana e prova rastreavel da rota de vitoria/transicoes por input

---

## 0.0 ITERACAO VISUAL V009 - IMPLEMENTADA, BUILDADA E OBSERVADA NO BLASTEM

- a v008 foi reprovada visualmente apesar da estabilidade tecnica: mattes opacos, frames anatomicos defeituosos, Perseguidor monolitico e parallax invertido
- a v009 promove `img_chase_bg_b_v009` + `img_chase_bg_a_v009`, com ceu profundo fixo, estrada de alto contraste e `chase_road` como owner unico de `HSCROLL_LINE` + `VSCROLL_COLUMN`
- o heroi usa apenas os quatro frames fonte aceitos; os frames com anatomia/ruido rejeitados nao entram no runtime
- estrela e Pulse reservam indice 0 transparente; o Pulse agora possui seis quadros de expansao
- o Perseguidor usa torso, cabeca e duas garras independentes com FK por LUT inteira, frames escalados pre-renderizados e poda da garra distante
- afterimages, garras duplicadas e nuvens duplicadas compartilham slots de VRAM quando frame-locked
- reserva de sprites: `SPR_initEx(680)`; estimativa ativa `648/680`; backgrounds + letterbox `674/744`, margem `70` tiles
- pool de obstaculos reduzido para tres slots, o conjunto simultaneo real: boulder, brand e energia
- build canonico SGDK 2.11 gerou `out/rom.bin`, SHA256 `a685b460d5397f0c4fe809350a9da653f6e322531bd0b7e027922b32bbbe1176`, `393216` bytes, com validacao `errors=0`
- BlastEm da ROM final preservou gameplay ativo em `out/evidence/blastem_gameplay_v009/screenshot.png`, sequencia temporal em `out/evidence/blastem_gameplay_v009/sequence/frame_01..04/` e SRAM MDRT fresca em `out/evidence/blastem_gameplay_v009/save.sram`
- a sequencia observada confirma duas garras com alcance relativo variavel, obstaculos atravessando faixas, heroi sem matte opaco e estrela sem caixa escura; aprovacao perceptual humana continua pendente
- amostra MDRT curta/partial da ROM final: `frames_seen=151`, `over_budget_frames=0`, `cpu_load_max=51`, `cpu_load_p95=50`, `max_scanline_sprites=20`, `sprite_engine_peak=14`
- o primeiro road loop com multiplicacao por scanline a 60 Hz chegou a cerca de 160% de CPU; diferencas finitas por soma e tabelas a 30 Hz restauraram a amostra para maximo 51% sem reduzir atores ou profundidade
- o torso source-derived foi limpo novamente para remover membros externos residuais; sem esse corte, o rig modular produzia anatomia duplicada apesar de usar sprites separados
- o validador final reconhece `testado_em_emulador=true` para este escopo rastreavel; isso nao prova rodada completa, vitoria, aprovacao perceptual ou budget VDP
- closeout canonico permanece `blocked`: regressao `first_playable_slice` divergiu do baseline antigo, o grafo generico reporta tres overlaps conservadores e o budget audit marca pico de 20 sprites/scanline no limite
- metodologia permanece bloqueada somente por `perceptual_motion_unvalidated`; faltam aprovacao humana, quatro eixos perceptivos e `visual_vdp_dump.bin`
- hygiene passou sem blockers; audio passou com 10 recursos, zero issues e 3,47% do budget de 4 MB
- status honesto: `implementado`, `buildado` e `testado_em_emulador` no escopo curto; ainda nao `validado_budget`, aprovado visualmente ou provado em rodada completa
- contratos canonicos: `doc/contracts/chase_v009_road_physics_contract.json`, `chase_v009_modular_boss_contract.json`, `chase_v009_scene_ownership.json` e `chase_v009_palette_slot_audit.json`
- tecnicas perigosas `cram_overdrive_midline` e `zero_overhead_hblank_isr` permanecem rejeitadas para a rota segura v009

---

## 0.1 ESTADO OPERACIONAL DO FIRST PLAYABLE 2026-06-04

- fluxo de entrega implementado: `BRANDING -> BOOT/title -> MENU -> CHASE -> resultado -> reinicio/menu`
- `APP_SCENE_CHASE` agora possui rodada de 75 segundos, tres faixas, A para salto, B para Pulse, START para pause, integridade, energia, pressao, vitoria e falha
- runtime modularizado em `chase_rules`, `chase_player`, `chase_obstacles`, `chase_pursuer`, `chase_road`, `chase_hud`, `scene_chase` e `system/audio`
- fundo elite tile-aware promovido para BG_B + BG_A; sprites source-baked aprovados foram preservados
- audio original local integrado por XGM2 com ownership fixo de CH1/CH2/CH3
- sprite reserve v011: `SPR_initEx(680)`; fundo residente medido: 675 tiles; headroom: 69 tiles
- DMA planejado no pior quadro: `6404/7168` bytes, status `ok` com margem curta; duas tabelas de line scroll e SAT incluidos
- `VDP_clearPlane` foi removido das entradas de cena; clears usam CPU e commits por frame usam `DMA_QUEUE`
- bootstrap de QA `SBIS` foi implementado no runtime probe para captura direta e one-shot de cenas no BlastEm
- ROM corrente buildada: SHA256 `950e35dfe1510769c3f9b9b53c45f3a91b3db1c44c273fecc8928e6a18d60a52`, `393216` bytes
- BlastEm confirmou `APP_SCENE_CHASE` ativa e resultado de derrota na ROM corrente; evidencia de cena em `out/evidence/scenes/first_playable_slice/`
- amostra MDRT corrente: alvo 60 fps, `over_budget_frames=0`, `cpu_load_max=72`, `cpu_load_p95=70`, `max_scanline_sprites=9`, `sprite_engine_peak=19`, escopo curto/partial
- ensaio automatizado de A/B na tela de resultado foi inconclusivo porque o harness nao conseguiu entregar input de gameplay nem em teste de pause; reinicio/menu e rota de vitoria continuam sem prova rastreavel
- blocker metodologico honesto permanece `perceptual_motion_unvalidated`; aprovacao humana nao foi inferida

### Estado dos gates do first playable

- build: sucesso; `out/rom.bin` corrente existe e foi observado no BlastEm
- validation: zero erros; warnings de gate visual, regressao, freshness/closeout e promocao AAA
- audio validation: passou, 10 recursos, zero issues, 3,47% do budget de 4 MB
- game design contracts: passaram sem blockers
- hygiene: passou sem blockers
- gameplay basico da cena e derrota: observados no BlastEm; performance da amostra: estavel
- audio: recursos/XGM2 validados e sessao reportou `audio=ok`; qualidade auditiva humana nao foi aprovada
- softlock/reinicio/menu e vitoria: nao comprovados por input rastreavel
- scene regression: `3/3` passa; menu/gameplay em comparacao exata e resultado em tolerancia estritamente limitada ao titulo variavel da janela do BlastEm
- freshness final: deve ser reexecutado apos a consolidacao documental v011
- closeout final: tecnicamente desbloqueado em build/runtime/regressao/residencia; permanece bloqueado pelos gates criativos/perceptuais e evidencias visuais completas
- ROM mastering: checksum, alinhamento, regiao, hash BlastEm e boot passam; decisao final `mastering_needs_fix`
- ready_for_aaa: false

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- pacote de source art autoral aprovado pelo usuario em `rascunho\entrada_bruta\legacy_megadrive_dev\source_art\celestial_chase_v001`
- preview VDP 320x224 aprovado como rota de laboratorio em `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\vdp_preview`
- cena `APP_SCENE_CHASE` implementada como entrada direta do projeto, usando `IMAGE img_chase_anim_runtime_bg` e sprites source-baked aprovados
- ROM vigente buildada em `out/rom.bin` como build_v004; evidencia BlastEm fresca confirma cena `CHASE`/`app_scene_id=4`
- `runtime_probe` canonico conectado ao loop principal e confirmado por SRAM `MDRT/READY`
- `visual_delivery_gate_report.json` criado para marcar o ROM como benchmark visual, nao entrega AAA
- candidata visual `elite_split_scene_candidate_v005` criada para aprovacao humana em `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\elite_split_scene`
- `elite_split_scene_candidate_v005` congelada como direcao visual apos aprovacao humana (`prossiga`), com registro em `locked_visual_direction_v005.json`
- candidata tecnica de fundo `runtime_split_candidates_v007` criada: BG_B completo + BG_A de pista baixo, estimativa 1356 tiles e folga de 60 tiles vs teto util 1416
- pacote de sprites candidatos `sprite_runtime_candidates_v003` criado para aprovacao visual: heroi `run_toward` 64x80/48x64 e boss far/mid; boss near/impact marcado como rig modular pendente
- diretriz de rework grafico criada em `data\processed\celestial_chase_v001\rework_directive_graphics_v001.json`: heroi 64x80 com contorno escuro/sem dither automatico e perseguidor em frontal 3/4 no eixo Z
- candidata atual `sprite_rework_outline_zaxis_v006` criada para aprovacao: heroi 64x80 balanceado, perseguidor 3/4 mid 96x80, head/horns modular 112x64; v004/v005 autoreprovadas por contorno pesado/board ruim/fragmentos da sheet
- `sprite_rework_outline_zaxis_v006` rejeitada pelo usuario com status `User_Rejected_Heavy_Line_Art`
- nova rota ativa: `Source_Baked_Pixel_Art_Standard`, em que a arte nasce como pixel art nativa e o conversor SGDK apenas empacota indices para o VDP
- gerado lote `source_baked_pixel_art_candidates_v001` com novo conceito-fonte de heroi 64x80 e perseguidor frontal 3/4; pixel-lock v002 e animacao v003 aprovados pelo usuario e promovidos para runtime v005
- validacao por GIF runtime-like v005 criou evidencia de movimento antes do claim runtime; a observacao detectou poeira estatica/fraca e levou ao rework do FX
- poeira de impacto v005 substitui o strip v003: burst horizontal D0-D4, PLTE16/tRNS=0, sem dither, animado de forma independente do frame B3 do boss

### O que e placeholder

- fundo runtime v004 e um recuo `fallback_reduced_residency`; a rota visual final `elite_split_scene` continua separada para composicao futura
- obstaculos e props ainda nao tem strips SGDK finais
- a candidata v005 usa sprite preview apenas para contexto; nao e extracao runtime aprovada
- `runtime_split_candidates_v007` segue em standby; `animation_strip_candidates_v003` ja foi promovido para `res/` como prova runtime v005
- `sprite_rework_outline_zaxis_v006` ainda e candidato visual em `data/processed`, sem strip de animacao, sem `res/`, sem build e sem BlastEm
- `source_baked_pixel_art_candidates_v001` possui pixel-lock/animacao aprovados, buildados, observados em GIF e testados em BlastEm; ainda falta aprovacao humana final do GIF como gate visual da animacao
- a prancha `source_baked_pixel_art_approval_board_v001.png` e conceito-fonte; os produtos finais runtime partem de `pixel_lock_v002` e `animation_strip_candidates_v003`

### O que falta para o slice ser completo

- aprovar visualmente o GIF v005 de movimento e impacto antes de ampliar a composicao
- reabrir `runtime_split_candidates_v007` quando houver budget para composicao de fundo mais rica
- produzir obstaculos, props e FX restantes como strips reais
- capturar `visual_vdp_dump.bin`/VLAB quando o fluxo de entrega visual estiver habilitado
- criar baseline/regressao visual deterministica da cena final
- aprofundar GDD para cobrir loop, kit, ritmo, inimigos e criterios de qualidade
- reexecutar scene closeout quando a cena sair de laboratorio para entrega candidata

### Snapshot dos gates QA

- visual_lab_aprovado: parcial; fonte/animacao aprovadas, GIF v005 gerado e BlastEm fresco, aguardando aprovacao humana final do movimento
- gameplay_rom_aprovada: funcional como cena visual, sem loop jogavel
- ready_for_aaa: false
- freshness_audit: ok, stale=0
- scene_closeout_gate: blocked apenas por gates criativos/documentais

### Blockers QA ativos

- `gdd_substantial_insufficient`
- `visual_gate_blocked`
- `procedural_fallback_as_final`
- `visual_direction_failed`

### Metricas de codigo

- first playable atual: `SPR_initEx(420)`, BG_B 501 tiles + BG_A 367/368 tiles, duas tabelas de line scroll e pool estatico de 6 slots
- pior quadro DMA planejado atual: 6404 bytes de 7168; scanline documental maximo 14; evidence runtime corrente pendente
- asset runtime principal: `img_chase_anim_runtime_bg`, 320x224, 16 cores, 258 tiles unicos
- sprite reserve do benchmark: `SPR_initEx(512)` para a prova com heroi 64x80 e boss 96x80 animados
- ResComp mediu heroi com pico de 8 sprites internos/70 tiles por frame; boss body com 6 sprites internos/74 tiles; poeira v005 com 2 sprites internos/18 tiles
- per-frame tile upload: controlado pelo sprite engine SGDK em troca de frame; codigo da cena nao faz DMA manual fora do VBlank
- res graph fresco: 11 declaracoes, VRAM residency `ok`, sprite reserve 512, overlaps 0

### Estado de evidencia canonica

- ROM vigente: SHA256 `9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed`, `262144` bytes
- `validation_report.json`: errors=0, warnings=5, blockers `gdd_substantial_insufficient`, `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`
- `runtime_metrics.json`: presente, `capture_status=partial`, `frames_seen=151`, `samples_recorded=32`, `over_budget_frames=0`, `cpu_load_max=21`, `max_scanline_sprites=16`, `sprite_engine_peak=3`, `fx_peak_concurrency=1`, `target_fps=60`
- `scene_regression_report.json`: ausente
- `emulator_session.json`: ok para a ROM vigente, `target_scene_match=true`, `fresh_sram_confirmed=true`, `gameplay_basico=funcional`, `performance=estavel`, `audio=ok`
- `freshness_audit_report.json`: ok, stale=0
- `visual_delivery_gate_report.json`: presente, `ready_for_aaa=false`, `max_delivery_status=technical_lab_validated`
- `scene_closeout_gate_report.json`: presente, status `blocked` por gates criativos/documentais, nao por evidencia de emulador

---

## 2. O QUE ACABOU DE ACONTECER

**2026-05-24 ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â Branding intro AAA v1 com assets nativos e VDP**

- Criado builder deterministico `tools/image-tools/build_branding_intro_assets.py` para transformar fontes nativas em PNGs SGDK-safe: `brand_engine_logo`, `brand_author_logo`, `brand_project_logo`, `brand_presents_text` e `brand_fx_tiles`.
- `SCENE_branding` deixou de ser placeholder textual e passou a usar `IMAGE` real via `VDP_drawImageEx`, fundo de tiles FX, shimmer/pulse de paleta, PSG procedural e FSM engine/author/project.
- ROM direta SGDK buildada em `tools/sgdk_wrapper/modelo/out/rom.bin`; SHA256 `D012A842ADE368E25AE739F1DBB8A87F1DEAEDBE3799F407D24C2C4B170FD734`.
- Evidencia visual capturada no BlastEm para a mesma ROM final:
  - engine: `out/evidence/blastem_brand_intro_engine_final_rom/screenshot.png`
  - author: `out/evidence/blastem_brand_intro_author_final_rom/screenshot.png`
  - project/presents: `out/evidence/blastem_brand_intro_project_present_final/screenshot.png`
- `res_graph_audit.ps1` passou com status `warn` apenas por exigir evidencia VDP runtime para tiles carregados por codigo. O wrapper canonico ainda fica preso em `validate_resources.ps1`/gate `.agent` degradado; nao promover para closeout final ate corrigir esse gate.

**2026-06-02 ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â Celestial Chase visual benchmark v001 integrado ao runtime**

- Promovido `res/gfx/chase_compare_flat.png` a partir do preview aprovado, com PLTE de 16 entradas e bit depth 4.
- Criada `SCENE_chase` e registrada no scene manager como `APP_SCENE_CHASE`.
- Entrada do projeto apontada diretamente para `CHASE` para evidencia visual rapida em BlastEm.
- Documentado recuo de budget: `compare_flat`, `scene_local_preload`, `IMAGE`, `lab_not_delivery`.
- Corrigida delegacao dos `.bat` locais para o wrapper central e restaurados PNGs de branding corrompidos da copia canonica.
- Build canonico gerou `out/rom.bin`; ResComp exigiu remover BOM de `res/resources.res`.
- `res_graph_audit.ps1` passou com VRAM residency `ok`.
- BlastEm abriu a ROM e capturou `out/evidence/blastem/screenshot.png`; screenshot confirma a cena CHASE em tela.
- Evidencia inicial era parcial por falta de heartbeat READY, VLAB/visual_vdp_dump e closeout de cena.
- Conectado `MDRuntimeProbe_init()` e `MDRuntimeProbe_tick()` em `src/main.c`.
- Recaptura BlastEm confirmou `fresh_sram_confirmed=true`, `READY` em SRAM e ROM SHA256 `2a63344f4e0c8c5b88eacd737d445496e7dc4ce2095eb29d84aebe94e38d711f`.
- Criado `out/logs/visual_delivery_gate_report.json`, bloqueando `ready_for_aaa` e classificando o estado maximo como `technical_lab_validated`.
- Gerado `out/logs/scene_closeout_gate_report.json` como `blocked`; o blocker de relatorio ausente saiu, restando apenas bloqueios de GDD/promocao visual.
- Gerada a prancha `chase_elite_split_approval_board_v005.png` como proxima aprovacao humana; v001/v003/v004 foram autoreprovadas por contaminacao de swatches, erro de transparencia e residuo de ceu em BG_A.
- Aprovada a direcao visual v005 pelo usuario e congelada em `locked_visual_direction_v005.json`.
- Gerada candidata tecnica `runtime_split_candidates_v007`: v005 completa em dois planos excede budget; recuo honesto usa BG_B completo e BG_A apenas na faixa baixa da estrada.
- Gerado pacote `sprite_runtime_candidates_v003`: heroi `run_toward` 64x80/48x64 e boss far/mid em PNG 4bpp/PLTE16; near/impact autoreprovado como sprite unico e roteado para rig modular.
- Rodado `art_diagnostic.py`: cenario `2_res_inadequate_check`, com 3 PNGs fonte soltos em `res/` precisando conversao e sem impacto direto na prova atual.
- Feedback humano retornou o protagonista e perseguidor para rework: contorno escuro de alta definicao, remover dither automatico/granulado, saturar azul/ivory/dourado, manter heroi 64x80, e trocar perseguidor de perfil lateral para frontal 3/4 no eixo Z.
- Canonizadas no feedback bank as heuristicas `Contorno Escuro Antes do Dither` e `Perseguidor Precisa Atacar no Eixo Z`.
- Gerada candidata `sprite_rework_outline_zaxis_v006`; v004 foi autoreprovada por contorno interno pesado e v005 por board sobreposto/fragmentos laterais do perseguidor.
- Usuario rejeitou definitivamente v006: `User_Rejected_Heavy_Line_Art`.
- Criado manifesto `Source_Baked_Pixel_Art_Standard`: conversao automatizada deixa de ser ferramenta de desenho; candidatos novos devem nascer como pixel art nativa, com paleta/linework/rampas ja embutidos na fonte.
- Gerada prancha `source_baked_pixel_art_approval_board_v001.png`; heroi e perseguidor agora sao candidatos de direcao source-baked, sem promocao para `res/`.
- Usuario aprovou o lote conceitual `Source_Baked_Pixel_Art_Standard` para pixel-lock estrito de 15 cores + transparente.
- `pixel_lock_v001` foi autoreprovado por contaminacao de crop no heroi; `pixel_lock_v002` troca para a pose limpa `component_2` e usa mascara exata de componente.
- Gerada prancha `pixel_lock_approval_board_v002.png` e laudo `pixel_lock_report_v002.json`: PNGs paletados PLTE16, `tRNS=0`, sem dither, ainda sem promocao para `res/`, sem ResComp e sem emulador.
- Usuario exigiu gate de animacao antes de liberar `res/`: contato de pe/peso, movimento em eixo Z, follow-through da capa, rig modular sincronizado e frame de impacto com shake.
- Canonizadas no feedback bank as heuristicas `Corrida em Eixo Z Precisa de Contato e Pivot`, `Capa Heroica Precisa de Follow Through` e `Boss Modular Precisa de Escala Sincronizada e Impacto`.
- Criado builder `tools/image-tools/build_celestial_chase_animation_v003.py` e gerada prancha `animation_strip_approval_board_v003.png`.
- `animation_strip_candidates_v003` contem hero strip 64x80 com 8 frames, pivot overlay, preview GIF, contratos de timing/pivot/impacto e strips modulares do perseguidor.
- Validacao local: PNGs dos strips em modo `P`, PLTE16, bit depth 4, colorType 3, `tRNS=0`; `hero_run_toward_strip_integrity_v003.json` retornou `passed`.
- Usuario aprovou o lote `animation_strip_candidates_v003` e autorizou quebrar o congelamento do pipeline.
- Promovido runtime v004 por `tools/image-tools/promote_celestial_chase_animation_v004.py`: fundo runtime de 258 tiles unicos, heroi 64x80, boss body 96x80, head 112x64, hoof 96x64 e dust 64x32 em `res/sprites/chase`.
- `SCENE_chase` agora anima manualmente o heroi com ticks `4,3,3,4,4,3,3,4`, boss body com ticks `6,5,5,7,5,5`, poeira em B3 e shake `+2,-2,+1,-1,0` via `VDP_setVerticalScroll`.
- Build_v003 gerado: ROM SHA256 `e43892dd739cdfafd1507873c350d7b8a1f17736a4bfefa5819b4cd8cfcb9efc`, `262144` bytes; validation `errors=0`, `warnings=9`.
- Validacao por GIF runtime-like v005, preservada localmente em `out/evidence/motion/chase_runtime_like_animation_observation_v005.gif`, revelou que a poeira v003 estava quase estatica/fraca quando congelada em D3.
- Criado `tools/image-tools/build_celestial_chase_impact_fx_v005.py` e promovido `pursuer_impact_dust_fx_64x32_strip_v005.png`: burst horizontal D0-D4, PLTE16, transparencia index 0, sem dither automatico.
- `SCENE_chase` passou a animar a poeira de impacto em timeline propria com ticks `2,2,2,3,3`, disparada no frame B3 junto ao shake vertical.
- Build_v004 gerado: ROM SHA256 `9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed`, `262144` bytes.
- Captura BlastEm fresca confirmou `target_scene_match=true`, `fresh_sram_confirmed=true`, `gameplay_basico=funcional`, `performance=estavel`, `audio=ok`, `max_scanline_sprites=16`, `over_budget_frames=0`.
- Closeout v005 ficou `blocked` apenas por GDD/gate visual/promocao AAA; tecnicamente a cena esta `technical_ready`, `testado_em_emulador=true` e `validado_budget=true`.

---

## 3. DECISOES PENDENTES

- [decisao 1]
- [decisao 2]

---

## 4. DECISION LOG CONSERVADOR

Registre aqui escolhas que evitaram tentativa-e-erro ou mudanca de rota.

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-06-02 | `CHASE` visual benchmark | usar `compare_flat` em `IMAGE` para a primeira ROM visual | `elite_split_scene` final e sprites animados foram adiados ate builder/strips reais | `doc/source_cases/chase_visual_benchmark/asset_promotion_report.md`, `out/evidence/blastem/screenshot.png` | elite split |
| 2026-06-02 | Evidencia BlastEm | conectar runtime probe canonico antes de nova captura | manter apenas screenshot parcial foi recusado para nao rebaixar o gate | `src/main.c`, `src/system/runtime_probe.c`, `out/logs/emulator_session.json` | visual_vdp_dump/VLAB |
| 2026-06-02 | Gate visual | criar `visual_delivery_gate_report.json` com `lab_not_delivery` | declarar AAA por build + screenshot foi recusado | `out/logs/visual_delivery_gate_report.json`, `out/logs/validation_report.json` | split por planos e assets animados |
| 2026-06-02 | Closeout de cena | gerar closeout `blocked` em vez de deixar relatorio ausente | tratar ausencia de closeout como estado aceitavel foi recusado | `out/logs/scene_closeout_gate_report.json` | resolver GDD e gate visual |
| 2026-06-02 | Split visual | submeter `elite_split_scene_candidate_v005` para aprovacao | v001/v003/v004 foram recusadas por problemas visuais/tecnicos | `data/processed/celestial_chase_v001/elite_split_scene/chase_elite_split_approval_board_v005.png` | aprovacao humana |
| 2026-06-02 | Direcao visual | congelar v005 como direcao aprovada e separar nova aprovacao para runtime | promover direto para `res` foi recusado porque budget e sprites ainda nao foram validados | `data/processed/celestial_chase_v001/elite_split_scene/locked_visual_direction_v005.json` | aprovar v007/v003 |
| 2026-06-02 | Split runtime | manter BG_B completo e reduzir BG_A a faixa baixa da pista | v005 full/mid/low em dois planos excedia o teto util de 1416 tiles | `data/processed/celestial_chase_v001/elite_split_scene/runtime_split_candidates_v007/chase_runtime_split_candidates_report_v007.json` | ResComp apos aprovacao |
| 2026-06-02 | Sprites runtime | apresentar apenas heroi e boss far/mid como candidatos | boss large/near como sprite unico foi recusado por matte contaminado e custo alto | `data/processed/celestial_chase_v001/sprite_runtime_candidates_v003/sprite_runtime_candidates_report_v003.json` | strip real e rig modular |
| 2026-06-02 | Rework grafico | manter heroi 64x80 e exigir contorno escuro sem dither automatico | reduzir para 48x64 por medo de flicker foi recusado porque o perseguidor ataca pelo eixo Z | `data/processed/celestial_chase_v001/sprite_rework_outline_zaxis_v006/graphics_rework_candidates_report_v006.json` | aprovacao humana |
| 2026-06-02 | Perseguidor | substituir perfil lateral por frontal 3/4 e rig modular no near | full-body near e side-profile foram recusados por leitura de plataforma lateral e risco de scanline | `data/processed/celestial_chase_v001/sprite_rework_outline_zaxis_v006/chase_graphics_rework_approval_board_v006.png` | rig modular |
| 2026-06-02 | V006 rejeitada | marcar `User_Rejected_Heavy_Line_Art` e trocar para `Source_Baked_Pixel_Art_Standard` | continuar corrigindo edge/outline por algoritmo foi recusado por matar a alma do sprite | `data/processed/celestial_chase_v001/source_baked_pixel_art_candidates_v001/source_baked_pixel_art_standard_manifest.json` | gerar fonte nova |
| 2026-06-02 | Fonte source-baked | gerar novos conceitos do zero para heroi 64x80 e perseguidor 3/4 | converter v006 ou aplicar novo pos-processamento foi recusado | `data/processed/celestial_chase_v001/source_baked_pixel_art_candidates_v001/source_baked_pixel_art_approval_board_v001.png` | aprovacao humana |
| 2026-06-03 | Pixel-lock source-baked | gerar `pixel_lock_v002` com mascara exata e pose limpa do heroi | promover `pixel_lock_v001` foi recusado por crop contaminado no heroi | `data/processed/celestial_chase_v001/source_baked_pixel_art_candidates_v001/pixel_lock_v002/pixel_lock_report_v002.json` | aprovacao humana do pixel-lock |
| 2026-06-03 | Animacao source-baked | gerar `animation_strip_candidates_v003` com timing, pivots e rig modular | promover sprites estaticos para `res/` foi recusado sem aprovar movimento | `data/processed/celestial_chase_v001/source_baked_pixel_art_candidates_v001/animation_strip_candidates_v003/animation_strip_candidate_report_v003.json` | aprovacao humana da animacao |
| 2026-06-03 | Runtime source-baked v004 | promover todos os strips aprovados, mas compor a primeira ROM com heroi + boss body + dust e fundo leve de 258 tiles | sobrepor head/hoof na primeira ROM foi recusado porque duplicava anatomia no body e poluia a leitura; fundo split v007 ficou standby para nao estourar VRAM com `SPR_initEx(512)` | `doc/source_cases/chase_visual_benchmark/animation_asset_promotion_report_v004.md`, `out/logs/res_graph_report.json`, `out/rom.bin` | BlastEm fresco |
| 2026-06-03 | Validacao de movimento v005 | observar GIF runtime-like antes de aceitar a animacao runtime e substituir poeira estatica por burst independente | confiar apenas em screenshot BlastEm ou manter dust congelado em D3 foi recusado porque nao valida movimento | `data/processed/celestial_chase_v001/source_baked_pixel_art_candidates_v001/runtime_animation_validation_v005/chase_runtime_like_animation_observation_v005.gif`, `out/logs/runtime_metrics.json` | aprovacao humana do GIF |

---

## 5. ROTEIRO DE FECHAMENTO

- build/rebuild canonico: ok, build_v004 SHA256 `9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed`
- contratos recompilados: ok
- grafo de recursos: ok
- validator: ok com warnings de entrega visual/GDD
- captura BlastEm: ok, `target_scene_match=true`, SRAM fresca
- regressao de cena v011: `3/3` aprovada para menu, gameplay e resultado
- freshness audit: deve ser reexecutado apos a consolidacao documental v011
- closeout gate: tecnicamente apto em build/runtime/regressao/budget; blockers humanos/visuais permanecem

---

## 6. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
- Plano de provas QA: `doc/14-plano-de-provas-qa.md`

## 7. ADOCAO METODOLOGICA 2026-06-04

- `project_methodology_manifest.json` adotado com lifecycle `existing`.
- `critical_motion=required`; permanece bloqueado ate aprovacao humana formal, VDP dump e perceptual_check completo.
- `road_physics=required`; a v011 implementa lane model, estado Z compartilhado e deformacao da pista.
- `modular_boss=required`; a v011 implementa torso, cabeca e garras runtime independentes com FK e poda ativa.
- GIF de observacao migrado para dentro do projeto em `out/evidence/motion/chase_runtime_like_animation_observation_v005.gif`.
- `technique_usage_manifest.json` registra source-baked pixel art, GIF motion approval e perceptual motion gate sem promover nenhuma tecnica para `MESTRE_*`.
- `.mddev/project.json` referencia os manifests e o report metodologico; `freshness_audit` permanece obrigatorio.
- O blocker honesto do claim critico continua `perceptual_motion_unvalidated`; road physics e boss modular possuem contratos e evidencia tecnica.
- Preflight final: passou sem avisos.
- Metodologia final: bloqueada somente por `perceptual_motion_unvalidated`; screenshot dedicado e SRAM fresca existem, mas faltam aprovacao humana, quatro eixos perceptivos e VDP dump.
- Closeout permaneceu reprovado e `ready_for_aaa=false`; nenhuma evidencia ou status foi promovido artificialmente.

## 8. HIGIENE E SINCRONIZACAO DOCUMENTAL 2026-06-04

- Materializados sem sobrescrita: `doc/project_hygiene_manifest.json` e `rascunho/README.md`.
- `project_hygiene` foi adicionado as validacoes metodologicas obrigatorias.
- `validate_project_hygiene.ps1`: `passed`, zero blockers.
- `validate_project_methodology.ps1`: permanece `blocked` somente por `perceptual_motion_unvalidated`.
- Faltam os sinais ja conhecidos: aprovacao humana, quatro eixos perceptivos, screenshot dedicado, SRAM fresca e VDP dump.
- Nenhuma ROM foi rebuildada ou revalidada em BlastEm nesta alteracao.

### Closeout metodologico observado

- `validate_resources.ps1 -CloseoutGate`: `ready_for_aaa=false`.
- `project_hygiene_ready=true` e `technique_usage_ready=true`.
- Blockers vigentes: `perceptual_motion_unvalidated`, `gdd_substantial_insufficient`, `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`, `emulator_evidence_stale`, `freshness_audit_stale`, `scene_closeout_gate_stale`.
- `scene_contract_compile_report.json` permanece stale; nenhuma evidencia antiga foi tratada como atual.

## 9. ENCAPSULAMENTO DO LEGADO 2026-06-04

- O gate de higiene passou a bloquear `external_path_reference_outside_project` em codigo, scripts, manifestos e documentacao ativa.
- Material legado usado na construcao foi copiado sem apagar a origem:
  - source art: `rascunho/entrada_bruta/legacy_megadrive_dev/source_art/celestial_chase_v001`;
  - derivados historicos: `rascunho/processado/legacy_megadrive_dev/processed/celestial_chase_v001`;
  - scripts historicos: `rascunho/entrada_bruta/legacy_megadrive_dev/tools/image-tools`.
- Cada conjunto possui `_external_input_inventory.json` com inventario de arquivos e SHA-256; `doc/project_hygiene_manifest.json` registra origem, copia local, autorizacao e hash do inventario.
- `validate_project_hygiene.ps1` verificou os tres inventarios arquivo a arquivo, sem divergencias ou referencias externas ativas.
- `naming_policy=portable_descriptive_v1` foi materializada; todo material ativo passou no gate de nomes portateis e descritivos.
- Documentacao ativa deixou de apontar operacionalmente para o workspace legado; referencias foram migradas para caminhos locais do projeto.
- Logs historicos em `out/` foram preservados como historia e nao sao tratados como dependencia ativa.
- Preflight resolveu o toolchain canonico local em `sdk/sgdk-2.11/`, sem usar `GDK` herdado do workspace antigo.
- Nenhuma ROM foi rebuildada e nenhuma evidencia BlastEm foi promovida nesta migracao.

### Closeout apos encapsulamento

- `project_hygiene_ready=true`, `technique_usage_ready=true`, `ready_for_aaa=false`.
- Blockers vigentes: `perceptual_motion_unvalidated`, `gdd_substantial_insufficient`, `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`, `emulator_evidence_stale`, `freshness_audit_stale`, `scene_closeout_gate_stale`.











































































