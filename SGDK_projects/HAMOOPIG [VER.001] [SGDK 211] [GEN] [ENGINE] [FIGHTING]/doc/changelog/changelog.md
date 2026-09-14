# Changelog Canonico - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

## 2026-09-14 - plano de evolução para modelo de engine

- Registrado plano em `doc/engine/fighting_engine_improvement_plan.md` com 12 etapas,
  contratos de especial/combos/configuração, separação abertura→título, timing,
  HUD transparente, dois cenários e documentação de extensão.
- Criado `doc/engine/fighting_engine_roadmap.json` com dependências e eixos de
  evidência separados para agentes com e sem visão.
- Revisão de fontes/atlas e validação de contexto/higiene; sem alteração de C/assets/ROM
  e sem nova execução de emulador. Melhorias propostas continuam `planejado`.

## 2026-09-14 - tela de titulo e menu OPTION

- `gRoom==1` deixou de avançar automaticamente após dois segundos e agora possui menu persistente `START`/`OPTION`.
- `OPTION` alterna `SFX ON/OFF` e `MUSIC ON/OFF`, com `BACK`; as preferências permanecem durante a sessão e controlam `FUNCAO_PLAY_SND` e o BGM de combate.
- P1 usa D-pad, A/START e B; P2 não interfere no front-end. A fonte `message_font` é reutilizada em células 16×16 e o cursor custa um tile.
- Build SGDK 2.11/Wine aprovado: ROM `out/rom.bin`, 2.490.368 bytes, sha256 `b77300943f5739f34010a39f877afce716da1658bd0e7eef5d115e4584bc36d9`.
- Evidência visual/áudio do menu ainda deve ser capturada no BlastEm; teto permanece `prototype`.

## 2026-09-12 - correções persistentes HUD, cenário e Musgo

- Energia zero agora apaga as 16 colunas de cada barra e a atualização ocorre durante o congelamento de KO.
- Showdown usa a reconstrução do laboratório `_agent_training/[ESTUDO]_mugen_sff_showdown_v1/work/reconstructed_viewports/frame_0000_viewer_default.png`, 14 cores e 604 tiles; o mundo completo não deixa vazio no scroll.
- Musgo em estado 570 é ancorado no piso e reaproveita 550. O derivado de derrota foi quarentenado após `ADDRESS ERROR` no emulador.
- Texto pós-luta recebe PAL2, prioridade alta e espaçamento; fidelidade integral à fonte autorada continua pendente.
- ROM final desta iteração: `62df66bc9aa96d0e61d8b94742b2d14423e29b7a616a4df32ee27a1c68127827`. BlastEm 61.2 fps sem crash no percurso observado: `out/emulator_evidence/interactive-round-integrity-20260912T072145Z/`.

## 2026-09-12 - integridade de round e encerramento da partida

- Corrigida a cópia de paletas para slots CRAM de 16 cores, eliminando a escrita além de `palette[64]`; corrigidos também facing do especial P2 e uso de profundidade não inicializada.
- Removido o piso temporário de energia que impedia KO. Implementados melhor de três, empate por tempo sem ponto, reset integral em fase de commit (`gRoom==12`) e tela pós-luta (`gRoom==11`).
- `CLEAR_VDP` invalida handles liberados; chamadas sensíveis de sprite verificam `NULL`; reset cobre física, input, projéteis, sparks, HUD e relógio.
- A/START permanecem disponíveis no menu pós-luta mesmo com `gPodeMover==0`; START retorna ao seletor. A revanche existe no código, mas ainda não foi exercitada no emulador.
- ROM final: 2.490.368 bytes, sha256 `2a2ce843cebb1a756f460f0274b6b02b3ad3c9f5a796df41d7087d4f81cac559`. BlastEm 60.2 fps: `out/emulator_evidence/interactive-round-integrity-20260912T064603Z/` prova KO natural, reset, segunda vitória, pós-luta e retorno ao seletor.
- Time-over/empate e reset limpo foram observados no binário anterior à correção isolada do input pós-luta: `out/emulator_evidence/interactive-round-integrity-20260912T063457Z/`.
- Ícone solto movido para `rascunho/upstream_reference/hamoopig_icon.png`; validadores de contexto, higiene e metodologia sem blockers. Teto permanece `prototype`.

## 2026-09-11 - palco Showdown park + camera H/V

- GIF `xmen-vs-streetfighter-stage-showdown-at-the-park.gif` copiado para `data/source_art/showdown/` com `showdown.def`. Capcom XMvSF = estudo/placeholder (mesmo teto do Ken).
- Builder `convert_showdown.py`: 512x256, bloco 4px, 10 cores 9-bit, 444 unique tiles. `IMAGE gfx_showdown` em BG_B PAL0 (`compare_flat`). Unique nativo ~3191 nao cabe; 4 paletas ja ocupadas.
- Camera: H no ponto medio dos lutadores, clamp 0…192. V `camPosY = max(air)/2` clamp 0…32 (`verticalfollow 0.5` do `.def`). Rest `vscroll=32` (chao no viewport 224). Pulo revela ceu. Lutador/sombra/spark/fireball usam `+camPosY`.
- Parallax BG0/BG1/BG2/BG3 gravado em `doc/art/showdown/camera_motion_contract.json`, nao executado.
- ROM sha256 `1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6`. BlastEm 59.6 fps: `out/emulator_evidence/interactive-showdown-20260911T225648Z/` idle/walk H/jump V/hit. Prototype.
- Aprendizado: `doc/agent_learning/showdown_stage_lessons.md`. `canonical_promotion_performed=false`.

## 2026-09-11 - relogio no WINDOW

