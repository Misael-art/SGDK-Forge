<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: bundles BlastEm selados em `out/evidence/` + `out/logs/`
- Ultima sincronizacao: `2026-08-06` (manual, agente da sessao 011)
- Changelog canonico: `doc/changelog/changelog.md`
- Assets rastreados: 7 grupos R1 `source_candidate`; 11 PNGs normalizados de concept/layer/palette study e 11 originais de geracao preservados. Nenhuma arte final existe.
- Ultimo build: rota `build_sgdk_wine_bridge.sh`, `wine_bridge_status=buildado`
- ROM vigente: `out/rom.bin` — 6 cenas: TITULO (boot), fase jogavel, playtest de fase, boss com arena, playtest de boss, game over/vitoria com continue. 5 copy abilities COM moveset
- Rebuild de verificacao no fim da sessao 011: `wine_bridge_status=buildado`, 0 erros, 0 warnings
- Blockers vigentes: `gradiente_ceu_1a_parada_longa` (defeito aberto, causa nao determinada, gates passam), `trilha_e_placeholder_gerada` (VGM programatico, nao composto), `cenas_do_template_ainda_em_src` (inalcancaveis, mas seguram 11 violacoes de audio em baseline), `artefato_visual_gameover` (coluna pontilhada no ceu, nao investigado), `divida_audio_do_template` (11 violacoes em baseline)
- Evidencia de emulador: 6 cenas com bundle `sealed` e gates PASS. `title_final` (cpu p99 14%), `ability_final` (**11/11 locomocao + `ability_moveset_fires` PASS**, 25/80 sprites, 18/20 scanline, cpu p99 60%), `boss_arena_final` (78%), `bosstest_final` (**combate 3/3**), `gameover2` (15%), `audio_final` (**A8 music_audible + A9 dac_headroom PASS**)
- Gate visual: `visual_lab_aprovado=False` (R1 entregue, mas julgamento humano, direcao de arte e prova em ROM ainda ausentes)
- Gate gameplay: `gameplay_rom_aprovada=False` — o loop titulo->fase->boss->game over/continue roda, as 5 abilities tem moveset e o audio toca, tudo provado por playtest scriptado. Falta: trilha composta (a atual e placeholder gerada), 3 fases (so existe 1), e revisao humana
- Gate AAA: `ready_for_aaa=False`
- QA runtime: instrumentacao=operacional gameplay=loop_completo_provado_com_abilities performance=medido_cpu_p99_14_a_90_por_cena audio=tocando_e_provado
<!-- SGDK GENERATED STATUS END -->

# 10 - Memory Bank & Context Tracker — KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

**Ultima atualizacao:** 2026-08-31
**Fase atual:** FASE 0 completa. **FASE 1 COMPLETA**: titulo -> fase -> boss -> game over/continue, 6 cenas com evidencia, 5 copy abilities com moveset, audio tocando. **23 gates de runtime** + 7 de audio. FASE 3 a ~95%.
**Proxima fase:** FASE 2 (loop construtor/critico do brief) ou expansao de conteudo: fases 2 e 3, trilha composta em Furnace, e os efeitos raster R3/R4/R5 (agua, faixa submersa, holofote) que seguem sem implementacao.

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.

---

## AVISO — heranca suja do template, corrigida em 2026-07-29

A versao anterior deste arquivo, materializada pelo bootstrap, continha o
**historico operacional de outro trabalho**: a sequencia de branding do proprio
template, datada de 2026-05-24 e 2026-06-03, com ROM `22a80b7c...` de 262144
bytes, `build_v002`, 5 assets versionados, 5 WAV XGM2, blockers
`visual_direction_failed` / `gdd_substantial_insufficient`, e um pico de CPU em
`frame_index=128`.

**Nada disso aconteceu neste projeto.** Foi tudo sobrescrito.

Licao que vale para todo projeto novo deste workspace: `new_project.sh` copia
`doc/10-memory-bank.md` do template **com o conteudo do template dentro**, e
esse arquivo e a autoridade #1 da HIERARQUIA DE VERDADE do AGENTS.md. Se a
primeira sessao nao zerar este arquivo, a segunda sessao vai tomar decisoes
acreditando em ROM, build, assets e blockers que nunca existiram. Registrado em
`doc/agent_learning/failure_patterns.md`.

---

## 1. O que este projeto e

Reimaginacao de **Kirby's Adventure (NES)** para Mega Drive. Fan game **nao
comercial**: arte e trilha 100% originais, nenhum asset extraido da ROM do NES,
ROM final nao vendavel.

Contrato tecnico mestre e normativo: [ARCHITECTURE.md](ARCHITECTURE.md).

Escopo VER.001: titulo -> 3 fases -> boss Whispy Woods -> game over/continue,
com 5 copy abilities (FIRE / BEAM / CUTTER / STONE / SWORD).

Tese criativa: o jogo do NES *tentava* gradientes de ceu, camadas de
profundidade e cor por regiao, e nao tinha hardware para isso. Nosso trabalho e
entregar o que ele estava alcancando. Todo cenario precisa responder "o que o
NES nao conseguiu fazer aqui?" com uma tecnica de MD nomeada, com owner e budget.

---

## 2. Verdades do host, verificadas — leia antes de tentar buildar

| Fato | Detalhe |
|---|---|
| **Unica rota de build funcional** | `bash tools/sgdk_wrapper/build_sgdk_wine_bridge.sh --project-root "<proj>"` |
| `tools/sgdk_wrapper/build.sh` | **QUEBRADO em Linux.** Nao use. |
| `tools/sgdk_wrapper/new_project.sh` | **QUEBRADO em Linux.** Precisa de PATH corrigido para rodar. |
| Causa raiz de ambos | `env.sh` prepende `$GDK/bin` ao PATH, e la existem symlinks `cp -> cp.exe`, `mkdir -> mkdir.exe`, `rm -> rm.exe`. Coreutils POSIX fica sombreado por binario Windows sob Wine, que nao entende caminho `/mnt/...`. |
| Corrigido? | **Nao, de proposito.** `tools/sgdk_wrapper/` e canonico; alterar exige aprovacao humana explicita (AGENTS.md). |
| Rota de captura | `bash tools/sgdk_wrapper/capture_blastem_evidence_linux.sh --project-root "<proj>" --output-base "<proj>/out/evidence/<nome>" --warmup-seconds 12` |
| Graphify | nao fica `fresh` neste host (mesma classe de bug, `graphify_forge.ps1:53`), logo `assert_agent_environment.ps1` retorna `blocked reason=prepare_failed`. Graphify e consultivo e nunca fonte de verdade — nao bloqueia producao. |

---

## 3. Estado real por subsistema

