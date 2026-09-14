<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-09-12T09:55:43.5627911-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 126
- Ultimo build versionado: build_v002
- ROM vigente (build HUD compacto): `f001418a654fc0aaf4a3c53cc4eb9f62470ac0f747c0dd2b3ba2b0c86453ec0b` (`2490368` bytes). O resumo de validation_report abaixo e historico, anterior a esta ROM; nao certifica a revisao visual.
- Validation summary: errors=1 warnings=11
- Blockers vigentes: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, changelog_missing, code_loaded_tiles_unmeasured, technique_usage_manifest_empty, scene_tilemap_conversion_report_missing, per_tile_palette_conflict_report_missing, freshness_audit_missing, scene_closeout_gate_missing
- Evidencia de emulador: sem_sessao
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=nao_testado performance=unproven audio=nao_testado hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

**Ultima atualizacao:** 2026-09-13
**Fase atual:** revisao visual/KO exercitada nos dois lados, NTSC/PAL; empate, vencedor por tempo e especiais após reset observados — prototype
**Proxima fase:** reduzir/parcelar uploads de sprites no pior quadro NTSC com janela ativa/preload, depois repetir HPRB NTSC/PAL; audicao/SFX e regressao PAL dos especiais continuam pendentes.
**Aprendizado:** cadernos `doc/agent_learning/musgo_roster_lessons.md` e `doc/agent_learning/showdown_stage_lessons.md`; Capture local 2026-09-11; `canonical_promotion_performed=false`

## 1. Origem e proveniencia

- Engine origem: `SGDK_Engines/HAMOOPIG-SGDK` (origem upstream `https://github.com/humbertodias/sgdk-HAMOOPIG`, commit f90c0c4).
- HAMOOPIG e a implementacao da engine HAMOOPI (by GameDevBoss / Daniel Moura, 2015-2022) para Mega Drive.
- **Creditos obrigatorios a GameDevBoss (Daniel Moura)** — exigencia do cabecalho de `src/main.c` upstream. Sem license formal; header declara "HAMOOPIG IS FREE AND ALWAYS WILL BE".
- Copia de referencia do material upstream (nao-fonte) em `rascunho/upstream_reference/` com hashes em `imported_assets_sha256.json`.
- A importacao original continha 22 arquivos upstream. O projeto atual e uma porta estendida com alteracoes em runtime, HUD, selecao, lutadores e ciclo de round; nao e mais byte-idempotente.

## 2. Estado operacional