- Digitos `spr_n*` saiam do AUTO_VRAM com dois grappler. Agora `ts_hud_clock` (n0–n9, 160x16, index 0→11) no WINDOW rows 3-4, cols 18-21. `VDP_setWindowOnTop(5)`. `ClockL`/`ClockR` nao spawnam.
- ROM sha256 `a53bc06beba88ace362e8e4b226c5db0d22cb4a18a8c10cc7b818d11afec1561`. BlastEm 61.1 fps: `out/emulator_evidence/interactive-musgo-fight-20260911T221658Z/01_idle_hud.png` (98) e `06_hit.png` (89) com dois Musgos. Prototype.

## 2026-09-11 - barra P1 no WINDOW

- Dois Musgos no idle expulsavam o sprite 128px da barra P1 (`AUTO_VRAM`). P1 passou para o mesmo contrato da P2: `TILESET` NONE/NONE, `VDP_setWindowOnTop(2)`, PAL1 prio FALSE, index 0→11.
- `ts_hud_p1_bar` cols 1-16 (esvazia pela direita, rumo ao KO). `hud_window_load/init/update/off` dono das duas barras. GE[3]/GE[5] nao spawnam. Lag vermelho continua omitido.
- ROM sha256 `77ea0cdd2433881b16d515ef5dd7af0e2c48475c987dc75cefdc6ff61202f8bc`. BlastEm 60.3 fps: `out/emulator_evidence/interactive-musgo-fight-20260911T220349Z/01_idle_hud.png` — amarelas nos dois lados no idle. Prototype.

## 2026-09-11 - Musgo grappler original (id=3)

- Personagem autoral Musgo (monstro do pantano) entra no roster como `id==3`. A sheet CPS2 de grappler pesado foi ancora tecnica de massa/timing/cell, nao fonte de pixel nem IP.
- Concept + idle de perfil + ciclos video-first em `data/source_art/musgo/`. Converter `convert_musgo.py` gera strips 9-bit, index 0 magenta, idle 80x104 (maior que Ken 64x96), walk 88x104, slam 88x120, teto 128. Arte olha para a direita.
- Runtime: `PLAYER_STATE_MUSGO` / `inc/player_musgo_table.h` / `res/musgo.res`. Hitboxes case 3 (active no ultimo/unico quadro). Gravidade 550 igual ao Ken. Paletas PAL2/PAL3 via `FUNCAO_APPLY_FIGHTER_PALETTE`. MODE cicla Ryo->Ken->Musgo. Seletor LEFT/RIGHT pelos 3; default P2=Musgo. SFX reusa GPL HAMOOPI. 700 e slam, sem fireball.
- Claim: `source_candidate` / prototype. Nao e pixel nativo final nem AAA. Idle ~7-9 HW sprites / ~95-100 tiles por frame.
- ROM 2.490.368 B, sha256 `c81fee9f9f7b799f30514418f01ceeb8d293788c51b5b6c89fb4376964e98589`. Seletor observado no BlastEm: `out/emulator_evidence/blastem-linux-20260911T212135Z-1769103/screenshot.png` (P1 Ryo, P2 Musgo). Bundle canonico bloqueado sem VDP dump; luta ainda sem captura.
- Aprendizado local capturado: caderno `doc/agent_learning/musgo_roster_lessons.md`; ledger 57 licoes; `canonical_promotion_performed=false`. Capture nao editou `.agent`.
- Palco BlastEm 61.1 fps, mesma ROM: `out/emulator_evidence/interactive-musgo-fight-20260911T214421Z/` — P1/P2 Musgo, walk, jump aereo, jab com spark. P1 barra some no idle (AUTO_VRAM de 2x ~100 tiles); P2 WINDOW ok. Prototype.

## 2026-09-11 - barra P2 em WINDOW/tiles

- Sprite 128px da barra direita continuava sumindo (H40 320 px/scanline e/ou pool AUTO_VRAM 1532-1951). P2 amarela passou para o plano WINDOW.
- `VDP_setWindowOnTop(2)`, tiles depois do BG em `gInd_tileset`, PAL1 prio FALSE (sprites de P1/KO/relogio por cima). Faixa preenchida com index 11 (preto); tile 0 do PNG remapeado porque plano nao tem transparencia de sprite.
- GE[4]/GE[6] nao spawnam. Deplecao = colunas esquerdas da barra P2 trocadas pelo tile preto (`hud_frame_for`). `hud_p2_window_off()` no `CLEAR_VDP`.
- ROM sha256 `21f1654d076b072d5bdb5710994df0f45ef037be99268d77a533fc94845eb575`. Evidencia BlastEm 59.9 fps: `out/emulator_evidence/interactive-hud-p2-window-20260911T170914Z/00_hud_both.png` — barras amarelas nos dois lados + KO. Prototype, nao AAA.

## 2026-09-12 - orientações Discord para revisão futura da engine

- Lidos `#ff-rheo-bout` e 14 canais complementares do RETRODEVBR (histórico, exemplos e anexos).
- Registradas orientações atribuídas ao desenvolvedor original GameDevBoss/Daniel Moura e complementos comunitários, com autoria separada.
- Conteúdo consolidado em `doc/engine/discord_guidance_original_engine_review_2026-09-12.md`.
- Backlog definido: resolução/paleta, tilesets e tilemaps, `gInd_tileset`, `SPR_initEx`, fronteiras de VRAM, ciclos/camadas, áudio, animações, manuais e validação em BlastEm/Gens KMod/ClownMDEmu.
- Nenhum código, asset, ROM ou claim de entrega foi alterado.

## 2026-09-11 - sombra, queda Ken, HUD P2 ainda aberto