| Subsistema | Status (vocabulario AGENTS.md) | Medicao |
|---|---|---|
| Instrumentacao / probe VLAB + KRB1 | `testado_em_emulador` | **21 gates de runtime + 5 de audio**. Bloco proprio KRB1 em SRAM 0x300 destravou parallax exato, P5 e pico de DMA |
| Rota de build | `testado_em_emulador` | `out/rom.bin` 262144 B |
| Cores / CRAM | `validado_budget` (baseline) | `doc/PALETTES.md` escrito. Layout de CRAM `[VERIFICADO]` em `pal.h:18-26`. **S/H decidido: ligado globalmente, todo tile de fundo priority=1.** Teto corrigido de 61 para **58** (2 slots viram operadores). Medido: 21/58 simultaneas, 0 ilegais |
| Performance | `validado_budget` (baseline) | p50/p95/p99 = 36/36/42, teto 100; 0 frames acima do budget |
| Folga de CPU | medida | `vblank_idle = 171` scanlines/frame na cena vazia |
| VRAM | `validado_budget` | mapa byte-exato somando 65536. Gates `vram_tile_budget` e `plane_size_locked` **PASS**. **DMA agora MEDIDO: pico 1792 B/frame** contra limite de projeto 4096 e teto de hardware 7372 — abaixo da estimativa de 3176 B de VRAMMAP.md §3.1 |
| Sprites | `testado_em_emulador` | pico medido **25/80 por frame, 18/20 por scanline** com 6 inimigos + 6 tufos + 12 tiros de ability. Chegou a 19/20 e a alavanca de degradacao do §5 foi gasta (camada 5 de 8 para 6 tufos). Estresse com 24 tufos numa fileira FALHOU o gate por scanline (24/20): para faixa horizontal o limite que morde e o por scanline. **Cada sprite de ate 4x4 tiles e UM sprite de hardware** — Kirby 32x32 custa 1, nao 4 |
| Parallax 5 camadas | `testado_em_emulador` | **VERIFICADO EXATAMENTE** pelo bloco KRB1, lendo a tabela de HScroll que a ROM programou: cameraX=23 -> ceu 0, montanhas -2, colinas -7, terreno -23, todos identicos a formula de projeto. A divida de medicao por forense de screenshot foi quitada |
| Raster R1-R5 | `testado_em_emulador` | **TODOS OS CINCO existem em ROM**: R1 gradiente, R2 bandas de parallax, R3 distorcao da agua, R4 paleta submersa (4 words verificados no CRAM), **R5 holofote com operadores de S/H** e regra de gameplay (boss so toma dano iluminado). `tile_priority_under_sh` 0/13. Defeito aberto: 1a parada do gradiente ficou longa |
| Audio | `testado_em_emulador` | `src/audio/xgm_router.c` e o dono unico. **Musica TOCANDO e provada**: gate A8 `music_audible` com RMS 0.0340 contra piso de silencio 0.015 MEDIDO. A9 `dac_headroom` pico 0.1186/0.85. **Custo de CPU no 68000: ~zero** (p99 50%->50%) porque o XGM2 mixa no Z80. Trilha e placeholder gerada por script, nao composta. PCM 8.9 KB de 384 |
| Boss Whispy Woods + arena | `testado_em_emulador` | **39 sprites/frame**, 10/scanline, cinematica com `F16_sin`, tronco em tiles. **Arena com as 4 camadas ligada.** Estourou o budget duas vezes e foi resolvido duas vezes: alavanca 1 do §5.1 (87%->75%) e depois, com a arena, pular o rebuild de HScroll com camera estatica (**96%->78%, 19->0 frames, DMA 1792->896 B, render byte-identico**). Alavancas 2 e 3 seguem sem uso. Falta dano por contato, derrota jogavel e transicao |
| Combate / derrota | `testado_em_emulador` | Kirby com vida 6, i-frames 60 com blink, knockback do §7 em `fix16`. Boss fere pelas pontas dos galhos so durante WHIP e por macas. **Contra-ataque pelo verbo do Kirby**: inalar a maca e devolve-la. `playtest_boss_combat 3/3` PROVADO: boss hp=0, kirby 4/6, boss derrotado |
| Game feel | `implementado` | coyote 4, jump buffer 5, hit-stop 4/8 em `fix16`. **Playtest scriptado cobre 11/11 estados do jogador** (`playtest_coverage` PASS), incluindo `swallow` e `ability` — o loop central esta PROVADO na ROM. Mas o playtest prova que o estado OCORREU, nunca que a fisica e boa: nenhum tunable foi validado por julgamento humano |
| Arte | `parcial` | **P1, P2, P3 e P4 estão arquivadas por reprovação visual em 2026-08-06.** P1 está em `data/source_art/archive/p1_2026-08-06_visual_rejected/p1/`; P2 em `rascunho/archive/p2_hd_arcade_original_proposal_2026-08-06_rejected/`; P3 em `data/archive/p3_2026-08-06_geometry_preserved_pixelization_rejected/`; P4 em `data/archive/p4_2026-08-06_vector_master_anatomy_rejected/`. P4 provou que limpeza vetorial não substitui anatomia e integração dos membros. Não há master aprovado, sheet final ou promoção para `res/`. |

---

## 4. Numeros medidos, que valem mais que opiniao

Bundle `out/evidence/probe_scene_demo/blastem-linux-20260729T150654Z-218744/`:

```
scene_id             3         (targeting de cena funciona)
cores simultaneas    21 / 61
CRAM ilegal          0
sprites/frame        0 / 80
sprites/scanline     0 / 20    AMOSTRADO: 4 scanlines/frame, nao exaustivo
frames > budget      0 / 0
cpu p50/p95/p99      36 / 36 / 42   teto 100
bg_a                 0xE000    confere com o default do SGDK

atribuicao por secao, scanlines/frame:
  input 2 | scene 90 | audio 1 | sprite 4 | vblank_idle 171
```

**Interpretacao honesta:** as 90 scanlines de `scene` sao `VDP_drawText`, custo
que sai do jogo final. As 171 de `vblank_idle` sao a folga bruta para parallax +
raster + entidades + boss. Isso **nao prova que o jogo cabe.** Prova que existe
folga mensuravel e que o instrumento de cobranca funciona.

---

## 5. Decisoes travadas (mudar exige entrada no changelog)

1. **5 camadas a partir de 2 planos.** BG_B fatiado em 3 bandas de line-scroll
   (ceu / montanhas / colinas) + BG_A jogavel + sprites no primeiro plano.
   Terceiro plano de BG nao existe no MD — AGENTS.md lista como alucinacao.
