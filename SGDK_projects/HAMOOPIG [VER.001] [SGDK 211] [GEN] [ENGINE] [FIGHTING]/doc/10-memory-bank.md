<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-09-19T03:17:18-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 126
- Ultimo build versionado: `out/rom.bin` / `c17af26742c71840462b9da9f7f2037993ff81eb8dd6170f92b3f3916af4ce86`
- ROM vigente (instrumentação VLAB de CPU/jitter, carga de entrada e residência): `c17af26742c71840462b9da9f7f2037993ff81eb8dd6170f92b3f3916af4ce86` (`2490368` bytes). O build passou pelo wrapper SGDK/Wine em `out/logs/linux_wine_build_report.json`.
- Validation summary: o relatório canônico disponível ainda está preso a SHA anterior e não pôde ser refeito porque o validador PowerShell não está disponível neste host; a captura DRAW atual está selada. O contrato VLAB, o teste host e o self-check do sealer passaram.
- Blockers vigentes: CPU sustentada ainda acima de 100% (`max_cpu_load=139%`, `max_cpu_jitter=7`), com custo de entrada separado (`initialization_cpu_peak=744%` no frame 7050); áudio sem captura isolada nesta ROM, revisão independente/rebinding e gates de higiene/proveniência, gameplay completo no SHA vigente e pior-frame combinado continuam pendentes. Sem promoção AAA.
- Evidência de emulador: DRAW real selado em `out/emulator_evidence/visual_ko_20260919T061243Z/evidence_manifest.json`; VLAB registra 7350 amostras, DMA máximo `7016 B`, 22 sprites ativos, 17 sprites/scanline, zero frames VDP acima do orçamento e ranges observados `[1020,420)` e `[1,1009)`. A tentativa de captura com áudio em `visual_ko_20260919T054050Z` falhou por ausência de stream monitorável único e não é evidência de áudio.
- Gate visual: visual_lab_aprovado=False; DRAW observado no SHA vigente, sem promoção AAA
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=parcial performance=VLAB_cena_luta_com_carga_de_entrada_separada_mas_pico_sustentado_139_porcento audio=sinal_presente_sem_audicao hardware_real=emulador_BlastEm
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - HAMOOPIG [VER.001] [SGDK 211] [GEN] [ENGINE] [FIGHTING]

**Ultima atualizacao:** 2026-09-16
**Fase atual:** build 2ba2 parcial: composição limpa da tela de título com fade; captura inicial e OPTIONS renovadas; P10 histórico permanece no SHA anterior até recaptura; revisão sensorial, gameplay completo e pior-frame continuam pendentes
**ROM vigente nesta fase:** `2ba2aaf883a489ac1d2966cc71b448b66a2f3561812dfd8f9c929fae1e06f5e8` (`out/rom.bin`).
**Proxima fase:** fechar audição crítica/visual independente; depois instrumentar pior-frame SGDK e projetar streaming/cache para cenários acima de 864 tiles.
**Aprendizado:** cadernos `doc/agent_learning/musgo_roster_lessons.md` e `doc/agent_learning/showdown_stage_lessons.md`; composição de título em `data/source_art/title/title_assets_report.json`; curadorias L083–L119 registram as revalidações atuais.

## 1. Origem e proveniencia

- Engine origem: `SGDK_Engines/HAMOOPIG-SGDK` (origem upstream `https://github.com/humbertodias/sgdk-HAMOOPIG`, commit f90c0c4).
- HAMOOPIG e a implementacao da engine HAMOOPI (by GameDevBoss / Daniel Moura, 2015-2022) para Mega Drive.
- **Creditos obrigatorios a GameDevBoss (Daniel Moura)** — exigencia do cabecalho de `src/main.c` upstream. Sem license formal; header declara "HAMOOPIG IS FREE AND ALWAYS WILL BE".
- Copia de referencia do material upstream (nao-fonte) em `rascunho/upstream_reference/` com hashes em `imported_assets_sha256.json`.
- A importacao original continha 22 arquivos upstream. O projeto atual e uma porta estendida com alteracoes em runtime, HUD, selecao, lutadores e ciclo de round; nao e mais byte-idempotente.

## 2. Estado operacional

- portado: sim (src/inc/res do upstream materializados)
- documentado: sim (este projeto)
- ROM histórica de referência: `14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440`; os claims abaixo são limitados ao que foi observado nessa build ou explicitamente marcado como pendente.
- implementado: sim (codigo upstream existe e foi portado)
- buildado: **sim (2026-09-15)** — `out/rom.bin` sha256 `14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440`, 2490368 bytes; `out/logs/continuation_p11_showdown_preview_refine_build.log`, exit code 0.
- testado_em_emulador: **parcial** — build histórica confirma KOs dos dois lados, derrota/vitoria Musgo, barras zeradas, reset, fonte do atlas e revanche NTSC. Em 2026-09-13: P2 vencedor + START em NTSC (`visual_ko_20260913T114321Z`) e PAL (`visual_ko_20260913T114702Z`); DRAW + reset (`visual_ko_20260913T114914Z`); vencedor por tempo com vida desigual + reset (`visual_ko_20260913T193905Z`). Audio com sinal e rota isolada em `visual_ko_20260913T115242Z`, sem audicao critica/SFX dedicados. Identidade de evidencias selada; faltam VLAB/VDP/runtime/pior budget.
- rom_head: **portado em 2026-09-10** — header sega agora carrega "HAMOOPIG - HAMOOPI ENGINE BY GAMEDEVBOSS" e "(C)GAMEDEVBOSS26" (antes SAMPLE PROGRAM); titulo da janela BlastEm exibe o nome real. ROM sha256: 558bea6c80c76ec3da23afd584d4b56ece7722847ab1efc8c2f23f43f8529be9
- validado_budget: **parcial** — HPRB schema 7 da matriz atual mediu máximos globais de 8.024 B DMA enfileirados, 41 sprites ativos, 60 sprites VDP e 17 sprites/scanline. A suíte P10 está coberta por probe, mas o pior-frame independente e a folga sensorial ainda não foram fechados.
- audio: **BGM Ken Stage ligado no XGM1** — MIDI vgmusic `ssf2_ken_stage_vgmusic.mid` (sha256 `44804801...`) e referencia e nao entra na ROM. VGM NTSC 9333 B (YM2612 3ch + PSG noise, 16 compassos @ 90 BPM, loop apos patches) em `res/music/ken_stage.vgm`; `XGM bgm_ken_stage` + `XGM_startPlay` em gRoom==10. Driver permanece XGM1 porque os SFX usam PCM CH3/CH4. Relatorios: `rascunho/ken_stage_vgm_report.json`. SFX Ken reusa o mapa GPL do Ryo.
- hud: **P1/P2 barras em sprites de células fixas 16×8**, oito segmentos por jogador, com índice 0 transparente e PAL1 amarelo; as células vazias são ocultadas, portanto o cenário fica visível até o topo. O relógio usa dois sprites do atlas; o WINDOW ficou restrito ao painel transitório de mensagens/resultado. KO ainda sprite. Orientação e medição em `doc/curation/2026_09_13/discord_life_bar_multiplex.md`.
- título: **menu persistente implementado em `gRoom==1`**. `START` entra no seletor; `OPTION` contém `SFX`, `MUSIC` e `BACK`. P1 navega com D-pad/A/START/B, P2 é ignorado e o avanço automático de 2 s foi removido. Fonte atlas 16×16 e cursor de um tile usam PAL1; configurações de áudio valem durante a sessão. Capturas manuais de título, OPTION e seletor: `out/emulator_evidence/title-menu-manual-20260914-v2/`; bundle canônico continua bloqueado por ausência de VLAB/VDP/runtime. Contrato em `doc/13-spec-cenas.md` e teste em `rascunho/temporario/test_title_menu_contract.py`.
- palco: **Showdown-at-the-Park compare_flat**, `gfx_showdown` 512x256 PAL0. Rota ativa `convert_tile_budget.py`: preview solicitado local, 14 cores, 864 tiles residentes, sem ampliacao de blocos 4x4. O candidato reduz o MSE RGB para 138.7790, preserva o guard `TILE_SPRITE_INDEX` e passou HPRB NTSC/PAL; permanece estudo/placeholder e requer revisão visual. Camera H 0..192 e V 0..32; parallax nao executado. Relatorio `res/gfx/showdown.json`.
- roster: **Ryo id=1, Ken id=2, Musgo id=3**. Ken: sheet arcade, idle 64x96, IP Capcom = placeholder. Musgo: grappler autoral de pantano, idle 80x104, walk 88x104, slam 88x120, faces right, `PLAYER_STATE_MUSGO` / `res/musgo.res`. MODE cicla 1-2-3. Seletor LEFT/RIGHT pelos tres; default P2=Musgo. Sem opt-in `fighting_2d_traditional`. Musgo e `source_candidate` (IA + quantize), nao pixel nativo final.
- sombra: **ligada** — `spr_sombra` 64x16 composto do primeiro frame de `spr_ryo_100`; follow em `FUNCAO_SPR_POSITION`.
- ready_for_aaa: false

## Repaginação e fechamento P03 — 2026-09-14

- ROM de referência do fechamento P03: `out/rom.bin`, sha256
  `3e46ac068062cfa83f305e85dd66b0c5822bcedd48766749e3a36c74e3ea1841`;
  HEAD `2eee6522`.
- Continuação P05: `energiaSP` agora tem clamp real `0..32` e é renderizada
  como oito células repetidas no BG_A (sem adicionar sprites à SAT). Build de
  integração posterior: sha256
  `39e48a8ca8e9a525ec013fc05c0afaf550b14dbcf955db462688ca52339a6b52`;
  `out/logs/linux_wine_build_report.json` exit code 0. O custo de especial
  agora é cobrado uma vez ao aceitar 700/730; ainda falta toggle de apresentação
  e revisão visual no emulador.
- P03 foi exercitado com input real. Os seis contratos host/estáticos passam e
  `doc/engine/p03_config_report.json` registra 8/8 casos de menu. `LIFE OFF` e
  `CLOCK OFF` foram observados dentro da luta; `MUSIC ON` retoma BGM apenas na
  borda da preferência.
- A repaginação usa uma única geometria (linha 13, cinco itens) e deriva a
  página de `cursor / 5`; o logo HAMOOPIG não é coberto. `DEBUG` mantém os nove
  itens em duas páginas e `B` retorna para OPTIONS no cursor DEBUG.
- INTRO/FADE não são opções do menu: permanecem em `GameConfig`, mas só voltam
  quando houver persistência SRAM ou retorno observável ao título.
- Limitação: as capturas aguardam revisão visual independente e não há escuta
  crítica de áudio; o teto continua `prototype`.
- Próximo bloco de implementação: P04 (eventos de combate/reset), seguido de
  barra especial P05.

## Primeiro corte de hits/combo — 2026-09-15

- `hitCounter` passou a representar o atacante em acertos físicos e de
  projétil; colisões simultâneas continuam incrementando os dois lutadores.
- O HUD exibe `N HITS` no BG_A (linha 21), usando o atlas de mensagens e sem
  sprites adicionais. O contador desaparece quando retorna a menos de dois
  acertos e é zerado pela transição ao estado neutro já existente.
- Build SGDK/Wine aprovado: ROM sha256
  `a85cb58f91a5bcfd71c53f88eeae0f12b1253df3dfcdd07d70d3aef157879639`;
  relatório `out/logs/linux_wine_build_report.json`, exit code 0.
- Ainda pendente: sequência real de multi-hit, captura visual/auditiva e
  verificação de que a mensagem não compete com KO/resultado.

## Opções de especial e combo — 2026-09-15

- `OPTIONS` passou a expor `SPCL ON/OFF`, `HITS ON/OFF`, `TBG ON/OFF` e `RULES ON/FREE`;
  a paginação global continua derivada de `cursor / 5`.
- `SPECIAL OFF` limpa as oito células do medidor na próxima atualização;
  `HITS OFF` remove somente a apresentação; `RULES FREE` permite 700/730 sem
  exigir nem consumir medidor e mantém `energiaSP` em zero.
- Build SGDK/Wine aprovado: ROM sha256
  `134dfd0980f306ed35ab02454baeb072bd087ea2a0077382e2862a462ea4207d`.
- Ainda falta validar estas rotas com input real no emulador e revisar a
  leitura visual das novas páginas.

## Pool de cenários selecionável — 2026-09-15

- `STAGE2 ON/OFF` foi adicionado às OPTIONS. Quando habilitado, P1 usa `C` no
  seletor para alternar `SHOWDOWN` e `BGB2`; quando desabilitado, o runtime
  força `gBG_Choice=1`.
- Os dois ramos já carregam assets distintos (`gfx_showdown`/`gfx_bgb2`), mas
  `gfx_bgb2` ainda é uma arte provisória de duas cores. A promoção para cenário
  final exige fonte autoral, revisão de saturação/repetição e budget próprio.
- Contratos atualizados em `doc/scene-contracts.json` e
  `doc/scene-regression.json`; validação visual e percurso emulador pendentes.

## Transição temporal revalidada — 2026-09-15

- A sessão `out/emulator_evidence/visual_ko_20260915T130109Z/` foi gravada a
  60 fps no SHA vigente. A sequência observada é abertura legível, fade-out,
  intervalo preto e fade-in do título, sem mapa de menu sobre a abertura.
- A captura é evidência temporal exploratória; review visual independente,
  métricas de pior-frame e validação em hardware real continuam pendentes.

## Ocupação de janela para streaming — 2026-09-15

- O diagnóstico de câmera em `out/logs/showdown_stream_window_report.json`
  encontrou 864 padrões globais e pico de 588 padrões únicos numa janela
  42×30 (viewport 320×224 + preload de uma tile), em câmera (184,24).
- O número é planejamento para o cache; não representa upload real nem fecha
  costura, latência ou budget. O streamer nativo permanece pendente.

## Transição abertura → título no SHA e170 (histórica) — 2026-09-15

- A captura `out/emulator_evidence/visual_ko_20260915T135842Z/` foi refeita
  depois da promoção do Stage 2 e está vinculada ao SHA
  `e17027c059396f296ee417da773e1a145bb59efc10999d005cfc5b23679ecf56`.
- O vídeo temporal mostra abertura, fade-out, intervalo preto limpo, título,
  seletor e combate; não há sobreposição observada entre mapas. O bundle é
  exploratório/select-only: revisão visual independente, pior-frame e hardware
  real continuam pendentes.

## KO e reset de round no SHA e170 (histórico) — 2026-09-15

- A rota real `out/emulator_evidence/visual_ko_20260915T140256Z/` levou Ryo ×
  Musgo ao KO no passo 25, registrou `PLAYER 2 WINS` e capturou
  `special_reset_health.png` com as duas barras restauradas.
- O manifesto e a ROM copiada têm SHA
  `e17027c059396f296ee417da773e1a145bb59efc10999d005cfc5b23679ecf56`.
  Esta é evidência de reset durante a luta; GUARD, THROW, simultaneous hit,
  time-over, revisão visual independente e pior-frame ainda não estão cobertos.

## StageDefinition orientada a dados — 2026-09-15

- `inc/stage.h`/`src/stage.c` agora declaram imagem, plano/paleta, loading
  model, orçamento e medição de tiles, câmera, parallax, movimento, BGM e
  proveniência para Showdown e BGB2.
- `src/init.c` consome esses campos e falha explicitamente se um palco
  residente ultrapassar seu orçamento. O build SGDK/Wine segue aprovado no SHA
  a187; o uploader/ring-cache de `STAGE_LOAD_STREAM_WINDOW` ainda não existe.

## Revalidação integrada no SHA a187 — 2026-09-15

- A alteração do loader invalidou as capturas anteriores; a matriz P10 foi
  recapturada e agora tem 36/36 manifests/HPRB no SHA
  `a1875f95c2c7c864b8c48adac34be3036c09fc30063354b65cbefd1fc8333bfe`.
- Também foram refeitos título/retorno, transição abertura→título, KO/reset e
  áudio isolado. O resumo atual registra 8.024 B DMA, 41 sprites ativos, 61
  links VDP e 17 sprites por scanline; review sensorial e pior-frame seguem
  pendentes.

## Promoção do Stage 2 para 864 tiles — 2026-09-15

- `data/source_art/stage2_swamp/convert_stage2.py` usa agora o mesmo teto de
  864 representantes do Showdown. A fonte 512×256 tem 1.829 padrões antes da
  redução e 864 depois; a paleta continua em 9 bits com índice 0 reservado.
- Build `e17027c0…ecf56` e captura `out/emulator_evidence/visual_ko_20260915T132543Z/`
  confirmam Stage 2 selecionado e carregado; HPRB registrou 7.008 B DMA,
  41 sprites ativos, 60 VDP e 17 por scanline.
- A arte ainda é candidata visual; revisão independente e streaming para
  futuros estágios maiores continuam pendentes.

## 3. Decisoes da porta (2026-09-10)

- Makefile Docker upstream substituido pelo wrapper canonico (`tools/sgdk_wrapper/build.sh`); upstream usava imagem `registry.gitlab.com/doragasu/docker-sgdk:v2.11`.
- `res.zip` upstream (821 KB) extraido para `res/` sem `__MACOSX`/`.DS_Store` e sem headers gerados (regenerados pelo rescomp no build).
- `fix_migration_issues.ps1` aplicou 10 reescritas; 8 foram revertidas por falso-positivo: as regras `include_sprite_h_to_sprite_eng_h` e `include_sound_h_to_snd_sound_h` assumem que `sprite.h`/`sound.h` sao headers de engine, mas aqui sao headers de RECURSO gerados pelo rescomp (declaram `spr_*`/`snd_*`). Mantidas as reescritas legitimas (`VDP_showFPS_1to3`, `SPR_init_args_to_void`).
- Boot files (`src/boot/sega.s`, `src/boot/rom_head.c`) do template modelo/SGDK 2.11 mantidos.
- Asset proveniencia: arte upstream = `hand_authored_pixel` (autoral do upstream); PCM silenciosos = `procedural_primitive` com `acceptance_status: placeholder`.