- Sombra: `sombra.png` usava indices da paleta antiga; PAL1 agora e HUD amarelo/vermelho, virava blob no chao. Pixels opacos remapeados para index 11 (preto da PAL1). VRAM da sombra em 1460 (fora do pool 1532-1951).
- Queda: Ken 550 nao setava `gravidadeY`/`impulsoY`; a fisica faz `impulsoY -= 1` e o lutador subia e sumia. Agora 550 inicia como o Ryo (`impulsoY=-14`, `gravidadeY=3`). Pulo Ken 300 ultimo quadro 99 (antes encerrava no ar).
- HUD: barra vermelha some com vida cheia (H40 320 px/scanline). P2 passou a ter strip espelhada (sem `SPR_setHFlip` no metasprite 128px). HUD spawna depois dos lutadores com AUTO_VRAM.
- Barra da direita **ainda nao aparece** na evidência (P1+KO sim). Proximo: encolher barras ou WINDOW/tiles.
- ROM sha256 `aa17b5b70507100ebb291dd83ae47e37e44d00973fa39f805ccdbaf170dbadbc`. Evidencia `out/emulator_evidence/interactive-hud-shadow-fall-20260911T163434Z/`. Prototype.

## 2026-09-11 - paleta no reset + hitbox/golpes do Ken

- Soft reset do emulador (BlastEm Tab = `ui.soft_reset`) nao zerava a RAM 68k: CRAM limpava, `gFrames`/`gRoom` sobreviviam, `FUNCAO_INICIALIZACAO` nao recarregava PAL2/PAL3. `int main(bool hardReset)` agora chama `SYS_hardReset()` quando `!hardReset` (SGDK 2.11 `sys.h` / sample platformer).
- Paletas da luta passam por `FUNCAO_APPLY_FIGHTER_PALETTE` em vez dos `if` duplicados.
- Ken (`id==2`) nao tinha `case` em `FUNCAO_FSM_HITBOXES`: sem hurtbox nem hitbox. Case 2 alinhado aos strips curtos (`101`/`104` 1 quadro, `102`/`106`/`151` 2, `105` 3). Close 152/154/155 aliasam 102/104/105. Jab/kick 1 quadro held em 8 frames.
- ROM 1.966.080 B, sha256 `c0a084e4a3340d1086b89bad6225641cd0a14d1c170b4f69e53f9888fae38168`.
- Evidencia BlastEm 59.8 fps: `out/emulator_evidence/interactive-ken-hit-reset-20260911T155121Z/` — `05_ken_attack.png` chute do Ken com spark; `07_after_soft_reset.png` title fade apos Tab; `11_fight_after_reset.png` Ryo+Ken paletas corretas apos reset. Prototype.

## 2026-09-11 - Ken frente, HUD SF, seletor

- Ken: a sheet arcade olha para a esquerda; cada frame foi `FLIP_LEFT_RIGHT` no converter para o padrao HAMOOPIG (Ryo olha para a direita). P1 Ken passa a encarar o oponente.
- HUD: sheet SF (shezzor) fatiada em barra amarela (`energiaBase`), vermelha (`energia` atrasada) 128x16 / 13 frames, e KO 48x24. Spawn em GE[3..7] com VRAM fixa 1600+. P2 usa HFlip. `res/hud_gfx.res`.
- Seletor: `gRoom==2` depois do title. Esquerda/direita troca Ryo/Ken, A confirma, Start do P1 fecha P2 com a escolha atual. Defaults P1=Ryo P2=Ken.
- palID 0 nao carregava paleta do lutador (CRAM lixo / verde-azul). Select agora grava `cursorP*ColorChoice`; init trata 0 como pal1.
- ROM 1.966.080 B, sha256 `ff1c205b9d574c5e2af3c4b372e3326563a58eb0bb3a4521dbe8a8ac7cbecac4`.
- Evidencia: `out/emulator_evidence/interactive-hud-select-20260911T151757Z/` (select + barras/KO). FPS nesta cena ~41–55. Prototype.



## 2026-09-11 - Ken arcade nativo + BGM Ken Stage + MODE

- Personagem Ken incluido a partir da sheet arcade `ken_arcade_st_v1.png` (1549x11279, sha256 `23ae9176...`), copiada para `data/source_art/ken_arcade/`. Sem o shrink 32x64 do MSSF2T SMS. Idle 64x96, especiais ate 128x128, paleta compartilhada 15 cores 9-bit, magenta index 0. Builder `convert_ken_arcade.py`; `res/ken.res` 116 KB packed.
- Runtime: `P[].id==2` via `PLAYER_STATE_KEN` / `ken_anim_for()`; especiais QCF/DP do Ryo tambem no Ken; sem fireball `spr_ryo_701` para id==2; SFX reusa GPL do HAMOOPI.
- MODE/SELECT: `JOY_MODE` sozinho em gRoom==10 cicla Ryo<->Ken no pad; MODE+START permanece debug. BlastEm default.cfg: tecla `f` = pad1 MODE.
- Musica: MIDI vgmusic Ken Stage (30751 B, sha256 `44804801...`) transcrito para VGM NTSC 9333 B (YM2612 3ch + PSG noise, 16 compassos @ 90 BPM, sem PCM). `XGM bgm_ken_stage` no driver XGM1 ja usado pelo projeto.
- ROM: 1.441.792 B, sha256 `62befee38c53603c166f3eb1703be47b308320eb91e163dc1f01e5ef13971f7a`.
- Evidencia BlastEm: `out/emulator_evidence/interactive-ken-mode-20260911T144506Z/` — screenshot Ken apos MODE, ~60 fps. Audio disk nao-silencioso em `...144351Z/audio.raw`. Relogio HUD pode sumir apos o spawn do Ken (AUTO_VRAM_ALLOC vs indices fixos).
- Aprendizado local: `rascunho/ken_integration_technical_conditions.json`. `canonical_promotion_performed=false`. Teto prototype; sheet/MIDI Capcom/vgmusic nao sustentam claim comercial.