2. **Um unico callback de H-int** no jogo inteiro, dirigido por tabela de faixas
   por cena. Teto de 16 faixas.
3. **Dono unico** por sistema acoplado: `systems/raster.c` (scroll+paleta+raster),
   `audio/xgm_router.c` (canais + janela de DMA), `systems/vram_budget.c` (VRAM).
4. **DMA somente no VBlank.** Sem excecao.
5. **Cotas fixas de sprite** por consumidor (ARCHITECTURE.md §5). Degradacao sob
   pressao: particulas -> primeiro plano -> projeteis. Kirby e inimigos nunca.
6. **Fan game nao comercial**, arte original, sem rip.

---

## 6. Bloqueios vigentes e como sair deles

| Blocker | Como resolver |
|---|---|
| ~~`vrammap_ausente`~~ | **RESOLVIDO 2026-07-29.** `doc/VRAMMAP.md` escrito; gate `vram_tile_budget` passou de `warn` para PASS |
| ~~`palettes_ausente`~~ | **RESOLVIDO 2026-07-29.** `doc/PALETTES.md` escrito; S/H decidido; teto corrigido para 58 |
| ~~`r1_julgamento_humano_pendente`~~ | **RESOLVIDO 2026-07-29.** R1+R2+R3 julgadas por medicao; loop de arte encerrado. Sources seguem bloqueadas para `res/` por falta de traducao para grade nativa e gate visual em ROM |
| `soundmap_ausente` | escrever `doc/SOUNDMAP.md` + `doc/17-audio-design.md`; decidir XGM vs XGM2 contra os headers em `sdk/sgdk-2.11/inc/snd/` |
| ~~`probe_nao_exporta_sh_prioridade_dma`~~ | **PARCIALMENTE RESOLVIDO 2026-07-30** via bloco KRB1: `cameraX`, HScroll por banda e contador de DMA agora medidos. Restam duas limitacoes reais: `sh_enabled` prova INTENCAO (SGDK nao expoe leitura do reg 0x0C) e a auditoria de prioridade le 0 de 0 em BG_A por motivo nao determinado |
| ~~`gate_p5_parcial`~~ | **RESOLVIDO 2026-07-30.** A causa nao era o VDP: era um `replace` meu que nao aplicou, deixando o passo de amostragem em 1 linha e cobrindo so linhas vazias de BG_A. Corrigido: **P5 = 0 violacoes de 17 amostrados (BG_A 4, BG_B 13), nao vacuo, PASS** |
| `divida_audio_do_template` | 11 violacoes herdadas (10 de `PSG_*` + 1 de `SOUND_PCM_CH1`) em `src/system/audio.c` e `src/scenes/scene_branding.c`. Em baseline rastreada, NAO silenciadas. Deve chegar a zero quando `src/audio/xgm_router.c` existir |
| `fase1_nao_iniciada` | **desbloqueado** — FASE 0 completa. Pode comecar |
| `p1_runtime_promotion_pending` | integrar os 16 source candidates em `res/`, buildar e validar em nova sessao BlastEm; A1 exige motion capture do output runtime e hash da ROM |
| `project_hygiene_blocked` | validator reporta `orphan_project_root_entry`, nomes legados/IDs maiusculos do proprio contrato P1 e referencia absoluta preexistente em `doc/scene-contracts.json:5`; nao impede a geracao offline, mas bloqueia closeout AAA |

---

## 7. Decision log conservador

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia |
|---|---|---|---|---|
| 2026-07-29 | Rota de build em Linux | usar `build_sgdk_wine_bridge.sh` | consertar `build.sh` (canonico, exige aprovacao humana) | `wine_bridge_status=buildado` |
| 2026-07-29 | Camadas de parallax | 3 bandas de line-scroll em BG_B | inventar terceiro plano de BG | AGENTS.md anti-alucinacao |
| 2026-07-29 | Evidencia | portar probe VLAB antes de qualquer codigo de jogo | prometer performance sem instrumento | 2 bundles `sealed` |
| 2026-07-29 | Arte | emitir pacote de prompts com grade RGB333 explicita | pedir concept art livre e quantizar depois | `doc/art/AI_IMAGE_PROMPT_PACK.md` |
| 2026-07-29 | Arte R1 | gerar e normalizar 7 pedidos como fonte rastreavel | promover PNG de IA diretamente para a ROM | `data/source_art/r1/r1_delivery_manifest.json` |
| 2026-07-29 | Memory bank | sobrescrever heranca do template | manter historico de branding alheio como se fosse nosso | este aviso |
| 2026-08-06 | Arte P1 | arquivar como `archived_visual_rejected` após reprovação humana | tratar checks mecânicos como aprovação visual | `data/source_art/archive/p1_2026-08-06_visual_rejected/ARCHIVED_ATTEMPT.md` |

---

## 8. Historico de sessoes