## 4. Bloqueios

- Nenhum bloqueio de metodo ou build. Teto `prototype`: P2/START, PAL basico, empate/time-over e sinal de audio agora tem provas em builds históricas. Permanecem especiais/projeteis apos reset, PAL ampliado, audicao/SFX, FPS do loop e pior DMA/SAT/fragmentacao. Selo de arquivos nao e aprovacao desses eixos.

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
- Residencia histórica (candidato 768): stage 768 + HUD 249 + inicio 1 = tile livre 1018; SGDK sprite region inicia em 1020 (420 tiles). O candidato atual 864 + atlas 72 usa primeiro livre 937; o degrau 1024 continua rejeitado. Guard consulta `TILE_SPRITE_INDEX`; isto nao prova pior DMA/scanline.
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

## 2026-09-14 - Stage 2 amplo e seleção por sessão

- Fonte candidata autoral preservada em `data/source_art/stage2_swamp/` com
  prompt e SHA-256 (`2dfbd4ac71077bed77f3d871c1ad97ec763730f9cdcd88363aacd312a699b133`).
- Conversão determinística para `res/gfx/bgb2.png`: 512×224, índice BG_B zero
  reservado, 13 entradas úteis na grade de 9 bits e 768 tiles após reuso de
  tiles completos. Relatório: `data/source_art/stage2_swamp/convert_stage2_report.json`.
- `STAGE2 ON/OFF` controla a seleção de P1; desligado força Showdown. Testes
  estáticos de seleção e paleta passaram. ROM recompilada:
  `7ca637e0fbcb4cd22abc5f04c6fd84006a886d41f084f6ad811e52e64a1b3bd2`.
- A imagem convertida foi inspecionada fora do emulador e está legível como
  cais/pântano; ainda não há captura BlastEm desta ROM, nem prova de câmera,
  DMA pior-frame, áudio ou validação final. Status permanece
  `source_candidate`/`pending_visual_review`.

## 2026-09-14 - Combo por evento e janela determinística

- Acertos válidos agora passam por `FUNCAO_REGISTER_HIT()` e alimentam uma
  janela de 60 ticks; o contador não desaparece ao retornar a idle e expira
  de forma determinística. Colisões simultâneas registram P1 e P2 uma vez.
- `FUNCAO_UPDATE_HIT_COMBOS()` roda somente no tick de combate não pausado;
  hit-pause congela a janela e o estado 570 limpa contador/timer no KO.
- Host regression `tests/test_combo_contract.py` passou junto da suíte (9/9).
  Build SGDK 2.11 concluído; ROM atual:
  `0a10f366bdd47dd6969862dc466fccb6e7bde5cd5b3dc554fd2879ddfe7088f4`.
- Ainda falta captura no emulador de uma sequência multi-hit e revisão visual
  do texto `N HITS`; o comportamento estático/host não promove essa evidência.

## 2026-09-14 - Relógio sem fundo opaco

- O atlas `clock_digits_window.png` tinha 1.635 pixels no índice 11, que
  tornava-se preenchimento opaco quando o sprite usava a PAL1 da barra. O
  conversor `data/source_art/sf_hud/convert_clock_mask.py` remapeia esse índice
  para 0 transparente e aproxima os demais tons da paleta compartilhada.
- `res/hud_gfx.res` usa agora `clock_digits_transparent.png`; o contrato completo
  está em `doc/ui_pixel_surface_contract.json` e o teste dedicado passou.
- Build SGDK 2.11 atualizado: ROM
  `0a10f366bdd47dd6969862dc466fccb6e7bde5cd5b3dc554fd2879ddfe7088f4`.
  Falta confirmar em captura NTSC/PAL que o cenário permanece visível atrás
  dos dois dígitos e que não há degradação de contorno.

## 2026-09-14 - Captura fresca da ROM atual

- A ROM `0a10f366bdd47dd6969862dc466fccb6e7bde5cd5b3dc554fd2879ddfe7088f4`
  foi executada no BlastEm; o burst mostra a abertura legal, o fade para preto
  e o menu de título já separado.
- A inspeção visual manual confirma que o splash não é coberto pelo menu. O
  bundle canônico foi bloqueado por `vlab_block_missing`, `vdp_dump` e
  `runtime_metrics` ausentes; câmera, DMA, FPS e áudio continuam pendentes.
- Artefatos exploratórios: `out/emulator_evidence/current_rom_20260914/`,
  `out/emulator_evidence/current_rom_20260914_transition/` e a captura fresca
  `out/emulator_evidence/current_rom_20260914_final8/`. Lição registrada
  em `doc/curation/2026_09_14/clock_stage_transition_learning.json`.

## 2026-09-14 - Ledger de eventos de combate

- `inc/combat_event.h`/`src/combat_event.c` adicionam uma fila estática de oito
  eventos por tick. `FUNCAO_REGISTER_HIT()` registra atacante, defensor, estado
  e tick sem duplicar dano ou efeitos da FSM existente.
- O overflow é explícito (o evento não é sobrescrito), permitindo reprovar o
  budget em vez de perder um hit silenciosamente. O reset ocorre no início de
  cada tick de luta.
- Host contract `tests/test_combat_event_contract.py` passou; suíte atual é
  12/12 e a ROM recompilada é
  `37204b1dacc9833cb57ba6d3a8302d069c37c1ddad7d4326383bf9fb37ae80c1`.
- P04 segue `in_progress`: falta substituir a aplicação legada por consumo
  centralizado, além de validar colisões simultâneas e reset no emulador.

## 2026-09-15 - TIMER BG compacto

- A opção `TBG ON/OFF` foi adicionada ao menu. `OFF` mantém o relógio totalmente
  transparente; `ON` escreve somente uma moldura 6×2 tiles em torno dos dois
  dígitos, sem WINDOW de tela inteira.
- O painel usa o mesmo tile PAL1 reservado do HUD, atualiza apenas quando a
  preferência muda e é limpo na saída da luta. Teste de superfície e suíte
  12/12 passaram; revisão visual em fundos dos dois palcos continua pendente.
- Build SGDK 2.11: ROM
  `9613d9ba8c4b0cb7ba7d76c0644551ad8dd6280994abb10ed5796558cb4b5d41`.

## 2026-09-15 - Mapa inicial do título protegido

- `title_commit_map()` usa DMA síncrona antes do fade inicial, evitando quadro
  parcialmente composto durante a passagem splash → título.
- Captura fresca: `out/emulator_evidence/current_rom_20260915_title_dma/`.
  O título é visível, mas a captura canônica continua pendente de VLAB/VDP e
  runtime metrics.
- A tentativa de entrar em OPTIONS gerou `out/emulator_evidence/current_rom_20260915_options_cpu/`;
  o canal de teclado externo não produziu confirmação reproduzível, portanto
  essa imagem não é aceita como prova da página.

## 2026-09-15 - Barreira de DMA na navegação do título

- A restauração do artwork do BG_A agora termina com `VDP_waitDMACompletion()`
  antes de a página OPTIONS/DEBUG ser escrita por CPU. A mudança foi feita
  para eliminar a corrida que podia deixar a composição parcial na troca.
- Build SGDK 2.11: ROM
  `90688a5d4f8dc5e613b12fc3a4e8e81ef1df5c5c56916e2d9f978b6fba811651`;
  suíte estática/host 12/12.
- A navegação foi exercitada manualmente com uma borda Down mantida por 200 ms
  seguida de A; OPTIONS estabilizou em `out/emulator_evidence/current_rom_20260915_options_dma_barrier/`.
  O bundle canônico ainda está bloqueado por VDP dump/runtime metrics ausentes.

## 2026-09-15 - Primeiro consumidor central de eventos

- `FUNCAO_REGISTER_HIT()` deixou de alterar diretamente `hitCounter` e
  `hitComboTimer`; agora apenas emite `CombatEvent`.
- `FUNCAO_CONSUME_COMBAT_EVENTS()` roda uma vez depois da FSM, com
  `COMBAT_EVENTS_CLAIM_CONSUMPTION()` protegendo contra consumo duplicado no
  mesmo tick. A vida e os ganhos de especial continuam nos caminhos legados;
  a migração completa do P04 ainda não está concluída.
- Build SGDK 2.11: ROM
  `1c685106ecbbe51e888eeeaddaa75132030ad01f27c52b22e49cc88b6b8bbb4f`;
  suíte estática/host 12/12.

## 2026-09-15 - Eventos HIT e GUARD

- O ledger agora classifica colisões confirmadas como `COMBAT_EVENT_HIT` e
  bloqueios como `COMBAT_EVENT_GUARD`, incluindo guard de projétil.
- O consumidor de combo ignora GUARD; isso impede combo falso por bloqueio e
  deixa a borda disponível para o futuro ganho de medidor.
- Build SGDK 2.11: ROM
  `1ab2396c7028ba4698e97abf6c442c484cab088fc36015592cff320a5a8d5d1a`;
  suíte estática/host 12/12.

## 2026-09-15 - Delta de especial anexado ao HIT

- `CombatEvent` passou a carregar `meterDefenderDelta`. Chamadas de
  `FUNCAO_UPDATE_LIFESP(..., 2, ...)` feitas após um HIT são anexadas ao evento
  e aplicadas pelo consumidor central, preservando clamp `0..32` sem dupla
  atualização.
- O caminho de projétil registra o HIT antes do delta. Chamadas fora de um
  evento continuam com fallback direto para não quebrar ferramentas legadas.
- Build SGDK 2.11: ROM
  `fbbdc278613daa06d9a5677408daa2f755976c97054d7d9612b1b9276e53759e`;
  suíte estática/host 13/13.

## 2026-09-15 - Política fixa de ganho HIT/GUARD

- O consumidor central agora aplica `+4` ao atacante e `+2` ao defensor em
  `COMBAT_EVENT_HIT`, e `+1` ao atacante em `COMBAT_EVENT_GUARD`.
- Os valores legados por golpe continuam armazenados como telemetria de
  migração, mas não são somados novamente. Isso elimina ganho implícito e
  torna o balanceamento reproduzível por dados.
- Build SGDK 2.11: ROM
  `5cef44779afe5356243d3ddcd486d40fd404b0461eca6dbcf4dfe257831d1de6`;
  suíte estática/host 13/13.

## 2026-09-15 - Harness de captura alinhado ao front-end

- `tests/capture_visual_ko.py` agora captura a tela de título e envia START
  antes de procurar o seletor. O harness antigo pressupunha entrada direta no
  seletor e reprovava a ROM nova por uma pré-condição obsoleta.
- Sessão curta em ROM histórica alcançou seletor e luta:
  `out/emulator_evidence/visual_ko_20260915T035136Z/`. Isso é evidência
  exploratória de entrada no gameplay; não certifica eventos, arte ou budget.

## 2026-09-15 - Deduplicação de eventos no mesmo tick

- `COMBAT_EVENTS_EMIT` agora suprime a segunda observação com a mesma tupla
  atacante/defensor/estado/tipo dentro do tick. O índice do evento original é
  preservado para que deltas legados continuem auditáveis sem criar outro
  combo ou ganho central de medidor.
- O contrato host foi ampliado para verificar contagem estável e anexação ao
  evento original; dano/resultado ainda seguem na rota legada até a próxima
  etapa de migração.
- Build SGDK 2.11: ROM
  `daa412775ec319764be97c59acb7cd58922db2c75a788900999e51c59a5bcb32`;
  suíte estática/host 13/13.
- Sessão exploratória vinculada ao build atual:
  `out/emulator_evidence/visual_ko_20260915T041529Z/`, ROM
  `daa412775ec319764be97c59acb7cd58922db2c75a788900999e51c59a5bcb32`;
  alcança título, seletor e luta e contém vídeo de percurso. Ainda não
  substitui bundle canônico de VDP/runtime nem revisão independente da arte
  quadriculada do cenário.

## 2026-09-15 - Vida consumida pelo ledger de combate

- `CombatEvent` agora carrega `healthDelta` e `healthAttached`. A primeira
  chamada de vida após HIT/GUARD fica enfileirada; o consumidor aplica o dano
  uma vez depois da FSM, preservando o lançamento para 550 e o clamp `0..96`.
- Uma segunda chamada para o mesmo evento é rejeitada como duplicata, evitando
  dano repetido quando a colisão é reavaliada no mesmo tick. Sem evento, o
  caminho direto continua disponível para cura, reset e compatibilidade legada.
- Contrato novo: `tests/test_health_event_contract.py`; suíte completa 14/14.
  Build SGDK 2.11: ROM
  `e4a85eed0a4c297e13607e76da314ac62b8823e731c26c5b2530599112070e87`.
- A migração cobre a aplicação de vida; resolução de vitória/empate, reset de
  round e instrumentação de eventos no BlastEm ainda não foram fechados.

## 2026-09-15 - Manifesto de captura tolera configuração Flatpak ausente

- O harness `tests/capture_visual_ko.py` não aborta mais ao procurar
  `blastem.cfg` em um diretório que o wrapper não materializa. O manifesto
  registra `config_sha256: null` e `config_path_present: false`, distinguindo
  configuração não observada de configuração validada.
- A captura completa foi repetida em ROM histórica e terminou com manifesto,
  screenshots e vídeo: `out/emulator_evidence/visual_ko_20260915T044013Z/`.
  O SHA da cópia e de `out/rom.bin` é
  `e4a85eed0a4c297e13607e76da314ac62b8823e731c26c5b2530599112070e87`.
- A sessão confirma apenas o percurso de entrada até luta/KO candidato; não
  substitui revisão visual independente, probe de eventos, VDP dump, áudio ou
  medição de pior-frame.

## 2026-09-15 - Resultado do evento e limpeza explícita entre rounds

- `CombatEvent.result` começa em `NONE` e o consumidor marca `HIT` ou `KO`
  depois de aplicar o delta de vida. O resultado fica disponível para futuras
  mensagens, áudio e telemetria sem inferir KO a partir de pixels amarelos.
- `COMBAT_EVENTS_RESET()` foi adicionado e é chamado por
  `FUNCAO_INICIALIZACAO()`, além do reset por tick. Eventos pendentes não
  atravessam o commit de uma nova luta.
- O contrato verifica resultado HIT/KO, reset explícito e os caminhos
  simultâneos; suíte completa permanece 14/14. Build SGDK 2.11:
  `e4a85eed0a4c297e13607e76da314ac62b8823e731c26c5b2530599112070e87`.
- A sessão atual está vinculada ao mesmo hash, mas continua exploratória: não
  mede o probe de eventos, VDP, budget ou áudio crítico.

## Continuação P04 — identidade do evento e guarda de vitória (2026-09-15)

- P08 avançou com uma fonte nativa do laboratório de Showdown: o recorte
  `128,224–640,480` do mundo 768×480 foi preservado localmente com SHA
  `9eee7558aa1a13c4536825d30786aaf04bbd613bd34cace5eba0cb3211467cfe`.
  O conversor produz 512×256 com 768 tiles, sem escala 4×, e a ROM
  `c9ae1c999525f31a387d06d491488870019d09eda95050954371d085f1a53849` chegou
  ao round no BlastEm. A composição ganhou mais vegetação/água/pedra, porém a
  repetição de tiles continua perceptível.
- O fixture do laboratório não é arte autoral final. DMA máximo continuou em
  8288 B contra 7782 B nominais NTSC; streaming nativo por janela, budget e
  revisão visual independente permanecem pendentes.
- A nova captura de transição
  `out/emulator_evidence/visual_ko_20260915T053734Z/opening_title_transition.mp4`
  registra 49,1 s a 60 fps desde o primeiro framebuffer. Abertura e título
  aparecem como cenas separadas com fade para preto entre elas; a pequena linha
  colorida de uma amostra intermediária não reapareceu no frame estável e ficou
  registrada como hipótese de tearing do capturador, não como causa comprovada.
- A sessão dirigida de combate em
  `out/emulator_evidence/visual_ko_20260915T054142Z/` validou o caminho real da
  sonda: 16 HIT e 1 PROJECTILE, 41 sprites ativos, 72 links VDP e 17 sprites
  por scanline. GUARD, THROW, colisão DOUBLE e KO não ocorreram nessa entrada;
  a ausência é uma lacuna de cobertura, não um zero promovido como regra.

- O diagnóstico de runtime foi estendido para HPRB schema 6: depois do consumo
  central, a ROM acumula contagens saturantes de eventos HIT/GUARD/THROW,
  projétil, colisão DOUBLE e KO, além do tamanho do último tick. O decoder
  mantém schemas 1–5 fechados para não aceitar tamanho/layout cruzado.
- Build SGDK/Wine atual: ROM
  `713cfe0751e49706bd6d75e844e114032963dfe04e228e02bc475f8b4e792e7b`;
  suíte de contratos: 16 arquivos, log
  `out/logs/continuation_p04_runtime_event_probe_suite.log`.
- A sessão `out/emulator_evidence/visual_ko_20260915T052605Z/` gravou SRAM
  decodificada em `hprb_probe_report.json` (schema 6, 1770 amostras, DMA
  máximo 8288, 17 sprites/scanline). Como foi uma sessão curta sem golpes
  confirmados, os contadores de combate ficaram zero; captura dirigida não
  zero e revisão de budget/visual permanecem pendentes.

- `CombatEvent` agora distingue `BODY`, `PROJECTILE`, `THROW` e `DOUBLE`, além de
  carregar `sourceInstance`. `COMBAT_EVENTS_EMIT` permanece compatível para o
  caminho corporal; projéteis usam `COMBAT_EVENTS_EMIT_SOURCE` e incrementam
  uma instância estável por disparo, reiniciada no round.