## 2026-09-10T17:11:35.6659733Z - bootstrap

- projeto criado a partir da estrutura canonica
- historico de ROM, hashes e evidencia do modelo removido
- status inicial: documentado; nao buildado; nao testado em emulador
- proximo gate: classificar contexto e metodologia

## 2026-09-10 - porta SGDK 2.11 (porta direta de SGDK_Engines/HAMOOPIG-SGDK)

- materializado `new_project.sh` (estrutura canonica completa) e classificado como `technical_demo` com ceiling `prototype`
- copiados 11 .c (src/) e 11 .h (inc/) do upstream, byte-idempotentes (verificados com cmp)
- `res.zip` upstream extraido para res/ (70 pngs; gfx.res/sprite.res/sound.res) sem junk e sem headers gerados
- sound.res upstream vazio substituido por placeholder: 17 PCM silenciosos XGM 800 amostras @16kHz (player.c/fsm.c/main.c exigem os simbolos snd_*); registro em rascunho/upstream_reference/sound_placeholder_manifest.json
- fix_migration_issues.ps1: 10 reescritas aplicadas; 8 revertidas como falso-positivo (sprite.h/sound.h aqui sao headers de RECURSO rescomp, nao de engine); mantidas VDP_showFPS_1to3 e SPR_init_args_to_void
- material upstream de referencia (README, docs, Makefile, Doxyfile, CI, web, res.zip) arquivado em rascunho/upstream_reference/
- Makefile Docker upstream nao portado: build passa a ser tools/sgdk_wrapper/build.sh (SDK sdk/sgdk-2.11)
- build: rota Wine flatpak → out/rom.bin 917.504 bytes, wine_bridge_status=buildado
- boot BlastEm 0.6.2 NTSC via wrapper canonico de captura: arena de luta a 60 fps (evidencia em out/emulator_evidence/blastem-linux-20260910T192043Z-1434440/ — screenshot, save.sram, log, session_runtime)
- status: buildado e bootado em emulador (boot only; input nao exercitado; audio placeholder declarado)

## 2026-09-10 (2) - header de ROM real + gameplay basico provado

- src/boot/rom_head.c: domestic/overseas "(HAMOOPI MD PORT BY HUMBERTODIAS)" e copyright "(C)GAMEDEVBOSS26" (antes SAMPLE PROGRAM); rebuild limpo (ROM sha256 558bea6c...)
- sessao interativa de input (out/emulator_evidence/interactive-20260910T195804Z/): xdotool -> gamepad 1; P1 anda com scroll de camera, golpes A/B animam, 60 fps sustentados; manifest com sequencia de inputs e limites de claim
- status: gameplay basico provido (movimento/golpe/camera); dano/HUD, fim de round e audio continuam nao provados

## 2026-09-11 - complementar o que o res.zip nao trazia

- PCM: placeholders silenciosos substituidos por WAV GPL do HAMOOPI (Daniel Moura), 16 kHz 16-bit mono, mapeados aos 17 `snd_*`; `FUNCAO_PLAY_SND` descomentado para P1/P2 id=1; `Z80_loadDriver(Z80_DRIVER_XGM)` no boot
- HUD relogio: `spr_n0..n9` convertidos de `system/spr_num_*.pcx`, remapeados a PAL1 16x16; `FUNCAO_RELOGIO` ligado com `SPR_releaseSprite` NULL-safe e spawn inicial 99
- sombra: `spr_sombra` 64x16 composto do frame de `ryo/100.png`; spawn em `FUNCAO_INICIALIZACAO` e follow em `FUNCAO_SPR_POSITION`
- docs: README e visao-geral deixam de ser o template; engine docs copiados para `doc/engine/`
- barras de energia GE[3..6] continuam sem sprite de HUD (codigo ja no-op se GE.sprite e NULL)
- rebuild Wine 2026-09-11: `out/rom.bin` 917.504 bytes, sha256 `6e5e846e7bc3f8393ba7b9e26639fe5806ebb95101252e76b8551ad521b40ca9`; sound.res 160 KB PCM XGM
- captura BlastEm 2026-09-11 (`out/emulator_evidence/blastem-linux-20260911T140738Z-109961/`): screenshot com relogio `99` e sombra no chao, 60.0 fps no titulo; bundle AAA rejeitado por VDP dump ausente; audio_driver=dummy nesta rota
- status: buildado + boot observado na ROM nova; audio nao provado por escuta (driver dummy)


## Curadoria local — 2026-09-11

Analise registrada em `doc/curation/2026_09_11/curadoria_hamoopig.md`. Confirmados estaticamente: copia de paleta ultrapassa palette[64] por 4 bytes; facing de especial P2 compara x consigo; round restart vazio. Prioridade: integridade, round completo e provas simetricas antes de ampliar roster. Contexto planning passou; higiene bloqueada pelo icone da raiz. Nenhum C/asset/ROM alterado, nenhuma nova execucao BlastEm, nenhuma promocao canonica. ROM preservada: `1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6`.
## 2026-09-12T09:18:42.3760666-03:00 - Correção da animação final de derrota do Musgo

## 2026-09-14 - P00/P01/P02 executados

- P00: vinculo fonte->ROM PROVADO. Rebuild a partir de artefatos limpos deu ROM
  bit-identica (`e2ca5833...be0f4`); o build e deterministico. Ressalva:
  `library_rebuild=false`, entao vale para as fontes do projeto, nao para a cadeia toda.
- P00: decoder HPRB endurecido. Quatro defeitos, tres produzindo FALSO VERDE --
  bloco truncado, par schema/size cruzado e `samples==0` eram aceitos com
  `decision='cabe'`. Agora ha `--self-check` com fixtures positivas e negativas.