- portado: sim (src/inc/res do upstream materializados)
- documentado: sim (este projeto)
- implementado: sim (codigo upstream existe e foi portado)
- buildado: **sim (2026-09-14)** — `out/rom.bin` sha256 `b77300943f5739f34010a39f877afce716da1658bd0e7eef5d115e4584bc36d9`, 2490368 bytes; `out/logs/linux_wine_build_report.json`, exit code 0.
- testado_em_emulador: **parcial** — ROM vigente confirma KOs dos dois lados, derrota/vitoria Musgo, barras zeradas, reset, fonte do atlas e revanche NTSC. Em 2026-09-13: P2 vencedor + START em NTSC (`visual_ko_20260913T114321Z`) e PAL (`visual_ko_20260913T114702Z`); DRAW + reset (`visual_ko_20260913T114914Z`); vencedor por tempo com vida desigual + reset (`visual_ko_20260913T193905Z`). Audio com sinal e rota isolada em `visual_ko_20260913T115242Z`, sem audicao critica/SFX dedicados. Identidade de evidencias selada; faltam VLAB/VDP/runtime/pior budget.
- rom_head: **portado em 2026-09-10** — header sega agora carrega "HAMOOPIG - HAMOOPI ENGINE BY GAMEDEVBOSS" e "(C)GAMEDEVBOSS26" (antes SAMPLE PROGRAM); titulo da janela BlastEm exibe o nome real. ROM sha256: 558bea6c80c76ec3da23afd584d4b56ece7722847ab1efc8c2f23f43f8529be9
- validado_budget: **nao** — probe HPRB mediu 10.064 bytes DMA no pior quadro NTSC (acima de ~7.782), 58 links VDP e 12 sprites/scanline; decisão técnica `cabe com recuo`. Reduzir/parcelar uploads antes de qualquer promoção.
- audio: **BGM Ken Stage ligado no XGM1** — MIDI vgmusic `ssf2_ken_stage_vgmusic.mid` (sha256 `44804801...`) e referencia e nao entra na ROM. VGM NTSC 9333 B (YM2612 3ch + PSG noise, 16 compassos @ 90 BPM, loop apos patches) em `res/music/ken_stage.vgm`; `XGM bgm_ken_stage` + `XGM_startPlay` em gRoom==10. Driver permanece XGM1 porque os SFX usam PCM CH3/CH4. Relatorios: `rascunho/ken_stage_vgm_report.json`. SFX Ken reusa o mapa GPL do Ryo.
- hud: **P1/P2 barras em sprites de células fixas 16×8**, oito segmentos por jogador, com índice 0 transparente e PAL1 amarelo; as células vazias são ocultadas, portanto o cenário fica visível até o topo. O relógio usa dois sprites do atlas; o WINDOW ficou restrito ao painel transitório de mensagens/resultado. KO ainda sprite. Orientação e medição em `doc/curation/2026_09_13/discord_life_bar_multiplex.md`.
- título: **menu persistente implementado em `gRoom==1`**. `START` entra no seletor; `OPTION` contém `SFX`, `MUSIC` e `BACK`. P1 navega com D-pad/A/START/B, P2 é ignorado e o avanço automático de 2 s foi removido. Fonte atlas 16×16 e cursor de um tile usam PAL1; configurações de áudio valem durante a sessão. Capturas manuais de título, OPTION e seletor: `out/emulator_evidence/title-menu-manual-20260914-v2/`; bundle canônico continua bloqueado por ausência de VLAB/VDP/runtime. Contrato em `doc/13-spec-cenas.md` e teste em `rascunho/temporario/test_title_menu_contract.py`.
- palco: **Showdown-at-the-Park compare_flat**, `gfx_showdown` 512x256 PAL0. Rota ativa `convert_tile_budget.py`: preview solicitado local, 14 cores, 768 tiles residentes, sem ampliacao de blocos 4x4. Reuso aproximado de tiles preserva detalhe pequeno mas perde detalhes locais; permanece estudo/placeholder. Camera H 0..192 e V 0..32; parallax nao executado. Relatorio `res/gfx/showdown.json`.
- roster: **Ryo id=1, Ken id=2, Musgo id=3**. Ken: sheet arcade, idle 64x96, IP Capcom = placeholder. Musgo: grappler autoral de pantano, idle 80x104, walk 88x104, slam 88x120, faces right, `PLAYER_STATE_MUSGO` / `res/musgo.res`. MODE cicla 1-2-3. Seletor LEFT/RIGHT pelos tres; default P2=Musgo. Sem opt-in `fighting_2d_traditional`. Musgo e `source_candidate` (IA + quantize), nao pixel nativo final.
- sombra: **ligada** — `spr_sombra` 64x16 composto do primeiro frame de `spr_ryo_100`; follow em `FUNCAO_SPR_POSITION`.
- ready_for_aaa: false

## 3. Decisoes da porta (2026-09-10)

- Makefile Docker upstream substituido pelo wrapper canonico (`tools/sgdk_wrapper/build.sh`); upstream usava imagem `registry.gitlab.com/doragasu/docker-sgdk:v2.11`.
- `res.zip` upstream (821 KB) extraido para `res/` sem `__MACOSX`/`.DS_Store` e sem headers gerados (regenerados pelo rescomp no build).
- `fix_migration_issues.ps1` aplicou 10 reescritas; 8 foram revertidas por falso-positivo: as regras `include_sprite_h_to_sprite_eng_h` e `include_sound_h_to_snd_sound_h` assumem que `sprite.h`/`sound.h` sao headers de engine, mas aqui sao headers de RECURSO gerados pelo rescomp (declaram `spr_*`/`snd_*`). Mantidas as reescritas legitimas (`VDP_showFPS_1to3`, `SPR_init_args_to_void`).
- Boot files (`src/boot/sega.s`, `src/boot/rom_head.c`) do template modelo/SGDK 2.11 mantidos.
- Asset proveniencia: arte upstream = `hand_authored_pixel` (autoral do upstream); PCM silenciosos = `procedural_primitive` com `acceptance_status: placeholder`.