- A condição de vitória da FSM foi corrigida de uma cadeia com `||` para
  exclusão com `&&`; o vencedor não recebe novos pontos a cada tick durante a
  animação de vitória.
- Suíte host/estática: 14/14. Build SGDK/Wine: ROM
  `30c7eb6fb2b1c66a9cbe092a49055395cc6b2e61bc34cfcb420a78a0069641f0`, relatório
  `out/logs/continuation_p04_event_source_victory_build.log`.
- O contrato de origem foi validado em C real; ainda falta captura instrumentada
  da colisão simultânea/projétil no emulador e o gate visual/auditivo.
- O percurso exploratório foi recapturado com a ROM `30c7eb6fb2b1c66a9cbe092a49055395cc6b2e61bc34cfcb420a78a0069641f0` em
  `out/emulator_evidence/visual_ko_20260915T045157Z/`; o manifesto registra
  `config_sha256: null` e áudio não capturado.
- No caminho de projétil defendido, o evento `GUARD` agora é emitido antes do
  chip; a atualização de vida fica centralizada e não pode escapar para a rota
  direta. Build posterior: ROM `54333ae8109bb499dab9a3fae109e2886c313dceb0e1c698cbda8f0b4e7f6dcb`,
  captura correspondente ainda pendente.
- A nova sessão exploratória foi concluída em
  `out/emulator_evidence/visual_ko_20260915T045548Z/`, com o mesmo SHA da ROM;
  ela confirma apenas o percurso básico e mantém revisão visual/auditiva e
  instrumentação de eventos como pendências.
- Agarrões aceitos agora têm tipo `COMBAT_EVENT_THROW` próprio, consumido como
  acerto confirmado para combo/medidor. Build posterior: ROM
  `dfdb6cb181c22f9d3e151a694abdad3cf0a66ca1ec3b0664c9a346b3e3e3b3cd`; captura
  correspondente em `out/emulator_evidence/visual_ko_20260915T050018Z/`.
- O cenário Showdown recebeu refinamento Lloyd/medoid em quatro passagens,
  reduzindo o erro RGB médio de `199.9134` para `177.0296` sem ultrapassar 768
  tiles. ROM posterior: `93c94843df3843628ac8d32fedf24edbcf50bc9660122cd4c0bf9c4ef72763f0`;
  a captura `out/emulator_evidence/visual_ko_20260915T050519Z/01_round.png`
  mostra melhora, mas não fecha o gate visual porque ainda há quadriculação.
- O bug gráfico do HUD foi isolado: o segmento de vida tinha preto no índice 0
  e magenta no índice 1. O asset foi normalizado para índice 0 transparente e
  amarelo no índice 2 da PAL1 compartilhada. A captura
  `out/emulator_evidence/visual_ko_20260915T051731Z/combat_005.png` não mostra
  mais o padrão corrompido durante a atualização da vida. ROM:
  `74d402437490e31b0dc95332bf2b30c98ccae19a9b18f85154cbc03fd4b268ac`;
  gate visual independente e budget permanecem pendentes.

## 2026-09-15 - StageDefinition e regressão do loader

- A seleção de cenário foi normalizada em `inc/stage.h`/`src/stage.c`. Cada
  `StageDefinition` declara id, nome, dimensões do `Image`, piso, limites de
  luta e suporte a 240 linhas; `src/init.c` e `src/select.c` consomem a mesma
  definição. A abstração reduz divergência entre cenários, mas não encerra a
  medição de câmera ou DMA.
- O build SGDK/Wine atual é a ROM
  `5cca18f17931b9d6eae814b542a5e1f4775a3059642e7c444ea3f7fa9e4cebc6`, com
  17 arquivos de teste host/estático aprovados. A captura
  `out/emulator_evidence/visual_ko_20260915T054808Z/` alcançou título,
  seletor e round e teve o HPRB schema 6 decodificado.
- Essa rota de regressão não produziu eventos de combate; a evidência dirigida
  anterior continua sendo a sessão com 16 HIT e 1 PROJECTILE. O relatório novo
  mede DMA máximo de 8288 B contra 7782 B nominais NTSC, mantendo o status
  `cabe com recuo`. O cenário Showdown ainda usa fixture de estudo do
  laboratório e aguarda revisão visual independente por causa da repetição de
  tiles.
- Lição canônica registrada em
  `doc/curation/2026_09_15/stage_definition_loader.json` (L071).

## 2026-09-15 - Física respeita limites do cenário

- O último acoplamento de largura foi removido de `src/physics.c`: quatro
  verificações de empurrão e o clamp final passaram a ler
  `gLimiteCenarioE/D`, derivados do `StageDefinition`, sem mudar o contrato de
  coordenadas do cenário atual.
- Build SGDK/Wine: ROM
  `28f7f94cc9a1ba6fb317a61f2afa4e49c09bb5b61b7900827688f294975aec0d`;
  contrato estático, build e captura
  `out/emulator_evidence/visual_ko_20260915T055443Z/` passaram. O HPRB schema 6
  segue confiável, com 8288 B de DMA máximo e zero eventos nessa rota curta.
- A mudança é uma generalização de runtime, não uma aprovação visual do
  Showdown: a repetição de tiles, PAL, áudio e o excesso de DMA ainda precisam
  de revisão/medição dedicadas.

## 2026-09-15 - Stage 2 512x256 e captura dirigida

- O conversor de `data/source_art/stage2_swamp/` agora preserva a fonte em
  512×256, sem o crop vertical anterior. O asset indexado continua com índice
  BG_B zero reservado, cores na grade Mega Drive e 768 tiles residentes; o
  relatório atualizado registra o novo hash de saída.
- `StageDefinition` marca BGB2 como compatível com conteúdo PAL/240. O
  harness `tests/capture_visual_ko.py --stage2 --probe-short` alterna o palco
  com P1 C (`D` no mapa padrão do BlastEm), chega ao round e deixa
  `00_stage2_selected.png`, `01_round.png` e o manifesto de cenário no bundle
  `out/emulator_evidence/visual_ko_20260915T060720Z/` e o manifesto declara
  `stage: BGB2` com o mesmo hash da ROM.
- ROM atual:
  `2a3516df1dc4150134b3e12ef64c3b7ab42aef29da25cd6610d2b003e82df13e`.
  A sessão confirma integração do palco, não qualidade artística: o cenário
  ainda mostra repetição de tiles, e o HPRB mantém DMA acima do envelope
  nominal (8288/7782 B). Câmera PAL, áudio e cobertura de combate continuam
  pendentes.

## 2026-09-15 - Regressão PAL do Stage 2

- A ROM `2a3516df1dc4150134b3e12ef64c3b7ab42aef29da25cd6610d2b003e82df13e`
  foi executada em PAL com o cenário BGB2 512×256. O bundle fresco é
  `out/emulator_evidence/visual_ko_20260915T061029Z/`.
- HPRB schema 6: 1470 amostras, 8288 B de DMA máximo, 40 sprites ativos,
  56 links VDP e 17 sprites por linha. O envelope PAL do decoder é 17408 B,
  então esta sessão passou o eixo de budget PAL. O resultado não distingue
  altura 224/240 porque esse campo ainda não é exportado pela sonda.
- O PAL valida integração do palco e residência dos sprites, não sensação de
  velocidade, mix de áudio ou qualidade visual. Esses eixos continuam
  pendentes, assim como a correção do excesso de DMA no envelope NTSC.

## 2026-09-15 - Probe de altura efetiva e H240

- `src/hamoopig_runtime_probe.c` passou ao HPRB schema 7, anexando a altura
  efetiva do VDP depois de `FUNCAO_SCREEN_HEIGHT_APPLY()`. Schemas 1–6 seguem
  decodificáveis; o novo teste `tests/test_hprb_screen_height_contract.py`
  impede regressão de tamanho/endian.
- A ROM `4df3e5b9bbc1441c34595d3c464a54d41480dfb154f1d7e3bbaed884bee5c503`
  foi executada em PAL com BGB2, H240 ligado pelo menu e overlay TEXT desligado.
  O bundle `out/emulator_evidence/visual_ko_20260915T062548Z/` reporta
  `schema: 7`, `screen_height: 240`, 2430 amostras e DMA 9568 B dentro do
  envelope PAL.
- A captura finalmente separa PAL-224 de PAL-240 por dado observado, não por
  inferência. Isso não fecha o budget NTSC, áudio ou a revisão da arte
  quadriculada.

## 2026-09-15 - Back-pressure de uploads de sprites e pior frame NTSC

- O excesso NTSC não vinha apenas do HUD: os lutadores eram criados com
  `SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE`, permitindo que frames grandes
  acumulassem DMA além do envelope de 7782 B. A correção habilita a proteção
  de capacidade do SGDK em `src/player.c`, `src/player_ken.c` e
  `src/player_musgo.c`.
- Combo/HITS e mensagens são overlays transitórios; suas cópias de tilemap
  agora usam CPU em `src/hud.c`, sem competir na fila DMA com os tiles de
  sprites. O comportamento visual precisa de revisão temporal, pois um frame
  pode ser aplicado no tick seguinte quando a fila está cheia.
- Build atual: ROM
  `c90aaa166634a7435665be43e111ff20b34bd13bec6721536a9f9964c2b7f372`, log
  `out/logs/continuation_p10_sprite_backpressure_build.log`.
- Evidência NTSC Stage 2: `out/emulator_evidence/visual_ko_20260915T063954Z/`;
  HPRB schema 7, altura 224, 1710 amostras, DMA máximo 7008 B, 17 sprites
  por linha, decisão `cabe`. O contrato H240/PAL anterior continua em
  `out/emulator_evidence/visual_ko_20260915T062548Z/`.
- A lição canônica é `doc/curation/2026_09_15/ntsc_dma_backpressure.json`
  (L074). Budget NTSC/PAL passou; falta revisão visual independente, áudio e
  cobertura dirigida de eventos de combate.

## 2026-09-15 - PAL-240 confirmado na ROM com back-pressure

- A primeira captura PAL-240 da ROM nova perdeu uma borda de navegação e
  terminou em 224 linhas; a repetição sem instância BlastEm residual confirmou
  `screen_height=240` diretamente no HPRB schema 7.
- Bundle fresco:
  `out/emulator_evidence/visual_ko_20260915T064928Z/`. O manifesto mantém
  `stage=BGB2`, `h240_requested=true` e o mesmo SHA da ROM
  `c90aaa166634a7435665be43e111ff20b34bd13bec6721536a9f9964c2b7f372`.
- O probe mediu 2520 amostras, 8160 B de DMA, 40 sprites ativos, 56 links VDP
  e 17 sprites por linha; o envelope PAL de 17408 B passou. A captura ainda é
  rota curta de integração, sem eventos de combate dirigidos ou revisão
  sensorial.

## 2026-09-15 - Proprietário estável de sprite e reset de HUD

- `PLAYER_STATE` deixou de liberar/recriar o metasprite do lutador em cada
  transição. `PLAYER_SET_SPRITE` conserva um objeto por lutador e usa
  `SPR_setDefinition`, posição, atributos e frame inicial.
- `hud_sync_segment_tile` acompanha o tile proprietário nos aliases P1/P2 e
  `hud_window_off` roda antes de `hud_window_init` em cada reset de round.
- Build: ROM `146116cd3a05a6c8b84bf28cda92f47f7444b29df65532a9381443fc67d51f6c`,
  log `out/logs/continuation_p09_stable_sprite_hud_reset_build.log`.
- Stage 2 chegou ao round na rota limpa `out/emulator_evidence/visual_ko_20260915T072159Z/`;
  o stress `out/emulator_evidence/visual_ko_20260915T072642Z/` alcançou KO
  sem o fatal anterior de alocação do HUD. A reentrada automática pós-KO ainda
  não foi validada pelo harness.
- Lição canônica: `doc/curation/2026_09_15/hud_alias_and_stable_fighter_sprite.json` (L075).

## 2026-09-15 - Reset de round: liberação dos cantos de hitbox e detector de vida

- O build `82501c1e6a41e19bdd42317c239ca4d9eb5f2e9bc690460e68122c40262e8871`
  (log `out/logs/continuation_p09_rect_release_build.log`) libera os 16
  `Rect*` de hitbox/debug no início de `FUNCAO_INICIALIZACAO()`. Esses handles
  sobreviviam ao round e podiam consumir o pool até a próxima criação do HUD.
- A captura fresca `out/emulator_evidence/visual_ko_20260915T074433Z/` mostra
  `combat_025.png` com a faixa de vida de P2 ausente durante KO,
  `special_reset_health.png` com vida restaurada no round seguinte e
  `after_combat.png` já dentro da nova abertura de luta. Não houve tela fatal.
- O harness `tests/capture_visual_ko.py` passou a medir somente a faixa superior
  da vida; antes somava a segunda linha da barra especial e produzia falso
  “P2 ainda cheio”. A barra especial continua independente e visível abaixo.
- Regra: qualquer sprite de debug criado durante a luta precisa ser liberado
  no commit de round, e os detectores de evidência devem separar cada linha do
  HUD por contrato geométrico, nunca por uma ROI que mistura métricas.

## 2026-09-15 - Candidato Showdown alinhado à referência solicitada

- `res/gfx/showdown.png` foi regenerado a partir de
  `rascunho/showdown_native_crop_preview.png`, com 768 representantes e quatro
  iterações de medoid. O MSE RGB caiu para 177.0296 contra 201.3010 do recorte
  anterior do laboratório.
- Build `14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440`:
  `out/logs/continuation_p11_showdown_preview_refine_build.log`. A captura
  `out/emulator_evidence/visual_ko_20260915T075323Z/01_round.png` confirma o
  palco Showdown no runtime.
- Isso é uma melhoria mensurável de conversão e vínculo asset→ROM, não uma
  aprovação artística. A aparência quadriculada precisa de revisão visual
  independente comparando referência, PNG convertido e framebuffer.
- Lição canônica: `doc/curation/2026_09_15/showdown_reference_preview_refinement.json` (L076).

## 2026-09-15 - Handoff e matriz integrada P10/P11

- Foram criados `doc/engine_quickstart.md`, `doc/engine_extension_guide.md` e
  `doc/controls_and_options.md` com os comandos reais, owners atuais e limites
  de proveniência. `tests/reproduce_p11_isolated.py` copiou os manuais para uma
  árvore mínima, verificou os tokens dos três manuais e compilou/probou
  `StageDefinition` com `-Wall -Wextra -Werror`; build SGDK e emulador continuam
  gates separados. Evidência: `out/p11_isolated_reproduction_20260915T094345Z/`.
- `tests/generate_qa_matrix.py` gera
  `doc/engine/p10_qa_matrix.json` com as 36 combinações ordenadas de lutadores,
  cenários e regiões. Todas começam como `not_run`; isso torna o furo explícito
  em vez de transformar duas capturas em cobertura total.
- `tests/test_qa_matrix_contract.py` protege a cardinalidade e a honestidade do
  manifesto. P10 segue em andamento até o budget worst-frame e as revisões
  visual/auditiva; a execução probe real dos 36 casos e o estresse de 100
  resets de cena já estão vinculados ao SHA atual.
- Captura integrada no SHA atual `14d8ac73...`: BGB2 NTSC, Ryo vs Musgo,
  21 HIT, 1 KO, 7008 B DMA enfileirados, 68 links VDP e 17 sprites/scanline.
  O caso foi marcado `runtime_status=passed` e `pending_visual_review`; os
  demais 35 casos possuem probes/HPRB próprios na matriz, mas não são promovidos
  a gameplay completo por inferência.
- Captura de áudio isolado no mesmo SHA em
  `out/emulator_evidence/visual_ko_20260915T080946Z/`: 48 kHz estéreo,
  36,05 s, RMS -28,29 dBFS, pico 5816, sem clipping e rota PulseAudio
  verificada. Isso prova sinal/roteamento; audição do mix continua pendente.

## 2026-09-15 - Degrau de qualidade do Showdown medido e promovido

- Candidatos de 864 e 1024 tiles reduziram o MSE RGB para 138.7790 e 84.8591,
  respectivamente. O candidato de 864 foi buildado e observado no BlastEm sem
  disparar o guard `TILE_SPRITE_INDEX=1020`; o de 1024 continua rejeitado.
- A ROM `da6f6e1b…bd9d7` recapturou P10, o reset de cena e INTRO/FADE com o
  candidato de 864. A melhoria seguinte ainda exige streaming/cache de padrões
  por janela para ultrapassar 864 sem corromper sprites em runtime.
- Lição atual: `doc/curation/2026_09_15/showdown_864_tile_promotion.json` (L086).

## 2026-09-15 - Matriz P10 de seleção vinculada à build histórica

- `tests/run_p10_matrix.py` passou a materializar o `default.cfg` empacotado do
  BlastEm e injetar apenas um cluster P2 versionado em
  `tests/blastem_qa.cfg`. Isso permite selecionar P1/P2 sem trocar a ROM ou
  inferir pares a partir de outra captura.
- As 36 combinações ordenadas agora possuem manifestos frescos na ROM
  `14d8ac73b4cf176d9c933e9645c52d6b8237a72e3fe26fa956d0e38ec320d440`; o
  relatório agregado é `out/logs/p10_matrix_runner_report.json` e a matriz é
  `doc/engine/p10_qa_matrix.json`.
- A repetição `probe-short` alcançou os 36 casos e gerou um
  `hprb_probe_report.json` decodificado por caso; dois casos PAL precisaram de
  uma segunda captura por estabilização do framebuffer, sem falha final.