| # | Data | O que aconteceu |
|---|---|---|
| 014 | 2026-08-06 | **P1 executada, A1 primeiro.** Draft radial do Kirby reprovada como `technical_pass_visual_fail`; nova A1 nasceu do model sheet R2 + key-pose board e passa auditoria v2. 16/16 assets entregues com notes/prompts e harness PASS. Contact sheets por grupo revisadas; repeticao procedural de B1-B3/C1/E1-E2 e logo quadrado foram reprovados e refeitos antes do fechamento. Nenhum asset foi promovido para `res/`; BlastEm permanece gate pendente. Higiene do projeto segue bloqueada por 3 classes, incluindo material legado e IDs maiusculos exigidos pelo pack. |
| 013 | 2026-08-06 | **R5 holofote: os 5 efeitos raster do contrato existem.** Usa os operadores de S/H reservados na FASE 0; clareia em vez de escurecer para nao violar P5. Regra de gameplay: boss so toma dano iluminado. **Duas licoes caras**: tabela virou PESSIMIZACAO (92%->107%) porque o indice exigia divisao de 32 bits — o que importa e o custo do indice, nao a tabela; e gastei degradacao antes de procurar desperdicio, violando minha propria licao. Final: 82%, 0 frames estourados. |
| 012 | 2026-08-06 | **R3 + R4: a agua.** Cena 10 LAKE com distorcao senoidal por linha e troca de paleta submersa no H-int, esta verificada no dump de CRAM (4 words exatos). Tensao do PALETTES.md (1 word vs 16) resolvida tornando a contagem medivel. 2 bugs meus: a otimizacao da arena quebrou o efeito animado, e derivar scanline de um contador saturado. **Defeito aberto registrado**: 1a parada do gradiente ficou longa, causa nao determinada, a diagnosticar por telemetria e nao por screenshot. |
| 011 | 2026-08-06 | **Copy abilities com moveset.** 5 movesets diferenciados por FEEL (pressao/precisao/compromisso/defesa/decisao) e por FORMA no FX. B faz dupla funcao: sem ability inala, com ability ataca. Gate novo `ability_moveset_fires` cobra que a recompensa FUNCIONE, nao so que seja concedida. Alavanca de degradacao gasta ANTES de quebrar: scanline 19/20 -> 18/20. **Bloqueio de ambiente: `/run/user/1000` 100% cheio por artefatos de teste de outro app fazia o flatpak falhar com ENOSPC** — o host tinha 46 GB livres, o que mascarou. Provavel causa tambem dos `window_timeout`. |
| 010 | 2026-08-06 | **Tela de titulo: FASE 1 FECHADA.** Titulo -> fase -> boss -> game over/continue -> titulo, 6 cenas com bundle selado e gates PASS. Gradiente noturno reusando o mesmo H-int (so a tabela muda). "PRESS START" custou 3 capturas: WINDOW sem tamanho, `VDP_setTextPriority` virou bloco cinza, e so funcionou com S/H desligado. Licao: cena sem efeito de S/H deve rodar sem S/H. Prompt piscante pego apagado por 2 capturas: affordance essencial nao pisca. |
| 009 | 2026-08-06 | **Audio ligado e provado tocando.** Router como dono unico com prioridade/ducking/fila; VGM real gerado por script. **Custo de CPU praticamente zero** (XGM2 mixa no Z80) — o medo de estourar o orcamento nao se confirmou. Gates A8/A9 novos. **Erro meu**: li `audio.raw` como int16 e diagnostiquei clipping inexistente; o formato e float32 e o pico real era -18.5 dBFS. Exposto por teste de controle com resultado impossivel. Baseline de audio teve a condicao de expiracao corrigida. |
| 008 | 2026-08-06 | **Game over + continue: o loop literal da FASE 1 fechado** (fase -> boss -> game over/continue; falta so o titulo proprio). Dano de inimigo na fase, com a regra de que inimigo sendo inalado nao machuca. Tela com countdown de 9 s e trava de input. **O gate semantico canonico reprovou a primeira versao com `blank_or_low_information_capture` e estava certo** — refiz com o vale ao fundo em vez de contestar. S/H desligado na cena de texto (fonte do SGDK e prioridade 0). Regressao: parallax 4/4 exato com camera em movimento. |
| 007 | 2026-08-06 | **Dano por contato e derrota.** Kirby com vida/i-frames/knockback; boss fere pelas pontas dos galhos durante WHIP e por macas; contra-ataque inalando a maca e devolvendo. Cena 7 com script proprio: **`playtest_boss_combat 3/3` — primeiro loop completo do jogo PROVADO** (boss hp=0, kirby 4/6). Sintese pedagogica em `LICOES_MEGADRIVE.md`. 3 erros meus de gate/script corrigidos. |
| 006 | 2026-08-06 | **Arena do boss com as 4 camadas.** Estourou o budget (cpu p99 96%, 19 de 32 frames). Resolvido por OTIMIZACAO SEM PERDA, nao por degradacao: a camera da arena e estatica e a tabela de HScroll era reconstruida todo frame com valores identicos -> p99 78%, 0 frames, DMA 896 B. Bugs: `PROBE_STAGE_reset` apagava o flag de S/H publicado antes dele; gate `screenshot_color_count` media a grandeza errada em cena com raster e foi rebaixado a soft com justificativa; processos `blastem.bin` acumulam e sobrevivem ao `flatpak kill`. |
| 005 | 2026-08-06 | **Playtest scriptado** do lado da ROM: 11/11 estados cobertos, `swallow` e `ability` provados, 2 gates novos. **Boss Whispy Woods**: 4 galhos x 7 segmentos com `F16_sin`, 39 sprites/frame. FALHOU o gate de budget a 87% de cpu; **alavanca 1 da escada documentada aplicada** -> 75%, 0 frames estourados, PASS. Bugs: backdrop apontando para a chave de transparencia sob S/H; `window_timeout` causado por instancia flatpak presa (nao por processo orfao). |
| 004 | 2026-07-30 | Instrumentacao: bloco proprio **KRB1** em SRAM 0x300 (nao estendi o VLAB para nao corromper os gates de cor do workspace). **Parallax verificado EXATAMENTE** nas 4 camadas lendo a tabela de HScroll. **DMA medido: 1792 B/frame** de 4096. Bug achado pela propria instrumentacao: `VDP_clearTextArea` gerava 16/16 tiles em prioridade 0 sob S/H. **Gate P5 marcado PARCIAL, nao aprovado.** |
| 003 | 2026-07-30 | Inimigos (pool fixo de 6), mecanica de inalar/engolir, copy ability FIRE concedida ao engolir. Botoes A=pular B=inalar. **Dois bugs corrigidos: pan congelava a simulacao (personagens flutuando) e corrupcao NAO DETERMINISTICA de 17-31 entradas de CRAM causada pelo H-int racing o flush de DMA em VBlank** (31 -> 17 -> 0 entradas, verificado por dump). Hipotese do custo de sprite REFUTADA por medicao. 14+5 gates PASS. |
| 002 | 2026-07-30 | FASE 1 nucleo: `raster.c` (dono unico de scroll+paleta+raster, 1 H-int), `kirby.c` (fisica fix16), `stage_map.c`, `scene_stage.c`, arte provisoria gerada com as paletas canonicas. 14 gates **PASS com 0 warnings**. Parallax diferencial PROVADO por medicao. Detalhe em [CHANGES.md](../CHANGES.md). |
| 001 | 2026-07-29 | Projeto criado e classificado `aaa_game` (`blockers=0`). Rota de build e captura verificadas no host. `ARCHITECTURE.md` escrito com primeira medicao real. Probe VLAB portado; 2 bundles selados. `gates.py` operacional com 13 gates. Pacote de arte R1 emitido. Sessao encerrada por limite de API; 3 subagentes perdidos; VRAMMAP/PALETTES/SOUNDMAP nao escritos. Detalhe em [CHANGES.md](../CHANGES.md). |
| 002 | 2026-07-29 | Codex gerou os 7 pedidos R1 (11 PNGs) e preservou originais com hashes. Todas as entregas foram normalizadas para canvas/paleta do pedido, marcadas `source_candidate_pending_human_judgment` e documentadas com prompt, autocritica e handoff. Nenhuma entrou em `res`, nenhuma ROM foi declarada testada. |

---

## 9. Referencias rapidas