## 4. Bloqueios

- Nenhum bloqueio de metodo ou build. Teto `prototype`: P2/START, PAL basico, empate/time-over e sinal de audio agora tem provas na ROM vigente. Permanecem especiais/projeteis apos reset, PAL ampliado, audicao/SFX, FPS do loop e pior DMA/SAT/fragmentacao. Selo de arquivos nao e aprovacao desses eixos.

## Playtest de especiais — 2026-09-13

- A sessão `out/emulator_evidence/visual_ko_20260913T230125Z/` está vinculada à ROM `532d4453...` e contém 288 quadros de comandos antes/depois do reset.
- Ryo P1 mostrou o projétil `spr_ryo_701` após a sequência que chega ao estado 700; Musgo P2 mostrou seu golpe `spr_musgo_700`, que não é um projétil por contrato do código.
- A captura prova evento visual e teardown/reentrada exploratória; não fecha hitbox, latência, DMA, SAT, scanline, FPS do loop ou áudio. Detalhes e lições: `doc/curation/2026_09_13/specials_playtest_closeout.md` e `doc/agent_learning/specials_playtest_lessons.md`.

## Probe VDP/DMA/SAT — 2026-09-13

- Build posterior com sonda opt-in: ROM `ae6f5dab...`; `HAMOOPIG_probeTick()` mede a fila DMA antes do VBlank, sprites ativos, links VDP e pico por scanline; snapshot HPRB em SRAM `0x500`.
- Sessão `visual_ko_20260914T000840Z`: DMA máximo 10.064 bytes no frame 3480, pico de scanline no frame 3158, 70 links, 12 por scanline, 39 ativos em 5.250 amostras. Resultado `cabe com recuo`; DMA NTSC é o blocker dominante.
- Relatório: `doc/curation/2026_09_13/vdp_probe_closeout.md` e `out/logs/hprb_probe_report_20260913.json`. Finalizador sem selo porque `00_select.png` foi um frame preto precoce; nenhuma conclusão de qualidade/performance foi promovida.
- Janela PAL curta na mesma ROM (`visual_ko_20260914T000023Z`) mediu DMA 7.984 B, 38 links e 8 sprites/scanline em 1.950 amostras: `cabe` no envelope PAL. O recuo de uploads é específico do pior quadro NTSC.
- Janela PAL repetida na ROM atual (`visual_ko_20260914T001135Z`) confirmou DMA 7.984 B, 38 links e 8 sprites/scanline; relatório `out/logs/hprb_probe_report_20260914_pal_latest.json`.
- Plano de redução DMA NTSC: `doc/curation/2026_09_14/dma_reduction_plan.md`. Não truncar a fila; primeiro atribuir o pico, separar preload e otimizar uploads de frame único/janela ativa, com nova prova NTSC/PAL antes de promover budget.
- Experimento controlado rejeitado: ROM de laboratório `91591dac…` trocou `spr_spark3` por `spr_spark2` apenas no `SparkType==3`; HPRB parcial continuou em 10.064 B (frame 4.469) e o impacto perdeu leitura. Baseline funcional `ae6f5dab…` foi restaurado; em seguida o build diagnóstico HPRB v3 passou a ser `8544c31d…`.
- HPRB v5 no mesmo frame: ROM `e91823b7…`, sessão `visual_ko_20260914T012538Z`, pico total 10.064 B no frame 4.469; 4.576 B já pendentes + 5.488 B de `SPR_update()`. HUD acrescentou no máximo 480 B; backlog de sprites é o blocker dominante.
- Revisão life-bar compacta (2026-09-14): asset `energy_yellow_segment.png` corrigido para índice 0 transparente e índice 2 amarelo; células 16×8 reduzem a linha para 16 sprites no pior caso. Captura final `visual_ko_20260914T030007Z` mostra cenário sem faixa preta e barras P1/P2; HPRB da sessão `blastem-linux-20260914T030115Z-1244960` mediu 5.688 B DMA, 17 links VDP e 5 sprites/scanline em 330 amostras (NTSC). O relatório é evidência da sessão e não promove `validado_budget` global.
- Laboratório de reuso de estado (`visual_ko_20260914T010324Z`): delta de sprites caiu para 6.408 B, mas total continuou 10.064 B; macro `HAMOOPIG_DMA_LAB_REUSE_STATE_SPRITE` voltou a 0. Candidato parcial, não promovido.
- Laboratório de backpressure (`visual_ko_20260914T014412Z`): remover `SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE` não mudou 10.064 B; `DMA_getMaxTransferSize()` não limita a rota atual. Macro `HAMOOPIG_DMA_LAB_DELAYED_FRAME` voltou a 0.
- Laboratório de ritmo neutro (`visual_ko_20260914T015158Z`): duplicar duração de idle/crouch/walk não mudou 10.064 B; macro `HAMOOPIG_DMA_LAB_IDLE_SLOW` voltou a 0. Ataques/transições continuam prioritários.
- Inspeção do vídeo vinculou o frame 3480 ao impacto grande/KO (`spr_spark3`) e o frame 3158 à pose/efeito de combate. O candidato será comparado em laboratório antes de alterar o spark de entrega.