- O resumo HPRB da matriz mediu, por região, NTSC máximo de 7024 B enfileirados,
  59 sprites VDP e 17 sprites/scanline; PAL máximo de 8024 B, 57 sprites VDP
  e 17 sprites/scanline. Ambos ficam no envelope DMA observado; o pior-frame
  independente e a revisão sensorial continuam pendentes.
  Todos os casos permanecem `pending_visual_review`; isso não prova gameplay
  completo, áudio, sensação temporal ou um reset de round durante a luta. O teste de
  integridade rejeita manifestos ausentes, SHA divergente, HPRB inválido ou
  par solicitado diferente.

## 2026-09-15 - Estresse de reset de cena P10

- `tests/run_scene_reset_cycles.py 100` completou 100/100 soft resets no
  BlastEm com a ROM de referência anterior `66a47938...e3c3`; processo permaneceu vivo, janela
  presente e capturas não vazias nos ciclos 1, 50 e 100.
- Manifesto: `out/emulator_evidence/scene_reset_cycles_20260915T111652Z/manifest.json`.
- Limite explícito: esta rota valida apenas boot/reset de cena; não exercita o
  reset de round em uma luta nem aprova visual, áudio ou estabilidade de gameplay.

## 2026-09-15 - P10 revalidado no SHA intermediário do retorno ao título (histórico)

- O runner `tests/run_p10_matrix.py --include-observed --probe-wait=1` recapturou
  os 36 pares, cenários e regiões na ROM `b74d2bcebfce1d7e9e831e90a6e029f610ddd5c30e95bb5f62e52d53f6a3aca1`.
- Dois casos PAL inicialmente não exportaram SRAM HPRB; ambos passaram após
  `--retry-failed --probe-wait=2`. O resumo final decodificou 36/36 casos:
  máximo global 8.024 B DMA enfileirados, 41 sprites ativos, 60 sprites VDP e 17/scanline.
- Todos permanecem `pending_visual_review`; probes curtos não provam gameplay
  completo, audição ou suavidade temporal.

## 2026-09-15 - Probe de combate mínimo na matriz P10 (histórico)

- A matriz foi recapturada com entradas bounded `P1: Right+Q x3; P2: J+X x2`.
  Os 36 casos no SHA `b74d2bcebfce1d7e9e831e90a6e029f610ddd5c30e95bb5f62e52d53f6a3aca1`
  produziram pelo menos um HIT cada; o HPRB foi decodificado sem falhas.
- Máximos observados: 8.024 B DMA enfileirados, 41 sprites ativos, 60 links
  VDP e 17 sprites por scanline. Isso é telemetria de rota, não prova de luta
  completa, KO, guarda/projétil/agarrão/multi-hit, reset de round ou qualidade.
- Evidência: `out/logs/p10_matrix_hprb_summary.json` e lição
  `doc/curation/2026_09_15/p10_combat_probe_current_rom.json` (L083).

## 2026-09-15 - Retorno observável de INTRO/FADE (histórico)

- A ROM `b74d2bcebfce1d7e9e831e90a6e029f610ddd5c30e95bb5f62e52d53f6a3aca1`
  adiciona `INTRO` e `FADE` ao menu e uma rota B real em SELECT e AFTER_MATCH.
- Bundle `out/emulator_evidence/title_return_20260915T112050Z/`: INTRO/FADE
  OFF retornou diretamente ao título; ON retornou pela abertura; cinco capturas
  não vazias e manifesto com a sequência de entrada foram registrados.
- O runtime/route está provado; suavidade temporal, legibilidade e qualidade
  visual continuam `pending_visual_review`.
- ROM histórica desta validação: `b74d2bcebfce1d7e9e831e90a6e029f610ddd5c30e95bb5f62e52d53f6a3aca1`; a cadeia atual usa o SHA 6c6d registrado acima.


## 2026-09-18 — Curadoria incremental canonica

- O usuario autorizou assimilar o aprendizado acumulado com o projeto incompleto. Oito principios entraram na referencia canonica `tools/sgdk_wrapper/.agent/references/hamoopig_engine_learning_2026_09_18.md` (caminho relativo ao workspace), acionada por quatro skills existentes.
- ROM auditada: `4c273bd5803913acbd62a55e6386f7c1e50e4d707cd14fd2fdd6c715ffa0ebbc`. Referencias a outros hashes em narrativas anteriores sao historicas; nao substituem esta identidade. Runtime e ROM nao alterados; nenhuma nova captura nesta rodada.
- 33/33 testes de host, self-check HPRB, 84/84 casos de schema e quatro quick_validate passaram. Framework global continua com falhas preexistentes, comparadas em `doc/curation/2026_09_18/framework_comparison.json`. Contexto passou; higiene possui dois tipos de blocker.
- 36 casos P10 permanecem `pending_visual_review`; nao equivalem a partidas aprovadas. Permanecem pendentes robustez de eventos, budget completo, sincronismo visual, streaming real, qualidade visual/audio e higiene. Sem promocao AAA.
- Diagnostico, plano, inventario e logs: `doc/curation/2026_09_18/curadoria_aprendizado_canonico.md`.

## 2026-09-19 — Separação de carga de entrada e CPU sustentada no VLAB

- `src/hamoopig_runtime_probe.c` continua registrando `SYS_getCPULoad()` e jitter como diferença absoluta entre cargas consecutivas e agora separa o I/O do próprio probe, restringe o agregado sustentado à cena de luta e exporta a carga de entrada em `words[52..54]`. A chamada `HAMOOPIG_probeFightInit()` marca a inicialização e uma cauda de 16 frames para não contaminar a média móvel de 8 frames.
- A ROM foi recompilada pelo wrapper SGDK/Wine no SHA `c17af26742c71840462b9da9f7f2037993ff81eb8dd6170f92b3f3916af4ce86`, 2.490.368 bytes.
- BlastEm selou `out/emulator_evidence/visual_ko_20260919T061243Z/evidence_manifest.json`; `combat_179.png` mostra a cena DRAW no frame final. VLAB registra 7350 amostras, 320x224, DMA máximo 7016 B, 17 sprites/scanline, 22 sprites ativos, zero `over_budget_frames`, `max_cpu_load=139%` no frame 6869 e `max_cpu_jitter=7`; a janela ficou em torno de 60 fps, mas 139% ainda impede declarar performance sustentada estável.
- A carga de entrada foi isolada como `initialization_cpu_peak=744%` no frame 7050. O pool oculto de hitbox/eixo também deixou de consumir sprites em produção (`RELEASE=1`), reduzindo o pico de sprites observado para 22.
- O bloco VLAB observou o pool de sprites `[1020,1440)` e o stage `[1,1010)`; isso é residência de cena observada, não prova de cada upload dinâmico de sprite.
- A captura com `--audio` em `visual_ko_20260919T054050Z` falhou porque o harness não encontrou um stream monitorável único; não há aprovação de áudio para este SHA.
- Claim permanece `prototype_partial`, `ready_for_aaa=false`; a próxima ação causal é reduzir/bisectar o pico de CPU antes de qualquer promoção, além de rebindingar validação/revisão e fechar os gates de governança.


## 2026-09-18 — Diagnostico visual comparativo com imagens GAME

Oito referencias fornecidas pelo usuario foram vistas e preservadas com hash em `rascunho/inputs/quality_reference_board_2026_09_18/`, somente para referencia de qualidade. Comparadas a quatro capturas persistidas da ROM 4c273bd5, ao codigo e aos recursos ativos. Diagnostico e plano: `doc/curation/2026_09_18/visual_gap/diagnostico_visual_comparativo.md`; prancha: `comparison_board.html` nessa pasta; backlog: 14 itens em seis marcos mais expansao posterior.

Conclusao: base ja possui sprites grandes, barras, combo, rounds, selecao, camera, hitpause e SFX. Prioridades sao identidade/legibilidade do HUD, retratos, poses especificas em lugar de aliases genericos, reautoria do palco, profundidade/animacao ambiental e integracao sonora. Camera existente nao deve ser confundida com parallax; imagens paradas nao comprovam movimento, FPS ou voz. Auditoria de arte: 132 ativos sem issues criticos nas verificacoes executadas; fontes em data com pendencias nao bloqueiam o grafo ativo. Sem runtime/ROM alterados, nova captura, aprovacao visual final ou promocao AAA.

## 2026-09-19 — Primeiro slice visual do seletor no ROM atual

- Implementado em `src/select.c` e `res/gfx.res`: fundo autoral `title_backdrop`, hierarquia `FIGHTER SELECT`, P1/P2, nomes, cursores e escolha de palco; a carga do fundo usa PAL0/BG_B e não adiciona sprite por frame.
- Build SGDK/Wine concluído em 18/09, ROM `10242282b1ccedccbf37bcad0579b13298009bb67bfe24678bebe0f0486020a6`, 2.490.368 bytes. Contratos host passaram: menu, HUD identity/segments, stage definition e stage selection.
- BlastEm real no mesmo SHA: `out/emulator_evidence/visual_ko_20260919T022950Z/00_select.png` mostra Ryo/Musgo e `STAGE SHOWDOWN`; manifesto limita a alegação ao framebuffer do seletor. A tentativa de troca para BGB2 produziu frame transitório vazio e não foi promovida.
- Probe curto BlastEm no mesmo SHA: cena 10, 1.710 amostras, 2 eventos/2 hits; HPRB máximo 7.040/7.782 B DMA, 41 sprites ativos, 61 links VDP e 17 sprites/scanline. HSEM registrou ataques, mas não guard, projétil, agarrão ou KO. Isso é telemetria diagnóstica, não gameplay completo.
- Estado: `buildado` e `testado_em_emulador` para o escopo observado; não `pronto`, `validado_budget` completo ou AAA. Bloqueios restantes: VDP dump/metrics canônicos ausentes no selador, audio mix sem nova captura, freshness warning (5 stale/1 missing), higiene com 2 blockers, proveniência de assets inválida e revisão visual independente.

## 2026-09-19 — VLAB e bundles BlastEm selados no SHA atual

- `src/hamoopig_runtime_probe.c` agora exporta o bloco visual canônico `VLAB` em
  SRAM `0x200`, com snapshot de métricas e 64 palavras de CRAM. Os blocos
  diagnósticos HPRB/HSEM permanecem em `0x500`/`0x580`, preservando os decoders
  existentes.
- Build SGDK/Wine passou no SHA `662ca81644013736f0ac01d0365d277d36b8f5b463192278532a5c7aedfe75dd`.
  O bundle canônico `out/evidence/blastem/` foi selado no BlastEm real com ROM,
  screenshot, SRAM, `visual_vdp_dump.bin` e `runtime_metrics.json`; a janela
  reportou 61,0 fps no snapshot de título. Isso não equivale a estabilidade
  sustentada.
- A luta no mesmo SHA foi selada em
  `out/emulator_evidence/visual_ko_20260919T025744Z/`: cena BGB2 observada,
  990 amostras, 1 hit, pico de 7008/7782 B DMA, 41 sprites ativos, 60 links VDP
  e 17 sprites/scanline. HSEM registrou ataques, sem guard, projétil, throw ou
  KO nessa rota curta. É telemetria de execução, não cobertura de partida.
- A captura do seletor em
  `out/emulator_evidence/visual_ko_20260919T025537Z/00_select.png` prova a
  composição P1/P2/Ryo/Musgo e `STAGE SHOWDOWN`. A tentativa de capturar o
  texto `BGB2` ainda retornou `SHOWDOWN`, embora o probe de luta tenha confirmado
  a cena BGB2; portanto a troca de palco permanece residual até haver um
  framebuffer de seleção estável.
- Resíduos honestos: partida completa e revanche, KO/time-over/draw cobertos por
  input normal no SHA atual, audição crítica do mix, carga CPU/jitter no VLAB
  (campos ainda não instrumentados), revisão visual/auditiva independente,
  freshness/higiene/proveniência e validação de recursos. Claim atual:
  `prototype_partial`, sem promoção AAA.

## 2026-09-20 — Renovação P10 e limite da recaptura semântica

A matriz P10 foi renovada contra a ROM SHA-256
`8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`:
`36/36 pending_visual_review`, `0 failed`, com resumo em
`out/logs/p10_matrix_hprb_summary.json` e máximos medidos de 48 sprites VDP,
12 sprites por scanline e 8176 bytes DMA enfileirados. A rota semântica atual
está em `out/emulator_evidence/visual_ko_20260920T001624972891Z-3780703/`,
mas não produziu SRAM/HSEM e seus quadros finais exibem overlay de pausa/debug;
ela não é aprovação visual nem telemetria semântica fechada. Permanecem P2 por
teclado, escuta crítica, revisão visual dos 36 casos, áudio, pior frame combinado
e revisão independente. Estado: `prototype_partial_current_sha`.

A recaptura seguinte, em `out/emulator_evidence/visual_ko_20260920T002156365973Z-3833796/`, corrigiu o fallback do harness para START exclusivo do P2 e removeu o overlay de pausa/debug. Ela ainda não produziu SRAM/HSEM nem um quadro inequívoco do projétil; permanece evidência de combate visual inconclusiva para aprovação semântica.

Título, opções e retorno também foram recapturados no SHA atual em `out/emulator_evidence/title_return_20260920T002445Z/`; as telas ficaram não vazias e sem overlay de debug, mas continuam sujeitas a revisão visual independente.

A seleção P2 foi recapturada com `--p1=ryo --p2fighter=ken --select-only` em `out/emulator_evidence/visual_ko_20260920T002637710025Z-3870542/selected_final.png`: Ryo/P1 e Ken/P2 aparecem com cards, retratos e palco BGB2 no SHA atual. A pendência específica de cursor P2 por teclado foi resolvida; confirmação dupla completa e mirror-match ainda requerem prova dedicada.

## 2026-09-20 — Prova same-ROM do golpe especial

- A rota isolada `tests/capture_visual_ko.py --specials-only` foi executada no
  BlastEm com teclado real, sem injeção de estado, gerando o bundle
  `out/emulator_evidence/visual_ko_20260920T033026169476Z-462317/` para a ROM
  SHA `8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`.
- O confronto visual do frame
  `special_only_p1_try0_4.png` mostra o projétil autoral de Ryo em voo, com
  impacto legível, HUD e BGB2 presentes. HSEM registrou 204 frames de projétil
  P1; HPRB registrou 3 eventos de projétil e 3 hits.
- O mesmo relatório mediu 7424 B de DMA enfileirado, 48 sprites VDP e 12
  sprites/scanline, dentro dos limites nominais. Não houve guarda ou throw:
  ambos ficaram em zero nesta rota; isso não autoriza claim de cobertura total.
- Status permanece `prototype_partial_current_sha`, `revise_before_growth` e
  `ready_for_aaa=false`. A próxima ação causal é fechar rotas dedicadas de
  guarda e agarrão e confrontá-las em imagem, mantendo abertos áudio, hitstop,
  cobertura de poses, pior quadro combinado e revisão sensorial de todas as telas.

## 2026-09-20 — Prova same-ROM do agarrão

- A rota `--throw-only` foi isolada do fallback de START que abria o painel de
  debug e repetida no BlastEm com teclado real. O bundle válido é
  `out/emulator_evidence/visual_ko_20260920T034410560385Z-533030/`.
- O frame `throw_only_contact_4.png` mostra Musgo suspenso no agarrão, Ryo em
  recuperação e `2 HITS` legível. HSEM registrou 68 frames de throw P1 e HPRB
  registrou 2 eventos de throw/2 hits; o SHA continua o da ROM atual.
- A medição de envelope ficou em 7424 B DMA, 48 sprites VDP e 12
  sprites/scanline. A rota anterior com `PAUSE/DEBUG` foi descartada.
- Guarda continua sem prova positiva, com zero frames/eventos nas rotas válidas.
  Status segue `prototype_partial_current_sha`, `revise_before_growth` e
  `ready_for_aaa=false`; ainda faltam hitstop, cobertura integral, áudio,
  pior quadro combinado e revisão sensorial de todas as telas.

## 2026-09-19 — Sinal de áudio e ajuste da captura do palco

- Nova captura BlastEm no SHA atual em
  `out/emulator_evidence/visual_ko_20260919T031410Z/` foi selada com ROM,
  screenshot, SRAM, VLAB/VDP dump e métricas. HPRB registrou 3540 amostras,
  1 hit, 7008/7782 B DMA, 41 sprites ativos, 60 links VDP e 17/scanline;
  HSEM registrou ataques P1/P2, sem guard/projétil/throw/KO.
- O WAV isolado foi auditado: 48 kHz estéreo, 11,55 s, sinal presente, rota
  verificada, RMS `-27,27 dBFS`, pico `6199` e zero clipping. O relatório é
  `audio_signal_report.json`; não é aprovação de mix, pois a audição crítica
  ainda não foi realizada.
- A ferramenta de captura agora aguarda 1,5 s após o C de seleção e, em
  `--select-only`, não envia A/X: move os cursores e fotografa antes de
  confirmar. A captura `out/emulator_evidence/visual_ko_20260919T032203Z/`
  mostra o seletor completo com Ryo/Musgo e `STAGE BGB2`; junto da captura
  SHOWDOWN anterior, isso fecha a observação visual de dois palcos no mesmo
  SHA. V10 continua `implemented_partial` por confirmação/desconfirmação ainda
  não capturadas.

## 2026-09-19 — Partida completa, KO e revanche observados

- A rota normal de input em
  `out/emulator_evidence/visual_ko_20260919T032351Z/` observou Ryo vs Musgo
  no BGB2, dois zeramentos de vida (`combat_025`/`combat_050`), duas telas de
  resultado `PLAYER 1 WINS` e `rematch_round.png`. O manifesto mantém o claim
  como playtest real e não transforma o detector de amarelo em prova isolada.