- Contrato mestre: `doc/ARCHITECTURE.md`
- Registro por sessao: `CHANGES.md`
- Pacote de arte: `doc/art/AI_IMAGE_PROMPT_PACK.md` + `doc/art/image_request_manifest.json` + `data/source_art/r1/r1_delivery_manifest.json`
- Harness: `tools/harness/gates.py`, `frametime.py`, `probe_format.py`
- GDD: `doc/11-gdd.md` (escopo e identidade reconciliados em 2026-08-31)
- Spec cenas: `doc/13-spec-cenas.md` (roadmap e gates reconciliados em 2026-08-31)

## 10. Sessao atual — núcleo visual nexialist v01 (2026-08-31)

- Diagnóstico canônico: cenário `2_res_inadequate_check`; 22 recursos ativos legíveis, nenhum bloqueio de build; fontes R1-R4/P1-P4 continuam negativas e não são fonte de pixels.
- Gerados e persistidos em `rascunho/nexialist_visual_nucleus_v01/`: painel de três rotas, model sheet revisado e conceito da cena-dourada. Hashes e prompts completos estão em `visual_nucleus_manifest.json` e `doc/art/nexialist_visual_nucleus_v01/generation_prompts.md`.
- Direção recomendada: Rota A — `Sunlit Cultivation`; luz superior-esquerda, BG_B frio e silencioso, BG_A verde/âmbar jogável, foreground de folhas esparso e FX de inalação ciano-branco com consequência de gameplay.
- DNA visual atualizado para v03 candidato: braços separados, contato de pés, `3/4 back` distinto, marcas faciais e margens de célula. Aprovação humana ainda pendente; escala alvo permanece 32×32.
- Criado `doc/asset_provenance_manifest.json`: os 22 símbolos visuais atuais são declarados `procedural_primitive` + `placeholder`; auditoria passou sem blockers, mas nenhum placeholder pode virar arte final.
- Budget preliminar: `cabe com recuo`. Layout base mediu 12 links e 4 sprites/linha; degrau seguinte 20 links e 7 sprites/linha; stress probe mediu overflow de pixels em 336/320 com 19 links. Nenhum número prova a nova cena em ROM.
- Gate humano vinculado aos hashes em `doc/art/nexialist_visual_nucleus_v01/human_gate_request.md`. Sem aprovação, não tocar em `res/`, não converter automaticamente e não alegar `visual_pass`/`ready_for_aaa`.

## 11. Decisão humana e segunda rodada visual — 2026-08-31

- Rota A — `Sunlit Cultivation` está registrada como `locked_visual_direction`, vinculada a `vegetable_valley_route_exploration_panel_v01` e SHA-256 `cb1ab99c66e2757b904a56402e4560619a1c123744dbb6b68930e118eb0a7d35`. A aprovação é somente de direção visual.
- A cena-dourada está registrada como `locked_composition_reference_only`, vinculada a `vegetable_valley_golden_scene_concept_v01` e SHA-256 `a52b366d8881d43133830fdafcf552bc93bba533dc25d729db96c7bdbf11e561`. Não é bitmap de conversão, asset nativo ou autorização para `res/`.
- O model sheet anterior foi reclassificado como `model_sheet_challenger_v01`, SHA-256 `0f2866de710ae3c920d003b1955d9a19029f7bcce2c50dbb79bac025552b501d`, `visual_gate=needs_rework`, `promotable=false`, `translation_authorized=false`. O blocker obsoleto `model_sheet_absent` foi removido; checks antigos não comprovados viraram `not_proven`.
- Produzido `model_sheet_challenger_v02`, SHA-256 `0d9be1e502eddedf1a364498180102fdc6e49b8ff7a48fa580d4b1ed36b8880a`, com o challenger v01 anexado explicitamente como referência. É novo challenger, não revisão fiel nem fonte canônica; ainda não autoriza tradução.
- Produzidos decomposição semântica, inventário de tile kit, estudo de parallax e comparação de três distribuições de paleta A/B/C em thumbnail 4:3, nearest e composição 320×224. Todos são controles visuais em `rascunho/`.
- Proveniência harmonizada: fan game derivado da identidade de Kirby/Nintendo/HAL, com execução gráfica original, sem reutilização ou extração de pixels dos jogos de referência. Identidade derivada não é declarada como propriedade intelectual original.
- Validação: JSON/diff check/proveniência/residência/self-check VDP passaram. O probe de estresse continua registrado como falha intencional de limite (336/320 pixels por scanline). Não houve alteração em `res/`, build ou captura BlastEm nesta rodada.

## 12. Decisão humana — rework antes da tradução nativa (2026-08-31)

- `model_sheet_challenger_v02`, SHA-256 `0d9be1e502eddedf1a364498180102fdc6e49b8ff7a48fa580d4b1ed36b8880a`, foi aceito somente como `turnaround_volume_reference_only`; `translation_authorized=false`.
- Motivo: deriva para render suave/glossy, gradientes, antialiasing e volume 3D. Preservar somente continuidade de volume, cinco ângulos, baseline, conexão dos braços e orientação facial.
- Produzido v03-A `cluster_strict`, SHA-256 `989d1a2398e9609dffe3e4f673e95b73e081ddffdcba9764829684498d8c6241`; e v03-B `silhouette_first`, SHA-256 `85a93885fec97490a8c220f3a35e66538e1a829e3c21f8c3392768c563b52f88`. v03-A foi posteriormente aprovado em escopo limitado; v03-B permanece `comparison_only`.
- v03-A usou v02 anexado como referência explícita. v03-B teve duas tentativas com referência explícita bloqueadas pelo filtro da ferramenta; a saída final foi gerada sem referência e está classificada como novo challenger, não revisão fiel.
- Probes mecânicos persistidos para cada challenger: 32×32, 64×64 nearest, 256×256 nearest, composição 320×224 e silhueta preta 32×32. Microcores high-res são medição de inadequação para sprite nativo, não rejeição do model sheet como fonte visual.
- Antes da decisão seguinte, o DNA mantinha `candidate_source_of_truth` no v01 e `scale_lock_status=draft`; isso foi substituído em escopo limitado pela aprovação humana do v03-A para uma pose idle 32×32. O turnaround completo continua sem aprovação.

## 13. Decisão humana — aprovação limitada do v03-A (2026-08-31)