- P01: `inc/timing.h`/`src/timing.c`. Logica passa a 60 ticks/s nas DUAS regioes
  (PAL alterna 1,1,1,1,2). Antes PAL rodava 17% mais lento. Relogio de round
  passou de 38 para 60 ticks por unidade: uma unidade agora e um segundo real.
- P01: o modo `TICK 50` era o defeito oferecido como opcao; virou perfil LEGACY,
  explicitamente de diagnostico.
- P01: o pico de DMA de 8448 B contra envelope NTSC de 7782 NAO e frame de combate.
  E o frame de CARGA da cena, dominado pelo tilemap 512x256 de `FUNCAO_INICIALIZACAO`.
  Confirmado nas duas regioes (frames 271 e 226, razao 1,199 = 1,2).
- P02: `inc/scene.h`/`src/scene.c`. As 8 trocas de cena migraram para
  `SCENE_request`/`SCENE_commit`; a convencao posicional de `gFrames=0/1` morreu.
- P02: abertura virou cena propria (`opening.c`), com fade in/hold/fade out. Os
  creditos agora aparecem inteiros, em vez de ficarem atras do painel do menu.
- P02: corrigido painel de titulo sem letras -- `PAL_fadeIn` levava PAL1 a preto
  porque `palette[]` nao continha as quatro paletas.
- Pendente e declarado: arte propria do titulo sem creditos embutidos; revisao de
  suavidade dos fades; harness de replay deterministico.