- Bundle selado com o SHA atual: HPRB/HSEM e VLAB vinculados a
  `662ca81644013736f0ac01d0365d277d36b8f5b463192278532a5c7aedfe75dd`.
  HPRB: 3180 amostras, 42 hits, 2 KO, DMA máximo 7016/7782 B, 71 links VDP,
  17 sprites/scanline, decisão `cabe`. Os picos DMA e scanline foram frames
  diferentes e permanecem separados.
- V13 passa a `implemented_partial`: ciclo partida/revanche e envelope VDP
  observados, mas não há aprovação de mix por escuta, CPU/jitter instrumentados,
  pior frame combinado ou revisão visual/gameplay/auditiva independente.

## 2026-09-19 — Confirmação e desconfirmação do seletor

- `out/emulator_evidence/visual_ko_20260919T032851Z/` registra uma rota
  específica de estado: `01_p1_confirmed.png` mostra `OK` no slot P1 após A;
  `02_desconfirmed_title.png` mostra o retorno ao título após B, sem entrar em
  `SCENE_FIGHT`.
- O harness agora separa essa prova do playtest e não usa inputs A/X no modo
  `--select-only`. V10 continua parcial porque a confirmação visual explícita
  do P2 ainda não foi capturada.

## 2026-09-19 — Time-over DRAW selado no primeiro terminal

- A ROM pós-instrumentação tem SHA `a602c21d29607ff36d34355c92081833ec7060c9ebc2433c134e33daaa69ec38` e foi recompilada pelo wrapper SGDK/Wine.
- BlastEm real selou `out/emulator_evidence/visual_ko_20260919T042046Z/evidence_manifest.json` com `combat_175.png`, SRAM, VLAB/VDP dump e runtime metrics. A foto mostra `DRAW` com o relógio em `00`.
- HDBG sticky da mesma SRAM registra `scene=10`, `clock=00`, `P1/P2 state=615/615`, `energiaBase=96/96` e `gResultTimer=11`; HPRB registra zero hits/KO. Isso fecha DRAW real por time-over, não inferência por espera.
- O harness passou a copiar a ROM sem preservar mtime antigo e a manter o primeiro terminal HDBG; a rota de timeout ainda é evidência de playtest, não aprovação de gameplay.
- Resíduos honestos: confirmação explícita do P2, escuta crítica do mix, CPU/jitter instrumentados, pior frame combinado, proveniência/freshness/validação de recursos e revisões independentes continuam abertos. Claim permanece `prototype_partial`, sem AAA.

## 2026-09-19 — Correção VLAB e recaptura DRAW no SHA vigente

- A revisão independente encontrou e confirmou uma escrita extra no bloco VLAB: o trecho `words[24..42]` emitia 20 palavras para 19 posições, deslocando a paleta CRAM. Removida a escrita extra em `src/hamoopig_runtime_probe.c`; `tests/test_visual_probe_contract.py` agora verifica a contagem, e o self-check do sealer passou.
- Build canônico SGDK/Wine passou no SHA `3ca61393cc365661dec9a3a1ee1b753ee27dd319bc972d0abb201cadb31a663a`, 2.490.368 bytes.
- Bundle DRAW fresco e selado em `out/emulator_evidence/visual_ko_20260919T045421Z/evidence_manifest.json`: screenshot `combat_175.png`, SRAM, VLAB/VDP dump e `runtime_metrics.json`, todos vinculados ao mesmo SHA. A imagem mostra `00 DRAW`; HDBG registra `scene=10`, clocks `0/0`, estados `615/615`, energias `96/96` e `gResultTimer=8`.
- HPRB/HSEM do mesmo SRAM: 7020 amostras, DMA máximo `7008/7782 B`, 40 sprites ativos, 17/20 sprites por scanline, picos DMA e scanline no frame 569, zero hits/guard/throw/projétil/KO. O bundle mantém `performance_claim=unproven`, pois CPU/jitter não são instrumentados e 60,2 fps é apenas snapshot.
- A confirmação P2 foi recapturada no mesmo SHA em `out/emulator_evidence/visual_ko_20260919T050147Z/02_both_confirmed.png`; a sessão também contém P1 confirmado e retorno por B.
- O harness `--draw` agora envia B como saída de emergência do free-step antes da espera; isso evita que uma borda START residual congele a rota sem alterar a ROM.
- Claim permanece `prototype_partial`, `ready_for_aaa=false`. Resíduos: gameplay completo no SHA vigente, audição crítica, validação/freshness/higiene/proveniência, técnica/VRAM formal e pior-frame combinado.

## 2026-09-19 — Validação canônica e revisão independente fechadas

- `validate_resources.ps1 -CloseoutGate` foi executado contra o SHA vigente. Resultado: 130 checks, 18 erros e 66 warnings; o relatório atual é `out/logs/validation_report.json` (SHA `7a486f849c30eddb4d6c871561bc746cdbdccbcf19ec3a6b4460fd1e285f6460`). Os blockers são explícitos: higiene/nomenclatura/GDD, visual gate, áudio ausente, evidência de emulador stale/session mismatch, tile budget por código, technique/provenance, tilemap/palette reports, freshness e scene closeout.
- A revisão independente foi rebindingada ao relatório atual e validada em `doc/independent_quality_review_validation.json`: `status=passed`, `growth_decision=revise_before_growth`, `quality_claim=unproven`, `ready_for_aaa=false`. Foram mantidos como riscos bloqueadores a residência VRAM não medida, CPU/jitter não instrumentados, pressão DMA/scanline próxima do teto e a higiene/proveniência/claims incompletos.
- A iteração permanece `prototype_partial`; nenhuma promoção AAA ou declaração de pronto é autorizada por esta rodada.

## 2026-09-19 — Iteração visual HUD/combate no SHA c6019980

- O HUD recebeu retratos recortados em close, chapa vazia de vida autoral convertida para 128x16, camada de dano recente e especial azul em faixa distinta. A profundidade foi corrigida para deixar a chapa visível atrás do preenchimento.
- O palco padrão passou a ser BGB2, e o seletor passou a exibir `ROSTER // VS`, nomes, P1/P2, estágio e previews Ryo/Musgo. Captura: `out/emulator_evidence/visual_ko_20260919T122736Z/00_select.png`.
- Build SGDK/Wine passou com ROM de 2.490.368 bytes e SHA `c6019980e96f08492844d85407c1df5e3f67da22a5a0606cda58ad27b99231ba`.
- BlastEm no mesmo SHA observou 59,9–61,1 fps, dano de 8 para 3 segmentos, `5 HITS`, spark e reação em `out/emulator_evidence/visual_ko_20260919T122930Z/`; a rota semântica está em `out/emulator_evidence/visual_ko_20260919T123310Z/`.
- Contratos visuais/estáticos selecionados passaram: visual probe, HUD identity, special bar, KO defeat, stage budget, title menu, stage selection, special event, time-over, scene reset e combo.
- Bloqueios honestos: a rota normal do SHA atual ainda não zerou a vida nem capturou KO/revanche; o letreiro/message font segue placeholder; parallax/ambiente do BGB2, áudio auditado por escuta, pior frame combinado e proveniência completa continuam abertos. O auditor de proveniência segue bloqueado por manifest histórico incompleto/ativos não declarados; a suíte P10 possui fixtures com SHA antigo.
- A rota `--timeover` no mesmo SHA chegou ao relógio `00` e exibiu `PLAYER 1 WINS` em `out/emulator_evidence/visual_ko_20260919T124155Z/after_timeover_observation.png`; isto comprova a tela de resultado, mas o detector/HDBG não fechou o terminal semântico e não deve ser chamado de DRAW.

## 2026-09-19 — KO autoral integrado e recapturado

- O letreiro de KO deixou de depender apenas do atlas pequeno: foi criado o
  `data/source_art/hud/generated_ko_banner_v01.png`, convertido por
  `data/source_art/hud/convert_ko_banner.py` para `res/sprite/hud/ko_banner.png`
  em 48x24, com transparência, PAL1 e proveniência declarada.
- A ROM recompilada pelo wrapper tem SHA
  `58199903b60bd69e1255cfdc8dcb5fa7c992879f838729972f884e74ab667efc`.
  BlastEm recapturou o fluxo no mesmo SHA em
  `out/emulator_evidence/visual_ko_20260919T131512Z/`: `zero_1_result.png`
  mostra o banner autoral sobre o KO, `combat_025.png` mantém combo/FX e
  `rematch_round.png` comprova o reset visual da revanche.
- O frame continua estável no playtest agressivo, entre 60,0 e 61,1 fps nos
  samples capturados. Isso não fecha ainda mix de áudio, CPU/jitter, pior frame
  combinado, proveniência histórica completa ou revisão independente.
- O claim permanece `prototype_partial`, `ready_for_aaa=false` e a decisão
  continua `revise_before_growth`; title/select, profundidade/ambiente e
  especial em estado pronto ainda precisam de iteração confrontada com imagem.

## 2026-09-19 — Title polido e evidência rebindada ao SHA final da rodada

- `src/title.c` passou a usar um card de menu azul com moldura de acento
  vermelho escuro, mantendo o conteúdo autoral do title e separando-o melhor do
  fundo. A rota title → options → select → title foi recapturada em
  `out/emulator_evidence/title_return_20260919T130908Z/`.
- O playtest agressivo pelo lado P2/Musgo fechou o KO no mesmo SHA final em
  `out/emulator_evidence/visual_ko_20260919T131512Z/`, incluindo
  `zero_1_result.png`, `rematch_round.png` e samples de 59,7–61,1 fps.
- O SHA vigente é
  `58199903b60bd69e1255cfdc8dcb5fa7c992879f838729972f884e74ab667efc`.
  A proveniência agora retorna `verdict=OK` (somente aviso histórico de
  `title_logo_overlay` fora do `.res`).
- A entrega continua `prototype_partial`: o Musgo legado está explicitamente
  em placeholder, o palco ainda não tem parallax/ambiente medido e áudio,
  CPU/jitter, pior frame combinado e revisão independente não estão fechados.

## 2026-09-19 — Seleção reautorizada, paleta do Musgo corrigida e evidência unificada

- `src/select.c` passou a compor cartões BG_A azul profundo com moldura vermelha
  escura, mantendo previews, nomes, P1/P2, estágio e comandos separados da área
  dos lutadores. A seleção final está em
  `out/emulator_evidence/visual_ko_20260919T135125Z/selected_final.png`.
- `data/source_art/musgo/convert_musgo.py` deixou de promover resíduos de matte
  rosa/púrpura para a paleta compartilhada e passou a preservar, no mesmo
  conversor, os sprites `.res` das poses `fall_v1`, `defeat_v1` e `victory_v1`.
  O contrato `test_ko_defeat_contract.py` voltou a passar após a regeneração.
- Build canônico SGDK/Wine e evidência final usam a ROM de SHA
  `fe5d55de3b713d9279b93abbe0194112e250bb10b84a70b76cc9746552267db8`.
- BlastEm recapturou combate, KO e revanche em
  `out/emulator_evidence/visual_ko_20260919T134925Z/`; o banner KO, a pose
  terminal, vida zerada e `ROUND 1` da revanche foram observados entre 60,0 e
  61,1 fps. Título/opções/retorno foram revalidados no mesmo SHA em
  `out/emulator_evidence/title_return_20260919T135151Z/`.
- Status permanece `prototype_partial`, `ready_for_aaa=false`. Continuam
  abertos: confirmação P2 no bundle final, áudio auditado por escuta, CPU/jitter,
  pior quadro combinado, parallax/ambiente do palco, cobertura completa de
  animações e revisão independente de tipografia/arte.

## 2026-09-19 — Ambiente animado BGB2 e recaptura no SHA vigente

- O palco BGB2 recebeu `spr_stage_water_glint`: quatro frames 16x8 derivados de
  `res/gfx/bgb2.png`, três instâncias PAL0 de profundidade 1 e seis tiles
  máximos. O runtime atualiza os glints a cada oito frames e os desliga ao
  trocar de cena; não há terceiro BG nem claim de parallax.
- O builder, a origem e o hash foram registrados em
  `doc/asset_provenance_manifest.json`; saída `res/sprite/stage/water_glint.png`
  tem SHA `30751a6b7fd4c631a232bd78331530fa76f909a4f0f6a5310e7664db9e508ad9`.
- Build SGDK/Wine passou com ROM de 2.490.368 bytes e SHA
  `1f2120842f8820fecbadc4acd9265830aa7f8b493fa75f0abc577b0eb7b02312`.
- BlastEm vinculou combate, KO, revanche e vídeo em
  `out/emulator_evidence/visual_ko_20260919T142855Z/`; title/options/select/retorno
  foram recapturados em `out/emulator_evidence/title_return_20260919T143530Z/`.
  Samples observados ficaram aproximadamente entre 59,2 e 61,1 fps, sem o
  crash do primeiro protótipo de recurso.
- Os sete contratos visuais/estáticos continuam passando. Status permanece
  `prototype_partial`, `ready_for_aaa=false`: cobertura completa de animações,
  golpe assinatura/projétil, mix auditado, CPU/jitter, pior quadro combinado,
  parallax real e revisão independente ainda não estão fechados.

## 2026-09-19 — Legibilidade da identidade no HUD

- `src/hud.c` passou a desenhar os nomes e estrelas usando PAL2/PAL3 já
  carregadas pelos lutadores. PAL1 usava índice-15 preto para texto, fazendo
  `RYO`/`MUSGO` desaparecerem contra o palco; a correção não adiciona sprites,
  tiles ou uma nova paleta CRAM.
- Build SGDK/Wine: ROM de 2.490.368 bytes, SHA
  `9027cb528431b3e43ea6e735acf3792ebf42cdc518163dd4af0abcbacf7ec668`.
- BlastEm confirmou title/options/select/retorno em
  `out/emulator_evidence/title_return_20260919T150646Z/` e HUD/ROUND/combat
  parcial em `out/emulator_evidence/visual_ko_20260919T150750Z/`, com samples
  entre 59,2 e 61,1 fps.
- A captura agressiva da nova identidade não chegou a zero de vida; não há
  claim de KO/revanche para este SHA. A evidência terminal anterior permanece
  explicitamente separada até uma rota KO válida ser recapturada.

## 2026-09-19 — Ciclo terminal e áudio capturados no SHA do HUD

- O harness agressivo passou de 240 para 360 passos, mantendo zero visível e
  detector terminal como gate. A ROM `9027cb528431b3e43ea6e735acf3792ebf42cdc518163dd4af0abcbacf7ec668`
  agora tem KO em `out/emulator_evidence/visual_ko_20260919T151652Z/zero_1_result.png`
  e revanche em `rematch_round.png`.
- O mesmo SHA teve áudio isolado capturado em
  `out/emulator_evidence/visual_ko_20260919T151846Z/emulator_audio.wav`:
  48 kHz estéreo, 41 s, média `-28,2 dB`, pico `-14,9 dB`, sem clipping.
  Isso fecha presença de sinal e não fecha audição crítica de mix.
- O ciclo visual segue `prototype_partial`: title/options/select, HUD com nomes
  legíveis, ROUND/FIGHT, palco BGB2, glints, combate, KO e rematch estão no
  mesmo SHA; poses completas, golpe assinatura/projétil autoral, CPU/jitter,
  pior quadro combinado, parallax real e revisão independente permanecem abertos.

## 2026-09-19 — Fatia visual confrontada no hash final

- HUD: duas placas autorais pré-renderizadas de vida, retratos, nomes, vitórias,
  relógio e rótulos `SP` com PAL2/PAL3. O HPRB final mediu 14 sprites ativos,
  50 links e 12 sprites por scanline.
- Seleção: `src/select.c` usa o índice 15 real da fonte SGDK para texto branco.
  A captura final é `out/emulator_evidence/visual_ko_20260919T182730Z/selected_final.png`.
- Especial: folhas compactas autorais `spr_ryo_100`/`spr_ryo_710` e projétil
  `spr_ryo_701` foram observados em movimento e impacto em
  `out/emulator_evidence/visual_ko_20260919T182850Z/semantics_projectile_06.png`.
  O estado de vitória 612 usa a folha compacta 611 para evitar buraco de tiles.
- Runtime: troca de definição de sprite aplica aquecimento de dois ticks e
  mantém o ator oculto até o DMA assentar. O quadro de reset fica limpo, sem
  corrupção; `after_reset_*` confirma a cena estabilizada.
- ROM final: `895642485a6269293ef3f812befc1aef7e61c711db78c7286dc5449d5f47dec5`,
  2.490.368 bytes. BlastEm final está em
  `out/emulator_evidence/visual_ko_20260919T183010Z/`; título/retorno em
  `out/emulator_evidence/title_return_20260919T182758Z/`.
- HPRB: DMA máximo `7520/7782 B`, delta de sprite `5880 B`, 14 sprites ativos,
  50 links VDP, 12/20 por scanline, 21 hits, 1 projétil e 1 KO; medição
  confiável, estados `within_nominal` e decisão `cabe`.
- Oito contratos e o self-check HPRB passaram. Status permanece
  `prototype_partial`, `ready_for_aaa=false`: áudio isolado do mesmo hash está
  em `out/emulator_evidence/visual_ko_20260919T183824Z/emulator_audio.wav`
  (48 kHz, 40,55 s, pico -15,3 dB, sem clipping), mas ainda não há audição crítica,
  cobertura completa de poses,
  parallax/multi-plano real, CPU/jitter sustentados, pior quadro combinado ou
  revisão independente fechados.

## 2026-09-19 — Recaptura same-ROM após correção de especial e telas

- ROM vigente: `933ce216c18e6cc8ee74125426d524a3e3e493a1b73e8ec92fd5df0c91e647ac`,
  2.490.368 bytes, construída pelo wrapper canônico.