- `decision=approved_as_model_sheet_source_for_single_native_key_pose` para `model_sheet_challenger_v03_a_cluster_strict`.
- SHA-256 `989d1a2398e9609dffe3e4f673e95b73e081ddffdcba9764829684498d8c6241`; `revision=v03_a`; `route=cluster_strict`; `native_scale=32x32`.
- Usos autorizados: `model_sheet_reference` e `single_idle_native_key_pose_translation`.
- O PNG high-res continua `visual_source`: não é arte nativa, não é promovível para `res/` e não autoriza outras poses, sprite sheet, animação ou runtime.
- A única pose idle ainda precisa passar por autoria nativa, lineart 1px, material topology, paleta, pixel-strict, ResComp, budget e aprovação visual humana.
- Produzidos dois candidatos nativos controlados da mesma silhueta/lineart: BASIC `native_idle_key_pose_basic_v01` SHA-256 `473bcdeab5b1b7edf7d32aeafe4d5d7f49aedb780684e94fddfde66c5aec3ecd` com 9 cores visíveis; ELITE `native_idle_key_pose_elite_v01` SHA-256 `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29` com 12. Ambos são `technical_candidate`, fora de `res/`, com visual humano pendente.
- O teste de repetição indexada exata passou para 2×/64×64 e 8×/256×256 nos dois candidatos. O budget isolado é 16 tiles 8×8/512 bytes, um link de sprite e 32 px máximos por scanline; isto não prova cena, ROM, DMA em VBlank ou emulador.

## 14. Decisão humana — ELITE para idle nativo e prova visual isolada (2026-09-01)

- Registrada `decision=approved_for_native_idle_key_pose_and_runtime_visual_proof` para `native_idle_key_pose_elite_v01`, SHA-256 `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29`, content SHA `ce677449e1ce5c0722add0fd587bdba93d5b278667cf7cdf0a51329195ad93bc`.
- Binding aprovado: `native_bbox=32x32`, `pivot=(16,31)`, `baseline_y=30`, `visible_colors=12`, `scale_lock_status=locked`. O uso é limitado a model sheet reference, uma pose idle nativa e cena dedicada de review; o runtime permanece pendente até build e BlastEm.
- BASIC permanece `comparison_control`/`superseded_by_visual_choice` e não é rejeição artística. v03-B permanece `comparison_only`; v03-A continua a fonte visual canônica por SHA, sem aprovação do turnaround completo.
- O recurso `spr_native_idle_elite` foi adicionado ao `res/resources.res` e é usado somente por `APP_SCENE_NATIVE_ART_REVIEW` (scene id 11). `APP_SCENE_STAGE` e `APP_SCENE_STAGE_PLAYTEST` continuam com `spr_ph_kirby` placeholder.
- Foram criados os contratos de estado, roster, budget, pivot/escala, direção, fases, turnaround, física e transições. Três novos key poses foram autorados em 32×32 para motion proof: contato, passagem e airborne; não formam sheet completa.
- A falsa evidência de escala foi corrigida: os probes ELITE 64×64 e 256×256 continuam derivados exclusivamente do 32×32 por NEAREST, com repetição exata de pixels/alpha registrada; contagem de microcores high-res não é usada contra a função de fonte visual.
- A prova isolada foi concluída: build/ResComp/semantic gate/BlastEm passaram para a cena 11, ROM SHA-256 `d37077b2d1c6e8c2f65a24ee0ffd4e64ebac57d37ef75520d5d7c1aef7cce8ad`, sessão `blastem-linux-20260901T084532Z-4098997`; movimento continua `animation_candidate`; `ready_for_aaa=false`.
- Teto atual: `testado_em_emulador_for_isolated_idle_review_only`. Não há autorização para substituir `first_playable`, fechar sheet/animação, promover `res/` ou declarar AAA.

## 15. Forward-test r1 da capacidade de animação — 2026-09-02

- A raiz operacional foi resolvida sem mistura: `/mnt/sdcard/Projects/Sgdk Forge`; o projeto prioritário é este diretório e o framework canônico é `tools/sgdk_wrapper/.agent`.
- A fonte r1 `data/source_art/r1/r1-01/concept.png`, SHA-256 `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`, foi confirmada como autoridade de identidade, turnaround, expressões e linguagem de movimento. O board não provou escala inteira global; a rota foi registrada como `visual_source_native_translation`.
- Persistidos em `out/forward_test_v03_r1/`: crops limpos, lineart de auditoria, strips separados de `idle`, `run` e `inhale`, GIFs com timing VBlank, contratos 3.0.0, mapas de fase, DNA visual, proveniência, budget e relatório dos 12 princípios.
- Hashes dos strips: idle `79c75241b921d06cd7f6c6c0ce5610abbb9262e135d102c219552097a4013fdd`; run `2619476171862b5a314ecfabbf27e17027b34c4eb60b96dca56896ee05c5050f`; inhale `0ba263c9fc1efa1dfdf17791652e241987da5473af73305372449f1100cf8af3`.
- `validate_animation_strip_artifact.py`, `validate_motion_semantics.py` e `analyze_sprite_strip_integrity.py` passaram para as três ações. `validate_animation_candidate.py` passou com `maximum_proven_claim=motion_semantic_candidate`.
- O relatório dos 12 princípios está `needs_review`; não há evidência de ROM para os strips, nem autorização para `res/`. O teto desta rodada é `motion_semantic_candidate`, não `ready_for_res`, `runtime_candidate`, `testado_em_emulador` ou AAA.
- O crop idle passou `source-audit` como `accepted_translation_source`; `route-shootout` executou 20 rotas, pulou 5 indisponíveis, não escolheu vencedor automático e verificou o lineage. O painel é `mechanical_geometry_probe`, SHA-256 `155343586fcd01960bca8316bcf98e224e062421a691fa7cba9b6c5af29c530f`, e não é arte final.

## 16. Autoria nativa temporal v04 — 2026-09-02

- Os strips v03 foram formalmente reclassificados como `mechanical_single_pose_temporal_probe`, `technical_probe`, `native_animation=false`, `native_lineart=false`; não são fonte de pixels para a nova rodada.
- Criado `out/forward_test_v04_native_temporal/` com 16 frames nativos temporalmente autorados (4 `idle`, 4 `run`, 4 `inhale`, 4 `jump_float`), todos fora de `res/`, com contratos 3.0.0, mapas de fase, GIFs, lineart auxiliar, proveniência e composição diagnóstica.
- A autoridade visual permanece `data/source_art/r1/r1-01/concept.png`, SHA-256 `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`; nenhum pixel dos probes v03 foi reutilizado.
- `validate_animation_strip_artifact.py`, `validate_motion_semantics.py` e `analyze_sprite_strip_integrity.py` passaram para as quatro ações. O agregado `validate_animation_candidate.py` passou com `maximum_proven_claim=motion_semantic_candidate`, sem blockers; princípios e dependências visuais continuam warnings, e `human_gate_ready=false`.
- O relatório dos 12 princípios está `needs_review`; o gate visual está `visual_gate_blocked`; o budget é apenas offline. Não há ROM/BlastEm/áudio/runtime para esses strips, nenhum arquivo de `res/` foi alterado e `promotable=false`/`res_promotion=false` continuam obrigatórios.
- Transições estão mapeadas em `contracts/transition_contract.json`: idle→run, run→idle, jump→fall→landing e inhale→recovery. A reutilização entre ações foi limitada a dois hashes de endpoint, explicitamente autorizada no manifest e não substitui quadros temporais.