## 5. Regra de continuidade

Atualize este arquivo, o changelog e os manifests sempre que a verdade
operacional mudar. Nunca copie hashes, builds, aprovacao ou evidencia do modelo.


## Curadoria local — 2026-09-11

Analise registrada em `doc/curation/2026_09_11/curadoria_hamoopig.md`. Confirmados estaticamente: copia de paleta ultrapassa palette[64] por 4 bytes; facing de especial P2 compara x consigo; round restart vazio. Prioridade: integridade, round completo e provas simetricas antes de ampliar roster. Contexto planning passou; higiene bloqueada pelo icone da raiz. Nenhum C/asset/ROM alterado, nenhuma nova execucao BlastEm, nenhuma promocao canonica. ROM preservada: `1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6`.

## Implementacao da curadoria — 2026-09-12

- Eliminado o overflow de CRAM por cópia de paleta limitada a slots de 16 cores.
- Corrigido o facing do especial do P2 e removido o piso temporário de energia que impedia KO natural.
- Implementados melhor de três, empate por tempo sem ponto, reset transacional em `gRoom==12` e pós-luta em `gRoom==11`.
- Reset integral agora cobre física, estado, buffers, projéteis, sparks, HUD, relógio e handles; `CLEAR_VDP` invalida handles liberados.
- O gate `gPodeMover` preserva A/START somente no menu pós-luta; START foi visto retornando ao seletor.
- O ícone solto da raiz foi movido para `rascunho/upstream_reference/hamoopig_icon.png`, preservando seu hash.
- Fechamento detalhado: `doc/curation/2026_09_12/implementation_closeout.json`.

## Historico das tentativas anteriores — 2026-09-12 (supersedido pela revisao abaixo)

- HUD: energia zero agora apaga as 16 colunas, inclusive P2, e a barra atualiza durante o congelamento de KO.
- Cenário: conversão baseada no preview do laboratório, 14 cores e 604 tiles; a versão 1× excedeu VRAM e foi rejeitada, mantendo-se o compromisso 4× medido.
- Experimento 2× (2026-09-12): 1.393 tiles com `SPR_initEx(320)` causaram corrupção de HUD/mapa/sprites no bundle `interactive-round-integrity-20260912T132630Z`; configuração foi revertida para 4× + `SPR_init()` e o hash estável `363774d9` foi preservado.
- Musgo: estado 570 fixa o pivô no piso e reaproveita a animação 550. O derivado `defeat.png` causou `ADDRESS ERROR` e foi quarentenado em `rascunho/defeat_experiment_address_error.png`.
- Musgo KO (patch 2026-09-12): estado 570 não reentra mais em `PLAYER_STATE(570)`; segura o último frame (`animFrameTotal`) e o tempo final, evitando reinício infinito da queda. Prova dedicada em emulador ainda pendente.
- Tentativa de invalidar o cache do HUD a cada frame zero foi removida: causava escritas redundantes e nao havia prova de cache corrompido. O reset de round ja restaurava `energia`; residual herdado nao foi confirmado como causa.
- Mensagens: pós-luta usa PAL2, prioridade alta e linhas separadas; fidelidade à fonte `hud_fonts_healthbars_v1.png` ainda não está provada.

## Revisao visual/KO implementada — 2026-09-12