- HUD recebeu folhas autorais opacas para os estados vazio/preenchido do especial;
  `out/emulator_evidence/visual_ko_20260919T191729Z/zero_1_settle.png` mostra
  KO, retratos, nomes brancos, relógio e barras sem buracos pretos.
- Título/opções/retorno foram recapturados em
  `out/emulator_evidence/title_return_20260919T191950Z/`; seleção do elenco em
  `out/emulator_evidence/visual_ko_20260919T191928Z/`.
- O golpe assinatura e o projétil foram recapturados no mesmo SHA em
  `out/emulator_evidence/visual_ko_20260919T192457Z/semantics_projectile_06.png`.
  HSEM registrou 67 frames de fireball e HPRB registrou 2 projéteis, 2 hits e 1
  guarda; `measurement_trustworthy=true`, DMA `7424/7782 B` e scanline `12/20`.
- Áudio isolado do mesmo SHA está em
  `out/emulator_evidence/visual_ko_20260919T192047Z/emulator_audio.wav`:
  48 kHz estéreo, 84 s, pico `-12,70 dBFS`, RMS `-27,71 dBFS`, sem clipping.
  A análise confirma integridade objetiva do sinal, não substitui escuta crítica.
- Status continua `prototype_partial`, `ready_for_aaa=false`. Permanecem abertos:
  cobertura integral das animações, reautoria final/parallax do palco, pior quadro
  combinado, CPU/jitter sustentados, escuta crítica do mix e revisão independente.
  O aquecimento de sprites ainda oculta o ator por um quadro transitório durante
  algumas trocas de definição; isso deve ser revisado antes de qualquer promoção.

## 2026-09-19 — Closeout operacional da fatia visual

- `scene_closeout_gate.ps1` foi executado sem rebuild/captura adicional usando a
  ROM observada; relatório: `out/logs/scene_closeout_gate_report.json`, status
  `warn`, seis etapas concluídas, quatro warnings e uma etapa pulada.
- A validação final ficou em `out/logs/validation_report.json` com `errors=4` e
  `warnings=85`. Persistem blockers de higiene/nomenclatura, juiz visual,
  áudio declarado sem auditoria, evidência de emulador stale/mismatch,
  residência de tiles carregados por C não medida e relatórios de técnica/cena
  ausentes.
- `out/logs/freshness_audit_report.json` está presente e reporta dois artefatos
  opcionais stale (`runtime_metrics` e `emulator_session`); não há artefato
  obrigatório ausente. Isso é warning operacional, não aprovação AAA.
- A revisão independente foi rebindingada ao SHA vigente e validada: `status=passed`,
  mas `growth_decision=revise_before_growth`, `quality_claim=unproven` e
  `ready_for_aaa=false`.

## 2026-09-19 — Seleção refinada e confronto dos dois palcos no mesmo SHA

- O build vigente permanece `df648176a73fa1ff67ba939f21226fc07d7da53e685da8d00eb986a3e56509fa`, com 2.490.368 bytes. A seleção foi refinada em `src/select.c`: cards P1/P2, frames quente/frio, retratos, nomes, estado `LOCKED/SELECT`, palco e comandos ficaram legíveis no framebuffer real.
- BlastEm confirmou seleção, confirmação dupla, BGB2 e retorno de opções/título: `visual_ko_20260919T203208Z/`, `visual_ko_20260919T204301Z/`, `visual_ko_20260919T204612Z/` e `title_return_20260919T205316Z/`.
- A fatia completa `visual_ko_20260919T203454Z/` mostrou ROUND/FIGHT, dano, hit-spark, KO autoral, vitória e 59,9–61,1 fps na janela. A rota semântica `visual_ko_20260919T203704Z/` mostrou projétil/impacto e guard; HSEM mediu 75 frames de fireball e 108 frames de guard. HPRB da sessão semântica mediu 7.424/7.782 B DMA, 50 sprites VDP e 12 sprites/scanline; a fatia de KO registrou 41 hits e 2 KO.
- O capturador foi corrigido para usar host X como P2 A, esperar `SCENE_SELECT` antes de rotular o frame e distinguir explicitamente `--showdown` de BGB2. Isso removeu falso negativo de confirmação e falso rótulo de palco; os testes `test_title_menu_contract.py` e `test_stage_selection_contract.py` passaram.
- `validate_resources.ps1 -CloseoutGate` foi reexecutado contra a ROM vigente: 137 checks, 18 erros e 73 warnings. Os blockers permanecem honestos: higiene/GDD, gate visual, áudio/relatórios, identidade/freshness de evidência, residency de tiles, técnicas e relatórios de tilemap/paleta. O claim continua `prototype_partial`; não é `pronto` nem AAA.
- O pedido/plan/review independente foi rebindingado aos artefatos atuais; `quality_review_router.py validate-report` passou com `growth_decision=revise_before_growth`, `quality_claim=unproven` e `ready_for_aaa=false`. A passagem valida a integridade do parecer, não promove a qualidade visual a AAA.

## 2026-09-19 — Bundle canônico BlastEm selado no SHA vigente

- A rota host foi regenerada para Linux/Flatpak BlastEm com alvo real `SCENE_TITLE=1`; a tentativa anterior com alvo `10` foi rejeitada honestamente por `runtime_scene_id=1` e não foi usada como prova.
- A captura canônica `out/evidence/blastem/` agora contém screenshot, SRAM, `visual_vdp_dump.bin`, ROM e `runtime_metrics.json`, todos no SHA `df648176a73fa1ff67ba939f21226fc07d7da53e685da8d00eb986a3e56509fa`; sessão `blastem-linux-20260919T211315Z-3033329`.
- `fresh_evidence_bundle_audit.ps1` e `finalize_emulator_evidence.ps1` passaram com `status=ok`, `seal_status=sealed` e `semantic_capture_valid=true`. A métrica de janela foi `59,7 fps` no instante; performance sustentada continua não provada.
- O bundle prova identidade/frescor e a tela observada no título; não substitui as capturas de gameplay já vinculadas nem autoriza promoção AAA.

## 2026-09-19 — Matriz P10 recapturada no SHA vigente

- Corrigido o runner `tests/run_p10_matrix.py` para emitir `--showdown` explicitamente nos 18 casos do parque; antes, esses casos podiam capturar BGB2 e apenas rotular SHOWDOWN.
- O harness recebeu diretórios únicos por microssegundo/PID e fallback local somente para o `default.cfg` quando o Flatpak fica temporariamente indisponível; nenhuma ROM ou evidência selada foi sobrescrita.
- Todos os 36 casos P10 foram recapturados com manifestos no SHA `df648176a73fa1ff67ba939f21226fc07d7da53e685da8d00eb986a3e56509fa`; `test_p10_evidence_integrity.py` passou. O status permanece `pending_visual_review`, pois probe/HPRB não substitui revisão visual, sonora ou sensorial.
- Resumo atual: `out/logs/p10_matrix_hprb_summary.json`, 36 casos, DMA máximo `8176 B`, 14 sprites ativos, 47 links VDP e 12 sprites/scanline.

## 2026-09-19 — Fatia visual real confrontada com as referências

- A fonte v02 do palco BGB2 foi reautorizada como raster original persistido em
  `data/source_art/stage2_swamp/generated_stage2_v02.png`, com prompt e hash
  registrados. A conversão produziu `res/gfx/bgb2.png` com 960 tiles únicos;
  `out/logs/scene_tilemap_conversion_report.json`,
  `out/logs/per_tile_palette_conflict_report.json` e
  `out/logs/tilemap_flag_report.json` medem a tradução. O runtime continua
  honestamente `compare_flat` em BG_B: não há claim de parallax real.
- O KO recebeu `res/sprite/hud/ko_banner_big.png`, folha autoral derivada em
  escala inteira e carregada como `spr_hud_ko_banner` 12x6. O quadro real
  `out/emulator_evidence/visual_ko_20260919T221705403442Z-3268880/zero_1_result.png`
  mostra KO dominante, combo, HUD, retratos, palco e pose de vencedor.
- A seleção refinada e a confirmação dupla foram vistas no mesmo SHA em
  `out/emulator_evidence/visual_ko_20260919T230347890426Z-3470306/`; a rota
  semântica `out/emulator_evidence/visual_ko_20260919T222523465819Z-3299137/`
  mostrou o projétil Ryo e FX de impacto em quadros reais.
- O áudio do mesmo SHA tem rota isolada e sinal objetivo em
  `out/emulator_evidence/visual_ko_20260919T225923273658Z-3454647/`:
  48 kHz estéreo, 43,8 s, sem clipping. Isso não fecha a escuta crítica do mix.
- A matriz P10 foi forçada a renovar os 36 casos, incluindo NTSC/PAL, os dois
  palcos e todas as combinações de elenco. `test_p10_evidence_integrity.py`
  passou; todos permanecem `pending_visual_review`, pois probe não é aprovação
  sensorial. O resumo atual mede DMA máximo `8176 B`, 14 sprites ativos,
  64 sprites VDP e 12 sprites por scanline.
- O bundle canônico BlastEm foi selado na sessão
  `blastem-linux-20260919T230119Z-3462151`; screenshot, SRAM, VDP dump e ROM
  têm SHA `723ba8c2b69555965800f5e09dccc5fa9d5f90ff7194d3d5d0c9a2a1c7498454` e
  `out/evidence/blastem/freshness_report.json` está `ok`.
- Status permanece `prototype_partial` e `ready_for_aaa=false`. Permanecem
  abertos: cobertura integral de animações/aliases, parallax multi-plano real,
  pior frame combinado com áudio, CPU/jitter sustentados, escuta crítica,
  residência completa de tiles carregados por C, higiene/proveniência completa
  e aprovação independente de qualidade.
- O auditor de proveniência foi corrigido para o schema canônico e agora retorna
  `verdict=OK`, com apenas três warnings de símbolos históricos fora dos `.res`;
  não há mais blocker de proveniência declarada nesta etapa.
- Título, opções e retorno foram recapturados no mesmo SHA em
  `out/emulator_evidence/title_return_20260919T231045Z/`; a página de opções
  preserva a mesma moldura/paleta do título e o manifest confirma a identidade
  da ROM.

## 2026-09-19 — Terminais autorais de Ken e prova no BlastEm

- Fontes autorais persistidas em `data/source_art/ken/` foram convertidas para
  `res/sprite/ken/victory_v1.png` (96x128) e `defeat_v1.png` (128x96), com
  transparência, grid 8x8 e paleta indexada de Ken.
- Ken agora liga 611/612 à vitória e 570/615 à derrota; Musgo usa sua derrota
  autoral em 615. O build passou no SHA
  `8ac1bda70511fbd395af9a3fa3f49ca356e39dec31254b8f336f96a0a405e506`.
- BlastEm observou Ken vencedor em
  `out/emulator_evidence/visual_ko_20260919T232926387580Z-3579731/zero_1_result.png`.
  A captura inversa foi encerrada sem claim após não produzir dano; seleção P2
  por teclado continua pendência de recaptura. Status permanece
  `prototype_partial`, sem promoção AAA.

## 2026-09-20 — Prova same-ROM de guarda

- A rota `--guard-only` foi ajustada para lançar o projétil antes de P2 segurar
  o recuo, evitando que o defensor caminhe para fora da janela de contato. O
  bundle válido é `out/emulator_evidence/visual_ko_20260920T035134604414Z-571565/`.
- O frame `guard_only_06.png` mostra sparks do bloqueio sem dano visual. HSEM
  registrou 76 frames de guarda P2 e 36 frames de projétil P1; HPRB registrou
  1 guard, 1 projétil e 0 hits.
- Envelope same-ROM do probe: 7424 B DMA, 61 sprites VDP e 12 sprites/scanline.
  Especial/projétil, guarda e agarrão agora têm provas isoladas; isso não fecha
  hitstop, cobertura integral, áudio, pior quadro combinado nem revisão sensorial.
- Status permanece `prototype_partial_current_sha`, `revise_before_growth` e
  `ready_for_aaa=false`.

## 2026-09-20 — Recaptura após câmera de impacto no SHA 640c3223

- A ROM vigente é `640c3223ec5b674af237e7ed31895540c5b7e7e5e6d4acce2376345b5f06cf90`.
  O runtime agora aplica tremor curto de câmera somente a eventos de combate
  aceitos; BG_A/HUD ficam fixos e a posição dos lutadores acompanha o palco.
- Especial same-ROM: `out/emulator_evidence/visual_ko_20260920T041415021491Z-688336/special_only_p1_try0_2.png`.
  O projétil é visível; HSEM mede 117 frames e HPRB mede 2 projéteis.
- Throw same-ROM: `out/emulator_evidence/visual_ko_20260920T041830157874Z-704017/throw_only_contact_4.png`.
  Musgo aparece suspenso, Ryo em recuperação e `2 HITS`; HSEM mede 68 frames
  de throw P1 e HPRB mede 2 throws/2 hits. Envelope: 7424 B DMA, 48 sprites
  VDP e 12 sprites/scanline.
- Guard same-ROM: `out/emulator_evidence/visual_ko_20260920T040520275634Z-656638/guard_only_05.png`.
  O impacto tem sparks e não reduz a vida; HPRB mede 1 guard/0 hits.
- Esses bundles provam resposta semântica isolada e o novo tremor de impacto,
  mas não promovem a qualidade geral. Título, seleção, KO, áudio e P10 ainda
  precisam de recaptura no mesmo SHA; status segue `prototype_partial_current_sha`.

## 2026-09-20 — Fatia visual recapturada no SHA 7431b4ee

- Build final desta etapa: `7431b4eed0b5d03039fa8dcb395509d562ae3e79f6308f59a2a2955ec6e3a08d`.
- Seleção validada em `out/emulator_evidence/visual_ko_20260920T051451465479Z-902783/selected_final.png`:
  BGB2 autoral, cards P1/P2, retratos/silhuetas, VS, estágio e comandos legíveis.
- Trilho de vida comprimido para três tiles BG_A com pontas espelhadas no P2;
  HPRB mede 7424 B DMA, 48 sprites VDP e 12 sprites/scanline no especial.
- Especial validado em `out/emulator_evidence/visual_ko_20260920T051517794165Z-904309/`:
  HSEM 203 frames de projétil P1; HPRB 3 projéteis/3 hits.
- Guarda validada em `out/emulator_evidence/visual_ko_20260920T052509378538Z-947249/`:
  HSEM 76 frames e HPRB 1 guard/0 hits; `guard_only_04.png` mostra o impacto.
- KO fechado no SHA final em `out/emulator_evidence/visual_ko_20260920T053546652798Z-1001707/`:
  `zero_1_settle.png` mostra o letreiro `KO`, `after_combat.png` mostra
  `PLAYER 1 WINS`, e HPRB mede 2 KO/41 hits com 7424 B DMA, 66 sprites VDP e
  12 sprites/scanline. A primeira tentativa abriu PAUSE/DEBUG, mas foi descartada.
- Título, opções e retorno recapturados no SHA final em
  `out/emulator_evidence/title_return_20260920T053318Z/`; a página `OPTIONS 3`
  agora está comprovada no framebuffer.
- Throw fechado no SHA final em `out/emulator_evidence/visual_ko_20260920T054131172698Z-1018183/`:
  `throw_only_contact_4.png` mostra Musgo suspenso e `2 HITS`; HSEM mede 68
  frames e HPRB mede 2 throws/2 hits, 7424 B DMA e 12 sprites/scanline.
- Status segue `prototype_partial_current_sha`, `revise_before_growth`, `ready_for_aaa=false`.

## 2026-09-20 — Banner KO transitório e revanche same-ROM no SHA 86b15dac

- O `spr_hud_ko_banner` deixou de ficar alocado e invisível durante toda a
  luta. `hud_ko_banner_set()` agora cria o metasprite apenas ao entrar em KO e
  o libera ao sair da mensagem, preservando o letreiro autoral sem reservar
  links SAT/VRAM no pior quadro normal.
- Build wrapper SGDK/Wine passou com ROM SHA
  `86b15dacb48a7df790cc68dde5b204309089f183ff84c9ad44339a95fa83d147`.
- A captura same-ROM em
  `out/emulator_evidence/visual_ko_20260920T060858990521Z-1139143/` mostra KO
  em `zero_1_settle.png`, resultado `PLAYER 1 WINS` em `after_combat.png` e
  ROUND 1 reiniciado em `rematch_round.png`.
- HPRB/HSEM do mesmo SRAM: 22 hits, 1 KO, DMA máximo 7184 B, 55 links VDP e
  12 sprites/scanline; decisão `cabe`, dentro do envelope NTSC nominal.
- O claim segue `prototype_partial_current_sha`, `revise_before_growth` e
  `ready_for_aaa=false`. As rotas de especial, guarda e throw foram renovadas
  neste SHA: especial tem HPRB nominal e guarda/throw têm frames visuais same-ROM;
  os dois probes isolados não emitiram SRAM e não sustentam claim de telemetria.
  Seleção, título e opções também foram recapturados. P10, áudio crítico,
  cobertura total de animações, pior frame combinado, residência VRAM e revisão
  independente continuam abertos.

## 2026-09-20 — BGB2 candidato de maior detalhe rejeitado no runtime

- A conversão autoral de `data/source_art/stage2_swamp/generated_stage2_v02.png`
  foi comparada nas variantes 1040/1120/1200, mas o BlastEm acionou
  `Fight tiles overlap sprite VRAM` porque esses degraus excedem a reserva viva.
  A promoção foi revertida para 864 tiles, o teto medido compatível com HUD e
  sprite region.
- `tests/test_stage_vram_budget.py` e o contrato de `StageDefinition` passaram;
  a fronteira entre tiles de cenário/HUD e a região de sprites continua guardada
  por `src/init.c`.
- O build SGDK/Wine com o degrau compatível gerou a ROM
  `9509ebbbdc6ea2f6c7036b8fba90f22de400976f119a0d4730a2e7ed6cb5a5f2`.