- Task: Correção da animação final de derrota do Musgo
- Asset snapshots:
  - room_0_bga -> v001 (/res/gfx/room_0_bga.png)
  - room_0_bgb -> v001 (/res/gfx/room_0_bgb.png)
  - gfx_bgb1 -> v001 (/res/gfx/bgb1.png)
  - gfx_bgb2 -> v001 (/res/gfx/bgb2.png)
  - gfx_showdown -> v001 (/res/gfx/showdown.png)
  - spr_hud_energy_y -> v001 (/res/sprite/hud/energy_yellow.png)
  - spr_hud_energy_r -> v001 (/res/sprite/hud/energy_red.png)
  - spr_hud_energy_y_p2 -> v001 (/res/sprite/hud/energy_yellow_p2.png)
  - spr_hud_energy_r_p2 -> v001 (/res/sprite/hud/energy_red_p2.png)
  - spr_hud_ko -> v001 (/res/sprite/hud/ko.png)
  - ts_hud_p1_bar -> v001 (/res/sprite/hud/energy_yellow_p1_window.png)
  - ts_hud_p2_bar -> v001 (/res/sprite/hud/energy_yellow_p2_window.png)
  - ts_hud_clock -> v001 (/res/sprite/hud/clock_digits_window.png)
  - spr_ken_pal1 -> v001 (/res/sprite/ken/palettes/pal1.png)
  - spr_ken_pal2 -> v001 (/res/sprite/ken/palettes/pal2.png)
  - spr_ken_100 -> v001 (/res/sprite/ken/100.png)
  - spr_ken_101 -> v001 (/res/sprite/ken/101.png)
  - spr_ken_102 -> v001 (/res/sprite/ken/102.png)
  - spr_ken_104 -> v001 (/res/sprite/ken/104.png)
  - spr_ken_105 -> v001 (/res/sprite/ken/105.png)
  - spr_ken_106 -> v001 (/res/sprite/ken/106.png)
  - spr_ken_151 -> v001 (/res/sprite/ken/151.png)
  - spr_ken_200 -> v001 (/res/sprite/ken/200.png)
  - spr_ken_201 -> v001 (/res/sprite/ken/201.png)
  - spr_ken_300 -> v001 (/res/sprite/ken/300.png)
  - spr_ken_420 -> v001 (/res/sprite/ken/420.png)
  - spr_ken_501 -> v001 (/res/sprite/ken/501.png)
  - spr_ken_550 -> v001 (/res/sprite/ken/550.png)
  - spr_ken_606 -> v001 (/res/sprite/ken/606.png)
  - spr_ken_700 -> v001 (/res/sprite/ken/700.png)
  - spr_ken_710 -> v001 (/res/sprite/ken/710.png)
  - spr_ken_720 -> v001 (/res/sprite/ken/720.png)
  - spr_ken_730 -> v001 (/res/sprite/ken/730.png)
  - spr_musgo_pal1 -> v001 (/res/sprite/musgo/palettes/pal1.png)
  - spr_musgo_pal2 -> v001 (/res/sprite/musgo/palettes/pal2.png)
  - spr_musgo_100 -> v001 (/res/sprite/musgo/100.png)
  - spr_musgo_101 -> v001 (/res/sprite/musgo/101.png)
  - spr_musgo_102 -> v001 (/res/sprite/musgo/102.png)
  - spr_musgo_104 -> v001 (/res/sprite/musgo/104.png)
  - spr_musgo_105 -> v001 (/res/sprite/musgo/105.png)
  - spr_musgo_106 -> v001 (/res/sprite/musgo/106.png)
  - spr_musgo_151 -> v001 (/res/sprite/musgo/151.png)
  - spr_musgo_200 -> v001 (/res/sprite/musgo/200.png)
  - spr_musgo_201 -> v001 (/res/sprite/musgo/201.png)
  - spr_musgo_300 -> v001 (/res/sprite/musgo/300.png)
  - spr_musgo_420 -> v001 (/res/sprite/musgo/420.png)
  - spr_musgo_501 -> v001 (/res/sprite/musgo/501.png)
  - spr_musgo_550 -> v001 (/res/sprite/musgo/550.png)
  - spr_musgo_606 -> v001 (/res/sprite/musgo/606.png)
  - spr_musgo_700 -> v001 (/res/sprite/musgo/700.png)
  - spr_musgo_710 -> v001 (/res/sprite/musgo/710.png)
  - spr_musgo_720 -> v001 (/res/sprite/musgo/720.png)
  - spr_musgo_730 -> v001 (/res/sprite/musgo/730.png)
  - spr_point -> v001 (/res/sprite/point.png)
  - spr_rect_bb -> v001 (/res/sprite/spr_rect_bb.png)
  - spr_rect_hb -> v001 (/res/sprite/spr_rect_hb.png)
  - spr_spark0 -> v001 (/res/sprite/spr_spark0.png)
  - spr_spark1 -> v001 (/res/sprite/spr_spark1.png)
  - spr_spark2 -> v001 (/res/sprite/spr_spark2.png)
  - spr_spark3 -> v001 (/res/sprite/spr_spark3.png)
  - spr_n0 -> v001 (/res/sprite/hud/n0.png)
  - spr_n1 -> v001 (/res/sprite/hud/n1.png)
  - spr_n2 -> v001 (/res/sprite/hud/n2.png)
  - spr_n3 -> v001 (/res/sprite/hud/n3.png)
  - spr_n4 -> v001 (/res/sprite/hud/n4.png)
  - spr_n5 -> v001 (/res/sprite/hud/n5.png)
  - spr_n6 -> v001 (/res/sprite/hud/n6.png)
  - spr_n7 -> v001 (/res/sprite/hud/n7.png)
  - spr_n8 -> v001 (/res/sprite/hud/n8.png)
  - spr_n9 -> v001 (/res/sprite/hud/n9.png)
  - spr_sombra -> v001 (/res/sprite/hud/sombra.png)
  - spr_ryo_pal1 -> v001 (/res/sprite/ryo/palettes/pal1.png)
  - spr_ryo_pal2 -> v001 (/res/sprite/ryo/palettes/pal2.png)
  - spr_ryo_000 -> v001 (/res/sprite/ryo/000.png)
  - spr_ryo_100 -> v001 (/res/sprite/ryo/100.png)
  - spr_ryo_101 -> v001 (/res/sprite/ryo/101.png)
  - spr_ryo_102 -> v001 (/res/sprite/ryo/102.png)
  - spr_ryo_103 -> v001 (/res/sprite/ryo/103.png)
  - spr_ryo_104 -> v001 (/res/sprite/ryo/104.png)
  - spr_ryo_105 -> v001 (/res/sprite/ryo/105.png)
  - spr_ryo_106 -> v001 (/res/sprite/ryo/106.png)
  - spr_ryo_107 -> v001 (/res/sprite/ryo/107.png)
  - spr_ryo_108 -> v001 (/res/sprite/ryo/108.png)
  - spr_ryo_113 -> v001 (/res/sprite/ryo/113.png)
  - spr_ryo_151 -> v001 (/res/sprite/ryo/151.png)
  - spr_ryo_152 -> v001 (/res/sprite/ryo/152.png)
  - spr_ryo_154 -> v001 (/res/sprite/ryo/154.png)
  - spr_ryo_155 -> v001 (/res/sprite/ryo/155.png)
  - spr_ryo_200 -> v001 (/res/sprite/ryo/200.png)
  - spr_ryo_201 -> v001 (/res/sprite/ryo/201.png)
  - spr_ryo_202 -> v001 (/res/sprite/ryo/202.png)
  - spr_ryo_204 -> v001 (/res/sprite/ryo/204.png)
  - spr_ryo_205 -> v001 (/res/sprite/ryo/205.png)
  - spr_ryo_207 -> v001 (/res/sprite/ryo/207.png)
  - spr_ryo_208 -> v001 (/res/sprite/ryo/208.png)
  - spr_ryo_300 -> v001 (/res/sprite/ryo/300.png)
  - spr_ryo_301 -> v001 (/res/sprite/ryo/301.png)
  - spr_ryo_302 -> v001 (/res/sprite/ryo/302.png)
  - spr_ryo_304 -> v001 (/res/sprite/ryo/304.png)
  - spr_ryo_306 -> v001 (/res/sprite/ryo/306.png)
  - spr_ryo_310 -> v001 (/res/sprite/ryo/310.png)
  - spr_ryo_320 -> v001 (/res/sprite/ryo/320.png)
  - spr_ryo_324 -> v001 (/res/sprite/ryo/324.png)
  - spr_ryo_325 -> v001 (/res/sprite/ryo/325.png)
  - spr_ryo_410 -> v001 (/res/sprite/ryo/410.png)
  - spr_ryo_420 -> v001 (/res/sprite/ryo/420.png)
  - spr_ryo_471 -> v001 (/res/sprite/ryo/471.png)
  - spr_ryo_472 -> v001 (/res/sprite/ryo/472.png)
  - spr_ryo_501 -> v001 (/res/sprite/ryo/501.png)
  - spr_ryo_502 -> v001 (/res/sprite/ryo/502.png)
  - spr_ryo_503 -> v001 (/res/sprite/ryo/503.png)
  - spr_ryo_550 -> v001 (/res/sprite/ryo/550.png)
  - spr_ryo_551 -> v001 (/res/sprite/ryo/551.png)
  - spr_ryo_552 -> v001 (/res/sprite/ryo/552.png)
  - spr_ryo_570 -> v001 (/res/sprite/ryo/570.png)
  - spr_ryo_606 -> v001 (/res/sprite/ryo/606.png)
  - spr_ryo_607 -> v001 (/res/sprite/ryo/607.png)
  - spr_ryo_608 -> v001 (/res/sprite/ryo/608.png)
  - spr_ryo_611 -> v001 (/res/sprite/ryo/611.png)
  - spr_ryo_612 -> v001 (/res/sprite/ryo/612.png)
  - spr_ryo_615 -> v001 (/res/sprite/ryo/615.png)
  - spr_ryo_700 -> v001 (/res/sprite/ryo/700.png)
  - spr_ryo_701 -> v001 (/res/sprite/ryo/701.png)
  - spr_ryo_702 -> v001 (/res/sprite/ryo/702.png)
  - spr_ryo_710 -> v001 (/res/sprite/ryo/710.png)
  - spr_ryo_730 -> v001 (/res/sprite/ryo/730.png)