## 17. Forward-test visual bitmap temporal v05 — 2026-09-02

- O v04 foi preservado sem alteração e sem reutilização de pixels. A revalidação com os validadores atuais foi executada fora do diretório v04; os quatro strips mantiveram seus hashes (`idle=fbb39afc1f13c0b48d0ecca8ec96e3afad0111b0b3261f95649be92f76930f75`, `run=53948d675086ca4f6bda95b55fbbbe2abafb5e25fcd4cb5abc0d43f272f86ba4`, `inhale=7b8163f51a23afdcc2055d7ac87181db0d330af3a92347883b9c854f3d40d4c9`, `jump_float=0ef7db58c137ed3351330cbcb6faa1725eb57bf8817858fa95442488f6bab40e`) e o estado atual reportou falhas de schema/proveniência/escala/aprovação; nenhuma correção foi aplicada ao v04.
- Criado `out/forward_test_v05_visual_bitmap_temporal/` com 16 fontes bitmap independentes geradas pelo produtor visual integrado, quatro hipóteses causais (duas por ação), quatro frames por ação, strips horizontais, GIFs VBlank e evidências 1x/2x/3x/8x, silhueta, delta, pivot/contact, composição 320×224, paleta, tiles, metasprite, DMA e scanline. A fonte de identidade segue sendo `data/source_art/r1/r1-01/concept.png`, SHA-256 `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`; o pedido referenciado foi bloqueado pelo filtro da ferramenta e isso está declarado no producer record.
- Hashes dos strips v05: `idle=8839cf0677f5e78490aea2055fafa2fe0a23e3b7cbf9e8a9417eca95b5802f6b`, `run=9e927115c4b4cfd564f6c517721715dc9850549191695079a8df0f200b994d6e`, `inhale=baf28a663f3ec4c4257ea57d99c7cd5beb5d80ffbebca4b8817d074f9091ffd1`, `jump_float=4338d521ad07926028c3d4e0c5f33c24930160e96d8e6114cd0316f8617a8bb3`.
- A tradução técnica preservou PNG indexado, índice 0 transparente e escala de pixels 1:1, mas os quatro validadores por strip retornaram `error` porque não existe lineart nativa separada e hash-bound; não foi fabricada lineart por rastreamento automático. O candidato agregado `animation_candidate_report.json` está `error`, `maximum_proven_claim=none`, com revisão cega abaixo do limiar (`needs_review`) e princípios/dependências visuais não fechados.
- O budget v05 é somente offline: 1 célula de hardware 32×32, 16 tiles 8×8 residentes no frame, 512 bytes DMA teóricos por frame, 1 sprite/scanline e pico declarado de 32 pixels/scanline; não é medição de VBlank, ROM, áudio ou emulador. Nenhum `res/` foi alterado.
- Testes canônicos desta rodada: animação 10/10, arte 128/128, forge-art 126/126, medição self-check aprovado e auditoria de proveniência do projeto `OK` sem blockers. O aprendizado local foi capturado sem promoção canônica. Próximo passo causal: autorar lineart nativa independente e repetir a revisão cega; só depois considerar uma nova rodada nos demais projetos `[GAME]`, sem transportar escala/paleta/solução do Kirby.

## 18. Forward-test visual e temporal corrigido v06 — 2026-09-02

- Criado somente em `out/forward_test_v06_corrected_native_temporal/`, sem alterar `res/`, `resources.res`, runtime, ROM, v04 ou v05. A autoridade continua `data/source_art/r1/r1-01/concept.png`, SHA-256 `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`.
- O v05 foi reproduzido como evidência negativa: matte checkerboard RGB, componente retangular, outlier de área, strips pretos, deriva de paleta, divergência GIF/strip, hipóteses misturadas, review cego hardcoded e contato temporal falso. O controle `run_hypothesis_b` foi rejeitado explicitamente.
- Persistidos fontes brutas do produtor visual, diagnósticos light/dark/chroma/checkerboard, matte edge-connected, lineart independente, 16 frames, strips, GIFs, contratos 3.0.0, mapas de fase, evidências 8× e relatórios de saneamento, triagem, paleta, equivalência, coerência, princípios, candidato e budget.
- `validate_v06_temporal_package.py --self-check` passou 11/11; pacote central passou sem findings; `validate_strip` passou os quatro contratos; self-checks de lineart, strip, artefato e motion semantics passaram. `idle_breathing` e `run_cycle` passaram a validação semântica; `inhale_or_charge` permanece bloqueado por probe mecânico/variação abaixo do perfil; `jump_float` permanece bloqueado porque o registry canônico não possui `jump_arc`.
- O GIF é derivado das células finais do strip e reabre com holds `[4,3,2,4]`. O contato de idle/inhale é pixel-bound; os primeiros quadros do salto não tocam borda e os quadros de aterrissagem declaram suporte. Não há review visual humano, runtime, emulador, áudio ou 60fps nesta rodada.
- Teto honesto: `temporal_translation_probe`; `human_review_policy=deferred_nonpromotional_review`, `human_gate_status=pending`, `promotable=false`, `res_promotion=false`. Próximo passo causal: nova autoria visual temporal independente para inhale/jump e decisão humana; não promover este pacote para `res/`.
- Avanço do gate de evidência visual: adicionados GIFs 2×/3×/8×, contact sheets, silhuetas, overlays de pivô/contato, fundos claro/escuro/chroma, composição 320×224, deltas e timing em `reports/evidence_render_report.json`. Os painéis são derivados das células finais e permanecem evidência diagnóstica, não aprovação visual.
- `canonical_curation_candidate_report.json` foi completado com sintoma, causa, fixture, correção, arquivos, antes/depois, aplicabilidade, risco de falso positivo e recomendação para cada aprendizado; nenhum `SKILL.md` foi editado.

## 19. Fechamento da rota native_grid_encoded — 2026-09-03