- Barras: recorte termina na linha 29 do atlas (antes dos numeros); apenas uma variante KO. Zero preenche o retangulo preto completo uma vez; vida positiva mantem pelo menos uma coluna.
- Dano: `EnergyType==2` nao reinicia queda; dano letal entra em 550 apenas uma vez, preservando lancamento ja iniciado. Clamps 0..96 com intermediario s16. Regressao host executa as funcoes C reais para os dois jogadores e 192 transicoes letais.
- Musgo: recursos distintos para queda (120x120, 2 frames), derrota deitada (128x64, 1 frame) e vitoria de punhos erguidos (88x128, 1 frame). Arte via image_gen, convertida para paleta existente, `source_candidate`; fonte e prompt persistidos em `data/source_art/musgo/ko_victory_source_v1.png` e `ko_victory_prompt.txt`.
- Round: espera resultado por pelo menos 180 ticks; KO exige timer >=440 e derrotado em 570. Animacao vencedora segura ultimo frame, sem determinar sozinha a transicao.
- Mensagens: alfabeto do atlas solicitado em `ts_hud_message_font`, PAL1, celulas 16x16, painel preto prioritario em BG_A, upload `DMA_QUEUE_COPY`. ROUND/FIGHT/KO/DRAW/PLAYER 1 ou 2 WINS, A REMATCH e START SELECT.
- Residencia: stage 768 + HUD 249 + inicio 1 = tile livre 1018; SGDK sprite region inicia em 1020 (420 tiles). Proximo degrau 832 termina em 1082: rejeitado estaticamente por sobrepor 62 tiles. Guard consulta `TILE_SPRITE_INDEX`; isto nao prova pior DMA/scanline.
- Corrigidos usos NULL dos marcadores de wins ausentes. Sombra passou a alocacao automatica em vez do indice fixo 1460, que pertence a fonte SGDK no layout observado.
- Diagnostico da ROM intermediaria dcb2babe: debugger leu vida 72 e depois 22; nenhum write em RAM/ROM. Socos produziram KO, barra vazia, derrota deitada e ROUND 2 em `visual_ko_20260912T141518Z/{ko_midfall.png,ko_ground.png,next_round.png}`. A primeira gravacao longa dessa pasta foi interrompida; nao equivale a partida completa.
- Revisao adicional: indice zero do BG_B reservado, cores opacas 1..14; evita que chao claro revele backdrop preto. Teste `rascunho/temporario/test_stage_palette.py` passou. Painel agora ocupa linhas 5..10, preservando a silhueta de vitoria.
- Capturas frescas revisadas: `out/emulator_evidence/visual_ko_20260912T162753Z/` e `visual_ko_20260912T162933Z/`. Queda, poses terminais, mensagens, HUD vazio e revanche observados; FPS sustentado/audio/budget nao certificados. Fechamento: `doc/curation/2026_09_12/visual_ko_closeout.md`.
- Aprendizado local: `doc/curation/2026_09_12/visual_ko_lessons.json`; nenhuma alteracao/promocao do framework canonico.

## Orientações externas para revisão da engine — 2026-09-12

- Foi lido o histórico completo de `#ff-rheo-bout` e 14 canais complementares do RETRODEVBR.
- As práticas de SGDK/VRAM/tiles/camadas, resolução, paleta, áudio, emuladores, animação, manual e escopo estão registradas em `doc/engine/discord_guidance_original_engine_review_2026-09-12.md`.
- GameDevBoss/Daniel Moura é identificado como desenvolvedor original da HAMOOPIG; autoria de orientações comunitárias (Vagno, Titan Doom, SirMacho, rheo, Alan ARS, HelderEstrela e outros) foi preservada no documento e não foi atribuída indevidamente.
- Próxima revisão planejada: mapear VRAM e `gInd_tileset`/`SPR_initEx`, medir tiles/ciclos/camadas/pior frame, revisar paleta/contraste, áudio e manuais, e só então promover mudanças.
- Nenhuma implementação ou promoção de claim foi feita como consequência desta pesquisa.

## Fechamento QA — 2026-09-13