- ROM: build_v001 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Estado 570 agora mantém o último frame autoral após a queda; build SGDK 2.11 concluído e o bundle antigo foi invalidado até nova captura.

## 2026-09-12T09:45:48.0720148-03:00 - Registro da correção terminal do KO do Musgo

- Task: Registro da correção terminal do KO do Musgo
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Estado 570 segura o último frame; build 363774d9 validado. Captura canônica recente bloqueada por framebuffer preto e ausência de probes VDP/runtime.

## 2026-09-12T09:54:10.1645136-03:00 - Captura canônica pós-correção do capturador

- Task: Captura canônica pós-correção do capturador
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: windowactivate adicionado ao capturador; screenshot agora legível em blastem-linux-20260912T125335Z-2562833. Gates ainda bloqueiam por VLAB/VDP dump/runtime metrics.

## 2026-09-12T09:55:43.5627911-03:00 - Fechamento da iteração P0 KO e captura

- Task: Fechamento da iteração P0 KO e captura
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f, 2490368 bytes)
- Validation: errors=1, warnings=11
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Build 2.11 exit 0; ROM 363774d9. Estado 570 terminal corrigido. Captura canônica legível e gate semântico passou; VLAB/VDP/runtime continuam pendentes.

## 2026-09-12 - Experimento de residência Showdown 2x2 revertido

- `BLOCK=2` (1.393 tiles) com `SPR_initEx(320)` foi executado e capturado em
  `out/emulator_evidence/interactive-round-integrity-20260912T132630Z/`.
- Resultado: corrupção de HUD, mapa e sprites por sobreposição da região de
  VRAM automática; variante rejeitada.
- Configuração restaurada: `BLOCK=4` + `SPR_init()`, ROM estável
  `363774d9592ec5e4e9dce133063ed013243601800a30ca6a78b0d8be61a5347f`.

## 2026-09-12 - Blindagem de KO/HUD

- `hud_window_update()` invalida o cache de frame quando `energiaBase<=0`,
  forçando a reescrita das 16 colunas pretas de P1 e P2.
- `FUNCAO_UPDATE_LIFESP()` zera `energia` junto com `energiaBase` no dano letal,
  evitando residual do medidor atrasado na troca de round.
- Build e captura dedicada de KO ainda são necessários para promoção.

## 2026-09-12 - Revisao visual/KO com provas novas

- ROM vigente: `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953`, 2490368 bytes; wrapper canonico exit 0, log `out/logs/visual_ko_verified_build.log`.
- Recortes de barras/KO corrigidos; alfabeto do atlas solicitado em PAL1 e mapa BG_A enviado no VBlank. Painel compacto deixa a pose de vitoria visivel.
- Supersede Blindagem acima: cache nao e invalidado continuamente, e residual sobrevivendo ao reset nao foi confirmado. Zero preenche 16 colunas uma vez. EnergyType 2 nao relanca o derrotado.
- Novas poses Musgo: queda, derrota deitada, vitoria; espera pelo pouso antes de proximo round. Fonte/prompt ImageGen persistidos com proveniencia source_candidate.
- Showdown sem ampliacao 4x4: 768 tiles representantes; indice 0 reservado para impedir buracos pretos no chao. Primeiro tile livre 1018, sprite region 1020. Degrau 832 rejeitado estaticamente.
- Testes host de vida/HUD e paleta/hash passaram. Sessoes finais Ken x Musgo e Musgo x Musgo mostram dois KOs, reset e revanche. Videos sem audio; sem certificacao de pior budget/PAL/P2 vencedor.
- Nove licoes JSON locais e fechamento em `doc/curation/2026_09_12/visual_ko_closeout.md`; framework canonico nao promovido.

## 2026-09-13 - QA simetrico, PAL, time-over e audio isolado

- ROM 532d4453 preservada, sem rebuild ou mudanca de C/assets.
- P2 vence e START retorna ao seletor em NTSC e PAL; DRAW e vencedor por tempo com vida desigual observados, seguidos por reset.
- Capturador recebe controles P2, regiao PAL, entrada de luta verificada, dano observado antes do time-over, configuracao e SRAM locais por sessao.
- Audio: corrigido roteamento do host para sink isolado; captura com sinal e sem clipping digital. Auditor PCM com self-check; silencio/rota ausente retorna erro. Audicao e SFX dedicados permanecem pendentes.
- Regressao nova do bloco C real de time-over: 9.216 pares de vida e idempotencia da pontuacao; testes anteriores de vida/paleta continuam passando.
- Finalizador canonico sela identidade/integridade de arquivos da ROM; nao promove pior budget, FPS do loop, VLAB/VDP/runtime ou AAA.
- Fechamento `doc/curation/2026_09_13/qa_continuation_closeout.md`, licoes locais `test_harness_lessons.json`; nenhuma promocao canonica.

## 2026-09-13 - Especiais antes/depois do reset

- Captura vinculada à ROM `532d44539809e40ad3ae8150532f27c91d7f638ee12d6b194cd53897f294a953` em `out/emulator_evidence/visual_ko_20260913T230125Z/`.
- Sequência de baixo/frente+golpe foi observada nos dois jogadores antes e depois do reset; Ryo emitiu `spr_ryo_701` e Musgo executou `spr_musgo_700`.
- O capturador passou a manter 24 quadros por tentativa para alcançar o frame de emissão do projétil. Resultado é evidência exploratória, sem promoção de budget ou áudio.