- Correção operacional de estado: `status=technical_runtime_creative_blocked`; o ramo específico do Kirby é `kirby_native_sprite_branch=blocked_native_pixel_authorship`. `technical_pass_visual_semantic_fail` permanece somente como histórico específico do v09, não como diagnóstico global.
- v08 permanece `mechanical_downscale_probe`; v09 permanece `technical_pass_visual_semantic_fail`, `animation_candidate=false`, `human_gate_ready=false` e `res_promotion=false`. v04–v09 e `res/`, runtime e ROM não foram alterados.
- A rota limitada `native_grid_encoded` foi preparada com R1, guia de contato, canvas lógico 32x32, fator inteiro, paleta explícita, pivot, linha de chão e must-preserve. Tentativa 01 falhou diretamente na medição: 1254x1254, não divisível por 32, fator não inteiro, blocos não uniformes e 28285 cores. SHA `787e6232bd2012fae3ab409b55bbc4a0b727ba0b4795c014cc11cd4dc95875ca`.
- Tentativa 02 foi materialmente distinta, mas o produtor externo rejeitou a saída com `HTTP 400`, `moderation_blocked`, etapa `output`, categoria `other`; nenhum arquivo ou pixel foi retornado. A rota foi encerrada após os dois ensaios autorizados, sem contornar moderação e sem resgate mecânico.
- Registros causais: `data/staging/animation_curation_run_keyposes_20260903/native_grid_encoded_attempt_01_record.md`, `native_grid_encoded_attempt_02_record.md` e `native_grid_encoded_route_report.md`. O inventário e a triagem dos ramos independentes estão em `data/staging/visual_inventory_20260903/`.
- Nenhuma rota autorizada produziu autoria nativa para run, inhale ou jump/float. Os guias high-res permanecem `visual_source`; não há nova strip, lineart final, recurso `res/`, alteração de runtime ou ROM.

## 20. Pacote isolado v10 — revisão visual em runtime — 2026-09-04

- Criado o ramo isolado `codex/kirby-visual-review-runtime-v10` com pacote de revisão visual em runtime; o estado permanece `runtime_visual_review_candidate`, `visual_pass=false`, `human_gate_ready=false` e `res_promotion=false`.
- A integração usa apenas a autoridade R1 (`591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`) e fontes/rotas persistidas. A linhagem é `assisted_native_translation`/`mechanical_affine_probe`; nenhuma declaração de autoria nativa foi feita.
- A ROM de revisão `2f2a7a2ce7c51f35ca8ee8fdf1c9ac2c784cc86150f15440da09bb329e8dcfbd` foi executada na cena dedicada 11 do BlastEm. O bundle foi selado com screenshot, SRAM e VDP dump, mas prova apenas consumo do recurso e snapshot de runtime.
- Os quatro strips continuam reprovados pelos entrypoints canônicos por lineart diagnóstica, linhagem mecânica, inconsistência de escala/movimento e perfil não canônico. O agregado retorna `status=error`, `maximum_proven_claim=none`; não há promoção para `res/` nem gate humano.
- Detalhes, comandos, hashes e o próximo gate causal estão em `doc/v10_runtime_visual_review_closeout.md`.

## 21. V11 — produção visual completa autorizada em branch de revisão — 2026-09-04

- Criada a branch `codex/kirby-full-visual-production-v11` a partir de `codex/kirby-visual-review-runtime-v10`; o histórico v10 permanece preservado.
- Registrada a decisão de escopo em `doc/v11_full_visual_production_scope_decision.json`: produção de candidatos visuais e integração na branch de revisão autorizadas; aceitação humana, promoção mainline e `ready_for_aaa` continuam bloqueadas.
- Implementado o único bridge solicitado, `forge-art native-edit`, com schema `tools/sgdk_wrapper/forge_art/schemas/native_edit_actions.schema.json`, ações explícitas, validação de limites/paleta, SHA before/after e saída staging-only.
- Produzido `kirby_run_contact_v11` em 32×32 P/4bpp a partir de 38 ações editoriais, usando exclusivamente `data/source_art/r1/r1-01/concept.png` como autoridade (`591d3106...31303cd`); o candidato passou pixel-contract e nearest 8×.
- O candidato foi integrado somente ao consumidor da cena 11 como `spr_native_run_contact_v11`, classificado `native_candidate`; placeholders do first playable, animações, stage, inimigos, boss e abilities não foram promovidos.
- Estado honesto: `status=full_visual_runtime_candidate`, `visual_pass=false`, `human_gate_ready=false`, `final_acceptance=false`, `ready_for_aaa=false`. Próximo gate causal: revisão humana da pose em 1× e captura runtime vinculada à ROM v11.

## 22. V11 — marco causal do run cycle — 2026-09-04

- A branch `codex/kirby-full-visual-production-v11` permaneceu isolada de v04–v10; a autoridade exclusiva continua sendo R1, SHA-256 `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`.
- O bridge `forge-art native-edit` foi endurecido com schema condicional, IDs únicos, no-op/atomicidade, saída staging-only, proteção de `data/`/`res/` e sidecar de hashes. `test_native_edit.py` passou 7/7 e `forge_art self-check` passou 136/136.
- Produzido o marco visual `run_cycle` com quatro poses nativas 32×32: contact `1754b9d685cf2329d09e33f504fb89983f5784ace114b2e620c26bd028c83a4a`, down `4d4a7f87e6ba7ce61716afd7a1e73c659623631c1714fe94ead5c244bcc74b7c`, passing `c0956699a838157386e41279c35b83f84186fe7f4131741c15c8984754f6167e` e flight/push `5fb235d361347bc8850c1f864d45f43a028f80a8f2b1038865569fd5351d1ce4`.
- Strip r3 SHA `d09d2627fd4538b0f828023acd2e45bbc19cbcf868877b80de143daed3fb1dea` e GIF SHA `49bcfab264d89506e4edd9d5d7497969117f50ece19b5a558bafd5852ed74e62`; integrity passou sem findings, mas o visual permanece simplificado e `visual_pass=false`.
- O recurso foi integrado ao estado real `KIRBY_RUN` da cena 4, sem hook de estado. Build canônico `rc=0`, ROM SHA `68f59e9c072a1671b723e8677c40c046f552684b93e5c6daf719a4439f972a10`; BlastEm selou a sessão `blastem-linux-20260904T094658Z-3181717` com cena 4, 59,6 fps snapshot, CPU 72, 16 sprites/scanline, 26 ativos e 0 over-budget.
- O playtest scene 5 foi descartado por bundle incompleto (`vlab_block_missing`, `artifact_missing:vdp_dump`, `artifact_missing:runtime_metrics`). A captura interativa Left mostra o ator no estágio real, mas não aprova fidelidade nem continuidade do ciclo.
- Estado honesto: `status=full_visual_runtime_candidate`, `claim_ceiling=run_cycle_visual_runtime_candidate`, `animation_candidate=false`, `human_gate_ready=false`, `final_acceptance=false`, `ready_for_aaa=false`, `res_promotion=false`. Próximo passo: produzir idle, inhale e jump/float nativos antes de qualquer gate humano.