- BlastEm mostrou palco/KO em
  `out/emulator_evidence/visual_ko_20260920T074931694042Z-1506141/` e o
  especial/FX em `out/emulator_evidence/visual_ko_20260920T080009749866Z-1541958/`.
- Isso é melhoria visual real do palco, não fechamento do diagnóstico: KO,
  seleção, título/opções e pior quadro completo ainda precisam ser recapturados
  neste SHA antes de qualquer claim consolidado.

## 2026-09-20 — Fatia renovada no SHA 7fd291d0

- Seleção e título foram vistos no BlastEm em
  `out/emulator_evidence/visual_ko_20260920T065443726553Z-1313427/`; a seleção
  mostra Ryo/Musgo, retratos, cards e BGB2 no mesmo hash. O título foi registrado,
  mas a tipografia/subtítulo ainda fica em revisão visual.
- A partida completa foi recapturada em
  `out/emulator_evidence/visual_ko_20260920T065617081824Z-1329197/`, com KO,
  resultado e retorno. O bundle de probe same-ROM é
  `out/emulator_evidence/visual_ko_20260920T070346595817Z-1352074/`.
- HPRB do probe mede 2 KO/42 hits, 7424 B DMA, 48 links VDP e 12
  sprites/scanline; decisão `cabe`. HSEM registra 2622 amostras. Isso vincula
  combate e palco ao hash atual, mas não fecha opções, revanche dedicada,
  guarda/throw com SRAM, áudio, P10, todas as poses, residência completa ou
  revisão independente.
- O gate de higiene voltou a `passed` após remover apenas diretórios vazios
  fragmentados que o harness havia recriado; nenhuma captura ou fonte autoral
  foi removida.

## 2026-09-20 — Título, opções e retorno no SHA 7fd291d0

- `tests/capture_title_return.py` recapturou as cinco transições e a página de
  opções em `out/emulator_evidence/title_return_20260920T071630Z/`.
- O manifesto da fatia agora aponta título, opções e retorno para o mesmo SHA do
  palco/combate. A tipografia e a revisão visual independente continuam como
  trabalho de acabamento; não há promoção AAA.

## 2026-09-20 — Front-end e palco recapturados no SHA 9509ebbb

- O título foi reautorado a partir de `room_0_bgb` existente: wordmark em escala
  nativa, retrato do porco ancorado à direita, remoção de pixel solto e cartão
  principal compacto. `OPTIONS 3`, retorno e abertura foram recapturados em
  `out/emulator_evidence/title_return_20260920T075901Z/`.
- A seleção foi recapturada em
  `out/emulator_evidence/visual_ko_20260920T075359233429Z-1521442/selected_final.png`.
  O bundle mostra Ryo/P1, Musgo/P2, retratos, VS, palco BGB2 e comandos.
- O palco BGB2 foi medido novamente: 1200/1120/1040 tiles invadem a reserva
  viva de sprites; 864 tiles é o degrau compatível com `TILE_SPRITE_INDEX=1020`,
  HUD e sprites. O guard deixou de falhar no BlastEm nessa configuração.
- Combate/KO/resultado same-ROM estão em
  `out/emulator_evidence/visual_ko_20260920T074931694042Z-1506141/`; a captura
  oscilou entre 59.5 e 60.8 fps. Especial/FX está em
  `out/emulator_evidence/visual_ko_20260920T080009749866Z-1541958/`.
- O claim permanece `prototype_partial_current_sha`, `revise_before_growth`,
  `ready_for_aaa=false`: áudio auditado, revanche dedicada, guarda/throw no
  mesmo SHA, P10, cobertura total de animações, residência completa e revisão
  independente ainda não estão fechados.

## 2026-09-20 — Forge Crystal e Sound Test no SHA e9e0efc1

- A BGM de luta deixou de usar a referência `bgm_ken_stage`. A nova faixa
  autoral `Forge Crystal` nasce de `data/source_audio/forge_crystal_score.json`:
  8 compassos, 150 BPM, 4/4, A menor, três vozes PSG e loop NTSC de 768 frames.
- O score passou `psg_score.py --self-check`, gerou VGM de 2051 B e a prova
  XGM2 gerou 1028 B, sem PCM. O recurso ativo é
  `res/music/mus_forge_brand.vgm`, carregado por `XGM mus_forge_brand`;
  `src/main.c` inicia a faixa com loop infinito na entrada da luta.
- O Sound Test foi implementado em `src/title.c` e `inc/title.h`: OPTIONS ->
  SOUND TEST; A alterna PLAY/STOP; B retorna a OPTIONS; a faixa é a mesma da
  luta.
- ROM compilada pelo bridge SGDK/Wine:
  `e9e0efc1a8894434911cc6f1054f1c9a072853927a56b983c9eec8c43e12a833`,
  2490368 B. BlastEm percorreu a rota real e capturou o Sound Test em
  `out/emulator_evidence/sound_test_20260920T123713Z/`.
- WAV same-ROM: 18,0 s, 48 kHz estéreo, sinal presente, pico 3648, RMS
  -24,55 dBFS, zero clipping e sink privado confirmado em
  `audio_signal_report.json`. Este é gate de sinal/roteamento; a escuta humana
  do timbre e da emenda do loop continua obrigatória. Status segue parcial,
  sem promoção AAA.
## 2026-09-20 — Diagnóstico visual reproduzido e palco BGB2 estabilizado no SHA 3f6e57d2

- A hipótese de corrupção exclusiva por escrita do HUD em BG_A foi testada: combo,
  especial, relógio, vida e mensagens passaram a possuir WINDOW como owner; o
  palco continuou corrompido, isolando a causa dominante na conversão do BGB2.
- `data/source_art/stage2_swamp/convert_stage2.py` passou a registrar o bloco de
  pré-tile e a variante runtime voltou ao bloco 4: fonte com 1.887 tiles,
  redução medida para 864, 653 tiles efetivos no ResComp. A variante bloco 2
  recuperou detalhe mas reintroduziu quadrados falsos; bloco 3 não inicializou no
  BlastEm e não foi promovido.
- Build bridge SGDK/Wine passou e gerou ROM `3f6e57d22c73128792af82621e0eb9a2e4b922b2d917eb7688051cc3e7d381dd`.
  Captura válida same-ROM: `out/emulator_evidence/visual_ko_20260920T193917471863Z-3875589/`.
- HPRB same-ROM: 2.130 frames, 7.424 B DMA máximo, 13 sprites ativos, 12
  sprites/scanline, 1 hit, sem KO no probe curto; HSEM: 1.145 amostras. O
  envelope nominal cabe, mas isso não é aprovação visual nem partida completa.
- Baseline, separação de sessões inválidas e laudo de tradução estão em
  `doc/curation/2026_09_18/visual_gap/visual_quality_baseline_2026_09_20.json`
  e `stage2_translation_runtime_report_2026_09_20.json`.
- Claim permanece `prototype_partial_current_sha`, `ready_for_aaa=false`.
  Ainda faltam reautoria por módulos/planos sem substituição de tile inteiro,
  HUD/seleção/KO no nível das referências, escuta crítica, partida/revanche
  completa, revisão independente e validação geral sem drift.
## 2026-09-20 — Sound Test recapturado no SHA 3f6e57d2

- A rota real TITLE -> OPTIONS -> SOUND TEST -> PLAY -> loop -> STOP foi
  recapturada em `out/emulator_evidence/sound_test_20260920T201101Z/` na mesma
  ROM vigente.
- `Forge Crystal` produziu WAV estéreo 48 kHz de 17,9 s, pico -19,07 dBFS,
  RMS -24,47 dBFS e zero clipping; a análise objetiva passou. A escuta humana
  de timbre, balanço, loop e mascaramento com SFX continua obrigatória.

## 2026-09-20 — Superfícies autorais integradas no SHA 8e7a34dc

- O seletor usa agora `generated_select_surface_v03.png`, traduzida para 204
  tiles em BG_A na faixa 655..858. BlastEm confirmou a superfície em
  `out/emulator_evidence/visual_ko_20260920T224941749302Z-331917/`.
- BGB2 passou para reuso regional preservador de material: 1.887 tiles de
  origem, 857 efetivos contra orçamento 864. A captura same-ROM em
  `out/emulator_evidence/visual_ko_20260920T230426778949Z-380612/01_round.png`
  mostra água, doca, raízes e silhuetas sem os maiores retângulos falsos.
- A barra de vida usa atlas composto do chassis azul/dourado autoral e dos
  estados de preenchimento persistidos. `WINDOW` foi aberto em tela cheia no
  commit da luta, tornando nomes, `SP`, especial, combo e mensagens visíveis
  sem devolver escrita transitória ao BG_A.
- BlastEm same-ROM observou 60,2 fps no bundle de combate. Sound Test foi
  recapturado em `out/emulator_evidence/sound_test_20260920T231117Z/`: 17,05 s,
  48 kHz, estéreo, sinal presente e zero clipping.
- ROM vigente: `8e7a34dc26ef317f90e5f93b1c00dac6bea25fd59eaf00d94f8e10a3616795dd`.
  Status permanece parcial: revisão independente, escuta crítica, FX/KO,
  partida completa e revanche ainda exigem evidência same-ROM.

- A tentativa de partida longa no mesmo SHA está em
  `out/emulator_evidence/visual_ko_20260920T232720289830Z-454619/`: resets de
  round e estabilidade de 59,9–61,1 fps foram observados, mas o harness perdeu
  contato depois do primeiro reset e não exportou `terminal_capture`. Não é
  prova de KO/resultado; o claim permanece parcial.
- A causa do falso negativo foi isolada: os caps quentes do atlas de vida ficam
  visíveis quando o fill chega a zero, portanto o detector antigo nunca atingia
  `yellow==0`, embora a SRAM mostrasse `P2 energia=0`, `P1 state=611/612` e
  `P2 state=550`. `tests/capture_visual_ko.py` agora separa candidato visual,
  confirmação HDBG, `KO -> AFTER_MATCH` e entrada A de revanche; o limite segue
  finito e sem injeção de estado.
- O primeiro replay mostrou um segundo blocker: `debugTerminalCaptured` era
  global à partida. Ele agora é limpo em `HAMOOPIG_probeFightInit`, preservando
  um HDBG terminal por round e permitindo que o mesmo ROM prove a segunda
  vitória e a transição de revanche.
- Bundle final no SHA `5a99b076be3ae96a382a07676e62b3b8f16d8de59b109a3fd8a886c8dd7d0d1f`:
  `visual_ko_20260920T235500737537Z-543800/`. A sessão registrou dois KO,
  `PLAYER 1 WINS`, retorno A à `ROUND 1` e HPRB same-ROM com 3.750 frames,
  `combat_total_ko=2`, 7.424 B DMA, 50 links VDP e 13 sprites/scanline.
- Sound Test no mesmo SHA: `sound_test_20260920T235813Z/`, PLAY/loop/STOP;
  WAV 48 kHz estéreo, 17,05 s, zero clipping. Escuta humana, barra viva,
  revisão independente e validação geral continuam gates abertos.

## 2026-09-21 — Forge Crystal v2 e evidência same-ROM atual

- `data/source_audio/build_forge_crystal_v2.py` tornou o arranjo reproduzível e
  ampliou a BGM para quatro funções PSG: lead, baixo, contraponto cristalino e
  percussão de ruído. O VGM tem 768 frames NTSC/12,8 s e SHA
  `2449b3d1a8c32e31179b257647b6decb05bcc80d7492ceffb151a4eca066418c`.
- O build canônico SGDK/Wine passou e gerou ROM
  `24262999f2390f14fe131ba3508e70ea348db024bd30cae43edc44082faad958`.
- Sound Test real em `out/emulator_evidence/sound_test_20260921T002424Z/`:
  tela autoral, PLAY/loop/STOP, WAV 48 kHz estéreo, 3290 valores PCM distintos,
  pico 3865, RMS -25,67 dBFS e zero clipping. O relatório continua limitado a
  sinal/rota; audição humana não foi executada.
- Combate com áudio em
  `out/emulator_evidence/visual_ko_20260921T002700587260Z-640941/`: 88,25 s,
  dois KOs, 42 hits, 7424 B DMA, 48 links VDP e 13 sprites/scanline. O bundle
  selado inclui VDP dump, runtime metrics, HPRB/HSEM e hash da ROM.
- VLAB atual registra `max_cpu_load=152`, `max_cpu_jitter=10` e
  `initialization_cpu_peak=1645`; logo, o envelope VDP cabe, mas a performance
  sustentada continua reprovada até reduzir o custo ou medir nova janela.

## 2026-09-21 — Eventos isolados e match same-ROM após ajuste de throw

- O alcance de contato dos estados 800/801 foi alinhado à separação física de
  100 px: a hitbox autoral passou a alcançar o limite legal sem ampliar o
  comando de throw. Build canônico gerou ROM
  `b6f7cd649f829c21555883014721992b04261f0c32b34a620538d0548be7cc88`.
- Probes same-ROM confirmaram: throw `2`, projectile `3`, guard `1`, todos com
  decisão VDP `cabe`; o roteiro de especiais também corrigiu o off-by-one que
  deixava `SPECIAL RULES` sem ser alternado.
- Match completo em `out/emulator_evidence/visual_ko_20260921T005523892270Z-727484/`
  registrou 2 KOs, 42 hits, rematch e áudio isolado de 87,6 s; bundle selado
  com `evidence_manifest.json` e VDP dump.
- Sound Test same-ROM em `out/emulator_evidence/sound_test_20260921T005842Z/`
  confirmou PLAY/loop/STOP e sinal estéreo sem clipping. Escuta humana,
  performance sustentada, barra viva, revisão independente e paridade visual
  com a prancha continuam abertos; status não sobe para AAA.

## 2026-09-21 — Ledger HCAD de lógica versus apresentação

- `src/hamoopig_runtime_probe.c` agora exporta o bloco SRAM `HCAD` em `0x640`,
  sem alterar os contratos VLAB/HPRB/HSEM. Ele conta frames de vídeo, ticks por
  frame, frames sem lógica, frames de dois ticks e commits de apresentação.
- `tests/analyze_hcad_cadence.py` decodifica o bloco e valida os invariantes.
  A captura same-ROM da ROM `edc9a23ff103bc1a7db6182f6f13d95567a464428eb7bdafc2db624ad53df427`
  registrou 7.260/7.260 frames e commits, 7.260 ticks, zero frames sem lógica;
  na luta foram 6.353 frames, ticks e commits.
- Isso fecha a medição da rota NTSC normal contra a hipótese de apresentação
  perdida, mas não fecha PAL/free-step, performance sustentada, escuta humana,
  barra viva ou paridade visual. O projeto permanece parcial.

## 2026-09-21 — Faixa de elenco ampliada e recaptura SHA d9334271

- `data/source_art/select/build_roster_icons.py` agora compõe três retratos
  autorais em frames 24x24 com acentos próprios; `src/select.c` os posiciona
  como faixa central de elenco sem usar pixels desenhados em C.
- A ROM canônica d9334271 foi observada no BlastEm em
  `out/emulator_evidence/visual_ko_20260921T020818911985Z-993126/` (seleção)
  e `out/emulator_evidence/visual_ko_20260921T020916512873Z-996433/`
  (combate/resultado/revanche). O manifesto carrega o relatório HCAD, que
  confirmou 7.980/7.980 commits na janela total e 7.071/7.071 na luta.
- A faixa é uma melhoria visual real, mas permanece `placeholder` até revisão
  independente e comparação com a prancha completa. Paridade visual, escuta
  humana, barra viva e performance sustentada continuam gates abertos.

## 2026-09-21 — Sound Test same-ROM d9334271

- `out/emulator_evidence/sound_test_20260921T021855Z/` confirmou TITLE ->
  OPTIONS -> SOUND TEST -> PLAY -> loop -> STOP com o mesmo SHA d9334271.
- O WAV isolado tem 48 kHz estéreo, 18,15 s, pico 3865, RMS -25,68 dBFS e
  zero clipping. Isso prova rota/sinal; a escuta humana de timbre, loop,
  balanço e mascaramento continua obrigatória antes de qualquer claim de
  “som cristalino” final.

## 2026-09-21 — Contraste de Musgo e ROM current SHA 3c82c14b

- O conversor de Musgo recebeu uma rampa verde/oliva contrastada, mantendo 15
  cores snapped e separando a silhueta do palco BGB2.
- BlastEm same-ROM confirmou seleção em `visual_ko_20260921T023824721736Z-1156410/`
  e combate/resultado/revanche em `visual_ko_20260921T023408630615Z-1134439/`.
  HCAD confirmou 6.060 frames/commits e 5.049 na luta; dois KOs e revanche
  foram observados.
- A janela ainda registrou 58,8 FPS; performance sustentada, impacto comum,
  hierarquia HUD, escuta humana e revisão independente seguem abertas.

## 2026-09-21 — HDBG/HSTR causal e freeze audiovisual no SHA d6b7ea5e

- O ROM efetivamente capturado no BlastEm foi congelado em
  `d6b7ea5e3e43c97b75caff47fa113c841378704b423de50adc2f287732eb9618`,
  2.490.368 bytes. O freeze inclui a rota
  `out/logs/blastem_capture_route_report.json` em
  `out/audiovisual_review/v5/freeze_hstr_v4/freeze_manifest.json`.
- `hamoopig_runtime_probe.c` passou a exportar HDBG schema 2 e o anel HSTR
  schema 1 (`0x700`, 128 registros) durante o especial. HSTR registra estado,
  animFrame, fireball, input, hitPause e presentation frame; não é timestamp
  de scanout nem substitui marcador audiovisual comum.