## 2026-09-13 - Sonda HPRB de VDP/DMA/SAT

- Adicionada sonda diagnóstica opt-in no loop, após `SPR_update()` e antes do VBlank; SRAM HPRB registra DMA pendente, sprites ativos, links VDP, pico por scanline e amostras.
- Build SGDK 2.11: ROM `ae6f5dab51c6c50b9e5ad94315f2bf8d89dcedfef724b83f6ab41277c59c1a62`.
- BlastEm observou DMA máximo 10.064 B (acima do envelope NTSC ~7.782 B), 58 links VDP e 12 sprites/scanline. Decisão `cabe com recuo`; reduzir/parcelar uploads é o próximo trabalho.
- Decoder e laudo em `rascunho/temporario/analyze_hprb_probe.py` e `doc/curation/2026_09_13/vdp_probe_closeout.md`. Selo final rejeitado por captura preta precoce; o resultado não promove performance.
- Janela PAL curta na mesma ROM mediu DMA máximo 7.984 B, 38 links VDP e 8 sprites/scanline; PAL cabe no envelope, mantendo o recuo apenas para NTSC.
- Plano aberto em `doc/curation/2026_09_14/dma_reduction_plan.md`: atribuir o frame de pico, separar preload e reduzir uploads de frame único/janela ativa; truncar a fila foi explicitamente rejeitado.
- HPRB v2 localizou o pico NTSC: frame 3480 (DMA 10.064 B) e pico de scanline no frame 3158. PAL na mesma ROM permaneceu em 7.984 B; a redução deve focar o trecho NTSC de combate/efeito.

## 2026-09-14 - Experimento DMA do efeito forte

- Variante de laboratório `HAMOOPIG_DMA_LAB_REDUCED=1` trocou apenas `spr_spark3` por `spr_spark2` no `SparkType==3`; ROM `91591dac…` buildou.
- HPRB parcial manteve o pico em 10.064 B (frame 4.469), acima do envelope NTSC; impacto visual menor. Hipótese rejeitada e binário oficial voltou a `ae6f5dab…`. Próximo passo: atribuição por componente no frame de pico, não redução cega de FX.

## 2026-09-14 - Atribuição HPRB v3

- Instrumentação em torno de `SPR_update()` mostrou 7.176 B de delta máximo
  de sprites e 5.536 B já pendentes antes da atualização, com total de 10.064 B.
- A medição confirma sprites como ramo dominante; plano passa a priorizar
  preload/janela ativa de frames. ROM diagnóstica `8544c31d…`, sem promoção de
  budget ou alteração da lógica de combate.

## 2026-09-14 - Laboratório de reuso de estado

- Reentrada no mesmo estado de `PLAYER_STATE()` reduziu o delta de sprites de
  7.176 B para 6.408 B, sem regressão visual observada.
- O pico total permaneceu 10.064 B; variante não promoveu e o macro foi
  restaurado. Próximo alvo é a fila prévia/preload de frames.

## 2026-09-14 - Backpressure nativo não acionado

- Variante sem `SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE` manteve o mesmo pico
  10.064 B; `DMA_getMaxTransferSize()` está sem teto efetivo nesta rota.
- Hipótese rejeitada, macro restaurado e backlog de uploads continua o alvo.

## 2026-09-14 - Ritmo neutro não reduz pico

- Alongar idle/crouch/walk em 2× não alterou o pico DMA de 10.064 B; ataques
  e transições são o alvo real. Macro restaurado, sem promoção.

## 2026-09-14 - HPRB v5: atribuição no frame crítico

- No frame 4.469, 10.064 B = 4.576 B de backlog prévio + 5.488 B de
  `SPR_update()`. Mensagem HUD mediu 480 B; o restante é backlog de sprites.
- ROM diagnóstica `e91823b7…`; links 54 e 9 sprites/scanline. O próximo ciclo
  deve reduzir uploads de animação entre frames, sem truncar a fila.

## 2026-09-14 - Life bar compacta orientada pelo Rheo

- Investigação registrada em `doc/curation/2026_09_13/discord_life_bar_multiplex.md`.
- Barras migradas do WINDOW para células fixas 16×8 (`energy_yellow_segment.png`), oito por jogador; vazios são ocultados e o cenário permanece visível atrás do HUD.
- O primeiro recorte tinha amarelo no índice 0 e produziu quadriculação; o asset foi corrigido para índice 0 transparente e índice 2 amarelo, conforme a PAL1 do HUD.
- Build wine bridge passou; ROM final `f001418a654fc0aaf4a3c53cc4eb9f62470ac0f747c0dd2b3ba2b0c86453ec0b`. Captura de combate `visual_ko_20260914T030007Z` e HPRB `hprb_probe_report_20260914_life_bar_final.json`.
- HPRB da sessão curta: 5.688 B DMA, 17 links VDP, 5 sprites/scanline; resultado dentro do envelope da amostra, sem promoção de `validado_budget` global.
## 2026-09-14 - Transição splash → menu

- `gRoom==1` mantém a abertura HAMOOPIG íntegra durante 120 frames; entrada
  inicial apenas pula o splash e não dispara `START` no mesmo frame.
- O menu restaura o tilemap original antes de desenhar o painel estreito,
  evitando DMA/fade concorrente e a corrupção visual observada na transição.
- Evidência manual BlastEm: `out/emulator_evidence/title-transition-final-20260914/`.
- ROM: `68baca0e2845a00d057e0d8b892102247f5674350194dcf8509b07e895734d7d`.