- Cinco sessoes da ROM 532d4453 seladas pelo finalizador canonico; `out/logs/evidence_closeout_report.json` = sealed e gate semantico passou. Selo e identidade/integridade, nao qualidade nem budget.
- P2/START em NTSC e PAL, DRAW + reset, vencedor por tempo com vida desigual + reset observados. Audio isolado com sinal em duas sessoes; audicao/SFX sob carga ainda pendentes.
- Regressoes de vida/HUD, paleta/hash e 9.216 pares do time-over passaram; auditor de sinal PCM tem self-check e falha em silencio/rota ausente.
- Grafo .res renovado: 4 informativos ALIGN e aviso code_loaded_tiles_unmeasured. Contratos de cena ainda sem relatorio de compilacao, validation_report historico; nao declarar pipeline global limpo.
- Host da retomada da tarde esteve sob carga elevada; FPS do titulo e video nao sao medida do loop.
- Nenhum C, asset ou ROM alterado nesta rodada; encerradas as sessoes de teste e removidos seus sinks temporarios.
- Provas, limites e proxima ordem: `doc/curation/2026_09_13/qa_continuation_closeout.md`. Licoes JSON locais em `test_harness_lessons.json`, caderno em `doc/agent_learning/qa_continuation_lessons.md`; Capture local executado sem promocao canonica.

## 2026-09-14 - Transição da abertura para o menu

- O splash HAMOOPIG permanece íntegro durante a abertura; `KEY_PRESSED` apenas
  o encerra e nunca é reutilizado para confirmar `START` no mesmo frame.
- A entrada no menu restaura o tilemap original e aplica o painel estreito
  somente depois, evitando corrupção por fade/DMA concorrentes.
- Evidência manual BlastEm: `out/emulator_evidence/title-transition-final-20260914/`
  (`opening_2s.png`, `menu_12s.png`). ROM
  `68baca0e2845a00d057e0d8b892102247f5674350194dcf8509b07e895734d7d`.
- O bundle canônico continua bloqueado por ausência de métricas VLAB/VDP/runtime;
  a captura manual não promove budget.

## 2026-09-14 - Planejamento do modelo de engine de luta

- Novo plano solicitado pelo usuário: `doc/engine/fighting_engine_improvement_plan.md`;
  tarefas/dependências e handoff por capacidade em `doc/engine/fighting_engine_roadmap.json`.
- Escopo planejado: timing/input, abertura separada com fade para título próprio,
  opções ON/OFF, especial, combos, relógio transparente, cenário revisado e segundo palco amplo.
- Inspeção desta rodada encontrou o commit `19eb8fae` e a ROM
  `e2ca583341b3f0784442b765df67080ebb02cd015b8e06494c570464e65be0f4`.
  Os hashes e claims anteriores permanecem históricos; vínculo fonte→ROM não foi revalidado.
- Confirmados em código/asset: opções recentes de debug/pausa/tick/H240; especial
  parcialmente comentado; atlas do relógio sem índice transparente 0; Showdown com
  substituição aproximada de 1.629 tiles por 768 representantes.
- Contexto planning e higiene passaram; auditoria de aprendizado encontrou contexto local.
  Nenhum runtime, asset ou ROM alterado, nenhum novo teste de emulador nesta rodada.
- Os próximos agentes devem registrar separadamente implementação, testes instrumentados,
  revisão visual/auditiva e budget. Abertura/menu sobrepostos ainda não atendem ao novo
  requisito de cenas distintas. Primeiro passo: P00 do plano.

## 2026-09-14 - Execucao P00 a P02

- O vinculo fonte->ROM que esta pagina dizia nao revalidado FOI revalidado no P00:
  rebuild limpo produz ROM bit-identica. Cada tarefa seguinte invalida esse vinculo;
  o roadmap marca `stale_after_PNN` ate novo rebuild.
- Licao do P00: o decoder HPRB aprovava budget a partir de SRAM truncada ou sem
  nenhuma amostra. Qualquer numero de DMA citado antes de 2026-09-14 a partir desse
  decoder precisa ser reconferido com `--self-check` e com `samples>0`.
- Licao do P01: `peak_dma_frame` e indice de FRAME DE VIDEO desde o boot, nao de tick
  nem relativo a cena. Depois do P01, em PAL os dois contadores divergem em 1,2x.
- Licao do P02: fade sobre 64 cores exige `palette[]` com as quatro paletas. Preencher
  so as do cenario apaga o texto da UI depois de ele ter sido carregado.
- ROM atual: `b64669e845453590668ba779f0f04d8145be6427e1e5f4934ce00ed84721c4ef`.