- A captura real
  `out/emulator_evidence/visual_ko_20260921T085100974673Z-2406057/` foi ingerida
  sem normalização. HCAD fechou 2.970 commits/lógica com zero ticks inválidos;
  a mídia continuou bloqueada por gaps PTS. Isso separa cadência do jogo e
  integridade temporal do arquivo.
- A consulta consecutiva com ROIs em 10,2–13,2 s produziu o candidato
  `gameplay-special-emission-latency-003`: HSTR correlacionado por host-clock
  aponta `state=700/animFrame=4` e fireball ativo perto do frame de mídia 620,
  mas o projétil só aparece visualmente por volta de 631. É um candidato de
  atraso de emissão/render, ainda não causa confirmada; o teste causal pedido é
  recaptura com marcador HSTR/PTS compartilhado.
- O gate qualificado libera apenas identidade, HCAD e visual no escopo de 3 s
  realmente visto; movimento, áudio/sync e cobertura permanecem bloqueados.
  O overhead repetido v3 preserva seis sessões do mesmo SHA, mas só um par
  completo; duas sessões terminaram sem ROM/telemetria. No par utilizável, a
  mediana observada foi +26,729 ms na captura e +580,808 ms na finalização.
  Segue `needs_review`; não há claim de FPS ou overhead estável.

## 2026-09-21 — Fechamento estrito da revisão qualificada

- O gate passou a exigir reviewer, método e lista `tools`, além das flags
  booleanas `video_playback` e `audio_audition`, evidência não vazia em cada
  veredito e intervalos `unexamined_intervals`
  parseáveis. A cobertura declarada precisa coincidir com o complemento
  calculado dos intervalos realmente vistos; `null`, formato inválido ou
  complemento divergente não qualifica o pacote.
- O caso HSTR real foi revalidado em
  `out/audiovisual_review/gameplay_special_hstr_v4_event/audiovisual_gate_event_review_hstr_strict_v8.json`.
  O reviewer é qualificado apenas para a observação visual do evento de 3 s;
  cobertura global, movimento e áudio continuam bloqueados.
- O contrato foi integrado ao wrapper em
  `tools/sgdk_wrapper/ci/test_audiovisual_review_contract.py` e ao
  `run_all_contract_gates.ps1 -Mode schema`; a execução passou 84 testes de
  schema e 3 contratos audiovisuais.
- A ingestão canônica agora produz `audiovisual_ingest_report.json` e os
  achados de gaps usam `media_temporal_integrity`; o nome amplo
  `capture_integrity` não é mais emitido pelo pipeline novo.

## 2026-09-21 — Revisão visual conservadora com pré/pós-contexto

- `query` passou a registrar intervalo do evento separado do intervalo de
  consulta, pré/pós-contexto configurável, segmento de cada frame, PTS, hashes,
  ROIs e mismatch de decodificação. A consulta real usou 0,5 s de contexto em
  cada lado: 241 frames solicitados, 240 decodificados, 181 no evento, 30 no
  pré-contexto e 29 no pós-contexto.
- O candidato `gameplay-special-emission-latency-004` foi regenerado com
  source indices 620/631/652. A inspeção efetiva viu somente esses três frames:
  620 sem projétil; 631 e 652 com projétil. Isso sustenta observação visual
  limitada, não fluidez nem causa confirmada.
- O gate conservador
  `out/audiovisual_review/gameplay_special_hstr_v4_context_v9/audiovisual_gate_event_review_hstr_strict_v9.json`
  registra `qualified=true`, mas somente 0,049998 s observados de 65,125 s;
  movimento, áudio e cobertura continuam bloqueados.

## 2026-09-21 — Vínculo exato ao frame-fonte e achado de gameplay

- `audiovisual_review.py` 2.2.0 substitui o seek ordinal de V2 por filtro
  `ffmpeg select` nos índices retornados pelo `ffprobe`; o relatório declara
  método, filtro, contagem e se o vínculo é exato. Mismatch de decodificação
  permanece não elegível para achado preciso.
- O query v10 do especial decodificou 241/241 frames, com 181 de evento, 30 de
  pré-contexto e 30 de pós-contexto. Foram vistos efetivamente os source
  indices 620, 631 e 652.
- O candidato `gameplay-special-emission-latency-005` correlaciona esses
  frames com HSTR `state=700`, `animFrame=4-5` e `fireball_active=1`: o
  projétil está ausente no 620 e visível nos 631/652. A evidência sustenta um
  possível atraso de feedback/renderização do especial, mas não fecha causa
  nem scanout VDP; o teste causal exige marcador runtime compartilhado.
- O gate v10 mantém `status=blocked`, revisão qualificada apenas para três
  observações visuais, cobertura de 0,049998 s/65,125 s e movimento/áudio/
  sincronismo/integridade temporal bloqueados.

## 2026-09-21 — Overhead pareado com HCAD persistido

- O harness `capture_visual_ko.py` não usa mais a heurística visual do HUD como
  gate do modo `--probe-short`; o resultado HCAD persistido decide se houve
  janela de combate válida. Falhas de precheck ao vivo continuam registradas.
- `capture_overhead_hstr_repeated_v6.json` fechou dois pares no mesmo SHA,
  ambos com 1.530 frames de lógica/apresentação, zero ticks inválidos e
  `fight_video_frames>0`. Medianas com vídeo: boot `-35,586 ms`, captura
  `-0,304 ms`, finalização `+444,197 ms`, total `+459,090 ms`.
- Os deltas de janela de combate foram `-6` e `+2` frames; o laudo não chama
  isso de FPS nem de perda de frames do jogo. O overhead está medido por fase,
  mas a cadência perceptiva permanece fora do claim.

## 2026-09-21 — Evidência de revisão com resolução de arquivos

- O manifesto de revisão agora exige `evidence_root`; cada `evidence_ref` é
  resolvido a partir do diretório do manifesto e deve existir dentro da raiz.
- O teste de contrato cobre referência órfã, raiz ausente e caminho fora da
  raiz; a revisão continua bloqueada quando a evidência não é localizável.
## 2026-09-21 — Pipeline audiovisual rastreável V0–V5

- Implementado `tools/sgdk_wrapper/audiovisual_review.py` com preflight, freeze,
  ingestão por PTS sem CFR, consulta por evento/ROI, achados candidatos e gate
  independente para integridade, cadência, visual, movimento, áudio e cobertura.
- O bundle histórico `visual_ko_20260920T074931694042Z-1506141` foi preservado
  e auditado: 10.822 frames, 194,683333 s, média de metadata ~55,59, `drop=858`,
  três buracos de PTS e WAV separado com delta de duração 466,667 ms. Não é FPS
  do jogo e não recebeu aprovação.
- O agente consultou sequências PNG reais dos eventos 30,8–33,5 s e 120,7–131,9
  s, com ROIs e frames adjacentes. Como a capacidade é image-only, movimento,
  áudio e estética permanecem `needs_review`; cobertura não examinada é explícita.
- V5 capturou no BlastEm com e sem vídeo, preservou relógio/timeline, e uma
  captura audiovisual foi ingerida/indexada/consultada. O par comparável mediu
  842,215 ms de overhead de parede; outra tentativa inválida (HUD ausente) foi
  preservada como `needs_review`.
- Fixtures negativas/positiva e contratos passaram. Esse registro inicial usava
  `capture_integrity` como rótulo amplo; a auditoria posterior corrigiu o modelo
  para `artifact_identity`, `media_temporal_integrity`, `game_cadence` e demais
  eixos independentes. Status do projeto segue parcial/prototype; nenhuma
  promoção AAA.
## 2026-09-21 — Auditoria de escopo audiovisual e correlação de gameplay

- Revisão do pipeline corrigiu o claim: o estado real é infraestrutura parcial
  de captura/indexação/diagnóstico; V0–V5 não equivalem à aprovação audiovisual
  global do jogo.
- `audiovisual_review.py` 2.0 separa `artifact_identity`,
  `media_temporal_integrity`, `av_sync`, `game_cadence`, visual, movimento,
  áudio e cobertura. HCAD pode passar enquanto PTS/drop da mídia falha.
- Revisão hash-bound agora exige reviewer, método, capacidades, hashes,
  intervalos realmente vistos, evidências e vereditos por eixo. Cobertura é
  calculada pela união dos intervalos; `null` e lista vazia sem cobertura real
  são rejeitados.
- Captura especial no SHA vigente gerou 144 amostras, HSEM com 204 frames de
  fogo, HPRB com 3 projéteis e HCAD 3.360/3.360. O candidato
  `gameplay-special-startup-transition-001` correlaciona Down-Right-Q, trecho
  10,2–13,2 s, ROI e telemetria, mas mantém causa não confirmada e encaminha
  recaptura com HDBG/HSEM por frame.
- Overhead faseado mede boot/captura/finalização, porém a repetição ainda teve
  pares insuficientes por falhas de prontidão do HUD; não há estimativa estável.

## 2026-09-21 — Contrato de âncora audiovisual compartilhada

- `audiovisual_review.py` 2.3.0 passou a emitir `synchronization.anchor_contract`.
  `capture_clock` do host é rejeitado como âncora; `av_sync` só pode passar com
  `runtime_media_anchor` hash-bound a runtime, frame-fonte/PTS e amostra de
  áudio, com erro medido e evidência local. O bundle HSTR real não possui esse
  marcador e continua `needs_review`; o gate v11 mantém movimento, áudio,
  sincronismo e cobertura bloqueados.

## 2026-09-21 — Suíte ampla e evidência P10 stale

- A suíte audiovisual direcionada passou em 19 testes. A suíte completa ainda
  falha na coleta de `test_p10_evidence_integrity.py` porque a matriz P10 aponta
  para bundles SHA `8ac1…` e o ROM congelado atual é `d6b7…`; a evidência antiga
  foi preservada e não foi reetiquetada.

## 2026-09-21 — Cadeia V0–V4 reemitida

- V0/V1/V2/V3/V4 foram reemitidos em diretórios novos com
  `audiovisual_review` 2.3.0 e schema 2.2.0, culminando no gate v12.
- O finding `gameplay-special-emission-latency-006` mantém o caso do especial
  como candidato: source index 620 sem projétil e 631/652 com projétil, HSTR
  correlacionado, causa ainda não confirmada por ausência de marcador de scanout.
- A revisão qualificada está estruturalmente válida, mas o gate continua
  bloqueando integridade temporal, sincronismo, movimento, áudio e cobertura.

## 2026-09-21 — Escopo explícito de claims

- O gate V12 agora inclui `claim_scopes`; a liberação visual é explicitamente
  limitada aos três frames vistos, enquanto movimento, áudio e cobertura ficam
  com escopo `none`.
## 2026-09-21 — Marcador compartilhado e rejeição do binder

- `out/marker_probe_v3/rom.bin` usa somente `HAMOOPIG_CAPTURE_MARKER` e tem
  SHA `3797bb8f…adb2a578`; `out/rom.bin` permaneceu `d6b7ea5e…eb9618`.
- `capture_visual_ko.py --rom=...` registra origem/hash; HANC terminal fornece
  contexto runtime (`marker_id=16`, frame 2880), sem ser PTS ou relógio host.
- `analyze_media_marker.py` consultou vídeo `21a019d4…d179ab` e áudio
  `cedfb6b9…52001e8`: 2 candidatos visuais e 209 de áudio. O binder exige
  seleção explícita, reviewer e evidência local.
- O binding candidato foi `needs_review` (100 ms, reviewer/evidência ausentes)
  e o ingest rejeitou sua liberação; gate BlastEm V1 ficou `blocked`, com gap
  PTS de 33,333 ms preservado. Não houve aprovação audiovisual/AAA.

## 2026-09-21 — V14: revisão consecutiva com PTS corrigido

- O pacote V11 tinha intervalos declarados deslocados dos PTS do `query_report`;
  foi preservado e não foi sobrescrito. O pacote V14 corrige a evidência para
  `10,3375–10,5375 s`, source indices consecutivos 620–632, com ROI gameplay
  e hashes do vídeo/áudio/ROM `e533…56eff6fd` / `2b72…74ae4a5` / `d6b7…eb9618`.
- A inspeção efetiva encontrou o projétil ausente em 620/621 e visível pela
  primeira vez em 622. O finding `gameplay-special-emission-latency-007` é
  `candidate_only`, com hipótese de atraso de apresentação, impacto, ROI,
  confiança 0,9 e teste causal dependente de marcador compartilhado; não
  confirma causa, overflow, scanout ou defeito de captura.
- Gate V14: `review_validation.qualified=true`, cobertura observada 0,3071%,
  `artifact_identity` e HCAD liberados nos próprios escopos, `visual_approval`
  liberado somente para `thirteen_consecutive_special_onset_frames_only`;
  integridade temporal, sincronismo, movimento, áudio e cobertura completa
  continuam bloqueados. Projeto segue prototype/technical_demo, sem AAA.
- V2 agora materializa clipe de vídeo FFV1 por `select` de índice-fonte e WAV
  nominal separado, sem reencodar master, CFR, interpolação ou deduplicação.
  No marcador v2 foram confirmados 49/49 frames do clipe e `play_event.sh`; a
  sincronização continua explicitamente não afirmada sem âncora comum.
- `audiovisual_review.py` 2.4.1 com `end-to-end` emitiu `v5_end_to_end_hstr_v14.json`:
  execução V0–V4 cross-checkada (`execution_status=passed`) com cadeia SHA
  completa e revisão `qualified=true`, mas claims finais `status=blocked`.
  O recibo registra captura sem `cadence_probe` como `needs_review`, não como
  FPS ou aprovação, e tem fixture negativo para reviewer ausente.
- O recibo exige ainda vínculo do finding ao `query_report` real e valida que
  seus source frames estão dentro do intervalo consultado; o caso HSTR passou
  com 620–632 dentro de 582–822.
- A revisão formal do código audiovisual está em
  `out/audiovisual_review/code_review_v24.json`, com decisão
  `review_passed_with_risk`: os riscos restantes são limites de percepção e
evidência, não autorização para promover o projeto.
- O binder técnico fechou positivamente no bundle diagnóstico: source frame
  701/PTS 11,683333 s e amostra 560800/48 kHz, marker 16/frame runtime 2880,
  erro 0,000333 ms. O V1 `marker_probe_v3_anchor_pass_ingest` libera somente
  `av_sync` como âncora compartilhada. O gate `marker_probe_v3_anchor_gate.json`
  mantém áudio perceptivo, movimento, visual e cobertura bloqueados, e mantém o
  gap PTS de 33,333 ms como falha de integridade. O MP4 exigiu retirar
  `coded_picture_number` do ffprobe para não travar a ingestão; PTS foi preservado.

## 2026-09-21 — V5 sem alias amplo, overhead repetido e achado de animação

- `audiovisual_review.py` 2.5.0 separa `artifact_identity` de integridade
  temporal, `av_sync`, cadência, visual, movimento, áudio e cobertura. V5 rejeita
  `capture_integrity` legado e exige overhead comparável com dois pares no mesmo
  SHA, HCAD e medianas faseadas.
- O recibo `out/audiovisual_review/v5_end_to_end_hstr_v14.json` foi reemitido:
  `execution_status=passed`, claims `status=blocked`; nenhuma aprovação ampla
  foi derivada de identidade, HCAD ou de revisão image-only.
- A ROM diagnóstica isolada `marker_event_probe_v2` tem SHA
  `cf34ff61…7b880f`; `out/rom.bin` permaneceu intacto. O detector de marker
  corrige células VDP 8x8 e falha fechado para PTS ilegível.
- O bundle BlastEm v2 preserva vídeo `21bb5045…d2e8a`, áudio
  `b689426f…8a8983f443`, HANC 32773/frame 1560 e HCAD 3060/3060, luta 1910,
  zero-tick 0. Dois gaps PTS mantêm integridade temporal e A/V em `needs_review`.
- HSTR exato registra `fball_active=1`, estado 700 e posição 232→242 no
  recorte 1560–1565. O finding
  `marker_event_capture_v2_finding_special_animation_001.json` registra um
  candidato vermelho/branco da transição do especial, com hashes, ROI, PTS,
  estado e teste causal sem captura. É candidato, não correção nem aprovação.
- Testes direcionados: 15 pytest audiovisuais, 5 contratos do wrapper e
  `validate_measurement_tools --self-check` passaram. A suíte ampla continua
  com a coleta P10 stale (`8ac1…` versus o freeze atual), preservada.
- O review/gate v2 (`marker_event_capture_v2_review_images.json` /
  `marker_event_capture_v2_gate.json`) validou `qualified=true` e liberou
  somente `visual_approval` para sete frames consecutivos; movimento, áudio,
  sincronismo, integridade temporal e cobertura completa ficaram bloqueados.

## 2026-09-21 — Auditoria de segunda ordem do V5

- O V5 passou a vincular o overhead repetido aos `rom_sha256` dos casos
  observados e ao `rom.bin` real da captura. `same_rom_sha256` sozinho não é
  suficiente: o overhead release `d6b7…eb9618` foi rejeitado para a captura
  diagnóstica `cf34…7b880f`, com `capture_overhead_rom_hash_mismatch_or_missing`.
- O binding de findings usa `query_interval` como janela efetivamente
  extraída quando há pré/pós-contexto; o intervalo-evento segue preservado no
  recibo para não confundir evento com mídia consultada.
- Regressões após a correção: `15 passed` no teste audiovisual do projeto e
  `5 passed` no contrato do wrapper. O recheck histórico compatível passou em
  `execution_status`, mantendo claims bloqueados por integridade temporal,
  sincronismo, movimento, áudio e cobertura conforme o caso.
- O medidor recebeu rota explícita `--rom` para overhead da ROM diagnóstica;
  a tentativa v2 não emitiu relatório/par aceito e foi interrompida sem alterar
  masters. O V5 não reutiliza overhead de outro SHA como fallback.
